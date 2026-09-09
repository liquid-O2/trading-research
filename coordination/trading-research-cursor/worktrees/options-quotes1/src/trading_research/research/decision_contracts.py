"""B00.6 exact reward composition and bounded evidence-admission contracts.

These utilities consume explicit synthetic/evaluated state; they neither fill
orders, model a policy nor infer an open-interest posterior.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import re

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.time import timestamp

SCHEMA = 'decision-contracts-v1'
MAX_FEE_INPUT_OCCURRENCES = 4096


def _name(value):
    if type(value) is not str or not value or len(value.encode()) > 256:
        raise ContractError('bounded nonempty immutable identity required')


def _signature(value):
    if type(value) is not str or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise ContractError('exact immutable Target.signature required')


def _fraction(value, *, nonnegative=False):
    if type(value) is not Fraction or nonnegative and value < 0:
        raise ContractError('exact Fraction USD required')


def _limit(value, maximum):
    if type(value) is not int or not 0 < value <= maximum:
        raise ContractError('positive configured limit exceeds finite contract')


def _tuple(value, cls, maximum, *, nonempty=False):
    if (type(value) is not tuple or len(value) > maximum or nonempty and not value
            or any(type(v) is not cls for v in value)):
        raise ContractError('bounded immutable typed tuple required')


def _ids(values, maximum=256, *, nonempty=False):
    _tuple(values, str, maximum, nonempty=nonempty)
    for value in values:
        _name(value)
    if len(set(values)) != len(values):
        raise ContractError('duplicate immutable identity')


class RecordValue:
    def record(self):
        spec = _SCHEMAS[type(self)]
        return {'schema': SCHEMA, 'type': type(self).__name__,
                'fields': {name: _encode(getattr(self, name)) for name in spec}}

    @property
    def version(self):
        raw = json.dumps(self.record(), sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
        return hashlib.sha256(raw).hexdigest()

    @classmethod
    def from_record(cls, record):
        return cls(**_record_fields(cls, record))


@dataclass(frozen=True)
class FeeCharge(RecordValue):
    id: str
    amount_usd: Fraction

    def __post_init__(self):
        _name(self.id); _fraction(self.amount_usd, nonnegative=True)


@dataclass(frozen=True)
class RewardDomain(RecordValue):
    account_id: str
    raw_definition_id: str
    scenario_id: str
    reward_basis: str
    common_boundary: int

    def __post_init__(self):
        for value in (self.account_id, self.raw_definition_id, self.scenario_id, self.reward_basis):
            _name(value)
        timestamp(self.common_boundary)


@dataclass(frozen=True)
class NetMark(RecordValue):
    at: int
    domain: RewardDomain
    gross_marked_usd: Fraction
    charges: tuple[FeeCharge, ...]
    max_fee_ids: int = 256

    def __post_init__(self):
        timestamp(self.at); _fraction(self.gross_marked_usd); _limit(self.max_fee_ids, 256)
        if type(self.domain) is not RewardDomain or self.at > self.domain.common_boundary:
            raise ContractError('mark belongs to an explicit common-boundary domain')
        _tuple(self.charges, FeeCharge, MAX_FEE_INPUT_OCCURRENCES)
        fees = {}
        for charge in self.charges:
            if charge.id in fees and fees[charge.id] != charge:
                raise ContractError('fee ID changed amount')
            fees[charge.id] = charge
        if len(fees) > self.max_fee_ids:
            raise ContractError('unique cash fee bound exceeded')
        object.__setattr__(self, 'charges', tuple(fees[key] for key in sorted(fees)))

    @property
    def charged_fees(self):
        return sum((fee.amount_usd for fee in self.charges), Fraction(0))

    @property
    def net_marked_usd(self):
        return self.gross_marked_usd - self.charged_fees


def _mark_values(marks, max_marks, max_fee_ids):
    _limit(max_marks, 64); _limit(max_fee_ids, 256)
    _tuple(marks, NetMark, max_marks)
    if len(marks) < 2:
        raise ContractError('at least two exact marks required')
    prior = None
    history = {}
    for mark in marks:
        if mark.domain != marks[0].domain or mark.max_fee_ids != max_fee_ids:
            raise ContractError('mark domain or configured fee bound changed')
        if prior is not None and mark.at <= prior.at:
            raise ContractError('marks must be strictly increasing')
        current = {fee.id: fee.amount_usd for fee in mark.charges}
        if any(current.get(key) != amount for key, amount in history.items()):
            raise ContractError('previous fee was lost or changed')
        if len(current) > max_fee_ids:
            raise ContractError('cash fee union exceeds bound')
        history = current; prior = mark
    net = tuple(mark.net_marked_usd for mark in marks)
    increments = tuple(b-a for a, b in zip(net, net[1:]))
    return increments, net[-1]-net[0], marks[-1].charged_fees, marks[-1].charged_fees-marks[0].charged_fees


@dataclass(frozen=True)
class IncrementalRewards(RecordValue):
    marks: tuple[NetMark, ...]
    increments: tuple[Fraction, ...]
    net_change: Fraction
    cumulative_charged_fees: Fraction
    interval_new_fees: Fraction
    max_marks: int = 64
    max_fee_ids: int = 256

    def __post_init__(self):
        expected = _mark_values(self.marks, self.max_marks, self.max_fee_ids)
        _tuple(self.increments, Fraction, 63)
        for value in (self.net_change, self.cumulative_charged_fees, self.interval_new_fees):
            _fraction(value)
        if expected != (self.increments, self.net_change, self.cumulative_charged_fees, self.interval_new_fees):
            raise ContractError('derived reward arithmetic does not match exact marks')

    @property
    def net_marks(self):
        return tuple(mark.net_marked_usd for mark in self.marks)

    @classmethod
    def from_record(cls, record, *, max_marks=64, max_fee_ids=256):
        _limit(max_marks, 64); _limit(max_fee_ids, 256)
        values = _record_fields(cls, record)
        if (values['max_marks'], values['max_fee_ids']) != (max_marks, max_fee_ids):
            raise ContractError('restored mark/fee limits changed')
        return incremental_rewards(**values)


def incremental_rewards(marks, *, max_marks=64, max_fee_ids=256):
    return IncrementalRewards(marks, *_mark_values(marks, max_marks, max_fee_ids), max_marks, max_fee_ids)


@dataclass(frozen=True)
class RewardState(RecordValue):
    at: int
    domain: RewardDomain
    state_version: str
    position: int
    pending_order: bool

    def __post_init__(self):
        timestamp(self.at); _name(self.state_version)
        if (type(self.domain) is not RewardDomain or type(self.position) is not int
                or self.position not in (-1, 0, 1) or type(self.pending_order) is not bool):
            raise ContractError('exact account state/domain and position/pending flag required')


@dataclass(frozen=True)
class RewardSegment(RecordValue):
    id: str
    initial: RewardState
    terminal: RewardState
    net_increment_usd: Fraction
    fee_ids: tuple[str, ...]

    def __post_init__(self):
        _name(self.id); _fraction(self.net_increment_usd); _ids(self.fee_ids)
        if (type(self.initial) is not RewardState or type(self.terminal) is not RewardState
                or self.initial.domain != self.terminal.domain
                or not self.initial.at < self.terminal.at <= self.initial.domain.common_boundary):
            raise ContractError('segment needs one domain and increasing endpoints before boundary')

    @property
    def domain(self):
        return self.initial.domain


def _segment_values(segments, max_segments, max_fee_ids):
    _limit(max_segments, 64); _limit(max_fee_ids, 256)
    _tuple(segments, RewardSegment, max_segments, nonempty=True)
    seen, fees = set(), set()
    prior = None
    for segment in segments:
        if segment.id in seen or segment.domain != segments[0].domain:
            raise ContractError('duplicate segment or changed reward domain')
        if prior is not None and prior.terminal != segment.initial:
            raise ContractError('continuation does not start in exact terminal state')
        if fees.intersection(segment.fee_ids):
            raise ContractError('same cash fee charged in multiple reward segments')
        seen.add(segment.id); fees.update(segment.fee_ids); prior = segment
        if len(fees) > max_fee_ids:
            raise ContractError('segment cash fee union exceeds bound')
    return segments[0].initial, segments[-1].terminal, sum((s.net_increment_usd for s in segments), Fraction(0)), tuple(sorted(fees))


@dataclass(frozen=True)
class RewardComposition(RecordValue):
    segments: tuple[RewardSegment, ...]
    initial: RewardState
    terminal: RewardState
    net_increment_usd: Fraction
    fee_ids: tuple[str, ...]
    max_segments: int = 64
    max_fee_ids: int = 256

    def __post_init__(self):
        expected = _segment_values(self.segments, self.max_segments, self.max_fee_ids)
        _fraction(self.net_increment_usd); _ids(self.fee_ids, self.max_fee_ids)
        if expected != (self.initial, self.terminal, self.net_increment_usd, self.fee_ids):
            raise ContractError('derived reward composition differs from exact segments')

    @classmethod
    def from_record(cls, record, *, max_segments=64, max_fee_ids=256):
        _limit(max_segments, 64); _limit(max_fee_ids, 256)
        values = _record_fields(cls, record)
        if (values['max_segments'], values['max_fee_ids']) != (max_segments, max_fee_ids):
            raise ContractError('restored segment/fee limits changed')
        return compose_rewards(**values)


def compose_rewards(segments, *, max_segments=64, max_fee_ids=256):
    return RewardComposition(segments, *_segment_values(segments, max_segments, max_fee_ids), max_segments, max_fee_ids)


def compare_complete_rewards(left, right):
    if type(left) is not RewardComposition or type(right) is not RewardComposition:
        raise ContractError('two exact reward compositions required')
    if left.initial != right.initial:
        raise ContractError('paired policies must share one exact initial account state')
    for value in (left, right):
        if (value.terminal.at != value.initial.domain.common_boundary
                or value.terminal.position != 0 or value.terminal.pending_order):
            raise DependencyUnavailable('complete flat/no-pending common boundary not reached')
    return left.net_increment_usd - right.net_increment_usd


@dataclass(frozen=True)
class EvidenceSeed(RecordValue):
    target_signature: str
    atoms: tuple[str, ...]
    known_at: int
    likelihood_contract: str

    def __post_init__(self):
        _signature(self.target_signature); _ids(self.atoms); timestamp(self.known_at)
        _name(self.likelihood_contract)


@dataclass(frozen=True)
class EvidenceFactor(RecordValue):
    id: str
    target_signature: str
    atoms: tuple[str, ...]
    payload_version: str
    known_at: int
    likelihood_contract: str | None

    def __post_init__(self):
        _name(self.id); _signature(self.target_signature); _ids(self.atoms, nonempty=True)
        _name(self.payload_version); timestamp(self.known_at)
        if self.likelihood_contract is not None:
            _name(self.likelihood_contract)


@dataclass(frozen=True)
class EvidenceAdmission(RecordValue):
    factor: EvidenceFactor
    outcome: str
    admitted_at: int

    def __post_init__(self):
        if type(self.factor) is not EvidenceFactor or self.outcome not in ('accepted', 'redundant_evidence'):
            raise ContractError('retained admission must bind a typed factor and recognized outcome')
        timestamp(self.admitted_at)
        if self.admitted_at < self.factor.known_at:
            raise ContractError('admission predates available factor')


def _factor_outcome(seed, consumed, factor):
    if factor.target_signature != seed.target_signature:
        raise ContractError('factor changed immutable target signature')
    if factor.likelihood_contract is None or factor.likelihood_contract != seed.likelihood_contract:
        raise DependencyUnavailable('explicit compatible conditional likelihood unavailable')
    atoms = set(factor.atoms)
    overlap = atoms & consumed
    if overlap == atoms:
        return 'redundant_evidence'
    if overlap:
        raise DependencyUnavailable('partial evidence overlap requires a coherent conditional factor')
    return 'accepted'


def _ledger_values(seed, seen_factors, max_factors, max_atoms):
    _limit(max_factors, 64); _limit(max_atoms, 256)
    if type(seed) is not EvidenceSeed or len(seed.atoms) > max_atoms:
        raise ContractError('bounded typed seed state required')
    _tuple(seen_factors, EvidenceAdmission, max_factors)
    consumed = set(seed.atoms); seen = set(); accepted = []; known = seed.known_at
    for entry in seen_factors:
        factor = entry.factor
        if factor.id in seen or entry.admitted_at < known or len(factor.atoms) > max_atoms:
            raise ContractError('duplicate factor binding, backdated ledger or atom bound')
        try:
            outcome = _factor_outcome(seed, consumed, factor)
        except DependencyUnavailable as exc:
            raise ContractError('restored ledger has unavailable likelihood/lineage') from exc
        if outcome != entry.outcome:
            raise ContractError('stored admission outcome disagrees with replayed lineage')
        if outcome == 'accepted':
            consumed.update(factor.atoms); accepted.append(factor)
        if len(consumed) > max_atoms:
            raise ContractError('consumed evidence union exceeds bound')
        seen.add(factor.id); known = entry.admitted_at
    return known, tuple(sorted(consumed)), tuple(accepted)


@dataclass(frozen=True)
class EvidenceLedger(RecordValue):
    seed: EvidenceSeed
    seen_factors: tuple[EvidenceAdmission, ...] = ()
    known_at: int | None = None
    max_factors: int = 64
    max_atoms: int = 256

    def __post_init__(self):
        known, _, _ = _ledger_values(self.seed, self.seen_factors, self.max_factors, self.max_atoms)
        if self.known_at is None:
            object.__setattr__(self, 'known_at', known)
        else:
            timestamp(self.known_at)
            if self.known_at != known:
                raise ContractError('ledger knowledge clock differs from replayed seed/admissions')

    @property
    def target_signature(self):
        return self.seed.target_signature

    @property
    def likelihood_contract(self):
        return self.seed.likelihood_contract

    @property
    def consumed_atoms(self):
        return _ledger_values(self.seed, self.seen_factors, self.max_factors, self.max_atoms)[1]

    @property
    def accepted_factors(self):
        return _ledger_values(self.seed, self.seen_factors, self.max_factors, self.max_atoms)[2]

    @classmethod
    def from_record(cls, record, *, expected_target_signature, expected_likelihood_contract,
                    max_factors=64, max_atoms=256):
        _limit(max_factors, 64); _limit(max_atoms, 256)
        _signature(expected_target_signature); _name(expected_likelihood_contract)
        values = _record_fields(cls, record)
        if (values['seed'].target_signature != expected_target_signature
                or values['seed'].likelihood_contract != expected_likelihood_contract
                or (values['max_factors'], values['max_atoms']) != (max_factors, max_atoms)):
            raise ContractError('restored evidence target/likelihood/limits changed')
        return cls(**values)


def admit_evidence(ledger, factor, *, cut):
    if type(ledger) is not EvidenceLedger or type(factor) is not EvidenceFactor:
        raise ContractError('typed immutable ledger and factor required')
    timestamp(cut)
    if cut < ledger.known_at or cut < factor.known_at:
        raise DependencyUnavailable('future evidence or backdated conditioned ledger')
    if factor.target_signature != ledger.target_signature:
        raise ContractError('factor changed target signature')
    if factor.likelihood_contract is None or factor.likelihood_contract != ledger.likelihood_contract:
        raise DependencyUnavailable('explicit compatible likelihood unavailable')
    for entry in ledger.seen_factors:
        if entry.factor.id == factor.id:
            if entry.factor != factor:
                raise ContractError('same factor ID changed immutable content')
            return ledger, 'duplicate'
    if len(ledger.seen_factors) >= ledger.max_factors or len(factor.atoms) > ledger.max_atoms:
        raise ContractError('seen factor or evidence atom bound exceeded')
    outcome = _factor_outcome(ledger.seed, set(ledger.consumed_atoms), factor)
    if outcome == 'accepted' and len(set(ledger.consumed_atoms) | set(factor.atoms)) > ledger.max_atoms:
        raise ContractError('consumed evidence union exceeds bound')
    entry = EvidenceAdmission(factor, outcome, cut)
    return EvidenceLedger(ledger.seed, ledger.seen_factors + (entry,), cut,
                          ledger.max_factors, ledger.max_atoms), outcome


# Exact source-only records; derived totals/lineage are reconstructed, not trusted.
_SCHEMAS = {
    FeeCharge: {'id': str, 'amount_usd': Fraction},
    RewardDomain: {'account_id': str, 'raw_definition_id': str, 'scenario_id': str,
                   'reward_basis': str, 'common_boundary': int},
    NetMark: {'at': int, 'domain': RewardDomain, 'gross_marked_usd': Fraction,
              'charges': (FeeCharge,), 'max_fee_ids': int},
    IncrementalRewards: {'marks': (NetMark,), 'max_marks': int, 'max_fee_ids': int},
    RewardState: {'at': int, 'domain': RewardDomain, 'state_version': str, 'position': int, 'pending_order': bool},
    RewardSegment: {'id': str, 'initial': RewardState, 'terminal': RewardState,
                    'net_increment_usd': Fraction, 'fee_ids': (str,)},
    RewardComposition: {'segments': (RewardSegment,), 'max_segments': int, 'max_fee_ids': int},
    EvidenceSeed: {'target_signature': str, 'atoms': (str,), 'known_at': int, 'likelihood_contract': str},
    EvidenceFactor: {'id': str, 'target_signature': str, 'atoms': (str,), 'payload_version': str,
                     'known_at': int, 'likelihood_contract': (str, type(None))},
    EvidenceAdmission: {'factor': EvidenceFactor, 'outcome': str, 'admitted_at': int},
    EvidenceLedger: {'seed': EvidenceSeed, 'seen_factors': (EvidenceAdmission,), 'known_at': int,
                     'max_factors': int, 'max_atoms': int},
}


def _encode(value):
    if type(value) is Fraction:
        return [value.numerator, value.denominator]
    if type(value) in _SCHEMAS:
        return value.record()
    if type(value) is tuple:
        return [_encode(v) for v in value]
    if value is None or type(value) in (str, int, bool):
        return value
    raise ContractError('unsupported immutable record value')


def _decode(spec, value):
    if spec is Fraction:
        if (type(value) is not list or len(value) != 2 or any(type(n) is not int for n in value)
                or value[1] <= 0):
            raise ContractError('canonical reduced rational pair required')
        result = Fraction(*value)
        if [result.numerator, result.denominator] != value:
            raise ContractError('rational record is not reduced')
        return result
    if type(spec) is tuple:
        if len(spec) == 1:
            if type(value) is not list or len(value) > 256:
                raise ContractError('bounded record array required')
            return tuple(_decode(spec[0], item) for item in value)
        if value is None:
            return None
        return _decode(spec[0], value)
    if spec in _SCHEMAS:
        return spec.from_record(value)
    if type(value) is not spec:
        raise ContractError('record scalar type mismatch')
    return value


def _record_fields(cls, record):
    if (type(record) is not dict or set(record) != {'schema', 'type', 'fields'}
            or record['schema'] != SCHEMA or record['type'] != cls.__name__
            or type(record['fields']) is not dict or set(record['fields']) != set(_SCHEMAS[cls])):
        raise ContractError('exact schema/type/source-field record required')
    return {name: _decode(spec, record['fields'][name]) for name, spec in _SCHEMAS[cls].items()}
