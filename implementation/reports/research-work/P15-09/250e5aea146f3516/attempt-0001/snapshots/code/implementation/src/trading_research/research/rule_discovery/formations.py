"""Causal F1/F2/F3 formation recipes. Array-first on MarketView bars."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping, Sequence
from hashlib import sha256
import json

import numpy as np

from trading_research.errors import ContractError
from trading_research.research.contracts.types import Coverage, EvidenceRef, Formation
from trading_research.research.rule_discovery.native import (
    MINUTE_NS,
    NS,
    NativeMarketView,
    SessionArrays,
    bars_reduceat,
    python_bars,
    ticks_to_decimal,
)

TICK = Decimal("0.25")
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
F1_MINUTES = 60
F2_MAX_MINUTES = 180
F3_LENGTHS = (15, 30, 60)
F3_WIDTH_MULT = Decimal("0.75")
F3_EFFICIENCY = Decimal("0.35")
Q_TICK = Decimal("0.25")


def _evidence(*, start_ns: int, end_ns: int, available_at_ns: int, sha: str = EMPTY_SHA256, row_ids: tuple[str, ...] = ("synth:0",)) -> EvidenceRef:
    return EvidenceRef(
        artifact_sha256=sha,
        row_ids=row_ids,
        event_start_ns=start_ns,
        event_end_ns=end_ns,
        available_at_ns=available_at_ns,
        coverage=Coverage.COMPLETE,
        limitation_ids=(),
    )


def formation_id(*, kind: str, start_ns: int, end_ns: int, cutoff_ns: int, asset_id: str) -> str:
    payload = json.dumps(
        {"kind": kind, "start_ns": start_ns, "end_ns": end_ns, "cutoff_ns": cutoff_ns, "asset_id": asset_id},
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(payload.encode()).hexdigest()[:16]


def median_int(values: Sequence[int]) -> int:
    if not values:
        raise ContractError("median of an empty series")
    ordered = sorted(int(v) for v in values)
    n = len(ordered)
    if n % 2:
        return ordered[n // 2]
    return ordered[n // 2 - 1]


def python_bar_window(events: list[tuple[int, int, int, int, int]], start_ns: int, end_ns: int) -> list[dict[str, Any]]:
    """Plain-Python 60-second bars. Exact-equality oracle for reduceat."""
    return python_bars(events, start_ns, end_ns, 60)


def complete_minute_rows(arrays: SessionArrays, start_ns: int, end_ns: int) -> list[dict[str, Any]]:
    return bars_reduceat(arrays, start_ns, end_ns, 60)


def _geom(rows: Sequence[Mapping[str, Any]]) -> tuple[Decimal, Decimal, Decimal, Decimal, int, int]:
    high = max(int(row["high_ticks"]) for row in rows)
    low = min(int(row["low_ticks"]) for row in rows)
    volume = sum(int(row["volume"]) for row in rows)
    available = max(int(row["known_at_ns"]) for row in rows)
    open_ticks = int(rows[0]["open_ticks"])
    close_ticks = int(rows[-1]["close_ticks"])
    return ticks_to_decimal(high), ticks_to_decimal(low), ticks_to_decimal(open_ticks), ticks_to_decimal(close_ticks), volume, available


def _to_formation(
    rows: Sequence[Mapping[str, Any]],
    *,
    kind: str,
    cutoff_ns: int,
    asset_id: str,
    extra: Mapping[str, Any] | None = None,
) -> Formation:
    start_ns = int(rows[0]["start_ns"])
    end_ns = int(rows[-1]["end_ns"])
    high, low, _open, _close, volume, available = _geom(rows)
    available = max(available, end_ns)
    if available > cutoff_ns:
        raise ContractError("formation availability exceeds cutoff")
    sha = EMPTY_SHA256
    fid = formation_id(kind=kind, start_ns=start_ns, end_ns=end_ns, cutoff_ns=cutoff_ns, asset_id=asset_id)
    parents = tuple(str(extra[k]) for k in sorted(extra) if extra is not None) if extra else ()
    return Formation(
        formation_id=fid,
        asset_id=asset_id,
        start_ns=start_ns,
        end_ns=end_ns,
        available_at_ns=available,
        high=high,
        low=low,
        volume=volume,
        profile_id=None,
        construction_kind=kind,
        parent_ids=parents,
        evidence=(_evidence(start_ns=start_ns, end_ns=end_ns, available_at_ns=available, sha=sha),),
    )


def f1_trailing_minutes(rows: Sequence[Mapping[str, Any]], *, issue_ns: int, minutes: int = F1_MINUTES) -> dict[str, Any]:
    eligible = [row for row in rows if int(row["end_ns"]) <= issue_ns]
    if len(eligible) < minutes:
        return {"available": False, "reason": "fewer than 60 matching minutes", "rows": []}
    window = list(eligible[-minutes:])
    return {"available": True, "reason": None, "rows": window, "kind": "F1"}


def f2_volume_completed(
    rows: Sequence[Mapping[str, Any]],
    *,
    issue_ns: int,
    median_volume: int,
    max_minutes: int = F2_MAX_MINUTES,
) -> dict[str, Any]:
    eligible = [row for row in rows if int(row["end_ns"]) <= issue_ns]
    if not eligible:
        return {"available": False, "reason": "no complete minutes", "rows": [], "overshoot": 0}
    walk = list(reversed(eligible[-max_minutes:]))
    included: list[Mapping[str, Any]] = []
    acc = 0
    for row in walk:
        included.append(row)
        acc += int(row["volume"])
        if acc >= median_volume:
            break
    else:
        return {"available": False, "reason": "volume threshold not reached within 180 matching minutes", "rows": [], "overshoot": 0}
    included.reverse()
    overshoot = acc - int(median_volume)
    return {
        "available": True,
        "reason": None,
        "rows": included,
        "kind": "F2",
        "overshoot": overshoot,
        "cumulative_volume": acc,
        "median_volume": int(median_volume),
        "final_minute_start_ns": int(included[0]["start_ns"]),
        "final_minute_end_ns": int(included[0]["end_ns"]),
        "final_minute_volume": int(included[0]["volume"]),
    }


def python_f2_volume_completed(
    volumes_newest_first: Sequence[int],
    *,
    median_volume: int,
    max_minutes: int = F2_MAX_MINUTES,
) -> dict[str, Any]:
    acc = 0
    n = 0
    for volume in volumes_newest_first[:max_minutes]:
        acc += int(volume)
        n += 1
        if acc >= median_volume:
            return {"available": True, "minutes": n, "overshoot": acc - int(median_volume), "cumulative": acc}
    return {"available": False, "minutes": n, "overshoot": 0, "cumulative": acc}


def f3_balance(
    rows: Sequence[Mapping[str, Any]],
    *,
    issue_ns: int,
    lengths: tuple[int, ...] = F3_LENGTHS,
) -> dict[str, Any]:
    eligible = [row for row in rows if int(row["end_ns"]) <= issue_ns]
    for length in lengths:
        if len(eligible) < length:
            continue
        window = eligible[-length:]
        start_ns = int(window[0]["start_ns"])
        prior = [row for row in eligible if int(row["end_ns"]) <= start_ns]
        if len(prior) < F1_MINUTES:
            continue
        scale_rows = prior[-F1_MINUTES:]
        high, low, open_px, close_px, _volume, _available = _geom(window)
        width = high - low
        s_high, s_low, _so, _sc, _sv, _sa = _geom(scale_rows)
        scale = s_high - s_low
        denom = width if width > Q_TICK else Q_TICK
        efficiency = abs(close_px - open_px) / denom
        if width <= F3_WIDTH_MULT * scale and efficiency <= F3_EFFICIENCY:
            return {
                "available": True,
                "reason": None,
                "rows": window,
                "kind": "F3",
                "length": length,
                "width": str(width),
                "scale_before": str(scale),
                "efficiency": str(efficiency),
                "scale_end_ns": start_ns,
            }
    return {"available": False, "reason": "no 15/30/60 window met width and efficiency", "rows": []}


def python_f3_first_length(candidates: Sequence[tuple[int, bool]]) -> int | None:
    """Oracle: first length in 15,30,60 order whose flag is True."""
    for length, ok in candidates:
        if ok:
            return length
    return None


def freeze_formation(result: Mapping[str, Any], *, cutoff_ns: int, asset_id: str) -> Formation | None:
    if not result.get("available"):
        return None
    return _to_formation(result["rows"], kind=str(result["kind"]), cutoff_ns=cutoff_ns, asset_id=asset_id, extra={"kind": str(result["kind"])})


def build_formations(market: NativeMarketView, spec: Mapping[str, Any], cutoff_ns: int) -> tuple[Formation, ...]:
    if cutoff_ns > market.end_ns:
        raise ContractError("cutoff is after the loaded session end")
    rows = complete_minute_rows(market.arrays, market.start_ns, cutoff_ns)
    policy = str(spec.get("formation_policy") or spec.get("changed_axis") or "F1")
    issue_ns = int(spec.get("issue_ns") or cutoff_ns)
    asset_id = market.asset_id
    out: list[Formation] = []
    if policy in {"F1", "time", "B0"}:
        f1 = f1_trailing_minutes(rows, issue_ns=issue_ns)
        formed = freeze_formation(f1, cutoff_ns=cutoff_ns, asset_id=asset_id)
        if formed is not None:
            out.append(formed)
    if policy in {"F2", "volume"}:
        median = int(spec.get("median_volume") or 0)
        f2 = f2_volume_completed(rows, issue_ns=issue_ns, median_volume=median)
        formed = freeze_formation(f2, cutoff_ns=cutoff_ns, asset_id=asset_id)
        if formed is not None:
            out.append(formed)
    if policy in {"F3", "balance"}:
        f3 = f3_balance(rows, issue_ns=issue_ns)
        formed = freeze_formation(f3, cutoff_ns=cutoff_ns, asset_id=asset_id)
        if formed is not None:
            out.append(formed)
    return tuple(out)


def future_perturbation_stable(before: Formation, after: Formation) -> bool:
    return (
        before.formation_id == after.formation_id
        and before.start_ns == after.start_ns
        and before.end_ns == after.end_ns
        and before.high == after.high
        and before.low == after.low
        and before.volume == after.volume
        and before.available_at_ns == after.available_at_ns
    )


@dataclass(frozen=True, slots=True)
class FormationCase:
    case_id: str
    kind: str
    available: bool
    overshoot: int | None
    length: int | None
    volume: int | None
    notes: str


def validate_cases(document: Mapping[str, Any]) -> list[str]:
    errors = []
    if document.get("schema_version") != "research-formation-cases-v1":
        errors.append("schema")
    if not isinstance(document.get("cases"), list) or not document.get("cases"):
        errors.append("cases")
    return errors


def slice_p15_05(day: str) -> dict[str, Any]:
    from trading_research.research.rule_discovery.engine_slice import run_candidate_branch_session

    return run_candidate_branch_session(day)
