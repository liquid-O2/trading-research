"""Historical volatility features and forward realized-variance targets on the
quarter-hour grid of one NQ account day (VOLATILITY.md, P2-03 inputs; no
options, no fitting).

One pass over the day's native BBO midpoints builds a minute frame: the
midpoint at every one-minute boundary under the contract's rule (the last
midpoint available at or before the boundary, age <= 5 s; a missing boundary
stays missing) and the open/high/low/close of the midpoints that became
available inside each minute. Every feature at an issue time t reads only
boundaries <= t and minutes that ended at or before t; every target reads only
boundaries >= t and carries the instant it becomes known. The arithmetic is the
registered pure functions of ``features/volatility.py``; this module only
arranges their inputs.

Two named departures from a literal reading of the contract, both because the
strict rule is rarely satisfiable over 23 hours (a single quiet overnight
minute, and always the 18:00 boundary itself, has no midpoint within five
seconds): the day-level inputs are given in a strict form (None when any
boundary is missing) and in a ``_cov`` form (the sum over the adjacent
boundary pairs that are both present, with the covered share beside it), and
OHLC is taken from the same-contract midpoint stream rather than from the
continuous trade bars, so a contract change can never sit inside an interval.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import log
from typing import Any, Mapping, Sequence

import numpy as np

from trading_research.errors import ContractError
from trading_research.research.experts import snapshots
from trading_research.research.experts.features.volatility import EPS, YZ_N, garman_klass, har_inputs, yang_zhang
from trading_research.research.experts.labels.volatility import matching_midpoints
from trading_research.research.method_pack.session_policy import NQSessionPolicy
from trading_research.research.rule_discovery.native import account_day_window

MINUTE_NS = snapshots.MINUTE_NS
RECENT_MINUTES = (1, 5, 15, 60)
GK_MINUTES = (15, 60)
TARGET_MINUTES = (15, 30, 60, 120)
#: a day's covered RV enters the ``_cov`` HAR series only above this covered share
MIN_DAY_COVERAGE = 0.95
SCHEMA = "volatility-grid-v1"


@dataclass(frozen=True, slots=True)
class MinuteFrame:
    start_ns: int
    end_ns: int
    bounds: np.ndarray  # int64[N+1] one-minute boundaries, start..end inclusive
    px: np.ndarray  # float64[N+1] boundary midpoint, NaN where the contract's rule finds none
    logret: np.ndarray  # float64[N] ln(px[k+1]/px[k]), NaN where either boundary is missing
    o: np.ndarray  # float64[N] midpoint OHLC of the minute [bounds[k], bounds[k+1]) by availability
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    n_mid: np.ndarray  # int64[N] midpoints that became available inside the minute

    @property
    def n_minutes(self) -> int:
        return int(self.logret.size)

    def index_of(self, ns: int) -> int:
        offset = int(ns) - self.start_ns
        if offset % MINUTE_NS:
            raise ContractError("minute frame indices are whole-minute boundaries")
        return offset // MINUTE_NS


def build_frame(t_ns: np.ndarray, mid: np.ndarray, available_at_ns: np.ndarray, start_ns: int, end_ns: int) -> MinuteFrame:
    start_ns, end_ns = int(start_ns), int(end_ns)
    if end_ns <= start_ns or (end_ns - start_ns) % MINUTE_NS:
        raise ContractError("minute frame needs a positive whole-minute window")
    n = (end_ns - start_ns) // MINUTE_NS
    bounds = start_ns + np.arange(n + 1, dtype=np.int64) * MINUTE_NS
    t_ns = np.asarray(t_ns, dtype=np.int64)
    mid = np.asarray(mid, dtype=np.float64)
    avail = np.asarray(available_at_ns, dtype=np.int64)
    order = np.argsort(avail, kind="mergesort")
    t_s, m_s, a_s = t_ns[order], mid[order], avail[order]
    px, good = matching_midpoints(t_s, m_s, a_s, bounds)
    px = np.where(good, px, np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        logret = np.diff(np.log(px))
    usable = np.isfinite(m_s) & (m_s > 0)
    m_u, a_u = m_s[usable], a_s[usable]
    seg = np.searchsorted(a_u, bounds, side="left")
    counts = np.diff(seg)
    o = np.full(n, np.nan)
    h = np.full(n, np.nan)
    l = np.full(n, np.nan)
    c = np.full(n, np.nan)
    present = counts > 0
    if np.any(present):
        body = m_u[: seg[-1]]  # nothing available at or after the window's end
        starts = seg[:-1][present]
        ends = seg[1:][present]
        o[present] = body[starts]
        c[present] = body[ends - 1]
        h[present] = np.maximum.reduceat(body, starts)
        l[present] = np.minimum.reduceat(body, starts)
    return MinuteFrame(start_ns, end_ns, bounds, px, logret, o, h, l, c, counts.astype(np.int64))


def window_rv(frame: MinuteFrame, i: int, j: int) -> tuple[float | None, str]:
    """RV over boundaries i..j: the registered sum of squared one-minute log
    returns; incomplete when any boundary in the window is missing."""
    if i < 0:
        return None, "before_account_day_open"
    if j > frame.n_minutes:
        return None, "crosses_account_day_or_close"
    if j <= i:
        return None, "empty_interval"
    r = frame.logret[i:j]
    if np.any(np.isnan(r)):
        return None, "missing_boundary_midpoint"
    return float(np.sum(r * r)), "ok"


def covered_rv(frame: MinuteFrame, i: int, j: int) -> tuple[float | None, float]:
    """The sum over the present adjacent boundary pairs of i..j and their share.
    NOT the contract's RV: a named partial-coverage quantity for day-level inputs."""
    i, j = max(0, i), min(frame.n_minutes, j)
    if j <= i:
        return None, 0.0
    r = frame.logret[i:j]
    ok = ~np.isnan(r)
    if not np.any(ok):
        return None, 0.0
    return float(np.sum(r[ok] * r[ok])), float(ok.mean())


def window_ohlc(frame: MinuteFrame, i: int, j: int) -> tuple[tuple[float, float, float, float] | None, str]:
    """Midpoint OHLC of the completed minutes i..j-1; complete only when every
    minute of the window saw a midpoint."""
    if i < 0:
        return None, "before_account_day_open"
    if j > frame.n_minutes or j <= i:
        return None, "empty_interval" if j <= i else "crosses_account_day_or_close"
    if np.any(frame.n_mid[i:j] == 0):
        return None, "minute_without_midpoint"
    return (float(frame.o[i]), float(np.max(frame.h[i:j])), float(np.min(frame.l[i:j])), float(frame.c[j - 1])), "ok"


def window_gk(frame: MinuteFrame, i: int, j: int) -> tuple[float | None, str]:
    ohlc, status = window_ohlc(frame, i, j)
    if ohlc is None:
        return None, status
    try:
        return float(garman_klass(*ohlc)["variance"]), "ok"
    except ContractError as exc:
        return None, f"rejected:{exc}"


def _log(value: float | None) -> float | None:
    return None if value is None else log(value + EPS)


def grid_rows(day: date, frame: MinuteFrame, *, policy: NQSessionPolicy | None = None) -> list[dict[str, Any]]:
    policy = policy or NQSessionPolicy()
    info = policy.rth(day)
    rth = snapshots.rth_window(day, policy=policy)
    rth_i = rth_j = None
    if rth is not None and frame.start_ns <= rth[0] < frame.end_ns:
        rth_i = frame.index_of(rth[0])
        rth_j = frame.index_of(min(rth[1], frame.end_ns))
    rows = []
    for t in snapshots.account_day_grid(day, policy=policy):
        t = int(t)
        g = frame.index_of(t)
        spot = frame.px[g]
        spot = None if np.isnan(spot) else float(spot)
        row: dict[str, Any] = {
            "day": day.isoformat(),
            "issue_ns": t,
            "is_holdout": snapshots.is_holdout(day),
            "session_bucket": snapshots.session_bucket(t),
            "calendar_state": info.get("state"),
            "rth_known": bool(info.get("known")),
            "in_rth": bool(rth_i is not None and rth_i <= g < rth_j),
            "spot_mid": spot,
            "elapsed_account_minutes": g,
            "remaining_account_minutes": frame.n_minutes - g,
            "elapsed_rth_minutes": 0 if rth_i is None else int(min(max(g - rth_i, 0), rth_j - rth_i)),
            "remaining_rth_minutes": 0 if rth_i is None else int(min(max(rth_j - g, 0), rth_j - rth_i)),
        }
        for n in RECENT_MINUTES:
            value, status = window_rv(frame, g - n, g)
            row[f"rv_recent_{n}m"] = value
            row[f"log_rv_recent_{n}m"] = _log(value)
            row[f"rv_recent_{n}m_status"] = status
        for n in GK_MINUTES:
            value, status = window_gk(frame, g - n, g)
            row[f"gk_{n}m"] = value
            row[f"log_gk_{n}m"] = _log(value)
            row[f"gk_{n}m_status"] = status
        # today's cash-session range so far, over the spot at t
        value = None
        if rth_i is not None and g > rth_i and spot is not None:
            ohlc, status = window_ohlc(frame, rth_i, min(g, rth_j))
            if ohlc is not None:
                value = (ohlc[1] - ohlc[2]) / spot
        row["rth_range_so_far_over_spot"] = value
        # the overnight (account-day open to the cash open) once the cash open has passed
        on_range = on_rv = on_cov_rv = None
        on_cov = None
        if rth_i is not None and g >= rth_i:
            present = frame.n_mid[:rth_i] > 0
            open_px = frame.px[rth_i]
            if np.any(present) and not np.isnan(open_px):
                on_range = float((np.nanmax(frame.h[:rth_i]) - np.nanmin(frame.l[:rth_i])) / open_px)
            on_rv, _ = window_rv(frame, 0, rth_i)
            on_cov_rv, on_cov = covered_rv(frame, 0, rth_i)
        row["overnight_range_over_open"] = on_range
        row["overnight_rv_strict"] = on_rv
        row["overnight_rv_cov"] = on_cov_rv
        row["log_overnight_rv_cov"] = _log(on_cov_rv)
        row["overnight_rv_coverage"] = on_cov
        # forward targets
        targets = [(f"tgt_rv_{n}m", g, g + n) for n in TARGET_MINUTES]
        if rth_i is not None and g < rth_j:
            targets.append(("tgt_rv_remaining_rth", g, rth_j))
        else:
            targets.append(("tgt_rv_remaining_rth", g, g))
        for name, i, j in targets:
            if name == "tgt_rv_remaining_rth" and j <= i:
                value, status = None, "after_rth_close" if rth_i is not None else "no_rth_session"
            else:
                value, status = window_rv(frame, i, j)
            row[name] = value
            row[f"{name}_status"] = status
            row[f"{name}_start_ns"] = int(frame.bounds[i])
            row[f"{name}_end_ns"] = int(frame.bounds[j]) if 0 <= j <= frame.n_minutes else None
            row[f"{name}_known_at_ns"] = int(frame.bounds[j]) if status == "ok" else None
        rows.append(row)
    return rows


def day_summary(day: date, frame: MinuteFrame, *, instrument_id: str | None, n_midpoints: int, policy: NQSessionPolicy | None = None) -> dict[str, Any]:
    """What the day contributes to LATER days' inputs; every field is known by
    the day's close."""
    policy = policy or NQSessionPolicy()
    rth = snapshots.rth_window(day, policy=policy)
    out: dict[str, Any] = {"day": day.isoformat(), "instrument_id": instrument_id, "n_midpoints": int(n_midpoints), "minutes": frame.n_minutes, "boundaries_missing": int(np.isnan(frame.px).sum())}
    spans = {"acct": (0, frame.n_minutes)}
    if rth is not None and frame.start_ns <= rth[0] < frame.end_ns:
        spans["rth"] = (frame.index_of(rth[0]), frame.index_of(min(rth[1], frame.end_ns)))
    for name, (i, j) in spans.items():
        strict, status = window_rv(frame, i, j)
        cov, share = covered_rv(frame, i, j)
        out[f"rv_{name}_strict"] = strict
        out[f"rv_{name}_status"] = status
        out[f"rv_{name}_cov"] = cov
        out[f"rv_{name}_coverage"] = share
        present = frame.n_mid[i:j] > 0
        if np.any(present):
            first = i + int(np.flatnonzero(present)[0])
            last = i + int(np.flatnonzero(present)[-1])
            ohlc = (float(frame.o[first]), float(np.nanmax(frame.h[i:j])), float(np.nanmin(frame.l[i:j])), float(frame.c[last]))
            out[f"ohlc_{name}"] = list(ohlc)
            out[f"ohlc_{name}_minutes_present"] = float(present.mean())
            try:
                out[f"gk_{name}"] = float(garman_klass(*ohlc)["variance"])
            except ContractError as exc:
                out[f"gk_{name}"] = None
                out[f"gk_{name}_reason"] = str(exc)
        else:
            out[f"ohlc_{name}"] = None
            out[f"gk_{name}"] = None
    return out


def yz_inputs(prior: Sequence[Mapping[str, Any] | None], name: str) -> list[tuple[str, float, float, float, float]]:
    """(day, o, c, u, d) of every session whose preceding session carries the
    same contract and a close: the contract's 'preceding same-contract close'.
    ``prior`` is every requested day in order: a summary for a session, None
    for a day the market did not trade (it does not break adjacency: the
    preceding session of the day after a holiday is the day before it), and a
    mapping with ``failed`` for a session whose data could not be read (it
    does: the close it would have supplied is unknown)."""
    rows = []
    sessions = [s for s in prior if s]
    for prev, cur in zip(sessions, sessions[1:]):
        if prev.get("failed") or cur.get("failed"):
            continue
        a, b = prev.get(f"ohlc_{name}"), cur.get(f"ohlc_{name}")
        if not a or not b or cur.get("instrument_id") is None or prev.get("instrument_id") != cur.get("instrument_id"):
            continue
        o_, h_, l_, c_ = b
        rows.append((cur["day"], log(o_ / a[3]), log(c_ / o_), log(h_ / o_), log(l_ / o_)))
    return rows


def day_level_inputs(prior: Sequence[Mapping[str, Any] | None], *, yz_n: int = YZ_N, gk_n: int = YZ_N) -> dict[str, Any]:
    """The inputs of an account day known at its open, from the sessions before
    it (``prior`` in order, None where a requested day had no session)."""
    sessions = [s for s in prior if s and not s.get("failed")]
    out: dict[str, Any] = {"prior_sessions": len(sessions)}
    series = {
        "rth": [s["rv_rth_strict"] for s in sessions if s.get("rv_rth_strict") is not None],
        "acct_strict": [s["rv_acct_strict"] for s in sessions if s.get("rv_acct_strict") is not None],
        "acct_cov": [s["rv_acct_cov"] for s in sessions if s.get("rv_acct_cov") is not None and s.get("rv_acct_coverage", 0.0) >= MIN_DAY_COVERAGE],
    }
    for name, values in series.items():
        har = har_inputs(values)
        for k in ("log_har1", "log_har5", "log_har22"):
            out[f"har_{name}_{k[4:]}"] = har.get(k)
        out[f"har_{name}_n"] = len(values)
    # sessions since the last strict cash-session RV (staleness of har_rth_har1)
    age = None
    for back, s in enumerate(reversed(sessions), start=1):
        if s.get("rv_rth_strict") is not None:
            age = back
            break
    out["har_rth_age_sessions"] = age
    for name in ("acct", "rth"):
        rows = yz_inputs(list(prior), name)[-yz_n:]
        if len(rows) == yz_n and yz_n > 1:
            _, o, c, u, d = zip(*rows)
            value = float(yang_zhang(o, c, u, d)["variance"])
            out[f"yz{yz_n}_{name}"] = value
            out[f"log_yz{yz_n}_{name}"] = _log(value)
        else:
            out[f"yz{yz_n}_{name}"] = None
            out[f"log_yz{yz_n}_{name}"] = None
        out[f"yz{yz_n}_{name}_n"] = len(rows)
        gks = [s[f"gk_{name}"] for s in sessions if s.get(f"gk_{name}") is not None][-gk_n:]
        mean = float(np.mean(gks)) if len(gks) == gk_n else None
        out[f"gk{gk_n}_mean_{name}"] = mean
        out[f"log_gk{gk_n}_mean_{name}"] = _log(mean)
        last = next((s[f"gk_{name}"] for s in reversed(sessions) if s.get(f"gk_{name}") is not None), None)
        out[f"log_gk_prior_day_{name}"] = _log(last)
    return out


def compute_day(day: date, t_ns: np.ndarray, mid: np.ndarray, available_at_ns: np.ndarray, *, instrument_id: str | None = None, policy: NQSessionPolicy | None = None) -> dict[str, Any]:
    """Rows and the day summary from one account day's midpoints (pure: the
    caller loads)."""
    policy = policy or NQSessionPolicy()
    start, end = account_day_window(day, policy=policy)
    frame = build_frame(t_ns, mid, available_at_ns, start, end)
    return {
        "schema": SCHEMA,
        "day": day.isoformat(),
        "rows": grid_rows(day, frame, policy=policy),
        "summary": day_summary(day, frame, instrument_id=instrument_id, n_midpoints=int(np.asarray(mid).size), policy=policy),
    }


def feature_view(row: Mapping[str, Any]) -> dict[str, Any]:
    """The columns of a row that are inputs (everything that is not a target)."""
    return {k: v for k, v in row.items() if not k.startswith("tgt_")}
