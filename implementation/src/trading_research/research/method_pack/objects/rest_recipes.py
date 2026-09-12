"""Remaining FORMULAS object recipes and printed F1 cases."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from trading_research.research.method_pack.adapters import signed_size
from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.logic import dec
from trading_research.research.method_pack.protocol import RecipeResult, add_fixture, register

DAY = date(2026, 1, 15)
YDAY = date(2026, 1, 14)
NEXT = date(2026, 1, 16)
Q = Decimal("0.25")


def _d(*clock):
    return et_ns(DAY, *clock)


def _yd(*clock):
    return et_ns(YDAY, *clock)


def _n(*clock):
    return et_ns(NEXT, *clock)


def _r(rid, state, value, **kwargs):
    return RecipeResult(rid, state, value, **kwargs)


def _ordered(*times):
    prev = None
    for t in times:
        if t is None:
            return None
        if prev is not None and t < prev:
            return False
        prev = t
    return True


def _vwap(trades, as_of=None, start=None):
    sum_v = Decimal(0)
    sum_pv = Decimal(0)
    for tr in trades:
        if tr.get("is_quote"):
            continue
        t = tr.get("t")
        if start is not None and t is not None and t < start:
            continue
        if as_of is not None and t is not None and t > as_of:
            continue
        v, p = dec(tr["size"]), dec(tr["price"])
        sum_v += v
        sum_pv += p * v
    return sum_v, sum_pv, (None if sum_v == 0 else sum_pv / sum_v)


@register("O031", ("trades", "anchor_known_at"))
def o031(inp: dict) -> RecipeResult:
    confirm = inp["anchor_known_at"]
    use_at = inp.get("use_at")
    if use_at is not None and confirm > use_at:
        return _r("O031", "invalid", {"avwap": None, "usable": False}, base_ok=False, reason="causal")
    sum_v, sum_pv, avwap = _vwap(inp["trades"], as_of=inp.get("as_of"), start=inp.get("anchor_price_at"))
    return _r("O031", "computed", {
        "avwap": avwap, "sum_v": sum_v, "sum_pv": sum_pv,
        "usable_at": confirm, "usable": True,
        "anchor_id": inp.get("anchor_id"),
        "anchor_known_at": confirm,
    }, known_at=confirm)


@register("O032", ("mu",))
def o032(inp: dict) -> RecipeResult:
    mu = dec(inp["mu"])
    sigma = dec(inp.get("sigma"))
    k = dec(inp.get("k"))
    if sigma is None or inp.get("variance_convention") is None or k is None:
        return _r("O032", "hole", {
            "upper": None, "lower": None, "band": None,
            "automatic_sigma": None, "faithful_band": None, "fade": False,
        }, hole_ids=["HOLE:O032:sigma"], coverage_ok=None)
    if sigma < 0:
        return _r("O032", "invalid", {"upper": None, "lower": None, "band": None,
            "automatic_sigma": None, "faithful_band": None, "fade": False},
            hole_ids=["HOLE:O032:sigma"], base_ok=False, reason="negative sigma")
    upper = mu + k * sigma
    lower = mu - k * sigma
    px = dec(inp.get("price"))
    touch_upper = None if px is None else px == upper
    return _r("O032", "computed", {
        "upper": upper, "lower": lower, "band": [lower, upper],
        "touch_upper": touch_upper, "fade": False, "faithful_band": True,
    }, known_at=inp.get("known_at"))


@register("O033", ("source_regime",))
def o033(inp: dict) -> RecipeResult:
    regime = inp.get("source_regime")
    if regime is None:
        return _r("O033", "hole", {
            "source_regime": None, "aggressive_ofm_ok": None, "balance_fade_ok": None,
            "automatic_regime": None,
        }, hole_ids=["HOLE:O033:engine"], coverage_ok=None)
    if regime == "uncertain":
        ofm = fade = None
    elif regime == "long_gamma":
        ofm, fade = False, True
    elif regime == "short_gamma":
        ofm, fade = True, False
    else:
        ofm = fade = None
    return _r("O033", "supplied", {
        "source_regime": regime,
        "aggressive_ofm_ok": ofm,
        "balance_fade_ok": fade,
        "automatic_regime": None,
        "other_gates_still_required": True,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O033:engine"])


@register("O034", ("symbol", "expiry", "observation_date"))
def o034(inp: dict) -> RecipeResult:
    is_0dte = inp["expiry"] == inp["observation_date"]
    mapped = dec(inp.get("mapping"))
    expected = inp.get("source_product")
    product_ok = None if expected is None else inp["symbol"] == expected
    return _r("O034", "computed", {
        "is_0dte": is_0dte,
        "native_strike": dec(inp.get("strike")),
        "symbol": inp["symbol"],
        "mapped_price": mapped,
        "source_product_ok": product_ok,
    }, known_at=inp.get("known_at"))


@register("O035", ("spot",))
def o035(inp: dict) -> RecipeResult:
    flip = dec(inp.get("flip"))
    spot = dec(inp.get("spot"))
    if flip is None:
        return _r("O035", "hole", {
            "flip_value": None, "spot_minus_flip": None, "relation": None,
            "automatic_flip": None,
        }, hole_ids=["HOLE:O035:engine"], coverage_ok=None)
    diff = None if spot is None else spot - flip
    if diff is None:
        rel = None
    elif diff > 0:
        rel = "above"
    elif diff < 0:
        rel = "below"
    else:
        rel = "on"
    interp = inp.get("source_regime_interpretation")
    return _r("O035", "supplied", {
        "flip_value": flip, "spot_minus_flip": diff, "relation": rel,
        "source_regime_interpretation": interp,
        "automatic_flip": None,
        "regime_from_difference": False,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O035:engine"])


@register("O036", ("walls",))
def o036(inp: dict) -> RecipeResult:
    walls = inp.get("walls") or []
    if not walls:
        return _r("O036", "hole", {"automatic_walls": None, "walls": []}, hole_ids=["HOLE:O036:engine"], coverage_ok=None)
    spot = dec(inp.get("spot"))
    out = []
    for w in walls:
        px = dec(w["price"])
        rel = None if spot is None else ("below" if spot < px else ("above" if spot > px else "on"))
        out.append({"id": w.get("id"), "rank": w.get("rank"), "price": px, "spot_relation": rel, "kind": w.get("kind")})
    ids = [w.get("id") for w in walls]
    pain_id = inp.get("max_pain_id")
    all_ids = ids + ([pain_id] if pain_id else [])
    if any(item is None for item in ids) or len(ids) != len(set(ids)):
        return _r("O036", "invalid", {"walls": out, "wall_ids": ids,
            "max_pain_id": pain_id, "distinct_ids": len(set(all_ids)),
            "automatic_walls": None}, hole_ids=["HOLE:O036:identity"],
            base_ok=False, reason="wall identity is missing or duplicated")
    return _r("O036", "supplied", {
        "walls": out,
        "wall_ids": ids,
        "max_pain_id": pain_id,
        "distinct_ids": len(set(all_ids)),
        "automatic_walls": None,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O036:engine"])


@register("O037", ("put_wall",))
def o037(inp: dict) -> RecipeResult:
    mp = dec(inp.get("max_pain"))
    if mp is None:
        return _r("O037", "hole", {
            "max_pain_value": None, "difference": None, "automatic_max_pain": None,
        }, hole_ids=["HOLE:O037:engine"], coverage_ok=None)
    wall = dec(inp.get("put_wall"))
    diff = None if wall is None else abs(mp - wall)
    return _r("O037", "supplied", {
        "max_pain_value": mp,
        "difference": diff,
        "equal_put_wall": None if wall is None else mp == wall,
        "automatic_max_pain": None,
        "predicted_terminal": None,
        "identity": inp.get("max_pain_id"),
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O037:engine"])


@register("O038", ("computed_vol",))
def o038(inp: dict) -> RecipeResult:
    val = dec(inp.get("source_value"))
    if val is None or not inp.get("unit"):
        missing = "source_value" if val is None else "unit"
        return _r("O038", "hole", {"source_value": None, "automatic_value": None}, hole_ids=["HOLE:O038:engine"], coverage_ok=None)
    computed = dec(inp.get("computed_vol"))
    return _r("O038", "supplied", {
        "source_value": val,
        "unit": inp.get("unit"),
        "computed_is_not_source": computed is None or computed != val,
        "automatic_value": None,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O038:engine"])


@register("O039", ("computed",))
def o039(inp: dict) -> RecipeResult:
    val = dec(inp.get("source_vol_gex"))
    if val is None or not inp.get("unit"):
        return _r("O039", "hole", {"source_vol_gex": None, "automatic_value": None, "faithful_value": None}, hole_ids=["HOLE:O039:engine"], coverage_ok=None)
    return _r("O039", "supplied", {
        "source_vol_gex": val,
        "unit": inp.get("unit"),
        "automatic_value": None,
        "faithful_value": val,
        "computed_comparison": dec(inp.get("computed")),
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O039:engine"])


@register("O040", ("gauge", "scale"))
def o040(inp: dict) -> RecipeResult:
    gauge = dec(inp.get("gauge"))
    scale = inp.get("scale")
    if gauge is None:
        return _r("O040", "hole", {"gauge_value": None, "automatic_pressure": None}, hole_ids=["HOLE:O040:engine"], coverage_ok=None)
    if scale is None:
        return _r("O040", "hole", {"gauge_value": gauge, "scale": None,
            "as_percent": None, "source_interpretation": None,
            "automatic_pressure": None, "entry_permission": None},
            hole_ids=["HOLE:O040:scale"], coverage_ok=None)
    interp = None if scale is None else inp.get("source_interpretation")
    pct = None
    if scale == "percent":
        pct = gauge
    return _r("O040", "supplied", {
        "gauge_value": gauge,
        "scale": scale,
        "as_percent": pct,
        "source_interpretation": interp,
        "automatic_pressure": None,
        "entry_permission": None,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O040:engine"])


@register("O041", ("kg1", "kg1_id", "reaction_id"))
def o041(inp: dict) -> RecipeResult:
    kg1 = inp.get("kg1")
    if kg1 is None or not inp.get("kg1_id") or inp.get("known_at") is None:
        return _r("O041", "hole", {"automatic_kg1": None, "ids": []}, hole_ids=["HOLE:O041:engine"], coverage_ok=None)
    ids = [i for i in (inp.get("kg1_id"), inp.get("hvn_id"), inp.get("reaction_id")) if i]
    reasons = [i for i in (inp.get("kg1_id"), inp.get("hvn_id")) if i]
    return _r("O041", "supplied", {
        "kg1": [dec(kg1[0]), dec(kg1[1])] if isinstance(kg1, (list, tuple)) else kg1,
        "ids": ids,
        "id_count": len(ids),
        "two_reason_ok": len(reasons) >= 2,
        "automatic_kg1": None,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O041:engine"])


@register("O042", ("vix",))
def o042(inp: dict) -> RecipeResult:
    pub_at = inp.get("publication_at")
    use_at = inp.get("use_at")
    vix = dec(inp.get("vix"))
    later_at = inp.get("later_at")
    if pub_at is None:
        return _r("O042", "hole", {"usable_vix": None, "faithful_preopen": None}, hole_ids=["HOLE:O042:publication"], coverage_ok=None)
    usable = vix if use_at is None or pub_at <= use_at else None
    later_ok = later_at is not None and use_at is not None and later_at <= use_at
    return _r("O042", "computed", {
        "usable_vix": usable,
        "later_available": later_ok,
        "later_vix_used": False,
        "faithful_preopen": True,
    }, known_at=pub_at)


@register("O043", ("vix",))
def o043(inp: dict) -> RecipeResult:
    vix = dec(inp["vix"])
    pct = vix / Decimal(252).sqrt()
    p = dec(inp.get("P"))
    points = None if p is None else pct * p / Decimal(100)
    return _r("O043", "computed", {
        "percent": pct,
        "point_estimate": points,
        "must_travel": False,
    }, known_at=inp.get("known_at"))


@register("O044", ("near", "far"))
def o044(inp: dict) -> RecipeResult:
    near, far = dec(inp["near"]), dec(inp["far"])
    diff = far - near
    ratio = far / near if near else None
    post = dec(inp.get("post_near"))
    post_at = inp.get("post_at")
    use_at = inp.get("use_at")
    post_ok = post_at is not None and (use_at is None or post_at <= use_at)
    change = None if post is None or not post_ok else post - near
    return _r("O044", "computed", {
        "difference": diff,
        "far_over_near": ratio,
        "post_available": post_ok,
        "change": change,
        "interpretation": None,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O044:interpretation"])


@register("O045", ("vvix", "available_at"))
def o045(inp: dict) -> RecipeResult:
    avail = inp.get("available_at")
    use_at = inp.get("use_at")
    vvix = dec(inp.get("vvix"))
    if vvix is None:
        return _r("O045", "hole", {"vvix": None, "entry_permission": None}, hole_ids=["HOLE:O045:observation"], coverage_ok=None)
    if avail is not None and use_at is not None and avail > use_at:
        return _r("O045", "invalid", {"vvix": None, "usable": False, "entry_permission": None}, base_ok=False, reason="causal")
    return _r("O045", "computed", {
        "vvix": vvix,
        "usable": True,
        "entry_permission": None,
    }, known_at=avail or inp.get("known_at"))


@register("O060", ("lo", "hi"))
def o060(inp: dict) -> RecipeResult:
    lo, hi = dec(inp["lo"]), dec(inp["hi"])
    if lo > hi:
        return _r("O060", "invalid", {"band": [lo, hi], "width": None,
            "inside": None, "edge_fade": False, "automatic_selector": None},
            base_ok=False, reason="lower bound exceeds upper bound")
    declared = inp.get("declared_at")
    use_at = inp.get("use_at")
    if declared is not None and use_at is not None and declared > use_at:
        return _r("O060", "invalid", {"inside": None, "automatic_selector": None}, base_ok=False, reason="causal")
    px = dec(inp.get("price"))
    inside = None if px is None else lo <= px <= hi
    return _r("O060", "supplied", {
        "band": [lo, hi],
        "width": hi - lo,
        "inside": inside,
        "edge_fade": False,
        "automatic_selector": None,
    }, known_at=declared or inp.get("known_at"), hole_ids=["HOLE:O060:selector"])


@register("O065", ("poc",))
def o065(inp: dict) -> RecipeResult:
    as_of = inp.get("as_of")
    if inp.get("coverage_complete") is False and inp.get("overnight_visits_count", True):
        return _r("O065", "hole", {"untested": None}, hole_ids=["HOLE:O065:coverage"], coverage_ok=None)
    visits = inp.get("visits") or []
    poc = dec(inp["poc"])
    hit = any((as_of is None or v["t"] <= as_of) and dec(v["price"]) == poc for v in visits)
    return _r("O065", "computed", {"untested": not hit, "poc": poc}, known_at=inp.get("known_at"))


@register("O070", ("profiles",))
def o070(inp: dict) -> RecipeResult:
    if inp.get("overlap"):
        return _r("O070", "hole", {"total": None, "composite": None, "automatic_window_selection": None}, hole_ids=["HOLE:O070:overlap"], coverage_ok=None)
    composite = {}
    for p in inp["profiles"]:
        for k, v in p.items():
            key = str(dec(k) if str(k).replace(".", "", 1).isdigit() else k)
            composite[key] = composite.get(key, Decimal(0)) + dec(v)
    total = sum(composite.values(), Decimal(0))
    return _r("O070", "computed", {
        "composite": composite,
        "total": total,
        "automatic_window_selection": None,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O070:selector"])


@register("O071", ("lo", "hi"))
def o071(inp: dict) -> RecipeResult:
    lo, hi = dec(inp["lo"]), dec(inp["hi"])
    if lo > hi:
        return _r("O071", "invalid", {"dealing_band": [lo, hi], "width": None,
            "inside": None}, base_ok=False, reason="lower bound exceeds upper bound")
    selected = inp.get("selected_at")
    use_at = inp.get("use_at")
    if selected is not None and use_at is not None and selected > use_at:
        return _r("O071", "invalid", {"inside": None}, base_ok=False, reason="causal")
    px = dec(inp.get("price"))
    ctrl = dec(inp.get("controlling_low", lo))
    return _r("O071", "supplied", {
        "dealing_band": [lo, hi],
        "width": hi - lo,
        "controlling_reference": ctrl,
        "inside": None if px is None else lo <= px <= hi,
        "band_known_before_use": None if selected is None or use_at is None else selected <= use_at,
    }, known_at=selected or inp.get("known_at"))


@register("O072", ("lo", "hi"))
def o072(inp: dict) -> RecipeResult:
    lo, hi = dec(inp["lo"]), dec(inp["hi"])
    if lo > hi:
        return _r("O072", "invalid", {"band": [lo, hi], "prior_defense_known": False},
                  base_ok=False, reason="reaction band lower bound exceeds upper bound")
    def_at = inp.get("defended_at")
    def_known = inp.get("defense_known_at", def_at)
    contact = inp.get("contact_at")
    use_at = inp.get("use_at")
    band_id = inp.get("band_id")
    other = inp.get("other_band_id")
    if other and band_id and other != band_id:
        inherit = False
    else:
        inherit = True
    known = def_known is not None and (use_at is None or def_known <= use_at)
    fresh = inp.get("fresh_defense_at")
    fresh_ok = fresh is not None and (use_at is None or fresh <= use_at)
    return _r("O072", "supplied", {
        "band": [lo, hi],
        "prior_defense_known": known and inherit,
        "fresh_available": fresh_ok,
        "inherit_other_band": False if other and other != band_id else None,
        "contact_at": contact,
    }, known_at=def_known or inp.get("known_at"))


@register("O074", ("known_at",))
def o074(inp: dict) -> RecipeResult:
    label = inp.get("inventory")
    if label is None:
        return _r("O074", "hole", {"inventory": None, "automatic_inventory": None}, hole_ids=["HOLE:O074:classifier"], coverage_ok=None)
    later = inp.get("later_response")
    return _r("O074", "supplied", {
        "inventory": label,
        "shelf": dec(inp.get("shelf")),
        "later_response": later,
        "revised_by_later": False,
        "automatic_inventory": None,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O074:classifier"])


@register("O076", ("H", "L"))
def o076(inp: dict) -> RecipeResult:
    h, l = dec(inp["H"]), dec(inp["L"])
    mpoc = (h + l) / 2
    vpoc = dec(inp.get("volume_poc"))
    px = dec(inp.get("price"))
    return _r("O076", "computed", {
        "mpoc": mpoc,
        "volume_poc": vpoc,
        "touch_mpoc": None if px is None else px == mpoc,
        "touch_vpoc": None if px is None or vpoc is None else px == vpoc,
        "distinct": vpoc is None or vpoc != mpoc,
    }, known_at=inp.get("known_at"))


@register("O078", ("visits",))
def o078(inp: dict) -> RecipeResult:
    as_of = inp.get("as_of")
    by_price = {}
    a_low = None
    for v in inp["visits"]:
        if as_of is not None and v.get("t") is not None and v["t"] > as_of:
            continue
        px = dec(v["price"])
        key = str(px)
        by_price.setdefault(key, [])
        by_price[key].append(v["letter"])
        if v["letter"] == "A":
            a_low = px if a_low is None else min(a_low, px)
    selected = inp.get("price")
    letters = by_price.get(str(dec(selected)), []) if selected is not None else []
    members = sorted(set(letters)) if selected is not None else None
    return _r("O078", "computed", {
        "members": members,
        "count": None if members is None else len(members),
        "a_low": a_low,
    }, known_at=inp.get("known_at"))


@register("O079", ("rows",))
def o079(inp: dict) -> RecipeResult:
    accepted = inp.get("accepted")
    as_of = inp.get("as_of")
    extra = inp.get("later_letter")
    extra_at = inp.get("later_at")
    rows = dict(inp["rows"])
    if extra and extra_at is not None and (as_of is None or extra_at <= as_of):
        px, letter = extra
        key = str(dec(px))
        rows[key] = list(rows.get(key, [])) + [letter]
    interior = []
    outer = []
    if accepted:
        lo, hi = dec(accepted[0]), dec(accepted[1])
        for k, letters in rows.items():
            px = dec(k)
            uniq = set(letters)
            if lo < px < hi and len(uniq) == 1:
                interior.append({"price": px, "letter": next(iter(uniq)), "count": len(uniq)})
            elif px > hi or px < lo:
                outer.append({"price": px, "letters": sorted(uniq)})
    return _r("O079", "supplied", {
        "interior": interior,
        "interior_count": len(interior),
        "outer_tail": outer,
        "interior_letter": interior[0]["letter"] if interior and len({x["letter"] for x in interior}) == 1 else None,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O079:selection"])


@register("O080", ("rows",))
def o080(inp: dict) -> RecipeResult:
    rows = sorted(((dec(k), set(v)) for k, v in inp["rows"].items()), key=lambda x: x[0], reverse=inp.get("side", "upper") == "upper")
    tail = []
    for px, letters in rows:
        if len(letters) == 1:
            tail.append((px, next(iter(letters))))
        else:
            break
    same = len({L for _, L in tail}) == 1 if tail else False
    criterion = inp.get("excess_criterion", "same_letter_tail")
    excess = same and len(tail) >= 2 if criterion == "same_letter_tail" else None
    return _r("O080", "computed", {
        "tail_length": len(tail),
        "same_letter": same,
        "excess": excess,
        "independent_other_side": True,
    }, known_at=inp.get("known_at"))


@register("O081", ("rows",))
def o081(inp: dict) -> RecipeResult:
    instrument = inp.get("instrument", "NQ")
    criterion = inp.get("poor_criterion")
    side = inp.get("side", "upper")
    rows = sorted(((dec(k), set(v)) for k, v in inp["rows"].items()), key=lambda x: x[0], reverse=side == "upper")
    tail = []
    nxt = None
    for i, (px, letters) in enumerate(rows):
        if len(letters) == 1:
            tail.append((px, next(iter(letters))))
        else:
            nxt = (px, letters)
            break
    if instrument != "NQ" and criterion is None:
        return _r("O081", "hole", {
            "tail_length": len(tail), "poor_high": None, "poor_low": None,
        }, hole_ids=["HOLE:O081:definition"], coverage_ok=None)
    poor_high = side == "upper" and len(tail) == 1
    poor_low = False
    excess_low = side == "lower" and len(tail) >= 2 and len({L for _, L in tail}) == 1
    return _r("O081", "computed", {
        "tail_length": len(tail),
        "next_row_multi": nxt is not None and len(nxt[1]) > 1,
        "poor_high": poor_high if side == "upper" else False,
        "poor_low": poor_low,
        "excess_not_poor_low": excess_low,
    }, known_at=inp.get("known_at"))


@register("O082", ("A", "B"))
def o082(inp: dict) -> RecipeResult:
    a, b = inp["A"], inp["B"]
    ibh = max(dec(a["H"]), dec(b["H"]))
    ibl = min(dec(a["L"]), dec(b["L"]))
    known = inp.get("ib_known_at")
    use_at = inp.get("use_at")
    defining = inp.get("defining_trade_at")
    if defining is not None and use_at is not None and defining > use_at:
        return _r("O082", "invalid", {"IBL": None, "IBH": None}, base_ok=False, reason="causal")
    later_h, later_l = dec(inp.get("later_H")), dec(inp.get("later_L"))
    upper_ext = None if later_h is None else max(Decimal(0), later_h - ibh)
    lower_ext = None if later_l is None else max(Decimal(0), ibl - later_l)
    both = None if upper_ext is None or lower_ext is None else (upper_ext > 0 and lower_ext > 0)
    return _r("O082", "computed", {
        "IBH": ibh, "IBL": ibl, "W": ibh - ibl,
        "upper_extension": upper_ext, "lower_extension": lower_ext,
        "both_broken": both,
    }, known_at=known or inp.get("known_at"))


@register("O083", ("open_px",))
def o083(inp: dict) -> RecipeResult:
    open_px = dec(inp["open_px"])
    as_of = inp.get("as_of")
    prices = inp.get("prices") or []
    crossed_below = False
    for p in prices:
        if as_of is not None and p["t"] > as_of:
            continue
        if dec(p["price"]) < open_px:
            crossed_below = True
    claim = inp.get("claim", "bullish_no_through_open")
    ok = (not crossed_below) if claim == "bullish_no_through_open" else None
    return _r("O083", "computed", {
        "no_through_open": ok,
        "crossed_below": crossed_below,
        "automatic_classifier": None,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O083:classifier"])


@register("O084", ("label", "label_at", "ib_extension"))
def o084(inp: dict) -> RecipeResult:
    label_at = inp.get("label_at")
    use_at = inp.get("use_at")
    label = inp.get("label")
    ext = dec(inp.get("ib_extension"))
    if label_at is not None and use_at is not None and label_at > use_at:
        return _r("O084", "invalid", {"label_available": False, "trend_day": False}, base_ok=False, reason="causal")
    return _r("O084", "supplied", {
        "label": label,
        "label_available": label_at is None or use_at is None or label_at <= use_at,
        "ib_extension": ext,
        "trend_day": False if label != "trend" else True,
        "automatic_classifier": None,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O084:classifier"])


@register("O085", ("shape", "author"))
def o085(inp: dict) -> RecipeResult:
    shape = inp.get("shape")
    brk = inp.get("break_at")
    retest = inp.get("retest_at")
    dirs = inp.get("directions") or []
    direction = None if len(set(dirs)) > 1 else (dirs[0] if dirs else inp.get("direction"))
    entry = bool(brk and retest)
    return _r("O085", "supplied", {
        "shape": shape,
        "entry_pass": entry,
        "direction": direction,
        "automatic_detector": None,
        "context_only": not entry,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O085:detector"])




@register("O090", ("lo", "hi"))
def o090(inp: dict) -> RecipeResult:
    lo, hi = dec(inp["lo"]), dec(inp["hi"])
    contact = inp.get("contact_at")
    confirm = inp.get("confirm_at")
    decision = inp.get("decision_at")
    if confirm is None:
        return _r("O090", "hole", {"route_ok": None}, hole_ids=["HOLE:O090:confirmation"], coverage_ok=None)
    known = inp.get("known_at")
    order = (_ordered(known, contact, confirm, decision) is True and
             contact is not None and confirm is not None and contact < confirm)
    if decision is not None and confirm > decision:
        return _r("O090", "invalid", {"route_ok": False}, base_ok=False, reason="causal")
    return _r("O090", "supplied", {
        "band": [lo, hi],
        "poc": dec(inp.get("poc")),
        "route_ok": order,
        "far_edge_replaces_confirm": False,
        "far_edge_at": inp.get("far_edge_at"),
    }, known_at=confirm)


@register("O091", ("ledge",))
def o091(inp: dict) -> RecipeResult:
    times = [inp.get("ledge_known_at"), inp.get("break_at"), inp.get("departure_at"), inp.get("retest_at"), inp.get("defense_at"), inp.get("entry_at")]
    if inp.get("other_band"):
        return _r("O091", "invalid", {"order_ok": False}, base_ok=False, reason="identity")
    required_times = ("ledge_known_at", "break_at", "departure_at", "retest_at", "defense_at")
    if any(inp.get(key) is None for key in required_times):
        missing = next(key for key in required_times if inp.get(key) is None)
        return _r("O091", "hole", {"order_ok": None}, hole_ids=[f"HOLE:O091:{missing}"], coverage_ok=None)
    order = _ordered(*[t for t in times if t is not None])
    entry = inp.get("entry_at")
    retest = inp.get("retest_at")
    if entry is not None and retest is not None and entry < retest:
        return _r("O091", "invalid", {"order_ok": False}, base_ok=False, reason="causal")
    return _r("O091", "supplied", {
        "ledge": dec(inp["ledge"]),
        "order_ok": order is not False,
    }, known_at=inp.get("defense_at") or inp.get("known_at"))


@register("O092", ("va_lo", "va_hi"))
def o092(inp: dict) -> RecipeResult:
    lo, hi = dec(inp["va_lo"]), dec(inp["va_hi"])
    px = dec(inp.get("price"))
    inside = None if px is None else lo <= px <= hi
    periods = inp.get("periods")
    period_inside = None
    if periods is not None:
        period_inside = all(dec(p[0]) >= lo and dec(p[1]) <= hi for p in periods)
    auto = None if inp.get("inside_convention") is None else period_inside
    return _r("O092", "computed", {
        "inside": inside,
        "period_inside": period_inside,
        "automatic_acceptance": auto,
    }, known_at=inp.get("known_at"), hole_ids=[] if inp.get("inside_convention") else ["HOLE:O092:acceptance"])


@register("O093", ("va_lo", "va_hi", "older_poc"))
def o093(inp: dict) -> RecipeResult:
    if inp.get("older_id") and inp.get("established_id") and inp.get("older_id") == inp.get("established_id"):
        return _r("O093", "invalid", {"distinct": False, "route_ok": False}, base_ok=False, reason="identity")
    tag_at = inp.get("tag_at")
    tag_px = dec(inp.get("tag_px"))
    older = dec(inp["older_poc"])
    tagged = tag_px == older if tag_px is not None else False
    decision = inp.get("decision_at")
    rej = inp.get("rejection_at")
    approach = inp.get("rejection_from")
    target = dec(inp.get("target"))
    expected_target = (dec(inp["va_hi"]) if approach == "above" else
                       dec(inp["va_lo"]) if approach == "below" else None)
    if tag_at is None or not tagged:
        return _r("O093", "computed", {
            "tagged": False, "route_ok": False, "distinct": True,
            "target": target,
        }, known_at=decision or inp.get("known_at"), base_ok=True)
    if approach is None or target is None:
        return _r("O093", "hole", {"tagged": True, "distinct": True,
            "route_ok": None, "target": target},
            hole_ids=["HOLE:O093:rejection_side_or_target"], coverage_ok=None)
    if target != expected_target:
        return _r("O093", "invalid", {"tagged": True, "distinct": True,
            "route_ok": False, "target": target}, base_ok=False,
            reason="failed-auction target is bound to the wrong value boundary")
    order = _ordered(inp.get("breakout_at"), tag_at, rej, decision)
    return _r("O093", "supplied", {
        "tagged": True,
        "distinct": True,
        "route_ok": order is not False,
        "target": target,
    }, known_at=decision or rej)




@register("O095", ("poc",))
def o095(inp: dict) -> RecipeResult:
    fails = inp.get("failed_crosses") or []
    as_of = inp.get("as_of") or inp.get("use_at")
    seen_ids, seen_times, tests = set(), set(), []
    for item in fails:
        f = item if isinstance(item, dict) else {"id": str(item), "t": item}
        at = f.get("known_at", f.get("t"))
        if at is None or (as_of is not None and at > as_of):
            continue
        if f.get("profile_id") is not None and inp.get("profile_id") is not None and f["profile_id"] != inp["profile_id"]:
            return _r("O095", "invalid", {"current_poc_read": None}, base_ok=False, reason="profile identity mismatch")
        fid = f.get("id", str(at))
        if fid not in seen_ids and at not in seen_times:
            tests.append(fid)
            seen_ids.add(fid)
            seen_times.add(at)
    count = len(tests)
    retest = inp.get("retest_at")
    use_at = inp.get("use_at")
    retest_ok = retest is not None and (use_at is None or retest <= use_at)
    passage = inp.get("passage_at")
    if passage is not None and retest is not None and retest < passage:
        return _r("O095", "invalid", {"retest_available": False}, base_ok=False, reason="retest precedes passage")
    passage_visible = passage is not None and (as_of is None or passage <= as_of)
    hold = inp.get("source_hold_confirmed")
    efficient = inp.get("source_passage_confirmed")
    complete = passage_visible and retest_ok and hold is True and efficient is True
    return _r("O095", "supplied" if complete else "hole", {
        "test_ids": tests,
        "failed_test_count": count,
        "passage_at": passage if passage_visible else None,
        "retest_available": retest_ok,
        "held_retest_at": retest if retest_ok and hold is True else None,
        "current_poc_read": "efficient_passage" if complete else None,
        "next_objective_id": inp.get("next_objective_id"),
        "far_edge_is_passage": False,
    }, known_at=inp.get("known_at"), coverage_ok=True if complete else None,
       hole_ids=[] if complete else ["HOLE:O095:source_passage_hold"])


@register("O096", ("lo", "hi"))
def o096(inp: dict) -> RecipeResult:
    lo, hi = dec(inp["lo"]), dec(inp["hi"])
    t0, t1 = inp.get("lower_at"), inp.get("upper_at")
    direction = inp.get("direction", "up")
    ordered_traversal = (t0 is not None and t1 is not None and
                         ((t0 < t1) if direction == "up" else (t1 < t0)))
    duration = None if t0 is None or t1 is None else abs(t1 - t0) / (60 * 1_000_000_000)
    retest = inp.get("retest_at")
    control = inp.get("control_at")
    entry = inp.get("entry_at")
    if entry is not None and ((retest is not None and retest > entry) or (control is not None and control > entry)):
        return _r("O096", "invalid", {"authorized": False, "no_hold": None}, base_ok=False, reason="causal")
    return _r("O096", "computed", {
        "duration_minutes": Decimal(str(int(duration))) if duration is not None else None,
        "whole_traversal": ordered_traversal,
        "rejected_over_30": False,
        "no_hold": None if inp.get("hold_definition") is None else inp.get("no_hold"),
        "authorized": False if entry is not None and (retest is None or control is None) else True,
    }, known_at=inp.get("known_at"), hole_ids=[] if inp.get("hold_definition") else ["HOLE:O096:hold"])


@register("O097", ("htf_side", "ltf_side", "thesis_at", "local_at"))
def o097(inp: dict) -> RecipeResult:
    thesis = inp.get("htf_side")
    local = inp.get("ltf_side")
    thesis_at = inp.get("thesis_at")
    local_at = inp.get("local_at")
    died = inp.get("thesis_died_at")
    use_at = inp.get("use_at")
    if local_at is not None and use_at is not None and local_at > use_at:
        return _r("O097", "invalid", {"aligned": False}, base_ok=False, reason="causal")
    alive = None if use_at is None else died is None or died > use_at
    aligned = None if alive is None or thesis is None or local is None else bool(alive and thesis == local)
    return _r("O097", "supplied", {
        "aligned": aligned,
        "thesis_alive": alive,
        "htf_side": thesis,
        "ltf_side": local,
    }, known_at=local_at or thesis_at)


@register("O100", ("bid_size_before", "bid_size_after"))
def o100(inp: dict) -> RecipeResult:
    before = dec(inp.get("bid_size_before"))
    after = dec(inp.get("bid_size_after"))
    change = None if before is None or after is None else after - before
    executed = dec(inp.get("executed_sell"))
    consumed = executed is not None and executed > 0
    depth = inp.get("depth_ok")
    lifecycle = inp.get("lifecycle_ok")
    verified_hidden = True if depth and lifecycle and consumed else (None if not (depth and lifecycle) else False)
    return _r("O100", "computed", {
        "display_change": change,
        "consumed_and_replenished": False if not consumed else (True if lifecycle else False),
        "verified_hidden_reserve": verified_hidden if verified_hidden is True else None,
        "execution_evidence": consumed,
    }, known_at=inp.get("known_at"), hole_ids=[] if depth and lifecycle else ["HOLE:O100:depth"])


@register("O102", ("known_at",))
def o102(inp: dict) -> RecipeResult:
    if inp.get("lifecycle"):
        life = inp["lifecycle"]
        consumption = dec(life.get("consumed"))
        refresh = dec(life.get("refresh"))
        display = dec(life.get("final_display"))
        return _r("O102", "computed", {
            "consumption": consumption,
            "refresh": refresh,
            "final_display": display,
            "verified_replenishment": True,
        }, known_at=inp.get("known_at"))
    first, last = dec(inp.get("first_display")), dec(inp.get("last_display"))
    net = None if first is None or last is None else last - first
    return _r("O102", "hole", {
        "net": net,
        "consumption": None,
        "refresh": None,
        "verified_replenishment": None,
    }, hole_ids=["HOLE:O102:lifecycle"], coverage_ok=None)


@register("O103", ("q", "area_ticks", "executed_total", "displayed"))
def o103(inp: dict) -> RecipeResult:
    q = dec(inp.get("q", Q))
    ticks = dec(inp.get("area_ticks", 2))
    width = ticks * q
    executed = dec(inp.get("executed_total"))
    displayed = dec(inp.get("displayed"))
    return _r("O103", "computed", {
        "width": width,
        "executed_total": executed,
        "displayed": displayed,
        "replenishment_hypothesis": executed is not None and displayed is not None and executed > displayed,
        "verified_hidden_reserve": None,
        "participant_count": None,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O103:verification"])


@register("O104", ("origin",))
def o104(inp: dict) -> RecipeResult:
    origin = dec(inp["origin"])
    q = dec(inp.get("q", Q))
    later = dec(inp.get("later_px"))
    edge = inp.get("selected_edge")
    band = inp.get("origin_band")
    if later is None:
        missing = "edge" if band is not None and edge is None else "later_px"
        return _r("O104", "hole", {"reward_points": None, "reward_ticks": None,
            "retest_is_reward": False}, hole_ids=[f"HOLE:O104:{missing}"], coverage_ok=None)
    if q is None or q <= 0:
        return _r("O104", "invalid", {"reward_points": None, "reward_ticks": None,
            "retest_is_reward": False}, base_ok=False, reason="nonpositive tick size")
    direction = inp.get("direction")
    pts = abs(later - origin) if direction is None else dec(direction) * (later - origin)
    ticks = pts / q if q else None
    return _r("O104", "computed", {
        "reward_points": pts,
        "reward_ticks": ticks,
        "retest_is_reward": False,
    }, known_at=inp.get("known_at"))


@register("O105", ("trades",))
def o105(inp: dict) -> RecipeResult:
    delta = Decimal(0)
    unknown = Decimal(0)
    for tr in inp["trades"]:
        got = signed_size(tr.get("side"), tr.get("size"))
        if got["sign"] is None:
            unknown += dec(tr["size"] or 0)
        else:
            delta += dec(got["signed"])
    exact = None if unknown else delta
    lo, hi = delta - unknown, delta + unknown
    ref = dec(inp.get("reference"))
    ref_unit = inp.get("reference_unit", "contracts")
    if ref is not None and ref_unit != "contracts":
        return _r("O105", "invalid", {"cvd": exact, "difference": None}, base_ok=False, reason="units")
    diff = None if exact is None or ref is None else exact - ref
    holes = []
    if unknown:
        holes.append("HOLE:O105:unknown_side")
    if ref is None:
        holes.append("HOLE:O105:reference")
    if inp.get("reset_verified") is False:
        holes.append("HOLE:O105:reset")
        exact = None
        diff = None
    return _r("O105", "hole" if holes else "computed", {
        "cvd": exact,
        "delta_interval": [lo, hi],
        "difference": diff,
        "automatic_reference": None,
    }, known_at=inp.get("known_at"), hole_ids=holes,
        coverage_ok=None if holes else True)


@register("O106", ("O", "C"))
def o106(inp: dict) -> RecipeResult:
    o, c = dec(inp["O"]), dec(inp["C"])
    change = c - o
    delta = Decimal(0)
    unknown = Decimal(0)
    for tr in inp.get("trades") or []:
        got = signed_size(tr.get("side"), tr.get("size"))
        if got["signed"] is not None:
            delta += dec(got["signed"])
        else:
            unknown += dec(tr.get("size") or 0)
    exact_delta = None if unknown else delta
    opposed = None if exact_delta is None else ((change > 0 and delta < 0) or (change < 0 and delta > 0))
    if change == 0 and exact_delta is not None:
        opposed = False
    return _r("O106", "hole" if unknown else "computed", {
        "price_change": change,
        "delta": exact_delta,
        "delta_bounds": [delta - unknown, delta + unknown],
        "opposed_signs": opposed,
    }, known_at=inp.get("known_at"),
        hole_ids=["HOLE:O106:aggressor_side"] if unknown else [],
        coverage_ok=None if unknown else True)


@register("O108", ("snapshots",))
def o108(inp: dict) -> RecipeResult:
    cid = inp.get("candle_id")
    use_at = inp.get("use_at")
    snaps = [s for s in inp["snapshots"] if cid is None or s.get("candle_id") == cid]
    if cid is not None and any(s.get("candle_id") != cid for s in inp["snapshots"]):
        if not snaps or any(s.get("candle_id") != cid for s in inp["snapshots"] if s.get("require_same", True)):
            if inp.get("require_same_candle") and len({s.get("candle_id") for s in inp["snapshots"]}) > 1:
                return _r("O108", "invalid", {"poc": None, "same_candle": False}, base_ok=False, reason="identity")
    chosen = None
    for s in snaps:
        if use_at is None or s["known_at"] <= use_at:
            chosen = s
    if chosen is None:
        return _r("O108", "invalid", {"poc": None}, base_ok=False, reason="causal")
    first = snaps[0]
    change = dec(chosen["poc"]) - dec(first["poc"])
    return _r("O108", "computed", {
        "poc": dec(chosen["poc"]),
        "change": change,
        "same_candle": True,
        "candle_id": chosen.get("candle_id", cid),
    }, known_at=chosen["known_at"])


@register("O109", ("rows",))
def o109(inp: dict) -> RecipeResult:
    q = dec(inp.get("q", Q))
    rows = sorted(inp["rows"], key=lambda r: dec(r["ask_px"]))
    ratios = []
    for r in rows:
        bid = dec(r["bid"])
        ask = dec(r["ask"])
        ratios.append(None if bid == 0 else ask / bid)
    consecutive = True
    for a, b in zip(rows, rows[1:]):
        if dec(b["ask_px"]) - dec(a["ask_px"]) != q:
            consecutive = False
    k = dec(inp.get("ratio_min"))
    n_req = inp.get("row_count")
    qualifies = None
    if k is not None and n_req is not None:
        qualifies = consecutive and len(rows) >= n_req and all(x is not None and x >= k for x in ratios)
    band = [dec(rows[0]["ask_px"]), dec(rows[-1]["ask_px"])] if rows else None
    printed = None
    if inp.get("printed_ask") is not None and inp.get("printed_bid") is not None:
        printed = dec(inp["printed_ask"]) / dec(inp["printed_bid"])
    return _r("O109", "computed", {
        "ratios": ratios,
        "consecutive": consecutive,
        "qualifies": qualifies,
        "stack_band": band,
        "printed_ratio": printed,
        "automatic_settings": None if k is None else True,
    }, known_at=inp.get("known_at"), hole_ids=[] if k is not None else ["HOLE:O109:settings"])


@register("O110", ("B", "S"))
def o110(inp: dict) -> RecipeResult:
    b, s = dec(inp["B"]), dec(inp["S"])
    multiple = None if s == 0 else b / s
    percent_of = None if s == 0 else (b / s) * Decimal(100)
    percent_more = None if s == 0 else ((b - s) / s) * Decimal(100)
    rule = inp.get("rule")
    flag = None
    if rule == "350_of":
        flag = percent_of is not None and percent_of >= Decimal(350)
    elif rule == "350_more":
        flag = percent_more is not None and percent_more >= Decimal(350)
    return _r("O110", "computed", {
        "buy_multiple": multiple,
        "percent_of": percent_of,
        "percent_more": percent_more,
        "source_350_flag": flag,
        "meets_of": percent_of == Decimal(350) if percent_of is not None else None,
        "meets_more": False if percent_more is not None and percent_more < Decimal(350) else None,
    }, known_at=inp.get("known_at"), hole_ids=[] if rule else ["HOLE:O110:convention"])


@register("O111", ("interval_s", "n_prints", "contracts"))
def o111(inp: dict) -> RecipeResult:
    sec = dec(inp["interval_s"])
    if sec <= 0:
        return _r("O111", "invalid", {"prints_per_second": None,
            "contracts_per_second": None, "source_panel_value": None,
            "automatic_speed": None}, base_ok=False, reason="nonpositive interval")
    prints = dec(inp["n_prints"]) / sec if sec else None
    cps = dec(inp["contracts"]) / sec if sec else None
    return _r("O111", "computed", {
        "prints_per_second": prints,
        "contracts_per_second": cps,
        "source_panel_value": None,
        "automatic_speed": None,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O111:panel"])


@register("O112", ("bid",))
def o112(inp: dict) -> RecipeResult:
    bid, ask = dec(inp.get("bid")), dec(inp.get("ask"))
    q = dec(inp.get("q", Q))
    if ask is None or bid is None:
        return _r("O112", "hole", {"spread_points": None, "spread_ticks": None}, hole_ids=["HOLE:O112:quote"], coverage_ok=None)
    if q is None or q <= 0:
        return _r("O112", "invalid", {"spread_points": None,
            "spread_ticks": None}, base_ok=False, reason="nonpositive tick size")
    if ask < bid:
        return _r("O112", "invalid", {"spread_points": None, "crossed": True}, base_ok=False, reason="crossed")
    spread = ask - bid
    return _r("O112", "computed", {
        "spread_points": spread,
        "spread_ticks": spread / q if q else None,
        "crossed": False,
    }, known_at=inp.get("known_at"))


@register("O113", ("from_px", "to_px", "from_at", "to_at"))
def o113(inp: dict) -> RecipeResult:
    t0, t1 = inp["from_at"], inp["to_at"]
    if t1 <= t0:
        return _r("O113", "invalid", {"duration_seconds": None,
            "net_distance": None, "net_speed": None,
            "aggressive_arrival": None, "post_touch_included": False},
            base_ok=False, reason="approach endpoints are not ordered")
    dur_s = (t1 - t0) / 1_000_000_000
    dist = abs(dec(inp["to_px"]) - dec(inp["from_px"]))
    speed = dist / Decimal(str(dur_s)) if dur_s else None
    return _r("O113", "computed", {
        "duration_seconds": Decimal(str(int(dur_s))) if dur_s == int(dur_s) else Decimal(str(dur_s)),
        "net_distance": dist,
        "net_speed": speed,
        "aggressive_arrival": None if inp.get("source_arrival") is None else inp.get("source_arrival"),
        "post_touch_included": False,
    }, known_at=t1, hole_ids=[] if inp.get("source_arrival") is not None else ["HOLE:O113:interpretation"])


@register("O114", ("sizes",))
def o114(inp: dict) -> RecipeResult:
    sizes = [int(s) for s in inp["sizes"]]
    if not sizes or any(size <= 0 for size in sizes):
        return _r("O114", "invalid", {"digit_counts": None,
            "declining": None, "source_classification": None},
            base_ok=False, reason="execution sizes must be positive")
    digits = [len(str(abs(s))) for s in sizes]
    declining = all(a > b for a, b in zip(digits, digits[1:]))
    grouping = inp.get("grouping")
    return _r("O114", "computed", {
        "digit_counts": digits,
        "declining": declining,
        "source_classification": None if grouping is None else declining,
    }, known_at=inp.get("known_at"), hole_ids=[] if grouping else ["HOLE:O114:threshold"])


@register("O115", ("origin",))
def o115(inp: dict) -> RecipeResult:
    origin = dec(inp["origin"])
    q = dec(inp.get("q", Q))
    reward_px = dec(inp.get("reward_px"))
    entry = dec(inp.get("entry"))
    confirm = dec(inp.get("confirm_px", reward_px))
    stages = [inp.get("defense_at"), inp.get("refresh_at"), inp.get("exhaustion_at"), inp.get("reward_at"), inp.get("entry_at")]
    order = _ordered(*[t for t in stages if t is not None])
    if q is None or q <= 0:
        return _r("O115", "invalid", {"reward_ticks": None,
            "entry_distance_ticks": None, "geometry_ok": None,
            "order_ok": None}, base_ok=False, reason="nonpositive tick size")
    ticks = None if reward_px is None else abs(reward_px - origin) / q
    dist = None if entry is None or confirm is None else abs(entry - confirm) / q
    geo_ok = None if dist is None else dist <= Decimal(2)
    return _r("O115", "supplied", {
        "reward_ticks": ticks,
        "entry_distance_ticks": dist,
        "geometry_ok": geo_ok,
        "order_ok": order is not False,
    }, known_at=inp.get("entry_at") or inp.get("known_at"))


@register("O116", ("known_at",))
def o116(inp: dict) -> RecipeResult:
    zone = inp.get("zone")
    if zone is None:
        return _r("O116", "hole", {"later_touches": None, "automatic_zone": None}, hole_ids=["HOLE:O116:construction"], coverage_ok=None)
    lo, hi = dec(zone[0]), dec(zone[1])
    if lo > hi:
        return _r("O116", "invalid", {"later_touches": None}, base_ok=False, reason="zone bounds reversed")
    dep = inp.get("departure_at")
    departure_price = dec(inp.get("departure_price"))
    formed = inp.get("formed_at", inp.get("known_at"))
    if dep is None or departure_price is None:
        return _r("O116", "hole", {"zone": [lo, hi], "later_touches": None, "automatic_zone": None},
                  hole_ids=["HOLE:O116:departure"], coverage_ok=None)
    if lo <= departure_price <= hi or formed is not None and dep <= formed:
        return _r("O116", "invalid", {"later_touches": 0, "automatic_zone": None},
                  base_ok=False, reason="no actual departure outside the formed zone")
    touches = inp.get("touches") or []
    touch_ids = []
    inside_run = False
    cutoff = inp.get("as_of", inp.get("use_at"))
    latest = formed
    holes = ["HOLE:O116:construction"]
    for t in sorted(touches, key=lambda row: row['t']):
        px = dec(t["price"])
        if t['t'] <= dep or cutoff is not None and t['t'] > cutoff:
            if t['t'] == dep and lo <= px <= hi:
                holes.append('HOLE:O116:ordering')
            continue
        if t.get('instrument_id', inp.get('instrument_id')) != inp.get('instrument_id'):
            return _r('O116', 'invalid', {'later_touches': None}, base_ok=False, reason='touch instrument mismatch')
        latest = max(latest or t['t'], t['t'])
        if lo <= px <= hi:
            if not inside_run:
                touch_ids.append(t.get('touch_id', f"{inp.get('zone_id', 'source-zone')}:touch:{t['t']}"))
                inside_run = True
        else:
            inside_run = False
    return _r("O116", "supplied", {
        "zone": [lo, hi],
        "zone_known_at": formed, "departure_at": dep, "touch_ids": touch_ids,
        "later_touches": len(touch_ids),
        "automatic_zone": None,
    }, known_at=latest, hole_ids=holes)


@register("O117", ("cutoff", "priors"))
def o117(inp: dict) -> RecipeResult:
    cutoff = inp.get("cutoff")
    priors = inp.get("priors") or []
    touch_ids, eligible, unresolved, seen_starts = [], [], [], set()
    current_at, current_id = inp.get('current_touch_at'), inp.get('current_touch_id')
    zone_id = inp.get('zone_id')
    invalid, missing = [], []
    latest = None
    if current_at is None:
        missing.append('current_touch_at')
    elif cutoff >= current_at:
        invalid.append('feature cutoff is not strictly before current touch')
    for p in priors:
        start = p.get("start")
        resolved = p.get("defense_at")
        pid = p.get('id', p.get('touch_id'))
        if pid is None or start is None:
            missing.append('prior_touch_identity')
            continue
        if p.get('zone_id', zone_id) != zone_id:
            invalid.append('history belongs to a different zone')
            continue
        if pid == current_id or current_at is not None and start >= current_at or start > cutoff:
            continue
        if pid in touch_ids or start in seen_starts:
            continue
        touch_ids.append(pid)
        seen_starts.add(start)
        if resolved is not None and resolved <= cutoff:
            eligible.append(pid)
            latest = max(latest or resolved, resolved)
        else:
            unresolved.append(pid)
    claimed = inp.get('selected_history_ids')
    if claimed is not None and not set(claimed) <= set(eligible):
        invalid.append('claimed memory includes a current, unresolved or unavailable outcome')
    return _r("O117", "computed", {
        "prior_touch_count": len(touch_ids),
        "resolved_defense_count": len(eligible), "prior_resolved_defense_count": len(eligible),
        "eligible_history_ids": eligible, "unresolved_history_ids": unresolved,
        "max_feature_known_at": latest, "memory_causal": False if invalid else None if missing else True,
        "current_counts_as_prior": False,
    }, known_at=latest or cutoff, base_ok=False if invalid else None if missing else True,
       coverage_ok=None if missing else True, reason='; '.join(invalid) or None,
       hole_ids=[f'HOLE:O117:{name}' for name in missing] + (['HOLE:O117:ordering_identity'] if invalid else []))


@register("O118", ("origin", "failed_pushes", "release_at", "failure_at", "entry_at"))
def o118(inp: dict) -> RecipeResult:
    origin = inp.get("origin")
    if origin is None:
        return _r("O118", "hole", {"linked": None}, hole_ids=["HOLE:O118:origin"], coverage_ok=None)
    later_high = inp.get("later_high_replaces")
    stages = {k: inp.get(k) for k in ("release_at", "failure_at", "refill_at", "drive_at", "hold_at")}
    entry = inp.get("entry_at")
    required = inp.get("required_stages") or []
    missing_req = [s for s in required if not stages.get(s if s.endswith("_at") else s + "_at" if False else {"refill": "refill_at", "drive": "drive_at", "hold": "hold_at"}.get(s, s))]
    branch_ok = not missing_req
    if entry is not None:
        for s in required:
            key = {"refill": "refill_at", "drive": "drive_at", "hold": "hold_at"}.get(s, s)
            t = stages.get(key)
            if t is None or t > entry:
                branch_ok = False
    return _r("O118", "supplied", {
        "origin": [dec(origin[0]), dec(origin[1])],
        "linked": True,
        "branch_ok": branch_ok,
        "later_high_replaces_origin": bool(later_high),
        "failed_push_count": inp.get("failed_pushes"),
    }, known_at=inp.get("known_at"))


@register("O119", ("prior_failures", "fail_at", "breakdown_at", "retest_at", "confirm_at", "entry_at"))
def o119(inp: dict) -> RecipeResult:
    fails = inp.get("prior_failures") or []
    ids, resolved, distinct = set(), set(), 0
    history_known = True
    for f in fails:
        fid, at = f.get("id"), f.get("known_at", f.get("t"))
        if f.get("band_id") is not None and inp.get("band_id") is not None and f["band_id"] != inp["band_id"]:
            return _r("O119", "invalid", {"order_ok": False}, base_ok=False, reason="historical failure band identity mismatch")
        if at is not None and at >= inp["fail_at"]:
            return _r("O119", "invalid", {"order_ok": False}, base_ok=False, reason="historical failure is not prior to current attempt")
        if fid is None or at is None:
            history_known = False
        if fid not in ids and (at is None or at not in resolved):
            distinct += 1
        ids.add(fid)
        if at is not None:
            resolved.add(at)
    seq = [inp.get("fail_at"), inp.get("breakdown_at"), inp.get("retest_at"), inp.get("confirm_at"), inp.get("entry_at")]
    entry = inp.get("entry_at")
    retest = inp.get("retest_at")
    if entry is not None and retest is not None and entry < retest:
        return _r("O119", "invalid", {"order_ok": False, "distinct_failures": distinct}, base_ok=False, reason="causal")
    confirm = inp.get("confirm_at")
    if confirm is None:
        return _r("O119", "hole", {"order_ok": None, "distinct_failures": distinct}, hole_ids=["HOLE:O119:confirmation"], coverage_ok=None)
    return _r("O119", "supplied", {
        "prior_failure_ids": sorted(x for x in ids if x is not None),
        "distinct_failures": distinct,
        "order_ok": _ordered(*[t for t in seq if t is not None]) is not False,
        "historical_failures_known": history_known,
    }, known_at=confirm, coverage_ok=True if history_known else None,
       hole_ids=[] if history_known else ["HOLE:O119:prior_failure_times"])


@register("O121", ("band",))
def o121(inp: dict) -> RecipeResult:
    times = [inp.get("arrival_at"), inp.get("rejection_at"), inp.get("added_at"), inp.get("decision_at")]
    decision = inp.get("decision_at")
    added = inp.get("added_at")
    if decision is not None and added is not None and added > decision:
        return _r("O121", "invalid", {"order_ok": False}, base_ok=False, reason="causal")
    depth = inp.get("depth_ok")
    if depth is not True or (added is None and inp.get("need_added")):
        return _r("O121", "hole", {"order_ok": None, "evidence": None}, hole_ids=["HOLE:O121:depth"], coverage_ok=None)
    return _r("O121", "supplied", {
        "band": dec(inp["band"]),
        "order_ok": _ordered(*[t for t in times if t is not None]) is not False,
        "evidence": True if depth is not False else None,
    }, known_at=decision or inp.get("known_at"))


@register("O122", ("support",))
def o122(inp: dict) -> RecipeResult:
    stages = [inp.get("absorption_at"), inp.get("reward_at"), inp.get("return_at"), inp.get("defense_at"), inp.get("decision_at")]
    if inp.get("return_at") is None and inp.get("complete_attempt"):
        return _r("O122", "computed", {"strict_reversal_sequence": False}, known_at=inp.get("known_at"), base_ok=True)
    if inp.get("cvd_reference") is None and inp.get("need_cvd", True):
        return _r("O122", "hole", {"strict_reversal_sequence": None}, hole_ids=["HOLE:O122:cvd"], coverage_ok=None)
    order = _ordered(*[t for t in stages if t is not None])
    return _r("O122", "supplied", {
        "strict_reversal_sequence": order is not False and all(stages),
        "support": dec(inp["support"]),
        "reward_px": dec(inp.get("reward_px")),
        "return_px": dec(inp.get("return_px")),
    }, known_at=inp.get("decision_at") or inp.get("known_at"))


@register("O123", ("origin", "confirm_px", "entry"))
def o123(inp: dict) -> RecipeResult:
    q = dec(inp.get("q", Q))
    origin, confirm, entry = dec(inp["origin"]), dec(inp["confirm_px"]), dec(inp["entry"])
    daily = dec(inp.get("daily_r"))
    cap = dec(inp.get("daily_cap", -4))
    if q is None or q <= 0:
        return _r("O123", "invalid", {"reward_ticks": None,
            "distance_ticks": None, "daily_stop_ok": None,
            "geometry_ok": None, "size_halved_repairs": False},
            base_ok=False, reason="nonpositive tick size")
    reward = abs(confirm - origin) / q
    dist = abs(entry - confirm) / q
    if cap != Decimal("-4"):
        return _r("O123", "invalid", {"reward_ticks": reward,
            "distance_ticks": dist, "daily_stop_ok": None,
            "geometry_ok": None, "size_halved_repairs": False},
            base_ok=False, reason="STOP daily cap must remain -4R")
    if daily is None:
        return _r("O123", "hole", {"reward_ticks": reward,
            "distance_ticks": dist, "daily_stop_ok": None,
            "geometry_ok": dist <= Decimal(2), "size_halved_repairs": False},
            hole_ids=["HOLE:O123:daily_r"], coverage_ok=None)
    daily_ok = daily > Decimal("-4")
    geo_ok = dist <= Decimal(2)
    return _r("O123", "computed", {
        "reward_ticks": reward,
        "distance_ticks": dist,
        "daily_stop_ok": daily_ok,
        "geometry_ok": geo_ok,
        "size_halved_repairs": False,
    }, known_at=inp.get("known_at"))


@register("O124", ("disagreement_candle", "poc_candle"))
def o124(inp: dict) -> RecipeResult:
    c1 = inp.get("disagreement_candle")
    c2 = inp.get("poc_candle")
    if c1 and c2 and c1 != c2:
        return _r("O124", "invalid", {"same_candle": False, "route_ok": False}, base_ok=False, reason="identity")
    if inp.get("tape") is None and inp.get("need_tape", True):
        return _r("O124", "hole", {"route_ok": None, "same_candle": True}, hole_ids=["HOLE:O124:tape"], coverage_ok=None)
    seq = _ordered(inp.get("disagreement_at"), inp.get("poc_at"), inp.get("flow_at"), inp.get("entry_at"))
    return _r("O124", "supplied", {
        "same_candle": True,
        "route_ok": seq is not False,
        "poc_from": dec(inp.get("poc_from")),
        "poc_to": dec(inp.get("poc_to")),
    }, known_at=inp.get("entry_at") or inp.get("known_at"))


@register("O125", ("vwap", "sigma"))
def o125(inp: dict) -> RecipeResult:
    mu, sig = dec(inp["vwap"]), dec(inp["sigma"])
    k = dec(inp.get("k", 2))
    if sig < 0:
        return _r("O125", "invalid", {"upper": None,
            "confirmation": None, "target": None}, base_ok=False,
            reason="negative sigma")
    upper = mu + k * sig
    touch = inp.get("touch_at")
    reject = inp.get("reject_at")
    confirm = inp.get("confirm_at")
    entry = inp.get("entry_at")
    target = dec(inp.get("target", mu))
    later = dec(inp.get("later_vwap"))
    if confirm is None:
        return _r("O125", "hole", {"upper": upper, "confirmation": None, "target": target}, hole_ids=["HOLE:O125:confirmation"], coverage_ok=None)
    order = _ordered(touch, reject, confirm, entry)
    return _r("O125", "supplied", {
        "upper": upper,
        "confirmation": True,
        "target": target,
        "later_rewrites_target": False,
        "later_vwap": later,
        "order_ok": order is not False,
    }, known_at=entry or confirm)


@register("O126", ("catalyst_at", "release_at", "failure_at", "refill_at", "drive_at", "retest_at", "entry_at"))
def o126(inp: dict) -> RecipeResult:
    keys = ("catalyst_at", "release_at", "failure_at", "refill_at", "drive_at", "retest_at", "entry_at")
    times = [inp.get(k) for k in keys]
    entry = inp.get("entry_at")
    need = inp.get("required", list(keys[:-1]))
    missing = [key for key in need if inp.get(key) is None]
    if missing:
        if inp.get("complete_attempt"):
            return _r("O126", "computed", {"sequence_ok": False,
                "short_gamma": inp.get("short_gamma")}, known_at=entry or inp.get("known_at"))
        return _r("O126", "hole", {"sequence_ok": None,
            "short_gamma": inp.get("short_gamma")},
            hole_ids=[f"HOLE:O126:{key}" for key in missing], coverage_ok=None)
    if entry is not None:
        for k in need:
            t = inp.get(k)
            if t is None or t > entry:
                return _r("O126", "invalid", {"sequence_ok": False}, base_ok=False, reason="causal")
    if inp.get("cvd_reference") is None and inp.get("need_cvd", True):
        return _r("O126", "hole", {"sequence_ok": None}, hole_ids=["HOLE:O126:cvd"], coverage_ok=None)
    return _r("O126", "supplied", {
        "sequence_ok": _ordered(*times) is True and inp.get("short_gamma") is True,
        "short_gamma": inp.get("short_gamma"),
    }, known_at=entry or inp.get("known_at"))


@register("O127", ("entry", "stop"))
def o127(inp: dict) -> RecipeResult:
    entry, stop = dec(inp["entry"]), dec(inp["stop"])
    risk = abs(entry - stop)
    r_mult = dec(inp.get("r_multiple"))
    r2 = None if r_mult is None else (entry + r_mult * risk if inp.get("side", "long") == "long" else entry - r_mult * risk)
    in_range = None if r_mult is None else Decimal(1) <= r_mult <= Decimal(3)
    dying = inp.get("dying_tape")
    qual = None if dying is None else True
    return _r("O127", "computed", {
        "initial_risk": risk,
        "r2": r2,
        "r_in_1_to_3": in_range,
        "qualification": qual,
        "automatic_selector": None,
    }, known_at=inp.get("known_at"),
        hole_ids=(["HOLE:O127:selector"] if dying is None else []) +
                 (["HOLE:O127:objective"] if r_mult is None else []),
        coverage_ok=None if dying is None or r_mult is None else True)


@register("O128", ("first_pullback_at", "entry_at"))
def o128(inp: dict) -> RecipeResult:
    first = inp.get("first_pullback_at")
    chosen = inp.get("chosen_pullback_at", first)
    later_fail = inp.get("later_failure_at")
    entry = inp.get("entry_at")
    if first is None:
        return _r("O128", "hole", {"first_pullback": None,
            "no_prior_failure": None, "later_failure_invalidates": False,
            "later_failure_at": later_fail, "order_ok": None},
            hole_ids=["HOLE:O128:first_pullback"], coverage_ok=None)
    if chosen is not None and first is not None and chosen != first:
        return _r("O128", "computed", {"first_pullback": False, "no_prior_failure": True}, known_at=entry or inp.get("known_at"), base_ok=True)
    return _r("O128", "supplied", {
        "first_pullback": True,
        "no_prior_failure": True,
        "later_failure_invalidates": False,
        "later_failure_at": later_fail,
        "order_ok": _ordered(inp.get("catalyst_at"), inp.get("release_at"), first, inp.get("confirm_at"), entry) is not False,
    }, known_at=entry or inp.get("known_at"))


@register("O129", ("lo", "hi"))
def o129(inp: dict) -> RecipeResult:
    lo, hi = dec(inp["lo"]), dec(inp["hi"])
    target = dec(inp.get("target"))
    seq = _ordered(inp.get("fail_at"), inp.get("depart_at"), inp.get("retest_at"), inp.get("entry_at"))
    long_gamma = inp.get("long_gamma")
    opposite_control = dec(inp.get("opposite_control"))
    if long_gamma is None:
        return _r("O129", "hole", {"band": [lo, hi], "target": target,
            "target_is_balance_low": False if target is not None and target != lo else (True if target == lo else None),
            "target_is_prior_opposite_control": None, "requires_lift": False,
            "order_ok": seq is not False, "long_gamma": None},
            hole_ids=["HOLE:O129:gamma"], coverage_ok=None)
    return _r("O129", "supplied", {
        "band": [lo, hi],
        "target": target,
        "target_is_balance_low": False if target is not None and target != lo else (True if target == lo else None),
        "requires_lift": False,
        "order_ok": seq is not False,
        "long_gamma": long_gamma,
        "target_is_prior_opposite_control": None if opposite_control is None or target is None else target == opposite_control,
    }, known_at=inp.get("entry_at") or inp.get("known_at"))


@register("O130", ("lo", "hi"))
def o130(inp: dict) -> RecipeResult:
    lo, hi = dec(inp["lo"]), dec(inp["hi"])
    if lo > hi:
        return _r("O130", "invalid", {"short_control": None,
            "old_defense_keeps_control": False}, base_ok=False,
            reason="lower bound exceeds upper bound")
    prior = inp.get("prior_defense_at")
    fresh = inp.get("fresh_defense_at")
    buyers = inp.get("buyers_defend_at")
    use_at = inp.get("use_at") or inp.get("entry_at")
    if buyers is not None and (use_at is None or buyers <= use_at):
        control = False
    else:
        control = fresh is not None and (use_at is None or fresh <= use_at)
    return _r("O130", "supplied", {
        "short_control": control,
        "old_defense_keeps_control": False,
        "prior_defense_at": prior,
        "fresh_defense_at": fresh,
    }, known_at=fresh or inp.get("known_at"))


@register("O131", ("micro_lo", "micro_hi", "entry", "stop"))
def o131(inp: dict) -> RecipeResult:
    complete = inp.get("complete_at")
    use_at = inp.get("use_at") or inp.get("entry_at")
    if complete is not None and use_at is not None and complete > use_at:
        return _r("O131", "invalid", {"qualifies": False}, base_ok=False, reason="causal")
    mlo, mhi = dec(inp["micro_lo"]), dec(inp["micro_hi"])
    stop, entry = dec(inp["stop"]), dec(inp["entry"])
    target = dec(inp.get("target"))
    below = stop < mlo if inp.get("side", "long") == "long" else stop > mhi
    strength = inp.get("source_strength")
    return _r("O131", "supplied", {
        "width": mhi - mlo,
        "stop_below_opposite": below,
        "target": target,
        "preexisting_target": inp.get("target_known_at") is None or
            use_at is None or inp.get("target_known_at") <= use_at,
        "qualifies": None if strength is None else bool(strength and below),
        "automatic_selector": None,
    }, known_at=complete or inp.get("known_at"),
        hole_ids=["HOLE:O131:strength"] if strength is None else [])


@register("O132", ("entry", "stop", "target"))
def o132(inp: dict) -> RecipeResult:
    entry, stop, target = dec(inp["entry"]), dec(inp["stop"]), dec(inp["target"])
    orig_risk = abs(entry - stop)
    r1 = abs(target - entry) / orig_risk if orig_risk else None
    later_stop = dec(inp.get("later_stop"))
    later_tgt = dec(inp.get("later_target"))
    later_risk = None if later_stop is None else abs(entry - later_stop)
    r2 = None if later_tgt is None or later_risk in (None, 0) else abs(later_tgt - entry) / later_risk
    return _r("O132", "computed", {
        "ratio": r1,
        "later_ratio": r2,
        "original_risk": orig_risk,
        "automatic_trailing": None,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O132:engine"])


@register("O133", ("entry_at", "confirm_at", "loss_at"))
def o133(inp: dict) -> RecipeResult:
    entry = inp.get("entry_at")
    confirm = inp.get("confirm_at")
    death = inp.get("death_at")
    loss = inp.get("loss_at")
    early = confirm is not None and entry is not None and entry < confirm
    confirmed_ok = confirm is not None and entry is not None and confirm <= entry
    killed = bool(death and (loss is None or death <= loss))
    if loss and not death:
        killed = False
    return _r("O133", "supplied", {
        "deliberate_early": early,
        "confirmed_branch": confirmed_ok,
        "thesis_killed_by_loss_alone": False,
        "automatic_selector": None,
    }, known_at=entry or inp.get("known_at"), hole_ids=["HOLE:O133:selector"])


@register("O134", ("tests", "inside_rows", "stopped_out"))
def o134(inp: dict) -> RecipeResult:
    tests = inp.get("tests") or []
    ordinal = len(tests)
    inside_rows = inp.get("inside_rows") or []
    current_is_one = True
    if inside_rows:
        current_is_one = True
    in_cohort = True
    if inp.get("stopped_out"):
        in_cohort = True
    return _r("O134", "supplied", {
        "ordinal": ordinal,
        "inside_rows_are_one_test": current_is_one,
        "in_cohort": in_cohort,
        "universal_third_touch": False,
    }, known_at=inp.get("known_at"))


@register("O135", ("resistance", "resistance_at", "entry_at"))
def o135(inp: dict) -> RecipeResult:
    marked = inp.get("resistance_at")
    entry = inp.get("entry_at")
    if marked is not None and entry is not None and marked > entry:
        return _r("O135", "invalid", {"case_ok": False, "automatic_full_trigger": None}, base_ok=False, reason="causal")
    return _r("O135", "supplied", {
        "case_ok": True,
        "automatic_full_trigger": None,
        "resistance": dec(inp.get("resistance")),
    }, known_at=entry or inp.get("known_at"), hole_ids=["HOLE:O135:selector"])


@register("O137", ("v1", "v2"))
def o137(inp: dict) -> RecipeResult:
    v1, v2 = inp["v1"], inp["v2"]
    administrative = {'version', 'model_version', 'frozen_at', 'created_at', 'updated_at', 'revision_at', 'recorded_at'}
    keys = (set(v1) | set(v2)) - administrative
    changed = sorted(k for k in keys if v1.get(k) != v2.get(k))
    from hashlib import sha256
    import json
    definition_hash = sha256(json.dumps(v2, sort_keys=True, separators=(',', ':'), default=str).encode()).hexdigest()
    frozen, start, end, review, revision = (inp.get(key) for key in
                                          ('frozen_at', 'sample_start_at', 'sample_end_at', 'comparison_at', 'revision_at'))
    complete = all(value is not None for value in (frozen, start, end, review, revision))
    causal = None if not complete else frozen <= start <= end <= review <= revision
    if revision is not None and inp.get('use_at') is not None and revision > inp['use_at']:
        causal = False
    block_id, parent = inp.get('review_block_id'), inp.get('revision_parent')
    identity = not (block_id is not None and parent is not None and block_id != parent)
    for observation in inp.get('observations', []):
        if (observation.get('decision_at') is not None and revision is not None
                and observation['decision_at'] < revision
                and observation.get('model_version') != inp.get('prior_model_version')):
            identity = False
    valid = causal is not False and identity and not (inp.get('claim_one_variable') is True and len(changed) != 1)
    return _r("O137", "computed", {
        "model_version": inp.get('model_version', v2.get('model_version', v2.get('version'))),
        "definition_hash": definition_hash, "encoding": "utf-8/sorted-keys/compact-json",
        "frozen_at": frozen, "observation_ids": [o.get('id') for o in inp.get('observations', [])],
        "revision_parent": parent, "revision_causal": causal,
        "changed_fields": changed,
        "count": len(changed),
        "one_variable": len(changed) == 1,
        "features": inp.get("features"),
    }, known_at=revision or inp.get("known_at"), base_ok=valid,
       hole_ids=[] if complete else ['HOLE:O137:review_block'],
       reason=None if valid else 'revision timing, prior-block identity or declared one-variable claim is invalid')


@register("O138", ("known_at",))
def o138(inp: dict) -> RecipeResult:
    close = dec(inp.get("close"))
    close_at = inp.get("close_at")
    rule_px = dec(inp.get("death_close"))
    recover = dec(inp.get("recover_px"))
    stop_at = inp.get("stopped_at")
    missing_news = inp.get("missing_news")
    complete = inp.get("death_conditions_complete")
    first_death = None
    if close is not None and rule_px is not None and close < rule_px:
        first_death = close_at
    revived = False
    if first_death is not None and recover is not None:
        revived = False
    if first_death:
        alive = False
    elif missing_news or complete is not True:
        alive = None
    else:
        alive = True
    if stop_at and not first_death:
        pass
    return _r("O138", "supplied", {
        "first_death": first_death,
        "alive": alive,
        "revived": revived,
        "stop_kills_thesis": False,
    }, known_at=first_death or inp.get("known_at"),
        hole_ids=["HOLE:O138:death_conditions"] if alive is None else [],
        coverage_ok=None if alive is None else True)


@register("O143", ("high", "confirm_at"))
def o143(inp: dict) -> RecipeResult:
    priced = inp.get("high_priced_at")
    confirm = inp.get("confirm_at")
    use_at = inp.get("use_at")
    prot = dec(inp.get("protected_high", inp.get("high")))
    if confirm is None:
        return _r("O143", "hole", {"protected_high": None}, hole_ids=["HOLE:O143:confirmation"], coverage_ok=None)
    if use_at is not None and confirm > use_at:
        return _r("O143", "invalid", {"protected_high": None, "usable": False}, base_ok=False, reason="causal")
    return _r("O143", "supplied", {
        "protected_high": prot,
        "known_at_confirm": confirm,
        "not_at_price_time": priced,
        "usable": True,
    }, known_at=confirm)


@register("O144", ("entry_at",))
def o144(inp: dict) -> RecipeResult:
    fresh_conf = inp.get("fresh_confirm_at")
    reused = inp.get("reused_confirm_at")
    entry = inp.get("entry_at")
    daily = dec(inp.get("daily_r"))
    cap = dec(inp.get("daily_cap", -4))
    prior_exit = inp.get("prior_exit_at")
    returned = inp.get("return_at")
    same_identity = inp.get("same_thesis_band")
    missing = [name for name, value in (("prior_exit_at", prior_exit),
        ("return_at", returned), ("same_thesis_band", same_identity),
        ("daily_r", daily)) if value is None]
    if missing:
        return _r("O144", "hole", {"fresh": None, "blocked": None,
            "freshness_ok": None, "parent_exit_at": prior_exit,
            "return_at": returned, "same_thesis_band": same_identity},
            hole_ids=[f"HOLE:O144:{name}" for name in missing], coverage_ok=None)
    if cap != Decimal("-4"):
        return _r("O144", "invalid", {"fresh": False, "blocked": None,
            "freshness_ok": False}, base_ok=False, reason="daily cap must remain -4R")
    blocked = daily is not None and cap is not None and daily <= cap
    fresh = (same_identity is True and reused is None and fresh_conf is not None and
             prior_exit < returned <= fresh_conf and (entry is None or fresh_conf <= entry))
    if reused is not None and entry is not None:
        fresh = False
    return _r("O144", "supplied", {
        "fresh": fresh and not blocked,
        "blocked": blocked,
        "freshness_ok": fresh,
    }, known_at=entry or inp.get("known_at"))


@register("O146", ("eligible", "journal"))
def o146(inp: dict) -> RecipeResult:
    eligible = list(inp["eligible"])
    journal = dict(inp["journal"])
    missing = [i for i in eligible if i not in journal]
    accounted = len(eligible) - len(missing)
    reason_at = inp.get("reason_at")
    entry_at = inp.get("entry_at")
    later_expl = reason_at is not None and entry_at is not None and reason_at > entry_at
    causal, separated, unknown = not later_expl, True, False
    breaches, reviews = [], []
    if len(set(eligible)) != len(eligible):
        return _r('O146', 'invalid', {'completeness': False}, base_ok=False, reason='duplicate eligible journal ID')
    for candidate_id in eligible:
        row = journal.get(candidate_id)
        if not isinstance(row, dict):
            unknown = True
            continue
        decision = row.get('decision_at')
        feature = row.get('feature_known_at', row.get('reason_at'))
        outcome = row.get('outcome_at')
        if decision is None or feature is None:
            unknown = True
        elif feature > decision:
            causal = False
        if outcome is not None and decision is not None and outcome <= decision:
            causal = False
        input_id, outcome_id = row.get('input_record_id'), row.get('outcome_record_id')
        if input_id is not None and outcome_id is not None and input_id == outcome_id:
            separated = False
        breaches.extend(row.get('breaches', []))
        for link in row.get('review_links', []):
            reviews.append(link)
            if outcome is not None and link.get('known_at') is not None and link['known_at'] < outcome:
                causal = False
            if link.get('from_version') == link.get('to_version') and link.get('from_version') is not None:
                separated = False
    return _r("O146", "computed", {
        "journal_rows": journal, "eligible_ids_accounted_for": [i for i in eligible if i in journal],
        "missing_ids": missing, "pre_entry_fields_valid": False if not causal else None if unknown else True,
        "inputs_outcomes_separate": separated, "breach_records": breaches, "review_links": reviews,
        "accounted": accounted,
        "of": len(eligible),
        "missing": missing,
        "completeness": not missing,
        "later_explanation": later_expl,
    }, known_at=inp.get("known_at"), base_ok=separated,
       hole_ids=['HOLE:O146:pre_entry_fields'] if unknown else [])


@register("O147", ("objects",))
def o147(inp: dict) -> RecipeResult:
    objs = inp["objects"]
    peer_at = inp.get("peer_fill_at")
    decision = inp.get("decision_at")
    test_at = inp.get("peer_test_at")
    reread = test_at is not None and (decision is None or test_at <= decision)
    if peer_at is not None and decision is not None and peer_at > decision:
        reread_fill = False
    else:
        reread_fill = False if peer_at else reread
    return _r("O147", "supplied", {
        "native_count": len(objs),
        "reread_ok": reread,
        "peer_fill_revises": reread_fill,
        "edge_inequality_relevant": False,
    }, known_at=decision or inp.get("known_at"))


@register("O148", ("eligible", "selected", "orders", "filled"))
def o148(inp: dict) -> RecipeResult:
    needed = ("eligible", "selected", "orders", "filled")
    missing = [key for key in needed if inp.get(key) is None]
    if missing:
        return _r("O148", "hole", {"eligible": None, "selected": None,
            "orders": None, "filled": None, "unselected": None,
            "missing_orders": None, "completeness": None, "pairable": None},
            hole_ids=[f"HOLE:O148:{key}" for key in missing], coverage_ok=None)
    eligible = int(inp.get("eligible", 0))
    selected = int(inp.get("selected", 0))
    orders = int(inp.get("orders", 0))
    filled = int(inp.get("filled", 0))
    if min(eligible, selected, orders, filled) < 0 or not (eligible >= selected >= orders >= filled):
        return _r("O148", "invalid", {"eligible": eligible, "selected": selected,
            "orders": orders, "filled": filled, "unselected": None,
            "missing_orders": None, "completeness": False, "pairable": False},
            base_ok=False, reason="cohort lifecycle counts are inconsistent")
    unselected = eligible - selected
    missing_orders = selected - orders
    completeness = missing_orders == 0
    selected_ids, filled_ids = inp.get('selected_ids'), inp.get('filled_candidate_ids')
    eligible_ids = inp.get('eligible_ids')
    order_records, fill_records = inp.get('order_records'), inp.get('fill_records')
    identity_errors = []
    if eligible_ids is not None:
        if len(set(eligible_ids)) != len(eligible_ids) or len(eligible_ids) != eligible:
            identity_errors.append('eligible IDs/count disagree')
    if selected_ids is not None:
        if len(set(selected_ids)) != len(selected_ids) or len(selected_ids) != selected:
            identity_errors.append('selected IDs/count disagree')
        if eligible_ids is not None and not set(selected_ids) <= set(eligible_ids):
            identity_errors.append('selected ID not in eligible cohort')
    if order_records is not None:
        order_map = {r.get('order_id'): r.get('candidate_id') for r in order_records}
        if None in order_map or len(order_map) != len(order_records) or len(order_map) != orders:
            identity_errors.append('order identities/count disagree')
        if selected_ids is None or not set(order_map.values()) <= set(selected_ids):
            identity_errors.append('order lacks its selected candidate')
        if fill_records is not None:
            fill_keys = [r.get('fill_id') for r in fill_records]
            filled_orders = {r.get('order_id') for r in fill_records}
            if None in fill_keys or len(set(fill_keys)) != len(fill_keys) or not filled_orders <= set(order_map):
                identity_errors.append('fill lacks its unique linked order')
            if len(filled_orders) != filled:
                identity_errors.append('filled order count differs; partial fills are not separate signals')
            filled_ids = sorted({order_map[oid] for oid in filled_orders if oid in order_map}, key=str)
    if identity_errors:
        return _r('O148', 'invalid', {'pairable': False, 'completeness': False},
                  base_ok=False, reason='; '.join(identity_errors))
    common_ids = inp.get('common_ids')
    pairable = False if filled != selected else None
    if isinstance(selected_ids, list) and isinstance(filled_ids, list) and isinstance(common_ids, list):
        pairable = (len(set(selected_ids)) == selected == len(selected_ids)
                    and len(set(filled_ids)) == filled == len(filled_ids)
                    and set(selected_ids) == set(filled_ids) == set(common_ids))
    if inp.get('claim_paired') is True and pairable is not True:
        return _r('O148', 'invalid', {'pairable': pairable, 'completeness': completeness},
                  base_ok=False, reason='cohorts lack complete common candidate identities')
    frozen = inp.get('frozen_at')
    first = inp.get('sample_start_at')
    if frozen is not None and first is not None and frozen > first:
        return _r('O148', 'invalid', {'cohort_causal': False, 'pairable': pairable},
                  base_ok=False, reason='cohort inclusion frozen after observations began')
    manifest = {key: inp.get(key) for key in ('process_version', 'inclusion_rule', 'frozen_at',
                                             'instrument_id', 'eligible_ids', 'selected_ids',
                                             'order_records', 'fill_records', 'split_direction')}
    complete_manifest = all(manifest[key] is not None for key in ('process_version', 'inclusion_rule', 'frozen_at', 'eligible_ids'))
    from hashlib import sha256
    import json
    cohort_hash = sha256(json.dumps(manifest, sort_keys=True, default=str).encode()).hexdigest() if complete_manifest else None
    return _r("O148", "computed", {
        "eligible": eligible,
        "selected": selected,
        "orders": orders,
        "filled": filled,
        "unselected": unselected,
        "missing_orders": missing_orders,
        "completeness": completeness,
        "pairable": pairable,
        "eligible_ids": eligible_ids, "selected_ids": selected_ids,
        "unselected_ids": sorted(set(eligible_ids) - set(selected_ids), key=str) if eligible_ids is not None and selected_ids is not None else None,
        "filled_candidate_ids": filled_ids,
        "order_records": order_records, "fill_records": fill_records, "cohort_hash": cohort_hash,
        "signal_cohort_id": inp.get('signal_cohort_id'), "fill_cohort_id": inp.get('fill_cohort_id'),
        "cohort_causal": None if frozen is None or first is None else frozen <= first,
        "candidate_discovery": "hole", "split_direction": inp.get('split_direction'),
    }, known_at=inp.get("known_at"), hole_ids=[] if complete_manifest else ['HOLE:O148:cohort_manifest'])






@register("O152", ("r_unit", "target_outcome", "quantity"))
def o152(inp: dict) -> RecipeResult:
    unit = dec(inp.get("r_unit"))
    tgt = dec(inp.get("target_outcome"))
    stp = dec(inp.get("stop_outcome"))
    if unit is not None and unit <= 0:
        return _r("O152", "invalid", {"target_r": None, "stop_r": None,
            "round_trip_cost": None}, base_ok=False, reason="nonpositive R unit")
    tgt_r = None if unit is None or tgt is None else tgt / unit
    stp_r = None if unit is None or stp is None else stp / unit
    tick_val = dec(inp.get("tick_value"))
    qty = dec(inp.get("quantity"))
    cost_ticks = dec(inp.get('round_trip_cost_ticks'))
    stop_slippage = dec(inp.get('stop_slippage_ticks'))
    if any(value is not None and value < 0 for value in (tick_val, qty, cost_ticks, stop_slippage)):
        return _r('O152', 'invalid', {'round_trip_cost': None}, base_ok=False, reason='negative cost units')
    rt = None if tick_val is None or qty is None or cost_ticks is None else tick_val * qty * cost_ticks
    gross_target, gross_stop = dec(inp.get('gross_target_ticks')), dec(inp.get('gross_stop_ticks'))
    consistency = None
    if gross_target is not None and gross_stop is not None and cost_ticks is not None and stop_slippage is not None:
        consistency = tgt == gross_target - cost_ticks and stp == -gross_stop - cost_ticks - stop_slippage
    return _r("O152", "computed", {
        "target_r": tgt_r,
        "stop_r": stp_r,
        "round_trip_cost": rt,
        "trade_cost_ticks": cost_ticks, "stop_slippage_ticks": stop_slippage,
        "supplied_gross_net_consistency": consistency, "account_fees_separate": True,
        "account_fee_ledger": inp.get('account_fees', []),
    }, known_at=inp.get("known_at"), base_ok=consistency is not False,
       hole_ids=[f'HOLE:O152:{key}' for key, value in [('tick_value', tick_val), ('round_trip_cost_ticks', cost_ticks)] if value is None])


@register("O153", ("wins", "losses", "mean_win", "mean_loss", "reported_ev"))
def o153(inp: dict) -> RecipeResult:
    if inp.get("wins") is None or inp.get("losses") is None:
        return _r("O153", "hole", {"win_rate": None, "ev": None,
            "profit_factor": None, "consistent": None,
            "from_market_prices": False},
            hole_ids=["HOLE:O153:denominator"], coverage_ok=None)
    wins = int(inp.get("wins", 0))
    losses = int(inp.get("losses", 0))
    if wins < 0 or losses < 0:
        return _r("O153", "invalid", {"win_rate": None, "ev": None,
            "profit_factor": None, "consistent": None,
            "from_market_prices": False}, base_ok=False,
            reason="negative outcome count")
    n = wins + losses
    wr = None if n == 0 else Decimal(wins) / n
    mw, ml = dec(inp.get("mean_win")), dec(inp.get("mean_loss"))
    ev = None if wr is None or mw is None or ml is None else wr * mw + (Decimal(1) - wr) * ml
    gross_win = None if mw is None else mw * wins
    gross_loss = None if ml is None else abs(ml) * losses
    pf = None if not gross_loss else gross_win / gross_loss
    reported = dec(inp.get("reported_ev"))
    consistent = None if reported is None or ev is None else reported == ev
    return _r("O153", "computed", {
        "win_rate": wr,
        "ev": ev,
        "profit_factor": pf,
        "consistent": consistent,
        "from_market_prices": False,
    }, known_at=inp.get("known_at"))




















@register("O164", ("volume", "response"))
def o164(inp: dict) -> RecipeResult:
    vol, resp = dec(inp["volume"]), dec(inp["response"])
    if vol < 0:
        return _r("O164", "invalid", {"response_per_volume": None,
            "absorption": None, "source_efficiency_class": None,
            "automatic_class": None}, base_ok=False, reason="negative executed volume")
    ratio = None if vol == 0 else resp / vol
    depth = inp.get("opposing_depth")
    absorption = None
    if resp == 0 and depth is None:
        absorption = None
    return _r("O164", "computed", {
        "response_per_volume": ratio,
        "absorption": absorption,
        "source_efficiency_class": None if inp.get("source_class") is None else inp.get("source_class"),
        "automatic_class": None,
    }, known_at=inp.get("known_at"), hole_ids=["HOLE:O164:interpretation"])






_PCT = Decimal(20) / Decimal(252).sqrt()
_PTS = _PCT * Decimal(5000) / Decimal(100)

add_fixture({"id": "O031-F1", "recipe": "O031", "inputs": {"trades": [{"price": 100, "size": 1, "t": _d(9, 40)}, {"price": 102, "size": 3, "t": _d(9, 50)}], "anchor_price_at": _d(9, 40), "anchor_known_at": _d(9, 50), "anchor_id": "swing", "as_of": _d(9, 50), "known_at": _d(9, 50), "use_at": _d(9, 50)}, "expected": {"avwap": Decimal("101.5"), "usable": True}})
add_fixture({"id": "O031-F1b", "recipe": "O031", "inputs": {"trades": [{"price": 100, "size": 1, "t": _d(9, 40)}, {"price": 102, "size": 3, "t": _d(9, 50)}], "anchor_price_at": _d(9, 40), "anchor_known_at": _d(9, 50), "as_of": _d(9, 50), "known_at": _d(9, 50), "use_at": _d(9, 45)}, "expected": {"usable": False, "base_ok": False}})
add_fixture({"id": "O032-F1", "recipe": "O032", "inputs": {"mu": 100, "sigma": 2, "variance_convention": "supplied", "k": 2, "price": 104, "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"band": [Decimal("96"), Decimal("104")], "touch_upper": True, "fade": False}})
add_fixture({"id": "O032-F1b", "recipe": "O032", "inputs": {"mu": 100, "sigma": 2, "variance_convention": "supplied", "k": Decimal("2.5"), "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"band": [Decimal("95"), Decimal("105")]}})
add_fixture({"id": "O032-F1c", "recipe": "O032", "inputs": {"mu": 100, "sigma": 2, "variance_convention": "supplied", "k": 3, "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"band": [Decimal("94"), Decimal("106")]}})
add_fixture({"id": "O032-F1d", "recipe": "O032", "inputs": {"mu": 100, "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"faithful_band": None, "automatic_sigma": None}})
add_fixture({"id": "O033-F1", "recipe": "O033", "inputs": {"source_regime": "long_gamma", "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"aggressive_ofm_ok": False, "balance_fade_ok": True, "automatic_regime": None}})
add_fixture({"id": "O033-F1b", "recipe": "O033", "inputs": {"source_regime": "uncertain", "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"aggressive_ofm_ok": None, "balance_fade_ok": None}})
add_fixture({"id": "O034-F1", "recipe": "O034", "inputs": {"symbol": "QQQ", "strike": 500, "expiry": date(2026, 9, 11), "observation_date": date(2026, 9, 11), "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"is_0dte": True, "mapped_price": None}})
add_fixture({"id": "O034-F1b", "recipe": "O034", "inputs": {"symbol": "QQQ", "strike": 500, "expiry": date(2026, 9, 14), "observation_date": date(2026, 9, 11), "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"is_0dte": False, "mapped_price": None}})
add_fixture({"id": "O035-F1", "recipe": "O035", "inputs": {"spot": 502, "flip": 500, "source_regime_interpretation": "uncertain", "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"spot_minus_flip": Decimal("2"), "relation": "above", "source_regime_interpretation": "uncertain", "automatic_flip": None}})
add_fixture({"id": "O035-F1b", "recipe": "O035", "inputs": {"spot": 502, "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"relation": None, "automatic_flip": None}})
add_fixture({"id": "O036-F1", "recipe": "O036", "inputs": {"walls": [{"id": "cw1", "rank": 1, "price": 510, "kind": "call"}, {"id": "cw2", "rank": 2, "price": 505, "kind": "call"}, {"id": "pw1", "rank": 1, "price": 490, "kind": "put"}], "max_pain_id": "mp1", "spot": 506, "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"distinct_ids": 4, "automatic_walls": None}})
add_fixture({"id": "O037-F1", "recipe": "O037", "inputs": {"max_pain": 500, "put_wall": 495, "max_pain_id": "mp", "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"difference": Decimal("5"), "automatic_max_pain": None}})
add_fixture({"id": "O037-F1b", "recipe": "O037", "inputs": {"put_wall": 495, "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"max_pain_value": None, "automatic_max_pain": None}})
add_fixture({"id": "O038-F1", "recipe": "O038", "inputs": {"source_value": 500, "unit": "etf", "computed_vol": 20, "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"source_value": Decimal("500"), "computed_is_not_source": True, "automatic_value": None}})
add_fixture({"id": "O038-F1b", "recipe": "O038", "inputs": {"computed_vol": 20, "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"source_value": None, "automatic_value": None}})
add_fixture({"id": "O039-F1", "recipe": "O039", "inputs": {"source_vol_gex": 12, "unit": "U", "computed": 10, "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"source_vol_gex": Decimal("12"), "automatic_value": None}})
add_fixture({"id": "O039-F1b", "recipe": "O039", "inputs": {"computed": 10, "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"faithful_value": None, "automatic_value": None}})
add_fixture({"id": "O040-F1", "recipe": "O040", "inputs": {"gauge": 7, "scale": "0-10", "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"gauge_value": Decimal("7"), "as_percent": None, "automatic_pressure": None, "entry_permission": None}})
add_fixture({"id": "O041-F1", "recipe": "O041", "inputs": {"kg1": [100, 101], "kg1_id": "kg1", "hvn_id": "hvn", "reaction_id": "rx", "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"id_count": 3, "two_reason_ok": True, "automatic_kg1": None}})
add_fixture({"id": "O041-F1b", "recipe": "O041", "inputs": {"kg1": [100, 101], "kg1_id": "kg1", "reaction_id": "rx", "known_at": _d(9, 20), "use_at": _d(9, 30)}, "expected": {"two_reason_ok": False}})
add_fixture({"id": "O042-F1", "recipe": "O042", "inputs": {"vix": 20, "publication_at": _d(8, 0), "later_vix": 25, "later_at": _d(16, 0), "known_at": _d(8, 0), "use_at": _d(9, 30)}, "expected": {"usable_vix": Decimal("20"), "later_available": False}})
add_fixture({"id": "O042-F1b", "recipe": "O042", "inputs": {"vix": 20, "known_at": _d(8, 0), "use_at": _d(9, 30)}, "expected": {"faithful_preopen": None}})
add_fixture({"id": "O043-F1", "recipe": "O043", "inputs": {"vix": 20, "P": 5000, "known_at": _d(8, 0), "use_at": _d(9, 30)}, "expected": {"percent": _PCT, "point_estimate": _PTS, "must_travel": False}})
add_fixture({"id": "O044-F1", "recipe": "O044", "inputs": {"near": 20, "far": 22, "post_near": 16, "post_at": _d(10, 5), "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"difference": Decimal("2"), "far_over_near": Decimal("1.1"), "change": None, "post_available": False}})
add_fixture({"id": "O044-F1b", "recipe": "O044", "inputs": {"near": 20, "far": 22, "post_near": 16, "post_at": _d(10, 5), "known_at": _d(10, 5), "use_at": _d(10, 6)}, "expected": {"change": Decimal("-4")}})
add_fixture({"id": "O045-F1", "recipe": "O045", "inputs": {"vvix": 100, "available_at": _d(9, 0), "known_at": _d(9, 0), "use_at": _d(9, 30)}, "expected": {"vvix": Decimal("100"), "entry_permission": None}})
add_fixture({"id": "O045-F1b", "recipe": "O045", "inputs": {"vvix": 110, "available_at": _d(10, 0), "known_at": _d(10, 0), "use_at": _d(9, 30)}, "expected": {"usable": False, "base_ok": False}})
add_fixture({"id": "O060-F1", "recipe": "O060", "inputs": {"lo": 100, "hi": 110, "declared_at": _d(9, 20), "price": 108, "known_at": _d(9, 20), "use_at": _d(9, 40)}, "expected": {"width": Decimal("10"), "inside": True, "edge_fade": False, "automatic_selector": None}})
add_fixture({"id": "O060-F1b", "recipe": "O060", "inputs": {"lo": 105, "hi": 115, "declared_at": _d(10, 30), "price": 108, "known_at": _d(10, 30), "use_at": _d(9, 40)}, "expected": {"base_ok": False}})
add_fixture({"id": "O065-F1", "recipe": "O065", "inputs": {"poc": 105, "visits": [], "as_of": _d(9, 40), "coverage_complete": True, "known_at": _yd(16, 0), "use_at": _d(9, 40)}, "expected": {"untested": True}})
add_fixture({"id": "O065-F1b", "recipe": "O065", "inputs": {"poc": 105, "visits": [{"t": _d(9, 45), "price": 105}], "as_of": _d(9, 45), "coverage_complete": True, "known_at": _yd(16, 0), "use_at": _d(9, 45)}, "expected": {"untested": False}})
add_fixture({"id": "O065-F1c", "recipe": "O065", "inputs": {"poc": 105, "visits": [], "as_of": _d(9, 40), "coverage_complete": False, "overnight_visits_count": True, "known_at": _yd(16, 0), "use_at": _d(9, 40)}, "expected": {"untested": None}})
add_fixture({"id": "O070-F1", "recipe": "O070", "inputs": {"profiles": [{"100": 3, "101": 2}, {"100": 4, "101": 1}], "known_at": _d(10, 0), "use_at": _d(10, 5)}, "expected": {"composite": {"100": Decimal("7"), "101": Decimal("3")}, "total": Decimal("10")}})
add_fixture({"id": "O070-F1b", "recipe": "O070", "inputs": {"profiles": [{"100": 3, "101": 2}, {"100": 4, "101": 1}], "overlap": True, "known_at": _d(10, 0), "use_at": _d(10, 5)}, "expected": {"total": None}})
add_fixture({"id": "O071-F1", "recipe": "O071", "inputs": {"lo": 100, "hi": 105, "controlling_low": 100, "selected_at": _d(9, 40), "price": 104, "known_at": _d(9, 40), "use_at": _d(10, 0)}, "expected": {"inside": True, "controlling_reference": Decimal("100")}})
add_fixture({"id": "O071-F1b", "recipe": "O071", "inputs": {"lo": 103, "hi": 108, "selected_at": _d(10, 1), "price": 104, "known_at": _d(10, 1), "use_at": _d(10, 0)}, "expected": {"base_ok": False}})
add_fixture({"id": "O072-F1", "recipe": "O072", "inputs": {"lo": 100, "hi": 101, "band_id": "a", "defended_at": _d(9, 30), "defense_known_at": _d(9, 32), "contact_at": _d(10, 0), "known_at": _d(9, 32), "use_at": _d(10, 0)}, "expected": {"prior_defense_known": True}})
add_fixture({"id": "O072-F1b", "recipe": "O072", "inputs": {"lo": 100, "hi": 101, "band_id": "a", "defended_at": _d(9, 30), "defense_known_at": _d(9, 32), "fresh_defense_at": _d(10, 2), "known_at": _d(9, 32), "use_at": _d(10, 1)}, "expected": {"fresh_available": False}})
add_fixture({"id": "O072-F1c", "recipe": "O072", "inputs": {"lo": 102, "hi": 103, "band_id": "b", "other_band_id": "a", "defended_at": _d(9, 30), "defense_known_at": _d(9, 32), "known_at": _d(9, 32), "use_at": _d(10, 0)}, "expected": {"inherit_other_band": False}})
add_fixture({"id": "O074-F1", "recipe": "O074", "inputs": {"inventory": "net_long", "shelf": 100, "later_response": "break_below_99", "known_at": _d(9, 20), "use_at": _d(9, 35)}, "expected": {"inventory": "net_long", "revised_by_later": False, "automatic_inventory": None}})
add_fixture({"id": "O074-F1b", "recipe": "O074", "inputs": {"known_at": _d(9, 20), "use_at": _d(9, 35)}, "expected": {"inventory": None, "automatic_inventory": None}})
add_fixture({"id": "O076-F1", "recipe": "O076", "inputs": {"H": 120, "L": 100, "volume_poc": 114, "price": 110, "known_at": _d(9, 30), "use_at": _d(9, 40)}, "expected": {"mpoc": Decimal("110"), "volume_poc": Decimal("114"), "touch_mpoc": True, "touch_vpoc": False}})
add_fixture({"id": "O078-F1", "recipe": "O078", "inputs": {"visits": [{"price": 100, "letter": "A", "t": _d(9, 35)}, {"price": 100, "letter": "A", "t": _d(9, 40)}, {"price": 100, "letter": "B", "t": _d(10, 5)}, {"price": 101, "letter": "A", "t": _d(9, 36)}], "price": 100, "as_of": _d(10, 30), "known_at": _d(10, 30), "use_at": _d(10, 31)}, "expected": {"members": ["A", "B"], "count": 2}})
add_fixture({"id": "O078-F1b", "recipe": "O078", "inputs": {"visits": [{"price": 100, "letter": "A", "t": _d(9, 35)}, {"price": 101, "letter": "A", "t": _d(9, 36)}], "price": 101, "as_of": _d(10, 0), "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"members": ["A"], "count": 1}})
add_fixture({"id": "O078-F1c", "recipe": "O078", "inputs": {"visits": [{"price": 100, "letter": "A", "t": _d(9, 35)}, {"price": 99, "letter": "A", "t": _d(9, 59)}], "price": 100, "as_of": _d(10, 0), "known_at": _d(10, 0), "use_at": _d(10, 0)}, "expected": {"a_low": Decimal("99")}})
add_fixture({"id": "O079-F1", "recipe": "O079", "inputs": {"rows": {"100": ["A", "B"], "101": ["C"], "102": ["C"], "103": ["C", "D"], "104": ["D"]}, "accepted": [100, 103], "known_at": _d(10, 30), "use_at": _d(10, 31)}, "expected": {"interior_letter": "C", "interior_count": 2}})
add_fixture({"id": "O079-F1b", "recipe": "O079", "inputs": {"rows": {"100": ["A", "B"], "101": ["C"], "102": ["C"], "103": ["C", "D"]}, "accepted": [100, 103], "later_letter": [101, "D"], "later_at": _d(11, 0), "as_of": _d(11, 0), "known_at": _d(11, 0), "use_at": _d(11, 1)}, "expected": {"interior_count": 1}})
add_fixture({"id": "O080-F1", "recipe": "O080", "inputs": {"rows": {"104": ["D"], "103": ["D"], "102": ["B", "D"]}, "side": "upper", "known_at": _d(10, 30), "use_at": _d(10, 31)}, "expected": {"tail_length": 2, "same_letter": True, "excess": True}})
add_fixture({"id": "O080-F1b", "recipe": "O080", "inputs": {"rows": {"104": ["D"], "103": ["C"], "102": ["B", "D"]}, "side": "upper", "known_at": _d(10, 30), "use_at": _d(10, 31)}, "expected": {"same_letter": False}})
add_fixture({"id": "O081-F1", "recipe": "O081", "inputs": {"rows": {"104": ["D"], "103": ["B", "D"]}, "instrument": "NQ", "side": "upper", "poor_criterion": "one_letter_outer", "known_at": _d(10, 30), "use_at": _d(10, 31)}, "expected": {"tail_length": 1, "poor_high": True}})
add_fixture({"id": "O081-F1b", "recipe": "O081", "inputs": {"rows": {"90": ["A"], "91": ["A"], "92": ["A", "B"]}, "instrument": "NQ", "side": "lower", "known_at": _d(10, 30), "use_at": _d(10, 31)}, "expected": {"excess_not_poor_low": True, "poor_low": False}})
add_fixture({"id": "O081-F1c", "recipe": "O081", "inputs": {"rows": {"104": ["D"], "103": ["B", "D"]}, "instrument": "ES", "side": "upper", "known_at": _d(10, 30), "use_at": _d(10, 31)}, "expected": {"poor_high": None}})
add_fixture({"id": "O082-F1", "recipe": "O082", "inputs": {"A": {"H": 110, "L": 100}, "B": {"H": 108, "L": 99}, "ib_known_at": _d(10, 30), "later_H": 112, "later_L": 98, "known_at": _d(10, 30), "use_at": _d(10, 31)}, "expected": {"IBH": Decimal("110"), "IBL": Decimal("99"), "W": Decimal("11"), "upper_extension": Decimal("2"), "lower_extension": Decimal("1"), "both_broken": True}})
add_fixture({"id": "O082-F1b", "recipe": "O082", "inputs": {"A": {"H": 110, "L": 100}, "B": {"H": 108, "L": 99}, "defining_trade_at": _d(10, 20), "ib_known_at": _d(10, 30), "known_at": _d(10, 30), "use_at": _d(10, 15)}, "expected": {"base_ok": False}})
add_fixture({"id": "O083-F1", "recipe": "O083", "inputs": {"open_px": 100, "prices": [{"t": _d(9, 30, 20), "price": 99}, {"t": _d(9, 32), "price": 102}], "as_of": _d(9, 32), "known_at": _d(9, 32), "use_at": _d(9, 32)}, "expected": {"no_through_open": False, "crossed_below": True}})
add_fixture({"id": "O083-F1b", "recipe": "O083", "inputs": {"open_px": 100, "prices": [{"t": _d(9, 30, 20), "price": 99}, {"t": _d(9, 40), "price": 102}], "as_of": _d(9, 31), "known_at": _d(9, 31), "use_at": _d(9, 31)}, "expected": {"crossed_below": True}})
add_fixture({"id": "O084-F1", "recipe": "O084", "inputs": {"label": "trend", "label_at": _d(16, 0), "ib_extension": 2, "known_at": _d(16, 0), "use_at": _d(10, 15)}, "expected": {"label_available": False, "base_ok": False}})
add_fixture({"id": "O084-F1b", "recipe": "O084", "inputs": {"label": "balance", "label_at": _d(10, 0), "ib_extension": 2, "known_at": _d(10, 0), "use_at": _d(10, 15)}, "expected": {"ib_extension": Decimal("2"), "trend_day": False}})
add_fixture({"id": "O085-F1", "recipe": "O085", "inputs": {"shape": "P", "author": "saint", "balance": [100, 105], "known_at": _d(10, 0), "use_at": _d(10, 5)}, "expected": {"entry_pass": False, "context_only": True}})
add_fixture({"id": "O085-F1b", "recipe": "O085", "inputs": {"shape": "P", "author": "sires", "directions": ["long", "short"], "known_at": _d(10, 0), "use_at": _d(10, 5)}, "expected": {"direction": None}})
add_fixture({"id": "O090-F1", "recipe": "O090", "inputs": {"lo": 100, "hi": 110, "poc": 106, "contact_at": _d(9, 40), "confirm_at": _d(9, 42), "decision_at": _d(9, 43), "far_edge_at": _d(10, 20), "known_at": _d(9, 20), "use_at": _d(9, 43)}, "expected": {"route_ok": True, "far_edge_replaces_confirm": False}})
add_fixture({"id": "O090-F1b", "recipe": "O090", "inputs": {"lo": 100, "hi": 110, "poc": 106, "contact_at": _d(9, 40), "decision_at": _d(9, 43), "known_at": _d(9, 20), "use_at": _d(9, 43)}, "expected": {"route_ok": None}})
add_fixture({"id": "O091-F1", "recipe": "O091", "inputs": {"ledge": 110, "ledge_known_at": _d(9, 30), "break_at": _d(9, 40), "departure_at": _d(9, 41), "retest_at": _d(9, 45), "defense_at": _d(9, 46), "entry_at": _d(9, 47), "known_at": _d(9, 30), "use_at": _d(9, 47)}, "expected": {"order_ok": True}})
add_fixture({"id": "O091-F1b", "recipe": "O091", "inputs": {"ledge": 110, "ledge_known_at": _d(9, 30), "break_at": _d(9, 40), "departure_at": _d(9, 41), "retest_at": _d(9, 45), "defense_at": _d(9, 46), "entry_at": _d(9, 44), "known_at": _d(9, 30), "use_at": _d(9, 44)}, "expected": {"order_ok": False, "base_ok": False}})
add_fixture({"id": "O091-F1c", "recipe": "O091", "inputs": {"ledge": 110, "other_band": True, "ledge_known_at": _d(9, 30), "break_at": _d(9, 40), "departure_at": _d(9, 41), "retest_at": _d(9, 45), "defense_at": _d(9, 46), "entry_at": _d(9, 47), "known_at": _d(9, 30), "use_at": _d(9, 47)}, "expected": {"base_ok": False}})
add_fixture({"id": "O092-F1", "recipe": "O092", "inputs": {"va_lo": 100, "va_hi": 110, "price": 108, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"inside": True, "automatic_acceptance": None}})
add_fixture({"id": "O092-F1b", "recipe": "O092", "inputs": {"va_lo": 100, "va_hi": 110, "price": 111, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"inside": False}})
add_fixture({"id": "O092-F1c", "recipe": "O092", "inputs": {"va_lo": 100, "va_hi": 110, "periods": [[102, 109], [101, 108]], "inside_convention": "whole_period", "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"period_inside": True}})
add_fixture({"id": "O092-F1d", "recipe": "O092", "inputs": {"va_lo": 100, "va_hi": 110, "periods": [[102, 109], [101, 111]], "inside_convention": "whole_period", "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"period_inside": False}})
add_fixture({"id": "O093-F1", "recipe": "O093", "inputs": {"va_lo": 100, "va_hi": 110, "older_poc": 115, "older_id": "old", "established_id": "est", "breakout_at": _d(9, 40), "tag_at": _d(9, 45), "tag_px": 115, "rejection_at": _d(9, 46), "rejection_from": "above", "decision_at": _d(9, 47), "side": "short", "target": 110, "known_at": _d(9, 20), "use_at": _d(9, 47)}, "expected": {"tagged": True, "distinct": True, "target": Decimal("110")}})
add_fixture({"id": "O093-F1b", "recipe": "O093", "inputs": {"va_lo": 100, "va_hi": 110, "older_poc": 115, "tag_px": 114, "decision_at": _d(9, 47), "known_at": _d(9, 20), "use_at": _d(9, 47)}, "expected": {"tagged": False, "route_ok": False}})
add_fixture({"id": "O093-F1c", "recipe": "O093", "inputs": {"va_lo": 100, "va_hi": 110, "older_poc": 115, "older_id": "same", "established_id": "same", "tag_at": _d(9, 45), "tag_px": 115, "known_at": _d(9, 20), "use_at": _d(9, 47)}, "expected": {"distinct": False, "base_ok": False}})
add_fixture({"id": "O095-F1", "recipe": "O095", "inputs": {"poc": 105, "failed_crosses": [_d(9, 40), _d(9, 45)], "passage_at": _d(9, 50), "retest_at": _d(9, 52), "as_of": _d(9, 45), "known_at": _d(9, 45), "use_at": _d(9, 45)}, "expected": {"failed_test_count": 2}})
add_fixture({"id": "O095-F1b", "recipe": "O095", "inputs": {"poc": 105, "failed_crosses": [_d(9, 40), _d(9, 45)], "retest_at": _d(9, 52), "known_at": _d(9, 50), "use_at": _d(9, 51)}, "expected": {"retest_available": False, "far_edge_is_passage": False}})
add_fixture({"id": "O096-F1", "recipe": "O096", "inputs": {"lo": 100, "hi": 110, "lower_at": _d(10, 0), "upper_at": _d(10, 40), "known_at": _d(10, 40), "use_at": _d(10, 40)}, "expected": {"duration_minutes": Decimal("40"), "rejected_over_30": False, "no_hold": None}})
add_fixture({"id": "O096-F1b", "recipe": "O096", "inputs": {"lo": 100, "hi": 110, "lower_at": _d(10, 0), "upper_at": _d(10, 40), "retest_at": _d(10, 45), "control_at": _d(10, 46), "entry_at": _d(10, 42), "known_at": _d(10, 40), "use_at": _d(10, 42)}, "expected": {"authorized": False, "base_ok": False}})
add_fixture({"id": "O097-F1", "recipe": "O097", "inputs": {"htf_side": "long", "ltf_side": "short", "thesis_at": _d(9, 20), "local_at": _d(9, 40), "known_at": _d(9, 20), "use_at": _d(9, 40)}, "expected": {"aligned": False}})
add_fixture({"id": "O097-F1b", "recipe": "O097", "inputs": {"htf_side": "long", "ltf_side": "long", "thesis_at": _d(9, 20), "local_at": _d(9, 45), "known_at": _d(9, 20), "use_at": _d(9, 46)}, "expected": {"aligned": True}})
add_fixture({"id": "O097-F1c", "recipe": "O097", "inputs": {"htf_side": "long", "ltf_side": "long", "thesis_at": _d(9, 20), "local_at": _d(9, 45), "thesis_died_at": _d(9, 44), "known_at": _d(9, 20), "use_at": _d(9, 46)}, "expected": {"aligned": False, "thesis_alive": False}})
add_fixture({"id": "O097-F1d", "recipe": "O097", "inputs": {"htf_side": "long", "ltf_side": "long", "thesis_at": _d(9, 20), "local_at": _d(9, 45), "known_at": _d(9, 20), "use_at": _d(9, 42)}, "expected": {"base_ok": False}})
add_fixture({"id": "O100-F1", "recipe": "O100", "inputs": {"bid_size_before": 10, "bid_size_after": 15, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"display_change": Decimal("5"), "consumed_and_replenished": False, "verified_hidden_reserve": None}})
add_fixture({"id": "O100-F1b", "recipe": "O100", "inputs": {"bid_size_before": 10, "bid_size_after": 15, "executed_sell": 4, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"execution_evidence": True, "verified_hidden_reserve": None}})
add_fixture({"id": "O102-F1", "recipe": "O102", "inputs": {"lifecycle": {"consumed": 6, "refresh": 8, "final_display": 12}, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"consumption": Decimal("6"), "refresh": Decimal("8"), "verified_replenishment": True}})
add_fixture({"id": "O102-F1b", "recipe": "O102", "inputs": {"first_display": 10, "last_display": 12, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"net": Decimal("2"), "verified_replenishment": None}})
add_fixture({"id": "O103-F1", "recipe": "O103", "inputs": {"q": Decimal("0.25"), "area_ticks": 2, "executed_total": 30, "displayed": 10, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"width": Decimal("0.50"), "verified_hidden_reserve": None, "participant_count": None}})
add_fixture({"id": "O104-F1", "recipe": "O104", "inputs": {"origin": 100, "q": Decimal("0.25"), "later_px": Decimal("100.75"), "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"reward_points": Decimal("0.75"), "reward_ticks": Decimal("3")}})
add_fixture({"id": "O104-F1b", "recipe": "O104", "inputs": {"origin": 100, "q": Decimal("0.25"), "later_px": 100, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"reward_ticks": Decimal("0")}})
add_fixture({"id": "O104-F1c", "recipe": "O104", "inputs": {"origin": 100, "origin_band": [100, Decimal("100.5")], "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"reward_points": None}})
add_fixture({"id": "O105-F1", "recipe": "O105", "inputs": {"trades": [{"side": "B", "size": 10}, {"side": "A", "size": 4}, {"side": "B", "size": 2}], "reference": 5, "reference_unit": "contracts", "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"cvd": Decimal("8"), "difference": Decimal("3")}})
add_fixture({"id": "O105-F1b", "recipe": "O105", "inputs": {"trades": [{"side": "B", "size": 10}, {"side": "A", "size": 4}, {"side": "B", "size": 2}], "reference": 100, "reference_unit": "price", "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"base_ok": False}})
add_fixture({"id": "O105-F1c", "recipe": "O105", "inputs": {"trades": [{"side": "B", "size": 10}, {"side": "A", "size": 4}, {"side": "B", "size": 2}, {"side": "N", "size": 3}], "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"cvd": None, "delta_interval": [Decimal("5"), Decimal("11")]}})
add_fixture({"id": "O106-F1", "recipe": "O106", "inputs": {"O": 100, "C": 101, "trades": [{"side": "B", "size": 4}, {"side": "A", "size": 10}], "known_at": _d(10, 1), "use_at": _d(10, 1)}, "expected": {"price_change": Decimal("1"), "delta": Decimal("-6"), "opposed_signs": True}})
add_fixture({"id": "O106-F1b", "recipe": "O106", "inputs": {"O": 100, "C": 100, "trades": [{"side": "B", "size": 4}, {"side": "A", "size": 10}], "known_at": _d(10, 1), "use_at": _d(10, 1)}, "expected": {"opposed_signs": False}})
add_fixture({"id": "O108-F1", "recipe": "O108", "inputs": {"candle_id": "K", "require_same_candle": True, "snapshots": [{"candle_id": "K", "poc": 100, "known_at": _d(10, 1)}, {"candle_id": "K", "poc": 101, "known_at": _d(10, 2)}], "known_at": _d(10, 2), "use_at": _d(10, 2)}, "expected": {"poc": Decimal("101"), "change": Decimal("1")}})
add_fixture({"id": "O108-F1b", "recipe": "O108", "inputs": {"candle_id": "K", "require_same_candle": True, "snapshots": [{"candle_id": "K", "poc": 100, "known_at": _d(10, 1)}, {"candle_id": "K", "poc": 101, "known_at": _d(10, 2)}], "known_at": _d(10, 2), "use_at": _d(10, 1, 30)}, "expected": {"poc": Decimal("100")}})
add_fixture({"id": "O108-F1c", "recipe": "O108", "inputs": {"candle_id": "K", "require_same_candle": True, "snapshots": [{"candle_id": "K", "poc": 100, "known_at": _d(10, 1)}, {"candle_id": "K+1", "poc": 101, "known_at": _d(10, 2)}], "known_at": _d(10, 2), "use_at": _d(10, 2)}, "expected": {"same_candle": False, "base_ok": False}})
add_fixture({"id": "O109-F1", "recipe": "O109", "inputs": {"q": Decimal("0.25"), "ratio_min": 4, "row_count": 3, "rows": [{"ask_px": 100, "ask": 40, "bid_px": Decimal("99.75"), "bid": 10}, {"ask_px": Decimal("100.25"), "ask": 60, "bid_px": 100, "bid": 10}, {"ask_px": Decimal("100.5"), "ask": 80, "bid_px": Decimal("100.25"), "bid": 20}], "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"ratios": [Decimal("4"), Decimal("6"), Decimal("4")], "qualifies": True, "stack_band": [Decimal("100"), Decimal("100.5")]}})
add_fixture({"id": "O109-F1b", "recipe": "O109", "inputs": {"q": Decimal("0.25"), "ratio_min": 4, "row_count": 3, "rows": [{"ask_px": 100, "ask": 40, "bid_px": Decimal("99.75"), "bid": 10}, {"ask_px": Decimal("100.5"), "ask": 80, "bid_px": Decimal("100.25"), "bid": 20}], "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"consecutive": False, "qualifies": False}})
add_fixture({"id": "O109-F1c", "recipe": "O109", "inputs": {"q": Decimal("0.25"), "rows": [{"ask_px": 100, "ask": 56, "bid_px": Decimal("99.75"), "bid": 5}], "printed_ask": 56, "printed_bid": 5, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"printed_ratio": Decimal("11.2")}})
add_fixture({"id": "O110-F1", "recipe": "O110", "inputs": {"B": 35, "S": 10, "rule": "350_of", "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"buy_multiple": Decimal("3.5"), "percent_of": Decimal("350"), "percent_more": Decimal("250"), "source_350_flag": True, "meets_more": False}})
add_fixture({"id": "O110-F1b", "recipe": "O110", "inputs": {"B": 35, "S": 10, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"source_350_flag": None}})
add_fixture({"id": "O111-F1", "recipe": "O111", "inputs": {"interval_s": 2, "n_prints": 6, "contracts": 15, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"prints_per_second": Decimal("3"), "contracts_per_second": Decimal("7.5"), "source_panel_value": None}})
add_fixture({"id": "O112-F1", "recipe": "O112", "inputs": {"bid": 100, "ask": Decimal("100.50"), "q": Decimal("0.25"), "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"spread_points": Decimal("0.50"), "spread_ticks": Decimal("2")}})
add_fixture({"id": "O112-F1b", "recipe": "O112", "inputs": {"bid": 100, "ask": Decimal("99.75"), "q": Decimal("0.25"), "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"crossed": True, "base_ok": False}})
add_fixture({"id": "O112-F1c", "recipe": "O112", "inputs": {"bid": 100, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"spread_points": None}})
add_fixture({"id": "O113-F1", "recipe": "O113", "inputs": {"from_px": 100, "to_px": 102, "from_at": _d(9, 59, 50), "to_at": _d(10, 0, 0), "known_at": _d(10, 0), "use_at": _d(10, 0)}, "expected": {"duration_seconds": Decimal("10"), "net_distance": Decimal("2"), "net_speed": Decimal("0.2"), "aggressive_arrival": None, "post_touch_included": False}})
add_fixture({"id": "O114-F1", "recipe": "O114", "inputs": {"sizes": [120, 85, 9], "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"digit_counts": [3, 2, 1], "declining": True, "source_classification": None}})
add_fixture({"id": "O114-F1b", "recipe": "O114", "inputs": {"sizes": [9, 85, 120], "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"digit_counts": [1, 2, 3], "declining": False}})
add_fixture({"id": "O115-F1", "recipe": "O115", "inputs": {"origin": 100, "q": Decimal("0.25"), "defense_at": _d(9, 40), "refresh_at": _d(9, 41), "exhaustion_at": _d(9, 42), "reward_at": _d(9, 43), "reward_px": Decimal("100.75"), "entry_at": _d(9, 43, 1), "entry": 101, "confirm_px": Decimal("100.75"), "known_at": _d(9, 43), "use_at": _d(9, 43, 1)}, "expected": {"reward_ticks": Decimal("3"), "entry_distance_ticks": Decimal("1"), "geometry_ok": True}})
add_fixture({"id": "O115-F1b", "recipe": "O115", "inputs": {"origin": 100, "q": Decimal("0.25"), "reward_px": Decimal("100.75"), "entry": 102, "confirm_px": Decimal("100.75"), "known_at": _d(9, 43), "use_at": _d(9, 43, 1)}, "expected": {"entry_distance_ticks": Decimal("5"), "geometry_ok": False}})
add_fixture({"id": "O116-F1", "recipe": "O116", "inputs": {"zone": [100, 101], "formed_at": _d(9, 40), "departure_at": _d(9, 45), "departure_price": 102, "touches": [{"t": _d(10, 0), "price": Decimal("100.75")}, {"t": _d(10, 0, 1), "price": Decimal("100.5")}, {"t": _d(10, 0, 2), "price": Decimal("100.75")}, {"t": _d(10, 0, 3), "price": 101}], "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"later_touches": 1, "automatic_zone": None}})
add_fixture({"id": "O116-F1b", "recipe": "O116", "inputs": {"known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"automatic_zone": None}})
add_fixture({"id": "O117-F1", "recipe": "O117", "inputs": {"cutoff": _d(9, 59), "priors": [{"id": "A", "end": _d(9, 40), "start": _d(9, 39), "defense_at": _d(9, 42)}, {"id": "B", "start": _d(9, 50), "end": _d(10, 5), "defense_at": _d(10, 5)}], "current_touch_id": "C", "current_touch_at": _d(10, 0), "current_success_at": _d(10, 10), "known_at": _d(10, 0), "use_at": _d(10, 0)}, "expected": {"prior_touch_count": 2, "resolved_defense_count": 1, "current_counts_as_prior": False}})
add_fixture({"id": "O118-F1", "recipe": "O118", "inputs": {"origin": [100, Decimal("100.5")], "failed_pushes": 2, "release_at": _d(9, 45), "failure_at": _d(9, 47), "entry_at": _d(9, 47), "required_stages": ["refill", "drive", "hold"], "known_at": _d(9, 40), "use_at": _d(9, 47)}, "expected": {"linked": True, "branch_ok": False, "later_high_replaces_origin": False}})
add_fixture({"id": "O119-F1", "recipe": "O119", "inputs": {"prior_failures": [{"id": "A", "t": _yd(10, 0)}, {"id": "B", "t": _yd(14, 0)}], "fail_at": _d(9, 40), "breakdown_at": _d(9, 45), "retest_at": _d(9, 50), "confirm_at": _d(9, 52), "entry_at": _d(9, 53), "known_at": _d(9, 52), "use_at": _d(9, 53)}, "expected": {"distinct_failures": 2, "order_ok": True}})
add_fixture({"id": "O119-F1b", "recipe": "O119", "inputs": {"prior_failures": [{"id": "A"}, {"id": "A"}], "fail_at": _d(9, 40), "breakdown_at": _d(9, 45), "retest_at": _d(9, 50), "confirm_at": _d(9, 52), "entry_at": _d(9, 53), "known_at": _d(9, 52), "use_at": _d(9, 53)}, "expected": {"distinct_failures": 1}})
add_fixture({"id": "O119-F1c", "recipe": "O119", "inputs": {"prior_failures": [{"id": "A"}, {"id": "B"}], "fail_at": _d(9, 40), "breakdown_at": _d(9, 45), "retest_at": _d(9, 50), "confirm_at": _d(9, 52), "entry_at": _d(9, 48), "known_at": _d(9, 48), "use_at": _d(9, 48)}, "expected": {"order_ok": False, "base_ok": False}})
add_fixture({"id": "O121-F1", "recipe": "O121", "inputs": {"band": 110, "arrival_at": _d(9, 40), "rejection_at": _d(9, 41), "added_at": _d(9, 42), "decision_at": _d(9, 43), "depth_ok": True, "known_at": _d(9, 30), "use_at": _d(9, 43)}, "expected": {"order_ok": True}})
add_fixture({"id": "O121-F1b", "recipe": "O121", "inputs": {"band": 110, "arrival_at": _d(9, 40), "rejection_at": _d(9, 41), "added_at": _d(9, 42), "decision_at": _d(9, 41, 30), "depth_ok": True, "known_at": _d(9, 30), "use_at": _d(9, 41, 30)}, "expected": {"base_ok": False}})
add_fixture({"id": "O121-F1c", "recipe": "O121", "inputs": {"band": 110, "arrival_at": _d(9, 40), "rejection_at": _d(9, 41), "decision_at": _d(9, 43), "need_added": True, "depth_ok": False, "known_at": _d(9, 30), "use_at": _d(9, 43)}, "expected": {"evidence": None}})
add_fixture({"id": "O122-F1", "recipe": "O122", "inputs": {"support": 100, "absorption_at": _d(9, 40), "reward_at": _d(9, 41), "reward_px": Decimal("100.75"), "return_at": _d(9, 42), "return_px": Decimal("100.50"), "defense_at": _d(9, 43), "decision_at": _d(9, 44), "cvd_reference": 1, "need_cvd": True, "known_at": _d(9, 44), "use_at": _d(9, 44)}, "expected": {"strict_reversal_sequence": True}})
add_fixture({"id": "O122-F1b", "recipe": "O122", "inputs": {"support": 100, "absorption_at": _d(9, 40), "reward_at": _d(9, 41), "defense_at": _d(9, 43), "decision_at": _d(9, 44), "complete_attempt": True, "need_cvd": False, "known_at": _d(9, 44), "use_at": _d(9, 44)}, "expected": {"strict_reversal_sequence": False}})
add_fixture({"id": "O122-F1c", "recipe": "O122", "inputs": {"support": 100, "absorption_at": _d(9, 40), "reward_at": _d(9, 41), "return_at": _d(9, 42), "defense_at": _d(9, 43), "decision_at": _d(9, 44), "need_cvd": True, "known_at": _d(9, 44), "use_at": _d(9, 44)}, "expected": {"strict_reversal_sequence": None}})
add_fixture({"id": "O123-F1", "recipe": "O123", "inputs": {"origin": 100, "confirm_px": Decimal("100.75"), "entry": 101, "q": Decimal("0.25"), "daily_r": -3, "daily_cap": -4, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"reward_ticks": Decimal("3"), "distance_ticks": Decimal("1"), "daily_stop_ok": True}})
add_fixture({"id": "O123-F1b", "recipe": "O123", "inputs": {"origin": 100, "confirm_px": Decimal("100.75"), "entry": 101, "q": Decimal("0.25"), "daily_r": -4, "daily_cap": -4, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"daily_stop_ok": False}})
add_fixture({"id": "O123-F1c", "recipe": "O123", "inputs": {"origin": 100, "confirm_px": Decimal("100.75"), "entry": Decimal("101.50"), "q": Decimal("0.25"), "daily_r": -3, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"distance_ticks": Decimal("3"), "geometry_ok": False, "size_halved_repairs": False}})
add_fixture({"id": "O124-F1", "recipe": "O124", "inputs": {"disagreement_candle": "K", "poc_candle": "K", "disagreement_at": _d(9, 40), "poc_at": _d(9, 41), "flow_at": _d(9, 42), "entry_at": _d(9, 43), "poc_from": 100, "poc_to": 101, "tape": True, "need_tape": True, "known_at": _d(9, 30), "use_at": _d(9, 43)}, "expected": {"same_candle": True, "route_ok": True}})
add_fixture({"id": "O124-F1b", "recipe": "O124", "inputs": {"disagreement_candle": "K", "poc_candle": "L", "disagreement_at": _d(9, 40), "poc_at": _d(9, 41), "tape": True, "known_at": _d(9, 30), "use_at": _d(9, 43)}, "expected": {"same_candle": False, "base_ok": False}})
add_fixture({"id": "O124-F1c", "recipe": "O124", "inputs": {"disagreement_candle": "K", "poc_candle": "K", "need_tape": True, "known_at": _d(9, 30), "use_at": _d(9, 43)}, "expected": {"route_ok": None}})
add_fixture({"id": "O125-F1", "recipe": "O125", "inputs": {"vwap": 100, "sigma": 2, "k": 2, "touch_at": _d(9, 40), "reject_at": _d(9, 41), "confirm_at": _d(9, 42), "entry_at": _d(9, 43), "target": 100, "later_vwap": 101, "known_at": _d(9, 20), "use_at": _d(9, 43)}, "expected": {"upper": Decimal("104"), "confirmation": True, "target": Decimal("100"), "later_rewrites_target": False}})
add_fixture({"id": "O125-F1b", "recipe": "O125", "inputs": {"vwap": 100, "sigma": 2, "k": 2, "touch_at": _d(9, 40), "known_at": _d(9, 20), "use_at": _d(9, 40)}, "expected": {"confirmation": None}})
add_fixture({"id": "O126-F1", "recipe": "O126", "inputs": {"catalyst_at": _d(9, 40), "release_at": _d(9, 41), "failure_at": _d(9, 42), "refill_at": _d(9, 43), "drive_at": _d(9, 45), "retest_at": _d(9, 47), "entry_at": _d(9, 48), "short_gamma": True, "cvd_reference": 1, "need_cvd": True, "known_at": _d(9, 48), "use_at": _d(9, 48)}, "expected": {"sequence_ok": True}})
add_fixture({"id": "O126-F1b", "recipe": "O126", "inputs": {"catalyst_at": _d(9, 40), "release_at": _d(9, 41), "failure_at": _d(9, 42), "refill_at": _d(9, 43), "drive_at": _d(9, 45), "retest_at": _d(9, 47), "entry_at": _d(9, 44), "short_gamma": True, "cvd_reference": 1, "known_at": _d(9, 44), "use_at": _d(9, 44)}, "expected": {"sequence_ok": False, "base_ok": False}})
add_fixture({"id": "O126-F1c", "recipe": "O126", "inputs": {"catalyst_at": _d(9, 40), "release_at": _d(9, 41), "failure_at": _d(9, 42), "refill_at": _d(9, 43), "drive_at": _d(9, 45), "retest_at": _d(9, 47), "entry_at": _d(9, 48), "short_gamma": True, "need_cvd": True, "known_at": _d(9, 48), "use_at": _d(9, 48)}, "expected": {"sequence_ok": None}})
add_fixture({"id": "O127-F1", "recipe": "O127", "inputs": {"entry": Decimal("101.25"), "stop": Decimal("99.75"), "side": "long", "r_multiple": 2, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"initial_risk": Decimal("1.5"), "r2": Decimal("104.25"), "r_in_1_to_3": True, "qualification": None, "automatic_selector": None}})
add_fixture({"id": "O128-F1", "recipe": "O128", "inputs": {"catalyst_at": _d(9, 40), "release_at": _d(9, 41), "first_pullback_at": _d(9, 43), "confirm_at": _d(9, 44), "entry_at": _d(9, 45), "later_failure_at": _d(10, 0), "known_at": _d(9, 45), "use_at": _d(9, 45)}, "expected": {"first_pullback": True, "no_prior_failure": True, "later_failure_invalidates": False}})
add_fixture({"id": "O128-F1b", "recipe": "O128", "inputs": {"first_pullback_at": _d(9, 43), "chosen_pullback_at": _d(9, 50), "entry_at": _d(9, 51), "known_at": _d(9, 51), "use_at": _d(9, 51)}, "expected": {"first_pullback": False}})
add_fixture({"id": "O129-F1", "recipe": "O129", "inputs": {"lo": 100, "hi": 110, "fail_at": _d(9, 40), "depart_at": _d(9, 42), "retest_at": _d(9, 45), "entry_at": _d(9, 46), "target": 103, "opposite_control": 103, "long_gamma": True, "known_at": _d(9, 46), "use_at": _d(9, 46)}, "expected": {"target": Decimal("103"), "target_is_balance_low": False, "target_is_prior_opposite_control": True, "requires_lift": False}})
add_fixture({"id": "O130-F1", "recipe": "O130", "inputs": {"lo": 109, "hi": 110, "prior_defense_at": _d(9, 30), "fresh_defense_at": _d(9, 47), "entry_at": _d(9, 48), "known_at": _d(9, 47), "use_at": _d(9, 48)}, "expected": {"short_control": True, "old_defense_keeps_control": False}})
add_fixture({"id": "O130-F1b", "recipe": "O130", "inputs": {"lo": 109, "hi": 110, "prior_defense_at": _d(9, 30), "fresh_defense_at": _d(9, 47), "buyers_defend_at": _d(9, 46), "entry_at": _d(9, 48), "known_at": _d(9, 47), "use_at": _d(9, 48)}, "expected": {"short_control": False}})
add_fixture({"id": "O131-F1", "recipe": "O131", "inputs": {"micro_lo": 100, "micro_hi": 102, "complete_at": _d(9, 40), "entry": 103, "stop": Decimal("99.75"), "target": 120, "side": "long", "known_at": _d(9, 20), "use_at": _d(9, 42)}, "expected": {"stop_below_opposite": True, "target": Decimal("120")}})
add_fixture({"id": "O131-F1b", "recipe": "O131", "inputs": {"micro_lo": 100, "micro_hi": 102, "complete_at": _d(10, 0), "entry": 103, "stop": Decimal("99.75"), "target": 120, "known_at": _d(10, 0), "use_at": _d(9, 42)}, "expected": {"base_ok": False}})
add_fixture({"id": "O132-F1", "recipe": "O132", "inputs": {"entry": 100, "stop": 90, "target": Decimal("106.9"), "later_stop": 95, "later_target": Decimal("109.15"), "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"ratio": Decimal("0.69"), "later_ratio": Decimal("1.83"), "original_risk": Decimal("10"), "automatic_trailing": None}})
add_fixture({"id": "O133-F1", "recipe": "O133", "inputs": {"entry_at": _d(9, 40), "confirm_at": _d(9, 45), "loss_at": _d(9, 42), "known_at": _d(9, 39), "use_at": _d(9, 40)}, "expected": {"deliberate_early": True, "confirmed_branch": False, "thesis_killed_by_loss_alone": False, "automatic_selector": None}})
add_fixture({"id": "O134-F1", "recipe": "O134", "inputs": {"tests": [_d(9, 30), _d(9, 45), _d(10, 0)], "inside_rows": [1, 2, 3], "stopped_out": True, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"ordinal": 3, "inside_rows_are_one_test": True, "in_cohort": True, "universal_third_touch": False}})
add_fixture({"id": "O135-F1", "recipe": "O135", "inputs": {"resistance": 110, "resistance_at": _d(12, 0), "entry_at": _d(14, 5), "known_at": _d(12, 0), "use_at": _d(14, 5)}, "expected": {"case_ok": True, "automatic_full_trigger": None}})
add_fixture({"id": "O135-F1b", "recipe": "O135", "inputs": {"resistance": 110, "resistance_at": _d(14, 30), "entry_at": _d(14, 5), "known_at": _d(14, 30), "use_at": _d(14, 5)}, "expected": {"base_ok": False}})
add_fixture({"id": "O137-F1", "recipe": "O137", "inputs": {"v1": {"A": True, "B": True, "T": 1}, "v2": {"A": True, "B": True, "T": 2}, "features": ["A", "B"], "known_at": _d(9, 0), "use_at": _n(9, 0)}, "expected": {"changed_fields": ["T"], "count": 1, "one_variable": True}})
add_fixture({"id": "O137-F1b", "recipe": "O137", "inputs": {"v1": {"A": True, "B": True, "C": False, "T": 1}, "v2": {"A": True, "B": True, "C": True, "T": 2}, "known_at": _d(9, 0), "use_at": _n(9, 0)}, "expected": {"count": 2, "one_variable": False}})
add_fixture({"id": "O138-F1", "recipe": "O138", "inputs": {"close": 99, "close_at": _d(10, 0), "death_close": 100, "recover_px": 102, "stopped_at": _d(9, 50), "known_at": _d(10, 0), "use_at": _d(10, 10)}, "expected": {"first_death": _d(10, 0), "alive": False, "revived": False, "stop_kills_thesis": False}})
add_fixture({"id": "O138-F1b", "recipe": "O138", "inputs": {"missing_news": True, "known_at": _d(9, 30), "use_at": _d(9, 40)}, "expected": {"alive": None}})
add_fixture({"id": "O143-F1", "recipe": "O143", "inputs": {"high": 110, "protected_high": 110, "high_priced_at": _d(9, 40), "confirm_at": _d(9, 50), "known_at": _d(9, 50), "use_at": _d(9, 51)}, "expected": {"protected_high": Decimal("110"), "usable": True}})
add_fixture({"id": "O143-F1b", "recipe": "O143", "inputs": {"high": 110, "confirm_at": _d(9, 50), "known_at": _d(9, 50), "use_at": _d(9, 45)}, "expected": {"usable": False, "base_ok": False}})
add_fixture({"id": "O144-F1", "recipe": "O144", "inputs": {"prior_exit_at": _d(9, 45), "return_at": _d(9, 50), "fresh_confirm_at": _d(9, 52), "entry_at": _d(9, 53), "same_thesis_band": True, "daily_r": -3, "known_at": _d(9, 53), "use_at": _d(9, 53)}, "expected": {"fresh": True, "freshness_ok": True}})
add_fixture({"id": "O144-F1b", "recipe": "O144", "inputs": {"prior_exit_at": _d(9, 45), "return_at": _d(9, 50), "reused_confirm_at": _d(9, 40), "entry_at": _d(9, 53), "same_thesis_band": True, "daily_r": -3, "known_at": _d(9, 53), "use_at": _d(9, 53)}, "expected": {"freshness_ok": False}})
add_fixture({"id": "O144-F1c", "recipe": "O144", "inputs": {"prior_exit_at": _d(9, 45), "return_at": _d(9, 50), "fresh_confirm_at": _d(9, 52), "entry_at": _d(9, 53), "same_thesis_band": True, "daily_r": -4, "daily_cap": -4, "known_at": _d(9, 53), "use_at": _d(9, 53)}, "expected": {"blocked": True, "fresh": False}})
add_fixture({"id": "O146-F1", "recipe": "O146", "inputs": {"eligible": ["A", "B", "C"], "journal": {"A": "win", "C": "win"}, "known_at": _d(16, 0), "use_at": _d(16, 1)}, "expected": {"accounted": 2, "of": 3, "missing": ["B"], "completeness": False}})
add_fixture({"id": "O146-F1b", "recipe": "O146", "inputs": {"eligible": ["A", "B", "C"], "journal": {"A": "win", "B": "loss", "C": "win"}, "reason_at": _d(10, 0), "entry_at": _d(9, 40), "known_at": _d(16, 0), "use_at": _d(16, 1)}, "expected": {"completeness": True, "later_explanation": True}})
add_fixture({"id": "O147-F1", "recipe": "O147", "inputs": {"objects": [{"root": "ES", "edge": 5000}, {"root": "NQ", "edge": 20000}, {"root": "YM", "edge": 40000}], "peer_test_at": _d(9, 40), "decision_at": _d(9, 42), "known_at": _d(9, 42), "use_at": _d(9, 42)}, "expected": {"native_count": 3, "reread_ok": True, "edge_inequality_relevant": False}})
add_fixture({"id": "O147-F1b", "recipe": "O147", "inputs": {"objects": [{"root": "ES"}, {"root": "NQ"}, {"root": "YM"}], "peer_fill_at": _d(9, 45), "decision_at": _d(9, 42), "known_at": _d(9, 42), "use_at": _d(9, 42)}, "expected": {"peer_fill_revises": False}})
add_fixture({"id": "O148-F1", "recipe": "O148", "inputs": {"eligible": 10, "selected": 6, "orders": 6, "filled": 4, "known_at": _d(16, 0), "use_at": _d(16, 1)}, "expected": {"eligible": 10, "selected": 6, "orders": 6, "filled": 4, "unselected": 4, "pairable": False}})
add_fixture({"id": "O148-F1b", "recipe": "O148", "inputs": {"eligible": 10, "selected": 6, "orders": 4, "filled": 4, "known_at": _d(16, 0), "use_at": _d(16, 1)}, "expected": {"missing_orders": 2, "completeness": False}})
add_fixture({"id": "O152-F1", "recipe": "O152", "inputs": {"r_unit": 32, "target_outcome": 95, "stop_outcome": -34, "round_trip_cost_ticks": 1, "stop_slippage_ticks": 1, "gross_target_ticks": 96, "gross_stop_ticks": 32, "tick_value": 2, "quantity": 3, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"target_r": Decimal("2.96875"), "stop_r": Decimal("-1.0625"), "round_trip_cost": Decimal("6")}})
add_fixture({"id": "O152-F1b", "recipe": "O152", "inputs": {"r_unit": 32, "target_outcome": 95, "quantity": 3, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"round_trip_cost": None}})
add_fixture({"id": "O153-F1", "recipe": "O153", "inputs": {"wins": 5, "losses": 5, "mean_win": 2, "mean_loss": -1, "reported_ev": Decimal("0.5"), "known_at": _d(16, 0), "use_at": _d(16, 1)}, "expected": {"win_rate": Decimal("0.5"), "ev": Decimal("0.5"), "profit_factor": Decimal("2"), "consistent": True, "from_market_prices": False}})
add_fixture({"id": "O153-F1b", "recipe": "O153", "inputs": {"wins": 5, "losses": 5, "mean_win": 2, "mean_loss": -1, "reported_ev": 1, "known_at": _d(16, 0), "use_at": _d(16, 1)}, "expected": {"consistent": False}})
add_fixture({"id": "O164-F1", "recipe": "O164", "inputs": {"volume": 100, "response": 1, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"response_per_volume": Decimal("0.01"), "automatic_class": None}})
add_fixture({"id": "O164-F1b", "recipe": "O164", "inputs": {"volume": 100, "response": 0, "known_at": _d(10, 0), "use_at": _d(10, 1)}, "expected": {"absorption": None, "source_efficiency_class": None}})
