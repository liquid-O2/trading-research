"""M01 mapped object recipes and printed F1 cases."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from trading_research.research.method_pack.clocks import et_ns, range_hl, aggregate_ohlcv
from trading_research.research.method_pack.logic import dec
from trading_research.research.method_pack.adapters import signed_size
from trading_research.research.method_pack.protocol import RecipeResult, add_fixture, register

DAY = date(2026, 1, 15)
Q = Decimal("0.25")


def _r(rid: str, state: str, value: dict, **kwargs) -> RecipeResult:
    return RecipeResult(rid, state, value, **kwargs)


def _d(*clock):
    return et_ns(DAY, *clock)


@register("O001", ("bars",))
def o001(inp: dict) -> RecipeResult:
    bars = inp["bars"]
    trades = inp.get("trades")
    need = inp.get("required_minutes", 5)
    price_ok = len(bars) >= need and all(b.get("complete") for b in bars[:need])
    if len(bars) < need:
        price_ok = False
    side_ok = None
    missing = []
    if trades is None:
        missing.append("aggressor")
        side_ok = None
    else:
        sides = [t.get("side") for t in trades]
        if any(s not in ("A", "B") for s in sides) or any(s is None for s in sides):
            missing.append("aggressor")
            side_ok = None
        else:
            side_ok = True
    coverage = True if price_ok and side_ok is True else (False if not price_ok else None)
    return _r("O001", "computed" if coverage is True else "hole", {
        "price_coverage": price_ok,
        "side_coverage": side_ok,
        "coverage_ok": coverage,
        "missing_fields": missing,
    }, coverage_ok=coverage, base_ok=True if coverage is not False else False)


@register("O002", ("lo", "hi"))
def o002(inp: dict) -> RecipeResult:
    lo, hi = dec(inp["lo"]), dec(inp["hi"])
    q = dec(inp.get("q", Q))
    bar = inp.get("bar") or {}
    L, H, C = dec(bar.get("L")), dec(bar.get("H")), dec(bar.get("C"))
    overlap = None
    if L is not None and H is not None:
        overlap = H >= lo and L <= hi
    upper_exc = (H - hi) if H is not None and H > hi else Decimal(0)
    ticks = (upper_exc / q) if q else None
    close_inside_strict = None if C is None else (lo < C < hi)
    close_below_hi = None if C is None else (C < hi)
    hold = None
    if inp.get("source_hold_duration") is None:
        hold = None
    return _r("O002", "computed", {
        "price_overlap": overlap,
        "upper_excursion_points": upper_exc,
        "upper_excursion_ticks": ticks,
        "close_inside_strict": close_inside_strict,
        "close_below_hi": close_below_hi,
        "source_hold": hold,
        "source_reject": None if inp.get("source_reject_def") is None else inp.get("source_reject"),
    }, known_at=inp.get("known_at"))


@register("O003", ("start_ns", "end_ns"))
def o003(inp: dict) -> RecipeResult:
    start, end = inp["start_ns"], inp["end_ns"]
    at = inp.get("event_ns", inp.get("use_at"))
    available = None if at is None else at >= end
    return _r("O003", "computed", {
        "start_ns": start,
        "end_ns": end,
        "window_known_at": end,
        "clock_verified": inp.get("clock_verified", True),
        "available": available,
        "clock_check": available,
    }, known_at=end, base_ok=True if available is not False else False)


@register("O004", ("members",))
def o004(inp: dict) -> RecipeResult:
    kind = inp.get("kind", "time")
    if kind == "native_range":
        return _r("O004", "hole", {
            "native_source_compatible": None,
            "O": None, "H": None, "L": None, "C": None, "V": None,
        }, hole_ids=["HOLE:O004:native_bar_definition"], coverage_ok=None, base_ok=None)
    members = inp["members"]
    agg = aggregate_ohlcv(members)
    known = inp.get("end_ns") or inp.get("known_at")
    return _r("O004", "computed", {
        "O": agg["O"], "H": agg["H"], "L": agg["L"], "C": agg["C"], "V": agg["V"],
        "complete": True,
        "native_source_compatible": True,
        "known_at": known,
    }, known_at=known)


@register("O005", ("members", "start_ns", "end_ns"))
def o005(inp: dict) -> RecipeResult:
    use_at = inp.get("use_at", inp["end_ns"])
    got = range_hl(inp["members"], inp["start_ns"], inp["end_ns"], use_at)
    if not got.get("available"):
        return _r("O005", "invalid" if got.get("invalid") else "hole", {
            "range_frozen": False,
            "H": got.get("H"), "L": got.get("L"), "W": got.get("W"),
        }, base_ok=False, known_at=got.get("known_at"), reason="causal" if use_at < inp["end_ns"] else got.get("invalid"))
    return _r("O005", "computed", {
        "L": got["L"], "H": got["H"], "W": got["W"],
        "range_frozen": True,
        "range_known_at": got["known_at"],
    }, known_at=got["known_at"])


@register("O006", ("start_ns", "end_ns", "L", "H"))
def o006(inp: dict) -> RecipeResult:
    verified = inp.get("source_clock_verified")
    if verified is False or inp.get("clock_id") == "00:00-03:00":
        return _r("O006", "hole", {
            "source_clock_verified": False,
            "W": dec(inp["H"]) - dec(inp["L"]),
        }, coverage_ok=None, base_ok=False if verified is False else None)
    w = dec(inp["H"]) - dec(inp["L"])
    return _r("O006", "computed", {
        "L": dec(inp["L"]), "H": dec(inp["H"]), "W": w,
        "source_clock_verified": True,
        "known_at": inp["end_ns"],
    }, known_at=inp["end_ns"])


@register("O007", ("L", "H"))
def o007(inp: dict) -> RecipeResult:
    L, H = dec(inp["L"]), dec(inp["H"])
    W = H - L
    if W <= 0:
        return _r("O007", "hole", {"W": W}, coverage_ok=None, hole_ids=["HOLE:O007:W"])
    q25 = L + Decimal("0.25") * W
    eq = L + Decimal("0.50") * W
    q75 = L + Decimal("0.75") * W
    px = dec(inp.get("price"))
    at_eq = None if px is None else px == eq
    return _r("O007", "computed", {
        "q25": q25, "eq": eq, "q75": q75, "W": W,
        "at_eq": at_eq,
        "strict_above_eq": None if px is None else px > eq,
        "strict_below_eq": None if px is None else px < eq,
    }, known_at=inp.get("known_at"), parent_ids=[inp.get("parent_id")] if inp.get("parent_id") else [])


@register("O008", ("range_open_ref",))
def o008(inp: dict) -> RecipeResult:
    open_ref = dec(inp["range_open_ref"])
    low = dec(inp.get("range_low"))
    first_print = dec(inp.get("first_print"))
    path = False
    events = inp.get("path_events") or []
    if events and low is not None:
        saw_low = False
        saw_open = False
        for ev in events:
            px = dec(ev["price"])
            if not saw_low and px == low:
                saw_low = True
            elif saw_low and px == open_ref:
                saw_open = True
        path = saw_low and saw_open
    numeric_gt = None if low is None else low > open_ref
    used = open_ref
    if inp.get("replace_with_first_print"):
        used = first_print
    return _r("O008", "supplied", {
        "range_open_ref": used,
        "reference_verified": True,
        "directed_path": path,
        "numeric_low_gt_open": numeric_gt,
        "replaced_by_first_print": bool(inp.get("replace_with_first_print")),
    }, known_at=inp.get("known_at"))


@register("O009", ("W",))
def o009(inp: dict) -> RecipeResult:
    W = dec(inp["W"])
    P = dec(inp.get("P"))
    prior = dec(inp.get("prior_W"))
    q = dec(inp.get("q", Q))
    pct = (Decimal(100) * W / P) if P not in (None, 0) else None
    ratio = (W / prior) if prior not in (None, 0) else None
    ticks = (W / q) if q else None
    klass = inp.get("source_width_class")
    return _r("O009", "computed", {
        "width_points": W,
        "width_ticks": ticks,
        "price_percent": pct,
        "width_ratio": ratio,
        "source_width_class": klass,
        "extended_context": klass,
    }, known_at=inp.get("known_at"))


@register("O010", ("H", "L"))
def o010(inp: dict) -> RecipeResult:
    H, L = dec(inp["H"]), dec(inp["L"])
    events = inp.get("events") or []
    window_start = inp["window_start"]
    window_end = inp.get("as_of", inp.get("window_end"))
    window_complete = inp.get("window_complete", window_end == inp.get("window_end"))
    high_at = None
    low_at = None
    for ev in events:
        t, px = ev["t"], dec(ev["price"])
        if t < window_start or t >= window_end:
            continue
        if px > H and high_at is None:
            high_at = t
        if px < L and low_at is None:
            low_at = t
    bar = inp.get("bar")
    if bar and high_at is None and low_at is None:
        if dec(bar["H"]) > H:
            high_at = bar.get("t", window_start)
        if dec(bar["L"]) < L:
            low_at = bar.get("t", window_start)
        first_side = None
        path = "both" if (dec(bar["H"]) > H and dec(bar["L"]) < L) else None
        return _r("O010", "computed", {
            "path": path or "unknown",
            "first_side": first_side,
            "high_break_at": high_at,
            "low_break_at": low_at,
        }, known_at=window_end)
    if high_at and low_at:
        path = "both"
        first = "high" if high_at < low_at else ("low" if low_at < high_at else None)
    elif high_at:
        path = "high_only" if window_complete else "high_only_so_far"
        first = "high"
    elif low_at:
        path = "low_only" if window_complete else "low_only_so_far"
        first = "low"
    else:
        path = "neither" if window_complete else "unknown"
        first = None
    return _r("O010", "computed", {
        "path": path,
        "first_side": first,
        "high_break_at": high_at,
        "low_break_at": low_at,
    }, known_at=window_end)


@register("O011", ("H", "L", "end_ns"))
def o011(inp: dict) -> RecipeResult:
    use_at = inp.get("use_at", inp["end_ns"])
    if use_at < inp["end_ns"]:
        return _r("O011", "invalid", {"final": False, "on_width": None}, base_ok=False, reason="causal")
    h, l = dec(inp["H"]), dec(inp["L"])
    return _r("O011", "computed", {
        "on_high": h, "on_low": l, "on_width": h - l,
        "window_id": inp.get("window_id", "sires_overnight"),
        "final": True,
    }, known_at=inp["end_ns"])


@register("O012", ("reference_px", "reference_known_at"))
def o012(inp: dict) -> RecipeResult:
    sweep_at = inp.get("sweep_at")
    decision = inp.get("decision_at")
    scope = inp.get("consumption_scope", "overnight")
    if sweep_at is None:
        return _r("O012", "hole", {"purged_at": None}, hole_ids=["HOLE:O012:sweep"], coverage_ok=None)
    if sweep_at < inp["reference_known_at"]:
        return _r("O012", "invalid", {}, base_ok=False, reason="causal")
    rth_active = True
    overnight_purged = True
    if scope == "rth_only":
        overnight_purged = False
        active = True
        purged_at = sweep_at
    else:
        active = False
        purged_at = sweep_at
    before = None if decision is None else (purged_at < decision if scope != "rth_only" else False)
    if scope == "rth_only":
        before = False
        active = True
    else:
        before = purged_at < decision if decision is not None else None
        active = not before if before is not None else None
    return _r("O012", "computed", {
        "purged_at": purged_at,
        "purge_before_decision": before,
        "active_before_use": active,
        "consumption_scope": scope,
        "overnight_purge_true": overnight_purged if scope != "rth_only" else True,
    }, known_at=purged_at)


@register("O013", ("open_px",))
def o013(inp: dict) -> RecipeResult:
    open_px = dec(inp["open_px"])
    vah, val = dec(inp.get("prior_vah")), dec(inp.get("prior_val"))
    rh, rl = dec(inp.get("prior_range_h")), dec(inp.get("prior_range_l"))
    above_value = None if vah is None else open_px > vah
    inside_value = None if (vah is None or val is None) else val <= open_px <= vah
    inside_range = None if (rh is None or rl is None) else rl <= open_px <= rh
    rvol = inp.get("rvol")
    rvol_ready = inp.get("rvol_known_at")
    use_at = inp.get("use_at")
    rvol_ok = None
    if rvol_ready is not None and use_at is not None:
        rvol_ok = rvol_ready <= use_at
    return _r("O013", "computed", {
        "above_value": above_value,
        "inside_value": inside_value,
        "inside_range": inside_range,
        "rvol_available": rvol_ok,
        "source_context": inp.get("source_context"),
    }, known_at=inp.get("known_at"))


@register("O014", ("L", "H"))
def o014(inp: dict) -> RecipeResult:
    L, H = dec(inp["L"]), dec(inp["H"])
    W = H - L
    ladder = {
        "0.1": H + Decimal("0.1") * W,
        "0.2": H + Decimal("0.2") * W,
        "0.3": H + Decimal("0.3") * W,
        "0.5": H + Decimal("0.5") * W,
    }
    px = dec(inp.get("price"))
    depth = None if px is None else (px - H) / W
    return _r("O014", "computed", {
        "upper_0_1": ladder["0.1"],
        "upper_0_2": ladder["0.2"],
        "upper_0_3": ladder["0.3"],
        "upper_0_5": ladder["0.5"],
        "depth_w": depth,
        "source_location_selected": inp.get("source_location_selected"),
    }, known_at=inp.get("known_at"))


@register("O015", ("L", "H"))
def o015(inp: dict) -> RecipeResult:
    L, H = dec(inp["L"]), dec(inp["H"])
    W = H - L
    if inp.get("use_outer_w") and inp.get("outer_W") is not None:
        W = dec(inp["outer_W"])
    upper = [H + Decimal("1.33") * W, H + Decimal("1.66") * W]
    lower = [L - Decimal("1.66") * W, L - Decimal("1.33") * W]
    return _r("O015", "computed", {
        "upper_band": upper,
        "lower_band": lower,
        "W": W,
        "parent_id": inp.get("parent_id"),
    }, known_at=inp.get("known_at"), parent_ids=[inp["parent_id"]] if inp.get("parent_id") else [])


@register("O016", ("outer_L", "outer_H"))
def o016(inp: dict) -> RecipeResult:
    oL, oH = dec(inp["outer_L"]), dec(inp["outer_H"])
    inner_L, inner_H = dec(inp.get("inner_L")), dec(inp.get("inner_H"))
    outer_w = oH - oL
    inner_w = None if inner_L is None or inner_H is None else inner_H - inner_L
    outer_eq = oL + outer_w / 2
    inner_eq = None if inner_w is None else inner_L + inner_w / 2
    merged = False
    return _r("O016", "computed" if inner_w is not None else "hole", {
        "outer_width": outer_w,
        "inner_width": inner_w,
        "outer_eq": outer_eq,
        "inner_eq": inner_eq,
        "ids_merged": merged,
        "automatic_construction": None,
    }, hole_ids=[] if inner_w is not None else ["HOLE:O016:inner_span"], coverage_ok=True if inner_w is not None else None)


# A supplied Session Stat record needs at least the labelled average band.  The
# median and min-average values remain optional because the source sometimes
# omits one of those displays; their absence is reported by the recipe rather
# than silently reconstructed from the other band.
@register("O017", ("average",))
def o017(inp: dict) -> RecipeResult:
    avg = inp.get("average")
    med = inp.get("median")
    min_avg = inp.get("min_average")
    avg_mid = None if not avg else (dec(avg[0]) + dec(avg[1])) / 2
    value = {
        "average_lo": None if not avg else dec(avg[0]),
        "average_hi": None if not avg else dec(avg[1]),
        "average_mid": avg_mid,
        "median_lo": None if not med else dec(med[0]),
        "median_hi": None if not med else dec(med[1]),
        "min_average": None if min_avg is None else min_avg,
        "automatic_bands": None,
        "min_of_widths_is_not_min_average": True,
    }
    holes = [] if min_avg is not None else ["HOLE:O017:min_average"]
    return _r("O017", "supplied" if avg else "hole", value, hole_ids=holes, coverage_ok=True if avg else None)


# A supplied reference is still a dated observation: the snapshot cutoff is
# the common mandatory envelope while EV mid versus EV bands remain optional
# source spellings.
@register("O018", ("known_at",))
def o018(inp: dict) -> RecipeResult:
    ev_mid = dec(inp.get("ev_mid"))
    eq = dec(inp.get("eq"))
    px = dec(inp.get("price"))
    envelope = dec(inp.get("generic_envelope"))
    known = ev_mid is not None
    return _r("O018", "supplied" if known else "hole", {
        "ev_mid": ev_mid,
        "eq": eq,
        "touches_eq": None if px is None or eq is None else px == eq,
        "touches_ev": None if px is None or ev_mid is None else px == ev_mid,
        "ev_reference_known": True if known else None,
        "automatic_ev": None,
        "envelope_fill": envelope,
    }, hole_ids=[] if known else ["HOLE:O018:ev_snapshot"], coverage_ok=True if known else None)


@register("O019", ("lo", "hi", "snapshot_known_at"))
def o019(inp: dict) -> RecipeResult:
    lo, hi = dec(inp.get("lo")), dec(inp.get("hi"))
    known_at = inp.get("snapshot_known_at")
    touch_at = inp.get("touch_at")
    if lo is None or hi is None or known_at is None:
        return _r("O019", "hole", {
            "source_zone_known": None,
            "entry_at_anchor": False,
            "automatic_pzone": None,
        }, hole_ids=["HOLE:O019:source_zone"], coverage_ok=None)
    return _r("O019", "supplied", {
        "lo": lo, "hi": hi,
        "anchor_at": inp.get("anchor_at"),
        "source_zone_known": True,
        "known_before_touch": known_at <= touch_at if touch_at is not None else None,
        "entry_at_anchor": False,
        "directed_path_recorded": bool(inp.get("source_id") and inp.get("target_id")),
        "automatic_pzone": None,
    }, known_at=known_at)


@register("O020", ("prior_rth_h", "prior_rth_l"))
def o020(inp: dict) -> RecipeResult:
    h, l = dec(inp["prior_rth_h"]), dec(inp["prior_rth_l"])
    eth_px = dec(inp.get("eth_price"))
    eth_consumes = False
    if eth_px is not None and eth_px > h:
        eth_consumes = inp.get("scope") == "eth_counts"
    return _r("O020", "computed", {
        "rth_high": h, "rth_low": l,
        "eth_consumes_rth_objective": eth_consumes,
        "direction_from_final_close": None,
    }, known_at=inp.get("known_at"))


@register("O021", ("event_ns",))
def o021(inp: dict) -> RecipeResult:
    t = inp["event_ns"]
    start = inp.get("window_start", _d(9, 40))
    end = inp.get("window_end", _d(9, 50))
    required = inp.get("window_required", True)
    if not required:
        return _r("O021", "computed", {"source_time_window": True, "applicability": "not_required"}, applicability="not_required")
    if t == end:
        return _r("O021", "hole", {"source_time_window": None}, hole_ids=["HOLE:O021:endpoint"], coverage_ok=None)
    inside = start <= t < end
    return _r("O021", "computed", {"source_time_window": inside, "inside": inside}, known_at=t)


@register("O022", ("label", "recorded_at"))
def o022(inp: dict) -> RecipeResult:
    recorded_at = inp.get("recorded_at")
    use_at = inp.get("use_at")
    if inp.get("label") is None:
        return _r("O022", "hole", {"source_clean": None}, hole_ids=["HOLE:O022:source_cleanliness"], coverage_ok=None)
    causal = recorded_at is not None and use_at is not None and recorded_at <= use_at
    if recorded_at is not None and use_at is not None and recorded_at > use_at:
        return _r("O022", "invalid", {"source_clean": False}, base_ok=False, reason="causal")
    return _r("O022", "supplied", {
        "source_clean": True if causal else None,
        "selector_from_pnl": False,
    }, known_at=recorded_at)


# The phase narrative is intentionally record-only.  It may contain a single
# phase or a later transition, so the C08 runner supplies its own mandatory
# envelope for this recipe instead of pretending that one phase name is a
# universal required input.
@register("O023", ("known_at",))
def o023(inp: dict) -> RecipeResult:
    dist_at = inp.get("distribution_at")
    use_at = inp.get("use_at")
    if dist_at is not None and use_at is not None and dist_at > use_at:
        return _r("O023", "invalid", {"distribution_available": False}, base_ok=False, reason="causal")
    auto = None
    return _r("O023", "supplied", {
        "accumulation": inp.get("accumulation"),
        "distribution_available": None if dist_at is None or use_at is None else dist_at <= use_at,
        "automatic_amd": auto,
    }, known_at=inp.get("known_at"))


@register("O024", ("attempts",))
def o024(inp: dict) -> RecipeResult:
    attempts = inp["attempts"]
    as_of = inp.get("as_of")
    seen = [a for a in attempts if as_of is None or a["end"] <= as_of]
    distinct = []
    for a in seen:
        if a["id"] not in {d["id"] for d in distinct}:
            distinct.append(a)
    prior = inp.get("prior_allocation")
    max_continue = None if prior is None else prior / 2
    return _r("O024", "computed", {
        "attempt_count": len(distinct),
        "max_continue_allocation": max_continue,
        "touch_rows_are_not_attempts": True,
    }, known_at=as_of)


@register("O025", ("or_h", "or_l"))
def o025(inp: dict) -> RecipeResult:
    h, l = dec(inp.get("or_h")), dec(inp.get("or_l"))
    if h is None or l is None or inp.get("or_end") is None:
        return _r("O025", "hole", {
            "mid": None if h is None or l is None else (h + l) / 2,
            "automatic_or": None,
        }, hole_ids=["HOLE:O025:or_end"], coverage_ok=None)
    mid = (h + l) / 2
    eq = dec(inp.get("range_eq"))
    return _r("O025", "computed", {
        "mid": mid,
        "distinct_from_eq": eq is None or mid != eq,
        "automatic_or": True,
    }, known_at=inp["or_end"])


@register("O026", ("low", "high", "low_confirmed_at", "high_confirmed_at"))
def o026(inp: dict) -> RecipeResult:
    mid = (dec(inp["low"]) + dec(inp["high"])) / 2
    known = max(inp["low_confirmed_at"], inp["high_confirmed_at"])
    touch = inp.get("touch_at")
    post = None if touch is None else touch >= known
    return _r("O026", "computed", {
        "midpoint": mid,
        "known_at": known,
        "post_confirmation_retrace": post,
        "automatic_pivot": None,
    }, known_at=known)


@register("O027", ("current_volume", "baseline"))
def o027(inp: dict) -> RecipeResult:
    known = inp.get("window_end")
    use_at = inp.get("use_at", known)
    if known is not None and use_at is not None and known > use_at:
        return _r("O027", "invalid", {"rvol": None}, base_ok=False, reason="causal")
    rvol = dec(inp["current_volume"]) / dec(inp["baseline"])
    high = inp.get("source_high_rvol")
    return _r("O027", "computed", {
        "rvol": rvol,
        "source_high_rvol": high,
    }, known_at=known)


@register("O028", ("a", "b"))
def o028(inp: dict) -> RecipeResult:
    a, b = dec(inp["a"]), dec(inp["b"])
    exact = a == b
    band = inp.get("source_band")
    near = None
    if band:
        near = dec(band[0]) <= a <= dec(band[1]) and dec(band[0]) <= b <= dec(band[1])
    return _r("O028", "computed", {
        "exact_equality": exact,
        "near_equal": near,
    }, known_at=inp.get("known_at"))


@register("O029", ("as_of",))
def o029(inp: dict) -> RecipeResult:
    as_of = inp.get("as_of")
    sched = inp.get("schedule_known_at")
    rel = inp.get("release_known_at")
    revision = inp.get("revision_at")
    date_only = inp.get("date_only")
    schedule_known = None if sched is None or as_of is None else sched <= as_of
    release_known = False if date_only else (None if rel is None or as_of is None else rel <= as_of)
    if date_only:
        release_known = None
    rev_ok = None if revision is None or as_of is None else revision <= as_of
    return _r("O029", "computed", {
        "schedule_known": schedule_known,
        "release_known": release_known,
        "revision_available": rev_ok,
    }, known_at=as_of)


@register("O047", ("reference_px", "side"))
def o047(inp: dict) -> RecipeResult:
    r = dec(inp["reference_px"])
    side = inp["side"]
    sweep_px = dec(inp.get("sweep_px"))
    close = dec(inp.get("confirm_close"))
    sweep_at = inp.get("sweep_at")
    confirm_at = inp.get("confirm_at")
    decision = inp.get("decision_at")
    ref_known = inp.get("reference_known_at")
    if sweep_at is None or confirm_at is None:
        return _r("O047", "hole", {"failure_confirmed": None}, hole_ids=["HOLE:O047:confirmation"], coverage_ok=None)
    if ref_known is not None and sweep_at < ref_known:
        return _r("O047", "invalid", {"failure_confirmed": False}, base_ok=False, reason="causal")
    if decision is not None and confirm_at > decision:
        return _r("O047", "invalid", {"failure_confirmed": False}, base_ok=False, reason="causal")
    swept = sweep_px > r if side == "short" else sweep_px < r
    if close is None:
        fail = None
    elif side == "short":
        fail = close < r
    else:
        fail = close > r
    seq = True if swept and fail is True else (False if swept and fail is False else None)
    return _r("O047", "computed", {
        "sweep_at": sweep_at,
        "confirm_at": confirm_at,
        "failure_confirmed": seq,
        "swept": swept,
        "strict_close": fail,
        "reference_known_before_sweep": None if ref_known is None else ref_known <= sweep_at,
    }, known_at=confirm_at, base_ok=False if seq is False else True)


@register("O048", ("known_at",))
def o048(inp: dict) -> RecipeResult:
    if inp.get("weekly_convention") is None and inp.get("need_week"):
        return _r("O048", "hole", {"weekly": None}, hole_ids=["HOLE:O048:weekly_scope"], coverage_ok=None)
    pdh, pdl = dec(inp.get("pdh")), dec(inp.get("pdl"))
    pwh, pwl = dec(inp.get("pwh")), dec(inp.get("pwl"))
    px = dec(inp.get("price"))
    return _r("O048", "computed", {
        "pdh": pdh, "pdl": pdl, "pwh": pwh, "pwl": pwl,
        "sweeps_daily_high": None if px is None or pdh is None else px > pdh,
        "sweeps_weekly_high": None if px is None or pwh is None else px > pwh,
    }, known_at=inp.get("known_at"))


@register("O050", ("open_px", "open_at"))
def o050(inp: dict) -> RecipeResult:
    events = inp.get("events") or []
    below = False
    above_after = False
    open_px = dec(inp["open_px"])
    for ev in events:
        if ev["t"] <= inp["open_at"]:
            continue
        px = dec(ev["price"])
        if not below and px < open_px:
            below = True
        elif below and px > open_px:
            above_after = True
    confirm = inp.get("source_confirmation")
    return _r("O050", "computed", {
        "cash_open": open_px,
        "below_then_above": below and above_after,
        "source_confirmation": confirm,
    }, known_at=inp.get("known_at", inp["open_at"]))


@register("O055", ("gap",))
def o055(inp: dict) -> RecipeResult:
    gap = inp.get("gap")
    if gap is None:
        return _r("O055", "hole", {"gap": None}, hole_ids=["HOLE:O055:construction"], coverage_ok=None)
    lo, hi = dec(gap[0]), dec(gap[1])
    fill_at = inp.get("fill_at")
    as_of = inp.get("as_of")
    filled = fill_at is not None and (as_of is None or fill_at <= as_of)
    touch = inp.get("touch_px")
    partial = None
    if touch is not None:
        partial = lo < dec(touch) < hi
        far = dec(touch) == lo or dec(touch) == hi
    else:
        far = None
    return _r("O055", "supplied", {
        "lo": lo, "hi": hi,
        "filled": filled,
        "partial_contact": partial,
        "far_edge": far,
        "active_gap": inp.get("active_policy"),
    }, known_at=inp.get("known_at"))


@register("O056", ("c1_l", "c2", "c3_close"))
def o056(inp: dict) -> RecipeResult:
    c2 = inp["c2"]
    ob = [dec(c2["L"]), dec(c2["H"])]
    mid = (ob[0] + ob[1]) / 2
    sweep = dec(c2["L"]) < dec(inp["c1_l"])
    confirm = dec(inp["c3_close"]) > dec(c2["H"])
    if inp.get("decision_at") is not None and inp.get("c3_known_at") is not None and inp["decision_at"] < inp["c3_known_at"]:
        return _r("O056", "invalid", {"confirmed": False}, base_ok=False, reason="causal")
    wick = [dec(c2["L"]), min(dec(c2["O"]), dec(c2["C"]))]
    return _r("O056", "computed", {
        "ob": ob,
        "mid": mid,
        "confirmed": sweep and confirm,
        "rejection_wick": wick,
        "wick_is_not_ob": wick != ob,
    }, known_at=inp.get("c3_known_at"))


@register("O057", ("O", "H", "L", "C"))
def o057(inp: dict) -> RecipeResult:
    o, h, l, c = dec(inp["O"]), dec(inp["H"]), dec(inp["L"]), dec(inp["C"])
    lower = [l, min(o, c)]
    upper = [max(o, c), h]
    full = [l, h]
    if lower[0] == lower[1]:
        lower = None
    return _r("O057", "computed", {
        "lower_wick": lower,
        "upper_wick": upper if upper[0] != upper[1] else None,
        "lower_width": None if lower is None else lower[1] - lower[0],
        "upper_width": None if upper[0] == upper[1] else upper[1] - upper[0],
        "full_ob": full,
    }, known_at=inp.get("known_at"))


@register("O058", ("O", "H", "L", "C", "V"))
def o058(inp: dict) -> RecipeResult:
    o, h, l, c, v = dec(inp["O"]), dec(inp["H"]), dec(inp["L"]), dec(inp["C"]), dec(inp["V"])
    rng = h - l
    body = abs(c - o)
    body_ratio = None if rng == 0 else body / rng
    prior = inp.get("prior_volumes")
    avg = None if not prior else sum((dec(x) for x in prior), Decimal(0)) / len(prior)
    vol_ratio = None if avg in (None, 0) else v / avg
    inside = None
    if body_ratio is not None and vol_ratio is not None:
        if body_ratio < Decimal("0.6") and vol_ratio > Decimal("1.5"):
            inside = True
        elif body_ratio == Decimal("0.6") or vol_ratio == Decimal("1.5"):
            inside = None
        else:
            inside = False
    return _r("O058", "computed", {
        "body_ratio": body_ratio,
        "volume_average": avg,
        "volume_ratio": vol_ratio,
        "displayed_small_body_high_volume": inside,
        "comparison_convention": None if inside is None else "strict",
    }, known_at=inp.get("known_at"), hole_ids=[] if inside is not None else ["HOLE:O058:comparison"])


@register("O061", ("trades",))
def o061(inp: dict) -> RecipeResult:
    bins = {}
    q = dec(inp.get("q", Q))
    for tr in inp["trades"]:
        if tr.get("is_quote"):
            continue
        px = dec(tr["price"])
        sz = dec(tr["size"])
        if inp.get("bin_lo") is not None:
            key = "agg"
            if not (dec(inp["bin_lo"]) <= px < dec(inp["bin_hi"])):
                continue
        else:
            key = px
        bins[key] = bins.get(key, Decimal(0)) + sz
    return _r("O061", "computed", {
        "bins": {str(k): v for k, v in bins.items()},
        "total": sum(bins.values(), Decimal(0)),
        "source_binning": None if inp.get("source_binning") is None else inp.get("source_binning"),
    }, known_at=inp.get("known_at"), hole_ids=[] if inp.get("source_binning") is not None or inp.get("native", True) else ["HOLE:O061:binning"])


@register("O062", ("known_at",))
def o062(inp: dict) -> RecipeResult:
    total, covered = dec(inp.get("total")), dec(inp.get("covered"))
    val, vah = dec(inp.get("val")), dec(inp.get("vah"))
    bins = inp.get("bins")
    if bins is not None:
        histogram = {dec(price): dec(volume) for price, volume in bins.items()}
        if any(volume < 0 for volume in histogram.values()):
            return _r("O062", "invalid", {"achieved_fraction": None}, base_ok=False, reason="negative profile volume")
        total = sum(histogram.values(), Decimal(0))
        convention = inp.get("boundary_convention")
        if val is not None and vah is not None and val <= vah and convention in {"closed", "left_closed_right_open"}:
            covered = sum((volume for price, volume in histogram.items()
                           if val <= price and (price <= vah if convention == "closed" else price < vah)), Decimal(0))
    missing = [name for name, value in (("total", total), ("covered", covered)) if value is None]
    if missing:
        return _r("O062", "hole", {"achieved_fraction": None, "val": val, "vah": vah},
                  hole_ids=[f"HOLE:O062:{name}" for name in missing], base_ok=None, coverage_ok=None)
    if total < 0 or covered < 0 or covered > total:
        return _r("O062", "invalid", {"achieved_fraction": None}, base_ok=False, reason="invalid profile coverage volumes")
    if total == 0:
        return _r("O062", "hole", {"achieved_fraction": None, "meets_required": None},
                  hole_ids=["HOLE:O062:positive_volume"], base_ok=None, coverage_ok=None)
    frac = covered / total
    req = dec(inp.get("required_fraction"))
    if req is not None and not 0 < req <= 1:
        return _r("O062", "invalid", {"achieved_fraction": frac}, base_ok=False, reason="invalid source value fraction")
    construction_known = bool(inp.get("construction_rule"))
    holes = [] if construction_known else ["HOLE:O062:construction"]
    if req is None:
        holes.append("HOLE:O062:required_fraction")
    return _r("O062", "computed", {
        "achieved_fraction": frac,
        "meets_required": None if req is None else frac >= req,
        "fraction": req, "volume_inside": covered, "val": val, "vah": vah,
        "construction_known": construction_known,
        "construction": inp.get("construction"),
    }, known_at=inp.get("known_at"), hole_ids=holes)


@register("O063", ("snapshots", "as_of"))
def o063(inp: dict) -> RecipeResult:
    as_of = inp["as_of"]
    chosen = None
    for snap in inp["snapshots"]:
        if snap["known_at"] <= as_of:
            chosen = snap
    if chosen is None:
        return _r("O063", "hole", {"poc": None}, coverage_ok=None, hole_ids=["HOLE:O063:snapshot"])
    return _r("O063", "computed", {
        "poc": chosen["poc"],
        "snapshot_known_at": chosen["known_at"],
        "mutated": False,
    }, known_at=chosen["known_at"])


@register("O064", ("bins",))
def o064(inp: dict) -> RecipeResult:
    bins = {dec(k): dec(v) for k, v in inp["bins"].items()}
    if any(value < 0 for value in bins.values()):
        return _r("O064", "invalid", {"poc": None}, base_ok=False, reason="negative profile volume")
    if not bins or sum(bins.values(), Decimal(0)) == 0:
        return _r("O064", "hole", {"poc": None, "poc_candidates": []},
                  hole_ids=["HOLE:O064:positive_volume"], base_ok=None, coverage_ok=None)
    mx = max(bins.values())
    cands = sorted(p for p, v in bins.items() if v == mx)
    rule = inp.get("tie_rule")
    poc = cands[0] if len(cands) == 1 else None
    if len(cands) > 1:
        if rule == "lowest":
            poc = cands[0]
        elif rule == "highest":
            poc = cands[-1]
        elif rule == "supplied" and dec(inp.get("supplied_poc")) in cands:
            poc = dec(inp["supplied_poc"])
    prices = sorted(bins)
    mid = (prices[0] + prices[-1]) / 2
    return _r("O064", "computed" if poc is not None else "hole", {
        "poc": poc,
        "max": mx,
        "max_volume": mx, "poc_candidates": cands, "poc_price_or_band": poc,
        "tie_state": "unique" if len(cands) == 1 else ("resolved" if poc is not None else "unresolved"),
        "tied": len(cands) > 1,
        "profile_midpoint": mid,
        "mid_is_poc_formula": False,
    }, known_at=inp.get("known_at"), hole_ids=[] if poc is not None else ["HOLE:O064:tie_rule"], coverage_ok=True if poc is not None else None)


@register("O066", ("node",))
def o066(inp: dict) -> RecipeResult:
    node = inp.get("node")
    if node is None:
        return _r("O066", "hole", {"volume": None}, hole_ids=["HOLE:O066:selector"], coverage_ok=None)
    vols = [dec(v) for v in inp.get("volumes", [])]
    peak = inp.get("peak")
    other = inp.get("reaction")
    overlap = None
    if other:
        a0, a1 = dec(node[0]), dec(node[1])
        b0, b1 = dec(other[0]), dec(other[1])
        overlap = [max(a0, b0), min(a1, b1)]
        if overlap[0] > overlap[1]:
            overlap = None
    return _r("O066", "supplied", {
        "node": [dec(node[0]), dec(node[1])],
        "volume": sum(vols, Decimal(0)),
        "peak": peak,
        "overlap": overlap,
        "independent_hvn": inp.get("independent_hvn"),
    }, known_at=inp.get("known_at"))


@register("O067", ("accepted_a", "accepted_b"))
def o067(inp: dict) -> RecipeResult:
    if inp.get("accepted_b") is None:
        return _r("O067", "hole", {"bridge_volume": None}, hole_ids=["HOLE:O067:accepted_area"], coverage_ok=None, base_ok=False)
    vols = [dec(v) for v in inp.get("bridge_volumes", [])]
    return _r("O067", "supplied", {
        "bridge_volume": sum(vols, Decimal(0)),
        "trough": inp.get("trough"),
    }, known_at=inp.get("known_at"))


@register("O068", ("shelf",))
def o068(inp: dict) -> RecipeResult:
    shelf = inp.get("shelf")
    if shelf is None:
        return _r("O068", "hole", {}, hole_ids=["HOLE:O068:detector"], coverage_ok=None)
    sv = sum((dec(v) for v in inp.get("shelf_volumes", [])), Decimal(0))
    tv = sum((dec(v) for v in inp.get("transition_volumes", [])), Decimal(0))
    return _r("O068", "supplied", {
        "shelf": [dec(shelf[0]), dec(shelf[1])],
        "shelf_volume": sv,
        "transition_volume": tv,
        "ratio_defines_ledge": False,
    }, known_at=inp.get("known_at"))


@register("O069", ("ledge_px",))
def o069(inp: dict) -> RecipeResult:
    ledge = dec(inp["ledge_px"])
    retest = dec(inp.get("retest_px"))
    same = retest == ledge if retest is not None else None
    vah = dec(inp.get("dev_vah"))
    vah_is_retest = False if vah is None or retest is None else retest == vah and vah != ledge
    return _r("O069", "computed", {
        "same_id": same,
        "vah_touch_is_retest": vah_is_retest,
    }, known_at=inp.get("known_at"))


@register("O073", ("lvn",))
def o073(inp: dict) -> RecipeResult:
    use_at = inp.get("use_at")
    hold_at = inp.get("hold_known_at")
    if hold_at is not None and use_at is not None and hold_at > use_at:
        return _r("O073", "invalid", {"hold_available": False}, base_ok=False, reason="causal")
    rth_poc = dec(inp.get("rth_poc"))
    return _r("O073", "supplied", {
        "lvn": inp.get("lvn"),
        "older_poc": dec(inp.get("older_poc")),
        "rth_poc_does_not_revise": rth_poc,
        "hold_available": None if hold_at is None or use_at is None else hold_at <= use_at,
    }, known_at=inp.get("known_at"))


@register("O075", ("balance",))
def o075(inp: dict) -> RecipeResult:
    open_px = dec(inp.get("open_px"))
    bal = inp.get("balance")
    va = inp.get("va")
    inside_bal = None if not bal or open_px is None else dec(bal[0]) <= open_px <= dec(bal[1])
    inside_va = None if not va or open_px is None else dec(va[0]) <= open_px <= dec(va[1])
    unresolved = inp.get("condition_unresolved", True)
    return _r("O075", "computed", {
        "inside_balance": inside_bal,
        "inside_va": inside_va,
        "cohort_eligibility": None if unresolved else inside_bal,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O075:scope"] if unresolved else [])


@register("O077", ("levels",))
def o077(inp: dict) -> RecipeResult:
    delta = Decimal(0)
    total = Decimal(0)
    unknown = Decimal(0)
    known = True
    for lvl in inp["levels"]:
        b = dec(lvl.get("B", 0))
        a = dec(lvl.get("A", 0))
        u = dec(lvl.get("N", 0))
        delta += b - a
        total += b + a + u
        unknown += u
        if u:
            known = False
    lo = delta - unknown
    hi = delta + unknown
    return _r("O077", "computed", {
        "known_delta": delta if known else None,
        "delta_interval": [lo, hi] if not known else [delta, delta],
        "total": total,
    }, known_at=inp.get("known_at"))


@register("O086", ("prior_high", "prior_close", "open_px"))
def o086(inp: dict) -> RecipeResult:
    ph, pc, op = dec(inp["prior_high"]), dec(inp["prior_close"]), dec(inp["open_px"])
    half_session = (op + ph) / 2
    half_close = (op + pc) / 2
    px = dec(inp.get("price"))
    return _r("O086", "computed", {
        "half_session_gap": half_session,
        "half_close_gap": half_close,
        "touches_half_session": None if px is None else px == half_session,
        "fill_to_high": False,
    }, known_at=inp.get("known_at"))


@register("O087", ("objective_px",))
def o087(inp: dict) -> RecipeResult:
    scope = inp.get("scope", "rth_only")
    eth_hit = inp.get("eth_hit")
    rth_hit = inp.get("rth_hit")
    decision = inp.get("decision_at")
    active = True
    if scope == "rth_only":
        active = not (rth_hit is not None and (decision is None or rth_hit < decision))
        if rth_hit is not None and decision is not None and rth_hit > decision:
            consumed_after = True
        else:
            consumed_after = False
    else:
        active = eth_hit is None
        consumed_after = False
    return _r("O087", "computed", {
        "active": active,
        "consumed_after_entry": consumed_after if scope == "rth_only" else False,
        "eth_hit_consumes_rth": False if scope == "rth_only" else True,
    }, known_at=inp.get("known_at"))


@register("O088", ("n", "onh", "onl", "both"))
def o088(inp: dict) -> RecipeResult:
    n = inp["n"]
    either = inp["onh"] + inp["onl"] - inp["both"]
    h, l = dec(inp.get("eth_h")), dec(inp.get("eth_l"))
    mpoc = None if h is None or l is None else (h + l) / 2
    return _r("O088", "computed", {
        "either": either,
        "either_rate": Decimal(either) / n,
        "both_rate": Decimal(inp["both"]) / n,
        "mpoc": mpoc,
        "not_volume_poc": True,
    }, known_at=inp.get("known_at"))


@register("O098", ("events",))
def o098(inp: dict) -> RecipeResult:
    buy = sell = unknown = 0
    total = 0
    for ev in inp["events"]:
        if ev.get("action") and ev["action"] != "T":
            continue
        got = signed_size(ev.get("side"), ev.get("size", 0))
        total += got["executed_size"] or 0
        if got["sign"] == 1:
            buy += ev["size"]
        elif got["sign"] == -1:
            sell += ev["size"]
        else:
            unknown += ev.get("size") or 0
    delta = buy - sell if unknown == 0 else None
    lo = (buy - sell) - unknown
    hi = (buy - sell) + unknown
    return _r("O098", "computed", {
        "buy": buy, "sell": sell, "unknown": unknown,
        "total": total, "delta": delta,
        "delta_interval": [lo, hi],
    }, known_at=inp.get("known_at"))


@register("O099", ("trades", "threshold"))
def o099(inp: dict) -> RecipeResult:
    thr = dec(inp["threshold"])
    mode = inp.get("mode", "per_print")
    marks = 0
    if mode == "per_print":
        for tr in inp["trades"]:
            if dec(tr["size"]) >= thr:
                marks += 1
    elif mode == "cluster":
        s = sum(dec(tr["size"]) for tr in inp["trades"])
        marks = 1 if s >= thr else 0
    return _r("O099", "computed", {
        "markers": marks,
        "mode": mode,
        "same_as_other_mode": False,
    }, known_at=inp.get("known_at"))


@register("O101", ("effort_size", "progress"))
def o101(inp: dict) -> RecipeResult:
    effort = dec(inp.get("effort_size"))
    progress = dec(inp.get("progress"))
    interp = inp.get("source_absorption")
    later = dec(inp.get("later_decline"))
    return _r("O101", "computed", {
        "effort": effort,
        "progress": progress,
        "absorption": interp,
        "later_decline_repairs": False,
        "later_decline": later,
    }, known_at=inp.get("known_at"), hole_ids=[] if interp is not None else ["HOLE:O101:detector"])


@register("O107", ("B", "A"))
def o107(inp: dict) -> RecipeResult:
    b, a = dec(inp.get("B", 0)), dec(inp.get("A", 0))
    total = b + a
    delta = b - a
    frac = None if total == 0 else delta / total
    return _r("O107", "computed", {
        "delta": delta, "total": total, "fraction": frac,
        "source_spike": inp.get("source_spike"),
    }, known_at=inp.get("known_at"), hole_ids=[] if inp.get("source_spike") is not None else ["HOLE:O107:classifier"])


@register("O120", ("O", "H", "L", "C"))
def o120(inp: dict) -> RecipeResult:
    o, h, l, c = dec(inp["O"]), dec(inp["H"]), dec(inp["L"]), dec(inp["C"])
    body = sorted([o, c])
    wick_low = l
    wick_high = h
    body_delta = None
    rows = inp.get("body_rows")
    if rows:
        b = sum(dec(r.get("B", 0)) for r in rows)
        a = sum(dec(r.get("A", 0)) for r in rows)
        body_delta = b - a
    as_of_c = dec(inp.get("as_of_c"))
    future_in_asof = False
    if as_of_c is not None:
        future_in_asof = dec(inp.get("later_price", 0)) == as_of_c
    return _r("O120", "computed", {
        "body_prices": body,
        "wick_low": wick_low,
        "wick_high": wick_high,
        "body_delta": body_delta,
        "later_price_in_earlier_asof": future_in_asof,
    }, known_at=inp.get("known_at"))


@register("O139", ("entry", "stop", "side"))
def o139(inp: dict) -> RecipeResult:
    e, s = dec(inp["entry"]), dec(inp["stop"])
    q = dec(inp.get("q", Q))
    side = inp["side"]
    dist = (e - s) if side == "long" else (s - e)
    valid = dist > 0
    ticks = dist / q if q else None
    close_rule = inp.get("close_below")
    wick = dec(inp.get("intrabar_low"))
    breached = False
    if close_rule is not None and wick is not None:
        breached = False
    return _r("O139", "computed" if valid else "invalid", {
        "entry": e, "stop": s, "side": side,
        "risk_points": dist,
        "risk_ticks": ticks,
        "valid_initial_stop": valid,
        "wick_breaches_close_policy": breached,
    }, base_ok=valid, known_at=inp.get("known_at"))


@register("O140", ("D", "quantity"))
def o140(inp: dict) -> RecipeResult:
    d = dec(inp["D"])
    m = dec(inp.get("M"))
    qty = dec(inp["quantity"])
    if m is None:
        return _r("O140", "hole", {"unit_risk": None}, hole_ids=["HOLE:O140:M"], coverage_ok=None)
    unit = d * m
    pos = unit * qty
    cap = dec(inp.get("cap"))
    cap_ok = None if cap is None else pos <= cap
    alloc = None
    if cap is not None and inp.get("integer_max"):
        alloc = int(cap // unit)
    return _r("O140", "computed", {
        "unit_risk": unit,
        "position_risk": pos,
        "cap_ok": cap_ok,
        "integer_max_contracts": alloc,
    }, known_at=inp.get("known_at"))


@register("O141", ("entry", "target", "selected_at", "decision_at"))
def o141(inp: dict) -> RecipeResult:
    if inp["selected_at"] > inp["decision_at"]:
        return _r("O141", "invalid", {"distance": None}, base_ok=False, reason="causal")
    e, t = dec(inp["entry"]), dec(inp["target"])
    dist = abs(t - e)
    prints = inp.get("prints") or []
    hit_after = any(p["t"] > inp["decision_at"] and dec(p["price"]) == t for p in prints)
    return _r("O141", "computed", {
        "entry": e, "target": t, "selected_at": inp["selected_at"],
        "distance": dist,
        "pre_entry_print_counts": False,
        "post_entry_hit": hit_after,
    }, known_at=inp["selected_at"])


@register("O142", ("position", "entry_at"))
def o142(inp: dict) -> RecipeResult:
    """Replay the supplied position-management ledger.

    O142 is deliberately an observation audit.  The recipe never turns a
    requested quantity into a fill and never derives a policy from a later
    price path.  The compact ``fills``/``trail_at`` fields used by the printed
    fixture are accepted as legacy spellings of the corresponding action
    records; richer callers can provide ``actions`` or
    ``management_actions``.
    """

    pos = dec(inp["position"])
    entry_at = inp["entry_at"]
    holes: list[str] = []
    reasons: list[str] = []
    base_ok: bool | None = True

    def _at(record: dict):
        for key in ("t", "at", "event_at", "time"):
            if record.get(key) is not None:
                return record[key]
        return None

    def _kind(record: dict) -> str:
        raw = record.get("kind", record.get("type", record.get("action", "")))
        return str(raw).strip().lower().replace("-", "_").replace(" ", "_")

    def _qty(record: dict):
        for key in ("filled_qty", "filled_quantity", "qty", "quantity", "size", "amount"):
            if record.get(key) is not None:
                return dec(record[key])
        return None

    # Normalize actual partial/exit fills, retaining every source field so the
    # result remains an auditable ledger rather than a simulated order stream.
    actions: list[dict] = []
    for fill in inp.get("fills") or []:
        if isinstance(fill, dict):
            row = dict(fill)
            row.setdefault("kind", "partial_fill")
        else:
            row = {"kind": "partial_fill", "qty": fill}
        actions.append(row)
    for action in inp.get("management_actions", inp.get("actions", [])) or []:
        if isinstance(action, dict):
            actions.append(dict(action))

    # Preserve the original compact trail fixture as an observed action.  A
    # supplied support timestamp after the trail event is a causal failure.
    if inp.get("trail_at") is not None and not any(
        _kind(a) in {"trail", "stop_move", "stop_amend", "breakeven"} and _at(a) == inp["trail_at"]
        for a in actions
    ):
        actions.append({"kind": "trail", "at": inp["trail_at"], "protected_at": inp.get("protected_at")})
    actions.sort(key=lambda a: (_at(a) is None, _at(a) if _at(a) is not None else 0))

    initial_stop = None
    for key in ("initial_stop", "initial_stop_px", "stop_initial"):
        if inp.get(key) is not None:
            initial_stop = dec(inp[key])
            break
    initial_target = None
    for key in ("initial_target", "initial_target_px", "target_initial"):
        if inp.get(key) is not None:
            initial_target = dec(inp[key])
            break
    initial_entry = dec(inp.get("entry_px", inp.get("entry_price", inp.get("entry"))))
    side = inp.get("side")
    initial_risk = dec(inp.get("initial_risk", inp.get("risk_points")))
    if initial_risk is None and initial_entry is not None and initial_stop is not None:
        if side == "long":
            initial_risk = initial_entry - initial_stop
        elif side == "short":
            initial_risk = initial_stop - initial_entry
        else:
            initial_risk = abs(initial_entry - initial_stop)

    stop_versions: list[dict] = []
    target_versions: list[dict] = []
    if initial_stop is not None:
        stop_versions.append({"version": 0, "at": entry_at, "stop": initial_stop})
    if initial_target is not None:
        target_versions.append({"version": 0, "at": entry_at, "target": initial_target})

    remaining = pos
    filled_total = Decimal(0)
    added_total = Decimal(0)
    exited_total = Decimal(0)
    trail_checks: list[bool | None] = []
    action_results: list[dict] = []
    policy = inp.get("source_policy", inp.get("policy", inp.get("action_policy")))
    explicit_policy_ok = inp.get("action_policy_ok")
    policy_checks: list[bool | None] = []
    risk_after_values: list[Decimal] = []
    recognized = {
        "partial", "partial_fill", "fill", "exit", "partial_exit", "scale_out",
        "close", "reduce", "trail", "stop_move", "stop_amend", "breakeven",
        "target_move", "target_amend", "amend", "add", "scale_in", "increase",
    }

    def _policy_allows(kind: str) -> bool | None:
        if policy is None:
            return None
        if isinstance(policy, dict):
            allowed = policy.get("allowed_actions", policy.get("actions"))
            if allowed is None:
                name = policy.get("name", policy.get("kind"))
                allowed = [name] if name is not None else None
            if allowed is None:
                return None
            allowed = {str(v).lower().replace("-", "_").replace(" ", "_") for v in allowed}
        elif isinstance(policy, (list, tuple, set)):
            allowed = {str(v).lower().replace("-", "_").replace(" ", "_") for v in policy}
        else:
            name = str(policy).lower().replace("-", "_").replace(" ", "_")
            allowed = {name}
        if kind in allowed or "all" in allowed:
            return True
        # Policy labels name a family of actions.  Keep this mapping narrow so
        # an arbitrary source label cannot become a universal permission.
        families = {
            "static": {"exit", "close", "partial_exit"},
            "partial": {"partial", "partial_fill", "partial_exit", "scale_out", "exit", "close"},
            "breakeven": {"breakeven", "exit", "close"},
            "trail": {"trail", "stop_move", "stop_amend", "exit", "close"},
            "add": {"add", "scale_in", "increase", "exit", "close"},
        }
        return any(kind in families.get(name, set()) for name in allowed)

    for action in actions:
        kind = _kind(action)
        at = _at(action)
        row = dict(action)
        row["kind"] = kind
        row["at"] = at
        qty = _qty(action)
        if at is None:
            holes.append("HOLE:O142:action_at")
        elif at < entry_at:
            base_ok = False
            reasons.append("action before entry")
            holes.append("HOLE:O142:ordering")
        if kind not in recognized:
            if kind:
                policy_checks.append(None)
            row["applied_quantity"] = Decimal(0)
            action_results.append(row)
            continue

        # Requested partials are records, not fills.  Only explicit filled_qty
        # (or the compact fills list) changes position quantity.
        reduce_kind = kind in {"partial", "partial_fill", "fill", "exit", "partial_exit", "scale_out", "close", "reduce"}
        add_kind = kind in {"add", "scale_in", "increase"}
        applied = Decimal(0)
        if qty is not None and at is not None and at >= entry_at:
            if reduce_kind:
                if qty < 0:
                    base_ok = False
                    reasons.append("negative management quantity")
                    holes.append("HOLE:O142:quantity")
                else:
                    applied = qty
                    if applied > remaining:
                        base_ok = False
                        reasons.append("management quantity exceeds position")
                        holes.append("HOLE:O142:overfill")
                        applied = remaining
                    remaining -= applied
                    filled_total += applied
                    exited_total += applied
            elif add_kind:
                secured = action.get("risk_secured", action.get("earlier_risk_secured", action.get("secured")))
                if secured is False:
                    base_ok = False
                    reasons.append("add without secured risk")
                    holes.append("HOLE:O142:secured_add")
                    policy_checks.append(False)
                elif secured is None:
                    policy_checks.append(None)
                    holes.append("HOLE:O142:secured_add")
                else:
                    policy_checks.append(True)
                applied = qty
                if applied < 0:
                    base_ok = False
                    reasons.append("negative add quantity")
                    holes.append("HOLE:O142:quantity")
                else:
                    remaining += applied
                    added_total += applied
        row["applied_quantity"] = applied

        # Structural support must be confirmed at or before the trail action.
        if kind in {"trail", "stop_move", "stop_amend", "breakeven"}:
            support_at = None
            for key in ("protected_known_at", "protected_at", "support_known_at", "confirmed_at"):
                if action.get(key) is not None:
                    support_at = action[key]
                    break
            if support_at is None:
                trail_checks.append(None)
                holes.append("HOLE:O142:protected_confirmation")
            else:
                ok = at is not None and support_at <= at
                trail_checks.append(ok)
                if not ok:
                    base_ok = False
                    reasons.append("trail support confirmed after action")
                    holes.append("HOLE:O142:ordering")

        new_stop = None
        for key in ("new_stop", "stop_px", "stop_price", "stop"):
            if action.get(key) is not None and kind in {"trail", "stop_move", "stop_amend", "breakeven", "amend"}:
                new_stop = dec(action[key])
                break
        if new_stop is not None:
            stop_versions.append({"version": len(stop_versions), "at": at, "stop": new_stop})
        new_target = None
        for key in ("new_target", "target_px", "target_price", "target"):
            if action.get(key) is not None and kind in {"target_move", "target_amend", "amend"}:
                new_target = dec(action[key])
                break
        if new_target is not None:
            target_versions.append({"version": len(target_versions), "at": at, "target": new_target})
        for key in ("initial_risk", "initial_risk_points"):
            if action.get(key) is not None:
                risk_after_values.append(dec(action[key]))
        policy_checks.append(_policy_allows(kind))
        action_results.append(row)

    # Legacy trail fields remain meaningful even when no rich action ledger is
    # supplied.  Keep the boolean explicit and preserve a late support as a
    # causal failure rather than making the action merely unknown.
    trail_at = inp.get("trail_at")
    prot_at = inp.get("protected_at")
    if trail_at is not None and prot_at is not None and not trail_checks:
        trail_checks.append(prot_at <= trail_at)
        if prot_at > trail_at:
            base_ok = False
            reasons.append("trail support confirmed after action")
            holes.append("HOLE:O142:ordering")
    trail_ok: bool | None
    if any(v is False for v in trail_checks):
        trail_ok = False
    elif any(v is None for v in trail_checks):
        trail_ok = None
    elif trail_checks:
        trail_ok = True
    else:
        trail_ok = None

    if explicit_policy_ok is not None:
        policy_ok = bool(explicit_policy_ok)
    elif policy_checks:
        policy_ok = False if any(v is False for v in policy_checks) else (None if any(v is None for v in policy_checks) else True)
    elif policy is None:
        policy_ok = None
    else:
        # A named static policy with no actions is still a recorded policy;
        # other policies need at least one action to audit.
        name = str(policy.get("name", policy.get("kind", "")) if isinstance(policy, dict) else policy).lower()
        policy_ok = True if name in {"static", "static_target", "static_objective"} else None
    if policy_ok is None:
        holes.append("HOLE:O142:action_policy")

    initial_risk_unchanged: bool | None
    if initial_risk is None:
        initial_risk_unchanged = None
        holes.append("HOLE:O142:initial_risk")
    else:
        initial_risk_unchanged = all(value == initial_risk for value in risk_after_values)
        if not initial_risk_unchanged:
            base_ok = False
            holes.append("HOLE:O142:initial_risk")

    known_at = inp.get("known_at")
    times = [t for t in (_at(a) for a in actions) if t is not None]
    latest_action_at = max(times) if times else None
    if known_at is not None and latest_action_at is not None and latest_action_at > known_at:
        # The claimed snapshot cannot predate an action whose ledger row is
        # already being used.  Keep the action values for audit, but mark the
        # availability error explicitly.
        base_ok = False
        holes.append("HOLE:O142:ordering")
        reasons.append("action available after claimed snapshot")
        known_at = latest_action_at
    elif known_at is None:
        known_at = latest_action_at
    value = {
        "remaining": remaining,
        "position_quantity_after": remaining,
        "filled_quantity": filled_total,
        "added_quantity": added_total,
        "exited_quantity": exited_total,
        "management_actions": action_results,
        "trail_supported": trail_ok,
        "stop_versions": stop_versions,
        "target_versions": target_versions,
        "action_policy_ok": policy_ok,
        "initial_stop": initial_stop,
        "initial_target": initial_target,
        "initial_risk": initial_risk,
        "initial_risk_unchanged": initial_risk_unchanged,
        "exit_reason": inp.get("exit_reason"),
        "requested_partial": inp.get("requested_partial"),
    }
    holes = list(dict.fromkeys(holes))
    state = "invalid" if base_ok is False and any(h.endswith(":ordering") or h.endswith(":overfill") for h in holes) else "computed"
    coverage = None if holes else True
    reason = reasons[0] if reasons else ("source policy or initial risk unavailable" if holes else None)
    return _r("O142", state, value, hole_ids=holes, coverage_ok=coverage,
              base_ok=base_ok, known_at=known_at, reason=reason)


@register("O145", ("results_r", "limit_r"))
def o145(inp: dict) -> RecipeResult:
    if any(x is None for x in inp["results_r"]):
        return _r("O145", "hole", {"permission": None}, hole_ids=["HOLE:O145:prior_result"], coverage_ok=None)
    total = sum(dec(x) for x in inp["results_r"])
    lim = dec(inp["limit_r"])
    perm = total > lim
    return _r("O145", "computed", {
        "sum_r": total,
        "entry_permission": perm,
    }, known_at=inp.get("known_at"))


@register("O150", ("limit",))
def o150(inp: dict) -> RecipeResult:
    """Audit an observed order/ticket lifecycle.

    Bracket distances, tick size, cancellation age, side and quantity are
    source configuration, not universal defaults.  They are calculated only
    when explicitly supplied (or when an explicit stop/target price is
    supplied).  The compact ``fill_qtys`` spelling remains supported for the
    printed fixture; richer callers can provide timestamped lifecycle events.
    """

    limit = dec(inp["limit"])
    q = dec(inp.get("q"))
    side = inp.get("side")
    holes: list[str] = []
    reasons: list[str] = []
    base_ok: bool | None = True

    placed = inp.get("placed_at", inp.get("placement_at"))
    decision = inp.get("decision_at")
    explicit_stop = dec(inp.get("stop"))
    explicit_target = dec(inp.get("target"))
    stop_ticks = dec(inp.get("stop_ticks"))
    target_ticks = dec(inp.get("target_ticks"))
    cancel_minutes = dec(inp.get("cancel_minutes"))
    cancel_at = inp.get("cancel_at")

    if explicit_stop is None and stop_ticks is not None:
        if q is None:
            holes.append("HOLE:O150:q")
        elif side not in {"long", "short"}:
            holes.append("HOLE:O150:side")
        elif side == "long":
            explicit_stop = limit - stop_ticks * q
        else:
            explicit_stop = limit + stop_ticks * q
    if explicit_target is None and target_ticks is not None:
        if q is None:
            holes.append("HOLE:O150:q")
        elif side not in {"long", "short"}:
            holes.append("HOLE:O150:side")
        elif side == "long":
            explicit_target = limit + target_ticks * q
        else:
            explicit_target = limit - target_ticks * q
    if stop_ticks is not None and stop_ticks <= 0:
        base_ok = False
        reasons.append("non-positive stop distance")
        holes.append("HOLE:O150:stop_ticks")
    if target_ticks is not None and target_ticks <= 0:
        base_ok = False
        reasons.append("non-positive target distance")
        holes.append("HOLE:O150:target_ticks")
    if cancel_at is None and placed is not None and cancel_minutes is not None:
        if cancel_minutes < 0:
            base_ok = False
            reasons.append("negative cancellation age")
            holes.append("HOLE:O150:cancel_minutes")
        else:
            cancel_at = placed + int(cancel_minutes * 60) * 1_000_000_000

    quantity = dec(inp.get("quantity"))
    if quantity is not None and quantity < 0:
        base_ok = False
        reasons.append("negative order quantity")
        holes.append("HOLE:O150:quantity")

    # Normalize the actual event ledger.  A numeric fill quantity is retained
    # as a fill with no timestamp; that keeps the old fixture useful while
    # making missing event keys visible in lifecycle_valid.
    events: list[dict] = []
    for event in inp.get("events", inp.get("order_events", inp.get("lifecycle", []))) or []:
        if isinstance(event, dict):
            events.append(dict(event))
    for qty in inp.get("fill_qtys", []) or []:
        if isinstance(qty, dict):
            row = dict(qty)
            row.setdefault("kind", "fill")
        else:
            row = {"kind": "fill", "qty": qty}
        events.append(row)
    for key, kind in (("triggered_at", "triggered"), ("cancel_at", "canceled"),
                      ("expired_at", "expired"), ("exit_at", "exit")):
        if inp.get(key) is not None and not any(
            str(e.get("kind", e.get("type", e.get("action", "")))).lower() == kind and
            e.get("t", e.get("at", e.get("event_at"))) == inp[key] for e in events
        ):
            events.append({"kind": kind, "at": inp[key]})

    def _at(event: dict):
        for key in ("t", "at", "event_at", "time"):
            if event.get(key) is not None:
                return event[key]
        return None

    def _kind(event: dict) -> str:
        return str(event.get("kind", event.get("type", event.get("action", "")))).strip().lower().replace("-", "_").replace(" ", "_")

    def _qty(event: dict):
        for key in ("filled_qty", "filled_quantity", "qty", "quantity", "size", "amount"):
            if event.get(key) is not None:
                return dec(event[key])
        return None

    events.sort(key=lambda event: (_at(event) is None, _at(event) if _at(event) is not None else 0))
    filled = Decimal(0)
    exited = Decimal(0)
    amended_qty = quantity
    state = "instruction" if placed is None else "resting"
    canceled_at = None
    timeline: list[dict] = []
    bracket_versions: list[dict] = []
    if explicit_stop is not None or explicit_target is not None:
        bracket_versions.append({"version": 0, "at": placed, "stop": explicit_stop, "target": explicit_target})

    recognized = {"trigger", "triggered", "fill", "partial_fill", "partial", "cancel", "canceled",
                  "expire", "expired", "amend", "replace", "exit", "partial_exit", "close"}
    for event in events:
        kind = _kind(event)
        at = _at(event)
        row = dict(event)
        row["kind"] = kind
        row["at"] = at
        row_before = state
        if at is None:
            holes.append("HOLE:O150:event_at")
        if decision is not None and at is not None and at < decision:
            base_ok = False
            reasons.append("order event before decision")
            holes.append("HOLE:O150:ordering")
        if placed is not None and at is not None and at < placed and kind not in {"instruction"}:
            base_ok = False
            reasons.append("order event before placement")
            holes.append("HOLE:O150:ordering")
        if canceled_at is not None and at is not None and at > canceled_at and kind not in {"amend", "replace", "instruction"}:
            base_ok = False
            reasons.append("event after cancellation")
            holes.append("HOLE:O150:ordering")

        if kind in {"trigger", "triggered"}:
            state = "triggered"
        elif kind in {"fill", "partial_fill", "partial"}:
            qty = _qty(event)
            if qty is None:
                holes.append("HOLE:O150:fill_quantity")
            elif qty < 0:
                base_ok = False
                reasons.append("negative fill quantity")
                holes.append("HOLE:O150:fill_quantity")
            else:
                filled += qty
                state = "filled" if amended_qty is not None and filled >= amended_qty else "partially_filled"
                if amended_qty is not None and filled > amended_qty:
                    base_ok = False
                    reasons.append("filled quantity exceeds order quantity")
                    holes.append("HOLE:O150:overfill")
        elif kind in {"cancel", "canceled"}:
            canceled_at = at
            state = "canceled"
        elif kind in {"expire", "expired"}:
            state = "expired"
        elif kind in {"exit", "partial_exit", "close"}:
            qty = _qty(event)
            if qty is not None:
                exited += max(Decimal(0), qty)
            state = "exited" if quantity is not None and exited >= filled and filled > 0 else state
        elif kind in {"amend", "replace"}:
            new_qty = dec(event.get("new_quantity", event.get("quantity")))
            if new_qty is not None:
                amended_qty = new_qty
            new_stop = dec(event.get("stop", event.get("stop_price")))
            new_target = dec(event.get("target", event.get("target_price")))
            if new_stop is not None or new_target is not None:
                bracket_versions.append({"version": len(bracket_versions), "at": at,
                                         "stop": new_stop, "target": new_target})
        elif kind and kind not in recognized:
            holes.append("HOLE:O150:event_kind")
        row["state_before"] = row_before
        row["state_after"] = state
        timeline.append(row)

    if quantity is None:
        holes.append("HOLE:O150:quantity")
        remaining = None
    else:
        remaining = quantity - filled
        if remaining < 0:
            remaining = Decimal(0)
        if canceled_at is not None:
            # Cancellation ends only working quantity; prior fills remain an
            # open position until an observed exit.
            remaining = max(Decimal(0), quantity - filled)
    position_open = None if filled == 0 else filled - exited > 0

    # No policy is inferred from the numbers.  A fully explicit bracket and
    # cancellation configuration can be audited as a supplied source policy;
    # otherwise retain the measured values and leave the policy hole visible.
    source_policy_ok = inp.get("source_policy_ok")
    if source_policy_ok is None:
        source_policy = inp.get("source_policy", inp.get("policy"))
        if source_policy is not None:
            source_policy_ok = bool(inp.get("policy_verified", True))
        elif stop_ticks is not None and target_ticks is not None and cancel_minutes is not None and q is not None and side in {"long", "short"} and placed is not None and quantity is not None:
            source_policy_ok = True
        else:
            source_policy_ok = None
    if source_policy_ok is None:
        holes.append("HOLE:O150:source_policy")
    if placed is None:
        holes.append("HOLE:O150:placed_at")
    if cancel_at is None:
        holes.append("HOLE:O150:cancel_at")

    # Any explicitly supplied fill event makes the lifecycle observable even
    # when there is no full order-event stream.  Missing timestamps remain a
    # coverage hole rather than being assigned the placement time.
    lifecycle_valid: bool | None
    if base_ok is False:
        lifecycle_valid = False
    elif any(h in holes for h in {"HOLE:O150:event_at", "HOLE:O150:fill_quantity", "HOLE:O150:quantity", "HOLE:O150:placed_at"}):
        lifecycle_valid = None
    else:
        lifecycle_valid = True
    if base_ok is False and any(h.endswith(":ordering") or h.endswith(":overfill") for h in holes):
        state = "invalid"
    elif holes and state == "instruction":
        state = "hole"
    known_at = inp.get("known_at")
    event_times = [at for at in (_at(e) for e in events) if at is not None]
    if known_at is None and event_times:
        known_at = max(event_times)
    value = {
        "stop": explicit_stop,
        "target": explicit_target,
        "cancel_at": cancel_at,
        "filled": filled,
        "filled_quantity": filled,
        "remaining": remaining,
        "remaining_quantity": remaining,
        "position_open": position_open,
        "order_state": state,
        "order_state_timeline": timeline,
        "bracket_versions": bracket_versions,
        "lifecycle_valid": lifecycle_valid,
        "source_policy_ok": source_policy_ok,
    }
    holes = list(dict.fromkeys(holes))
    coverage = None if holes else True
    reason = reasons[0] if reasons else ("order policy or lifecycle field unavailable" if holes else None)
    return _r("O150", state, value, hole_ids=holes, coverage_ok=coverage,
              base_ok=base_ok, known_at=known_at, reason=reason)


@register("O162", ("releases", "as_of"))
def o162(inp: dict) -> RecipeResult:
    as_of = inp["as_of"]
    series, period = inp.get('series_id'), inp.get('reference_period')
    releases = inp['releases']
    series_ids = {r.get('series_id') for r in releases if r.get('series_id') is not None}
    periods = {r.get('reference_period') for r in releases if r.get('reference_period') is not None}
    if series is None and len(series_ids) > 1 or period is None and len(periods) > 1:
        return _r('O162', 'hole', {'value': None}, hole_ids=['HOLE:O162:series_period_question'], coverage_ok=None)
    if series is None and len(series_ids) == 1:
        series = next(iter(series_ids))
    if period is None and len(periods) == 1:
        period = next(iter(periods))
    seen, history, missing = [], [], []
    for row in releases:
        if row.get('series_id', series) != series or row.get('reference_period', period) != period:
            continue
        available = row.get('available_at', row.get('at'))
        assumption = None
        if available is None and inp.get('release_as_availability') is True:
            available = row.get('released_at')
            assumption = 'verified release used as availability'
        if type(available) is not int:
            missing.append('available_at')
            continue
        version = {**row, 'available_at': available, 'availability_assumption': assumption}
        history.append(version)
        if available <= as_of:
            seen.append(version)
    if not seen:
        return _r("O162", "hole", {"value": None}, hole_ids=["HOLE:O162:vintage"], coverage_ok=None)
    policy = inp.get('vintage_policy')
    if len(seen) > 1 and policy not in {'latest_available', 'initial_release'}:
        return _r('O162', 'hole', {'value': None, 'vintage_history': history},
                  hole_ids=['HOLE:O162:vintage_policy'], coverage_ok=None)
    if missing:
        return _r('O162', 'hole', {'value': None, 'vintage_history': history},
                  hole_ids=['HOLE:O162:available_at'], coverage_ok=None)
    chosen_at = (min if policy == 'initial_release' else max)(r['available_at'] for r in seen)
    choices = [r for r in seen if r['available_at'] == chosen_at]
    if len({str(r.get('value')) for r in choices}) > 1:
        return _r('O162', 'hole', {'value': None, 'vintage_history': history},
                  hole_ids=['HOLE:O162:vintage_order'], coverage_ok=None)
    chosen = choices[0]
    value = dec(chosen.get('value'))
    return _r("O162", "computed", {"value": value, "actual_value": value,
               "vintage_at": chosen_at, "available_at": chosen_at,
               "latest_available_vintage_at_decision": chosen.get('vintage_id'),
               "series_id": chosen.get('series_id', series), "reference_period": chosen.get('reference_period', period),
               "vintage_history": sorted(history, key=lambda r: r['available_at']),
               "availability_assumption": chosen['availability_assumption']}, known_at=chosen_at)


def _bars_5() -> list[dict]:
    return [{"complete": True, "start": _d(10, i)} for i in range(5)]


add_fixture({"id": "O001-F1", "recipe": "O001", "inputs": {"bars": _bars_5(), "trades": [{"side": "B", "size": 2}] * 5, "required_minutes": 5, "known_at": _d(10, 5), "use_at": _d(10, 6)}, "expected": {"price_coverage": True, "side_coverage": True, "coverage_ok": True}})
add_fixture({"id": "O001-F1a", "recipe": "O001", "inputs": {"bars": _bars_5(), "trades": [{"side": None, "size": 12}], "required_minutes": 5, "known_at": _d(10, 5), "use_at": _d(10, 6)}, "expected": {"price_coverage": True, "side_coverage": None, "coverage_ok": None}})
add_fixture({"id": "O001-F1b", "recipe": "O001", "inputs": {"bars": _bars_5(), "trades": [{"side": "B", "size": 2}] * 5, "required_minutes": 5, "known_at": _d(10, 5), "use_at": _d(10, 6)}, "expected": {"coverage_ok": True}})
add_fixture({"id": "O001-F1c", "recipe": "O001", "inputs": {"bars": _bars_5()[:4], "trades": [{"side": "B", "size": 1}] * 4, "required_minutes": 5, "known_at": _d(10, 4), "use_at": _d(10, 6)}, "expected": {"coverage_ok": False}})
add_fixture({"id": "O002-F1", "recipe": "O002", "inputs": {"lo": Decimal("100"), "hi": Decimal("101"), "q": Q, "bar": {"L": Decimal("100.50"), "H": Decimal("102"), "C": Decimal("101")}, "known_at": _d(10, 1), "use_at": _d(10, 2)}, "expected": {"price_overlap": True, "upper_excursion_points": Decimal("1"), "upper_excursion_ticks": Decimal("4"), "close_below_hi": False, "source_hold": None}})
add_fixture({"id": "O002-F1b", "recipe": "O002", "inputs": {"lo": Decimal("100"), "hi": Decimal("101"), "bar": {"L": Decimal("100.50"), "H": Decimal("102"), "C": Decimal("100.75")}, "known_at": _d(10, 1), "use_at": _d(10, 2)}, "expected": {"close_below_hi": True, "close_inside_strict": True}})
add_fixture({"id": "O003-F1", "recipe": "O003", "inputs": {"start_ns": _d(3, 0), "end_ns": _d(3, 30), "event_ns": _d(3, 15), "use_at": _d(3, 15), "known_at": _d(3, 30)}, "expected": {"clock_check": False}})
add_fixture({"id": "O003-F1b", "recipe": "O003", "inputs": {"start_ns": _d(3, 0), "end_ns": _d(3, 30), "event_ns": _d(3, 31), "use_at": _d(3, 31), "known_at": _d(3, 30)}, "expected": {"clock_check": True}})
add_fixture({"id": "O004-F1", "recipe": "O004", "inputs": {"members": [{"O": 100, "H": 102, "L": 99, "C": 101, "V": 10}, {"O": 101, "H": 103, "L": 100, "C": 102, "V": 20}], "end_ns": _d(10, 2), "known_at": _d(10, 2), "use_at": _d(10, 3)}, "expected": {"O": Decimal("100"), "H": Decimal("103"), "L": Decimal("99"), "C": Decimal("102"), "V": Decimal("30")}})
add_fixture({"id": "O004-F1b", "recipe": "O004", "inputs": {"members": [{"O": 100, "H": 102, "L": 99, "C": 101, "V": 10}], "kind": "native_range", "known_at": _d(10, 2), "use_at": _d(10, 3)}, "expected": {"native_source_compatible": None}})

_m69 = [{"start": _d(6, 0) + i * 60_000_000_000, "end": _d(6, 0) + (i + 1) * 60_000_000_000, "H": Decimal("120") if i == 0 else Decimal("110"), "L": Decimal("100"), "O": Decimal("110"), "C": Decimal("110"), "V": 1} for i in range(180)]
add_fixture({"id": "O005-F1", "recipe": "O005", "inputs": {"members": _m69, "start_ns": _d(6, 0), "end_ns": _d(9, 0), "use_at": _d(9, 0), "known_at": _d(9, 0)}, "expected": {"L": Decimal("100"), "H": Decimal("120"), "W": Decimal("20"), "range_frozen": True}})
add_fixture({"id": "O005-F1b", "recipe": "O005", "inputs": {"members": _m69 + [{"start": _d(9, 10), "end": _d(9, 11), "H": Decimal("130"), "L": Decimal("120"), "O": Decimal("120"), "C": Decimal("130"), "V": 1}], "start_ns": _d(6, 0), "end_ns": _d(9, 0), "use_at": _d(9, 11), "known_at": _d(9, 0)}, "expected": {"H": Decimal("120")}})
add_fixture({"id": "O005-F1c", "recipe": "O005", "inputs": {"members": _m69, "start_ns": _d(6, 0), "end_ns": _d(9, 0), "use_at": _d(8, 50), "known_at": _d(9, 0)}, "expected": {"range_frozen": False, "base_ok": False}})
add_fixture({"id": "O006-F1", "recipe": "O006", "inputs": {"start_ns": _d(3, 0), "end_ns": _d(3, 30), "L": 200, "H": 208, "clock_id": "03:00-03:30", "source_clock_verified": True, "known_at": _d(3, 30), "use_at": _d(3, 35)}, "expected": {"W": Decimal("8"), "source_clock_verified": True}})
add_fixture({"id": "O006-F1b", "recipe": "O006", "inputs": {"start_ns": _d(0, 0), "end_ns": _d(3, 0), "L": 200, "H": 220, "clock_id": "00:00-03:00", "source_clock_verified": False, "known_at": _d(3, 0), "use_at": _d(3, 35)}, "expected": {"source_clock_verified": False}})
add_fixture({"id": "O007-F1", "recipe": "O007", "inputs": {"L": 100, "H": 120, "price": 110, "parent_id": "r1", "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"q25": Decimal("105"), "eq": Decimal("110"), "q75": Decimal("115"), "at_eq": True, "strict_above_eq": False, "strict_below_eq": False}})
add_fixture({"id": "O007-F1b", "recipe": "O007", "inputs": {"L": Decimal("100"), "H": Decimal("100.25"), "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"eq": Decimal("100.125")}})
add_fixture({"id": "O008-F1", "recipe": "O008", "inputs": {"range_open_ref": 112, "range_low": 100, "first_print": 108, "path_events": [{"t": _d(10, 0), "price": 100}, {"t": _d(10, 10), "price": 112}], "known_at": _d(9, 0), "use_at": _d(10, 10)}, "expected": {"directed_path": True, "numeric_low_gt_open": False, "range_open_ref": Decimal("112")}})
add_fixture({"id": "O009-F1", "recipe": "O009", "inputs": {"W": 20, "P": 20000, "prior_W": 80, "q": Q, "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"price_percent": Decimal("0.10"), "width_ratio": Decimal("0.25"), "width_ticks": Decimal("80"), "extended_context": None}})
add_fixture({"id": "O010-F1", "recipe": "O010", "inputs": {"H": 120, "L": 100, "window_start": _d(9, 30), "window_end": _d(10, 30), "as_of": _d(10, 30), "window_complete": True, "events": [{"t": _d(9, 35), "price": 121}, {"t": _d(10, 10), "price": 99}], "known_at": _d(10, 30), "use_at": _d(10, 31)}, "expected": {"path": "both", "first_side": "high"}})
add_fixture({"id": "O010-F1b", "recipe": "O010", "inputs": {"H": 120, "L": 100, "window_start": _d(9, 30), "window_end": _d(10, 30), "as_of": _d(10, 0), "window_complete": False, "events": [{"t": _d(9, 35), "price": 121}, {"t": _d(10, 10), "price": 99}], "known_at": _d(10, 0), "use_at": _d(10, 0)}, "expected": {"path": "high_only_so_far"}})
add_fixture({"id": "O010-F1c", "recipe": "O010", "inputs": {"H": 120, "L": 100, "window_start": _d(9, 30), "window_end": _d(10, 30), "as_of": _d(10, 30), "window_complete": True, "bar": {"H": 121, "L": 99, "t": _d(9, 40)}, "events": [], "known_at": _d(10, 30), "use_at": _d(10, 31)}, "expected": {"path": "both", "first_side": None}})
add_fixture({"id": "O011-F1", "recipe": "O011", "inputs": {"H": 150, "L": 130, "end_ns": _d(9, 30), "window_id": "sires_overnight", "use_at": _d(9, 30), "known_at": _d(9, 30)}, "expected": {"on_width": Decimal("20")}})
add_fixture({"id": "O011-F1b", "recipe": "O011", "inputs": {"H": 150, "L": 130, "end_ns": _d(9, 30), "use_at": _d(9, 20), "known_at": _d(9, 30)}, "expected": {"final": False, "base_ok": False}})
add_fixture({"id": "O012-F1", "recipe": "O012", "inputs": {"reference_px": 110, "reference_known_at": et_ns(DAY - timedelta(days=1), 18, 0), "sweep_at": _d(2, 10), "decision_at": _d(9, 45), "consumption_scope": "overnight", "known_at": _d(2, 10), "use_at": _d(9, 45)}, "expected": {"purged_at": _d(2, 10), "purge_before_decision": True}})
add_fixture({"id": "O012-F1b", "recipe": "O012", "inputs": {"reference_px": 110, "reference_known_at": et_ns(DAY - timedelta(days=1), 18, 0), "sweep_at": _d(10, 0), "decision_at": _d(9, 45), "known_at": _d(10, 0), "use_at": _d(9, 45)}, "expected": {"purge_before_decision": False}})
add_fixture({"id": "O012-F1c", "recipe": "O012", "inputs": {"reference_px": 110, "reference_known_at": et_ns(DAY - timedelta(days=1), 18, 0), "sweep_at": _d(2, 10), "decision_at": _d(9, 45), "consumption_scope": "rth_only", "known_at": _d(2, 10), "use_at": _d(9, 45)}, "expected": {"active_before_use": True}})
add_fixture({"id": "O013-F1", "recipe": "O013", "inputs": {"open_px": 112, "prior_val": 100, "prior_vah": 110, "prior_range_l": 95, "prior_range_h": 115, "rvol_known_at": _d(9, 35), "use_at": _d(9, 31), "known_at": _d(9, 30)}, "expected": {"above_value": True, "inside_range": True, "rvol_available": False}})
add_fixture({"id": "O014-F1", "recipe": "O014", "inputs": {"L": 100, "H": 120, "price": 121, "known_at": _d(9, 0), "use_at": _d(9, 41)}, "expected": {"upper_0_1": Decimal("122"), "upper_0_2": Decimal("124"), "upper_0_3": Decimal("126"), "upper_0_5": Decimal("130"), "depth_w": Decimal("0.05")}})
add_fixture({"id": "O015-F1", "recipe": "O015", "inputs": {"L": 100, "H": 120, "parent_id": "outer", "known_at": _d(9, 0), "use_at": _d(10, 0)}, "expected": {"upper_band": [Decimal("146.60"), Decimal("153.20")], "lower_band": [Decimal("66.80"), Decimal("73.40")]}})
add_fixture({"id": "O015-F1b", "recipe": "O015", "inputs": {"L": 106, "H": 114, "parent_id": "inner", "known_at": _d(9, 0), "use_at": _d(10, 0)}, "expected": {"upper_band": [Decimal("124.64"), Decimal("127.28")]}})
add_fixture({"id": "O016-F1", "recipe": "O016", "inputs": {"outer_L": 100, "outer_H": 120, "inner_L": 106, "inner_H": 114, "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"outer_width": Decimal("20"), "inner_width": Decimal("8"), "ids_merged": False}})
add_fixture({"id": "O016-F1b", "recipe": "O016", "inputs": {"outer_L": 100, "outer_H": 120, "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"inner_width": None}})
add_fixture({"id": "O017-F1", "recipe": "O017", "inputs": {"average": [100, 120], "median": [102, 118], "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"average_mid": Decimal("110"), "median_lo": Decimal("102"), "median_hi": Decimal("118"), "min_average": None, "automatic_bands": None}})
add_fixture({"id": "O018-F1", "recipe": "O018", "inputs": {"ev_mid": 111, "eq": 110, "price": 110, "generic_envelope": 111, "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"touches_eq": True, "touches_ev": False, "automatic_ev": None}})
add_fixture({"id": "O018-F1b", "recipe": "O018", "inputs": {"eq": 110, "price": 110, "generic_envelope": 111, "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"ev_reference_known": None}})
add_fixture({"id": "O019-F1", "recipe": "O019", "inputs": {"lo": 100, "hi": 102, "anchor_at": _d(9, 0), "snapshot_known_at": _d(9, 2), "touch_at": _d(9, 45), "source_id": "z", "target_id": "ro", "known_at": _d(9, 2), "use_at": _d(9, 45)}, "expected": {"source_zone_known": True, "known_before_touch": True, "entry_at_anchor": False}})
add_fixture({"id": "O019-F1b", "recipe": "O019", "inputs": {"lo": 100, "hi": 102, "anchor_at": _d(9, 0), "known_at": _d(9, 0), "use_at": _d(9, 45)}, "expected": {"source_zone_known": None}})
add_fixture({"id": "O020-F1", "recipe": "O020", "inputs": {"prior_rth_h": 120, "prior_rth_l": 100, "eth_price": 121, "scope": "rth_only", "known_at": et_ns(DAY - timedelta(days=1), 16, 0), "use_at": _d(9, 40)}, "expected": {"eth_consumes_rth_objective": False}})
add_fixture({"id": "O021-F1", "recipe": "O021", "inputs": {"event_ns": _d(9, 45), "known_at": _d(9, 45), "use_at": _d(9, 45)}, "expected": {"source_time_window": True}})
add_fixture({"id": "O021-F1b", "recipe": "O021", "inputs": {"event_ns": _d(9, 55), "known_at": _d(9, 55), "use_at": _d(9, 55)}, "expected": {"source_time_window": False}})
add_fixture({"id": "O021-F1c", "recipe": "O021", "inputs": {"event_ns": _d(10, 7), "window_required": False, "known_at": _d(10, 7), "use_at": _d(10, 7)}, "expected": {"source_time_window": True, "applicability": "not_required"}})
add_fixture({"id": "O022-F1", "recipe": "O022", "inputs": {"label": "london_preferred", "recorded_at": _d(2, 0), "use_at": _d(3, 30), "known_at": _d(2, 0)}, "expected": {"source_clean": True, "selector_from_pnl": False}})
add_fixture({"id": "O022-F1b", "recipe": "O022", "inputs": {"label": "london_clean", "recorded_at": _d(12, 0), "use_at": _d(2, 0), "known_at": _d(12, 0)}, "expected": {"base_ok": False}})
add_fixture({"id": "O023-F1", "recipe": "O023", "inputs": {"accumulation": True, "distribution_at": _d(10, 15), "use_at": _d(9, 30), "known_at": _d(9, 0)}, "expected": {"distribution_available": False, "base_ok": False}})
add_fixture({"id": "O024-F1", "recipe": "O024", "inputs": {"attempts": [{"id": "A1", "end": _d(9, 41)}, {"id": "A2", "end": _d(9, 44)}, {"id": "A3", "end": _d(9, 48)}], "as_of": _d(9, 45), "prior_allocation": 4, "known_at": _d(9, 45), "use_at": _d(9, 45)}, "expected": {"attempt_count": 2, "max_continue_allocation": Decimal("2")}})
add_fixture({"id": "O024-F1b", "recipe": "O024", "inputs": {"attempts": [{"id": "A1", "end": _d(9, 41)}, {"id": "A2", "end": _d(9, 44)}, {"id": "A3", "end": _d(9, 48)}], "as_of": _d(9, 49), "known_at": _d(9, 49), "use_at": _d(9, 49)}, "expected": {"attempt_count": 3}})
add_fixture({"id": "O025-F1", "recipe": "O025", "inputs": {"or_h": 108, "or_l": 100, "or_end": _d(9, 45), "range_eq": 110, "known_at": _d(9, 45), "use_at": _d(9, 50)}, "expected": {"mid": Decimal("104"), "distinct_from_eq": True}})
add_fixture({"id": "O026-F1", "recipe": "O026", "inputs": {"low": 100, "high": 120, "low_confirmed_at": _d(9, 40), "high_confirmed_at": _d(9, 55), "touch_at": _d(9, 52), "known_at": _d(9, 55), "use_at": _d(9, 52)}, "expected": {"midpoint": Decimal("110"), "post_confirmation_retrace": False}})
add_fixture({"id": "O026-F1b", "recipe": "O026", "inputs": {"low": 100, "high": 120, "low_confirmed_at": _d(9, 40), "high_confirmed_at": _d(9, 55), "touch_at": _d(10, 0), "known_at": _d(9, 55), "use_at": _d(10, 0)}, "expected": {"post_confirmation_retrace": True}})
add_fixture({"id": "O027-F1", "recipe": "O027", "inputs": {"current_volume": 300, "baseline": 200, "window_end": _d(9, 35), "use_at": _d(9, 35), "known_at": _d(9, 35)}, "expected": {"rvol": Decimal("1.5"), "source_high_rvol": None}})
add_fixture({"id": "O027-F1b", "recipe": "O027", "inputs": {"current_volume": 300, "baseline": 200, "window_end": _d(9, 35), "use_at": _d(9, 31), "known_at": _d(9, 35)}, "expected": {"base_ok": False}})
add_fixture({"id": "O028-F1", "recipe": "O028", "inputs": {"a": Decimal("120.00"), "b": Decimal("120.00"), "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"exact_equality": True}})
add_fixture({"id": "O028-F1b", "recipe": "O028", "inputs": {"a": Decimal("120.00"), "b": Decimal("120.25"), "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"exact_equality": False, "near_equal": None}})
add_fixture({"id": "O029-F1", "recipe": "O029", "inputs": {"schedule_known_at": et_ns(DAY - timedelta(days=1), 12, 0), "release_known_at": _d(8, 30) + 2_000_000_000, "as_of": _d(8, 30) + 1_000_000_000, "known_at": _d(8, 30), "use_at": _d(8, 30) + 1_000_000_000}, "expected": {"schedule_known": True, "release_known": False}})
add_fixture({"id": "O047-F1", "recipe": "O047", "inputs": {"reference_px": 110, "side": "short", "sweep_px": 111, "sweep_at": _d(10, 1), "confirm_close": 109, "confirm_at": _d(10, 5), "decision_at": _d(10, 6), "reference_known_at": _d(10, 0), "known_at": _d(10, 5), "use_at": _d(10, 6)}, "expected": {"failure_confirmed": True}})
add_fixture({"id": "O047-F1b", "recipe": "O047", "inputs": {"reference_px": 110, "side": "short", "sweep_px": 111, "sweep_at": _d(10, 1), "confirm_close": 111, "confirm_at": _d(10, 5), "decision_at": _d(10, 6), "reference_known_at": _d(10, 0), "known_at": _d(10, 5), "use_at": _d(10, 6)}, "expected": {"failure_confirmed": False}})
add_fixture({"id": "O047-F1c", "recipe": "O047", "inputs": {"reference_px": 110, "side": "short", "sweep_px": 111, "sweep_at": _d(10, 1), "confirm_close": 110, "confirm_at": _d(10, 5), "decision_at": _d(10, 6), "reference_known_at": _d(10, 0), "known_at": _d(10, 5), "use_at": _d(10, 6)}, "expected": {"failure_confirmed": False}})
add_fixture({"id": "O047-F1d", "recipe": "O047", "inputs": {"reference_px": 110, "side": "short", "sweep_px": 111, "sweep_at": _d(10, 1), "confirm_close": 109, "confirm_at": _d(10, 5), "decision_at": _d(10, 4), "reference_known_at": _d(10, 0), "known_at": _d(10, 5), "use_at": _d(10, 4)}, "expected": {"base_ok": False}})
add_fixture({"id": "O048-F1", "recipe": "O048", "inputs": {"pdh": 110, "pdl": 100, "pwh": 120, "pwl": 90, "price": 115, "weekly_convention": "previous_week_candle", "need_week": True, "known_at": _d(9, 30), "use_at": _d(10, 0)}, "expected": {"sweeps_daily_high": True, "sweeps_weekly_high": False}})
add_fixture({"id": "O048-F1b", "recipe": "O048", "inputs": {"pdh": 110, "need_week": True, "known_at": _d(9, 30), "use_at": _d(10, 0)}, "expected": {"weekly": None}})
add_fixture({"id": "O050-F1", "recipe": "O050", "inputs": {"open_px": 100, "open_at": _d(9, 30), "events": [{"t": _d(9, 32), "price": 99}, {"t": _d(9, 34), "price": 101}], "known_at": _d(9, 30), "use_at": _d(9, 34)}, "expected": {"below_then_above": True, "source_confirmation": None}})
add_fixture({"id": "O055-F1", "recipe": "O055", "inputs": {"gap": [100, 104], "fill_at": _d(10, 15), "as_of": _d(10, 14), "touch_px": 101, "known_at": _d(9, 40), "use_at": _d(10, 14)}, "expected": {"filled": False, "partial_contact": True}})
add_fixture({"id": "O056-F1", "recipe": "O056", "inputs": {"c1_l": 101, "c2": {"O": 102, "H": 104, "L": 100, "C": 103}, "c3_close": 105, "c3_known_at": _d(9, 43), "decision_at": _d(9, 44), "known_at": _d(9, 43), "use_at": _d(9, 44)}, "expected": {"ob": [Decimal("100"), Decimal("104")], "mid": Decimal("102"), "confirmed": True}})
add_fixture({"id": "O056-F1b", "recipe": "O056", "inputs": {"c1_l": 101, "c2": {"O": 102, "H": 104, "L": 100, "C": 103}, "c3_close": 103, "c3_known_at": _d(9, 43), "decision_at": _d(9, 44), "known_at": _d(9, 43), "use_at": _d(9, 44)}, "expected": {"confirmed": False}})
add_fixture({"id": "O057-F1", "recipe": "O057", "inputs": {"O": 102, "C": 103, "H": 104, "L": 100, "known_at": _d(9, 43), "use_at": _d(9, 44)}, "expected": {"lower_wick": [Decimal("100"), Decimal("102")], "lower_width": Decimal("2"), "upper_wick": [Decimal("103"), Decimal("104")], "upper_width": Decimal("1")}})
add_fixture({"id": "O058-F1", "recipe": "O058", "inputs": {"O": 100, "C": 102, "H": 110, "L": 100, "V": 200, "prior_volumes": [100] * 14, "known_at": _d(9, 43), "use_at": _d(9, 44)}, "expected": {"body_ratio": Decimal("0.2"), "volume_average": Decimal("100"), "volume_ratio": Decimal("2"), "displayed_small_body_high_volume": True}})
add_fixture({"id": "O061-F1", "recipe": "O061", "inputs": {"trades": [{"price": 100, "size": 2}, {"price": Decimal("100.25"), "size": 3}, {"price": 100, "size": 1}], "q": Q, "native": True, "source_binning": "native", "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"total": Decimal("6")}})
add_fixture({"id": "O061-F1b", "recipe": "O061", "inputs": {"trades": [{"price": 100, "size": 50, "is_quote": True}], "native": True, "source_binning": "native", "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"total": Decimal("0")}})
add_fixture({"id": "O062-F1", "recipe": "O062", "inputs": {"total": 100, "covered": 68, "required_fraction": Decimal("0.68"), "construction": "saint_68", "known_at": _d(16, 0), "use_at": _d(16, 1)}, "expected": {"achieved_fraction": Decimal("0.68"), "meets_required": True}})
add_fixture({"id": "O063-F1", "recipe": "O063", "inputs": {"snapshots": [{"known_at": _d(10, 0), "poc": 100}, {"known_at": _d(10, 30), "poc": 101}], "as_of": _d(10, 5), "known_at": _d(10, 0), "use_at": _d(10, 5)}, "expected": {"poc": 100}})
add_fixture({"id": "O064-F1", "recipe": "O064", "inputs": {"bins": {"100": 4, "101": 10, "102": 6}, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"poc": Decimal("101"), "max": Decimal("10"), "mid_is_poc_formula": False}})
add_fixture({"id": "O064-F1b", "recipe": "O064", "inputs": {"bins": {"100": 4, "101": 10, "102": 10}, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"poc": None, "tied": True}})
add_fixture({"id": "O066-F1", "recipe": "O066", "inputs": {"node": [100, 102], "volumes": [4, 10, 6], "peak": 101, "reaction": [Decimal("100.5"), Decimal("101.5")], "known_at": _d(9, 30), "use_at": _d(9, 45)}, "expected": {"volume": Decimal("20"), "overlap": [Decimal("100.5"), Decimal("101.5")]}})
add_fixture({"id": "O067-F1", "recipe": "O067", "inputs": {"accepted_a": True, "accepted_b": True, "bridge_volumes": [2, 1, 2], "trough": 102, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"bridge_volume": Decimal("5"), "trough": 102}})
add_fixture({"id": "O068-F1", "recipe": "O068", "inputs": {"shelf": [100, 102], "shelf_volumes": [8, 8, 7], "transition_volumes": [3, 1], "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"shelf_volume": Decimal("23"), "transition_volume": Decimal("4"), "ratio_defines_ledge": False}})
add_fixture({"id": "O069-F1", "recipe": "O069", "inputs": {"ledge_px": 102, "retest_px": 102, "dev_vah": 103, "known_at": _d(9, 50), "use_at": _d(10, 5)}, "expected": {"same_id": True, "vah_touch_is_retest": False}})
add_fixture({"id": "O073-F1", "recipe": "O073", "inputs": {"lvn": [100, 101], "older_poc": Decimal("100.5"), "rth_poc": 103, "hold_known_at": _d(9, 31), "use_at": _d(9, 30), "known_at": _d(9, 30)}, "expected": {"base_ok": False}})
add_fixture({"id": "O075-F1", "recipe": "O075", "inputs": {"open_px": 103, "balance": [100, 120], "va": [105, 115], "condition_unresolved": True, "known_at": _d(9, 30), "use_at": _d(9, 31)}, "expected": {"inside_balance": True, "inside_va": False, "cohort_eligibility": None}})
add_fixture({"id": "O077-F1", "recipe": "O077", "inputs": {"levels": [{"B": 7, "A": 4}, {"B": 2, "A": 5}], "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"known_delta": Decimal("0"), "total": Decimal("18")}})
add_fixture({"id": "O077-F1b", "recipe": "O077", "inputs": {"levels": [{"B": 7, "A": 4}, {"B": 2, "A": 5, "N": 2}], "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"known_delta": None, "delta_interval": [Decimal("-2"), Decimal("2")]}})
add_fixture({"id": "O086-F1", "recipe": "O086", "inputs": {"prior_high": 110, "prior_close": 105, "open_px": 114, "price": 112, "known_at": _d(9, 30), "use_at": _d(9, 31)}, "expected": {"half_session_gap": Decimal("112"), "half_close_gap": Decimal("109.5"), "touches_half_session": True, "fill_to_high": False}})
add_fixture({"id": "O087-F1", "recipe": "O087", "inputs": {"objective_px": 120, "scope": "rth_only", "eth_hit": _d(2, 0), "rth_hit": _d(10, 0), "decision_at": _d(9, 40), "known_at": et_ns(DAY - timedelta(days=1), 16, 0), "use_at": _d(9, 40)}, "expected": {"active": True, "consumed_after_entry": True}})
add_fixture({"id": "O088-F1", "recipe": "O088", "inputs": {"n": 10, "onh": 6, "onl": 5, "both": 3, "eth_h": 120, "eth_l": 100, "known_at": _d(16, 0), "use_at": _d(16, 1)}, "expected": {"either": 8, "either_rate": Decimal("0.8"), "both_rate": Decimal("0.3"), "mpoc": Decimal("110")}})
add_fixture({"id": "O098-F1", "recipe": "O098", "inputs": {"events": [
    {"side": "A", "size": 2, "action": "T"}, {"side": "B", "size": 1, "action": "T"},
    {"side": "B", "size": 3, "action": "T"}, {"side": "B", "size": 1, "action": "T"},
    {"side": "B", "size": 1, "action": "T"}, {"side": "A", "size": 1, "action": "T"},
    {"side": "A", "size": 1, "action": "T"}, {"side": "B", "size": 1, "action": "T"},
], "known_at": 1, "use_at": 2}, "expected": {"buy": 7, "sell": 4, "total": 11, "delta": 3}})
add_fixture({"id": "O098-F1b", "recipe": "O098", "inputs": {"events": [
    {"side": "A", "size": 2, "action": "T"}, {"side": "B", "size": 1, "action": "T"},
    {"side": "B", "size": 3, "action": "T"}, {"side": "B", "size": 1, "action": "T"},
    {"side": "B", "size": 1, "action": "T"}, {"side": "A", "size": 1, "action": "T"},
    {"side": "A", "size": 1, "action": "T"}, {"side": "B", "size": 1, "action": "T"},
    {"side": "N", "size": 2, "action": "T"},
], "known_at": 1, "use_at": 2}, "expected": {"total": 13, "delta": None, "delta_interval": [1, 5]}})
add_fixture({"id": "O098-F1c", "recipe": "O098", "inputs": {"events": [{"side": "A", "size": 100, "action": "C"}], "known_at": 1, "use_at": 2}, "expected": {"total": 0}})
add_fixture({"id": "O099-F1", "recipe": "O099", "inputs": {"trades": [{"size": 60}, {"size": 60}], "threshold": 100, "mode": "per_print", "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"markers": 0}})
add_fixture({"id": "O099-F1b", "recipe": "O099", "inputs": {"trades": [{"size": 100}], "threshold": 100, "mode": "per_print", "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"markers": 1}})
add_fixture({"id": "O101-F1", "recipe": "O101", "inputs": {"effort_size": 100, "progress": Decimal("0.25"), "later_decline": 2, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"absorption": None, "later_decline_repairs": False}})
add_fixture({"id": "O107-F1", "recipe": "O107", "inputs": {"B": 80, "A": 20, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"delta": Decimal("60"), "total": Decimal("100"), "fraction": Decimal("0.6"), "source_spike": None}})
add_fixture({"id": "O120-F1", "recipe": "O120", "inputs": {"O": 100, "C": 101, "H": 102, "L": 99, "body_rows": [{"B": 3, "A": 8}], "as_of_c": 100, "later_price": 101, "known_at": _d(10, 5), "use_at": _d(10, 6)}, "expected": {"body_prices": [Decimal("100"), Decimal("101")], "wick_low": Decimal("99"), "wick_high": Decimal("102"), "body_delta": Decimal("-5"), "later_price_in_earlier_asof": False}})
add_fixture({"id": "O139-F1", "recipe": "O139", "inputs": {"entry": 105, "stop": 100, "side": "long", "q": Q, "intrabar_low": 99, "close_below": 100, "known_at": _d(9, 44), "use_at": _d(9, 44)}, "expected": {"risk_points": Decimal("5"), "risk_ticks": Decimal("20"), "valid_initial_stop": True, "wick_breaches_close_policy": False}})
add_fixture({"id": "O139-F1b", "recipe": "O139", "inputs": {"entry": 105, "stop": 110, "side": "short", "q": Q, "known_at": _d(9, 44), "use_at": _d(9, 44)}, "expected": {"risk_points": Decimal("5"), "risk_ticks": Decimal("20")}})
add_fixture({"id": "O139-F1c", "recipe": "O139", "inputs": {"entry": 105, "stop": 106, "side": "long", "q": Q, "known_at": _d(9, 44), "use_at": _d(9, 44)}, "expected": {"valid_initial_stop": False}})
add_fixture({"id": "O140-F1", "recipe": "O140", "inputs": {"D": 2, "M": 10, "quantity": 3, "cap": 50, "integer_max": True, "known_at": _d(9, 44), "use_at": _d(9, 44)}, "expected": {"unit_risk": Decimal("20"), "position_risk": Decimal("60"), "cap_ok": False, "integer_max_contracts": 2}})
add_fixture({"id": "O141-F1", "recipe": "O141", "inputs": {"entry": 100, "target": 104, "selected_at": _d(9, 40), "decision_at": _d(9, 41), "prints": [{"t": _d(9, 39), "price": 104}, {"t": _d(10, 0), "price": 104}], "known_at": _d(9, 40), "use_at": _d(9, 41)}, "expected": {"distance": Decimal("4"), "pre_entry_print_counts": False, "post_entry_hit": True}})
add_fixture({"id": "O142-F1", "recipe": "O142", "inputs": {"position": 3, "entry_at": _d(9, 40), "fills": [{"qty": 1, "t": _d(9, 50)}], "protected_at": _d(10, 0), "trail_at": _d(9, 55), "known_at": _d(9, 50), "use_at": _d(9, 55)}, "expected": {"remaining": Decimal("2"), "trail_supported": False}})
add_fixture({"id": "O145-F1", "recipe": "O145", "inputs": {"results_r": [-1, -1, -2], "limit_r": -4, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"sum_r": Decimal("-4"), "entry_permission": False}})
add_fixture({"id": "O145-F1b", "recipe": "O145", "inputs": {"results_r": [Decimal("-3.5")], "limit_r": -4, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"entry_permission": True}})
add_fixture({"id": "O150-F1", "recipe": "O150", "inputs": {"limit": 100, "q": Q, "side": "long", "stop_ticks": 32, "target_ticks": 96, "placed_at": _d(10, 0), "cancel_minutes": 30, "quantity": 3, "fill_qtys": [1, 1], "known_at": _d(10, 0), "use_at": _d(10, 0)}, "expected": {"stop": Decimal("92"), "target": Decimal("124"), "cancel_at": _d(10, 30), "filled": Decimal("2"), "remaining": Decimal("1")}})
add_fixture({"id": "O162-F1", "recipe": "O162", "inputs": {"releases": [
    {"at": et_ns(date(2026, 4, 1), 8, 30), "value": Decimal("2.0")},
    {"at": et_ns(date(2026, 5, 1), 8, 30), "value": Decimal("1.5")},
], "as_of": et_ns(date(2026, 4, 15), 10, 0), "known_at": et_ns(date(2026, 4, 1), 8, 30), "use_at": et_ns(date(2026, 4, 15), 10, 0)}, "expected": {"value": Decimal("2.0")}})
add_fixture({"id": "O162-F1b", "recipe": "O162", "inputs": {"releases": [
    {"at": et_ns(date(2026, 4, 1), 8, 30), "value": Decimal("2.0")},
    {"at": et_ns(date(2026, 5, 1), 8, 30), "value": Decimal("1.5")},
], "vintage_policy": "latest_available", "as_of": et_ns(date(2026, 5, 2), 10, 0), "known_at": et_ns(date(2026, 5, 1), 8, 30), "use_at": et_ns(date(2026, 5, 2), 10, 0)}, "expected": {"value": Decimal("1.5")}})
