# Unnamed member — prior reaction area plus minor HVN

## Current evidence

Phase 1 setup implementation and the acquired historical census are complete. These counts describe observed setups with branch-specific input limitations; they are not fills or profitability. The source definitions below retain author-specific boundaries. Our inferred reconstruction is versioned separately.

[Full method measurements](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/MEMBER-TWO-REASONS.md) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md) · [Research status](current-status.md).

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS | full acquired historical measurement | 352 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/MEMBER-TWO-REASONS.md |
| MEMBER-TWO-REASONS | B0/B0.1 engineering slice (9 dates, not a family population) | see P15-14 BASELINE_PARITY | not claimed | vacuous all() is unknown; reaction-period HVN fails; applied in the scan path; full-history not run | implementation/reports/research-work/P15-14/ |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS | M07 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |

## Source definitions


Operating method / MEMBER-TWO-REASONS. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


This is the member's own model reported in [K10], not another Sires payout strategy. His original levels were higher-timeframe HVNs with prior clean reactions; KG1 supplied an additional compatible source, not a replacement ([K10] pp.4–6).

| Step | Source loop | Source-object implementation snapshot and evidence limits |
|---|---|---|
| 1 | Before the session, identify the current auction phase, previously reacted areas and HTF objective; write the conditional thesis. ([K10] pp.5, 7, 12.) | [O070](composite-profiles.md) · [O071](dealing-range.md) · [O072](prior-reaction-area.md) · [O138](thesis-lifecycle.md) · [O141](trade-objective.md). Selected composite/dealing-range parents, reaction history, thesis and objective records are implemented. Native prices cannot supply a missing author-selected thesis. |
| 2 | Require the prior reaction area and an independently identified nearby minor HVN to agree. A KG1 reference may add an input where appropriate. ([K10] pp.6–7.) | [O041](kg1-level.md) · [O066](hvn.md) · [O072](prior-reaction-area.md). Independent same-location reasons are checked against their actual parents. The proprietary KG1 engine remains unavailable and a generic gamma wall cannot substitute for it. |
| 3 | Wait for the planned reaction: short on the resistance rejection, or long on the return/second tap when buyers absorb and hold. ([K10] pp.7–8.) | [O072](prior-reaction-area.md) · [O101](absorption-and-big-trades.md) · [O139](structural-risk.md). The assembler now requires the actual contact and subsequent reaction at the selected area before entry. Missing local confirmation remains unknown. |
| 4 | Put risk beyond the relevant rejection structure; use the preplanned target, then the selected management method. ([K10] pp.7–9.) | [O139](structural-risk.md) · [O140](position-sizing.md) · [O141](trade-objective.md) · [O142](position-management.md) · [O150](order-lifecycle.md). Linked structural risk, size, objectives, management and order lifecycle are implemented. Supplied geometry does not prove an order or fill. |
| 5 | Review written thesis quality and actual aggregate results, including evaluation costs and execution discipline. ([K10] pp.3–5, 10–15.) | [O146](process-journal.md) · [O152](cost-model.md) · [O153](outcome-metrics.md). The process journal, costs and outcome distribution consume actual linked episodes. The member's missing account history cannot be inferred from market moves. |

**Not standalone:** one HVN, a rounded resistance price, the cover's payout, or merely adding a KG1 level. The prose says 1.5R planned targets, but the short graphic shows a 1.00R ticket and the long graphic shows a later 9.60R expansion ([K10] pp.7–8). Keep these evidence states separate; neither the exact universal bracket nor the full trailing-convexity mechanism can be certified.

### Phase 1 predicate — `MEMBER-TWO-REASONS`

```sql
thesis_predefined AND objective_fixed AND risk_defined
AND prior_reaction_area_known AND independent_minor_hvn_known
AND confluence_band_defined AND actual_band_contact
AND area_known_at <= touch_at AND hvn_known_at <= touch_at
AND touch_at <= reaction_at AND reaction_at <= decision_at
AND (
  (side = 'short' AND resistance_rejection
                  AND stop_above_rejection_high)
  OR
  (side = 'long' AND planned_return_to_structure
                 AND buyers_absorb_and_hold
                 AND stop_behind_long_invalidation)
)
```

Citation: [K10] pp.5–8, 12. Score the structural sequence and post-entry outcomes in the instrument actually shown, which is ES-202609 (re-read 2026-09-15 below). A target-policy check is separate and unknown when the prose and ticket conflict. The student's case is not automatic evidence for transferring the same thresholds to another contract.



## Source fidelity re-read, 2026-09-15

[K10] was re-read in full and its charts rendered at native resolution. The material fact the zoomed tickets add is the instrument: every chart is **ES-202609** (Deepchart via dxFeed, 2-minute and 30-minute), and the tickets use ES tick economics ([K10] pp.7–8, 12–13). The Lucid Trading slide dates the presentation to July 01, 2026 ([K10] p.4).

- **Trade 1** is "SELL 2 | R:R 1.00" with a 20-tick stop (−$500 = 2 × 20 × $12.50) at the pre-marked 7,558.75–7,564.00 pair; **trade 2** is "BUY 2 | R:R 9.60" from ≈7,530 with a 20-tick stop and a 192-tick target box (+$4,800) up to ≈7,578; the 30-minute context shows the balance 7,545.25–7,564.50, the value box 7,586.25–7,597.75 and the objective band 7,625.75–7,639.25 ([K10] pp.7–8, 12).
- **Sizing** is a fixed $500 risk with the quantity derived from the stop distance (tickets "SELL 2 / 20 ticks −$500", "SELL 1.82 / 22 ticks −$500.50", "BUY 1.82 / 22 ticks") ([K10] p.13).
- The prose says both targets were planned at 1.5R ([K10] text); the drawn first ticket is R:R 1.00 and the second R:R 9.60. The existing note above that keeps these evidence states separate stands.
- The two reasons are a level that rejected before (look left, any prior history) and a minor high-volume node close by, or a KG1 level aligned with the author's own areas; there is no 12:45 split and no disjoint time windows ([K10] pp.6–8). Ruled F15.

**Consequence.** The only worked example is on ES. The two-reason rule, the marked-level discipline and the fixed-dollar sizing are instrument-agnostic, but the author-example replay needs an ES tape; the native census tape is NQ and ES is held only as an options decode in Phase 2. B0.2 records the replay as data_unavailable until an ES tape exists, and the NQ adapter is labelled a transfer.


### Astra dossier corrections (2026-09-15, night)

From [MEMBER-TWO-REASONS.md](/workspace/planning/research-program/reviews/astra-family-dossiers-2026-09-15/MEMBER-TWO-REASONS.md), ruled SD10: [K10] p.13 shows two SELL drawings (2 @ 20 ticks; 1.82 @ 22 ticks) and one BUY (1.82 @ 22 ticks), R:R 1.00 each, although the caption says three shorts; fixtures use the drawn directions; the four displayed payouts (July 8 $2,000; June 30 $1,845.50; June 23 $1,223.75; June 22 $1,974.50) sum to $7,043.75 on one account, a subset of the cohort.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Auction and profile structure.** [Auction balance](auction-balance.md) · [Volume profile](value-and-profiles.md) · [Profile value area](value-area.md) · [Profile point of control](profile-poc.md) · [High-volume node](hvn.md) · [Composite auction profiles](composite-profiles.md) · [Source-selected dealing range](dealing-range.md) · [Prior defended reaction area](prior-reaction-area.md) · [Prior-session auction landmarks](prior-session-reference-levels.md) · [Remaining auction objectives](unfinished-business.md).

**Auction routes inside a method.** [Higher- and lower-timeframe control alignment](htf-ltf-alignment.md).

**Order-flow evidence.** [Executed aggressor-side trades](aggressor-trades.md) · [Absorption: effort without price reward](absorption-and-big-trades.md).

**Regime and thesis context.** [Source KG1 level](kg1-level.md).

**Risk, objectives and process.** [Thesis, validity band and death condition](thesis-lifecycle.md) · [Entry-side structural invalidation](structural-risk.md) · [Exposure fitted to source risk constraints](position-sizing.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md) · [Thesis and execution journal](process-journal.md).

**Research, execution-study and risk records.** [Frozen observation cohort](research-cohort.md) · [Observed order lifecycle](order-lifecycle.md) · [Trading and account costs](cost-model.md) · [Outcome distribution of a declared process](outcome-metrics.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[K10]: </workspace/sources/documents/discretionary/10k-first-month.pdf>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
