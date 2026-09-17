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


def prior_sessions(market, count: int = MAX_LOOKBACK_SESSIONS) -> list[dict[str, Any]]:
    """The previous ``count`` trading sessions, most recent first.

    Each entry is the full 18:00-16:00 CME session the authors' charts draw as
    the D-1 / D-2 / D-3 high and low. Sessions that are not in the owned cache
    are simply absent; the caller reports the gap rather than substituting.
    """
    supplied = getattr(market, "b02_prior_sessions", None)
    if supplied is not None:
        return list(supplied)[:count]
    cached = getattr(market, "_prior_sessions_cache", None)
    if cached is not None and len(cached) >= count:
        return cached[:count]
    out: list[dict[str, Any]] = []
    day = market.day
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


def prior_value_area(market, fraction: str = ".70") -> dict[str, Any] | None:
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
                result = None
    except Exception:
        result = None
    setattr(market, "_prior_value_cache", result)
    return result
