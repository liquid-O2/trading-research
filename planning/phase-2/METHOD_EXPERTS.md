# Method-specific context experts and conditional plans

Owners `P2-13` (all eight source methods) and `P2-21`; `P2-22` owns conditional plans/replay. Each source entry method has a separately fitted artifact/configuration using the common engine. Do not pool Jumbo, Green Bird, Sires and Saint into one unexplained “good market” score. Share primitives and fitting code; keep branch/source semantics and tests distinct.

## Training population and targets

At every shared snapshot, build a row for every source method whose source clock and required prefix can be evaluated. Include complete no-setup rows. For each method/branch over next 30 and 60 matching minutes: occurrence y=1 if an eligible frozen rule opportunity qualifies within the horizon, else0 on complete coverage. Conditional utility is the fixed benchmark net points of the **first** qualifying opportunity, selected by qualification time then stable ID, not the best future setup. If no opportunity occurs, utility is missing. If geometry/fill/coverage is unsupported, occurrence can still be observed while utility is unknown. Store both masks.

Also build pre-opportunity rows at the actual source qualification clock before any subsequent outcomes; these predict that opportunity's utility, ordered outcome, delay and directional remaining movement. Do not mix occurrence-grid rows and already-qualified rows in one loss without a target-kind column and separate heads/denominators. Response evidence used to qualify a source setup is available on the pre-opportunity row; it was not available on a prior planning row.

Per method fit: branch occurrence softmax/binary heads; conditional mean utility ridge; .1/.5/.9 utility and remaining-excursion quantiles; ordered target/stop/neither class probabilities. Multi-label branch occurrences use independent binary heads inside that method artifact, since several branches can occur in one horizon. Conditional plans are built from these heads plus causal global forecasts. Exact fitting, support and calibration follow the shared contracts. Unsupported rare branches retain baseline eligibility and low-support priors; a profitable-looking six-example Keani cell cannot be declared learned.

## Source-specific feature and output contract

| Method | Required method context and forecasts | Branch distinctions and invalidation |
| --- | --- | --- |
| JJ-TBR | Overnight extension/compression, prior purge and its age, source range geometry, open location, value/profile, single/double-break topology and order, remaining directional excursion, consumed objective, source timing, vol/range forecast and alternatives | Preserve all eight registry branches: outbound/reversal, extended/purged/rotation, extension reaction, other session and timed P-zone. Predict branch suitability separately. Existing P-zones are input references; no Phase 3 zone optimizer. Outbound source deadline remains09:40. |
| GB-FAIL | Reference type/age, prior session/hour/week/month, sweep/reclaim chronology, cash-open/Asia case, direction, failed breakout versus continuation probability, opposing liquidity and confirmation delay | All eight registry branches including refinement scope; preserve the source sweep-entry exception and each source clock. A reclaim continuation is not automatically a failed breakout. |
| GB-VWAP | London/Asia high relationship and close condition, VWAP anchor/band, pullback depth, directional continuation, remaining expansion and reversal alternative | Source long branch remains distinct. A newly proposed short/custom reference belongs to its labelled Phase 1.5 custom sibling, not a fabricated source short. |
| GB-SCALP | Bearish/bullish direction, favorable/discounted pullback, trend exhaustion versus continuation, local flow and shorter remaining reward | Two source case branches plus the known partial automatic-admission scope. Explicit operational trigger is our version; a partial source description is not magically complete. |
| SIRES | Operational day taxonomy and uncertainty, gamma/KG1 regime assumptions, thesis direction, value/balance, flow/reward/defense, squeeze versus failed auction, session quality, invalidation and remaining draw | Preserve12 registry branches and management/re-entry observations. Distinguish DOM rejection, absorption/reward/retest, four-stage stop, footprint reaction, VWAP fade, aggressive/passive OFM, squeeze, balance failure, defended continuation, microbalance and KG1. Low-support branches remain visible. |
| SAINT-AMT | Higher-timeframe balance/trending/new balance, POC/value migration, arrival/control, lower-timeframe agreement and defended retest | Four source routes: continuation retest, trapped-buyers retest, failed-auction return, POC traversal. Require independent HTF/LTF clocks and source control conditions. |
| MEMBER-TWO-REASONS | Prior reaction area, independent minor HVN formation, touch memory, arrival/response quality and competing nearby source reference | Two routes remain distinct. Same-price coincidence or a profile made from the reaction period does not create two independent reasons. |
| KEANI-OPEN-ABOVE-VALUE | Whole A period above prior VAH, higher developing value, aggressive break and defended imbalance retest | The single source long route retains sequence/availability. Before A completion predict the later route; do not mark its complete predicate true. Sparse outcome is acceptable as inconclusive. |

Read each source wiki method and its exact predicate in the canonical Phase 1 formulas when implementing its adapter. These tables do not replace those source predicates. Use Phase 1.5 `resolve_source_context` and normalized records so the new expert cannot silently change setup qualification.

Method feature matrix is the common price/auction/flow/options/cross-market set plus its own source-prerequisite booleans/masks, reference identity/type/age, branch clock distances, selected-rule role and causal upstream predictions. Allowed hinge products, same six semantics mapped to existing method columns: distance_to_reference×predicted_vol30m; reference_age×touch_count; directional_context×flow_reward120s; value_migration×reference_side; confirmation_delay_prior_median×remaining_excursion_median; gamma_scenario_sign×auction_efficiency. An unavailable semantic column disables and records that interaction; it does not get an invented input.

## Research/process scope

REFILL-STUDY gets a memory expert for subsequent touch occurrence and conditional reaction. It requires a causal formation and distinct contacts, prior resolved reactions and pre-touch grade/features. It does not claim actual selected limit orders or the author's private grading model. Complete nonarrival=0 for arrival; reaction given nonarrival is undefined.

JETBUNDLE-STATES gets a distinct transition artifact for B/A/D/E/W only on source-supplied labels with adequate evidence, plus our separately labelled operational states when true ten-level/cancellation inputs are absent. Do not call B/A/D/E/W AMT day types. An annotation fit reports annotation agreement; predictive contribution needs future NQ outcomes independently. When source labels are unavailable, retain the operational auction/flow expert and mark source-state learning unsupported.

STOIC-DATA gets macro/process context features and a fitted contribution head only where publication/vintage support exists. Its scientific collection process is not a trade trigger. STOIC-RISK stays a deterministic separately tested risk overlay; private account states are not invented for a fitted entry model. The benchmark's fixed one-mini/day-start limit is its own research policy.

## Conditional plan schema and deterministic builder

```python
@dataclass(frozen=True, slots=True)
class ConditionalPlan:
    plan_id: str
    method_id: str
    snapshot_id: str
    issue_at_ns: int
    expires_at_ns: int
    thesis_id: str
    revision_of: str | None
    status: str       # supported | watch | low_support | unavailable
    alternatives: tuple[dict, ...] # branch/side/reference, probabilities, utility interval
    selected_branch: str | None
    side: int | None
    reference_id: str | None
    confirmation_recipe: str | None
    ambition: str | None           # reduced | baseline | extended
    time_window: tuple[int, int]
    death_conditions: tuple[dict, ...]
    evidence_for_revision: tuple[str, ...]
    forecast_ids: tuple[str, ...]
    selection_manifest_id: str
```

At issue t, score each eligible branch/reference as `p_occurrence * conditional_mean_net_points`. Do not score unavailable conditional utility as0. Select the highest supported score>0, ties within 1% choose the source baseline then stable ID. Keep every alternative and uncertainty. If no positive supported score, status=`watch`; a missing essential native input yields unavailable; inadequate fit support yields low_support. A plan is a recommendation for a later integrator, not a hard veto of baseline setup discovery.

Confirmation recipe is the frozen Phase 1.5 choice for that branch/fold; context may recommend among the registered alternatives only when separate conditional heads have sufficient data for each. Otherwise keep baseline confirmation. Ambition: reduced when forecast favorable median<baseline target distance; extended when forecast favorable .1 quantile>1.5*baseline target distance; baseline otherwise. This tag does not change the benchmark's actual target/exit in the Phase 2 context comparison. Reference/side must exist and be causal; no novel price is manufactured from a forecast quantile here.

Expire at min(next scheduled quarter-hour update, source expiry, account-day flatten). Death conditions are the source structural invalidation, source window close, reference invalidation/replacement, stale essential input and a known change in the source prerequisite. Revision retains thesis ID while branch/side/reference remain the same; otherwise creates a new thesis ID linked to the old one with evidence and time. Never rewrite a prior plan's probability or pretend the final daily explanation was the initial forecast.

## Context contribution replay

For a comparison-only selector, keep a qualifying source opportunity if the latest valid supported method plan scores its branch>0. Compare with ungated source opportunities, a training-only session-frequency gate and an interpretable price-context gate (directional ER30m>=.35 and target remains positive). All use identical qualification, confirmation, fills, costs, stop/target and day-start risk policy. Unsupported plans default to the unchanged baseline in a separate `fallback_inclusive` replay; also report supported-only coverage. Do not hide absence of IV/native data behind a good subset result.

Admit a context expert for downstream use only with the shared support/causality gates and demonstrated loss/calibration improvement or a measured conditional-utility contribution with uncertainty. Useful descriptive context can be retained as descriptive even when its fitted head fails. Separate branch reliability, calibration, incremental value, opportunity loss and actual model consumption. Final entry selection and combined account economics remain Phase 4 work.
