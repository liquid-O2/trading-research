<!-- full-phase1-measurement-current -->
# Phase 1 — full acquired historical measurement

The unchanged versioned scanners searched **1,742 declared session dates**, 2020-01-01 through 2026-09-03, across all 50 branches and eight additional observation units. The composed census contains **99,294 daily jobs** and **18,747 qualifying market setups**, plus three actual collection-process jobs. The independent primary run and all 90 calendar-recovery dates completed and were verified.

**The acquired observed-input census is executed. Input-limited populations remain unmeasured beyond the observed subset; the exact affected branch/session denominators are listed below.** Qualification does not establish a winning trade. All reported outcomes are subsequent observed prices; no return simulation or actual fill is claimed. Phase 2 remains the additional context layer that selects which setups to use.

[Current measurement report and exact limitations](/workspace/implementation/reports/phase1-live/historical-measurement/MEASUREMENT_REPORT.md).
<!-- /full-phase1-measurement-current -->

## Preserved implementation and prior measurement history

# Trading research

**Current status:** setup implementation and bounded validation are complete; Phase 1 historical setup measurement remains. Phase 2 is the context layer for selecting setups. See the [current phase boundary and next work](planning/phase-1-live/PHASE.md).

<!-- phase1-strategy-current -->
Current strategy reconstruction: **66 setups, 258 no-setup rejections and 0 unavailable market-input candidates** in the declared evaluation sample. Context and research units are separate.

Personal size, account limits and executed-order records do not gate setups. Auction states, QQQ gamma/key levels, P-zones and macro context have explicit source-inspired implementations. A no-setup rejection is not a losing trade or a software failure.

[Completion report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/COMPLETION_REPORT.md) · [Strategy results](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/STRATEGY_RESULTS.md) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md) · [Charts](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/charts/README.md).

Validation: 803 passed, 36 subtests passed in 110.74s (0:01:50); 776 completed jobs across all 58 branch/extra units; 77 primary charts visually checked.
<!-- /phase1-strategy-current -->

## Preserved v2 source-audit baseline

The following section records the earlier, broader source-audit scope. Its personal-record requirements and p/f/u counts are historical comparisons; the strategy scope and current classifications above supersede them.

Git repo root is `/workspace` (`liquid-O2/trading-research`).

- **Start here: [Phase 1 current status and reading guide](planning/phase-1-live/PHASE.md)**
- Readable methods: [live wiki](planning/phase-1-live/wiki/index.md)
- Current completion: [native v2 report](implementation/reports/phase1-live/implementation-v2/COMPLETION_REPORT.md)
- Current measurements: [native v2 results](implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/RESULTS.md)
- Preserved historical measurements: [v1 empirical results](implementation/reports/phase1-live/empirical/RESULTS.md)
- Recovery provenance: [data recovery and event-clock findings](implementation/reports/phase1-live/data-recovery-v1/README.md)
- Implementation: [implementation/](implementation/) (Python import `trading_research`)
- Runners: `implementation/tools/run_phase1_objects.py` (objects/method pass/versioned historical replay) and `implementation/tools/run_phase1_empirical.py` (frozen empirical jobs)
- Reports: `implementation/reports/phase1-live/`
- Raw data: `data/` (gitignored)

Do not edit `planning/phase-1-from-scratch/`, `planning/phase-1-fable/`, `archive/`, or `sources/`.
