"""C0–C3 CVD variants. Unknown aggressor volume is never treated as zero."""
from __future__ import annotations

from dataclasses import dataclass
from math import log, exp
from typing import Any, Mapping, Sequence

import numpy as np

from trading_research.errors import ContractError
from trading_research.research.contracts.types import Coverage, EvidenceRef, FeatureValue
from trading_research.research.rule_discovery.native import PrefixSums, cvd_from_prefix, python_cvd

LN2 = log(2.0)
C2_HALF_LIFE_NS = 300 * 1_000_000_000
C1_WINDOW_NS = 5 * 60 * 1_000_000_000
UNKNOWN_GATE = 0.20
C3_MAD_SCALE = 1.4826
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def batch_delta(sizes: Sequence[int], sides: Sequence[int]) -> dict[str, Any]:
    """D_b known signed, V_b all size, U_b unknown size. Unknown is never filled with 0 as known."""
    signed, volume, unknown = python_cvd(list(sizes), list(sides))
    known = volume - unknown
    unknown_share = (unknown / volume) if volume else 0.0
    ratio = signed / max(known, 1)
    admitted = unknown_share <= UNKNOWN_GATE and volume > 0
    return {
        "delta": signed,
        "volume": volume,
        "unknown": unknown,
        "known": known,
        "unknown_share": unknown_share,
        "known_ratio": ratio,
        "normalized_admitted": admitted,
        "c0": signed,
    }


def fixture_plus10_minus4_unknown6() -> dict[str, Any]:
    return batch_delta([10, 4, 6], [1, -1, 0])


def decay_factor(dt_ns: int, *, half_life_ns: int = C2_HALF_LIFE_NS) -> float:
    if dt_ns < 0:
        raise ContractError("negative decay interval")
    if half_life_ns <= 0:
        raise ContractError("half-life must be positive")
    return exp(-LN2 * dt_ns / half_life_ns)


def c2_step(prev_z: float, prev_known: float, delta: int, known: int, dt_ns: int) -> tuple[float, float, float | None]:
    factor = decay_factor(dt_ns)
    z = factor * prev_z + float(delta)
    k = factor * prev_known + float(known)
    normalized = z / k if k > 0 else None
    return z, k, normalized


def python_c2_series(events: Sequence[tuple[int, int, int]]) -> list[dict[str, Any]]:
    """events: (t_ns, signed_delta, known_volume). Plain Python reference."""
    z = 0.0
    k = 0.0
    t_prev = None
    rows = []
    for t_ns, signed, known in events:
        dt = 0 if t_prev is None else t_ns - t_prev
        z, k, normalized = c2_step(z, k, signed, known, dt)
        rows.append({"t_ns": t_ns, "z": z, "known": k, "normalized": normalized})
        t_prev = t_ns
    return rows


def vector_c0(prefix: PrefixSums, start_ns: int, end_ns: int) -> dict[str, Any]:
    signed, volume, unknown = cvd_from_prefix(prefix, start_ns, end_ns)
    return {"delta": signed, "volume": volume, "unknown": unknown, "c0": signed}


def c1_normalized(signed: int, volume: int, unknown: int) -> dict[str, Any]:
    known = volume - unknown
    share = (unknown / volume) if volume else 1.0
    value = signed / max(known, 1)
    available = volume > 0 and share <= UNKNOWN_GATE
    return {
        "value": value if available else None,
        "available": available,
        "unknown_share": share,
        "reason": None if available else "unknown_aggressor_share_above_0.20",
        "raw_ratio": value,
    }


def median_float(values: Sequence[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    if n == 0:
        raise ContractError("median of empty")
    if n % 2:
        return float(ordered[n // 2])
    return (ordered[n // 2 - 1] + ordered[n // 2]) / 2.0


def mad(values: Sequence[float]) -> float:
    med = median_float(values)
    return median_float([abs(v - med) for v in values])


def c3_zscore(current: float, history: Sequence[float]) -> dict[str, Any]:
    if len(history) < 1:
        return {"available": False, "reason": "missing prior 20-session same-bucket history", "value": None}
    med = median_float(history)
    scale = max(1.0, C3_MAD_SCALE * mad(history))
    return {"available": True, "value": (current - med) / scale, "median": med, "scale": scale}


def feature(
    name: str,
    value: float | None,
    *,
    unit: str,
    available_at_ns: int,
    missing_reason: str | None,
    row_ids: tuple[str, ...] = ("delta:0",),
) -> FeatureValue:
    return FeatureValue(
        name=name,
        value=value,
        unit=unit,
        available_at_ns=available_at_ns,
        evidence=(
            EvidenceRef(
                artifact_sha256=EMPTY_SHA256,
                row_ids=row_ids,
                event_start_ns=available_at_ns,
                event_end_ns=available_at_ns,
                available_at_ns=available_at_ns,
                coverage=Coverage.COMPLETE if value is not None else Coverage.MISSING,
                limitation_ids=() if value is not None else ("unknown_aggressor",),
            ),
        ),
        missing_reason=missing_reason,
    )


def emit_features(batch: Mapping[str, Any], *, available_at_ns: int, history: Sequence[float] | None = None) -> tuple[FeatureValue, ...]:
    c1 = c1_normalized(int(batch["delta"]), int(batch["volume"]), int(batch["unknown"]))
    c3 = c3_zscore(float(batch["delta"]), history or ())
    rows = [
        feature("C0", float(batch["c0"]), unit="contracts", available_at_ns=available_at_ns, missing_reason=None),
        feature(
            "C1",
            None if not c1["available"] else float(c1["value"]),
            unit="ratio",
            available_at_ns=available_at_ns,
            missing_reason=None if c1["available"] else str(c1["reason"]),
        ),
        feature(
            "C3",
            None if not c3["available"] else float(c3["value"]),
            unit="z",
            available_at_ns=available_at_ns,
            missing_reason=None if c3["available"] else str(c3.get("reason") or "unavailable"),
        ),
    ]
    return tuple(rows)


def frozen_delta_ignores_unknown(buy: int, sell: int, unknown: int) -> int:
    """Reproduce historical_features.delta: sum(b-a), the unknown column is dropped."""
    return int(buy) - int(sell)


@dataclass(frozen=True, slots=True)
class DeltaCase:
    case_id: str
    delta: int
    volume: int
    unknown: int
    admitted: bool


def slice_p15_06(day: str) -> dict[str, Any]:
    from trading_research.research.rule_discovery.engine_slice import run_candidate_branch_session

    return run_candidate_branch_session(day)
