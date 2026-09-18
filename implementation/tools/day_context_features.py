#!/usr/bin/env python3
"""The day and the moment a trade is decided in, as the two authors describe
them: selection features, every one a fact known at the row's ``decision_at``.
``build_selection_dataset.py`` adds them to every row beside the level
features of ``grading_features.py``.

Jumbo (Time-Based Ranges Framework; page in brackets):

  range size            the 6-9 range in percent of price and his size bin
                        ("the size of the ONS range will give you a hint
                        whether we will have a false breakout or just a
                        breakout", [12], range table [13])
  overnight             the overnight range in percent of price ("extended
                        overnight range", [12], [24]); which prior extremes
                        the overnight purged and which edges are still drawn
                        ("every significant overnight liquidity has been
                        purged", [12]; the purge confluence, [11])
  open location         the 09:00 and the RTH open against prior value and
                        the prior session (PD RTH Range+, [32]-[34]), the
                        day's classification and whether the trade is on the
                        side of the day's direction
  value layer           the width of the 06:00-09:30 value area in percent
  news week             his low / moderate / risk-on table ([22]) and the
                        release of the day; the 10:00 releases that delay
                        cycle 2 ([18]) are NOT on disk: recorded as absent
  sister index          NQ against ES overnight ([12] scenario 2)
  the clock             his windows: the open to 09:40, the 09:40-09:50
                        reversal window, to 10:00, to 12:00, lunch, PM ([8],
                        [15]-[19], [36])
  sessions correlation  for a decision after 12:00, the morning's range
                        against the 6-9 range and its close within it ("AM
                        Consolidation -> PM Expansion", [36])
  volume signature      the trigger minute's volume against the 14 before it
                        and its body's share of its range (Absorption zone+:
                        "small body with high volume", [31], [35]; "Volume
                        Divergence", [37])

Green Bird: the day model, the bias of the overnight and whether the trade is
with it, the overnight span in percent of price, the open held beyond both
session boxes, and the same clock and volume-signature reads.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

MINUTE = 60 * 1_000_000_000
WINDOWS = (("pre_open", "00:00", "09:30"), ("open_drive", "09:30", "09:40"), ("reversal_window", "09:40", "09:50"), ("to_ten", "09:50", "10:00"), ("cycle_two", "10:00", "12:00"), ("lunch", "12:00", "13:00"), ("pm", "13:00", "16:00"))


def _f(value) -> float | None:
    return None if value is None else float(value)


def _pct(width, price) -> float | None:
    if width is None or price in (None, 0):
        return None
    return round(float(width) / float(price) * 100, 4)


def _span(market, start: int, end: int) -> dict[str, float] | None:
    rows = [r for r in (market.bars(start, end, 60) or []) if r.get("H") is not None and r.get("L") is not None]
    if not rows:
        return None
    closes = [r for r in rows if r.get("C") is not None]
    return {"high": max(float(r["H"]) for r in rows), "low": min(float(r["L"]) for r in rows), "close": None if not closes else float(closes[-1]["C"])}


def jumbo_day(market) -> dict[str, tuple[Any, int]]:
    """Jumbo's reads of the day, each with the time it is KNOWN: a row decided before that
    time does not get it (a London trade at 03:00 knows neither the 6-9 range nor the open)."""
    from trading_research.research.method_pack.profile_nodes import shape
    from trading_research.research.rule_discovery.source_adapters import jumbo as jj

    context = jj.session_context(market)
    read, box = context.get("read") or {}, context.get("box")
    inputs = read.get("inputs") or {}
    price = context.get("price_at_0900")
    size = context.get("range_class") or {}
    start, six, half_eight, nine, open_ns = int(market.at("18:00", -1)), int(market.at("06:00")), int(market.at("08:30")), int(market.at("09:00")), int(market.at("09:30"))
    night = _span(market, start, nine)
    value = jj.box_geometry(market, "ny_value")
    prior_value = context.get("prior_value") or {}
    news, sister = context.get("news_week") or {}, context.get("sister_index") or {}
    out: dict[str, tuple[Any, int]] = {}

    def known(at: int, **fields) -> None:
        for name, item in fields.items():
            out[name] = (item, at)

    known(
        start,
        day_news_tier=news.get("tier"),
        day_news_release=";".join(news.get("release_today") or []) or None,
        day_ten_am_release=None,  # [18]: no 10:00 release calendar on disk; absent, not False
    )
    night_width = None if night is None else night["high"] - night["low"]
    night_rows = [r for r in (market.bars(start, nine, 60) or []) if r.get("O") is not None]
    night_open = float(night_rows[0]["O"]) if night_rows else None
    known(
        nine,
        day_range_pct=_f(size.get("pct")),
        day_range_bin=size.get("bin"),
        day_big_range=read.get("big_range"),
        day_overnight_range_pct=_pct(night_width, price),
        day_overnight_vs_box=None if not night_width or box is None or not box["width"] else round(night_width / float(box["width"]), 3),
        # "Balanced - imbalanced overnight matters" (JR p.33): how much of the overnight range was net travel, and where it closed
        day_overnight_efficiency=None if not night_width or night_open is None or night["close"] is None else round(abs(night["close"] - night_open) / night_width, 3),
        day_overnight_close_position=None if not night_width or night["close"] is None else round((night["close"] - night["low"]) / night_width, 3),
        day_overnight_purged_high=inputs.get("overnight_purged_high"),
        day_overnight_purged_low=inputs.get("overnight_purged_low"),
        day_edges_still_drawn=len(inputs.get("edges_still_drawn") or []),
        day_open_location=inputs.get("open_location"),
        day_sister_divergence_high=sister.get("divergence_at_high"),
        day_sister_divergence_low=sister.get("divergence_at_low"),
        day_nq_minus_es_overnight_pct=sister.get("nq_minus_es_overnight_pct"),
    )
    if box is not None:
        low, high, width = float(box["low"]), float(box["high"]), float(box["width"])
        # "Based on 3 different profiles is possible to anticipate single/double breaks ... Volume never lies"; his
        # chart prints "Profile Type b / Direction Bearish" (JR p.22): the 6-9 range's own profile
        profile = market.profile(six, nine) if callable(getattr(market, "profile", None)) else None
        poc = None if not profile or profile.get("poc") is None else float(profile["poc"])
        early, late = _span(market, six, half_eight), _span(market, half_eight, nine)
        vah, val = _f(prior_value.get("vah")), _f(prior_value.get("val"))
        known(
            nine,
            day_box_profile_shape=None if not profile else shape(profile),
            day_box_poc_position=None if poc is None or not width else round((poc - low) / width, 3),
            # "usually present on 8:30 red folder news" (TBR p.24): how much of the range the last half hour made
            day_0830_expansion=None if early is None or late is None or early["high"] <= early["low"] else round((late["high"] - late["low"]) / (early["high"] - early["low"]), 3),
            # "RTH open location in relation to previous day value/range and the current day 6-9" (JR p.34)
            day_box_inside_prior_value=None if vah is None or val is None or not width else round(max(0.0, min(high, vah) - max(low, val)) / width, 3),
        )
        rth_open = _f(context.get("rth_open"))
        known(open_ns, day_rth_open_in_box=None if rth_open is None or not width else round((rth_open - low) / width, 3))
    known(
        open_ns,
        day_rth_open_location=inputs.get("rth_open_location"),
        day_open_inside_value=read.get("open_inside_value"),
        day_classification=read.get("classification"),
        day_primary_play=read.get("primary_play"),
        day_aligned=read.get("aligned"),
        day_trend_direction=read.get("trend_direction"),
        day_value_range_pct=None if value is None else _pct(value["width"], price),
    )
    known(nine, day_classification_pre_open=read.get("classification_pre_open"))
    return out


def green_day(market) -> dict[str, Any]:
    from trading_research.research.rule_discovery.source_adapters import green_b02 as gb

    read = gb.session_read(market)
    inputs = read.get("inputs") or {}
    return {
        "day_model": read.get("day_model"),
        "day_primary_play": read.get("primary_play"),
        "day_bias": read.get("bias"),
        "day_overnight_range_pct": _pct(inputs.get("overnight_span"), inputs.get("cash_open")),
        "day_open_beyond_session_boxes": inputs.get("open_beyond_session_boxes"),
        "day_weekly_level_reachable": inputs.get("weekly_level_reachable"),
        "day_overnight_events": len(read.get("overnight_events") or []),
    }


def _big_orders(market):
    """The day's big aggressive orders (his BigTrades floors: "a 100 threshold on NQ during NY and 75 during
    London", JR p.50), once per market: (time, sign, lots, low, high) arrays, or None without tape."""
    cached = getattr(market, "_context_big_orders", "missing")
    if cached != "missing":
        return cached
    from trading_research.research.method_pack import trade_tape as tt

    result = None
    tape = tt.trades_between(market.data_root, int(market.instrument_id), int(market.start), int(market.end)) if getattr(market, "data_root", None) else None
    if tape is not None:
        ot, osg, lots, olo, ohi = tt.aggressive_orders(*tape)
        floor = [75 if int(x) < int(market.at("09:30")) else 100 for x in ot]
        keep = lots >= floor
        result = (ot[keep], osg[keep], lots[keep], olo[keep], ohi[keep])
    setattr(market, "_context_big_orders", result)
    return result


def moment(market, *, at_ns: int, side: str, day: dict[str, Any], box: dict | None = None, level: float | None = None, evrange: dict | None = None) -> dict[str, Any]:
    """What is known at the decision about the clock, the range's edges, the morning behind an afternoon
    trade, the volume of the minute that triggered it and the big orders at the level."""
    out: dict[str, Any] = {}
    window = None
    for name, start, end in WINDOWS:
        if int(market.at(start)) <= at_ns < int(market.at(end)):
            window = name
    out["clock_window"] = window or ("overnight" if at_ns < int(market.at("09:30")) else "after_close")
    direction = day.get("day_trend_direction") or day.get("day_bias")
    out["side_with_day_direction"] = None if direction not in ("long", "short") else direction == side
    out["side_on_sister_divergence"] = None if day.get("day_sister_divergence_high") is None else bool(day["day_sister_divergence_high"] if side == "short" else day["day_sister_divergence_low"])
    nine, open_ns, noon = int(market.at("09:00")), int(market.at("09:30")), int(market.at("12:00"))
    box_width = None if box is None else float(box["width"])
    if box is not None and at_ns > nine:
        # "first stage of the move taking both high and low of the range before the full reversal between
        # 9:40-9:50" (JR p.20): which edges of the 6-9 range have already traded through, and how often
        rows = [r for r in (market.bars(nine, at_ns, 60) or []) if int(r.get("known_at") or r["end"]) <= at_ns and r.get("H") is not None]
        low, high = float(box["low"]), float(box["high"])
        above = [int(r["start"]) for r in rows if float(r["H"]) > high]
        below = [int(r["start"]) for r in rows if float(r["L"]) < low]
        out["box_edges_broken"] = "both" if above and below else ("high" if above else ("low" if below else "none"))
        out["minutes_since_first_edge_break"] = None if not (above or below) else round((at_ns - min(above + below)) / MINUTE, 1)
        if rows and evrange and evrange.get("upper") is not None and evrange.get("lower") is not None and float(evrange["upper"]) > float(evrange["lower"]):
            # "am vol expected range" (JR p.33): how much of the expected morning is already spent
            spent = max(float(r["H"]) for r in rows) - min(float(r["L"]) for r in rows)
            out["range_spent_vs_expected"] = round(spent / (float(evrange["upper"]) - float(evrange["lower"])), 3)
            if level is not None:
                out["level_beyond_expected_range"] = bool(level > float(evrange["upper"]) or level < float(evrange["lower"]))
    if at_ns >= int(market.at("09:45")):
        # "AM is completely off-limits" on a choppy open (TBR p.23): the first quarter hour's net travel against its path
        first = [r for r in (market.bars(open_ns, int(market.at("09:45")), 60) or []) if r.get("C") is not None and r.get("O") is not None]
        path = sum(abs(float(r["C"]) - float(r["O"])) for r in first)
        if first and path > 0:
            out["open_efficiency_15m"] = round(abs(float(first[-1]["C"]) - float(first[0]["O"])) / path, 3)
    if at_ns >= noon:
        morning = _span(market, open_ns, noon)
        if morning is not None:
            width = morning["high"] - morning["low"]
            out["am_range_vs_box"] = None if not box_width else round(width / box_width, 3)
            out["am_close_position"] = None if not width or morning["close"] is None else round((morning["close"] - morning["low"]) / width, 3)
    rows = [r for r in (market.bars(at_ns - 15 * MINUTE, at_ns, 60) or []) if int(r.get("known_at") or r["end"]) <= at_ns]
    if len(rows) >= 5:
        last, before = rows[-1], rows[:-1]
        volumes = [float(r["V"]) for r in before if r.get("V") is not None]
        if last.get("V") is not None and volumes and sum(volumes) > 0:
            out["trigger_relative_volume"] = round(float(last["V"]) / (sum(volumes) / len(volumes)), 3)
        if all(last.get(k) is not None for k in ("O", "H", "L", "C")) and float(last["H"]) > float(last["L"]):
            out["trigger_body_share"] = round(abs(float(last["C"]) - float(last["O"])) / (float(last["H"]) - float(last["L"])), 3)
    big = _big_orders(market) if level is not None else None
    if big is not None:
        # "aggressive buyers getting rekt right at session highs" (JR): big orders near the level in the last ten
        # minutes, split by whether they pushed INTO the level (against the fade) or with the trade
        ot, osg, lots, olo, ohi = big
        near = (ot >= at_ns - 10 * MINUTE) & (ot < at_ns) & (ohi >= level - 10) & (olo <= level + 10)
        sign = 1 if side == "long" else -1
        out["big_orders_against_trade_10m"] = int((osg[near] == -sign).sum())
        out["big_contracts_against_trade_10m"] = int(lots[near][osg[near] == -sign].sum())
        out["big_orders_with_trade_10m"] = int((osg[near] == sign).sum())
    return out


def context_rows(family: str, market, rows: list[dict]) -> list[dict]:
    """``rows`` with the day and moment context added (family 'JJ' or 'GB'). A day read given as
    (value, known_at) reaches only the rows decided at or after it was known."""
    day = jumbo_day(market) if family == "JJ" else green_day(market)
    box = evrange = None
    if family == "JJ":
        from trading_research.research.rule_discovery.source_adapters import jumbo as jj

        context = jj.session_context(market)
        box, evrange = context.get("box"), context.get("evrange")
    out = []
    for row in rows:
        at = int(row["decision_at"])
        seen = {name: (item[0] if at >= item[1] else None) if isinstance(item, tuple) else item for name, item in day.items()}
        level = row.get("reference_px")
        out.append({**row, **seen, **moment(market, at_ns=at, side=str(row["side"]), day=seen, box=box, level=None if level is None else float(level), evrange=evrange)})
    return out
