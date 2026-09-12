"""M11 STOIC-DATA process and macro-application acceptance cases."""

from __future__ import annotations

from copy import deepcopy
from datetime import date

from ..clocks import et_ns
from ..evidence import fixture_document
from ..fixture_utils import method_case


def _at(day: date, hour: int = 9, minute: int = 0) -> int:
    return et_ns(day, hour, minute)


JAN1 = date(2026, 1, 1)
JAN2 = date(2026, 1, 2)
JAN31 = date(2026, 1, 31)
FEB1 = date(2026, 2, 1)
FEB2 = date(2026, 2, 2)
MAR1 = date(2026, 3, 1)


STAGE_LIMITS = {
    "process_spec_frozen": "spec_known_at",
    "inclusion_rule_fixed": "inclusion_frozen_at",
    "uniform_schema": "spec_known_at",
    "all_eligible_observations_retained": "comparison_at",
    "features_available_before_decisions": "sample_end_at",
    "outcomes_separated_from_inputs": "comparison_at",
    "aggregate_winner_loser_comparison_recorded": "comparison_at",
    "revision_uses_only_prior_sample": "revision_at",
    "release_vintages_recorded": "macro_decision_at",
    "historical_comparison_defined": "macro_decision_at",
    "cycle_and_indicator_rules_recorded": "macro_decision_at",
}


def _records() -> list[dict]:
    records = []
    for number in range(1, 101):
        decision = _at(JAN2, 9, 0) + number * 60_000_000_000
        records.append({
            "observation_id": f"obs-{number:03d}",
            "schema_version": "stoic-process-v1",
            "feature_known_at": decision - 1_000_000_000,
            "decision_at": decision,
            "outcome_at": decision + 1_000_000_000,
            "outcome": "winner" if number <= 80 else "loser",
            "input_record_id": f"input-{number:03d}",
            "outcome_record_id": f"outcome-{number:03d}",
        })
    return records


def _process(*, branch: str = "process_review") -> dict:
    records = _records()
    eligible = [row["observation_id"] for row in records]
    return {
        "branch": branch,
        "side": "not_applicable",
        "instrument_id": "STOIC-process-fixture",
        "band_id": "stoic-process-v1",
        "decision_at": _at(FEB2, 9, 0),
        "process_spec_frozen": True,
        "spec_known_at": _at(JAN1, 9, 0),
        "sample_start_at": _at(JAN2, 9, 0),
        "inclusion_rule_fixed": True,
        "uniform_schema": True,
        "all_eligible_observations_retained": True,
        "features_available_before_decisions": True,
        "outcomes_separated_from_inputs": True,
        "aggregate_winner_loser_comparison_recorded": True,
        "revision_uses_only_prior_sample": True,
        # Actual cohort and process records included in every evidence payload.
        "process_version": "stoic-process-v1",
        "inclusion_rule_id": "stoic-january-all-eligible-v1",
        "inclusion_frozen_at": _at(JAN1, 9, 0),
        "sample_end_at": _at(JAN31, 16, 0),
        "eligible_ids": eligible,
        "retained_ids": list(eligible),
        "sample_records": records,
        "comparison_at": _at(FEB1, 9, 0),
        "comparison_groups": {"winner": 80, "loser": 20},
        "comparison_metric_definition": "supplied-aggregate-feature-comparison-v1",
        "revision_at": _at(FEB2, 9, 0),
        "revision_version": "stoic-process-v2",
        "revision_input_ids": list(eligible),
        "trading_sequence_created": False,
        "pnl_computed": False,
        "model_trained": False,
    }


def _macro() -> dict:
    op = _process(branch="macro_application")
    op.update({
        "release_vintages_recorded": True,
        "historical_comparison_defined": True,
        "cycle_and_indicator_rules_recorded": True,
        "macro_decision_at": _at(date(2026, 1, 15), 9, 0),
        "vintage_records": [
            {"series_id": "credit", "period": "2025-12", "released_at": _at(date(2026, 1, 10)),
             "used_available_at": _at(date(2026, 1, 10)), "value": "1.5",
             "revised_at": _at(MAR1), "revised_value": "2.0"},
            {"series_id": "housing", "period": "2025-12", "released_at": _at(date(2026, 1, 11)),
             "used_available_at": _at(date(2026, 1, 11)), "value": "3.0"},
        ],
        "historical_baseline_id": "stoic-history-v1",
        "historical_baseline_known_at": _at(date(2026, 1, 12)),
        "cycle_rule_id": "supplied-stoic-cycle-v1",
        "indicator_rule_ids": ["credit-rule-v1", "housing-rule-v1"],
        "custom_metric_kind": "c_score",
        "c_score": "2.4",
        "z_score": "1.2",
        "substituted_metric": None,
        "automatic_current_verdict": None,
    })
    return op


def _document(fid: str, predicate: str, op: dict) -> dict:
    return fixture_document("STOIC-DATA", predicate, fid, op)


def _payload(candidate: dict, field: str, assertions: dict, evidence: dict) -> dict:
    binding = candidate["operands"].get(field, {})
    record = assertions.get(binding.get("assertion_id"), {})
    for eid in record.get("evidence_ids", []):
        if eid in evidence:
            return evidence[eid].get("payload", {})
    return {}


def audit_candidate(candidate, operands, objects, assertions, evidence) -> list[dict]:
    """Audit actual process rows, vintages and metric identities."""
    findings: list[dict] = []
    payload = _payload(candidate, "process_spec_frozen", assertions, evidence)
    records = payload.get("sample_records") or []
    eligible = payload.get("eligible_ids") or []
    retained = payload.get("retained_ids") or []
    expected_ids = {f"obs-{number:03d}" for number in range(1, 101)}
    actual_ids = {row.get("observation_id") for row in records}
    if operands.get("process_spec_frozen") is True:
        if (payload.get("process_version") != "stoic-process-v1"
                or operands.get("spec_known_at") != _at(JAN1, 9, 0)
                or operands.get("sample_start_at") != _at(JAN2, 9, 0)):
            findings.append({"field": "process_spec_frozen", "kind": "identity",
                             "reason": "process v1 was not actually frozen January 1 before the January block",
                             "recipe_id": "O137"})
    if operands.get("inclusion_rule_fixed") is True:
        frozen = payload.get("inclusion_frozen_at")
        if frozen is None or operands.get("sample_start_at") is None or frozen >= operands["sample_start_at"]:
            findings.append({"field": "inclusion_rule_fixed", "kind": "ordering",
                             "reason": "inclusion rule was frozen after the sample began or after outcomes",
                             "recipe_id": "O148"})
    if operands.get("all_eligible_observations_retained") is True:
        if set(eligible) != expected_ids or set(retained) != expected_ids or actual_ids != expected_ids:
            findings.append({"field": "all_eligible_observations_retained", "kind": "identity",
                             "reason": "actual ID coverage does not retain all 100 eligible observations",
                             "recipe_id": "O148"})
    if operands.get("uniform_schema") is True:
        if not records or {row.get("schema_version") for row in records} != {"stoic-process-v1"}:
            findings.append({"field": "uniform_schema", "kind": "identity",
                             "reason": "January observations do not share the frozen v1 schema",
                             "recipe_id": "O148"})
    if operands.get("features_available_before_decisions") is True:
        if not records or any(row.get("feature_known_at") is None or row.get("decision_at") is None
                              or row["feature_known_at"] > row["decision_at"] for row in records):
            findings.append({"field": "features_available_before_decisions", "kind": "ordering",
                             "reason": "an actual feature was first available after its decision",
                             "recipe_id": "O146"})
    if operands.get("outcomes_separated_from_inputs") is True:
        if not records or any(row.get("input_record_id") == row.get("outcome_record_id")
                              or row.get("outcome_at") is None or row.get("decision_at") is None
                              or row["outcome_at"] <= row["decision_at"] for row in records):
            findings.append({"field": "outcomes_separated_from_inputs", "kind": "identity",
                             "reason": "outcomes are not separate post-decision records",
                             "recipe_id": "O146"})
    if operands.get("aggregate_winner_loser_comparison_recorded") is True:
        groups = payload.get("comparison_groups") or {}
        actual_groups = {
            "winner": sum(row.get("outcome") == "winner" for row in records),
            "loser": sum(row.get("outcome") == "loser" for row in records),
        }
        if (groups != actual_groups or not payload.get("comparison_metric_definition")
                or payload.get("comparison_at") != _at(FEB1, 9, 0)):
            findings.append({"field": "aggregate_winner_loser_comparison_recorded", "kind": "identity",
                             "reason": "February 1 comparison does not reconcile its actual winner/loser groups",
                             "recipe_id": "O153"})
    if operands.get("revision_uses_only_prior_sample") is True:
        last_outcome = max((row.get("outcome_at") for row in records if row.get("outcome_at") is not None), default=None)
        comparison = payload.get("comparison_at")
        revision = payload.get("revision_at")
        valid = (last_outcome is not None and comparison is not None and revision is not None
                 and last_outcome < comparison < revision
                 and revision == _at(FEB2, 9, 0)
                 and payload.get("revision_version") == "stoic-process-v2"
                 and set(payload.get("revision_input_ids") or []) == actual_ids)
        if not valid:
            findings.append({"field": "revision_uses_only_prior_sample", "kind": "ordering",
                             "reason": "v2 revision does not use only the completed January block after comparison",
                             "recipe_id": "O137"})
    if any(payload.get(key) is not False for key in
           ("trading_sequence_created", "pnl_computed", "model_trained")):
        findings.append({"field": "process_spec_frozen", "kind": "identity",
                         "reason": "process audit invented a trading sequence, P&L, or trained model",
                         "recipe_id": "O137"})

    if candidate["predicate"] == "macro_application":
        macro_at = payload.get("macro_decision_at")
        if operands.get("release_vintages_recorded") is True:
            vintages = payload.get("vintage_records") or []
            valid = (vintages and macro_at is not None
                     and all(row.get("released_at") is not None and row.get("used_available_at") is not None
                             and row["released_at"] <= row["used_available_at"] <= macro_at
                             for row in vintages))
            if not valid:
                findings.append({"field": "release_vintages_recorded", "kind": "ordering",
                                 "reason": "a March revision or unavailable vintage was used for the January decision",
                                 "recipe_id": "O162"})
        if operands.get("historical_comparison_defined") is True:
            if (not payload.get("historical_baseline_id")
                    or payload.get("historical_baseline_known_at") is None
                    or payload["historical_baseline_known_at"] > macro_at):
                findings.append({"field": "historical_comparison_defined", "kind": "ordering",
                                 "reason": "historical comparison was unavailable at the macro decision",
                                 "recipe_id": "O160"})
        if operands.get("cycle_and_indicator_rules_recorded") is True:
            valid = (payload.get("cycle_rule_id") and payload.get("indicator_rule_ids")
                     and payload.get("custom_metric_kind") == "c_score"
                     and payload.get("c_score") is not None
                     and payload.get("substituted_metric") != "z_score")
            if not valid:
                findings.append({"field": "cycle_and_indicator_rules_recorded", "kind": "identity",
                                 "reason": "custom C-score/cycle rules are missing or replaced by z-score",
                                 "recipe_id": "O159"})
    return findings


def _late(fid: str) -> dict:
    doc = _document(fid, "process", _process())
    binding = doc["candidates"][0]["operands"]["process_spec_frozen"]
    assertion = next(row for row in doc["assertions"] if row["assertion_id"] == binding["assertion_id"])
    late = _at(JAN2, 10, 0)
    assertion.update(observation_start=late, observation_end=late, known_at=late)
    for eid in assertion["evidence_ids"]:
        next(row for row in doc["evidence"] if row["evidence_id"] == eid).update(
            observation_start=late, observation_end=late, known_at=late)
    return doc


def _missing(fid: str) -> dict:
    doc = _document(fid, "process", _process())
    del doc["candidates"][0]["operands"]["uniform_schema"]
    return doc


def _identity(fid: str) -> dict:
    doc = _document(fid, "process", _process())
    binding = doc["candidates"][0]["operands"]["all_eligible_observations_retained"]
    assertion = next(row for row in doc["assertions"] if row["assertion_id"] == binding["assertion_id"])
    assertion["band_id"] = "foreign-process"
    for eid in assertion["evidence_ids"]:
        next(row for row in doc["evidence"] if row["evidence_id"] == eid)["band_id"] = "foreign-process"
    return doc


def method_fixtures() -> list[dict]:
    rows = [
        method_case("STOIC-DATA", "process", "M11-F1",
                    _document("M11-F1", "process", _process()), "pass"),
        method_case("STOIC-DATA", "macro_application", "M11-F1-macro",
                    _document("M11-F1-macro", "macro_application", _macro()),
                    "pass", kind="macro_application"),
    ]
    dropped = _process()
    dropped["retained_ids"] = dropped["retained_ids"][:80]
    dropped["sample_records"] = dropped["sample_records"][:80]
    rows.append(method_case("STOIC-DATA", "process", "M11-F2-drop-losers",
                            _document("M11-F2-drop-losers", "process", dropped), "fail"))
    late_inclusion = _process()
    late_inclusion["inclusion_frozen_at"] = _at(FEB1, 10, 0)
    rows.append(method_case("STOIC-DATA", "process", "M11-F2-late-inclusion",
                            _document("M11-F2-late-inclusion", "process", late_inclusion), "fail"))
    march = _macro()
    march["vintage_records"][0]["used_available_at"] = _at(MAR1)
    march["vintage_records"][0]["value"] = march["vintage_records"][0]["revised_value"]
    rows.append(method_case("STOIC-DATA", "macro_application", "M11-F2-march-vintage",
                            _document("M11-F2-march-vintage", "macro_application", march),
                            "fail", kind="macro_application"))
    zscore = _macro()
    zscore.update(custom_metric_kind="z_score", c_score=None, substituted_metric="z_score")
    rows.append(method_case("STOIC-DATA", "macro_application", "M11-F2-zscore",
                            _document("M11-F2-zscore", "macro_application", zscore),
                            "fail", kind="macro_application"))

    for fid, fields in (
        ("M11-F3-vintage", ("release_vintages_recorded",)),
        ("M11-F3-history", ("historical_comparison_defined",)),
        ("M11-F3-rules", ("cycle_and_indicator_rules_recorded",)),
    ):
        op = _macro()
        for field in fields:
            op[field] = None
        rows.append(method_case("STOIC-DATA", "macro_application", fid,
                                _document(fid, "macro_application", op), "unknown",
                                kind="macro_application"))

    rows.append(method_case("STOIC-DATA", "process", "M11-F1:late", _late("M11-F1:late"), "fail", kind="c08_late"))
    rows.append(method_case("STOIC-DATA", "process", "M11-F1:missing", _missing("M11-F1:missing"), "unknown", kind="c08_missing"))
    rows.append(method_case("STOIC-DATA", "process", "M11-F1:identity", _identity("M11-F1:identity"), "fail", kind="c08_identity"))
    return rows


def semantic_audit() -> dict:
    rows = method_fixtures()
    return {"fixture_count": len(rows), "all_pass": all(row["status"] == "pass" for row in rows),
            "process_cases": sum(row["predicate"] == "process" for row in rows),
            "macro_cases": sum(row["predicate"] == "macro_application" for row in rows)}
