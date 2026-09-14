"""One-mini BBO/latency/cost/risk benchmark. Isolated from scanners."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Iterable, Mapping, Sequence

from trading_research.errors import ContractError
from trading_research.research.contracts.outcomes import PassageResult, first_passage
from trading_research.research.contracts.types import QuoteBatch

TICK = Decimal("0.25")
POINT_VALUE = Decimal("20")
COMMISSION_SIDE = Decimal("2.50")
LATENCY_NS = 250_000_000
MAX_QUOTE_AGE_NS = 1_000_000_000
ENTRY_WINDOW_NS = 5_000_000_000
DAY_LOSS_LIMIT = Decimal("1000")
STRESS_LATENCY_NS = 500_000_000
STRESS_TICKS = 2
STRESS_COMMISSION = Decimal("3.50")


@dataclass(frozen=True, slots=True)
class Fill:
    opportunity_id: str
    side: int
    decision_at_ns: int
    fill_at_ns: int
    price: Decimal
    quantity: int
    commission: Decimal
    kind: str
    quote_event_ns: int | None


@dataclass
class DayReplay:
    account_day: str
    fills: list[Fill] = field(default_factory=list)
    occupied: list[dict[str, Any]] = field(default_factory=list)
    skipped: list[dict[str, Any]] = field(default_factory=list)
    realized_dollars: Decimal = Decimal(0)
    marked_dollars: Decimal = Decimal(0)
    risk_stop: bool = False
    gap_breach: bool = False
    zero_entry: bool = True
    complete: bool = True
    unsupported_fills: list[str] = field(default_factory=list)


def _quote_usable(quote: QuoteBatch, *, at_ns: int, max_age_ns: int = MAX_QUOTE_AGE_NS) -> bool:
    if quote.ambiguous:
        return False
    if quote.bid is None or quote.ask is None:
        return False
    if quote.ask < quote.bid:
        return False
    if (quote.bid_size or 0) <= 0 or (quote.ask_size or 0) <= 0:
        return False
    if quote.available_at_ns > at_ns:
        return False
    if at_ns - quote.event_ns > max_age_ns:
        return False
    return True


def _fill_price(quote: QuoteBatch, side: int, *, ticks: int) -> Decimal:
    slip = TICK * ticks
    if side == 1:
        return quote.ask + slip  # type: ignore[operator]
    return quote.bid - slip  # type: ignore[operator]


def net_points(*, side: int, entry: Decimal, exit_price: Decimal, commission: Decimal) -> Decimal:
    delta = (exit_price - entry) if side == 1 else (entry - exit_price)
    return delta - commission / POINT_VALUE


def net_dollars(*, side: int, entry: Decimal, exit_price: Decimal, commission: Decimal) -> Decimal:
    return net_points(side=side, entry=entry, exit_price=exit_price, commission=commission) * POINT_VALUE


def select_quote(quotes: Sequence[QuoteBatch], *, after_ns: int, deadline_ns: int) -> QuoteBatch | None:
    chosen = None
    for quote in quotes:
        if quote.available_at_ns < after_ns:
            continue
        if quote.available_at_ns > deadline_ns:
            break
        if _quote_usable(quote, at_ns=quote.available_at_ns):
            chosen = quote
            break
    return chosen


def replay_family(
    opportunities: Sequence[Mapping[str, Any]],
    quotes: Sequence[QuoteBatch],
    *,
    account_day: str,
    policy: Mapping[str, Any] | None = None,
) -> DayReplay:
    cfg = {
        "latency_ns": LATENCY_NS,
        "ticks": 1,
        "commission_side": COMMISSION_SIDE,
        "day_loss_limit": DAY_LOSS_LIMIT,
        "flatten_deadline_ns": None,
    }
    if policy:
        cfg.update(policy)
    replay = DayReplay(account_day=account_day)
    open_fill: Fill | None = None
    open_stop: Decimal | None = None
    open_target: Decimal | None = None
    day_start = Decimal(0)
    ordered = sorted(
        opportunities,
        key=lambda item: (int(item["decision_at_ns"]), str(item.get("reference_id") or ""), str(item["opportunity_id"])),
    )
    seen: set[tuple[str, str, str]] = set()
    for item in ordered:
        oid = str(item["opportunity_id"])
        key = (str(item.get("rule_id") or ""), str(item.get("reference_id") or ""), str(item.get("contact_id") or oid))
        side = int(item["side"])
        if key in seen:
            replay.skipped.append({"opportunity_id": oid, "reason": "duplicate_contact"})
            continue
        seen.add(key)
        if replay.risk_stop:
            replay.skipped.append({"opportunity_id": oid, "reason": "day_risk_stop"})
            continue
        if open_fill is not None:
            replay.occupied.append({"opportunity_id": oid, "open": open_fill.opportunity_id})
            continue
        decision = int(item["decision_at_ns"])
        after = decision + int(cfg["latency_ns"])
        quote = select_quote(quotes, after_ns=after, deadline_ns=after + ENTRY_WINDOW_NS)
        if quote is None:
            replay.skipped.append({"opportunity_id": oid, "reason": "no_quote"})
            replay.unsupported_fills.append(oid)
            continue
        entry = _fill_price(quote, side, ticks=int(cfg["ticks"]))
        stop = item.get("stop")
        target = item.get("target")
        if stop is not None and target is not None:
            stop_d, target_d = Decimal(str(stop)), Decimal(str(target))
            if side * (entry - stop_d) <= 0 or side * (target_d - entry) <= 0:
                replay.skipped.append({"opportunity_id": oid, "reason": "geometry_invalid_after_latency"})
                continue
            remaining = cfg["day_loss_limit"] + (replay.realized_dollars - day_start)
            stop_risk = abs(entry - stop_d) * POINT_VALUE + Decimal("2") * cfg["commission_side"]
            if stop_risk > remaining:
                replay.skipped.append({"opportunity_id": oid, "reason": "remaining_loss_budget"})
                continue
            open_stop, open_target = stop_d, target_d
        commission = cfg["commission_side"]
        open_fill = Fill(
            opportunity_id=oid,
            side=side,
            decision_at_ns=decision,
            fill_at_ns=quote.available_at_ns,
            price=entry,
            quantity=1,
            commission=commission,
            kind="entry",
            quote_event_ns=quote.event_ns,
        )
        replay.fills.append(open_fill)
        replay.zero_entry = False
        exit_fill = _maybe_exit(
            quotes,
            open_fill=open_fill,
            stop=open_stop,
            target=open_target,
            latency_ns=int(cfg["latency_ns"]),
            ticks=int(cfg["ticks"]),
            commission_side=cfg["commission_side"],
            flatten_deadline_ns=cfg["flatten_deadline_ns"],
        )
        if exit_fill is None:
            replay.complete = False
            replay.unsupported_fills.append(oid)
            open_fill = None
            continue
        replay.fills.append(exit_fill)
        pnl = net_dollars(side=open_fill.side, entry=open_fill.price, exit_price=exit_fill.price, commission=open_fill.commission + exit_fill.commission)
        replay.realized_dollars += pnl
        replay.marked_dollars = replay.realized_dollars
        if pnl < -cfg["day_loss_limit"] or replay.realized_dollars - day_start <= -cfg["day_loss_limit"]:
            if pnl < -cfg["day_loss_limit"]:
                replay.gap_breach = True
            replay.risk_stop = True
        open_fill = None
        open_stop = None
        open_target = None
    if not replay.fills:
        replay.zero_entry = True
    return replay


def replay_calendar(days: Sequence[Mapping[str, Any]]) -> list[DayReplay]:
    """Daily series: complete zero-entry days stay; missing days are omitted."""
    series: list[DayReplay] = []
    for item in days:
        if item.get("missing"):
            continue
        series.append(
            replay_family(
                item.get("opportunities") or (),
                item.get("quotes") or (),
                account_day=str(item["account_day"]),
                policy=item.get("policy"),
            )
        )
    return series


def _maybe_exit(
    quotes: Sequence[QuoteBatch],
    *,
    open_fill: Fill,
    stop: Decimal | None,
    target: Decimal | None,
    latency_ns: int,
    ticks: int,
    commission_side: Decimal,
    flatten_deadline_ns: int | None,
) -> Fill | None:
    side = open_fill.side
    trigger_ns = None
    reason = "expiry"
    for quote in quotes:
        if quote.available_at_ns <= open_fill.fill_at_ns:
            continue
        if not _quote_usable(quote, at_ns=quote.available_at_ns):
            continue
        px = quote.bid if side == 1 else quote.ask
        if px is None:
            continue
        hit_stop = stop is not None and side * (px - stop) <= 0
        hit_target = target is not None and side * (px - target) >= 0
        if hit_stop and hit_target:
            trigger_ns = quote.available_at_ns
            reason = "ambiguous_stop_target"
            break
        if hit_stop:
            trigger_ns = quote.available_at_ns
            reason = "stop"
            break
        if hit_target:
            trigger_ns = quote.available_at_ns
            reason = "target"
            break
        if flatten_deadline_ns is not None and quote.available_at_ns >= flatten_deadline_ns:
            trigger_ns = quote.available_at_ns
            reason = "flatten"
            break
    if trigger_ns is None and flatten_deadline_ns is not None:
        trigger_ns = flatten_deadline_ns
        reason = "flatten"
    if trigger_ns is None:
        return None
    after = trigger_ns + latency_ns
    quote = select_quote(quotes, after_ns=after, deadline_ns=after + ENTRY_WINDOW_NS)
    if quote is None:
        return None
    if side == 1:
        price = quote.bid - TICK * ticks  # type: ignore[operator]
    else:
        price = quote.ask + TICK * ticks  # type: ignore[operator]
    return Fill(
        opportunity_id=open_fill.opportunity_id,
        side=side,
        decision_at_ns=open_fill.decision_at_ns,
        fill_at_ns=quote.available_at_ns,
        price=price,
        quantity=1,
        commission=commission_side,
        kind=reason,
        quote_event_ns=quote.event_ns,
    )


def worked_net_pnl_fixture() -> dict[str, Any]:
    entry = Decimal("100.25")
    exit_price = Decimal("101.75")
    commission = Decimal("5.00")
    dollars = net_dollars(side=1, entry=entry, exit_price=exit_price, commission=commission)
    points = net_points(side=1, entry=entry, exit_price=exit_price, commission=commission)
    return {
        "entry": str(entry),
        "exit": str(exit_price),
        "commission": str(commission),
        "net_dollars": str(dollars),
        "net_points": str(points),
        "expected_dollars": "25.00",
        "expected_points": "1.25",
        "match": dollars == Decimal("25.00") and points == Decimal("1.25"),
    }


def gap_loss_not_clipped() -> dict[str, Any]:
    dollars = net_dollars(side=1, entry=Decimal("100.00"), exit_price=Decimal("40.00"), commission=Decimal("5.00"))
    return {"dollars": str(dollars), "clipped": dollars == -DAY_LOSS_LIMIT, "below_limit": dollars < -DAY_LOSS_LIMIT}
