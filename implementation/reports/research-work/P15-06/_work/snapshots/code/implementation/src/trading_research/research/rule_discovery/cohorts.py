"""Resolved cohort markouts. Unresolved cohorts cannot borrow later mids."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from trading_research.errors import ContractError

HORIZONS = (30, 120, 300)
NS = 1_000_000_000


def markout(
    trades: Sequence[Mapping[str, Any]],
    *,
    horizon_s: int,
    snapshot_ns: int,
) -> dict[str, Any]:
    if horizon_s not in HORIZONS:
        raise ContractError("unsupported cohort horizon")
    horizon_ns = horizon_s * NS
    resolved_buy: list[float] = []
    resolved_sell: list[float] = []
    buy_vol = 0
    sell_vol = 0
    unresolved = 0
    for trade in trades:
        sign = trade.get("sign")
        qty = int(trade["qty"])
        price = float(trade["price"])
        event_ns = int(trade["event_ns"])
        mid = trade.get("mid_at_horizon")
        mid_available_ns = trade.get("mid_available_ns")
        if sign not in (1, -1):
            continue
        due = event_ns + horizon_ns
        if mid is None or mid_available_ns is None or int(mid_available_ns) > snapshot_ns or due > snapshot_ns:
            unresolved += 1
            continue
        value = qty * sign * (float(mid) - price)
        if sign == 1:
            resolved_buy.append(value / qty)
            buy_vol += qty
        else:
            resolved_sell.append(value / qty)
            sell_vol += qty
    def stats(rows: list[float], volume: int) -> dict[str, Any]:
        if not rows:
            return {"mean": None, "median": None, "positive_fraction": None, "volume": 0}
        ordered = sorted(rows)
        n = len(ordered)
        median = ordered[n // 2] if n % 2 else ordered[n // 2 - 1]
        return {
            "mean": sum(rows) / n,
            "median": median,
            "positive_fraction": sum(1 for v in rows if v > 0) / n,
            "volume": volume,
        }
    buy = stats(resolved_buy, buy_vol)
    sell = stats(resolved_sell, sell_vol)
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
    return markout(trades, horizon_s=horizon_s, snapshot_ns=snapshot_ns)


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
