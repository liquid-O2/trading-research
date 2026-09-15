"""Eight future-RV heads with matching-boundary sampling and close/roll exclusions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
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
    event = t_ns[order]
    idx = np.searchsorted(avail, boundaries, side="right") - 1
    out = np.full(boundaries.shape, np.nan, dtype=np.float64)
    if avail.size == 0:
        return out, np.zeros(boundaries.shape, dtype=np.bool_)
    ok_idx = idx >= 0
    clipped = np.clip(idx, 0, avail.size - 1)
    chosen_avail = np.where(ok_idx, avail[clipped], -1)
    chosen_event = np.where(ok_idx, event[clipped], -1)
    age = boundaries - chosen_avail
    good = (
        ok_idx
        & (age >= 0)
        & (age <= MAX_MID_AGE_NS)
        & (chosen_event <= boundaries)
        & np.isfinite(px[clipped])
        & (px[clipped] > 0)
    )
    out[good] = px[idx[good]]
    return out, good


def python_matching_midpoints(
    t_ns: Sequence[int],
    mid: Sequence[float],
    available_at_ns: Sequence[int],
    boundaries: Sequence[int],
) -> list[float | None]:
    rows = sorted(zip(available_at_ns, t_ns, mid))
    out: list[float | None] = []
    for b in boundaries:
        chosen = None
        for avail, event, px in rows:
            if event <= b and avail <= b and (b - avail) <= MAX_MID_AGE_NS:
                chosen = float(px)
        out.append(chosen)
    return out


def load_bbo_midpoints(day: date, start_ns: int, end_ns: int) -> dict[str, np.ndarray | str | None]:
    """Native MarketView quote midpoints. Not trades-only closes."""
    from trading_research.research.method_pack.event_cache import ownership
    from trading_research.research.method_pack.mbp1_views import plan_window
    from trading_research.research.rule_discovery.native import (
        DATA_ROOT,
        TICK_FLOAT,
        contract_selection,
        decode_arrow_table,
        load_span_arrow,
        stitch_monthly_seams,
    )

    selection = contract_selection(day)
    instrument_id = selection["archive"]["instrument_id"]
    plan = plan_window(DATA_ROOT, int(start_ns) - MAX_MID_AGE_NS, int(end_ns), ownership=ownership(str(DATA_ROOT)))
    stitch_monthly_seams(plan)
    parts_t: list[np.ndarray] = []
    parts_mid: list[np.ndarray] = []
    parts_avail: list[np.ndarray] = []
    sources: list[str] = []
    for span in plan.get("owned_spans") or []:
        path = Path(span["path"])
        table, offsets = load_span_arrow(
            path,
            int(span["start_ns"]),
            int(span["end_ns"]),
            instrument_id=instrument_id,
            trades_only=False,
        )
        if table.num_rows == 0:
            continue
        arrays = decode_arrow_table(
            table,
            start_ns=int(start_ns) - MAX_MID_AGE_NS,
            end_ns=int(end_ns),
            instrument_id=str(instrument_id),
            source_file=str(path),
            row_offsets=offsets,
        )
        bid = arrays.bid_ticks.astype(np.float64) * TICK_FLOAT
        ask = arrays.ask_ticks.astype(np.float64) * TICK_FLOAT
        valid = (arrays.bid_ticks > 0) & (arrays.ask_ticks >= arrays.bid_ticks) & (arrays.ask_ticks > 0)
        if not np.any(valid):
            continue
        parts_t.append(arrays.t_ns[valid])
        parts_avail.append(arrays.known_at_ns[valid])
        parts_mid.append(0.5 * (bid[valid] + ask[valid]))
        sources.append(str(path))
    if not parts_t:
        return {
            "t_ns": np.zeros(0, dtype=np.int64),
            "mid": np.zeros(0, dtype=np.float64),
            "available_at_ns": np.zeros(0, dtype=np.int64),
            "instrument_id": str(instrument_id),
            "source": None,
            "kind": "bbo_midpoint_age_le_5s",
        }
    t_ns = np.concatenate(parts_t)
    order = np.argsort(t_ns, kind="mergesort")
    return {
        "t_ns": t_ns[order],
        "mid": np.concatenate(parts_mid)[order],
        "available_at_ns": np.concatenate(parts_avail)[order],
        "instrument_id": str(instrument_id),
        "source": sources[0],
        "kind": "bbo_midpoint_age_le_5s",
    }


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
