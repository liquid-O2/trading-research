# SMT divergence (sister-index hunts)

## Definition
SMT = one index takes a prior high or low while a sister index does not, or takes it later / shallower. Jumbo's classify step asks "whether sister indices already hunted the same side" `[FIND p.3 L57–58]`; the prior assistant asked how the user defines overnight relative strength `[CEX L105]`. Phase 1 treats SMT as a hypothesis evaluated continuously in the window, not a 09:30 snapshot, at several scales `[BRIEF]`. SMT is not treated as a Green Bird edge `[BRIEF]`.

## Citations
- Multi-asset comparison requested by the user (beyond three-asset dispersion tools) `[DTM L24]`; ES is information, NQ executes `[BRIEF]`.
- Cross-index data: ES / YM / RTY 1-minute bars and trades 2020 → 2026; ES MBP-1 ends 2024-08-30 `[INV L142–148, L150, L211, L235]`.
- Pine multi-symbol sweep screener (CL / ES / NQ / GC / YM / SI HTF sweeps) as a construction reference `[PINE HTF Sweep Model with CISD Table.txt:79–84, 136–142, 755–767]`.

## Faithful object
- `flow.smt.ohlc.4`: on 1-minute bars for NQ, ES, YM, RTY; level set `S1` = {Asia H/L, London H/L, 6–9 H/L, PDH/PDL}; at each minute in 09:30–12:00, flag `hunted(i, level)` when index i has traded beyond its own level; SMT event = NQ hunted and at least one sister not hunted within the next 5 minutes (and the converse). Multi-scale: level sets `S2` = prior-hour H/L, `S3` = 5-minute swing H/L (5-bar fractal `[PINE Key levels, MTF swing highs, lows & 4h candle boxes.txt:150–164]`).
- `flow.smt.pine.3-3`: Open Source Fractal 3/3 confirmed-pivot matcher as coded (lookback 200, chart mintick for both markets, min 2-tick score, overlap 2 ticks, 12-bar merge) `[PINE Open Source Fractal - Customized.txt:144–182,1200–1521]`. Code-score unit errors stay as disagreement diagnostics. Causal confirmation only.

## Upgrades
- `flow.smt.trade.nq`: NQ leg from trades (tick-precise sweep time), sisters from 1-minute bars; ES from MBP-1 where covered (to 2024-08, outside F → marked not-measurable in F).
- Lag tolerance 1 / 5 / 15 minutes; pair set NQ–ES only vs all four.
- Native-tick vs return-volatility normalized score.

## Outcomes
- SMT event count per session and level set; path class and Judas / single-break label conditional on an SMT event (labels only, no predictor training).
- Grid at the swept level after an SMT event; faithful disagreements = sessions where `flow.smt.trade.nq`, `flow.smt.ohlc.4`, and `flow.smt.pine.3-3` disagree on the presence of an event at the 6–9 edges.

## Links
[range-path-class](range-path-class.md) · [session-fail-boxes](session-fail-boxes.md) · [data-coverage](data-coverage.md) · [cvd-variants](cvd-variants.md)
