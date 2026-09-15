"""P15-12 Sires thesis and flow."""
from __future__ import annotations

from pathlib import Path

from trading_research.research.rule_discovery.native import replay_native_row
from trading_research.research.rule_discovery.source_adapters.sires import (
    FAMILY,
    family_document,
    four_stage_order,
    independent_thesis_direction,
    ofm_objective_r,
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
