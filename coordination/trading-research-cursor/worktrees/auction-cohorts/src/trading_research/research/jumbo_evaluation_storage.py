"""Lossless table storage for repeated Jumbo evaluation statistics.

This changes representation only. Every estimate, endpoint, support value,
bootstrap diagnostic, calibration cell and group remains. The historical
publication policy omits date vectors; the target's intended-date universes
and retained prediction rows supply those coordinates separately.
"""
from copy import deepcopy
import json
import math
import struct

from trading_research.errors import IntegrityError


SCHEMA = 'jumbo-grouped-date-evaluation-tables-v1'
VALUE_PATHS = (
    ('estimate',), ('lower',), ('upper',), ('valid_dates',), ('missing_dates',), ('valid_events',),
    ('support', 'independent_dates'), ('support', 'events'), ('support', 'sparse'), ('support', 'reasons'),
    ('bootstrap', 'lower'), ('bootstrap', 'upper'),
    ('bootstrap', 'valid_replicates'), ('bootstrap', 'invalid_replicates'),
)
POLICY_PATHS = (
    ('support', 'minimum_independent_dates'), ('support', 'minimum_events'),
    ('bootstrap', 'confidence'), ('bootstrap', 'replicates'), ('bootstrap', 'seed'),
    ('bootstrap', 'block_length'), ('bootstrap', 'method'), ('bootstrap', 'circular_end_wrap'),
)
BASE_KEYS = {p[0] for p in (*VALUE_PATHS, *POLICY_PATHS)}
DATE_KEYS = {'date_values', 'intended_dates'}


def normalized_json_bytes(value):
    """Canonical bytes for already normalized JSON, without a second tree walk."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def _at(value, path):
    for key in path:
        value = value[key]
    return value


def _intern(value, values, index):
    # JSON keys distinguish -0.0 from 0.0 and booleans from integers, unlike
    # Python tuple equality. No approximate equality or rounding is used.
    key = json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    if key not in index:
        index[key] = len(values)
        values.append(value)
    return index[key]


def pack_grouped_evaluation(value):
    """Pack repeated scalar cells and the existing calibration alias exactly."""
    from trading_research.research.jumbo_models import json_safe
    if value.get('kind') != 'grouped_date_evaluation':
        raise IntegrityError('grouped date evaluation required for table storage')
    rows, policies, row_index, policy_index = [], [], {}, {}

    def statistic(cell):
        if cell is None:
            return None
        for section in ('support', 'bootstrap'):
            expected = {p[1] for p in (*VALUE_PATHS, *POLICY_PATHS) if p[0] == section}
            if set(cell[section]) != expected:
                raise IntegrityError('unrecognized statistic fields must not be omitted by storage')
        policy = json_safe([_at(cell, path) for path in POLICY_PATHS])
        policy_id = _intern(policy, policies, policy_index)
        row = json_safe([_at(cell, path) for path in VALUE_PATHS]) + [policy_id]
        ref = _intern(row, rows, row_index)
        extras = {k: v for k, v in cell.items() if k not in BASE_KEYS | DATE_KEYS}
        return {'statistic': ref, 'extras': extras}

    groups = {}
    for name, group in value['groups'].items():
        if group.get('calibration') is not group.get('calibration_by_class'):
            raise IntegrityError('evaluation calibration alias changed; retain both definitions explicitly')
        packed = {k: v for k, v in group.items()
                  if k not in DATE_KEYS | {'metrics', 'paired', 'calibration', 'calibration_by_class'}}
        packed['metrics'] = {key: statistic(cell) for key, cell in group['metrics'].items()}
        packed['paired'] = statistic(group['paired'])
        classes = group['calibration_by_class']
        if classes is None:
            packed['calibration_by_class'] = None
        else:
            packed_classes = {}
            for class_name, definition in classes.items():
                bins = []
                for cell in definition['bins']:
                    bootstrap = cell['date_bootstrap']
                    if set(bootstrap) != {'predicted_mean', 'outcome_lower', 'outcome_upper', 'shared_weights'}:
                        raise IntegrityError('unrecognized calibration fields must not be omitted by storage')
                    bins.append({**{k: v for k, v in cell.items() if k != 'date_bootstrap'},
                                 'date_bootstrap': {k: statistic(v) if k != 'shared_weights' else v
                                                    for k, v in bootstrap.items()}})
                packed_classes[class_name] = {**{k: v for k, v in definition.items() if k != 'bins'}, 'bins': bins}
            packed['calibration_by_class'] = packed_classes
        groups[name] = packed
    return json_safe({'schema': SCHEMA,
        'statistics_columns': [list(p) for p in VALUE_PATHS] + [['policy_id']],
        'policy_columns': [list(p) for p in POLICY_PATHS],
        'statistics_rows': rows, 'policies': policies, 'groups': groups,
        'report_metadata': {k: v for k, v in value.items() if k != 'groups'},
        'calibration_alias': 'calibration_by_class',
        'date_vector_policy': 'Same existing publication policy: date_values and intended_dates omitted; target universes and exact prediction-row coordinates retained separately.'},
        omit_date_vectors=True)


def expand_grouped_evaluation(value, *, group_ids=None):
    """Restore the original published shape, optionally for selected groups.

    An individual group can be inspected without expanding all other groups.
    The original report metadata continues to describe the complete population.
    """
    if (value.get('schema') != SCHEMA
            or value.get('statistics_columns') != [list(p) for p in VALUE_PATHS] + [['policy_id']]
            or value.get('policy_columns') != [list(p) for p in POLICY_PATHS]
            or value.get('calibration_alias') != 'calibration_by_class'):
        raise IntegrityError('recognized complete evaluation storage schema required')
    rows, policies = value['statistics_rows'], value['policies']

    def statistic(cell):
        if cell is None:
            return None
        index = cell['statistic']
        if type(index) is not int or not 0 <= index < len(rows):
            raise IntegrityError('statistic reference is outside its retained table')
        row = rows[index]
        if len(row) != len(VALUE_PATHS) + 1:
            raise IntegrityError('statistic row width changed')
        policy = row[-1]
        if type(policy) is not int or not 0 <= policy < len(policies) or len(policies[policy]) != len(POLICY_PATHS):
            raise IntegrityError('statistic policy reference changed')
        if set(cell['extras']) & (BASE_KEYS | DATE_KEYS):
            raise IntegrityError('statistic extras overwrite a retained value')
        result = deepcopy(cell['extras'])
        for path, scalar in zip((*VALUE_PATHS, *POLICY_PATHS), (*row[:-1], *policies[policy]), strict=True):
            target = result
            for key in path[:-1]:
                target = target.setdefault(key, {})
            target[path[-1]] = deepcopy(scalar)
        return result

    selected = tuple(value['groups']) if group_ids is None else tuple(str(v) for v in group_ids)
    if any(key not in value['groups'] for key in selected):
        raise IntegrityError('requested evaluation group is absent')
    groups = {}
    for key in selected:
        packed = value['groups'][key]
        group = {k: deepcopy(v) for k, v in packed.items()
                 if k not in {'metrics', 'paired', 'calibration_by_class'}}
        group['metrics'] = {name: statistic(cell) for name, cell in packed['metrics'].items()}
        group['paired'] = statistic(packed['paired'])
        classes = packed['calibration_by_class']
        if classes is None:
            restored = None
        else:
            restored = {}
            for name, definition in classes.items():
                bins = []
                for cell in definition['bins']:
                    bins.append({**{k: deepcopy(v) for k, v in cell.items() if k != 'date_bootstrap'},
                                 'date_bootstrap': {k: statistic(v) if k != 'shared_weights' else v
                                                   for k, v in cell['date_bootstrap'].items()}})
                restored[name] = {**{k: deepcopy(v) for k, v in definition.items() if k != 'bins'}, 'bins': bins}
        group['calibration_by_class'] = group['calibration'] = restored
        groups[key] = group
    return {**deepcopy(value['report_metadata']), 'groups': groups}


def verify_packed_evaluation(original, packed):
    """Check every published field against the actual unpacked values.

    Expand one group at a time, without constructing or serializing a second
    hundred-megabyte report. Missing floats follow the existing JSON-null rule.
    """
    import numpy as np
    counts = {'groups': len(original['groups']), 'scalar_values': 0,
              'missing_numbers_retained_as_null': 0, 'maximum_absolute_float_error': 0.0}

    def same(left, right):
        if isinstance(left, np.generic):
            left = left.item()
        if isinstance(left, dict):
            keys = set(left) - DATE_KEYS
            if keys != set(right):
                raise IntegrityError('evaluation storage changed published field names')
            for key in keys:
                if key == 'calibration' and 'calibration_by_class' in left:
                    if right[key] is not right['calibration_by_class']:
                        raise IntegrityError('evaluation storage lost its calibration alias')
                    continue
                same(left[key], right[key])
        elif isinstance(left, (list, tuple, np.ndarray)):
            if not isinstance(right, list) or len(left) != len(right):
                raise IntegrityError('evaluation storage changed a published vector')
            for a, b in zip(left, right, strict=True):
                same(a, b)
        elif isinstance(left, float):
            if not math.isfinite(left):
                if right is not None:
                    raise IntegrityError('missing evaluation value was changed')
                counts['missing_numbers_retained_as_null'] += 1
            elif type(right) is not float or struct.pack('!d', left) != struct.pack('!d', right):
                raise IntegrityError('evaluation storage changed an exact floating value')
            counts['scalar_values'] += 1
        else:
            if type(left) is not type(right) or left != right:
                raise IntegrityError('evaluation storage changed a value or its type')
            counts['scalar_values'] += 1

    same({k: v for k, v in original.items() if k != 'groups'}, packed['report_metadata'])
    if set(original['groups']) != set(packed['groups']):
        raise IntegrityError('evaluation storage changed the group population')
    for key, group in original['groups'].items():
        same(group, expand_grouped_evaluation(packed, group_ids=(key,))['groups'][key])
    return {**counts, 'passed': True, 'comparison': 'Every published field; floats identical at64 bits, missing nonfinite values retain the existing JSON-null policy.'}
