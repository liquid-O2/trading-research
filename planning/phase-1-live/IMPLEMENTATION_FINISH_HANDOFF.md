# Finish Phase 1 implementation

**Executed implementation work order; not a certificate that all of Phase 1 is complete.** The implementation was delivered in commit `84221545fac35d35ff24f2ebc264aec7d1145b61`. The gap descriptions below are retained as the historical work order and must not be treated as fresh evidence that those defects still exist.

**User clarification, 2026-09-13:** Phase 1 includes historical measurement of the implemented setups. Phase 2 is the context layer for selecting specific setups. The earlier allowance below for a bounded engineering sample establishes implementation validation only; it does not replace the remaining Phase 1 measurement.

Continue from the accepted implementation: freeze the measurement scope and outcome definitions, scan the declared NQ 2020+ study, retain coverage/exposure and separate setup denominators, measure subsequent behavior, and publish the setup evidence. Preserve source-required setup context. Do not start a cross-setup context selector, optimize it, or call that Phase 1 measurement. Do not restart the completed implementation checklist below. [Current status](PHASE.md) and the accepted strategy-reconstruction report identify the actual baseline.

Prepared 2026-09-13 after a final integration review. This is a work order for a new task, not another source-definition book. Execute it through implementation, native replay, verification and current documentation. Do not stop after an audit, a plan, a status rename or a fixture-only acceptance.

## Objective and boundaries

Complete the source-grounded, reproducible Phase 1 research pipeline for the existing 12 methods, 50 catalog branches and eight additional observation units. Preserve the distinction between a documented method, its operational research variant, a discovered market opportunity and an author's actual trade. The goal does not require reconstructing private trades or proving profitability.

Work in `/workspace` (`liquid-O2/trading-research`). Read AGENTS.md. Start from the **current working tree**, not a reset to HEAD: the preceding task left intentional documentation corrections uncommitted. Inspect and preserve those changes before creating any isolated checkout. At preparation, HEAD was `f8b14eff72e669a27035d7de9d15ec88a1c4cdd2`. Unrelated untracked `.audit/method-pack-v1.tsv`, `implementation/reports/phase1-live/derived-views/mbp1-1by6_0q8/` and `sources/method/` must not be swept into commits or deleted.

Existing raw files are immutable. Do not edit `sources/`, `archive/`, either old planning tree, or existing raw files under `/workspace/data`. New derived datasets need their own paths, versions, source hashes and membership receipts; data remains ignored and uncommitted. No Phase 2, 85-model expansion, parameter search, classifier training, live trading or paid data purchase. Resolve routine engineering choices autonomously and continue independent work if an external input is unavailable.

The active market study is **NQ from 2020-01-01 through actual acquired endpoints**, as already specified in DATA_SCOPE.md. Earlier history may be needed for causal lookbacks, but must not enter the new opportunity denominator. Peer ES/YM/RTY or macro inputs are conditional on the source branch that consumes them; an unrelated missing dataset cannot block all methods. No NQ-to-MNQ fill claims.

## Read the existing owners of the definitions

Start with `/workspace/planning/phase-1-live/PHASE.md`, `DATA_SCOPE.md`, and `wiki/index.md`. The 12 `wiki/method-*.md` pages and their linked objects contain the compiled source sequences and PDF/post citations. Use the raw cited pages to resolve a specific uncertainty or contradiction; do not repeat an exhaustive PDF transcription or build a second wiki.

FORMULAS.md owns object/procedure contracts. The accepted `implementation/reports/phase1-live/empirical/registry/` owns the **old comparison definitions**, not the full author methods. RESULTS.md is measured evidence, not source law. `wiki/current-status.md` and the Jumbo/Sires/member correction sections explain the misleading legacy labels. `SOURCE_CALIBRATION_DISCOVERY_HANDOFF.md` and the old method-pass completion reports describe earlier work, not proof that this task is already done.

Reuse the existing implementation in `implementation/src/trading_research/research/method_pack/`, including native resolution, MBP-1 views, object producers, causal assembly, source configurations, method predicates and lifecycle checks. Reuse the 22-case/17-configuration source catalog and existing negative controls. Extend the current architecture rather than building a parallel engine.

## Verified gaps to close

### 1. Connect historical discovery to the method evaluator

`discovery.py:run_historical()` currently returns `[]`; its audit rejects a complete selector. `pass_runner.py` records holes and scores supplied episodes. The empirical runner instead schedules the 19 entries in `empirical_registry.py:SPECS`. The `unavailable_definition` default is not a source review. `empirical_binding.py` supplies only narrow numeric roles. Registering a name or passing an already-selected fixture does not implement historical discovery.

Create one authoritative branch-coverage manifest, consumed by discovery, reporting and acceptance. For all 50 branches and eight extra units, record: source definition/citation, necessary objects/operands, actual producer and scanner, observation unit, operational assumptions, required inputs, coverage state and evidence for any external limitation. Reconcile all 166 objects and 373 operand bindings against the reachable paths. Classify source knowledge, implementation, input availability and measured results separately; remove blanket source-unavailable fallbacks from current reporting.

The 18 specifically excluded but documented branches are:

- JJ-TBR: `judas_outbound`, `single_extended`, `single_purged`, `other_session`, `timed_pzone_reversal`.
- SIRES: `dom_rejection`, `absorption_reward_retest`, `stop_four_stage`, `footprint_confirmed_reaction`, `ofm_aggressive`, `ofm_passive`, `clean_squeeze`, `balance_failure_fade`, `defended_band_continuation`, `microbalance_break`, `kg1_retest`.
- MEMBER-TWO-REASONS: `resistance_short`, `planned_return_long`.

Implement their observable discovery and ordered sequences using the existing objects. Derive market-observable fields from market data rather than demanding the author's private journal. Where the source is qualitative, choose a minimal causal operationalization, document its rationale and freeze it as an explicitly named research assumption before evaluating its outcomes. Do not claim that threshold is author-exact. Do not replace the method with an arbitrary box, band touch or favorable future path. Preserve specifically unavailable external operands without suppressing independent observable stages.

Known source corrections must survive: TBR p.7 prints seven other-session formation windows; TBR p.12 publishes reduced expectations/range-edge targets; STOP pp.10, 12, 14 publishes stages and numerical checks; CONT p.11 publishes the clean-squeeze sequence; OFM p.14 publishes the passive variant without requiring individual passive-order identity. Exact P-zone/KG1 generation remains distinct from the documented usage sequence.

### 2. Finish the sequences inside the existing comparisons

Audit all 19 supported comparisons and the other 13 dispositions too. Current support does not mean the whole source method is implemented. Preserve the old simplified endpoints as historical comparisons; add the missing observable method stages in the new version:

- Saint: distinct original/older auction identities, actual failed-exploration/reacceptance antecedents, two prior failed-buying episodes where required, same-boundary retests and POC routes.
- Keani: opening state followed by developing value, imbalance break and defended retest where documented; above-value A-period alone is not the entry sequence.
- Sires VWAP: context, selected band and actual local flow confirmation; inward bar close alone is not the method.
- Green Bird/Jumbo: causal context, source-specific reference and selected confirmation/risk/objective. Preserve the November 20 sweep entry before the later MSS/FVG annotation. A VWAP touch endpoint is not a profitable-trade label.
- Refill: separate market zone/return observations from the proprietary selected-order model, quantities and fills. Do not lower thresholds to manufacture candidates.
- GB-SCALP, Jetbundle, Stoic and management/re-entry units: implement the published market/process/state/risk operations in their actual units. Do not invent a classifier, proprietary formula or historical account ledger, and do not require one to calculate an independently observable quantity.

The earlier matrix lists 24 objects without registered native/derived producers, including context O033–O045 and process/macro objects. Inspect actual adapters and consumers individually. Some are legitimate external-record interfaces; others may have usable local market or macro inputs. Existing `discovery_audit.json` classifications are hypotheses to recheck, not authority to call every missing operand private.

### 3. Use a consistent event-time market path

Reuse `mbp1_views.py`, native resolution and owned physical spans. Local MBP-1 starts 2020-01-01 at 23:00 UTC; standalone trades start 2021-09-01 at 18:00 UTC. MBP-1 includes executions: only action `T` contributes traded OHLCV, profiles or delta. Quote updates supply only their documented depth-one observations. Canonical file ownership must prevent pooling monthly/weekly duplicates while preserving real repeated executions.

The code already buckets tape by event time, then incorrectly demands exact agreement with vendor receive-time bars. Fix this throughout coverage, profiles, candles, VWAP, delta and their consumers. Build event-time-derived inputs consistently where event data exists; preserve vendor-clock bars as a separately identified source/comparison. Do not mix the clocks silently. Vendor OHLCV differences are diagnostics, not automatic proof of tape loss. Missing receive timestamps do not prohibit event-time research; historical feed arrival is not thereby known.

Preserve timestamp tie batches and physical identity. Without exchange sequence, order-dependent O/C, trigger ordering and same-batch outcomes can remain ambiguous while order-independent volume/extrema remain computable. Handle book reset/clear/update flags according to verified schema semantics. Do not infer deeper queues, hidden reserve or individual order identity from MBP-1.

Recheck all old tape dates/current and prior windows, including the **2021-09-01 truncated standalone session and its prior session**, not just the four 2022/2026 windows already reconciled. Do not merely turn off validation: prove source membership, identity, bounds, transformations and observed coverage under a declared contract.

### 4. Integrate existing recovery and correct calendars/coverage

Read `implementation/reports/phase1-live/coverage-audit/README.md`, `data-recovery-v1/README.md` and their receipts. Already available:

- 12,420 recovered minute keys across nine 2020+ sessions, in the existing minute-recovery manifest; 32 pre-2020 keys are outside the study denominator.
- The later 780-row August 3–4 RTH reconstruction overlaps two of those sessions. Reconcile by instrument/minute/source identity; never append both.
- An MBP-1-derived tail beyond the standalone bar endpoint, with its own clock and coverage limits.
- Twenty macro series, 37,003 vintage records and verified initial BLS release clocks in `macro-backfill/`; do not reacquire them. Connect only required series with their actual vintage/availability semantics.

Implement explicit derived-input admission; the current empirical bar path does not use these recovery manifests. Preserve their clock basis: 1s-to-1m recovery does not turn vendor bars into event-time candles.

Replace all-weekday/dense-390-minute assumptions with a versioned product/session policy where the source calls for actual trading sessions. Verify historical NQ holidays, early closes, maintenance and DST from authoritative product-specific evidence. Do not use cash-calendar closure alone as futures-hours proof. Require correct same-contract prior history across rolls; continuous-front files do not contain every active contract's earlier trading. Never stitch instruments silently or substitute an arbitrary last observed day across unknown coverage.

Distinguish observed executions, adequately evidenced no-trade intervals, scheduled closure and unknown coverage. Specify how each affects time bars, TPO, opening references, VWAP prefixes and action scans. Quote activity alone is not a full-feed continuity certificate; absent bars alone are not proof of lost trades. Keep the July 2020 two-hour gap unresolved unless evidence resolves it. The previously reported 10,270 missing overnight slots before MBP-1 are mostly outside the new 2020+ study; do not make repairing the old pre-2020 sample a prerequisite.

### 5. Run and verify a new version, preserving the old one

The accepted empirical registry is v1.0.0 and run v1.0.2, manifest `d80935d548abe3cafcd695ec842dc69b1d3391646c2da8fe0db9e935a6c37247`. Preserve its exact inputs, definitions, artifacts and results. The ordinary old validator detects current wiki drift; `wiki-reconciliation/` explains historical reproduction. Do not rewrite frozen hashes to make validation green.

Create a new registry/run identity for changed scanners, clocks, calendars, inputs and study dates, with an explicit evaluation-exposure record. The existing `revise-reporting` path is restricted to historical reporting repairs and refuses further reuse; implement a proper versioned path for this work. Verify every tool, binding and report honors the selected run root rather than silently reading the old default registry.

Freeze the new scope and deterministic, coverage-independent pilot/sample policy before outcomes. Exercise every executable branch in the pilot, including valid, failing, ambiguous and missing-input controls. Then complete all declared 2020+ jobs, with branch/date omissions and reasons visible. A bounded Phase 1 sample is acceptable if explicitly declared; do not present it as a full-archive census or silently exclude difficult years/branches. All-year scan capability must be resumable. The prior 165-job run need not be rerun just for documentation; changed definitions/inputs require their own replay.

Require real native-data integration checks, not just supplied true flags. Test future perturbation, timestamp ties, same-band/candle identity, independent reaction/HVN provenance, event/bucket boundaries, quiet versus unknown intervals, holiday/roll boundaries, overlap deduplication, fresh re-entry, quantity lifecycles and checkpoint invalidation. Include negative cases that reject a simplified proxy when a required method stage is absent. Missing actual account/order records must not turn market observations into fictional fills.

Run the appropriate existing tests and regression probes, then the full suite on final code. Update acceptance to verify reachable scanners, exact branch membership, fresh code/test/input identities, actual native evidence and completed declared populations. Reconcile p/f/u and exclusions at every level; retain observed subsets under missing population scope and keep unknown separate from zero candidates. No pooled family win rate across dependent populations.

### 6. Deliver readable evidence and close the work

Make diagnostic charts show the predicates needed to explain the result: actual TDO/VWAP/band snapshots, 2-minute MSS/FVG candles, profiles and local flow sequences, and local-price detail for distant prior-month levels. Use deterministic examples covering each executable branch and available verdict; visually inspect them. Source cases, research assumptions, observations and outcomes must be distinguishable.

Update PHASE.md, the existing 12 live method pages and their index from the new authoritative manifest/report. Each method must show what is defined, what its scanner does, current n/p/f/u and scope, and exact remaining input limits without needing RESULTS.md open. Keep historical reports identified as historical; do not overwrite their results or create another manually maintained assumptions book. Provide one current completion report, executable reproduction commands and these two tables after family reports:

`family | variant | n | faithful_disagreements | status | report path`

`family | id | verdict | fixture | leakage | proxy-as-faithful | notes`

**Done means:** every branch/unit has an evidence-backed disposition; all implementable market-data paths and published process interfaces are connected and tested; all declared jobs ran or retain an exact externally evidenced data block; final reports/charts reconcile; current documentation agrees with code; raw inputs and the historical run are preserved. No implementable branch may be hidden behind `unavailable_definition`, a fixture-only pass, missing author trade logs or an unexecuted placeholder. A remaining proprietary/input limitation must name the exact operand, citation, inspected local evidence, attempted recovery and affected behavior. Report those separately from software completion. Do not declare full historical method measurement complete while such measurement remains blocked.
