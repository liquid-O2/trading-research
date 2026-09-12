"""M12 STOIC-RISK fixed-baseline printed-ladder acceptance cases."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from decimal import Decimal

from ..clocks import et_ns
from ..evidence import fixture_document
from ..fixture_utils import method_case


METHOD = "STOIC-RISK"
DAY = date(2026, 1, 15)
YDAY = date(2026, 1, 14)


def _t(hour: int, minute: int = 0, *, day: date = DAY) -> int:
    return et_ns(day, hour, minute)


STAGE_LIMITS = {
    "validated_process": "validation_known_at",
    "prior_sample_n": "validation_known_at",
    "win_rate_known": "validation_known_at",
    "average_rr_known": "validation_known_at",
    "mc_loss_streak_known": "validation_known_at",
    "base_risk_fraction": "baseline_known_at",
    "risk_stage": "decision_at",
    "risk_units": "decision_at",
    "planned_reward_r": "decision_at",
    "next_risk_units": "decision_at",
    "first_trade_closed": "first_trade_close_at",
    "first_trade_result_units": "first_trade_close_at",
    "second_trade_result_units": "second_trade_close_at",
}


def _prior_records(n: int) -> list[dict]:
    return [
        {
            "trade_id": f"prior-{number:03d}",
            "process_id": "stoic-process-v1",
            "closed_at": _t(12, number % 60, day=YDAY),
            "outcome": "win" if number <= round(n * .55) else "loss",
        }
        for number in range(1, n + 1)
    ]


def _base(stage: str, *, n: int = 100, b: str = "100",
          fraction: str | None = None) -> dict:
    baseline = Decimal(b)
    frac = Decimal(fraction) if fraction is not None else baseline / Decimal(10000)
    decision = {"first": _t(9, 30), "second": _t(10, 1),
                "reset_after_second_win": _t(11, 1)}[stage]
    records = _prior_records(n)
    op = {
        "branch": stage, "risk_stage": stage, "side": "not_applicable",
        "instrument_id": "STOIC-process-fixture", "band_id": "stoic-process-v1",
        "decision_at": decision, "validated_process": True,
        "prior_sample_n": n, "win_rate_known": True,
        "average_rr_known": True, "mc_loss_streak_known": True,
        "base_risk_fraction": frac,
        "validation_known_at": _t(16, 5, day=YDAY),
        "baseline_known_at": _t(9, 0), "second_trade_close_at": _t(11, 0),
        "process_id": "stoic-process-v1", "process_version": "stoic-process-v1",
        "prior_sample_ids": [row["trade_id"] for row in records],
        "prior_trade_records": records,
        "validation_record": {
            "validation_id": "validation-stoic-v1-20260114",
            "process_id": "stoic-process-v1",
            "sample_ids": [row["trade_id"] for row in records],
            "sample_n": n, "known_at": _t(16, 5, day=YDAY),
        },
        "win_rate_record": {
            "metric_id": "stoic-process-v1-win-rate", "process_id": "stoic-process-v1",
            "value": "0.55", "definition": "closed wins / closed observations",
            "known_at": _t(16, 1, day=YDAY),
        },
        "average_rr_record": {
            "metric_id": "stoic-process-v1-average-rr", "process_id": "stoic-process-v1",
            "value": "2", "definition": "source supplied average reward:risk",
            "known_at": _t(16, 2, day=YDAY),
        },
        "mc_record": {
            "result_id": "stoic-process-v1-mc-loss-streak",
            "design_id": "source-supplied-mc-v1", "process_id": "stoic-process-v1",
            "max_loss_streak": 8, "known_at": _t(16, 3, day=YDAY),
            "supplied_result": True,
        },
        "equity_baseline": {
            "baseline_id": "stoic-fixed-E0-v1", "E0": "10000", "B": str(baseline),
            "fraction": str(frac), "known_at": _t(9, 0), "fixed": True,
        },
        "closed_trade_records": [],
        "activation_heading": "after two consecutive wins",
        "printed_activation": "increase risk on the second trade after one win",
        "requested_transition": "printed",
    }
    if stage == "first":
        op.update(risk_units=Decimal(1), planned_reward_r=Decimal(3),
                  planned_risk_amount=baseline, planned_reward_amount=baseline * 3)
    elif stage == "second":
        first_close = _t(10, 0)
        op.update(
            first_trade_closed=True, first_trade_result_units=Decimal(3),
            first_trade_close_at=first_close, risk_units=Decimal(4),
            planned_reward_r=Decimal(3), planned_risk_amount=baseline * 4,
            planned_reward_amount=baseline * 12,
            closed_trade_records=[{
                "trade_id": "ladder-trade-1", "process_id": "stoic-process-v1",
                "stage": "first", "closed_at": first_close,
                "result_units": "3", "result_amount": str(baseline * 3),
            }], stage_parent_trade_id="ladder-trade-1")
    else:
        op.update(
            second_trade_result_units=Decimal(12), next_risk_units=Decimal(1),
            next_risk_amount=baseline, cumulative_result_units=Decimal(15),
            cumulative_result_amount=baseline * 15,
            closed_trade_records=[
                {"trade_id": "ladder-trade-1", "process_id": "stoic-process-v1",
                 "stage": "first", "closed_at": _t(10, 0),
                 "result_units": "3", "result_amount": str(baseline * 3)},
                {"trade_id": "ladder-trade-2", "process_id": "stoic-process-v1",
                 "stage": "second", "parent_trade_id": "ladder-trade-1",
                 "closed_at": _t(11, 0), "result_units": "12",
                 "result_amount": str(baseline * 12)},
            ], stage_parent_trade_id="ladder-trade-2")
    return op


def _add_support_object(doc: dict, object_id: str, recipe_id: str, value: dict,
                        parents: list[str], known_at: int, payload: dict) -> None:
    candidate = doc["candidates"][0]
    template = doc["evidence"][0]
    evidence_id = f"{object_id}:evidence"
    evidence = deepcopy(template)
    evidence.update({"evidence_id": evidence_id,
                     "description": f"Actual synthetic support record for {recipe_id}.",
                     "payload": deepcopy(payload), "observation_start": known_at,
                     "observation_end": known_at, "known_at": known_at})
    doc["evidence"].append(evidence)
    doc["objects"].append({
        "object_id": object_id, "recipe_id": recipe_id, "method_id": METHOD,
        "branch_scope": [candidate["branch"]], "author": METHOD,
        "instrument_id": candidate["instrument_id"], "band_id": candidate["band_ids"][0],
        "side": candidate["side"], "parent_ids": list(parents),
        "source_ref": template["source_ref"], "source_version": template["source_version"],
        "value": deepcopy(value), "units": {}, "formation_start": known_at,
        "formation_end": known_at, "as_of": known_at, "known_at": known_at,
        "state": "supplied", "hole_ids": [], "evidence_ids": [evidence_id],
    })
    candidate["object_ids"].append(object_id)


def _document(fid: str, op: dict) -> dict:
    """Create C01 records with explicit cohort, outcome, validation and risk parents."""
    support = {name: f"{fid}:support:{name}" for name in
               ("cohort", "outcomes", "validation", "equity", "trades", "stage")}
    op["support_object_ids"] = deepcopy(support)
    doc = fixture_document(METHOD, "printed_ladder", fid, op)
    validation_at = op.get("validation_known_at")
    prior_records = op.get("prior_trade_records")
    prior_records_for_support = prior_records if isinstance(prior_records, list) else []
    prior_closes = [row.get("closed_at") for row in prior_records_for_support
                    if row.get("closed_at") is not None]
    outcome_at = max(prior_closes, default=validation_at)
    payload = {key: value for key, value in op.items() if not key.startswith("_")}
    _add_support_object(doc, support["cohort"], "O148",
                        {"process_id": op.get("process_id"),
                         "sample_ids": op.get("prior_sample_ids")},
                        [], outcome_at, payload)
    _add_support_object(doc, support["outcomes"], "O153",
                        {"process_id": op.get("process_id"),
                         "prior_trade_records": prior_records},
                        [support["cohort"]], outcome_at, payload)
    _add_support_object(doc, support["validation"], "O154",
                        op.get("validation_record") or {},
                        [support["cohort"], support["outcomes"]], validation_at, payload)
    _add_support_object(doc, support["equity"], "O140",
                        op.get("equity_baseline") or {},
                        [], op.get("baseline_known_at"), payload)
    closed_records = op.get("closed_trade_records")
    closed_for_support = closed_records if isinstance(closed_records, list) else []
    trade_closes = [row.get("closed_at") for row in closed_for_support
                    if row.get("closed_at") is not None]
    trade_at = max(trade_closes, default=outcome_at)
    _add_support_object(doc, support["trades"], "O153",
                        {"process_id": op.get("process_id"),
                         "closed_trade_records": closed_records},
                        [], trade_at, payload)
    _add_support_object(doc, support["stage"], "O155",
                        {"risk_stage": op.get("risk_stage"),
                         "stage_parent_trade_id": op.get("stage_parent_trade_id")},
                        [support["validation"], support["equity"], support["trades"]],
                        op.get("decision_at"), payload)
    objects = {row["object_id"]: row for row in doc["objects"]}
    for field, binding in doc["candidates"][0]["operands"].items():
        object_id = binding.get("object_id", f"{fid}:o:{field}")
        obj = objects.get(object_id)
        if obj is None:
            continue
        if obj["recipe_id"] == "O154":
            obj["parent_ids"] = [support["validation"]]
        elif obj["recipe_id"] == "O155":
            if field == "base_risk_fraction":
                obj["parent_ids"] = [support["equity"]]
            elif field in {"first_trade_closed", "first_trade_result_units",
                           "first_trade_close_at", "second_trade_result_units"}:
                obj["parent_ids"] = [support["trades"]]
            else:
                obj["parent_ids"] = [support["stage"]]
        if "assertion_id" in binding:
            assertion = next(row for row in doc["assertions"]
                             if row["assertion_id"] == binding["assertion_id"])
            assertion["object_id"] = obj["object_id"]
    return doc


def _payload(candidate: dict, field: str, assertions: dict, objects: dict,
             evidence: dict) -> dict:
    binding = candidate.get("operands", {}).get(field, {})
    record = assertions.get(binding.get("assertion_id"))
    if record is None:
        record = objects.get(binding.get("object_id"), {})
    for evidence_id in record.get("evidence_ids", []):
        if evidence_id in evidence:
            return evidence[evidence_id].get("payload", {})
    return {}


def _decimal_value(value):
    """Return a finite Decimal, or None for missing/malformed source data."""
    if value is None or isinstance(value, bool):
        return None
    try:
        result = Decimal(value)
    except (TypeError, ValueError, ArithmeticError):
        return None
    return result if result.is_finite() else None


def _event_value(value):
    return value if type(value) is int else None


def audit_candidate(candidate, operands, objects, assertions, evidence) -> list[dict]:
    """Audit actual process/trade identities and fixed-baseline stage geometry."""
    findings: list[dict] = []

    def issue(field: str, reason: str, *, kind: str = "identity",
              unknown: bool = False, recipe: str = "O155",
              affects_admission: bool = True) -> None:
        findings.append({"field": field, "kind": kind, "unknown": unknown,
                         "reason": reason, "recipe_id": recipe,
                         "affects_admission": affects_admission})

    payload = _payload(candidate, "validated_process", assertions, objects, evidence)
    if not payload:
        payload = _payload(candidate, "risk_stage", assertions, objects, evidence)
    process_id = payload.get("process_id")
    prior = payload.get("prior_trade_records")
    prior_ids = payload.get("prior_sample_ids")
    validation = payload.get("validation_record")
    validation_at_raw = payload.get("validation_known_at")
    validation_at = _event_value(validation_at_raw)

    if operands.get("validated_process") is True:
        missing_sample = (
            process_id is None or not isinstance(prior, list)
            or not isinstance(prior_ids, list) or not isinstance(validation, dict)
            or not validation or validation_at_raw is None
        )
        if not missing_sample:
            missing_sample = any(
                row.get("trade_id") is None or row.get("process_id") is None
                or row.get("closed_at") is None for row in prior
            ) or any(validation.get(key) is None for key in
                     ("sample_ids", "sample_n", "process_id", "known_at"))
        if missing_sample:
            issue("validated_process",
                  "prior cohort or validation availability is missing",
                  kind="supplied_record_missing", unknown=True, recipe="O154")
        else:
            actual_ids = [row["trade_id"] for row in prior]
            valid_sample = (
                len(prior) == operands.get("prior_sample_n") and len(prior) >= 100
                and len(actual_ids) == len(set(actual_ids))
                and actual_ids == prior_ids == validation["sample_ids"]
                and validation["sample_n"] == len(prior)
                and validation["process_id"] == process_id
                and validation_at is not None
                and _event_value(validation["known_at"]) == validation_at
                and all(row["process_id"] == process_id
                        and _event_value(row["closed_at"]) is not None
                        and row["closed_at"] <= validation_at < candidate["decision_at"]
                        for row in prior)
            )
            if not valid_sample:
                issue("validated_process",
                      "actual prior cohort does not contain 100 unique closed trades from the same process before validation",
                      recipe="O154")
        for field, record_name, id_name in (
            ("win_rate_known", "win_rate_record", "metric_id"),
            ("average_rr_known", "average_rr_record", "metric_id"),
            ("mc_loss_streak_known", "mc_record", "result_id"),
        ):
            if operands.get(field) is not True:
                continue
            record = payload.get(record_name)
            required = [id_name, "process_id", "known_at"]
            if field == "mc_loss_streak_known":
                required += ["design_id", "max_loss_streak", "supplied_result"]
            else:
                required += ["value", "definition"]
            if (not isinstance(record, dict) or not record
                    or validation_at_raw is None
                    or any(record.get(key) is None for key in required)):
                issue(field, f"{record_name} or its availability is missing",
                      kind="supplied_record_missing", unknown=True, recipe="O154")
                continue
            record_at = _event_value(record["known_at"])
            valid = (validation_at is not None and record_at is not None
                     and record["process_id"] == process_id
                     and record_at <= validation_at < candidate["decision_at"])
            if field == "mc_loss_streak_known":
                valid = valid and record["supplied_result"] is True
            if not valid:
                issue(field,
                      f"{record_name} contradicts the same-process identity or pre-decision availability",
                      recipe="O154")

    support = payload.get("support_object_ids") or {}
    expected_recipes = {"cohort": "O148", "outcomes": "O153",
                        "validation": "O154", "equity": "O140",
                        "trades": "O153", "stage": "O155"}
    graph_missing = not support or any(support.get(name) not in objects
                                       for name in expected_recipes)
    if graph_missing:
        issue("validated_process",
              "risk decision parent graph is unavailable",
              kind="supplied_record_missing", unknown=True, recipe="O154")
    else:
        relations_ok = (
            all(objects[support[name]]["recipe_id"] == recipe
                for name, recipe in expected_recipes.items())
            and objects[support["outcomes"]]["parent_ids"] == [support["cohort"]]
            and set(objects[support["validation"]]["parent_ids"])
                == {support["cohort"], support["outcomes"]}
            and set(objects[support["stage"]]["parent_ids"])
                == {support["validation"], support["equity"], support["trades"]}
        )
        if not relations_ok:
            issue("validated_process",
                  "risk decision parent graph contradicts the required cohort/outcome/validation/equity identities",
                  recipe="O154")

    baseline = payload.get("equity_baseline")
    b = None
    if (not isinstance(baseline, dict) or not baseline
            or any(baseline.get(key) is None for key in ("baseline_id", "E0", "B"))):
        issue("base_risk_fraction", "fixed E0/B baseline is missing",
              kind="supplied_record_missing", unknown=True)
    else:
        e0, b = _decimal_value(baseline["E0"]), _decimal_value(baseline["B"])
        if e0 is None or b is None:
            issue("base_risk_fraction", "fixed E0/B baseline is malformed")
            b = None
        elif e0 <= 0 or b <= 0:
            issue("base_risk_fraction", "fixed E0 and B must both be positive")
        else:
            actual_fraction = b / e0
            if actual_fraction != operands.get("base_risk_fraction"):
                issue("base_risk_fraction",
                      "declared fraction does not reconcile to the fixed E0/B baseline")
        if baseline.get("fixed") is False:
            issue("base_risk_fraction", "observed baseline was rebased instead of fixed")
        elif baseline.get("fixed") is None:
            issue("base_risk_fraction", "fixed-baseline status is missing",
                  kind="supplied_record_missing", unknown=True)

    stage = operands.get("risk_stage")
    closed = payload.get("closed_trade_records")
    if stage is not None and stage != candidate.get("branch"):
        issue("risk_stage", "risk stage does not match the candidate branch")
    if stage == "first" and operands.get("risk_units") == Decimal(1):
        risk_amount = _decimal_value(payload.get("planned_risk_amount"))
        reward_amount = _decimal_value(payload.get("planned_reward_amount"))
        if b is None or risk_amount is None or reward_amount is None:
            issue("risk_units", "first-stage risk or reward amount is missing",
                  kind="supplied_record_missing", unknown=True)
        elif risk_amount != b or reward_amount != 3 * b:
            issue("risk_units", "first printed risk/target does not equal fixed 1B/3B")
    elif stage == "second":
        parent_id = payload.get("stage_parent_trade_id")
        first = (next((row for row in closed if row.get("trade_id") == parent_id), None)
                 if isinstance(closed, list) and parent_id is not None else None)
        required = ("trade_id", "process_id", "stage", "closed_at",
                    "result_units", "result_amount")
        risk_amount = _decimal_value(payload.get("planned_risk_amount"))
        reward_amount = _decimal_value(payload.get("planned_reward_amount"))
        incomplete = (parent_id is None or first is None or b is None
                      or any(first.get(key) is None for key in required)
                      or risk_amount is None or reward_amount is None)
        if incomplete:
            issue("first_trade_closed",
                  "actual first trade or second-stage cash geometry is missing",
                  kind="supplied_record_missing", unknown=True)
        else:
            first_close = _event_value(first["closed_at"])
            actual = (
                first["process_id"] == process_id and first["stage"] == "first"
                and _decimal_value(first["result_units"]) == Decimal(3)
                and _decimal_value(first["result_amount"]) == 3 * b
                and first_close == operands.get("first_trade_close_at")
                and first_close is not None and first_close < candidate["decision_at"]
                and risk_amount == 4 * b and reward_amount == 12 * b
            )
            if not actual:
                issue("first_trade_closed",
                      "second stage is not funded by the actual same-process closed first +3B trade on the fixed baseline",
                      kind="ordering")
        if operands.get("risk_units") != Decimal(4):
            issue("risk_units",
                  "4% of updated equity is not the printed fixed four-baseline-unit risk")
    elif stage == "reset_after_second_win" and operands.get("second_trade_result_units") is not None:
        second_id = payload.get("stage_parent_trade_id")
        second = (next((row for row in closed if row.get("trade_id") == second_id), None)
                  if isinstance(closed, list) and second_id is not None else None)
        first_id = second.get("parent_trade_id") if isinstance(second, dict) else None
        first = (next((row for row in closed if row.get("trade_id") == first_id), None)
                 if isinstance(closed, list) and first_id is not None else None)
        required_first = ("trade_id", "process_id", "stage", "closed_at",
                          "result_units", "result_amount")
        required_second = (*required_first, "parent_trade_id")
        cumulative_units = _decimal_value(payload.get("cumulative_result_units"))
        cumulative_amount = _decimal_value(payload.get("cumulative_result_amount"))
        next_amount = _decimal_value(payload.get("next_risk_amount"))
        second_available = payload.get("second_trade_close_at")
        incomplete = (
            second_id is None or second is None or first_id is None or first is None or b is None
            or any(first.get(key) is None for key in required_first)
            or any(second.get(key) is None for key in required_second)
            or cumulative_units is None or cumulative_amount is None or next_amount is None
            or second_available is None
        )
        if incomplete:
            issue("second_trade_result_units",
                  "linked first/second trade records, close availability, or reset cash geometry is missing",
                  kind="supplied_record_missing", unknown=True)
        else:
            first_close = _event_value(first["closed_at"])
            second_close = _event_value(second["closed_at"])
            actual = (
                second["parent_trade_id"] == first["trade_id"]
                and first["stage"] == "first" and second["stage"] == "second"
                and first["process_id"] == second["process_id"] == process_id
                and _decimal_value(first["result_units"]) == Decimal(3)
                and _decimal_value(second["result_units"]) == Decimal(12)
                and _decimal_value(first["result_amount"]) == 3 * b
                and _decimal_value(second["result_amount"]) == 12 * b
                and first_close is not None and second_close is not None
                and first_close < second_close == second_available
                and second_close < candidate["decision_at"]
                and cumulative_units == Decimal(15) and cumulative_amount == 15 * b
                and next_amount == b
            )
            if not actual:
                issue("second_trade_result_units",
                      "reset contradicts the linked +3B/+12B trades, cash amounts, close order, or +15B geometry",
                      kind="ordering")

    if payload.get("simulation_run_by_pack") is True:
        issue("mc_loss_streak_known", "method pass invented a Monte Carlo simulation", recipe="O154")
    if payload.get("entry_created") is True or payload.get("profitability_asserted") is True:
        issue("risk_stage", "risk overlay invented an entry or profitability claim")
    if payload.get("requested_transition") == "general_activation":
        issue("risk_stage",
              "general activation is unresolved because the heading and printed ladder conflict",
              kind="supplied_record_missing", unknown=True)
    else:
        issue("risk_stage",
              "general activation remains unresolved because the source heading and printed ladder conflict",
              kind="supplied_record_missing", affects_admission=False)
    if payload.get("requested_transition") == "after_second_loss":
        issue("second_trade_result_units", "the next state after a second loss is unpublished",
              kind="supplied_record_missing", unknown=True)
    elif payload.get("requested_transition") == "equity_rebase":
        issue("risk_units", "equity rebasing and later-cycle transitions are unpublished",
              kind="supplied_record_missing", unknown=True)
    return findings


def _manifest_mutations() -> list[dict]:
    source = _document("M12-F1-first", _base("first"))

    def case(suffix: str, mutate, expected: str, kind: str) -> dict:
        document = deepcopy(source)
        fid = f"M12-F1:{suffix}"
        document["candidates"][0]["candidate_id"] = fid
        for assertion in document["assertions"]:
            assertion["candidate_id"] = fid
        mutate(document)
        return method_case(METHOD, "printed_ladder", fid, document, expected, kind=kind)

    def late(document: dict) -> None:
        assertion = next(row for row in document["assertions"]
                         if row["field"] == "validated_process")
        when = document["candidates"][0]["decision_at"] + 1
        assertion.update(observation_start=when, observation_end=when, known_at=when)
        for row in document["evidence"]:
            if row["evidence_id"] in assertion["evidence_ids"]:
                row.update(observation_start=when, observation_end=when, known_at=when)

    def missing(document: dict) -> None:
        document["candidates"][0]["operands"].pop("mc_loss_streak_known")

    def identity(document: dict) -> None:
        obj = next(row for row in document["objects"]
                   if row["object_id"].endswith(":o:base_risk_fraction"))
        obj["band_id"] = "foreign-equity-baseline"
        for row in document["evidence"]:
            if row["evidence_id"] in obj["evidence_ids"]:
                row["band_id"] = "foreign-equity-baseline"

    return [case("late", late, "fail", "c08_late"),
            case("missing", missing, "unknown", "c08_missing"),
            case("identity", identity, "fail", "c08_identity")]


def method_fixtures() -> list[dict]:
    first = _base("first")
    second = _base("second")
    reset = _base("reset_after_second_win")
    rows = [
        method_case(METHOD, "printed_ladder", "M12-F1-first",
                    _document("M12-F1-first", first), "pass"),
        method_case(METHOD, "printed_ladder", "M12-F1-second",
                    _document("M12-F1-second", second), "pass"),
        method_case(METHOD, "printed_ladder", "M12-F1-reset",
                    _document("M12-F1-reset", reset), "pass"),
    ]
    not_closed = _base("second")
    not_closed["first_trade_closed"] = False
    not_closed["first_trade_close_at"] = _t(10, 2)
    not_closed["closed_trade_records"][0]["closed_at"] = _t(10, 2)
    rows.append(method_case(METHOD, "printed_ladder", "M12-F2-not-closed",
                            _document("M12-F2-not-closed", not_closed), "fail"))
    rebased = _base("second")
    rebased.update(risk_units=Decimal("4.12"), planned_risk_amount=Decimal("412"),
                   updated_equity=Decimal("10300"),
                   updated_equity_fraction=Decimal("0.04"))
    rows.append(method_case(METHOD, "printed_ladder", "M12-F2-rebase-412",
                            _document("M12-F2-rebase-412", rebased), "fail"))
    n99 = _base("first", n=99)
    n99["validated_process"] = False
    rows.append(method_case(METHOD, "printed_ladder", "M12-F2-n99",
                            _document("M12-F2-n99", n99), "fail"))
    fraction = _base("first", b="101", fraction="0.0101")
    rows.append(method_case(METHOD, "printed_ladder", "M12-F2-base-1.01pct",
                            _document("M12-F2-base-1.01pct", fraction), "fail"))
    unvalidated = _base("first")
    unvalidated["validated_process"] = False
    rows.append(method_case(METHOD, "printed_ladder", "M12-F2-unvalidated",
                            _document("M12-F2-unvalidated", unvalidated), "fail"))
    mc = _base("first")
    mc.update(validated_process=None, mc_loss_streak_known=None)
    mc["mc_record"].update(result_id=None, design_id=None, max_loss_streak=None,
                           supplied_result=False)
    rows.append(method_case(METHOD, "printed_ladder", "M12-F3-mc",
                            _document("M12-F3-mc", mc), "unknown"))
    activation = _base("first")
    activation["requested_transition"] = "general_activation"
    rows.append(method_case(METHOD, "printed_ladder", "M12-F3-activation",
                            _document("M12-F3-activation", activation), "unknown"))
    after_loss = _base("reset_after_second_win")
    after_loss.update(second_trade_result_units=None, next_risk_units=None,
                      requested_transition="after_second_loss")
    after_loss["closed_trade_records"][1].update(result_units="-4", result_amount="-400")
    rows.append(method_case(METHOD, "printed_ladder", "M12-F3-after-loss",
                            _document("M12-F3-after-loss", after_loss), "unknown"))
    rebase_hole = _base("first")
    rebase_hole["requested_transition"] = "equity_rebase"
    rows.append(method_case(METHOD, "printed_ladder", "M12-F3-rebase-policy",
                            _document("M12-F3-rebase-policy", rebase_hole), "unknown"))
    rows.extend(_manifest_mutations())
    return rows


def semantic_audit() -> dict:
    rows = method_fixtures()
    return {
        "fixture_count": len(rows),
        "all_pass": all(row["status"] == "pass" for row in rows),
        "positive_cases": sum(row["id"].startswith("M12-F1-") for row in rows),
        "negative_cases": sum(row["id"].startswith("M12-F2-") for row in rows),
        "hole_cases": sum(row["id"].startswith("M12-F3-") for row in rows),
        "c08_cases": sum(row["kind"].startswith("c08_") for row in rows),
    }
