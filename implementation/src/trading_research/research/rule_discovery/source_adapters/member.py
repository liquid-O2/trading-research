"""P15-14 Member independent-reasons branches."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

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

FAMILY = "MEMBER-TWO-REASONS"
BRANCHES = FAMILY_BRANCHES[FAMILY]
FINDINGS = ("balance_adoption", "vacuous_all")


def family_document() -> dict[str, Any]:
    return {
        "schema_version": "research-family-spec-v1",
        "family": FAMILY,
        "task_id": "P15-14",
        "branches": list(BRANCHES),
        "findings": list(FINDINGS),
        "clock_zone_unverified": True,
    }


def hvn_from_reaction_period_fails(reaction_window: tuple[int, int], hvn_window: tuple[int, int]) -> bool:
    """Using the reaction period to form the purported independent HVN fails."""
    return not (hvn_window[0] >= reaction_window[1])


def two_records_same_parent_are_not_two_reasons(parent_ids: Sequence[str]) -> bool:
    return len(set(parent_ids)) >= 2


def vacuous_all(rows: Sequence[Any], predicate) -> bool | None:
    """Empty collections cannot certify a conjunct. Unknown, not True."""
    if not rows:
        return None
    return all(predicate(row) for row in rows)


def rearm_requires_departure(*, departed: bool, outside_complete_bar: bool) -> bool:
    return bool(departed and outside_complete_bar)


def apply_member_rules(document: Mapping[str, Any], market, branch: str, version: str) -> dict[str, Any]:
    """Reaction-period HVN fails; vacuous all() is unknown; same-parent records are not two reasons."""
    out = dict(document)
    kept = []
    for episode in list(out.get("episodes") or []):
        row = dict(episode)
        values = dict(row.get("values") or {})
        geometry = row.get("geometry") or {}
        reaction = geometry.get("reaction_window") or values.get("reaction_window")
        hvn = geometry.get("hvn_window") or values.get("hvn_window")
        if isinstance(reaction, (list, tuple)) and isinstance(hvn, (list, tuple)) and len(reaction) == 2 and len(hvn) == 2:
            values["hvn_from_reaction_period_fails"] = hvn_from_reaction_period_fails((int(reaction[0]), int(reaction[1])), (int(hvn[0]), int(hvn[1])))
            if values["hvn_from_reaction_period_fails"]:
                values["independent_hvn"] = False
        window_rows = geometry.get("reaction_bars") or values.get("window_rows") or []
        values["vacuous_all"] = vacuous_all(window_rows, lambda item: True)
        parents = list(row.get("parent_ids") or values.get("parent_ids") or geometry.get("parent_ids") or [])
        derivations = row.get("operand_derivations") or {}
        if not parents:
            for item in derivations.values() if isinstance(derivations, dict) else []:
                parents.extend(item.get("parents") or [])
        if parents:
            values["two_independent_reasons"] = two_records_same_parent_are_not_two_reasons([str(p) for p in parents])
        values["member_adapter_rules"] = True
        row["values"] = values
        kept.append(row)
    out["episodes"] = kept
    out["member_adapter_rules"] = True
    out["baseline_version"] = version
    return out


register_family_transform(FAMILY, apply_member_rules)


def _member_prior_reasons(market, side: str) -> dict[str, Any]:
    """Prior-day reaction and disjoint HVN, same recipe as scan_member_repaired."""
    from datetime import date
    from decimal import Decimal as D

    from trading_research.research.method_pack.branch_coverage import setting
    from trading_research.research.method_pack.empirical_market import clock
    from trading_research.research.method_pack.historical_features import Q, pivots

    prior = market.prior("day")
    empty = {"reaction": None, "node": None, "independent": None, "profile": None, "confluence": None}
    if not prior.get("sessions"):
        return empty
    day = prior["sessions"][-1]
    win = day["window"]
    split = clock(date.fromisoformat(day["day"]), setting("auction_selection")["member_prior_split"])
    reactionbars = win.bars(win.start, split, 300)
    qualified = []
    for reaction in pivots(reactionbars):
        after = [row for row in reactionbars if row["start"] >= reaction["at"] and row["known_at"] <= reaction["known_at"]]
        if not after:
            continue
        distance = (
            reaction["price"] - min(row["L"] for row in after)
            if reaction["side"] == "high"
            else max(row["H"] for row in after) - reaction["price"]
        )
        if distance >= Q * setting("reaction")["reaction_ticks"]:
            qualified.append(dict(reaction, reaction_distance=distance))
    wanted = "high" if side == "short" else "low"
    reactions = [row for row in qualified if row["side"] == wanted]
    profile = win.profile(split, win.end)
    levels = {row["price"]: row["total_volume"] for row in profile["rows"]}
    radius = setting("reaction")["hvn_radius_ticks"]
    nodes = [
        price
        for price, volume in levels.items()
        if volume > 0 and all(volume > levels.get(price + Q * i, D(0)) for i in range(-radius, radius + 1) if i)
    ]
    pairs = []
    for reaction in reactions:
        matching = [price for price in nodes if abs(price - reaction["price"]) <= Q * setting("reaction")["confluence_ticks"]]
        if not matching:
            continue
        node = min(matching, key=lambda price: (abs(price - reaction["price"]), price))
        pairs.append((reaction, node))
    if not pairs:
        return {"reaction": None, "node": None, "independent": False, "profile": profile, "confluence": False}
    reaction, node = pairs[-1]
    independent = reaction["known_at"] <= split and profile["formation_start"] >= split
    confluence = abs(node - reaction["price"]) <= Q * setting("reaction")["confluence_ticks"]
    return {"reaction": reaction, "node": node, "independent": independent, "profile": profile, "confluence": confluence}


def confirm_at_contact(market, *, branch, contact, reference, formation=None, changed_axis="none", view=None) -> dict[str, Any]:
    """Defense (long) or rejection (short) after the candidate contact."""
    from trading_research.research.method_pack.historical_features import MINUTE, Q, sign
    from trading_research.research.method_pack.historical_flow import flow_stages
    from trading_research.research.rule_discovery.baseline_repairs import flow_absent_repaired, local_observations_repaired
    from trading_research.research.rule_discovery.source_adapters.confirmation import (
        bounds,
        contact_as_trigger,
        contact_side,
        scanner_ref,
    )

    trigger = contact_as_trigger(market, contact)
    side = contact_side(contact)
    sg = sign(side)
    ref = scanner_ref(reference, formation)
    lo, hi = bounds(ref)
    if lo is None or hi is None:
        decision = trigger.get("known_at") or trigger.get("end")
        return {
            "values": {"branch": branch, "side": side, "source_confirmation": None, "decision_at": decision, "location_touched": True},
            "confirm_at": None,
            "decision_at": decision,
            "cutoff_ns": decision,
            "source_confirmation": None,
        }
    from trading_research.research.method_pack.historical_flow import exact_contact

    exact = exact_contact(market, trigger, lo, hi)
    touch_at = exact["at"] if exact else (contact.get("at_ns") or trigger.get("start"))
    obs = local_observations_repaired(market, touch_at, [lo, hi], side)
    stages = flow_stages(obs)
    defense = stages["defense"]
    selected = defense if side == "long" else stages["reward"]
    decision = selected["known_at"] if selected else obs["end"]
    entry = selected.get("entry_px", selected["last"]) if selected else None
    observed = [row for row in obs["chunks"] if row["end"] <= decision]
    high = max((row["high"] for row in observed), default=hi)
    low = min((row["low"] for row in observed), default=lo)
    stop = high + Q if side == "short" else low - Q
    missing = flow_absent_repaired(market, trigger["start"], min(int(market.end), ((int(decision) + MINUTE - 1) // MINUTE) * MINUTE), observed)
    prior = _member_prior_reasons(market, side)
    reaction = prior.get("reaction")
    profile = prior.get("profile")
    reaction_at = None if reaction is None else reaction.get("known_at")
    hvn_at = None if profile is None else profile.get("known_at")
    prior_known = None if reaction is None or touch_at is None else int(reaction_at) < int(touch_at)
    values = {
        "branch": branch,
        "side": side,
        "thesis_predefined": None if ref.get("known_at") is None or touch_at is None else int(ref["known_at"]) < int(touch_at),
        "objective_fixed": None if entry is None else sg * ((entry + sg * abs(entry - stop)) - entry) > 0,
        "risk_defined": None if entry is None else sg * (entry - stop) > 0,
        "prior_reaction_area_known": prior_known,
        "area_known_at": reaction_at if reaction_at is not None else ref.get("known_at"),
        "independent_minor_hvn_known": prior.get("independent"),
        "hvn_known_at": hvn_at,
        "confluence_band_defined": prior.get("confluence"),
        "actual_band_contact": True,
        "touch_at": touch_at,
        "reaction_at": selected["known_at"] if selected else None,
        "confirm_at": selected["known_at"] if selected else None,
        "decision_at": decision,
        "source_confirmation": True if selected else missing,
    }
    if side == "short":
        values["resistance_rejection"] = selected is not None or missing
        values["stop_above_rejection_high"] = stop > high
    else:
        values["planned_return_to_structure"] = prior_known
        values["buyers_absorb_and_hold"] = defense["held"] if defense else missing
        values["stop_behind_long_invalidation"] = stop < low
    return {"values": values, "confirm_at": values["confirm_at"], "decision_at": decision, "cutoff_ns": decision, "source_confirmation": values["source_confirmation"]}


def scan_variant(market, view, spec: RuleSpec) -> dict[str, Any]:
    return dispatch_scan_variant(market, view, spec)


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-14"
    payload["findings"] = list(FINDINGS)
    payload["clock_zone_unverified"] = clock_zone_unverified(FAMILY)
    payload["vacuous_all"] = "empty window is unknown, not True"
    payload["population_kind"] = "engineering_slice"
    payload["adapter_rules_applied"] = True
    return payload


from decimal import Decimal as _D

from trading_research.research.rule_discovery.source_adapters.b02_saint_track import (
    FIXED_RISK_USD,
    NQ_TICK_VALUE,
    Q as B02_Q,
    cascade_stages,
    combine_verdict,
    contact_reaction,
    dec,
    episode_doc,
    export_rules,
    first_touch,
    fixtures,
    outside_native_tape,
    reaction_held,
    replay_unavailable,
    market_at,
    market_bars,
    parse_rec,
    replay_match,
    stage,
    window_doc,
)

REACTION_TICKS = 4
CONFLUENCE_TICKS = 2
HVN_RADIUS = 2
# K10 pp.6-7: the minor HVN belongs to the "higher-timeframe profile". On the
# ES tape of his K10 session (2026-08-03) the prior single day traded below
# both of his pairs; the composite of the prior ten sessions carries minor
# nodes at 7,558-7,561 and 7,543-7,547, where his pairs sit.
HTF_SESSIONS = 10
TARGET_R = _D("1.5")

RULES = {
    "F15-no-1245-split": {"kind": "literal", "source": "K10 pp.5-8"},
    "F15-two-reasons": {
        "kind": "OD",
        "source": "OD:reaction_ticks=4, confluence_ticks=2, look-left any prior history (K10 pp.5-8)",
    },
    "F15-kg1-alternative": {"kind": "OD", "source": "OD:KG1 aligned within confluence_ticks (K10 p.6)"},
    "F15-independence-admission": {"kind": "literal", "source": "K10 pp.5-8"},
    "F15-target-1.5R": {"kind": "literal", "source": "K10 pp.7-8"},
    "F15-ticket-rr-conflict": {"kind": "literal", "source": "K10 pp.7-8 tickets R:R 1.00 and 9.60"},
    "F15-stop-beyond-rejection": {"kind": "literal", "source": "K10 pp.7-8"},
    "F15-fixed-500-risk": {"kind": "literal", "source": "K10 p.13"},
    "F15-k10-p13-drawn-directions": {
        "kind": "literal",
        "source": "K10 p.13",
        "notes": "Drawings are two SELL and one BUY. Caption says three shorts. B0.2 uses the drawn directions as the negative control. Caption is conflicting evidence.",
    },
    "RR-23-instrument-transfer": {"kind": "OD", "source": "OD:instrument transfer NQ from ES-202609 (K10 pp.7-8,12-13)"},
}

K10_P13_DRAWN_DIRECTIONS = ("short", "short", "long")
K10_P13_CAPTION = "three shorts"


def _rules():
    return export_rules(RULES, RULE_FNS)


def _look_left_reactions(market, side: str):
    fx = fixtures(market)
    if fx.get("reactions") is not None:
        wanted = "high" if side == "short" else "low"
        return [dict(r) for r in fx["reactions"] if r.get("side") == wanted]
    try:
        from trading_research.research.method_pack.historical_features import pivots

        prior = market.prior("day")
        rows = []
        if prior.get("sessions"):
            win = prior["sessions"][-1]["window"]
            rows.extend(win.bars(win.start, win.end, 300))
        rows.extend(market_bars(market, getattr(market, "start", 0), getattr(market, "end", 0), 300))
        qualified = []
        for reaction in pivots(rows):
            after = [r for r in rows if r["start"] >= reaction["at"] and r["known_at"] <= reaction["known_at"]]
            if not after:
                continue
            distance = (
                reaction["price"] - min(r["L"] for r in after)
                if reaction["side"] == "high"
                else max(r["H"] for r in after) - reaction["price"]
            )
            if distance >= B02_Q * REACTION_TICKS:
                qualified.append(dict(reaction, reaction_distance=distance))
        wanted = "high" if side == "short" else "low"
        return [r for r in qualified if r["side"] == wanted]
    except Exception:
        return []


def _look_left_hvns(market):
    fx = fixtures(market)
    if fx.get("hvns") is not None:
        return [dict(r) for r in fx["hvns"]]
    try:
        from trading_research.research.method_pack.profile_nodes import composite
        from trading_research.research.rule_discovery.source_adapters.session_levels import prior_sessions

        spans = prior_sessions(market, HTF_SESSIONS)
        payloads = []
        for span in spans:
            win = span.get("window")
            if win is not None:
                payloads.append(win.profile(win.start, win.end))
        profile = composite(payloads)
        if profile is None:
            return []
        levels = {dec(r["price"]): dec(r["total_volume"]) for r in profile["rows"]}
        known_at = max(int(s.get("known_at") or 0) for s in spans) or int(getattr(market, "start", 0))
        parent = f"composite:{len(payloads)}"
        nodes = []
        for price, volume in levels.items():
            if volume <= 0:
                continue
            if all(volume > levels.get(price + B02_Q * i, _D(0)) for i in range(-HVN_RADIUS, HVN_RADIUS + 1) if i):
                nodes.append({"price": price, "id": f"hvn:{price}", "known_at": known_at, "parent": parent})
        return nodes
    except Exception:
        return []


def _kg1_levels(market):
    fx = fixtures(market)
    if fx.get("kg1") is not None:
        return list(fx["kg1"])
    try:
        from trading_research.research.method_pack.strategy_options import key_gamma_reference

        return list(key_gamma_reference(market) or [])
    except Exception:
        return []


def _pair_reasons(reactions, hvns, kg1, side: str):
    pairs = []
    for reaction in reactions:
        px = dec(reaction["price"])
        matching = [n for n in hvns if abs(dec(n["price"]) - px) <= B02_Q * CONFLUENCE_TICKS]
        if matching:
            node = min(matching, key=lambda n: (abs(dec(n["price"]) - px), dec(n["price"])))
            pairs.append((reaction, node, "hvn"))
            continue
        kg_hit = []
        for node in kg1:
            level = node.get("price")
            if level is None and node.get("low") is not None and node.get("high") is not None:
                level = (dec(node["low"]) + dec(node["high"])) / 2
            elif level is None:
                level = node.get("low")
            if level is not None and not isinstance(level, bool) and abs(dec(level) - px) <= B02_Q * CONFLUENCE_TICKS:
                kg_hit.append(node)
        if kg_hit:
            pairs.append((reaction, kg_hit[0], "kg1"))
    return pairs


def _independent(reaction, second, kind: str) -> bool:
    if second is None:
        return False
    r_id = str(reaction.get("id") or reaction.get("parent") or "")
    s_id = str(second.get("id") or second.get("parent") or "")
    if r_id and s_id and r_id == s_id:
        return False
    r_win = reaction.get("window")
    s_win = second.get("window")
    if r_win and s_win and tuple(r_win) == tuple(s_win):
        return False
    return True


def scan_member_branch_b02(market, branch: str) -> list[dict[str, Any]]:
    side = "short" if branch == "resistance_short" else "long"
    sg = 1 if side == "long" else -1
    reactions = _look_left_reactions(market, side)
    hvns = _look_left_hvns(market)
    kg1 = _kg1_levels(market)
    pairs = _pair_reasons(reactions, hvns, kg1, side)
    fx = fixtures(market)
    if fx.get("force_pair"):
        pairs = [tuple(fx["force_pair"])]
    if not pairs:
        ctx = stage("context", "fail", None, {"split_1245": False, "reasons": 0})
        stages = cascade_stages([ctx])
        verdict, failed, unknown = combine_verdict(stages)
        return [
            episode_doc(
                family=FAMILY,
                branch=branch,
                side=side,
                market=market,
                verdict=verdict,
                failed=failed,
                unknown=unknown,
                stages=stages,
                rules=_rules(),
                values={"split_1245": False, "k10_p13_drawn_directions": list(K10_P13_DRAWN_DIRECTIONS)},
                decision_at=getattr(market, "end", None),
            )
        ]
    reaction, second, kind = pairs[-1]
    independent = _independent(reaction, second, kind)
    if fx.get("independent") is not None:
        independent = bool(fx["independent"])
    px = dec(reaction["price"])
    second_px = dec(second.get("price") or second.get("low") or px)
    lo = min(px, second_px) - B02_Q
    hi = max(px, second_px) + B02_Q
    start = market_at(market, "09:30") if getattr(market, "day", None) is not None else getattr(market, "start", 0)
    try:
        start = market_at(market, "09:30")
    except Exception:
        start = getattr(market, "start", 0)
    bars = market_bars(market, start, getattr(market, "end", start), 60)
    contact = first_touch(bars, lo, hi)
    if fx.get("contact"):
        contact = dict(fx["contact"])
    ctx = stage("context", "pass", reaction.get("known_at"), {"split_1245": False, "look_left": True})
    ref = stage("reference", "pass" if independent else "fail", reaction.get("known_at"), {"reaction": str(px), "second": str(second_px), "kind": kind, "independent": independent})
    loc = stage("location", "pass", reaction.get("known_at"), {"low": str(lo), "high": str(hi), "band_defined": True})
    if contact is None:
        trig = stage("trigger", "fail", None, {"touch": False})
        stages = cascade_stages([ctx, ref, loc, trig])
        verdict, failed, unknown = combine_verdict(stages)
        return [
            episode_doc(
                family=FAMILY,
                branch=branch,
                side=side,
                market=market,
                verdict=verdict,
                failed=failed,
                unknown=unknown,
                stages=stages,
                rules=_rules(),
                values={"independent": independent, "split_1245": False},
                decision_at=getattr(market, "end", None),
                reference={"low": lo, "high": hi},
            )
        ]
    reaction_bar = contact_reaction(bars, contact, px, side)
    trig = stage(
        "trigger",
        "pass" if reaction_bar else "fail",
        int((reaction_bar or contact).get("known_at") or contact["end"]),
        {"touch": True, "reaction": True if reaction_bar else False},
    )
    if reaction_bar is None:
        trig = stage("trigger", "fail", int(contact.get("known_at") or contact["end"]), {"touch": True, "reaction": False})
        stages = cascade_stages([ctx, ref, loc, trig])
        verdict, failed, unknown = combine_verdict(stages)
        return [
            episode_doc(
                family=FAMILY,
                branch=branch,
                side=side,
                market=market,
                verdict=verdict,
                failed=failed,
                unknown=unknown,
                stages=stages,
                rules=_rules(),
                values={"independent": independent, "split_1245": False, "reaction": False},
                decision_at=int(contact.get("known_at") or contact["end"]),
                reference={"low": lo, "high": hi},
                trigger=contact,
            )
        ]
    after = [r for r in bars if int(r["start"]) >= int(contact["start"])]
    observed = after[:5] or [contact]
    high = max(dec(r["H"]) for r in observed if r.get("H") is not None)
    low = min(dec(r["L"]) for r in observed if r.get("L") is not None)
    entry = dec(contact.get("C") or px)
    stop = high + B02_Q if side == "short" else low - B02_Q
    if fx.get("rejection_high") is not None and side == "short":
        high = dec(fx["rejection_high"])
        stop = high + B02_Q
    if fx.get("rejection_low") is not None and side == "long":
        low = dec(fx["rejection_low"])
        stop = low - B02_Q
    r_dist = abs(entry - stop)
    target = entry + sg * r_dist * TARGET_R
    stop_ticks = (r_dist / B02_Q) if r_dist > 0 else _D("1")
    qty = (FIXED_RISK_USD / (stop_ticks * NQ_TICK_VALUE)) if stop_ticks > 0 else None
    stop_ok = stop > high if side == "short" else stop < low
    held = reaction_held(bars, reaction_bar, px, side)
    if fx.get("held") is not None:
        held = bool(fx["held"])
    conf = stage(
        "confirmation",
        "pass" if held else "fail",
        int((reaction_bar or contact).get("known_at") or contact["end"]),
        {
            "held": held,
            "kind": kind,
            "level_reason": kind,
            "flow_reason": "prior_reaction",
        },
    )
    risk = stage(
        "risk",
        "pass" if stop_ok else "fail",
        int(contact.get("known_at") or contact["end"]),
        {
            "stop": str(stop),
            "rejection_high": str(high) if side == "short" else None,
            "rejection_low": str(low) if side == "long" else None,
            "risk_usd": str(FIXED_RISK_USD),
            "quantity": str(qty) if qty is not None else None,
            "tick_value": str(NQ_TICK_VALUE),
            "instrument_transfer": True,
        },
    )
    obj = stage(
        "objective",
        "pass",
        int(contact.get("known_at") or contact["end"]),
        {
            "target_r": "1.5",
            "target": str(target),
            "conflicting_evidence": [{"ticket": "first", "rr": 1.00}, {"ticket": "second", "rr": 9.60}],
        },
    )
    stages = cascade_stages([ctx, ref, loc, trig, conf, risk, obj])
    verdict, failed, unknown = combine_verdict(stages)
    decision = int(contact.get("known_at") or contact["end"])
    values = {
        "split_1245": False,
        "independent": independent,
        "target_r": "1.5",
        "conflicting_evidence": [{"ticket": "first", "rr": 1.00}, {"ticket": "second", "rr": 9.60}],
        "stop_above_rejection_high": bool(side == "short" and stop > high),
        "quantity": str(qty) if qty is not None else None,
        "risk_usd": "500",
        "instrument_transfer": True,
        "k10_p13_drawn_directions": list(K10_P13_DRAWN_DIRECTIONS),
        "k10_p13_caption": K10_P13_CAPTION,
    }
    return [
        episode_doc(
            family=FAMILY,
            branch=branch,
            side=side,
            market=market,
            verdict=verdict,
            failed=failed,
            unknown=unknown,
            stages=stages,
            rules=_rules(),
            values=values,
            decision_at=decision,
            reference={"low": lo, "high": hi, "reaction": px},
            trigger=contact,
            geometry={"entry": entry, "stop": stop, "target": target},
        )
    ]


def scan_b02(market, rec, *, overrides=None) -> dict[str, Any]:
    with enumeration_scope(overrides):
        return _scan_b02_impl(market, rec, overrides=overrides)


def _scan_b02_impl(market, rec, *, overrides=None) -> dict[str, Any]:
    stage_overrides, _enum = split_b02_overrides(overrides)
    family, branches = parse_rec(rec, FAMILY, BRANCHES)
    episodes = []
    for branch in branches:
        episodes.extend(scan_member_branch_b02(market, branch))
    rules = _rules()
    for episode in episodes:
        episode["rules"] = rules
    branch = branches[0] if len(branches) == 1 else None
    document = window_doc(FAMILY, branch, market, episodes, rules, extra={"family": family, "branches": list(branches)})
    if not stage_overrides:
        return document
    from trading_research.research.rule_discovery.search import finish_scan_b02

    return finish_scan_b02(document, stage_overrides)


def replay_example(market, example) -> dict[str, Any]:
    instrument = str((example or {}).get("instrument") or "")
    example_id = str((example or {}).get("id") or "")
    if example_id == "MB-2026-07-K10" or instrument.upper().startswith("ES"):
        expected = (example or {}).get("expected_detection") or {}
        return {
            "detected": None,
            "branch": expected.get("branch"),
            "our_side": None,
            "our_level": None,
            "our_entry_ns": None,
            "author_level": None,
            "author_side": expected.get("side"),
            "divergence": "ES tape required",
            "reached_location": False,
            "failing_operand": None,
        }
    if outside_native_tape(example or {}) or (example or {}).get("inside_tape") is False:
        return replay_unavailable(example, "date outside the tape")
    if market is None:
        return replay_unavailable(example, "date outside the tape")
    doc = scan_b02(market, {"family": FAMILY})
    return replay_match(doc, example)


RULE_FNS = {
    "F15-no-1245-split": scan_member_branch_b02,
    "F15-two-reasons": _pair_reasons,
    "F15-kg1-alternative": _kg1_levels,
    "F15-independence-admission": _independent,
    "F15-target-1.5R": scan_member_branch_b02,
    "F15-ticket-rr-conflict": scan_member_branch_b02,
    "F15-stop-beyond-rejection": scan_member_branch_b02,
    "F15-fixed-500-risk": scan_member_branch_b02,
    "F15-k10-p13-drawn-directions": scan_member_branch_b02,
    "RR-23-instrument-transfer": replay_example,
}

