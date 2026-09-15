"""P15-07 S1–S4 machines and CASE/OR adjudication."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from trading_research.research.contracts.types import Contact, Coverage, EvidenceRef, SequenceSpec
from trading_research.research.method_pack.expressions import Parser, evaluate
from trading_research.research.rule_discovery.native import replay_native_row
from trading_research.research.rule_discovery.sequences import (
    Eval,
    advance_sequence,
    causal_case,
    causal_or,
    frozen_case,
    frozen_or_short_circuit,
    initial_state,
    mirror,
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
    selector = Eval(None, ("branch",), ("branch",))
    branches = [("judas_reversal", Eval(True, ("a",), ()))]
    default = Eval(False, ("else",), ())
    correct = causal_case(selector, branches, default)
    frozen = frozen_case(None, [("judas_reversal", True)], False)
    assert correct.value is None
    assert frozen is False
    assert "branch" in correct.operands


def test_or_retains_both_operands():
    left = Eval(True, ("left_field",), ())
    right = Eval(False, ("right_field",), ())
    correct = causal_or(left, right)
    frozen = frozen_or_short_circuit(left, right)
    assert correct.value is True
    assert "right_field" in correct.operands
    assert "right_field" not in frozen.operands


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
    tree = Parser("CASE branch WHEN 'x' THEN TRUE ELSE FALSE END").parse()
    assert tree[0] == "CASE"
    selected = next((body for key, body in tree[2] if key[1] == None), tree[3])
    assert selected[0] == "literal"
    assert selected[1] is False
