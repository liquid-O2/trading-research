"""Write the P15-18 draft receipt stub for the rehearsal attempt."""
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
    "planning/phase-1-5/tasks/P15-18.md",
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
bank = json.loads((R / "REFINEMENT_BANK.json").read_text())
rules = json.loads((R / "SELECTED_RULES_BY_FOLD.json").read_text())
dispositions = json.loads((R / "FAMILY_DISPOSITIONS.json").read_text())
combinations = json.loads((R / "combinations" / "COMBINATIONS.json").read_text())
breadth = Path(sys.argv[3])

stub = {
    "schema_version": "research-p15-18-draft-receipt-v1",
    "status": "draft",
    "task_id": "P15-18",
    "role": "rehearsal on the P15-17 rehearsal allowlist; the definitive round runs on attempt-0003",
    "written_at": datetime.now(timezone.utc).isoformat(),
    "attempt": str(R),
    "PLAN_SNAPSHOT": {
        "root": str(WS),
        "note": "the live planning files as they are at the time of this draft",
        "files": {rel: digest(WS / rel) for rel in PLAN_FILES},
    },
    "freeze": {"path": str(FREEZE), "sha256": digest(FREEZE)},
    "predecessor_receipts": {
        "P15-17": {
            "status": "PENDING",
            "attempt": str(breadth),
            "draft_stub_sha256": digest(breadth / "DRAFT_STUB.json"),
            "allowlist_sha256": digest(breadth / "REFINEMENT_ALLOWLIST.json"),
            "reason": "P15-17's receipt is issued for attempt-0003 after P15-16A closes",
        }
    },
    "run": {
        "run_root": str(R),
        "run_meta_sha256": digest(R / "RUN_META.json"),
        "manifest_sha256": digest(R / "MANIFEST.json"),
        "run_complete_sha256": digest(R / "RUN_COMPLETE.json"),
        "shard_inventory_sha256": digest(R / "SHARD_INVENTORY.json"),
        "bank": meta["bank"],
        "workers": meta["workers"],
        "declared_jobs": complete["declared_jobs"],
        "written_jobs": complete["written_jobs"],
        "declared_jobs_reconciled": complete["declared_jobs_reconciled"],
        "retained_failures": complete["retained_failures"],
        "code_identity": meta["code_identity"],
        "combination_run_root": str(R / "combinations"),
    },
    "artifacts": {
        name: artifact(name)
        for name in (
            "REFINEMENT_BANK.json",
            "TRIALS.jsonl",
            "SELECTED_RULES_BY_FOLD.json",
            "FAMILY_DISPOSITIONS.json",
            "FAMILY_REPORTS",
            "WORK_LOG.md",
            "SELF_CHECK.txt",
            "combinations/COMBINATIONS.json",
        )
    },
    "results_summary": {
        "bank_counts": bank["counts"],
        "caps": {
            "per_bank": bank["max_neighbors_per_bank"],
            "per_family": bank["max_neighbors_per_family"],
        },
        "folds": len(rules["folds"]),
        "combinations_executed": combinations["executed"],
        "combinations_not_applicable": combinations["not_applicable"],
        "family_dispositions": [
            {"family": row["family"], "status": row["status"], "first_attribution": row["first_attribution"]}
            for row in dispositions["families"]
        ],
        "all_history_descriptive_recommendation": rules["all_history_descriptive_recommendation"],
    },
    "acceptance": {
        "A01": "a combination exists only when each ingredient beats B0.2 on inner tuning and both live"
        " on one branch: tests test_a_combination_needs_both_ingredients_to_beat_the_baseline and"
        " test_a_combination_whose_ingredients_live_on_different_branches_is_not_applicable;"
        " combinations/COMBINATIONS.json records 3 executed and 10 not applicable with reasons",
        "A02": "test_a_fold_selects_only_from_its_own_inner_days: moving a fold's test days leaves its"
        " choice identical and moves the fold whose fit days those are",
        "A03": "the support gate is unchanged from the breadth stage; a six-example result stays"
        " inconclusive_support (refinement.support_sensitivity, reported at half and twice)",
        "A04": "every proposal has exactly one ledger row (190 = the bank's rows), including duplicates"
        " and not-applicable ones; Holm runs across the stage's candidates",
        "A05": "SELECTED_RULES_BY_FOLD.json carries a per-fold selection_manifest_id and a separately"
        " labelled all-history descriptive recommendation",
        "A06": "PENDING: command exit codes and predecessor verification with the P15-17 receipt",
        "A07": "PENDING: EVIDENCE_MATRIX.json is written with the final receipt",
        "A08": "PENDING: the assigned probes (S07, S11, S12, S13, S17, S22, S24, S32; S01-S03 cited from"
        " the P15-01 bound evidence) are run against the definitive round",
    },
    "limitations": [
        "Rehearsal: the allowlist comes from the P15-17 rehearsal, whose pairing baseline is the"
        " uncorrected P15-16A root, so no disposition here is a research finding.",
        "A combined candidate needs both mechanisms on one branch; 10 of 13 proposals pair mechanisms"
        " from different branches of the same family and are recorded not_applicable.",
        "2020-06-30 is a retained runtime failure in both stages (no native account-day view).",
    ],
}
path = R / "DRAFT_STUB.json"
path.write_text(json.dumps(stub, indent=1, sort_keys=True))
print("wrote", path)
print("plan snapshot files", len(stub["PLAN_SNAPSHOT"]["files"]))
