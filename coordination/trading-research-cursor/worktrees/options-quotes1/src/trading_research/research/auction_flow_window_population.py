"""Consumer driver from admitted observation/trade series to causal window tables.

Root owns definitions, helper corrections, registration and execution. This
module does not scan raw MBP, invent acquired bounds, join acquisitions, or
claim family completion. Neighbor support is previous/current/next UTC day of
the same physical file only.
"""
from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.time import MINUTE, NS
from trading_research.operations.artifacts import digest, file_digest
from trading_research.research.auction_flow_window_links import join_window_eligibility
from trading_research.research.auction_flow_production import source_variant, window_artifact_prefix
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries, read_series_tables
from trading_research.research.auction_flow_windows import TRADE_FIELDS


KIND = 'auction_flow_window_population_v1'
UNIT_KIND = 'auction_flow_window_unit_v1'
POPULATION_KIND = 'auction_flow_observation_population_v1'
CONTRACT_KIND = 'auction_flow_causal_window_links_contract_v1'
CONTRACT_VERSION = 1
CUT_CADENCE_NS = 5 * MINUTE
DAY_NS = 24 * 60 * MINUTE
LOOKBACK_NS = 240 * MINUTE
LOOKAHEAD_NS = 60 * MINUTE + NS
FORMATION_MINUTES = (5, 15, 60, 240)
LATENCY_NS = (250_000_000, 0, 1_000_000_000)
FORWARD_HORIZONS_MINUTES = (5, 15, 60)
SOURCE_SHARDS = 16
BATCH_ROWS = 65536
_SHA_LEN = 64
_INT64_MIN = -(2 ** 63)
_INT64_MAX = 2 ** 63 - 1
_STAGE_NAMES = ('training', 'development', 'calibration', 'confirmation')
_IDENTITY_KEYS = (
    'root', 'source_path', 'source_metadata_sha256', 'source_variant',
    'acquired_event_start_ns', 'acquired_event_end_ns',
)
OPERATIONAL_CONTRACT_FIELDS = (
    'phase', 'selected_unit_ids', 'accepted_window_units',
    'source_paths', 'parallel_keys', 'pilot_unit_ids',
)



def _pa():
    import pyarrow as pa
    return pa


def _pc():
    import pyarrow.compute as pc
    return pc


def _mapping(value, *, what):
    if not isinstance(value, dict):
        raise IntegrityError(f'{what} must be an object')
    return value


def _text(value, *, what, allow_empty=False):
    if type(value) is not str or (not value and not allow_empty):
        raise IntegrityError(f'{what} must be a concrete string')
    return value


def _py_int(value, *, what):
    if value is None:
        return None
    if type(value) is bool:
        raise IntegrityError(f'{what} must be an exact integer')
    result = int(value)
    if not _INT64_MIN <= result <= _INT64_MAX:
        raise IntegrityError(f'{what} exceeds the exact int64 domain')
    return result


def _add_checked(*values, what):
    total = 0
    for value in values:
        total += int(value)
        if not _INT64_MIN <= total <= _INT64_MAX:
            raise IntegrityError(f'{what} exceeds the exact int64 domain')
    return total












def encode_window_unit_id(source_path, start_ns, end_ns):
    path = _text(source_path, what='source_path')
    start = _py_int(start_ns, what='event_start_ns')
    end = _py_int(end_ns, what='event_end_ns')
    if start is None or end is None or not start < end:
        raise IntegrityError('window unit identity requires a positive half-open [start, end)')
    return [path, start, end]


def decode_window_unit_id(key):
    if type(key) is str and len(key) == _SHA_LEN:
        return {'receipt_sha256': key}
    if not isinstance(key, (list, tuple)) or len(key) != 3:
        raise IntegrityError('window unit id must be [source_path, start_ns, end_ns] or a receipt sha256')
    path, start, end = key
    return {'source_path': path, 'event_start_ns': int(start), 'event_end_ns': int(end)}


def source_path_shard(source_path, *, shards=SOURCE_SHARDS):
    if type(shards) is not int or shards != SOURCE_SHARDS:
        raise IntegrityError('source-path shards are frozen to sixteen workers')
    path = _text(source_path, what='source_path')
    return int.from_bytes(hashlib.sha256(path.encode()).digest()[:8], 'big') % shards


def utc_day_start_ns(event_start_ns):
    start = _py_int(event_start_ns, what='event_start_ns')
    return (start // DAY_NS) * DAY_NS


def scientific_contract_digest(contract):
    rec = _mapping(contract, what='contract')
    return digest({name: rec[name] for name in rec if name not in OPERATIONAL_CONTRACT_FIELDS})


def _series_digest(series):
    if not isinstance(series, dict):
        return None
    files = []
    for item in series.get('files') or []:
        groups = [(g.get('sha256'), g.get('rows')) for g in item.get('row_group_values') or []]
        files.append((item.get('sha256'), item.get('rows'), groups))
    return {'rows': series.get('rows'), 'schema': series.get('schema'), 'files': files}


def _receipt_sha(unit):
    reference = unit.get('receipt') or {}
    return reference.get('sha256')


def _unit_id(unit):
    return encode_window_unit_id(
        unit['source_path'], unit['source_window_start_ns'], unit['source_window_end_ns'])


def window_unit_cache_key(*, unit_id, receipt_sha256, observation_series, neighbor_refs,
                          source_identity, contract_digest):
    return digest({
        'unit_id': unit_id,
        'receipt_sha256': receipt_sha256,
        'observation': _series_digest(observation_series),
        'neighbors': neighbor_refs,
        'source_identity': source_identity,
        'contract_digest': contract_digest,
    })


def empty_trade_table(schema=None):
    """Logical empty trades; no invented event rows."""
    pa = _pa()
    if schema is not None:
        return pa.table({field.name: pa.array([], type=field.type) for field in schema}, schema=schema)
    fields = []
    for name in TRADE_FIELDS:
        if name in ('source_key', 'raw_side', 'raw_action'):
            fields.append(pa.field(name, pa.string()))
        elif name == 'price_valid':
            fields.append(pa.field(name, pa.int64()))
        else:
            fields.append(pa.field(name, pa.int64()))
    schema = pa.schema(fields)
    return pa.table({field.name: pa.array([], type=field.type) for field in schema}, schema=schema)


def empty_observation_table():
    from trading_research.research.auction_flow_observation_tables import observation_schema
    pa = _pa()
    schema = observation_schema()
    return pa.table({field.name: pa.array([], type=field.type) for field in schema}, schema=schema)


def _empty_table(schema):
    pa = _pa()
    return pa.table({field.name: pa.array([], type=field.type) for field in schema}, schema=schema)


def _no_instrument_tables():
    from trading_research.research.auction_flow_window_links import feature_schema, label_schema
    return _empty_table(feature_schema()), _empty_table(label_schema())


def _concat_ordered(tables):
    pa = _pa()
    present = [table for table in tables if table is not None]
    if not present:
        raise IntegrityError('ordered day concat lost its member tables')
    nonempty = [table for table in present if len(table)]
    schema = nonempty[0].schema if nonempty else present[0].schema
    aligned = [_empty_table(schema) if not len(table) else table for table in present]
    if len(aligned) == 1:
        return aligned[0]
    return pa.concat_tables(aligned)


def _read_logical(series, *, empty):
    if not isinstance(series, dict) or series.get('rows', 0) == 0 or not series.get('files'):
        return empty, False
    tables = list(read_series_tables(series))
    if not tables:
        return empty, True
    if len(tables) == 1:
        return tables[0], True
    return _concat_ordered(tables), True


def _clip_observations(table, support_start, support_end):
    pc = _pc()
    keep = pc.and_(
        pc.less(table['event_start_ns'], support_end),
        pc.greater(table['event_end_ns'], support_start),
    )
    return table.filter(keep)


def _clip_trades(table, support_start, support_end):
    pc = _pc()
    keep = pc.and_(
        pc.greater_equal(table['t'], support_start),
        pc.less(table['t'], support_end),
    )
    return table.filter(keep)


def _day_atom_count(table, cut_start, cut_end):
    if not len(table) or 'event_start_ns' not in table.column_names:
        return 0
    pc = _pc()
    keep = pc.and_(
        pc.greater_equal(table['event_start_ns'], cut_start),
        pc.less(table['event_start_ns'], cut_end),
    )
    return int(len(table.filter(keep)))


def _instrument_ids(table, cut_start, cut_end):
    if not len(table) or 'instrument_id' not in table.column_names:
        return ()
    pc = _pc()
    day = table.filter(pc.and_(
        pc.greater_equal(table['event_start_ns'], cut_start),
        pc.less(table['event_start_ns'], cut_end),
    ))
    if not len(day):
        return ()
    return tuple(int(value) for value in _pc().unique(day['instrument_id']).to_pylist() if value is not None)


def _filter_instruments(table, instrument_ids, column='instrument_id'):
    if column not in table.column_names:
        return table.slice(0, 0)
    if not instrument_ids:
        return table.slice(0, 0)
    pa = _pa()
    return table.filter(_pc().is_in(
        table[column], value_set=pa.array(list(instrument_ids), type=table.schema.field(column).type)))


def _trade_series(receipt):
    storage = receipt.get('event_storage') or receipt.get('artifacts') or {}
    series = storage.get('trades')
    if series is None:
        raise IntegrityError('receipt lost its logical trades series')
    return series


def _acquired_bounds(receipt):
    unit = _mapping(receipt.get('unit'), what='receipt.unit')
    start = unit.get('observed_file_start_ns')
    end = unit.get('observed_file_end_ns')
    if type(start) is not int or type(end) is not int:
        raise IntegrityError('receipt.unit must retain observed_file_start_ns/observed_file_end_ns')
    acquired_end = end + 1
    if not start < acquired_end:
        raise IntegrityError('acquired physical file event bounds must be a half-open [start, end)')
    return start, acquired_end


def _source_identity(unit, receipt):
    rec_unit = _mapping(receipt.get('unit'), what='receipt.unit')
    path = _text(unit['source_path'], what='source_path')
    sha = rec_unit.get('source_metadata_sha256') or receipt.get('source_metadata_sha256')
    if type(sha) is not str or len(sha) != _SHA_LEN:
        raise IntegrityError('original receipt.source_metadata_sha256 is required')
    start, end = _acquired_bounds(receipt)
    return {
        'root': _text(unit['root'], what='root'),
        'source_path': path,
        'source_metadata_sha256': sha,
        'source_variant': source_variant(path),
        'acquired_event_start_ns': start,
        'acquired_event_end_ns': end,
    }


def _flag_count(table, name, *, true=True):
    if name not in table.column_names:
        return 0
    values = table[name].to_pylist()
    return sum(1 for value in values if value is true)


def _either_flag_count(table, first, second):
    return sum(a is True or b is True for a, b in zip(table[first].to_pylist(), table[second].to_pylist()))


def _complete_features(table):
    required = ('atoms_complete', 'coordinate_complete', 'supplied_raw_coordinate_stable',
                'source_instrument_presence', 'source_coverage_complete',
                'flow_history_complete', 'price_history_complete')
    if not all(name in table.column_names for name in required):
        return 0
    return sum(all(values) for values in zip(*(table[name].to_pylist() for name in required)))


def _schema_sha256(table):
    return hashlib.sha256(str(table.schema).encode()).hexdigest()


def _write_series(outputs, name, table):
    series = ParquetSeries(outputs, name, encoding='plain')
    if not len(table):
        series.append(table)
    else:
        offset = 0
        while offset < len(table):
            amount = min(BATCH_ROWS, len(table) - offset)
            series.append(table.slice(offset, amount))
            offset += amount
    return series.finish()


def _is_unavailable(unit):
    rows = unit.get('atomic_rows', unit.get('observation_rows'))
    instruments = unit.get('instruments')
    status = unit.get('source_window_status')
    return (
        status == 'unavailable_source_window'
        or rows == 0
        or instruments == 0
    )


def _index_units(units):
    by_id, by_sha, by_day = {}, {}, {}
    for unit in units:
        ident = tuple(_unit_id(unit))
        if ident in by_id:
            raise IntegrityError('observation population repeats a source-path/start/end window')
        by_id[ident] = unit
        sha = _receipt_sha(unit)
        if type(sha) is str:
            if sha in by_sha:
                raise IntegrityError('observation population repeats a receipt sha256')
            by_sha[sha] = unit
        day = (unit['source_path'], utc_day_start_ns(unit['source_window_start_ns']))
        if day in by_day:
            raise IntegrityError('observation population repeats a physical-file UTC day')
        by_day[day] = unit
    return by_id, by_sha, by_day


def _resolve_selected(units, selected_unit_ids, by_id, by_sha):
    if selected_unit_ids is None:
        return list(units)
    if not isinstance(selected_unit_ids, (list, tuple)) or not selected_unit_ids:
        raise IntegrityError('selected_unit_ids must be a nonempty list when provided')
    selected, seen = [], set()
    for key in selected_unit_ids:
        if type(key) is str and key in by_sha:
            unit = by_sha[key]
        else:
            decoded = decode_window_unit_id(key)
            if 'receipt_sha256' in decoded:
                unit = by_sha.get(decoded['receipt_sha256'])
            else:
                unit = by_id.get((decoded['source_path'], decoded['event_start_ns'], decoded['event_end_ns']))
        if unit is None:
            raise IntegrityError('selected_unit_ids are not members of the observation population')
        ident = tuple(_unit_id(unit))
        if ident in seen:
            raise IntegrityError('selected_unit_ids contain a duplicate')
        seen.add(ident)
        selected.append(unit)
    return selected


def plan_window_units(population, selected_unit_ids=None, *, source_paths=None):
    """Pure metadata plan: selected days plus same-file previous/next UTC members."""
    rec = _mapping(population, what='population')
    if rec.get('kind') != POPULATION_KIND:
        raise IntegrityError('authenticated observation population required')
    units = rec.get('units')
    if not isinstance(units, list) or not units:
        raise IntegrityError('observation population lost its unit summaries')
    by_id, by_sha, by_day = _index_units(units)
    if source_paths is not None:
        if not isinstance(source_paths, list) or not source_paths:
            raise IntegrityError('source_paths filter must be a nonempty list when provided')
        known = {unit['source_path'] for unit in units}
        if any(path not in known for path in source_paths):
            raise IntegrityError('source_paths are not members of the observation population')
        if len(set(source_paths)) != len(source_paths):
            raise IntegrityError('source_paths contain a duplicate')
    selected = _resolve_selected(units, selected_unit_ids, by_id, by_sha)
    if source_paths is not None:
        selected = [unit for unit in selected if unit['source_path'] in source_paths]
        if {unit['source_path'] for unit in selected} != set(source_paths) and selected_unit_ids is None:
            raise IntegrityError('source_paths do not join the selected observation units')
    planned, groups = [], {}
    for unit in selected:
        path = unit['source_path']
        day = utc_day_start_ns(unit['source_window_start_ns'])
        previous = by_day.get((path, day - DAY_NS))
        following = by_day.get((path, day + DAY_NS))
        members = {
            'previous': None if previous is None else _unit_id(previous),
            'current': _unit_id(unit),
            'next': None if following is None else _unit_id(following),
        }
        member_units = [item for item in (previous, unit, following) if item is not None]
        row = {
            'unit_id': members['current'],
            'receipt_sha256': _receipt_sha(unit),
            'root': unit['root'],
            'source_path': path,
            'source_path_shard': source_path_shard(path),
            'cut_start_ns': unit['source_window_start_ns'],
            'cut_end_ns': unit['source_window_end_ns'],
            'utc_day_start_ns': day,
            'members': members,
            'member_count': len(member_units),
            'unavailable': _is_unavailable(unit),
            'observation_rows': int(unit.get('atomic_rows', unit.get('observation_rows') or 0)),
            'trade_rows': int((unit.get('receipt_counts') or {}).get('trades') or 0),
            'instruments': unit.get('instruments'),
            'receipt': unit.get('receipt'),
            'observation_series': unit.get('series'),
            'neighbor_units': {
                'previous': previous,
                'current': unit,
                'next': following,
            },
        }
        planned.append(row)
        groups.setdefault(path, []).append(row)
    for path in groups:
        groups[path].sort(key=lambda item: item['cut_start_ns'])
    unavailable = sum(1 for item in planned if item['unavailable'])
    return {
        'selected': planned,
        'by_source_path': groups,
        'population_units': len(units),
        'population_source_files': len({unit['source_path'] for unit in units}),
        'selected_units': len(planned),
        'unavailable_units': unavailable,
        'measured_units': len(planned) - unavailable,
        'source_unit_counts': {path: len(items) for path, items in groups.items()},
        'source_files': sorted(groups),
        'index': {'by_id': by_id, 'by_sha': by_sha, 'by_day': by_day},
    }


def project_window_resources(inventory, measured_units):
    """Pilot max CPU over obs+trade input, plus fixed empty-unit cost. Not a feasibility claim."""
    if not isinstance(inventory, list) or not inventory:
        raise IntegrityError('resource projection requires the full population inventory')
    if not measured_units:
        raise IntegrityError('resource projection requires measured window units')
    for row in measured_units:
        if (row.get('cpu_seconds') is None or row['cpu_seconds'] < 0
                or int(row.get('observation_input_rows') or 0) < 0
                or int(row.get('trade_input_rows') or 0) < 0):
            raise IntegrityError('resource projection requires complete measured units')
    nonempty = [row for row in measured_units
                if int(row['observation_input_rows']) + int(row['trade_input_rows']) > 0]
    empty = [row for row in measured_units
             if int(row['observation_input_rows']) + int(row['trade_input_rows']) == 0]
    if not nonempty:
        raise IntegrityError('resource projection needs at least one nonempty observation/trade window')
    def input_rows(row):
        return int(row['observation_input_rows']) + int(row['trade_input_rows'])
    per_input_cpu = max(row['cpu_seconds'] / input_rows(row) for row in nonempty)
    per_input_wall = max(row.get('wall_seconds', row['cpu_seconds']) / input_rows(row) for row in nonempty)
    output_basis = [row for row in nonempty if int(row.get('output_bytes') or 0) > 0]
    per_input_output = max((row['output_bytes'] / input_rows(row) for row in output_basis), default=0.0)
    fixed_cpu = max((row['cpu_seconds'] for row in empty), default=0.0) * len(inventory)
    fixed_wall = max((row.get('wall_seconds', row['cpu_seconds']) for row in empty), default=0.0) * len(inventory)
    full_nonempty = 0
    for item in inventory:
        obs = int(item.get('observation_rows', item.get('atomic_rows') or 0))
        trades = int(item.get('trade_rows', (item.get('receipt_counts') or {}).get('trades') or 0))
        if obs + trades > 0:
            full_nonempty += obs + trades
    return {
        'method': (
            'nonempty maximum CPU/wall/output per observation+trade input row, plus maximum '
            'empty-unit fixed cost for every population unit; 1.5 margin. Empty units never '
            'enter a per-row division. complete_feasible is not claimed.'
        ),
        'units_measured': len(measured_units),
        'population_units': len(inventory),
        'population_nonempty_input_rows': full_nonempty,
        'cpu_seconds_with_margin': 1.5 * (per_input_cpu * full_nonempty + fixed_cpu),
        'sequential_wall_seconds_with_margin': 1.5 * (per_input_wall * full_nonempty + fixed_wall),
        'output_bytes_with_margin': int(1.5 * per_input_output * full_nonempty) + 16 * 1024 ** 2,
        'measured_maximum_unit_cpu_seconds': max(row['cpu_seconds'] for row in measured_units),
        'measured_maximum_unit_output_bytes': max(int(row.get('output_bytes') or 0) for row in measured_units),
        'complete_feasible': False,
    }


def _validate_contract(contract):
    rec = _mapping(contract, what='contract')
    if rec.get('kind') != CONTRACT_KIND or rec.get('version') != CONTRACT_VERSION:
        raise ContractError('window population requires the frozen causal-window contract')
    if rec.get('family_complete') is True:
        raise ContractError('this driver cannot certify family completion')
    if rec.get('cut_cadence_ns') != CUT_CADENCE_NS:
        raise ContractError('cut cadence must be exact UTC five minutes')
    if list(rec.get('formation_minutes') or ()) != list(FORMATION_MINUTES):
        raise ContractError('every declared formation candidate must be retained')
    if list(rec.get('latency_ns') or ()) != list(LATENCY_NS):
        raise ContractError('every declared latency candidate must be retained')
    if list(rec.get('forward_horizons_minutes') or ()) != list(FORWARD_HORIZONS_MINUTES):
        raise ContractError('every declared forward horizon must be retained')
    return rec


def _load_calendar(contract):
    reference = contract.get('cash_calendar')
    if not isinstance(reference, dict) or type(reference.get('path')) is not str:
        raise IntegrityError('window contract must retain the authenticated cash_calendar reference')
    from trading_research.foundations.cash_calendar import CashCalendar
    path = Path(reference['path'])
    if path.stat().st_size != reference['size_bytes'] or file_digest(path) != reference['sha256']:
        raise IntegrityError('cash calendar differs from the frozen reference')
    return CashCalendar(path)


def _default_build(observations, trades, *, contract, source_identity, cut_start_ns, cut_end_ns, calendar):
    from trading_research.research.auction_flow_window_links import build_window_tables
    return build_window_tables(
        observations, trades, contract=contract, source_identity=source_identity,
        cut_start_ns=cut_start_ns, cut_end_ns=cut_end_ns, calendar=calendar,
    )


def _accepted_map(contract, load_reference):
    accepted = {}
    allowed_paths = set(contract.get('source_paths') or [])
    for item in contract.get('accepted_window_units') or []:
        hint = item.get('source_path') or (item.get('source_identity') or {}).get('source_path')
        if allowed_paths and hint is not None and hint not in allowed_paths:
            continue
        row = item if isinstance(item, dict) and 'cache_key' in item and 'features' in item else load_reference(item)
        key = row.get('cache_key')
        if type(key) is not str:
            raise IntegrityError('accepted_window_units must bind an exact cache_key')
        accepted[key] = row
    return accepted


def _unique_instrument_ids(table):
    if 'instrument_id' not in table.column_names or not len(table):
        return []
    return [int(value) for value in _pc().unique(table['instrument_id']).to_pylist() if value is not None]


def _inventory_from_population(population):
    inventory = []
    for unit in population['units']:
        inventory.append({
            'unit_id': _unit_id(unit),
            'source_path': unit['source_path'],
            'observation_rows': int(unit.get('atomic_rows', unit.get('observation_rows') or 0)),
            'trade_rows': int((unit.get('receipt_counts') or {}).get('trades') or 0),
            'receipt': unit.get('receipt'),
        })
    return inventory


class _RollingDayCache:
    def __init__(self):
        self.observations = {}
        self.trades = {}
        self.receipts = {}
        self.trade_schema = None
        self.data_reads = 0
        self.cache_hits = 0

    def receipt(self, unit, load_reference):
        sha = _receipt_sha(unit)
        if sha in self.receipts:
            return self.receipts[sha]
        loaded = load_reference(unit['receipt'])
        self.receipts[sha] = loaded
        return loaded

    def observation(self, unit):
        key = tuple(_unit_id(unit))
        if key in self.observations:
            self.cache_hits += 1
            return self.observations[key]
        table, read = _read_logical(unit.get('series'), empty=empty_observation_table())
        self.data_reads += int(read)
        self.observations[key] = table
        return table

    def trade(self, unit, load_reference):
        key = tuple(_unit_id(unit))
        if key in self.trades:
            self.cache_hits += 1
            return self.trades[key]
        receipt = self.receipt(unit, load_reference)
        series = _trade_series(receipt)
        empty = empty_trade_table(self.trade_schema)
        table, read = _read_logical(series, empty=empty)
        self.data_reads += int(read)
        if len(table):
            self.trade_schema = table.schema
        self.trades[key] = table
        return table

    def retain(self, keys):
        keep = {tuple(key) for key in keys}
        self.observations = {key: table for key, table in self.observations.items() if key in keep}
        self.trades = {key: table for key, table in self.trades.items() if key in keep}


def run_window_population(*, population, contract, outputs, load_reference,
                          selected_unit_ids=None, finalize=True, build_tables=None):
    """Materialize per-unit feature/label series from admitted observation/trade tables."""
    if not isinstance(outputs, BoundedOutputs) or not callable(load_reference):
        raise ContractError('bounded outputs and authenticated reference loader required')
    if type(finalize) is not bool:
        raise IntegrityError('finalize must be an explicit boolean')
    frozen = _validate_contract(contract)
    rec = _mapping(population, what='population')
    if rec.get('kind') != POPULATION_KIND:
        raise IntegrityError('authenticated observation population required')
    selected_ids = selected_unit_ids if selected_unit_ids is not None else frozen.get('selected_unit_ids')
    source_paths = frozen.get('source_paths')
    plan = plan_window_units(rec, selected_ids, source_paths=source_paths)
    calendar = _load_calendar(frozen)
    contract_digest = scientific_contract_digest(frozen)
    accepted = _accepted_map(frozen, load_reference)
    build = _default_build if build_tables is None else build_tables
    started, wall_started = time.process_time(), time.monotonic()
    summaries, measurements, unit_refs = [], [], []
    reused = recomputed = 0
    feature_rows = label_rows = 0
    complete_features = censored_features = complete_labels = censored_labels = 0
    for path in plan['source_files']:
        cache = _RollingDayCache()
        path_reads = path_hits = 0
        for planned in plan['by_source_path'][path]:
            keep = [planned['members'][side] for side in ('previous', 'current', 'next')
                    if planned['members'][side] is not None]
            cache.retain(keep)
            began, wall_began, before = time.process_time(), time.monotonic(), outputs.written
            unit = planned['neighbor_units']['current']
            receipt = cache.receipt(unit, load_reference)
            identity = _source_identity(unit, receipt)
            neighbor_refs = {}
            for side in ('previous', 'current', 'next'):
                member = planned['neighbor_units'][side]
                if member is None:
                    neighbor_refs[side] = None
                    continue
                member_receipt = cache.receipt(member, load_reference)
                neighbor_refs[side] = {
                    'unit_id': _unit_id(member),
                    'receipt': member.get('receipt'),
                    'observation': _series_digest(member.get('series')),
                    'trades': _series_digest(_trade_series(member_receipt)),
                }
            cache_key = window_unit_cache_key(
                unit_id=planned['unit_id'], receipt_sha256=planned['receipt_sha256'],
                observation_series=unit.get('series'), neighbor_refs=neighbor_refs,
                source_identity=identity, contract_digest=contract_digest)
            cut_start, cut_end = planned['cut_start_ns'], planned['cut_end_ns']
            if cut_end - cut_start > DAY_NS:
                raise IntegrityError('selected window cut lost the original UTC day bound')
            prefix = window_artifact_prefix({
                'root': unit['root'],
                'source_path': unit['source_path'],
                'source_metadata_sha256': identity['source_metadata_sha256'],
                'event_start_ns': cut_start,
                'event_end_ns': cut_end,
            })
            prior = accepted.get(cache_key)
            if prior is not None:
                for series_name in ('features', 'labels'):
                    for reference in prior[series_name]['files']:
                        path_ref = Path(reference['path'])
                        if path_ref.stat().st_size != reference['size_bytes'] or file_digest(path_ref) != reference['sha256']:
                            raise IntegrityError('accepted window output changed')
                summary = {
                    **prior,
                    'reused': True,
                    'cache_key': cache_key,
                    'reuse_cpu_seconds': time.process_time() - began,
                    'reuse_wall_seconds': time.monotonic() - wall_began,
                    'reuse_output_bytes': 0,
                    'data_reads': 0,
                    'cache_hits': 0,
                }
                reused += 1
            else:
                obs_in = trade_in = 0
                disposition = None
                if planned['unavailable']:
                    features, labels = _no_instrument_tables()
                    disposition = 'no_observed_instrument'
                    validation = {
                        'feature_rows': 0, 'label_rows': 0, 'instrument_count': 0,
                        'instrument_ids': [], 'cut_count': (cut_end - cut_start + CUT_CADENCE_NS - 1) // CUT_CADENCE_NS,
                        'source_unit_disposition': disposition,
                    }
                else:
                    members = [planned['neighbor_units'][side] for side in ('previous', 'current', 'next')
                               if planned['neighbor_units'][side] is not None]
                    current_obs = cache.observation(unit)
                    instrument_ids = _instrument_ids(current_obs, cut_start, cut_end)
                    if not instrument_ids:
                        features, labels = _no_instrument_tables()
                        disposition = 'no_observed_instrument'
                        validation = {
                            'feature_rows': 0, 'label_rows': 0, 'instrument_count': 0,
                            'instrument_ids': [], 'cut_count': (cut_end - cut_start + CUT_CADENCE_NS - 1) // CUT_CADENCE_NS,
                            'source_unit_disposition': disposition,
                        }
                    else:
                        if len(members) > 3:
                            raise IntegrityError('window support cannot exceed three UTC days')
                        obs_parts = [_filter_instruments(cache.observation(member), instrument_ids)
                                     for member in members]
                        trade_parts = [_filter_instruments(cache.trade(member, load_reference), instrument_ids)
                                       for member in members]
                        observations = _concat_ordered(obs_parts)
                        trades = _concat_ordered(trade_parts)
                        current_before = _day_atom_count(
                            _filter_instruments(current_obs, instrument_ids), cut_start, cut_end)
                        support_start = cut_start - LOOKBACK_NS
                        support_end = cut_end + LOOKAHEAD_NS
                        observations = _clip_observations(observations, support_start, support_end)
                        trades = _clip_trades(trades, support_start, support_end)
                        if _day_atom_count(observations, cut_start, cut_end) < current_before:
                            raise IntegrityError('window inputs lost the full selected UTC day')
                        obs_in, trade_in = len(observations), len(trades)
                        result = build(
                            observations, trades, contract=frozen, source_identity=identity,
                            cut_start_ns=cut_start, cut_end_ns=cut_end, calendar=calendar)
                        features = result['features']
                        labels = result['labels']
                        validation = result.get('validation') or {}
                stored_features = _write_series(outputs, f'{prefix}-features', features)
                stored_labels = _write_series(outputs, f'{prefix}-labels', labels)
                validation_features = int(validation.get('feature_rows', len(features)))
                validation_labels = int(validation.get('label_rows', len(labels)))
                instrument_ids = list(validation.get('instrument_ids') or _unique_instrument_ids(features))
                summary = {
                    'version': KIND,
                    'kind': UNIT_KIND,
                    'unit_id': planned['unit_id'],
                    'receipt_sha256': planned['receipt_sha256'],
                    'cache_key': cache_key,
                    'reused': False,
                    'disposition': validation.get('source_unit_disposition', disposition),
                    'receipt': unit.get('receipt'),
                    'observation_series': _series_digest(unit.get('series')),
                    'neighbor_member_refs': neighbor_refs,
                    'source_identity': identity,
                    'contract_digest': contract_digest,
                    'features': stored_features,
                    'labels': stored_labels,
                    'feature_rows': validation_features,
                    'label_rows': validation_labels,
                    'instrument_ids': instrument_ids,
                    'instrument_count': int(validation.get('instrument_count', len(instrument_ids))),
                    'tiled_feature_rows': _flag_count(features, 'atoms_complete'),
                    'complete_feature_rows': _complete_features(features),
                    'censored_feature_rows': (
                        _either_flag_count(features, 'left_censored', 'right_censored')
                    ),
                    'complete_label_rows': _flag_count(labels, 'complete'),
                    'censored_label_rows': (
                        _either_flag_count(labels, 'left_censored', 'right_censored')
                    ),
                    'latencies_ns': list(LATENCY_NS),
                    'horizons_minutes': list(FORWARD_HORIZONS_MINUTES),
                    'feature_schema_sha256': _schema_sha256(features),
                    'label_schema_sha256': _schema_sha256(labels),
                    'cut_start_ns': cut_start,
                    'cut_end_ns': cut_end,
                    'cut_count': int(validation.get('cut_count', (cut_end - cut_start + CUT_CADENCE_NS - 1) // CUT_CADENCE_NS)),
                    'observation_input_rows': obs_in,
                    'trade_input_rows': trade_in,
                    'data_reads': cache.data_reads - path_reads,
                    'cache_hits': cache.cache_hits - path_hits,
                    'cpu_seconds': time.process_time() - began,
                    'wall_seconds': time.monotonic() - wall_began,
                    'output_bytes': outputs.written - before,
                    'original_refs': {
                        'receipt': unit.get('receipt'),
                        'observation_series': unit.get('series') and {
                            'rows': unit['series'].get('rows'),
                            'files': [item.get('sha256') for item in unit['series'].get('files') or []],
                        },
                    },
                    'family_complete': False,
                }
                unit_ref = outputs.json(f'{prefix}-window-unit.json', summary, kind=UNIT_KIND)
                summary['reference'] = unit_ref
                unit_refs.append(unit_ref)
                recomputed += 1
            path_reads = cache.data_reads
            path_hits = cache.cache_hits
            summaries.append(summary)
            measurements.append({
                'unit_id': planned['unit_id'],
                'cpu_seconds': summary['cpu_seconds'],
                'wall_seconds': summary['wall_seconds'],
                'output_bytes': summary['output_bytes'],
                'observation_input_rows': summary.get('observation_input_rows', 0),
                'trade_input_rows': summary.get('trade_input_rows', 0),
                'feature_rows': summary.get('feature_rows', 0),
                'label_rows': summary.get('label_rows', 0),
            })
            feature_rows += int(summary.get('feature_rows') or 0)
            label_rows += int(summary.get('label_rows') or 0)
            complete_features += int(summary.get('complete_feature_rows') or 0)
            censored_features += int(summary.get('censored_feature_rows') or 0)
            complete_labels += int(summary.get('complete_label_rows') or 0)
            censored_labels += int(summary.get('censored_label_rows') or 0)
    data_reads = sum(item.get('data_reads') or 0 for item in summaries)
    cache_hits = sum(item.get('cache_hits') or 0 for item in summaries)
    inventory = _inventory_from_population(rec)
    projection = project_window_resources(inventory, measurements) if measurements and any(
        row['observation_input_rows'] + row['trade_input_rows'] > 0 for row in measurements) else {
        'complete_feasible': False, 'units_measured': 0, 'population_units': len(inventory),
    }
    payload = {
        'kind': KIND,
        'phase': frozen.get('phase'),
        'finalize': finalize,
        'passed': True,
        'family_complete': False,
        'complete_family_statistics': False,
        'all_family_validation_complete': False,
        'complete_feasible': False,
        'contract_digest': contract_digest,
        'population_source_windows': plan['population_units'],
        'population_source_files': plan['population_source_files'],
        'processed_source_windows': len(summaries),
        'unavailable_source_windows': plan['unavailable_units'],
        'measured_source_windows': plan['measured_units'],
        'feature_rows': feature_rows,
        'label_rows': label_rows,
        'complete_feature_rows': complete_features,
        'censored_feature_rows': censored_features,
        'complete_label_rows': complete_labels,
        'censored_label_rows': censored_labels,
        'source_unit_counts': plan['source_unit_counts'],
        'source_files': plan['source_files'],
        'reused_units': reused,
        'new_units': recomputed,
        'data_reads': data_reads,
        'cache_hits': cache_hits,
        'cpu_seconds': time.process_time() - started,
        'wall_seconds': time.monotonic() - wall_started,
        'output_bytes': outputs.written,
        'resource_projection': projection,
        'units': summaries,
        'refs': {'units': unit_refs},
        'raw_source_scans': 0,
    }
    if not finalize:
        payload['measurements'] = measurements
        return payload
    coverage = {
        'kind': 'auction_flow_window_population_coverage_v1',
        'population_source_windows': plan['population_units'],
        'processed_source_windows': len(summaries),
        'unavailable_source_windows': plan['unavailable_units'],
        'measured_source_windows': plan['measured_units'],
        'feature_rows': feature_rows,
        'label_rows': label_rows,
        'source_files': plan['source_files'],
        'source_unit_counts': plan['source_unit_counts'],
        'family_complete': False,
    }
    coverage_ref = outputs.json('window-population-coverage.json', coverage,
                                kind='auction_flow_window_population_coverage_v1')
    payload['coverage'] = coverage
    payload['refs']['coverage'] = coverage_ref
    payload['refs']['population'] = outputs.json('window-population.json', payload, kind=KIND)
    return payload


__all__ = [
    'CONTRACT_KIND',
    'DAY_NS',
    'FROZEN_STAGE_DATES',
    'KIND',
    'LOOKAHEAD_NS',
    'LOOKBACK_NS',
    'OPERATIONAL_CONTRACT_FIELDS',
    'SOURCE_SHARDS',
    'UNIT_KIND',
    'decode_window_unit_id',
    'empty_observation_table',
    'empty_trade_table',
    'encode_window_unit_id',
    'join_window_eligibility',
    'plan_window_units',
    'project_window_resources',
    'run_window_population',
    'scientific_contract_digest',
    'source_path_shard',
    'utc_day_start_ns',
    'window_unit_cache_key',
]
