#!/usr/bin/env python3
"""Evaluate actual completed census collection using the accepted process scanner."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
import time
sys.path.insert(0,'/workspace/implementation/src')
from trading_research.research.method_pack import historical_runner as hr
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.measurement_runner import configure_runtime
from trading_research.research.method_pack.native_discovery import scan_branch
from recover_calendars import RecoveredFeatures


def main(root):
    configure_runtime();root=Path(root).resolve();registry,manifest=hr.load_registry(root)
    inputs=hr.read(root/'validation/COLLECTION_INPUTS.json')
    reconciliation=hr.read(root/'validation/CENSUS_RECONCILIATION.json')
    assert reconciliation['all_declared_sessions_completed']
    days=registry['scope']['evaluation_dates']
    frozen=int(datetime.fromisoformat(registry['research_frozen_at']).timestamp()*1e9)
    # Earliest saved checkpoint is an evidenced collection-recording timestamp,
    # not an invented pre-2020 freeze or a precision claim about process launch.
    first_checkpoint=min(Path(p).stat().st_mtime_ns for p in reconciliation['job_hashes'])
    assert frozen < first_checkpoint
    composition=hr.read(root/'protocol/CALENDAR_RECOVERY_COMPOSITION.json')
    inclusion=content_hash({'days':days,'daily_units':[r['coverage_id'] for r in manifest['branches']
        if not (r['method_id']=='STOIC-DATA' and r['branch']=='process_review')],
        'composition_sha256':composition['composition_sha256']})
    record={'id':'collection:evaluation:'+registry['registry_sha256'],
        'spec_sha256':registry['registry_sha256'],'spec_frozen_at':frozen,
        'collection_started_at':first_checkpoint,'collection_completed_at':time.time_ns(),
        'collection_start_basis':'earliest retained selected daily checkpoint mtime; recording timestamp, not precise worker launch',
        'eligible_ids':inputs['eligible_ids'],'included_ids':inputs['included_ids'],
        'inclusion_sha256':inclusion,'frozen_inclusion_sha256':inclusion,
        'inclusion_basis':'frozen full primary scope plus frozen calendar dependency replacement rule',
        'features':inputs['features'],'outcomes':inputs['outcomes'],
        'record_schemas':inputs['record_schemas'],'feature_fields':['predecision_values','operand_derivations'],
        'outcome_fields':['fixed_horizon_price_excursions','postdecision_boundary_ordering'],
        'comparison_counts':inputs['outcome_counts'],'revisions':[],
        'members_manifest':{'path':str(root/'validation/CENSUS_RECONCILIATION.json'),
            'sha256':hr.file_digest(root/'validation/CENSUS_RECONCILIATION.json')},
        'interpretation':'actual census process review; comparisons are observed boundary outcomes, not winning and losing actual trades'}
    path=root/'jobs/evaluation/process-review.json'
    if path.exists():record=hr.read(path)
    else:hr.immutable_json(path,record)
    market=RecoveredFeatures(days[-1],records={**hr._records(registry),'process_review':[record]})
    completed=[]
    for row in manifest['branches']:
        if row['method_id']!='STOIC-DATA':continue
        destination=hr._job_path(root,'evaluation','collection',row['coverage_id'])
        if destination.exists():doc=hr.verify_job(hr.read_job(destination),registry,row)
        else:
            doc=scan_branch(market,row)
            doc.update(registry_sha256=registry['registry_sha256'],software_sha256=registry['software']['sha256'],
                cohort='evaluation',collection_dates=days,
                input_receipts=[*market.input_receipts,{'path':str(path),'sha256':hr.file_digest(path)}],
                domain_observations=hr.domain_receipts(root,market),job_state='completed',outcomes=[],setup_measurements=[],
                native_executions=market.window.document['row_count'])
            hr.write_job(destination,doc)
            hr.verify_job(doc,registry,row)
        completed.append({'coverage_id':row['coverage_id'],'path':str(destination),'sha256':hr.file_digest(destination),
                          'episodes':len(doc['episodes']),'verdicts':[e['research_verdict'] for e in doc['episodes']]})
    hr.immutable_json(root/'validation/COLLECTION_REVIEW.json',{'status':'completed','jobs':completed,
        'entry_setup_denominator':0,'scope':'actual collection process; macro context retains final historical as-of values'})
    selection_path=root/'charts/SELECTION.json';selection=hr.read(selection_path)
    for receipt in completed:
        doc=hr.read_job(receipt['path'])
        for e in doc['episodes']:
            if not any(x['coverage_id']==receipt['coverage_id'] and x['candidate_id']==e['candidate_id'] for x in selection['charts']):
                selection['charts'].append({'job':receipt,'candidate_id':e['candidate_id'],'coverage_id':receipt['coverage_id'],
                    'outcome':'actual_collection_process','order':(doc['session_date'],e['decision_at'],e['candidate_id'])})
    selection_path.write_text(__import__('json').dumps(selection,indent=2)+'\n')
    print(__import__('json').dumps(completed,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run-root',required=True);main(p.parse_args().run_root)
