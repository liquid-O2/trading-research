# One-mini policy, execution, management and independent risk

Binding additions: the [specialist experiment program](../SPECIALIST_EXPERIMENT_PROGRAM.md) supplies per-parent and per-child phases; [runtime scheduling](RUNTIME_SCHEDULER.md) fixes publication and state behavior. These elaborate the cards without declaring any trading test passed.
[Common contracts](COMMON_CONTRACTS.md) bind every card. This is a specification for future code. The primary position set is `{-1,0,+1}` in one selected outright NQ or ES contract, with total absolute position across instruments at most one. A full contract can fill or remain unfilled; fractional-mini holdings and partial exits are infeasible. Pending orders can still create accidental excess exposure and must be included in risk reservations. A flip is close, confirm flat, then separately approve the opposite entry.

## P01 — Action state and complete sequential policy

1. **Purpose/sources.** Translate G08 opportunity choice into lawful state transitions; user one-mini scope, JTR-15, AUT-10, CD3-01/02.
2. **Inputs.** Timestamped candidate set, calibrated action values, F02/03 instrument/calendar, current position, pending orders, executable BBO and P08/09 headroom. Evaluate on candidate changes, fills and risk events; receipt age is mandatory.
3. **Definition.** In flat state choose wait, abstain, marketable entry, limit entry or stop/stop-limit intent with explicit expiry. While held choose hold, full exit, cancel/replace protective orders, or update a permitted trail. Permit at most one active entry intention plus its contingent protection; atomic risk reservation prevents two simultaneous candidates entering. Binding local refinement: [SR-P01](../SYSTEM_REFINEMENT.md#sr-p01).
4. **Outputs/labels.** `Decision` and `OrderIntent` with preconditions, state/version, expiry and full future management-policy ID. Target `VALUE(action,h)` includes non-fill and the subsequent policy; abstain has zero trading P&L but logged foregone opportunities.
5. **Dependencies.** G06–09 propose; P08/09 veto; P07 executes. P01 cannot directly mutate broker position or override vetoes.
6. **Comparators.** Rule-based highest positive conservative value; regularized contextual utility/ranker; later constrained finite-horizon dynamic programming. Offline RL is optional only after simulator/support audit, not the baseline. Binding further upgrade and child comparisons: [UP-P01](../UPGRADE_PATHS.md#up-p01).
7. **Learning.** Fit on OOF action forecasts and simulated complete paths, retaining all rejected candidates. No fabricated observed counterfactuals; split dates and policy tuning chronologically.
8. **Tests.** T-P01: simultaneous long/short signals, fill during cancellation, reversal, stale account version, boundary near entry, all forecasts missing. Assert position/order reservations never authorize more than one unit.
9. **Acceptance.** Zero unexplained state violations; evaluate daily net, risk overshoot, regret bounds under simulator variants and stability. Predictive score alone cannot promote policy.
10. **Ablation/fallback/resources.** Remove wait model, gate or target adaptation separately. On unavailable market state no new entry; manage existing exposure through independent risk. Class A/B; bound active intents and log every transition.

## P02 — Structural stop and full-position destination choice

1. **Purpose/sources.** Make stop/target geometry executable before entry; JTR-16/17, ALS-04/05, TBR-05, L01–19.
2. **Inputs.** Entry-side executable quote, tick value, frozen candidate band, mapped uncertainty, structural invalidation, future excursion distributions, opposing destinations, fees and remaining USD headroom. Update proposal before order; later revisions are separate decisions.
3. **Definition.** Enumerate source stop variants and volatility/zone-scaled buffers from a registered training grid. Round adverse stops outward to valid ticks, then recompute USD loss. Target candidates include nearer transition, POC/internal level, outer boundary and time exit. Reject plans whose conservative loss plus reserved costs exceeds headroom; do not move a logical stop solely to fit one mini. Binding local refinement: [SR-P02](../SYSTEM_REFINEMENT.md#sr-p02).
4. **Outputs/labels.** `BracketPlan(entry,stop,target,time_exit,geometry_version)` with planned gross/net risk and payoff distribution. Labels record barrier order, unresolved and gap ambiguity, not nominal RR as win probability.
5. **Dependencies.** L supplies objects; G05/06 evaluate; P08 approves and P07 stages orders. Formation anchor and protection anchor may differ and retain distinct IDs.
6. **Comparators.** Fixed tick/source bracket, fixed volatility bracket, structural stop plus nearest target, calibrated joint path optimizer. Nominal low RR is eligible if expected net value supports it. Binding further upgrade and child comparisons: [UP-P02](../UPGRADE_PATHS.md#up-p02).
7. **Learning.** Select buffers/horizons only in nested development; include failed and non-filled candidates. Never optimize from winners' median adverse excursion alone.
8. **Tests.** T-P02: midpoint versus wick-low stop, target behind entry, stop inside spread, changing tick definition, gap-through, near/far competing level and mapping error wider than risk budget.
9. **Acceptance.** Valid tick/side geometry and budget arithmetic must pass exactly. Compare same opportunity cohorts and full account outcomes; freeze parameter stability/benefit criteria through V03.
10. **Ablation/fallback/resources.** Separate stop adaptation from target extension and entry depth. Fall back to validated fixed geometry or abstain; never widen protection to recover money. Class A/B, small bounded bracket set per candidate.

## P03 — Full-position exits, protected structure and trailing value

1. **Purpose/sources.** Preserve RDL-01/02, K18-04, NYA-04, CD3-02, ALS-06 without unavailable partial exits or private trailing formulas.
2. **Inputs.** Live one-unit position, original bracket/risk, current bid/ask, confirmed swing/aggression pockets, updated remaining-path forecasts, elapsed time and boundary/headroom. Recompute at causal protection/forecast events and risk ticks.
3. **Definition.** Compare original stop/target, immediate thesis-invalid exit, entry-price stop, confirmed swing trail, volatility trail, flow-conditioned protection, target extension and time-based exit. Each is a distinct policy. A protective stop can tighten only under its registered rule; entry-price protection is not zero net risk. Target extension requires fresh expected remaining value, not increased displayed RR. Binding local refinement: [SR-P03](../SYSTEM_REFINEMENT.md#sr-p03).
4. **Outputs/labels.** `ManagementDecision` links old/new stop/target, reason and confirmation time. Labels: realized net exit, all-trade MFE/MAE, giveback, duration and tail gap loss. Future maxima are labels only.
5. **Dependencies.** P02 original plan, M08/M11 causal references, G06 residual value, optional R15/R19 later. P07 implements and P08 retains veto authority.
6. **Comparators.** Fixed bracket/time exit; simple volatility/swing trail; discrete exit/hold regression and constrained stopping model. Compare isolated target change and stop change before their joint policy. Binding further upgrade and child comparisons: [UP-P03](../UPGRADE_PATHS.md#up-p03).
7. **Learning.** Train using position histories generated by frozen entry policies, plus held-out policy transfer tests. Do not condition only on positions that later reached profit.
8. **Tests.** T-P03: backdated swing confirmation, trail replacement race, stop gap, target amendment before fill, sudden loss of source feed, and “protected” position that can still lose.
9. **Acceptance.** Measure net/day, conditional tail loss, retained upside and foregone recovery on paired full paths. No universal breakeven or convexity claim; accept only frozen out-of-sample tradeoff.
10. **Ablation/fallback/resources.** Separate optional Response input from price-only management. Revert to valid existing protection; critical risk may flatten. Class A/B, constant state per position; no partial runner.

## P04 — Re-entry, idea memory and cumulative risk

1. **Purpose/sources.** Preserve JTR-24, SRE, ALS-03, CCS-05, OFM-05 and L17 lifecycle while preventing retry history from disappearing.
2. **Inputs.** Parent thesis/object IDs, previous decisions/fills/losses, new approach/return events, failed defenses, updated forecasts, elapsed time and remaining daily/firm allowance. Update on each new candidate and close.
3. **Definition.** A repeat candidate requires an explicitly registered fresh-evidence condition, such as leave-band then re-enter, new defended pocket or revised source state. Keep total realized plus open/reserved idea loss. Compare no re-entry, one repeat, source three-attempt benchmark and value-based repeats under fixed idea/day budgets; quantities never increase after a loss. Binding local refinement: [SR-P04](../SYSTEM_REFINEMENT.md#sr-p04).
4. **Outputs/labels.** `RetryState(attempt,visit,loss_used,new_evidence,belief_revision)` and eligible/veto reason. Label incremental repeat value and entire parent-idea/day outcome.
5. **Dependencies.** L17 separates visits/object roles; G08 ranks fresh opportunity; P08 applies cumulative risk. A stopped trade may update belief but neither compels nor automatically forbids another entry.
6. **Comparators.** No-retry and fixed cooldown/cap rules; logistic repeat-quality model; hierarchical hazard/value model sharing sparse repeat cohorts. Binding further upgrade and child comparisons: [UP-P04](../UPGRADE_PATHS.md#up-p04).
7. **Learning.** Group whole idea/date across splits; retain failed thesis and no-reentry opportunities. Attempt-number effects need coverage adjustment because later attempts are selected paths.
8. **Tests.** T-P04: object rename/merge must preserve losses; stop-and-immediate new quote is not fresh visit; two correlated objects cannot reset budget; same-day halt blocks later hypothetical recovery.
9. **Acceptance.** Compare complete idea/day risk and return; report repeat counts, marginal value, loss clustering and uncertainty across dates. No minimum opportunity count forced.
10. **Ablation/fallback/resources.** Remove new-evidence/decay features separately; fallback no re-entry when lineage/state is uncertain. Class A/B, bounded session ledger with durable history.

## P05 — Event replay and passive-fill uncertainty

1. **Purpose/sources.** Prevent touch-fill optimism in RFE-05–10 and Pine bar backtests; respect DA02/04 and MBP-1 limits.
2. **Inputs.** Eligible MBP-1 trades and validated derived BBO changes, action/side/flag provenance, source ordering/receipt assumptions, submitted order price/size, latency, contract and session. Preserve native intervening events even when candidate scoring is slower. Native option data does not provide futures execution BBO by substitution.
3. **Definition.** Maintain separate strategy-information and venue-outcome clocks. A marketable order uses the valid standing venue ask/bid at simulated order arrival, including a quote last updated before arrival, plus modeled impact; it does not wait for a new quote update. Outcome replay may observe venue events not yet received by the strategy, but they cannot enter the decision inputs. Missing/reordered snapshots or insufficient displayed size yield explicit price/fill uncertainty. Feed latency and outbound order latency are separate assumptions. Passive one-unit fills require post-arrival executions at eligible prices under declared priority assumptions. Maintain optimistic touch bound, trade-through/conservative bound and calibrated probabilistic queue scenario; none is asserted exact with MBP-1. Exclude crossed auctions from continuous-book rules. Stop triggers and stop-limit fills are separate events. Binding local refinement: [SR-P05](../SYSTEM_REFINEMENT.md#sr-p05).
4. **Outputs/labels.** `SimulatedOrderEvent` with scenario, possible/confirmed-under-assumption fill, price/time/cost and ambiguity cause. Queue position is latent, not ground truth. Labels include non-fill and adverse markouts.
5. **Dependencies.** F01–09 ordered replay, P01 intents, P07 state machine; G06 uses validated uncertainty bounds rather than a favorable fill label.
6. **Comparators.** Conservative marketable baseline; passive bounds; survival fill model calibrated later from authorized paper/order telemetry. Full-depth/MBO is a separately justified dependency, not invented now. Binding further upgrade and child comparisons: [UP-P05](../UPGRADE_PATHS.md#up-p05).
7. **Learning.** Fit latency/fill distributions only on past telemetry or explicitly simulated scenarios; historical hypothetical order fills do not identify actual queue rank. Report cohort by timing quality.
8. **Tests.** T-P05: touched with no prints, trade-through gap, cancellation/fill race, same-time ambiguous order, stale quote, price improvement, stop-trigger-no-fill and duplicate execution. Standing unchanged BBO at arrival, an intervening venue quote not yet received locally, missing depth for a sweep, and zero-size best quotes must be tested separately.
9. **Acceptance.** Accounting/state invariants exact; economic advantage must survive conservative plausible fill/cost scenarios or remain unresolved. Shadow quote replay alone cannot validate passive queue fills.
10. **Ablation/fallback/resources.** Compare identical ex-ante candidates across policies including non-fills; fallback marketable benchmark or abstention. Class D/A, streaming event buffers; no full-book queue claim.

## P06 — Routing, latency, cost and adverse-selection experts

1. **Purpose/sources.** Compare market/passive/wait/cancel actions economically; JTR-15, FP8-02, RFE-05 and TECH-06.
2. **Inputs.** Spread/tick value, top sizes/OFI, pace, volatility, candidate age, expected runway, simulated/observed ack and cancel latency, itemized fee schedule with effective dates. Hot-path receipt age updates continuously.
3. **Definition.** Estimate execution shortfall from decision benchmark to fill and subsequent signed markouts at registered 1/5/15/30-second and longer horizons. Separate spread, latency drift, slippage/impact, fees and selection effects to avoid charging the spread twice. Route among P01 permitted actions; cancellation incurs race risk even without explicit fee. Binding local refinement: [SR-P06](../SYSTEM_REFINEMENT.md#sr-p06).
4. **Outputs/labels.** Cost/markout distributions, fill probability and stale-intent expiry; P05 supplies scenario-conditioned fills. Target net action value includes probability mass for non-fill.
5. **Dependencies.** M09/10, C volatility, P05 and F12 telemetry feed G06/P01. No routing model bypasses P08.
6. **Comparators.** Fixed conservative tick costs, spread/volatility linear or quantile regression, calibrated boosted model and competing-risks fill/adverse model. Model uncertainty can favor waiting or crossing. Binding further upgrade and child comparisons: [UP-P06](../UPGRADE_PATHS.md#up-p06).
7. **Learning.** Past-only, instrument/session/coverage stratified; include all sent/cancelled/rejected orders. Actual order-policy selection biases require support diagnostics, not causal uplift claims from filled trades alone.
8. **Tests.** T-P06: wide/locked/crossed markets, negative apparent costs, zero volume, slow ack, burst slippage and cancellation after fill; reconcile gross-to-net terms exactly.
9. **Acceptance.** Cost quantile calibration and conservative sequential net benefit, with stressed latency/slippage. Freeze stress ranges from measured distributions plus prespecified adverse scenarios; no unsupported one-tick assumption.
10. **Ablation/fallback/resources.** Quote-only, trades-only, no prediction, fixed route. Use validated conservative costs if model stale. Class A/B, initial combined decision-stack latency budget from CC-09; measure actual opportunity decay.

## P07 — Broker order state, idempotency and reconciliation

1. **Purpose/sources.** Make later authorized execution auditable and resistant to duplicate/excess orders; prompt operational requirements and JTR-15.
2. **Inputs.** Risk-approved intent/version, broker events/positions/open orders, instrument route, connectivity and authenticated session status. Event and local receipt timestamps stay separate.
3. **Definition.** Durable state machine: proposed→reserved→sent→acknowledged→working→filled/cancelled/rejected/unknown. Timeout means unknown, not safely cancelled. Use idempotent client IDs; reconcile broker truth before retrying. Manage contingent protection/OCO according to verified broker semantics; sibling cancellation is not assumed atomic. Binding local refinement: [SR-P07](../SYSTEM_REFINEMENT.md#sr-p07).
4. **Outputs/labels.** `OrderEvent`, reconciled position and discrepancies, reconciliation latency and unprotected-exposure intervals. No prediction target for exact state handling.
5. **Dependencies.** P08 reservations, P01 intent, F12 adapter; P10 handles critical mismatch. Separate read-only research replay adapter from future live adapter/credentials.
6. **Comparators.** Deterministic state machine/reference reducer; statistical latency anomaly detector optional. Learned state mutation is inappropriate. Binding further upgrade and child comparisons: [UP-P07](../UPGRADE_PATHS.md#up-p07).
7. **Learning.** N/A for state semantics; train-only baselines for anomaly detection, with synthetic faults distinct from real incident evidence.
8. **Tests.** T-P07: duplicate ack/fill, fill-before-ack, reconnect after accepted order, OCO sibling race, partial broker messages, exchange cancel rejection and inconsistent local/broker position.
9. **Acceptance.** No duplicate authorized exposure or unexplained ledger imbalance in fault suite. Uncertain position prevents new entries; verify actual broker behavior before deployment.
10. **Ablation/fallback/resources.** Fault injection with/without telemetry checks; reconcile and flatten under P10 when required. Class A; append-only order log, replicated durable checkpoint if later deployment warrants it. No external account action authorized by this plan.

## P08 — Independent daily USD risk and pre-trade reservations

1. **Purpose/sources.** Enforce user's daily loss objective independently of model confidence; ALS-05, SRE-06, AUT-03.
2. **Inputs.** Day-start net liquidation/cash adjustments, realized net P&L, executable liquidation value, all working/pending exposure, stop geometry, conservative gap/cost reserve and account floor. Update every order/fill/quote/risk event.
3. **Definition.** Let `N_t` be trading-date realized net plus executable open liquidation P&L, excluding deposits/withdrawals, and `B_day≤1000 USD` the frozen daily budget. Remaining daily headroom is `H_day=B_day+N_t`; this is measured from day start, not the intraday peak. Reserve incremental adverse loss from the current liquidation mark to each existing/candidate stop, plus remaining fees/overshoot and feasible pending-order race scenarios. The combined worst-case incremental reserve must be ≤H_day and ≤P09 firm headroom. Do not count an already marked open loss twice, double-charge accrued fees, or count profit from an unfilled favorable order as headroom. At exhausted headroom halt/flatten under P10; evaluate lower budgets in development. Binding local refinement: [SR-P08](../SYSTEM_REFINEMENT.md#sr-p08).
4. **Outputs/labels.** Approval/veto, reservation, halt/flatten events, planned versus realized overshoot and tail loss. Objective is bounded planned exposure; gaps can violate realized budget and must be reported.
5. **Dependencies.** Receives reconciled P07 state and P02 geometry; independently callable emergency path. Cannot trust model-reported position or delay exit to satisfy profit/holding rules.
6. **Comparators.** Hard deterministic budget, lower fixed budgets and drawdown-aware entry abstention challengers; learned sizing cannot exceed one mini or relax limits. Binding further upgrade and child comparisons: [UP-P08](../UPGRADE_PATHS.md#up-p08).
7. **Learning.** Risk reserve quantiles estimated past-only and stress-tested; halt policy selected in development with full paths, not resampled terminal daily totals alone.
8. **Tests.** T-P08: open loss already in N_t plus remaining mark-to-stop loss; profitable day then giveback to the day-start floor; fees causing breach; concurrent reservations; cancelled-but-unknown entry; gap beyond stop; cash withdrawals and DST reset. Hand-calculate both daily and firm headroom, with no double counting.
9. **Acceptance.** Zero unauthorized planned-limit breaches; report probability/magnitude of realized overshoot, tail intervals and worst observed path. No claim stop orders guarantee ≤$1,000.
10. **Ablation/fallback/resources.** Compare conservative reserves and lower budgets without weakening user cap. Unknown account/risk state halts entries and invokes reconciliation/flatten. Class A, independent process/service boundary recommended for live stage.

## P09 — Firm product and account lifecycle constraints

1. **Purpose/sources.** Keep current verified firm rules separate from research alpha and daily loss; [account research](../ACCOUNT_CONSTRAINTS.md), RFE-11–13, AUT-05.
2. **Inputs.** Versioned selected product/purchase date/signed terms, initial balance, EOD high-water history, intraday liquidation balance, payout requests/locks, consistency/holding/news/boundary rules and business fees.
3. **Definition.** Deterministic account state machine for evaluation, funded, payout pending/paid, live transition and breach/closure. Compute trailing floor from the product's stated update rule, but enforce intraday if required. Separate consistency numerator/denominator, pending withdrawal reservation and cash eligibility. No universal $2,000 payout cap, trailing rule or minimum hold is hardcoded across firms. Binding local refinement: [SR-P09](../SYSTEM_REFINEMENT.md#sr-p09).
4. **Outputs/labels.** `AccountState(rule_version,floor,headroom,eligibility,breach_reason)`; account survival, time-to-eligibility and actual cash timeline. Hypothetical eligible payout is not received cash.
5. **Dependencies.** P07 fills and P11 cash; P08 uses stricter applicable headroom, P10 boundaries. Actual product selection/terms are required before deployment, not before research design.
6. **Comparators.** Rule engine against hand-calculated reference paths; research compares product scenarios. Learned forecasts may estimate future survival but cannot interpret/override contractual limits. Binding further upgrade and child comparisons: [UP-P09](../UPGRADE_PATHS.md#up-p09).
7. **Learning.** N/A for rules; any survival estimate uses complete chronological intraday paths and uncertainty, never iid per-trade pass probabilities by default.
8. **Tests.** T-P09: EOD update versus intraday breach, equality boundary, locked floor, loss-day consistency denominator, commission convention, pending payout, product version change, news/holding and holiday flatten.
9. **Acceptance.** Exact reference-path agreement and resolved deployment-critical term ambiguities. Report trading edge and account eligibility separately; forbidden strategy behavior is a product-fit failure.
10. **Ablation/fallback/resources.** Rule-scenario sensitivity; missing/contradictory active terms block that deployment. Do not force a low-quality trade to satisfy activity rules. Class A, versioned compact state/history.

## P10 — Day boundary, outage and emergency flattening

1. **Purpose/sources.** Meet no-cross-day-hold requirement and operational safety without assuming connectivity or instant fills; prompt, current firm schedules.
2. **Inputs.** F03 exchange/firm/broker calendar, holiday/DST/version, market status, local/broker position/order truth, heartbeat/freshness and time-to-cutoff. Independent wall-clock schedule plus event processing.
3. **Definition.** Effective cutoff is the earliest applicable required boundary. Start cancel/flatten with measured latency/retry buffer before cutoff; permit new entries only when their explicit boundary-truncated plan can still exit with the required buffer. Use forecasts for the actual remaining horizon; do not silently reuse an untruncated one-hour forecast or categorically discard the final hour. Cancel outstanding entries, close full position, verify broker flat and no live order. On feed/broker uncertainty reconcile, use permitted independent risk route, and escalate unresolved state. No stop can ensure a fill while the market is closed. Binding local refinement: [SR-P10](../SYSTEM_REFINEMENT.md#sr-p10).
4. **Outputs/labels.** Boundary plan/events, confirmed-flat timestamp, late/failed flatten, unprotected duration and incident report. A forced exit is costed in daily net.
5. **Dependencies.** F03, P07–09 and later verified broker emergency capabilities. Existing broker-side protection remains relevant during local outage.
6. **Comparators.** Deterministic calendar/timer and conservative fixed buffer; empirical quantile buffer challenger. No learned decision can elect to ignore cutoff. Binding further upgrade and child comparisons: [UP-P10](../UPGRADE_PATHS.md#up-p10).
7. **Learning.** Buffer chosen from past telemetry plus fault scenarios and frozen; holidays/terms versioned as known, not inferred from regular weekdays.
8. **Tests.** T-P10: half-day, DST, broker-specific earlier cutoff, feed freeze, rejected close, reconnect with filled entry, local restart near boundary and unavailable market.
9. **Acceptance.** All simulated reachable flatten cases resolve before cutoff; unavoidable/unresolved cases are explicit deployment no-go defects until operational remedy exists. Report live/shadow timing evidence, not guaranteed safety.
10. **Ablation/fallback/resources.** Stress timer/event failures independently; redundant alert/risk route designed during deployment. Class A, low-volume independent scheduler and persistent incident log.

## P11 — Trading net, business cash and objective accounting

1. **Purpose/sources.** Prevent copied-account or payout screenshots from substituting for user objective; DTM-U05, AUT-01/05, K10/K18/NYA/F23.
2. **Inputs.** Every eligible day, one-mini fills/fees, forced exits, account fees/data/platform costs, rule-version payout split/buffer, requested/approved/received cash, refunds and taxes only if explicitly modeled. Cash dates and P&L dates remain distinct.
3. **Definition.** Primary proposed metric `sum(day_net)/count(eligible_days)` includes zero-trade days. Trading net includes execution costs; second ledger reports business net cash after all paid costs and actually received payouts, plus accrued eligible/unpaid amounts separately. Account acquisition/reset expenses include failed attempts; no multi-account scale-up. Report both accounting interpretations while user choice remains open. Binding local refinement: [SR-P11](../SYSTEM_REFINEMENT.md#sr-p11).
4. **Outputs/labels.** Daily/monthly trading and cash ledgers, gross-to-net reconciliation, target gap, risk distribution, equity/floor paths and payout eligibility. One NQ $2,000 equals 100 net points; ES equals 40.
5. **Dependencies.** P07/P09 and predeclared F03 eligibility calendar; V04 evaluates feasibility with dependence-aware uncertainty.
6. **Comparators.** Deterministic double-entry/reconciliation checks; business scenario analysis, no learned accounting. Predictive cashflow model optional only after actual product assumptions fixed. Binding further upgrade and child comparisons: [UP-P11](../UPGRADE_PATHS.md#up-p11).
7. **Learning.** N/A to arithmetic. Missing historical data exclusions must be fixed before outcomes; future outages remain in operational denominator.
8. **Tests.** T-P11: flat day, losing evaluation plus reset, payout pending versus paid, withdrawal not trading loss, fee date, overnight session trading-date attribution and gross/net spread double charge.
9. **Acceptance.** Exact ledger equality and transparent denominator. Economic aspiration passes only under V04 evidence; reported favorable point estimate does not prove sustainable $2,000/day.
10. **Ablation/fallback/resources.** Report costs and payout scenarios separately; unknown fees remain explicit ranges, not zero. Class A/D, tiny ledger relative to event data; no tax/legal advice implied.

## P12 — Execution-instrument research selection

1. **Purpose/sources.** Honor one NQ or ES, preferably NQ, while testing suitability rather than hindsight switching; user scope, X03/X04.
2. **Inputs.** Matched-date development predictions/economics, actual contract liquidity/costs, information masks, tail risk and account rules. NQ and ES point/tick values remain different.
3. **Definition.** Run separate one-mini NQ and one-mini ES development policies under identical protocol and eligible dates; compare achievable net/day, budget-fit opportunity set, fill/cost stress and uncertainty. Prefer NQ if performance/risk is not materially inferior under a margin frozen in development. Freeze selection before each outer/future test. A later intraday selector is a separate registered policy, total position ≤1, flat-confirmed before switching. Binding local refinement: [SR-P12](../SYSTEM_REFINEMENT.md#sr-p12).
4. **Outputs/labels.** Selection record with uncertainty, common and extended-cohort results and reasons. Targets are complete daily policy distributions, not normalized points alone.
5. **Dependencies.** X03/04, P01–11, V02–04. Information universe remains broad whichever instrument executes.
6. **Comparators.** Always NQ, always ES; development-selected instrument; optional contextual selector only if added complexity earns value. Binding further upgrade and child comparisons: [UP-P12](../UPGRADE_PATHS.md#up-p12).
7. **Learning.** No selection on outer results, best-day oracle or asset-specific lucky periods. Account for this choice in trial count and selection uncertainty.
8. **Tests.** T-P12: inconsistent trading dates, accidental overlapping holdings, contract roll, different fee/tick values and shared information ablation.
9. **Acceptance.** Report both instruments' fair results; choose no viable deployment if neither clears economic/risk gates. Preference does not establish feasibility.
10. **Ablation/fallback/resources.** Compare fixed selection against adaptive trial; revert to previously validated fixed instrument or flat. Class B/D; at most doubles main replay workload, shared causal features cached.
