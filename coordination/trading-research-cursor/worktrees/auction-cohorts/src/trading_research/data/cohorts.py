"""Dataset/field/cohort readiness separate from inventory or provider claims."""

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import ArtifactRef, ArtifactStore, digest, file_digest
from trading_research.operations.journal import Journal
from trading_research.research.period import (ResearchPeriodPolicyV1, ResearchScopeV1,
    PrimaryAdmissionV1, check_cohort_bounds, validate_primary_cut, validate_scope,
    validate_primary_admission)


@dataclass(frozen=True)
class CohortEvidence:
    id: str
    dataset_id: str
    field: str
    cohort_id: str
    operation: str
    state: str
    depth: str
    source_identity: str
    definition_version: str
    code_version: str
    observation_start: int | None
    observation_end: int | None
    latency_scenario: str | None
    evidence: ArtifactRef
    reason: str
    dependent_units: tuple[str, ...]
    next_action: str | None

    def __post_init__(self):
        if not all((self.id, self.dataset_id, self.field, self.cohort_id, self.operation, self.source_identity,
                    self.definition_version, self.code_version, self.reason)):
            raise ContractError("field/cohort evidence needs exact source, operation and implementation scope")
        if self.state not in {"unassessed", "observed", "eligible", "estimated", "ineligible", "missing", "incomplete"}:
            raise ContractError("unregistered cohort readiness state")
        if self.depth not in {"inventory", "metadata", "row_prefix", "complete_window", "complete_partition", "actual_receipt_capture"}:
            raise ContractError("unregistered evidence depth")
        if self.state == "eligible" and self.depth in {"inventory", "metadata", "row_prefix"}:
            raise ContractError("inventory, metadata and a prefix cannot certify complete operation eligibility")
        if self.operation == "actual_live_receipt" and self.state == "eligible" and self.depth != "actual_receipt_capture":
            raise ContractError("historical provider timestamps are not an actual strategy-receipt capture")
        if self.state in {"missing", "incomplete", "ineligible"} and not self.next_action:
            raise ContractError("unavailable cohorts require a concrete next action")


class CohortRegistry:
    def __init__(self, root: Path, *, catalog_path: Path, schemas_path: Path,
                 expected_dataset_ids: frozenset[str], prior_audit_references: tuple[dict, ...]):
        self.root, self.artifacts = Path(root), ArtifactStore(Path(root) / "artifacts")
        self.journal = Journal(Path(root) / "cohorts.sqlite")
        catalog = json.loads(Path(catalog_path).read_bytes())
        schemas = json.loads(Path(schemas_path).read_bytes())
        self.datasets = {d["dataset_id"]:d for d in catalog["datasets"]}
        if len(self.datasets) != len(catalog["datasets"]) or set(self.datasets) != set(expected_dataset_ids) or set(schemas) != set(expected_dataset_ids):
            raise IntegrityError("readiness inventory does not exactly match all scoped dataset IDs")
        self.version = digest({"catalog":file_digest(catalog_path), "schemas":file_digest(schemas_path),
                               "prior_audit_references":prior_audit_references})
        self.journal.append(key=f"inventory:{self.version}", kind="readiness_inventory",
                            payload={"version":self.version, "catalog":catalog, "schemas":schemas,
                                     "prior_audit_references":prior_audit_references,
                                     "eligibility": "unassessed; inventory completeness and prior audit depth are preserved without promotion"})

    def append(self, record: CohortEvidence, *, scope: ResearchScopeV1 | None = None,
               policy: ResearchPeriodPolicyV1 | None = None, actual_cut_at: int | None = None,
               admission: PrimaryAdmissionV1 | None = None):
        if type(record) is not CohortEvidence:
            raise ContractError("typed cohort evidence is required")
        if record.dataset_id not in self.datasets:
            raise ContractError("cohort evidence references an unknown scoped dataset")
        validate_scope(scope, policy)
        if scope is not None and scope.is_primary:
            if type(admission) is not PrimaryAdmissionV1:
                raise ContractError("primary cohort admission requires an immutable population envelope")
            if actual_cut_at is None:
                actual_cut_at = admission.actual_cut_at
            else:
                validate_primary_cut(actual_cut_at, policy)  # type: ignore[arg-type]
                if actual_cut_at != admission.actual_cut_at:
                    raise IntegrityError("primary cohort frozen cut differs from its admission envelope")
            validate_primary_admission(admission, (record,), scope=scope, policy=policy)  # type: ignore[arg-type]
        elif admission is not None:
            raise ContractError("population admission envelope is only valid for an explicit primary scope")
        period_error = None
        if scope is not None:
            try:
                check_cohort_bounds(scope, policy, record.observation_start, record.observation_end,
                                    depth=record.depth, state=record.state,
                                    frozen_cut_at=actual_cut_at)
            except ContractError as exc:
                period_error = exc
        report = self.artifacts.read_json(record.evidence)
        if record.state in {"eligible", "estimated"}:
            report_scope = report.get("certification", {})
            if (not report.get("success") or record.dataset_id not in report_scope.get("datasets", [])
                    or record.cohort_id != report_scope.get("cohort_id") or record.operation not in report_scope.get("operations", [])
                    or record.field not in report_scope.get("fields", []) or record.depth != report_scope.get("depth")):
                raise IntegrityError("eligibility claim is not supported by this exact field/cohort/operation artifact")
        if period_error is not None:
            raise period_error
        self.journal.append(key=f"cohort:{record.id}", kind="cohort_evidence",
                            payload={"inventory_version":self.version, "record":asdict(record),
                                     **({"research_scope":asdict(scope)} if scope is not None else {}),
                                     **({"primary_admission":asdict(admission)} if admission is not None else {})})

    def append_primary(self, record: CohortEvidence, *, scope: ResearchScopeV1,
                       policy: ResearchPeriodPolicyV1, actual_cut_at: int,
                       admission: PrimaryAdmissionV1):
        """Append through the explicit primary period/source admission boundary."""
        validate_scope(scope, policy, require_primary=True)
        if type(admission) is not PrimaryAdmissionV1:
            raise ContractError("append_primary requires an immutable population admission envelope")
        return self.append(record, scope=scope, policy=policy, actual_cut_at=actual_cut_at,
                           admission=admission)

    def audit(self):
        evidence = [e["payload"]["record"] for e in self.journal.read() if e["kind"] == "cohort_evidence" and e["payload"]["inventory_version"] == self.version]
        return {"inventory_version":self.version, "dataset_count":len(self.datasets), "cohort_evidence_count":len(evidence),
                "datasets":{id:{"inventory_status":d.get("status"), "eligibility":"unassessed" if not any(r["dataset_id"] == id for r in evidence) else "operation_and_cohort_specific",
                                "evidence_ids":[r["id"] for r in evidence if r["dataset_id"] == id]}
                            for id,d in self.datasets.items()}}
