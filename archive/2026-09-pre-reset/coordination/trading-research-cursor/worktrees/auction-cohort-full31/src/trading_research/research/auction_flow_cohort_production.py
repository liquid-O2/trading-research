"""Full-population unpublished cohort histograms, fits and source-window paths.

This is a production consumer of retained source-window receipts. It accumulates
the complete acquired eligible trade projection for one ROOT and acquisition
COLLECTION, fits the three registered unpublished recipes after the knowledge
cut, and measures whole-window plus atomic-one-minute true CVD OHLC. It does
not admit F11 serving, merge collections, claim participant identity, or treat
the 4096-print preflight prefix as training.
"""
from __future__ import annotations

from bisect import bisect_left
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path
import re
import time

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.time import datetime_ns, timestamp
from trading_research.measurements.cvd import (
    CohortChannel, CohortDefinition, exact_number, fixed_source_cohort,
)
from trading_research.operations.artifacts import digest
from trading_research.research.auction_flow_cohorts import (
    BATCH_ROWS, MAX_PRINTS, CohortWindow, TradeSizeHistogram,
    fit_unpublished_cohort_definition, merge_histogram_reports,
)
from trading_research.research.auction_flow_production import (
    WINDOW_RECEIPT_KIND, authenticate_artifact_reference, authenticate_retained_payload,
    production_window_identity, source_variant,
)
from trading_research.research.auction_flow_storage import (
    BoundedOutputs, read_json_artifact, read_series_tables,
)
from trading_research.research.auction_flow_windows import TRADE_FIELDS, prepare_trade_batch


VERSION = 'auction-flow-full-population-cohort-controller-v1'
CONTRACT_KIND = 'auction_flow_full_population_cohort_contract_v1'
PREFIX_CONTRACT_KIND = 'auction_flow_actual_cohort_validation_contract_v1'
HISTOGRAM_KIND = 'auction_flow_full_training_histogram_v1'
FITS_KIND = 'auction_flow_full_training_fits_v1'
WINDOW_KIND = 'auction_flow_full_population_cohort_window_v1'
ROWSET_KIND = 'auction_flow_full_population_cohort_rowset_v1'
AGGREGATION_UNIT = 'provider-reported-trade-record'
FIXED_FILTERS = ('all', 'ny_ge100', 'london_ge75', 'inclusive30_through60')
SOFT_KNOTS = (1, 30, 61, 75, 100)
ADAPTIVE_RECIPES = (
    ('count_quartiles', 'count', ((1, 4), (1, 2), (3, 4))),
    ('volume_quartiles', 'volume', ((1, 4), (1, 2), (3, 4))),
    ('source_top35_count_quantile', 'count', ((13, 20),)),
)
COLLECTIONS = ('monthly', 'dated')
TRAINING_DATES = {
    'NQ': ('2020-01-01', '2022-12-31'),
    'ES': ('2020-01-01', '2020-12-31'),
}
PROTOCOL_CHRONOLOGY = {
    'ES': {
        'train': ('2020-01-01', '2020-12-31'),
        'development': ('2023-07-01', '2023-12-31'),
        'calibration': ('2024-01-01', '2024-03-31'),
        'confirmation': ('2024-04-01', '2024-08-31'),
    },
    'NQ': {
        'train': ('2020-01-01', '2022-12-31'),
        'development': ('2023-01-01', '2023-12-31'),
        'calibration': ('2024-01-01', '2024-12-31'),
        'confirmation': ('2025-01-01', '2026-09-03'),
    },
}
SOURCE_VARIANTS = (
    'Monthly YYYY-MM.parquet and dated YYYY-MM-DD.parquet acquisitions remain '
    'separate collections. Overlapping calendar dates are not independent market '
    'dates and are never concatenated or silently superseded.')
TRAINING_SCOPE = (
    'Complete acquired eligible trade projection for the declared training '
    'schedule of one ROOT and one acquisition COLLECTION. This is not a 4096-print '
    'prefix, not raw MBP, and not asserted coverage of unobserved market history.')
HISTOGRAM_SCOPE = 'complete_acquired_eligible_projection'
_UNPUBLISHED = 'unpublished mathematical calculations'
_NO_INTERVAL = 'unavailable_no_positive_interval_after_training_availability'
_BEFORE_AVAIL = 'unavailable_before_training_availability'
_EMPTY_TRAIN = 'unavailable_empty_training_population'
_NO_POST_TRAIN = 'dated_collection_no_post_training_evaluation_population'
_NO_FIT = 'unavailable_no_fit_for_collection'
_UNSUPPORTED_HISTORY = 'unsupported_full_temporal_market_history_required'
_PREFIX_SCOPE = 'rejected_prefix_or_calibration_scope_is_not_full_training'
_COMMON = ('open', 'high', 'low', 'close', 'high_at_ns', 'low_at_ns', 'high_source_order',
           'low_source_order', 'buy', 'sell', 'unknown', 'volume', 'observed_signed_lower',
           'observed_signed_upper', 'true_signed_lower', 'true_signed_upper')
_CHANNEL_FIELDS = (
    'channel_id', 'role', 'open', 'high', 'low', 'close', 'high_at_ns', 'low_at_ns',
    'high_source_order', 'low_source_order', 'high_origin', 'low_origin', 'buy', 'sell',
    'unknown', 'volume', 'signed', 'weighted_prints', 'contributing_prints', 'count_occupancy',
    'volume_occupancy', 'observed_signed_lower', 'observed_signed_upper', 'true_signed_lower',
    'true_signed_upper', 'empty_observed_channel', 'history_complete')
_BAR_FIELDS = (
    'bin', 'event_start_ns', 'event_end_ns', 'known_at_ns', 'supported_start_ns',
    'supported_end_ns', 'clipped', 'source_coverage_complete', 'coordinate_complete',
    'prints', 'volume', 'empty_observed_window', 'partition_volume', 'partition_weighted_prints')
_ROW_FIELDS = (
    'root', 'collection', 'source_path', 'date', 'chronological_split', 'interval_kind',
    'bin', 'event_start_ns', 'event_end_ns', 'coverage_source_complete',
    'coverage_coordinate_complete', 'definition', 'channel_id', 'channel_role', 'prints',
    'volume', 'weighted_prints', 'count_occupancy', 'volume_occupancy', 'open', 'high',
    'low', 'close', 'signed', 'signed_excursion', 'unknown', 'observed_signed_lower',
    'observed_signed_upper', 'availability', 'date_block_id', 'independent_date_unit',
    'acquisition_overlap_key', 'row_role')
_CPU_NAMES = (
    'receipt_authentication_and_membership',
    'histogram_accumulation',
    'fit_and_cut_availability',
    'current_cache_decoding',
    'preparation_and_filtering',
    'whole_path_updates',
    'atomic_path_updates',
    'whole_atomic_finalization',
    'original_source_comparisons',
    'full_atom_composition',
    'serialization',
    'orchestration_and_report_assembly',
)
_MONTHLY_NAME = re.compile(r'^(\d{4}-\d{2})\.parquet$')
_DATED_NAME = re.compile(r'^(\d{4}-\d{2}-\d{2})\.parquet$')


def _cpu():
    return {name: 0.0 for name in _CPU_NAMES}


def _acc(cpu, name, started):
    cpu[name] += time.process_time() - started
    return time.process_time()


def _counts():
    return {'decoded_rows': 0, 'decoded_batches': 0, 'prepared_prints': 0, 'sliced_prints': 0,
            'instantiated_bars': 0, 'report_bars': 0, 'report_channels': 0,
            'full_path_print_contributions': 0, 'serialized_bytes': 0, 'rowset_rows': 0}


def _pairs(values):
    if type(values) not in (tuple, list):
        raise ContractError('declared adaptive recipes are not the registered unpublished set')
    pairs = []
    for item in values:
        if type(item) not in (tuple, list) or len(item) != 2:
            raise ContractError('declared adaptive recipes are not the registered unpublished set')
        a, b = item
        if type(a) is not int or type(b) is not int:
            raise ContractError('declared adaptive recipes are not the registered unpublished set')
        pairs.append((a, b))
    return tuple(pairs)


def _exact_int_sequence(values, expected, *, name):
    if type(values) not in (tuple, list) or len(values) != len(expected):
        raise ContractError(f'cohort production contract changed its registered {name}')
    if any(type(item) is not int for item in values):
        raise ContractError(f'cohort production contract changed its registered {name}')
    if tuple(values) != expected:
        raise ContractError(f'cohort production contract changed its registered {name}')
    return tuple(values)


def _fractions(pairs):
    return tuple(Fraction(a, b) for a, b in pairs)


def _utc_date(text):
    if type(text) is not str or len(text) != 10 or text[4] != '-' or text[7] != '-':
        raise ContractError('utc_date must be an explicit YYYY-MM-DD calendar date')
    year, month, day = (int(part) for part in text.split('-'))
    datetime(year, month, day, tzinfo=timezone.utc)
    return text


def date_start_ns(text):
    text = _utc_date(text)
    year, month, day = (int(part) for part in text.split('-'))
    return datetime_ns(datetime(year, month, day, tzinfo=timezone.utc))


def date_end_exclusive_ns(text):
    text = _utc_date(text)
    year, month, day = (int(part) for part in text.split('-'))
    return datetime_ns(datetime(year, month, day, tzinfo=timezone.utc) + timedelta(days=1))


def training_bounds(root):
    if root not in TRAINING_DATES:
        raise ContractError('cohort training root must be NQ or ES')
    start, end = TRAINING_DATES[root]
    return {'root': root, 'start_date': start, 'end_date': end,
            'event_period_start_ns': date_start_ns(start),
            'event_period_cut_ns': date_end_exclusive_ns(end)}


def chronological_split(root, date):
    if root not in PROTOCOL_CHRONOLOGY:
        raise ContractError('chronological split root must be NQ or ES')
    day = _utc_date(date)
    for name, (start, end) in PROTOCOL_CHRONOLOGY[root].items():
        if start <= day <= end:
            return name
    return 'outside_declared_partitions'


def collection_from_source_path(source_path):
    if type(source_path) is not str or not source_path:
        raise ContractError('source_path is required to classify the acquisition collection')
    name = Path(source_path).name
    if _MONTHLY_NAME.match(name):
        return 'monthly'
    if _DATED_NAME.match(name):
        return 'dated'
    raise ContractError('source_path filename is neither a monthly YYYY-MM nor dated YYYY-MM-DD parquet')


def full_population_cohort_contract():
    """Caller-supplied contract Codex can freeze for registered dispatch."""
    return {
        'kind': CONTRACT_KIND,
        'aggregation_unit': AGGREGATION_UNIT,
        'atomic_width_ns': 60_000_000_000,
        'maximum_prepared_batch_rows': BATCH_ROWS,
        'fixed_filters': list(FIXED_FILTERS),
        'fixed_soft_knots': list(SOFT_KNOTS),
        'adaptive_definitions': [
            {'name': name, 'weighting': weighting, 'probabilities': [list(pair) for pair in pairs]}
            for name, weighting, pairs in ADAPTIVE_RECIPES
        ],
        'chronology': {root: {name: list(bounds) for name, bounds in stages.items()}
                       for root, stages in PROTOCOL_CHRONOLOGY.items()},
        'training_dates': {root: list(bounds) for root, bounds in TRAINING_DATES.items()},
        'collections': list(COLLECTIONS),
        'all_original_source_checks_retained': True,
        'full_window_and_all_one_minute_bars': True,
        'context_or_location_evaluation': False,
        'f11_serving_admitted': False,
        'family_statistics_complete': False,
        'full_temporal_market_history_required': False,
        'full_temporal_market_history_complete': False,
        'source_variants': SOURCE_VARIANTS,
        'training_scope': TRAINING_SCOPE,
        'histogram_scope': HISTOGRAM_SCOPE,
    }


def validate_cohort_production_contract(contract):
    if type(contract) is not dict:
        raise ContractError('full-population cohort contract is required')
    if contract.get('kind') == PREFIX_CONTRACT_KIND or 'maximum_training_prefix_prints' in contract:
        raise ContractError(_PREFIX_SCOPE)
    if (contract.get('kind') != CONTRACT_KIND
            or contract.get('aggregation_unit') != AGGREGATION_UNIT
            or contract.get('atomic_width_ns') != 60_000_000_000
            or contract.get('maximum_prepared_batch_rows') != BATCH_ROWS
            or tuple(contract.get('fixed_filters') or ()) != FIXED_FILTERS
            or tuple(contract.get('collections') or ()) != COLLECTIONS
            or contract.get('all_original_source_checks_retained') is not True
            or contract.get('full_window_and_all_one_minute_bars') is not True
            or contract.get('context_or_location_evaluation') is not False
            or contract.get('f11_serving_admitted') is not False
            or contract.get('family_statistics_complete') is not False
            or contract.get('full_temporal_market_history_required') is not False
            or contract.get('full_temporal_market_history_complete') is not False
            or contract.get('source_variants') != SOURCE_VARIANTS
            or contract.get('training_scope') != TRAINING_SCOPE
            or contract.get('histogram_scope') != HISTOGRAM_SCOPE):
        raise ContractError('cohort production contract changed its registered limits or family scope')
    _exact_int_sequence(contract.get('fixed_soft_knots'), SOFT_KNOTS, name='soft knots')
    recipes = contract.get('adaptive_definitions')
    if type(recipes) is not list or len(recipes) != len(ADAPTIVE_RECIPES):
        raise ContractError('declared adaptive recipes are not the registered unpublished set')
    for got, (name, weighting, pairs) in zip(recipes, ADAPTIVE_RECIPES, strict=True):
        if (type(got) is not dict or got.get('name') != name or got.get('weighting') != weighting
                or _pairs(got.get('probabilities') or ()) != pairs):
            raise ContractError('declared adaptive recipes are not the registered unpublished set')
    chronology = contract.get('chronology')
    training = contract.get('training_dates')
    if type(chronology) is not dict or set(chronology) != {'ES', 'NQ'}:
        raise ContractError('cohort chronology must retain the protocol NQ and ES partitions')
    if type(training) is not dict or set(training) != {'ES', 'NQ'}:
        raise ContractError('training dates must retain the protocol NQ and ES closures')
    for root in ('ES', 'NQ'):
        if tuple(training[root] or ()) != TRAINING_DATES[root]:
            raise ContractError('training dates changed the protocol train closure')
        stages = chronology[root]
        if type(stages) is not dict or set(stages) != set(PROTOCOL_CHRONOLOGY[root]):
            raise ContractError('cohort chronology lost a declared partition')
        for name, bounds in PROTOCOL_CHRONOLOGY[root].items():
            if tuple(stages[name] or ()) != bounds:
                raise ContractError('cohort chronology changed a declared partition')
    return contract


def contract_identity(contract):
    validate_cohort_production_contract(contract)
    return digest({key: contract[key] for key in sorted(contract)})


def schedule_member_key(member):
    if type(member) is not dict:
        raise ContractError('expected schedule members must be explicit records')
    root = member.get('root')
    if root not in TRAINING_DATES:
        raise ContractError('expected schedule member root must be NQ or ES')
    path = member.get('source_path')
    collection = collection_from_source_path(path)
    declared = member.get('collection')
    if declared is not None and declared != collection:
        raise ContractError('declared collection does not match the source_path filename')
    sha = member.get('source_metadata_sha256')
    if type(sha) is not str or len(sha) != 64:
        raise ContractError('expected member source_metadata_sha256 is incomplete')
    start, end = member.get('event_start_ns'), member.get('event_end_ns')
    timestamp(start)
    timestamp(end)
    if not start < end:
        raise ContractError('expected member event interval is empty or reversed')
    day = _utc_date(member.get('utc_date') or member.get('cash_date'))
    return {
        'root': root, 'collection': collection, 'source_path': path,
        'source_metadata_sha256': sha, 'event_start_ns': start, 'event_end_ns': end,
        'utc_date': day,
    }


def _join_key(member):
    item = schedule_member_key(member)
    return (item['root'], item['source_path'], item['source_metadata_sha256'],
            item['event_start_ns'], item['event_end_ns'])


def _require_series(table):
    if any(name not in table.column_names for name in TRADE_FIELDS):
        raise IntegrityError('retained trade series lost a required raw field projection')


def _unique_source_key(table):
    import pyarrow.compute as pc

    keys = pc.unique(table['source_key']).to_pylist()
    if len(keys) != 1 or type(keys[0]) is not str or not keys[0]:
        raise IntegrityError('a cohort window cannot join distinct acquired source streams')
    return keys[0]


def _filter_instrument(table, instrument_id):
    import pyarrow.compute as pc

    return table.filter(pc.equal(table['instrument_id'], instrument_id))


def _literal_from_histogram(histogram, probabilities, weighting):
    if not histogram:
        raise IntegrityError('literal quantile reference requires the selected training sizes')
    total = sum(count for _, count in histogram) if weighting == 'count' else sum(
        size * count for size, count in histogram)
    thresholds = []
    for probability in probabilities:
        mass = 0
        chosen = None
        for size, count in histogram:
            mass += count if weighting == 'count' else size * count
            if mass >= probability * total:
                chosen = size + 1
                break
        if chosen is None:
            raise IntegrityError('literal quantile mass never reached the requested interior probability')
        thresholds.append(chosen)
    cuts = (1, *sorted(set(thresholds)), None)
    realized_count = []
    realized_volume = []
    for lower, upper in zip(cuts, cuts[1:]):
        count = volume = 0
        for size, amount in histogram:
            if size >= lower and (upper is None or size < upper):
                count += amount
                volume += size * amount
        realized_count.append(count)
        realized_volume.append(volume)
    return {'requested_thresholds': tuple(thresholds), 'cuts': cuts,
            'realized_count': tuple(realized_count), 'realized_volume': tuple(realized_volume)}


def _compare_fit(fitted, literal, definition_name):
    if fitted['recipe']['requested_thresholds'] != literal['requested_thresholds']:
        raise IntegrityError(f'{definition_name} unpublished thresholds differ from the independent size+1 rule')
    got = tuple((channel.lower_inclusive, channel.upper_exclusive) for channel in fitted['definition'].channels)
    expected = tuple(zip(literal['cuts'], literal['cuts'][1:]))
    if got != expected:
        raise IntegrityError(f'{definition_name} unpublished channel intervals differ from the independent size+1 rule')
    if fitted['realized_count'] != literal['realized_count'] or fitted['realized_volume'] != literal['realized_volume']:
        raise IntegrityError(f'{definition_name} realized count/volume differ from the independent training sizes')


def _all_definition():
    return CohortDefinition('all', AGGREGATION_UNIT, (CohortChannel('all', 1, None),))


def _soft_definition():
    return CohortDefinition('soft-benchmark-knots-v1', AGGREGATION_UNIT, (), SOFT_KNOTS)


def _window_complete(measured):
    instruments = measured.get('instruments')
    if type(instruments) is not list:
        raise IntegrityError('retained measurement lost its raw-instrument population')
    if not instruments:
        source = measured.get('source_coverage_complete')
        coordinate = measured.get('coordinate_complete')
        if source is True and coordinate is True:
            return True, True
        raise IntegrityError('empty measurement must declare explicit window coverage')
    source = all(item.get('whole_window', {}).get('source_coverage_complete') is True for item in instruments)
    coordinate = all((item.get('coordinate') or {}).get('complete') is True
                     and item.get('whole_window', {}).get('coordinate_complete') is True
                     for item in instruments)
    return source, coordinate


def _load_measurement(reference):
    authenticate_artifact_reference(reference)
    measured = read_json_artifact(reference)
    if type(measured) is not dict:
        raise IntegrityError('retained measurement artifact is not an object')
    return measured


def load_cohort_receipt(receipt_or_ref):
    """Accept an in-memory receipt or an immutable size/hash-bound receipt reference."""
    if (type(receipt_or_ref) is dict and {'path', 'sha256', 'size_bytes'} <= set(receipt_or_ref)
            and receipt_or_ref.get('kind') != WINDOW_RECEIPT_KIND and 'unit' not in receipt_or_ref):
        authenticate_artifact_reference(receipt_or_ref)
        receipt_or_ref = read_json_artifact(receipt_or_ref)
    if type(receipt_or_ref) is not dict or receipt_or_ref.get('kind') != WINDOW_RECEIPT_KIND:
        raise IntegrityError('cohort production requires a source window receipt')
    return receipt_or_ref


def authenticate_cohort_receipt(receipt, *, expected_member, contract):
    """Join one successful source receipt to an explicit expected schedule member.

    Relevant trade/measurement identities are authenticated. Producer-tree hashes
    are not re-derived here so a downstream consumer edit cannot invalidate the
    source producer.
    """
    validate_cohort_production_contract(contract)
    receipt = load_cohort_receipt(receipt)
    if receipt.get('success') is not True:
        raise IntegrityError('incomplete window receipt cannot enter the training or evaluation join')
    expected = schedule_member_key(expected_member)
    unit = receipt.get('unit')
    if type(unit) is not dict:
        raise IntegrityError('window receipt lost its unit')
    identity = production_window_identity(unit)
    if receipt.get('unit_identity') not in (None, identity):
        raise IntegrityError('window receipt unit_identity does not join its unit')
    if (unit.get('root') != expected['root']
            or unit.get('source_path') != expected['source_path']
            or unit.get('source_metadata_sha256') != expected['source_metadata_sha256']
            or unit.get('event_start_ns') != expected['event_start_ns']
            or unit.get('event_end_ns') != expected['event_end_ns']):
        raise IntegrityError('window receipt does not join the expected schedule member')
    unit_date = unit.get('utc_date') or unit.get('cash_date')
    if unit_date is not None and _utc_date(unit_date) != expected['utc_date']:
        raise IntegrityError('window receipt date does not join the expected schedule member')
    artifacts = receipt.get('artifacts')
    if type(artifacts) is not dict or 'trades' not in artifacts or 'measurement' not in artifacts:
        raise IntegrityError('window receipt lost its trade or measurement artifact')
    authenticate_retained_payload(artifacts['trades'])
    authenticate_artifact_reference(artifacts['measurement'])
    for name in ('excluded', 'quotes', 'continuation'):
        if name in artifacts:
            authenticate_retained_payload(artifacts[name])
    natives = artifacts.get('native')
    if natives is not None:
        if type(natives) is not list:
            raise IntegrityError('window receipt native artifacts are invalid')
        for reference in natives:
            authenticate_retained_payload(reference)
    measured = _load_measurement(artifacts['measurement'])
    start = measured.get('event_start_ns')
    end = measured.get('event_end_ns')
    known = measured.get('known_at_ns')
    timestamp(start)
    timestamp(end)
    timestamp(known)
    if (start, end) != (expected['event_start_ns'], expected['event_end_ns']):
        raise IntegrityError('measurement bounds do not join the expected schedule member')
    if known < end:
        raise IntegrityError('measurement known_at precedes the event-period end')
    parameters = receipt.get('parameters') if type(receipt.get('parameters')) is dict else {}
    delay = parameters.get('latency_ns')
    if delay is None:
        delay = known - end
    if type(delay) is not int or not 0 <= delay <= 1_000_000_000 or known - end != delay:
        raise IntegrityError('receipt delay does not join measurement known_at minus event end')
    source_complete, coordinate_complete = _window_complete(measured)
    return {
        'receipt': receipt, 'unit': unit, 'unit_identity': identity, 'expected': expected,
        'collection': expected['collection'], 'measured': measured,
        'trades': artifacts['trades'], 'measurement_reference': artifacts['measurement'],
        'delay': delay, 'published_at': known, 'source_complete': source_complete,
        'coordinate_complete': coordinate_complete,
        'window_acquired_complete': source_complete and coordinate_complete,
        'whole_window_inside_acquired_file': unit.get('whole_window_inside_acquired_file'),
        'split': chronological_split(expected['root'], expected['utc_date']),
    }


def join_training_receipts(expected_members, receipts, *, contract):
    """Require a complete 1-1 join; missing, duplicate or tampered members reject."""
    validate_cohort_production_contract(contract)
    if type(expected_members) not in (tuple, list) or not expected_members:
        raise ContractError('training requires an explicit nonempty expected schedule')
    if type(receipts) not in (tuple, list):
        raise ContractError('training receipts must be an explicit sequence')
    expected = [schedule_member_key(item) for item in expected_members]
    keys = [_join_key(item) for item in expected]
    if len(set(keys)) != len(keys):
        raise ContractError('duplicated expected training member')
    collections = {item['collection'] for item in expected}
    roots = {item['root'] for item in expected}
    if len(collections) != 1 or len(roots) != 1:
        raise ContractError('one training accumulation joins one ROOT and one COLLECTION')
    if len(receipts) != len(expected):
        raise IntegrityError('training receipts do not match the expected schedule membership')
    joined = {}
    for receipt in receipts:
        receipt = load_cohort_receipt(receipt)
        unit = receipt.get('unit') if type(receipt.get('unit')) is dict else {}
        key = (unit.get('root'), unit.get('source_path'), unit.get('source_metadata_sha256'),
               unit.get('event_start_ns'), unit.get('event_end_ns'))
        if key in joined:
            raise IntegrityError('duplicated source-window evidence cannot be merged')
        matches = [item for item, item_key in zip(expected, keys, strict=True) if item_key == key]
        if not matches:
            raise IntegrityError('receipt is not a member of the expected training schedule')
        authenticated = authenticate_cohort_receipt(receipt, expected_member=matches[0], contract=contract)
        if authenticated['split'] != 'train':
            raise ContractError('testing, calibration or confirmation rows cannot enter training')
        if not authenticated['window_acquired_complete']:
            raise IntegrityError('a missing or incomplete expected training window cannot be treated as empty or completed')
        joined[key] = authenticated
    if set(joined) != set(keys):
        missing = [item for item, key in zip(expected, keys, strict=True) if key not in joined]
        raise IntegrityError(f'missing expected training window cannot be treated as empty or completed: {missing[0]["utc_date"]}')
    return tuple(joined[key] for key in keys)


def _member_id(joined):
    trades = joined['trades']
    measurement = joined['measurement_reference']
    return digest({
        'expected': joined['expected'],
        'unit_identity': joined['unit_identity'],
        'trades': {'rows': trades.get('rows'), 'sha256': tuple(item.get('sha256') for item in trades.get('files') or ())},
        'measurement': {'sha256': measurement.get('sha256'), 'size_bytes': measurement.get('size_bytes'),
                        'uncompressed_sha256': measurement.get('uncompressed_sha256')},
    })


def _ingest_training_trades(joined, histogram, counts):
    expected = joined['expected']
    delay = joined['delay']
    last_t = last_order = None
    last_obs = None
    source_key = None
    member_id = _member_id(joined)
    added = False
    for table in read_series_tables(joined['trades']):
        counts['decoded_batches'] += 1
        counts['decoded_rows'] += len(table)
        _require_series(table)
        if not len(table):
            continue
        key = _unique_source_key(table)
        if source_key is None:
            source_key = key
        elif key != source_key:
            raise IntegrityError('a cohort window cannot join distinct acquired source streams')
        for offset in range(0, len(table), BATCH_ROWS):
            part = table.slice(offset, min(BATCH_ROWS, len(table) - offset))
            with prepare_trade_batch(part) as prepared:
                if len(prepared):
                    values = prepared.values
                    t, order, known = values['t'], values['source_order'], values['known_at_ns']
                    if (int(t[0]) < expected['event_start_ns'] or int(t[-1]) >= expected['event_end_ns']
                            or any(int(stamp) < expected['event_start_ns'] or int(stamp) >= expected['event_end_ns']
                                   for stamp in t)):
                        raise IntegrityError('training series print is outside the retained training window')
                    if any(int(item) != int(stamp) + delay for stamp, item in zip(t, known)):
                        raise IntegrityError('training series delay does not match the retained source delay')
                    if last_t is not None and (int(t[0]) < last_t or int(order[0]) <= last_order):
                        raise IntegrityError('training series lost original source order')
                    last_t, last_order = int(t[-1]), int(order[-1])
                    last_obs = last_t
                histogram.add_prepared(prepared, 0, len(prepared), member_id=member_id)
                counts['prepared_prints'] += len(prepared)
                added = True
    if not added:
        histogram.add_sizes((), member_id=member_id)
    published = None if last_obs is None else last_obs + 1 + delay
    return member_id, source_key, last_obs, published


def _coverage_payload(joined_members, *, acquired_complete):
    return {
        'expected_members': len(joined_members),
        'joined_members': len(joined_members),
        'missing_members': (),
        'partial_files': tuple(item['expected']['utc_date'] for item in joined_members
                               if item['whole_window_inside_acquired_file'] is False),
        'acquired_projection_complete': acquired_complete,
        'full_temporal_market_history_complete': False,
        'histogram_scope': HISTOGRAM_SCOPE,
    }


def accumulate_training_collection(*, root, collection, expected_members, receipts, contract):
    """Accumulate one ROOT/COLLECTION training histogram from complete receipt joins."""
    cpu, counts = _cpu(), _counts()
    entry = started = time.process_time()
    validate_cohort_production_contract(contract)
    if collection not in COLLECTIONS:
        raise ContractError('training collection must be monthly or dated')
    bounds = training_bounds(root)
    joined = join_training_receipts(expected_members, receipts, contract=contract)
    started = _acc(cpu, 'receipt_authentication_and_membership', started)
    if any(item['expected']['root'] != root or item['expected']['collection'] != collection for item in joined):
        raise IntegrityError('joined training members escaped the declared ROOT/COLLECTION')
    for item in joined:
        day = item['expected']['utc_date']
        if not bounds['start_date'] <= day <= bounds['end_date']:
            raise ContractError('training member date is outside the protocol train closure')
    manifests = {
        'kind': 'full_acquired_eligible_projection',
        'root': root, 'collection': collection,
        'histogram_scope': HISTOGRAM_SCOPE,
        'full_temporal_market_history_complete': False,
        'training_scope': TRAINING_SCOPE,
        'contract_identity': contract_identity(contract),
    }
    members = []
    window_reports = []
    last_obs_published = None
    for item in joined:
        histogram = TradeSizeHistogram(source_manifest=manifests, fold_manifest=dict(manifests),
                                       aggregation_unit=contract['aggregation_unit'])
        try:
            member_id, source_key, last_obs, published = _ingest_training_trades(item, histogram, counts)
            window_reports.append(histogram.record(coverage_complete=True))
        finally:
            histogram.close()
        members.append({
            'id': member_id, 'expected': item['expected'], 'unit_identity': item['unit_identity'],
            'source_key': source_key, 'end': item['expected']['event_end_ns'],
            'published_at': item['published_at'], 'last_observation_ns': last_obs,
            'last_observation_published_at': published,
            'history_complete': item['window_acquired_complete'],
            'source_complete': item['source_complete'],
            'coordinate_complete': item['coordinate_complete'],
            'whole_window_inside_acquired_file': item['whole_window_inside_acquired_file'],
            'measurement_reference': item['measurement_reference'],
            'split': item['split'],
        })
        if published is not None and (last_obs_published is None or published > last_obs_published):
            last_obs_published = published
    report = window_reports[0] if len(window_reports) == 1 else merge_histogram_reports(*window_reports)
    started = _acc(cpu, 'histogram_accumulation', started)
    event_period_cut = bounds['event_period_cut_ns']
    last_window_published = max(item['published_at'] for item in members)
    knowledge_cut = max(event_period_cut, last_window_published)
    if last_obs_published is not None:
        knowledge_cut = max(knowledge_cut, last_obs_published)
    payload = {
        'version': VERSION, 'kind': HISTOGRAM_KIND, 'publication_status': 'unpublished',
        'output_kind': _UNPUBLISHED, 'admitted_for_serving': False,
        'root': root, 'collection': collection,
        'histogram_report': report, 'members': tuple(members),
        'coverage': _coverage_payload(joined, acquired_complete=True),
        'event_period_cut_ns': event_period_cut,
        'last_window_published_at': last_window_published,
        'last_observation_published_at': last_obs_published,
        'knowledge_cut_ns': knowledge_cut,
        'full_temporal_market_history_complete': False,
        'histogram_scope': HISTOGRAM_SCOPE,
        'contract_identity': contract_identity(contract),
        'prints': report['prints'], 'contracts': report['contracts'],
        'histogram_identity': report['identity'],
    }
    helper = time.process_time() - entry
    named = sum(cpu[name] for name in _CPU_NAMES if name != 'orchestration_and_report_assembly')
    cpu['orchestration_and_report_assembly'] = helper - named
    payload['cpu_components_disjoint'] = cpu
    payload['helper_cpu_seconds'] = helper
    payload['workload_counts'] = counts
    return payload


class TrainingCollectionAccumulator:
    """Incremental complete-window training join for one ROOT/COLLECTION."""

    def __init__(self, *, root, collection, expected_members, contract):
        validate_cohort_production_contract(contract)
        if collection not in COLLECTIONS:
            raise ContractError('training collection must be monthly or dated')
        self.root = root
        self.collection = collection
        self.contract = contract
        self._expected = [schedule_member_key(item) for item in expected_members]
        keys = [_join_key(item) for item in self._expected]
        if not keys or len(set(keys)) != len(keys):
            raise ContractError('training requires distinct explicit expected schedule members')
        if any(item['root'] != root or item['collection'] != collection for item in self._expected):
            raise ContractError('accumulator members escaped the declared ROOT/COLLECTION')
        self._keys = keys
        self._pending = {key: item for key, item in zip(keys, self._expected, strict=True)}
        self._joined = {}

    def remaining_members(self):
        return tuple(self._pending[key] for key in self._keys if key in self._pending)

    def add_receipt(self, receipt):
        receipt = load_cohort_receipt(receipt)
        unit = receipt.get('unit') if type(receipt.get('unit')) is dict else {}
        key = (unit.get('root'), unit.get('source_path'), unit.get('source_metadata_sha256'),
               unit.get('event_start_ns'), unit.get('event_end_ns'))
        if key in self._joined:
            raise IntegrityError('duplicated source-window evidence cannot be merged')
        if key not in self._pending:
            raise IntegrityError('receipt is not a remaining expected training member')
        authenticated = authenticate_cohort_receipt(
            receipt, expected_member=self._pending[key], contract=self.contract)
        if authenticated['split'] != 'train' or not authenticated['window_acquired_complete']:
            raise IntegrityError('a missing or incomplete expected training window cannot be treated as empty or completed')
        self._joined[key] = authenticated
        del self._pending[key]
        return authenticated

    def complete(self):
        if self._pending:
            raise IntegrityError('a missing expected training window cannot be treated as empty or completed')
        receipts = [self._joined[key]['receipt'] for key in self._keys]
        return accumulate_training_collection(
            root=self.root, collection=self.collection, expected_members=self._expected,
            receipts=receipts, contract=self.contract)


def persist_training_histogram(outputs, payload):
    if not isinstance(outputs, BoundedOutputs):
        raise ContractError('training histogram persist requires bounded registered outputs')
    if type(payload) is not dict or payload.get('kind') != HISTOGRAM_KIND:
        raise ContractError('only a completed full-training histogram can be persisted')
    if payload.get('coverage', {}).get('acquired_projection_complete') is not True:
        raise IntegrityError('incomplete training histogram cannot be published as complete')
    name = f"{payload['root']}-{payload['collection']}-training-histogram.json.zst"
    return outputs.json_compressed(name, payload, kind=HISTOGRAM_KIND)


def restore_training_histogram(reference):
    authenticate_artifact_reference(reference)
    payload = read_json_artifact(reference)
    if type(payload) is not dict or payload.get('kind') != HISTOGRAM_KIND:
        raise IntegrityError('restored object is not a completed full-training histogram')
    report = payload.get('histogram_report')
    if type(report) is not dict or report.get('identity') != payload.get('histogram_identity'):
        raise IntegrityError('restored histogram identity does not join its report')
    if payload.get('full_temporal_market_history_complete') is True:
        raise IntegrityError('restored histogram invented full temporal market history')
    return payload


def fit_training_collection(payload, *, contract, evaluation_members=None):
    """Fit the three recipes after the later of last publication and train end."""
    started = time.process_time()
    validate_cohort_production_contract(contract)
    if type(payload) is not dict or payload.get('kind') != HISTOGRAM_KIND:
        raise ContractError('fit requires a completed full-training histogram')
    if payload.get('contract_identity') != contract_identity(contract):
        raise IntegrityError('histogram contract identity does not join the caller-supplied contract')
    if payload.get('full_temporal_market_history_complete') is True:
        raise IntegrityError('full temporal market history cannot be asserted to pass a fit guard')
    if contract.get('full_temporal_market_history_required') is True:
        return {
            'version': VERSION, 'kind': FITS_KIND, 'root': payload['root'],
            'collection': payload['collection'], 'unavailable': _UNSUPPORTED_HISTORY,
            'fits': None, 'publication_status': 'unpublished', 'admitted_for_serving': False,
            'full_temporal_market_history_complete': False,
        }
    report = payload['histogram_report']
    if report.get('coverage_complete') is not True or payload.get('coverage', {}).get('acquired_projection_complete') is not True:
        raise IntegrityError('fit requires the complete acquired training join')
    members = payload['members']
    if not members:
        raise IntegrityError('fit requires explicit training member identities')
    if not report.get('prints'):
        return {
            'version': VERSION, 'kind': FITS_KIND, 'root': payload['root'],
            'collection': payload['collection'], 'unavailable': _EMPTY_TRAIN,
            'fits': None, 'publication_status': 'unpublished', 'admitted_for_serving': False,
            'event_period_cut_ns': payload['event_period_cut_ns'],
            'knowledge_cut_ns': payload['knowledge_cut_ns'],
            'histogram_identity': report['identity'],
        }
    identities = tuple(item['id'] for item in members)
    windows = {item['id']: {'end': item['end'], 'published_at': item['published_at'],
                            'history_complete': item['history_complete']}
               for item in members}
    event_period_cut = payload['event_period_cut_ns']
    knowledge_cut = payload['knowledge_cut_ns']
    # Kernel train_end must be at/after every member publication. Event-period
    # and knowledge cuts stay distinct in the published payload.
    kernel_train_end = knowledge_cut
    available_at = knowledge_cut
    timestamp(kernel_train_end)
    timestamp(available_at)
    fits = {}
    for spec in contract['adaptive_definitions']:
        name, weighting, pairs = spec['name'], spec['weighting'], _pairs(spec['probabilities'])
        probabilities = _fractions(pairs)
        fitted = fit_unpublished_cohort_definition(
            report, train_end=kernel_train_end, available_at=available_at,
            member_identities=identities, aggregation_unit=contract['aggregation_unit'],
            probabilities=probabilities, weighting=weighting, version=name, member_windows=windows)
        literal = _literal_from_histogram(tuple(report['histogram']), probabilities, weighting)
        _compare_fit(fitted, literal, name)
        fits[name] = {
            'definition': fitted['definition'], 'recipe': fitted['recipe'],
            'realized_count': fitted['realized_count'], 'realized_volume': fitted['realized_volume'],
            'realized_count_occupancy': fitted['realized_count_occupancy'],
            'realized_volume_occupancy': fitted['realized_volume_occupancy'],
            'publication_status': fitted['publication_status'],
            'literal_requested_thresholds': literal['requested_thresholds'],
            'histogram_identity': fitted['histogram_identity'],
            'output_kind': _UNPUBLISHED, 'admitted_for_serving': False,
            'fitted_boundary_kind': 'unpublished_training_quantile',
            'descriptive_training_bins_only': True,
        }
    eval_after = []
    post_train = None
    if evaluation_members is not None:
        for member in evaluation_members:
            item = schedule_member_key(member)
            if item['root'] != payload['root'] or item['collection'] != payload['collection']:
                raise ContractError('evaluation membership must stay on the same ROOT/COLLECTION')
            if item['event_start_ns'] >= available_at:
                eval_after.append(item)
        post_train = bool(eval_after)
    result = {
        'version': VERSION, 'kind': FITS_KIND, 'publication_status': 'unpublished',
        'output_kind': _UNPUBLISHED, 'admitted_for_serving': False,
        'root': payload['root'], 'collection': payload['collection'],
        'histogram_identity': report['identity'],
        'member_ids': identities,
        'event_period_cut_ns': event_period_cut,
        'knowledge_cut_ns': knowledge_cut,
        'kernel_train_end_ns': kernel_train_end,
        'available_at': available_at,
        'fits': fits, 'unavailable': None,
        'post_training_evaluation_population': post_train,
        'post_training_evaluation_disposition': None if post_train is not False else _NO_POST_TRAIN,
        'full_temporal_market_history_complete': False,
        'histogram_scope': HISTOGRAM_SCOPE,
        'fit_disposition': 'unpublished_acquired_projection_fit',
        'contract_identity': payload['contract_identity'],
        'helper_cpu_seconds': time.process_time() - started,
    }
    return result


def persist_training_fits(outputs, payload):
    if not isinstance(outputs, BoundedOutputs):
        raise ContractError('training fit persist requires bounded registered outputs')
    if type(payload) is not dict or payload.get('kind') != FITS_KIND:
        raise ContractError('only a completed full-training fit payload can be persisted')
    serializable = dict(payload)
    fits = payload.get('fits')
    if fits is not None:
        packed = {}
        for name, item in fits.items():
            definition = item['definition']
            packed[name] = {key: value for key, value in item.items() if key != 'definition'}
            packed[name]['definition_record'] = {
                'version': definition.version, 'aggregation_unit': definition.aggregation_unit,
                'channels': tuple((c.id, c.lower_inclusive, c.upper_exclusive, c.role)
                                  for c in definition.channels),
                'knots': definition.knots, 'partition': definition.partition,
                'origin': definition.origin, 'available_at': definition.available_at,
                'fit_recipe_id': definition.fit_recipe_id, 'id': definition.id,
            }
        serializable['fits'] = packed
    name = f"{payload['root']}-{payload['collection']}-training-fits.json.zst"
    return outputs.json_compressed(name, serializable, kind=FITS_KIND)


def _restore_definition(record):
    channels = tuple(CohortChannel(item[0], item[1], item[2], item[3]) for item in record['channels'])
    knots = tuple(record['knots'])
    definition = CohortDefinition(
        record['version'], record['aggregation_unit'], channels, knots,
        partition=record['partition'], origin=record['origin'],
        available_at=record['available_at'], fit_recipe_id=record['fit_recipe_id'])
    if definition.id != record['id']:
        raise IntegrityError('restored fitted definition identity changed')
    return definition


def restore_training_fits(reference):
    authenticate_artifact_reference(reference)
    payload = read_json_artifact(reference)
    if type(payload) is not dict or payload.get('kind') != FITS_KIND:
        raise IntegrityError('restored object is not a completed full-training fit payload')
    fits = payload.get('fits')
    if fits:
        restored = {}
        for name, item in fits.items():
            record = dict(item)
            definition = _restore_definition(record.pop('definition_record'))
            record['definition'] = definition
            restored[name] = record
        payload = dict(payload)
        payload['fits'] = restored
    return payload


def _definition_plan(fits, unavailable, unit_start, unit_end, *, collection_eval_disposition=None):
    plan = []
    for name in FIXED_FILTERS:
        definition = _all_definition() if name == 'all' else fixed_source_cohort(name)
        plan.append({'name': name, 'kind': 'fixed_source', 'definition': definition,
                     'start_ns': unit_start, 'end_ns': unit_end, 'unavailable': None,
                     'compare_original': True, 'causal': True})
    plan.append({'name': 'soft_benchmark_knots', 'kind': 'fixed_soft', 'definition': _soft_definition(),
                 'start_ns': unit_start, 'end_ns': unit_end, 'unavailable': None,
                 'compare_original': False, 'causal': True})
    for name, _, _ in ADAPTIVE_RECIPES:
        if collection_eval_disposition is not None:
            plan.append({'name': name, 'kind': 'adaptive', 'definition': None,
                         'start_ns': None, 'end_ns': None, 'unavailable': collection_eval_disposition,
                         'compare_original': False, 'causal': False})
            continue
        if unavailable is not None:
            plan.append({'name': name, 'kind': 'adaptive', 'definition': None,
                         'start_ns': None, 'end_ns': None, 'unavailable': unavailable,
                         'compare_original': False, 'causal': False})
            continue
        definition = fits[name]['definition']
        start = max(unit_start, definition.available_at)
        if start >= unit_end:
            plan.append({'name': name, 'kind': 'adaptive', 'definition': definition,
                         'start_ns': start, 'end_ns': unit_end, 'unavailable': _NO_INTERVAL,
                         'compare_original': False, 'causal': False})
            continue
        plan.append({'name': name, 'kind': 'adaptive', 'definition': definition,
                     'start_ns': start, 'end_ns': unit_end, 'unavailable': None,
                     'compare_original': False, 'causal': True})
    if len(plan) != 8:
        raise IntegrityError('current unit must evaluate the eight registered cohort definitions')
    return plan


def _bounds(prepared, start_ns, end_ns):
    import numpy as np

    if not len(prepared):
        return 0, 0
    stamps = prepared.values['t']
    left = int(np.searchsorted(stamps, start_ns, side='left'))
    right = int(np.searchsorted(stamps, end_ns, side='left'))
    return left, right


class _IntervalIndex:
    def __init__(self, batches):
        self._batches = []
        self._first = []
        self._last = []
        self._cache = {}
        for batch in batches:
            if not len(batch):
                continue
            stamps = batch.values['t']
            self._batches.append(batch)
            self._first.append(int(stamps[0]))
            self._last.append(int(stamps[-1]))

    def slices(self, start_ns, end_ns):
        key = (start_ns, end_ns)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        found = []
        begin = bisect_left(self._last, start_ns)
        stop = bisect_left(self._first, end_ns)
        for batch in self._batches[begin:stop]:
            left, right = _bounds(batch, start_ns, end_ns)
            if left < right:
                found.append((batch, left, right))
        found = tuple(found)
        self._cache[key] = found
        return found


def _add_slices(window, index, start_ns, end_ns, counts):
    added = 0
    for prepared, left, right in index.slices(start_ns, end_ns):
        window.add_prepared(prepared, left, right)
        counts['sliced_prints'] += right - left
        added += right - left
    counts['full_path_print_contributions'] += added
    return added


def _window(definition, instrument_id, start_ns, end_ns, delay):
    return CohortWindow(definition=definition, instrument_id=instrument_id, start_ns=start_ns,
                        end_ns=end_ns, latency_ns=delay, maximum_prints=MAX_PRINTS)


def _included(channels):
    matches = [channel for channel in channels if channel['role'] == 'included']
    if len(matches) != 1:
        raise IntegrityError('source-filter comparison needs exactly one included channel')
    return matches[0]


def _compare_common(channel, flow, *, prints_key):
    checked = 0
    for name in _COMMON:
        if channel[name] != flow[name]:
            raise IntegrityError(f'cohort {channel["channel_id"]} {name} differs from the original measured flow')
        checked += 1
    if channel[prints_key] != flow['prints']:
        raise IntegrityError(f'cohort {channel["channel_id"]} prints differ from the original measured flow')
    checked += 1
    if channel['history_complete'] != flow['coverage_complete']:
        raise IntegrityError('cohort history flag differs from the original measured flow coverage')
    checked += 1
    return checked


def _compare_source_record(record, original, name):
    flows = original['flows']
    if name == 'all':
        channel = record['channels'][0]
        checked = _compare_common(channel, flows['all'], prints_key='weighted_prints')
        if record['prints'] != original['prints'] or record['volume'] != flows['all']['volume']:
            raise IntegrityError('all-flow cohort population differs from the original measured window')
        return checked + 2, 1
    channel = _included(record['channels'])
    checked = _compare_common(channel, flows[name], prints_key='weighted_prints')
    excluded_volume = sum((item['volume'] for item in record['channels'] if item['role'] != 'included'), Fraction(0))
    excluded_prints = sum((item['weighted_prints'] for item in record['channels'] if item['role'] != 'included'),
                          Fraction(0))
    if channel['volume'] + excluded_volume != flows['all']['volume']:
        raise IntegrityError('excluded source channels do not reconcile to all-flow volume')
    if channel['weighted_prints'] + excluded_prints != original['prints']:
        raise IntegrityError('excluded source channels do not reconcile to all-flow prints')
    if record['prints'] != original['prints'] or record['volume'] != flows['all']['volume']:
        raise IntegrityError('source-filter window population differs from the original all-flow population')
    return checked + 4, 1


def _compose_atoms(atom_records):
    if not atom_records:
        return None
    composed = []
    total_prints = sum(atom['prints'] for atom in atom_records)
    total_volume = sum(atom['volume'] for atom in atom_records)
    n = len(atom_records[0]['channels'])
    for index in range(n):
        opening = atom_records[0]['openings'][index]
        close = exact_number(opening)
        high = low = close
        high_at = low_at = None
        high_order = low_order = None
        buy = sell = unknown = weighted = Fraction(0)
        contributing = 0
        for atom in atom_records:
            channel = atom['channels'][index]
            offset = close - channel['open']
            translated_high = channel['high'] + offset
            translated_low = channel['low'] + offset
            translated_close = channel['close'] + offset
            if translated_high > high:
                high = translated_high
                high_at = channel['high_at_ns']
                high_order = channel['high_source_order']
            if translated_low < low:
                low = translated_low
                low_at = channel['low_at_ns']
                low_order = channel['low_source_order']
            buy += channel['buy']
            sell += channel['sell']
            unknown += channel['unknown']
            weighted += channel['weighted_prints']
            contributing += channel['contributing_prints']
            close = translated_close
        composed.append({
            'channel_id': atom_records[0]['channels'][index]['channel_id'],
            'open': exact_number(opening), 'high': high, 'low': low, 'close': close,
            'high_at_ns': high_at, 'low_at_ns': low_at,
            'high_source_order': high_order, 'low_source_order': low_order,
            'buy': buy, 'sell': sell, 'unknown': unknown, 'volume': buy + sell + unknown,
            'weighted_prints': weighted, 'contributing_prints': contributing,
            'observed_signed_lower': (buy - sell) - unknown,
            'observed_signed_upper': (buy - sell) + unknown,
        })
    return {'channels': composed, 'prints': total_prints, 'volume': total_volume}


def _compare_composed(whole, composed):
    if composed is None:
        raise IntegrityError('atom composition produced no path for a supported whole interval')
    if whole['prints'] != composed['prints'] or whole['volume'] != composed['volume']:
        raise IntegrityError('composed atom populations differ from the whole cohort window')
    if len(whole['channels']) != len(composed['channels']):
        raise IntegrityError('composed atom channels differ from the whole cohort window')
    for channel, item in zip(whole['channels'], composed['channels'], strict=True):
        for name in ('channel_id', 'open', 'high', 'low', 'close', 'high_at_ns', 'low_at_ns',
                     'high_source_order', 'low_source_order', 'buy', 'sell', 'unknown', 'volume',
                     'weighted_prints', 'contributing_prints', 'observed_signed_lower',
                     'observed_signed_upper'):
            if channel[name] != item[name]:
                raise IntegrityError(f'composed atom {name} differs from the whole cohort window')
    partition = sum((channel['volume'] for channel in composed['channels']), Fraction(0))
    unknown = sum((channel['unknown'] for channel in composed['channels']), Fraction(0))
    if whole['partition'] and partition != whole['volume']:
        raise IntegrityError('composed atom partition mass differs from the whole cohort window')
    if unknown != sum((channel['unknown'] for channel in whole['channels']), Fraction(0)):
        raise IntegrityError('composed atom unknown mass differs from the whole cohort window')


def _pack_channels(channels):
    return [[channel[name] for name in _CHANNEL_FIELDS] for channel in channels]


def _pack_bar(meta, record):
    return [meta[name] if name in meta else record[name] for name in _BAR_FIELDS]


def _definition_identity(item):
    definition = item['definition']
    if definition is None:
        return {'name': item['name'], 'kind': item['kind'], 'unavailable': item['unavailable'],
                'publication_status': 'unpublished', 'output_kind': _UNPUBLISHED,
                'causal': item.get('causal', False)}
    return {
        'name': item['name'], 'kind': item['kind'], 'definition_id': definition.id,
        'definition_version': definition.version, 'definition_origin': definition.origin,
        'definition_available_at': definition.available_at, 'fit_recipe_id': definition.fit_recipe_id,
        'aggregation_unit': definition.aggregation_unit, 'partition': definition.partition,
        'channels': tuple((c.id, c.lower_inclusive, c.upper_exclusive, c.role) for c in definition.channels),
        'knots': definition.knots, 'start_ns': item['start_ns'], 'end_ns': item['end_ns'],
        'unavailable': item['unavailable'], 'publication_status': 'unpublished',
        'output_kind': _UNPUBLISHED, 'admitted_for_serving': False,
        'causal': item.get('causal', True),
    }


def _atom_support(atom, start_ns, end_ns):
    original_start, original_end = atom['event_start_ns'], atom['event_end_ns']
    if original_end <= start_ns or original_start >= end_ns:
        return None
    supported_start = max(original_start, start_ns)
    supported_end = min(original_end, end_ns)
    if supported_start >= supported_end:
        return None
    return {
        'bin': atom['bin'], 'event_start_ns': original_start, 'event_end_ns': original_end,
        'known_at_ns': atom['known_at_ns'], 'supported_start_ns': supported_start,
        'supported_end_ns': supported_end, 'clipped': supported_start != original_start,
        'source_coverage_complete': atom['trade']['source_coverage_complete'],
        'coordinate_complete': atom['trade']['coordinate_complete'],
        'original': atom,
    }


def _publish_path(record):
    return {
        'event_start_ns': record['event_start_ns'], 'event_end_ns': record['event_end_ns'],
        'known_at_ns': record['known_at_ns'], 'source_delay_ns': record['source_delay_ns'],
        'definition_id': record['definition_id'], 'definition_origin': record['definition_origin'],
        'definition_available_at': record['definition_available_at'],
        'fit_recipe_id': record['fit_recipe_id'], 'publication_status': record['publication_status'],
        'source_coverage_complete': record['source_coverage_complete'],
        'coordinate_complete': record['coordinate_complete'],
        'flow_history_complete': record['flow_history_complete'],
        'prints': record['prints'], 'volume': record['volume'],
        'partition_volume': record['partition_volume'],
        'partition_weighted_prints': record['partition_weighted_prints'],
        'empty_observed_window': record['empty_observed_window'],
        'source_key': record['source_key'],
        'first_print': record['first_print'], 'last_print': record['last_print'],
        'openings': record['openings'],
        'channels': record['channels'],
        'output_kind': record['output_kind'],
        'admitted_for_serving': record['admitted_for_serving'],
    }


def _decode_current(trade_storage, instrument_ids, delay, start_ns, end_ns, counts):
    grouped = {raw_id: [] for raw_id in instrument_ids}
    keys = {raw_id: None for raw_id in instrument_ids}
    last = {raw_id: (None, None) for raw_id in instrument_ids}
    partitioned = 0
    for table in read_series_tables(trade_storage):
        counts['decoded_batches'] += 1
        counts['decoded_rows'] += len(table)
        _require_series(table)
        assigned = 0
        for raw_id in instrument_ids:
            kept = _filter_instrument(table, raw_id)
            if not len(kept):
                continue
            assigned += len(kept)
            key = _unique_source_key(kept)
            if keys[raw_id] is None:
                keys[raw_id] = key
            elif key != keys[raw_id]:
                raise IntegrityError('a cohort window cannot join distinct acquired source streams')
            t = kept['t'].to_pylist()
            order = kept['source_order'].to_pylist()
            known = kept['known_at_ns'].to_pylist()
            prev_t, prev_order = last[raw_id]
            if prev_t is not None and (t[0] < prev_t or order[0] <= prev_order):
                raise IntegrityError('current series lost original source order')
            if any(t[i] < t[i - 1] or order[i] <= order[i - 1] for i in range(1, len(t))):
                raise IntegrityError('current series lost original source order')
            if any(stamp < start_ns or stamp >= end_ns for stamp in t):
                raise IntegrityError('current series print is outside the retained unit window')
            if any(item != stamp + delay for stamp, item in zip(t, known)):
                raise IntegrityError('current series delay does not match the retained source delay')
            last[raw_id] = (t[-1], order[-1])
            grouped[raw_id].append(kept)
        if assigned != len(table):
            raise IntegrityError('retained trade does not belong to a declared current raw instrument')
        partitioned += assigned
    if partitioned != counts['decoded_rows']:
        raise IntegrityError('retained and partitioned current trade counts do not reconcile')
    return grouped, keys


def _prepare_groups(grouped, counts):
    prepared = {}
    try:
        for raw_id, tables in grouped.items():
            items = []
            prepared[raw_id] = items
            for table in tables:
                for offset in range(0, len(table), BATCH_ROWS):
                    batch = prepare_trade_batch(table.slice(offset, min(BATCH_ROWS, len(table) - offset)))
                    items.append(batch)
                    counts['prepared_prints'] += len(batch)
        return prepared
    except BaseException:
        _release(prepared)
        raise


def _release(prepared):
    for items in prepared.values():
        for batch in items:
            if not batch.released:
                batch.close()


def _row_channel(root, collection, source_path, date, split, interval_kind, bin_number,
                 start_ns, end_ns, source_complete, coordinate_complete, definition_name,
                 channel, availability, *, independent):
    signed = channel['signed']
    return {
        'root': root, 'collection': collection, 'source_path': source_path, 'date': date,
        'chronological_split': split, 'interval_kind': interval_kind, 'bin': bin_number,
        'event_start_ns': start_ns, 'event_end_ns': end_ns,
        'coverage_source_complete': source_complete,
        'coverage_coordinate_complete': coordinate_complete,
        'definition': definition_name, 'channel_id': channel['channel_id'],
        'channel_role': channel['role'], 'prints': channel['contributing_prints'],
        'volume': channel['volume'], 'weighted_prints': channel['weighted_prints'],
        'count_occupancy': channel['count_occupancy'],
        'volume_occupancy': channel['volume_occupancy'],
        'open': channel['open'], 'high': channel['high'], 'low': channel['low'],
        'close': channel['close'], 'signed': signed,
        'signed_excursion': channel['high'] - channel['low'],
        'unknown': channel['unknown'],
        'observed_signed_lower': channel['observed_signed_lower'],
        'observed_signed_upper': channel['observed_signed_upper'],
        'availability': availability,
        'date_block_id': f'{root}:{collection}:{date}',
        'independent_date_unit': independent,
        'acquisition_overlap_key': f'{root}:{date}',
        'row_role': 'date_summary' if independent else 'interval_measurement',
    }


def _unavailable_row(root, collection, source_path, date, split, interval_kind, bin_number,
                     start_ns, end_ns, source_complete, coordinate_complete, definition_name,
                     disposition, *, independent):
    return {
        'root': root, 'collection': collection, 'source_path': source_path, 'date': date,
        'chronological_split': split, 'interval_kind': interval_kind, 'bin': bin_number,
        'event_start_ns': start_ns, 'event_end_ns': end_ns,
        'coverage_source_complete': source_complete,
        'coverage_coordinate_complete': coordinate_complete,
        'definition': definition_name, 'channel_id': None, 'channel_role': None,
        'prints': None, 'volume': None, 'weighted_prints': None,
        'count_occupancy': None, 'volume_occupancy': None,
        'open': None, 'high': None, 'low': None, 'close': None, 'signed': None,
        'signed_excursion': None, 'unknown': None,
        'observed_signed_lower': None, 'observed_signed_upper': None,
        'availability': disposition,
        'date_block_id': f'{root}:{collection}:{date}',
        'independent_date_unit': independent,
        'acquisition_overlap_key': f'{root}:{date}',
        'row_role': 'date_summary' if independent else 'interval_measurement',
    }


def measure_source_window_cohorts(receipt, *, training, contract, outputs, expected_member=None):
    """Whole-window and one-minute unpublished cohort paths for one source receipt."""
    if not isinstance(outputs, BoundedOutputs):
        raise ContractError('cohort window measurement requires bounded registered outputs')
    cpu, counts = _cpu(), _counts()
    byte_start = outputs.written
    entry = started = time.process_time()
    validate_cohort_production_contract(contract)
    if expected_member is None:
        unit = receipt.get('unit') if type(receipt) is dict else None
        if type(unit) is not dict:
            raise IntegrityError('evaluation receipt lost its unit')
        expected_member = {
            'root': unit['root'], 'source_path': unit['source_path'],
            'source_metadata_sha256': unit['source_metadata_sha256'],
            'event_start_ns': unit['event_start_ns'], 'event_end_ns': unit['event_end_ns'],
            'utc_date': unit.get('utc_date') or unit.get('cash_date'),
        }
    joined = authenticate_cohort_receipt(receipt, expected_member=expected_member, contract=contract)
    started = _acc(cpu, 'receipt_authentication_and_membership', started)
    measured = joined['measured']
    unit = joined['unit']
    expected = joined['expected']
    delay = joined['delay']
    start_ns, end_ns = expected['event_start_ns'], expected['event_end_ns']
    if type(training) is not dict or training.get('kind') != FITS_KIND:
        raise ContractError('evaluation requires a completed training-fit payload for this collection')
    if training.get('root') != expected['root'] or training.get('collection') != expected['collection']:
        raise IntegrityError('evaluation cannot apply a cross-collection or cross-root fitted threshold')
    if training.get('contract_identity') != contract_identity(contract):
        raise IntegrityError('training fit contract identity does not join the caller-supplied contract')
    fits = training.get('fits')
    unavailable = training.get('unavailable')
    collection_disp = None
    if (training.get('post_training_evaluation_population') is False
            and joined['split'] != 'train' and expected['collection'] == 'dated'):
        collection_disp = training.get('post_training_evaluation_disposition') or _NO_POST_TRAIN
    if fits is None and unavailable is None:
        unavailable = _NO_FIT
    plan = _definition_plan(fits, unavailable, start_ns, end_ns,
                            collection_eval_disposition=collection_disp)
    started = _acc(cpu, 'fit_and_cut_availability', started)
    instruments = measured.get('instruments')
    if type(instruments) is not list:
        raise IntegrityError('current measurement lost its raw-instrument population')
    if any(type(item.get('instrument_id')) is not int for item in instruments):
        raise IntegrityError('current measurement lost an exact raw instrument identity')
    raw_ids = tuple(item['instrument_id'] for item in instruments)
    if len(set(raw_ids)) != len(raw_ids):
        raise IntegrityError('duplicate current instrument IDs')
    grouped, source_keys = _decode_current(joined['trades'], raw_ids, delay, start_ns, end_ns, counts)
    started = _acc(cpu, 'current_cache_decoding', started)
    prepared = {}
    reports = []
    rowset = []
    compared_fields = compared_channels = 0
    split = joined['split']
    date = expected['utc_date']
    try:
        prepared = _prepare_groups(grouped, counts)
        indexes = {raw_id: _IntervalIndex(items) for raw_id, items in prepared.items()}
        started = _acc(cpu, 'preparation_and_filtering', started)
        for instrument in instruments:
            raw_id = int(instrument['instrument_id'])
            index = indexes[raw_id]
            atoms = instrument.get('atomic_windows')
            if type(atoms) is not list:
                raise IntegrityError('current measurement lost its one-minute atomic windows')
            whole_original = instrument['whole_window']
            instrument_report = {
                'instrument_id': raw_id, 'coordinate': instrument['coordinate'],
                'source_key': source_keys[raw_id],
                'whole_source_coverage_complete': whole_original['source_coverage_complete'],
                'whole_coordinate_complete': whole_original['coordinate_complete'],
                'definitions': [],
            }
            for item in plan:
                identity = _definition_identity(item)
                if item['unavailable'] is not None:
                    early = []
                    for atom in atoms:
                        early.append({
                            'bin': atom['bin'], 'event_start_ns': atom['event_start_ns'],
                            'event_end_ns': atom['event_end_ns'],
                            'disposition': item['unavailable'],
                            'inherited_source_coverage_complete': atom['trade']['source_coverage_complete'],
                            'inherited_coordinate_complete': atom['trade']['coordinate_complete'],
                        })
                        rowset.append(_unavailable_row(
                            expected['root'], expected['collection'], expected['source_path'], date,
                            split, 'atomic_minute', atom['bin'], atom['event_start_ns'],
                            atom['event_end_ns'], atom['trade']['source_coverage_complete'],
                            atom['trade']['coordinate_complete'], item['name'], item['unavailable'],
                            independent=False))
                    rowset.append(_unavailable_row(
                        expected['root'], expected['collection'], expected['source_path'], date,
                        split, 'whole_window', None, start_ns, end_ns,
                        whole_original['source_coverage_complete'],
                        whole_original['coordinate_complete'], item['name'], item['unavailable'],
                        independent=True))
                    instrument_report['definitions'].append({
                        **identity, 'whole': {'disposition': item['unavailable']},
                        'atomic_unavailable': early,
                        'atomic': {'schema': {'bar': _BAR_FIELDS, 'channel': _CHANNEL_FIELDS},
                                   'bars': [], 'channels': []},
                    })
                    counts['report_bars'] += 1 + len(early)
                    continue
                definition, supported_start, supported_end = item['definition'], item['start_ns'], item['end_ns']
                supported = [_atom_support(atom, supported_start, supported_end) for atom in atoms]
                present = [row for row in supported if row is not None]
                missing = []
                for atom, row in zip(atoms, supported, strict=True):
                    if row is None and atom['event_end_ns'] <= supported_start:
                        missing.append({
                            'bin': atom['bin'], 'event_start_ns': atom['event_start_ns'],
                            'event_end_ns': atom['event_end_ns'], 'disposition': _BEFORE_AVAIL,
                            'inherited_source_coverage_complete': atom['trade']['source_coverage_complete'],
                            'inherited_coordinate_complete': atom['trade']['coordinate_complete'],
                        })
                        rowset.append(_unavailable_row(
                            expected['root'], expected['collection'], expected['source_path'], date,
                            split, 'atomic_minute', atom['bin'], atom['event_start_ns'],
                            atom['event_end_ns'], atom['trade']['source_coverage_complete'],
                            atom['trade']['coordinate_complete'], item['name'], _BEFORE_AVAIL,
                            independent=False))
                    elif row is None:
                        raise IntegrityError('atomic cadence shifted away from the measured one-minute bounds')
                whole_source = whole_original['source_coverage_complete'] if item['kind'] != 'adaptive' else (
                    all(row['source_coverage_complete'] for row in present) if present else False)
                whole_coord = whole_original['coordinate_complete'] if item['kind'] != 'adaptive' else (
                    all(row['coordinate_complete'] for row in present) if present else False)
                whole = _window(definition, raw_id, supported_start, supported_end, delay)
                counts['instantiated_bars'] += 1
                started = _acc(cpu, 'orchestration_and_report_assembly', started)
                _add_slices(whole, index, supported_start, supported_end, counts)
                started = _acc(cpu, 'whole_path_updates', started)
                atom_windows = []
                for row in present:
                    atom_window = _window(definition, raw_id, row['supported_start_ns'],
                                          row['supported_end_ns'], delay)
                    counts['instantiated_bars'] += 1
                    _add_slices(atom_window, index, row['supported_start_ns'], row['supported_end_ns'], counts)
                    atom_windows.append((row, atom_window))
                started = _acc(cpu, 'atomic_path_updates', started)
                whole_record = whole.record(source_coverage_complete=whole_source,
                                            coordinate_complete=whole_coord)
                atom_records = []
                packed_bars, packed_channels = [], []
                for row, atom_window in atom_windows:
                    record = atom_window.record(source_coverage_complete=row['source_coverage_complete'],
                                                coordinate_complete=row['coordinate_complete'])
                    atom_records.append(record)
                    meta = {**row, 'prints': record['prints'], 'volume': record['volume'],
                            'empty_observed_window': record['empty_observed_window'],
                            'partition_volume': record['partition_volume'],
                            'partition_weighted_prints': record['partition_weighted_prints']}
                    packed_bars.append(_pack_bar(meta, record))
                    packed_channels.append(_pack_channels(record['channels']))
                    counts['report_channels'] += len(record['channels'])
                    for channel in record['channels']:
                        rowset.append(_row_channel(
                            expected['root'], expected['collection'], expected['source_path'], date,
                            split, 'atomic_minute', row['bin'], row['supported_start_ns'],
                            row['supported_end_ns'], row['source_coverage_complete'],
                            row['coordinate_complete'], item['name'], channel, 'available',
                            independent=False))
                started = _acc(cpu, 'whole_atomic_finalization', started)
                if item['compare_original']:
                    fields, channels = _compare_source_record(whole_record, whole_original, item['name'])
                    compared_fields += fields
                    compared_channels += channels
                    for row, record in zip(present, atom_records, strict=True):
                        if row['clipped']:
                            continue
                        fields, channels = _compare_source_record(record, row['original']['trade'], item['name'])
                        compared_fields += fields
                        compared_channels += channels
                started = _acc(cpu, 'original_source_comparisons', started)
                if present:
                    _compare_composed(whole_record, _compose_atoms(atom_records))
                elif whole_record['prints'] != 0:
                    raise IntegrityError('supported adaptive interval lost its atomic coverage')
                started = _acc(cpu, 'full_atom_composition', started)
                for channel in whole_record['channels']:
                    rowset.append(_row_channel(
                        expected['root'], expected['collection'], expected['source_path'], date,
                        split, 'whole_window', None, supported_start, supported_end,
                        whole_source, whole_coord, item['name'], channel, 'available',
                        independent=True))
                counts['report_bars'] += 1 + len(packed_bars) + len(missing)
                counts['report_channels'] += len(whole_record['channels'])
                instrument_report['definitions'].append({
                    **identity, 'whole': _publish_path(whole_record),
                    'atomic': {'schema': {'bar': _BAR_FIELDS, 'channel': _CHANNEL_FIELDS},
                               'bars': packed_bars, 'channels': packed_channels},
                    'atomic_unavailable': missing,
                    'supported_start_ns': supported_start, 'supported_end_ns': supported_end,
                    'atom_count': len(packed_bars), 'channel_count': len(whole_record['channels']),
                })
            reports.append(instrument_report)
    finally:
        _release(prepared)
    counts['rowset_rows'] = len(rowset)
    result = {
        'version': VERSION, 'kind': WINDOW_KIND, 'publication_status': 'unpublished',
        'output_kind': _UNPUBLISHED, 'admitted_for_serving': False,
        'f11_serving_admitted': False, 'context_or_location_evaluation': False,
        'family_statistics_complete': False,
        'unit': {'root': expected['root'], 'collection': expected['collection'],
                 'source_path': expected['source_path'], 'utc_date': date,
                 'event_start_ns': start_ns, 'event_end_ns': end_ns,
                 'source_metadata_sha256': expected['source_metadata_sha256'],
                 'source_variant': source_variant(expected['source_path'])},
        'unit_identity': joined['unit_identity'],
        'measurement_reference': joined['measurement_reference'],
        'training': {
            'root': training['root'], 'collection': training['collection'],
            'histogram_identity': training.get('histogram_identity'),
            'available_at': training.get('available_at'),
            'event_period_cut_ns': training.get('event_period_cut_ns'),
            'knowledge_cut_ns': training.get('knowledge_cut_ns'),
            'unavailable': training.get('unavailable'),
            'post_training_evaluation_population': training.get('post_training_evaluation_population'),
            'fit_disposition': training.get('fit_disposition'),
        },
        'definitions': [_definition_identity(item) for item in plan],
        'channel_schema': _CHANNEL_FIELDS, 'bar_schema': _BAR_FIELDS,
        'row_schema': _ROW_FIELDS,
        'instruments': reports,
        'exact_original_source_fields_compared': compared_fields,
        'exact_original_source_channels_compared': compared_channels,
        'date_aggregation': {
            'date_block_id': f"{expected['root']}:{expected['collection']}:{date}",
            'acquisition_overlap_key': f"{expected['root']}:{date}",
            'independent_date_unit': f"{expected['root']}:{expected['collection']}:{date}",
            'minute_rows_are_not_independent_dates': True,
            'overlapping_collections_are_not_independent_dates': True,
        },
        'full_temporal_market_history_complete': False,
        'passed': True,
    }
    variant = source_variant(expected['source_path'])
    prefix = f"{expected['root']}-{expected['collection']}-{start_ns}-{variant}"
    window_ref = outputs.json_compressed(f'{prefix}-cohort-window.json.zst', result, kind=WINDOW_KIND)
    rowset_ref = outputs.json_compressed(
        f'{prefix}-cohort-rowset.json.zst',
        {'kind': ROWSET_KIND, 'schema': _ROW_FIELDS, 'rows': rowset,
         'date_aggregation': result['date_aggregation']},
        kind=ROWSET_KIND)
    cpu['serialization'] += window_ref.get('cpu_seconds', 0.0) + rowset_ref.get('cpu_seconds', 0.0)
    counts['serialized_bytes'] = window_ref['size_bytes'] + rowset_ref['size_bytes']
    helper_cpu = time.process_time() - entry
    named = sum(cpu[name] for name in _CPU_NAMES if name != 'orchestration_and_report_assembly')
    cpu['orchestration_and_report_assembly'] = helper_cpu - named
    if cpu['orchestration_and_report_assembly'] < 0:
        raise IntegrityError('disjoint cohort helper CPU stages exceed the measured helper total')
    return {
        'reference': window_ref,
        'rowset_reference': rowset_ref,
        'rowset': rowset,
        'cpu_components_disjoint': cpu,
        'helper_cpu_seconds': helper_cpu,
        'serialization_cpu_seconds': cpu['serialization'],
        'output_bytes': outputs.written - byte_start,
        'workload_counts': counts,
        'instruments': len(reports),
        'definitions': 8,
        'exact_original_source_fields_compared': compared_fields,
        'exact_original_source_channels_compared': compared_channels,
        'passed': True,
    }


def select_training_fits(training_fits, *, root, collection):
    if type(training_fits) is not dict:
        raise ContractError('training fits must be an explicit mapping or payload')
    if training_fits.get('kind') == FITS_KIND:
        if training_fits.get('root') != root or training_fits.get('collection') != collection:
            raise IntegrityError('selected training fits escaped the declared ROOT/COLLECTION')
        return training_fits
    key = (root, collection)
    if key in training_fits:
        return training_fits[key]
    named = training_fits.get(root, {})
    if type(named) is dict and collection in named:
        return named[collection]
    raise IntegrityError('no training fit payload for the declared ROOT/COLLECTION')
