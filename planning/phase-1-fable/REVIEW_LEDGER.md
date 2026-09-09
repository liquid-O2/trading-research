# Review ledger — sources/documents/ (2026-09-09)

Every file under `sources/documents/` and the three reference files, with how it was reviewed and where it lands. "Read" = every line / every page visually inspected. Tiers follow `wiki/index.md`. Dispositions: **measure** (Phase 1 object), **experiment** (comparison row), **defer** (Phase 2–3), **reference** (construction / vocabulary only), **out** (out of scope).

## jumbo/
| file | reviewed | tier | feeds | disposition |
|---|---|---|---|---|
| `Time-Based ranges Framework (JJumbo).pdf` | 38 pp read, p.12 and p.30 zoomed | 2 | tbr-6-9-range, range-path-class, extensions, clock grid, grid (3-strike, rejection blocks) | measure |
| `SessionStat+.pdf` | 12 pp read | 2 | sessionstat-9-12-envelope | measure |
| `xfcmg2.pdf` | 48 pp (66 posts) read, p.8, p.11, p.23, p.24 zoomed | 2 (2026 use outranks older marketing) | open-location-switch (p.11 table), range-path-class (p.24 table, p.23), ev-range (p.7), absorption/BigTrades (p.23, p.25, p.44–46), clocks (p.7, p.8, p.14–15, p.25, p.47), P-zones (p.8, p.16) | measure |
| `jjumbo-findings.pdf` | 14 pp read | 2, secondary to TBR / SS / XF / JJX / PACK | day-type cartoon (p.4), classify step (p.3), London TBR (p.4–5), range size / balance (p.6), P-zone figure (p.6) | experiment / reference |
| `JJumbo_Conversation_Export.md` | 484 lines read; user turns §1 L50–58, §7 L146–153 | 1 (user) / 4 (assistant) | data lock (MBP-1 only), derived ranges as a clock search, classification of range, 9–12 layer, delta profile beside RTH VP | measure |

## discretionary/ (35 PDFs; short codes used in the wiki)
| code | file | pp | feeds | disposition |
|---|---|---|---|---|
| ABS | your-mistakes-with-absorption.pdf | 14 | absorption definition (p.8–9), signature at POC vs extreme (p.2, p.6–7), replenishment window (p.3–4) | measure |
| RD | reading-delta.pdf | 11 | delta as reward check (p.6–7), refill schematic (p.8–9), LVN extreme (p.9) | measure |
| REF | refill-effect.pdf | 24 | zone from clustered large aggressive prints (p.5), refill = reload (p.3, p.10), AUC 0.54 raw aggression (p.9), feature table (p.8) | measure (touch-level proxy) / not-measurable (off-touch book) |
| RTVP | reading-the-volume-profile.pdf | 13 | VAH / POC / VAL 68% (p.4), POC magnet (p.5), balanced vs trending profile (p.7, p.9) | measure |
| BIG | only-trade-big-trades.pdf | 19 | BigTrades = aggression marker, 30–60 contracts (p.3), effort vs reward (p.4), body vs wick prints (p.6) | measure |
| WIC | whos-in-control.pdf | 12 | arrival aggression vs drift (p.4), retest confirmation (p.5, p.7–8) | reference (labels) |
| MAMT | mastering-amt-vp.pdf | 27 | 80% balance rule (p.4), POC / VAH / VAL (p.5), P / b day types (p.7), opening inside yesterday's balance (p.2 L24) | measure |
| MATH | the-math-behind-auction-market-theory.pdf | 16 | absorption properly defined (p.8), imbalance not an oracle (p.6), value is a process (p.9) | measure |
| TRAP | trapped-buyers-one-retest.pdf | 13 | heavy delta print at extreme = trapped side (p.4), balance redraw (p.3) | measure (delta profile) |
| STOP | stop-re-entering.pdf | 17 | definitions of absorption, delta, delta print, CVD (p.3), failed vs confirmed absorption (p.2 L13, p.10), trapped buyers off delta (p.9) | measure |
| OFM | origin-of-the-move.pdf | 19 | squeeze / refill clock, retest entries (p.5–9) | reference (execution model) |
| C1 | code-1-thesis.pdf | 8 | trading thesis discipline | out (psychology) |
| C2 | code-2-risk.pdf | 8 | risk rules | out (risk is locked by the brief, not a Phase 1 object) |
| C3 | code-3-orderflow.pdf | 8 | balance / single prints / 40% VA (p.6–7) | measure (VA 40% variant) |
| GEX | gex-framework.pdf | 22 | dealer hedging, gamma flip, strikes (p.2–5) | measure (options-nodes) |
| VIX4 | vix-lesson-4.pdf | 10 | VIX → expected ES points (p.4), intraday VIX / ES divergence (p.6) | experiment (vol features) |
| VWAP | vwap-lesson-10.pdf | 9 | VWAP deviation bands, CVD definition (p.3–6) | experiment (VWAP band row under ev-range) |
| NYAM | ny-am-session.pdf | 12 | refill trade walk-through, third-retest failure (p.4–6) | reference |
| DE | data-engine.pdf | 9 | keep your own stats, standard deviations of readings (p.5) | reference (method) |
| AMT1 | amt-lesson-1.pdf | 14 | balance / imbalance, 70% VA, POC / VAH / VAL (p.4–5) | measure |
| — | amt-on-live-markets.pdf | 14 | AMT applied live | reference |
| — | vp-lesson-2.pdf | 9 | volume profile lesson | measure (value-and-profiles, via AMT1 / RTVP definitions) |
| — | tpo-lesson-3.pdf | 10 | TPO profile | experiment (`value.tpo` variant, time-based profile) |
| — | dom-lesson-5.pdf, dom-lesson-6.pdf, dom-lesson-7.pdf | 8 / 8 / 8 | DOM depth reading | not-measurable (needs depth beyond BBO; MBP-1 only) |
| — | fp-lesson-8.pdf, fp-lesson-9.pdf | 8 / 8 | footprint reading | measure (footprint = per-price aggressor volume from trades; feeds absorption / BigTrades) |
| — | 10k-first-month.pdf, 18k-payout-session.pdf, 2345-funded-session.pdf, a-clean-continuation-short.pdf, anatomy-of-a-losing-start.pdf, average-unprofitable-trader.pdf, emotion.pdf | 16 / 15 / 11 / 14 / 12 / 33 / 9 | session recaps, trader psychology, P&L narratives | out (no computable object; no P&L in Phase 1) |

## conversations/
| file | reviewed | tier | feeds | disposition |
|---|---|---|---|---|
| `Develop Trading Model.md` | 1,540 lines; user turn L13–31 | 1 / 4 | user asks: double / single breaks and day types, improve and adapt time ranges, several CVD methods incl. gamma CVD, GK / YZ / HAR forward vol, multi-asset SMT, level families, mixture of experts (Phase 2–3); assistant's day-type table L44–49 restates TBR p.12 / p.24 | measure (labels) / defer (models) |
| `Design robust feature levels.md` | 1,854 lines; user turns L10, L168, L279 | 1 / 4 | options data limits, no participant identity, OI as prior, gamma nodes as levels | measure (options-nodes), not-measurable (dealer IDs) |
| `conversation_export (1).md` | 1,306 lines | 4 (assistant) with user quotes | MBP-1 replenishment proxy (L35), regime proposal (L70), SMT question (L105) | experiment |
| `conversation_raw_log.md` | 1,072 lines | 4 | MBP-1 event tokens (L270, L378, L444, L637) | experiment (absorption B) |

## indicators/
| file | reviewed | tier | feeds | disposition |
|---|---|---|---|---|
| `Pinescript-indicators--main.zip` | 84 files / 51,601 lines, every line; md5 duplicate check | 2 | see `wiki/sources-pine-archive.md` | experiment (hardcoded tables) / reference |
| `Open Source Fractal - Customized.txt` | 1,521 lines | 2 | fractal swing definition | reference (SMT level set S3 uses the 5-bar fractal) |
| `momentum-volume-flow-levels.txt` | 488 lines | 2 | momentum / volume-flow levels | out (generic) |

Pine files by role (J = Jumbo geometry, S = hardcoded stats to recompute, L = live-stat framework / construction reference, R = level drawing only, X = generic TA out of scope, D = duplicate):
J: `6 to 9 Session and Levels.txt`, `Pre-market session levels and stats.txt`, `session_statmap`.
S: `4H HOD LOD Checkpoint Analysis.txt`, `4h Candle Curves.txt`, `AM TBR - NQ Stats.txt`, `Daily Floor Pivots.txt`, `First presented FVG (with stats) with statistical hourly ranges & bias.txt`, `IB ORB Statistical Mapper hardcoded.txt`, `Initial Balance Statistical Mapping.txt`, `NQ Hourly Retracement Levels.txt`, `hourly_stats_levels`, `NQ Hourly Retracements 12y Stats with Levels.txt`, `NQ Statistical Mapper.txt`, `nq_stats_mapper`, `NQ Stats ALN profiler.txt`, `NQ Stats Initial Balance.txt`, `NQ Stats Noon Curve.txt`, `NQ Stats Price Distributions.txt`, `NQ Stats RTH Breaks with stats.txt`, `NY 5m and & 15m Orb Statistics & LTF Candle structure.txt`, `Range Prob.txt`, `Range Projections Statistical Levels.txt`, `Statistcal Daily Profile & Ranges.txt`, `magic_hours`.
L: `ADR Levels with Stats.txt`, `CISD with fib or range extensions and stats.txt`, `Confluence Suite.txt`, `DTT Time Based Ranges.txt`, `Daily High Low probability zones.txt`, `Daily close stats.txt`, `Daily statistical range and levels.txt`, `Deviation based reversion with Stats.txt`, `Expected Volatility .txt`, `HTF Candle Stats by Time of Day.txt`, `HTF Sweep Model with CISD Table.txt`, `HTF Sweeps & Liquidity Levels with CISD.txt`, `Historical High and Lows Statistical Analysis 30min bins.txt`, `IB ORB Live Stats.txt`, `Initial Balance & Extensions with Stats by DOW.txt`, `Initial Balance & levels with stats.txt`, `MTF HTF market analysis toolkit.txt`, `MTF OHLC retracement stats.txt`, `NQ Stats all in one.txt`, `NY vs Asia Statistical Levels.txt`, `Session Based Statmap with closing stats.txt`, `Session First Bar Range.txt`, `Session Opening Bar Range.txt`, `Session Raid Stats.txt`, `Session Range Candles + 25% Level.txt`, `Session Range Projections with stats.txt`, `Session Statistical Levels.txt`, `Session standard deviations with stats.txt`, `Sessions & VP with prev session VP & daily weekly opens.txt`, `Statistical OHLC Projections HTF.txt`, `Statistical VWAP study Session and RTH VWAP.txt`, `Statmap HTF no like for like lookback.txt`, `Sweep, CISD, MTF FVG & Key Levels.txt`, `Time based Range Retracement with Stats.txt`, `Time based level retracement - stats.txt`, `Time based ranges with stats.txt`, `Time based retracement by DOW - stats.txt`, `VP History Widget.txt`, `Weekly Initial Balance.txt`.
R: `Hourly Time Levels.txt`, `Key levels, MTF swing highs, lows & 4h candle boxes.txt`, `MTF OHLC Lines with Breakout & Retracement Labels.txt`, `MTF Swing Highs and Lows.txt`, `Session highs lows and opens.txt`.
X: `8020 System.txt`, `ATR Breakout.txt`, `Adaptive Volatility Adjusted Momentum Score.txt`, `HMM Enhanced Regime Probability.txt`, `Inside and Outside bar stats.txt`, `Leptokurtic Directional Bias.txt`, `MTF Bollinger Bands Trend Stop.txt`, `Oscillator Suite.txt`, `Pivot Order Blocks.txt`, `Reversal Breakout System Outside Inside Bar with Stats.txt`, `TTM Squeeze Divergence.txt`, `confluence_suite`, `README.md` (title only).
D: `6 to 9 session & levels v2.txt` (byte-identical to `6 to 9 Session and Levels.txt`).

## inventory/
| file | reviewed | feeds | disposition |
|---|---|---|---|
| `DATA_INVENTORY.md` | 765 lines | wiki/data-coverage (all dataset IDs, coverage, storage) | measure |
| `databento_pull_list.md` | 91 lines | none; a request list, not an acquisition record `[README L13]` | reference |

## reference-images/
| file | reviewed | disposition |
|---|---|---|
| `zerano-charts-SPX-2026-08-24T18-51-29-251Z.webp` | converted, viewed; SPX chart with drawn levels | reference (no numbers usable) |

## Root files and references
| file | reviewed | disposition |
|---|---|---|
| `README.md` | read | index of groups; Skylit links not downloaded (Phase 2–3) |
| `SOURCE_MANIFEST.json` | read | sizes and SHA-256 per source; not re-hashed here |
| `references/agent-method-matt-wiki.md` | 157 lines | method (tier 3) |
| `references/jumbo-x-wiki-pack.md` | 110 lines | 2026 timeline, EV range page spec, demote list; its "allowed edits / no new tickets" block addresses Astra's tree and is superseded by the brief for this tree |
| `references/greenbirdtrader-trading-framework.md` | 701 lines | Green Bird objects with HIS WORDS / HIS CHART / INFERRED tags |

## Not reviewed by instruction
`planning/phase-1-from-scratch/` (isolated), `archive/2026-09-pre-reset/` (closed; no page lacked a citation), Skylit documentation (Phase 2–3).
