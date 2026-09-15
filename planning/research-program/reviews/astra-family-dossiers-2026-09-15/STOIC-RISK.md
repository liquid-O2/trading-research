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
- W:31 “The [printed risk-state ladder](asymmetric-risk-state.md) and [prior loss-streak validation](loss-streak-validation.md) now have implemented contracts.” — Accurate no-entry and supplied-record scope; actual validation is still required.
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

- Catalog audit: wiki/source-catalog.md:49 “| [DATA] — data-engine.pdf | 9 | Stoic guest contribution: research/macro process and risk overlay; [Stoic — data engine / quantifying fundamentals](method-stoic-data-engine.md) / [Stoic — asymmetric compounding](method-stoic-asymmetric-compounding.md) |” — Accurate page count and broad attribution/scope, verified against the complete raw PDF. This attribution does not certify every caption, implementation claim or traded outcome; the refinements are in §§1–6.
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

===== REVIEW.md — part 1/2 =====
# Second source-fidelity review — 2026-09-15

## Result

Twelve source dossiers are complete. The written method pages generally preserve the authors’ qualitative frameworks better than the historical scanners do. The strongest new implementation discrepancy is Jumbo’s extension-band arithmetic. The strongest new evidence findings concern conflicting captions, live versus drawn order prices, unresolved source variants, and incompatible statistics panels. None of the existing engineering counts establishes author-exact trades, fills or profitability.

Repository reviewed: `/tmp/astra-family-dossiers-2026-09-15/repo`, detached commit `62812ad285e7583fab421c03296b3cf2f55faae5`. No repository files were changed. `/workspace` was treated as read-only; git reads used `GIT_OPTIONAL_LOCKS=0` because the worktree metadata lives there. All generated reports, crops, notes and verification receipts are under `/tmp/astra-family-dossiers-2026-09-15/`; PyMuPDF is isolated under `/tmp/astra-pymupdf`.

Authority: [first review](repo/planning/research-program/reviews/astra-fidelity-2026-09-15/REVIEW.md) and the final “source-fidelity rulings (2026-09-15)” addendum in [DISPOSITION](repo/planning/research-program/reviews/phase1-code-review-2026-09-14/DISPOSITION.md). F01–F20 retain their original meanings. This pass adds source evidence and does not silently reverse a ruling. A chosen operational baseline remains a research choice even when a source figure shows different geometry.

## Coverage and reproducibility

- Read all41 PDFs completely:711 pages, including318 pages across26 SIRES lessons,183 Jumbo pages including duplicate compilations,60 Green Bird archive pages,52 Saint pages,16 Member,33 Keani,24 Refill,16 Jetbundle and9 Stoic. Read both September14 JSON posts and all seven photos. Page numbers include covers.
- Read every source image page and enlarged chart/ticket/annotation regions. [FIGURE_MANIFEST.json](FIGURE_MANIFEST.json) records PDF-point or raster-pixel crop coordinates, magnification, source/page and reading. Numerical readings use detailed crops, not page thumbnails. Repeated images are identified in [DUPLICATE_FIGURES.json](DUPLICATE_FIGURES.json):62 pixel-identical images in the secondary Jumbo PDFs map to inspected archive figures; duplicate page text was read separately.
- The manifest has2,769 records:2,139 inspected views,62 duplicate-image readings,317 additional detail renders whose readings are recorded at inspected parents,250 unused supplemental renders and one superseded empty crop. These are rendering records, not2,769 independent charts. Unused crops are explicitly labeled; they are not counted as additional inspections.
- [COVERAGE_CHECK.json](COVERAGE_CHECK.json) verifies all711 page overviews and records source SHA-256 hashes. Detailed readings are in [jj_notes.json](jj_notes.json), [jr_notes.json](jr_notes.json), [gb_notes.json](gb_notes.json), [sires_notes.json](sires_notes.json) and [other_notes.json](other_notes.json). [SOURCE_INVENTORY.json](SOURCE_INVENTORY.json) records page dimensions and embedded-image bounds.
- The requested reference-images directory contains only a Zerano SPX image in this checkout. Relevant Jumbo/GB evidence is in the named PDFs, owned media frames and September14 photos. No unrelated reference image was substituted.
- Genuinely unreadable fields remain unknown: examples include GEX p.16 node numbers, partly clipped K18 p.10 quarter-tick labels, GB p.46 fig1 exact prices/date, several overlapping Jumbo ticket labels and Keani dashboard average-win decimals. No guessed value is treated as a fixture.

## New findings and refinements

Severity reflects impact on source fidelity, not expected trading returns. Detailed rule-by-rule mappings, exact wiki quotations and proposed replacements are in the linked dossiers.

| ID | Finding and evidence | Prior-review relationship |
|---|---|---|
| SD01 HIGH | **Jumbo extension band is one full parent width too close.** Source drawings use H+[1.33,1.66]W / L−[1.66,1.33]W. Historical B0 uses0.33/0.66 at `method_pack/historical_price_scanners.py:85`; B0.1 repeats it at `baseline_repairs.py:690`. Standalone `objects/range_geometry.py:680` uses1.33/1.66. For H110/L100 the source upper band123.30–126.60 becomes113.30–116.60 in historical enumeration. Raw TBR pp.10,20–21; [JJ-TBR §3](JJ-TBR.md). | New J21; separate from F08’s10:00 cutoff and F11’s confirmation restriction. |
| SD02 MEDIUM | **Quarter-location and timing labels need source scope.** Jumbo permits EQ/quadrants and both EQ directions; “EQ-only source location” describes the baseline, not the author. The raw Jan28 ticket’s14:53:46 timestamp has no printed zone; SessionStat has aggregation/cross-midnight limitations. TBR pp.12–15,27–29; SS pp.7–8; JR pp.3,71. [JJ-TBR](JJ-TBR.md). | J22 adds source-location wording/side evidence; preserves F08/F11/F18/F19. The35% footprint filter already exists in wiki/footprint.md:5. |
| SD03 MEDIUM | **GB London stop is below the recent higher low, above the earlier sweep.** September14 photo1 shows live28903.75/drawn stop28875.25 against early sweep≈28827. Mandatory retest is explicit. Photo2 live short29081.75 differs from drawing29081.50; photo3 is another account. No plotted target proves a realized exit. [GB-FAIL](GB-FAIL.md), P14 post2099513366326730859/photos1–3. | Refines F14 and the accepted retest/operational-stop rulings; F06’s undispatched A1–A4 remains. |
| SD04 MEDIUM | **GB result/order evidence cannot be merged.** February24 VWAP caption150points conflicts with February25 reply30pointstop/100pointwin. September11 golden-pocket drawing29382/29347 has its stop inside the pocket; live entries and pending targets vary by photo/account. GB pp.33–34; P11 post2099503614372741234/photos1–3. [GB-VWAP](GB-VWAP.md), [GB-SCALP](GB-SCALP.md). | Textual profit conflict and inside-pocket stop were already in first-review family findings; new crops establish exact artifact identities. F01/F06/F14 remain. |
| SD05 HIGH | **SIRES branch identity remains wrong for clean squeeze.** CONT p.11 excludes failure AND retest; current clean_squeeze requires a pullback. Passive OFM p.14 permits no aggression at failure, while BIG’s long-gamma fade omits own reward and GEX p.18 asks for it. These are distinct source branches/variants. [SIRES §§1–3](SIRES.md). | F02 already identifies clean-squeeze inversion; this pass adds contradictory long-gamma variants and passive replay evidence. |
| SD06 HIGH | **SIRES04 metadata does not repair source geometry.** A/sires.py:81–115 reads absent replenishment fields; its stop_four_stage branch is outside that filter. Lines55–59,125–128 write unsigned1R/2R/3R distances without changing target prices, with integer casts on price inputs. Source3tick neighborhood is not a count of additions. STOP pp.6–15; OFM pp.6,12,14. [SIRES §3](SIRES.md). | F03’s dropped-row defect remains; adds target-distance versus price and branch-scope consequences. F09 thesis/location proxies remain. |
| SD07 MEDIUM | **SIRES captions sometimes describe outcomes absent from the visible ticket.** OFM p.14 says take-profit but shows an open losing long andx8 replay; NYAM pp.8–9 holds58tick/$290risk while extending40→106tick target; STOP mixes Nov7/Nov13 positions; CONT p.9 checks POC after the trade. [SIRES S20,S24–S29](SIRES.md). | New evidence-state/causality refinements; prevents captions or cursors becoming fill/time fixtures. |
| SD08 MEDIUM | **SIRES source statistics and risk claims need separate denominators.** MAMT appendix has contract-group either/both ON and IB rates distinct from73% midpoint; ANAT’s nine-trade equity reaches−$480 despite a declared$250cap; STOP’s five-loss cartoon exceeds−4R if one day. MAMT pp.20–26; ANAT pp.4–10; STOP pp.1,14. [SIRES](SIRES.md). | Exact figure qualifications are new; general denominator separation,40% VA,40–80 trades and30-session review already exist in object wiki pages. |
| SD09 MEDIUM | **Saint’s bridge route has specific shelf endpoints.** RTVP p.8 travels upper edge of lower shelf→lower edge of upper shelf. TRAP MNQ drawing is entry29729.25/SL29736.75/TP29678.75,7.5/50.5points, and its UTC-midnight execution chart differs from later profile cursors and a separate Sim2 DOM. [SAINT-AMT](SAINT-AMT.md). | Refines F04’s profile/control/Asia failures; no new invented numerical profile classifier. |
| SD10 MEDIUM | **Member p.13 shows two SELL drawings and one BUY, despite “three shorts” caption.** Exact ticket sides matter for the HTF-demand counterexample. Four displayed payouts sum$7,043.75 across June/July, not the full headline account cohort. K10 pp.3,13. [MEMBER-TWO-REASONS](MEMBER-TWO-REASONS.md). | New chart/account scope; F15 and already-documented1.5R-versus9.6R contrast remain. |
| SD11 MEDIUM | **Keani source says OR in prose, AND in caption.** AVG p.21 allows POC or previous VAH; p.22 says both. The dashboard151/102/49 and hypothetical20trade70%/5R examples are different populations; p.30 pretrade rhetoric includes post-session tasks. [KEANI-OPEN-ABOVE-VALUE](KEANI-OPEN-ABOVE-VALUE.md). | New source-conflict/denominator detail; F16’s11:00,60minute,strict-value-rise and A-width proxies remain. |
| SD12 HIGH evidence | **Refill source panels are not one consistent replication target.** p.5 is dated MNQ10Jan2025,09:36–09:44 ET. Prose156/79 split conflicts with half/half figures; p.15 adds rest_min=30/variant=3/t_minutes=30 and largestloss−$300.62; p.19 andp.20 pass rates differ; p.21 daily-stop gains are+3,+7,+11,+13,+14,+13points, and payout panels disagree with p.23. [REFILL-STUDY](REFILL-STUDY.md). | F10/F20 still block population/chronology equivalence; corrects first-review “undated” characterization. Do not select the favorable panel or invent undocumented engine semantics. |
| SD13 MEDIUM | **Jetbundle chart is an AAPL-quantile heuristic and a displayed slice.** MATH p.10 plots events5,000–19,999 of a stated20,000-event dataset; p.11 blanks are unprinted cells, not zeros. Sires chart p.14 gives Aug21,2026; p.13 is a19.75/158point8R drawing. [JETBUNDLE-STATES](JETBUNDLE-STATES.md). | New plotted population/date/precision constraints; no source entry algorithm is disclosed. |
| SD14 LOW | **Stoic custom inputs are unpublished, not proven proprietary formulas.** DATA pp.3–6 gives process and undated macro categories without formulas/dated input table; all-winner/all-loser comparison exceeds record-count validation. [STOIC-DATA](STOIC-DATA.md). | No additional mandatory trading rule found missing; preserve non-entry scope. |
| SD15 LOW | **Stoic ladder is correct only within its printed fixed-unit path.** After+3units, the second trade risks4units: loss means net−1 from start but−4 from peak; win gives total+15 then reset. Heading’s “two wins” conflicts with escalation after the first. Other loss/reset paths remain unspecified. DATA pp.7–8. [STOIC-RISK](STOIC-RISK.md). | Existing wiki already preserves arithmetic/heading conflict; adds peak-drawdown qualification, not a new source rule. |

## Written understanding and suggested rewrites

Each dossier quotes the strategy-bearing wiki sentences, gives a verdict and raw location, maps the source rule to B0/B0.1/04, separates true corpus omissions from missing wiring, and proposes exact replacement text. Green Bird’s SOURCE_ADDITIONS sentences are divided between GB-FAIL and GB-SCALP with cross-references; GB-VWAP has no new September14 source trigger. The source catalog’s41 page counts and broad attributions are correct. Its general claim that settings/contradictions were retained needs the additional qualifications above; a catalog inspection assertion cannot replace figure-specific evidence.

Do not rewrite “operational” into “source-exact” merely because a baseline choice was approved. In particular, preserve the source London retest but label two5-minute closes/short mirror and far-sweep stop as choices; preserve the actual inside-pocket GB stop; keep Jumbo before10:00 scoped to the extended case; retain SIRES variants and unpublished CVD/gamma/platform inputs; keep Jetbundle and Stoic as process/risk methods.

## What can actually be tested

- **Now, without new market data:** source-figure arithmetic, ordered geometry, ticket type/side/price identity, caption contradictions, fixed-unit risk arithmetic, missing-versus-zero matrix cells, exact quotations and citation identity. Dossiers provide the concrete numbers and negative examples.
- **On owned native history where the exact date/contract is covered:** selected pre-September3,2026 NQ/ES price/flow sequences, source clocks after verification, same-parent geometry and causal availability. The12 dossiers list dated examples. Matching an NQ price path does not authenticate an MNQ fill, platform CVD setting or private account action.
- **Needs additional data or source disclosure:** September8–14,2026 cases beyond the owned endpoint; full-depth/hidden-reserve inference and platform settings; author fill/account records; exact4537/3249-day Jumbo cohorts; ES2021–24 MAMT contract cohorts; Refill’s235-session original classifier/fill engine; AAPL20,000-event labels; Stoic’s original macro inputs and complete ladder policy.
- No native replay, profitability backtest, new historical census or repository checker was run. Existing counts are cited receipts only. [FINAL_VERIFICATION.json](FINAL_VERIFICATION.json) checks731 exact wiki quotation fragments, all six sections and both tables in each dossier, the220-line limit, cited code-file existence, page/crop coverage, source hashes and unchanged tracked repository state. It does not validate a strategy edge.

## Dossier index

| Strategy | Dossier | Lines |
|---|---|---:|
| JJ-TBR | [JJ-TBR.md](JJ-TBR.md) | 161 |
| GB-FAIL | [GB-FAIL.md](GB-FAIL.md) | 120 |
| GB-VWAP | [GB-VWAP.md](GB-VWAP.md) | 85 |
| GB-SCALP | [GB-SCALP.md](GB-SCALP.md) | 96 |
| SIRES | [SIRES.md](SIRES.md) | 178 |
| SAINT-AMT | [SAINT-AMT.md](SAINT-AMT.md) | 131 |
| MEMBER-TWO-REASONS | [MEMBER-TWO-REASONS.md](MEMBER-TWO-REASONS.md) | 101 |
| KEANI-OPEN-ABOVE-VALUE | [KEANI-OPEN-ABOVE-VALUE.md](KEANI-OPEN-ABOVE-VALUE.md) | 106 |
| REFILL-STUDY | [REFILL-STUDY.md](REFILL-STUDY.md) | 122 |
| JETBUNDLE-STATES | [JETBUNDLE-STATES.md](JETBUNDLE-STATES.md) | 108 |
| STOIC-DATA | [STOIC-DATA.md](STOIC-DATA.md) | 93 |
| STOIC-RISK | [STOIC-RISK.md](STOIC-RISK.md) | 90 |

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
|---|---|---|---|---|---|
| JJ-TBR | second source dossier | not a census | not measured | material divergence | /tmp/astra-family-dossiers-2026-09-15/JJ-TBR.md |
| GB-FAIL | second source dossier | not a census | not measured | partial source fidelity | /tmp/astra-family-dossiers-2026-09-15/GB-FAIL.md |
| GB-VWAP | second source dossier | not a census | not measured | sequence supported; parameters operational | /tmp/astra-family-dossiers-2026-09-15/GB-VWAP.md |
| GB-SCALP | second source dossier | not a census | not measured | entry trigger unresolved | /tmp/astra-family-dossiers-2026-09-15/GB-SCALP.md |
| SIRES | second source dossier | not a census | not measured | material divergence and source conflicts | /tmp/astra-family-dossiers-2026-09-15/SIRES.md |
| SAINT-AMT | second source dossier | not a census | not measured | qualitative method; unrecovered selection | /tmp/astra-family-dossiers-2026-09-15/SAINT-AMT.md |
| MEMBER-TWO-REASONS | second source dossier | not a census | not measured | partial fidelity | /tmp/astra-family-dossiers-2026-09-15/MEMBER-TWO-REASONS.md |
| KEANI-OPEN-ABOVE-VALUE | second source dossier | not a census | not measured | sequence supported; variants unresolved | /tmp/astra-family-dossiers-2026-09-15/KEANI-OPEN-ABOVE-VALUE.md |
| REFILL-STUDY | second source dossier | not a census | not measured | source population unreproduced | /tmp/astra-family-dossiers-2026-09-15/REFILL-STUDY.md |
| JETBUNDLE-STATES | second source dossier | not a census | not measured | process only; classifier unrecovered | /tmp/astra-family-dossiers-2026-09-15/JETBUNDLE-STATES.md |
| STOIC-DATA | second source dossier | not a census | not measured | process only; model unpublished | /tmp/astra-family-dossiers-2026-09-15/STOIC-DATA.md |
| STOIC-RISK | second source dossier | not a census | not measured | printed arithmetic supported | /tmp/astra-family-dossiers-2026-09-15/STOIC-RISK.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
|---|---|---|---|---|---|---|
| JJ-TBR | source review | material divergence | figures inspected; native replay not run | no new estimate | operational limits explicit | SD01/SD02; extension arithmetic, quarter locations, source clocks |
| GB-FAIL | source review | partial source fidelity | figures inspected; native replay not run | no new estimate | operational limits explicit | SD03; required retest, recent-structure stop, distinct live/drawn artifacts |
| GB-VWAP | source review | sequence supported; parameters operational | figures inspected; native replay not run | no new estimate | operational limits explicit | SD04; one narrated setup,100/150 result conflict |
| GB-SCALP | source review | entry trigger unresolved | figures inspected; native replay not run | no new estimate | operational limits explicit | F01/F06/F14; contextual examples and unwired operational A4 |
| SIRES | source review | material divergence and source conflicts | figures inspected; native replay not run | no new estimate | operational limits explicit | SD05–SD08; F02/F03/F09 still apply |
| SAINT-AMT | source review | qualitative method; unrecovered selection | figures inspected; native replay not run | no new estimate | operational limits explicit | SD09; shelf bridge geometry and Asia ticket identity |
