"""Recovery uses disposable seconds and never replaces existing native minutes."""

import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from trading_research.research.method_pack.minute_recovery import (
    MINUTE_DATASET, SECOND_DATASET, gap_requests, recover_minutes,
)
from trading_research.research.method_pack.mbp1_views import TapeError


BASE = 1_704_153_600_000


def write(root, dataset, rows):
    path = root / dataset / "2024.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), path, row_group_size=2)
    return path


def second(offset, instrument=42, price=100, volume=1):
    return {"t": BASE + offset, "instrument_id": instrument, "o": price,
            "h": price + 1, "l": price - 1, "c": price + .5, "v": volume}


def test_recovers_only_missing_contract_minutes_and_preserves_raw(tmp_path):
    root, out = tmp_path / "raw", tmp_path / "out"
    source = write(root, SECOND_DATASET, [second(1000), second(59000, price=102, volume=3),
                                        second(60000, price=105), second(61000, instrument=43, price=200)])
    write(root, MINUTE_DATASET, [second(60000, price=105)])
    before = source.read_bytes()
    result = recover_minutes(root, out, [{"t": BASE, "instrument_id": 42},
                                         {"t": BASE + 60000, "instrument_id": 42},
                                         {"t": BASE + 60000, "instrument_id": 43}])
    bars = [json.loads(line) for line in Path(result["artifact"]["path"]).read_text().splitlines()]
    assert result["recovered_keys"] == 2 and result["already_present_keys"] == 1
    assert result["unresolved_keys"] == [] and source.read_bytes() == before
    assert (bars[0]["O"], bars[0]["H"], bars[0]["L"], bars[0]["C"], bars[0]["V"]) == ("100", "103", "99", "102.5", "4")
    assert bars[0]["observed_second_count"] == 2 and bars[0]["complete"] is None
    assert bars[0]["known_at"] == (BASE + 60000) * 1_000_000
    assert bars[1]["instrument_id"] == 43


def test_duplicate_second_is_not_summed_or_deduplicated(tmp_path):
    root = tmp_path / "raw"
    write(root, SECOND_DATASET, [second(1000), second(1000)])
    with pytest.raises(TapeError, match="duplicate"):
        recover_minutes(root, tmp_path / "out", [{"t": BASE, "instrument_id": 42}])


def test_missing_seconds_stay_unresolved_and_raw_destination_rejected(tmp_path):
    root = tmp_path / "raw"
    write(root, SECOND_DATASET, [second(1000)])
    wanted = [{"t": BASE + 60000, "instrument_id": 42}]
    with pytest.raises(ValueError, match="outside"):
        recover_minutes(root, root / "derived", wanted)
    result = recover_minutes(root, tmp_path / "out", wanted)
    assert result["recovered_keys"] == 0
    assert result["unresolved_keys"] == [{"t": BASE + 60000, "instrument_id": "42"}]


def test_audit_manifest_has_explicit_ns_conversion():
    request = {"minute_start_ns": BASE * 1_000_000, "instrument_id": 42}
    assert gap_requests({"missing_keys": [request]}) == [{"t": BASE, "instrument_id": 42}]
    with pytest.raises(ValueError, match="conflicting"):
        gap_requests({"missing_keys": [{**request, "t": BASE + 60000}]})
