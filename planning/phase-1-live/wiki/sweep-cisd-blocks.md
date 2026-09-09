# Sweep, CISD, and rejection blocks

Not a Green Bird object. GB sweep + fail-back of a *session box* lives on [session-fail-boxes](session-fail-boxes.md). This page is the Jumbo/Pine **candle** construction: three-candle sweep, CISD, rejection block.

## Definition
**Sweep block (Jumbo):** candle 2 sweeps candle 1; candle 3 closes beyond candle 2; rejection blocks use the sweep wick `[TBR p.25–29]`. **CISD:** change in state of delivery — opposing-run scan after a sweep, with body-inside / wick-envelope / close-cross variants in Pine `[PINE Open Source Fractal - Customized.txt:1–118,306–342]` `[PINE HTF Sweep Model with CISD Table.txt:112–179]`. These are candle objects with formation and invalidation times. They are not SMT and not a GB grade.

## Citations
- TBR 2/3/5m three-candle sequence; wick vs body rejection `[TBR p.25–29, p.29 L443]`.
- Open Source Fractal: C2 sweep/close-back, CISD opposing-run, C3/C4 open-to-prior-mid, invalidation; HTF lookahead is not causal availability `[PINE Open Source Fractal - Customized.txt:523–951]`.
- HTF Sweep Model: screener / close-inside / body-inside / delayed CISD close crossing `[PINE HTF Sweep Model with CISD Table.txt:300–408,537–727]`.
- Whole-body test tightening `[PINE HTF Sweeps & Liquidity Levels with CISD.txt:694–696]`.
- Log-wick midpoint, wick-lick, expansive, pro-trend, silver subtypes `[PINE Sweep, CISD, MTF FVG & Key Levels.txt:652–724,1084–1440]`.

## Faithful object
- `block.sweep.tbr.3m`: 3-minute NQ OHLC; C2 high/low strictly beyond C1; C3 close beyond C2 in the sweep direction; block bounds = C2 wick; known at C3 close.
- `cisd.fractal.literal`: Open Source Fractal opposing-run rule as coded (lookback, mintick score, overlap), causal replay only (no HTF lookahead).

## Upgrades
- Timeframe 1/3/5/15m and HTF completed bars.
- Wick vs body vs close sweep; arithmetic vs log midpoint.
- Body-envelope vs wick-envelope CISD; scan 10/20 bars.
- Invalidation: close vs wick through far edge.
- All-event lifecycle (no display-history cap).

## Outcomes
Formation/confirmation delay; block revisit; penetration; invalidation; reject vs continuation on the shared grid; no-event sessions. Code-versus-causal disagreements retained as diagnostics, not silently repaired.

## Links
[fvg-body-gaps](fvg-body-gaps.md) · [session-fail-boxes](session-fail-boxes.md) · [touch-reject-hold-break-grid](touch-reject-hold-break-grid.md) · [smt-divergence](smt-divergence.md)
