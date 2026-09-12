"""One physical native partition through selector, assembly and reporting."""
from copy import deepcopy
from datetime import date
import csv
import json

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from trading_research.research.method_pack.empirical_bar_engine import run_bar_rule
from trading_research.research.method_pack.empirical_market import BarMarket, clock
from trading_research.research.method_pack.empirical_protocol import population_summary
from trading_research.research.method_pack.empirical_registry import build_registry, canonical_hash, validated_registry_batch
from trading_research.research.method_pack.empirical_selectors import MINUTE
from trading_research.research.method_pack.evidence import SchemaError
from trading_research.research.method_pack.assembly import assemble_episode, replay_assembled

DAY=date(2026,1,15)
DATASET='quantpad/cme__nq-continuous-futures__ohlcv-1m'


@pytest.fixture
def market(tmp_path):
    start,end=clock(DAY,'00:00'),clock(DAY,'16:00')
    rows=[]
    for t in range(start,end,MINUTE):
        # All early highs are100; a single10:01 excursion and later reclaim.
        high=102 if t==clock(DAY,'10:01') else 100
        rows.append({'t':t//1_000_000,'o':99.,'h':float(high),'l':98.,'c':99.,'v':10.,'instrument_id':42})
    path=tmp_path/DATASET/'native.parquet';path.parent.mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist(rows),path,row_group_size=120)
    manifest=tmp_path/'manifests/files.csv';manifest.parent.mkdir()
    with manifest.open('w') as f:
        writer=csv.DictWriter(f,fieldnames=['dataset_id','archive_path']);writer.writeheader()
        writer.writerow({'dataset_id':DATASET,'archive_path':path.relative_to(tmp_path).as_posix()})
    definition=tmp_path/'derived/continuous-futures__instrument-and-roll-maps/nq-instruments.json'
    definition.parent.mkdir(parents=True)
    definition.write_text(json.dumps([{'instrument_id':42,'root':'NQ','raw_symbol':'NQH6',
                                      'min_price_increment':'.25','first_definition_ns':start-1}]))
    return BarMarket({'partition_id':'fixture-native-partition','instrument_id':42,'session_date':str(DAY)},tmp_path)


@pytest.fixture
def registry():
    doc=build_registry();doc['freeze_status']='frozen';doc['registry_sha256']=canonical_hash(doc)
    return doc


def rule(registry,method,branch):
    return next(r for r in registry['rules'] if r['method_id']==method and r['branch']==branch)


def test_native_selector_assembled_evaluator_and_population_report(market,registry):
    selected=rule(registry,'GB-FAIL','nyam_box')
    found=run_bar_rule(selected,market,registry)
    assert len(found['records'])==1 and not found['population_holes']
    opportunity,replay=found['records'][0]
    assert replay.verdict=='pass'
    with validated_registry_batch(registry):
        assembled=market.source_assembly(selected,opportunity,registry)
        repeated=replay_assembled(assembled.manifest,resolver=market.resolver)
    assert assembled.result['verdict']=='unknown'  # private bias/risk/selection absent
    assert repeated.result['verdict']==assembled.result['verdict']
    assert assembled.result['faithful_eligible'] is False
    assert assembled.result['historical_comparison_eligible'] is True
    assert assembled.result['software_complete'] is True
    assert assembled.parsed['objects'] if isinstance(assembled.parsed,dict) else assembled.manifest['objects']
    summary=population_summary([{'opportunity':opportunity.to_dict(),'replay':replay.to_dict(opportunity)}])
    assert summary['N']==summary['p']==1 and summary['actual_fills'] is None


def test_narrow_jumbo_numeric_semantic_binding_keeps_source_unknown(market,registry):
    selected=rule(registry,'JJ-TBR','internal_rotation')
    found=run_bar_rule(selected,market,registry)
    opportunity,replay=found['records'][0]
    with validated_registry_batch(registry):
        assembled=market.source_assembly(selected,opportunity,registry)
        assert assembled.result['operands']['range_frozen']['value'] is True
        assert assembled.result['verdict']=='unknown'
        assert assembled.result['operands']['source_confirmation']['value'] is None
        doc=deepcopy(assembled.manifest)
        doc['assembly']['roles'][0]['source_definition']['value']['formation_start']+=MINUTE
        with pytest.raises(SchemaError,match='formation'):
            replay_assembled(doc,resolver=market.resolver)


def test_completed_zero_requires_actual_search_and_missing_reference_is_distinct(market,registry):
    selected=rule(registry,'JJ-TBR','extension_reaction')
    found=run_bar_rule(selected,market,registry)
    assert found['search_executed'] is True and not found['records'] and not found['population_holes']
    prior=rule(registry,'GB-FAIL','prior_day_level')
    missing=run_bar_rule(prior,market,registry)
    assert missing['search_executed'] is True and not missing['records'] and missing['population_holes']


def test_runner_recomputes_native_endpoint_and_rejects_changed_prices(market,registry):
    from dataclasses import replace
    from trading_research.research.method_pack.empirical_runner import execute_bar_records,endpoint_object
    selected=rule(registry,'GB-FAIL','nyam_box')
    found=run_bar_rule(selected,market,registry)
    with validated_registry_batch(registry):
        records=execute_bar_records(selected,market,registry,found)
    assert records[0]['native_endpoint_object']['recipe_id']=='O004'
    opportunity,replay=found['records'][0]
    endpoint=dict(replay.endpoint,C=replay.endpoint['C']+1)
    with pytest.raises(ValueError,match='differs from native producer'):
        endpoint_object(market,selected,opportunity,replace(replay,endpoint=endpoint))


def test_checkpoint_cannot_skip_foreign_partition(tmp_path,registry):
    from trading_research.research.method_pack.empirical_runner import run_job
    from trading_research.research.method_pack.empirical_protocol import write_json
    job={'job_id':'bar--intended','cohort':'bar-monthly','partition':{'partition_id':'intended','date':str(DAY),'instrument_id':42},'rule_ids':[]}
    # Same-run copied checkpoint must be rejected before reading any native data.
    write_json(tmp_path/'checkpoints/bar--intended.json',{'job_sha256':'foreign'})
    with pytest.raises(ValueError,match='stale or damaged'):
        run_job(job,{'manifest_sha256':'a'*64,'implementation':{'sha256':'b'*64}},registry,tmp_path,tmp_path/'absent')
