"""P15-14 Member independent reasons."""
from __future__ import annotations

from pathlib import Path

from trading_research.research.rule_discovery.native import replay_native_row
from trading_research.research.rule_discovery.source_adapters.member import (
    apply_member_rules,
    family_document,
    hvn_from_reaction_period_fails,
    rearm_requires_departure,
    two_records_same_parent_are_not_two_reasons,
    vacuous_all,
)


def test_a01_hvn_from_reaction_period_fails():
    assert hvn_from_reaction_period_fails((0, 10), (0, 10)) is True
    assert hvn_from_reaction_period_fails((0, 10), (10, 20)) is False


def test_a02_same_parent_not_two_reasons():
    assert two_records_same_parent_are_not_two_reasons(("p", "p")) is False
    assert two_records_same_parent_are_not_two_reasons(("p", "q")) is True


def test_a03_rearm_needs_departure():
    assert rearm_requires_departure(departed=True, outside_complete_bar=True) is True
    assert rearm_requires_departure(departed=False, outside_complete_bar=True) is False


def test_vacuous_all_is_unknown():
    assert vacuous_all([], lambda row: True) is None
    assert vacuous_all([1, 2], lambda row: row > 0) is True
    assert vacuous_all([1, 0], lambda row: row > 0) is False
    assert family_document()["clock_zone_unverified"] is True


def test_member_findings_applied_in_scan():
    import inspect

    src = inspect.getsource(apply_member_rules)
    assert "hvn_from_reaction_period_fails" in src
    assert "vacuous_all" in src
    assert "two_records_same_parent_are_not_two_reasons" in src
    out = apply_member_rules(
        {
            "episodes": [
                {
                    "candidate_id": "a",
                    "values": {"reaction_window": (0, 10), "hvn_window": (0, 10), "window_rows": []},
                    "parent_ids": ["p", "p"],
                }
            ]
        },
        None,
        "planned_return_long",
        "B0.1",
    )
    values = out["episodes"][0]["values"]
    assert values["hvn_from_reaction_period_fails"] is True
    assert values["vacuous_all"] is None
    assert values["two_independent_reasons"] is False
    assert values["member_adapter_rules"] is True


def test_s07_native_replay():
    path = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
    if Path(path).is_file():
        assert replay_native_row(path, 769284)["kind"] == "native"
