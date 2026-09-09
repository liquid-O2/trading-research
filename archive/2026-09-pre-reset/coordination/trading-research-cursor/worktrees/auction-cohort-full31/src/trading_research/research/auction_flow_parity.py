"""Complete ordered parity of retained series across different physical cuts."""
from __future__ import annotations

from trading_research.errors import IntegrityError
from trading_research.research.auction_flow_arrow import value_digest
from trading_research.research.auction_flow_storage import read_series_tables


def _blocks(series):
    import pyarrow as pa

    pending, rows = [], 0
    schema = None
    for item in series:
        for table in read_series_tables(item):
            if schema is None:
                schema = table.schema
            if table.schema != schema:
                raise IntegrityError('retained parity input schema changed')
            offset = 0
            while offset < len(table):
                take = min(65536 - rows, len(table) - offset)
                pending.append(table.slice(offset, take))
                rows += take
                offset += take
                if rows == 65536:
                    yield pa.concat_tables(pending).combine_chunks()
                    pending, rows = [], 0
    if pending:
        yield pa.concat_tables(pending).combine_chunks()


def compare_series(expected, observed, *, float_tolerances=None):
    """Compare all rows/fields, preserving original order and multiplicity.

    Raw/event series require exact valid scalar bits, including floating source
    fields. Only native floating integrals may use an explicit (atol, rtol).
    """
    import numpy as np
    import pyarrow as pa

    rows = exact = floating = 0
    maximum = 0.0
    a, b = iter(_blocks(expected)), iter(_blocks(observed))
    while True:
        left, right = next(a, None), next(b, None)
        if left is None or right is None:
            if left is not None or right is not None:
                raise IntegrityError('retained partition parity lost rows or duplicated events')
            break
        if len(left) != len(right) or left.schema != right.schema:
            raise IntegrityError('retained partition parity changed its original schema or row order')
        float_names = [] if float_tolerances is None else [f.name for f in left.schema if pa.types.is_floating(f.type)]
        if value_digest(left.drop(float_names)) != value_digest(right.drop(float_names)):
            raise IntegrityError('retained partition parity changed an exact source value, path, clock or mask')
        exact += len(left) * (left.num_columns - len(float_names))
        for name in float_names:
            x, y = left[name].to_numpy(), right[name].to_numpy()
            if (left[name].null_count or right[name].null_count or not np.isfinite(x).all() or not np.isfinite(y).all()
                    or not np.allclose(x, y, atol=float_tolerances[0], rtol=float_tolerances[1])):
                raise IntegrityError('retained native floating integral changed outside its declared tolerance')
            maximum = max(maximum, float(np.max(np.abs(x - y), initial=0)))
            floating += len(left)
        rows += len(left)
    if rows != sum(s['rows'] for s in expected) or rows != sum(s['rows'] for s in observed):
        raise IntegrityError('retained parity metadata does not match its complete physical rows')
    return {'passed': True, 'rows': rows, 'exact_field_comparisons': exact, 'floating_field_comparisons': floating,
        'float_tolerances': float_tolerances, 'maximum_float_absolute_error': maximum,
        'scope': 'complete ordered values and multiplicity across all retained series files'}
