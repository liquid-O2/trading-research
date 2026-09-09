# 04 — AM envelope grid (EV range, SessionStat 9–12, 1.33 / 1.66, P-zone benchmark, vol features)

**Outcome.** Every envelope and target object prints reach, overshoot, reject, time-to-touch, in/out-of-value and calibration on F, with vol features attached as columns.

**Wiki.** `wiki/ev-range-expected-move.md`, `wiki/sessionstat-9-12-envelope.md`, `wiki/extensions-1-33-1-66.md`, `wiki/p-zones-benchmark.md`, `wiki/vol-estimators.md`.

**Definition → compute → pass.**
1. Vol features `vol.*` per session (daily OHLC 18:00–17:00; 1-minute RV; ATM IV and skew from NDX quote-1m or NQ.OPT bars at 09:25; VX slope); terciles frozen on F.
2. EV rows: `env.ev.{mean60, median60, p75, p90, rv20, gk20, yz20, har, iv, vix16}` × `ref.{0930open, eq69, 0900close, tdo}`; each with its own midpoint id.
3. SessionStat rows `env.ss.{avgHL60, medHL60, minavg60}` and projections; extension rows `env.ext.{133,166,100,050}` from edge and from EQ, 6–9 and London box; P-zone `pz.approx.A` and `pz.approx.B`; `env.vwap.sd2` comparison row.
4. Outcomes per grid; calibration share with Wilson interval; coincidence counts between rows; closest-object ranking at the AM extreme.
5. Pass command: `... run_phase1_objects.py report --family env --family vol`

**Acceptance criteria.**
- Every row prints `n`, reach, overshoot, reject, time-to-touch p50, in/out-of-value share, calibration share ± interval.
- `pz.learned` row printed as `deferred`.
- `faithful disagreements` counted against `env.ev.mean60` (EV rows), `env.ss.avgHL60` (SS rows), `env.ext.133.from-edge` (extension rows), `pz.approx.A` (P-zone rows).

**Blocked by.** 01.
**Out of scope.** A forward-vol product; learned P-zones.
