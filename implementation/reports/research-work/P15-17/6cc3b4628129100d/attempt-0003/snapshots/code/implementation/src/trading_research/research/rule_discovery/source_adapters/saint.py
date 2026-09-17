"""P15-13 Saint auction alignment branches."""
from __future__ import annotations

from typing import Any, Mapping

from trading_research.research.contracts.types import RuleSpec
from trading_research.research.rule_discovery.source_adapters.enumeration import (
    enumeration_point,
    enumeration_scope,
    split_b02_overrides,
)
from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    dispatch_scan_variant,
    register_family_transform,
    scan_family_date,
)

FAMILY = "SAINT-AMT"
BRANCHES = FAMILY_BRANCHES[FAMILY]
FINDINGS = ("C7-arrival", "C7-alignment", "C7-profile")


def family_document() -> dict[str, Any]:
    return {
        "schema_version": "research-family-spec-v1",
        "family": FAMILY,
        "task_id": "P15-13",
        "branches": list(BRANCHES),
        "findings": list(FINDINGS),
        "clock_zone_unverified": True,
        "operational_rules": {
            "arrival_read_recorded": "first HTF-balance contact bar exists and is complete before confirmation",
            "alignment_ok": "LTF break direction equals the trade side",
            "profile_allows_trade": "HTF 68% POC lies inside the HTF balance",
        },
        "label": "operational",
    }


def evaluate_arrival_read(*, trigger_complete: bool, trigger_before_confirm: bool) -> bool:
    return bool(trigger_complete and trigger_before_confirm)


def evaluate_ltf_alignment(*, side: str, ltf_break_up: bool | None) -> bool | None:
    if ltf_break_up is None:
        return None
    if side == "long":
        return bool(ltf_break_up)
    if side == "short":
        return not bool(ltf_break_up)
    return None


def evaluate_profile_permission(*, poc, low, high) -> bool | None:
    if poc is None or low is None or high is None:
        return None
    return bool(low <= poc <= high)


def _ltf_break_up_from_bars(episode: Mapping[str, Any]) -> bool | None:
    """LTF break direction from the trigger close versus the LTF balance, not from trade side."""
    trigger = episode.get("trigger") or {}
    ltf = (episode.get("geometry") or {}).get("ltf_balance") or {}
    close = trigger.get("C")
    high, low = ltf.get("high"), ltf.get("low")
    if close is None or high is None or low is None:
        return None
    if close > high:
        return True
    if close < low:
        return False
    return None


def apply_operational_stages(episode: Mapping[str, Any], market=None) -> dict[str, Any]:
    """Evaluate arrival, LTF alignment and profile permission from bars/profile geometry."""
    values = dict(episode.get("values") or {})
    geometry = episode.get("geometry") or {}
    profile = geometry.get("htf_profile") or {}
    trigger = episode.get("trigger") or {}
    ref = episode.get("reference") or geometry.get("htf_balance") or {}
    side = str(episode.get("side") or values.get("side") or "")
    complete = bool(trigger.get("observed_complete") or trigger.get("complete"))
    trigger_at = trigger.get("known_at") or trigger.get("end")
    confirm_at = values.get("confirm_at")
    if not trigger or trigger_at is None:
        arrival = None
    elif confirm_at is None:
        arrival = None
    else:
        before = int(trigger_at) <= int(confirm_at)
        arrival = evaluate_arrival_read(trigger_complete=complete, trigger_before_confirm=before)
    alignment = evaluate_ltf_alignment(side=side, ltf_break_up=_ltf_break_up_from_bars(episode))
    permission = evaluate_profile_permission(poc=profile.get("poc"), low=ref.get("low"), high=ref.get("high"))
    if permission is None and profile.get("poc") is not None:
        htf = geometry.get("htf_balance") or {}
        permission = evaluate_profile_permission(poc=profile.get("poc"), low=htf.get("low") or ref.get("low"), high=htf.get("high") or ref.get("high"))
    if market is not None and permission is None and ref.get("start") is not None and ref.get("known_at") is not None:
        live = market.profile(ref["start"], ref["known_at"], ".68")
        permission = evaluate_profile_permission(poc=live.get("poc"), low=ref.get("low"), high=ref.get("high"))
    values["arrival_read_recorded"] = arrival
    values["alignment_ok"] = alignment
    values["profile_allows_trade"] = permission
    values["operational_rule_label"] = "operational"
    return values


def reassess_episode(episode: Mapping[str, Any]) -> dict[str, Any]:
    from trading_research.research.method_pack.catalog import PRIMARY
    from trading_research.research.method_pack.expressions import evaluate
    from trading_research.research.method_pack.strategy_policy import EXCLUDED, POLICY, observation_scope

    out = dict(episode)
    method = str(out.get("method") or out.get("method_id") or FAMILY)
    predicate = out.get("predicate") or PRIMARY[method]
    values = out.get("values") or {}
    try:
        source_result = evaluate(method, predicate, values)
        excluded = EXCLUDED.get(method, frozenset())
        result = evaluate(method, predicate, values, excluded_fields=excluded)
    except (ValueError, KeyError, TypeError):
        return out
    scope = observation_scope(method, out.get("branch"))
    status = {True: "setup", False: "no_setup", None: "data_unavailable"}[result.value]
    if scope != "entry_setup":
        status = {True: "condition_present", False: "condition_absent", None: "data_unavailable"}[result.value]
    strategy = dict(out.get("strategy_assessment") or {})
    strategy.update(
        {
            "version": POLICY["version"],
            "scope": scope,
            "status": status,
            "failed_conditions": result.failed,
            "unavailable_conditions": result.unknown,
        }
    )
    out["strategy_assessment"] = strategy
    out["research_verdict"] = {True: "pass", False: "fail", None: "unknown"}[result.value]
    out["failed"] = result.failed
    out["unknown"] = result.unknown
    out["source_contract_verdict"] = {True: "pass", False: "fail", None: "unknown"}[source_result.value]
    return out


def bind_saint_operational(document: Mapping[str, Any], market, branch: str, version: str) -> dict[str, Any]:
    """Bind C7 operational stages into B0.1 episode verdicts from actual geometry. Not applied to B0."""
    from trading_research.research.rule_discovery.source_adapters.common import episode_status

    out = dict(document)
    episodes = []
    arrival_none = 0
    status_changed = 0
    for episode in list(out.get("episodes") or []):
        row = dict(episode)
        old_status = episode_status(row)
        row["values"] = apply_operational_stages(row, market=market)
        if row["values"].get("arrival_read_recorded") is None:
            arrival_none += 1
        new_row = reassess_episode(row)
        if episode_status(new_row) != old_status:
            status_changed += 1
        episodes.append(new_row)
    out["episodes"] = episodes
    out["saint_operational_bound"] = True
    out["baseline_version"] = version
    out["arrival_none_count"] = arrival_none
    out["status_changed_from_arrival_none"] = status_changed
    return out


register_family_transform(FAMILY, bind_saint_operational)


def confirm_at_contact(market, *, branch, contact, reference, formation=None, changed_axis="none", view=None) -> dict[str, Any]:
    """Two-bar body/delta control after the contact, then operational stages."""
    from trading_research.research.method_pack.historical_auction_scanners import _control
    from trading_research.research.method_pack.historical_features import MINUTE, Q, sign
    from trading_research.research.rule_discovery.baseline_repairs import _control_absence_repaired
    from trading_research.research.rule_discovery.source_adapters.confirmation import (
        contact_as_trigger,
        contact_side,
        scanner_ref,
    )

    trigger = contact_as_trigger(market, contact)
    side = contact_side(contact)
    sg = sign(side)
    ref = scanner_ref(reference, formation)
    end = min(int(market.end), int(trigger["end"]) + 60 * MINUTE)
    lo, hi = ref.get("low"), ref.get("high")
    boundary = hi if side == "long" else lo
    retest_hi = (boundary + Q) if boundary is not None else None
    retest_lo = (boundary - Q) if boundary is not None else None
    from trading_research.research.method_pack.historical_features import first_contact

    retest = None
    if retest_lo is not None and retest_hi is not None:
        retest = first_contact(market.bars(trigger["end"], end), retest_lo, retest_hi)
    control, controlbars = _control(market, retest["end"] if retest else trigger["end"], end, side)
    decision = control["known_at"] if control else end
    entry = control["C"] if control else None
    stop = None
    if lo is not None and hi is not None:
        stop = lo - Q if side == "long" else hi + Q
    target = hi if side == "long" else lo
    confirm_at = control["known_at"] if control else None
    profile = None
    if ref.get("start") is not None and ref.get("known_at") is not None:
        profile = market.profile(ref["start"], ref["known_at"], ".68")
    permission = None
    if profile and profile.get("poc") is not None and lo is not None and hi is not None:
        permission = lo <= profile["poc"] <= hi
    arrival = None
    trigger_at = trigger.get("known_at") or trigger.get("end")
    complete = bool(trigger.get("observed_complete") or trigger.get("complete"))
    if trigger_at is None:
        arrival = None
    elif confirm_at is None:
        arrival = None
    else:
        arrival = bool(complete and int(trigger_at) <= int(confirm_at))
    alignment = None
    close = trigger.get("C")
    if close is not None and lo is not None and hi is not None:
        if close > hi:
            alignment = side == "long"
        elif close < lo:
            alignment = side == "short"
    held = None
    if retest and control and boundary is not None:
        held = all(
            r["L"] >= boundary - Q * 2 if side == "long" else r["H"] <= boundary + Q * 2
            for r in market.bars(retest["start"], control["end"])
        )
    values = {
        "branch": branch,
        "side": side,
        "balance_fixed_before_use": True if ref.get("known_at") is not None else None,
        "balance_known_at": ref.get("known_at"),
        "profile_allows_trade": permission,
        "arrival_read_recorded": arrival,
        "arrival_at": trigger.get("start"),
        "control_evidence_recorded": True if control else _control_absence_repaired(market, retest["end"] if retest else trigger["end"], end, side),
        "control_at": confirm_at,
        "alignment_ok": True if control else alignment,
        "risk_defined": None if entry is None or stop is None else sg * (entry - stop) > 0,
        "objective_fixed": None if entry is None or target is None else sg * (target - entry) > 0,
        "ltf_balance_broken": True,
        "ltf_balance_known_at": ref.get("known_at"),
        "breakout_at": trigger.get("known_at") or trigger.get("end"),
        "same_boundary_retest_held": held if retest else None,
        "repeated_aggression_in_trade_direction": True if control else _control_absence_repaired(market, retest["end"] if retest else trigger["end"], end, side),
        "retest_at": retest["start"] if retest else None,
        "confirm_at": confirm_at,
        "decision_at": decision,
        "source_confirmation": True if control else None,
    }
    return {"values": values, "confirm_at": confirm_at, "decision_at": decision, "cutoff_ns": decision, "source_confirmation": values["source_confirmation"]}


def scan_variant(market, view, spec: RuleSpec) -> dict[str, Any]:
    return dispatch_scan_variant(market, view, spec)


def later_htf_cannot_explain_earlier_retest(htf_known_at: int, retest_at: int) -> bool:
    return int(htf_known_at) <= int(retest_at)


def ltf_without_htf_does_not_qualify(htf_known: bool, ltf_agree: bool) -> bool:
    return bool(htf_known) and bool(ltf_agree)


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-13"
    payload["operational_rules"] = family_document()["operational_rules"]
    payload["clock_zone_unverified"] = clock_zone_unverified(FAMILY)
    payload["leaves_unknown"] = False
    payload["population_kind"] = "engineering_slice"
    payload["operational_bound"] = True
    payload["arrival_none_count"] = sum(int(scan.get("arrival_none_count") or 0) for scan in payload.get("scans") or [])
    payload["status_changed_from_arrival_none"] = sum(
        int(scan.get("status_changed_from_arrival_none") or 0) for scan in payload.get("scans") or []
    )
    return payload


# B0.2-2026-09-15. Finding ids in rule_id. Does not run on B0/B0.1 paths.
from decimal import Decimal as _D, InvalidOperation as _InvalidOperation

from trading_research.research.rule_discovery.source_adapters.b02_saint_track import (
    B02_VERSION,
    FixtureMarket,
    Q as B02_Q,
    account_day_for_example,
    as_balance,
    bar_complete,
    bars_upto,
    cascade_stages,
    combine_verdict,
    dec,
    episode_doc,
    export_rules,
    first_touch,
    first_true_break,
    fixtures,
    market_at,
    market_bars,
    market_day,
    outside_native_tape,
    parse_rec,
    replay_match,
    replay_unavailable,
    retest_held,
    stage_from,
    window_doc,
)

ARRIVAL_BARS = 5
ARRIVAL_FAST_RATIO = _D("0.08")
SHAPE_MID_FRAC = _D("0.35")
SHAPE_VA_SPAN = _D("0.90")
BALANCE_COVER = _D("0.55")

RULES = {
    "F04-arrival_read": {
        "kind": "OD",
        "source": "OD:approach_bars=5,fast_ratio=0.08 of balance_width (WIC p.4)",
    },
    "F04-profile_allows_trade": {
        "kind": "OD",
        "source": "OD:shape classifier mid_volume_frac/poc_pos (RTVP pp.6-11)",
    },
    "F04-double-shelf-target": {"kind": "literal", "source": "RTVP p.8"},
    "F04-alignment_ok": {
        "kind": "OD",
        "source": "OD:HTF value-migration vs 15m break, never from trade side (WIC pp.5-10)",
    },
    "F05-failed_auction_return": {"kind": "literal", "source": "AMTL p.8"},
    "F05-poc_traversal": {"kind": "literal", "source": "AMTL p.9; RTVP p.5"},
    "RR-22-asia-session": {"kind": "literal", "source": "TRAP pp.3-10"},
    "RR-22-balance-fit": {
        "kind": "OD",
        "source": "OD:cover_frac>=0.55 else latest confirmed (TRAP p.3)",
    },
    "RR-22-single-retest": {"kind": "literal", "source": "TRAP pp.6-7"},
    "RR-22-asia-range": {"kind": "literal", "source": "TRAP p.8"},
    "RR-22-long-mirror": {"kind": "literal", "source": "TRAP long mirror as ruled"},
}


def _bar_px(row, key):
    """Decimal OHLC/delta or None. Missing/non-numeric is not a comparable price."""
    value = row.get(key) if isinstance(row, Mapping) else None
    if value is None:
        return None
    try:
        return dec(value)
    except (_InvalidOperation, TypeError, ValueError):
        return None


def classify_arrival(approach_bars, balance_width):
    """F04. Fast if mean |C-O| / width >= 0.08. WIC p.4."""
    if not approach_bars or balance_width is None or dec(balance_width) <= 0:
        return None, None
    bodies = []
    for row in approach_bars:
        if row.get("C") is None or row.get("O") is None:
            continue
        if not (row.get("observed_complete") or row.get("complete")):
            continue
        bodies.append(abs(dec(row["C"]) - dec(row["O"])))
    if not bodies:
        return None, None
    ratio = (sum(bodies) / _D(len(bodies))) / dec(balance_width)
    return ("fast" if ratio >= ARRIVAL_FAST_RATIO else "slow"), ratio


def classify_profile_shape(profile, low, high):
    """F04. Trending excluded. RTVP pp.6-11."""
    if profile is None or low is None or high is None:
        return None, None
    width = dec(high) - dec(low)
    if width <= 0:
        return None, None
    rows = list(profile.get("rows") or [])
    poc = profile.get("poc")
    total = sum(int(r.get("total_volume") or r.get("volume") or 0) for r in rows)
    mid_lo = dec(low) + width * _D("0.25")
    mid_hi = dec(high) - width * _D("0.25")
    mid = 0
    for row in rows:
        px = row.get("price")
        if px is None:
            continue
        if mid_lo <= dec(px) <= mid_hi:
            mid += int(row.get("total_volume") or row.get("volume") or 0)
    mid_frac = (_D(mid) / _D(total)) if total else None
    va_span = None
    vah, val = profile.get("vah"), profile.get("val")
    if vah is not None and val is not None:
        va_span = (dec(vah) - dec(val)) / width
    poc_pos = ((dec(poc) - dec(low)) / width) if poc is not None else None
    peaks = sorted(
        ((dec(r["price"]), int(r.get("total_volume") or r.get("volume") or 0)) for r in rows if r.get("price") is not None),
        key=lambda item: item[1],
        reverse=True,
    )
    if len(peaks) >= 2 and peaks[1][1] > 0 and abs(peaks[0][0] - peaks[1][0]) >= width * _D("0.15"):
        lo_p, hi_p = sorted([peaks[0][0], peaks[1][0]])
        return "double", {"mid_frac": mid_frac, "poc_pos": poc_pos, "lower_shelf": lo_p, "upper_shelf": hi_p}
    trending = (mid_frac is not None and mid_frac < SHAPE_MID_FRAC) or (va_span is not None and va_span > SHAPE_VA_SPAN)
    if trending:
        return "trending", {"mid_frac": mid_frac, "va_span": va_span, "poc_pos": poc_pos}
    if poc_pos is not None and poc_pos >= _D("0.66"):
        return "P", {"mid_frac": mid_frac, "poc_pos": poc_pos}
    if poc_pos is not None and poc_pos <= _D("0.34"):
        return "b", {"mid_frac": mid_frac, "poc_pos": poc_pos}
    return "balanced", {"mid_frac": mid_frac, "poc_pos": poc_pos}


def opposite_shelf_near_edge(profile, side, low, high):
    """RTVP p.8. Long: lower edge of the upper shelf. Short: upper edge of the lower shelf."""
    shape, operands = classify_profile_shape(profile, low, high)
    if shape != "double" or not operands:
        return None, None
    lo_p = operands.get("lower_shelf")
    hi_p = operands.get("upper_shelf")
    if lo_p is None or hi_p is None:
        return None, None
    mid = (dec(lo_p) + dec(hi_p)) / 2
    lower_high = None
    upper_low = None
    for row in profile.get("rows") or []:
        px = row.get("price")
        if px is None:
            continue
        px = dec(px)
        if px < mid:
            lower_high = px if lower_high is None else max(lower_high, px)
        elif px > mid:
            upper_low = px if upper_low is None else min(upper_low, px)
    if side == "long":
        return "opposite_shelf_near_edge", upper_low
    return "opposite_shelf_near_edge", lower_high


def htf_control_direction(market, balance, decision_at):
    """F04. Value migration of the HTF balance, not the trade side. WIC pp.5-10."""
    fx = fixtures(market).get("htf_control")
    if fx in {"up", "down"}:
        return fx
    if balance is None or decision_at is None:
        return None
    session_start = int(getattr(market, "start", 0) or 0)
    bal_start = int(balance.get("start") or session_start)
    # HistoricalFeatures.bars returns [] when end <= start. A fitted balance
    # can start after the trigger; never invert the window (repair 2026-09-15).
    win_start = session_start if bal_start >= int(decision_at) else min(bal_start, int(decision_at))
    rows = bars_upto(market_bars(market, win_start, decision_at), decision_at)
    if not rows:
        rows = bars_upto(market_bars(market, session_start, decision_at), decision_at)
    if not rows or rows[-1].get("C") is None:
        return None
    mid = (dec(balance["low"]) + dec(balance["high"])) / 2
    close = dec(rows[-1]["C"])
    if close > mid:
        return "up"
    if close < mid:
        return "down"
    return None


def ltf_break_direction(trigger, balance, boundary=None):
    """LTF break of the traded level, not only the HTF box edges."""
    if trigger is None or trigger.get("C") is None:
        return None
    close = dec(trigger["C"])
    if boundary is not None:
        if close > dec(boundary):
            return "up"
        if close < dec(boundary):
            return "down"
        return None
    if balance is None:
        return None
    if close > dec(balance["high"]):
        return "up"
    if close < dec(balance["low"]):
        return "down"
    return None


def fit_balance(market):
    """RR-22. Redraw until it fits. TRAP p.3."""
    fx = as_balance(fixtures(market).get("balance"), known_at=int(getattr(market, "start", 0)), start=int(getattr(market, "start", 0)))
    if fx:
        fx["width"] = dec(fx["high"]) - dec(fx["low"])
        return fx, "fixture"
    try:
        from trading_research.research.method_pack.historical_auction_scanners import balances, primary_balance

        ref, found = primary_balance(market)
        rows = list(found or [])
        if not rows:
            rows = list(balances(market_bars(market, market.start, market.end, 300)) or [])
        known_end = market_at(market, "09:30") if hasattr(market, "at") or getattr(market, "day", None) else int(getattr(market, "end", 0))
        known = [r for r in rows if r.get("known_at") is not None and int(r["known_at"]) <= int(known_end)]
        pool = known or rows
        session = market_bars(market, market.start, min(int(getattr(market, "end", 0)), int(known_end)))
        if session and pool:
            lo = min(dec(r["L"]) for r in session if r.get("L") is not None)
            hi = max(dec(r["H"]) for r in session if r.get("H") is not None)
            span = hi - lo
            best = None
            best_cover = _D("-1")
            for item in pool:
                width = dec(item["high"]) - dec(item["low"])
                if span <= 0:
                    cover = _D("0")
                else:
                    covered = min(dec(item["high"]), hi) - max(dec(item["low"]), lo)
                    cover = (covered / span) if covered > 0 else _D("0")
                if cover > best_cover or (cover == best_cover and best is not None and int(item.get("known_at") or 0) > int(best.get("known_at") or 0)):
                    best, best_cover = item, cover
            if best is not None and best_cover >= BALANCE_COVER:
                out = dict(best)
                out["width"] = dec(out["high"]) - dec(out["low"])
                return out, "cover"
        if ref is not None:
            out = dict(ref)
            out["width"] = dec(out["high"]) - dec(out["low"])
            return out, "primary"
        if pool:
            out = dict(pool[-1])
            out["width"] = dec(out["high"]) - dec(out["low"])
            return out, "latest"
    except Exception:
        pass
    return None, "missing"


def _approach_into(bars, extreme, side_extreme: str, before_ns: int):
    prior = [r for r in bars if int(r.get("known_at") or r["end"]) < int(before_ns)]
    if not prior:
        return []
    touching = []
    for row in reversed(prior):
        if side_extreme == "high" and row.get("H") is not None and dec(row["H"]) >= dec(extreme) - B02_Q * 4:
            touching.append(row)
        elif side_extreme == "low" and row.get("L") is not None and dec(row["L"]) <= dec(extreme) + B02_Q * 4:
            touching.append(row)
        if len(touching) >= ARRIVAL_BARS:
            break
    touching.reverse()
    return touching[-ARRIVAL_BARS:]


def _stage_profile(profile, balance):
    shape, operands = classify_profile_shape(profile, balance.get("low") if balance else None, balance.get("high") if balance else None)
    payload = {"shape": shape, "allows_trade": None if shape is None else shape != "trending", **(operands or {})}
    return stage_from("context", balance.get("known_at") if balance else None, payload, require=("allows_trade",))


def _rules():
    return export_rules(RULES, RULE_FNS)


def _finish(family, branch, side, market, stages, values, decision_at, reference, trigger, geometry):
    stages = cascade_stages(stages)
    verdict, failed, unknown = combine_verdict(stages)
    values = dict(values)
    values.setdefault("branch", branch)
    values.setdefault("side", side)
    return episode_doc(
        family=family,
        branch=branch,
        side=side,
        market=market,
        verdict=verdict,
        failed=failed,
        unknown=unknown,
        stages=stages,
        rules=_rules(),
        values=values,
        decision_at=decision_at,
        reference=reference,
        trigger=trigger,
        geometry=geometry,
    )


def _break_levels(market, balance, side: str):
    edge = dec(balance["high"]) if side == "long" else dec(balance["low"])
    levels = [edge]
    for raw in fixtures(market).get("intraday_levels") or []:
        px = dec(raw)
        if px not in levels:
            levels.append(px)
    extra = fixtures(market).get("break_level")
    if extra is not None:
        if isinstance(extra, (list, tuple)):
            for item in extra:
                px = dec(item)
                if px not in levels:
                    levels.append(px)
        else:
            px = dec(extra)
            if px not in levels:
                levels.append(px)
    return levels


def _scan_continuation_or_trapped(market, branch, balance, bars):
    episodes = []
    sides = ("long", "short") if branch != "trapped_buyers_retest" else ("short", "long")
    profile = None
    try:
        if balance.get("start") is not None and balance.get("known_at") is not None:
            profile = market.profile(balance["start"], balance["known_at"], ".68")
    except Exception:
        profile = fixtures(market).get("profile")
    if profile is None:
        profile = fixtures(market).get("profile")
    context = _stage_profile(profile, balance)
    ref_stage = stage_from(
        "reference",
        balance.get("known_at") if balance else None,
        {
            "low": str(balance["low"]) if balance else None,
            "high": str(balance["high"]) if balance else None,
            "fit": "fixture" if fixtures(market).get("balance") else "od",
            "balance_known": balance is not None,
        },
        require=("balance_known",),
    )
    session_open = bars[0].get("O") if bars else None
    loc = stage_from(
        "location",
        balance.get("known_at") if balance else None,
        {
            "session_open": str(session_open) if session_open is not None else None,
            "balance_low": str(balance["low"]) if balance else None,
            "balance_high": str(balance["high"]) if balance else None,
            "levels_marked": balance is not None,
        },
        require=("levels_marked",),
    )
    for side in sides:
        sg = 1 if side == "long" else -1
        candidates = _break_levels(market, balance, side)
        breaks = []
        for level in candidates:
            trigger = first_true_break(bars, level, side)
            if trigger is not None:
                breaks.append((level, trigger))
        if not breaks:
            continue
        breaks.sort(key=lambda item: int(item[1].get("start") or 0))
        if not fixtures(market).get("intraday_levels") and not fixtures(market).get("break_level"):
            breaks = breaks[:1]
        for boundary, trigger in breaks:
            after = [r for r in bars if int(r["start"]) >= int(trigger["end"])]
            retest = first_touch(after, dec(boundary) - B02_Q, dec(boundary) + B02_Q)
            if branch == "trapped_buyers_retest":
                extreme_side = "high" if side == "short" else "low"
                extreme_px = balance["high"] if side == "short" else balance["low"]
            else:
                extreme_side = "high" if side == "long" else "low"
                extreme_px = boundary
            approach = _approach_into(bars, extreme_px, extreme_side, trigger["start"])
            klass, ratio = classify_arrival(approach, balance.get("width") or (dec(balance["high"]) - dec(balance["low"])))
            if branch == "continuation_retest":
                arrival_ok = None if klass is None else klass == "slow"
            else:
                arrival_ok = None if klass is None else klass == "fast"
            ltf_dir = ltf_break_direction(trigger, balance, boundary)
            htf_dir = htf_control_direction(market, balance, int(trigger.get("known_at") or trigger["end"]))
            if ltf_dir is None or htf_dir is None:
                align_ok = None
            else:
                align_ok = htf_dir == ltf_dir
            confirm_at = int(retest.get("known_at") or retest["end"]) if retest else None
            held = None
            if retest is not None:
                held = retest_held(after, retest, boundary, side)
            trap_delta = None
            if branch == "trapped_buyers_retest":
                deltas = [r.get("delta") for r in approach if r.get("delta") is not None]
                if not deltas:
                    trap_delta = None
                elif side == "short":
                    trap_delta = sum(dec(d) for d in deltas) > 0
                else:
                    trap_delta = sum(dec(d) for d in deltas) < 0
            beyond = sg * (dec(trigger["C"]) - dec(boundary)) > 0
            origin_then_through = True
            trig_stage = stage_from(
                "trigger",
                int(trigger.get("known_at") or trigger["end"]),
                {
                    "break_level": str(boundary),
                    "close": str(trigger["C"]),
                    "beyond_boundary": beyond,
                    "true_break": origin_then_through,
                },
                require=("beyond_boundary", "true_break"),
            )
            retest_aggression = None
            if retest is not None and retest.get("delta") is not None:
                retest_aggression = sg * dec(retest["delta"]) > 0
            conf_operands = {
                "arrival": klass,
                "arrival_ratio": str(ratio) if ratio is not None else None,
                "arrival_ok": arrival_ok,
                "retest": True if retest else False,
                "confirm_at": confirm_at,
                "held_retest": held,
                "htf_control": htf_dir,
                "ltf_break": ltf_dir,
                "alignment_ok": align_ok,
                "retest_aggression": retest_aggression,
            }
            if branch == "trapped_buyers_retest":
                conf_operands["trap_delta_at_extreme"] = trap_delta
                require = ("confirm_at", "held_retest", "arrival_ok", "alignment_ok")
            else:
                require = ("confirm_at", "held_retest", "arrival_ok", "alignment_ok")
            conf = stage_from("confirmation", confirm_at, conf_operands, require=require)
            entry = dec(retest["C"]) if retest and retest.get("C") is not None else None
            stop = dec(balance["low"]) - B02_Q if side == "long" else dec(balance["high"]) + B02_Q
            shape = (context.get("operands") or {}).get("shape")
            if shape == "double":
                selector, target = opposite_shelf_near_edge(profile, side, balance["low"], balance["high"])
            else:
                selector = "VAH" if side == "long" else "VAL"
                target = dec(balance["high"]) if side == "long" else dec(balance["low"])
            risk_defined = entry is not None and stop is not None and (entry - stop) * sg > 0
            risk = stage_from(
                "risk",
                confirm_at,
                {"entry": str(entry) if entry is not None else None, "stop": str(stop), "risk_defined": risk_defined},
                require=("risk_defined",),
            )
            distance = abs(dec(target) - entry) if target is not None and entry is not None else None
            asia = int(trigger["start"]) < market_at(market, "09:30") if getattr(market, "day", None) is not None else False
            obj = stage_from(
                "objective",
                confirm_at,
                {
                    "target": str(target) if target is not None else None,
                    "selector": selector,
                    "target_fixed": target is not None,
                    "distance": str(distance) if distance is not None else None,
                    "asia_range_claim": "150-160",
                    "inside_asia_usual_range": bool(_D("150") <= distance <= _D("160")) if asia and distance is not None else None,
                },
                require=("target_fixed",),
            )
            stages = [context, ref_stage, loc, trig_stage, conf, risk, obj]
            values = {
                "arrival_read": klass,
                "profile_allows_trade": context["verdict"] == "pass",
                "profile_shape": (context.get("operands") or {}).get("shape"),
                "alignment_ok": align_ok,
                "confirm_at": confirm_at,
                "ltf_balance": {"low": str(balance["low"]), "high": str(balance["high"])},
                "same_boundary_retest": True if retest else False,
                "held_retest": held,
                "asia_session": asia,
                "target_selector": selector,
                "true_break": True,
            }
            geometry = {
                "entry": entry,
                "stop": stop,
                "target": target,
                "break_level": boundary,
                "ltf_balance": balance,
                "htf_profile": profile,
                "selector": selector,
            }
            decision = confirm_at if confirm_at is not None else int(trigger.get("known_at") or trigger["end"])
            episodes.append(_finish(FAMILY, branch, side, market, stages, values, decision, balance, trigger, geometry))
    return episodes


def _prior_va_distinct(balance, va_lo, va_hi, side: str) -> bool | None:
    """AMTL p.8 previous area of fair value, not an overlap with the current box."""
    if va_lo is None or va_hi is None or balance is None:
        return None
    if side == "short":
        return dec(va_hi) < dec(balance["low"])
    return dec(va_lo) > dec(balance["high"])


def _scan_failed_auction(market, balance, bars):
    episodes = []
    prior = fixtures(market).get("prior_va") or {}
    try:
        hist = market.prior("day")
        sessions = (hist or {}).get("sessions") or []
        if sessions and not prior:
            win = sessions[-1]["window"]
            p = win.profile(win.start, win.end) if hasattr(win, "profile") else None
            if p:
                prior = {"val": p.get("val"), "vah": p.get("vah")}
    except Exception:
        pass
    if fixtures(market).get("prior_va"):
        prior = fixtures(market)["prior_va"]
    profile = fixtures(market).get("profile")
    if profile is None:
        try:
            profile = market.profile(balance.get("start") or market.start, balance.get("known_at") or market.end, ".68")
        except Exception:
            profile = None
    context = _stage_profile(profile, balance)
    ref_stage = stage_from(
        "reference",
        balance.get("known_at"),
        {"low": str(balance["low"]), "high": str(balance["high"]), "balance_known": True},
        require=("balance_known",),
    )
    va_lo, va_hi = prior.get("val"), prior.get("vah")
    loc = stage_from(
        "location",
        balance.get("known_at"),
        {
            "prior_val": str(va_lo) if va_lo is not None else None,
            "prior_vah": str(va_hi) if va_hi is not None else None,
            "older_auction_required": False,
            "prior_va_known": va_lo is not None and va_hi is not None,
        },
        require=("prior_va_known",),
    )
    if va_lo is None or va_hi is None:
        for side in ("long", "short"):
            stages = [context, ref_stage, loc]
            episodes.append(_finish(FAMILY, "failed_auction_return", side, market, stages, {"older_auction_gate": False}, balance.get("known_at"), balance, {}, {}))
        return episodes
    for side in ("long", "short"):
        distinct = _prior_va_distinct(balance, va_lo, va_hi, side)
        if distinct is False:
            continue
        drive = None
        left_original = False
        for row in bars:
            if row.get("C") is None:
                continue
            close = dec(row["C"])
            if not left_original:
                if side == "short" and close < dec(balance["low"]):
                    left_original = True
                elif side == "long" and close > dec(balance["high"]):
                    left_original = True
                continue
            # AMTL p.8: after leaving current value, a close inside the previous area.
            if dec(va_lo) <= close <= dec(va_hi):
                drive = row
                break
        if drive is None:
            continue
        after = [r for r in bars if int(r["start"]) >= int(drive["start"])]
        inside_va = [
            r
            for r in after
            if r.get("C") is not None and dec(va_lo) <= dec(r["C"]) <= dec(va_hi)
        ]
        attempted_acceptance = len(inside_va) >= 2
        rejection = None
        for row in after:
            if row.get("C") is None:
                continue
            if int(row["start"]) < int(drive["end"]):
                continue
            if side == "short" and dec(row["C"]) > dec(va_hi):
                rejection = row
                break
            if side == "long" and dec(row["C"]) < dec(va_lo):
                rejection = row
                break
        ret = None
        start_from = rejection or drive
        for row in bars:
            if int(row["start"]) < int(start_from["end"]):
                continue
            if row.get("C") is None:
                continue
            if dec(balance["low"]) < dec(row["C"]) < dec(balance["high"]):
                ret = row
                break
        return_held = False
        if ret is not None:
            held_n = 0
            deadline = int(ret.get("end") or 0) + 15 * 60_000_000_000
            for row in bars:
                if int(row["start"]) < int(ret["end"]):
                    continue
                known = int(row.get("known_at") or row["end"])
                if known > deadline:
                    break
                if row.get("C") is None:
                    continue
                if dec(balance["low"]) < dec(row["C"]) < dec(balance["high"]):
                    held_n += 1
                else:
                    held_n = 0
                    break
            return_held = held_n >= 5
        confirm_at = int(ret.get("known_at") or ret["end"]) if ret and return_held else None
        trig = stage_from(
            "trigger",
            int(drive.get("known_at") or drive["end"]),
            {"drive": True, "drive_observed": True, "prior_va_distinct": distinct},
            require=("drive_observed", "prior_va_distinct"),
        )
        conf = stage_from(
            "confirmation",
            confirm_at,
            {
                "rejection": True if rejection else False,
                "return": True if ret else False,
                "return_held": return_held,
                "attempted_acceptance": attempted_acceptance,
                "confirm_at": confirm_at,
                "older_auction_gate": False,
            },
            require=("attempted_acceptance", "rejection", "return", "return_held", "confirm_at"),
        )
        decision = confirm_at if confirm_at is not None else int((rejection or drive).get("known_at") or drive["end"])
        stages = [context, ref_stage, loc, trig, conf]
        episodes.append(
            _finish(
                FAMILY,
                "failed_auction_return",
                side,
                market,
                stages,
                {"older_auction_gate": False, "confirm_at": confirm_at, "ltf_balance": {"low": str(balance["low"]), "high": str(balance["high"])}},
                decision,
                balance,
                drive,
                {"entry": dec(ret["C"]) if ret and ret.get("C") is not None else None},
            )
        )
    return episodes


def _scan_poc(market, balance, bars):
    episodes = []
    profile = fixtures(market).get("profile")
    if profile is None:
        try:
            profile = market.profile(balance.get("start") or market.start, balance.get("known_at") or market.end, ".68")
        except Exception:
            profile = None
    poc = None if profile is None else profile.get("poc")
    context = _stage_profile(profile, balance)
    ref_stage = stage_from(
        "reference",
        balance.get("known_at"),
        {"poc": str(poc) if poc is not None else None, "poc_known": poc is not None},
        require=("poc_known",),
    )
    loc = stage_from(
        "location",
        balance.get("known_at"),
        {"poc": str(poc) if poc is not None else None, "poc_known": poc is not None},
        require=("poc_known",),
    )
    if poc is None:
        episodes.append(_finish(FAMILY, "poc_traversal", "long", market, [context, ref_stage, loc], {"confirm_at": None, "ltf_balance": balance}, balance.get("known_at"), balance, {}, {}))
        return episodes
    fa_eps = _scan_failed_auction(market, balance, bars)
    prior_va_known = False
    ret_times = []
    for ep in fa_eps:
        for item in ep.get("stages") or []:
            ops = item.get("operands") or {}
            if item.get("stage") == "location" and ops.get("prior_va_known"):
                prior_va_known = True
            if item.get("stage") == "confirmation" and ops.get("return") and item.get("at_ns"):
                ret_times.append(int(item["at_ns"]))
    inside = [r for r in bars if r.get("C") is not None and dec(balance["low"]) <= dec(r["C"]) <= dec(balance["high"])]
    if ret_times:
        start_after = min(ret_times)
        inside = [r for r in inside if int(r["start"]) >= start_after]
    elif prior_va_known:
        decision = int(inside[-1].get("known_at") or inside[-1]["end"]) if inside else balance.get("known_at")
        stages = [
            context,
            ref_stage,
            loc,
            stage_from("trigger", decision, {"poc_push": False, "failed_auction_return": False}, require=("failed_auction_return",)),
        ]
        episodes.append(_finish(FAMILY, "poc_traversal", "long", market, stages, {"confirm_at": None, "ltf_balance": balance}, decision, balance, {}, {"poc": poc}))
        return episodes
    fail_holds = 0
    last_fail = None
    push = None
    left_poc = False
    hold = None
    held = None
    for row in inside:
        if not bar_complete(row):
            continue
        low_px = _bar_px(row, "L")
        high_px = _bar_px(row, "H")
        close_px = _bar_px(row, "C")
        open_px = _bar_px(row, "O")
        delta_px = _bar_px(row, "delta")
        tagged = low_px is not None and high_px is not None and low_px <= dec(poc) <= high_px
        # Repeated failure to hold: wick through POC and close back at or below it. AMTL p.9.
        if tagged and high_px is not None and close_px is not None and high_px > dec(poc) and close_px <= dec(poc):
            fail_holds += 1
            last_fail = row
        if (
            push is None
            and delta_px is not None
            and close_px is not None
            and open_px is not None
            and close_px > dec(poc)
            and delta_px > 0
            and close_px > open_px
        ):
            push = row
            after = [r for r in inside if int(r["start"]) >= int(row["end"])]
            left_poc = any(
                r.get("C") is not None and dec(r["C"]) > dec(poc) + B02_Q * 2 for r in after[:8]
            )
            hold = first_touch(after, dec(poc) - B02_Q, dec(poc) + B02_Q)
            if hold is not None:
                held = True
                for r in bars_upto(after, int(hold.get("known_at") or hold["end"])):
                    if r.get("C") is not None and dec(r["C"]) < dec(poc):
                        held = False
                        break
            else:
                held = False
    if push is not None:
        side = "long"
        target = balance["high"]
        tell = "aggressive_through_held_retest"
        confirm_at = int(hold.get("known_at") or hold["end"]) if hold else None
        trig = stage_from(
            "trigger",
            int(push.get("known_at") or push["end"]),
            {"poc_push": True, "left_poc": bool(left_poc)},
            require=("poc_push",),
        )
        conf = stage_from(
            "confirmation",
            confirm_at,
            {
                "tell": tell,
                "held_retest": bool(held),
                "confirm_at": confirm_at,
                "left_poc": bool(left_poc),
                "target": "VAH",
            },
            require=("held_retest", "confirm_at", "left_poc"),
        )
        obj = stage_from(
            "objective",
            confirm_at,
            {"target": str(target), "selector": "VAH", "target_fixed": target is not None},
            require=("target_fixed",),
        )
        stages = [context, ref_stage, loc, trig, conf, obj]
        decision = confirm_at if confirm_at is not None else int(push.get("known_at") or push["end"])
        episodes.append(
            _finish(
                FAMILY,
                "poc_traversal",
                side,
                market,
                stages,
                {"poc_tell": tell, "confirm_at": confirm_at, "ltf_balance": balance, "target_edge": "VAH" if held else None, "held_retest": bool(held)},
                decision,
                balance,
                push,
                {"entry": dec((hold or push).get("C") or push["C"]), "target": dec(target), "poc": poc},
            )
        )
        return episodes
    if fail_holds >= 2:
        side = "short"
        target = balance["low"]
        tell = "repeated_failure_to_hold_poc"
        decision = int((last_fail or inside[-1]).get("known_at") or (last_fail or inside[-1])["end"])
        trig = stage_from(
            "trigger",
            decision,
            {"poc_failures": fail_holds, "repeated_failure": True},
            require=("repeated_failure",),
        )
        conf = stage_from(
            "confirmation",
            decision,
            {"tell": tell, "repeated_failure": True, "confirm_at": decision, "target": "VAL"},
            require=("repeated_failure", "confirm_at"),
        )
        obj = stage_from(
            "objective",
            decision,
            {"target": str(target), "selector": "VAL", "target_fixed": target is not None},
            require=("target_fixed",),
        )
        stages = [context, ref_stage, loc, trig, conf, obj]
        episodes.append(
            _finish(
                FAMILY,
                "poc_traversal",
                side,
                market,
                stages,
                {"poc_tell": tell, "confirm_at": decision, "ltf_balance": balance, "target_edge": "VAL"},
                decision,
                balance,
                last_fail,
                {"target": dec(target), "poc": poc},
            )
        )
    elif inside:
        decision = int(inside[-1].get("known_at") or inside[-1]["end"])
        stages = [
            context,
            ref_stage,
            loc,
            stage_from("trigger", decision, {"poc_push": False, "poc_failures": fail_holds}, require=("poc_push",)),
        ]
        episodes.append(_finish(FAMILY, "poc_traversal", "long", market, stages, {"confirm_at": None, "ltf_balance": balance}, decision, balance, {}, {"poc": poc}))
    return episodes


def scan_saint_branch_b02(market, branch: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    balance, _fit = fit_balance(market)
    balance = enumeration_point(
        "references", balance, family="SAINT-AMT", branch=branch, market=market
    )
    if balance is None:
        return [], [{"reason": "no HTF balance", "kind": "measured_selection"}]
    bars = market_bars(market, getattr(market, "start", 0), getattr(market, "end", 0), 60)
    if branch in {"continuation_retest", "trapped_buyers_retest"}:
        return _scan_continuation_or_trapped(market, branch, balance, bars), []
    if branch == "failed_auction_return":
        return _scan_failed_auction(market, balance, bars), []
    if branch == "poc_traversal":
        return _scan_poc(market, balance, bars), []
    return [], [{"reason": f"unknown branch {branch}"}]


def scan_b02(market, rec, *, overrides=None) -> dict[str, Any]:
    with enumeration_scope(overrides):
        return _scan_b02_impl(market, rec, overrides=overrides)


def _scan_b02_impl(market, rec, *, overrides=None) -> dict[str, Any]:
    stage_overrides, _enum = split_b02_overrides(overrides)
    family, branches = parse_rec(rec, FAMILY, BRANCHES)
    episodes = []
    omissions = []
    for branch in branches:
        eps, oms = scan_saint_branch_b02(market, branch)
        episodes.extend(eps)
        omissions.extend(oms)
    rules = _rules()
    for episode in episodes:
        episode["rules"] = rules
    branch = branches[0] if len(branches) == 1 else None
    document = window_doc(FAMILY, branch, market, episodes, rules, omissions, {"family": family, "branches": list(branches)})
    if not stage_overrides:
        return document
    from trading_research.research.rule_discovery.search import finish_scan_b02

    return finish_scan_b02(document, stage_overrides)


def replay_example(market, example) -> dict[str, Any]:
    if outside_native_tape(example or {}):
        return replay_unavailable(example, "date outside the tape")
    wanted = account_day_for_example(example or {})
    need_load = wanted and (market is None or str(market_day(market)) != wanted)
    if need_load:
        try:
            from trading_research.research.rule_discovery.source_adapters.common import load_source_market

            market = load_source_market(wanted)
        except Exception:
            return replay_unavailable(example, "date outside the tape")
    if market is None:
        return replay_unavailable(example, "date outside the tape")
    extra = {}
    levels = (example or {}).get("levels") or {}
    if levels.get("balance"):
        extra["balance"] = levels["balance"]
    if levels.get("intraday_levels"):
        extra["intraday_levels"] = list(levels["intraday_levels"])
    if levels.get("break_level"):
        extra.setdefault("intraday_levels", [])
        extra["intraday_levels"] = list(extra["intraday_levels"]) + list(
            levels["break_level"] if isinstance(levels["break_level"], (list, tuple)) else [levels["break_level"]]
        )
    view = FixtureMarket(market, extra) if extra else market
    bars = market_bars(view, getattr(view, "start", 0), getattr(view, "end", 0), 60)
    if not bars:
        doc = window_doc(FAMILY, None, view, [], _rules(), extra={"tape_missing": True})
        return replay_match(doc, example)
    doc = scan_b02(view, {"family": FAMILY})
    return replay_match(doc, example)


RULE_FNS = {
    "F04-arrival_read": classify_arrival,
    "F04-profile_allows_trade": classify_profile_shape,
    "F04-double-shelf-target": opposite_shelf_near_edge,
    "F04-alignment_ok": htf_control_direction,
    "F05-failed_auction_return": _scan_failed_auction,
    "F05-poc_traversal": _scan_poc,
    "RR-22-asia-session": scan_b02,
    "RR-22-balance-fit": fit_balance,
    "RR-22-single-retest": _scan_continuation_or_trapped,
    "RR-22-asia-range": scan_b02,
    "RR-22-long-mirror": _scan_continuation_or_trapped,
}

