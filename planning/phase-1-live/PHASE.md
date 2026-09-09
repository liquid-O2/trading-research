# PHASE 1 — measurement and comparison of objects

## One outcome
Every object family in `wiki/index.md` is measured on frozen slice F (NY trade dates 2024-01-02 → 2026-08-31) with a faithful source object and named upgrades, and the pass command prints one line per variant.

## One pass command
```
/tmp/trading-research-venv/bin/python trading-research/tools/run_phase1_objects.py report
```
Prints, one row per family × variant, in this order of families (range, path, open, env, vol, flow, value, fail, gap, block, tpo, options):

```
family | variant | n | faithful disagreements | experiment status | report path
range  | range.6-9.published | <n> | 0 | measured | trading-research/reports/phase1-live/range/range.6-9.published.json
...
```
Exit code 0 only when every family has at least one `measured` row and no row lacks a report path. `experiment status` ∈ {measured, null, worse, better, deferred, not-measurable}; definitions in `SPEC.md` §6. Per-family runs: `report --family <f>`.

## Ticket spine (thin vertical slices, in order)
1. `tickets/01-6-9-and-path.md` — runner, frozen slice, grid, faithful 6–9 + path + both width tables.
2. `tickets/02-clocks-bars-windows.md` — 5–9 family, Jumbo London TBR, Asia TBR, GB clocks, vol/dollar/trade bars, 9:40–9:50 vs first 20 min.
3. `tickets/03-day-class-and-open-switch.md` — Judas / extended / purged + 27-cell open switch + in-value vs in-range + split 76% claim.
4. `tickets/04-ev-extensions-p-zone.md` — EV estimator grid, SessionStat 9–12, 1.33/1.66 both coordinates, P-zone 500-session disclosed approx, vol features.
5. `tickets/05-cvd-and-smt.md` — five CVD constructions + SMT (trade NQ, OHLC 3–4, Pine matcher).
6. `tickets/06-value-absorption-options.md` — VP / delta / key zones / absorption / BigTrades / footprint / on-touch refill / VWAP ±2SD.
7. `tickets/07-session-fail-boxes.md` — GB fail-boxes vs Jumbo labels; A+ = sweep happened.
8. `tickets/08-fvg-cisd-tpo.md` — FVG/body gaps, CISD/rejection blocks, TPO + AMT labels (not inside 07).
9. `tickets/09-options-nodes.md` — options-only: native nodes on NDX, NDXP, SPX, SPXW.

## Must not change
`sources/`, raw data under `/workspace/data`, `archive/`, `planning/phase-1-from-scratch/`, `planning/phase-1-fable/`. This tree writes only under `planning/phase-1-live/` (planning) and `trading-research/reports/phase1-live/` plus the retained artifact store (runs).

## Execution conventions
Registered runner only; approved resource limits only (E0 envelope: CPU 180 s soft / 190 s hard, 4 GiB, 360 s wall per run); MBP-1 work chunked per month into retained per-session tables; failures and budgets retained, never reset; no resumed workers without a new instruction. No trading, no live deployment, no paid data.

This file is the planning stop. It does not start the runner, workers, or any measurement.

## Definition of done
All stories in `PRD.md` pass; the pass command exits 0; `QUESTIONS_RESOLVED.md` lists only closed grids and not-measurable rows.

## What Phase 1 does not do
Predict (Phase 2), learn location or P-zones (Phase 3), select a clock, compute P&L, touch account or risk settings.
