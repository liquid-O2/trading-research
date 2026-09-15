"""Eight future-RV heads with matching-boundary sampling and close/roll exclusions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Sequence

import numpy as np

from trading_research.errors import ContractError
from trading_research.research.experts.features.volatility import realized_variance
from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.session_policy import NQSessionPolicy
from trading_research.research.rule_discovery.native import account_day_window

NS = 1_000_000_000
MINUTE_NS = 60 * NS
HEADS = (
    "rv_15m",
    "rv_30m",
    "rv_60m",
    "rv_120m",
    "remaining_current_bucket",
    "next_analysis_bucket",
    "remaining_rth",
    "remaining_account_day",
)
BUCKET_NS = 15 * MINUTE_NS
MAX_MID_AGE_NS = 5 * NS


@dataclass(frozen=True, slots=True)
class TargetHead:
    name: str
    start_ns: int
    end_ns: int
    duration_ns: int
    variance: float | None
    status: str
    coverage: str
    reason: str | None
    label_known_at_ns: int | None
    sampling: str


def matching_midpoints(
    t_ns: np.ndarray,
    mid: np.ndarray,
    available_at_ns: np.ndarray,
    boundaries: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Last midpoint with available_at <= boundary and age <= 5s. Missing boundary is NaN."""
    order = np.argsort(available_at_ns, kind="mergesort")
    avail = available_at_ns[order]
    px = mid[order]
    idx = np.searchsorted(avail, boundaries, side="right") - 1
    out = np.full(boundaries.shape, np.nan)
    ok_idx = idx >= 0
    chosen_avail = np.where(ok_idx, avail[np.clip(idx, 0, max(avail.size - 1, 0))], -1)
    age = boundaries - chosen_avail
    good = ok_idx & (age >= 0) & (age <= MAX_MID_AGE_NS) & np.isfinite(px[np.clip(idx, 0, max(px.size - 1, 0))])
    out[good] = px[idx[good]]
    return out, good


def python_matching_midpoints(
    t_ns: Sequence[int],
    mid: Sequence[float],
    available_at_ns: Sequence[int],
    boundaries: Sequence[int],
) -> list[float | None]:
    rows = sorted(zip(available_at_ns, mid))
    out: list[float | None] = []
    for b in boundaries:
        chosen = None
        for avail, px in rows:
            if avail <= b and (b - avail) <= MAX_MID_AGE_NS:
                chosen = float(px)
        out.append(chosen)
    return out


def _horizon_end(start_ns: int, minutes: int, close_ns: int, roll_ns: int | None) -> tuple[int | None, str | None]:
    end = start_ns + minutes * MINUTE_NS
    if end > close_ns:
        return None, "crosses_account_day_or_close"
    if roll_ns is not None and start_ns < roll_ns < end:
        return None, "crosses_roll"
    return end, None


def build_heads(
    *,
    issue_ns: int,
    day: date,
    t_ns: np.ndarray,
    mid: np.ndarray,
    available_at_ns: np.ndarray,
    roll_ns: int | None = None,
    sampling: str = "bbo_midpoint_age_le_5s",
    policy: NQSessionPolicy | None = None,
) -> list[TargetHead]:
    policy = policy or NQSessionPolicy()
    start_day, end_day = account_day_window(day, policy=policy)
    rth = policy.rth(day)
    rth_close = rth["windows"][0][1] if rth.get("windows") else et_ns(day, 16, 0)
    heads: list[TargetHead] = []
    bucket_open = issue_ns - ((issue_ns - start_day) % BUCKET_NS)
    bucket_end = bucket_open + BUCKET_NS
    next_bucket_open = bucket_end
    next_bucket_end = next_bucket_open + BUCKET_NS

    def rv_between(a: int, b: int) -> tuple[float | None, str, str | None]:
        if b <= a:
            return None, "unsupported", "empty_interval"
        step = MINUTE_NS
        n = int((b - a + step - 1) // step)
        bounds = a + np.arange(n + 1, dtype=np.int64) * step
        bounds[-1] = b
        px, good = matching_midpoints(t_ns, mid, available_at_ns, bounds)
        if not bool(np.all(good)):
            return None, "incomplete", "missing_boundary_midpoint"
        try:
            result = realized_variance(px.tolist())
        except ContractError as exc:
            return None, "unsupported", str(exc)
        return float(result["variance"]), "ok", None

    specs = [
        ("rv_15m", issue_ns, _horizon_end(issue_ns, 15, end_day, roll_ns)),
        ("rv_30m", issue_ns, _horizon_end(issue_ns, 30, end_day, roll_ns)),
        ("rv_60m", issue_ns, _horizon_end(issue_ns, 60, end_day, roll_ns)),
        ("rv_120m", issue_ns, _horizon_end(issue_ns, 120, end_day, roll_ns)),
        ("remaining_current_bucket", issue_ns, (bucket_end if bucket_end <= end_day else None, None if bucket_end <= end_day else "crosses_account_day_or_close")),
        ("next_analysis_bucket", next_bucket_open, (next_bucket_end if next_bucket_end <= end_day else None, None if next_bucket_end <= end_day else "crosses_account_day_or_close")),
        ("remaining_rth", issue_ns, (rth_close if issue_ns < rth_close else None, None if issue_ns < rth_close else "after_rth_close")),
        ("remaining_account_day", issue_ns, (end_day if issue_ns < end_day else None, None if issue_ns < end_day else "at_or_after_close")),
    ]
    for name, start, (end, reason) in specs:
        if end is None:
            heads.append(
                TargetHead(name, start, start, 0, None, "unsupported", "masked", reason, None, sampling)
            )
            continue
        var, status, why = rv_between(start, end)
        known = None if status != "ok" else int(end)
        heads.append(
            TargetHead(
                name=name,
                start_ns=int(start),
                end_ns=int(end),
                duration_ns=int(end - start),
                variance=var,
                status=status,
                coverage="complete" if status == "ok" else "incomplete",
                reason=why,
                label_known_at_ns=known,
                sampling=sampling,
            )
        )
    return heads


def heads_to_json(heads: Sequence[TargetHead]) -> list[dict[str, Any]]:
    return [
        {
            "name": h.name,
            "start_ns": h.start_ns,
            "end_ns": h.end_ns,
            "duration_ns": h.duration_ns,
            "variance": h.variance,
            "status": h.status,
            "coverage": h.coverage,
            "reason": h.reason,
            "label_known_at_ns": h.label_known_at_ns,
            "sampling": h.sampling,
        }
        for h in heads
    ]
