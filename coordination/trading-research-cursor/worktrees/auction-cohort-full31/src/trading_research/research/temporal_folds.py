"""Versioned finite temporal populations, separate target clocks and OOF routes.

These records never upgrade the legacy Sample/Fold wire schema. A compiled plan
proves eligibility from declared evidence; actual reads remain the F11 boundary.
"""
from dataclasses import dataclass, fields
from itertools import islice

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import ArtifactRef, canonical_json, digest
from trading_research.research.period import (PrimaryAdmissionV1, ResearchPeriodPolicyV1,
    ResearchScopeV1, check_sample_population, validate_consumer_admission,
    validate_consumer_admission_shape, validate_scope)


@dataclass(frozen=True)
class V01V02LimitsV1:
    max_ledger_candidates: int = 4096
    max_ledger_definitions: int = 1024
    max_ledger_outcomes: int = 8192
    max_temporal_population: int = 4096
    max_dependencies_per_sample: int = 64
    max_total_dependencies: int = 16384
    max_stages: int = 64
    max_oof_edges: int = 4096
    max_parent_groups_per_sample: int = 64
    max_id_utf8_bytes: int = 256
    max_payload_bytes: int = 65536
    max_checkpoint_bytes: int = 2097152
    max_nested_depth: int = 32

    def __post_init__(self):
        if any(type(getattr(self, f.name)) is not int or getattr(self, f.name) < 1 for f in fields(self)):
            raise ContractError('positive exact finite limits required')


DEFAULT_LIMITS = V01V02LimitsV1()


def bounded(values, maximum, name):
    if type(maximum) is not int or maximum < 1:
        raise ContractError('positive exact iterable capacity required')
    result = tuple(islice(iter(values), maximum + 1))
    if len(result) > maximum:
        raise ContractError(name + ' capacity exceeded')
    return result


def identity(value, limits=DEFAULT_LIMITS):
    if type(value) is not str or not value or (limits is not None and len(value.encode('utf-8')) > limits.max_id_utf8_bytes):
        raise ContractError('bounded nonempty exact identity required')
    return value


def names(values, maximum, limits=DEFAULT_LIMITS):
    if type(values) is not tuple or (maximum is not None and len(values) > maximum):
        raise ContractError('immutable identity capacity exceeded')
    for value in values:
        identity(value, limits)
    if len(set(values)) != len(values):
        from collections import Counter
        raise ContractError('duplicate identity: ' + ','.join(sorted(v for v,n in Counter(values).items() if n>1)))
    return values


def _limits(limits):
    if type(limits) is not V01V02LimitsV1:
        raise ContractError('typed finite limits required')
    limits.__post_init__()


def bounded_json(raw, maximum, limits=DEFAULT_LIMITS):
    """Bound bytes and JSON nesting before parsing, then require canonical bytes."""
    import json
    _limits(limits)
    if type(raw) is not bytes or len(raw) > maximum:
        raise ContractError('canonical payload byte capacity exceeded')
    depth = 0
    quoted = escaped = False
    for byte in raw:
        if quoted:
            if escaped:
                escaped = False
            elif byte == 92:
                escaped = True
            elif byte == 34:
                quoted = False
        elif byte == 34:
            quoted = True
        elif byte in (91, 123):
            depth += 1
            if depth > limits.max_nested_depth:
                raise ContractError('canonical payload nesting capacity exceeded')
        elif byte in (93, 125):
            depth -= 1
    try:
        value = json.loads(raw)
        if canonical_json(value) != raw:
            raise ValueError('noncanonical')
    except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
        raise ContractError('invalid canonical payload') from exc
    return value


@dataclass(frozen=True)
class TemporalDependencyV1:
    id: str
    kind: str
    start: int
    end: int
    known_at: int
    evidence_ref: ArtifactRef

    def __post_init__(self):
        identity(self.id, None)
        if self.kind not in ('raw_past', 'label_span', 'carried_state') or type(self.kind) is not str:
            raise ContractError('unknown temporal dependency kind')
        for value in (self.start, self.end, self.known_at):
            timestamp(value)
        if self.start > self.end or type(self.evidence_ref) is not ArtifactRef:
            raise ContractError('invalid temporal dependency span/evidence')

    @property
    def evidence_bytes(self):
        return canonical_json({'format': 'TemporalDependencyEvidenceV1', 'id': self.id,
                               'kind': self.kind, 'start': self.start, 'end': self.end,
                               'known_at': self.known_at})


def validate_dependency_bytes(dependency, payloads, limits=DEFAULT_LIMITS):
    _limits(limits)
    if type(dependency) is not TemporalDependencyV1:
        raise ContractError('typed dependency required')
    ref = dependency.evidence_ref
    identity(dependency.id, limits)
    if ref.size_bytes > limits.max_payload_bytes:
        raise ContractError('dependency payload capacity exceeded')
    raw = payloads.get(ref.sha256)
    if raw != dependency.evidence_bytes or len(raw) != ref.size_bytes:
        raise IntegrityError('temporal dependency evidence bytes disagree')
    import hashlib
    if hashlib.sha256(raw).hexdigest() != ref.sha256:
        raise IntegrityError('temporal dependency evidence hash disagrees')


@dataclass(frozen=True)
class TemporalSampleV1:
    id: str
    date_group: str
    decision_at: int
    target_end: int
    label_known_at: int
    target_version: str
    phase_role: str
    endpoint_group: str
    parent_groups: tuple[str, ...]
    dependencies: tuple[TemporalDependencyV1, ...]

    def __post_init__(self):
        for value in (self.id, self.date_group, self.target_version, self.endpoint_group):
            identity(value, None)
        for value in (self.decision_at, self.target_end, self.label_known_at):
            timestamp(value)
        if not self.decision_at < self.target_end <= self.label_known_at:
            raise ContractError('actual target and maturity clocks disagree')
        if type(self.phase_role) is not str or self.phase_role not in ('train', 'tune', 'calibrate', 'outer', 'future'):
            raise ContractError('unknown immutable phase role')
        names(self.parent_groups, None, None)
        if type(self.dependencies) is not tuple or any(type(d) is not TemporalDependencyV1 for d in self.dependencies):
            raise ContractError('typed immutable temporal dependencies required')
        names(tuple(d.id for d in self.dependencies), None, None)
        if any(d.kind == 'raw_past' and (d.end > self.decision_at or d.known_at > self.decision_at) for d in self.dependencies):
            raise ContractError('raw historical input after original decision')
        object.__setattr__(self, 'parent_groups', tuple(sorted(self.parent_groups)))
        object.__setattr__(self, 'dependencies', tuple(sorted(self.dependencies, key=lambda d: d.id)))

    @property
    def dependency_end(self):
        """Diagnostic maximum only; never the actual label target endpoint."""
        return max((self.target_end, *(d.end for d in self.dependencies if d.kind != 'raw_past')))


_REASONS = ('outside_registered_training_window', 'forbidden_phase_role',
            'label_not_mature_at_fit', 'dependency_not_available_at_fit',
            'forbidden_dependency_overlap')


@dataclass(frozen=True)
class TemporalExclusionV1:
    sample_id: str
    reason: str
    dependency_ids: tuple[str, ...]

    def __post_init__(self):
        identity(self.sample_id, None)
        if self.reason not in _REASONS:
            raise ContractError('unknown temporal exclusion reason')
        names(self.dependency_ids, None, None)
        object.__setattr__(self, 'dependency_ids', tuple(sorted(self.dependency_ids)))


@dataclass(frozen=True)
class TemporalFoldV1:
    id: str
    fit_at: int
    evaluation_start: int
    evaluation_end: int
    embargo_ns: int
    training_start: int | None
    training_roles: tuple[str, ...]
    training_ids: tuple[str, ...]
    evaluation_ids: tuple[str, ...]
    exclusions: tuple[TemporalExclusionV1, ...]
    sample_manifest_hash: str

    def __post_init__(self):
        identity(self.id, None); identity(self.sample_manifest_hash, None)
        for value in (self.fit_at, self.evaluation_start, self.evaluation_end):
            timestamp(value)
        if self.fit_at > self.evaluation_start or self.evaluation_start >= self.evaluation_end:
            raise ContractError('invalid chronological temporal fold')
        if type(self.embargo_ns) is not int or self.embargo_ns < 0:
            raise ContractError('nonnegative exact embargo required')
        if self.training_start is not None:
            timestamp(self.training_start)
            if self.training_start >= self.evaluation_start:
                raise ContractError('invalid rolling training start')
        names(self.training_roles, 3)
        if not self.training_roles or set(self.training_roles) - {'train', 'tune', 'calibrate'}:
            raise ContractError('outer/future state cannot fit development roles')
        for values in (self.training_ids, self.evaluation_ids):
            names(values, None, None)
        if set(self.training_ids) & set(self.evaluation_ids):
            raise ContractError('temporal membership overlaps')
        if type(self.exclusions) is not tuple or any(type(e) is not TemporalExclusionV1 for e in self.exclusions):
            raise ContractError('typed immutable exclusions required')
        names(tuple(e.sample_id for e in self.exclusions), None, None)

    @property
    def version(self):
        return digest({'type': 'TemporalFoldV1', 'fields': self})

    @property
    def purged(self):
        return tuple((e.sample_id, e.reason) for e in self.exclusions)


def temporal_population(population, limits=DEFAULT_LIMITS):
    _limits(limits)
    rows = bounded(population, limits.max_temporal_population, 'temporal population')
    if any(type(s) is not TemporalSampleV1 for s in rows):
        raise ContractError('exact temporal sample population required')
    names(tuple(s.id for s in rows), limits.max_temporal_population, limits)
    total = 0
    for s in rows:
        if len(s.dependencies)>limits.max_dependencies_per_sample or len(s.parent_groups)>limits.max_parent_groups_per_sample:
            raise ContractError('temporal row capacity exceeded')
        total += len(s.dependencies)
        if total > limits.max_total_dependencies:
            raise ContractError('total temporal dependency capacity exceeded')
        s.__post_init__()
        for value in (s.id, s.date_group, s.target_version, s.endpoint_group):
            identity(value, limits)
        names(s.parent_groups, limits.max_parent_groups_per_sample, limits)
        names(tuple(d.id for d in s.dependencies), limits.max_dependencies_per_sample, limits)
        for d in s.dependencies:
            d.__post_init__()
            identity(d.id,limits)
            if d.evidence_ref.size_bytes>limits.max_payload_bytes:
                raise ContractError('temporal dependency payload capacity exceeded')
    return tuple(sorted(rows, key=lambda s: (s.decision_at, s.id)))


def compile_temporal_fold(population, *, id, fit_at, evaluation_start, evaluation_end,
                          embargo_ns=0, training_start=None, training_roles=('train',),
                          limits=DEFAULT_LIMITS, scope: ResearchScopeV1 | None = None,
                          policy: ResearchPeriodPolicyV1 | None = None,
                          admission: PrimaryAdmissionV1 | None = None):
    rows = temporal_population(population, limits)
    validate_scope(scope, policy)
    admission_cut = validate_consumer_admission_shape(scope=scope, policy=policy, admission=admission)
    check_sample_population(scope, policy, rows, fit_at=fit_at,
                            evaluation_start=evaluation_start, evaluation_end=evaluation_end,
                            training_start=training_start,
                            actual_cut_at=admission_cut)
    validate_consumer_admission(rows, scope=scope, policy=policy, admission=admission)
    identity(id, limits)
    return _compile_temporal_semantics(rows,id=id,fit_at=fit_at,evaluation_start=evaluation_start,
        evaluation_end=evaluation_end,embargo_ns=embargo_ns,training_start=training_start,training_roles=training_roles)


def _compile_temporal_semantics(rows, *, id, fit_at, evaluation_start, evaluation_end,
                                embargo_ns=0, training_start=None, training_roles=('train',)):
    # Validate controls before membership enumeration, including empty populations.
    TemporalFoldV1(id, fit_at, evaluation_start, evaluation_end, embargo_ns,
                   training_start, training_roles, (), (), (), digest(rows))
    evaluation = tuple(s for s in rows if evaluation_start <= s.decision_at < evaluation_end)
    groups = {s.date_group for s in evaluation}
    if any(s.date_group in groups and s not in evaluation for s in rows):
        raise ContractError('evaluation boundary splits date group')
    if training_start is not None:
        inside = {s.date_group for s in rows if training_start <= s.decision_at < evaluation_start}
        if any(s.date_group in inside and s.decision_at < training_start for s in rows):
            raise ContractError('training boundary splits date group')
    training, exclusions = [], []
    threshold = evaluation_start - embargo_ns
    for s in rows:
        if s.decision_at >= evaluation_start:
            continue
        reason, ids = None, ()
        if training_start is not None and s.decision_at < training_start:
            reason = _REASONS[0]
        elif s.phase_role not in training_roles:
            reason = _REASONS[1]
        elif s.label_known_at > fit_at:
            reason = _REASONS[2]
        elif any(d.known_at > fit_at for d in s.dependencies):
            reason = _REASONS[3]
            ids = tuple(d.id for d in s.dependencies if d.known_at > fit_at)
        else:
            ids = tuple(d.id for d in s.dependencies if d.kind != 'raw_past' and d.end >= threshold)
            if s.target_end >= threshold or ids:
                reason = _REASONS[4]
        if reason is None:
            training.append(s.id)
        else:
            exclusions.append(TemporalExclusionV1(s.id, reason, ids))
    return TemporalFoldV1(id, fit_at, evaluation_start, evaluation_end, embargo_ns,
                           training_start, tuple(sorted(training_roles)), tuple(training),
                           tuple(s.id for s in evaluation), tuple(exclusions), digest(rows))


def validate_temporal_fold_population(population, fold, *, limits=DEFAULT_LIMITS,
                                      scope: ResearchScopeV1 | None = None,
                                      policy: ResearchPeriodPolicyV1 | None = None,
                                      admission: PrimaryAdmissionV1 | None = None):
    if type(fold) is not TemporalFoldV1:
        raise ContractError('exact temporal fold required')
    rows = temporal_population(population, limits)
    validate_scope(scope, policy)
    admission_cut = validate_consumer_admission_shape(scope=scope, policy=policy, admission=admission)
    check_sample_population(scope, policy, rows, fit_at=fold.fit_at,
                            evaluation_start=fold.evaluation_start, evaluation_end=fold.evaluation_end,
                            training_start=fold.training_start,
                            actual_cut_at=admission_cut)
    validate_consumer_admission(rows, scope=scope, policy=policy, admission=admission)
    expected = compile_temporal_fold(rows, id=fold.id, fit_at=fold.fit_at,
        evaluation_start=fold.evaluation_start, evaluation_end=fold.evaluation_end,
        embargo_ns=fold.embargo_ns, training_start=fold.training_start,
        training_roles=fold.training_roles, limits=limits, scope=scope, policy=policy,
        admission=admission)
    if expected != fold:
        raise ContractError('temporal plan differs from complete retained population')
    return expected


def compile_primary_temporal_fold(population, *, id, fit_at, evaluation_start, evaluation_end,
                                  scope: ResearchScopeV1, policy: ResearchPeriodPolicyV1,
                                  admission: PrimaryAdmissionV1, embargo_ns=0,
                                  training_start=None, training_roles=('train',),
                                  limits=DEFAULT_LIMITS):
    """Compile a primary temporal fold with explicit complete-population admission."""
    validate_scope(scope, policy, require_primary=True)
    if type(admission) is not PrimaryAdmissionV1:
        raise ContractError('compile_primary_temporal_fold requires an immutable population admission envelope')
    return compile_temporal_fold(population, id=id, fit_at=fit_at,
                                 evaluation_start=evaluation_start, evaluation_end=evaluation_end,
                                 embargo_ns=embargo_ns, training_start=training_start,
                                 training_roles=training_roles, limits=limits, scope=scope,
                                 policy=policy, admission=admission)


@dataclass(frozen=True)
class FitStage:
    id: str
    role: str
    population: tuple[TemporalSampleV1, ...]
    fold: TemporalFoldV1
    completed_at: int

    def __post_init__(self):
        identity(self.id, None); identity(self.role, None)
        if type(self.population) is not tuple:
            raise ContractError('immutable stage population required')
        _validate_temporal_semantics(self.population, self.fold)
        timestamp(self.completed_at)
        if self.completed_at < self.fold.fit_at:
            raise ContractError('stage completion before fit')


@dataclass(frozen=True)
class OOFEdge:
    producer: str
    consumer: str
    row_ids: tuple[str, ...]

    def __post_init__(self):
        identity(self.producer, None); identity(self.consumer, None)
        names(self.row_ids, None, None)


def compile_oof_schedule(stages, required_edges, *, limits=DEFAULT_LIMITS):
    _limits(limits)
    stages = bounded(stages, limits.max_stages, 'fit stage')
    edges = bounded(required_edges, limits.max_oof_edges, 'OOF edge')
    if any(type(s) is not FitStage for s in stages) or any(type(e) is not OOFEdge for e in edges):
        raise ContractError('typed stage and edge records required')
    by = {s.id: s for s in stages}
    if len(by) != len(stages) or len({(e.producer,e.consumer) for e in edges}) != len(edges):
        raise ContractError('duplicate stage/OOF edge')
    for stage in stages:
        identity(stage.id,limits); identity(stage.role,limits)
        validate_temporal_fold_population(stage.population, stage.fold, limits=limits)
    adjacency = {s.id: [] for s in stages}
    admitted = []
    for edge in edges:
        identity(edge.producer,limits); identity(edge.consumer,limits)
        names(edge.row_ids,limits.max_temporal_population,limits)
        if edge.producer not in by or edge.consumer not in by:
            raise ContractError('missing required OOF stage')
        p, c = by[edge.producer], by[edge.consumer]
        if set(edge.row_ids) != set(c.fold.training_ids):
            raise ContractError('required OOF rows do not cover downstream training')
        pp = {s.id:s for s in p.population}; cp = {s.id:s for s in c.population}
        for row_id in edge.row_ids:
            s = cp[row_id]
            if (pp.get(row_id) != s or row_id not in p.fold.evaluation_ids
                    or row_id in p.fold.training_ids or s.phase_role in ('outer','future')
                    or p.completed_at > s.decision_at or p.completed_at > c.fold.fit_at
                    or s.date_group in {pp[i].date_group for i in p.fold.training_ids}):
                raise ContractError('OOF original row/phase/group/completion route differs')
            admitted.append((edge.producer, edge.consumer, row_id))
        adjacency[edge.consumer].append(edge.producer)
    visiting, done = set(), set()
    for root in by:
        stack=[(root,False)]
        while stack:
            key,leaving=stack.pop()
            if leaving:
                visiting.remove(key);done.add(key);continue
            if key in visiting:
                raise ContractError('cyclic required OOF schedule')
            if key in done: continue
            if len(visiting)>=limits.max_stages:
                raise ContractError('OOF depth capacity exceeded')
            visiting.add(key);stack.append((key,True))
            stack.extend((p,False) for p in reversed(adjacency[key]))
    return tuple(sorted(admitted))


def temporal_checkpoint(population, fold, *, limits=DEFAULT_LIMITS):
    """Retain an exact typed plan and its local configuration beside F11."""
    rows=temporal_population(population,limits)
    validate_temporal_fold_population(rows,fold,limits=limits)
    from trading_research.research.finite_encoding import encode_wire
    return encode_wire({'format':'TemporalCheckpointV1','limits':{f.name:getattr(limits,f.name) for f in fields(limits)},
        'population':rows,'fold':fold},records=(TemporalDependencyV1,TemporalSampleV1,TemporalFoldV1,
        TemporalExclusionV1,ArtifactRef),maximum=limits.max_checkpoint_bytes,max_depth=limits.max_nested_depth)


def restore_temporal_checkpoint(raw, *, limits=DEFAULT_LIMITS):
    value=bounded_json(raw,limits.max_checkpoint_bytes,limits)
    if type(value) is not dict or set(value)!={'format','limits','population','fold'} or value['format']!='TemporalCheckpointV1':
        raise ContractError('unknown temporal checkpoint format')
    if value['limits']!={f.name:getattr(limits,f.name) for f in fields(limits)}:
        raise ContractError('temporal restore configuration differs')
    _preflight_temporal_wire(value['population'],value['fold'],limits)
    from trading_research.operations.artifact_graph import _restore
    rows,fold=_restore(value['population']),_restore(value['fold'])
    validate_temporal_fold_population(rows,fold,limits=limits)
    if temporal_checkpoint(rows,fold,limits=limits)!=raw:
        raise ContractError('noncanonical temporal checkpoint')
    return rows,fold


def _validate_temporal_semantics(population, fold):
    """Record consistency only; service limits are adjacent retained policy."""
    if type(population) is not tuple or any(type(s) is not TemporalSampleV1 for s in population) or type(fold) is not TemporalFoldV1:
        raise ContractError('typed temporal records required')
    rows=tuple(sorted(population,key=lambda s:(s.decision_at,s.id)))
    expected=_compile_temporal_semantics(rows,id=fold.id,fit_at=fold.fit_at,
        evaluation_start=fold.evaluation_start,evaluation_end=fold.evaluation_end,
        embargo_ns=fold.embargo_ns,training_start=fold.training_start,training_roles=fold.training_roles)
    if expected!=fold:
        raise ContractError('temporal plan differs from retained records')
    return expected


def _preflight_temporal_wire(population, fold, limits):
    def array(raw,maximum):
        if type(raw) is not dict or set(raw)!={'tuple'} or type(raw['tuple']) is not list or len(raw['tuple'])>maximum:
            raise ContractError('temporal restore array capacity exceeded')
        return raw['tuple']
    def record(raw,cls):
        if (type(raw) is not dict or set(raw)!={'type','fields'} or raw['type']!=cls.__name__
                or type(raw['fields']) is not dict or set(raw['fields'])!={f.name for f in fields(cls)}):
            raise ContractError('temporal restore record fields differ')
        return raw['fields']
    total=0
    for row in array(population,limits.max_temporal_population):
        s=record(row,TemporalSampleV1)
        for key in ('id','date_group','target_version','endpoint_group'):
            identity(s[key],limits)
        for group in array(s['parent_groups'],limits.max_parent_groups_per_sample):
            identity(group,limits)
        deps=array(s['dependencies'],limits.max_dependencies_per_sample); total+=len(deps)
        if total>limits.max_total_dependencies:
            raise ContractError('temporal restore total dependency capacity exceeded')
        for dep in deps:
            values=record(dep,TemporalDependencyV1); identity(values['id'],limits)
            ref=record(values['evidence_ref'],ArtifactRef)
            if type(ref['size_bytes']) is not int or not 0<=ref['size_bytes']<=limits.max_payload_bytes:
                raise ContractError('temporal restore dependency byte capacity exceeded')
    f=record(fold,TemporalFoldV1); identity(f['id'],limits)
    for key in ('training_ids','evaluation_ids'):
        for value in array(f[key],limits.max_temporal_population):
            identity(value,limits)
    for exclusion in array(f['exclusions'],limits.max_temporal_population):
        e=record(exclusion,TemporalExclusionV1); identity(e['sample_id'],limits)
        for value in array(e['dependency_ids'],limits.max_dependencies_per_sample):
            identity(value,limits)
    array(f['training_roles'],3)
