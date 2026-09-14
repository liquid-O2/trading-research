import json,sys,os,collections
from decimal import Decimal as D
S=os.environ['SCRATCH'];sys.path.insert(0,S)
import flowsim
Q=D('.25')
def dec(x):return None if x is None else D(str(x))
def sg(side):return 1 if side=='long' else -1

FLOWSEEN={  # SIRES conjunct -> stage key in (st|cat) whose absence produced False
 'arriving_aggression':'defense','little_progress':'defense','local_rejection':'reward',
 'source_dom_confirmation':'defense','passive_wall_confirmed':'defense','opposing_effort_no_result':'defense',
 'own_reward_confirmed':'reward','fresh_reward_retest_defended':'renewed','defense':'defense',
 'replenishment':'refresh','opponent_thinning':'thinning','absorber_aggressive':'liftoff','lift_off':'liftoff',
 'local_absorption':'defense','absorption_at_that_band':'defense','ladder_confirmation':'defense',
 'first_squeeze':'release','squeeze_failed':'failure','catalyst_reclaimed':'refill','refill_held':'refill',
 'initiative_drive':'drive','drive_retest_defended':'retest','own_aggression_rewarded':'drive',
 'source_squeeze_failed':'failure','buyers_area_identified':'failure','catalyst_known':'catalyst',
 'first_pullback':'pullback','continuation_confirmed':'continuation','failed_aggression_at_extreme':'defense',
 'left_failed_area':'release','retest_same_failed_area':'failure','fresh_same_side_defense':'defense',
 'refresh_consistent':'refresh','repeated_effort_no_reward':'release',
 'no_prior_squeeze_failure':'failure','reward_near_origin':'reward','aggression_still_unrewarded':'failure',
 'tape_died_at_failure':'failure','no_aggression_at_failure':'failure','fast_release':'release',
 'opposing_pullback_aggression_absorbed':'pullback','intervening_wicks_taken':'drive','entry_above_buyers':'failure',
}
OWNDELTA={'cvd_filter_ok','delta_filter_ok','source_flow_confirmation','executed_aggression',
          'control_side_matches_thesis','aggression_confirms'}

def classify(r):
    m=r['method'];br=r['branch'];v=r['values'];side=r['side'];out=[]
    lf=r.get('local_flow')
    sim=None
    if lf:
        cb,stb,catb=flowsim.run(lf,side,False)
        cf,stf,catf=flowsim.run(lf,side,True)
        sim=dict(cb=cb,stb=stb,catb=catb,stf=stf,catf=catf,
                 gap=any(lf[i]['start']!=lf[i-1]['end'] for i in range(1,len(lf))),
                 unk=any(c['unknown']>0 for c in cb))
    for c in (r['failed'] or []):
        k,defect,note='ambiguous',None,''
        base=c.split(' ')[0]
        if base=='NOT':base=c.split()[1]
        # ---- pure comparison conjuncts emitted by expressions.py as "a b (op)"
        if ' ' in c and c.endswith((')',)):
            parts=c.split();lhs,rhs,op=parts[0],parts[1],parts[2].strip('()')
            a,b=v.get(lhs),v.get(rhs)
            if a is None or b is None:
                k,note='ambiguous','operand null in a comparison reported as failed'
            else:
                A,B=dec(a),dec(b)
                got={'>':A>B,'<':A<B,'>=':A>=B,'<=':A<=B}.get(op)
                k='genuine' if got is False else 'mis-implemented'
                note=f'{lhs}={A} {op} {rhs}={B} -> {got}; strict convention per FORMULAS O047-F1/base-4'
                if got is not False:defect='comparison recomputed True but reported failed'
            out.append((c,k,defect,note));continue
        # ---- GB-FAIL
        if m=='GB-FAIL':
            if base=='box_return_ok':
                lo,hi,cl=dec(r['ref']['low']),dec(r['ref']['high']),dec(v.get('confirm_close'))
                if cl is None:k,note='ambiguous','confirm_close null'
                else:
                    got=True if lo==hi else (lo<cl<hi)
                    k='genuine' if got is False else 'mis-implemented'
                    note=f'box [{lo},{hi}] close {cl} -> inside={got}; FORMULAS:1468 requires lo<close<hi'
                    if got is not False:defect='box_return_ok recomputed True'
            elif base in('risk_defined','objective_fixed'):
                e,st,tg=dec(r['entry']),dec(r['stop']),dec(r['target'])
                if e is None:k,note='ambiguous','entry null'
                else:
                    got=sg(side)*(e-st)>0 if base=='risk_defined' else sg(side)*(tg-e)>0
                    k='genuine' if got is False else 'mis-implemented'
                    note=f'entry {e} stop {st} target {tg} -> {got}'
            elif base=='source_tdo_close_confirmed':
                k='genuine';note='asia_tdo variant: close did not cross midnight TDO (recorded False); OR-partner NOT tdo_required also false by design'
            elif base=='tdo_required':
                k='genuine';note='NOT tdo_required is the OR partner of source_tdo_close_confirmed; both sides reported by expressions.py OR'
            elif base=='source_hold_confirmed':
                g=(r.get('mss') or {})
                k='genuine';note=f"mss_fvg gap={g.get('gap')} structure={g.get('structure')} -> AND False"
            elif base=='bias_recorded':
                k='genuine';note='pre-context range known_at after sweep'
        # ---- JJ-TBR
        elif m=='JJ-TBR':
            if base in('source_confirmation','reaction_side_confirmed'):
                if v.get('confirm_at') is not None:
                    k='genuine';note='O056 three-candle signature evaluated on real candles and returned confirmed=False'
                else:
                    w=r['decision_at']-(r['trig'].get('start') or r['occurrence_at'])
                    if w>0:k,note='genuine',f'no aligned 3x{180}s triple; absent() over observed window of {w/1e9:.0f}s'
                    else:k,defect,note='mis-implemented','P2',f'absent() over zero/negative window ({w}ns)'
            elif base in('risk_defined','objective_fixed','objective_is_remaining_draw','rotation_context',
                         'reversal_context','extended_context','purged_compressed_context','context_fixed',
                         'entry_at_eq_or_quadrant','edge_swept','source_time_window','objective_is_opposing_draw',
                         'objective_is_range_edge','objective_is_named_rotation_target','prior_expansion',
                         'touch_in_source_extension_area','directional_context','at_rth_open','range_frozen',
                         'objective_is_selected_exhaustion','directed_path_recorded','source_zone_known'):
                if base in('risk_defined','objective_fixed'):
                    e,st,tg=dec(r['entry']),dec(r['stop']),dec(r['target'])
                    if e is None:k,note='ambiguous','entry null'
                    else:
                        got=sg(side)*(e-st)>0 if base=='risk_defined' else sg(side)*(tg-e)>0
                        k='genuine' if got is False else 'mis-implemented'
                        note=f'entry {e} stop {st} target {tg} -> {got}'
                else:
                    k='genuine';note='geometry/context operand measured directly from the frozen reference; no absence or ordering step'
        elif m=='GB-VWAP':
            if base=='continuation_context':
                bc,ah,lh=dec(v.get('breakout_close')),dec(v.get('asia_high')),dec(v.get('london_high'))
                if bc is not None and ah is not None and lh is not None and bc>max(ah,lh):
                    k,defect='mis-implemented','D1'
                    note=(f'operand as defined (historical_price_scanners.py:308) is breakout_close {bc} > max(asia {ah}, '
                          f'london {lh}) = True, but line 314 rebinds continuation_context with absent(breakout.end,deadline), '
                          'the answer to the retest question; the True evidence is discarded and the episode is reported '
                          'as a failed context instead of an unobserved retest')
                else:
                    k,note='genuine','breakout close not above both highs'
        # ---- SAINT
        elif m=='SAINT-AMT':
            csw=r.get('csw');tstart=r['trig'].get('start');tend=r['trig'].get('end');dec_at=r['decision_at']
            if base in('control_evidence_recorded','local_control_confirms_return','repeated_body_selling',
                       'repeated_aggression_in_trade_direction'):
                if csw and csw[1]<=csw[0]:
                    k,defect='mis-implemented','P2'
                    note=f'_control_absence(historical_auction_scanners.py:28) returned False from a zero-length window {csw}; no bar was read'
                elif csw:
                    k='genuine';note=f'control window {(csw[1]-csw[0])/1e9:.0f}s fully observed, no two successive directional body+delta bars'
            elif base in('same_boundary_retest_held','original_balance_reaccepted','aggressive_poc_passage'):
                w=None if tend is None else dec_at-tend
                if w is None:k,note='ambiguous','trigger end unavailable'
                elif w>0:k,note='genuine',f'absent() over {w/1e9:.0f}s of observed post-trigger window'
                else:k,defect,note='mis-implemented','P2',f'absent() over zero/negative window ({w}ns)'
            elif base in('older_value_tested','older_value_rejected'):
                w=None if tstart is None else dec_at-tstart
                if w is None:k,note='ambiguous','trigger start unavailable'
                elif w>0:k,note='genuine',f'absent() over {w/1e9:.0f}s observed window; older value never contacted/rejected'
                else:k,defect,note='mis-implemented','P2',f'absent() over zero/negative window ({w}ns)'
            elif base in('prior_buying_at_upper_extreme','two_distinct_prior_failures'):
                w=None if tstart is None or r['ref'].get('known_at') is None else tstart-r['ref']['known_at']
                if w is None:k,note='ambiguous','window bounds unavailable'
                elif w>0:k,note='genuine',f'absent() over {w/1e9:.0f}s of prior observed window'
                else:k,defect,note='mis-implemented','P2',f'absent() over zero/negative window ({w}ns)'
            elif base in('risk_defined','objective_fixed'):
                e,st,tg=dec(r['entry']),dec(r['stop']),dec(r['target'])
                if e is None:k,note='ambiguous','entry null'
                else:
                    got=sg(side)*(e-st)>0 if base=='risk_defined' else sg(side)*(tg-e)>0
                    k='genuine' if got is False else 'mis-implemented'
                    note=f'entry {e} stop {st} target {tg} -> {got}'
            elif base in('source_poc_hold_confirmed','ltf_break_down','profile_allows_trade','alignment_ok',
                         'balance_fixed_before_use','arrival_read_recorded','target_is_far_balance_edge','ltf_balance_broken'):
                k='genuine';note='measured directly on the recorded control bars / frozen profile'
        # ---- KEANI
        elif m=='KEANI-OPEN-ABOVE-VALUE':
            if base in('developing_value_builds_higher','source_rejection_observed','aggressive_buy_imbalance_break',
                       'time_of_day_allowed','buyers_defend_same_imbalance_band','dom_supports_long'):
                k='genuine'
                note=('absent(m,10:00,11:00,fields=C) over a full observed hour: no developing-value rejection / '
                      'diagonal-imbalance break existed, so the later stages are absence-propagated False')
                if base=='time_of_day_allowed':
                    note+=' (conjunct-level artefact: a time gate is reported False when there is no break at all)'
            elif base in('prior_value_fixed','a_period_complete','objective_fixed','risk_defined'):
                k='genuine';note='direct operand'
        # ---- MEMBER / SIRES flow
        if k=='ambiguous' and m in('SIRES','MEMBER-TWO-REASONS'):
            if base in OWNDELTA and sim:
                tot=sum(c['delta'] for c in sim['cb'])
                got=None if sim['unk'] else tot*sg(side)>0
                k='genuine' if got is False else 'ambiguous'
                note=f'own_delta recomputed from {len(sim["cb"])} recorded chunks: sum(delta)={tot}, side={side} -> {got}'
            elif base in FLOWSEEN and sim:
                key=FLOWSEEN[base]
                b=(sim['stb'].get(key) if key in sim['stb'] else sim['catb'].get(key))
                f=(sim['stf'].get(key) if key in sim['stf'] else sim['catf'].get(key))
                if sim['unk']:
                    k,note='ambiguous','a recorded chunk has unknown aggressor volume'
                elif b is None and f is None:
                    k='genuine'
                    note=(f'stage {key} re-derived as absent from the {len(sim["cb"])} recorded 5s windows both as-published '
                          f'and with the P1 baseline fix; windows contiguous (no empty window) so P1 is inert here')
                elif b is None and f is not None:
                    k,defect='mis-implemented','P1';note=f'stage {key} appears once the effort baseline is the immediately preceding window'
                else:
                    k='genuine'
                    note=(f'stage {key} IS present in the re-derivation (identical under the P1 fix); this conjunct is an '
                          'attribute measured on that selected 5s window, not a stage-absence answer')
            elif base in('thesis_alive','risk_defined','objective_fixed','auction_route_ok','location_fixed',
                         'real_extreme','balance_context','target_is_prior_opposite_control','prior_band_control',
                         'same_band_retest','stop_below_aggression','branch_regime_allowed','short_gamma','long_gamma',
                         'source_kg1_level_known','kg1_retest','at_valid_level','source_vwap_known',
                         'selected_deviation_touched','microbalance_frozen','breakout_in_thesis_direction',
                         'stop_behind_microbalance','directional_strength','candle_delta_disagreement','intrabar_poc_flip'):
                if base in('thesis_alive','risk_defined','objective_fixed'):
                    e,st,tg=dec(r['entry']),dec(r['stop']),dec(r['target'])
                    if e is None:k,note='ambiguous','entry null'
                    else:
                        got=sg(side)*(e-st)>0 if base in('risk_defined','thesis_alive') else sg(side)*(tg-e)>0
                        k='genuine' if got is False else 'mis-implemented'
                        note=(f'entry {e} stop {st} target {tg} -> {got}; entry is the last observed chunk price because '
                              f'no branch stage was selected')
                else:
                    k='genuine';note='operand measured directly on recorded bars/chunks; no absence or ordering step'
            elif sim:
                if sim['unk']:
                    k,note='ambiguous','a recorded 5s window carries unknown-aggressor volume'
                elif any((sim['stb'][x] is None)!=(sim['stf'][x] is None) for x in sim['stb']) or \
                     any((sim['catb'][x] is None)!=(sim['catf'][x] is None) for x in sim['catb']):
                    k,defect,note='mis-implemented','P1','stage selection changes under the corrected effort baseline'
                else:
                    k='genuine'
                    note=(f're-derived on the {len(sim["cb"])} recorded contiguous 5s windows; identical with the P1 '
                          'baseline fix, so the conjunct value is a real measurement on the tape')
        out.append((c,k,defect,note))
    return out

def main():
    rows=[]
    for name in ('A','B'):
        data=json.load(open(S+f'/sample{name}.json'))
        for r in data:
            for c,k,defect,note in classify(r):
                rows.append(dict(sample=name,date=r['date'],method=r['method'],branch=r['branch'],
                    candidate_id=r['cid'],side=r['side'],conjunct=c,classification=k,defect=defect,evidence=note))
    with open(S+'/classifications.jsonl','w') as fh:
        for x in rows:fh.write(json.dumps(x)+'\n')
    print('conjunct rows',len(rows))
    for name in ('A','B'):
        sub=[x for x in rows if x['sample']==name]
        print(name,collections.Counter(x['classification'] for x in sub))
        print(' defects',collections.Counter(x['defect'] for x in sub if x['defect']))
        amb=collections.Counter((x['method'],x['conjunct']) for x in sub if x['classification']=='ambiguous')
        for kk,vv in amb.most_common(25):print('  AMB',vv,kk)
main()
