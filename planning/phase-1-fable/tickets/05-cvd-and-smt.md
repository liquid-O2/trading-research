# 05 — CVD variants + SMT

**Outcome.** Five CVD constructions and two SMT constructions computed on F with divergence / event flags at the box edges and a pairwise agreement matrix; trade-level rows are faithful.

**Wiki.** `wiki/cvd-variants.md`, `wiki/smt-divergence.md`.

**Definition → compute → pass.**
1. `flow.cvd.trade` from MBP-1 trade events (cross-checked against `cov.nq.trades`), `flow.cvd.ohlc`, `flow.cvd.part.trade` (≥100 / 20–99 / <20), `flow.cvd.part.ohlc`, `flow.cvd.gamma` (declared weight table from ticket 06's nodes; until then the row prints `deferred`).
2. `flow.smt.ohlc.4` on NQ / ES / YM / RTY 1-minute bars, level sets S1 / S2 / S3, lags 1 / 5 / 15; `flow.smt.trade.nq`; `flow.smt.trade.es` printed `not-measurable` in F.
3. Flags per session at the 6–9 edges and at the AM extreme; agreement matrices.
4. Pass command: `... run_phase1_objects.py report --family flow`

**Acceptance criteria.**
- Agreement matrices square with `n` per cell; faithful disagreements counted against `flow.cvd.trade` and `flow.smt.ohlc.4`.
- SMT event counts printed per level set and lag; class-conditional shares printed as labels, no predictor.

**Blocked by.** 01 (gamma CVD weights also need 06).
**Out of scope.** SMT as a Green Bird edge; dealer identities.
