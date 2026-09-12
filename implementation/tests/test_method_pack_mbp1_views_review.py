"""Targeted review fixtures for C02/C03 MBP-1 view provenance."""

import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from trading_research.research.method_pack.adapters import MBP1_RELATIVE
from trading_research.research.method_pack.mbp1_views import export_views, iter_mbp1_window, plan_window


BASE = 1_704_153_600_000_000_000


def _export_one(tmp_path, row):
    source = tmp_path / "raw" / MBP1_RELATIVE / "2024-01.parquet"
    source.parent.mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist([row]), source)
    ownership = {
        "owned_spans": [{
            "path": str(source),
            "start_ns": BASE,
            "end_ns": BASE + 1_000_000_000,
            "kind": "monthly",
            "dataset": "nq-mbp-1",
            "status": "owned",
        }],
        "holes": [],
    }
    result = export_views(
        tmp_path / "raw",
        tmp_path / "views",
        BASE,
        BASE + 1_000_000_000,
        views=["bbo"],
        ownership=ownership,
    )
    return json.loads(Path(result["artifacts"]["bbo"]["path"]).read_text())


def test_bbo_retains_native_update_side(tmp_path):
    row = {
        "t": BASE + 10,
        "action": "M",
        "side": "A",
        "price": 100.0,
        "size": 2,
        "bid_px": 99.75,
        "ask_px": 100.0,
        "bid_sz": 3,
        "ask_sz": 5,
        "instrument_id": 42,
        "flags": 0,
    }
    bbo = _export_one(tmp_path, row)

    assert bbo["action"] == "M"
    assert bbo["side"] == "A"
    assert bbo["resting_side"] == "A"


def test_receive_time_controls_event_availability_when_present(tmp_path):
    receive_ns = BASE + 700_000_000
    row = {
        "t": BASE + 10,
        "ts_recv": receive_ns,
        "action": "M",
        "side": "B",
        "price": 100.0,
        "size": 2,
        "bid_px": 99.75,
        "ask_px": 100.0,
        "bid_sz": 3,
        "ask_sz": 5,
        "instrument_id": 42,
        "flags": 0,
    }
    bbo = _export_one(tmp_path, row)

    assert bbo["event_ns"] == BASE + 10
    assert bbo["ts_recv"] == receive_ns
    assert bbo["known_at"] == receive_ns


def test_output_symlink_back_into_raw_is_rejected(tmp_path):
    source = tmp_path / "raw" / MBP1_RELATIVE / "2024-01.parquet"
    source.parent.mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist([{
        "t": BASE + 10,
        "action": "T",
        "side": "B",
        "price": 100.0,
        "size": 1,
        "bid_px": 99.75,
        "ask_px": 100.0,
        "bid_sz": 3,
        "ask_sz": 5,
        "instrument_id": 42,
        "flags": 0,
    }]), source)
    link = tmp_path / "apparently-external"
    link.symlink_to(tmp_path / "raw", target_is_directory=True)

    with pytest.raises(ValueError, match="outside"):
        export_views(tmp_path / "raw", link / "derived", BASE, BASE + 20)


def test_parquet_window_prunes_nonoverlapping_row_groups(tmp_path, monkeypatch):
    source = tmp_path / "raw" / MBP1_RELATIVE / "2024-01.parquet"
    source.parent.mkdir(parents=True)
    rows = [{
        "t": BASE + offset,
        "action": "T",
        "side": "B",
        "price": 100.0,
        "size": 1,
        "bid_px": 99.75,
        "ask_px": 100.0,
        "bid_sz": 3,
        "ask_sz": 5,
        "instrument_id": 42,
        "flags": 0,
    } for offset in range(1, 7)]
    pq.write_table(pa.Table.from_pylist(rows), source, row_group_size=2)
    real = pq.ParquetFile(source)
    groups_read = []

    class SpyParquetFile:
        schema_arrow = real.schema_arrow
        metadata = real.metadata
        num_row_groups = real.num_row_groups

        def iter_batches(self, *args, **kwargs):
            groups_read.extend(kwargs["row_groups"])
            return real.iter_batches(*args, **kwargs)

    monkeypatch.setattr(pq, "ParquetFile", lambda _path: SpyParquetFile())
    ownership = {
        "owned_spans": [{
            "path": str(source),
            "start_ns": BASE,
            "end_ns": BASE + 10,
            "kind": "monthly",
            "dataset": "nq-mbp-1",
            "status": "owned",
        }],
        "holes": [],
    }
    plan = plan_window(tmp_path / "raw", BASE + 3, BASE + 5, ownership=ownership)

    assert [row["event_ns"] for row in iter_mbp1_window(plan)] == [BASE + 3, BASE + 4]
    assert groups_read == [1]
