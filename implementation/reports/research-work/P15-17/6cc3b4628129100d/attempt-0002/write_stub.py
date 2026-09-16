"""Write the P15-17 stage B draft receipt stub for the rehearsal attempt."""
import json, sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from trading_research.research.rule_discovery import search_run as m

R = Path(sys.argv[1])
FREEZE = Path(sys.argv[2])
WS = Path("/workspace")

# The verifier's required set plus this task's reads (AGENTS.md rule; the cards'
# read pointer is HOW_TO_RUN.md, which replaces the retired PSTACK_EXECUTION.md).
PLAN_FILES = [
    "AGENTS.md",
    "planning/ROADMAP.md",
    "planning/research-program/PSTACK_EXECUTION.md",
    "planning/research-program/HOW_TO_RUN.md",
    "planning/research-program/WORKFLOW.md",
    "planning/research-program/DATA_CONTRACTS.md",
    "planning/research-program/ASSURANCE.md",
    "planning/research-program/SILENT_FAILURES.md",
    "planning/research-program/TASK_GRAPH.json",
    "planning/research-program/ASSURANCE_CASES.json",
    "planning/research-program/AMENDMENTS.json",
    "planning/phase-1-5/tasks/P15-17.md",
    "planning/phase-1-5/SEARCH_CONTRACT.md",
    "planning/research-program/EVALUATION.md",
    "planning/research-program/OUTCOMES.md",
    "planning/research-program/RETENTION.md",
    "planning/research-program/PERFORMANCE.md",
]


def digest(path):
    h = sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def artifact(relative):
    path = R / relative
    if path.is_dir():
        members = sorted(p for p in path.rglob("*") if p.is_file())
        return {
            "path": str(path),
            "files": len(members),
            "members": {str(p.relative_to(path)): digest(p) for p in members},
        }
    return {"path": str(path), "sha256": digest(path)} if path.is_file() else {"path": str(path), "missing": True}


freeze = json.loads(FREEZE.read_text())
meta = json.loads((R / "RUN_META.json").read_text())
complete = json.loads((R / "RUN_COMPLETE.json").read_text())
results = json.loads((R / "BREADTH_RESULTS.json").read_text())

stub = {
    "schema_version": "research-p15-17-draft-receipt-v1",
    "status": "draft",
    "task_id": "P15-17",
    "stage": "B",
    "role": "rehearsal and parity oracle; the definitive run is attempt-0003",
    "written_at": datetime.now(timezone.utc).isoformat(),
    "attempt": str(R),
    "stage_a_attempt": str(FREEZE.parent),
    "PLAN_SNAPSHOT": {
        "root": str(WS),
        "note": "the live planning files as they are at the time of this draft",
        "files": {rel: digest(WS / rel) for rel in PLAN_FILES},
    },
    "freeze": {"path": str(FREEZE), "sha256": digest(FREEZE), "immutable": freeze["immutable"]},
    "predecessor_receipts": {
        "P15-08": {
            "path": freeze["ra3_bank"]["p15_08_receipt_path"],
            "sha256": freeze["ra3_bank"]["p15_08_receipt_sha256"],
        },
        "P15-16": {
            "path": freeze["ra3_bank"]["p15_16_closed_receipt_path"],
            "sha256": freeze["ra3_bank"]["p15_16_closed_receipt_sha256"],
        },
        "P15-16A": {
            "status": "PENDING",
            "reason": "the P15-16A receipt is issued by the integration round; its digest, the"
            " corrected B0.2 run root and the supplemental root for prior_week_level, asia_box,"
            " prior_day_level and the tdo_retest mode are supplied for attempt-0003",
        },
    },
    "run": {
        "run_root": str(R),
        "run_meta_sha256": digest(R / "RUN_META.json"),
        "manifest_sha256": digest(R / "MANIFEST.json"),
        "run_complete_sha256": digest(R / "RUN_COMPLETE.json"),
        "dates_declared": complete["dates"],
        "declared_jobs": complete["declared_jobs"],
        "written_jobs": complete["written_jobs"],
        "declared_jobs_reconciled": complete["declared_jobs_reconciled"],
        "retained_failures": complete["retained_failures"],
        "workers": meta["workers"],
        "b02_roots": meta["b02_roots"],
        "code_identity": meta["code_identity"],
        "previous_code_identities": meta.get("previous_code_identities", []),
        "code_identity_equivalence": {
            "claim": "the run started under a runner without the per-session cache release and"
            " finished under the runner with it",
            "evidence": "four first-segment dates (2020-01-02, 2021-03-15, 2022-03-14, 2022-06-15)"
            " re-run under the second identity: 640/640 candidate documents and 4/4 daily records"
            " byte-identical",
            "log": "implementation/reports/research-work/P15-17/_fast/WORK_LOG.md"
            " (round 2, 'Identity equivalence')",
        },
    },
    "artifacts": {
        name: artifact(name)
        for name in (
            "TRIALS.jsonl",
            "BREADTH_RESULTS.json",
            "REFINEMENT_ALLOWLIST.json",
            "FAMILY_REPORTS",
            "JOB_RECONCILIATION.json",
            "WORK_LOG.md",
        )
    },
    "results_summary": {
        "candidates": results["candidates"],
        "supported": results["supported"],
        "unsupported": len(results["unsupported"]),
        "rows_by_status": results["coverage"]["rows_by_status"],
        "runtime_failure_classes": results["coverage"]["runtime_failure_classes"],
        "promoted": [r["candidate_id"] for r in results["decisions"] if r["promotion"]["promoted"]],
        "dispositions": {
            key: sum(1 for r in results["decisions"] if r["promotion"]["disposition"] == key)
            for key in sorted({r["promotion"]["disposition"] for r in results["decisions"]})
        },
        "retention": {
            key: sum(1 for r in results["retention"] if r["status"] == key)
            for key in sorted({r["status"] for r in results["retention"]})
        },
    },
    "acceptance": {
        "A01": "every registered candidate has a row in every fold: TRIALS.jsonl 800 = 160 x 5;"
        " terminal dispositions in BREADTH_RESULTS.coverage.rows_by_status sum to 278,560 and"
        " RUN_COMPLETE reconciles 278,720 declared = 278,560 written + 160 absent on the retained"
        " failure date",
        "A02": "tests/rule_discovery/test_p15_17.py::test_a02_outer_outcomes_do_not_change_the_fold_choice"
        " and select_for_fold_from_series reading only fit+tune days",
        "A03": "the bank is the frozen CANDIDATE_BANK.json pinned in MANIFEST.bank_sha256; no"
        " candidate was added after any result was read",
        "A04": "daily_benchmark raises unless opportunities == fills + exclusions; JOB_RECONCILIATION"
        " checks both sides of every declared job document",
        "A05": "complete_run closes a run whose only pending dates carry retained failure records,"
        " naming them; pending dates without a record are refused",
        "A06": "PENDING: the final receipt carries command exit codes and predecessor verification"
        " for attempt-0003",
        "A07": "PENDING: EVIDENCE_MATRIX.json is written with the final receipt",
        "A08": "PENDING: the assigned silent-failure probes (S06, S07, S11, S12, S13, S15, S22, S24,"
        " S32 per the live card; S01-S03 are cited from the P15-01 bound evidence, not re-probed)"
        " are run against attempt-0003",
    },
    "limitations": [
        "This is the rehearsal: the pairing baseline is the uncorrected P15-16A root"
        " 1019e6c09ee54609, so no disposition here is a research finding about a candidate.",
        "REFILL-STUDY:supplied_selected_order has no B0.2 job in any P15-16A root; its two"
        " candidates pair against an in-process B0.2 scan (pairing_baseline_source ="
        " in_process_b02_scan).",
        "800 candidate-date rows are input_unavailable (20 holiday sessions x 40 SIRES and"
        " REFILL-STUDY candidates, 'market has no cutoff clock'): a missing input, recorded with"
        " its date, not counted as a software failure and not silently dropped.",
        "2020-06-30 is a retained runtime failure (no native account-day view); its 160 declared"
        " jobs are absent and named in RUN_COMPLETE.json.",
        "The cost stress covers commission and exit slippage exactly and the 500 ms latency by"
        " rebinding the two constants exits.py reads at call time; no file is edited.",
    ],
}
path = R / "DRAFT_STUB.json"
path.write_text(json.dumps(stub, indent=1, sort_keys=True))
print("wrote", path)
print("plan snapshot files", len(stub["PLAN_SNAPSHOT"]["files"]))
print("artifacts", {k: (v.get("sha256") or v.get("files")) for k, v in stub["artifacts"].items()})
