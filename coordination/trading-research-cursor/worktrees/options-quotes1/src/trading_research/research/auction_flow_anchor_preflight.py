"""Registered real-source reconciliation of the new exact anchor consumers."""
from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timezone
from fractions import Fraction
import time
from zoneinfo import ZoneInfo

from trading_research.errors import IntegrityError
from trading_research.measurements.profiles import FrozenGrid
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.research.auction_flow_anchors import AuctionAnchor, MINUTE_NS, ROLLING_MINUTES, named_clock_anchors
from trading_research.research.auction_flow_anchor_trades import AnchorTrades, AtomicTrades, FlowPath, RollingAnchorTrades
from trading_research.research.auction_flow_anchor_tpo import AnchorTPO, BRACKET_MINUTES
from trading_research.research.auction_flow_anchor_profiles import BAR_PROXIES, PIN069BarClose, bar_proxy_atoms, profile_catalogue
from trading_research.research.auction_flow_measurements import SOURCE_FILTERS
from trading_research.research.auction_flow_storage import read_series_tables
from trading_research.research.auction_flow_windows import TapeWindow


VERSION = 'auction-flow-actual-anchor-composition-check-v1'


def _same(actual, expected):
    """Compare live tuples/Fractions with JSON lists and tagged exact values."""
    return canonical_json(actual) == canonical_json(expected)


def _compare_tape(aggregate, literal):
    count = 0
    for name in SOURCE_FILTERS:
        for key in FlowPath.__dataclass_fields__:
            if not _same(aggregate['flows'][name][key], literal['flows'][name][key]):
                raise IntegrityError(f'anchor composition differs from original ordered tape: {name}.{key}')
            count += 1
    for key in ('sparse_profile', 'prints', 'unpriced_prints', 'sum_squared_trade_sizes', 'price_history_complete', 'flow_history_complete'):
        if not _same(aggregate[key], literal[key]):
            raise IntegrityError(f'anchor composition differs from original tape population/mass: {key}')
        count += 1
    for key, value in literal['weighted_price'].items():
        if not _same(aggregate['weighted_price'][key], value):
            raise IntegrityError(f'anchor exact weighted price differs from original tape: {key}')
        count += 1
    for key in ('high', 'low'):
        value = None if literal['observed_' + key + '_ticks'] is None else (
            literal['observed_' + key + '_ticks'], literal['observed_' + key + '_at_ns'], literal['observed_' + key + '_source_order'])
        if not _same(aggregate[key + '_price_at_order'], value):
            raise IntegrityError('anchor changed the exact original price extremum or first attainment clock')
        count += 1
    return count


def check_anchor_unit(measured, unit, *, measurement_reference, trade_storage, calendar, outputs):
    """Every admitted full-window atom, all three TPO widths and rolling suffixes.

    These resource windows check composition and representations. Named clocks
    matching a full window are reported explicitly; the gap-hour arithmetic
    check is not silently relabelled a general formation or family statistic.
    """
    cpu, results, excluded, replay = {}, [], [], {}
    start, end, cut = measured['event_start_ns'], measured['event_end_ns'], measured['known_at_ns']
    latency = cut - end
    day = date.fromisoformat(unit['cash_date']) if unit.get('cash_date') else datetime.fromtimestamp(
        end // 10**9, timezone.utc).astimezone(ZoneInfo('America/New_York')).date()
    byte_start = outputs.written
    for instrument in measured['instruments']:
        identity = instrument['coordinate']
        raw_id = instrument['instrument_id']
        if not identity['complete']:
            excluded.append({'instrument_id': raw_id, 'coordinate': identity,
                'prints': instrument['whole_window']['prints'], 'volume': instrument['whole_window']['flows']['all']['volume'],
                'reason': 'full requested formation does not retain one completely supported physical coordinate',
                'original_measurements_and_failure_population_retained': True})
            continue
        scope = dict(root=unit['root'], instrument_id=raw_id, contract_key=identity['contract_key'], source_lineage=unit['source_path'])
        clocks = named_clock_anchors(day=day, cut_ns=cut, calendar=calendar, **scope)
        matches = tuple(a for a in clocks['anchors'] if a.spans == ((start, end),))
        selected = matches[0] if matches else AuctionAnchor('registered_source_window_composition_check', 'event',
            spans=((start, end),), selection_known_at_ns=cut,
            source_versions=(unit['source_metadata_version'],), selection_evidence=digest(unit), **scope)
        selected = replace(selected, source_versions=tuple(sorted(set(selected.source_versions + (
            measured['coordinate_manifest_version'], unit['source_metadata_version'])))))
        began = time.process_time()
        atoms = tuple(AtomicTrades.from_record(row['trade'], root=unit['root'], contract_key=identity['contract_key'],
            source_lineage=unit['source_path'], evidence_id=digest({'measurement': measurement_reference['sha256'],
                'instrument_id': raw_id, 'atomic_bin': row['bin']})) for row in instrument['atomic_windows'])
        cpu['atom_validation_and_binding'] = cpu.get('atom_validation_and_binding', 0.0) + time.process_time() - began
        began = time.process_time()
        fixed = AnchorTrades(selected)
        tpos = {m: AnchorTPO(selected, bracket_minutes=m) for m in BRACKET_MINUTES}
        for atom in atoms:
            fixed.add(atom)
            for tpo in tpos.values():
                tpo.add(atom)
        cpu['fixed_path_mass_and_tpo_updates'] = cpu.get('fixed_path_mass_and_tpo_updates', 0.0) + time.process_time() - began
        began = time.process_time()
        aggregate = fixed.record(event_end_ns=end, decision_cut_ns=cut, latency_ns=latency)
        tpo_values = {str(m): tpo.record(event_end_ns=end, decision_cut_ns=cut, latency_ns=latency) for m, tpo in tpos.items()}
        cpu['fixed_exact_statistics_and_tpo_finalization'] = cpu.get('fixed_exact_statistics_and_tpo_finalization', 0.0) + time.process_time() - began
        began = time.process_time()
        comparison = _compare_tape(aggregate, instrument['whole_window'])
        for minutes, result in tpo_values.items():
            literal = next(v for v in instrument['time_at_price']['tpo'] if v['bracket_width_ns'] == int(minutes) * MINUTE_NS)
            observed = tuple((row, tuple(i for i in range(len(result['bracket_schedule'])) if bits & (1 << i)))
                             for row, _, bits in result['rows'])
            if not _same(observed, literal['row_bracket_incidence']):
                raise IntegrityError('atomic TPO incidence differs from the complete separately accumulated actual raw trade visits')
        ib = instrument['time_at_price']['initial_balance']
        if end - start >= 60 * MINUTE_NS:
            new_ib = tpo_values['30']['initial_balance']['60']
            if ((None if new_ib['high'] is None else new_ib['high'][0]) != ib['observed_high_ticks']
                    or (None if new_ib['low'] is None else new_ib['low'][0]) != ib['observed_low_ticks']):
                raise IntegrityError('initial balance lost the actual raw trade extremes')
        cpu['full_anchor_and_tpo_reference_comparison'] = cpu.get('full_anchor_and_tpo_reference_comparison', 0.0) + time.process_time() - began
        began = time.process_time()
        profiles = profile_catalogue(fixed.profile, anchor=selected, known_at_ns=cut,
            coverage_complete=aggregate['price_history_complete'])
        proxies = ()
        if fixed.profile.rows:
            grid = FrozenGrid(0, 1, min(fixed.profile.rows), max(fixed.profile.rows), 'complete-observed-comparison-grid-v1', cut,
                max_rows=fixed.profile.maximum_cells)
            proxies = tuple(bar_proxy_atoms(atoms, anchor=selected, grid=grid, variant=variant,
                coverage_complete=aggregate['price_history_complete']) for variant in BAR_PROXIES)
        cpu['full_profile_and_bar_proxy_catalogue'] = cpu.get('full_profile_and_bar_proxy_catalogue', 0.0) + time.process_time() - began
        began = time.process_time()
        rolling_values = {}
        for minutes in ROLLING_MINUTES:
            if minutes * MINUTE_NS > end - start:
                continue
            rolling = RollingAnchorTrades(minutes=minutes, source_versions=selected.source_versions, **scope)
            # Advance at the registered one-minute atom cadence. Unrequested
            # intermediate reports do not repeat geometry/JSON computation.
            for atom in atoms:
                rolling.add(atom)
                rolling.trim(event_end_ns=atom.end_ns)
            result = rolling.record(event_end_ns=end, decision_cut_ns=cut, latency_ns=latency)
            rolling_values[str(minutes)] = result
            replay[(raw_id, minutes)] = (TapeWindow(instrument_id=raw_id, start_ns=end - minutes * MINUTE_NS,
                end_ns=end, latency_ns=latency), result)
        cpu['rolling_all_atom_additions_and_removals_and_final_statistics'] = cpu.get(
            'rolling_all_atom_additions_and_removals_and_final_statistics', 0.0) + time.process_time() - began
        source_clock = next(a for a in clocks['anchors'] if a.variant == 'source_06_09_fixed_utc_minus4')
        began = time.process_time()
        pin069 = PIN069BarClose(source_clock)
        pin069_values = tuple(pin069.add(atom) for atom in atoms)
        cpu['pin069_actual_completed_bar_sequence'] = cpu.get('pin069_actual_completed_bar_sequence', 0.0) + time.process_time() - began
        results.append({'instrument_id': raw_id, 'coordinate': identity, 'named_clock_matches': tuple(a.variant for a in matches),
            'named_clock_unavailable': clocks['unavailable'], 'composition_check_uses_named_scientific_formation': bool(matches),
            'aggregate': aggregate, 'tpo': tpo_values, 'profiles': profiles, 'bar_proxies': proxies,
            'rolling': rolling_values, 'pin069_completed_bar_sequence': pin069_values,
            'exact_whole_tape_fields_compared': comparison,
            'all_original_tpo_row_bracket_memberships_equal': True,
            'legacy_tpo_source_display_minimum_brackets': tuple(v['minimum_completed_brackets'] for v in instrument['time_at_price']['tpo']),
            'atom_count': len(atoms), 'atom_price_rows': sum(len(a.rows) for a in atoms)})
    began = time.process_time()
    if replay:
        import pyarrow.compute as pc
        for table in read_series_tables(trade_storage):
            for (raw_id, _), (tape, _) in replay.items():
                kept = table.filter(pc.and_(pc.equal(table['instrument_id'], raw_id), pc.greater_equal(table['t'], tape.start)))
                tape.add(kept)
        for _, (tape, aggregate) in replay.items():
            literal = tape.record(source_coverage_complete=aggregate['source_coverage_complete'],
                                  coordinate_complete=aggregate['coordinate_complete'])
            _compare_tape(aggregate, literal)
    cpu['complete_retained_trade_rolling_replay_and_comparison'] = time.process_time() - began
    result = {'version': VERSION, 'unit': unit, 'measurement_reference': measurement_reference,
        'passed': True, 'instruments': results, 'coordinate_exclusions': excluded, 'cpu_components_disjoint': cpu,
        'rolling_actual_tape_comparisons': len(replay), 'or15_default_anchor': False,
        'source_bar_comparisons_are_exact_trade_profiles': False,
        'annual_or_model_workload_projection_complete': False,
        'scope': 'complete actual resource-window composition/representation checks, separate from full-cohort family inference'}
    reference = outputs.json_compressed(f"{unit['root']}-{start}-{unit['source_variant']}-anchor-check.json.zst", result,
        kind='auction_flow_actual_anchor_composition_check')
    return {'reference': reference, 'cpu_components_disjoint': cpu, 'serialization_cpu_seconds': reference['cpu_seconds'],
        'output_bytes': outputs.written - byte_start, 'instruments': len(results),
        'coordinate_exclusions': len(excluded), 'atom_count': sum(r['atom_count'] for r in results),
        'atom_price_rows': sum(r['atom_price_rows'] for r in results),
        'rolling_actual_tape_comparisons': len(replay), 'passed': True}
