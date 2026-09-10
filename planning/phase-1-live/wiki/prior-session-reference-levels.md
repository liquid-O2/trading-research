# Prior-session reference levels and touch tables

## Definition
The prior RTH close, open, initial-balance high and low, and the half gap of the session gap (the tables' rows are "1/2 Gap of pHOD Touched" and "1/2 Gap of pLOD Touched": the midpoint between today's open and the prior HOD or LOD it gapped beyond; the close-based half gap is a named variant), with the ES probability tables Ethos publishes for them: opening location relative to the previous session (gap up / down, within prior IB, within prior value) and which prior levels get touched given that location `[MAMT p.21–23]`. Ids `lvl.pclose`, `lvl.popen`, `lvl.halfgap`, `lvl.pib.high`, `lvl.pib.low`. PDH / PDL live on [session-fail-boxes](session-fail-boxes.md); prior VAH / VAL / POC on [value-and-profiles](value-and-profiles.md).

## Citations
- Opening location rows; opens above / below the previous range and within the previous range touch tables; IB rows `[MAMT p.21–23]` (ES, four contracts, 1,040 days 2021–2024, PST).
- Gap statistics: 70–75% eventually fill; small gaps under 0.5% fill same-session about 65%, gaps over 1% about 35%; a Micro Nasdaq study found no gap-fade edge `[MAMT p.19]`.

## Faithful object
`lvl.pclose` = last print of the prior 16:00 RTH close (settlement as a named row); `lvl.popen` = prior 09:30 first print; `lvl.pib.high` / `low` = prior 09:30–10:30 H / L; `lvl.halfgap` = (pHOD + today's 09:30 open) / 2 when the open is above pHOD and (pLOD + open) / 2 when it is below pLOD (the p.22–23 rows), undefined otherwise; `lvl.halfgap.close` = (prior close + open) / 2 as the named variant; `known_at` 09:30. The printed "1/2 Gap of pHOD Touched" cells equal the "Opens Above pHOD" shares to the digit, so the row is recomputed in both readings (touch rate; denominator share). Opening-location class = today's 09:30 open vs prior close, prior H / L, prior IB, prior VA.

## Upgrades
- Gap size bins (< 0.5%, 0.5–1%, > 1%); same-session vs eventual fill; up vs down gaps.

## Outcomes
- MAMT p.21–23 rows recomputed on NQ F per opening class (quoted ES cell beside the NQ cell); gap-fill rates by bin; time-to-touch.

## Links
[prior-eth-profile](prior-eth-profile.md) · [open-location-switch](open-location-switch.md) · [session-fail-boxes](session-fail-boxes.md) · [tpo-ib-auction](tpo-ib-auction.md)
