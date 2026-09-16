# Results ledger

One card per task: the question it answered, the headline numbers, whether it met its target, a verdict, and the smallest lever if it needs an upgrade. Cards for tasks closed before 2026-09-16 were written by the orchestrator from their receipts; open tasks write their own `RESULT_CARD.json` (see DELIVERABLES.md). Verdicts: **done well**, **needs upgrade**, **not reaching target**, **not applicable**. This page is where upgrades are decided in small parts; the phase releases roll it up.

## Phase 1

| Task | Question | Headline | Target met | Verdict | Lever |
| --- | --- | --- | --- | --- | --- |
| Census run-1.0.1 | How often do the source setups occur on our data, measured faithfully? | 1,742 sessions searched; 18,747 observed setups over 50 branches (JJ-TBR 3,912; GB-FAIL 7,589; GB-VWAP 499; GB-SCALP 3,066; SIRES 2,538; SAINT-AMT 785; MEMBER 352; KEANI 6); 773 tests, 341 charts inspected | yes, for the acquired observed-input population; input-limited populations explicitly unmeasured | done well, with limits | KEANI (6 setups) and SAINT are input-limited; the B0.2 baseline of Phase 1.5 re-measures them source-faithfully |

## Phase 1.5

| Task | Question | Headline | Target met | Verdict | Lever |
| --- | --- | --- | --- | --- | --- |
| P15-00 | Is the Phase 1 baseline bound to one frozen identity with typed records? | 50 branches and 8 units reconciled; 7 engineering-date slots per input group; canonical hashes order-independent (receipt ea9693217cb577cb) | yes | done well | none |
| P15-01 | Does the verifier reject forged, missing or incomplete evidence? | Independent suite 27/27 and 14-probe suite 14/14 after two hardening rounds; verification time cut from hours to under a minute by the round-2 index and memos (receipt a4c95ab43aef1038) | yes | done well | keep the memo keys tied to graph identity as the graph changes |
| P15-02 | Does the native MarketView reproduce the frozen scanners byte for byte? | Byte parity 3,420/3,420 on the stratified sample; B0.1 coverage seams labelled (receipt c9669fa98ba72c43) | yes | done well | feed completeness stays unknown; it is a data limit, not a code lever |
| P15-03 | Are outcomes, the costed replay and the folds defined causally? | Ordered first-passage labels with ambiguity states; $25 net-P&L fixture; folds 2022 to 2026 with purge and embargo (receipt b957ec04d76e9c71) | yes | needs upgrade | the block bootstrap must draw within calendar-year segments as the contract says; fix under way 2026-09-16 |
| P15-04 | Is every numerical operand traced to its source? | 48 ledger rows; printed formulas recovered where stated; B0-only Strategy Book with frozen regime dimensions (receipt 0d0a57cc4de997b4) | yes | done well, with limits | one VIX formula discrepancy (L001) and 6–9 deviations recorded only; turn on the author's text if it appears |
| P15-05 | Are formations F1–F3 and profiles causal and exact? | Fixtures pass; value-area sparse-row walk confirmed as a frozen-pack defect, contiguous bins used (receipt 8e1ea422bfc8678d) | yes | done well | none |
| P15-06 | Are the CVD variants and cohort memory causal with unknown volume kept separate? | +10/−4/unknown 6 fixture; half-life decay; unresolved cohorts never leak (receipt 50d64d506299dc8d) | yes | done well | none |
| P15-07 | Do the response state machines S1–S4 order stages causally? | Retest-before-reclaim rejected; missing aggression cannot qualify S3/S4 (receipt ac09070f5aeb604b) | yes | done well | none |
| P15-08 | Is the candidate bank finite and pre-declared? | 160 non-baseline candidates, 50 baselines, 840 deferred; byte-identical expansion before outcome access (receipt 9728f9ee0bbbdfd5) | yes | done well | none |
| P15-09 to P15-16 | Does each family adapter reproduce its source predicate and report unknowns? | Slice-verified adapters; per-candidate p90 7.6 to 20.4 s before the fast engine; SAINT left its B0.1 unknown state; Keani C4 rejection implemented | yes for the slice | needs upgrade | the population-level plausibility gate (added in P15-16A) is what caught unmeasured stages; keep it in front of every population run |
| P15-16A | Is B0.2 the source's own rule, measured on the whole population? | 41 branches over 1,742 sessions; 37 in bound; 4 out of bound with diagnoses (GB golden_pocket, SIRES ofm_aggressive and balance_failure_fade under the unobservable gamma regime, REFILL touch_record); author examples 7 of 8 late-2026 reach location | partial | needs upgrade | gamma regime for the two SIRES branches turns on the Phase 2 options boards; the full-session weekly candle for prior_week_level |
| P15-17 | Which mechanism changes beat B0.2 under the gates? | Rehearsal on attempt-0002: no candidate promoted; 89 inconclusive on support, 38 baseline retained, 21 rejected; definitive run in progress | pending | pending | pending the definitive run with the hold-out excluded |
| P15-18 | Does refinement inside each fold's past improve the selected banks? | Rehearsal: 190 proposals, 46 executed, three clear the gates (not a finding until the definitive run) | pending | pending | pending |
| P15-19 | Which exit policy holds up on frozen entries? | rehearsal in progress | pending | pending | pending |
| P15-20 | Is the release complete and honest? | machinery built; rehearsal release in 4 s with census reconciled | pending | pending | pending |

## Phase 2

Cards appear as each task closes.
