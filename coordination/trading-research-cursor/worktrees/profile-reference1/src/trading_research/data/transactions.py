"""F05 bounded immutable receipts, transaction revision chains and causal deltas.

This is an engineering ledger. Native condition/ownership certification remains
an explicit adapter input; raw source events and their existing IDs are unchanged.
"""
from dataclasses import asdict, dataclass, fields, replace
from decimal import Decimal
import hashlib
import json
from typing import Literal
from types import MappingProxyType

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.instruments import InstrumentDefinition
from trading_research.foundations.time import AvailabilityBasis, Clocks, timestamp
from trading_research.operations.artifacts import canonical_json, digest

SCHEMA = 'canonical-transactions-v1'


def _name(value):
    if not isinstance(value, str) or not value:
        raise ContractError('nonempty transaction identity required')
    return value


def _positive(value):
    if type(value) is not int or value <= 0:
        raise ContractError('positive integer bound or whole quantity required')
    return value


def _decimal(value):
    if value is not None and (not isinstance(value, Decimal) or not value.is_finite()):
        raise ContractError('finite exact Decimal or explicit missing value required')


@dataclass(frozen=True)
class TransactionKey:
    provider: str
    dataset: str
    publisher_or_venue: str | None
    channel: str | None
    source_session: str
    instrument_key: str
    ownership_id: str
    ownership_basis: Literal['provider_transaction', 'source_row']
    ownership_evidence_id: str

    def __post_init__(self):
        for value in (self.provider, self.dataset, self.source_session, self.instrument_key,
                      self.ownership_id, self.ownership_evidence_id):
            _name(value)
        for value in (self.publisher_or_venue, self.channel):
            if value is not None:
                _name(value)
        if self.ownership_basis not in ('provider_transaction', 'source_row'):
            raise ContractError('transaction ownership must have a declared evidence basis')

    @property
    def id(self):
        return digest(asdict(self))


@dataclass(frozen=True)
class TransactionValue:
    event_at: int
    price_decimal: Decimal | None
    price_ticks: int | None
    quantity: int
    quantity_unit: str
    reported_aggressor: int | None
    aggregation_unit: str
    instrument_kind: str
    terms_version: str
    usd_multiplier: Decimal | None
    money_role: str | None
    volume_eligibility: bool | None
    directional_eligibility: bool
    condition_contract_id: str
    raw_condition: str
    quality_reasons: tuple[str, ...]
    history_complete: bool
    source_order: int | None = None

    def __post_init__(self):
        timestamp(self.event_at)
        _positive(self.quantity)
        for value in (self.quantity_unit, self.aggregation_unit, self.terms_version,
                      self.condition_contract_id, self.raw_condition):
            _name(value)
        for value in (self.price_decimal, self.usd_multiplier):
            _decimal(value)
        if self.price_ticks is not None and type(self.price_ticks) is not int:
            raise ContractError('profile price must be exact ticks or missing')
        if self.reported_aggressor is not None and (type(self.reported_aggressor) is not int or self.reported_aggressor not in (-1, 1)):
            raise ContractError('reported aggressor is buy, sell or unknown')
        if self.volume_eligibility is not None and type(self.volume_eligibility) is not bool:
            raise ContractError('volume eligibility is true, false or unresolved')
        if type(self.directional_eligibility) is not bool or type(self.history_complete) is not bool:
            raise ContractError('direction and history eligibility need explicit booleans')
        if self.directional_eligibility and self.volume_eligibility is not True:
            raise ContractError('direction cannot be certified without volume eligibility')
        if not isinstance(self.quality_reasons, tuple) or any(not isinstance(v, str) or not v for v in self.quality_reasons):
            raise ContractError('quality reasons must be immutable named evidence')
        if self.source_order is not None and (type(self.source_order) is not int or self.source_order < 0):
            raise ContractError('source order is nonnegative or explicitly absent')
        units = {'futures_outright': 'contracts', 'single_option': 'contracts', 'equity': 'shares', 'spread': 'spread_units'}
        if units.get(self.instrument_kind) != self.quantity_unit:
            raise ContractError('instrument kind and quantity unit disagree')
        if (self.usd_multiplier is None) != (self.money_role is None):
            raise ContractError('money requires both multiplier and amount role')
        if self.usd_multiplier is not None:
            if self.usd_multiplier <= 0:
                raise ContractError('positive money multiplier required')
            _name(self.money_role)

    @property
    def unit_identity(self):
        return (self.quantity_unit, self.instrument_kind, self.aggregation_unit,
                self.terms_version, self.usd_multiplier, self.money_role)

    @property
    def side(self):
        return self.reported_aggressor if self.directional_eligibility else None

    def record(self):
        return {**asdict(self), 'price_decimal': None if self.price_decimal is None else str(self.price_decimal),
                'usd_multiplier': None if self.usd_multiplier is None else str(self.usd_multiplier)}

    @classmethod
    def restore(cls, row):
        return cls(**{**row, 'price_decimal': None if row['price_decimal'] is None else Decimal(row['price_decimal']),
                      'usd_multiplier': None if row['usd_multiplier'] is None else Decimal(row['usd_multiplier']),
                      'quality_reasons': tuple(row['quality_reasons'])})


@dataclass(frozen=True)
class TransactionReceipt:
    receipt_id: str
    source_event_id: str
    root_key: TransactionKey
    version_id: str
    predecessor_version_id: str | None
    operation: str
    clocks: Clocks
    source_address: str
    raw_payload_hash: str
    raw_payload: bytes
    value: TransactionValue | None
    condition_contract_id: str
    identity_evidence_id: str

    def __post_init__(self):
        for value in (self.receipt_id, self.source_event_id, self.version_id, self.source_address,
                      self.condition_contract_id, self.identity_evidence_id):
            _name(value)
        if not isinstance(self.root_key, TransactionKey) or not isinstance(self.clocks, Clocks):
            raise ContractError('receipt needs typed transaction ownership and clocks')
        if not isinstance(self.raw_payload, bytes) or hashlib.sha256(self.raw_payload).hexdigest() != self.raw_payload_hash:
            raise IntegrityError('receipt raw payload hash mismatch')
        if self.operation not in ('insert', 'revise', 'cancel'):
            raise ContractError('transaction operation is insert, revise or cancel')
        if self.predecessor_version_id is not None:
            _name(self.predecessor_version_id)
        if (self.operation == 'insert') != (self.predecessor_version_id is None):
            raise ContractError('only insert has no predecessor')
        if self.predecessor_version_id == self.version_id:
            raise ContractError('transaction cannot precede itself')
        if self.operation == 'cancel':
            if self.value is not None:
                raise ContractError('cancel has no replacement value')
        elif not isinstance(self.value, TransactionValue):
            raise ContractError('insert/revise needs a complete immutable value')
        if self.value is not None and self.value.condition_contract_id != self.condition_contract_id:
            raise ContractError('receipt and value condition versions disagree')

    def business_record(self):
        return {'root_key': asdict(self.root_key), 'version_id': self.version_id,
                'predecessor_version_id': self.predecessor_version_id, 'operation': self.operation,
                'value': None if self.value is None else self.value.record(),
                'condition_contract_id': self.condition_contract_id, 'identity_evidence_id': self.identity_evidence_id}

    def record(self):
        return {**self.business_record(), 'receipt_id': self.receipt_id, 'source_event_id': self.source_event_id,
                'clocks': asdict(self.clocks), 'source_address': self.source_address,
                'raw_payload_hash': self.raw_payload_hash, 'raw_payload_hex': self.raw_payload.hex()}

    @classmethod
    def restore(cls, row):
        c = row['clocks']
        return cls(**{k: v for k, v in row.items() if k not in ('root_key', 'clocks', 'value', 'raw_payload_hex')},
                   root_key=TransactionKey(**row['root_key']), clocks=Clocks(**{**c, 'basis': AvailabilityBasis(c['basis'])}),
                   raw_payload=bytes.fromhex(row['raw_payload_hex']),
                   value=None if row['value'] is None else TransactionValue.restore(row['value']))


@dataclass(frozen=True)
class TransactionDelta:
    root_key: TransactionKey
    operation: str
    cause_receipt_ids: tuple[str, ...]
    prior_version_id: str | None
    next_version_id: str
    before_value: TransactionValue | None
    after_value: TransactionValue | None
    known_at: int
    computed_at: int
    definition_version: str = SCHEMA
    batch_versions: tuple[str, ...] = ()
    batch_index: int = 0

    def __post_init__(self):
        timestamp(self.known_at); timestamp(self.computed_at)
        if self.batch_versions == ():
            object.__setattr__(self, 'batch_versions', (self.next_version_id,))
        if (not isinstance(self.batch_versions, tuple) or not self.batch_versions
                or any(not isinstance(v, str) or not v for v in self.batch_versions)
                or len(set(self.batch_versions)) != len(self.batch_versions)
                or type(self.batch_index) is not int or not 0 <= self.batch_index < len(self.batch_versions)
                or self.batch_versions[self.batch_index] != self.next_version_id):
            raise ContractError('delta needs ordered complete atomic resolution membership')
        _name(self.next_version_id); _name(self.definition_version)
        if self.prior_version_id is not None:
            _name(self.prior_version_id)
        if not isinstance(self.root_key, TransactionKey) or self.known_at < self.computed_at:
            raise ContractError('delta has invalid ownership/completion availability')
        if (not isinstance(self.cause_receipt_ids, tuple) or not self.cause_receipt_ids
                or len(set(self.cause_receipt_ids)) != len(self.cause_receipt_ids)):
            raise ContractError('delta needs unique immutable receipt evidence')
        for identity in self.cause_receipt_ids:
            _name(identity)
        for value in (self.before_value, self.after_value):
            if value is not None and not isinstance(value, TransactionValue):
                raise ContractError('delta before/after value must be immutable')
        valid = {'insert': self.prior_version_id is None and self.before_value is None and self.after_value is not None,
                 'revise': self.prior_version_id is not None and self.before_value is not None and self.after_value is not None,
                 'cancel': self.prior_version_id is not None and self.before_value is not None and self.after_value is None}
        if not valid.get(self.operation) or self.next_version_id == self.prior_version_id:
            raise ContractError('delta operation/predecessor/value mismatch')
        if self.before_value is not None and self.after_value is not None and self.before_value.unit_identity != self.after_value.unit_identity:
            raise ContractError('revision cannot change transaction units/contract terms')

    @property
    def batch_id(self):
        return digest((self.root_key.id, self.batch_versions, self.known_at,
                       self.computed_at, self.definition_version))

    @property
    def affected_event_intervals(self):
        return tuple(sorted({(v.event_at, timestamp(v.event_at + 1)) for v in (self.before_value, self.after_value) if v is not None}))

    @property
    def affected_fields(self):
        if self.before_value is None or self.after_value is None:
            return frozenset(f.name for f in fields(TransactionValue)) | {'lineage'}
        return frozenset(f.name for f in fields(TransactionValue)
                         if getattr(self.before_value, f.name) != getattr(self.after_value, f.name)) | {'lineage'}

    def payload(self):
        return {'root_key': asdict(self.root_key), 'operation': self.operation, 'cause_receipt_ids': self.cause_receipt_ids,
                'prior_version_id': self.prior_version_id, 'next_version_id': self.next_version_id,
                'before_value': None if self.before_value is None else self.before_value.record(),
                'after_value': None if self.after_value is None else self.after_value.record(),
                'known_at': self.known_at, 'computed_at': self.computed_at, 'definition_version': self.definition_version,
                'batch_versions': self.batch_versions, 'batch_index': self.batch_index,
                'affected_event_intervals': self.affected_event_intervals, 'affected_fields': sorted(self.affected_fields)}

    @property
    def id(self):
        return digest(self.payload())

    def record(self):
        return {'id': self.id, **self.payload()}

    @classmethod
    def restore(cls, row):
        result = cls(**{k: v for k, v in row.items() if k not in
                        ('id', 'root_key', 'cause_receipt_ids', 'batch_versions', 'before_value', 'after_value', 'affected_event_intervals', 'affected_fields')},
                     root_key=TransactionKey(**row['root_key']), cause_receipt_ids=tuple(row['cause_receipt_ids']),
                     batch_versions=tuple(row['batch_versions']),
                     before_value=None if row['before_value'] is None else TransactionValue.restore(row['before_value']),
                     after_value=None if row['after_value'] is None else TransactionValue.restore(row['after_value']))
        if canonical_json(result.record()) != canonical_json(row):
            raise IntegrityError('delta hash, support or field record is inconsistent')
        return result


@dataclass(frozen=True)
class Admission:
    status: str
    receipt_id: str
    pending_version_ids: tuple[str, ...]
    deltas: tuple[TransactionDelta, ...]
    committed_at: int


@dataclass(frozen=True)
class ResolvedTransaction:
    root_key: TransactionKey
    version_id: str
    version_hash: str
    value: TransactionValue
    known_at: int


class TransactionLedger:
    """Atomic bounded engineering state; durable source input is owned by F04."""
    def __init__(self, *, max_records=4096, max_bytes=8 * 1024**2, max_pending=256,
                 max_resolution_deltas=256, definition_version=SCHEMA):
        for value in (max_records, max_bytes, max_pending, max_resolution_deltas):
            _positive(value)
        _name(definition_version)
        self._config = MappingProxyType({'max_records': max_records, 'max_bytes': max_bytes, 'max_pending': max_pending,
                       'max_resolution_deltas': max_resolution_deltas, 'definition_version': definition_version})
        self._receipts = {}
        self._versions = {}
        self._successors = {}
        self._inserts = {}
        self._heads = {}
        self._pending = set()
        self._deltas = ()
        self._last_input_known = None
        self._last_commit = None

    @property
    def config(self):
        return self._config

    def _state(self):
        return {'receipts': [{'receipt': r.record(), 'completion_at': at} for r, at in self._receipts.values()],
                'versions': {id: {'receipt_id': r.receipt_id, 'business_hash': digest(r.business_record())}
                             for id, r in sorted(self._versions.items())},
                'successors': dict(sorted(self._successors.items())), 'inserts': dict(sorted(self._inserts.items())),
                'heads': dict(sorted(self._heads.items())), 'pending': sorted(self._pending),
                'deltas': [d.record() for d in self._deltas],
                'last_input_known': self._last_input_known, 'last_commit': self._last_commit}

    def metrics(self):
        records = sum(map(len, (self._receipts, self._versions, self._successors, self._inserts,
                               self._heads, self._pending, self._deltas)))
        return {'retained_records': records, 'retained_envelope_bytes': len(canonical_json(self._state())),
                'pending_versions': len(self._pending), 'receipt_count': len(self._receipts),
                'version_count': len(self._versions), 'delta_count': len(self._deltas)}

    def _check_bounds(self):
        m = self.metrics()
        if (m['retained_records'] > self.config['max_records'] or m['retained_envelope_bytes'] > self.config['max_bytes']
                or m['pending_versions'] > self.config['max_pending']):
            raise ContractError('transaction retained record/byte/pending bound reached; explicit backpressure required')

    def _fork(self):
        candidate = TransactionLedger(**self.config)
        for name in ('_receipts', '_versions', '_successors', '_inserts', '_heads'):
            setattr(candidate, name, dict(getattr(self, name)))
        candidate._pending = set(self._pending)
        candidate._deltas = self._deltas
        candidate._last_input_known, candidate._last_commit = self._last_input_known, self._last_commit
        return candidate

    def admit(self, receipt: TransactionReceipt, *, actual_completion_at: int) -> Admission:
        timestamp(actual_completion_at)
        if not isinstance(receipt, TransactionReceipt):
            raise ContractError('typed immutable transaction receipt required')
        old = self._receipts.get(receipt.receipt_id)
        if old is not None:
            if old[0] != receipt:
                raise IntegrityError('receipt ID reused with different bytes/content')
            return Admission('duplicate_receipt', receipt.receipt_id, tuple(sorted(self._pending)), (), old[1])
        if (actual_completion_at < receipt.clocks.known_at
                or self._last_input_known is not None and receipt.clocks.known_at < self._last_input_known
                or self._last_commit is not None and actual_completion_at < self._last_commit):
            raise ContractError('receipt/completion regressed; do not backdate late input')
        candidate = self._fork()
        candidate._receipts[receipt.receipt_id] = (receipt, actual_completion_at)
        candidate._last_input_known, candidate._last_commit = receipt.clocks.known_at, actual_completion_at
        prior_version = candidate._versions.get(receipt.version_id)
        if prior_version is not None:
            if prior_version.business_record() != receipt.business_record():
                raise IntegrityError('immutable revision ID content or identity evidence changed')
            emitted = ()
            status = 'duplicate_version'
        else:
            candidate._install_version(receipt)
            emitted = candidate._resolve(receipt, actual_completion_at)
            status = 'committed' if emitted else 'pending_dependency'
        candidate._check_bounds()
        self.__dict__.update(candidate.__dict__)
        return Admission(status, receipt.receipt_id, tuple(sorted(self._pending)), emitted, actual_completion_at)

    def _install_version(self, receipt):
        id, root, previous = receipt.version_id, receipt.root_key.id, receipt.predecessor_version_id
        if receipt.operation == 'insert':
            if root in self._inserts:
                raise IntegrityError('second insertion of existing transaction root')
            self._inserts[root] = id
        elif previous in self._successors:
            raise IntegrityError('transaction predecessor has conflicting successors')
        else:
            self._successors[previous] = id
        self._versions[id] = receipt
        self._pending.add(id)
        # Validate known and formerly pending edges, including an introduced cycle.
        for version, row in self._versions.items():
            parent = self._versions.get(row.predecessor_version_id)
            if parent is not None:
                if parent.root_key != row.root_key:
                    raise ContractError('transaction predecessor belongs to another root')
                if parent.operation == 'cancel':
                    raise ContractError('terminal transaction cancellation cannot be revised')
            seen, cursor = set(), version
            while cursor in self._versions:
                if cursor in seen:
                    raise ContractError('transaction predecessor cycle')
                seen.add(cursor)
                cursor = self._versions[cursor].predecessor_version_id
        identities = {row.value.unit_identity for row in self._versions.values()
                      if row.root_key.id == root and row.value is not None}
        if len(identities) > 1:
            raise ContractError('transaction revision changes instrument units/terms')

    def _resolve(self, trigger, at):
        root = trigger.root_key.id
        head = self._heads.get(root)
        current = self._inserts.get(root) if head is None else self._successors.get(head)
        emitted = []
        while current is not None and current in self._versions and current in self._pending:
            if len(emitted) >= self.config['max_resolution_deltas']:
                raise ContractError('pending chain exceeds atomic materialization bound')
            row = self._versions[current]
            previous = self._versions.get(head)
            before = previous.value if previous is not None else None
            causes = tuple(sorted({trigger.receipt_id, row.receipt_id, *([previous.receipt_id] if previous is not None else [])}))
            delta = TransactionDelta(row.root_key, row.operation, causes, head, row.version_id, before, row.value,
                                     at, at, self.config['definition_version'])
            emitted.append(delta)
            self._pending.remove(current)
            self._heads[root] = current
            head, current = current, self._successors.get(current)
        members = tuple(d.next_version_id for d in emitted)
        emitted = [replace(d, batch_versions=members, batch_index=i) for i, d in enumerate(emitted)]
        self._deltas += tuple(emitted)
        return tuple(emitted)

    @property
    def deltas(self):
        return self._deltas

    def pending(self, *, cut: int | None = None):
        if cut is None:
            return tuple(sorted(self._pending))
        timestamp(cut)
        admitted = {r.version_id for r, at in self._receipts.values() if at <= cut}
        resolved = {d.next_version_id for d in self._deltas if d.known_at <= cut}
        return tuple(sorted(admitted - resolved))

    def asof(self, *, instrument: str, cut: int, start: int | None = None, end: int | None = None):
        timestamp(cut); _name(instrument)
        for at in (start, end):
            if at is not None:
                timestamp(at)
        if start is not None and end is not None and start >= end:
            raise ContractError('transaction window must be nonempty and half-open')
        live = {}
        for delta in self._deltas:
            if delta.known_at <= cut and delta.root_key.instrument_key == instrument:
                if delta.after_value is None:
                    live.pop(delta.root_key.id, None)
                else:
                    row = self._versions[delta.next_version_id]
                    live[delta.root_key.id] = ResolvedTransaction(delta.root_key, delta.next_version_id,
                                                                digest(row.business_record()), delta.after_value, delta.known_at)
        return tuple(r for _, r in sorted(live.items()) if (start is None or r.value.event_at >= start)
                     and (end is None or r.value.event_at < end))

    def changes(self, *, instrument: str, cut: int, start: int, end: int):
        timestamp(cut); timestamp(start); timestamp(end)
        if start >= end:
            raise ContractError('correction-impact interval must be nonempty')
        return tuple(d for d in self._deltas if d.root_key.instrument_key == instrument and d.known_at <= cut
                     and d.operation != 'insert' and any(v is not None and start <= v.event_at < end
                                                       for v in (d.before_value, d.after_value)))

    def checkpoint(self):
        return canonical_json({'schema': SCHEMA, 'config': dict(self.config), 'state': self._state(), 'metrics': self.metrics()})

    @classmethod
    def restore(cls, payload: bytes):
        try:
            row = json.loads(payload)
            if row['schema'] != SCHEMA:
                raise ContractError('unknown transaction ledger checkpoint schema')
            result = cls(**row['config'])
            for entry in row['state']['receipts']:
                result.admit(TransactionReceipt.restore(entry['receipt']), actual_completion_at=entry['completion_at'])
            if result.checkpoint() != payload:
                raise IntegrityError('transaction checkpoint lineage/arithmetic/counters are inconsistent')
            return result
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            if isinstance(exc, ContractError):
                raise
            raise IntegrityError('malformed transaction checkpoint') from exc


@dataclass(frozen=True)
class ConditionRule:
    code: str
    volume_eligible: bool
    directional_eligible: bool
    reason: str

    def __post_init__(self):
        _name(self.code); _name(self.reason)
        if type(self.volume_eligible) is not bool or type(self.directional_eligible) is not bool or (self.directional_eligible and not self.volume_eligible):
            raise ContractError('condition rule needs explicit compatible eligibility booleans')


@dataclass(frozen=True)
class ConditionDecision:
    contract_id: str
    code: str
    volume_eligible: bool | None
    directional_eligible: bool
    reason: str


@dataclass(frozen=True)
class ConditionContract:
    provider: str
    schema_version: str
    effective_start: int
    effective_end: int
    evidence_id: str
    rules: tuple[ConditionRule, ...]
    synthetic: bool

    def __post_init__(self):
        for value in (self.provider, self.schema_version, self.evidence_id):
            _name(value)
        timestamp(self.effective_start); timestamp(self.effective_end)
        if self.effective_start >= self.effective_end or type(self.synthetic) is not bool:
            raise ContractError('condition contract needs a dated domain and explicit synthetic status')
        if (not isinstance(self.rules, tuple) or any(not isinstance(r, ConditionRule) for r in self.rules)
                or len({r.code for r in self.rules}) != len(self.rules)):
            raise ContractError('condition table needs unique immutable rules')
        if self.synthetic and not self.provider.startswith('synthetic'):
            raise ContractError('synthetic condition rules cannot claim native provider certification')

    @property
    def id(self):
        return digest(asdict(self))

    def decide(self, code: str, *, event_at: int):
        timestamp(event_at); _name(code)
        if not self.effective_start <= event_at < self.effective_end:
            raise ContractError('condition table has no certification at this event date')
        rule = next((r for r in self.rules if r.code == code), None)
        return ConditionDecision(self.id, code, rule.volume_eligible if rule else None,
                                 rule.directional_eligible if rule else False,
                                 rule.reason if rule else 'unresolved_condition_contract')


@dataclass(frozen=True)
class NonTransaction:
    source_event_id: str
    reason: str
    observed_size: int | None


@dataclass(frozen=True)
class MBPInstrumentMapping:
    """Explicit dataset-to-definition evidence; no absent exchange fields inferred."""
    dataset_id: str
    schema_version: str
    definition: InstrumentDefinition
    evidence_id: str

    def __post_init__(self):
        for text in (self.dataset_id, self.schema_version, self.evidence_id):
            _name(text)
        if not isinstance(self.definition, InstrumentDefinition):
            raise ContractError('MBP mapping requires an immutable instrument definition')
        if self.definition.classification != 'future':
            raise ContractError('MBP futures adapter requires an outright future definition')

    @property
    def id(self):
        return digest(asdict(self))


def transaction_from_mbp(event, *, root_key: TransactionKey, mapping: MBPInstrumentMapping, terms, instrument_kind: str,
                         money_role: str, condition_contract: ConditionContract, condition_code: str,
                         order: int | None, history_complete: bool):
    """Wrap already decoded MBP; do not change its ID or infer correction targets."""
    from trading_research.data.events import CanonicalEvent, Flags
    from trading_research.foundations.units import FuturesTerms
    from trading_research.foundations.instruments import instrument_identity
    if (not isinstance(event, CanonicalEvent) or not isinstance(terms, FuturesTerms)
            or not isinstance(condition_contract, ConditionContract) or not isinstance(root_key, TransactionKey)
            or not isinstance(mapping, MBPInstrumentMapping)):
        raise ContractError('typed decoded event, mapping, terms and dated condition contract required')
    # source_session is the observed acquisition scope here, not an inferred
    # exchange session. The decoder has no channel field, so channel stays absent.
    definition = mapping.definition
    expected_publisher = None if event.publisher_id is None else str(event.publisher_id)
    if (mapping.dataset_id != event.address.dataset_id or mapping.schema_version != event.address.schema_version
            or definition.key.provider != root_key.provider
            or definition.key.instrument_id != str(event.instrument_id)
            or root_key.instrument_key != instrument_identity(definition)
            or root_key.publisher_or_venue != expected_publisher or root_key.channel is not None
            or root_key.source_session != event.address.acquisition_version
            or instrument_kind != 'futures_outright' or terms != definition.futures_terms()
            or definition.clocks.known_at > event.clocks.known_at
            or not definition.clocks.valid_from <= event.clocks.event_at < definition.clocks.valid_until
            or definition.key.expiry_at is not None and event.clocks.event_at >= definition.key.expiry_at
            or order != event.provider_sequence):
        raise ContractError('MBP raw instrument, publisher, acquisition scope, order or definition terms disagree')
    if (root_key.provider != condition_contract.provider or event.address.schema_version != condition_contract.schema_version
            or root_key.dataset != event.address.dataset_id or (root_key.ownership_basis == 'source_row' and root_key.ownership_id != event.address.id)):
        raise ContractError('condition/ownership evidence does not match decoded source scope')
    if event.action != 'T':
        return NonTransaction(event.id, 'non_trade_action' if event.action is not None else 'unknown_action', event.size)
    if event.flags & Flags.SNAPSHOT:
        return NonTransaction(event.id, 'snapshot_initialization', event.size)
    if event.size is None or event.size <= 0:
        raise ContractError('invalid outright transaction size')
    decision = condition_contract.decide(condition_code, event_at=event.clocks.event_at)
    try:
        ticks = None if event.price is None else terms.ticks(event.price).value
    except ContractError:
        ticks = None
    value = TransactionValue(event.clocks.event_at, event.price, ticks, event.size, 'contracts', event.aggressor,
                             'provider-reported-trade-record', instrument_kind, terms.definition_version,
                             terms.usd_per_point, money_role, decision.volume_eligible, decision.directional_eligible,
                             decision.contract_id, decision.code, (*event.quality_reasons, decision.reason),
                             history_complete and not bool(event.flags & Flags.MAYBE_BAD_BOOK), order)
    raw = canonical_json({'raw_fields_hex': event.raw_fields.hex(),
                          'raw_record_hex': None if event.raw_record is None else event.raw_record.hex(),
                          'instrument_mapping_id': mapping.id, 'instrument_mapping': asdict(mapping)})
    return TransactionReceipt(event.id, event.id, root_key, event.address.id, None, 'insert', event.clocks,
                              canonical_json(asdict(event.address)).decode(), hashlib.sha256(raw).hexdigest(), raw,
                              value, condition_contract.id, root_key.ownership_evidence_id)
