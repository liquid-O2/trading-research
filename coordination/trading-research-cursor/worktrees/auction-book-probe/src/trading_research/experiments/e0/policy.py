"""Typed E0 action values and the decision boundary used by the runner.

The E0 policy layer deliberately consumes already fitted, already checked
artifacts.  It does not fit a model, inspect a realized path, or choose a
target after a replay.  A value row contains the complete three-way bracket
distribution (target, stop and deadline/non-fill) and the immutable lineage
needed to establish that the row was available at the decision cut.

The repository has deliberately small common :class:`Opportunity` and
:class:`Decision` messages.  This module supplies the E0 sidecar that binds
those messages to value and policy identities while retaining the common
messages as the public action boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, localcontext
from fractions import Fraction
from typing import Any, Iterable, Mapping

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.contracts import (
    Capability,
    CoverageMask,
    Decision,
    Opportunity,
)
from trading_research.foundations.time import AvailabilityBasis, Clocks, timestamp
from trading_research.operations.artifacts import digest


_ZERO = Decimal("0")


def _name(value: Any, label: str) -> str:
    if type(value) is not str or not value:
        raise ContractError(f"{label} requires a nonempty immutable identity")
    return value


def _number(value: Any, label: str) -> Decimal | Fraction:
    """Accept exact decimal/rational inputs and reject implicit binary floats."""

    if isinstance(value, bool) or not isinstance(value, (Decimal, Fraction, int)):
        raise ContractError(f"{label} requires an exact Decimal or Fraction")
    if isinstance(value, Decimal) and not value.is_finite():
        raise ContractError(f"{label} must be finite")
    return value


def _fraction(value: Any, label: str, *, unit: bool = False) -> Fraction:
    value = _number(value, label)
    result = value if isinstance(value, Fraction) else Fraction(value)
    if unit and not 0 <= result <= 1:
        raise ContractError(f"{label} must lie in [0,1]")
    return result


def _decimal(value: Decimal | Fraction | int, label: str) -> Decimal:
    value = _number(value, label)
    if isinstance(value, Decimal):
        return value
    with localcontext() as context:
        context.prec = 60
        return Decimal(value.numerator) / Decimal(value.denominator)


def _sum_decimal(values: Iterable[Decimal]) -> Decimal:
    # The quantities in the E0 fixtures are finite decimal values.  A local
    # context prevents a caller's low precision context from changing a
    # policy value while retaining the exact Decimal arithmetic contract.
    with localcontext() as context:
        context.prec = 60
        total = Decimal(0)
        for value in values:
            total += value
        return +total


def _weighted_decimal(probability: Fraction, value: Decimal | Fraction | int) -> Decimal:
    with localcontext() as context:
        context.prec = 60
        return _decimal(value, "USD outcome") * Decimal(probability.numerator) / Decimal(probability.denominator)


@dataclass(frozen=True)
class TargetPolicy:
    """A registered fixed target distance.

    ``multiple`` is a policy identity, not a realized-path choice.  A caller
    may provide ``target_ticks`` when the geometry was already materialized;
    the bracket bridge independently verifies the side and tick geometry.
    """

    id: str
    multiple: int | Fraction = 1
    target_ticks: int | None = None
    policy_version: str | None = None
    source_version: str | None = None

    def __post_init__(self) -> None:
        _name(self.id, "target policy")
        multiple = _fraction(self.multiple, "target multiple")
        if multiple <= 0:
            raise ContractError("target multiple must be positive")
        if self.target_ticks is not None and type(self.target_ticks) is not int:
            raise ContractError("target geometry must use integer ticks")
        if self.policy_version is not None:
            _name(self.policy_version, "target policy version")
        if self.source_version is not None:
            _name(self.source_version, "target policy source")

    @property
    def version(self) -> str:
        return digest(self)


@dataclass(frozen=True)
class E0SyntheticNumericalEvidence:
    """Explicit evidence for a pure arithmetic/control value.

    This type is intentionally separate from committed model prediction
    evidence.  It is suitable for the small INT06/geometry controls whose
    probabilities are declared numerical inputs; it is not a substitute for
    the F11 read/fit closure used by a production learned branch.
    """

    id: str
    fitted_at: int
    target_version: str
    fold_id: str
    feature_version: str
    model_version: str | None = None
    calibrator_version: str | None = None
    source_version: str = ""
    kind: str = "synthetic_numeric_control"

    def __post_init__(self) -> None:
        for value, label in ((self.id, "synthetic artifact"),
                             (self.target_version, "synthetic target"),
                             (self.fold_id, "synthetic fold"),
                             (self.feature_version, "synthetic feature")):
            _name(value, label)
        timestamp(self.fitted_at)
        if self.model_version is not None:
            _name(self.model_version, "synthetic model")
        if self.calibrator_version is not None:
            _name(self.calibrator_version, "synthetic calibrator")
        if self.source_version:
            _name(self.source_version, "synthetic source")
        if self.kind != "synthetic_numeric_control":
            raise ContractError("synthetic evidence must use its registered kind")

    @property
    def version(self) -> str:
        return digest(self)


@dataclass(frozen=True)
class E0CommittedPredictionEvidence:
    """The stable policy-side binding for one actual F11 bracket prediction.

    ``head_evidence`` is copied from :class:`E0BracketPrediction` and must
    retain all three target-specific read manifests and fitted closures.  The
    policy layer does not inspect learner internals; it verifies that this
    nonempty typed closure is present and binds its aggregate identities to the
    value row.
    """

    prediction_version: str
    policy_version: str
    sample_id: str
    decision_at: int
    head_evidence: tuple
    fitted_at: int
    source_version: str = ""
    kind: str = "committed_f11_prediction"
    prediction: Any = None

    def __post_init__(self) -> None:
        from trading_research.experiments.e0.learning import E0BracketPrediction
        if type(self.prediction) is not E0BracketPrediction:
            raise ContractError("committed evidence requires an actual typed bracket prediction")
        self.prediction.__post_init__()
        prediction = self.prediction
        actual_fitted_at = max(e[4]["verified_head_receipt"].fitted_at for e in prediction.head_evidence)
        if ((self.prediction_version, self.policy_version, self.sample_id, self.decision_at,
             self.head_evidence, self.fitted_at) !=
                (prediction.version, prediction.policy_version, prediction.sample_id, prediction.at,
                 prediction.head_evidence, actual_fitted_at)
                or self.kind != "committed_f11_prediction"):
            raise ContractError("policy evidence differs from actual retained prediction and fit completion")
        timestamp(self.fitted_at)
        if self.fitted_at > self.decision_at:
            raise DependencyUnavailable("fitted prediction artifact is unavailable at decision cut")
        if self.source_version:
            _name(self.source_version, "prediction source")

    @classmethod
    def from_prediction(cls, prediction: Any, *, fitted_at: int | None = None,
                        source_version: str = "") -> "E0CommittedPredictionEvidence":
        from trading_research.experiments.e0.learning import E0BracketPrediction
        if type(prediction) is not E0BracketPrediction:
            raise ContractError("committed evidence requires an actual typed bracket prediction")
        prediction.__post_init__()
        actual = max(e[4]["verified_head_receipt"].fitted_at for e in prediction.head_evidence)
        if fitted_at is not None and fitted_at != actual:
            raise ContractError("caller fit timestamp differs from actual retained completion")
        return cls(prediction.version, prediction.policy_version, prediction.sample_id,
                   prediction.at, prediction.head_evidence, actual, source_version,
                   prediction=prediction)

    @property
    def probabilities(self):
        return self.prediction.probabilities

    @property
    def id(self) -> str:
        return self.prediction_version

    @property
    def model_version(self) -> str:
        return self.prediction_version

    @property
    def calibrator_version(self) -> str:
        return self.prediction_version

    @property
    def target_version(self) -> str:
        return digest(tuple(e[2] for e in self.head_evidence))

    @property
    def fold_id(self) -> str:
        return digest(tuple(e[3] for e in self.head_evidence))

    @property
    def feature_version(self) -> str:
        return digest(self.head_evidence)

    @property
    def target_versions(self) -> tuple[str, ...]:
        return tuple(e[2] for e in self.head_evidence)


E0ModelArtifactEvidence = E0SyntheticNumericalEvidence | E0CommittedPredictionEvidence


@dataclass(frozen=True)
class E0RuleSelection:
    """Typed first-inward-fade selection for the deterministic rule branch."""

    decision_set_id: str
    candidate_id: str
    side: int
    policy: TargetPolicy
    decision_at: int
    row_version: str
    object_version: str
    source_version: str
    observation_version: str
    source_versions: tuple[str, ...]
    decision_set: Any

    def __post_init__(self) -> None:
        for value, label in ((self.decision_set_id, "rule decision set"),
                             (self.candidate_id, "rule candidate"),
                             (self.row_version, "rule row evidence"),
                             (self.object_version, "rule object evidence"),
                             (self.source_version, "rule source"),
                             (self.observation_version, "rule observation")):
            _name(value, label)
        if type(self.side) is not int or self.side not in (-1, 1):
            raise ContractError("rule selection must carry one signed side")
        if type(self.policy) is not TargetPolicy:
            raise ContractError("rule selection requires a typed fixed target policy")
        fixed = {"target-1x-fixed": 1, "target-2x-fixed": 2}
        if self.policy.id not in fixed or Fraction(self.policy.multiple) != fixed[self.policy.id]:
            raise ContractError("rule selection requires one of the exact fixed target policies")
        timestamp(self.decision_at)
        if type(self.source_versions) is not tuple or not self.source_versions or any(
                type(value) is not str or not value for value in self.source_versions):
            raise ContractError("rule selection requires immutable observation source versions")
        from trading_research.experiments.e0.observations import E0DecisionSet as ObservationDecisionSet
        if type(self.decision_set) is not ObservationDecisionSet:
            raise ContractError("rule selection must retain its actual typed observation decision set")
        decision_set = self.decision_set
        decision_set.__post_init__()
        from trading_research.experiments.e0.candidates import Contact
        for row in decision_set.rows:
            row.__post_init__()
            if row.contact is not None:
                contact = row.contact
                if (type(contact) is not Contact
                        or (contact.object_id, contact.object_version, contact.at,
                            contact.visit, contact.approach, contact.fade_side) !=
                           (row.object_id, row.object_version, row.cut,
                            row.visit, row.approach, row.fade_side)
                        or not row.band.contains(contact.price)
                        or contact.fade_side != (None if contact.approach is None else -contact.approach)):
                    raise ContractError("rule contact differs from its actual candidate observation")
        if (tuple(sorted(decision_set.rows, key=lambda row: row.order_key)) != decision_set.rows
                or len({row.id for row in decision_set.rows}) != len(decision_set.rows)):
            raise ContractError("rule decision set changed its exact ordered candidate population")
        selected = next((row for row in decision_set.rows if row.contact is not None
                         and row.side in (-1, 1) and row.fade_side == row.side), None)
        if selected is None:
            raise DependencyUnavailable("no first inward fade is available at the observation cut")
        if ((self.decision_set_id, self.candidate_id, self.side, self.decision_at,
             self.row_version, self.object_version, self.source_version,
             self.observation_version, self.source_versions) !=
                (decision_set.id, selected.id, selected.side, decision_set.cut,
                 selected.version, selected.object_version, selected.source_version,
                 digest((decision_set.version, selected.version, selected.contact)),
                 decision_set.source_versions)):
            raise ContractError("rule selection differs from its first actual inward fade observation")

    @classmethod
    def from_decision_set(cls, decision_set: Any, *, policy: TargetPolicy) -> "E0RuleSelection":
        """Select the first inward fade from the actual observation decision set."""

        from trading_research.experiments.e0.observations import E0DecisionSet as ObservationDecisionSet
        if type(decision_set) is not ObservationDecisionSet:
            raise ContractError("rule selection requires an actual observations.E0DecisionSet")
        if type(policy) is not TargetPolicy:
            raise ContractError("rule selection requires a typed target policy")
        contacts = tuple(row for row in decision_set.rows if row.contact is not None and row.side in (-1, 1))
        selected = next((row for row in contacts if row.fade_side == row.side), None)
        if selected is None:
            raise DependencyUnavailable("no first inward fade is available at the observation cut")
        if selected.known_at > decision_set.cut or selected.decision_set_id != decision_set.id:
            raise ContractError("rule selection row is not available in its observation decision set")
        return cls(decision_set.id, selected.id, selected.side, policy, decision_set.cut,
                   selected.version, selected.object_version, selected.source_version,
                   digest((decision_set.version, selected.version, selected.contact)),
                   tuple(decision_set.source_versions), decision_set)


@dataclass(frozen=True)
class E0ActionValue:
    """Complete expected value for one candidate under one target policy."""

    candidate_id: str
    policy: TargetPolicy
    target_probability: Decimal | Fraction
    stop_probability: Decimal | Fraction
    deadline_probability: Decimal | Fraction
    target_net_usd: Decimal | Fraction
    stop_net_usd: Decimal | Fraction
    deadline_net_usd: Decimal | Fraction
    decision_at: int
    known_at: int
    model_version: str
    target_version: str
    fold_id: str
    feature_version: str
    calibrator_version: str | None = None
    source_version: str = ""
    object_version: str = ""
    decision_set_id: str = ""
    side: int = 1
    horizon_end: int | None = None
    intent_id: str | None = None
    expiry_at: int | None = None
    uncertainty: str = "declared_complete_distribution"
    occupancy_end: int | None = None
    risk_reserve_usd: Decimal | Fraction = Decimal(0)
    complete: bool = True
    unavailable_reason: str | None = None
    nonfill_probability: Decimal | Fraction | None = None
    opportunity: Opportunity | None = None
    artifact_evidence: E0ModelArtifactEvidence | None = None

    def __post_init__(self) -> None:
        _name(self.candidate_id, "candidate")
        if type(self.policy) is not TargetPolicy:
            raise ContractError("E0 action value requires a typed registered target policy")
        for at, label in ((self.decision_at, "decision"), (self.known_at, "value-known")):
            timestamp(at)
            if at < 0:
                raise ContractError(f"{label} clock cannot use a sentinel")
        if self.known_at > self.decision_at:
            raise DependencyUnavailable("value artifact is not available at its decision cut")
        if self.horizon_end is not None:
            timestamp(self.horizon_end)
            if self.horizon_end <= self.decision_at:
                raise ContractError("E0 target horizon must follow the decision cut")
        if self.expiry_at is not None:
            timestamp(self.expiry_at)
            if self.expiry_at <= self.decision_at:
                raise ContractError("E0 intent expiry must follow the decision cut")
        if self.occupancy_end is not None:
            timestamp(self.occupancy_end)
            if self.occupancy_end <= self.decision_at:
                raise ContractError("action occupancy must follow the decision cut")
        if type(self.side) is not int or self.side not in (-1, 1):
            raise ContractError("E0 action value side must be signed")
        for value, label in ((self.target_probability, "target probability"),
                             (self.stop_probability, "stop probability"),
                             (self.deadline_probability, "deadline probability")):
            _fraction(value, label, unit=True)
        probabilities = tuple(_fraction(value, label, unit=True) for value, label in (
            (self.target_probability, "target probability"),
            (self.stop_probability, "stop probability"),
            (self.deadline_probability, "deadline probability")))
        if sum(probabilities, Fraction(0)) != 1:
            raise ContractError("complete E0 bracket probabilities must sum to one")
        if self.nonfill_probability is not None and _fraction(self.nonfill_probability, "non-fill probability", unit=True) != probabilities[2]:
            raise ContractError("deadline and non-fill probability disagree")
        for value, label in ((self.target_net_usd, "target net"),
                             (self.stop_net_usd, "stop net"),
                             (self.deadline_net_usd, "deadline net"),
                             (self.risk_reserve_usd, "risk reserve")):
            _number(value, label)
        if _fraction(self.risk_reserve_usd, "risk reserve") < 0:
            raise ContractError("risk reserve must be nonnegative")
        for value, label in ((self.model_version, "model"), (self.target_version, "target"),
                             (self.fold_id, "fold"), (self.feature_version, "feature")):
            _name(value, label)
        for value, label in ((self.calibrator_version, "calibrator"), (self.source_version, "source"),
                             (self.object_version, "object"), (self.decision_set_id, "decision set")):
            if value:
                _name(value, label)
        if self.intent_id is not None:
            _name(self.intent_id, "intent")
        if type(self.complete) is not bool:
            raise ContractError("value completeness must be explicit")
        if self.opportunity is not None and type(self.opportunity) is not Opportunity:
            raise ContractError("action sidecar opportunity must use the common typed port")
        if self.artifact_evidence is not None and type(self.artifact_evidence) not in (
                E0SyntheticNumericalEvidence, E0CommittedPredictionEvidence):
            raise ContractError("E0 action value requires typed artifact evidence")

    @property
    def probabilities(self) -> tuple[Fraction, Fraction, Fraction]:
        return tuple(_fraction(value, label, unit=True) for value, label in (
            (self.target_probability, "target probability"),
            (self.stop_probability, "stop probability"),
            (self.deadline_probability, "deadline probability")))

    @property
    def expected_net_usd(self) -> Decimal:
        return _sum_decimal(_weighted_decimal(probability, value) for probability, value in zip(
            self.probabilities, (self.target_net_usd, self.stop_net_usd, self.deadline_net_usd)))

    @property
    def expected_net(self) -> Decimal:
        return self.expected_net_usd

    @property
    def target_policy(self) -> TargetPolicy:
        return self.policy

    @property
    def policy_id(self) -> str:
        return self.policy.id

    @property
    def target_multiple(self) -> Fraction:
        return _fraction(self.policy.multiple, "target multiple")

    @property
    def version(self) -> str:
        return digest(self)

    def record(self) -> dict[str, Any]:
        return _action_value_record(self)


# The expression above is intentionally replaced below with a regular helper
# so record() remains easy to read while preserving the immutable wire shape.
def _action_value_record(value: E0ActionValue) -> dict[str, Any]:
    return {
        "schema": "E0ActionValue.v1",
        "candidate_id": value.candidate_id,
        "policy": value.policy,
        "probabilities": tuple(value.probabilities),
        "target_net_usd": value.target_net_usd,
        "stop_net_usd": value.stop_net_usd,
        "deadline_net_usd": value.deadline_net_usd,
        "decision_at": value.decision_at,
        "known_at": value.known_at,
        "model_version": value.model_version,
        "calibrator_version": value.calibrator_version,
        "target_version": value.target_version,
        "fold_id": value.fold_id,
        "feature_version": value.feature_version,
        "source_version": value.source_version,
        "object_version": value.object_version,
        "decision_set_id": value.decision_set_id,
        "side": value.side,
        "horizon_end": value.horizon_end,
        "intent_id": value.intent_id,
        "expiry_at": value.expiry_at,
        "uncertainty": value.uncertainty,
        "occupancy_end": value.occupancy_end,
        "risk_reserve_usd": value.risk_reserve_usd,
        "complete": value.complete,
        "unavailable_reason": value.unavailable_reason,
        "artifact_evidence": value.artifact_evidence,
    }


@dataclass(frozen=True)
class E0DecisionSet:
    """Complete candidate population at one information cut."""

    id: str
    at: int
    candidate_ids: tuple[str, ...] = ()
    opportunities: tuple[Opportunity, ...] = ()
    source_event_ids: tuple[str, ...] = ()
    source_version: str = ""
    policy_version: str = "E0-selection-v1"
    pre_action_state_version: str = ""
    completed_at: int | None = None

    def __post_init__(self) -> None:
        _name(self.id, "decision set")
        timestamp(self.at)
        if self.completed_at is not None:
            timestamp(self.completed_at)
            if self.completed_at < self.at:
                raise ContractError("decision-set completion precedes its cut")
        if type(self.candidate_ids) is not tuple or any(type(v) is not str or not v for v in self.candidate_ids):
            raise ContractError("decision set candidate IDs must be immutable strings")
        if len(set(self.candidate_ids)) != len(self.candidate_ids):
            raise ContractError("decision set candidate IDs must be unique")
        if type(self.opportunities) is not tuple or any(type(v) is not Opportunity for v in self.opportunities):
            raise ContractError("decision set opportunities must use the common typed port")
        opportunity_ids = tuple(o.id for o in self.opportunities)
        if len(set(opportunity_ids)) != len(opportunity_ids):
            raise ContractError("decision set opportunities must be unique")
        if self.candidate_ids and opportunity_ids and tuple(self.candidate_ids) != opportunity_ids:
            raise ContractError("candidate population and opportunities have different order or membership")
        if self.source_version:
            _name(self.source_version, "decision-set source")
        if self.policy_version:
            _name(self.policy_version, "decision-set policy")
        if self.pre_action_state_version:
            _name(self.pre_action_state_version, "pre-action state")

    @property
    def version(self) -> str:
        return digest(self)


DecisionSet = E0DecisionSet
ActionValue = E0ActionValue
BracketValue = E0ActionValue
PolicyInput = E0ActionValue


def _attr(value: Any, *names: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        for name in names:
            if name in value:
                return value[name]
    else:
        for name in names:
            if hasattr(value, name):
                return getattr(value, name)
    return default


def _metadata(value: Any) -> dict[str, Any]:
    """Extract common fit metadata without depending on a particular learner."""

    if value is None:
        return {}
    result = {
        "id": _attr(value, "id", "version", "artifact_id"),
        "fitted_at": _attr(value, "fitted_at", "fit_at", "known_at"),
        "target_version": _attr(value, "target_version"),
        "fold_version": _attr(value, "fold_version"),
        "fold_id": _attr(value, "fold_id", "fold_version"),
        "model_version": _attr(value, "model_version", "prediction_version"),
        "calibrator_version": _attr(value, "calibrator_version"),
        "feature_version": _attr(value, "feature_version"),
        "source_version": _attr(value, "source_version"),
        "kind": _attr(value, "kind"),
        "target_versions": _attr(value, "target_versions"),
    }
    artifact = _attr(value, "artifact")
    if artifact is not None:
        nested = _metadata(artifact)
        for key, item in nested.items():
            if result.get(key) is None:
                result[key] = item
    if result.get("fitted_at") is None:
        artifacts = _attr(value, "fit_artifacts")
        if artifacts:
            times = [_attr(a, "fitted_at", "fit_at") for a in artifacts]
            times = [t for t in times if type(t) is int]
            if times:
                result["fitted_at"] = max(times)
    return result


def _artifact_rows(artifacts: Any, calibration: Any) -> list[Any]:
    rows: list[Any] = []
    if artifacts is not None:
        if isinstance(artifacts, Mapping):
            rows.extend(artifacts.values())
        elif isinstance(artifacts, (tuple, list, set)):
            rows.extend(artifacts)
        else:
            rows.append(artifacts)
    if calibration is not None:
        rows.append(calibration)
    return rows


def _decision_set_parts(decision_set: Any) -> tuple[str, int, tuple[str, ...], tuple[Opportunity, ...], str, str, int]:
    from trading_research.experiments.e0.observations import E0DecisionSet as PopulationDecisionSet
    if type(decision_set) is PopulationDecisionSet:
        return (decision_set.id, decision_set.cut, tuple(row.id for row in decision_set.rows), (),
                digest(decision_set.source_versions), "", decision_set.cut)
    if isinstance(decision_set, E0DecisionSet):
        return (decision_set.id, decision_set.at,
                decision_set.candidate_ids or tuple(o.id for o in decision_set.opportunities),
                decision_set.opportunities, decision_set.source_version,
                decision_set.pre_action_state_version, decision_set.completed_at or decision_set.at)
    ds_id = _attr(decision_set, "id", "decision_set_id", "version")
    at = _attr(decision_set, "at", "decision_at", "cut")
    if ds_id is None or at is None:
        raise ContractError("score_and_decide_e0 requires a typed decision-set identity and cut")
    timestamp(at)
    opportunities = _attr(decision_set, "opportunities", "candidates", default=()) or ()
    if type(opportunities) is not tuple:
        opportunities = tuple(opportunities)
    if any(type(o) is not Opportunity for o in opportunities):
        opportunities = ()
    ids = _attr(decision_set, "candidate_ids", "ids", default=()) or tuple(o.id for o in opportunities)
    ids = tuple(ids)
    source = _attr(decision_set, "source_version", "version", default="") or ""
    state = _attr(decision_set, "pre_action_state_version", "state_version", default="") or ""
    completed = _attr(decision_set, "completed_at", "known_at", default=at) or at
    timestamp(completed)
    return _name(ds_id, "decision set"), at, ids, opportunities, source, state, completed


def _flatten_candidate_values(bracket_candidates: Any, candidate_id: str) -> tuple[Any, ...]:
    if isinstance(bracket_candidates, Mapping):
        row = bracket_candidates.get(candidate_id)
    else:
        row = next((v for v in bracket_candidates if _attr(v, "candidate_id", "id") == candidate_id), None)
    if row is None:
        return ()
    if isinstance(row, Mapping):
        for key in ("values", "policies", "policy_values", "target_policies"):
            if key in row and isinstance(row[key], (tuple, list, set)):
                return tuple(row[key])
    for name in ("values", "policies", "policy_values", "target_policies"):
        nested = getattr(row, name, None)
        if nested is not None and isinstance(nested, (tuple, list, set)):
            return tuple(nested)
    if isinstance(row, (tuple, list, set)):
        return tuple(row)
    return (row,)


def _coerce_policy(value: Any) -> TargetPolicy:
    if isinstance(value, TargetPolicy):
        return value
    if type(value) is str:
        return TargetPolicy(value)
    if isinstance(value, Mapping):
        return TargetPolicy(id=value.get("id", value.get("policy_id")),
                            multiple=value.get("multiple", value.get("target_multiple", 1)),
                            target_ticks=value.get("target_ticks"),
                            policy_version=value.get("policy_version"),
                            source_version=value.get("source_version"))
    return TargetPolicy(id=_attr(value, "id", "policy_id"),
                        multiple=_attr(value, "multiple", "target_multiple", default=1),
                        target_ticks=_attr(value, "target_ticks"),
                        policy_version=_attr(value, "policy_version"),
                        source_version=_attr(value, "source_version"))


def _coerce_value(row: Any, *, candidate_id: str, decision_set_id: str, decision_at: int) -> E0ActionValue:
    if isinstance(row, E0ActionValue):
        if row.candidate_id != candidate_id or row.decision_set_id not in ("", decision_set_id):
            raise ContractError("action value is bound to a different candidate or decision set")
        return row
    policy = _coerce_policy(_attr(row, "policy", "plan_policy", "target_policy", "policy_id"))
    def get(*names: str, default: Any = None) -> Any:
        return _attr(row, *names, default=default)
    known = get("known_at", "available_at", "computed_at", default=decision_at)
    at = get("decision_at", "cut", default=decision_at)
    target_probability = get("target_probability", "target_first_probability", "p_target")
    stop_probability = get("stop_probability", "stop_first_probability", "p_stop")
    deadline_probability = get("deadline_probability", "nonfill_probability", "p_deadline", "p_nonfill")
    target_net = get("target_net_usd", "target_value_usd", "target_net")
    stop_net = get("stop_net_usd", "stop_value_usd", "stop_net")
    deadline_net = get("deadline_net_usd", "nonfill_net_usd", "deadline_value_usd", "deadline_net", default=Decimal(0))
    missing = [name for name, item in (("target_probability", target_probability), ("stop_probability", stop_probability),
                                        ("deadline_probability", deadline_probability), ("target_net_usd", target_net),
                                        ("stop_net_usd", stop_net)) if item is None]
    if missing:
        raise ContractError("complete E0 action value missing " + ", ".join(missing))
    return E0ActionValue(
        candidate_id=candidate_id, policy=policy,
        target_probability=target_probability, stop_probability=stop_probability,
        deadline_probability=deadline_probability, target_net_usd=target_net,
        stop_net_usd=stop_net, deadline_net_usd=deadline_net,
        decision_at=at, known_at=known,
        model_version=get("model_version", "model_id", default=""),
        target_version=get("target_version", "target_id", default=""),
        fold_id=get("fold_id", "fold_version", default=""),
        feature_version=get("feature_version", "features_version", default=""),
        calibrator_version=get("calibrator_version", "calibration_version"),
        source_version=get("source_version", default=""), object_version=get("object_version", default=""),
        decision_set_id=get("decision_set_id", default=decision_set_id),
        side=get("side", default=1), horizon_end=get("horizon_end"), intent_id=get("intent_id"),
        expiry_at=get("expiry_at", "expires_at"), uncertainty=get("uncertainty", default="declared_complete_distribution"),
        occupancy_end=get("occupancy_end", "known_flat_at"), risk_reserve_usd=get("risk_reserve_usd", default=Decimal(0)),
        complete=get("complete", "distribution_complete", default=True),
        unavailable_reason=get("unavailable_reason"),
        nonfill_probability=get("nonfill_probability"), opportunity=get("opportunity"),
        artifact_evidence=get("artifact_evidence", "model_artifact_evidence"))


def _state_value(state: Any, *names: str, default: Any = None) -> Any:
    return _attr(state, *names, default=default)


def _make_opportunity(value: E0ActionValue, *, decision_set_id: str, at: int,
                      existing: Opportunity | None = None) -> Opportunity:
    if existing is not None:
        if existing.id != value.candidate_id or existing.decision_set_id != decision_set_id:
            raise ContractError("opportunity candidate or decision-set identity changed")
        opportunity = existing
    else:
        known = value.known_at
        clocks = Clocks(event_at=at, known_at=known, source_version=value.source_version or value.version,
                        basis=AvailabilityBasis.PUBLISHED, published_at=known)
        opportunity = Opportunity(value.candidate_id, decision_set_id, value.object_version or value.version,
                                  (value.source_version or value.version,),
                                  value.side, (value.policy.id,), (value.model_version,),
                                  (value.candidate_id + ":wait",), clocks, (), value.unavailable_reason)
    return opportunity


def _attach(obj: Any, name: str, value: Any) -> None:
    # The common messages intentionally keep a compact legacy wire shape.  E0
    # bindings are sidecars so that adding them cannot silently alter a prior
    # protocol hash.
    try:
        object.__setattr__(obj, name, value)
    except (AttributeError, TypeError):
        pass


def _artifact_checks(values: tuple[E0ActionValue, ...], artifacts: Any, calibration: Any,
                     *, decision_at: int) -> str | None:
    # A negative/unfinished population may legitimately be evaluated without
    # a model closure: it cannot authorize an entry.  A positive complete row
    # must carry an explicit typed artifact binding, however.  This preserves
    # the all-negative flat/wait control without leaving a learned admission
    # path open when ``model_artifacts`` is omitted.
    actionable = tuple(value for value in values
                       if value.complete and not value.unavailable_reason
                       and value.side in (-1, 1) and value.expected_net_usd > 0)
    if not actionable:
        return None
    rows = _artifact_rows(artifacts, calibration)
    if not rows:
        embedded = tuple(value.artifact_evidence for value in actionable
                         if value.artifact_evidence is not None)
        if len(embedded) == len(actionable):
            rows = []
            for evidence in embedded:
                if not any(evidence == prior for prior in rows):
                    rows.append(evidence)
        else:
            return "model artifact evidence unavailable at decision cut"
    if any(type(row) not in (E0SyntheticNumericalEvidence, E0CommittedPredictionEvidence)
           for row in rows):
        return "typed model artifact evidence is required"
    provided_ids = set()
    declared_targets = set()
    declared_folds = set()
    declared_features = set()
    plain_targets = []
    for artifact in rows:
        meta = _metadata(artifact)
        fitted = meta.get("fitted_at")
        if fitted is not None:
            timestamp(fitted)
            if fitted > decision_at:
                return "future fitted artifact unavailable at decision cut"
        for name in (meta.get("id"), meta.get("model_version"), meta.get("calibrator_version")):
            if name:
                provided_ids.add(name)
        target = meta.get("target_version")
        if target:
            declared_targets.add(target)
            plain_targets.append(target)
        for field, target_set in ((meta.get("fold_id"), declared_folds),
                                  (meta.get("feature_version"), declared_features)):
            if field:
                target_set.add(field)
        for composite in (meta.get("target_versions") or ()):
            if composite:
                declared_targets.add(composite)
    # Separate plain head artifacts must not be allowed to masquerade as one
    # composite prediction.  The committed evidence class carries the exact
    # three-head aggregate explicitly and is the only multi-head exception.
    if len(rows) > 1 and len(set(plain_targets)) > 1 and not any(
            isinstance(row, E0CommittedPredictionEvidence) for row in rows):
        return "target/horizon provenance mismatch"
    for value in actionable:
        if type(value.artifact_evidence) is E0CommittedPredictionEvidence:
            committed = value.artifact_evidence
            committed.__post_init__()
            if not any(type(row) is E0CommittedPredictionEvidence
                       and row == committed for row in rows):
                return "actual committed prediction evidence is missing"
            if ((value.candidate_id, value.decision_at, value.policy.id) !=
                    (committed.sample_id, committed.decision_at, committed.policy_version)
                    or (Fraction(value.target_probability), Fraction(value.stop_probability),
                        Fraction(value.deadline_probability)) !=
                       tuple(p for _, p in committed.probabilities)
                    or value.nonfill_probability not in (None, 0)):
                return "value probabilities or query differ from actual committed prediction"
        elif any(type(row) is E0CommittedPredictionEvidence
                 and row.prediction_version == value.model_version for row in rows):
            return "value lacks its exact committed prediction evidence"
        if not declared_targets or value.target_version not in declared_targets:
            return "target/horizon provenance mismatch"
        if not declared_folds or value.fold_id not in declared_folds:
            return "fold provenance mismatch"
        if not declared_features or value.feature_version not in declared_features:
            return "feature provenance mismatch"
        if value.model_version not in provided_ids:
            return "model artifact identity mismatch"
        if value.calibrator_version and value.calibrator_version not in provided_ids:
            return "model artifact identity mismatch"
        embedded_meta = _metadata(value.artifact_evidence) if value.artifact_evidence is not None else {}
        if (embedded_meta.get("source_version") and value.source_version
                and embedded_meta.get("source_version") != value.source_version):
            return "source provenance mismatch"
    return None


def _model_ids(values: tuple[E0ActionValue, ...], artifacts: Any, calibration: Any) -> tuple[str, ...]:
    result: list[str] = []
    rows = []
    if artifacts is not None:
        rows.extend(artifacts.values() if isinstance(artifacts, Mapping) else artifacts if isinstance(artifacts, (tuple, list)) else (artifacts,))
    if calibration is not None:
        rows.append(calibration)
    for row in rows:
        ident = _metadata(row).get("id")
        if ident and ident not in result:
            result.append(ident)
    for row in values:
        for ident in (row.model_version, row.calibrator_version):
            if ident and ident not in result:
                result.append(ident)
    return tuple(result)


def score_and_decide_e0(*, decision_set, model_artifacts=None, calibration=None,
                        bracket_candidates, account_state=None, risk_state=None) -> tuple[tuple[Opportunity, ...], Decision]:
    """Create complete E0 opportunity sidecars and one canonical decision.

    ``bracket_candidates`` may be a mapping from candidate ID to one value row,
    a mapping to a tuple of target-policy rows, or an iterable of such rows.
    Values are never inferred from outcomes.  The function returns an explicit
    abstention/flat decision when a dependency is unavailable or every complete
    action value is non-positive.
    """

    ds_id, at, ids, existing_opportunities, source_version, state_version, completed = _decision_set_parts(decision_set)
    if not ids:
        if isinstance(bracket_candidates, Mapping):
            ids = tuple(bracket_candidates)
        else:
            ids = tuple(_attr(v, "candidate_id", "id") for v in bracket_candidates)
    if any(type(v) is not str or not v for v in ids) or len(set(ids)) != len(ids):
        raise ContractError("complete ordered candidate population is required")
    existing_by_id = {o.id: o for o in existing_opportunities}
    all_values: dict[str, tuple[E0ActionValue, ...]] = {}
    global_reason = None
    for candidate_id in ids:
        rows = tuple(_coerce_value(v, candidate_id=candidate_id, decision_set_id=ds_id, decision_at=at)
                     for v in _flatten_candidate_values(bracket_candidates, candidate_id))
        if rows and any(v.decision_at != at for v in rows):
            raise ContractError("candidate value belongs to a different decision cut")
        if rows:
            all_values[candidate_id] = rows
    flat_values = tuple(v for rows in all_values.values() for v in rows)
    global_reason = _artifact_checks(flat_values, model_artifacts, calibration, decision_at=at)
    output_opportunities: list[Opportunity] = []
    rejected: list[tuple[str, str]] = []
    selected: tuple[str, E0ActionValue] | None = None
    best_values: dict[str, E0ActionValue] = {}
    for candidate_id in ids:
        rows = all_values.get(candidate_id, ())
        if not rows:
            reason = "no_action_candidate"
            rejected.append((candidate_id, reason))
            continue
        if global_reason:
            rejected.append((candidate_id, global_reason))
            continue
        if candidate_id.lower().startswith("background") or _attr(rows[0], "side", default=1) == 0:
            # A background row is not an actionable contact.  If its source
            # row is itself incomplete, retain the stronger missing-action
            # reason used by the frozen all-negative case instead of implying
            # that an incomplete value was evaluated.
            rejected.append((candidate_id, "no_action_candidate" if any(
                not row.complete or row.unavailable_reason for row in rows)
                else "no_candidate_contact"))
            continue
        if any(not row.complete or row.unavailable_reason for row in rows):
            reason = next((row.unavailable_reason for row in rows if row.unavailable_reason), None)
            rejected.append((candidate_id, reason or "complete bracket outcome distribution is required"))
            continue
        value = max(rows, key=lambda row: (row.expected_net_usd,
                                           -_fraction(row.policy.multiple, "target multiple"),
                                           row.policy.id))
        best_values[candidate_id] = value
        if value.expected_net_usd <= 0:
            # The all-negative fixture uses the more conservative wording;
            # mixed populations retain the explicit negative-value reason.
            rejected.append((candidate_id, "nonpositive_conservative_value"))
        else:
            if selected is None or value.expected_net_usd > selected[1].expected_net_usd:
                selected = (candidate_id, value)
    if any(value.expected_net_usd > 0 for value in best_values.values()):
        rejected = [(candidate_id, "negative_complete_value" if reason == "nonpositive_conservative_value" else reason)
                    for candidate_id, reason in rejected]
    positive = bool(selected)
    risk_reason = None
    if positive:
        state = risk_state if risk_state is not None else account_state
        known = _state_value(state, "state_known", "known", default=True)
        if known is False:
            risk_reason = "unknown account, position, pending order or quote state"
        elif _state_value(state, "account_flat", "flat", default=True) is False or _state_value(state, "position", default=0):
            risk_reason = "account is not flat with reconciled empty broker order state"
        elif _state_value(state, "pending_orders", "pending", "broker_open_orders", default=()):
            risk_reason = "pending or unknown order occupies one-mini action state"
        elif _state_value(state, "entry_eligible", "allowed", default=True) is False:
            risk_reason = _state_value(state, "reason", "halt_reason", default="risk state veto")
        if risk_reason:
            rejected.append((selected[0], risk_reason))
            selected = None
    if global_reason:
        selected_action = "abstain"
        risk_verdict = "abstain:" + global_reason
        rejected = [(candidate_id, global_reason) for candidate_id in ids]
    elif not positive and not best_values:
        selected_action = "abstain" if any(reason in {"complete bracket outcome distribution is required", "target/horizon provenance mismatch"} or reason.startswith("future ") for _, reason in rejected) else "flat_or_wait"
        risk_verdict = "abstain:" + (rejected[0][1] if rejected else "no complete candidate values") if selected_action == "abstain" else "not_called_for_entry"
    elif selected is None and best_values and not any(value.expected_net_usd > 0 for value in best_values.values()):
        selected_action = "flat_or_wait"
        risk_verdict = "not_called_for_entry"
    elif selected is None:
        selected_action = "flat_or_wait"
        risk_verdict = "risk_veto:" + (risk_reason or "nonpositive conservative value")
    else:
        candidate_id, value = selected
        selected_action = f"enter_{'long' if value.side == 1 else 'short'}_{value.policy.id}"
        risk_verdict = "pending_independent_gate"
    opportunity_values = all_values
    for candidate_id in ids:
        if candidate_id not in best_values:
            continue
        rows = opportunity_values[candidate_id]
        chosen = best_values[candidate_id]
        opportunity = _make_opportunity(chosen, decision_set_id=ds_id, at=at, existing=existing_by_id.get(candidate_id))
        _attach(opportunity, "e0_values", rows)
        _attach(opportunity, "selected_policy", best_values.get(candidate_id).policy if candidate_id in best_values else None)
        _attach(opportunity, "selected_value", best_values.get(candidate_id))
        output_opportunities.append(opportunity)
    # Preserve the declared population order even if a candidate was missing a
    # value row; no hidden sorting may change the decision-set identity.
    output_opportunities.sort(key=lambda value: ids.index(value.id))
    selected_value = selected[1] if selected is not None else None
    intent_id = selected_value.intent_id if selected_value is not None else None
    expiry = selected_value.expiry_at if selected_value is not None else None
    if expiry is None and selected_value is not None:
        expiry = selected_value.horizon_end
    pre_state = state_version or _state_value(account_state, "version", "state_version", default="") or _state_value(risk_state, "version", "state_version", default="") or digest({"account": account_state, "risk": risk_state})
    decision_id = _attr(decision_set, "decision_id", "id", default=None) or digest({"schema": "E0Decision.v1", "decision_set": ds_id, "at": at, "candidates": ids, "values": tuple(_action_value_record(v) for v in flat_values)})
    decision = Decision(decision_id, at, ids, selected_action, tuple(rejected), pre_state,
                        _model_ids(flat_values, model_artifacts, calibration), intent_id, expiry,
                        risk_verdict, max((completed, *(v.known_at for v in flat_values)), default=completed), None)
    _attach(decision, "decision_set_id", ds_id)
    _attach(decision, "selected_policy_id", selected_value.policy.id if selected_value else None)
    _attach(decision, "selected_value", selected_value)
    _attach(decision, "opportunities", tuple(output_opportunities))
    _attach(decision, "value_sidecars", tuple(flat_values))
    _attach(decision, "source_version", source_version)
    return tuple(output_opportunities), decision


def action_value(*args, **kwargs) -> E0ActionValue:
    """Small named constructor useful to runners and fixture builders."""

    return E0ActionValue(*args, **kwargs)


__all__ = [
    "TargetPolicy", "E0SyntheticNumericalEvidence", "E0CommittedPredictionEvidence",
    "E0ModelArtifactEvidence", "E0RuleSelection", "E0ActionValue", "ActionValue", "BracketValue", "PolicyInput",
    "E0DecisionSet", "DecisionSet", "score_and_decide_e0", "action_value",
]
