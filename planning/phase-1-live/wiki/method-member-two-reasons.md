# Unnamed member — prior reaction area plus minor HVN

<!-- phase1-strategy-current -->
## Current reconstructed strategy

MEMBER-TWO-REASONS: 1 setup, 6 no setup, 0 unavailable input. Personal execution requirements are excluded from qualification.

[Current method report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/MEMBER-TWO-REASONS.md) · [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md).

| Scope and classification | Observations |
| --- | --- |
| entry_setup:no_setup | 6 |
| entry_setup:setup | 1 |

The preserved source audit below describes its original scope. An inferred level/state is identified as our model; it is not a recovered author label or evidence of an actual trade.
<!-- /phase1-strategy-current -->

## Preserved v2 source-audit baseline

The following section records the earlier, broader source-audit scope. Its personal-record requirements and p/f/u counts are historical comparisons; the strategy scope and current classifications above supersede them.

<!-- phase1-native-v2-current -->
## Current native research implementation — 2026-09-13

Every listed scanner/interface ran for its declared dates or actual collection unit. Source definitions below remain the owner of the method; frozen operational choices are in [the research policy](/workspace/implementation/reports/phase1-live/implementation-v2/RESEARCH_POLICY.json).

Evaluation dates: 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-02, 2024-01-02, 2025-01-02, 2026-01-02. No date was replaced because of missing coverage. `n=p+f`; `N observed=n+u`. A missing population scope is recorded separately from an observed zero.

| Branch/unit | n | p | f | u | Observed scope |
| --- | --- | --- | --- | --- | --- |
| resistance_short | 1 | 0 | 1 | 0 | observed_subset_with_input_limits |
| planned_return_long | 1 | 0 | 1 | 0 | observed_subset_with_input_limits |

**resistance_short** — prior reaction + independently observed nearby minor HVN → current rejection → stop above rejection. Source: K10 pp.5–7,12. Scanner: `trading_research.research.method_pack.historical_auction_scanners:scan_member`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: calendar_unverified (5 job records); same_contract_prior_scope_unknown (4 job records).

**planned_return_long** — planned prior structure + independent minor HVN → second/distinct return → buyers absorb/hold → structural stop. Source: K10 pp.6–8,12. Scanner: `trading_research.research.method_pack.historical_auction_scanners:scan_member`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: calendar_unverified (5 job records); same_contract_prior_scope_unknown (4 job records).

Native market/process research is executed; author-exact verdicts and faithful disagreements remain unknown. No comparison observation is represented as a fill. [Date-level evidence for this method](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/MEMBER-TWO-REASONS.md) · [Software acceptance and remaining external inputs](/workspace/implementation/reports/phase1-live/implementation-v2/COMPLETION_REPORT.md).

<!-- /phase1-native-v2-current -->

## Source definitions and retained historical comparison notes

Operating method / MEMBER-TWO-REASONS. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


This is the member's own model reported in [K10], not another Sires payout strategy. His original levels were higher-timeframe HVNs with prior clean reactions; KG1 supplied an additional compatible source, not a replacement ([K10] pp.4–6).

| Step | Source loop | Current implementation and evidence limits |
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

Citation: [K10] pp.5–8, 12. Score the structural sequence and post-entry outcomes in the instrument actually shown. A target-policy check is separate and unknown when the prose and ticket conflict. The student's case is not automatic evidence for transferring the same thresholds to another contract.

## Definition and scanner correction — 2026-09-13

Both legacy `unavailable_definition` rows below **have source definitions and implemented M07 predicates**. The limitation is absent historical discovery of the selected reaction/HVN context and its subsequent confirmation, not missing source documents or an undefined two-reason method.

| Branch | Existing definition | Actual unresolved scope |
|---|---|---|
| `resistance_short` | K10 pp.5–7: premarked prior resistance/reaction plus an independent nearby minor HVN, rejection, stop above the rejection high; [prior reaction](prior-reaction-area.md), [HVN](hvn.md) and M07 geometry/order checks exist. | Build causal reaction-area and minor-HVN selection with explicit profile window, scale and proximity rules, then detect current rejection. Those operational choices need source support or named research assumptions; the two-reason short is defined. |
| `planned_return_long` | K10 p.8: a preplanned return to structure, buyers absorbing and holding at the level, followed by the long; M07 checks the area/contact/reaction and structural risk. | Connect the planned structure to historical return and absorption discovery. The general method's two-reason context and the long case's own evidence must retain their scopes. Later expansion is an outcome, not an entry selector. |

K10 pp.7–8 states a planned 1.5R target while the figures preserve different ticket/outcome states. K10 p.9 explicitly withholds the full trailing mechanism. These are specific target/management issues; they do not make the entry sequences unavailable. KG1 is an additional location input, not a requirement to erase the independently described reaction/HVN model.

These are unscanned historical populations, not zero-opportunity searches. See the [source/evaluator/scanner distinction](current-status.md#correction-definitions-exist-18-branches-were-not-scanned). No scanner or empirical result changed in this correction.

## Implementation and empirical status — 2026-09-12

The [M07 contract](../FORMULAS.md#m07) and its 18 operand bindings are implemented and reviewed. [Method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py) and [causal assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py) consume the selected object evidence. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish software completion; the source and data limits described below remain.

The frozen empirical v1 run has the following historical dispositions. **`unavailable_definition` is the original registry label, not the current assessment of source availability; those rows were not scanned.** Counts are **recorded comparison opportunities**, with separate branch denominators; jobs processed can still contain missing inputs. See [exact definitions](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md), [group results](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) and [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

| Branch | Frozen disposition | Recorded p / f / u | Jobs processed / eligible | Missing-input jobs |
|---|---|---:|---:|---:|
| `resistance_short` | `unavailable_definition` | unavailable | — | — |
| `planned_return_long` | `unavailable_definition` | unavailable | — | — |

All scheduled comparison jobs are accounted for. The unsupported branches had no historical searches scheduled; they were recorded as dispositions only. Zero recorded rows under missing scope do not mean a completed zero-opportunity population. The complete **source-method verdict remains unknown**; these counts establish neither author-selected trades nor fills, P&L or a pooled success rate. The [current status page](current-status.md) explains the sampled dates, evidence boundary and frozen-run reproduction.

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
