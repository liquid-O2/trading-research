# GEX walls and max pain

## Definition
Three strike-level objects from the dealer-gamma map: the call wall, the largest call gamma above spot, resistance as dealers sell into it; the put wall, the largest put gamma below, support as dealers buy into it; max pain, the strike where option value is lowest, toward which price drifts into expiry `[GEX p.13]`. That is the text. The p.13 chart draws three ranked call walls (▲ 740, ▲▲ 732, ▲▲▲ 730 against spot 731.98 — the third below spot) and the p.15 panel prints the put wall and max pain at the same strike (715), so the drawn object is a ranked top-3 set per option side on either side of spot (`.rank{1,2,3}` named variants) and the one-per-side rule is its faithful reduction; the same panels mark a "Vol Trigger" level, print OI-GEX beside VOL-GEX (volume-weighted) and a dealer hedge flow "per 1 % move" — none defined in the text (recorded, not built). In long gamma the walls are hard boundaries, in short gamma they break easily `[GEX p.13]`; gamma clusters near the money and hedging intensity rises into 0DTE `[GEX p.16]`; charm pulls toward the biggest open-interest strikes `[GEX p.17]`. Ids `value.node.callwall.<product>`, `value.node.putwall.<product>`, `value.node.maxpain.<product>` on the product table of [options-nodes](options-nodes.md) (NDX, NDXP, SPX, SPXW native; QQQ, SPY, NQ.OPT variants).

## Citations
- Net GEX by strike, call wall and max pain marked `[GEX p.7]`; key levels `[GEX p.13]`; where to anchor: major strikes, high OI, front expiry and 0DTE, events `[GEX p.14]`; strikes and 0DTE `[GEX p.16]`; vanna and charm `[GEX p.17]`; confirm the fade / the break with order flow `[GEX p.18]`; re-check after a big impulse `[GEX p.19–20]`; two gamma models disagreeing near the flip `[K18 p.4]`.

## Faithful object
Per product at 09:25 ET, from the EOD open-interest vintage and reconstructed Greeks (dte ≤ 14; ≤ 7 named): call wall = the strike with the largest call gamma × OI above native spot; put wall = the strike with the largest put gamma × OI below; max pain = the strike minimizing the total intrinsic value of open calls plus puts at expiry for the nearest expiry. Each row carries product, native, mapped_nq, map_known_at, OI_vintage as on [options-nodes](options-nodes.md). Intraday 0DTE positioning is not in the data; the EOD vintage is a lag proxy. The flip is read three ways, all printed — the aggregate net-GEX root as spot moves (the p.7 sentence), the cumulative-sum-over-strikes root (the retained `family_gex.py`), and the per-strike sign change the p.7 bars show — and the regime two ways, by the sign of net GEX (p.6) and by spot vs flip (p.7, p.19).

## Upgrades
- dte ≤ 7 vs ≤ 14; nearest-expiry-only vs all expiries; QQQ, SPY, NQ.OPT rows; vanna / charm not computed (D3 in `../RULES.md`).

## Outcomes
- Grid at each wall on its own side (call wall above, put wall below, plus the ranked variants), split by gamma regime and by the p.14 location state (approaching the strike: reject vs accept; already at the strike: contained vs trending away); close distance to the nearest of call wall / put wall / max pain on expiry days; native vs mapped disagreement; coincidence with EV bands and −0.5.

## Links
[options-nodes](options-nodes.md) · [ev-range-expected-move](ev-range-expected-move.md) · [vol-estimators](vol-estimators.md)
