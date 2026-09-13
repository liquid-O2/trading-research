#!/usr/bin/env python3
"""Execute only factual-calendar dependencies under a separately frozen identity."""
import argparse
from datetime import date, timedelta, datetime, timezone
import json
from pathlib import Path
import sys
sys.path.insert(0, '/workspace/implementation/src')

from trading_research.research.method_pack import historical_runner as hr
from trading_research.research.method_pack import measurement_runner as mr
from trading_research.research.method_pack.historical_features import HistoricalFeatures
from trading_research.research.method_pack.session_policy import ReconstructionSessionPolicy, POLICY_PATH
from trading_research.research.method_pack.empirical_protocol import content_hash

BASE=Path('/workspace/implementation/reports/phase1-live/historical-measurement')
CALENDAR=BASE/'calendar-evidence/RECOVERED_CALENDAR.json'
HELPER=Path(__file__).resolve()


def calendar_document():
    document=hr.read(POLICY_PATH)
    document['exceptions'].update(hr.read(CALENDAR)['exceptions'])
    document['recovered_calendar_receipt']={'path':str(CALENDAR),'sha256':hr.file_digest(CALENDAR)}
    return document


class RecoveredFeatures(HistoricalFeatures):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.policy=ReconstructionSessionPolicy(calendar_document())
        self.window.schedule=self.policy
        self.input_receipts.append({'path':str(CALENDAR),'sha256':hr.file_digest(CALENDAR)})


def freeze(root, parent):
    root=Path(root).resolve();parent=Path(parent).resolve()
    registry,manifest=hr.load_registry(parent)
    updates=[date.fromisoformat(d) for d in hr.read(CALENDAR)['exceptions']]
    affected=[d for d in registry['scope']['evaluation_dates']
              if any(u <= date.fromisoformat(d) <= u+timedelta(days=62) for u in updates)]
    scope=dict(registry['scope'],evaluation_dates=affected,
               selection='all calendar-update dates and following 62 calendar days, covering every bounded structural lookback; no outcome selection',
               sample_kind='factual-input recovery dependency partition of the complete census',
               parent_census={'path':str(parent),'registry_sha256':registry['registry_sha256']},
               recovery_helper={'path':str(HELPER),'sha256':hr.file_digest(HELPER)},
               recovered_calendar={'path':str(CALENDAR),'sha256':hr.file_digest(CALENDAR)})
    hr.immutable_json(root/'protocol/SCOPE.json',scope)
    frozen=hr.freeze(root,scope_path=root/'protocol/SCOPE.json',records_path=CALENDAR,strategy=True)
    composition={'schema':'phase1-calendar-recovery-composition-v1',
        'frozen_at':datetime.now(timezone.utc).isoformat(),
        'primary_run':{'path':str(parent),'registry_sha256':registry['registry_sha256']},
        'recovery_run':{'path':str(root),'registry_sha256':frozen['registry_sha256']},
        'replace_all_daily_units_on_dates':affected,'all_other_dates':'primary census jobs unchanged',
        'setup_implementation_changed':False,'outcome_rules_changed':False,
        'source_input_change':{'path':str(CALENDAR),'sha256':hr.file_digest(CALENDAR)},
        'dependency_bound':'62 days is the maximum existing structural lookback; the P-zone 1100-day published-bar training does not consume matching-calendar exceptions',
        'exposure':'primary census is executing and some prior outcomes exist; calendar facts selected solely from dated official exchange schedules, not setup results'}
    composition['composition_sha256']=content_hash(composition)
    hr.immutable_json(parent/'protocol/CALENDAR_RECOVERY_COMPOSITION.json',composition)
    return {'affected_sessions':len(affected),'recovery_registry_sha256':frozen['registry_sha256'],
            'composition_sha256':composition['composition_sha256']}


def activate(root):
    registry,manifest=hr.load_registry(root)
    for key in ('recovery_helper','recovered_calendar'):
        receipt=registry['scope'][key]
        if hr.file_digest(receipt['path'])!=receipt['sha256']:
            raise ValueError('recovery identity changed: '+key)
    if Path(registry['records']['path'])!=CALENDAR:
        raise ValueError('recovery calendar source differs')
    mr.HistoricalFeatures=RecoveredFeatures


def self_check():
    policy=ReconstructionSessionPolicy(calendar_document())
    assert policy.rth('2023-02-20')['rth_end']=='13:00'
    assert policy.rth('2025-01-09')['windows']==[]
    assert policy.previous_session('2025-01-10')['date']=='2025-01-08'
    assert policy.previous_session('2023-02-21')['date']=='2023-02-20'
    assert policy.rth('2021-12-31')['state']=='regular'
    return {'status':'pass','checks':5,'source':'official dated CME matching schedules; no cash-calendar substitution'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['freeze','run','date','check'])
    p.add_argument('--run-root',default=str(BASE/'run-calendar-recovery-v1'))
    p.add_argument('--parent-root',default=str(BASE/'run-1.0.1'));p.add_argument('--workers',type=int,default=4)
    p.add_argument('--dates');a=p.parse_args()
    if a.command=='check':result=self_check()
    elif a.command=='freeze':result=freeze(a.run_root,a.parent_root)
    else:
        activate(a.run_root)
        result=mr.date_job(a.run_root,a.dates) if a.command=='date' else mr.run(a.run_root,a.workers,a.dates)
    print(json.dumps(hr.serializable(result),indent=2),flush=True)
