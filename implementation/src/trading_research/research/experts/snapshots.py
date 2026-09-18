"""The quarter-hour issue-time grid of an NQ account day, and the join from a
decision time to the grid.

An account day runs from 18:00 New York time on the previous calendar day to
its close (17:00, or the early close the session policy carries). Issue times
are the quarter hours inside it. New York's UTC offset is a whole number of
hours in both regimes and the market is closed across the Sunday 02:00
transition, so stepping 15 minutes in absolute time from the 18:00 start lands
on wall-clock quarter hours on every day, DST weeks included.

Nothing here reads market data; the grid is a calendar object.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.session_policy import NQSessionPolicy
from trading_research.research.rule_discovery.native import account_day_window

NS = 1_000_000_000
MINUTE_NS = 60 * NS
QUARTER_NS = 15 * MINUTE_NS
NEW_YORK = ZoneInfo("America/New_York")

#: DATA_CONTRACTS analysis buckets, New York wall clock, [start, end) in minutes of the day
BUCKETS = (
    ("reopen", 18 * 60, 24 * 60),
    ("asia", 0, 3 * 60),
    ("europe", 3 * 60, 9 * 60 + 30),
    ("us_morning", 9 * 60 + 30, 12 * 60),
    ("us_afternoon", 12 * 60, 16 * 60),
    ("late", 16 * 60, 17 * 60),
)


def _local(ns: int) -> datetime:
    """New York wall clock of an instant, to the whole second below it (integer
    division: a float division rounds 17:59:59.999999999 up to 18:00)."""
    return datetime.fromtimestamp(int(ns) // NS, tz=timezone.utc).astimezone(NEW_YORK)


def account_day_grid(day: date, *, policy: NQSessionPolicy | None = None) -> np.ndarray:
    """Quarter-hour issue times t with account-day start <= t < account-day end."""
    start, end = account_day_window(day, policy=policy)
    n = int((end - start + QUARTER_NS - 1) // QUARTER_NS)
    return start + np.arange(n, dtype=np.int64) * QUARTER_NS


def rth_window(day: date, *, policy: NQSessionPolicy | None = None) -> tuple[int, int] | None:
    """(open, close) of the cash session, or None on a day the policy closes."""
    policy = policy or NQSessionPolicy()
    windows = policy.rth(day).get("windows") or []
    if not windows:
        return None
    return int(windows[0][0]), int(windows[0][1])


def rth_grid(day: date, *, policy: NQSessionPolicy | None = None) -> np.ndarray:
    """Quarter-hour issue times with RTH open <= t < RTH close."""
    window = rth_window(day, policy=policy)
    if window is None:
        return np.zeros(0, dtype=np.int64)
    grid = account_day_grid(day, policy=policy)
    return grid[(grid >= window[0]) & (grid < window[1])]


def account_day_of(ns: int) -> date:
    """The account day an instant belongs to: the New York date, moved to the
    next calendar day from 18:00 on."""
    local = _local(ns)
    day = local.date()
    return day + timedelta(days=1) if local.hour >= 18 else day


def grid_time_for(decision_at_ns: int, *, day: date | None = None, policy: NQSessionPolicy | None = None) -> int | None:
    """The latest grid time <= ``decision_at_ns`` inside the decision's account
    day; None when the instant lies outside the account day (the 17:00-18:00
    closure, or after an early close). A decision exactly on a quarter hour
    joins to that quarter hour: a row issued at t uses data available at or
    before t, so it is known at the decision."""
    decision = int(decision_at_ns)
    day = day or account_day_of(decision)
    start, end = account_day_window(day, policy=policy)
    if decision < start or decision >= end:
        return None
    return start + ((decision - start) // QUARTER_NS) * QUARTER_NS


def session_bucket(ns: int) -> str:
    local = _local(ns)
    minute = local.hour * 60 + local.minute
    for name, lo, hi in BUCKETS:
        if lo <= minute < hi:
            return name
    return "closed"


def is_holdout(day: date) -> bool:
    """The Phase 2 blind hold-out: nothing fitted may use these days."""
    return day >= date(2026, 4, 1)


__all__ = [
    "BUCKETS",
    "MINUTE_NS",
    "QUARTER_NS",
    "account_day_grid",
    "account_day_of",
    "grid_time_for",
    "is_holdout",
    "rth_grid",
    "rth_window",
    "session_bucket",
    "et_ns",
]
