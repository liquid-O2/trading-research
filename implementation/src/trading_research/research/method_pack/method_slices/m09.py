"""M09 REFILL-STUDY acceptance cases at the C01 evidence boundary."""

from __future__ import annotations

from copy import deepcopy
from datetime import date

from ..clocks import et_ns
from ..evidence import fixture_document
from ..fixture_utils import method_case


DAY = date(2026, 1, 15)


def _t(hour: int, minute: int, second: int = 0) -> int:
    return et_ns(DAY, hour, minute, second)


STAGE_LIMITS = {
    "zone_definition_recorded": "zone_known_at",
    "zone_frozen": "zone_known_at",
    "departure_observed": "departure_at",
    "distinct_touch_id": "touch_at",
    "thesis_recorded": "zone_known_at",
    "memory_uses_only_prior_resolved_touches": "feature_max_known_at",
    "label_uses_only_post_touch_observations": "label_resolved_at",
    "instrument_and_threshold_preserved": "zone_known_at",
    "grade_model_frozen_before_touch": "model_known_at",
    "touch_selected_without_future_information": "order_at",
    "one_position_policy": "order_at",
    "fill_assumption_recorded": "order_at",
}


def _touch(*, branch: str = "touch_record") -> dict:
    return {
        "branch": branch,
        "side": "long",
        "instrument_id": "NQ-refill-fixture",
        "band_id": "REFILL-zone-100-101",
        "decision_at": _t(10, 10),
        "zone_definition_recorded": True,
        "zone_frozen": True,
        "zone_known_at": _t(9, 40),
        "departure_observed": True,
        "departure_at": _t(9, 45),
        "distinct_touch_id": True,
        "touch_at": _t(10, 0),
        "thesis_recorded": True,
        "feature_max_known_at": _t(9, 59),
        "memory_uses_only_prior_resolved_touches": True,
        "label_uses_only_post_touch_observations": True,
        "instrument_and_threshold_preserved": True,
        # Actual source relationships retained in each evidence payload.
        "zone": ["100", "101"],
        "zone_id": "REFILL-zone-100-101",
        "departure_zone_id": "REFILL-zone-100-101",
        "touch_zone_id": "REFILL-zone-100-101",
        "formation_id": "formation-001",
        "touch_id": "touch-001",
        "departure_price": "102",
        "touch_price": "100.5",
        "threshold_id": "source-refill-threshold-v1",
        "feature_touch_ids": ["touch-prior-001"],
        "prior_touch_records": [
            {"touch_id": "touch-prior-001", "resolved_at": _t(9, 42),
             "zone_id": "REFILL-zone-100-101"},
        ],
        "label_touch_id": "touch-001",
        "label_resolved_at": _t(10, 10),
        "label_definition": "supplied-source-hold-label",
        "automatic_zone_engine": None,
    }


def _order() -> dict:
    op = _touch(branch="supplied_selected_order")
    op.update({
        "grade_model_frozen_before_touch": True,
        "grade_available_at": _t(10, 0, 30),
        "touch_selected_without_future_information": True,
        "order_at": _t(10, 1),
        "order_inside_ticks": 12,
        "stop_ticks": 32,
        "target_ticks": 96,
        "cancel_minutes": 30,
        "one_position_policy": True,
        "round_trip_cost_ticks": 1,
        "stop_slippage_ticks": 1,
        "fill_assumption_recorded": True,
        "parent_touch_id": "touch-001",
        "order_id": "refill-order-001",
        "model_id": "supplied-refill-grader-v1",
        "model_known_at": _t(8, 0),
        "training_cutoff_at": _t(7, 59),
        "inclusion_frozen_at": _t(9, 30),
        "grade_feature_max_known_at": _t(9, 59),
        "selection_day": DAY.isoformat(),
        "signal_cohort_id": "refill-signals-312",
        "signal_count": 312,
        "fill_cohort_id": "refill-limit-fills-64",
        "fill_count": 64,
        "paired_cohort_claim": False,
        "later_ofm_causal_status": "negative",
        "later_ofm_result_r": "-0.54",
        "profit_reconstructed": False,
        "fill_rule": "touch_or_trade_through_modeled",
        "queue_verified": False,
    })
    return op


def _document(fid: str, predicate: str, op: dict) -> dict:
    return fixture_document("REFILL-STUDY", predicate, fid, op)


def _order_document(fid: str, op: dict) -> dict:
    """Attach the selected order to an actual, separately typed touch row."""
    doc = _document(fid, "selected_order_configuration", op)
    parent_id = f"{fid}:parent-touch"
    parent_doc = _document(parent_id, "touch_causality", _touch())
    parent = parent_doc["candidates"][0]
    parent["cohort_id"] = "synthetic-fixtures-parent-touches"
    parent["touch_id"] = op["parent_touch_id"]
    target = doc["candidates"][0]
    target["parent_attempt_id"] = parent_id
    target["touch_id"] = op["parent_touch_id"]
    target["order_id"] = op["order_id"]
    doc["candidates"].append(parent)
    doc["objects"].extend(parent_doc["objects"])
    doc["assertions"].extend(parent_doc["assertions"])
    doc["evidence"].extend(parent_doc["evidence"])
    return doc


def _payload(candidate: dict, field: str, assertions: dict, objects: dict, evidence: dict) -> dict:
    binding = candidate["operands"].get(field, {})
    record = assertions.get(binding.get("assertion_id")) or objects.get(binding.get("object_id"))
    if record:
        for eid in record.get("evidence_ids", []):
            if eid in evidence:
                return evidence[eid].get("payload", {})
    return {}


def audit_candidate(candidate, operands, objects, assertions, evidence) -> list[dict]:
    """Audit touch/order identities and source cohort relationships."""
    findings: list[dict] = []
    payload = _payload(candidate, "zone_definition_recorded", assertions, objects, evidence)
    zone = payload.get("zone") or []
    zone_ids = {payload.get("zone_id"), payload.get("departure_zone_id"), payload.get("touch_zone_id")}
    if operands.get("zone_definition_recorded") is True:
        if zone_ids != set(candidate["band_ids"]):
            findings.append({"field": "zone_definition_recorded", "kind": "identity",
                             "reason": "formation, departure and return do not share the frozen source zone identity",
                             "recipe_id": "O116"})
        if (payload.get("formation_id") is None or payload.get("touch_id") is None
                or payload.get("formation_id") == payload.get("touch_id")):
            findings.append({"field": "distinct_touch_id", "kind": "identity",
                             "reason": "return touch is not a distinct episode identity",
                             "recipe_id": "O148"})
        try:
            lo, hi = map(float, zone)
            departure, touch = float(payload.get("departure_price")), float(payload.get("touch_price"))
            actual_route = not lo <= departure <= hi and lo <= touch <= hi
        except (TypeError, ValueError):
            actual_route = False
        if not actual_route:
            findings.append({"field": "departure_observed", "kind": "identity",
                             "reason": "actual prices do not show departure followed by a return into the zone",
                             "recipe_id": "O116"})

    feature_at, touch_at = operands.get("feature_max_known_at"), operands.get("touch_at")
    if feature_at is not None and touch_at is not None and feature_at >= touch_at:
        findings.append({"field": "feature_max_known_at", "kind": "ordering",
                         "reason": "every feature must be known strictly before the current touch",
                         "recipe_id": "O149"})
    if operands.get("memory_uses_only_prior_resolved_touches") is True:
        records = payload.get("prior_touch_records") or []
        feature_ids = set(payload.get("feature_touch_ids") or [])
        current_id = payload.get("touch_id")
        valid = (records and feature_ids == {row.get("touch_id") for row in records}
                 and current_id not in feature_ids and feature_at is not None
                 and all(row.get("resolved_at") is not None and row["resolved_at"] <= feature_at
                         and row.get("zone_id") in candidate["band_ids"] for row in records))
        if not valid:
            findings.append({"field": "memory_uses_only_prior_resolved_touches", "kind": "ordering",
                             "reason": "memory includes the current/future or unresolved touch outcome",
                             "recipe_id": "O117"})
    if operands.get("label_uses_only_post_touch_observations") is True:
        label_at = payload.get("label_resolved_at")
        if (label_at is None or touch_at is None or label_at <= touch_at
                or payload.get("label_touch_id") != payload.get("touch_id")):
            findings.append({"field": "label_uses_only_post_touch_observations", "kind": "ordering",
                             "reason": "current label is not a post-touch observation of the same touch",
                             "recipe_id": "O148"})

    if candidate["predicate"] == "selected_order_configuration":
        if payload.get("parent_touch_id") != payload.get("touch_id"):
            findings.append({"field": "parent_touch_id", "kind": "identity",
                             "reason": "selected order is not attached to its actual touch record",
                             "recipe_id": "O150"})
        if not candidate.get("parent_attempt_id") or candidate.get("touch_id") != payload.get("parent_touch_id"):
            findings.append({"field": "parent_touch_id", "kind": "identity",
                             "reason": "selected order lacks its actual separately typed parent touch candidate",
                             "recipe_id": "O150"})
        model_at = payload.get("model_known_at")
        train_at = payload.get("training_cutoff_at")
        inclusion_at = payload.get("inclusion_frozen_at")
        order_at = operands.get("order_at")
        grade_at = operands.get("grade_available_at")
        causal = all(value is not None for value in (model_at, train_at, inclusion_at, order_at, grade_at, touch_at))
        causal = causal and train_at <= model_at < touch_at and inclusion_at < touch_at
        causal = causal and payload.get("grade_feature_max_known_at") < touch_at
        causal = causal and grade_at <= order_at and model_at < order_at and inclusion_at < order_at
        if (operands.get("grade_model_frozen_before_touch") is True
                and (not causal or payload.get("selection_day") != DAY.isoformat())):
            findings.append({"field": "grade_model_frozen_before_touch", "kind": "ordering",
                             "reason": "model, training cutoff, inclusion, features or grade were not frozen before touch/order",
                             "recipe_id": "O149"})
        if (operands.get("touch_selected_without_future_information") is True
                and (payload.get("signal_count"), payload.get("fill_count")) != (312, 64)):
            findings.append({"field": "touch_selected_without_future_information", "kind": "identity",
                             "reason": "published signal/fill cohort counts were not preserved",
                             "recipe_id": "O148"})
        if (operands.get("touch_selected_without_future_information") is True
                and (payload.get("paired_cohort_claim") is True
                     or payload.get("signal_cohort_id") == payload.get("fill_cohort_id"))):
            findings.append({"field": "touch_selected_without_future_information", "kind": "identity",
                             "reason": "312 signals and 64 fills are distinct cohorts, not paired trades",
                             "recipe_id": "O148"})
        if (operands.get("touch_selected_without_future_information") is True
                and (payload.get("later_ofm_causal_status") != "negative"
                     or payload.get("profit_reconstructed") is not False)):
            findings.append({"field": "touch_selected_without_future_information", "kind": "identity",
                             "reason": "later OFM negative causal correction was omitted or replaced by reconstructed profit",
                             "recipe_id": "O149"})
    return findings


def _mutate_time(doc: dict, fid: str, field: str, when: int) -> None:
    candidate = doc["candidates"][0]
    binding = candidate["operands"][field]
    records = doc["assertions"] if "assertion_id" in binding else doc["objects"]
    key = "assertion_id" if "assertion_id" in binding else "object_id"
    record = next(row for row in records if row[key] == binding[key])
    record["known_at"] = when
    if "observation_end" in record:
        record.update(observation_start=when, observation_end=when)
    else:
        record.update(formation_start=when, formation_end=when, as_of=when)
    for eid in record.get("evidence_ids", []):
        next(row for row in doc["evidence"] if row["evidence_id"] == eid).update(
            observation_start=when, observation_end=when, known_at=when)


def _late(fid: str) -> dict:
    doc = _document(fid, "touch_causality", _touch())
    _mutate_time(doc, fid, "zone_definition_recorded", _t(10, 1))
    return doc


def _missing(fid: str) -> dict:
    doc = _document(fid, "touch_causality", _touch())
    del doc["candidates"][0]["operands"]["distinct_touch_id"]
    return doc


def _identity(fid: str) -> dict:
    doc = _document(fid, "touch_causality", _touch())
    binding = doc["candidates"][0]["operands"]["departure_observed"]
    assertion = next(row for row in doc["assertions"] if row["assertion_id"] == binding["assertion_id"])
    assertion["band_id"] = "foreign-zone"
    for eid in assertion["evidence_ids"]:
        next(row for row in doc["evidence"] if row["evidence_id"] == eid)["band_id"] = "foreign-zone"
    return doc


def method_fixtures() -> list[dict]:
    rows = [
        method_case("REFILL-STUDY", "touch_causality", "M09-F1",
                    _document("M09-F1", "touch_causality", _touch()), "pass"),
        method_case("REFILL-STUDY", "selected_order_configuration", "M09-F1-order",
                    _order_document("M09-F1-order", _order()),
                    "pass", kind="selected_order_configuration"),
    ]

    future = _touch()
    future["prior_touch_records"].append({
        "touch_id": "touch-001", "resolved_at": _t(10, 10),
        "zone_id": future["band_id"],
    })
    future["feature_touch_ids"].append("touch-001")
    rows.append(method_case("REFILL-STUDY", "touch_causality", "M09-F2-future-memory",
                            _document("M09-F2-future-memory", "touch_causality", future), "fail"))
    later = _order()
    later.update(model_known_at=_t(10, 2), training_cutoff_at=_t(10, 2),
                 selection_day="2026-01-16")
    rows.append(method_case("REFILL-STUDY", "selected_order_configuration", "M09-F2-future-grade",
                            _order_document("M09-F2-future-grade", later),
                            "fail", kind="selected_order_configuration"))
    paired = _order()
    paired.update(paired_cohort_claim=True, fill_cohort_id=paired["signal_cohort_id"])
    rows.append(method_case("REFILL-STUDY", "selected_order_configuration", "M09-F2-paired-cohorts",
                            _order_document("M09-F2-paired-cohorts", paired),
                            "fail", kind="selected_order_configuration"))

    missing_zone = _touch()
    missing_zone.update(zone_definition_recorded=None, zone_frozen=None,
                        instrument_and_threshold_preserved=None, automatic_zone_engine=None)
    rows.append(method_case("REFILL-STUDY", "touch_causality", "M09-F3-zone",
                            _document("M09-F3-zone", "touch_causality", missing_zone), "unknown"))
    missing_grade = _order()
    missing_grade.update(grade_model_frozen_before_touch=None, grade_available_at=None,
                         touch_selected_without_future_information=None, model_id=None)
    rows.append(method_case("REFILL-STUDY", "selected_order_configuration", "M09-F3-grade",
                            _order_document("M09-F3-grade", missing_grade),
                            "unknown", kind="selected_order_configuration"))

    rows.append(method_case("REFILL-STUDY", "touch_causality", "M09-F1:late",
                            _late("M09-F1:late"), "fail", kind="c08_late"))
    rows.append(method_case("REFILL-STUDY", "touch_causality", "M09-F1:missing",
                            _missing("M09-F1:missing"), "unknown", kind="c08_missing"))
    rows.append(method_case("REFILL-STUDY", "touch_causality", "M09-F1:identity",
                            _identity("M09-F1:identity"), "fail", kind="c08_identity"))
    return rows


def semantic_audit() -> dict:
    rows = method_fixtures()
    return {
        "fixture_count": len(rows),
        "all_pass": all(row["status"] == "pass" for row in rows),
        "touch_cases": sum(row["predicate"] == "touch_causality" for row in rows),
        "selected_order_cases": sum(row["predicate"] == "selected_order_configuration" for row in rows),
    }
