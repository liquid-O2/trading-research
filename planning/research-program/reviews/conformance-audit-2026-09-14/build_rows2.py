import json
R=[]
def row(m,b,stage,anchor,src,code,cls,note=''):
    R.append({'method':m,'branch':b,'stage':stage,'source_anchor':anchor,'source_statement':src,
              'code':code,'class':cls,'note':note})
S='historical_price_scanners.py'; A='historical_auction_scanners.py'; F='historical_flow.py'; P='historical_process_scanners.py'; X='strategy_context.py'

SIR=['dom_rejection','absorption_reward_retest','stop_four_stage','footprint_confirmed_reaction','vwap_deviation_fade',
     'ofm_aggressive','ofm_passive','clean_squeeze','balance_failure_fade','defended_band_continuation','kg1_retest']
for b in SIR:
    row('SIRES',b,'thesis / regime','C1 pp.3-6;GEX pp.4-20','write direction, objective and validity band; gamma regime where the source uses it',
        f'{F}:128-131 thesis_alive = sign(entry-stop)>0; auction_route_ok = ref.complete; branch_regime_allowed=True except ofm_aggressive/balance_failure_fade','mismatch' if b in ('ofm_aggressive','balance_failure_fade') else 'inferred',
        'no recorded death condition, value migration or news is consumed; thesis_alive restates risk_defined')
    row('SIRES',b,'location','ABS p.7 "what he actually wants for absorption entries are real extremes: shelves, ledges, low volume nodes, minor volume nodes"',
        'a real, fixed extreme - not a recalculating value line',
        f'{F}:283-284,308 the location is the latest 5-minute alternating-pivot balance known by 09:30, band = edge +/- 1 tick; shelves/ledges/LVN/minor nodes are never used','mismatch',
        'C7: real_extreme (line 170/177) is origin<=low+Q or origin>=high-Q with origin==edge, so it is true by construction')
    row('SIRES',b,'invalidation','ANAT pp.8-10;C2 pp.3-7','the controlling structure determines invalidation',
        f'{F}:157 stop = band edge -/+ 1 tick (A2-STRUCTURAL-RISK)','operational')
    row('SIRES',b,'objective','ANAT pp.8-10 "an actual HTF objective determines available reward"',
        'a real higher-timeframe objective',f'{F}:158-159 target = opposite edge of the same balance (or the VWAP price on the fade)','operational')
row('SIRES','dom_rejection','effort / no progress','DOM6/DOM7 pp.3-7','arriving aggression makes little progress at a premarked level',
    f'{F}:64,85 effort = >=2 opponent prints, opposing>own, opposing >= previous 5s chunk; no_progress = adverse move <= 2 ticks (A2-FLOW)','operational')
row('SIRES','dom_rejection','DOM confirmation','DOM6/DOM7 pp.3-7','additional opposing participation visible on the ladder',
    f'{F}:72 displayed_defense = any completed depth-one row with the passive side inside the band','operational','depth-one only')
row('SIRES','absorption_reward_retest','reward near origin','ABS pp.5-13','reward by the new controlling side inside the three-tick neighbourhood',
    f'{F}:92,173 reward = chunk last price >= 3 ticks from origin; reward_near_origin = |reward.first-origin| <= 3 ticks','exact')
row('SIRES','absorption_reward_retest','fresh retest','ABS pp.5-13','retest of the rewarded area with renewed defence',
    f'{F}:94-96 reward_retest then renewed (own>opposing and held)','exact')
row('SIRES','absorption_reward_retest','CVD filter','ABS pp.8-13','CVD must support the read',
    f'{F}:163 own_delta = signed sum of all chunk deltas up to the decision; unknown aggressor volume makes it None','operational',
    'the plotted CVD reference/reset is unpublished')
row('SIRES','stop_four_stage','defense','STOP p.10 "Initial defense. Aggression hits the level, volume runs above average, price holds"',
    'volume above average and price holds',f'{F}:85 effort and no_progress and held; "above average" is replaced by >= the previous 5-second chunk','operational')
row('SIRES','stop_four_stage','replenishment','STOP p.10 "My minimum filter is three ticks of replenishment; one or two is the classic fake-out zone"',
    'at least three ticks of replenishment',f'{F}:88 refresh = any later chunk with a depth-one add, opposing>0 and held - no tick count at all','missing',
    'the source-stated three-tick filter appears in no code path and in no A2 assumption')
row('SIRES','stop_four_stage','exhaustion','STOP p.10 "the aggressor\'s volume starts declining and delta turns against them"',
    'declining aggressor volume AND delta turning',f'{F}:90 thinning = opponent mean <= 0.5*defense mean and opposing<defense opposing; the delta-turn half is not tested here','operational')
row('SIRES','stop_four_stage','lift-off / reward','STOP p.12 "two upticks, which is my minimum, two to four, for calling it a reward system"',
    'a 2-4 tick lift-off',f'{F}:98 2*Q <= sign*(last-origin) <= 4*Q','exact')
row('SIRES','stop_four_stage','entry distance','STOP p.13 "the entry itself came six to eight ticks above the absorption, which is far too delayed"',
    'entry close to the confirmation',f'{F}:181 entry_distance_ticks measured; predicate bound 0-2 ticks (A2-FLOW entry_distance_ticks=2)','operational')
row('SIRES','stop_four_stage','account stop','STOP pp.12,14 stated -4R daily stop','respect the -4R daily stop',
    f'{F}:184-185 m.supplied("account") - never present; daily_r_before is in strategy_policy.EXCLUDED under reconstruction','missing','recorded as skipped')
row('SIRES','footprint_confirmed_reaction','delta disagreement','FP9 pp.4-7','candle direction disagrees with executed delta at the level',
    f'{F}:199 (C-O)*delta < 0 on the containing one-minute candle','exact')
row('SIRES','footprint_confirmed_reaction','intrabar POC flip','FP9 pp.4-7','POC relocates within the candle',
    f'{F}:191-197 two snapshots, at +30s and at the candle close, of the max-volume price; flip = directional move between them','inferred',
    'the snapshot clock is a project choice; the source shows a continuous footprint')
row('SIRES','vwap_deviation_fade','deviation band','VWAP pp.3-8','price at a selected deviation of the source VWAP/anchor',
    f'{F}:296 +/-1 SD of the session VWAP, first distinct visit per side (A2-AUCTION-SAMPLE vwap_deviation_sd=1)','inferred')
row('SIRES','vwap_deviation_fade','objective','VWAP pp.3-8','rotation toward VWAP or the named objective',
    f'{F}:159 target = the VWAP price itself','operational')
row('SIRES','ofm_aggressive','catalyst / release / failure','OFM pp.3-13','repeated absorbed effort, attempted squeeze, failure',
    f'{F}:104-112 catalyst = the defense chunk; release = >=3 ticks own-side; failure = back within 1 tick of origin','operational')
row('SIRES','ofm_aggressive','refill and drive retest','OFM pp.6-13;BIG pp.7-14','catalyst reclaim/refill, initiative drive, intervening wicks, defended retest',
    f'{F}:107-109 refill (held + depth-one add), drive (beyond release), retest inside the drive range','operational')
row('SIRES','ofm_aggressive','gamma regime','BIG pp.14-18;GEX pp.4-20 short-gamma-only',
    'the aggressive OFM branch is short-gamma only',
    f'{F}:247-256 m.supplied("gamma") - never present; reconstruct mode substitutes strategy_options.gamma_at (BS midquote IV, r=q=0, call+/put-, prior-date OI)','inferred',
    'EXTERNAL[gamma] records the omission; the inventory sign is an assumption')
row('SIRES','ofm_passive','dying tape','OFM p.14 "The squeeze fails with no aggressive orders at the failure at all: the speed of tape just dies"',
    'tape speed dies, no aggressive orders at the failure',
    f'{F}:221-222 tape_died = failure.count < 0.5*release.count; no_aggression = failure.opponent_count==0','inferred',
    'the 50% pace threshold is a project constant; Speed of Tape (10) settings are unpublished')
row('SIRES','ofm_passive','entry and stop','OFM p.14 "Entry above the buyers, stop below the aggression, scalp target in the 1R to 3R zone"',
    'entry above the buyers, stop below the aggression, 1R-3R target',
    f'{F}:223 entry_above_buyers = entry>band high; stop_below_aggression = stop<band low; no 1R-3R objective is bound','missing',
    'the source objective band is not implemented')
row('SIRES','clean_squeeze','no prior failure','CONT p.11;OFM p.5','fast release with no earlier failed squeeze',
    f'{F}:228 False if a failure stage exists, else True only when absence is certified','exact')
row('SIRES','clean_squeeze','absorbed pullback','CONT p.11','opposing aggression absorbed on the first pullback',
    f'{F}:229 pullback.opposing>own and held','operational')
row('SIRES','balance_failure_fade','unpaid aggression','BIG pp.14-15,18','aggression at the extreme repeatedly goes unpaid',
    f'{F}:234-236 defense stage, then release as "left", failure as "retest", retest.no_progress','operational')
row('SIRES','balance_failure_fade','objective','BIG pp.14-15,18 "fade toward where the opposite side previously had control"',
    'previous opposite control',f'{F}:236 target_is_prior_opposite_control = target in (ref.low, ref.high) - restates line 158','inferred','vacuous')
row('SIRES','defended_band_continuation','prior band control','NYAM pp.4-5;K18 pp.7,11,14','prior defence/control is visible at the band',
    f'{F}:312-318 a full dom_rejection episode is run on contacts[0] and its defense stage is required','operational')
row('SIRES','defended_band_continuation','executed aggression vs thesis','CONT pp.4-10;ANAT p.7','real participation AND the control side matching the thesis',
    f'{F}:241 executed_aggression and control_side_matches_thesis are bound to the same own_delta value','mismatch',
    'two distinct source conditions collapse to one operand')
row('SIRES','microbalance_break','microbalance','K2345 pp.4-7','a small price balance inside the established directional auction',
    f'{F}:329-333 a later balance with an earlier wider balance; A2-BALANCE 4 alternating confirmed pivots, 300s bars, 25% edge tolerance','operational')
row('SIRES','microbalance_break','thesis direction','K2345 pp.4-7 "Within the established directional auction ... price shows strength and breaks it"',
    'the break must run with the established direction',
    f'{F}:337 selects the trigger by sign(C-boundary)>0 and {F}:346 binds breakout_in_thesis_direction to the same expression','mismatch','C6')
row('SIRES','microbalance_break','invalidation','K2345 p.7 "use the opposite side of that structure for risk"',
    'stop behind the microbalance',f'{F}:340,347 stop = opposite edge -/+ 1 tick; stop_behind_microbalance restates it','inferred','vacuous')
row('SIRES','kg1_retest','KG1 level','NYAM pp.8-9','the source KG1 level',
    f'{F}:277-281 m.supplied("kg1") - never present; reconstruct mode substitutes strategy_options.key_gamma_reference (largest |signed gamma| strike mapped through NQ/QQQ)','inferred',
    'EXTERNAL[kg1]; the wiki states this is not the literal KG1 formula')
row('SIRES','kg1_retest','retest / confirmation','NYAM pp.8-9','an actual same-band retest with aggressive confirmation',
    f'{F}:244 kg1_retest=True literal; aggression_confirms = own_delta','mismatch','the retest operand is a constant')
for b,anc,note in (('case_description','FORMULAS M05;K18 pp.5-6','early pre-confirmation attempts'),
                   ('management','RD pp.4-5;C2 p.5;K18 pp.8-14','breakeven/trail/partials'),
                   ('reentry','STOP pp.6,14-15;ANAT pp.7,10','fresh confirmation after a stop-out')):
    row('SIRES',b,'all stages',anc,note,f'{P}:251 scan_supplied_unit; no supplied record exists, only an external_operand omission','missing','recorded as skipped')
json.dump(R,open('rows_part2.json','w'));print(len(R))
