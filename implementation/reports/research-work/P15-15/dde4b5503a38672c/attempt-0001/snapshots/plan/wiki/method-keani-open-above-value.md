# Keani — open above value

## Current evidence

Phase 1 setup implementation and the acquired historical census are complete. These counts describe observed setups with branch-specific input limitations; they are not fills or profitability. The source definitions below retain author-specific boundaries. Our inferred reconstruction is versioned separately.

[Full method measurements](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/KEANI-OPEN-ABOVE-VALUE.md) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md) · [Research status](current-status.md).

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE | full acquired historical measurement | 6 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/KEANI-OPEN-ABOVE-VALUE.md |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE | M08 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |

## Source definitions


Operating method / KEANI-OPEN-ABOVE-VALUE. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


[AVG] pp.21–22 calls this **Keani's own setup**, which Sires then validates through AMT. It is separate from the unnamed member above.

| Step | Source loop | Source-object implementation snapshot and evidence limits |
|---|---|---|
| 1 | Current TPO opens fully above yesterday's value: the entire A period is clear of prior VAH. Observe the developing profile around 10:00. | [O050](cash-open-reference.md) · [O061](value-and-profiles.md) · [O062](value-area.md) · [O078](tpo-ib-auction.md). The complete A period is checked against the available prior profile, with native profile and time-period identities. All four frozen empirical openings remain unclassified because prior profiles are unverified. |
| 2 | Value builds higher; observe rejection at POC or previous VAH within that bullish auction. | [O063](developing-profile.md). Developing snapshots and ordered value-build/rejection evidence are implemented; later profile values cannot rewrite an earlier observation. |
| 3 | Price breaks the current developing VAH with aggressive buying imbalances. Freeze the actual imbalance prices and their known time. | [O063](developing-profile.md) · [O109](footprint-imbalance-zones.md). The developing-VAH breakout and actual imbalance band retain separate identities and clocks. The source's aggressive breakout interpretation remains distinct from literal price measurements. |
| 4 | Price returns to those imbalance prices; buyers defend them, with the DOM and time of day supporting the trade. | [O100](dom.md) · [O109](footprint-imbalance-zones.md) · [O120](footprint.md). The later retest must join the same imbalance and its local defense. Missing DOM/source confirmation remains an explicit hole. |
| 5 | Enter long toward a worthwhile, preselected HTF objective, with defined risk. | [O139](structural-risk.md) · [O141](trade-objective.md) · [O142](position-management.md) · [O150](order-lifecycle.md). Preselected risk, objective and subsequent management/lifecycle admission are implemented. They remain unavailable for a historical candidate without the source records. |

All steps: [AVG] pp.21–22. **Not standalone:** an opening gap, `open > current VAH`, an eventual bullish day, or a break without defense on return. Around 10:00 is an observation point, not access to the finished day type. The displayed dashboard results and the document's data-collection discussion do not establish this setup's entry edge.

### Phase 1 predicate — `KEANI-OPEN-ABOVE-VALUE`

```sql
prior_value_fixed AND a_period_complete
AND a_low > prior_vah
AND developing_value_builds_higher AND source_rejection_observed
AND dev_vah_known_at <= breakout_at
AND breakout_close > dev_vah_at_break
AND aggressive_buy_imbalance_break
AND imbalance_band_known_at <= retest_at
AND breakout_at < retest_at AND retest_at <= defense_at
AND buyers_defend_same_imbalance_band AND dom_supports_long
AND time_of_day_allowed AND objective_fixed AND risk_defined
AND a_end_at <= observation_at AND observation_at <= breakout_at
AND defense_at <= decision_at AND side = 'long'
```

Citation: [AVG] pp.21–22. The source's near-10:00 observation does not define an exact universal minute tolerance. Missing that convention is an explicitly named timing variant. A developing-VAL short is not claimed as Keani's published mirror.


## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Session and range geometry.** [Opening location and participation](open-location-switch.md).

**Price references and price-action confirmation.** [09:30 cash-open price](cash-open-reference.md).

**Auction and profile structure.** [Auction balance](auction-balance.md) · [Volume profile](value-and-profiles.md) · [Profile value area](value-area.md) · [Developing profile snapshot](developing-profile.md) · [Profile point of control](profile-poc.md) · [Time-price-opportunity profile](tpo-ib-auction.md) · [Prior-session auction landmarks](prior-session-reference-levels.md) · [Remaining auction objectives](unfinished-business.md).

**Auction routes inside a method.** [Accepted break and defended boundary retest](break-retest.md) · [Higher- and lower-timeframe control alignment](htf-ltf-alignment.md).

**Order-flow evidence.** [Executed aggressor-side trades](aggressor-trades.md) · [DOM at a planned location](dom.md) · [Diagonal footprint imbalance stacks](footprint-imbalance-zones.md) · [Native candle footprint](footprint.md).

**Risk, objectives and process.** [Entry-side structural invalidation](structural-risk.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md).

**Research, execution-study and risk records.** [Observed order lifecycle](order-lifecycle.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
