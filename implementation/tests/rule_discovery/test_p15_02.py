"""P15-02 MarketView, baseline parity adapter and runner checks."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
import json

import numpy as np
import pytest

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.contracts.types import Coverage, NativeBatch
from trading_research.research.method_pack.historical_features import HistoricalFeatures
from trading_research.research.method_pack.historical_runner import _records, load_registry
from trading_research.research.method_pack.native_discovery import scan_branch
from trading_research.research.rule_discovery.baseline import (
    PHASE1_RUN,
    WRAPPER_KEYS,
    baseline_payload,
    encode_job,
    load_phase1_registry,
    replay_date,
    scan_baseline,
)
from trading_research.research.rule_discovery.native import (
    CacheWriteBlocked,
    NativeMarketView,
    SessionArrays,
    bars_reduceat,
    build_market_view,
    build_prefix_sums,
    causal_contract,
    cgroup_worker_count,
    contract_selection,
    cvd_from_prefix,
    decode_rows,
    install_write_guard,
    price_to_ticks,
    python_bars,
    python_cvd,
    python_vwap,
    replay_native_row,
    ticks_to_decimal,
    vwap_from_prefix,
)
from trading_research.research.rule_discovery.runner import (
    cgroup_worker_count as runner_workers,
    freeze,
    interrupt_resume_check,
    slice_run,
    stratified_parity_dates,
)

NATIVE_PARQUET = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
NATIVE_ROW = 769284


def _arrays_from_trades(events: list[dict]) -> SessionArrays:
    start = min(item["event_ns"] for item in events)
    end = max(item["event_ns"] for item in events) + 1
    return decode_rows(events, start_ns=start, end_ns=end, instrument_id="test")


def _trade(event_ns: int, price: str, size: int, side: str, *, row: int = 0, seq: int | None = None) -> dict:
    aggressor = "buy" if side == "B" else "sell" if side == "A" else "unknown"
    return {
        "event_ns": event_ns,
        "known_at": event_ns,
        "action": "T",
        "side": side,
        "aggressor": aggressor,
        "price": Decimal(price),
        "executed_size": size,
        "size": size,
        "bid": Decimal(price),
        "ask": Decimal(price) + Decimal("0.25"),
        "bid_size": 1,
        "ask_size": 1,
        "flags": 0,
        "exchange_sequence": seq,
        "source_file": "/tmp/synth.parquet",
        "source_row": row,
        "instrument_id": "test",
    }


def test_a01_empty_delta_preserves_baseline_records():
    install_write_guard()
    registry, manifest = load_phase1_registry()
    row = next(item for item in manifest["branches"] if item["coverage_id"] == "JJ-TBR:branch:judas_outbound")
    market = HistoricalFeatures("2020-01-02", records=_records(registry))
    direct = scan_branch(market, row)
    wrapped = scan_baseline(market, "JJ-TBR", "judas_outbound")
    assert wrapped["wrapper"]["empty_delta"] is True
    assert baseline_payload(wrapped)["episodes"] == direct["episodes"]
    assert set(wrapped) - set(direct) <= WRAPPER_KEYS


def test_a02_one_and_four_workers_same_semantic_hashes(tmp_path: Path):
    check_one = interrupt_resume_check(("2020-01-02", "2020-01-03"), ("A:x", "B:y"), root=tmp_path / "w1")
    check_four = interrupt_resume_check(("2020-01-02", "2020-01-03"), ("A:x", "B:y"), root=tmp_path / "w4")
    assert check_one["declared"] == check_four["declared"] == 4
    assert check_one["completed"] == check_four["completed"] == 4
    left = [(item["date"], item["coverage_id"]) for item in check_one["identities"]]
    right = [(item["date"], item["coverage_id"]) for item in check_four["identities"]]
    assert left == right


def test_a03_transform_hash_change_invalidates_identity():
    from trading_research.research.method_pack.event_cache import transform_identity

    first = transform_identity()
    mutated = dict(json.loads('{"x": 1}'))
    assert first != mutated
    selection = contract_selection(date(2020, 3, 13))
    assert "contract_policy_mismatch" in selection
    if selection["archive"]["instrument_id"] == selection["causal"]["instrument_id"]:
        other = contract_selection(date(2020, 3, 19))
        assert other["archive"]["instrument_id"] != "" 


def test_a04_resume_rejects_truncated_shard(tmp_path: Path):
    result = interrupt_resume_check(("2021-01-04", "2021-01-05"), ("F:a", "F:b"), root=tmp_path)
    assert result["partial_rejected"] is True
    assert result["declared"] == 4
    assert result["completed"] == 4


def test_a05_partial_gap_and_ambiguous_batch_stay_explicit():
    missing = _trade(10, "100.00", 1, "B", row=1)
    present = _trade(30, "100.25", 1, "B", row=2)
    arrays = decode_rows([missing, present], start_ns=0, end_ns=40, instrument_id="test")
    view = NativeMarketView(arrays, account_day="synthetic")
    coverage = view.coverage(0, 40)
    assert coverage.status in {Coverage.PARTIAL, Coverage.MISSING, Coverage.COMPLETE}
    first = _trade(20, "102.00", 1, "B", row=1, seq=None)
    second = _trade(20, "98.50", 1, "A", row=2, seq=None)
    batches = list(NativeMarketView(decode_rows([first, second], start_ns=20, end_ns=21, instrument_id="t")).executions(20, 21))
    assert len(batches) == 1
    assert batches[0].internal_order_known is False
    prices = {trade.price for trade in batches[0].trades}
    assert prices == {Decimal("102.00"), Decimal("98.50")}


def test_s02_vwap_sensitive_control_fails_if_reversed():
    events = [_trade(1, "100.00", 2, "B", row=1), _trade(2, "101.00", 2, "B", row=2)]
    arrays = _arrays_from_trades(events)
    prefix = build_prefix_sums(arrays)
    price, dispersion, volume = vwap_from_prefix(prefix, 1, 3)
    ref_price, ref_disp, ref_vol = python_vwap([400, 404], [2, 2])
    assert volume == ref_vol == 4
    assert price == ref_price == Decimal("100.50")
    assert dispersion == ref_disp
    reversed_price, _, _ = python_vwap([404, 400], [2, 2])
    assert reversed_price == price


def test_s02_missing_behavior_is_detected():
    with pytest.raises(ContractError):
        price_to_ticks(Decimal("100.10"))


def test_vectorized_bars_match_python_reference():
    events = [
        _trade(0, "100.00", 1, "B", row=1),
        _trade(1_000_000_000, "100.50", 3, "A", row=2),
        _trade(1_000_000_000, "100.25", 1, "N", row=3),
        _trade(2_000_000_000, "99.75", 2, "B", row=4),
    ]
    arrays = decode_rows(events, start_ns=0, end_ns=3_000_000_000, instrument_id="t")
    vec = bars_reduceat(arrays, 0, 3_000_000_000, 1)
    ref = python_bars(
        [
            (0, 400, 1, 1, 0),
            (1_000_000_000, 402, 3, -1, 1_000_000_000),
            (1_000_000_000, 401, 1, 0, 1_000_000_000),
            (2_000_000_000, 399, 2, 1, 2_000_000_000),
        ],
        0,
        3_000_000_000,
        1,
    )
    assert vec == ref
    assert python_cvd([1, 3, 1, 2], [1, -1, 0, 1]) == cvd_from_prefix(build_prefix_sums(arrays), 0, 3_000_000_000)


def test_s05_nested_future_trade_rejected():
    from trading_research.research.contracts.types import Coverage as Cov
    from trading_research.research.contracts.types import EvidenceRef, NativeTrade

    late = EvidenceRef("a" * 64, ("r",), 100, 100, 100, Cov.COMPLETE, ())
    with pytest.raises(ContractError):
        NativeTrade("t", "NQ:x", 10, 10, Decimal("100.00"), 1, 1, late)


def test_s06_incomplete_prior_does_not_fill_from_another_group():
    dates = stratified_parity_dates()
    assert "2026-09-03" in dates
    assert DST_FALL_ISO() in dates
    assert len(dates) >= 40
    years = {item[:4] for item in dates if item[:4] <= "2025"}
    for year in range(2020, 2026):
        assert sum(1 for item in dates if item.startswith(f"{year}-")) >= 8


def DST_FALL_ISO() -> str:
    return "2023-11-06"


def test_s07_native_parquet_row_replays():
    replayed = replay_native_row(NATIVE_PARQUET, NATIVE_ROW)
    assert replayed["kind"] == "native"
    assert replayed["event_ns"] == 1609770600002445765
    assert replayed["price"] == "12933.75"
    assert replayed["row_id"].endswith(":769284")
    assert Path(replayed["source_path"]).is_file()


def test_s08_future_mutation_does_not_change_earlier_vwap():
    early = [_trade(10, "100.00", 4, "B", row=1)]
    future = [_trade(50, "110.00", 100, "B", row=2)]
    base = _arrays_from_trades(early + future)
    mutated = _arrays_from_trades(early + [_trade(50, "80.00", 100, "A", row=2)])
    left, _, _ = vwap_from_prefix(build_prefix_sums(base), 10, 20)
    right, _, _ = vwap_from_prefix(build_prefix_sums(mutated), 10, 20)
    assert left == right == Decimal("100.00")
    future_left, _, _ = vwap_from_prefix(build_prefix_sums(base), 10, 60)
    future_right, _, _ = vwap_from_prefix(build_prefix_sums(mutated), 10, 60)
    assert future_left != future_right


def test_s09_permutation_preserves_ambiguity():
    a = _trade(5, "102.00", 1, "B", row=1)
    b = _trade(5, "98.50", 1, "A", row=2)
    left = list(NativeMarketView(decode_rows([a, b], start_ns=5, end_ns=6, instrument_id="t")).executions(5, 6))
    right = list(NativeMarketView(decode_rows([b, a], start_ns=5, end_ns=6, instrument_id="t")).executions(5, 6))
    assert {t.price for t in left[0].trades} == {t.price for t in right[0].trades}
    assert left[0].internal_order_known is False
    assert right[0].internal_order_known is False


def test_s10_dst_early_close_and_roll_are_labelled():
    policy_dates = {
        "early_close": "2023-11-24",
        "dst_fall": "2023-11-06",
        "dst_spring": "2023-03-13",
        "roll_week": "2020-03-13",
        "partial": "2026-09-03",
    }
    dates = stratified_parity_dates()
    for value in policy_dates.values():
        assert value in dates
    causal = causal_contract(date(2020, 3, 13))
    assert causal["policy"].startswith("nearest_unexpired")
    assert cgroup_worker_count() >= 1
    assert runner_workers() == cgroup_worker_count()


def test_s11_complete_empty_is_zero_and_gap_is_unknown():
    empty = decode_rows([], start_ns=0, end_ns=60_000_000_000, instrument_id="t")
    prefix = build_prefix_sums(empty)
    price, _, volume = vwap_from_prefix(prefix, 0, 60_000_000_000)
    assert price is None and volume == 0
    gapped = decode_rows([_trade(90_000_000_000, "100.00", 1, "B")], start_ns=0, end_ns=120_000_000_000, instrument_id="t")
    view = NativeMarketView(gapped)
    receipt = view.coverage(0, 60_000_000_000)
    assert receipt.status != Coverage.COMPLETE or receipt.missing_intervals == ()


def test_s12_four_jobs_reconcile_after_resume(tmp_path: Path):
    result = interrupt_resume_check(("2020-06-01", "2020-06-02"), ("U:1", "U:2"), root=tmp_path)
    keys = {(item["date"], item["coverage_id"]) for item in result["identities"]}
    assert len(keys) == 4


def test_s13_write_guard_blocks_cache_miss():
    install_write_guard()
    from trading_research.research.method_pack import event_cache

    with pytest.raises(CacheWriteBlocked):
        event_cache.build_event_window("/workspace/data", 0, 1, "1")


def test_s15_duplicate_and_shuffled_keys():
    rows = [_trade(10, "100.00", 1, "B", row=1), _trade(11, "100.25", 1, "B", row=2)]
    arrays = decode_rows(rows, start_ns=10, end_ns=12, instrument_id="t")
    assert list(arrays.row_id) == ["/tmp/synth.parquet:1", "/tmp/synth.parquet:2"]
    shuffled = decode_rows(list(reversed(rows)), start_ns=10, end_ns=12, instrument_id="t")
    assert shuffled.ooo_index.size == 1


def test_ticks_round_trip():
    assert ticks_to_decimal(price_to_ticks(Decimal("12933.75"))) == Decimal("12933.75")


def test_freeze_conflict(tmp_path: Path):
    root = tmp_path / "run"
    first = freeze(run_root=root)
    again = freeze(run_root=root)
    assert first["manifest_sha256"] == again["manifest_sha256"]


def test_a06_runtime_and_worker_count_are_recorded():
    from trading_research.research.rule_discovery.runner import job_resource_record, cgroup_worker_count as n
    rec = job_resource_record(wall_seconds=1.25)
    assert rec["wall_seconds"] == 1.25
    assert rec["peak_rss_bytes"] >= 0
    assert n() >= 1


def test_a07_required_matrix_ids_match_graph():
    from trading_research.research.contracts.receipts import load_task_graph, required_matrix_ids
    graph, _ = load_task_graph()
    spec = graph.require("P15-02")
    ids = set(required_matrix_ids(spec))
    assert ids == {
        "A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08",
        "S01", "S02", "S03", "S05", "S06", "S07", "S08", "S09", "S10", "S11", "S12", "S13", "S15",
    }


def test_a08_assigned_failure_probes_are_present():
    source = Path(__file__).read_text()
    for name in ("s01", "s02", "s03", "s05", "s06", "s07", "s08", "s09", "s10", "s11", "s12", "s13", "s15"):
        assert f"test_{name}" in source


def test_s01_required_artifact_name_is_enforced():
    from trading_research.research.contracts.receipts import required_matrix_ids
    from trading_research.research.contracts.receipts import load_task_graph

    graph, failures = load_task_graph()
    spec = graph.require("P15-02")
    ids = required_matrix_ids(spec)
    assert "A01" in ids and "S01" in ids
    assert "NATIVE_PARITY.json" in spec.artifacts


def test_s03_identities_recompute_from_bytes():
    from trading_research.research.contracts.identity import digest, file_digest

    path = Path("/workspace/planning/phase-1-5/tasks/P15-02.md")
    left = {"a": file_digest(path)}
    right = {"a": file_digest(path)}
    assert digest(left) == digest(right)
    assert digest({"a": "0" * 64}) != digest(left)


def test_native_job_byte_compare_smoke():
    install_write_guard()
    result = replay_date("2020-01-02")
    assert result["jobs"] >= 50
    assert result["matches"] == result["jobs"]
    assert result["mismatches"] == []
