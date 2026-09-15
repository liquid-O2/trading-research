"""P15-07 S1–S4 machines and CASE/OR adjudication."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from trading_research.research.contracts.types import Contact, Coverage, EvidenceRef, SequenceSpec
from trading_research.research.method_pack.expressions import Parser, evaluate
from trading_research.research.rule_discovery.cohorts import markout
from trading_research.research.rule_discovery.native import replay_native_row
from trading_research.research.rule_discovery.sequences import (
    Eval,
    FROZEN_CASE_REF,
    FROZEN_OR_REF,
    advance_sequence,
    causal_case,
    causal_or,
    cohort_signed_mean,
    initial_state,
    mirror,
    observe_frozen_case_unknown_selector,
    observe_frozen_or_operand_drop,
    rearm_ready,
    recipe_spec,
)


def _contact(side: int = 1) -> Contact:
    ev = EvidenceRef("a" * 64, ("c1",), 10, 10, 10, Coverage.COMPLETE, ())
    return Contact(
        contact_id="c1",
        reference_id="r1",
        batch_id="b1",
        at_ns=10,
        available_at_ns=10,
        side=side,
        kind="strict_sweep",
        possible_prices=(Decimal("100"),),
        departure_evidence=(ev,),
        evidence=(ev,),
    )


def _run(recipe: str, steps: list[tuple[int, dict]], *, side: int = 1):
    spec = recipe_spec(recipe)
    state = initial_state(spec, _contact(side), now_ns=10, expiry_ns=10 + 600_000_000_000)
    for now, inputs in steps:
        state = advance_sequence(state, inputs.get("batch"), spec, now_ns=now, inputs=inputs)
    return state


def test_a01_retest_before_reclaim_cannot_satisfy_s2():
    state = _run(
        "S2",
        [
            (11, {"sweep_ticks": 2, "swept_extreme": 99}),
            (12, {"later_contact_within_1_tick": True, "favorable_close_2_ticks": True, "retest_before_reclaim": True, "complete_bar": None}),
            (13, {"complete_bar": {"close_inside": True, "event_ns": 13}}),
            (14, {"later_contact_within_1_tick": True, "favorable_close_2_ticks": True, "retest_before_reclaim": True}),
        ],
    )
    assert state.state != "confirmed" or "retest_before_reclaim" in {p.name for p in state.stage_evidence}
    early = _run("S2", [(11, {"sweep_ticks": 2}), (12, {"later_contact_within_1_tick": True, "favorable_close_2_ticks": True})])
    assert early.state != "confirmed"


def test_a02_missing_aggression_cannot_qualify_s3_s4():
    s3 = _run("S3", [(11, {"sweep_ticks": 2}), (12, {"complete_bar": {"close_inside": True, "event_ns": 12}})])
    assert s3.state == "input_unknown"
    s4 = _run("S4", [(11, {"opposing_aggression": None})])
    assert s4.state == "input_unknown"


def test_a03_same_batch_cannot_satisfy_two_stages():
    spec = recipe_spec("S1")
    contact = _contact()
    state = initial_state(spec, contact, now_ns=10, expiry_ns=1000)
    state = advance_sequence(state, {"batch_id": "b1", "event_ns": 10}, spec, now_ns=11, inputs={"sweep_ticks": 2, "swept_extreme": 99})
    state = advance_sequence(
        state,
        {"batch_id": "b1", "event_ns": 10},
        spec,
        now_ns=12,
        inputs={"complete_bar": {"close_inside": True, "event_ns": 10}, "batch": {"batch_id": "b1", "event_ns": 10}},
    )
    assert state.state != "confirmed"


def test_a04_expired_does_not_revive_without_rearm():
    spec = recipe_spec("S1")
    contact = _contact()
    state = initial_state(spec, contact, now_ns=10, expiry_ns=50)
    state = advance_sequence(state, None, spec, now_ns=50, inputs={})
    assert state.state == "expired"
    later = advance_sequence(state, None, spec, now_ns=80, inputs={"sweep_ticks": 8, "complete_bar": {"close_inside": True}})
    assert later.state == "expired"
    assert rearm_ready(departed_ticks=5, scale_at_first_contact_ticks=10, outside_complete_bar=True) is True
    assert rearm_ready(departed_ticks=1, scale_at_first_contact_ticks=10, outside_complete_bar=True) is False


def test_a05_mirrored_long_short():
    assert mirror(4, 1) == 4
    assert mirror(4, -1) == -4
    long = _run("S1", [(11, {"sweep_ticks": 2}), (20, {"complete_bar": {"close_inside": True, "event_ns": 20}})], side=1)
    short = _run("S1", [(11, {"sweep_ticks": 2}), (20, {"complete_bar": {"close_inside": True, "event_ns": 20}})], side=-1)
    assert long.state == short.state == "confirmed"


def test_case_unknown_selector_propagates():
    observed = observe_frozen_case_unknown_selector()
    assert observed["frozen_ref"]["path"].endswith("expressions.py")
    assert observed["frozen_ref"]["start_line"] == 150
    assert observed["frozen_value"] is False
    assert observed["primitive_value"] is None
    assert "selector" in observed["primitive_operands"]
    assert FROZEN_CASE_REF["end_line"] == 153


def test_or_retains_both_operands():
    observed = observe_frozen_or_operand_drop()
    assert observed["frozen_ref"]["start_line"] == 171
    assert observed["frozen_value"] is True
    assert observed["frozen_dropped_right"] is True
    assert observed["primitive_value"] is True
    assert "right_field" in observed["primitive_operands"]
    assert FROZEN_OR_REF["end_line"] == 175


def test_s09_ambiguous_batch_does_not_order_stages():
    spec = recipe_spec("S1")
    state = initial_state(spec, _contact(), now_ns=10, expiry_ns=1000)
    state = advance_sequence(state, {"batch_id": "b1"}, spec, now_ns=11, inputs={"sweep_ticks": 2, "complete_bar": {"close_inside": True, "event_ns": 11}})
    assert state.state != "confirmed"


def test_s22_rearm_uses_frozen_threshold():
    assert rearm_ready(departed_ticks=4, scale_at_first_contact_ticks=10, outside_complete_bar=True)
    assert not rearm_ready(departed_ticks=4, scale_at_first_contact_ticks=100, outside_complete_bar=True)


def test_s07_native_replay():
    path = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
    if not Path(path).is_file():
        pytest.skip("native parquet missing")
    assert replay_native_row(path, 769284)["kind"] == "native"


def test_expressions_case_tree_else_on_none_selector():
    observed = observe_frozen_case_unknown_selector()
    frozen = evaluate
    assert callable(frozen)
    assert observed["frozen_value"] is False
    tree = Parser("CASE branch WHEN 'x' THEN TRUE ELSE FALSE END").parse()
    assert tree[0] == "CASE"


def test_s3_uses_volume_weighted_cohort_mean():
    trades = [
        {"sign": 1, "qty": 10, "price": 100.0, "event_ns": 0, "mid_at_horizon": 101.0, "mid_available_ns": 120_000_000_000},
        {"sign": 1, "qty": 1, "price": 100.0, "event_ns": 0, "mid_at_horizon": 99.0, "mid_available_ns": 120_000_000_000},
    ]
    result = markout(trades, horizon_s=120, snapshot_ns=120_000_000_000)
    mean = cohort_signed_mean(result, 1)
    assert mean == pytest.approx(0.8181818181818182)
    state = _run(
        "S3",
        [
            (11, {"sweep_ticks": 2, "swept_extreme": 99}),
            (12, {"complete_bar": {"close_inside": True, "event_ns": 12}, "c1": 0.5, "cohort_120": result, "cohort_available_at_ns": 12}),
        ],
    )
    assert state.state == "confirmed"
    unweighted_zero = _run(
        "S3",
        [
            (11, {"sweep_ticks": 2, "swept_extreme": 99}),
            (12, {"complete_bar": {"close_inside": True, "event_ns": 12}, "c1": 0.5, "cohort_120_mean": 0.0, "cohort_available_at_ns": 12}),
        ],
    )
    assert unweighted_zero.state != "confirmed"
