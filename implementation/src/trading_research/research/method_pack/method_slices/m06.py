"""M06 SAINT-AMT acceptance cases at the C01 production boundary."""

from __future__ import annotations

from copy import deepcopy
from datetime import date

from ..clocks import et_ns
from ..evidence import fixture_document
from ..fixture_utils import method_case


DAY = date(2026, 1, 15)


def _t(hour: int, minute: int) -> int:
    return et_ns(DAY, hour, minute)


STAGE_LIMITS = {
    "balance_fixed_before_use": "balance_known_at",
    "profile_allows_trade": "balance_known_at",
    "arrival_read_recorded": "arrival_at",
    "control_evidence_recorded": "control_at",
    "alignment_ok": "control_at",
    "risk_defined": "decision_at",
    "objective_fixed": "decision_at",
    "ltf_balance_broken": "breakout_at",
    "same_boundary_retest_held": "retest_at",
    "repeated_aggression_in_trade_direction": "confirm_at",
    "prior_buying_at_upper_extreme": "prior_failures_known_at",
    "two_distinct_prior_failures": "prior_failures_known_at",
    "ltf_break_down": "breakout_at",
    "repeated_body_selling": "confirm_at",
    "older_value_tested": "older_value_touch_at",
    "older_value_rejected": "rejection_at",
    "original_balance_reaccepted": "reaccept_at",
    "local_control_confirms_return": "control_at",
    "aggressive_poc_passage": "poc_passage_at",
    "source_poc_hold_confirmed": "poc_passage_at",
    "target_is_far_balance_edge": "decision_at",
}


def _common(branch: str, *, side: str) -> dict:
    return {
        "branch": branch,
        "side": side,
        "instrument_id": "ES-fixture",
        "band_id": "SAINT-HTF-100-110",
        "balance_fixed_before_use": True,
        "profile_allows_trade": True,
        "arrival_read_recorded": True,
        "control_evidence_recorded": True,
        "alignment_ok": True,
        "risk_defined": True,
        "objective_fixed": True,
        "balance_known_at": _t(8, 0),
        "arrival_at": _t(9, 40),
        "control_at": _t(9, 52),
        "decision_at": _t(9, 53),
        # Auditable source relationships retained in every evidence payload.
        "htf_control_side": side,
        "ltf_control_side": side,
        "control_state": "directional",
        "source_value_fraction": "0.68",
    }


def _continuation() -> dict:
    op = _common("continuation_retest", side="long")
    op.update({
        "ltf_balance_broken": True,
        "ltf_balance_known_at": _t(9, 30),
        "breakout_at": _t(9, 45),
        "same_boundary_retest_held": True,
        "repeated_aggression_in_trade_direction": True,
        "retest_at": _t(9, 50),
        "confirm_at": _t(9, 52),
        "breakout_band_id": op["band_id"],
        "retest_band_id": op["band_id"],
        "retest_observed": True,
    })
    return op


def _trapped() -> dict:
    op = _common("trapped_buyers_retest", side="short")
    op.update({
        "prior_buying_at_upper_extreme": True,
        "two_distinct_prior_failures": True,
        "prior_failures_known_at": _t(8, 0),
        "ltf_break_down": True,
        "same_boundary_retest_held": True,
        "repeated_body_selling": True,
        "breakout_at": _t(9, 45),
        "retest_at": _t(9, 50),
        "confirm_at": _t(9, 52),
        "prior_failures": [
            {"failure_id": "prior-AM", "resolved_at": _t(7, 0), "band_id": op["band_id"]},
            {"failure_id": "prior-PM", "resolved_at": _t(7, 30), "band_id": op["band_id"]},
        ],
        "breakout_band_id": op["band_id"],
        "retest_band_id": op["band_id"],
        "retest_observed": True,
        "upper_extreme": "110",
    })
    return op


def _failed_auction() -> dict:
    op = _common("failed_auction_return", side="long")
    op.update({
        "older_value_tested": True,
        "older_value_rejected": True,
        "older_value_known_at": _t(9, 20),
        "older_value_touch_at": _t(9, 40),
        "rejection_at": _t(9, 45),
        "original_balance_reaccepted": True,
        "reaccept_at": _t(9, 50),
        "local_control_confirms_return": True,
        "control_at": _t(9, 52),
        "original_balance_id": op["band_id"],
        "tested_value_id": "SAINT-older-value-90-98",
    })
    return op


def _poc() -> dict:
    op = _common("poc_traversal", side="long")
    op.update({
        "original_balance_reaccepted": True,
        "reaccept_at": _t(9, 48),
        "aggressive_poc_passage": True,
        "source_poc_hold_confirmed": True,
        "target_is_far_balance_edge": True,
        "poc_passage_at": _t(9, 51),
        "control_at": _t(9, 52),
        "original_balance_id": op["band_id"],
        "poc_profile_id": op["band_id"],
    })
    return op


def _document(fid: str, op: dict) -> dict:
    return fixture_document("SAINT-AMT", "sequence", fid, op)


def _assertion(doc: dict, fid: str, field: str) -> dict:
    return next(row for row in doc["assertions"]
                if row["candidate_id"] == fid and row["field"] == field)


def _payload_for(candidate: dict, field: str, assertions: dict, evidence: dict) -> dict:
    binding = candidate["operands"].get(field, {})
    assertion = assertions.get(binding.get("assertion_id"), {})
    for eid in assertion.get("evidence_ids", []):
        record = evidence.get(eid)
        if record:
            return record.get("payload", {})
    return {}


def audit_candidate(candidate, operands, objects, assertions, evidence) -> list[dict]:
    """Validate source relationships that a nullable Boolean cannot prove."""
    findings: list[dict] = []
    payload = _payload_for(candidate, "alignment_ok", assertions, evidence)
    if operands.get("alignment_ok") is True:
        if (payload.get("htf_control_side") != candidate["side"]
                or payload.get("ltf_control_side") != candidate["side"]):
            findings.append({"field": "alignment_ok", "kind": "identity",
                             "reason": "actual HTF and current LTF control do not match the decision side",
                             "recipe_id": "O097"})
        if payload.get("control_state") == "free_two_sided":
            findings.append({"field": "control_evidence_recorded", "kind": "identity",
                             "reason": "free two-sided chop is not present directional control",
                             "recipe_id": "O097"})
        if payload.get("source_value_fraction") in {"0.70", "0.40"}:
            findings.append({"field": "profile_allows_trade", "kind": "identity",
                             "reason": "foreign value convention substituted for Saint's source profile",
                             "recipe_id": "O062"})

    if operands.get("two_distinct_prior_failures") is True:
        payload = _payload_for(candidate, "two_distinct_prior_failures", assertions, evidence)
        failures = payload.get("prior_failures") or []
        identities = {(row.get("failure_id"), row.get("resolved_at")) for row in failures}
        cutoff = operands.get("prior_failures_known_at")
        valid = (len(failures) >= 2 and len(identities) == len(failures)
                 and all(row.get("band_id") in candidate["band_ids"] for row in failures)
                 and cutoff is not None
                 and all(row.get("resolved_at") is not None and row["resolved_at"] <= cutoff
                         for row in failures))
        if not valid:
            findings.append({"field": "two_distinct_prior_failures", "kind": "identity",
                             "reason": "prior failures are not distinct resolved episodes at the same HTF band",
                             "recipe_id": "O119"})

    if operands.get("same_boundary_retest_held") is True:
        payload = _payload_for(candidate, "same_boundary_retest_held", assertions, evidence)
        if not (payload.get("breakout_band_id") == payload.get("retest_band_id")
                and payload.get("retest_band_id") in candidate["band_ids"]):
            findings.append({"field": "same_boundary_retest_held", "kind": "identity",
                             "reason": "breakout and retest do not use the actual same boundary",
                             "recipe_id": "O091"})
        if payload.get("retest_observed") is not True:
            findings.append({"field": "same_boundary_retest_held", "kind": "identity",
                             "reason": "chased attempt has no observed current boundary retest",
                             "recipe_id": "O091"})
        binding = candidate["operands"].get("same_boundary_retest_held", {})
        record = assertions.get(binding.get("assertion_id"), {})
        if (operands.get("retest_at") is not None and record.get("observation_end") is not None
                and record["observation_end"] < operands["retest_at"]):
            findings.append({"field": "same_boundary_retest_held", "kind": "ordering",
                             "reason": "retest claim reuses evidence observed before the current retest",
                             "recipe_id": "O091"})

    if candidate["branch"] == "failed_auction_return":
        payload = _payload_for(candidate, "original_balance_reaccepted", assertions, evidence)
        if (payload.get("original_balance_id") not in candidate["band_ids"]
                or payload.get("tested_value_id") in candidate["band_ids"]
                or payload.get("tested_value_id") is None):
            findings.append({"field": "original_balance_reaccepted", "kind": "identity",
                             "reason": "failed-auction route does not preserve distinct tested and original value identities",
                             "recipe_id": "O094"})
        if (operands.get("reaccept_at") is not None and operands.get("control_at") is not None
                and operands["control_at"] < operands["reaccept_at"]):
            findings.append({"field": "local_control_confirms_return", "kind": "ordering",
                             "reason": "current control observation predates original-balance reacceptance",
                             "recipe_id": "O094"})

    if candidate["branch"] == "poc_traversal":
        payload = _payload_for(candidate, "aggressive_poc_passage", assertions, evidence)
        if (payload.get("original_balance_id") not in candidate["band_ids"]
                or payload.get("poc_profile_id") not in candidate["band_ids"]):
            findings.append({"field": "aggressive_poc_passage", "kind": "identity",
                             "reason": "POC passage is not bound to the reaccepted original profile",
                             "recipe_id": "O095"})
        if (operands.get("poc_passage_at") is not None and operands.get("control_at") is not None
                and operands["control_at"] < operands["poc_passage_at"]):
            findings.append({"field": "source_poc_hold_confirmed", "kind": "ordering",
                             "reason": "source POC hold/control predates the current passage",
                             "recipe_id": "O095"})
    return findings


def _late_control(fid: str) -> dict:
    doc = _document(fid, _trapped())
    assertion = _assertion(doc, fid, "control_evidence_recorded")
    late = _t(9, 54)
    assertion.update(observation_start=late, observation_end=late, known_at=late)
    for eid in assertion["evidence_ids"]:
        next(row for row in doc["evidence"] if row["evidence_id"] == eid).update(
            observation_start=late, observation_end=late, known_at=late)
    return doc


def _missing_control(fid: str) -> dict:
    doc = _document(fid, _trapped())
    del doc["candidates"][0]["operands"]["control_evidence_recorded"]
    return doc


def _identity_retest(fid: str) -> dict:
    doc = _document(fid, _trapped())
    assertion = _assertion(doc, fid, "same_boundary_retest_held")
    assertion["band_id"] = "foreign-band"
    for eid in assertion["evidence_ids"]:
        next(row for row in doc["evidence"] if row["evidence_id"] == eid)["band_id"] = "foreign-band"
    return doc


def method_fixtures() -> list[dict]:
    rows: list[dict] = []
    for fid, op in (
        ("M06-F1", _trapped()),
        ("M06-F1-continuation", _continuation()),
        ("M06-F1-failed-auction", _failed_auction()),
        ("M06-F1-poc", _poc()),
    ):
        rows.append(method_case("SAINT-AMT", "sequence", fid, _document(fid, op), "pass"))

    duplicate = _trapped()
    duplicate["prior_failures"][1] = deepcopy(duplicate["prior_failures"][0])
    rows.append(method_case("SAINT-AMT", "sequence", "M06-F2-duplicate-failure",
                            _document("M06-F2-duplicate-failure", duplicate), "fail"))
    chop = _trapped()
    chop["control_state"] = "free_two_sided"
    rows.append(method_case("SAINT-AMT", "sequence", "M06-F2-free-chop",
                            _document("M06-F2-free-chop", chop), "fail"))
    chased = _continuation()
    chased["retest_observed"] = False
    rows.append(method_case("SAINT-AMT", "sequence", "M06-F2-no-retest",
                            _document("M06-F2-no-retest", chased), "fail"))

    current = _trapped()
    current.update(control_evidence_recorded=None, alignment_ok=None,
                   ltf_control_side=None, control_state=None)
    rows.append(method_case("SAINT-AMT", "sequence", "M06-F3-current-control",
                            _document("M06-F3-current-control", current), "unknown"))
    profile = _trapped()
    profile.update(profile_allows_trade=None, source_value_fraction=None)
    rows.append(method_case("SAINT-AMT", "sequence", "M06-F3-profile-selection",
                            _document("M06-F3-profile-selection", profile), "unknown"))
    hold = _continuation()
    hold.update(same_boundary_retest_held=None, retest_observed=None)
    rows.append(method_case("SAINT-AMT", "sequence", "M06-F3-hold-procedure",
                            _document("M06-F3-hold-procedure", hold), "unknown"))

    rows.append(method_case("SAINT-AMT", "sequence", "M06-F1:late",
                            _late_control("M06-F1:late"), "fail", kind="c08_late"))
    rows.append(method_case("SAINT-AMT", "sequence", "M06-F1:missing",
                            _missing_control("M06-F1:missing"), "unknown", kind="c08_missing"))
    rows.append(method_case("SAINT-AMT", "sequence", "M06-F1:identity",
                            _identity_retest("M06-F1:identity"), "fail", kind="c08_identity"))
    return rows


def semantic_audit() -> dict:
    rows = method_fixtures()
    return {
        "fixture_count": len(rows),
        "all_pass": all(row["status"] == "pass" for row in rows),
        "branches": sorted({row["actual_value"]["branch"] for row in rows
                            if row["id"].startswith("M06-F1-") or row["id"] == "M06-F1"}),
    }
