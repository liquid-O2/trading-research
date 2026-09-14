# 00-foundation v2 additional-repair coordinator work log

Installed pstack: poteto-mode SKILL.md sha256 `dc166350bc3bb3b9a061930380e971b3ca8c9f55822c52d7249b92b43f5cb865`. Autonomous-run playbook sha256 `15e54ad3ac92565613980772d8708de6e19cc4690bfd4bb3fb8836522407377b`. Bug-fix playbook sha256 `e958c67d5454fc12d76ec645b50dfd85c423082aac13a49e2913ef2815948216`. figure-it-out sha256 `e041c64a39f1084a20e60ee99762c4dbd3ec8be56ed33fd68ea867b8bd8bd3e4`. show-me-your-work sha256 `831e85ba3f84f38bf338cd03e6af050fea357752e25a825e334c99f59d7f2077`. Parent Grok for every role. `inherit-parent` means the subagent `model` field is omitted.

## Exit condition

All of the following hold on actual new artifacts, not the rejected v2 attempt `240838146c38c484`:

1. Targeted tests in `tests/rule_discovery/test_p15_00.py` and `test_p15_01.py` pass with `-p no:cacheprovider`.
2. Unchanged 27-case checker `/workspace/tools/check_foundation_adversarial.py` passes 27/27 on the new P15-00, P15-01 and subphase receipts.
3. Additional probe `/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/additional_probe.py` matches expected exits on the new P15-00, subphase and GATE_REVIEW: three accepted controls exit 0, eleven invalid cases exit 2.
4. `verify_research_release.py subphase --receipt NEW_SUBPHASE --gate-review NEW_GATE_REVIEW` exits 0.
5. Historical v1 and reviewed v2 attempts remain byte-identical. Phase 1 evidence and `/workspace/data` are untouched. Subphase 01 is not started.

## Playbook steps

1. State the exit condition. done, this file.
2. Pick Cursor `/loop`. skip: this Grok build has no Cursor `/loop` or wake facility. PSTACK_EXECUTION says execute and checkpoint normally.
3. Smallest verified change per unit. in progress. Git commit skipped: user forbids commit/push/reset.
4. Mid-run discoveries. pending.
5. Checkpoint in DECISIONS.tsv. in progress.
6. Stop when the predicate is met. pending.
7. Opening a PR. skip: user forbids PR/push/merge.

figure-it-out Phase A/B used the existing 00-foundation runbook and the 2026-09-14 v2 review. No new research plan.

Bug-fix how/why fan-out. skip: REVIEW.md names the five mechanisms and line numbers; confirmed by reading receipts.py. Architect/arena. skip: ASSURANCE.md already names the validation rules.

## Throughput checkpoint

Blocking first steps. Reproduce the ten invalid acceptances on the public CLI. Repair `verify_gate_review`, evidence-matrix, snapshot identity, artifact schema and lineage leaf checks. Add discriminating tests. Repair producers if stricter checks expose incomplete artifacts. Write new immutable P15-00, P15-01, subphase and GATE_REVIEW identities.

Independent workstreams. None. Shared checkout, one writer.

Shared mutable state. `/workspace/implementation/src/trading_research/research/contracts/receipts.py`, producers in `baseline_manifest.py` and `receipts.py`, tests, and `implementation/reports/research-work`.

Smallest safe decomposition. Save failing additional-probe output. Change the verifier. Prove with tests. Then new receipts.

## Worker assignment

| worker | task | checkout | status | evidence |
| --- | --- | --- | --- | --- |
| coordinator (parent Grok) | reproduce, repair, produce receipts | `/workspace` | completed | P15-00 `40ffb49bc037e3cc`, P15-01 `ee71900e26791e89`, subphase `6824d15fbda635ce` |
| read-only reviewer | after first candidate | `/workspace` | completed, issues | sibling holes then repaired; inherit-parent |

## Commands

Recorded as they run.
