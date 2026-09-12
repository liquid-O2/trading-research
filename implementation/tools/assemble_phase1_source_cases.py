#!/usr/bin/env python3
"""Replay fixed, dated source comparisons through the normal C01 boundary.

The native controls are declared in the versioned source-case catalog. Their
measurement cutoff is not an observed author fill or a historical selector.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from trading_research.research.method_pack.assembly import assemble_episode
from trading_research.research.method_pack.contracts import fields_for
from trading_research.research.method_pack.native_windows import collect_window, AuditedWindowResolver
from trading_research.research.method_pack.protocol import jsonable
from trading_research.research.method_pack.source_config import load_catalog


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'implementation/validation/phase1-completion/source-cases'
BARS='quantpad/cme__nq-continuous-futures__ohlcv-1m'
TRADES='quantpad/cme__nq-continuous-futures__trades'


def exact_ns(value):
    at=datetime.fromisoformat(value).replace(tzinfo=ZoneInfo('America/New_York'))
    return int(at.timestamp())*1_000_000_000


def save(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(jsonable(value),indent=2)+'\n')
    return dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def build(case_id):
    catalog=load_catalog(verify_sources=True)
    case=next(c for c in catalog['cases'] if c['case_id']==case_id)
    method=case['method_id'];configuration=catalog['configurations'][case['configuration_ids'][0]]
    instrument=158704 if case_id=='GB-FAIL-2025-11-20' else 42002475
    branch='nyam_box' if method=='GB-FAIL' else 'source_long' if method=='GB-VWAP' else 'internal_rotation'
    side='short' if method=='GB-FAIL' else 'long'
    specs={row['role']:row for row in case['native_control_windows']}
    end=max(exact_ns(row['end_et']) for row in specs.values())
    candidate=dict(candidate_id=case_id+':native-control',method_id=method,branch=branch,side=side,
       instrument_id=instrument,session_date_et=case_id[-10:],decision_at=end,band_ids=[case_id+':selected-reference'],
       object_ids=[],assertion_ids=[],cohort_id='fixed_source_comparisons_v2',evidence_mode='native_control',
       variant='comparison',source_case_id=case_id,operands={},
       cutoff_interpretation='Declared measurement cutoff; actual author entry timestamp/fill is not inferred.')
    objects=[];roles=[];windows=[];bindings={}
    def native(role,rid,inputs,*,dataset=BARS,parents=(),add_role=True):
        spec=specs[role];start,stop=exact_ns(spec['start_et']),exact_ns(spec['end_et'])
        win=collect_window(ROOT/'data',dataset,start,stop,instrument,required='ohlcv' if dataset==BARS else 'trades')
        windows.append(win)
        obj=dict(object_id=case_id+':'+role+':'+rid,recipe_id=rid,method_id=method,branch_scope=[branch],
           author=configuration['author'],instrument_id=instrument,parent_ids=[p['object_id'] for p in parents],
           source_ref='; '.join(case['source_refs']),source_version='source-cases-v2.0.0',value={},units={},
           formation_start=start,formation_end=stop,as_of=stop,known_at=stop,state='computed',hole_ids=[],evidence_ids=[],
           raw_member_locators=win.raw_member_locators,inputs={**inputs,'use_at':end,'variant':'comparison'})
        objects.append(obj)
        if add_role:
            roles.append(dict(object_id=obj['object_id'],role=role,method_id=method,author=obj['author'],instrument_id=instrument,
              source_configuration_id=configuration['configuration_id'],source_configuration_version=configuration['version'],
              control_window_id=spec['control_window_id'],control_window_version=spec['version'],
              source_definition=dict(status='inference',value=dict(role=role,formation_start=start,formation_end=stop,
                   session_date_et=candidate['session_date_et']),source_refs=spec['source_refs'],reason=spec['reason'])))
        return obj
    def bind(obj,*fields):
        for field in fields:bindings[field]=dict(object_id=obj['object_id'])
    if method=='JJ-TBR':
        ref=native('source_range','O005',dict(range_id=case_id+':06-09'))
        bind(ref,'range_frozen','range_known_at')
    elif method=='GB-VWAP':
        for role in ('asia','london'):
            ref=native(role,'O046',dict(range_id=case_id+':'+role,source_clock_verified=False))
            bind(ref,role+'_high',role+'_known_at')
        breakout=native('breakout_candle','O004',dict(kind='time',size_minutes=1))
        bind(breakout,'breakout_at','breakout_close')
        spec=specs['vwap_at_retest'];vwap=native('vwap_at_retest','O030',dict(reset_id='comparison-prior-1800',
            reset_at=exact_ns(spec['start_et']),as_of=exact_ns(spec['end_et']),reset_verified=True,basis='HLC3'))
        bind(vwap,'vwap_at_retest','vwap_known_at','vwap_reset_verified')
        retest=native('retest_candle','O002',dict(reference_parent_id=vwap['object_id']),parents=[vwap])
        bind(retest,'retest_at','retest_low','retest_high')
    else:
        ref=native('failure_reference','O046',dict(range_id=case_id+':09-10',clock_variant='nyam',source_clock_verified=True))
        bind(ref,'reference_px','reference_known_at')
        bar=native('failure_confirmation','O004',dict(kind='time',size_minutes=2),add_role=False)
        sweep=native('failure_confirmation','O047',dict(reference_parent_id=ref['object_id'],measurement_side='high',
              confirmation_bar_parent_id=bar['object_id']),dataset=TRADES,parents=[ref,bar])
        # These are measurements of a selected NQ comparison window. The
        # source shows an MNQ sweep entry and no exact execution clock. Its
        # later close/MSS must not become the source's entry prerequisites.
    audit=json.loads((ROOT/'implementation/src/trading_research/research/method_pack/discovery_audit.json').read_text())
    declared={row['field']:row for row in audit['methods'][method]['branches'][branch]['unavailable_inputs']}
    limitations=[]
    for field in fields_for(method):
        if field in bindings:continue
        row=declared.get(field)
        kind=row['kind'] if row else 'supplied_record_missing'
        reason=row['reason'] if row else 'This retrospective source comparison contains no actual selected source observation/process record for this operand.'
        item=dict(field=field,kind=kind,reason=reason,source_ref='; '.join(case['source_refs']))
        if kind=='source_definition':
            item['source_setting']=dict(status='unknown',value=None,source_refs=case['source_refs'],reason=reason)
        limitations.append(item)
    candidate['object_ids']=[o['object_id'] for o in objects]
    resolver=AuditedWindowResolver(ROOT/'data')
    episode=assemble_episode(candidate,objects,bindings=bindings,roles=roles,limitations=limitations,resolver=resolver)
    result=dict(case_id=case_id,source_case=case,measurement_result=episode.result,bindings=episode.bindings,
       assembly_holes=episode.holes,resolved_objects=list(episode.parsed[1].values()),
       native_window_audits=resolver.audit_records(),
       source_case_agreement='Literal native computations and declared sequence are reviewable; no author fill or complete source-method pass is inferred.',
       faithful_disagreements=None,historical_candidates=None)
    if method=='GB-FAIL':
        result['comparison_only_fields']=['sweep_at','sweep_high','sweep_low','confirm_close']
        result['source_predicate_exclusion_reason']='The selected NQ 10:38–10:40 measurements are not observed MNQ source sweep/fill or confirmation records. They remain in resolved_objects; actual source entry is the earlier sweep, with later MSS/FVG retained only as annotations.'
    # In-process admission tokens belong to the interpreter, never serialized.
    for obj in result['resolved_objects']:obj.pop('_source_admission',None)
    manifest=save(OUT/(case_id+'.episodes.json'),episode.manifest)
    results=save(OUT/(case_id+'.result.json'),result)
    print(json.dumps(dict(case_id=case_id,verdict=episode.result['verdict'],software_complete=episode.result['software_complete'],
        native_object_count=len(objects),missing_operand_count=len(episode.holes),manifest=manifest,result=results)),flush=True)
    return dict(case_id=case_id,manifest=manifest,result=results)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--case',choices=['JJ-range-control-2026-02-24','GB-VWAP-2026-02-24','GB-FAIL-2025-11-20','all'],default='all');args=parser.parse_args()
    cases=['JJ-range-control-2026-02-24','GB-VWAP-2026-02-24','GB-FAIL-2025-11-20'] if args.case=='all' else [args.case]
    rows=[build(case) for case in cases]
    save(OUT/'manifest-index.json',rows)


if __name__=='__main__':main()
