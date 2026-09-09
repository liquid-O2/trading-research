"""Virtual quote series reconstructed from immutable original source Parquet.

Logical quote observations stay exact. Physical quote Parquet is not written.
One required finish replay is charged; later consumer rereads are not free.
"""
from __future__ import annotations

import copy
import sys
import time
from pathlib import Path

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import digest, file_digest, canonical_json
from trading_research.research.auction_flow_arrow import VERSION as VALUE_HASH_VERSION, value_digest
from trading_research.research.auction_flow_data import (
    CARRY_VERSION as SOURCE_CARRY_VERSION,
    VERSION as STREAM_VERSION,
    AuctionFlowStream,
)
from trading_research.research.auction_flow_storage import BoundedOutputs, read_json_artifact


VERSION = 'auction-flow-raw-source-quote-replay-v1'
ENCODING = 'raw-source-quote-replay-v1'
BATCH_ROWS = 65536
MEASUREMENT_CARRY_VERSION = 'auction-flow-measurement-continuation-v1'
_IMPLEMENTATION_FILES = (
    ('auction_flow_data.py', 'trading_research.research.auction_flow_data'),
    ('data/compact.py', 'trading_research.data.compact'),
    ('data/compact_native.py', 'trading_research.data.compact_native'),
    ('data/reconcile.py', 'trading_research.data.reconcile'),
    ('auction_flow_arrow.py', 'trading_research.research.auction_flow_arrow'),
    ('auction_flow_quote_replay.py', 'trading_research.research.auction_flow_quote_replay'),
)


def _dataset_for(root):
    return f'quantpad/cme__{root.lower()}-continuous-futures__mbp-1'


def _source_identity(manifest):
    if not isinstance(manifest, dict):
        raise IntegrityError('complete original source stream manifest required')
    return {key: value for key, value in manifest.items() if key != 'source_cpu_components'}


def _materialize_quote_table(table):
    import pyarrow as pa

    if not isinstance(table, pa.Table):
        raise IntegrityError('open exact Arrow projection series required')
    for index, field in enumerate(table.schema):
        if pa.types.is_dictionary(field.type):
            table = table.set_column(index, field.name, table.column(index).cast(field.type.value_type))
    return table.combine_chunks()


def _serialize_schema(schema):
    return {'ipc_hex': schema.serialize().to_pybytes().hex(), 'text': str(schema)}


def _restore_schema(payload):
    import pyarrow as pa

    if payload is None:
        return None
    try:
        raw = bytes.fromhex(payload['ipc_hex'])
        if not 0 < len(raw) <= 1024**2:
            raise IntegrityError('quote replay lost its exact logical Arrow schema')
        schema = pa.ipc.read_schema(pa.BufferReader(raw))
    except IntegrityError:
        raise
    except Exception as exc:
        raise IntegrityError('quote replay lost its exact logical Arrow schema') from exc
    if str(schema) != payload.get('text'):
        raise IntegrityError('quote replay logical schema text does not match its serialized Arrow schema')
    return schema


def _bound_source_index_reference(reference):
    if (not isinstance(reference, dict) or type(reference.get('path')) is not str or not reference['path']
            or type(reference.get('sha256')) is not str or len(reference['sha256']) != 64
            or type(reference.get('size_bytes')) is not int
            or not 0 <= reference['size_bytes'] <= 512 * 1024**2):
        raise ContractError('bounded frozen source-index reference required')
    return copy.deepcopy(reference)


def _initial_source_continuation(continuation, *, start_ns, end_ns):
    if continuation is None:
        return None
    if not isinstance(continuation, dict):
        raise ContractError('initial quote replay continuation is source-only AuctionFlowStream carry or None')
    if (continuation.get('version') == MEASUREMENT_CARRY_VERSION or 'instruments' in continuation
            or (isinstance(continuation.get('source'), dict) and 'blocked' not in continuation)):
        raise ContractError('initial quote replay continuation cannot be a measurement continuation')
    if continuation.get('version') != SOURCE_CARRY_VERSION:
        raise ContractError('initial quote replay continuation is source-only AuctionFlowStream carry or None')
    if continuation.get('next_start_ns') == end_ns:
        raise ContractError('initial quote replay continuation cannot be this window\'s terminal source carry')
    if continuation.get('next_start_ns') != start_ns:
        raise IntegrityError('source continuation is changed, nonadjacent, uncompleted or from another lineage')
    return copy.deepcopy(continuation)


def implementation_identity():
    """Pin replay-relevant source files and the exact reconstructing runtime."""
    import importlib
    import numpy
    import pyarrow as pa

    files = {}
    for name, module_name in _IMPLEMENTATION_FILES:
        module = sys.modules.get(module_name) or importlib.import_module(module_name)
        path = Path(module.__file__).resolve()
        files[name] = {'sha256': file_digest(path), 'size_bytes': path.stat().st_size}
    return {'files': files, 'value_hash_version': VALUE_HASH_VERSION,
            'python': '{}.{}.{}'.format(*sys.version_info[:3]), 'numpy': numpy.__version__,
            'pyarrow': pa.__version__}


def _require_implementation(recorded):
    current = implementation_identity()
    if (not isinstance(recorded, dict) or recorded.get('files') != current['files']
            or recorded.get('value_hash_version') != current['value_hash_version']
            or recorded.get('python') != current['python'] or recorded.get('numpy') != current['numpy']
            or recorded.get('pyarrow') != current['pyarrow']):
        raise IntegrityError('quote replay implementation or runtime changed; refuse silent reinterpretation')


def _producer_manifest(manifest):
    if (not isinstance(manifest, dict) or manifest.get('version') != STREAM_VERSION
            or manifest.get('encoding') == ENCODING or 'replay_descriptor' in manifest
            or 'source_cpu_components' not in manifest
            or 'canonical_selected_raw_stream' not in manifest
            or 'source_all_field_arrow_stream_sha256' not in manifest
            or 'source_continuation' not in manifest or 'projection' not in manifest
            or 'sources' not in manifest):
        raise IntegrityError('original completed producer stream manifest required; a quote replay cannot be its own reference')
    return manifest


def _stream_kwargs(descriptor):
    paths = descriptor['source_paths']
    if not isinstance(paths, (list, tuple)) or not paths:
        raise IntegrityError('quote replay descriptor lost its explicit source paths')
    return dict(data_root=Path(descriptor['data_root']), dataset=descriptor['dataset'],
                start_ns=descriptor['start_ns'], end_ns=descriptor['end_ns'],
                maximum_scan_rows=descriptor['maximum_scan_rows'], latency_ns=descriptor['latency_ns'],
                batch_rows=BATCH_ROWS, source_paths=tuple(paths),
                continuation=descriptor['initial_continuation'])


def _iter_quote_replay(descriptor, *, check_implementation=True, accounting=None):
    """Replay logical quote chunks from original sources. Source identity after the last yield."""
    metadata_started = time.process_time()
    if (not isinstance(descriptor, dict) or descriptor.get('encoding') != ENCODING
            or descriptor.get('version') != VERSION or descriptor.get('roundtrip_exact') is True
            or descriptor.get('published') is True or type(descriptor.get('rows')) is not int
            or descriptor['rows'] < 0 or not isinstance(descriptor.get('chunks'), list)
            or descriptor.get('batch_rows') != BATCH_ROWS):
        raise IntegrityError('complete unpublished quote replay descriptor required')
    if check_implementation:
        _require_implementation(descriptor.get('implementation'))
    expected_schema = _restore_schema(descriptor.get('logical_schema'))
    chunks = descriptor['chunks']
    if expected_schema is None and chunks:
        raise IntegrityError('quote replay descriptor has chunks without a logical schema')
    index = read_json_artifact(descriptor['source_index_reference'])
    stream = AuctionFlowStream(**_stream_kwargs(descriptor), index=index)
    metadata_cpu = time.process_time() - metadata_started
    cursor = 0
    rows = 0
    for batch in stream:
        for original in batch.quotes:
            table = _materialize_quote_table(original)
            if expected_schema is None:
                raise IntegrityError('quote replay produced logical quotes that were never recorded')
            if not table.schema.equals(expected_schema, check_metadata=True):
                raise IntegrityError('replayed quote schema differs from the recorded logical schema')
            offset = 0
            while offset < len(table):
                if cursor >= len(chunks):
                    raise IntegrityError('quote replay produced extra logical chunks')
                expected = chunks[cursor]
                amount = expected.get('rows')
                if type(amount) is not int or not 1 <= amount <= BATCH_ROWS:
                    raise IntegrityError('quote replay chunk lost its recorded logical boundary')
                part = table.slice(offset, amount).combine_chunks()
                if len(part) != amount:
                    raise IntegrityError('quote replay lost a recorded logical quote chunk boundary')
                if value_digest(part) != expected.get('sha256'):
                    raise IntegrityError('replayed quote values differ from their complete recorded logical chunk')
                rows += amount
                cursor += 1
                offset += amount
                yield part
    metadata_started = time.process_time()
    if cursor != len(chunks) or rows != descriptor['rows']:
        raise IntegrityError('quote replay missed logical chunks or changed multiplicity')
    observed = stream.manifest()
    expected_identity = descriptor.get('source_identity')
    if (digest(_source_identity(observed)) != descriptor.get('source_identity_sha256')
            or digest(_source_identity(observed)) != digest(expected_identity)
            or digest(expected_identity) != descriptor.get('source_identity_sha256')):
        raise IntegrityError('replayed source identity differs from the original producer stream manifest')
    if accounting is not None:
        accounting['metadata_cpu_seconds'] = (metadata_cpu + time.process_time() - metadata_started
            + observed['source_cpu_components']['source_metadata_and_open'])


def _verify_quote_replay_descriptor(descriptor, *, accounting=None):
    """Private verifier: candidate descriptor need not carry a success flag."""
    compared = 0
    for table in _iter_quote_replay(descriptor, check_implementation=True, accounting=accounting):
        compared += len(table) * table.num_columns
    return compared


def read_quote_replay_tables(series):
    """Yield recorded logical quote tables, then enforce the original source identity."""
    if (not isinstance(series, dict) or series.get('roundtrip_exact') is not True
            or series.get('encoding') != ENCODING or type(series.get('rows')) is not int
            or series['rows'] < 0 or not isinstance(series.get('replay_descriptor'), dict)
            or not isinstance(series.get('files'), list)):
        raise IntegrityError('complete verified quote replay series required')
    if series['files']:
        raise IntegrityError('quote replay series cannot carry physical quote Parquet files')
    descriptor = read_json_artifact(series['replay_descriptor'])
    schema = _restore_schema(descriptor.get('logical_schema'))
    expected = {'version': VERSION, 'series': descriptor['series'], 'rows': descriptor['rows'],
                'row_groups': descriptor['row_groups'], 'schema': None if schema is None else str(schema),
                'serialized_bytes': series['replay_descriptor']['size_bytes'],
                'compared_values': descriptor['rows'] * (0 if schema is None else len(schema))}
    if any(series.get(key) != value for key, value in expected.items()):
        raise IntegrityError('published quote replay summary differs from its exact descriptor')
    count = 0
    groups = 0
    for table in _iter_quote_replay(descriptor, check_implementation=True):
        count += len(table)
        groups += 1
        yield table
    if count != series['rows'] or groups != series.get('row_groups'):
        raise IntegrityError('published quote replay series lost rows or changed multiplicity')


class QuoteReplaySeries:
    def __init__(self, outputs, name, *, data_root, source_index_reference, root, start_ns, end_ns,
                 source_paths, maximum_scan_rows, latency_ns=250_000_000, continuation=None):
        if (not isinstance(outputs, BoundedOutputs) or type(name) is not str or not name
                or type(root) is not str or root not in ('NQ', 'ES')
                or type(start_ns) is not int or type(end_ns) is not int or not 0 <= start_ns < end_ns < 2**63
                or type(latency_ns) is not int or not 0 <= latency_ns <= 1_000_000_000
                or end_ns + latency_ns >= 2**63
                or type(maximum_scan_rows) is not int or maximum_scan_rows < 1
                or type(source_paths) is not tuple or not source_paths
                or len(set(source_paths)) != len(source_paths)
                or any(type(path) is not str or not path for path in source_paths)):
            raise ContractError('bounded registered raw-source quote replay series required')
        self.outputs, self.name = outputs, name
        self.data_root = Path(data_root).resolve()
        self.source_index_reference = _bound_source_index_reference(source_index_reference)
        self.root, self.dataset = root, _dataset_for(root)
        self.start_ns, self.end_ns = start_ns, end_ns
        self.source_paths = source_paths
        self.maximum_scan_rows = maximum_scan_rows
        self.latency_ns = latency_ns
        self.continuation = _initial_source_continuation(continuation, start_ns=start_ns, end_ns=end_ns)
        self.schema = None
        self.chunks = []
        self.chunk_metadata_bytes = 0
        self.rows = self.groups = self.compared_values = 0
        self.closed = self.failed = False
        self.cpu_seconds = 0.0

    def abort(self):
        self.failed = self.outputs.failed = True

    def append(self, table, source=None):
        if self.closed or self.failed:
            raise IntegrityError('open exact Arrow projection series required')
        started = time.process_time()
        try:
            table = _materialize_quote_table(table)
            if self.schema is None:
                if len(table):
                    self.schema = table.schema
            elif not self.schema.equals(table.schema, check_metadata=True):
                raise IntegrityError('event schema changed within one retained series')
            offset = 0
            while offset < len(table):
                amount = min(BATCH_ROWS, len(table) - offset)
                part = table.slice(offset, amount).combine_chunks()
                digest_sha = value_digest(part)
                chunk = {'rows': amount, 'sha256': digest_sha}
                chunk_bytes = len(canonical_json(chunk)) + 1
                if self.rows + amount > self.maximum_scan_rows or self.chunk_metadata_bytes + chunk_bytes > max(1024, self.outputs.maximum_file):
                    raise ContractError('quote replay rows or retained chunk metadata exceed declared bounds')
                self.chunk_metadata_bytes += chunk_bytes
                self.chunks.append(chunk)
                self.rows += amount
                self.groups += 1
                offset += amount
                if len(self.chunks) > self.maximum_scan_rows:
                    raise ContractError('quote replay chunk metadata exceeds its declared memory bound')
        except BaseException:
            self.abort()
            raise
        finally:
            self.cpu_seconds += time.process_time() - started

    def _descriptor_payload(self, source_manifest):
        producer = _producer_manifest(source_manifest)
        if (producer.get('start_ns') != self.start_ns or producer.get('end_ns') != self.end_ns
                or producer.get('dataset') != self.dataset
                or producer.get('event_latency_scenario_ns') != self.latency_ns):
            raise IntegrityError('producer stream window does not join this quote replay series')
        paths = producer.get('explicit_source_variant_paths')
        if paths is not None and tuple(paths) != self.source_paths:
            raise IntegrityError('producer stream source paths do not join this quote replay series')
        identity = _source_identity(producer)
        return {'version': VERSION, 'encoding': ENCODING, 'series': self.name,
            'data_root': str(self.data_root),
            'source_index_reference': copy.deepcopy(self.source_index_reference),
            'root': self.root, 'dataset': self.dataset, 'start_ns': self.start_ns, 'end_ns': self.end_ns,
            'source_paths': list(self.source_paths), 'latency_ns': self.latency_ns,
            'maximum_scan_rows': self.maximum_scan_rows, 'batch_rows': BATCH_ROWS,
            'initial_continuation': self.continuation,
            'logical_schema': None if self.schema is None else _serialize_schema(self.schema),
            'chunks': list(self.chunks), 'rows': self.rows, 'row_groups': self.groups,
            'value_hash_version': VALUE_HASH_VERSION,
            'source_identity': identity, 'source_identity_sha256': digest(identity),
            'implementation': implementation_identity()}

    def finish(self, source_manifest):
        if self.closed or self.failed:
            raise IntegrityError('failed or completed quote replay series cannot publish again')
        started = time.process_time()
        charged_write = False
        try:
            payload = self._descriptor_payload(source_manifest)
            reference = self.outputs.json(f'{self.name}-replay-descriptor.json', payload,
                                          kind='auction_flow_quote_replay_descriptor')
            stored = read_json_artifact(reference)
            if digest(stored) != digest(payload):
                raise IntegrityError('retained quote replay descriptor changed before verification')
            self.cpu_seconds += time.process_time() - started
            charged_write = True
            replay_started = time.process_time()
            accounting = {}
            compared = _verify_quote_replay_descriptor(stored, accounting=accounting)
            replay_cpu = time.process_time() - replay_started
            self.compared_values = compared
            self.closed = True
            return {'version': VERSION, 'series': self.name, 'rows': self.rows, 'row_groups': self.groups,
                'encoding': ENCODING, 'schema': None if self.schema is None else str(self.schema),
                'files': [], 'compared_values': compared, 'roundtrip_exact': True,
                'cpu_seconds': self.cpu_seconds, 'serialized_bytes': reference['size_bytes'],
                'replay_descriptor': reference, 'quote_replay_validation_cpu_seconds': replay_cpu,
                'quote_replay_metadata_cpu_seconds': accounting['metadata_cpu_seconds']}
        except BaseException:
            if not charged_write:
                self.cpu_seconds += time.process_time() - started
            self.abort()
            raise
