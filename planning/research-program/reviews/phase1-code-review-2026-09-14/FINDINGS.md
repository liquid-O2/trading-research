# Phase 1 accepted research code — adversarial review findings, 2026-09-14

PHASE 1 ACCEPTED RESEARCH CODE - ADVERSARIAL REVIEW (read-only; no census run)
Repro scripts sit beside this file; run with /workspace/implementation/.venv/bin/python <script>. All import harness.py,
an in-memory HistoricalFeatures over synthetic MBP-1 rows built the way tests/test_phase1_historical_replay.py builds one.
Paths are under implementation/src/trading_research/research/method_pack/.

=============================== PROVEN FINDINGS ===============================

[P1] effort window compares against the wrong predecessor                                              severity: medium
file: historical_flow.py:63-64   previous=chunks[-1] ... opposing>=previous['opposing']
defect: each 5-second effort window is compared with the previous NON-EMPTY chunk, not with its immediately preceding
  equal-duration window (the A2-FLOW wording), so any quiet interval silently changes the comparison baseline.
repro: f7_previous_chunk_skips_empty.py
  observed: quiet +5s window absent -> [(0,10,True),(10,4,False)]; same tape plus one far-from-band print at +5s ->
            [(0,10,True),(5,0,False),(10,4,True)]   (rows are: chunk offset s, opposing volume, effort)
  expected: the +10s window scores the same in both - its true predecessor has opposing=0 either way
affects: flow_stages defense/refresh/thinning and _catalyst_stages - all 11 SIRES local branches, MEMBER-TWO-REASONS
  both sides, KEANI buyer_defense.
census: yes - moves stage selection and therefore pass/fail/unknown counts.
test: test_phase1_historical_replay.py drives local_observations on a dense tape only. WEAKER.

[P2] a zero-length interval is certified as fully observed                                             severity: medium
file: event_time.py:298   range(start//MINUTE*MINUTE, end, MINUTE)   consumed by historical_assembly.py:91-94 absent()
defect: EventWindow.coverage returns observed_scope_complete=True when end<=start (the loop body never runs), so absent()
  answers False - "definitely did not happen" - from zero minutes of evidence. measurement_outcomes.rounded_coverage:53-55
  guards exactly this case; coverage() does not.
repro: f2_absent_empty_interval.py
  observed: coverage(t,t) complete True; absent(m,t,t) False; scan_green_vwap with its 5m breakout on the final bar ->
            continuation_context False -> research_verdict 'fail'
  expected: no observable post-breakout window -> None -> 'unknown'
affects: every absent()/_control_absence/flow_absent whose window collapses at the session end - historical_price_scanners
  :40,171,314 and historical_auction_scanners:98,108,109,158,161,162,168.
census: yes - turns 'unknown' episodes into 'fail', moving f, u and n=p+f.
test: test_phase1_historical_replay.py:288-291 asserts absent() only on a positive-length interval. WEAKER.

[P3] population completeness is measured over the wrong window                                         severity: medium
file: historical_assembly.py:99   coverage=market.coverage(market.at('09:30'), market.end)
defect: window_result measures coverage from 09:30 only, while scanners build references from 18:00 (overnight range,
  Asia/London, prior hour, TBR 06:00-09:00, other-session 20:00/00:00/03:00), so a wholly unobserved formation hour still
  reports a complete population.
repro: f5_population_coverage_scope.py
  observed: 60 unknown minutes inside the Asia formation; whole-window coverage complete False; yet population_complete
            True, population_candidate_count 1, omissions []
  expected: population_complete False and population_candidate_count None - the reference itself is unknown
affects: all 50 branches; this is the Phase 1.5 denominator.
census: yes for population_complete / population_candidate_count; episode counts unchanged.
test: population_complete is asserted only in test_empirical_reporting.py, a different module. ABSENT for window_result.

[P4] sweep-extreme read can abort the branch job                                                       severity: medium
file: historical_price_scanners.py:224-225   path=m.bars(...); max(r['H'] for r in path)
defect: m.bars(trigger.start, confirmation_end) drops bars whose known_at exceeds the aligned 5-minute boundary
  (event_time.py:290). If the sweep bar is the last minute of its block and its members arrive after that boundary, path
  is empty and max()/min() raise instead of recording an availability omission.
repro: f4_green_failure_empty_path.py
  observed: ValueError: max() iterable argument is empty - scan_green_failure aborts
  expected: an availability omission on the branch
affects: GB-FAIL nyam_box, previous_hour, asia_tdo_case, cash_open_reclaim_case, prior_*_level, and mss_fvg_refinement
  through its parent.
census: no - the accepted run completed so it never fired; latent, and it hides a real availability gap.
test: no test builds a late-availability sweep bar. ABSENT.

[P5] observe_outcome never scans the last partial second                                               severity: low
file: historical_outcomes.py:27-32   the spans list has no tail span
defect: candidate crossing seconds come from market.bars(scan_start,end,1), which excludes the bar whose end exceeds
  end_ns, and no tail span is appended; measurement_outcomes.boundary_order:121-123 does append it, so the two accepted
  outcome modules disagree on the same episode whenever decision_at is not second-aligned.
repro: f1_observe_outcome_tail.py
  observed: observe_outcome -> 'no_boundary_in_observed_horizon', resolved_at None; boundary_order on the same episode ->
            'objective_observed' at the target print inside the horizon
  expected: target_observed from both
affects: SIRES, MEMBER, KEANI and REFILL (decision times derived from raw event ns); JJ-TBR/GB/SAINT are minute-aligned.
census: outcome labels only, not episode counts; under-reports first passages.
test: nothing in tests/ imports observe_outcome. ABSENT.

[P6] pivot-less references collapse into one population                                                severity: low
file: historical_flow.py:306   key=tuple(p['id'] for p in ref.get('pivots',[])), side
defect: the per-side dedup key is the reference's pivot-id tuple; KG1 references carry no pivots, so every supplied KG1
  level hashes to ((),side) and only the first is ever scanned.
repro: f3_kg1_reference_collapse.py
  observed: two supplied KG1 levels, both contacted -> 2 episodes, both from 'kg1-a'
  expected: each reference enumerates its own long/short population (up to 4 episodes)
affects: SIRES kg1_retest only.
census: no - the accepted reconstruction uses strategy_options.key_gamma_reference, which returns exactly one level.
test: no scanner-level kg1 test exists. ABSENT.

[P7] closing endpoint inclusive for extrema, exclusive for first passage                               severity: low
file: measurement_outcomes.py:82 (start < event_ns <= end) versus :114-123 (spans cover [start,end))
defect: inside one measure_setup record interval_extrema uses (start,end] - matching OUTCOMES.md - while boundary_order
  scans [start,end), so a print exactly at the horizon end is an excursion that can never be a first passage.
repro: f6_interval_end_mismatch.py
  observed: extrema high 101 with favorable_points 1 (the full target distance) and boundary 'expired_without_observed_boundary'
  expected: one endpoint convention per record
affects: every measured setup; only bites on an exact-nanosecond hit.
census: outcome labels only.
test: test_phase1_measurement.py covers both helpers but never a print at end_ns. WEAKER.

============================= UNPROVEN SUSPICIONS ==============================
historical_price_scanners.py:314 - continuation_context (a breakout-context operand) is rebound with the retest-absence answer, discarding the True set at :308.
historical_flow.py:283-284 and historical_auction_scanners.py:13 - with no balance confirmed by 09:30 a much later balance is adopted with no omission row.
historical_assembly.py:74 - the future-operand guard skips bindings passed known_at=None; historical_price_scanners.py:142-176 and historical_auction_scanners.py:103-112 use them.
measurement_outcomes.py:33-36 - price_origin falls back to episode['trigger']['C'] (for GB-FAIL a sweep close up to 5 minutes earlier) yet reports measurement_start_delay_seconds 0.
historical_auction_scanners.py:97 - all(...) over a possibly empty m.bars read certifies same_boundary_retest_held vacuously True.
event_time.py:289-290 - bars whose known_at exceeds a read's end are dropped with no omission record, in every clock-bounded read.
expressions.py:152 - a CASE whose selector is unknown silently takes ELSE instead of propagating unknown, and the selector's failed list is dropped.
expressions.py:171-175 - OR short-circuits and returns only the satisfied side's fields, so the other side's operands leave selected_fields and the causality check.
historical_flow.py:42 - trades with known_at > chunk end are dropped from that chunk and never picked up by a later one.
historical_features.py:268 - the delta() helper ignores unknown-aggressor volume, unlike _Bar.delta which is None when unknown > 0.
historical_features.py:205-211 - reconstruct mode sets range_scope_complete True from a published prior range while scope_complete stays False.
historical_flow.py:85 - flow_stages can select a pre-touch chunk as defense when touch - effort_seconds < market.start.
empirical_tape.py _profile_payload - the value-area/POC neighbour walk runs on a sparse row list whenever coverage is incomplete, so val/vah can step across untraded ticks.

============================== MODULES NOT REACHED =============================
Read in full: all twelve listed modules, plus historical_assembly, expressions and mbp1_views (_Bar/TradeBars).
Not reached: profiles._poc / _value_area_tie_both internals, strategy_measurements (StrategyWindow, batch_price,
published_prior_range), macro_backfill, native_discovery dispatch, empirical_tape.m09_research_comparison (the REFILL
state machine), adapters.py. Clocks were probed rather than only read: et_ns raises on both the ambiguous and the
nonexistent ET wall time, and the 18:00->16:00 account day is 22h across both 2025 DST transitions - no DST, early-close
or Sunday-open defect found.

================================== VERDICT ====================================
The causal spine is sound: clocks are strict, unknown aggressors and unknown endpoints stay None, references freeze at
known_at, and I found no read of post-decision data - every defect is a boundary or bookkeeping error, not look-ahead.
But P1 and P2 move pass/fail/unknown counts and P3 mis-states the denominator, so the frozen baseline needs versioned
amendments before Phase 1.5 treats it as exact.
