"""Green Bird source-faithful scan (B0.3).

Rebuilt 2026-09-17 against `reports/research-work/reviews/FIDELITY_AUDIT_2026-09-17.md`
sections 2.1-2.4. Where the audit and the previous adapter disagreed, the audit
wins; where the audit and the wiki method pages disagreed, the audit wins.

The object (audit 2.1): "Session highs. Session lows. Breakouts. Fakeouts. I
know my range. Then I watch how price behaves at its edges. Break out and hold?
I'm looking for continuation. Sweep a level and fail back inside? I'm looking
for the reversal."  The references are the lines and boxes of the author's
layout and every dated chart draws the same ones:

* Asia box 20:00-00:00 ET and London box 02:00-05:00 ET, in every month (G1);
* the 09:00-10:00 NY box traded from 10:00 and the 10:00-11:00 NY box traded
  from 11:00, then each later completed hour from its close (G2);
* True Day Open, PDH/PDL, PWH/PWL, the NWOG (objective) and the golden pocket.

Every reference stays live until it is swept, whatever the hour (G3); the only
clock rules the author states are "I wait until after 10AM" for the 9-10 box
and "after the open" for the London reclaim long.
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from bisect import bisect_left
from typing import Any, Iterable, Mapping, Sequence
import inspect

from trading_research.research.method_pack.empirical_market import clock
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.historical_features import MINUTE, Q, sign
from trading_research.research.method_pack.protocol import jsonable
from trading_research.research.rule_discovery.source_adapters.enumeration import (
    enumeration_point,
    enumeration_scope,
    split_b02_overrides,
)
from trading_research.research.rule_discovery.source_adapters.session_levels import prior_sessions
from trading_research.research.rule_discovery.source_adapters.trade_selection import (
    MAX_ENTRIES_PER_SESSION,
    select_session_trades,
)

B02_VERSION = "B0.3-2026-09-17"
STAGE_ORDER = (
    "context",
    "reference",
    "location",
    "trigger",
    "confirmation",
    "risk",
    "objective",
    "management",
)
FIVE = 5 * MINUTE
HOUR = 60 * MINUTE

# Replay tolerances. LEVEL_TOLERANCE is the strict band used for the "within a
# few points" column of the replay table; TICKET_RISK_FALLBACK is the risk used
# when a ticket prints no stop (the median printed stop is about 27 points,
# audit 2.4).
LEVEL_TOLERANCE = Decimal("5.00")
TICKET_RISK_FALLBACK = Decimal("27.00")

# Risk and management. The tickets print "Amount: 750" with quantity =
# 750 / (stop points x 6) on all eight tickets (audit 2.1 "Risk and
# management"); the point factor is the fleet's per-account risk, not MNQ's
# $2 (audit 2.5), so the baseline keeps $750 over the MNQ point value and
# records the discrepancy rather than "correcting" the rule.
RISK_DOLLARS = Decimal("750")
MNQ_POINT_VALUE = Decimal("2")
# G12: partials every ~25 points through a parked limit ladder; the observed
# rungs are 13.75-32.25 apart (08-27, 08-28, 09-15).
LADDER_SPACING = Decimal("25")
# G6: stops are structural, beyond the sweep wick or the zone, not one tick.
# 2026-09-03 stops exactly on the sweep extreme and 2026-08-31 stops 22 points
# beyond it; two points is the smallest structural buffer consistent with both.
SWEEP_STOP_BUFFER = Decimal("2")

# The failure must follow the sweep. Sweep-to-entry on the tickets is 5-15
# minutes (09-03 00:40->00:45, 11-20 10:00->10:05, 08-28 10:00->10:05,
# 08-27 11:15->11:30 and 12:45->13:00, 07-13 20:30->20:40, 09-15 09:50->10:05).
# The bound is four times the observed maximum so no ticket is excluded and a
# level that "fails" hours later is not counted as the author's trade.
FAIL_WINDOW_BARS = 12
FAIL_WINDOW_NS = FAIL_WINDOW_BARS * FIVE
# A reference can be swept more than once a session: 2026-08-27 traded the
# 9-10 box high on its second excursion at 13:00 after an earlier break held.
MAX_CYCLES_PER_LEVEL = 6
# G9: "break and close beyond the range, hold, pullback, enter with the move".
# "Hold" is registered as two consecutive complete five-minute closes beyond
# the edge; the source does not state a bar count (open question in the report).
CONTINUATION_HOLD_BARS = 2

REC_IDENTITY_KEYS = frozenset({"family", "method_id", "branch", "coverage_id", "registered_od", "parameters"})
AUTHOR_EXAMPLES_PATH = Path(__file__).resolve().parents[6] / "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-17.json"

B02_BRANCHES = {
    "GB-FAIL": (
        "london_box",
        "asia_box",
        "asia_tdo_case",
        "prior_day_level",
        "prior_week_level",
        "nyam_box",
        "previous_hour",
        "cash_open_reclaim_case",
        "golden_pocket",
        "continuation",
    ),
    "GB-VWAP": ("source_long",),
    "GB-SCALP": ("golden_pocket_continuation",),
}
SCALP_OBSERVATIONS = ("bearish_small_scalp", "bullish_discount_pullback")

# G1: one clock each, in every month of the record.
ASIA_BOX = {"name": "20:00-00:00", "start": "20:00", "end": "00:00", "start_off": -1, "end_off": 0}
LONDON_BOX = {"name": "02:00-05:00", "start": "02:00", "end": "05:00", "start_off": 0, "end_off": 0}


# ---------------------------------------------------------------------------
# primitives


def _d(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _dec(value: Any) -> Decimal:
    out = _d(value)
    if out is None:
        raise ValueError("decimal required")
    return out


def asia_box_spec(day: date | None = None) -> dict[str, Any]:
    """G1: 20:00-00:00 ET in every month. ``day`` is accepted and ignored."""
    return dict(ASIA_BOX)


def london_box_spec(day: date | None = None) -> dict[str, Any]:
    """G1: 02:00-05:00 ET in every month. ``day`` is accepted and ignored."""
    return dict(LONDON_BOX)


def derived_quantity(stop_points: Decimal | None) -> Decimal | None:
    if stop_points is None or stop_points <= 0:
        return None
    return RISK_DOLLARS / (stop_points * MNQ_POINT_VALUE)


def limit_ladder(entry: Decimal, target: Decimal, side: str, spacing: Decimal = LADDER_SPACING) -> list[Decimal]:
    if entry is None or target is None or spacing <= 0:
        return []
    step = spacing if sign(side) * (target - entry) > 0 else -spacing
    rungs: list[Decimal] = []
    price = entry + step
    for _ in range(64):
        if sign(side) * (price - target) >= 0:
            break
        rungs.append(price)
        price = price + step
    rungs.append(target)
    return rungs


def pocket_in_leg_direction(low: Decimal, high: Decimal, impulse_side: str) -> tuple[Decimal, Decimal]:
    """50%-61.8% retracement of a measured impulse, in the impulse's direction."""
    low_d, high_d = _dec(low), _dec(high)
    if high_d < low_d:
        low_d, high_d = high_d, low_d
    width = high_d - low_d
    if impulse_side == "long":
        return (high_d - width * Decimal("0.618"), high_d - width * Decimal("0.5"))
    return (low_d + width * Decimal("0.5"), low_d + width * Decimal("0.618"))


def near_edge(pocket: tuple[Decimal, Decimal], impulse_side: str) -> Decimal:
    lo, hi = pocket
    return hi if impulse_side == "long" else lo


def far_edge(pocket: tuple[Decimal, Decimal], impulse_side: str) -> Decimal:
    lo, hi = pocket
    return lo if impulse_side == "long" else hi


def session_label(market, ns: int) -> str:
    if market.at("20:00", -1) <= ns < market.at("00:00"):
        return "asia"
    if market.at("00:00") <= ns < market.at("03:00"):
        return "overnight"
    if market.at("03:00") <= ns < market.at("09:30"):
        return "london"
    if market.at("09:30") <= ns < market.at("12:00"):
        return "ny_am"
    if market.at("12:00") <= ns <= market.at("16:00"):
        return "ny_pm"
    return "other"


def next_rth_open_ns(market, decision_ns: int) -> int:
    for offset in range(0, 6):
        stamp = market.at("09:30", offset)
        if stamp > decision_ns:
            return int(stamp)
    return int(decision_ns + 18 * HOUR)


def _bar_complete(row: Mapping[str, Any] | None) -> bool:
    return bool(row) and bool(row.get("observed_complete")) and row.get("C") is not None


def session_bars(market, seconds: int = 60) -> list[dict[str, Any]]:
    """The session's completed bars at one resolution, loaded once per market.

    Every scan below slices this list; the window object is asked for bars once
    per resolution so a full-session scan costs one pass over the tape.
    """
    key = f"_gb_bars_{seconds}"
    rows = getattr(market, key, None)
    if rows is None:
        try:
            rows = list(market.bars(int(market.start), int(market.end), seconds) or [])
        except Exception:
            rows = []
        rows = [row for row in rows if row.get("start") is not None]
        rows.sort(key=lambda row: int(row["start"]))
        setattr(market, key, rows)
        setattr(market, f"{key}_starts", [int(row["start"]) for row in rows])
    return rows


def _safe_bars(market, start: int, end: int, seconds: int = 60) -> list[dict[str, Any]]:
    if start is None or end is None or end <= start:
        return []
    rows = session_bars(market, seconds)
    if not rows:
        return []
    starts = getattr(market, f"_gb_bars_{seconds}_starts")
    lo = max(int(start), int(market.start))
    hi = min(int(end), int(market.end))
    if hi <= lo:
        return []
    left = bisect_left(starts, lo)
    right = bisect_left(starts, hi)
    return rows[left:right]


def five_minute_grid(market) -> dict[int, dict[str, Any]]:
    """Complete five-minute clock bars keyed by their aligned start."""
    grid = getattr(market, "_gb_five_grid", None)
    if grid is None:
        grid = {}
        for row in session_bars(market, 300):
            if _bar_complete(row):
                grid[int(row["start"]) // FIVE * FIVE] = row
        setattr(market, "_gb_five_grid", grid)
    return grid


def _five_min_row(market, start: int) -> dict[str, Any] | None:
    return five_minute_grid(market).get(int(start) // FIVE * FIVE)


def _range(market, start: int, end: int, label: str) -> dict[str, Any] | None:
    if end <= start:
        return None
    try:
        ref = market.range(start, end, label)
    except Exception:
        return None
    if ref is None or ref.get("low") is None or ref.get("high") is None:
        return None
    return ref


def excursion(market, start: int, end: int) -> tuple[Decimal | None, Decimal | None]:
    rows = _safe_bars(market, start, end)
    if not rows:
        return None, None
    highs = [_dec(r["H"]) for r in rows if r.get("H") is not None]
    lows = [_dec(r["L"]) for r in rows if r.get("L") is not None]
    if not highs or not lows:
        return None, None
    return max(highs), min(lows)


def _tdo(market) -> Decimal | None:
    rows = _safe_bars(market, market.at("00:00"), market.at("00:00") + MINUTE)
    if not rows:
        return None
    return _d(rows[0].get("O"))


# ---------------------------------------------------------------------------
# prior-period references
#
# G2/G3: PDH/PDL are the previous CME session's extremes, the line the author's
# TradingView layout draws. 2026-09-01's printed PDL 29,270 is the previous
# session's 18:00-16:00 low (29,273.50 on our tape) and not its RTH low
# (29,355.00), so the reference is the full prior session, loaded from the
# already-cached window of that session.


def _prior_session_window(market) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    fixture = getattr(market, "b02_prior_day", None)
    if fixture is not None:
        return dict(fixture), []
    cached = getattr(market, "_gb_prior_session", None)
    if cached is not None:
        return (None if cached[0] is None else dict(cached[0])), list(cached[1])
    result = _prior_session_window_uncached(market)
    setattr(market, "_gb_prior_session", result)
    return (None if result[0] is None else dict(result[0])), list(result[1])


def _prior_session_window_uncached(market) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    sessions = prior_sessions(market, 1)
    if not sessions:
        return _prior_rth_window(market, reason="prior_full_session_unavailable")
    span = sessions[0]
    return (
        {
            "id": span["id"],
            "low": span["low"],
            "high": span["high"],
            "close": span["close"],
            "open": span["open"],
            "known_at": span["known_at"],
            "scope": span["scope"],
            "period_end": span["date"],
        },
        [],
    )


def _prior_rth_window(market, *, reason: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    try:
        prior = market.prior("day")
    except Exception as exc:
        return None, [{"reason": reason}, {"reason": "prior_day_unavailable", "detail": str(exc)}]
    span = (prior or {}).get("range")
    if not span or span.get("low") is None:
        return None, [{"reason": reason}, {"reason": "prior_day_unavailable"}]
    out = dict(span)
    out["scope"] = "rth_0930_1600"
    return out, [{"reason": reason, "operand": "prior_session_scope", "detail": "fell back to the RTH prior-day window"}]


PRIOR_WEEK_SCOPE = "rth_0930_1600"
PRIOR_WEEK_CONVENTION = "iso_monday_to_sunday"
PRIOR_WEEK_CALENDAR = "method_pack.session_policy (versioned regular NQ matching policy)"


def _prior_week_range(market) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    fixture = getattr(market, "b02_prior_week", None)
    if fixture is not None:
        return dict(fixture), []
    try:
        prior = market.prior("week")
    except Exception as exc:
        return None, [{"reason": "prior_week_unavailable", "detail": str(exc)}]
    span = (prior or {}).get("range")
    if not span or span.get("low") is None or span.get("high") is None:
        return None, [{"reason": "prior_week_range_missing"}]
    week_end = market.day - timedelta(days=market.day.weekday())
    ref = dict(span)
    ref.update(
        {
            "id": f"prior_week:{market.instrument_id}:{week_end}",
            "period_kind": "week",
            "scope": PRIOR_WEEK_SCOPE,
            "source_calendar": PRIOR_WEEK_CALENDAR,
            "week_convention": PRIOR_WEEK_CONVENTION,
            "period_start": str(week_end - timedelta(days=7)),
            "period_end": str(week_end - timedelta(days=1)),
            "known_at": int(span.get("end") or market.start),
        }
    )
    omissions = [
        {
            "reason": "full_session_scope_unmeasured",
            "operand": "full_session_prior_week_window",
            "detail": "prior('week') supplies RTH windows only",
        }
    ]
    return ref, omissions


def _nwog_levels(market) -> dict[str, Any] | None:
    """New Week Opening Gap: Friday's close to Sunday's 18:00 open.

    G7: the gap is a magnet and an objective ("close the whole trade when price
    hits NWOG"), never an entry reference. It is therefore carried only on the
    objective ladder.
    """
    if market.day.weekday() > 4:
        return None
    monday = market.day - timedelta(days=market.day.weekday())
    if (market.day - monday).days > 4:
        return None
    sunday_open = clock(monday - timedelta(days=1), "18:00")
    rows = _safe_bars(market, sunday_open, sunday_open + MINUTE)
    open_px = _d(rows[0].get("O")) if rows else None
    friday_close = None
    try:
        prior = market.prior("week")
        span = (prior or {}).get("range")
        friday_close = _d((span or {}).get("close"))
    except Exception:
        friday_close = None
    if open_px is None or friday_close is None:
        return None
    lo, hi = sorted([open_px, friday_close])
    return {"low": lo, "high": hi, "id": f"nwog:{market.instrument_id}:{monday}", "known_at": int(sunday_open)}


# ---------------------------------------------------------------------------
# the reference set


def _box_ns(market, spec: Mapping[str, Any]) -> tuple[int, int]:
    start = market.at(spec["start"], spec["start_off"])
    end = market.at(spec["end"], spec["end_off"])
    if spec["end"] == "00:00" and spec["end_off"] == 0 and end <= start:
        end = market.at("00:00")
    return int(start), int(end)


def _prior_session_box(market, window: tuple[str, str]) -> dict[str, Any] | None:
    """One clock window of the previous session, from that session's own tape."""
    sessions = prior_sessions(market, 1)
    if not sessions:
        return None
    span = sessions[0]
    win = span.get("window")
    if win is None:
        return None
    day = date.fromisoformat(span["date"])
    try:
        rows = win.bars(clock(day, window[0]), clock(day, window[1]), 300)
    except Exception:
        return None
    highs = [_dec(row["H"]) for row in rows if row.get("H") is not None]
    lows = [_dec(row["L"]) for row in rows if row.get("L") is not None]
    if not highs or not lows:
        return None
    return {"low": min(lows), "high": max(highs), "date": span["date"]}


def session_references(market) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Every drawn reference of the author's layout, with the hour it goes live.

    Boxes are frozen at their close and traded from it; the 09:00-10:00 box is
    not traded before 10:00 ("I wait until after 10AM. The 9 to 10AM range is
    established. No guessing beforehand."). Each later completed hour is the
    portable version of the same reference ("Optional: previous hour high/low
    if you are trading later hours").
    """
    refs: list[dict[str, Any]] = []
    omissions: list[dict[str, Any]] = []

    def add_box(kind: str, branch: str, start: int, end: int, label: str, *, running_after: int | None = None) -> None:
        ref = _range(market, start, end, label)
        if ref is None:
            omissions.append({"reason": "reference_window_unavailable", "kind": kind})
            return
        refs.append(
            {
                "id": f"{kind}:{market.instrument_id}:{start}:{end}",
                "kind": kind,
                "branch": branch,
                "low": _dec(ref["low"]),
                "high": _dec(ref["high"]),
                "known_at": int(ref.get("known_at") or end),
                "live_from": int(end),
                "window": [int(start), int(end)],
                "sides": ("long", "short"),
            }
        )
        # G-D (coordinator guidance 2026-09-17): while a session is open its
        # high and low so far are the reference the author trades -- 2026-07-30
        # bought the London low at 04:00, inside the 02:00-05:00 box. The
        # running reference goes live an hour after the session opens and is
        # superseded by the frozen box at its close. The 09:00-10:00 NY box is
        # the stated exception ("I wait until after 10AM").
        if running_after is None:
            return
        cursor = int(running_after)
        while cursor <= int(end):
            running = _range(market, start, cursor, f"{label}-running-{cursor}")
            cursor += 15 * MINUTE
            if running is None:
                continue
            refs.append(
                {
                    "id": f"{kind}_running:{market.instrument_id}:{start}:{cursor}",
                    "kind": f"{kind}_running",
                    "branch": branch,
                    "low": _dec(running["low"]),
                    "high": _dec(running["high"]),
                    "known_at": int(cursor),
                    "live_from": int(cursor),
                    "window": [int(start), int(cursor)],
                    "sides": ("long", "short"),
                    "running": True,
                    "frozen_at": int(end),
                }
            )

    a_start, a_end = _box_ns(market, ASIA_BOX)
    add_box("asia_box", "asia_box", a_start, a_end, "asia-box-20:00-00:00", running_after=a_start + HOUR)
    l_start, l_end = _box_ns(market, LONDON_BOX)
    add_box("london_box", "london_box", l_start, l_end, "london-box-02:00-05:00", running_after=l_start + HOUR)
    add_box("ny_box_09_10", "nyam_box", int(market.at("09:00")), int(market.at("10:00")), "ny-box-09-10")
    add_box("ny_box_10_11", "nyam_box", int(market.at("10:00")), int(market.at("11:00")), "ny-box-10-11")
    for hour in range(11, 16):
        add_box(
            f"hour_box_{hour:02d}",
            "previous_hour",
            int(market.at(f"{hour:02d}:00")),
            int(market.at(f"{hour + 1:02d}:00")),
            f"hour-box-{hour:02d}",
        )

    # The author's NY boxes stay drawn overnight: 2026-08-11's 20:40 long was
    # taken at the previous session's 09:00-10:00 box low with the PDH as the
    # objective (audit 2.1 "Entry clock"). The prior session's own window is
    # already loaded for PDH/PDL, so its boxes are measurable.
    for label, window in (("prev_ny_box_09_10", ("09:00", "10:00")), ("prev_ny_box_10_11", ("10:00", "11:00"))):
        span = _prior_session_box(market, window)
        if span is None:
            continue
        refs.append(
            {
                "id": f"{label}:{market.instrument_id}:{span['date']}",
                "kind": label,
                "branch": "nyam_box",
                "low": span["low"],
                "high": span["high"],
                "known_at": int(market.start),
                "live_from": int(market.start),
                "sides": ("long", "short"),
                "session_date": span["date"],
            }
        )
    tdo = _tdo(market)
    if tdo is not None:
        refs.append(
            {
                "id": f"tdo:{market.instrument_id}:{market.day}",
                "kind": "tdo",
                "branch": "asia_tdo_case",
                "low": tdo,
                "high": tdo,
                "known_at": int(market.at("00:00")) + MINUTE,
                "live_from": int(market.at("00:00")) + MINUTE,
                "sides": ("long", "short"),
            }
        )
    prior_day, day_omissions = _prior_session_window(market)
    omissions.extend(day_omissions)
    if prior_day is not None:
        refs.append(
            {
                "id": prior_day.get("id") or f"prior_day:{market.instrument_id}:{market.day}",
                "kind": "prior_day",
                "branch": "prior_day_level",
                "low": _dec(prior_day["low"]),
                "high": _dec(prior_day["high"]),
                "known_at": int(prior_day.get("known_at") or market.start),
                "live_from": int(market.start),
                "scope": prior_day.get("scope"),
                "sides": ("long", "short"),
            }
        )
    prior_week, week_omissions = _prior_week_range(market)
    omissions.extend(week_omissions)
    if prior_week is not None:
        refs.append(
            {
                "id": prior_week.get("id"),
                "kind": "prior_week",
                "branch": "prior_week_level",
                "low": _dec(prior_week["low"]),
                "high": _dec(prior_week["high"]),
                "known_at": int(prior_week.get("known_at") or market.start),
                "live_from": int(market.start),
                "scope": prior_week.get("scope"),
                "sides": ("long", "short"),
            }
        )
    refs = list(enumeration_point("references", refs, market=market, family="GB-FAIL") or refs)
    return refs, omissions


def objective_levels(market, refs: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Every drawn level available as an objective rung, plus TDO and the NWOG."""
    out: list[dict[str, Any]] = []
    for ref in refs:
        out.append({"price": _dec(ref["high"]), "label": f"{ref['kind']}_high", "known_at": ref["known_at"]})
        out.append({"price": _dec(ref["low"]), "label": f"{ref['kind']}_low", "known_at": ref["known_at"]})
    # The author's NY boxes stay drawn overnight: 2026-08-11's 20:40 long was
    # taken at the previous session's 09:00-10:00 box low with the PDH as the
    # objective (audit 2.1 "Entry clock"). The prior session's own window is
    # already loaded for PDH/PDL, so its boxes are measurable.
    for label, window in (("prev_ny_box_09_10", ("09:00", "10:00")), ("prev_ny_box_10_11", ("10:00", "11:00"))):
        span = _prior_session_box(market, window)
        if span is None:
            continue
        refs.append(
            {
                "id": f"{label}:{market.instrument_id}:{span['date']}",
                "kind": label,
                "branch": "nyam_box",
                "low": span["low"],
                "high": span["high"],
                "known_at": int(market.start),
                "live_from": int(market.start),
                "sides": ("long", "short"),
                "session_date": span["date"],
            }
        )
    tdo = _tdo(market)
    if tdo is not None:
        out.append({"price": tdo, "label": "tdo", "known_at": int(market.at("00:00")) + MINUTE})
    nwog = _nwog_levels(market)
    if nwog is not None:
        out.append({"price": nwog["low"], "label": "nwog_low", "known_at": nwog["known_at"]})
        out.append({"price": nwog["high"], "label": "nwog_high", "known_at": nwog["known_at"]})
    return out


def next_drawn_level(levels: Sequence[Mapping[str, Any]], *, beyond: Decimal, side: str, known_by: int) -> dict[str, Any] | None:
    """The next drawn level past ``beyond`` in the trade's direction."""
    candidates = [
        row
        for row in levels
        if int(row.get("known_at") or 0) <= int(known_by)
        and (row["price"] < beyond if side == "short" else row["price"] > beyond)
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda row: row["price"]) if side == "short" else min(candidates, key=lambda row: row["price"])


# ---------------------------------------------------------------------------
# sweep and fail


def sweep_cycles(
    market,
    *,
    level: Decimal,
    side: str,
    begin: int,
    end: int,
    box_low: Decimal | None = None,
    box_high: Decimal | None = None,
    max_cycles: int = MAX_CYCLES_PER_LEVEL,
) -> list[dict[str, Any]]:
    """Every sweep of ``level`` and the five-minute close that failed it.

    The whole sequence is read on the author's own clock: "I wait until after
    10AM", "I wait for the 5 min close back below the PDL after sweeping above
    it".  A cycle opens on the first complete five-minute bar whose extreme is
    beyond the level and closes on the first later five-minute bar that closes
    back through the level and back inside the reference's own range ("Sweep a
    level and fail back inside? I'm looking for the reversal").  A cycle whose
    failure does not arrive inside ``FAIL_WINDOW_BARS`` is recorded as ``held``
    -- the breakout the author calls continuation.
    """
    grid = five_minute_grid(market)
    stamps = sorted(t for t in grid if begin <= t < end)
    cycles: list[dict[str, Any]] = []
    index = 0
    while index < len(stamps) and len(cycles) < max_cycles:
        stamp = stamps[index]
        row = grid[stamp]
        lo, hi = _d(row.get("L")), _d(row.get("H"))
        if lo is None or hi is None:
            index += 1
            continue
        if not (hi > level if side == "short" else lo < level):
            index += 1
            continue
        sweep_at = int(row.get("start") or stamp)
        extreme = hi if side == "short" else lo
        deadline = min(int(end), stamp + FAIL_WINDOW_NS)
        fail = None
        inside = None
        cursor = index
        while cursor < len(stamps) and stamps[cursor] < deadline:
            bar = grid[stamps[cursor]]
            bar_hi, bar_lo, close = _d(bar.get("H")), _d(bar.get("L")), _d(bar.get("C"))
            if side == "short" and bar_hi is not None and bar_hi > extreme:
                extreme = bar_hi
            if side == "long" and bar_lo is not None and bar_lo < extreme:
                extreme = bar_lo
            through = close is not None and (close <= level if side == "short" else close >= level)
            if through:
                inside = None
                if box_low is not None and box_high is not None and box_low < box_high:
                    inside = box_low <= close <= box_high
                if inside is not False:
                    fail = bar
                    break
            cursor += 1
        cycle_end = int((fail or {}).get("end") or deadline)
        cycles.append(
            {
                "cycle": len(cycles),
                "sweep": row,
                "sweep_at": sweep_at,
                "extreme": extreme,
                "depth": (extreme - level) if side == "short" else (level - extreme),
                "fail": fail,
                "fail_at": None if fail is None else int(fail.get("known_at") or fail.get("end")),
                "inside_reference": inside,
                "status": "failed" if fail is not None else "held",
                "window_end": deadline,
            }
        )
        if len(cycles) >= max_cycles:
            cycles[-1]["cycles_truncated"] = True
        index = next(
            (
                i
                for i in range(index + 1, len(stamps))
                if stamps[i] >= cycle_end
                and (_d(grid[stamps[i]].get("C")) is not None)
                and ((_d(grid[stamps[i]]["C"]) <= level) if side == "short" else (_d(grid[stamps[i]]["C"]) >= level))
            ),
            len(stamps),
        )
    return cycles


def _five_minute_fail(cycle: Mapping[str, Any]) -> dict[str, Any] | None:
    return cycle.get("fail")


def failure_close(market, *, level: Decimal, side: str, cycle: Mapping[str, Any], end: int) -> dict[str, Any] | None:
    """The one-minute close back through the level: the author's fast fill.

    "Sweep a level and fail back inside? I'm looking for the reversal."  The
    five-minute close is the trigger the author states; the tickets are filled
    as the failure becomes visible on the tape inside that bar (2026-08-28:
    the 10:00 minute sweeps the 09:00-10:00 box high and closes back below it,
    and the ticket prints inside that same five-minute bar). This mode reads the
    same failure on the one-minute clock and enters at its close.
    """
    fail = _five_minute_fail(cycle)
    if fail is None:
        return None
    # G-B (coordinator guidance 2026-09-17): the cycle ends with the failure the
    # author waits for, not with the first one-minute poke back inside while
    # price is still making new extremes (2026-08-27 13:00: ours fired at 12:38
    # on the first poke; he waited for the sweep to 29,675). The one-minute read
    # is therefore taken inside the five-minute bar that failed.
    sweep_at = int(cycle["sweep_at"])
    extreme = _d(cycle.get("extreme"))
    window_end = min(int(end), int(fail.get("end") or (sweep_at + FIVE)))
    for row in _safe_bars(market, sweep_at, window_end):
        close = _d(row.get("C"))
        hi, lo = _d(row.get("H")), _d(row.get("L"))
        beyond = (hi is not None and hi > level) if side == "short" else (lo is not None and lo < level)
        if not beyond or close is None:
            continue
        through = close <= level if side == "short" else close >= level
        if through and (extreme is None or ((hi is not None and hi >= extreme) if side == "short" else (lo is not None and lo <= extreme))):
            return {"entry": close, "decision_at": int(row.get("known_at") or row.get("end")), "bar": row, "extreme": extreme}
    return {
        "entry": _d(fail.get("C")),
        "decision_at": int(fail.get("known_at") or fail.get("end")),
        "bar": fail,
        "extreme": extreme,
    }


RETEST_WINDOW_NS = 4 * HOUR


def _rejection_fill(market, *, level: Decimal, side: str, cycle: Mapping[str, Any], end: int) -> dict[str, Any] | None:
    """The author sells as the spike turns.

    Round-2 guidance (2026-08-31): the 09:31 minute closes 29,506.50 with a
    ten-point upper wick and the 09:32 bar opens 29,506.75; his fill is
    29,510.50. The fill is the open of the bar after the one-minute rejection
    candle -- the wick larger than the body, beyond the level -- not the later
    failure close.
    """
    sweep_at = int(cycle["sweep_at"])
    rows = _safe_bars(market, sweep_at, min(int(end), sweep_at + FAIL_WINDOW_NS))
    for current, following in zip(rows, rows[1:]):
        o, c = _d(current.get("O")), _d(current.get("C"))
        hi, lo = _d(current.get("H")), _d(current.get("L"))
        if None in (o, c, hi, lo):
            continue
        beyond = hi > level if side == "short" else lo < level
        if not beyond:
            continue
        body_hi, body_lo = max(o, c), min(o, c)
        wick = (hi - body_hi) if side == "short" else (body_lo - lo)
        if wick <= (body_hi - body_lo):
            continue
        entry = _d(following.get("O"))
        if entry is None:
            continue
        return {"entry": entry, "decision_at": int(following.get("known_at") or following.get("end")), "rejection_at": int(current["start"])}
    return None


def at_level_fill(market, *, level: Decimal, side: str, cycle: Mapping[str, Any], end: int) -> dict[str, Any] | None:
    """The resting limit at the level, filled on the retest after the failure.

    "Once closed below, low risk entry on any retracement with stops above PDL"
    (GB p.3). G-A (coordinator guidance 2026-09-17): the fill is the retest of
    the level, not the confirming close -- 2026-09-03 closes below the True Day
    Open at 00:30 and fills 29,238.25 at 00:45; 2026-07-13 closes below the PDL
    at 19:01 and fills at 20:40; 2026-09-14 closes above the London low at 09:35
    and fills 28,903 at 09:40. The retest is searched for the rest of the
    session, bounded at four hours, and nothing is filled before the close that
    made the failure observable.
    """
    visible = failure_close(market, level=level, side=side, cycle=cycle, end=end)
    fail = cycle.get("fail")
    stamps = [int(visible["decision_at"])] if visible is not None else []
    if fail is not None:
        stamps.append(int(fail.get("known_at") or fail.get("end")))
    if not stamps:
        return None
    from_ns = min(stamps)
    for row in _safe_bars(market, from_ns, min(int(end), from_ns + RETEST_WINDOW_NS)):
        lo, hi = _d(row.get("L")), _d(row.get("H"))
        if lo is None or hi is None or int(row.get("start") or 0) < from_ns:
            continue
        if lo <= level <= hi:
            return {"entry": level, "decision_at": int(row.get("known_at") or row.get("end")), "visible_at": from_ns}
    return None


# ---------------------------------------------------------------------------
# episode assembly


def _stage(name: str, verdict: str, at_ns: int | None, **operands: Any) -> dict[str, Any]:
    return {"stage": name, "verdict": verdict, "at_ns": at_ns, "operands": jsonable(operands)}


def _rules_for(*ids: str) -> list[dict[str, Any]]:
    out = []
    for rule_id in ids:
        row = RULES.get(rule_id)
        if not row:
            continue
        out.append({"rule_id": rule_id, **{k: v for k, v in row.items() if k != "_fn"}})
    return out


def _gate_stages(stages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blocked = None
    blocker = None
    out: list[dict[str, Any]] = []
    by_name = {row["stage"]: row for row in stages}
    for name in STAGE_ORDER:
        row = by_name.get(name)
        if row is None:
            continue
        if blocked == "fail" and row.get("verdict") == "pass":
            operands = dict(row.get("operands") or {})
            operands["blocked_by"] = blocker
            row = {**row, "verdict": "fail", "operands": operands}
        out.append(row)
        if blocked is None and row.get("verdict") == "fail":
            blocked = "fail"
            blocker = name
    return out


def _verdict_from_stages(stages: list[dict[str, Any]]) -> tuple[str, list[str], list[str]]:
    failed = [row["stage"] for row in stages if row["verdict"] == "fail"]
    unknown = [row["stage"] for row in stages if row["verdict"] == "unknown"]
    if unknown and not failed:
        return "unknown", failed, unknown
    if failed:
        return "fail", failed, unknown
    return "pass", failed, unknown


def _episode(
    market,
    *,
    family: str,
    branch: str,
    side: str,
    stages: list[dict[str, Any]],
    rules: list[dict[str, Any]],
    decision_at: int | None,
    entry: Decimal | None,
    stop: Decimal | None,
    target: Decimal | None,
    reference: Mapping[str, Any] | None,
    trigger: Mapping[str, Any] | None,
    values: dict[str, Any],
    geometry: dict[str, Any],
    scope: str = "entry_setup",
) -> dict[str, Any]:
    ordered = _gate_stages(stages)
    verdict, failed, unknown = _verdict_from_stages(ordered)
    if decision_at is None:
        decision_at = int(market.end)
        if verdict == "pass":
            verdict = "unknown"
            unknown = list(unknown) + ["decision_at"]
    # An entry may never be filled before the evidence that admitted it: the
    # decision time is the latest at_ns of every stage on the episode.
    stamps = [int(row["at_ns"]) for row in ordered if row.get("at_ns") is not None]
    evidence_at = max(stamps) if stamps else None
    if evidence_at is not None and int(decision_at) < evidence_at:
        verdict = "fail"
        failed = list(failed) + ["causality"]
        ordered = ordered + [
            {
                "stage": "confirmation",
                "verdict": "fail",
                "at_ns": evidence_at,
                "operands": {"reason": "entry_precedes_evidence", "decision_at": int(decision_at), "evidence_at": evidence_at},
            }
        ]
    identity = {
        "method": family,
        "branch": branch,
        "side": side,
        "session_date": str(market.day),
        "instrument_id": market.instrument_id,
        "reference_id": None if reference is None else reference.get("id"),
        "occurrence_at": None if trigger is None else trigger.get("start", trigger.get("at")),
        "mode": values.get("confirmation_mode"),
        "cycle": values.get("cycle"),
        "baseline": B02_VERSION,
    }
    if scope == "entry_setup":
        status = {"pass": "setup", "fail": "no_setup", "unknown": "data_unavailable"}[verdict]
    else:
        status = {"pass": "condition_present", "fail": "condition_absent", "unknown": "data_unavailable"}[verdict]
    stop_points = None if entry is None or stop is None else abs(entry - stop)
    ladder = limit_ladder(entry, target, side) if entry is not None and target is not None else []
    geometry = dict(geometry)
    geometry.update(
        {
            "entry": entry,
            "stop": stop,
            "target": target,
            "ladder": ladder,
            "first_objective": geometry.get("first_objective"),
            "far_objective": None if not ladder else ladder[-1],
            "stop_points": stop_points,
            "reward_points": None if entry is None or target is None else abs(target - entry),
            "r_multiple_at_target": None
            if entry is None or target is None or stop_points in (None, 0)
            else abs(target - entry) / stop_points,
            "risk_dollars": RISK_DOLLARS,
            "derived_quantity": derived_quantity(stop_points),
            "objective_horizon_ns": next_rth_open_ns(market, decision_at),
        }
    )
    values = dict(values)
    values.update(
        {
            "branch": branch,
            "side": side,
            "decision_at": decision_at,
            "risk_defined": None if entry is None or stop is None else sign(side) * (entry - stop) > 0,
            "objective_fixed": None if entry is None or target is None else sign(side) * (target - entry) > 0,
            "evidence_at": evidence_at,
            "confirmation_delay_ns": None if evidence_at is None else int(decision_at) - evidence_at,
        }
    )
    return jsonable(
        {
            "schema": "phase1-historical-episode-v2",
            "candidate_id": "b03:" + content_hash(identity)[:32],
            "method": family,
            "branch": branch,
            "predicate": "sequence",
            "side": side,
            "session_date": str(market.day),
            "instrument_id": market.instrument_id,
            "reference_id": identity["reference_id"],
            "trigger_id": None if trigger is None else trigger.get("bar_id", trigger.get("id")),
            "occurrence_at": identity["occurrence_at"],
            "decision_at": decision_at,
            "values": values,
            "stages": ordered,
            "rules": rules,
            "research_verdict": verdict,
            "failed": failed,
            "unknown": unknown,
            "strategy_assessment": {"status": status, "scope": scope, "baseline_version": B02_VERSION},
            "author_exact_verdict": "unknown",
            "faithful_eligible": False,
            "actual_trade": False,
            "reference": reference,
            "trigger": trigger,
            "geometry": geometry,
            "baseline_version": B02_VERSION,
            "input_sha256": (market.window.document or {}).get("input_sha256"),
        }
    )


def directional_bias(market, at_ns: int) -> dict[str, Any]:
    """G10: recorded, never a filter.

    The author's bias is a qualitative higher-timeframe lean plus the overnight
    sweep-and-reclaim; no rule is published. The two operands below are our own
    observable proxies and are carried as context only.
    """
    phase = "post_1000" if at_ns >= market.at("10:00") else "pre_1000"
    cache = getattr(market, "_gb_bias", None)
    if cache is None:
        cache = {}
        setattr(market, "_gb_bias", cache)
    if phase in cache:
        return dict(cache[phase])
    out: dict[str, Any] = {"direction": None, "prior_side": None, "box_side": None, "rule": "recorded_not_filtered"}
    prior, _omit = _prior_session_window(market)
    if prior is not None and prior.get("close") is not None:
        mid = (_dec(prior["low"]) + _dec(prior["high"])) / Decimal("2")
        out["prior_side"] = "long" if _dec(prior["close"]) >= mid else "short"
    if at_ns >= market.at("10:00"):
        box = _range(market, int(market.at("09:00")), int(market.at("10:00")), "ny-box-09-10")
        if box is not None and box.get("open") is not None and box.get("close") is not None:
            out["box_side"] = "long" if _dec(box["close"]) >= _dec(box["open"]) else "short"
    out["direction"] = out["box_side"] or out["prior_side"]
    cache[phase] = dict(out)
    return out


def _level_trade(
    market,
    *,
    family: str,
    branch: str,
    side: str,
    ref: Mapping[str, Any],
    level: Decimal,
    cycle: Mapping[str, Any],
    mode: str,
    entry: Decimal | None,
    decision_at: int | None,
    objectives: Sequence[Mapping[str, Any]],
    rule_ids: tuple[str, ...],
    extra_values: Mapping[str, Any] | None = None,
    extra_stages: Sequence[Mapping[str, Any]] | None = None,
    stop_override: Decimal | None = None,
    level_edge: str | None = None,
    target_override: Decimal | None = None,
    first_objective_override: Decimal | None = None,
) -> dict[str, Any]:
    sweep_at = int(cycle["sweep_at"])
    extreme = _d(cycle.get("extreme"))
    depth = _d(cycle.get("depth"))
    fail = cycle.get("fail")
    box_low, box_high = _d(ref.get("low")), _d(ref.get("high"))
    opposite = box_low if side == "short" else box_high
    # "Objectives are the opposite edge of the reference, then the next drawn
    # level": when the level traded is not the reference's matching edge, the
    # opposite edge can sit the wrong side of the entry, and the first rung is
    # then the next drawn level.
    if opposite is not None and sign(side) * (opposite - level) <= 0:
        opposite = None
    stop = stop_override
    if stop is None and extreme is not None:
        stop = extreme + SWEEP_STOP_BUFFER if side == "short" else extreme - SWEEP_STOP_BUFFER
    far = None
    if decision_at is not None:
        far_row = next_drawn_level(objectives, beyond=opposite if opposite is not None else level, side=side, known_by=decision_at)
        far = None if far_row is None else far_row["price"]
    if first_objective_override is not None:
        opposite = first_objective_override
    target = target_override if target_override is not None else (far if far is not None else opposite)
    bias = directional_bias(market, decision_at or sweep_at)

    location_ok = extreme is not None and depth is not None and depth > 0
    trigger_ok = cycle.get("status") == "failed"
    confirm_ok = entry is not None and decision_at is not None
    risk_ok = entry is not None and stop is not None and sign(side) * (entry - stop) > 0
    objective_ok = entry is not None and target is not None and sign(side) * (target - entry) > 0
    stop_points = None if entry is None or stop is None else abs(entry - stop)
    quantity = derived_quantity(stop_points)
    at_ns = decision_at or int(cycle.get("window_end") or sweep_at)

    stages = [
        _stage(
            "context",
            "pass",
            at_ns,
            session=session_label(market, at_ns),
            bias_direction=bias.get("direction"),
            bias_rule="recorded_not_filtered",
            reference_live_from=ref.get("live_from"),
            no_entry_window_filter=True,
        ),
        _stage(
            "reference",
            "pass",
            int(ref.get("known_at") or at_ns),
            id=ref.get("id"),
            kind=ref.get("kind"),
            box_low=box_low,
            box_high=box_high,
            level=level,
            live_from=ref.get("live_from"),
            scope=ref.get("scope"),
        ),
        _stage(
            "location",
            "pass" if location_ok else "fail",
            sweep_at,
            level=level,
            sweep_extreme=extreme,
            sweep_depth=depth,
            cycle=cycle.get("cycle"),
        ),
        _stage(
            "trigger",
            "pass" if trigger_ok else "fail",
            None if fail is None else int(fail.get("known_at") or fail.get("end")),
            status=cycle.get("status"),
            fail_close=None if fail is None else _d(fail.get("C")),
            fail_window_bars=FAIL_WINDOW_BARS,
            bars_sweep_to_fail=None
            if fail is None
            else int((int(fail.get("end")) - sweep_at) // FIVE),
        ),
        _stage(
            "confirmation",
            "pass" if confirm_ok else "fail",
            decision_at,
            mode=mode,
            entry=entry,
            reason=None if confirm_ok else f"no_fill_{mode}",
        ),
        _stage(
            "risk",
            "pass" if risk_ok else "fail",
            decision_at,
            stop=stop,
            entry=entry,
            stop_points=stop_points,
            buffer_points=str(SWEEP_STOP_BUFFER),
            risk_dollars=str(RISK_DOLLARS),
        ),
        _stage(
            "objective",
            "pass" if objective_ok else "fail",
            decision_at,
            first_objective=opposite,
            far_objective=target,
            next_drawn_level=far,
        ),
        _stage(
            "management",
            "pass" if risk_ok and objective_ok and quantity is not None else "fail",
            decision_at,
            derived_quantity=quantity,
            ladder_spacing=str(LADDER_SPACING),
            ladder_rungs=len(limit_ladder(entry, target, side)) if entry is not None and target is not None else 0,
        ),
    ]
    if extra_stages:
        by_name = {row["stage"]: row for row in stages}
        for row in extra_stages:
            current = by_name.get(row["stage"])
            if current is None:
                by_name[row["stage"]] = dict(row)
                continue
            operands = dict(current.get("operands") or {})
            operands.update(row.get("operands") or {})
            # a branch that supplies its own stage owns that stage's verdict:
            # the golden pocket's location is a zone touch, not a sweep depth.
            by_name[row["stage"]] = {**current, **row, "verdict": row.get("verdict", current.get("verdict")), "operands": operands}
        stages = [by_name[name] for name in STAGE_ORDER if name in by_name]

    values = {
        "reference_id": ref.get("id"),
        "reference_kind": ref.get("kind"),
        "reference_px": level,
        "reference_known_at": ref.get("known_at"),
        "confirmation_mode": mode,
        "cycle": cycle.get("cycle"),
        "sweep_at": sweep_at,
        "sweep_extreme": extreme,
        "sweep_depth": depth,
        "fail_at": cycle.get("fail_at"),
        "bias_recorded": True,
        "bias": bias,
        "first_objective": opposite,
        "level_edge": level_edge,
    }
    if extra_values:
        values.update(dict(extra_values))
    return _episode(
        market,
        family=family,
        branch=branch,
        side=side,
        stages=stages,
        rules=_rules_for(*rule_ids),
        decision_at=decision_at,
        entry=entry,
        stop=stop,
        target=target,
        reference=dict(ref),
        trigger=cycle.get("sweep"),
        values=values,
        geometry={"confirmation_mode": mode, "first_objective": opposite},
    )


# The play changes with the day (user instruction 2026-09-17). The author names
# the reference in play each morning from the overnight context, and the model
# follows from what price does at it: "Break out and hold? I'm looking for
# continuation. Sweep a level and fail back inside? I'm looking for the
# reversal."
PLAY_OF_BRANCH = {
    "london_box": "london_reclaim",
    "asia_box": "asia_fade",
    "asia_tdo_case": "asia_fade",
    "prior_day_level": "overnight_reclaim",
    "prior_week_level": "weekly_level",
    "nyam_box": "ny_box_fail",
    "previous_hour": "previous_hour_fail",
    "cash_open_reclaim_case": "cash_open",
    "golden_pocket": "pocket_continuation",
    "golden_pocket_continuation": "pocket_continuation",
    "continuation": "break_and_hold",
    "source_long": "vwap_continuation",
}
# "Optional: previous hour high/low if you are trading later hours" (GB p.7):
# the hour boxes are a PM reference, after the two NY boxes have played out.
PREVIOUS_HOUR_FROM = "12:00"


def session_read(market) -> dict[str, Any]:
    """The day's read and the reference it puts in play.

    Audit 2.1 "Overnight structure sets the bias": a PDL sweep-and-reclaim
    overnight sets a long bias and names the prior-day level ("Bias from
    overnight PDL sweep and reclaim. Long overnight. NYAM: buy pullbacks"); an
    Asia-high sweep after midnight names the Asia box; "after that 500-point
    overnight dump my plan was to look for a retracement toward the weekly
    opening gap" names the pocket and the NWOG. When the overnight breaks a
    session edge and holds it, the NY session is a pullback/continuation day
    rather than a "ONE MODEL" sweep-and-fail day.
    """
    cached = getattr(market, "_gb_read", None)
    if cached is not None:
        return cached
    refs = getattr(market, "_gb_refs_cache", None)
    if refs is None:
        refs, _omit = session_references(market)
        setattr(market, "_gb_refs_cache", refs)
    by_kind = {ref["kind"]: ref for ref in refs}
    open_ns = int(market.at("09:30"))
    events: list[str] = []
    bias = None
    primary = "ny_box_fail"

    prior = by_kind.get("prior_day")
    if prior is not None:
        for side, level, label in (("long", _dec(prior["low"]), "pdl"), ("short", _dec(prior["high"]), "pdh")):
            cycles = sweep_cycles(
                market,
                level=level,
                side=side,
                begin=int(market.start),
                end=open_ns,
                box_low=_dec(prior["low"]),
                box_high=_dec(prior["high"]),
                max_cycles=1,
            )
            if cycles and cycles[0]["status"] == "failed":
                events.append(f"{label}_sweep_and_reclaim")
                bias = bias or ("long" if side == "long" else "short")
                primary = "overnight_reclaim"

    asia = by_kind.get("asia_box")
    if asia is not None:
        for side, level, label in (("short", _dec(asia["high"]), "asia_high"), ("long", _dec(asia["low"]), "asia_low")):
            cycles = sweep_cycles(
                market,
                level=level,
                side=side,
                begin=int(asia["live_from"]),
                end=open_ns,
                box_low=_dec(asia["low"]),
                box_high=_dec(asia["high"]),
                max_cycles=1,
            )
            if cycles:
                events.append(f"{label}_swept")
                if primary == "ny_box_fail":
                    primary = "asia_fade"

    london = by_kind.get("london_box")
    if london is not None:
        for side, level, label in (("long", _dec(london["low"]), "london_low"), ("short", _dec(london["high"]), "london_high")):
            cycles = sweep_cycles(
                market,
                level=level,
                side=side,
                begin=int(london["live_from"]),
                end=open_ns,
                box_low=_dec(london["low"]),
                box_high=_dec(london["high"]),
                max_cycles=1,
            )
            if cycles:
                events.append(f"{label}_swept")

    overnight_high, overnight_low = excursion(market, int(market.start), open_ns)
    overnight_span = None if overnight_high is None else overnight_high - overnight_low
    open_rows = _safe_bars(market, open_ns, open_ns + MINUTE)
    open_px = _d(open_rows[0].get("O")) if open_rows else None

    held_beyond = None
    if open_px is not None:
        for ref in (asia, london):
            if ref is None:
                continue
            if open_px > _dec(ref["high"]):
                held_beyond = "up" if held_beyond in (None, "up") else "mixed"
            elif open_px < _dec(ref["low"]):
                held_beyond = "down" if held_beyond in (None, "down") else "mixed"
            else:
                held_beyond = "mixed" if held_beyond else None
                break
    day_model = "pullback_continuation" if held_beyond in {"up", "down"} else "sweep_and_fail"
    if day_model == "pullback_continuation" and primary == "ny_box_fail":
        primary = "pocket_continuation"

    plays = {"ny_box_fail", "cash_open", "asia_fade", "london_reclaim", "overnight_reclaim", "pocket_continuation"}
    week = by_kind.get("prior_week")
    reachable = None
    if week is not None and overnight_span:
        reach_low = (overnight_low or Decimal(0)) - overnight_span
        reach_high = (overnight_high or Decimal(0)) + overnight_span
        reachable = (reach_low <= _dec(week["low"]) <= reach_high) or (reach_low <= _dec(week["high"]) <= reach_high)
        if reachable:
            plays.add("weekly_level")
    plays.add("previous_hour_fail")
    if day_model == "pullback_continuation":
        plays.add("break_and_hold")
        plays.add("vwap_continuation")
    read = {
        "day_model": day_model,
        "primary_play": primary,
        "plays": sorted(plays),
        "bias": bias,
        "bias_rule": "recorded, never a filter (G10)",
        "overnight_events": events,
        "inputs": {
            "overnight_high": overnight_high,
            "overnight_low": overnight_low,
            "overnight_span": overnight_span,
            "cash_open": open_px,
            "open_beyond_session_boxes": held_beyond,
            "weekly_level_reachable": reachable,
            "previous_hour_from": PREVIOUS_HOUR_FROM,
        },
        "rule": "the overnight names the reference: a PDL/PDH sweep-and-reclaim puts the prior-day level in play, an Asia-edge sweep puts the Asia box in play; an open held beyond both session boxes makes the NY session a pullback/continuation day, otherwise it is a sweep-and-fail day",
    }
    setattr(market, "_gb_read", read)
    return read


# ---------------------------------------------------------------------------
# branch scans


def _fail_branch_episodes(market, refs: Sequence[Mapping[str, Any]], objectives: Sequence[Mapping[str, Any]], *, kinds: set[str]) -> list[dict[str, Any]]:
    episodes: list[dict[str, Any]] = []
    for ref in refs:
        if ref["kind"] not in kinds:
            continue
        begin = max(int(ref["live_from"]), int(market.start))
        end = int(market.end)
        if end <= begin:
            continue
        line_reference = ref["kind"] in {"prior_day", "prior_week", "tdo"}
        combinations = [("short", "high"), ("long", "low")]
        if line_reference:
            combinations += [("short", "low"), ("long", "high")]
        for side, edge in combinations:
            level = _dec(ref[edge])
            if _dec(ref["low"]) == _dec(ref["high"]) and edge == "high":
                continue  # a single-price reference (the True Day Open) has one level
            # "fail back inside the range" is the test when the level is the
            # reference's own edge on that side. When the author fades the far
            # edge -- "the 5 min close back below the PDL after sweeping above
            # it" -- the close he waits for is outside the prior day's range,
            # so only the close-through-the-level test applies.
            matching_edge = (side, edge) in {("short", "high"), ("long", "low")}
            for cycle in sweep_cycles(
                market,
                level=level,
                side=side,
                begin=begin,
                end=end,
                box_low=_dec(ref["low"]) if matching_edge else None,
                box_high=_dec(ref["high"]) if matching_edge else None,
            ):
                fail = cycle.get("fail")
                close_entry = None if fail is None else _d(fail.get("C"))
                close_at = None if fail is None else int(fail.get("known_at") or fail.get("end"))
                modes = [
                    ("five_minute_close", close_entry, close_at, ("GB-FAIL-five-minute-close",), None, cycle),
                ]
                minute = failure_close(market, level=level, side=side, cycle=cycle, end=end)
                # The one-minute failure is its own trigger: the mode that
                # enters on it is decided when that bar closes, not when the
                # later five-minute bar does.
                minute_cycle = cycle
                if minute is not None:
                    minute_cycle = {
                        **cycle,
                        "fail": minute["bar"],
                        "fail_at": minute["decision_at"],
                        "status": "failed",
                    }
                modes.append(
                    (
                        "failure_close_1m",
                        None if minute is None else minute["entry"],
                        None if minute is None else minute["decision_at"],
                        ("GB-FAIL-one-minute-failure-close",),
                        None,
                        minute_cycle,
                    )
                )
                rejection = _rejection_fill(market, level=level, side=side, cycle=cycle, end=end)
                modes.append(
                    (
                        "next_bar_open",
                        None if rejection is None else rejection["entry"],
                        None if rejection is None else rejection["decision_at"],
                        ("GB-FAIL-one-minute-failure-close",),
                        None,
                        minute_cycle,
                    )
                )
                fill = at_level_fill(market, level=level, side=side, cycle=cycle, end=end)
                modes.append(
                    (
                        "at_level",
                        None if fill is None else fill["entry"],
                        None if fill is None else fill["decision_at"],
                        ("GB-FAIL-limit-at-level",),
                        {"limit_visible_at_ns": None if fill is None else fill["visible_at"]},
                        minute_cycle,
                    )
                )
                # G-G: an overnight sweep is re-entered after the open at the
                # same level (2025-11-19 swept and reclaimed the previous week's
                # low at 04:18 and the author bought it at 10:00). It is a second
                # fill of the same opportunity, not a second setup.
                open_ns = int(market.at("09:30"))
                if minute is not None and int(minute["decision_at"]) < open_ns < int(end):
                    post = None
                    for row in _safe_bars(market, open_ns, min(int(end), open_ns + RETEST_WINDOW_NS)):
                        row_lo, row_hi = _d(row.get("L")), _d(row.get("H"))
                        if row_lo is None or row_hi is None:
                            continue
                        if row_lo <= level <= row_hi:
                            post = row
                            break
                    modes.append(
                        (
                            "post_open_retest",
                            None if post is None else level,
                            None if post is None else int(post.get("known_at") or post.get("end")),
                            ("GB-FAIL-limit-at-level",),
                            {"overnight_failure_at_ns": int(minute["decision_at"])},
                            minute_cycle,
                        )
                    )
                for mode, entry, at_ns, rule_ids, extra, use_cycle in modes:
                    episodes.append(
                        _level_trade(
                            market,
                            family="GB-FAIL",
                            branch=ref["branch"],
                            side=side,
                            ref=ref,
                            level=level,
                            cycle=use_cycle,
                            mode=mode,
                            level_edge=edge,
                            entry=entry,
                            decision_at=at_ns,
                            objectives=objectives,
                            rule_ids=("GB-REF-sessions-and-boxes",) + rule_ids + ("GB-RISK-stop-beyond-wick", "GB-OBJ-opposite-edge-then-next-level"),
                            extra_values=extra,
                        )
                    )
    return episodes


def _scan_nyam(market, refs, objectives) -> list[dict[str, Any]]:
    return _fail_branch_episodes(market, refs, objectives, kinds={"ny_box_09_10", "ny_box_10_11"})


def _scan_previous_hour(market, refs, objectives) -> list[dict[str, Any]]:
    """The previous hour's high and low, "if you are trading later hours".

    G-E (coordinator guidance 2026-09-17): the author's reference is the swing
    of the trailing sixty minutes, not only a completed clock hour -- 2026-04-23
    and 2026-08-27 sell at 13:00 the sweep of a high made at 12:15-12:45, and
    2026-08-13 sells at 11:45 the failure of the 11:30 spike. The rolling
    reference is re-cut every fifteen minutes and sits beside the completed
    clock-hour boxes.
    """
    gated = []
    for ref in refs:
        if not str(ref["kind"]).startswith("hour_box_"):
            continue
        item = dict(ref)
        item["live_from"] = max(int(ref["live_from"]), int(market.at(PREVIOUS_HOUR_FROM)))
        gated.append(item)
    step = 5 * MINUTE
    cursor = int(market.at("11:00"))
    session_end = int(market.at("16:00"))
    while cursor <= session_end:
        window_start = cursor - HOUR
        span = _range(market, window_start, cursor, f"trailing-hour-{cursor}")
        if span is not None:
            gated.append(
                {
                    "id": f"trailing_hour:{market.instrument_id}:{cursor}",
                    "kind": "trailing_hour",
                    "branch": "previous_hour",
                    "low": _dec(span["low"]),
                    "high": _dec(span["high"]),
                    "known_at": cursor,
                    "live_from": cursor,
                    "window": [window_start, cursor],
                    "sides": ("long", "short"),
                    "rolling": True,
                }
            )
        cursor += step
    return _fail_branch_episodes(market, gated, objectives, kinds={ref["kind"] for ref in gated})


def _scan_asia(market, refs, objectives) -> list[dict[str, Any]]:
    return _fail_branch_episodes(market, refs, objectives, kinds={"asia_box"})


def _scan_pdl(market, refs, objectives) -> list[dict[str, Any]]:
    return _fail_branch_episodes(market, refs, objectives, kinds={"prior_day"})


def _scan_pwl(market, refs, objectives) -> list[dict[str, Any]]:
    return _fail_branch_episodes(market, refs, objectives, kinds={"prior_week"})


def _scan_asia_tdo(market, refs, objectives) -> list[dict[str, Any]]:  # noqa: C901
    """The Asia-high sweep confirmed by a five-minute close through the TDO.

    Audit 2.1/2.2: "closed on the 5 minute below TDO" (2026-09-08); the variant
    sits beside the plain close-back-through-the-level mode, it does not
    replace it.
    """
    tdo = _tdo(market)
    out: list[dict[str, Any]] = _fail_branch_episodes(market, refs, objectives, kinds={"tdo"})
    asia = next((ref for ref in refs if ref["kind"] == "asia_box"), None)
    if asia is None:
        return out
    begin = max(int(asia["live_from"]), int(market.start))
    for side in ("short", "long"):
        level = _dec(asia["high"]) if side == "short" else _dec(asia["low"])
        for cycle in sweep_cycles(market, level=level, side=side, begin=begin, end=int(market.end)):
            confirm = None
            if tdo is not None:
                t = int(cycle["sweep_at"]) // FIVE * FIVE
                deadline = min(int(market.end), int(cycle["sweep_at"]) + FAIL_WINDOW_NS)
                while t + FIVE <= deadline:
                    bar = _five_min_row(market, t)
                    if _bar_complete(bar):
                        close = _d(bar.get("C"))
                        if close is not None and ((close < tdo) if side == "short" else (close > tdo)):
                            confirm = bar
                            break
                    t += FIVE
            entry = None if confirm is None else _d(confirm.get("C"))
            at_ns = None if confirm is None else int(confirm.get("known_at") or confirm.get("end"))
            out.append(
                _level_trade(
                    market,
                    family="GB-FAIL",
                    branch="asia_tdo_case",
                    side=side,
                    ref=asia,
                    level=level,
                    cycle=cycle,
                    mode="tdo_close",
                    entry=entry,
                    decision_at=at_ns,
                    objectives=objectives,
                    rule_ids=("GB-REF-sessions-and-boxes", "GB-FAIL-tdo-close"),
                    extra_values={"tdo": tdo},
                    extra_stages=[
                        _stage(
                            "confirmation",
                            "pass" if confirm is not None else ("unknown" if tdo is None else "fail"),
                            at_ns,
                            mode="tdo_close",
                            tdo=tdo,
                            reason=None if confirm is not None else ("tdo_unavailable" if tdo is None else "no_five_minute_close_through_tdo"),
                        )
                    ],
                )
            )
    return out


def _scan_london(market, refs, objectives) -> list[dict[str, Any]]:
    """The London box, with the author's post-open reclaim sequence beside it.

    2026-09-14: the London low is swept at 06:00, price makes a higher low at
    09:15 and, "after the open, price closes back above the London low. That's
    my entry."  The generic sweep/fail modes run on the same box.
    """
    out = _fail_branch_episodes(market, refs, objectives, kinds={"london_box"})
    london = next((ref for ref in refs if ref["kind"] == "london_box"), None)
    if london is None:
        return out
    open_ns = int(market.at("09:30"))
    for side in ("long", "short"):
        level = _dec(london["low"]) if side == "long" else _dec(london["high"])
        pre = sweep_cycles(market, level=level, side=side, begin=int(london["live_from"]), end=open_ns, max_cycles=1)
        if not pre:
            continue
        cycle = pre[0]
        confirm = None
        t = open_ns // FIVE * FIVE
        while t + FIVE <= int(market.end):
            bar = _five_min_row(market, t)
            if _bar_complete(bar):
                close = _d(bar.get("C"))
                if close is not None and ((close >= level) if side == "long" else (close <= level)):
                    confirm = bar
                    break
            t += FIVE
            if t > open_ns + 2 * HOUR:
                break
        entry = None if confirm is None else _d(confirm.get("C"))
        at_ns = None if confirm is None else int(confirm.get("known_at") or confirm.get("end"))
        retest_low, retest_high = excursion(market, int(cycle["sweep_at"]), min(int(market.end), open_ns))
        higher_low = None
        if side == "long" and retest_low is not None and _d(cycle.get("extreme")) is not None:
            higher_low = retest_low >= _dec(cycle["extreme"])
        out.append(
            _level_trade(
                market,
                family="GB-FAIL",
                branch="london_box",
                side=side,
                ref=london,
                level=level,
                cycle={**cycle, "status": "failed" if confirm is not None else cycle.get("status")},
                mode="post_open_reclaim",
                entry=entry,
                decision_at=at_ns,
                objectives=objectives,
                rule_ids=("GB-REF-sessions-and-boxes", "GB-FAIL-post-open-reclaim"),
                extra_values={"higher_low": higher_low, "pre_open_sweep": True},
                extra_stages=[
                    _stage(
                        "confirmation",
                        "pass" if confirm is not None else "fail",
                        at_ns,
                        mode="post_open_reclaim",
                        reason=None if confirm is not None else "no_post_open_close_back_through",
                        higher_low=higher_low,
                    )
                ],
            )
        )
    return out


def _scan_cash_open(market, refs, objectives) -> list[dict[str, Any]]:
    """G4/G-C: the 09:30 manipulation, the reclaim, and the retracement.

    "9:30am manipulation below, reclaim, enter for longs targeting retracement
    into discount, stops at lows" (GB p.3). G-C (coordinator guidance
    2026-09-17): the reference the open reaction sweeps is the pre-open range --
    the 09:00-09:30 extremes, the 06:00-09:30 extremes and the overnight
    extremes -- and the fill is the limit at that level, not the open print
    (2026-08-31 sells 29,510.5 at the swept pre-open high at 09:33, not 29,467
    at the open). This is the one play in which the 09:00-09:30 range is a
    reference; the 09:00-10:00 box itself stays "after 10AM".
    """
    open_rows = _safe_bars(market, int(market.at("09:30")), int(market.at("09:31")))
    if not open_rows:
        return []
    open_px = _d(open_rows[0].get("O"))
    if open_px is None:
        return []
    windows = {
        "pre_open_09_0930": (int(market.at("09:00")), int(market.at("09:30"))),
        "pre_open_06_0930": (int(market.at("06:00")), int(market.at("09:30"))),
        "overnight": (int(market.start), int(market.at("09:30"))),
    }
    spans = {}
    for name, (start, stop) in windows.items():
        span = _range(market, start, stop, f"gb-{name}")
        if span is not None:
            spans[name] = span
    if not spans:
        return []
    pre = spans.get("pre_open_06_0930") or next(iter(spans.values()))
    pre_low, pre_high = _dec(pre["low"]), _dec(pre["high"])
    out: list[dict[str, Any]] = []
    end = min(int(market.end), int(market.at("11:00")))
    seen: set[tuple] = set()
    levels = [("cash_open", open_px)]
    for name, span in spans.items():
        levels.append((f"{name}_high", _dec(span["high"])))
        levels.append((f"{name}_low", _dec(span["low"])))
    for side in ("long", "short"):
        for level_name, level_px in levels:
            key = (side, str(level_px))
            if key in seen:
                continue
            seen.add(key)
            ref = {
                "id": f"cash_open:{market.instrument_id}:{market.day}:{level_name}",
                "kind": "cash_open",
                "branch": "cash_open_reclaim_case",
                "low": pre_low,
                "high": pre_high,
                "known_at": int(market.at("09:30")),
                "live_from": int(market.at("09:30")),
            }
            cycles = sweep_cycles(
                market, level=level_px, side=side,
                begin=int(market.at("09:30")), end=end,
                box_low=pre_low, box_high=pre_high, max_cycles=1,
            )
            if not cycles:
                continue
            cycle = cycles[0]
            extreme = _d(cycle.get("extreme"))
            stop = None if extreme is None else (extreme - SWEEP_STOP_BUFFER if side == "long" else extreme + SWEEP_STOP_BUFFER)
            pocket = pocket_in_leg_direction(pre_low, pre_high, side)
            first = pocket[0] if side == "long" else pocket[1]
            target = pre_high if side == "long" else pre_low
            minute = failure_close(market, level=level_px, side=side, cycle=cycle, end=end)
            use_cycle = cycle if minute is None else {**cycle, "fail": minute["bar"], "fail_at": minute["decision_at"], "status": "failed"}
            fill = at_level_fill(market, level=level_px, side=side, cycle=cycle, end=end)
            rejection = _rejection_fill(market, level=level_px, side=side, cycle=cycle, end=end)
            modes = [
                ("at_level", None if fill is None else fill["entry"], None if fill is None else fill["decision_at"]),
                ("failure_close_1m", None if minute is None else minute["entry"], None if minute is None else minute["decision_at"]),
                ("next_bar_open", None if rejection is None else rejection["entry"], None if rejection is None else rejection["decision_at"]),
            ]
            for mode, entry, at_ns in modes:
                out.append(
                    _level_trade(
                        market,
                        family="GB-FAIL",
                        branch="cash_open_reclaim_case",
                        side=side,
                        ref=ref,
                        level=level_px,
                        cycle=use_cycle,
                        mode=mode,
                        entry=entry,
                        decision_at=at_ns,
                        objectives=objectives,
                        rule_ids=("GB-CASH-OPEN-reclaim",),
                        stop_override=stop,
                        target_override=target,
                        first_objective_override=first,
                        extra_values={
                            "cash_open": open_px,
                            "pre_open_range": [pre_low, pre_high],
                            "retracement_first_rung": first,
                            "cash_open_level": level_name,
                        },
                        extra_stages=[
                            _stage(
                                "objective",
                                "pass" if entry is not None and sign(side) * (target - entry) > 0 else "fail",
                                at_ns,
                                first_objective=first,
                                far_objective=target,
                                rule="retracement of the pre-open range, then its extreme",
                            )
                        ],
                    )
                )
    return out


def _impulse_leg(market, *, end_ns: int | None = None) -> dict[str, Any] | None:
    """G8: the impulse that made the day's session extreme, either direction.

    The leg runs from the session extreme back to the swing extreme that
    preceded it. Round-2 guidance: that origin is searched back through the
    prior RTH session -- 2026-07-29's overnight dump measures from the prior
    RTH high near 27,935 down to the 18:00 low 27,190, and its 61.8% is the
    author's 27,650 pocket line; a leg confined to 18:00-00:00 cannot produce
    it.
    """
    end = int(end_ns or market.at("11:00"))
    rows = _safe_bars(market, int(market.start), end)
    prior_rows: list[dict[str, Any]] = []
    sessions = prior_sessions(market, 1)
    if sessions:
        win = sessions[0].get("window")
        if win is not None:
            day = date.fromisoformat(sessions[0]["date"])
            try:
                prior_rows = list(win.bars(clock(day, "09:30"), clock(day, "16:00"), 300) or [])
            except Exception:
                prior_rows = []
    rows = prior_rows + list(rows)
    if len(rows) < 10:
        return None
    high_row = max(rows, key=lambda r: _dec(r["H"]) if r.get("H") is not None else Decimal("-1e12"))
    low_row = min(rows, key=lambda r: _dec(r["L"]) if r.get("L") is not None else Decimal("1e12"))
    hi_at, lo_at = int(high_row["start"]), int(low_row["start"])
    if hi_at > lo_at:
        leg = {"kind": "up", "low": _dec(low_row["L"]), "high": _dec(high_row["H"]), "start": lo_at, "end": int(high_row["end"])}
    else:
        leg = {"kind": "down", "low": _dec(low_row["L"]), "high": _dec(high_row["H"]), "start": hi_at, "end": int(low_row["end"])}
    if leg["high"] - leg["low"] <= 0:
        return None
    leg["side"] = "long" if leg["kind"] == "up" else "short"
    return leg


def _scan_golden_pocket(market, refs, objectives, *, family: str, branch: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for end_label, end_ns in (("overnight", int(market.at("02:00"))), ("nyam", int(market.at("11:00")))):
        out.extend(_pocket_for_leg(market, refs, objectives, family=family, branch=branch, end_ns=end_ns, label=end_label))
    return out


def _pocket_for_leg(market, refs, objectives, *, family: str, branch: str, end_ns: int, label: str) -> list[dict[str, Any]]:
    leg = _impulse_leg(market, end_ns=end_ns)
    if leg is None:
        return []
    side = "long" if leg["kind"] == "up" else "short"
    pocket = pocket_in_leg_direction(leg["low"], leg["high"], side)
    lo, hi = pocket
    ref = {
        "id": f"golden_pocket:{market.instrument_id}:{market.day}:{label}:{leg['kind']}",
        "kind": "golden_pocket",
        "branch": branch,
        "low": lo,
        "high": hi,
        "known_at": int(leg["end"]),
        "live_from": int(leg["end"]),
        "impulse": [leg["low"], leg["high"]],
    }
    touch = None
    for row in _safe_bars(market, int(leg["end"]), int(market.end)):
        row_lo, row_hi = _d(row.get("L")), _d(row.get("H"))
        if row_lo is None or row_hi is None:
            continue
        if row_lo <= hi and row_hi >= lo:
            touch = row
            break
    confirm = None
    if touch is not None:
        near = near_edge(pocket, side)
        t = int(touch["start"]) // FIVE * FIVE
        deadline = min(int(market.end), int(touch["start"]) + FAIL_WINDOW_NS)
        while t + FIVE <= deadline:
            bar = _five_min_row(market, t)
            if _bar_complete(bar):
                close = _d(bar.get("C"))
                if close is not None and ((close > near) if side == "long" else (close < near)):
                    confirm = bar
                    break
            t += FIVE
    entry = None if confirm is None else _d(confirm.get("C"))
    at_ns = None if confirm is None else int(confirm.get("known_at") or confirm.get("end"))
    far = far_edge(pocket, side)
    # G8: the stop is beyond the zone, not on its 50% line.
    stop = (far - SWEEP_STOP_BUFFER) if side == "long" else (far + SWEEP_STOP_BUFFER)
    target = leg["high"] if side == "long" else leg["low"]
    cycle = {
        "cycle": 0,
        "sweep": touch,
        "sweep_at": int((touch or {}).get("start") or leg["end"]),
        "extreme": None if touch is None else (_d(touch.get("L")) if side == "long" else _d(touch.get("H"))),
        "depth": Decimal("0") if touch is not None else None,
        "fail": confirm,
        "fail_at": at_ns,
        "status": "failed" if confirm is not None else "held",
        "window_end": int(market.end),
    }
    episode = _level_trade(
        market,
        family=family,
        branch=branch,
        side=side,
        ref=ref,
        level=near_edge(pocket, side),
        cycle=cycle,
        mode="pocket_close",
        entry=entry,
        decision_at=at_ns,
        objectives=objectives,
        rule_ids=("GB-POCKET-impulse-both-directions",),
        stop_override=stop,
        extra_values={"pocket": [lo, hi], "impulse": [leg["low"], leg["high"]], "impulse_kind": leg["kind"], "leg_window": label},
        extra_stages=[
            _stage(
                "location",
                "pass" if touch is not None else "fail",
                None if touch is None else int(touch["start"]),
                pocket_low=lo,
                pocket_high=hi,
                reason=None if touch is not None else "no_pocket_touch",
            ),
            _stage(
                "trigger",
                "pass" if touch is not None else "fail",
                None if touch is None else int(touch["start"]),
                status="pocket_touch" if touch is not None else "no_touch",
            ),
            _stage(
                "objective",
                "pass" if entry is not None and sign(side) * (target - entry) > 0 else "fail",
                at_ns,
                first_objective=target,
                far_objective=target,
                rule="the impulse extreme",
            ),
        ],
    )
    return [episode]


def _scan_continuation(market, refs, objectives) -> list[dict[str, Any]]:
    """G9: break and close beyond a box edge, hold, retest of the edge, entry.

    "Break out and hold? I'm looking for continuation." (2026-09-15); 2026-09-10
    long 29,222 on the retest of the broken 09:00-10:00 high 29,200.
    """
    out: list[dict[str, Any]] = []
    for ref in refs:
        if ref["kind"] not in {"asia_box", "london_box", "ny_box_09_10", "ny_box_10_11", "prior_day"}:
            continue
        begin = max(int(ref["live_from"]), int(market.start))
        for side in ("long", "short"):
            level = _dec(ref["high"]) if side == "long" else _dec(ref["low"])
            closes: list[dict[str, Any]] = []
            t = begin // FIVE * FIVE
            hold = None
            while t + FIVE <= int(market.end):
                bar = _five_min_row(market, t)
                t += FIVE
                if not _bar_complete(bar):
                    continue
                close = _d(bar.get("C"))
                if close is None:
                    continue
                beyond = close > level if side == "long" else close < level
                if beyond:
                    closes.append(bar)
                    if len(closes) >= CONTINUATION_HOLD_BARS:
                        hold = bar
                        break
                else:
                    closes = []
            retest = None
            if hold is not None:
                for row in _safe_bars(market, int(hold["end"]), int(market.end)):
                    row_lo, row_hi = _d(row.get("L")), _d(row.get("H"))
                    if row_lo is None or row_hi is None:
                        continue
                    if row_lo <= level <= row_hi:
                        retest = row
                        break
                    broke = row_lo < level if side == "long" else row_hi > level
                    if broke:
                        break
            entry = None if retest is None else level
            at_ns = None if retest is None else int(retest.get("known_at") or retest.get("end"))
            stop = None
            if retest is not None:
                stop = (_dec(retest["L"]) - SWEEP_STOP_BUFFER) if side == "long" else (_dec(retest["H"]) + SWEEP_STOP_BUFFER)
            far_row = None if at_ns is None else next_drawn_level(objectives, beyond=level, side=side, known_by=at_ns)
            target = None if far_row is None else far_row["price"]
            cycle = {
                "cycle": 0,
                "sweep": hold,
                "sweep_at": int((hold or {}).get("start") or begin),
                "extreme": level,
                "depth": Decimal("0"),
                "fail": retest,
                "fail_at": at_ns,
                "status": "failed" if retest is not None else "held",
                "window_end": int(market.end),
            }
            out.append(
                _level_trade(
                    market,
                    family="GB-FAIL",
                    branch="continuation",
                    side=side,
                    ref=ref,
                    level=level,
                    cycle=cycle,
                    mode="break_and_hold_retest",
                    entry=entry,
                    decision_at=at_ns,
                    objectives=objectives,
                    rule_ids=("GB-CONTINUATION-break-hold-retest",),
                    stop_override=stop,
                    extra_values={"hold_bars": CONTINUATION_HOLD_BARS},
                    extra_stages=[
                        _stage(
                            "location",
                            "pass" if hold is not None else "fail",
                            None if hold is None else int(hold.get("start") or begin),
                            level=level,
                            edge="broken and held",
                            reason=None if hold is not None else "no_close_beyond_the_edge",
                        ),
                        _stage(
                            "trigger",
                            "pass" if hold is not None else "fail",
                            None if hold is None else int(hold.get("known_at") or hold.get("end")),
                            status="held" if hold is not None else "no_hold",
                            hold_bars=CONTINUATION_HOLD_BARS,
                        ),
                        _stage(
                            "confirmation",
                            "pass" if retest is not None else "fail",
                            at_ns,
                            mode="break_and_hold_retest",
                            reason=None if retest is not None else "no_retest_of_broken_edge",
                        ),
                        _stage(
                            "objective",
                            "pass" if entry is not None and target is not None and sign(side) * (target - entry) > 0 else "fail",
                            at_ns,
                            first_objective=target,
                            far_objective=target,
                            rule="the next drawn level",
                        ),
                    ],
                )
            )
    return out


VWAP_STOP_POINTS = Decimal("30")


def _scan_vwap(market, refs, objectives) -> list[dict[str, Any]]:
    """GB-VWAP, the single published example (2026-02-24).

    "Broke & closed above London + Asia highs -> retraced into VWAP -> long
    entry. 30-point stop. Continuation play"; "I only look at VWAP when I'm
    considering a Continuation trade".
    """
    asia = next((ref for ref in refs if ref["kind"] == "asia_box"), None)
    london = next((ref for ref in refs if ref["kind"] == "london_box"), None)
    if asia is None or london is None:
        return []
    level = max(_dec(asia["high"]), _dec(london["high"]))
    ref = {
        "id": f"vwap_continuation:{market.instrument_id}:{market.day}",
        "kind": "vwap_continuation",
        "branch": "source_long",
        "low": min(_dec(asia["low"]), _dec(london["low"])),
        "high": level,
        "known_at": max(int(asia["known_at"]), int(london["known_at"])),
        "live_from": int(market.at("09:30")),
    }
    breakout = None
    t = int(market.at("09:30")) // FIVE * FIVE
    while t + FIVE <= int(market.end):
        bar = _five_min_row(market, t)
        t += FIVE
        if not _bar_complete(bar):
            continue
        close = _d(bar.get("C"))
        if close is not None and close > level:
            breakout = bar
            break
    retest = None
    vw = None
    if breakout is not None:
        for row in _safe_bars(market, int(breakout["end"]), int(market.end)):
            snapshot = market.vwap(int(row["start"]))
            price = _d((snapshot or {}).get("price"))
            if price is None:
                continue
            if _dec(row["L"]) <= price <= _dec(row["H"]):
                retest, vw = row, snapshot
                break
    entry = None if retest is None else _d(retest.get("C"))
    at_ns = None if retest is None else int(retest.get("known_at") or retest.get("end"))
    stop = None if entry is None else entry - VWAP_STOP_POINTS
    far_row = None if at_ns is None else next_drawn_level(objectives, beyond=level, side="long", known_by=at_ns)
    target = None if far_row is None else far_row["price"]
    cycle = {
        "cycle": 0,
        "sweep": breakout,
        "sweep_at": int((breakout or {}).get("start") or market.at("09:30")),
        "extreme": level,
        "depth": Decimal("0"),
        "fail": retest,
        "fail_at": at_ns,
        "status": "failed" if retest is not None else "held",
        "window_end": int(market.end),
    }
    return [
        _level_trade(
            market,
            family="GB-VWAP",
            branch="source_long",
            side="long",
            ref=ref,
            level=level,
            cycle=cycle,
            mode="vwap_retest",
            entry=entry,
            decision_at=at_ns,
            objectives=objectives,
            rule_ids=("GB-VWAP-continuation",),
            stop_override=stop,
            extra_values={"vwap_at_retest": None if vw is None else _d(vw.get("price")), "breakout_level": level},
            extra_stages=[
                _stage(
                    "location",
                    "pass" if breakout is not None else "fail",
                    None if breakout is None else int(breakout.get("start") or market.at("09:30")),
                    level=level,
                    edge="max(Asia high, London high)",
                    reason=None if breakout is not None else "no_close_above_both_session_highs",
                ),
                _stage(
                    "trigger",
                    "pass" if breakout is not None else "fail",
                    None if breakout is None else int(breakout.get("known_at") or breakout.get("end")),
                    status="closed_above_asia_and_london_highs" if breakout is not None else "no_breakout_close",
                ),
                _stage(
                    "confirmation",
                    "pass" if retest is not None else "fail",
                    at_ns,
                    mode="vwap_retest",
                    reason=None if retest is not None else "no_vwap_retest",
                ),
            ],
        )
    ]


def _scan_scalp_observation(market, branch: str) -> list[dict[str, Any]]:
    """F01: the two old scalp branches stay observations, never entries."""
    stages = [
        _stage("context", "pass", int(market.at("09:30")), session="ny_am"),
        _stage("reference", "unknown", None, reason="scalp_observation_only"),
    ]
    return [
        _episode(
            market,
            family="GB-SCALP",
            branch=branch,
            side="long" if "bullish" in branch else "short",
            stages=stages,
            rules=_rules_for("GB-SCALP-observations"),
            decision_at=int(market.at("09:30")),
            entry=None,
            stop=None,
            target=None,
            reference=None,
            trigger=None,
            values={"confirmation_mode": None, "observation_only": True},
            geometry={},
            scope="observation",
        )
    ]


SCANNERS = {
    ("GB-FAIL", "london_box"): _scan_london,
    ("GB-FAIL", "asia_box"): _scan_asia,
    ("GB-FAIL", "asia_tdo_case"): _scan_asia_tdo,
    ("GB-FAIL", "prior_day_level"): _scan_pdl,
    ("GB-FAIL", "prior_week_level"): _scan_pwl,
    ("GB-FAIL", "nyam_box"): _scan_nyam,
    ("GB-FAIL", "previous_hour"): _scan_previous_hour,
    ("GB-FAIL", "cash_open_reclaim_case"): _scan_cash_open,
    ("GB-FAIL", "golden_pocket"): lambda m, r, o: _scan_golden_pocket(m, r, o, family="GB-FAIL", branch="golden_pocket"),
    ("GB-FAIL", "continuation"): _scan_continuation,
    ("GB-VWAP", "source_long"): _scan_vwap,
    ("GB-SCALP", "golden_pocket_continuation"): lambda m, r, o: _scan_golden_pocket(
        m, r, o, family="GB-SCALP", branch="golden_pocket_continuation"
    ),
}

# The author's clock: a drawn reference stays live until swept, at any hour, so
# the selection clock is the whole session the scan can observe.
SELECTION_CLOCK = ("18:00", -1, "16:00", 0)


def _document(
    market,
    family: str,
    branch: str,
    episodes: list[dict[str, Any]],
    *,
    omissions: list | None = None,
    selection: Mapping[str, Any] | None = None,
    day_read: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    counts = {key: sum(ep["research_verdict"] == key for ep in episodes) for key in ("pass", "fail", "unknown")}
    try:
        coverage = market.coverage(market.at("09:30"), market.end)
    except Exception:
        coverage = {"observed_scope_complete": False}
    bias_recorded = sum(1 for ep in episodes if (ep.get("values") or {}).get("bias_recorded"))
    return jsonable(
        {
            "method_id": family,
            "branch": branch,
            "session_date": str(market.day),
            "instrument_id": market.instrument_id,
            "population_scope": "owned_observed_events",
            "population_complete": bool((coverage or {}).get("observed_scope_complete")) and not omissions,
            "coverage": coverage,
            "N_observed": len(episodes),
            "n": counts["pass"] + counts["fail"],
            "p": counts["pass"],
            "f": counts["fail"],
            "u": counts["unknown"],
            "episodes": episodes,
            "omissions": list(omissions or []),
            "baseline_version": B02_VERSION,
            "clock_zone_unverified": False,
            "coverage_id": f"{family}:branch:{branch}",
            "rules": _rules_for(*RULES),
            "bias": {"recorded": bias_recorded, "filtered": False, "rule_id": "GB-BIAS-recorded-not-filtered"},
            "selection": selection,
            "day_read": day_read,
            "input_sha256": (market.window.document or {}).get("input_sha256"),
        }
    )


def selection_for(market, episodes: Sequence[Mapping[str, Any]], *, primary_play: str | None = None) -> dict[str, Any]:
    """The author's trade list: the chosen play first, at most three entries."""
    start = int(market.at(SELECTION_CLOCK[0], SELECTION_CLOCK[1]))
    end = int(market.at(SELECTION_CLOCK[2], SELECTION_CLOCK[3]))
    bars = _safe_bars(market, int(market.start), int(market.end))
    chosen = [ep for ep in episodes if (ep.get("values") or {}).get("play") == primary_play] if primary_play else list(episodes)
    result = select_session_trades(chosen, bars=bars, clock=(start, end), max_entries=MAX_ENTRIES_PER_SESSION)
    fallback = False
    if not result["n_entries"] and primary_play:
        rest = [ep for ep in episodes if (ep.get("values") or {}).get("play") != primary_play]
        if rest:
            result = select_session_trades(rest, bars=bars, clock=(start, end), max_entries=MAX_ENTRIES_PER_SESSION)
            fallback = bool(result["n_entries"])
    result["primary_play"] = primary_play
    result["fallback_play_used"] = fallback
    return result


def scan_b02(market, rec: Mapping[str, Any] | None = None, *, overrides=None) -> dict[str, Any]:
    with enumeration_scope(overrides):
        return _scan_b02_impl(market, rec, overrides=overrides)


def _scan_b02_impl(market, rec: Mapping[str, Any] | None = None, *, overrides=None) -> dict[str, Any]:
    stage_overrides, _enum = split_b02_overrides(overrides)

    def finish(doc):
        if not stage_overrides:
            return doc
        from trading_research.research.rule_discovery.search import finish_scan_b02

        return finish_scan_b02(doc, stage_overrides)

    rec = {key: value for key, value in dict(rec or {}).items() if key in REC_IDENTITY_KEYS}
    family = rec.get("family") or rec.get("method_id") or "GB-FAIL"
    branch = rec.get("branch")
    branches = B02_BRANCHES.get(family, ())
    if branch in SCALP_OBSERVATIONS and family == "GB-SCALP":
        return finish(_document(market, family, branch, _scan_scalp_observation(market, branch)))
    selected = list(branches) if branch in {None, "*", "all", "B0.2", "B0.3"} else [branch]
    refs, omissions = session_references(market)
    setattr(market, "_gb_refs_cache", refs)
    objectives = objective_levels(market, refs)
    read = session_read(market)
    allowed = set(read.get("plays") or ())
    episodes: list[dict[str, Any]] = []
    used: list[str] = []
    for name in selected:
        fn = SCANNERS.get((family, name))
        if fn is None:
            omissions.append({"reason": "unknown_b02_branch", "branch": name})
            continue
        play = PLAY_OF_BRANCH.get(name)
        if play not in allowed:
            omissions.append({"reason": "play_not_in_the_day_read", "branch": name, "play": play, "day_model": read.get("day_model")})
            continue
        used.append(name)
        try:
            episodes.extend(fn(market, refs, objectives))
        except Exception as exc:
            omissions.append({"reason": "scan_error", "branch": name, "error": f"{type(exc).__name__}: {exc}"})
    episodes = list(enumeration_point("contacts", episodes, market=market, family=family) or episodes)
    for episode in episodes:
        episode["values"]["play"] = PLAY_OF_BRANCH.get(episode.get("branch"))
        episode["values"]["is_primary_play"] = episode["values"]["play"] == read.get("primary_play")
    label = used[0] if len(used) == 1 else "B0.3"
    selection = selection_for(market, episodes, primary_play=read.get("primary_play"))
    return finish(_document(market, family, label, episodes, omissions=omissions, selection=selection, day_read=read))


def funnel_from_document(document: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, dict[str, dict[str, int]]] = {}
    for ep in document.get("episodes") or []:
        branch = ep.get("branch") or document.get("branch")
        bucket = out.setdefault(branch, {name: {"pass": 0, "fail": 0, "unknown": 0} for name in STAGE_ORDER})
        for row in ep.get("stages") or []:
            name = row.get("stage")
            if name not in bucket:
                continue
            verdict = row.get("verdict") or "unknown"
            if verdict not in bucket[name]:
                verdict = "unknown"
            bucket[name][verdict] += 1
    return {
        "branch": document.get("branch"),
        "family": document.get("method_id"),
        "counts": {
            "pass": document.get("p"),
            "fail": document.get("f"),
            "unknown": document.get("u"),
            "episodes": document.get("N_observed"),
        },
        "bias": document.get("bias"),
        "selection": document.get("selection"),
        "stages": out,
    }


# ---------------------------------------------------------------------------
# author-example replay


def _example_actions(example: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [row for row in (example.get("actions") or []) if isinstance(row, Mapping)]


def proper_entries(example: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The author's proper entries: the marked trades, not every fill.

    Green Bird's proper entry is the one marked with the TradingView
    risk-reward tool (entry line, red stop box, green target box); a chart that
    shows only limit rungs or a P&L card has no proper entry to match.
    """
    out = []
    for row in _example_actions(example):
        if not row.get("proper_entry"):
            continue
        action = str(row.get("action") or "")
        side = "long" if action == "buy" else "short" if action == "sell" else row.get("side")
        out.append(
            {
                "time_et": row.get("time_et"),
                "date": row.get("date") or example.get("date"),
                "side": side,
                "price": _d(row.get("price")),
                "stop": _d(row.get("stop")),
                "target": _d(row.get("target")),
                "branch": row.get("branch"),
                "reference": row.get("reference"),
                "marked_by": row.get("marked_by"),
                "note": row.get("note"),
            }
        )
    return out


def other_fills(example: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {"time_et": row.get("time_et"), "action": row.get("action"), "price": row.get("price"), "note": row.get("note")}
        for row in _example_actions(example)
        if row.get("price") is not None and not row.get("proper_entry")
    ]


def _entry_ns(market, date_text: str | None, time_et: str | None) -> int | None:
    if not time_et:
        return None
    token = str(time_et).split("-")[0].split("(")[0].strip()
    parts = token.split(":")
    if len(parts) < 2:
        return None
    try:
        hour, minute = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    day = market.day
    if date_text:
        try:
            day = date.fromisoformat(str(date_text)[:10])
        except ValueError:
            day = market.day
    offset = (day - market.day).days
    if hour >= 18:
        offset -= 1
    try:
        return int(market.at(f"{hour:02d}:{minute:02d}", offset))
    except Exception:
        return None


def _bars_from_window(at_ns: int, window: tuple[int, int]) -> float:
    """Distance from the printed window, in five-minute bars; zero inside it."""
    if window[0] <= at_ns <= window[1]:
        return 0.0
    gap = window[0] - at_ns if at_ns < window[0] else at_ns - window[1]
    return gap / FIVE


def _printed_window_ns(market, date_text, time_et) -> tuple[int, int] | None:
    """The printed entry time, or the printed window when the post gives a range.

    Charts are read to the minute the author drew, and several posts print a
    window ("09:40-09:50", "03:00-04:00") rather than a fill time. The window is
    the acceptance band; a single stamp is the stamp.
    """
    if not time_et:
        return None
    text = str(time_et)
    first = _entry_ns(market, date_text, text)
    if first is None:
        return None
    tail = text.split("-", 1)[1].strip() if "-" in text else None
    last = _entry_ns(market, date_text, tail) if tail else None
    if last is None or last < first:
        last = first
    return first, last


def match_entry(
    market,
    episodes: Sequence[Mapping[str, Any]],
    entry: Mapping[str, Any],
    *,
    strict_points: Decimal = LEVEL_TOLERANCE,
) -> dict[str, Any]:
    """Does any episode produce this printed entry, on this side, at this time?"""
    window = _printed_window_ns(market, entry.get("date"), entry.get("time_et"))
    want_ns = None if window is None else window[0]
    price = entry.get("price")
    side = entry.get("side")
    risk = None
    if price is not None and entry.get("stop") is not None:
        risk = abs(_dec(entry["stop"]) - _dec(price))
    tolerance = risk if risk is not None else TICKET_RISK_FALLBACK
    want_play = PLAY_OF_BRANCH.get(entry.get("branch"))
    rows = []
    for ep in episodes:
        if ep.get("research_verdict") != "pass" or ep.get("side") != side:
            continue
        if want_play is not None and PLAY_OF_BRANCH.get(ep.get("branch")) != want_play:
            continue
        got = _d((ep.get("geometry") or {}).get("entry"))
        at_ns = ep.get("decision_at")
        if got is None or at_ns is None:
            continue
        dt_bars = None if window is None else _bars_from_window(int(at_ns), window)
        delta = None if price is None else abs(got - _dec(price))
        rows.append(
            {
                "episode": ep,
                "entry": got,
                "at_ns": int(at_ns),
                "delta_points": delta,
                "bars_from_printed": dt_bars,
                "branch": ep.get("branch"),
                "mode": (ep.get("values") or {}).get("confirmation_mode"),
                "reference_kind": (ep.get("values") or {}).get("reference_kind"),
            }
        )
    # R2 (coordinator round 2): a ticket time is a stamp and keeps one
    # five-minute bar; a time read off a chart is a chart read and gets three.
    bars_allowed = 1.0 if entry.get("marked_by") == "rr_tool" else 3.0
    in_time = [row for row in rows if row["bars_from_printed"] is not None and row["bars_from_printed"] <= bars_allowed]
    want_branch = entry.get("branch")
    if in_time:
        scored = sorted(
            in_time,
            key=lambda row: (
                0 if want_branch and row["branch"] == want_branch else 1,
                Decimal("1e9") if row["delta_points"] is None else row["delta_points"],
            ),
        )
    else:
        scored = sorted(
            rows,
            key=lambda row: (
                9e9 if row["bars_from_printed"] is None else row["bars_from_printed"],
                0 if want_branch and row["branch"] == want_branch else 1,
            ),
        )
    best = scored[0] if scored else None
    no_price = price is None
    detected_strict = bool(
        best
        and best["delta_points"] is not None
        and best["delta_points"] <= strict_points
        and best["bars_from_printed"] is not None
        and best["bars_from_printed"] <= bars_allowed
    )
    play_ok = None if best is None else PLAY_OF_BRANCH.get(best["branch"]) == want_play
    detected_risk = bool(
        best
        and (no_price or (best["delta_points"] is not None and best["delta_points"] <= tolerance))
        and best["bars_from_printed"] is not None
        and best["bars_from_printed"] <= bars_allowed
    )
    detected_3 = bool(
        best
        and (no_price or (best["delta_points"] is not None and best["delta_points"] <= tolerance))
        and best["bars_from_printed"] is not None
        and best["bars_from_printed"] <= 3.0
    )
    return {
        "printed_time_et": entry.get("time_et"),
        "printed_price": None if price is None else float(_dec(price)),
        "printed_side": side,
        "printed_stop": None if entry.get("stop") is None else float(_dec(entry["stop"])),
        "marked_by": entry.get("marked_by"),
        "expected_branch": entry.get("branch"),
        "tolerance_points": float(tolerance),
        "strict_points": float(strict_points),
        "no_printed_level": no_price,
        "detected": detected_risk,
        "detected_strict": detected_strict,
        "detected_within_3_bars": detected_3,
        "our_entry": None if best is None else float(best["entry"]),
        "our_entry_ns": None if best is None else best["at_ns"],
        "our_branch": None if best is None else best["branch"],
        "our_mode": None if best is None else best["mode"],
        "our_reference": None if best is None else best["reference_kind"],
        "our_play": None if best is None else PLAY_OF_BRANCH.get(best["branch"]),
        "expected_play": want_play,
        "play_matches": play_ok,
        "delta_points": None if best is None or best["delta_points"] is None else float(best["delta_points"]),
        "bars_from_printed": None if best is None or best["bars_from_printed"] is None else float(best["bars_from_printed"]),
        "n_pass_episodes": len(rows),
        "bars_allowed": bars_allowed,
        "fills_tested": sorted({str(row["mode"]) for row in rows}),
        "matched_fill": None if best is None else best["mode"],
    }


def _date_outside_tape(example: Mapping[str, Any]) -> bool:
    """Is this example's session outside the owned calendar?

    An example that is outside it is answered without touching the window cache,
    so an after-tape replay never builds an event window.
    """
    from trading_research.research.rule_discovery.source_adapters.common import is_native_session

    if example.get("inside_tape") is False:
        return True
    try:
        day = date.fromisoformat(str(example.get("date") or "")[:10])
    except Exception:
        return True
    return not is_native_session(day)


def replay_example(market, example: Mapping[str, Any]) -> dict[str, Any]:
    """Replay one dated example, matching ENTRIES only (user instruction)."""
    example = dict(example)
    if _date_outside_tape(example):
        return {
            "example_id": example.get("id"),
            "detected": None,
            "divergence": "date outside the tape",
            "entries": [],
            "other_fills": other_fills(example),
            "branch": None,
            "our_side": None,
            "our_level": None,
            "our_entry_ns": None,
            "author_level": None,
            "author_side": None,
            "reached_location": None,
            "failing_stage": None,
            "failing_operand": "date",
        }
    families = []
    family = str(example.get("family") or "GB-FAIL")
    if "GB-SCALP" in family:
        families.append("GB-SCALP")
    if "GB-VWAP" in family:
        families.append("GB-VWAP")
    if "GB-FAIL" in family or not families:
        families.append("GB-FAIL")
    episodes: list[dict[str, Any]] = []
    read: dict[str, Any] = {}
    for item in families:
        doc = scan_b02(market, {"family": item, "branch": "all"})
        episodes.extend(doc.get("episodes") or [])
        read = read or (doc.get("day_read") or {})
    entries = proper_entries(example)
    matched = [match_entry(market, episodes, entry) for entry in entries]
    detected = None if not matched else all(row["detected"] for row in matched)
    best = next((row for row in matched if row["detected"]), matched[0] if matched else None)
    return {
        "example_id": example.get("id"),
        "detected": detected,
        "detected_strict": None if not matched else all(row["detected_strict"] for row in matched),
        "entries": matched,
        "n_proper_entries": len(matched),
        "n_detected": sum(1 for row in matched if row["detected"]),
        "other_fills": other_fills(example),
        "day_read": read,
        "play": None if best is None else best.get("our_play"),
        "expected_play": None if not matched else matched[0].get("expected_play"),
        "branch": None if best is None else best["our_branch"],
        "our_side": None if not entries else entries[0].get("side"),
        "our_level": None if best is None else best["our_entry"],
        "our_entry_ns": None if best is None else best["our_entry_ns"],
        "author_level": None if best is None else best["printed_price"],
        "author_side": None if not entries else entries[0].get("side"),
        "reached_location": bool(episodes),
        "failing_stage": None if detected else "confirmation",
        "failing_operand": None if detected else "entry_price_or_time",
        "divergence": "" if detected else "entry_not_reproduced",
    }


# ---------------------------------------------------------------------------
# rules


RULES: dict[str, dict[str, Any]] = {
    "GB-REF-sessions-and-boxes": {
        "kind": "literal",
        "source": "FIDELITY_AUDIT_2026-09-17 2.1/2.3 G1, G2, G3; GB pp.1-2, 7, 37; charts 2026-04-23, 08-11/12, 08-27, 09-10/11/14/15",
        "finding": "G1,G2,G3",
        "parameters": {
            "asia": "20:00-00:00 ET, every month",
            "london": "02:00-05:00 ET, every month",
            "ny": ["09:00-10:00 from 10:00", "10:00-11:00 from 11:00"],
            "later_hours": "each completed hour from its close (11:00-16:00)",
            "prior_day_scope": "previous CME session 18:00-16:00",
            "prior_week_scope": PRIOR_WEEK_SCOPE,
            "lifecycle": "live until swept; no entry-window filter",
            "dropped": ["ny_session_extreme", "nwog_entry_branch", "09:00-09:30 half box (G13)"],
        },
        "_fn": session_references,
    },
    "GB-FAIL-five-minute-close": {
        "kind": "literal",
        "source": "GB p.3 'I wait for the 5 min close back below the PDL after sweeping above it'",
        "finding": "G3",
        "parameters": {"fail_window_bars": FAIL_WINDOW_BARS, "max_cycles_per_level": MAX_CYCLES_PER_LEVEL},
        "_fn": sweep_cycles,
    },
    "GB-FAIL-one-minute-failure-close": {
        "kind": "literal",
        "source": "the same 'fail back inside' trigger read on the one-minute clock; the tickets fill inside the five-minute bar (2026-08-28 10:05, 2025-11-20 10:05)",
        "finding": "G3",
        "_fn": failure_close,
    },
    "GB-FAIL-limit-at-level": {
        "kind": "literal",
        "source": "GB pp.43, 58, 59; 2026-09-15 fill at the box top on the 10:05 retest",
        "finding": "G3",
        "_fn": at_level_fill,
    },
    "GB-FAIL-tdo-close": {
        "kind": "literal",
        "source": "GB p.9, pp.27, 59; 2026-09-08 'closed on the 5 minute below TDO'",
        "finding": "G2",
        "_fn": _scan_asia_tdo,
    },
    "GB-FAIL-post-open-reclaim": {
        "kind": "literal",
        "source": "GB post 2099513366326730859 (2026-09-14) 'After the open, price closes back above the London low. That's my entry'",
        "finding": "G3",
        "_fn": _scan_london,
    },
    "GB-CASH-OPEN-reclaim": {
        "kind": "literal",
        "source": "GB p.3 '9:30am manipulation below, reclaim, enter for longs targeting retracement into discount, stops at lows'",
        "finding": "G4",
        "_fn": _scan_cash_open,
    },
    "GB-POCKET-impulse-both-directions": {
        "kind": "literal",
        "source": "GB p.2 '50%-61.8% fib retracement as my golden pocket zone'; 2026-09-11 CPI leg; 2026-07-29 overnight leg",
        "finding": "G8",
        "parameters": {"stop": "beyond the far edge of the zone", "leg": "the impulse that made the session extreme"},
        "_fn": _scan_golden_pocket,
    },
    "GB-CONTINUATION-break-hold-retest": {
        "kind": "literal",
        "source": "GB 2026-09-15 'Break out and hold? I'm looking for continuation'; 2026-09-10 retest long",
        "finding": "G9",
        "parameters": {"hold_bars": CONTINUATION_HOLD_BARS, "hold_bars_source": "unstated"},
        "_fn": _scan_continuation,
    },
    "GB-VWAP-continuation": {
        "kind": "literal",
        "source": "GB 2026-02-24 'Broke & closed above London + Asia highs -> retraced into VWAP -> long entry. 30-point stop'",
        "finding": "F13",
        "parameters": {"stop_points": str(VWAP_STOP_POINTS)},
        "_fn": _scan_vwap,
    },
    "GB-RISK-stop-beyond-wick": {
        "kind": "literal",
        "source": "GB pp.52-53, 56, 58, 60; audit 2.3 G6",
        "finding": "G6",
        "parameters": {
            "stop": "sweep extreme +/- buffer",
            "buffer_points": str(SWEEP_STOP_BUFFER),
            "risk_dollars": str(RISK_DOLLARS),
            "ticket_stop_band_points": [17.25, 48.25],
        },
        "_fn": derived_quantity,
    },
    "GB-OBJ-opposite-edge-then-next-level": {
        "kind": "literal",
        "source": "GB 2026-09-14 'Midnight open first. London high next'; tickets R:R 3.99-11.09",
        "finding": "G12",
        "parameters": {"ladder_spacing": str(LADDER_SPACING), "observed_rungs_points": [13.75, 32.25]},
        "_fn": limit_ladder,
    },
    "GB-BIAS-recorded-not-filtered": {
        "kind": "OD",
        "source": "audit 2.3 G10: the author's bias is qualitative; the proxy is ours and never filters the baseline",
        "finding": "G10",
        "_fn": directional_bias,
    },
    "GB-SELECT-one-to-three-a-day": {
        "kind": "literal",
        "source": "GB 2026-09-11 'One opportunity at a time'; 2026-09-14 'Two trades were enough'; audit 2.3 G11",
        "finding": "G11",
        "parameters": {"max_entries": MAX_ENTRIES_PER_SESSION},
        "_fn": select_session_trades,
    },
    "GB-SCALP-observations": {
        "kind": "literal",
        "source": "GB p.40",
        "finding": "F01",
        "_fn": _scan_scalp_observation,
    },
    "GB-NWOG-objective-only": {
        "kind": "literal",
        "source": "GB p.4 'close the whole trade when price hits NWOG'; audit 2.3 G7",
        "finding": "G7",
        "_fn": _nwog_levels,
    },
}


def _bind_rule_lines() -> None:
    here = Path(__file__).name
    for row in RULES.values():
        fn = row.get("_fn")
        if fn is None:
            continue
        try:
            row["file_line"] = f"{here}:{inspect.getsourcelines(fn)[1]}"
        except (OSError, TypeError):
            row["file_line"] = here


_bind_rule_lines()
