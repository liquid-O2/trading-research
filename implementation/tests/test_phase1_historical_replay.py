"""Causal upstream controls for historical discovery, not supplied true flags."""
from copy import deepcopy
from datetime import date,timedelta
from pathlib import Path
from decimal import Decimal as D
import json

import pytest

from trading_research.research.method_pack.adapters import normalize_mbp1_row
from trading_research.research.method_pack.branch_coverage import build_manifest,validate_manifest
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.empirical_market import clock
from trading_research.research.method_pack.event_time import aggregate_events,EventWindow,VERSION,CONTRACT,MINUTE,SECOND
from trading_research.research.method_pack.historical_features import HistoricalFeatures,balances
from trading_research.research.method_pack.historical_flow import exact_contact,local_observations,flow_stages,_flow_episode
from trading_research.research.method_pack.historical_assembly import HistoricalEpisode
from trading_research.research.method_pack.historical_runner import selected_root,immutable_json,verify_job,scope_for_range
from trading_research.research.method_pack.native_resolution import NativeEvidenceError,file_digest

DAY=date(2026,1,15)
START=clock(DAY-timedelta(days=1),'18:00')
END=clock(DAY,'16:00')
TOUCH=clock(DAY,'10:00')


def raw(at,px=100,size=1,side='B',action='T',index=0,bid_size=10,**kw):
    row=normalize_mbp1_row({'t':at,'price':str(px),'size':size,'side':side,'action':action,
        'instrument_id':17,'flags':128,'bid_px':'100','ask_px':'100.25','bid_sz':bid_size,'ask_sz':10,**kw},
        source_file='upstream-control.parquet',source_row=index)
    row['event_id']=f"{row['source_file']}:{row['source_row']}"
    return row


class Market(HistoricalFeatures):
    def __init__(self,events,records=None):
        events=sorted(events,key=lambda r:r['event_ns'])
        for i,row in enumerate(events):row['source_row']=i;row['event_id']=f'upstream-control.parquet:{i}'
        self.events=events
        doc=aggregate_events(events,START,END,17)
        doc.update(schema=VERSION,contract_sha256=content_hash(CONTRACT),instrument_id=17,
            start_ns=START,end_ns=END,input_sha256=content_hash(doc),plan={'unowned_intervals':[]})
        super().__init__(DAY,document=doc,records=records)
    def local(self,start,end,*,book=False):
        return [r for r in self.events if start<=r['event_ns']<end and (book or r['action']=='T')]


def flow_events(mode='normal'):
    events=[]
    def add(offset,px=100,size=1,side='B',action='T',bid=10):
        events.append(raw(TOUCH+int(offset*SECOND),px,size,side,action,bid_size=bid))
    # Actual traded reference, then baseline, defending sells, displayed
    # additions, thinner opposing prints and a three-tick buyer reward.
    add(-120,100);add(-100,105);add(-60,102)
    add(-4,100,1,'A');add(-3,100,1,'B');add(-2,100,0,'N','M')
    add(0,100,5,'A');add(1,100,5,'A');add(2,100,1,'B');add(3,100,0,'N','M')
    add(5,100,4,'A');add(6,100,4,'A');add(7,100,1,'B');add(8,100,0,'N','M',20)
    add(10,100,1,'A');add(12,100.25,1,'B')
    for i in range(5):add(15+i*.5,100.25 if i<4 else 100.75,10,'B')
    if mode=='passive':
        add(20,100,1,'B')
        add(25,100.5,10,'B')
    elif mode=='clean':
        add(20,100.5,10,'A');add(21,100.5,10,'A')
        add(25,100.75,30,'B');add(26,101,1,'B')
    else:
        add(20,100.75,1,'A');add(21,100.75,3,'B');add(25,100.75,5,'B')
    return events


def reference(m):
    return m.range(TOUCH-2*MINUTE,TOUCH,'native-reference')


def result(m,branch):
    trigger=m.bars(TOUCH,TOUCH+MINUTE)[0]
    return _flow_episode(m,branch,reference(m),trigger,'long',[D('99.75'),D('100.25')])


def account(tmp_path,value):
    record={'id':'actual-control-account','known_at':TOUCH-1,'instrument_id':17,'daily_r_before':value}
    path=tmp_path/'ledger.json';path.write_text(json.dumps([record]))
    return {**record,'evidence_path':str(path),'evidence_sha256':file_digest(path)}


def test_manifest_exact_membership_not_just_a_rehashed_registry():
    manifest=build_manifest();validate_manifest(manifest)
    assert manifest['counts']=={'methods':12,'branches':50,'additional_units':8,'objects':166,'operands':373}
    bad=deepcopy(manifest);bad['branches'].pop();bad['manifest_sha256']=content_hash({k:v for k,v in bad.items() if k!='manifest_sha256'})
    with pytest.raises(ValueError,match='omits'):validate_manifest(bad)
    assert all(r['historical_routes'] for r in manifest['operand_matrix'])


def test_raw_flow_defense_refresh_thinning_reward_and_new_retest_are_ordered():
    m=Market(flow_events());obs=local_observations(m,TOUCH,[D('99.75'),D('100.25')],'long')
    stages=flow_stages(obs)
    assert stages['defense']['known_at']<stages['refresh']['known_at']<stages['thinning']['known_at']<stages['liftoff']['known_at']
    assert stages['reward']['known_at']<stages['reward_retest']['known_at']<stages['renewed']['known_at']
    assert result(m,'dom_rejection')['research_verdict']=='pass'
    assert result(m,'absorption_reward_retest')['research_verdict']=='pass'


def test_stop_market_stages_survive_missing_account_and_literal_minus_four_boundary(tmp_path):
    m=Market(flow_events())
    observed=result(m,'stop_four_stage')
    assert observed['values']['reward_ticks']=='3'
    assert observed['values']['replenishment'] is True
    assert observed['research_verdict']=='unknown'
    m=Market(flow_events(),records={'account':[account(tmp_path,-4)]})
    assert result(m,'stop_four_stage')['research_verdict']=='fail'
    m=Market(flow_events(),records={'account':[account(tmp_path,-3)]})
    assert result(m,'stop_four_stage')['research_verdict']=='pass'


def test_simplified_contact_and_reward_cannot_replace_fresh_reward_retest():
    m=Market([r for r in flow_events() if r['event_ns']<TOUCH+20*SECOND])
    result_row=result(m,'absorption_reward_retest')
    assert result_row['values']['own_reward_confirmed'] is True
    assert result_row['values']['fresh_reward_retest_defended'] is None
    assert result_row['research_verdict']!='pass'


def test_passive_variant_does_not_require_individual_passive_order_identity():
    m=Market(flow_events('passive'))
    row=result(m,'ofm_passive')
    assert row['values']['source_squeeze_failed'] is True
    assert row['values']['no_aggression_at_failure'] is True
    assert row['research_verdict']=='pass'


def test_clean_squeeze_requires_absorbed_first_pullback_and_continuation():
    m=Market(flow_events('clean'));row=result(m,'clean_squeeze')
    assert row['research_verdict']=='pass'
    changed=[dict(r,side='B') if TOUCH+20*SECOND<=r['event_ns']<TOUCH+25*SECOND else r for r in flow_events('clean')]
    assert result(Market(changed),'clean_squeeze')['research_verdict']=='fail'


def test_flow_future_perturbation_cannot_change_completed_dom_decision():
    rows=flow_events();a=result(Market(deepcopy(rows)),'dom_rejection')
    changed=[dict(r,price=D('100000'),executed_size=99999) if r['event_ns']>a['decision_at'] else r for r in rows]
    b=result(Market(changed),'dom_rejection')
    assert (a['decision_at'],a['values'],a['research_verdict'])==(b['decision_at'],b['values'],b['research_verdict'])


def test_actual_contact_time_and_whole_equal_timestamp_batch_are_preserved():
    m=Market([raw(TOUCH,102),raw(TOUCH+10*SECOND,100),raw(TOUCH+10*SECOND,99.75),raw(TOUCH+20*SECOND,101)])
    bar=m.bars(TOUCH,TOUCH+MINUTE)[0]
    contact=exact_contact(m,bar,D('99.75'),D(100))
    assert contact['at']==TOUCH+10*SECOND and len(contact['event_ids'])==2
    assert exact_contact(m,bar,D(99),D(99)) is None


def test_price_balance_needs_repeated_confirmed_swings_not_a_clock_box():
    prices=[104,105,110,106,104,100,103,106,110.25,106,103,100.25,103,105]
    start=TOUCH-90*MINUTE
    rows=[raw(start+i*5*MINUTE+SECOND,p) for i,p in enumerate(prices)]
    m=Market(rows);found=balances(m.bars(start,TOUCH,300))
    assert found and len(found[-1]['pivots'])==4
    assert found[-1]['known_at']>found[-1]['pivots'][-1]['at']
    assert not balances(Market([raw(start+i*5*MINUTE+SECOND,105) for i in range(14)]).bars(start,TOUCH,300))


def test_unowned_partial_minute_never_becomes_complete_from_one_trade():
    m=Market([raw(TOUCH+SECOND,100)])
    m.window.document['plan']['unowned_intervals']=[{'start_ns':TOUCH+30*SECOND,'end_ns':TOUCH+MINUTE}]
    assert m.coverage(TOUCH,TOUCH+MINUTE)['observed_scope_complete'] is False
    assert m.bars(TOUCH,TOUCH+MINUTE)[0]['V']==1


def test_record_membership_and_checkpoint_identity_are_checked(tmp_path):
    m=Market(flow_events(),records={'account':[account(tmp_path,-3)]})
    assert m.supplied('account',TOUCH)[0]['daily_r_before']==-3
    m.records['account'][0]['daily_r_before']=100
    with pytest.raises(NativeEvidenceError,match='absent from'):m.supplied('account',TOUCH)
    with pytest.raises(NativeEvidenceError,match='another registry'):
        verify_job({'registry_sha256':'old'},{'registry_sha256':'new'},{})
    with pytest.raises(NativeEvidenceError,match='historical empirical'):
        selected_root('/workspace/implementation/reports/phase1-live/empirical/new')
    path=tmp_path/'frozen.json';immutable_json(path,{'a':1})
    with pytest.raises(NativeEvidenceError,match='immutable'):immutable_json(path,{'a':2})


def test_all_year_date_range_includes_difficult_calendar_days_without_replacement():
    assert scope_for_range('2023-01-01','2023-01-03')==['2023-01-01','2023-01-02','2023-01-03']
    with pytest.raises(ValueError):scope_for_range('2019-12-31','2020-01-02')


def test_missing_reference_scope_is_unknown_and_typed_artifacts_serialize(tmp_path):
    from dataclasses import dataclass
    from trading_research.research.method_pack.historical_price_scanners import _known
    from trading_research.research.method_pack.historical_runner import write_job,read_job
    assert _known({'complete':True,'coverage':{'observed_scope_complete':False}}) is None
    assert _known({'complete':True,'coverage':{'observed_scope_complete':True}}) is True
    @dataclass
    class Observation:
        day:date
        price:D
    path=tmp_path/'typed.json.gz'
    write_job(path,{'observation':Observation(DAY,D('100.25')),'members':(1,2)})
    assert read_job(path)=={'observation':{'day':str(DAY),'price':'100.25'},'members':[1,2]}


def test_ambiguous_native_response_is_unknown_without_inventing_a_state_label():
    from trading_research.research.method_pack.historical_process_scanners import scan_jetbundle
    start=clock(DAY,'09:30');end=start+2*MINUTE
    m=Market([raw(start+SECOND,100),raw(end-SECOND,101),raw(end-SECOND,102)])
    e=scan_jetbundle(m,'B')['episodes'][0]
    assert e['values']['response_record_complete'] is None
    assert e['values']['state'] is None
    assert e['research_verdict']=='unknown'


def test_concurrent_immutable_cache_publication_accepts_equal_existing_directory(tmp_path,monkeypatch):
    import errno
    from trading_research.research.method_pack import event_cache
    from trading_research.research.method_pack.event_time import CONTRACT
    m=Market([raw(TOUCH,100)])
    doc=m.window.document
    doc['membership_sha256']='physical-members';doc['raw_sources_unchanged']=True
    monkeypatch.setattr(event_cache,'ownership',lambda root:{})
    monkeypatch.setattr(event_cache,'plan_window',lambda *a,**k:{'ownership_sha256':'owned'})
    monkeypatch.setattr(event_cache,'identify_sources',lambda plan:[])
    monkeypatch.setattr(event_cache,'build_event_window',lambda *a,**k:doc)
    original=Path.rename
    def racing_publish(temp,destination):
        destination.mkdir()
        for child in temp.iterdir():(destination/child.name).write_bytes(child.read_bytes())
        raise OSError(errno.ENOTEMPTY,'concurrent directory exists')
    monkeypatch.setattr(Path,'rename',racing_publish)
    a,receipt=event_cache.cached_window(tmp_path/'raw',START,END,17,cache_root=tmp_path/'cache')
    assert Path(receipt['path']).is_file()
    assert not list((tmp_path/'cache').glob('building-*'))
    b,again=event_cache.cached_window(tmp_path/'raw',START,END,17,cache_root=tmp_path/'cache')
    assert again==receipt and b['input_sha256']==a['input_sha256']


def test_verified_digest_rehashes_small_files_and_detects_same_size_backdated_changes(tmp_path,monkeypatch):
    import os
    from trading_research.research.method_pack import historical_runner as runner
    path=tmp_path/'member';path.write_bytes(b'AAA');initial=path.stat();calls=[]
    full=runner._full_file_digest
    def counted(p):calls.append(str(p));return full(p)
    monkeypatch.setattr(runner,'_full_file_digest',counted)
    a=runner.file_digest(path)
    assert runner.file_digest(path)==a and len(calls)==2
    path.write_bytes(b'BBB');os.utime(path,ns=(initial.st_atime_ns,initial.st_mtime_ns))
    assert runner.file_digest(path)!=a and len(calls)==3


def test_parent_binding_cannot_replace_the_selected_child_branch():
    m=Market(flow_events())
    e=HistoricalEpisode(m,'GB-FAIL','mss_fvg_refinement','long',{'id':'child','at':TOUCH},{'id':'parent'})
    with pytest.raises(ValueError,match='changed selected branch'):
        e.bind({'branch':'nyam_box'},operation='parent copy')
    assert e.values['branch']=='mss_fvg_refinement'


def green_reclaim_events(ambiguous_close=False):
    start=clock(DAY,'06:00')
    events=[raw(at,100 if at==clock(DAY,'09:00') else 102) for at in range(start,TOUCH,MINUTE)]
    events += [raw(TOUCH,99.5),raw(TOUCH,99.75)]
    events += [raw(TOUCH+i*MINUTE,100.5) for i in range(1,5)]
    events.append(raw(TOUCH+5*MINUTE-SECOND,100.5))
    if ambiguous_close:events.append(raw(TOUCH+5*MINUTE-SECOND,100.75))
    return events


def test_reclaim_uses_known_close_without_requiring_unneeded_open():
    from trading_research.research.method_pack.historical_price_scanners import scan_green_failure
    m=Market(green_reclaim_events())
    candle=m.bars(TOUCH,TOUCH+5*MINUTE,300)[0]
    assert candle['O'] is None and candle['C']==D('100.5')
    e=next(r for r in scan_green_failure(m,'nyam_box')['episodes'] if r['side']=='long')
    assert e['values']['complete_clock_five_minute_bar'] is True
    assert e['values']['confirm_close']=='100.5'
    assert e['research_verdict']=='pass'


def test_ambiguous_reclaim_close_stays_unknown_not_failed():
    from trading_research.research.method_pack.historical_price_scanners import scan_green_failure
    e=next(r for r in scan_green_failure(Market(green_reclaim_events(True)),'nyam_box')['episodes'] if r['side']=='long')
    assert e['values']['complete_clock_five_minute_bar'] is None
    assert e['values']['confirm_close'] is None
    assert e['research_verdict']=='unknown'


def test_absence_requires_only_consumed_fields_and_keeps_numeric_volume():
    from trading_research.research.method_pack.historical_assembly import absent
    m=Market([raw(TOUCH,100),raw(TOUCH+SECOND,101),raw(TOUCH+SECOND,102)])
    assert absent(m,TOUCH,TOUCH+MINUTE,fields=('C',)) is None
    assert absent(m,TOUCH,TOUCH+MINUTE) is False
    assert m.bars(TOUCH,TOUCH+MINUTE)[0]['V']==3


def test_o056_does_not_require_unconsumed_c2_open():
    from trading_research.research.method_pack.historical_price_scanners import _ob
    from trading_research.research.method_pack.branch_coverage import setting
    duration=setting('tbr_sessions')['confirmation_seconds']*SECOND
    start=TOUCH//duration*duration-duration
    events=[raw(at,100) for at in range(start,start+3*duration,MINUTE)]
    m=Market(events);touch=m.bars(start+duration,start+2*duration)[0]
    assert _ob(m,touch,'long',start+3*duration)[0] is False
    tied=[*events,raw(start+duration,99.75)]
    m=Market(tied);touch=m.bars(start+duration,start+2*duration)[0]
    assert _ob(m,touch,'long',start+3*duration)[0] is False


def test_missing_local_endpoint_does_not_certify_absent_flow_stage():
    from trading_research.research.method_pack.historical_flow import flow_absent
    m=Market([raw(TOUCH,100),raw(TOUCH+SECOND,101),raw(TOUCH+SECOND,102)])
    obs=local_observations(m,TOUCH,[D('99.75'),D('100.25')],'long')
    assert flow_absent(m,TOUCH,TOUCH+MINUTE,obs['chunks']) is None


def test_unknown_aggressor_preserves_volume_but_cannot_confirm_directional_flow():
    rows=[dict(r,side='N') if r['action']=='T' else r for r in flow_events()]
    m=Market(rows);obs=local_observations(m,TOUCH,[D('99.75'),D('100.25')],'long')
    assert sum(r['unknown'] for r in obs['chunks'])>0
    assert flow_stages(obs)['defense'] is None
    e=result(m,'absorption_reward_retest')
    assert e['values']['cvd_filter_ok'] is None
    assert e['values']['opposing_effort_no_result'] is None
    assert e['research_verdict']=='unknown'
    assert sum(b['V'] for b in m.bars(TOUCH,TOUCH+MINUTE))==sum(r['executed_size'] for r in rows if r['action']=='T' and TOUCH<=r['event_ns']<TOUCH+MINUTE)


def test_future_unknown_aggressor_does_not_poison_completed_flow_decision():
    rows=flow_events();a=result(Market(deepcopy(rows)),'dom_rejection')
    changed=[dict(r,side='N') if r['event_ns']>a['decision_at'] else r for r in rows]
    b=result(Market(changed),'dom_rejection')
    assert (a['decision_at'],a['values'],a['research_verdict'])==(b['decision_at'],b['values'],b['research_verdict'])
