"""TPO visits and explicitly estimated dwell; neither is traded volume."""

from collections import defaultdict
from dataclasses import dataclass

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.bars import Watermark, WindowCoverage
from trading_research.measurements.tape import RowGrid, TradeView


@dataclass(frozen=True)
class TPO:
    visits: tuple[tuple[int, tuple[int, ...]], ...]
    bracket_opportunities: int
    provisional_single_rows: tuple[int, ...]
    confirmed_single_rows: tuple[int, ...]
    final: bool
    complete_coverage: bool
    definition_version: str

    @property
    def histogram(self):
        return {row:len(brackets) for row, brackets in self.visits}


def tpo_reference(ledger: TradeView, *, instrument: str, start: int, end: int, cut: int,
                  bracket_ns: int, grid: RowGrid, coverage: WindowCoverage, definition_version: str,
                  minimum_brackets: int, watermark: Watermark | None = None) -> TPO:
    if (type(bracket_ns) is not int or bracket_ns <= 0 or type(minimum_brackets) is not int or minimum_brackets <= 0
            or start >= end or cut < start or not definition_version):
        raise ContractError("TPO needs frozen bracket/grid, anchor and confirmation rules")
    if (coverage.instrument, coverage.start, coverage.end) != (instrument, start, end) or coverage.known_at > cut:
        raise DependencyUnavailable("TPO lacks matching available coverage")
    trades = ledger.asof(instrument=instrument, start=start, end=min(end, cut + 1), cut=cut)
    visits = defaultdict(set)
    for t in trades:
        if t.price is not None:
            visits[grid.row(t.price)].add((t.event_at - start) // bracket_ns)
    opportunities = (min(end, cut + 1) - start + bracket_ns - 1) // bracket_ns
    final = watermark is not None and watermark.known_at <= cut and watermark.through_event_at >= end
    complete = coverage.complete and all(t.history_complete and t.price is not None for t in trades)
    singles = tuple(sorted(row for row, brackets in visits.items() if len(brackets) == 1))
    return TPO(tuple((row, tuple(sorted(brackets))) for row, brackets in sorted(visits.items())), opportunities,
               singles, singles if final and complete and opportunities >= minimum_brackets else (), final, complete, definition_version)


@dataclass(frozen=True)
class DwellEstimate:
    duration_by_row: tuple[tuple[int, int], ...]
    covered_duration_ns: int
    missing_or_stale_duration_ns: int
    uncertain_order_duration_ns: int
    method: str = "last_observed_trade_price_with_explicit_stale_cap"


def bounded_dwell(ledger: TradeView, *, instrument: str, start: int, end: int, cut: int,
                  stale_cap_ns: int, grid: RowGrid) -> DwellEstimate:
    if start >= end or cut < end or type(stale_cap_ns) is not int or stale_cap_ns <= 0:
        raise ContractError("dwell estimate needs an elapsed interval and explicit maximum carry duration")
    trades = ledger.asof(instrument=instrument, start=start, end=end, cut=cut)
    groups = defaultdict(list)
    for t in trades:
        groups[t.event_at].append(t)
    times, durations, ambiguous = sorted(groups), defaultdict(int), 0
    for n, at in enumerate(times):
        batch = groups[at]
        until = min(end, times[n + 1] if n + 1 < len(times) else end, at + stale_cap_ns)
        ordered = len(batch) == 1 or (all(t.order is not None for t in batch) and len({t.order for t in batch}) == len(batch))
        if ordered:
            price = max(batch, key=lambda t: t.order or 0).price
        elif len({t.price for t in batch}) == 1:
            price = batch[0].price
        else:
            ambiguous += until - at
            continue
        if price is not None and all(t.history_complete for t in batch):
            durations[grid.row(price)] += until - at
    covered = sum(durations.values())
    return DwellEstimate(tuple(sorted(durations.items())), covered, end - start - covered, ambiguous)
