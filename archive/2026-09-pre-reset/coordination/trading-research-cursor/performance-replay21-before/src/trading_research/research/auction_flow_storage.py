"""Bounded immutable event/measurement files with complete Arrow round trips.

Files stay inside the registered attempt directory. References contain actual
file hashes and schemas; failed partial files retain their bytes and cost.
The source projection is written once and reused by subsequent consumers.
"""
from __future__ import annotations

import io
import hashlib
import json
from pathlib import Path
import time

from trading_research.research.auction_flow_arrow import VERSION as VALUE_HASH_VERSION, value_digest
from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import canonical_json, file_digest


VERSION = 'auction-flow-bounded-parquet-storage-v1'
PHYSICAL_ENCODING_KEY = b'auction_flow.physical_encoding'
LOGICAL_SCHEMA_KEY = b'auction_flow.logical_arrow_schema'


class _BoundedFile(io.RawIOBase):
    def __init__(self, owner, path):
        self.owner, self.path = owner, path
        self.stream = path.open('xb')
        self.written = 0

    def writable(self):
        return True

    def seekable(self):
        return False

    def tell(self):
        return self.written

    def write(self, payload):
        if self.closed or self.owner.failed:
            raise IntegrityError('closed or failed bounded output cannot resume')
        size = len(payload)
        if self.written + size > self.owner.maximum_file or self.owner.written + size > self.owner.maximum_total:
            self.owner.failed = True
            raise ContractError('registered derived-output allowance exhausted before write')
        try:
            count = self.stream.write(payload)
            self.written += count
            self.owner.written += count
            if count != size:
                raise IntegrityError('incomplete registered artifact write')
            return count
        except BaseException:
            self.owner.failed = True
            raise

    def flush(self):
        if not self.stream.closed:
            self.stream.flush()

    def close(self):
        if not self.closed:
            try:
                self.flush()
            finally:
                self.stream.close()
                super().close()


class BoundedOutputs:
    def __init__(self, directory, *, maximum_total_bytes, maximum_file_bytes):
        if (type(maximum_total_bytes) is not int or type(maximum_file_bytes) is not int
                or not 1 <= maximum_file_bytes <= maximum_total_bytes):
            raise ContractError('explicit finite aggregate and individual artifact limits required')
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=False)
        self.maximum_total, self.maximum_file = maximum_total_bytes, maximum_file_bytes
        self.written = 0
        self.failed = False
        self.names, self.files = set(), []

    def create(self, name):
        if (self.failed or type(name) is not str or not name or name in self.names
                or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.' for c in name)
                or name.startswith('.')):
            raise ContractError('new bounded artifact name required')
        self.names.add(name)
        return _BoundedFile(self, self.directory / name)

    def reference(self, name, *, kind):
        path = self.directory / name
        if self.failed or name not in self.names or path.stat().st_size > self.maximum_file:
            raise IntegrityError('partial or unbounded artifact cannot be published')
        ref = {'path': str(path), 'sha256': file_digest(path), 'size_bytes': path.stat().st_size, 'kind': kind}
        self.files.append(ref)
        return ref

    def json(self, name, value, *, kind):
        payload = canonical_json(value) + b'\n'
        with self.create(name) as stream:
            stream.write(payload)
        return self.reference(name, kind=kind)

    def json_compressed(self, name, value, *, kind, maximum_uncompressed_bytes=512 * 1024**2,
                        measurement_fast_path=False):
        """Lossless Zstandard bytes of the unchanged exact canonical JSON.

        The full decompressed bytes are checked before publication. Compression
        never converts exact fractions, timestamps or integer quantities.
        """
        import pyarrow as pa

        started = time.process_time()
        if type(maximum_uncompressed_bytes) is not int or not 1 <= maximum_uncompressed_bytes <= 512 * 1024**2:
            raise ContractError('finite decompressed measurement-artifact allowance required')
        if type(measurement_fast_path) is not bool:
            raise ContractError('explicit exact measurement serialization path required')
        if measurement_fast_path:
            from trading_research.research.auction_flow_structural_encoding import exact_measurement_json
            payload = exact_measurement_json(value) + b'\n'
        else:
            payload = canonical_json(value) + b'\n'
        if len(payload) > maximum_uncompressed_bytes:
            self.failed = True
            raise ContractError('uncompressed exact measurement exceeds its declared memory/output-read bound')
        compressed = pa.compress(payload, codec='zstd', asbytes=True)
        with self.create(name) as stream:
            stream.write(compressed)
        ref = self.reference(name, kind=kind)
        try:
            restored = pa.decompress(Path(ref['path']).read_bytes(), decompressed_size=len(payload), codec='zstd', asbytes=True)
        except BaseException:
            self.failed = True
            raise
        if restored != payload:
            self.failed = True
            raise IntegrityError('exact measurement bytes failed complete compressed round trip')
        return {**ref, 'encoding': 'canonical-json-zstd-v1', 'uncompressed_size_bytes': len(payload),
                'uncompressed_sha256': hashlib.sha256(payload).hexdigest(), 'roundtrip_exact': True,
                'cpu_seconds': time.process_time() - started,
                'canonicalizer': 'exact_measurement_domain_v1' if measurement_fast_path else 'generic_exact_v1'}


def read_json_artifact(reference, *, maximum_uncompressed_bytes=512 * 1024**2):
    """Read an explicitly retained, size/hash-bound exact measurement artifact."""
    import pyarrow as pa

    if (type(maximum_uncompressed_bytes) is not int or not 1 <= maximum_uncompressed_bytes <= 512 * 1024**2
            or type(reference.get('size_bytes')) is not int or not 0 <= reference['size_bytes'] <= 512 * 1024**2):
        raise ContractError('bounded complete measurement reference required')
    path = Path(reference['path'])
    if path.stat().st_size != reference['size_bytes']:
        raise IntegrityError('retained exact measurement length changed')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != reference['sha256']:
        raise IntegrityError('retained exact measurement content changed')
    if reference.get('encoding') == 'canonical-json-zstd-v1':
        size = reference.get('uncompressed_size_bytes')
        if type(size) is not int or not 0 <= size <= maximum_uncompressed_bytes:
            raise ContractError('retained decompressed measurement exceeds its declared bound')
        raw = pa.decompress(raw, decompressed_size=size, codec='zstd', asbytes=True)
        if len(raw) != size or hashlib.sha256(raw).hexdigest() != reference['uncompressed_sha256']:
            raise IntegrityError('retained measurement decompression changed exact canonical bytes')
    elif reference.get('encoding') is not None:
        raise ContractError('unsupported exact measurement encoding')
    elif len(raw) > maximum_uncompressed_bytes:
        raise ContractError('retained exact JSON exceeds its declared read bound')
    return json.loads(raw)


class ParquetSeries:
    def __init__(self, outputs, name, *, maximum_rows_per_file=262144, encoding='plain'):
        if (not isinstance(outputs, BoundedOutputs) or type(name) is not str or not name
                or type(maximum_rows_per_file) is not int or not 65536 <= maximum_rows_per_file <= 1_000_000
                or encoding not in ('plain', 'delta', 'structural')):
            raise ContractError('bounded registered Parquet series required')
        self.outputs, self.name, self.maximum_rows = outputs, name, maximum_rows_per_file
        self.encoding = encoding
        self.schema = self.storage_schema = self.writer = self.stream = None
        self.current_rows = self.rows = self.groups = self.compared_values = 0
        self.current_name = None
        self.expected = []
        self.files = []
        self.closed = self.failed = False
        self.cpu_seconds = 0.0

    def abort(self):
        self.failed = self.outputs.failed = True
        try:
            if self.writer is not None:
                self.writer.close()
        except Exception:
            pass
        finally:
            if self.stream is not None:
                self.stream.close()
            self.writer = self.stream = None

    def _finish_file(self):
        import pyarrow.parquet as pq

        if self.writer is None:
            return
        self.writer.close()
        self.stream.close()
        ref = self.outputs.reference(self.current_name, kind='auction_flow_parquet')
        with pq.ParquetFile(ref['path']) as stored:
            if (stored.metadata.num_rows != self.current_rows or not stored.schema_arrow.equals(self.storage_schema, check_metadata=True)
                    or stored.num_row_groups != len(self.expected)):
                raise IntegrityError('retained Parquet schema or population differs from its source projection')
            for index, (rows, sha, codec) in enumerate(self.expected):
                table = stored.read_row_group(index, use_threads=False).combine_chunks()
                if codec is not None:
                    from trading_research.research.auction_flow_structural_encoding import decode_table
                    table = decode_table(table, codec)
                    table = table.replace_schema_metadata(self.schema.metadata)
                if len(table) != rows or value_digest(table) != sha:
                    raise IntegrityError('retained event/measurement fields failed exact complete Arrow round trip')
                self.compared_values += rows * table.num_columns
        self.files.append({**ref, 'rows': self.current_rows, 'row_groups': len(self.expected),
            'value_hash_version': VALUE_HASH_VERSION,
            'row_group_values': [{'rows': rows, 'sha256': sha, **({'codec': codec} if codec is not None else {})}
                                 for rows, sha, codec in self.expected],
            **({'physical_encoding': 'structural'} if self.encoding == 'structural' else {})})
        self.writer = self.stream = None
        self.expected = []
        self.current_rows = 0

    def append(self, table, source=None):
        import pyarrow as pa
        import pyarrow.parquet as pq

        if self.closed or self.failed or not isinstance(table, pa.Table):
            raise IntegrityError('open exact Arrow projection series required')
        started = time.process_time()
        try:
            # Dictionary encoding is storage representation, not an additional
            # source value. Materialize it consistently before byte comparison.
            for index, field in enumerate(table.schema):
                if pa.types.is_dictionary(field.type):
                    table = table.set_column(index, field.name, table.column(index).cast(field.type.value_type))
            if self.schema is None:
                self.schema = table.schema
                self.storage_schema = self.schema
                if self.encoding == 'structural':
                    metadata = dict(self.schema.metadata or {})
                    if PHYSICAL_ENCODING_KEY in metadata or LOGICAL_SCHEMA_KEY in metadata:
                        raise IntegrityError('an encoded physical table must be restored before reuse')
                    metadata[PHYSICAL_ENCODING_KEY] = b'structural-v1'
                    metadata[LOGICAL_SCHEMA_KEY] = self.schema.serialize().to_pybytes()
                    self.storage_schema = self.schema.with_metadata(metadata)
            elif not self.schema.equals(table.schema, check_metadata=True):
                raise IntegrityError('event schema changed within one retained series')
            offset = 0
            while offset < len(table):
                if self.writer is None:
                    self.current_name = f'{self.name}-{len(self.files):04d}.parquet'
                    self.stream = self.outputs.create(self.current_name)
                    dictionary = [field.name for field in self.schema if pa.types.is_string(field.type)
                        or pa.types.is_large_string(field.type) or pa.types.is_binary(field.type) or pa.types.is_large_binary(field.type)]
                    options = {'use_dictionary': dictionary}
                    if self.encoding in ('delta', 'structural'):
                        encodings = {}
                        for field in self.schema:
                            if pa.types.is_integer(field.type):
                                encodings[field.name] = 'DELTA_BINARY_PACKED'
                            elif pa.types.is_floating(field.type):
                                encodings[field.name] = 'BYTE_STREAM_SPLIT'
                            elif field.name in dictionary:
                                encodings[field.name] = 'DELTA_BYTE_ARRAY'
                        options = {'use_dictionary': False, 'column_encoding': encodings}
                    self.writer = pq.ParquetWriter(self.stream, self.storage_schema, compression='zstd', compression_level=3,
                        write_statistics=True, version='2.6', **options)
                amount = min(65536, self.maximum_rows - self.current_rows, len(table) - offset)
                part = table.slice(offset, amount).combine_chunks()
                sha, codec, physical = value_digest(part), None, part
                if self.encoding == 'structural':
                    from trading_research.research.auction_flow_structural_encoding import encode_table
                    physical, codec = encode_table(part)
                    physical = physical.replace_schema_metadata(self.storage_schema.metadata)
                self.expected.append((amount, sha, codec))
                self.writer.write_table(physical, row_group_size=amount)
                self.current_rows += amount
                self.rows += amount
                self.groups += 1
                offset += amount
                if self.current_rows == self.maximum_rows:
                    self._finish_file()
        except BaseException:
            self.abort()
            raise
        finally:
            self.cpu_seconds += time.process_time() - started

    def finish(self):
        if self.closed or self.failed:
            raise IntegrityError('failed or completed Parquet series cannot publish again')
        started = time.process_time()
        try:
            self._finish_file()
            self.closed = True
            self.cpu_seconds += time.process_time() - started
            return {'version': VERSION, 'series': self.name, 'rows': self.rows, 'row_groups': self.groups,
                'encoding': self.encoding, 'compression': 'zstd-level-3',
                'schema': None if self.schema is None else str(self.schema), 'files': self.files,
                'compared_values': self.compared_values, 'roundtrip_exact': True,
                'cpu_seconds': self.cpu_seconds,
                'serialized_bytes': sum(r['size_bytes'] for r in self.files)}
        except BaseException:
            self.cpu_seconds += time.process_time() - started
            self.abort()
            raise


def read_series_tables(series):
    """Read every logical value from a complete, size/hash-bound series.

    Physical encodings are private storage. All event, anchor, model and
    comparison consumers use this boundary to receive original Arrow values.
    Per-row-group logical digests detect edited transform descriptors as well
    as changed stored values. The final series count is checked on exhaustion.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    if (not isinstance(series, dict) or series.get('roundtrip_exact') is not True
            or type(series.get('rows')) is not int or series['rows'] < 0
            or not isinstance(series.get('files'), list)):
        raise IntegrityError('complete verified logical series reference required')
    count = 0
    schema = None
    for reference in series['files']:
        path = Path(reference['path'])
        if (type(reference.get('size_bytes')) is not int or not 0 < reference['size_bytes'] <= 512 * 1024**2
                or path.stat().st_size != reference['size_bytes'] or file_digest(path) != reference['sha256']):
            raise IntegrityError('retained logical series file changed or exceeded its bound')
        with pq.ParquetFile(path) as stored:
            metadata = stored.schema_arrow.metadata or {}
            encoded = reference.get('physical_encoding') == 'structural'
            if encoded:
                raw_schema = metadata.get(LOGICAL_SCHEMA_KEY)
                if (metadata.get(PHYSICAL_ENCODING_KEY) != b'structural-v1'
                        or not isinstance(raw_schema, bytes) or not 0 < len(raw_schema) <= 1024**2):
                    raise IntegrityError('encoded physical file lost its exact logical schema')
                logical_schema = pa.ipc.read_schema(pa.BufferReader(raw_schema))
            else:
                if reference.get('physical_encoding') is not None or PHYSICAL_ENCODING_KEY in metadata or LOGICAL_SCHEMA_KEY in metadata:
                    raise IntegrityError('encoded physical values cannot bypass logical restoration')
                logical_schema = stored.schema_arrow
            if schema is None:
                schema = logical_schema
            if (not logical_schema.equals(schema, check_metadata=True) or str(logical_schema) != series['schema']
                    or stored.metadata.num_rows != reference['rows']
                    or stored.num_row_groups != reference['row_groups']
                    or len(reference['row_group_values']) != stored.num_row_groups):
                raise IntegrityError('retained logical series schema or population changed')
            file_count = 0
            for index, expected in enumerate(reference['row_group_values']):
                if (type(expected.get('rows')) is not int or not 0 < expected['rows'] <= 65536
                        or stored.metadata.row_group(index).num_rows != expected['rows']
                        or encoded != ('codec' in expected)):
                    raise IntegrityError('retained logical row group lost its complete restoration contract')
                table = stored.read_row_group(index, use_threads=False).combine_chunks()
                if encoded:
                    from trading_research.research.auction_flow_structural_encoding import decode_table
                    table = decode_table(table, expected['codec']).replace_schema_metadata(logical_schema.metadata)
                if not table.schema.equals(logical_schema, check_metadata=True) or value_digest(table) != expected['sha256']:
                    raise IntegrityError('retained logical values differ from their complete verified row group')
                file_count += len(table)
                yield table
            if file_count != reference['rows']:
                raise IntegrityError('retained logical file has incomplete or duplicated rows')
            count += file_count
    if count != series['rows']:
        raise IntegrityError('retained logical series lost rows or changed multiplicity')
