# STOIC-RISK — source dossier, 2026-09-15

Reviewed detached commit `62812ad2`; repository unchanged. W = `wiki/method-stoic-asymmetric-compounding.md`. Raw aliases: DATA = `sources/documents/discretionary/data-engine.pdf`. Page numbers count the cover. R = author rule; E = example; D = discretionary/unpublished. Figure readings and reproducible 3× crops: `FIGURE_MANIFEST.json`, with page-level notes in `other_notes.json`.
Code citations: M = `implementation/src/trading_research/research/method_pack/`; B0.1 = `implementation/src/trading_research/research/rule_discovery/baseline_repairs.py`; A = `implementation/src/trading_research/research/rule_discovery/source_adapters/`; L = `implementation/reports/research-work/P15-04/0d0a57cc4de997b4/attempt-0001/SOURCE_RECONSTRUCTION_LEDGER.json`. F = `planning/research-program/reviews/astra-fidelity-2026-09-15/REVIEW.md`; DIS = `planning/research-program/reviews/phase1-code-review-2026-09-14/DISPOSITION.md`, final “source-fidelity rulings (2026-09-15)” addendum. F finding IDs retain their first-pass meaning. “Match” does not certify author fills or profitability.

## 1. THE AUTHOR'S METHOD AS STATED

- Q1 R — Only overlay an existing validated process after100+ trades; know sample win rate, average reward:risk and maximum consecutive losses from Monte Carlo. If any is unknown, do not use the overlay. Base risk must never exceed1%; expect intentional equity volatility and avoid overconfidence. DATA pp.8–9.
- Q2 E/R — Printed example first trade risks one baseline unit (1% in the illustration) at1:3; a win banks3 units. Second trade risks original1 plus banked3=4 units; another3R win earns12, cumulative15 units. A second-trade loss after first win leaves cumulative3−4=−1. These are fixed-original-unit arithmetic, not percentages repeatedly rebased on changed equity. DATA p.7.
- Q3 R/D — After the second win reset to1 base unit and repeat. The heading says activation on a “two trade winning streak,” but the ladder increases risk after the FIRST win; preserve both statements and name any chosen branch. First-trade loss, second-trade loss reset, breakeven/partial outcomes and general sizing denominator are not fully specified. DATA p.7.
- Q4 E — “Win streaks are more common than people think, the data proves it” and evaluation targets8–10% achievable in2–4 trades are assertions/illustrations; no measured win-streak distribution, evaluation rule set, fees, loss-limit model or probability of passing is printed. Do not convert this into expected profitability or current prop-firm guidance. DATA pp.7–8.
- Q5 R/D — The overlay does not select market entries, instrument, stop distance, target price or session.3R is the printed example’s reward policy, not a new entry trigger or proof every eligible system has3R outcomes. Eligibility consumes a process/trade/risk ledger, not price bars. DATA pp.3,7–8.
- Q6 E, figure register — All9 pages inspected. p.7’s five magnified cards explicitly print1→3,4→12,total15,worst-case−1,reset1; no chart or ticket proves those returns occurred. p.8 four guardrails give base≤1%,volatile curve,100+ trades,known WR/averageRR/MC loss streak. pp.1–6/9 contain decorative curves/text and the separate data-engine process; no empirical risk-equity or account history.

## 2. OUR WRITTEN UNDERSTANDING

- W:5 “Phase 1 setup implementation and the acquired historical census are complete.” — Misleading as a fidelity statement: completion is the repository’s engineering census claim, not reproduction of the author. The printed ladder can be matched; a generic live compounding system cannot be inferred from it.
- W:5 “These counts describe observed setups with branch-specific input limitations; they are not fills or profitability.” — Accurate limitation: observed setups are not fills or profitability.
- W:5 “The source definitions below retain author-specific boundaries.” — Misleading if read as fully enforced source boundaries; see §3 for the source conditions that remain operational or absent.
- W:5 “Our inferred reconstruction is versioned separately.” — Accurate description of versioning; version separation alone does not establish source fidelity.
- W:11 “| STOIC-RISK | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/STOIC-RISK.md |” — Accurate reported zero entry setups; no price-entry denominator applies.
- W:12 “| STOIC-RISK | P15-16 process observation (engineering slice, not a family population) | 0 entry setups | not claimed | personal records excluded from setup qualification | implementation/reports/research-work/P15-16/ |” — Accurate exclusion of personal risk records from market setup qualification.
- W:16 “| STOIC-RISK | M12 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |” — Accurate non-entry scope; engineering fixture pass is only conditional arithmetic/record validation, not live-system validation.
- W:24 “The risk overlay has different inputs and a different loop, so it stays separate:” — Accurate separate overlay inputs/loop.
- W:26 “1.” — Accurate eligibility and≤1% base guardrail; DATA p.8 uses100+ andp.9 says100. “Observations” should explicitly mean trades from the validated process.
- W:26 “**Establish eligibility.** An existing trading process must have at least 100 observations, known win rate and average R:R, and a Monte Carlo estimate of maximum loss streak; base risk must not exceed 1% ([DATA] p.8).” — Accurate eligibility and≤1% base guardrail; DATA p.8 uses100+ andp.9 says100. “Observations” should explicitly mean trades from the validated process.
- W:27 “2.” — Accurate printed original-unit first leg; DATA p.7.
- W:27 “**First trade.** In the printed illustration, risk one baseline unit (1% of initial account units) for 3R.” — Accurate printed original-unit first leg; DATA p.7.
- W:27 “A win banks three baseline units ([DATA] p.7).” — Accurate printed original-unit first leg; DATA p.7.
- W:28 “3.” — Accurate second leg and cumulative loss arithmetic; DATA p.7. It is−1 from initial baseline, not a1-unit drawdown from the intermediate peak.
- W:28 “**Second trade.** Risk the original one plus the three just banked, four units total.” — Accurate second leg and cumulative loss arithmetic; DATA p.7. It is−1 from initial baseline, not a1-unit drawdown from the intermediate peak.
- W:28 “A 3R win earns twelve more units; a loss leaves the two-trade sequence down one unit ([DATA] p.7).” — Accurate second leg and cumulative loss arithmetic; DATA p.7. It is−1 from initial baseline, not a1-unit drawdown from the intermediate peak.
- W:29 “4.” — Accurate explicit reset and volatility/validation constraints; DATA pp.7–8.
- W:29 “**Reset after the second win.** Return to base risk and repeat.” — Accurate explicit reset and volatility/validation constraints; DATA pp.7–8.
- W:29 “Retain the source's stated volatility and validation constraints ([DATA] pp.7–8).” — Accurate explicit reset and volatility/validation constraints; DATA pp.7–8.
- W:31 “**Not standalone:** a win streak does not generate a trade; this overlay consumes trades admitted by an already validated process.” — Accurate no-entry and supplied-record scope; actual validation is still required.
- W:31 “The [printed risk-state ladder](/workspace/wiki/asymmetric-risk-state.md) and [prior loss-streak validation](/workspace/wiki/loss-streak-validation.md) now have implemented contracts.” — Accurate no-entry and supplied-record scope; actual validation is still required.
- W:31 “Actual prior process, account and Monte Carlo records remain required; generic bootstrap output does not establish the source validation.” — Accurate no-entry and supplied-record scope; actual validation is still required.
- W:33 “The page heading says the overlay activates on a “two trade winning streak,” while its explicit ladder increases risk **after the first 3R win**.” — Accurate preservation of the heading/ladder conflict; DATA p.7. No forced resolution is needed.
- W:33 “Preserve that discrepancy.” — Accurate preservation of the heading/ladder conflict; DATA p.7. No forced resolution is needed.
- W:33 “The following Phase 1 predicate checks the **printed ladder**, not an invented resolution of the heading:” — Accurate preservation of the heading/ladder conflict; DATA p.7. No forced resolution is needed.
- W:50 “Citation: [DATA] pp.7–8.” — Accurate fixed-baseline arithmetic, unspecified other transitions and limited audit scope; DATA pp.7–8.
- W:50 “Units use the initial baseline of the printed illustration, so `3 - 4 = -1` and `3 + 12 = 15`; silently rebasing every percentage on the changed equity produces different arithmetic.” — Accurate fixed-baseline arithmetic, unspecified other transitions and limited audit scope; DATA pp.7–8.
- W:50 “Handling after other outcomes, the sizing denominator in a general implementation, and the heading's alternative activation rule are not fully specified.” — Accurate fixed-baseline arithmetic, unspecified other transitions and limited audit scope; DATA pp.7–8.
- W:50 “The generic overlay is therefore only partially reconstructable.” — Accurate fixed-baseline arithmetic, unspecified other transitions and limited audit scope; DATA pp.7–8.
- W:50 “This is a rule/arithmetic audit, not a new simulation or a profitability claim.” — Accurate fixed-baseline arithmetic, unspecified other transitions and limited audit scope; DATA pp.7–8.
- W:55 “These pages define the observations, locations, execution branches and process records in the loop.” — Accurate object-navigation limitation.
- W:55 “A shared object does not transfer another author’s entry rule.” — Accurate object-navigation limitation.
- W:64 “Compiled from the cited raw evidence and [OPERATORS].” — Accurate component-score limitation.
- W:64 “Existing formula IDs identify component attachments; their historical scores do not certify this whole method.” — Accurate component-score limitation.
- W:36–46 exact clauses “validated_process AND prior_sample_n >= 100”, “win_rate_known AND average_rr_known AND mc_loss_streak_known”, “base_risk_fraction <= 0.01 AND base_risk_fraction > 0”, first “risk_units = 1 AND planned_reward_r = 3”, second “first_trade_closed AND first_trade_result_units = 3”/“risk_units = 4 AND planned_reward_r = 3”/“first_trade_close_at < decision_at”, reset “second_trade_result_units = 12”/“next_risk_units = 1”, “ELSE NULL” — Accurate printed-ladder contract with operational chronology/positive-base convention, not a fully specified general money-management algorithm. DATA pp.7–8.
- Missing page qualification: “worst case” is local to the win→loss two-trade illustration, not a global lifetime drawdown bound; the source’s2–4-trade evaluation claim has no frequency/probability evidence. Navigation and source aliases add no rule.

- Catalog audit: wiki/source-catalog.md:49 “| [DATA] — data-engine.pdf | 9 | Stoic guest contribution: research/macro process and risk overlay; [Stoic — data engine / quantifying fundamentals](/workspace/wiki/method-stoic-data-engine.md) / [Stoic — asymmetric compounding](/workspace/wiki/method-stoic-asymmetric-compounding.md) |” — Accurate page count and broad attribution/scope, verified against the complete raw PDF. This attribution does not certify every caption, implementation claim or traded outcome; the refinements are in §§1–6.
- Catalog audit: wiki/source-catalog.md:5 “Settings, numerical examples, contradictions and incomplete disclosures were retained according to their role.” — Misleading if read as exhaustive retention: this dossier identifies further figure-specific qualifications. The page-count/attribution inventory is accurate; a prior inspection claim cannot substitute for those missing details.


## 3. OUR IMPLEMENTATION

- Q1 → B0/B0.1 M/historical_process_scanners.py:225–239; M/method_slices/m12.py:23–36,52–96; O154/O155 supplied-record contracts. F, Stoic Risk A1 already records faithful eligibility/chronology conditional on genuine records. New: fixture n100,WR.55,averageRR2,MCmaxloss8 and artificial09:30/10:01/11:01 clocks are fabricated TEST inputs explicitly, not recovered author statistics or session rules (m12.py:40–90).
- Q2/Q3 → M/historical_process_scanners.py:240–242; M/method_slices/m12.py:98–130. F, Stoic Risk A2 already confirms1→4→1 and heading discrepancy. Match printed fixed-unit arithmetic; missing other outcome transitions because source does not define them. Do not quietly infer martingale, two-wins-before-escalation or changed-equity percentages.
- Q4/Q5/Q6 → M/strategy_policy.py:42–44/A/common.py:116/A/processes.py:239–260 retains personal/process scope. Match no generated entries or claimed real account. No source empirical streak probability, costs, drawdown-barrier or pass-frequency model is implemented, because none is supplied; generic Monte Carlo tools are not evidence of the author’s unpublished sample.

## 4. WHAT WE MISSED

- No additional mandatory arithmetic/eligibility rule was found missing from the wiki’s printed-ladder contract. The heading conflict, fixed baseline and unknown other transitions are already documented; do not count them again as omissions.
- The source’s “worst case” language lacks a distinction between net result from the start and drawdown from the first-win peak. The wiki arithmetic is correct but could state that limit explicitly. This is a mathematical qualification of the example, not a new author rule.
- The source offers no sample supporting its streak-frequency/evaluation-speed claims. An absence of empirical proof must not be filled with the synthetic fixture’s55%/2R/eight-loss inputs.

## 5. WHAT WE WROTE WRONGLY

- W:26 “An existing trading process must have at least 100 observations” → “An existing trading process must have at least100 consistently recorded prior trades.” DATA pp.8–9. Unrelated market snapshots do not satisfy the source’s sample guardrail.
- W:28 “a loss leaves the two-trade sequence down one unit” → retain and append “That is net from the initial baseline; it gives back four units from the intermediate three-unit profit peak.” DATA p.7 arithmetic3−4=−1.
- W:5 “Phase 1 setup implementation and the acquired historical census are complete.” → “The printed-ladder arithmetic and supplied-record eligibility contracts are implemented; no entry census or complete live risk system is claimed.” DATA pp.7–8.
- Planning/phase-1-5/tasks/P15-16.md:45’s no-manufactured-market-entry instruction is accurate. Preserve it and label any future loss-branch/reset/equity-denominator extension as an explicit research variant, not recovered source law.

## 6. HOW TO TELL IF IT IS ACCURATE

- Exact runnable arithmetic fixture: fixed E0=100,B=1; win first→103; second risk4,win12→115; win then loss→99; after second win next risk returns1. If every percentage silently uses new equity, it fails the printed arithmetic. Both heading and explicit ladder remain recorded.
- Eligibility negative tests:99 prior trades; missing WR/averageRR/MC; future-dated validation; first win still unrealized; base>1%; unrelated process IDs. All can run on supplied/synthetic records now, labeled tests. Require genuine process records for real qualification.
- Drawdown fixture:103→99 is4 original units (about3.88% of intermediate equity), despite net−1 original unit; no global drawdown cap follows. Do not generalize “worst case” across arbitrary loss sequences.
- No dated author trades or demonstrated streak frequency exist in this source. Owned NQ market data cannot supply personal validation or prove2–4-trade evaluation passes; those require actual trade outcomes, account rules/costs and an explicitly declared simulation design.

| family | variant | n | faithful_disagreements | status | report path |
|---|---|---|---|---|---|
| STOIC-RISK | second source dossier | not a census | not measured | printed arithmetic supported | /tmp/astra-family-dossiers-2026-09-15/STOIC-RISK.md |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
|---|---|---|---|---|---|---|
| STOIC-RISK | source review | printed arithmetic supported | figures inspected; native replay not run | no new leakage estimate | operational limits explicit | SD15; fixed-unit ladder, peak drawdown, unspecified branches |
