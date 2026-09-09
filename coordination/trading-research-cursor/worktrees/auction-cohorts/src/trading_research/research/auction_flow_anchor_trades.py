"""Exact composition of admitted trade atoms, without replaying annual tape.

The atom boundary is scientific: it must already be split at a selected
anchor, bracket or rolling cut. A minute containing a causal mid-minute event
cannot be used in its entirety. Source coverage and physical identity remain
explicit inputs from the registered source reader.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, localcontext
from fractions import Fraction

from trading_research.errors import ContractError, IntegrityError
from trading_research.measurements.vwap import exact_sqrt, weighted_quantile
from trading_research.research.auction_flow_anchors import AuctionAnchor, MINUTE_NS, ROLLING_MINUTES
from trading_research.research.auction_flow_measurements import SOURCE_FILTERS, SparseSideMass
from trading_research.research.auction_flow_windows import VERSION as TAPE_VERSION


VERSION = 'auction-flow-exact-anchor-trades-v1'


def _integer(value, *, minimum=0):
    return type(value) is int and value >= minimum


def _intervals(spans):
    """Unbounded-duration, bounded-input-size internal interval normalization."""
    result = []
    for a, b in spans:
        if result and a < result[-1][0]:
            raise IntegrityError('constituent interval order regressed')
        if result and a <= result[-1][1]:
            result[-1] = (result[-1][0], max(result[-1][1], b))
        else:
            result.append((a, b))
    return tuple(result)


def missing_intervals(intended, supplied):
    supplied = _intervals(supplied)
    missing = []
    index = 0
    for start, end in intended:
        cursor = start
        while index < len(supplied) and supplied[index][1] <= start:
            index += 1
        j = index
        while j < len(supplied) and supplied[j][0] < end:
            a, b = supplied[j]
            if cursor < a:
                missing.append((cursor, min(a, end)))
            cursor = max(cursor, min(b, end))
            j += 1
        if cursor < end:
            missing.append((cursor, end))
    return tuple(missing)


@dataclass(frozen=True)
class FlowPath:
    """Ordered zero-open path monoid; strict extrema preserve first attainment."""
    high: int = 0
    low: int = 0
    close: int = 0
    high_at_ns: int | None = None
    low_at_ns: int | None = None
    high_source_order: int | None = None
    low_source_order: int | None = None
    buy: int = 0
    sell: int = 0
    unknown: int = 0
    prints: int = 0
    excluded_prints: int = 0
    excluded_volume: int = 0

    @classmethod
    def from_record(cls, record, *, name, start_ns, end_ns):
        if record.get('filter') != name or record.get('open') != 0:
            raise IntegrityError('an exact constituent zero-open cohort is required')
        values = {name: record[name] for name in cls.__dataclass_fields__}
        result = cls(**values)
        if (any(not _integer(values[k]) for k in ('buy', 'sell', 'unknown', 'prints', 'excluded_prints', 'excluded_volume'))
                or any(type(values[k]) is not int for k in ('high', 'low', 'close'))
                or result.close != result.buy - result.sell
                or record.get('volume') != result.buy + result.sell + result.unknown
                or not result.low <= min(0, result.close) <= max(0, result.close) <= result.high):
            raise IntegrityError('constituent ordered path or side mass does not reconcile')
        for extrema in ('high', 'low'):
            at, order = values[extrema + '_at_ns'], values[extrema + '_source_order']
            if values[extrema] == 0:
                if at is not None or order is not None:
                    raise IntegrityError('an unchanged opening extremum has no invented event clock')
            elif not (_integer(at) and start_ns <= at < end_ns and _integer(order)):
                raise IntegrityError('constituent path extremum lost its exact event address')
        return result

    def then(self, other):
        if type(other) is not FlowPath:
            raise ContractError('ordered flow composition requires an exact path')
        high_from_second = self.close + other.high > self.high
        low_from_second = self.close + other.low < self.low
        return FlowPath(
            self.close + other.high if high_from_second else self.high,
            self.close + other.low if low_from_second else self.low,
            self.close + other.close,
            other.high_at_ns if high_from_second else self.high_at_ns,
            other.low_at_ns if low_from_second else self.low_at_ns,
            other.high_source_order if high_from_second else self.high_source_order,
            other.low_source_order if low_from_second else self.low_source_order,
            *(getattr(self, k) + getattr(other, k) for k in
              ('buy', 'sell', 'unknown', 'prints', 'excluded_prints', 'excluded_volume')))

    def record(self, *, name, coverage_complete, all_prints, all_volume):
        volume = self.buy + self.sell + self.unknown
        return {**asdict(self), 'filter': name, 'open': 0, 'volume': volume,
            'coverage_complete': coverage_complete,
            'observed_signed_lower': self.close - self.unknown,
            'observed_signed_upper': self.close + self.unknown,
            'true_signed_lower': self.close - self.unknown if coverage_complete else None,
            'true_signed_upper': self.close + self.unknown if coverage_complete else None,
            'known_side_fraction': Fraction(self.buy + self.sell, volume) if volume else None,
            'count_occupancy': Fraction(self.prints, all_prints) if all_prints else None,
            'volume_occupancy': Fraction(volume, all_volume) if all_volume else None,
            'empty_observed_cohort': coverage_complete and not self.prints,
            'ordering_basis': 'original source order, concatenated within one retained physical source lineage'}


@dataclass(frozen=True)
class AtomicTrades:
    root: str
    contract_key: str
    instrument_id: int
    source_lineage: str
    evidence_id: str
    start_ns: int
    end_ns: int
    known_at_ns: int
    source_complete: bool
    coordinate_complete: bool
    start_source_order: int | None
    paths: tuple
    rows: tuple
    unpriced: tuple
    unpriced_prints: int
    # Each point is (event time, source order, price or None, source key, row).
    first: tuple | None
    last: tuple | None
    first_priced: tuple | None
    last_priced: tuple | None
    high: tuple | None
    low: tuple | None
    sum_squared_sizes: int

    @classmethod
    def from_record(cls, record, *, root, contract_key, source_lineage, evidence_id, start_source_order=None):
        if (record.get('version') != TAPE_VERSION or root not in ('NQ', 'ES')
                or type(contract_key) is not str or not contract_key.startswith(root + ':')
                or any(type(s) is not str or not s for s in (source_lineage, evidence_id))
                or not _integer(record.get('instrument_id'), minimum=1)
                or not _integer(record.get('event_start_ns')) or not _integer(record.get('event_end_ns'))
                or not record['event_start_ns'] < record['event_end_ns'] < 2**63 - 1_000_000_000
                or not _integer(record.get('known_at_ns'))
                or not 0 <= record['known_at_ns'] - record['event_end_ns'] <= 1_000_000_000
                or any(type(record.get(k)) is not bool for k in ('source_coverage_complete', 'coordinate_complete'))
                or start_source_order is not None and not _integer(start_source_order)):
            raise ContractError('admitted exact trade atom, coordinate, source lineage and evidence required')
        start, end = record['event_start_ns'], record['event_end_ns']
        paths = tuple(FlowPath.from_record(record['flows'][name], name=name, start_ns=start, end_ns=end)
                      for name in SOURCE_FILTERS)
        all_path = paths[0]
        mass = record['sparse_profile']
        rows = tuple(tuple(r) for r in mass['rows'])
        unpriced = tuple(mass['unpriced_buy_sell_unknown'])
        if (mass.get('row_ticks') != 1 or mass.get('origin_ticks') != 0
                or len(unpriced) != 3 or any(not _integer(v) for v in unpriced)
                or len(rows) > 1_000_000
                or any(len(r) != 4 or not _integer(r[0], minimum=1) or r[0] >= 2**53
                    or any(not _integer(v) for v in r[1:]) or not sum(r[1:]) for r in rows)
                or any(rows[i][0] >= rows[i + 1][0] for i in range(len(rows) - 1))
                or any(sum(r[i + 1] for r in rows) + unpriced[i] != getattr(all_path, name)
                       for i, name in enumerate(('buy', 'sell', 'unknown')))
                or mass.get('total_volume') != all_path.buy + all_path.sell + all_path.unknown
                or record.get('prints') != all_path.prints
                or not _integer(record.get('unpriced_prints')) or record['unpriced_prints'] > all_path.prints
                or not _integer(record.get('sum_squared_trade_sizes'))):
            raise IntegrityError('exact sparse atom mass, grid, sizes or side channels changed')
        if any(p.prints + p.excluded_prints != all_path.prints
               or p.buy + p.sell + p.unknown + p.excluded_volume != mass['total_volume'] for p in paths):
            raise IntegrityError('fixed cohort population does not reconcile with all trades')

        def point(name):
            p = record[name]
            if p is None:
                return None
            if (not _integer(p.get('event_ns')) or not start <= p['event_ns'] < end
                    or not _integer(p.get('source_order')) or not _integer(p.get('source_row'))
                    or type(p.get('source_key')) is not str or not p['source_key']
                    or type(p.get('price_valid')) is not bool
                    or (p.get('price_ticks') is None) != (not p['price_valid'])
                    or p['price_valid'] and (not _integer(p['price_ticks'], minimum=1) or p['price_ticks'] >= 2**53)
                    or p.get('known_at_ns') != p['event_ns'] + record['known_at_ns'] - end):
                raise IntegrityError('atom endpoint lost exact source address or price')
            return (p['event_ns'], p['source_order'], p['price_ticks'], p['source_key'], p['source_row'])

        first, last, first_priced, last_priced = (point(name) for name in
            ('first_trade', 'last_trade', 'first_priced_trade', 'last_priced_trade'))
        if (bool(all_path.prints) != (first is not None) or (first is None) != (last is None)
                or first is not None and (last[0] < first[0] or last[1] < first[1]
                    or start_source_order is not None and first[1] < start_source_order)
                or bool(rows) != (first_priced is not None) or (first_priced is None) != (last_priced is None)
                or first_priced is not None and (first_priced[2] is None or last_priced[2] is None)):
            raise IntegrityError('atom endpoints or explicit event cursor contradict the retained population')
        extremes = []
        for name in ('high', 'low'):
            price = record['observed_' + name + '_ticks']
            at = record['observed_' + name + '_at_ns']
            order = record['observed_' + name + '_source_order']
            if price is None:
                if rows or at is not None or order is not None:
                    raise IntegrityError('missing observed extremum contradicts priced mass')
                extremes.append(None)
            else:
                if (not rows or price != (rows[-1][0] if name == 'high' else rows[0][0])
                        or not _integer(at) or not start <= at < end or not _integer(order)):
                    raise IntegrityError('atom extremum must retain actual exact price and event clock')
                extremes.append((price, at, order))
        return cls(root, contract_key, record['instrument_id'], source_lineage, evidence_id,
            start, end, record['known_at_ns'], record['source_coverage_complete'], record['coordinate_complete'],
            start_source_order, paths, rows, unpriced, record['unpriced_prints'], first, last,
            first_priced, last_priced, *extremes, record['sum_squared_trade_sizes'])


def _join_paths(first, second):
    return tuple(a.then(b) for a, b in zip(first, second, strict=True))


def _adjust_mass(profile, atom, sign):
    for row, *amounts in atom.rows:
        if row not in profile.rows:
            if sign < 0 or len(profile.rows) >= profile.maximum_cells:
                raise IntegrityError('anchor price-mass removal or finite row capacity failed')
            profile.rows[row] = [0, 0, 0]
        current = profile.rows[row]
        for i, value in enumerate(amounts):
            current[i] += sign * value
            if current[i] < 0:
                raise IntegrityError('rolling removal produced negative exact side mass')
        if not any(current):
            del profile.rows[row]
    for i, value in enumerate(atom.unpriced):
        profile.unpriced[i] += sign * value
        if profile.unpriced[i] < 0:
            raise IntegrityError('rolling removal produced negative unpriced mass')
    path = atom.paths[0]
    profile.total += sign * (path.buy + path.sell + path.unknown)


class _FlowQueue:
    """Two-stack FIFO with amortized constant path composition per atom.

    The reverse stack accumulates oldest.then(next), since extrema composition
    is associative but not commutative. Sparse price mass is updated separately.
    """
    def __init__(self):
        self.incoming, self.outgoing = [], []

    def push(self, atom):
        paths = atom.paths if not self.incoming else _join_paths(self.incoming[-1][1], atom.paths)
        self.incoming.append((atom, paths))

    def _reverse(self):
        if not self.outgoing:
            while self.incoming:
                atom, _ = self.incoming.pop()
                paths = atom.paths if not self.outgoing else _join_paths(atom.paths, self.outgoing[-1][1])
                self.outgoing.append((atom, paths))

    def peek(self):
        self._reverse()
        return self.outgoing[-1][0] if self.outgoing else None

    def pop(self):
        self._reverse()
        if not self.outgoing:
            raise ContractError('cannot remove an absent rolling constituent')
        return self.outgoing.pop()[0]

    def paths(self):
        a = self.outgoing[-1][1] if self.outgoing else tuple(FlowPath() for _ in SOURCE_FILTERS)
        b = self.incoming[-1][1] if self.incoming else tuple(FlowPath() for _ in SOURCE_FILTERS)
        return _join_paths(a, b)

    def atoms(self):
        yield from (pair[0] for pair in reversed(self.outgoing))
        yield from (pair[0] for pair in self.incoming)


def dispersion(profile):
    """Exact moments and quantiles; only the square root uses decimal rounding."""
    base = profile.weighted_price()
    weighted = tuple((price, sum(mass)) for price, mass in sorted(profile.rows.items()))
    median = weighted_quantile(weighted, Fraction(1, 2))
    mad = None if median is None else weighted_quantile(tuple((abs(p - median), q) for p, q in weighted), Fraction(1, 2))
    mean = base['vwap_ticks']
    sd = exact_sqrt(base['variance_ticks_squared'])
    bands = None
    if sd is not None:
        with localcontext() as context:
            context.prec = 50
            center = Decimal(mean.numerator) / Decimal(mean.denominator)
            bands = {str(k): tuple(str(v) for v in (center - sd * Decimal(k.numerator) / Decimal(k.denominator),
                                                   center + sd * Decimal(k.numerator) / Decimal(k.denominator)))
                     for k in (Fraction(1), Fraction(2), Fraction(5, 2), Fraction(3))}
    return {**base, 'weighted_median_ticks': median, 'weighted_mad_ticks': mad,
        'scaled_mad_ticks_7413_over_5000': None if mad is None else mad * Fraction(7413, 5000),
        'sd_ticks_decimal50': None if sd is None else str(sd), 'sd_bands_ticks_decimal50': bands,
        'sd_evaluation': '50-significant-digit decimal evaluation of the retained exact rational variance',
        'percent_bands_ticks': None if mean is None else {str(p): (mean - abs(mean) * p, mean + abs(mean) * p)
            for p in (Fraction(1, 100), Fraction(1, 40), Fraction(3, 100))},
        'unpriced_volume_excluded_from_price_moments': sum(profile.unpriced)}


class AnchorTrades:
    """One fixed/composite formation with compact exact primitive state."""
    def __init__(self, anchor, *, maximum_atoms=1_000_000, maximum_profile_cells=250000):
        if (type(anchor) is not AuctionAnchor or not _integer(maximum_atoms, minimum=1)
                or maximum_atoms > 1_000_000):
            raise ContractError('explicit admitted anchor and bounded constituent count required')
        self.anchor, self.maximum_atoms = anchor, maximum_atoms
        self.profile = SparseSideMass(maximum_cells=maximum_profile_cells)
        self.paths = tuple(FlowPath() for _ in SOURCE_FILTERS)
        self.supplied, self.failed_source, self.failed_coordinate = [], [], []
        self.members = []
        self.first = self.last = self.first_priced = self.last_priced = None
        self.high = self.low = None
        self.unpriced_prints = self.sum_squared_sizes = 0
        self.known_at = 0
        self.delay = None
        self._failed = False

    def _check_atom(self, atom):
        if type(atom) is not AtomicTrades:
            raise ContractError('an exact admitted immutable trade atom is required')
        if any(getattr(atom, k) != getattr(self.anchor, k) for k in
               ('root', 'contract_key', 'instrument_id', 'source_lineage')):
            raise IntegrityError('anchor cannot merge source acquisitions or physical contracts')
        if len(self.members) >= self.maximum_atoms:
            raise ContractError('anchor constituent count exceeds its registered bound')
        if (not any(a <= atom.start_ns < atom.end_ns <= b for a, b in self.anchor.spans)
                or self.supplied and atom.start_ns < self.supplied[-1][1]):
            raise IntegrityError('atom overlaps prior membership or crosses a scientific anchor boundary; split actual events first')
        expected_cursor = self.anchor.start_source_order if atom.start_ns == self.anchor.start_ns else None
        if atom.start_source_order != expected_cursor:
            raise IntegrityError('a causal event start requires its exact admitted source-order cut')
        if self.last is not None and atom.first is not None and (atom.first[0] < self.last[0] or atom.first[1] <= self.last[1]):
            raise IntegrityError('anchor constituents duplicate or regress original physical event order')
        if self.delay is not None and atom.known_at_ns - atom.end_ns != self.delay:
            raise IntegrityError('one anchor cannot mix publication-delay scenarios')

    def add(self, atom):
        if self._failed:
            raise IntegrityError('a failed anchor cannot resume or publish partial state')
        try:
            self._check_atom(atom)
            _adjust_mass(self.profile, atom, 1)
            self.delay = atom.known_at_ns - atom.end_ns
            self.paths = _join_paths(self.paths, atom.paths)
            self.supplied.append((atom.start_ns, atom.end_ns))
            if not atom.source_complete:
                self.failed_source.append((atom.start_ns, atom.end_ns))
            if not atom.coordinate_complete:
                self.failed_coordinate.append((atom.start_ns, atom.end_ns))
            self.members.append(atom.evidence_id)
            self.known_at = max(self.known_at, atom.known_at_ns)
            self.unpriced_prints += atom.unpriced_prints
            self.sum_squared_sizes += atom.sum_squared_sizes
            self.first = self.first or atom.first
            self.last = atom.last or self.last
            self.first_priced = self.first_priced or atom.first_priced
            self.last_priced = atom.last_priced or self.last_priced
            if atom.high is not None and (self.high is None or atom.high[0] > self.high[0]):
                self.high = atom.high
            if atom.low is not None and (self.low is None or atom.low[0] < self.low[0]):
                self.low = atom.low
        except BaseException:
            self._failed = True
            raise

    def record(self, *, event_end_ns, decision_cut_ns, latency_ns):
        if self._failed:
            raise IntegrityError('a failed anchor cannot publish partial state')
        if self.delay is not None and latency_ns != self.delay:
            raise ContractError('anchor publication must use the constituent source-delay scenario')
        known_at = max(self.known_at, self.anchor.publication_at(event_end_ns, latency_ns=latency_ns))
        if (not _integer(decision_cut_ns) or decision_cut_ns < known_at
                or self.supplied and event_end_ns < self.supplied[-1][1]):
            raise ContractError('anchor output is unavailable at this observation/selection cut')
        intended = self.anchor.prefix_spans(event_end_ns)
        missing = missing_intervals(intended, self.supplied)
        source_complete = bool(intended) and not missing and not self.failed_source
        coordinate_complete = bool(intended) and not missing and not self.failed_coordinate
        complete = source_complete and coordinate_complete
        all_path = self.paths[0]
        volume = all_path.buy + all_path.sell + all_path.unknown
        if self.profile.total != volume:
            raise IntegrityError('anchor path volume and all priced/unpriced mass differ')
        exposure = sum(b - a for a, b in intended)
        return {'version': VERSION, 'anchor': self.anchor.record(), 'observation_end_ns': event_end_ns,
            'known_at_ns': known_at, 'decision_cut_ns': decision_cut_ns, 'formation_final': event_end_ns == self.anchor.end_ns,
            'intended_prefix_spans': intended, 'supplied_spans': _intervals(self.supplied), 'missing_spans': missing,
            'source_failure_spans': _intervals(self.failed_source), 'coordinate_failure_spans': _intervals(self.failed_coordinate),
            'source_coverage_complete': source_complete, 'coordinate_complete': coordinate_complete,
            'flow_history_complete': complete, 'price_history_complete': complete and not self.unpriced_prints,
            'members': tuple(self.members), 'prints': all_path.prints, 'unpriced_prints': self.unpriced_prints,
            'first_trade': self.first, 'last_trade': self.last, 'first_priced_trade': self.first_priced,
            'last_priced_trade': self.last_priced, 'high_price_at_order': self.high, 'low_price_at_order': self.low,
            'sum_squared_trade_sizes': self.sum_squared_sizes,
            'formation_exposure_ns': exposure,
            'count_intensity_per_second': Fraction(all_path.prints * 10**9, exposure) if complete and exposure else None,
            'volume_intensity_per_second': Fraction(volume * 10**9, exposure) if complete and exposure else None,
            'flows': {name: path.record(name=name, coverage_complete=complete, all_prints=all_path.prints, all_volume=volume)
                for name, path in zip(SOURCE_FILTERS, self.paths, strict=True)},
            'sparse_profile': self.profile.record(coverage_complete=complete), 'weighted_price': dispersion(self.profile),
            'empty_observed_formation': complete and not all_path.prints,
            'marked_size_and_interarrival_quantiles': 'require exact retained event populations; constituent quantiles are not averaged'}


class RollingAnchorTrades:
    """Moving exact membership, with sparse additions/removals and path FIFO."""
    def __init__(self, *, minutes, root, contract_key, instrument_id, source_lineage,
                 source_versions, maximum_atoms=20000, maximum_profile_cells=250000):
        if type(minutes) is not int or minutes not in ROLLING_MINUTES:
            raise ContractError('registered rolling formation length required')
        if (root not in ('NQ', 'ES') or type(contract_key) is not str or not contract_key.startswith(root + ':')
                or not _integer(instrument_id, minimum=1) or type(source_lineage) is not str or not source_lineage
                or type(source_versions) is not tuple or not source_versions
                or any(type(s) is not str or not s for s in source_versions)):
            raise ContractError('one exact coordinate and original source lineage required for rolling membership')
        if not _integer(maximum_atoms, minimum=1) or maximum_atoms > 20000:
            raise ContractError('bounded rolling constituent count required')
        self.root, self.contract_key, self.instrument_id = root, contract_key, instrument_id
        self.source_lineage, self.source_versions = source_lineage, source_versions
        self.minutes, self.width, self.maximum_atoms = minutes, minutes * MINUTE_NS, maximum_atoms
        self.maximum_profile_cells = maximum_profile_cells
        self.queue = _FlowQueue()
        self.profile = SparseSideMass(maximum_cells=maximum_profile_cells)
        self.last_end = self.last_order = self.cut = None
        self.delay = None
        self.count = 0
        self._failed = False

    def add(self, atom):
        if self._failed:
            raise IntegrityError('a failed rolling calculation cannot resume')
        try:
            if (type(atom) is not AtomicTrades or atom.start_source_order is not None
                    or any(getattr(atom, k) != getattr(self, k) for k in
                        ('root', 'contract_key', 'instrument_id', 'source_lineage'))
                    or self.last_end is not None and atom.start_ns < self.last_end
                    or self.cut is not None and atom.start_ns < self.cut
                    or atom.first is not None and self.last_order is not None and atom.first[1] <= self.last_order
                    or self.delay is not None and atom.known_at_ns - atom.end_ns != self.delay
                    or self.count >= self.maximum_atoms):
                raise IntegrityError('rolling atom identity/order/cursor or bounded membership is invalid')
            _adjust_mass(self.profile, atom, 1)
            self.delay = atom.known_at_ns - atom.end_ns
            self.queue.push(atom)
            self.count += 1
            self.last_end = atom.end_ns
            if atom.last is not None:
                self.last_order = atom.last[1]
        except BaseException:
            self._failed = True
            raise

    def record(self, *, event_end_ns, decision_cut_ns, latency_ns):
        from trading_research.research.auction_flow_anchors import rolling_anchor

        if self._failed:
            raise IntegrityError('a failed rolling calculation cannot publish')
        if (not _integer(event_end_ns, minimum=self.width) or self.cut is not None and event_end_ns < self.cut
                or self.delay is not None and latency_ns != self.delay
                or self.last_end is not None and self.last_end > event_end_ns):
            raise ContractError('rolling cut cannot contain future atoms or regress')
        anchor = rolling_anchor(minutes=self.minutes, event_end_ns=event_end_ns, selection_known_at_ns=event_end_ns,
            source_versions=self.source_versions, **{k: getattr(self, k) for k in
                ('root', 'contract_key', 'instrument_id', 'source_lineage')})
        # Validate publication before any destructive downdate.
        expected_known = anchor.publication_at(event_end_ns, latency_ns=latency_ns)
        if not _integer(decision_cut_ns) or decision_cut_ns < expected_known:
            raise ContractError('rolling result is unavailable at its actual publication cut')
        try:
            self.trim(event_end_ns=event_end_ns)
            value = AnchorTrades(anchor, maximum_atoms=self.maximum_atoms, maximum_profile_cells=self.maximum_profile_cells)
            # Metadata is O(active atoms); mass and flow do not replay here.
            atoms = tuple(self.queue.atoms())
            value.paths = self.queue.paths()
            value.profile = self.profile
            value.delay = self.delay
            value.supplied = [(a.start_ns, a.end_ns) for a in atoms]
            value.failed_source = [(a.start_ns, a.end_ns) for a in atoms if not a.source_complete]
            value.failed_coordinate = [(a.start_ns, a.end_ns) for a in atoms if not a.coordinate_complete]
            value.members = [a.evidence_id for a in atoms]
            value.known_at = max((a.known_at_ns for a in atoms), default=0)
            value.unpriced_prints = sum(a.unpriced_prints for a in atoms)
            value.sum_squared_sizes = sum(a.sum_squared_sizes for a in atoms)
            for name in ('first', 'first_priced'):
                setattr(value, name, next((getattr(a, name) for a in atoms if getattr(a, name) is not None), None))
            for name in ('last', 'last_priced'):
                setattr(value, name, next((getattr(a, name) for a in reversed(atoms) if getattr(a, name) is not None), None))
            highs, lows = [a.high for a in atoms if a.high is not None], [a.low for a in atoms if a.low is not None]
            value.high = max(highs, key=lambda p: p[0], default=None)
            value.low = min(lows, key=lambda p: p[0], default=None)
            result = value.record(event_end_ns=event_end_ns, decision_cut_ns=decision_cut_ns, latency_ns=latency_ns)
            self.cut = event_end_ns
            return result
        except BaseException:
            self._failed = True
            raise

    def trim(self, *, event_end_ns):
        """Advance bounded working membership without publishing statistics."""
        if self._failed:
            raise IntegrityError('a failed rolling calculation cannot advance')
        if (not _integer(event_end_ns, minimum=self.width) or self.cut is not None and event_end_ns < self.cut
                or self.last_end is not None and self.last_end > event_end_ns):
            raise ContractError('rolling membership cut cannot regress or contain future atoms')
        try:
            start = event_end_ns - self.width
            while self.queue.peek() is not None and self.queue.peek().end_ns <= start:
                _adjust_mass(self.profile, self.queue.pop(), -1)
                self.count -= 1
            first = self.queue.peek()
            if first is not None and first.start_ns < start:
                raise IntegrityError('rolling left edge crosses an atom; split original events at this exact cut')
            self.cut = event_end_ns
        except BaseException:
            self._failed = True
            raise
