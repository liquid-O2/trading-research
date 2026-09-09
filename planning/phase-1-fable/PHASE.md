# PHASE 1 — measurement and comparison of objects

## One outcome
Every object family in `wiki/index.md` is measured on the frozen slice F (NY trade dates 2024-01-02 → 2026-08-31) with a faithful source object and named upgrades, and the pass command prints one line per variant.

## One pass command
```
/tmp/trading-research-venv/bin/python trading-research/tools/run_phase1_objects.py report
```
Prints, one row per family × variant, in this order of families (range, path, open, env, vol, flow, value, fail):

```
family | variant | n | faithful disagreements | experiment status | report path
range  | range.6-9.published | <n> | 0 | measured | trading-research/reports/phase1-fable/range/range.6-9.published.json
...
```
Exit code 0 only when every family has at least one `measured` row and no row lacks a report path. `experiment status` ∈ {measured, null, worse, better, deferred, not-measurable}; definitions in `SPEC.md` §6. Per-family runs: `report --family <f>`.

## Ticket spine (thin vertical slices, in order)
1. `tickets/01-runner-and-6-9-path-report.md` — runner, frozen slice, grid, faithful 6–9 + path report (tracer bullet).
2. `tickets/02-clock-grid-and-bars.md` — clock / bar / volume-window grid.
3. `tickets/03-day-class-and-open-location.md` — day class + open-location switch (27 cells, XF p.11 recompute).
4. `tickets/04-am-envelope-grid.md` — EV range, SessionStat 9–12, 1.33 / 1.66, P-zone benchmark, vol features.
5. `tickets/05-cvd-and-smt.md` — CVD variants + SMT.
6. `tickets/06-value-absorption-nodes.md` — value areas, delta profile, key zones, absorption, BigTrades, options nodes.
7. `tickets/07-session-fail-boxes.md` — session-fail boxes vs Jumbo labels.

## Must not change
`sources/`, raw data under `/workspace/data`, `archive/2026-09-pre-reset/`, `planning/phase-1-from-scratch/`. This tree writes only under `planning/phase-1-fable/` (planning) and `trading-research/reports/phase1-fable/` plus the retained artifact store (runs).

## Execution conventions
Registered runner only; approved resource limits only (E0 envelope: CPU 180 s soft / 190 s hard, 4 GiB, 360 s wall per run); MBP-1 work chunked per month into retained per-session tables; failures and budgets retained, never reset; no resumed workers without a new instruction `[trading-research/AGENTS.md]`. No trading, no live deployment, no paid data.

## Definition of done
All ten stories in `PRD.md` pass; the pass command exits 0; `QUESTIONS.md` still lists only closed grids and not-measurable rows (nothing open for the user).

## What Phase 1 does not do
Predict (Phase 2), learn location or P-zones (Phase 3), select a clock, compute P&L, touch account or risk settings.
