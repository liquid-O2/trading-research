"""Identified synthetic fixtures for local flow, branch, and lifecycle audits.

The original compact fixtures often supplied only conclusions or scalar
summaries.  These replacements attach explicit synthetic record identities,
event clocks, coverage, and policy definitions so a positive fixture exercises
the reviewed producer rather than a compatibility shortcut.
"""

from copy import deepcopy
from decimal import Decimal


def _checks(*names, false=()):
    return {name: name not in set(false) for name in names}


def _trade(fid, index, at, *, price=100, size=1, side="B", **extra):
    return {"event_id": f"{fid}:trade:{index}", "event_ns": at, "known_at": at,
            "price": Decimal(str(price)), "size": size, "side": side,
            "action": "T", "instrument_id": "fixture-contract", **extra}


def install(fixtures):
    for spec in fixtures:
        if spec.get("_completion_flow_v2"):
            continue
        fid, rid = spec["id"], spec["recipe"]
        inp, expected = spec["inputs"], spec["expected"]
        known = inp.get("known_at", inp.get("use_at", 100))
        use = inp.get("use_at", known)

        if rid == "O098":
            for index, row in enumerate(inp.get("events", [])):
                if str(row.get("action", "T")).upper() == "T":
                    row.update(event_id=f"{fid}:trade:{index}", event_ns=known-index,
                               known_at=known-index, price=row.get("price", 100),
                               instrument_id="fixture-contract")
            inp["coverage_ok"] = True
        elif rid == "O099":
            rows = inp.get("trades", [])
            for index, row in enumerate(rows):
                row.update(event_id=f"{fid}:trade:{index}", event_ns=known-len(rows)+index,
                           known_at=known-len(rows)+index, price=row.get("price", 100),
                           side=row.get("side", "B"), instrument_id="fixture-contract")
            inp["source_setting"] = {"setting_id": f"{fid}:setting",
                "threshold": inp["threshold"], "comparator": ">=",
                "aggregation_mode": inp.get("mode", "per_print")}
        elif fid in {"O100-F1", "O100-F1b"}:
            q0, q1 = known-3, known-1
            inp.update(band=[100, 100], reset_at=known-4, depth_coverage="bbo",
                       execution_coverage_ok=True, defense_interpretation=None,
                       quotes=[{"quote_id": f"{fid}:quote:0", "at": q0, "known_at": q0,
                                "bid": 100, "ask": Decimal("100.25"), "bid_size": 10, "ask_size": 9},
                               {"quote_id": f"{fid}:quote:1", "at": q1, "known_at": q1,
                                "bid": 100, "ask": Decimal("100.25"), "bid_size": 15, "ask_size": 9}],
                       events=[])
            if fid.endswith("F1b"):
                inp["events"] = [_trade(fid, 0, known-2, price=100, size=4, side="A")]
        elif fid == "O102-F1":
            inp.update(price=100, passive_side="bid", hold=True,
                       consumption_events=[{"event_id": f"{fid}:consume", "at": known-2,
                                            "known_at": known-2, "price": 100, "size": 6}],
                       refresh_events=[{"event_id": f"{fid}:refresh", "at": known-1,
                                        "known_at": known-1, "price": 100, "size": 8}],
                       first_display=10, last_display=12)
            inp.pop("lifecycle", None)
        elif fid == "O116-F1":
            inp.update(zone_id=f"{fid}:zone", source_setting_id=f"{fid}:setting",
                       instrument_id="fixture-contract", formation_event_ids=[f"{fid}:formation"],
                       departure_event_id=f"{fid}:departure",
                       source_setting={"instrument_id": "fixture-contract", "threshold": 100},
                       threshold=100)
            for index, row in enumerate(inp["touches"]):
                row.update(touch_id=f"{fid}:touch:{index}", instrument_id="fixture-contract")
        elif fid == "O118-F1":
            inp.update(origin_id=f"{fid}:origin", side="long",
                       stage_ledger={"release": inp["release_at"], "failure": inp["failure_at"],
                                     "refill": inp["failure_at"]+1, "drive": inp["failure_at"]+2,
                                     "hold": inp["failure_at"]+3, "retest": inp["failure_at"]+4,
                                     "reward": inp["failure_at"]+5, "entry": inp["failure_at"]+6})
            expected.update(linked=True, branch_ok=True)
        elif fid == "O120-F1":
            inp.update(tick_size=1, candle_id=f"{fid}:candle", instrument_id="fixture-contract",
                       formation_start=known-3, formation_end=known, as_of=known, coverage_ok=True,
                       events=[_trade(fid, 0, known-2, price=100, size=3, side="B", candle_id=f"{fid}:candle"),
                               _trade(fid, 1, known-1, price=100, size=8, side="A", candle_id=f"{fid}:candle")])
            inp.pop("body_rows", None)
        elif rid == "O121":
            inp.update(branch_id=f"{fid}:branch", band_id=f"{fid}:band", side="long",
                       checks=_checks("arriving_aggression", "little_progress", "local_rejection", "source_dom_confirmation"),
                       added_participation=True)
            if fid.endswith("F1c"):
                inp["checks"]["source_dom_confirmation"] = None
                inp["added_participation"] = None
        elif rid == "O122":
            names=("passive_wall_confirmed","opposing_effort_no_result","own_reward_confirmed",
                   "reward_near_origin","fresh_reward_retest_defended","cvd_filter_ok","delta_filter_ok")
            inp.update(branch_id=f"{fid}:branch", band_id=f"{fid}:band", side="long",
                       checks=_checks(*names))
            if fid.endswith("F1b"):
                a, b, d = inp["absorption_at"], inp["reward_at"], inp["defense_at"]
                inp.update(return_at=b+1, decision_at=d+1)
                inp["checks"]["fresh_reward_retest_defended"] = False
            elif fid.endswith("F1c"):
                inp["checks"]["cvd_filter_ok"] = None
        elif rid == "O123":
            inp.update(branch_id=f"{fid}:branch", band_id=f"{fid}:band", side="long",
                       stage_ledger={"defense": known-5, "replenishment": known-4,
                                     "exhaustion": known-3, "liftoff": known-2, "decision": use},
                       checks=_checks("defense", "replenishment", "opponent_thinning",
                                      "absorber_aggressive", "lift_off"))
        elif rid == "O124":
            inp.update(branch_id=f"{fid}:branch", candle_id=inp.get("disagreement_candle"),
                       footprint_snapshot_ids=[f"{fid}:snapshot:0", f"{fid}:snapshot:1"],
                       checks=_checks("candle_delta_disagreement", "local_absorption",
                                      "intrabar_poc_flip", "source_flow_confirmation"))
            if fid.endswith("F1c"):
                inp["checks"]["source_flow_confirmation"] = None
        elif rid == "O125":
            inp.update(branch_id=f"{fid}:branch", side="short", selected_band="upper",
                       vwap_snapshot_id=f"{fid}:vwap", band_snapshot_id=f"{fid}:band",
                       target_snapshot_id=f"{fid}:target", band_known_at=known,
                       checks=_checks("source_vwap_known", "selected_deviation_touched",
                                      "absorption_at_that_band", "ladder_confirmation"))
            if fid.endswith("F1b"):
                inp["checks"]["ladder_confirmation"] = None
        elif rid == "O126":
            inp.update(branch_id=f"{fid}:branch", origin_id=f"{fid}:origin", side="long")
            names=("repeated_effort_no_reward","first_squeeze","squeeze_failed","catalyst_reclaimed",
                   "refill_held","initiative_drive","intervening_wicks_taken",
                   "drive_retest_defended","own_aggression_rewarded","cvd_filter_ok")
            inp["checks"] = _checks(*names)
            inp["stage_ledger"] = {"catalyst":inp["catalyst_at"],"first_release":inp["release_at"],
                "failure":inp["failure_at"],"refill":inp["refill_at"],"drive":inp["drive_at"],
                "drive_retest":inp["retest_at"],"reward":inp["retest_at"]+1,"decision":inp["entry_at"]}
            if fid.endswith("F1c"): inp["checks"]["cvd_filter_ok"] = None
        elif rid == "O128":
            inp.update(branch_id=f"{fid}:branch", origin_id=f"{fid}:origin", side="long",
                       failure_history={"coverage_complete":True,"events":[]},
                       checks=_checks("catalyst_known","fast_release",
                                      "opposing_pullback_aggression_absorbed","continuation_confirmed"))
            if fid.endswith("F1b"):
                inp.update(catalyst_at=known-5, release_at=known-4, confirm_at=known-1)
        elif rid == "O129":
            inp.update(branch_id=f"{fid}:branch", balance_id=f"{fid}:balance",
                       failed_area_id=f"{fid}:failed-area", target_id=f"{fid}:target", side="short",
                       checks=_checks("balance_context","failed_aggression_at_extreme","left_failed_area",
                                      "retest_same_failed_area","aggression_still_unrewarded",
                                      "target_is_prior_opposite_control"))
        elif rid == "O130":
            inp.update(branch_id=f"{fid}:branch", thesis_id=f"{fid}:thesis",
                       band_id=f"{fid}:band", side="short", retest_at=inp["fresh_defense_at"]-1,
                       checks=_checks("prior_band_control","same_band_retest","fresh_same_side_defense",
                                      "executed_aggression","refresh_consistent","control_side_matches_thesis"))
            if fid.endswith("F1b"): inp["checks"]["control_side_matches_thesis"] = False
        elif rid == "O131":
            inp.update(branch_id=f"{fid}:branch", microbalance_id=f"{fid}:microbalance",
                       target_id=f"{fid}:target", side=inp.get("side", "long"),
                       microbalance_frozen=True, directional_strength=True,
                       breakout_in_thesis_direction=True,
                       target_known_at=inp.get("complete_at", known)-2,
                       stage_ledger={"target_known":inp.get("complete_at", known)-2,
                                     "microbalance_known":inp.get("complete_at", known)-1,
                                     "breakout":inp.get("complete_at", known),"decision":use})
        elif rid == "O132":
            inp.update(branch_id=f"{fid}:branch", kg1_level_id=f"{fid}:kg1", side="long",
                       stage_ledger={"kg1_known":known-4,"retest":known-3,
                                     "confirmation":known-2,"decision":known-1})
        elif rid == "O133":
            inp.update(branch_id=f"{fid}:branch", case_id=f"{fid}:case", thesis_id=f"{fid}:thesis",
                       risk_declared_at=inp["entry_at"]-2, early_choice_at=inp["entry_at"]-1,
                       checks=_checks("thesis_alive","preconfirmation_entry","small_risk_declared",
                                      "stop_predefined","explicitly_early_entry","source_refill_return",
                                      "source_risk_predefined"))
        elif rid == "O134":
            tests=inp.pop("tests")
            inp.update(branch_id=f"{fid}:branch", case_id=f"{fid}:case", band_id=f"{fid}:band",
                       no_new_buyer_defense=True,
                       test_episodes=[{"test_id":f"{fid}:test:{index}","return_at":at,
                                       "departure_at":at+1,"band_id":f"{fid}:band"}
                                      for index,at in enumerate(tests)])
        elif rid == "O135" and not fid.endswith("F1b"):
            inp.update(branch_id=f"{fid}:branch", case_id=f"{fid}:case",
                       resistance_id=f"{fid}:resistance", side="short", small_risk=True,
                       source_exhaustion=True, session_end_at=inp["entry_at"]+10,
                       approach_events=[{"event_id":f"{fid}:approach:0","at":inp["entry_at"]-2,"price":109},
                                        {"event_id":f"{fid}:approach:1","at":inp["entry_at"]-1,"price":110}])
        elif rid == "O136":
            inp.update(support_event_id=f"{fid}:support", candidate_side=inp.get("direction"),
                       linked_candidate_ids=[f"{fid}:candidate"])
        elif rid == "O138" and not fid.endswith("F1b"):
            inp.update(thesis_id=f"{fid}:thesis", declared_at=known-10, decision_at=use,
                       death_conditions=[{"condition_id":f"{fid}:close-rule","comparator":"<",
                                          "threshold":inp["death_close"],"coverage_complete":True}],
                       events=[{"event_id":f"{fid}:close","condition_id":f"{fid}:close-rule",
                                "value":inp["close"],"at":inp["close_at"],"known_at":inp["close_at"]}])
        elif rid == "O144":
            fresh = inp.get("fresh_confirm_at", inp.get("reused_confirm_at"))
            permitted = inp.get("daily_r", -3) > inp.get("daily_cap", -4)
            inp.update(parent_entry_id=f"{fid}:entry", parent_position_id=f"{fid}:position",
                       parent_exit_id=f"{fid}:exit", parent_exit_at=inp["prior_exit_at"],
                       new_candidate_id=f"{fid}:candidate", parent_thesis_id=f"{fid}:thesis",
                       new_thesis_id=f"{fid}:thesis", parent_band_id=f"{fid}:band",
                       new_band_id=f"{fid}:band", fresh_confirmation_at=fresh,
                       decision_at=inp["entry_at"], full_branch_verdict=True,
                       account_permission=permitted, thesis_state="alive")
        elif rid == "O145":
            results=inp.pop("results_r")
            inp.update(source_id="fixture-source",account_id="fixture-account",session_id="fixture-session",
                       policy_id=f"{fid}:policy",decision_at=use,session_finished=False,
                       source_policy={"source_id":"fixture-source","account_id":"fixture-account",
                                      "session_id":"fixture-session","policy_id":f"{fid}:policy",
                                      "limit_r":inp["limit_r"],"frozen_at":known-10,
                                      "r_definition_id":f"{fid}:original-r",
                                      "prior_ledger_coverage_complete":True},
                       result_records=[{"result_id":f"{fid}:result:{index}","result_r":value,
                                        "close_at":known-len(results)+index-1,
                                        "available_at":known-len(results)+index,
                                        "r_definition_id":f"{fid}:original-r",
                                        "source_id":"fixture-source","account_id":"fixture-account",
                                        "session_id":"fixture-session","policy_id":f"{fid}:policy"}
                                       for index,value in enumerate(results)])
        elif rid == "O146":
            eligible=list(inp.get("eligible", [])); supplied=inp.get("journal", {})
            rows=[]
            for index,candidate in enumerate(eligible):
                if candidate not in supplied: continue
                decision=known-20+index
                rows.append({"candidate_id":candidate,"decision_at":decision,"feature_known_at":decision-1,
                    "thesis_id":f"{candidate}:thesis","reason":"fixture reason","confidence":3,
                    "context":"balance","regime":"regular","session_start_at":decision-1,
                    "confidence_known_at":decision-1,"input_record_id":f"{candidate}:input",
                    "outcome_record_id":f"{candidate}:outcome","outcome":supplied[candidate],
                    "outcome_at":decision+1,"known_at":decision+1})
            inp.update(process_version="fixture-v1",process_config={
                "required_pre_entry_fields":["thesis_id","reason","confidence","context","regime"],
                "confidence":{"min":1,"max":5},"review":{"example_sessions":30}},
                eligible_ids=eligible,journal_rows=rows)
        elif rid == "O150":
            placed=inp["placed_at"]
            inp.update(order_id=f"{fid}:order",candidate_id=f"{fid}:candidate",
                       position_id=f"{fid}:position",order_type="limit",use_at=placed+3,known_at=placed+3,
                       source_policy={"policy_id":f"{fid}:policy","stop_ticks":inp["stop_ticks"],
                                      "target_ticks":inp["target_ticks"],"cancel_minutes":inp["cancel_minutes"],
                                      "one_position_at_a_time":True},other_open_positions=0,
                       order_events=[{"event_id":f"{fid}:fill:0","kind":"fill","qty":1,"at":placed+1},
                                     {"event_id":f"{fid}:fill:1","kind":"fill","qty":1,"at":placed+2}])
            inp.pop("fill_qtys", None)
        elif rid == "O151":
            inp.update(order_id=f"{fid}:order", fill_convention="first later print through limit",
                       queue_evidence=False, source_policy={"policy_id":f"{fid}:policy"})
            for index,row in enumerate(inp.get("trades", [])):
                row.update(event_id=f"{fid}:trade:{index}", known_at=row["t"])
        elif rid == "O152":
            inp.update(account_fees=[], account_fees_separate=True)
        elif rid == "O155":
            inp.setdefault("validated_process", True)
            inp.setdefault("risk_stage", "first")
        elif rid == "O156":
            inp.setdefault("scenario_id", f"{fid}:scenario")
            inp.setdefault("path_design", {"kind":"supplied synthetic paths"})
            inp.setdefault("trailing_drawdown_rule", "supplied fixture rule")
            inp.setdefault("consistency_rule", "supplied fixture rule")
            inp.setdefault("source_causal_status", "corrected")
        elif rid == "O165":
            criteria=[]
            for name in ("high_aggression","low_response_efficiency","opposite_liquidity_holds_and_refills"):
                criteria.append({"criterion_id":f"{fid}:{name}","criterion":name,
                                 "observed":inp[name],"known_at":known,
                                 "instrument_id":inp["source_symbol"]})
            inp.update(criteria=criteria,evidence=[{"evidence_id":f"{fid}:evidence","known_at":known}])
        elif rid == "O166":
            state_at,next_at=inp["state_at"],inp["next_state_at"]
            inp.update(cadence={"kind":"fixed","interval":next_at-state_at},
                       current_observation={"state_id":f"{fid}:state:0","state_label":inp["from_state"],
                         "state_at":state_at,"known_at":state_at,"sequence":1,"instrument_id":inp["source_symbol"],
                         "cohort_id":inp["cohort_id"],"reset_id":f"{fid}:reset"},
                       next_observation={"state_id":f"{fid}:state:1","state_label":inp["to_state"],
                         "state_at":next_at,"known_at":next_at,"sequence":2,"instrument_id":inp["source_symbol"],
                         "cohort_id":inp["cohort_id"],"reset_id":f"{fid}:reset"},
                       conditioning_evidence=[{"evidence_id":f"{fid}:conditioning",
                                               "known_at":inp["conditioning_known_at"]}])

        spec["_completion_flow_v2"] = True


__all__ = ["install"]
