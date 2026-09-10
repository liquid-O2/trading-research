# Daily open (18:00) and the Sunday weekly open

## Definition
The 18:00 ET first print of each futures session, drawn as the "6 PM Daily Open" line, and the Sunday 18:00 weekly open `[PINE Sessions & VP with prev session VP & daily weekly opens.txt:84, 90, 641–642, 673–685]`. Green Bird's NWOG is the Sunday 18:00 open against Friday's close `[GB L60]`; Ethos measures overnight inventory from 6 pm `[MAMT p.14]`. Id `lvl.1800open`; the Sunday instance is the Sunday endpoint of `lvl.nwog` on [session-fail-boxes](session-fail-boxes.md).

## Citations
- Open-level inputs and session stamps `[PINE Sessions & VP with prev session VP & daily weekly opens.txt:84–93, 641–642, 673–685]`; Sunday 18:00 reopen `[GB L60]`; 6 pm as the overnight start `[MAMT p.14]`; session key 18:00 → 17:00 (`../SPEC.md` §1).
- Tier-2 hit table for overnight hourly opens during NY, e.g. "12:00am_open" 73.67 and "07:00am_midpoint" 94.19 `[PINE NQ Hourly Retracement Levels.txt:279–401]`.

## Faithful object
`lvl.1800open`: first print at 18:00:00 ET of the current session on NQ 1-second bars (trade-level first print named), `known_at` 18:00; outcomes: touch in 09:30–12:00 and by 16:00 with the shared grid.

## Upgrades
- 17:00 settlement price as a named sibling; the full overnight hourly open / mid grid (00:00 open = `lvl.tdo`) as comparison rows on [clock-grid-and-bars](clock-grid-and-bars.md).

## Outcomes
- Touch rate by 12:00 / 16:00; hourly-open hit rows recomputed on F and L beside the hardcoded values; distance from the 09:30 open.

## Links
[session-fail-boxes](session-fail-boxes.md) · [clock-grid-and-bars](clock-grid-and-bars.md) · [overnight-range](overnight-range.md) · [sources-pine-archive](sources-pine-archive.md)
