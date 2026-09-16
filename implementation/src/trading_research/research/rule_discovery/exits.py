"""Fixed-entry exit policies E0-E4. Owned by P15-19. Does not edit execution.py."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, Sequence
import bisect
import gc
import gzip
import json
import resource
import time
import traceback

import numpy as np

from trading_research.errors import ContractError
from trading_research.research.contracts.execution import (
    COMMISSION_SIDE,
    ENTRY_WINDOW_NS,
    LATENCY_NS,
    POINT_VALUE,
    TICK,
    net_dollars,
    net_points,
    select_quote,
)
from trading_research.research.contracts.outcomes import PriceBatch
from trading_research.research.contracts.types import (
    Coverage,
    EvidenceRef,
    NativeBatch,
    QuoteBatch,
)

POLICIES = ("E0", "E1", "E2", "E3", "E4")
POLICY_EXPIRY_MINUTES = {"E0": 60, "E1": 30, "E2": 120, "E3": None, "E4": None}
MINUTE_NS = 60_000_000_000
DEFAULT_ROUND_TRIP = COMMISSION_SIDE * 2
TICK_MAGNITUDE = Decimal("30000")
REASONS = frozenset(
    {
        "objective",
        "stop",
        "break-even stop",
        "trailing stop",
        "expiry",
        "source deadline",
        "account-day close",
    }
)
JOBS_ROOT = Path("/workspace/implementation/reports/research-work/P15-16A/1e13829f2c88f1e1/jobs")
SLICE_DATES = (
    "2020-01-02",
    "2021-01-04",
    "2022-01-03",
    "2023-01-03",
    "2023-11-06",
    "2024-01-02",
    "2024-07-01",
    "2025-01-02",
    "2026-01-02",
    "2026-09-03",
)


@dataclass(frozen=True, slots=True)
class FrozenEntry:
    entry_id: str
    family: str
    branch: str
    side: int
    fill_price: Decimal
    fill_at_ns: int
    initial_stop: Decimal | None
    objective: Decimal | None
    source_deadline_ns: int | None
    flatten_at_ns: int
    quantity: int = 1
    round_trip_cost: Decimal = DEFAULT_ROUND_TRIP
    account_day: str = ""

    def __post_init__(self) -> None:
        if self.quantity != 1:
            raise ContractError("one-mini policy has no fractional partials")
        if self.side not in (-1, 1):
            raise ContractError("side must be -1 or 1")
        if self.flatten_at_ns < self.fill_at_ns:
            raise ContractError("flatten cannot precede fill")
        if type(self.fill_at_ns) is not int or type(self.flatten_at_ns) is not int:
            raise ContractError("clocks must be int nanoseconds")


@dataclass(frozen=True, slots=True)
class StopUpdate:
    trigger_batch_id: str
    trigger_available_at_ns: int
    effective_after_batch_id: str
    effective_available_at_ns: int
    stop: Decimal
    kind: str


@dataclass(frozen=True, slots=True)
class ExitRecord:
    policy_id: str
    entry_id: str
    exit_at_ns: int
    exit_price: Decimal
    reason: str
    net_points: Decimal
    net_dollars: Decimal
    stop_updates: tuple[StopUpdate, ...]
    complete: bool = True

    def __post_init__(self) -> None:
        if self.reason not in REASONS:
            raise ContractError(f"unknown exit reason {self.reason}")


@dataclass(frozen=True, slots=True)
class UnsupportedRecord:
    """E3/E4 only. Initial R is undefined. A04."""

    policy_id: str
    entry_id: str
    reason: str = "undefined_initial_r"
    complete: bool = False

    def __post_init__(self) -> None:
        if self.reason != "undefined_initial_r":
            raise ContractError("UnsupportedRecord is only undefined_initial_r")
        if self.policy_id not in ("E3", "E4"):
            raise ContractError("undefined initial R is unsupported only for E3/E4")


@dataclass(frozen=True, slots=True)
class IncompleteExit:
    """Trigger fired but no executable quote under the 5-second window."""

    policy_id: str
    entry_id: str
    reason: str = "incomplete_no_quote"
    trigger_reason: str | None = None
    trigger_ns: int | None = None
    complete: bool = False

    def __post_init__(self) -> None:
        if self.reason != "incomplete_no_quote":
            raise ContractError("IncompleteExit reason must be incomplete_no_quote")


PolicyRecord = ExitRecord | UnsupportedRecord | IncompleteExit


@dataclass(frozen=True, slots=True)
class PairedExits:
    entry_id: str
    records: dict[str, PolicyRecord]
    occupancy_flags: dict[str, bool]


@dataclass(frozen=True, slots=True)
class MarketBatch:
    batch_id: str
    event_ns: int
    available_at_ns: int
    bids: tuple[Decimal, ...]
    asks: tuple[Decimal, ...]
    trade_prices: tuple[Decimal, ...]
    bid: Decimal | None
    ask: Decimal | None
    bid_size: int
    ask_size: int
    ambiguous: bool


def attempt_partial_exit(quantity: int | Decimal) -> None:
    """One-mini benchmark rejects scale-outs. A03."""
    raise ContractError("one-mini policy has no fractional partials")


def initial_r(entry: FrozenEntry) -> Decimal | None:
    stop = entry.initial_stop
    if stop is None:
        return None
    width = abs(entry.fill_price - stop)
    if width <= 0:
        return None
    return width


def break_even_stop(entry: FrozenEntry) -> Decimal:
    offset = entry.round_trip_cost / POINT_VALUE
    return entry.fill_price + Decimal(entry.side) * offset


def _tighten(side: int, old: Decimal, candidate: Decimal) -> Decimal:
    if side == 1:
        return old if candidate < old else candidate
    return old if candidate > old else candidate


def _binding_deadline(entry: FrozenEntry, policy_id: str) -> tuple[int, str]:
    bound_ns = entry.flatten_at_ns
    bound_reason = "account-day close"
    minutes = POLICY_EXPIRY_MINUTES[policy_id]
    if minutes is not None:
        expiry_ns = entry.fill_at_ns + int(minutes) * MINUTE_NS
        if expiry_ns < bound_ns:
            bound_ns = expiry_ns
            bound_reason = "expiry"
    source = entry.source_deadline_ns
    if source is not None and source < bound_ns:
        bound_ns = source
        bound_reason = "source deadline"
    return bound_ns, bound_reason


def _hits_stop_batch(batch: MarketBatch, side: int, stop: Decimal | None) -> bool:
    if stop is None:
        return False
    if side == 1:
        if batch.bids and min(batch.bids) <= stop:
            return True
        return bool(batch.trade_prices) and min(batch.trade_prices) <= stop
    if batch.asks and max(batch.asks) >= stop:
        return True
    return bool(batch.trade_prices) and max(batch.trade_prices) >= stop


def _hits_target_batch(batch: MarketBatch, side: int, target: Decimal | None) -> bool:
    if target is None:
        return False
    if side == 1:
        if batch.bids and max(batch.bids) >= target:
            return True
        return bool(batch.trade_prices) and max(batch.trade_prices) >= target
    if batch.asks and min(batch.asks) <= target:
        return True
    return bool(batch.trade_prices) and min(batch.trade_prices) <= target


def _stop_reason(kind: str | None) -> str:
    if kind == "break_even":
        return "break-even stop"
    if kind == "trailing":
        return "trailing stop"
    return "stop"


def _fill_price(quote: QuoteBatch, side: int) -> Decimal:
    if side == 1:
        return quote.bid - TICK  # type: ignore[operator]
    return quote.ask + TICK  # type: ignore[operator]


def _make_exit(
    entry: FrozenEntry,
    policy_id: str,
    *,
    trigger_ns: int,
    reason: str,
    quotes: Sequence[QuoteBatch],
    stop_updates: tuple[StopUpdate, ...],
    account_end_ns: int | None,
) -> ExitRecord | IncompleteExit:
    after = trigger_ns + LATENCY_NS
    deadline = after + ENTRY_WINDOW_NS
    if account_end_ns is not None and deadline > account_end_ns:
        deadline = account_end_ns
    quote = select_quote(quotes, after_ns=after, deadline_ns=deadline)
    if quote is None:
        return IncompleteExit(
            policy_id,
            entry.entry_id,
            trigger_reason=reason,
            trigger_ns=trigger_ns,
        )
    price = _fill_price(quote, entry.side)
    points = net_points(
        side=entry.side,
        entry=entry.fill_price,
        exit_price=price,
        commission=entry.round_trip_cost,
    )
    dollars = net_dollars(
        side=entry.side,
        entry=entry.fill_price,
        exit_price=price,
        commission=entry.round_trip_cost,
    )
    return ExitRecord(
        policy_id=policy_id,
        entry_id=entry.entry_id,
        exit_at_ns=quote.available_at_ns,
        exit_price=price,
        reason=reason,
        net_points=points,
        net_dollars=dollars,
        stop_updates=stop_updates,
    )


class _Live:
    __slots__ = (
        "stop",
        "stop_kind",
        "pending_stop",
        "pending_kind",
        "pending_trigger",
        "pending_trigger_ns",
        "armed",
        "high_bid",
        "low_ask",
        "updates",
    )

    def __init__(self, stop: Decimal | None) -> None:
        self.stop = stop
        self.stop_kind: str | None = None
        self.pending_stop: Decimal | None = None
        self.pending_kind: str | None = None
        self.pending_trigger: str | None = None
        self.pending_trigger_ns: int | None = None
        self.armed = False
        self.high_bid: Decimal | None = None
        self.low_ask: Decimal | None = None
        self.updates: list[StopUpdate] = []

    def apply_pending(self, batch_id: str, available_at_ns: int) -> None:
        if self.pending_stop is None or self.pending_trigger is None or self.pending_trigger_ns is None:
            return
        self.stop = self.pending_stop
        self.stop_kind = self.pending_kind
        self.updates.append(
            StopUpdate(
                trigger_batch_id=self.pending_trigger,
                trigger_available_at_ns=self.pending_trigger_ns,
                effective_after_batch_id=batch_id,
                effective_available_at_ns=available_at_ns,
                stop=self.pending_stop,
                kind=self.pending_kind or "stop",
            )
        )
        self.pending_stop = None
        self.pending_kind = None
        self.pending_trigger = None
        self.pending_trigger_ns = None

    def queue(self, batch_id: str, new_stop: Decimal, kind: str, available_at_ns: int) -> None:
        if self.stop is not None and new_stop == self.stop and self.pending_stop is None:
            return
        self.pending_stop = new_stop
        self.pending_kind = kind
        self.pending_trigger = batch_id
        self.pending_trigger_ns = available_at_ns


def _manage(
    state: _Live,
    *,
    batch_id: str,
    available_at_ns: int,
    max_bid: Decimal | None,
    min_ask: Decimal | None,
    entry: FrozenEntry,
    policy_id: str,
    r_width: Decimal | None,
) -> None:
    if policy_id not in ("E3", "E4") or r_width is None:
        return
    side = entry.side
    if side == 1 and max_bid is not None:
        if state.high_bid is None or max_bid > state.high_bid:
            state.high_bid = max_bid
    if side == -1 and min_ask is not None:
        if state.low_ask is None or min_ask < state.low_ask:
            state.low_ask = min_ask
    reached = False
    if side == 1 and state.high_bid is not None:
        reached = state.high_bid >= entry.fill_price + r_width
    elif side == -1 and state.low_ask is not None:
        reached = state.low_ask <= entry.fill_price - r_width
    if not reached and not state.armed:
        return
    if not state.armed:
        state.armed = True
        if policy_id == "E3":
            be = break_even_stop(entry)
            base = state.stop if state.stop is not None else be
            state.queue(batch_id, _tighten(side, base, be), "break_even", available_at_ns)
            return
    if policy_id != "E4" or not state.armed:
        return
    base = state.pending_stop if state.pending_stop is not None else state.stop
    if side == 1:
        if state.high_bid is None:
            return
        candidate = state.high_bid - r_width
    else:
        if state.low_ask is None:
            return
        candidate = state.low_ask + r_width
    if base is None:
        state.queue(batch_id, candidate, "trailing", available_at_ns)
        return
    tightened = _tighten(side, base, candidate)
    if tightened != base or state.stop_kind != "trailing":
        state.queue(batch_id, tightened, "trailing", available_at_ns)


def _merge_batches(
    quotes: Sequence[QuoteBatch],
    trades: Sequence[PriceBatch | NativeBatch] = (),
) -> list[MarketBatch]:
    buckets: dict[int, dict[str, Any]] = {}

    def bucket(event_ns: int, available_at_ns: int) -> dict[str, Any]:
        row = buckets.get(event_ns)
        if row is None:
            row = {
                "available": available_at_ns,
                "bids": [],
                "asks": [],
                "trades": [],
                "bid": None,
                "ask": None,
                "bid_size": 0,
                "ask_size": 0,
                "ambiguous": False,
                "batch_id": f"m{event_ns}",
            }
            buckets[event_ns] = row
        if available_at_ns > row["available"]:
            row["available"] = available_at_ns
        return row

    for quote in quotes:
        row = bucket(quote.event_ns, quote.available_at_ns)
        row["batch_id"] = quote.batch_id
        if quote.bid is not None:
            row["bids"].append(quote.bid)
            row["bid"] = quote.bid
        if quote.ask is not None:
            row["asks"].append(quote.ask)
            row["ask"] = quote.ask
        row["bid_size"] = quote.bid_size or 0
        row["ask_size"] = quote.ask_size or 0
        row["ambiguous"] = row["ambiguous"] or quote.ambiguous
    for item in trades:
        if isinstance(item, NativeBatch):
            row = bucket(item.event_ns, item.available_at_ns)
            row["batch_id"] = item.batch_id
            for trade in item.trades:
                row["trades"].append(trade.price)
        else:
            row = bucket(item.event_ns, item.available_at_ns)
            row["trades"].extend(item.prices)
    out: list[MarketBatch] = []
    for event_ns in sorted(buckets):
        row = buckets[event_ns]
        out.append(
            MarketBatch(
                batch_id=str(row["batch_id"]),
                event_ns=event_ns,
                available_at_ns=int(row["available"]),
                bids=tuple(row["bids"]),
                asks=tuple(row["asks"]),
                trade_prices=tuple(row["trades"]),
                bid=row["bid"],
                ask=row["ask"],
                bid_size=int(row["bid_size"] or 0),
                ask_size=int(row["ask_size"] or 0),
                ambiguous=bool(row["ambiguous"]),
            )
        )
    return out


def evaluate_policy(
    entry: FrozenEntry,
    policy_id: str,
    quotes: Sequence[QuoteBatch],
    trades: Sequence[PriceBatch | NativeBatch] = (),
    *,
    known_at_guard: bool = True,
    market_batches: Sequence[MarketBatch] | None = None,
) -> PolicyRecord:
    if policy_id not in POLICIES:
        raise ContractError(f"unknown policy {policy_id}")
    r_width = initial_r(entry)
    if policy_id in ("E3", "E4") and r_width is None:
        return UnsupportedRecord(policy_id, entry.entry_id)
    quotes = tuple(sorted(quotes, key=lambda quote: (quote.available_at_ns, quote.batch_id)))
    batches = list(market_batches) if market_batches is not None else _merge_batches(quotes, trades)
    bound_ns, bound_reason = _binding_deadline(entry, policy_id)
    account_end = entry.flatten_at_ns + MINUTE_NS
    state = _Live(entry.initial_stop)
    ns_index = [batch.event_ns for batch in batches]
    start = bisect.bisect_right(ns_index, entry.fill_at_ns)
    for batch in batches[start:]:
        max_bid = max(batch.bids) if batch.bids else None
        min_ask = min(batch.asks) if batch.asks else None
        if known_at_guard:
            state.apply_pending(batch.batch_id, batch.available_at_ns)
        else:
            state.apply_pending(batch.batch_id, batch.available_at_ns)
            _manage(
                state,
                batch_id=batch.batch_id,
                available_at_ns=batch.available_at_ns,
                max_bid=max_bid,
                min_ask=min_ask,
                entry=entry,
                policy_id=policy_id,
                r_width=r_width,
            )
            state.apply_pending(batch.batch_id, batch.available_at_ns)
        hit_stop = _hits_stop_batch(batch, entry.side, state.stop)
        hit_obj = _hits_target_batch(batch, entry.side, entry.objective)
        time_hit = batch.available_at_ns >= bound_ns
        if hit_stop:
            return _make_exit(
                entry,
                policy_id,
                trigger_ns=batch.available_at_ns,
                reason=_stop_reason(state.stop_kind),
                quotes=quotes,
                stop_updates=tuple(state.updates),
                account_end_ns=account_end,
            )
        if hit_obj:
            return _make_exit(
                entry,
                policy_id,
                trigger_ns=batch.available_at_ns,
                reason="objective",
                quotes=quotes,
                stop_updates=tuple(state.updates),
                account_end_ns=account_end,
            )
        if time_hit:
            return _make_exit(
                entry,
                policy_id,
                trigger_ns=batch.available_at_ns,
                reason=bound_reason,
                quotes=quotes,
                stop_updates=tuple(state.updates),
                account_end_ns=account_end,
            )
        if known_at_guard:
            _manage(
                state,
                batch_id=batch.batch_id,
                available_at_ns=batch.available_at_ns,
                max_bid=max_bid,
                min_ask=min_ask,
                entry=entry,
                policy_id=policy_id,
                r_width=r_width,
            )
    return _make_exit(
        entry,
        policy_id,
        trigger_ns=bound_ns,
        reason=bound_reason,
        quotes=quotes,
        stop_updates=tuple(state.updates),
        account_end_ns=account_end,
    )


def evaluate_entry(
    entry: FrozenEntry,
    quotes: Sequence[QuoteBatch],
    trades: Sequence[PriceBatch | NativeBatch] = (),
    *,
    known_at_guard: bool = True,
    market_batches: Sequence[MarketBatch] | None = None,
) -> PairedExits:
    batches = list(market_batches) if market_batches is not None else _merge_batches(quotes, trades)
    records: dict[str, PolicyRecord] = {}
    for policy_id in POLICIES:
        records[policy_id] = evaluate_policy(
            entry,
            policy_id,
            quotes,
            trades,
            known_at_guard=known_at_guard,
            market_batches=batches,
        )
    return PairedExits(
        entry_id=entry.entry_id,
        records=records,
        occupancy_flags={policy_id: False for policy_id in POLICIES},
    )


def evaluate_entries(
    entries: Sequence[FrozenEntry],
    quotes: Sequence[QuoteBatch],
    trades: Sequence[PriceBatch | NativeBatch] = (),
    *,
    known_at_guard: bool = True,
    market_batches: Sequence[MarketBatch] | None = None,
) -> list[PairedExits]:
    batches = list(market_batches) if market_batches is not None else _merge_batches(quotes, trades)
    paired = [
        evaluate_entry(
            entry,
            quotes,
            trades,
            known_at_guard=known_at_guard,
            market_batches=batches,
        )
        for entry in entries
    ]
    by_key: dict[tuple[str, str], list[int]] = {}
    for index, entry in enumerate(entries):
        by_key.setdefault((entry.family, entry.branch), []).append(index)
    for indexes in by_key.values():
        ordered = sorted(indexes, key=lambda i: (entries[i].fill_at_ns, entries[i].entry_id))
        last_exit: dict[str, int] = {}
        for index in ordered:
            flags = dict(paired[index].occupancy_flags)
            fill = entries[index].fill_at_ns
            for policy_id in POLICIES:
                prev = last_exit.get(policy_id)
                if prev is not None and fill < prev:
                    flags[policy_id] = True
                rec = paired[index].records[policy_id]
                if isinstance(rec, ExitRecord) and rec.complete:
                    last_exit[policy_id] = rec.exit_at_ns
            paired[index] = PairedExits(paired[index].entry_id, paired[index].records, flags)
    return paired


def _as_decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    text = str(value)
    if text in {"", "None", "null"}:
        return None
    number = Decimal(text)
    if not number.is_finite():
        raise ContractError("nonfinite price")
    return number


def _geometry_price(geometry: Mapping[str, Any], *names: str) -> Decimal | None:
    for name in names:
        if name not in geometry or geometry[name] is None:
            continue
        raw = _as_decimal(geometry[name])
        if raw is None:
            continue
        if name.endswith("_ticks") or (raw == raw.to_integral_value() and abs(raw) >= TICK_MAGNITUDE):
            from trading_research.research.rule_discovery.native import ticks_to_decimal

            return ticks_to_decimal(int(raw))
        return raw
    return None


def frozen_entry_from_b02_episode(
    episode: Mapping[str, Any],
    *,
    flatten_at_ns: int,
    round_trip_cost: Decimal = DEFAULT_ROUND_TRIP,
) -> FrozenEntry | None:
    if episode.get("research_verdict") != "pass":
        return None
    geometry = episode.get("geometry") or {}
    if not isinstance(geometry, Mapping):
        return None
    fill = _geometry_price(geometry, "entry", "entry_ticks")
    stop = _geometry_price(geometry, "stop", "stop_ticks")
    target = _geometry_price(geometry, "target", "target_ticks", "first_objective")
    if fill is None or stop is None or target is None:
        return None
    raw_side = episode.get("side")
    if raw_side in (1, "long", "LONG"):
        side = 1
    elif raw_side in (-1, "short", "SHORT"):
        side = -1
    else:
        return None
    if side * (fill - stop) <= 0 or side * (target - fill) <= 0:
        return None
    source = geometry.get("objective_horizon_ns")
    if source is None:
        source = geometry.get("cancel_ns")
    source_ns = int(source) if source is not None else None
    entry_id = str(episode.get("candidate_id") or episode.get("reference_id") or "")
    if not entry_id:
        return None
    fill_at = episode.get("decision_at")
    if fill_at is None:
        return None
    return FrozenEntry(
        entry_id=entry_id,
        family=str(episode.get("method") or episode.get("family") or ""),
        branch=str(episode.get("branch") or ""),
        side=side,
        fill_price=fill,
        fill_at_ns=int(fill_at),
        initial_stop=stop,
        objective=target,
        source_deadline_ns=source_ns,
        flatten_at_ns=flatten_at_ns,
        round_trip_cost=round_trip_cost,
        account_day=str(episode.get("session_date") or ""),
    )


def batches_from_view(view: Any) -> tuple[list[MarketBatch], list[QuoteBatch]]:
    from trading_research.research.rule_discovery.native import ticks_to_decimal

    arrays = view.arrays
    n = int(arrays.t_ns.size)
    batches: list[MarketBatch] = []
    quotes: list[QuoteBatch] = []
    sha = getattr(getattr(view, "_evidence", None), "artifact_sha256", None) or ("a" * 64)
    i = 0
    while i < n:
        event_ns = int(arrays.t_ns[i])
        j = i + 1
        while j < n and int(arrays.t_ns[j]) == event_ns:
            j += 1
        available = max(event_ns, max(int(arrays.known_at_ns[k]) for k in range(i, j)))
        bids: list[Decimal] = []
        asks: list[Decimal] = []
        trades: list[Decimal] = []
        bid_ticks = set()
        ask_ticks = set()
        for k in range(i, j):
            bt = int(arrays.bid_ticks[k])
            at = int(arrays.ask_ticks[k])
            if bt:
                bids.append(ticks_to_decimal(bt))
                bid_ticks.add(bt)
            if at:
                asks.append(ticks_to_decimal(at))
                ask_ticks.add(at)
            if bool(arrays.is_trade[k]) and int(arrays.price_ticks[k]):
                trades.append(ticks_to_decimal(int(arrays.price_ticks[k])))
        last = j - 1
        bid = ticks_to_decimal(int(arrays.bid_ticks[last])) if int(arrays.bid_ticks[last]) else None
        ask = ticks_to_decimal(int(arrays.ask_ticks[last])) if int(arrays.ask_ticks[last]) else None
        bid_size = int(arrays.bid_sz[last]) or 0
        ask_size = int(arrays.ask_sz[last]) or 0
        ambiguous = len(bid_ticks) > 1 or len(ask_ticks) > 1
        batch_id = f"{arrays.instrument_id}:{event_ns}"
        batches.append(
            MarketBatch(
                batch_id=batch_id,
                event_ns=event_ns,
                available_at_ns=available,
                bids=tuple(bids),
                asks=tuple(asks),
                trade_prices=tuple(trades),
                bid=bid,
                ask=ask,
                bid_size=bid_size,
                ask_size=ask_size,
                ambiguous=ambiguous,
            )
        )
        if (
            bid is not None
            and ask is not None
            and ask >= bid
            and bid_size > 0
            and ask_size > 0
            and not ambiguous
        ):
            row_id = str(arrays.row_id[last]) if getattr(arrays, "row_id", None) is not None and arrays.row_id.size else batch_id
            evidence = EvidenceRef(
                artifact_sha256=sha if len(str(sha)) == 64 else "a" * 64,
                row_ids=(row_id or batch_id,),
                event_start_ns=event_ns,
                event_end_ns=event_ns,
                available_at_ns=available,
                coverage=Coverage.COMPLETE,
                limitation_ids=(),
            )
            quotes.append(
                QuoteBatch(
                    batch_id=f"quote:{batch_id}",
                    asset_id=getattr(view, "asset_id", "NQ:x"),
                    event_ns=event_ns,
                    available_at_ns=available,
                    bid=bid,
                    ask=ask,
                    bid_size=bid_size,
                    ask_size=ask_size,
                    ambiguous=False,
                    evidence=(evidence,),
                )
            )
        i = j
    return batches, quotes


@dataclass(slots=True)
class CompactDay:
    event_ns: np.ndarray
    available_at_ns: np.ndarray
    min_bid: np.ndarray
    max_bid: np.ndarray
    min_ask: np.ndarray
    max_ask: np.ndarray
    min_trade: np.ndarray
    max_trade: np.ndarray
    q_avail: np.ndarray
    q_bid: np.ndarray
    q_ask: np.ndarray


def compact_from_view(view: Any) -> CompactDay:
    """Group one account day's tick arrays by event timestamp.

    P15-17: the grouping loop that used to stand here ran in Python over every
    distinct event of the account day and cost 7.2 s of a measured session
    (2020-01-02, 190,809 groups, one core). `kernels.compact_day_kernel` is
    that loop statement for statement over the same int64 arrays, and
    `compact_from_view_scalar` (appended at the end of this module) keeps the
    original as its parity oracle. Measured on the same session: 0.023 s.

    The kernel is compiled for int64/bool inputs; the native arrays already
    carry those dtypes, so `ascontiguousarray` is a no-op view, not a copy.

    Nothing below this function may move: a `runtime_failure` job row records a
    traceback, and a traceback names the line of every frame, so this module's
    line numbers are part of the bytes the engine writes.
    """
    arrays = view.arrays
    n = int(arrays.t_ns.size)
    if n == 0:
        empty = np.zeros(0, dtype=np.int64)
        nan = np.zeros(0, dtype=np.float64)
        return CompactDay(empty, empty, nan, nan, nan, nan, nan, nan, empty, nan, nan)
    return CompactDay(
        *kernels.compact_day_kernel(
            np.ascontiguousarray(arrays.t_ns, dtype=np.int64),
            np.ascontiguousarray(arrays.known_at_ns, dtype=np.int64),
            np.ascontiguousarray(arrays.bid_ticks, dtype=np.int64),
            np.ascontiguousarray(arrays.ask_ticks, dtype=np.int64),
            np.ascontiguousarray(arrays.price_ticks, dtype=np.int64),
            np.ascontiguousarray(arrays.is_trade, dtype=np.bool_),
            np.ascontiguousarray(arrays.bid_sz, dtype=np.int64),
            np.ascontiguousarray(arrays.ask_sz, dtype=np.int64),
            0.25,
        )
    )


# --------------------------------------------------------------------------
# The blank run below is deliberate and load-bearing. A P15-17 job row with
# status `runtime_failure` records `traceback.format_exc()`, and a traceback
# names the line of every frame it walks -- several of them in this module.
# The speedup above therefore had to be written WITHOUT moving any line: a
# replaced function body is padded back to its original length here and every
# new definition is appended past the last existing one. Do not close this
# gap; closing it silently rewrites the bytes of every failure row.
# --------------------------------------------------------------------------






























def _finite_le(value: float, bound: float) -> bool:
    return value == value and value <= bound


def _finite_ge(value: float, bound: float) -> bool:
    return value == value and value >= bound


def _hit_stop_compact(day: CompactDay, index: int, side: int, stop: Decimal | None) -> bool:
    if stop is None:
        return False
    level = float(stop)
    if side == 1:
        return _finite_le(float(day.min_bid[index]), level) or _finite_le(float(day.min_trade[index]), level)
    return _finite_ge(float(day.max_ask[index]), level) or _finite_ge(float(day.max_trade[index]), level)


def _hit_target_compact(day: CompactDay, index: int, side: int, target: Decimal | None) -> bool:
    if target is None:
        return False
    level = float(target)
    if side == 1:
        return _finite_ge(float(day.max_bid[index]), level) or _finite_ge(float(day.max_trade[index]), level)
    return _finite_le(float(day.min_ask[index]), level) or _finite_le(float(day.min_trade[index]), level)


def _fill_from_compact(
    day: CompactDay,
    side: int,
    after_ns: int,
    deadline_ns: int,
) -> tuple[int, Decimal] | None:
    idx = int(np.searchsorted(day.q_avail, after_ns, side="left"))
    n = int(day.q_avail.size)
    while idx < n and int(day.q_avail[idx]) <= deadline_ns:
        avail = int(day.q_avail[idx])
        if side == 1:
            price = Decimal(str(day.q_bid[idx])) - TICK
        else:
            price = Decimal(str(day.q_ask[idx])) + TICK
        return avail, price
    return None


def _make_exit_compact(
    entry: FrozenEntry,
    policy_id: str,
    *,
    trigger_ns: int,
    reason: str,
    day: CompactDay,
    stop_updates: tuple[StopUpdate, ...],
    account_end_ns: int,
) -> ExitRecord | IncompleteExit:
    after = trigger_ns + LATENCY_NS
    deadline = after + ENTRY_WINDOW_NS
    if deadline > account_end_ns:
        deadline = account_end_ns
    filled = _fill_from_compact(day, entry.side, after, deadline)
    if filled is None:
        return IncompleteExit(
            policy_id,
            entry.entry_id,
            trigger_reason=reason,
            trigger_ns=trigger_ns,
        )
    exit_at, price = filled
    points = net_points(
        side=entry.side,
        entry=entry.fill_price,
        exit_price=price,
        commission=entry.round_trip_cost,
    )
    dollars = net_dollars(
        side=entry.side,
        entry=entry.fill_price,
        exit_price=price,
        commission=entry.round_trip_cost,
    )
    return ExitRecord(
        policy_id=policy_id,
        entry_id=entry.entry_id,
        exit_at_ns=exit_at,
        exit_price=price,
        reason=reason,
        net_points=points,
        net_dollars=dollars,
        stop_updates=stop_updates,
    )


def evaluate_policy_compact(
    entry: FrozenEntry,
    policy_id: str,
    day: CompactDay,
    *,
    known_at_guard: bool = True,
) -> PolicyRecord:
    """Manage one fixed entry to its exit over the compact account-day tape.

    P15-17: E0, E1 and E2 never move the stop -- `_manage` returns on its first
    line for any policy outside ("E3", "E4"), so nothing is ever queued and
    `state.updates` stays empty -- which makes the whole walk a first passage
    over a fixed stop, a fixed objective and one binding deadline.
    `kernels.fixed_stop_first_passage_kernel` runs the identical three tests in
    the identical source order (stop, then objective, then the deadline, so a
    batch that touches both is the pessimistic stop) and stops at the identical
    batch. E3 and E4, which do move the stop, still walk the Python loop, which
    lives on as `evaluate_policy_compact_scalar` at the end of this module and
    is also the parity oracle the tests compare the kernel against.

    Measured 2026-09-16 on 2020-01-02, one core: the whole bank's E0 benchmark
    (148 candidates, plus the cost-stress repeat) fell from 40.6 s to 1.1 s
    together with the scan reuse; on synthetic tapes with equal-timestamp
    batches, gaps and quoteless batches the two paths agree record for record.

    Nothing below this function may move: a `runtime_failure` job row records a
    traceback, and a traceback names the line of every frame, so this module's
    line numbers are part of the bytes the engine writes.
    """
    if policy_id not in POLICIES:
        raise ContractError(f"unknown policy {policy_id}")
    if policy_id in ("E3", "E4"):
        return evaluate_policy_compact_scalar(
            entry, policy_id, day, known_at_guard=known_at_guard
        )
    bound_ns, bound_reason = _binding_deadline(entry, policy_id)
    index, code = kernels.fixed_stop_first_passage_kernel(
        day.min_bid,
        day.max_bid,
        day.min_ask,
        day.max_ask,
        day.min_trade,
        day.max_trade,
        day.available_at_ns,
        int(np.searchsorted(day.event_ns, entry.fill_at_ns, side="right")),
        int(entry.side),
        0.0 if entry.initial_stop is None else float(entry.initial_stop),
        entry.initial_stop is not None,
        0.0 if entry.objective is None else float(entry.objective),
        entry.objective is not None,
        int(bound_ns),
    )
    if code == 0:
        trigger_ns = int(bound_ns)
        reason = bound_reason
    else:
        trigger_ns = int(day.available_at_ns[index])
        reason = _stop_reason(None) if code == 1 else ("objective" if code == 2 else bound_reason)
    return _make_exit_compact(
        entry,
        policy_id,
        trigger_ns=trigger_ns,
        reason=reason,
        day=day,
        stop_updates=(),
        account_end_ns=entry.flatten_at_ns + MINUTE_NS,
    )


# --------------------------------------------------------------------------
# The blank run below is deliberate and load-bearing. A P15-17 job row with
# status `runtime_failure` records `traceback.format_exc()`, and a traceback
# names the line of every frame it walks -- several of them in this module.
# The speedup above therefore had to be written WITHOUT moving any line: a
# replaced function body is padded back to its original length here and every
# new definition is appended past the last existing one. Do not close this
# gap; closing it silently rewrites the bytes of every failure row.
# --------------------------------------------------------------------------






















def _flag_occupancy(entries: Sequence[FrozenEntry], paired: list[PairedExits]) -> list[PairedExits]:
    by_key: dict[tuple[str, str], list[int]] = {}
    for index, entry in enumerate(entries):
        by_key.setdefault((entry.family, entry.branch), []).append(index)
    for indexes in by_key.values():
        ordered = sorted(indexes, key=lambda i: (entries[i].fill_at_ns, entries[i].entry_id))
        last_exit: dict[str, int] = {}
        for index in ordered:
            flags = dict(paired[index].occupancy_flags)
            fill = entries[index].fill_at_ns
            for policy_id in POLICIES:
                prev = last_exit.get(policy_id)
                if prev is not None and fill < prev:
                    flags[policy_id] = True
                rec = paired[index].records[policy_id]
                if isinstance(rec, ExitRecord) and rec.complete:
                    last_exit[policy_id] = rec.exit_at_ns
            paired[index] = PairedExits(paired[index].entry_id, paired[index].records, flags)
    return paired


def evaluate_entries_compact(entries: Sequence[FrozenEntry], day: CompactDay) -> list[PairedExits]:
    paired = []
    for entry in entries:
        records = {
            policy_id: evaluate_policy_compact(entry, policy_id, day) for policy_id in POLICIES
        }
        paired.append(
            PairedExits(
                entry_id=entry.entry_id,
                records=records,
                occupancy_flags={policy_id: False for policy_id in POLICIES},
            )
        )
    return _flag_occupancy(entries, paired)


def record_to_json(record: PolicyRecord) -> dict[str, Any]:
    if isinstance(record, UnsupportedRecord):
        return {
            "policy_id": record.policy_id,
            "entry_id": record.entry_id,
            "reason": record.reason,
            "complete": False,
            "disposition": "unsupported_undefined_r",
        }
    if isinstance(record, IncompleteExit):
        return {
            "policy_id": record.policy_id,
            "entry_id": record.entry_id,
            "reason": record.reason,
            "trigger_reason": record.trigger_reason,
            "trigger_ns": record.trigger_ns,
            "complete": False,
            "disposition": "incomplete_no_quote",
        }
    return {
        "policy_id": record.policy_id,
        "entry_id": record.entry_id,
        "exit_at_ns": record.exit_at_ns,
        "exit_price": str(record.exit_price),
        "reason": record.reason,
        "net_points": str(record.net_points),
        "net_dollars": str(record.net_dollars),
        "complete": True,
        "stop_updates": [
            {
                "trigger_batch_id": item.trigger_batch_id,
                "trigger_available_at_ns": item.trigger_available_at_ns,
                "effective_after_batch_id": item.effective_after_batch_id,
                "effective_available_at_ns": item.effective_available_at_ns,
                "stop": str(item.stop),
                "kind": item.kind,
            }
            for item in record.stop_updates
        ],
    }


def paired_to_json(paired: PairedExits, entry: FrozenEntry | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {
        "entry_id": paired.entry_id,
        "occupancy_flags": paired.occupancy_flags,
        "records": {policy_id: record_to_json(paired.records[policy_id]) for policy_id in POLICIES},
    }
    if entry is not None:
        body.update(
            {
                "family": entry.family,
                "branch": entry.branch,
                "side": entry.side,
                "fill_price": str(entry.fill_price),
                "fill_at_ns": entry.fill_at_ns,
                "account_day": entry.account_day,
            }
        )
    return body


def _load_pass_entries(day: str, jobs_root: Path, flatten_at_ns: int) -> list[FrozenEntry]:
    folder = jobs_root / day
    entries: list[FrozenEntry] = []
    if not folder.is_dir():
        return entries
    for path in sorted(folder.glob("*.json.gz")):
        with gzip.open(path, "rt") as handle:
            document = json.load(handle)
        for episode in document.get("episodes") or []:
            frozen = frozen_entry_from_b02_episode(episode, flatten_at_ns=flatten_at_ns)
            if frozen is not None:
                entries.append(replace(frozen, account_day=day))
    return entries


def run_native_slice(
    dates: Sequence[str] = SLICE_DATES,
    jobs_root: Path = JOBS_ROOT,
    *,
    out_dir: Path,
) -> dict[str, Any]:
    from trading_research.research.rule_discovery.native import (
        account_day_window,
        build_market_view,
        install_write_guard,
    )

    install_write_guard()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs_root = Path(jobs_root)
    slice_rows: list[dict[str, Any]] = []
    reason_counts = {policy_id: {} for policy_id in POLICIES}
    net_sums = {policy_id: Decimal(0) for policy_id in POLICIES}
    undefined_r_counts = {policy_id: 0 for policy_id in POLICIES}
    incomplete_counts = {policy_id: 0 for policy_id in POLICIES}
    occupancy_counts = {policy_id: 0 for policy_id in POLICIES}
    date_counts: list[dict[str, Any]] = []
    n_entries = 0
    for day in dates:
        start_ns, end_ns = account_day_window(date.fromisoformat(day))
        flatten_at_ns = end_ns - MINUTE_NS
        entries = _load_pass_entries(day, jobs_root, flatten_at_ns)
        view = build_market_view(day, full_account_day=True)
        tape = compact_from_view(view)
        paired_rows = evaluate_entries_compact(entries, tape)
        day_n = 0
        for entry, paired in zip(entries, paired_rows):
            n_entries += 1
            day_n += 1
            body = paired_to_json(paired, entry)
            body["account_day"] = day
            slice_rows.append(body)
            for policy_id in POLICIES:
                rec = paired.records[policy_id]
                if paired.occupancy_flags[policy_id]:
                    occupancy_counts[policy_id] += 1
                if isinstance(rec, UnsupportedRecord):
                    undefined_r_counts[policy_id] += 1
                    continue
                if isinstance(rec, IncompleteExit):
                    incomplete_counts[policy_id] += 1
                    continue
                bucket = reason_counts[policy_id]
                bucket[rec.reason] = bucket.get(rec.reason, 0) + 1
                net_sums[policy_id] += rec.net_points
                if rec.exit_at_ns > end_ns:
                    raise ContractError(f"exit after account-day close {day} {entry.entry_id}")
        date_counts.append({"date": day, "entries": day_n})
        del view, tape, paired_rows, entries
    reconciliation = {
        "schema": "p15-19-prep-reconciliation-v2",
        "descriptive_only": True,
        "dates": list(dates),
        "date_counts": date_counts,
        "entries": n_entries,
        "jobs_root": str(jobs_root),
        "per_policy": {
            policy_id: {
                "reason_counts": reason_counts[policy_id],
                "reason_sum": sum(reason_counts[policy_id].values()),
                "unsupported_undefined_r": undefined_r_counts[policy_id],
                "incomplete_no_quote": incomplete_counts[policy_id],
                "occupancy_flagged": occupancy_counts[policy_id],
                "net_points": str(net_sums[policy_id]),
            }
            for policy_id in POLICIES
        },
    }
    for policy_id in POLICIES:
        row = reconciliation["per_policy"][policy_id]
        total = row["reason_sum"] + row["unsupported_undefined_r"] + row["incomplete_no_quote"]
        if total != n_entries:
            raise ContractError(f"{policy_id} record count {total} != entries {n_entries}")
        if policy_id in ("E0", "E1", "E2") and row["unsupported_undefined_r"] != 0:
            raise ContractError(f"{policy_id} must not emit undefined-R unsupported records")
    (out_dir / "SLICE_EXITS.json").write_text(json.dumps({"entries": slice_rows}, indent=2) + "\n")
    (out_dir / "RECONCILIATION.json").write_text(json.dumps(reconciliation, indent=2) + "\n")
    return reconciliation


# --------------------------------------------------------------------------
# P15-17 speedup, appended so that NO line number above this point moves.
# --------------------------------------------------------------------------
from trading_research.research.rule_discovery import kernels  # noqa: E402


def compact_from_view_scalar(view: Any) -> CompactDay:
    """The pre-kernel reference implementation, kept as the parity oracle."""
    arrays = view.arrays
    n = int(arrays.t_ns.size)
    if n == 0:
        empty = np.zeros(0, dtype=np.int64)
        nan = np.zeros(0, dtype=np.float64)
        return CompactDay(empty, empty, nan, nan, nan, nan, nan, nan, empty, nan, nan)
    t = arrays.t_ns
    change = np.empty(n, dtype=np.bool_)
    change[0] = True
    if n > 1:
        change[1:] = t[1:] != t[:-1]
    starts = np.flatnonzero(change)
    g = int(starts.size)
    event_ns = np.empty(g, dtype=np.int64)
    available_at_ns = np.empty(g, dtype=np.int64)
    min_bid = np.full(g, np.nan)
    max_bid = np.full(g, np.nan)
    min_ask = np.full(g, np.nan)
    max_ask = np.full(g, np.nan)
    min_trade = np.full(g, np.nan)
    max_trade = np.full(g, np.nan)
    q_avail = np.empty(g, dtype=np.int64)
    q_bid = np.empty(g, dtype=np.float64)
    q_ask = np.empty(g, dtype=np.float64)
    q_n = 0
    tick = 0.25
    for gi, start in enumerate(starts):
        start = int(start)
        end = int(starts[gi + 1]) if gi + 1 < g else n
        event = int(t[start])
        event_ns[gi] = event
        known = int(np.max(arrays.known_at_ns[start:end]))
        available_at_ns[gi] = event if event > known else known
        bids = arrays.bid_ticks[start:end]
        asks = arrays.ask_ticks[start:end]
        pos_b = bids[bids > 0]
        pos_a = asks[asks > 0]
        if pos_b.size:
            min_bid[gi] = float(int(pos_b.min())) * tick
            max_bid[gi] = float(int(pos_b.max())) * tick
        if pos_a.size:
            min_ask[gi] = float(int(pos_a.min())) * tick
            max_ask[gi] = float(int(pos_a.max())) * tick
        trades = arrays.price_ticks[start:end]
        trade_mask = arrays.is_trade[start:end] & (trades > 0)
        if np.any(trade_mask):
            px = trades[trade_mask]
            min_trade[gi] = float(int(px.min())) * tick
            max_trade[gi] = float(int(px.max())) * tick
        last = end - 1
        bt = int(arrays.bid_ticks[last])
        at = int(arrays.ask_ticks[last])
        bsz = int(arrays.bid_sz[last])
        asz = int(arrays.ask_sz[last])
        unique_b = int(np.unique(pos_b).size) if pos_b.size else 0
        unique_a = int(np.unique(pos_a).size) if pos_a.size else 0
        if bt > 0 and at > 0 and at >= bt and bsz > 0 and asz > 0 and unique_b <= 1 and unique_a <= 1:
            q_avail[q_n] = available_at_ns[gi]
            q_bid[q_n] = float(bt) * tick
            q_ask[q_n] = float(at) * tick
            q_n += 1
    return CompactDay(
        event_ns,
        available_at_ns,
        min_bid,
        max_bid,
        min_ask,
        max_ask,
        min_trade,
        max_trade,
        q_avail[:q_n],
        q_bid[:q_n],
        q_ask[:q_n],
    )




def evaluate_policy_compact_scalar(
    entry: FrozenEntry,
    policy_id: str,
    day: CompactDay,
    *,
    known_at_guard: bool = True,
) -> PolicyRecord:
    """The pre-kernel reference loop: E3/E4 still run it, and the tests compare
    the first-passage kernel against it record for record."""
    if policy_id not in POLICIES:
        raise ContractError(f"unknown policy {policy_id}")
    r_width = initial_r(entry)
    if policy_id in ("E3", "E4") and r_width is None:
        return UnsupportedRecord(policy_id, entry.entry_id)
    bound_ns, bound_reason = _binding_deadline(entry, policy_id)
    account_end = entry.flatten_at_ns + MINUTE_NS
    state = _Live(entry.initial_stop)
    start = int(np.searchsorted(day.event_ns, entry.fill_at_ns, side="right"))
    n = int(day.event_ns.size)
    side = entry.side
    for index in range(start, n):
        batch_id = str(int(day.event_ns[index]))
        avail_ns = int(day.available_at_ns[index])
        mb = float(day.max_bid[index])
        ma = float(day.min_ask[index])
        max_bid = None
        min_ask = None
        if mb == mb and (state.high_bid is None or mb > float(state.high_bid)):
            max_bid = Decimal(str(mb))
        if ma == ma and (state.low_ask is None or ma < float(state.low_ask)):
            min_ask = Decimal(str(ma))
        if known_at_guard:
            state.apply_pending(batch_id, avail_ns)
        else:
            state.apply_pending(batch_id, avail_ns)
            _manage(
                state,
                batch_id=batch_id,
                available_at_ns=avail_ns,
                max_bid=max_bid,
                min_ask=min_ask,
                entry=entry,
                policy_id=policy_id,
                r_width=r_width,
            )
            state.apply_pending(batch_id, avail_ns)
        hit_stop = _hit_stop_compact(day, index, side, state.stop)
        hit_obj = _hit_target_compact(day, index, side, entry.objective)
        time_hit = avail_ns >= bound_ns
        trigger_ns = avail_ns
        if hit_stop:
            return _make_exit_compact(
                entry,
                policy_id,
                trigger_ns=trigger_ns,
                reason=_stop_reason(state.stop_kind),
                day=day,
                stop_updates=tuple(state.updates),
                account_end_ns=account_end,
            )
        if hit_obj:
            return _make_exit_compact(
                entry,
                policy_id,
                trigger_ns=trigger_ns,
                reason="objective",
                day=day,
                stop_updates=tuple(state.updates),
                account_end_ns=account_end,
            )
        if time_hit:
            return _make_exit_compact(
                entry,
                policy_id,
                trigger_ns=trigger_ns,
                reason=bound_reason,
                day=day,
                stop_updates=tuple(state.updates),
                account_end_ns=account_end,
            )
        if known_at_guard:
            _manage(
                state,
                batch_id=batch_id,
                available_at_ns=avail_ns,
                max_bid=max_bid,
                min_ask=min_ask,
                entry=entry,
                policy_id=policy_id,
                r_width=r_width,
            )
    return _make_exit_compact(
        entry,
        policy_id,
        trigger_ns=bound_ns,
        reason=bound_reason,
        day=day,
        stop_updates=tuple(state.updates),
        account_end_ns=account_end,
    )


# ==========================================================================
# P15-19 — the fixed-entry exit study.
#
# The entry stage is frozen before this runs: the entries, their sizes, costs
# and initial structural stops come from the P15-18 selected rules' own job
# documents. This is a separately counted decision family: it compares E0-E4 on
# those unchanged entries and can never change an entry candidate's disposition.
# ==========================================================================

P15_19_TASK_ID = "P15-19"
EXIT_RESULTS_SCHEMA = "research-p15-19-exit-results-v1"
FIXED_ENTRIES_SCHEMA = "research-p15-19-fixed-entries-v1"
EXIT_SHARD_SCHEMA = "research-p15-19-exit-shard-v1"


def selected_entry_rules(
    refinement_run_root: str | Path, breadth_run_root: str | Path
) -> list[dict[str, Any]]:
    """The frozen entry rules of the exit study, with the run that holds each.

    A fold that kept its breadth parent contributes that parent (its entries live
    in the breadth run); a refined or combined rule contributes itself.
    """
    refinement = Path(refinement_run_root)
    breadth = Path(breadth_run_root)
    rules = json.loads((refinement / "SELECTED_RULES_BY_FOLD.json").read_text())
    executed: set[str] = set()
    combinations = refinement / "combinations" / "COMBINATIONS.json"
    if combinations.is_file():
        executed = set(json.loads(combinations.read_text())["executed"])
    out: dict[str, dict[str, Any]] = {}

    def add(candidate_id: str, *, role: str, jobs_root: Path, family: str, year: int, parents):
        row = out.setdefault(
            str(candidate_id),
            {
                "candidate_id": str(candidate_id),
                "role": role,
                "family": family,
                "jobs_root": str(jobs_root),
                "parent_trial_ids": list(parents),
                "outer_folds": [],
            },
        )
        row["outer_folds"].append(int(year))

    for fold in rules["folds"]:
        year = int(fold["outer_fold"])
        for role in fold["roles"]:
            if role["role"] == "refined_selected":
                add(
                    role["candidate_id"],
                    role="refined_selected",
                    jobs_root=refinement,
                    family=role["family"],
                    year=year,
                    parents=role.get("parent_trial_ids") or [],
                )
            else:
                # the fold kept the breadth parent: its entries are the parent's
                for parent in role.get("parent_trial_ids") or []:
                    add(
                        parent,
                        role="retained_parent",
                        jobs_root=breadth,
                        family=role["family"],
                        year=year,
                        parents=[role["candidate_id"]],
                    )
        for candidate_id in fold.get("combinations") or []:
            if candidate_id in executed:
                add(
                    candidate_id,
                    role="combined",
                    jobs_root=refinement / "combinations",
                    family=str(candidate_id).split(":")[0],
                    year=year,
                    parents=[],
                )
    return [out[key] for key in sorted(out)]


def _entry_from_job_row(
    row: Mapping[str, Any], *, day: str, family: str, branch: str, flatten_at_ns: int
) -> FrozenEntry:
    """Rebuild the frozen entry a run recorded. The source deadline is not in the
    record, so it is left unset here and the study verifies the reconstruction by
    recomputing E0 and comparing it with the E0 the run wrote."""
    return FrozenEntry(
        entry_id=str(row["entry_id"]),
        family=family,
        branch=branch,
        side=int(row["side"]),
        fill_price=Decimal(str(row["fill_price"])),
        fill_at_ns=int(row["fill_at_ns"]),
        initial_stop=None if row.get("initial_stop") is None else Decimal(str(row["initial_stop"])),
        objective=None if row.get("objective") is None else Decimal(str(row["objective"])),
        source_deadline_ns=None,
        flatten_at_ns=int(flatten_at_ns),
        round_trip_cost=Decimal(str(row.get("round_trip_cost") or DEFAULT_ROUND_TRIP)),
        account_day=day,
    )


def frozen_entries_for_day(
    day: str, rules: Sequence[Mapping[str, Any]], *, flatten_at_ns: int
) -> dict[str, list[tuple[FrozenEntry, dict[str, Any]]]]:
    """Every frozen entry of every selected rule on one account day, with the E0
    record the entry run wrote beside it."""
    from trading_research.research.rule_discovery import search_run

    out: dict[str, list[tuple[FrozenEntry, dict[str, Any]]]] = {}
    for rule in rules:
        path = search_run.job_path(rule["jobs_root"], day, rule["candidate_id"])
        if not path.is_file():
            continue
        job = search_run.read_gz(path)
        body = job.get("candidate") or {}
        rows = body.get("entries") or []
        if not rows:
            continue
        pairs = []
        for row in rows:
            entry = _entry_from_job_row(
                row,
                day=day,
                family=str(job.get("family") or rule["family"]),
                branch=str(job.get("branch") or ""),
                flatten_at_ns=flatten_at_ns,
            )
            pairs.append((entry, dict(row)))
        out[str(rule["candidate_id"])] = pairs
    return out


def freeze_entries(
    *,
    breadth_run_root: str | Path,
    refinement_run_root: str | Path,
    out_path: str | Path | None = None,
    dates: Sequence[str] | None = None,
) -> dict[str, Any]:
    """FIXED_ENTRIES.json: which rules, which days, how many entries, and the
    initial structural risk each entry carries. Pure: it reads job documents."""
    from trading_research.research.rule_discovery import search_run

    rules = selected_entry_rules(refinement_run_root, breadth_run_root)
    refinement = Path(refinement_run_root)
    if dates is None:
        dates = json.loads((refinement / "MANIFEST.json").read_text())["dates"]
    per_rule: dict[str, dict[str, Any]] = {
        rule["candidate_id"]: {"entries": 0, "days": 0} for rule in rules
    }
    # The entry runs' daily shards already say how many entries each candidate
    # filled on each day, so the days that carry a frozen entry are found
    # without opening a single job document; the documents are read once, in the
    # run, for the days that actually have one.
    wanted: dict[str, set[str]] = {}
    for rule in rules:
        wanted.setdefault(str(rule["jobs_root"]), set()).add(str(rule["candidate_id"]))
    days: list[str] = []
    total = 0
    for day in dates:
        seen = False
        for jobs_root, ids in wanted.items():
            shard = search_run.daily_path(jobs_root, day)
            if shard.is_file():
                counts = {
                    row["candidate_id"]: int(row.get("candidate_fills") or 0)
                    for row in json.loads(shard.read_text())["rows"]
                    if row["candidate_id"] in ids
                }
            else:
                # no daily shard: read the documents rather than report no entry
                counts = {}
                for candidate_id in ids:
                    path = search_run.job_path(jobs_root, day, candidate_id)
                    if not path.is_file():
                        continue
                    body = search_run.read_gz(path).get("candidate") or {}
                    counts[candidate_id] = len(body.get("entries") or [])
            for candidate_id, fills in counts.items():
                if not fills:
                    continue
                seen = True
                stats = per_rule[candidate_id]
                stats["entries"] += fills
                stats["days"] += 1
                total += fills
        if seen:
            days.append(day)
    body = {
        "schema_version": FIXED_ENTRIES_SCHEMA,
        "task_id": P15_19_TASK_ID,
        "breadth_run_root": str(breadth_run_root),
        "refinement_run_root": str(refinement_run_root),
        "policies": list(POLICIES),
        "policy_expiry_minutes": dict(POLICY_EXPIRY_MINUTES),
        "rules": rules,
        "per_rule": per_rule,
        "dates_with_entries": days,
        "entries": total,
    }
    if out_path is not None:
        search_run._write_json(Path(out_path), body)
    return body


def evaluate_exit_day(
    day: str,
    rules: Sequence[Mapping[str, Any]],
    *,
    tape: CompactDay | None = None,
) -> dict[str, Any]:
    """One account day of the exit study: every frozen entry of every selected
    rule under all five policies, on one loaded tape.

    E0 is recomputed here and checked against the E0 the entry run recorded. A
    mismatch is reported per entry (it would mean the reconstruction lost a
    binding source deadline) and excluded from the paired comparison, never
    silently accepted.
    """
    from datetime import date as _date

    from trading_research.research.rule_discovery.native import (
        account_day_window,
        build_market_view,
        install_write_guard,
    )

    install_write_guard()
    _, end_ns = account_day_window(_date.fromisoformat(day))
    flatten_at_ns = end_ns - MINUTE_NS
    frozen = frozen_entries_for_day(day, rules, flatten_at_ns=flatten_at_ns)
    if not frozen:
        return {
            "schema_version": EXIT_SHARD_SCHEMA,
            "account_day": day,
            "rules": {},
            "entries": 0,
            "e0_mismatches": 0,
        }
    if tape is None:
        view = build_market_view(day, full_account_day=True)
        tape = compact_from_view(view)
    out: dict[str, Any] = {}
    mismatches = 0
    entries_seen = 0
    for candidate_id, pairs in frozen.items():
        entries = [entry for entry, _ in pairs]
        paired = evaluate_entries_compact(entries, tape)
        rows = []
        for (entry, recorded), result in zip(pairs, paired):
            entries_seen += 1
            row: dict[str, Any] = {
                "entry_id": entry.entry_id,
                "side": entry.side,
                "fill_at_ns": entry.fill_at_ns,
                "fill_price": str(entry.fill_price),
                "initial_stop": None if entry.initial_stop is None else str(entry.initial_stop),
                "objective": None if entry.objective is None else str(entry.objective),
                "round_trip_cost": str(entry.round_trip_cost),
                "recorded_e0": {
                    "exit_at_ns": recorded.get("exit_at_ns"),
                    "exit_reason": recorded.get("exit_reason"),
                    "net_points": recorded.get("net_points"),
                },
                "policies": {},
            }
            for policy_id in POLICIES:
                record = result.records[policy_id]
                body = record_to_json(record)
                body["occupancy_flagged"] = bool(result.occupancy_flags[policy_id])
                row["policies"][policy_id] = body
            e0 = row["policies"]["E0"]
            recorded_points = recorded.get("net_points")
            row["e0_matches_entry_run"] = bool(
                e0.get("complete")
                and recorded_points is not None
                and Decimal(str(e0["net_points"])) == Decimal(str(recorded_points))
                and int(e0["exit_at_ns"]) == int(recorded["exit_at_ns"])
            )
            if not row["e0_matches_entry_run"]:
                mismatches += 1
            rows.append(row)
        out[candidate_id] = rows
    return {
        "schema_version": EXIT_SHARD_SCHEMA,
        "task_id": P15_19_TASK_ID,
        "account_day": day,
        "rules": out,
        "entries": entries_seen,
        "e0_mismatches": mismatches,
    }


_EXIT_WORKER: dict[str, Any] = {}


def _init_exit_worker(payload: Mapping[str, Any]) -> None:
    _EXIT_WORKER.update(payload)


def _process_exit_date(day: str) -> dict[str, Any]:
    from trading_research.research.rule_discovery import search_run

    root = Path(_EXIT_WORKER["run_root"])
    started = time.perf_counter()
    try:
        shard = evaluate_exit_day(day, _EXIT_WORKER["rules"])
    except Exception as exc:
        record = {
            "date": day,
            "status": "failed",
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(limit=8),
        }
        search_run._write_json(root / "failed" / f"{day}.json", record)
        return record
    finally:
        # the same per-session cache release the breadth runner uses: pure
        # loaders keyed by path, so releasing them changes no result
        search_run.release_session_caches()
        gc.collect()
    path = search_run._write_json(root / "exits" / f"{day}.json", shard)
    record = {
        "date": day,
        "status": "completed",
        "entries": shard["entries"],
        "e0_mismatches": shard["e0_mismatches"],
        "shard_sha256": search_run.file_sha256(path),
        "wall_seconds": time.perf_counter() - started,
        "peak_rss_bytes": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024,
    }
    search_run._write_json(root / "checkpoints" / f"{day}.json", record)
    return record


def run_exit_study(
    *,
    breadth_run_root: str | Path,
    refinement_run_root: str | Path,
    run_root: str | Path,
    workers: int = 4,
    dates: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Evaluate E0-E4 on the frozen entries, one account day at a time.

    Only days that actually carry a frozen entry are loaded; the entry stage is
    never re-scanned, so the study is a function of the two run roots.
    """
    from concurrent.futures import ProcessPoolExecutor, as_completed

    from trading_research.research.rule_discovery import search_run

    root = Path(run_root)
    root.mkdir(parents=True, exist_ok=True)
    fixed = freeze_entries(
        breadth_run_root=breadth_run_root,
        refinement_run_root=refinement_run_root,
        out_path=root / "FIXED_ENTRIES.json",
        dates=dates,
    )
    selected = list(dates) if dates else fixed["dates_with_entries"]
    todo = [
        day
        for day in selected
        if not (root / "checkpoints" / f"{day}.json").is_file()
    ]
    started = time.perf_counter()
    completed: list[str] = []
    failed: list[str] = []
    payload = {"run_root": str(root), "rules": fixed["rules"]}
    if workers <= 1:
        _init_exit_worker(payload)
        for day in todo:
            record = _process_exit_date(day)
            (completed if record["status"] == "completed" else failed).append(day)
    elif todo:
        with ProcessPoolExecutor(
            max_workers=int(workers), initializer=_init_exit_worker, initargs=(payload,)
        ) as pool:
            futures = {pool.submit(_process_exit_date, day): day for day in todo}
            for future in as_completed(futures):
                day = futures[future]
                try:
                    record = future.result()
                except Exception:
                    search_run._write_json(
                        root / "failed" / f"{day}.json",
                        {"date": day, "status": "failed", "error": traceback.format_exc()},
                    )
                    failed.append(day)
                    continue
                (completed if record["status"] == "completed" else failed).append(day)
    pending = [day for day in selected if not (root / "checkpoints" / f"{day}.json").is_file()]
    summary = {
        "task_id": P15_19_TASK_ID,
        "run_root": str(root),
        "dates_with_entries": len(selected),
        "dates_completed": len(selected) - len(pending),
        "dates_failed": sorted(set(failed)),
        "dates_pending": len(pending),
        "workers": int(workers),
        "wall_seconds": time.perf_counter() - started,
        "entries": fixed["entries"],
    }
    search_run._write_json(root / "PROGRESS.json", summary)
    if not pending:
        search_run._write_json(
            root / "RUN_COMPLETE.json",
            {
                "schema_version": "research-p15-19-run-complete-v1",
                "task_id": P15_19_TASK_ID,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "fixed_entries_sha256": search_run.file_sha256(root / "FIXED_ENTRIES.json"),
                "shards": len(selected),
                "summary": summary,
            },
        )
    return summary


def _fold_of(day: str, folds: Sequence[Mapping[str, Any]]) -> int | None:
    for fold in folds:
        if day in fold["_test_set"]:
            return int(fold["test_year"])
    return None


def exit_daily_series(shards: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Per rule, per policy, the daily net points and the completeness of each
    day, from the study's own shards.

    A day counts for a (policy, E0) pair only when every frozen entry of that
    rule on that day is complete under both: an incomplete exit or an
    unsupported E3/E4 keeps its entry in the ledger and takes the day out of the
    paired comparison instead of imputing a number.
    """
    out: dict[str, dict[str, Any]] = {}
    for shard in shards:
        day = str(shard["account_day"])
        for candidate_id, rows in (shard.get("rules") or {}).items():
            rule = out.setdefault(
                candidate_id,
                {
                    "daily": {},
                    "entries": 0,
                    "e0_mismatches": 0,
                    "unsupported": {policy: 0 for policy in POLICIES},
                    "incomplete": {policy: 0 for policy in POLICIES},
                    "occupancy_flagged": {policy: 0 for policy in POLICIES},
                    "reasons": {policy: {} for policy in POLICIES},
                },
            )
            totals = {policy: Decimal(0) for policy in POLICIES}
            complete = {policy: True for policy in POLICIES}
            usable = True
            for row in rows:
                rule["entries"] += 1
                if not row["e0_matches_entry_run"]:
                    rule["e0_mismatches"] += 1
                    usable = False
                for policy in POLICIES:
                    body = row["policies"][policy]
                    if body.get("occupancy_flagged"):
                        rule["occupancy_flagged"][policy] += 1
                    if body.get("reason") == "undefined_initial_r":
                        rule["unsupported"][policy] += 1
                        complete[policy] = False
                        continue
                    if not body.get("complete"):
                        rule["incomplete"][policy] += 1
                        complete[policy] = False
                        continue
                    totals[policy] += Decimal(str(body["net_points"]))
                    reason = str(body.get("reason"))
                    rule["reasons"][policy][reason] = rule["reasons"][policy].get(reason, 0) + 1
            rule["daily"][day] = {
                "usable": usable,
                "net_points": {policy: str(totals[policy]) for policy in POLICIES},
                "complete": {policy: complete[policy] for policy in POLICIES},
                "entries": len(rows),
            }
    return out


def evaluate_exit_study(
    *,
    run_root: str | Path,
    refinement_run_root: str | Path,
    freeze_path: str | Path,
    out_dir: str | Path | None = None,
    holdout: tuple[str, str] | None = None,
) -> dict[str, Any]:
    """EXIT_RESULTS.json, EXIT_TRIALS.jsonl and the family reports.

    Every comparison is against E0 on the same unchanged entries. The entry
    stage's dispositions are carried through untouched: this family counts its
    own trials and cannot promote or rescue an entry candidate.
    """
    import numpy as _np

    from trading_research.research.rule_discovery import refinement as _refinement
    from trading_research.research.rule_discovery import search_run

    root = Path(run_root)
    out = Path(out_dir) if out_dir else root
    out.mkdir(parents=True, exist_ok=True)
    fixed = json.loads((root / "FIXED_ENTRIES.json").read_text())
    freeze = search_run.load_freeze(freeze_path)
    trimmed, holdout_excluded = search_run.apply_holdout(search_run.load_splits(freeze), holdout)
    folds = [dict(fold, _test_set=set(fold["test"])) for fold in trimmed]
    entry_dispositions = _entry_dispositions(refinement_run_root)

    shards = []
    for day in fixed["dates_with_entries"]:
        path = root / "exits" / f"{day}.json"
        if path.is_file():
            shards.append(json.loads(path.read_text()))
    series = exit_daily_series(shards)

    rows: list[dict[str, Any]] = []
    for rule in fixed["rules"]:
        candidate_id = rule["candidate_id"]
        body = series.get(candidate_id)
        if body is None:
            continue
        for policy in POLICIES:
            if policy == "E0":
                continue
            diffs: list[float] = []
            days_in_order: list[str] = []
            per_block: dict[int, list[float]] = {}
            days = 0
            resolved = 0
            holdout_days = 0
            for day, cell in sorted(body["daily"].items()):
                if search_run.in_holdout(day, holdout):
                    # the blind hold-out chooses no exit policy
                    holdout_days += 1
                    continue
                if not cell["usable"] or not cell["complete"]["E0"] or not cell["complete"][policy]:
                    continue
                diff = float(Decimal(cell["net_points"][policy]) - Decimal(cell["net_points"]["E0"]))
                diffs.append(diff)
                days_in_order.append(day)
                days += 1
                resolved += int(cell["entries"])
                year = _fold_of(day, folds)
                if year is not None:
                    per_block.setdefault(year, []).append(diff)
            block_improvements = [float(_np.mean(values)) for _, values in sorted(per_block.items())]
            rows.append(
                {
                    "candidate_id": f"{candidate_id}|{policy}",
                    "entry_rule": candidate_id,
                    "policy": policy,
                    "family": rule["family"],
                    "branch": str(candidate_id).split(":")[1] if ":" in candidate_id else "",
                    "bank": "EXIT",
                    "recipe_id": policy,
                    "parameters": {"expiry_minutes": POLICY_EXPIRY_MINUTES[policy]},
                    "changed_axes": 1,
                    "daily_diff": diffs,
                    "daily_days": days_in_order,
                    "daily_segments": [day[:4] for day in days_in_order],
                    "mean_diff": float(_np.mean(diffs)) if diffs else 0.0,
                    "block_improvements": block_improvements,
                    "supported_outer_blocks": len(block_improvements),
                    "eligible_test_days": days,
                    "resolved_opportunities": resolved,
                    # the entry population is identical by construction, so the
                    # frequency floor cannot bite in this family
                    "candidate_entries": body["entries"],
                    "baseline_entries": body["entries"],
                    "software_causality_pass": body["e0_mismatches"] == 0,
                    "runtime_failures": 0,
                    "cost_stress_sign_reversal": False,
                    "unexplained_coverage_loss": False,
                    "coverage_loss_days": body["incomplete"][policy],
                    "missed_move": 0,
                    "stop_first": 0,
                    "nearest_approach_S": None,
                    "adverse_S_before_favorable_0_5S": None,
                    "objective_reached": None,
                    "unsupported_entries": body["unsupported"][policy],
                    "incomplete_entries": body["incomplete"][policy],
                    "occupancy_flagged_entries": body["occupancy_flagged"][policy],
                    "exit_reasons": body["reasons"][policy],
                    "e0_mismatches": body["e0_mismatches"],
                    "holdout_days_excluded": holdout_days,
                }
            )
    decided = search_run.decide(rows)
    for row in decided:
        entry = entry_dispositions.get(row["entry_rule"], {})
        row["entry_stage"] = {
            "disposition": entry.get("disposition"),
            "promoted": entry.get("promoted"),
            "trial_ids": entry.get("trial_ids", []),
            "unchanged_by_this_study": True,
        }
        # a separately counted decision family: an exit can improve a rule's
        # daily points and still not make its entry promotable
        row["entry_rescued"] = False

    ledger_path = out / "EXIT_TRIALS.jsonl"
    if ledger_path.exists():
        ledger_path.unlink()
    ledger = _refinement.TrialLedger(ledger_path)
    for row in decided:
        ledger.append(
            _refinement.make_trial_record(
                trial_id=f"P15-19:{row['entry_rule']}:{row['policy']}",
                parent_trial_ids=list(row["entry_stage"]["trial_ids"]),
                family=row["family"],
                branch=row["branch"],
                outer_fold=None,
                stage="exit_study",
                bank="EXIT",
                parameters=row["parameters"],
                code_hash=search_run.code_identity()["code_sha256"],
                data_hash=fixed.get("refinement_run_root"),
                plan_hash=search_run.file_sha256(freeze_path),
                candidate_population_counts={
                    "entries": row["candidate_entries"],
                    "eligible_days": row["eligible_test_days"],
                    "unsupported_entries": row["unsupported_entries"],
                    "incomplete_entries": row["incomplete_entries"],
                    "occupancy_flagged_entries": row["occupancy_flagged_entries"],
                },
                score=row["mean_diff"],
                support=row["promotion"]["support_sensitivity"],
                test_metrics={
                    "mean_diff": row["mean_diff"],
                    "p_raw": row["promotion"]["p_raw"],
                    "p_holm": row["promotion"]["p_holm"],
                    "ci_low": row["promotion"]["ci_low"],
                    "ci_high": row["promotion"]["ci_high"],
                    "exit_reasons": row["exit_reasons"],
                },
                reason=row["promotion"]["reason"],
                disposition=row["promotion"]["disposition"],
                artifacts={"run_root": str(root)},
                failure_attribution=row["failure_attribution"],
                candidate_id=row["candidate_id"],
                recipe_id=row["policy"],
                status="attempted",
                entry_stage_disposition=row["entry_stage"]["disposition"],
                entry_rescued=False,
                holdout_excluded=holdout_excluded,
            )
        )

    results = {
        "schema_version": EXIT_RESULTS_SCHEMA,
        "task_id": P15_19_TASK_ID,
        "run_root": str(root),
        "baseline_policy": "E0",
        "policies": list(POLICIES),
        "policy_expiry_minutes": dict(POLICY_EXPIRY_MINUTES),
        "uncertainty": freeze["uncertainty"],
        "promotion_gates": freeze["promotion_gates"],
        "decision_family": "exit study, counted separately from the entry stage",
        "holdout_excluded": holdout_excluded,
        "cannot_rescue_an_entry": True,
        "entries": fixed["entries"],
        "rules": fixed["rules"],
        "per_rule": {
            candidate_id: {
                "entries": body["entries"],
                "e0_mismatches": body["e0_mismatches"],
                "days": len(body["daily"]),
                "unsupported": body["unsupported"],
                "incomplete": body["incomplete"],
                "occupancy_flagged": body["occupancy_flagged"],
                "exit_reasons": body["reasons"],
            }
            for candidate_id, body in sorted(series.items())
        },
        "comparisons": [
            {
                key: value
                for key, value in row.items()
                if key not in ("daily_diff", "daily_days", "daily_segments")
            }
            for row in decided
        ],
    }
    search_run._write_json(out / "EXIT_RESULTS.json", results)

    reports = out / "FAMILY_REPORTS"
    reports.mkdir(parents=True, exist_ok=True)
    retention = [
        {
            "candidate_id": row["candidate_id"],
            "family": row["family"],
            "branch": row["branch"],
            "bank": "EXIT",
            "status": "active_selected" if row["promotion"]["promoted"] else "inactive_retained",
            "first_attribution": (row["failure_attribution"] or [None])[0],
            "reason": row["promotion"]["reason"],
        }
        for row in decided
    ]
    for family in sorted({row["family"] for row in decided}):
        text = search_run.family_report(
            family,
            decided,
            retention,
            [],
            run_root=str(root),
            report_path=str(reports / f"{family}.md"),
            title="P15-19 exit study (E0 baseline)",
            results_file="EXIT_RESULTS.json",
        )
        (reports / f"{family}.md").write_text(text)

    return {
        "comparisons": len(decided),
        "promoted": [row["candidate_id"] for row in decided if row["promotion"]["promoted"]],
        "e0_mismatches": sum(body["e0_mismatches"] for body in series.values()),
        "family_reports": sorted(path.name for path in reports.glob("*.md")),
    }


def _entry_dispositions(refinement_run_root: str | Path) -> dict[str, dict[str, Any]]:
    """The entry stage's own verdicts, read once and never rewritten here."""
    root = Path(refinement_run_root)
    out: dict[str, dict[str, Any]] = {}
    rules = json.loads((root / "SELECTED_RULES_BY_FOLD.json").read_text())
    for fold in rules["folds"]:
        year = fold["outer_fold"]
        for role in fold["roles"]:
            row = out.setdefault(
                str(role["candidate_id"]),
                {"disposition": role.get("disposition"), "promoted": bool(role.get("promoted")), "trial_ids": []},
            )
            row["trial_ids"].append(f"P15-18:{year}:{role['candidate_id']}")
            if role.get("role") == "retained_parent":
                # the fold kept the breadth parent, so the parent's own entries
                # are the frozen ones and its trials are the breadth trials
                for parent in role.get("parent_trial_ids") or []:
                    parent_row = out.setdefault(
                        str(parent),
                        {"disposition": "retained_baseline", "promoted": False, "trial_ids": []},
                    )
                    trial = f"P15-17:{year}:{parent}"
                    if trial not in parent_row["trial_ids"]:
                        parent_row["trial_ids"].append(trial)
        for candidate_id in fold.get("combinations") or []:
            row = out.setdefault(
                str(candidate_id),
                {"disposition": None, "promoted": False, "trial_ids": []},
            )
            trial = f"P15-18:{year}:{candidate_id}"
            if trial not in row["trial_ids"]:
                row["trial_ids"].append(trial)
    # every exit trial must name the entry trial it descends from
    ledger = root / "TRIALS.jsonl"
    if ledger.is_file():
        for line in ledger.read_text().splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            row = out.setdefault(
                str(record["candidate_id"]),
                {"disposition": record.get("disposition"), "promoted": False, "trial_ids": []},
            )
            if record["trial_id"] not in row["trial_ids"]:
                row["trial_ids"].append(record["trial_id"])
    return out
