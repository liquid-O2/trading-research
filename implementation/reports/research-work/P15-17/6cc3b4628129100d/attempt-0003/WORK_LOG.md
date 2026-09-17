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
  SPEC.md, copied into `snapshots/plan/`), CODE_SNAPSHOT (the runtime modules, the three owned test
  files and the drift set tabulated below, copied into `snapshots/code/`), DRAFT_MANIFEST, EVIDENCE_MATRIX (A01-A10 plus the assigned
  cases S06, S07, S11, S12, S13, S15, S22, S24, S32, each bound to a test node id, a command index and
  hashed evidence), DECISIONS.tsv, REPORT.md and RESULT_CARD.json.
- Predecessors pinned, rebound on 2026-09-17 to the receipts the subphase gates actually closed on
  (wiki/current-status.md): P15-09 `250e5aea146f3516`, P15-10 `b89cbd7b0f4473cc`, P15-11
  `9e7fda7b291cce99`, P15-12 `f33f750e365a04c1`, P15-13 `8de8e78a21b0838a`, P15-14 `f01de253cf514105`,
  P15-15 `ced9a15cf6c6dae2`, P15-16 `cf6bf4778e53a0b0` and **P15-16A** `a931349e71b6ee2f` (sha256
  86174e0540b4abd9...). The earlier binding used preserved first-round attempts of P15-09, P15-10,
  P15-11, P15-13, P15-14 and P15-15; their PLAN_SNAPSHOTs pin wiki method pages at digests the
  amendment chain does not start from, so the chain could not excuse the later edits to those pages.
  The 04 gate receipts pin exactly the `sha256_before` the 2026-09-15 amendments carry forward.
- 2026-09-17: the branch is merged, so every declared file is hashed from /workspace. The four
  native-slice tests failed on main because `native-slice/jobs/` is gitignored (.gitignore:124) and
  the merge could not carry it; the 800 job documents were copied from the merged worktree into this
  attempt's run root, which restores the fixture the tests read. `SHARD_INVENTORY.json` still pins
  their per-date sha256, so the copy is checkable. The three recorded pytest commands were then re-run
  against the live tree: 111, 117 and 72 passed, exit 0 each, and the logs in the attempt directories
  are those runs.
- `tools/verify_research_release.py task` exits 0 for this receipt on 2026-09-17, after the
  coordinator's integration patch to `contracts/receipts.py` (amendment chain exempt from the plan
  hash comparison, a required artifact matched by a path component, and an added file under an owned
  path cleared by a verified successor that pins it at the live digest).
## Code drift superseded by this attempt

The stage A and fast-engine rounds changed files that closed tasks had pinned, and P15-16A's
owned `source_adapters/` directory gained `enumeration.py` after its receipt closed. The verifier
clears a stale pin, or an unpinned owned file, only when a later verified receipt that lists that
task as a predecessor pins the same path at the live digest, so attempt-0003's CODE_SNAPSHOT
carries the whole set. Both halves were computed mechanically (drift.py and pinset.py over every
receipt under reports/research-work, plus an import and open trace of the runner entry), never
from memory.

Executed by this attempt (imported or opened by the run or by its own verification pass):

| file | live digest | closed task whose pin it supersedes |
| --- | --- | --- |
| `src/trading_research/research/contracts/evaluation.py` | `880e41cdbbb975f4` | P15-03, P15-04 |
| `src/trading_research/research/contracts/execution.py` | `a3ecbfae92dd40a0` | P15-03 |
| `src/trading_research/research/contracts/identity.py` | `da3cb30399536f8f` | P15-00, P15-01, P15-02, P15-03 |
| `src/trading_research/research/contracts/outcomes.py` | `6c4a2aac7c624170` | P15-03 |
| `src/trading_research/research/contracts/receipts.py` | `859efe869728a0dc` | P15-01, P15-16A |
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
| `tools/verify_research_release.py` | `e4e8c4efe83cf985` | P15-01 |

Pinned for identity only, on the coordinator's 2026-09-17 integration patch, so that P15-01,
P15-02, P15-03, P15-05, P15-09 to P15-16 and P15-16A resolve at the live digests. This attempt
did not execute these files; the pin declares the bytes, not that the run used them. Two further
files of P15-16A's owned `source_adapters/` package, `__init__.py` and `confirmation.py`, are pinned
as well so the whole directory is declared; neither has drifted, so neither appears below:

| file | live digest | closed task whose pin it supersedes |
| --- | --- | --- |
| `src/trading_research/research/rule_discovery/baseline_manifest.py` | `aeab5b67affd961e` | P15-00, P15-02 |
| `src/trading_research/research/rule_discovery/families/green_failure.json` | `de3a409576450429` | P15-10, P15-16A |
| `src/trading_research/research/rule_discovery/families/green_vwap_scalp.json` | `19285ddbe75aa7f3` | P15-11, P15-16A |
| `src/trading_research/research/rule_discovery/families/jumbo.json` | `6dbcfcf1482990c1` | P15-09, P15-16A |
| `src/trading_research/research/rule_discovery/families/keani.json` | `a2a55677a7c5c44c` | P15-15, P15-16A |
| `src/trading_research/research/rule_discovery/families/member.json` | `5c31a6eb7941ed1b` | P15-14, P15-16A |
| `src/trading_research/research/rule_discovery/families/processes.json` | `739053dada3382dd` | P15-16, P15-16A |
| `src/trading_research/research/rule_discovery/families/saint.json` | `b5c37ecf25a21665` | P15-13, P15-16A |
| `src/trading_research/research/rule_discovery/families/sires.json` | `23d55fae9fec481b` | P15-12, P15-16A |
| `src/trading_research/research/rule_discovery/sequences.py` | `7b40ce15fb4573ca` | P15-07 |
| `tests/contracts/test_receipt_memos.py` | `730e52aee5cf0cd3` | P15-16A |
| `tests/rule_discovery/test_p15_01.py` | `c0308999a81f1b21` | P15-01 |
| `tests/rule_discovery/test_p15_02.py` | `696a924f2b7f6ab4` | P15-02 |
| `tests/rule_discovery/test_p15_03.py` | `ecd1706ed13d6213` | P15-03 |
| `tests/rule_discovery/test_p15_09.py` | `1f9ce359a8b94e53` | P15-09 |
| `tests/rule_discovery/test_p15_10.py` | `c3607106df86f5c5` | P15-10 |
| `tests/rule_discovery/test_p15_12.py` | `025ce5501d8b6042` | P15-12 |
| `tests/rule_discovery/test_p15_13.py` | `d0d4c3dd4ea588ce` | P15-13 |
| `tests/rule_discovery/test_p15_14.py` | `daa353afb7534041` | P15-14 |
| `tests/rule_discovery/test_p15_15.py` | `1227338095bec482` | P15-15 |
| `tests/rule_discovery/test_p15_16.py` | `4d053e9908a7b8a4` | P15-16 |
| `tests/rule_discovery/test_p15_16a.py` | `92542de11a7c35de` | P15-16A |
| `tools/produce_p15_16a.py` | `fe82bd8cab7bebf6` | P15-16A |
| `tools/replay_author_examples.py` | `314bce0bef8418e9` | P15-16A |
| `src/trading_research/research/rule_discovery/source_adapters/enumeration.py` | `598dd33475bb69da` | P15-16A (added under P15-16A's owned directory after its receipt closed) |

Still stale for their owners, and deliberately not pinned here: `src/trading_research/research/experts/labels/volatility.py` (P2-03), `src/trading_research/research/experts/options/atlas.py` (P2-10), `src/trading_research/research/experts/options/boards.py` (P2-10), `src/trading_research/research/experts/options/instruments.py` (P2-09, P2-10), `src/trading_research/research/experts/options/native.py` (P2-09, P2-10), `src/trading_research/research/experts/options/pricing.py` (P2-10), `src/trading_research/research/experts/options/slice_runner.py` (P2-03, P2-09, P2-10), `src/trading_research/research/rule_discovery/candidate_bank_v1.json` (P15-08), `src/trading_research/research/rule_discovery/cohorts.py` (P15-06), `src/trading_research/research/rule_discovery/delta.py` (P15-06), `tests/context_experts/test_p2_03.py` (P2-03), `tests/context_experts/test_p2_09.py` (P2-09), `tests/context_experts/test_p2_10.py` (P2-10), `tests/rule_discovery/test_p15_06.py` (P15-06), `tests/rule_discovery/test_p15_07.py` (P15-07), `tests/rule_discovery/test_p15_08.py` (P15-08), `tools/run_context_experts.py` (P2-03, P2-09, P2-10). Those tasks are outside the chain this patch covers.
