"""Append-only evidence transactions, with separate engineering/research states."""

from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
from typing import Any, Iterator

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import (
    ArtifactStore, artifact_ref, canonical_json, digest, publish_new,
)
from trading_research.operations.scope import Scope, ScopeEntry


ENGINEERING = {"unstarted", "in_progress", "implemented", "verified"}
EVALUATION = {"unrun", "running", "evaluated"}
DISPOSITIONS = {"undecided", "selected", "rejected", "inconclusive", "dependency_blocked", "not_applicable"}


def initial_record(entry: ScopeEntry, scope_version: str) -> dict:
    unit = entry.definition.get("unit")
    comparison = unit.get("upgrade_contract", {}).get("comparison") if isinstance(unit, dict) else None
    return {
        "id": entry.id, "kind": entry.kind,
        "scope_version": scope_version,
        "unit_or_source_or_dataset_or_task_id": entry.owner,
        "phase_or_clause": entry.phase_or_clause,
        "definition_version": entry.definition_version,
        "definition_reviewed": False, "review_artifacts": [],
        "dependency_ids": list(entry.dependency_ids),
        "eligibility_and_cohort": {"status": "unassessed", "cohorts": []},
        "engineering_state": "unstarted", "evaluation_state": "unrun",
        "disposition": "undecided", "reference_and_code_artifacts": [],
        "acceptance_basis": "unassessed",
        "verification_artifacts": [], "experiment_artifacts": [],
        "source_variant_and_upgrade_stage": "unregistered",
        "applicable_upgrade_comparison": comparison,
        "assertion_ids": [], "dependency_details": [],
        "reason": "Definition imported; implementation and applicability have not been established.",
        "next_action": "Review full contract, source clauses and local cases; register concrete assertions and eligible comparisons.",
    }


class Ledger:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.events = self.root / "events"
        self.artifacts = ArtifactStore(self.root / "artifacts")

    @contextmanager
    def _lock(self) -> Iterator[None]:
        self.root.mkdir(parents=True, exist_ok=True)
        with (self.root / ".lock").open("a+b") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream, fcntl.LOCK_UN)

    def history(self) -> list[dict]:
        result = []
        previous = None
        for sequence, path in enumerate(sorted(self.events.glob("*.json")), 1):
            event = json.loads(path.read_bytes())
            body = {k: v for k, v in event.items() if k != "event_hash"}
            expected = digest(body)
            if (event["sequence"] != sequence or event["previous"] != previous
                    or event["event_hash"] != expected
                    or path.name != f"{sequence:010d}-{expected}.json"):
                raise IntegrityError(f"broken implementation history: {path.name}")
            result.append(event)
            previous = expected
        return result

    def current(self) -> dict[str, dict]:
        state: dict[str, dict] = {}
        for event in self.history():
            for id in event.get("retired_ids", []):
                if id not in state:
                    raise IntegrityError(f"retirement of unknown scope ID: {id}")
                del state[id]
            ids = [r["id"] for r in event["records"]]
            if len(ids) != len(set(ids)):
                raise IntegrityError("duplicate record in evidence transaction")
            state.update({r["id"]: r for r in event["records"]})
        return state

    def _append(self, records: list[dict], *, action: str, reason: str,
                scope_ref: dict | None = None, retired_ids: list[str] | None = None,
                attachment_key: str | None = None, attachment_digest: str | None = None) -> str:
        previous = self.history()
        event = {
            "sequence": len(previous) + 1,
            "previous": previous[-1]["event_hash"] if previous else None,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "action": action, "reason": reason, "records": records,
            "scope_ref": scope_ref, "retired_ids": retired_ids or [],
        }
        if attachment_key is not None:
            event.update(attachment_key=attachment_key, attachment_digest=attachment_digest)
        event["event_hash"] = digest(event)
        path = self.events / f"{event['sequence']:010d}-{event['event_hash']}.json"
        publish_new(path, canonical_json(event) + b"\n")
        return event["event_hash"]

    def import_scope(self, scope: Scope) -> dict:
        with self._lock():
            current = self.current()
            if current:
                self.audit(scope)
                return {"imported": 0, "preserved": len(current), "scope_version": scope.version}
            ref = self.artifacts.put_json(scope.bundle(), kind="scope_definition")
            records = [initial_record(e, scope.version) for e in scope.entries.values()]
            self._append(records, action="scope_import", reason="Import complete scope without empirical status.",
                         scope_ref=asdict(ref))
            return {"imported": len(records), "preserved": 0, "scope_version": scope.version}

    def migrate_scope(self, scope: Scope, *, reason: str) -> dict:
        if not reason.strip():
            raise ContractError("scope migration requires prior requirement/reason/dependency consequences")
        with self._lock():
            current = self.current()
            if not current:
                raise ContractError("import a scope before migration")
            records = []
            changed = []
            for id, entry in scope.entries.items():
                old = current.get(id)
                if old and old["definition_version"] == entry.definition_version:
                    record = {**old, "scope_version": scope.version}
                else:
                    record = initial_record(entry, scope.version)
                    if old:
                        record["prior_record_hash"] = digest(old)
                        record["reason"] = f"Changed definition requires revalidation: {reason}"
                        changed.append(id)
                records.append(record)
            retired = sorted(set(current) - set(scope.entries))
            ref = self.artifacts.put_json(scope.bundle(), kind="scope_definition")
            self._append(records, action="scope_migration", reason=reason, scope_ref=asdict(ref), retired_ids=retired)
            return {"changed": changed, "retired": retired, "active": len(records)}

    def _validate_record(self, record: dict, *, valid_ids: set[str]) -> None:
        if record["engineering_state"] not in ENGINEERING or record["evaluation_state"] not in EVALUATION:
            raise ContractError("invalid independent status")
        if record["disposition"] not in DISPOSITIONS:
            raise ContractError("invalid disposition")
        if not record["reason"].strip() or not record["next_action"].strip():
            raise ContractError("reason and next action are required")
        if not set(record["dependency_ids"]).issubset(valid_ids):
            raise ContractError("unknown scope dependency")
        for field in ("reference_and_code_artifacts", "verification_artifacts", "experiment_artifacts", "review_artifacts"):
            for ref in record[field]:
                self.artifacts.read(artifact_ref(ref))
        if record["definition_reviewed"] and not record["review_artifacts"]:
            raise ContractError("definition review requires a review artifact")
        if record["engineering_state"] in {"implemented", "verified"}:
            if not record["definition_reviewed"] or not record["reference_and_code_artifacts"]:
                raise ContractError("implementation requires reviewed definition and code/reference evidence")
        if record["engineering_state"] == "verified":
            if not record["verification_artifacts"] or not record["assertion_ids"]:
                raise ContractError("verification requires named executed assertions")
            covered = set()
            for ref in record["verification_artifacts"]:
                if ref["kind"] != "verification":
                    raise ContractError("wrong verification artifact kind")
                result = self.artifacts.read_json(artifact_ref(ref))
                if result.get("success") is not True or record["id"] not in result.get("covers", []):
                    raise ContractError("verification report failed or does not cover the record")
                covered.update(result.get("passed_assertion_ids", []))
            if not set(record["assertion_ids"]).issubset(covered):
                raise ContractError("assertions absent from executed verification evidence")
        if record["evaluation_state"] == "evaluated" and not record["experiment_artifacts"]:
            raise ContractError("evaluation requires experiment evidence")
        if record["disposition"] == "dependency_blocked" and not record["dependency_details"]:
            raise ContractError("blocked branch requires an exact missing dependency")
        if record["disposition"] == "not_applicable" and not record.get("applicability_contract"):
            raise ContractError("not_applicable requires a contract-based reason")
        if record["disposition"] in {"selected", "rejected"}:
            basis = record.get("acceptance_basis", "unassessed")
            if basis == "operational_fidelity":
                if record["engineering_state"] != "verified":
                    raise ContractError("operational acceptance requires verified invariant evidence")
            elif basis == "empirical":
                if record["evaluation_state"] != "evaluated" or not record["experiment_artifacts"]:
                    raise ContractError("hypothesis selection/rejection requires empirical evaluation")
            else:
                raise ContractError("selection/rejection must distinguish operational fidelity from empirical evidence")
        if record["kind"] == "dataset" and not record["eligibility_and_cohort"]:
            raise ContractError("dataset field/cohort eligibility record missing")

    def update(self, changes: dict[str, dict], *, reason: str,
               append_fields: tuple[str, ...] = (), attachment_key: str | None = None) -> str:
        allowed_append = {"reference_and_code_artifacts", "verification_artifacts",
                          "experiment_artifacts", "review_artifacts", "assertion_ids"}
        if (not isinstance(append_fields, tuple) or len(set(append_fields)) != len(append_fields)
                or not set(append_fields).issubset(allowed_append)):
            raise ContractError("only explicit evidence lists can be appended atomically")
        if attachment_key is not None and (type(attachment_key) is not str or not attachment_key):
            raise ContractError("attachment key must be a nonempty immutable identity")
        attachment_digest = digest({"changes": changes, "reason": reason,
                                    "append_fields": append_fields}) if attachment_key is not None else None
        with self._lock():
            if attachment_key is not None:
                matches = [e for e in self.history() if e.get("attachment_key") == attachment_key]
                if matches:
                    if len(matches) != 1 or matches[0].get("attachment_digest") != attachment_digest:
                        raise ContractError("attachment key already binds different evidence")
                    return matches[0]["event_hash"]
            state = self.current()
            immutable = {"id", "kind", "scope_version", "definition_version",
                         "unit_or_source_or_dataset_or_task_id", "phase_or_clause"}
            records = []
            for id, patch in changes.items():
                if id not in state or immutable.intersection(patch):
                    raise ContractError(f"unknown ID or attempted definition mutation: {id}")
                if set(patch) - (set(state[id]) | {"applicability_contract", "acceptance_basis"}):
                    raise ContractError(f"unknown evidence field in {id}")
                record = {**state[id], **patch}
                for field in append_fields:
                    if field in patch:
                        if type(patch[field]) is not list:
                            raise ContractError("appended evidence must be a list")
                        record[field] = list({digest(value): value for value in
                                              [*state[id][field], *patch[field]]}.values())
                self._validate_record(record, valid_ids=set(state))
                records.append(record)
            if not records or not reason.strip():
                raise ContractError("an update needs records and a reason")
            return self._append(records, action="evidence_update", reason=reason,
                                attachment_key=attachment_key, attachment_digest=attachment_digest)

    def audit(self, scope: Scope, *, require_complete: bool = False) -> dict:
        state = self.current()
        missing, extra = sorted(set(scope.entries) - set(state)), sorted(set(state) - set(scope.entries))
        if missing or extra:
            raise IntegrityError(f"scope coverage differs: missing={missing[:12]}, extra={extra[:12]}")
        for id, entry in scope.entries.items():
            record = state[id]
            if record["scope_version"] != scope.version or record["definition_version"] != entry.definition_version:
                raise IntegrityError(f"stale ledger definition: {id}; explicit migration required")
            self._validate_record(record, valid_ids=set(state))
        engineering_pending = [r["id"] for r in state.values() if r["engineering_state"] != "verified"]
        research_pending = [r["id"] for r in state.values()
                            if r["disposition"] in {"undecided", "dependency_blocked", "inconclusive"}]
        unresolved = sorted(set(engineering_pending) | set(research_pending))
        if require_complete and unresolved:
            raise IntegrityError(f"program is incomplete: {len(unresolved)} unresolved records")
        return {
            "scope_version": scope.version, "records": len(state),
            "kinds": dict(Counter(r["kind"] for r in state.values())),
            "engineering": dict(Counter(r["engineering_state"] for r in state.values())),
            "evaluation": dict(Counter(r["evaluation_state"] for r in state.values())),
            "dispositions": dict(Counter(r["disposition"] for r in state.values())),
            "definition_reviewed": sum(r["definition_reviewed"] for r in state.values()),
            "unresolved_records": len(unresolved), "coverage_valid": True,
            "engineering_complete": not engineering_pending,
            "engineering_pending": len(engineering_pending),
            "research_disposition_complete": not research_pending,
            "research_pending": len(research_pending),
            "economic_evidence": "No economic conclusion is inferred from coverage or engineering status.",
        }
