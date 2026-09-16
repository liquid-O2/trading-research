# Early Phase 2 coordinator work log

Playbook: Autonomous run (`playbooks/autonomous-run.md`) with figure-it-out framing. Installed poteto-mode SKILL.md sha256 `dc166350bc3bb3b9a061930380e971b3ca8c9f55822c52d7249b92b43f5cb865`.

## Throughput checkpoint

Blocking first steps: recompute P15-02 hash; instrument ledger and quote filter; BSM fixture.
Independent workstreams: none. Single writer in this worktree.
Shared mutable state: `implementation/src/trading_research/research/experts/` and `implementation/reports/research-work/`.
Smallest safe decomposition: P2-09 adapters and tests, then P2-10 pricing/boards/atlas, then P2-03 arithmetic, then `produce_receipts.py`.

## Skips

- Autonomous-run step 2 wake/`/loop`: no wake facility in this Grok host.
- Opening a PR, Babysit, Shipping: local implementation only.
- GATE_REVIEW.json and SUBPHASE_RECEIPT.json: orchestrator after merge.
- Previous gate 01-datasets-and-fitting: 2026-09-14 amendment starts these tasks from verified P15-02.
- P2-04: out of scope.
- git commit/push/checkout/reset/stash/rebase: forbidden.
- Eval and Hillclimb playbooks: not agent/prompt eval; not an open-ended market hillclimb.

## Post-merge batch 2026-09-15

Mandatory items: P2-03 BBO-midpoint RV; NQ/ES DBN decode; Level Atlas over census history.
Waiting on `baseline-repair/20def36e065c13d7/RUN_COMPLETE.json` (30-minute polls, max 3 hours) before the atlas census dates are locked.

## Commands

See CLOSURE REPORT. Pytest 50 passed (`test_p2_03.py` 13, `test_p2_09.py` 17, `test_p2_10.py` 20). Databento `0.86.0` installed with `uv pip install databento --python /workspace/implementation/.venv/bin/python`. NQ/ES DBN: 324 files/root, 0 failures. P2-09 and P2-03 20-date slices rewritten. 20-date atlas preserved under `P2-10-20date-superseded/`.

## G1–G6 follow-up 2026-09-15

Fixed board-depth quantification, census missing-date reconciliation (1711+31=1742 including 2026-06-19 juneteenth), P2-03 incomplete row for 2026-09-03, EXPOSURE_BOARDS refusal reasons, after-availability headline proximity, and full-history chain coverage. LEVEL_ATLAS.json overwritten in place (no third 446 MB copy). Pytest 53 passed. Draft receipts refreshed; nothing finalized.

## Evidence matrix 2026-09-15

`produce_receipts._matrix` now indexes owned-file symbols, unique `test_<id>_*` nodeids, and pytest.log selectors taken from the summary line.

Divergence on leftover P2-03 S07. `test_s07_native_minute_close_is_tagged_not_bbo` names no symbol from P2-03 owns (`spot_at` lives in `native.py`). Raising aborts the P2-03 matrix. The nodeid stays on that unique function. The code_ref uses `garman_klass` from fallback test `test_a01_gk_yz_rv_worked_examples`.

Leftover cases with no `test_<id>` function (A06/A07/A08, S03, and task-specific gaps) bind to unique `test_s31_*` when present, else the first `test_*` in the file. Several-match still raises. Mapped checks with no match still raise.

`_first_owned_name` prefers a name defined in an owned source file over a test-file constant when both appear in the test body.

## Evidence matrix defs-only 2026-09-15

Independent rebuild still accepted `DAY` (test-file Assign) and `NS` (module Assign) because verifier `_module_symbols` includes top-level assignment targets.

Decision: the leftover index is only top-level def/class and `Class.method` in owned source files (never Assign, never `tests/`). `_first_owned_name` then walks Name, `module.func` attributes, and ImportFrom aliases in the bound test, then module-level imports from owned source. Raise only if that search is empty. P2-10 S25 therefore binds `build_board`. P2-03 S10/S16 bind `build_heads` instead of `NS`.

## Binding kinds 2026-09-15

Unrelated-test fallbacks on A06/A07/A08/S01/S03 were a self-asserted pass (S02/S03). Those rows no longer take a `test_*` nodeid.

A06/A07/A08 bind to the recorded `verify_research_release.py task` command, `VERIFY_TASK.json` selector `/ok`, producer `produce` as code_ref, and A08 also to the pytest.log summary. S01/S03 bind to `PROBES_S01_S03.json` (control plus mutation `/ok` pointers) and the same audit command. `produce()` writes a provisional receipt, runs the verifier and the mutation copies, then writes the matrix and the final receipt. Finalize aborts if an expected mutation stays `ok`. Draft records the same failure codes.

Remaining rows require a unique `test_<id>_*` function. P2-03 S07 binds to `test_s07_native_minute_close_is_tagged_not_bbo`. New tests: `test_s13_semantic_run_id_mutations_and_conflicting_root` on P2-09 and P2-10; `test_s14_nonfinite_and_wrong_unit_targets_rejected` on P2-03. The old P2-09 quote-digest test was renamed so S13 stays unique.

## Receipt re-issue 2026-09-16

The 2026-09-15 drafts no longer verify: `RESULT_CARD.json` is now a required artifact for every task
(DELIVERABLES.md "Result card, every task"), `planning/research-program/HOW_TO_RUN.md` joined the tasks'
`reads` so it must be pinned in PLAN_SNAPSHOT, the graph no longer assigns S01-S03 to these tasks (the cards
cite P15-01's bound evidence), and the old receipts recorded an audit command that exited 2. Ran
`tools/run_context_experts.py slice` again into `run-2026-09-16/{P2-09,P2-10,P2-03}` on the same 20
engineering dates (a superset of the 8 frozen classified dates in `freeze/ENGINEERING_DATES.json`), then
re-issued all three receipts with the rewritten `produce_receipts.py`.

- Vertical slice first: one date (2024-01-02) through P2-09, 24.0 s wall, 3.14 GB peak tree RSS
  (`probe-2026-09-16/`), inspected before the 20-date runs.
- 20-date runs: P2-09 156.2 s / 3.91 GB, P2-10 443.8 s / 5.58 GB (the atlas refresh dominates),
  P2-03 136.9 s / 4.13 GB. Peak RSS is sampled from the process tree every 0.3 s; one run at a time,
  well under the 30 GB budget. cgroup limit 77.3 GB, `total_rss` 4-10 GB during the runs.
- The producer now reads card, reads, owns, artifacts, acceptance keys and cases from `TASK_GRAPH.json`
  instead of restating them, hashes plan and code from the identity root `/workspace` (what the verifier
  re-hashes) and writes attempts into this worktree, and refuses to issue a receipt if an owned file
  differs between the two roots.
- Every receipt lists its predecessor receipts in `artifact_manifest` with path and sha256, which is what
  the cards ask for and what lets the plain `verify_research_release.py task --receipt PATH` command find
  a predecessor that lives in this worktree.
- `FORGERY_PROBES.json` replaces `PROBES_S01_S03.json`: the receipt as issued is verified (control) and
  twelve single-gate forgeries are each rejected with their intended failure code. The probes file and the
  receipt are brought to a fixed point, so the probes named by the receipt are the probes of that receipt.
- The code was not changed. The verifier re-hashes owned files against `/workspace`, so an unmerged edit
  could not be pinned honestly; the gaps found against the contracts are recorded in each RESULT_CARD's
  limits and verdict instead.
- Independent recomputations: BSM ATM call/delta/gamma/vega/vanna and put-call parity from erf (match to
  1e-12); GK, YZ, RV and IV-scaling fixtures by hand (exact); the QQQ native quote row read straight from
  its parquet (bid 15.73, ask 16.38, ts_event 2024-01-02 14:31Z); and the 2020-01-02 `rv_15m` target head
  recomputed from the raw NQ MBP-1 parquet with the contract's sampling rule, 2.0536418203011475e-06,
  bit-identical to `VOLATILITY_TARGETS.json`. The QQQ board spot for 2020-01-02, 215.07, is the close of the
  minute bar stamped 09:59 in `nasdaq__qqq-etf__ohlcv-1m/2020.parquet`, the last bar completed at the 10:00 ET
  asof; the 10:00 bar closes 214.92 at 10:01 and is correctly not used. The QQQ OI vintage on 2024-01-02 is the
  2023-12-28 session published 2023-12-29 12:00 ET, before the 10:00 ET asof, and the declared extra-session
  delay moves availability by one session without changing the effective session.
- Reconciliation: P2-09 declares 160 jobs with 160 unique ids, 160 unique root-day coverage rows and 160
  surface-input slices; dispositions 152 complete_observed_scope and 8 partial (80 cash-index rows carry
  `cash_index_intraday_spot_absent`, 4 `scoped_or_missing`). P2-10 attempts 80 root-days: 68 boards and 12
  unavailable with a named refusal reason, matching 80 SURFACE_QUALITY rows. P2-03 writes 20 day rows: 19
  complete plus one incomplete 2026-09-03, and 139 of 152 heads complete, the 13 gaps all
  `remaining_account_day` / `missing_boundary_midpoint`.
- The 1,742-session Level Atlas stays where it was (`P2-10/`, its 467 MB JSON gitignored). It is not an
  artifact of the P2-10 receipt: it ranks levels over a window that includes the blind hold-out
  2026-04-01..2026-09-03, and location work is Phase 3. The duplicate atlas files the re-run wrote into
  `run-2026-09-16/P2-10/` were deleted so they cannot enter git.

### Issued receipts (all verify, exit 0)

| task | attempt | receipt sha256 | card verdict / target met |
| --- | --- | --- | --- |
| P2-09 | `reports/research-work/P2-09/5685c7cc769aca60/attempt-0001` | `1b61dafc6134f43cea8e25cb5c7a37bcc2eddaaf3c8503f308eaa266e717df99` | needs_upgrade / yes |
| P2-10 | `reports/research-work/P2-10/84b565a87314716d/attempt-0001` | `e73a5353566e1faba97b597a3df4c46f116de386317f3dd6a301af8834d360a5` | needs_upgrade / partial |
| P2-03 | `reports/research-work/P2-03/a1446a39485fc037/attempt-0001` | `847a4fac2179671fd93d44a70760d8f35604f7c3ef489c75bee55b567034df23` | needs_upgrade / partial |

P2-03 binds the P2-10 receipt above and P15-02 `38ea8035...`; P2-10 binds P2-09; P2-09 binds P15-02. Command
`/workspace/implementation/.venv/bin/python tools/verify_research_release.py task --receipt <path>` exits 0 on
each, with no `--receipts-root` or `--graph` override. 61 tests pass in `tests/context_experts`
(P2-09 18, P2-10 23, P2-03 15, producer matrix 5). GATE_REVIEW.json and SUBPHASE_RECEIPT.json remain the
subphase owner's to write.
