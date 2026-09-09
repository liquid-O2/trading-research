# Full-system contract refinement

This binding review refines every one of the **153 parent contracts**. It preserves the existing 191 named refinements, original source routes and P0–P7 experiment program. Each row below adds a concrete definition/interaction clarification, comparison and local failure case. These are authored implementation requirements; their proposed trading-system tests have not been run.

The [complete handoff](IMPLEMENTATION_HANDOFF.md) and [scope index](IMPLEMENTATION_SCOPE.md) carry the entire B00–B10 program in one continuing implementation workflow. The original IV/VIX question illustrated desired feature/model depth across the system; it did not replace the other families. This contract pass makes the definitions and comparisons precise. The companion [153 substantive upgrade paths and 191 specific child bindings](UPGRADE_PATHS.md) preserve original idea → prior conversation improvement → further construction, with [shared implementation constructions](UPGRADE_CONSTRUCTIONS.md). They can improve deterministic measurements without adding a model.

## Corrections that apply across the graph

| Issue | Binding resolution and future verification |
|---|---|
| Computation latency counted twice | CC-01 uses actual completion and required input/confirmation availability; modeled duration is applied once only when completion is unobserved. The 10:00:00 input / 10:00:02 finish example must remain available at 10:00:02. |
| Normalization and quality dependencies look recursive | F06.RAW prechecks precede F05 normalization; F06.SEMANTIC and F07 operation eligibility follow it. The port compiler must reject an actual cycle. |
| Unchanged prices confused with missing observations | Distinguish source events, last value change, receipt, standing-state validity, liveness and scheduled publication cadence. Healthy unchanged quotes may be valid; repeated copies do not certify an outage. |
| Incompatible prediction targets | Integrated/realized variation, terminal-return variance, extrema, first passage and executable policy value carry different capabilities, units and horizons. Terminal variance needs covariance terms unless the model justifies their absence. |
| Conflicting probabilities across heads | Enforce only the declared coherence relations: fixed-object cumulative incidence by nested horizon, noncrossing quantiles, explicit outcome partitions and realizable joint paths. Overlapping roles/bands are not exclusive categories. Gap crossings break naive nested-band reach assumptions. |
| Calibration broken by later changes | Coherence projection, calibration, gating and selection have a declared order; the final emitted chain is evaluated. Every fitted transform belongs to the chronological training closure. |
| Moving definitions create apparent new market events | Freeze episode/label geometry and record revisions separately: developing value areas, profile bins, swing thresholds, mapped nodes and dynamic targets. Price motion, boundary motion and representation change have distinct provenance. |
| Gamma sensitivity treated as exact finite hedging | Local Greeks, full nonlinear scenario repricing, assumed holdings and actual observed flow remain separate. Near-expiry delta saturation is a required finite-move case. No dealer ownership is inferred from aggregate OI. |
| Uncertainty collapses from duplicated observations | Preserve common quote/sign/surface/holdings errors and evidence-assimilation lineage. Missing tape is different from observed unknown-side volume; endpoint OI supervision does not identify the intraday path. |
| Future evaluation extended until favorable | Choose a fixed endpoint before collecting evidence, or specify a valid sequential-inference protocol with its process assumptions. An ordinary interval cannot be extended until it passes. |
| An early benchmark becomes the end of scope | B00–B10 remains one program. Engineering state, evaluation state and selected/rejected/inconclusive/blocked disposition are separate and evidence-backed. Every source clause, unit, dataset and task remains visible. |

The [common contracts](components/COMMON_CONTRACTS.md), [computation schedule](components/COMPUTATION_SCHEDULE.md) and [runtime scheduler](components/RUNTIME_SCHEDULER.md) contain the corrected graph-wide rules. Parent-local details below also bind named children when their inputs/outputs are affected; do not force an unrelated child to repeat a shared arithmetic test, but record the applicable parent evidence and integration check.

## Local refinements

### Foundations: 12 contracts

<a id="sr-f01"></a>
#### SR-F01 — Atomic reproducible ingestion

Parent: [F01 — Immutable ingestion and schema decoding](components/FOUNDATIONS.md); [individual phases](experiments/F.md#f01).

**Definition and interaction.** Accept a partition only after schema, counts and content identity are committed together; interrupted or partial output cannot enter a consumer manifest. Preserve decimal-to-tick conversion errors and source enum encodings explicitly.

**Comparison.** Compare reference and optimized readers across chunk sizes, projection and restart; an ingestion optimization must preserve downstream event identity.

**Local cases to implement.** Crash between data and manifest write; decimal just off tick; same payload through native and exported encodings; reordered input files.

<a id="sr-f02"></a>
#### SR-F02 — Identity with purpose-specific eligibility

Parent: [F02 — Instrument, option contract and settlement registry](components/FOUNDATIONS.md); [individual phases](experiments/F.md#f02).

**Definition and interaction.** Use distinct valuation, flow-aggregation and execution eligibility. Keep instrument identity valid-time and knowledge-time separately; a corrected historical definition can repair research truth without being made available to an earlier decision.

**Comparison.** Compare authoritative as-of registry and provider mappings on common instruments; uncertain metadata blocks only operations requiring it.

**Local cases to implement.** ID reused on a later date; definition corrected after a trade; multi-leg contract with an incomplete leg; adjusted multiplier that is valid but nonstandard.

<a id="sr-f03"></a>
#### SR-F03 — Calendar-version and reset ownership

Parent: [F03 — Trading calendar, session and boundary engine](components/FOUNDATIONS.md); [individual phases](experiments/F.md#f03).

**Definition and interaction.** Assign every reset and boundary a stable calendar event ID and explicit owner. Independent timers fire once even without a market tick; a late calendar correction creates a recorded new version rather than silently moving old labels.

**Comparison.** Compare historical source-clock variants with the exchange/business-date reference while holding price information and trading horizon fixed.

**Local cases to implement.** Restart immediately before and after boundary; duplicated calendar event; shortened session inside a formation window; a boundary update while a position exists.

<a id="sr-f04"></a>
#### SR-F04 — Availability accounting without double latency

Parent: [F04 — Availability ledger and causal replay clock](components/FOUNDATIONS.md); [individual phases](experiments/F.md#f04).

**Definition and interaction.** Define derived availability as the later of all required input availabilities and actual computation completion. Add a modeled compute duration only when completion is not observed; never add it twice. Raw validation precedes normalization; downstream semantic quality uses normalized outputs through separate ports.

**Comparison.** Compare single-stream reference and partitioned scheduling with identical admitted observations; isolate feed, queue and compute delay contributions.

**Local cases to implement.** Input known at 10:00:00, task finishes 10:00:02 with two-second duration: usable at 10:00:02, not 10:00:04; delayed correction and tied independent streams.

<a id="sr-f05"></a>
#### SR-F05 — Correction and cross-source identity

Parent: [F05 — Event identity, trade conditions and side normalization](components/FOUNDATIONS.md); [individual phases](experiments/F.md#f05).

**Definition and interaction.** Track original transaction, receipt revision and correction as separate identities. Apply a correction once at its availability and retain the previous decision view. Book-event side and trade aggressor remain separate even when the same character is used.

**Comparison.** Compare embedded and standalone tapes by multiplicity and correction lineage, including uncertain match sets; do not force a one-to-one identity from time/price alone.

**Local cases to implement.** Two identical legitimate prints plus one duplicated file; correction before original delivery; correction changing side/size; unresolved cross-source pairing.

<a id="sr-f06"></a>
#### SR-F06 — Freshness versus unchanged value

Parent: [F06 — Quality, gaps, stale data and quarantine](components/FOUNDATIONS.md); [individual phases](experiments/F.md#f06).

**Definition and interaction.** Maintain last source observation, last value change, last local receipt and source-liveness evidence separately. An unchanged healthy book can remain valid; a repeated copied snapshot cannot establish freshness. Recovery of the book does not reconstruct missing trade history.

**Comparison.** Compare fixed eligibility rules and anomaly advisories on reviewed quiet, outage and restart cohorts; measure both coverage loss and corruption leakage.

**Local cases to implement.** Same unchanged price under a healthy feed and a dead feed; a new snapshot carrying an old economic observation; book recovery with incomplete CVD history.

<a id="sr-f07"></a>
#### SR-F07 — Join support and asynchronous error

Parent: [F07 — As-of joins and coverage tensor](components/FOUNDATIONS.md); [individual phases](experiments/F.md#f07).

**Definition and interaction.** A joined vector records per-field age and joint support, not only a row-level valid bit. Preserve uncertainty from asynchronously sampled calls/puts, source/receiver prices and reports; a backward join alone does not make them contemporaneous.

**Comparison.** Compare exact common-cut observed subsets with age-matched larger subsets and separately labeled estimates, using the same downstream target.

**Local cases to implement.** All fields individually within TTL but collected across a large price move; one stale field inside an otherwise new row; overlapping acquisitions with conflicting payloads.

<a id="sr-f08"></a>
#### SR-F08 — Roll bridge and genuine price moves

Parent: [F08 — Futures rolls and equity adjustments](components/FOUNDATIONS.md); [individual phases](experiments/F.md#f08).

**Definition and interaction.** A roll bridge uses actually contemporaneous eligible contracts and records its observation interval. Separate adjustment jumps from genuine overnight movement; expire or translate each object under its declared coordinate policy, retaining exposure and cost lineage.

**Comparison.** Compare fixed/prior-volume roll and reset/translation on common dates without picking the best realized roll economics.

**Local cases to implement.** No simultaneous overlap; both roll and genuine market gap; profile translated twice; dividend-adjusted return input accidentally joined to raw option strikes.

<a id="sr-f09"></a>
#### SR-F09 — Activity bars and event conservation

Parent: [F09 — Causal bars and multiresolution aggregation](components/FOUNDATIONS.md); [individual phases](experiments/F.md#f09).

**Definition and interaction.** The initial event/volume-bar reference closes on the first whole event meeting its threshold and retains overshoot. A split-event alternative must retain one source event with explicit allocation; it cannot create several independent trade observations.

**Comparison.** Compare time, whole-event volume and explicitly allocated bars while matching raw events and reporting completion delay and variable exposure.

**Local cases to implement.** A single trade exceeds several thresholds; empty valid interval versus missing data; reset inside a bar; late correction after a final version.

<a id="sr-f10"></a>
#### SR-F10 — Object state dimensions

Parent: [F10 — Versioned market-object and event registry](components/FOUNDATIONS.md); [individual phases](experiments/F.md#f10).

**Definition and interaction.** Separate object existence/eligibility from visit state and evidence state. An object can remain active after a contact or reclaim. Persist generator-specific allowed transitions and lineage for simultaneous split/merge/retest changes.

**Comparison.** Compare the active-set query against replay of the immutable event log at every tested cut; lifecycle forecasts cannot mutate facts.

**Local cases to implement.** Contact wrongly deactivates a usable level; split and merge at one cut; invalidation followed by reactivation under a new version; restart midway through a visit.

<a id="sr-f11"></a>
#### SR-F11 — Artifact dependency closure

Parent: [F11 — Feature, prediction and fold artifact store](components/FOUNDATIONS.md); [individual phases](experiments/F.md#f11).

**Definition and interaction.** Include actual input columns, transform state, model/calibrator versions, target definition and numerical execution settings in artifact lineage. Atomically commit artifacts and manifests; a changed upstream dependency invalidates only its dependent graph.

**Comparison.** Reproduce a complete run from the declared dependency closure and compare reference tolerances across numerical backends.

**Local cases to implement.** Changed scaler with same model name; missing transitive dependency; partially written cache; accidentally served calibration labels; tolerated numeric drift exceeding a decision threshold.

<a id="sr-f12"></a>
#### SR-F12 — Transport recovery and paired capture

Parent: [F12 — Historical/live adapter and receipt telemetry](components/FOUNDATIONS.md); [individual phases](experiments/F.md#f12).

**Definition and interaction.** Capture source sequence/reset events and local transport gaps separately from market inactivity. Replay the exact captured stream, including disconnections and subscription changes, and compare the actual served versions at their completion times.

**Comparison.** Compare historical and live adapters on the same captured bytes before comparing separately acquired histories; estimate timing uncertainty by source/session.

**Local cases to implement.** Sequence reset after reconnect; duplicate snapshot plus new trades; subscription changes midway through a forecast; UTC clock adjustment while monotonic elapsed time remains valid.

### Measurements: 13 contracts

<a id="sr-m01"></a>
#### SR-M01 — CVD scale, bounds and missing history

Parent: [M01 — Ordinary traded CVD](components/MEASUREMENTS.md); [individual phases](experiments/M.md#m01).

**Definition and interaction.** Publish signed net, buy/sell/unknown mass, interval increments and anchor age together. Unknown-side bounds describe observed unknown volume; missing trades after an outage require a separate incompleteness flag and cannot receive a finite bound from observed volume alone.

**Comparison.** Compare raw cumulative, causal increments and seasonally scaled flow with the same target; preserve the reported-side definition in every variant.

**Local cases to implement.** Unknown signs with complete tape versus unseen volume in a gap; reset creates a large apparent change; unit scaling and correction cross an anchor.

<a id="sr-m02"></a>
#### SR-M02 — Cohort definition and sampling stability

Parent: [M02 — Size-cohort CVD with true within-bar OHLC](components/MEASUREMENTS.md); [individual phases](experiments/M.md#m02).

**Definition and interaction.** Record whether cohorts refer to provider trade summaries, individual prints or another observable unit. Keep empty-but-observed cohort OHLC distinct from missing coverage, and preserve thresholds/version at each event rather than rebucketing old decisions after refitting.

**Comparison.** Compare fixed, equal-count and equal-volume cohorts plus close-only/full-OHLC channels on matched source aggregation and opportunity cuts.

**Local cases to implement.** A vendor changes trade aggregation; one large trade crosses an activity-bar boundary; unknown-side volume concentrated in one cohort; identical closes with reversed extrema order.

<a id="sr-m03"></a>
#### SR-M03 — Divergence as a timed joint observation

Parent: [M03 — Divergence and SMT measurement family](components/MEASUREMENTS.md); [individual phases](experiments/M.md#m03).

**Definition and interaction.** Carry anchor age, comparison duration, amplitude and confirmation delay alongside the divergence sign. A source failure to breach is evaluated only over its observed opportunity interval; missing or closed source data cannot assert nonconfirmation.

**Comparison.** Compare continuous joint price/flow changes, thresholded divergence and sequence encoders with the same anchors and decision time.

**Local cases to implement.** Equal highs within tick tolerance; source market closed; receiver breach precedes source availability; divergence disappears before its pivot confirmation becomes usable.

<a id="sr-m04"></a>
#### SR-M04 — Profile ties, grid phase and topology

Parent: [M04 — Trade-at-price volume profiles and value geometry](components/MEASUREMENTS.md); [individual phases](experiments/M.md#m04).

**Definition and interaction.** Retain the entire POC maximizer set/plateau alongside the reference tie-selected price. Quantify node persistence under neighboring row widths, grid origins and smoothing; a tiny bin shift must not manufacture an independent shelf.

**Comparison.** Compare exact histogram, multiscale smoothing and learned profile representation at matched density/width while preserving each anchor's mass.

**Local cases to implement.** Symmetric double peak; flat POC plateau; grid shifted one tick; narrow valley disappears under smoothing; value-area expansion overshoots the requested fraction.

<a id="sr-m05"></a>
#### SR-M05 — Side dominance under unknown volume

Parent: [M05 — Delta profiles and side-separated auction geometry](components/MEASUREMENTS.md); [individual phases](experiments/M.md#m05).

**Definition and interaction.** At each row retain the observed delta interval from unknown signed volume and distinguish sign-certified from sign-ambiguous concentration. Total, positive, negative and absolute-delta masses remain separate; delta/total requires observed nonzero mass.

**Comparison.** Compare total density, signed channels and uncertainty-aware side profiles on the same anchors and candidate geometry.

**Local cases to implement.** Observed delta changes sign within its unknown-volume bound; buy and sell shelves cancel in net; one empty row creates a spurious ratio peak.

<a id="sr-m06"></a>
#### SR-M06 — TPO confirmation and observational dwell

Parent: [M06 — TPO and time-at-price auction measurements](components/MEASUREMENTS.md); [individual phases](experiments/M.md#m06).

**Definition and interaction.** Separate currently single-print rows from final confirmed single prints, and retain the bracket opportunity count. Trade-visit occupancy, bar-range filling and interpolated dwell are different estimands with their own missing-time exposure.

**Comparison.** Compare bracket sizes and exact visits versus bounded dwell on the same session; evaluate additional value over both volume and price-only geometry.

**Local cases to implement.** A provisional single print fills later; no trade observed during a long stale interval; one bracket revisits a row many times; early close changes available brackets.

<a id="sr-m07"></a>
#### SR-M07 — VWAP numerical and anchor stability

Parent: [M07 — Price VWAP, anchored VWAP and dispersion](components/MEASUREMENTS.md); [individual phases](experiments/M.md#m07).

**Definition and interaction.** Use stable weighted moments with explicit rolling-window downdates and zero-mass behavior. Track anchor selection and birth separately from its historical geometric start; several anchors at one price remain correlated candidates.

**Comparison.** Compare exact two-pass references, online updates and rolling downdates; compare anchor and dispersion choices without post-hoc choosing the winning anchor.

**Local cases to implement.** Large price with tiny dispersion; remove the last trade in a rolling window; confirmed swing anchors a historical window only when known; split and adjustment consistency.

<a id="sr-m08"></a>
#### SR-M08 — Swing threshold ownership

Parent: [M08 — Causal swings, structure and retracement anchors](components/MEASUREMENTS.md); [individual phases](experiments/M.md#m08).

**Definition and interaction.** Freeze a directional-change threshold at leg birth for the initial reference. A dynamically updated threshold is a separate causal detector because falling volatility can trigger confirmation without further price movement. Store equal-extreme tie and nested-leg rules.

**Comparison.** Compare fixed-at-birth and dynamic thresholds after their actual delay, against raw lagged-price and running-extreme controls.

**Local cases to implement.** Price unchanged while volatility threshold falls; plateau equal highs; nested swings confirm together; gap jumps beyond reversal threshold.

<a id="sr-m09"></a>
#### SR-M09 — Pressure observation support

Parent: [M09 — Best-quote OFI, imbalance and replenishment proxies](components/MEASUREMENTS.md); [individual phases](experiments/M.md#m09).

**Definition and interaction.** Define event-rate exposure using observed source time and retain action ambiguity on two-sided updates. Imbalance and microprice are unavailable when total eligible displayed size is zero; no hidden-depth interpretation enters a feature name.

**Comparison.** Compare quote state, observed action rates, trade flow and their interactions with common cuts and coverage; normalization must preserve tick/contract units.

**Local cases to implement.** Both sizes zero; spread changes with unchanged imbalance; action side N on a two-sided update; a gap crossing the OFI window; trade and subsequent book change counted twice.

<a id="sr-m10"></a>
#### SR-M10 — Effort denominators and exposure

Parent: [M10 — Tape intensity, effort, progress and response efficiency](components/MEASUREMENTS.md); [individual phases](experiments/M.md#m10).

**Definition and interaction.** Use covered elapsed time for activity rates, with missing time separate from quiet time. Retain progress, effort and duration alongside any ratio, and define burst start/completion without using its future maximum.

**Comparison.** Compare additive numerator/denominator models, bounded ratios and marked event models on identical observation windows.

**Local cases to implement.** Zero effort and one-tick motion; identical quantity in different durations; partial outage in the denominator; a burst chosen because of its later price reversal.

<a id="sr-m11"></a>
#### SR-M11 — Memory membership and markout origin

Parent: [M11 — Aggression memory and subsequent markout ledger](components/MEASUREMENTS.md); [individual phases](experiments/M.md#m11).

**Definition and interaction.** Freeze each queried cluster membership/version at the cut. Future cluster merges cannot rewrite prior feature membership or training groups. Record markout origin, observation process and maturity separately from a later protection confirmation.

**Comparison.** Compare price-only clusters with signed/cohort/decayed memory using identical births; evaluate decay and retest policies separately from cluster discovery.

**Local cases to implement.** A later print bridges two clusters; overlapping markout horizons; protection confirmed after the opportunity has passed; opposing memories at one price.

<a id="sr-m12"></a>
#### SR-M12 — Reference identity and missing opens

Parent: [M12 — Opens, gaps, settlements and reference-price measurements](components/MEASUREMENTS.md); [individual phases](experiments/M.md#m12).

**Definition and interaction.** Distinguish the first observed print from a certified session open when opening data are missing. Each reference carries source type, economic observation date and known time; substitutions create named alternatives rather than changing its identity.

**Comparison.** Compare gap/reclaim predictions by reference type at common availability, with auction and incomplete-open cohorts explicit.

**Local cases to implement.** Late first observed print; revised settlement; exchange open differs from bar timestamp; two references numerically equal but have different publication histories.

<a id="sr-m13"></a>
#### SR-M13 — Sparse footprint contrast

Parent: [M13 — Footprint and within-bar aggression geometry](components/MEASUREMENTS.md); [individual phases](experiments/M.md#m13).

**Definition and interaction.** Keep empty observed cells, unobserved cells and price gaps distinct. Compare raw ratio thresholds with count-aware/shrunk side contrasts; smoothing or pseudocounts are versioned estimators and cannot create traded mass.

**Comparison.** Compare continuous side contrasts, binary stacks and spatial/temporal encoders at matched row size, minimum mass and decision delay.

**Local cases to implement.** One buy against zero sells; ratio dominated by two contracts; nonadjacent traded rows appear stacked after gap compression; provisional tail changes before bar completion.

### Context: 24 contracts

<a id="sr-c01"></a>
#### SR-C01 — Range birth, freeze and anchor identity

Parent: [C01 — Source-faithful range and session geometry](components/CONTEXT.md); [individual phases](experiments/C.md#c01).

**Definition and interaction.** Give provisional formation, completed observation, publication and later revision distinct states. A valid range needs all required source intervals or an explicit partial-range variant. Store raw anchor coordinates and normalized multiples before display rounding.

**Comparison.** Compare identical underlying intervals through event/bar references and each disclosed source anchor; revisions create new views without changing earlier decisions.

**Local cases to implement.** Zero width; missing early high; a last forming trade arriving late; 1.33 extension versus normalized position 1.33; revised prior-RTH range.

<a id="sr-c02"></a>
#### SR-C02 — Ordered contact and breach semantics

Parent: [C02 — Ordered break, sweep and reclaim state](components/CONTEXT.md); [individual phases](experiments/C.md#c02).

**Definition and interaction.** Define breach, traded contact, gap crossing, return and retest separately against the frozen object version. Record unresolved tie sets when source ordering is insufficient. A final no-break label requires a complete horizon.

**Comparison.** Compare strict source transitions and registered hysteresis/tolerance variants on the same observed path and denominator.

**Local cases to implement.** Both edges inside one unresolved bar; repeated high breaks before low; gap across an edge without traded touch; state at exact horizon endpoint.

<a id="sr-c03"></a>
#### SR-C03 — Overlapping branch forecasts

Parent: [C03 — Jumbo path and internal-versus-extension forecast experts](components/CONTEXT.md); [individual phases](experiments/C.md#c03).

**Definition and interaction.** Treat wide/internal, first projection, later reversal and partial-retrace branches as hypotheses/heads that may overlap. Use a multinomial only after defining an exclusive outcome partition; common-target head probabilities are not added as independent evidence.

**Comparison.** Compare pooled conditional path model, partial pooling and branch-specific experts at matched information and effective day support.

**Local cases to implement.** One path reaches a projection then partially retraces and later reverses; two heads share the same outcome; missing branch applicability; repeated prefixes from one day.

<a id="sr-c04"></a>
#### SR-C04 — Opening reference and attribute maturity

Parent: [C04 — Open location relative to prior auction structure](components/CONTEXT.md); [individual phases](experiments/C.md#c04).

**Definition and interaction.** Freeze the prior profile/reference version used for opening classification. Keep observed opening attributes, elapsed persistence and matured future type separate; reference touches have declared tolerance and ordering.

**Comparison.** Compare prior-range-only, prior-value-only and joint opening information using identical opening cuts and future horizons.

**Local cases to implement.** Reference tested before versus after departure; opening band crossed after an apparent early drive; prior profile corrected at noon; missing true first trade.

<a id="sr-c05"></a>
#### SR-C05 — Formation as a causal stopping rule

Parent: [C05 — Adaptive clock, activity and auction-range discovery](components/CONTEXT.md); [individual phases](experiments/C.md#c05).

**Definition and interaction.** Specify anchor, eligible activity, stop condition, maximum formation time and no-formation outcome. Include days without a completed adaptive range in the opportunity/day denominator; a boundary selector cannot see its downstream future outcome at inference.

**Comparison.** Compare clock/activity/auction rules with equal search budget and common full-day policy denominator; distinguish formation-selection value from forecast value.

**Local cases to implement.** Threshold reached during one atomic trade; activity gap; stop never reached; two equally scored windows; inner selector accidentally trained on an outer date.

<a id="sr-c06"></a>
#### SR-C06 — Coherent excursion and path objects

Parent: [C06 — Conditional excursion and P-zone distribution](components/CONTEXT.md); [individual phases](experiments/C.md#c06).

**Definition and interaction.** Retain decision anchor, fixed end, upward/downward excursion and terminal-price target as separate fields. Joint samples must obey their own price-path support; marginal quantiles do not imply ordering, reach or a realized path. Calibrate only target-compatible outputs.

**Comparison.** Compare marginal quantiles with joint excursion/time/path models using the capabilities each actually supplies; price-grid contact differs from gap crossing.

**Local cases to implement.** Terminal displacement larger than sampled maximum; crossing quantiles; shifted decision price with same named session end; no future observations versus a zero move.

<a id="sr-c07"></a>
#### SR-C07 — Frozen versus moving auction references

Parent: [C07 — Auction acceptance, rejection, balance and discovery](components/CONTEXT.md); [individual phases](experiments/C.md#c07).

**Definition and interaction.** For dwell/volume outside value, identify whether the boundary is frozen at episode birth or updated with the developing profile. Record boundary-motion events separately from price crossings. Observation gaps do not establish continuous dwell or rejection.

**Comparison.** Compare fixed-reference acceptance, causal moving-reference acceptance and continuous measurements while controlling for profile maturity.

**Local cases to implement.** Price unchanged while VAH moves across it; wick outside then no observed trades; moving boundary reverses twice; a covered quiet interval versus lost feed.

<a id="sr-c08"></a>
#### SR-C08 — Comparable distribution migration

Parent: [C08 — Value migration and multiscale auction relationships](components/CONTEXT.md); [individual phases](experiments/C.md#c08).

**Definition and interaction.** Compare nonnegative profile mass on a shared raw-price/tick grid with explicit overflow and coverage. Separate total mass growth, normalized shape change, coordinate drift and missing-support change; signed delta uses buy/sell or positive/negative channels rather than an invalid signed probability measure.

**Comparison.** Compare POC/centroid shifts, overlap and transport-style shape features on fixed support and matched elapsed time/activity.

**Local cases to implement.** Same POC but opposite mass transfer; removed wing mimics migration; negative delta bins; all mass at one price; roll-coordinate bridge change.

<a id="sr-c09"></a>
#### SR-C09 — Seasonal target and exposure accounting

Parent: [C09 — Historical range and seasonal volatility baseline](components/CONTEXT.md); [individual phases](experiments/C.md#c09).

**Definition and interaction.** Separate true range, anchored excursion, integrated return variance and terminal-return variance. A seasonal baseline records covered duration, trading/calendar clock and prior-price scale; incomplete sessions are neither ordinary full sessions nor zero observations.

**Comparison.** Compare pooled and partially pooled seasonality on the same target/cohort, retaining gap and short-session channels.

**Local cases to implement.** Same range with different terminal variance; missing previous close; shortened session; unchanged valid price path; holiday incorrectly counted as a zero day.

<a id="sr-c10"></a>
#### SR-C10 — Valid-domain GK arithmetic

Parent: [C10 — Garman–Klass measurement and forecast specialist](components/CONTEXT.md); [individual phases](experiments/C.md#c10).

**Definition and interaction.** For valid positive OHLC, H encloses O/C and L encloses O/C. A materially negative GK result signals invalid inputs/numerics, not negative variance to silently clip. Keep overnight movement separate and label the lag-to-forecast mapping.

**Comparison.** Compare exact GK and alternative estimators on identical completed intervals before comparing downstream learners.

**Local cases to implement.** H below close; decimal/log roundoff near constant price; opening gap with constant intraday path; scaled prices give identical log variance.

<a id="sr-c11"></a>
#### SR-C11 — YZ interval and component identity

Parent: [C11 — Yang–Zhang opening-jump-aware specialist](components/CONTEXT.md); [individual phases](experiments/C.md#c11).

**Definition and interaction.** Preserve ordered contiguous interval pairs, sample-variance convention, Rogers–Satchell term, n-dependent weight and opening-gap definition. Missing intervals change applicability or an explicitly defined gap target, not the sample count silently.

**Comparison.** Compare open/close boundary and component variants on matched observed intervals; distinguish estimator choice from forecast-model capacity.

**Local cases to implement.** n=1; skipped session between previous close and open; opening-only move; all equal prices; futures overnight boundary differs from RTH boundary.

<a id="sr-c12"></a>
#### SR-C12 — Observed price process and missing-grid semantics

Parent: [C12 — Multiscale realized variance and semivariance](components/CONTEXT.md); [individual phases](experiments/C.md#c12).

**Definition and interaction.** Declare trade, midpoint or another price process and causal sampling rule. Healthy unchanged standing quotes can yield true zero returns; missing observation/liveness cannot. No next-tick interpolation enters a current grid point. Mark the covered target duration.

**Comparison.** Compare sampling/noise methods against independent reference grids and downstream forecasts on the same supported process.

**Local cases to implement.** Constant live midpoint with active bid/ask bounce; forward-filled outage; future nearest tick chosen for a past sample; partial final grid interval.

<a id="sr-c13"></a>
#### SR-C13 — Forecast scale and retransformation

Parent: [C13 — HAR and multiscale forward-volatility expert](components/CONTEXT.md); [individual phases](experiments/C.md#c13).

**Definition and interaction.** Give variance, volatility and log-variance models distinct target IDs. Exponentiating a conditional mean log variance estimates a different functional from mean variance; mean forecasts need a trained distribution/retransformation rule and separate calibration.

**Comparison.** Compare persistence, HAR variants and registered long-memory alternatives with identical target, lags, horizon and tuning budget; retain component contributions rather than only a model name.

**Local cases to implement.** Log residuals with nonzero spread; 5 trading versus calendar days; unavailable current full-day RV; rolling warmup and same endpoint predicted at many prefixes.

<a id="sr-c14"></a>
#### SR-C14 — Jump proxy versus identified discontinuity

Parent: [C14 — Jump, discontinuity and burst-volatility expert](components/CONTEXT.md); [individual phases](experiments/C.md#c14).

**Definition and interaction.** Record sampling, noise, finite-sample and threshold conventions for jump proxies; distinguish opening gaps, observed intraday discontinuities, clustered bursts and feed recovery. Zero truncated RV-minus-BV is a proxy outcome, not proof that no jump occurred.

**Comparison.** Compare total variation, robust two-part continuous/jump forecasts and event-conditioned tails with natural event prevalence.

**Local cases to implement.** Spread bounce; two adjacent jumps contaminating BV; feed reconnection; scheduled announcement with no move; missing observations through the alleged jump.

<a id="sr-c15"></a>
#### SR-C15 — Common horizon and derivative conventions

Parent: [C15 — Implied-volatility, skew and term-structure forecast specialist](components/CONTEXT.md); [individual phases](experiments/C.md#c15).

**Definition and interaction.** Keep native-expiry, fixed-tenor and fixed-end forecasts distinct; record forward/spot, delta and calendar/trading-time conventions. Same-horizon physical variance gaps require OOF physical forecasts. Surface dynamics use explicit early measurement/scenario ports to avoid cycles.

**Comparison.** Compare actual richer smile/term/event information separately from more powerful model class and from quote-coverage selection.

**Local cases to implement.** Two equal DTE labels with different settlement times; rolling tenor changes without same-contract IV change; a physical forecast trained on its own outcome; unsupported wing.

<a id="sr-c16"></a>
#### SR-C16 — Cadence-aware volatility information

Parent: [C16 — VX, volatility-complex and cross-market stress expert](components/CONTEXT.md); [individual phases](experiments/C.md#c16).

**Definition and interaction.** Daily VX/index observations remain known daily state with age and expected next publication; they are not fabricated intraday updates and are not invalid solely because their values have not changed. VIX-option price/forward/IV targets use explicit native units and settlement class.

**Comparison.** Compare each independently supported source at its actual cadence and effective information age before joint stress forecasting.

**Local cases to implement.** Repeated daily value during a live session; new daily publication; VIX forward versus equity IV units; missing intraday cash print; source outage versus scheduled silence.

<a id="sr-c17"></a>
#### SR-C17 — Event information versions

Parent: [C17 — Scheduled events, announcements and publication state](components/CONTEXT.md); [individual phases](experiments/C.md#c17).

**Definition and interaction.** Separate scheduled time as then known, schedule revision, actual publication, receipt, consensus vintage and observed price reaction. An unscheduled event cannot appear in pre-event calendar features from a later complete calendar.

**Comparison.** Compare anticipation, observed reaction and verified surprise channels separately, with matched non-event clocks and event episodes.

**Local cases to implement.** Release postponed after an earlier schedule; statement followed by press conference; consensus timestamp after publication; corrected macro value; coincident events.

<a id="sr-c18"></a>
#### SR-C18 — Independent control outcomes

Parent: [C18 — Participation, control and effort-progress forecast specialists](components/CONTEXT.md); [individual phases](experiments/C.md#c18).

**Definition and interaction.** Observed aggression/control features may summarize price/flow, but their predictive targets must be later movement, persistence or value rather than the same contemporaneous formula. Keep unknown-side and missing-tape states separate throughout cohort interactions.

**Comparison.** Compare price-only, ordinary/cohort/OFI/footprint and joint heads at common cuts; reduce repeated-prefix weighting to episode/day support.

**Local cases to implement.** Positive signed flow with adverse price response; all flow unsigned; two cohorts offset; current control label accidentally used as future target; missing MBP with valid trades.

<a id="sr-c19"></a>
#### SR-C19 — Conditioned remainder and deadline

Parent: [C19 — Remaining-session movement and opportunity budget](components/CONTEXT.md); [individual phases](experiments/C.md#c19).

**Definition and interaction.** Define remaining excursions from the current decision price and the actual fixed end. Recondition on the observed prefix and age of upstream forecasts; do not reset a stale horizon or subtract past realized range from a total-range point estimate.

**Comparison.** Compare unconditional, elapsed-time-only and prefix-conditioned remainder models with identical feasible destinations/deadline.

**Local cases to implement.** Early high never revisited; late-session target first reached after cutoff; previously traveled range expands again; only a short remainder of a 60-minute forecast is usable.

<a id="sr-c20"></a>
#### SR-C20 — Filtered regime fit closure

Parent: [C20 — Regime and distribution-shift conditioning](components/CONTEXT.md); [individual phases](experiments/C.md#c20).

**Definition and interaction.** Regime features use permitted contemporaneous measurements and preceding matured residuals, never current downstream forecasts or a smoothed future state. Fit normalization, state model and state-to-head mapping within each upstream training closure.

**Comparison.** Compare continuous axes, filtered discrete/duration state and pooled models, keeping feed-coverage state separately attributable.

**Local cases to implement.** State labels permute after refit; missing-feed regime looks like calm; rare state with one date; current forecast fed back into its own state classifier.

<a id="sr-c21"></a>
#### SR-C21 — Session handoff timing

Parent: [C21 — Session transition and time-dependent path expert](components/CONTEXT.md); [individual phases](experiments/C.md#c21).

**Definition and interaction.** Retain formation end, check interval, actual known completion and trading-date ownership for every source session. Earlier named session is not necessarily complete before the next opening cut; no full-session summary crosses that boundary early.

**Comparison.** Compare known partial versus completed preceding-session state with explicit age and same future end; window shifts count as registered searches.

**Local cases to implement.** Overlapping London/NY definitions; midnight session; shortened day; source event postpones an expected turn; prior session delivered late.

<a id="sr-c22"></a>
#### SR-C22 — Proposal before scoring

Parent: [C22 — Context originator and applicability contract](components/CONTEXT.md); [individual phases](experiments/C.md#c22).

**Definition and interaction.** Create initial Context opportunities from available forecast/state and a bounded stop/target recipe. Current G reach/value/ranking outputs consume those proposals; they cannot be prerequisites for their own birth. A later proposal-refinement pass has a separate acyclic port/version.

**Comparison.** Compare level-only and Context-originated proposal sets, then score the same set to separate generation from selection.

**Local cases to implement.** A source-only opportunity; cyclic proposal→score→proposal; duplicate intents at one cut; missing feasible stop; Context proposal survives absent Response.

<a id="sr-c23"></a>
#### SR-C23 — Parkinson scale and interval support

Parent: [C23 — Parkinson high-low variance specialist](components/CONTEXT.md); [individual phases](experiments/C.md#c23).

**Definition and interaction.** Treat the high-low equation as a completed-interval measurement under its assumptions. Define mean-per-interval versus accumulated variance explicitly; multiplying annualization/display values into intraday targets without a clock model is invalid.

**Comparison.** Compare range information and forecast mapping separately on common interval/coverage cohorts.

**Local cases to implement.** Opening jump outside sampled interval; high equals low; differing interval lengths; incomplete high/low; log-price scaling invariance.

<a id="sr-c24"></a>
#### SR-C24 — Innovation variance versus return-path variance

Parent: [C24 — ARCH/GARCH conditional-variance challenger](components/CONTEXT.md); [individual phases](experiments/C.md#c24).

**Definition and interaction.** State the mean/residual process and distinguish predicted innovation variance, integrated conditional variance and terminal-return variance. Multi-step aggregation must respect modeled serial dependence; missing returns are not zero shocks. Record optimizer/domain failures.

**Comparison.** Compare constrained ARCH/GARCH/asymmetric/tail variants with matched targets and complexity budgets against EWMA/HAR.

**Local cases to implement.** Autoregressive mean creates return covariance; holiday/no observation versus zero residual; near-unit persistence; failed fit; invalid heavy-tail moment parameter.

### Options: 23 contracts

<a id="sr-o01"></a>
#### SR-O01 — Per-operation chain eligibility

Parent: [O01 — Chain assembly, eligibility and coverage accounting](components/OPTIONS.md); [individual phases](experiments/O.md#o01).

**Definition and interaction.** Use separate valuation, signing, OI, exposure and comparison masks. Preserve exact PIT membership and duplicate acquisition lineage; one missing Greek cannot remove a valid gross trade, while an observed trade does not certify all listed wings.

**Comparison.** Compare observed union and fixed comparable intersections without claiming their different populations estimate the same effect.

**Local cases to implement.** Valid trade with no IV; listed but unquoted wing; adjusted contract; duplicate narrow/broad acquisition; current-day list contains a later listing.

<a id="sr-o02"></a>
#### SR-O02 — Identified IV interval and solver error

Parent: [O02 — Option price validation and IV inversion](components/OPTIONS.md); [individual phases](experiments/O.md#o02).

**Definition and interaction.** Separate price admissibility, solver convergence and IV identification. Propagate quote plus underlying/forward/rate/model uncertainty jointly; an intrinsic boundary or zero bid may give one-sided/no IV identification rather than a finite point. Report solver tolerance separately from market uncertainty.

**Comparison.** Compare direct price inversion and interval/scenario inversion with independent pricing references and exercise-aware models.

**Local cases to implement.** Bid below admissible bound; valid ask only; wide bid/ask with perfect solver residual; uncertain underlying; near-zero vega creates unstable IV.

<a id="sr-o03"></a>
#### SR-O03 — Trade condition and correlated sign uncertainty

Parent: [O03 — Options trade-sign uncertainty](components/OPTIONS.md); [individual phases](experiments/O.md#o03).

**Definition and interaction.** Sign only conditions to which the chosen quote comparison applies; auction/late/corrected/package prints retain gross volume but may not support current-BBO aggressor inference. Preserve quote-age, source and shared classifier-error groups.

**Comparison.** Compare quote/tick/unknown scenarios with suitable labelled data only; stress clustered rather than exclusively independent sign errors.

**Local cases to implement.** Many trades signed from one bad quote; late reported print; locked market; corrected aggressor; OPRA labels inferred from unrelated futures must not become truth.

<a id="sr-o04"></a>
#### SR-O04 — Feasible surface domain and quote slack

Parent: [O04 — Arbitrage-aware volatility surface and uncertainty](components/OPTIONS.md); [individual phases](experiments/O.md#o04).

**Definition and interaction.** Record which price intervals can be jointly satisfied by the chosen contract-consistent surface. If quotes are mutually inconsistent, expose minimal/weighted slack, rejected rows and uncertainty instead of claiming exact bid/ask and arbitrage consistency simultaneously. Separate current fit from temporal forecasts.

**Comparison.** Compare local price interpolation, constrained parametric fits and richer representations on held-out prices and downstream uncertainty under matched support.

**Local cases to implement.** Individually plausible but jointly nonconvex quotes; incompatible expiry classes; one bad wing dictates curvature; solver warm start reaches a different solution; unchanged underlying and sparse quotes.

<a id="sr-o05"></a>
#### SR-O05 — Partial derivatives versus total scenario response

Parent: [O05 — Greeks and unit-consistent sensitivities](components/OPTIONS.md); [individual phases](experiments/O.md#o05).

**Definition and interaction.** Each Greek states coordinate, held-fixed variables, volatility/time scale and model. Surface-aware total derivatives are separate from partial Black/tree Greeks. Finite scenario repricing verifies nonlinear behavior; a finite-difference numerical error bar is not economic uncertainty.

**Comparison.** Compare analytic/automatic/numerical partials and full repricing under independently specified sticky/surface scenarios.

**Local cases to implement.** Charm sign under calendar versus remaining time; vanna percent factor; exercise boundary; 0DTE sharp delta change; a surface path alters both IV and forward.

<a id="sr-o06"></a>
#### SR-O06 — Position-interval and publication lineage

Parent: [O06 — Reported OI state and next-report label service](components/OPTIONS.md); [individual phases](experiments/O.md#o06).

**Definition and interaction.** Store OI position interval and knowledge/publication separately. At a newly delivered report, advance the state anchor once; do not retain already covered flow as new inventory evidence. Missing reports and explicit zero reports differ; label revisions follow a frozen policy.

**Comparison.** Compare first-report primary labels and revised-report sensitivity with exact contract/report intervals.

**Local cases to implement.** Delayed report replacing an older anchor; prior flow counted twice; Friday/holiday gap; missing zero row; first-observed archive version is actually a revision.

<a id="sr-o07"></a>
#### SR-O07 — Coherent endpoint distribution

Parent: [O07 — Aggregate next-reported-OI forecast experts](components/OPTIONS.md); [individual phases](experiments/O.md#o07).

**Definition and interaction.** Forecast nonnegative endpoint stock with contract/strike/expiry aggregates reconciled through joint samples. Do not enforce signed-delta volume bounds when gross flow, exercises or adjustments invalidate them. Weight repeated prefix predictions of one endpoint as dependent observations.

**Comparison.** Compare persistence, volume-only, hierarchical/count/distributional and sequence/set methods on identical publication-eligible endpoint labels.

**Local cases to implement.** Many minute prefixes share one report; aggregate quantile differs from sum of marginal quantiles; newly listed option; expiry cohort with no comparable next report.

<a id="sr-o08"></a>
#### SR-O08 — State-anchor flow coverage and assimilation

Parent: [O08 — Intraday aggregate-holdings scenario updater](components/OPTIONS.md); [individual phases](experiments/O.md#o08).

**Definition and interaction.** Any volume-based current-holdings bound must cover all relevant transactions since the report's position interval, not merely since receipt or process start. Gaps add uncertainty. Report updates reconcile already assimilated flow once; O07 forecasts and their underlying flow are not independent observations.

**Comparison.** Compare frozen state, feasible identified intervals and endpoint-trained latent paths; include direct observed-flow forecasting as a challenger.

**Local cases to implement.** Missing pre-receipt morning trades; restart mid-day; delayed report; identical endpoint with different intraday paths; duplicate forecast/flow input narrows uncertainty incorrectly.

<a id="sr-o09"></a>
#### SR-O09 — Local exposure versus finite hedge scenario

Parent: [O09 — Exposure scenarios and concentration boards](components/OPTIONS.md); [individual phases](experiments/O.md#o09).

**Definition and interaction.** The gamma quantity scaled to a 1% move is a local derivative-based sensitivity. A finite 1% move, especially near expiry, requires full option-delta repricing with the stated surface/holdings scenario. Signed ownership remains an assumption; unsigned concentration is observable only conditional on valuation/OI inputs.

**Comparison.** Compare scaled local Greeks, exact finite-shock delta changes and observed-feature direct forecasts without renaming any of them actual dealer hedging.

**Local cases to implement.** 0DTE move across strike saturates delta while local gamma overstates change; sign scenario reversal; multiplier error; zero assumed holdings; simultaneous IV/time/price move.

<a id="sr-o10"></a>
#### SR-O10 — Counterfactual domain for attribution

Parent: [O10 — Mechanical-versus-flow exposure-change decomposition](components/OPTIONS.md); [individual phases](experiments/O.md#o10).

**Definition and interaction.** A factor-order decomposition must define valid revaluation for expiries, listings and missing support at both endpoints. Do not invent a prior quote or zero OI to balance a union. Reconcile comparable economic changes separately from coverage/unknown residuals; factor allocations are conventions.

**Comparison.** Compare fixed-intersection revaluation and full-scope change, with ordered/symmetric attribution only on valid counterfactual states.

**Local cases to implement.** Contract expires between snapshots; new listing with no prior valuation; wing disappears; zero total change with large offsetting factors; factor order requires an invalid expired surface.

<a id="sr-o11"></a>
#### SR-O11 — Node identity under representation changes

Parent: [O11 — Node extraction, width and stable identity](components/OPTIONS.md); [individual phases](experiments/O.md#o11).

**Definition and interaction.** Separate raw strike membership, extraction-version changes, node split/merge and mapped-coordinate movement. Physical support, scenario uncertainty and contact tolerance remain distinct. Grid/smoothing changes cannot masquerade as economic node migration.

**Comparison.** Compare individual strikes and stable clustered objects at matched density, width and support; evaluate identity quality before role-model gains.

**Local cases to implement.** Equal peaks swap rank; smoother joins two nodes; one quote vanishes; same members move in normalized moneyness solely because spot changes; born-after-contact proposal.

<a id="sr-o12"></a>
#### SR-O12 — Economic survival versus observation censoring

Parent: [O12 — Node persistence, migration and thickening/thinning experts](components/OPTIONS.md); [individual phases](experiments/O.md#o12).

**Definition and interaction.** Define survival of members, extraction identity and actionable role separately. Expiry is an economic endpoint; feed/quote loss censors observations; merge/split produces lineage events. Rank and share changes retain denominator attribution.

**Comparison.** Compare static nodes and duration/history models with competing endpoints and censor sensitivity; never train missing-data death as proven unwind.

**Local cases to implement.** Outage deletes a node; expiry removes it; two nodes merge; total board exposure changes with one node constant; physical strike fixed while mapped center moves.

<a id="sr-o13"></a>
#### SR-O13 — Typed topology and scenario semantics

Parent: [O13 — Exposure topology and source pattern grammar](components/OPTIONS.md); [individual phases](experiments/O.md#o13).

**Definition and interaction.** Pattern detectors name the exposure channel, sign assumption, universe and distance order. Opposing signed scenarios are not observed opposing dealers; exposure valleys do not establish thin order-book depth. Forecast ports run after their stated primitive measurements.

**Comparison.** Compare named rule grammar and continuous topology on identical boards with scenario/density controls.

**Local cases to implement.** Same unsigned board under opposite sign scenario; mixed expiry at one strike; small intervening node; no quoted liquidity information in an exposure air pocket.

<a id="sr-o14"></a>
#### SR-O14 — Set identity and masking invariants

Parent: [O14 — Within-chain strike-by-expiry pattern experts](components/OPTIONS.md); [individual phases](experiments/O.md#o14).

**Definition and interaction.** Permutation invariance does not mean duplicate invariance: duplicated acquisitions are errors, while distinct compatible contracts have real additive mass. Preserve absolute price, remaining time, identities and masks; padded tokens cannot contribute to pooling or calibration.

**Comparison.** Compare summaries, per-expiry experts and set/graph/temporal models with the same information, mask patterns and fitted upstream closure.

**Local cases to implement.** Duplicate exact contract; two distinct series share strike; all padding; absent expiry; randomized record order; future temporal token; cardinality change without exposure change.

<a id="sr-o15"></a>
#### SR-O15 — Flow conservation with shared sign error

Parent: [O15 — Signed options contracts and premium-flow ledger](components/OPTIONS.md); [individual phases](experiments/O.md#o15).

**Definition and interaction.** Maintain full eligible trade mass, event corrections and buy/sell/unknown totals independently for contracts and premium. Scenario intervals preserve correlated sign errors and unknown coverage; missing trades cannot be bounded merely by observed unknown-side volume.

**Comparison.** Compare gross and signed constructions on common complete scope; quantify selection bias of notable/top-N print feeds.

**Local cases to implement.** One bad quote signs many prints; correction reverses premium; all signs unknown; top-N cap; missing tape interval; calls and puts with equal premium but different contracts.

<a id="sr-o16"></a>
#### SR-O16 — Frozen weighting and mapping Jacobian

Parent: [O16 — Delta-, gamma-, vega-, vanna- and charm-weighted flow/CVD](components/OPTIONS.md); [individual phases](experiments/O.md#o16).

**Definition and interaction.** Retain the actual Greek snapshot chosen at trade availability, its event-time eligibility and physical units. Event-frozen, arrival-repriced and later-revalued series are separate. Receiver mini-equivalent mapping includes its coordinate Jacobian and uncertainty; changing mapping is not new flow.

**Comparison.** Compare unweighted/Greek-weighted and native/mapped channels with identical prints, preserving within-bar order and each channel's independent tests.

**Local cases to implement.** Late Greek snapshot; 100x vega convention; near-zero mapping slope; a mapping update changes cumulative equivalent without trades; same weighted close with different extrema.

<a id="sr-o17"></a>
#### SR-O17 — Center and band denominator semantics

Parent: [O17 — Exposure-weighted strike center and bands](components/OPTIONS.md); [individual phases](experiments/O.md#o17).

**Definition and interaction.** Compute the magnitude center before rounding and split upper/lower strictly under the chosen equality rule. All-on-one-strike, zero total and absent-side cases have distinct outputs. Opening-envelope samples count valid observed clock intervals, not only changed prices or copied unverified snapshots.

**Comparison.** Compare exact source center/filter/envelope and robust center variants with fixed expiry/support and separately labelled scenario bounds.

**Local cases to implement.** Center lies between ticks; all mass at center; 50% of maximum versus percentile; eight covered unchanged minutes; eight copies spanning an unobserved outage.

<a id="sr-o18"></a>
#### SR-O18 — As-of breadth and exposure denominators

Parent: [O18 — Flow breadth, concentration and OI-relative activity experts](components/OPTIONS.md); [individual phases](experiments/O.md#o18).

**Definition and interaction.** Store eligible/listed/quoted/traded contract denominators separately. Prior same-time volume norms condition on covered duration and known session calendar. Volume/OI, count share and premium share retain distinct interpretations and zero/missing states.

**Comparison.** Compare normalized breadth/concentration versus raw flow under stable and changing universes; partial pooling uses only prior data.

**Local cases to implement.** Broad list arrives later; no OI report versus zero OI; one high-premium print; intraday acquisition gap; short session volume compared with full sessions.

<a id="sr-o19"></a>
#### SR-O19 — Distinct native futures-option capabilities

Parent: [O19 — Futures-options-specific information experts](components/OPTIONS.md); [individual phases](experiments/O.md#o19).

**Definition and interaction.** Use exact underlying future, exercise/payoff and outright/UDS identities. A valid aggressor trade can support flow despite absent option BBO; settlement/trade-implied valuation is explicitly event-specific and uncertain. A daily settlement cannot be a continuously refreshed quoted surface.

**Comparison.** Compare flow-only, published-OI/settlement-only and combined native/OPRA information at matched availability.

**Local cases to implement.** Trade-only strike with no IV; negative spread price; delayed settlement statistic; unknown multiplier sentinel; distinct underlying futures for nearby option expiries.

<a id="sr-o20"></a>
#### SR-O20 — Causal package allocation without duplicated mass

Parent: [O20 — Multi-leg, sweep and large-print ambiguity specialist](components/OPTIONS.md); [individual phases](experiments/O.md#o20).

**Definition and interaction.** A print may have uncertain membership, but each realized grouping scenario allocates its mass once. Later legs revise package hypotheses only at their availability; they cannot relabel the first decision view. Unknown package direction stays a scenario.

**Comparison.** Compare no grouping, documented flags and causal clustering with delayed-completion and coincidental-print controls.

**Local cases to implement.** One print matches two packages; delayed second leg; incomplete ratios; identical size coincidence; grouping changes signed net but not total raw mass.

<a id="sr-o21"></a>
#### SR-O21 — Statistical versus identification uncertainty

Parent: [O21 — Options uncertainty and applicability propagation](components/OPTIONS.md); [individual phases](experiments/O.md#o21).

**Definition and interaction.** Retain separate data/coverage, numerical, sampling, model and latent-identification uncertainty, plus their dependence. A calibrated forecast can be evaluated on observed outcomes; unobserved dealer/current holdings cannot acquire truthful confidence from that calibration.

**Comparison.** Compare point forecasts, coherent joint scenarios and conservative bounds using identical downstream targets and eligibility.

**Local cases to implement.** Common underlying error across all contracts; several independent scenarios incorrectly averaged into confidence; missing wing outside training support; perfect in-sample applicability score.

<a id="sr-o22"></a>
#### SR-O22 — Role targets and proposal lifecycle

Parent: [O22 — Options node/path and actionable-role forecast experts](components/OPTIONS.md); [individual phases](experiments/O.md#o22).

**Definition and interaction.** Define reach, traversal, rebound, continuation and invalidation events explicitly; roles may overlap unless an exclusive outcome partition is declared. New refined entries are new birth-time proposals. Local→cross-asset→joint-refined ports execute once without same-cut feedback.

**Comparison.** Compare direct observed features and holdings-mediated features on the same targets/candidates, then compare proposal-generation changes separately.

**Local cases to implement.** A node is traversed then supports continuation; target and support labels overlap; offset selected after contact; source-only reaction; joint-refined forecast fed back into local ancestor.

<a id="sr-o23"></a>
#### SR-O23 — Complete minimizer and payoff domain

Parent: [O23 — Per-expiry max-pain settlement-payoff benchmark](components/OPTIONS.md); [individual phases](experiments/O.md#o23).

**Definition and interaction.** Return the full minimizer set over the declared valid settlement domain, including flat intervals or the entire domain when OI is zero. Unknown wings imply unknown payoff contributions, not zero contracts. Terminal intrinsic payout remains distinct from holder P&L and earlier American exercise.

**Comparison.** Compare breakpoint slope arithmetic with independent direct payoff sums and fair round-strike/node role baselines.

**Local cases to implement.** Calls-only lower flat region; puts-only upper flat region; zero OI; changed valid price domain; missing wings move minimizer; adjusted deliverable needs a different payoff function.

### Cross-market information: 10 contracts

<a id="sr-x01"></a>
#### SR-X01 — Availability intervals and source cadence

Parent: [X01 — Asynchronous cross-market alignment](components/CROSS_ASSET.md); [individual phases](experiments/X.md#x01).

**Definition and interaction.** Align by usable knowledge, retaining source event interval, last observation, receipt and expected publication cadence. A coarse bar only supports a within-bar event interval; scheduled silence differs from feed failure. Coarsening must not invent event order.

**Comparison.** Compare common-grid and source-triggered decisions at first actionable receiver cuts, with explicit latency and interval-order scenarios.

**Local cases to implement.** ETF bar spans two opposite touches; daily state remains unchanged; next-nearest quote is in future; delayed source event arrives after receiver move.

<a id="sr-x02"></a>
#### SR-X02 — Mapping pushforward and fitted inverse

Parent: [X02 — Related-instrument coordinate and sensitivity mapping](components/CROSS_ASSET.md); [individual phases](experiments/X.md#x02).

**Definition and interaction.** Map geometry and joint uncertainty through the same frozen coordinate model. Distinguish algebraic/Jacobian inverse from a separately fitted conditional reverse regression, which need not equal 1/b. Near-zero slopes or extrapolation invalidate sensitivity conversion; nonlinear bands require scenario pushforward.

**Comparison.** Compare ratio, affine and basis filters using held-out coordinate/interval error relative to candidate width; separate proxy mapping from observed source touch.

**Local cases to implement.** Wide forward interval; inverse regression differs from reciprocal slope; dividend/roll jump; near-zero b; mapped edges reverse order under invalid slope.

<a id="sr-x03"></a>
#### SR-X03 — Nasdaq comparison estimands

Parent: [X03 — Nasdaq-chain comparison and NDX hypothesis](components/CROSS_ASSET.md); [individual phases](experiments/X.md#x03).

**Definition and interaction.** Freeze each chain's eligibility and common-cohort definition before outcome inspection. Report matched-intersection information gain and full-supported deployment value separately; density, available expiries and mapping uncertainty are explicit comparison dimensions.

**Comparison.** Compare futures-only, each Nasdaq chain, pairs and joint information at equal model/search capacity, including no-local-node episodes.

**Local cases to implement.** NDX missing near expiry; NDXP versus monthly settlement; QQQ missing node; quote-quality filter preferentially drops stress days; different candidate counts.

<a id="sr-x04"></a>
#### SR-X04 — S&P information versus execution choice

Parent: [X04 — S&P-chain comparison and fair ES alternative](components/CROSS_ASSET.md); [individual phases](experiments/X.md#x04).

**Definition and interaction.** Separate the value of S&P information for NQ from the choice to execute ES. Use actual one-mini point values/costs/risk-feasible plans, common predeclared dates and independent source-quality masks; missing ES execution data does not remove valid source-only NQ opportunities.

**Comparison.** Compare SPY/SPX/SPXW/native-option contributions and NQ/ES policies as different experiments with distinct estimands.

**Local cases to implement.** Valid SPX signal during an ES replay gap; AM/PM same date; unequal budget-fit opportunity counts; one instrument's unavailable losing day silently excluded.

<a id="sr-x05"></a>
#### SR-X05 — First-actionable transmission episode

Parent: [X05 — Source reaction to receiver opportunity transmission](components/CROSS_ASSET.md); [individual phases](experiments/X.md#x05).

**Definition and interaction.** Freeze the source-event definition, confirmation time, receiver state and residual future horizon at availability. Cluster repeated notifications into source episodes while preserving new information. Common-driver controls must themselves be as-of; predictive increment is not causal proof.

**Comparison.** Compare source level event, source returns and receiver-only models at identical actionable cuts, plus extra-lag and event-time placebos.

**Local cases to implement.** Source already moved and receiver followed; same event emits three alerts; later confirmation changes source event class; contradictory events; minute-order ambiguity.

<a id="sr-x06"></a>
#### SR-X06 — Joint-model fit closure and shared evidence

Parent: [X06 — Joint multi-chain, multi-asset temporal pattern model](components/CROSS_ASSET.md); [individual phases](experiments/X.md#x06).

**Definition and interaction.** All learned encoders, mappings, source heads, imputers and calibrators belong to the joint training closure. Preserve common-shock dependence and actual missingness patterns; attention weights or graph edges alone do not establish contribution or transmission.

**Comparison.** Compare additive versus joint information using same target/cohort/capacity budgets and leave-family/edge/time ablations with full refits.

**Local cases to implement.** One current downstream forecast leaks to its ancestor; duplicated board; entire source absent; graph edge learned on test date; future universe cardinality token.

<a id="sr-x07"></a>
#### SR-X07 — Comparable relative-flow states

Parent: [X07 — Relative strength, cross-flow SMT and lead-lag experts](components/CROSS_ASSET.md); [individual phases](experiments/X.md#x07).

**Definition and interaction.** Define return/flow normalization, reference anchors, beta estimation window and observed lag separately. Do not compare arbitrary cumulative levels across resets or markets. Keep lag estimation causal and distinguish same-market price units from standardized predictive residuals.

**Comparison.** Compare price-only SMT, flow/cohort/OHLC innovations and joint variants with common latency and pair-search budgets.

**Local cases to implement.** Opposite resets create apparent divergence; feed lag creates false lead; beta changes sign; unknown-side cohort; identical CVD close with different path.

<a id="sr-x08"></a>
#### SR-X08 — Proxy, print and constituent boundaries

Parent: [X08 — ETF and constituent-event context](components/CROSS_ASSET.md); [individual phases](experiments/X.md#x08).

**Definition and interaction.** ETF relative behavior is a proxy, not observed constituent breadth. TRF unsigned receipt-time information, constituent-weighted breadth and earnings surprise retain independent acquisition/identity/publication gates. Corrected prints revise state only when received.

**Comparison.** Compare ETF price/volume, known-event, later certified constituent and TRF channels separately before fusion.

**Local cases to implement.** ETF volume assigned a fictional aggressor; current constituents used historically; delayed/cancelled TRF print; later top-print rank; earnings timestamp uncertain.

<a id="sr-x09"></a>
#### SR-X09 — Native units and global-session support

Parent: [X09 — Global futures, currency and commodity transmission](components/CROSS_ASSET.md); [individual phases](experiments/X.md#x09).

**Definition and interaction.** Each child retains native economic units, currency direction, contract grade/multiplier, actual cadence and calendar. Related-market spread proxies do not imply an arbitrage identity. Shared features do not remove independent per-child target/horizon scores.

**Comparison.** Compare each global source and currency contribution separately and jointly with receiver-only/common-driver controls.

**Local cases to implement.** Japan holiday during US session; inverse FX quote; copper weight/currency mismatch; daily yield treated as intraday tick; commodity roll creates false stress.

<a id="sr-x10"></a>
#### SR-X10 — Report vintage and effective observations

Parent: [X10 — Slow positioning, inventories and fund-flow context](components/CROSS_ASSET.md); [individual phases](experiments/X.md#x10).

**Definition and interaction.** Keep methodology/version, observation interval, first available publication and revisions. Report-level state changes cannot be interpreted as market changes when units/scope changed. Repeated minute use of one release does not create independent report evidence.

**Comparison.** Compare level/change/age and each slow-source addition using report- and date-dependent uncertainty and verified publication cohorts.

**Local cases to implement.** One weekly report repeated thousands of times; delayed holiday release; revised history; unit/methodology break; missing release mistaken for zero change.

### Locations: 19 contracts

<a id="sr-l01"></a>
#### SR-L01 — Provisional and frozen internal geometry

Parent: [L01 — Internal range quarters, EQ and range-open locations](components/LOCATION.md); [individual phases](experiments/L.md#l01).

**Definition and interaction.** Each quarter/EQ/open object retains the exact range version and whether it is provisional. A changed forming range creates a changed candidate; labels keep their birth geometry. Coincident open/EQ prices retain provenance without becoming duplicate economic actions.

**Comparison.** Compare internal object types and roles with a fixed scorer, then role models on the same objects and matched grid controls.

**Local cases to implement.** Open equals EQ; zero-width range; later forming high moves EQ after contact; two anchors yield same price; internal continuation without gamma.

<a id="sr-l02"></a>
#### SR-L02 — Projection coordinate and contact outcome

Parent: [L02 — Range edges and edge-relative extensions](components/LOCATION.md); [individual phases](experiments/L.md#l02).

**Definition and interaction.** Store edge-relative k and normalized range position separately, preserving exact source grids before rounding. Traded contact, gap crossing, partial retrace and later continuation are distinct outcomes; a far no-reach candidate remains in coverage accounting.

**Comparison.** Compare fixed projections and learned excursion-derived proposals with density/distance/width controlled before whole-policy comparison.

**Local cases to implement.** W100 upper edge+133 versus x=1.33; mirrored lower region; jump across a band; contact followed by continuation; multiple ratios round to one tick.

<a id="sr-l03"></a>
#### SR-L03 — Prior-session reference interpretation

Parent: [L03 — Previous-RTH and full-session structure](components/LOCATION.md); [individual phases](experiments/L.md#l03).

**Definition and interaction.** Keep RTH-only source freshness and ETH-aware challenger as separate states on the same prior reference. A roll/price bridge or source revision creates explicit new mapping/version; prior old-contract extremes are not silently current-contract prices.

**Comparison.** Compare source anchor and sweep rules independently from added prior-value/delta information.

**Local cases to implement.** ETH sweep followed by RTH trade; prior RTH incomplete on holiday; current 6–9 high confused with prior high; roll changes coordinate; late prior correction.

<a id="sr-l04"></a>
#### SR-L04 — Statistical zone estimand and uncertainty

Parent: [L04 — Statistical bounds and improved P-zones](components/LOCATION.md); [individual phases](experiments/L.md#l04).

**Definition and interaction.** Separate forecast quantile/mode, geometric candidate support, statistical estimation uncertainty, mapping uncertainty and contact tolerance. A zero-excursion mass may imply no travel rather than a new profitable level. Snapping creates an explicit changed proposal and label geometry.

**Comparison.** Compare free, snapped and soft-node-distance statistical proposals at matched count/width; then compare fixed candidate role scoring.

**Local cases to implement.** Several quantiles collapse to current price; broad band inflates touch rate; mode of max differs from reversal price; snap crosses side; wrong anchor at a later cut.

<a id="sr-l05"></a>
#### SR-L05 — Profile feature and role separation

Parent: [L05 — Volume-profile value, nodes, shelves and valleys](components/LOCATION.md); [individual phases](experiments/L.md#l05).

**Definition and interaction.** Represent tied POCs, shelves, valleys and multimodal separators with explicit membership/prominence and anchor. Historic low volume is not current thin depth. Grid/smoothing changes are representation effects, not new auction events.

**Comparison.** Compare every profile-location type against POC/VA-only and matched-grid controls, holding scoring fixed before model changes.

**Local cases to implement.** POC plateau; valley filled by later trades; unchanged profile under grid-phase shift; same price from different anchors; boundary moves after entry.

<a id="sr-l06"></a>
#### SR-L06 — Side concentration and observed protection

Parent: [L06 — Delta-profile and side-concentration locations](components/LOCATION.md); [individual phases](experiments/L.md#l06).

**Definition and interaction.** Generate side/contrast geometry from explicit buy/sell/unknown channels without destroying opposing mass by net cancellation. Protection/reward is a later observed state; it cannot select which initial shelf was born. Missing signed tape may retain total-volume geometry only.

**Comparison.** Compare total profile, signed contrast and cohort-side locations at identical anchors, with clustered sign/coverage perturbations.

**Local cases to implement.** Net delta zero but strong two-sided activity; high positive delta loses; unknown-heavy wing; later reward backdates shelf; opposing shelves share price.

<a id="sr-l07"></a>
#### SR-L07 — TPO qualification and birth history

Parent: [L07 — TPO, initial balance, single prints and auction tails](components/LOCATION.md); [individual phases](experiments/L.md#l07).

**Definition and interaction.** Single prints/tails/poor extremes have provisional and final qualification times. Keep bracket visitation separate from continuous dwell and traded volume; a candle gap does not fill every intermediate TPO row. Naked/unfilled history states their observation interval.

**Comparison.** Compare source bracket/IB objects, exact dwell and volume alternatives with identical eligibility and visit definitions.

**Local cases to implement.** Single print filled before final qualification; same bracket revisits one row; missing bracket; weekly holiday IB; next-open gap crosses prior POC without trade.

<a id="sr-l08"></a>
#### SR-L08 — Leg confirmation and geometry revisions

Parent: [L08 — Swing, retracement and dynamic-range locations](components/LOCATION.md); [individual phases](experiments/L.md#l08).

**Definition and interaction.** Keep pivot event, confirmation, running leg and replacement as distinct records. Reversal thresholds fixed at leg birth or explicitly versioned cannot confirm a swing solely because a volatility estimate fell. Model confirmation cost at the actual actionable price.

**Comparison.** Compare fixed pivot, tick/vol reversal and provisional legs with matched age/delay/geometry controls.

**Local cases to implement.** Equal highs; no reversal in a trend; changing volatility threshold without price movement; nested legs; later confirmation backplotted at old extreme.

<a id="sr-l09"></a>
#### SR-L09 — Price-gap versus traded-imbalance definition

Parent: [L09 — FVG, imbalance and displacement-origin zones](components/LOCATION.md); [individual phases](experiments/L.md#l09).

**Definition and interaction.** A three-bar wick/body gap is price geometry, not proof no trades occurred there during bar two. Measured volume imbalance requires tape. Formation/mitigation/inversion rules use exact completed bar IDs and known times; partial-bar variants are separate.

**Comparison.** Compare disclosed wick/body structures and actual footprint imbalance with similar price size/age and density controls.

**Local cases to implement.** Bar two trades through the future FVG zone; identical consecutive HTF bars; zone fills before confirmation becomes available; future wick; missing trade coverage.

<a id="sr-l10"></a>
#### SR-L10 — Source geometry alternatives and shared identity

Parent: [L10 — Order-block and rejection-block entry regions](components/LOCATION.md); [individual phases](experiments/L.md#l10).

**Definition and interaction.** Retain each explicitly disclosed sweep/close rule and the separately named full-range/body/wick interpretations where drawing bounds are unresolved. Geometry, entry timing and stop choice are independent factors; the same L10/R18 source event is shared lineage.

**Comparison.** Compare source variants and simple confirmation with actual post-confirmation entry/non-fill economics, without choosing the winning geometry afterward.

**Local cases to implement.** Third candle late; midpoint stop already invalid at entry; no midpoint retracement; body/wick disagreement; same event counted as two independent confirmations.

<a id="sr-l11"></a>
#### SR-L11 — Descriptive dispersion versus forecast interval

Parent: [L11 — VWAP and anchored-dispersion locations](components/LOCATION.md); [individual phases](experiments/L.md#l11).

**Definition and interaction.** VWAP dispersion is weighted historical price spread under a named anchor, not automatically a confidence interval or future coverage claim. Frozen targets and explicitly tracking VWAP policies have different label/management definitions.

**Comparison.** Compare exact/proxy VWAP, robust bands and contextual roles with fixed anchor and feasible moving-target policies.

**Local cases to implement.** Reset changes line; unchanged covered prices; moving VWAP turns a prior miss into a hit in a faulty labeler; borrowed index volume; two-SD band mislabeled 95% future probability.

<a id="sr-l12"></a>
#### SR-L12 — Reference publication and price meaning

Parent: [L12 — Opens, settlement, gaps and reference-price locations](components/LOCATION.md); [individual phases](experiments/L.md#l12).

**Definition and interaction.** Official settlement, last trade, first observed trade, verified session open and corporate-action/roll-adjusted reference are distinct. TRF objects begin at receipt with unsigned provenance and known correction lineage; unknown mapping cannot create an exact receiver price.

**Comparison.** Compare reference types/fractions/clock windows and eligible print-derived objects against simple prior-price/round-number controls.

**Local cases to implement.** Late settlement; first archive row is not true session open; print correction; opening gap without traded contact; prior date carried under today's name.

<a id="sr-l13"></a>
#### SR-L13 — Mapped-node versions and source observability

Parent: [L13 — Options concentration nodes mapped to execution](components/LOCATION.md); [individual phases](experiments/L.md#l13).

**Definition and interaction.** Retain source node and mapping versions independently. Mapping drift can move the receiver band without source node change; uncertainty does not establish true cash-index contact. Keep support/uncertainty/tolerance separate and preserve no-reach versions.

**Comparison.** Compare each chain/dynamics/holdings feature and mapped versus source-event information at matched width/density and source coverage.

**Local cases to implement.** NDXP/QQQ disagree; mapping changes after entry; missing wing; tiny source node; physically unchanged strike moves in receiver coordinates; large uncertainty makes plan infeasible.

<a id="sr-l14"></a>
#### SR-L14 — Composite corridor identity and role

Parent: [L14 — Exposure centers, bands and topology corridors](components/LOCATION.md); [individual phases](experiments/L.md#l14).

**Definition and interaction.** Keep each corridor's ordered member nodes and interval versus endpoint role. A wide corridor already containing price is not evidence of predictive reach. Exposure centers, max-pain minimizers and arithmetic midpoints retain distinct formulas and shared-evidence lineage.

**Comparison.** Compare composite objects with constituent nodes alone using matched count/width and separate contact/destination targets.

**Local cases to implement.** Current price inside broad corridor; empty side; minimizer is an interval; expiry filter changes all members; duplicate node and corridor votes.

<a id="sr-l15"></a>
#### SR-L15 — Receiver proposal at source availability

Parent: [L15 — Source-event receiver opportunities without local touch](components/LOCATION.md); [individual phases](experiments/L.md#l15).

**Definition and interaction.** Start reward and geometry at the receiver's first actionable cut after source confirmation. Source failure is a prospective cancellation/management event, not hindsight removal of a losing opportunity. Feasible receiver protection exists independently of local node presence.

**Comparison.** Compare immediate, pullback and confirmation policies from the same source episodes, including already-consumed movement and non-fills.

**Local cases to implement.** Source signal arrives after receiver turn; source later fails; receiver has no node; current receiver spread widens; contradictory source triggers; no valid stop.

<a id="sr-l16"></a>
#### SR-L16 — Proposal budget and two-stage comparison

Parent: [L16 — Learned location proposal and bounded price refinement](components/LOCATION.md); [individual phases](experiments/L.md#l16).

**Definition and interaction.** Freeze spatial domain, grid, width/count and generation time; candidate offsets outside allowed neighborhoods become separately identified proposals. Proposal selection and downstream scoring form an acyclic sequence. Future outcomes supervise training only, never choose current realized geometry.

**Comparison.** First compare generators under a common fixed scorer and matched opportunity budget; then compare scorers on common frozen proposals; finally refit whole policies.

**Local cases to implement.** Every tick proposed to inflate coverage; all peaks round to one action; offset changes after scoring; no-reach grid cells omitted; outer-day optimum leaks into proposal.

<a id="sr-l17"></a>
#### SR-L17 — Observed lifecycle versus learned retirement

Parent: [L17 — Location lifecycle, retest and invalidation hazard](components/LOCATION.md); [individual phases](experiments/L.md#l17).

**Definition and interaction.** Store observed touches, geometric invalidation, economic expiry and data loss independently from a policy's decision to retire. Retirement does not delete the object's history or exempt its rejected opportunities from a comparison; repeated visits retain a stable episode identity.

**Comparison.** Compare deterministic TTL/first-touch rules and learned hazards on full initial populations, accounting for selective later retests and censoring.

**Local cases to implement.** Retired level later reacts; feed loss treated as failure; small revision resets visits; sweep/reclaim after invalidation; two contacts without leaving band.

<a id="sr-l18"></a>
#### SR-L18 — Provenance groups and equivalent actions

Parent: [L18 — Correlated objects, provenance groups and candidate-set assembly](components/LOCATION.md); [individual phases](experiments/L.md#l18).

**Definition and interaction.** Separate shared-source lineage, overlapping geometry and empirically correlated forecasts. Transitive geometric overlap is not proof all members are one independent signal. Deduplicate economically identical action plans without discarding distinct evidence or alternate feasible plans.

**Comparison.** Compare complete lists, deterministic grouping and learned set aggregation; use duplication-invariance and count/width controls with full rejected-candidate accounting.

**Local cases to implement.** A overlaps B and B overlaps C but A/C differ; POC and VWAP share trades; two expiries share strike; identical orders from different objects; active-set overflow.

<a id="sr-l19"></a>
#### SR-L19 — Origin versus later rewarded memory

Parent: [L19 — Large-print, origin-of-move and aggression-memory locations](components/LOCATION.md); [individual phases](experiments/L.md#l19).

**Definition and interaction.** Birth all eligible causal aggression/origin clusters at their actual formation time. Later reward/protection adds a new state/version; it cannot retrospectively make only winning clusters eligible. Source size filters are proxies with native units, not participant labels.

**Comparison.** Compare raw origins, price-only clusters and later observed flow-memory states with delay/size/density/sign controls.

**Local cases to implement.** Largest print receives no reward; small cluster precedes move; later protected state; opposite side unknown; old idea relabeled to bypass cumulative risk.

### Mixtures and selection: 10 contracts

<a id="sr-g01"></a>
#### SR-G01 — Evidence diversity and duplicate experts

Parent: [G01 — Target-specific Context and path mixtures](components/GATES_AND_SELECTION.md); [individual phases](experiments/G.md#g01).

**Definition and interaction.** Track shared inputs, fitted ancestors and duplicate predictions as evidence groups. Duplicating an equivalent expert must not be presented as additional independent support; calibrate the complete selected mixture and missingness policy.

**Comparison.** Compare a matched-input joint model, independent heads, grouped mixtures and a simple single expert; inspect residual diversity and clone sensitivity.

**Local cases to implement.** Clone one expert under several IDs; identical means with different tail distributions; a group disappears; gate trained on the same labels as its upstream calibrator.

<a id="sr-g02"></a>
#### SR-G02 — Variance and horizon estimand identity

Parent: [G02 — Rich volatility and excursion ensembles](components/GATES_AND_SELECTION.md); [individual phases](experiments/G.md#g02).

**Definition and interaction.** Distinguish integrated/realized variance targets from variance of terminal return, and variance of price changes from log returns. Each port names sampling, clock and horizon; aggregation/rescaling requires the stated mathematical relationship.

**Comparison.** Compare horizon-specific forecasts and explicit aggregation models; evaluate coherent excursion/path heads separately from variance-only accuracy.

**Local cases to implement.** Annualized IV mixed with raw squared ticks; summing terminal-return variances while ignoring dependence; session remainder changes; crossed quantiles after transformation.

<a id="sr-g03"></a>
#### SR-G03 — Calibration through the whole fitted chain

Parent: [G03 — Forecast calibration and uncertainty service](components/GATES_AND_SELECTION.md); [individual phases](experiments/G.md#g03).

**Definition and interaction.** Treat calibrators and learned coherence corrections as fitted dependencies in the OOF graph. Reassess calibration after any change to expert weights, support gate, target or monotonicity transformation; local calibration does not automatically survive selection.

**Comparison.** Compare identity, pooled and conditional transforms on separate chronological roles, including reliability after the actual policy's selection.

**Local cases to implement.** Calibrator sees the downstream training label; coherence repair changes tail coverage; constant forecasts; rare cohort overfit; good unconditional reliability with bad selected-subset reliability.

<a id="sr-g04"></a>
#### SR-G04 — Overlap-aware reach event algebra

Parent: [G04 — Level reach and first-passage expert](components/GATES_AND_SELECTION.md); [individual phases](experiments/G.md#g04).

**Definition and interaction.** Define whether first contact is to individual objects, disjoint spatial regions or co-contact sets. Overlapping objects can be touched together, so their marginal probabilities are not a categorical partition. CDF monotonicity applies to the same frozen object and cut.

**Comparison.** Compare independent marginal heads and a coherent arrival/region model with complete candidate geometry, explicit gap events and no-contact probability.

**Local cases to implement.** Two identical bands; nested bands crossed by a price gap; overlapping bands with simultaneous contact; a shorter-horizon reach probability above a longer-horizon probability.

<a id="sr-g05"></a>
#### SR-G05 — Arrival-conditioned path coherence

Parent: [G05 — Conditional departure, continuation and runner-quality experts](components/GATES_AND_SELECTION.md); [individual phases](experiments/G.md#g05).

**Definition and interaction.** The target registry states which outcomes are exclusive, nested or overlapping. Pre-contact integration includes arrival time/state and the remaining fixed-end window; post-contact heads have their own information set and cannot replace earlier forecasts retrospectively.

**Comparison.** Compare direct joint reach/departure prediction, correctly factored conditional models and arrival-state integration; verify both conditional and unconditional calibration.

**Local cases to implement.** Runner after a partial retrace; contact just before horizon end; a current-inside object; future arrival features accidentally supplied at the earlier cut.

<a id="sr-g06"></a>
#### SR-G06 — Value uncertainty after action search

Parent: [G06 — Executable action-value and cost model](components/GATES_AND_SELECTION.md); [individual phases](experiments/G.md#g06).

**Definition and interaction.** Separate future payoff dispersion, parameter uncertainty and scenario uncertainty in the value output. The chosen maximum across many actions needs selection-aware evaluation; a per-action lower bound is not automatically a simultaneous guarantee.

**Comparison.** Compare expected-value and prespecified conservative policies on the same complete action grid with jointly paired uncertainty and calibrated net outcomes.

**Local cases to implement.** Adding many noisy action variants creates a false winner; identical gross P&L with different costs; duplicated plans; uncertainty collapses when adverse fill/markout dependence is ignored.

<a id="sr-g07"></a>
#### SR-G07 — Planner support and transition error

Parent: [G07 — Value of waiting, deeper levels and additional information](components/GATES_AND_SELECTION.md); [individual phases](experiments/G.md#g07).

**Definition and interaction.** Declare finite planning states, event/time resolution and the prospective object-arrival model. Continuation can depend on future observations only through a trained transition distribution; it cannot query the replay's actual future candidate set. Carry planning uncertainty and occupancy.

**Comparison.** Compare shallow reference trees, act/wait rules and fitted continuation at matched actions; increase depth only if transition-error stress and complete-policy evidence improve.

**Local cases to implement.** A future object known only from the completed replay; deeper planning amplifies small optimistic bias; pending cancellation occupies the action state; no valid continuation model.

<a id="sr-g08"></a>
#### SR-G08 — Economic action identity and stable selection

Parent: [G08 — Candidate ranking and constrained action selection](components/GATES_AND_SELECTION.md); [individual phases](experiments/G.md#g08).

**Definition and interaction.** Deduplicate equivalent executable plans while retaining all source-object provenance. Ranking two descriptions of the same order is not two opportunities. Freeze tie behavior and record rejected alternatives including those displaced by an occupied position.

**Comparison.** Compare pointwise, pairwise and set selection on identical unique plans; report sensitivity to candidate density and correlated proposal families.

**Local cases to implement.** Candidate order permutation; duplicated source labels; equal values at numerical tolerance; best-ranked plan becomes infeasible before dispatch; many near-identical stops.

<a id="sr-g09"></a>
#### SR-G09 — Eligibility versus statistical abstention

Parent: [G09 — Applicability, disagreement and abstention gate](components/GATES_AND_SELECTION.md); [individual phases](experiments/G.md#g09).

**Definition and interaction.** Keep deterministic invalidity, unsupported model domain and discretionary uncertainty abstention as separate reasons. Report selection coverage by time/day and by opportunity population, including flat days and opportunities consumed by earlier trades.

**Comparison.** Compare support thresholds using the joint risk/coverage/net frontier and reliability of the selected subset, with thresholds fixed before confirmation.

**Local cases to implement.** High apparent accuracy from rejecting almost all activity; a data outage confused with low confidence; a rare supported event versus an unseen mask; denominator changes after threshold tuning.

<a id="sr-g10"></a>
#### SR-G10 — Atomic model-version compatibility

Parent: [G10 — Per-expert adaptation, recalibration and retirement policy](components/GATES_AND_SELECTION.md); [individual phases](experiments/G.md#g10).

**Definition and interaction.** An upstream update carries a compatibility manifest for scalers, calibrators, gates and continuation models. Refit/revalidate affected dependents or retain the preceding complete compatible bundle; do not mix versions because individual files load successfully.

**Comparison.** Compare frozen bundles, scheduled bundle changes and prespecified granular updates including their recalibration, downtime and compute costs.

**Local cases to implement.** New expert with old gate calibration; update while an inference is pending; rollback after changed feature schema; late labels would change a past update decision.

### Policy, execution and risk: 12 contracts

<a id="sr-p01"></a>
#### SR-P01 — Intent version and asynchronous exposure

Parent: [P01 — Action state and complete sequential policy](components/POLICY_EXECUTION_RISK.md); [individual phases](experiments/P.md#p01).

**Definition and interaction.** Bind every action to current account/market/proposal versions and an expiry; risk reservation and submit authorization are atomic. Pending, unknown and contingent orders are included in feasible race states. Record real fault-induced excess exposure rather than assuming the desired position invariant makes it impossible.

**Comparison.** Compare deterministic reducer/reference and learned selection using the same lawful action set and full occupancy/day paths.

**Local cases to implement.** Two approvals race; fill after cancel request; stale intent; unknown position; opposite signal while held; broker fault creates extra exposure requiring resolution.

<a id="sr-p02"></a>
#### SR-P02 — Rounded geometry after feasible entry

Parent: [P02 — Structural stop and full-position destination choice](components/POLICY_EXECUTION_RISK.md); [individual phases](experiments/P.md#p02).

**Definition and interaction.** Round stops/targets under explicit side/conservative rules and recompute USD geometry with the actual entry/fill and fees. A logical stop cannot be silently moved to fit the mini. Entry slippage beyond the reserved geometry triggers defined risk handling.

**Comparison.** Compare fixed, structural and forecast-based brackets with the same entry opportunities and separate stop/target factors.

**Local cases to implement.** Stop rounds inside spread; target behind entry; slippage invalidates reserved plan; changing tick definition; same raw targets round identically; mapping width exceeds budget.

<a id="sr-p03"></a>
#### SR-P03 — Management policy occupancy and labels

Parent: [P03 — Full-position exits, protected structure and trailing value](components/POLICY_EXECUTION_RISK.md); [individual phases](experiments/P.md#p03).

**Definition and interaction.** Value hold/exit/stop/target amendments from current executable liquidation state to the fixed remaining end. Separate realized-trade MFE/MAE from fixed-horizon diagnostic excursions. Entry-price protection still has fees/gap risk; amendments preserve prior protection until verified replacement under broker semantics.

**Comparison.** Compare exit and target changes independently on common entry paths, then replay each complete policy with its changed occupation/risk state.

**Local cases to implement.** Unfilled target amendment; cancel/replace race; backdated swing; target extension consumes later opportunity; early-exit policy tested only on eventual winners.

<a id="sr-p04"></a>
#### SR-P04 — Idea lineage and risk attribution

Parent: [P04 — Re-entry, idea memory and cumulative risk](components/POLICY_EXECUTION_RISK.md); [individual phases](experiments/P.md#p04).

**Definition and interaction.** Preserve cumulative gross losses, net idea P&L and open/pending incremental risk as distinct quantities under a frozen idea-budget rule. Renames/splits/merges and correlated aliases cannot reset loss history; allocate each fill once with shared-risk references.

**Comparison.** Compare no retry, fixed retry limits and evidence-conditioned retries from the same original ideas/days, including paths without later visits.

**Local cases to implement.** Two aliases retry same thesis; merge after a loss; profitable earlier retry versus gross-loss budget; immediate new quote is not new evidence; daily halt prevents recovery.

<a id="sr-p05"></a>
#### SR-P05 — Executable outcomes under declared uncertainty

Parent: [P05 — Event replay and passive-fill uncertainty](components/POLICY_EXECUTION_RISK.md); [individual phases](experiments/P.md#p05).

**Definition and interaction.** Venue-outcome replay and strategy knowledge remain separate. Standing valid BBO can fill a marketable unit at arrival under depth/impact assumptions. Touch, trade-through and queue models are scenario-conditioned evidence, not universally ordered guaranteed fill truths; quote-only shadow does not identify passive queue rank.

**Comparison.** Compare marketable and passive/wait policies on common ex-ante opportunities under plausible joint latency/fill/cost scenarios.

**Local cases to implement.** No print at touched limit; one-level depth insufficient after adverse move; venue quote unseen locally; auction transition; gap/stop-limit non-fill; same-time ambiguous order.

<a id="sr-p06"></a>
#### SR-P06 — Cost benchmark and joint fill distribution

Parent: [P06 — Routing, latency, cost and adverse-selection experts](components/POLICY_EXECUTION_RISK.md); [individual phases](experiments/P.md#p06).

**Definition and interaction.** Define decision benchmark, arrival benchmark, actual fills and markout horizons. Spread/latency/impact are attribution terms within shortfall, not extra charges on already side-correct fills. Model fill, execution price and adverse markout jointly where dependent; filled-only samples do not evaluate routing policy.

**Comparison.** Compare fixed costs and calibrated conditional distributions with all sent/cancelled/rejected/non-filled actions and stressed end-to-end paths.

**Local cases to implement.** Entry at ask and exit at bid plus an erroneous extra spread; favorable price improvement; high fill probability selects toxic states; cancel after fill; changing fees.

<a id="sr-p07"></a>
#### SR-P07 — Event reducer and snapshot reconciliation

Parent: [P07 — Broker order state, idempotency and reconciliation](components/POLICY_EXECUTION_RISK.md); [individual phases](experiments/P.md#p07).

**Definition and interaction.** Order states are a reducer over durable IDs/revisions, not an assumed ordered message list. Reconcile broker snapshot as-of with subsequent events; a stale snapshot cannot erase a known fill. Timeout/unknown is unresolved exposure, and OCO cancellation needs actual semantics.

**Comparison.** Compare reference reducer across event permutations allowed by the source contract, restart and duplicate delivery; learned anomaly detection cannot mutate exact state.

**Local cases to implement.** Fill-before-ack; late working snapshot after fill; duplicate execution ID; disconnect after submit; sibling fill race; legitimate execution correction.

<a id="sr-p08"></a>
#### SR-P08 — Independent mark-to-stop reserve

Parent: [P08 — Independent daily USD risk and pre-trade reservations](components/POLICY_EXECUTION_RISK.md); [individual phases](experiments/P.md#p08).

**Definition and interaction.** Compute day-start net headroom, current liquidation mark and incremental adverse reserve without double counting open losses or paid fees. Enumerate pending-order races jointly; finite stress reserves are not an absolute bound on market gaps. Trading and business cash adjustments retain distinct effects.

**Comparison.** Compare exact reference risk paths and conservative reserve/budget policies under the same hard user ceiling.

**Local cases to implement.** Two concurrent intents; open loss counted twice; unfilled profit counted as headroom; withdrawal; profit then giveback; gap exceeds reserve; fee currency rounding.

<a id="sr-p09"></a>
#### SR-P09 — Versioned account rules and transitions

Parent: [P09 — Firm product and account lifecycle constraints](components/POLICY_EXECUTION_RISK.md); [individual phases](experiments/P.md#p09).

**Definition and interaction.** Record effective product/terms/date, calendar, floor-update clock and payout/fee state explicitly. Rule interpretation is deterministic under that version; unresolved active terms block only dependent account/deployment certification, not unrelated model research.

**Comparison.** Compare hand-calculated lifecycle paths and declared product scenarios without tuning rules to make the strategy pass.

**Local cases to implement.** EOD floor with intraday enforcement; payout pending; locked floor; rule revision; fee changes consistency denominator; broker-specific cutoff conflict.

<a id="sr-p10"></a>
#### SR-P10 — Independent timers and flat confirmation

Parent: [P10 — Day boundary, outage and emergency flattening](components/POLICY_EXECUTION_RISK.md); [individual phases](experiments/P.md#p10).

**Definition and interaction.** Schedule boundary/risk timers independently of incoming ticks, with UTC/calendar versions and monotonic duration tracking. Confirm flat only against reconciled position and all residual entry/contingent orders; a stale empty snapshot is insufficient. A market closure/outage remains an explicit unresolved outcome.

**Comparison.** Compare fixed and empirically justified buffers through deterministic reachable faults and actual future telemetry when available.

**Local cases to implement.** No market tick near cutoff; clock adjustment; rejected close; late entry fill after cancel; restart while flattening; venue closed; stale broker flat snapshot.

<a id="sr-p11"></a>
#### SR-P11 — Eligible-day and cash conservation

Parent: [P11 — Trading net, business cash and objective accounting](components/POLICY_EXECUTION_RISK.md); [individual phases](experiments/P.md#p11).

**Definition and interaction.** Freeze eligible-day membership before results and keep future outages/flat days in the operational denominator. Separate trading P&L, deposits/withdrawals, received cash, pending entitlements and all paid business costs. Every ledger entry has one ownership/date rule.

**Comparison.** Compare independent cash/position/fee reconstructions and accounting scenarios; no learned substitute for arithmetic.

**Local cases to implement.** Withdrawal double-counted as loss; pending payout counted received; failed evaluation fees omitted; reset across midnight; fee charged twice; missing market day removed after loss.

<a id="sr-p12"></a>
#### SR-P12 — Instrument choice as registered selection

Parent: [P12 — Execution-instrument research selection](components/POLICY_EXECUTION_RISK.md); [individual phases](experiments/P.md#p12).

**Definition and interaction.** Compare actual one-mini feasible policies with native point values, costs and risk budgets; do not force equal trade counts that hide an instrument's budget-fit differences. Freeze preference margin and selection before outer/future evidence; trial history includes selection.

**Comparison.** Compare fixed NQ, fixed ES and development-selected policy on common dates, with wider supported cohorts separately reported.

**Local cases to implement.** Different data dates; larger NQ tick changes feasible stops; preference under wide uncertainty; hindsight daily switching; overlapping holdings during contract/instrument change.

### Later Response: 22 contracts

<a id="sr-r01"></a>
#### SR-R01 — Frozen approach episode

Parent: [R01 — Approach speed, aggression and progress](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r01).

**Definition and interaction.** Define outer-band start, inward direction, departure/reset and time origin against a fixed object version. Quote motion and executed-trade progress are distinct inputs; no-contact and censored approaches remain valid outcomes.

**Comparison.** Compare speed/effort/acceleration representations and prefix actions with common initial approach episodes.

**Local cases to implement.** Zero elapsed time; band moves around stationary price; quote-only drift; delayed trade; approach reverses before contact; reset during a feed gap.

<a id="sr-r02"></a>
#### SR-R02 — Stall detection versus subsequent reversal

Parent: [R02 — High-effort stall and absorption proxy](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r02).

**Definition and interaction.** High effort and limited progress belong to a completed as-of observation window; later opposite movement is a target/transition. Preserve print-only, at-touch-book and coverage-uncertain evidence separately, with own/source-side orientation.

**Comparison.** Compare simple price stall, effort-conditioned stall and book/cohort additions at identical detection cuts and natural base rates.

**Local cases to implement.** Large volume with efficient continuation; same effort from many prints; unsigned flow; reversal occurs before delayed detection; stall window grows after outcome.

<a id="sr-r03"></a>
#### SR-R03 — Causal push segmentation and observed quiet

Parent: [R03 — Diminishing-effort exhaustion](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r03).

**Definition and interaction.** Push start/end and confirmation latency are versioned. Declining eligible activity requires covered observation and all relevant size cohorts; no prints in a filtered display is not inactivity. Quiet efficient price movement differs from exhaustion.

**Comparison.** Compare rate/size/efficiency decay and confirmed-push structure with simple price deceleration and common prefixes.

**Local cases to implement.** Unseen large-size cohort; no-trade quote drift; confirmed swing arrives late; feed outage; declining volume but increasing progress per contract.

<a id="sr-r04"></a>
#### SR-R04 — Burst event and limited-extension window

Parent: [R04 — Stopping burst and climax hypothesis](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r04).

**Definition and interaction.** A burst's extremeness threshold, grouping and completed extension window are fixed causal definitions. Late aggregate/corrected prints and source batching are separate from contemporaneous bursts. Future turning price cannot pick the detection event.

**Comparison.** Compare continuous effort/stall and extreme-tail flags/models under equal information and event-weighted support.

**Local cases to implement.** One late summary print; many adjacent bursts; burst followed by stronger continuation; current tail norm includes burst; window selected to stop at reversal.

<a id="sr-r05"></a>
#### SR-R05 — Displayed-state recovery bounds

Parent: [R05 — At-touch replenishment and resilience sequence](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r05).

**Definition and interaction.** At-touch net recovery uses a known unchanged best-price episode and normalized execution semantics. Price loss ends that episode; reappearance is a new observed state unless identity exists. Size recovery does not identify gross adds/cancels, reserve inventory or the same defender.

**Comparison.** Compare print-only, book-only and combined recovery/duration features with realistic batching/order uncertainty.

**Local cases to implement.** Best price disappears then returns; trade and cancel offset; recovery by unrelated orders; repeated snapshots; three price ticks versus three updates.

<a id="sr-r06"></a>
#### SR-R06 — Depth capability and order identity

Parent: [R06 — Depth-wide support, pulling and layering dependency](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r06).

**Definition and interaction.** Keep best-price-state persistence distinct from individual order lifetime. MBP-1 cannot reconstruct off-touch changes from later best quotes. Richer anonymous order/depth data still do not identify participant motives; full-depth branches have an explicit acquisition/cohort gate.

**Comparison.** Compare trade/BBO/depth information on the same supported dates only after definitions and incremental value justify depth research.

**Local cases to implement.** Off-touch pull invisible at best; benign cancellation; missing depth level; anonymous order replacement; BBO changes falsely called an order cancellation.

<a id="sr-r07"></a>
#### SR-R07 — Provisional footprint geometry

Parent: [R07 — Candle/footprint effort-result disagreement](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r07).

**Definition and interaction.** Candle body/wick membership is a function of the current or completed candle version. Reclassifying prior trades under final geometry is permitted only at close, not in earlier predictions. Signed-flow uncertainty propagates into disagreement rather than an invented definite sign.

**Comparison.** Compare completed-bar and explicitly provisional geometry with the same first-actionable economics and separate event-order features.

**Local cases to implement.** Future wick enlarges; same final OHLC/delta different path; bar reset; all sides unknown; close changes body membership after signal.

<a id="sr-r08"></a>
#### SR-R08 — Diagonal ratio support and shrinkage meaning

Parent: [R08 — Diagonal imbalance and stacked-flow defense](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r08).

**Definition and interaction.** State tick orientation, ratio-versus-percent convention, denominator support and stack birth timing. A sparse absent row can mean unobserved rather than zero. Cross-price count shrinkage is a feature model, not automatically a binomial confidence claim about independent trades.

**Comparison.** Compare raw ratios, regularized contrast and total-effort/stack features at matched density/width, preserving exact source comparators.

**Local cases to implement.** 350% of versus 350% greater; missing row; zero denominator; wide spread; two stacks share rows; final stack backdated before its last qualifying row.

<a id="sr-r09"></a>
#### SR-R09 — POC identity versus relative-position change

Parent: [R09 — Developing POC flip and footprint-mode migration](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r09).

**Definition and interaction.** Separate an argmax membership flip, dominance/tie transition, centroid change and movement relative to a changing bar range. Earlier mass stays at its traded prices. Grid/normalization changes cannot create an economic flip event.

**Comparison.** Compare tied-mode sets, dominance/persistence and continuous profile changes on common fixed bins and full initial sequences.

**Local cases to implement.** Range expands with mode stationary; one print breaks a tie; POC plateau; final bar mode used early; grid width changes mid-episode.

<a id="sr-r10"></a>
#### SR-R10 — CVD anchor and dimensional invariance

Parent: [R10 — CVD-relative control and multiscale divergence](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r10).

**Definition and interaction.** Compare each CVD with its own scale/anchor and causal median or increments. Cross-cohort/market channels have explicit normalization; resets and arbitrary additive offsets cannot create a divergence. Price/contract/Greek units remain separate.

**Comparison.** Compare ordinary/cohort/OHLC and price/flow divergence families independently before common-target fusion.

**Local cases to implement.** Reset during approach; additive constant changes a faulty signal; incomparable options/futures units; delayed pivot; same close with different extrema.

<a id="sr-r11"></a>
#### SR-R11 — Distinct balance branches and common origins

Parent: [R11 — Balance break, retest and failed-retest reversal](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r11).

**Definition and interaction.** Freeze A/B balance and reference identities with their known times. Prior-POC and prior-value failed-auction variants remain separate; return to A is not evidence of later far-edge traversal. No-retest/failed/unfinished branches share the initial opportunity denominator.

**Comparison.** Compare source branch rules and multistate duration models from identical initial balances, with later stages valued at their own cuts.

**Local cases to implement.** B not distinct from A; B profile formed later; return to A then stall; acceptance at B instead of rejection; no-retest runner; repeated edge crossings.

<a id="sr-r12"></a>
#### SR-R12 — Directional branch and origin lineage

Parent: [R12 — Failed squeeze, refill and renewed same-direction squeeze](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r12).

**Definition and interaction.** Retain original squeeze direction, catalyst, intermediate failure and new pocket as separate stage/objects. Failed squeeze then renewed original direction is different from opposite-direction fade. All source origins enter before the branch is known.

**Comparison.** Compare immediate squeeze, failure fade and original-direction resqueeze under the same original episodes, timing and risk lineage.

**Local cases to implement.** Bullish squeeze fails then resumes upward; catalyst renamed after loss; no retest; newer pocket created after favorable move; incomplete resqueeze.

<a id="sr-r13"></a>
#### SR-R13 — Quiet failure with complete observation

Parent: [R13 — Quiet failure and passive-reversion alternative](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r13).

**Definition and interaction.** A quiet-failure claim needs covered full-size activity plus observed progress/reclaim state. Missing own-side aggression is permitted; missing tape is not affirmative quiet evidence. Separate inefficient opposing push from efficient low-volume continuation.

**Comparison.** Compare direct C/L, price/pace failure and added own-flow confirmation with lost-move and entry-delay accounting.

**Local cases to implement.** Filtered bubbles absent but other sizes active; quote withdrawal rally; inactive holiday interval; source gap; opposing push resumes with little effort.

<a id="sr-r14"></a>
#### SR-R14 — Ordered stages and skipped-stage alternatives

Parent: [R14 — Opposing absorption, reward, refresh and lift-off sequence](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r14).

**Definition and interaction.** Each source stage has exact observable predicates, orientation, clock and units. Source conjunction and flexible/skipped-stage model are distinct variants; a missing/unobserved stage cannot silently count complete. Shared flow measures are correlated evidence.

**Comparison.** Compare every prefix and selected leave-stage-out paths from the same initial opportunities, using updated entry/horizon/risk.

**Local cases to implement.** Progress before delta turn; recovery without price progress; three updates without three ticks; late final confirmation; timed-out stage; missing book.

<a id="sr-r15"></a>
#### SR-R15 — Observed reward and protection maturity

Parent: [R15 — Rewarded-side memory and protected structure](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r15).

**Definition and interaction.** Name price-markout reward separately from executable net trade profit. A protected origin/swing becomes known only after its registered observation/confirmation; its later survival is a future outcome. Preserve failures and sign uncertainty.

**Comparison.** Compare flow-memory protection with price-only swing protection and fixed brackets on all original pockets and complete position paths.

**Local cases to implement.** Positive markout but costs lose; largest flow unrewarded; protected low later breaks; two control switches; confirmation backdated; stop gaps.

<a id="sr-r16"></a>
#### SR-R16 — Frozen minor-node and wick references

Parent: [R16 — Minor-node and intra-wick repeated reactions](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r16).

**Definition and interaction.** Keep anchor/node versions and neighboring regions distinct throughout contact episodes. Final wick membership is unavailable before close; changing profile bins/anchors is a revision, not evidence a prior entry used the new node.

**Comparison.** Compare minor/major nodes and volume/delta/flow additions with matched spatial support and all initial contacts.

**Local cases to implement.** Later-selected wick encloses a winning entry; small node next to valley; upper/lower region swap; developing anchor changes; repeated same-visit ticks.

<a id="sr-r17"></a>
#### SR-R17 — Visit definition and selected survivors

Parent: [R17 — First, second and later defended retests](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r17).

**Definition and interaction.** A new visit requires declared leave distance/time on stable lineage; revision/alias does not reset count. Later visits are selected survival paths, so conditional later-visit accuracy and whole-origin waiting value are separate estimands.

**Comparison.** Compare first/second/later policies from common origins with duration/age/defense features and full retry risk.

**Local cases to implement.** No-return runner; several ticks inside one visit; new alias after loss; deep overshoot; second visit only among strong surviving objects.

<a id="sr-r18"></a>
#### SR-R18 — Shared block event and independent action variants

Parent: [R18 — Jumbo sweep, order-block and rejection-block entries](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r18).

**Definition and interaction.** Use the same L10 source event/geometry record for R18 rather than manufacturing independent confirmation. Source close/sweep thresholds, body/wick alternatives and confirmation/retracement actions retain separate IDs and actual availability.

**Comparison.** Compare timing and stop geometry as separate factors against direct C/L and simple price confirmation on identical origin cohorts.

**Local cases to implement.** Incomplete third candle; no retracement; midpoint versus extreme stop; late source event; same L10/R18 evidence counted twice; failed confirmation continuation.

<a id="sr-r19"></a>
#### SR-R19 — Residual value from actual state

Parent: [R19 — Response-to-action and residual-management adapter](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r19).

**Definition and interaction.** At each prefix, price, remaining horizon, occupancy, risk and future management policy define action value. Waiting cannot retain the original ideal entry/reward. The augmented G pass uses frozen baseline outputs once and cannot feed back into their ancestors.

**Comparison.** Compare entry/filter/exit contributions independently, then replay full policies on common original opportunities including no completion/non-fill.

**Local cases to implement.** Confirmation after target; daily halt while waiting; new spread; existing position blocks candidate; baseline and augmented reward counted twice; unsupported counterfactual fill.

<a id="sr-r20"></a>
#### SR-R20 — Source-variant completeness without repaint

Parent: [R20 — Pine structural and oscillator timing hypotheses](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r20).

**Definition and interaction.** Each routed Pine clause becomes an exact member-specific rule/exception fixture or an explicit unavailable/defective disposition. Shared numeric machinery does not merge similarly named source variants. Drawing/backplot locations are separate from computation availability.

**Comparison.** Compare faithful causal rules, separately corrected defects and continuous-feature alternatives, with each source variant and search trial retained.

**Local cases to implement.** Identical HTF bars; unoffset future HTF; display switch changes numbers; missing source tail; current-inclusive statistic; different CISD rules share a name.

<a id="sr-r21"></a>
#### SR-R21 — Contextual mixture closure

Parent: [R21 — Context-conditioned sequence alternatives](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r21).

**Definition and interaction.** Combine only compatible future targets and horizon/policy definitions using OOF complete-chain forecasts. Soft contextual state, coverage and uncertain gamma scenarios are distinct inputs; final day labels and current augmented outputs cannot condition their own predictors.

**Comparison.** Compare hard source gates, simple available-expert mixture and learned soft gate with calibration after combination and source/sequence ablations.

**Local cases to implement.** All experts missing; duplicate flow evidence; future day-type gate; uncertain opposite gamma scenarios; regime changes while held; collapsed gate.

<a id="sr-r22"></a>
#### SR-R22 — Blinded annotation evidence

Parent: [R22 — Blinded visual/source annotation and mechanism adjudication](components/RESPONSE_DEFERRED.md); [individual phases](experiments/R.md#r22).

**Definition and interaction.** Separate visible measurement, source interpretation, ambiguity and numeric replay outcome. Independent blinded annotations require genuinely separate readings with future hidden; repeated output from one procedure is not independent inter-rater evidence. Preserve unavailable pixels/formulas without invention.

**Comparison.** Compare rule-derived versus independently annotated fields and numeric-only versus annotation-assisted research; selected source charts never estimate natural deployment prevalence.

**Local cases to implement.** Future chart section visible; copied prior annotation; image/caption side conflict; order drawn but unfilled; cropped scale; source time cannot be established.

### Research and operations: 8 contracts

<a id="sr-v01"></a>
#### SR-V01 — Observation-aware label completeness

Parent: [V01 — Label, opportunity and evidence artifact service](components/RESEARCH_AND_OPERATIONS.md); [individual phases](experiments/V.md#v01).

**Definition and interaction.** Store target end, actual observation end, maturity and revision separately. Administrative boundaries defined into the target are complete outcomes; lost observation before the target ends is censoring. Missingness potentially related to volatility requires sensitivity or bounds rather than assumed random censoring.

**Comparison.** Compare independent reference and optimized labelers by event algebra and coverage, including direct joint and factored labels.

**Local cases to implement.** Observed no-touch versus outage; horizon ends at a planned boundary; all losses disappear during feed gaps; a revised object changes an old label; co-contact outcomes double counted.

<a id="sr-v02"></a>
#### SR-V02 — Fitted-state availability and calibration leakage

Parent: [V02 — Chronological splits, purging and OOF dependency builder](components/RESEARCH_AND_OPERATIONS.md); [individual phases](experiments/V.md#v02).

**Definition and interaction.** Every model, calibrator and learned transform has an information cut and label-maturity eligibility. Build OOF for the full chain, including feature discovery and calibration; fold/date labels alone do not establish that every fitted value was knowable then.

**Comparison.** Compare expanding and rolling chronology with explicit training/tuning/calibration/evaluation roles and dependency-closure checks.

**Local cases to implement.** A weekly report label matures after a scheduled refit; calibrator trained on downstream examples; historical feature lookback shared legally; retained state encodes a held-out future label.

<a id="sr-v03"></a>
#### SR-V03 — Complete search and screening accountability

Parent: [V03 — Hypothesis, search-budget and multiple-testing registry](components/RESEARCH_AND_OPERATIONS.md); [individual phases](experiments/V.md#v03).

**Definition and interaction.** Register the search over definitions, inputs, labels, models, gates and policies together. Keep scientifically screened-out, failed-to-run, data-blocked and empirically rejected branches distinct; an early screening gate cannot silently erase mandatory scope.

**Comparison.** Compare registered small search spaces and stronger candidates at matched information/compute; reserve independent confirmation for selected hypotheses and prespecified interactions.

**Local cases to implement.** Same hypothesis renamed; a failed job omitted from resource/search accounting; IV/VIX examples crowd out other required families; an untested branch labeled inferior.

<a id="sr-v04"></a>
#### SR-V04 — Completion and evidence are separate decisions

Parent: [V04 — Evidence gates and economic feasibility decision](components/RESEARCH_AND_OPERATIONS.md); [individual phases](experiments/V.md#v04).

**Definition and interaction.** Report implementation coverage, applicable-test coverage, predictive support, integrated economics and future evidence as distinct statuses. A complete research package can report not-met or inconclusive economics; a bounded data audit cannot mark a signal validated.

**Comparison.** Compare the complete supported system and simple baselines under the frozen objective and account definitions; retain every unresolved dependency in the final coverage report.

**Local cases to implement.** All files exist but tests are placeholders; a local metric passes while account paths fail; blocked future evidence reported complete; a favorable point estimate substituted for the required interval.

<a id="sr-v05"></a>
#### SR-V05 — Monitoring the collection of experts

Parent: [V05 — Drift, calibration monitoring and controlled adaptation](components/RESEARCH_AND_OPERATIONS.md); [individual phases](experiments/V.md#v05).

**Definition and interaction.** Calibrate the joint alert policy across correlated experts and repeated monitoring times. Distinguish individual warnings from a family-wide incident and measure cumulative false-alarm/abstention cost; critical deterministic faults retain immediate handling.

**Comparison.** Replay frozen seasonal, residual and multivariate monitors with actual label delays and correlated source failures before enabling an adaptation policy.

**Local cases to implement.** One common feed fault triggers dozens of false independent alarms; delayed labels mask drift; repeated small alarms cause permanent abstention; stable predictions but worsening execution.

<a id="sr-v06"></a>
#### SR-V06 — Decision parity at numerical boundaries

Parent: [V06 — Historical/live parity, restart and deterministic replay](components/RESEARCH_AND_OPERATIONS.md); [individual phases](experiments/V.md#v06).

**Definition and interaction.** Compare semantic state and final actions exactly where specified, while allowing justified numeric tolerances only for intermediate calculations. Small floating differences crossing a threshold require a deterministic decision rule or explicit ambiguity resolution.

**Comparison.** Compare reference, optimized, chunked and restarted runs on identical captured inputs, including configurations near action thresholds.

**Local cases to implement.** Numerically close values choose opposite sides; different chunk sizes change a tied POC; interrupted atomic write; restart after send but before acknowledgement; same capture with different receipt scheduling.

<a id="sr-v07"></a>
#### SR-V07 — Attribution with changed populations

Parent: [V07 — Failure attribution and controlled diagnostic interventions](components/RESEARCH_AND_OPERATIONS.md); [individual phases](experiments/V.md#v07).

**Definition and interaction.** Separate a fixed-opportunity scorer intervention from a generator intervention and a full-policy intervention. Refit downstream OOF dependents when the intervention changes their training inputs; population/occupancy changes are part of full-policy effects.

**Comparison.** Compare paired baseline replacements and selected factorial interactions, retaining invariant risk controls and reporting nonadditive effects without forced credit allocation.

**Local cases to implement.** A removed feature changes candidate count; an earlier trade blocks a later one; a baseline swap invalidates gate calibration; conditional gains reverse on the full eligible-day ledger.

<a id="sr-v08"></a>
#### SR-V08 — Resumable work and full-scope progress

Parent: [V08 — Resource-aware reproducible experiment orchestration](components/RESEARCH_AND_OPERATIONS.md); [individual phases](experiments/V.md#v08).

**Definition and interaction.** Jobs have immutable configuration/input IDs, atomic output commits and explicit retry/checkpoint semantics. Track completed, pending, blocked and rejected work against the whole scope across resumptions of the same implementation thread; budget limits do not imply scientific rejection.

**Comparison.** Benchmark reference and optimized pipelines with cold/warm caches and realistic contention; continue independent eligible work when a branch awaits data or future observations.

**Local cases to implement.** Retry duplicates artifacts or trials; changed input hash resumes an incompatible checkpoint; disk-full partial model appears complete; one blocked feature stops unrelated milestones.

## Evidence and acceptance

The source file [component_refinements.psv](review/system-refinement/component_refinements.psv) contains 153 individually authored records and is checked against exact parent IDs. The preserved baseline is in [baseline.zip](review/system-refinement/baseline.zip), with [baseline.json](review/system-refinement/baseline.json). Coverage/link/hash checks establish document consistency only; they do not certify the semantics of an implementation or market performance.

At implementation expand each case into named expected assertions under the parent/local phase and relevant source clause. Apply zero-unexplained-failure rules for deterministic semantics, correct inference for forecasts, and full constrained economic evaluation for actionable changes. Preserve rejected and inconclusive results. The full-system pass is not a claim that no further improvement is possible.
