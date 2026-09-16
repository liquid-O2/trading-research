# P15-16A JJ-TBR repair round work log

Exit predicate: measured stages, population scan, plausibility gate, 16 inside-tape examples reach location or this log explains why, fixtures for repaired rules, B0/B0.1 byte-identical, deliverables under `_repair_jumbo/`.

## Playbook

Autonomous run. Cursor `/loop` skipped (this session drives the predicate). Opening a PR skipped (no git commands). Architect/how fan-out skipped (cap of three live agents, one code writer, grok-4.6 only).

## Decisions

- Wiki path is `wiki/method-jumbo-tbr.md`, not `method-jumbo-judas.md`.
- TBR p.6 is the NY clock (all times Eastern). The prompt's TBR p.4 citation is indicator settings. Recorded, not a rule change.
- Order-block predicate is O056 / TBR pp.27-28: C2 sweeps C1 and C3 closes beyond C2's opposite extreme (`C3 > H2` long, `C3 < L2` short). The first-round `_three_candle_ob` used `C3 > C2.C`, which could not fail on real data.
- Rejection-block is TBR p.29: rejection wick on the sweep candle, next candle closes beyond it. Always-`None` is retired.
- F11 pass is any of 2m/3m/5m OB or rejection-block, computed from bars at the location. Missing complete windows are unknown, never pass.
- Confirmation searches from the sweep/touch, not only from the reclaim. The 2025-01-28 reclaim at 09:53 is the entry (RR-06); the OB may print between the sweep and the reclaim.
- C2/RB must trade the location. A three-candle structure 30 minutes away is not the source signature.
- RR-02 lives in `scan_b02`. EQ, q1, and q3 are enumerated on both sides. The branch context binds the side. No qualifying context yields no episode. `common.py` already has `R-eq: None`; q1/q3 defaults there are unchanged so B0/B0.1 stay frozen.
- Overnight purge for `single_purged` is an OD stand-in (A2): overnight high > prior RTH high or overnight low < prior RTH low. "All significant overnight liquidity" is not observable on this tape.
- `other_session` trigger is sweep-or-touch of quadrant / box edge / ±0.5 / 1.33-1.66 inside 03:00-06:00. The window is not the trigger. Pass requires a sweep plus F11. At most one pass per side (`first_pass_already_taken`).
- `timed_pzone_reversal` stays fixture-limited. No zone generator.
- Risk and objective stages are omitted after a failed confirmation so the funnel's last shared stage pass equals document `p`.
- `runner.py` imported `directory_listing_digest` from `contracts.identity`, which does not exist in this worktree. Local digest using existing `file_digest`. Documented in MERGE_NOTES. Required to import tests. Not a family rule change.

## Source quotes that bound a choice

- TBR PAGE 12: "EQ or quadrants become our levels of interest" in the extended overnight case; "before 10am"; "after 10am all interest in being in a position is not longer present" for that case only (F08).
- TBR PAGE 12: purged case "anticipate price expanding from the inner range levels (EQ, Quadrants)"; 09:40-09:50 "use it as continuation where i would look to add".
- TBR PAGE 27: "Time frame of execution 2 minutes 3 minutes 5 minutes"; "candle 2 sweeps candle 1 / candle 3 closes above candle 2".
- TBR PAGE 29: "Closure of the candle above the sweep candle confirms the rejection block set up".
- JR p.70: "An astonishing 86.46% of reversal of off the -0.5 stdv (exhaustion)". Histogram share, not a scanner target.
- JR pp.50, 63-64: London box 02:00-03:00, action 03:00-06:00.

## Author-example location misses

Replay file: `_repair_jumbo/REPLAY_jumbo.json`. Tolerance is 2 points. Dates after 2026-08-19 stay `data_unavailable`. No rule was changed to force a hit.

Reached location on the date (episode at a printed level within 2 points, or an explicit tape reason):

| id | reached location | detected | failing operand / tape reason |
|---|---|---|---|
| JJ-2025-01-28 | yes | yes | |
| JJ-2025-05-23-LONDON | no | no | Author bought 21115 at 02:20, during the 02:00-03:00 box build and at prior RTH low / SessionStat 4H, not at a 03:00-06:00 London-box quadrant. RR-04 keeps the action window at 03:00-06:00. Our first long is 21123.5 (8.5 pts from 21115). |
| JJ-2025-09-09 | no | no | Our level 23739.24 is the RR-01 band midpoint. Author printed the far edge 23727. Band width 16.5 pts. Finding, not a rule change. |
| JJ-2025-09-12 | yes | yes | |
| JJ-2025-10-01 | yes | yes | |
| JJ-2025-10-03 | yes | no | confirmation / source_confirmation (no F11 OB/RB at L) |
| JJ-2025-10-06-LONDON | yes | no | author_level prefers L 25052; our episode is q1 25094.6. Location exists. |
| JJ-2025-10-07-LONDON | yes | no | same shape: author L vs our q1/EQ |
| JJ-2025-10-08-LONDON | no | no | L swept at 02:45 inside the formation window, not in 03:00-06:00. Our 03:00-06:00 long is q1 25045.5. Author L 25028. RR-04 window kept. |
| JJ-2025-10-13 | yes | yes | |
| JJ-2025-11-10 | yes | yes | |
| JJ-2025-11-18 | no | no | Our 24394.5 is the RR-01 lower-band midpoint inside the author's printed [24375, 24420]. `_author_level` fell through to L 24660 because the band key is `minus_1_33_1_66_band`. Finding. |
| JJ-2025-12-30 | yes | yes | |
| JJ-2026-01-02 | yes | no | author_level L 25681 vs printed P-zone 25761. Location at the fixture box exists. |
| JJ-2026-01-09 | no | no | Author long is the 25655-25665 9am P-zone (fill 25664.25). `_author_level` prefers L 25710. Our episode is the fixture midpoint 25660, 5 pts from each printed edge (tolerance 2). Rule unchanged. |
| JJ-2026-02-24 | yes | no | entry_outside_window |
| JJ-2026-06-05-LONDON | yes | no | author -1.66 30058 vs our quadrant 30138 |
| JJ-2026-06-09 | no | no | Example levels are BigTrades sizes 219 and 245, not prices. Our short is the 6-9 high 29739.5. No printed price to match. |
| JJ-2026-07-06 | no | no | Our 30076.9 is inside H+[1.33,1.66]W [30065, 30095]. Confirmation failed (source_confirmation). Midpoint is 3.1 pts from 30080, outside the 2-pt tolerance. |
| JJ-2026-07-10 | yes | no | author R_lo 29770 vs our EQ 29829.5. Location exists. |
| JJ-2026-07-16 | no | no | Formation H/L 29561.25 / 29361. Author swept 29525 at 09:30-09:35, which is not the 6-9 high. `judas_outbound` requires a sweep of the frozen edge. No episode. |
| JJ-2026-07-27 | no | no | Open 28590.50 vs prior RTH [28212.5, 28630.75]. Native `prior("day")` has high/low only, no VAL/VAH. Label is inside_value, so `single_extended` emits nothing. Author "below VAH" is unobservable without a prior profile. |
| JJ-2026-07-28 | no | no | Open 27948.75 vs PDL 27939 (not below). VAL missing. Purge_low is true. Selector still requires below_val/below_pdl. No episode. |
| JJ-2026-08-28 and later | n/a | n/a | after tape, data_unavailable |

## Verification round (driver failures 1-4)

- Gate no longer stamps a diagnosis from `bound.page`. Out of bound fails unless `out_of_bound_justification` is a human quote on a different page. `test_mutated_pass_rate_bound_fails_the_gate` copies bounds, sets `[0,0]`, and asserts fail.
- Density killers (not wider bounds): confirmation bars start after the trigger so the sweep is not its own OB; Judas confirmation is hunted 09:40-10:10; rejection-block is 2/3/5-minute with wick > body; rotation is EQ sweep only; London pass needs a box-edge raid and a 3-minute OB (TBR p.27 favourite).
- Every replay miss sets `failing_operand`. After-tape dates return `date outside the tape` before the market is read.
- Restored `_track_jumbo` FUNNEL/REPLAY/RULES to committed bytes. This round writes under `_repair_jumbo/` only.

## Prior RTH value

`_prior_rth` reads `market.prior("day")` range high/low. VAL/VAH are not on that payload, so they go in `unknown`. When VA is missing, open between PDL and PDH is labelled `inside_value`. That is why `internal_rotation` is the common branch on the slice and why 2026-07-27/28 do not emit extended/purged episodes. Inventing a VA would be a generator. Left unknown.
