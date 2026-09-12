# Empirical extension progress

2026-09-12: Executing SOURCE_CALIBRATION_DISCOVERY_HANDOFF.md on
`codex/phase1-calibration-discovery-v1`, starting at
`c6052fe5f29e06949255653270aebcfd0a8caca8`.

Existing untracked `.audit/method-pack-v1.tsv`, derived MBP-1 directory,
the handoff, and `sources/method/` are preserved. Raw data is read-only and
ignored. Earlier implementation acceptance remains baseline history.

- Stage 1: Luna Max independently assembling calibration dispositions from
  the 22 retained cases and existing chart reviews.
- Stage 2: Sol High designing all catalog branch rules, assumptions and
  observation-unit dispositions; Luna Max inventories actual coverage and
  prepares chronological partitions without examining evaluation outcomes.
- Lead: integrating native selector/replay infrastructure and validation.
- Baseline full suite launched with JUnit evidence under
  `implementation/reports/phase1-live/empirical/validation/`.

Research decision: comparison definitions must remain separate from source
faithfulness. Missing private selections, fills, labels and process records
will not be inferred from favorable price paths. Retrospective evaluation
will make no untouched-sample claim without evidence of prior non-exposure.

Proposed evaluation sampling: first eligible covered session per calendar
month and instrument, chronological and fixed before outcomes. Full chosen
partitions will be scanned, including unsuccessful and censored opportunities.
This is a sample of acquired history, not an exhaustive archive census.

Current status: working; no empirical gate or completion claimed yet.

## Pre-freeze integration, 2026-09-12

Baseline suite passed639tests+2subtests. Calibration ledger accounts for22cases,
17configurations and50branches, independently of historical opportunity counts.
Astra Low rule review replaced the initial delegated rule-design work at the
user's request. Current registry supports19 explicitly named comparisons;
31branches and8additional observation units retain precise source/ledger limits.
No evaluation outcomes have yet been examined.

Coverage-selected samples contain161monthly native-bar sessions and4annual
standalone-trade sessions. Source dates and detected prior-audit exposures are
excluded;2024–2025 are excluded by existing audit outputs. These are chronological
samples of acquired coverage, not an archive census or an untouched-data claim.
Trade and MBP1 schemas are not mixed. No MNQ-to-NQ fill transfer is allowed.

Independent pre-freeze review found and is resolving: ambiguous wording for
next-close/first-retest endpoints; insufficient35day previous-month lookback
(expanded62days); nested MSS completion-reference backdating (point event now
at actual parent completion); exact prior-RTH/profile policy checks; and exact
checkpoint/job membership validation. Native pipeline, source assembler and
endpoint producer checks are connected in run_phase1_empirical.py. Full tape
binding, review tests and final freeze remain in progress. No evaluation scan
or empirical completion is claimed at this point.

## Freeze and operational gates

Independent selector review resolved all six findings. Additional native tape
integration controls cover prior-session/config identity and exact O098 pair
plus touch evidence. The settled native calibration pipeline ran all14bar
rules on excluded2026-02-24, producing21comparison opportunities with native
endpoint/assembler checks. These observations remain outside historical n.
The integrated suite passed724tests+36subtests; a final settled-code rerun is
in progress because reporting edits completed during the preceding run.

Frozen registry7ce33ad43587e44168f2b5cbb910386c33f90cc5f8a1a5c6f2d90709791df381.
Frozen runbbeb2776b90ac4fc0e35b7f654b2b3f44b5129e9bf8e1de2dd6e33e5d7a3ff07
contains165date jobs and2274rule/date jobs. Every job must be completed,
including missing-data dispositions. No evaluation outcomes had been examined
at freeze. Resume: implementation/.venv/bin/python
implementation/tools/run_phase1_empirical.py run --workers 4.

## Reporting revision after initial exposure

Stopped the four-worker run after45published bar jobs when independent report
review foundFER-01: mixed missing/nonempty groups used inconsistent semantic
versus transport observation units; missing/unfinished scope suppressed actual
observed counts, and family all-null totals became0. The independent audit
reconciled506original observations (210pass,293fail,3unknown; n503) and all489
present native bar endpoints, with no duplicate IDs, clock violations or
source-faithful admissions. This is a reporting defect, not a rule revision.

Original manifest,45checkpoints, test identity, reports and logs are preserved
under empirical/revisions/run-v1; original ignored artifacts stay in place.
EVALUATION_EXPOSURE.json conservatively marks the entire submitted165job
manifest exposed. Revision1.0.1 may change only the reporter and orchestration
module; selector source, registry, parameters, inputs and jobs must remain
identical. Every job will be recomputed after current tests/calibration; no old
checkpoint will be relabelled. New artifact directories include the run hash.

## Revised run underway

The corrected reporter was independently reconciled against all45preserved
artifacts: groups/rules/families each retain p210/f293/u3/n503/N506. Actual
missing/unscanned scopes remain separate, with null full-population rates.
The tape metadata cache additionally passed two-source full-profile/minute/
membership equivalence against the preserved original implementation.

Current implementation7895d8d3c3d6875b25c5416c80b3ebca334048c8afcb6efd37d63a9afc0c85f8
passed733tests+36subtests. Native calibration now exercisesall19supportedrules
on excluded2026-02-24 (24comparison opportunities, excluded from historical n).
Run1.0.1 manifeste4a7250026e9fef46b6c729aace161bf69148a4082420770b8de9b7f8cf7a371
preserves the original registry, inputs and165jobs. The first bar and tape
pilot checkpoints both passed; the latter correctly continues independent
branches with a missing prior tape session. Full165job recomputation started
with4bounded workers; no old checkpoint was promoted or relabelled.

## Canonical artifact layout follow-up

Stopped run1.0.1 after85published jobs when actual report validation rejected
the new run-hash artifact directories: its canonical path check still assumed
the legacy layout. No price/rule results were changed. All85checkpoints and
run1.0.1manifest, tests and logs are archived under revisions/run-v1.0.1;
large artifacts remain in their existing hash-isolated locations. Exposure
record1.0.2 retains all165jobs as potentially exposed. Repair only the path
binding and revision orchestration, then validate actual bar+tape pilot reports
BEFORE the next full rerun. No existing checkpoint will be relabelled.

## v1.0.2 actual pilot gate (2026-09-12 20:12 UTC)

Native calibration reran all 19 supported definitions. Revised manifest `d80935d548abe3cafcd695ec842dc69b1d3391646c2da8fe0db9e935a6c37247` binds implementation `8c3097892f5851d84c9c0d5decb09d3026755840ac1acec9d56b3ed89be8556f`. Actual bar and tape pilot jobs produced 12 records and a valid report, preserving observed counts, missing coverage and 163 unscanned jobs separately. Full suite and independent pilot review remain pending. Preserved baseline checks reran successfully. Rules, parameters, source definitions and selected dates remain unchanged.

## Current replay and review

The v1.0.2 suite passed 736 tests in127.90 seconds; native calibration exercised all19 rules and24 opportunities on an excluded source date. Original/post-repair checks passed: six preserved cases, six repair checks,27 audit cases and five paired-quantity probes. The independent actual-pilot gate reconciled p7/f4/u1 and confirmed unchanged selector/replay outputs against the archived version. Full replay started automatically with four bounded workers. By151/165 checkpoints, no job failure had occurred. Native endpoint snapshot review and the first21 of42 rendered chart inspections passed; completion still awaits all jobs and final identity-bound review.

## Completed empirical acceptance (2026-09-12)

All165 frozen jobs and2274 rule/partition assignments completed. Current results reconcile p1000/f1412/u40, n2412/N2452 across raw/group/rule/family levels; no pooled global rate is admitted. Data/source limits remain explicit:733 missing-data assignments,6 completed with population holes, all4 opening classifications unknown, M09 one completed zero and3 missing searches.736 tests and all baseline regressions passed. Independent review reconstructed2309 native endpoints, verified all165 jobs and50 chart bindings, and passed source/causality/counting gates. All50 charts were actually visually inspected, and the165-job resume check added no records.

Final records: `implementation/reports/phase1-live/empirical/COMPLETION_REPORT.md`, `EMPIRICAL_ACCEPTANCE.json`, `RESULTS.md`, and `PHASE_AND_AUDIT_TABLES.md`. Registry1.0.0 and run1.0.2 retain prior exposure and both reporting revisions. Current implementation8c3097892f5851d84c9c0d5decb09d3026755840ac1acec9d56b3ed89be8556f; run d80935d548abe3cafcd695ec842dc69b1d3391646c2da8fe0db9e935a6c37247. No pending job or implementation work remains within this frozen scope. Raw data and protected content preserved; no push or merge.

## Subsequent publication authorization

After empirical acceptance, the user explicitly requested committing the completed extension and pushing it to `main`. The acceptance record above describes the local completion state before this later authorization. Existing unrelated untracked audit, derived-view and source files remain excluded from this commit.
