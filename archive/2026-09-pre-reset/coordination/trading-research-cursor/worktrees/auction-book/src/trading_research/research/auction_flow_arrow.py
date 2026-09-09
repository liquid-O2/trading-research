"""Exact scalar Arrow value hashes, independent of offsets and unused padding.

All valid integer/string/Boolean values and floating-point bits are retained.
Null validity is hashed separately; bytes underneath null slots have no value.
Schema types, column order and row multiplicity remain part of the digest.
"""
from __future__ import annotations

import hashlib
import json

from trading_research.errors import ContractError


VERSION = 'arrow-scalar-value-and-validity-v1'


def value_digest(table):
    import numpy as np
    import pyarrow as pa
    import pyarrow.compute as pc

    if not isinstance(table, pa.Table) or len(table) > 65536:
        raise ContractError('bounded scalar Arrow table required for value hashing')
    sha = hashlib.sha256()
    sha.update(VERSION.encode())
    sha.update(len(table).to_bytes(8, 'big'))
    for field, original in zip(table.schema, table.columns, strict=True):
        kind = field.type.value_type if pa.types.is_dictionary(field.type) else field.type
        column = original.cast(kind) if pa.types.is_dictionary(field.type) else original
        header = json.dumps([field.name, str(kind)], separators=(',', ':')).encode()
        sha.update(len(header).to_bytes(8, 'big'))
        sha.update(header)
        valid = pc.is_valid(column).to_numpy(zero_copy_only=False)
        sha.update(np.packbits(valid, bitorder='little').tobytes())
        if pa.types.is_null(kind):
            continue
        if pa.types.is_boolean(kind):
            values = pc.fill_null(column, False).to_numpy(zero_copy_only=False)
            sha.update(np.packbits(values, bitorder='little').tobytes())
        elif pa.types.is_integer(kind) or pa.types.is_floating(kind):
            filled = pc.fill_null(column, pa.scalar(0, type=kind)) if column.null_count else column
            values = filled.to_numpy(zero_copy_only=False)
            sha.update(values.astype(values.dtype.newbyteorder('<'), copy=False).tobytes(order='C'))
        elif (pa.types.is_string(kind) or pa.types.is_large_string(kind)
              or pa.types.is_binary(kind) or pa.types.is_large_binary(kind)):
            empty = '' if pa.types.is_string(kind) or pa.types.is_large_string(kind) else b''
            filled = pc.fill_null(column, pa.scalar(empty, type=kind)) if column.null_count else column
            flat = filled.combine_chunks()
            buffers = flat.buffers()
            dtype = '<i8' if pa.types.is_large_string(kind) or pa.types.is_large_binary(kind) else '<i4'
            offsets = np.frombuffer(buffers[1], dtype=dtype, count=len(flat) + 1,
                                    offset=flat.offset * np.dtype(dtype).itemsize)
            left, right = int(offsets[0]), int(offsets[-1])
            sha.update((offsets - left).tobytes())
            if right > left:
                sha.update(memoryview(buffers[2])[left:right])
        else:
            raise ContractError(f'unregistered scalar Arrow hash type: {kind}')
    return sha.hexdigest()
