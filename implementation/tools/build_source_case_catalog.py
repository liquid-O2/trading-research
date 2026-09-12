#!/usr/bin/env python3
"""Freeze reviewed source facts without turning illustration times into fills."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'implementation/reports/phase1-live/methods/charts/full-audit-sources.json'
OUT = ROOT / 'implementation/src/trading_research/research/method_pack/source_cases_v2.json'
SOURCES = {s['key']: {k:s[k] for k in ('path','sha256','pages')}
           for s in json.loads(AUDIT.read_text())['sources']}

def setting(value, refs, reason, status='fact'):
    return dict(value=value,status=status,source_refs=refs,reason=reason)

def unknown(refs, reason):
    return setting(None,refs,reason,'unknown')

CONFIGS = {}
def config(key, author, scope, settings):
    CONFIGS[key] = dict(configuration_id=key,version='2.0.0',author=author,scope=scope,settings=settings)

config('jumbo-published-geometry','Jumbo',['M01','O005','O014','O015','O056','O058'],{
 'range_clock':setting(['06:00','09:00','America/New_York'],['TBR:4'],'Published base range; dated per session.'),
 'orderblock_bar_minutes':setting([2,3,5],['TBR:27'],'Permitted execution timeframes; the examples on pages 27 and 28 are explicitly three minutes.'),
 'absorption_body_max':setting('0.6',['TBR:35'],'Published body/range maximum.'),
 'absorption_volume_min':setting('1.5',['TBR:35'],'Published volume/14-period average minimum.'),
 'absorption_history':setting(14,['TBR:35'],'Exactly fourteen configured complete volume members are required.'),
 'profile_va_policy':unknown(['JR:4','JR:41'],'Separate profile figures do not recover platform expansion/tie construction.')})
config('jumbo-sessionstat','Jumbo',['O017'],{
 'platform':setting('TradingView',['SS:7'],'The source describes bar_index and timestamp detection.'),
 'timeframe_dependence':setting({'below_2_minutes':'levels may differ by design','below_5_minutes':'price and extending-bar differences possible','recommendation':'above 2-3 minutes except 1h/15m non-custom sessions'},['SS:7'],'Each comparison must retain timeframe, version, and session-detection configuration.'),
 'engine':unknown(['SS:7'],'Descriptions of boundary dependence do not disclose the statistical engine.')})
config('gb-nov20-sweep','Green Bird',['M02','GB-FAIL-2025-11-20'],{
 'bar_minutes':setting(2,['GB:43'],'Toolbar and chart header both identify the figure timeframe.'),
 'display_symbol':setting('MNQZ2025',['GB:43'],'Micro E-mini source display; acquired NQZ5 is only a price comparison.'),
 'entry_sequence':setting(['high_sweep','observed_short_position'],['GB:43'],'Position line at 25301.75 sits in the swept-high area.'),
 'observed_position_price':setting('25301.75',['GB:43'],'Visible short-position line, not an exchange fill record.'),
 'mss_fvg_role':setting('later_annotation',['GB:43'],'Subsequent MSS/FVG drawings do not become this entry prerequisite.'),
 'fill_time':unknown(['GB:43'],'Screenshot supplies no exact fill timestamp or complete execution ledger.')})
config('gb-vwap-continuation','Green Bird',['M03','GB-VWAP-2026-02-24'],{
 'entry_sequence':setting(['close_above_london_and_asia_highs','later_vwap_retrace','long'],['GB:33'],'Continuation reply states this sequence.'),
 'stop_points':setting('30',['GB:33'],'Source example stop distance; no monetary tick value inferred.'),
 'reset':unknown(['GB:33'],'Source post does not disclose the VWAP reset.'),
 'price_basis':unknown(['GB:33'],'Source does not disclose trade or bar price basis.'),
 'asia_london_windows':unknown(['GB:33'],'Named sessions are visible; their exact clock settings are not published.'),
 'prior_comparison':setting({'reset':'previous 18:00 America/New_York','basis':'HLC3','asia':['20:00','00:00'],'london':['02:00','05:00']},['GB:33'],'Frozen prior reconstruction choice, not an identified author setting. No new search.', 'inference')})
config('gb-discretionary-scalp','Green Bird',['M04'],{
 'bearish_case':setting({'bias':'bearish','side':'short','reported_points':[20,30],'size':'no increase'},['GB:40'],'September 2 post describes limited short scalps; it does not supply fills or a general target rule.'),
 'bullish_case':setting({'side':'long','location':'discount pullback','size':'smaller'},['GB:40'],'September 10 post describes the long loop in NYAM direction.'),
 'automatic_entry':unknown(['GB:40'],'Neither post discloses a repeatable trigger, selected impulse, full invalidation or exit algorithm.')})
config('sires-overnight','Sires',['O011','O073','M05'],{
 'window':setting({'start':'18:00','start_day_offset':-1,'end':'09:30','timezone':'America/New_York'},['MAMT:14'],'O073 binds to the same dated O011 window; not a global ETH definition.'),
 'reference_roles':setting(['overnight','prior_ETH','prior_RTH','developing_RTH'],['MAMT:14','MAMT:15','MAMT:16'],'Each keeps its own window and identity.'),
 'MPOC':setting('(profile_high+profile_low)/2',['MAMT:15'],'Profile midpoint remains distinct from volume POC.')})
config('sires-vwap-illustration','Sires',['O004','O030','O032'],{
 'anchor':setting('Session',['VWAP:8'],'Visible inputs field.'),
 'offset':setting(0,['VWAP:8'],'Visible zero offset.'),
 'timeframe':setting('Chart',['VWAP:8'],'Visible timeframe setting.'),
 'wait_for_timeframe_close':setting(True,['VWAP:8'],'Enabled in visible inputs.'),
 'source_price_label':setting('(H + L + …)',['VWAP:8'],'Truncated original label, retained literally.'),
 'price_basis':unknown(['VWAP:8'],'Full price-source formula cannot be read; HLC3 is plausible, not verified.'),
 'reset_clock':unknown(['VWAP:8'],'Session anchor does not disclose platform session clock.'),
 'enabled_multipliers':setting(['1','2'],['VWAP:8'],'Inputs 1 and 2 enabled; multiplier 3 disabled.'),
 'discussed_multiplier':setting('2.5',['VWAP:8'],'Caption differs from the visible enabled inputs.', 'source_conflict')})
for key,author,fraction,refs in [('sires-va40','Sires','0.40',['C3:7']),('saint-va68','Saint','0.68',['RTVP:4']),('vp-lesson-va70','Sires','0.70',['AMT1:5','MAMT:5'])]:
 config(key,author,['O062'],{'fraction':setting(fraction,refs,'Scoped source value-area percentage; no common default.'),'algorithm':unknown(refs,'Source percentage alone does not determine row expansion/ties.')})
config('sires-process','Sires',['O139','O146','O153'],{
 'confidence_scale':setting([1,5],['C1:6'],'Integer score at session start; original record is immutable.'),
 'confidence_observation':setting('session_start',['C1:6'],'Later review cannot rewrite original confidence.'),
 'review_example_sessions':setting(30,['C1:6'],'Scoped review example, not universal sample sufficiency.'),
 'excursion_collection_trades':setting([40,80],['C2:4'],'Collect observed MFE/MAE distributions with native windows/censoring; optimization deferred.'),
 'retained_categories':setting(['win','loss','flat','open','censored','missing_result','miss','breach'],['C1:6'],'Implementation accounting retains all identified observations; source explicitly names wins, losses, breaches and missed rules.', 'inference')})
config('sires-stop-sequence','Sires',['O122','O123','STOP-confirmed','STOP-early'],{
 'stages':setting(['absorption','price_reward','return_and_defense','aggression_and_delta_confirmation'],['STOP:10','STOP:12'],'Full staged interpretation remains tied to each source observation.'),
 'bars_nq_walkthrough':setting({'kind':'native_range','size':40},['STOP:8'],'NQ walkthrough uses native 40-range; not applied to the separate ES clip.'),
 'range_construction':unknown(['STOP:8'],'Native overshoot/reversal construction is not disclosed.')})
config('member-two-reasons','Member',['M07'],{
 'reasons':setting(['prior_reaction','minor_HVN'],['K10:7'],'Independent source reasons, not two arbitrary object IDs.'),
 'target_R':setting('1.5',['K10:7','K10:8'],'Both plans use 1.5R; later expansion is an outcome, not planned target.')})
config('stoic-process-risk','Stoic',['M11','M12','O154','O155','O156'],{
 'observation_unit':setting('research_process_and_risk_rule',['DATA:3','DATA:7','DATA:8'],'Data Engine is not an entry strategy.'),
 'macro_status':setting('deferred',['DATA:5'],'No macro model or Phase 2 return simulation in this implementation.'),
 'execution_journal':unknown(['DATA:3'],'Illustrated process is not a supplied private order ledger.')})
config('keani-open-above-blueprint','Keani',['M08'],{
 'sequence':setting(['open_above_value','rejection_at_POC_and_prior_VAH','aggressive_buying_break','held_retest'],['AVG:22'],'Literal caption and schematic; individual dated observations remain separate dependencies.'),
 'value_engine':unknown(['AVG:22'],'The schematic does not disclose VA construction or dated profile windows.'),
 'imbalance_configuration':unknown(['AVG:22'],'No footprint ratio/filter configuration is recoverable from this schematic.')})
config('refill-observation-study','Refill',['M09'],{
 'observation_unit':setting('defender_response_on_return_to_selected_level',['REF:7'],'Caption separates the response study from an entry trigger.'),
 'illustrated_sequence':setting(['level_built','first_test_no_result','second_test_no_result','buyers_regain_control'],['REF:7'],'Two separate visits in the retained NQ source chart.'),
 'zone_selector':unknown(['REF:7'],'Source describes aggressive-order clusters without publishing a complete reproducible selector.'),
 'execution_records':unknown(['REF:12'],'Illustration is not an individual order/fill/queue ledger.')})
config('jetbundle-participation-process','Jetbundle',['M10'],{
 'participation_actions':setting(['provide','withdraw','consume'],['MATH:3'],'Source participation vocabulary; BBO changes do not identify all three hidden/depth mechanisms.'),
 'observation_unit':setting('participation_response_state_transition',['MATH:3'],'AAPL order-book illustrations and separate NQ discussion; no entry algorithm.'),
 'classifier':unknown(['MATH:3','MATH:10','MATH:11'],'Named states do not disclose a trainable deterministic classifier or a supplied native state record series.')})

CASES=[]
def case(key,method,refs,configs,day,instrument,timeframe,interval,decision,*,profiles=(),annotations=(),missing=(),date_status='fact'):
    CASES.append(dict(case_id=key,method_id=method,source_refs=refs,configuration_ids=configs,
      evidence_mode='source_illustration',historical_candidate=False,
      date=setting(day,refs,'Date printed in the source.' if day else 'Exact trading date not readable in retained source.',date_status if day else 'unknown'),
      instrument=setting(instrument,refs,'Source display identity; never silently transferred to NQ.' if instrument else 'Native instrument/contract not established.', 'fact' if instrument else 'unknown'),
      timeframe=setting(timeframe,refs,'Case-specific visible/published chart configuration.' if timeframe else 'No verified case-specific bar size.','fact' if timeframe else 'unknown'),
      observation_interval=setting(interval,refs,'Visible observation window; fill timestamp is separately unknown.' if interval else 'No exact dated observation interval.','fact' if interval else 'unknown'),
      observed_decision=setting(decision,refs,'Source illustration or printed process decision; no invented execution record.','fact' if decision else 'unknown'),
      profiles=list(profiles),later_annotations=list(annotations),missing_fields=list(missing)))
    CASES[-1]['source_images']=[dict(image_id=ref+':page',source_key=ref.split(':')[0],page=int(ref.split(':')[1]),
      sha256=SOURCES[ref.split(':')[0]]['sha256'],region='full original page; figure and caption preserved together') for ref in refs]
    CASES[-1]['recorded_at']='2026-09-12'
    CASES[-1]['contemporaneous_process_record']=False

case('JJ-range-control-2026-02-24','JJ-TBR',['TBR:4','TBR:21'],['jumbo-published-geometry'],'2026-02-24','NQH6',{'kind':'time','minutes':1},{'start_et':'06:00','end_et':'09:00'},None,missing=['source_trade_decision'],date_status='inference')
CASES[-1]['date']['reason']='Frozen existing native geometry control date; not a date claimed by the Jumbo source figure.'
CASES[-1]['timeframe']['status']='inference';CASES[-1]['timeframe']['reason']='One-minute inputs for clock geometry control; not a source entry timeframe.'
CASES[-1]['evidence_mode']='native_control'
CASES[-1]['instrument']['status']='inference';CASES[-1]['instrument']['reason']='Acquired native control contract, not a displayed source fill.'
case('JJ-profiles-2026-06-12','JJ-TBR',['JR:4'],['jumbo-published-geometry'],'2026-06-12','NQ',None,None,{'kind':'profile_context','post_id':'2065444190557761675'},profiles=['separate_left_profile_1','separate_left_profile_2','separate_left_profile_3','developing_current'],missing=['exact_profile_windows','native_contract','timeframe','decision_timestamp','VA_algorithm'])
case('JJ-orderblock-long','JJ-TBR',['TBR:27','TBR:28'],['jumbo-published-geometry'],None,None,{'kind':'time','minutes':3},None,{'kind':'orderblock_illustration','side':'long','bounds':'full C2 range'},missing=['date','native_contract','event_members'])
case('JJ-orderblock-short-mirror','JJ-TBR',['TBR:27','TBR:28'],['jumbo-published-geometry'],None,None,{'kind':'time','minutes':3},None,{'kind':'mirrored_implementation_control','side':'short','bounds':'full C2 range'},missing=['dated_short_source_case','date','native_contract','event_members'])
CASES[-1]['evidence_mode']='synthetic_fixture'
CASES[-1]['observed_decision']['status']='inference';CASES[-1]['observed_decision']['reason']='Mirrored geometry invariant. Retained pages illustrate longs, so this is not an observed source short.'
CASES[-1]['timeframe']['status']='inference';CASES[-1]['timeframe']['reason']='Mirrored test uses the source long illustration clock.'
case('GB-FAIL-2025-11-20','GB-FAIL',['GB:31','GB:43'],['gb-nov20-sweep'],'2025-11-20','MNQZ2025',{'kind':'time','minutes':2},{'start_et':'08:00','end_et':'11:02','timezone':'America/New_York'}, {'kind':'displayed_short_position','price':'25301.75','sequence':'entry_at_high_sweep','fill_time':None},annotations=[{'kind':'later_MSS_FVG','entry_prerequisite':False},{'kind':'opposing_09_10_low_objective','planned_before_entry':None}],missing=['actual_fill_time','actual_fill_ledger','native_MNQ_data'])
CASES[-1]['source_sweep_region']=setting({'start_et':'10:30','end_et':'10:44'},['GB:43'],'Broad region around the eye/position at the later high sweep. This is a retrospective visual locator, not a fill timestamp.','inference')
case('GB-VWAP-2026-02-24','GB-VWAP',['GB:33','GB:34'],['gb-vwap-continuation'],'2026-02-24',None,{'kind':'time','minutes':1},{'start_et':'08:30','end_et':'10:25','timezone':'America/New_York'}, {'side':'long','sequence':['close_above_Asia_and_London','VWAP_retrace','entry'],'stop_points':'30'},annotations=[{'reported_points':['150','100'],'status':'source_conflict','planned_target':False}],missing=['display_native_contract','VWAP_reset','VWAP_basis','session_clocks','actual_fill_time'])
CASES[-1]['timeframe']['status']='inference';CASES[-1]['timeframe']['reason']='Bar spacing resembles one minute; retained source has no readable explicit timeframe label. Frozen prior comparison uses one minute.'
for suffix,post,created,side,description in [
 ('bearish','2095257805242446135','2026-09-02T21:09:23Z','short',{'bias':'bearish','reported_points':[20,30],'size':'no increase'}),
 ('bullish','2098075540607410229','2026-09-10T15:46:03Z','long',{'direction':'NYAM','location':'discount pullbacks','size':'smaller'})]:
 case('GB-SCALP-'+suffix,'GB-SCALP',['GB:40'],['gb-discretionary-scalp'],None,None,None,None,
      {'kind':'discretionary_scalp_description','side':side,'post_id':post,'description':description},
      missing=['native_contract','exact_trading_date','entry_time','fill_ledger','size_quantity','repeatable_entry_and_exit_rules'])
 CASES[-1]['source_post_created_at']=setting(created,['GB:40'],'Publication time is not an entry, fill or native observation timestamp.')
case('SIRES-overnight-profile','SIRES',['MAMT:14','MAMT:15','MAMT:16'],['sires-overnight','sires-va40'],None,None,None,{'start_et_previous_day':'18:00','end_et':'09:30','timezone':'America/New_York'}, {'kind':'overnight_LVN_and_shelf_hold','older_POC_alignment':'source interpretation'},profiles=['overnight','older_POC_parent','previous_ETH','developing_RTH'],missing=['date','native_contract','VA_algorithm','exact_LVN_selection'])
case('SIRES-same-candle-POC','SIRES',['FP9:5','FP9:7','FP8:6'],['sires-va40'],None,None,None,None,{'kind':'same_candle_POC_relocation'},profiles=['earlier_candle_snapshot','later_same_candle_snapshot'],missing=['date','native_contract','exact_snapshot_times','source_POC_tie_rule'])
case('STOP-confirmed','SIRES',['STOP:11','STOP:12'],['sires-stop-sequence'],None,'EPZ25',{'kind':'time','minutes':1},None,{'kind':'confirmed_entry','side':'long','checks':['location','reward','renewed_defense','delta_confirmation']},profiles=['prior_profile','developing_profile'],missing=['exact_dated_event_interval','ES_full_depth','actual_execution_record'])
case('STOP-early','SIRES',['STOP:13'],['sires-stop-sequence'],None,'EPZ25',{'kind':'time','minutes':1},None,{'kind':'wrong_entry','stage':'before_full_confirmation','outcome':'loss'},missing=['exact_date_year','event_interval','actual_execution_record'])
case('SIRES-losses-2026-07-23','SIRES',['ANAT:1','ANAT:6','ANAT:8','ANAT:9'],['sires-process'],'2026-07-23','NQ',None,{'start_display_clock':'10:14','end_display_clock':'10:32','timezone':None}, {'kind':'session_attempts','attempts':[{'ordinal':i+1,'display_clock':t,'outcome':o} for i,(t,o) in enumerate(zip(['10:14','10:15','10:17','10:24','10:25','10:27','10:30','10:31','10:32'],['loss','loss','win','loss','win','win','loss','loss','win']))]},annotations=[{'reported_session_trade_count':9},{'caption_first_four':'hurt','third_plotted_outcome':'positive','status':'source_conflict'}],missing=['exact_order_fill_times','price_levels','chart_timezone','bar_size'])
case('SAINT-break-retest','SAINT-AMT',['TRAP:7','TRAP:3','TRAP:4','TRAP:5','TRAP:9'],['saint-va68'],None,None,None,None,{'side':'short','kind':'trapped_buyers_retest','sequence':['upper_balance','AM_PM_failures','break','same_band_retest','short']},profiles=['daily_delta_profile','selected_balance'],missing=['date','native_contract','exact_band','source_footprint_configuration'])
case('SAINT-failed-auction','SAINT-AMT',['AMTL:10','AMTL:8','AMTL:9'],['saint-va68'],None,None,None,None,{'kind':'failed_auction_return_to_value'},profiles=['selected_balance','established_value'],missing=['date','native_contract','exact_interval','source_control_interpretation'])
for suffix,page,side in [('resistance',7,'short'),('return',8,'long')]:
 case('MEMBER-'+suffix,'MEMBER-TWO-REASONS',[f'K10:{page}'],['member-two-reasons'],None,'ES',None,None,{'side':side,'kind':'prior_reaction_plus_minor_HVN' if side=='short' else 'planned_return_absorption','target_R':'1.5'},profiles=['selected_minor_HVN'],missing=['date','native_contract','band_coordinates','fill_times'])
 if page==7:
  CASES[-1]['timeframe']=setting({'execution_minutes':2,'context_minutes':5},['K10:7'],'Right ES execution chart is two minutes; separate left NQ context panel is five minutes.')
  CASES[-1]['profiles'].append('separate_NQ_context_panel')
case('KEANI-open-above','KEANI-OPEN-ABOVE-VALUE',['AVG:22'],['keani-open-above-blueprint'],None,None,None,None,{'side':'long','kind':'open_above_prior_value','sequence':['prior_value','complete_A_low','developing_value','aggressive_breakout','defended_retest']},profiles=['prior_value','developing_current_value'],missing=['date','native_contract','VA_configuration','imbalance_configuration','exact_decision_time'])
CASES[-1]['source_figure_kind']='schematic sketch; no dated market chart'
case('REFILL-selected-order','REFILL-STUDY',['REF:7','REF:12','OFM:18'],['refill-observation-study'],None,'NQ',None,None,{'kind':'selected_order_study','observation_unit':'touch_and_order','actual_live_fill':False},missing=['source_model_and_zone_selector','individual_selected_order_ledger','date','native_contract'])
case('JETBUNDLE-state-process','JETBUNDLE-STATES',['MATH:3','MATH:10','MATH:11'],['jetbundle-participation-process'],None,'AAPL',None,None,{'kind':'state_transition_illustration','native_NQ_applicable':True},missing=['exact_native_state_observations','unpublished_classifier','full_participation_events'])
case('STOIC-process','STOIC-DATA',['DATA:3','DATA:4'],['stoic-process-risk'],None,None,None,None,{'kind':'research_process','sequence':['define','record_uniformly','compare','revise_version'],'entry_strategy':False},missing=['private_contemporaneous_research_records'])
case('STOIC-risk','STOIC-RISK',['DATA:7','DATA:8'],['stoic-process-risk'],None,None,None,None,{'kind':'printed_risk_stages','entry_strategy':False,'new_simulation':False},missing=['validation_trade_journal','source_Monte_Carlo_records'])

# Exact windows of the frozen native controls. They are retrospective
# measurement selections and never supply an unknown author setting or fill.
CONTROL_WINDOWS={
 'JJ-range-control-2026-02-24':[
  ('source_range','2026-02-24T06:00','2026-02-24T09:00')],
 'GB-FAIL-2025-11-20':[
  ('failure_reference','2025-11-20T09:00','2025-11-20T10:00'),
  ('failure_confirmation','2025-11-20T10:38','2025-11-20T10:40')],
 'GB-VWAP-2026-02-24':[
  ('asia','2026-02-23T20:00','2026-02-24T00:00'),
  ('london','2026-02-24T02:00','2026-02-24T05:00'),
  ('vwap_at_retest','2026-02-23T18:00','2026-02-24T10:00'),
  ('breakout_candle','2026-02-24T09:44','2026-02-24T09:45'),
  ('retest_candle','2026-02-24T10:00','2026-02-24T10:01')],
}
for row in CASES:
 row['native_control_windows']=[{'control_window_id':row['case_id']+':'+role,
   'version':'2.0.0','role':role,'start_et':start,'end_et':end,'timezone':'America/New_York',
   'status':'inference','source_refs':row['source_refs'],
   'reason':'Exact window of the frozen reconstructed comparison; not a source execution time or verified author setting.'}
  for role,start,end in CONTROL_WINDOWS.get(row['case_id'],[])]

doc=dict(schema='phase1-source-cases-v2',version='2.0.0',reviewed_at='2026-09-12',
 scope='Stages 1-7 implementation source configurations; illustrations and native controls have no historical admissions.',
 sources=SOURCES,configurations=CONFIGS,cases=CASES)
OUT.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n')
print(OUT, len(CONFIGS), 'configurations',len(CASES),'case records')
