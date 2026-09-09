# 05 — CVD and SMT

**Outcome.** Five CVD constructions and SMT (OHLC 3–4 assets, trade-level NQ, Pine 3/3 matcher) computed on F with divergence / event flags and pairwise agreement. Trade-level CVD is faithful. SMT is not a Green Bird edge.

**Wiki.** `wiki/cvd-variants.md`, `wiki/smt-divergence.md`.

**Definition → compute → pass.**
1. `flow.cvd.trade` from MBP-1 trade events (cross-checked against `cov.nq.trades`), `flow.cvd.ohlc`, `flow.cvd.part.trade` (≥100 / 20–99 / <20), `flow.cvd.part.ohlc`, `flow.cvd.gamma` (declared weight table from ticket 09 nodes; until then the row prints `deferred`).
2. `flow.smt.ohlc.4` on NQ / ES / YM / RTY 1-minute bars, level sets S1 / S2 / S3, lags 1 / 5 / 15; `flow.smt.trade.nq`; `flow.smt.pine.3-3`; `flow.smt.trade.es` printed `not-measurable` in F.
3. Flags per session at the 6–9 edges and at the AM extreme; agreement matrices.
4. Pass command: `... run_phase1_objects.py report --family flow`

**Acceptance criteria.**
- Agreement matrices square with `n` per cell; faithful disagreements counted against `flow.cvd.trade` and `flow.smt.ohlc.4`.
- Pine matcher row present; code-versus-causal disagreements retained as diagnostics.
- SMT event counts printed per level set and lag; class-conditional shares as labels, no predictor.

**Blocked by.** 01 (gamma CVD weights also need 09).
**Out of scope.** SMT as a Green Bird edge; dealer identities.
