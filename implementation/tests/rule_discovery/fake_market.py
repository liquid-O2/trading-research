"""A minute-bar stand-in for HistoricalFeatures, for rule-level adapter tests.

Only the members the B0.3 Jumbo and Green Bird scans use are implemented, and
the prior-period objects are supplied as fixtures so no test ever asks the
frozen /workspace/data cache for a window that does not exist.
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Iterable, Mapping

from trading_research.research.method_pack.clocks import et_ns

MINUTE = 60_000_000_000


def ns(day: date, hhmm: str, offset: int = 0) -> int:
    hour, minute = (int(part) for part in hhmm.split(":"))
    return int(et_ns(day + timedelta(days=offset), hour, minute))


class _Policy:
    def previous_session(self, day):
        return {"date": str(day - timedelta(days=1)), "windows": [], "known": True}

    def rth(self, day):
        return {"known": True, "windows": []}


class _Window:
    def __init__(self):
        self.document = {"input_sha256": "fake"}


class FakeMarket:
    """Minute bars between prev-day 18:00 and 16:00, the tape window's shape."""

    def __init__(self, day: str, bars: Iterable[Mapping[str, Any]], *, instrument_id: int = 1, prior_day=None, prior_week=None, prior_sessions=None, prior_value=None):
        self.day = date.fromisoformat(day)
        self.instrument_id = instrument_id
        self.data_root = "/workspace/data"
        self.policy = _Policy()
        self.window = _Window()
        self.input_receipts: list = []
        self.start = ns(self.day, "18:00", -1)
        self.end = ns(self.day, "16:00")
        self._bars = sorted((dict(row) for row in bars), key=lambda row: row["start"])
        self.b02_prior_day = prior_day
        self.b02_prior_week = prior_week
        self.b02_prior_sessions = prior_sessions
        self.b02_prior_value = prior_value
        self.jj_sessionstat = False

    # -- clock ------------------------------------------------------------
    def at(self, text, offset=0):
        return ns(self.day, text, offset)

    # -- bars -------------------------------------------------------------
    def bars(self, start, end, seconds=60):
        if start < self.start or end > self.end or end <= start:
            return []
        rows = [row for row in self._bars if start <= row["start"] < end]
        if seconds == 60:
            return rows
        out = []
        step = seconds * 1_000_000_000
        anchor = (start // step) * step
        while anchor < end:
            group = [row for row in rows if anchor <= row["start"] < anchor + step]
            anchor += step
            if not group:
                continue
            out.append(
                {
                    "start": group[0]["start"],
                    "end": group[-1]["end"],
                    "O": group[0]["O"],
                    "H": max(row["H"] for row in group),
                    "L": min(row["L"] for row in group),
                    "C": group[-1]["C"],
                    "V": sum(row.get("V", 0) for row in group),
                    "known_at": group[-1]["known_at"],
                    "observed_complete": True,
                    "bar_id": f"{seconds}s:{group[0]['start']}",
                }
            )
        return out

    def range(self, start, end, label):
        rows = self.bars(start, end)
        if not rows:
            return None
        return {
            "id": f"{label}:{self.instrument_id}:{start}:{end}",
            "start": start,
            "end": end,
            "known_at": end,
            "low": min(row["L"] for row in rows),
            "high": max(row["H"] for row in rows),
            "open": rows[0]["O"],
            "close": rows[-1]["C"],
        }

    def coverage(self, start, end):
        return {"observed_scope_complete": True}

    def prior(self, kind="day"):
        if kind == "week" and self.b02_prior_week:
            return {"range": self.b02_prior_week, "omissions": [], "sessions": []}
        return {"range": None, "omissions": [], "sessions": []}

    def vwap(self, at):
        rows = [row for row in self._bars if row["start"] <= at]
        if not rows:
            return {"price": None}
        total = sum(Decimal(str(row.get("V", 1))) for row in rows)
        if total <= 0:
            return {"price": None}
        pv = sum(Decimal(str(row["C"])) * Decimal(str(row.get("V", 1))) for row in rows)
        return {"price": pv / total, "known_at": at}


def bar(day: date, hhmm: str, o, h, l, c, *, offset: int = 0, volume: int = 100) -> dict[str, Any]:
    start = ns(day, hhmm, offset)
    return {
        "start": start,
        "end": start + MINUTE,
        "O": Decimal(str(o)),
        "H": Decimal(str(h)),
        "L": Decimal(str(l)),
        "C": Decimal(str(c)),
        "V": volume,
        "known_at": start + MINUTE,
        "observed_complete": True,
        "bar_id": f"m:{start}",
    }


def flat_series(day: date, start_hhmm: str, minutes: int, price, *, offset: int = 0, volume: int = 100) -> list[dict[str, Any]]:
    """``minutes`` one-minute bars from ``start_hhmm`` all at ``price``."""
    hour, minute = (int(part) for part in start_hhmm.split(":"))
    out = []
    for index in range(minutes):
        total = hour * 60 + minute + index
        stamp = f"{(total // 60) % 24:02d}:{total % 60:02d}"
        roll = offset + (total // (24 * 60))
        out.append(bar(day, stamp, price, price, price, price, offset=roll, volume=volume))
    return out
