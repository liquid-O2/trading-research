"""Fixed-entry exit policies E0-E4. Owned by P15-19. Does not edit execution.py."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, Sequence
import bisect
import gzip
import json

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
