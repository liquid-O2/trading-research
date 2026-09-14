import json
R=[]
def row(m,b,stage,anchor,src,code,cls,note=''):
    R.append({'method':m,'branch':b,'stage':stage,'source_anchor':anchor,'source_statement':src,
              'code':code,'class':cls,'note':note})

S='historical_price_scanners.py'; A='historical_auction_scanners.py'; F='historical_flow.py'; P='historical_process_scanners.py'

# ---------------- JJ-TBR ----------------
JT=[('judas_outbound','TBR pp.8-10'),('judas_reversal','TBR pp.8-11,27-29'),('single_extended','TBR pp.12-14,24'),
    ('single_purged','TBR pp.12-15'),('internal_rotation','JR pp.3,38-43;TBR p.12'),('extension_reaction','TBR pp.20-21'),
    ('other_session','TBR p.7,36'),('timed_pzone_reversal','JR pp.16-18,53-55')]
for b,anc in JT:
    row('JJ-TBR',b,'freeze the range','TBR p.7-8 "Time range selection: 6:00am - 9:00am"',
        '06:00-09:00 formation, H/L/EQ/quadrants/open/close frozen',
        f'{S}:46 scan_jumbo formations=[(06:00,09:00)]; m.range -> span(); range_frozen=_known(ref) {S}:135','exact')
    row('JJ-TBR',b,'structural invalidation','TBR pp.24-29 "midpoint stop/entry vs conservative boundary stop"',
        'stop at the controlling structure; the two p.29 midpoint captions conflict',
        f'{S}:114/116 stop=range edge -/+ 1 tick (outbound) or O056 C2 extremum (all other branches); A2-STRUCTURAL-RISK outside_structure_ticks=1','operational')
row('JJ-TBR','judas_outbound','context/direction','TBR pp.12,16-24','read overnight size/balance, purge, open vs prior value, news, behaviour',
    f'{S}:20-21 direction = sign(pre_0600_0900_close - overnight_open); nothing else consumed; A2-CONTEXT','inferred',
    'news, prior value/range, RVOL and behaviour never reach a branch operand')
row('JJ-TBR','judas_outbound','entry','TBR p.8 "we position ourselves right at the open"',
    'enter at the 09:30 cash open, participate in the judas move',
    f'{S}:99-113 first execution timestamp batch at 09:30:00-09:30:01; single-price batch else published O','exact')
row('JJ-TBR','judas_outbound','objective','TBR p.8 "towards the projections of the range where the reversal will take place"',
    'range projections; p.8 names the -0.5 projection for the reversal',
    f'{S}:88 target = edge +/- 0.5*width (A2-TBR-PROJ exhaustion=.5)','operational')
row('JJ-TBR','judas_outbound','exit window','TBR p.8 "have positions closed as we reach the reversal window"',
    'close by 09:40-09:50', f'{S}:145 exit_window_recorded=True (literal); A2-TBR-CLOCK outbound_end=09:40 never read by the scanner','missing',
    'no exit clock is evaluated; the operand is a constant')
row('JJ-TBR','judas_reversal','sweep','TBR p.8 "the judas trades from 9:30 to the reversal window"',
    'the false breakout precedes the 09:40-09:50 reversal window',
    f'{S}:71,89-90 the sweep itself is searched only in m.bars(09:40,09:50)','mismatch','C1')
row('JJ-TBR','judas_reversal','confirmation','TBR pp.27-31 "2/3/5-minute orderblocks or rejection blocks"',
    'the source episode\'s own OB/rejection-block/absorption signature',
    f'{S}:26-40 _ob(): one fixed 180s O056 C1/C2/C3 sweep+CISD triple; A2-TBR-CLOCK confirmation_seconds=180','operational',
    'rejection blocks, absorption candles, BigTrades and footprint confirmations are never alternatives')
row('JJ-TBR','judas_reversal','objective','TBR pp.8-11 "levels of interest will be the mean reversal levels or -0.5 projection"',
    'mean reversal level / -0.5 projection, then higher projections',
    f'{S}:80 target = opposite completed range edge; objective_is_opposing_draw {S}:149 restates it','mismatch',
    'the source names the -0.5 projection and the mean reversal area; the code targets the opposite edge only')
for b in ('single_extended','single_purged','internal_rotation'):
    row('JJ-TBR',b,'entry location','TBR p.12 "the EQ or quadrants become our levels on interest"',
        'EQ or 0.25/0.75 quadrants',f'{S}:82-83 location=[(low+high)/2]*2; A2-TBR-PROJ internal=[.25,.5,.75] is never read','missing','C5')
    row('JJ-TBR',b,'action window','TBR p.12 "you want to be in the trade before 10am ... after 10am all interest in being in a position is not longer present"',
        'entries before 10:00',f'{S}:72 action_end forced to 16:00','mismatch','C2')
row('JJ-TBR','single_extended','context','TBR p.12 "taking in consideration the size of the overnight range"',
    'extended overnight range',f'{S}:129 extended = overnight_width >= prior RTH width (A2-CONTEXT wide_ratio=1)','operational')
row('JJ-TBR','single_purged','context','TBR p.12 "every significant overnight liquidity has been purged"',
    'overnight stop hunts already removed the liquidity',
    f'{S}:156-161 any bar after the prior RTH range is known that exceeds prior H/L, AND width<=0.5*prior width','operational')
row('JJ-TBR','single_purged','window use','TBR p.12 "discarding the 9:40 9:50 window ... rather use it as continuation where i would look to add"',
    '09:40-09:50 is an add window, not a reversal',f'{S} no 09:40-09:50 handling on this branch; expansion_policy=True literal {S}:163','missing')
row('JJ-TBR','internal_rotation','objective','JR p.3 "EQ is a location; EV and EQ are different targets"',
    'nearer named rotation objective',f'{S}:166 objective_is_named_rotation_target = target in (low,high) - restates line 80','inferred','vacuous')
row('JJ-TBR','extension_reaction','location','TBR pp.20-21 1.33-1.66 extension area',
    'the 1.33-1.66 projection of the parent range',
    f'{S}:85 [low-0.66W, low-0.33W] long / [high+0.33W, high+0.66W] short == 1.33-1.66 of parent width','exact')
row('JJ-TBR','extension_reaction','objective','TBR pp.20-21;JR pp.23-26 "the still-owed objective"',
    'the remaining directional objective',f'{S}:170 target_unused = opposite edge not traded between formation end and touch','operational')
row('JJ-TBR','other_session','clock','TBR p.7 lists 20:00-20:30, 00:00-00:30, 03:00-03:30, 09:30-10:00, 10:00-10:30, 12:00-12:30, 15:00-15:30',
    'seven published formations besides 06:00-09:00',f'{S}:49-52 setting(tbr_sessions)[other] enumerates exactly those seven','exact')
row('JJ-TBR','other_session','case verification','TBR p.36;JR pp.46,50-51 "apply the selected geometry ... to the observed London or later-session case"',
    'a source-known clock and a source case are required',f'{S}:176 source_clock_verified=True and source_case_verified=True, both literals, kind=policy','mismatch',
    'the wiki requires a source-known case; the operand is a constant')
row('JJ-TBR','other_session','action horizon','TBR p.7','no published action horizon',
    f'{S}:52 end+60 minutes (A2-TBR-CLOCK other_action_minutes=60)','inferred')
row('JJ-TBR','timed_pzone_reversal','zone','JR pp.16-18,53-55 time-anchored P-zones',
    'the actual time-anchored P-zone band and its named destination',
    f'{S}:53-61 m.supplied("pzone") - never present; reconstruct mode substitutes strategy_pzones.inferred_pzones (02:00/09:00/10:00 anchors, 70th/80th pct, 500 sessions)','inferred',
    'EXTERNAL[pzone] records the omission; the inferred model is labelled inferred_model')
row('JJ-TBR','management','all stages','TBR pp.24,36-37;FORMULAS M01','partials, breakeven, trailing, 3 failed attempts, -50% after failure',
    f'{P}:251 scan_supplied_unit - no supplied record exists, branch emits only an external_operand omission','missing','recorded as skipped')

# ---------------- GB-FAIL ----------------
GB=[('nyam_box','GB pp.23,30-35'),('previous_hour','GB pp.27,35'),('asia_tdo_case','GB pp.27,32-39'),
    ('prior_day_level','GB pp.25,33'),('prior_week_level','GB pp.33,38'),('prior_month_level','GB p.33'),
    ('cash_open_reclaim_case','GB p.40')]
for b,anc in GB:
    row('GB-FAIL',b,'reference',anc,'finish the selected box or use a known prior level; NYAM 09:00-10:00 cannot be traded before 10:00',
        f'{S}:189-200 _gb_refs; nyam 09:00-10:00, hours 08..14, asia 20:00-00:00, prior day/week/month span, cash open O','exact')
    row('GB-FAIL',b,'sweep','GB p.31 "sweep -> reclaim -> opposing liquidity"','sweep above and fail back below (short) / below and reclaim (long)',
        f'{S}:215-217 first bar strictly beyond the boundary, then exact_contact with strict above/below','exact')
    row('GB-FAIL',b,'confirmation','GB p.25 "I wait for the 5 min close back below the PDL after sweeping above it"',
        'wait for a completed five-minute close back through the level',
        f'{S}:219-223 only the single aligned five-minute candle that contains the sweep is read','mismatch','C3')
    row('GB-FAIL',b,'invalidation','GB p.25 "low risk entry on any retracement with stops above PDL"',
        'stop beyond the swept level / sweep extreme',f'{S}:227 stop = sweep-path extreme +/- 1 tick','operational')
    row('GB-FAIL',b,'objective','GB pp.25,30-39 "opposing liquidity"','opposite box edge, 50%, TDO, prior/session extremes or NWOG as actually named',
        f'{S}:228 target = opposite edge of the reference; cash-open case uses boundary + 0.5*(boundary-low)','operational')
    row('GB-FAIL',b,'context/bias','GB pp.23,38-40 directional read',
        'establish the contextual direction before the sweep',
        f'{S}:229-230 bias_recorded = a 06:00->begin range exists and is known before the trigger; direction itself is never compared with the side','mismatch',
        'bias_recorded carries availability only, not a direction; a short and a long at the same level both pass')
row('GB-FAIL','asia_tdo_case','TDO confirmation','GB pp.21,27,32-39 midnight true-day open','the midnight opening price confirms the side',
    f'{S}:233-241 tdo = O of the 00:00-00:01 bar; source_tdo_close_confirmed = sign(close-tdo)>0','exact')
row('GB-FAIL','nyam_box','golden pocket','GB p.25 "I use the 50% -61.8% fib retracement as my golden pocket zone"',
    'optional 50-61.8% retracement of the measured impulse',
    f'{S}:242 pocket_required=False literal; impulse_known_at / touch_in_measured_pocket are never bound to an observation','missing',
    'the predicate\'s pocket clause is inert on every branch')
row('GB-FAIL','nyam_box','retracement entry','GB p.25 "once closed below, low risk entry on any retracement"',
    'enter the reclaim or its retracement',f'{S}:242 retracement_entry=False literal on every branch except mss_fvg_refinement','missing')
row('GB-FAIL','mss_fvg_refinement','annotation','GB p.31 post 1991589280142315537 "Sweep of 9-10 highs -> failed breakout -> MSS + FVG entry"',
    'later MSS+FVG annotation of a completed parent reclaim',
    f'{S}:256-279 three aligned 2-minute candles after the parent decision; gap = c.L>a.H; structure = c.C beyond max(a.H,b.H); A2-MSS-FVG horizon 30 min','operational')

# ---------------- GB-VWAP ----------------
row('GB-VWAP','source_long','reference','GB p.33 "Broke & closed above London + Asia highs"',
    'both finished session highs',f'{S}:283-287 asia 20:00-00:00, london 02:00-05:00 (A2-GB-CLOCK); boundary = max of both highs','operational',
    'exact London bounds are not published; the clock is a labelled choice')
row('GB-VWAP','source_long','breakout','GB p.33','price breaks and closes above both highs',
    f'{S}:288 first completed 5-minute bar with C > max(asia,london) high','exact')
row('GB-VWAP','source_long','confirmation','GB p.33 "retraced into VWAP -> long entry"','retrace into the contemporaneous VWAP',
    f'{S}:293-300 first later minute bar whose [L,H] contains the session VWAP snapshot at its start; 60-minute horizon','operational')
row('GB-VWAP','source_long','continuation context','GB p.33','the close above both highs is the continuation context',
    f'{S}:308 sets continuation_context=True, then {S}:314 REBINDS it with the retest-absence answer when no retest is found','mismatch',
    'D1, already proven in reviews/phase1-code-review-2026-09-14 (repro_d1.py); not re-proved here')
row('GB-VWAP','source_long','VWAP reset','GB p.33 / wiki "vwap_reset_verified is required for an author-faithful automatic check"',
    'the platform VWAP reset must be verified',f'{S}:309 vwap_reset_verified=True literal; A2-GB-CLOCK vwap_reset=18:00 is an assumption','mismatch',
    'the operand designed as the fidelity gate is a constant')
row('GB-VWAP','source_long','invalidation/objective','GB p.33 "30-point stop", 150-point result',
    'source stop of 30 points; target unpublished',f'{S}:303 stop = retest bar low - 1 tick; no target bound (target=None)','operational')

# ---------------- GB-SCALP ----------------
for b,post in (('bearish_small_scalp','GB p.40 post 2095257805242446135'),('bullish_discount_pullback','GB p.40 post 2098075540607410229')):
    row('GB-SCALP',b,'directional read',post,'pre-existing bearish bias / NYAM-direction long',
        f'{P}:60-69 one confirmed 1-minute pivot pair inside 06:00-09:30 (short) or 09:00-10:00 (long)','inferred')
    row('GB-SCALP',b,'pullback',post,'favourable pullback into discount/premium',
        f'{P}:71,77 first_contact on [eq,hi] or [lo,eq]; source_directional_pullback_observed restates that selection','inferred','vacuous')
    row('GB-SCALP',b,'entry trigger',post,'not published',f'{P}:84 automatic_entry_admission=None; branch automatic_admission returns a literal NULL','missing','recorded as skipped')
    row('GB-SCALP',b,'size / management',post,'small exposure and limited management',
        f'{P}:78-79 from m.supplied("scalp_process") - never present; both fields are in strategy_policy.EXCLUDED','missing','recorded as skipped')
row('GB-SCALP','automatic_admission','entry rule','GB p.40','no complete repeatable entry is disclosed',
    f'{P}:253-257 returns an explicit external_definition omission','exact','honest NULL')
json.dump(R,open('rows_part1.json','w'))
print(len(R))
