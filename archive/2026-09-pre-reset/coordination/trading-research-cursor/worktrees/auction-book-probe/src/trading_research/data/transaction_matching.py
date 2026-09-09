"""Bounded cross-source candidate graphs; similarity never certifies ownership."""
from dataclasses import asdict, dataclass, field
import re

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest


@dataclass(frozen=True)
class MatchObservation:
    id: str
    source_row_id: str
    source_identity_evidence: str
    raw_hash: str
    schema_version: str
    instrument: str
    event_start: int
    event_end: int
    known_at: int
    price_key: str | None
    quantity: int
    reported_side: int | None
    condition: str | None
    aggregation_unit: str
    quantity_unit: str
    price_unit: str
    kind: str = 'trade'
    source_order: int | None = None

    def __post_init__(self):
        for value in (self.id, self.source_row_id, self.source_identity_evidence, self.schema_version,
                      self.instrument, self.aggregation_unit, self.quantity_unit, self.price_unit):
            if not isinstance(value, str) or not value:
                raise ContractError('matching requires explicit source identity, schema and units')
        for value in (self.event_start, self.event_end, self.known_at):
            timestamp(value)
        if self.event_start >= self.event_end or type(self.quantity) is not int or self.quantity < 0:
            raise ContractError('matching needs a nonempty time precision interval and nonnegative size')
        if self.kind not in ('trade', 'snapshot', 'book') or self.kind == 'trade' and self.quantity <= 0:
            raise ContractError('matching kind/quantity mismatch')
        if self.reported_side is not None and (type(self.reported_side) is not int or self.reported_side not in (-1, 1)):
            raise ContractError('matching preserves reported sign or unknown')
        if not isinstance(self.raw_hash, str) or re.fullmatch('[0-9a-f]{64}', self.raw_hash) is None:
            raise ContractError('matching needs immutable raw content hash')
        for value in (self.price_key, self.condition):
            if value is not None and (not isinstance(value, str) or not value):
                raise ContractError('missing matching fields must be None')
        if self.source_order is not None and (type(self.source_order) is not int or self.source_order < 0):
            raise ContractError('matching source order must be explicit or absent')

    def economic_record(self):
        return {k: v for k, v in asdict(self).items() if k not in ('id', 'known_at')}


@dataclass(frozen=True)
class PairingProof:
    left_id: str
    right_id: str
    evidence_id: str
    known_at: int

    def __post_init__(self):
        timestamp(self.known_at)
        if any(not isinstance(v, str) or not v for v in (self.left_id, self.right_id, self.evidence_id)):
            raise ContractError('certified pairing requires explicit identity evidence')


@dataclass(frozen=True)
class MatchContract:
    id: str
    left_schema: str
    right_schema: str
    instrument: str
    quantity_unit: str
    price_unit: str
    time_rule: str
    primary: str
    proofs: tuple[PairingProof, ...] = ()

    def __post_init__(self):
        if any(not isinstance(v, str) or not v for v in (self.id, self.left_schema, self.right_schema,
                                                        self.instrument, self.quantity_unit, self.price_unit)):
            raise ContractError('cross-source comparison contract is incomplete')
        if self.time_rule not in ('exact_interval', 'overlapping_precision') or self.primary not in ('left', 'right'):
            raise ContractError('declare comparable time precision and a primary measurement source')
        if not isinstance(self.proofs, tuple) or any(not isinstance(p, PairingProof) for p in self.proofs):
            raise ContractError('identity proofs must be immutable')


@dataclass(frozen=True)
class MatchComponent:
    left_ids: tuple[str, ...]
    right_ids: tuple[str, ...]
    candidate_edges: tuple[tuple[str, str], ...]
    certified_pairs: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Reconciliation:
    contract_id: str
    contract_hash: str
    input_known_at: int | None
    left_ids: tuple[str, ...]
    right_ids: tuple[str, ...]
    candidate_edges: tuple[tuple[str, str], ...]
    certified_pairs: tuple[tuple[str, str], ...]
    candidate_capacity: int
    distinct_print_count_conditional_bounds: tuple[int, int] | None
    unmatched_left: tuple[str, ...]
    unmatched_right: tuple[str, ...]
    discrepancies: tuple[tuple[str, str | None, str | None], ...]
    components: tuple[MatchComponent, ...]
    primary: str
    primary_measurement_records: int
    primary_measurement_volume: int
    left_volume: int
    right_volume: int
    input_hash: str
    input_rows: int
    duplicate_acquisition_rows: int
    pair_comparisons: int
    left_record_count: int
    right_record_count: int
    published: bool = field(default=False, init=False)

    @property
    def id(self):
        return digest(asdict(self))


def _capacity(left_ids, edges):
    """Maximum possible pair count only; the arbitrary witness is never emitted."""
    neighbors = {id: [] for id in left_ids}
    for left, right in edges:
        neighbors[left].append(right)
    matched = {}

    def visit(left, seen):
        for right in neighbors[left]:
            if right not in seen:
                seen.add(right)
                if right not in matched or visit(matched[right], seen):
                    matched[right] = left
                    return True
        return False

    return sum(visit(left, set()) for left in left_ids)


def reconcile_observations(left, right, *, contract: MatchContract, max_rows=512, max_candidate_edges=4096):
    """Pure unpublished reference result; input_known_at is only an input floor."""
    if (not isinstance(left, tuple) or not isinstance(right, tuple) or not isinstance(contract, MatchContract)
            or any(type(v) is not int or v <= 0 for v in (max_rows, max_candidate_edges))
            or len(left) + len(right) > max_rows):
        raise ContractError('bounded immutable cross-source observations required')
    source_input = (left, right)
    dedup_count = 0
    normalized = []
    for values, schema in ((left, contract.left_schema), (right, contract.right_schema)):
        by_row, by_id = {}, {}
        for observation in values:
            if not isinstance(observation, MatchObservation):
                raise ContractError('typed cross-source observation required')
            if (observation.schema_version, observation.instrument, observation.quantity_unit, observation.price_unit) != (schema, contract.instrument, contract.quantity_unit, contract.price_unit):
                raise ContractError('matching cannot silently mix schema, raw instruments or units')
            old_id = by_id.get(observation.id)
            if old_id is not None and old_id != observation:
                raise IntegrityError('matching observation ID reused with changed content')
            by_id[observation.id] = observation
            old = by_row.get(observation.source_row_id)
            if old is not None:
                if old.economic_record() != observation.economic_record():
                    raise IntegrityError('verified source row reused with different content')
                dedup_count += 1
                if observation.id < old.id:
                    by_row[observation.source_row_id] = observation
            else:
                by_row[observation.source_row_id] = observation
        normalized.append(tuple(sorted(by_row.values(), key=lambda o: o.id)))
    left, right = normalized
    if {o.id for o in left} & {o.id for o in right}:
        raise ContractError('cross-source observation IDs need distinct namespaces')
    discrepancies = set()
    for side, values in (('left', left), ('right', right)):
        for o in values:
            position = (o.id, None) if side == 'left' else (None, o.id)
            if o.kind != 'trade':
                discrepancies.add(('snapshot_state' if o.kind == 'snapshot' else 'book_state', *position))
            elif o.condition is None:
                discrepancies.add(('condition_unknown', *position))
            if o.kind == 'trade' and o.reported_side is None:
                discrepancies.add(('side_uncertainty', *position))
            if o.kind == 'trade' and o.price_key is None:
                discrepancies.add(('unsupported_price', *position))
    trades_left = tuple(o for o in left if o.kind == 'trade')
    trades_right = tuple(o for o in right if o.kind == 'trade')
    candidates = []
    comparisons = 0
    for a in trades_left:
        for b in trades_right:
            comparisons += 1
            same_time = ((a.event_start, a.event_end) == (b.event_start, b.event_end) if contract.time_rule == 'exact_interval'
                         else max(a.event_start, b.event_start) < min(a.event_end, b.event_end))
            if not same_time or a.price_key is None or a.price_key != b.price_key:
                continue
            if a.aggregation_unit != b.aggregation_unit or a.quantity != b.quantity:
                discrepancies.add(('aggregation_mismatch', a.id, b.id))
                continue
            if a.condition is None or b.condition is None:
                continue
            if a.condition != b.condition:
                discrepancies.add(('condition_disagreement', a.id, b.id))
                continue
            if a.reported_side != b.reported_side:
                discrepancies.add(('side_disagreement', a.id, b.id))
            if len(candidates) >= max_candidate_edges:
                raise ContractError('cross-source candidate-edge bound reached; no truncated certainty')
            candidates.append((a.id, b.id))
    candidates = tuple(sorted(candidates))
    proofs, used_left, used_right = [], set(), set()
    for proof in contract.proofs:
        pair = (proof.left_id, proof.right_id)
        if pair not in candidates or proof.left_id in used_left or proof.right_id in used_right:
            raise IntegrityError('identity proof is unsupported, duplicated or conflicts with one-to-one ownership')
        proofs.append(pair)
        used_left.add(proof.left_id); used_right.add(proof.right_id)
    proofs = tuple(sorted(proofs))
    left_ids, right_ids = tuple(o.id for o in trades_left), tuple(o.id for o in trades_right)
    remaining_edges = tuple((a, b) for a, b in candidates if a not in used_left and b not in used_right)
    capacity = len(proofs) + _capacity(tuple(id for id in left_ids if id not in used_left), remaining_edges)
    # Every component preserves its possible pairings; no witness gets promoted.
    neighbors = {('L', id): set() for id in left_ids} | {('R', id): set() for id in right_ids}
    for a, b in candidates:
        neighbors['L', a].add(('R', b)); neighbors['R', b].add(('L', a))
    remaining = set(neighbors)
    components = []
    while remaining:
        reached, stack = set(), [min(remaining)]
        while stack:
            node = stack.pop()
            if node not in reached:
                reached.add(node); stack.extend(neighbors[node] - reached)
        remaining -= reached
        ls = tuple(sorted(id for side, id in reached if side == 'L'))
        rs = tuple(sorted(id for side, id in reached if side == 'R'))
        ce = tuple(pair for pair in candidates if pair[0] in ls)
        components.append(MatchComponent(ls, rs, ce, tuple(pair for pair in proofs if pair[0] in ls)))
    for id in left_ids:
        if not neighbors['L', id]:
            discrepancies.add(('missing_counterpart', id, None))
    for id in right_ids:
        if not neighbors['R', id]:
            discrepancies.add(('missing_counterpart', None, id))
    primary = trades_left if contract.primary == 'left' else trades_right
    known = max([*(o.known_at for values in source_input for o in values), *(p.known_at for p in contract.proofs)], default=None)
    # Only declared whole-print records support this conditional execution count.
    comparable_prints = all(o.price_key is not None and o.condition is not None
                            and o.aggregation_unit == 'whole-print' for o in (*trades_left, *trades_right))
    bounds = ((len(left_ids) + len(right_ids) - capacity, len(left_ids) + len(right_ids) - len(proofs))
              if comparable_prints else None)
    return Reconciliation(contract.id, digest(asdict(contract)), known, left_ids, right_ids, candidates, proofs, capacity,
                          bounds,
                          tuple(id for id in left_ids if id not in used_left), tuple(id for id in right_ids if id not in used_right),
                          tuple(sorted(discrepancies, key=lambda r: (r[0], r[1] or '', r[2] or ''))),
                          tuple(sorted(components, key=lambda c: (c.left_ids, c.right_ids))), contract.primary,
                          len(primary), sum(o.quantity for o in primary), sum(o.quantity for o in trades_left),
                          sum(o.quantity for o in trades_right), digest([[asdict(o) for o in sorted(values, key=lambda x: x.id)] for values in source_input]),
                          sum(len(values) for values in source_input), dedup_count, comparisons, len(trades_left), len(trades_right))
