# 00-foundation coordinator work log

Installed pstack: poteto-mode SKILL.md sha256 `dc166350bc3bb3b9a061930380e971b3ca8c9f55822c52d7249b92b43f5cb865`. Autonomous-run playbook sha256 `15e54ad3ac92565613980772d8708de6e19cc4690bfd4bb3fb8836522407377b`. figure-it-out sha256 `e041c64a39f1084a20e60ee99762c4dbd3ec8be56ed33fd68ea867b8bd8bd3e4`. Parent Grok for every role. `inherit-parent` means the subagent `model` field is omitted.

## Exit condition

P15-00 and P15-01 `TASK_RECEIPT.json` files are `implemented_verified` with A01–A06 true. `verify_research_release.py task` exits 0 on both actual receipts. `verify_research_release.py subphase` exits 0 on the coordinator `SUBPHASE_RECEIPT.json`. Next subphase is not started.

## Playbook steps

1. State the exit condition. done.
2. Pick Cursor `/loop`. skip: this Grok build has no Cursor `/loop` or wake facility.
3. Smallest verified change per unit. done.
4. Mid-run discoveries. done (`/tmp` log path replaced by a durable attempt).
5. Checkpoint in DECISIONS.tsv. done.
6. Stop when the predicate is met. done. Subphase verifier exit 0.

figure-it-out Phase A/B used the existing 00-foundation runbook. No new research plan.

Feature how. skip: TYPE_REFERENCE.py and the task cards already name the types.
Feature architect. skip: the blueprint is concrete.
Feature Opening a PR / commits / interrogate. skip: local evidence only.

## Throughput checkpoint

Blocking first steps. Verify the accepted Phase 1 census. Implement types and identity. Bind baseline identities and engineering dates from coverage. Write the P15-00 receipt. Build the verifier. Verify P15-00 retrospectively. Write the subphase receipt.

Independent workstreams. None until P15-00 is accepted. P15-01 depends on it. Shared checkout serializes writers.

Shared mutable state. `/workspace` git tree, `research/contracts`, `implementation/tools/verify_research_release.py`, and `implementation/reports/research-work`.

Smallest safe decomposition. Coordinator owned the P15-00 first slice. One P15-01 code writer after that receipt exists. Coordinator writes `SUBPHASE_RECEIPT.json` and reviews.

## Previous gate

Accepted Phase 1 census. `CENSUS_RECONCILIATION.json` status pass. 1,742 sessions, 99,294 daily jobs, 18,747 setups. Registry sha256 `63e572556212f5c02f524af1cb8b70ef4e35eaa07649c24b78bb604d79f9cbf6`. Coverage sha256 `cddf4a52d79bf9c00ad5e84c29e51222876e09f4f156bd09f0e0f818462940c8`. Calendar composition sha256 `8508a2bfadc1af381bf1b35345d9c6519a7d07999d18955cfddc7bd500b4ecb2`. Bootstrap task predecessors: none.

Unrelated dirty tree at start: planning/wiki moves and README/AGENTS edits. Not staged into this subphase.

## Worker assignment

| worker | task | checkout | status | evidence |
| --- | --- | --- | --- | --- |
| coordinator | P15-00 first slice | `/workspace` | implemented_verified; P15-01 verified it retrospectively | `implementation/reports/research-work/P15-00/b291864ccceaca9a/attempt-0001/TASK_RECEIPT.json` |
| poteto-agent `01a09f22-0fbf-70e1-8ae6-f4a785343a20` | P15-01 | `/workspace` after coordinator pause | completed | `implementation/reports/research-work/P15-01/039267553e8bf721/attempt-0001/TASK_RECEIPT.json` sha256 `549429da5d43ff6fc347723fe4f4c8eda4550b31190bb94324ab82e2afba2c4f` |
| coordinator | SUBPHASE_RECEIPT.json | `/workspace` | pass, verifier exit 0 | `implementation/reports/research-work/00-foundation/f7135f8d696ff1f5/attempt-0001/SUBPHASE_RECEIPT.json` |
| poteto-agent `01a09f34-dbf0-7141-8e96-3bde4ceb87f4` | trail review | read-only | completed | inherit-parent Grok, not cross-model |

Retained incomplete P15-00 attempts under `d6ee475ab70bbc3a` used a `/tmp` log path.
