"""Regression tests for outcome-blind native coverage freezes."""

from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
import json

import pyarrow as pa
import pyarrow.parquet as pq

from trading_research.research.method_pack.empirical_coverage import (
    CoverageValidationError,
    build_frozen_split,
    full_rth_sessions,
    inventory_native,
    validate_frozen_split,
)


MINUTE_NS = 60_000_000_000


def _rth_rows(day: date, instrument_id: int = 42, *, missing: int | None = None):
    from zoneinfo import ZoneInfo

    start = datetime.combine(day, datetime.min.time().replace(hour=9, minute=30),
                             tzinfo=ZoneInfo("America/New_York"))
    start_ns = int(start.astimezone(timezone.utc).timestamp() * 1_000_000_000)
    rows = []
    for index in range(390):
        if index == missing:
            continue
        t_ms = (start_ns + index * MINUTE_NS) // 1_000_000
        rows.append({
            "t": t_ms, "o": 100.0, "h": 101.0, "l": 99.0,
            "c": 100.5, "v": 1.0, "instrument_id": instrument_id,
        })
    return rows, start_ns


def _fixture_root(tmp_path, *, trade_day: date | None = None):
    ohlcv = tmp_path / "quantpad/cme__nq-continuous-futures__ohlcv-1m"
    ohlcv.mkdir(parents=True)
    rows = []
    for day in (date(2026, 1, 2), date(2026, 1, 5), date(2026, 2, 3)):
        day_rows, _ = _rth_rows(day)
        rows.extend(day_rows)
    pq.write_table(pa.Table.from_pylist(rows), ohlcv / "2026.parquet", row_group_size=390)

    definitions = tmp_path / "derived/continuous-futures__instrument-and-roll-maps"
    definitions.mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist([{
        "instrument_id": 42, "raw_symbol": "NQH6",
        "min_price_increment": 0.25,
        "first_definition_ns": 1_700_000_000_000_000_000,
    }]), definitions / "nq-instruments.parquet")

    if trade_day is not None:
        trades = tmp_path / "quantpad/cme__nq-continuous-futures__trades"
        trades.mkdir(parents=True)
        _, session_start = _rth_rows(trade_day)
        pq.write_table(pa.Table.from_pylist([{
            "t": session_start, "price": 100.0, "size": 1,
            "side": "B", "instrument_id": 42, "flags": 0,
        }]), trades / "2026-01-01.parquet")
    return tmp_path


def test_inventory_and_exact_full_rth_session(tmp_path):
    root = _fixture_root(tmp_path)
    inventory = inventory_native(root, roots=["NQ"])
    record = inventory["roots"]["NQ"]["datasets"]["definition"]["files"][0]
    assert record["valid_metadata"] is True
    assert record["instrument_ids"] == ["42"]
    assert record["canonical_owner"] == "filesystem_fallback"

    sessions = full_rth_sessions(root, "NQ", start_date=date(2026, 1, 1),
                                 inventory=inventory)
    assert [row["date"] for row in sessions] == ["2026-01-02", "2026-01-05", "2026-02-03"]
    assert all(row["rth_minute_count"] == 390 for row in sessions)


def test_incomplete_session_is_not_promoted(tmp_path):
    root = tmp_path / "bad"
    path = root / "quantpad/cme__nq-continuous-futures__ohlcv-1m"
    path.mkdir(parents=True)
    rows, _ = _rth_rows(date(2026, 1, 2), missing=77)
    pq.write_table(pa.Table.from_pylist(rows), path / "2026.parquet")
    inventory = inventory_native(root, roots=["NQ"])
    assert full_rth_sessions(root, "NQ", start_date=date(2026, 1, 1),
                             inventory=inventory) == []


def test_monthly_freeze_excludes_known_dates_and_preserves_unknown_exposure(tmp_path):
    root = _fixture_root(tmp_path)
    split = build_frozen_split(
        root, roots=["NQ"], start_date=date(2026, 1, 1), end_date=date(2026, 2, 28),
        source_dates={date(2026, 1, 2)}, prior_inspected_dates=set(),
        include_hashes=True,
    )
    assert [row["date"] for row in split["partitions"]] == ["2026-01-05", "2026-02-03"]
    assert all(row["exposure"]["prior_exposure_status"] == "unknown"
               for row in split["partitions"])
    assert split["partitions"][0]["lookback"]["calendar_days"] == 62
    assert split["partitions"][0]["dataset_windows"]["ohlcv_1m"]["files"]
    result = validate_frozen_split(split, data_root=root)
    assert result["valid"] is True


def test_annual_filter_requires_tape_metadata_and_freezes_prior_rth_window(tmp_path):
    root = _fixture_root(tmp_path, trade_day=date(2026, 1, 5))
    split = build_frozen_split(
        root, roots=["NQ"], start_date=date(2026, 1, 5), end_date=date(2026, 1, 5),
        required_dataset_keys=("ohlcv_1m", "definition", "trades"),
        selection_frequency="annual", required_data_policy="filter",
        source_dates=set(), prior_inspected_dates=set(), include_hashes=True,
    )
    assert len(split["partitions"]) == 1
    partition = split["partitions"][0]
    assert partition["status"] == "eligible"
    assert partition["dataset_windows"]["trades"]["window_start_et"].startswith("2026-01-02T09:30")
    assert partition["dataset_windows"]["trades"]["files"]
    assert validate_frozen_split(split, data_root=root)["valid"] is True


def test_validation_detects_changed_frozen_input_and_forbidden_outcome_key(tmp_path):
    root = _fixture_root(tmp_path)
    split = build_frozen_split(
        root, roots=["NQ"], start_date=date(2026, 2, 3), end_date=date(2026, 2, 3),
        source_dates=set(), prior_inspected_dates=set(), include_hashes=True,
    )
    path = root / split["partitions"][0]["input_identities"][0]["path"]
    table = pq.read_table(path)
    rows = table.to_pylist()
    rows[0]["c"] = 123.0
    pq.write_table(pa.Table.from_pylist(rows), path)
    result = validate_frozen_split(split, data_root=root)
    assert result["valid"] is False
    assert any("frozen input changed" in error for error in result["errors"])

    forged = deepcopy(split)
    forged["outcomes"] = []
    assert validate_frozen_split(forged, verify_hashes=False)["valid"] is False
