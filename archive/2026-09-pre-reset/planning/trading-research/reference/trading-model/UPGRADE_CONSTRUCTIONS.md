# Implementation constructions for the full-system upgrades

This is binding implementation detail for [all parent upgrade paths and child bindings](UPGRADE_PATHS.md). The constructions below supply shared mathematical and software contracts; they do not replace the 153 parent cards, 191 local definitions or original source clauses. Each applicable P0 must register an exact variant, input/target/clock, parameterization, reference and resource budget before code and outcomes. Every empirical comparison remains planned.

An upgrade can improve a measurement, representation, forecast, decision, deterministic service or research method. A shared construction may serve many components, but each consumer retains its own target and integration evidence. Only eligible comparisons proceed; unsupported ones retain precise dependencies, and no unnecessary learned model is required.

<a id="upk-01"></a>
## UPK-01 — Incremental, typed computation and repair

For F01–F12, X01/X02 and deterministic P/V services, compile the declared dependency graph into ports with input field/version requirements, identity, units, clock and capability. A cache key includes source-content version, definition/parameter version, interval/object identity and all fitted dependencies, not merely file path and nominal date. A correction invalidates its actual dependency descendants. Repair starts from a checkpoint that predates the earliest affected retained state, or marks an irrecoverable output unavailable. Missing raw observations are not reconstructed from future knowledge.

Compare a literal complete recomputation with incremental dirty-port propagation, shared sufficient summaries, bounded event coalescing and deadline scheduling. Mandatory integrity/risk/timer lanes cannot be skipped to improve throughput. Optional computations may be dropped/coalesced only under a declared expiry/fallback policy. Record actual completion; when it exists, do not add modeled latency a second time. Unchanged numeric values can have changed provenance, and fresh identical source observations differ from copied stale state.

The engineering scorecard measures exact/tolerance-qualified event, state and action parity; bytes read; CPU/RAM/storage; invalidation radius; recovery work; and deadline misses. Improvements that intentionally change admitted information or decision cadence become separate information/policy experiments rather than being described as pure optimization.

<a id="upk-02"></a>
## UPK-02 — Expected-state residuals, soft cohorts and memory

For M01–M13, participation/Response, options flow and cross-market residuals, preserve raw measurements. A descriptive residual is `r_w = y_w − m_hat(x_w)`, with a separate supported scale estimate when standardizing. Register which context is permitted in `x_w`: for intensity surprise, the default is pre-window state plus known clock/covered exposure; for effort-versus-progress description, current completed-window effort may condition expected progress. Neither residual is automatically a causal effect or a mathematical martingale innovation.

Fit every expected-value/scale transform within the chronological training closure. Historical downstream training uses out-of-fold transformed outputs where required by V02, not residuals from a baseline fitted on the same evaluation labels. At a live cut, all raw inputs to the completed-window residual are already available; future markouts remain labels until maturity. Zero/small scale, missing coverage and observed unknown sign have explicit states. Do not normalize missing tape into apparent calm.

Hard size cohorts remain exact source comparators. A continuous alternative uses registered nonnegative basis weights `b_j(q)` on trade size or log-size. If channels partition flow, enforce `sum_j b_j(q)=1`; otherwise document overlap and never sum the overlapping channels as independent volume. Weighted cumulative flow is `C_j(t)=sum_{i≤t} s_i q_i b_j(q_i)`. Its true OHLC includes the start value and every admitted within-bar update. Changing the basis is a new definition, not a retrospective reclassification of an earlier published path.

A causal decayed/spatial memory can use `M_j(p,t)=sum_i a_i K_j(p−p_i) D_j(t,t_i)`, with declared amplitude, spatial support, decay clock and event eligibility. Keep sign channels and unknown mass distinct. Time, executed-volume and visit-based decay are separate variants. New protection or reward status is appended only after its defining observed event/label has matured. Memory summarizes historical effort; it is not measured remaining participant inventory.

Compare raw totals/rules, robust seasonal summaries, these compact residual/basis features and only then a bounded learned temporal model. A flow/price point-process challenger must specify event types, time resolution, positive intensities, kernel support, stability/initialization, likelihood and observation gaps. The [Bacry–Muzy abstract](https://arxiv.org/abs/1301.1135) motivates joint trade-arrival/price-change kernels; its market results are not evidence for this implementation.

<a id="upk-03"></a>
## UPK-03 — Functional profiles, topology and future mass

For M04–M07/M13, C08, O11/O12/O17 and corresponding L/R families, retain exact raw support before smoothing. On a frozen grid, a nonnegative mass profile has `v_k≥0`, total `A=sum_k v_k` and normalized `p_k=v_k/A` only when `A>0`. Signed delta uses separate nonnegative side channels. Grid origin, tick/row width, formation anchor, overflow, smoothing and tie/plateau rules are part of the definition.

Compare scalar landmarks, weighted quantiles/moments, local prominence, modes persistent across registered smoothing scales, and compact spatial bases. Distinguish scale persistence from a node's observed lifetime. A density-mode persistence algorithm is an optional named challenger with its own exact specification; the [Chazal et al. publisher abstract](https://doi.org/10.1145/2535927) supports the general clustering idea, not a statistical guarantee for serially dependent trading profiles.

For equal finite ordered support, a one-dimensional normalized mass displacement diagnostic is `W1 = sum_k abs(P_k−Q_k) Δp_k`, where `P_k/Q_k` are cumulative masses. This compares distributions, not physical relocation of historical trades. If overflow or incomplete support prevents an exact distance, report the defined observed-domain comparison and overflow separately; do not assign an invented tail location. Decompose changes caused by new trades, corrections, rebinning and normalization.

The new C08 future-profile challenger has explicit auxiliary targets at a fixed cut and horizon: future added volume `A_new`; a no-new-volume state; and the distribution of added mass across the cut-frozen grid conditional on positive volume, including overflow bins. Forecast joint samples or a declared factored law. Reconstruct total future profile from current mass plus future additions; correction effects are separately identified, never silently interpreted as market mass migration. Derived future POC, value area, modes and repair are scored alongside mass/volume accuracy. Missing future tape gives an unavailable/censored target, not zero added volume.

A future option-exposure-field target must state whether it is a subsequently observable board under a frozen valuation/holdings-scenario definition or a latent quantity. A future computed scenario board is not observed dealer inventory. Freeze label-generating model/definition versions, preserve future support/uncertainty and score direct price/path value independently of agreement with that board. OI endpoint supervision alone does not identify the intraday exposure path.

Expected developing-profile residuals use historical prefixes matched by causal formation/time/activity state; completed-session shape is not a current feature. Shape improvements require downstream path/location/policy evidence before being called trading improvements.

<a id="upk-04"></a>
## UPK-04 — Landmark, duration and recurrent-event forecasts

C02–C08/C17–C21, G04/G05, O12/O22, L17 and R use a common episode ledger when appropriate. Register the anchor/object version, episode start, observed state/prefix, allowed transitions, event geometry, time origin, termination, gaps and censoring. Overlapping source attributes remain an attribute vector or explicit joint state; they are not forced into mutually exclusive labels. A competing event model uses a genuine outcome partition, including co-contact/gap/no-event outcomes where applicable.

A simple discrete-time transition model estimates `p_j(k | state, elapsed, I_t)` with nonnegative probabilities whose sum is at most one; the remaining probability means no transition in that bin. Derive survival/cumulative incidence from the same law rather than fitting incompatible independent horizons. A semi-Markov variant includes elapsed time in the current state. Recurrent visits include pressure dose, recovery, novelty, time away and object/episode dependence; flicker does not automatically create another visit.

Ambiguous event order from the observation process remains ambiguous. Use a likelihood/scoring rule over compatible outcomes when specified, a bounded scenario comparison, or an unavailable label; do not manufacture one tick ordering from OHLC. Freeze barrier/region geometry for each forecast. A moving-boundary policy is separately labeled and evaluated.

Pre-touch predictions may condition on eventual reach only in the declared label population, using information available at the original cut. To predict consequences of arrival conditions, integrate a predicted arrival-state distribution. Actual future arrival features cannot enter that pre-touch prediction. Distinguish immediate bounce, retrace, renewed runner, traversal and unresolved outcome, along with occupied duration.

Compare source finite-state rules, shrunken empirical transition tables, additive hazards and compact structured/temporal models. Use independent episode/date/report support and conditional proper scores, then the real delayed entry/exit policy. The same episode can support several labels, but does not become several independent observations.

<a id="upk-05"></a>
## UPK-05 — Shared representations, residual experts and coherent mixtures

G01/G02, C/O/X/R specialists and their joint models compare three changes separately: information available, representation of that information and forecasting capacity. A strong shared baseline plus regularized family-specific residuals is an explicit challenger to isolated experts and a large end-to-end model. Residual corrections must respect the output domain: for example, logits/CDF parameters for probabilities, positive scale parameterizations for variance, and defined joint scenario support for paths.

For distribution stacking, `F_mix(y)=sum_e w_e F_e(y)` with `w_e≥0` and `sum_e w_e=1` applies only to compatible target, horizon, receiver, cut and observation process. Mixture quantiles come from `F_mix`, not a naive average of quantiles. Hierarchical weights can separate common evidence lineage, within-family alternatives and genuinely distinct information. Compare this hierarchy with a simple flat blend; independence is not assumed from different model names. Equivalent duplicate expert outputs/evidence must pass the declared duplication-invariance or bounded-sensitivity case.

Cross-source representations preserve absolute and normalized coordinates, units, settlement/lifecycle, known-at time and support. Set/graph edges represent declared geometry, shared evidence or predictive transmission, with those relations distinguished. Learned edge/lag choices and missing-pattern reliability are training-only. Attention weights, predictive lags and feature importance do not establish causal influence.

Coherence, calibration, applicability and selection form an ordered fitted chain. Score the final emitted outputs after those operations; a later projection or gate may invalidate earlier calibration. Conditional calibrators use partial pooling where supported and retain simple global fallback. Evaluate natural deployment prevalence and selected best-action margins, not only an artificially balanced training sample.

<a id="upk-06"></a>
## UPK-06 — Multiscale memory and volatility target contracts

Every GK/YZ/Parkinson/RV/semivariance/jump/HAR/GARCH/implied/complex specialist keeps its own measurement and forward target. Integrated/realized variation, terminal-return variance, extrema, first passage and executable value are distinct capabilities. Terminal-return variance aggregation includes covariance unless the declared model justifies its absence. A daily integrated-variance forecast cannot automatically produce barrier order or a remaining-session path.

The HAR/ARFI clarification is preserved as an upgrade path. The explicit additional long-memory challenger is ARFIMA for a registered log-variance or log-volatility target: `phi(B)(1−B)^d(y_t−mu)=theta(B) epsilon_t`. Register orders, admissible memory/stability domain, innovation law, zero handling, initialization, finite fractional-filter truncation and horizon prediction. HAR's rectangular lag averages, a smooth distributed-lag basis and ARFIMA receive separate comparisons. A target called log volatility is not silently replaced with log variance.

The [Andersen et al. working paper, section 4](https://archive.nyu.edu/bitstream/2451/27128/2/wpa99061.pdf) describes fractional differencing of log realized volatility followed by ARMA forecasting. Here it supplies a method reference, not copied coefficients or evidence of NQ/ES superiority. Mean forecasts after a log transform require integration/retransformation under the declared predictive distribution; exponentiating its conditional mean is a different functional. Zero/floor conventions change the target and need sensitivity checks.

A realized-measurement-augmented or asymmetric GARCH challenger needs its exact equation/reference and positivity/stability/tail assumptions registered before implementation. Compare added RV information separately from model-class changes. Surface/term/event/0DTE features retain their complete child programs; adding one long-memory model does not replace them or guarantee their mixture is better. Score compatible physical and implied targets separately, then their calibrated bridges and economic contribution.

<a id="upk-07"></a>
## UPK-07 — Joint sensitivity and uncertainty scenarios

O02–O23, X02, L13/L14, G06/G09 propagate common scenarios for quote/sign/surface, assumed holdings, mappings and model parameters. A scenario index represents the same joint world across contracts and candidate actions. Do not independently choose favorable holdings for one node, an unrelated favorable map for another and an incompatible fill for the selected action.

For an option valuation function, compare local derivative approximations with exact finite repricing under a declared joint coordinate/volatility/time shock. Preserve option-value change, option delta-equivalent change and hypothetical offsetting hedge adjustment as different fields with explicit units/signs. Event-frozen sensitivity-weighted flow, arrival repricing and later mechanical revaluation remain separate paths. Aggregate contract counts, premium, delta, Gamma, vega, vanna and charm only through a defined unit-compatible transformation, never an unexplained sum.

Latent intraday holdings/package/queue quantities retain separate observational, parameter and structural-model uncertainty. Endpoint OI cannot identify a unique path; unlabelled package heuristics cannot identify an order owner. Use evidence-compatible model families and direct observable predictive challengers. A finite scenario range is conditional on the registered scenario set, not a universal statistical bound or calibrated probability interval unless that additional claim is supported.

Measure both forecast dispersion and action disagreement. Report which uncertainty changes the selected action and the potential value of improved data/computation. Early quality masks depend on input validity; late action-sensitivity diagnostics depend on completed downstream forecasts/value. The latter cannot feed the current upstream scenario/mixture through an unregistered cycle.

<a id="upk-08"></a>
## UPK-08 — Spatial proposals and controlled geometry

For every L family and C05/C22/O11 originator, a candidate has explicit parent identity, geometry, side/role, birth/revision time, trigger/entry alternatives, expiry and source support. Exact source geometry remains a comparator. A learned field on a fixed relative-price grid separates contact probability, conditional outcome/role and executable utility. Utility is not normalized as if it were a probability density. No-reach/unresolved/no-action states remain in the target population.

Compare generation with a frozen scorer, scoring with a frozen candidate set, and finally the refitted complete policy. Match or stratify candidate count, width, distance, age, support and information/confirmation delay. Include compatible ordinary-price/grid/placebo candidates. A wider band or more proposals can increase contact rate without improving placement, and a moving/snap-to-best region cannot rewrite its earlier label.

A limited offset stays within its registered parent geometry/uncertainty neighborhood; otherwise issue a distinct generator object. Keep actual geometry, measurement/mapping uncertainty and execution tolerance separately typed. Object lifecycle state is a fact; useful lifetime/retention is a forecast/policy. Source narrative labels never create hidden liquidity, identity or mandatory exclusion rules.

<a id="upk-09"></a>
## UPK-09 — Paired full-policy value and bounded waiting

For G06–G08/P/R19, evaluate feasible complete actions on common admissible path/fill/cost scenarios. For two complete policies with the same initial state, the paired quantity is `Delta V = E[R_A−R_B]`, with common model error retained. Common random numbers can reduce simulation noise in differences; they do not remove simulator bias, unsupported action outcomes or market uncertainty. Direct value models and paired residual-value models use chronological training and supported target definitions.

Use either incremental liquidation-equity reward or total-return semi-Markov macroactions. For the latter, `Q(s,a)=E[R_a + V(s_terminal,t_terminal)]`; continuation begins after the complete macroaction, not on its next tick with the same trade payoff counted again. All alternatives share the actual terminal account boundary and include pending orders, one-mini occupancy, fees and cumulative idea/day/firm constraints.

Compare myopic action, source fixed wait/confirmation rules, one-step and bounded two-decision lookahead before deeper planning. Waiting consumes time and can cause nonarrival, invalidation, price deterioration or a missed later opportunity. The value of observing another stage is conditional on its transition law, not guaranteed by a stronger-looking pattern.

Joint stop/target/expiry/route search uses a registered bounded grid. Dominance pruning is allowed only under the stated common outcome and continuation contract; keep complete enumeration as the reference. Optional management uses paired incremental hold/exit/amend value with replacement delay/race costs and tested shrinkage/hysteresis. Mandatory independent risk actions do not wait for a discretionary value threshold. Re-entry requires measured fresh evidence and the same cumulative budgets; no unit escalation or profit-recovery target is added.

<a id="upk-10"></a>
## UPK-10 — Operational protocols, evidence and broad research completion

P07/P08/P09/P10 and F/V improvements use executable deterministic reference reducers, typed rules, reachable-state traces, correction/restart cases and explicit external capability assumptions. Enumerate bounded send/ack/fill/cancel/reconcile interleavings and feasible reservation states. A local idempotent intent log is not a guarantee of external exactly-once orders without verified broker semantics. A stop or latency quantile is not a guaranteed fill during a halt or arbitrary gap.

Deadline control budgets cancellation, reconciliation, full flattening and verification before the earliest mandatory cutoff. Use a conservative fixed fallback until actual telemetry supports a conditional buffer. Account rules are versioned balance/time/lifecycle functions with hand-calculated examples; a learner cannot reinterpret them. Trading net and business cash use separate complete ledgers, including eligible no-trade days and failed-account costs.

Research begins with bounded, registered coverage of every eligible family and expands according to supported effect, uncertainty and resource value. Keep information-versus-capacity controls, layered ablations, planted null/positive/interaction cases and precisely scoped oracle diagnostics. An approximate oracle search is not an exact upper-bound proof. A diagnostic explains its own intervention/population; no ablation is automatically causal attribution.

Freeze future evaluation endpoints or a valid sequential protocol before prospective data. Evaluate registered adaptation as part of the policy, grouping related alarms and separating source faults from market/model drift. Preserve engineering state, evaluation state and selected/rejected/inconclusive/dependency disposition for every exact scope ID and required phase. Continue independent eligible branches when one input or future observation is unavailable. The implementation thread ends with an accurate scope/evidence reconciliation, not at E0 or one family.

## New ports and targets must remain acyclic

These upgrades add constructions inside the existing parent/child scope; they do not authorize an implicit cycle or duplicate process per row. Register new named ports before their first dependent implementation:

| Construction | Producer and allowed direction | Target/consumer rule |
|---|---|---|
| Expected/residual measurements | Raw/reference M/O/X measurements plus preceding-state and fold-local fitted transforms → residual features | Raw channels remain available; fit lineage and information budget are explicit |
| Future profile evolution | M profile/flow and deterministic observed auction state → C08.PROFILE_EVOLUTION → L/G consumers | Predict future mass/shape at a frozen cut; do not consume current downstream C18/O22/G action forecasts as a hidden prerequisite |
| Auction state versus transition | C07.STATE contains current observed occupancy/progress; C07.TRANSITION is a separately fitted forecast | If C08 consumes current auction state, use C07.STATE, not a recursively dependent transition forecast |
| Option topology versus evolution | O11 nodes and observed O10/O12 changes → O13 measured topology → O12.FIELD_EVOLUTION/O12 forecasts → O22/L | Split O12 observed state from its prediction; O13 measured topology cannot require that same current O12 prediction |
| Primitive price/surface scenarios | Existing C15.SCENARIO after O04 and permitted primitive/preceding state → sensitivity/attribution consumers | Preserve the earlier explicit ban on current O10/O12/C19/O22/X06/final G feedback |
| Late decision sensitivity | Joint O21 early quality/scenarios → downstream predictions/value → O21.DECISION_SENSITIVITY or G09.SELECT | Late sensitivity may inform the current final decision or next-cycle computation, not the current upstream fit/gate |
| Hierarchical mixture/paired value | Compatible chronological expert forecasts → mixtures/calibration → candidate action values/differences → selection/risk | Coherence/calibration/selection order and all fitted dependencies are versioned |

Use the existing [computation schedule](components/COMPUTATION_SCHEDULE.md) and [runtime scheduler](components/RUNTIME_SCHEDULER.md) as the governing graph. Port compilation must reconcile these additions, exact new target schemas and observation processes, reject a cycle, and produce prefix/restart/action parity fixtures. Register measurement, auxiliary prediction and policy-value targets separately. Sharing a model representation does not make incompatible targets interchangeable.
