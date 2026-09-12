from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from trading_research.research.method_pack.empirical_protocol import population_summary
from trading_research.research.method_pack.empirical_reporting import (
    build_results,
    content_hash,
    file_hash,
    write_results,
)


SOURCE_ROOT = Path(__file__).parents[1] / "reports/phase1-live/empirical"


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _fixture(tmp_path: Path, *, two_jobs: bool = True, same_year: bool = False, two_contracts: bool = False, versioned: bool = False) -> tuple[Path, list[str]]:
    root = tmp_path / "empirical"
    (root / "registry").mkdir(parents=True)
    shutil.copy(SOURCE_ROOT / "registry/CANDIDATE_REGISTRY.json", root / "registry/CANDIDATE_REGISTRY.json")
    registry = json.loads((root / "registry/CANDIDATE_REGISTRY.json").read_text())
    supported = [row["rule_id"] for row in registry["rules"] if row["supported"]]
    rule_ids = supported[:2]
    jobs = []
    days = ("2025-01-02", "2025-01-03") if same_year and two_jobs else ("2025-01-02", "2026-01-05") if two_jobs else ("2025-01-02",)
    for index, day in enumerate(days):
        instrument = 43 if two_contracts and index == 1 else 42
        jobs.append({
            "job_id": f"bar-monthly--P{index + 1}",
            "cohort": "bar-monthly",
            "partition": {"partition_id": f"P{index + 1}", "date": day, "instrument_id": instrument},
            "rule_ids": rule_ids,
        })
    manifest = {"schema": "phase1-empirical-run-v1", "registry_sha256": registry["registry_sha256"], "jobs": jobs}
    if versioned:
        manifest["run_version"] = "1.0.1"
    manifest["manifest_sha256"] = content_hash(manifest)
    _write_json(root / "RUN_MANIFEST.json", manifest)

    for index, job in enumerate(jobs):
        partition_id = job["partition"]["partition_id"]
        instrument = job["partition"]["instrument_id"]
        records = []
        for rule_index, rule_id in enumerate(rule_ids):
            rule = next(row for row in registry["rules"] if row["rule_id"] == rule_id)
            # The second job is deliberately a missing-data population for
            # the second rule, so null metrics can be asserted.
            if index == 1 and rule_index == 1:
                continue
            opportunity_id = f"{partition_id}-{rule_index}"
            records.append({
                "opportunity": {
                    "opportunity_id": opportunity_id,
                    "rule_id": rule_id,
                    "method_id": rule["method_id"],
                    "branch": rule["branch"],
                    "partition_id": partition_id,
                    "instrument_id": instrument,
                    "session_date": job["partition"]["date"],
                    "evidence_mode": "research_comparison",
                    "observation_unit": rule["observation_unit"],
                },
                "replay": {
                    "opportunity_id": opportunity_id,
                    "verdict": "pass" if rule_index == 0 else "unknown",
                    "selected_signal_at": 1 if rule_index == 0 else None,
                    "censored": rule_index == 1,
                    "ambiguous": False,
                    "timing_violations": 0,
                    "proxy_as_faithful": 0,
                },
                "source_assembly": {"result": {"verdict": "unknown"}},
            })
        rule_rows = []
        for rule_id in rule_ids:
            rule = next(row for row in registry["rules"] if row["rule_id"] == rule_id)
            subset = [record for record in records if record["opportunity"]["rule_id"] == rule_id]
            missing = index == 1 and rule_id == rule_ids[1]
            rule_rows.append({
                "rule_id": rule_id,
                "method_id": rule["method_id"],
                "branch": rule["branch"],
                "observation_unit": rule["observation_unit"],
                "search_executed": True,
                "status": "missing_data" if missing else "completed",
                "population_holes": [],
                "summary": population_summary(subset),
                "references": [],
            })
        artifact = {
            "schema": "phase1-empirical-artifact-v1",
            "job_id": job["job_id"],
            "registry_sha256": registry["registry_sha256"],
            "implementation_sha256": f"impl-{index}",
            "records": records,
            "rules": rule_rows,
            "bars": [],
        }
        artifact_path = root / "artifacts"
        if versioned:
            artifact_path /= manifest["manifest_sha256"][:16]
        artifact_path = artifact_path / job["job_id"] / "records.json"
        _write_json(artifact_path, artifact)
        checkpoint = {
            "schema": "phase1-empirical-checkpoint-v1",
            "job_id": job["job_id"],
            "job_sha256": content_hash(job),
            "cohort": job["cohort"],
            "partition_id": partition_id,
            "session_date": job["partition"]["date"],
            "instrument_id": instrument,
            "registry_sha256": registry["registry_sha256"],
            "implementation_sha256": f"impl-{index}",
            "run_manifest_sha256": manifest["manifest_sha256"],
            "search_completed": True,
            "artifact_path": str(artifact_path.resolve()),
            "artifact_sha256": file_hash(artifact_path),
            "rules": rule_rows,
        }
        _write_json(root / "checkpoints" / f"{job['job_id']}.json", checkpoint)
    return root, rule_ids


def test_report_groups_and_keeps_missing_data_null(tmp_path: Path):
    root, rule_ids = _fixture(tmp_path)
    result = build_results(root)
    assert result["validation"]["valid"] is True
    assert result["validation"]["warnings"]
    assert result["scope"]["cohorts"]["bar-monthly"]["eligible"] == 2
    assert result["scope"]["cohorts"]["bar-monthly"]["scanned"] == 2
    rule = next(row for row in result["rule_reports"] if row["rule_id"] == rule_ids[1])
    assert rule["status"] == "data_hole"
    assert any(group["status"] == "data_hole" and group["rate"] is None for group in rule["groups"])
    assert len(result["rule_reports"]) == 50
    assert len(result["extra_observation_units"]) == 8
    write_results(root)
    markdown = (root / "RESULTS.md").read_text()
    assert "family | variant | n | faithful_disagreements | status | report path" in markdown
    assert "family | id | verdict | fixture | leakage | proxy-as-faithful | notes" in markdown


def test_report_rejects_swapped_checkpoint_filename(tmp_path: Path):
    root, _ = _fixture(tmp_path, two_jobs=False)
    checkpoint = root / "checkpoints/bar-monthly--P1.json"
    checkpoint.rename(root / "checkpoints/bar-monthly--P2.json")
    result = build_results(root)
    assert result["validation"]["valid"] is False
    assert any("filename/content identity mismatch" in error for error in result["validation"]["errors"])


def test_report_rejects_artifact_tampering(tmp_path: Path):
    root, _ = _fixture(tmp_path, two_jobs=False)
    artifact = root / "artifacts/bar-monthly--P1/records.json"
    artifact.write_text(artifact.read_text().replace('"bars": []', '"bars": [{"tampered": true}]'))
    result = build_results(root)
    assert result["validation"]["valid"] is False
    assert any("artifact hash mismatch" in error for error in result["validation"]["errors"])


def test_mixed_missing_and_nonempty_same_group_keeps_observed_counts(tmp_path: Path):
    root, rule_ids = _fixture(tmp_path, same_year=True)
    result = build_results(root)
    rule = next(row for row in result["rule_reports"] if row["rule_id"] == rule_ids[1])
    group = next(row for row in rule["groups"] if row["year"] == "2025")
    assert group["population_complete"] is False
    assert group["observed_counts"] == {"p": 0, "f": 0, "u": 1, "n": 0, "N": 1}
    assert group["N"] == 1
    assert group["rate"] is None
    assert group["observed_interval"] == [0.0, 1.0]


def test_unscanned_partition_retains_observed_rule_counts(tmp_path: Path):
    root, rule_ids = _fixture(tmp_path, two_jobs=False)
    manifest_path = root / "RUN_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["jobs"].append({
        "job_id": "bar-monthly--P2",
        "cohort": "bar-monthly",
        "partition": {"partition_id": "P2", "date": "2025-01-03", "instrument_id": 42},
        "rule_ids": rule_ids,
    })
    manifest["manifest_sha256"] = content_hash({key: value for key, value in manifest.items() if key != "manifest_sha256"})
    _write_json(manifest_path, manifest)
    result = build_results(root)
    rule = next(row for row in result["rule_reports"] if row["rule_id"] == rule_ids[0])
    assert rule["scope"]["remaining"] == 1
    assert rule["population_complete"] is False
    assert rule["observed_counts"]["n"] == 1
    assert rule["n"] == 1
    assert rule["N"] == 1
    assert rule["rate"] is None


def test_group_scope_does_not_repeat_other_year_or_contract(tmp_path: Path):
    root, rule_ids = _fixture(tmp_path, two_contracts=True)
    result = build_results(root)
    rule = next(row for row in result["rule_reports"] if row["rule_id"] == rule_ids[0])
    assert len(rule["groups"]) == 2
    assert {(row["year"], row["instrument_id"], row["eligible"], row["scanned"], row["remaining"])
            for row in rule["groups"]} == {("2025", "42", 1, 1, 0), ("2026", "43", 1, 1, 0)}
    assert all(row["population_complete"] is True for row in rule["groups"])
    assert rule["observed_counts"]["p"] == sum(row["observed_counts"]["p"] for row in rule["groups"])
    assert rule["observed_counts"]["f"] == sum(row["observed_counts"]["f"] for row in rule["groups"])
    assert rule["observed_counts"]["u"] == sum(row["observed_counts"]["u"] for row in rule["groups"])
    assert rule["observed_counts"]["n"] == sum(row["observed_counts"]["n"] for row in rule["groups"])
    assert rule["observed_counts"]["N"] == sum(row["observed_counts"]["N"] for row in rule["groups"])


def test_versioned_run_uses_manifest_hash_artifact_namespace(tmp_path: Path):
    root, _ = _fixture(tmp_path, two_jobs=False, versioned=True)
    result = build_results(root)
    assert result["validation"]["valid"] is True
    manifest = json.loads((root / "RUN_MANIFEST.json").read_text())
    assert (root / "artifacts" / manifest["manifest_sha256"][:16]).exists()


def test_versioned_run_rejects_foreign_artifact_namespace(tmp_path: Path):
    root, _ = _fixture(tmp_path, two_jobs=False, versioned=True)
    checkpoint_path = root / "checkpoints/bar-monthly--P1.json"
    checkpoint = json.loads(checkpoint_path.read_text())
    checkpoint["artifact_path"] = checkpoint["artifact_path"].replace(
        "/artifacts/" + checkpoint["run_manifest_sha256"][:16] + "/",
        "/artifacts/foreign-prefix/",
    )
    _write_json(checkpoint_path, checkpoint)
    result = build_results(root)
    assert result["validation"]["valid"] is False
    assert any("artifact path is not the canonical job artifact" in error for error in result["validation"]["errors"])


def test_truly_unavailable_family_has_null_n(tmp_path: Path):
    root, _ = _fixture(tmp_path, two_jobs=False)
    result = build_results(root)
    family = next(row for row in result["family_reports"] if row["family"] == "GB-SCALP")
    assert family["n"] is None
    assert family["observed_counts"] is None
