"""Two of Jumbo's pre-open reads that come from outside the NQ tape.

News week (TBR pp.22-24, "Market Conditions"): "The three most important red
folder news ... CPI, NFP, FOMC ... as well as the days leading up to the news
... i don't completely cease trading ... but i lower my expectations and
risk." His table marks each weekday of a news week low / moderate / risk-on.
It is drawn for the usual weekdays (CPI Wednesday, NFP Friday, FOMC
Wednesday); read relative to the release it says:

    CPI    the day itself and the days after it: risk-on; the day before:
           low; two days before: moderate
    NFP    the day itself: moderate; the day before: low; the Monday of the
           week: moderate; the days between: risk-on
    FOMC   the decision day: low; every other day of the week: risk-on

When two releases share a week the more cautious tier stands. A week with
none of the three has no tier.

Sister index (TBR p.12, scenario 2: "Stop Hunts - relative strength/weakness
between indices during overnight ... every significant overnight liquidity
has been purged"): whether NQ and ES each took the prior session's (18:00-16:00) high
and low overnight, where they disagree, and how far each travelled from 18:00
to the read at 09:00.

Both are recorded reads for the selection layer, never gates.
"""
from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

CALENDAR = "free-sources/context__event-calendar__normalized/combined-event-calendar.parquet"
ES_BARS = "quantpad/cme__es-continuous-futures__ohlcv-1m"
TIER_ORDER = {"low": 0, "moderate": 1, "risk_on": 2}
NEWS = ("cpi", "nfp", "fomc")


@lru_cache(maxsize=4)
def _releases(data_root: str) -> dict[date, tuple[str, ...]]:
    import pyarrow.parquet as pq

    path = Path(data_root) / CALENDAR
    if not path.is_file():
        return {}
    table = pq.read_table(path, columns=["event_date", "event_type"]).to_pylist()
    out: dict[date, list[str]] = {}
    for row in table:
        if row["event_type"] in NEWS and row["event_date"] is not None:
            out.setdefault(row["event_date"], []).append(row["event_type"])
    return {day: tuple(sorted(set(kinds))) for day, kinds in out.items()}


def _tier(kind: str, day: date, release: date) -> str:
    offset = (day - release).days
    if kind == "fomc":
        return "low" if offset == 0 else "risk_on"
    weekdays_before = sum(1 for n in range(1, (release - day).days + 1) if (day + timedelta(days=n)).weekday() < 5) if offset < 0 else 0
    if kind == "cpi":
        if offset >= 0:
            return "risk_on"
        return "low" if weekdays_before == 1 else ("moderate" if weekdays_before == 2 else "risk_on")
    if offset == 0:
        return "moderate"
    if weekdays_before == 1:
        return "low"
    return "moderate" if day.weekday() == 0 else "risk_on"


def news_week(day: date, data_root: str | None) -> dict[str, Any]:
    """The tier of ``day`` in his table, the releases of its week and the
    distance to each. ``available`` is False when the calendar is not on disk."""
    releases = _releases(str(data_root)) if data_root else {}
    if not releases:
        return {"available": False, "tier": None, "events": []}
    monday = day - timedelta(days=day.weekday())
    events = []
    for n in range(5):
        when = monday + timedelta(days=n)
        for kind in releases.get(when, ()):
            events.append({"kind": kind, "date": when.isoformat(), "days_from_release": (day - when).days, "tier": _tier(kind, day, when)})
    tier = min((e["tier"] for e in events), key=TIER_ORDER.get) if events else None
    return {"available": True, "tier": tier, "events": events, "release_today": sorted(e["kind"] for e in events if e["days_from_release"] == 0)}


@lru_cache(maxsize=3)
def _es_year(data_root: str, year: int):
    import pyarrow.parquet as pq

    path = Path(data_root) / ES_BARS / f"{year}.parquet"
    if not path.is_file():
        return None
    table = pq.read_table(path, columns=["t", "o", "h", "l", "c"]).to_pandas().sort_values("t")
    newest = int(table["t"].max())
    unit = 1_000_000_000 if newest < 10**11 else (1_000_000 if newest < 10**14 else (1_000 if newest < 10**17 else 1))  # s, ms, us or ns
    return (table["t"].to_numpy() * unit), table["o"].to_numpy(), table["h"].to_numpy(), table["l"].to_numpy(), table["c"].to_numpy()


def _es_span(data_root: str, start: int, end: int) -> dict[str, float] | None:
    import numpy as np
    from datetime import datetime, timezone

    year = datetime.fromtimestamp(start / 1e9, tz=timezone.utc).year
    rows = _es_year(data_root, year)
    if rows is None:
        return None
    t, o, h, l, c = rows
    i, j = int(np.searchsorted(t, start)), int(np.searchsorted(t, end))
    if j <= i:
        return None
    return {"open": float(o[i]), "high": float(h[i:j].max()), "low": float(l[i:j].min()), "close": float(c[j - 1])}


def sister_index(*, data_root: str | None, prior_window: tuple[int, int] | None, overnight: tuple[int, int], nq_prior: Mapping[str, Any] | None, nq_overnight: Mapping[str, Any] | None) -> dict[str, Any]:
    """NQ against ES over the same two windows: the prior session and the
    overnight up to the read. Everything here is known at the read."""
    if not data_root or prior_window is None or nq_prior is None or nq_overnight is None:
        return {"available": False}
    es_prior = _es_span(str(data_root), int(prior_window[0]), int(prior_window[1]))
    es_night = _es_span(str(data_root), int(overnight[0]), int(overnight[1]))
    if es_prior is None or es_night is None:
        return {"available": False}
    nq_high, nq_low = float(nq_overnight["high"]) > float(nq_prior["high"]), float(nq_overnight["low"]) < float(nq_prior["low"])
    es_high, es_low = es_night["high"] > es_prior["high"], es_night["low"] < es_prior["low"]
    nq_move = (float(nq_overnight["close"]) - float(nq_overnight["open"])) / float(nq_overnight["open"])
    es_move = (es_night["close"] - es_night["open"]) / es_night["open"]
    return {
        "available": True,
        "nq_purged_prior_high": nq_high,
        "nq_purged_prior_low": nq_low,
        "es_purged_prior_high": es_high,
        "es_purged_prior_low": es_low,
        # one index took the liquidity and the other refused: his "relative strength/weakness between indices"
        "divergence_at_high": nq_high != es_high,
        "divergence_at_low": nq_low != es_low,
        "nq_overnight_pct": round(nq_move * 100, 4),
        "es_overnight_pct": round(es_move * 100, 4),
        "nq_minus_es_overnight_pct": round((nq_move - es_move) * 100, 4),
    }
