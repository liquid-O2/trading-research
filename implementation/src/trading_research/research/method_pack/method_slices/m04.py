"""M04 GB-SCALP acceptance cases at the C01 production boundary.

The source describes a directional scalp loop, but it does not publish a
repeatable entry trigger, impulse selector, general invalidation rule, or exit
algorithm.  The four case-description operands below therefore stay bounded
to the source observations that are actually disclosed.  ``automatic_admission``
is evaluated from the FORMULAS ``NULL`` expression and is never reconstructed
here.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from decimal import Decimal

from ..clocks import et_ns
from ..evidence import fixture_document
from ..fixture_utils import method_case


METHOD = "GB-SCALP"
DAY = date(2026, 1, 15)


def _t(hour: int, minute: int, second: int = 0) -> int:
    return et_ns(DAY, hour, minute, second)


# A Boolean producer is available at the source event that supplies it.  The
# caps are intentionally event keys from the fixture payload, rather than a
# universal entry clock or a policy inferred from the 20-point illustration.
STAGE_LIMITS = {
    "direction_recorded_before_entry": "direction_at",
    "small_size_recorded": "size_at",
    "source_directional_pullback_observed": "pullback_at",
    "source_scalp_management_recorded": "management_at",
}


def _positive_case(branch: str = "bearish_small_scalp") -> dict:
    """Return the two source-described branch examples.

    M04-F1 is the bearish case from the acceptance text: the directional read
    is recorded at 09:30, a favorable pop is observed at 09:40, one contract is
    declared at 09:39, the short is entered at 09:41, and the source supplies a
    limited 20-point management illustration.  The bullish branch keeps the
    same disclosed loop and uses the source's discount-pullback wording.
    """

    if branch == "bearish_small_scalp":
        side = "short"
        direction = "bearish"
        pullback_kind = "favorable_pop"
        location = "directional_pullback"
    elif branch == "bullish_discount_pullback":
        side = "long"
        direction = "bullish"
        pullback_kind = "discount_pullback"
        location = "discount"
    else:
        raise ValueError(f"unknown GB-SCALP branch: {branch}")

    band_id = "GB-SCALP-range-100-120"
    return {
        "branch": branch,
        "side": side,
        "instrument_id": "NQ-fixture",
        "band_id": band_id,
        "direction_recorded_before_entry": True,
        "small_size_recorded": True,
        "source_directional_pullback_observed": True,
        "source_scalp_management_recorded": True,
        # Actual C01 observation/consumption times.
        "direction_at": _t(9, 30),
        "bias_recorded_at": _t(9, 30),
        "pullback_at": _t(9, 40),
        "pop_at": _t(9, 40),
        "size_at": _t(9, 39),
        "declared_size_at": _t(9, 39),
        "entry_at": _t(9, 41),
        "management_at": _t(9, 42),
        # Source observations retained in the evidence payload.  These are
        # checked by audit_candidate; they are not extra FORMULAS operands.
        "direction_side": direction,
        "bias_side": direction,
        "direction": direction,
        "pullback_kind": pullback_kind,
        "source_pullback": pullback_kind,
        "pullback_location": location,
        "pullback_range_id": band_id,
        "parent_range_id": band_id,
        "size_contracts": 1,
        "declared_size": 1,
        "quantity": 1,
        "small_size_limit": 1,
        "management_policy": "limited_source_scalp",
        "management_points": Decimal("20"),
        "limited_scalp_points": Decimal("20"),
        "scalp_management_points": Decimal("20"),
        "source_management_reference": "cited 20-point limited scalp case",
        # The management observation is part of the disclosed case record, so
        # the candidate cutoff follows the entry and the action.
        "decision_at": _t(9, 42),
    }


def _document(fid: str, predicate: str, op: dict) -> dict:
    return fixture_document(METHOD, predicate, fid, op)


def _payloads_for(candidate, field, objects, assertions, evidence) -> list[dict]:
    """Collect the actual C01 payloads for one bound producer.

    ``fixture_document`` puts the compact fixture values in an observation
    payload.  Reading that payload here means late, missing, and identity
    mutations operate on the same assertion/evidence records that
    ``score_episode`` consumes.
    """

    binding = candidate.get("operands", {}).get(field, {})
    assertion = assertions.get(binding.get("assertion_id"), {})
    obj = objects.get(binding.get("object_id"), {})
    records = []
    for record in (assertion, obj):
        if isinstance(record, dict):
            value = record.get("value")
            if isinstance(value, dict):
                records.append(value)
            for evidence_id in record.get("evidence_ids", ()):
                observed = evidence.get(evidence_id, {})
                payload = observed.get("payload")
                if isinstance(payload, dict):
                    records.append(payload)
                    observation = payload.get("observation")
                    if isinstance(observation, dict):
                        printed = observation.get("printed_inputs")
                        if isinstance(printed, dict):
                            records.append(printed)
    return records


def _values(payloads: list[dict], names: tuple[str, ...]) -> list[object]:
    values = []
    for payload in payloads:
        for name in names:
            if name in payload and payload[name] is not None:
                values.append(payload[name])
    return values


def _first(payloads: list[dict], names: tuple[str, ...]):
    values = _values(payloads, names)
    return values[0] if values else None


def _direction_matches(value, side: str) -> bool:
    if side == "short":
        return value in {"short", "bearish"}
    if side == "long":
        return value in {"long", "bullish"}
    return False


def _source_hole(field: str, reason: str, recipe_id: str) -> dict:
    return {
        "field": field,
        "kind": "source_definition",
        "unknown": True,
        "reason": reason,
        "recipe_id": recipe_id,
    }


def audit_candidate(candidate, operands, objects, assertions, evidence) -> list[dict]:
    """Audit relationships that nullable source flags cannot prove.

    A witnessed timing/side/size/parent violation sets ``base_ok`` false in
    the shared evidence scorer.  Missing source details become coverage
    unknown.  The automatic selector's four source-definition holes are
    emitted on every automatic result, while the unresolved general target
    policy is informational and does not change admission.
    """

    findings: list[dict] = []
    side = operands.get("side")
    entry_at = _first(_payloads_for(candidate, "direction_recorded_before_entry", objects, assertions, evidence), ("entry_at",))

    def add(field: str, kind: str, reason: str, recipe_id: str, *, unknown: bool = False,
            affects_admission: bool | None = None, affected_output: str | None = None) -> None:
        finding = {
            "field": field,
            "kind": kind,
            "reason": reason,
            "recipe_id": recipe_id,
        }
        if unknown:
            finding["unknown"] = True
        if affects_admission is not None:
            finding["affects_admission"] = affects_admission
        if affected_output is not None:
            finding["affected_output"] = affected_output
        findings.append(finding)

    if operands.get("direction_recorded_before_entry") is True:
        payloads = _payloads_for(candidate, "direction_recorded_before_entry", objects, assertions, evidence)
        directions = _values(payloads, ("direction_side", "bias_side", "direction"))
        direction_times = _values(payloads, ("direction_at", "bias_recorded_at"))
        if not directions or not direction_times or entry_at is None:
            findings.append(_source_hole(
                "direction_recorded_before_entry",
                "The source direction and its pre-entry timestamp are not supplied",
                "O136",
            ))
        elif any(not _direction_matches(value, side) for value in directions):
            add("direction_recorded_before_entry", "identity",
                "The recorded Green Bird direction does not match the actual scalp side",
                "O136")
        elif any(when >= entry_at for when in direction_times):
            add("direction_recorded_before_entry", "ordering",
                "The directional read was recorded at or after the scalp entry",
                "O136")

    if operands.get("small_size_recorded") is True:
        payloads = _payloads_for(candidate, "small_size_recorded", objects, assertions, evidence)
        sizes = _values(payloads, ("size_contracts", "declared_size", "quantity"))
        limits = _values(payloads, ("small_size_limit",))
        size_times = _values(payloads, ("size_at", "declared_size_at"))
        if not sizes or not limits or not size_times or entry_at is None:
            findings.append(_source_hole(
                "small_size_recorded",
                "The actual quantity, explicit small-size policy, and declaration time are not supplied",
                "O140",
            ))
        elif any(Decimal(str(size)) > Decimal(str(limit)) for size in sizes for limit in limits):
            add("small_size_recorded", "identity",
                "The actual quantity exceeds the explicitly supplied small-size policy",
                "O140")
        elif any(when > entry_at for when in size_times):
            add("small_size_recorded", "ordering",
                "The small exposure was declared after the scalp entry",
                "O140")

    if operands.get("source_directional_pullback_observed") is True:
        payloads = _payloads_for(candidate, "source_directional_pullback_observed", objects, assertions, evidence)
        pullback_times = _values(payloads, ("pullback_at", "pop_at"))
        parent_ids = _values(payloads, ("pullback_range_id", "parent_range_id"))
        if not pullback_times or not parent_ids or entry_at is None:
            findings.append(_source_hole(
                "source_directional_pullback_observed",
                "The favorable pullback/pop and its selected parent range are not supplied",
                "O053",
            ))
        elif any(parent_id not in candidate.get("band_ids", ()) for parent_id in parent_ids):
            add("source_directional_pullback_observed", "identity",
                "The observed pullback is attached to a different parent range",
                "O053")
        elif any(when >= entry_at for when in pullback_times):
            add("source_directional_pullback_observed", "ordering",
                "The favorable pullback/pop was observed at or after the scalp entry",
                "O053")

    if operands.get("source_scalp_management_recorded") is True:
        payloads = _payloads_for(candidate, "source_scalp_management_recorded", objects, assertions, evidence)
        management_times = _values(payloads, ("management_at",))
        policy = _first(payloads, ("management_policy",))
        points = _values(payloads, ("management_points", "limited_scalp_points", "scalp_management_points"))
        if not management_times or policy is None or not points or entry_at is None:
            findings.append(_source_hole(
                "source_scalp_management_recorded",
                "The source limited-scalp management record is incomplete",
                "O142",
            ))
        elif any(when <= entry_at for when in management_times):
            add("source_scalp_management_recorded", "ordering",
                "The observed scalp-management action does not follow the entry",
                "O142")

    if candidate.get("predicate") == "automatic_admission":
        # These are the exact source gaps named by the M04 section.  Keep the
        # names independent so a report can show all four holes on every row.
        findings.extend([
            _source_hole("entry_trigger",
                         "The source does not disclose a repeatable full scalp entry trigger",
                         "M04"),
            _source_hole("measured_impulse",
                         "The source does not disclose how the directional impulse is selected or measured",
                         "O053"),
            _source_hole("invalidation",
                         "The source does not disclose a general entry-side invalidation rule",
                         "O139"),
            _source_hole("exit_algorithm",
                         "The source does not disclose a general scalp exit algorithm",
                         "O142"),
        ])
        findings.append({
            "field": "general_target_policy",
            "kind": "source_conflict",
            "reason": "The cited 20-point example is source management context, not a general target policy",
            "recipe_id": "O141",
            "unknown": True,
            "affects_admission": False,
            "affected_output": "target_policy",
        })

    return findings


def _late_direction_document(fid: str, op: dict) -> dict:
    """Mutate actual direction assertion/evidence availability after entry."""

    document = _document(fid, "case_description", op)
    field = "direction_recorded_before_entry"
    candidate = document["candidates"][0]
    assertion_id = candidate["operands"][field]["assertion_id"]
    assertion = next(row for row in document["assertions"] if row["assertion_id"] == assertion_id)
    late = _t(9, 43)
    assertion.update(known_at=late, observation_start=late, observation_end=late)
    for evidence_id in assertion["evidence_ids"]:
        observed = next(row for row in document["evidence"] if row["evidence_id"] == evidence_id)
        observed.update(known_at=late, observation_start=late, observation_end=late)
    return document


def _missing_document(fid: str, op: dict) -> dict:
    """Remove a real candidate binding so C01 reports a missing producer."""

    document = _document(fid, "case_description", op)
    document["candidates"][0]["operands"].pop("small_size_recorded")
    return document


def _identity_document(fid: str, op: dict) -> dict:
    """Move the actual bound direction assertion/evidence to a foreign band."""

    document = _document(fid, "case_description", op)
    field = "direction_recorded_before_entry"
    candidate = document["candidates"][0]
    assertion_id = candidate["operands"][field]["assertion_id"]
    assertion = next(row for row in document["assertions"] if row["assertion_id"] == assertion_id)
    assertion["band_id"] = "foreign-band"
    for evidence_id in assertion["evidence_ids"]:
        observed = next(row for row in document["evidence"] if row["evidence_id"] == evidence_id)
        observed["band_id"] = "foreign-band"
    return document


def method_fixtures() -> list[dict]:
    rows: list[dict] = []

    bearish = _positive_case()
    rows.append(method_case(METHOD, "case_description", "M04-F1",
                            _document("M04-F1", "case_description", bearish), "pass"))

    bullish = _positive_case("bullish_discount_pullback")
    rows.append(method_case(METHOD, "case_description", "M04-F1-bullish",
                            _document("M04-F1-bullish", "case_description", bullish), "pass"))

    # Automatic admission is deliberately unknown even when the bounded case
    # description passes.  Keep one row per positive branch so both declared
    # branches are represented without inventing a selector.
    rows.append(method_case(METHOD, "automatic_admission", "M04-F1-automatic",
                            _document("M04-F1-automatic", "automatic_admission", bearish), "unknown"))
    rows.append(method_case(METHOD, "automatic_admission", "M04-F1-bullish-automatic",
                            _document("M04-F1-bullish-automatic", "automatic_admission", bullish), "unknown"))

    late = deepcopy(bearish)
    late["direction_at"] = _t(9, 43)
    late["bias_recorded_at"] = _t(9, 43)
    rows.append(method_case(METHOD, "case_description", "M04-F2-late-direction",
                            _late_direction_document("M04-F2-late-direction", late), "fail",
                            kind="negative"))

    wrong_side = deepcopy(bearish)
    wrong_side.update(direction_side="bullish", bias_side="bullish", direction="bullish")
    rows.append(method_case(METHOD, "case_description", "M04-F2-wrong-side",
                            _document("M04-F2-wrong-side", "case_description", wrong_side), "fail",
                            kind="negative"))

    large = deepcopy(bearish)
    large.update(size_contracts=2, declared_size=2, quantity=2)
    rows.append(method_case(METHOD, "case_description", "M04-F2-large-size",
                            _document("M04-F2-large-size", "case_description", large), "fail",
                            kind="negative"))

    # M04-F3 leaves the disclosed loop auditable while preserving the source
    # holes.  Automatic rows remain NULL and carry all four admission holes.
    for suffix, field in (
        ("direction", "direction_recorded_before_entry"),
        ("pullback", "source_directional_pullback_observed"),
        ("management", "source_scalp_management_recorded"),
    ):
        hole = deepcopy(bearish)
        hole[field] = None
        rows.append(method_case(METHOD, "case_description", f"M04-F3-{suffix}",
                                _document(f"M04-F3-{suffix}", "case_description", hole),
                                "unknown", kind="hole"))

    rows.append(method_case(METHOD, "automatic_admission", "M04-F3-automatic",
                            _document("M04-F3-automatic", "automatic_admission", bearish),
                            "unknown", kind="hole"))

    # C08 mutations alter C01 assertion/evidence records.  No private
    # ``late``/``identity`` fixture flags participate in scoring.
    rows.append(method_case(METHOD, "case_description", "M04-F1:late",
                            _late_direction_document("M04-F1:late", bearish), "fail",
                            kind="c08_late"))
    rows.append(method_case(METHOD, "case_description", "M04-F1:missing",
                            _missing_document("M04-F1:missing", bearish), "unknown",
                            kind="c08_missing"))
    rows.append(method_case(METHOD, "case_description", "M04-F1:identity",
                            _identity_document("M04-F1:identity", bearish), "fail",
                            kind="c08_identity"))

    return rows


def semantic_audit() -> dict:
    rows = method_fixtures()
    automatic_hole_fields = set()
    for row in rows:
        if row["predicate"] != "automatic_admission":
            continue
        for hole in row["actual_value"]["holes"]:
            if hole.get("kind") != "source_definition":
                continue
            field = hole.get("field")
            if field is None:
                field = (hole.get("missing_fields") or [None])[0]
            if field is not None:
                automatic_hole_fields.add(field)
    return {
        "fixture_count": len(rows),
        "all_pass": all(row["status"] == "pass" for row in rows),
        "predicates": sorted({row["predicate"] for row in rows}),
        "automatic_hole_fields": sorted(automatic_hole_fields),
    }


__all__ = [
    "METHOD",
    "STAGE_LIMITS",
    "_document",
    "_positive_case",
    "_t",
    "audit_candidate",
    "method_fixtures",
    "semantic_audit",
]
