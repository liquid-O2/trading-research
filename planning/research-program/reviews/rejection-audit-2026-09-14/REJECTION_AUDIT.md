# Rejection audit — are the no-setup rejections genuine? 2026-09-14

PHASE 1 "NO SETUP" REJECTION AUDIT - independent, read-only. SCRATCH =
/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/rejection-audit

METHOD
A. Strategy reconstruction run-1.1.0-r1, evaluation cohort: ALL 258 entry_setup/no_setup episodes from
   jobs/evaluation/<date>/<branch>.json.gz (2020-01-02, 2021-01-04, 2022-01-03, 2024-01-02, 2025-01-02,
   2026-01-02). Every failing conjunct of every episode audited: 690 conjunct instances.
B. Census run-1.0.1: 40 dates evenly spaced over the 1742-session index (2020-01-01..2026-09-03); pool of all
   1644 no_setup episodes there; stratified draw of 196 over all 36 branches with rejections - 2 per branch
   plus a share proportional to that branch's census rejection count (JJ-TBR:other_session 22,
   GB-FAIL:previous_hour 13, SIRES branches 3-7). 527 conjunct instances. records/non-setup-observations.
   jsonl.gz never opened; the census was never run.
Operand checking (1217 instances; 1007 = 83% re-measured, 210 accepted on code reading alone):
 - 402 recomputed arithmetically from published operands/geometry (comparisons, box test, risk/objective).
 - 448 re-derived by re-running flow_stages/_catalyst_stages over the published 5-second local_flow windows
   (SCRATCH/flowsim.py), once as shipped and once with the P1 fix (baseline = immediately preceding window,
   an empty window counting as opposing=0). The simulator reproduced all 3567 recorded `effort` flags exactly.
 - 157 re-measured on a market rebuilt with HistoricalFeatures(day, data_root='/workspace/data',
   records={'strategy_reconstruction':True}) as tests/test_phase1_historical_replay.py builds one
   (SCRATCH/verify_market.py, 6 sessions): every absent()/_control_absence window re-read for length and for
   m.coverage(...)['observed_scope_complete']; plus 20 re-reads of _ob()/the 5-minute confirmation bar and 4
   regenerations of local_observations from the raw MBP-1 tape - all 24 matched the published operands.
Predicates read from /workspace/planning/phase-1-live/FORMULAS.md (M01-M08 bodies, C04, O047), the A2-*
assumption texts in branch_coverage.py, and /workspace/wiki/method-*.md with the linked object pages.

TABLE (conjunct instances, samples A+B combined; SIRES rows roll up the 42 stage names)
| family    | failing conjunct                       |   n | genuine | mis | amb | attributable |
| GB-FAIL   | confirm_close vs reference_px          |  93 |     93 |  0 |  0 | -    |
| GB-FAIL   | box_return_ok                          |  88 |     88 |  0 |  0 | -    |
| GB-FAIL   | NOT tdo_required + source_tdo_close_cnf|  28 |     28 |  0 |  0 | -    |
| GB-FAIL   | source_hold_confirmed + objective_fixed|  13 |     13 |  0 |  0 | -    |
| GB-VWAP   | continuation_context                   |   3 |      0 |  3 |  0 | D1=3 |
| JJ-TBR    | source_confirmation + reaction_side_cnf| 128 |    128 |  0 |  0 | -    |
| JJ-TBR    | risk_defined                           |  41 |     41 |  0 |  0 | -    |
| JJ-TBR    | context/objective geometry (6 names)   |  20 |     20 |  0 |  0 | -    |
| KEANI     | absence-propagated stages (6 names)    |  58 |     58 |  0 |  0 | -    |
| KEANI     | a_low > prior_vah                      |   7 |      7 |  0 |  0 | -    |
| MEMBER    | buyers_absorb_and_hold / resist_reject |  12 |     12 |  0 |  0 | -    |
| SAINT-AMT | control_evidence_recorded              |  21 |      4 | 17 |  0 | P2=17|
| SAINT-AMT | same_boundary_retest_held              |  17 |     17 |  0 |  0 | -    |
| SAINT-AMT | objective_fixed                        |  16 |     16 |  0 |  0 | -    |
| SAINT-AMT | original_balance_reaccepted            |  10 |     10 |  0 |  0 | -    |
| SAINT-AMT | local_control_confirms_return          |   9 |      2 |  7 |  0 | P2=7 |
| SAINT-AMT | older_value_tested / older_value_reject|  14 |     14 |  0 |  0 | -    |
| SAINT-AMT | repeated_body_sell + repeated_aggression|   6 |      0 |  6 |  0 | P2=6 |
| SAINT-AMT | other measured operands (5 names)      |  19 |     19 |  0 |  0 | -    |
| SIRES     | flow stage absent / stage attribute    | 376 |    376 |  0 |  0 | P1=0 |
| SIRES     | thesis_alive / risk_defined / obj_fixed| 137 |    137 |  0 |  0 | -    |
| SIRES     | own-delta (CVD) filters (6 names)      |  60 |     60 |  0 |  0 | -    |
| SIRES     | footprint candle / gamma / microbalance|  41 |     41 |  0 |  0 | -    |
| TOTAL     |                                        |1217 |   1184 | 33 |  0 | P1=0 P2=30 P3=0 D1=3 |
By sample: A 690 = 675 genuine + 15 mis (all P2); B 527 = 509 + 18 (15 P2, 3 D1).
Episode level: A 258/258 rejected by >=1 verified conjunct (0 artifacts; 9 episodes also cite a vacuous
conjunct). B 193/196 genuine, 3 artifacts (all GB-VWAP).

MIS-IMPLEMENTED EXAMPLES
[P2] zero-length interval certified as fully observed - event_time.py:298 via historical_assembly.py:93, with
 an explicit twin at historical_auction_scanners.py:28 (`if end<=after:return False`).
 2021-01-04, SAINT-AMT:continuation_retest, short, decision 1609774260000000000. Recorded operands:
 control_search_window [1609774260000000000, 1609774260000000000] (length 0), control_evidence_recorded=False,
 repeated_aggression_in_trade_direction=False, confirm_at=null, retest_at=null.
 Code: no same-boundary retest existed, so control_start was set to the window end; _control_absence saw
 end<=after and returned False - "two successive directional body/delta closes definitely did not occur" -
 having read zero bars. On the rebuilt market m.coverage(t,t).observed_scope_complete=True and absent(m,t,t)
 =False, so the generic absent() path yields the same vacuous False.
 Predicate: A2-AUCTION-SAMPLE defines control as two successive directional body+delta closes; FORMULAS C04
 forbids COALESCE(missing,false). With no observation window the answer must be unknown.
 Repro: .venv/bin/python SCRATCH/repro_p2_saint.py. Decisive in 4 of the 1644 pool episodes
 2026-05-01 continuation_retest long, 2026-07-02 poc_traversal short): there every other operand is unknown,
 so repaired code reports data_unavailable, not no_setup. In the other 26 instances the episode is
 independently rejected by a conjunct measured over a positive, fully observed window.
[D1] GB-VWAP continuation_context is overwritten with the answer to a different question -
 historical_price_scanners.py:308 binds it, :314 rebinds it (listed as an unproven suspicion in the
 2026-09-14 review; proven here on production data).
 2023-12-08, GB-VWAP:source_long, long, decision 1702051500000000000. Recorded operands: breakout_close
 16044.5, asia_high 16029.0, london_high 16029.0, retest_at null, continuation_context False - the only
 failing conjunct. Code: line 308 computed breakout.C > max(asia.high, london.high) = True; with no VWAP
 retest found, line 314 rebound the same field to absent(breakout.end, deadline) = False, discarding the True.
 Predicate: M03 continuation_context IS the close above both finished highs; a missing retest belongs in
 retest_at/retest_low/retest_high, which are already null, so sequence_ok is NULL and C04 gives 'unknown'.
 Repro: .venv/bin/python SCRATCH/repro_d1.py. All 17 GB-VWAP rejections in the 40-date pool fail on
 continuation_context and nothing else.
[P1] effort baseline, historical_flow.py:63-64 - NOT attributable to any sampled rejection. All 149 sampled
 episodes with a published local_flow have contiguous 5-second windows (3567 of them, zero empty), so
 chunks[-1] is always the immediately preceding window; re-running the stage selectors with the corrected
 baseline changed no stage in any episode. The defect is real in code but inert on this tape at these bands.
[P3] historical_assembly.py:99 - 0 attributable. It moves population_complete and population_candidate_count
 only; episode classification never reads them. Not audited further here.

AMBIGUOUS CAUSES
No sampled rejection had to be left ambiguous, but residual uncertainty is of three kinds.
 - 210/1217 conjunct instances (17%) were accepted on code reading plus the published operand rather than
   re-measured: JJ-TBR source_confirmation where the O056 recipe returned confirmed=False (47), GB-FAIL tdo
   operands (28), SIRES footprint candle operands (23), KEANI absence stages on un-rebuilt sessions (26).
 - Unknown-aggressor volume: no sampled 5-second window had unknown>0, so no SIRES/MEMBER conjunct took the
   flow_absent -> None path. Episodes where it does are classified data_unavailable and are out of scope.
 - Tie-batch ordering and review defects P4-P7 were not exercised: P4 never fired in the accepted run,
   P5-P7 touch outcome labels rather than setup verdicts.
Two spec divergences, zero effect here: GB-FAIL treats prior_day/week/month levels as boxes, gating
box_return_ok instead of the identity true FORMULAS.md:372 prescribes for a single line (never failed
alone there); KEANI reports time_of_day_allowed=False when there is no imbalance break at all.

ESTIMATE OF THE SHARE OF REJECTIONS THAT ARE ARTIFACTS
Sample A (all 258 audited): 0% artifacts (0/258; one-sided 95% bound ~1.2%). 3.5% of rejections (9/258) name
at least one vacuously-false conjunct beside a real one. 2.2% of conjunct instances (15/690) are P2.
Sample B: 1.5% of the audited draw (3/196) and 1.28% of the 40-date pool (21/1644 = 17 GB-VWAP D1 + 4 SAINT
P2) would stop being rejections under repaired code - becoming data_unavailable, not setups. Extrapolating by
branch to the whole census (GB-VWAP 619 rejections, effectively all D1; SAINT 8459 at the pool's 2.1% rate)
gives about 1.1% of the 72,387 census rejections, roughly 800 episodes, concentrated in GB-VWAP.
Not checked: the 17% of conjuncts accepted on code reading; whether any *setup* should have been a rejection
(only rejections were audited); outcome labels; population_complete/candidate_count, which P3 does corrupt;
and any session outside the 6 reconstruction dates and the 40 census dates.

VERDICT
The rejections are overwhelmingly genuine: all 258 reconstruction rejections and 193 of 196 sampled census
rejections rest on at least one conjunct re-measured as false over a positive, fully observed window, and the
two defects the skepticism centred on (P1, P3) move nothing here.
Exposure is narrow: about 1% of census rejections - all of GB-VWAP plus ~2% of SAINT - are unknowns
mislabelled as rejections, and 3-4% cite a vacuously-false reason, so failed_conditions is less trustworthy
than the verdict itself.
