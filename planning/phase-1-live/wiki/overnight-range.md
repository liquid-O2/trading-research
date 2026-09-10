# Overnight range (ONH / ONL)

## Definition
The high and low of the full overnight session 18:00–09:30 ET (`range.on.1800-0930`), the reference behind the Ethos statistic that one of the two is touched in RTH about 94% of the time, "either, not both" `[MAMT p.15]`. It is a rail and a timing filter: a long level a few points above the overnight low is not wrong, its timing is `[MAMT p.15]`. Distinct from the Asia and London sub-boxes on [clock-grid-and-bars](clock-grid-and-bars.md) and from the GB Asia box.

## Citations
- 94% chance of touching either the overnight high or the overnight low during the current session `[MAMT p.15]`; ES table: ONH and ONL both touched 20–24%, ONH or ONL 92–95%, ONH 60–65%, ONL 52–57% (ES, four contracts, 1,040 days 2021–2024, PST sessions) `[MAMT p.20–21]`.
- Overnight inventory from 6 pm to 9:30 as the window `[MAMT p.14]`.
- Pre-open checklist: locate the overnight vs yesterday's value `[AMT1 p.12]`.

## Faithful object
`range.on.1800-0930`: H / L of 18:00:00–09:29:59 ET on NQ 1-second bars, `known_at` 09:30; outcomes in 09:30–16:00 with the shared grid (touch `t2`).

## Upgrades
- Window start 20:00 (GB Asia clock) as a named variant; trade-level H / L.
- Touch by 12:00 vs by 16:00; either / both / neither as three rows.

## Outcomes
- Recompute of the MAMT p.21 overnight rows on NQ F (quoted cell beside recomputed cell); time-to-first-touch; which extreme first.
- Distance from the first-touched extreme to the nearest RTH level in the recipe under test (the "level above ONL" timing claim, descriptive only).

## Links
[overnight-profile](overnight-profile.md) · [clock-grid-and-bars](clock-grid-and-bars.md) · [session-fail-boxes](session-fail-boxes.md) · `../RULES.md` A1.1
