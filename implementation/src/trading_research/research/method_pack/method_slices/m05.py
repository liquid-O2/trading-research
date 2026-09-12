"""M05 SIRES acceptance cases at the C01 production evidence boundary."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from decimal import Decimal

from ..clocks import et_ns
from ..evidence import fixture_document
from ..fixture_utils import method_case


DAY = date(2026, 1, 15)


def _t(hour: int, minute: int, second: int = 0) -> int:
    return et_ns(DAY, hour, minute, second)


# Each qualitative observation is available at the event that actually
# consumes it.  evidence.fixture_document and evidence.score_episode both use
# this map, so an assertion recorded between touch and decision cannot be
# backdated to an earlier SIRES stage.
STAGE_LIMITS = {
    # Common thesis/location gates.
    "thesis_alive": "decision_at",
    "auction_route_ok": "touch_at",
    "branch_regime_allowed": "touch_at",
    "location_fixed": "location_known_at",
    "location_touched": "touch_at",
    "objective_fixed": "decision_at",
    "risk_defined": "decision_at",
    # DOM rejection.
    "arriving_aggression": "aggression_at",
    "little_progress": "rejection_at",
    "local_rejection": "rejection_at",
    "source_dom_confirmation": "rejection_at",
    # Strict absorption/reward/retest.
    "real_extreme": "touch_at",
    "passive_wall_confirmed": "absorption_at",
    "opposing_effort_no_result": "absorption_at",
    "own_reward_confirmed": "reward_at",
    "reward_near_origin": "reward_at",
    "cvd_filter_ok": "confirm_at",
    "fresh_reward_retest_defended": "retest_at",
    # Four-stage STOP.
    "defense": "defense_at",
    "replenishment": "replenish_at",
    "opponent_thinning": "exhaust_at",
    "absorber_aggressive": "liftoff_at",
    "delta_filter_ok": "liftoff_at",
    "lift_off": "liftoff_at",
    # Footprint and VWAP branches.
    "at_valid_level": "level_known_at",
    "candle_delta_disagreement": "absorption_at",
    "local_absorption": "absorption_at",
    "intrabar_poc_flip": "flip_at",
    "source_flow_confirmation": "flip_at",
    "source_vwap_known": "band_known_at",
    "selected_deviation_touched": "touch_at",
    "absorption_at_that_band": "confirm_at",
    "ladder_confirmation": "confirm_at",
    # Aggressive OFM.
    "short_gamma": "touch_at",
    "repeated_effort_no_reward": "catalyst_at",
    "first_squeeze": "first_release_at",
    "squeeze_failed": "failure_at",
    "catalyst_reclaimed": "refill_at",
    "refill_held": "refill_at",
    "initiative_drive": "drive_at",
    "intervening_wicks_taken": "drive_at",
    "drive_retest_defended": "retest_at",
    "own_aggression_rewarded": "retest_at",
    # Passive OFM and clean squeeze.
    "source_squeeze_failed": "failure_at",
    "tape_died_at_failure": "failure_at",
    "no_aggression_at_failure": "failure_at",
    "buyers_area_identified": "failure_at",
    "entry_above_buyers": "entry_trigger_at",
    "stop_below_aggression": "entry_trigger_at",
    "catalyst_known": "catalyst_at",
    "fast_release": "release_at",
    "no_prior_squeeze_failure": "release_at",
    "first_pullback": "pullback_at",
    "opposing_pullback_aggression_absorbed": "pullback_at",
    "continuation_confirmed": "confirm_at",
    # Balance failure, defended band, microbalance, and KG1.
    "long_gamma": "touch_at",
    "balance_context": "touch_at",
    "failed_aggression_at_extreme": "failure_at",
    "left_failed_area": "leave_at",
    "retest_same_failed_area": "retest_at",
    "aggression_still_unrewarded": "retest_at",
    "target_is_prior_opposite_control": "decision_at",
    "prior_band_control": "prior_defense_at",
    "same_band_retest": "retest_at",
    "fresh_same_side_defense": "confirm_at",
    "executed_aggression": "confirm_at",
    "refresh_consistent": "confirm_at",
    "control_side_matches_thesis": "confirm_at",
    "microbalance_frozen": "microbalance_known_at",
    "directional_strength": "breakout_at",
    "breakout_in_thesis_direction": "breakout_at",
    "stop_behind_microbalance": "decision_at",
    "source_kg1_level_known": "level_known_at",
    "kg1_retest": "retest_at",
    "aggression_confirms": "confirm_at",
    # Incomplete source cases.
    "preconfirmation_entry": "decision_at",
    "small_risk_declared": "decision_at",
    "stop_predefined": "decision_at",
    "same_support_band": "decision_at",
    "no_new_buyer_defense": "decision_at",
    "resistance_known_before_approach": "decision_at",
    "upward_approach_loses_aggression": "decision_at",
    "source_refill_return": "decision_at",
    "explicitly_early_entry": "decision_at",
    "source_risk_predefined": "decision_at",
    # Separate management and re-entry units.
    "action_matches_preselected_policy": "action_at",
    "stop_trailed": "action_at",
    "protected_structure_confirmed": "action_at",
    "risk_added": "action_at",
    "earlier_risk_secured": "action_at",
    "thesis_dead": "action_at",
    "exit_or_new_thesis_recorded": "action_at",
    "same_band_id": "decision_at",
    "price_back_inside_band": "fresh_confirmation_at",
    "fresh_confirmation_after_stopout": "fresh_confirmation_at",
    "daily_limit_allows_entry": "decision_at",
}


def _common(branch: str, *, side: str = "short") -> dict:
    return {
        "branch": branch,
        "side": side,
        "instrument_id": "NQ-fixture",
        "band_id": "SIRES-band-109-110",
        "thesis_alive": True,
        "auction_route_ok": True,
        "branch_regime_allowed": True,
        "location_fixed": True,
        "location_touched": True,
        "objective_fixed": True,
        "risk_defined": True,
        "thesis_known_at": _t(9, 20),
        "location_known_at": _t(9, 20),
        "touch_at": _t(9, 40),
        "confirm_at": _t(9, 47),
        "decision_at": _t(9, 48),
    }


def _defended() -> dict:
    op = _common("defended_band_continuation")
    op.update({
        "touch_at": _t(9, 45),
        "prior_band_control": True,
        "same_band_retest": True,
        "fresh_same_side_defense": True,
        "executed_aggression": True,
        "refresh_consistent": True,
        "control_side_matches_thesis": True,
        "prior_defense_at": _t(9, 30),
        "retest_at": _t(9, 45),
        # Literal M05-F1 geometry retained in the evidence payload.
        "band": [Decimal("109"), Decimal("110")],
        "stop_px": Decimal("111"),
        "objective_px": Decimal("103"),
    })
    return op


def _absorption() -> dict:
    op = _common("absorption_reward_retest")
    op.update({
        "real_extreme": True,
        "passive_wall_confirmed": True,
        "opposing_effort_no_result": True,
        "own_reward_confirmed": True,
        "reward_near_origin": True,
        "cvd_filter_ok": True,
        "fresh_reward_retest_defended": True,
        "absorption_at": _t(9, 40),
        "reward_at": _t(9, 42),
        "retest_at": _t(9, 45),
    })
    return op


def _ofm() -> dict:
    op = _common("ofm_aggressive")
    op.update({
        "short_gamma": True,
        "repeated_effort_no_reward": True,
        "first_squeeze": True,
        "squeeze_failed": True,
        "catalyst_reclaimed": True,
        "refill_held": True,
        "initiative_drive": True,
        "intervening_wicks_taken": True,
        "drive_retest_defended": True,
        "own_aggression_rewarded": True,
        "cvd_filter_ok": True,
        "catalyst_at": _t(9, 10),
        "first_release_at": _t(9, 15),
        "failure_at": _t(9, 20),
        "refill_at": _t(9, 30),
        "drive_at": _t(9, 40),
        "retest_at": _t(9, 45),
    })
    return op


def _stop() -> dict:
    op = _common("stop_four_stage")
    op.update({
        "real_extreme": True,
        "defense": True,
        "replenishment": True,
        "opponent_thinning": True,
        "absorber_aggressive": True,
        "delta_filter_ok": True,
        "lift_off": True,
        "reward_ticks": 3,
        "entry_distance_ticks": 1,
        "daily_r_before": -3,
        "defense_at": _t(9, 40),
        "replenish_at": _t(9, 41),
        "exhaust_at": _t(9, 42),
        "liftoff_at": _t(9, 43),
    })
    return op


def _balance() -> dict:
    op = _common("balance_failure_fade")
    op.update({
        "long_gamma": True,
        "balance_context": True,
        "failed_aggression_at_extreme": True,
        "left_failed_area": True,
        "retest_same_failed_area": True,
        "aggression_still_unrewarded": True,
        "target_is_prior_opposite_control": True,
        "failure_at": _t(9, 30),
        "leave_at": _t(9, 35),
        "retest_at": _t(9, 45),
    })
    return op


def _dom() -> dict:
    op = _common("dom_rejection")
    op.update({
        "arriving_aggression": True,
        "little_progress": True,
        "local_rejection": True,
        "source_dom_confirmation": True,
        "aggression_at": _t(9, 40),
        "rejection_at": _t(9, 42),
    })
    return op


def _footprint() -> dict:
    op = _common("footprint_confirmed_reaction")
    op.update({
        "at_valid_level": True,
        "candle_delta_disagreement": True,
        "local_absorption": True,
        "intrabar_poc_flip": True,
        "source_flow_confirmation": True,
        "level_known_at": _t(9, 20),
        "absorption_at": _t(9, 40),
        "flip_at": _t(9, 43),
    })
    return op


def _vwap() -> dict:
    op = _common("vwap_deviation_fade")
    op.update({
        "source_vwap_known": True,
        "selected_deviation_touched": True,
        "absorption_at_that_band": True,
        "cvd_filter_ok": True,
        "ladder_confirmation": True,
        "band_known_at": _t(9, 20),
        "touch_at": _t(9, 40),
        "confirm_at": _t(9, 45),
    })
    return op


def _passive() -> dict:
    op = _common("ofm_passive", side="long")
    op.update({
        "source_squeeze_failed": True,
        "tape_died_at_failure": True,
        "no_aggression_at_failure": True,
        "buyers_area_identified": True,
        "entry_above_buyers": True,
        "stop_below_aggression": True,
        "failure_at": _t(9, 30),
        "entry_trigger_at": _t(9, 45),
    })
    return op


def _clean() -> dict:
    op = _common("clean_squeeze", side="long")
    op.update({
        "catalyst_known": True,
        "fast_release": True,
        "no_prior_squeeze_failure": True,
        "first_pullback": True,
        "opposing_pullback_aggression_absorbed": True,
        "continuation_confirmed": True,
        "catalyst_at": _t(9, 20),
        "release_at": _t(9, 30),
        "pullback_at": _t(9, 40),
        "confirm_at": _t(9, 45),
    })
    return op


def _microbalance() -> dict:
    op = _common("microbalance_break", side="long")
    op.update({
        "microbalance_frozen": True,
        "directional_strength": True,
        "breakout_in_thesis_direction": True,
        "stop_behind_microbalance": True,
        "microbalance_known_at": _t(9, 30),
        "breakout_at": _t(9, 45),
    })
    return op


def _kg1() -> dict:
    op = _common("kg1_retest")
    op.update({
        "source_kg1_level_known": True,
        "kg1_retest": True,
        "aggression_confirms": True,
        "level_known_at": _t(9, 20),
        "retest_at": _t(9, 45),
    })
    return op


def _document(fid: str, predicate: str, op: dict, *, parent: bool = False) -> dict:
    """Build the full C01 document and optionally add an actual parent attempt."""
    doc = fixture_document("SIRES", predicate, fid, op)
    if parent:
        target = doc["candidates"][0]
        parent_id = f"{fid}:parent"
        parent_decision = op.get("parent_decision_at", target["decision_at"])
        parent_doc = fixture_document("SIRES", "sequence", parent_id, {
            "branch": target["branch"],
            "side": target["side"],
            "instrument_id": target["instrument_id"],
            "band_id": target["band_ids"][0],
            "decision_at": parent_decision,
        })
        parent_candidate = parent_doc["candidates"][0]
        parent_candidate["cohort_id"] = "synthetic-fixtures-parent-attempts"
        target["parent_attempt_id"] = parent_id
        doc["candidates"].append(parent_candidate)
        doc["objects"].extend(parent_doc["objects"])
        doc["assertions"].extend(parent_doc["assertions"])
        doc["evidence"].extend(parent_doc["evidence"])
    return doc


def _identity_mutation(fid: str, op: dict) -> dict:
    doc = _document(fid, "sequence", op)
    field = "fresh_same_side_defense"
    aid = doc["candidates"][0]["operands"][field]["assertion_id"]
    assertion = next(row for row in doc["assertions"] if row["assertion_id"] == aid)
    assertion["band_id"] = "foreign-band"
    for eid in assertion["evidence_ids"]:
        next(row for row in doc["evidence"] if row["evidence_id"] == eid)["band_id"] = "foreign-band"
    return doc


def _late_mutation(fid: str, op: dict) -> dict:
    doc = _document(fid, "sequence", op)
    field = "prior_band_control"
    aid = doc["candidates"][0]["operands"][field]["assertion_id"]
    assertion = next(row for row in doc["assertions"] if row["assertion_id"] == aid)
    late = _t(9, 31)
    assertion.update(observation_start=late, observation_end=late, known_at=late)
    for eid in assertion["evidence_ids"]:
        next(row for row in doc["evidence"] if row["evidence_id"] == eid).update(
            observation_start=late, observation_end=late, known_at=late
        )
    return doc


def _missing_mutation(fid: str, op: dict) -> dict:
    doc = _document(fid, "sequence", op)
    del doc["candidates"][0]["operands"]["refresh_consistent"]
    return doc


def _stale_defense_mutation(fid: str, op: dict) -> dict:
    """Bind the claimed fresh defense to the actual 09:30 prior evidence."""
    doc = _document(fid, "sequence", op)
    assertions = {row["field"]: row for row in doc["assertions"]}
    assertions["fresh_same_side_defense"]["evidence_ids"] = list(
        assertions["prior_band_control"]["evidence_ids"]
    )
    return doc


def _stale_reentry_mutation(fid: str, op: dict) -> dict:
    """Keep claimed current values while supplying only pre-exit observations."""
    doc = _document(fid, "reentry", op, parent=True)
    assertions = {
        row["field"]: row for row in doc["assertions"]
        if row["candidate_id"] == fid
    }
    stale_at = _t(9, 47)
    for field in ("fresh_same_side_defense", "fresh_confirmation_after_stopout"):
        assertion = assertions[field]
        assertion.update(observation_start=stale_at, observation_end=stale_at, known_at=stale_at)
        for eid in assertion["evidence_ids"]:
            evidence = next(row for row in doc["evidence"] if row["evidence_id"] == eid)
            evidence.update(observation_start=stale_at, observation_end=stale_at, known_at=stale_at)
    return doc


def _case(branch: str) -> dict:
    if branch == "pre_file_early":
        return {"branch": branch, "side": "long", "decision_at": _t(9, 40),
                "thesis_alive": True, "preconfirmation_entry": True,
                "small_risk_declared": True, "stop_predefined": True}
    if branch == "third_retest_case":
        return {"branch": branch, "side": "short", "decision_at": _t(10, 1),
                "same_support_band": True, "distinct_test_count": 3,
                "no_new_buyer_defense": True, "risk_defined": True}
    if branch == "late_resistance_fade_case":
        return {"branch": branch, "side": "short", "decision_at": _t(14, 5),
                "resistance_known_before_approach": True,
                "upward_approach_loses_aggression": True, "small_risk_declared": True}
    return {"branch": branch, "side": "long", "decision_at": _t(9, 40),
            "source_refill_return": True, "explicitly_early_entry": True,
            "source_risk_predefined": True}


def audit_candidate(candidate, operands, objects, assertions, evidence) -> list[dict]:
    """Audit SIRES relationships that are identities rather than SQL values."""
    findings: list[dict] = []
    parent = candidate.get("parent_record")
    if candidate["predicate"] == "reentry" and parent is not None:
        actual_same_band = parent["band_ids"] == candidate["band_ids"]
        claimed_same_band = operands.get("same_band_id")
        if claimed_same_band is not None and claimed_same_band != actual_same_band:
            findings.append({"field": "same_band_id", "kind": "identity",
                             "reason": "same_band_id disagrees with the actual parent/current band IDs",
                             "recipe_id": "O144"})
        if operands.get("fresh_confirmation_after_stopout") is True:
            prior_exit = operands.get("prior_exit_at")
            fresh = operands.get("fresh_confirmation_at")
            if prior_exit is None or fresh is None:
                findings.append({"field": "fresh_confirmation_at",
                                 "kind": "supplied_record_missing", "unknown": True,
                                 "reason": "fresh confirmation needs actual prior-exit and confirmation records",
                                 "recipe_id": "O144"})

            for field in ("touch_at", "retest_at", "fresh_confirmation_at"):
                when = operands.get(field)
                if prior_exit is not None and (when is None or when <= prior_exit):
                    findings.append({"field": field, "kind": "ordering",
                                     "reason": f"current {field} must follow the actual prior exit",
                                     "recipe_id": "O144"})

            fresh_binding = candidate["operands"].get("fresh_confirmation_after_stopout", {})
            fresh_assertion = assertions.get(fresh_binding.get("assertion_id"), {})
            if (prior_exit is not None and fresh_assertion
                    and fresh_assertion.get("observation_end") is not None
                    and fresh_assertion["observation_end"] <= prior_exit):
                findings.append({"field": "fresh_confirmation_after_stopout", "kind": "ordering",
                                 "reason": "reentry freshness assertion was observed before the actual prior exit",
                                 "recipe_id": "O144"})

    if candidate["predicate"] in {"sequence", "reentry"} and candidate["branch"] == "defended_band_continuation":
        prior_binding = candidate["operands"].get("prior_band_control", {})
        fresh_binding = candidate["operands"].get("fresh_same_side_defense", {})
        prior = assertions.get(prior_binding.get("assertion_id"), {})
        fresh = assertions.get(fresh_binding.get("assertion_id"), {})
        if prior and fresh and set(prior.get("evidence_ids", ())) & set(fresh.get("evidence_ids", ())):
            findings.append({"field": "fresh_same_side_defense", "kind": "identity",
                             "reason": "fresh confirmation reuses the prior-defense evidence ID",
                             "recipe_id": "O130"})
        if (operands.get("fresh_same_side_defense") is True and fresh
                and fresh.get("observation_end") is not None
                and operands.get("retest_at") is not None
                and fresh["observation_end"] <= operands["retest_at"]):
            findings.append({"field": "fresh_same_side_defense", "kind": "ordering",
                             "reason": "claimed fresh defense was not observed after the current retest",
                             "recipe_id": "O130"})
    return findings


def method_fixtures() -> list[dict]:
    rows: list[dict] = []

    defended = _defended()
    rows.append(method_case("SIRES", "sequence", "M05-F1", _document("M05-F1", "sequence", defended), "pass"))

    # Every confirmed branch receives a complete positive algebra case with
    # its literal fields and strict stage ordering bound through C01 records.
    for suffix, op in (
        ("dom", _dom()),
        ("absorption", _absorption()),
        ("stop", _stop()),
        ("footprint", _footprint()),
        ("vwap", _vwap()),
        ("ofm", _ofm()),
        ("ofm-passive", _passive()),
        ("clean-squeeze", _clean()),
        ("balance-fade", _balance()),
        ("microbalance", _microbalance()),
        ("kg1", _kg1()),
    ):
        fid = f"M05-F1-{suffix}"
        rows.append(method_case("SIRES", "sequence", fid, _document(fid, "sequence", op), "pass"))

    stale = _defended()
    rows.append(method_case("SIRES", "sequence", "M05-F2-stale-confirm",
                            _stale_defense_mutation("M05-F2-stale-confirm", stale), "fail"))

    omit = _ofm()
    omit.update(first_squeeze=False, squeeze_failed=False, refill_held=False)
    rows.append(method_case("SIRES", "sequence", "M05-F2-ofm-omit",
                            _document("M05-F2-ofm-omit", "sequence", omit), "fail"))
    early = _ofm()
    early["decision_at"] = _t(9, 39)
    rows.append(method_case("SIRES", "sequence", "M05-F2-ofm-early",
                            _document("M05-F2-ofm-early", "sequence", early), "fail"))

    no_reward = _absorption()
    no_reward.update(own_reward_confirmed=False, fresh_reward_retest_defended=False)
    rows.append(method_case("SIRES", "sequence", "M05-F2-absorption",
                            _document("M05-F2-absorption", "sequence", no_reward), "fail"))

    stop_at_limit = _stop()
    stop_at_limit["daily_r_before"] = -4
    rows.append(method_case("SIRES", "sequence", "M05-F2-stop-r",
                            _document("M05-F2-stop-r", "sequence", stop_at_limit), "fail"))

    # own_reward_confirmed is deliberately absent: the long-gamma fade body
    # does not consume it and the binder marks it not_required.
    fade = _balance()
    rows.append(method_case("SIRES", "sequence", "M05-F2-fade-no-own-reward",
                            _document("M05-F2-fade-no-own-reward", "sequence", fade), "pass"))

    holes = []
    refresh = _defended(); refresh["refresh_consistent"] = None
    holes.append(("M05-F3-refresh", refresh))
    cvd = _absorption(); cvd["cvd_filter_ok"] = None
    holes.append(("M05-F3-cvd", cvd))
    depth = _common("dom_rejection")
    depth.update(arriving_aggression=True, little_progress=True, local_rejection=True,
                 source_dom_confirmation=None, aggression_at=_t(9, 40), rejection_at=_t(9, 42))
    holes.append(("M05-F3-depth", depth))
    gamma = _ofm(); gamma["short_gamma"] = None
    holes.append(("M05-F3-gamma", gamma))
    kg1 = _common("kg1_retest")
    kg1.update(source_kg1_level_known=None, kg1_retest=True, aggression_confirms=True,
               level_known_at=_t(9, 20), retest_at=_t(9, 45))
    holes.append(("M05-F3-kg1", kg1))
    death = _defended(); death["thesis_alive"] = None
    holes.append(("M05-F3-thesis-death", death))
    for fid, op in holes:
        rows.append(method_case("SIRES", "sequence", fid, _document(fid, "sequence", op), "unknown"))

    # C08 mutations exercise real C01 observation times and identities.
    rows.append(method_case("SIRES", "sequence", "M05-F1:late",
                            _late_mutation("M05-F1:late", defended),
                            {"verdict": "fail", "detected_causal_violations": 2}, kind="c08_late"))
    rows.append(method_case("SIRES", "sequence", "M05-F1:missing",
                            _missing_mutation("M05-F1:missing", defended), "unknown", kind="c08_missing"))
    rows.append(method_case("SIRES", "sequence", "M05-F1:identity",
                            _identity_mutation("M05-F1:identity", defended), "fail", kind="c08_identity"))

    # Incomplete descriptions remain their own predicate and cohort kind.
    for branch in ("pre_file_early", "third_retest_case", "late_resistance_fade_case", "ofm_early_refill_case"):
        fid = f"M05-case-{branch}"
        rows.append(method_case("SIRES", "case_description", fid,
                                _document(fid, "case_description", _case(branch)), "pass",
                                kind="case_description"))

    management = {
        "branch": "defended_band_continuation", "side": "short",
        "instrument_id": "NQ-fixture", "band_id": "SIRES-band-109-110",
        "decision_at": _t(9, 48), "parent_decision_at": _t(9, 48),
        "action_at": _t(9, 55), "action_matches_preselected_policy": True,
        "supporting_structure_known_at": _t(9, 54), "stop_trailed": True,
        "protected_structure_confirmed": True, "risk_added": False,
        "earlier_risk_secured": True, "thesis_dead": False,
        "exit_or_new_thesis_recorded": False,
    }
    rows.append(method_case("SIRES", "management", "M05-management-pass",
                            _document("M05-management-pass", "management", management, parent=True),
                            "pass", kind="management"))
    bad_management = deepcopy(management)
    bad_management["protected_structure_confirmed"] = False
    rows.append(method_case("SIRES", "management", "M05-management-unprotected",
                            _document("M05-management-unprotected", "management", bad_management, parent=True),
                            "fail", kind="management"))

    reentry = _defended()
    reentry.update(decision_at=_t(10, 0), touch_at=_t(9, 57), confirm_at=_t(9, 59),
                   retest_at=_t(9, 57),
                   fresh_same_side_defense=True, prior_exit_at=_t(9, 50),
                   fresh_confirmation_at=_t(9, 59), same_band_id=True,
                   price_back_inside_band=True, fresh_confirmation_after_stopout=True,
                   daily_limit_allows_entry=True, parent_decision_at=_t(9, 48))
    rows.append(method_case("SIRES", "reentry", "M05-reentry-pass",
                            _document("M05-reentry-pass", "reentry", reentry, parent=True),
                            "pass", kind="reentry"))
    reused = deepcopy(reentry)
    rows.append(method_case("SIRES", "reentry", "M05-reentry-reused",
                            _stale_reentry_mutation("M05-reentry-reused", reused),
                            "fail", kind="reentry"))
    return rows


def semantic_audit() -> dict:
    """Machine-readable checks used by the M05 integration tests/report audit."""
    rows = method_fixtures()
    return {
        "fixture_count": len(rows),
        "all_pass": all(row["status"] == "pass" for row in rows),
        "predicates": sorted({row["predicate"] for row in rows}),
        "case_descriptions": sum(row["kind"] == "case_description" for row in rows),
        "management_cases": sum(row["kind"] == "management" for row in rows),
        "reentry_cases": sum(row["kind"] == "reentry" for row in rows),
    }
