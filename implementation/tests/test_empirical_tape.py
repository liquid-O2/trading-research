from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from trading_research.research.method_pack.adapters import normalize_trade_row
from trading_research.research.method_pack.empirical_protocol import population_summary
from trading_research.research.method_pack.empirical_tape import (
    load_tape_session, m09_research_comparison, stream_native_trades,
)
from trading_research.research.method_pack.native_resolution import NativeEvidenceError


NS = 1_000_000_000
MINUTE = 60 * NS
INSTRUMENT = 17
TRADES = "quantpad/cme__nq-continuous-futures__trades"
BARS = "quantpad/cme__nq-continuous-futures__ohlcv-1m"


def _write_parquet(path: Path, rows, *, row_group_size=3):
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), path, row_group_size=row_group_size)


def _frozen(path: Path, root: Path, dataset: str):
    return {
        "path": path.relative_to(root).as_posix(), "dataset_id": dataset,
        "bytes": path.stat().st_size,
        "sha256": sha256(path.read_bytes()).hexdigest(),
        "hash_basis": "full_file_sha256",
    }


def _native_root(tmp_path: Path, *, missing_bar=False, unknown=False):
    root = tmp_path / "data"
    start = 1_800_000_000_000_000_000
    trade_path = root / TRADES / "fixture.parquet"
    bar_path = root / BARS / "fixture.parquet"
    definition = root / "derived/continuous-futures__instrument-and-roll-maps/nq-instruments.parquet"
    # Row 1 is foreign. Rows 3 and 4 are intentionally identical market
    # events but distinct physical members and must both survive.
    trades = [
        {"t": start + 1, "price": "100.00", "size": 2, "side": "B", "instrument_id": INSTRUMENT},
        {"t": start + 2, "price": "999.00", "size": 4, "side": "B", "instrument_id": 999},
        {"t": start + 3, "price": "100.25", "size": 1, "side": "A", "instrument_id": INSTRUMENT},
        {"t": start + MINUTE + 1, "price": "100.50", "size": 3, "side": "N" if unknown else "B", "instrument_id": INSTRUMENT},
        {"t": start + MINUTE + 1, "price": "100.50", "size": 3, "side": "N" if unknown else "B", "instrument_id": INSTRUMENT},
        {"t": start + 2 * MINUTE + 1, "price": "100.25", "size": 1, "side": "A", "instrument_id": INSTRUMENT},
    ]
    bars = [
        {"t": start // 1_000_000, "o": "100.00", "h": "100.25", "l": "100.00", "c": "100.25", "v": 3, "instrument_id": INSTRUMENT},
        {"t": (start + MINUTE) // 1_000_000, "o": "100.50", "h": "100.50", "l": "100.50", "c": "100.50", "v": 6, "instrument_id": INSTRUMENT},
        {"t": (start + 2 * MINUTE) // 1_000_000, "o": "100.25", "h": "100.25", "l": "100.25", "c": "100.25", "v": 1, "instrument_id": INSTRUMENT},
    ]
    if missing_bar:
        bars.pop(1)
    _write_parquet(trade_path, trades, row_group_size=2)
    _write_parquet(bar_path, bars, row_group_size=1)
    _write_parquet(definition, [{
        "instrument_id": INSTRUMENT, "raw_symbol": "NQZ9", "root": "NQ",
        "min_price_increment": "0.25", "first_definition_ns": start - NS,
    }])
    identities = [_frozen(trade_path, root, TRADES), _frozen(bar_path, root, BARS),
                  _frozen(definition, root, "derived/continuous-futures__instrument-and-roll-maps")]
    _write_parquet(root / "manifests/files.parquet", [
        {"archive_path": row["path"], "bytes": row["bytes"]} for row in identities
    ])
    return root, start, identities


def test_stream_verifies_frozen_hash_and_preserves_exact_physical_members(tmp_path):
    root, start, identities = _native_root(tmp_path)
    stream = stream_native_trades(root, TRADES, start, start + 3 * MINUTE,
                                  INSTRUMENT, frozen_inputs=identities)
    rows = list(stream)
    assert len(rows) == 5
    assert [row["source_row"] for row in rows] == [0, 2, 3, 4, 5]
    assert rows[2]["event_ns"] == rows[3]["event_ns"]
    assert rows[2]["price"] == rows[3]["price"]
    assert stream.row_count == 5
    assert [(row["row_start"], row["row_end"]) for row in stream.physical_members] == [
        (0, 1), (2, 6),
    ]
    assert all(identity.hash_basis == "full_file_sha256" for identity in stream.file_identities)
    with pytest.raises(NativeEvidenceError, match="single-use"):
        list(stream)

    bad = [dict(row) for row in identities]
    bad[0]["sha256"] = "0" * 64
    with pytest.raises(NativeEvidenceError, match="differs from frozen"):
        stream_native_trades(root, TRADES, start, start + 3 * MINUTE,
                             INSTRUMENT, frozen_inputs=bad)
    with pytest.raises(NativeEvidenceError, match="bounded 48-hour"):
        stream_native_trades(root, TRADES, start, start + 49 * 60 * MINUTE,
                             INSTRUMENT, frozen_inputs=identities)


def test_tape_session_is_bounded_profile_delta_and_independent_coverage(tmp_path):
    root, start, identities = _native_root(tmp_path, unknown=True)
    session = load_tape_session(
        root, TRADES, start, start + 3 * MINUTE, INSTRUMENT,
        frozen_inputs=identities, value_area_fraction="0.70")
    assert session["row_count"] == 5
    assert len(session["membership_sha256"]) == 64
    assert len(session["evidence_sha256"]) == 64
    assert session["coverage"]["coverage_ok"] is True
    assert len(session["coverage"]["reconciliation"]) == 3
    assert session["coverage"]["reconciliation"][1]["endpoint_order"] == "unknown_order"
    assert session["profile"]["total_volume"] == Decimal(10)
    assert session["profile"]["tick_size"] == Decimal("0.25")
    assert session["profile"]["value_area_fraction"] == Decimal("0.70")
    assert session["minutes"][0]["known_delta"] == Decimal(1)
    assert session["minutes"][1]["unknown_volume"] == Decimal(6)
    assert session["minutes"][1]["delta"] is None
    assert session["minutes"][1]["delta_low"] == Decimal(-6)
    assert session["minutes"][1]["delta_high"] == Decimal(6)
    assert session["flow"]["known_delta"] == Decimal(0)
    assert session["flow"]["delta"] is None
    # The session retains profile/minute aggregates and compact locators, not
    # a list of all native trade rows or all event IDs.
    assert "rows" not in session and "event_ids" not in session["profile"]


def test_missing_ohlcv_minute_never_becomes_complete_from_tape_extents(tmp_path):
    root, start, identities = _native_root(tmp_path, missing_bar=True)
    session = load_tape_session(root, TRADES, start, start + 3 * MINUTE,
                                INSTRUMENT, frozen_inputs=identities)
    assert session["coverage"]["coverage_ok"] is None
    assert session["coverage"]["coverage_reason"] == "missing_native_intervals"
    assert session["coverage"]["missing_intervals"] == [
        [start + MINUTE, start + 2 * MINUTE]
    ]
    assert session["profile"]["coverage"]["ok"] is None


def test_m08_va70_expands_both_equal_adjacent_rows(tmp_path):
    root = tmp_path / "va-data"
    start = 1_850_000_000_000_000_000
    trade_path = root / TRADES / "va.parquet"
    bar_path = root / BARS / "va.parquet"
    definition = root / "derived/continuous-futures__instrument-and-roll-maps/nq-instruments.parquet"
    levels = [("100.00", 1), ("100.25", 2), ("100.50", 4),
              ("100.75", 2), ("101.00", 1)]
    _write_parquet(trade_path, [
        {"t": start + index + 1, "price": price, "size": size,
         "side": "B", "instrument_id": INSTRUMENT}
        for index, (price, size) in enumerate(levels)
    ])
    _write_parquet(bar_path, [{
        "t": start // 1_000_000, "o": "100.00", "h": "101.00",
        "l": "100.00", "c": "101.00", "v": 10,
        "instrument_id": INSTRUMENT,
    }])
    _write_parquet(definition, [{
        "instrument_id": INSTRUMENT, "raw_symbol": "NQZ9", "root": "NQ",
        "min_price_increment": "0.25", "first_definition_ns": start - NS,
    }])
    identities = [_frozen(trade_path, root, TRADES), _frozen(bar_path, root, BARS),
                  _frozen(definition, root, "derived/continuous-futures__instrument-and-roll-maps")]
    _write_parquet(root / "manifests/files.parquet", [
        {"archive_path": row["path"], "bytes": row["bytes"]} for row in identities
    ])
    session = load_tape_session(
        root, TRADES, start, start + MINUTE, INSTRUMENT,
        frozen_inputs=identities, value_area_fraction="0.70",
        value_area_tie_policy="both", poc_tie_policy="lowest")
    profile = session["profile"]
    assert profile["poc"] == Decimal("100.50")
    assert (profile["val"], profile["vah"]) == (
        Decimal("100.25"), Decimal("100.75"))
    assert profile["volume_inside_value"] == Decimal(8)
    assert profile["value_area_algorithm"] == "contiguous_larger_adjacent_volume_tie_both"
    assert profile["value_area_tie_policy"] == "both"


def _trade(at, price, size=1, side="B", row=0, *, instrument=INSTRUMENT):
    return normalize_trade_row(
        {"t": at, "price": price, "size": size, "side": side,
         "instrument_id": instrument},
        dataset_id=TRADES, source_file="fixture.parquet", source_row=row)


def _rule():
    return {
        "rule_id": "REFILL-STUDY:touch_record:comparison-v1",
        "method_id": "REFILL-STUDY", "branch": "touch_record",
        "evidence_mode": "research_comparison",
        "observation_unit": "zone_return",
        "transport_observation_unit": "zone_touch",
        "assumption_ids": ["A-M09-touch-record-v1"],
        "parameters": {"min_event_quantity": 100, "min_events": 2,
                       "formation_seconds": 120, "span_ticks": 2,
                       "departure_ticks": 4, "response_ticks": 4,
                       "horizon_minutes": 15},
    }


def _partition(end):
    return {"partition_id": "NQ-2030-01-02-17", "instrument_id": INSTRUMENT,
            "date": "2030-01-02", "session": {"end_ns": end}}


def test_m09_pair_departure_distinct_returns_and_tied_outcome_ambiguity():
    t0 = 1_900_000_000_000_000_000
    rows = [
        _trade(t0 + 1 * NS, "100.00", 100, "B", 0),
        _trade(t0 + 2 * NS, "100.50", 100, "B", 1),  # immutable [100,100.5]
        _trade(t0 + 3 * NS, "101.50", 1, "B", 2),    # departure
        _trade(t0 + 4 * NS, "100.25", 1, "A", 3),    # return 1
        _trade(t0 + 5 * NS, "101.50", 1, "B", 4),    # pass
        _trade(t0 + 6 * NS, "101.50", 1, "B", 5),    # fresh departure
        _trade(t0 + 7 * NS, "100.00", 1, "A", 6),    # return 2
        _trade(t0 + 8 * NS, "101.50", 1, "B", 7),
        _trade(t0 + 8 * NS, "99.00", 1, "A", 8),     # competing batch
        _trade(t0 + 9 * NS, "101.50", 1, "B", 9),    # rearm again
        _trade(t0 + 10 * NS, "100.25", 1, "A", 10),  # return 3
        _trade(t0 + 16 * MINUTE, "100.75", 1, "B", 11),
    ]
    result = m09_research_comparison(
        rows, rule=_rule(), partition=_partition(t0 + 30 * MINUTE),
        registry_sha256="a" * 64, tick_size="0.25", coverage_ok=True)
    assert len(result["zones"]) == 1
    assert result["zones"][0]["low"] == "100.00"
    assert result["zones"][0]["high"] == "100.50"
    assert result["zones"][0]["immutable"] is True
    assert result["zones"][0]["expires_at"] == t0 + 30 * MINUTE
    assert result["zones"][0]["return_count"] == 3
    assert [row["replay"]["verdict"] for row in result["records"]] == [
        "pass", "unknown", "fail",
    ]
    assert all(row["opportunity"]["observation_unit"] == "zone_touch"
               for row in result["records"])
    assert result["records"][1]["replay"]["ambiguous"] is True
    assert result["records"][1]["replay"]["reason"] == "same_timestamp_competing_outcomes"
    summary = population_summary(result["records"])
    assert (summary["opportunities"], summary["p"], summary["f"], summary["u"]) == (3, 1, 1, 1)
    assert summary["attempts"] is summary["orders"] is summary["actual_fills"] is None


def test_m09_same_side_formation_batch_skips_all_and_future_does_not_change_ids():
    t0 = 1_910_000_000_000_000_000
    prefix = [
        _trade(t0 + NS, "99.75", 100, "B", 0),
        _trade(t0 + NS, "100.00", 100, "B", 1),  # ambiguous same-side batch
        _trade(t0 + 2 * NS, "100.00", 100, "B", 2),
        _trade(t0 + 3 * NS, "100.25", 100, "B", 3),
        _trade(t0 + 4 * NS, "101.25", 1, "B", 4),
        _trade(t0 + 5 * NS, "100.00", 1, "A", 5),
    ]
    kwargs = dict(rule=_rule(), partition=_partition(t0 + 30 * MINUTE),
                  registry_sha256="b" * 64, tick_size="0.25", coverage_ok=None)
    first = m09_research_comparison(prefix, **kwargs)
    extended = m09_research_comparison(
        prefix + [_trade(t0 + 6 * NS, "101.25", 1, "B", 6)], **kwargs)
    assert len(first["zones"]) == 1
    assert first["zones"][0]["formation_event_ids"] == (
        "fixture.parquet:2:17", "fixture.parquet:3:17")
    assert first["ambiguities"][0]["skipped_member_count"] == 2
    assert first["ambiguous_formation_batch_count"] == 1
    assert first["ambiguous_formation_event_count"] == 2
    assert first["records"][0]["opportunity"] == extended["records"][0]["opportunity"]
    assert first["records"][0]["opportunity"]["reference"]["low"] == "100.00"


def test_m09_rejects_foreign_and_duplicate_physical_members():
    t0 = 1_920_000_000_000_000_000
    kwargs = dict(rule=_rule(), partition=_partition(t0 + MINUTE),
                  registry_sha256="c" * 64, tick_size="0.25", coverage_ok=True)
    with pytest.raises(NativeEvidenceError, match="foreign"):
        m09_research_comparison([_trade(t0 + NS, "100", instrument=99)], **kwargs)
    row = _trade(t0 + NS, "100", row=1)
    with pytest.raises(NativeEvidenceError, match="duplicate physical"):
        m09_research_comparison([row, row], **kwargs)
