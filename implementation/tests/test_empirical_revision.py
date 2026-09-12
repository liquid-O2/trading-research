"""Exposure revisions cannot silently change selectors or reuse old output."""
import json
from copy import deepcopy
from unittest.mock import patch
import pytest
from trading_research.research.method_pack import empirical_runner as runner
from trading_research.research.method_pack.empirical_protocol import write_json


def prepared(tmp_path):
    module='implementation/src/trading_research/research/method_pack/'
    before={module+'empirical_reporting.py':'old-report',module+'empirical_bar_engine.py':'same-selector'}
    after=dict(before);after[module+'empirical_reporting.py']='repaired-report'
    current={'sha256':'new-code','files':after}
    old={'registry_sha256':'unchanged-rules','implementation':{'sha256':'old-code','files':before},
         'splits':{},'jobs':[{'job_id':'fixed-job','rule_ids':['fixed-rule']}],'outcome_blind':True}
    old['manifest_sha256']=runner.manifest_hash(old)
    write_json(tmp_path/'RUN_MANIFEST.json',old)
    write_json(tmp_path/'revisions/run-v1/RUN_MANIFEST.json',old)
    artifact=tmp_path/'pilot-artifact.json';write_json(artifact,{'native_control':'same-excluded-date'})
    write_json(tmp_path/'calibration/NATIVE_PIPELINE.json',{'implementation_sha256':'new-code',
        'registry_sha256':'unchanged-rules','artifact_path':str(artifact),'artifact_sha256':runner.file_hash(artifact)})
    write_json(tmp_path/'EVALUATION_EXPOSURE.json',{'revisions':[{'revision':'1.0.1','previous_run_manifest_sha256':old['manifest_sha256'],
        'reason':'Reporting-only count repair; original date/rule population remains fixed.'}]})
    return old,current


def test_reporting_revision_retains_original_population_and_discloses_exposure(tmp_path):
    old,current=prepared(tmp_path)
    with patch.object(runner,'load_registry',return_value={'registry_sha256':'unchanged-rules'}),patch.object(runner,'implementation_identity',return_value=current):
        runner.revise_reporting_run(tmp_path)
    new=json.loads((tmp_path/'RUN_MANIFEST.json').read_text())
    assert new['jobs']==old['jobs'] and new['registry_sha256']==old['registry_sha256']
    assert new['outcome_blind'] is False and new['rule_and_split_freeze_unchanged'] is True
    assert new['revision']['source_rule_or_selector_changes'] is False
    assert new['previous_run_manifest_sha256']==old['manifest_sha256']


def test_reporting_revision_cannot_smuggle_changed_selector_after_outcomes(tmp_path):
    old,current=prepared(tmp_path)
    changed=deepcopy(current)
    changed['files']['implementation/src/trading_research/research/method_pack/empirical_bar_engine.py']='changed-selector'
    with patch.object(runner,'load_registry',return_value={'registry_sha256':'unchanged-rules'}),patch.object(runner,'implementation_identity',return_value=changed):
        with pytest.raises(ValueError,match='reporting-only'):
            runner.revise_reporting_run(tmp_path)
    assert json.loads((tmp_path/'RUN_MANIFEST.json').read_text())==old


def test_second_recorded_layout_revision_is_versioned_and_cannot_repeat(tmp_path):
    old,current=prepared(tmp_path)
    old['run_version']='1.0.1';old['manifest_sha256']=runner.manifest_hash(old)
    write_json(tmp_path/'RUN_MANIFEST.json',old)
    write_json(tmp_path/'revisions/run-v1.0.1/RUN_MANIFEST.json',old)
    write_json(tmp_path/'EVALUATION_EXPOSURE.json',{'revisions':[{'revision':'1.0.2',
        'previous_run_manifest_sha256':old['manifest_sha256'],'reason':'Canonical artifact layout repair.'}]})
    with patch.object(runner,'load_registry',return_value={'registry_sha256':'unchanged-rules'}),patch.object(runner,'implementation_identity',return_value=current):
        result=runner.revise_reporting_run(tmp_path)
        assert result['run_version']=='1.0.2'
        with pytest.raises(ValueError,match='already applied'):
            runner.revise_reporting_run(tmp_path)


def test_reporting_revision_refuses_to_relabel_existing_checkpoints(tmp_path):
    old,current=prepared(tmp_path)
    write_json(tmp_path/'checkpoints/stale.json',{'job_id':'fixed-job','implementation_sha256':'old-code'})
    with pytest.raises(ValueError,match='archive original checkpoints'):
        runner.revise_reporting_run(tmp_path)
    assert json.loads((tmp_path/'RUN_MANIFEST.json').read_text())==old


def test_absent_prior_tape_window_does_not_block_current_independent_branches():
    from datetime import date
    from types import SimpleNamespace
    from trading_research.research.method_pack.native_resolution import NativeEvidenceError
    market=SimpleNamespace(day=date(2021,9,1),instrument_id=42,dataset_id='bars')
    partition={'input_identities':[],'dataset_windows':{'trades':{'dataset_id':'trades'}}}
    current={'row_count':3,'coverage':{'coverage_ok':None}}
    with patch('trading_research.research.method_pack.empirical_tape.load_tape_session',
               side_effect=[NativeEvidenceError('no canonical native tape file overlaps requested interval'),current]):
        tape,prior=runner.tape_context(market,partition,'/unused')
    assert tape==current and prior['row_count']==0 and prior['coverage']['coverage_ok'] is None
    with patch('trading_research.research.method_pack.empirical_tape.load_tape_session',
               side_effect=NativeEvidenceError('native tape differs from frozen manifest')):
        with pytest.raises(NativeEvidenceError,match='differs from frozen'):
            runner.tape_context(market,partition,'/unused')
