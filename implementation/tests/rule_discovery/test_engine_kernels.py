"""Numba kernels vs plain-Python references. Tests fail if a reference is removed."""

from __future__ import annotations

from decimal import Decimal
import inspect
import math

import numpy as np
import pytest

from trading_research.research.rule_discovery import kernels as kd
from trading_research.research.rule_discovery.delta import fixture_plus10_minus4_unknown6
from trading_research.research.rule_discovery.kernels import (
    C2_HALF_LIFE_NS,
    KERNEL_NAMES,
    MINUTE_NS,
    NS,
    PYTHON_REFERENCE_NAMES,
    ST_CONFIRMED,
    ST_SWEPT,
    relative_close,
    warmup_kernels,
)
from trading_research.errors import ContractError
from trading_research.research.rule_discovery.native import price_to_ticks, price_to_units, python_vwap
from trading_research.research.rule_discovery.source_adapters.common import (
    _synth_bar,
    enumerate_lifecycle_contacts,
    quadrant_locations,
    ten_bar_dwell_contacts,
)


def test_python_references_are_present_and_not_kernels():
    for name in PYTHON_REFERENCE_NAMES:
        fn = getattr(kd, name)
        source = inspect.getsource(fn)
        assert "@njit" not in source
        assert "njit(" not in source
        assert name.replace("python_", "") + "_kernel" not in source
        assert "for " in source
    for name in KERNEL_NAMES:
        fn = getattr(kd, name)
        source = inspect.getsource(fn)
        assert "@njit" in source


def test_spec_delta_fixture_plus10_minus4_unknown6():
    batch = fixture_plus10_minus4_unknown6()
    assert batch["delta"] == 6
    assert batch["volume"] == 20
    assert batch["unknown"] == 6
    assert batch["known_ratio"] == pytest.approx(6 / 14)
    assert batch["unknown_share"] == pytest.approx(0.30)
    assert batch["normalized_admitted"] is False
    signed, volume, unknown, ratio, admitted = kd.python_delta_imbalance([10, 4, 6], [1, -1, 0])
    k_signed, k_volume, k_unknown, k_ratio, k_admitted = kd.delta_imbalance_kernel(
        np.array([10, 4, 6], dtype=np.int64),
        np.array([1, -1, 0], dtype=np.int64),
    )
    assert (signed, volume, unknown, admitted) == (6, 20, 6, 0)
    assert (int(k_signed), int(k_volume), int(k_unknown), int(k_admitted)) == (6, 20, 6, 0)
    assert ratio == k_ratio == pytest.approx(6 / 14)
    assert relative_close(ratio, k_ratio)


def test_spec_f2_overshoot_eight_plus_three_plus_three():
    newest_first = [3, 3, 8]
    minutes, overshoot, cumulative = kd.python_f2_walk(newest_first, 10)
    k_minutes, k_overshoot, k_cumulative = kd.f2_walk_kernel(np.array(newest_first, dtype=np.int64), np.int64(10), np.int64(180))
    assert (minutes, overshoot, cumulative) == (3, 4, 14)
    assert (int(k_minutes), int(k_overshoot), int(k_cumulative)) == (3, 4, 14)


def test_spec_vwap_two_and_two():
    price, _disp, volume = python_vwap([400, 404], [2, 2])
    assert price == Decimal("100.50")
    assert volume == 4


def test_c2_halves_after_one_half_life():
    zs, ks, _norms = kd.python_c2_fold([0, C2_HALF_LIFE_NS], [10, 0], [10, 0])
    k_zs, k_ks, k_norms = kd.c2_fold_kernel(
        np.array([0, C2_HALF_LIFE_NS], dtype=np.int64),
        np.array([10, 0], dtype=np.int64),
        np.array([10, 0], dtype=np.int64),
        np.int64(C2_HALF_LIFE_NS),
    )
    assert zs[0] == pytest.approx(10.0)
    assert zs[1] == pytest.approx(5.0)
    assert ks[1] == pytest.approx(5.0)
    assert relative_close(zs[1], float(k_zs[1]))
    assert relative_close(ks[1], float(k_ks[1]))
    assert relative_close(float(k_norms[1]), 1.0)


def test_ten_bar_dwell_is_one_lifecycle_contact():
    result = ten_bar_dwell_contacts()
    assert result["n_bars"] == 10
    assert result["n_contacts"] == 1
    high = [410] * 10
    low = [406] * 10
    python_idx = kd.python_lifecycle_contacts(high, low, 408, 408, 4)
    kernel_idx = list(kd.contact_lifecycle_kernel(np.array(high, dtype=np.int64), np.array(low, dtype=np.int64), np.int64(408), np.int64(408), np.int64(4)))
    assert python_idx == kernel_idx == [0]


def test_departure_rearms_a_second_contact():
    high = [410, 410, 420, 410]
    low = [406, 406, 419, 406]
    python_idx = kd.python_lifecycle_contacts(high, low, 408, 408, 4)
    kernel_idx = list(kd.lifecycle_contact_indices(high, low, 408, 408, 4))
    assert python_idx == kernel_idx == [0, 3]


def test_spec_rearm_requires_complete_outside_bar():
    high = [410, 420, 410]
    low = [406, 419, 406]
    four_tick = kd.python_lifecycle_contacts(high, low, 408, 408, 4)
    spec = kd.python_rearm_contacts(high, low, 408, 408, scale_ticks=10)
    k_spec = list(kd.rearm_contacts_kernel(np.array(high, dtype=np.int64), np.array(low, dtype=np.int64), np.int64(408), np.int64(408), np.int64(10)))
    assert four_tick == [0, 2]
    assert spec == k_spec == [0, 2]


def test_sweep_and_s1_reclaim():
    high = [400, 400, 399, 401]
    low = [399, 395, 398, 400]
    first, extreme, disp = kd.python_sweep_displacement(high, low, 399, 401, 1)
    k_first, k_extreme, k_disp = kd.sweep_displacement_kernel(
        np.array(high, dtype=np.int64), np.array(low, dtype=np.int64), np.int64(399), np.int64(401), np.int64(1)
    )
    assert (first, extreme, disp) == (int(k_first), int(k_extreme), int(k_disp)) == (1, 395, 4)
    close = [400, 396, 399, 400]
    state, sweep_i, confirm_i = kd.python_s1_machine(high, low, close, 399, 401, 1, 0, 3)
    k_state, k_sweep, k_confirm = kd.s1_machine_kernel(
        np.array(high, dtype=np.int64),
        np.array(low, dtype=np.int64),
        np.array(close, dtype=np.int64),
        np.int64(399),
        np.int64(401),
        np.int64(1),
        np.int64(0),
        np.int64(3),
    )
    assert state == int(k_state) == ST_CONFIRMED
    assert sweep_i == int(k_sweep) == 1
    assert confirm_i == int(k_confirm) == 2
    assert ST_SWEPT == 1


def test_s2_reclaim_then_defended_retest():
    high = [400, 400, 400, 400]
    low = [399, 395, 399, 398]
    close = [400, 396, 400, 401]
    python = kd.python_s2_machine(high, low, close, 399, 401, 1, 0, 3)
    kernel = kd.s2_machine_kernel(
        np.array(high, dtype=np.int64),
        np.array(low, dtype=np.int64),
        np.array(close, dtype=np.int64),
        np.int64(399),
        np.int64(401),
        np.int64(1),
        np.int64(0),
        np.int64(3),
    )
    assert python == tuple(int(v) for v in kernel)
    assert python[0] == ST_CONFIRMED
    assert python[1] == 1
    assert python[2] == 2
    assert python[3] == 3


def test_s3_missing_c1_is_input_unknown_and_gate_rejects():
    high = [400, 400, 399, 401]
    low = [399, 395, 398, 400]
    close = [400, 396, 399, 400]
    missing = kd.python_s3_machine(high, low, close, 399, 401, 1, 0, 3, 0.0, 0, 0.0, 0, 0)
    k_missing = kd.s3_machine_kernel(
        np.array(high, dtype=np.int64),
        np.array(low, dtype=np.int64),
        np.array(close, dtype=np.int64),
        np.int64(399),
        np.int64(401),
        np.int64(1),
        np.int64(0),
        np.int64(3),
        0.0,
        np.int64(0),
        0.0,
        np.int64(0),
        np.int64(0),
    )
    assert missing == tuple(int(v) for v in k_missing)
    assert missing[0] == kd.ST_INPUT_UNKNOWN
    weak = kd.python_s3_machine(high, low, close, 399, 401, 1, 0, 3, 0.10, 1, 0.5, 1, 0)
    k_weak = kd.s3_machine_kernel(
        np.array(high, dtype=np.int64),
        np.array(low, dtype=np.int64),
        np.array(close, dtype=np.int64),
        np.int64(399),
        np.int64(401),
        np.int64(1),
        np.int64(0),
        np.int64(3),
        0.10,
        np.int64(1),
        0.5,
        np.int64(1),
        np.int64(0),
    )
    assert weak == tuple(int(v) for v in k_weak)
    assert weak[0] == ST_SWEPT
    ok = kd.python_s3_machine(high, low, close, 399, 401, 1, 0, 3, 0.30, 1, 0.5, 1, 0)
    k_ok = kd.s3_machine_kernel(
        np.array(high, dtype=np.int64),
        np.array(low, dtype=np.int64),
        np.array(close, dtype=np.int64),
        np.int64(399),
        np.int64(401),
        np.int64(1),
        np.int64(0),
        np.int64(3),
        0.30,
        np.int64(1),
        0.5,
        np.int64(1),
        np.int64(0),
    )
    assert ok == tuple(int(v) for v in k_ok)
    assert ok[0] == ST_CONFIRMED


def test_quadrant_bound_not_on_whole_tick_enumerates():
    low, high = Decimal("100.00"), Decimal("108.50")
    loc = quadrant_locations(low, high, "long")
    assert loc["q1"] == Decimal("102.125")
    with pytest.raises(ContractError, match="integer NQ tick"):
        price_to_ticks(loc["q1"])
    assert price_to_units(loc["q1"]) == 1021250
    bars = [_synth_bar(0, Decimal("102.00"), Decimal("102.25"), bar_id="Q1")]
    contacts = enumerate_lifecycle_contacts(
        bars, lower=loc["q1"], upper=loc["q1"], reference_id="ref-q1", side="long", reference_lifecycle_id="life-q1"
    )
    assert len(contacts) == 1
    assert contacts[0]["low"] == "102.00"
    miss = enumerate_lifecycle_contacts(
        [_synth_bar(0, Decimal("101.00"), Decimal("101.50"), bar_id="M")],
        lower=loc["q1"],
        upper=loc["q1"],
        reference_id="ref-q1",
        side="long",
    )
    assert miss == []


def test_s4_unknown_aggression_is_input_unknown():
    state, event_i = kd.python_s4_machine(
        opposing=[0, -1],
        quantile=2,
        adverse_ticks=[0, 0],
        cap_ticks=2,
        close=[100, 101],
        contact_extreme=100,
        side=1,
        contact_i=0,
        pressure_last_i=1,
        deadline_i=1,
    )
    k_state, k_event = kd.s4_machine_kernel(
        np.array([0, -1], dtype=np.int64),
        np.int64(2),
        np.array([0, 0], dtype=np.int64),
        np.int64(2),
        np.array([100, 101], dtype=np.int64),
        np.int64(100),
        np.int64(1),
        np.int64(0),
        np.int64(1),
        np.int64(1),
    )
    assert state == int(k_state) == kd.ST_INPUT_UNKNOWN
    assert event_i == int(k_event) == 1


def test_book_observe_deplete_and_replenish():
    bid = [100, 99, 100]
    ask = [101, 101, 101]
    sz = [4, 0, 2]
    ask_sz = [1, 1, 1]
    python = kd.python_book_observe(bid, ask, sz, ask_sz, 100, 1)
    kernel = kd.book_observe_kernel(
        np.array(bid, dtype=np.int64),
        np.array(ask, dtype=np.int64),
        np.array(sz, dtype=np.int64),
        np.array(ask_sz, dtype=np.int64),
        np.int64(100),
        np.int64(1),
    )
    assert python == tuple(int(v) for v in kernel) == (2, 1, 1, 1)


def test_profile_accumulate_literal_bins():
    ticks = [100, 100, 101, 102, 102, 102]
    sizes = [10, 5, 4, 8, 8, 5]
    python = kd.python_profile_accumulate(ticks, sizes, 100, 3)
    kernel = list(kd.profile_accumulate_kernel(np.array(ticks, dtype=np.int64), np.array(sizes, dtype=np.int64), np.int64(100), np.int64(3)))
    assert python == kernel == [15, 4, 21]
    assert sum(python) == 40


def test_minute_bars_match_on_gap_and_unknown_aggressor():
    t_ns = [0, MINUTE_NS, 3 * MINUTE_NS]
    ticks = [400, 402, 399]
    size = [1, 3, 2]
    side = [1, 0, -1]
    known = [0, MINUTE_NS, 3 * MINUTE_NS]
    python = kd.python_minute_bars(t_ns, ticks, size, side, known, 0, 4 * MINUTE_NS)
    kernel = kd.minute_bars_kernel(
        np.array(t_ns, dtype=np.int64),
        np.array(ticks, dtype=np.int64),
        np.array(size, dtype=np.int64),
        np.array(side, dtype=np.int64),
        np.array(known, dtype=np.int64),
        np.int64(0),
        np.int64(4 * MINUTE_NS),
    )
    assert python["open_ticks"] == list(kernel[2])
    assert python["high_ticks"] == list(kernel[3])
    assert python["low_ticks"] == list(kernel[4])
    assert python["close_ticks"] == list(kernel[5])
    assert python["volume"] == list(kernel[6])
    assert python["signed"] == list(kernel[7])
    assert python["unknown"] == list(kernel[8])
    assert python["volume"] == [1, 3, 2]
    assert python["unknown"] == [0, 3, 0]


def test_markout_arrays_unresolved_does_not_borrow():
    python = kd.python_markout_arrays(
        sign=[1, 1],
        qty=[10, 1],
        price=[100.0, 100.0],
        event_ns=[0, 0],
        mid=[101.0, float("nan")],
        mid_available_ns=[30 * NS, 30 * NS],
        horizon_ns=30 * NS,
        snapshot_ns=60 * NS,
    )
    kernel = kd.markout_arrays_kernel(
        np.array([1, 1], dtype=np.int64),
        np.array([10, 1], dtype=np.int64),
        np.array([100.0, 100.0], dtype=np.float64),
        np.array([0, 0], dtype=np.int64),
        np.array([101.0, math.nan], dtype=np.float64),
        np.array([30 * NS, 30 * NS], dtype=np.int64),
        np.int64(30 * NS),
        np.int64(60 * NS),
    )
    assert python[0] == pytest.approx(10.0)
    assert python[1] == 10
    assert python[4] == 1
    assert relative_close(python[0], float(kernel[0]))
    assert int(kernel[1]) == 10
    assert int(kernel[4]) == 1


def test_randomized_arrays_match_references():
    rng = np.random.default_rng(20260915)
    n = 400
    high = rng.integers(390, 420, size=n).astype(np.int64)
    low = high - rng.integers(0, 6, size=n)
    t_ns = np.cumsum(rng.integers(1, 5, size=n).astype(np.int64)) * (NS // 4)
    t_ns[50:53] = t_ns[50]
    size = rng.integers(1, 20, size=n).astype(np.int64)
    side = rng.choice(np.array([-1, 0, 1], dtype=np.int64), size=n)
    ticks = ((high + low) // 2).astype(np.int64)
    known = t_ns.copy()
    lo, hi = 400, 405
    py_c = kd.python_lifecycle_contacts(high.tolist(), low.tolist(), lo, hi, 4)
    k_c = list(kd.contact_lifecycle_kernel(high, low, np.int64(lo), np.int64(hi), np.int64(4)))
    assert py_c == k_c
    py_s = kd.python_sweep_displacement(high.tolist(), low.tolist(), lo, hi, 1)
    k_s = kd.sweep_displacement_kernel(high, low, np.int64(lo), np.int64(hi), np.int64(1))
    assert py_s == (int(k_s[0]), int(k_s[1]), int(k_s[2]))
    py_d = kd.python_delta_imbalance(size.tolist(), side.tolist())
    k_d = kd.delta_imbalance_kernel(size, side)
    assert py_d[0:3] == (int(k_d[0]), int(k_d[1]), int(k_d[2]))
    assert py_d[4] == int(k_d[4])
    assert relative_close(py_d[3], float(k_d[3]))
    py_bars = kd.python_minute_bars(t_ns.tolist(), ticks.tolist(), size.tolist(), side.tolist(), known.tolist(), int(t_ns[0]), int(t_ns[-1] + MINUTE_NS))
    k_bars = kd.minute_bars_kernel(t_ns, ticks, size, side, known, np.int64(t_ns[0]), np.int64(t_ns[-1] + MINUTE_NS))
    assert py_bars["volume"] == list(k_bars[6])
    assert py_bars["signed"] == list(k_bars[7])
    assert py_bars["unknown"] == list(k_bars[8])
    min_tick = int(ticks.min())
    n_bins = int(ticks.max() - min_tick + 1)
    py_p = kd.python_profile_accumulate(ticks.tolist(), size.tolist(), min_tick, n_bins)
    k_p = list(kd.profile_accumulate_kernel(ticks, size, np.int64(min_tick), np.int64(n_bins)))
    assert py_p == k_p


def test_f3_first_length_on_wide_then_balance():
    open_ticks = [40000] * 60 + [40000] * 15 + [39960] + [40000] * 14
    high_ticks = [40100] * 60 + [40040] * 30
    low_ticks = [39900] * 60 + [39960] * 30
    close_ticks = [40000] * 90
    python = kd.python_f3_first(open_ticks, high_ticks, low_ticks, close_ticks)
    kernel = int(kd.f3_first_kernel(np.array(open_ticks, dtype=np.int64), np.array(high_ticks, dtype=np.int64), np.array(low_ticks, dtype=np.int64), np.array(close_ticks, dtype=np.int64)))
    assert python == kernel == 30


def test_warmup_compiles():
    warmup_kernels()
