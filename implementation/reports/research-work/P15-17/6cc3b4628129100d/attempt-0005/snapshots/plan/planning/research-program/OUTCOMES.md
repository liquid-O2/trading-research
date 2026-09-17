# Outcome labels and fixed execution benchmark

Owner `P15-03`. Proposed implementation modules: `research/contracts/outcomes.py`, `research/contracts/execution.py`. Reuse native batching and coverage from the existing `method_pack` modules; keep future labels in a module that scanners and feature builders cannot import.

## Causal scale and descriptive movement

Tick `q=0.25` NQ points. At time t define `S_t=max(4q, H-L)` from the complete preceding 60 matching minutes on the same contract. If fewer than 60 matching minutes are available, scale is missing, not filled from the future. A scheduled closed interval does not count as a matching minute; a feed gap inside a scheduled minute makes scale missing. This is a fixed research normalization, separate from the Phase 2 forecast.

For direction `s ∈ {-1,+1}` and reference price p, favorable excursion is `max(0, max_u s*(P_u-p))`; adverse excursion is `max(0, max_u -s*(P_u-p))`. Divide by S for normalized values. Use native interval extrema in `(t,t+h]` with h=5,15,30,60,120 minutes and remaining account-day, recording exact elapsed matching/wall time. Fixed horizons extending past the allowed close are unsupported fixed-horizon labels; separately report the truncated-to-close descriptor. Preserve raw Phase 1 labels unchanged.

Example: long p=100, later prices 102,99,104, S=4 gives MFE=4 points=1S and MAE=1 point=.25S. These extrema do not reveal whether a target preceded a stop.

## Ordered outcomes

`first_passage(events, *, start_ns, end_ns, side, entry, stop, target, coverage) -> PassageResult` returns `target_first | stop_first | neither | same_batch_ambiguous | prior_gap_unknown | missing_future | invalid_geometry`, resolution time, evidence IDs and available-at time. Scan entire equal-timestamp native batches; if both boundaries first occur in one batch, ordering is ambiguous. A gap before the first observed crossing prevents certifying first passage. If complete coverage ends without crossing, return `neither`. Require `side*(entry-stop)>0` and `side*(target-entry)>0`.

Ordered diagnostic grid uses stop distances `{.25S,.5S,1S}` and target distances `{.5S,1S,2S}` at horizons 15,30,60,120 minutes and account-day end. Compute all cells as descriptive diagnostics. The registered primary rule comparison uses the rule's causal structural stop and objective, with a 60-minute expiry; an explicitly earlier source deadline takes precedence. If the rule has no structural pair, use .5S stop and 1S target and label this `standardized_research_geometry`. Never choose the best grid cell after reading test outcomes.

Literal fixtures: long entry100, stop99,target102; batches `(t+1,[100.5]),(t+2,[102]),(t+3,[98.5])` give target-first. Replace the second batch with `[98.5,102]` and result is same-batch-ambiguous. Insert a missing interval before t+2 and result is prior-gap-unknown. Complete prices bounded in [99.25,101.75] give neither. Mirror prices/direction to test shorts.

## Executable benchmark

`replay_family(opportunities, market, policy) -> DayReplay` is a deterministic one-NQ-mini, one-position-at-a-time research simulation. It is separate from descriptive price labels. Contract economics are $20/point and .25-point tick ($5/tick), as specified by [CME NQ](https://www.cmegroup.com/markets/equities/nasdaq/e-mini-nasdaq-100.contractSpecs.html). The commission assumption is $2.50 per contract per side; this is our replaceable research assumption, not a broker quote.

Default latency 250ms after qualification. Enter at the first complete available BBO batch at or after `decision+250ms`, no later than 5 seconds after that time. Long pays ask+one tick; short receives bid-one tick. Quote must be noncrossed, have positive displayed size, be at most one second old and have known availability. No quote means no simulated fill, separately counted. The entry direction must retain valid stop/target geometry after costs; otherwise skip `geometry_invalid_after_latency`. No favorable backfill to the qualification price.

At a simultaneous decision time choose earliest reference issue, then stable opportunity ID; priority is fixed before outcomes. While a position is open, log later signals as `occupied`, including their counterfactual descriptive labels. At most one entry per `(rule_id, reference_id, distinct_contact_id)`; a new contact requires the registered departure/rearm rule. Do not impose a fixed daily trade quota.

Exit is a market-order benchmark triggered when executable liquidation BBO crosses the fixed stop or target: bid for a long, ask for a short. Fill at first valid BBO at or after trigger+250ms, with one adverse tick. A price gap fills at that actual quote, not the boundary. Simultaneous ambiguous stop/target evidence produces two bounded replay paths; exclude from primary paired inference if paths disagree and show both bounds. The source expiry or 60-minute expiry triggers the same delayed market exit. Force flatten at least one minute before the verified account-day matching close. If no usable quote before close, mark replay incomplete, never carry the position into another account day or invent a fill.

Daily marked P&L includes realized cash, commissions and open liquidation value at bid/ask less estimated exit commission/slippage. If it reaches -$1,000 relative to day-start, submit the same delayed flatten and reject later entries for that day. A gap/latency can breach -$1,000; record the breach, do not clip it. Before entry, reject if estimated stop risk including round-trip costs exceeds the remaining loss budget. Unrealized gains do not reset the day-start loss limit. There are no partial contracts or scaling in this benchmark.

Net points for long = exit-entry - commissions/20; short reverses the price difference. Example: quoted ask100.00, entry100.25; later exit bid102.00, filled101.75; $5 round-trip commission gives `(1.50*20)-5=$25`, or 1.25 net points. Stress setting uses 500ms latency, two adverse ticks per side and $3.50 commission per side. All settings are frozen assumptions, not predicted fills.

## Opportunity quality, confirmation delay and missed moves

Compare a response-confirmed entry against: (1) the same reference's first admissible contact; (2) a time-only delayed contact with delay equal to that variant's **training-fold median** confirmation delay for family/session, fallback family then global; (3) unchanged source confirmation. The delay distribution is never fitted on test outcomes. If its median is unsupported, use exactly 60 seconds and label fallback. Every comparison uses the same reference formation and candidate exposure window, plus candidate-specific coverage reporting.

A missed-move descriptor records a favorable .5S,1S,2S crossing before confirmation and whether the structural opportunity remains positive after the actual delayed fill. It is not automatically a loss. Late entries can be useful if subsequent net reward remains positive; this is evaluated rather than forbidden.

## Unchanged-entry exit experiment

Hold a frozen set of entries, sizes, costs and initial structural stops constant. Compare exactly five policies: E0 structural objective + 60-minute/source expiry; E1 30-minute/source expiry with the same stop/target; E2 120-minute/source expiry; E3 break-even activation after +1 initial R, stop becomes entry plus round-trip assumed costs, updated only after the triggering batch is known; E4 trailing stop after +1R, long stop=max(old stop, highest observed executable bid -1R), short symmetric, never loosen. All end at the account-day close. If an explicit source deadline is earlier, all policies retain it and report no effective change where applicable.

No target/stop uses a future maximum or an ex-post optimal exit. Entries with unavailable initial R remain in the denominator ledger and are unsupported for E3/E4. Report paired entry-level and serialized daily results; entries changed by prior exit occupancy are separately identified. Choose exits only in inner tuning; final test comparisons retain every policy. This is a bounded baseline study, not the final learned management system.
