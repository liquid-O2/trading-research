"""Declared exact profile representations and completed-bar source comparisons."""
from __future__ import annotations

from fractions import Fraction

from trading_research.errors import ContractError, IntegrityError
from trading_research.measurements.profiles import FrozenGrid, ProfileDefinition, bar_allocation_rows
from trading_research.research.auction_flow_anchor_trades import AtomicTrades, _integer
from trading_research.research.auction_flow_anchors import AuctionAnchor
from trading_research.research.auction_flow_measurements import SparseSideMass
from trading_research.research.auction_flow_profiles import MassView, geometry, side_geometry, transform_mass, view_sparse


VERSION = 'auction-flow-declared-anchor-profile-views-v1'
BAR_PROXIES = ('equal_inclusive_rows', 'continuous_overlap', 'pin066_source', 'pin066_corrected', 'close', 'hlc3')


def profile_catalogue(profile, *, anchor, known_at_ns, coverage_complete):
    if (type(profile) is not SparseSideMass or type(anchor) is not AuctionAnchor
            or not _integer(known_at_ns) or known_at_ns < anchor.selection_known_at_ns
            or profile.row_ticks != 1 or profile.origin_ticks != 0):
        raise ContractError('exact one-tick anchor mass and actual availability required')
    if not profile.rows:
        return {'version': VERSION, 'variants': (), 'reason': 'no_observed_priced_mass',
            'unpriced': tuple(profile.unpriced), 'coverage_complete': coverage_complete}
    low, high = min(profile.rows), max(profile.rows)
    views = []
    def make(width, origin, name):
        grid = FrozenGrid(origin, width, (low - origin) // width, (high - origin) // width,
            name, known_at_ns, max_rows=profile.maximum_cells)
        return view_sparse(profile, coordinate_identity=anchor.contract_key, grid=grid, coverage_complete=coverage_complete)
    original = make(1, 0, 'current-prefix-one-tick-origin-zero-v1')
    def add(name, view, fraction=Fraction(7, 10), poc_tie='lower', value_tie='upper'):
        definition = ProfileDefinition(name, anchor_kind=anchor.kind, value_fraction=fraction,
            poc_tie=poc_tie, value_tie=value_tie)
        views.append({'variant': name, 'grid': view.grid, 'representation': view.representation,
            'geometry': geometry(view, definition=definition), 'side_geometry': side_geometry(view)})
    for fraction in (Fraction(17, 25), Fraction(7, 10)):
        add('source-one-tick-value-' + str(fraction), original, fraction)
    for value_tie in ('lower', 'both'):
        add('value70-expansion-tie-' + value_tie, original, value_tie=value_tie)
    add('value70-poc-tie-upper', original, poc_tie='upper')
    for width in (2, 4, 8):
        for origin in (0, 1):
            add(f'value70-width{width}-origin{origin}', make(width, origin, f'current-prefix-width{width}-origin{origin}-v1'))
    for scale in (1, 2, 4):
        add(f'value70-triangular-scale{scale}', transform_mass(original, kind='triangular', scale=scale))
    return {'version': VERSION, 'anchor_id': anchor.id, 'known_at_ns': known_at_ns, 'variants': tuple(views),
        'grid_selection': 'extent of observed current-prefix mass at this actual feature cut',
        'future_target_rule': 'reuse this frozen prefix grid, preserve all low/high overflow',
        'all_raw_mass_retained_by_input_profile': True, 'cartesian_parameter_search': False}


def bar_proxy_atoms(atoms, *, anchor, grid, variant, coverage_complete):
    if (type(atoms) is not tuple or len(atoms) > 1_000_000 or type(anchor) is not AuctionAnchor
            or type(grid) is not FrozenGrid or variant not in BAR_PROXIES or type(coverage_complete) is not bool):
        raise ContractError('admitted completed-bar atoms, frozen grid and named proxy required')
    bars, unpriced_without_bar = [], 0
    end = last_order = None
    for atom in atoms:
        if (type(atom) is not AtomicTrades or atom.start_source_order is not None
                or any(getattr(atom, k) != getattr(anchor, k) for k in ('root', 'contract_key', 'instrument_id', 'source_lineage'))
                or not any(a <= atom.start_ns < atom.end_ns <= b for a, b in anchor.spans)
                or end is not None and atom.start_ns < end or atom.known_at_ns > grid.known_at
                or atom.first is not None and last_order is not None and atom.first[1] <= last_order):
            raise IntegrityError('bar proxy members lost actual identity, complete-bar boundaries or availability')
        end = atom.end_ns
        if atom.last is not None:
            last_order = atom.last[1]
        if atom.first_priced is None:
            unpriced_without_bar += sum(atom.unpriced)
            continue
        bars.append((atom.first_priced[2], atom.high[0], atom.low[0], atom.last_priced[2],
            atom.paths[0].buy + atom.paths[0].sell + atom.paths[0].unknown - sum(atom.unpriced), sum(atom.unpriced)))
    allocation = bar_allocation_rows(tuple(bars), grid=grid, variant=variant)
    unpriced = tuple(allocation['unpriced'][i] + (unpriced_without_bar if i == 2 else 0) for i in range(3))
    view = MassView(anchor.contract_key, grid, allocation['rows'], allocation['low_overflow'], allocation['high_overflow'],
        unpriced, coverage_complete, (('bar_proxy', variant),))
    result = geometry(view, definition=ProfileDefinition('bar-proxy-' + variant, anchor_kind=anchor.kind))
    return {'version': VERSION, 'variant': variant, 'members': tuple(a.evidence_id for a in atoms), 'geometry': result,
        'allocation': allocation, 'unpriced_without_supported_bar_geometry': unpriced_without_bar,
        'retained_total_mass': view.total_mass, 'source_flat_bar_lost_mass': allocation['source_flat_bar_lost_mass'],
        'pin066_source_bottom_bin_poc': None if variant != 'pin066_source' or result['scalar_poc'] == grid.lower_row else result['scalar_poc'],
        'side_interpretation': 'bar-body trend and symmetric wick allocation for PIN066; unknown side for other proxies',
        'observed_ohlc_geometry_rule': 'first/last priced actual trade and exact observed extrema; unpriced mass retained separately'}


class PIN069BarClose:
    """Disclosed first/new-high reset with bar-close times full bar volume.

    The geometric origin is the completed bar's start. Its selection clock is
    the actual bar publication, including the first bar. High tracking changes
    only on a reset, matching the retained literal source comparator.
    """
    def __init__(self, source_window):
        if type(source_window) is not AuctionAnchor or source_window.variant != 'source_06_09_fixed_utc_minus4':
            raise ContractError('the disclosed fixed UTC-4 06–09 source window is required')
        self.window = source_window
        self.high = self.origin = self.selection_known = self.last_end = self.last_order = None
        self.volume = self.pv = 0
        self.unsupported_volume = 0
        self.members = []
        self.complete = True
        self.selection_history_complete = True
        self.high_state_unresolved = False
        self._failed = False

    def add(self, atom):
        if self._failed:
            raise IntegrityError('a failed PIN069 calculation cannot publish or resume')
        try:
            if (type(atom) is not AtomicTrades or atom.start_source_order is not None
                    or any(getattr(atom, k) != getattr(self.window, k) for k in ('root', 'contract_key', 'instrument_id', 'source_lineage'))
                    or self.last_end is not None and atom.start_ns < self.last_end
                    or atom.first is not None and self.last_order is not None and atom.first[1] <= self.last_order):
                raise IntegrityError('source reanchor requires the same actual ordered completed bars')
            within = any(a <= atom.start_ns < b for a, b in self.window.spans)
            self.selection_history_complete &= atom.source_complete and atom.coordinate_complete and not atom.unpriced_prints
            if self.last_end is not None and atom.start_ns != self.last_end:
                self.selection_history_complete = False
            if atom.high is None or atom.last_priced is None or self.high_state_unresolved:
                # Quiet/no-price bars do not fabricate a new-high trigger.
                self.complete = False
                self.high_state_unresolved |= within or self.high is None
                self.unsupported_volume += atom.paths[0].buy + atom.paths[0].sell + atom.paths[0].unknown
                self.last_end = atom.end_ns
                if atom.last is not None:
                    self.last_order = atom.last[1]
                self.members.append(atom.evidence_id)
                return {'status': 'unavailable_source_high_state' if self.high_state_unresolved else 'unavailable_bar_high_or_close',
                    'bar': atom.evidence_id, 'known_at_ns': atom.known_at_ns, 'source_recovery_inferred': False}
            reset = self.high is None or within and atom.high[0] > self.high
            if reset:
                self.high, self.origin, self.selection_known = atom.high[0], atom.start_ns, max(atom.known_at_ns, self.window.selection_known_at_ns)
                self.volume = self.pv = self.unsupported_volume = 0
                self.members, self.complete = [], True
            elif self.last_end is not None and atom.start_ns != self.last_end:
                self.complete = False
            self.complete &= self.selection_history_complete and atom.source_complete and atom.coordinate_complete and not atom.unpriced_prints
            volume = atom.paths[0].buy + atom.paths[0].sell + atom.paths[0].unknown
            self.volume += volume
            self.pv += atom.last_priced[2] * volume
            self.members.append(atom.evidence_id)
            self.last_end = atom.end_ns
            if atom.last is not None:
                self.last_order = atom.last[1]
            return {'version': VERSION, 'variant': 'PIN069_completed_bar_close_full_volume', 'reset': reset,
                'bar': atom.evidence_id, 'origin_ns': self.origin, 'selection_known_at_ns': self.selection_known,
                'known_at_ns': max(self.selection_known, atom.known_at_ns), 'source_window_contains_bar_start': within,
                'sum_bar_close_volume': self.pv, 'bar_volume': self.volume,
                'observed_bar_close_vwap_ticks': Fraction(self.pv, self.volume) if self.volume else None,
                'complete_bar_close_vwap_ticks': Fraction(self.pv, self.volume) if self.complete and self.volume else None,
                'history_complete': self.complete, 'unsupported_bar_volume': self.unsupported_volume,
                'selection_history_complete': self.selection_history_complete,
                'members': tuple(self.members), 'geometry_origin_is_publication_time': False}
        except BaseException:
            self._failed = True
            raise
