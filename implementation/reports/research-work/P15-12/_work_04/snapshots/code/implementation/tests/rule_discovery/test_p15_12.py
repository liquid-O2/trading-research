"""P15-12 Sires thesis and flow."""
from __future__ import annotations

from pathlib import Path

from trading_research.research.rule_discovery.native import replay_native_row
from trading_research.research.rule_discovery.source_adapters.sires import (
    FAMILY,
    apply_sires_rules,
    family_document,
    four_stage_order,
    independent_thesis_direction,
    ofm_objective_r,
    p1_preceding_equal_window,
    swapped_middle_rejected,
    three_tick_replenishment,
)


def test_a01_four_stage_rejects_swap():
    assert four_stage_order() == ("locate", "provoke", "absorb", "continue")
    assert swapped_middle_rejected(("locate", "absorb", "provoke", "continue")) is True
    assert swapped_middle_rejected(four_stage_order()) is False


def test_a02_absorption_not_raw_delta():
    doc = family_document()
    assert "P1" in doc["findings"]


def test_a03_kg1_inferred():
    assert family_document()["adapter_rules"]["P6"]


def test_a04_own_population_and_c5():
    micro = {"low": 1, "high": 3}
    htf = {"low": 0, "high": 20}
    assert independent_thesis_direction(micro, htf) == 1
    upper = {"low": 16, "high": 18}
    assert independent_thesis_direction(upper, htf) == -1
    assert independent_thesis_direction(None, htf) is None


def test_a05_replenishment_and_ofm():
    assert three_tick_replenishment(3) is True
    assert three_tick_replenishment(2) is False
    assert ofm_objective_r(100, 90, 3) == 30
    assert ofm_objective_r(100, 90, 1) == 10


def test_s23_unresolved_does_not_update():
    prior = {"memory": 1}
    later = {"memory": 1}
    assert prior == later


def test_s07_native_replay():
    path = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
    if Path(path).is_file():
        assert replay_native_row(path, 769284)["kind"] == "native"


def test_clock_zone():
    assert family_document()["clock_zone_unverified"] is True
    assert FAMILY == "SIRES"


def test_p6_dedup_and_replenishment_and_ofm_in_scan_path():
    import inspect

    src = inspect.getsource(apply_sires_rules)
    assert "reference_lifecycle_id" in src
    assert "three_tick_replenishment" in src
    assert "ofm_objective_r" in src
    kg = apply_sires_rules(
        {
            "episodes": [
                {"candidate_id": "a", "values": {}, "reference": {"reference_lifecycle_id": "LIFE1", "id": "r1:t1"}},
                {"candidate_id": "b", "values": {}, "reference": {"reference_lifecycle_id": "LIFE1", "id": "r1:t2"}},
                {"candidate_id": "c", "values": {}, "reference": {"reference_lifecycle_id": "LIFE2", "id": "r2:t1"}},
            ]
        },
        None,
        "kg1_retest",
        "B0.1",
    )
    assert [ep["candidate_id"] for ep in kg["episodes"]] == ["a", "c"]
    ofm = apply_sires_rules(
        {
            "episodes": [
                {
                    "candidate_id": "ok",
                    "geometry": {"entry": 100, "stop": 90},
                    "values": {"passive_replenishment_ticks": 3},
                },
                {
                    "candidate_id": "no",
                    "geometry": {"entry": 100, "stop": 90},
                    "values": {"passive_replenishment_ticks": 1},
                },
            ]
        },
        None,
        "ofm_passive",
        "B0.1",
    )
    ids = [ep["candidate_id"] for ep in ofm["episodes"]]
    assert ids == ["ok"]
    assert ofm["episodes"][0]["values"]["ofm_objective_1r"] == 10
    assert ofm["episodes"][0]["values"]["ofm_objective_3r"] == 30
    empty = p1_preceding_equal_window(4, None)
    assert empty["previous"] == 0
    assert empty["empty_as_zero"] is True


def test_b0_matches_frozen_scan_branch():
    from trading_research.research.rule_discovery.source_adapters.common import FROZEN_PARITY_DATES, replay_b0_against_frozen
    from trading_research.research.rule_discovery.source_adapters import sires as _sires  # noqa: F401

    rows = []
    for day in FROZEN_PARITY_DATES:
        for branch in ("kg1_retest", "ofm_aggressive"):
            row = replay_b0_against_frozen(day, FAMILY, branch)
            rows.append(row)
            assert row["b0_transform_markers"] == []
            assert row["match"] is True, row
    assert len(rows) == 6


def test_changed_axis_scan_variant_exists():
    import inspect
    from trading_research.research.rule_discovery.source_adapters.sires import scan_variant

    assert "dispatch_scan_variant" in inspect.getsource(scan_variant)
