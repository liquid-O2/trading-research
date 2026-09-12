# Implementation plan following the full audit

September 12, 2026. **Execution record:** stages 1–7 are implemented. Current acceptance, remaining evidence limits and the final runner results are recorded in [COMPLETION_REPORT.md](COMPLETION_REPORT.md), [COMPLETION_MATRIX.md](COMPLETION_MATRIX.md) and [CHART_VERIFICATION.md](CHART_VERIFICATION.md). Stage 8 remains deferred. The requirements below are retained from the plan, based on the [full audit](FULL_AUDIT.md), [166-object inventory](OBJECT_AUDIT.md), [diagnostics](charts/full-audit-probes.json) and [source findings](charts/full-audit-sources.json).

The first objective is to reproduce the documented observations and actual source cases with correctly timed native objects. Complete that before expanding historical discovery or searching parameters. Preserve useful existing helpers; do not restart the whole codebase.

## 1. Resolve source configuration and case interpretation

Create a versioned source-configuration record and case manifest. Each case needs its original PDF/page/post/image, date and timezone confidence, native symbol/contract, chart type/timeframe, observation interval, displayed profile IDs, source settings, observed decision and subsequent annotations. Keep unreadable or absent fields explicit.

Start with cases that exercise different missing behavior:

- Jumbo February 24 range geometry as an existing control; June 12 separate session profiles/footprint; a source orderblock case in each direction.
- Green Bird November 20 sweep entry, and the separately documented VWAP continuation. Preserve their different entry sequences. Use each figure's timeframe, not a blanket two-minute chart.
- Sires overnight/ETH/current profile references, same-candle footprint/POC change and one complete four-stage example; a source loss or early attempt must also remain in the case set.
- Saint break/retest and failed-auction routes; Keani's prior-value/opening-A/developing-value sequence; the member's two independently supported reasons.
- Refill selected-order records and non-entry process/state/risk examples as their own observation units.

Carry the newly found codex scale/review example and MFE/MAE collection guidance into process configuration. Carry the exact visible Sires VWAP settings and unresolved source-price label into the VWAP configuration. Bind O073 to O011 for that Sires overnight example. Recover the active SessionStat timeframe constraint. Source-specific values stay scoped; they do not become global defaults.

**Deliverable:** source configuration and case records with fact/inference/unknown distinctions, plus precise amendments to the relevant live contracts. An observed screenshot entry may have a price or time interval without a precise fill timestamp. Source illustrations need no invented private trading journal or new prospective collection period before they can be examined.

**Acceptance:** each plotted reference and claimed entry can be traced to the source figure; the November 20 entry is not delayed to later MSS/FVG; no MNQ display is labeled an observed NQ fill; no source setting is silently supplied from another author.

## 2. Enforce native identity, coverage and availability at the object boundary

Use the existing adapters, instrument definitions, file ownership and clock helpers. Resolve every raw-member locator into actual immutable source members; verify instrument, units, interval and ownership. Computed inputs must come from those resolved members. Preserve native source precision and tie-batch ordering limits.

Add typed result contracts for every O object and distinct types for validity state, order state and qualitative interpretation. Propagate `base_ok`, `coverage_ok`, holes and dependency availability through manifest parsing and method scoring. Derive `known_at` from all incorporated observations. A missing internal time or coverage record cannot become a caller-supplied true flag.

Route O004 through complete clock-aligned bar construction. Distinguish a known empty interval from missing data. Preserve native contract changes, session boundaries, and source-specific time/range-bar construction.

**Deliverable:** verified object envelope/member resolver and complete bar/coverage producer, with invalidated or explicitly isolated legacy outputs whose sign/timing/configuration conflicts.

**Acceptance:** P01–P03, P05–P07, P10, P20 and P25 cannot certify the malformed observation; the nonexistent-locator example is rejected; missing coverage remains unknown through the method boundary. Complete supported observations still work. No new universal time horizon, tick size, reset or event-order tie-break is introduced.

## 3. Build full dated profiles, references and snapshots

Construct volume and signed-volume histograms for each independently identified prior RTH, prior ETH, overnight, current developing RTH and selected-range profile. Construct composites by explicit constituent IDs. Retain native price rows, buy/sell/unknown/total volume, H/L, POC and ties, VA fraction/algorithm, source bin grid, session date, instrument, formation bounds, snapshot ID, `as_of` and `known_at`.

Implement the source's VA construction where specified; otherwise keep that part unknown or name a comparison variant. The 40%, 68% and 70% settings are separate configurations. Resolve the conflicting legacy VA tie policies and regenerate any signed caches affected by the old A/B inversion. Never reuse final-RTH levels as an earlier developing profile.

Build distinct earlier-profile references, tested/untested history, and source-defined composite/reference joins. Volume POC and profile midpoint remain distinct. Extend O063/O077 to retain their full documented payloads.

**Deliverable:** full native profile objects and source-case panels showing all relevant prior/current profiles separately, with reproducible references.

**Acceptance:** earlier snapshots are invariant when later events are appended; each price row reconciles to native side/volume totals; unknown side is retained; profile identity survives equal prices; the existing tie counterexample has an explicit policy; the source comparison visibly includes every relevant profile rather than just scalar lines.

## 4. Complete geometry, TPO and local flow producers

Implement both sides of the documented geometry and orderblock/TPO rules. Preserve the actual parent range for every projection and pocket. Enforce the stated history length for the 14-period candle average. Build source-compatible TPO membership and required consecutive periods.

Construct local footprints, diagonal comparisons, imbalance runs, POC snapshots, side concentration, price response, and displayed large-trade filters from native observations. Preserve each author's filter and bar configuration. Keep location, aggressive execution, passive refill evidence, reward, return, renewed defense and subsequent confirmation as separate linked observations.

Use trade/BBO data for supported facts. Do not manufacture full-depth cancellations or hidden reserve from best quotes. When only qualitative source interpretation exists, retain the native measurements and the attributed interpretation separately.

**Deliverable:** full geometry/TPO/flow objects required by the selected source cases, with exact parent/candle/band identity and event intervals.

**Acceptance:** P04, P08–P09, P11–P19 no longer produce the demonstrated incorrect result. Include mirrored sides, missing history, no reward, missing retest, reversed events, tied events, unknown-side volume and a same-candle POC example. Passing an arithmetic ratio is insufficient to certify an entire local sequence.

## 5. Complete persistent thesis, attempt, order and process records

Link thesis validity/death events, source objectives, attempts, exits, re-entries, order instructions, fills, working quantity, position quantity and management actions. Enforce type-specific source policy and account/session scope. Preserve original risk and subsequent bracket versions.

Repair O150 cancellation, expiry, amendment and post-cancellation exit behavior. Requested actions must not reduce a position before actual fills. Reconcile quantities against amended orders and actual exits. Keep one-position and cancellation-age constraints only where the selected source configuration requires them.

Bind triad observations to native instrument-specific AMT objects and actual first-use times. Bind state transitions to ordered adjacent observations under a declared cadence. Keep supplied count arithmetic separate from transition evidence and any future classifier.

Apply the journal to our own research process: original thesis/reason/confidence, all identified attempts, misses/breaches, actual observations and later revisions. Keep source illustrations separate from contemporaneous process records. Preserve Stoic's validation and risk illustration as process/risk checks; they are not an entry strategy. Retain all outcome categories and denominators rather than summarizing only wins and losses.

**Deliverable:** complete observed lifecycle/process records and their invariants, with no order routing or portfolio simulation.

**Acceptance:** P21–P27 are resolved at the relevant boundary; cancellation ends working quantity while an already filled position can still exit; expiry prohibits later fills without a new valid order; amendments reconcile; source caps do not leak across methods; absent validation or transition evidence stays unknown.

## 6. Assemble every required method operand explicitly

Build typed input views for M01–M12. For every required operand declare its producer, source role, units, identity, dependency times and evidence. For example, `asia_high`, `london_high` and `prior_vah` need semantic reference producers with their own dated parents; they are not arbitrary aliases of whichever scalar is present.

Compose the selected branch only. Preserve source-specific alternatives, optional applicability, management and re-entry units. No arbitrary `value_field` renaming, copied Boolean, nearest-price join or another author's confirmation may fill a missing field. Separate missing producer implementation from a genuine unknown source definition.

**Deliverable:** source-case/native input assembly connected through the existing method evaluator and reference-outcome path, with a producer/coverage matrix covering every operand.

**Acceptance:** all 12 method contracts have a complete binding inventory; selected case records can travel from real members to full object payloads to method results and explicit holes. A valid loss can satisfy sequence rules. A favorable later outcome cannot repair a failed prerequisite.

## 7. Validate the source cases and the reporting contract

Render each selected case using the correctly configured native bars, profiles and events. Compare the original and reconstructed figures at the observed decision time. Record what matches, what contradicts the source, and what remains unreadable or unavailable. Source-case fitting is calibration evidence, not an unbiased historical success rate.

Check complete object output schemas and meaningful domain invariants alongside existing fixtures. Use the 27 audit examples as regression candidates, extending only where the repaired design requires it. Keep the useful shared-guard mutations, but do not let them stand in for native event tests.

Make software completeness, source ambiguity, data coverage, source-case agreement and measured historical scope separate report dimensions. Under C07, a missing required output must cause implementation failure. Print both required family tables and retain source/loss/miss cases; report source illustrations separately from automatic historical discovery.

**Deliverable:** reviewable source-case reports and a contract-complete acceptance report. No full-method claim while required branches or producer outputs are missing.

## 8. Later research, after this implementation is reviewable

Only after the preceding outputs are checked should research compare alternative price bases such as HL2/HLC3/OHLC4, source-compatible timeframes, entry timing, thresholds or reconstructed proprietary components. Use named assumptions, a frozen calibration set, an untouched evaluation set, and complete opportunity/coverage accounting. Record revised hypotheses as new versions.

That later work may infer useful approximations from actual source dates where the original engine is unpublished. Its evidence should say exactly what was reconstructed and how closely it matches. A failed arbitrary approximation does not prove the source trade was invalid. None of this parameter search, classifier training or new performance simulation is part of the present audit.

Macro work remains deferred. Native market observations, source-case fidelity and the research process are the immediate dependencies.

## Work order and completion gate

**Configuration/cases → object boundary → full profiles and local observations → persistent lifecycles → method input views → source-case comparison and acceptance → later research.** Geometry and profile/flow implementation can be split into independently reviewable changes after their shared identity/time contracts are fixed.

The implementation is complete for a declared method scope only when every required output is produced or explicitly unknown for an evidenced source/data reason, every required operand has a real producer, the relevant source cases and adverse invariants have been checked, and the report labels match that scope. Registered IDs, empty historical cohorts and green minimal fixtures are not substitutes for those conditions.
