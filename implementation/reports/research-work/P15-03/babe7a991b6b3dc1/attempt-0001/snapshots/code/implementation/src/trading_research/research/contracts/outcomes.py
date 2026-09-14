"""Causal scale, descriptive excursions and ordered first-passage labels."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Mapping

from trading_research.errors import ContractError
from trading_research.research.contracts.types import Coverage, CoverageReceipt, NativeBatch

TICK = Decimal("0.25")
MINUTE_NS = 60_000_000_000
HORIZONS_MINUTES = (5, 15, 30, 60, 120)
STOP_MULT = (Decimal("0.25"), Decimal("0.50"), Decimal("1"))
TARGET_MULT = (Decimal("0.50"), Decimal("1"), Decimal("2"))
PASSAGE_RESULTS = frozenset({
    "target_first",
    "stop_first",
    "neither",
    "same_batch_ambiguous",
    "prior_gap_unknown",
    "missing_future",
    "invalid_geometry",
})


@dataclass(frozen=True, slots=True)
class PriceBatch:
    event_ns: int
    available_at_ns: int
    prices: tuple[Decimal, ...]
    event_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PassageResult:
    result: str
    resolved_at_ns: int | None
    available_at_ns: int | None
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.result not in PASSAGE_RESULTS:
            raise ContractError(f"unknown passage result {self.result}")


def causal_scale(high: Decimal | None, low: Decimal | None, *, matching_minutes: int, complete: bool) -> Decimal | None:
    if not complete or matching_minutes < 60 or high is None or low is None:
        return None
    width = high - low
    floor = 4 * TICK
    return width if width > floor else floor


def excursions(prices: Iterable[Decimal], *, side: int, reference: Decimal) -> dict[str, Decimal]:
    if side not in (-1, 1):
        raise ContractError("side must be -1 or 1")
    favorable = Decimal(0)
    adverse = Decimal(0)
    for price in prices:
        move = Decimal(side) * (price - reference)
        if move > favorable:
            favorable = move
        opp = -move
        if opp > adverse:
            adverse = opp
    return {
        "mfe_points": max(Decimal(0), favorable),
        "mae_points": max(Decimal(0), adverse),
    }


def _batches_from_native(batches: Iterable[NativeBatch]) -> list[PriceBatch]:
    rows = []
    for batch in batches:
        rows.append(
            PriceBatch(
                event_ns=batch.event_ns,
                available_at_ns=batch.available_at_ns,
                prices=tuple(trade.price for trade in batch.trades),
                event_ids=tuple(trade.event_id for trade in batch.trades),
            )
        )
    return rows


def _gap_before(unknown: Iterable[tuple[int, int]], start_ns: int, at_ns: int) -> bool:
    for lo, hi in unknown:
        if hi <= start_ns or lo >= at_ns:
            continue
        if hi > start_ns and lo < at_ns:
            return True
    return False


def first_passage(
    events: Iterable[PriceBatch | NativeBatch] | Iterable[Mapping[str, object]],
    *,
    start_ns: int,
    end_ns: int,
    side: int,
    entry: Decimal,
    stop: Decimal,
    target: Decimal,
    coverage: CoverageReceipt | Mapping[str, object] | None = None,
) -> PassageResult:
    if side not in (-1, 1):
        raise ContractError("side must be -1 or 1")
    if side * (entry - stop) <= 0 or side * (target - entry) <= 0:
        return PassageResult("invalid_geometry", None, None, ())
    unknown: tuple[tuple[int, int], ...] = ()
    complete = True
    if isinstance(coverage, CoverageReceipt):
        unknown = coverage.missing_intervals
        complete = coverage.status == Coverage.COMPLETE
    elif isinstance(coverage, Mapping):
        raw = coverage.get("unknown_intervals") or coverage.get("missing_intervals") or ()
        unknown = tuple((int(a), int(b)) for a, b in raw)
        status = coverage.get("status") or coverage.get("observed_scope_complete")
        if status in (False, Coverage.PARTIAL, Coverage.MISSING, "partial", "missing"):
            complete = False
        if coverage.get("observed_scope_complete") is False:
            complete = False
    rows: list[PriceBatch] = []
    for item in events:
        if isinstance(item, NativeBatch):
            rows.extend(_batches_from_native((item,)))
        elif isinstance(item, PriceBatch):
            rows.append(item)
        else:
            prices = item.get("prices")  # type: ignore[assignment]
            rows.append(
                PriceBatch(
                    event_ns=int(item["event_ns"]),  # type: ignore[index]
                    available_at_ns=int(item.get("available_at_ns") or item["event_ns"]),  # type: ignore[index]
                    prices=tuple(Decimal(str(p)) for p in prices),  # type: ignore[arg-type]
                    event_ids=tuple(str(x) for x in (item.get("event_ids") or ())),  # type: ignore[union-attr]
                )
            )
    rows.sort(key=lambda row: row.event_ns)
    if end_ns <= start_ns:
        return PassageResult("missing_future", None, None, ())
    for row in rows:
        if row.event_ns <= start_ns or row.event_ns > end_ns:
            continue
        hits_target = any(side * (price - target) >= 0 for price in row.prices)
        hits_stop = any(side * (price - stop) <= 0 for price in row.prices)
        if not hits_target and not hits_stop:
            continue
        if _gap_before(unknown, start_ns, row.event_ns):
            return PassageResult("prior_gap_unknown", row.event_ns, row.available_at_ns, row.event_ids)
        if hits_target and hits_stop:
            return PassageResult("same_batch_ambiguous", row.event_ns, row.available_at_ns, row.event_ids)
        if hits_target:
            return PassageResult("target_first", row.event_ns, row.available_at_ns, row.event_ids)
        return PassageResult("stop_first", row.event_ns, row.available_at_ns, row.event_ids)
    if not complete:
        return PassageResult("missing_future", None, None, ())
    return PassageResult("neither", None, None, ())


def interval_extrema(
    events: Iterable[PriceBatch | NativeBatch] | Iterable[Mapping[str, object]],
    *,
    start_ns: int,
    end_ns: int,
) -> dict[str, Decimal | int | None | str]:
    """Native interval extrema on the contract convention (t, t+h]."""
    rows: list[PriceBatch] = []
    for item in events:
        if isinstance(item, NativeBatch):
            rows.extend(_batches_from_native((item,)))
        elif isinstance(item, PriceBatch):
            rows.append(item)
        else:
            prices = item.get("prices")  # type: ignore[assignment]
            rows.append(
                PriceBatch(
                    event_ns=int(item["event_ns"]),  # type: ignore[index]
                    available_at_ns=int(item.get("available_at_ns") or item["event_ns"]),  # type: ignore[index]
                    prices=tuple(Decimal(str(p)) for p in prices),  # type: ignore[arg-type]
                    event_ids=tuple(str(x) for x in (item.get("event_ids") or ())),  # type: ignore[union-attr]
                )
            )
    high: Decimal | None = None
    low: Decimal | None = None
    high_at: int | None = None
    low_at: int | None = None
    for row in rows:
        if row.event_ns <= start_ns or row.event_ns > end_ns:
            continue
        for price in row.prices:
            if high is None or price > high:
                high = price
                high_at = row.event_ns
            if low is None or price < low:
                low = price
                low_at = row.event_ns
    return {
        "high": high,
        "low": low,
        "high_at_ns": high_at,
        "low_at_ns": low_at,
        "convention": "(t, t+h]",
    }


def ordered_grid(
    events: Iterable[PriceBatch],
    *,
    start_ns: int,
    side: int,
    entry: Decimal,
    scale: Decimal,
    account_end_ns: int,
    coverage: CoverageReceipt | Mapping[str, object] | None = None,
) -> dict[str, PassageResult]:
    grid = {}
    horizons = list(HORIZONS_MINUTES) + ["account"]
    for stop_m in STOP_MULT:
        for target_m in TARGET_MULT:
            stop = entry - Decimal(side) * stop_m * scale
            target = entry + Decimal(side) * target_m * scale
            for horizon in horizons:
                end_ns = account_end_ns if horizon == "account" else start_ns + int(horizon) * MINUTE_NS
                key = f"stop_{stop_m}_target_{target_m}_h_{horizon}"
                grid[key] = first_passage(
                    events,
                    start_ns=start_ns,
                    end_ns=end_ns,
                    side=side,
                    entry=entry,
                    stop=stop,
                    target=target,
                    coverage=coverage,
                )
    return grid
