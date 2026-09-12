# Source reread and dated reconstructions

**Later correction:** the [profile coverage audit](PROFILE_COVERAGE_CHECK.md) distinguishes documented rules from incomplete code, connects Sires's overnight profile to the clock already recorded in O011, and corrects the November 20 entry interpretation: the displayed short is at the high sweep; a later MSS is not a required wait for that entry. Further parameter searches are deferred.

The earlier blanket “source hole” description overstated what was missing. The sources contain usable intent, settings and a research process. We can implement explicit hypotheses for unspecified details and compare them with the dated figures. On September 12, the user authorized this approach and deprioritized macro work.

Two reconstructions now run on acquired NQ data. Their measurements are [documented with the figures](reconstructions/README.md). They are source-fit examples, not historical trade results. The original method-pack cohort still has N=0 because these retrospective examples do not create a complete automatic selector or an actual execution journal.

## AAPL was an example

[The math behind auction market theory](../../../../sources/documents/discretionary/the-math-behind-auction-market-theory.pdf) p.3 explicitly connects the AAPL illustration to an NQ application; p.16 calls the 20,000-event AAPL sample illustrative. Requiring AAPL and at least ten levels for every use was our error.

M10 and O163/O165/O166 now permit NQ or another declared native instrument. Book depth is checked against the scope declared for the observation. Transition counts must belong to the same instrument; matching the printed 84/12 percentages by coincidence is no longer rejected. The live formulas, wiki, implementation and selector audit were corrected together.

The remaining source gap is narrower: p.10 supplies qualitative B/A/D/E/W meanings but no numerical observation windows, aggression/response thresholds or label priority. These can become explicitly named research classifiers. The acquired NQ MBP-1 schema has best-price updates and native actions but no order IDs or deeper book. It cannot provide an exact full order lifecycle or off-touch cancellations. A top-of-book reconstruction must state that scope instead of claiming unseen events.

## Stoic's process is present

[The Data Engine](../../../../sources/documents/discretionary/data-engine.pdf) p.3 specifies the process: select a concept, make its execution steps repeatable, collect every trade consistently, compare winners and losers, refine and repeat. We do not need Stoic's private trade journal to apply that process to our own research. The two source-fit cases are an initial calibration record, not a substitute for the ensuing trade sample.

The genuinely unpublished items on p.5 are the custom fundamental score formulas, series choices, historical lookbacks, weights and cycle definitions. Macro reconstruction is outside this pass, following the user's direction.

For the p.7 risk ladder, the original baseline arithmetic is available: risk 1 unit; a 3R win banks 3; risk 4; a second 3R win adds 12; reset to 1. A loss on the second trade leaves net −1. The heading says activation after a two-trade winning streak, whereas the printed ladder raises risk after the first win. That ambiguity requires choosing and labeling a risk variant if implemented. The p.8 inputs—100+ closed trades, their win rate/average RR and a Monte Carlo loss-streak estimate—must come from the underlying tested process. They are our research dependencies, not evidence that the workflow definition is absent.

## Intended attempts can be recovered

The [Green Bird raw-post collection](../../../../sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf) provides more than generic setup descriptions:

| Source case | Recovered intent | What still needs reconstruction |
|---|---|---|
| 2026-02-24, p.33, post `2026329904690712970` | Close above London and Asia highs, retrace to VWAP, enter long; 30-point stop. The reply limits VWAP use to continuations. | Exact session clocks, price basis, order and fill. Original result is 150 points, while the p.34 reply says 100; neither supplies a planned target. |
| 2025-11-20, p.31 post `1991589280142315537`, p.43 figure | Later sweep of 09–10 highs, failed breakout, MSS/FVG entry, opposing 09–10 lows. | Exact MSS/entry mechanics and fill; the screenshot does identify the intended later attempt. |
| 2026-09-01/02, pp.23–25 | Bearish NYAM retracement at 50–61.8%, sweep above PDL, five-minute close back below, enter on retracement or after a few points, stop above PDL/swing high for the cited case, target lows. | Exact chosen swing/impulse and execution records. This is more specific than a generic missing risk rule. |

The November 20 chart is **two-minute**, as shown by both its toolbar and instrument header. The earlier chart review incorrectly called it three-minute. The five-minute rule in later PDL replies is a different source case; it should not erase this MSS/FVG figure's two-minute geometry.

The [case ledger](reconstructions/source-case-ledger.jsonl) records the recovered intent and original post timestamps. These are retrospective source annotations. A post published after the trade cannot act as a pre-trade historical selector.

## VWAP settings and reasoning

[Sires VWAP Lesson 10](../../../../sources/documents/discretionary/vwap-lesson-10.pdf) p.8 visibly specifies Session anchoring, `(H+L+C)/3`, zero offset, standard-deviation bands and chart timeframe with close confirmation. The inputs image enables multipliers 1 and 2, with 3 unchecked; the caption/prose mentions 2.5. That discrepancy remains explicit. We did not fit deviation bands in this pass.

The lesson explains daily session VWAP and catalyst/swing anchoring on p.7; pp.4–6 combine deviation location with absorption/CVD confirmation. Green Bird's p.33 continuation reply instead uses VWAP as the auction average after the session-high breakout. Sires' platform settings are a useful reconstruction hypothesis, but do not establish Green Bird's configuration.

For February 24, testing four resets and four price bases against 13 readable points favors previous-day 18:00 New York among the tested resets. HLC3 fits with **1.485-point RMSE** and **3.005-point maximum error**. OHLC4 is slightly closer (1.390 RMSE), but that difference is smaller than one source pixel (about 0.76 points); the source cannot identify the exact price basis at this resolution. Midnight HLC3 fits at 3.495 RMSE. Cash-open HLC3 fits much worse and cannot cover the five pre-open points.

The three tested London windows (02–05, 03–05, 02–08), with Asia 20–00, all give the first close above both highs at the end of the 09:44 minute (09:45 availability) and the first touch of the prior completed VWAP during 10:00 (10:01 bar-end evidence). That matches the visible sequence without resolving which London clock the author used.

## Verification and scope

The primary assistant read the retained guide PDFs and raw-post records and personally checked both reconstructed figures against the embedded originals. No subagents performed these checks. The available Stoic/VWAP documents are companion guides; a full spoken transcript was not found in the local source set. Linked YouTube pages did not expose usable captions in the accessible session, so no claim of full-video review is made.

The reconstruction scripts check complete minute membership, native contract identity, tick metadata, gap formation times and post-decision touch logic. Inputs, outputs, source files and builders are hashed. Research choices remain in the reconstruction artifacts; only the source-supported AAPL/NQ correction changed FORMULAS. No macro acquisition, Phase 2 work, execution or source-faithful success-rate claim was added.

All 11 focused M10 checks and all 10 public-command checks passed after the correction. These verify implementation behavior, not method performance.

Run `python implementation/tools/reconstruct_source_cases.py` from `/workspace` using the runtime recorded in [manifest.json](reconstructions/manifest.json).
