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


def jumbo_day(market) -> dict[str, Any]:
    from trading_research.research.rule_discovery.source_adapters import jumbo as jj

    context = jj.session_context(market)
    read, box = context.get("read") or {}, context.get("box")
    inputs = read.get("inputs") or {}
    price = context.get("price_at_0900")
    size = context.get("range_class") or {}
    night = _span(market, int(market.at("18:00", -1)), int(market.at("09:00")))
    value = jj.box_geometry(market, "ny_value")
    news, sister = context.get("news_week") or {}, context.get("sister_index") or {}
    return {
        "day_range_pct": _f(size.get("pct")),
        "day_range_bin": size.get("bin"),
        "day_big_range": read.get("big_range"),
        "day_overnight_range_pct": None if night is None else _pct(night["high"] - night["low"], price),
        "day_overnight_vs_box": None if night is None or box is None or not box["width"] else round((night["high"] - night["low"]) / float(box["width"]), 3),
        "day_overnight_purged_high": inputs.get("overnight_purged_high"),
        "day_overnight_purged_low": inputs.get("overnight_purged_low"),
        "day_overnight_balanced": inputs.get("overnight_balanced"),
        "day_edges_still_drawn": len(inputs.get("edges_still_drawn") or []),
        "day_open_location": inputs.get("open_location"),
        "day_rth_open_location": inputs.get("rth_open_location"),
        "day_open_inside_value": read.get("open_inside_value"),
        "day_classification": read.get("classification"),
        "day_primary_play": read.get("primary_play"),
        "day_aligned": read.get("aligned"),
        "day_trend_direction": read.get("trend_direction"),
        "day_value_range_pct": None if value is None else _pct(value["width"], price),
        "day_news_tier": news.get("tier"),
        "day_news_release": ";".join(news.get("release_today") or []) or None,
        "day_ten_am_release": None,  # [18]: no 10:00 release calendar on disk; absent, not False
        "day_sister_divergence_high": sister.get("divergence_at_high"),
        "day_sister_divergence_low": sister.get("divergence_at_low"),
        "day_nq_minus_es_overnight_pct": sister.get("nq_minus_es_overnight_pct"),
    }


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


def moment(market, *, at_ns: int, side: str, day: dict[str, Any], box_width: float | None = None) -> dict[str, Any]:
    """What is known at the decision about the clock, the morning behind an
    afternoon trade, and the volume of the minute that triggered it."""
    out: dict[str, Any] = {}
    window = None
    for name, start, end in WINDOWS:
        if int(market.at(start)) <= at_ns < int(market.at(end)):
            window = name
    out["clock_window"] = window or ("overnight" if at_ns < int(market.at("09:30")) else "after_close")
    direction = day.get("day_trend_direction") or day.get("day_bias")
    out["side_with_day_direction"] = None if direction not in ("long", "short") else direction == side
    out["side_on_sister_divergence"] = None if day.get("day_sister_divergence_high") is None else bool(day["day_sister_divergence_high"] if side == "short" else day["day_sister_divergence_low"])
    noon = int(market.at("12:00"))
    if at_ns >= noon:
        morning = _span(market, int(market.at("09:30")), noon)
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
    return out


def context_rows(family: str, market, rows: list[dict]) -> list[dict]:
    """``rows`` with the day and moment context added (family 'JJ' or 'GB')."""
    day = jumbo_day(market) if family == "JJ" else green_day(market)
    box_width = None
    if family == "JJ":
        from trading_research.research.rule_discovery.source_adapters import jumbo as jj

        box = jj.session_context(market).get("box")
        box_width = None if box is None else float(box["width"])
    out = []
    for row in rows:
        out.append({**row, **day, **moment(market, at_ns=int(row["decision_at"]), side=str(row["side"]), day=day, box_width=box_width)})
    return out
