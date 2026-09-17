# P15-17 attempt-0005 — the amended evaluation of the attempt-0003/0004 runs

Evaluation-only attempt, 2026-09-17. No candidate was re-run: attempt-0003 (the
breadth population, 1,742 declared sessions x 160 candidates) and attempt-0004 (the
16 executed profile-supplement candidates) are read as they stand, and every
document this attempt binds from them is pinned by sha256 in `RUN_BINDING.json`.

## Why this attempt exists

The coordinator found two defects in attempt-0003's results, and EVALUATION.md,
WORKFLOW.md and DELIVERABLES.md were amended on 2026-09-17:

- With 2,000 bootstrap draws the smallest attainable p-value is 1/2001 and the
  smallest attainable Holm-adjusted p-value for a family of 164 is 164/2001 = .082.
  No candidate could ever pass the `p_holm <= .05` gate, whatever the data said, and
  thirteen candidates positive in all five folds were labelled `rejected_by_evidence`
  with reason `holm`. Draws are now 20,000, the attainable floor m/(B+1) is reported
  beside every adjusted p-value, and a candidate that fails only Holm is
  `inconclusive_multiplicity`, not rejected.
- The support gate now applies to **both** sides of a pair. A candidate whose own
  baseline is below the gate is `inconclusive_support`, with its own frequency, the
  ratio to the baseline's and its unpaired mean recorded.

## What changed in the code (this attempt's own files and the two contract files)

- `contracts/evaluation.py`: `BOOTSTRAP_DRAWS = 20000`; new
  `attainable_holm_floor(m, draws)` and `floor_admits_decision(m, draws, limit)`;
  the evaluation protocol document now publishes the smallest attainable p and the
  .025 floor limit.
- `rule_discovery/search_run.py`: the outer row carries
  `baseline_resolved_opportunities` and both unpaired means; `support_block()` and
  `fold_metrics_from_series()`; `_multiplicity_block()` published in
  `BREADTH_RESULTS.json` and `RUN_META.json`; the family report gained a
  **Multiplicity** table and a **Support on both sides of the pair** table; the
  ledger row carries the support counts, the attainable floor and its own fold
  metric beside the pooled decision metric.
- `rule_discovery/refinement.py`: `evaluate_promotion()` implements the two-sided
  support gate and the `inconclusive_multiplicity` disposition and reports the floor.
- `rule_discovery/exits.py`: the exit rows declare the baseline's resolved count
  explicitly (symmetric by construction) and carry the same support block.

## Result under the amended contract

164 candidates in one Holm family (148 supported frozen + 16 supplement), attainable
floor 0.0082 against the .025 limit, so the stage can decide.

| disposition | candidates |
| --- | --- |
| promoted | 2 |
| inconclusive_support | 108 |
| retained_baseline | 40 |
| rejected_by_evidence | 14 |
| inconclusive_multiplicity | 0 |

- `GB-FAIL:previous_hour:T4` (Timing): +5.5885 points/day, 95% CI [3.399, 7.877],
  p_raw 0.00005, p_holm 0.0082, 648 vs 374 resolved opportunities over 1,107 days
  and 5 blocks, all five blocks positive.
- `JJ-TBR:judas_reversal:S4` (Sequence): +3.4417 points/day, CI [2.400, 4.484],
  469 vs 388 opportunities. **Marked implausible** — see below.

Under the superseded 2,000 draws the same evidence produced zero promotions; the
thirteen all-positive candidates that were labelled `rejected_by_evidence/holm` are
no longer rejected on multiplicity.

## The S1 audit (AUDIT_S1.md) and what it found

`SIRES:absorption_reward_retest:S1` (+25.78 points/day) is an artefact, twice over:
its baseline resolved 19 opportunities against the candidate's 10,325 (ratio 543.4,
so the pair is now `inconclusive_support/baseline_support`), and every Sequence-bank
entry in the run is filled up to its own `deadline_s` **before** the stage that
admitted it (`confirmation_delay_s` in [-600, 0] on 100% of S1's entries; the same
signature scales with `cohort_s` and `pressure_s` on S3 and S4). 52 of the 160
frozen candidates are Sequence-bank. The per-year stability the coordinator asked
about is *not* the anomaly: 1.40 points of spread against a 1.22-point mean standard
error is exactly what 2,400 entries a year implies.

`JJ-TBR:judas_reversal:S4` is a Sequence-bank candidate with the same signature
(-60.0 s on every entry) and its fold means spread 5.81 points against a 1.47-point
mean standard error (3.9 sems), so it is recorded `implausible_pending_audit` in
`RESULT_CARD.json`, which forbids `done_well`. `GB-FAIL:previous_hour:T4` carries
neither signature (delays +180 to +300 s; fold spread 3.51 against 3.19, 1.1 sems).

## Evidence in this attempt

- `BREADTH_RESULTS.json`, `TRIALS.jsonl` (880 rows = 176 registered candidates x 5
  folds), `REFINEMENT_ALLOWLIST.json` (byte-identical to attempt-0003's: selection is
  inner-only and no amendment touched it), `FAMILY_REPORTS/` (9 families, both
  WORKFLOW tables plus the new multiplicity and two-sided support tables).
- `SELF_CHECK.txt` from `self_check.py`, run against this attempt's results and
  attempt-0003's shards: the top candidate's mean recomputed to 25.779936 with delta
  0, one native entry traced to the P15-16A job bytes, and 278,720 declared jobs
  reconciled to 278,560 written + 160 absent on the retained failure date.
- `native-slice/`: the five declared dates x 160 candidates re-run on 2026-09-17
  with the amended code, so the slice's code identity matches the modules that
  produced this evaluation.
- `AUDIT_S1.md`, `RUN_BINDING.json`.

## Limits

- Same-model self-review only.
- The blind hold-out (2026-04-01..2026-09-03, 112 account days) enters nothing here.
- The Sequence-bank ordering defect is reported, not fixed: fixing it changes the
  scan and needs a new population run, which this attempt was not authorised to do.

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
| `src/trading_research/research/contracts/evaluation.py` | `46c38d6489484a82` | P15-03, P15-04, P15-17, P15-18, P15-19 |
| `src/trading_research/research/contracts/execution.py` | `a3ecbfae92dd40a0` | P15-03 |
| `src/trading_research/research/contracts/identity.py` | `da3cb30399536f8f` | P15-00, P15-01, P15-02, P15-03 |
| `src/trading_research/research/contracts/outcomes.py` | `6c4a2aac7c624170` | P15-03 |
| `src/trading_research/research/contracts/receipts.py` | `29410b389ade6802` | P15-01, P15-16A, P15-17 |
| `src/trading_research/research/method_pack/historical_features.py` | `0fea65612affd342` | P15-06 |
| `src/trading_research/research/rule_discovery/baseline.py` | `828a4b49d800b0e5` | P15-02 |
| `src/trading_research/research/rule_discovery/engine_slice.py` | `fa066745cdc13f3d` | P15-05, P15-06, P15-07, P15-08 |
| `src/trading_research/research/rule_discovery/exits.py` | `4ff532e31974b1aa` | P15-17, P15-18, P15-19 |
| `src/trading_research/research/rule_discovery/formations.py` | `13d8c38e30d23284` | P15-05, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16 |
| `src/trading_research/research/rule_discovery/kernels.py` | `32667f9aeda3ca26` | P15-16A |
| `src/trading_research/research/rule_discovery/native.py` | `a5dc6e3cc4b2e850` | P15-02, P15-04, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A |
| `src/trading_research/research/rule_discovery/profiles.py` | `055cf22d0f59ff40` | P15-05 |
| `src/trading_research/research/rule_discovery/refinement.py` | `99134fbf895fb1b5` | P15-17, P15-18, P15-19 |
| `src/trading_research/research/rule_discovery/registry.py` | `f9a4ea72e387c8d4` | P15-08 |
| `src/trading_research/research/rule_discovery/run_adapter_populations.py` | `07d890b1cf654504` | P15-16A |
| `src/trading_research/research/rule_discovery/runner.py` | `84718a616a7b5e58` | P15-02, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A |
| `src/trading_research/research/rule_discovery/search_run.py` | `c99f355b31726037` | P15-17, P15-18, P15-19 |
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
| `tests/rule_discovery/test_p15_17.py` | `068cb4f64188ab65` | P15-17, P15-18, P15-19 |
| `tests/rule_discovery/test_p15_18.py` | `073f481df2152a95` | P15-17, P15-18, P15-19 |
| `tests/rule_discovery/test_p15_19.py` | `01f9f924493c2fd1` | P15-17, P15-18, P15-19 |
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
