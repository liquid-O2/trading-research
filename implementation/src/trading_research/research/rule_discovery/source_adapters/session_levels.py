"""Prior-session levels shared by the source-faithful Jumbo and Green Bird scans.

Both authors draw the same prior-period objects: Green Bird's PDH/PDL and the
True Day Open, JJumboFX's D-1/D-2/D-3 highs and lows and the prior RTH value
area (pRTHVAH / pRTHVAL / POC on his MGLevels panel). The session window the
scanners already hold starts at the previous day's 18:00, so those objects come
from the previous sessions' own cached windows, loaded once per market.
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from trading_research.research.method_pack.empirical_market import clock

MAX_LOOKBACK_SESSIONS = 3


def _d(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _session_span(market, day: date) -> dict[str, Any] | None:
    """The full CME session 18:00(D-1) - 16:00(D) of ``day``, from the cache."""
    from trading_research.research.method_pack.event_cache import cached_window
    from trading_research.research.method_pack.event_time_fast import FastEventWindow

    start = clock(day - timedelta(days=1), "18:00")
    end = clock(day, "16:00")
    try:
        document, receipt = cached_window(market.data_root, start, end, market.instrument_id)
        window = FastEventWindow(document, schedule=market.policy)
        rows = window.bars(window.start, window.end, 300)
    except Exception:
        return None
    highs = [_d(r["H"]) for r in rows if r.get("H") is not None]
    lows = [_d(r["L"]) for r in rows if r.get("L") is not None]
    if not highs or not lows:
        return None
    market.input_receipts.append(receipt)
    return {
        "date": str(day),
        "id": f"prior_session:{market.instrument_id}:{day}",
        "low": min(lows),
        "high": max(highs),
        "open": _d(rows[0].get("O")),
        "close": _d(rows[-1].get("C")),
        "known_at": int(end),
        "scope": "cme_session_1800_1600",
        "window": window,
    }


def prior_sessions(market, count: int | None = None) -> list[dict[str, Any]]:
    """The previous ``count`` trading sessions, most recent first.

    Each entry is the full 18:00-16:00 CME session the authors' charts draw as
    the D-1 / D-2 / D-3 high and low. Sessions that are not in the owned cache
    are simply absent; the caller reports the gap rather than substituting.
    """
    if count is None:
        count = MAX_LOOKBACK_SESSIONS  # read at call time so a rescan override reaches it
    supplied = getattr(market, "b02_prior_sessions", None)
    if supplied is not None:
        return list(supplied)[:count]
    cached = getattr(market, "_prior_sessions_cache", None)
    if cached is not None and len(cached) >= count:
        return cached[:count]
    out: list[dict[str, Any]] = []
    day = getattr(market, "day", None)
    policy = getattr(market, "policy", None)
    if day is None or policy is None or getattr(market, "instrument_id", None) is None:
        # a view that is not the session window (the native replay view) has no
        # prior-period objects of its own; the caller records the gap
        setattr(market, "_prior_sessions_cache", [])
        return []
    for _ in range(count * 3):
        if len(out) >= count:
            break
        try:
            policy = market.policy.previous_session(day)
        except Exception:
            break
        if not policy or not policy.get("date"):
            break
        day = date.fromisoformat(policy["date"])
        span = _session_span(market, day)
        if span is not None:
            out.append(span)
    setattr(market, "_prior_sessions_cache", out)
    return out


def prior_value_area(market, fraction: str = ".70") -> dict[str, Any] | None:  # noqa: D401
    """Prior RTH value area (pRTHVAH / pRTHVAL / POC) from the prior session.

    The author reads value off his MGLevels panel; the owned equivalent is the
    prior session's RTH volume profile at the 70% value area.
    """
    supplied = getattr(market, "b02_prior_value", None)
    if supplied is not None:
        return dict(supplied)
    cached = getattr(market, "_prior_value_cache", "missing")
    if cached != "missing":
        return cached
    result = None
    try:
        prior = market.prior("day")
        sessions = (prior or {}).get("sessions") or []
        rows = []
        for item in sessions:
            window = item.get("window")
            if window is None:
                continue
            payload = window.profile(window.start, window.end)
            rows.append(payload)
        if rows:
            payload = rows[-1]
            result = {
                "vah": _d(payload.get("vah")),
                "val": _d(payload.get("val")),
                "poc": _d(payload.get("poc")),
                "known_at": int((prior.get("range") or {}).get("known_at") or market.start),
                "scope": "prior_rth_profile_0.70",
            }
            if result["vah"] is None or result["val"] is None:
                result = {"unavailable": "profile_returned_no_value_area"}
        else:
            result = {"unavailable": "no_prior_session_window"}
    except Exception as exc:
        # Never a silent None: the reason the value area could not be measured
        # is carried so the day read can record read_inputs_missing and the
        # population can count it, instead of 53 sessions quietly losing their
        # open location.
        result = {"unavailable": f"{type(exc).__name__}: {exc}"}
    setattr(market, "_prior_value_cache", result)
    return result


# ---------------------------------------------------------------------------
# Green Bird's prior-period lines (added 2026-09-18; nothing above is changed)
#
# His PDH/PDL are the prior GLOBEX day, 18:00 to 17:00 ET, and the line rolls
# at 18:00 (chart p52_x105 draws two "PDL" labels, one ending at the close and
# the next from 18:00). His weekly lines are the whole weekly candle: "last
# weeks range has a high and a low which is time based, from the opening to
# the closing of the weekly candle" (GB p.32). The session windows of the
# event cache end at 16:00, so the 16:00-17:00 hour and the overnight part of
# the weekly candle come from the owned one-minute bars of the SAME contract
# (rows carry their instrument id; another contract's prices never stand in).

NQ_MINUTE_BARS = "quantpad/cme__nq-continuous-futures__ohlcv-1m"


@lru_cache(maxsize=4)
def _minute_year(data_root: str, year: int):
    import pyarrow.parquet as pq

    path = Path(data_root) / NQ_MINUTE_BARS / f"{year}.parquet"
    if not path.is_file():
        return None
    table = pq.read_table(path, columns=["t", "o", "h", "l", "c", "instrument_id"]).to_pandas().sort_values("t")
    newest = int(table["t"].max())
    unit = 1_000_000_000 if newest < 10**11 else (1_000_000 if newest < 10**14 else (1_000 if newest < 10**17 else 1))  # s, ms, us or ns
    return tuple(table[name].to_numpy() * (unit if name == "t" else 1) for name in ("t", "o", "h", "l", "c", "instrument_id"))


def minute_span(data_root: Any, instrument_id: Any, start_ns: int, end_ns: int) -> dict[str, Any] | None:
    """High, low, open and close of one contract's one-minute bars in
    [start_ns, end_ns). None when a year of the window is not on disk;
    ``rows`` 0 when it is and the contract did not trade there; ``other_rows``
    counts the bars of OTHER contracts in the window (a roll inside it)."""
    import numpy as np
    from datetime import datetime, timezone

    years = range(datetime.fromtimestamp(start_ns / 1e9, tz=timezone.utc).year, datetime.fromtimestamp((end_ns - 1) / 1e9, tz=timezone.utc).year + 1)
    parts = []
    for year in years:
        rows = _minute_year(str(data_root), year)
        if rows is None:
            return None
        t = rows[0]
        i, j = int(np.searchsorted(t, start_ns)), int(np.searchsorted(t, end_ns))
        parts.append(tuple(column[i:j] for column in rows))
    t, o, h, l, c, ids = (np.concatenate([part[n] for part in parts]) for n in range(6))
    own = ids == int(instrument_id)
    out: dict[str, Any] = {"rows": int(own.sum()), "other_rows": int((~own).sum())}
    if out["rows"]:
        out.update(
            {
                "high": _d(float(h[own].max())),
                "low": _d(float(l[own].min())),
                "open": _d(float(o[own][0])),
                "close": _d(float(c[own][-1])),
                "first_ns": int(t[own][0]),
                "last_ns": int(t[own][-1]),
            }
        )
    return out


def globex_prior_day(market) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """Green Bird's prior day: the Globex day 18:00-17:00 ET, known at 17:00.

    The 18:00-16:00 part is the prior session's own cached window (the span
    Jumbo uses, unchanged); the 16:00-17:00 hour is added from the one-minute
    bars. 2026-08-27: his "PDH" label sits at about 29,437 and both of his
    ladders end at 29,425.50; the prior session's high to 16:00 is 29,368.25
    and the closing hour ran to 29,437.75 at 16:59. When the closing hour is
    not available the 16:00 span is returned with the gap recorded, never
    silently.
    """
    sessions = prior_sessions(market, 1)
    if not sessions:
        return None, [{"reason": "prior_full_session_unavailable"}]
    span = dict(sessions[0])
    day = date.fromisoformat(span["date"])
    hour = minute_span(getattr(market, "data_root", None), market.instrument_id, clock(day, "16:00"), clock(day, "17:00")) if getattr(market, "data_root", None) else None
    if hour is None or (not hour["rows"] and hour["other_rows"]):
        # no bars on disk, or the hour traded on another contract (roll day)
        return span, [{"reason": "globex_closing_hour_unavailable", "operand": "prior_day_16_17", "detail": "prior day kept at the 18:00-16:00 session scope", "date": span["date"]}]
    if hour["rows"]:
        span["high"] = max(span["high"], hour["high"])
        span["low"] = min(span["low"], hour["low"])
        span["close"] = hour["close"]
    span["known_at"] = int(clock(day, "17:00"))
    span["scope"] = "globex_day_1800_1700"
    return span, []
