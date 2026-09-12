"""JETBUNDLE-STATES method cases at the C01 manifest boundary."""

from __future__ import annotations

from copy import deepcopy
from datetime import date

from ..clocks import et_ns
from ..evidence import fixture_document
from ..fixture_utils import method_case


METHOD = "JETBUNDLE-STATES"
DAY = date(2026, 1, 15)


def _t(hour: int, minute: int = 0, second: int = 0) -> int:
    return et_ns(DAY, hour, minute, second)


# Source prerequisites are capped at their current observation.  A transition
# outcome is deliberately uncapped here: score_episode's transition-specific
# binding allows next_state_at to become known at the next state itself.
STAGE_LIMITS = {
    "participation_record_complete": "participation_known_at",
    "response_record_complete": "response_known_at",
    "state": "state_at",
    "two_sided_executions": "state_at",
    "recent_revisits": "state_at",
    "low_aggression_both_sides": "state_at",
    "high_aggression": "state_at",
    "low_response_efficiency": "state_at",
    "opposite_liquidity_holds_and_refills": "state_at",
    "aggression": "state_at",
    "efficient_displacement": "state_at",
    "prior_absorption_or_effort": "state_at",
    "replenishment_stops": "state_at",
    "level_gives_way": "state_at",
    "cancellations_dominate": "state_at",
    "conditioning_known_at": "state_at",
}

_STATE_CRITERIA = {
    "B": ("two_sided_executions", "recent_revisits", "low_aggression_both_sides"),
    "A": ("high_aggression", "low_response_efficiency",
          "opposite_liquidity_holds_and_refills"),
    "D": ("aggression", "efficient_displacement"),
    "E": ("prior_absorption_or_effort", "replenishment_stops", "level_gives_way"),
    "W": ("cancellations_dominate",),
}


def _state(state: str) -> dict:
    """Construct a fully observed supplied state in the source illustration."""

    at = _t(10, 0)
    op = {
        "branch": state,
        "side": "not_applicable",
        "instrument_id": "AAPL-fixture",
        "band_id": "jetbundle-AAPL-local-1000",
        "participation_record_complete": True,
        "participation_known_at": at,
        "response_record_complete": True,
        "response_known_at": at,
        "state": state,
        "state_at": at,
        "source_symbol": "AAPL",
        "source_state_id": f"state-{state}-1000",
        "state_observation_id": f"state-observation-{state}-1000",
        "source_event_log_id": "AAPL-10-level-events-1000",
        "native_event_types": ["add", "cancel", "execute"],
        "depth_levels": 10,
        "local_interval_id": "AAPL-local-1000",
        "response_points": "0.25",
        "criteria_evidence_ids": {
            criterion: f"{criterion}-observation-{state}-1000"
            for criterion in _STATE_CRITERIA[state]
        },
        "observation_cadence": "one-minute",
        "automatic_state": None,
    }
    for criterion in _STATE_CRITERIA[state]:
        op[criterion] = True
    if state == "A":
        op.update({
            "executed_effort": "100",
            "response_points": "0.25",
            "opposite_hold_refill_id": "refill-A-1000",
        })
    elif state == "B":
        op.update({"revisit_count": 3, "two_sided_volume": True})
    elif state == "D":
        op.update({"displacement_points": "2.0"})
    elif state == "E":
        op.update({"prior_effort_id": "effort-E-0959", "level_id": "level-E-1000"})
    elif state == "W":
        op.update({"native_cancel_count": 8, "display_imbalance": True})
    return op


def _payload(candidate: dict, field: str, assertions: dict, objects: dict,
             evidence: dict) -> dict:
    binding = candidate.get("operands", {}).get(field, {})
    record = assertions.get(binding.get("assertion_id"))
    if record is None:
        record = objects.get(binding.get("object_id"), {})
    for evidence_id in record.get("evidence_ids", []):
        row = evidence.get(evidence_id)
        if row is not None:
            return row.get("payload", {})
    return {}


def audit_candidate(candidate, operands, objects, assertions, evidence) -> list[dict]:
    """Audit source-native identity and qualitative state evidence."""

    findings: list[dict] = []

    def issue(field: str, reason: str, *, kind: str = "identity",
              unknown: bool = False, recipe: str = "O165",
              affects_admission: bool = True) -> None:
        findings.append({"field": field, "kind": kind, "unknown": unknown,
                         "reason": reason, "recipe_id": recipe,
                         "affects_admission": affects_admission})

    state = operands.get("state")
    payload = _payload(candidate, "state", assertions, objects, evidence)
    source_symbol = payload.get("source_symbol")
    if state is None:
        issue("state", "supplied state label is missing",
              kind="supplied_record_missing", unknown=True, recipe="O165")
    elif state not in _STATE_CRITERIA:
        issue("state", "state label is outside the supplied B/A/D/E/W alphabet",
              recipe="O165")
    elif candidate.get("branch") != state:
        issue("state", "candidate branch must match its supplied state label",
              recipe="O165")
    elif payload.get("source_state_id") is None or payload.get("state_observation_id") is None:
        issue("state", "supplied state lacks its actual source state observation identity",
              kind="supplied_record_missing", unknown=True, recipe="O165")
    else:
        source_state_id = payload.get("source_state_id")
        if not isinstance(source_state_id, str):
            issue("state", "source state observation identity must be an opaque string",
                  recipe="O165")

    # The native AAPL ten-level process is a source boundary.  A compact NQ
    # BBO or a display imbalance cannot establish participation completeness.
    if operands.get("participation_record_complete") is True:
        native = payload.get("native_event_types") or []
        missing = []
        if payload.get("source_event_log_id") is None:
            missing.append("source_event_log_id")
        if not {"add", "cancel", "execute"} <= set(native):
            missing.append("native_event_types")
        depth = payload.get("depth_levels")
        if type(depth) is not int or depth < 10:
            missing.append("depth_levels")
        if source_symbol is None:
            missing.append("source_symbol")
        elif source_symbol != "AAPL":
            issue("participation_record_complete",
                  "NQ/BBO participation is not the source AAPL ten-level event process",
                  recipe="O163")
        if missing:
            issue("participation_record_complete",
                  "native participation process is missing: " + ", ".join(missing),
                  kind="supplied_record_missing", unknown=True, recipe="O163")

    if operands.get("response_record_complete") is True:
        response_missing = []
        if payload.get("local_interval_id") is None:
            response_missing.append("local_interval_id")
        if payload.get("response_points") is None:
            response_missing.append("response_points")
        if response_missing:
            issue("response_record_complete",
                  "same-interval response evidence is missing: " + ", ".join(response_missing),
                  kind="supplied_record_missing", unknown=True, recipe="O164")

    if state in _STATE_CRITERIA:
        criteria_ids = payload.get("criteria_evidence_ids")
        if not isinstance(criteria_ids, dict):
            criteria_ids = {}
        for criterion in _STATE_CRITERIA[state]:
            if operands.get(criterion) is True and not criteria_ids.get(criterion):
                issue(criterion, "state criterion lacks its actual supplied observation identity",
                      kind="supplied_record_missing", unknown=True, recipe="O165")

    if candidate.get("predicate") == "transition_observation":
        if payload.get("conditioning_observation_id") is None:
            # The field itself remains a nullable C01 operand; this additional
            # finding records why a supplied transition cannot claim a source
            # conditioning context.
            issue("conditioning_known_at", "transition lacks its current-state conditioning observation",
                  kind="supplied_record_missing", unknown=True, recipe="O166")
        counts = payload.get("reported_counts")
        if counts is not None and source_symbol != "AAPL":
            issue("next_state_at", "AAPL transition counts cannot be transferred to an NQ cohort",
                  recipe="O166")
        cond = operands.get("conditioning_known_at")
        current = operands.get("state_at")
        if cond is not None and current is not None and cond > current:
            issue("conditioning_known_at", "conditioning is first known after the current state",
                  kind="ordering", recipe="O166")

        # A transition is an audit over two separately observed state rows.
        # The timing operands alone are insufficient: verify both actual
        # state candidates and retain their producer trace for the caller.
        state_records = candidate.get("state_records") or {}
        current_record = state_records.get("current")
        next_record = state_records.get("next")
        if current_record is None or next_record is None:
            issue("state_records", "transition lacks separately observed current and next state records",
                  kind="supplied_record_missing", unknown=True, recipe="O166")
        else:
            from trading_research.research.method_pack.evidence import score_episode

            # Check the linked record type before dispatching it to the public
            # scorer.  A malformed link to another transition must be treated
            # as an identity failure; recursively scoring it can otherwise
            # follow the same link forever.
            linked_results = []
            for role, record in (("current", current_record), ("next", next_record)):
                if (record.get("method_id") != METHOD
                        or record.get("predicate") != "state_observation"):
                    issue("state_records", f"{role} transition record is not a state observation",
                          recipe="O165")
                    linked_results.append((role, record, None))
                    continue
                linked_results.append((role, record,
                                       score_episode(record, objects, assertions, evidence)))
            current_result = linked_results[0][2]
            next_result = linked_results[1][2]
            support = {
                "supporting_object_ids": sorted({identifier
                                                  for result in (current_result, next_result)
                                                  if result is not None
                                                  for identifier in result.get("used_object_ids", [])}),
                "supporting_assertion_ids": sorted({identifier
                                                     for result in (current_result, next_result)
                                                     if result is not None
                                                     for identifier in result.get("used_assertion_ids", [])}),
                "supporting_evidence_ids": sorted({identifier
                                                    for result in (current_result, next_result)
                                                    if result is not None
                                                    for identifier in result.get("used_evidence_ids", [])}),
                "kind": "supporting_records",
            }
            findings.append(support)
            for role, record, result in linked_results:
                if result is not None and result.get("verdict") == "fail":
                    issue("state_records", f"{role} observed state record fails its source-state audit",
                          recipe="O165")
                elif result is not None and result.get("verdict") == "unknown":
                    issue("state_records", f"{role} observed state record is incomplete",
                          kind="supplied_record_missing", unknown=True, recipe="O165")

            current_payload = _payload(current_record, "state", assertions, objects, evidence)
            next_payload = _payload(next_record, "state", assertions, objects, evidence)
            transition_identity = ("method_id", "instrument_id", "side", "band_ids",
                                   "cohort_id", "evidence_mode")
            for key in transition_identity:
                expected = candidate.get(key)
                if key == "band_ids":
                    current_value = current_record.get(key)
                    next_value = next_record.get(key)
                    if current_value != expected or next_value != expected:
                        issue("state_records", f"current/next state {key} differs from transition cohort",
                              recipe="O166")
                elif current_record.get(key) != expected or next_record.get(key) != expected:
                    issue("state_records", f"current/next state {key} differs from transition cohort",
                          recipe="O166")

            def bound_value(record: dict, field: str):
                binding = record.get("operands", {}).get(field, {})
                source = assertions.get(binding.get("assertion_id"))
                if source is None:
                    source = objects.get(binding.get("object_id"), {})
                return source.get("value", {}).get(field)

            # The transition's branch/state is its from-state.  The linked
            # next observation may be any member of the source B/A/D/E/W
            # alphabet, including an off-diagonal A->E or D->A change, but it
            # must carry its own branch/state-consistent observation.
            current_state = bound_value(current_record, "state") if current_result is not None else None
            next_state = bound_value(next_record, "state") if next_result is not None else None
            if current_record.get("branch") != candidate.get("branch"):
                issue("state_records", "current state branch differs from transition from-state",
                      recipe="O166")
            if current_state != operands.get("state"):
                issue("state_records", "current state label differs from transition from-state",
                      recipe="O166")
            if next_state not in _STATE_CRITERIA or next_record.get("branch") != next_state:
                issue("state_records", "next state must be its own valid B/A/D/E/W observation",
                      recipe="O165")
            if current_payload.get("source_symbol") != next_payload.get("source_symbol"):
                issue("state_records", "current and next state source symbols differ",
                      recipe="O166")
            target_payload = _payload(candidate, "state", assertions, objects, evidence)
            if (target_payload.get("source_symbol") != current_payload.get("source_symbol")
                    or target_payload.get("source_symbol") != next_payload.get("source_symbol")):
                issue("state_records", "state records do not share the transition source symbol",
                      recipe="O166")
            if (current_payload.get("observation_cadence") != next_payload.get("observation_cadence")
                    or target_payload.get("observation_cadence") not in {
                        None, current_payload.get("observation_cadence")
                    }):
                issue("state_records", "state records do not share the declared observation cadence",
                      recipe="O166")

            expected_current = operands.get("state_at")
            expected_next = operands.get("next_state_at")
            actual_current = bound_value(current_record, "state_at")
            actual_next = bound_value(next_record, "state_at")
            if actual_current != expected_current:
                issue("state_at", "current state record time does not match transition state_at",
                      recipe="O166")
            if actual_next != expected_next:
                issue("next_state_at", "next state record time does not match transition next_state_at",
                      recipe="O166")

            cadence = payload.get("cadence_seconds")
            adjacency_id = payload.get("adjacency_observation_id")

            def _source_ids(source_payload: dict) -> set[str]:
                identifiers = set()
                for key in ("source_state_id", "state_observation_id", "observation_id", "state_id"):
                    value = source_payload.get(key)
                    if isinstance(value, str) and value:
                        identifiers.add(value)
                return identifiers

            def _linked_previous_id(source_payload: dict) -> str | None:
                for key in ("previous_state_id", "prior_state_id",
                            "previous_state_observation_id", "prior_state_observation_id",
                            "previous_observation_id", "prior_observation_id",
                            "linked_previous_state_id"):
                    value = source_payload.get(key)
                    if isinstance(value, str) and value:
                        return value
                return None

            def _explicitly_clear(payloads: tuple[dict, ...], false_names: tuple[str, ...],
                                  true_names: tuple[str, ...]) -> bool:
                found = False
                for payload_row in payloads:
                    for name in false_names:
                        if name in payload_row:
                            found = True
                            if payload_row[name] is not False:
                                return False
                    for name in true_names:
                        if name in payload_row:
                            found = True
                            if payload_row[name] is not True:
                                return False
                return found

            def _cadence_marker(source_payload: dict):
                value = source_payload.get("observation_cadence")
                if value is None:
                    value = source_payload.get("cadence_seconds")
                return value

            # An exact source linkage can establish adjacency even when the
            # event stream is not uniformly spaced.  It must name the prior
            # current observation, retain the same observation cadence, carry
            # the same transition cohort (checked above), explicitly witness
            # no gap and no reset, and cite an adjacency observation.
            source_payloads = (payload, current_payload, next_payload)
            current_source_ids = _source_ids(current_payload)
            next_source_ids = _source_ids(next_payload)
            linked_previous = _linked_previous_id(next_payload)
            target_current_id = next((payload.get(key) for key in
                                      ("current_state_id", "previous_state_id",
                                       "current_state_observation_id")
                                      if isinstance(payload.get(key), str)
                                      and payload.get(key)), None)
            target_next_id = next((payload.get(key) for key in
                                   ("next_state_id", "next_state_observation_id")
                                   if isinstance(payload.get(key), str)
                                   and payload.get(key)), None)
            exact_source_link = (
                isinstance(adjacency_id, str) and bool(adjacency_id)
                and current_source_ids and next_source_ids
                and (linked_previous in current_source_ids
                     or (target_current_id in current_source_ids
                         and target_next_id in next_source_ids))
                and _cadence_marker(current_payload) is not None
                and _cadence_marker(current_payload) == _cadence_marker(next_payload)
                and _explicitly_clear(
                    source_payloads,
                    ("gap", "has_gap", "gap_detected", "data_gap",
                     "observation_gap", "sequence_gap", "gap_or_reset"),
                    ("no_gap", "gap_free"),
                )
                and _explicitly_clear(
                    source_payloads,
                    ("reset", "has_reset", "reset_detected", "session_reset",
                     "sequence_reset", "state_reset", "gap_or_reset"),
                    ("no_reset", "reset_free"),
                )
            )
            if adjacency_id is None:
                issue("next_state_at", "transition lacks its declared adjacency observation",
                      kind="supplied_record_missing", unknown=True, recipe="O166")
            elif not isinstance(adjacency_id, str) or not adjacency_id:
                issue("next_state_at", "transition adjacency observation identity is not an opaque string",
                      recipe="O166")
            elif cadence is not None and (type(cadence) is not int or cadence <= 0):
                issue("next_state_at", "transition cadence is not an exact positive integer",
                      recipe="O166")
            elif expected_current is not None and expected_next is not None and expected_next > expected_current:
                uniform_cadence = (type(cadence) is int and cadence > 0
                                   and expected_next - expected_current == cadence * 1_000_000_000)
                if not uniform_cadence and not exact_source_link:
                    issue("next_state_at", "current and next state observations lack a proven adjacency link",
                          kind="supplied_record_missing", unknown=True, recipe="O166")
            elif not exact_source_link and cadence is None:
                issue("next_state_at", "transition lacks its declared cadence/adjacency proof",
                      kind="supplied_record_missing", unknown=True, recipe="O166")

    return findings


def _document(fid: str, op: dict, predicate: str = "state_observation") -> dict:
    return fixture_document(METHOD, predicate, fid, op)


def _transition_document(fid: str, op: dict) -> dict:
    """Build a transition plus two separately typed state observations."""

    document = _document(fid, op, "transition_observation")
    target = document["candidates"][0]
    current_id = f"{fid}:current-state"
    next_id = f"{fid}:next-state"

    def state_record(label: str, at: int, opaque_id: str) -> dict:
        state = _state(label)
        state.update({
            "instrument_id": op.get("instrument_id", state["instrument_id"]),
            "band_id": op.get("band_id", state["band_id"]),
            "source_symbol": op.get("source_symbol", state["source_symbol"]),
            "state_at": at,
            "participation_known_at": at,
            "response_known_at": at,
            "known_at": at,
            "source_state_id": opaque_id,
            "state_observation_id": f"observation-{opaque_id}",
            "criteria_known_at": {
                criterion: at for criterion in _STATE_CRITERIA[label]
            },
        })
        return state

    state_at = op.get("state_at")
    next_state_at = op.get("next_state_at")
    current = state_record(op.get("state", "A"), state_at, "opaque-current-state")
    next_state = state_record(op.get("next_state", op.get("state", "A")),
                              next_state_at, "opaque-next-state")
    current_doc = _document(current_id, current)
    next_doc = _document(next_id, next_state)
    document["candidates"].extend(current_doc["candidates"])
    document["candidates"].extend(next_doc["candidates"])
    document["objects"].extend(current_doc["objects"])
    document["objects"].extend(next_doc["objects"])
    document["assertions"].extend(current_doc["assertions"])
    document["assertions"].extend(next_doc["assertions"])
    document["evidence"].extend(current_doc["evidence"])
    document["evidence"].extend(next_doc["evidence"])
    target["current_state_candidate_id"] = current_id
    target["next_state_candidate_id"] = next_id
    return document


def _manifest_mutation_cases() -> list[dict]:
    """C08 rows mutate actual C01 objects/evidence, then bind and score them."""

    source = _document("M10-F1", _state("A"))

    def case(suffix: str, mutate, expected: str, kind: str, predicate: str = "state_observation") -> dict:
        document = deepcopy(source)
        fid = f"M10-F1:{suffix}"
        candidate = document["candidates"][0]
        candidate["candidate_id"] = fid
        for assertion in document["assertions"]:
            assertion["candidate_id"] = fid
        mutate(document)
        return method_case(METHOD, predicate, fid, document, expected, kind=kind)

    def late_participation(document: dict) -> None:
        late = _state("A")["state_at"] + 1
        obj = next(row for row in document["objects"]
                   if row["object_id"].endswith(":participation_known_at"))
        obj.update({"known_at": late, "as_of": late,
                    "formation_start": late, "formation_end": late})
        for evidence_row in document["evidence"]:
            if evidence_row["evidence_id"] in obj["evidence_ids"]:
                evidence_row.update({"known_at": late,
                                     "observation_start": late,
                                     "observation_end": late})

    def foreign_state(document: dict) -> None:
        obj = next(row for row in document["objects"]
                   if row["object_id"].endswith(":state"))
        obj["band_id"] = "foreign-state-band"
        for evidence_row in document["evidence"]:
            if evidence_row["evidence_id"] in obj["evidence_ids"]:
                evidence_row["band_id"] = "foreign-state-band"

    def missing_participation(document: dict) -> None:
        document["candidates"][0]["operands"].pop("participation_record_complete")

    return [
        case("c08-late", late_participation, "fail", "c08_late"),
        case("c08-identity", foreign_state, "fail", "c08_identity"),
        case("c08-missing", missing_participation, "unknown", "c08_missing"),
    ]


def method_fixtures() -> list[dict]:
    rows = []
    for state in ("B", "A", "D", "E", "W"):
        fid = "M10-F1" if state == "A" else f"M10-F1-{state}"
        rows.append(method_case(METHOD, "state_observation", fid,
                                _document(fid, _state(state)), "pass"))

    transition = _state("A")
    transition.update({
        "next_state_at": _t(10, 1),
        "conditioning_known_at": _t(9, 59),
        "next_state_id": "state-A-1001",
        "conditioning_observation_id": "conditioning-A-0959",
        "adjacency_observation_id": "adjacent-state-observation-A-1000-1001",
        "cadence_seconds": 60,
    })
    rows.append(method_case(METHOD, "transition_observation", "M10-F1-transition",
                            _transition_document("M10-F1-transition", transition), "pass"))

    # The next state is a separately audited target and may be a legitimate
    # off-diagonal transition.  Keep an A->E fixture so a branch identity
    # check cannot silently turn the transition table into persistence only.
    transition_ae = deepcopy(transition)
    transition_ae.update({"next_state": "E", "next_state_id": "state-E-1001"})
    rows.append(method_case(METHOD, "transition_observation", "M10-F1-transition-AE",
                            _transition_document("M10-F1-transition-AE", transition_ae), "pass"))

    no_cancel = _state("W")
    no_cancel.update({"cancellations_dominate": None, "display_imbalance": True})
    rows.append(method_case(METHOD, "state_observation", "M10-F2-W-no-cancels",
                            _document("M10-F2-W-no-cancels", no_cancel), "unknown",
                            kind="negative"))

    late_conditioning = deepcopy(transition)
    late_conditioning["conditioning_known_at"] = _t(10, 0, 30)
    rows.append(method_case(METHOD, "transition_observation", "M10-F2-conditioning",
                            _transition_document("M10-F2-conditioning", late_conditioning),
                            "fail", kind="negative"))

    tied = deepcopy(transition)
    tied["next_state_at"] = tied["state_at"]
    tied["next_state_id"] = "state-A-tied"
    rows.append(method_case(METHOD, "transition_observation", "M10-F2-tied-order",
                            _transition_document("M10-F2-tied-order", tied),
                            "unknown", kind="negative"))

    nq_counts = deepcopy(transition)
    nq_counts.update({
        "instrument_id": "NQ-fixture",
        "source_symbol": "NQ",
        "reported_counts": {"D": 84, "A": 12, "B": 4, "E": 0, "W": 0},
    })
    rows.append(method_case(METHOD, "transition_observation", "M10-F2-nq-counts",
                            _transition_document("M10-F2-nq-counts", nq_counts),
                            "fail", kind="negative"))

    depth_hole = _state("A")
    depth_hole.update({"participation_record_complete": None, "depth_levels": 2})
    rows.append(method_case(METHOD, "state_observation", "M10-F3-depth",
                            _document("M10-F3-depth", depth_hole), "unknown", kind="hole"))

    rows.extend(_manifest_mutation_cases())
    return rows


__all__ = ["STAGE_LIMITS", "audit_candidate", "method_fixtures"]
