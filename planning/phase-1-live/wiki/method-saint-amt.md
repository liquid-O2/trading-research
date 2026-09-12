# Saint — AMT on live markets and confirmed alignment

Operating method / SAINT-AMT. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


[AMTL] p.12 explicitly describes its apparent setups as the same acceptance/rejection read applied at the area being tested. [WIC] p.10 names higher/lower-timeframe alignment as the whole method. [RTVP] p.6 states his preference for continuations and relatively infrequent reversals. Keep all four Saint PDFs together, and keep his decisions separate from Sires's.

| Step | Saint's ordered loop | Current implementation and evidence limits |
|---|---|---|
| 1. Fit the higher-timeframe balance to traded structure | Identify accepted value and its actual extremes; redraw the balance until it fits the market before trading it. Read the profile: balanced distribution; two shelves and their connecting LVN; P/b with a formed balance at the head/base. An unbalanced trending profile is left alone until a new balance forms. ([RTVP] pp.3–11; [TRAP] pp.3–4.) | [O060](auction-balance.md) · [O061](value-and-profiles.md) · [O066](hvn.md) · [O067](lvn.md) · [O068](profile-shelf.md) · [O071](dealing-range.md). Native profile structure and attributed balance/dealing-range admission are implemented. Choosing the source's intended HTF distribution remains a separate source observation. |
| 2. Read arrival, acceptance/rejection and the controlling side | At the extreme ask whether price accepts or rejects; inspect how price arrived, executed delta and whether aggressive effort achieves movement. Heavy buying at an upper extreme can identify trapped buyers if repeated attempts fail. ([AMTL] pp.5–10; [WIC] pp.4–6; [TRAP] pp.4–5.) | [O077](weekly-delta-profile.md) · [O113](approach-speed.md) · [O119](trapped-buyers.md) · [O164](response-efficiency.md). Local arrival, signed concentration and effort/response measurements are implemented. Unpublished classification thresholds and source interpretations remain unavailable automatically. |
| 3. Require the lower timeframe to agree | Wait through free two-sided chop. An actual intraday balance break followed by a held retest shows control; inspect the 15-minute view when the smaller chart is unclear. In the trapped-buyer example, two prior AM/PM failures support the thesis, but the current break/retest is still required. ([WIC] pp.7–10; [TRAP] pp.5–9.) | [O091](break-retest.md) · [O094](failed-auction-saint.md) · [O097](htf-ltf-alignment.md). Selected HTF/LTF parent identities and the ordered break/failed-auction/retest sequence are implemented. Distinct historical references cannot be replaced by duplicate current-session levels. |
| 4. Confirm at the retest and enter | Confirm real initiative in the intended direction; the short example has repeated aggressive selling inside candle bodies, with footprint and DOM agreement. If the retest is missed, do not chase; wait for another relevant area/test. If buyers take and defend the band instead, revise the directional read. ([TRAP] pp.6–12; [WIC] pp.8–10.) | [O004](execution-bars.md) · [O098](aggressor-trades.md) · [O119](trapped-buyers.md) · [O120](footprint.md). Native execution bars and side-specific local flow can support the selected retest. Missing aggressor, depth, platform settings or precise decision time remain evidence gaps. |
| 5. Target the actual next accepted area and manage the evidence | Initial destinations are POC/fair value, the other shelf, the far balance edge or prior balance. Repeated inability to cross and hold POC favors chop; aggressive passage, with a held retest where shown, supports travel to the far side. The TRAP ticket deliberately keeps the objective within a realistic Asia-range distance and uses normal risk. ([RTVP] pp.5–8; [AMTL] pp.8–11; [TRAP] pp.8–10.) | [O064](profile-poc.md) · [O067](lvn.md) · [O139](structural-risk.md) · [O141](trade-objective.md) · [O142](position-management.md). Fixed next-area objectives, structural invalidation and management records are implemented. Source selection and actual management require contemporaneous evidence. |

The failed-auction branch in [AMTL] pp.8–10 is **lower value tried → failure to accept → return into original value → read POC/acceptance again**. Its live example can dip deeply and take time to confirm. Do not import Sires's narrower instant rejection at an older POC as a mandatory condition for every Saint failed-auction read.

**Not standalone:** HTF bias, a large positive delta print, slow/fast arrival, P/b shape, an 80/20 claim, or a high-volume node. Saint's P/b examples start with an impulsive move, establish the new balance, then wait for its break/retest ([RTVP] pp.10–11). They do not license buying every P or selling every b. His choice to wait for rebalance on a trending profile also must not be replaced with Sires's permission to trade an established trend.

### Phase 1 predicate — `SAINT-AMT`

`alignment_ok` means the *current* HTF read and actual lower-timeframe control agree. `source_route_ok` chooses the documented path instead of pooling all profile conditions:

```sql
balance_fixed_before_use AND profile_allows_trade
AND arrival_read_recorded AND control_evidence_recorded
AND alignment_ok AND risk_defined AND objective_fixed
AND balance_known_at <= arrival_at
AND arrival_at <= control_at AND control_at <= decision_at
AND CASE branch
  WHEN 'continuation_retest' THEN
    ltf_balance_broken AND same_boundary_retest_held
    AND repeated_aggression_in_trade_direction
    AND ltf_balance_known_at < breakout_at
    AND breakout_at < retest_at AND retest_at <= confirm_at
    AND confirm_at <= decision_at
  WHEN 'trapped_buyers_retest' THEN
    prior_buying_at_upper_extreme AND two_distinct_prior_failures
    AND prior_failures_known_at < breakout_at
    AND ltf_break_down AND same_boundary_retest_held
    AND repeated_body_selling AND side = 'short'
    AND breakout_at < retest_at AND retest_at <= confirm_at
    AND confirm_at <= decision_at
  WHEN 'failed_auction_return' THEN
    older_value_tested AND older_value_rejected
    AND original_balance_reaccepted AND local_control_confirms_return
    AND older_value_known_at < older_value_touch_at
    AND older_value_touch_at < rejection_at
    AND rejection_at < reaccept_at AND reaccept_at <= decision_at
  WHEN 'poc_traversal' THEN
    original_balance_reaccepted AND aggressive_poc_passage
    AND source_poc_hold_confirmed AND target_is_far_balance_edge
    AND reaccept_at < poc_passage_at AND poc_passage_at <= decision_at
  ELSE NULL
END
```

Citations: [RTVP] pp.5–11; [AMTL] pp.8–12; [WIC] pp.7–10; [TRAP] pp.3–10. Preserve an explicitly sourced long mirror as its own side binding. A range still in “free game” with no confirmed control fails entry admission; an unobserved retest is unknown, not an assumed continuation. Measure POC chop versus passage and the subsequent source objective separately.

## Implementation and empirical status — 2026-09-12

The [M06 contract](../FORMULAS.md#m06) and its 37 operand bindings are implemented and reviewed. [Method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py) and [causal assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py) consume the selected object evidence. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish software completion; the source and data limits described below remain.

The frozen empirical v1 run has the following branch dispositions. Counts are **recorded comparison opportunities**, with separate branch denominators; jobs processed can still contain missing inputs. See [exact definitions](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md), [group results](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) and [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

| Branch | Frozen disposition | Recorded p / f / u | Jobs processed / eligible | Missing-input jobs |
|---|---|---:|---:|---:|
| `continuation_retest` | `data_hole` | 31 / 75 / 0 | 161 / 161 | 54 |
| `trapped_buyers_retest` | `data_hole` | 0 / 0 / 0 | 4 / 4 | 4 |
| `failed_auction_return` | `data_hole` | 0 / 0 / 0 | 4 / 4 | 4 |
| `poc_traversal` | `data_hole` | 0 / 0 / 0 | 4 / 4 | 4 |

All declared jobs for these branches are accounted for; none remain pending. Zero recorded rows under missing scope do not mean a completed zero-opportunity population. The complete **source-method verdict remains unknown**; these counts establish neither author-selected trades nor fills, P&L or a pooled success rate. The [current status page](current-status.md) explains the sampled dates, evidence boundary and frozen-run reproduction.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Auction and profile structure.** [Auction balance](auction-balance.md) · [Volume profile](value-and-profiles.md) · [Profile value area](value-area.md) · [Developing profile snapshot](developing-profile.md) · [Profile point of control](profile-poc.md) · [High-volume node](hvn.md) · [Low-volume node](lvn.md) · [Profile shelf](profile-shelf.md) · [Source-selected dealing range](dealing-range.md) · [Signed volume-by-price profile](weekly-delta-profile.md) · [Developing auction day structure](day-type.md) · [Profile shape and trade permission](profile-shape.md) · [Saint's Asia-range target context](asia-range-risk-context.md).

**Auction routes inside a method.** [Rotation within accepted balance](balance-rotation.md) · [Accepted break and defended boundary retest](break-retest.md) · [Re-acceptance into value](value-reacceptance.md) · [Saint's failed auction and return to value](failed-auction-saint.md) · [POC failure versus efficient passage](poc-traversal.md) · [Higher- and lower-timeframe control alignment](htf-ltf-alignment.md).

**Order-flow evidence.** [Executed aggressor-side trades](aggressor-trades.md) · [DOM at a planned location](dom.md) · [Absorption: effort without price reward](absorption-and-big-trades.md) · [Executed passive replenishment](passive-replenishment.md) · [Local delta concentration at an extreme](delta-spike.md) · [How price arrives at the area](approach-speed.md) · [Trapped aggression at an auction extreme](trapped-buyers.md) · [Native candle footprint](footprint.md).

**Risk, objectives and process.** [Entry-side structural invalidation](structural-risk.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md).

**Research, execution-study and risk records.** [Observed order lifecycle](order-lifecycle.md).

**Auction-state observation.** [Aggressive effort versus price-response efficiency](response-efficiency.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[RTVP]: </workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>
[AMTL]: </workspace/sources/documents/discretionary/amt-on-live-markets.pdf>
[WIC]: </workspace/sources/documents/discretionary/whos-in-control.pdf>
[TRAP]: </workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
