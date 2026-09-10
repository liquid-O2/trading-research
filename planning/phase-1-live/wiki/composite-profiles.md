# Composite profiles

## Definition
Profiles merged over several days or weeks; the HVNs and LVNs that survive across that span are the levels the whole market respects, and a naked POC that lines up with a composite shelf is a level to build a session around `[VP2 p.6]`. Ethos uses a yearly composite (365 days of volume) as support behind a failed-auction long `[BIG p.10]`, reads a yearly-composite low-participation zone as sliced through then used as resistance `[CONT p.7]`, and names the yearly POC as an objective `[K10 p.12]`. Ids `value.vp.composite.{5d,20d,250d}`.

## Citations
- Composite profile, naked POC + composite shelf `[VP2 p.6]`; yearly composite as support, thin volume below the node `[BIG p.10–11]`; yearly composite low-participation zone `[CONT p.7]`; yearly POC as the HTF objective `[K10 p.12]`.
- Caution: trade the current auction, not last week's `[MATH p.12]`.

## Faithful object
`value.vp.composite.5d`, `.20d`, `.250d`: trade-level profile over the trailing N completed sessions (18:00–16:00 each), 1-tick bins, POC, VA 70%, HVN / LVN / shelf / ledge by the `value.kz` rules; `known_at` = prior session close; refreshed daily.

## Upgrades
- 4-tick bins; OHLC-1m profile for the 250-day row (L slice); RTH-only scope.
- Node-survival rule: HVN present in both 20d and 250d as a "heavyweight" flag `[VP2 p.6]`.

## Outcomes
- Grid at composite HVN, LVN, POC; slice-through vs stall at composite LVNs `[CONT p.7]`; naked-POC + composite-shelf coincidence counts.
- Faithful disagreements: node sets that differ between 20d and 250d.

## Links
[value-and-profiles](value-and-profiles.md) · [unfinished-business](unfinished-business.md) · [dealing-range](dealing-range.md)
