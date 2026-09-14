import json
R=[]
def row(m,b,stage,anchor,src,code,cls,note=''):
    R.append({'method':m,'branch':b,'stage':stage,'source_anchor':anchor,'source_statement':src,
              'code':code,'class':cls,'note':note})
A='historical_auction_scanners.py'; P='historical_process_scanners.py'; X='strategy_context.py'; F='historical_flow.py'

SA=['continuation_retest','trapped_buyers_retest','failed_auction_return','poc_traversal']
for b in SA:
    row('SAINT-AMT',b,'HTF balance','RTVP pp.3-11 "redraw the balance until it fits the market before trading it"',
        'a fitted, accepted higher-timeframe balance',
        f'{A}:10-13 primary_balance = last 4-alternating-pivot 5-minute balance known by 09:30, else the first confirmed after (A2-AUCTION-SAMPLE)','operational')
    row('SAINT-AMT',b,'profile permission','RTVP pp.3-11 "An unbalanced trending profile is left alone until a new balance forms"',
        'a trending/unbalanced profile forbids the trade',
        f'{A}:46-47 profile_allows_trade = ref.low <= 68% profile POC <= ref.high; the POC of a profile taken over the balance is inside it by construction','mismatch',
        'the source gate is never able to refuse')
    row('SAINT-AMT',b,'arrival read','AMTL pp.5-10;WIC pp.4-6 "inspect how price arrived, executed delta and whether aggressive effort achieves movement"',
        'read arrival, acceptance/rejection and the controlling side',
        f'{A}:49 arrival_read_recorded=True literal; no arrival speed, delta or effort/response observation is bound','missing')
    row('SAINT-AMT',b,'HTF/LTF alignment','WIC p.10 "higher/lower-timeframe alignment as the whole method"',
        'the current HTF read and the lower-timeframe control must agree',
        f'{A}:51 alignment_ok = True when any two successive same-side body+delta bars exist, else None; the HTF read is never computed or compared','mismatch',
        'the operand can never be False')
    row('SAINT-AMT',b,'confirmation','TRAP pp.6-12 "repeated aggressive selling inside candle bodies, with footprint and DOM agreement"',
        'real repeated initiative in the intended direction',
        f'{A}:16-22 _control = two consecutive complete bars with same-sign delta and same-sign body (A2-AUCTION-SAMPLE control)','operational',
        'footprint and DOM agreement are not required')
    row('SAINT-AMT',b,'invalidation','TRAP pp.8-10','risk beyond the structure being traded',
        f'{A}:92,151 stop = LTF balance opposite edge, or min(trigger extreme, older balance extreme) -/+ 1 tick','operational')
    row('SAINT-AMT',b,'objective','RTVP pp.5-8;AMTL pp.8-11 "POC/fair value, the other shelf, the far balance edge or prior balance"',
        'the next accepted area',f'{A}:92,152 target = the far edge of the HTF balance only','operational',
        'POC, shelves and the prior balance are never selected as destinations')
row('SAINT-AMT','continuation_retest','LTF break','WIC pp.7-10 "An actual intraday balance break followed by a held retest shows control"',
    'a distinct lower-timeframe balance break',
    f'{A}:76-84 LTF = 60-second balances narrower than half the HTF width; first completed close beyond the LTF boundary','operational')
row('SAINT-AMT','continuation_retest','same-boundary retest','WIC pp.7-10','return to the same boundary and hold',
    f'{A}:87-97 first contact within +/-1 tick of the boundary inside 60 minutes; held = every bar to the control end stays within 2 ticks','operational')
row('SAINT-AMT','trapped_buyers_retest','two prior failures','TRAP pp.4-5,5-9 "two prior AM/PM failures support the thesis, but the current break/retest is still required"',
    'two distinct earlier upper-extreme buying failures',
    f'{A}:59-68 _upper_failures = contacts of high+/-1 tick with positive delta followed within 30 minutes by a close 4 ticks below the high','operational')
row('SAINT-AMT','failed_auction_return','older value tested and rejected','AMTL p.8 "If price reaches that lower area and rejects it, coming all the way back up rather than accepting into it"',
    'an older separate area of fair value is tried and rejected',
    f'{A}:141-142 first contact of the older balance 68% value area, then a close beyond its opposite value edge','exact')
row('SAINT-AMT','failed_auction_return','reacceptance','AMTL p.8 "Once price comes back into the original range"','return inside the original balance',
    f'{A}:146 first completed close strictly inside ref low/high after the rejection','exact')
row('SAINT-AMT','failed_auction_return','older-balance selection','AMTL pp.8-10','a previous area of fair value',
    f'{A}:121-134 the last balance known before the primary balance starts, else the last balance of the prior session','operational')
row('SAINT-AMT','poc_traversal','POC passage','AMTL p.9 "if buyers push aggressively through POC, maybe with a retest that holds"',
    'aggressive passage through the original POC',
    f'{A}:148 a completed close beyond the 68% POC with same-sign delta','exact')
row('SAINT-AMT','poc_traversal','hold','AMTL p.9','a retest that holds',f'{A}:167 all control bars close on the far side of the POC','operational')
row('SAINT-AMT','poc_traversal','far-edge objective','AMTL p.9 "80 percent that price runs all the way to the far extreme"',
    'the far balance extreme',f'{A}:169 target_is_far_balance_edge = target in (low,high) - restates line 152','inferred','vacuous')

for b,side in (('resistance_short','short'),('planned_return_long','long')):
    row('MEMBER-TWO-REASONS',b,'prior reaction area','K10 pp.5-7 "a level he\'d already marked as a key area of resistance, price had rejected from it before"',
        'a previously reacted higher-timeframe level',
        f'{A}:185-194 confirmed 5-minute pivots inside the prior session before 12:45 with >=4 ticks of reaction (A2-REACTION-HVN)','operational')
    row('MEMBER-TWO-REASONS',b,'independent minor HVN','K10 p.7 "He lined it up against a minor high volume node sitting close by, two independent reasons"',
        'an independently identified nearby minor HVN',
        f'{A}:196-206 locally maximal volume price in the prior session after 12:45, within 2 ticks of the reaction (A2-REACTION-HVN)','operational',
        'the 12:45 split that makes the two reasons "independent" is a project constant')
    row('MEMBER-TWO-REASONS',b,'band contact','K10 pp.7-8','price arrives at the confluence area',
        f'{A}:213-218 first distinct contact after 09:30 with an exact execution inside [lo,hi]; actual_band_contact=True literal','operational')
    row('MEMBER-TWO-REASONS',b,'invalidation','K10 p.7 "Stop went above the high of the rejection"','stop beyond the rejection structure',
        f'{A}:225-226 stop = extreme of the observed flow chunks +/- 1 tick','exact')
    row('MEMBER-TWO-REASONS',b,'objective','K10 p.7 "target set at 1.5R"','1.5R planned target (the graphics show 1.00R and 9.60R)',
        f'{A}:227 target = entry +/- 1.5*|entry-stop| (A2-REACTION-HVN target_r=1.5)','exact')
row('MEMBER-TWO-REASONS','resistance_short','rejection','K10 pp.7-8 "short on the resistance rejection"','an observed rejection at the area',
    f'{A}:222 the "reward" flow stage (>=3 ticks away from origin with own>opposing)','operational')
row('MEMBER-TWO-REASONS','planned_return_long','second tap and hold','K10 pp.6-8 "long on the return/second tap when buyers absorb and hold"',
    'a distinct later return, buyers absorb and hold',
    f'{A}:213-216 the FIRST distinct contact of the current session is used; the prior-session reaction is treated as the first visit','operational',
    'a defensible reading, but the source "second tap" is not counted in-session')

for b in ('touch_record',):
    row('REFILL-STUDY',b,'zone formation','REF pp.5-7 "Form the zone from clustered large aggressive orders"',
        'clustered large aggressive executions with instrument, side, span and formation time',
        f'{P}:25-31 m09_research_comparison with A2-REFILL (min 100 lots, >=2 events, 120s, 2-tick span)','operational')
    row('REFILL-STUDY',b,'departure','REF pp.5-7 "price then leaves"','an observed departure',
        f'{P}:40 departure_observed = ref.departure_at is not None (A2-REFILL departure_ticks=4)','exact')
    row('REFILL-STUDY',b,'distinct return','REF pp.6-9 "At each later return, create a distinct touch event"','a distinct later return',
        f'{P}:40 distinct_touch_id against earlier resolved touches of the same zone','exact')
    row('REFILL-STUDY',b,'pre-touch memory','REF pp.6-9 "Freeze memory of earlier defenses ... before this touch resolves"',
        'only earlier resolved touches may inform this one',
        f'{P}:42 memory_uses_only_prior_resolved_touches = all prior resolved_at < occurrence_start','exact')
    row('REFILL-STUDY',b,'thesis / zone definition / label discipline','REF pp.5-9',
        'zone definition, thesis and label separation are recorded',
        f'{P}:38-43 zone_definition_recorded, instrument_and_threshold_preserved, thesis_recorded and label_uses_only_post_touch_observations are all literal True','missing',
        'four predicate conjuncts can never be false')
row('REFILL-STUDY','touch_record','grading','REF pp.8-9,16 "Grade the already-found touch under a frozen model"','a frozen touch-grader',
    f'branch_coverage EXTERNAL[selection]; not implemented, recorded as an external operand','missing','recorded as skipped')
for b in ('supplied_selected_order','selected_order_configuration'):
    row('REFILL-STUDY',b,'execution configuration','REF p.12 "rest a limit order 12 ticks inside the level, stop 32 ticks, target 96 ticks, cancel after 30 minutes, one position at a time, 1-tick round-trip cost and 1 tick of stop slippage"',
        'the documented 12/32/96/30-minute one-position configuration',
        f'{P}:251 scan_supplied_unit; no supplied order record exists, so the whole configuration predicate is unevaluated','missing','recorded as skipped')

JB=[('B',['two_sided_executions','recent_revisits','low_aggression_both_sides']),('A',['high_aggression','low_response_efficiency','opposite_liquidity_holds_and_refills']),
    ('D',['aggression','efficient_displacement']),('E',['prior_absorption_or_effort','replenishment_stops','level_gives_way']),('W',['cancellations_dominate'])]
for b,names in JB:
    row('JETBUNDLE-STATES',b,'observation scope','MATH pp.4-6 "Observe provide, withdraw, consume through submissions, cancellations and executions"',
        'provide/withdraw/consume over the auction',
        f'{P}:175 exactly one fixed window, 09:30-09:32 (A2-AUCTION-SAMPLE jet_observation)','inferred',
        'one 2-minute sample per session stands for the whole auction')
    row('JETBUNDLE-STATES',b,'state assignment','MATH pp.9-10','assign the heuristic current state',
        f'{P}:196-211 only from a supplied dated state_label record - never present; reconstruct mode uses {X}:46-69 auction_criteria','inferred',
        'EXTERNAL[state_label]; no classifier is published')
row('JETBUNDLE-STATES','B','criteria','MATH p.9 "Local value is characterized by two-sided executions and frequent, recent revisits, low aggression on both sides"',
    'two-sided trade, recent revisits, low aggression both sides',
    f'{X}:67 buy>0 and sell>0; revisit = price sets of quarter 1&3 or 2&4 intersect; low = both sides <= the preceding equal window','exact')
row('JETBUNDLE-STATES','A','criteria','MATH pp.6-8','high aggression, little response, opposite liquidity holds and refills',
    f'{X}:55-61 high = max(buy,sell) >= 1.5x prior; absorb = |response|/range <= 0.2; refill = adverse response <= 2 ticks and passive adds > 0','inferred',
    '1.5 / 0.2 / 2-tick constants are project choices')
row('JETBUNDLE-STATES','D','criteria','MATH pp.6-8 "Efficient aggression is discovery"','aggression with efficient displacement',
    f'{X}:58 efficiency >= 0.6 and |response| >= 2 ticks','inferred')
row('JETBUNDLE-STATES','E','criteria','MATH pp.7-11','prior absorption/effort, replenishment stops, level gives way',
    f'{X}:62-65 prior one-sided volume; current adds <= 0.25x prior adds; last-quarter VWAP beyond the prior window extreme','inferred',
    'level_gives_way is direction-agnostic: it does not have to give against the prior effort')
row('JETBUNDLE-STATES','W','criteria','MATH pp.7-11','cancellations dominate',
    f'{X}:32-33,66 withdrawal = max(0, depth-one removals - all executions) > adds + volume','inferred',
    'a depth-one estimate, not identified MBO cancels; the source measures actual cancellations')
row('JETBUNDLE-STATES','transition_observation','transition','MATH pp.7-11 "Observe the next transition conditional on current liquidity and pace"',
    'adjacent dated same-identity transitions',f'{P}:251 scan_supplied_unit; no dated label records exist','missing','recorded as skipped')

row('STOIC-DATA','process_review','frozen spec','DATA p.3 "define a reproducible execution/research process before collecting the sample"',
    'the process is defined before collection',f'{P}:152-158 from m.records["process_review"]; no such record is ever supplied, so the branch emits zero episodes','missing','recorded as pending_process_record')
row('STOIC-DATA','process_review','uniform collection / winner-loser comparison','DATA pp.3-4','collect every observation the same way; compare all winners and losers',
    f'{P}:154-157 operands exist and are computed from the record, but no record exists','missing')
row('STOIC-DATA','macro_application','release vintages','DATA pp.5-6','compare indicators with history using standardized deviations',
    f'{P}:109-129 CPIAUCSL and PAYEMS initial releases only, O160 against 12 prior initial observations (A2-MACRO)','operational')
row('STOIC-DATA','macro_application','cycle / C-score / trend','DATA pp.5-6 "custom C-scores ... macro cycle ... leverage/credit/housing/valuation indicators"',
    'a custom C-score, cycle and trend-strength verdict',
    f'{P}:165 cycle_and_indicator_rules_recorded = True when reconstructing, else None; strategy_context.inferred_macro computes mean(payroll z, -CPI z) instead','mismatch',
    'the operand is set True by a substitute two-series composite that the wiki says is explicitly not the C-score')

row('STOIC-RISK','first','eligibility','DATA p.8','>=100 observations, known win rate and average R:R, Monte Carlo loss streak, base risk <= 1%',
    f'{P}:226-237 from m.supplied("risk_stage") and O154 validation - never present','missing','recorded as skipped (EXTERNAL[validated_process])')
row('STOIC-RISK','first','ladder arithmetic','DATA p.7 "Risk 1% at 1 to 3. Win: account up 3%"','1 unit at 3R',
    f'{P}:240-242 published_arithmetic risk_units=1, planned_reward_R=3, reward_baseline_units=3','exact','reported, not evaluated')
row('STOIC-RISK','second','ladder arithmetic','DATA p.7 "Risk 1% plus the 3% banked, 4% total. Win 3R: plus 12%"','4 units at 3R, +12',
    f'{P}:240-242 risk_units=4, reward_baseline_units=12','exact','reported, not evaluated')
row('STOIC-RISK','reset_after_second_win','reset','DATA p.7 "After the second win, reset to 1% base risk and repeat"','back to 1 unit',
    f'{P}:242 next_after_second_win=1','exact')
row('STOIC-RISK','first','activation rule','DATA p.7 "dynamic risk that only activates on a two trade winning streak" vs the ladder that raises risk after the first 3R win',
    'the source contradicts itself','no code resolves it; the wiki preserves the discrepancy and the predicate audits the printed ladder','operational','source limit, not a defect')
json.dump(R,open('rows_part3.json','w'));print(len(R))
