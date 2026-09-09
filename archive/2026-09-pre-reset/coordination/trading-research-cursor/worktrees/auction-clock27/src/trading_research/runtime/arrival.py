"""F12 bounded offline raw arrival journal and deterministic adapter replay.

No network, worker thread, broker send or clock acquisition is implemented here.
Supplied actual-capture labels are provenance claims, not collection certification.
Kernel adapters below execute only pure transitions on detached in-memory state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import tempfile
from typing import Callable

from trading_research.errors import ContractError, IntegrityError

SCHEMA = 'ArrivalTrace.v1'
DEFINITION = 'F12.ARRIVAL_TRACE.v1'
MAX_RECORDS = 4096
MAX_RAW_BYTES = 1024 * 1024
MAX_JOURNAL_BYTES = 64 * 1024 * 1024
MAX_CHECKPOINT_BYTES = 16 * 1024 * 1024
MAX_CALLBACKS = 64
MAX_FRAME_BYTES = 2 * MAX_RAW_BYTES + 65536
KINDS = frozenset({'source', 'timer', 'completion', 'decision', 'order_ack',
                   'connection', 'subscription', 'gap', 'cursor', 'clock_adjust', 'boot'})
PROVENANCES = frozenset({'actual_capture', 'modeled_scenario', 'synthetic_fixture'})
MAGIC = b'F12TRACE1\n'
FRAME_HEADER = struct.Struct('>4sQQ32s')
EMPTY_PREFIX = hashlib.sha256(b'F12.ARRIVAL_TRACE.v1:empty').hexdigest()


def _utf8(value):
    try:
        return value.encode('utf-8')
    except UnicodeError as exc:
        raise ContractError('invalid Unicode string') from exc


def _name(value, name='identity'):
    if type(value) is not str or not value or len(_utf8(value)) > 4096:
        raise ContractError(f'{name} must be a bounded nonempty string')
    return value


def _integer(value, name, *, nonnegative=False):
    if type(value) is not int or not -(2**63) <= value < 2**63 or (nonnegative and value < 0):
        raise ContractError(f'{name} requires an exact {"nonnegative " if nonnegative else ""}int64')
    return value


def _hash_text(value):
    if type(value) is not str or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise ContractError('lowercase SHA256 required')
    return value


def _json_value(value, depth=0):
    if depth > 32:
        raise ContractError('JSON nesting bound exceeded')
    if type(value) is dict:
        if len(value) > MAX_RECORDS or any(type(k) is not str for k in value):
            raise ContractError('JSON object requires bounded string keys')
        for k, v in value.items():
            if len(_utf8(k)) > 4096:
                raise ContractError('JSON key bound exceeded')
            _json_value(v, depth + 1)
    elif type(value) is list:
        if len(value) > MAX_RECORDS:
            raise ContractError('JSON array bound exceeded')
        for v in value:
            _json_value(v, depth + 1)
    elif type(value) is float:
        if not math.isfinite(value):
            raise ContractError('nonfinite JSON value')
    elif type(value) is int:
        _integer(value, 'JSON integer')
    elif type(value) is str:
        if len(_utf8(value)) > MAX_FRAME_BYTES:
            raise ContractError('JSON string bound exceeded')
    elif value is not None and type(value) is not bool:
        raise ContractError('only detached JSON values are accepted')


def canonical(value, *, max_bytes=MAX_CHECKPOINT_BYTES):
    _json_value(value)
    try:
        raw = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                         allow_nan=False).encode('utf-8')
    except (ValueError, TypeError, UnicodeError) as exc:
        raise ContractError('invalid canonical JSON') from exc
    if len(raw) > max_bytes:
        raise ContractError('canonical JSON byte bound exceeded')
    return raw


def _pairs(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise IntegrityError('duplicate JSON object key')
        result[k] = v
    return result


def parse_json(raw, *, max_bytes=MAX_CHECKPOINT_BYTES):
    if type(raw) is not bytes or len(raw) > max_bytes:
        raise ContractError('bounded exact JSON bytes required')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise IntegrityError('malformed JSON bytes') from exc
    _json_value(value)
    return value


def _copy(value):
    return parse_json(canonical(value))


def content_hash(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def prefix_hash(previous, record):
    _hash_text(previous)
    return hashlib.sha256(bytes.fromhex(previous) + record.canonical_bytes).hexdigest()


def _required(payload, names):
    if type(payload) is not dict:
        raise ContractError('payload body must be an object')
    if not set(names).issubset(payload):
        raise ContractError('record payload is missing required fields: ' + ','.join(sorted(set(names) - set(payload))))


def _names(payload, names):
    for key in names:
        _name(payload[key], key)


def _name_list(value, name):
    if type(value) is not list or any(type(v) is not str for v in value) or len(set(value)) != len(value):
        raise ContractError(f'{name} requires a list of unique identities')
    for v in value:
        _name(v, name)


@dataclass(frozen=True, init=False)
class ArrivalRecord:
    schema_version: int
    trace_id: str
    arrival_ordinal: int
    delivery_id: str
    kind: str
    boot_id: str
    receipt_utc_ns: int
    receipt_monotonic_ns: int
    provenance: str
    source_event_utc_ns: int | None
    provider_published_utc_ns: int | None
    _payload_json: bytes = field(repr=False)

    def __init__(self, *, trace_id, arrival_ordinal, delivery_id, kind, boot_id,
                 receipt_utc_ns, receipt_monotonic_ns, provenance, payload,
                 source_event_utc_ns=None, provider_published_utc_ns=None, schema_version=1):
        if type(schema_version) is not int or schema_version != 1:
            raise ContractError('unknown arrival schema version')
        for name, value in [('trace_id', trace_id), ('delivery_id', delivery_id), ('boot_id', boot_id)]:
            _name(value, name)
        _integer(arrival_ordinal, 'arrival ordinal', nonnegative=True)
        _integer(receipt_utc_ns, 'receipt UTC')
        _integer(receipt_monotonic_ns, 'receipt monotonic', nonnegative=True)
        for value in (source_event_utc_ns, provider_published_utc_ns):
            if value is not None:
                _integer(value, 'source/provider UTC')
        if type(kind) is not str or kind not in KINDS or type(provenance) is not str or provenance not in PROVENANCES:
            raise ContractError('unknown arrival kind or provenance')
        if type(payload) is not dict:
            raise ContractError('record payload must be an object')
        raw = canonical(payload, max_bytes=MAX_FRAME_BYTES)
        p = parse_json(raw)
        if kind == 'source':
            _required(p, ('source_id', 'instrument', 'definition', 'stream_generation', 'economic_id',
                          'semantic_kind', 'raw_hex', 'raw_sha256', 'decoder_id'))
            _names(p, ('source_id', 'instrument', 'definition', 'stream_generation', 'decoder_id'))
            if p['economic_id'] is not None:
                _name(p['economic_id'], 'economic ID')
            if p['semantic_kind'] not in ('snapshot', 'trade', 'other'):
                raise ContractError('unknown source semantic kind')
            if type(p['raw_hex']) is not str or len(p['raw_hex']) > 2 * MAX_RAW_BYTES:
                raise ContractError('bounded exact raw hex required')
            try:
                source_raw = bytes.fromhex(p['raw_hex'])
            except ValueError as exc:
                raise ContractError('invalid raw hex') from exc
            if source_raw.hex() != p['raw_hex'] or hashlib.sha256(source_raw).hexdigest() != _hash_text(p['raw_sha256']):
                raise IntegrityError('raw SHA or canonical hex mismatch')
            if p.get('provider_sequence') is not None:
                _integer(p['provider_sequence'], 'provider sequence', nonnegative=True)
            if p.get('provider_cursor') is not None:
                _name(p['provider_cursor'], 'provider cursor')
        elif kind == 'timer':
            _required(p, ('timer_id', 'callback_id', 'due_boot_id', 'due_monotonic_ns'))
            _names(p, ('timer_id', 'callback_id', 'due_boot_id'))
            _integer(p['due_monotonic_ns'], 'timer due monotonic', nonnegative=True)
            if p['due_boot_id'] != boot_id or p['due_monotonic_ns'] > receipt_monotonic_ns:
                raise ContractError('timer firing needs a due time in the same boot')
            if p.get('due_utc_ns') is not None:
                _integer(p['due_utc_ns'], 'diagnostic due UTC')
        elif kind == 'completion':
            _required(p, ('job_id', 'callback_id', 'input_version_ids', 'start_boot_id', 'start_monotonic_ns', 'result'))
            _names(p, ('job_id', 'callback_id', 'start_boot_id'))
            _name_list(p['input_version_ids'], 'frozen input versions')
            _integer(p['start_monotonic_ns'], 'computation start monotonic', nonnegative=True)
            if p['start_boot_id'] == boot_id and p['start_monotonic_ns'] > receipt_monotonic_ns:
                raise ContractError('completion precedes same-boot computation start')
        elif kind == 'decision':
            _required(p, ('decision_id', 'callback_id', 'served_version_ids', 'action'))
            _names(p, ('decision_id', 'callback_id'))
            _name_list(p['served_version_ids'], 'served versions')
        elif kind == 'order_ack':
            _required(p, ('order_id', 'ack_id', 'state_version', 'economic_known_at', 'simulated_boundary'))
            _names(p, ('order_id', 'ack_id'))
            _integer(p['state_version'], 'order state version', nonnegative=True)
            _integer(p['economic_known_at'], 'order economic known UTC')
            if p['simulated_boundary'] is not True:
                raise ContractError('only supplied simulated order boundaries are implemented')
        elif kind == 'connection':
            _required(p, ('source_id', 'generation', 'status', 'reason'))
            _names(p, ('source_id', 'generation', 'reason'))
            if p['status'] not in ('connected', 'disconnected', 'denied'):
                raise ContractError('unknown connection status')
        elif kind == 'subscription':
            _required(p, ('source_id', 'subscription_id', 'generation', 'operation', 'instruments'))
            _names(p, ('source_id', 'subscription_id', 'generation'))
            _name_list(p['instruments'], 'subscription instrument scope')
            if not p['instruments'] or p['operation'] not in ('subscribe', 'unsubscribe', 'denied'):
                raise ContractError('invalid subscription change')
        elif kind == 'gap':
            _required(p, ('source_id', 'generation', 'gap_id', 'status', 'reason'))
            _names(p, ('source_id', 'generation', 'gap_id', 'reason'))
            if p['status'] not in ('open', 'closed'):
                raise ContractError('invalid gap marker')
            if p.get('expected_count') is not None:
                _integer(p['expected_count'], 'expected count', nonnegative=True)
                _name(p.get('evidence_id'), 'expected-population evidence')
        elif kind == 'cursor':
            _required(p, ('source_id', 'generation', 'cursor'))
            _names(p, ('source_id', 'generation', 'cursor'))
        elif kind == 'clock_adjust':
            _required(p, ('old_utc_ns', 'new_utc_ns', 'old_monotonic_ns', 'new_monotonic_ns', 'evidence_id'))
            _name(p['evidence_id'])
            for key in ('old_utc_ns', 'new_utc_ns'):
                _integer(p[key], key)
            for key in ('old_monotonic_ns', 'new_monotonic_ns'):
                _integer(p[key], key, nonnegative=True)
            if (p['new_utc_ns'] != receipt_utc_ns or p['new_monotonic_ns'] != receipt_monotonic_ns
                    or p['old_monotonic_ns'] > p['new_monotonic_ns']):
                raise ContractError('clock adjustment is not paired with this receipt')
        else:
            _required(p, ('previous_boot_id', 'new_boot_id'))
            _name(p['new_boot_id'])
            if p['previous_boot_id'] is not None:
                _name(p['previous_boot_id'])
            if p['new_boot_id'] != boot_id:
                raise ContractError('boot marker/envelope mismatch')
        for key, value in [('schema_version', schema_version), ('trace_id', trace_id),
                           ('arrival_ordinal', arrival_ordinal), ('delivery_id', delivery_id),
                           ('kind', kind), ('boot_id', boot_id), ('receipt_utc_ns', receipt_utc_ns),
                           ('receipt_monotonic_ns', receipt_monotonic_ns), ('provenance', provenance),
                           ('source_event_utc_ns', source_event_utc_ns),
                           ('provider_published_utc_ns', provider_published_utc_ns), ('_payload_json', raw)]:
            object.__setattr__(self, key, value)
        if len(self.canonical_bytes) > MAX_FRAME_BYTES:
            raise ContractError('arrival envelope exceeds frame bound')

    @property
    def payload(self):
        return parse_json(self._payload_json)

    @property
    def raw_bytes(self):
        if self.kind != 'source':
            raise ContractError('only source arrivals have undecoded raw bytes')
        return bytes.fromhex(self.payload['raw_hex'])

    def record(self):
        return {name: getattr(self, name) for name in (
            'schema_version', 'trace_id', 'arrival_ordinal', 'delivery_id', 'kind', 'boot_id',
            'receipt_utc_ns', 'receipt_monotonic_ns', 'provenance', 'source_event_utc_ns',
            'provider_published_utc_ns')} | {'payload': self.payload}

    @property
    def canonical_bytes(self):
        return canonical(self.record(), max_bytes=MAX_FRAME_BYTES)

    @property
    def sha256(self):
        return hashlib.sha256(self.canonical_bytes).hexdigest()

    @classmethod
    def from_record(cls, record):
        if type(record) is not dict:
            raise ContractError('arrival record must be an object')
        required = {'schema_version', 'trace_id', 'arrival_ordinal', 'delivery_id', 'kind', 'boot_id',
                    'receipt_utc_ns', 'receipt_monotonic_ns', 'provenance', 'payload'}
        if not required.issubset(record) or set(record) - required - {'source_event_utc_ns', 'provider_published_utc_ns'}:
            raise ContractError('arrival envelope fields disagree with schema')
        return cls(**record)


def _initial_control():
    return {'boots': {}, 'active_boot': None, 'sources': {}, 'subscriptions': {},
            'gaps': {}, 'cursors': {}, 'clock_diagnostics': [], 'source_epochs': {}, 'subscription_epochs': {}}


def _control_after(control, record):
    """No decoding: validate transport envelopes and retain control evidence."""
    out = _copy(control)
    p, kind, at = record.payload, record.kind, record.arrival_ordinal
    boot = out['boots'].get(record.boot_id)
    if boot is not None and record.receipt_monotonic_ns < boot['monotonic_ns']:
        raise ContractError('same-boot receipt monotonic clock regressed')
    if out['active_boot'] is not None and out['active_boot'] != record.boot_id:
        if kind != 'boot' or p['previous_boot_id'] != out['active_boot'] or boot is not None:
            raise ContractError('boot transition requires a new explicit boot epoch')
    if kind == 'boot' and (p['previous_boot_id'] != out['active_boot'] or boot is not None):
        raise ContractError('boot marker does not match the preceding epoch')
    if kind == 'clock_adjust':
        if boot is None or p['old_utc_ns'] != boot['utc_ns'] or p['old_monotonic_ns'] != boot['monotonic_ns']:
            raise ContractError('clock adjustment lacks matching preceding clock evidence')
        out['clock_diagnostics'].append({'kind': 'clock_adjust', 'ordinal': at, 'boot_id': record.boot_id,
                                        'utc_step_ns': p['new_utc_ns'] - p['old_utc_ns'],
                                        'monotonic_elapsed_ns': p['new_monotonic_ns'] - p['old_monotonic_ns'],
                                        'evidence_id': p['evidence_id']})
    elif boot is not None and record.receipt_utc_ns < boot['utc_ns']:
        out['clock_diagnostics'].append({'kind': 'utc_regression_without_marker', 'ordinal': at,
                                        'boot_id': record.boot_id, 'utc_step_ns': record.receipt_utc_ns - boot['utc_ns']})
    out['boots'][record.boot_id] = {'monotonic_ns': record.receipt_monotonic_ns,
                                    'utc_ns': record.receipt_utc_ns, 'last_ordinal': at}
    out['active_boot'] = record.boot_id
    if kind == 'connection':
        old = out['sources'].get(p['source_id'])
        epochs = out['source_epochs'].setdefault(p['source_id'], [])
        if old and p['generation'] != old['generation'] and p['generation'] in epochs:
            raise ContractError('stream generation cannot be reused')
        if p['generation'] not in epochs:
            epochs.append(p['generation'])
        if old and p['status'] == 'connected' and old['status'] != 'connected' and p['generation'] == old['generation']:
            raise ContractError('reconnect requires a new stream generation')
        if old and p['generation'] != old['generation'] and p['status'] != 'connected':
            raise ContractError('generation change needs a connected marker')
        same = old is not None and p['generation'] == old['generation']
        out['sources'][p['source_id']] = {'generation': p['generation'], 'status': p['status'],
            'last_sequence': old['last_sequence'] if same else None, 'last_ordinal': at,
            'reason': p['reason'], 'connection_evidence': record.delivery_id,
            'gap_started_ordinal': (old['gap_started_ordinal'] if same and old['gap_started_ordinal'] is not None else at) if p['status'] != 'connected' else None}
    elif kind == 'source':
        source = out['sources'].get(p['source_id'])
        if source is None:
            out['source_epochs'][p['source_id']] = [p['stream_generation']]
            source = {'generation': p['stream_generation'], 'status': 'connected', 'last_sequence': None,
                      'last_ordinal': at, 'reason': 'implicit_initial_generation',
                      'connection_evidence': record.delivery_id, 'gap_started_ordinal': None}
        if source['generation'] != p['stream_generation'] or source['status'] != 'connected':
            raise ContractError('source delivery lacks an active matching stream generation')
        seq = p.get('provider_sequence')
        if seq is not None and source['last_sequence'] is not None and seq < source['last_sequence']:
            raise ContractError('sequence regression requires an explicit new generation')
        source['last_sequence'] = source['last_sequence'] if seq is None else seq
        source['last_ordinal'] = at
        out['sources'][p['source_id']] = source
        if p.get('provider_cursor') is not None:
            out['cursors'][p['source_id']] = {'generation': p['stream_generation'], 'cursor': p['provider_cursor'], 'ordinal': at}
    elif kind == 'subscription':
        key = content_hash([p['source_id'], p['subscription_id']])
        old = out['subscriptions'].get(key)
        epochs = out['subscription_epochs'].setdefault(key, [])
        if old and p['generation'] != old['generation'] and p['generation'] in epochs:
            raise ContractError('subscription generation cannot be reused')
        if p['generation'] not in epochs:
            epochs.append(p['generation'])
        if old and p['operation'] == 'subscribe' and old['operation'] != 'subscribe' and old['generation'] == p['generation']:
            raise ContractError('subscription restart requires a new generation')
        out['subscriptions'][key] = {**p, 'ordinal': at, 'delivery_id': record.delivery_id,
                                    'ended_ordinal': at if p['operation'] == 'unsubscribe' else None}
    elif kind == 'gap':
        old = out['gaps'].get(p['gap_id'])
        if p['status'] == 'closed' and (old is None or old['status'] != 'open'
                or (old['source_id'], old['generation']) != (p['source_id'], p['generation'])):
            raise ContractError('gap close lacks a matching open incident')
        if old is not None and p['status'] == 'open':
            raise IntegrityError('gap ID cannot be reopened or silently replaced')
        out['gaps'][p['gap_id']] = {**p, 'open_evidence': record.record() if old is None else old['open_evidence'],
            'close_evidence': record.record() if p['status'] == 'closed' else None, 'opened_ordinal': old['opened_ordinal'] if old else at,
                                  'closed_ordinal': at if p['status'] == 'closed' else None,
                                  'delivery_id': record.delivery_id}
    elif kind == 'cursor':
        source = out['sources'].get(p['source_id'])
        if source is None or source['generation'] != p['generation']:
            raise ContractError('cursor lacks a matching source generation')
        out['cursors'][p['source_id']] = {**p, 'ordinal': at}
    return out


def _journal_clock_after(control, record):
    out = _copy(control)
    old = out.get(record.boot_id)
    if old is not None and record.receipt_monotonic_ns < old:
        raise ContractError('same-boot raw receipt monotonic clock regressed')
    out[record.boot_id] = record.receipt_monotonic_ns
    return out


_DURABLE_TOKEN = object()


@dataclass(frozen=True)
class CommittedArrival:
    record: ArrivalRecord
    prefix_sha256: str
    storage_boundary: str
    archive_id: str
    _durable_token: object = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        if not isinstance(self.record, ArrivalRecord):
            raise ContractError('typed committed arrival required')
        _hash_text(self.prefix_sha256); _name(self.archive_id)
        if self.storage_boundary not in ('synthetic_fixture', 'durable_local_journal'):
            raise ContractError('unknown retained input boundary')
        if self.storage_boundary == 'durable_local_journal' and self._durable_token != (_DURABLE_TOKEN, self.record.sha256, self.prefix_sha256, self.archive_id):
            raise ContractError('durable proof must be issued by the local journal; not a security sandbox')


def fixture_trace(records):
    """Finite supplied scenarios, not a substitute for committing actual receipts."""
    if type(records) is not tuple or len(records) > MAX_RECORDS:
        raise ContractError('bounded immutable fixture trace required')
    prefix, result = EMPTY_PREFIX, []
    for record in records:
        if not isinstance(record, ArrivalRecord) or record.provenance == 'actual_capture':
            raise ContractError('actual capture requires the durable journal boundary')
        prefix = prefix_hash(prefix, record)
        result.append(CommittedArrival(record, prefix, 'synthetic_fixture', 'fixture:' + record.trace_id))
    return tuple(result)


class UncertainCommit(IntegrityError):
    """No decoder ran; reopen and inspect before retrying an uncertain write."""


class DecodeAfterCommit(ContractError):
    def __init__(self, committed, cause):
        super().__init__('decoder failed after durable raw commit: ' + committed.record.delivery_id)
        self.committed, self.cause = committed, cause


class JournalCorruption(IntegrityError):
    def __init__(self, message, *, offset, frame_index):
        super().__init__(message)
        self.offset, self.frame_index = offset, frame_index


class TornTail(IntegrityError):
    def __init__(self, inspection):
        super().__init__('torn final frame requires explicit quarantine recovery')
        self.inspection = inspection


@dataclass(frozen=True)
class JournalInspection:
    records: tuple[ArrivalRecord, ...]
    verified_end: int
    tail: bytes
    source_sha256: str

    @property
    def tail_classification(self):
        return 'torn_final_frame' if self.tail else 'complete'


def frame_bytes(record):
    if not isinstance(record, ArrivalRecord):
        raise ContractError('typed arrival frame required')
    raw = record.canonical_bytes
    return FRAME_HEADER.pack(b'ARV1', len(raw), len(raw) ^ ((1 << 64) - 1), hashlib.sha256(raw).digest()) + raw


def _inspect_bytes(raw):
    if len(raw) > MAX_JOURNAL_BYTES or not raw.startswith(MAGIC):
        raise JournalCorruption('journal size or magic mismatch', offset=0, frame_index=0)
    offset, records, seen, control, trace_id = len(MAGIC), [], {}, {}, None
    while offset < len(raw):
        start = offset
        if len(raw) - offset < FRAME_HEADER.size:
            return JournalInspection(tuple(records), start, raw[start:], hashlib.sha256(raw).hexdigest())
        marker, length, complement, expected = FRAME_HEADER.unpack(raw[offset:offset + FRAME_HEADER.size])
        if marker != b'ARV1' or complement != length ^ ((1 << 64) - 1) or not 0 < length <= MAX_FRAME_BYTES:
            raise JournalCorruption('frame header corruption', offset=start, frame_index=len(records) + 1)
        offset += FRAME_HEADER.size
        if len(raw) - offset < length:
            return JournalInspection(tuple(records), start, raw[start:], hashlib.sha256(raw).hexdigest())
        payload = raw[offset:offset + length]
        if hashlib.sha256(payload).digest() != expected:
            raise JournalCorruption('frame checksum corruption', offset=start, frame_index=len(records) + 1)
        try:
            record = ArrivalRecord.from_record(parse_json(payload, max_bytes=MAX_FRAME_BYTES))
            if record.canonical_bytes != payload:
                raise IntegrityError('frame is not canonical JSON')
            if len(records) >= MAX_RECORDS or record.delivery_id in seen:
                raise IntegrityError('journal count or duplicate delivery conflict')
            if records and record.arrival_ordinal <= records[-1].arrival_ordinal:
                raise IntegrityError('journal arrival ordinal regressed')
            if trace_id is not None and trace_id != record.trace_id:
                raise IntegrityError('journal mixed trace identities')
            control = _journal_clock_after(control, record)
        except (ContractError, IntegrityError, KeyError, TypeError, ValueError) as exc:
            raise JournalCorruption('invalid retained arrival: ' + str(exc), offset=start, frame_index=len(records) + 1) from exc
        trace_id = record.trace_id
        seen[record.delivery_id] = record.sha256
        records.append(record)
        offset += length
    return JournalInspection(tuple(records), offset, b'', hashlib.sha256(raw).hexdigest())


def _lock(file, exclusive):
    if os.name != 'posix':
        raise ContractError('F12 local journal requires declared POSIX flock/fsync support')
    import fcntl
    try:
        fcntl.flock(file.fileno(), (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        raise ContractError('arrival journal already has an incompatible writer/reader lock') from exc


def inspect_journal(path):
    with open(path, 'rb') as file:
        _lock(file, False)
        raw = file.read(MAX_JOURNAL_BYTES + 1)
        return _inspect_bytes(raw)


def _notify(hook, operation):
    if hook is not None:
        hook(operation)


def _write_all(file, raw):
    view = memoryview(raw)
    while view:
        written = file.write(view)
        if not written:
            raise OSError('short journal write made no progress')
        view = view[written:]


def _sync_dir(path, hook=None):
    _notify(hook, 'fsync_directory')
    fd = os.open(str(path), os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write(path, raw, *, hook=None, max_bytes=MAX_CHECKPOINT_BYTES):
    path = Path(path)
    if type(raw) is not bytes or len(raw) > max_bytes or not path.parent.is_dir():
        raise ContractError('bounded atomic artifact and existing parent directory required')
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb', buffering=0) as file:
            _notify(hook, 'write_all'); _write_all(file, raw)
            _notify(hook, 'flush'); file.flush()
            _notify(hook, 'fsync'); os.fsync(file.fileno())
        _notify(hook, 'replace'); os.replace(temporary, path)
        _sync_dir(path.parent, hook)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class RawArrivalJournal:
    """Single-writer local durable append. Failed I/O poisons this open handle."""
    def __init__(self, path, *, hook=None):
        self._path, self.hook = Path(path).resolve(), hook
        self.stats = {'write_attempts': 0, 'committed_appends': 0, 'written_bytes': 0, 'attempted_write_bytes': 0, 'flush_calls': 0, 'fsync_calls': 0, 'decode_attempts': 0}
        if not self.path.parent.is_dir():
            raise ContractError('journal parent must already exist')
        self._file = None
        self._poisoned = False
        self._records, self._seen, self._prefix = [], {}, EMPTY_PREFIX
        self._control = {}
        try:
            fd = os.open(self.path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
            created = True
        except FileExistsError:
            fd = os.open(self.path, os.O_RDWR)
            created = False
        file = os.fdopen(fd, 'r+b', buffering=0)
        try:
            _lock(file, True)
            if created:
                _notify(hook, 'write_all'); _write_all(file, MAGIC)
                _notify(hook, 'flush'); file.flush()
                _notify(hook, 'fsync'); os.fsync(file.fileno())
                _sync_dir(self.path.parent, hook)
            file.seek(0)
            inspection = _inspect_bytes(file.read(MAX_JOURNAL_BYTES + 1))
            if inspection.tail:
                raise TornTail(inspection)
            # Reopening a complete frame after uncertain fsync establishes local
            # durability now; it does not invent a historical persistence time.
            _notify(hook, 'flush'); file.flush()
            _notify(hook, 'fsync'); os.fsync(file.fileno())
            for record in inspection.records:
                self._install(record)
            self._file = file
            file.seek(0, os.SEEK_END)
        except BaseException:
            file.close()
            raise

    @property
    def path(self):
        return self._path

    def _install(self, record):
        self._prefix = prefix_hash(self._prefix, record)
        self._records.append(record)
        self._seen[record.delivery_id] = record
        self._control = _journal_clock_after(self._control, record)

    @property
    def records(self):
        return tuple(self._records)

    @property
    def committed(self):
        prefix, result = EMPTY_PREFIX, []
        for record in self._records:
            prefix = prefix_hash(prefix, record)
            result.append(CommittedArrival(record, prefix, 'durable_local_journal', str(self.path.resolve()), (_DURABLE_TOKEN, record.sha256, prefix, str(self.path.resolve()))))
        return tuple(result)

    def append(self, record):
        if self._file is None or self._poisoned:
            raise UncertainCommit('closed or uncertain journal requires reopening')
        if not isinstance(record, ArrivalRecord):
            raise ContractError('typed raw arrival required')
        old = self._seen.get(record.delivery_id)
        if old is not None:
            if old != record:
                raise IntegrityError('delivery ID reused with different content')
            return next(c for c in self.committed if c.record.delivery_id == record.delivery_id), False
        if len(self._records) >= MAX_RECORDS:
            raise ContractError('arrival record capacity exhausted without eviction')
        if self._records and (record.arrival_ordinal <= self._records[-1].arrival_ordinal
                              or record.trace_id != self._records[0].trace_id):
            raise ContractError('arrival order or trace identity changed')
        proposed_control = _journal_clock_after(self._control, record)
        raw = frame_bytes(record)
        self._file.seek(0, os.SEEK_END)
        if self._file.tell() + len(raw) > MAX_JOURNAL_BYTES:
            raise ContractError('journal byte bound exceeded without eviction')
        try:
            self.stats['write_attempts'] += 1
            self.stats['attempted_write_bytes'] += len(raw)
            _notify(self.hook, 'write_all'); _write_all(self._file, raw)
            self.stats['written_bytes'] += len(raw)
            self.stats['flush_calls'] += 1
            _notify(self.hook, 'flush'); self._file.flush()
            self.stats['fsync_calls'] += 1
            _notify(self.hook, 'fsync'); os.fsync(self._file.fileno())
        except BaseException as exc:
            self._poisoned = True
            raise UncertainCommit('raw write may be partial or durable; no decoder dispatched') from exc
        self._prefix = prefix_hash(self._prefix, record)
        self._records.append(record); self._seen[record.delivery_id] = record
        self._control = proposed_control
        self.stats['committed_appends'] += 1
        return CommittedArrival(record, self._prefix, 'durable_local_journal', str(self.path.resolve()), (_DURABLE_TOKEN, record.sha256, self._prefix, str(self.path.resolve()))), True

    def append_and_decode(self, record, decoder):
        if not isinstance(record, ArrivalRecord) or record.kind != 'source' or not callable(decoder):
            raise ContractError('source record and explicit decoder required')
        committed, created = self.append(record)
        try:
            self.stats['decode_attempts'] += 1
            _notify(self.hook, 'decode')
            value = decoder(record.raw_bytes)
        except Exception as exc:
            raise DecodeAfterCommit(committed, exc) from exc
        return committed, created, value

    def close(self):
        if self._file is not None:
            self._file.close()
            self._file = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def quarantine_torn_tail(source, destination):
    """Hold the original read lock and exclusively create all recovery artifacts."""
    source, destination = Path(source), Path(destination)
    evidence_path = destination.with_name(destination.name + '.quarantine.json')
    tail_path = destination.with_name(destination.name + '.tail.bin')
    if source.resolve() == destination.resolve():
        raise ContractError('recovery requires a distinct new archive')
    with source.open('rb') as original:
        _lock(original, False)
        raw = original.read(MAX_JOURNAL_BYTES + 1)
        inspection = _inspect_bytes(raw)
        if not inspection.tail:
            raise ContractError('recovery requires a classified torn tail')
        evidence = {'schema': SCHEMA, 'source_path': str(source.resolve()),
            'source_sha256': inspection.source_sha256, 'verified_end': inspection.verified_end,
            'verified_prefix_records': len(inspection.records), 'tail_path': str(tail_path),
            'tail_bytes': len(inspection.tail), 'tail_sha256': hashlib.sha256(inspection.tail).hexdigest(),
            'tail_classification': 'torn_final_frame', 'original_mutated': False,
            'simulated_boundary': True, 'actual_live_evidence': False}
        # Existing artifacts are never overwritten. A partial recovery remains
        # explicit evidence and requires a fresh destination on retry.
        for path, payload in ((tail_path, inspection.tail), (evidence_path, canonical(evidence)),
                              (destination, raw[:inspection.verified_end])):
            try:
                with path.open('xb', buffering=0) as file:
                    _write_all(file, payload); file.flush(); os.fsync(file.fileno())
            except FileExistsError as exc:
                raise ContractError('recovery destination already exists') from exc
        _sync_dir(destination.parent)
    return evidence | {'evidence_path': str(evidence_path), 'new_archive': str(destination)}


@dataclass(frozen=True, init=False)
class CallbackSpec:
    id: str
    version_hash: str
    accepted_kinds: frozenset[str]
    state_schema: str
    _initial_json: bytes = field(repr=False)
    transition: Callable = field(repr=False, compare=False)
    semantic_projection: Callable = field(repr=False, compare=False)
    projection_id: str

    def __init__(self, id, version_hash, accepted_kinds, state_schema, initial_state,
                 transition, *, semantic_projection=None, projection_id='identity'):
        _name(id); _hash_text(version_hash); _name(state_schema); _name(projection_id)
        if (type(accepted_kinds) is not frozenset or not accepted_kinds or not accepted_kinds.issubset(KINDS)
                or type(initial_state) is not dict or not callable(transition)
                or semantic_projection is not None and not callable(semantic_projection)):
            raise ContractError('callback registry needs immutable kinds, JSON state and explicit pure functions')
        if semantic_projection is not None and projection_id == 'identity':
            raise ContractError('custom semantic projection requires its own version identity')
        for key, value in [('id', id), ('version_hash', version_hash), ('accepted_kinds', accepted_kinds),
                           ('state_schema', state_schema), ('_initial_json', canonical(initial_state)),
                           ('transition', transition), ('semantic_projection', semantic_projection),
                           ('projection_id', projection_id)]:
            object.__setattr__(self, key, value)

    @property
    def initial_state(self):
        return parse_json(self._initial_json)

    def validate_state(self, state):
        if type(state) is not dict or set(state) != set(self.initial_state):
            raise ContractError('callback state violates registered top-level field schema')
        for key, initial in self.initial_state.items():
            if initial is not None and type(state[key]) is not type(initial):
                raise ContractError('callback state field changed its registered JSON type')
        canonical(state)

    def semantic(self, state):
        value = _copy(state) if self.semantic_projection is None else self.semantic_projection(_copy(state))
        canonical(value)
        return value

    def declaration(self):
        return {'id': self.id, 'version_hash': self.version_hash, 'accepted_kinds': sorted(self.accepted_kinds),
                'state_schema': self.state_schema, 'initial_sha256': hashlib.sha256(self._initial_json).hexdigest(),
                'projection_id': self.projection_id}


def _registry(specs):
    if type(specs) is not tuple or len(specs) > MAX_CALLBACKS or any(not isinstance(s, CallbackSpec) for s in specs):
        raise ContractError('bounded immutable callback registry required')
    if len({s.id for s in specs}) != len(specs):
        raise ContractError('callback IDs must be unique')
    return tuple(sorted(specs, key=lambda s: s.id))


def _output_sections(outputs):
    if type(outputs) is not list:
        raise ContractError('callback output must be an explicit JSON list')
    result = {'semantic': [], 'timing': [], 'transport': []}
    for output in outputs:
        if type(output) is not dict or set(output) - {'semantic', 'timing', 'transport'} or 'semantic' not in output:
            raise ContractError('observable output needs explicit semantic/timing/transport sections')
        for kind in result:
            if kind in output:
                result[kind].append(_copy(output[kind]))
    return result


def _record_semantic(record):
    p = record.payload
    if record.kind == 'source':
        return {'kind': 'source', **{k: p[k] for k in ('source_id', 'instrument', 'definition', 'semantic_kind')}}
    if record.kind == 'decision':
        return {'kind': 'decision', **{k: p[k] for k in ('decision_id', 'action', 'served_version_ids')}}
    if record.kind in {'connection', 'subscription', 'gap', 'cursor', 'boot', 'clock_adjust'}:
        return {'kind': record.kind, 'control': p}
    return {'kind': record.kind}


def _observation(record, specs, states, callback_outputs, *, definition, policy):
    sections = {'semantic': {}, 'timing': {}, 'transport': {}}
    for id, outputs in callback_outputs.items():
        parts = _output_sections(outputs)
        for kind in sections:
            if parts[kind]:
                sections[kind][id] = parts[kind]
    semantic = {'record': _record_semantic(record), 'states': {s.id: s.semantic(states[s.id]) for s in specs}, 'outputs': sections['semantic']}
    timing = {'boot_id': record.boot_id, 'receipt_utc_ns': record.receipt_utc_ns,
              'receipt_monotonic_ns': record.receipt_monotonic_ns,
              'source_event_utc_ns': record.source_event_utc_ns,
              'provider_published_utc_ns': record.provider_published_utc_ns, 'outputs': sections['timing']}
    return {'arrival_ordinal': record.arrival_ordinal, 'delivery_id': record.delivery_id, 'kind': record.kind,
            'semantic': semantic, 'semantic_sha256': content_hash({'definition': definition, 'policy': policy,
                'callbacks': [s.declaration() for s in specs], 'semantic': semantic}),
            'timing': timing, 'transport': {'record_sha256': record.sha256, 'provenance': record.provenance,
                                          'outputs': sections['transport']},
            'simulated_boundary': True, 'actual_live_evidence': False}


class ArrivalReplay:
    """Atomic offline callback fold; no decoder runs on an uncommitted actual receipt."""
    def __setattr__(self, name, value):
        if name in {'callbacks', 'trace_id', 'definition', 'policy_version'} and hasattr(self, name):
            raise ContractError('replay configuration is immutable')
        object.__setattr__(self, name, value)

    def __init__(self, callbacks, *, trace_id, definition=DEFINITION, policy_version='frozen-offline-v1'):
        self.callbacks = _registry(callbacks)
        self.trace_id, self.definition, self.policy_version = _name(trace_id), _name(definition), _name(policy_version)
        self._states = {s.id: s.initial_state for s in self.callbacks}
        self._control, self._seen, self._prefix = _initial_control(), {}, EMPTY_PREFIX
        self._records, self._observations, self._boundaries = [], [], []
        self.stats = {'records_applied': 0, 'callback_calls': 0, 'retained_record_bytes': 0,
                      'restore_validation_records': 0, 'duplicate_write_retries': 0, 'callback_attempts': 0,
                      'checkpoint_history_rows_serialized': 0, 'checkpoint_bytes_serialized': 0}

    @property
    def states(self):
        return _copy(self._states)

    @property
    def control(self):
        return _copy(self._control)

    @property
    def observations(self):
        return tuple(_copy(o) for o in self._observations)

    @property
    def next_ordinal(self):
        return self._records[-1].arrival_ordinal + 1 if self._records else 0

    def _selected(self, record):
        selected = tuple(s for s in self.callbacks if record.kind in s.accepted_kinds)
        p = record.payload
        named = p.get('decoder_id') if record.kind == 'source' else p.get('callback_id')
        if named is not None and named not in {s.id for s in selected}:
            raise ContractError('record names an unregistered callback or unsupported callback kind')
        if not selected and record.kind in {'source', 'timer', 'completion', 'decision', 'order_ack'}:
            raise ContractError('data/timer/completion/decision/ack requires an explicit callback')
        return selected

    def consume(self, committed):
        if not isinstance(committed, CommittedArrival):
            raise ContractError('replay requires a retained committed boundary')
        record = committed.record
        if record.trace_id != self.trace_id:
            raise ContractError('replay trace identity changed')
        if record.provenance == 'actual_capture' and committed.storage_boundary != 'durable_local_journal':
            raise ContractError('actual receipt cannot bypass durable raw append')
        old = self._seen.get(record.delivery_id)
        if old is not None:
            index = next(i for i, r in enumerate(self._records) if r.delivery_id == record.delivery_id)
            expected_prefix = EMPTY_PREFIX
            for prior in self._records[:index + 1]:
                expected_prefix = prefix_hash(expected_prefix, prior)
            if (old != record.sha256 or committed.prefix_sha256 != expected_prefix
                    or self._boundaries[index] != {'storage_boundary': committed.storage_boundary, 'archive_id': committed.archive_id}):
                raise IntegrityError('replay delivery identity or retained commit proof changed')
            self.stats['duplicate_write_retries'] += 1
            return False
        if len(self._records) >= MAX_RECORDS or record.arrival_ordinal < self.next_ordinal:
            raise ContractError('replay capacity or arrival order violation')
        proposed_prefix = prefix_hash(self._prefix, record)
        if committed.prefix_sha256 != proposed_prefix:
            raise IntegrityError('retained input prefix changed or was skipped')
        if self.stats['retained_record_bytes'] + len(record.canonical_bytes) > MAX_JOURNAL_BYTES:
            raise ContractError('replay retained input byte bound exceeded')
        selected = self._selected(record)
        control = _control_after(self._control, record)
        states, outputs = _copy(self._states), {}
        for spec in selected:
            self.stats['callback_attempts'] += 1
            result = spec.transition(_copy(states[spec.id]), record.record())
            if type(result) is not tuple or len(result) != 2:
                raise ContractError('pure callback must return (new_state, output_list)')
            new_state, emitted = result
            spec.validate_state(new_state)
            _output_sections(emitted)
            states[spec.id], outputs[spec.id] = _copy(new_state), _copy(emitted)
        observation = _observation(record, self.callbacks, states, outputs,
                                   definition=self.definition, policy=self.policy_version)
        proposed_records = self._records + [record]
        proposed_observations = self._observations + [observation]
        proposed_boundaries = self._boundaries + [{'storage_boundary': committed.storage_boundary,
                                                  'archive_id': committed.archive_id}]
        proposed_seen = self._seen | {record.delivery_id: record.sha256}
        # Capacity failure, projection error or callback failure cannot expose
        # any part of the proposed record transition.
        self._checkpoint_value(states=states, control=control, records=proposed_records,
            observations=proposed_observations, boundaries=proposed_boundaries,
            seen=proposed_seen, prefix=proposed_prefix)
        self._states, self._control, self._seen, self._prefix = states, control, proposed_seen, proposed_prefix
        self._records, self._observations, self._boundaries = proposed_records, proposed_observations, proposed_boundaries
        self.stats['records_applied'] += 1
        self.stats['callback_calls'] += len(selected)
        self.stats['retained_record_bytes'] += len(record.canonical_bytes)
        return True

    def consume_all(self, committed_records):
        if type(committed_records) is not tuple:
            raise ContractError('immutable retained trace or batch required')
        for committed in committed_records:
            self.consume(committed)
        return self.observations

    def observation_at_utc(self, cut, *, mapping_policy):
        """UTC cuts require an explicit single-boot nondecreasing mapping."""
        _integer(cut, 'UTC observation cut')
        if mapping_policy != 'single_boot_nondecreasing_utc':
            raise ContractError('unregistered UTC-to-arrival-cut mapping')
        if len({r.boot_id for r in self._records}) > 1 or any(
                a.receipt_utc_ns > b.receipt_utc_ns for a, b in zip(self._records, self._records[1:])):
            raise ContractError('UTC cut is ambiguous across boot/clock adjustment; use arrival ordinal')
        values = [o for o in self._observations if o['timing']['receipt_utc_ns'] <= cut]
        return _copy(values[-1]) if values else None

    def _checkpoint_value(self, *, states=None, control=None, records=None, observations=None,
                          boundaries=None, seen=None, prefix=None):
        records = self._records if records is None else records
        value = {'schema': SCHEMA, 'definition': self.definition, 'policy_version': self.policy_version,
                 'callbacks': [s.declaration() for s in self.callbacks], 'trace_id': self.trace_id,
                 'prefix_sha256': self._prefix if prefix is None else prefix,
                 'consumed_count': len(records), 'next_ordinal': records[-1].arrival_ordinal + 1 if records else 0,
                 'delivery_hashes': self._seen if seen is None else seen,
                 'callback_states': self._states if states is None else states,
                 'control': self._control if control is None else control,
                 'observations': self._observations if observations is None else observations,
                 'input_boundaries': self._boundaries if boundaries is None else boundaries,
                 'simulated_boundary': True, 'actual_live_evidence': False}
        serialized = canonical({'checkpoint': value, 'sha256': content_hash(value)})
        self.stats['checkpoint_history_rows_serialized'] += len(records)
        self.stats['checkpoint_bytes_serialized'] += len(serialized)
        return value

    def checkpoint(self):
        value = self._checkpoint_value()
        return canonical({'checkpoint': value, 'sha256': content_hash(value)})

    def write_checkpoint(self, path, *, hook=None):
        raw = self.checkpoint()
        atomic_write(path, raw, hook=hook)
        return hashlib.sha256(raw).hexdigest()

    @classmethod
    def restore(cls, raw, *, callbacks, retained_prefix, trace_id,
                definition=DEFINITION, policy_version='frozen-offline-v1'):
        parsed = parse_json(raw)
        if type(parsed) is not dict or set(parsed) != {'checkpoint', 'sha256'}:
            raise IntegrityError('checkpoint envelope schema changed')
        if canonical(parsed) != raw or parsed['sha256'] != content_hash(parsed['checkpoint']):
            raise IntegrityError('checkpoint bytes or content hash changed')
        value = parsed['checkpoint']
        result = cls(callbacks, trace_id=trace_id, definition=definition, policy_version=policy_version)
        if (value.get('schema') != SCHEMA or value.get('trace_id') != trace_id
                or value.get('definition') != definition or value.get('policy_version') != policy_version
                or value.get('callbacks') != [s.declaration() for s in result.callbacks]
                or type(retained_prefix) is not tuple or value.get('consumed_count') != len(retained_prefix)):
            raise ContractError('checkpoint prefix/configuration/callback registry mismatch')
        # Bounded full-prefix verification is deliberate and counted, not an
        # unreported constant-time restore or an external exactly-once claim.
        result.consume_all(retained_prefix)
        if result.checkpoint() != raw:
            raise IntegrityError('checkpoint state, clocks, outputs or source identities disagree with retained prefix')
        result.stats['restore_validation_records'] = len(retained_prefix)
        return result

    def service_record(self):
        return {'schema': SCHEMA, 'raw_receipts': [r.record() for r in self._records],
                'canonical_stream': [r.sha256 for r in self._records],
                'served_versions': [o['semantic']['outputs'] for o in self._observations if o['kind'] == 'decision'],
                'trace_prefix': self._prefix, 'clock_diagnostics': self.control['clock_diagnostics'],
                'parity': {'status': 'not_compared'}, 'telemetry': _copy(self.stats),
                'incidents': self.control['gaps'], 'simulated_boundary': True, 'actual_live_evidence': False}


def _numeric_differences(left, right, path='$'):
    result = []
    if type(left) in (int, float) and type(right) in (int, float) and left != right:
        return [{'path': path, 'left': left, 'right': right}]
    if type(left) is dict and type(right) is dict:
        for key in sorted(set(left) & set(right)):
            result.extend(_numeric_differences(left[key], right[key], path + '.' + key))
    elif type(left) is list and type(right) is list:
        for i, (a, b) in enumerate(zip(left, right)):
            result.extend(_numeric_differences(a, b, path + '[' + str(i) + ']'))
    return result


def compare_observations(left, right):
    if left is None or right is None:
        return {'semantic_equal': False, 'timing_equal': False, 'transport_equal': False,
                'identity_equal': False, 'parity': False, 'difference_kind': 'missing_observation'}
    semantic = left['semantic'] == right['semantic'] and left['semantic_sha256'] == right['semantic_sha256']
    timing = left['timing'] == right['timing']
    transport = left['transport'] == right['transport']
    identity = (left['arrival_ordinal'], left['delivery_id'], left['kind']) == (right['arrival_ordinal'], right['delivery_id'], right['kind'])
    kind = ('equal' if semantic and timing and transport and identity else 'semantic_mismatch' if not semantic
            else 'timing_mismatch' if not timing else 'transport_only_difference' if not transport else 'record_identity_mismatch')
    return {'semantic_equal': semantic, 'timing_equal': timing, 'transport_equal': transport,
            'identity_equal': identity, 'parity': semantic and timing and transport and identity,
            'difference_kind': kind, 'numeric_tolerance': 0,
            'numeric_differences': _numeric_differences(left['semantic'], right['semantic'])}


def first_divergence(left, right, *, original_records, scope='all'):
    if scope not in {'all', 'decisions'} or type(original_records) is not tuple:
        raise ContractError('explicit parity scope and retained original trace required')
    left = tuple(o for o in left if scope == 'all' or o['kind'] == 'decision')
    right = tuple(o for o in right if scope == 'all' or o['kind'] == 'decision')
    for index in range(max(len(left), len(right))):
        a = left[index] if index < len(left) else None
        b = right[index] if index < len(right) else None
        comparison = compare_observations(a, b)
        if not comparison['parity']:
            row = a if a is not None else b
            end = next((i + 1 for i, r in enumerate(original_records) if r.delivery_id == row['delivery_id']), None)
            return {'scope': scope, 'status': 'divergent', 'comparison': comparison,
                    'first_ordinal': row['arrival_ordinal'], 'diagnostic_receipt_utc_ns': row['timing']['receipt_utc_ns'],
                    'delivery_id': row['delivery_id'], 'left': a, 'right': b,
                    'minimal_leading_prefix': None if end is None else [r.record() for r in original_records[:end]],
                    'minimality': 'shortest original leading prefix containing first unequal selected boundary',
                    'simulated_boundary': True, 'actual_live_evidence': False}
    return {'scope': scope, 'status': 'equal', 'compared_boundaries': len(left),
            'minimal_leading_prefix': None, 'simulated_boundary': True, 'actual_live_evidence': False}


def delay_one(records, *, seed, target_utc_ns, target_monotonic_ns):
    """Counterfactual derived trace with explicit origin map; original bytes stay intact."""
    _integer(seed, 'fault seed', nonnegative=True)
    _integer(target_utc_ns, 'fault UTC target')
    _integer(target_monotonic_ns, 'fault monotonic target', nonnegative=True)
    if type(records) is not tuple or not records or len(records) > MAX_RECORDS:
        raise ContractError('bounded original fault trace required')
    control, previous, identities = _initial_control(), -1, set()
    for record in records:
        if not isinstance(record, ArrivalRecord):
            raise ContractError('typed original fault records required')
        if record.trace_id != records[0].trace_id or record.arrival_ordinal <= previous or record.delivery_id in identities:
            raise ContractError('original fault trace identity/order invalid')
        control = _control_after(control, record)
        previous = record.arrival_ordinal
        identities.add(record.delivery_id)
    if len({r.boot_id for r in records}) != 1 or any(r.provenance == 'actual_capture' for r in records):
        raise ContractError('bounded fault transformation supports one-boot synthetic/model traces only')
    eligible = sorted((r for r in records if r.kind == 'source'), key=lambda r: r.arrival_ordinal)
    if not eligible:
        raise ContractError('delay fault has no eligible source receipt')
    selected_index = seed % len(eligible)
    selected = eligible[selected_index]
    if target_utc_ns < selected.receipt_utc_ns or target_monotonic_ns < selected.receipt_monotonic_ns:
        raise ContractError('delay fault cannot move receipt earlier')
    plan = {'name': 'delay_one', 'version': 'integer-slot-v1', 'seed': seed,
            'selected_index': selected_index, 'selected_original_ordinal': selected.arrival_ordinal,
            'selected_delivery_id': selected.delivery_id, 'target_utc_ns': target_utc_ns,
            'target_monotonic_ns': target_monotonic_ns,
            'original_sha256': content_hash([r.record() for r in records])}
    trace_id = records[0].trace_id + ':fault:' + content_hash(plan)
    ordered = sorted(records, key=lambda r: (target_monotonic_ns if r is selected else r.receipt_monotonic_ns,
                                            1 if r is selected else 0, r.arrival_ordinal))
    transformed, mapping, control = [], [], _initial_control()
    for ordinal, old in enumerate(ordered):
        row = old.record() | {'trace_id': trace_id, 'arrival_ordinal': ordinal, 'provenance': 'modeled_scenario'}
        if old is selected:
            row |= {'receipt_utc_ns': target_utc_ns, 'receipt_monotonic_ns': target_monotonic_ns}
        new = ArrivalRecord.from_record(row)
        control = _control_after(control, new)
        transformed.append(new)
        mapping.append({'arrival_ordinal': ordinal, 'original_ordinal': old.arrival_ordinal,
                        'delivery_id': old.delivery_id, 'original_sha256': old.sha256})
    plan |= {'origin_mapping': mapping, 'transformed_sha256': content_hash([r.record() for r in transformed]),
             'simulated_boundary': True, 'actual_live_evidence': False}
    return tuple(transformed), plan


def monotonic_elapsed(start_boot, start_ns, end_boot, end_ns):
    _name(start_boot); _name(end_boot)
    _integer(start_ns, 'monotonic start', nonnegative=True); _integer(end_ns, 'monotonic end', nonnegative=True)
    if start_boot != end_boot:
        return {'elapsed_ns': None, 'reason': 'cross_boot'}
    if end_ns < start_ns:
        raise ContractError('same-boot elapsed clock regressed')
    return {'elapsed_ns': end_ns - start_ns, 'reason': 'same_boot_monotonic'}


def receipt_lag(record, *, source_id, session_id, method='source_to_receipt',
                comparable_clock_evidence_id=None, uncertainty_ns=None):
    _name(source_id); _name(session_id)
    if not isinstance(record, ArrivalRecord) or method not in ('source_to_receipt', 'provider_to_receipt'):
        raise ContractError('typed arrival and registered lag method required')
    if record.kind != 'source' or record.payload['source_id'] != source_id:
        raise ContractError('lag source label must match retained source identity')
    if comparable_clock_evidence_id is not None:
        _name(comparable_clock_evidence_id)
    if uncertainty_ns is not None:
        _integer(uncertainty_ns, 'clock uncertainty', nonnegative=True)
    source = record.source_event_utc_ns if method == 'source_to_receipt' else record.provider_published_utc_ns
    value = None if source is None else record.receipt_utc_ns - source
    qualified = source is not None and comparable_clock_evidence_id is not None and uncertainty_ns is not None
    return {'retained_record': record.record(), 'delivery_id': record.delivery_id, 'source_id': source_id, 'session_id': session_id,
            'method': method, 'provenance': record.provenance, 'value_ns': value,
            'uncertainty_ns': uncertainty_ns, 'clock_evidence_id': comparable_clock_evidence_id,
            'qualified': qualified, 'actual_qualified': qualified and record.provenance == 'actual_capture',
            'reason': 'missing_source_clock' if source is None else 'qualified_clock_pair' if qualified else 'unverified_clock_comparability',
            'simulated_boundary': True, 'actual_live_evidence': False}


def completion_lag(record, *, source_id, session_id):
    if not isinstance(record, ArrivalRecord) or record.kind != 'completion':
        raise ContractError('completion receipt required')
    _name(source_id); _name(session_id)
    p = record.payload
    elapsed = monotonic_elapsed(p['start_boot_id'], p['start_monotonic_ns'], record.boot_id, record.receipt_monotonic_ns)
    return {'retained_record': record.record(), 'delivery_id': record.delivery_id, 'source_id': source_id, 'session_id': session_id,
            'method': 'start_to_completion_monotonic', 'provenance': record.provenance,
            'value_ns': elapsed['elapsed_ns'], 'uncertainty_ns': 0 if elapsed['elapsed_ns'] is not None else None,
            'clock_evidence_id': record.delivery_id, 'qualified': elapsed['elapsed_ns'] is not None,
            'actual_qualified': elapsed['elapsed_ns'] is not None and record.provenance == 'actual_capture',
            'reason': elapsed['reason'], 'simulated_boundary': True, 'actual_live_evidence': False}


def latency_summary(samples, *, source_id, session_id, method, provenance):
    _name(source_id); _name(session_id); _name(method)
    if type(samples) is not tuple or len(samples) > MAX_RECORDS or type(provenance) is not str or provenance not in PROVENANCES:
        raise ContractError('immutable latency samples and explicit provenance required')
    if method not in ('source_to_receipt', 'provider_to_receipt', 'start_to_completion_monotonic'):
        raise ContractError('unknown latency method')
    unique = {}
    for sample in samples:
        _required(sample, ('retained_record', 'source_id', 'session_id', 'method', 'clock_evidence_id', 'uncertainty_ns'))
        record = ArrivalRecord.from_record(sample['retained_record'])
        if sample['method'] == 'start_to_completion_monotonic':
            expected = completion_lag(record, source_id=sample['source_id'], session_id=sample['session_id'])
        else:
            expected = receipt_lag(record, source_id=sample['source_id'], session_id=sample['session_id'],
                method=sample['method'], comparable_clock_evidence_id=sample['clock_evidence_id'], uncertainty_ns=sample['uncertainty_ns'])
        if canonical(sample) != canonical(expected):
            raise IntegrityError('latency arithmetic/qualification differs from retained evidence')
        key = content_hash([record.trace_id, record.delivery_id, sample['source_id'], sample['session_id'], sample['method']])
        if key in unique and unique[key] != sample:
            raise IntegrityError('latency sample identity changed')
        unique[key] = _copy(sample)
    selected = [s for s in unique.values() if (s['source_id'], s['session_id'], s['method'], s['provenance'])
                == (source_id, session_id, method, provenance)]
    values = sorted(s['value_ns'] for s in selected if s['qualified'] and s['value_ns'] is not None)
    for value in values:
        _integer(value, 'lag sample')
    def quantile(numerator):
        return values[(numerator * len(values) + 99) // 100 - 1] if values else None
    return {'source_id': source_id, 'session_id': session_id, 'method': method, 'provenance': provenance,
            'duplicate_samples': len(samples) - len(unique), 'n': len(values), 'excluded': len(selected) - len(values), 'p50': quantile(50),
            'p95': quantile(95), 'p99': quantile(99), 'reason': 'qualified_samples' if values else 'no_qualified_samples',
            'actual_qualified_count': sum(s['actual_qualified'] for s in selected if s['qualified'] and s['value_ns'] is not None),
            'simulated_boundary': True, 'actual_live_evidence': False}


def drop_summary(population_ids, *, source_id, generation, window_id, identity_contract,
                 expected_count=None, expected_evidence_id=None):
    for value in (source_id, generation, window_id, identity_contract):
        _name(value)
    if type(population_ids) is not tuple or len(population_ids) > MAX_RECORDS:
        raise ContractError('bounded explicit delivery population identities required')
    for value in population_ids:
        _name(value)
    unique = len(set(population_ids))
    if expected_count is not None:
        _integer(expected_count, 'expected population', nonnegative=True)
        _name(expected_evidence_id, 'independently evidenced expected population')
        if unique > expected_count:
            raise IntegrityError('observed unique population exceeds the declared expected universe')
    elif expected_evidence_id is not None:
        raise ContractError('expected evidence without a population count is incomplete')
    missing = None if expected_count is None else expected_count - unique
    return {'source_id': source_id, 'generation': generation, 'window_id': window_id,
            'identity_contract': identity_contract, 'unique_received': unique,
            'duplicate_receipts': len(population_ids) - unique, 'expected_count': expected_count,
            'expected_evidence_id': expected_evidence_id, 'missing': missing,
            'drop_rate': [missing, expected_count] if expected_count else None,
            'reason': 'missing_expected_population' if expected_count is None else 'empty_expected_population' if not expected_count else 'evidenced_population',
            'simulated_boundary': True, 'actual_live_evidence': False}


def _schema_transition(transition):
    """Normalize malformed declared adapter payloads, preserving domain failures."""
    def guarded(state, record):
        try:
            return transition(state, record)
        except (ContractError, IntegrityError):
            raise
        except (KeyError, TypeError, AttributeError, ValueError, UnicodeError) as exc:
            raise ContractError('malformed registered wrapper payload') from exc
    return guarded


def _synthetic_scope(state, record, *, allow_provider_sequence_merge=False):
    if record['provenance'] not in ('synthetic_fixture', 'modeled_scenario'):
        raise ContractError('pure wrapper requires explicit synthetic/model clocks; actual capture is gated')
    if record['kind'] == 'source':
        keys = ('instrument', 'definition') if allow_provider_sequence_merge else ('source_id', 'instrument', 'definition')
        scope = {k: record['payload'][k] for k in keys}
        if state['source_scope'] is not None and state['source_scope'] != scope:
            raise ContractError('single-scope wrapper source identity changed')
        state['source_scope'] = scope


# These finite adapters bind existing kernels to detached JSON state. They do
# not implement vendor parsers or certify that supplied evidence was captured.
def market_callback(id='market', *, version='toy-market-v1'):
    initial = {'value': None, 'quantity': 0, 'economic_applications': 0, 'raw_deliveries': 0,
               'seen': {}, 'incidents': [], 'timers': [], 'timer_business': {}, 'decisions': [], 'source_scope': None}
    def transition(state, record):
        p, kind = record['payload'], record['kind']
        if record['provenance'] not in ('synthetic_fixture', 'modeled_scenario'):
            raise ContractError('toy callback supports only synthetic/model records')
        if kind == 'source':
            if p['decoder_id'] != id:
                return state, []
            _synthetic_scope(state, record, allow_provider_sequence_merge=True)
            raw = parse_json(bytes.fromhex(p['raw_hex']), max_bytes=MAX_RAW_BYTES)
            if type(raw) is not dict:
                raise ContractError('toy decoder requires an explicit object')
            state['raw_deliveries'] += 1
            economic = None if p['economic_id'] is None else content_hash([p['source_id'], p['instrument'], p['definition'], p['economic_id']])
            business = content_hash([p['semantic_kind'], raw])
            if economic is not None and economic in state['seen']:
                if state['seen'][economic] != business:
                    state['incidents'].append({'kind': 'economic_identity_conflict', 'economic_id': p['economic_id']})
                    return state, [{'semantic': {'status': 'economic_conflict'}, 'transport': {'delivery_id': record['delivery_id']}}]
                return state, [{'semantic': {'status': 'duplicate_economic_event'}, 'transport': {'delivery_id': record['delivery_id']}}]
            if p['semantic_kind'] in {'snapshot', 'trade'}:
                quantity = _integer(raw.get('quantity'), 'toy quantity', nonnegative=True)
                state['quantity'] = quantity if p['semantic_kind'] == 'snapshot' else state['quantity'] + quantity
            if 'value' in raw:
                state['value'] = _integer(raw['value'], 'toy value')
            if economic is not None:
                state['seen'][economic] = business
            state['economic_applications'] += 1
            return state, [{'semantic': {'status': 'applied', 'value': state['value'], 'quantity': state['quantity']}}]
        if p.get('callback_id') != id:
            return state, []
        if kind == 'timer':
            signature = content_hash(p)
            if p['timer_id'] in state['timer_business'] and state['timer_business'][p['timer_id']] != signature:
                raise IntegrityError('timer firing identity changed')
            state['timer_business'][p['timer_id']] = signature
            duplicate = p['timer_id'] in state['timers']
            if not duplicate:
                state['timers'].append(p['timer_id'])
            return state, [{'semantic': {'timer_id': p['timer_id'], 'duplicate': duplicate},
                            'timing': {'fired_ordinal': record['arrival_ordinal']}}]
        state['decisions'].append({'decision_id': p['decision_id'], 'value': state['value'], 'quantity': state['quantity']})
        return state, [{'semantic': state['decisions'][-1], 'transport': {'recorded_action': p['action']}}]
    return CallbackSpec(id, content_hash(version), frozenset({'source', 'decision', 'timer'}), 'ToyMarketState.v1',
        initial, _schema_transition(transition), semantic_projection=lambda s: {k: s[k] for k in ('value', 'quantity', 'incidents', 'timers', 'decisions')},
        projection_id='toy-economic-state-v1')


def transaction_callback(id='transactions'):
    from trading_research.data.transactions import TransactionKey, TransactionValue, TransactionReceipt, TransactionLedger
    from trading_research.foundations.time import AvailabilityBasis, Clocks
    initial = {'checkpoint_hex': None, 'raw_deliveries': 0, 'economic_applications': 0,
               'quantity': 0, 'versions': [], 'incidents': [], 'source_scope': None}
    def transition(state, record):
        p = record['payload']
        if p['decoder_id'] != id:
            return state, []
        _synthetic_scope(state, record)
        if p['semantic_kind'] != 'trade':
            raise ContractError('F05 transaction wrapper requires explicit trade semantics')
        body = parse_json(bytes.fromhex(p['raw_hex']), max_bytes=MAX_RAW_BYTES)
        _required(body, ('transaction_key', 'version_id', 'operation', 'predecessor_version_id',
                         'value', 'condition_contract_id', 'identity_evidence_id'))
        key = TransactionKey(**body['transaction_key'])
        if (p['economic_id'] != key.ownership_id or p['source_id'] != key.provider
                or p['instrument'] != key.instrument_key):
            raise ContractError('source/economic identity does not match declared F05 ownership')
        value = None if body['value'] is None else TransactionValue.restore(body['value'])
        if value is not None and (value.terms_version != p['definition'] or value.event_at != record['source_event_utc_ns']):
            raise ContractError('F05 value changed source event/definition identity')
        at = record['arrival_ordinal']
        clocks = Clocks(record['source_event_utc_ns'], at, body['version_id'], AvailabilityBasis.ASSUMED,
                        assumption_id='F12.synthetic-logical-arrival-ordinal')
        raw = bytes.fromhex(p['raw_hex'])
        receipt = TransactionReceipt(record['delivery_id'], body['version_id'], key, body['version_id'],
            body['predecessor_version_id'], body['operation'], clocks,
            'F12:' + record['trace_id'] + ':' + record['delivery_id'], p['raw_sha256'], raw, value,
            body['condition_contract_id'], body['identity_evidence_id'])
        ledger = TransactionLedger() if state['checkpoint_hex'] is None else TransactionLedger.restore(bytes.fromhex(state['checkpoint_hex']))
        state['raw_deliveries'] += 1
        try:
            admission = ledger.admit(receipt, actual_completion_at=at)
        except IntegrityError as exc:
            state['incidents'].append({'kind': 'economic_identity_conflict', 'delivery_id': record['delivery_id'], 'reason': str(exc)})
            return state, [{'semantic': {'status': 'economic_conflict'}, 'transport': {'delivery_id': record['delivery_id']}}]
        state['checkpoint_hex'] = ledger.checkpoint().hex()
        state['economic_applications'] += len(admission.deltas)
        values = ledger.asof(instrument=p['instrument'], cut=at)
        state['quantity'] = sum(row.value.quantity for row in values if row.value.volume_eligibility is True)
        state['versions'] = sorted(row.version_id for row in values)
        return state, [{'semantic': {'status': admission.status, 'quantity': state['quantity'], 'versions': state['versions']},
                        'timing': {'kernel_logical_completion_ordinal': at},
                        'transport': {'receipt_id': receipt.receipt_id, 'clock_basis': 'synthetic logical ordinal; economic event UTC preserved'}}]
    return CallbackSpec(id, content_hash('F05.TransactionLedger-wrapper-v1'), frozenset({'source'}),
        'F12.F05State.v1', initial, _schema_transition(transition),
        semantic_projection=lambda s: {'quantity': s['quantity'], 'versions': s['versions'],
                                      'economic_applications': s['economic_applications'],
                                      'incident_kinds': [i['kind'] for i in s['incidents']]},
        projection_id='F05-economic-projection-v1')


def quality_callback(bindings, *, entry_fields, protection_fields=(), graph=None, id='quality', joint_span_ns=2**62):
    """F06/F07 wrapper for explicitly UTC-compatible synthetic records only.

    Clock-adjusted inputs need a separately registered F07 clock contract; the
    wrapper rejects them rather than altering economic observation timestamps.
    """
    from trading_research.foundations.joined import EligibilityIndex, JointPolicy
    from trading_research.foundations.quality import FieldFact, QualityIncident, QualityRecovery
    from trading_research.foundations.time import Clocks, AvailabilityBasis
    from trading_research.runtime.scheduling import DirtyPlanner
    if type(bindings) is not tuple or any(type(row) is not tuple or len(row) != 3 for row in bindings):
        raise ContractError('quality adapter needs (name, FieldKey, OperationPolicy) tuples')
    if type(entry_fields) is not tuple or type(protection_fields) is not tuple:
        raise ContractError('quality scopes must be immutable tuples')
    _integer(joint_span_ns, 'declared synthetic joint span', nonnegative=True)
    by_name = {name: (key, policy) for name, key, policy in bindings}
    if len(by_name) != len(bindings) or not entry_fields or not set((*entry_fields, *protection_fields)).issubset(by_name):
        raise ContractError('quality entry/protection scopes must name registered fields')
    kernel_bindings = tuple((key, policy) for _, key, policy in bindings)
    initial = {'events': [], 'last_utc': None, 'support': {}, 'entry_eligible': False,
               'protection_eligible': False, 'blocked_ports': [], 'unconditional_ports': []}
    def event_from(record):
        p, at = record['payload'], record['receipt_utc_ns']
        if record['kind'] == 'source' and p['decoder_id'] == id:
            b = parse_json(bytes.fromhex(p['raw_hex']), max_bytes=MAX_RAW_BYTES)
            _required(b, ('quality_kind',))
            if b.get('quality_kind') == 'no_data':
                return None
            if b.get('quality_kind') == 'fact':
                _required(b, ('field_name', 'observed_at', 'value', 'available_operations'))
                _name_list(b['available_operations'], 'explicit synthetic capabilities')
                _name(b['field_name'], 'quality field')
                if b['field_name'] not in by_name:
                    raise ContractError('unregistered quality field')
                key, policy = by_name[b['field_name']]
                if p['instrument'] != key.instrument or p['definition'] != key.definition_version:
                    raise ContractError('quality source identity changed')
                observed = _integer(b['observed_at'], 'economic field observation UTC')
                if record['source_event_utc_ns'] is not None and record['source_event_utc_ns'] != observed:
                    raise ContractError('quality wrapper cannot alter the economic observation clock')
                clocks = Clocks(observed, at, b.get('source_version', record['delivery_id']), AvailabilityBasis.ASSUMED,
                    assumption_id='F12.synthetic-UTC-compatible', clock_uncertainty_ns=b.get('uncertainty_ns', 0))
                return FieldFact(b.get('fact_id', record['delivery_id']), key, p['source_id'], observed,
                    clocks, canonical(b['value']), revision=b.get('revision', 0),
                    available_operations=frozenset(b['available_operations']),
                    eligible=b.get('eligible', True), estimated=b.get('estimated', False))
            if b.get('quality_kind') == 'recovery':
                fields = frozenset(by_name[n][0] for n in b['field_names'])
                return QualityRecovery(b['id'], b['incident_id'], fields, at, b['effective_at'], b['method'], b['evidence_id'])
            raise ContractError('unregistered synthetic quality payload')
        if record['kind'] == 'gap' and p.get('quality_fields'):
            if p['status'] != 'open':
                raise ContractError('transport gap close is not a certified F06 field recovery')
            fields = frozenset(by_name[n][0] for n in p['quality_fields'])
            return QualityIncident(p['gap_id'], 'raw', fields, at, p.get('affected_from_utc_ns', at), None,
                p.get('quality_kind', 'source_gap'), 'dependent-feature-block',
                frozenset(by_name[n][1].operation for n in p['quality_fields']), record['delivery_id'],
                scope=p.get('quality_scope', 'state'), requires_recovery=p.get('requires_recovery', False))
        return None
    def transition(state, record):
        if record['provenance'] == 'actual_capture' or (state['last_utc'] is not None and record['receipt_utc_ns'] < state['last_utc']):
            raise ContractError('F07 wrapper requires the registered nondecreasing synthetic UTC contract')
        event = event_from(record)
        if event is not None:
            state['events'].append(record)
        index = EligibilityIndex(kernel_bindings)
        for prior in state['events']:
            index.append(event_from(prior))
        cut = record['receipt_utc_ns']
        support = {name: index.field(key, policy.id, cut=cut) for name, (key, policy) in by_name.items()}
        state['support'] = {name: {'admitted': value.admitted, 'state': value.state,
                                  'value': None if value.payload_json is None else parse_json(value.payload_json),
                                  'reasons': list(value.reasons), 'candidate_id': value.candidate_id,
                                  'observed_at': value.observed_at, 'age_ns': value.age_ns}
                            for name, value in support.items()}
        joint = JointPolicy('F12.synthetic-joined', joint_span_ns)
        state['entry_eligible'] = index.snapshot(tuple((by_name[n][0], by_name[n][1].id) for n in entry_fields), cut=cut, joint_policy=joint).supported
        state['protection_eligible'] = bool(protection_fields) and index.snapshot(
            tuple((by_name[n][0], by_name[n][1].id) for n in protection_fields), cut=cut, joint_policy=joint).supported
        if graph is not None:
            unavailable = frozenset(by_name[n][0].producer for n, value in support.items() if not value.admitted)
            plan = DirtyPlanner(graph).plan({}, unavailable=unavailable)
            state['blocked_ports'], state['unconditional_ports'] = sorted(plan.blocked), list(plan.unconditional)
        state['last_utc'] = cut
        return state, [{'semantic': {'fields': state['support'], 'entry_eligible': state['entry_eligible'],
                                     'independent_protection_eligible': state['protection_eligible'],
                                     'blocked_ports': state['blocked_ports'], 'unconditional_ports': state['unconditional_ports']},
                        'transport': {'kernel': 'F06/F07 and DirtyPlanner', 'clock_contract': 'synthetic UTC-compatible'}}]
    declaration = {'wrapper': 'F06/F07-v1', 'bindings': [[n, k.version, p.version] for n, k, p in bindings],
                   'entry_fields': list(entry_fields), 'protection_fields': list(protection_fields),
                   'graph_version': None if graph is None else graph.version, 'joint_span_ns': joint_span_ns}
    return CallbackSpec(id, content_hash(declaration), frozenset({'source', 'gap', 'decision'}), 'F12.QualityState.v1', initial,
        _schema_transition(transition), semantic_projection=lambda s: {k: s[k] for k in ('support', 'entry_eligible', 'protection_eligible', 'blocked_ports', 'unconditional_ports')},
        projection_id='F06/F07-support-v1')


class _MemoryJournal:
    """Detached implementation of the existing Journal read/append boundary."""
    def __init__(self, events=()):
        self.events = _copy(list(events))
        from trading_research.operations.artifacts import canonical_json as kernel_json
        from trading_research.operations.journal import Journal
        previous = None
        for index, event in enumerate(self.events, 1):
            expected = Journal._hash(index, event['key'], event['kind'], kernel_json(event['payload']), previous)
            if (event['sequence'], event['previous'], event['hash']) != (index, previous, expected):
                raise IntegrityError('memory kernel journal prefix corrupted')
            previous = expected

    def read(self):
        return tuple(_copy(e) for e in self.events)

    def append(self, *, key, kind, payload, expected_head=None, check_head=False):
        from trading_research.operations.artifacts import canonical_json as kernel_json
        from trading_research.operations.journal import Journal
        raw = kernel_json(payload)
        normalized = json.loads(raw)
        for old in self.events:
            if old['key'] == key:
                if old['kind'] != kind or old['payload'] != normalized:
                    raise IntegrityError('memory kernel journal idempotency key conflict')
                return old['hash'], False
        previous = self.events[-1]['hash'] if self.events else None
        if check_head and previous != expected_head:
            raise ContractError('memory kernel journal optimistic head changed')
        sequence = len(self.events) + 1
        sha = Journal._hash(sequence, key, kind, raw, previous)
        self.events.append({'sequence': sequence, 'key': key, 'kind': kind, 'payload': normalized,
                            'previous': previous, 'hash': sha})
        canonical(self.events)
        return sha, True


def publication_callback(id='publication'):
    from trading_research.foundations.graph import Graph, Port, InputPort
    from trading_research.foundations.time import Clocks, AvailabilityBasis
    from trading_research.runtime.publication import VersionStore
    graph = Graph((Port('F12.wrapper.input', 'F12', 0, 'F12.Input.v1', frozenset({'value'}), lane='offline'),
        Port('F12.wrapper.result', 'F12', 1, 'F12.Result.v1', frozenset({'value'}),
             (InputPort('F12.wrapper.input', 'F12.Input.v1', frozenset({'value'})),), lane='offline')))
    initial = {'journal': [], 'sources': {}, 'jobs': {}, 'completed': {}, 'published': [], 'served': [], 'timers': [], 'timer_business': {}, 'source_scope': None}
    def transition(state, record):
        p, kind, at = record['payload'], record['kind'], record['arrival_ordinal']
        if (p.get('decoder_id') if kind == 'source' else p.get('callback_id')) != id:
            return state, []
        _synthetic_scope(state, record)
        journal = _MemoryJournal(state['journal'])
        store = VersionStore(graph, journal)
        emitted = []
        if kind == 'source':
            body = parse_json(bytes.fromhex(p['raw_hex']), max_bytes=MAX_RAW_BYTES)
            _required(body, ('version_id', 'value', 'job_id', 'expires_at_ordinal'))
            version, job = _name(body['version_id']), _name(body['job_id'])
            old = state['sources'].get(version)
            if old is not None:
                if old['business_sha256'] != content_hash(body):
                    raise IntegrityError('publication source version changed')
                return state, [{'semantic': {'status': 'duplicate_source_version', 'version': version}}]
            clocks = Clocks(record['source_event_utc_ns'], at, version, AvailabilityBasis.ASSUMED,
                            assumption_id='F12.synthetic-logical-arrival-ordinal')
            root = store.publish_root('F12.wrapper.input', cut=at, clocks=clocks, payload=canonical(body['value']),
                                      source_evidence_ids=(record['delivery_id'],))
            request = store.freeze('F12.wrapper.result', cut=at, submitted_at=at, input_ids=(root.metadata.id,),
                expires_at=body['expires_at_ordinal'], horizon_end=body.get('horizon_end_ordinal'),
                code_version='F12.publication-wrapper-v1', parameter_version='frozen')
            if job in state['jobs']:
                raise IntegrityError('computation job ID changed')
            state['sources'][version] = {'business_sha256': content_hash(body), 'root_id': root.metadata.id}
            state['jobs'][job] = {'request_id': request.id, 'input_version_ids': [version],
                'submitted_boot_id': record['boot_id'], 'submitted_monotonic_ns': record['receipt_monotonic_ns']}
            emitted = [{'semantic': {'status': 'frozen', 'input_version': version}, 'timing': {'submitted_ordinal': at}}]
        elif kind == 'completion':
            job = state['jobs'].get(p['job_id'])
            if job is None or job['input_version_ids'] != p['input_version_ids']:
                raise ContractError('completion changed the registered frozen input vector')
            if p['start_boot_id'] != job['submitted_boot_id'] or p['start_monotonic_ns'] < job['submitted_monotonic_ns']:
                raise ContractError('computation start must follow its frozen inputs in the same boot')
            business = content_hash(p)
            if p['job_id'] in state['completed']:
                if state['completed'][p['job_id']]['business'] != business:
                    raise IntegrityError('completed job content changed')
                return state, [{'semantic': {'status': 'duplicate_completion'}}]
            request = store.restore_request(job['request_id'])
            value = store.complete(request, payload=canonical(p['result']), completed_at=at)
            state['completed'][p['job_id']] = {'business': business, 'completed_ordinal': at}
            if value is not None:
                item = {'input_version': p['input_version_ids'][0], 'published_ordinal': at,
                        'kernel_version_id': value.metadata.id, 'value': p['result']}
                state['published'].append(item)
                emitted = [{'semantic': {'status': 'published', 'input_version': item['input_version'], 'value': item['value']},
                            'timing': {'published_ordinal': at}, 'transport': {'kernel_version_id': value.metadata.id}}]
            else:
                emitted = [{'semantic': {'status': 'expired'}, 'timing': {'completed_ordinal': at}}]
        elif kind == 'decision':
            latest = store.latest('F12.wrapper.result', available_at=at, observation_cut=at, max_age_ns=2**62)
            item = None if latest is None else next(x for x in state['published'] if x['kernel_version_id'] == latest.metadata.id)
            served = [] if item is None else [item['input_version']]
            result = {'decision_id': p['decision_id'], 'served': served,
                      'value': None if item is None else item['value'], 'matches_recorded_versions': served == p['served_version_ids']}
            state['served'].append(result)
            emitted = [{'semantic': result, 'timing': {'decision_ordinal': at},
                        'transport': {'recorded_action': p['action'], 'kernel_version_id': None if latest is None else latest.metadata.id}}]
        else:
            signature = content_hash(p)
            if p['timer_id'] in state['timer_business']:
                if state['timer_business'][p['timer_id']] != signature:
                    raise IntegrityError('timer firing identity changed')
                return state, [{'semantic': {'status': 'duplicate_timer'}}]
            state['timer_business'][p['timer_id']] = signature
            state['timers'].append(p['timer_id'])
            emitted = [{'semantic': {'timer_id': p['timer_id']}, 'timing': {'fired_ordinal': at}}]
        state['journal'] = list(journal.read())
        return state, emitted
    return CallbackSpec(id, content_hash('VersionStore-pure-memory-wrapper-v1'), frozenset({'source', 'completion', 'decision', 'timer'}),
        'F12.PublicationState.v1', initial, _schema_transition(transition),
        semantic_projection=lambda s: {'published': [{'input_version': p['input_version'], 'value': p['value']} for p in s['published']],
                                      'served': s['served'], 'timers': s['timers']},
        projection_id='VersionStore-economic-output-v1')


def order_callback(initial_orders, *, account_id, initial_events=(), id='orders'):
    """Bind OrderLedger.observe to supplied pending orders and in-memory journal.

    Existing order intents are boundary input. OrderLedger.submit is never called.
    No path, SDK, broker transport or reconciliation permission is passed in.
    """
    from dataclasses import asdict
    from trading_research.execution.orders import OrderLedger, OrderSpec, BrokerEvent
    if (type(initial_orders) is not tuple or any(not isinstance(s, OrderSpec) or s.account_id != account_id for s in initial_orders)
            or type(initial_events) is not tuple or any(not isinstance(e, BrokerEvent) for e in initial_events)):
        raise ContractError('typed supplied simulated orders/events required')
    _name(account_id)
    def ledger_for(events):
        # Constructor owns filesystem I/O. The existing pure reducer and observe
        # method need only these two explicitly supplied attributes.
        ledger = object.__new__(OrderLedger)
        ledger.account_id, ledger.journal = account_id, _MemoryJournal(events)
        return ledger
    initial_journal = _MemoryJournal()
    initial_journal.append(key='account-contract', kind='order_account',
                           payload={'account_id': account_id, 'adapter': 'simulated-and-replayed-broker-evidence-only'})
    for spec in initial_orders:
        initial_journal.append(key='order:' + spec.client_id, kind='order_submitted', payload={'spec': asdict(spec)})
    initial_ledger = ledger_for(initial_journal.read())
    for event in initial_events:
        initial_ledger.observe(event)
    initial = {'journal': list(initial_ledger.journal.read()), 'ack_business': {}, 'last_economic': {e.client_id: [max(x.event_at for x in initial_events if x.client_id == e.client_id), -1] for e in initial_events},
               'version_business': {}, 'source_scope': None,
               'raw_acks': 0, 'stale_rejections': 0, 'duplicates': 0, 'states': {},
               'positions': dict(initial_ledger.state()['positions']), 'incidents': [], 'submissions': 0}
    def transition(state, record):
        p, at = record['payload'], record['arrival_ordinal']
        if p.get('callback_id', id) != id:
            return state, []
        _synthetic_scope(state, record)
        initial_known = max((e.known_at for e in initial_events), default=max((o.submitted_at for o in initial_orders), default=0))
        if at < initial_known:
            raise ContractError('arrival ordinal precedes declared initial logical order boundary')
        state['raw_acks'] += 1
        business = content_hash(p)
        old = state['ack_business'].get(p['ack_id'])
        if old is not None:
            if old != business:
                raise IntegrityError('acknowledgement economic ID changed')
            state['duplicates'] += 1
            return state, [{'semantic': {'status': 'duplicate_ack'}}]
        state['ack_business'][p['ack_id']] = business
        prior = state['last_economic'].get(p['order_id'])
        identity = [p['economic_known_at'], p['state_version']]
        version_key = content_hash([p['order_id'], identity])
        version_business = content_hash({k: v for k, v in p.items() if k not in {'ack_id', 'evidence_version'}})
        if version_key in state['version_business'] and state['version_business'][version_key] != version_business:
            raise IntegrityError('order state version has contradictory content')
        state['version_business'][version_key] = version_business
        if prior is not None and identity < prior:
            state['stale_rejections'] += 1
            state['incidents'].append({'kind': 'stale_order_state', 'ack_id': p['ack_id']})
            return state, [{'semantic': {'status': 'stale_order_state_rejected'}, 'transport': {'ack_id': p['ack_id']}}]
        ledger = ledger_for(state['journal'])
        message = BrokerEvent(p['ack_id'], p['order_id'], p.get('state', 'acknowledged'),
            p['economic_known_at'], at, p.get('evidence_version', record['delivery_id']),
            execution_id=p.get('execution_id'), filled_quantity=p.get('filled_quantity', 0),
            fill_ticks=p.get('fill_ticks'), reason='supplied F12 simulated boundary evidence')
        ledger.observe(message)
        result = ledger.state()
        state['journal'] = list(ledger.journal.read())
        state['ack_business'][p['ack_id']], state['last_economic'][p['order_id']] = business, identity
        state['states'][p['order_id']] = {'observed_state': p.get('state', 'acknowledged'),
                                        'kernel_state': result['orders'][p['order_id']]['state']}
        state['positions'] = dict(result['positions'])
        return state, [{'semantic': {'order_id': p['order_id'], **state['states'][p['order_id']],
                                     'positions': state['positions']},
                        'timing': {'availability_ordinal': at},
                        'transport': {'economic_known_at': p['economic_known_at'], 'simulated_boundary': True}}]
    from trading_research.operations.artifacts import canonical_json as kernel_json
    version = hashlib.sha256(kernel_json(['OrderLedger-observe-wrapper-v1', account_id, initial_orders, initial_events])).hexdigest()
    return CallbackSpec(id, version, frozenset({'order_ack'}), 'F12.OrderBoundaryState.v1', initial, _schema_transition(transition),
        semantic_projection=lambda s: {'states': s['states'], 'positions': s['positions'], 'incidents': s['incidents'], 'submissions': s['submissions']},
        projection_id='OrderLedger-state-and-position-v1')
