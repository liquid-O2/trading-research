"""Chronological grouped folds and transitive fitted-artifact exclusion checks."""

from dataclasses import dataclass
from typing import Iterable, Mapping

from trading_research.errors import ContractError
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest
from trading_research.research.period import (PrimaryAdmissionV1, ResearchPeriodPolicyV1,
    ResearchScopeV1, check_sample_population, validate_consumer_admission,
    validate_consumer_admission_shape, validate_scope)


@dataclass(frozen=True)
class Sample:
    id: str
    date_group: str
    decision_at: int
    label_known_at: int
    dependency_end: int
    target_version: str

    def __post_init__(self) -> None:
        for at in (self.decision_at, self.label_known_at, self.dependency_end):
            timestamp(at)
        if (any(type(v) is not str or not v for v in (self.id, self.date_group, self.target_version))
                or self.dependency_end < self.decision_at or self.label_known_at < self.dependency_end):
            raise ContractError("sample must declare its full mature interval and date group")


@dataclass(frozen=True)
class Fold:
    id: str
    fit_at: int
    evaluation_start: int
    evaluation_end: int
    embargo_ns: int
    training_ids: tuple[str, ...]
    evaluation_ids: tuple[str, ...]
    purged: tuple[tuple[str, str], ...]
    sample_manifest_hash: str
    training_start: int | None = None

    def __post_init__(self):
        for at in (self.fit_at, self.evaluation_start, self.evaluation_end):
            timestamp(at)
        if (any(type(v) is not str or not v for v in (self.id, self.sample_manifest_hash))
                or self.fit_at > self.evaluation_start or self.evaluation_end <= self.evaluation_start
                or type(self.embargo_ns) is not int or self.embargo_ns < 0):
            raise ContractError("invalid immutable fold declaration")
        for values in (self.training_ids, self.evaluation_ids):
            if (not isinstance(values, tuple) or any(type(v) is not str or not v for v in values)
                    or len(set(values)) != len(values)):
                raise ContractError("fold membership must be immutable and unique")
        if set(self.training_ids).intersection(self.evaluation_ids):
            raise ContractError("training and evaluation memberships overlap")
        if (not isinstance(self.purged, tuple)
                or any(not isinstance(v, tuple) or len(v) != 2
                       or any(type(s) is not str or not s for s in v) for v in self.purged)
                or len({v[0] for v in self.purged}) != len(self.purged)):
            raise ContractError("purge evidence must be immutable and unique")
        if self.training_start is not None:
            timestamp(self.training_start)
            if self.training_start >= self.evaluation_start:
                raise ContractError("training window begins after evaluation")

    @property
    def version(self) -> str:
        return digest(self)


def chronological_fold(samples: Iterable[Sample], *, id: str, fit_at: int,
                       evaluation_start: int, evaluation_end: int, embargo_ns: int = 0,
                       training_start: int | None = None, scope: ResearchScopeV1 | None = None,
                       policy: ResearchPeriodPolicyV1 | None = None,
                       admission: PrimaryAdmissionV1 | None = None) -> Fold:
    samples = tuple(samples)
    if any(not isinstance(s, Sample) for s in samples):
        raise ContractError("fold population requires typed samples")
    validate_scope(scope, policy)
    admission_cut = validate_consumer_admission_shape(scope=scope, policy=policy, admission=admission)
    check_sample_population(scope, policy, samples, fit_at=fit_at,
                            evaluation_start=evaluation_start, evaluation_end=evaluation_end,
                            training_start=training_start,
                            actual_cut_at=admission_cut)
    validate_consumer_admission(samples, scope=scope, policy=policy, admission=admission)
    rows = tuple(sorted(samples, key=lambda s: (s.decision_at, s.id)))
    for at in (fit_at, evaluation_start, evaluation_end):
        timestamp(at)
    if (not id or fit_at > evaluation_start or evaluation_end <= evaluation_start
            or type(embargo_ns) is not int or embargo_ns < 0):
        raise ContractError("invalid forward fold boundaries or embargo")
    if len({s.id for s in rows}) != len(rows):
        raise ContractError("duplicate sample identity")
    if training_start is not None:
        timestamp(training_start)
        if training_start>=evaluation_start:raise ContractError("training window begins after evaluation")
        inside={s.date_group for s in rows if training_start<=s.decision_at<evaluation_start}
        if any(s.date_group in inside and s.decision_at<training_start for s in rows):
            raise ContractError("training boundary splits a correlated date group")
    evaluation = tuple(s for s in rows if evaluation_start <= s.decision_at < evaluation_end)
    groups = {s.date_group for s in evaluation}
    # A caller must place the entire same-date group inside the evaluation block.
    if any(s.date_group in groups and not evaluation_start <= s.decision_at < evaluation_end for s in rows):
        raise ContractError("evaluation boundary splits a related same-date asset/object group")
    training, purged = [], []
    for s in rows:
        if s.decision_at >= evaluation_start:
            continue
        if training_start is not None and s.decision_at<training_start:
            purged.append((s.id,"outside_registered_training_window"))
        elif s.label_known_at > fit_at:
            purged.append((s.id, "label_not_mature_at_fit"))
        elif s.dependency_end >= evaluation_start - embargo_ns:
            purged.append((s.id, "dependency_interval_overlaps_evaluation_or_embargo"))
        else:
            training.append(s.id)
    return Fold(id, fit_at, evaluation_start, evaluation_end, embargo_ns,
                tuple(training), tuple(s.id for s in evaluation), tuple(purged), digest(rows),training_start)


def validate_fold_population(samples: Iterable[Sample], fold: Fold, *,
                             scope: ResearchScopeV1 | None = None,
                             policy: ResearchPeriodPolicyV1 | None = None,
                             admission: PrimaryAdmissionV1 | None = None) -> Fold:
    """A supplied dataclass is a declaration, not evidence of its membership."""
    if not isinstance(fold, Fold):
        raise ContractError("typed fold required")
    samples = tuple(samples)
    validate_scope(scope, policy)
    admission_cut = validate_consumer_admission_shape(scope=scope, policy=policy, admission=admission)
    check_sample_population(scope, policy, samples, fit_at=fold.fit_at,
                            evaluation_start=fold.evaluation_start, evaluation_end=fold.evaluation_end,
                            training_start=fold.training_start,
                            actual_cut_at=admission_cut)
    validate_consumer_admission(samples, scope=scope, policy=policy, admission=admission)
    expected = chronological_fold(samples, id=fold.id, fit_at=fold.fit_at,
                                  evaluation_start=fold.evaluation_start, evaluation_end=fold.evaluation_end,
                                  embargo_ns=fold.embargo_ns, training_start=fold.training_start,
                                  scope=scope, policy=policy, admission=admission)
    if expected != fold:
        raise ContractError("fold membership/purge evidence differs from retained population")
    return expected


def chronological_primary_fold(samples: Iterable[Sample], *, id: str, fit_at: int,
                                evaluation_start: int, evaluation_end: int,
                                scope: ResearchScopeV1, policy: ResearchPeriodPolicyV1,
                                admission: PrimaryAdmissionV1, embargo_ns: int = 0,
                                training_start: int | None = None) -> Fold:
    """Compile a primary fold with an explicit complete-population admission."""
    validate_scope(scope, policy, require_primary=True)
    if type(admission) is not PrimaryAdmissionV1:
        raise ContractError("chronological_primary_fold requires an immutable population admission envelope")
    return chronological_fold(samples, id=id, fit_at=fit_at, evaluation_start=evaluation_start,
                               evaluation_end=evaluation_end, embargo_ns=embargo_ns,
                               training_start=training_start, scope=scope, policy=policy,
                               admission=admission)


@dataclass(frozen=True)
class FittedArtifact:
    id: str
    role: str
    fold_version: str
    fitted_at: int
    training_ids: frozenset[str]
    training_groups: frozenset[str]
    training_labels_known_through: int
    upstream_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if any(type(v) is not str or not v for v in (self.id, self.role, self.fold_version)):
            raise ContractError("fitted transforms, experts and calibrators require versioned identity")
        if (not isinstance(self.training_ids,frozenset) or not isinstance(self.training_groups,frozenset)
                or not isinstance(self.upstream_ids,tuple)):
            raise ContractError("fitted sample/group membership and dependency identities must be immutable")
        if any(type(v) is not str or not v for v in (*self.training_ids, *self.training_groups, *self.upstream_ids)):
            raise ContractError("fitted membership and dependency identities must be strings")
        timestamp(self.fitted_at)
        timestamp(self.training_labels_known_through)
        if self.training_labels_known_through > self.fitted_at:
            raise ContractError("fitted artifact uses labels unavailable at fit time")
        if len(set(self.upstream_ids)) != len(self.upstream_ids):
            raise ContractError("duplicate fitted dependency")


def validate_oof(sample: Sample, artifact_id: str, artifacts: Iterable[FittedArtifact], *, fold_version: str,
                 upstream_fold_routes: Mapping[str,str] | None = None) -> tuple[str, ...]:
    artifacts = tuple(artifacts)
    by_id = {a.id: a for a in artifacts}
    if len(by_id) != len(artifacts):
        raise ContractError("duplicate fitted artifact ID")
    visited, visiting = set(), set()

    def visit(id: str) -> None:
        if id in visiting:
            raise ContractError("cyclic fitted lineage")
        if id in visited:
            return
        if id not in by_id:
            raise ContractError("missing fitted dependency; transforms/calibrators cannot be omitted")
        a = by_id[id]
        expected_fold = fold_version if id == artifact_id else (upstream_fold_routes or {}).get(id,fold_version)
        if a.fold_version != expected_fold or a.fitted_at > sample.decision_at:
            raise ContractError("future fit or stale fold artifact")
        if sample.id in a.training_ids or sample.date_group in a.training_groups:
            raise ContractError("in-sample leakage in transitive fitted closure")
        visiting.add(id)
        for upstream in a.upstream_ids:
            visit(upstream)
            if by_id[upstream].fitted_at > a.fitted_at:
                raise ContractError("fitted dependency was built after its consumer")
        visiting.remove(id)
        visited.add(id)

    visit(artifact_id)
    return tuple(sorted(visited))
