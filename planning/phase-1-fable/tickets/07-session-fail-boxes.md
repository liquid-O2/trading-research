# 07 — Session-fail boxes vs Jumbo labels

**Outcome.** The sweep + fail-back labeler runs on every named box and level, and its agreement with the Jumbo day-type labels is a printed matrix.

**Wiki.** `wiki/session-fail-boxes.md`, `wiki/touch-reject-hold-break-grid.md`.

**Definition → compute → pass.**
1. Boxes and levels: `box.6-9`, `box.gb.nyam` (events counted from 10:00), `box.gb.10-11`, `box.gb.hour`, `box.gb.asia`, `box.gb.london`, `box.jumbo.london`, `box.prior-rth`, `lvl.tdo`, `lvl.nwog`, `lvl.0930open`; `loc.gp` flag; `label.aplus`.
2. Events under `grid.gb.c5` (faithful) and `b.c1`, depth `d` and cap `k` variants.
3. Agreement matrix vs ticket 01 / 03 labels (Judas / single-extended / single-purged / neither); post-event grid outcomes; magnet reach (TDO, NWOG, PDH / PDL, opposite edge); NWOG Monday fill rates; TDO touch rate beside the tier-2 73.75% `[PINE nq_stats_mapper L311–313]`.
4. Pass command: `... run_phase1_objects.py report --family fail`

**Acceptance criteria.**
- Matrix rows sum to the F session count; no `box.gb.nyam` event before 10:00.
- Faithful disagreements = sessions where `fail.6-9.gb.c5` and `judas.depth.any` disagree, printed.
- Excluded GB items (partials, 7:30 open, "above TDO = short", wickless model, CPI boxes) absent from the row list.

**Blocked by.** 02 (box construction), 03 (labels).
**Out of scope.** Entries, exits, partials, any P&L.
