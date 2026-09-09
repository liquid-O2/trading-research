"""Immutable annual checkpoint joins for the registered extraction worker."""
import hashlib
import json

from trading_research.errors import IntegrityError
from trading_research.operations.artifacts import artifact_ref, digest
from trading_research.operations.trials import TrialRegistry


def _file(root, ref):
    path = root / ref["path"]
    if not path.resolve().is_relative_to(root.resolve()) or "archive" in path.parts:
        raise IntegrityError("checkpoint input escaped the retained package")
    raw = path.read_bytes()
    if len(raw) != ref["size_bytes"] or hashlib.sha256(raw).hexdigest() != ref["sha256"]:
        raise IntegrityError("checkpoint input changed")
    return json.loads(raw)


def checked_checkpoints(packet, protocol, root, store):
    plan = store.read_json(artifact_ref(packet["execution_plan"]))
    reference = _file(root, plan["reference_manifest"])
    review = _file(root, plan["interrupted_attempt_review"])
    state = TrialRegistry(root / "evidence/trials").state()
    attempt = state["attempts"].get(review["attempt"]["id"])
    trial = state["trials"].get(review["attempt"]["trial_id"])
    old_packet = _file(root, review["packet"])
    if (review["family"] != protocol["family"] or attempt != review["attempt"]
            or attempt["status"] != "interrupted" or attempt["family"] != protocol["family"]
            or trial != review["trial"] or trial["configuration"]["mode"] != "develop"
            or trial["configuration"]["phase"] != "extract"
            or trial["code_hash"] != reference["source_code_snapshot_sha256"]
            or old_packet["trial_id"] != attempt["trial_id"]
            or old_packet["attempt_id"] != attempt["id"]
            or old_packet["code_snapshot"]["sha256"] != trial["code_hash"]
            or old_packet["tools_snapshot"] != trial["configuration"]["tools_snapshot"]
            or old_packet["analysis_plan"] != packet["analysis_plan"]
            or trial["configuration"]["analysis_plan"] != packet["analysis_plan"]
            or old_packet["protocol_sha256"] != packet["protocol_sha256"]
            or trial["configuration"]["protocol_sha256"] != packet["protocol_sha256"]
            or old_packet["predecessor"] != trial["configuration"]["predecessor"]
            or plan["completed_shards"] != review["completed_shards"]):
        raise IntegrityError("checkpoint lacks its exact registered interrupted provenance")
    snapshot = store.read_json(artifact_ref(old_packet["code_snapshot"]))
    predecessor = old_packet["predecessor"]
    raw = (root / predecessor["path"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != predecessor["sha256"]:
        raise IntegrityError("checkpoint admission predecessor changed")
    admission_execution = json.loads(raw)
    admission_attempt = state["attempts"].get(admission_execution["attempt_id"])
    admission_trial = state["trials"].get(admission_execution["trial_id"])
    if (admission_execution.get("success") is not True or admission_execution.get("mode") != "admit"
            or admission_execution.get("family") != protocol["family"]
            or admission_execution.get("protocol_sha256") != packet["protocol_sha256"]
            or admission_attempt is None or admission_attempt["status"] != "succeeded"
            or admission_attempt["family"] != protocol["family"]
            or admission_attempt["trial_id"] != admission_execution["trial_id"]
            or admission_trial is None or admission_trial["code_hash"] != admission_execution["code_snapshot"]["sha256"]
            or admission_trial["configuration"]["tools_snapshot"] != admission_execution["tools_snapshot"]
            or not any(r["kind"] == "research_study_execution" and r["sha256"] == digest(admission_execution)
                       for r in admission_attempt["result_artifacts"])):
        raise IntegrityError("checkpoint has no exact successful registered admission receipt")
    admission = store.read_json(artifact_ref(admission_execution["worker_report"]))
    if admission.get("success") is not True or admission.get("mode") != "admit":
        raise IntegrityError("checkpoint admission worker did not complete")
    for module in reference["modules"]:
        raw = (root / module["reference_path"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != module["reference_sha256"]:
            raise IntegrityError("preserved reference source changed")
        original = bytes.fromhex(snapshot["files"][module["original_path"]]["$bytes"])
        if (hashlib.sha256(original).hexdigest() != module["original_sha256"]
                or snapshot["manifest"][module["original_path"]] != module["original_sha256"]):
            raise IntegrityError("reference does not identify the checked original bytes")
        expected = original
        for name in ("ohlc_ranges", "ohlc_mechanisms", "jumbo_tables", "date_statistics", "jumbo_report"):
            expected = expected.replace(f"trading_research.research.{name}".encode(),
                                        f"references.jumbo_extraction_v1.{name}".encode())
        if raw != expected:
            raise IntegrityError("reference changes extend beyond declared import rewrites")
    records = {}
    for ref in plan["completed_shards"]:
        row = _file(root, ref)
        key = row["root"], row["year"]
        if (key in records or key[0] not in protocol["roots"] or key[1] not in range(2020, 2025)
                or set(row["tables"]) != {"formations", "paths", "specials"}
                or row["intended_cash_dates"] < 1):
            raise IntegrityError("checkpoint population identity differs")
        admitted = sorted((r for r in admission["partitions"] if r["root"] == key[0]
                           and 2020 <= int(r["source_path"].rsplit("/", 1)[-1].split(".")[0]) <= 2024),
                          key=lambda r: r["source_path"])
        if len(admitted) != 5 or row["canonical_sources"] != [r["canonical_table"] for r in admitted]:
            raise IntegrityError("checkpoint sources differ from the actually admitted root cohort")
        for value in (*row["tables"].values(), row["statistics"]):
            store.read(artifact_ref({k: value[k] for k in ("sha256", "size_bytes", "kind")}))
        records[key] = {"record": row, "checkpoint": ref, "original_attempt_id": attempt["id"]}
    return records


