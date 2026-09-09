# SessionStat historical high/low envelopes

Family: **Jumbo**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[SessionStat+.pdf, pp.3–6](../../../sources/documents/jumbo/SessionStat%2B.pdf#page=3) presents simple mean, weighted mean and median H/L levels, shorter “minimum average” swing levels, and extensions from the upper-minus-lower statistical range. UI lookback is 60; upper/lower expansion defaults 0.5. It supports 15m/1h/4h/daily/weekly and four custom slots. Weights, minimum-average estimator and reference anchor are unspecified. [SessionStat+.pdf, pp.7–12](../../../sources/documents/jumbo/SessionStat%2B.pdf#page=7) documents bar/time detection differences, same-day timestamp restrictions, 23:59 workaround, and 09–12/RTH/daily envelopes. Chop can cause repeated breaches; low volatility can leave envelopes unreachable. [xfcmg2.pdf, pp.19,45–46; posts 2074192880776647082,1928125498736955814](../../../sources/documents/jumbo/xfcmg2.pdf#page=19) shows 09–12 minimum-average and London H4 usage.

## Computability and faithful reconstruction

OHLC gives long history and event-clock reconstruction. Trade/bar variants are feasible on their own samples. Unspecified estimator branches remain blocked.

Keep simple/weighted/median/minimum-average identities distinct. Store sample membership, anchor, upper/lower distance, lookback and availability. Preserve the source same-day limitation in its benchmark; label a cross-midnight implementation as an upgrade.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **prior-only-60**, **clock-exact/cross-midnight**, **mean/median/empirical-quantile**, **vol-normalized**, and **fixed-grid/time/trade/volume/dollar-bar** versions.
- **weighted-mean** and **minimum-average** require Q06 before faithful counting; proposed alternative weights receive separate names.

## Phase 1 outcomes

Upper/lower reach and both/neither, width coverage, overshoot, return to envelope/open, repeated breaches in chop, unreachable levels and stability by year/session/volatility.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q06 defines weights, minimum-average estimator, H/L distance anchor and lookback inclusion. Do not infer these from UI labels.

## Related

[distribution envelopes](distribution-envelopes.md), [time based ranges](time-based-ranges.md), [jumbo p zones](jumbo-p-zones.md)

Review findings: J-SS-01, J-SS-02, J-SS-03, J-X-06, J-X-14. [Review ledger](../REVIEW_LEDGER.md).
