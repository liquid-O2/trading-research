"""P15-15 Keani ordered opening-value branch."""
from __future__ import annotations

from typing import Any, Mapping

from trading_research.research.contracts.types import RuleSpec
from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    dispatch_scan_variant,
    register_family_transform,
    scan_family_date,
)

FAMILY = "KEANI-OPEN-ABOVE-VALUE"
BRANCHES = FAMILY_BRANCHES[FAMILY]
FINDINGS = ("C4",)


def family_document() -> dict[str, Any]:
    return {
        "schema_version": "research-family-spec-v1",
        "family": FAMILY,
        "task_id": "P15-15",
        "branches": list(BRANCHES),
        "findings": list(FINDINGS),
        "clock_zone_unverified": True,
        "c4": "rejection wick into developing POC or prior-day VAH; developing-VAL remains B0",
    }


def a_period_trade_below_vah_invalidates(low, vah) -> bool:
    if low is None or vah is None:
        return False
    return low < vah


def value_after_break_cannot_satisfy_before(value_known_at: int, break_at: int) -> bool:
    return int(value_known_at) <= int(break_at)


def low_support_inconclusive(n: int, floor: int = 5) -> bool:
    return n < floor


def apply_keani_rules(document: Mapping[str, Any], market, branch: str, version: str) -> dict[str, Any]:
    """C4: A-period trade below VAH invalidates; value after the break cannot satisfy a before-break gate."""
    out = dict(document)
    kept = []
    for episode in list(out.get("episodes") or []):
        row = dict(episode)
        values = dict(row.get("values") or {})
        a_low = values.get("a_low")
        vah = values.get("prior_vah")
        values["a_period_below_vah_invalidates"] = a_period_trade_below_vah_invalidates(a_low, vah)
        if values["a_period_below_vah_invalidates"]:
            values["whole_period_above_vah"] = False
        break_at = values.get("breakout_at")
        value_at = values.get("dev_vah_known_at")
        if break_at is not None and value_at is not None:
            values["value_known_before_break"] = value_after_break_cannot_satisfy_before(value_at, break_at)
            if values["value_known_before_break"] is False:
                values["value_after_break_rejected"] = True
        n = values.get("support_n") or values.get("n") or (row.get("geometry") or {}).get("support_n")
        if n is not None:
            values["low_support_inconclusive"] = low_support_inconclusive(int(n))
        values["c4_rejection_levels"] = (row.get("geometry") or {}).get("rejection_level")
        values["keani_adapter_rules"] = True
        row["values"] = values
        kept.append(row)
    out["episodes"] = kept
    out["keani_adapter_rules"] = True
    out["baseline_version"] = version
    return out


register_family_transform(FAMILY, apply_keani_rules)


def confirm_at_contact(market, *, branch, contact, reference, formation=None, changed_axis="none", view=None) -> dict[str, Any]:
    """Unchanged Keani stages from B0.1; defense uses the candidate band when the axis changed."""
    from decimal import Decimal as D

    from trading_research.research.method_pack.branch_coverage import setting
    from trading_research.research.method_pack.historical_features import MINUTE, Q, first_contact
    from trading_research.research.method_pack.historical_flow import exact_contact, flow_stages
    from trading_research.research.rule_discovery.baseline_repairs import absent_repaired, flow_absent_repaired, local_observations_repaired
    from trading_research.research.rule_discovery.source_adapters.confirmation import bounds, scanner_ref

    prior = market.prior("day")
    old = prior["sessions"][-1]["window"] if prior.get("sessions") else None
    p = old.profile(old.start, old.end) if old else None
    a = market.range(market.at("09:30"), market.at("10:00"), "Keani-A")
    if a is None:
        decision = int(market.end)
        return {
            "values": {"branch": branch, "side": "long", "a_period_complete": None, "source_confirmation": None, "decision_at": decision},
            "confirm_at": None,
            "decision_at": decision,
            "cutoff_ns": decision,
            "source_confirmation": None,
        }
    initial = market.profile(a["start"], a["end"])
    limit = market.at(setting("keani_time")["latest_break"])
    observation = breakout = band = retest = defense = exact = obs = None
    dev = None
    for row in market.bars(a["end"], limit):
        current = market.profile(a["start"], row["start"])
        higher = current["val"] is not None and initial["val"] is not None and current["val"] > initial["val"] and current["vah"] >= initial["vah"]
        poc = current.get("poc")
        prior_vah = p["vah"] if p and p.get("vah") is not None and prior.get("scope_complete") else None
        hit_poc = poc is not None and row["C"] is not None and row["L"] <= poc and row["C"] > poc
        hit_vah = prior_vah is not None and row["C"] is not None and row["L"] <= prior_vah and row["C"] > prior_vah
        rejection = higher and row["C"] is not None and (hit_poc or hit_vah)
        if observation is None and rejection:
            observation = row
            continue
        if observation and row.get("observed_complete") and row["C"] is not None and current["vah"] is not None and row["C"] > current["vah"]:
            footprint = market.window.footprints.get(row["start"])
            if not footprint or any(u > 0 for _px, _b, _s, u in footprint["rows"]):
                continue
            cfg = setting("imbalance")
            im = market.domain(
                "O109",
                {
                    "candle_id": row["bar_id"],
                    "footprint_rows": [{"price": px, "B": b, "A": s} for px, b, s, u in footprint["rows"]],
                    "q": Q,
                    "ratio_min": D(str(cfg["ratio"])),
                    "row_count": cfg["consecutive_rows"],
                    "zero_rule": cfg["zero"],
                    "known_at": row["known_at"],
                },
            )
            runs = im.get("buy_runs", [])
            if runs:
                breakout = row
                dev = current
                band = [D(str(v)) for v in runs[0]["band"]]
                break
    cand_lo, cand_hi = bounds(scanner_ref(reference, formation))
    if changed_axis not in {"none", "baseline", ""} and cand_lo is not None and cand_hi is not None:
        band = [cand_lo, cand_hi]
    if breakout and band:
        retest = first_contact(market.bars(breakout["end"], min(int(market.end), breakout["end"] + 60 * MINUTE)), *band)
        if retest:
            exact = exact_contact(market, retest, *band)
            if exact:
                obs = local_observations_repaired(market, exact["at"], band, "long")
                defense = flow_stages(obs)["defense"]
    absent_stage = absent_repaired(market, a["end"], limit, fields=("C",))
    decision = defense["known_at"] if defense else min(int(market.end), limit + 60 * MINUTE)
    absent_defense = (
        flow_absent_repaired(market, retest["start"], min(int(market.end), ((int(decision) + MINUTE - 1) // MINUTE) * MINUTE), [r for r in obs["chunks"] if r["known_at"] <= decision])
        if obs
        else absent_stage
    )
    values = {
        "branch": branch,
        "side": "long",
        "prior_value_fixed": True if p and p.get("vah") is not None and prior.get("scope_complete") else None,
        "prior_vah": p["vah"] if p and prior.get("scope_complete") else None,
        "a_period_complete": True if a["coverage"]["observed_scope_complete"] else None,
        "a_low": a["low"],
        "a_end_at": a["known_at"],
        "developing_value_builds_higher": True if observation else absent_stage,
        "source_rejection_observed": True if observation else absent_stage,
        "observation_at": observation["known_at"] if observation else None,
        "dev_vah_known_at": dev["known_at"] if dev else None,
        "dev_vah_at_break": dev["vah"] if dev else None,
        "breakout_at": breakout["known_at"] if breakout else None,
        "breakout_close": breakout["C"] if breakout else None,
        "aggressive_buy_imbalance_break": True if breakout else absent_stage,
        "imbalance_band_known_at": breakout["known_at"] if breakout else None,
        "retest_at": exact["at"] if exact else None,
        "defense_at": defense["known_at"] if defense else None,
        "buyers_defend_same_imbalance_band": defense["held"] if defense else absent_defense,
        "dom_supports_long": defense["displayed_defense"] if defense else absent_defense,
        "time_of_day_allowed": breakout["known_at"] <= limit if breakout else absent_stage,
        "objective_fixed": None,
        "risk_defined": None,
        "decision_at": decision,
        "confirm_at": defense["known_at"] if defense else None,
        "source_confirmation": True if defense else absent_defense,
    }
    return {"values": values, "confirm_at": values["confirm_at"], "decision_at": decision, "cutoff_ns": decision, "source_confirmation": values["source_confirmation"]}


def scan_variant(market, view, spec: RuleSpec) -> dict[str, Any]:
    return dispatch_scan_variant(market, view, spec)


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-15"
    payload["findings"] = list(FINDINGS)
    payload["clock_zone_unverified"] = clock_zone_unverified(FAMILY)
    payload["population_kind"] = "engineering_slice"
    payload["adapter_rules_applied"] = True
    return payload


from decimal import Decimal as _D

from trading_research.research.rule_discovery.source_adapters.b02_saint_track import (
    Q as B02_Q,
    cascade_stages,
    combine_verdict,
    dec,
    episode_doc,
    export_rules,
    first_touch,
    fixtures,
    market_at,
    market_bars,
    outside_native_tape,
    parse_rec,
    replay_match,
    replay_unavailable,
    stage,
    window_doc,
)

RULES = {
    "F16-a-period": {"kind": "literal", "source": "TPO p.3"},
    "F16-observation-1000": {"kind": "literal", "source": "AVG p.21"},
    "F16-no-1100-cutoff": {"kind": "literal", "source": "F16"},
    "F16-no-60m-expiry": {"kind": "literal", "source": "F16"},
    "F16-no-val-rise": {"kind": "literal", "source": "F16"},
    "F16-open-above-value": {"kind": "literal", "source": "AVG pp.21-22"},
    "F16-rejection-poc-or-prior-vah": {
        "kind": "literal",
        "source": "AVG p.21",
        "unresolved": "AVG p.22 caption draws rejection at POC and prior VAH (AND). AVG p.21 prose is OR (POC or prior VAH). B0.2 implements the p.21 OR reading. The p.21/p.22 conflict is unresolved.",
        "conflict": "p.21 OR vs p.22 AND",
    },
    "F16-imbalance-vah-break": {"kind": "OD", "source": "OD:O109 buy run or synth fixture band (AVG pp.21-28)"},
    "F16-defended-retest": {"kind": "literal", "source": "AVG pp.21-28"},
    "F16-three-tick-reward": {"kind": "literal", "source": "AVG p.24"},
    "F16-htf-objective": {"kind": "OD", "source": "OD:nearest of prior-day high, prior VAH, weekly high above (F16)"},
}


def _rules():
    return export_rules(RULES, RULE_FNS)


def _prior_profile(market):
    fx = fixtures(market)
    if fx.get("prior_vah") is not None or fx.get("prior_day_high") is not None:
        return {
            "vah": fx.get("prior_vah"),
            "high": fx.get("prior_day_high"),
            "scope_complete": True,
        }
    try:
        prior = market.prior("day")
        if not prior.get("sessions"):
            return {}
        win = prior["sessions"][-1]["window"]
        rng = prior.get("range") or {}
        vah = None
        try:
            rth_start = win.at("09:30") if hasattr(win, "at") else None
            rth_end = win.at("16:00") if hasattr(win, "at") else None
        except Exception:
            rth_start = rth_end = None
        if rth_start is not None and rth_end is not None:
            p70 = win.profile(rth_start, rth_end, ".70")
            if p70 and p70.get("vah") is not None:
                vah = p70.get("vah")
        if vah is None:
            p = win.profile(win.start, win.end)
            vah = p.get("vah") if p else None
        return {"vah": vah, "high": rng.get("high"), "scope_complete": prior.get("scope_complete"), "value_fraction": "0.70"}
    except Exception:
        return {}


def _weekly_high(market):
    fx = fixtures(market)
    if fx.get("weekly_high") is not None:
        return dec(fx["weekly_high"])
    try:
        prior = market.prior("week")
        rng = (prior or {}).get("range") or {}
        if rng.get("high") is not None:
            return dec(rng["high"])
    except Exception:
        return None
    return None


def _nearest_htf(entry, prior_day_high, prior_vah, weekly_high):
    candidates = []
    for name, level in (("prior_day_high", prior_day_high), ("prior_vah", prior_vah), ("weekly_high", weekly_high)):
        if level is None:
            continue
        px = dec(level)
        if px > dec(entry):
            candidates.append((px - dec(entry), name, px))
    if not candidates:
        return None, None
    _dist, name, px = min(candidates)
    return name, px


def scan_keani_branch_b02(market, branch: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    a_start = market_at(market, "09:30")
    a_end = market_at(market, "10:00")
    a = None
    try:
        a = market.range(a_start, a_end, "Keani-A")
    except Exception:
        a = None
    fx = fixtures(market)
    if fx.get("a_period"):
        a = dict(fx["a_period"])
        a.setdefault("start", a_start)
        a.setdefault("end", a_end)
    prior = _prior_profile(market)
    prior_vah = prior.get("vah")
    prior_high = prior.get("high")
    weekly = _weekly_high(market)
    fully_above = False
    if a is not None and prior_vah is not None and a.get("low") is not None:
        # SD11: equality of A low with prior VAH fails the strict fully-above condition. AVG p.21.
        fully_above = dec(a["low"]) > dec(prior_vah)
    extra = {
        "fully_above_a_eligible": 1 if fully_above else 0,
        "a_period": ["09:30", "10:00"],
        "cutoff_1100": False,
        "retest_expiry_60m": False,
        "val_rise_required": False,
        "value_fraction": prior.get("value_fraction") or "0.70",
        "prior_session": ["09:30", "16:00"],
    }
    ctx = stage(
        "context",
        "pass" if fully_above else ("unknown" if a is None or prior_vah is None else "fail"),
        a_end,
        {
            "a_low": str(a["low"]) if a and a.get("low") is not None else None,
            "prior_vah": str(prior_vah) if prior_vah is not None else None,
            "a_period": "09:30-10:00",
            "fully_above": fully_above,
            "strict_gt": True,
            "value_fraction": extra["value_fraction"],
        },
    )
    ref = stage("reference", "pass" if prior_vah is not None else "unknown", a_end, {"prior_vah": str(prior_vah) if prior_vah is not None else None})
    if a is None:
        stages = cascade_stages([ctx, ref])
        verdict, failed, unknown = combine_verdict(stages)
        ep = episode_doc(
            family=FAMILY,
            branch=branch,
            side="long",
            market=market,
            verdict=verdict,
            failed=failed,
            unknown=unknown,
            stages=stages,
            rules=_rules(),
            values={"a_period_complete": False},
            decision_at=a_end,
        )
        return [ep], extra
    bars = market_bars(market, a_end, getattr(market, "end", a_end), 60)
    observation = None
    breakout = None
    band = fx.get("imbalance_band")
    if band:
        band = [dec(band[0]), dec(band[1])]
    for row in bars:
        current = None
        try:
            current = market.profile(a["start"], row["start"])
        except Exception:
            current = fx.get("developing_profile")
        poc = None if current is None else current.get("poc")
        hit_poc = poc is not None and row.get("C") is not None and row.get("L") is not None and dec(row["L"]) <= dec(poc) and dec(row["C"]) > dec(poc)
        hit_vah = prior_vah is not None and row.get("C") is not None and row.get("L") is not None and dec(row["L"]) <= dec(prior_vah) and dec(row["C"]) > dec(prior_vah)
        if observation is None and (hit_poc or hit_vah):
            observation = dict(row)
            observation["rejection_level"] = "developing_poc" if hit_poc else "prior_day_vah"
            continue
        if observation and (row.get("observed_complete") or row.get("complete")) and row.get("C") is not None:
            vah = None if current is None else current.get("vah")
            if vah is not None and dec(row["C"]) > dec(vah):
                runs = []
                try:
                    im = market.domain("O109", {"candle_id": row.get("bar_id")})
                    runs = im.get("buy_runs") or []
                except Exception:
                    runs = []
                if fx.get("imbalance_band") is not None:
                    runs = [{"band": fx["imbalance_band"]}]
                if runs or fx.get("imbalance_band") is not None:
                    breakout = row
                    if runs and not band:
                        band = [dec(v) for v in runs[0]["band"]]
                    break
    loc = stage(
        "location",
        "pass" if observation else ("fail" if bars else "unknown"),
        int(observation.get("known_at") or observation["end"]) if observation else a_end,
        {
            "rejection": None if observation is None else observation.get("rejection_level"),
            "val_rise_required": False,
            "poc_or_prior_vah": "OR",
            "p22_and_unresolved": True,
        },
    )
    trig = stage(
        "trigger",
        "pass" if breakout else "fail",
        int(breakout.get("known_at") or breakout["end"]) if breakout else None,
        {"breakout": True if breakout else False, "cutoff_1100": False},
    )
    retest = None
    reward = None
    if breakout and band:
        after = [r for r in bars if int(r["start"]) >= int(breakout["end"])]
        retest = first_touch(after, band[0], band[1])
        if retest:
            later = [r for r in after if int(r["start"]) >= int(retest["end"])]
            need = dec(retest.get("C") or band[1]) + B02_Q * 3
            for row in later:
                if row.get("C") is not None and dec(row["C"]) >= need:
                    if row.get("L") is None or dec(row["L"]) >= dec(band[0]) - B02_Q:
                        reward = row
                        break
    conf_verdict = "fail"
    if retest and reward:
        conf_verdict = "pass"
    elif retest and not reward:
        conf_verdict = "fail"
    elif breakout and not retest:
        conf_verdict = "fail"
    conf = stage(
        "confirmation",
        conf_verdict,
        int((reward or retest or breakout).get("known_at") or (reward or retest or breakout)["end"]) if (reward or retest or breakout) else None,
        {"retest": True if retest else False, "three_tick_reward": True if reward else False, "expiry_60m": False},
    )
    entry = dec((retest or breakout or {}).get("C") or (a.get("high") if a else 0))
    stop = (band[0] - B02_Q) if band else (dec(a["low"]) - B02_Q if a.get("low") is not None else None)
    name, target = _nearest_htf(entry, prior_high, prior_vah, weekly)
    used_a_width = False
    if target is None:
        obj_verdict = "unknown"
    else:
        obj_verdict = "pass"
    obj = stage("objective", obj_verdict, a_end, {"selector": name, "target": str(target) if target is not None else None, "a_high_plus_a_width": used_a_width})
    risk = stage("risk", "pass" if entry is not None and stop is not None and entry > stop else "unknown", a_end, {"stop": str(stop) if stop is not None else None, "entry": str(entry)})
    stages = cascade_stages([ctx, ref, loc, trig, conf, risk, obj])
    verdict, failed, unknown = combine_verdict(stages)
    decision = int((reward or retest or breakout or {"known_at": a_end}).get("known_at") or a_end)
    values = {
        "a_period": "09:30-10:00",
        "time_of_day_allowed": True,
        "val_rise_required": False,
        "three_tick_reward": True if reward else False,
        "objective_kind": name,
        "a_high_plus_a_width": False,
        "cutoff_1100": False,
        "retest_expiry_60m": False,
    }
    ep = episode_doc(
        family=FAMILY,
        branch=branch,
        side="long",
        market=market,
        verdict=verdict,
        failed=failed,
        unknown=unknown,
        stages=stages,
        rules=_rules(),
        values=values,
        decision_at=decision,
        reference=a,
        trigger=breakout or observation or {},
        geometry={"entry": entry, "stop": stop, "target": target, "imbalance_band": band},
    )
    return [ep], extra


def scan_b02(market, rec) -> dict[str, Any]:
    family, branches = parse_rec(rec, FAMILY, BRANCHES)
    episodes = []
    extra = {"family": family, "branches": list(branches), "fully_above_a_eligible": 0}
    for branch in branches:
        eps, meta = scan_keani_branch_b02(market, branch)
        episodes.extend(eps)
        extra.update(meta)
    rules = _rules()
    for episode in episodes:
        episode["rules"] = rules
    branch = branches[0] if len(branches) == 1 else None
    return window_doc(FAMILY, branch, market, episodes, rules, extra=extra)


def replay_example(market, example) -> dict[str, Any]:
    expected = (example or {}).get("expected_detection") or {}
    if not example or example.get("id") is None:
        out = replay_unavailable(example, "no dated example")
        out["branch"] = "source_long"
        return out
    if outside_native_tape(example):
        return replay_unavailable(example, "date outside the tape")
    if market is None:
        return replay_unavailable(example, "date outside the tape")
    doc = scan_b02(market, {"family": FAMILY, "branch": "source_long"})
    return replay_match(doc, example)


RULE_FNS = {
    "F16-a-period": scan_keani_branch_b02,
    "F16-observation-1000": scan_keani_branch_b02,
    "F16-no-1100-cutoff": scan_keani_branch_b02,
    "F16-no-60m-expiry": scan_keani_branch_b02,
    "F16-no-val-rise": scan_keani_branch_b02,
    "F16-open-above-value": scan_keani_branch_b02,
    "F16-rejection-poc-or-prior-vah": scan_keani_branch_b02,
    "F16-imbalance-vah-break": scan_keani_branch_b02,
    "F16-defended-retest": scan_keani_branch_b02,
    "F16-three-tick-reward": scan_keani_branch_b02,
    "F16-htf-objective": _nearest_htf,
}

