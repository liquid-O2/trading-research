"""Update wiki and PROJECT_HANDOFF after a successful B0.1 full-history run."""
from __future__ import annotations

from pathlib import Path
import json

ROOT = Path("/workspace")
RUN_ROOT = Path(__file__).resolve().parent


def changed_rows(summary):
    rows = []
    for row in summary["branches"]:
        if (
            row["episodes_b0"] != row["episodes_b01"]
            or row["pass_b0"] != row["pass_b01"]
            or row["fail_b0"] != row["fail_b01"]
            or row["unknown_b0"] != row["unknown_b01"]
            or row["no_setup_b0"] != row["no_setup_b01"]
            or row["data_unavailable_b0"] != row["data_unavailable_b01"]
            or row["verdict_changed"]
            or row["only_b0"]
            or row["only_b01"]
        ):
            rows.append(row)
    return rows


def counts_line(row):
    return (
        f"`{row['coverage_id']}`: B0 ep/pass/fail/unknown/no_setup/data_unavailable "
        f"{row['episodes_b0']}/{row['pass_b0']}/{row['fail_b0']}/{row['unknown_b0']}/{row['no_setup_b0']}/{row['data_unavailable_b0']} "
        f"→ B0.1 {row['episodes_b01']}/{row['pass_b01']}/{row['fail_b01']}/{row['unknown_b01']}/{row['no_setup_b01']}/{row['data_unavailable_b01']}"
        + (f"; directions {dict(sorted(row['directions'].items()))}" if row["directions"] else "")
    )


def update_current_status(summary, complete):
    path = ROOT / "wiki/current-status.md"
    text = path.read_text()
    run_root = complete["run_root"]
    run_id = complete["run_id"]
    changed = changed_rows(summary)
    bullets = "\n".join(f"- {counts_line(row)}" for row in changed)
    block = f"""**B0.1 full-history measurement.** Corrected baseline `{summary['baseline_repair_version']}` was measured over all {summary['n_dates']} run-1.0.1 evaluation dates × {summary['n_branches']} affected branches ({complete['job_count']} jobs) at [run `{run_id}`]({run_root}/). Manifest sha256 `{complete['manifest_sha256']}`. B0 columns are the stored run-1.0.1 job verdicts, not a rescan. Branches whose episode or verdict counts moved:

{bullets}

SAINT-AMT's corrected baseline remains unknown until adapter P15-13 evaluates `arrival_read_recorded`, `alignment_ok` and `profile_allows_trade`. This update did not start subphase 03.

"""
    marker = "**Known baseline discrepancies.**"
    if "B0.1 full-history measurement." in text:
        return
    if marker not in text:
        raise SystemExit("current-status.md missing known baseline discrepancies marker")
    text = text.replace(marker, block + marker, 1)
    # Refresh the longer section's closing sentence about pending measurement.
    old = "Until the corrected baseline is measured, GB-VWAP's rejection column is treated as unknown."
    new = (
        f"The corrected baseline is now measured at `{run_id}`; GB-VWAP rejections that were the D1 overwrite "
        "are unknown under B0.1. SAINT-AMT remains unknown pending P15-13."
    )
    if old in text:
        text = text.replace(old, new)
    path.write_text(text)


def update_log(summary, complete):
    path = ROOT / "wiki/log.md"
    text = path.read_text()
    if complete["run_id"] in text.split("## 2026-09-14 — B0.1 full-history measurement")[-1][:200] if "B0.1 full-history" in text else "":
        return
    if text.startswith("# Ingest log\n\n## 2026-09-14 — B0.1 full-history measurement"):
        return
    changed = changed_rows(summary)
    entry = f"""# Ingest log

## 2026-09-14 — B0.1 full-history measurement

Measured corrected baseline `{summary['baseline_repair_version']}` over the full run-1.0.1 evaluation calendar: {summary['n_dates']} dates × {summary['n_branches']} affected branches = {complete['job_count']} jobs. Run `{complete['run_id']}` at `{complete['run_root']}`. Manifest sha256 `{complete['manifest_sha256']}`; SUMMARY.json sha256 `{complete['summary_sha256']}`; RUN_COMPLETE.json written last. Workers requested 10 (cgroup default {complete.get('cgroup_worker_count')}, quota {complete.get('cpu_quota_cpus')}); achieved concurrency {complete.get('achieved_concurrency')}; orchestrator wall seconds {complete.get('wall_seconds_orchestrator')}. Failed dates: none. B0 columns read from run-1.0.1 job files. {len(changed)} branches changed episode or verdict counts versus B0. SAINT-AMT remains unknown pending P15-13. Frozen method_pack and run-1.0.1 were not edited. Subphase 03 was not started.

Evidence: [run root]({complete['run_root']}/) · [SUMMARY.md]({complete['run_root']}/SUMMARY.md) · [RUN_COMPLETE.json]({complete['run_root']}/RUN_COMPLETE.json) · [disposition](/workspace/planning/research-program/reviews/phase1-code-review-2026-09-14/DISPOSITION.md).

"""
    if not text.startswith("# Ingest log\n"):
        raise SystemExit("wiki/log.md missing ingest header")
    path.write_text(entry + text[len("# Ingest log\n"):])


def update_handoff(complete):
    path = ROOT / "PROJECT_HANDOFF.md"
    text = path.read_text()
    if complete["run_id"] in text and "B0.1 full-history measurement" in text:
        return
    insertion = f"""
### B0.1 full-history measurement

Corrected baseline **B0.1-2026-09-14** measured on the full run-1.0.1 evaluation calendar. Do not start `03-primitives` in this run.

| Artifact | Path | Identity |
| --- | --- | --- |
| Run root | [{complete['run_id']}]({complete['run_root']}/) | run-id `{complete['run_id']}` |
| Manifest | [MANIFEST.json]({complete['run_root']}/MANIFEST.json) | sha256 `{complete['manifest_sha256']}` |
| Summary | [SUMMARY.json]({complete['run_root']}/SUMMARY.json) | sha256 `{complete['summary_sha256']}` |
| Completion | [RUN_COMPLETE.json]({complete['run_root']}/RUN_COMPLETE.json) | job_count {complete['job_count']}; failed_dates empty |

B0 columns are stored run-1.0.1 job verdicts. SAINT-AMT remains unknown pending P15-13.

"""
    anchor = "## 8. Current stopping point\n"
    idx = text.find(anchor)
    if idx < 0:
        raise SystemExit("PROJECT_HANDOFF.md missing section 8")
    # Insert after the first paragraph following the heading.
    rest = text[idx + len(anchor):]
    para_end = rest.find("\n### ")
    if para_end < 0:
        raise SystemExit("PROJECT_HANDOFF.md section 8 has no subsection")
    # Find end of opening paragraph block (blank line before first ###)
    first_sub = text.find("\n### ", idx)
    text = text[:first_sub] + "\n" + insertion + text[first_sub:]
    path.write_text(text)


def main():
    summary = json.loads((RUN_ROOT / "SUMMARY.json").read_text())
    complete = json.loads((RUN_ROOT / "RUN_COMPLETE.json").read_text())
    if complete.get("failed_dates"):
        raise SystemExit("failed_dates not empty; docs updater refuses")
    update_current_status(summary, complete)
    update_log(summary, complete)
    update_handoff(complete)
    print("updated wiki/current-status.md wiki/log.md PROJECT_HANDOFF.md")


if __name__ == "__main__":
    main()
