"""Independent synthetic controls; no evaluation dates or outcomes are read."""
from copy import deepcopy
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from trading_research.research.method_pack import empirical_bar_engine as engine
from trading_research.research.method_pack.empirical_market import clock
from trading_research.research.method_pack.empirical_protocol import ReplayResult
from trading_research.research.method_pack.empirical_registry import build_registry
from trading_research.research.method_pack.empirical_selectors import MINUTE, compact_bar, make_opportunity

DAY=date(2026,2,24)


def bar(start,minutes=1,low=100,high=102,close=101):
    return {'bar_id':f'fixture:{start}:{minutes}','instrument_id':42,'start':start,
            'end':start+minutes*MINUTE,'known_at':start+minutes*MINUTE,'complete':True,
            'O':Decimal(close),'H':Decimal(high),'L':Decimal(low),'C':Decimal(close),'V':Decimal(10)}


class FixtureMarket:
    def __init__(self):
        self.day=DAY;self.instrument_id=42;self.end=clock(DAY,'16:00')
        self.partition={'partition_id':'independent-synthetic-review','instrument_id':42,'session_date':str(DAY)}
        self.overrides={};self.requests=[]

    def bars(self,start,end,minutes=1):
        self.requests.append((start,end,minutes))
        return [deepcopy(self.overrides.get(t,bar(t,minutes,105,107,106))) for t in range(start,end,minutes*MINUTE)]

    def object(self,method,branch,recipe,start,end,inputs=None,label=None):
        members=self.bars(start,end)
        value=bar(start,(end-start)//MINUTE,min(b['L'] for b in members),max(b['H'] for b in members),members[-1]['C'])
        return {'object_id':'synthetic-complete-A'},SimpleNamespace(coverage_ok=True,value=value)


def rules():
    registry=build_registry()
    lookup={(r['method_id'],r['branch']):r for r in registry['rules']}
    return registry,lookup


def parent_fixture(market,lookup,registry):
    trigger=bar(clock(DAY,'10:00'),low=109,high=111,close=110)
    reference={'reference_id':'synthetic-box','instrument_id':42,'known_at':clock(DAY,'10:00'),'complete':True,'high':Decimal(110),'low':Decimal(90),'object_ids':[]}
    parent=make_opportunity(lookup['GB-FAIL','nyam_box'],market.partition,reference,trigger,'short',registry['registry_sha256'],market.end)
    completion=bar(clock(DAY,'10:00'),5,108,112,109)
    replay=ReplayResult(parent.opportunity_id,'pass',completion['end'],compact_bar(completion),'synthetic_parent_reclaim',selected_signal_at=completion['end']).validate(parent)
    return {'records':[(parent,replay)],'population_holes':[],'references':[reference]},replay.completed_at


def run_mss(market,registry,lookup,parent):
    with patch.object(engine,'run_bar_rule',return_value=parent):
        return engine._mss(lookup['GB-FAIL','mss_fvg_refinement'],market,registry)


def test_mss_completed_reference_and_child_are_point_events_at_actual_completion():
    registry,lookup=rules();market=FixtureMarket();parent,completion=parent_fixture(market,lookup,registry)
    result=run_mss(market,registry,lookup,parent)
    child,_=result['records'][0]
    assert child.reference_known_at==completion
    assert child.reference['parent_completion_at']==completion
    assert child.occurrence_start==child.occurrence_end==child.available_at==completion
    assert child.trigger['start']<completion  # source candle remains separately identified
    assert all(start>=clock(DAY,'10:06') for start,_,_ in market.requests)


def test_mss_postparent_endpoint_and_mature_record_ignore_later_price_changes():
    registry,lookup=rules();market=FixtureMarket();parent,_=parent_fixture(market,lookup,registry)
    for text,lo,hi,c in [('10:06',108,110,109),('10:08',107,109,108),('10:10',104,106,105)]:
        t=clock(DAY,text);market.overrides[t]=bar(t,2,lo,hi,c)
    before=run_mss(market,registry,lookup,parent)['records'][0]
    assert before[1].verdict=='pass' and before[1].completed_at==clock(DAY,'10:12')
    t=clock(DAY,'10:20');market.overrides[t]=bar(t,2,500,700,600)
    after=run_mss(market,registry,lookup,parent)['records'][0]
    assert before[0].to_dict()==after[0].to_dict()
    assert before[1].to_dict(before[0])==after[1].to_dict(after[0])


def test_mss_missing_first_postparent_candle_is_unknown_not_later_gap_success():
    registry,lookup=rules();market=FixtureMarket();parent,_=parent_fixture(market,lookup,registry)
    t=clock(DAY,'10:06');market.overrides[t]=dict(bar(t,2),complete=False)
    result=run_mss(market,registry,lookup,parent)['records'][0][1]
    assert result.verdict=='unknown' and result.censored


def profile_payload(day):
    return {'profile':{'instrument_id':42,'formation_start':clock(day,'09:30'),'formation_end':clock(day,'16:00'),
                       'known_at':clock(day,'16:00'),'as_of':clock(day,'16:00'),'kind':'prior_rth','session_date':str(day),'coverage':{'ok':True},'vah':Decimal(100),'val':Decimal(90),
                       'poc':Decimal(95),'profile_id':'synthetic-prior-profile','snapshot_id':'synthetic-prior-snapshot',
                       'value_area_fraction':Decimal('0.70'),'value_area_algorithm':'contiguous_larger_adjacent_volume_tie_both','value_area_tie_policy':'both','poc_tie_policy':'lowest'}}


def test_opening_state_preserves_below_value_and_missing_value_in_population():
    registry,lookup=rules();market=FixtureMarket();rule=lookup['KEANI-OPEN-ABOVE-VALUE','source_long']
    profile=profile_payload(DAY-timedelta(days=1))
    passed=engine._opening_state(rule,market,registry,profile)['records']
    assert len(passed)==1 and passed[0][1].verdict=='pass'
    first=clock(DAY,'09:30');market.overrides[first]=bar(first,1,99,107,106)
    failed=engine._opening_state(rule,market,registry,profile)['records']
    assert len(failed)==1 and failed[0][1].verdict=='fail'
    unknown=engine._opening_state(rule,market,registry,None)['records']
    assert len(unknown)==1 and unknown[0][1].verdict=='unknown'


def test_opening_state_rejects_wrong_value_area_policy():
    registry,lookup=rules();market=FixtureMarket();profile=profile_payload(DAY-timedelta(days=1))
    profile['profile']['value_area_fraction']=Decimal('0.40')
    with pytest.raises(ValueError,match='configuration|VA70'):
        engine._opening_state(lookup['KEANI-OPEN-ABOVE-VALUE','source_long'],market,registry,profile)


def test_opening_state_rejects_stale_same_instrument_profile():
    registry,lookup=rules();market=FixtureMarket()
    stale=profile_payload(DAY-timedelta(days=7))
    with pytest.raises(ValueError,match='prior|formation|session|profile'):
        engine._opening_state(lookup['KEANI-OPEN-ABOVE-VALUE','source_long'],market,registry,stale)


def test_resume_rejects_another_jobs_checkpoint_even_with_valid_artifact_hash(tmp_path):
    import json
    from trading_research.research.method_pack.empirical_runner import file_hash, run_job
    artifact=tmp_path/'other-artifact.json';artifact.write_text('{}')
    checkpoints=tmp_path/'checkpoints';checkpoints.mkdir()
    job={'job_id':'wanted-job','cohort':'bar-monthly','partition':{'partition_id':'wanted-partition','date':str(DAY),'instrument_id':42},'rule_ids':['wanted-rule']}
    manifest={'manifest_sha256':'manifest','implementation':{'sha256':'implementation'}}
    checkpoint={'job_id':'other-job','partition_id':'other-partition','registry_sha256':'another-registry',
                'session_date':'2020-01-01','instrument_id':99,'search_completed':True,
                'run_manifest_sha256':'manifest','implementation_sha256':'implementation',
                'artifact_path':str(artifact),'artifact_sha256':file_hash(artifact),'rules':[]}
    (checkpoints/'wanted-job.json').write_text(json.dumps(checkpoint))
    with pytest.raises(ValueError,match='checkpoint|job|partition|registry|identity'):
        run_job(job,manifest,{'registry_sha256':'wanted-registry'},tmp_path)


def test_run_validation_rejects_rehashed_omission_of_a_frozen_split_partition(tmp_path):
    import json
    from trading_research.research.method_pack import empirical_runner as runner
    registry,_=rules();registry['freeze_status']='frozen'
    from trading_research.research.method_pack.empirical_registry import canonical_hash
    registry['registry_sha256']=canonical_hash(registry)
    calibration=tmp_path/'calibration';calibration.mkdir();(calibration/'calibration_matrix.json').write_text('{}')
    splits={}
    for cohort in runner.COHORTS:
        path=tmp_path/(cohort+'.json')
        split={'manifest_sha256':'synthetic-split','partitions':[{'partition_id':'declared-unscanned','date':str(DAY),'instrument_id':42}] if cohort=='bar-monthly' else []}
        path.write_text(json.dumps(split))
        splits[cohort]={'path':str(path),'sha256':runner.file_hash(path),'manifest_sha256':'synthetic-split'}
    (calibration/'NATIVE_PIPELINE.json').write_text('{}')
    manifest={'schema':'phase1-empirical-run-v1','registry_sha256':registry['registry_sha256'],
              'implementation':{'sha256':'synthetic-code'},'calibration_sha256':runner.file_hash(calibration/'calibration_matrix.json'),
              'native_pipeline_sha256':runner.file_hash(calibration/'NATIVE_PIPELINE.json'),
              'splits':splits,'jobs':[]}
    manifest['manifest_sha256']=runner.manifest_hash(manifest)
    (tmp_path/'RUN_MANIFEST.json').write_text(json.dumps(manifest))
    with patch.object(runner,'load_registry',return_value=registry),patch.object(runner,'implementation_identity',return_value={'sha256':'synthetic-code'}):
        with pytest.raises(ValueError,match='job|partition|membership|split|manifest'):
            runner.validate_run(tmp_path)


class SelectorFixtureMarket(FixtureMarket):
    """Complete synthetic clock grid for branch controls, not native evidence."""
    def bars(self,start,end,minutes=1):
        self.requests.append((start,end,minutes))
        return [deepcopy(self.overrides.get((t,minutes),bar(t,minutes,105.5,106.5,106))) for t in range(start,end,minutes*MINUTE)]

    def range_reference(self,rule,start,end,recipe='O046',label='range',require_inside=False):
        return {'reference_id':f'synthetic:{label}:{start}:{end}','instrument_id':42,'known_at':end,
                'formation_start':start,'formation_end':end,'complete':True,'high':Decimal(110),'low':Decimal(100),
                'object_ids':[],'require_inside_box':require_inside}

    def prior_reference(self,rule,kind='day'):
        return self.range_reference(rule,clock(DAY-timedelta(days=1),'09:30'),clock(DAY-timedelta(days=1),'16:00'),label='prior-'+kind)

    def minute_open_reference(self,rule,at,label):
        result=self.range_reference(rule,at,at+MINUTE,label=label)
        result.update(high=Decimal(106),low=Decimal(106))
        return result

    def vwap(self,rule,at):
        return {'price':Decimal(106),'variance':Decimal(1),'known_at':at,'object_id':'synthetic-prefix-vwap'}

    def put(self,text,minutes,lo,hi,c):
        t=clock(DAY,text);self.overrides[t,minutes]=bar(t,minutes,lo,hi,c)


BAR_BRANCHES=[
 ('JJ-TBR','judas_reversal'),('JJ-TBR','extension_reaction'),('JJ-TBR','internal_rotation'),
 *[('GB-FAIL',b) for b in ('nyam_box','previous_hour','prior_day_level','prior_week_level','prior_month_level','cash_open_reclaim_case','asia_tdo_case','mss_fvg_refinement')],
 ('GB-VWAP','source_long'),('SIRES','vwap_deviation_fade'),('SAINT-AMT','continuation_retest')]


@pytest.mark.parametrize('method,branch',BAR_BRANCHES)
def test_each_supported_bar_branch_has_a_positive_synthetic_observation(method,branch):
    registry,lookup=rules();market=SelectorFixtureMarket();rule=lookup[method,branch]
    if method=='JJ-TBR':
        if branch=='judas_reversal':market.put('09:41',1,109,111,110)
        elif branch=='extension_reaction':market.put('09:01',1,123,125,124)
        else:
            market.put('09:30',1,104,106,106);market.put('09:31',1,109,111,110)
    elif method=='GB-FAIL':
        if branch=='cash_open_reclaim_case':market.put('09:34',1,106,108,107)
        elif branch=='asia_tdo_case':
            market.put('00:02',1,109,111,110);market.put('00:04',1,104,106,105)
        else:
            market.put('10:01' if branch in {'nyam_box','mss_fvg_refinement'} else '09:31',1,109,111,110)
            if branch=='mss_fvg_refinement':
                market.put('10:06',2,108,110,109);market.put('10:08',2,107,109,108);market.put('10:10',2,104,106,105)
    elif method=='GB-VWAP':market.put('05:01',1,110,112,111)
    elif method=='SIRES':market.put('09:30',5,106,108,107)
    else:
        market.put('09:30',5,110,112,111);market.put('09:35',5,109,112,111)
    found=engine.run_bar_rule(rule,market,registry)
    assert found['search_executed'] is True
    assert found['records']
    assert any(replay.verdict=='pass' for _,replay in found['records'])
    for opportunity,replay in found['records']:
        opportunity.validate();replay.validate(opportunity)
        assert opportunity.actual_fill is None and replay.source_method_verdict=='unknown'
