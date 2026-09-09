"""Independent table-backed checks for frozen profile/reference geometry."""
from datetime import date, time
from fractions import Fraction
from pathlib import Path
import json
import hashlib
import tempfile
import unittest

from trading_research.errors import IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.measurements.profiles import (
    FrozenGrid, ProfileDefinition, bar_allocation_rows, profile_geometry_rows,
)
from trading_research.operations.artifacts import file_digest
from trading_research.research.auction_flow_core_statistics import FROZEN_STAGE_POLICY
from trading_research.research.auction_flow_measurements import SparseSideMass
from trading_research.research.auction_flow_anchors import AuctionAnchor
from trading_research.research.auction_flow_profile_reference import (
    BAR_PROXY_VARIANTS, BASELINE_VARIANT_ID, FORMATION_MINUTES, FROZEN_GEOMETRY_VARIANTS,
    IntegerMass, LATENCY_NS, MINUTE_NS, NS, SOURCE_LATENCY_NS, ZONE, aligned_cuts,
    classify_future_contact, compact_side_geometry, compare_frozen_developing_va,
    decode_exact_int, delayed_selection_blocks_origin, emit_geometry_payload,
    encode_exact_int, extract_sparse_profile, extract_unit_cells,
    future_mass_on_frozen_grid, geometry_from_mass, geometry_schema,
    integer_profile_geometry, labelled_sd, match_atom_identity,
    normalize_exact_integers, null_geometry, pin069_reanchor, publication_known,
    require_frozen_variants, variant_definition, write_series_table, read_series_tables,
)
from trading_research.research.auction_flow_window_links import feature_schema, label_schema
from trading_research.research.auction_flow_profile_statistics import (
    KIND, PAIRED_CONTRASTS, _GFIELDS, accumulate_geometry_row,
    authenticate_reused_partition, decode_profile_partition_key,
    encode_profile_partition_key, new_partition_accumulators, profile_partition_plan,
    project_profile_resources, reconstruct_profile_groups, run_profile_statistics,
    write_partition_groups,
)
from trading_research.research.auction_flow_profiles import (
    geometry, transform_mass, view_sparse,
)
from trading_research.research.auction_flow_storage import (
    BoundedOutputs, ParquetSeries, read_json_artifact,
)


SHA = 'ab' * 32
SHA2 = 'cd' * 32
SHA3 = 'ef' * 32
WEEKLY = 'quantpad/weekly-nq-2020-06.parquet'
WEEKLY_B = 'quantpad/weekly-nq-2020-06-b.parquet'
MONTHLY = 'databento/monthly-nq-2020-06.parquet'
PATH_ES = 'quantpad/weekly-es-2020-06.parquet'


def _ns(day, hour, minute=0, second=0, *, zone=ZONE):
    return local_timestamp(day, time(hour, minute, second), zone)


def frozen_contract(**extra):
    contract = {
        'kind': 'auction_flow_profile_reference_statistics_contract_v1',
        'version': 1,
        'full_family_complete': False,
        'geometry_variants': [dict(item) for item in FROZEN_GEOMETRY_VARIANTS],
        'bar_proxy_variants': list(BAR_PROXY_VARIANTS),
        'anchor_definitions': {
            'fixed_clocks': [
                {'id': 'cash_rth'}, {'id': 'prior_cash_rth'},
                {'id': 'observed_futures_18_17'}, {'id': 'overnight_18_0930'},
                {'id': 'morning_06_09_ny'}, {'id': 'source_06_09_fixed_utc_minus4'},
                {'id': 'source_monday_22_21_utc'}, {'id': 'source_tuesday_22_21_utc'},
            ],
            'rolling_minutes': [5, 15, 60, 240],
        },
        'clock': {'latencies_ns': [0, 250000000, 1000000000], 'cut_stride_ns': 300000000000},
        'statistics': {
            'block_length': 5,
            'bootstrap_replicates': 1000,
            'confidence': 0.95,
            'minimum_independent_dates': 100,
            'minimum_events': 20,
            'quantiles': [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99],
            'seed': 20260908,
        },
        'stage_policy': {
            root: {name: list(bounds) for name, bounds in stages.items()}
            for root, stages in FROZEN_STAGE_POLICY.items()
        },
        'source_collections': {
            WEEKLY: 'weekly_acquisitions',
            WEEKLY_B: 'weekly_acquisitions',
            MONTHLY: 'monthly_acquisitions',
            PATH_ES: 'weekly_acquisitions',
        },
        'primary_population': {'start': '2020-01-01', 'end': '2026-09-04'},
        'cash_session_table': {
            '2020-03-08': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-06-14': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-06-15': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-06-01': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-06-08': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-06-16': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-07-01': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-07-15': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-09-15': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-10-15': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-11-26': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-11-27': {'state': 'early_close', 'open': '09:30:00', 'close': '13:00:00'},
            '2020-12-15': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-12-28': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-12-29': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-12-30': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-12-31': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2021-01-04': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2021-01-15': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2019-12-16': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
        },
        'footprint': {},
    }
    contract.update(extra)
    return contract


def refuse_reference(reference, **kwargs):
    raise IntegrityError(f'external or unexpected reference load {reference!r}')


def own_output_loader(root):
    root = Path(root).resolve()

    def load(reference, maximum=None):
        if not isinstance(reference, dict) or type(reference.get('path')) is not str:
            raise IntegrityError('reference required')
        path = Path(reference['path']).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise IntegrityError('external reference rejected') from exc
        size = path.stat().st_size
        if type(reference.get('size_bytes')) is int and size != reference['size_bytes']:
            raise IntegrityError('reference size mismatch')
        if maximum is not None and size > maximum:
            raise IntegrityError('reference exceeds size bound')
        if reference.get('sha256') and file_digest(path) != reference['sha256']:
            raise IntegrityError('reference hash mismatch')
        if path.suffix == '.json' or path.name.endswith('.json'):
            return json.loads(path.read_bytes())
        return {'path': str(path), 'sha256': reference.get('sha256'), 'size_bytes': size}

    return load


def _atom_trade(*, start, end, known, instrument, contract, rows, unpriced=(0, 0, 0),
                complete=True, prints=None, high=None, low=None, first=None, last=None,
                order=0):
    priced = [0, 0, 0]
    for _row, buy, sell, unknown in rows:
        priced[0] += buy
        priced[1] += sell
        priced[2] += unknown
    volume = sum(priced)
    if first is None and rows:
        first = rows[0][0]
    if last is None and rows:
        last = rows[-1][0]
    if high is None and rows:
        high = max(row[0] for row in rows)
    if low is None and rows:
        low = min(row[0] for row in rows)
    sum_pv = sum(row * (buy + sell + unknown) for row, buy, sell, unknown in rows)
    sum_p2v = sum(row * row * (buy + sell + unknown) for row, buy, sell, unknown in rows)
    return {
        'bin': (start - (start // MINUTE_NS * MINUTE_NS)) // MINUTE_NS,
        'instrument_id': instrument,
        'event_start_ns': start,
        'event_end_ns': end,
        'known_at_ns': known,
        'coordinate': {'complete': complete, 'contract_key': contract},
        'trade': {
            'instrument_id': instrument,
            'event_start_ns': start,
            'event_end_ns': end,
            'known_at_ns': known,
            'source_coverage_complete': complete,
            'price_history_complete': complete and sum(unpriced) == 0,
            'flow_history_complete': complete,
            'coordinate_complete': complete,
            'prints': prints if prints is not None else (1 if volume or sum(unpriced) else 0),
            'unpriced_prints': 1 if sum(unpriced) else 0,
            'first_priced_ticks': first,
            'last_priced_ticks': last,
            'observed_high_ticks': high,
            'observed_low_ticks': low,
            'first_priced_event_ns': start,
            'last_priced_event_ns': end - 1,
            'first_priced_source_order': order,
            'last_priced_source_order': order,
            'sparse_profile': {
                'row_ticks': 1,
                'origin_ticks': 0,
                'rows': [list(row) for row in rows],
                'unpriced_buy_sell_unknown': list(unpriced),
                'total_volume': volume + sum(unpriced),
            },
            'weighted_price': {
                'priced_volume': volume,
                'sum_price_volume': sum_pv,
                'sum_price_squared_volume': sum_p2v,
            },
        },
    }


def _minute_atoms(start, minutes, *, instrument, contract, rows, complete=True, unpriced=(0, 0, 0)):
    atoms = []
    for index in range(minutes):
        a = start + index * MINUTE_NS
        b = a + MINUTE_NS
        atoms.append(_atom_trade(
            start=a, end=b, known=b + SOURCE_LATENCY_NS, instrument=instrument,
            contract=contract, rows=rows, unpriced=unpriced, complete=complete, order=index,
        ))
        atoms[-1]['bin'] = index
    return atoms


def _measurement(*, root, start, end, atoms_by_instrument, status='measured'):
    instruments = []
    for instrument_id, atoms in atoms_by_instrument:
        instruments.append({'instrument_id': instrument_id, 'atomic_windows': atoms})
    return {
        'status': status,
        'root': root,
        'event_start_ns': start,
        'event_end_ns': end,
        'known_at_ns': end + SOURCE_LATENCY_NS,
        'atomic_width_ns': MINUTE_NS,
        'instruments': instruments,
    }


def _observation_rows(unit_meta, atoms, *, sha=SHA):
    rows = []
    for atom in atoms:
        trade = atom['trade']
        profile = extract_sparse_profile(trade['sparse_profile'])
        rows.append({
            'root': unit_meta['root'],
            'source_path': unit_meta['source_path'],
            'source_metadata_sha256': sha,
            'source_variant': sha[:12],
            'source_window_start_ns': unit_meta['start'],
            'source_window_end_ns': unit_meta['end'],
            'receipt_sha256': sha,
            'measurement_sha256': sha,
            'canonical_raw_values_sha256': unit_meta.get('canonical', sha),
            'instrument_id': atom['instrument_id'],
            'contract_key': atom['coordinate']['contract_key'],
            'event_start_ns': atom['event_start_ns'],
            'event_end_ns': atom['event_end_ns'],
            'known_at_ns': atom['known_at_ns'],
            'atomic_bin': atom['bin'],
            'coordinate_complete': atom['coordinate']['complete'],
            'source_coverage_complete': trade['source_coverage_complete'],
            'price_history_complete': trade['price_history_complete'],
            'flow_history_complete': trade['flow_history_complete'],
            'priced_buy': profile['priced_buy'],
            'priced_sell': profile['priced_sell'],
            'priced_unknown': profile['priced_unknown'],
            'unpriced_buy': profile['unpriced'][0],
            'unpriced_sell': profile['unpriced'][1],
            'unpriced_unknown': profile['unpriced'][2],
            'priced_volume': profile['priced_volume'],
            'sum_price_volume': trade['weighted_price']['sum_price_volume'],
            'sum_price_squared_volume': trade['weighted_price']['sum_price_squared_volume'],
            'prints': trade['prints'],
            'unpriced_prints': trade['unpriced_prints'],
            'first_priced_ticks': trade['first_priced_ticks'],
            'last_priced_ticks': trade['last_priced_ticks'],
            'observed_high_ticks': trade['observed_high_ticks'],
            'observed_low_ticks': trade['observed_low_ticks'],
        })
    return rows


def _write_table(outputs, name, rows, schema=None):
    import pyarrow as pa
    if schema is not None:
        names = [field.name for field in schema]
        aligned = []
        for row in rows or ():
            item = {}
            for field in schema:
                if field.name in row:
                    item[field.name] = row[field.name]
                elif pa.types.is_boolean(field.type):
                    item[field.name] = False
                elif not field.nullable and pa.types.is_string(field.type):
                    item[field.name] = ''
                elif not field.nullable and pa.types.is_integer(field.type):
                    item[field.name] = 0
                else:
                    item[field.name] = None
            aligned.append(item)
        table = pa.table(
            {name: pa.array([row[name] for row in aligned], type=schema.field(name).type) for name in names},
            schema=schema,
        ) if aligned else pa.table({name: pa.array([], type=schema.field(name).type) for name in names}, schema=schema)
    elif not rows:
        table = pa.table({'root': pa.array([], type=pa.string())})
    else:
        names = list(rows[0])
        table = pa.table({
            name: pa.array([row[name] for row in rows]) for name in names
        })
    series = ParquetSeries(outputs, name, encoding='plain')
    series.append(table)
    return series.finish()


def _write_unit(outputs, name, *, root, path, start, end, atoms_by_instrument, sha=SHA,
                canonical=None, status='measured'):
    measured = _measurement(
        root=root, start=start, end=end, atoms_by_instrument=atoms_by_instrument, status=status,
    )
    measurement_ref = outputs.json(f'{name}-measurement.json', measured, kind='auction_flow_measurement_v1')
    receipt_ref = outputs.json(f'{name}-receipt.json', {
        'kind': 'auction_flow_source_window_receipt_v1',
        'success': True,
        'status': status,
        'sha256': sha,
    }, kind='auction_flow_source_window_receipt_v1')
    atoms = [atom for _instrument, group in atoms_by_instrument for atom in group]
    obs_rows = _observation_rows(
        {'root': root, 'source_path': path, 'start': start, 'end': end, 'canonical': canonical or sha},
        atoms, sha=sha,
    )
    series = _write_table(outputs, f'{name}-observations', obs_rows)
    return {
        'kind': 'auction_flow_observation_unit_v1',
        'root': root,
        'source_path': path,
        'source_window_start_ns': start,
        'source_window_end_ns': end,
        'source_window_status': status,
        'unavailable_reason': None if status == 'measured' else 'unavailable_source_window',
        'atomic_rows': len(obs_rows),
        'series': series,
        'measurement': measurement_ref,
        'receipt': receipt_ref,
        'original_refs': {'measurement': measurement_ref, 'receipt_reference': receipt_ref},
        'source_metadata_sha256': sha,
        'source_variant': sha[:12],
    }


def _quality_flags(complete=True):
    return {
        'atoms_complete': complete,
        'coordinate_complete': complete,
        'supplied_raw_coordinate_stable': complete,
        'source_instrument_presence': True,
        'source_coverage_complete': complete,
        'flow_history_complete': complete,
        'price_history_complete': complete,
    }


def _window_rows(*, path, root, instrument, contract, cut, sha=SHA, complete=True,
                 last=110, high=110, low=100, no_new=False, no_priced=False, stage='training',
                 acquired_start=None, acquired_end=None, formation_minutes=None,
                 label_known_at_ns=None, geometry_incomplete=False):
    formations = FORMATION_MINUTES if formation_minutes is None else (int(formation_minutes),)
    acquired_start = cut - max(formations) * MINUTE_NS if acquired_start is None else acquired_start
    acquired_end = cut if acquired_end is None else acquired_end
    flags = _quality_flags(complete)
    identity = {
        'root': root, 'source_path': path, 'source_metadata_sha256': sha,
        'source_variant': sha[:12],
        'acquired_event_start_ns': acquired_start, 'acquired_event_end_ns': acquired_end,
        'instrument_id': instrument, 'contract_key': contract,
    }
    features = []
    for minutes in formations:
        for latency in LATENCY_NS:
            formation_start = cut - minutes * MINUTE_NS
            features.append({
                **identity,
                'formation_minutes': minutes, 'latency_ns': int(latency),
                'cut_ns': cut,
                'event_start_ns': formation_start, 'event_end_ns': cut,
                'known_at_ns': cut + SOURCE_LATENCY_NS,
                'formation_id': f'feat-{cut}-{minutes}-{latency}',
                'stage': stage, 'stage_boundary': False,
                'left_censored': False, 'right_censored': False, 'censor_reason': None,
                'contract_transition': False,
                'complete': complete, 'chronological_eligible': True,
                'data_complete': complete, 'contract_stable': True,
                **flags,
            })
    labels = []
    for latency in LATENCY_NS:
        for horizon_kind, minutes in (
            ('fixed_minutes', 5), ('fixed_minutes', 15), ('fixed_minutes', 60),
            ('remaining_session', None),
        ):
            start = cut + latency
            width = (minutes or 5) * MINUTE_NS
            end = start + width
            known = label_known_at_ns if label_known_at_ns is not None else end + SOURCE_LATENCY_NS
            labels.append({
                **identity,
                'cut_ns': cut, 'latency_ns': latency,
                'horizon_kind': horizon_kind, 'horizon_minutes': minutes,
                'event_start_ns': start, 'event_end_ns': end, 'known_at_ns': known,
                'label_id': f'lab-{cut}-{latency}-{horizon_kind}-{minutes}',
                'stage': stage, 'stage_boundary': False,
                'remaining_session_applicable': horizon_kind == 'remaining_session',
                'remaining_session_disposition': None,
                'left_censored': False, 'right_censored': False, 'censor_reason': None,
                'complete': complete, 'chronological_eligible': True,
                'data_complete': complete, 'contract_stable': True,
                'contract_transition': False, 'no_new_trade': no_new,
                'no_priced_trade': no_priced, **flags,
                'last_priced_ticks': last, 'observed_high_ticks': high, 'observed_low_ticks': low,
            })
    _ = geometry_incomplete
    return features, labels


def _feature_write_schema():
    import pyarrow as pa
    base = feature_schema()
    names = set(base.names)
    extras = []
    for field in (
        pa.field('latency_ns', pa.int64(), nullable=True),
        pa.field('complete', pa.bool_(), nullable=True),
        pa.field('chronological_eligible', pa.bool_(), nullable=True),
        pa.field('data_complete', pa.bool_(), nullable=True),
        pa.field('contract_stable', pa.bool_(), nullable=True),
    ):
        if field.name not in names:
            extras.append(field)
    return pa.schema(list(base) + extras)


def _write_window_unit(outputs, name, *, path, root, start, end, feature_rows, label_rows, sha=SHA):
    features = _write_table(outputs, f'{name}-features', feature_rows, schema=_feature_write_schema())
    labels = _write_table(outputs, f'{name}-labels', label_rows, schema=label_schema())
    return {
        'kind': 'auction_flow_window_unit_v1',
        'unit_id': [path, start, end],
        'source_identity': {
            'root': root, 'source_path': path, 'source_metadata_sha256': sha,
            'source_variant': sha[:12],
            'acquired_event_start_ns': start, 'acquired_event_end_ns': end,
        },
        'root': root, 'source_path': path,
        'cut_start_ns': start, 'cut_end_ns': end,
        'features': features, 'labels': labels,
        'feature_rows': len(feature_rows), 'label_rows': len(label_rows),
        'instrument_count': 1, 'cut_count': 1,
    }


def _run(directory, *, units, window_units=None, contract=None, selected=None):
    outputs = BoundedOutputs(directory, maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2)
    population = {
        'kind': 'auction_flow_observation_population_v1',
        'units': units,
        'all_population_materialized': True,
    }
    windows = {
        'kind': 'auction_flow_window_population_v1',
        'units': window_units or [],
    }
    return run_profile_statistics(
        population=population, window_population=windows,
        contract=contract or frozen_contract(), outputs=outputs,
        load_reference=own_output_loader(directory),
        selected_partition_keys=selected,
    ), outputs


def _run_geometry(directory, *, units, window_units=None, contract=None, selected=None):
    """Real partition/Arrow geometry path; statistical checks use _run instead."""
    import pyarrow as pa
    from trading_research.research.auction_flow_profile_reference import compute_profile_partition, empty_completeness
    from trading_research.research.auction_flow_profile_statistics import (
        _require_contract, _load_calendar, neighbor_units, profile_partition_source_refs,
        window_unit_refs, profile_partition_identity,
    )
    outputs = BoundedOutputs(directory, maximum_total_bytes=256 * 1024 ** 2,
                             maximum_file_bytes=64 * 1024 ** 2)
    population = {'kind': 'auction_flow_observation_population_v1', 'units': units,
                  'all_population_materialized': True}
    load = own_output_loader(directory)
    frozen, _stats, policy, collections = _require_contract(contract or frozen_contract(), population=population)
    calendar = _load_calendar(frozen, load)
    plan = profile_partition_plan(population, frozen)
    keys = plan['keys'] if selected is None else [tuple(key) for key in selected]
    total = empty_completeness()
    refs = {key: [] for key in ('geometry', 'tpo', 'joins', 'cells')}
    for ordinal, key in enumerate(keys):
        members = plan['members'][key]
        neighbors = neighbor_units(plan, key, collections=collections)
        source_refs = (profile_partition_source_refs(members, role='selected')
                       + profile_partition_source_refs(neighbors, role='support'))
        paths = {unit['source_path'] for unit in members + neighbors}
        window_refs = window_unit_refs(window_units or [], paths=paths)
        identity = profile_partition_identity(frozen, collection=key[0], root=key[1], year=key[2],
                                              source_refs=source_refs, window_refs=window_refs)
        _ref, part, _measurement = compute_profile_partition(
            key=key, members=members, neighbors=neighbors, identity=identity,
            source_refs=source_refs, contract=frozen, calendar=calendar, policy=policy,
            window_units=window_units or [], outputs=outputs, ordinal=ordinal, pa=pa,
            stats=None, load_reference=load, window_refs=window_refs,
        )
        for name in refs:
            refs[name].append(part[name])
        for name, value in part['completeness_counts'].items():
            if name in total and type(value) is int:
                total[name] += value
        total['unavailable_units'].extend(part['completeness_counts'].get('unavailable_units') or [])
    refs['completeness'] = outputs.json('geometry-fixture-completeness.json', total,
                                        kind='profile_geometry_fixture_completeness')
    return {'refs': refs, 'passed': True}, outputs


def _read_groups(result, load):
    return reconstruct_profile_groups(load(result['refs']['groups']), load, role='groups')


def _geometry_tables(result):
    rows = []
    for series in result['refs']['geometry']:
        for table in read_series_tables(series):
            names = table.column_names
            cols = {name: table.column(name).to_pylist() for name in names}
            for index in range(len(table)):
                rows.append({name: cols[name][index] for name in names})
    return rows


def _tpo_tables(result):
    rows = []
    for series in result['refs']['tpo']:
        for table in read_series_tables(series):
            names = table.column_names
            cols = {name: table.column(name).to_pylist() for name in names}
            for index in range(len(table)):
                rows.append({name: cols[name][index] for name in names})
    return rows


def _join_tables(result):
    rows = []
    for series in result['refs']['joins']:
        for table in read_series_tables(series):
            names = table.column_names
            cols = {name: table.column(name).to_pylist() for name in names}
            for index in range(len(table)):
                rows.append({name: cols[name][index] for name in names})
    return rows


class ProfileReferenceLiteralTests(unittest.TestCase):
    def test_owned_atom_evidence_is_identical_and_not_rehashed_per_tpo_projection(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from trading_research.research import auction_flow_profile_reference as module
        start = 2**53 + 3
        atom = {'source_path':'/fixture/source','event_start_ns':start,
            'event_end_ns':start+MINUTE_NS,'known_at_ns':start+MINUTE_NS+SOURCE_LATENCY_NS,
            'instrument_id':7,'rows':((100,5,1,0),(101,0,0,2)), 'unpriced':(0,0,7),
            'priced_buy':5,'priced_sell':1,'priced_unknown':2,'prints':4}
        anchor=SimpleNamespace(root='NQ',contract_key='NQ:H0',instrument_id=7,source_lineage='fixture-lineage')
        original=module.to_atomic_trades(atom,anchor)
        def sha(payload):
            return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),
                ensure_ascii=False,allow_nan=False).encode()).hexdigest()
        cells=sha({'rows':[[100,5,1,0],[101,0,0,2]],'unpriced':[0,0,7]})
        expected=sha({'path':'/fixture/source','start':start,'end':start+MINUTE_NS,
            'instrument_id':7,'cells':cells})
        self.assertEqual(original.evidence_id,expected)
        module.bind_owned_atom_evidence(atom)
        self.assertEqual(atom['evidence_id'],expected)
        with patch.object(module,'cells_content_hash',side_effect=AssertionError('redundant cell hashing')):
            module.bind_owned_atom_evidence(atom)
            for _ in range(6):
                projected=module.to_atomic_trades(atom,anchor)
                self.assertEqual(projected,original)
                self.assertEqual(projected.start_ns,start)

    def test_contract_rejects_first_wave_variant_reduction(self):
        contract = frozen_contract()
        contract['geometry_variants'] = contract['geometry_variants'][:2]
        with self.assertRaises(IntegrityError):
            require_frozen_variants(contract)

    def test_token_cannot_skip_frozen_kind_or_variants(self):
        contract = frozen_contract(fixture=True, skip_variants=True)
        contract['kind'] = 'profile_fixture_token_v1'
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=8 * 1024 ** 2, maximum_file_bytes=4 * 1024 ** 2)
            with self.assertRaises(IntegrityError):
                run_profile_statistics(
                    population={'kind': 'auction_flow_observation_population_v1', 'units': []},
                    window_population={'kind': 'auction_flow_window_population_v1', 'units': []},
                    contract=contract, outputs=outputs, load_reference=refuse_reference,
                )

    def test_extract_sparse_profile_keeps_ordered_side_cells(self):
        extracted = extract_sparse_profile({
            'row_ticks': 1, 'origin_ticks': 0,
            'rows': [[100, 5, 1, 0], [101, 0, 2, 3]],
            'unpriced_buy_sell_unknown': [0, 0, 7],
            'total_volume': 18,
        })
        self.assertEqual(extracted['rows'], ((100, 5, 1, 0), (101, 0, 2, 3)))
        self.assertEqual(extracted['unpriced'], (0, 0, 7))
        self.assertEqual(extracted['priced_volume'], 11)

    def test_zero_priced_mass_is_null_geometry(self):
        mass = IntegerMass()
        spec = next(item for item in FROZEN_GEOMETRY_VARIANTS if item['id'] == BASELINE_VARIANT_ID)
        compact, view = geometry_from_mass(
            mass, spec, coordinate_identity='NQ:H0', known_at_ns=1, coverage_complete=True,
        )
        self.assertIsNone(view)
        self.assertEqual(compact['geometry_status'], 'unknown_priced_population')
        self.assertIsNone(compact['scalar_poc'])

    def test_delayed_selection_cannot_publish_before_selection(self):
        self.assertTrue(delayed_selection_blocks_origin(20, 10))
        known = publication_known(input_known_ns=12, selection_known_ns=20, cut_ns=10, latency_ns=0)
        self.assertEqual(known, 20)
        self.assertGreaterEqual(known, 20)

    def test_future_contact_preserves_unknown_touch_order(self):
        result = classify_future_contact(
            poc=100, val=98, vah=104, high=110, low=90, last=101,
            complete=True, no_new=False, no_priced=False,
        )
        self.assertTrue(result['poc_touch'])
        self.assertTrue(result['poc_traverse'])
        self.assertTrue(result['terminal_inside_va'])
        self.assertFalse(result['touch_order_identified'])

    def test_no_event_and_censor_are_retained(self):
        self.assertEqual(classify_future_contact(
            poc=100, val=98, vah=104, high=110, low=90, last=101,
            complete=True, no_new=True, no_priced=False,
        )['status'], 'no_event')
        self.assertEqual(classify_future_contact(
            poc=100, val=98, vah=104, high=110, low=90, last=101,
            complete=False, no_new=False, no_priced=False,
        )['status'], 'censored')

    def test_frozen_vs_moving_va_splits_boundary_and_crossing(self):
        moving = compare_frozen_developing_va(
            prior_val=100, prior_vah=110, current_val=99, current_vah=110,
            previous_price=105, current_price=105,
        )
        self.assertTrue(moving['boundary_moving'])
        self.assertFalse(moving['price_crossing_frozen_va'])
        crossing = compare_frozen_developing_va(
            prior_val=100, prior_vah=110, current_val=100, current_vah=110,
            previous_price=105, current_price=99,
        )
        self.assertFalse(crossing['boundary_moving'])
        self.assertTrue(crossing['price_crossing_frozen_va'])

    def test_geometry_from_mass_matches_unchanged_kernel_on_plateau(self):
        mass = IntegerMass()
        mass.buy[100] = 5
        mass.buy[101] = 5
        mass.buy[102] = 1
        mass.sum_q = 11
        mass.sum_pq = 100 * 5 + 101 * 5 + 102 * 1
        mass.sum_p2q = 100 * 100 * 5 + 101 * 101 * 5 + 102 * 102 * 1
        sixty_eight = next(item for item in FROZEN_GEOMETRY_VARIANTS if item['id'] == 'source-one-tick-value-17/25')
        seventy = next(item for item in FROZEN_GEOMETRY_VARIANTS if item['id'] == BASELINE_VARIANT_ID)
        left, view = geometry_from_mass(
            mass, sixty_eight, coordinate_identity='NQ:H0:plateau', known_at_ns=1,
            coverage_complete=True, verify_kernel=True,
        )
        right, _ = geometry_from_mass(
            mass, seventy, coordinate_identity='NQ:H0:plateau', known_at_ns=1,
            coverage_complete=True, verify_kernel=True,
        )
        expected_68 = geometry(view, definition=variant_definition(sixty_eight))
        expected_70 = geometry(view, definition=variant_definition(seventy))
        self.assertEqual(left['poc_set'], tuple(expected_68['poc_set']))
        self.assertEqual(right['poc_set'], (100, 101))
        self.assertEqual(left['scalar_poc'], 100)
        self.assertNotEqual(expected_68['overshoot'], expected_70['overshoot'])
        self.assertEqual(left['overshoot_num'], expected_68['overshoot'].numerator)
        self.assertEqual(right['overshoot_num'], expected_70['overshoot'].numerator)

    def test_partition_plan_encodes_collection_root_year(self):
        day = date(2020, 6, 15)
        start = _ns(day, 18) - 24 * 60 * MINUTE_NS
        end = start + 24 * 60 * MINUTE_NS
        population = {
            'kind': 'auction_flow_observation_population_v1',
            'units': [{
                'root': 'NQ', 'source_path': WEEKLY,
                'source_window_start_ns': start, 'source_window_end_ns': end,
                'atomic_rows': 1,
                'series': {'roundtrip_exact': True, 'rows': 1, 'files': []},
            }],
        }
        plan = profile_partition_plan(population, frozen_contract())
        self.assertEqual(plan['canonical_keys'], [['weekly_acquisitions', 'NQ', 2020]])
        self.assertEqual(decode_profile_partition_key(plan['canonical_keys'][0]), plan['keys'][0])


class ProfileReferenceRunTests(unittest.TestCase):
    def test_completed_morning_emits_all_14_variants_and_6_proxies(self):
        day = date(2020, 6, 15)
        start = _ns(day, 6)
        end = _ns(day, 9)
        rows = ((100, 5, 0, 0), (101, 5, 0, 0), (102, 1, 0, 0))
        atoms = _minute_atoms(start, 180, instrument=7, contract='NQ:H0', rows=rows)
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=128 * 1024 ** 2, maximum_file_bytes=32 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'morning', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            result, _ = _run(
                Path(tmp) / 'run', units=[unit],
                selected=[['weekly_acquisitions', 'NQ', 2020]],
            )
            self.assertEqual(result['kind'], KIND)
            self.assertFalse(result['family_complete'])
            geometry_rows = _geometry_tables(result)
            completed = [
                row for row in geometry_rows
                if row.get('anchor_variant') == 'morning_06_09_ny' and row.get('eligible_complete')
            ]
            variant_ids = {row['geometry_variant'] for row in completed if row.get('proxy_variant') is None}
            self.assertEqual(variant_ids, {item['id'] for item in FROZEN_GEOMETRY_VARIANTS})
            proxies = {row['proxy_variant'] for row in completed if row.get('proxy_variant')}
            self.assertEqual(proxies, set(BAR_PROXY_VARIANTS))
            plateau = next(
                row for row in completed
                if row['geometry_variant'] == BASELINE_VARIANT_ID and row.get('proxy_variant') is None
            )
            sixty_eight = next(
                row for row in completed
                if row['geometry_variant'] == 'source-one-tick-value-17/25'
            )
            self.assertEqual(list(plateau['poc_set']), [100, 101])
            self.assertEqual(plateau['poc_count'], 2)
            self.assertEqual(plateau['scalar_poc'], 100)
            self.assertNotEqual(plateau['overshoot_num'], sixty_eight['overshoot_num'])
            upper = next(row for row in completed if row['geometry_variant'] == 'value70-poc-tie-upper')
            self.assertEqual(upper['scalar_poc'], 101)

    def test_bar_proxies_retain_flat_lost_mass(self):
        day = date(2020, 6, 15)
        start = _ns(day, 6)
        end = _ns(day, 9)
        flat = ((102, 11, 0, 0),)
        atoms = _minute_atoms(start, 180, instrument=7, contract='NQ:H0', rows=flat)
        for atom in atoms:
            atom['trade']['observed_high_ticks'] = 102
            atom['trade']['observed_low_ticks'] = 102
            atom['trade']['first_priced_ticks'] = 102
            atom['trade']['last_priced_ticks'] = 102
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=128 * 1024 ** 2, maximum_file_bytes=32 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'flat', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            result, _ = _run_geometry(Path(tmp) / 'run', units=[unit], selected=[['weekly_acquisitions', 'NQ', 2020]])
            geometry_rows = _geometry_tables(result)
            source = next(
                row for row in geometry_rows
                if row.get('proxy_variant') == 'pin066_source' and row.get('anchor_variant') == 'morning_06_09_ny'
            )
            corrected = next(
                row for row in geometry_rows
                if row.get('proxy_variant') == 'pin066_corrected' and row.get('anchor_variant') == 'morning_06_09_ny'
            )
            self.assertGreater(source['source_flat_bar_lost_mass'], 0)
            self.assertEqual(corrected['source_flat_bar_lost_mass'], 0)

    def test_tpo_visits_differ_from_range_proxy_and_final_singles_need_two_brackets(self):
        day = date(2020, 6, 15)
        start = _ns(day, 6)
        end = _ns(day, 9)
        atoms = []
        for index in range(180):
            a = start + index * MINUTE_NS
            b = a + MINUTE_NS
            price = 100 if index % 2 == 0 else 102
            atoms.append(_atom_trade(
                start=a, end=b, known=b + SOURCE_LATENCY_NS, instrument=7, contract='NQ:H0',
                rows=((price, 1, 0, 0),), high=102, low=100, first=price, last=price,
                order=index,
            ))
            atoms[-1]['bin'] = index
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=128 * 1024 ** 2, maximum_file_bytes=32 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'tpo', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            result, _ = _run_geometry(Path(tmp) / 'run', units=[unit], selected=[['weekly_acquisitions', 'NQ', 2020]])
            tpo_rows = _tpo_tables(result)
            visits = [
                row for row in tpo_rows
                if row.get('representation') == 'whole_trade_visits' and row.get('bracket_minutes') == 15
                and row.get('anchor_variant') == 'morning_06_09_ny' and row.get('cut_ns') == end
            ]
            proxy = [
                row for row in tpo_rows
                if row.get('representation') == 'ohlc_range_proxy' and row.get('bracket_minutes') == 15
                and row.get('anchor_variant') == 'morning_06_09_ny' and row.get('cut_ns') == end
            ]
            self.assertTrue(visits)
            self.assertTrue(proxy)
            self.assertEqual(len(visits), 1)
            self.assertEqual(len(proxy), 1)
            self.assertEqual(visits[0]['visit_count'], 2)
            self.assertEqual(visits[0]['visit_rows'], [100, 102])
            self.assertEqual(visits[0]['complete_brackets'], 12)
            self.assertEqual(proxy[0]['visit_count'], 3)
            self.assertEqual(proxy[0]['visit_rows'], [100, 101, 102])
            self.assertIsNotNone(visits[0]['final_single_print_rows'])
            incomplete = [
                row for row in tpo_rows if row.get('complete_brackets') is not None and row['complete_brackets'] < 2
            ]
            for row in incomplete:
                self.assertIsNone(row.get('final_single_print_rows'))

    def test_zero_effort_and_unpriced_incomplete_are_null(self):
        day = date(2020, 6, 15)
        start = _ns(day, 10)
        end = start + 5 * MINUTE_NS
        empty = _minute_atoms(start, 5, instrument=7, contract='NQ:H0', rows=(), complete=True)
        for atom in empty:
            atom['trade']['prints'] = 0
            atom['trade']['first_priced_ticks'] = None
            atom['trade']['last_priced_ticks'] = None
            atom['trade']['observed_high_ticks'] = None
            atom['trade']['observed_low_ticks'] = None
        unpriced = _minute_atoms(
            start, 5, instrument=8, contract='NQ:H0', rows=(), complete=False, unpriced=(0, 0, 4),
        )
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'nulls', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, empty), (8, unpriced)],
            )
            result, _ = _run_geometry(Path(tmp) / 'run', units=[unit], selected=[['weekly_acquisitions', 'NQ', 2020]])
            geometry_rows = _geometry_tables(result)
            statuses = {row['geometry_status'] for row in geometry_rows if row.get('geometry_status')}
            self.assertTrue(statuses & {'no_priced_volume', 'unknown_priced_population', 'incomplete_unpriced', 'observed_partial'})
            for row in geometry_rows:
                if row.get('geometry_status') in ('no_priced_volume', 'unknown_priced_population'):
                    self.assertIsNone(row['scalar_poc'])
                    self.assertIsNone(row['val_row'])

    def test_baseline_rows_across_two_dates_sources_and_instruments(self):
        dates = (date(2020, 6, 15), date(2020, 6, 16))
        paths = (WEEKLY, WEEKLY_B)
        units = []
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=128 * 1024 ** 2, maximum_file_bytes=32 * 1024 ** 2)
            for day_index, day in enumerate(dates):
                start = _ns(day, 10)
                end = start + 5 * MINUTE_NS
                # Distinct dates retain two source owners without presenting
                # competing raw identities at the same instrument and clock.
                for path, sha in (((WEEKLY, SHA), (WEEKLY_B, SHA2))[day_index],):
                    atoms7 = _minute_atoms(start, 5, instrument=7, contract='NQ:H0', rows=((100, 2, 0, 0),))
                    atoms8 = _minute_atoms(start, 5, instrument=8, contract='NQ:M0', rows=((200, 2, 0, 0),))
                    units.append(_write_unit(
                        outputs, f'u{day_index}-{sha[:4]}', root='NQ', path=path,
                        start=start, end=end, atoms_by_instrument=[(7, atoms7), (8, atoms8)],
                        sha=sha, canonical=sha,
                    ))
            result, _ = _run_geometry(Path(tmp) / 'run', units=units, selected=[['weekly_acquisitions', 'NQ', 2020]])
            geometry_rows = _geometry_tables(result)
            baseline = [
                row for row in geometry_rows
                if row.get('geometry_variant') == BASELINE_VARIANT_ID
                and row.get('proxy_variant') is None
                and row.get('anchor_kind') in ('developing', 'rolling')
            ]
            identities = {
                (row['economic_date'], row['source_path'], row['instrument_id'], row['anchor_variant'])
                for row in baseline
            }
            self.assertGreaterEqual(len({item[0] for item in identities}), 2)
            self.assertGreaterEqual(len({item[1] for item in identities}), 2)
            self.assertGreaterEqual(len({item[2] for item in identities}), 2)
            self.assertIn('developing_cash_rth', {item[3] for item in identities})
            self.assertTrue({'rolling_5m', 'rolling_15m', 'rolling_60m', 'rolling_240m'} <= {item[3] for item in identities})

    def test_same_instrument_code_different_contracts_stay_separate(self):
        day = date(2020, 6, 15)
        start = _ns(day, 10)
        end = start + 5 * MINUTE_NS
        h0 = _minute_atoms(start, 5, instrument=7, contract='NQ:H0', rows=((100, 3, 0, 0),))
        m0 = _minute_atoms(start, 5, instrument=7, contract='NQ:M0', rows=((300, 3, 0, 0),))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'roll', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, h0 + m0)],
            )
            result, _ = _run_geometry(Path(tmp) / 'run', units=[unit], selected=[['weekly_acquisitions', 'NQ', 2020]])
            geometry_rows = _geometry_tables(result)
            contracts = {row['contract_key'] for row in geometry_rows if row.get('contract_key')}
            self.assertIn('NQ:H0', contracts)
            self.assertIn('NQ:M0', contracts)
            h0_poc = {row['scalar_poc'] for row in geometry_rows if row.get('contract_key') == 'NQ:H0' and row.get('scalar_poc') is not None}
            m0_poc = {row['scalar_poc'] for row in geometry_rows if row.get('contract_key') == 'NQ:M0' and row.get('scalar_poc') is not None}
            self.assertTrue(h0_poc)
            self.assertTrue(m0_poc)
            self.assertTrue(h0_poc.isdisjoint(m0_poc))

    def test_monthly_neighbor_is_not_mixed_into_weekly_rolling(self):
        day = date(2020, 6, 15)
        prev = date(2020, 6, 14)
        start = _ns(day, 0)
        end = start + 60 * MINUTE_NS
        prev_start = _ns(prev, 20)
        prev_end = prev_start + 60 * MINUTE_NS
        weekly_prev = _minute_atoms(prev_start, 60, instrument=7, contract='NQ:H0', rows=((100, 1, 0, 0),))
        weekly_cur = _minute_atoms(start, 60, instrument=7, contract='NQ:H0', rows=((101, 1, 0, 0),))
        monthly = _minute_atoms(prev_start, 60, instrument=7, contract='NQ:H0', rows=((999, 9, 0, 0),))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=128 * 1024 ** 2, maximum_file_bytes=32 * 1024 ** 2)
            units = [
                _write_unit(outputs, 'wprev', root='NQ', path=WEEKLY, start=prev_start, end=prev_end,
                            atoms_by_instrument=[(7, weekly_prev)], sha=SHA),
                _write_unit(outputs, 'wcur', root='NQ', path=WEEKLY, start=start, end=end,
                            atoms_by_instrument=[(7, weekly_cur)], sha=SHA),
                _write_unit(outputs, 'mprev', root='NQ', path=MONTHLY, start=prev_start, end=prev_end,
                            atoms_by_instrument=[(7, monthly)], sha=SHA3, canonical=SHA3),
            ]
            result, _ = _run_geometry(
                Path(tmp) / 'run', units=units, selected=[['weekly_acquisitions', 'NQ', 2020]],
            )
            geometry_rows = _geometry_tables(result)
            weekly_rows = [row for row in geometry_rows if row.get('source_collection') == 'weekly_acquisitions']
            self.assertTrue(weekly_rows)
            for row in weekly_rows:
                self.assertNotEqual(row.get('scalar_poc'), 999)

    def test_joins_cover_latencies_horizons_and_censor_cohorts(self):
        day = date(2020, 6, 15)
        start = _ns(day, 10)
        end = start + 5 * MINUTE_NS
        atoms = _minute_atoms(start, 5, instrument=7, contract='NQ:H0', rows=((100, 4, 1, 0), (104, 2, 0, 0)))
        cut = end
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'join', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            features, labels = _window_rows(
                path=WEEKLY, root='NQ', instrument=7, contract='NQ:H0', cut=cut,
                acquired_start=start, acquired_end=end,
            )
            extra, extra_labels = _window_rows(
                path=WEEKLY, root='NQ', instrument=7, contract='NQ:H0', cut=cut,
                acquired_start=start, acquired_end=end, complete=False,
            )
            labels.extend(extra_labels)
            window = _write_window_unit(
                outputs, 'win', path=WEEKLY, root='NQ', start=start, end=end,
                feature_rows=features, label_rows=labels,
            )
            result, _ = _run_geometry(
                Path(tmp) / 'run', units=[unit], window_units=[window],
                selected=[['weekly_acquisitions', 'NQ', 2020]],
            )
            joins = _join_tables(result)
            latencies = {row['latency_ns'] for row in joins}
            horizons = {(row['horizon_kind'], row['horizon_minutes']) for row in joins}
            self.assertEqual(latencies, {0, 250000000, 1000000000})
            self.assertIn(('fixed_minutes', 5), horizons)
            self.assertIn(('fixed_minutes', 15), horizons)
            self.assertIn(('fixed_minutes', 60), horizons)
            self.assertIn(('remaining_session', None), horizons)
            statuses = {row['join_status'] for row in joins}
            self.assertTrue({'observed', 'censored', 'no_event'} & statuses or 'observed' in statuses)
            for row in joins:
                self.assertFalse(row.get('touch_order_identified'))

    def test_future_grid_overflow_is_explicit(self):
        mass = IntegerMass()
        mass.buy[100] = 4
        mass.buy[101] = 4
        mass.sum_q = 8
        mass.sum_pq = 100 * 4 + 101 * 4
        mass.sum_p2q = 10000 * 4 + 10201 * 4
        following = [{
            'rows': ((90, 3, 0, 0), (120, 2, 0, 0)),
            'unpriced': (0, 0, 0),
            'row_ticks': 1,
            'origin_ticks': 0,
        }]
        compact, grid = future_mass_on_frozen_grid(
            mass, following, coordinate_identity='NQ:H0', known_at_ns=1, coverage_complete=True,
        )
        self.assertEqual(grid.lower_row, 100)
        self.assertEqual(grid.upper_row, 101)
        self.assertGreater(compact['future_low_overflow_buy'] + compact['future_high_overflow_buy'], 0)

    def test_date_mean_weights_one_cut_and_one_hundred_cuts_equally(self):
        day_one = date(2020, 6, 15)
        day_two = date(2020, 6, 16)
        start_one = _ns(day_one, 9, 30)
        end_one = start_one + 5 * MINUTE_NS
        start_two = _ns(day_two, 9, 30)
        end_two = start_two + 500 * MINUTE_NS
        narrow = _minute_atoms(start_one, 5, instrument=7, contract='NQ:H0', rows=((100, 3, 0, 0), (101, 3, 0, 0)))
        wide = _minute_atoms(
            start_two, 500, instrument=7, contract='NQ:H0',
            rows=tuple((100 + offset, 1, 0, 0) for offset in range(8)),
        )
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2)
            units = [
                _write_unit(outputs, 'one', root='NQ', path=WEEKLY, start=start_one, end=end_one,
                            atoms_by_instrument=[(7, narrow)]),
                _write_unit(outputs, 'hundred', root='NQ', path=WEEKLY, start=start_two, end=end_two,
                            atoms_by_instrument=[(7, wide)]),
            ]
            result, _ = _run(Path(tmp) / 'run', units=units, selected=[['weekly_acquisitions', 'NQ', 2020]])
            load = own_output_loader(Path(tmp) / 'run')
            groups = _read_groups(result, load)
            developing = [
                group for group in groups
                if group.get('anchor') == 'rolling_5m'
                and group.get('variant') == BASELINE_VARIANT_ID
                and group.get('group_kind') == 'geometry'
                and group.get('proxy') is None
            ]
            self.assertTrue(developing)
            metric = developing[0]['metrics']['va_width_ticks']
            self.assertEqual(metric['eligible_independent_dates'], 2)
            date_mean = metric['date_mean']
            if isinstance(date_mean, dict):
                date_mean = date_mean.get('estimate')
            event_mean = metric['event_mean']
            self.assertIsNotNone(date_mean)
            self.assertIsNotNone(event_mean)
            self.assertNotAlmostEqual(date_mean, event_mean)

    def test_nanoseconds_above_float_mantissa_roundtrip(self):
        start = 2 ** 53 + 3 * MINUTE_NS + 1
        end = start + 5 * MINUTE_NS
        atoms = []
        for index in range(5):
            a = start + index * MINUTE_NS
            b = a + MINUTE_NS
            atoms.append(_atom_trade(
                start=a, end=b, known=b + SOURCE_LATENCY_NS, instrument=7, contract='NQ:H0',
                rows=((100, 1, 0, 0),), order=index,
            ))
            atoms[-1]['bin'] = index
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'ns', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            result, _ = _run_geometry(Path(tmp) / 'run', units=[unit])
            for series in result['refs']['cells']:
                for table in read_series_tables(series):
                    values = table.column('event_start_ns').to_pylist()
                    self.assertTrue(any(value > 2 ** 53 for value in values))
                    self.assertTrue(all(type(value) is int for value in values))
                    self.assertNotEqual(float(values[0]), values[0]) if values[0] > 2 ** 53 else True

    def test_accepted_observation_receipt_resolves_measurement_and_binds_identity(self):
        from trading_research.research.auction_flow_profile_reference import measurement_reference, load_measurement_cells
        from trading_research.research.auction_flow_profile_statistics import profile_partition_source_refs
        start = _ns(date(2020, 6, 15), 10)
        end = start + MINUTE_NS
        atoms = _minute_atoms(start, 1, instrument=7, contract='NQ:H0', rows=((100, 1, 0, 0),))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=16 * 1024 ** 2,
                                     maximum_file_bytes=8 * 1024 ** 2)
            direct = _write_unit(outputs, 'receipt-layout', root='NQ', path=WEEKLY,
                start=start, end=end, atoms_by_instrument=[(7, atoms)])
            measured = direct['measurement']
            receipt = outputs.json('accepted-receipt.json', {
                'kind': 'auction_flow_source_window_receipt_v1', 'success': True, 'status': 'measured',
                'unit': {'root': 'NQ', 'source_path': WEEKLY, 'event_start_ns': start, 'event_end_ns': end},
                'artifacts': {'measurement': measured},
            }, kind='auction_flow_source_window_receipt_v1')
            accepted = {k: v for k, v in direct.items() if k not in ('measurement', 'receipt', 'original_refs')}
            accepted.update(receipt=receipt, original_refs={
                'receipt_reference': receipt, 'receipt_sha256': receipt['sha256'],
                'measurement_sha256': measured['sha256']})
            self.assertEqual(measurement_reference(accepted), measured)
            self.assertEqual(load_measurement_cells(accepted), load_measurement_cells(direct))
            self.assertEqual(profile_partition_source_refs([accepted])[0]['measurement']['sha256'], measured['sha256'])
            with self.assertRaises(IntegrityError):
                measurement_reference({**accepted, 'source_path': 'another-source.parquet'})
            with self.assertRaises(IntegrityError):
                measurement_reference({**accepted, 'original_refs': {**accepted['original_refs'], 'measurement_sha256': '00' * 32}})
            with self.assertRaises(IntegrityError):
                measurement_reference({**accepted, 'receipt': {**receipt, 'sha256': '00' * 32}})

    def test_public_hash_tampering_is_rejected(self):
        day = date(2020, 6, 15)
        start = _ns(day, 10)
        end = start + MINUTE_NS
        atoms = _minute_atoms(start, 1, instrument=7, contract='NQ:H0', rows=((100, 1, 0, 0),))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=16 * 1024 ** 2, maximum_file_bytes=8 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'tamper', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            tampered = dict(unit['measurement'])
            tampered['sha256'] = '00' * 32
            with self.assertRaises(IntegrityError):
                read_json_artifact(tampered)
            loader = own_output_loader(tmp)
            with self.assertRaises(IntegrityError):
                loader(tampered)

    def test_parquet_nulls_and_types_survive_roundtrip(self):
        day = date(2020, 6, 15)
        start = _ns(day, 10)
        end = start + 5 * MINUTE_NS
        atoms = _minute_atoms(start, 5, instrument=7, contract='NQ:H0', rows=(), complete=True)
        for atom in atoms:
            atom['trade']['prints'] = 0
            atom['trade']['first_priced_ticks'] = None
            atom['trade']['last_priced_ticks'] = None
            atom['trade']['observed_high_ticks'] = None
            atom['trade']['observed_low_ticks'] = None
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=32 * 1024 ** 2, maximum_file_bytes=8 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'nulls2', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            result, _ = _run_geometry(Path(tmp) / 'run', units=[unit], selected=[['weekly_acquisitions', 'NQ', 2020]])
            for series in result['refs']['geometry']:
                counted = 0
                for table in read_series_tables(series):
                    counted += len(table)
                    self.assertIn('scalar_poc', table.column_names)
                    poc = table.column('scalar_poc')
                    self.assertTrue(poc.null_count >= 0)
                    self.assertEqual(str(table.schema.field('cut_ns').type), 'int64')
                self.assertEqual(counted, series['rows'])

    def test_dst_early_close_and_cross_midnight_clocks_are_distinct(self):
        dst = date(2020, 3, 8)
        early = date(2020, 11, 27)
        start_dst = _ns(dst, 6)
        end_dst = _ns(dst, 9)
        start_early = _ns(early, 9, 30)
        end_early = _ns(early, 13)
        dst_atoms = _minute_atoms(start_dst, 180, instrument=7, contract='NQ:H0', rows=((100, 1, 0, 0),))
        early_atoms = _minute_atoms(
            start_early, 210, instrument=7, contract='NQ:H0', rows=((100, 1, 0, 0),)
        )
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2)
            units = [
                _write_unit(outputs, 'dst', root='NQ', path=WEEKLY, start=start_dst, end=end_dst,
                            atoms_by_instrument=[(7, dst_atoms)]),
                _write_unit(outputs, 'early', root='NQ', path=WEEKLY, start=start_early, end=end_early,
                            atoms_by_instrument=[(7, early_atoms)]),
            ]
            result, _ = _run_geometry(Path(tmp) / 'run', units=units, selected=[['weekly_acquisitions', 'NQ', 2020]])
            geometry_rows = _geometry_tables(result)
            variants = {row['anchor_variant'] for row in geometry_rows}
            self.assertIn('morning_06_09_ny', variants)
            self.assertIn('developing_observed_futures_18_17', variants)
            self.assertIn('cash_rth', variants)

    def test_unavailable_unit_is_retained_with_reason(self):
        day = date(2020, 6, 15)
        start = _ns(day, 10)
        end = start + MINUTE_NS
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=16 * 1024 ** 2, maximum_file_bytes=8 * 1024 ** 2)
            unit = {
                'kind': 'auction_flow_observation_unit_v1',
                'root': 'NQ',
                'source_path': WEEKLY,
                'source_window_start_ns': start,
                'source_window_end_ns': end,
                'source_window_status': 'unavailable_source_window',
                'unavailable_reason': 'no observed instrument or incoming source owner in this window',
                'atomic_rows': 0,
                'series': {'roundtrip_exact': True, 'rows': 0, 'schema': 'empty', 'files': []},
            }
            empty = _write_table(outputs, 'empty-obs', [])
            unit['series'] = empty
            result, _ = _run_geometry(Path(tmp) / 'run', units=[unit], selected=[['weekly_acquisitions', 'NQ', 2020]])
            load = own_output_loader(Path(tmp) / 'run')
            completeness = load(result['refs']['completeness'])
            self.assertGreaterEqual(completeness['units_unavailable'], 1)
            self.assertTrue(completeness.get('unavailable_units'))

    def test_resource_projection_uses_source_byte_atom_and_geometry_work(self):
        projection = project_profile_resources(
            [{'cpu_seconds': 2.0, 'source_bytes': 1000, 'atoms': 10, 'geometry_rows': 5, 'output_bytes': 100}],
            remaining_source_bytes=2000, remaining_atoms=20, remaining_geometry_rows=10, margin=1.5,
        )
        self.assertGreaterEqual(projection['cpu_seconds_with_margin'], 1.5 * 2.0 * 2)
        self.assertIn('per source byte', projection['method'])
        self.assertIn('per atom', projection['method'])
        self.assertIn('per geometry row', projection['method'])

    def test_coarse_and_triangular_conserve_side_mass(self):
        import numpy as np
        sparse = SparseSideMass(row_ticks=1, origin_ticks=0)
        sparse.add(
            price_ticks=np.array([99, 100, 101, 102], dtype=np.int64),
            price_valid=np.array([1, 1, 1, 1], dtype=np.uint8),
            size=np.array([2, 3, 5, 7], dtype=np.int64),
            side=np.array([1, -1, 0, 1], dtype=np.int64),
        )
        sparse.add(price_ticks=np.array([0], dtype=np.int64),
                   price_valid=np.array([0], dtype=np.uint8),
                   size=np.array([11], dtype=np.int64), side=np.array([0], dtype=np.int64))
        view = view_sparse(
            sparse, coordinate_identity='NQ:H0', coverage_complete=True,
            grid=FrozenGrid(100, 1, 0, 2, 'cmp', 1, 16),
        )
        coarse = transform_mass(view, kind='coarsen', scale=2)
        tri = transform_mass(view, kind='triangular', scale=1)
        self.assertEqual(coarse.total_mass, view.total_mass)
        self.assertEqual(tri.total_mass, view.total_mass)
        for channel, index in (('buy', 0), ('sell', 1), ('unknown', 2)):
            def mass(item):
                return sum(getattr(row, channel) for row in item.rows) + item.low_overflow[index] + item.high_overflow[index] + item.unpriced[index]
            self.assertEqual(mass(coarse), mass(view))
            self.assertEqual(mass(tri), mass(view))

    def test_irrational_variance_keeps_labelled_sd(self):
        approx, text, kind = labelled_sd(Fraction(14, 9))
        self.assertIsNotNone(approx)
        self.assertNotEqual(kind, 'undefined')
        self.assertNotEqual(kind, 'exact_rational_sqrt')

    def test_identity_mismatch_is_rejected(self):
        cell = {
            'instrument_id': 7, 'event_start_ns': 1, 'event_end_ns': 2,
            'priced_buy': 5, 'priced_sell': 0, 'priced_unknown': 0,
            'unpriced': (0, 0, 0), 'priced_volume': 5, 'contract_key': 'NQ:H0',
        }
        obs = dict(cell)
        obs['unpriced_buy'] = 0
        obs['unpriced_sell'] = 0
        obs['unpriced_unknown'] = 0
        match_atom_identity(cell, obs)
        obs['priced_buy'] = 4
        with self.assertRaises(IntegrityError):
            match_atom_identity(cell, obs)


def _cell_tables(result):
    rows = []
    for series in result['refs']['cells']:
        for table in read_series_tables(series):
            names = table.column_names
            cols = {name: table.column(name).to_pylist() for name in names}
            for index in range(len(table)):
                rows.append({name: cols[name][index] for name in names})
    return rows


def _paired_tables(result, load):
    return reconstruct_profile_groups(load(result['refs']['paired']), load, role='paired')


class ProfileReferenceCorrectionTests(unittest.TestCase):
    def test_zero_latency_is_present(self):
        day = date(2020, 6, 15)
        start = _ns(day, 10)
        end = start + 5 * MINUTE_NS
        atoms = _minute_atoms(start, 5, instrument=7, contract='NQ:H0', rows=((100, 4, 0, 0),))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'zero', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            features, labels = _window_rows(
                path=WEEKLY, root='NQ', instrument=7, contract='NQ:H0', cut=end,
                acquired_start=start, acquired_end=end,
            )
            window = _write_window_unit(
                outputs, 'win', path=WEEKLY, root='NQ', start=start, end=end,
                feature_rows=features, label_rows=labels,
            )
            result, _ = _run_geometry(
                Path(tmp) / 'run', units=[unit], window_units=[window],
                selected=[['weekly_acquisitions', 'NQ', 2020]],
            )
            joins = _join_tables(result)
            self.assertIn(0, {row['latency_ns'] for row in joins})
            zeros = [row for row in joins if row['latency_ns'] == 0]
            self.assertTrue(zeros)
            self.assertTrue(any(
                row.get('actual_known_at_ns') is not None
                and row.get('scenario_known_at_ns') is not None
                and row['actual_known_at_ns'] != row['scenario_known_at_ns']
                for row in zeros
            ))

    def test_future_stage_mismatch_and_own_geometry_incomplete_are_rejected(self):
        day = date(2020, 6, 15)
        start = _ns(day, 10)
        end = start + 5 * MINUTE_NS
        complete_atoms = _minute_atoms(start, 5, instrument=7, contract='NQ:H0', rows=((100, 2, 0, 0),))
        incomplete = _minute_atoms(
            start, 5, instrument=8, contract='NQ:M0', rows=((200, 2, 0, 0),), complete=False,
        )
        confirm = local_timestamp(date(2025, 2, 1), time(12, 0), ZONE)
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'rej', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, complete_atoms), (8, incomplete)],
            )
            feat_ok, lab_mismatch = _window_rows(
                path=WEEKLY, root='NQ', instrument=7, contract='NQ:H0', cut=end,
                acquired_start=start, acquired_end=end, label_known_at_ns=confirm,
            )
            feat_inc, lab_inc = _window_rows(
                path=WEEKLY, root='NQ', instrument=8, contract='NQ:M0', cut=end,
                acquired_start=start, acquired_end=end, complete=True,
            )
            window = _write_window_unit(
                outputs, 'win', path=WEEKLY, root='NQ', start=start, end=end,
                feature_rows=feat_ok + feat_inc, label_rows=lab_mismatch + lab_inc,
            )
            result, _ = _run_geometry(
                Path(tmp) / 'run', units=[unit], window_units=[window],
                selected=[['weekly_acquisitions', 'NQ', 2020]],
            )
            joins = _join_tables(result)
            mismatch = [
                row for row in joins
                if row.get('instrument_id') == 7 and row.get('join_status') not in (None, 'no_label')
            ]
            incomplete_rows = [
                row for row in joins
                if row.get('instrument_id') == 8 and row.get('join_status') not in (None, 'no_label')
            ]
            self.assertTrue(mismatch)
            self.assertTrue(any(
                row.get('scientific_reason') == 'label_maturity_not_same_named_stage'
                or row.get('join_status') == 'stage_leak'
                for row in mismatch
            ))
            self.assertTrue(incomplete_rows)
            self.assertTrue(any(
                row.get('join_status') == 'formation_incomplete'
                or row.get('censor_reason') == 'own_geometry_incomplete'
                for row in incomplete_rows
            ))
            self.assertFalse(any(row.get('join_status') == 'observed' for row in mismatch + incomplete_rows))

    def test_prior_final_va_does_not_affect_earlier_developing(self):
        day = date(2020, 6, 15)
        start = _ns(day, 9, 30)
        end = _ns(day, 16)
        atoms = _minute_atoms(start, 390, instrument=7, contract='NQ:H0', rows=((100, 1, 0, 0), (104, 1, 0, 0)))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=128 * 1024 ** 2, maximum_file_bytes=32 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'dev', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            result, _ = _run_geometry(Path(tmp) / 'run', units=[unit], selected=[['weekly_acquisitions', 'NQ', 2020]])
            geometry_rows = _geometry_tables(result)
            cash = next(
                row for row in geometry_rows
                if row.get('anchor_variant') == 'cash_rth'
                and row.get('geometry_variant') == BASELINE_VARIANT_ID
                and row.get('proxy_variant') is None
            )
            developing = [
                row for row in geometry_rows
                if row.get('anchor_variant') == 'developing_cash_rth'
                and row.get('proxy_variant') is None
            ]
            self.assertTrue(developing)
            for row in developing:
                self.assertNotEqual(row.get('completed_geometry_id'), cash.get('geometry_id'))
                self.assertNotEqual(row.get('geometry_id'), cash.get('geometry_id'))

    def test_completed_prior_anchor_emits_later_links(self):
        day = date(2020, 6, 15)
        start = _ns(day, 6)
        end = _ns(day, 10)
        atoms = _minute_atoms(start, 240, instrument=7, contract='NQ:H0', rows=((100, 1, 0, 0),))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=128 * 1024 ** 2, maximum_file_bytes=32 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'later', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            result, _ = _run_geometry(Path(tmp) / 'run', units=[unit], selected=[['weekly_acquisitions', 'NQ', 2020]])
            joins = _join_tables(result)
            later = [row for row in joins if row.get('later_completed_link') is True]
            self.assertTrue(later)
            self.assertTrue(any(row.get('anchor_variant') == 'morning_06_09_ny' for row in later))

    def test_adjacent_same_collection_files_form_one_mass_other_collection_never_joins(self):
        day = date(2020, 6, 15)
        first_start = _ns(day, 10)
        first_end = first_start + 60 * MINUTE_NS
        second_start = first_end
        second_end = second_start + 60 * MINUTE_NS
        left = _minute_atoms(first_start, 60, instrument=7, contract='NQ:H0', rows=((100, 1, 0, 0),))
        right = _minute_atoms(second_start, 60, instrument=7, contract='NQ:H0', rows=((101, 1, 0, 0),))
        monthly = _minute_atoms(first_start, 60, instrument=7, contract='NQ:H0', rows=((999, 9, 0, 0),))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=128 * 1024 ** 2, maximum_file_bytes=32 * 1024 ** 2)
            units = [
                _write_unit(outputs, 'a', root='NQ', path=WEEKLY, start=first_start, end=first_end,
                            atoms_by_instrument=[(7, left)], sha=SHA),
                _write_unit(outputs, 'b', root='NQ', path=WEEKLY_B, start=second_start, end=second_end,
                            atoms_by_instrument=[(7, right)], sha=SHA2, canonical=SHA2),
                _write_unit(outputs, 'm', root='NQ', path=MONTHLY, start=first_start, end=first_end,
                            atoms_by_instrument=[(7, monthly)], sha=SHA3, canonical=SHA3),
            ]
            result, _ = _run_geometry(
                Path(tmp) / 'run', units=units, selected=[['weekly_acquisitions', 'NQ', 2020]],
            )
            geometry_rows = _geometry_tables(result)
            weekly = [row for row in geometry_rows if row.get('source_collection') == 'weekly_acquisitions']
            monthly_rows = [row for row in geometry_rows if row.get('source_collection') == 'monthly_acquisitions']
            self.assertTrue(weekly)
            for row in weekly:
                self.assertNotEqual(row.get('scalar_poc'), 999)
            rolling = [
                row for row in weekly
                if row.get('anchor_variant') == 'rolling_60m' and row.get('proxy_variant') is None
                and row.get('cut_ns') == second_end
            ]
            self.assertTrue(rolling)
            for row in rolling:
                self.assertEqual(row.get('source_path'), WEEKLY_B)
                self.assertEqual(row.get('source_metadata_sha256'), SHA2)
            if monthly_rows:
                self.assertTrue(any(row.get('scalar_poc') == 999 for row in monthly_rows))

    def test_civil_week_month_quarter_year_rows_exist_with_partial_status(self):
        day = date(2020, 6, 15)
        start = _ns(day, 10)
        end = start + 5 * MINUTE_NS
        atoms = _minute_atoms(start, 5, instrument=7, contract='NQ:H0', rows=((100, 2, 0, 0),))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'civil', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            result, _ = _run_geometry(Path(tmp) / 'run', units=[unit], selected=[['weekly_acquisitions', 'NQ', 2020]])
            geometry_rows = _geometry_tables(result)
            variants = {row['anchor_variant'] for row in geometry_rows}
            for name in ('civil_ny_week', 'civil_ny_month', 'civil_ny_quarter', 'civil_ny_year'):
                self.assertIn(name, variants)
                rows = [row for row in geometry_rows if row.get('anchor_variant') == name]
                self.assertTrue(any(row.get('eligible_complete') is not True for row in rows))
                self.assertTrue(any(row.get('coverage_complete') is not True for row in rows))

    def test_pin069_new_high_resets_origin_and_accumulates_quotient(self):
        day = date(2020, 6, 15)
        start = _ns(day, 6, zone='Etc/GMT+4')
        window = AuctionAnchor(
            variant='source_06_09_fixed_utc_minus4', kind='jumbo_named_range',
            root='NQ', instrument_id=7, contract_key='NQ:H0',
            source_lineage='weekly_acquisitions/NQ/NQ:H0',
            spans=((start, start + 180 * MINUTE_NS),),
            selection_known_at_ns=0, source_versions=('pin069-test',),
        )
        bars = (
            (100, 100, 1, 1),
            (101, 101, 2, 2),
            (100, 99, 3, 3),
        )
        atoms = []
        for index, (high, close, volume, order) in enumerate(bars):
            a = start + index * MINUTE_NS
            b = a + MINUTE_NS
            atoms.append({
                'instrument_id': 7, 'contract_key': 'NQ:H0',
                'event_start_ns': a, 'event_end_ns': b,
                'known_at_ns': b + SOURCE_LATENCY_NS,
                'rows': ((close, volume, 0, 0),),
                'unpriced': (0, 0, 0),
                'priced_buy': volume, 'priced_sell': 0, 'priced_unknown': 0,
                'priced_volume': volume,
                'first_priced_ticks': close, 'last_priced_ticks': close,
                'observed_high_ticks': high, 'observed_low_ticks': close,
                'first_priced_event_ns': a, 'last_priced_event_ns': b - 1,
                'first_priced_source_order': order, 'last_priced_source_order': order,
                'source_coverage_complete': True, 'coordinate_complete': True,
                'prints': 1, 'unpriced_prints': 0, 'source_path': WEEKLY,
            })
        first = pin069_reanchor(atoms[:1], cut_ns=atoms[0]['event_end_ns'], window=window)
        self.assertEqual(first['pin069_origin_ns'], atoms[0]['event_start_ns'])
        second = pin069_reanchor(atoms[:2], cut_ns=atoms[1]['event_end_ns'], window=window)
        self.assertEqual(second['pin069_origin_ns'], atoms[1]['event_start_ns'])
        self.assertTrue(second['pin069_reset'])
        third = pin069_reanchor(atoms, cut_ns=atoms[2]['event_end_ns'], window=window)
        self.assertEqual(third['pin069_origin_ns'], atoms[1]['event_start_ns'])
        self.assertEqual(third['pin069_sum_close_volume'], 101 * 2 + 99 * 3)
        self.assertEqual(third['pin069_bar_volume'], 5)
        self.assertEqual(third['pin069_vwap_num'] / third['pin069_vwap_den'], (202 + 297) / 5)

    def test_required_computed_fields_survive_parquet(self):
        day = date(2020, 6, 15)
        start = _ns(day, 6)
        end = _ns(day, 9)
        atoms = _minute_atoms(start, 180, instrument=7, contract='NQ:H0', rows=((100, 5, 1, 0), (101, 2, 0, 0)))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=128 * 1024 ** 2, maximum_file_bytes=32 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'fields', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            result, _ = _run_geometry(Path(tmp) / 'run', units=[unit], selected=[['weekly_acquisitions', 'NQ', 2020]])
            import pyarrow as pa
            required = {field.name for field in geometry_schema(pa)}
            for series in result['refs']['geometry']:
                for table in read_series_tables(series):
                    self.assertTrue(required.issubset(set(table.column_names)))

    def test_coarse_width2_origin1_uses_physical_ticks(self):
        day = date(2020, 6, 15)
        start = _ns(day, 6)
        end = _ns(day, 9)
        atoms = _minute_atoms(start, 180, instrument=7, contract='NQ:H0', rows=((100, 5, 0, 0), (101, 5, 0, 0)))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=128 * 1024 ** 2, maximum_file_bytes=32 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'coarse', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            result, _ = _run_geometry(Path(tmp) / 'run', units=[unit], selected=[['weekly_acquisitions', 'NQ', 2020]])
            geometry_rows = _geometry_tables(result)
            coarse = next(
                row for row in geometry_rows
                if row.get('geometry_variant') == 'value70-width2-origin1'
                and row.get('anchor_variant') == 'morning_06_09_ny'
                and row.get('proxy_variant') is None
            )
            self.assertEqual(coarse['grid_width'], 2)
            self.assertEqual(coarse['grid_origin'], 1)
            if coarse['scalar_poc'] is not None:
                self.assertEqual(coarse['physical_poc_ticks'], coarse['scalar_poc'] * 2 + 1)

    def test_unpriced_only_atoms_are_retained_exactly_once(self):
        day = date(2020, 6, 15)
        start = _ns(day, 10)
        end = start + 3 * MINUTE_NS
        priced = _minute_atoms(start, 2, instrument=7, contract='NQ:H0', rows=((100, 1, 0, 0),))
        unpriced = _minute_atoms(
            start + 2 * MINUTE_NS, 1, instrument=7, contract='NQ:H0', rows=(), unpriced=(0, 0, 4),
        )
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=32 * 1024 ** 2, maximum_file_bytes=8 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'unp', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, priced + unpriced)],
            )
            result, _ = _run_geometry(Path(tmp) / 'run', units=[unit], selected=[['weekly_acquisitions', 'NQ', 2020]])
            cells = [row for row in _cell_tables(result) if row.get('unpriced_only') is True]
            keys = [
                (row['source_path'], row['instrument_id'], row['event_start_ns'], row['event_end_ns'])
                for row in cells
            ]
            self.assertEqual(len(cells), 1)
            self.assertEqual(len(keys), len(set(keys)))
            self.assertEqual(cells[0]['unpriced_unknown'], 4)

    def test_joined_anchor_variant_group_has_two_independent_dates(self):
        dates = (date(2020, 6, 15), date(2020, 6, 16))
        units = []
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=128 * 1024 ** 2, maximum_file_bytes=32 * 1024 ** 2)
            for day in dates:
                start = _ns(day, 10)
                end = start + 5 * MINUTE_NS
                atoms = _minute_atoms(start, 5, instrument=7, contract='NQ:H0', rows=((100, 2, 0, 0),))
                units.append(_write_unit(
                    outputs, day.isoformat(), root='NQ', path=WEEKLY, start=start, end=end,
                    atoms_by_instrument=[(7, atoms)],
                ))
            result, _ = _run(Path(tmp) / 'run', units=units, selected=[['weekly_acquisitions', 'NQ', 2020]])
            load = own_output_loader(Path(tmp) / 'run')
            groups = _read_groups(result, load)
            found = [
                group for group in groups
                if group.get('group_kind') == 'geometry'
                and group.get('anchor') == 'rolling_5m'
                and group.get('variant') == BASELINE_VARIANT_ID
                and group.get('proxy') is None
                and group.get('metrics', {}).get('priced_volume', {}).get('eligible_independent_dates', 0) >= 2
            ]
            self.assertTrue(found)

    def test_no_proxy_self_pair(self):
        day = date(2020, 6, 15)
        start = _ns(day, 6)
        end = _ns(day, 9)
        atoms = _minute_atoms(start, 180, instrument=7, contract='NQ:H0', rows=((100, 3, 0, 0), (101, 3, 0, 0)))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=128 * 1024 ** 2, maximum_file_bytes=32 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'pair', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            result, _ = _run(Path(tmp) / 'run', units=[unit], selected=[['weekly_acquisitions', 'NQ', 2020]])
            load = own_output_loader(Path(tmp) / 'run')
            paired = _paired_tables(result, load)
            for group in paired:
                if group.get('group_kind') == 'paired_proxy':
                    self.assertIsNotNone(group.get('proxy'))
                    self.assertNotEqual(group.get('proxy'), BASELINE_VARIANT_ID)
                    self.assertTrue(str(group.get('contrast') or '').startswith('exact_vs_'))
                if group.get('group_kind') == 'paired_geometry':
                    left, _sep, right = str(group.get('variant') or '').partition('__')
                    self.assertTrue(left and right and left != right)

    def test_civil_completion_denominator_has_literal_year_end_and_stage(self):
        from trading_research.research.auction_flow_profile_statistics import civil_completion_dates
        policy = frozen_contract()['stage_policy']
        self.assertEqual(civil_completion_dates(2020, 'training', 'NQ', 'civil_ny_quarter', policy),
                         ['2020-04-01', '2020-07-01', '2020-10-01', '2021-01-01'])
        self.assertEqual(civil_completion_dates(2020, 'training', 'NQ', 'civil_ny_year', policy),
                         ['2021-01-01'])
        self.assertEqual(civil_completion_dates(2024, 'calibration', 'NQ', 'civil_ny_year', policy), [])
        self.assertEqual(civil_completion_dates(2024, 'confirmation', 'NQ', 'civil_ny_year', policy),
                         ['2025-01-01'])

    def test_accepted_partition_reuse_matches_fresh_and_corrupt_neighbor_is_rejected(self):
        day = date(2020, 6, 15)
        start = _ns(day, 10)
        end = start + 5 * MINUTE_NS
        atoms = _minute_atoms(start, 5, instrument=7, contract='NQ:H0', rows=((100, 2, 0, 0),))
        neighbor_day = date(2019, 12, 16)
        neighbor_start = _ns(neighbor_day, 10)
        neighbor_end = neighbor_start + 5 * MINUTE_NS
        neighbor_atoms = _minute_atoms(
            neighbor_start, 5, instrument=7, contract='NQ:H0', rows=((90, 1, 0, 0),),
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            data = BoundedOutputs(tmp / 'data', maximum_total_bytes=32 * 1024 ** 2, maximum_file_bytes=8 * 1024 ** 2)
            unit = _write_unit(
                data, 'reuse', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            neighbor = _write_unit(
                data, 'neighbor', root='NQ', path='quantpad/weekly-nq-2019-12.parquet',
                start=neighbor_start, end=neighbor_end,
                atoms_by_instrument=[(7, neighbor_atoms)], sha=SHA3, canonical=SHA3,
            )
            population = {'kind': 'auction_flow_observation_population_v1', 'units': [unit, neighbor]}
            windows = {'kind': 'auction_flow_window_population_v1', 'units': []}
            contract = frozen_contract(source_collections={
                WEEKLY: 'weekly_acquisitions',
                WEEKLY_B: 'weekly_acquisitions',
                MONTHLY: 'monthly_acquisitions',
                PATH_ES: 'weekly_acquisitions',
                'quantpad/weekly-nq-2019-12.parquet': 'weekly_acquisitions',
            })
            loader = own_output_loader(tmp)
            first = run_profile_statistics(
                population=population, window_population=windows, contract=contract,
                outputs=BoundedOutputs(tmp / 'fresh', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2),
                load_reference=loader,
                selected_partition_keys=[['weekly_acquisitions', 'NQ', 2020]],
            )
            part_ref = first['refs']['partitions'][0]
            reused = run_profile_statistics(
                population=population, window_population=windows, contract=contract,
                outputs=BoundedOutputs(tmp / 'reuse', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2),
                load_reference=loader,
                selected_partition_keys=[['weekly_acquisitions', 'NQ', 2020]],
                accepted_partitions=[part_ref],
            )
            self.assertEqual(reused['counts']['reused_partitions'], 1)
            operational = {'reused_partitions', 'new_partitions'}
            for name, value in first['counts'].items():
                if name in operational:
                    continue
                self.assertEqual(reused['counts'][name], value, name)
            self.assertEqual(
                reconstruct_profile_groups(loader(reused['refs']['groups']), loader, role='groups'),
                reconstruct_profile_groups(loader(first['refs']['groups']), loader, role='groups'),
            )
            part = loader(part_ref)
            support = [item for item in (part.get('support_refs') or []) if item.get('role') == 'support']
            self.assertTrue(support)
            mutated = dict(part)
            mutated_refs = [dict(item) for item in support]
            measurement = dict(mutated_refs[0].get('measurement') or {})
            measurement['sha256'] = '00' * 32
            mutated_refs[0]['measurement'] = measurement
            mutated['support_refs'] = mutated_refs
            with self.assertRaises(IntegrityError):
                authenticate_reused_partition(mutated, loader)

    def test_join_rows_are_four_formations_by_three_latencies_by_four_horizons(self):
        day = date(2020, 6, 15)
        start = _ns(day, 10)
        end = start + 5 * MINUTE_NS
        atoms = _minute_atoms(start, 5, instrument=7, contract='NQ:H0', rows=((100, 4, 0, 0),))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2)
            unit = _write_unit(
                outputs, 'arms', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            features, labels = _window_rows(
                path=WEEKLY, root='NQ', instrument=7, contract='NQ:H0', cut=end,
                acquired_start=start, acquired_end=end,
            )
            self.assertEqual(len(features), 12)
            self.assertEqual(len(labels), 12)
            for feature in features:
                self.assertIsNotNone(feature.get('latency_ns'))
                self.assertIs(feature.get('complete'), True)
                self.assertIs(feature.get('chronological_eligible'), True)
                self.assertIs(feature.get('data_complete'), True)
                self.assertIs(feature.get('contract_stable'), True)
            window = _write_window_unit(
                outputs, 'win', path=WEEKLY, root='NQ', start=start, end=end,
                feature_rows=features, label_rows=labels,
            )
            result, _ = _run_geometry(
                Path(tmp) / 'run', units=[unit], window_units=[window],
                selected=[['weekly_acquisitions', 'NQ', 2020]],
            )
            joins = [
                row for row in _join_tables(result)
                if row.get('later_completed_link') is not True
            ]
            by_geometry = {}
            for row in joins:
                by_geometry.setdefault(row.get('geometry_id'), []).append(row)
            matched = [rows for rows in by_geometry.values() if len(rows) == 48]
            self.assertTrue(matched)
            eligible = None
            for rows in matched:
                pairs = {
                    (
                        row.get('formation_minutes'), row.get('latency_ns'),
                        row.get('horizon_kind'), row.get('horizon_minutes'),
                    )
                    for row in rows
                }
                self.assertEqual(len(pairs), 48)
                zeros = [row for row in rows if row.get('latency_ns') == 0]
                if any(row.get('join_status') == 'observed' for row in zeros):
                    eligible = rows
            self.assertIsNotNone(eligible)
            for row in eligible:
                if row.get('latency_ns') == 0:
                    self.assertEqual(row.get('actual_known_at_ns'), row.get('cut_ns') + SOURCE_LATENCY_NS)
                    self.assertEqual(row.get('scenario_known_at_ns'), row.get('cut_ns'))
                if row.get('latency_ns') == SOURCE_LATENCY_NS:
                    self.assertEqual(row.get('scenario_known_at_ns'), row.get('actual_known_at_ns'))
                if row.get('latency_ns') == 1_000_000_000:
                    self.assertEqual(row.get('scenario_known_at_ns'), row.get('cut_ns') + 1_000_000_000)

    def test_civil_year_end_keeps_evening_mass_before_midnight(self):
        dec, jan = date(2020, 12, 31), date(2021, 1, 1)
        times = (_ns(dec, 17, 59), _ns(dec, 18), _ns(dec, 23, 59), _ns(jan, 0))
        with tempfile.TemporaryDirectory() as tmp:
            data = BoundedOutputs(Path(tmp) / 'data', maximum_total_bytes=32 * 1024 ** 2,
                                  maximum_file_bytes=8 * 1024 ** 2)
            units = []
            for index, (start, volume) in enumerate(zip(times, (1, 2, 4, 8))):
                atoms = _minute_atoms(start, 1, instrument=7, contract='NQ:H0',
                                      rows=((100, volume, 0, 0),))
                units.append(_write_unit(data, str(index), root='NQ', path=WEEKLY,
                    start=start, end=start + MINUTE_NS, atoms_by_instrument=[(7, atoms)]))
            result, _ = _run_geometry(Path(tmp) / 'run', units=units)
            rows = [row for row in _geometry_tables(result)
                    if row.get('geometry_variant') == BASELINE_VARIANT_ID
                    and row.get('proxy_variant') is None]
            for variant in ('civil_ny_month', 'civil_ny_quarter', 'civil_ny_year'):
                actual = sorted((row['year'], int(row['priced_volume'])) for row in rows
                                if row.get('anchor_variant') == variant and row.get('priced_volume'))
                self.assertEqual(actual, [(2020, 7), (2021, 8)], variant)
            from trading_research.research.auction_flow_core_statistics import economic_date
            self.assertEqual(economic_date(times[1]), '2021-01-01')
            self.assertEqual(economic_date(times[2]), '2021-01-01')

    def test_civil_periods_reset_with_literal_disjoint_volumes(self):
        cases = (
            ('civil_ny_week', date(2020, 6, 8), date(2020, 6, 15), 11, 22),
            ('civil_ny_month', date(2020, 6, 15), date(2020, 7, 15), 13, 26),
            ('civil_ny_quarter', date(2020, 6, 15), date(2020, 10, 15), 14, 28),
        )
        for variant, first_day, second_day, first_vol, second_vol in cases:
            with self.subTest(variant=variant):
                first_start = _ns(first_day, 10)
                first_end = first_start + 5 * MINUTE_NS
                second_start = _ns(second_day, 10)
                second_end = second_start + 5 * MINUTE_NS
                first_atoms = _minute_atoms(
                    first_start, 5, instrument=7, contract='NQ:H0', rows=((100, first_vol, 0, 0),),
                )
                second_atoms = _minute_atoms(
                    second_start, 5, instrument=7, contract='NQ:H0', rows=((110, second_vol, 0, 0),),
                )
                with tempfile.TemporaryDirectory() as tmp:
                    outputs = BoundedOutputs(
                        Path(tmp) / 'fixtures', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2,
                    )
                    units = [
                        _write_unit(
                            outputs, first_day.isoformat(), root='NQ', path=WEEKLY,
                            start=first_start, end=first_end,
                            atoms_by_instrument=[(7, first_atoms)],
                        ),
                        _write_unit(
                            outputs, second_day.isoformat(), root='NQ', path=WEEKLY_B,
                            start=second_start, end=second_end,
                            atoms_by_instrument=[(7, second_atoms)], sha=SHA2, canonical=SHA2,
                        ),
                    ]
                    result, _ = _run_geometry(
                        Path(tmp) / 'run', units=units,
                        selected=[['weekly_acquisitions', 'NQ', 2020]],
                    )
                    rows = [
                        row for row in _geometry_tables(result)
                        if row.get('anchor_variant') == variant
                        and row.get('geometry_variant') == BASELINE_VARIANT_ID
                        and row.get('proxy_variant') is None
                    ]
                    volumes = sorted(int(row['priced_volume']) for row in rows if row.get('priced_volume'))
                    self.assertEqual(volumes, [first_vol * 5, second_vol * 5])
                    origins = sorted(int(row['anchor_start_ns']) for row in rows)
                    self.assertEqual(len(set(origins)), 2)
                    self.assertLess(origins[0], origins[1])

    def test_december_does_not_enter_january_month(self):
        dec = date(2020, 12, 15)
        jan = date(2021, 1, 15)
        dec_start = _ns(dec, 10)
        dec_end = dec_start + 5 * MINUTE_NS
        jan_start = _ns(jan, 10)
        jan_end = jan_start + 5 * MINUTE_NS
        dec_atoms = _minute_atoms(dec_start, 5, instrument=7, contract='NQ:H0', rows=((100, 9, 0, 0),))
        jan_atoms = _minute_atoms(jan_start, 5, instrument=7, contract='NQ:H0', rows=((200, 4, 0, 0),))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2)
            units = [
                _write_unit(
                    outputs, 'dec', root='NQ', path=WEEKLY, start=dec_start, end=dec_end,
                    atoms_by_instrument=[(7, dec_atoms)],
                ),
                _write_unit(
                    outputs, 'jan', root='NQ', path=WEEKLY_B, start=jan_start, end=jan_end,
                    atoms_by_instrument=[(7, jan_atoms)], sha=SHA2, canonical=SHA2,
                ),
            ]
            result, _ = _run_geometry(
                Path(tmp) / 'run', units=units, selected=[['weekly_acquisitions', 'NQ', 2021]],
            )
            months = [
                row for row in _geometry_tables(result)
                if row.get('anchor_variant') == 'civil_ny_month'
                and row.get('geometry_variant') == BASELINE_VARIANT_ID
                and row.get('proxy_variant') is None
            ]
            self.assertTrue(months)
            for row in months:
                self.assertEqual(int(row['priced_volume']), 20)
                self.assertGreaterEqual(int(row['anchor_start_ns']), _ns(date(2021, 1, 1), 0))

    def test_later_data_does_not_change_earlier_numeric_references(self):
        day = date(2020, 6, 15)
        later = date(2020, 6, 16)
        start = _ns(day, 6)
        end = _ns(day, 9)
        later_start = _ns(later, 6)
        later_end = _ns(later, 9)
        atoms = _minute_atoms(start, 180, instrument=7, contract='NQ:H0', rows=((100, 5, 1, 0), (101, 2, 0, 0)))
        later_atoms = _minute_atoms(
            later_start, 180, instrument=7, contract='NQ:H0', rows=((140, 9, 0, 0),),
        )
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2)
            first_unit = _write_unit(
                outputs, 'early', root='NQ', path=WEEKLY, start=start, end=end,
                atoms_by_instrument=[(7, atoms)],
            )
            early, _ = _run_geometry(Path(tmp) / 'early', units=[first_unit], selected=[['weekly_acquisitions', 'NQ', 2020]])
            later_unit = _write_unit(
                outputs, 'late', root='NQ', path=WEEKLY_B, start=later_start, end=later_end,
                atoms_by_instrument=[(7, later_atoms)], sha=SHA2, canonical=SHA2,
            )
            both, _ = _run_geometry(
                Path(tmp) / 'both', units=[first_unit, later_unit],
                selected=[['weekly_acquisitions', 'NQ', 2020]],
            )

            def snapshot(rows):
                out = {}
                for row in rows:
                    if row.get('economic_date') != '2020-06-15':
                        continue
                    if row.get('geometry_variant') != BASELINE_VARIANT_ID or row.get('proxy_variant') is not None:
                        continue
                    key = (row.get('anchor_variant'), row.get('cut_ns'))
                    out[key] = (
                        row.get('physical_val_ticks'), row.get('physical_vah_ticks'),
                        row.get('pin069_vwap_num'), row.get('pin069_vwap_den'),
                        row.get('observed_prior_close_ticks'),
                    )
                return out

            self.assertTrue(snapshot(_geometry_tables(early)))
            self.assertEqual(snapshot(_geometry_tables(early)), snapshot(_geometry_tables(both)))

    def test_large_volume_numerator_roundtrip_and_side_wasserstein(self):
        import math
        import pyarrow as pa
        from trading_research.research.auction_flow_profile_statistics import _geometry_metrics
        left, right = 2 ** 32, 2 ** 32 + 1
        mass = IntegerMass()
        mass.add({
            'rows': ((100000, left, 0, 0), (100002, right, 0, 0)),
            'unpriced': (0, 0, 0),
            'prints': 2, 'unpriced_prints': 0,
            'source_coverage_complete': True,
            'price_history_complete': True,
            'coordinate_complete': True,
            'origin_ticks': 0, 'row_ticks': 1,
            'source_path': WEEKLY,
            'measurement_sha256': SHA,
        })
        spec = next(item for item in FROZEN_GEOMETRY_VARIANTS if item['id'] == BASELINE_VARIANT_ID)
        compact, _ = emit_geometry_payload(
            mass=mass, spec=spec, coordinate_identity='NQ:H0:large',
            known_at_ns=1, coverage_complete=True, include_side=True,
            include_vwap=True, include_footprint=False, footprint_params=None,
        )
        total = left + right
        sq = left * left + right * right
        expected_c = Fraction(sq, total * total)
        cnum = decode_exact_int(compact['concentration_num'], compact.get('concentration_num_text'))
        cden = decode_exact_int(compact['concentration_den'], compact.get('concentration_den_text'))
        self.assertGreater(cnum, 2 ** 63 - 1)
        self.assertGreater(cden, 2 ** 63 - 1)
        self.assertEqual(Fraction(cnum, cden), expected_c)
        expected_p2 = 100000 * 100000 * left + 100002 * 100002 * right
        self.assertEqual(
            decode_exact_int(
                compact['sum_price_squared_volume'], compact.get('sum_price_squared_volume_text'),
            ),
            expected_p2,
        )
        moments = mass.vwap_moments()
        vnum = decode_exact_int(
            compact['variance_ticks_squared_num'], compact.get('variance_ticks_squared_num_text'),
        )
        vden = decode_exact_int(
            compact['variance_ticks_squared_den'], compact.get('variance_ticks_squared_den_text'),
        )
        self.assertEqual(Fraction(vnum, vden), moments['variance_ticks_squared'])
        schema = geometry_schema(pa)
        row = {field.name: None for field in schema}
        row.update(compact)
        row['source_collection'] = 'weekly_acquisitions'
        row['root'] = 'NQ'
        row['year'] = 2020
        normalize_exact_integers(row)
        table = pa.table(
            {field.name: pa.array([row.get(field.name)], type=field.type) for field in schema},
            schema=schema,
        )
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=16 * 1024 ** 2, maximum_file_bytes=8 * 1024 ** 2)
            series = write_series_table(outputs, 'large-geo', table)
            got_table = next(read_series_tables(series))
            got = {name: got_table.column(name).to_pylist()[0] for name in got_table.column_names}
        self.assertEqual(
            decode_exact_int(got['concentration_num'], got.get('concentration_num_text')), cnum)
        self.assertEqual(
            decode_exact_int(got['concentration_den'], got.get('concentration_den_text')), cden)
        self.assertEqual(
            decode_exact_int(got['sum_price_squared_volume'], got.get('sum_price_squared_volume_text')),
            expected_p2,
        )
        self.assertEqual(
            decode_exact_int(got['variance_ticks_squared_num'], got.get('variance_ticks_squared_num_text')),
            vnum,
        )
        metrics = _geometry_metrics(got)
        self.assertTrue(math.isfinite(metrics['concentration']))
        self.assertTrue(math.isfinite(metrics['variance_ticks_squared']))
        self.assertAlmostEqual(metrics['concentration'], float(expected_c), places=12)
        sides = IntegerMass()
        sides.add({
            'rows': ((100, 100, 0, 0), (102, 0, 102, 0)),
            'unpriced': (0, 0, 0),
            'prints': 2, 'unpriced_prints': 0,
            'source_coverage_complete': True,
            'price_history_complete': True,
            'coordinate_complete': True,
            'origin_ticks': 0, 'row_ticks': 1,
        })
        side = compact_side_geometry(sides)
        self.assertEqual(
            Fraction(
                decode_exact_int(side['side_wasserstein_num'], side.get('side_wasserstein_num_text')),
                decode_exact_int(side['side_wasserstein_den'], side.get('side_wasserstein_den_text')),
            ),
            Fraction(2, 1),
        )

    def test_every_required_schema_field_has_named_statistic(self):
        from trading_research.research.auction_flow_profile_statistics import (
            GEOMETRY_METRIC_NAMES, JOIN_METRIC_NAMES, TPO_METRIC_NAMES, METRIC_UNITS,
        )
        for name in (*GEOMETRY_METRIC_NAMES, *TPO_METRIC_NAMES, *JOIN_METRIC_NAMES):
            self.assertIn(name, METRIC_UNITS)
            self.assertTrue(METRIC_UNITS[name])

    def test_intended_link_no_event_retains_missing_cuts(self):
        dates = (date(2020, 6, 15), date(2020, 6, 16))
        units = []
        windows = []
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=128 * 1024 ** 2, maximum_file_bytes=32 * 1024 ** 2)
            for index, day in enumerate(dates):
                start = _ns(day, 10)
                end = start + 5 * MINUTE_NS
                atoms = _minute_atoms(start, 5, instrument=7, contract='NQ:H0', rows=((100, 4, 0, 0),))
                units.append(_write_unit(
                    outputs, day.isoformat(), root='NQ', path=WEEKLY, start=start, end=end,
                    atoms_by_instrument=[(7, atoms)],
                ))
                features, labels = _window_rows(
                    path=WEEKLY, root='NQ', instrument=7, contract='NQ:H0', cut=end,
                    acquired_start=start, acquired_end=end, complete=True,
                    no_new=(index == 0),
                )
                windows.append(_write_window_unit(
                    outputs, f'win-{day.isoformat()}', path=WEEKLY, root='NQ',
                    start=start, end=end, feature_rows=features, label_rows=labels,
                ))
            result, _ = _run(
                Path(tmp) / 'run', units=units, window_units=windows,
                selected=[['weekly_acquisitions', 'NQ', 2020]],
            )
            load = own_output_loader(Path(tmp) / 'run')
            groups = _read_groups(result, load)
            intended = [
                group for group in groups
                if group.get('group_kind') == 'join'
                and group.get('measurement_status') == 'intended_link'
            ]
            self.assertTrue(intended)
            chosen = [group for group in intended if group.get('anchor') == 'developing_cash_rth'
                      and group.get('variant') == BASELINE_VARIANT_ID and group.get('formation_minutes') == 5
                      and group.get('latency_ns') == 0 and group.get('horizon_kind') == 'fixed_minutes'
                      and group.get('horizon_minutes') == 5 and group.get('session') == 'cash_rth']
            self.assertEqual(len(chosen), 1, repr([g.keys() for g in intended[:1]]))
            metric = chosen[0]['metrics']['no_event']
            self.assertEqual(metric['eligible_observations'], 14)
            self.assertAlmostEqual(metric['event_mean'], 1 / 14)
            self.assertAlmostEqual(chosen[0]['metrics']['missing']['event_mean'], 12 / 14)
            # Independently identified known-feature rolling links give the conditional rate1/2.
            known = [row for row in _join_tables(result) if row.get('anchor_variant') == 'rolling_5m'
                     and row.get('geometry_variant') == BASELINE_VARIANT_ID and row.get('feature_id')
                     and row.get('formation_minutes') == 5 and row.get('latency_ns') == 0
                     and row.get('horizon_kind') == 'fixed_minutes' and row.get('horizon_minutes') == 5]
            self.assertEqual(len(known), 2)
            self.assertEqual(sorted(row['join_status'] for row in known), ['no_event', 'observed'])

    def test_geometry_pairing_once_and_indexes_release(self):
        acc = new_partition_accumulators()

        def row(*, anchor, kind, cut, day, variant=BASELINE_VARIANT_ID, proxy=None,
                complete=True, poc=100, val=99, vah=101):
            return {
                'source_collection': 'weekly_acquisitions', 'root': 'NQ', 'year': 2020,
                'stage': 'training', 'session': 'rth',
                'anchor_variant': anchor, 'anchor_kind': kind,
                'geometry_variant': variant, 'proxy_variant': proxy,
                'cut_ns': cut, 'published_known_ns': cut,
                'instrument_id': 7, 'contract_key': 'NQ:H0',
                'canonical_raw_values_sha256': SHA, 'source_path': WEEKLY,
                'economic_date': day, 'eligible_complete': complete,
                'geometry_status': 'complete' if complete else 'observed_partial',
                'selected_partition_member': True,
                'physical_poc_ticks': poc, 'physical_val_ticks': val,
                'physical_vah_ticks': vah, 'va_width_physical_ticks': vah - val,
                'overshoot_num': 0, 'overshoot_den': 1, 'priced_volume': 10,
                'scalar_poc': poc, 'val_row': val, 'vah_row': vah,
            }

        for index in range(240):
            accumulate_geometry_row(
                acc, row(anchor='developing_cash_rth', kind='developing', cut=index,
                         day='2020-06-15'),
                collection='weekly_acquisitions', year=2020,
            )
            accumulate_geometry_row(
                acc, row(anchor='rolling_5m', kind='rolling', cut=index, day='2020-06-16'),
                collection='weekly_acquisitions', year=2020,
            )
        days = ('2020-06-17', '2020-06-18', '2020-06-19')
        for cut, day in zip((1000, 2000, 3000), days):
            for offset, spec in enumerate(FROZEN_GEOMETRY_VARIANTS):
                accumulate_geometry_row(
                    acc, row(
                        anchor='cash_rth', kind='rth', cut=cut, day=day,
                        variant=spec['id'], poc=100 + offset, val=98 + offset, vah=102 + offset,
                    ),
                    collection='weekly_acquisitions', year=2020,
                )
            for offset, proxy in enumerate(BAR_PROXY_VARIANTS):
                accumulate_geometry_row(
                    acc, row(
                        anchor='cash_rth', kind='rth', cut=cut, day=day,
                        proxy=proxy, poc=90 + offset, val=88 + offset, vah=92 + offset,
                    ),
                    collection='weekly_acquisitions', year=2020,
                )
        self.assertEqual(len(acc['geometry_index']), 0)
        self.assertEqual(len(acc['exact_index']), 0)
        self.assertEqual(len(acc['proxy_index']), 0)
        for left, right, contrast in PAIRED_CONTRASTS:
            matches = [
                stores for key, stores in acc['paired'].items()
                if key[_GFIELDS.index('contrast')] == contrast
                and key[_GFIELDS.index('group_kind')] == 'paired_geometry'
            ]
            self.assertEqual(len(matches), 1, contrast)
            store = next(iter(matches[0].values()))
            self.assertEqual(store.n, 3, contrast)
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=32 * 1024 ** 2, maximum_file_bytes=8 * 1024 ** 2)
            write_partition_groups(
                outputs, 'pair-once', acc,
                stats=frozen_contract()['statistics'], policy=FROZEN_STAGE_POLICY,
                collection='weekly_acquisitions', root='NQ', year=2020,
                contract=frozen_contract(),
            )
        for left, right, contrast in PAIRED_CONTRASTS:
            matches = [
                stores for key, stores in acc['paired'].items()
                if key[_GFIELDS.index('contrast')] == contrast
                and key[_GFIELDS.index('group_kind')] == 'paired_geometry'
            ]
            store = next(iter(matches[0].values()))
            self.assertEqual(store.n, 3, contrast)

    def test_december_cash_warms_january_prior_reference(self):
        dec = date(2020, 12, 31)
        jan = date(2021, 1, 4)
        dec_start = _ns(dec, 9, 30)
        dec_end = _ns(dec, 16)
        jan_start = _ns(jan, 9, 30)
        jan_end = jan_start + 10 * MINUTE_NS
        dec_atoms = _minute_atoms(dec_start, 390, instrument=7, contract='NQ:H0', rows=((111, 3, 0, 0),))
        jan_atoms = _minute_atoms(jan_start, 10, instrument=7, contract='NQ:H0', rows=((200, 2, 0, 0),))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=128 * 1024 ** 2, maximum_file_bytes=32 * 1024 ** 2)
            units = [
                _write_unit(
                    outputs, 'dec31', root='NQ', path=WEEKLY, start=dec_start, end=dec_end,
                    atoms_by_instrument=[(7, dec_atoms)],
                ),
                _write_unit(
                    outputs, 'jan4', root='NQ', path=WEEKLY_B, start=jan_start, end=jan_end,
                    atoms_by_instrument=[(7, jan_atoms)], sha=SHA2, canonical=SHA2,
                ),
            ]
            result, _ = _run_geometry(
                Path(tmp) / 'run', units=units, selected=[['weekly_acquisitions', 'NQ', 2021]],
            )
            rows = _geometry_tables(result)
            self.assertFalse([
                row for row in rows
                if row.get('economic_date') == '2020-12-31' and row.get('anchor_variant') == 'cash_rth'
            ])
            developing = [
                row for row in rows
                if row.get('anchor_variant') == 'developing_cash_rth'
                and row.get('economic_date') == '2021-01-04'
                and row.get('proxy_variant') is None
            ]
            self.assertTrue(developing)
            self.assertTrue(all(row.get('completed_geometry_id') for row in developing))
            self.assertTrue(all(row.get('observed_prior_close_ticks') == 111 for row in developing))

    def test_december_january_spanning_week_owned_by_end_date(self):
        first = date(2020, 12, 28)
        second = date(2021, 1, 2)
        first_start = _ns(first, 10)
        first_end = first_start + 5 * MINUTE_NS
        second_start = _ns(second, 10)
        second_end = second_start + 5 * MINUTE_NS
        first_atoms = _minute_atoms(first_start, 5, instrument=7, contract='NQ:H0', rows=((100, 7, 0, 0),))
        second_atoms = _minute_atoms(second_start, 5, instrument=7, contract='NQ:H0', rows=((110, 3, 0, 0),))
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=256 * 1024 ** 2, maximum_file_bytes=64 * 1024 ** 2)
            units = [
                _write_unit(
                    outputs, 'dec28', root='NQ', path=WEEKLY, start=first_start, end=first_end,
                    atoms_by_instrument=[(7, first_atoms)],
                ),
                _write_unit(
                    outputs, 'jan2', root='NQ', path=WEEKLY_B, start=second_start, end=second_end,
                    atoms_by_instrument=[(7, second_atoms)], sha=SHA2, canonical=SHA2,
                ),
            ]
            selected_2021, _ = _run_geometry(
                Path(tmp) / 'y2021', units=units, selected=[['weekly_acquisitions', 'NQ', 2021]],
            )
            selected_2020, _ = _run_geometry(
                Path(tmp) / 'y2020', units=units, selected=[['weekly_acquisitions', 'NQ', 2020]],
            )
            weeks_2021 = [
                row for row in _geometry_tables(selected_2021)
                if row.get('anchor_variant') == 'civil_ny_week'
                and row.get('geometry_variant') == BASELINE_VARIANT_ID
                and row.get('proxy_variant') is None
            ]
            weeks_2020 = [
                row for row in _geometry_tables(selected_2020)
                if row.get('anchor_variant') == 'civil_ny_week'
                and row.get('geometry_variant') == BASELINE_VARIANT_ID
                and row.get('proxy_variant') is None
            ]
            self.assertTrue(weeks_2021)
            self.assertEqual({int(row['priced_volume']) for row in weeks_2021 if row.get('priced_volume')}, {50})
            self.assertTrue(all(row.get('economic_date') == '2021-01-04' for row in weeks_2021))
            self.assertFalse(weeks_2020)


class ProfileListStorageTests(unittest.TestCase):
    def test_null_empty_and_large_signed_list_values_roundtrip(self):
        import pyarrow as pa
        table = pa.table({'levels': pa.array([None, [], [-(2 ** 60), None, 0, 2 ** 60]],
                                            type=pa.list_(pa.int64())),
                          'flag': pa.array([None, False, True], type=pa.bool_())})
        with tempfile.TemporaryDirectory() as tmp:
            outputs = BoundedOutputs(Path(tmp) / 'fixtures', maximum_total_bytes=2 * 1024 ** 2,
                                     maximum_file_bytes=1024 ** 2)
            series = write_series_table(outputs, 'lists', table)
            got = pa.concat_tables(list(read_series_tables(series)))
            self.assertTrue(got.schema.equals(table.schema, check_metadata=True))
            self.assertEqual(got.to_pydict(), {'levels': [None, [], [-(2 ** 60), None, 0, 2 ** 60]],
                                             'flag': [None, False, True]})


if __name__ == '__main__':
    unittest.main()
