# 04 — EV range, extensions, P-zone, SessionStat, vol

**Outcome.** Every envelope and target object prints reach, overshoot, reject, time-to-touch, in/out-of-value and calibration on F. EV, SessionStat, 1.33/1.66 and P-zone stay distinct.

**Wiki.** `wiki/ev-range-expected-move.md`, `wiki/sessionstat-9-12-envelope.md`, `wiki/extensions-1-33-1-66.md`, `wiki/p-zones-benchmark.md`, `wiki/vol-estimators.md`.

**Definition → compute → pass.**
1. Vol features `vol.*` per session; terciles frozen on F.
2. EV rows: `env.ev.{mean60, median60, p75, p90, rv20, gk20, yz20, har, iv, vix16}` × `ref.{0930open,0900open,eq69,0900close,tdo}`; each with its own midpoint id, not EQ69.
3. SessionStat `env.ss.{avgHL60, medHL60, minavg60}` (minimum-average is a named approximation).
4. Extensions `env.ext.{133,166,100,050}` **beyond-edge** and **range-origin**, 6–9 and London box.
5. P-zone `pz.approx.A` = 500-session nearest-rank 50/75/90/95/99 bands (T1–T4 labels are approximation tiers); `pz.approx.B`; upgrades history-60, vol-scaled, volume-filter, VP-node-snap. `pz.learned` = `deferred`.
6. VWAP comparison row `env.vwap.rth.sd2`.
7. Pass command: `... run_phase1_objects.py report --family env --family vol`

**Acceptance criteria.**
- Every row prints `n`, reach, overshoot, reject, time-to-touch p50, in/out-of-value share, calibration share ± interval.
- EV / SessionStat / extension / P-zone ids never share a family primary key.
- `pz.approx.A` history count printed (500 or warmup n).
- `faithful disagreements` against `env.ev.mean60`, `env.ss.avgHL60`, `env.ext.133.from-edge`, `pz.approx.A`.

**Blocked by.** 01.
**Out of scope.** Forward-vol product; learned P-zones.
