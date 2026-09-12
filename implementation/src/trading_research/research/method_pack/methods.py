"""M01 fixture construction and strict dispatch to the completed method slices.

Public candidate scoring lives in evidence.score_episode.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from decimal import Decimal
from typing import Any

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.logic import (
    kleene_and, kleene_or, kleene_not, kleene_eq, kleene_cmp, kleene_case,
    kleene_between, implies, verdict,
)
from trading_research.research.method_pack.protocol import jsonable

DAY = date(2026, 1, 15)

M01_BRANCHES = (
    "judas_outbound",
    "judas_reversal",
    "single_extended",
    "single_purged",
    "internal_rotation",
    "extension_reaction",
    "other_session",
    "timed_pzone_reversal",
)

_M01_COMMON_FIELDS = (
    "range_frozen",
    "context_fixed",
    "location_touched",
    "source_confirmation",
    "risk_defined",
    "objective_fixed",
    "range_known_at",
    "context_at",
    "touch_at",
    "confirm_at",
    "decision_at",
)

_M01_BRANCH_FIELDS = {
    "judas_outbound": (
        "directional_context",
        "at_rth_open",
        "objective_is_selected_exhaustion",
        "exit_window_recorded",
    ),
    "judas_reversal": (
        "reversal_context",
        "edge_swept",
        "sweep_at",
        "source_time_window",
        "objective_is_opposing_draw",
    ),
    "single_extended": (
        "extended_context",
        "entry_at_eq_or_quadrant",
        "objective_is_range_edge",
        "reduced_expectations",
    ),
    "single_purged": (
        "purged_compressed_context",
        "purge_known_at",
        "entry_at_eq_or_quadrant",
        "expansion_policy",
    ),
    "internal_rotation": (
        "rotation_context",
        "entry_at_named_internal_or_ev_band",
        "objective_is_named_rotation_target",
    ),
    "extension_reaction": (
        "prior_expansion",
        "touch_in_source_extension_area",
        "reaction_side_confirmed",
        "objective_is_remaining_draw",
    ),
    "other_session": (
        "source_clock_verified",
        "source_case_verified",
    ),
    "timed_pzone_reversal": (
        "source_zone_known",
        "source_time_window",
        "zone_known_at",
        "directed_path_recorded",
    ),
}

_M01_EVENT_FIELDS = {
    "range_known_at",
    "context_at",
    "touch_at",
    "confirm_at",
    "decision_at",
    "sweep_at",
    "purge_known_at",
    "zone_known_at",
}


def _g(op: dict, name: str):
    return op.get(name)


def _cmp(op: dict, a: str, rel: str, b: str):
    return kleene_cmp(rel, _g(op, a), _g(op, b))


def m01_sequence(op: dict):
    branch = _g(op, "branch")
    body = kleene_case(branch, {
        "judas_outbound": kleene_and(_g(op, "directional_context"), _g(op, "at_rth_open"), _g(op, "objective_is_selected_exhaustion"), _g(op, "exit_window_recorded")),
        "judas_reversal": kleene_and(_g(op, "reversal_context"), _g(op, "edge_swept"), _cmp(op, "sweep_at", "<=", "confirm_at"), _g(op, "source_time_window"), _g(op, "objective_is_opposing_draw")),
        "single_extended": kleene_and(_g(op, "extended_context"), _g(op, "entry_at_eq_or_quadrant"), _g(op, "objective_is_range_edge"), _g(op, "reduced_expectations")),
        "single_purged": kleene_and(_g(op, "purged_compressed_context"), _cmp(op, "purge_known_at", "<", "decision_at"), _g(op, "entry_at_eq_or_quadrant"), _g(op, "expansion_policy")),
        "internal_rotation": kleene_and(_g(op, "rotation_context"), _g(op, "entry_at_named_internal_or_ev_band"), _g(op, "objective_is_named_rotation_target")),
        "extension_reaction": kleene_and(_g(op, "prior_expansion"), _g(op, "touch_in_source_extension_area"), _g(op, "reaction_side_confirmed"), _g(op, "objective_is_remaining_draw")),
        "other_session": kleene_and(_g(op, "source_clock_verified"), _g(op, "source_case_verified")),
        "timed_pzone_reversal": kleene_and(_g(op, "source_zone_known"), _g(op, "source_time_window"), _cmp(op, "zone_known_at", "<=", "touch_at"), _g(op, "directed_path_recorded")),
    }, default=None)
    return kleene_and(
        _g(op, "range_frozen"), _g(op, "context_fixed"), _g(op, "location_touched"),
        _g(op, "source_confirmation"), _g(op, "risk_defined"), _g(op, "objective_fixed"),
        _cmp(op, "range_known_at", "<=", "touch_at"),
        _cmp(op, "context_at", "<=", "touch_at"),
        _cmp(op, "touch_at", "<=", "confirm_at"),
        _cmp(op, "confirm_at", "<=", "decision_at"),
        body,
    )


def _m01_identity_ok(op: dict):
    """Check the identity joins required by the M01 operator input.

    Identity is carried by the evidence producer, rather than inferred from a
    nearby price.  The relation fields are optional for legacy raw-derived
    rows; when present, however, a mismatched parent, instrument, band, or
    side is a witnessed invalid join.  Missing identity evidence is left for
    the evidence seam to report as unknown.
    """

    checks: list[bool | None] = []

    range_id = op.get("range_id")
    parent_id = op.get("projection_parent_id", op.get("parent_id"))
    if range_id is not None or parent_id is not None:
        checks.append(None if range_id is None or parent_id is None else range_id == parent_id)

    instrument_id = op.get("instrument_id")
    for key in ("range_instrument_id", "context_instrument_id", "confirmation_instrument_id"):
        if key in op:
            checks.append(None if instrument_id is None or op.get(key) is None else op[key] == instrument_id)

    band_id = op.get("band_id")
    for key in ("location_band_id", "context_band_id", "confirmation_band_id"):
        if key in op:
            checks.append(None if band_id is None or op.get(key) is None else op[key] == band_id)

    side = op.get("side")
    for key in ("location_side", "context_side", "confirmation_side", "source_confirmation_side"):
        if key in op:
            checks.append(None if side is None or op.get(key) is None else op[key] == side)

    # A bound evidence layer may provide this result after checking producer
    # records.  It is conjunctive with the explicit joins above.
    if "identity_ok" in op:
        checks.append(op.get("identity_ok"))

    return kleene_and(*checks) if checks else True


def _m01_required_fields(op: dict) -> tuple[str, ...] | None:
    branch = op.get("branch")
    branch_fields = _M01_BRANCH_FIELDS.get(branch)
    if branch_fields is None:
        return None
    return _M01_COMMON_FIELDS + branch_fields


def _m01_assertion_records(op: dict) -> list[dict]:
    """Return C01 assertion records from either supported fixture spelling."""

    records = op.get("assertions")
    if records is None:
        evidence = op.get("evidence")
        if isinstance(evidence, dict):
            records = evidence.get("assertions")
    if records is None:
        return []
    if isinstance(records, dict):
        return [dict(v, field=k) if isinstance(v, dict) and "field" not in v else v for k, v in records.items()]
    return [r for r in records if isinstance(r, dict)]


def _m01_operand_bindings(op: dict) -> dict[str, dict]:
    bindings = op.get("operand_bindings")
    if bindings is None:
        evidence = op.get("evidence")
        if isinstance(evidence, dict):
            bindings = evidence.get("operand_bindings")
    if not isinstance(bindings, dict):
        return {}
    return {str(k): v for k, v in bindings.items() if isinstance(v, dict)}


def _m01_evidence_status(op: dict) -> tuple[bool | None, list[str], list[str]]:
    """Validate the minimal binding contract before evaluating M01.

    The predicate remains a literal three-valued expression.  This seam only
    prevents a flattened/naked Boolean from masquerading as a source
    assertion.  Production and supplied manifests are validated by the C01
    parser; direct fixture calls use the same assertion/binding shape.
    """

    required = _m01_required_fields(op)
    if required is None:
        return None, ["HOLE:M01:branch"], ["branch"]

    assertions = _m01_assertion_records(op)
    bindings = _m01_operand_bindings(op)
    by_field: dict[str, list[dict]] = {}
    for record in assertions:
        field = record.get("field")
        if field:
            by_field.setdefault(str(field), []).append(record)

    # A strict row must identify the candidate and method.  We do not require
    # these on raw market rows here; the manifest binder supplies them before
    # calling the scorer.  Fixture rows, by contrast, always carry them.
    if not assertions and not bindings:
        return None, ["HOLE:M01:evidence"], list(required)

    holes: list[str] = []
    unbound: list[str] = []
    invalid = False
    candidate_id = op.get("candidate_id")
    method_id = op.get("method_id", "JJ-TBR")
    branch = op.get("branch")
    band_id = op.get("band_id")
    side = op.get("side")

    for field in required:
        value_present = field in op
        value = op.get(field)
        records = by_field.get(field, [])
        binding = bindings.get(field)
        if not records and binding is None:
            unbound.append(field)
            holes.append(f"HOLE:M01:{field}")
            continue

        # Bindings may be a compact producer reference while assertions carry
        # the complete C01 provenance.  Either must agree with the flattened
        # operator value when both provide it.
        bound_value = binding.get("value") if binding is not None else None
        if binding is not None and "value" in binding and bound_value != value:
            invalid = True
        if binding is not None:
            recipe = binding.get("recipe_id", binding.get("producer_recipe_id"))
            if not recipe:
                invalid = True

        for record in records:
            if "value" in record and record.get("value") != value:
                invalid = True
            if method_id is not None and record.get("method_id") not in (None, method_id):
                invalid = True
            if branch is not None and record.get("branch") not in (None, branch):
                invalid = True
            if candidate_id is not None and record.get("candidate_id") not in (None, candidate_id):
                invalid = True
            if band_id is not None and record.get("band_id") not in (None, band_id):
                invalid = True
            if side is not None and record.get("side") not in (None, side):
                invalid = True
            if not record.get("evidence_ids"):
                invalid = True
            if record.get("known_at") is None:
                invalid = True
            if record.get("observation_start") is None or record.get("observation_end") is None:
                invalid = True
            if not record.get("evidence_mode"):
                invalid = True
            if not record.get("source_ref"):
                invalid = True

        if not value_present:
            unbound.append(field)
            holes.append(f"HOLE:M01:{field}")

    if invalid:
        return False, ["HOLE:M01:identity_or_provenance"], unbound
    if holes:
        return None, holes, unbound
    return True, [], []


PREDICATES = {("JJ-TBR", "sequence"): m01_sequence}


def causal_base_ok(op: dict) -> bool | None:
    if op.get("_wrong_identity"):
        return False
    times = [
        ("range_known_at", "touch_at"),
        ("context_at", "touch_at"),
        ("touch_at", "confirm_at"),
        ("confirm_at", "decision_at"),
        ("reference_known_at", "sweep_at"),
        ("zone_known_at", "touch_at"),
    ]
    for a, b in times:
        va, vb = op.get(a), op.get(b)
        if va is not None and vb is not None and va > vb:
            return False
    if op.get("decision_at") is not None and op.get("context_at") is not None:
        if op["context_at"] > op["decision_at"]:
            return False
    return True


def score_candidate(method_id: str, predicate: str, op: dict) -> dict:
    """Legacy M01 fixture diagnostics; never used to admit supplied episodes."""
    fn = PREDICATES[(method_id, predicate)]
    seq = fn(op)
    base = op.get("base_ok")
    if base is None:
        base = causal_base_ok(op)
    evidence_ok = True
    evidence_holes: list[str] = []
    unbound_fields: list[str] = []
    if method_id == "JJ-TBR" and predicate == "sequence":
        evidence_ok, evidence_holes, unbound_fields = _m01_evidence_status(op)
        base = kleene_and(base, _m01_identity_ok(op), evidence_ok)
        cov = op.get("coverage_ok", None)
    else:
        cov = op.get("coverage_ok", True)
    v = verdict(base, cov, seq)
    return {
        "base_ok": base,
        "coverage_ok": cov,
        "sequence_ok": seq,
        "verdict": v,
        "evidence_ok": evidence_ok,
        "hole_ids": evidence_holes,
        "unbound_fields": unbound_fields,
        "operands": jsonable(op),
    }


def _t(*clock):
    return et_ns(DAY, *clock)


_M01_PRODUCER_RECIPES = {
    "branch": "O005",
    "range_frozen": "O005",
    "context_fixed": "O009",
    "location_touched": "O002",
    "source_confirmation": "O057",
    "risk_defined": "O139",
    "objective_fixed": "O141",
    "range_known_at": "O005",
    "context_at": "O009",
    "touch_at": "O002",
    "confirm_at": "O057",
    "decision_at": "O150",
    "directional_context": "O013",
    "at_rth_open": "O050",
    "objective_is_selected_exhaustion": "O141",
    "exit_window_recorded": "O021",
    "reversal_context": "O009",
    "edge_swept": "O047",
    "sweep_at": "O047",
    "source_time_window": "O021",
    "objective_is_opposing_draw": "O141",
    "purged_compressed_context": "O012",
    "purge_known_at": "O012",
    "entry_at_eq_or_quadrant": "O007",
    "expansion_policy": "O009",
    "extended_context": "O009",
    "objective_is_range_edge": "O141",
    "reduced_expectations": "O009",
    "rotation_context": "O009",
    "entry_at_named_internal_or_ev_band": "O018",
    "objective_is_named_rotation_target": "O087",
    "prior_expansion": "O010",
    "touch_in_source_extension_area": "O015",
    "reaction_side_confirmed": "O057",
    "objective_is_remaining_draw": "O087",
    "source_clock_verified": "O003",
    "source_case_verified": "O006",
    "source_zone_known": "O019",
    "zone_known_at": "O019",
    "directed_path_recorded": "O019",
}


def _m01_sync_evidence(op: dict) -> dict:
    """Keep the compact and expanded C01 fixture spellings in sync."""

    records = _m01_evidence_records(op)
    candidate_operands = {}
    for field, binding in op.get("operand_bindings", {}).items():
        if "assertion_id" in binding:
            candidate_operands[field] = {"assertion_id": binding["assertion_id"]}
        elif "object_id" in binding:
            candidate_operands[field] = {
                "object_id": binding["object_id"],
                "value_field": binding.get("value_field", field),
            }
    candidate = {
        "candidate_id": op.get("candidate_id"),
        "method_id": op.get("method_id", "JJ-TBR"),
        "branch": op.get("branch"),
        "instrument_id": op.get("instrument_id"),
        "band_ids": [op.get("band_id")] if op.get("band_id") else [],
        "side": op.get("side"),
        "decision_at": op.get("decision_at"),
        "session_date_et": DAY.isoformat(),
        "object_ids": [row.get("object_id") for row in op.get("objects", [])],
        "assertion_ids": [row.get("assertion_id") for row in op.get("assertions", [])],
        "cohort_id": "synthetic-fixtures",
        "evidence_mode": op.get("evidence_mode", "synthetic_fixture"),
        "predicate": "sequence",
        "operands": candidate_operands,
    }
    op["candidate"] = candidate
    op["evidence_records"] = records
    op["evidence"] = {
        "candidate": candidate,
        "objects": op.get("objects", []),
        "assertions": op.get("assertions", []),
        "operand_bindings": op.get("operand_bindings", {}),
        "records": records,
    }
    return op


def _m01_evidence_records(op: dict) -> list[dict]:
    records: list[dict] = []
    for row in [*op.get("objects", []), *op.get("assertions", [])]:
        for eid in row.get("evidence_ids", []):
            if any(existing.get("evidence_id") == eid for existing in records):
                continue
            field = row.get("field")
            value = row.get("value") if field else row.get("value", {})
            records.append({
                "evidence_id": eid,
                "method_id": "JJ-TBR",
                "branch": op.get("branch"),
                "instrument_id": op.get("instrument_id"),
                "band_id": op.get("band_id"),
                "side": op.get("side"),
                "source_ref": "M01 synthetic source-illustration fixture",
                "source_version": "method-pack-v1",
                "description": f"Synthetic source observation for {field or row.get('recipe_id')}",
                "payload": {"field": field, "value": jsonable(value)},
                "observation_start": row.get("observation_start", row.get("formation_start")),
                "observation_end": row.get("observation_end", row.get("formation_end")),
                "known_at": row.get("known_at"),
                "evidence_mode": "synthetic_fixture",
            })
    return records


def _m01_object(
    op: dict,
    field: str,
    recipe_id: str,
    known_at: int,
    *,
    value: Any = None,
    parent_ids: tuple[str, ...] = (),
    state: str = "supplied",
    object_id: str | None = None,
) -> dict:
    object_id = object_id or f"{op['candidate_id']}:{field}"
    if value is None:
        value = {"field": field, "value": op.get(field)}
    return {
        "object_id": object_id,
        "recipe_id": recipe_id,
        "method_id": "JJ-TBR",
        "branch_scope": [op.get("branch")],
        "author": "JJumbo",
        "parent_ids": list(parent_ids),
        "source_ref": "M01 synthetic source-illustration fixture",
        "source_version": "method-pack-v1",
        "value": value,
        "units": {
            field: "event_key?" if field in _M01_EVENT_FIELDS else ("enum" if field == "branch" else "boolean?"),
            "price": "points",
            "time": "UTC_ns",
        },
        "formation_start": op.get("range_start_at", op.get("range_known_at")),
        "formation_end": known_at,
        "as_of": known_at,
        "known_at": known_at,
        "state": state,
        "hole_ids": [],
        "evidence_ids": [f"ev:{object_id}"],
        "raw_member_locators": [{"fixture_id": op.get("fixture_id"), "field": field}],
        "band_id": op.get("band_id"),
        "side": op.get("side"),
        "instrument_id": op.get("instrument_id"),
    }


def _m01_assertion(
    op: dict,
    field: str,
    recipe_id: str,
    known_at: int,
    *,
    observation_start: int | None = None,
    observation_end: int | None = None,
    value: Any = None,
    assertion_id: str | None = None,
    object_id: str | None = None,
) -> dict:
    if value is None:
        value = op.get(field)
    if observation_start is None:
        observation_start = op.get("range_start_at", known_at)
    if observation_end is None:
        observation_end = known_at
    if assertion_id is None:
        assertion_id = f"{op['candidate_id']}:{field}"
    if object_id is None:
        object_id = f"{op['candidate_id']}:{field}"
    return {
        "assertion_id": assertion_id,
        "field": field,
        "value": value,
        "method_id": "JJ-TBR",
        "branch": op.get("branch"),
        "candidate_id": op.get("candidate_id"),
        "instrument_id": op.get("instrument_id"),
        "band_id": op.get("band_id"),
        "side": op.get("side"),
        "evidence_ids": [f"ev:{assertion_id}"],
        "observation_start": observation_start,
        "observation_end": observation_end,
        "known_at": known_at,
        "available_at": known_at,
        "evidence_mode": "synthetic_fixture",
        "source_ref": "M01 synthetic source-illustration fixture",
        "source_version": "method-pack-v1",
        "reason": f"{field} supplied by {recipe_id} for this fixture",
        "recipe_id": recipe_id,
        "producer_recipe_id": recipe_id,
        "object_id": object_id,
    }


def _m01_add_binding(
    op: dict,
    field: str,
    *,
    recipe_id: str | None = None,
    known_at: int | None = None,
    observation_start: int | None = None,
    observation_end: int | None = None,
    value: Any = None,
    parent_ids: tuple[str, ...] = (),
    state: str = "supplied",
) -> None:
    recipe_id = recipe_id or _M01_PRODUCER_RECIPES[field]
    if known_at is None:
        if field.endswith("_at"):
            known_at = op.get(field)
        elif field in ("range_frozen", "range_known_at"):
            known_at = op.get("range_known_at")
        elif field in ("context_fixed", "context_at"):
            known_at = op.get("context_at")
        elif field in {
            "directional_context",
            "reversal_context",
            "extended_context",
            "purged_compressed_context",
            "rotation_context",
            "expansion_policy",
            "reduced_expectations",
            "source_clock_verified",
            "source_case_verified",
        }:
            known_at = op.get("context_at")
        elif field in ("location_touched", "touch_at", "edge_swept"):
            known_at = op.get("touch_at")
        elif field in ("source_confirmation", "confirm_at"):
            known_at = op.get("confirm_at")
        else:
            known_at = op.get("decision_at")
    if known_at is None:
        return
    object_row = _m01_object(
        op,
        field,
        recipe_id,
        known_at,
        parent_ids=parent_ids,
        state=state,
        value={field: op.get(field)},
    )
    objects = op.setdefault("objects", [])
    objects[:] = [row for row in objects if row.get("object_id") != object_row["object_id"]]
    objects.append(object_row)
    assertions = op.setdefault("assertions", [])
    assertions[:] = [row for row in assertions if row.get("field") != field]
    bindings = op.setdefault("operand_bindings", {})
    if field in _M01_EVENT_FIELDS or field == "branch":
        # C01 event_key operands are object values.  Assertions are reserved
        # for nullable Booleans and cannot carry an event timestamp.
        bindings[field] = {
            "field": field,
            "value": op.get(field) if value is None else value,
            "object_id": object_row["object_id"],
            "value_field": field,
            "recipe_id": recipe_id,
            "producer_recipe_id": recipe_id,
            "known_at": known_at,
            "evidence_ids": list(object_row["evidence_ids"]),
            "band_id": op.get("band_id"),
            "side": op.get("side"),
        }
    else:
        assertion = _m01_assertion(
            op,
            field,
            recipe_id,
            known_at,
            observation_start=observation_start,
            observation_end=observation_end,
            value=op.get(field) if value is None else value,
            object_id=object_row["object_id"],
        )
        assertions.append(assertion)
        bindings[field] = {
            "field": field,
            "value": assertion["value"],
            "assertion_id": assertion["assertion_id"],
            "recipe_id": recipe_id,
            "producer_recipe_id": recipe_id,
            "object_id": object_row["object_id"],
            "known_at": known_at,
            "evidence_ids": list(assertion["evidence_ids"]),
            "band_id": op.get("band_id"),
            "side": op.get("side"),
        }


def _m01_remove_binding(op: dict, field: str) -> None:
    op.setdefault("assertions", [])[:] = [
        row for row in op.get("assertions", []) if row.get("field") != field
    ]
    op.setdefault("objects", [])[:] = [
        row for row in op.get("objects", []) if row.get("object_id") != f"{op.get('candidate_id')}:{field}"
    ]
    op.setdefault("operand_bindings", {}).pop(field, None)
    _m01_sync_evidence(op)


def _m01_update_field(op: dict, field: str, value: Any, *, known_at: int | None = None) -> dict:
    op = deepcopy(op)
    op[field] = value
    for row in op.get("assertions", []):
        if row.get("field") == field:
            row["value"] = value
            if known_at is not None:
                row["known_at"] = known_at
                row["available_at"] = known_at
                row["observation_end"] = known_at
    for row in op.get("objects", []):
        if row.get("object_id", "").endswith(f":{field}"):
            if isinstance(row.get("value"), dict):
                row["value"][field] = value
            if known_at is not None:
                row["known_at"] = known_at
                row["as_of"] = known_at
                row["formation_end"] = known_at
    if field in op.get("operand_bindings", {}):
        op["operand_bindings"][field]["value"] = value
        if known_at is not None:
            op["operand_bindings"][field]["known_at"] = known_at
    return _m01_sync_evidence(op)


def _m01_retag_branch(op: dict, branch: str, values: dict[str, Any]) -> dict:
    """Create a branch-scoped fixture while preserving C01 provenance."""

    op = deepcopy(op)
    op["branch"] = branch
    op["fixture_branch"] = branch
    for field, value in values.items():
        op[field] = value
    active = set(_M01_COMMON_FIELDS + _M01_BRANCH_FIELDS[branch])
    op["assertions"] = [
        row for row in op.get("assertions", []) if row.get("field") in active
    ]
    op["objects"] = [
        row for row in op.get("objects", [])
        if row.get("object_id") == op.get("range_id")
        or row.get("object_id", "").split(":")[-1] in active
    ]
    op["operand_bindings"] = {
        field: binding
        for field, binding in op.get("operand_bindings", {}).items()
        if field in active
    }
    for row in op["assertions"]:
        row["branch"] = branch
    for row in op["objects"]:
        row["branch_scope"] = [branch]
    for field in _M01_COMMON_FIELDS:
        # Common records from the positive fixture remain tied to the same
        # candidate/band/side but need the new branch label.
        if field in op:
            _m01_add_binding(op, field, recipe_id=_M01_PRODUCER_RECIPES[field])
    for field in _M01_BRANCH_FIELDS[branch]:
        if field in op and op.get(field) is not None:
            _m01_add_binding(op, field, recipe_id=_M01_PRODUCER_RECIPES[field])
    return _m01_sync_evidence(op)


def m01_judas_reversal_fixture() -> dict:
    """Raw positive M01-F1 operator input with C01 evidence records."""

    range_id = "M01-F1-range-6-9"
    band_id = "M01-F1-band-high"
    pos = {
        "fixture_id": "M01-F1",
        "candidate_id": "M01-F1",
        "method_id": "JJ-TBR",
        "branch": "judas_reversal",
        "range_id": range_id,
        "projection_parent_id": range_id,
        "band_id": band_id,
        "location_band_id": band_id,
        "context_band_id": band_id,
        "confirmation_band_id": band_id,
        "location_side": "short",
        "context_side": "short",
        "confirmation_side": "short",
        "source_confirmation_side": "short",
        "range_instrument_id": "NQ",
        "context_instrument_id": "NQ",
        "confirmation_instrument_id": "NQ",
        "instrument_id": "NQ",
        "side": "short",
        "range_start_at": _t(6, 0),
        "range_frozen": True,
        "context_fixed": True,
        "location_touched": True,
        "source_confirmation": True,
        "risk_defined": True,
        "objective_fixed": True,
        "range_known_at": _t(9, 0),
        "context_at": _t(9, 20),
        "touch_at": _t(9, 41),
        "confirm_at": _t(9, 43),
        "decision_at": _t(9, 44),
        "reversal_context": True,
        "edge_swept": True,
        "sweep_at": _t(9, 41),
        "source_time_window": True,
        "objective_is_opposing_draw": True,
        "coverage_ok": True,
        "evidence_mode": "synthetic_fixture",
        "source_ref": "M01-F1 synthetic source-illustration",
        "sweep_depth_w": Decimal("0.05"),
        "range_L": Decimal("100"),
        "range_H": Decimal("120"),
        "range_W": Decimal("20"),
        "sweep_px": Decimal("121"),
        "rejection_structure_high": Decimal("121"),
        "stop_px": Decimal("122"),
        "stop_above_structure": True,
        "objective_px": Decimal("100"),
        "objective_role": "opposing_draw",
        "objective_parent_id": range_id,
        "parent_links": {
            "range_id": range_id,
            "projection_parent_id": range_id,
            "objective_parent_id": range_id,
        },
        "identity_links": [
            {"relationship": "projection_parent", "child_id": band_id, "parent_id": range_id},
            {"relationship": "objective_parent", "child_id": "objective", "parent_id": range_id},
        ],
        "confirmation_mode": "source_rejection",
        "rejection_observed": True,
        "continued_acceptance_above_edge": False,
        "objects": [],
        "assertions": [],
        "operand_bindings": {},
    }
    # A named range parent lets identity mutations be checked as a real join,
    # rather than by a test-only sentinel.
    range_object = _m01_object(
        pos,
        "range_frozen",
        "O005",
        pos["range_known_at"],
        value={"L": pos["range_L"], "H": pos["range_H"], "W": pos["range_W"]},
        object_id=range_id,
    )
    pos["objects"].append(range_object)
    for field in ("branch",) + _M01_COMMON_FIELDS + _M01_BRANCH_FIELDS["judas_reversal"]:
        _m01_add_binding(pos, field, parent_ids=(range_id,) if field in {"source_confirmation", "objective_fixed"} else ())
    return _m01_sync_evidence(pos)


def _m01_fixture_document(op: dict) -> dict:
    """Return the canonical C01 document represented by an M01 fixture.

    The fixture helpers maintain a compact operator view for direct predicate
    tests, but the method-pack runner must consume the same typed producer
    records as a supplied episode.  Rebuilding a document from the flattened
    values would erase mutations to parent joins, availability, and evidence
    provenance, so this function only packages the already-built records.
    """

    from trading_research.research.method_pack import FORMULA_VERSION

    fixture = _m01_sync_evidence(deepcopy(op))
    return {
        "formula_version": FORMULA_VERSION,
        "candidates": [deepcopy(fixture["candidate"])],
        "objects": deepcopy(fixture.get("objects", [])),
        "assertions": deepcopy(fixture.get("assertions", [])),
        "evidence": deepcopy(fixture.get("evidence_records", [])),
    }


def _m01_mutate_identity_join(op: dict) -> dict:
    """Create an identity-negative fixture by changing a real parent join."""

    op = deepcopy(op)
    range_object = next(
        (row for row in op.get("objects", []) if row.get("object_id") == op.get("range_id")),
        None,
    )
    if range_object is None:
        # Keep this defensive path deterministic for callers constructing a
        # reduced fixture by hand.  The normal M01 fixture always has a named
        # range parent.
        return _m01_sync_evidence(op)

    foreign = deepcopy(range_object)
    foreign["object_id"] = f"{op.get('candidate_id')}:other-range"
    foreign["band_id"] = f"{op.get('band_id')}:other-range"
    foreign["value"] = {
        "L": op.get("range_L"),
        "H": op.get("range_H"),
        "W": op.get("range_W"),
    }
    op.setdefault("objects", []).append(foreign)

    # Repoint a used event producer to the foreign range.  The positive fixture
    # has a named range parent for the semantic confirmation/objective records,
    # while the event operands are the records that score_episode consumes.
    # Attaching the foreign parent to context_at makes the mismatch observable
    # through the real C01 object graph; changing only a compact op-level label
    # would be discarded by the parser.
    target = next(
        (row for row in op["objects"] if row.get("object_id") == f"{op.get('candidate_id')}:context_at"),
        None,
    )
    if target is None:
        target = next(
            (row for row in op["objects"] if row.get("object_id") == f"{op.get('candidate_id')}:source_confirmation"),
            None,
        )
    if target is not None:
        target["parent_ids"] = [foreign["object_id"]]

    op["projection_parent_id"] = foreign["object_id"]
    op["parent_id"] = foreign["object_id"]
    op["objective_parent_id"] = foreign["object_id"]
    op["identity_ok"] = False
    op.setdefault("parent_links", {})["projection_parent_id"] = foreign["object_id"]
    op.setdefault("parent_links", {})["objective_parent_id"] = foreign["object_id"]
    for link in op.get("identity_links", []):
        link["parent_id"] = foreign["object_id"]
    return _m01_sync_evidence(op)


# Explicit aliases make the fixture seam easy for the pass runner/evidence
# binder to consume without exposing a second, divergent fixture definition.
m01_positive_fixture_op = m01_judas_reversal_fixture
m01_fixture_inputs = m01_judas_reversal_fixture


def m01_method_fixtures() -> list[dict]:
    pos = m01_judas_reversal_fixture()
    rows = [_method_case("JJ-TBR", "sequence", "M01-F1", pos, "pass")]

    # Fully observed acceptance above the range edge is a witnessed rejection
    # of the source reversal route.  A later target remains irrelevant.
    acceptance = _m01_update_field(pos, "source_confirmation", False)
    acceptance["confirmation_mode"] = "continued_acceptance"
    acceptance["rejection_observed"] = False
    acceptance["continued_acceptance_above_edge"] = True
    rows.append(_method_case("JJ-TBR", "sequence", "M01-F2-acceptance", acceptance, "fail"))

    # Context fixed at 09:50 is after both the touch and the 09:44 decision.
    late = _m01_update_field(pos, "context_at", _t(9, 50), known_at=_t(9, 50))
    rows.append(_method_case("JJ-TBR", "sequence", "M01-F2-late-context", late, "fail"))

    # The projection/parent identity is deliberately from another range.
    identity = _m01_mutate_identity_join(pos)
    rows.append(_method_case("JJ-TBR", "sequence", "M01-F2-identity", identity, "fail"))

    later_target = deepcopy(acceptance)
    later_target["later_target"] = Decimal("80")
    later_target["later_target_at"] = _t(10, 0)
    rows.append(_method_case("JJ-TBR", "sequence", "M01-F2-later-target", later_target, "fail"))

    missing_confirmation = _m01_update_field(pos, "source_confirmation", None)
    _m01_remove_binding(missing_confirmation, "source_confirmation")
    missing_confirmation["coverage_ok"] = None
    missing_confirmation["hole_ids"] = ["HOLE:M01:source_confirmation"]
    rows.append(_method_case("JJ-TBR", "sequence", "M01-F3-confirmation", missing_confirmation, "unknown"))

    # Branch-specific source holes deliberately remain unknown.  No proxy is
    # substituted for P-zone, EVRange, or Session Stat+ evidence.
    pzone = _m01_retag_branch(pos, "timed_pzone_reversal", {
        "source_zone_known": None,
        "source_time_window": True,
        "zone_known_at": None,
        "directed_path_recorded": None,
    })
    for field in ("source_zone_known", "zone_known_at", "directed_path_recorded"):
        _m01_remove_binding(pzone, field)
    pzone["coverage_ok"] = None
    pzone["hole_ids"] = ["HOLE:O019:source_zone"]
    rows.append(_method_case("JJ-TBR", "sequence", "M01-F3-pzone", pzone, "unknown"))

    ev = _m01_retag_branch(pos, "internal_rotation", {
        "rotation_context": True,
        "entry_at_named_internal_or_ev_band": None,
        "objective_is_named_rotation_target": True,
    })
    _m01_remove_binding(ev, "entry_at_named_internal_or_ev_band")
    ev["coverage_ok"] = None
    ev["hole_ids"] = ["HOLE:O018:engine"]
    rows.append(_method_case("JJ-TBR", "sequence", "M01-F3-ev", ev, "unknown"))

    session_stat = _m01_retag_branch(pos, "single_purged", {
        "purged_compressed_context": True,
        "purge_known_at": _t(9, 35),
        "entry_at_eq_or_quadrant": True,
        "expansion_policy": None,
    })
    _m01_remove_binding(session_stat, "expansion_policy")
    session_stat["coverage_ok"] = None
    session_stat["hole_ids"] = ["HOLE:O017:policy"]
    rows.append(_method_case("JJ-TBR", "sequence", "M01-F3-session-stat", session_stat, "unknown"))

    # C08 method mutations are separate rows so the report can distinguish
    # causal violations from ordinary source-negative controls.
    c08_late = deepcopy(pos)
    c08_late["range_known_at"] = _t(9, 45)
    c08_late = _m01_update_field(c08_late, "range_known_at", _t(9, 45), known_at=_t(9, 45))
    c08_late["coverage_ok"] = True
    rows.append(_method_case("JJ-TBR", "sequence", "M01-F1:c08-late", c08_late, "fail", kind="c08_late"))

    c08_missing = deepcopy(pos)
    c08_missing.pop("location_touched", None)
    _m01_remove_binding(c08_missing, "location_touched")
    c08_missing["coverage_ok"] = None
    rows.append(_method_case("JJ-TBR", "sequence", "M01-F1:c08-missing", c08_missing, "unknown", kind="c08_missing"))

    c08_identity = _m01_mutate_identity_join(pos)
    rows.append(_method_case("JJ-TBR", "sequence", "M01-F1:c08-identity", c08_identity, "fail", kind="c08_identity"))
    return rows


def _method_case(
    method_id: str,
    predicate: str,
    fid: str,
    op: dict,
    expected: str,
    *,
    kind: str = "method",
) -> dict:
    from trading_research.research.method_pack.evidence import parse_manifest, score_episode

    if (method_id, predicate) != ("JJ-TBR", "sequence"):
        raise ValueError('this fixture bridge is only for the M01 sequence')
    document = _m01_fixture_document(op)
    candidates, objects, assertions, evidence = parse_manifest(document, method_id)
    candidate_id = document["candidates"][0]["candidate_id"]
    got = score_episode(candidates[candidate_id], objects, assertions, evidence)
    status = "pass" if got["verdict"] == expected else "fail"
    return {
        "id": fid,
        "recipe": method_id,
        "kind": kind,
        "predicate": predicate,
        "status": status,
        "failures": [] if status == "pass" else [f"verdict {got['verdict']} != {expected}"],
        "actual_value": got,
        "inputs": jsonable(document),
        "expected": {"verdict": expected},
        "expected_verdict": expected,
        "evidence_mode": "synthetic_fixture",
        "operands": jsonable(op),
        "detected_causal_violation": got["base_ok"] is False and expected == "fail",
        "hole_ids": got.get("hole_ids", []),
        "unbound_fields": got.get("unbound_fields", []),
    }


def method_fixtures(method_id: str) -> list[dict]:
    """Run the completed method slice; a missing slice is an implementation error."""
    from importlib import import_module
    from .catalog import METHOD_BY_ID
    if method_id == "JJ-TBR":
        return m01_method_fixtures()
    module = __package__ + '.method_slices.' + METHOD_BY_ID[method_id].lower()
    return import_module(module).method_fixtures()
