"""P15-13 Saint auction alignment."""
from __future__ import annotations

from pathlib import Path

from trading_research.research.rule_discovery.native import replay_native_row
from trading_research.research.rule_discovery.source_adapters.saint import (
    apply_operational_stages,
    evaluate_arrival_read,
    evaluate_ltf_alignment,
    evaluate_profile_permission,
    family_document,
    later_htf_cannot_explain_earlier_retest,
    ltf_without_htf_does_not_qualify,
)


def test_a01_later_htf_cannot_explain_earlier_retest():
    assert later_htf_cannot_explain_earlier_retest(10, 20) is True
    assert later_htf_cannot_explain_earlier_retest(30, 20) is False


def test_a02_ltf_without_htf_does_not_qualify():
    assert ltf_without_htf_does_not_qualify(False, True) is False
    assert ltf_without_htf_does_not_qualify(True, True) is True


def test_a03_profile_raw_volume_permission():
    assert evaluate_profile_permission(poc=5, low=0, high=10) is True
    assert evaluate_profile_permission(poc=15, low=0, high=10) is False
    assert evaluate_profile_permission(poc=None, low=0, high=10) is None


def test_a04_operational_stages_leave_unknown():
    values = apply_operational_stages(
        {
            "side": "long",
            "trigger": {"C": 12, "observed_complete": True, "known_at": 5, "start": 1, "end": 5},
            "decision_at": 20,
            "values": {"confirm_at": 20},
            "geometry": {
                "htf_profile": {"poc": 5},
                "htf_balance": {"low": 0, "high": 10},
                "ltf_balance": {"low": 0, "high": 10},
            },
            "reference": {"low": 0, "high": 10},
        }
    )
    assert values["arrival_read_recorded"] is True
    assert values["alignment_ok"] is True
    assert values["profile_allows_trade"] is True
    assert values["operational_rule_label"] == "operational"
    assert evaluate_arrival_read(trigger_complete=True, trigger_before_confirm=True) is True
    assert evaluate_ltf_alignment(side="short", ltf_break_up=True) is False
    doc = family_document()
    assert doc["label"] == "operational"


def test_operational_stages_read_market_not_literals():
    import inspect

    src = inspect.getsource(apply_operational_stages)
    compact = src.replace(" ", "")
    assert "trigger_complete=True" not in compact
    assert "ltf_break_up=Trueifside" not in compact
    long_but_break_down = apply_operational_stages(
        {
            "side": "long",
            "trigger": {"C": 10, "observed_complete": True, "known_at": 5, "end": 5},
            "decision_at": 20,
            "values": {"confirm_at": 20},
            "geometry": {"htf_profile": {"poc": 50}, "ltf_balance": {"low": 40, "high": 60}},
            "reference": {"low": 0, "high": 100},
        }
    )
    assert long_but_break_down["alignment_ok"] is False
    assert long_but_break_down["arrival_read_recorded"] is True
    assert long_but_break_down["profile_allows_trade"] is True
    refused = apply_operational_stages(
        {
            "side": "long",
            "trigger": {"C": 12, "observed_complete": True, "known_at": 5, "end": 5},
            "decision_at": 20,
            "geometry": {"htf_profile": {"poc": 999}, "ltf_balance": {"low": 0, "high": 10}},
            "reference": {"low": 0, "high": 10},
        }
    )
    assert refused["profile_allows_trade"] is False
    incomplete = apply_operational_stages(
        {
            "side": "short",
            "trigger": {"C": -1, "observed_complete": False, "known_at": 50, "end": 50},
            "decision_at": 20,
            "values": {"confirm_at": 20},
            "geometry": {"htf_profile": {"poc": 5}, "ltf_balance": {"low": 0, "high": 10}},
            "reference": {"low": 0, "high": 10},
        }
    )
    assert incomplete["arrival_read_recorded"] is False


def test_missing_confirm_at_is_unknown():
    from trading_research.research.rule_discovery.source_adapters.saint import reassess_episode

    values = apply_operational_stages(
        {
            "side": "long",
            "method": "SAINT-AMT",
            "branch": "continuation_retest",
            "trigger": {"C": 12, "observed_complete": True, "known_at": 5, "start": 1, "end": 5},
            "decision_at": 20,
            "values": {},
            "geometry": {
                "htf_profile": {"poc": 5},
                "htf_balance": {"low": 0, "high": 10},
                "ltf_balance": {"low": 0, "high": 10},
            },
            "reference": {"low": 0, "high": 10},
        }
    )
    assert values["arrival_read_recorded"] is None
    episode = reassess_episode(
        {
            "method": "SAINT-AMT",
            "branch": "continuation_retest",
            "side": "long",
            "values": values,
            "strategy_assessment": {"status": "no_setup"},
        }
    )
    assert episode["research_verdict"] == "unknown"
    assert episode["strategy_assessment"]["status"] == "data_unavailable"


def test_b0_matches_frozen_scan_branch():
    from trading_research.research.rule_discovery.source_adapters.common import FROZEN_PARITY_DATES, replay_b0_against_frozen
    from trading_research.research.rule_discovery.source_adapters import saint as _saint  # noqa: F401

    for day in FROZEN_PARITY_DATES:
        row = replay_b0_against_frozen(day, "SAINT-AMT", "poc_traversal")
        assert row["b0_transform_markers"] == []
        assert row["match"] is True, row


def test_bind_operational_in_scan_path():
    import inspect
    from trading_research.research.rule_discovery.source_adapters.saint import bind_saint_operational

    src = inspect.getsource(bind_saint_operational)
    assert "apply_operational_stages" in src
    bound = bind_saint_operational(
        {
            "episodes": [
                {
                    "method": "SAINT-AMT",
                    "branch": "continuation_retest",
                    "side": "long",
                    "trigger": {"C": 12, "observed_complete": True, "known_at": 5, "end": 5},
                    "decision_at": 20,
                    "values": {"confirm_at": 20},
                    "geometry": {
                        "htf_profile": {"poc": 5},
                        "ltf_balance": {"low": 0, "high": 10},
                    },
                    "reference": {"low": 0, "high": 10},
                    "strategy_assessment": {"status": "data_unavailable"},
                }
            ]
        },
        None,
        "continuation_retest",
        "B0.1",
    )
    assert bound["episodes"][0]["values"]["arrival_read_recorded"] is True
    assert bound["saint_operational_bound"] is True


def test_s07_native_replay():
    path = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
    if Path(path).is_file():
        assert replay_native_row(path, 769284)["kind"] == "native"
