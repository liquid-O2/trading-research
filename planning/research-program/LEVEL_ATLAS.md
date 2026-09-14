# Level Atlas: a causal census of option-derived levels against daily extremes and strategy references

Registered 2026-09-14 as the first Phase 3 step, runnable as soon as the native option exposure boards from P2-09 and P2-10 exist. It is descriptive: no fitting, no selection, no candidate changes. It tests one stated thesis with counts: that option-derived levels mark the day's high or low, and that a strategy's own reference works best when such a level sits nearby.

## Inputs, all causal

- Exposure boards per root and expiry from P2-10: NDX, NDXP, SPX, SPXW, SPY, QQQ, NQ options and ES options where owned, with the board's availability clock (prior-date OI, quote age, chain coverage) recorded per level. A level is usable on a day only from its availability clock onward.
- Level types per board: the largest absolute signed-gamma strike (the existing key-gamma reference), the call wall and put wall, the gamma flip, max pain, and the top three strikes by absolute gamma, vanna and vega exposure, each mapped to NQ through the concurrent price ratio the existing code uses; plus the day's implied move from the front expiry.
- Native daily extremes from the full account-day market view (P15-02): the account-day high and low, the regular-session high and low, and their times.
- Every strategy branch's reference level and decision time from the corrected baseline population (B0.1), and its outcome under the fixed benchmark from P15-03.

## What is counted, per day and per level

1. **Extreme proximity.** Distance in ticks and in S units from each usable level to the day's high and to the day's low; whether the extreme printed within 4, 8 and 16 ticks of the level; the time of the extreme relative to the level's availability. Reported per root, expiry, level type, year, session bucket and volatility regime, with counts and block-bootstrap intervals, against a matched control of levels shifted by the deterministic offsets the search contract already defines for density-matched controls.
2. **Strategy alignment.** For every branch opportunity: the signed distance from its reference to the nearest usable level of each type, in S units; then the benchmark outcome distribution conditional on that distance in fixed bins (within 0.1 S, 0.25 S, 0.5 S, 1 S, beyond). Reported per branch and per level type, with the unconditional rate beside it.
3. **Root agreement.** When two or more roots place a level within 0.25 S of each other, the same two measurements for the agreeing level versus single-root levels.
4. **Change features.** The one-day change in each level's exposure and the intraday rate of change of aggregate gamma and of executed volume, binned, against the same two measurements.

## Outputs

`LEVEL_ATLAS.md` and `LEVEL_ATLAS.json` under the producing attempt, with every number pointing to its artifact; one CSV per root. A limitations section states chain coverage per root and year, the inventory-sign assumption, and that the atlas is descriptive.

## Boundary

The atlas informs the Phase 3 location pack: which roots, level types, tolerances and conditions deserve a fitted location expert, and which strategy branches show alignment sensitivity worth a conditional plan in Phase 2. It selects nothing itself, adds no candidate to Phase 1.5, and its dates carry research exposure like every other census.

## Profile Atlas: volume-profile structures as a separate level family

Registered 2026-09-14 on the user's instruction that profile-derived areas are their own, heavily discretionary family. The discretion is removed by enumeration, not by choice. Every cell below is measured exactly as the option levels above (extreme proximity against shifted controls; strategy alignment by distance bin; root or window agreement), with the same causal availability rule: a profile is usable only after its window completes and its execution volume is known.

| Axis | Enumerated values |
| --- | --- |
| Profile window | prior regular session; prior full account day; overnight (18:00 to 09:30); composite of the prior five sessions; composite of the prior calendar week; developing intraday profile at the decision time, as an immutable version |
| Structure | point of control; naked point of control (never revisited since formed); value-area high and low at the registered 70% rule; high-volume node; low-volume node; shelf; ledge |
| Box construction | the node band the Phase 1.5 specification defines (adjacent bins at or above 50% of the peak until a valley or eight bins); a fixed band of 0.1 S, 0.25 S or 0.5 S around the structure's price; the structure's own plateau width when it has one |
| Freshness | formed within the prior session; within five sessions; any age; never revisited since formation |

Shelf and ledge have no printed source definition. Their operational definitions are registered in P15-05 as labelled research choices: a shelf is a run of at least three adjacent bins whose volumes lie within 20% of each other and whose mean exceeds twice the profile's median bin volume, bounded on one side by a drop of at least 50% (the ledge is that boundary bin). These definitions are hypotheses to be measured, not source rules, and the atlas reports them beside the source-defined structures.

Outputs, boundary and exposure follow the option-level atlas above; the profile family is reported in its own tables so it can be selected or rejected separately in the Phase 3 pack.
