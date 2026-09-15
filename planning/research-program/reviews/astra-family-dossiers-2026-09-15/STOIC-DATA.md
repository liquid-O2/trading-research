# STOIC-DATA — source dossier, 2026-09-15

Reviewed detached commit `62812ad2`; repository unchanged. W = `wiki/method-stoic-data-engine.md`. Raw aliases: DATA = `sources/documents/discretionary/data-engine.pdf`. Page numbers count the cover. R = author rule; E = example; D = discretionary/unpublished. Figure readings and reproducible 3× crops: `FIGURE_MANIFEST.json`, with page-level notes in `other_notes.json`.
Code citations: M = `implementation/src/trading_research/research/method_pack/`; B0.1 = `implementation/src/trading_research/research/rule_discovery/baseline_repairs.py`; A = `implementation/src/trading_research/research/rule_discovery/source_adapters/`; L = `implementation/reports/research-work/P15-04/0d0a57cc4de997b4/attempt-0001/SOURCE_RECONSTRUCTION_LEDGER.json`. F = `planning/research-program/reviews/astra-fidelity-2026-09-15/REVIEW.md`; DIS = `planning/research-program/reviews/phase1-code-review-2026-09-14/DISPOSITION.md`, final “source-fidelity rulings (2026-09-15)” addendum. F finding IDs retain their first-pass meaning. “Match” does not certify author fills or profitability.

## 1. THE AUTHOR'S METHOD AS STATED

- D1 R — Stoic guest contribution published by Sires: pick a trading concept, turn it into a repeatable step-by-step execution process, collect many trades consistently, compare ALL winners against ALL losers, identify recurring differences, refine and repeat. If two people following rules take different trades, the process is not sufficiently defined. DATA pp.1,3,9.
- D2 R — Journaling examines individual mistakes; data collection examines system-level behavior. Both are useful; a single candle/outcome is not reliably predictable while aggregate tendencies can be studied. These are methodological claims, not proof that a concept or dataset guarantees an edge. DATA pp.3–4.
- D3 R/D — Quantify fundamentals: trend-strength score, comparison with its own historical average, custom C-scores across releases, standardized deviations and macro-cycle position. The guide gives categories, not exact indicator universe, weighting, lookbacks, normalization or score/decision formulas. “Inputs are numbers” does not make model choices uniquely objective. DATA p.5.
- D4 E/D — Undated tech-bubble example: compare sentiment with business-cycle overheating/contraction, examine leverage/corporate borrowing/housing/valuation, compare dot-com P/E/capex and then-current economic/rate conditions, conclude the run-up is not structurally a bubble. This is the author’s example verdict at an unspecified time, not our current market assessment or an entry signal. No input table or dates are supplied. DATA p.6.
- D5 R/D — Process and outlook precede discretionary execution. No instrument-specific entry trigger, stop, target, session clock, size or management algorithm is disclosed in pp.3–6. DATA pp.7–8’s asymmetric-risk overlay has its own eligibility and arithmetic; see STOIC-RISK.md rather than inventing a macro trading rule.
- D6 E, full figure register — All9 pages are text/cards and decorative branding; no empirical chart, dated macro dataset, order ticket or account curve. p.3 journaling box, p.4 probability analogy/two outcome cards, p.5 five quantitative-input cards, p.6 undated bubble conclusion, p.7 five risk-ladder cards, p.8 four guardrails, p.9 process summary. Their numbers are illustrative arithmetic, not measured macro-strategy performance. All embedded cards were read at3×; page overview covers vector text/decoration.

## 2. OUR WRITTEN UNDERSTANDING

- W:5 “Phase 1 setup implementation and the acquired historical census are complete.” — Misleading as a fidelity statement: completion is the repository’s engineering census claim, not reproduction of the author. This is a research process, and the macro formula remains unpublished; F, Stoic Data A–F.
- W:5 “These counts describe observed setups with branch-specific input limitations; they are not fills or profitability.” — Accurate limitation: observed setups are not fills or profitability.
- W:5 “The source definitions below retain author-specific boundaries.” — Misleading if read as fully enforced source boundaries; see §3 for the source conditions that remain operational or absent.
- W:5 “Our inferred reconstruction is versioned separately.” — Accurate description of versioning; version separation alone does not establish source fidelity.
- W:11 “| STOIC-DATA | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/STOIC-DATA.md |” — Accurate reported zero entry setups; not evidence of no opportunities or a completed macro model.
- W:12 “| STOIC-DATA | P15-16 process observation (engineering slice, not a family population) | 0 entry setups | not claimed | no entry denominator | implementation/reports/research-work/P15-16/ |” — Accurate non-entry process unit.
- W:16 “| STOIC-DATA | M11 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |” — Accurate scope; retained engineering pass/zero labels do not demonstrate Stoic’s original macro outputs.
- W:24 “This is Stoic's contribution in [DATA] pp.3–8, published in a Sires guide.” — Accurate contribution/provenance; pp.7–8 are the separate risk overlay.
- W:24 “Its ordered loop is:” — Accurate contribution/provenance; pp.7–8 are the separate risk overlay.
- W:28 “Pick the concept, then define a reproducible execution/research process before collecting the sample. ([DATA] p.3.)” — Accurate reproducible-process-first rule; DATA p.3.
- W:28 “[O137](model-definition.md).” — Accurate engineering contracts, but hashes/immutable inventories/revision lineage are our implementation safeguards, not printed Stoic requirements.
- W:28 “Versioned process definitions, immutable observation inventories, hashes and revision lineage are implemented.” — Accurate engineering contracts, but hashes/immutable inventories/revision lineage are our implementation safeguards, not printed Stoic requirements.
- W:28 “The source must still supply the actual process definition.” — Accurate engineering contracts, but hashes/immutable inventories/revision lineage are our implementation safeguards, not printed Stoic requirements.
- W:29 “Collect every observation the same way; distinguish individual journaling from aggregate system-level data. ([DATA] pp.3–4.)” — Accurate uniform collection and journal-versus-aggregate distinction; DATA pp.3–4.
- W:29 “[O146](process-journal.md) · [O148](research-cohort.md).” — Accurate causal record capability/limitation; source does not publish this exact ledger schema.
- W:29 “Uniform inclusion, observation clocks and process/review ledgers are implemented.” — Accurate causal record capability/limitation; source does not publish this exact ledger schema.
- W:29 “Missing contemporaneous source records cannot be created from later outcomes.” — Accurate causal record capability/limitation; source does not publish this exact ledger schema.
- W:30 “Compare all winners and losers, identify recurring differences, refine the process and repeat. ([DATA] pp.3–4.)” — Accurate all-winner/all-loser refinement loop; DATA pp.3–4.
- W:30 “[O153](outcome-metrics.md).” — Accurate supplied-outcome support and no universal entry rule.
- W:30 “Outcome distributions and prior-sample revision checks are implemented for supplied episodes.” — Accurate supplied-outcome support and no universal entry rule.
- W:30 “Stoic's general process remains a research unit with no published universal entry rule.” — Accurate supplied-outcome support and no universal entry rule.
- W:31 “Quantify trend strength, position versus historical averages, custom C-scores, standard deviations and macro cycle.” — Accurate macro input categories and bubble-analysis ordering; DATA pp.5–6.
- W:31 “For the bubble example: identify the cycle → examine leverage/credit/housing/valuation indicators → compare with history → reach a data-based verdict. ([DATA] pp.5–6.)” — Accurate macro input categories and bubble-analysis ordering; DATA pp.5–6.
- W:31 “[O157](macro-indicators.md) · [O158](macro-cycle.md) · [O159](c-score.md) · [O160](standardized-deviation.md) · [O161](trend-strength.md) · [O162](economic-release-vintage.md).” — Accurate conditional record support and missing formulas/series/thresholds; “Proprietary” is stronger than the guide establishes—custom and unpublished is the evidenced description.
- W:31 “Release-vintage admission, supplied macro/cycle/C-score/trend records and defined standardized comparisons are implemented.” — Accurate conditional record support and missing formulas/series/thresholds; “Proprietary” is stronger than the guide establishes—custom and unpublished is the evidenced description.
- W:31 “Proprietary formulas, the full source series and unpublished decision thresholds remain unavailable.” — Accurate conditional record support and missing formulas/series/thresholds; “Proprietary” is stronger than the guide establishes—custom and unpublished is the evidenced description.
- W:33 “The last step is an application of the data process, not a separate intraday entry.” — Accurate non-entry and historical-verdict limitations; DATA p.6 is undated, not necessarily identifiable as any particular historical month.
- W:33 “The source's historical bubble conclusion is not a current market verdict.” — Accurate non-entry and historical-verdict limitations; DATA p.6 is undated, not necessarily identifiable as any particular historical month.
- W:33 “Concepts, a macro label or one unusual release are not standalone trades.” — Accurate non-entry and historical-verdict limitations; DATA p.6 is undated, not necessarily identifiable as any particular historical month.
- W:47 “For the macro application add `release_vintages_recorded AND historical_comparison_defined AND cycle_and_indicator_rules_recorded`.” — Accurate process scope and unavailable macro-model rule/entry specification. Release-vintage controls are our causal operationalization, not a printed formula.
- W:47 “Citation: [DATA] pp.3–6.” — Accurate process scope and unavailable macro-model rule/entry specification. Release-vintage controls are our causal operationalization, not a printed formula.
- W:47 “This measures the research process.” — Accurate process scope and unavailable macro-model rule/entry specification. Release-vintage controls are our causal operationalization, not a printed formula.
- W:47 “Exact macro-model outputs remain unknown without its unpublished rules; no entry/stop/target strategy is disclosed.” — Accurate process scope and unavailable macro-model rule/entry specification. Release-vintage controls are our causal operationalization, not a printed formula.
- W:52 “These pages define the observations, locations, execution branches and process records in the loop.” — Accurate object-navigation limitation.
- W:52 “A shared object does not transfer another author’s entry rule.” — Accurate object-navigation limitation.
- W:63 “Compiled from the cited raw evidence and [OPERATORS].” — Accurate component-score limitation.
- W:63 “Existing formula IDs identify component attachments; their historical scores do not certify this whole method.” — Accurate component-score limitation.
- W:38–44 “process_spec_frozen AND spec_known_at < sample_start_at”, “inclusion_rule_fixed AND uniform_schema”, “all_eligible_observations_retained”, “features_available_before_decisions”, “outcomes_separated_from_inputs”, “aggregate_winner_loser_comparison_recorded”, “revision_uses_only_prior_sample” — Accurate engineering formalization of reproducibility/consistent collection/comparison; strict freezing, causal timestamps and previous-sample revision are prudent operational safeguards, not author-published SQL. DATA pp.3–4.
- W:47 “release_vintages_recorded AND historical_comparison_defined AND cycle_and_indicator_rules_recorded” — Accurate intended causal macro-record contract, operational addition to DATA pp.5–6. A numeric proxy does not recover the source C-score.
- Missing page qualification: the entire source contains no actual dated bubble inputs/formula or empirical data-engine performance chart. No additional mandatory entry rule was found. Navigation/source aliases introduce no method claims.

- Catalog audit: wiki/source-catalog.md:49 “| [DATA] — data-engine.pdf | 9 | Stoic guest contribution: research/macro process and risk overlay; [Stoic — data engine / quantifying fundamentals](method-stoic-data-engine.md) / [Stoic — asymmetric compounding](method-stoic-asymmetric-compounding.md) |” — Accurate page count and broad attribution/scope, verified against the complete raw PDF. This attribution does not certify every caption, implementation claim or traded outcome; the refinements are in §§1–6.
- Catalog audit: wiki/source-catalog.md:5 “Settings, numerical examples, contradictions and incomplete disclosures were retained according to their role.” — Misleading if read as exhaustive retention: this dossier identifies further figure-specific qualifications. The page-count/attribution inventory is accurate; a prior inspection claim cannot substitute for those missing details.


## 3. OUR IMPLEMENTATION

- D1/D2 → B0 M/historical_process_scanners.py:144–170; B0.1:1321–1349; generic process records/O137,O146,O148,O153. F, Stoic Data A–B already covers contract versus absent original dated process records. Match ordered collection/comparison concept; operational hashes, membership and chronology. New audit caution: B0.1:1335 tests comparison-count totals, not whether the source’s recurring differences were substantively identified; a count alone is not completed research.
- D3/D4 → M/historical_process_scanners.py:109–141; M/strategy_context.py:88–101; M/strategy_policy.py:37–38; B0.1:1339–1346. F already documents twelve prior first-release values, equal mean of payroll z and negative CPI z, and explicit is_source_C_score=False. Missing source cycle/leverage/credit/housing/valuation rules. New: averaging two level-based release z-scores cannot reproduce the p.6 multi-factor historical-comparison verdict merely because both are numeric.
- D5/D6 → M/strategy_policy.py:44; A/processes.py:239–260/A/common.py:115 preserves process scope. Match no entry denominator.04 does not add a recovered macro strategy. No source performance statistic exists to match; decorative cover graphics are not an equity curve.

## 4. WHAT WE MISSED

- No additional mandatory author trading rule was found beyond the process/categories already in the wiki. Exact C-score/cycle/indicator formulas and original bubble inputs are genuinely unpublished, not something the repository failed to transcribe.
- The source’s “objective” outlook and bubble conclusion are assertions without dated underlying observations in this PDF. The wiki correctly withholds a current market verdict; a figure manifest should additionally state that no empirical chart/table supplies the missing inputs.
- All-winner/all-loser COMPARISON is more than counting membership. The contract/scanner can validate record structure without establishing that recurring differences were analyzed; this is a limit on our implementation claim, not an undiscovered numerical rule.

## 5. WHAT WE WROTE WRONGLY

- W:31 “Proprietary formulas, the full source series and unpublished decision thresholds remain unavailable.” → “The guide does not publish its custom formulas, full source series, dates or decision thresholds; their proprietary status is not established here.” DATA pp.5–6.
- W:5 “Phase 1 setup implementation and the acquired historical census are complete.” → “The declared research-process contracts are implemented. Stoic’s original macro model and dated input/output history have not been reproduced.” DATA pp.3–6.
- W:30 “Outcome distributions and prior-sample revision checks are implemented for supplied episodes.” → retain and append “A complete source-process review also needs the actual winner/loser comparison and resulting rule revision; count consistency alone does not demonstrate that analysis.” DATA p.3; B0.1:1335–1336.
- Planning/phase-1-5/tasks/P15-16.md:45 “Adapt Refilling touch/memory observations, jetbundle state/transition evidence, Stoic macro/collection and risk records without manufacturing market entries.” — Accurate scope; retain. No source-justified rewrite should convert this into a macro entry task.

## 6. HOW TO TELL IF IT IS ACCURATE

- Runnable contract fixtures: two reviewers following the same frozen specification select the same eligible observations; retain losers as well as winners; no future outcome in features; revisions use completed earlier samples; journal mistakes and aggregate analysis remain separate records. Test actual comparison artifacts, not only counts.
- Owned CPI/payroll first-release vintages can test our12-observation signed-z proxy and publication clocks. They cannot validate undisclosed C-scores or the bubble conclusion without the original leverage/borrowing/housing/valuation/capex/history inputs and model.
- No dated author trade, statistic, frequency or macro performance curve is supplied. Zero entry setups is appropriate scope, not a fidelity score. The source supports reproducibility/process tests and identification of unknown formulas, not a profitability backtest.

| family | variant | n | faithful_disagreements | status | report path |
|---|---|---|---|---|---|
| STOIC-DATA | second source dossier | not a census | not measured | process only; model unpublished | /tmp/astra-family-dossiers-2026-09-15/STOIC-DATA.md |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
|---|---|---|---|---|---|---|

| STOIC-DATA | source review | process only; model unpublished | figures inspected; native replay not run | no new leakage estimate | operational limits explicit | SD14; custom model and supplied research records |
