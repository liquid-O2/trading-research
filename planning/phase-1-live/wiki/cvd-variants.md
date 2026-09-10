# CVD variants

## Definition
CVD = the running sum of aggressive buy volume minus aggressive sell volume `[STOP p.3 L40–44]` `[VWAP p.5 L61]`. The user asked for several CVD methods, including a gamma CVD `[DTM L23]`. Phase 1 computes five named variants on the same sessions and reports where they disagree; participants are size / aggressor proxies, gamma CVD is a declared weight table, no dealer identities `[BRIEF]`.

## Citations
- Delta as a filter, delta prints, trapped crowds `[STOP p.2 L10–13, p.9 L169–171]`; is the aggression rewarded `[RD p.6 L78–89]`; CVD rolling over as trigger `[STOP p.9 L171]`; VWAP + CVD confluence `[VWAP p.5–6 L61–85]`. The "CVD median" is a plotted line on the CVD panel (`[ABS p.5]` "Plot the median line"; `[BIG p.12]` "CVD below its median"; `[STOP p.8]` "rolling over its median") whose construction no source states; when CVD is rebuilt the median is a named variant (session median of CVD so far; rolling median), never a constant.
- Databento `side` = aggressor, not customer vs dealer `[DRFL L215–219]` (assistant restating the vendor schema); MBP-1 trades carry side, size, order count `[JJX L159]`.
- OHLC-level delta proxies: Pine up/down volume rule by close position `[PINE Confluence Suite.txt:243–255]`.

## Faithful object
`flow.cvd.trade`: from NQ trades (aggressor side from MBP-1 trade events), reset at 18:00 ET, sampled per 1-second bar.

## Upgrades
| id | construction |
|---|---|
| `flow.cvd.ohlc` | 1-minute bars: volume × sign by close position in bar range (Pine rule) `[PINE Confluence Suite.txt:246–252]` |
| `flow.cvd.part.trade` | trade-level, split into size buckets ≥ 100, 20–99, < 20 (participant proxies; 100 = Jumbo's NY BigTrades threshold `[XF p.25]`) |
| `flow.cvd.part.ohlc` | bar-level split by bar volume tercile (proxy for large-participation minutes) |
| `flow.cvd.gamma` | trade-level CVD weighted by `w(price)` = sign(net dealer gamma at the nearest strike node) × {+1, −1}, gamma from [options-nodes](options-nodes.md); weight table declared in the report, never fitted |

Session reset variants: 18:00 (default), 09:30.

## Outcomes
- Divergence flags at box edges: CVD new extreme without price new extreme (and the converse) within the grid window; slope over 09:30–10:00; sign agreement between variants.
- Per-session correlation between variants; faithful disagreements = sessions where a variant's divergence flag at the AM extreme differs from `flow.cvd.trade`.
- No predictive claim: flags are columns for Phase 2.

## Links
[absorption-and-big-trades](absorption-and-big-trades.md) · [smt-divergence](smt-divergence.md) · [options-nodes](options-nodes.md) · [value-and-profiles](value-and-profiles.md)
