from pathlib import Path
import json,datetime
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
state_path=Path('/workspace/planning/trading-research/state/CURRENT.json');d=json.loads(state_path.read_text())
families={};attempts={}
for f in sorted(Path('/workspace/trading-research/evidence/trials/events').glob('*.json')):
 e=json.loads(f.read_text());p=e['payload'];k=e['kind']
 if k=='family': families[p['id']]=dict(p)
 elif k=='budget_amended': families[p['family']].update(p['authorized_limits'])
 elif k=='started': attempts[p['id']]={**p,'status':'running'}
 elif k=='finished': attempts[p['id']].update(p)
for key,family in [('auction_budget','Research-Auction-Flow-acquired-MBP-v1'),('jumbo_budget','Research-Jumbo-acquired-contract-OHLC-v1'),('options_oi_budget','Research-Options-OI-report-lifecycle-v1'),('cross_market_budget','Research-Cross-Market-Alignment-Descriptive-acquired-v1'),('physical_volatility_budget','Research-Physical-OHLC-Volatility-acquired-v1'),('daily_volatility_budget','Research-Daily-Volatility-Complex-acquired-v1'),('scheduled_event_budget','Research-Scheduled-Events-acquired-calendar-v1')]:
 if family not in families:continue
 f=families[family];aa=[a for a in attempts.values() if a['family']==family]
 d.setdefault(key,{}).update(family=family,maximum_attempts=f['max_attempts'],attempts_used=len(aa),attempts_remaining=f['max_attempts']-len(aa),cpu_total_limit_seconds=f['cpu_budget_seconds'],cpu_used_seconds=sum(a.get('cpu_seconds') or 0 for a in aa if a['status']!='running'),cpu_reserved_running_seconds=sum(a['cpu_reservation_seconds'] for a in aa if a['status']=='running'),running_attempts=[a['id'] for a in aa if a['status']=='running'])
current=d['current_deliverable']
current['verification_failures'].append({'branch':'cross_market','attempt':4,'execution':'/workspace/trading-research/reports/cross-market-runs/3224d8b35c2b190d3367073659864677f29ef2ca339e75da8f2c3d71e678fac4/execution.json','tests_passed':37,'exception':'SIGXCPU -24,900CPU bound','cpu_seconds':900.147188,'output_bytes':167312081,'decision':'No full. Unchanged120CPU diagnostic5 identifies scalar pivots/backward joins/writer and per-row group loops; one consolidated performance correction.'})
current['accepted_evidence']['cross_market_diagnostic5']={'execution':'/workspace/trading-research/reports/cross-market-runs/b4e66d6268c9183e6a801990882fce483ce5c9f678eaa997258c42fc9607e055/execution.json','cpu_seconds':121.29358,'scope':'Bounded profile unchanged2020 computation including37fixtures, no population/throughput acceptance','profile':'/workspace/trading-research/reports/cross-market-runs/b4e66d6268c9183e6a801990882fce483ce5c9f678eaa997258c42fc9607e055/outputs/profile.json','repair':'/workspace/coordination/trading-research-cursor/crossmarket6-performance.md'}
workers=['profile_reference_correction:20260909T011010Z-36f51cf9','cross_market_performance:20260909T011745Z-67b30eee']
research=['optionsOIfull6:ed8fc072fb4a7e9a40d0a23274c570e98accbe0c74fa00d0066508904c9c9ff3','options_quote_admission1']
current['active_work']={'codex':'Prepare bounded full quote-quality implementation/runner from frozen13families; prepare profile runner while two corrected implementations run. Review fullOI6 result when finished.','cursor':workers,'registered':research}
current['progress_reviews'].append({'at':now,'acceptance_advanced':'OI5 exact logical parity to accepted pilot2 passes for all8logicaltables anddate/statisticalresults,43checks. Actualsourceproduction12.04CPU vs65.80previousmeasurement, fullprojection2992CPU3.71GB passes; all185mrowOI6 running. Crossmarket37checks pass but900CPU pilotfails;120CPUprofile diagnosescost, one repair. Profile lookahead/calendar/memory defects found beforeexecution and one correction active. Quote13families20029files86.536GB metadata frozen and actualadmissionstarted. AllD1 remains incomplete.'})
d.update(updated_at=now,active_cursor_workers=workers,active_research_processes=research,research_execution='FullOI6 andquoteadmission1 active; profile science correction andcross-market measured performance repair in isolatedCursor checkouts.',resume_only_when_requested=False)
state_path.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
p=Path('/workspace/coordination/trading-research-cursor/state.json');c=json.loads(p.read_text());c.update(updated_at=now,current_deliverable=current,active_cursor_workers=workers,active_research_processes=research)
for k in d:
 if k.endswith('_budget'):c[k]=d[k]
p.write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
p=Path('/workspace/planning/trading-research/STATUS.md');t=p.read_text();end=t.index('## Completed evidence and pending work')
p.write_text('## Current Deliverable 1 progress — '+now+'\n\nAll185,361,441 admitted OI/contract rows are being processed after43checks and complete logical parity with the earlier arithmetic pilot. Measured source production is12.04CPU seconds for1,150,347rows; full projection2992CPU seconds and3.71GB passes the existing caps. Full causal-window statistics49 remains accepted:13partitions,3589source windows,4,092,200features and12,276,600labels.\n\nCross-market pilot4 passed37checks but exhausted900CPU seconds; it is not accepted. A120CPU diagnostic identified scalar pivots, repeated backward joins, output conversion and per-row grouping; one performance repair is active. The profile draft required correction of premature final-session references, missing calendar anchors, and annual memory retention before any scientific execution. Quote-quality admission is active across13quote families andsupport inputs:20,029files,86.536GB; actual row counts remain pending admission.\n\nDeliverable1 remains in progress. Remaining profile/cohort/structure/memory, options/IV/exposure, cross-market and distinct supported mechanisms must be completed before Context. Exact evidence and consumed budgets are in [CURRENT.json](state/CURRENT.json). Historical figures below do not override current state.\n\n'+t[end:])
print(json.dumps({'updated':now,'auction_attempts':d['auction_budget']['attempts_used'],'oi_attempts':d['options_oi_budget']['attempts_used'],'cross_attempts':d['cross_market_budget']['attempts_used']}))
