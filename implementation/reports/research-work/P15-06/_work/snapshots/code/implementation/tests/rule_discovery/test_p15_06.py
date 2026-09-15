"""P15-06 CVD variants and resolved cohort memory."""
from __future__ import annotations

from pathlib import Path

import pytest

from trading_research.research.method_pack.historical_features import delta as frozen_delta
from trading_research.research.rule_discovery.cohorts import (
    HORIZONS,
    appending_unresolved_does_not_mark_out,
    markout,
    memory_features,
)
from trading_research.research.rule_discovery.delta import (
    UNKNOWN_GATE,
    batch_delta,
    c2_step,
    decay_factor,
    emit_features,
    fixture_plus10_minus4_unknown6,
    frozen_delta_ignores_unknown,
    python_c2_series,
)
from trading_research.research.rule_discovery.native import python_cvd, replay_native_row


def test_a01_unknown_volume_is_never_zero():
    result = fixture_plus10_minus4_unknown6()
    assert result["delta"] == 6
    assert result["volume"] == 20
    assert result["unknown"] == 6
    assert result["known"] == 14
    assert result["known_ratio"] == pytest.approx(6 / 14)
    assert result["unknown_share"] == pytest.approx(0.30)
    assert result["normalized_admitted"] is False
    assert result["unknown_share"] > UNKNOWN_GATE
    signed, volume, unknown = python_cvd([10, 4, 6], [1, -1, 0])
    assert (signed, volume, unknown) == (6, 20, 6)
    assert frozen_delta_ignores_unknown(10, 4, 6) == 6
    assert frozen_delta_ignores_unknown(0, 0, 6) == 0


def test_a02_half_life_halves_after_300s():
    z, k, _n = c2_step(10.0, 10.0, 0, 0, 300_000_000_000)
    assert z == pytest.approx(5.0)
    assert k == pytest.approx(5.0)
    assert decay_factor(300_000_000_000) == pytest.approx(0.5)
    series = python_c2_series([(0, 10, 10), (300_000_000_000, 0, 0)])
    assert series[-1]["z"] == pytest.approx(5.0)


def test_a03_unresolved_cohort_has_no_future_markout():
    trades = [
        {"sign": 1, "qty": 2, "price": 100.0, "event_ns": 0, "mid_at_horizon": 101.0, "mid_available_ns": 30_000_000_000},
        {"sign": 1, "qty": 3, "price": 100.0, "event_ns": 1_000_000_000, "mid_at_horizon": None, "mid_available_ns": None},
    ]
    before = markout(trades[:1], horizon_s=30, snapshot_ns=30_000_000_000)
    after = markout(trades, horizon_s=30, snapshot_ns=30_000_000_000)
    assert before["buy"]["mean"] == after["buy"]["mean"]
    assert after["unresolved"] == 1
    mutated = appending_unresolved_does_not_mark_out(before, 1)
    assert mutated["buy_mean_unchanged"] == before["buy"]["mean"]
    future_mid = markout(
        [{"sign": 1, "qty": 2, "price": 100.0, "event_ns": 0, "mid_at_horizon": 120.0, "mid_available_ns": 40_000_000_000}],
        horizon_s=30,
        snapshot_ns=30_000_000_000,
    )
    assert future_mid["buy"]["mean"] is None
    assert future_mid["unresolved"] == 1


def test_a04_high_cvd_is_not_rewarded_buying():
    trades = [{"sign": 1, "qty": 10, "price": 100.0, "event_ns": 0, "mid_at_horizon": 99.0, "mid_available_ns": 30_000_000_000}]
    result = markout(trades, horizon_s=30, snapshot_ns=30_000_000_000)
    assert result["rewarded_buyers"] is False
    batch = batch_delta([10], [1])
    assert batch["delta"] == 10
    assert result["buy"]["mean"] < 0


def test_a05_variants_emitted_with_lineage():
    batch = fixture_plus10_minus4_unknown6()
    features = emit_features(batch, available_at_ns=10)
    names = {item.name for item in features}
    assert {"C0", "C1", "C3"} <= names
    c1 = next(item for item in features if item.name == "C1")
    assert c1.value is None
    assert "unknown" in (c1.missing_reason or "")
    c0 = next(item for item in features if item.name == "C0")
    assert c0.value == 6.0
    assert c0.evidence[0].row_ids


def test_s09_same_timestamp_batch_does_not_invent_aggressor():
    result = batch_delta([5, 5], [0, 0])
    assert result["delta"] == 0
    assert result["unknown"] == 10
    assert result["normalized_admitted"] is False


def test_s11_missing_horizon_is_unknown_not_zero():
    trades = [{"sign": 1, "qty": 4, "price": 10.0, "event_ns": 0, "mid_at_horizon": None, "mid_available_ns": None}]
    result = markout(trades, horizon_s=120, snapshot_ns=10)
    assert result["buy"]["mean"] is None
    assert result["unresolved"] == 1
    assert result["buy"]["volume"] == 0


def test_s14_literal_vector_and_mirror():
    long = batch_delta([10, 4], [1, -1])
    short = batch_delta([10, 4], [-1, 1])
    assert long["delta"] == -short["delta"]
    assert long["volume"] == short["volume"]


def test_s23_resolved_only_updates_memory():
    memory = memory_features(
        touch_count=1,
        formation_ns=0,
        last_contact_ns=5,
        now_ns=15,
        pre_touch_departure=True,
        signed_volume_at_band=3,
        prior_resolved=[{"available": True, "mean": 0.5}, {"available": False, "mean": 9.0}],
    )
    assert memory["prior_favorable_count"] == 1
    assert memory["prior_resolved_count"] == 2


def test_s07_native_replay():
    path = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
    if not Path(path).is_file():
        pytest.skip("native parquet missing")
    row = replay_native_row(path, 769284)
    assert row["kind"] == "native"


def test_horizons_registered():
    assert HORIZONS == (30, 120, 300)


def test_frozen_delta_drops_unknown_column():
    class Footprint:
        def __init__(self):
            self.window = type("W", (), {"footprints": {}})()

    market = Footprint()
    market.window.footprints = {
        0: {"end": 1, "known_at": 1, "rows": [(100, 10, 4, 6)]},
    }
    assert frozen_delta(market, 0, 1) == 6
