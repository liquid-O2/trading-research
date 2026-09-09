# 51: EV range and open-location switch

**What to build:** A distinct AM expected-move envelope report and causal open-location conditioning table, including EV-to-EQ reactions and in-value versus in-range double-break expectancy.

**Blocked by:** [01: Published 06–09 range to a real path report](01-published-06-09-range-to-a-real-path-report.md), [09: Judas and both single-break day classes](09-judas-and-both-single-break-day-classes.md).

**Status:** planned; this amendment authorizes no implementation or workers. Definitions use the closed variant grids, with no new questions or definition blockers.

**PRD:** [EV range requirement](../PRD.md#required-behavior). **Wiki:** [EV range](../wiki/ev-range-expected-move.md), [open-location switch](../wiki/jumbo-day-classes.md#2026-open-location-switch), [conditional break expectancy](../wiki/range-break-paths.md#2026-conditional-break-expectancy). **Contract:** [matching SPEC columns and variants](../SPEC.md#ev-range-and-open-location-switch).

## Owned scope

Own EV construction/versions and the switch's conditional report. Reuse the range, prior value, width/balance and day-class records in the 01/09 dependency closure; reuse accepted clock and volatility comparisons where available. Keep P-zones, extensions, SessionStat and the two EQ targets distinct. The original EV formula is not required: benchmark and upgrades are explicitly disclosed approximations. Do not add another ticket or change earlier ticket ownership.

Add the [session-fail](../wiki/session-fail-boxes.md) comparison to this report. Consume ticket 09's sweep/fail-back versus hold-outside labeler and ticket 06's completed boxes, TDO, cash-open, NWOG and golden-pocket records. Compare those named labels beside Judas/single-break and the open-location switch. Keep inferred Asia/London clocks tagged. Use known-then location and confirmation records; keep future path outcomes separate. Existing dependencies remain 01 and 09.

## Vertical slice

1. Freeze the SPEC's finite EV and switch variants, availability cutoffs and common outcome grid before confirmation.
2. Compute real-data bounds and open-location snapshots, then EV reach/overshoot/rejection/EQ-return and conditional break paths on native and matched samples.
3. Report all outcome cells, mature n, warmup/missingness, nonreturn, ambiguous order and year stability. Keep the July 9 A-period claim separate from post-OR and developing-RVOL populations. Include this slice in the unchanged all-family pass.

## Independent expected result

For an arithmetic fixture with A=100, historical upper excursions 8/12 and lower excursions 6/10, the mean envelope is [92,110] and its midpoint is 101. A completed 6–9 range [88,112] has EQ=100: these target IDs must differ. Observations 109→110→100 touch the upper envelope before returning to the 6–9 EQ. This small fixture checks arithmetic; it does not replace the 60-session real-data warmup.

With prior value [98,105] and prior range [90,110], an open at 103 is inside both; 107 is outside value but inside range; 113 is above both; 105 retains a value-boundary state. Above-average RVOL first known at 09:45 cannot label the 09:30 snapshot. A 15m OR edge cannot support a pre-09:45 return observation. Verify these independent cases and one manually adjudicated real-data case.

A 09:35 cash-open reclaim may exist while GB-NYAM is still forming. A GB-NYAM fail-back confirmed at 10:05 cannot label the 09:30 snapshot. A NWOG touch changes a destination outcome, not an entry flag. Match the Jumbo comparison cutoff to the completed GB box before comparing rates.

## Acceptance

- [ ] The same report includes the session-fail labeler, print/5-minute confirmations, hold-outside failures and matched Jumbo comparisons. NWOG remains a destination, golden pocket a location and A+ a sweep-only label. No post-10:00 outcome leaks into an earlier open-location input.
- [ ] EV variants have distinct identities, frozen bounds, input lineage and known_at; all required SPEC columns are emitted.
- [ ] Open value/range/6–9 positions remain independent, with mixed/boundary/unavailable populations; switch states use only inputs known at their cutoff.
- [ ] The report includes the common reaction grid, both EQ targets, conditional break counts, clock/width/balance comparisons, failures and complete denominators.
- [ ] Source percentages remain claims; null/worse/low-support comparisons are visible. No approximation is attributed as the original EV formula, and no execution or break-even result is inferred.
- [ ] Independent expected cases pass; slice 51 and the all-family command require the actual report and reject missing/stale evidence or leakage.

## Coverage and statistics command

```sh
phase1 measure --slice 51 --verify
```

Proposed interface for later execution only. Planned report root: `reports/phase-1/51/`. Print the existing `family | variant | n | faithful disagreements | experiment status | report path` header. [PHASE](../PHASE.md) retains the single `phase1 measure --all --verify` stop command.
