# Phase 1.5, rebuilt on the source-faithful scanners (2026-09-17)

Owner: Fable (main thread). This file is an addition to the pack, not an edit of a pinned plan file; it re-aims subphases 05 to 07 at the rebuilt B0.3 scanners and records the decisions the user delegated on 2026-09-17 ("you are free to make upgrades to our plan or our processes"). The scientific rules of [SEARCH_CONTRACT.md](SEARCH_CONTRACT.md), [EVALUATION.md](/workspace/planning/research-program/EVALUATION.md) and [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md) stay in force: one declared axis per candidate, chronological outer folds with inner tuning, density-matched controls, multiplicity control, failure attribution on every deselected candidate, a trial ledger, nothing from the future.

## Why the earlier subphase-05 results are void

P15-17 attempt-0005, P15-18 attempt-0002 and P15-19 definitive-0002 ran on scanners the source audit later failed (AUDIT_S1: every Sequence-bank entry dated before its admitting evidence; the +25.78/day candidate was 10,325 entries against a 19-entry baseline). The rebuilt scanners reproduce the authors' dated tickets (fidelity-round8 REPORT: Jumbo 23 of 24 plus the documented 06-05 range, Green Bird 16 of 16, Sires 19 of 19 and Saint 1 of 1 on drawn levels, Member 2 of 2 on the ES tape) and are the only baseline a comparison may use. Their receipts are superseded, not amended.

## The baseline and the guard

- **B0.3** is the rebuilt scanner of each family with the authors' own selection rules (the candidate list) and the executed list (one position at a time, adds, flips) as the traded list.
- **Fidelity pin.** `implementation/tools/fidelity_guard.py` re-runs every family's ticket replay and compares each ticket's flag with `FIDELITY_PIN.json`. A change that loses a pinned ticket does not merge, whichever family it was meant for. Every candidate below also reports its recall of the pinned tickets; a candidate that drops tickets is an *upgrade candidate that departs from the source* and is labelled so, never silently promoted.
- **Population baseline.** Each family's executed list over the frozen session list (P15-00, n = 1,742; Sires, Saint and Member on the generated-level population once that runner exists) gives the reference distributions: net points a session, win rate, R at target, frequency, and the day-read strata.

## What is searched

Two kinds of candidate, because they cost differently:

1. **Rescan candidates** change how the scanner reads the tape (one axis each). They need a population rescan (about 20 minutes a family on 10 workers). Kept to the source's open parameters:
   - Timing: Judas window ±15 minutes and the no-clock variant (T1, T2, T4); Green Bird previous-hour start 10:00 / 11:00 / 12:00; Asia box from midnight / from 20:00.
   - Formation: the 6-9 box against 06:30-09:30 and 07:00-09:00 (F1-F3 as applicable); the 9-10 box against the developing box (his documented mistake as a negative control).
   - Sequence: confirmation modes as a set (next-bar open, rejection close, signature close, at-level limit with inside limit 2 / 5 / 8 points); failure margin 1 / 2 / 4 points.
   - Memory: cycle caps 1 / 2 / 4 at a line; carried-in boxes consumed or kept (Sires).
   - Reference (Sires, Saint, Member): adaptive size cut 0.99 / 0.995 / 0.998, floor 10 / 20 / 40, band 4 / 6 / 8 points, absorption on or off.
2. **Offline candidates** change what is done with the candidate list and need no rescan; they are evaluated from the recorded candidate rows and the bars:
   - Selection: round trips a segment 1 / 2 / 3 / 6, one entry a line, primary play only, edge first or time order, adds off / same line / any line, flips off / on.
   - Exits (P15-19, E0-E4): fixed structural target, next drawn level, trail behind confirmed swing, time stop at the session's deadline, break-even after 1R.
   - Regime conditioning (the user's "ranges by regime"): every offline candidate is also evaluated per stratum of the day read (Jumbo classification and range bin; Green Bird day model and overnight bias; Sires session type) and a stratum-conditional policy is one further candidate per family. A conditional policy is fitted on the fit fold only.

The breadth stays inside the contract: at most 24 rescan candidates a family and at most 40 offline candidates a family, each with one declared axis; refinement neighbourhoods and one combination as the contract states.

## How a candidate is judged

- Outer folds by calendar year (2020 to 2026 gives five test folds after a two-year fit); inner tuning on the fit fold only.
- Primary score: daily net points of the executed list on the test fold, with the bootstrap interval of the amended stage-B evaluation (20,000 draws, attainable Holm floor published, support gate on both sides).
- Constraints reported beside the score: pinned-ticket recall, frequency floor, delay distribution, stratum breakdown.
- Failure attribution on every deselected candidate from the contract's list (frequency, location_miss, confirmation_miss, adverse_cost, multiplicity, inconclusive_support).
- Density-matched controls for every reference-changing candidate.

## Order of work

1. Merge the fidelity branch; pin the tickets; keep the guard in every merge.
2. Population baselines: Jumbo and Green Bird exist (`population-round8c`); build the generated-level population runner for Sires, Saint and Member (order-level boxes carried across sessions; the ES market for Member).
3. Offline candidates first (cheap, many): selection and exits on the recorded candidate rows, then regime conditioning.
4. Rescan candidates (expensive, few): one queue on the machine, sequential jobs, each writing its own run root; worktrees separate the code of each family so a change to one scanner cannot touch another.
5. Refinement and the single combination per family; the trial ledger; P15-20 release with the fidelity pin as part of the release evidence.

## Order across phases (2026-09-17, 20:30)

The first grading fit and the population baselines settle the order: the executed lists of all three families are the admitted pool traded blindly (Jumbo +68, Green Bird +3.5, Sires +4.7 points a session before costs, at 6 to 17 trades a session), and no cap or ordering of the pool recovers the authors' one to three trades. What separates their trades from the pool is what they read beside the level: the volume profile and its nodes, the delta at the level, the aggression at the level, the memory of the level, the room to the next major level. Those are the Phase 3 objects. So Phase 3 is built alongside the Phase 1.5 queue, not after Phase 2, and Phase 2 is fitted on it:

1. Phase 1.5 rescan and selection candidates run as an unattended queue and are judged by the fold tool; results land in the report as they finish.
2. The shared object layer (`implementation/tools/grading_features.py`): profiles and nodes (from the framework's own profile payloads), delta (footprints), aggression boxes (the box table, done), memory, location, room. It serves every family the same way, so an object one author uses is tested as a confluence filter or a grading feature for another (the user's request of 2026-09-17: Jumbo and Green Bird read profiles and delta for their levels too).
3. Grading (Phase 2) is re-fitted on the object layer per family, at the authors' density, leave-one-day-out; the ticket recall at density is the number that says whether the object layer holds what they grade on.
4. Cross-strategy candidates are one declared axis ("confluence"): a family's entry gated by another family's object (an aggression box at the Judas sweep, a prior-day node at the Green Bird box), evaluated exactly like any other candidate, with recall reported beside the score.

## Phase 2, re-aimed

Phase 2 is the grading layer: what makes the author take one of the ten to forty admitted opportunities. The first fit (fidelity-round8 REPORT section 11) shows the levels-and-time features carry part of Jumbo's choice and none of Green Bird's; the next feature families are the Refill decomposition (memory, construction, location, flow) computed at order level, and the Phase 3 level objects (profiles, delta bands, aggression clusters). Phase 2 experts are fitted per fold and compared against the same executed-list baseline, at the author's density.
