# 07 — Session-fail boxes

**Outcome.** Sweep + fail-back labeler runs on every named box and level; agreement with Jumbo day-type labels is a printed matrix. Green Bird objects keep HIS WORDS / HIS CHART / INFERRED tags.

**Wiki.** `wiki/session-fail-boxes.md`, `wiki/touch-reject-hold-break-grid.md`.

**Definition → compute → pass.**
1. Boxes and levels: `box.6-9`, `box.gb.nyam` (events counted from 10:00), `box.gb.10-11`, `box.gb.hour`, `box.gb.asia` (inferred 20:00–00:00), `box.gb.london` (inferred 02:00–05:00), `box.jumbo.london` (separate), `box.prior-rth`, `lvl.tdo` (00:00 print + 5m close-back), `lvl.nwog` (Friday settlement vs Sunday 18:00), `lvl.0930open`; `loc.gp` (50–61.8 of completed impulse, location only); `label.aplus` = sweep observed.
2. Events under `grid.gb.c5` (faithful) and `b.c1`; depth `d` and cap `k` as upgrades, not as the A+ definition.
3. Agreement matrix vs ticket 01 / 03 labels (Judas / single-extended / single-purged / neither); post-event grid outcomes; magnet reach (TDO, NWOG, PDH/PDL, opposite edge).
4. Pass command: `... run_phase1_objects.py report --family fail`

**Acceptance criteria.**
- Matrix rows sum to the F session count; no `box.gb.nyam` event before 10:00.
- Jumbo London and GB-London are different rows.
- `label.aplus` true iff a sweep was observed; unknown if coverage insufficient; not gated on depth `d`.
- Excluded items absent from the row list: 25-pt partials, 7:30 NY true open, “above TDO = short”, wickless model, fleet/DLL, SMT-as-GB, FVG/CISD as GB objects.

**Blocked by.** 02 (box construction), 03 (labels).
**Out of scope.** Entries, exits, partials, any P&L.
