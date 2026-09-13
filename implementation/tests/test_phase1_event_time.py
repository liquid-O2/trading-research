"""Event-clock integration and admission regressions for the new replay."""
from copy import deepcopy
from decimal import Decimal

import pytest

from trading_research.research.method_pack.adapters import normalize_mbp1_row
from trading_research.research.method_pack.event_time import (
    aggregate_events, BookObservations, build_event_window, CONTRACT, EventWindow,
    interval_state, MINUTE, VERSION, vendor_diagnostics,
)
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.native_resolution import NativeEvidenceError

START = 1_800_000_000_000_000_000


def event(offset, price, size=1, side="B", index=0, action="T", **more):
    return normalize_mbp1_row({"t": START + offset, "price": str(price), "size": size,
        "side": side, "action": action, "instrument_id": 17, "flags": 128, **more},
        source_file="native.parquet", source_row=index)


def window(rows, minutes=3):
    doc = aggregate_events(rows, START, START + minutes * MINUTE, 17)
    doc.update(schema=VERSION, contract_sha256=content_hash(CONTRACT), instrument_id=17,
               start_ns=START, end_ns=START + minutes * MINUTE)
    return EventWindow(doc)


def test_timestamp_ties_do_not_destroy_extrema_volume_or_resolve_open():
    rows = [event(1, 100, 2, index=0), event(1, 101, 3, index=1), event(2, 102, index=2)]
    bar = window(rows).bars(START, START + MINUTE)[0]
    assert bar["O"] is None and bar["C"] == 102
    assert (bar["H"], bar["L"], bar["V"]) == (102, 100, 6)
    assert bar["complete"] is False and bar["observed_complete"] is True
    assert window(rows).profile(START, START + MINUTE)["total_volume"] == 6


def test_real_repeated_executions_survive_but_repeated_physical_identity_rejected():
    rows = [event(1, 100, 2, index=0), event(1, 100, 2, index=1)]
    assert window(rows).bars(START, START + MINUTE)[0]["V"] == 4
    with pytest.raises(NativeEvidenceError, match="duplicate physical"):
        window([rows[0], rows[0]])


def test_quote_update_never_becomes_trade_and_buckets_are_half_open():
    rows = [event(0, 100, index=0), event(MINUTE - 1, 101, index=1),
            event(MINUTE, 102, index=2), event(MINUTE + 1, 999, 1000, index=3, action="M")]
    observed = window(rows)
    assert [r["V"] for r in observed.bars(START, START + 2 * MINUTE)] == [2, 1]
    assert observed.vwap(START, START + MINUTE)["price"] == Decimal("100.5")
    assert observed.vwap(START, START + 2 * MINUTE)["price"] == 101


def test_future_perturbation_does_not_change_profile_vwap_or_candles():
    rows = [event(1, 100, index=0), event(MINUTE + 1, 101, index=1)]
    changed = [*rows[:1], event(MINUTE + 1, 10000, 123456, index=1)]
    a, b = window(rows), window(changed)
    assert a.profile(START, START + MINUTE) == b.profile(START, START + MINUTE)
    assert a.vwap(START, START + MINUTE) == b.vwap(START, START + MINUTE)
    assert a.bars(START, START + MINUTE) == b.bars(START, START + MINUTE)


def test_different_vendor_clock_diagnostic_does_not_withhold_event_data():
    observed = window([event(1, 100, 1, index=0), event(MINUTE - 1, 101, 2, index=1)])
    bars = observed.bars(START, START + MINUTE)
    vendor = [dict(bars[0], V=1, H=100, C=100)]
    check = vendor_diagnostics(bars, vendor)
    assert check["different_minutes"] == 1 and check["purpose"] == "diagnostic_only"
    assert bars[0]["complete"] is True
    assert observed.coverage(START, START + MINUTE)["observed_scope_complete"] is True
    assert observed.coverage(START, START + MINUTE)["market_coverage_complete"] is None


def test_quiet_unknown_and_closed_are_separate_and_no_flat_bar_is_fabricated(tmp_path):
    observed = window([event(1, 100, index=0)])
    assert len(observed.bars(START, START + 3 * MINUTE)) == 1
    assert observed.coverage(START, START + 3 * MINUTE)["states"]["unknown_coverage"] == 2
    assert interval_state(START, START + MINUTE, []) == "unknown_coverage"
    receipt = {"kind": "verified_no_trade", "source_sha256": "a" * 64,
               "start_ns": START, "end_ns": START + MINUTE}
    assert interval_state(START, START + MINUTE, [], continuity=[receipt]) == "unknown_coverage"
    import json
    from trading_research.research.method_pack.native_resolution import file_digest
    evidence = tmp_path / 'continuity.json'
    evidence.write_text(json.dumps({'kind':'verified_no_trade','start_ns':START,
        'end_ns':START+MINUTE,'verification_method':'synthetic complete exchange sequence and heartbeat control'}))
    receipt.update(source_path=str(evidence),source_sha256=file_digest(evidence))
    assert interval_state(START, START + MINUTE, [], continuity=[receipt]) == "evidenced_no_trade"
    class Closed:
        def state(self, start, end):
            return "scheduled_closure"
    assert interval_state(START, START + MINUTE, [], schedule=Closed()) == "scheduled_closure"
    with pytest.raises(NativeEvidenceError, match="conflict"):
        interval_state(START, START + MINUTE, [{}], schedule=Closed())


def test_book_clear_snapshot_bad_book_and_same_batch_ambiguity_cut_comparisons():
    def quote(at, bid_size, **kw):
        return event(at, 100, index=at, action="M", bid_px="100", ask_px="100.25",
                     bid_sz=bid_size, ask_sz=4, **kw)
    book = BookObservations()
    book.add(quote(1, 10))
    first = book.add(quote(2, 15))[0]
    assert first["bid_added"] is None
    added = book.add(quote(3, 1, flags=128 | 32))[0]
    assert added["bid_added"] == 5
    snapshot = book.add(quote(4, 3))[0]
    assert snapshot["reset"] is True and snapshot["bid_removed"] is None
    book.finish()
    book.add(quote(5, 2, flags=128 | 4))
    bad = book.finish()[0]
    assert bad["bad_book"] is True and bad["bid"] is None
    book.add(quote(6, 10))
    book.add(quote(6, 20))
    tie = book.finish()[0]
    assert tie["timestamp_order_known"] is False and tie["bid_added"] is None


def test_native_owned_mbp_window_has_hash_membership_and_no_weekly_pooling(tmp_path):
    import pyarrow as pa
    import pyarrow.parquet as pq
    from trading_research.research.method_pack.adapters import MBP1_RELATIVE
    root = tmp_path / "raw"
    directory = root / MBP1_RELATIVE
    directory.mkdir(parents=True)
    raw = [{"t": START + 1, "price": 100., "size": 2, "side": "B", "action": "T", "instrument_id": 17, "flags": 128},
           {"t": START + 1, "price": 100., "size": 2, "side": "B", "action": "T", "instrument_id": 17, "flags": 128},
           {"t": START + 2, "price": 101., "size": 500, "side": "B", "action": "M", "instrument_id": 17, "flags": 128}]
    monthly, weekly = directory / "2027-01.parquet", directory / "2027-01-04.parquet"
    for path in (monthly, weekly):
        pq.write_table(pa.Table.from_pylist(raw), path)
    (root / "manifests").mkdir()
    pq.write_table(pa.Table.from_pylist([{"archive_path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size}
                                        for p in (monthly, weekly)]), root / "manifests/files.parquet")
    ownership = {"owned_spans": [{"path": str(monthly), "start_ns": START, "end_ns": START + MINUTE}], "holes": []}
    doc = build_event_window(root, START, START + MINUTE, 17, ownership=ownership)
    assert doc["row_count"] == 2 and doc["bars"]["60"][0]["V"] == 4
    assert len(doc["source_files"]) == 1 and len(doc["membership_sha256"]) == 64
    with pytest.raises(NativeEvidenceError, match="frozen"):
        build_event_window(root, START, START + MINUTE, 17, ownership=ownership,
                           frozen_inputs=[dict(doc["source_files"][0], sha256="0" * 64)])
