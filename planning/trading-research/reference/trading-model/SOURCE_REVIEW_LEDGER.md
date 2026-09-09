# Source review ledger

Status: supplied-source review complete. Every supplied PDF page received full textual and actual visual review; every supplied text/source passage was read to its end. Intrinsically cropped/unreadable content and absent attachments remain explicit below. No empirical trading tests, production implementation or trained edge is claimed. Current design focus is Context, Location and supporting layers; detailed Response development remains deferred.

Review conducted 2026-09-05–06 UTC. Bundle README describes a 2026-09-06 upload; preserve the timestamp discrepancy as provenance.

## Reconciliation

52 actual bundle files: 50 entries in the current manifest and two extra controls README.md and SOURCE_MANIFEST.json. The initial manifest contained 49 entries; its current version adds only the user-supplied conversations/Design robust feature levels.md received during review. The original 49 entries remain unchanged; all 50 current entries match file hashes/sizes. The control-file change and both verified versions are recorded in review/source-control-versions/version_reconciliation.json. No source was rewritten by this task. 39 PDFs, 580 pages. ZIP safely extracted to isolated review directory: 83 regular text/source members, 51,659 lines; no binary assets. All 83 members were statically read; no bundled code was executed.

## Exact file coverage

| Exact path | Extent | Text reviewed | Visual reviewed | Findings and unresolved |
|---|---|---|---|---|
| `/workspace/sources/documents/README.md` | 30 lines | 1-30 | N/A (see attachment limitations) | Bundle scope/control reconciliation; Upload-date discrepancy is recorded; no independent trading mechanism. |
| `/workspace/sources/documents/SOURCE_MANIFEST.json` | 252 lines | 1-252 | N/A (see attachment limitations) | Bundle hash/size reconciliation; Initial 49-entry manifest changed to 50 entries during review by addition of the user-supplied DRF conversation. Original 49 entries are byte-identical under the verified original serialization; both control versions recorded. Current full 252 lines read and all 50 file hashes/sizes reconciled; no source content rewritten by this task. |
| `/workspace/sources/documents/conversations/Develop Trading Model.md` | 1540 lines | 1-1540 | N/A (see attachment limitations) | DTM-U01–DTM-U05; DTM-A01–DTM-A18; Both user posts and all assistant content read; historical attachment/tool descriptions are not missing original pixels/results. |
| `/workspace/sources/documents/conversations/conversation_export (1).md` | 1306 lines | 1-1306 | N/A (see attachment limitations) | CEX-01..CEX-27; Bracketed tool calls and attachment descriptions do not contain their original results/pixels; historical data claims require audit. |
| `/workspace/sources/documents/conversations/conversation_raw_log.md` | 1072 lines | 1-1072 | N/A (see attachment limitations) | CRL-01..CRL-20; Part A has user queries only; earlier assistant replies absent. Attachments reviewed as separate supplied files. |
| `/workspace/sources/documents/discretionary/10k-first-month.pdf` | 16 pages | 1-16 | 1-16 | K10-01..K10-06; Video/private trailing rule absent; screenshot/prose RR and trade-direction discrepancies; partial payout dashboard only. |
| `/workspace/sources/documents/discretionary/18k-payout-session.pdf` | 15 pages | 1-15 | 1-15 | K18-01..K18-08; Full video/payout/account ledgers absent; open-position label misread as stop risk; combined PnL and profile-asymmetry claim unresolved. |
| `/workspace/sources/documents/discretionary/2345-funded-session.pdf` | 11 pages | 1-11 | 1-11 | F23-01..07; Direction/CVD contradiction p6; missing full recording/fills; planned RR and target fills not verified;2vs5 trades and1300vs2345 unresolved. |
| `/workspace/sources/documents/discretionary/a-clean-continuation-short.pdf` | 14 pages | 1-14 | 1-14 | CCS-01..08; Post-trade dealing-range profile; exact anchors,DOM/video/fills absent; risk/reward overlay not verified ticket. |
| `/workspace/sources/documents/discretionary/amt-lesson-1.pdf` | 14 pages | 1-14 | 1-14 | AM1-01..AM1-10 |
| `/workspace/sources/documents/discretionary/amt-on-live-markets.pdf` | 14 pages | 1-14 | 1-14 | ALM-01–06; p6 direction ambiguous; p11 rightmost recovery contradicts current lower-hold prose; chart anchors incomplete |
| `/workspace/sources/documents/discretionary/anatomy-of-a-losing-start.pdf` | 12 pages | 1-12 | 1-12 | ALS-01..06; Four-loss narrative contradicts chart;250cap vs480loss;thesis paraphrase wrong;figures/drawings lack raw execution verification. |
| `/workspace/sources/documents/discretionary/average-unprofitable-trader.pdf` | 33 pages | 1-33 | 1-33 | AUT-01–11; p18 right sentence masked and p26 bottom marks cut in original images; main mechanisms also in prose. Dashboard/closed account list not full fills/fee ledger. Missing original interview video; numerical claims unverified. |
| `/workspace/sources/documents/discretionary/code-1-thesis.pdf` | 8 pages | 1-8 | 1-8 | CD1-01–CD1-05; Linked video not embedded; CD1 p5 clipped originals recovered; IOD/RFZ reuse same chart without post-touch outcome. |
| `/workspace/sources/documents/discretionary/code-2-risk.pdf` | 8 pages | 1-8 | 1-8 | CD2-01–CD2-05; No empirical evidence supplied; source claims retained as hypotheses. |
| `/workspace/sources/documents/discretionary/code-3-orderflow.pdf` | 8 pages | 1-8 | 1-8 | CD3-01–CD3-05; No empirical evidence supplied; source claims retained as hypotheses. |
| `/workspace/sources/documents/discretionary/data-engine.pdf` | 9 pages | 1-9 | 1-9 | DEN-01–DEN-05; No empirical evidence supplied; source claims retained as hypotheses. |
| `/workspace/sources/documents/discretionary/dom-lesson-5.pdf` | 8 pages | 1-8 | 1-8 | DM5-01..04; Linked videos not embedded; hidden identity/depth not inferable from MBP1 |
| `/workspace/sources/documents/discretionary/dom-lesson-6.pdf` | 8 pages | 1-8 | 1-8 | DM6-01..05; Linked videos not embedded; hidden identity/depth not inferable from MBP1 |
| `/workspace/sources/documents/discretionary/dom-lesson-7.pdf` | 8 pages | 1-8 | 1-8 | DM7-01..05; Linked videos not embedded; hidden identity/depth not inferable from MBP1 |
| `/workspace/sources/documents/discretionary/emotion.pdf` | 9 pages | 1-9 | 1-9 | EMO-01–EMO-04; Linked video not embedded; mindset claims not evidence of edge. |
| `/workspace/sources/documents/discretionary/fp-lesson-8.pdf` | 8 pages | 1-8 | 1-8 | FP8-01..05; Linked videos not embedded; formula/diagram contradictions documented |
| `/workspace/sources/documents/discretionary/fp-lesson-9.pdf` | 8 pages | 1-8 | 1-8 | FP9-01..06; Linked videos not embedded; formula/diagram contradictions documented |
| `/workspace/sources/documents/discretionary/gex-framework.pdf` | 22 pages | 1-22 | 1-22 | GXF-01–GXF-13; Original rasters pp7/13/15 cropped; p16 source image degraded and quantitative axes/labels largely unreadable; formulas proprietary/unprovided. |
| `/workspace/sources/documents/discretionary/mastering-amt-vp.pdf` | 27 pages | 1-27 | 1-27 | MAV-01–14; MPOC/balance definitions, source table denominators and missing primary citations; p23 clipped visual labels recovered from text; histograms illustrative |
| `/workspace/sources/documents/discretionary/ny-am-session.pdf` | 12 pages | 1-12 | 1-12 | NYA-01..06; Open PnL called stopped/closed;RR increase is larger reward not changed risk in drawing;aggregate/per-account mismatch;private KG1/video absent. |
| `/workspace/sources/documents/discretionary/only-trade-big-trades.pdf` | 19 pages | 1-19 | 1-19 | OBT-01..OBT-10; Brackets explicitly review drawings; exact aggression/imbalance settings, composite lookback and gamma series absent; missing continuous video. |
| `/workspace/sources/documents/discretionary/origin-of-the-move.pdf` | 19 pages | 1-19 | 1-19 | OFM-01..OFM-09; Video/private trailing lesson absent; selected stills do not verify fills; pp8/9 direction-risk ambiguity and p14 unfilled-target caption corrected in ledger. |
| `/workspace/sources/documents/discretionary/reading-delta.pdf` | 11 pages | 1-11 | 1-11 | RDL-01–07; Highest delta-print definition/settings absent; cropped neighboring illustrations; pending targets not verified fills |
| `/workspace/sources/documents/discretionary/reading-the-volume-profile.pdf` | 13 pages | 1-13 | 1-13 | RVP-01–08; No numeric axes or causal snapshots;68/70/40% VA variants; schematic differs from summary |
| `/workspace/sources/documents/discretionary/refill-effect.pdf` | 24 pages | 1-24 | 1-24 | RFE-01–14; Zone/model/labels/code unavailable; split, execution loss, pass-rate and multi-account statistics disagree; all empirical claims unverified |
| `/workspace/sources/documents/discretionary/stop-re-entering.pdf` | 17 pages | 1-17 | 1-17 | SRE-01..SRE-07; Videos absent; clip-one figure actually matches wrong Nov7 example, while correct Nov13 is a different day. Static SIM frames do not verify fills or sequential tape claims. |
| `/workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf` | 16 pages | 1-16 | 1-16 | MAT-01–09; AAPL thresholds/sample counts unavailable; blank matrix cells not inferred; p13 caption not supported by price schematic |
| `/workspace/sources/documents/discretionary/tpo-lesson-3.pdf` | 10 pages | 1-10 | 1-10 | TP3-01..07; p5 final sentence clipped; p6 second chart recovered by embedded-image extraction |
| `/workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf` | 13 pages | 1-13 | 1-13 | TBR-01..TBR-07; Video/fills/level timestamps absent; execution MNQ quantity unknown; original marker and drawing prices differ; Delta settings absent. |
| `/workspace/sources/documents/discretionary/vix-lesson-4.pdf` | 10 pages | 1-10 | 1-10 | VX4-01..09; External calculator/video not embedded; source heuristics unvalidated |
| `/workspace/sources/documents/discretionary/vp-lesson-2.pdf` | 9 pages | 1-9 | 1-9 | VP2-01..VP2-05 |
| `/workspace/sources/documents/discretionary/vwap-lesson-10.pdf` | 9 pages | 1-9 | 1-9 | VW10-01..07; Linked videos not embedded; formula/diagram contradictions documented |
| `/workspace/sources/documents/discretionary/whos-in-control.pdf` | 12 pages | 1-12 | 1-12 | WIC-01–07; p4 defended/broken orientation ambiguous; delta/inventory claims not directly verified; images are not monotonic replay |
| `/workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf` | 14 pages | 1-14 | 1-14 | YMA-01–06; Three-tick definition/CVD median missing; price versus CVD units error; lower delta diagram repeats contradictory upper-side text |
| `/workspace/sources/documents/indicators/Open Source Fractal - Customized.txt` | 1521 lines | 1-1521 | N/A (see attachment limitations) | OSF-01–10; Static inspection only; Pine not compiled/executed. Confirmed pivots/backdated drawings, HTF parity, ambiguous intrabar behavior and paired tick normalization require fixtures. |
| `/workspace/sources/documents/indicators/Pinescript-indicators--main.zip` | archive/image | All 83 members; see itemized coverage below | N/A (see attachment limitations) | PIN001–PIN083 (all member finding sub-IDs below); 83 regular text/source members read in full; no binary assets or bundled execution. PIN080/PIN081 supplied files end in incomplete code. |
| `/workspace/sources/documents/indicators/momentum-volume-flow-levels.txt` | 488 lines | 1-488 | N/A (see attachment limitations) | MVF-01–07; Static inspection only; Pine not compiled/executed. OHLC-sign volume proxy; display-dependent signal; backdated mutable clusters. |
| `/workspace/sources/documents/inventory/DATA_INVENTORY.md` | 765 lines | 1-765 | N/A (see attachment limitations) | INV-01..INV-12 |
| `/workspace/sources/documents/inventory/databento_pull_list.md` | 91 lines | 1-91 | N/A (see attachment limitations) | INV-10; CEX-10/CEX-22..26 |
| `/workspace/sources/documents/jumbo/JJumbo_Conversation_Export.md` | 484 lines | 1-484 | N/A (see attachment limitations) | JCV-U01..U06; JCV-A01..A10; Earlier assistant replies condensed in supplied export; no embedded image pixels. |
| `/workspace/sources/documents/jumbo/SessionStat+.pdf` | 12 pages | 1-12 | 1-12 | JSS-01–JSS-07; Weighted/minimum-average/P-zone formulas not fully disclosed; chart screenshots do not establish causal availability or edge. |
| `/workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf` | 38 pages | 1-38 | 1-38 | JTR-01–JTR-24; EST/ET wording, rejection-block stop caption/drawing, statistical denominators and unpublished formulas remain explicit; visuals fully inspected. |
| `/workspace/sources/documents/jumbo/jjumbo-findings.pdf` | 14 pages | 1-14 | 1-14 | JFN-01..JFN-12; Prior assistant synthesis; corrections recorded against originals. |
| `/workspace/sources/documents/jumbo/xfcmg2.pdf` | 48 pages | 1-48 | 1-48 | JXA-01..JXA-26; Missing referenced videos and five images; p29 table digits partly ambiguous; formulas and performance unverified. |
| `/workspace/sources/documents/reference-images/zerano-charts-SPX-2026-08-24T18-51-29-251Z.webp` | archive/image | 1-1 | 1-1 | IMG-01..IMG-07; Entire image and three enlarged regions reviewed; formulas/grey-line legend/drawing times unavailable; watermark partly obscures bottom table rows. |
| `/workspace/sources/documents/conversations/Design robust feature levels.md` | 1854 lines | 1-1854 | N/A (see attachment limitations) | DRF-U01–DRF-U12; DRF-A01–DRF-A29; Mermaid source fully reviewed; screenshot pixels not embedded. User excludes old archive; historical archive claims not verified or adopted. |

## Reconciled review totals

PDF text pages actually reviewed: 580/580. PDF pages actually viewed: 580/580. All supplied pages are accounted for; original-image extraction/enlargement supplemented tiny chart/diagram review.

Historical conversations: 5 files, 6,256 supplied lines, all read end-to-end. This includes both user messages in Develop Trading Model and the added Design robust feature levels conversation. Mermaid source and attachment descriptions were read; absent original pixels/tool results remain absent.

The standalone reference WEBP was actually viewed in full and in three enlarged panels. Two standalone indicator sources total 2,009 lines, all read. README/manifest and inventory/pull-list files were fully read. The original retrieved Jumbo tweet archive contains 66 posts across 48 pages; this is full coverage of the supplied artifact, not the author’s entire work.

ZIP member review is itemized below and in review/zip_inventory.json. Source passage/diagram findings are recorded with stable IDs in SOURCE_FINDINGS_AND_CONFLICTS.md. Missing referenced assets and partially unreadable source digits remain explicit even when supplied page review is complete.

## Extracted ZIP member coverage

| Exact isolated member path | Lines | Text reviewed | Findings | Visual content |
|---|---|---|---|---|
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/4H HOD LOD Checkpoint Analysis.txt` | 956 | 1-956 | PIN001 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/4h Candle Curves.txt` | 604 | 1-604 | PIN002 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/6 to 9 Session and Levels.txt` | 680 | 1-680 | PIN003 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/6 to 9 session & levels v2.txt` | 680 | 1-680 | PIN004 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/8020 System.txt` | 489 | 1-489 | PIN005 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/ADR Levels with Stats.txt` | 556 | 1-556 | PIN006 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/AM TBR - NQ Stats.txt` | 700 | 1-700 | PIN007 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/ATR Breakout.txt` | 43 | 1-43 | PIN008 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Adaptive Volatility Adjusted Momentum Score.txt` | 140 | 1-140 | PIN009 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/CISD with fib or range extensions and stats.txt` | 430 | 1-430 | PIN010 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Confluence Suite.txt` | 936 | 1-936 | PIN011 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/DTT Time Based Ranges.txt` | 1363 | 1-1363 | PIN012 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Daily Floor Pivots.txt` | 1200 | 1-1200 | PIN013 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Daily High Low probability zones.txt` | 309 | 1-309 | PIN014 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Daily close stats.txt` | 459 | 1-459 | PIN015 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Daily statistical range and levels.txt` | 1007 | 1-1007 | PIN016 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Deviation based reversion with Stats.txt` | 366 | 1-366 | PIN017 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Expected Volatility .txt` | 223 | 1-223 | PIN018 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/First presented FVG (with stats) with statistical hourly ranges & bias.txt` | 629 | 1-629 | PIN019 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/HMM Enhanced Regime Probability.txt` | 382 | 1-382 | PIN020 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/HTF Candle Stats by Time of Day.txt` | 316 | 1-316 | PIN021 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/HTF Sweep Model with CISD Table.txt` | 859 | 1-859 | PIN022 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/HTF Sweeps & Liquidity Levels with CISD.txt` | 1260 | 1-1260 | PIN023 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Historical High and Lows Statistical Analysis 30min bins.txt` | 140 | 1-140 | PIN024 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Hourly Time Levels.txt` | 155 | 1-155 | PIN025 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/IB ORB Live Stats.txt` | 464 | 1-464 | PIN026 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/IB ORB Statistical Mapper hardcoded.txt` | 409 | 1-409 | PIN027 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Initial Balance & Extensions with Stats by DOW.txt` | 837 | 1-837 | PIN028 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Initial Balance & levels with stats.txt` | 738 | 1-738 | PIN029 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Initial Balance Statistical Mapping.txt` | 679 | 1-679 | PIN030 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Inside and Outside bar stats.txt` | 109 | 1-109 | PIN031 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Key levels, MTF swing highs, lows & 4h candle boxes.txt` | 830 | 1-830 | PIN032 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Leptokurtic Directional Bias.txt` | 296 | 1-296 | PIN033 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/MTF Bollinger Bands Trend Stop.txt` | 86 | 1-86 | PIN034 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/MTF HTF market analysis toolkit.txt` | 1012 | 1-1012 | PIN035 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/MTF OHLC Lines with Breakout & Retracement Labels.txt` | 358 | 1-358 | PIN036 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/MTF OHLC retracement stats.txt` | 347 | 1-347 | PIN037 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/MTF Swing Highs and Lows.txt` | 418 | 1-418 | PIN038 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/NQ Hourly Retracement Levels.txt` | 947 | 1-947 | PIN039 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/NQ Hourly Retracements 12y Stats with Levels.txt` | 619 | 1-619 | PIN040 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/NQ Statistical Mapper.txt` | 950 | 1-950 | PIN041 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/NQ Stats ALN profiler.txt` | 255 | 1-255 | PIN042 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/NQ Stats Initial Balance.txt` | 131 | 1-131 | PIN043 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/NQ Stats Noon Curve.txt` | 414 | 1-414 | PIN044 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/NQ Stats Price Distributions.txt` | 1234 | 1-1234 | PIN045 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/NQ Stats RTH Breaks with stats.txt` | 157 | 1-157 | PIN046 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/NQ Stats all in one.txt` | 784 | 1-784 | PIN047 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/NY 5m and & 15m Orb Statistics & LTF Candle structure.txt` | 1189 | 1-1189 | PIN048 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/NY vs Asia Statistical Levels.txt` | 791 | 1-791 | PIN049 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Oscillator Suite.txt` | 550 | 1-550 | PIN050 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Pivot Order Blocks.txt` | 125 | 1-125 | PIN051 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Pre-market session levels and stats.txt` | 1548 | 1-1548 | PIN052 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/README.md` | 1 | 1-1 | PIN053 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Range Prob.txt` | 616 | 1-616 | PIN054 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Range Projections Statistical Levels.txt` | 352 | 1-352 | PIN055 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Reversal Breakout System Outside Inside Bar with Stats.txt` | 289 | 1-289 | PIN056 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Session Based Statmap with closing stats.txt` | 554 | 1-554 | PIN057 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Session First Bar Range.txt` | 237 | 1-237 | PIN058 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Session Opening Bar Range.txt` | 513 | 1-513 | PIN059 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Session Raid Stats.txt` | 701 | 1-701 | PIN060 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Session Range Candles + 25% Level.txt` | 1196 | 1-1196 | PIN061 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Session Range Projections with stats.txt` | 1243 | 1-1243 | PIN062 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Session Statistical Levels.txt` | 1623 | 1-1623 | PIN063 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Session highs lows and opens.txt` | 846 | 1-846 | PIN064 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Session standard deviations with stats.txt` | 786 | 1-786 | PIN065 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Sessions & VP with prev session VP & daily weekly opens.txt` | 686 | 1-686 | PIN066 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Statistcal Daily Profile & Ranges.txt` | 483 | 1-483 | PIN067 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Statistical OHLC Projections HTF.txt` | 974 | 1-974 | PIN068 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Statistical VWAP study Session and RTH VWAP.txt` | 666 | 1-666 | PIN069 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Statmap HTF no like for like lookback.txt` | 1004 | 1-1004 | PIN070 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Sweep, CISD, MTF FVG & Key Levels.txt` | 1603 | 1-1603 | PIN071 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/TTM Squeeze Divergence.txt` | 127 | 1-127 | PIN072 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Time based Range Retracement with Stats.txt` | 521 | 1-521 | PIN073 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Time based level retracement - stats.txt` | 297 | 1-297 | PIN074 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Time based ranges with stats.txt` | 552 | 1-552 | PIN075 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Time based retracement by DOW - stats.txt` | 319 | 1-319 | PIN076 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/VP History Widget.txt` | 309 | 1-309 | PIN077 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/Weekly Initial Balance.txt` | 366 | 1-366 | PIN078 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/confluence_suite` | 578 | 1-578 | PIN079 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/hourly_stats_levels` | 579 | 1-579 | PIN080 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/magic_hours` | 950 | 1-950 | PIN081 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/nq_stats_mapper` | 950 | 1-950 | PIN082 | No embedded images; drawing logic reviewed as source when text complete |
| `/workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/session_statmap` | 579 | 1-579 | PIN083 | No embedded images; drawing logic reviewed as source when text complete |

ZIP members fully read: 83/83; lines actually read: 51659/51659. Static inspection, no Pine code execution.

## External Skylit documentation accounting

Research date 2026-09-06 UTC. All 96 indexed pages were fetched successfully and accounted for: 41 full narrative/text reads and 55 focused generated-API semantic reviews. Focused review covered endpoint descriptions, defaults, field meanings, constraints, aggregation, timing and availability; it does not claim every repeated generated schema/example/boilerplate line was read verbatim. All 87/87 retrieved substantive images were actually viewed, with originals enlarged where needed. Findings and exact URLs are in EXTERNAL_RESEARCH.md; raw captures/hashes and readable versions are retained under review/external/skylit.

| Page ID and exact URL | Supplied capture lines | Review method | Image coverage |
|---|---|---|---|
| [SKY001](https://docs.skylit.ai/platform/overview) | 41 | Full readable text | 0 images, 0 viewed |
| [SKY002](https://docs.skylit.ai/platform/support) | 30 | Full readable text | 0 images, 0 viewed |
| [SKY003](https://docs.skylit.ai/platform/changelog) | 47 | Full readable text | 0 images, 0 viewed |
| [SKY004](https://docs.skylit.ai/introduction) | 116 | Full readable text | 4 images, 4 viewed |
| [SKY005](https://docs.skylit.ai/intended-audience) | 25 | Full readable text | 0 images, 0 viewed |
| [SKY006](https://docs.skylit.ai/core-concepts) | 262 | Full readable text | 16 images, 16 viewed |
| [SKY007](https://docs.skylit.ai/navigating-skylit-web-app) | 66 | Full readable text | 0 images, 0 viewed |
| [SKY008](https://docs.skylit.ai/how-to-read-and-use-heatseeker) | 90 | Full readable text | 0 images, 0 viewed |
| [SKY009](https://docs.skylit.ai/best-practices) | 101 | Full readable text | 1 images, 1 viewed |
| [SKY010](https://docs.skylit.ai/limitations) | 67 | Full readable text | 0 images, 0 viewed |
| [SKY011](https://docs.skylit.ai/common-pitfalls-and-mistakes) | 97 | Full readable text | 0 images, 0 viewed |
| [SKY012](https://docs.skylit.ai/faqs) | 95 | Full readable text | 0 images, 0 viewed |
| [SKY013](https://docs.skylit.ai/examples-and-case-studies) | 57 | Full readable text | 7 images, 7 viewed |
| [SKY014](https://docs.skylit.ai/resources) | 19 | Full readable text | 0 images, 0 viewed |
| [SKY015](https://docs.skylit.ai/patternpedia/pattern-the-whipsaw) | 35 | Full readable text | 3 images, 3 viewed |
| [SKY016](https://docs.skylit.ai/patternpedia/pattern-rainbow-road) | 35 | Full readable text | 3 images, 3 viewed |
| [SKY017](https://docs.skylit.ai/patternpedia/pattern-the-gatekeeper) | 39 | Full readable text | 3 images, 3 viewed |
| [SKY018](https://docs.skylit.ai/patternpedia/case-study-speculative-and-decoy-nodes) | 35 | Full readable text | 3 images, 3 viewed |
| [SKY019](https://docs.skylit.ai/patternpedia/pattern-trend) | 37 | Full readable text | 3 images, 3 viewed |
| [SKY020](https://docs.skylit.ai/patternpedia/pattern-rug-setup) | 34 | Full readable text | 2 images, 2 viewed |
| [SKY021](https://docs.skylit.ai/patternpedia/the-ten-commandments-of-using-heatseeker) | 20 | Full readable text | 0 images, 0 viewed |
| [SKY022](https://docs.skylit.ai/patternpedia/topping-patterns-bottoming-patterns) | 47 | Full readable text | 3 images, 3 viewed |
| [SKY023](https://docs.skylit.ai/help-page/general-information) | 14 | Full readable text | 0 images, 0 viewed |
| [SKY024](https://docs.skylit.ai/help-page/written-guides) | 21 | Full readable text | 0 images, 0 viewed |
| [SKY025](https://docs.skylit.ai/help-page/video-links) | 31 | Full readable text | 0 images, 0 viewed |
| [SKY026](https://docs.skylit.ai/help-page/useful-threads) | 47 | Full readable text | 0 images, 0 viewed |
| [SKY027](https://docs.skylit.ai/api-reference/introduction) | 126 | Full readable text | 0 images, 0 viewed |
| [SKY028](https://docs.skylit.ai/api-reference/authentication) | 93 | Full readable text | 0 images, 0 viewed |
| [SKY029](https://docs.skylit.ai/api-reference/heatmap/live-per-strike-heatmap-one-or-more-symbols) | 407 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY030](https://docs.skylit.ai/api-reference/heatmap/replay-per-strike-heatmap-at-a-past-instant-one-or-more-symbols) | 411 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY031](https://docs.skylit.ai/api-reference/heatmap/live-sse-stream-one-symbol-per-connection) | 306 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY032](https://docs.skylit.ai/flowseeker/overview) | 396 | Full readable text | 21 images, 21 viewed |
| [SKY033](https://docs.skylit.ai/api-reference/flow/raw-flow-feed-for-a-ticker-flow-score-+-flowbonus-per-trade) | 841 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY034](https://docs.skylit.ai/api-reference/flow/aggregate-flow-over-an-arbitrary-[start-end]-window) | 553 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY035](https://docs.skylit.ai/api-reference/flow/per-ticker-net-premium-time-series-"flow-tide") | 517 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY036](https://docs.skylit.ai/api-reference/flow/trailing-per-time-of-day-flow-baseline-avg-+-stddev) | 475 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY037](https://docs.skylit.ai/api-reference/flow/live-momentum-signal-vs-baseline-5m-30m-1h-windows) | 494 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY038](https://docs.skylit.ai/api-reference/flow/strike-level-flow-concentration) | 519 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY039](https://docs.skylit.ai/api-reference/flow/todays-flow-vs-trailing-average-with-similar-days-lookback) | 521 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY040](https://docs.skylit.ai/api-reference/sector/sector-or-industry-level-flow-aggregation) | 502 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY041](https://docs.skylit.ai/api-reference/market/market-wide-breadth-advancedecline-and-sector-rotation) | 506 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY042](https://docs.skylit.ai/api-reference/market/market-wide-flow-overview-for-the-current-trading-day) | 449 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY043](https://docs.skylit.ai/api-reference/market/bucketed-market-wide-net-call-premium-net-put-premium-time-series) | 495 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY044](https://docs.skylit.ai/api-reference/sweeps/aggregated-multi-exchange-sweep-activity) | 602 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY045](https://docs.skylit.ai/api-reference/analytics/aggregate-sentiment-scoring-across-timeframes-vwf-sdf-fir-composite) | 613 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY046](https://docs.skylit.ai/api-reference/analytics/volume-vs-open-interest-accumulation-analysis) | 539 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY047](https://docs.skylit.ai/api-reference/analytics/moneyness-breakdown-with-pattern-detection) | 558 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY048](https://docs.skylit.ai/api-reference/scoring/detailed-scoring-for-a-single-trade) | 543 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY049](https://docs.skylit.ai/api-reference/ratios/chain-level-bidaskmid-distribution) | 518 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY050](https://docs.skylit.ai/api-reference/ratios/per-contract-bidaskmid-distribution) | 494 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY051](https://docs.skylit.ai/api-reference/ratios/chain-level-callput-aware-bullbear-pressure) | 517 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY052](https://docs.skylit.ai/api-reference/ratios/per-contract-callput-aware-bullbear-pressure) | 496 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY053](https://docs.skylit.ai/api-reference/underlying/list-underlyings-active-on-a-date) | 386 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY054](https://docs.skylit.ai/api-reference/underlying/prefix-search-active-tickers) | 355 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY055](https://docs.skylit.ai/api-reference/underlying/top-underlyings-by-daily-flow) | 402 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY056](https://docs.skylit.ai/api-reference/underlying/top-underlyings-by-trailing-5-day-flow) | 400 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY057](https://docs.skylit.ai/api-reference/underlying/bulk-underlying-stats-for-a-list-of-tickers) | 388 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY058](https://docs.skylit.ai/api-reference/underlying/daily-stats-for-a-single-underlying) | 395 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY059](https://docs.skylit.ai/api-reference/underlying/intraday-chart-bars-for-a-ticker) | 415 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY060](https://docs.skylit.ai/api-reference/underlying/raw-enriched-trades-for-a-ticker) | 635 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY061](https://docs.skylit.ai/api-reference/underlying/premium-volume-by-strike) | 449 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY062](https://docs.skylit.ai/api-reference/underlying/premium-volume-by-expiration-for-a-strike) | 421 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY063](https://docs.skylit.ai/api-reference/underlying/list-traded-expirations-for-a-ticker) | 345 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY064](https://docs.skylit.ai/api-reference/underlying/option-chain-snapshot) | 429 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY065](https://docs.skylit.ai/api-reference/underlying/daily-history-for-a-ticker) | 368 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY066](https://docs.skylit.ai/api-reference/underlying/relative-volume-bars-for-a-ticker) | 495 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY067](https://docs.skylit.ai/api-reference/contract/top-contracts-by-daily-flow) | 535 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY068](https://docs.skylit.ai/api-reference/contract/top-contracts-by-trailing-5-day-flow) | 532 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY069](https://docs.skylit.ai/api-reference/contract/contracts-with-unusual-relative-volume) | 595 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY070](https://docs.skylit.ai/api-reference/contract/contracts-with-significant-oi-changes) | 500 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY071](https://docs.skylit.ai/api-reference/contract/bulk-contract-stats-for-a-list-of-symbols) | 422 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY072](https://docs.skylit.ai/api-reference/contract/daily-stats-for-a-single-contract) | 436 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY073](https://docs.skylit.ai/api-reference/contract/intraday-chart-bars-for-a-contract) | 455 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY074](https://docs.skylit.ai/api-reference/contract/raw-enriched-trades-for-a-contract) | 597 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY075](https://docs.skylit.ai/api-reference/contract/daily-history-for-a-contract) | 421 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY076](https://docs.skylit.ai/api-reference/contract/relative-volume-bars-for-a-contract) | 470 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY077](https://docs.skylit.ai/api-reference/dark-pool/paginated-off-exchange-trf-prints) | 567 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY078](https://docs.skylit.ai/api-reference/dark-pool/largest-individual-dark-pool-prints-for-a-ticker) | 429 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY079](https://docs.skylit.ai/api-reference/meta/this-openapi-specification-as-json) | 180 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY080](https://docs.skylit.ai/mcp/overview) | 83 | Full readable text | 0 images, 0 viewed |
| [SKY081](https://docs.skylit.ai/mcp/quickstart) | 150 | Full readable text | 0 images, 0 viewed |
| [SKY082](https://docs.skylit.ai/mcp/tools) | 138 | Full readable text | 0 images, 0 viewed |
| [SKY083](https://docs.skylit.ai/mcp/examples) | 86 | Full readable text | 0 images, 0 viewed |
| [SKY084](https://docs.skylit.ai/nexus/overview) | 15 | Full readable text | 0 images, 0 viewed |
| [SKY085](https://docs.skylit.ai/atlas/overview) | 344 | Full readable text | 14 images, 14 viewed |
| [SKY086](https://docs.skylit.ai/atlas/drawing-presets) | 94 | Full readable text | 4 images, 4 viewed |
| [SKY087](https://docs.skylit.ai/atlas/indicators/gex-vwap) | 43 | Full readable text | 0 images, 0 viewed |
| [SKY088](https://docs.skylit.ai/atlas/indicators/vwap) | 32 | Full readable text | 0 images, 0 viewed |
| [SKY089](https://docs.skylit.ai/atlas/indicators/cvd) | 41 | Full readable text | 0 images, 0 viewed |
| [SKY090](https://docs.skylit.ai/atlas/indicators/volume-profile) | 35 | Full readable text | 0 images, 0 viewed |
| [SKY091](https://docs.skylit.ai/atlas/indicators/tpo) | 48 | Full readable text | 0 images, 0 viewed |
| [SKY092](https://docs.skylit.ai/api-reference/history/ohlcv-price-bars-for-a-symbol-and-resolution) | 619 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY093](https://docs.skylit.ai/api-reference/symbols/search-symbols) | 333 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY094](https://docs.skylit.ai/api-reference/symbols/resolve-a-symbol) | 415 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY095](https://docs.skylit.ai/api-reference/meta/datafeed-configuration) | 359 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |
| [SKY096](https://docs.skylit.ai/api-reference/meta/server-time) | 215 | Focused API semantics; generated boilerplate not fully read | 0 images, 0 viewed |

Official account/provider/method sources were read to the specific relevant passages described in ACCOUNT_CONSTRAINTS.md and EXTERNAL_RESEARCH.md (TECH-01–18). Their scope is focused factual/method research, not a claim of full-text review of every referenced book/paper/site. Unavailable original Garman–Klass full text and proprietary formulas are disclosed. No external account actions or messages were sent.

## Completion boundary

No supplied page, passage or source member remains unread. Cropped/degraded originals, omitted attachments/videos, unprovided formulas and truncated Pine file tails cannot be reconstructed; exact limitations remain in the file rows and OPEN_QUESTIONS_AND_RISKS.md. Exhaustive document review is distinct from proportionate market-data auditing: see DATA_CAPABILITY_AUDIT.md for the actual sampled rows/files and unrun validation work.

Third-review addendum: the [conversation recheck](CONVERSATION_RECHECK.md) reexamined all 122 existing conversation findings against explicit experiment units; it does not replace the original full-text reading record. Five additional bounded primary-source checks are recorded separately in [THIRD_REVIEW_RESEARCH.md](THIRD_REVIEW_RESEARCH.md). The [bounded VIX audit](review/third-review/VIX_FEASIBILITY.md) and [third design review](THIRD_DESIGN_REVIEW.md) describe new work. Supplied source files were not edited or reclassified as performance evidence.
