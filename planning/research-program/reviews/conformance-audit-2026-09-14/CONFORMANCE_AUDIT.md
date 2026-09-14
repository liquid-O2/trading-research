# Method conformance audit — twelve methods, stage by stage against their sources, 2026-09-14

METHOD CONFORMANCE AUDIT - twelve methods vs their cited sources and the frozen run-1.0.1 method_pack. Read-only.
261 per-branch/per-stage rows in rows.jsonl; reproductions f1..f7 here (harness.py = frozen HistoricalFeatures,
pattern of tests/test_phase1_historical_replay.py). Classes: exact | operational (qualitative source, labelled threshold)
| inferred (no source statement) | mismatch (code contradicts the print) | missing (absent, not recorded as skipped).
Reused, not re-proved: reviews/phase1-code-review-2026-09-14 (P1-P7, D1 GB-VWAP, D2 seams). Columns: branch | stage |
anchor | code | class. price=historical_price_scanners, auct=historical_auction_scanners, flow=historical_flow,
proc=historical_process_scanners, ctx=strategy_context.
== JJ-TBR (8 entry branches + management) ==
all | freeze 6-9 range | TBR p.7 "6:00am - 9:00am" | price:46 formations + m.range span | exact
judas_outbound | entry, exit window | TBR p.8 "position ourselves right at the open" / "positions closed as we reach the reversal window" | price:99-113 the 09:30:00-01 execution batch; :145 exit_window_recorded literal True | exact / missing
judas_reversal | edge sweep | TBR p.8 "judas trades from 9:30 to the reversal window" | price:71,89 sweep searched only 09:40-09:50 | mismatch C1
judas_reversal | confirmation | TBR pp.27-31 OB / rejection block / absorption | price:26-40 one 180s O056 triple only | operational
single_*, rotation | entry level | TBR p.12 "the EQ or quadrants" | price:82 EQ only; A2-TBR-PROJ internal=[.25,.5,.75] unread | missing C5
single_*, rotation, extension | action window | TBR p.12 "after 10am all interest ... is not longer present" | price:72 action_end=16:00 | mismatch C2
extension_reaction | 1.33-1.66 band | TBR pp.20-21 | price:85 [low-.66W,low-.33W] = 1.33-1.66 of the parent width | exact
other_session | seven clocks / source case | TBR p.7 list; p.36 | price:49-52 identical seven; :176 both operands literal True | exact / mismatch C7
timed_pzone_reversal | zone | JR pp.16-18,53-55 | supplied P-zone absent; strategy_pzones v1 substitute, labelled | inferred
== GB-FAIL (7 sweep branches + mss_fvg_refinement) ==
all 7 | reference, sweep | GB pp.23,27,33,40; p.31 "sweep -> reclaim -> opposing liquidity" | price:189-217 box/hour/asia/prior D-W-M/cash open, then strict first breach + exact contact | exact
all 7 | five-minute reclaim | GB p.25 "I wait for the 5 min close back below the PDL" | price:219-223 only the sweep's own candle | mismatch C3
all 7 | contextual bias | GB pp.23,38-40 directional read | price:230 availability of a 06:00 range; no side term | mismatch C7
all 7 | objective / invalidation | GB pp.25,30-39 opposing liquidity, stop above PDL | price:227-228 sweep extreme +/-1 tick; opposite edge | operational
nyam_box | golden pocket, retracement entry | GB p.25 "50%-61.8% fib ... golden pocket" | price:242 both flags literal False | missing
asia_tdo_case | TDO | GB pp.27,32-39 midnight open | price:233-241 O of the 00:00 bar, signed close test | exact
mss_fvg_refinement | annotation | GB p.31 post 1991589280142315537 | price:256-279 three aligned 2-min candles, 30-min horizon | operational
== GB-VWAP (source_long) ==
break of both highs | GB p.33 "Broke & closed above London + Asia highs" | price:288 first 5-min close above the max | exact
session clocks / VWAP return | GB p.33 (London bounds unpublished) | price:283 asia 20:00-00:00, london 02:00-05:00; :293-300 60-min horizon | operational
continuation_context | GB p.33 | price:308 True then :314 rebound to the retest-absence answer | mismatch D1
vwap_reset_verified | wiki: the author-faithful gate | price:309 literal True | mismatch C7
== GB-SCALP (2 case branches + automatic_admission) ==
both | direction, pullback | GB p.40 posts | proc:60-71 one 1-min pivot pair, first_contact on the premium/discount half | inferred
both | entry trigger | GB p.40 - not published | proc:84 None; automatic_admission returns a literal NULL omission | missing (skipped)
both | size / management | GB p.40 | supplied scalp_process absent; both fields in POLICY EXCLUDED | missing (skipped)
== SIRES (11 flow branches, microbalance_break, 3 process units) ==
all | thesis and death | C1 pp.3-6 | flow:128 thesis_alive = sign(entry-stop)>0; no recorded death consumed | inferred
all | location | ABS p.7 "real extremes: shelves, ledges, low volume nodes, minor volume nodes" | flow:283,308 today's pivot-balance edge; O066-O069/O116 unreferenced | mismatch C7
all | invalidation, objective | ANAT pp.8-10 | flow:157-159 band edge +/-1 tick; opposite balance edge | operational
stop_four_stage | replenishment | STOP p.10 "minimum filter is three ticks of replenishment" | flow:88 any add + held; no tick test anywhere | missing
stop_four_stage | lift-off, -4R stop | STOP pp.10-14 "two upticks ... two to four" | flow:98 2Q<=move<=4Q; supplied account absent | exact / missing (skipped)
absorption_reward_retest | reward, fresh retest | ABS pp.5-13 three-tick neighbourhood | flow:92-96,173 3-tick reward then renewed defence | exact
ofm_passive | dying tape, 1R-3R target | OFM p.14 "the speed of tape just dies" | flow:221 count < 0.5x release; no objective bound | inferred / missing
ofm_aggressive, balance_fade | gamma regime | BIG pp.14-18; GEX pp.4-20 | supplied gamma absent; strategy_options BS model substitute | inferred
footprint_confirmed_reaction | intrabar POC flip | FP9 pp.4-7 | flow:191-197 two snapshots (+30s, close) of the max-volume price | inferred
defended_band_continuation | aggression vs thesis | CONT pp.4-10 (two conditions) | flow:241 both bound to the same own_delta | mismatch C7
microbalance_break | thesis direction | K2345 pp.4-7 "within the established directional auction" | flow:337 selects it, :346 restates it | mismatch C5
kg1_retest | retest | NYAM pp.8-9 | flow:244 kg1_retest literal True; level from an inferred key-gamma model | mismatch C7
== SAINT-AMT (4 branches) ==
all | HTF balance | RTVP pp.3-11 "redraw the balance until it fits the market" | auct:10-13 latest pivot-balance known by 09:30 | operational
all | profile permission | RTVP pp.3-11 "an unbalanced trending profile is left alone" | auct:46 POC inside the balance - always true | mismatch C7
all | arrival read, HTF/LTF alignment | AMTL pp.5-10 arrival/delta/effort; WIC p.10 "alignment ... is the whole method" | auct:49 literal True (nothing observed); :51 True whenever control exists, HTF read never computed | missing / mismatch C7
all | confirmation, objective | TRAP pp.6-12; RTVP pp.5-8 | auct:16-22 two same-sign body+delta bars; :152 far balance edge only | operational
failed_auction_return | tried and rejected, reacceptance | AMTL p.8 "reaches that lower area and rejects it" | auct:141-146 older VA contact, close beyond, close inside | exact
poc_traversal | POC passage, hold | AMTL p.9 "buyers push aggressively through POC" | auct:148,167 close beyond POC with same-sign delta | exact
== MEMBER-TWO-REASONS (2 branches) ==
both | prior reaction area, minor HVN | K10 p.7 "two independent reasons pointing at the same price" | auct:185-206 prior-session pivots (>=4 ticks) + local volume max within 2 ticks | operational
both | invalidation, objective | K10 p.7 "stop above the high of the rejection, target set at 1.5R" | auct:225-227 flow extreme +/-1 tick; 1.5R | exact
short / long | rejection, second tap | K10 pp.6-8 "short on the resistance rejection" / "the return/second tap" | auct:222 the flow "reward" stage; :213 the first distinct contact of the session | operational
== KEANI-OPEN-ABOVE-VALUE (source_long) ==
A above prior value | AVG p.21 "A period sitting clear of the prior value area high" | auct:286 a_low vs prior VAH in the predicate | exact
rejection | AVG p.21 "reject off the POC or the previous day's value area high" | auct:259 wick into the DEVELOPING value-area LOW | mismatch C4
imbalance break, defended retest | AVG p.21 "aggressive buying imbalances ... if the buyers defend them" | auct:261-278 O109 3-row diagonal stack ratio 3; same-band flow defence | operational / exact
time of day | AVG p.21 "waits until around 10:00" | A2-KEANI-TIME A=09:30-10:00, break by 11:00 | operational
== REFILL-STUDY (touch_record + 2 supplied units) ==
touch_record | formation, departure, return, pre-touch memory | REF pp.5-9 "freeze memory ... before this touch resolves" | proc:25-46 A2-REFILL 100 lots / 2 events / 120s / 4-tick departure; :42 only prior resolved touches | operational / exact
touch_record | definition, thesis, label discipline | REF pp.5-9 | proc:38-43 four predicate conjuncts are literal True | missing
touch_record / supplied | grader, 12/32/96/30-min config | REF pp.8-9,12,16 | EXTERNAL[selection]; no supplied order record | missing (skipped)
== JETBUNDLE-STATES (B, A, D, E, W + transition) ==
all | observation scope | MATH pp.4-6 provide / withdraw / consume | proc:175 one fixed 09:30-09:32 window per session | inferred
all | state assignment | MATH pp.9-10 | supplied labels absent; ctx:46-69 classifier only under reconstruction | inferred
B | criteria | MATH p.9 "two-sided executions and frequent, recent revisits, low aggression on both sides" | ctx:67 the same three tests | exact
A, D, E, W | criteria | MATH pp.6-11 | ctx:55-66 1.5x effort, efficiency<=0.2 / >=0.6, adverse<=2 ticks, adds<=0.25x prior, depth-one removals less executions > adds+volume | inferred
== STOIC-DATA (process_review, macro_application) ==
process_review | frozen spec, uniform sample, winner/loser | DATA pp.3-4 | proc:152-158 needs a record never supplied; 0 episodes | missing
macro_application | vintages, standardization | DATA pp.5-6 | proc:109-129 CPI/PAYEMS initial releases, 12-prior O160 | operational
macro_application | C-score, cycle, trend | DATA pp.5-6 "custom C-scores ... macro cycle" | proc:165 operand True via a 2-series z composite substitute | mismatch C7
== STOIC-RISK (first, second, reset_after_second_win) ==
all | eligibility | DATA p.8 "100+ sample, win rate, R:R, Monte Carlo, base <= 1%" | proc:226-237 supplied ledger never present | missing (skipped)
all | printed ladder | DATA p.7 "Risk 1% at 1 to 3" / "4% total ... plus 12%" / "reset to 1%" | proc:240-242 1/3, 4/12, reset 1 | exact
first | activation rule | DATA p.7 "only activates on a two trade winning streak" vs the ladder | discrepancy preserved, not resolved | operational

MISMATCHES
C1 JJ-TBR judas_reversal sweep clock. TBR p.8 "the judas trades from 9:30 to the reversal window and the actual reversal
   trade between the 9:40 and 9:50" - the false breakout precedes the window; price:71,89-90 search the sweep only inside
   09:40-09:50. f1: sweep 09:35 + reversal 09:42 -> N=0; same geometry, sweep 09:42 -> 2. The source case never enters.
C2 JJ-TBR single_extended/single_purged/internal_rotation/extension_reaction action window. TBR p.12 "you want to be in
   the trade before 10am ... after 10am all interest in being in a position is not longer present"; price:72 forces
   action_end=16:00. f2: a 14:00 EQ contact still emits candidates (touch 270 min after 09:30). Inflates the population.
C3 GB-FAIL all seven sweep branches, five-minute reclaim. GB p.25 "I wait for the 5 min close back below the PDL after
   sweeping above it"; price:219-223 read only the aligned candle containing the sweep. f3: sweep 10:01 whose own candle
   closes above and whose NEXT closes back inside -> fail (confirm_close 101.5 vs 101.0); the same reclaim moved inside
   the sweep candle -> pass. Understates pass / overstates fail on the largest method (7589 rows).
C4 KEANI rejection stage. AVG p.21 "Price will probably reject off the POC or the previous day's value area high";
   auct:258-260 require row.L <= the DEVELOPING value-area low and a close above it. f4: two sessions identical except
   wick depth - rejection off the developing POC 103.0 observes nothing; the same candle at VAL 102.0 starts everything.
C5 SIRES microbalance_break thesis direction. K2345 pp.4-7: the break occurs "within the established directional
   auction"; flow:337 selects the trigger by sign(C-boundary)>0 and flow:346 restates it, the larger balance serving only
   as the target. f6: long and short breaks of one microbalance inside one larger balance both bind True.
C6 GB-VWAP continuation_context (reused, not re-proved). price:314 rebinds the operand with the retest-absence answer,
   discarding the True from price:308. Proven as D1 in reviews/phase1-code-review-2026-09-14 (repro_d1.py, 2023-12-08).
C7 Constant, restating and side-independent operands, all twelve methods. f7 lists 25 predicate operands bound to Python
   literals - GB-FAIL pocket_required/retracement_entry=False plus side-independent bias_recorded, GB-VWAP
   vwap_reset_verified, JJ-TBR source_clock_verified/source_case_verified/exit_window_recorded, SAINT arrival_read_recorded
   and alignment_ok (never False), SIRES kg1_retest/same_band_retest/microbalance_frozen, REFILL's four record conjuncts,
   STOIC-DATA cycle_and_indicator_rules_recorded - and shows O065-O069, O072, O087, O116 (naked POC, HVN, LVN, shelf,
   ledge, prior reaction area, unfinished business, refill zone) are referenced by no scanner although ABS p.7 names
   exactly those as the required absorption locations. SIRES real_extreme (flow:170,177) is true by construction (band =
   edge +/- 1 tick) and SAINT profile_allows_trade (auct:46) can never refuse. Gates that should reject cannot; verdicts
   are biased toward pass and unknown.

MISSING STAGES (source-stated, absent from the code and from the assumption ledger)
- STOP p.10 "minimum filter is three ticks of replenishment" - no tick measure in flow_stages refresh.
- TBR p.12 quadrant (0.25 / 0.75) entries - declared in A2-TBR-PROJ, read by no code path (f5).
- TBR p.8 outbound exit at the reversal window; TBR p.12 single_purged's 09:40-09:50 add window.
- GB p.25 golden pocket (50-61.8%) and the "entry on any retracement" variant - both flags literal False.
- OFM p.14 "scalp target in the 1R to 3R zone" - ofm_passive binds no objective at all.
- AMTL pp.5-10 / TRAP pp.4-5 arrival read (speed, delta, effort vs movement) - literal True.
- REF pp.5-9 zone definition, thesis and label-discipline records - four literal True conjuncts.
- Recorded as skipped and legitimate (EXTERNAL ledger): P-zone bands, KG1, gamma maps, account/-4R ledger, supplied
  B-A-D-E-W labels, touch grader and selected orders, STOIC process/risk ledgers, GB-SCALP entry rule - the most decisive
  stage of 8 of the 12 methods.

INFERRED CHOICES THAT MOST SHAPE RESULTS
1  A2-AUCTION-SAMPLE primary = latest pivot-balance known by 09:30 - the only reference for all 15 SIRES and 4 SAINT branches.
2  A2-BALANCE 4 alternating pivots / 300s bars / 25% edge tolerance - decides whether any SIRES/SAINT candidate exists.
3  A2-FLOW effort_seconds=5, local_horizon_seconds=120 - every Sires/Member/Keani stage clock; one chunk late is invisible.
4  A2-FLOW minimum_effort_events=2, no_progress_ticks=2 - the effort/absorption gate on 13 branches.
5  A2-TBR-CLOCK confirmation_seconds=180 + one O056 signature - the only JJ-TBR confirmation, replacing the manual's
   orderblocks, rejection blocks, absorption candles and footprint reads.
6  action_end=16:00 on four JJ-TBR branches (C2) - the largest single population inflator found.
7  A2-GB-CLOCK asia 20:00-00:00 / london 02:00-05:00, reclaim_seconds=300 - sets both GB-FAIL references and all of GB-VWAP.
8  A2-AUCTION-SAMPLE jet_observation=09:30-09:32 - one 2-minute sample stands for the whole auction in all five states.
9  A2-REACTION-HVN member_prior_split=12:45 - the constant that makes the two Member reasons "independent".
10 A2-KEANI-TIME latest_break=11:00 and keani_fallback_objective=A_high+A_width - the only time bound and default objective.

VERDICT (exact / operational / inferred / mismatch / missing)
JJ-TBR                  partially faithful              11 / 13 /  4 /  6 /  6
GB-FAIL                 partially faithful              15 / 15 /  0 / 14 /  2
GB-VWAP                 partially faithful               1 /  3 /  0 /  2 /  0
GB-SCALP                faithful with labelled choices   1 /  0 /  4 /  0 /  4
SIRES                   partially faithful               5 / 35 / 16 / 16 /  6
SAINT-AMT               partially faithful               3 / 21 /  1 /  8 /  4
MEMBER-TWO-REASONS      faithful with labelled choices   4 /  8 /  0 /  0 /  0
KEANI-OPEN-ABOVE-VALUE  partially faithful               2 /  2 /  0 /  1 /  0
REFILL-STUDY            faithful with labelled choices   3 /  1 /  0 /  0 /  4
JETBUNDLE-STATES        faithful with labelled choices   1 /  0 / 14 /  0 /  1
STOIC-DATA              partially faithful               0 /  1 /  0 /  1 /  2
STOIC-RISK              faithful with labelled choices   3 /  1 /  0 /  0 /  1
No method is unfaithful: every branch traces to a cited source stage and no invented strategy was found. The defects are
clock boundaries (C1-C3), one wrong level (C4) and a large family of operands that cannot refuse a candidate (C5, C7).
