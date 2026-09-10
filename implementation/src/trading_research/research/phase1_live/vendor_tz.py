"""Assumed stored TZ per vendor. Session bounds are always America/New_York.

QuantPad and Databento timestamps are UTC Unix epochs. Clocks convert ET wall
times to UTC epochs via ZoneInfo, so a 06:00 ET bound matches those epochs.
Yahoo daily cash and Theta OI request_date are civil dates (US session dates).
They have no intraday clock. Mixing a naive ET wall integer with a UTC epoch
is a construction fail.
"""

from __future__ import annotations

from datetime import date, time, timezone
from zoneinfo import ZoneInfo

from trading_research.foundations.calendar import local_timestamp

ET = "America/New_York"
STORED = {
    "quantpad_ohlcv": "UTC epoch milliseconds",
    "quantpad_trades": "UTC epoch nanoseconds",
    "quantpad_mbp1": "UTC epoch nanoseconds",
    "yahoo_cash_daily": "civil date (America/New_York session date)",
    "theta_oi": "civil request_date (America/New_York session date)",
    "theta_quote_1m": "UTC epoch or exchange timestamp converted at read",
    "databento_nqopt": "UTC (DBN); not parsed for OI in this pass",
    "session_clocks": "America/New_York wall via local_timestamp -> UTC epoch",
}


def et_ns(day: date, wall: time, offset: int = 0) -> int:
    return local_timestamp(day, wall, ET) if offset == 0 else None


def utc_ms_to_et_iso(ms: int) -> str:
    from datetime import datetime
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).astimezone(ZoneInfo(ET)).isoformat()
