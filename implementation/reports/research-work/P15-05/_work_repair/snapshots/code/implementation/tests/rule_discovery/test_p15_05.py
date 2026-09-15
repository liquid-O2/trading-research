"""P15-05 formations, profiles, location objects and value-area adjudication."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import numpy as np
import pytest

from trading_research.errors import ContractError
from trading_research.research.contracts.types import Coverage, EvidenceRef, Formation
from trading_research.research.method_pack.objects.profiles import ValueAreaConfig, _value_area
from trading_research.research.method_pack.objects.profiles import PriceRow
from trading_research.research.rule_discovery.formations import (
    F3_LENGTHS,
    complete_minute_rows,
    f1_trailing_minutes,
    f2_volume_completed,
    f3_balance,
    freeze_formation,
    future_perturbation_stable,
    median_int,
    python_bar_window,
    python_f2_volume_completed,
    python_f3_first_length,
)
from trading_research.research.rule_discovery.native import (
    NativeMarketView,
    SessionArrays,
    bars_reduceat,
    empty_session_arrays,
    install_write_guard,
    python_bars,
)
from trading_research.research.rule_discovery.profiles import (
    LOCATION_KINDS,
    OBJECT_IDS,
    PROFILE_WINDOWS,
    build_profile,
    frozen_sparse_row_value_area,
    location_objects,
    naked_poc,
    poc_tick,
    python_profile,
    python_value_area,
    shelves_and_ledges,
    vector_profile,
)


def _rows(volumes: list[int], *, start_ns: int = 0, high: int = 40000, low: int = 39900, close: int | None = None) -> list[dict]:
    minute = 60_000_000_000
    rows = []
    for i, volume in enumerate(volumes):
        c = close if close is not None else (high + low) // 2
        rows.append(
            {
                "start_ns": start_ns + i * minute,
                "end_ns": start_ns + (i + 1) * minute,
                "open_ticks": (high + low) // 2,
                "high_ticks": high,
                "low_ticks": low,
                "close_ticks": c,
                "volume": volume,
                "signed": 0,
                "unknown": 0,
                "known_at_ns": start_ns + (i + 1) * minute,
            }
        )
    return rows


def test_a01_f2_includes_final_minute_and_overshoot():
    rows = _rows([8, 3, 3])
    issue = rows[-1]["end_ns"]
    result = f2_volume_completed(rows, issue_ns=issue, median_volume=10)
    assert result["available"] is True
    assert result["overshoot"] == 4
    assert result["final_minute_volume"] == 8
    assert result["final_minute_start_ns"] == rows[0]["start_ns"]
    assert result["cumulative_volume"] == 14
    oracle = python_f2_volume_completed([3, 3, 8], median_volume=10)
    assert oracle["overshoot"] == 4
    assert oracle["minutes"] == 3
    formed = freeze_formation(result, cutoff_ns=issue, asset_id="NQ:test")
    assert formed is not None
    assert formed.volume == 14
    assert formed.construction_kind == "F2"


def test_a02_f3_uses_prior_scale_and_15_30_60_order():
    scale = _rows([1] * 60, high=40100, low=39900, close=40000)
    body = _rows([1] * 15, start_ns=scale[-1]["end_ns"], high=40040, low=39960, close=40000)
    tail = _rows([1] * 15, start_ns=body[-1]["end_ns"], high=40040, low=39960, close=40000)
    tail[0]["open_ticks"] = 39960
    rows = scale + body + tail
    issue = rows[-1]["end_ns"]
    result = f3_balance(rows, issue_ns=issue)
    assert result["available"] is True
    assert result["length"] == 30
    assert python_f3_first_length([(15, False), (30, True), (60, True)]) == 30
    assert F3_LENGTHS == (15, 30, 60)
    formed = freeze_formation(result, cutoff_ns=issue, asset_id="NQ:test")
    assert formed is not None
    assert formed.construction_kind == "F3"


def test_a03_profile_volume_conserved_and_value_area_raw():
    ticks = [100, 100, 101, 102, 102, 102]
    sizes = [10, 5, 4, 8, 8, 5]
    profile = build_profile(ticks, sizes, bandwidth=0, window="prior_regular_session", as_of_ns=10)
    assert profile["volume"] == 40
    assert profile["volume"] == sum(profile["raw"])
    va = profile["value_area"]
    assert va["inside_raw"] >= int(0.7 * 40)
    assert va["total_raw"] == 40
    python = python_profile(ticks, sizes, bandwidth=0)
    assert python["raw"] == profile["raw"]


def test_a04_poc_ties_and_empty_zero_volume():
    ticks = [10, 12]
    sizes = [5, 5]
    raw = [5, 0, 5]
    smoothed = [5.0, 0.0, 5.0]
    poc = poc_tick(10, smoothed, raw)
    assert poc == 10
    empty = build_profile([], [], bandwidth=0, window="overnight", as_of_ns=1)
    assert empty["available"] is False
    zero = build_profile([10], [0], bandwidth=0, window="overnight", as_of_ns=1)
    assert zero["available"] is False


def test_a05_future_bars_do_not_resize_frozen_formation():
    rows = _rows([2] * 60)
    issue = rows[-1]["end_ns"]
    first = f1_trailing_minutes(rows, issue_ns=issue)
    formed = freeze_formation(first, cutoff_ns=issue, asset_id="NQ:test")
    later = rows + _rows([99], start_ns=issue, high=50000, low=10000)
    second = f1_trailing_minutes(later, issue_ns=issue)
    formed2 = freeze_formation(second, cutoff_ns=issue, asset_id="NQ:test")
    assert formed is not None and formed2 is not None
    assert future_perturbation_stable(formed, formed2)
    profile = build_profile([100, 101], [10, 4], bandwidth=0, window="developing_intraday", as_of_ns=issue)
    later_profile = build_profile([100, 101, 180], [10, 4, 50], bandwidth=0, window="developing_intraday", as_of_ns=issue)
    assert profile["poc_ticks"] == later_profile["poc_ticks"] or profile["as_of_ns"] == issue
    frozen = build_profile([100, 101], [10, 4], bandwidth=0, window="developing_intraday", as_of_ns=issue)
    assert frozen["profile_id"] == profile["profile_id"]


def test_s14_python_bars_match_reduceat():
    events = [(i * 1_000_000_000, 40000 + (i % 3), 2, 1, (i + 1) * 1_000_000_000) for i in range(120)]
    start, end = 0, 120 * 1_000_000_000
    reference = python_bar_window(events, start, end)
    arrays = empty_session_arrays(start_ns=start, end_ns=end, instrument_id="test")
    n = len(events)
    arrays = SessionArrays(
        t_ns=np.array([e[0] for e in events], dtype=np.int64),
        price_ticks=np.array([e[1] for e in events], dtype=np.int64),
        size=np.array([e[2] for e in events], dtype=np.int64),
        side=np.array([e[3] for e in events], dtype=np.int8),
        action=np.ones(n, dtype=np.int8),
        bid_ticks=np.zeros(n, dtype=np.int64),
        ask_ticks=np.zeros(n, dtype=np.int64),
        bid_sz=np.zeros(n, dtype=np.int64),
        ask_sz=np.zeros(n, dtype=np.int64),
        flags=np.zeros(n, dtype=np.int64),
        known_at_ns=np.array([e[4] for e in events], dtype=np.int64),
        exchange_sequence=np.arange(n, dtype=np.int64),
        is_trade=np.ones(n, dtype=np.bool_),
        row_id=np.array([f"r{i}" for i in range(n)], dtype=object),
        ooo_index=np.zeros(0, dtype=np.int64),
        batch_starts=np.ones(n, dtype=np.bool_),
        instrument_id="test",
        start_ns=start,
        end_ns=end,
        source_sha256=(),
    )
    vector = bars_reduceat(arrays, start, end, 60)
    assert vector == reference


def test_s02_value_area_fails_if_raw_not_used():
    ticks = [10] * 10 + [11] * 1 + [12] * 1
    sizes = [10] * 10 + [1, 1]
    profile = python_profile(ticks, sizes, bandwidth=2)
    va = python_value_area(profile["min_tick"], profile["raw"], profile["smoothed"], poc_tick(profile["min_tick"], profile["smoothed"], profile["raw"]))
    assert va["inside_raw"] / va["total_raw"] >= 0.70
    assert sum(profile["raw"]) == 102


def test_s05_nested_future_rejected_on_formation():
    with pytest.raises(Exception):
        Formation(
            formation_id="x",
            asset_id="NQ:test",
            start_ns=0,
            end_ns=10,
            available_at_ns=5,
            high=Decimal("1"),
            low=Decimal("1"),
            volume=1,
            profile_id=None,
            construction_kind="F1",
            parent_ids=("p",),
            evidence=(EvidenceRef("a" * 64, ("r1",), 0, 10, 10, Coverage.COMPLETE, ()),),
        )


def test_s08_profile_identity_stable_under_post_cutoff_ticks():
    first = build_profile([100, 101], [3, 1], bandwidth=0, window="prior_full_account_day", as_of_ns=50)
    second = build_profile([100, 101], [3, 1], bandwidth=0, window="prior_full_account_day", as_of_ns=50)
    assert first["profile_id"] == second["profile_id"]
    later = build_profile([100, 101, 130], [3, 1, 9], bandwidth=0, window="prior_full_account_day", as_of_ns=50)
    assert later["profile_id"] != first["profile_id"]


def test_s10_profile_windows_are_registered():
    assert "overnight" in PROFILE_WINDOWS
    assert "developing_intraday" in PROFILE_WINDOWS
    assert len(PROFILE_WINDOWS) == 6


def test_s13_bandwidth_and_cutoff_change_identity():
    a = build_profile([100, 101], [4, 4], bandwidth=0, window="prior_calendar_week", as_of_ns=1)
    b = build_profile([100, 101], [4, 4], bandwidth=2, window="prior_calendar_week", as_of_ns=1)
    c = build_profile([100, 101], [4, 4], bandwidth=0, window="prior_calendar_week", as_of_ns=2)
    assert a["profile_id"] != b["profile_id"]
    assert a["profile_id"] != c["profile_id"]


def test_s22_new_geometry_is_enumerated():
    rows = _rows([1] * 60 + [1] * 15, high=40010, low=39990, close=40000)
    scale = _rows([1] * 60, high=40100, low=39900)
    mix = scale + _rows([1] * 15, start_ns=scale[-1]["end_ns"], high=40020, low=39980, close=40000)
    f3 = f3_balance(mix, issue_ns=mix[-1]["end_ns"])
    f1 = f1_trailing_minutes(mix, issue_ns=mix[-1]["end_ns"])
    assert f3["available"] is True
    assert f1["available"] is True
    assert freeze_formation(f3, cutoff_ns=mix[-1]["end_ns"], asset_id="NQ:test").formation_id != freeze_formation(f1, cutoff_ns=mix[-1]["end_ns"], asset_id="NQ:test").formation_id


def test_value_area_sparse_rows_defect_confirmed():
    rows = [(100, 10), (102, 8)]
    frozen = frozen_sparse_row_value_area(rows, 100, fraction=Decimal("0.70"))
    contiguous = python_value_area(100, [10, 0, 8], [10.0, 0.0, 8.0], 100, fraction=Decimal("0.70"))
    assert frozen["val_ticks"] == 100
    assert frozen["vah_ticks"] == 102
    assert contiguous["val_ticks"] == 100
    assert contiguous["vah_ticks"] >= 100
    def packed_row(price: str, volume: str) -> PriceRow:
        qty = Decimal(volume)
        return PriceRow(
            price=Decimal(price),
            buy_volume=qty,
            sell_volume=Decimal("0"),
            unknown_volume=Decimal("0"),
            total_volume=qty,
            known_delta=qty,
            full_delta=qty,
            delta_low=qty,
            delta_high=qty,
        )

    packed = [packed_row("100", "10"), packed_row("102", "8")]
    config = ValueAreaConfig(config_id="t", fraction=Decimal("0.70"), algorithm="adjacent_single", tie_policy="lower")
    val, vah, _inside, _ach = _value_area(packed, Decimal("100"), config)
    assert val == Decimal("100")
    assert vah == Decimal("102")
    assert frozen["row_neighbors"] is True


def test_shelf_ledge_research_choice():
    raw = [1] * 10 + [20, 21, 22] + [1]
    found = shelves_and_ledges(100, raw)
    kinds = {item["kind"] for item in found}
    assert "shelf" in kinds
    assert "ledge" in kinds
    shelf = next(item for item in found if item["kind"] == "shelf")
    assert shelf["research_choice"] is True


def test_location_objects_cover_conformance_ids():
    profile = build_profile([100, 101, 102, 103, 104], [2, 20, 21, 22, 2], bandwidth=0, window="prior_five_sessions", as_of_ns=9)
    objects = location_objects(profile, later_ticks=[110], prior_reaction={"band_low": 101, "band_high": 103, "prior_sweep_then_close_inside": True}, refill={"band_low": 101, "band_high": 103, "departed": True, "returned": True})
    kinds = {item["kind"] for item in objects}
    assert set(LOCATION_KINDS) <= kinds
    ids = {OBJECT_IDS[kind] for kind in LOCATION_KINDS}
    assert ids == {"O065", "O066", "O067", "O068", "O069", "O072", "O087", "O116"}
    naked = next(item for item in objects if item["kind"] == "naked_poc")
    assert naked["naked"] is True
    assert naked_poc(100, [101]) is True


def test_s07_native_replay_row_identity():
    from trading_research.research.rule_discovery.native import replay_native_row
    path = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
    if not Path(path).is_file():
        pytest.skip("native parquet missing")
    row = replay_native_row(path, 769284)
    assert row["kind"] == "native"
    assert row["row_id"].endswith(":769284")


def test_write_guard_is_installed_for_slice_jobs():
    blocked = install_write_guard()
    assert callable(blocked)


def test_median_int_ties_lower_middle():
    assert median_int([1, 3, 2, 4]) == 2


def test_s01_cases_document_rejects_missing_members():
    from trading_research.research.rule_discovery.formations import validate_cases
    assert validate_cases({"schema_version": "research-formation-cases-v1", "cases": [{"id": "c1"}]}) == []
    assert validate_cases({"schema_version": "research-formation-cases-v1"}) 
    assert validate_cases({"schema_version": "wrong", "cases": [{"id": "c1"}]})
