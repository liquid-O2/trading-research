# P2-10 — planning/phase-2/tasks/P2-10.md

Attempt `/workspace/.worktrees/phase2-early/implementation/reports/research-work/P2-10/e39e05c1a0029051/attempt-0001`. Native slice on 20 engineering dates (2020-01-02 to 2026-09-03), run through `tools/run_context_experts.py slice`.

## Commands

0. `/workspace/implementation/.venv/bin/python -m pytest tests/context_experts/test_p2_10.py -q -p no:cacheprovider` in `/workspace/.worktrees/phase2-early/implementation` exited 0 in 23.5s (log `pytest.log`).
1. `/workspace/implementation/.venv/bin/python tools/run_context_experts.py slice --run-root reports/research-work/phase2-early/run-2026-09-16/P2-10 --manifest reports/research-work/phase2-early/freeze/ENGINEERING_DATES.json --dates 2020-01-02,2020-03-02,2020-03-13,2020-04-01,2020-06-01,2021-01-04,2021-03-01,2021-04-01,2022-01-03,2022-03-01,2022-04-01,2023-01-03,2023-03-13,2023-11-06,2024-01-02,2024-03-01,2025-01-02,2025-03-03,2026-01-02,2026-09-03 --task P2-10` in `/workspace/.worktrees/phase2-early/implementation` exited 0 in 443.8s (log `slice.log`).
2. `/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt /workspace/.worktrees/phase2-early/implementation/reports/research-work/P2-09/70b4435eca17dab6/attempt-0001/TASK_RECEIPT.json` in `/workspace/.worktrees/phase2-early/implementation` exited 0 in 30.4s (log `predecessor_verify.log`).

## Inspected output

- board QQQ 2020-01-02 at asof_ns 1577977200000000000: model bsm, scenario call_positive_put_negative labelled baseline_proxy_not_known_inventory, n_live 183, n_with_oi 161, spot 215.07, multiplier 100, ATM IV {'index': 169, 'iv': 0.1323457566738129, 'status': 'ok', 'strike': 215.0}.

## Forgery probes

The receipt as issued verifies (control ok=True). 12 of 12 single-gate forgeries are rejected with their intended failure code: remove_artifact -> ARTIFACT_MISSING, substitute_file -> SCHEMA, row_count -> INVENTORY, invalid_json -> JSON_PARSE, plan_digest -> IDENTITY, code_digest -> IDENTITY, run_id -> IDENTITY, omit_owned_file -> INVENTORY, command_log -> ARTIFACT_HASH, predecessor_digest -> PREDECESSOR_HASH, matrix_evidence -> ARTIFACT_HASH, matrix_status -> ACCEPTANCE.

## Limitations

- Boards are built on 20 engineering dates at 10:00 ET, not on the full history.
- The full-chain reference model is the labelled equivalent-European approximation; the American tree is a bounded sensitivity model, not an exact American price.
- The American 400/800 sensitivity runs on one engineering ATM contract, not on OPTIONS.md's sample of 16 contracts per supported American root and engineering date, and no per-cohort 10% Greek-exclusion record is written: the CRR gamma at 400 versus 800 steps differs far more than 10% at these step counts, and no American Greek is consumed by any board or feature.
- Exposure scenarios are assumptions about sign, never known dealer inventory.
- The 1,742-session Level Atlas produced on 2026-09-15 stays under reports/research-work/phase2-early/P2-10 as a descriptive by-product; it is not an artifact of this receipt because it ranks levels over a window that includes the blind hold-out 2026-04-01..2026-09-03, and location work is Phase 3.
- Headline rows whose interval is [value, value] are deterministic identity checks against the contract's literal worked example: the inputs are fixed, so the interval is the value itself and not a sampling interval.
- Nothing here is fitted, tuned, ranked or selected, so the blind hold-out 2026-04-01..2026-09-03 is not consumed; 2026-09-03 appears only as a slice date.

## Result card

**Question.** Do the pricing, Greek and exposure-board primitives reproduce the contract's reference vectors, and do the native boards they build carry their model and scenario labels?

| headline | value | unit | support or interval | note |
| --- | --- | --- | --- | --- |
| ATM European call, S=K=100, sigma=.2, T=1 | 7.965567455405804 | index points | interval [7.965567455405804, 7.965567455405804] | deterministic identity against the OPTIONS.md reference 7.96556746; parity C-P-(S-K) is 0 |
| worst analytic-versus-finite-difference relative error | 1.158454902178182e-07 | relative | support 4 | delta, gamma, vega and vanna at h=.01 and v=.0001; the contract tolerance is 1e-4 |
| American 400 versus 800 step delta relative difference | 2.3045399153515474e-05 | relative | support 1 | one engineering ATM contract, not the contract's 16-per-root-date sample; the exclusion gate is 10% |
| native boards built | 68 | boards | support 80 | 12 of 80 root-days are refused with a named reason |
| median live contracts per NQ board | 1.0 | contracts | support 12 | medians by root: {'ES': 6.0, 'NQ': 1.0, 'QQQ': 883.0, 'SPY': 1125.0}; QQQ and SPY are deep, NQ and ES are degenerate |

**Plausibility.**

- the ATM European call against an independent erf implementation of the BSM formula: observed 7.965567455405804; expected 7.96556746 (plausible)
- board depth matches the quote plane each root actually owns: observed median live contracts {'ES': 6.0, 'NQ': 1.0, 'QQQ': 883.0, 'SPY': 1125.0}; expected hundreds for the QQQ and SPY OPRA chains, single digits for NQ and ES whose only owned quote is a one-minute last-trade mid (plausible)
- the board spot is the last completed minute close before the asof, not the bar that closes after it: observed QQQ 2020-01-02 board spot 215.07; expected 215.07, the close of the 09:59 bar; the 10:00 bar closes 214.92 at 10:01 and must not be used (plausible)

**Target.** Card P2-10 A01-A08: fixture and parity to declared tolerance, finite-difference and American 400/800 sensitivity, .01 vega scaling with explicit units, unavailable rather than invented IV and term brackets, and scenario labels that are assumptions. **Met:** partial.

**Verdict.** needs_upgrade — The primitives match the independent reference vectors to 1e-12 and every board row carries its model, scenario and coverage labels, but the NQ and ES boards built from owned data are degenerate (median live contracts 1.0 and 6.0), and the American 400/800 sensitivity is one engineering contract rather than the contract's per-root-date sample, so the exposure board is only informative for QQQ and SPY today.

**Lever.** Own an option BBO or MBP schema for NQ and ES, then run the American sensitivity on the contract's 16 contracts per supported root and engineering date with the 10% exclusion recorded per cohort. Evidence that it worked: EXPOSURE_BOARDS.depth_by_root would show NQ and ES medians in the tens, and GREEK_SENSITIVITY would carry a per-cohort excluded-Greek record instead of one ATM case.

**Limits.**

- Boards are built on 20 engineering dates at 10:00 ET, not on the full history.
- The full-chain reference model is the labelled equivalent-European approximation; the American tree is a bounded sensitivity model, not an exact American price.
- The American 400/800 sensitivity runs on one engineering ATM contract, not on OPTIONS.md's sample of 16 contracts per supported American root and engineering date, and no per-cohort 10% Greek-exclusion record is written: the CRR gamma at 400 versus 800 steps differs far more than 10% at these step counts, and no American Greek is consumed by any board or feature.
- Exposure scenarios are assumptions about sign, never known dealer inventory.
- The 1,742-session Level Atlas produced on 2026-09-15 stays under reports/research-work/phase2-early/P2-10 as a descriptive by-product; it is not an artifact of this receipt because it ranks levels over a window that includes the blind hold-out 2026-04-01..2026-09-03, and location work is Phase 3.
- Headline rows whose interval is [value, value] are deterministic identity checks against the contract's literal worked example: the inputs are fixed, so the interval is the value itself and not a sampling interval.
- Nothing here is fitted, tuned, ranked or selected, so the blind hold-out 2026-04-01..2026-09-03 is not consumed; 2026-09-03 appears only as a slice date.
