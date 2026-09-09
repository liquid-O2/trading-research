"""Named-formation consumer of retained source measurements and trade caches.

This controller enumerates scientific clock/rolling/caller anchors and measures
them from admitted AtomicTrades plus exact cache reconstruction at intra-atom
cuts. It is not a wrapper around the whole-window composition probe. Codex
owns registered execution and family acceptance.
"""
from __future__ import annotations

from datetime import date
from fractions import Fraction
import time

from trading_research.errors import ContractError, IntegrityError
from trading_research.measurements.profiles import FrozenGrid
from trading_research.operations.artifacts import digest
from trading_research.research.auction_flow_anchors import (
    CONTRACT_SHA256, DETAIL_SHA256, KINDS, MINUTE_NS, ROLLING_MINUTES,
    AuctionAnchor, named_clock_anchors, rolling_anchor,
)
from trading_research.research.auction_flow_anchor_profiles import (
    BAR_PROXIES, PIN069BarClose, bar_proxy_atoms, profile_catalogue,
)
from trading_research.research.auction_flow_anchor_tpo import (
    BRACKET_MINUTES, AnchorTPO, required_atom_cuts,
)
from trading_research.research.auction_flow_anchor_trades import (
    AnchorTrades, AtomicTrades, RollingAnchorTrades, SourceOrderDomain,
    _integer, admit_source_order_domain, collection_packaging, missing_intervals,
)
from trading_research.research.auction_flow_profiles import footprint_geometry, view_sparse
from trading_research.research.auction_flow_storage import BoundedOutputs, read_json_artifact, read_series_tables
from trading_research.research.auction_flow_windows import (
    TRADE_FIELDS, TapeWindow, prepare_trade_batch,
)


VERSION = 'auction-flow-named-anchor-production-consumer-v1'
REQUEST_KIND = 'auction_flow_anchor_production_request_v1'
RESULT_KIND = 'auction_flow_anchor_production_result_v1'
STAT_KIND = 'auction_flow_anchor_production_statistic_row_v1'
RECEIPT_KIND = 'auction_flow_anchor_production_receipt_v1'
WINDOW_CACHE_KIND = 'auction_flow_admitted_source_window_v1'
BATCH_ROWS = 65_536
NAMED_CLOCK_VARIANTS = (
    'cash_rth', 'prior_cash_rth', 'observed_futures_18_17', 'overnight_18_0930',
    'morning_06_09_ny', 'source_06_09_fixed_utc_minus4',
    'source_monday_22_21_utc', 'source_tuesday_22_21_utc',
    'civil_ny_week', 'civil_ny_month', 'civil_ny_quarter', 'civil_ny_year',
)
PRODUCTS = (
    'anchor_trades', 'tpo', 'profile_catalogue', 'bar_proxy_atoms', 'vwap_dispersion', 'pin069',
)
FORMATIONS = ('closed', 'developing_prefix')
PENDING_SELECTION_KINDS = ('event', 'swing', 'composite')
DEFAULT_FOOTPRINT = {
    'ratio': Fraction(3), 'minimum_volume': 1, 'comparison': 'same_price',
    'zero_opponent': 'infinite_if_minimum', 'minimum_stack_rows': 2,
}


def _civil_date(value):
    if type(value) is date:
        return value
    if type(value) is str:
        try:
            result = date.fromisoformat(value)
        except ValueError as exc:
            raise ContractError('explicit civil date required') from exc
        if result.isoformat() != value:
            raise ContractError('explicit civil date required')
        return result
    raise ContractError('explicit civil date required')


def _text(value, *, name):
    if type(value) is not str or not value:
        raise ContractError(f'{name} required')
    return value


def _products(value):
    if value is None:
        return PRODUCTS
    if type(value) is not tuple or not value or any(item not in PRODUCTS for item in value):
        raise ContractError('explicit supported production products required')
    if len(set(value)) != len(value):
        raise ContractError('duplicate production products are not a schedule')
    return value


def auction_anchor(value):
    """Bind an admitted AuctionAnchor or its exact scientific record."""
    if type(value) is AuctionAnchor:
        return value
    if type(value) is not dict:
        raise ContractError('explicit admitted auction anchor or its record required')
    if value.get('contract_sha256') not in (None, CONTRACT_SHA256) or value.get('detail_sha256') not in (None, DETAIL_SHA256):
        raise IntegrityError('caller anchor does not join the current scientific contract')
    spans = value.get('spans')
    versions = value.get('source_versions')
    members = value.get('members') or ()
    if type(spans) not in (tuple, list) or type(versions) not in (tuple, list) or type(members) not in (tuple, list):
        raise ContractError('caller anchor lost its exact membership or source versions')
    return AuctionAnchor(
        variant=_text(value.get('variant'), name='anchor variant'),
        kind=_text(value.get('kind'), name='anchor kind'),
        root=_text(value.get('root'), name='root'),
        instrument_id=value.get('instrument_id'),
        contract_key=_text(value.get('contract_key'), name='raw contract'),
        source_lineage=_text(value.get('source_lineage'), name='source lineage'),
        spans=tuple(tuple(pair) for pair in spans),
        selection_known_at_ns=value.get('selection_known_at_ns'),
        source_versions=tuple(versions),
        members=tuple(members),
        revision_of=value.get('revision_of'),
        selection_evidence=value.get('selection_evidence'),
        start_source_order=value.get('start_source_order'))


def _request_name(*parts):
    text = '-'.join(str(part).replace(':', '_').replace('/', '_') for part in parts)
    return ''.join(ch if ch.isalnum() or ch in '-_.' else '_' for ch in text)


def _raw_contract(row):
    if type(row) is not dict:
        raise ContractError('supported raw contract record required')
    root = _text(row.get('root'), name='root')
    key = _text(row.get('contract_key'), name='raw contract')
    lineage = _text(row.get('source_lineage'), name='source lineage')
    if root not in ('NQ', 'ES') or not key.startswith(root + ':') or not _integer(row.get('instrument_id'), minimum=1):
        raise ContractError('supported raw contract identity required')
    return {'root': root, 'instrument_id': row['instrument_id'], 'contract_key': key, 'source_lineage': lineage}


def _decision_cuts(rows):
    if type(rows) not in (tuple, list) or not rows:
        raise ContractError('frozen complete decision-cut schedule required')
    result = []
    seen = set()
    for row in rows:
        if type(row) is not dict:
            raise ContractError('explicit civil-date decision cut required')
        day, cut = _civil_date(row.get('civil_date')), row.get('cut_ns')
        if not _integer(cut):
            raise ContractError('explicit decision cut required')
        key = (day, cut)
        if key in seen:
            raise ContractError('duplicate decision cut is not a complete frozen schedule')
        seen.add(key)
        result.append({'civil_date': day, 'cut_ns': cut})
    return tuple(result)


def _domain(value, *, collection, contracts):
    if value is None:
        return None
    if type(value) is SourceOrderDomain:
        domain = value
    elif type(value) is dict:
        domain = admit_source_order_domain(
            value.get('spans') or value.get('domains'),
            collection=value.get('collection', collection),
            raw_contract=value.get('raw_contract'),
            root=value.get('root'),
            disjoint_selection=value.get('disjoint_selection'))
    else:
        raise ContractError('optional source-order domain must be an admitted map')
    if domain.collection != collection:
        raise IntegrityError('source-order domain collection does not join the request collection')
    keys = {(row['root'], row['contract_key']) for row in contracts}
    if (domain.root, domain.raw_contract) not in keys:
        raise IntegrityError('source-order domain names an unrequested raw contract')
    return domain


def expand_anchor_schedule(schedule, *, calendar):
    """Materialize every requested formation or exact availability disposition."""
    if type(schedule) is not dict or schedule.get('kind') != REQUEST_KIND:
        raise ContractError('frozen named-anchor production request schedule required')
    if schedule.get('contract_sha256') not in (None, CONTRACT_SHA256) or schedule.get('detail_sha256') not in (None, DETAIL_SHA256):
        raise IntegrityError('request schedule does not join the current scientific contract')
    collection = _text(schedule.get('collection'), name='acquisition collection')
    cuts = _decision_cuts(schedule.get('decision_cuts'))
    contracts = tuple(_raw_contract(row) for row in (schedule.get('raw_contracts') or ()))
    if not contracts:
        raise ContractError('supported raw contracts required')
    products = _products(schedule.get('products'))
    latency = schedule.get('latency_ns', 250_000_000)
    if not _integer(latency) or latency > 1_000_000_000:
        raise ContractError('explicit supported source-delay scenario required')
    domain = _domain(schedule.get('source_order_domain'), collection=collection, contracts=contracts)
    variants = schedule.get('named_clock_variants', True)
    if variants is True:
        variants = NAMED_CLOCK_VARIANTS
    elif type(variants) is not tuple or any(v not in NAMED_CLOCK_VARIANTS for v in variants):
        raise ContractError('named clock variants must be the registered scientific set')
    rolling = schedule.get('rolling_minutes', ())
    if rolling not in ((), None) and (
            type(rolling) is not tuple or any(m not in ROLLING_MINUTES for m in rolling)):
        raise ContractError('rolling minutes must be the registered 5/15/60/240 set')
    rolling = () if rolling is None else rolling
    rolling_ends = schedule.get('rolling_event_ends', ())
    if rolling and (type(rolling_ends) is not tuple or not rolling_ends or any(not _integer(v, minimum=1) for v in rolling_ends)):
        raise ContractError('rolling requests need explicit event ends; source UTC days are not formations')
    formations = schedule.get('formations', ('closed',))
    if type(formations) is not tuple or not formations or any(item not in FORMATIONS for item in formations):
        raise ContractError('closed and developing-prefix formations are distinct requests')
    developing_ends = schedule.get('developing_event_ends', ())
    if 'developing_prefix' in formations and (
            type(developing_ends) is not tuple or any(not _integer(v, minimum=1) for v in developing_ends)):
        raise ContractError('developing prefixes need explicit observation ends')
    pending_kinds = schedule.get('pending_selection_kinds', ())
    if type(pending_kinds) is not tuple or any(k not in PENDING_SELECTION_KINDS for k in pending_kinds):
        raise ContractError('missing selection producers must be named explicitly')
    cut_by_day = {}
    for row in cuts:
        cut_by_day.setdefault(row['civil_date'], []).append(row['cut_ns'])
    work = []

    def add(row):
        work.append(row)

    for row in cuts:
        for contract in contracts:
            clocks = named_clock_anchors(
                day=row['civil_date'], cut_ns=row['cut_ns'], calendar=calendar, **contract)
            available = {anchor.variant: anchor for anchor in clocks['anchors']}
            unavailable = {item['variant']: item for item in clocks['unavailable']}
            for variant in variants:
                request_id = _request_name(
                    'named', variant, row['civil_date'].isoformat(), contract['contract_key'], row['cut_ns'])
                if variant in unavailable:
                    add({'request_id': request_id + '-closed', 'kind': 'named_clock', 'variant': variant,
                         'civil_date': row['civil_date'], 'decision_cut_ns': row['cut_ns'],
                         'contract': contract, 'products': products, 'latency_ns': latency,
                         'formation': 'closed', 'disposition': 'unavailable',
                         'availability': unavailable[variant]})
                    continue
                if variant not in available:
                    add({'request_id': request_id + '-closed', 'kind': 'named_clock', 'variant': variant,
                         'civil_date': row['civil_date'], 'decision_cut_ns': row['cut_ns'],
                         'contract': contract, 'products': products, 'latency_ns': latency,
                         'formation': 'closed', 'disposition': 'not_applicable',
                         'availability': {'variant': variant, 'reason': 'weekday_or_clock_not_applicable'}})
                    continue
                anchor = available[variant]
                if 'closed' in formations:
                    add({'request_id': request_id + '-closed', 'kind': 'named_clock', 'variant': variant,
                         'civil_date': row['civil_date'], 'decision_cut_ns': row['cut_ns'],
                         'contract': contract, 'products': products, 'latency_ns': latency,
                         'formation': 'closed', 'anchor': anchor, 'event_end_ns': anchor.end_ns,
                         'disposition': 'measure'})
                if 'developing_prefix' in formations:
                    for end in developing_ends:
                        if not anchor.start_ns < end < anchor.end_ns:
                            add({'request_id': request_id + f'-prefix-{end}', 'kind': 'named_clock',
                                 'variant': variant, 'civil_date': row['civil_date'],
                                 'decision_cut_ns': row['cut_ns'], 'contract': contract,
                                 'products': products, 'latency_ns': latency,
                                 'formation': 'developing_prefix', 'anchor': anchor, 'event_end_ns': end,
                                 'disposition': 'unavailable',
                                 'availability': {'reason': 'developing_prefix_outside_declared_formation'}})
                            continue
                        add({'request_id': request_id + f'-prefix-{end}', 'kind': 'named_clock',
                             'variant': variant, 'civil_date': row['civil_date'],
                             'decision_cut_ns': row['cut_ns'], 'contract': contract,
                             'products': products, 'latency_ns': latency,
                             'formation': 'developing_prefix', 'anchor': anchor, 'event_end_ns': end,
                             'disposition': 'measure'})
            for kind in pending_kinds:
                add({'request_id': _request_name('pending', kind, row['civil_date'].isoformat(),
                                                contract['contract_key'], row['cut_ns']),
                     'kind': kind, 'variant': kind, 'civil_date': row['civil_date'],
                     'decision_cut_ns': row['cut_ns'], 'contract': contract, 'products': products,
                     'latency_ns': latency, 'formation': 'closed',
                     'disposition': 'pending_selection_producer',
                     'availability': {'reason': 'selection_producer_not_supplied', 'kind': kind,
                                      'hindsight_pivot_manufactured': False}})
    for minutes in rolling:
        for end in rolling_ends:
            for contract in contracts:
                known = end
                add({'request_id': _request_name('rolling', minutes, contract['contract_key'], end),
                     'kind': 'rolling', 'variant': f'rolling_{minutes}m', 'minutes': minutes,
                     'decision_cut_ns': max(cut for day in cut_by_day for cut in cut_by_day[day]),
                     'contract': contract, 'products': products, 'latency_ns': latency,
                     'formation': 'closed', 'event_end_ns': end,
                     'anchor': rolling_anchor(minutes=minutes, event_end_ns=end,
                        selection_known_at_ns=known, source_versions=('rolling-request-cut',), **contract),
                     'disposition': 'measure'})
    for index, raw in enumerate(schedule.get('caller_anchors') or ()):
        if type(raw) is not dict and type(raw) is not AuctionAnchor:
            raise ContractError('caller-supplied causal or composite anchors must be explicit records')
        if type(raw) is dict and raw.get('kind') in PENDING_SELECTION_KINDS and raw.get('selection_evidence') is None:
            add({'request_id': _request_name('caller', raw.get('kind'), index),
                 'kind': raw.get('kind'), 'variant': raw.get('variant'), 'contract': contracts[0],
                 'products': products, 'latency_ns': latency, 'formation': 'closed',
                 'decision_cut_ns': cuts[0]['cut_ns'],
                 'disposition': 'pending_selection_producer',
                 'availability': {'reason': 'selection_evidence_absent', 'hindsight_pivot_manufactured': False}})
            continue
        try:
            anchor = auction_anchor(raw if type(raw) is AuctionAnchor or 'spans' in raw else raw.get('anchor', raw))
        except (ContractError, IntegrityError) as exc:
            add({'request_id': _request_name('caller', index), 'kind': getattr(raw, 'kind', None) or raw.get('kind'),
                 'disposition': 'rejected', 'availability': {'reason': str(exc)},
                 'products': products, 'latency_ns': latency, 'formation': 'closed',
                 'decision_cut_ns': cuts[0]['cut_ns'], 'contract': contracts[0]})
            continue
        if anchor.kind not in KINDS:
            raise ContractError('caller anchor kind is outside the scientific set')
        formation = raw.get('formation', 'closed') if type(raw) is dict else 'closed'
        event_end = raw.get('event_end_ns', anchor.end_ns) if type(raw) is dict else anchor.end_ns
        decision = raw.get('decision_cut_ns') if type(raw) is dict else None
        if decision is None:
            decision = max(row['cut_ns'] for row in cuts)
        if formation == 'closed' and event_end != anchor.end_ns:
            add({'request_id': _request_name('caller', anchor.variant, index), 'kind': anchor.kind,
                 'variant': anchor.variant, 'anchor': anchor, 'event_end_ns': event_end,
                 'decision_cut_ns': decision, 'contract': {
                     'root': anchor.root, 'instrument_id': anchor.instrument_id,
                     'contract_key': anchor.contract_key, 'source_lineage': anchor.source_lineage},
                 'products': products, 'latency_ns': latency, 'formation': formation,
                 'disposition': 'unavailable',
                 'availability': {'reason': 'closed_formation_requires_declared_end'}})
            continue
        if formation == 'developing_prefix' and not (anchor.start_ns < event_end <= anchor.end_ns):
            add({'request_id': _request_name('caller', anchor.variant, index), 'kind': anchor.kind,
                 'variant': anchor.variant, 'anchor': anchor, 'disposition': 'unavailable',
                 'availability': {'reason': 'developing_prefix_outside_declared_formation'},
                 'products': products, 'latency_ns': latency, 'formation': formation,
                 'decision_cut_ns': decision, 'contract': {
                     'root': anchor.root, 'instrument_id': anchor.instrument_id,
                     'contract_key': anchor.contract_key, 'source_lineage': anchor.source_lineage}})
            continue
        add({'request_id': _request_name('caller', anchor.kind, anchor.variant, event_end, index),
             'kind': anchor.kind, 'variant': anchor.variant, 'anchor': anchor,
             'event_end_ns': event_end, 'decision_cut_ns': decision,
             'contract': {'root': anchor.root, 'instrument_id': anchor.instrument_id,
                          'contract_key': anchor.contract_key, 'source_lineage': anchor.source_lineage},
             'products': products, 'latency_ns': latency, 'formation': formation,
             'disposition': 'measure'})
    explicit = schedule.get('requests')
    if explicit is not None:
        if type(explicit) is not tuple or not explicit:
            raise ContractError('explicit request list must be the complete frozen membership')
        by_id = {row['request_id']: row for row in work}
        selected = []
        for row in explicit:
            if type(row) is not dict or type(row.get('request_id')) is not str:
                raise ContractError('explicit request membership records required')
            if row.get('kind') == 'source_utc_day':
                selected.append({**row, 'disposition': 'source_utc_day_is_not_a_scientific_formation',
                                 'availability': {'reason': 'source_utc_day_is_not_a_scientific_formation'}})
            elif row['request_id'] in by_id:
                selected.append(by_id[row['request_id']])
            else:
                selected.append({**row, 'disposition': 'not_a_member_of_enumerated_schedule',
                                 'availability': {'reason': 'request_is_not_a_member_of_the_enumerated_schedule'}})
        work = selected
    ids = [row['request_id'] for row in work]
    if len(ids) != len(set(ids)):
        raise ContractError('request schedule downsampled or duplicated identities')
    return {
        'version': VERSION, 'collection': collection, 'decision_cuts': cuts, 'raw_contracts': contracts,
        'source_order_domain': None if domain is None else domain.record(),
        'domain': domain, 'latency_ns': latency, 'products': products,
        'requests': tuple(work), 'or15_default_anchor': False,
        'source_utc_days_used_as_scientific_formations': False,
        'hindsight_pivots_manufactured': False,
        'arbitrary_top_n': False,
    }


def _window_record(row, *, collection):
    if type(row) is not dict:
        raise ContractError('admitted source-window catalog records required')
    root = _text(row.get('root'), name='root')
    contract = _text(row.get('contract_key'), name='raw contract')
    source_path = row.get('source_path')
    packaging = row.get('packaging')
    if packaging is None and type(source_path) is str and source_path:
        packaging = collection_packaging(source_path)
    if packaging not in ('civil-date-named', 'civil-month-named'):
        raise ContractError('admitted window must disclose monthly or date-named collection packaging')
    window_collection = _text(row.get('collection', collection), name='acquisition collection')
    if window_collection != collection:
        raise IntegrityError('catalog window is outside the requested acquisition collection')
    if not _integer(row.get('event_start_ns')) or not _integer(row.get('event_end_ns')):
        raise ContractError('admitted window needs exact event bounds')
    if not row['event_start_ns'] < row['event_end_ns']:
        raise ContractError('admitted window bounds are empty')
    if not _integer(row.get('instrument_id'), minimum=1):
        raise ContractError('admitted window needs its raw instrument')
    source_key = _text(row.get('source_key') or row.get('source_path') or row.get('source_lineage'), name='source key')
    return {
        **row,
        'root': root, 'contract_key': contract, 'collection': window_collection, 'packaging': packaging,
        'source_key': source_key,
        'source_lineage': _text(row.get('source_lineage') or source_key, name='source lineage'),
        'source_coverage_complete': bool(row.get('source_coverage_complete')),
        'coordinate_complete': bool(row.get('coordinate_complete')),
        'latency_ns': row.get('latency_ns', 250_000_000),
        'receipt_sha256': row.get('receipt_sha256'),
        'coordinate_identity': row.get('coordinate_identity') or contract,
    }


class _PreparedWindow:
    """Decode one source window once into bounded prepared batches."""
    def __init__(self, window):
        self.window = window
        self._prepared = None
        self.atoms = tuple(window['atoms']) if window.get('atoms') else ()

    def bind_measurement(self):
        measured = self.window.get('measurement')
        reference = self.window.get('measurement_reference')
        if measured is None and reference is not None:
            measured = read_json_artifact(reference)
            self.window['measurement'] = measured
        if not measured or self.atoms:
            return
        instruments = measured['instruments'] if isinstance(measured, dict) and 'instruments' in measured else ()
        bound = []
        for instrument in instruments:
            if instrument.get('instrument_id') != self.window['instrument_id']:
                continue
            identity = instrument.get('coordinate') or {}
            if identity.get('contract_key') not in (None, self.window['contract_key']):
                raise IntegrityError('measurement contract does not join the admitted window')
            for row in instrument.get('atomic_windows') or ():
                trade = row['trade']
                bound.append(AtomicTrades.from_record(
                    trade, root=self.window['root'], contract_key=self.window['contract_key'],
                    source_lineage=self.window['source_lineage'],
                    evidence_id=digest({'window': self.window['source_key'], 'bin': row.get('bin'),
                                        'start': row.get('event_start_ns'), 'end': row.get('event_end_ns')})))
        self.atoms = tuple(bound)

    def prepare(self):
        if self._prepared is not None:
            return self._prepared
        tables = self.window.get('trade_tables')
        storage = self.window.get('trade_storage')
        if tables is None and storage is not None:
            tables = tuple(read_series_tables(storage))
        if tables is None:
            self._prepared = ()
            return self._prepared
        batches = []
        for table in tables:
            if not set(TRADE_FIELDS).issubset(table.schema.names):
                raise IntegrityError('retained trade cache lost original fields')
            for offset in range(0, len(table), BATCH_ROWS):
                batches.append(prepare_trade_batch(table.slice(offset, min(BATCH_ROWS, len(table) - offset))))
        self._prepared = tuple(batches)
        return self._prepared

    def close(self):
        if self._prepared:
            for batch in self._prepared:
                batch.release()
        self._prepared = ()


def _eligible_runs(prepared, *, instrument_id, source_keys, start_ns, end_ns, start_source_order, known_at_limit):
    import numpy as np

    if not len(prepared):
        return
    values = prepared.values
    t, order, inst, known = values['t'], values['source_order'], values['instrument_id'], values['known_at_ns']
    ok = (inst == instrument_id) & (t >= start_ns) & (t < end_ns) & (known <= known_at_limit)
    if start_source_order is not None:
        ok &= (t > start_ns) | (order >= start_source_order)
    indices = [int(i) for i in np.flatnonzero(ok) if prepared.source_key(int(i)) in source_keys]
    if not indices:
        return
    left = indices[0]
    prev = left
    for index in indices[1:]:
        if index != prev + 1:
            yield left, prev + 1
            left = index
        prev = index
    yield left, prev + 1


def reconstruct_boundary_atom(*, window, start_ns, end_ns, start_source_order, latency_ns,
                              source_complete, coordinate_complete, known_at_limit, batches):
    """Rebuild one scientific piece from retained exact trades. Never reads MBP."""
    if not _integer(start_ns) or not _integer(end_ns) or not start_ns < end_ns:
        raise ContractError('exact reconstruction interval required')
    if start_source_order is not None and not _integer(start_source_order):
        raise ContractError('exact causal source-order cut required')
    tape = TapeWindow(instrument_id=window['instrument_id'], start_ns=start_ns, end_ns=end_ns,
                      latency_ns=latency_ns)
    keys = {window['source_key']}
    for prepared in batches:
        for left, right in _eligible_runs(
                prepared, instrument_id=window['instrument_id'], source_keys=keys,
                start_ns=start_ns, end_ns=end_ns, start_source_order=start_source_order,
                known_at_limit=known_at_limit):
            tape.add_prepared(prepared, left, right)
    record = tape.record(source_coverage_complete=source_complete, coordinate_complete=coordinate_complete)
    return AtomicTrades.from_record(
        record, root=window['root'], contract_key=window['contract_key'],
        source_lineage=window['source_lineage'], start_source_order=start_source_order,
        evidence_id=digest({'kind': 'reconstructed_boundary_atom', 'source_key': window['source_key'],
                            'start_ns': start_ns, 'end_ns': end_ns, 'start_source_order': start_source_order}))


def _covering_windows(prepared, *, contract, start_ns, end_ns, domain):
    chosen = []
    for item in prepared:
        window = item.window
        if (window['root'] != contract['root'] or window['contract_key'] != contract['contract_key']
                or window['instrument_id'] != contract['instrument_id']):
            continue
        if domain is not None:
            try:
                domain.span_for_key(window['source_key'])
            except IntegrityError:
                continue
        if window['event_start_ns'] < end_ns and start_ns < window['event_end_ns']:
            chosen.append(item)
    ordered = sorted(chosen, key=lambda item: (item.window['event_start_ns'], item.window['event_end_ns']))
    for first, second in zip(ordered, ordered[1:]):
        if first.window['event_end_ns'] > second.window['event_start_ns']:
            raise IntegrityError('overlapping source spans in one collection cannot be concatenated')
    return ordered


def _scientific_cuts(anchor, *, event_end_ns, products, extra=()):
    cuts = {event_end_ns, *extra}
    for start, end in anchor.prefix_spans(event_end_ns):
        cuts.update((start, end))
        if anchor.kind == 'rolling':
            cuts.update(range(start, end, MINUTE_NS))
    if 'tpo' in products:
        cuts.update(required_atom_cuts(anchor, event_end_ns=event_end_ns))
    return tuple(sorted(c for c in cuts if type(c) is int))


def _split(start, end, cuts):
    inner = tuple(cut for cut in cuts if start < cut < end)
    if not inner:
        return ((start, end),)
    points = (start,) + inner + (end,)
    return tuple(zip(points[:-1], points[1:]))


def _covered_slice(window, start, end):
    return (window['source_coverage_complete']
            and window['event_start_ns'] <= start < end <= window['event_end_ns'])


def _coordinate_slice(window, start, end):
    return (window['coordinate_complete']
            and window['event_start_ns'] <= start < end <= window['event_end_ns'])


def assemble_constituents(anchor, *, event_end_ns, products, windows, domain, latency_ns, decision_cut_ns):
    """Wholly aligned atoms plus exact cache reconstruction at scientific cuts."""
    intended = anchor.prefix_spans(event_end_ns)
    if not intended:
        return {'atoms': (), 'reconstruction': (), 'missing': intended, 'status': 'empty_prefix'}
    extra = ()
    if anchor.kind == 'rolling':
        extra = (event_end_ns - (event_end_ns - anchor.start_ns),)
    cuts = _scientific_cuts(anchor, event_end_ns=event_end_ns, products=products, extra=extra)
    pieces, reconstruction, unavailable = [], [], []
    for start, end in intended:
        covering = _covering_windows(windows, contract={
            'root': anchor.root, 'contract_key': anchor.contract_key, 'instrument_id': anchor.instrument_id},
            start_ns=start, end_ns=end, domain=domain)
        occupied = tuple((max(item.window['event_start_ns'], start), min(item.window['event_end_ns'], end))
                         for item in covering)
        for gap_start, gap_end in missing_intervals(((start, end),), occupied):
            unavailable.append((gap_start, gap_end, 'missing_source_interval'))
        for item in covering:
            window = item.window
            item.bind_measurement()
            if item.atoms:
                intervals = [(atom.start_ns, atom.end_ns, atom) for atom in item.atoms
                             if atom.start_ns < end and start < atom.end_ns]
            else:
                intervals = [(max(window['event_start_ns'], start), min(window['event_end_ns'], end), None)]
            for atom_start, atom_end, parent in intervals:
                left, right = max(atom_start, start), min(atom_end, end)
                if left >= right:
                    continue
                for piece_start, piece_end in _split(left, right, cuts):
                    cursor = anchor.start_source_order if piece_start == anchor.start_ns else None
                    aligned = (parent is not None and parent.start_ns == piece_start
                               and parent.end_ns == piece_end and parent.start_source_order == cursor)
                    if aligned:
                        pieces.append(parent)
                        continue
                    if parent is not None and parent.start_ns == piece_start and parent.end_ns == piece_end and cursor is None:
                        pieces.append(parent)
                        continue
                    batches = item.prepare()
                    if not batches:
                        unavailable.append((piece_start, piece_end, 'boundary_reconstruction_unavailable'))
                        continue
                    source_complete = _covered_slice(window, piece_start, piece_end)
                    coordinate_complete = _coordinate_slice(window, piece_start, piece_end)
                    if parent is not None:
                        source_complete = source_complete and parent.source_complete
                        coordinate_complete = coordinate_complete and parent.coordinate_complete
                    atom = reconstruct_boundary_atom(
                        window=window, start_ns=piece_start, end_ns=piece_end,
                        start_source_order=cursor, latency_ns=latency_ns,
                        source_complete=source_complete, coordinate_complete=coordinate_complete,
                        known_at_limit=decision_cut_ns, batches=batches)
                    pieces.append(atom)
                    reconstruction.append({
                        'start_ns': piece_start, 'end_ns': piece_end, 'start_source_order': cursor,
                        'source_key': window['source_key'], 'parent_evidence': None if parent is None else parent.evidence_id,
                        'whole_minute_used_across_cut': False,
                    })
    pieces = tuple(sorted(pieces, key=lambda atom: (atom.start_ns, atom.end_ns)))
    return {
        'atoms': pieces,
        'reconstruction': tuple(reconstruction),
        'unavailable': tuple(unavailable),
        'intended': intended,
        'cuts': cuts,
        'status': 'ready',
    }


def _statistic_row(request, *, trades=None, tpo=None, profiles=None, disposition, coverage):
    path = None if trades is None else trades['flows']['all']
    weighted = None if trades is None else trades.get('weighted_price')
    source = None
    if profiles and profiles.get('variants'):
        source = next((row for row in profiles['variants'] if row['variant'] == 'source-one-tick-value-7/10'),
                      profiles['variants'][0])
    geometry = None if source is None else source.get('geometry')
    tpo_30 = None if not tpo else tpo.get('30')
    return {
        'kind': STAT_KIND, 'request_id': request['request_id'], 'disposition': disposition,
        'root': request['contract']['root'], 'collection': request.get('collection'),
        'raw_contract': request['contract']['contract_key'],
        'anchor_definition': None if request.get('anchor') is None else request['anchor'].record(),
        'variant': request.get('variant'), 'formation': request.get('formation'),
        'requested_event_end_ns': request.get('event_end_ns'),
        'decision_cut_ns': request.get('decision_cut_ns'),
        'support': None if trades is None else trades.get('source_coverage_complete'),
        'coverage': coverage,
        'price_range': None if trades is None else (None if trades.get('low_price_at_order') is None else trades['low_price_at_order'][0],
                                                    None if trades.get('high_price_at_order') is None else trades['high_price_at_order'][0]),
        'volume': None if path is None else path['volume'],
        'buy': None if path is None else path['buy'],
        'sell': None if path is None else path['sell'],
        'unknown': None if path is None else path['unknown'],
        'delta': None if path is None else path['close'],
        'poc': None if geometry is None else geometry.get('scalar_poc'),
        'value_area': None if geometry is None else geometry.get('value_rows'),
        'nodes': None if geometry is None else geometry.get('local_peaks'),
        'shape': None if source is None else source.get('side_geometry'),
        'vwap': None if weighted is None else weighted.get('vwap_ticks'),
        'dispersion': None if weighted is None else {
            'variance_ticks_squared': weighted.get('variance_ticks_squared'),
            'weighted_mad_ticks': weighted.get('weighted_mad_ticks'),
            'sd_ticks_decimal50': weighted.get('sd_ticks_decimal50'),
        },
        'tpo_features': None if tpo_30 is None else {
            'complete_brackets': tpo_30.get('complete_brackets'),
            'final_single_print_rows': tpo_30.get('final_single_print_rows'),
            'low_tail_rows': tpo_30.get('low_tail_rows'),
            'high_tail_rows': tpo_30.get('high_tail_rows'),
            'initial_balance': tpo_30.get('initial_balance'),
        },
        'empty_observed_formation': None if trades is None else trades.get('empty_observed_formation'),
        'no_volume': bool(path is not None and path['volume'] == 0),
    }


def _measure_request(request, *, windows, domain, collection):
    if request['disposition'] != 'measure':
        return {
            'request_id': request['request_id'], 'disposition': request['disposition'],
            'availability': request.get('availability'), 'statistic': _statistic_row(
                {**request, 'collection': collection}, disposition=request['disposition'],
                coverage=request['disposition']),
        }
    anchor, products = request['anchor'], request['products']
    event_end, decision, latency = request['event_end_ns'], request['decision_cut_ns'], request['latency_ns']
    assembled = assemble_constituents(
        anchor, event_end_ns=event_end, products=products, windows=windows, domain=domain,
        latency_ns=latency, decision_cut_ns=decision)
    atoms = assembled['atoms']
    if request['kind'] == 'rolling':
        rolling = RollingAnchorTrades(
            minutes=request['minutes'], source_versions=anchor.source_versions,
            source_order_domain=domain, **request['contract'])
        for atom in atoms:
            rolling.add(atom)
        trades = rolling.record(event_end_ns=event_end, decision_cut_ns=decision, latency_ns=latency)
        fixed_profile = rolling.profile
    else:
        fixed = AnchorTrades(anchor, source_order_domain=domain)
        for atom in atoms:
            fixed.add(atom)
        trades = fixed.record(event_end_ns=event_end, decision_cut_ns=decision, latency_ns=latency)
        fixed_profile = fixed.profile
    tpo_values = {}
    if 'tpo' in products:
        for minutes in BRACKET_MINUTES:
            tpo = AnchorTPO(anchor, bracket_minutes=minutes)
            for atom in atoms:
                tpo.add(atom)
            tpo_values[str(minutes)] = tpo.record(event_end_ns=event_end, decision_cut_ns=decision, latency_ns=latency)
    profiles = None
    footprint = None
    if 'profile_catalogue' in products or 'vwap_dispersion' in products:
        profiles = profile_catalogue(
            fixed_profile, anchor=anchor, known_at_ns=trades['known_at_ns'],
            coverage_complete=trades['price_history_complete'])
        if profiles.get('variants') and fixed_profile.rows:
            low, high = min(fixed_profile.rows), max(fixed_profile.rows)
            grid = FrozenGrid(0, 1, low, high, 'current-prefix-one-tick-origin-zero-v1', trades['known_at_ns'],
                              max_rows=fixed_profile.maximum_cells)
            original = view_sparse(fixed_profile, coordinate_identity=anchor.contract_key, grid=grid,
                                   coverage_complete=trades['price_history_complete'])
            footprint = footprint_geometry(original, **DEFAULT_FOOTPRINT)
    proxies = ()
    if 'bar_proxy_atoms' in products:
        bar_atoms = tuple(atom for atom in atoms if atom.start_source_order is None)
        if fixed_profile.rows:
            grid = FrozenGrid(0, 1, min(fixed_profile.rows), max(fixed_profile.rows),
                              'completed-bar-proxy-grid-v1', trades['known_at_ns'],
                              max_rows=fixed_profile.maximum_cells)
            proxies = tuple(bar_proxy_atoms(bar_atoms, anchor=anchor, grid=grid, variant=variant,
                                            coverage_complete=trades['price_history_complete'])
                            for variant in BAR_PROXIES)
        else:
            proxies = tuple({'variant': variant, 'reason': 'no_observed_priced_mass'} for variant in BAR_PROXIES)
    pin069 = None
    if 'pin069' in products:
        if anchor.variant != 'source_06_09_fixed_utc_minus4':
            pin069 = {'status': 'pin069_requires_fixed_utc_minus4_source_window',
                      'requested': True, 'computed': False}
        else:
            seq = PIN069BarClose(anchor)
            pin069 = tuple(seq.add(atom) for atom in atoms if atom.start_source_order is None)
    coverage = ('complete' if trades['source_coverage_complete'] and trades['coordinate_complete']
                else 'partial' if atoms else 'missing')
    if assembled['unavailable'] and coverage == 'complete':
        coverage = 'partial'
    disposition = ('no_volume' if trades['empty_observed_formation']
                   else 'partial' if coverage == 'partial'
                   else 'completed' if coverage == 'complete'
                   else 'missing_coverage')
    payload = {
        'request_id': request['request_id'], 'disposition': disposition, 'coverage': coverage,
        'anchor': trades.get('anchor') or anchor.record(),
        'formation': request['formation'], 'formation_final': trades.get('formation_final'),
        'observation_end_ns': event_end, 'decision_cut_ns': decision,
        'trades': trades if 'anchor_trades' in products or 'vwap_dispersion' in products else None,
        'tpo': tpo_values or None,
        'profiles': profiles,
        'footprint': footprint,
        'bar_proxies': proxies or None,
        'pin069': pin069,
        'reconstruction': assembled['reconstruction'],
        'unavailable_intervals': assembled['unavailable'],
        'source_order_domain': None if domain is None else domain.record(),
        'members': trades.get('members'),
        'atom_count': len(atoms),
        'quote_or_book_carry_composed': False,
        'whole_minute_used_across_cut': False,
        'raw_mbp_read': False,
    }
    payload['statistic'] = _statistic_row(
        {**request, 'collection': collection}, trades=trades, tpo=tpo_values or None,
        profiles=profiles, disposition=disposition, coverage=coverage)
    return payload


def consume_anchor_schedule(schedule, *, catalog, calendar, outputs, registered_attempt=None):
    """Measure every scheduled scientific formation from retained source artifacts."""
    if not isinstance(outputs, BoundedOutputs):
        raise ContractError('named-anchor production requires bounded registered outputs')
    if type(catalog) is not dict or catalog.get('kind') not in (WINDOW_CACHE_KIND, None):
        raise ContractError('admitted source measurement/trade-cache catalog required')
    started = time.process_time()
    cpu = {}
    byte_start = outputs.written
    expanded = expand_anchor_schedule(schedule, calendar=calendar)
    cpu['schedule_membership'] = time.process_time() - started
    collection = expanded['collection']
    domain = expanded['domain']
    packaging = None
    prepared = []
    began = time.process_time()
    for row in catalog.get('windows') or ():
        window = _window_record(row, collection=collection)
        if packaging is None:
            packaging = window['packaging']
        elif window['packaging'] != packaging:
            raise IntegrityError('monthly and date-named acquisitions are distinct collections')
        prepared.append(_PreparedWindow(window))
    cpu['catalog_admission'] = time.process_time() - began
    results = []
    began = time.process_time()
    try:
        for request in expanded['requests']:
            request = {**request, 'collection': collection}
            try:
                results.append(_measure_request(request, windows=prepared, domain=domain, collection=collection))
            except (ContractError, IntegrityError) as exc:
                results.append({
                    'request_id': request['request_id'], 'disposition': 'rejected',
                    'availability': {'reason': str(exc)},
                    'statistic': _statistic_row(request, disposition='rejected', coverage='rejected'),
                })
    finally:
        for item in prepared:
            item.close()
    cpu['measurement'] = time.process_time() - began
    if len(results) != len(expanded['requests']):
        raise IntegrityError('request schedule was downsampled')
    began = time.process_time()
    references = []
    for row in results:
        name = _request_name(row['request_id'], 'anchor-result') + '.json.zst'
        references.append(outputs.json_compressed(name, row, kind=RESULT_KIND))
        row['result_ref'] = references[-1]
        row['statistic']['result_ref'] = references[-1]
    statistics = tuple(row['statistic'] for row in results)
    statistic_ref = outputs.json_compressed(
        _request_name(collection, 'anchor-statistics') + '.json.zst',
        {'kind': STAT_KIND, 'version': VERSION, 'rows': statistics}, kind=STAT_KIND)
    receipt = {
        'kind': RECEIPT_KIND, 'version': VERSION, 'success': True,
        'collection': collection, 'request_count': len(results),
        'result_count': len(results),
        'completed': sum(row['disposition'] == 'completed' for row in results),
        'no_volume': sum(row['disposition'] == 'no_volume' for row in results),
        'partial': sum(row['disposition'] == 'partial' for row in results),
        'unavailable': sum(row['disposition'] == 'unavailable' for row in results),
        'pending_selection_producer': sum(row['disposition'] == 'pending_selection_producer' for row in results),
        'rejected': sum(row['disposition'] == 'rejected' for row in results),
        'missing_coverage': sum(row['disposition'] == 'missing_coverage' for row in results),
        'not_applicable': sum(row['disposition'] == 'not_applicable' for row in results),
        'source_utc_day_is_not_a_scientific_formation': sum(
            row['disposition'] == 'source_utc_day_is_not_a_scientific_formation' for row in results),
        'atom_count': sum(row.get('atom_count') or 0 for row in results),
        'reconstruction_count': sum(len(row.get('reconstruction') or ()) for row in results),
        'references': references, 'statistic_reference': statistic_ref,
        'source_order_domain': None if domain is None else domain.record(),
        'registered_attempt': registered_attempt,
        'family_statistics_or_model_complete': False,
        'context_or_location_evaluation': False,
        'or15_default_anchor': False,
        'raw_mbp_read': False,
        'arbitrary_top_n': False,
        'hindsight_pivots_manufactured': False,
    }
    receipt_ref = outputs.json(_request_name(collection, 'anchor-production-receipt') + '.json',
                               receipt, kind=RECEIPT_KIND)
    cpu['serialization'] = time.process_time() - began
    cpu['total'] = time.process_time() - started
    return {
        'version': VERSION, 'kind': RESULT_KIND, 'success': True,
        'receipt': receipt, 'receipt_reference': receipt_ref,
        'statistic_reference': statistic_ref, 'result_references': tuple(references),
        'results': tuple(results), 'statistics': statistics,
        'request_count': len(results), 'result_count': len(results),
        'atom_count': receipt['atom_count'],
        'cpu_components_disjoint': cpu,
        'cpu_seconds': cpu['total'],
        'output_bytes': outputs.written - byte_start,
        'family_statistics_or_model_complete': False,
        'context_or_location_evaluation': False,
    }
