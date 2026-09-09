"""Frozen historical E0 fit, selection and calibration stages.

Evaluation labels are never selection inputs. A complete bracket distribution
is a separately named normalization of three target-specific binary heads.
"""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from fractions import Fraction
import hashlib
import json
from statistics import fmean
from zoneinfo import ZoneInfo

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.research.calibration import CalibratedBinary, fit_sigmoid_calibration
from trading_research.research.folds import Sample, Fold, chronological_fold
from trading_research.research.models import BinaryExample, BinaryModel, FrequencyModel, fit_frequency, fit_logistic
from trading_research.research.period import ResearchScopeV1
from trading_research.research.scoring import Metric


HISTORICAL_SCOPE = "E0_historical_2022_2025_harness"
FEATURE_COLUMNS = ("side", "object_type", "distance_over_width", "range_position",
                   "prior_rth_distance", "five_minute_return_ticks",
                   "thirty_minute_realized_variation_ticks2", "minute_sine",
                   "minute_cosine", "remaining_minutes")
FREQUENCY_COLUMNS = ("object_type", "side", "distance_over_width")
# Types are the stable integer codes of all nine range and four prior-RTH objects.
FREQUENCY_CUTS = (tuple(float(x) for x in range(1, 13)), (0.,), (.25, .5, 1.))
ROLE_YEARS = (("fit", 2022), ("selection", 2023), ("calibration", 2024),
              ("retrospective_evaluation", 2025))


def bracket_target_payload(policy_version, head):
    if policy_version not in ("target-1x-fixed", "target-2x-fixed") or head not in ("target", "stop", "deadline"):
        raise ContractError("unregistered fixed E0 bracket target descriptor")
    return canonical_json({"schema": "E0BracketTargetV1", "policy_version": policy_version,
        "head": head, "horizon_ns": 900_000_000_000, "endpoint": "original_decision_plus_horizon",
        "route": "local_target_cancel_protection_reconcile_marketable_exit_v1",
        "labels": "actual_complete_native_bracket_outcome", "quantity": 1})


def year_start(year):
    return int(datetime(year, 1, 1, tzinfo=timezone.utc).timestamp()) * 1_000_000_000


@dataclass(frozen=True)
class E0LearningConfig:
    target_version: str
    cohort_version: str
    denominator_id: str
    columns: tuple[str, ...] = FEATURE_COLUMNS
    frequency_columns: tuple[str, ...] = FREQUENCY_COLUMNS
    frequency_cuts: tuple[tuple[float, ...], ...] = FREQUENCY_CUTS
    lambdas: tuple[float, ...] = (.1, 1., 10.)
    calibration_l2: float = .1
    embargo_ns: int = 900_000_000_000
    scope: str = HISTORICAL_SCOPE
    control: str = "full_e0"
    policy_version: str | None = None
    head: str | None = None
    target_payload: bytes | None = None

    def __post_init__(self):
        if (self.scope != HISTORICAL_SCOPE or not all((self.target_version, self.cohort_version,
                self.denominator_id)) or self.lambdas != (.1, 1., 10.) or self.calibration_l2 != .1
                or type(self.embargo_ns) is not int or self.embargo_ns != 900_000_000_000):
            raise ContractError("E0 learning requires the frozen historical scope, target and finite search")
        if self.control not in ("full_e0", "analytic_ridge", "constant_feature", "physical_reach"):
            raise ContractError("unregistered E0 feature control")
        if (self.policy_version is None) != (self.head is None) or self.head not in (None, "target", "stop", "deadline"):
            raise ContractError("a complete bracket head must bind its fixed policy")
        if self.head is not None and (self.target_payload != bracket_target_payload(self.policy_version, self.head)
                or hashlib.sha256(self.target_payload).hexdigest() != self.target_version):
            raise ContractError("E0 target bytes do not bind the exact policy, head and original endpoint")
        if self.target_payload is not None and (type(self.target_payload) is not bytes
                or hashlib.sha256(self.target_payload).hexdigest() != self.target_version):
            raise ContractError("E0 target version differs from its retained target bytes")
        if (type(self.columns) is not tuple or not self.columns or len(set(self.columns)) != len(self.columns)
                or type(self.frequency_columns) is not tuple or not self.frequency_columns
                or not set(self.frequency_columns) <= set(self.columns)
                or len(self.frequency_columns) != len(self.frequency_cuts)):
            raise ContractError("immutable declared input columns and frequency cells required")
        if self.control == "full_e0" and (self.columns, self.frequency_columns, self.frequency_cuts) != (
                FEATURE_COLUMNS, FREQUENCY_COLUMNS, FREQUENCY_CUTS):
            raise ContractError("full E0 must retain every causal feature and the fixed conditional bins")

    @property
    def version(self):
        return digest(self)

    @property
    def research_scope(self):
        return ResearchScopeV1.diagnostic(cohort_id=self.scope + ":" + self.cohort_version,
                                          denominator_id=self.denominator_id)


@dataclass(frozen=True)
class E0Stages:
    population: tuple[Sample, ...]
    role_ids: tuple[tuple[str, tuple[str, ...]], ...]
    fit_fold: Fold
    calibration_fold: Fold
    scope: str
    target_version: str

    @property
    def version(self):
        return digest(self)

    def ids(self, role):
        return dict(self.role_ids)[role]


def e0_stages(population, config: E0LearningConfig):
    if type(config) is not E0LearningConfig:
        raise ContractError("typed historical E0 learning configuration required")
    config.__post_init__()
    rows = tuple(sorted(population, key=lambda s: (s.decision_at, s.id)))
    if (not rows or len(rows) > 200000 or any(type(s) is not Sample for s in rows)
            or len({s.id for s in rows}) != len(rows)):
        raise ContractError("bounded complete unique E0 sample population required")
    role_ids = []
    for s in rows:
        s.__post_init__()
        day = date.fromisoformat(s.date_group)
        if (day.year not in (2022, 2023, 2024, 2025) or s.target_version != config.target_version
                or not year_start(day.year) <= s.decision_at < year_start(day.year + 1)):
            raise ContractError("E0 row crosses the frozen year, date-group or target scope")
        actual_day = datetime.fromtimestamp(s.decision_at // 1_000_000_000,
                                            ZoneInfo("America/New_York")).date()
        if day != actual_day:
            raise ContractError("E0 date group differs from the actual New York business date")
    for role, year in ROLE_YEARS:
        ids = tuple(s.id for s in rows if date.fromisoformat(s.date_group).year == year)
        if not ids:
            raise DependencyUnavailable("E0 historical stage lacks complete rows: " + role)
        role_ids.append((role, ids))
    fit = chronological_fold(rows, id=config.version + ":fit-2022", fit_at=year_start(2023),
        evaluation_start=year_start(2023), evaluation_end=year_start(2026),
        training_start=year_start(2022), embargo_ns=config.embargo_ns, scope=config.research_scope)
    calibration = chronological_fold(rows, id=config.version + ":calibrate-2024", fit_at=year_start(2025),
        evaluation_start=year_start(2025), evaluation_end=year_start(2026),
        training_start=year_start(2024), embargo_ns=config.embargo_ns, scope=config.research_scope)
    return E0Stages(rows, tuple(role_ids), fit, calibration, config.scope, config.target_version)


def audit_training_intervals(training, heldout, *, embargo_ns):
    """Audit proposed memberships, including post-heldout dependency intervals.

    Actual forward fit membership is compiled separately. This rejects a split
    date group and exposes overlap/embargo even if the row cannot train yet.
    """
    if type(embargo_ns) is not int or embargo_ns < 0:
        raise ContractError("exact nonnegative embargo required")
    train, test = tuple(training), tuple(heldout)
    if any(type(s) is not Sample for s in (*train, *test)) or not test:
        raise ContractError("typed proposed training and heldout samples required")
    if {s.date_group for s in train} & {s.date_group for s in test}:
        raise ContractError("a date group assigned to heldout cannot be split into training even without interval overlap")
    return tuple((s.id, "purged" if any(
        s.decision_at <= h.dependency_end + embargo_ns and s.dependency_end >= h.decision_at - embargo_ns
        for h in test) else "admitted") for s in train)


@dataclass(frozen=True)
class E0BinaryFit:
    config: E0LearningConfig
    stages: E0Stages
    frequency: FrequencyModel
    logistic_candidates: tuple[BinaryModel, ...]
    selection_scores: tuple[tuple[float, float], ...]
    selected: BinaryModel | FrequencyModel
    calibrated: CalibratedBinary | FrequencyModel
    selection_read_manifests: tuple
    fallback_reason: str | None

    @property
    def version(self):
        return digest(self)

    @property
    def selected_lambda(self):
        return self.selected.l2_strength if isinstance(self.selected, BinaryModel) else None


def fit_e0_binary(examples, config: E0LearningConfig):
    examples = tuple(examples)
    if any(type(e) is not BinaryExample for e in examples):
        raise ContractError("E0 fit consumes typed feature reads and observed binary labels")
    stages = e0_stages(tuple(e.sample for e in examples), config)
    by = {e.sample.id: e for e in examples}
    late = tuple(identity for identity in stages.ids("selection")
                 if by[identity].sample.label_known_at > year_start(2024)
                 or by[identity].sample.dependency_end >= year_start(2024))
    if late:
        raise DependencyUnavailable("E0 selection labels unavailable at frozen 2023 stage: " + ",".join(late))
    frequency = fit_frequency(examples, stages.fit_fold, config.frequency_columns,
        cuts=config.frequency_cuts, prior_strength=2., prior_center="uniform", scope=config.research_scope)
    if len({by[s].outcome for s in stages.fit_fold.training_ids}) < 2:
        return E0BinaryFit(config, stages, frequency, (), (), frequency, frequency, (),
                           "single_class_registered_conditional_frequency_fallback")
    metric = Metric("log_loss", probability_floor=1e-12)
    candidates, scores, manifests = [], [], []
    for strength in config.lambdas:
        model = fit_logistic(examples, stages.fit_fold, config.columns,
                             l2_strength=strength, scope=config.research_scope)
        rows = []
        for identity in stages.ids("selection"):
            example = by[identity]
            prediction, reads = model.predict(example)
            rows.append(metric.loss(example.outcome, prediction))
            manifests.append((strength, identity, prediction, reads))
        candidates.append(model)
        scores.append((strength, fmean(rows)))
    selected_strength = min(scores, key=lambda pair: (pair[1], pair[0]))[0]
    selected = next(model for model in candidates if model.l2_strength == selected_strength)
    calibrated = fit_sigmoid_calibration(selected, examples, stages.calibration_fold,
        l2_strength=config.calibration_l2, scope=config.research_scope)
    return E0BinaryFit(config, stages, frequency, tuple(candidates), tuple(scores), selected,
                       calibrated, tuple(manifests), None)


@dataclass(frozen=True)
class E0BracketPrediction:
    branch: str
    policy_version: str
    sample_id: str
    at: int
    probabilities: tuple[tuple[str, Fraction], ...]
    head_evidence: tuple
    normalization: str = "normalized_target_stop_deadline_binary_heads_v1"

    def __post_init__(self):
        if (self.branch not in ("frequency", "logistic") or not self.policy_version
                or tuple(k for k, _ in self.probabilities) != ("target", "stop", "deadline")
                or any(type(p) is not Fraction or not 0 <= p <= 1 for _, p in self.probabilities)
                or sum((p for _, p in self.probabilities), Fraction()) != 1
                or type(self.head_evidence) is not tuple or len(self.head_evidence) != 3
                or self.normalization != "normalized_target_stop_deadline_binary_heads_v1"):
            raise ContractError("complete target-specific bracket probability closure required")
        from trading_research.experiments.e0.learning_store import E0VerifiedHeadReceipt
        from types import MappingProxyType
        raw = []
        for expected, evidence in zip(("target", "stop", "deadline"), self.head_evidence):
            if type(evidence) is not tuple or len(evidence) != 5:
                raise ContractError("exact committed head evidence required")
            name, model_id, target, fold, reads = evidence
            if type(reads) is not MappingProxyType:
                raise ContractError("immutable actual committed reads required")
            receipt = reads.get("verified_head_receipt")
            if (name != expected or type(receipt) is not E0VerifiedHeadReceipt
                    or receipt.model_id != model_id or receipt.fold_version != fold
                    or receipt.request.row_id != self.sample_id
                    or receipt.request.decision_cut != self.at
                    or receipt.request.target_definition_ref.sha256 != target
                    or receipt.fitted_at > self.at
                    or receipt.commit_ref != reads.get("commit_ref")
                    or receipt.model_node_id != reads.get("model_node_id")
                    or receipt.source_node_id != reads.get("source_node_id")
                    or receipt.request != reads.get("request")
                    or receipt.request.fold_node_id != reads.get("fold_node_id")
                    or receipt.manifest != reads.get("actual_read_manifest")
                    or tuple(node_id for node_id, _ in receipt.fitted_nodes) != reads.get("fitted_closure")
                    or hashlib.sha256(reads["actual_target_definition"]).hexdigest() != target):
                raise ContractError("bracket evidence differs from actual retained head query")
            definition = json.loads(reads["actual_target_definition"])
            if definition.get("policy_version") != self.policy_version or definition.get("head") != name:
                raise ContractError("bracket target definition differs from policy/head")
            raw.append(receipt.probability)
        total = sum(raw, Fraction())
        if total <= 0 or tuple(p for _, p in self.probabilities) != tuple(p / total for p in raw):
            raise ContractError("bracket probabilities differ from actual committed predictions")

    @property
    def version(self):
        return digest(self)


def predict_complete_bracket(*, branch, policy_version, fits, examples, committed_predict):
    """Serving is delegated to the required actual retained F11 store accessor.

    ``committed_predict`` maps the three heads to exact E0CommittedBinaryFit
    accessors. It cannot be replaced by an unverified callback declaration.
    """
    from trading_research.experiments.e0.learning_store import E0CommittedBinaryFit
    if branch not in ("frequency", "logistic") or not policy_version or type(committed_predict) is not dict:
        raise ContractError("bracket serving needs the fixed policy and committed model accessor")
    names = ("target", "stop", "deadline")
    if set(fits) != set(names) or set(examples) != set(names) or set(committed_predict) != set(names):
        raise ContractError("a binary reach probability cannot substitute for complete bracket outcomes")
    probabilities, evidence, populations = [], [], []
    first = examples["target"].sample
    for name in names:
        fit, example = fits[name], examples[name]
        if type(fit) is not E0BinaryFit or type(example) is not BinaryExample:
            raise ContractError("actual typed fitted head and query required")
        fit.config.__post_init__()
        accessor = committed_predict[name]
        if type(accessor) is not E0CommittedBinaryFit or accessor.fit_version != fit.version:
            raise ContractError("complete bracket requires the exact retained accessor for each actual fit")
        if (example.sample.id, example.sample.decision_at, example.sample.date_group) != (
                first.id, first.decision_at, first.date_group):
            raise ContractError("complete bracket heads changed the action row or decision cut")
        if fit.config.target_version != example.sample.target_version:
            raise ContractError("complete bracket head requested a different target/policy")
        if (fit.config.policy_version, fit.config.head) != (policy_version, name):
            raise ContractError("head target identity does not bind the fixed bracket policy")
        populations.append(tuple((s.id, s.date_group, s.decision_at) for s in fit.stages.population))
        model = fit.frequency if branch == "frequency" else fit.calibrated
        binding = accessor.binding(model)
        if (binding.target_ref.sha256 != fit.config.target_version
                or binding.target_ref.size_bytes != len(fit.config.target_payload)):
            raise ContractError("complete bracket target differs from its actual retained bytes")
        p, reads = accessor(model, example)
        if not isinstance(p, (float, int)) or isinstance(p, bool) or not 0 <= p <= 1 or not reads:
            raise ContractError("invalid committed prediction or absent actual read evidence")
        if reads["actual_target_definition"] != fit.config.target_payload:
            raise ContractError("complete bracket target differs from its actual retained bytes")
        probabilities.append(Fraction(str(p)))
        evidence.append((name, model.id, fit.config.target_version,
                         reads["verified_head_receipt"].fold_version, reads))
    if any(population != populations[0] for population in populations[1:]):
        raise ContractError("complete bracket heads changed the retained population")
    if len({fit.config.target_version for fit in fits.values()}) != 3:
        raise ContractError("three distinct target-specific bracket heads required")
    normalizer = sum(probabilities, Fraction())
    if normalizer <= 0:
        raise DependencyUnavailable("complete bracket heads have zero total probability mass")
    return E0BracketPrediction(branch, policy_version, first.id, first.decision_at,
        tuple((name, p / normalizer) for name, p in zip(names, probabilities)), tuple(evidence))


@dataclass(frozen=True)
class E0Head:
    name: str
    fit: E0BinaryFit
    committed: object
    examples: tuple[BinaryExample, ...]


@dataclass(frozen=True)
class E0BracketRouter:
    """Actual fitted and retained models for both independently fixed policies."""
    policies: tuple[tuple[str, tuple[E0Head, ...]], ...]

    def __post_init__(self):
        from trading_research.experiments.e0.learning_store import E0CommittedBinaryFit
        if (type(self.policies) is not tuple or tuple(name for name, _ in self.policies) != (
                "target-1x-fixed", "target-2x-fixed")):
            raise ContractError("E0 serving router must retain both fixed policies")
        for policy, heads in self.policies:
            if tuple(head.name for head in heads) != ("target", "stop", "deadline"):
                raise ContractError("complete E0 policy requires exactly its three outcome heads")
            for head in heads:
                if (type(head) is not E0Head or type(head.fit) is not E0BinaryFit
                        or type(head.committed) is not E0CommittedBinaryFit
                        or head.committed.fit_version != head.fit.version
                        or (head.fit.config.policy_version, head.fit.config.head) != (policy, head.name)
                        or tuple(sorted((e.sample for e in head.examples), key=lambda s: (s.decision_at, s.id)))
                           != head.fit.stages.population):
                    raise ContractError("E0 router supplied another fit, target or source population")

    @property
    def version(self):
        return digest(tuple((policy, tuple((head.name, head.fit.version,
            tuple(binding.commit_ref for binding in head.committed.bindings)) for head in heads))
            for policy, heads in self.policies))

    def __call__(self, *, branch, policy_version, day, row, features):
        heads = dict(self.policies).get(policy_version)
        if heads is None:
            raise ContractError("E0 serving requested an unregistered target policy")
        examples = {}
        for head in heads:
            original = next((e for e in head.examples if e.sample.id == row.id
                             and e.sample.decision_at == row.cut and e.sample.date_group == day.day), None)
            if original is None:
                raise DependencyUnavailable("E0 query is absent from the retained complete head population")
            examples[head.name] = BinaryExample(original.sample, features, original.outcome)
        return predict_complete_bracket(branch=branch, policy_version=policy_version,
            fits={head.name: head.fit for head in heads}, examples=examples,
            committed_predict={head.name: head.committed for head in heads})
