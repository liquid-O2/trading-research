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
    values = apply_operational_stages({"side": "long", "geometry": {"htf_profile": {"poc": 5}, "htf_balance": {"low": 0, "high": 10}}})
    assert values["arrival_read_recorded"] is True
    assert values["alignment_ok"] is True
    assert values["profile_allows_trade"] is True
    assert values["operational_rule_label"] == "operational"
    assert evaluate_arrival_read(trigger_complete=True, trigger_before_confirm=True) is True
    assert evaluate_ltf_alignment(side="short", ltf_break_up=True) is False
    doc = family_document()
    assert doc["label"] == "operational"


def test_s07_native_replay():
    path = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
    if Path(path).is_file():
        assert replay_native_row(path, 769284)["kind"] == "native"
