"""Finite raw-receipt oracle; never calls the incremental ledger or reducers."""
from dataclasses import dataclass
from fractions import Fraction

from trading_research.data.transactions import ResolvedTransaction, TransactionReceipt
from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest


@dataclass(frozen=True)
class LiteralState:
    live: tuple[ResolvedTransaction, ...]
    pending: tuple[str, ...]
    receipts_examined: int
    links_examined: int


def replay(receipts: tuple[tuple[TransactionReceipt, int], ...], *, cut: int, max_receipts=4096):
    timestamp(cut)
    if not isinstance(receipts, tuple) or type(max_receipts) is not int or max_receipts <= 0 or len(receipts) > max_receipts:
        raise ContractError('literal raw receipt replay requires a finite registered input')
    seen, versions, completions, successors, roots = {}, {}, {}, {}, {}
    previous_input = previous_completion = None
    examined = links = 0
    for receipt, completed in receipts:
        timestamp(completed)
        if not isinstance(receipt, TransactionReceipt):
            raise ContractError('literal oracle needs immutable receipts')
        if completed > cut:
            continue
        examined += 1
        if receipt.receipt_id in seen:
            if seen[receipt.receipt_id] != receipt:
                raise IntegrityError('literal conflicting physical receipt')
            continue
        if (completed < receipt.clocks.known_at or previous_input is not None and receipt.clocks.known_at < previous_input
                or previous_completion is not None and completed < previous_completion):
            raise ContractError('literal receipt availability/completion regressed')
        previous_input, previous_completion = receipt.clocks.known_at, completed
        seen[receipt.receipt_id] = receipt
        if receipt.version_id in versions:
            if versions[receipt.version_id].business_record() != receipt.business_record():
                raise IntegrityError('literal conflicting transaction revision')
            continue
        versions[receipt.version_id] = receipt
        completions[receipt.version_id] = completed
        root = receipt.root_key.id
        if receipt.operation == 'insert':
            if root in roots:
                raise IntegrityError('literal second insertion')
            roots[root] = receipt.version_id
        else:
            predecessor = receipt.predecessor_version_id
            if predecessor in successors:
                raise IntegrityError('literal forked transaction')
            successors[predecessor] = receipt.version_id
    for id, receipt in versions.items():
        visited, cursor = set(), id
        while cursor in versions:
            links += 1
            if cursor in visited:
                raise ContractError('literal cyclic correction chain')
            visited.add(cursor)
            row = versions[cursor]
            if row.root_key != receipt.root_key:
                raise ContractError('literal cross-root correction')
            if cursor != id and row.operation == 'cancel':
                raise ContractError('literal revision after terminal cancel')
            cursor = row.predecessor_version_id
        if receipt.value is not None:
            same = [r.value for r in versions.values() if r.root_key == receipt.root_key and r.value is not None]
            if any(value.unit_identity != receipt.value.unit_identity for value in same):
                raise ContractError('literal correction changes units')
    reached, live = set(), []
    for root, initial in sorted(roots.items()):
        chain, cursor = [], initial
        while cursor in versions:
            links += 1
            chain.append(cursor); reached.add(cursor)
            cursor = successors.get(cursor)
        final = versions[chain[-1]]
        if final.value is not None:
            live.append(ResolvedTransaction(final.root_key, final.version_id, digest(final.business_record()),
                                            final.value, max(completions[id] for id in chain)))
    return LiteralState(tuple(live), tuple(sorted(set(versions) - reached)), examined, links)


def aggregate(state: LiteralState, *, instrument: str, cut: int, row_ticks=1, grid_origin=0,
              start=None, end=None, coverage_complete=True, money_role='synthetic_notional_USD'):
    """Full sums over the final raw graph, independent of before/after algebra."""
    timestamp(cut)
    if type(row_ticks) is not int or row_ticks <= 0 or type(grid_origin) is not int:
        raise ContractError('literal profile grid is invalid')
    values = [r for r in state.live if r.root_key.instrument_key == instrument and r.known_at <= cut
              and (start is None or r.value.event_at >= start) and (end is None or r.value.event_at < end)]
    eligible = [r.value for r in values if r.value.volume_eligibility is True]
    buy = sum(v.quantity for v in eligible if v.directional_eligibility and v.reported_aggressor == 1)
    sell = sum(v.quantity for v in eligible if v.directional_eligibility and v.reported_aggressor == -1)
    unknown = sum(v.quantity for v in eligible if not v.directional_eligibility or v.reported_aggressor is None)
    unknown_conditions = sum(r.value.quantity for r in values if r.value.volume_eligibility is None)
    rows = {}
    for v in eligible:
        if v.price_ticks is not None:
            row = grid_origin + ((v.price_ticks - grid_origin) // row_ticks) * row_ticks
            cells = rows.setdefault(row, [0, 0, 0])
            channel = 0 if v.directional_eligibility and v.reported_aggressor == 1 else 1 if v.directional_eligibility and v.reported_aggressor == -1 else 2
            cells[channel] += v.quantity
    priced_ticks = [v for v in eligible if v.price_ticks is not None]
    mass = sum(v.quantity for v in priced_ticks)
    first = sum(v.price_ticks * v.quantity for v in priced_ticks)
    second = sum(v.price_ticks * v.price_ticks * v.quantity for v in priced_ticks)
    priced_money = [v for v in eligible if v.price_decimal is not None and v.usd_multiplier is not None]
    if any(v.money_role != money_role for v in priced_money):
        raise ContractError('literal money role mismatch')
    money = sum((Fraction(v.price_decimal) * Fraction(v.usd_multiplier) * v.quantity for v in priced_money), Fraction())
    signed_money = sum((Fraction(v.price_decimal) * Fraction(v.usd_multiplier) * v.quantity *
                        (v.reported_aggressor if v.directional_eligibility and v.reported_aggressor is not None else 0)
                        for v in priced_money), Fraction())
    complete = coverage_complete and not unknown_conditions and all(v.history_complete for v in eligible)
    return {'live_versions': tuple(sorted(r.version_id for r in values)), 'buy': buy, 'sell': sell, 'unknown': unknown,
            'total': buy + sell + unknown, 'signed': buy - sell, 'prints': len(eligible),
            'observed_volume': sum(r.value.quantity for r in values),
            'excluded_volume': sum(r.value.quantity for r in values if r.value.volume_eligibility is False),
            'condition_unresolved_volume': unknown_conditions,
            'profile_unpriced_volume': sum(v.quantity for v in eligible if v.price_ticks is None),
            'money_unpriced_volume': sum(v.quantity for v in eligible if v.price_decimal is None or v.usd_multiplier is None),
            'profile': tuple((p, *cells) for p, cells in sorted(rows.items())),
            'tick_mass': mass, 'tick_first': first, 'tick_second': second,
            'vwap': Fraction(first, mass) if mass else None,
            'variance': Fraction(second, mass) - Fraction(first, mass) ** 2 if mass else None,
            'notional': money if money_role else None, 'signed_notional': signed_money if money_role else None,
            'signed_bounds': (buy - sell - unknown, buy - sell + unknown) if complete else None,
            'complete_history': complete, 'values_summed': len(values)}
