# Phase 1 implementation and empirical status

As of 2026-09-12, the implementation and the declared empirical v1 sample are complete. Historical source fidelity and market coverage remain separate questions. Start with the [method index](index.md), then read the relevant method's frozen comparison definition and its missing evidence.

## What is complete

The [implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md), [obligation matrix](/workspace/implementation/validation/phase1-completion/obligation-matrix.json) and [post-implementation repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) cover 166 object contracts, 9 shared contracts, 12 method contracts and 373 operand bindings. Native and parent-derived producers, supplied-record admission, causal assembly and lifecycle checks exist. Each object page now links to its current contract and code. A supplied-only contract is implemented even when the actual proprietary or private record required to instantiate it is absent.

The [empirical completion report](/workspace/implementation/reports/phase1-live/empirical/COMPLETION_REPORT.md) accounts for all 165 selected date jobs and 2,274 rule/date assignments, with zero pending work in that frozen scope. It evaluates 19 explicit research-comparison definitions and records 31 other branch dispositions, covering all 50 catalog branches. Eight additional management, re-entry, state, process and risk observation units retain their own supplied-only denominators. [Readable rules](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md) distinguish assumptions from source statements.

The integrated empirical acceptance passed 736 tests, the retained baseline and repair probes, 27 independent audit cases, five quantity regressions and review of 50 selected charts. [Verification](/workspace/implementation/reports/phase1-live/empirical/validation/FINAL_VERIFICATION.json) and [independent review](/workspace/implementation/reports/phase1-live/empirical/validation/FINAL_EMPIRICAL_REVIEW.md) retain the precise tested identities and scope. The [wiki reconciliation record](/workspace/implementation/reports/phase1-live/wiki-reconciliation/README.md) documents the later documentation checks.

## What the historical run actually measured

The frozen sample selected the first eligible covered native NQ bar session in each retained month: 161 dates across 2010–2026. Four additional standalone-trade dates cover 2021, 2022, 2023 and 2026. Source/calibration dates and detected prior-inspection dates were excluded using the frozen selection rules; the 2024–2025 tape dates were already exposed. This is a coverage-selected sample, not every session in the acquired archive. Prior exposure is incompletely knowable, and reporting revisions record outcome exposure. [Coverage and splits](/workspace/implementation/reports/phase1-live/empirical/coverage/README.md) and the [run manifest](/workspace/implementation/reports/phase1-live/empirical/RUN_MANIFEST.json) identify the exact dates and inputs.

There are 2,452 recorded comparison opportunities: 1,000 pass, 1,412 fail and 40 unknown (`n = p + f = 2,412`; `N = p + f + u = 2,452`). The unknowns include 30 censored and 10 ambiguous records. Passing endpoints produce 1,000 nested comparison signals. These additive counts combine different branch populations; they are neither distinct trades nor a pooled success rate. Actual source selections, attempts, orders and fills remain unavailable. Every complete source-method verdict remains unknown, and faithful disagreements remain null. [Results by branch, year and native contract](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) retain the compatible denominators and labelled observed rates.

The [PHASE and audit tables](/workspace/implementation/reports/phase1-live/empirical/PHASE_AND_AUDIT_TABLES.md) retain all family, branch and extra-unit dispositions. The run reports zero timing violations and zero proxy-as-faithful admissions. Those checks do not establish profitability or causal trading efficacy.

## Evidence that remains unavailable

Of 2,274 rule/date assignments, 1,535 completed, six completed with population holes and 733 retained missing-data dispositions. At least one input is missing in 157 of the 165 date jobs; valid observations from those dates remain visible. The completed scope therefore correctly retains `data_hole`.

- Prior reference windows, same-contract histories, trade/profile coverage and adjacent-minute reconciliation remain incomplete in specified partitions. An unobserved search does not count as a completed zero-opportunity day.
- [Keani](method-keani-open-above-value.md) has four observed openings and four unknown opening-above-value classifications because required prior profiles are unverified. [Refill](method-refill-effect.md) has one verified zero-zone search in 2023 and three tape searches with coverage holes. The tape-dependent [Saint](method-saint-amt.md) routes preserve missing profile, reference or delta dispositions.
- Proprietary platform settings, source selectors and readouts remain unavailable where unpublished. Examples include Jumbo's EV/P-zone/Stat+ engines, source gamma/KG1 maps, the Refill classifier and the jetbundle state classifier. Implemented admission of a supplied record does not recover the underlying private calculation.
- Thesis, selection, order, fill, account and management histories require their actual linked records. NQ comparison data cannot establish an MNQ execution. The [Green Bird November 2025 sweep entry](method-green-bird-failure.md) is distinguished from its later MSS/FVG annotation; the July 23 Sires caption/attempt conflict remains explicit in [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

The next evidence review should inspect each measured branch's definition, exclusions and charts, then identify which missing inputs can be recovered. Any broader sample or changed detector needs a separately declared version and exposure record. The present run supplies no basis for silently tuning a threshold or relabelling comparison outcomes as source trades.

## Current wiki and the frozen run

Empirical registry 1.0.0 hashes all 190 wiki pages that existed when it was frozen, alongside four executable definition files. Updating the live wiki changes that input identity. The historical registry and acceptance have been preserved; the ordinary live validator deliberately rejects the old registry against these newer pages. A future registry must be frozen explicitly against its actual current inputs.

The [definition snapshot](/workspace/implementation/reports/phase1-live/wiki-reconciliation/FROZEN_DEFINITIONS.json) preserves all 194 exact files from accepted commit `8449573`. The archival check verifies every snapshot hash, binds only the definition root to those historical bytes, and runs the original acceptance assertions against unchanged executable and market inputs:

```sh
cd /workspace
PYTHONPATH=implementation/src implementation/.venv/bin/python implementation/reports/phase1-live/wiki-reconciliation/verify_frozen_empirical.py
```

Its [verification record](/workspace/implementation/reports/phase1-live/wiki-reconciliation/VERIFICATION.json) identifies every changed or added wiki page. This verifies the historical run in its historical definition context; it does not claim that the updated wiki was part of the earlier freeze or weaken the live drift checks.

This status page is a research record, not a standalone trade. [Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source catalog and precedence](source-catalog.md) · [Ingest log](log.md)
