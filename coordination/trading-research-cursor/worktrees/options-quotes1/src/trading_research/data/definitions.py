"""Full-field bounded futures-definition audit with explicit external term joins."""

from collections import Counter
from dataclasses import asdict,dataclass
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import resource
import time

from trading_research.data.events import encode_fields,decode_fields
from trading_research.errors import ContractError,DependencyUnavailable,IntegrityError
from trading_research.foundations.contracts import InstrumentKey
from trading_research.foundations.instruments import InstrumentDefinition,InstrumentRetirement,instrument_identity
from trading_research.foundations.time import Clocks,AvailabilityBasis
from trading_research.operations.artifacts import code_manifest,code_snapshot,digest,file_digest
from trading_research.operations.trials import TrialRegistry


@dataclass(frozen=True)
class ProductTermsEvidence:
    root:str
    multiplier:Decimal
    tick_size:Decimal|None
    known_at:int
    source_version:str
    source_urls:tuple[str,...]
    historical_basis:str

    def __post_init__(self):
        if self.root not in ('NQ','ES') or not self.source_version or not self.source_urls or self.historical_basis not in ('published_product_reference','verified_historical_terms'):
            raise ContractError("external product terms require explicit provenance and historical interpretation")
        if any(not isinstance(v,Decimal) or not v.is_finite() or v<=0 for v in (self.multiplier,*([] if self.tick_size is None else [self.tick_size]))):raise ContractError("positive exact product terms required")


def futures_definition(row:dict,*,root:str,source_id:str,source_version:str,latency_ns:int,latency_scenario:str,external_terms:ProductTermsEvidence|None=None):
    raw=encode_fields(row)
    if encode_fields(decode_fields(raw))!=raw:raise IntegrityError("definition raw-field roundtrip failed")
    if type(latency_ns) is not int or latency_ns<0 or not latency_scenario:raise ContractError("missing strategy receipt requires a named nonnegative delay assumption")
    if row.get('instrument_class')!='F' or not re.fullmatch(root+r'[HMUZ]\d{1,2}',row.get('raw_symbol') or ''):
        raise DependencyUnavailable("definition is not a classified canonical quarterly mini outright")
    if row.get('security_update_action')=='D':raise DependencyUnavailable("deleted definition requires a known-time retirement record")
    activation,expiration=row.get('activation'),row.get('expiration')
    if any(type(v) is not int for v in (activation,expiration)) or not 0<=activation<expiration<2**63:
        raise DependencyUnavailable("missing/sentinel activation or expiry")
    provider=row.get('ts_recv');event=row.get('t')
    if type(provider) is not int or not 0<provider<2**63 or type(event) is not int or not 0<event<2**63:
        raise DependencyUnavailable("missing definition event/provider-receipt clock")
    known=max(provider,event)+latency_ns
    tick=None if row.get('min_price_increment') is None else Decimal(str(row['min_price_increment']))
    multiplier=None if row.get('contract_multiplier') is None else Decimal(str(row['contract_multiplier']))
    external_version=None
    if external_terms:
        if external_terms.root!=root or external_terms.known_at>known:raise DependencyUnavailable("external product terms unavailable at the modeled definition publication")
        if tick is not None and external_terms.tick_size is not None and tick!=external_terms.tick_size or multiplier is not None and multiplier!=external_terms.multiplier:
            raise IntegrityError("raw and external tick/multiplier terms conflict")
        tick=external_terms.tick_size if tick is None else tick;multiplier=external_terms.multiplier if multiplier is None else multiplier;external_version=digest(external_terms)
    version=digest({'source_id':source_id,'source_version':source_version,'raw':raw,'external_terms':external_version,'latency_ns':latency_ns,'scenario':latency_scenario})
    key=InstrumentKey('quantpad','GLBX.MDP3',str(row['instrument_id']),row['raw_symbol'],root,version,expiration)
    clocks=Clocks(event,known,source_version,AvailabilityBasis.ASSUMED,provider_received_at=provider,valid_from=activation,valid_until=expiration,assumption_id=latency_scenario)
    return InstrumentDefinition(key,clocks,'future',multiplier,tick)


def futures_retirement(row:dict,*,previous:InstrumentDefinition,source_id:str,source_version:str,
                       latency_ns:int,latency_scenario:str):
    """Decode a deletion with its explicit known prior definition; preserve raw identity."""
    raw=encode_fields(row)
    if encode_fields(decode_fields(raw))!=raw:raise IntegrityError("retirement raw-field roundtrip failed")
    if row.get('security_update_action')!='D':raise ContractError("retirement adapter requires a deletion record")
    if (not isinstance(previous,InstrumentDefinition) or previous.classification!='future' or previous.key.underlying not in ('NQ','ES')
            or (previous.key.provider,previous.key.venue)!=('quantpad','GLBX.MDP3')):
        raise DependencyUnavailable("quarterly mini retirement requires a known prior outright")
    if row.get('instrument_class') not in (None,'','F'):
        raise ContractError("deletion class differs from the prior outright")
    if str(row.get('instrument_id'))!=previous.key.instrument_id:
        raise ContractError("deleted record and prior instrument ID differ")
    if row.get('raw_symbol') not in (None,'',previous.key.raw_symbol):
        raise ContractError("deleted symbol and prior instrument lifetime differ")
    for field,expected in (('activation',previous.clocks.valid_from),('expiration',previous.key.expiry_at)):
        if row.get(field) is not None and (type(row[field]) is not int or row[field]!=expected):
            raise ContractError("deleted lifetime boundary differs from the prior outright")
    if type(latency_ns) is not int or latency_ns<0 or not latency_scenario or not source_id or not source_version:
        raise ContractError("retirement needs source bytes/version and explicit nonnegative latency")
    event,received=row.get('t'),row.get('ts_recv')
    if any(type(v) is not int or not 0<v<2**63 for v in (event,received)):
        raise DependencyUnavailable("missing deletion event/provider-receipt clock")
    known=max(event,received)+latency_ns
    if previous.clocks.known_at>=known:raise DependencyUnavailable("prior definition not available before deletion")
    clocks=Clocks(event,known,source_version,AvailabilityBasis.ASSUMED,provider_received_at=received,
                  assumption_id=latency_scenario)
    identity=digest({'source_id':source_id,'source_version':source_version,'raw':raw,
                     'previous':previous.key.definition_version,'clocks':clocks})
    return InstrumentRetirement(identity,previous.key.definition_version,instrument_identity(previous),event,clocks)


def audit_definitions(*,data_root:Path,output_root:Path,years:tuple[int,...]=(2021,2022,2023,2024,2025),roots:tuple[str,...]=('NQ','ES')):
    import pyarrow.parquet as pq
    package=Path(__file__).resolve().parents[3];registry=TrialRegistry(output_root)
    selections=tuple(f'quantpad/cme__{root.lower()}-continuous-futures__definition/{year}.parquet' for root in roots for year in years)
    protocol={'purpose':'complete-selected-definition-partition-fidelity','partitions':selections,'maximum_rows':10000,'maximum_file_bytes':64*1024**2,
              'receipt_assumption':'provider-received-plus-250ms','external_multiplier_fill':'none; report missing raw multipliers separately','economic_evaluation':False}
    registry.register_family('B01-definition-partitions-v1',scope_ids=('F01','F02','B01.1','B01.5'),protocol=protocol,max_attempts=4,cpu_budget_seconds=240)
    source_hashes={p:file_digest(data_root/p) for p in selections};snapshot=code_snapshot(package,registry.artifacts)
    trial=registry.register(name='Full selected NQ/ES definition partitions',family='B01-definition-partitions-v1',stage='engineering',configuration=protocol,code_hash=digest(code_manifest(package)),data_hashes=source_hashes,fold_version='no-fit',target_version='full-schema-definition-fidelity-v1')
    attempt=registry.start(trial,cpu_reservation_seconds=60);start=time.monotonic();cpu=time.process_time();rows=0;reports=[];definitions=[]
    try:
        for relative in selections:
            path=data_root/relative
            if path.stat().st_size>protocol['maximum_file_bytes']:raise ContractError("definition file exceeds registered size bound")
            pf=pq.ParquetFile(path);root='NQ' if '__nq-' in relative else 'ES';classes=Counter();errors=Counter();updates=Counter();missing=Counter();content=hashlib.sha256();parsed=0;file_rows=0;ids=set()
            for batch in pf.iter_batches(batch_size=1024,use_threads=False):
                for row in batch.to_pylist():
                    rows+=1
                    ordinal=file_rows;file_rows+=1
                    if rows>protocol['maximum_rows']:raise ContractError("definition row budget exceeded")
                    raw=encode_fields(row);content.update(raw);content.update(b'\n');classes[str(row.get('instrument_class'))]+=1;updates[str(row.get('security_update_action'))]+=1
                    missing.update(k for k,v in row.items() if v is None)
                    try:
                        d=futures_definition(row,root=root,source_id=relative+':row:'+str(ordinal),source_version=source_hashes[relative],latency_ns=250000000,latency_scenario='definition-provider-plus-250ms')
                        parsed+=1;ids.add(d.key.instrument_id)
                        definitions.append({'source_path':relative,'raw_fields_hash':digest(raw),'instrument_id':d.key.instrument_id,'raw_symbol':d.key.raw_symbol,'definition_version':d.key.definition_version,
                                            'known_at':d.clocks.known_at,'event_at':d.clocks.event_at,'activation':d.clocks.valid_from,'expiration':d.key.expiry_at,'tick_size':None if d.tick_size is None else str(d.tick_size),
                                            'raw_multiplier':None if d.multiplier is None else str(d.multiplier),'execution_eligibility':d.eligibility('execution')})
                    except (ContractError,DependencyUnavailable,IntegrityError) as exc:errors[type(exc).__name__+': '+str(exc)]+=1
            if file_rows!=pf.metadata.num_rows:raise IntegrityError("full partition decode disagrees with footer row count")
            reports.append({'path':relative,'whole_file_hash':source_hashes[relative],'full_schema':str(pf.schema_arrow),'rows':file_rows,'decoded_outright_rows':parsed,
                            'distinct_outright_instruments':len(ids),'instrument_classes':dict(classes),'security_updates':dict(updates),'missing_fields':dict(missing),'unresolved_rows':dict(errors),'all_row_field_hash':content.hexdigest()})
            pf.close()
            if file_digest(path)!=source_hashes[relative]:raise IntegrityError("definition input changed during audit")
        report={'success':True,'trial_id':trial,'attempt_id':attempt,'code_snapshot':asdict(snapshot),'partitions':reports,'definitions':definitions,'total_rows':rows,
                'cpu_seconds':time.process_time()-cpu,'wall_seconds':time.monotonic()-start,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                'depth':'complete_selected_partitions','operation':'raw futures definition identity/field audit','economic_runs':0,
                'limitations':['No missing raw multiplier is filled from a guessed value.','Whole-file identities and all supplied fields are retained; purpose-specific unresolved terms remain explicit.','Provider receipt plus 250ms is a modeled strategy-availability scenario, not actual receipt capture.','This does not certify the completeness of all simultaneously listed outright contract tapes.']}
        ref=registry.artifacts.put_json(report,kind='full_selected_definition_audit');registry.finish(attempt,status='succeeded',cpu_seconds=report['cpu_seconds'],wall_seconds=report['wall_seconds'],peak_rss_bytes=report['peak_rss_bytes'],reason='Complete selected definition files examined with unresolved terms preserved.',result_artifacts=(asdict(ref),))
        return {'success':True,'rows':rows,'partitions':len(reports),'report':str(registry.artifacts.path(ref)),'artifact':asdict(ref)}
    except BaseException as exc:
        ref=registry.artifacts.put_json({'error':type(exc).__name__,'reason':str(exc),'completed_partitions':reports,'rows_read':rows,'code_snapshot':asdict(snapshot)},kind='failed_definition_audit')
        registry.finish(attempt,status='failed',cpu_seconds=time.process_time()-cpu,wall_seconds=time.monotonic()-start,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,reason=str(exc),result_artifacts=(asdict(ref),));raise


if __name__=='__main__':
    root=Path(__file__).resolve().parents[3]
    print(json.dumps(audit_definitions(data_root=root.parent/'data',output_root=root/'evidence/trials'),indent=2))
