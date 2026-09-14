"""Schema blueprint for P15-00/P2-00; not an implemented research package.

The task owners place these declarations in the specified package, implement
boundary validation, and add the numerical behavior from the Markdown contracts.
Money/prices use Decimal; all clocks are UTC nanoseconds. No algorithm runs here.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Iterable, Literal, Protocol, TypeAlias

Ns: TypeAlias = int
AssetId: TypeAlias = str
Side: TypeAlias = Literal[-1, 1]
JSONValue: TypeAlias = None | bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"]


class Coverage(Enum):
    COMPLETE = "complete_observed_scope"
    PARTIAL = "partial"
    MISSING = "missing"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    path: str
    sha256: str
    schema_version: str
    byte_count: int
    row_count: int | None


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    artifact_sha256: str
    row_ids: tuple[str, ...]
    event_start_ns: Ns
    event_end_ns: Ns
    available_at_ns: Ns
    coverage: Coverage
    limitation_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CoverageReceipt:
    start_ns: Ns
    end_ns: Ns
    status: Coverage
    expected_matching_intervals: tuple[tuple[Ns, Ns], ...]
    observed_intervals: tuple[tuple[Ns, Ns], ...]
    missing_intervals: tuple[tuple[Ns, Ns], ...]
    calendar_sha256: str
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class NativeTrade:
    event_id: str
    asset_id: AssetId
    event_ns: Ns
    available_at_ns: Ns
    price: Decimal
    quantity: int
    aggressor: Side | None
    evidence: EvidenceRef


@dataclass(frozen=True, slots=True)
class NativeBatch:
    batch_id: str
    event_ns: Ns
    available_at_ns: Ns
    trades: tuple[NativeTrade, ...]
    internal_order_known: bool


@dataclass(frozen=True, slots=True)
class QuoteBatch:
    batch_id: str
    asset_id: AssetId
    event_ns: Ns
    available_at_ns: Ns
    bid: Decimal | None
    ask: Decimal | None
    bid_size: int | None
    ask_size: int | None
    ambiguous: bool
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class Bar:
    bar_id: str
    asset_id: AssetId
    start_ns: Ns
    end_ns: Ns
    available_at_ns: Ns
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal | None
    volume: int
    known_signed_volume: int
    unknown_aggressor_volume: int
    coverage: Coverage
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class FeatureValue:
    name: str
    value: float | None
    unit: str
    available_at_ns: Ns
    evidence: tuple[EvidenceRef, ...]
    missing_reason: str | None


@dataclass(frozen=True, slots=True)
class Snapshot:
    snapshot_id: str
    account_day: str
    asset_id: AssetId
    issue_at_ns: Ns
    feature_schema: str
    values: tuple[FeatureValue, ...]
    policy_sha256: str


@dataclass(frozen=True, slots=True)
class RuleSpec:
    rule_id: str
    family: str
    source_branch: str | None
    version: str
    provenance: Literal["source_literal", "source_inspired", "custom"]
    baseline_rule_id: str | None
    changed_axis: str
    parameters: dict[str, str | int | bool]
    required_inputs: tuple[str, ...]
    required_stages: tuple[str, ...]
    formation_policy: str
    expiry_policy: str


@dataclass(frozen=True, slots=True)
class Formation:
    formation_id: str
    asset_id: AssetId
    start_ns: Ns
    end_ns: Ns
    available_at_ns: Ns
    high: Decimal
    low: Decimal
    volume: int
    profile_id: str | None
    construction_kind: str
    parent_ids: tuple[str, ...]
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class Reference:
    reference_id: str
    reference_lifecycle_id: str
    formation_id: str
    asset_id: AssetId
    lower: Decimal
    upper: Decimal
    issue_at_ns: Ns
    expiry_at_ns: Ns
    permitted_sides: tuple[Side, ...]
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class Contact:
    contact_id: str
    reference_id: str
    batch_id: str
    at_ns: Ns
    available_at_ns: Ns
    side: Side
    kind: Literal["touch", "strict_sweep", "ambiguous"]
    possible_prices: tuple[Decimal, ...]
    departure_evidence: tuple[EvidenceRef, ...]
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class PredicateEvidence:
    name: str
    value: bool | None
    available_at_ns: Ns | None
    evidence: tuple[EvidenceRef, ...]
    missing_reason: str | None


@dataclass(frozen=True, slots=True)
class ContextEvidence:
    family: str
    branch: str
    reference_id: str
    at_ns: Ns
    predicates: tuple[PredicateEvidence, ...]


@dataclass(frozen=True, slots=True)
class SequenceSpec:
    recipe_id: str
    ordered_stages: tuple[str, ...]
    deadline_seconds: int
    parameters: dict[str, str | int | bool]


@dataclass(frozen=True, slots=True)
class SequenceState:
    sequence_id: str
    recipe_id: str
    contact_id: str
    state: str
    state_at_ns: Ns
    available_at_ns: Ns
    deadline_ns: Ns
    stage_evidence: tuple[PredicateEvidence, ...]
    terminal_reason: str | None
    working_memory: dict[str, JSONValue]


@dataclass(frozen=True, slots=True)
class SequenceInputs:
    reference: Reference
    context: ContextEvidence
    completed_bars: tuple[Bar, ...]
    flow_features: tuple[FeatureValue, ...]
    available_at_ns: Ns


@dataclass(frozen=True, slots=True)
class Opportunity:
    opportunity_id: str
    parent_opportunity_id: str | None
    overlap_group_id: str
    rule_id: str
    family: str
    branch: str
    account_day: str
    side: Side
    issue_at_ns: Ns
    decision_at_ns: Ns
    reference_asset: AssetId
    response_asset: AssetId
    execution_asset: AssetId
    reference_id: str
    lower: Decimal
    upper: Decimal
    entry_reference: Decimal | None
    invalidation: Decimal | None
    objective: Decimal | None
    expiry_at_ns: Ns
    stages: tuple[EvidenceRef, ...]
    coverage: Coverage
    source_exact: bool
    hypothesis_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ScanResult:
    opportunities: tuple[Opportunity, ...]
    rejected_contacts: tuple[Contact, ...]
    unknown_contacts: tuple[Contact, ...]
    formations: tuple[Formation, ...]
    sequences: tuple[SequenceState, ...]
    coverage: CoverageReceipt
    baseline_payloads: tuple[dict[str, JSONValue], ...]


BaselineResult: TypeAlias = ScanResult


@dataclass(frozen=True, slots=True)
class TargetRow:
    target_row_id: str
    snapshot_id: str
    target_id: str
    account_day: str
    interval_start_ns: Ns
    interval_end_ns: Ns
    label_available_at_ns: Ns | None
    value: float | str | None
    unit: str
    event_kind: str
    censor_at_ns: Ns | None
    coverage: Coverage
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class SplitManifest:
    split_id: str
    fit_days: tuple[str, ...]
    tune_days: tuple[str, ...]
    calibration_days: tuple[str, ...]
    test_days: tuple[str, ...]
    purged_row_ids: tuple[str, ...]
    embargo_days: tuple[str, ...]
    fit_cutoff_ns: Ns
    selection_cutoff_ns: Ns
    label_availability_cutoff_ns: Ns
    exposure_ledger_sha256: str


@dataclass(frozen=True, slots=True)
class ExpertDataset:
    dataset_id: str
    snapshots: ArtifactRef
    targets: ArtifactRef
    predictor_matrix: ArtifactRef
    row_ids: ArtifactRef
    columns: tuple[str, ...]
    target_ids: tuple[str, ...]
    feature_dictionary: ArtifactRef
    target_dictionary: ArtifactRef
    parent_prediction_manifests: tuple[ArtifactRef, ...]
    rule_selection_manifests: tuple[ArtifactRef, ...]


@dataclass(frozen=True, slots=True)
class ExpertConfig:
    expert_id: str
    feature_groups: tuple[str, ...]
    feature_columns: tuple[str, ...]
    target_heads: tuple[str, ...]
    target_units: tuple[str, ...]
    recipe: str
    hyperparameter_grid: dict[str, list[JSONValue]]
    hinge_product_pairs: tuple[tuple[str, str], ...]
    fit_schedule: str
    support_policy: str
    fallback_policy: str
    ablation_groups: tuple[str, ...]
    policy_sha256: str


@dataclass(frozen=True, slots=True)
class ExpertArtifact:
    expert_id: str
    artifact_id: str
    config: ArtifactRef
    dataset_id: str
    split_id: str
    preprocessing: ArtifactRef
    coefficients: ArtifactRef
    calibration: ArtifactRef
    support_by_head: dict[str, str]
    training_row_ids: ArtifactRef
    train_end_ns: Ns
    fit_available_at_ns: Ns
    parent_artifacts: tuple[ArtifactRef, ...]


ModelArtifact: TypeAlias = ExpertArtifact


@dataclass(frozen=True, slots=True)
class Forecast:
    forecast_id: str
    expert_id: str
    artifact_sha256: str
    snapshot_id: str
    issue_at_ns: Ns
    horizon_id: str
    target_end_ns: Ns | None
    output: dict[str, float | str | None]
    support: str
    train_end_ns: Ns
    fit_available_at_ns: Ns
    input_feature_ids: tuple[str, ...]
    parent_forecast_ids: tuple[str, ...]


class MarketView(Protocol):
    def executions(self, start_ns: Ns, end_ns: Ns) -> Iterable[NativeBatch]: ...
    def quotes(self, start_ns: Ns, end_ns: Ns) -> Iterable[QuoteBatch]: ...
    def coverage(self, start_ns: Ns, end_ns: Ns) -> CoverageReceipt: ...
    def completed_bars(self, start_ns: Ns, end_ns: Ns, seconds: int) -> tuple[Bar, ...]: ...


class Expert(Protocol):
    def fit(self, dataset: ExpertDataset, split: SplitManifest, config: ExpertConfig) -> ExpertArtifact: ...
    def predict(self, artifact: ExpertArtifact, snapshots: tuple[Snapshot, ...]) -> tuple[Forecast, ...]: ...
    def serialize(self, artifact: ExpertArtifact, destination: str) -> ArtifactRef: ...
    def load(self, artifact: ArtifactRef) -> ExpertArtifact: ...
    def explain_inputs(self, artifact: ExpertArtifact) -> dict[str, JSONValue]: ...
