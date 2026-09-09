"""Shared exact correction algebra for flow, profile and money; finite adapters."""
from dataclasses import asdict, dataclass, replace
from decimal import Decimal
from fractions import Fraction
import json
from types import MappingProxyType

from trading_research.data.transactions import SCHEMA, ResolvedTransaction, TransactionDelta, TransactionLedger
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.foundations.units import Ticks
from trading_research.measurements.tape import Trade
from trading_research.operations.artifacts import canonical_json, digest


@dataclass(frozen=True)
class TransactionSnapshot:
    instrument: str
    cut: int
    definition_version: str
    configuration_hash: str
    configuration: tuple[tuple[str, object], ...]
    delta_ids: tuple[str, ...]
    live_versions: tuple[str, ...]
    buy: int
    sell: int
    unknown: int
    total: int
    prints: int
    observed_volume: int
    excluded_volume: int
    condition_unresolved_volume: int
    profile_unpriced_volume: int
    money_unpriced_volume: int
    profile: tuple[tuple[int, int, int, int], ...]
    tick_mass: int
    tick_first: int
    tick_second: int
    notional: Fraction | None
    signed_notional: Fraction | None
    unknown_notional: Fraction | None
    money_role: str | None
    complete_history: bool

    @property
    def signed(self):
        return self.buy - self.sell

    @property
    def signed_bounds(self):
        return (self.signed - self.unknown, self.signed + self.unknown) if self.complete_history else None

    @property
    def certified_total(self):
        return self.total if self.complete_history else None

    @property
    def vwap(self):
        return Fraction(self.tick_first, self.tick_mass) if self.tick_mass else None

    @property
    def variance(self):
        return Fraction(self.tick_second, self.tick_mass) - self.vwap ** 2 if self.tick_mass else None

    @property
    def id(self):
        return digest(asdict(self))


def _zero():
    return {'buy': 0, 'sell': 0, 'unknown': 0, 'total': 0, 'prints': 0, 'observed_volume': 0,
            'excluded_volume': 0, 'condition_unresolved_volume': 0, 'profile_unpriced_volume': 0,
            'money_unpriced_volume': 0, 'tick_mass': 0, 'tick_first': 0, 'tick_second': 0,
            'notional': Fraction(), 'signed_notional': Fraction(), 'unknown_notional': Fraction(),
            'incomplete_count': 0}


class TransactionReducer:
    """One declared instrument/anchor/unit state, with bounded retained lineage."""
    def __init__(self, *, instrument: str, instrument_kind: str, quantity_unit: str,
                 terms_version: str, aggregation_unit: str, usd_multiplier: Decimal | None,
                 money_role: str | None, row_ticks=1, grid_origin=0, start=None, end=None,
                 coverage_complete=True, definition_version=SCHEMA, max_records=4096,
                 max_bytes=8 * 1024**2, max_profile_rows=512, max_snapshot_versions=128):
        if any(not isinstance(v, str) or not v for v in (instrument, instrument_kind, quantity_unit,
                                                        terms_version, aggregation_unit, definition_version)):
            raise ContractError('reducer needs explicit instrument/units/definition')
        if any(type(v) is not int or v <= 0 for v in (row_ticks, max_records, max_bytes, max_profile_rows, max_snapshot_versions)) or type(grid_origin) is not int:
            raise ContractError('positive reducer retention bounds and exact tick grid required')
        if type(coverage_complete) is not bool:
            raise ContractError('coverage status must be explicit')
        if (usd_multiplier is None) != (money_role is None) or (usd_multiplier is not None and
                (not isinstance(usd_multiplier, Decimal) or not usd_multiplier.is_finite() or usd_multiplier <= 0
                 or not isinstance(money_role, str) or not money_role)):
            raise ContractError('money projection requires a finite multiplier and role')
        for at in (start, end):
            if at is not None:
                timestamp(at)
        if start is not None and end is not None and start >= end:
            raise ContractError('reducer anchor interval must be nonempty')
        self._config = MappingProxyType({'instrument': instrument, 'instrument_kind': instrument_kind, 'quantity_unit': quantity_unit,
                       'terms_version': terms_version, 'aggregation_unit': aggregation_unit,
                       'usd_multiplier': None if usd_multiplier is None else str(usd_multiplier), 'money_role': money_role,
                       'row_ticks': row_ticks, 'grid_origin': grid_origin, 'start': start, 'end': end,
                       'coverage_complete': coverage_complete, 'definition_version': definition_version,
                       'max_records': max_records, 'max_bytes': max_bytes, 'max_profile_rows': max_profile_rows,
                       'max_snapshot_versions': max_snapshot_versions})
        self._active = {}
        self._seen = {}
        self._deltas = ()
        self._totals = _zero()
        self._rows = {}
        self._snapshots = {}
        self._snapshot_cursors = {}
        self._last_known = None

    @property
    def config(self):
        return self._config

    def _new(self):
        c = self.config
        return TransactionReducer(**{**c, 'usd_multiplier': None if c['usd_multiplier'] is None else Decimal(c['usd_multiplier'])})

    def _contains(self, value):
        return value is not None and (self.config['start'] is None or value.event_at >= self.config['start']) and (self.config['end'] is None or value.event_at < self.config['end'])

    def _check_value(self, value):
        if value is None:
            return
        c = self.config
        actual = (value.instrument_kind, value.quantity_unit, value.terms_version, value.aggregation_unit,
                  None if value.usd_multiplier is None else str(value.usd_multiplier), value.money_role)
        expected = tuple(c[k] for k in ('instrument_kind', 'quantity_unit', 'terms_version', 'aggregation_unit', 'usd_multiplier', 'money_role'))
        if actual != expected:
            raise ContractError('transaction cannot mix reducer instrument class/units/multiplier/terms')

    def _contribute(self, value, direction, totals, rows):
        if not self._contains(value):
            return
        q = value.quantity * direction
        totals['observed_volume'] += q
        if value.volume_eligibility is None:
            totals['condition_unresolved_volume'] += q
            return
        if not value.volume_eligibility:
            totals['excluded_volume'] += q
            return
        side = value.side
        channel = {1: 'buy', -1: 'sell', None: 'unknown'}[side]
        totals[channel] += q
        totals['total'] += q
        totals['prints'] += direction
        totals['incomplete_count'] += direction * int(not value.history_complete)
        if value.price_ticks is None:
            totals['profile_unpriced_volume'] += q
        else:
            price = value.price_ticks
            row = self.config['grid_origin'] + ((price - self.config['grid_origin']) // self.config['row_ticks']) * self.config['row_ticks']
            cells = rows.setdefault(row, [0, 0, 0])
            cells[{1: 0, -1: 1, None: 2}[side]] += q
            if not any(cells):
                del rows[row]
            totals['tick_mass'] += q
            totals['tick_first'] += q * price
            totals['tick_second'] += q * price * price
        if value.price_decimal is None or value.usd_multiplier is None:
            totals['money_unpriced_volume'] += q
        else:
            amount = Fraction(value.price_decimal) * Fraction(value.usd_multiplier) * q
            totals['notional'] += amount
            totals['signed_notional'] += amount * (side or 0)
            totals['unknown_notional'] += amount if side is None else 0

    def _state(self):
        return {'active': {key: {'version_id': version, 'value': None if value is None else value.record()}
                           for key, (version, value) in sorted(self._active.items())},
                'seen': dict(sorted(self._seen.items())), 'deltas': [d.record() for d in self._deltas],
                'totals': self._totals, 'rows': sorted((p, *v) for p, v in self._rows.items()),
                'snapshot_cuts': list(self._snapshots),
                'snapshots': [{'id': snap.id, 'cursor': self._snapshot_cursors[snap.id], 'value': asdict(snap)}
                              for snap in self._snapshots.values()],
                'last_known': self._last_known}

    def metrics(self):
        return {'retained_records': len(self._active) + len(self._seen) + len(self._deltas) + len(self._snapshots) + len(self._rows),
                'retained_envelope_bytes': len(canonical_json(self._state())), 'profile_rows': len(self._rows),
                'delta_count': len(self._deltas), 'snapshot_versions': len(self._snapshots)}

    def _check_bounds(self):
        m, c = self.metrics(), self.config
        if (m['retained_records'] > c['max_records'] or m['retained_envelope_bytes'] > c['max_bytes']
                or m['profile_rows'] > c['max_profile_rows'] or m['snapshot_versions'] > c['max_snapshot_versions']):
            raise ContractError('transaction reducer retained record/byte/profile/snapshot bound reached')
        t = self._totals
        nonnegative = ('buy', 'sell', 'unknown', 'total', 'prints', 'observed_volume', 'excluded_volume',
                       'condition_unresolved_volume', 'profile_unpriced_volume', 'money_unpriced_volume', 'tick_mass', 'tick_second', 'incomplete_count')
        if (any(t[k] < 0 for k in nonnegative) or any(v < 0 for row in self._rows.values() for v in row)
                or t['total'] != t['buy'] + t['sell'] + t['unknown']
                or t['observed_volume'] != t['total'] + t['excluded_volume'] + t['condition_unresolved_volume']
                or t['tick_mass'] + t['profile_unpriced_volume'] != t['total']):
            raise IntegrityError('transaction reducer nonnegative mass/conservation failed')

    def apply(self, delta: TransactionDelta):
        return bool(self.apply_batch((delta,)))

    def apply_batch(self, deltas: tuple[TransactionDelta, ...]):
        if not isinstance(deltas, tuple) or len(deltas) > self.config['max_records']:
            raise ContractError('bounded immutable delta batch required')
        # Complete atomic admissions may be concatenated, but never sliced.
        offset = 0
        while offset < len(deltas):
            first = deltas[offset]
            if not isinstance(first, TransactionDelta):
                raise ContractError('typed delta required')
            count = len(first.batch_versions)
            group = deltas[offset:offset + count]
            if (len(group) != count or any(not isinstance(d, TransactionDelta) for d in group)
                    or tuple(d.batch_index for d in group) != tuple(range(count))
                    or any(d.batch_id != first.batch_id for d in group)
                    or tuple(d.next_version_id for d in group) != first.batch_versions):
                raise IntegrityError('incomplete or reordered atomic transaction resolution batch')
            offset += count
        candidate = self._new()
        candidate._active, candidate._seen = dict(self._active), dict(self._seen)
        candidate._rows, candidate._totals = {p: list(v) for p, v in self._rows.items()}, dict(self._totals)
        candidate._deltas, candidate._snapshots = self._deltas, dict(self._snapshots)
        candidate._snapshot_cursors = dict(self._snapshot_cursors)
        candidate._last_known = self._last_known
        added = 0
        for delta in deltas:
            if not isinstance(delta, TransactionDelta) or delta.definition_version != self.config['definition_version']:
                raise ContractError('delta schema/definition mismatch')
            if delta.root_key.instrument_key != self.config['instrument']:
                raise ContractError('delta belongs to another raw instrument')
            prior_hash = candidate._seen.get(delta.id)
            raw_hash = digest(delta.record())
            if prior_hash is not None:
                if prior_hash != raw_hash:
                    raise IntegrityError('delta ID reused with changed bytes')
                continue
            if candidate._last_known is not None and delta.known_at < candidate._last_known:
                raise ContractError('delta availability regressed')
            prior = candidate._active.get(delta.root_key.id, (None, None))
            if prior != (delta.prior_version_id, delta.before_value):
                raise IntegrityError('forged before value or skipped transaction delta')
            candidate._check_value(delta.before_value); candidate._check_value(delta.after_value)
            candidate._contribute(delta.before_value, -1, candidate._totals, candidate._rows)
            candidate._contribute(delta.after_value, 1, candidate._totals, candidate._rows)
            candidate._active[delta.root_key.id] = (delta.next_version_id, delta.after_value)
            candidate._seen[delta.id] = raw_hash
            candidate._deltas += (delta,)
            candidate._last_known = delta.known_at
            added += 1
        candidate._check_bounds()
        self.__dict__.update(candidate.__dict__)
        return added

    def snapshot(self, cut: int):
        timestamp(cut)
        totals, rows, active, delta_ids = _zero(), {}, {}, []
        for delta in self._deltas:
            if delta.known_at <= cut:
                self._contribute(delta.before_value, -1, totals, rows)
                self._contribute(delta.after_value, 1, totals, rows)
                active[delta.root_key.id] = (delta.next_version_id, delta.after_value)
                delta_ids.append(delta.id)
        c = self.config
        snap = TransactionSnapshot(c['instrument'], cut, c['definition_version'], digest(dict(c)),
                                   tuple(sorted(c.items())), tuple(sorted(delta_ids)),
                                   tuple(sorted(version for version, value in active.values() if self._contains(value))),
                                   **{k: totals[k] for k in ('buy', 'sell', 'unknown', 'total', 'prints', 'observed_volume',
                                                           'excluded_volume', 'condition_unresolved_volume', 'profile_unpriced_volume',
                                                           'money_unpriced_volume', 'tick_mass', 'tick_first', 'tick_second')},
                                   profile=tuple((p, *v) for p, v in sorted(rows.items())),
                                   notional=totals['notional'] if c['money_role'] else None,
                                   signed_notional=totals['signed_notional'] if c['money_role'] else None,
                                   unknown_notional=totals['unknown_notional'] if c['money_role'] else None,
                                   money_role=c['money_role'], complete_history=c['coverage_complete'] and not totals['incomplete_count'] and not totals['condition_unresolved_volume'])
        if snap.id not in self._snapshots:
            prior = self._snapshots
            self._snapshots = {**prior, snap.id: snap}
            self._snapshot_cursors[snap.id] = len(self._deltas)
            try:
                self._check_bounds()
            except BaseException:
                self._snapshots = prior
                del self._snapshot_cursors[snap.id]
                raise
        return snap

    def checkpoint(self):
        return canonical_json({'schema': 'transaction-reducer-v1', 'config': dict(self.config), 'state': self._state(), 'metrics': self.metrics()})

    @classmethod
    def restore(cls, payload: bytes):
        try:
            row = json.loads(payload)
            if row['schema'] != 'transaction-reducer-v1':
                raise ContractError('unknown transaction reducer checkpoint')
            c = row['config']
            result = cls(**{**c, 'usd_multiplier': None if c['usd_multiplier'] is None else Decimal(c['usd_multiplier'])})
            deltas = tuple(TransactionDelta.restore(d) for d in row['state']['deltas'])
            cursor = 0
            for recorded in row['state']['snapshots']:
                next_cursor = recorded['cursor']
                if type(next_cursor) is not int or not cursor <= next_cursor <= len(deltas):
                    raise IntegrityError('invalid historical snapshot admission cursor')
                result.apply_batch(deltas[cursor:next_cursor])
                cursor = next_cursor
                snap = result.snapshot(recorded['value']['cut'])
                if snap.id != recorded['id']:
                    raise IntegrityError('snapshot lineage/arithmetic mismatch')
            result.apply_batch(deltas[cursor:])
            if result.checkpoint() != payload:
                raise IntegrityError('reducer checkpoint arithmetic, cursor or counters changed')
            return result
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, ContractError):
                raise
            raise IntegrityError('malformed transaction reducer checkpoint') from exc


def trade_from_transaction(resolved: ResolvedTransaction) -> Trade | None:
    if not isinstance(resolved, ResolvedTransaction):
        raise ContractError('resolved transaction required')
    value = resolved.value
    if value.volume_eligibility is None:
        raise DependencyUnavailable('unresolved condition cannot enter an eligible finite tape')
    if not value.volume_eligibility:
        return None
    if value.instrument_kind not in ('futures_outright', 'single_option') or value.quantity_unit != 'contracts':
        raise ContractError('finite contract tape cannot silently admit spread/share units')
    return Trade(resolved.root_key.id, resolved.version_hash, resolved.root_key.instrument_key, value.event_at,
                 resolved.known_at, None if value.price_ticks is None else Ticks(value.price_ticks), value.quantity,
                 value.side, None, value.aggregation_unit, value.history_complete)


class TransactionTapeView:
    def __init__(self, ledger: TransactionLedger):
        if not isinstance(ledger, TransactionLedger):
            raise ContractError('transaction tape view needs its bounded ledger')
        self.ledger = ledger

    def asof(self, *, instrument, cut, start=None, end=None):
        resolved_rows = self.ledger.asof(instrument=instrument, cut=cut, start=start, end=end)
        domains = {}
        for resolved in resolved_rows:
            key = resolved.root_key
            domain = (key.provider, key.dataset, key.publisher_or_venue, key.channel, key.source_session)
            domains.setdefault(resolved.value.event_at, set()).add(domain)
        # The single-row adapter cannot establish an order domain. Restore local
        # order only for a common fully declared domain in the entire time tie.
        return tuple(replace(trade, order=resolved.value.source_order)
                     if len(domains[trade.event_at]) == 1 and None not in next(iter(domains[trade.event_at])) else trade
                     for resolved in resolved_rows if (trade := trade_from_transaction(resolved)) is not None)

    def changes(self, *, instrument, cut, start, end):
        from trading_research.measurements.tape import CorrectionImpact
        return tuple(CorrectionImpact(d.id, d.known_at,
                                      instrument if d.before_value is not None else None,
                                      d.before_value.event_at if d.before_value is not None else None,
                                      instrument if d.after_value is not None else None,
                                      d.after_value.event_at if d.after_value is not None else None)
                     for d in self.ledger.changes(instrument=instrument, cut=cut, start=start, end=end))


def transaction_checkpoint(ledger: TransactionLedger, reducers: dict[str, TransactionReducer]):
    if not isinstance(reducers, dict) or any(not isinstance(k, str) or not k for k in reducers):
        raise ContractError('named consumer cursors required')
    for reducer in reducers.values():
        expected = tuple(d for d in ledger.deltas if d.root_key.instrument_key == reducer.config['instrument'])
        if reducer._deltas != expected:
            raise IntegrityError('consumer checkpoint skipped or forged a committed transaction delta')
    return canonical_json({'schema': 'transaction-bundle-v1', 'ledger_hex': ledger.checkpoint().hex(),
                           'reducers': {name: reducer.checkpoint().hex() for name, reducer in sorted(reducers.items())}})


def restore_transaction_checkpoint(payload: bytes):
    try:
        row = json.loads(payload)
        if row['schema'] != 'transaction-bundle-v1':
            raise ContractError('unknown atomic transaction bundle')
        ledger = TransactionLedger.restore(bytes.fromhex(row['ledger_hex']))
        reducers = {name: TransactionReducer.restore(bytes.fromhex(raw)) for name, raw in row['reducers'].items()}
        if transaction_checkpoint(ledger, reducers) != payload:
            raise IntegrityError('transaction bundle is not canonical')
        return ledger, reducers
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, ContractError):
            raise
        raise IntegrityError('malformed transaction checkpoint bundle') from exc
