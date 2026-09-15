"""Resolved cohort markouts. Unresolved cohorts cannot borrow later mids."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from trading_research.errors import ContractError

HORIZONS = (30, 120, 300)
NS = 1_000_000_000


def _resolved_or_unresolved(trade: Mapping[str, Any], *, horizon_ns: int, snapshot_ns: int) -> tuple[bool, int, int, float, float | None]:
    sign = trade.get("sign")
    qty = int(trade["qty"])
    price = float(trade["price"])
    event_ns = int(trade["event_ns"])
    mid = trade.get("mid_at_horizon")
    mid_available_ns = trade.get("mid_available_ns")
    due = event_ns + horizon_ns
    unresolved = sign not in (1, -1) or mid is None or mid_available_ns is None or int(mid_available_ns) > snapshot_ns or due > snapshot_ns
    return unresolved, int(sign or 0), qty, price, None if mid is None else float(mid)


def _side_stats(*, weighted_sum: float, volume: int, units: list[float]) -> dict[str, Any]:
    if volume <= 0 or not units:
        return {"mean": None, "median": None, "positive_fraction": None, "volume": 0}
    ordered = sorted(units)
    n = len(ordered)
    median = ordered[n // 2] if n % 2 else ordered[n // 2 - 1]
    return {
        "mean": weighted_sum / volume,
        "median": median,
        "positive_fraction": sum(1 for value in units if value > 0) / n,
        "volume": volume,
    }


def markout(
    trades: Sequence[Mapping[str, Any]],
    *,
    horizon_s: int,
    snapshot_ns: int,
) -> dict[str, Any]:
    """Volume-weighted SPEC markout: M_h = sum(q_i*s_i*(mid_(i+h)-price_i)) / sum(q_i)."""
    if horizon_s not in HORIZONS:
        raise ContractError("unsupported cohort horizon")
    horizon_ns = horizon_s * NS
    buy_sum = 0.0
    sell_sum = 0.0
    buy_vol = 0
    sell_vol = 0
    buy_units: list[float] = []
    sell_units: list[float] = []
    unresolved = 0
    for trade in trades:
        is_unresolved, sign, qty, price, mid = _resolved_or_unresolved(trade, horizon_ns=horizon_ns, snapshot_ns=snapshot_ns)
        if sign not in (1, -1):
            continue
        if is_unresolved or mid is None:
            unresolved += 1
            continue
        unit = sign * (mid - price)
        contribution = qty * unit
        if sign == 1:
            buy_sum += contribution
            buy_vol += qty
            buy_units.append(unit)
        else:
            sell_sum += contribution
            sell_vol += qty
            sell_units.append(unit)
    buy = _side_stats(weighted_sum=buy_sum, volume=buy_vol, units=buy_units)
    sell = _side_stats(weighted_sum=sell_sum, volume=sell_vol, units=sell_units)
    rewarded_buyers = buy["mean"] is not None and buy["mean"] > 0
    return {
        "horizon_s": horizon_s,
        "buy": buy,
        "sell": sell,
        "unresolved": unresolved,
        "rewarded_buyers": rewarded_buyers,
        "snapshot_ns": snapshot_ns,
    }


def python_markout(trades: Sequence[Mapping[str, Any]], *, horizon_s: int, snapshot_ns: int) -> dict[str, Any]:
    """Independent plain-Python reference. Collects (qty, unit) pairs then reduces; does not call markout()."""
    if horizon_s not in HORIZONS:
        raise ContractError("unsupported cohort horizon")
    horizon_ns = horizon_s * NS
    pairs: dict[int, list[tuple[int, float]]] = {1: [], -1: []}
    unresolved = 0
    for trade in trades:
        sign = trade.get("sign")
        if sign not in (1, -1):
            continue
        qty = int(trade["qty"])
        price = float(trade["price"])
        event_ns = int(trade["event_ns"])
        mid = trade.get("mid_at_horizon")
        mid_available_ns = trade.get("mid_available_ns")
        due = event_ns + horizon_ns
        if mid is None or mid_available_ns is None or int(mid_available_ns) > snapshot_ns or due > snapshot_ns:
            unresolved += 1
            continue
        unit = int(sign) * (float(mid) - price)
        pairs[int(sign)].append((qty, unit))

    def reduce_pairs(rows: list[tuple[int, float]]) -> dict[str, Any]:
        if not rows:
            return {"mean": None, "median": None, "positive_fraction": None, "volume": 0}
        volume = 0
        weighted = 0.0
        units: list[float] = []
        for qty, unit in rows:
            volume += qty
            weighted += qty * unit
            units.append(unit)
        units.sort()
        n = len(units)
        median = units[n // 2] if n % 2 else units[n // 2 - 1]
        return {
            "mean": weighted / volume,
            "median": median,
            "positive_fraction": sum(1 for unit in units if unit > 0) / n,
            "volume": volume,
        }

    buy = reduce_pairs(pairs[1])
    sell = reduce_pairs(pairs[-1])
    return {
        "horizon_s": horizon_s,
        "buy": buy,
        "sell": sell,
        "unresolved": unresolved,
        "rewarded_buyers": buy["mean"] is not None and buy["mean"] > 0,
        "snapshot_ns": snapshot_ns,
    }


def resolved_memory_row(markout_result: Mapping[str, Any], *, side: int = 1) -> dict[str, Any]:
    """Refilling / prior-contact memory consumes the volume-weighted M_h, never an unweighted trade mean."""
    key = "buy" if side > 0 else "sell"
    stats = markout_result[key]
    mean = stats.get("mean")
    return {
        "available": mean is not None,
        "mean": mean,
        "volume": stats.get("volume") or 0,
        "unresolved": markout_result.get("unresolved") or 0,
        "horizon_s": markout_result.get("horizon_s"),
    }


def memory_features(
    *,
    touch_count: int,
    formation_ns: int,
    last_contact_ns: int | None,
    now_ns: int,
    pre_touch_departure: bool,
    signed_volume_at_band: int,
    prior_resolved: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    since_formation = now_ns - formation_ns
    since_contact = None if last_contact_ns is None else now_ns - last_contact_ns
    favorable = [
        row for row in prior_resolved
        if row.get("available") and float(row.get("mean") or 0) > 0
    ]
    return {
        "touch_count": touch_count,
        "time_since_formation_ns": since_formation,
        "time_since_last_contact_ns": since_contact,
        "pre_touch_departure": pre_touch_departure,
        "signed_volume_at_band": signed_volume_at_band,
        "prior_resolved_count": len(prior_resolved),
        "prior_favorable_count": len(favorable),
    }


def appending_unresolved_does_not_mark_out(existing: Mapping[str, Any], extra_unresolved: int) -> dict[str, Any]:
    buy_mean = existing["buy"]["mean"]
    return {
        "buy_mean_unchanged": buy_mean,
        "unresolved": existing["unresolved"] + extra_unresolved,
    }


@dataclass(frozen=True, slots=True)
class CohortCase:
    case_id: str
    horizon_s: int
    unresolved: int
    rewarded_buyers: bool
