"""Frozen slice F and long slice L as NY trade dates."""

from __future__ import annotations

from datetime import date, time, timedelta
from pathlib import Path

from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.research.phase1_live import F_END, F_START, L_END, L_START, ZONE

CALENDAR_PATH = Path("/workspace/trading-research/configs/cash-rth-calendar-research-v1.json")
RESEARCH_CUT = local_timestamp(date(2026, 9, 9), time(0), ZONE)


def _iso(value: str) -> date:
    return date.fromisoformat(value)


def load_calendar(path: Path | None = None) -> CashCalendar:
    return CashCalendar(path or CALENDAR_PATH)


def trade_dates(calendar: CashCalendar, start: date, end: date, *, cut: int = RESEARCH_CUT) -> tuple[date, ...]:
    days = []
    day = start
    while day <= end:
        row = calendar.resolve(day, cut=cut)
        if row.state != "closed":
            days.append(day)
        day += timedelta(days=1)
    return tuple(days)


def slice_dates(calendar: CashCalendar, slice_id: str) -> tuple[date, ...]:
    if slice_id == "F":
        return trade_dates(calendar, _iso(F_START), _iso(F_END))
    if slice_id == "L":
        cal = trade_dates(calendar, date(2020, 1, 1), _iso(L_END))
        pre = _weekdays(_iso(L_START), date(2019, 12, 31))
        return tuple(d for d in (*pre, *cal) if _iso(L_START) <= d <= _iso(L_END))
    raise ValueError(f"unknown slice {slice_id}")


def _weekdays(start: date, end: date) -> tuple[date, ...]:
    days = []
    day = start
    while day <= end:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return tuple(days)


def session_bounds(day: date) -> tuple[int, int]:
    """Globex session 18:00 ET prior calendar day to 17:00 ET trade date."""
    start = local_timestamp(day - timedelta(days=1), time(18, 0), ZONE)
    end = local_timestamp(day, time(17, 0), ZONE)
    return start, end
