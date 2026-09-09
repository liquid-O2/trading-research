# PRD — Phase 1: measure and compare the objects

## Problem
The sources describe range, envelope, value, flow and session-fail objects with published or hardcoded statistics of unknown provenance. Nothing has been recomputed on our data with one shared definition of touch, reject, hold and break. Without that, later phases would train on labels nobody has checked.

## Goal (one outcome)
Every object family in `wiki/index.md` is computed on frozen slice F (NY trade dates 2024-01-02 → 2026-08-31) with a faithful source object and named upgrades, and one pass command prints, per family and variant:

`family | variant | n | faithful disagreements | experiment status | report path`

"Better" means descriptive statistics on F, never P&L. Null or worse is a valid result.

## Non-goals
- No trading, no execution, no account or risk work. The $2,000 average daily net target, $1,000 daily loss cap, one account and one NQ mini are locked facts, not Phase 1 deliverables.
- No predictor training, no learned selector of ranges, no learned reversal / P-zone model (Phase 2–3).
- No MBP-10, no MBO, no paid data expansion `[JJX L16]`.
- No edits to `sources/`, raw data, `archive/`, `planning/phase-1-from-scratch/`, or `planning/phase-1-fable/`.
- No Skylit Heatseeker / Flowseeker / Atlas work.

## Users
The researcher running the pass command and reading `wiki/` before deciding Phase 2 scope.

## Locked decisions
Execute NQ, ES is information. No overnight hold across the day boundary (nothing measured across 17:00 → 18:00). Range high and low are rails, not reversal zones. Width tables use 6–9 H−L **and** prior RTH H−L; those tables are not the same. Extensions 1.33 / 1.66 come from the 6–9 (or London) range, are not P-zones, and are not called ATL. P-zone formula unavailable → disclosed approximation as benchmark (500-session percentile bands). One shared touch / reject / hold / break grid. Fixed clock grid, no free-form box. MBP-1 only. Options nodes are native on **NDX, NDXP, SPX, SPXW**; QQQ, SPY, NQ.OPT are named variants. Cash NDX/SPX minutes are not assumed. A+ = a sweep happened. Hidden book and unpublished node engines print not-measurable.

## Stories (each checkable by the pass command or by a file existing)

1. **Tracer bullet.** Pass command `--family range` prints `range.6-9.published` with `n` equal to F sessions that survive the coverage rule, `faithful disagreements = 0`, status `measured`, report at the printed path containing the path-class table, both width tables, and the −0.5 reversal rate. (ticket 01)
2. **Published tables recomputed.** Range and path reports contain the XF p.24 range-size table and the TBR p.30 reversal statistic recomputed on F and on L, each quoted cell beside the recomputed cell. (ticket 01)
3. **Clock grid.** Every row in `wiki/clock-grid-and-bars.md` prints a line; indistinguishable coverage tables are merged and listed. Jumbo London is a separate row from GB-London. (ticket 02)
4. **Day class and open location.** Each F session carries `path_class`, `break_order`, `day_type`, `open_cell` (27 cells), `balance`, `edge_clean`. XF p.11 rows recomputed. In-value vs in-range vs outside-both double-break printed. 76% claim printed on **two** denominators (A-period 09:30–10:00, and frozen OR-edge return). (ticket 03)
5. **AM envelope grid.** Every EV, SessionStat, extension and P-zone row prints reach, overshoot, reject, time-to-touch, in/out-of-value, calibration with Wilson 95%. P-zone `pz.approx.A` uses the 500-session disclosed bands. (ticket 04)
6. **CVD and SMT.** Five CVD variants and SMT (OHLC-4, trade NQ, Pine 3/3 matcher) print event counts and pairwise agreement. (ticket 05)
7. **Value, absorption, nodes.** VP, delta, key zones, absorption A/B, BigTrades 100/75, footprint diagonal, VWAP row, and OI/gamma nodes for **NDX, NDXP, SPX, SPXW** print grid outcomes. QQQ, SPY, NQ.OPT are named variants. Each node row has native, mapped_nq, map_known_at, OI_vintage. Hidden book, dealer inventory, Skylit print `not-measurable`. (ticket 06)
8. **Session-fail boxes.** Every box in `wiki/session-fail-boxes.md` prints fail-back counts and an agreement matrix against Jumbo labels; GB-NYAM outcomes start at 10:00; A+ is sweep-only. (ticket 07)
9. **FVG / CISD / TPO.** First-presented FVG, TBR/Pine CISD-blocks, and TPO/AMT labels print on F. Not attached to GB pages. IB remains the ticket-02 comparison row. (ticket 08)
10. **One command, whole phase.** `PHASE.md` pass command with no family argument prints every family's lines and exits 0 only when every family has at least one `measured` row and no row lacks a report path.
11. **Provenance.** Every printed variant id is defined on exactly one wiki page; every quoted number carries a citation.

## Acceptance for Phase 1 as a whole
All stories pass on F. Reports live under `trading-research/reports/phase1-live/` as canonical JSON plus a Markdown twin. No file under the must-not-change list has a changed hash.

## Out of scope but recorded
`QUESTIONS_RESOLVED.md` lists closed variant grids and not-measurable rows. Nothing there blocks Phase 1.
