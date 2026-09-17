# P15-17 stage B — attempt-0003 (definitive). One line per decision.

**Definitive breadth screen.** Produced by the orchestrator on the merged code (P15-16A integration
round 3) with both B0.2 roots, the supplemental `823273eba4b9ec50` first and the main
`1019e6c09ee54609` second, at 17 workers. `RUN_META.json` carries one code identity
(`2758b5f8946073de`, no supersessions) and `p15_16a_receipt: PENDING` for the orchestrator to fill.
The rehearsal and parity oracle is `attempt-0002`; stage A `47dedaaa4f5b9ce1` remains the frozen input.

- Run: 1,742 declared dates, 1,741 with 160 job documents and a daily record; `2020-06-30` keeps its
  genuine `no native account-day view` failure record. `RUN_COMPLETE.json` closes the run through the
  retained-failure path: 278,720 declared = 278,560 written + 160 absent on that date, reconciled, with
  `SHARD_INVENTORY.json` carrying the file-level hashes of the gitignored daily and checkpoint shards.
- Terminal dispositions over the 278,560 rows: 256,720 evaluated, 20,880 unsupported, 800
  `input_unavailable` (20 holiday sessions x the 40 SIRES and REFILL-STUDY candidates whose families read
  the native view -- a missing input, recorded at the source by the runner in this run, not a software
  failure), 160 `session_unavailable` (2020-01-01, a closed RTH holiday).
- Blind hold-out (EVALUATION.md amendment 2026-09-16): 112 dates of 2026-04-01..2026-09-03 are trimmed
  out of the 2026 outer test window before anything is scored. They enter no inner tuning, no Holm
  family, no gate and no table here; `BREADTH_RESULTS.json.holdout_excluded` and every ledger row record
  the exclusion. Their job documents stay on disk for the release replay (`search_run.holdout_replay`).
- Evaluation: streaming, 69.7 s, peak RSS 0.285 GB. 800 ledger rows = 160 candidates x 5 folds.
- Result: no candidate clears the promotion gates. 91 inconclusive_support, 38 retained_baseline,
  19 rejected_by_evidence. The baseline is retained in every family; 45 bank selections across the five
  folds go forward to refinement (10, 10, 9, 8, 8).
- The bootstrap now draws block starts inside each calendar-year segment, as EVALUATION.md requires, and
  reports block lengths 1 and 10 beside the frozen block 5 as sensitivity.
- Self-check (`SELF_CHECK.txt`, `self_check.py`): the top candidate's mean paired improvement 25.779936
  over 1,094 hold-out-free test days and 5 blocks recomputes exactly (delta 0); an independent
  implementation of the selection rule reproduces fold 2022's SIRES picks; the native trace reaches the
  P15-16A job bytes with its sha256 recomputed; declared jobs reconcile to unique artifacts and terminal
  dispositions.
- `RESULT_CARD.json` (and REPORT.md's last section): verdict `not_reaching_target`, met `no`.

## Profile supplement (attempt-0004), merged evaluation

- The 2026-09-16 supplement is declared in `../attempt-0004/CANDIDATE_BANK_SUPPLEMENT.json` and hashed
  into that attempt's `RUN_META.bank` *before* the run starts (`declared_at` 2026-09-16T21:10:28Z, the
  first checkpoint later): 20 one-axis candidates, P3 value area .68 and P4 value area .40, on exactly
  the ten branches that carry P1/P2.
- Four are recorded `duplicate` and not run: SAINT-AMT's B0.2 track builds its value area with
  `fraction=".68"`, so P3 on continuation_retest, failed_auction_return, poc_traversal and
  trapped_buyers_retest would be the baseline under another name. Every other family reaches
  `historical_features.profile` at .70, so P3 and P4 are genuine one-axis changes there.
- `search.py` threads the recipe's `fraction` (Decimal) into `profile_value_area`; the stage records
  `profile_fraction` in its operands, so a supplement whose parameter never arrived is visible.
- attempt-0004: 16 candidates x 1,742 dates at 6 workers, 2,256 s, one retained failure (2020-06-30),
  same B0.2 roots, same folds, same hold-out exclusion as attempt-0003.
- Merged evaluation (`evaluate_run(..., extra_run_roots=[attempt-0004])`): one ledger of 880 rows
  (160 x 5 + 16 x 5), one BREADTH_RESULTS, one allowlist, and **one Holm family of 164 decided
  candidates** -- 148 supported breadth candidates plus the 16 executed supplement candidates. The 12
  unsupported breadth cells and the 4 duplicate supplement cells keep their rows but enter no test, so
  the family is 164 of the 180 declared. The 800 earlier trials' p-values are re-adjusted under this
  larger family; the file now in place is the merged one.
- Result unchanged in kind: no candidate clears the gates. 101 inconclusive_support, 44
  retained_baseline, 19 rejected_by_evidence. The best supplement candidate is
  `KEANI-OPEN-ABOVE-VALUE:source_long:P4` at +0.0397 net points per common complete day,
  inconclusive_support.
- For the release's breakdown edition: `search_run.paired_series_rows(run_root)` streams, per candidate
  and per day, the date, both sides' daily net points and the decision clock of every opportunity, so the
  release can cut by year, session bucket or day of week without re-running the search.

## Receipt and verification

- `TASK_RECEIPT.json` (disposition `retained_baseline`) with PLAN_SNAPSHOT (17 live planning files plus
  SPEC.md, copied into `snapshots/plan/`), CODE_SNAPSHOT (the runtime modules and the three owned test
  files, copied into `snapshots/code/`), DRAFT_MANIFEST, EVIDENCE_MATRIX (A01-A10 plus the assigned
  cases S06, S07, S11, S12, S13, S15, S22, S24, S32, each bound to a test node id, a command index and
  hashed evidence), DECISIONS.tsv, REPORT.md and RESULT_CARD.json.
- Predecessors pinned: P15-09 through P15-16 and **P15-16A** (`fb725d77e6834c3f/attempt-0001`, sha256
  9230f8ab1dadf583..., disposition implemented_verified) -- the receipt that was pending through the
  rehearsal now exists and is bound here.
- `tools/verify_research_release.py task` exits 2. Every residual failure is one of three classes, none
  of them a defect in this attempt's evidence: (a) the declared code files of this branch are not on
  main yet, so their bytes, symbols and test node ids cannot resolve under /workspace; (b) the
  recursive check of P15-09..P15-16A reports identity drift inside those receipts, which this task does
  not own; (c) the required artifact name `FAMILY_REPORTS/` cannot match, because the verifier keys the
  manifest by `Path(path).name`, which never carries a trailing slash. (c) is a one-line fix in either
  TASK_GRAPH (drop the slash) or receipts.py (`rstrip("/")` when comparing); both files are outside this
  task's ownership.

## Code drift superseded by this attempt

The stage A and fast-engine rounds changed files that closed tasks had pinned. The verifier clears a stale pin only when a later verified receipt pins the same path at the live digest and lists that task as a predecessor, so attempt-0003's CODE_SNAPSHOT now pins every drifted path this run executed. The set was computed mechanically (drift.py over every receipt under reports/research-work, then an import and open trace of the runner entry), never from memory.

| file | live digest | closed task whose pin it supersedes |
| --- | --- | --- |
| `src/trading_research/research/contracts/evaluation.py` | `880e41cdbbb975f4` | P15-03, P15-04 |
| `src/trading_research/research/contracts/execution.py` | `a3ecbfae92dd40a0` | P15-03 |
| `src/trading_research/research/contracts/identity.py` | `da3cb30399536f8f` | P15-00, P15-01, P15-02, P15-03 |
| `src/trading_research/research/contracts/outcomes.py` | `6c4a2aac7c624170` | P15-03 |
| `src/trading_research/research/method_pack/historical_features.py` | `0fea65612affd342` | P15-06 |
| `src/trading_research/research/rule_discovery/baseline.py` | `828a4b49d800b0e5` | P15-02 |
| `src/trading_research/research/rule_discovery/engine_slice.py` | `fa066745cdc13f3d` | P15-05, P15-06, P15-07, P15-08 |
| `src/trading_research/research/rule_discovery/formations.py` | `13d8c38e30d23284` | P15-05, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16 |
| `src/trading_research/research/rule_discovery/kernels.py` | `32667f9aeda3ca26` | P15-16A |
| `src/trading_research/research/rule_discovery/native.py` | `a5dc6e3cc4b2e850` | P15-02, P15-04, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A |
| `src/trading_research/research/rule_discovery/profiles.py` | `055cf22d0f59ff40` | P15-05 |
| `src/trading_research/research/rule_discovery/registry.py` | `f9a4ea72e387c8d4` | P15-08 |
| `src/trading_research/research/rule_discovery/run_adapter_populations.py` | `07d890b1cf654504` | P15-16A |
| `src/trading_research/research/rule_discovery/runner.py` | `84718a616a7b5e58` | P15-02, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A |
| `src/trading_research/research/rule_discovery/source_adapters/b02_saint_track.py` | `556a06dee0152557` | P15-16A |
| `src/trading_research/research/rule_discovery/source_adapters/common.py` | `c9bf81473f7d7e1e` | P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A |
| `src/trading_research/research/rule_discovery/source_adapters/green_b02.py` | `06810196af8df2c4` | P15-16A |
| `src/trading_research/research/rule_discovery/source_adapters/green_failure.py` | `876fa272a1c0ce8e` | P15-10, P15-16A |
| `src/trading_research/research/rule_discovery/source_adapters/green_vwap_scalp.py` | `22cb77bf7f57a687` | P15-11, P15-16A |
| `src/trading_research/research/rule_discovery/source_adapters/jumbo.py` | `eac7cd5f49979471` | P15-09, P15-16A |
| `src/trading_research/research/rule_discovery/source_adapters/keani.py` | `cbf3d13d1e3ef07e` | P15-15, P15-16A |
| `src/trading_research/research/rule_discovery/source_adapters/member.py` | `43f89b8b916b31ba` | P15-14, P15-16A |
| `src/trading_research/research/rule_discovery/source_adapters/processes.py` | `c0e8e1761caeec98` | P15-16 |
| `src/trading_research/research/rule_discovery/source_adapters/refill_b02.py` | `ce3b57fae514f132` | P15-16A |
| `src/trading_research/research/rule_discovery/source_adapters/saint.py` | `44eabc51c02a0bc3` | P15-13, P15-16A |
| `src/trading_research/research/rule_discovery/source_adapters/sires.py` | `9c13a4ce68cd4c08` | P15-12 |
| `src/trading_research/research/rule_discovery/source_adapters/sires_b02.py` | `222c7a87e3ef5fbf` | P15-16A |
| `src/trading_research/research/contracts/receipts.py` | `c17758c964678ec0` | P15-01, P15-16A (executed by this attempt's own verification pass, not by the search run) |
| `tools/verify_research_release.py` | `e4e8c4efe83cf985` | P15-01 (executed by this attempt's own verification pass, not by the search run) |

Not pinned here, and therefore still stale for their owners: every drifted path this run did not execute -- the Phase 2 expert modules and tools (P2-03, P2-09, P2-10), the other tasks' own test files, and `tools/produce_p15_16a.py` and `tools/replay_author_examples.py` (P15-16A). Declaring bytes this attempt never ran would be a false identity.
