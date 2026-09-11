# Implementation handoff

This is the build contract for the next implementation task. The current deliverable is the specification; the models are not already corrected or empirically validated. Read the master guide, shared engines, protocol and all relevant cards before implementing a family. Do not rebuild the old source audit.

## 1. Scope and authority

Implement exactly R-J01–25, R-G01–11, R-A01–18, R-F01–18, R-R01–04 and R-S01–09. R-P01–20 are excluded. Preserve the source audit as provenance, not an implementation oracle. All numerical assumptions in these cards are authorized research choices. No author clarification is required to implement a declared default; unresolved stronger data quantities use their explicitly named observable alternative.

Use an isolated new package under `implementation/src/trading_research/research/research_v1/` and a new runner `implementation/tools/run_research_v1.py`. Reuse an existing utility only after its contracts and tests match this specification; old daily recipe booleans and caches do not qualify automatically. Do not modify `RULES.md`, `FORMULAS.md`, `CHART_AUDIT_FABLE.md`, sources, archive or the preserved audit report during the build. Git operations remain in `/workspace`; `data/` stays ignored and on disk.

Canonical configuration is `research-spec/model_specs.json`, generated from the six `research-spec/models/*.json` files by `implementation/tools/research_spec_build.py`. Hand edits belong in those six source files, then regenerate. Formula semantics are in ENGINES.md. A card's explicit parameter/binding overrides an engine default only for that card. If a required behavior is not otherwise specialized, use the exact engine default, not a newly guessed constant.

Validate the handoff before building with `python implementation/tools/research_spec_validate.py` from `/workspace` (requires Python `jsonschema`). It applies [model_specs.schema.json](model_specs.schema.json) and checks provenance, dependency references, grid budgets and the small numerical examples. [validation.json](validation.json) records those specification checks; it does not certify a future implementation.

Dependencies specify evidence producers. `consumers` are evaluation destinations and do not create a reverse build dependency. During a consumer's grid search, all producer defaults remain fixed. Test producer changes through their own registered comparisons; do not silently combine independently selected best settings into an unregistered composite. An explicitly registered composite configuration must record every producer hash, count as a new trial and be selected inside the same chronological training boundary.

`inputs` lists the unconditional inputs. `conditional_inputs` and `conditional_dependencies` activate only for the stated selector, such as `branch=BIG_resqueeze`; otherwise their absence cannot block the default. Within R01, each native product is evaluated independently: an unavailable ETF dividend input cannot suppress a valid European NDXP snapshot. R01 is context for a futures consumer, not permission to execute options.

## 2. Module responsibilities and APIs

Use immutable dataclasses or equivalent typed records. Do not implement the following interfaces as opaque daily booleans.

| Module | Required responsibility and interface |
|---|---|
| `config.py` | `load_config(path)->ResearchConfig`; validate IDs, parameter domains, conditional inputs, config hash, freeze timestamp, selected input manifest and split dates. Unknown keys are errors, never ignored. |
| `adapters.py` | `iter_events(dataset, instrument, start_ns, end_ns, batch_rows)->Iterator[EventBatch]`; normalize D01–D10, preserve ordering groups/provenance, filter by partition metadata before reading columns. |
| `calendar.py` | `session_intervals(instrument, trading_date)->SessionSchedule`; real holiday/early-close/halt intervals, UTC bounds, raw contract mapping. Cache schedule by versioned calendar hash. |
| `quality.py` | `assess_coverage(events, schedule)->CoverageRecord`; missing versus verified zero, aggressor coverage, cross-feed reconciliation, incomplete outcome censoring. |
| `bars.py` | `build_bars(events, alignment, duration)->Iterator[CompletedBar]`; exact start/end/available_at, no row-count resampling; explicit price-range-bar variant for F14. |
| `references.py` | `form_reference(...)`, `advance_reference(event)`, `snapshot(asof)`; E01 geometry and independent first visits, E09 gap state, no rewriting history. |
| `profiles.py` | `profile_snapshot(events, scope, asof, config)->ProfileSnapshot`; E03 VP/TPO/delta, nodes, ledges, shape, actual row-to-price conversion and repair ledger. |
| `statistics.py` | `fit_prior_history(samples, cutoff, config)->FrozenEstimator`; E04 histories, type7 quantiles, weighting, EV/P-zone scales and widths; sample dates persisted. |
| `flow.py` | `observe_flow(events, book, area, start, config)->FlowObservation`; E05–E07 footprints, CVD, absorption, first-passage reward, reload evidence, fixed-window and streaming refill modes. |
| `structure.py` | `advance_structure(completed_bar)->list[StructureEvent]`; E08 pivot recognition, alternating legs, FVGs, OB/RB, frozen microbalances, explicit expiry. |
| `options.py` | `native_snapshot(product, asof, config)->OptionScenarioSnapshot`; E10 input vintages, model selection, IV/Greek solve, parity forward, scopes/walls/flip roots. |
| `episodes.py` | `advance_episode(event, state, config)->Transition`; E02 ordered contact/break/hold/retest/confirmation/failure and E07 catalyst routes. Store full transition histories. |
| `models/{jumbo,greenbird,amt,flow,regime,sires}.py` | One registered function/class per ID composing the shared engines according to its card; model-specific payload matches declared outputs. All 85 IDs must be registered even if a date is unavailable. |
| `execution.py` | `simulate(signal, subsequent_events, config)->OrderFillLedger`; E11 arrival delays, valid BBO, adverse fills, trade-through limits, stops, target updates, fees and censoring. |
| `evaluation.py` | Explicit eligible-session/hour/episode populations, typed outcomes, proper losses, paired net performance, chronological inner/outer runs and multiplicity-aware comparisons. |
| `render.py` | Plot from the exact reference/snapshot/episode/fill records used for metrics; show all availability times, first-visit line ends, gaps and order evidence. |

Minimal episode transition record fields are `episode_id, parent_id, model_id, variant_id, instrument, trading_date, from_state, to_state, event_ts, available_at, input_ids, side, frozen_area_id, reason, quality`. A model may add fields, but cannot discard these. Features expose `known_at`; outcomes expose both observation horizon and completion/censoring time. Keep market price, ticks, contracts, dollar gamma and normalized risk in different typed columns.

## 3. Build order and required evidence

1. **Contracts and quality:** D01–D04 adapters, calendar, raw contract mapping, side conventions and coverage. Reproduce a complete winter session, a summer session, early close, roll boundary, missing-minute case and unknown-aggressor case. ES price SMT can use trades/bars after its BBO archive ends.
2. **Price geometry and event clocks:** E00–E02, E08, E09 and the reference ledger. Implement J01–10/J18–25 and G01–10 price-event layers. This does not enable a model's flow gate before its flow layer exists.
3. **Profiles and statistical inputs:** E03–E05, prior-only histories, VP/TPO repair and value snapshots. Implement A01–18, J06/J11–17/J21 and context parts of S04/S08/S09. Preserve intraday versus completed objects.
4. **Signed flow:** complete D02 trust tests, E06–E07 and F01–18/S01–09 observation/state layers. Displayed reload stays named inference; missing order IDs are not fabricated. Implement passive and aggressive branches separately.
5. **Native context:** D05–D10, E10 and R01–04. Options/CVD gates are enabled only for variants that declare them. No missing input is defaulted to neutral or false.
6. **Orders and outcomes:** E11, all 49 signal cards and six management cards, then deterministic plots. Context/component consumers must explicitly wait until features exist.
7. **Research comparisons:** default runs first, registered one-factor grids and at most two-axis interactions, then chronological retrospective evaluation. Produce all family tables. Freeze a prospective candidate only after the build and historical comparison gates pass.

Stages are implementation dependencies, not permission to report partial completion as all models done. The handoff is complete only when each ID has an implemented default, required branches/grids or an exact data-unavailable result, meaningful acceptance tests and its report. A model with no qualifying historical events still needs full state/negative/censoring tests; do not invent positives.

## 4. Golden and metamorphic tests

`golden_cases.json` supplies numerically checked small examples for the specification. The build must implement independent tests of those examples, plus the per-card `acceptance_cases`. The specification checker verifies their arithmetic/configuration, not a future trading engine's behavior.

Required shared behavioral tests:

- Prefix invariance: run once through a decision cutoff and again on the full session; every earlier feature, chosen ID and order is identical.
- Perturb future prices/volume/calendar revisions; earlier signals remain identical. Perturb a past qualifying input and the affected later observation changes as expected.
- Unit transformations: convert points to ticks and back exactly; NQ and sister markets retain their own multiplier/tick. Test off-grid prices as failures.
- Mirrored artificial tape: reflect prices around a fixed centre, reverse buy/sell signs and swap highs/lows; every symmetric recipe reverses side with matching times/distances. Explicit long-only source branches remain named exceptions.
- Equal timestamps, target/stop ambiguity, gaps through levels, missing formation bars, absent midnight print, insufficient lookback, unknown side, zero denominators and incomplete outcomes produce their declared states.
- First-visit lifetime: equality retires only the visited side; ETH counts; a later strict sweep may finish the original pending episode but cannot rearm the reference after failure/expiry.
- Episode counting: three in-band bars are one visit; separate area attempts use actual departure/time or the explicit S07 post-exit new-flow rule. Old prints cannot be reused as new defense.
- Correct execution: no fills before order arrival; limits require the declared trade-through; adverse entry gaps are retained; exits are not postponed to obtain a cheaper spread; pre-entry extremes do not enter MAE/MFE.

Use real dated defect examples from the preserved audit as regressions for old bugs, not forced positives for newly chosen assumptions. In particular retain July 10, 2026 pre-09:40 projection timing, January 28, 2026 prior-high consumption at the previous 16:45, missing IB first-visit rearming, actual five-minute completion times, true overnight profile scope and the older source stop/POC ambiguities as historical comparisons.

## 5. CLI and artifacts the build must provide

The following are required future CLI interfaces; they are not commands claimed to exist today:

```
python implementation/tools/run_research_v1.py validate-inputs --config CONFIG --start DATE --end DATE
python implementation/tools/run_research_v1.py build-inputs --config CONFIG --start DATE --end DATE
python implementation/tools/run_research_v1.py run-defaults --config CONFIG --families all-main --start DATE --end DATE
python implementation/tools/run_research_v1.py run-grid --config CONFIG --model R-J01 --split SPLIT_ID
python implementation/tools/run_research_v1.py evaluate --config CONFIG --split all-retrospective
python implementation/tools/run_research_v1.py render --config CONFIG --families all-main
python implementation/tools/run_research_v1.py verify --config CONFIG
```

Partition large input work by instrument/date and aggregate streaming batches (default 250,000 rows). Persist derived products once; reuse them by full content/config hash. Never load multi-year MBP-1 into one dataframe. Initial acceptance jobs use one or two sessions at a time; broad experiments run only after those pass. A longer run may checkpoint between partitions, but a partial archive must not be labelled complete.

Derived market data belongs under `data/derived/research-v1/{manifest_hash}/{module}/`. Reviewable reports and small fixtures belong under `implementation/reports/research-v1/{run_id}/`. Every run includes `run_manifest.json`, `coverage.json`, `config.json`, candidate/trial registry, typed event/fill summaries, per-family report, both required PHASE/audit tables, example charts and completion check. Checkpoints include partition boundaries and immutable hashes, never pickle an unversioned opaque strategy state.

## 6. Ready-to-use implementation task

> Implement `/workspace/planning/phase-1-live/RESEARCH_BUILD_SPEC.md` and all linked normative files for the 85 non-Pine main models. Start with the data contracts and shared engines, then all model cards. Use the exact defaults and bounded grids; label them as new research definitions. Follow first-visit retirement for both highs and lows, all available-at rules and the order simulator. Build derived inputs from stored data where specified. Do not ask for unpublished author formulas: those uncertainties have declared research alternatives. Do not fabricate unavailable order IDs, dealer positions, native cash minutes or event vintages. Keep old sources/audit/RULES/FORMULAS/Fable files intact. Implement in the isolated research_v1 package, run meaningful arithmetic/sequence/prefix/coverage tests, produce both family tables and charts from the event ledger, and evaluate defaults before the bounded chronological experiments. Report every ID's implementation status and distinguish correctness, historical promise and prospective improvement. Do not claim improved performance until the registered tests support it.
