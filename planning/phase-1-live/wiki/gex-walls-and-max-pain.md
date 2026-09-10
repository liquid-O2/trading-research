# GEX walls and max pain

## Definition
Three strike-level objects from the dealer-gamma map: the call wall, the largest call gamma above spot, resistance as dealers sell into it; the put wall, the largest put gamma below, support as dealers buy into it; max pain, the strike where option value is lowest, toward which price drifts into expiry `[GEX p.13]`. In long gamma the walls are hard boundaries, in short gamma they break easily `[GEX p.13]`; gamma clusters near the money and hedging intensity rises into 0DTE `[GEX p.16]`; charm pulls toward the biggest open-interest strikes `[GEX p.17]`. Ids `value.node.callwall.<product>`, `value.node.putwall.<product>`, `value.node.maxpain.<product>` on the product table of [options-nodes](options-nodes.md) (NDX, NDXP, SPX, SPXW native; QQQ, SPY, NQ.OPT variants).

## Citations
- Net GEX by strike, call wall and max pain marked `[GEX p.7]`; key levels `[GEX p.13]`; where to anchor: major strikes, high OI, front expiry and 0DTE, events `[GEX p.14]`; strikes and 0DTE `[GEX p.16]`; vanna and charm `[GEX p.17]`; confirm the fade / the break with order flow `[GEX p.18]`; re-check after a big impulse `[GEX p.19–20]`; two gamma models disagreeing near the flip `[K18 p.4]`.

## Faithful object
Per product at 09:25 ET, from the EOD open-interest vintage and reconstructed Greeks (dte ≤ 14; ≤ 7 named): call wall = the strike with the largest call gamma × OI above native spot; put wall = the strike with the largest put gamma × OI below; max pain = the strike minimizing the total intrinsic value of open calls plus puts at expiry for the nearest expiry. Each row carries product, native, mapped_nq, map_known_at, OI_vintage as on [options-nodes](options-nodes.md). Intraday 0DTE positioning is not in the data; the EOD vintage is a lag proxy.

## Upgrades
- dte ≤ 7 vs ≤ 14; nearest-expiry-only vs all expiries; QQQ, SPY, NQ.OPT rows; vanna / charm not computed (D3 in `../RULES.md`).

## Outcomes
- Grid at each wall, split by gamma regime (above / below `value.node.flip.<product>`); close distance to max pain on expiry days; native vs mapped disagreement; coincidence with EV bands and −0.5.

## Links
[options-nodes](options-nodes.md) · [ev-range-expected-move](ev-range-expected-move.md) · [vol-estimators](vol-estimators.md)
