# Unknown and data-unavailable label audit, 2026-09-14

UNKNOWN / DATA-UNAVAILABLE AUDIT - accepted census run-1.0.1 (1,742 sessions x 57 branches = 99,294 branch-sessions,
101,710 observed candidates, 18,747 setups). Dedup basis: MEASUREMENT_RESULTS["branches"] and records/coverage-exclusions.jsonl.gz
(one row per branch-session). by_year and by_decision_session repeat the same jobs (by_decision_session 5x); they were not used.
Code paths below are implementation/src/trading_research/research/method_pack/ unless noted.

== LABEL INVENTORY == (label | rule file:line | plain meaning | unduplicated count | share)
decided statuses setup 18,796 / no_setup 72,387 / condition_present 2,145 / condition_absent 7,961 (historical_assembly.py:64,67)
candidate_status:data_unavailable | historical_assembly.py:64,67 | at least one selected input is None, so the rule cannot be decided | 421 | 0.41% of candidates (211 of 90,344 entry-setup = 0.23%)
research_verdict "unknown"        | historical_assembly.py:79 | the same 421 candidates, pre-reconstruction verdict | 421 | 0.41%
completed_search                  | measurement_runner.py:141-143 | prefix observed, no active limitation, no unavailable candidate | 72,925 | 73.4% of branch-sessions
observed_search_with_input_limitations | measurement_runner.py:143 | searched, but at least one limitation retained | 13,575 | 13.7%
personal_execution_out_of_scope   | measurement_runner.py:142, strategy_policy.py:43 | branch needs the author's own records | 12,194 | 12.3%
scheduled_closure                 | measurement_runner.py:143 | certified closed RTH, no episodes                | 600 | 0.6%
unknown_current_minutes           | report_census.py:75-78 counting event_time.py:298-313 holes (state rule event_time.py:137-157; relaxation strategy_measurements.py:136-162) | minutes of the required prefix whose trade coverage cannot be certified | 617,067 branch-session-minutes = 17,037 DISTINCT calendar minutes | 0.74% of the 2,299,440 distinct census minutes (0.70% of 88.4M branch-session minutes)
"current input prefix has unknown intervals" | report_census.py:77 | that session has >=1 such minute | 2,373 branch-sessions on 70 dates | 2.4%
"actual dated process/source records absent" | historical_process_scanners.py:292 | no dated personal trade/process record exists | 12,194 | 12.3%
"no actual validated process and risk-stage ledger" | historical_process_scanners.py:239 | same, for the risk-ladder method | 5,226 | 5.3%
"collection review is emitted after this date job finishes" | historical_process_scanners.py:169 | the review artefact is published later than the date being measured | 3,484 | 3.5%
"GB p.40 discloses no complete repeatable scalp entry" | historical_process_scanners.py:257 | the source book never states the entry rule | 1,742 | 1.8%
same_contract_prior_scope_unknown | historical_features.py:198 | a prior-session lookback day is not fully covered for the SAME contract | 676 sessions / 1,812 day-rows | 0.7%
calendar_unverified               | historical_features.py:180 (state session_policy.py:64-67) | a candidate holiday has no dated CME schedule acquired | 544 | 0.5%
formation_has_no_observed_executions | historical_price_scanners.py:67 | a named formation window contains no trades | 231 sessions / 435 rows | 0.2%
"KG1/key-gamma model input unavailable" | historical_flow.py:281; strategy_options.py:123-129,65,87,144 | no option-chain gamma level could be built causally | 107 | 0.11% (6.1% of that branch's 1,742 sessions)
"no distinct older completed auction..." | historical_auction_scanners.py:135 | prefix holds only one price-defined balance | 90 | 0.09%
other labels: author_exact_verdict "unknown" is a constant on all 101,710 candidates (historical_assembly.py:96, by design, not a data gap);
  unavailable_candidates = per-session count of the 421 (measurement_runner.py:139,150); "A period has no observed executions" 47 (historical_auction_scanners.py:253);
  boundaries_not_defined 3,066 setups and measurement_reference_unavailable 0 (measurement_outcomes.py:104-106, report_census.py:90)
smaller labels: "scheduled RTH closure; no market-state observation" 60 (historical_process_scanners.py:180); "no dated P-zone bands/destinations" 35
  (historical_price_scanners.py:61); "earlier potential (directional) breakout close is unknown" 34+4 (historical_assembly.py:121, historical_price_scanners.py:290);
  nonpositive_formation_width 22 (historical_price_scanners.py:70); "bar contact has no exact band execution" 1 (historical_auction_scanners.py:218)
cash_open_order_unknown           | historical_price_scanners.py:195 | the 09:30 minute has no usable opening print | 58 | 0.06%
session_reference_missing         | historical_price_scanners.py:285 | Asia/London reference windows contain no trades | 21 | 0.02%
incomplete_future_coverage (horizon) | measurement_outcomes.py:166 | the 5/15/30/60-min window is not fully inside the admitted day | 2,768 of 74,988 horizon rows | 3.7% (2,753 = clock ran past the 16:00 admitted end)
missing_future_coverage (boundary)| measurement_outcomes.py:111,146 | stop/target never resolved and the remaining window is not certified | 90 of 18,747 setups | 0.5%

== CAUSE CLASSIFICATION == (a raw data absent | b deliberate rule, data exists | c input never owned | d code failed to read available data)
(c) 22,646 branch-session labels: "actual dated process/source records absent" 12,194; "no actual validated process and risk-stage ledger" 5,226;
    "collection review ... after this date job" 3,484; "GB p.40 ..." 1,742. Plus "no dated P-zone bands/destinations" 35. Personal trade journals,
    a proprietary risk ledger, an unpublished entry rule and dated P-zone records are not in /workspace/data at all (glob for process/ledger/journal/
    trade-record datasets returns nothing). Nothing to read.
(a) 16,938 of 17,037 distinct unknown minutes (99.42%); 544 calendar_unverified (no dated CME schedule acquired - nq_session_policy_v2.json holds only
    4 dated exceptions, and run-calendar-recovery-v1 already repaired two more); 47 "A period"; 21 session_reference_missing; 10 of 12 sampled formation
    rows; 9 of 14 sampled KG1 (the QQQ quote file for that date does not exist: 1,677 files vs 1,742 sessions); 4 of 18 sampled same_contract_prior;
    part of cash_open_order_unknown (expiry/holiday minutes).
(b) 421 data_unavailable candidates; 96 unknown minutes on archive ownership boundaries; 3 unknown minutes with quotes but no trades;
    1,812 same_contract_prior rows dominated by the same-contract-only rule; 2,753 truncated horizons; 90 "no distinct older auction";
    2 of 10 sampled cash_open_order_unknown; 5 of 14 sampled KG1. Raw rows exist; a documented three-valued rule refuses to guess.
(d) ZERO instances found. See RAW CHECKS.

== RAW CHECKS ==
Sample: 460 rows in sample.jsonl - an EXHAUSTIVE check of all 17,037 distinct unknown minutes (not a sample), 42 data_unavailable candidates across
8 methods and 2020-2026, 18 same_contract_prior, 14 KG1, 12 calendar_unverified, 12 formation, 10 cash_open, 8 session_reference, 6 older-auction,
6 A-period, 12 not-owned-record rows, 60 reverse-check sessions. Every check reads /workspace/data parquet directly.

unknown_current_minutes (17,037/17,037 checked, 100%):
  16,938 (99.42%)  no MBP-1 row of any kind exists in /workspace/data for that minute -> (a). These fall on 24 dates: 8 Good Fridays/Christmas Eve
                   (1,320 min each), 11 New Year/Christmas evenings (360 each), 2025-01-09 national day of mourning (930), 2026-09-03 (831 - the
                   archive itself ends at 2026-09-03 06:09 UTC), 2026-06-19 (300), 2025-09-01 (180), 2024-11-29 after-Thanksgiving early close (180).
  96     (0.56%)   rows AND trades for the session's own contract DO exist. All 96 sit on an archive ownership boundary: 94 are the 23:59 and 00:00 UTC
                   minutes at 47 monthly-file seams, 1 is 2024-11-29 12:59 ET and 1 is 2026-09-03 02:09 ET (last minute of the last file).
                   Cause: adapters.py:2896-2901 sets a month file's owned span to [first observed row, last observed row+1ns], so two adjacent months
                   leave a hairline unowned gap (e.g. 2021-05-31 23:59:59.945247868 -> 2021-06-01 00:00:00.003959239 = 58.7 ms). Verified: that
                   58.7 ms contains 0 rows in any file, while the two minutes around it hold 241/21 and 560/70 rows/trades. event_time.py:307 marks any
                   minute touched by an unowned span unknown and strategy_measurements.py:143 disables the ownership relaxation for the whole requested
                   range. Rule (b): every existing row was read; continuity across a file seam is not certified. Not a defect, but cosmetically misleading.
  3      (0.02%)   quote rows but zero trades (2021-11-01 00:33 ET: 52 book rows, 0 trades; 2026-06-19 x2). event_time.py:137-157 refuses to infer
                   "quiet" from quotes. Rule (b), explicitly documented in the module docstring.
  -> 0 of 17,037 is a case of the code failing to read trade rows that exist and are inside an owned span.
candidate_status:data_unavailable (42 checked): 10/10 JETBUNDLE cases have a genuinely empty 09:28-09:30 or 09:30-09:32 window (4 and 6) -> (a).
  32/32 of the other methods have raw executions around the decision; the None operand comes from a rule. Proven for three of them:
  - 2020-04-17 GB-FAIL previous_hour (repro_confirm_close.py): the 09:30-09:35 confirmation bar has 10,178 trades and known H/L/V, but its final
    nanosecond batch is 6 rows at two prices (8817.50 / 8817.75) and the acquired MBP-1 schema has NO exchange_sequence column, so mbp1_views.py:176-184
    returns C=None -> confirm_close/box_return_ok/risk_defined/objective_fixed unknown. Rule (b) on an ordering field that is genuinely absent (a).
  - 2020-02-27 SIRES kg1_retest: identical mechanism on the 09:31-09:32 close (2 rows, 8659.75/8660.00) -> key_gamma_reference returns [] although
    the gamma model itself was available (replayed live: regime "short", 82 contracts).
  - 2023-12-28 SIRES kg1_retest: gamma model replayed -> "no eligible quote/prior-OI contracts", all 104 quoted contracts rejected for missing prior
    open interest -> (a), the acquired OI snapshot does not cover them.
same_contract_prior_scope_unknown (18): 14 "prior day traded, but only under a different contract id" -> the same-contract-only rule (b);
  4 "prior day has no rows at all" -> (a). 1,355 of the 1,812 rows are GB-FAIL prior_month_level, where a whole prior month precedes a roll.
calendar_unverified (12): 6 dates have full RTH trading in the raw tape, 6 have none. Either way the label only says the dated CME schedule was never
  acquired; the code never mis-reads the tape -> (a)/(c).
cash_open_order_unknown (10): 4 "09:30 minute empty" and 4 "book rows, no trades" - all quarterly-expiry or holiday minutes -> (a).
  2 (2024-06-03, 2026-06-02) have 3,586 and 5,160 trades at 09:30 (repro_cash_open.py): the first nanosecond batch is 2 rows at 2 prices, no sequence
  column, so O=None; vendor 1-minute reconciliation (strategy_measurements.py:72-97) refused because published V=5084 vs native 5083 on 2024-06-03 and
  because the 2026-06-02 vendor minute does not exist. Rule (b) - deliberately refuses an endpoint from a provably different population.
KG1 (14): 9 QQQ quote file absent -> (a); 5 files present, of which 3 fail on the ambiguous 09:31 close and 1 on missing prior OI -> (b)/(a).
formation (12): 10 windows truly empty, 2 rows-but-no-trades -> (a)/(b). session_reference_missing (8): 8/8 Asia AND London windows empty -> (a).
A period (6): 5/6 empty, 1 (2024-03-15) has 7 book rows and 0 trades because the mapped contract expired at 09:30 -> (a). Older-auction (6): 6/6 have a
full overnight tape - the rule needs a second price-defined balance, not more rows -> (b). Not-owned records (12): no process/ledger/journal/trade-record
dataset exists anywhere under /workspace/data -> (c). Category (d) instances: NONE; no defect reproduction could be written because no defect was found.

== REVERSE CHECK ==
30 sessions with the largest unknown_current_minutes: all are the closure dates listed above; per-minute parquet counts confirm 0 rows for every
unknown minute except the 94 seam minutes and the 2 end-of-file minutes already itemised.
30 sessions with zero unknown minutes (random across 2020-2025): 20 have >=1 trade for the session's own contract in all 1,320 prefix minutes. The rest
are the one caveat worth stating: 2020-12-24 and 2023-05-29 have 180 minutes with no rows at all (early closes), 2023-06-16 has 388 no-row and 155
quote-only minutes (the mapped contract expired at 09:30 on quad-witching), and 2020-06-18 / 2021-03-17 / 2021-12-10 / 2022-08-18 / 2024-09-13 /
2025-02-13 / 2025-02-24 have 1-12 quote-only minutes. These count as COMPLETE because strategy_measurements.py:136-162 treats a fully
enumerated owned archive interval as complete ("no market-feed completeness claim"). So "zero unknown" means "the archive file demonstrably covers the
interval", not "a trade printed in every minute". That relaxation removed 1,456,713 of 2,073,780 strict unknown branch-session minutes (70%); it makes
the census LESS conservative, never more. 2024-11-29 is the mirror image: the same early close is flagged unknown only because the November file
physically stops at 12:59 ET.

== TOTAL EFFECT ==
Entry-setup scope (the 37 branches that produce setups): 64,454 branch-sessions - 61,050 (94.72%) completed_search, 2,960 (4.59%) carry at least one
limitation, 444 (0.69%) scheduled closure. 1,932 of the 2,960 are limited by unknown minutes, and 1,196 of those by nothing but the month-seam hairline.
Candidates: 421 of 101,710 (0.41%) are data_unavailable; 211 of 90,344 entry-setup candidates (0.23%).
Setups: all 18,747 are measured and reported; 452 (2.41%) sit in a limited session and are therefore excluded from the eligible-session denominator
(18,295 of 18,747); 206 of those 452 (1.10% of all setups) are on month-seam-only dates.
Horizons: 2,768 of 74,988 (3.69%) incomplete, of which 2,753 are simply a 60-minute clock running past the 16:00 admitted end; only 15 reflect thin data.
Fraction that would change if every (d) defect were fixed: 0%, because no (d) defect exists. For contrast, if the two most conservative (b) rules were
relaxed: declaring monthly ownership to the month boundary would move 1,196 entry-setup sessions (1.86%) and 206 setups (1.10%) into the complete
denominator and would change no measured price; accepting a vendor-reconciled opening print would clear at most 58 cash_open_order_unknown sessions and
some of the 421 data_unavailable candidates (<=0.41% of candidates). Neither changes a single measured outcome.

== VERDICT ==
1. The "unavailable" labels are not a reading failure. Of the 17,037 minutes the census calls unknown, 16,938 (99.4%) have no market data of any kind in
   /workspace/data - they are Good Fridays, Christmas and New Year evenings, a national day of mourning, and the hours after the archive itself ends.
2. The remaining 99 minutes, and almost all the candidate-level "data unavailable" flags, are cases where the data IS there and the program deliberately
   refuses to guess: it will not order two trades printed in the same nanosecond at two prices (the files carry no sequence number), will not treat quotes
   as proof that nobody traded, and will not certify continuity across the seam between two monthly files. Those are stated rules, not bugs.
3. The biggest blocks of "unavailable" - about 22,600 of them - are for inputs the project never had and never claimed to have: the author's own trade
   journal, a proprietary risk ledger, an entry rule the source book does not state. No amount of code fixing produces data that was never collected.
   Net effect on results: 0.41% of candidates undecided, 2.4% of setups outside the complete-session denominator, 0 measured prices affected.
