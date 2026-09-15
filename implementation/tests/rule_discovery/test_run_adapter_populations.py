"""Native three-date adapter-population runner."""
from __future__ import annotations

from pathlib import Path
import json

from trading_research.research.rule_discovery.run_adapter_populations import (
    BRANCH_IDS,
    BRANCH_RECORDS,
    JOB_PATH_SCHEME,
    VWAP_CENSUS_JOB,
    _completion_ok,
    init_run,
    job_filename,
    job_path,
    read_job,
    resolve_recorded_job_path,
    run_dates,
)

B01_ROOT = Path("/workspace/implementation/reports/research-work/adapter-populations/dd386316321ee58d")

DATES = ["2021-01-04", "2022-06-15", "2023-12-08"]
REQUIRED_FILES = (
    "london_box",
    "asia_box",
    "overnight_scan",
    "golden_pocket_continuation",
    "source_long",
)
STAGE_KEYS = ("arrival_read_recorded", "alignment_ok", "profile_allows_trade")


def _fail_text(run_root: Path, result) -> str:
    chunks = []
    for day in result.get("failed_dates") or []:
        path = run_root / "jobs" / day / "FAILURE.json"
        if path.is_file():
            chunks.append(path.read_text())
        else:
            chunks.append(day)
    for item in result.get("date_results") or []:
        if not item.get("ok"):
            chunks.append(item.get("error") or item.get("traceback") or str(item))
    return "\n".join(chunks) or str(result)


def test_adapter_populations_three_native_dates(tmp_path: Path):
    ctx = init_run(workers=1, reports_parent=tmp_path)
    manifest = ctx["manifest"]
    assert manifest["branches"] == list(BRANCH_IDS)
    assert len(manifest["dates"]) == 1742
    assert len(manifest["branch_records"]) == 9

    first = run_dates(ctx, DATES, workers=1)
    if first.get("failed_dates"):
        raise AssertionError(_fail_text(ctx["run_root"], first))

    for day in DATES:
        day_dir = ctx["run_root"] / "jobs" / day
        completion_path = day_dir / "completion.json"
        assert completion_path.is_file(), day
        assert not (day_dir / "FAILURE.json").exists(), day
        assert _completion_ok(completion_path, ctx, ctx["rows"]) is True
        gz = sorted(path.name for path in day_dir.glob("*.json.gz"))
        assert gz == sorted(job_filename(row["coverage_id"]) for row in BRANCH_RECORDS)
        for rec in BRANCH_RECORDS:
            assert (day_dir / job_filename(rec["coverage_id"])).is_file(), rec["coverage_id"]
        completion = json.loads(completion_path.read_text())
        for rec in BRANCH_RECORDS:
            document = read_job(day_dir / job_filename(rec["coverage_id"]))
            assert document.get("baseline_version")
            assert "wall_seconds" in document
            assert "peak_rss_bytes" in document
            if rec["family"] != "SAINT-AMT":
                continue
            for episode in document.get("episodes") or []:
                values = episode.get("values") or {}
                for key in STAGE_KEYS:
                    assert key in values, (day, rec["branch"], key)
            branch_stats = completion["branch_stats"][rec["coverage_id"]]
            assert "stages" in branch_stats
            for key in STAGE_KEYS:
                assert "false" in branch_stats["stages"][key]
                assert "none" in branch_stats["stages"][key]

    second = run_dates(ctx, DATES, workers=1)
    assert second.get("failed_dates") == []
    resumed = [item for item in second.get("date_results") or [] if item.get("resumed") or item.get("ok")]
    assert len(resumed) == 3
    for day in DATES:
        day_dir = ctx["run_root"] / "jobs" / day
        assert not (day_dir / "FAILURE.json").exists(), day
        assert _completion_ok(day_dir / "completion.json", ctx, ctx["rows"]) is True


def test_job_path_coverage_ids_sharing_a_branch_name_do_not_collide():
    root = Path("/tmp/job-path-collision")
    keani = "KEANI-OPEN-ABOVE-VALUE:branch:source_long"
    vwap = "GB-VWAP:branch:source_long"
    left = job_path(root, "2026-01-02", keani)
    right = job_path(root, "2026-01-02", vwap)
    assert left != right
    assert left.name == "KEANI-OPEN-ABOVE-VALUE--branch--source_long.json.gz"
    assert right.name == VWAP_CENSUS_JOB
    assert JOB_PATH_SCHEME == "coverage_id--json.gz"
    assert job_filename(vwap) == VWAP_CENSUS_JOB


def test_b01_run_root_readers_use_recorded_paths_not_the_scheme():
    manifest = json.loads((B01_ROOT / "MANIFEST.json").read_text())
    assert "job_path_scheme" not in manifest
    day = "2021-01-04"
    completion = json.loads((B01_ROOT / "jobs" / day / "completion.json").read_text())
    assert completion["jobs"]
    for item in completion["jobs"]:
        recorded = resolve_recorded_job_path(B01_ROOT, item)
        assert recorded.is_file(), recorded
        assert recorded.name == f"{item['branch']}.json.gz"
        scheme = job_path(B01_ROOT, day, item["coverage_id"])
        assert scheme != recorded
        assert scheme.name == job_filename(item["coverage_id"])
