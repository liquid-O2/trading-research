# Empirical completion report

Completed the authorized empirical extension on `codex/phase1-calibration-discovery-v1`. All 165 frozen jobs and 2,274 rule/partition assignments were scanned and replayed. No evaluation work remains in this frozen scope. The measurement report correctly retains `data_hole`; completion of the scan does not imply complete market coverage or complete source definitions.

## Results and denominators

The run produced 2,452 research-comparison opportunity records: 1,000 pass, 1,412 fail and 40 unknown, so observed `n=2,412` and `N=2,452`. The unknowns comprise 30 censored and 10 ambiguous records. These are additive audit counts across separate branch populations, not a pooled success rate or distinct trades. Passing comparison endpoints produce 1,000 nested comparison signals; actual discretionary selections, attempts, orders and fills remain null.

family | p | f | u | n | N | scope status
--- | ---: | ---: | ---: | ---: | ---: | ---
GB-FAIL | 744 | 1131 | 8 | 1875 | 1883 | data_hole
GB-SCALP | null | null | null | null | null | unavailable_definition
GB-VWAP | 36 | 12 | 8 | 48 | 56 | data_hole
JETBUNDLE-STATES | null | null | null | null | null | unavailable_definition
JJ-TBR | 141 | 150 | 10 | 291 | 301 | data_hole
KEANI-OPEN-ABOVE-VALUE | 0 | 0 | 4 | 0 | 4 | measured
MEMBER-TWO-REASONS | null | null | null | null | null | unavailable_definition
REFILL-STUDY | 0 | 0 | 0 | 0 | 0 | data_hole
SAINT-AMT | 31 | 75 | 0 | 106 | 106 | data_hole
SIRES | 48 | 44 | 10 | 92 | 102 | data_hole
STOIC-DATA | null | null | null | null | null | unavailable_definition
STOIC-RISK | null | null | null | null | null | unavailable_definition

[Full branch/year/contract results](RESULTS.md) retain 790 compatible groups, observed counts, coverage, censored/ambiguous results and group-specific denominator intervals. Incomplete-population rates remain null; conditional observed rates are labelled separately. Family and rule rates are not pooled. [Both required PHASE and audit tables](PHASE_AND_AUDIT_TABLES.md) follow the family results and include all 50 branches plus 8 distinct observation units.

## Scope completed

| scope | declared | scanned | remaining |
| --- | ---: | ---: | ---: |
| NQ monthly native-bar sessions, 2010–2026 |161|161|0|
| NQ annual standalone-trade sessions, 2021/2022/2023/2026 |4|4|0|
| Rule/partition assignments |2274|2274|0|

The coverage-selected sample uses the first eligible monthly bar session and first eligible annual standalone-trade session, with frozen 62-day lookbacks. It is a sample, not an exhaustive census of acquired data. Source/calibration dates and detected prior-inspection dates were excluded before evaluation. Prior exposure is not fully knowable, and both reporting revisions explicitly record evaluation exposure; no untouched-sample claim is made.

Of 2,274 rule/partition assignments, 1,535 completed, 6 completed with population holes and 733 retained missing-data dispositions. 157 of 165 date jobs contain at least one missing rule input; this does not erase their other observed opportunities. All four opening clocks are observed, but their opening-above-value classifications remain unknown because required prior profiles are unverified. M09 has one legitimate completed zero-zone search in 2023 and three searches with unverified tape coverage; its overall missing population is not reported as a completed zero. The three tape-dependent Saint routes retain precise missing-profile, reference or delta dispositions. [Coverage inventory and splits](coverage/README.md) and [partition checkpoints](RUN_MANIFEST.json) identify exact inputs and scope.

## Calibration and source limits

[Calibration](calibration/CALIBRATION_REPORT.md) accounts for all 22 retained cases, 17 configurations and 50 catalog branches. It reuses accepted reviews, records 20 source-image reinspection cases, and keeps losses, early attempts and non-entry cases. The July 23 Sires caption/attempt conflict remains explicit; Green Bird's November 20 sweep and later MSS annotation remain separate; MNQ displays are not promoted to NQ fills. Source-specific settings, interval-valued decision clocks and missing private calculations are preserved.

The frozen registry contains 19 executable comparison definitions, 31 unavailable/source-case/supplied/non-entry branch dispositions, and 8 separate management, re-entry, state, process and risk observation units. No missing state classifier or private order ledger is manufactured. [Readable rules](registry/CANDIDATE_RULES.md) and the [validated registry](registry/CANDIDATE_REGISTRY.json) state assumptions, availability, first-opportunity populations, lifecycle, expiry, deduplication and missing handling.

Every complete source-method verdict remains unknown; faithful disagreements therefore remain null. The reported comparison outcomes do not establish source-faithful entries, discretionary choices, fills, causal trading efficacy or profitability. Data limits include incomplete earlier overnight/reference windows, same-contract prior-session coverage, unavailable MNQ input, and native trade/profile or minute reconciliation gaps. The registry retains the exact missing observation or unresolved definition for each unsupported branch.

## Verification and review

The current integrated suite passed 736 tests in 127.90 seconds. The preserved baseline was 639 tests and 2 subtests. Current baseline rechecks also passed six original cases, six post-repair checks, 27 independent audit cases and five paired-quantity probes. [Tested identity](validation/TESTED_IDENTITY.json) binds the current source, test and CLI hashes; earlier acceptance artifacts remain baseline history.

Native calibration exercised all 19 supported definitions and 24 comparison opportunities on the excluded February 24 source/control date. The actual version 1.0.2 bar/tape pilot report passed before scale-up and reproduced archived selector/replay outputs. Every completed job's artifact, native input identity, typed opportunity/replay clocks, exact rule membership and source boundary were checked. Independent review reconstructed all 2,309 retained bar endpoints exactly from native minute OHLCV. Timing violations and proxy-as-faithful admissions are both zero. All 165 jobs were then resumed and hash-verified without adding any record.

All 50 charts selected by the frozen first-rule/outcome and first-observed-year policy were visually inspected and bound to the exact scored records. [Chart index and review](charts/README.md) retain the PNGs and review ledger. They are minute-context plots; dynamic VWAP, TDO, aggregate-candle and flow details remain in the records rather than every predicate being overlaid. The independent reviewer additionally inspected six exact images.

[Independent final review](validation/FINAL_EMPIRICAL_REVIEW.md) passed source, causality, counting and chart gates. [Final verification](validation/FINAL_VERIFICATION.json) reconciles raw, group, rule and family counts and checks current identities and all chart bindings. Two reporting integration defects were repaired and retained with regression coverage: suppression of observed counts under missing scope, and rejection of versioned artifact paths. The exposed runs remain in `revisions/run-v1/` and `revisions/run-v1.0.1/`; all 165 jobs were recomputed for version 1.0.2. Selectors, assumptions, native inputs and cohort membership were unchanged by those revisions.

## Identities and reproduction

- Registry version 1.0.0: `7ce33ad43587e44168f2b5cbb910386c33f90cc5f8a1a5c6f2d90709791df381`.
- Run version 1.0.2: `d80935d548abe3cafcd695ec842dc69b1d3391646c2da8fe0db9e935a6c37247`.
- Tested implementation: `8c3097892f5851d84c9c0d5decb09d3026755840ac1acec9d56b3ed89be8556f`.
- [Commands](COMMANDS.md) include calibration, frozen validation, bounded run/resume, reporting, chart generation and final acceptance checks.
- [Empirical acceptance](EMPIRICAL_ACCEPTANCE.json) is separately scoped from the prior method-pack acceptance.

Raw `/workspace/data` remains on disk, ignored and uncommitted. Protected source/archive/old-plan content and the baseline acceptance were preserved. Large derived artifacts are ignored; small manifests, checkpoints, tests and reports are reviewable. No push or merge was performed. Repeating the documented `run --workers 4` command verifies and resumes the completed frozen run; it has zero remaining jobs.
