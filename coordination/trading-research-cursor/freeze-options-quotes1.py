from pathlib import Path
import json,hashlib,datetime

ROOT=Path('/workspace/trading-research'); DATA=Path('/workspace/data')
def write(path,value):
    raw=(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    with path.open('xb') as f:f.write(raw)
    return {'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw),'kind':value['kind']}
def ref(path):
    raw=path.read_bytes();return {'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}
oi=json.loads((ROOT/'validation/OPTIONS_OI_REPORT_LIFECYCLE_V1.json').read_text())
files=[];datasets=[]
for directory in sorted((DATA/'thetadata-opra').iterdir()):
    if not directory.is_dir() or '__quote-1m__' not in directory.name or 'legacy' in directory.name:continue
    if not any(x in directory.name for x in ('__dte14__strike-range','__dte60__atm10','__dte60-full-chain')):continue
    chain=directory.name.split('__')[1].split('-')[0].upper()
    family='vix_full' if chain=='VIX' else 'near' if '__dte14__' in directory.name else 'broad'
    current=[]
    for path in sorted(directory.iterdir()):
        if not(path.name.endswith('.parquet') or path.name.endswith('.empty.json')):continue
        day=path.name[:10];datetime.date.fromisoformat(day)
        if not '2020-01-01'<=day<='2026-09-03':continue
        current.append({'path':str(path.relative_to(DATA)),'dataset_id':str(directory.relative_to(DATA)),
            'chain':chain,'role':'quote','source_family':family,'request_date':day,'size_bytes':path.stat().st_size})
    files.extend(current);datasets.append({'dataset_id':str(directory.relative_to(DATA)),'chain':chain,'source_family':family,
        'source_file_count':len(current),'source_bytes':sum(x['size_bytes'] for x in current)})
support_dirs=[('underlier_daily',DATA/'free-sources/yahoo__cash-daily__normalized'),
    ('rates',DATA/'free-sources/fred__usd-rates__normalized'),('corporate_actions',DATA/'free-sources/yahoo__corporate-actions__normalized'),
    ('qqq_minute',DATA/'quantpad/nasdaq__qqq-etf__ohlcv-1m'),('spy_minute',DATA/'quantpad/nyse-arca__spy-etf__ohlcv-1m')]
for role,directory in support_dirs:
    for path in sorted(directory.iterdir()):
        if path.suffix!='.parquet':continue
        files.append({'path':str(path.relative_to(DATA)),'dataset_id':str(directory.relative_to(DATA)),
            'role':role,'size_bytes':path.stat().st_size})
manifest={'kind':'options_quote_source_files_v1','file_count':len(files),'files':files,
    'total_bytes':sum(x['size_bytes'] for x in files),'maximum_file_bytes':max(x['size_bytes'] for x in files),
    'note':'Filesystem metadata only. Actual row counts, source hashes and schemas require registered admission; no science executed.'}
manifest_ref=write(ROOT/'validation/OPTIONS_QUOTE_SOURCE_FILES_V1.json',manifest)
contract={
 'kind':'options_quote_quality_support_contract_v1','version':1,'family':'Research-Options-Quote-Quality-Support-acquired-v1',
 'authority':'Latest user2026-09-08T20:41 requires all Deliverable1 measurements/statistics/timing before Context. This is the distinct quote-quality scientific population, preserving OI and other family budgets.',
 'scope_ids':['O01','O01.COVERAGE','O02.BIDASK_IV','X02'],
 'scope':'All acquired quote-minute quality/coverage, near-broad comparisons, full intended-date cut boards and source-clock age; underlier/rate/action support and joined observed listing/OI support. No valuation, Greeks, dealer positions or Context inference.',
 'source_file_manifest':manifest_ref,'source_datasets':datasets,'cash_calendar':oi['cash_calendar'],'population':oi['population'],
 'source_catalog':oi['source_catalog'],'oi_protocol':ref(ROOT/'validation/OPTIONS_OI_REPORT_LIFECYCLE_V1.json'),
 'identity':'Exact chain+OSI+expiration+millistrike+right. Validate OSI root/date/right/strike against source columns; preserve file_id and row_index. Chain names NDX/NDXP/SPX/SPXW remain distinct. No binary float tolerance changes to accepted millistrike identity.',
 'clocks':{
   'actual':'ts_event_ns is the exact recorded sampling/source clock. received_at_ns,published_at_ns,known_at_ns,last_actual_update_ns are NULL; causal_feature_eligible false. Do not call a sampled unchanged quote the actual last update.',
   'scenario':'Retrospective asof uses ts_event<=cut and request_date<=cut date, newest time within current intended session only. Do not carry previous-session quote into a new session silently. Preserve effective acquisition availability if request date is later than source date.',
   'cuts_local':['09:30','10:00','15:00','cash_close'],'diagnostic_cuts_utc':['15:00'],
   'ages':'sample_age=cut-latest sampled timestamp; unchanged_payload_age=cut-first observed timestamp of current identical payload run; last_actual_update_age unknown. Both source ages numeric separately, gaps/invalid/conflict break certainty of unchanged run. Do not use unchanged age as sample staleness.',
   'stale_threshold_seconds':[60,300,900],
   'session':'Actual cash open/close including early closes. Nonapplicable 15:00 after early close retained as not_applicable, not missing quote. 15:00UTC diagnostic separate.'},
 'duplicates':'Within and across near/broad: same identity/time and identical all bid/ask/size/exchange/condition payload is one alias with multiplicity/provenance. Same identity/time different payload is conflict with no winner or usable price. Later nonconflicting observations can restore quote; do not fall back through a current conflict to an older valid quote. Source-family own and union/matched populations all retained.',
 'quality':{
   'base_partition':['invalid_identity','invalid_clock','invalid_numeric','conflict','all_zero','one_sided','crossed','locked','two_sided'],
   'flags':['condition_zero','nonpositive_size','negative_size','zero_bid','zero_ask','negative_price','nonfinite_price','session_outside','request_date_mismatch'],
   'usable':'Known valid identity and clock; finite bid>0, ask>=bid, both sizes>0, no conflict. Locked usable but separately flagged. Conditions/exchanges descriptive; do not invent eligibility semantics for undocumented numeric condition codes.',
   'denominators':'Input raw rows; distinct identity/time observations; each source-family distinct rows; union unique records; matched exact-time near/broad pairs; cut observed contracts; observed listing universe. Report each separately; marginal flags overlap and do not sum to partition totals.'},
 'coverage':'Every intended cash date x7chains x5cuts, own source families plus deduplicated union. Missing file, JSON empty marker, no prior sampled minute, no quote, unlisted quote, listed unquoted, unavailable listing denominator distinct. Missing near monthly quotes do not prove outage nor no listed option; do not infer zero-DTE membership. Quoted universe union listings and OI, no absent=zero.',
 'dte_buckets':['expired','0','1','2-7','8-14','15-30','31-60','61+'],
 'oi_join':'Use accepted OI compact identity/reports/asof intervals with exact reconstruction, without redoing OI definitions or original OI scans. Daily listed is observed acquisition listing, not PIT. At every quote cut select same sourceclock OI as accepted interval ledger, retain missing/ambiguous/stale/expired; OI-weighted coverage denominator only available nonnegative OI, zero total ->undefined. Report number/amount of missing OI separately. VIX listing unknown. Pilot may bind accepted first16-date OI; full requires accepted full OI.',
 'support':'QQQ/SPY latest eligible complete one-minute bar at/before cut; preserve bar close/known source assumption and gaps. Cash NDX/SPX daily close is same-date only at/after declared cashclose as a retrospective convention, earlier cuts use prior available cash-date close; actual publication unknown. VIX cash comes from already accepted daily-volatility evidence in subsequent valuation support if needed, not an invented source here. FRED has current vintage and no historical PIT proof; preserve date/realtime_start/end and each tenor. Corporate actions have exdates, dividend/split only and NULL announcement clocks; future exdate cannot be a known-at feature. These are support diagnostics for later explicitly retrospective valuation, not causal features.',
 'storage':'Do not copy billions of quote rows. Store typed compact cut boards with source addresses and payload, exact aliases/conflicts and input-quality date aggregates; full unchanged-run counts/ages can be reduced online. Original authenticated source files plus schema/sort/dedup rule reconstruct arbitrary minute history. An interval ledger is optional only if measured smaller than source and downstream necessary; source-reference recipe is sufficient. Per-contract cut provenance must reconstruct exact payload and run-start evidence. Exceptions may be reason/mask ranges with original addresses, not wide duplicate invalid tape.',
 'statistics':{**oi['statistics'],'groups':'chain/source_family/year/stage/cut/right/DTE bucket; all source-row, unique-row, cut and matched/listed populations separately. Metric-specific independent cash dates, raw support, exact quantiles, equal-date means; paired near-broad on same physical contract/cut/time and own support separately.',
   'metrics':'Quality-class/flag fractions, quoted/listed/OI-covered fractions, bid/ask/mid/spread absolute and relative (positive mid only), sample age and unchanged-payload age separately, stale thresholds, near-broad agreement/conflict, missing files/empty markers/no sample, underlier/rate/action support. No implied-volatility inference in this module.'},
 'operational_pilot':'First8intended cash dates, all7chains/allsourcefamilies/all5cuts, no fitted quality/expiry selection. Full measured gate uses source rows+compressed bytes and output/cut counts with1.5margin and separately measured fixed tests/statistics cost.',
 'partitioning':'Optional seven chain shards, owned days/chains explicit, same-family supervised children under actual17.85CPU/82,999,996,416B. Full reducer authenticates each partition, all input and implementation identities and each own statistical group. No child spawns itself.',
 'resources':{'cpu_budget_seconds':90000,'max_attempts':8,'mode_cpu_seconds':{'admit':1800,'pilot':1200,'full':60000},'hard_cpu_margin':10,
   'memory_bytes':8*1024**3,'maximum_source_file_bytes':max(manifest['maximum_file_bytes']+1024**2,128*1024**2),
   'per_attempt_output_bytes':16*1024**3,'maximum_study_output_bytes':48*1024**3,'wall_seconds':10800},
 'remaining':'IV/Greeks/surfaces, trade signing/exposure/holdings scenarios, VIX implied-surface construction and futures options remain subsequent D1 branches. Complete quote-quality population alone does not complete options.'}
out=write(ROOT/'validation/OPTIONS_QUOTE_QUALITY_SUPPORT_V1.json',contract)
print(json.dumps({'protocol':out,'files':len(files),'quote_datasets':len(datasets),'bytes':manifest['total_bytes'],'max_file':manifest['maximum_file_bytes']}))
