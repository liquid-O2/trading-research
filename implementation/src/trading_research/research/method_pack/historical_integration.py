"""Native membership, clock separation and derived admission regressions."""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timezone
from decimal import Decimal
import importlib.util
import json
from pathlib import Path

from .event_time import aggregate_events, build_event_window, EventWindow, MINUTE, SECOND, vendor_diagnostics
from .event_cache import ownership, cached_window
from .empirical_tape import NativeTradeStream
from .empirical_protocol import content_hash
from .mbp1_views import iter_mbp1_window, plan_window
from .native_resolution import file_digest, NativeEvidenceError
from .historical_runner import BASE, ROOT, OLD, immutable_json
from .derived_admission import admitted_recovery, admitted_tail, RECOVERY
from .session_policy import NQSessionPolicy


def multiset(events):
    return Counter((r['event_ns'],str(r['price']),r['executed_size'],r['side'],int(r.get('flags') or 0)) for r in events)


def counter_hash(counter):return content_hash([[list(k),v] for k,v in sorted(counter.items())])


def _legacy_reader():
    path=ROOT/'implementation/reports/phase1-live/data-recovery-v1/audit_tape.py'
    spec=importlib.util.spec_from_file_location('phase1_legacy_readonly_tape_util',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def old_tape_windows():
    windows=[];helper=_legacy_reader()
    for checkpoint_path in sorted((OLD/'checkpoints').glob('tape-*.json')):
        checkpoint=json.loads(checkpoint_path.read_text());path=Path(checkpoint['artifact_path'])
        if file_digest(path)!=checkpoint['artifact_sha256']:raise NativeEvidenceError('historical tape artifact changed')
        artifact=json.loads(path.read_text())
        for role in ('tape','prior_profile'):
            source=artifact[role];start,end,instrument=source['formation_start'],source['formation_end'],source['instrument_id']
            plan=plan_window(ROOT/'data',start,end,ownership=ownership(str(ROOT/'data')))
            mbp=list(iter_mbp1_window(plan,trades_only=True,instrument_id=instrument))
            try:
                standalone=NativeTradeStream(ROOT/'data','quantpad/cme__nq-continuous-futures__trades',start,end,instrument)
                tape=list(standalone)
            except NativeEvidenceError as exc:
                if str(exc)!='no canonical native tape file overlaps requested interval':raise
                tape=[]
            a,b=multiset(mbp),multiset(tape)
            first=min((r['event_ns'] for r in tape),default=None)
            shared=Counter({k:v for k,v in a.items() if first is not None and k[0]>=first})
            overlap_matches=shared==b if first is not None else None
            if first is not None and not overlap_matches:
                raise NativeEvidenceError('standalone/owned MBP execution membership differs in shared observed window')
            transformed=aggregate_events(mbp,start,end,instrument,seconds=(60,))
            year=datetime.fromtimestamp(start/SECOND,timezone.utc).year
            vendor_path=ROOT/f'data/quantpad/cme__nq-continuous-futures__ohlcv-1m/{year}.parquet'
            vendor=helper.native_rows(vendor_path,start,end,instrument,bars=True)
            vendor_rows=[dict(start=r['t'],**{k:r[k.lower()] for k in 'OHLCV'}) for r in vendor]
            diagnostic=vendor_diagnostics(transformed['bars']['60'],vendor_rows)
            source_files={str(ROOT/'data'/r['path']):r['sha256'] for r in source['source_files']}
            source_files.update({r['path']:file_digest(Path(r['path'])) for r in plan['owned_spans']})
            source_files[str(vendor_path)]=file_digest(vendor_path)
            window={'date':checkpoint['session_date'],'role':role,'start_ns':start,'end_ns':end,'instrument_id':instrument,
                'mbp_executions':len(mbp),'standalone_executions':len(tape),'full_window_multiset_equal':a==b,
                'shared_observed_multiset_equal':overlap_matches,'standalone_first_event_ns':first,
                'mbp_only_executions':sum((a-b).values()),'standalone_only_executions':sum((b-a).values()),
                'mbp_multiset_sha256':counter_hash(a),'standalone_multiset_sha256':counter_hash(b),
                'physical_membership_sha256':transformed['membership_sha256'],
                'source_files':source_files,'owned_plan':plan,'vendor_diagnostics':diagnostic,
                'disposition':'owned MBP event input available' if mbp else 'no observed executions; calendar/coverage must decide scope',
                'validation':'no receive-clock equality gate; exact multiset within the actual shared event interval'}
            windows.append(window)
            print(json.dumps({k:window[k] for k in ('date','role','mbp_executions','standalone_executions','shared_observed_multiset_equal')}),flush=True)
    if len(windows)!=8:raise NativeEvidenceError('old tape date/current/prior membership is not exactly eight windows')
    return windows


def tail_check():
    rows,receipt=admitted_tail()
    instruments={str(r['instrument_id']) for r in rows}
    if len(instruments)!=1:raise NativeEvidenceError('tail has multiple instruments; explicit partition required')
    start=min(r['start_ns'] for r in rows);end=max(r['end_ns'] for r in rows)
    doc=build_event_window(ROOT/'data',start,end,next(iter(instruments)),ownership=ownership(str(ROOT/'data')),seconds=(60,))
    fresh={r['start_ns']:r for r in doc['bars']['60']}
    mismatches=[]
    for old in rows:
        new=fresh.get(old['start_ns'])
        if new is None or any(old.get(k) is None and new.get(k) is not None or old.get(k) is not None and
                (new.get(k) is None or Decimal(str(old[k]))!=Decimal(str(new[k]))) for k in 'OHLCV'):
            mismatches.append(old['start_ns'])
    if mismatches or len(fresh)!=len(rows):raise NativeEvidenceError('fresh owned tail transformation differs')
    return {**receipt,'start_ns':start,'end_ns':end,'instrument_id':next(iter(instruments)),
        'fresh_rows':len(fresh),'mismatches':mismatches,'fresh_physical_membership_sha256':doc['membership_sha256'],
        'sources':doc['source_files'],'raw_sources_unchanged':doc['raw_sources_unchanged']}


def recovery_check():
    # Reuse the already performed full native-second derivation. Verify its
    # actual input/artifact hashes again before admitting it to this registry.
    path=BASE/'DERIVED_ADMISSION.json';receipt=json.loads(path.read_text())
    if not receipt.get('transformations_verified'):raise NativeEvidenceError('recovery transformation was not verified')
    for item in receipt['source_files']+receipt['source_manifests']:
        if file_digest(Path(item['path']))!=item['sha256']:raise NativeEvidenceError('recovery input changed')
    recovered=json.loads(Path(RECOVERY).read_text())
    artifact=Path(recovered['artifact']['path'])
    if file_digest(artifact)!=recovered['artifact']['sha256']:raise NativeEvidenceError('recovery artifact changed')
    days=Counter(datetime.fromtimestamp(json.loads(line)['start_ns']/SECOND,timezone.utc).date().isoformat()
        for line in artifact.read_text().splitlines() if json.loads(line)['start_ns']>=1577836800*SECOND)
    return {'admission_path':str(path),'admission_sha256':file_digest(path),
        'recovered_study_keys':receipt['recovered_study_keys'],'august_equal_overlaps':receipt['equal_overlaps_not_added'],
        'admitted_unique_keys':receipt['admitted_keys'],'outside_study_keys':receipt['outside_study_keys'],
        'utc_dates':dict(days),'clock_basis':'vendor_receive_time',
        'method_input_use':'admitted as vendor-clock recovery and diagnostics; no vendor bar inserted into the event-time method path',
        'native_transformations_verified':True,'source_files':receipt['source_files'],'source_manifests':receipt['source_manifests']}


def july_gap():
    from .empirical_market import clock
    from datetime import date
    start,end=clock(date(2020,6,30),'18:00'),clock(date(2020,6,30),'20:00')
    # Report this declared gap window exactly, without substituting a later
    # quiet/busy interval. Native observations do not certify feed continuity.
    from .event_cache import contract_at
    inst=contract_at(ROOT/'data',start)['instrument_id']
    doc,receipt=cached_window(ROOT/'data',start,end,inst,seconds=(60,))
    return {'start_ns':start,'end_ns':end,'instrument_id':inst,'executions':doc['row_count'],
        'coverage':EventWindow(doc,schedule=NQSessionPolicy()).coverage(start,end),'input_receipt':receipt,
        'gap_resolution':'unresolved; observed subset and unknown feed completeness retained'}


def run_integration(output=BASE/'NATIVE_INTEGRATION.json'):
    report={'schema':'phase1-native-integration-v2','old_tape_windows':old_tape_windows(),
        'derived_recovery':recovery_check(),'tail':tail_check(),'july_gap':july_gap(),
        'calendar_recovery':json.loads((BASE/'calendar-evidence/recovery-attempt.json').read_text()),
        'calendar_policy_sha256':file_digest(Path(__file__).with_name('nq_session_policy_v2.json'))}
    report['report_sha256']=content_hash(report)
    immutable_json(output,report)
    return report
