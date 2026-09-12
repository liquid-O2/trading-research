"""Source-specific execution sequences for O121--O136.

These producers audit already selected source cases and native observations.
They do not discover trades or fill unpublished selectors.  Every required
stage retains its identity and event time; an absent stage is unknown unless a
fully covered admitted attempt observed that the event did not occur.
"""

from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from functools import wraps
from typing import Any, Callable, Iterable

from trading_research.research.method_pack.contracts import OutputField
from trading_research.research.method_pack.logic import dec, kleene_and
from trading_research.research.method_pack.protocol import RecipeResult, guard


FLOW_SEQUENCE_SCHEMAS: dict[str, tuple[str, ...]] = {
    "O121": ("branch_id", "band_id", "band", "side", "stage_ledger", "arriving_aggression", "little_progress", "local_rejection", "source_dom_confirmation", "added_participation", "evidence", "order_ok", "branch_ok"),
    "O122": ("branch_id", "band_id", "support", "side", "stage_ledger", "passive_wall_confirmed", "opposing_effort_no_result", "own_reward_confirmed", "reward_near_origin", "fresh_reward_retest_defended", "cvd_filter_ok", "delta_filter_ok", "reward_price", "return_price", "reward_and_retest_distinct", "strict_reversal_sequence", "branch_ok"),
    "O123": ("branch_id", "band_id", "side", "stage_ledger", "defense", "replenishment", "opponent_thinning", "absorber_aggressive", "lift_off", "reward_ticks", "distance_ticks", "entry_distance_ticks", "reward_gate_ok", "entry_gate_ok", "daily_r_before", "daily_stop_ok", "geometry_ok", "stage_evidence_ok", "branch_ok", "size_halved_repairs"),
    "O124": ("branch_id", "candle_id", "footprint_snapshot_ids", "same_candle", "stage_ledger", "candle_delta_disagreement", "local_absorption", "intrabar_poc_flip", "source_flow_confirmation", "poc_from", "poc_to", "route_ok", "branch_ok"),
    "O125": ("branch_id", "side", "vwap_snapshot_id", "band_snapshot_id", "band_known_at", "selected_band", "selected_band_price", "target_snapshot_id", "target", "upper", "lower", "stage_ledger", "source_vwap_known", "selected_deviation_touched", "absorption_at_that_band", "ladder_confirmation", "confirmation", "later_vwap", "later_rewrites_target", "order_ok", "branch_ok"),
    "O126": ("branch_id", "origin_id", "side", "stage_ledger", "repeated_effort_no_reward", "first_squeeze", "squeeze_failed", "catalyst_reclaimed", "refill_held", "initiative_drive", "intervening_wicks_taken", "drive_retest_defended", "own_aggression_rewarded", "cvd_filter_ok", "short_gamma", "sequence_ok", "branch_ok"),
    "O127": ("branch_id", "side", "buyers_area_id", "buyers_area", "entry", "stop", "initial_risk", "r_multiple", "r2", "r_in_1_to_3", "stage_ledger", "source_squeeze_failed", "tape_died_at_failure", "no_aggression_at_failure", "buyers_area_identified", "entry_above_buyers", "stop_below_aggression", "qualification", "automatic_selector", "branch_ok"),
    "O128": ("branch_id", "origin_id", "side", "stage_ledger", "catalyst_known", "fast_release", "first_pullback", "no_prior_failure", "failure_history_complete", "prior_failure_ids", "opposing_pullback_aggression_absorbed", "continuation_confirmed", "later_failure_invalidates", "later_failure_at", "order_ok", "branch_ok"),
    "O129": ("branch_id", "balance_id", "band", "side", "failed_area_id", "stage_ledger", "balance_context", "long_gamma", "failed_aggression_at_extreme", "left_failed_area", "retest_same_failed_area", "aggression_still_unrewarded", "target", "target_id", "target_is_balance_low", "target_is_prior_opposite_control", "requires_lift", "order_ok", "branch_ok"),
    "O130": ("branch_id", "thesis_id", "band_id", "band", "side", "stage_ledger", "prior_band_control", "same_band_retest", "fresh_same_side_defense", "executed_aggression", "refresh_consistent", "control_side_matches_thesis", "short_control", "old_defense_keeps_control", "prior_defense_at", "fresh_defense_at", "branch_ok"),
    "O131": ("branch_id", "microbalance_id", "micro_low", "micro_high", "width", "side", "stage_ledger", "microbalance_frozen", "directional_strength", "breakout_in_thesis_direction", "stop", "stop_side_ok", "stop_below_opposite", "target", "target_id", "objective_preexists", "preexisting_target", "qualifies", "automatic_selector", "branch_ok"),
    "O132": ("branch_id", "kg1_level_id", "kg1_known", "side", "stage_ledger", "retest_at", "confirm_at", "entry_sequence", "entry", "stop", "target", "initial_reward_to_risk", "ratio", "original_risk", "later_reward_to_risk", "later_ratio", "management_records", "automatic_trailing", "branch_ok"),
    "O133": ("branch_id", "case_id", "thesis_id", "stage_ledger", "thesis_alive", "preconfirmation_entry", "small_risk_declared", "stop_predefined", "explicitly_early_entry", "source_refill_return", "source_risk_predefined", "case_fidelity", "deliberate_early", "full_confirmed_branch_pass", "confirmed_branch", "thesis_killed_by_loss_alone", "automatic_early_admission", "automatic_selector"),
    "O134": ("branch_id", "case_id", "band_id", "test_ids", "distinct_test_count", "current_test_ordinal", "ordinal", "inside_rows_are_one_test", "same_support_band", "no_new_buyer_defense", "case_fidelity", "in_cohort", "stopped_out", "universal_third_touch", "automatic_entry_selector"),
    "O135": ("branch_id", "case_id", "resistance_id", "resistance", "resistance_known", "approach_at", "source_exhaustion", "side", "small_risk", "short_case_fidelity", "case_ok", "session_end_at", "automatic_entry_selector", "automatic_full_trigger"),
    "O136": ("bias_recorded", "bias_side", "bias_start", "bias_known_at", "origin_reference_id", "support_event_id", "revision_history", "linked_candidate_ids", "direction", "candidate_side", "later_event_explains_bias", "later_event_at", "automatic_bias_selector"),
}


LEGACY_REQUIRED = {
    "O121": ("band",), "O122": ("support",), "O123": ("origin", "confirm_px", "entry"),
    "O124": ("disagreement_candle", "poc_candle"), "O125": ("vwap", "sigma"),
    "O126": ("catalyst_at", "release_at", "failure_at", "refill_at", "drive_at", "retest_at", "entry_at"),
    "O127": ("entry", "stop"), "O128": ("first_pullback_at", "entry_at"),
    "O129": ("lo", "hi"), "O130": ("lo", "hi"),
    "O131": ("micro_lo", "micro_hi", "entry", "stop"),
    "O132": ("entry", "stop", "target"), "O133": ("entry_at", "confirm_at", "loss_at"),
    "O134": ("tests", "inside_rows", "stopped_out"),
    "O135": ("resistance", "resistance_at", "entry_at"), "O136": ("bias_at",),
}


RICH_MARKERS = {
    "O121": {"branch_id", "band_id", "stage_ledger"}, "O122": {"branch_id", "band_id", "checks"},
    "O123": {"branch_id", "stage_ledger", "defense"}, "O124": {"branch_id", "candle_id", "footprint_snapshot_ids"},
    "O125": {"branch_id", "selected_band", "vwap_snapshot_id"}, "O126": {"branch_id", "origin_id", "checks"},
    "O127": {"branch_id", "buyers_area_id", "checks"}, "O128": {"branch_id", "failure_history", "checks"},
    "O129": {"branch_id", "balance_id", "failed_area_id"}, "O130": {"branch_id", "thesis_id", "band_id"},
    "O131": {"branch_id", "microbalance_id", "target_id"}, "O132": {"branch_id", "kg1_level_id", "management_records"},
    "O133": {"branch_id", "case_id", "checks"}, "O134": {"branch_id", "case_id", "test_episodes"},
    "O135": {"branch_id", "case_id", "approach_events"}, "O136": {"support_event_id", "linked_candidate_ids"},
}


def _schema(rid: str, **values: Any) -> dict[str, Any]:
    out = {name: None for name in FLOW_SEQUENCE_SCHEMAS[rid]}
    out.update(values)
    return out


def _result(rid: str, state: str, values: dict[str, Any] | None = None, **kwargs: Any) -> RecipeResult:
    return RecipeResult(rid, state, _schema(rid, **(values or {})), **kwargs)


def _holes(rid: str, names: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(f"HOLE:{rid}:{name}" for name in names))


def _override(rid: str) -> Callable:
    def decorate(fn: Callable[[dict], RecipeResult]) -> Callable[[dict], RecipeResult]:
        @wraps(fn)
        def wrapped(inp: dict) -> RecipeResult:
            rich = any(key in inp for key in RICH_MARKERS[rid])
            blocked = guard(inp, rid, () if rich else LEGACY_REQUIRED[rid])
            if blocked is not None:
                if blocked.reason in {"dependency available after use", "dependency available after claimed snapshot"}:
                    try: observed = fn(inp)
                    except (ArithmeticError, KeyError, TypeError, ValueError): observed = _result(rid, "invalid", {}, base_ok=False)
                    observed.state, observed.base_ok, observed.reason = "invalid", False, blocked.reason
                    observed.hole_ids = list(dict.fromkeys(observed.hole_ids + blocked.hole_ids))
                    return observed
                return _result(rid, blocked.state, blocked.value, hole_ids=blocked.hole_ids,
                               known_at=blocked.known_at, base_ok=blocked.base_ok,
                               coverage_ok=blocked.coverage_ok, reason=blocked.reason)
            try: return fn(inp)
            except (ArithmeticError, KeyError, TypeError, ValueError) as exc:
                return _result(rid, "invalid", {}, base_ok=False, coverage_ok=None,
                               hole_ids=_holes(rid, ["input_type"]), known_at=inp.get("known_at"),
                               reason=f"invalid flow sequence input: {exc}")
        return wrapped
    return decorate


def _ledger(inp: dict, names: tuple[str, ...], aliases: dict[str, tuple[str, ...]] | None = None) -> dict[str, Any]:
    supplied = inp.get("stage_ledger")
    if isinstance(supplied, dict): return {name: supplied.get(name) for name in names}
    aliases = aliases or {}
    out = {}
    for name in names:
        keys = aliases.get(name, (f"{name}_at",))
        out[name] = next((inp.get(key) for key in keys if inp.get(key) is not None), None)
    return out


def _order(ledger: dict[str, Any], *, required: tuple[str, ...] | None = None,
           allow_equal: bool = False) -> tuple[bool | None, list[str]]:
    names = required or tuple(ledger)
    missing = [name for name in names if ledger.get(name) is None]
    if missing: return None, missing
    values = [ledger[name] for name in names]
    if any(type(value) is not int for value in values): raise ValueError("stage event keys must be int64")
    return all(a <= b if allow_equal else a < b for a, b in zip(values, values[1:])), []


def _bools(source: dict, names: tuple[str, ...], *, inp: dict | None = None) -> tuple[dict[str, bool | None], list[str]]:
    inp = inp or {}
    values = {name: source.get(name, inp.get(name)) for name in names}
    for name, value in values.items():
        if value is not None and type(value) is not bool: raise ValueError(f"{name} must be Boolean or null")
    return values, [name for name, value in values.items() if value is None]


def _finish(rid: str, values: dict[str, Any], *, checks: list[bool | None], missing: list[str],
            order: bool | None, known_at: int | None, supplied: bool = True,
            false_is_valid: bool = True) -> RecipeResult:
    observed_branch = kleene_and(*checks, order)
    branch = False if observed_branch is False else None if missing else observed_branch
    values["branch_ok"] = branch
    if order is False:
        return _result(rid, "invalid", values, hole_ids=_holes(rid, ["stage_order"]),
                       known_at=known_at, base_ok=False, coverage_ok=True,
                       reason="required source stages are reversed or tied")
    holes = _holes(rid, missing)
    state = "hole" if holes or branch is None else "supplied" if supplied else "computed"
    return _result(rid, state, values, hole_ids=holes, known_at=known_at,
                   base_ok=None if holes else True, coverage_ok=None if holes else True)


def _identity_holes(inp: dict, *names: str) -> list[str]:
    return [name for name in names if inp.get(name) is None]


@_override("O121")
def o121(inp: dict) -> RecipeResult:
    ledger = _ledger(inp, ("aggression", "rejection", "added_participation", "decision"), {
        "aggression": ("aggression_at", "arrival_at"), "rejection": ("rejection_at",),
        "added_participation": ("added_participation_at", "added_at"), "decision": ("decision_at",)})
    required = ("aggression", "rejection", "decision") + (("added_participation",) if inp.get("need_added", True) else ())
    # Preserve conceptual source order even when added participation is optional.
    ordered_names = tuple(n for n in ledger if n in required)
    order, missing = _order(ledger, required=ordered_names)
    checks, absent = _bools(inp.get("checks", {}), ("arriving_aggression", "little_progress", "local_rejection", "source_dom_confirmation"), inp=inp)
    added = inp.get("added_participation")
    if added is None and ledger.get("added_participation") is not None:
        added = True
    evidence = kleene_and(*checks.values(), added if inp.get("need_added", True) else True)
    absent += _identity_holes(inp, "branch_id", "band_id", "side")
    values = {"branch_id": inp.get("branch_id"), "band_id": inp.get("band_id"),
              "band": deepcopy(inp.get("band")), "side": inp.get("side"), "stage_ledger": ledger,
              **checks, "added_participation": added, "evidence": evidence, "order_ok": order}
    return _finish("O121", values, checks=[evidence], missing=missing+absent, order=order,
                   known_at=ledger.get("decision", inp.get("known_at")))


@_override("O122")
def o122(inp: dict) -> RecipeResult:
    ledger = _ledger(inp, ("absorption", "reward", "reward_return", "renewed_defense", "decision"), {
        "reward_return": ("reward_return_at", "return_at", "retest_at"),
        "renewed_defense": ("renewed_defense_at", "defense_at")})
    order, missing = _order(ledger)
    names=("passive_wall_confirmed","opposing_effort_no_result","own_reward_confirmed","reward_near_origin","fresh_reward_retest_defended","cvd_filter_ok","delta_filter_ok")
    checks, absent=_bools(inp.get("checks",{}),names,inp=inp)
    distinct = (ledger["reward"] is not None and ledger["reward_return"] is not None and ledger["reward"] < ledger["reward_return"])
    if ledger["reward"] is None or ledger["reward_return"] is None: distinct=None
    branch=kleene_and(*checks.values(),distinct)
    absent += _identity_holes(inp, "branch_id", "band_id", "side")
    values={"branch_id":inp.get("branch_id"),"band_id":inp.get("band_id"),"support":dec(inp.get("support")),"side":inp.get("side"),
            "stage_ledger":ledger,**checks,"reward_price":dec(inp.get("reward_price",inp.get("reward_px"))),
            "return_price":dec(inp.get("return_price",inp.get("return_px"))),"reward_and_retest_distinct":distinct,
            "strict_reversal_sequence":kleene_and(branch,order)}
    result=_finish("O122",values,checks=[branch],missing=missing+absent,order=order,known_at=ledger.get("decision",inp.get("known_at")))
    result.value["strict_reversal_sequence"]=result.value["branch_ok"]
    return result


@_override("O123")
def o123(inp: dict) -> RecipeResult:
    q=dec(inp.get("q",inp.get("tick_size",Decimal("0.25"))))
    if q is None or q<=0: raise ValueError("tick size must be positive")
    origin=dec(inp.get("origin")); confirm=dec(inp.get("confirm_price",inp.get("confirm_px"))); entry=dec(inp.get("entry"))
    direction=str(inp.get("side",inp.get("direction",""))).lower(); sign=Decimal(1) if direction in {"long","buy","b"} else Decimal(-1) if direction in {"short","sell","a","s"} else None
    raw=None if origin is None or confirm is None else confirm-origin
    reward=None if raw is None else abs(raw) / q if sign is None else sign*raw/q
    distance=None if entry is None or confirm is None else abs(entry-confirm)/q
    reward_gate=None if reward is None else Decimal(2)<=reward<=Decimal(4)
    entry_gate=None if distance is None else Decimal(0)<=distance<=Decimal(2)
    daily=dec(inp.get("daily_r_before",inp.get("daily_r"))); cap=dec(inp.get("daily_cap",-4))
    if cap != -4: return _result("O123","invalid",{"reward_ticks":reward,"distance_ticks":distance,"entry_distance_ticks":distance,"size_halved_repairs":False},base_ok=False,reason="STOP daily cap must remain -4R")
    daily_ok=None if daily is None else daily>-4
    ledger=_ledger(inp,("defense","replenishment","exhaustion","liftoff","decision"),{"replenishment":("replenishment_at","replenish_at"),"exhaustion":("exhaustion_at","exhaust_at"),"liftoff":("liftoff_at","reward_at"),"decision":("decision_at","entry_at")})
    rich=any(k in inp for k in RICH_MARKERS["O123"])
    order,missing=_order(ledger)
    check_names=("defense","replenishment","opponent_thinning","absorber_aggressive","lift_off")
    flags,absent=_bools(inp.get("checks",{}),check_names,inp=inp)
    stages=kleene_and(*flags.values(),order)
    geo=kleene_and(reward_gate,entry_gate)
    absent += _identity_holes(inp, "branch_id", "band_id")
    values={"branch_id":inp.get("branch_id"),"band_id":inp.get("band_id"),"side":direction or None,"stage_ledger":ledger,**flags,
            "reward_ticks":reward,"distance_ticks":distance,"entry_distance_ticks":distance,"reward_gate_ok":reward_gate,"entry_gate_ok":entry_gate,
            "daily_r_before":daily,"daily_stop_ok":daily_ok,"geometry_ok":geo,"stage_evidence_ok":stages,"size_halved_repairs":False}
    return _finish("O123",values,checks=[geo,daily_ok,stages],missing=missing+absent+([] if daily is not None else ["daily_r_before"])+([] if sign is not None else ["side"]),order=order,known_at=ledger.get("decision",inp.get("known_at")),supplied=False)


@_override("O124")
def o124(inp: dict) -> RecipeResult:
    ids=list(inp.get("footprint_snapshot_ids",[])); candle=inp.get("candle_id",inp.get("disagreement_candle")); poc_candle=inp.get("poc_candle",candle)
    same=None if candle is None or poc_candle is None else poc_candle==candle
    if same is False: return _result("O124","invalid",{"branch_id":inp.get("branch_id"),"candle_id":candle,"footprint_snapshot_ids":ids,"same_candle":False,"route_ok":False,"branch_ok":False},base_ok=False,reason="footprint stages cross candle identity")
    ledger=_ledger(inp,("disagreement","poc_flip","flow_confirmation","decision"),{"poc_flip":("poc_flip_at","poc_at","flip_at"),"flow_confirmation":("flow_confirmation_at","flow_at"),"decision":("decision_at","entry_at")})
    order,missing=_order(ledger)
    flags,absent=_bools(inp.get("checks",{}),("candle_delta_disagreement","local_absorption","intrabar_poc_flip","source_flow_confirmation"),inp=inp)
    absent += _identity_holes(inp, "branch_id", "candle_id")
    if not ids or None in ids or len(ids) != len(set(ids)): absent.append("footprint_snapshot_ids")
    values={"branch_id":inp.get("branch_id"),"candle_id":candle,"footprint_snapshot_ids":ids,"same_candle":same,"stage_ledger":ledger,**flags,
            "poc_from":dec(inp.get("poc_from")),"poc_to":dec(inp.get("poc_to")),"route_ok":kleene_and(*flags.values(),order)}
    result=_finish("O124",values,checks=list(flags.values()),missing=missing+absent,order=order,known_at=ledger.get("decision",inp.get("known_at")))
    result.value["route_ok"]=result.value["branch_ok"]
    return result


@_override("O125")
def o125(inp: dict) -> RecipeResult:
    mu,sig,k=dec(inp.get("vwap")),dec(inp.get("sigma")),dec(inp.get("k"))
    if sig is not None and sig<0: raise ValueError("negative sigma")
    upper=None if None in (mu,sig,k) else mu+k*sig; lower=None if None in (mu,sig,k) else mu-k*sig
    side=str(inp.get("side","short" if inp.get("selected_band","upper")=="upper" else "long" if inp.get("selected_band")=="lower" else "" )).lower()
    selected=inp.get("selected_band")
    price=upper if selected=="upper" else lower if selected=="lower" else None
    ledger=_ledger(inp,("band_known","touch","absorption","ladder_confirmation","decision"),{"band_known":("band_known_at",),"absorption":("absorption_at", "reject_at"),"ladder_confirmation":("ladder_confirmation_at","confirm_at"),"decision":("decision_at","entry_at")})
    order,missing=_order(ledger)
    flags,absent=_bools(inp.get("checks",{}),("source_vwap_known","selected_deviation_touched","absorption_at_that_band","ladder_confirmation"),inp=inp)
    target=dec(inp.get("target")); holes=[]
    if target is None: holes.append("target")
    if selected not in {"upper","lower"}: holes.append("selected_band")
    if None in (mu,sig,k): holes.append("vwap_deviation_definition")
    holes += _identity_holes(inp, "branch_id", "vwap_snapshot_id", "band_snapshot_id", "target_snapshot_id")
    if side not in {"long", "short"}: holes.append("side")
    values={"branch_id":inp.get("branch_id"),"side":side or None,"vwap_snapshot_id":inp.get("vwap_snapshot_id"),"band_snapshot_id":inp.get("band_snapshot_id"),
            "band_known_at":ledger["band_known"],"selected_band":selected,"selected_band_price":price,"target_snapshot_id":inp.get("target_snapshot_id"),"target":target,"upper":upper,"lower":lower,
            "stage_ledger":ledger,**flags,"confirmation":flags["ladder_confirmation"],"later_vwap":dec(inp.get("later_vwap")),"later_rewrites_target":False,"order_ok":order}
    return _finish("O125",values,checks=list(flags.values()),missing=missing+absent+holes,order=order,known_at=ledger.get("decision",inp.get("known_at")))


@_override("O126")
def o126(inp: dict) -> RecipeResult:
    ledger=_ledger(inp,("catalyst","first_release","failure","refill","drive","drive_retest","reward","decision"),{"catalyst":("catalyst_at",),"first_release":("first_release_at","release_at"),"drive_retest":("drive_retest_at","retest_at"),"reward":("reward_at","retest_at"),"decision":("decision_at","entry_at")})
    order,missing=_order(ledger)
    names=("repeated_effort_no_reward","first_squeeze","squeeze_failed","catalyst_reclaimed","refill_held","initiative_drive","intervening_wicks_taken","drive_retest_defended","own_aggression_rewarded","cvd_filter_ok")
    flags,absent=_bools(inp.get("checks",{}),names,inp=inp)
    absent += _identity_holes(inp, "branch_id", "origin_id", "side")
    values={"branch_id":inp.get("branch_id"),"origin_id":inp.get("origin_id"),"side":inp.get("side"),"stage_ledger":ledger,**flags,"short_gamma":inp.get("short_gamma"),"sequence_ok":kleene_and(*flags.values(),order)}
    result=_finish("O126",values,checks=list(flags.values()),missing=missing+absent,order=order,known_at=ledger.get("decision",inp.get("known_at")))
    result.value["sequence_ok"]=result.value["branch_ok"]
    return result


@_override("O127")
def o127(inp: dict) -> RecipeResult:
    side=str(inp.get("side") or "").lower(); entry,stop=dec(inp.get("entry")),dec(inp.get("stop")); risk=None if entry is None or stop is None else abs(entry-stop)
    multiple=dec(inp.get("r_multiple")); r2=None if multiple is None or risk is None or side != "long" else entry+multiple*risk
    area=inp.get("buyers_area"); area_hi=dec(area[1]) if isinstance(area,(list,tuple)) else dec(inp.get("buyers_area_high"))
    aggression_low=dec(inp.get("aggression_low"));
    flags,absent=_bools(inp.get("checks",{}),("source_squeeze_failed","tape_died_at_failure","no_aggression_at_failure","buyers_area_identified","entry_above_buyers","stop_below_aggression"),inp=inp)
    if flags["buyers_area_identified"] is None: flags["buyers_area_identified"] = area is not None if any(k in inp for k in RICH_MARKERS["O127"]) else None
    if flags["entry_above_buyers"] is None and entry is not None and area_hi is not None: flags["entry_above_buyers"]=entry>area_hi
    if flags["stop_below_aggression"] is None and stop is not None and aggression_low is not None: flags["stop_below_aggression"]=stop<aggression_low
    dying=inp.get("dying_tape")
    if flags["tape_died_at_failure"] is None and dying is not None: flags["tape_died_at_failure"]=bool(dying)
    absent=[n for n,v in flags.items() if v is None]
    ledger=_ledger(inp,("failure","entry_trigger","decision"),{"entry_trigger":("entry_trigger_at",),"decision":("decision_at","entry_at")})
    rich=any(k in inp for k in RICH_MARKERS["O127"])
    order,missing=_order(ledger)
    if side not in {"long","short"}: missing.append("side")
    qual=kleene_and(side=="long",*flags.values(),order)
    absent += _identity_holes(inp, "branch_id", "buyers_area_id")
    values={"branch_id":inp.get("branch_id"),"side":side or None,"buyers_area_id":inp.get("buyers_area_id"),"buyers_area":deepcopy(area),"entry":entry,"stop":stop,"initial_risk":risk,
            "r_multiple":multiple,"r2":r2,"r_in_1_to_3":None if multiple is None else 1<=multiple<=3,"stage_ledger":ledger,**flags,"qualification":qual,"automatic_selector":None}
    return _finish("O127",values,checks=[side=="long",*flags.values()],missing=missing+absent+([] if multiple is not None else ["objective"]),order=order,known_at=ledger.get("decision",inp.get("known_at")),supplied=False)


@_override("O128")
def o128(inp: dict) -> RecipeResult:
    ledger=_ledger(inp,("catalyst","release","pullback","confirmation","decision"),{"pullback":("pullback_at","first_pullback_at"),"confirmation":("confirmation_at","confirm_at"),"decision":("decision_at","entry_at")})
    order,missing=_order(ledger)
    chosen=inp.get("chosen_pullback_at",ledger["pullback"]); first=ledger["pullback"]
    first_ok=None if first is None else chosen==first
    history=inp.get("failure_history")
    prior_ids=[]; history_complete=None; no_prior=None
    if isinstance(history,dict):
        history_complete=history.get("coverage_complete")
        decision=ledger["decision"]
        prior=[r for r in history.get("events",[]) if r.get("at") is not None and (decision is None or r["at"]<=decision) and r.get("failed") is True]
        raw_ids=[r.get("failure_id",r.get("event_id")) for r in prior]
        if any(value is None for value in raw_ids) or len(raw_ids) != len(set(raw_ids)):
            history_complete = None
        prior_ids=[str(value) for value in raw_ids if value is not None]
        no_prior=False if prior_ids else True if history_complete is True else None
    flags,absent=_bools(inp.get("checks",{}),("catalyst_known","fast_release","opposing_pullback_aggression_absorbed","continuation_confirmed"),inp=inp)
    absent=[n for n,v in flags.items() if v is None]
    later=inp.get("later_failure_at")
    absent += _identity_holes(inp, "branch_id", "origin_id", "side")
    values={"branch_id":inp.get("branch_id"),"origin_id":inp.get("origin_id"),"side":inp.get("side"),"stage_ledger":ledger,**flags,
            "first_pullback":first_ok,"no_prior_failure":no_prior,"failure_history_complete":history_complete,"prior_failure_ids":prior_ids,
            "later_failure_invalidates":False,"later_failure_at":later,"order_ok":order}
    return _finish("O128",values,checks=[*flags.values(),first_ok,no_prior],missing=missing+absent+([] if history_complete is True else ["failure_history"]),order=order,known_at=ledger.get("decision",inp.get("known_at")))


@_override("O129")
def o129(inp: dict) -> RecipeResult:
    lo,hi=dec(inp.get("lo")),dec(inp.get("hi")); band=deepcopy(inp.get("band",[lo,hi] if lo is not None and hi is not None else None))
    ledger=_ledger(inp,("failure","departure","same_area_return","decision"),{"failure":("failure_at","fail_at"),"departure":("departure_at","depart_at","leave_at"),"same_area_return":("same_area_return_at","retest_at"),"decision":("decision_at","entry_at")})
    order,missing=_order(ledger)
    flags,absent=_bools(inp.get("checks",{}),("balance_context","failed_aggression_at_extreme","left_failed_area","retest_same_failed_area","aggression_still_unrewarded","target_is_prior_opposite_control"),inp=inp)
    target=dec(inp.get("target")); opposite=dec(inp.get("opposite_control"))
    if flags["target_is_prior_opposite_control"] is None and target is not None and opposite is not None: flags["target_is_prior_opposite_control"]=target==opposite
    absent=[n for n,v in flags.items() if v is None]
    absent += _identity_holes(inp, "branch_id", "balance_id", "failed_area_id", "target_id", "side")
    values={"branch_id":inp.get("branch_id"),"balance_id":inp.get("balance_id"),"band":band,"side":inp.get("side"),"failed_area_id":inp.get("failed_area_id"),"stage_ledger":ledger,
            **flags,"long_gamma":inp.get("long_gamma"),"target":target,"target_id":inp.get("target_id"),"target_is_balance_low":None if target is None or lo is None else target==lo,
            "requires_lift":False,"order_ok":order}
    return _finish("O129",values,checks=list(flags.values()),missing=missing+absent,order=order,known_at=ledger.get("decision",inp.get("known_at")))


@_override("O130")
def o130(inp: dict) -> RecipeResult:
    lo,hi=dec(inp.get("lo")),dec(inp.get("hi")); band=deepcopy(inp.get("band",[lo,hi] if lo is not None and hi is not None else None))
    if band is not None and dec(band[0])>dec(band[1]): raise ValueError("continuation band bounds reversed")
    ledger=_ledger(inp,("prior_defense","same_band_return","fresh_defense","decision"),{"prior_defense":("prior_defense_at",),"same_band_return":("same_band_return_at","retest_at"),"fresh_defense":("fresh_defense_at",),"decision":("decision_at","entry_at","use_at")})
    rich=any(k in inp for k in RICH_MARKERS["O130"])
    order,missing=_order(ledger)
    flags,absent=_bools(inp.get("checks",{}),("prior_band_control","same_band_retest","fresh_same_side_defense","executed_aggression","refresh_consistent","control_side_matches_thesis"),inp=inp)
    short_control=kleene_and(*flags.values(),order)
    absent += _identity_holes(inp, "branch_id", "thesis_id", "band_id", "side")
    values={"branch_id":inp.get("branch_id"),"thesis_id":inp.get("thesis_id"),"band_id":inp.get("band_id"),"band":band,"side":inp.get("side"),"stage_ledger":ledger,**flags,
            "short_control":short_control,"old_defense_keeps_control":False,"prior_defense_at":ledger["prior_defense"],"fresh_defense_at":ledger["fresh_defense"]}
    return _finish("O130",values,checks=list(flags.values()),missing=missing+absent,order=order,known_at=ledger.get("decision",inp.get("known_at")))


@_override("O131")
def o131(inp: dict) -> RecipeResult:
    lo,hi=dec(inp.get("micro_low",inp.get("micro_lo"))),dec(inp.get("micro_high",inp.get("micro_hi")))
    if lo is None or hi is None or hi<=lo: raise ValueError("microbalance requires positive width")
    side=str(inp.get("side") or "").lower(); stop=dec(inp.get("stop")); target=dec(inp.get("target")); target_known=inp.get("target_known_at")
    ledger=_ledger(inp,("target_known","microbalance_known","breakout","decision"),{"target_known":("target_known_at",),"microbalance_known":("microbalance_known_at","complete_at"),"breakout":("breakout_at",),"decision":("decision_at","entry_at","use_at")})
    rich=any(k in inp for k in RICH_MARKERS["O131"])
    order,missing=_order(ledger)
    stop_ok=None if stop is None else stop<lo if side=="long" else stop>hi if side=="short" else False
    frozen=inp.get("microbalance_frozen")
    strength=inp.get("directional_strength",inp.get("source_strength")); breakout=inp.get("breakout_in_thesis_direction",strength)
    objective=target_known is not None and ledger["microbalance_known"] is not None and target_known<ledger["microbalance_known"]
    if not rich and target_known is None: objective=None
    checks=[frozen,strength,breakout,stop_ok,objective]
    holes=missing+[name for name,value in (("microbalance_frozen",frozen),("directional_strength",strength),("target_known_at",target_known),("stop",stop)) if value is None]
    holes += _identity_holes(inp, "branch_id", "microbalance_id", "target_id", "side")
    values={"branch_id":inp.get("branch_id"),"microbalance_id":inp.get("microbalance_id"),"micro_low":lo,"micro_high":hi,"width":hi-lo,"side":side or None,"stage_ledger":ledger,
            "microbalance_frozen":frozen,"directional_strength":strength,"breakout_in_thesis_direction":breakout,"stop":stop,"stop_side_ok":stop_ok,"stop_below_opposite":stop_ok,
            "target":target,"target_id":inp.get("target_id"),"objective_preexists":objective,"preexisting_target":objective,"qualifies":kleene_and(*checks,order),"automatic_selector":None}
    result=_finish("O131",values,checks=checks,missing=holes,order=order,known_at=ledger.get("decision",inp.get("known_at")))
    result.value["qualifies"]=result.value["branch_ok"]
    return result


def _directional_ratio(side: str, entry: Decimal, stop: Decimal, target: Decimal) -> Decimal | None:
    risk=(entry-stop) if side=="long" else (stop-entry)
    reward=(target-entry) if side=="long" else (entry-target)
    return None if risk<=0 else reward/risk


@_override("O132")
def o132(inp: dict) -> RecipeResult:
    side=str(inp.get("side") or "").lower(); entry,stop,target=(dec(inp.get(k)) for k in ("entry","stop","target"))
    initial_risk=None if entry is None or stop is None else abs(entry-stop)
    ratio=None if None in (entry,stop,target) else _directional_ratio(side,entry,stop,target)
    ledger=_ledger(inp,("kg1_known","retest","confirmation","decision"),{"kg1_known":("kg1_known_at",),"confirmation":("confirmation_at","confirm_at"),"decision":("decision_at","entry_at")})
    rich=any(k in inp for k in RICH_MARKERS["O132"])
    order,missing=_order(ledger)
    records=deepcopy(inp.get("management_records",[]))
    later_stop=dec(inp.get("later_stop")); later_target=dec(inp.get("later_target")); latest_ratio=None
    if later_stop is not None and later_target is not None: latest_ratio=_directional_ratio(side,entry,later_stop,later_target)
    current_stop,current_target=stop,target
    last_at=ledger.get("decision",inp.get("known_at"))
    for row in sorted(records,key=lambda r:r.get("at",0)):
        if row.get("at") is None or last_at is not None and row["at"]<=last_at: return _result("O132","invalid",{"branch_id":inp.get("branch_id"),"kg1_level_id":inp.get("kg1_level_id"),"management_records":records},base_ok=False,reason="management action is not later than entry")
        if row.get("stop") is not None: current_stop=dec(row["stop"])
        if row.get("target") is not None: current_target=dec(row["target"])
        latest_ratio=_directional_ratio(side,entry,current_stop,current_target); last_at=row["at"]
    kg1_known=inp.get("kg1_known",ledger["kg1_known"] is not None)
    entry_seq=kleene_and(kg1_known,order)
    holes=missing+_identity_holes(inp, "branch_id", "kg1_level_id", "side")
    holes += [name for name,value in (("entry",entry),("stop",stop),("target",target)) if value is None]
    holes += ["engine"]
    values={"branch_id":inp.get("branch_id"),"kg1_level_id":inp.get("kg1_level_id"),"kg1_known":kg1_known,"side":side or None,"stage_ledger":ledger,"retest_at":ledger["retest"],"confirm_at":ledger["confirmation"],"entry_sequence":entry_seq,
            "entry":entry,"stop":stop,"target":target,"initial_reward_to_risk":ratio,"ratio":ratio,"original_risk":initial_risk,"later_reward_to_risk":latest_ratio,"later_ratio":latest_ratio,"management_records":records,"automatic_trailing":None}
    return _finish("O132",values,checks=[kg1_known],missing=holes,order=order,known_at=last_at)


@_override("O133")
def o133(inp: dict) -> RecipeResult:
    ledger=_ledger(inp,("risk_declared","early_choice","entry","full_confirmation","outcome"),{"risk_declared":("risk_declared_at",),"early_choice":("early_choice_at",),"entry":("entry_at",),"full_confirmation":("full_confirmation_at","confirm_at"),"outcome":("outcome_at","loss_at")})
    entry,confirm=ledger["entry"],ledger["full_confirmation"]
    early=None if entry is None or confirm is None else entry<confirm
    flags,absent=_bools(inp.get("checks",{}),("thesis_alive","preconfirmation_entry","small_risk_declared","stop_predefined","explicitly_early_entry","source_refill_return","source_risk_predefined"),inp=inp)
    order_checks = []
    for left, right in (("risk_declared", "early_choice"), ("early_choice", "entry"),
                        ("entry", "full_confirmation"), ("entry", "outcome")):
        if ledger[left] is None or ledger[right] is None:
            absent.append(left if ledger[left] is None else right)
        else:
            order_checks.append(ledger[left] < ledger[right])
    if any(check is False for check in order_checks):
        return _result("O133", "invalid", {"branch_id": inp.get("branch_id"),
                       "case_id": inp.get("case_id"), "thesis_id": inp.get("thesis_id"),
                       "stage_ledger": ledger}, base_ok=False,
                       reason="early-attempt stages are reversed or tied")
    absent += _identity_holes(inp, "branch_id", "case_id", "thesis_id")
    case=kleene_and(*flags.values(),early)
    if absent and case is True: case = None
    values={"branch_id":inp.get("branch_id"),"case_id":inp.get("case_id"),"thesis_id":inp.get("thesis_id"),"stage_ledger":ledger,**flags,
            "case_fidelity":case,"deliberate_early":early,"full_confirmed_branch_pass":False,"confirmed_branch":False if early else None,
            "thesis_killed_by_loss_alone":False,"automatic_early_admission":None,"automatic_selector":None}
    holes=absent+["selector"]
    return _result("O133","hole",values,hole_ids=_holes("O133",holes),known_at=entry or inp.get("known_at"),coverage_ok=None)


@_override("O134")
def o134(inp: dict) -> RecipeResult:
    episodes=inp.get("test_episodes")
    if episodes is None:
        episodes=[{"test_id":None,"return_at":at,"departure_at":None,"band_id":inp.get("band_id")} for at in inp.get("tests",[])]
    ids=[]; returns=set(); invalid=[]; missing=[]
    for row in episodes:
        tid=row.get("test_id",row.get("id")); ret=row.get("return_at",row.get("at")); dep=row.get("departure_at")
        if tid is None or ret is None: missing.append("test_identity"); continue
        if inp.get("band_id") is not None and row.get("band_id",inp.get("band_id"))!=inp.get("band_id"): invalid.append("test belongs to another band"); continue
        if ret in returns or tid in ids: continue
        if any(k in inp for k in RICH_MARKERS["O134"]) and ids and dep is None: missing.append("departure")
        ids.append(str(tid)); returns.add(ret)
    no_def=inp.get("no_new_buyer_defense"); ordinal=len(ids); stopped=inp.get("stopped_out")
    missing += _identity_holes(inp, "branch_id", "case_id", "band_id")
    fidelity=kleene_and(ordinal==3,no_def,stopped is not None)
    same_support_band=None if inp.get("band_id") is None or not episodes else all(row.get("band_id")==inp.get("band_id") for row in episodes)
    identity_complete=bool(episodes) and not missing and not invalid
    if missing and fidelity is True: fidelity = None
    values={"branch_id":inp.get("branch_id"),"case_id":inp.get("case_id"),"band_id":inp.get("band_id"),"test_ids":ids,"distinct_test_count":ordinal,"current_test_ordinal":ordinal,"ordinal":ordinal,
            "inside_rows_are_one_test":True if identity_complete else None,"same_support_band":same_support_band,"no_new_buyer_defense":no_def,"case_fidelity":fidelity,"in_cohort":True if identity_complete else None,"stopped_out":stopped,"universal_third_touch":False,"automatic_entry_selector":None}
    if invalid: return _result("O134","invalid",values,hole_ids=_holes("O134",["identity"]),base_ok=False,reason="; ".join(invalid))
    holes=missing+([] if no_def is not None else ["no_new_buyer_defense"])+["selector"]
    return _result("O134","hole",values,hole_ids=_holes("O134",holes),known_at=inp.get("known_at"),coverage_ok=None)


@_override("O135")
def o135(inp: dict) -> RecipeResult:
    marked=inp.get("resistance_known_at",inp.get("resistance_at")); entry=inp.get("decision_at",inp.get("entry_at")); approach=inp.get("approach_at")
    if marked is not None and entry is not None and marked>entry: return _result("O135","invalid",{"branch_id":inp.get("branch_id"),"case_id":inp.get("case_id"),"resistance":dec(inp.get("resistance")),"resistance_known":False,"case_ok":False,"automatic_full_trigger":None},base_ok=False,reason="resistance was marked after entry")
    events=inp.get("approach_events",[]); upward=None
    if events:
        prices=[dec(r.get("price")) for r in events]; upward=all(a<=b for a,b in zip(prices,prices[1:])); approach=max(r.get("at",r.get("known_at",0)) for r in events)
    exhaustion=inp.get("source_exhaustion",inp.get("upward_approach_loses_aggression")); side=str(inp.get("side") or "").lower(); small=inp.get("small_risk")
    fidelity=kleene_and(marked is not None and (entry is None or marked<=entry),upward if upward is not None else None,exhaustion,side=="short",small)
    holes=[name for name,value in (("approach",upward),("source_exhaustion",exhaustion),("small_risk",small)) if value is None]
    holes += _identity_holes(inp, "branch_id", "case_id", "resistance_id", "side")
    if holes and fidelity is True: fidelity = None
    values={"branch_id":inp.get("branch_id"),"case_id":inp.get("case_id"),"resistance_id":inp.get("resistance_id"),"resistance":dec(inp.get("resistance")),"resistance_known":marked is not None if inp.get("resistance_id") is not None else None,
            "approach_at":approach,"source_exhaustion":exhaustion,"side":side or None,"small_risk":small,"short_case_fidelity":fidelity,"case_ok":fidelity,"session_end_at":inp.get("session_end_at"),"automatic_entry_selector":None,"automatic_full_trigger":None}
    holes += ["selector"]
    return _result("O135","hole",values,hole_ids=_holes("O135",holes),known_at=entry or inp.get("known_at"),coverage_ok=None)


@_override("O136")
def o136(inp: dict) -> RecipeResult:
    bias_at=inp.get("bias_at",inp.get("bias_known_at")); direction=inp.get("direction",inp.get("bias_side")); origin=inp.get("origin_reference_id"); support=inp.get("support_event_id")
    missing=[name for name,value in (("bias_known_at",bias_at),("direction",direction),("origin_reference_id",origin)) if value is None]
    rich=any(k in inp for k in RICH_MARKERS["O136"])
    if rich and support is None: missing.append("support_event_id")
    candidate=inp.get("candidate_side"); use=inp.get("use_at")
    identity=None if candidate is None or direction is None else candidate==direction
    causal=None if use is None or bias_at is None else bias_at<=use
    if candidate is None: missing.append("candidate_side")
    if use is None: missing.append("use_at")
    if support is None: missing.append("support_event_id")
    values={"bias_recorded":True if not missing and identity is True and causal is True else False if identity is False or causal is False else None,"bias_side":direction,"bias_start":inp.get("bias_start",bias_at),"bias_known_at":bias_at,
            "origin_reference_id":origin,"support_event_id":support,"revision_history":deepcopy(inp.get("revision_history",[])),"linked_candidate_ids":list(inp.get("linked_candidate_ids",[])),"direction":direction,
            "candidate_side":candidate,"later_event_explains_bias":False,"later_event_at":inp.get("later_event_at"),"automatic_bias_selector":None}
    if identity is False or causal is False: return _result("O136","invalid",values,hole_ids=_holes("O136",["identity" if identity is False else "causal"]),known_at=bias_at,base_ok=False,reason="candidate side differs from bias" if identity is False else "bias available after use")
    return _result("O136","hole" if missing else "supplied",values,hole_ids=_holes("O136",missing),known_at=bias_at,base_ok=None if missing else True,coverage_ok=None if missing else True)


REGISTRATION_OVERRIDES={rid:globals()[rid.lower()] for rid in FLOW_SEQUENCE_SCHEMAS}
NATIVE_PRODUCERS: dict[str, Callable] = {}


class FlowDerivationError(ValueError):
    """The declared semantic parent graph cannot produce the selected branch."""


DERIVED_PARENT_ROLES = {
    "O121": {"absorption": {"O101"}, "dom": {"O100"}, "participation": {"O103"}},
    "O122": {"absorption": {"O101"}, "replenishment": {"O102"}, "reward": {"O104"}, "cvd": {"O105"}},
    "O123": {"replenishment": {"O102"}, "thinning": {"O114"}, "liftoff": {"O115"}, "daily_risk": {"O145"}},
    "O124": {"delta": {"O106"}, "poc": {"O108"}, "footprint": {"O120"}, "flow": {"O100"}},
    "O125": {"vwap": {"O030", "O031"}, "band": {"O032"}, "flow": {"O100"}, "objective": {"O141"}},
    "O126": {"catalyst": {"O118"}, "zone": {"O116"}, "markers": {"O099"}, "imbalance": {"O110"}, "cvd": {"O105"}},
    "O127": {"tape": {"O111"}, "buyers_area": {"O116", "O072"}, "risk": {"O139"}},
    "O128": {"catalyst": {"O118"}, "tape": {"O111"}, "absorption": {"O101"}, "history": {"O117", "O118"}},
    "O129": {"balance": {"O060"}, "absorption": {"O101"}, "objective": {"O141"}},
    "O130": {"prior_area": {"O072"}, "zone": {"O116"}, "replenishment": {"O102"}, "trades": {"O098"}, "thesis": {"O138"}},
    "O131": {"microbalance": {"O060"}, "risk": {"O139"}, "objective": {"O141"}, "thesis": {"O138"}},
    "O132": {"kg1": {"O041"}, "management": {"O142"}},
    "O133": {"thesis": {"O138"}, "risk": {"O139"}, "exposure": {"O140"}},
    "O134": {"memory": {"O117"}, "dom": {"O100"}},
    "O135": {"approach": {"O113"}, "footprint": {"O120"}},
    "O136": {"support": {"O047", "O048", "O054", "O091", "O097"}},
}


def _derived_parents(recipe_id: str, config: dict, parents: list[dict]) -> dict[str, dict]:
    selected = config.get("parent_roles")
    required = DERIVED_PARENT_ROLES[recipe_id]
    if not isinstance(selected, dict) or set(selected) != set(required):
        raise FlowDerivationError(f"{recipe_id} requires exact semantic parent_roles {sorted(required)}")
    index = {str(parent.get("object_id")): parent for parent in parents}
    if len(index) != len(parents) or set(map(str, selected.values())) != set(index):
        raise FlowDerivationError("semantic parent roles must cover each actual parent exactly once")
    out = {}
    for role, allowed in required.items():
        parent = index.get(str(selected[role]))
        if parent is None or parent.get("recipe_id") not in allowed:
            raise FlowDerivationError(f"{role} parent has the wrong producer identity")
        if parent.get("state") == "invalid" or parent.get("recipe_base_ok") is False:
            raise FlowDerivationError(f"{role} parent is invalid")
        out[role] = parent
    return out


def _pv(parent: dict, name: str, *fallbacks: str) -> Any:
    value = parent.get("value", {})
    for field in (name, *fallbacks):
        if field in value and value[field] is not None:
            return deepcopy(value[field])
    return None


def _pt(parent: dict, name: str, *fallbacks: str) -> int | None:
    value = _pv(parent, name, *fallbacks)
    return value if type(value) is int else parent.get("known_at")


def _objective_price(parent: dict) -> Any:
    selected = _pv(parent, "selected_objective", "target")
    if isinstance(selected, dict):
        for field in ("price", "target", "poc", "selected_edge", "reward_price"):
            if selected.get(field) is not None:
                return deepcopy(selected[field])
        return None
    return selected


def derived_flow(recipe_id: str, config: dict, parents: list[dict]) -> RecipeResult:
    """Build a branch input only from fixed semantic fields of selected parents."""
    try:
        role = _derived_parents(recipe_id, config, parents)
        # Caller selects branch/source identity and decision time. Measurements,
        # checks, stages and geometry below always come from the parent graph.
        # Keep only selection identity and a small set of declared recipe
        # literals.  Blind config copying would let a caller inject output
        # fields that never appeared in the selected parent graph.
        common = {"branch_id", "side", "case_id", "known_at", "use_at",
                  "instrument_id", "method_id", "source_id"}
        recipe_literals = {
            "O121": {"need_added"}, "O122": {"complete_attempt"},
            "O123": {"daily_cap"}, "O126": {"short_gamma"},
            "O127": {"r_multiple"}, "O132": {"entry"},
            "O136": {"direction", "candidate_side", "bias_start"},
        }.get(recipe_id, set())
        inp = {key: deepcopy(config[key]) for key in common | recipe_literals if key in config}
        decision = config.get("decision_at", config.get("use_at"))
        if recipe_id == "O121":
            a,d,p = role["absorption"],role["dom"],role["participation"]
            absorption = _pv(a,"source_absorption","absorption")
            inp.update(band_id=a.get("band_id"),band=_pv(a,"band"),
                stage_ledger={"aggression":a.get("known_at"),"rejection":d.get("known_at"),"added_participation":p.get("known_at"),"decision":decision},
                checks={"arriving_aggression":None if _pv(a,"effort") is None else _pv(a,"effort")>0,
                        "little_progress":absorption,"local_rejection":_pv(d,"defense_interpretation"),
                        "source_dom_confirmation":_pv(d,"defense_interpretation")},
                added_participation=None if _pv(p,"participant_count") is None else _pv(p,"participant_count")>0)
        elif recipe_id == "O122":
            a,r,w,c = role["absorption"],role["replenishment"],role["reward"],role["cvd"]
            inp.update(band_id=a.get("band_id"),support=_pv(w,"origin"),
                stage_ledger={"absorption":a.get("known_at"),"reward":_pt(w,"reward_at"),"reward_return":_pt(w,"return_at"),"renewed_defense":r.get("known_at"),"decision":decision},
                checks={"passive_wall_confirmed":_pv(r,"verified_replenishment"),"opposing_effort_no_result":_pv(a,"source_absorption","absorption"),
                        "own_reward_confirmed":_pv(w,"directional_reward"),"reward_near_origin":_pv(w,"directional_reward"),
                        "fresh_reward_retest_defended":_pv(r,"hold"),
                        "cvd_filter_ok":_pv(c,"directional_relation") if type(_pv(c,"directional_relation")) is bool else None,
                        "delta_filter_ok":None},
                reward_price=_pv(w,"reward_price"),return_price=_pv(w,"return_price"))
        elif recipe_id == "O123":
            r,t,l,d = role["replenishment"],role["thinning"],role["liftoff"],role["daily_risk"]
            stages=_pv(l,"stage_ledger") or {}
            inp.update(origin=_pv(l,"origin"),confirm_price=_pv(l,"reward_price"),entry=config.get("entry"),q=config.get("tick_size",config.get("q")),
                daily_r_before=_pv(d,"daily_R_before"),
                stage_ledger={"defense":stages.get("defense"),"replenishment":stages.get("replenishment"),"exhaustion":stages.get("exhaustion"),"liftoff":stages.get("liftoff"),"decision":decision},
                checks={"defense":_pv(r,"hold"),"replenishment":_pv(r,"verified_replenishment"),"opponent_thinning":_pv(t,"source_classification"),
                        "absorber_aggressive":None if not _pv(l,"defender_aggression_events") else True,"lift_off":_pv(l,"directional_reward")})
        elif recipe_id == "O124":
            d,p,f,o = role["delta"],role["poc"],role["footprint"],role["flow"]
            candle=_pv(f,"candle_id")
            inp.update(candle_id=candle,poc_candle=_pv(p,"candle_id"),footprint_snapshot_ids=_pv(p,"snapshot_ids") or [],
                stage_ledger={"disagreement":d.get("known_at"),"poc_flip":_pt(p,"flip_at"),"flow_confirmation":o.get("known_at"),"decision":decision},
                checks={"candle_delta_disagreement":_pv(d,"opposed_signs"),"local_absorption":_pv(o,"defense_interpretation"),
                        "intrabar_poc_flip":None if _pv(p,"change") is None else _pv(p,"change")!=0,"source_flow_confirmation":_pv(o,"defense_interpretation")},
                poc_from=_pv(p,"poc_before"),poc_to=_pv(p,"poc_after"))
        elif recipe_id == "O125":
            v,b,f,o = role["vwap"],role["band"],role["flow"],role["objective"]
            side=config.get("side"); selected=config.get("selected_band")
            inp.update(vwap=_pv(v,"vwap"),sigma=_pv(b,"sigma"),k=_pv(b,"k"),vwap_snapshot_id=v["object_id"],band_snapshot_id=b["object_id"],
                selected_band=selected,target=_objective_price(o),target_snapshot_id=o["object_id"],
                stage_ledger={"band_known":b.get("known_at"),"touch":config.get("touch_at"),"absorption":f.get("known_at"),"ladder_confirmation":f.get("known_at"),"decision":decision},
                checks={"source_vwap_known":_pv(v,"vwap") is not None,"selected_deviation_touched":config.get("selected_deviation_touched"),
                        "absorption_at_that_band":_pv(f,"defense_interpretation"),"ladder_confirmation":_pv(f,"defense_interpretation")})
        elif recipe_id == "O126":
            c,z,m,i,v = role["catalyst"],role["zone"],role["markers"],role["imbalance"],role["cvd"]
            stages=_pv(c,"stage_ledger") or {}
            inp.update(origin_id=_pv(c,"origin_id"),stage_ledger={"catalyst":c.get("known_at"),"first_release":stages.get("release"),"failure":stages.get("failure"),
                "refill":stages.get("refill"),"drive":stages.get("drive"),"drive_retest":stages.get("retest"),"reward":stages.get("reward"),"decision":decision},
                checks={"repeated_effort_no_reward":_pv(c,"linked"),"first_squeeze":stages.get("release") is not None,"squeeze_failed":stages.get("failure") is not None,
                    "catalyst_reclaimed":_pv(c,"linked"),"refill_held":stages.get("hold") is not None,"initiative_drive":stages.get("drive") is not None,
                    "intervening_wicks_taken":config.get("intervening_wicks_taken"),"drive_retest_defended":stages.get("retest") is not None,
                    "own_aggression_rewarded":stages.get("reward") is not None,
                    "cvd_filter_ok":_pv(v,"directional_relation") if type(_pv(v,"directional_relation")) is bool else None})
        elif recipe_id == "O127":
            t,a,r = role["tape"],role["buyers_area"],role["risk"]
            area=_pv(a,"zone","band"); entry=config.get("entry"); stop=_pv(r,"structural_stop")
            inp.update(buyers_area_id=a["object_id"],buyers_area=area,entry=entry,stop=stop,aggression_low=config.get("aggression_low"),
                stage_ledger={"failure":config.get("failure_at"),"entry_trigger":config.get("entry_trigger_at"),"decision":decision},
                checks={"source_squeeze_failed":config.get("source_squeeze_failed"),"tape_died_at_failure":config.get("tape_died_at_failure"),
                    "no_aggression_at_failure":config.get("no_aggression_at_failure"),"buyers_area_identified":area is not None,
                    "entry_above_buyers":None if entry is None or not area else dec(entry)>dec(area[1]),"stop_below_aggression":_pv(r,"stop_side_ok")})
        elif recipe_id == "O128":
            c,t,a,h = role["catalyst"],role["tape"],role["absorption"],role["history"]
            stages=_pv(c,"stage_ledger") or {}
            resolved=_pv(h,"eligible_history_ids") or []
            unresolved=_pv(h,"unresolved_history_ids") or []
            inp.update(origin_id=_pv(c,"origin_id"),stage_ledger={"catalyst":c.get("known_at"),"release":stages.get("release"),"pullback":config.get("pullback_at"),"confirmation":config.get("confirmation_at"),"decision":decision},
                failure_history={"coverage_complete":not unresolved,"events":[{"failure_id":x,"at":h.get("known_at"),"failed":True} for x in resolved]},
                checks={"catalyst_known":_pv(c,"linked"),"fast_release":config.get("fast_release"),"opposing_pullback_aggression_absorbed":_pv(a,"source_absorption"),"continuation_confirmed":config.get("continuation_confirmed")})
        elif recipe_id == "O129":
            b,a,o = role["balance"],role["absorption"],role["objective"]
            band = _pv(b,"balance_band","band")
            inp.update(balance_id=b["object_id"],band=band,lo=band[0] if band else None,hi=band[1] if band else None,
                failed_area_id=a["object_id"],target=_objective_price(o),target_id=o["object_id"],
                stage_ledger={"failure":a.get("known_at"),"departure":config.get("departure_at"),"same_area_return":config.get("retest_at"),"decision":decision},
                checks={"balance_context":_pv(b,"balance") or config.get("long_gamma"),"failed_aggression_at_extreme":_pv(a,"source_absorption"),"left_failed_area":config.get("left_failed_area"),
                    "retest_same_failed_area":config.get("retest_same_failed_area"),"aggression_still_unrewarded":_pv(a,"source_absorption"),"target_is_prior_opposite_control":_pv(o,"objective_preknown")})
        elif recipe_id == "O130":
            p,z,r,t,h = role["prior_area"],role["zone"],role["replenishment"],role["trades"],role["thesis"]
            inp.update(thesis_id=h["object_id"],band_id=z["object_id"],band=_pv(z,"zone"),stage_ledger={"prior_defense":p.get("known_at"),"same_band_return":config.get("retest_at"),"fresh_defense":r.get("known_at"),"decision":decision},
                checks={"prior_band_control":_pv(p,"prior_defense_known"),"same_band_retest":_pv(p,"same_band_contact"),"fresh_same_side_defense":_pv(r,"verified_replenishment"),
                    "executed_aggression":bool(_pv(t,"event_records")),"refresh_consistent":_pv(r,"verified_replenishment"),"control_side_matches_thesis":_pv(h,"alive_at_decision")})
        elif recipe_id == "O131":
            m,r,o,h = role["microbalance"],role["risk"],role["objective"],role["thesis"]
            band=_pv(m,"balance_band","band") or [config.get("micro_low"),config.get("micro_high")]
            selected=_pv(o,"selected_objective") or {}
            inp.update(microbalance_id=m["object_id"],micro_low=band[0],micro_high=band[1],stop=_pv(r,"structural_stop"),target=selected.get("price",_pv(o,"target")),target_id=o["object_id"],
                target_known_at=o.get("known_at"),stage_ledger={"target_known":o.get("known_at"),"microbalance_known":m.get("known_at"),"breakout":config.get("breakout_at"),"decision":decision},
                microbalance_frozen=True,directional_strength=config.get("directional_strength"),breakout_in_thesis_direction=config.get("breakout_in_thesis_direction"))
        elif recipe_id == "O132":
            k,m = role["kg1"],role["management"]
            inp.update(kg1_level_id=k["object_id"],kg1_known=True,kg1_known_at=k.get("known_at"),
                stop=_pv(m,"initial_stop"),target=_pv(m,"initial_target"),management_records=_pv(m,"management_actions") or [],
                stage_ledger={"kg1_known":k.get("known_at"),"retest":config.get("retest_at"),"confirmation":config.get("confirm_at"),"decision":decision})
        elif recipe_id == "O133":
            h,r,e = role["thesis"],role["risk"],role["exposure"]
            inp.update(thesis_id=h["object_id"],stage_ledger={"risk_declared":r.get("known_at"),"early_choice":config.get("early_choice_at"),"entry":decision,"full_confirmation":config.get("confirm_at"),"outcome":config.get("outcome_at")},
                checks={"thesis_alive":_pv(h,"alive_at_decision"),"preconfirmation_entry":None if decision is None or config.get("confirm_at") is None else decision<config["confirm_at"],
                    "small_risk_declared":_pv(e,"cap_ok"),"stop_predefined":_pv(r,"risk_known_before_entry"),"explicitly_early_entry":config.get("explicitly_early_entry"),
                    "source_refill_return":config.get("source_refill_return"),"source_risk_predefined":_pv(r,"risk_known_before_entry")})
        elif recipe_id == "O134":
            m,d = role["memory"],role["dom"]
            ids=_pv(m,"eligible_history_ids") or []
            inp.update(band_id=_pv(m,"zone_id"),test_episodes=[{"test_id":x,"return_at":i+1,"departure_at":i+2,"band_id":_pv(m,"zone_id")} for i,x in enumerate(ids)],
                no_new_buyer_defense=False if _pv(d,"defense_interpretation") is True else None if _pv(d,"defense_interpretation") is None else True,
                stopped_out=config.get("stopped_out"))
        elif recipe_id == "O135":
            a,f = role["approach"],role["footprint"]
            inp.update(approach_at=a.get("known_at"),source_exhaustion=_pv(a,"aggressive_arrival"),approach_events=[{"at":_pv(a,"from_at"),"price":_pv(a,"from_price")},{"at":_pv(a,"to_at"),"price":_pv(a,"to_price")}],
                resistance_known_at=config.get("resistance_known_at"),entry_at=decision)
        elif recipe_id == "O136":
            s=role["support"]
            inp.update(direction=_pv(s,"side","direction","control_side") or config.get("direction"),bias_at=s.get("known_at"),support_event_id=s["object_id"],origin_reference_id=config.get("origin_reference_id") or s.get("band_id") or s["object_id"])
        result = REGISTRATION_OVERRIDES[recipe_id](inp)
        result.parent_ids = [parent["object_id"] for parent in parents]
        return result
    except (FlowDerivationError, KeyError, TypeError, ValueError) as exc:
        return _result(recipe_id, "invalid", {}, base_ok=False, coverage_ok=None,
                       hole_ids=_holes(recipe_id, ["parents"]), reason=str(exc))


DERIVED_PRODUCERS = {
    recipe_id: (lambda config, parents, recipe_id=recipe_id: derived_flow(recipe_id, config, parents))
    for recipe_id in FLOW_SEQUENCE_SCHEMAS
}
REQUIRED_INPUTS = {recipe_id: () for recipe_id in FLOW_SEQUENCE_SCHEMAS}


def _field(name: str) -> OutputField:
    if name in {"footprint_snapshot_ids","prior_failure_ids","management_records","test_ids","revision_history","linked_candidate_ids"}: return OutputField((list,))
    if name in {"stage_ledger","buyers_area","band"}: return OutputField((dict,list,Decimal,int),True)
    if name in {"distinct_test_count","current_test_ordinal","ordinal"}: return OutputField((int,),True)
    if name.endswith("_at") or name in {"band_known_at","bias_start","bias_known_at","session_end_at"}: return OutputField((int,),True)
    bool_names={"arriving_aggression","little_progress","local_rejection","source_dom_confirmation","added_participation","evidence","order_ok","branch_ok","passive_wall_confirmed","opposing_effort_no_result","own_reward_confirmed","reward_near_origin","fresh_reward_retest_defended","cvd_filter_ok","delta_filter_ok","reward_and_retest_distinct","strict_reversal_sequence","defense","replenishment","opponent_thinning","absorber_aggressive","lift_off","reward_gate_ok","entry_gate_ok","daily_stop_ok","geometry_ok","stage_evidence_ok","size_halved_repairs","same_candle","candle_delta_disagreement","local_absorption","intrabar_poc_flip","source_flow_confirmation","route_ok","source_vwap_known","selected_deviation_touched","absorption_at_that_band","ladder_confirmation","confirmation","later_rewrites_target","repeated_effort_no_reward","first_squeeze","squeeze_failed","catalyst_reclaimed","refill_held","initiative_drive","intervening_wicks_taken","drive_retest_defended","own_aggression_rewarded","short_gamma","sequence_ok","r_in_1_to_3","source_squeeze_failed","tape_died_at_failure","no_aggression_at_failure","buyers_area_identified","entry_above_buyers","stop_below_aggression","qualification","automatic_selector","catalyst_known","fast_release","first_pullback","no_prior_failure","failure_history_complete","opposing_pullback_aggression_absorbed","continuation_confirmed","later_failure_invalidates","balance_context","long_gamma","failed_aggression_at_extreme","left_failed_area","retest_same_failed_area","aggression_still_unrewarded","target_is_balance_low","target_is_prior_opposite_control","requires_lift","prior_band_control","same_band_retest","fresh_same_side_defense","executed_aggression","refresh_consistent","control_side_matches_thesis","short_control","old_defense_keeps_control","microbalance_frozen","directional_strength","breakout_in_thesis_direction","stop_side_ok","stop_below_opposite","objective_preexists","preexisting_target","qualifies","kg1_known","entry_sequence","automatic_trailing","thesis_alive","preconfirmation_entry","small_risk_declared","stop_predefined","explicitly_early_entry","source_refill_return","source_risk_predefined","case_fidelity","deliberate_early","full_confirmed_branch_pass","confirmed_branch","thesis_killed_by_loss_alone","automatic_early_admission","inside_rows_are_one_test","same_support_band","no_new_buyer_defense","in_cohort","stopped_out","universal_third_touch","automatic_entry_selector","resistance_known","source_exhaustion","small_risk","short_case_fidelity","case_ok","automatic_full_trigger","bias_recorded","later_event_explains_bias","automatic_bias_selector"}
    if name in bool_names: return OutputField((bool,),True)
    if name in {"branch_id","band_id","side","candle_id","vwap_snapshot_id","band_snapshot_id","selected_band","target_snapshot_id","origin_id","buyers_area_id","balance_id","failed_area_id","target_id","thesis_id","microbalance_id","kg1_level_id","case_id","resistance_id","origin_reference_id","support_event_id","bias_side","direction","candidate_side"}: return OutputField((str,),True)
    return OutputField((Decimal,),True)


OUTPUT_SCHEMAS={
    rid:{name:OutputField(_field(name).types, nullable=True) for name in names}
    for rid,names in FLOW_SEQUENCE_SCHEMAS.items()
}

__all__=["DERIVED_PARENT_ROLES","DERIVED_PRODUCERS","FLOW_SEQUENCE_SCHEMAS","NATIVE_PRODUCERS","OUTPUT_SCHEMAS","REGISTRATION_OVERRIDES","REQUIRED_INPUTS"]
