# PRD — Phase 1: measure and compare the objects

## Problem
The sources describe many range, envelope, value and flow objects with published or hardcoded statistics of unknown provenance. Nothing has been recomputed on our own data with one shared definition of touch, reject, hold and break. Without that, Phase 2 (context) and Phase 3 (location) would train on labels nobody has checked.

## Goal (one outcome)
Every object family in `wiki/index.md` is computed on the frozen slice F (NY trade dates 2024-01-02 → 2026-08-31) with a faithful source object and named upgrades, and one pass command prints, per family and variant:

`family | variant | n | faithful disagreements | experiment status | report path`

"Better" means descriptive statistics on F, never P&L `[BRIEF]`. Null or worse is a valid result and is printed as such.

## Non-goals
- No trading, no execution, no account or risk work. The $2,000 average daily net target, $1,000 daily loss cap, one account and one NQ mini are locked facts, not Phase 1 deliverables `[BRIEF]`.
- No predictor training, no learned selector of ranges, no learned reversal / P-zone model (Phase 2–3).
- No MBP-10, no MBO, no paid data expansion `[JJX L16]` `[AGENTS.md]`.
- No edits to `sources/`, raw data, `archive/`, or `planning/phase-1-from-scratch/`.
- No Skylit Heatseeker / Flowseeker / Atlas work.

## Users
The researcher running the pass command and reading `wiki/` before deciding Phase 2 scope.

## Locked decisions carried in
Execute NQ, ES is information. No overnight hold across the day boundary (affects only window ends: nothing is measured across 17:00 → 18:00). Range high and low are rails, not reversal zones. Width table uses 6–9 H−L and prior RTH H−L. Extensions 1.33 / 1.66 come from the 6–9 (or London) range, are not P-zones, and are not called ATL. P-zone formula unavailable → disclosed approximation as benchmark. One shared touch / reject / hold / break grid. Fixed clock grid, no free-form box. MBP-1 only. Hidden book and unpublished node engines are printed as not measurable `[BRIEF]`.

## Stories (each checkable by the pass command or by a file existing)
1. **Tracer bullet.** I run the pass command with `--family range` and get one line for `range.6-9.published` with `n` equal to the number of F sessions that survive the coverage rule, `faithful disagreements = 0`, status `measured`, and a report file at the printed path containing the path-class table and the −0.5 reversal rate. Passes when the JSON at the path validates against `SPEC.md` §6 and its `n` matches the printed `n`. (ticket 01)
2. **Published tables recomputed.** The `range` and `path` reports contain the XF p.24 range-size table and the TBR p.30 reversal statistic recomputed on F and on L, each cell printed beside the quoted number with the absolute difference. Passes when every quoted cell has a recomputed cell with `n > 0`. (ticket 01)
3. **Clock grid.** Every row in `wiki/clock-grid-and-bars.md` prints a line; rows whose coverage table is indistinguishable from another row are merged and the merge is listed in the report. Passes when the number of printed clock rows equals the table rows minus listed merges. (ticket 02)
4. **Day class and open location.** Each F session carries labels `path_class`, `break_order`, `day_type`, `open_cell` (27 cells), `balance`, `edge_clean`, and the XF p.11 rows are recomputed for the two named cells. Passes when the label file has one row per session and no null in those columns. (ticket 03)
5. **AM envelope grid.** Every EV, SessionStat, extension and P-zone row prints reach, overshoot, reject, time-to-touch and in/out-of-value with `n`, and a calibration column. Passes when each row's calibration share is printed with a Wilson 95% interval. (ticket 04)
6. **CVD and SMT.** Five CVD variants and two SMT variants print divergence / event counts and pairwise agreement; the trade-level variant is the faithful row. Passes when the agreement matrix is square and every off-diagonal entry has `n`. (ticket 05)
7. **Value, absorption, nodes.** VP (trade-level and OHLC), delta profile, key zones, absorption A and B, BigTrades 100 / 75, and OI / gamma nodes print grid outcomes; hidden book, dealer inventory and Skylit engines print `not-measurable`. Passes when those three rows exist with that status. (ticket 06)
8. **Session-fail boxes.** Every box in `wiki/session-fail-boxes.md` prints fail-back counts and an agreement matrix against Jumbo labels; GB-NYAM outcomes start at 10:00. Passes when the matrix rows sum to the session count and no GB-NYAM event timestamp precedes 10:00. (ticket 07)
9. **One command, whole phase.** `PHASE.md`'s pass command with no family argument prints every family's lines in one table and exits 0 only when every family has at least one `measured` row and no row is missing a report path. (all tickets)
10. **Provenance.** Every variant id printed by the pass command is defined in exactly one wiki page (its Faithful object or Upgrades section), and every number quoted in a wiki page carries a `[SOURCE p./L]` citation. Passes by grep over those sections: one defining page per id.

## Acceptance for Phase 1 as a whole
All ten stories pass on F. Reports live under `trading-research/reports/phase1-fable/` as canonical JSON plus a Markdown twin. No file under the must-not-change list has a changed hash.

## Out of scope but recorded
`QUESTIONS.md` lists the closed variant grids and the not-measurable rows. Nothing there blocks Phase 1.
