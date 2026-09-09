"""Append-only family budgets, immutable configurations and every run attempt."""

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
from typing import Iterator

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import ArtifactStore, artifact_ref, canonical_json, digest, publish_new

STAGES = {"original", "corrected", "representation", "model", "integration", "engineering"}


class TrialRegistry:
    def __init__(self, root: Path):
        self.root = Path(root)
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
        events, previous = [], None
        for n, path in enumerate(sorted((self.root / "events").glob("*.json")), 1):
            event = json.loads(path.read_bytes())
            key = digest({k: v for k, v in event.items() if k != "hash"})
            if (event["sequence"] != n or event["previous"] != previous or event["hash"] != key
                    or path.name != f"{n:010d}-{key}.json"):
                raise IntegrityError("broken trial journal")
            events.append(event)
            previous = key
        return events

    def _append(self, kind: str, payload: dict) -> str:
        history = self.history()
        event = {"kind": kind, "payload": payload, "sequence": len(history) + 1,
                 "previous": history[-1]["hash"] if history else None,
                 "recorded_at": datetime.now(timezone.utc).isoformat()}
        event["hash"] = digest(event)
        publish_new(self.root / "events" / f"{event['sequence']:010d}-{event['hash']}.json",
                    canonical_json(event) + b"\n")
        return event["hash"]

    def state(self) -> dict:
        state = {"families": {}, "trials": {}, "attempts": {},
                 "effective_budgets": {}, "budget_amendments": {}}
        for e in self.history():
            p = e["payload"]
            if e["kind"] == "family":
                state["families"][p["id"]] = p
                state["effective_budgets"][p["id"]] = {
                    k: p[k] for k in ("max_attempts", "cpu_budget_seconds")}
            elif e["kind"] == "budget_amended":
                expected = self._amendment_payload(p["authorization"], state)
                if p != expected or p["amendment_id"] in state["budget_amendments"]:
                    raise IntegrityError("invalid budget amendment transition")
                state["effective_budgets"][p["family"]] = p["authorized_limits"]
                state["budget_amendments"][p["amendment_id"]] = {
                    "payload": p, "event_hash": e["hash"]}
            elif e["kind"] == "trial":
                state["trials"][p["id"]] = p
            elif e["kind"] == "started":
                state["attempts"][p["id"]] = {**p, "status": "running"}
            elif e["kind"] == "finished":
                if p["id"] not in state["attempts"] or state["attempts"][p["id"]]["status"] != "running":
                    raise IntegrityError("invalid attempt transition")
                state["attempts"][p["id"]].update(p)
        return state

    def register_family(self, id: str, *, scope_ids: tuple[str, ...], protocol: dict,
                        max_attempts: int, cpu_budget_seconds: int) -> None:
        if (not id or not scope_ids or type(max_attempts) is not int or max_attempts <= 0
                or type(cpu_budget_seconds) is not int or cpu_budget_seconds <= 0 or not protocol):
            raise ContractError("family requires scope, frozen protocol and a finite run budget")
        payload = {"id": id, "scope_ids": list(scope_ids), "protocol": protocol,
                   "max_attempts": max_attempts, "cpu_budget_seconds": cpu_budget_seconds}
        payload = json.loads(canonical_json(payload))
        with self._lock():
            old = self.state()["families"].get(id)
            if old is not None:
                if old != payload:
                    raise ContractError("family registration is immutable; resource changes require an explicit authorized amendment")
                return
            self._append("family", payload)

    def _amendment_payload(self, authorization: dict, state: dict) -> dict:
        ref = artifact_ref(authorization)
        document = self.artifacts.read_json(ref)
        required = {"kind", "amendment_id", "family", "base_family_sha256",
                    "previous_limits", "authorized_limits", "approval", "reason"}
        if not required <= document.keys() or document["kind"] != "family_budget_authorization_v1":
            raise ContractError("explicit retained family budget authorization required")
        approval = document["approval"]
        if (not isinstance(approval, dict) or approval.get("source") != "explicit_user_approval"
                or any(not isinstance(approval.get(k), str) or not approval[k].strip()
                       for k in ("approved_at", "question", "answer"))
                or not document["amendment_id"] or not document["reason"]):
            raise ContractError("authorization must retain the explicit approval and its scope")
        family = document["family"]
        if (family not in state["families"]
                or document["base_family_sha256"] != digest(state["families"][family])):
            raise ContractError("budget authorization differs from the original registered family")
        previous, authorized = document["previous_limits"], document["authorized_limits"]
        keys = {"max_attempts", "cpu_budget_seconds"}
        if (not isinstance(previous, dict) or not isinstance(authorized, dict)
                or set(previous) != keys or set(authorized) != keys
                or any(type(v) is not int or v <= 0 for v in (*previous.values(), *authorized.values()))
                or previous != state["effective_budgets"][family]
                or any(authorized[k] < previous[k] for k in keys)
                or authorized == previous):
            raise ContractError("amendment must explicitly increase current limits without a reset")
        return {k: document[k] for k in ("amendment_id", "family", "base_family_sha256",
                "previous_limits", "authorized_limits", "reason")} | {"authorization": authorization}

    def amend_budget(self, *, authorization: dict) -> str:
        """Append a user-authorized resource change; preserve every prior record.

        The retained authorization names the exact original family and previous
        limits. This never changes scientific configuration or forgives usage.
        """
        authorization = json.loads(canonical_json(authorization))
        document = self.artifacts.read_json(artifact_ref(authorization))
        with self._lock():
            state = self.state()
            existing = state["budget_amendments"].get(document.get("amendment_id"))
            if existing is not None:
                if existing["payload"]["authorization"] != authorization:
                    raise ContractError("amendment ID already identifies different authorization")
                return existing["event_hash"]
            payload = self._amendment_payload(authorization, state)
            return self._append("budget_amended", payload)

    def register(self, *, name: str, family: str, stage: str, configuration: dict,
                 code_hash: str, data_hashes: dict, fold_version: str, target_version: str,
                 parent_trial: str | None = None) -> str:
        if stage not in STAGES or not all((name, code_hash, fold_version, target_version)):
            raise ContractError("trial omits its immutable implementation/target/fold/stage")
        scientific = {"family": family, "stage": stage, "configuration": configuration,
                      "code_hash": code_hash, "data_hashes": data_hashes, "fold_version": fold_version,
                      "target_version": target_version, "parent_trial": parent_trial}
        id = digest(scientific)  # Cosmetic names do not create independent hypotheses.
        with self._lock():
            state = self.state()
            if family not in state["families"] or (parent_trial is not None and parent_trial not in state["trials"]):
                raise ContractError("unregistered experiment family or source-comparison parent")
            if id not in state["trials"]:
                self._append("trial", {"id": id, "name": name, **scientific})
            elif name != state["trials"][id]["name"]:
                self._append("alias", {"trial_id": id, "name": name})
        return id

    def start(self, trial_id: str, *, cpu_reservation_seconds: int) -> str:
        if type(cpu_reservation_seconds) is not int or cpu_reservation_seconds <= 0:
            raise ContractError("attempt needs a positive bounded CPU reservation")
        with self._lock():
            state = self.state()
            if trial_id not in state["trials"]:
                raise ContractError("unregistered run")
            family = state["trials"][trial_id]["family"]
            attempts = [a for a in state["attempts"].values() if a["family"] == family]
            if any(a["trial_id"] == trial_id and a["status"] == "running" for a in attempts):
                raise ContractError("attempt already running; preserve and resolve interrupted evidence explicitly")
            charged = sum(a["cpu_reservation_seconds"] if a["status"] == "running"
                          else a["cpu_seconds"] for a in attempts)
            limit = state["effective_budgets"][family]
            if len(attempts) >= limit["max_attempts"] or charged + cpu_reservation_seconds > limit["cpu_budget_seconds"]:
                raise ContractError("registered family resource/search budget exhausted")
            id = digest({"trial": trial_id, "attempt_number": len(state["attempts"]) + 1})
            self._append("started", {"id": id, "trial_id": trial_id, "family": family,
                                     "cpu_reservation_seconds": cpu_reservation_seconds})
        return id

    def finish(self, attempt_id: str, *, status: str, cpu_seconds: float | None,
               wall_seconds: float | None, peak_rss_bytes: int | None, reason: str,
               result_artifacts: tuple[dict, ...] = ()) -> None:
        if status not in {"succeeded", "failed", "interrupted"} or not reason:
            raise ContractError("explicit run outcome/reason required")
        with self._lock():
            attempt = self.state()["attempts"].get(attempt_id)
            if attempt is None or attempt["status"] != "running":
                raise ContractError("unknown or already finalized attempt")
            if status == "succeeded" and (cpu_seconds is None or wall_seconds is None or peak_rss_bytes is None or not result_artifacts):
                raise ContractError("successful run requires actual output artifacts and resource observations")
            for value in (cpu_seconds, wall_seconds, peak_rss_bytes):
                if value is not None and (isinstance(value, bool) or value < 0):
                    raise ContractError("invalid resource measurement")
            for ref in result_artifacts:
                self.artifacts.read(artifact_ref(ref))
            # Unknown killed-worker usage charges its reservation; never infer zero cost.
            self._append("finished", {"id": attempt_id, "status": status,
                         "cpu_seconds": cpu_seconds if cpu_seconds is not None else attempt["cpu_reservation_seconds"],
                         "resource_basis": "observed" if cpu_seconds is not None else "reservation_charged_usage_unknown",
                         "wall_seconds": wall_seconds, "peak_rss_bytes": peak_rss_bytes,
                         "reason": reason, "result_artifacts": list(result_artifacts)})
