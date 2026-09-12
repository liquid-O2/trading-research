"""Focused O150/O166 identity and inner-clock correctness regressions."""

from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path

import pytest

from trading_research.research.method_pack import objects  # noqa: F401
from trading_research.research.method_pack.protocol import run_recipe


PROBES = (Path(__file__).parents[1] / "validation" /
          "phase1-post-implementation-check" / "original-check" /
          "lifecycle-probes.json")


def probe(name):
    document = json.loads(PROBES.read_text())
    return deepcopy(next(row["inputs"] for row in document["results"]
                         if row["probe"] == name))


def order(events, *, use_at=30, **overrides):
    result = {
        "candidate_id": "candidate-A", "order_id": "order-A",
        "position_id": "position-A", "instrument_id": "NQ",
        "source_id": "refill", "method_id": "REFILL-STUDY",
        "side": "long", "order_type": "limit", "limit": 100,
        "q": Decimal("0.25"), "quantity": 3, "placed_at": 10,
        "placement_known_at": 10, "use_at": use_at,
        "other_open_positions": 0,
        "source_policy": {
            "policy_id": "refill-v1", "source_id": "refill",
            "method_id": "REFILL-STUDY", "stop_ticks": 32,
            "target_ticks": 96, "one_position_at_a_time": True,
        },
        "events": deepcopy(events),
    }
    result.update(overrides)
    return result


def event(kind, at, **overrides):
    row = {
        "event_id": f"{kind}-{at}", "kind": kind, "at": at,
        "known_at": at, "order_id": "order-A",
        "position_id": "position-A", "candidate_id": "candidate-A",
        "instrument_id": "NQ",
    }
    row.update(overrides)
    return row


@pytest.mark.parametrize(
    "name,recipe_id,expected_state",
    [
        ("foreign_order_fill", "O150", "invalid"),
        ("future_fill_backdated", "O150", "invalid"),
        ("transition_missing_labels", "O166", "hole"),
        ("transition_backdated", "O166", "invalid"),
    ],
)
def test_exact_independent_invalid_inputs_no_longer_certify(name, recipe_id, expected_state):
    inputs = probe(name)
    result = run_recipe(recipe_id, inputs)

    assert result.state == expected_state
    assert result.base_ok is not True
    if recipe_id == "O150":
        assert result.value["lifecycle_valid"] is not True
        assert result.value["filled_quantity"] is None
        supplied_event = inputs["events"][0]
        retained_event = result.value["unapplied_events"][0]
        assert retained_event["at"] == supplied_event["at"]
        assert retained_event["known_at"] == supplied_event["known_at"]
    else:
        assert result.value["transition_valid"] is not True


@pytest.mark.parametrize(
    "name,recipe_id,validity_field",
    [("order_control", "O150", "lifecycle_valid"),
     ("transition_control", "O166", "transition_valid")],
)
def test_exact_independent_valid_controls_remain_valid(name, recipe_id, validity_field):
    result = run_recipe(recipe_id, probe(name))

    assert result.state == "computed"
    assert result.base_ok is True
    assert result.value[validity_field] is True


@pytest.mark.parametrize("kind", ["fill", "exit_fill", "cancel", "amend"])
@pytest.mark.parametrize(
    "identity,value",
    [("order_id", "order-B"), ("position_id", "position-B"),
     ("instrument_id", "ES"), ("candidate_id", "candidate-B")],
)
def test_witnessed_foreign_identity_is_rejected_before_each_mutation(kind, identity, value):
    prefix = [event("fill", 11, qty=1)] if kind == "exit_fill" else []
    changes = {"qty": 1} if kind in {"fill", "exit_fill"} else (
        {"new_quantity": 4} if kind == "amend" else {}
    )
    bad = event(kind, 15, **changes)
    bad[identity] = value

    result = run_recipe("O150", order([*prefix, bad]))

    assert result.state == "invalid"
    assert result.base_ok is False
    assert result.value["lifecycle_valid"] is False
    assert result.value["filled_quantity"] is None
    assert bad["event_id"] not in {row["event_id"] for row in result.value["order_state_timeline"]}


@pytest.mark.parametrize(
    "kind,required_link,changes",
    [
        ("fill", "order_id", {"qty": 1}),
        ("fill", "position_id", {"qty": 1}),
        ("fill", "instrument_id", {"qty": 1}),
        ("cancel", "order_id", {}),
        ("cancel", "instrument_id", {}),
        ("amend", "order_id", {"new_quantity": 4}),
        ("amend", "instrument_id", {"new_quantity": 4}),
        ("exit_fill", "position_id", {"qty": 1}),
        ("exit_fill", "instrument_id", {"qty": 1}),
    ],
)
def test_missing_required_relationship_is_a_hole_and_is_not_applied(kind, required_link, changes):
    prefix = [event("fill", 11, qty=1)] if kind == "exit_fill" else []
    incomplete = event(kind, 15, **changes)
    incomplete.pop(required_link)

    result = run_recipe("O150", order([*prefix, incomplete]))

    assert result.state == "hole"
    assert result.base_ok is None
    assert result.value["lifecycle_valid"] is None
    assert result.value["filled_quantity"] is None
    assert result.value["known_prefix_filled_quantity"] == (1 if prefix else 0)
    assert any(required_link in hole for hole in result.hole_ids)


@pytest.mark.parametrize(
    "kind,events,expected",
    [
        ("fill", [event("fill", 15, qty=1)], {"filled_quantity": 1, "position_quantity": 1}),
        ("cancel", [event("cancel", 15)], {"remaining_quantity": 0, "position_quantity": 0}),
        ("amend", [event("amend", 15, new_quantity=4)], {"remaining_quantity": 4}),
        ("exit_fill", [event("fill", 11, qty=1), event("exit_fill", 15, qty=1)],
         {"filled_quantity": 1, "position_quantity": 0}),
    ],
)
def test_fully_linked_event_controls_apply(kind, events, expected):
    result = run_recipe("O150", order(events))

    assert result.state == "computed", (kind, result.reason, result.hole_ids)
    assert result.value["lifecycle_valid"] is True
    for key, value in expected.items():
        assert result.value[key] == value


def test_valid_reopen_generation_and_postcancel_exit_remain_supported():
    events = [
        event("partial_fill", 11, qty=1),
        event("cancel", 12),
        event("reopen", 13, prior_order_id="order-A", new_order_id="order-B",
              new_quantity=2),
        event("partial_fill", 14, order_id="order-B", qty=1),
        event("cancel", 15, order_id="order-B"),
        event("exit_fill", 16, order_id="order-A", qty=2),
    ]

    result = run_recipe("O150", order(events))

    assert result.state == "computed", result.reason
    assert result.value["active_order_id"] == "order-B"
    assert result.value["filled_quantity"] == 2
    assert result.value["position_quantity"] == 0
    assert result.value["position_open"] is False


def test_delayed_fill_applies_only_when_its_claimed_availability_is_reached():
    delayed = event("fill", 15, known_at=18, qty=1)

    pending = run_recipe("O150", order([delayed], use_at=17))
    available = run_recipe("O150", order([delayed], use_at=18))

    assert pending.state == "computed"
    assert pending.value["filled_quantity"] == 0
    assert pending.value["pending_events"] == [delayed]
    assert pending.known_at == 10
    assert available.value["filled_quantity"] == 1
    assert available.known_at == 18


def test_unknown_fill_availability_stays_unknown_and_preserves_known_prefix():
    unknown = event("fill", 15, known_at=None, qty=1)

    result = run_recipe("O150", order([unknown]))

    assert result.state == "hole"
    assert result.known_at is None
    assert result.value["filled_quantity"] is None
    assert result.value["known_prefix_filled_quantity"] == 0
    assert result.value["unapplied_events"][0]["known_at"] is None


def test_future_fill_with_consistent_clock_is_pending_but_backdated_clock_rejects():
    future = run_recipe("O150", order([event("fill", 20, qty=1)], use_at=15))
    backdated = run_recipe("O150", order([event("fill", 20, known_at=12, qty=1)], use_at=15))

    assert future.state == "computed"
    assert future.value["filled_quantity"] == 0
    assert future.value["pending_events"][0]["at"] == 20
    assert backdated.state == "invalid"
    assert "availability precedes occurrence" in backdated.reason


def test_snapshot_after_use_is_rejected_without_rewriting_either_clock():
    inputs = order([event("fill", 20, qty=1)], use_at=15, as_of=30)

    result = run_recipe("O150", inputs)

    assert result.state == "invalid"
    assert "snapshot occurs after lifecycle use" in result.reason
    assert result.value["requested_as_of"] == 30
    assert result.value["use_at"] == 15


@pytest.mark.parametrize("carrier", ["events", "fill_qtys"])
@pytest.mark.parametrize("marker", ["synthetic_from_policy", "_o150_internal_policy_cancel"])
def test_caller_cannot_claim_internal_policy_status_to_bypass_event_links(carrier, marker):
    supplied = {"kind": "fill", "qty": 1, "at": 15, "known_at": 15,
                "order_id": "order-A", marker: True}
    inputs = order([])
    inputs[carrier] = [supplied]

    result = run_recipe("O150", inputs)

    assert result.state == "hole"
    assert result.base_ok is None
    assert result.value["filled_quantity"] is None
    assert result.value["known_prefix_filled_quantity"] == 0
    assert result.value["unapplied_events"][0].get("synthetic_from_policy") is None


def test_pending_reopen_does_not_activate_new_generation_or_admit_its_fill():
    events = [
        event("cancel", 12),
        event("reopen", 13, known_at=25, prior_order_id="order-A",
              new_order_id="order-B", new_quantity=2),
        event("fill", 15, order_id="order-B", qty=1),
    ]

    result = run_recipe("O150", order(events, use_at=20))

    assert result.state == "hole"
    assert result.value["active_order_id"] == "order-A"
    assert result.value["filled_quantity"] is None
    assert result.value["known_prefix_filled_quantity"] == 0
    assert [row["event_id"] for row in result.value["pending_events"]] == ["reopen-13"]
    assert [row["event_id"] for row in result.value["unapplied_events"]] == ["fill-15"]


def test_later_explicit_cancel_does_not_suppress_earlier_policy_deadline():
    events = [event("cancel", 25), event("fill", 22, qty=1)]

    result = run_recipe("O150", order(events, cancel_at=20))

    assert result.state == "invalid"
    assert "fill without valid working order" in result.reason
    assert next(row for row in result.value["order_state_timeline"] if row["at"] == 20)["kind"] == "cancel"


@pytest.mark.parametrize(
    "changes,reason",
    [
        ({"event_at": 16}, "occurrence aliases conflict"),
        ({"available_at": 15, "known_at": 16}, "availability aliases conflict"),
        ({"source_order_id": "order-B"}, "order identity aliases conflict"),
        ({"source_symbol": "ES"}, "instrument identity aliases conflict"),
    ],
)
def test_order_event_aliases_cannot_hide_contradictory_claims(changes, reason):
    row = event("fill", 15, qty=1, **changes)

    result = run_recipe("O150", order([row]))

    assert result.state == "invalid"
    assert reason in result.reason


def transition(from_state="D", to_state="A", *, current_known=10, next_known=20,
               as_of=None, use_at=None, conditioning=None):
    result = {
        "current_observation": {
            "state_label": from_state, "state_id": "current", "state_at": 10,
            "known_at": current_known, "sequence": 1, "instrument_id": "NQ",
            "cohort_id": "cohort", "reset_id": "session",
        },
        "next_observation": {
            "state_label": to_state, "state_id": "next", "state_at": 20,
            "known_at": next_known, "sequence": 2, "instrument_id": "NQ",
            "cohort_id": "cohort", "reset_id": "session",
        },
        "cadence": "adjacent-state-observations",
        "conditioning_evidence": conditioning or [{"evidence_id": "condition", "at": 8, "known_at": 9}],
    }
    if as_of is not None:
        result["as_of"] = as_of
    if use_at is not None:
        result["use_at"] = use_at
    return result


@pytest.mark.parametrize("from_state", list("BADEW"))
@pytest.mark.parametrize("to_state", list("BADEW"))
def test_every_valid_state_label_pair_can_form_an_observed_transition(from_state, to_state):
    result = run_recipe("O166", transition(from_state, to_state))

    assert result.state == "computed"
    assert result.value["transition_valid"] is True
    assert result.value["from_state"] == from_state
    assert result.value["to_state"] == to_state


@pytest.mark.parametrize("record,label_hole", [("current_observation", "current_state_label"),
                                                ("next_observation", "next_state_label")])
def test_each_missing_state_label_is_an_explicit_hole(record, label_hole):
    inputs = transition()
    inputs[record].pop("state_label")

    result = run_recipe("O166", inputs)

    assert result.state == "hole"
    assert result.value["transition_valid"] is None
    assert f"HOLE:O166:{label_hole}" in result.hole_ids


@pytest.mark.parametrize("bad_label", ["", "Z", 1, ["A"]])
def test_invalid_state_labels_are_rejected_without_inventing_a_classifier(bad_label):
    inputs = transition(to_state=bad_label)

    result = run_recipe("O166", inputs)

    assert result.state == "invalid"
    assert result.value["transition_valid"] is False
    assert result.value["to_state"] == (bad_label if isinstance(bad_label, str) else None)
    assert result.value["automatic_transition"] is None


def test_future_transition_is_pending_and_unknown_state_availability_stays_unknown():
    future = run_recipe("O166", transition(as_of=15, use_at=25))
    unknown = run_recipe("O166", transition(next_known=None))

    assert future.state == "hole"
    assert future.value["transition_valid"] is None
    assert future.value["pending_observations"] == ["next"]
    assert future.known_at == 10
    assert unknown.state == "hole"
    assert unknown.value["transition_valid"] is None
    assert unknown.known_at is None


@pytest.mark.parametrize(
    "inputs,reason",
    [
        (transition(current_known=5), "current state availability precedes occurrence"),
        (transition(next_known=6), "next state availability precedes occurrence"),
        (transition(conditioning=[{"evidence_id": "condition", "at": 8, "known_at": 7}]),
         "conditioning evidence 0 availability precedes occurrence"),
        (transition(as_of=30, use_at=25), "snapshot occurs after transition use"),
    ],
)
def test_transition_rejects_each_contradictory_inner_or_use_clock(inputs, reason):
    result = run_recipe("O166", inputs)

    assert result.state == "invalid"
    assert result.value["transition_valid"] is False
    assert reason in result.reason


@pytest.mark.parametrize(
    "record,changes,reason",
    [
        ("current_observation", {"at": 11}, "occurrence aliases conflict"),
        ("next_observation", {"available_at": 20, "known_at": 21},
         "availability aliases conflict"),
        ("current_observation", {"id": "foreign"}, "identity aliases conflict"),
        ("next_observation", {"source_symbol": "ES"}, "instrument identity aliases conflict"),
    ],
)
def test_transition_aliases_cannot_hide_contradictory_claims(record, changes, reason):
    inputs = transition()
    inputs[record].update(changes)

    result = run_recipe("O166", inputs)

    assert result.state == "invalid"
    assert result.value["transition_valid"] is False
    assert reason in result.reason
