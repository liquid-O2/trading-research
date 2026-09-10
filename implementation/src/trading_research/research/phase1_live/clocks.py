"""Named clocks. No free-form boxes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time, timedelta

from trading_research.foundations.calendar import local_timestamp
from trading_research.research.phase1_live import ZONE

MS = 1_000_000


@dataclass(frozen=True)
class Clock:
    id: str
    start: time
    end: time
    start_offset: int
    end_offset: int
    outcome_start: time
    outcome_end: time
    outcome_start_offset: int
    outcome_end_offset: int
    note: str


def _t(h, m=0, s=0):
    return time(h, m, s)


CLOCKS = {
    "range.6-9.published": Clock(
        "range.6-9.published", _t(6), _t(9), 0, 0, _t(9, 30), _t(12), 0, 0,
        "ONS 06:00-09:00 TBR p.7",
    ),
    "range.5-9": Clock(
        "range.5-9", _t(5), _t(9), 0, 0, _t(9, 30), _t(12), 0, 0, "5-9 family XF p.7",
    ),
    "range.7-9": Clock(
        "range.7-9", _t(7), _t(9), 0, 0, _t(9, 30), _t(12), 0, 0, "5-9 family",
    ),
    "range.8-9": Clock(
        "range.8-9", _t(8), _t(9), 0, 0, _t(9, 30), _t(12), 0, 0, "5-9 family",
    ),
    "range.london.00-03": Clock(
        "range.london.00-03", _t(0), _t(3), 0, 0, _t(3), _t(6), 0, 0, "Jumbo box into 03:00",
    ),
    "range.london.0300-0330": Clock(
        "range.london.0300-0330", _t(3), _t(3, 30), 0, 0, _t(3, 30), _t(6), 0, 0,
        "TBR London opening range",
    ),
    "range.asia.2000-2030": Clock(
        "range.asia.2000-2030", _t(20), _t(20, 30), -1, -1, _t(20, 30), _t(0), -1, 0,
        "TBR Asia opening range",
    ),
    "range.gb.asia": Clock(
        "range.gb.asia", _t(20), _t(0), -1, 0, _t(0), _t(6), 0, 0, "GB inferred 20:00-00:00",
    ),
    "range.gb.london": Clock(
        "range.gb.london", _t(2), _t(5), 0, 0, _t(5), _t(9, 30), 0, 0, "GB inferred 02:00-05:00",
    ),
    "range.gb.nyam": Clock(
        "range.gb.nyam", _t(9), _t(10), 0, 0, _t(10), _t(12), 0, 0,
        "GB NYAM. Outcomes start 10:00",
    ),
    "range.gb.10-11": Clock(
        "range.gb.10-11", _t(10), _t(11), 0, 0, _t(11), _t(12), 0, 0, "GB 10-11 hour",
    ),
    "range.or.5m": Clock(
        "range.or.5m", _t(9, 30), _t(9, 35), 0, 0, _t(9, 35), _t(12), 0, 0, "OR 5m reference",
    ),
    "range.or.15m": Clock(
        "range.or.15m", _t(9, 30), _t(9, 45), 0, 0, _t(9, 45), _t(12), 0, 0, "OR 15m reference",
    ),
    "range.ib": Clock(
        "range.ib", _t(9, 30), _t(10, 30), 0, 0, _t(10, 30), _t(16), 0, 0, "IB comparison only",
    ),
    "prior.rth": Clock(
        "prior.rth", _t(9, 30), _t(16), 0, 0, _t(16), _t(17), 0, 0, "prior RTH 09:30-16:00",
    ),
    "range.midnight.0000-0030": Clock(
        "range.midnight.0000-0030", _t(0), _t(0, 30), 0, 0, _t(0, 30), _t(3), 0, 0,
        "TBR midnight opening range",
    ),
    "range.rth.0930-1000": Clock(
        "range.rth.0930-1000", _t(9, 30), _t(10), 0, 0, _t(10), _t(12), 0, 0,
        "TBR equities opening range A period",
    ),
    "range.rth.1000-1030": Clock(
        "range.rth.1000-1030", _t(10), _t(10, 30), 0, 0, _t(10, 30), _t(12), 0, 0,
        "TBR RTH AM second window",
    ),
    "range.lunch.1200-1230": Clock(
        "range.lunch.1200-1230", _t(12), _t(12, 30), 0, 0, _t(12, 30), _t(16), 0, 0,
        "TBR lunch opening range comparison",
    ),
    "range.moc.1500-1530": Clock(
        "range.moc.1500-1530", _t(15), _t(15, 30), 0, 0, _t(15, 30), _t(16), 0, 0,
        "TBR MOC comparison",
    ),
    "range.on.1800-0930": Clock(
        "range.on.1800-0930", _t(18), _t(9, 30), -1, 0, _t(9, 30), _t(12), 0, 0,
        "overnight 18:00-09:30 H/L",
    ),
}


def wall_ns(day: date, clock: time, offset: int = 0) -> int:
    return local_timestamp(day + timedelta(days=offset), clock, ZONE)


def clock_bounds(day: date, spec: Clock) -> dict[str, int]:
    start = wall_ns(day, spec.start, spec.start_offset)
    end = wall_ns(day, spec.end, spec.end_offset)
    if end <= start:
        end = wall_ns(day, spec.end, spec.end_offset + 1)
    out_s = wall_ns(day, spec.outcome_start, spec.outcome_start_offset)
    out_e = wall_ns(day, spec.outcome_end, spec.outcome_end_offset)
    if out_e <= out_s:
        out_e = wall_ns(day, spec.outcome_end, spec.outcome_end_offset + 1)
    return {
        "start_ns": start,
        "end_ns": end,
        "outcome_start_ns": out_s,
        "outcome_end_ns": out_e,
        "start_ms": start // MS,
        "end_ms": end // MS,
        "outcome_start_ms": out_s // MS,
        "outcome_end_ms": out_e // MS,
        "known_at_ns": end,
    }


def rth_end_ns(day: date, early_close: time | None) -> int:
    return wall_ns(day, early_close or time(16, 0), 0)
