"""Green Bird's drawn lines on the native tape, against what his charts print.

Every expected value is a label he printed on a chart (context pass
2026-09-18, sections C and D); MNQ labels sit within a point or two of NQ.
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from trading_research.research.rule_discovery.source_adapters import green_b02 as gb
from trading_research.research.rule_discovery.source_adapters.common import load_source_market
from trading_research.research.rule_discovery.source_adapters.session_levels import prior_sessions

LABEL_TOLERANCE = Decimal("3")  # a chart label read to the point, MNQ against NQ


def _refs(market):
    refs, omissions = gb.session_references(market)
    return {ref["kind"]: ref for ref in refs}, omissions


@pytest.mark.parametrize(
    "day, printed_pdh, source",
    [
        ("2026-08-27", Decimal("29437"), "p38_x62 / p56_x119: 'PDH' label about 29,437; both ladders end 29,425.50 under it"),
        ("2026-04-23", Decimal("27137"), "p45_x79: the PDH line starts at 18:00 at about 27,137"),
    ],
)
def test_c1_prior_day_high_is_the_globex_day_to_1700(day, printed_pdh, source):
    market = load_source_market(day)
    refs, omissions = _refs(market)
    prior = refs["prior_day"]
    assert prior["scope"] == "globex_day_1800_1700", omissions
    assert abs(prior["high"] - printed_pdh) <= LABEL_TOLERANCE, (prior["high"], source)
    # negative control: the 18:00-16:00 session high (Jumbo's span, unchanged)
    # is NOT his line on either day -- the closing hour made the high
    session_high = prior_sessions(market, 1)[0]["high"]
    assert abs(session_high - printed_pdh) > Decimal("40"), session_high
    assert not [row for row in omissions if row.get("reason") == "globex_closing_hour_unavailable"]


def test_c1_a_missing_closing_hour_is_recorded_not_hidden(monkeypatch):
    from trading_research.research.rule_discovery.source_adapters import session_levels

    market = load_source_market("2026-08-27")
    monkeypatch.setattr(session_levels, "minute_span", lambda *a, **k: None)
    span, omissions = session_levels.globex_prior_day(market)
    assert span["scope"] == "cme_session_1800_1600" and span["high"] == Decimal("29368.25")
    assert [row["reason"] for row in omissions] == ["globex_closing_hour_unavailable"]


@pytest.mark.parametrize(
    "day, edge, printed, source",
    [
        ("2025-11-26", "high", Decimal("25360"), "p43_x73 prints PWH at about 25,360 (made Monday 11-17 03:57, outside RTH)"),
        ("2025-11-19", "low", Decimal("24625"), "p31_x51: long 24,625.00 'Sweep of previous weeks low and reclaim'"),
    ],
)
def test_c2_prior_week_is_the_whole_weekly_candle(day, edge, printed, source):
    """'from the opening to the closing of the weekly candle' (GB p.32)."""
    refs, omissions = _refs(load_source_market(day))
    week = refs["prior_week"]
    assert week["scope"] == "weekly_candle_sun1800_fri1700", omissions
    assert abs(week[edge] - printed) <= LABEL_TOLERANCE, (week[edge], source)


def test_c2_rth_only_week_misses_his_line_and_a_fallback_is_recorded(monkeypatch):
    """Negative control: with the candle unavailable the RTH windows stand in,
    labelled and recorded, and they do not reproduce his 25,360 (25,310.00)."""
    monkeypatch.setattr(gb, "weekly_candle", lambda market: {"unavailable": "week_not_wholly_on_this_contract"})
    refs, omissions = _refs(load_source_market("2025-11-26"))
    week = refs["prior_week"]
    assert week["scope"] == "rth_0930_1600"
    assert abs(week["high"] - Decimal("25360")) > Decimal("40"), week["high"]
    assert "weekly_candle_unavailable" in [row.get("reason") for row in omissions]


def _tape_week_of_2025_07_27():
    """Tape facts recomputed from the raw one-minute bars, not from the adapter:
    the Sunday 18:00 open, the Friday 15:59 close and the first minute after the
    open that traded at that close."""
    import pandas as pd
    import pyarrow.parquet as pq

    frame = pq.read_table("/workspace/data/quantpad/cme__nq-continuous-futures__ohlcv-1m/2025.parquet").to_pandas()
    frame.index = pd.to_datetime(frame["t"], unit="ms", utc=True).dt.tz_convert("America/New_York")
    frame = frame.sort_index()
    week = frame.loc["2025-07-27 18:00":"2025-08-01 16:59"]
    friday_close = float(frame.loc["2025-07-25 15:59":"2025-07-25 15:59"]["c"].iloc[0])
    filled = week[(week["l"] <= friday_close) & (week["h"] >= friday_close)]
    return float(week["o"].iloc[0]), friday_close, filled.index[0]


def test_c10_the_weekly_gap_is_a_level_all_week_until_it_is_filled():
    """His Tuesday 2026-09-08 chart still draws both NWOG lines (p16_x18): the
    gap is the draw of the week until it is filled. Native week of 2025-07-27:
    on the raw bars the gap opens Sunday 18:00 and first trades at the Friday
    close on Tuesday 07-29 at 15:39. So Monday and Tuesday carry it (Tuesday
    with the minute it dies), and Wednesday no longer has it."""
    sunday_open, friday_close, filled_at = _tape_week_of_2025_07_27()
    assert str(filled_at)[:16] == "2025-07-29 15:39" and abs(sunday_open - friday_close) > 50
    lo, hi = sorted([Decimal(str(sunday_open)), Decimal(str(friday_close))])

    monday = gb._nwog_levels(load_source_market("2025-07-28"))
    assert monday is not None and monday["dead_at"] is None

    tuesday_market = load_source_market("2025-07-29")
    tuesday = gb._nwog_levels(tuesday_market)
    assert tuesday is not None, "the gap was dropped after Monday"
    assert abs(tuesday["low"] - lo) <= Decimal("1") and abs(tuesday["high"] - hi) <= Decimal("1")
    assert int(tuesday_market.at("15:39")) < tuesday["dead_at"] <= int(tuesday_market.at("15:41"))
    # a rung that is dead at the decision is not offered as the next drawn level; before it dies it is
    rung = {"price": tuesday["low"], "label": "nwog_low", "known_at": tuesday["known_at"], "dead_at": tuesday["dead_at"]}
    beyond = tuesday["low"] + Decimal("500")
    assert gb.next_drawn_level([rung], beyond=beyond, side="short", known_by=tuesday["dead_at"] - 1) is not None
    assert gb.next_drawn_level([rung], beyond=beyond, side="short", known_by=tuesday["dead_at"]) is None

    assert gb._nwog_levels(load_source_market("2025-07-30")) is None, "filled before Wednesday's session opened"
