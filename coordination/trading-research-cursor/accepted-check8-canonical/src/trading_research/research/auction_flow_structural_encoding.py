"""Lossless physical encodings for retained auction/flow observations.

Only stored representations change. Every decoded field has the original
Arrow type, nulls and exact value. Integer differences never pass through a
float. A row-group descriptor records each reversible operation; source
addresses, original clocks, exact column-reference differences and -1
sentinels are restored before consumption.
"""
from __future__ import annotations

from fractions import Fraction
import json

from trading_research.errors import ContractError, IntegrityError


VERSION = 'auction-flow-exact-integer-structural-encoding-v1'


def encode_table(table):
    """Return the physical table and its explicit ordered inverse operations.

    References always use the original input values. Descriptor order is also
    the restoration order, so a transformed reference is restored before any
    dependent column uses it. Nullable logical columns are left unchanged by
    sentinel encoding. An integer difference that cannot fit int64 retains
    its original values.
    """
    import pyarrow as pa
    import pyarrow.compute as pc

    if not isinstance(table, pa.Table) or len(table) > 65536:
        raise ContractError('one bounded logical Arrow row group required')
    encoded, operations, used = table, [], set()

    def transform(name, reference=None, sentinel=False):
        nonlocal encoded
        if name not in table.column_names or name in used:
            return
        field = table.schema.field(name)
        if field.type != pa.int64():
            return
        original = table[name]
        if reference is not None:
            if (reference not in table.column_names or table.schema.field(reference).type != pa.int64()
                    or table[reference].null_count or original.null_count):
                return
        if sentinel and (original.null_count or not field.nullable):
            return
        values = original
        if sentinel:
            values = pc.if_else(pc.equal(values, -1), pa.scalar(None, type=pa.int64()), values)
        try:
            if reference is not None:
                values = pc.subtract_checked(values, table[reference])
        except pa.ArrowInvalid:
            # A codec is never allowed to narrow the admitted integer domain.
            return
        if reference is None and not sentinel:
            return
        encoded = encoded.set_column(encoded.schema.get_field_index(name), field, values)
        operations.append({'column': name, 'reference': reference,
                           'null_restores_sentinel': -1 if sentinel else None})
        used.add(name)

    def present_lacks_trade_reference(name, reference):
        # A missing trade clock/order must not expand a present value into a
        # huge epoch or order residual. Fallback is a storage choice only.
        if (reference not in table.column_names or table.schema.field(name).type != pa.int64()
                or table.schema.field(reference).type != pa.int64()):
            return True
        present = pc.fill_null(pc.and_(pc.is_valid(table[name]), pc.not_equal(table[name], -1)), False)
        missing = pc.fill_null(pc.or_(pc.is_null(table[reference]), pc.equal(table[reference], -1)), False)
        return pc.any(pc.and_(present, missing)).as_py() is True

    native = 'event_start_ns' in table.column_names and 'event_end_ns' in table.column_names
    if native:
        transform('event_end_ns', 'event_start_ns')
        transform('known_at_ns', 'event_end_ns')
        transform('first_trade_at_ns', 'event_start_ns', sentinel=True)
        transform('first_trade_source_order', sentinel=True)
        for name in table.column_names:
            if (name in ('last_trade_at_ns', 'high_price_at_ns', 'low_price_at_ns',
                         'ofi_high_at_ns', 'ofi_low_at_ns')
                    or name.endswith(('__high_at_ns', '__low_at_ns'))):
                if not present_lacks_trade_reference(name, 'first_trade_at_ns'):
                    transform(name, 'first_trade_at_ns', sentinel=True)
            elif (name in ('last_trade_source_order', 'high_price_source_order', 'low_price_source_order')
                    or name.endswith(('__high_source_order', '__low_source_order'))):
                if not present_lacks_trade_reference(name, 'first_trade_source_order'):
                    transform(name, 'first_trade_source_order', sentinel=True)
        for name in table.column_names:
            if name.endswith('_at_ns') and name != 'known_at_ns':
                transform(name, 'event_start_ns', sentinel=True)
            elif name.endswith('_source_order'):
                transform(name, sentinel=True)
        for name in ('last_price_ticks', 'high_price_ticks', 'low_price_ticks'):
            transform(name, 'first_price_ticks')
    else:
        transform('known_at_ns', 't')
        transform('source_order', 'source_row')
        transform('ask', 'bid')
    return encoded, {'version': VERSION, 'operations': operations}


def decode_table(table, descriptor):
    """Restore exactly one physical row group before any research consumer."""
    import pyarrow as pa
    import pyarrow.compute as pc

    if (not isinstance(table, pa.Table) or len(table) > 65536
            or not isinstance(descriptor, dict) or set(descriptor) != {'version', 'operations'}
            or descriptor['version'] != VERSION or not isinstance(descriptor['operations'], list)
            or len(descriptor['operations']) > table.num_columns):
        raise IntegrityError('bounded complete structural row-group descriptor required')
    restored, changed = table, set()
    for operation in descriptor['operations']:
        if (not isinstance(operation, dict)
                or set(operation) != {'column', 'reference', 'null_restores_sentinel'}):
            raise IntegrityError('unknown structural integer operation')
        name, reference, sentinel = (operation[k] for k in ('column', 'reference', 'null_restores_sentinel'))
        if (type(name) is not str or name not in table.column_names or name in changed
                or table.schema.field(name).type != pa.int64()
                or reference is not None and (type(reference) is not str or reference not in table.column_names
                    or reference == name or restored.schema.field(reference).type != pa.int64()
                    or restored[reference].null_count)
                or sentinel is not None and (type(sentinel) is not int or sentinel != -1)
                or reference is None and sentinel is None):
            raise IntegrityError('changed, repeated or unsupported structural integer column')
        values = restored[name]
        try:
            if reference is not None:
                values = pc.add_checked(values, restored[reference])
            if sentinel is not None:
                values = pc.fill_null(values, sentinel)
        except pa.ArrowInvalid as exc:
            raise IntegrityError('structural integer restoration left the exact int64 domain') from exc
        restored = restored.set_column(restored.schema.get_field_index(name), restored.schema.field(name), values)
        changed.add(name)
    return restored


def exact_measurement_json(value, *, maximum_items=20_000_000):
    """The existing canonical JSON bytes for the explicit measurement domain.

    Measurement dictionaries contain built-in values, tuples, Fractions and
    the explicitly supported retained ValueArea record.
    Validate this narrower domain without the generic dataclass/enum/date
    conversion on every scalar. The C JSON encoder handles its native tree;
    only exact Fractions need a tagged default. No existing canonical format
    or reference reader changes. Full-byte parity is checked on retained data.
    """
    from dataclasses import fields
    from trading_research.measurements.tape import ValueArea

    record_fields = {ValueArea: tuple(f.name for f in fields(ValueArea))}
    if type(maximum_items) is not int or not 1 <= maximum_items <= 20_000_000:
        raise ContractError('bounded exact measurement tree required')
    pending, seen, count = [value], set(), 0
    while pending:
        current = pending.pop()
        count += 1
        if count > maximum_items:
            raise ContractError('exact measurement tree exceeds its declared item bound')
        kind = type(current)
        if kind is dict or kind is list or kind is tuple:
            identity = id(current)
            if identity in seen:
                continue
            seen.add(identity)
            if kind is dict:
                if any(type(key) is not str for key in current):
                    raise ContractError('exact measurement object keys must be strings')
                pending.extend(current.values())
            else:
                pending.extend(current)
        elif kind in record_fields:
            identity = id(current)
            if identity not in seen:
                seen.add(identity)
                pending.extend(getattr(current, f) for f in record_fields[kind])
        elif current is not None and kind not in (str, int, float, bool, Fraction):
            raise ContractError(f'unsupported exact measurement value: {kind.__name__}')

    def default(current):
        if type(current) is Fraction:
            return {'$fraction': [current.numerator, current.denominator]}
        if type(current) in record_fields:
            return {f: getattr(current, f) for f in record_fields[type(current)]}
        raise ContractError('unsupported exact measurement serialization value')

    return json.dumps(value, default=default, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')
