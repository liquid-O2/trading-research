"""Disposable tapes exercise transport, signed volume, identity and bar timing."""

from pathlib import Path
import hashlib
import json

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from trading_research.research.method_pack.adapters import MBP1_RELATIVE, normalize_mbp1_row
from trading_research.research.method_pack.mbp1_views import (
    TapeError, TradeBars, export_views, iter_mbp1_window, plan_window,
)


BASE = 1_704_153_600_000_000_000


def raw(at, *, action="T", side="B", price=100.0, size=1, instrument=42, sequence=None):
    row = {"t": BASE + at, "action": action, "side": side, "price": price, "size": size,
           "bid_px": 99.75, "ask_px": 100.0, "bid_sz": 3, "ask_sz": 5,
           "instrument_id": instrument, "flags": 0}
    if sequence is not None:
        row["sequence"] = sequence
    return row


def tape(tmp_path, rows, *, name="2024-01.parquet", typed=False):
    path = tmp_path / "raw" / MBP1_RELATIVE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows)
    if typed:
        index = table.schema.get_field_index("t")
        table = table.set_column(index, "t", table.column(index).cast(pa.timestamp("ns", tz="UTC")))
    pq.write_table(table, path, row_group_size=2)
    return path


def ownership(path, start=BASE, end=BASE + 120_000_000_000):
    return {"owned_spans": [{"path": str(path), "start_ns": start, "end_ns": end,
                             "kind": "monthly", "dataset": "nq-mbp-1", "status": "owned"}], "holes": []}


def read_artifact(result, view):
    return [json.loads(line) for line in Path(result["artifacts"][view]["path"]).read_text().splitlines()]


def test_raw_unchanged_duplicates_ties_actions_and_hashes(tmp_path):
    rows = [raw(1, action="A", size=100), raw(2, price=100, size=2),
            raw(2, price=100, size=2), raw(2, price=101), raw(3, side="A", price=102, size=3),
            raw(4, action="F", size=50), raw(1_000_000_000, side="N", price=103, size=4)]
    path = tape(tmp_path, rows)
    before = path.read_bytes()
    result = export_views(tmp_path / "raw", tmp_path / "views", BASE, BASE + 60_000_000_000,
                          ownership=ownership(path))
    assert path.read_bytes() == before
    assert result["raw_source_signatures_unchanged"]
    trades = read_artifact(result, "trades")
    assert len(trades) == 5
    assert [t["source_row"] for t in trades] == [1, 2, 3, 4, 6]
    assert trades[0]["event_ns"] == BASE + 2
    assert trades[0]["signed_size"] == 2
    bars = read_artifact(result, "ohlcv-1m")
    assert len(bars) == 1
    bar = bars[0]
    assert bar["O"] is None  # equal timestamps, different prices, no exchange sequence
    assert bar["H"] == "103.0" and bar["L"] == "100.0" and bar["C"] == "103.0"
    assert (bar["V"], bar["buy_volume"], bar["sell_volume"], bar["unknown_volume"]) == (12, 5, 3, 4)
    assert bar["delta_known"] == 2 and bar["delta"] is None
    assert bar["known_at"] == BASE + 60_000_000_000
    assert bar["complete"] is None
    assert len(read_artifact(result, "bbo")) == 7
    for artifact in result["artifacts"].values():
        assert hashlib.sha256(Path(artifact["path"]).read_bytes()).hexdigest() == artifact["sha256"]


def test_monthly_ownership_not_append_duplicate_weekly_tape(tmp_path):
    rows = [raw(1), raw(2, side="A")]
    path = tape(tmp_path, rows)
    tape(tmp_path, rows, name="2024-01-01.parquet")
    result = export_views(tmp_path / "raw", tmp_path / "views", BASE, BASE + 3,
                          views=["trades"])
    assert len(read_artifact(result, "trades")) == 2
    assert all(row["source_file"] == str(path) for row in read_artifact(result, "trades"))


def test_arrow_exact_ns_half_open_filter_and_physical_rows(tmp_path):
    path = tape(tmp_path, [raw(1), raw(2), raw(3), raw(4), raw(5)], typed=True)
    plan = plan_window(tmp_path / "raw", BASE + 2, BASE + 5, ownership=ownership(path))
    rows = list(iter_mbp1_window(plan, trades_only=True))
    assert [r["event_ns"] for r in rows] == [BASE + 2, BASE + 3, BASE + 4]
    assert [r["source_row"] for r in rows] == [1, 2, 3]


def test_different_contracts_are_separate_and_empty_seconds_are_omitted(tmp_path):
    path = tape(tmp_path, [raw(1, instrument=42), raw(2, instrument=43), raw(2_000_000_000, instrument=43)])
    result = export_views(tmp_path / "raw", tmp_path / "views", BASE, BASE + 3_000_000_000,
                          views=["ohlcv-1s"], ownership=ownership(path))
    bars = read_artifact(result, "ohlcv-1s")
    assert [(r["start_ns"], r["instrument_id"]) for r in bars] == [(BASE, 42), (BASE, 43), (BASE + 2_000_000_000, 43)]


def test_sequence_can_resolve_ohlc_ties_without_changing_volume():
    accumulator = TradeBars(1, BASE, BASE + 1_000_000_000)
    for index, row in enumerate([raw(1, price=101, sequence=2), raw(1, price=100, sequence=1)]):
        accumulator.add(normalize_mbp1_row(row, source_file="fixture", source_row=index))
    bar = accumulator.finish()[0]
    assert bar["O"] == 100 and bar["C"] == 101 and bar["V"] == 2


def test_out_of_order_tape_fails_explicitly(tmp_path):
    path = tape(tmp_path, [raw(2), raw(1)])
    plan = plan_window(tmp_path / "raw", BASE, BASE + 3, ownership=ownership(path))
    with pytest.raises(TapeError, match="out of order"):
        list(iter_mbp1_window(plan))


def test_raw_output_path_and_overlap_are_rejected(tmp_path):
    path = tape(tmp_path, [raw(1)])
    with pytest.raises(ValueError, match="outside"):
        export_views(tmp_path / "raw", tmp_path / "raw" / "derived", BASE, BASE + 3,
                     ownership=ownership(path))
    manifest = ownership(path)
    manifest["owned_spans"].append(dict(manifest["owned_spans"][0]))
    with pytest.raises(TapeError, match="overlap"):
        plan_window(tmp_path / "raw", BASE, BASE + 3, ownership=manifest)


def test_partial_bar_and_missing_ownership_retained(tmp_path):
    path = tape(tmp_path, [raw(1)])
    result = export_views(tmp_path / "raw", tmp_path / "views", BASE + 1, BASE + 30_000_000_000,
                          views=["ohlcv-1m"], ownership=ownership(path, BASE + 1, BASE + 2))
    assert result["plan"]["unowned_intervals"] == [{"start_ns": BASE + 2, "end_ns": BASE + 30_000_000_000}]
    bar = read_artifact(result, "ohlcv-1m")[0]
    assert bar["full_bar_requested"] is False and bar["complete"] is None
