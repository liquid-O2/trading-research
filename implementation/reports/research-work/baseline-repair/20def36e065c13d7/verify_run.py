"""Post-run verification for B0.1 full-history measurement. Does not write under data/sources/phase1-live."""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json
import subprocess
import sys

ROOT = Path("/workspace")
RUN_ROOT = Path(__file__).resolve().parent
PHASE1 = ROOT / "implementation/reports/phase1-live/historical-measurement/run-1.0.1"
PREVIEW = (
    ROOT
    / "planning/research-program/reviews/phase1-code-review-2026-09-14/repair-preview"
    / "BASELINE_REPAIR_DELTA.json"
)
DEFERRED = "JJ-TBR:branch:judas_reversal_deferred"
COUNT_KEYS = ("episodes", "pass", "fail", "unknown", "no_setup")
PY = "/workspace/implementation/.venv/bin/python"


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_job(path: Path):
    return json.loads(gzip.decompress(path.read_bytes()))


def counts(document):
    episodes = document.get("episodes") or []
    no_setup = 0
    data_unavailable = 0
    for episode in episodes:
        status = (episode.get("strategy_assessment") or {}).get("status")
        if status == "no_setup":
            no_setup += 1
        elif status == "data_unavailable":
            data_unavailable += 1
    return {
        "episodes": len(episodes),
        "pass": sum(episode["research_verdict"] == "pass" for episode in episodes),
        "fail": sum(episode["research_verdict"] == "fail" for episode in episodes),
        "unknown": sum(episode["research_verdict"] == "unknown" for episode in episodes),
        "no_setup": no_setup,
        "data_unavailable": data_unavailable,
    }


def run_cmd(argv, cwd=None, env=None):
    proc = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True)
    return proc


def first_failure_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("FAILED") or stripped.startswith("FAIL ") or "ERROR" in stripped[:12]:
            return stripped
    return ""


def summary_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in reversed(lines):
        if "passed" in line or "failed" in line or "TOTAL FAILURES" in line or line.startswith("exit"):
            return line
    return lines[-1] if lines else ""


def main():
    report = {"run_root": str(RUN_ROOT), "checks": []}
    manifest = json.loads((RUN_ROOT / "MANIFEST.json").read_text())
    summary = json.loads((RUN_ROOT / "SUMMARY.json").read_text())
    complete = json.loads((RUN_ROOT / "RUN_COMPLETE.json").read_text())
    preview = json.loads(PREVIEW.read_text())

    # 1. preview B0.1 columns
    ours = {row["coverage_id"]: row for row in summary["preview_by_branch"]}
    mismatches = []
    for row in preview["branches"]:
        cid = row["coverage_id"]
        got = ours.get(cid)
        if got is None:
            mismatches.append({"coverage_id": cid, "error": "missing"})
            continue
        for key in COUNT_KEYS:
            if row[f"{key}_b01"] != got[f"{key}_b01"]:
                mismatches.append(
                    {
                        "coverage_id": cid,
                        "field": f"{key}_b01",
                        "preview": row[f"{key}_b01"],
                        "run": got[f"{key}_b01"],
                    }
                )
    report["checks"].append(
        {
            "name": "preview_40_b01_counts",
            "ok": not mismatches,
            "n_mismatches": len(mismatches),
            "sample": mismatches[:12],
        }
    )

    # 2. B0 vs run-1.0.1 on the 40 preview dates
    b0_bad = []
    for day in summary["preview_dates"]:
        completion = json.loads((RUN_ROOT / "jobs" / day / "completion.json").read_text())
        for cid, rec in completion["branch_stats"].items():
            gold_path = PHASE1 / "jobs/evaluation" / day / (cid.replace(":", "--") + ".json.gz")
            if cid == DEFERRED:
                if gold_path.exists():
                    b0_bad.append({"date": day, "coverage_id": cid, "error": "unexpected B0 file"})
                elif rec["b0"]["episodes"] != 0:
                    b0_bad.append({"date": day, "coverage_id": cid, "error": "deferred B0 not zero"})
                continue
            gold = counts(read_job(gold_path))
            for key in ("episodes", "pass", "fail", "unknown", "no_setup", "data_unavailable"):
                if rec["b0"][key] != gold[key]:
                    b0_bad.append(
                        {
                            "date": day,
                            "coverage_id": cid,
                            "field": key,
                            "stored": rec["b0"][key],
                            "run_1_0_1": gold[key],
                        }
                    )
    report["checks"].append(
        {
            "name": "preview_40_b0_vs_run101",
            "ok": not b0_bad,
            "n_mismatches": len(b0_bad),
            "sample": b0_bad[:12],
        }
    )

    # 3. every job hash in completion
    hash_bad = []
    n_jobs = 0
    for day in manifest["dates"]:
        completion = json.loads((RUN_ROOT / "jobs" / day / "completion.json").read_text())
        for item in completion["jobs"]:
            n_jobs += 1
            path = Path(item["path"])
            if not path.is_file() or sha256_file(path) != item["sha256"]:
                hash_bad.append({"date": day, "coverage_id": item["coverage_id"]})
    report["checks"].append(
        {
            "name": "job_hashes_in_completion",
            "ok": not hash_bad and n_jobs == complete["job_count"],
            "n_jobs": n_jobs,
            "expected": complete["job_count"],
            "n_mismatches": len(hash_bad),
            "sample": hash_bad[:8],
        }
    )

    # 4. check_outcome_fixtures
    env = {**{k: v for k, v in __import__("os").environ.items()}, "PYTHONPATH": str(ROOT / "implementation/src")}
    proc = run_cmd([PY, str(ROOT / "tools/check_outcome_fixtures.py")], cwd=str(ROOT / "implementation"), env=env)
    out = proc.stdout + proc.stderr
    print("VERIFIER check_outcome_fixtures.py exit", proc.returncode)
    print("SUMMARY", summary_line(out))
    fail = first_failure_line(out)
    if fail:
        print("FIRST_FAILURE", fail)
    report["checks"].append(
        {
            "name": "check_outcome_fixtures",
            "ok": proc.returncode == 0,
            "exit": proc.returncode,
            "summary": summary_line(out),
            "first_failure": fail,
        }
    )

    # 5. baseline repair tests
    proc = run_cmd(
        [PY, "-m", "pytest", "-p", "no:cacheprovider", "-q", "tests/rule_discovery/test_baseline_repairs.py", "--tb=line"],
        cwd=str(ROOT / "implementation"),
        env=env,
    )
    out = proc.stdout + proc.stderr
    print("VERIFIER pytest test_baseline_repairs.py exit", proc.returncode)
    print("SUMMARY", summary_line(out))
    fail = first_failure_line(out)
    if fail:
        print("FIRST_FAILURE", fail)
    report["checks"].append(
        {
            "name": "pytest_baseline_repairs",
            "ok": proc.returncode == 0,
            "exit": proc.returncode,
            "summary": summary_line(out),
            "first_failure": fail,
        }
    )

    # 6. frozen method_pack git diff
    proc = run_cmd(["git", "diff", "--", "implementation/src/trading_research/research/method_pack"], cwd=str(ROOT))
    diff = proc.stdout.strip()
    print("VERIFIER git diff method_pack exit", proc.returncode)
    print("SUMMARY", "empty" if not diff else f"nonempty {len(diff.splitlines())} lines")
    if diff:
        print("FIRST_FAILURE", diff.splitlines()[0])
    report["checks"].append(
        {
            "name": "method_pack_git_diff_empty",
            "ok": proc.returncode == 0 and not diff,
            "exit": proc.returncode,
            "summary": "empty" if not diff else f"nonempty {len(diff.splitlines())} lines",
        }
    )

    # 7. data tree not newer than manifest
    proc = run_cmd(
        [
            "find",
            str(ROOT / "data"),
            "-newer",
            str(RUN_ROOT / "MANIFEST.json"),
            "-printf",
            "%p\n",
        ]
    )
    newer = [line for line in proc.stdout.splitlines() if line.strip()]
    print("VERIFIER find data -newer MANIFEST exit", proc.returncode)
    print("SUMMARY", f"newer_files {len(newer)}")
    if newer:
        print("FIRST_FAILURE", newer[0])
    report["checks"].append(
        {
            "name": "data_unchanged_vs_manifest",
            "ok": not newer,
            "n_newer": len(newer),
            "sample": newer[:20],
        }
    )

    report["all_ok"] = all(item["ok"] for item in report["checks"])
    (RUN_ROOT / "VERIFY.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("VERIFY_ALL_OK", report["all_ok"])
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
