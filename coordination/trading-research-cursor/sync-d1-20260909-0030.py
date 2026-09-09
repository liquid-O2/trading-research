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
d['auction_budget']['check_extension']={'path':'/workspace/trading-research/validation/AUCTION_FLOW_SOURCE_CHECK_EXTENSION_V40.json'}
current=d['current_deliverable'];e=current['accepted_evidence']
e['options_oi_pilot2']={'execution':'/workspace/trading-research/reports/options-oi-runs/7afd70dbe582775095dc3367834abdd4ba4a71ff2263dff0948587ba3d7b0816/execution.json','tests_passed':39,'source_files':208,'source_rows':1150347,'report_rows':583277,'interval_rows':583277,'lifecycle_rows':630861,'coverage_rows':112,'intended_dates':16,'cpu_seconds':89.579493,'measurement_cpu_seconds':65.796733319,'wall_seconds':98.07726465119049,'peak_rss_bytes':505901056,'output_bytes':43709142,'actual_output_bytes':21842429,'full_population_complete':False,'full_resource_gate_passed':False,'projection':{'scale':161.13524093164932,'cpu_seconds':21711.619780634992,'output_bytes':5312932021.171165},'resource_reassessment':'/workspace/coordination/trading-research-cursor/options-oi2-resource-review.json','finding':'39 checks pass; full measured cost exceeds unchanged 5000CPU/4GiB bounds. Registered unchanged cProfile replay3 diagnoses actual dominant cost before one repair; no full run launched.'}
workers=['crossmarket1correction:20260909T001448Z-9c9529d7','auctionremainingassessment1:20260909T002428Z-42b82dfc','optionsquotesassessment1:20260909T002557Z-acf5c876']
research=['windowstatisticsfull49:9c23254897fa93ff20a30214a7e73ca1adb4baf1c6d3b24bc23a3b464ee2939b','optionsOIprofile3:e9c6e60ccb9e300079d5e94dca92cf7735644bd3fd8b805968e2951efd0fcec9']
current['active_work']={'codex':'Review actual full window statistics49; use OIprofile3 to consolidate measured performance repair, then full gate; integrate corrected cross-market measurements; continue remaining D1 mechanisms.','cursor':workers,'registered':research}
d.update(updated_at=now,active_cursor_workers=workers,active_research_processes=research,research_execution='Full windowstatistics49 and registered unchanged OI diagnostic3 active; sourceperformance36 remains accepted.',resume_only_when_requested=False)
state_path.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
p=Path('/workspace/coordination/trading-research-cursor/state.json');c=json.loads(p.read_text());c.update(updated_at=now,current_deliverable=current,active_cursor_workers=workers,active_research_processes=research)
for k in d:
 if k.endswith('_budget'):c[k]=d[k]
p.write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
p=Path('/workspace/planning/trading-research/STATUS.md');s=p.read_text();end=s.index('## Completed evidence and pending work')
s='''## Current Deliverable 1 progress — 2026-09-09T00:30 UTC

All 3,589 causal source windows have retained formation/label output: 4,092,200 feature rows and 12,276,600 labels, with 37 explicitly unavailable source windows. Recovery46 passed40 checks, reused3,505 units and completed84 in9.27minutes without a raw-source rescan. Full window-statistics49 is running with eight consumers after its20-check pilot.

Options OI pilot2 passed39 checks on208files/1,150,347rows, producing583,277 reports and630,861 lifecycle rows across16dates/sevenchains. Its measured full projection exceeds the frozen5000CPU-second/4GiB limits; an unchanged registered profiling replay3 is diagnosing the expensive steps before a consolidated performance repair. The pilot is accepted for its arithmetic and population only. Cross-market correction remains in progress, alongside focused remaining-auction and quote/valuation source assessments.

Earlier accepted full core statistics, Jumbo descriptive confirmation/timing, physical OHLC volatility, daily VX/VIX curves and scheduled-event measurement remain accepted for their stated branches. Deliverable1 remains in progress across all remaining mechanisms; Context and Location have not started. Exact current evidence, active runs and resource budgets are in [CURRENT.json](state/CURRENT.json); historical figures below are retained references and do not override it.

'''+s[end:]
s=s.replace('The latest user explicitly requested fixing the remaining source timestamp faults. That repair is now verified and integrated. The earlier 20:11 UTC cutoff was exceeded during the continuation; all time and resources remain recorded. No workers remain active.','The latest user explicitly resumed full Deliverable1 measurement/statistics/timing at20:41UTC. The source timestamp repair remains verified and integrated; its exceeded earlier20:11 cutoff and all elapsed/resources remain recorded. Current active work is listed above and in CURRENT.json.')
p.write_text(s)
p=Path('/workspace/trading-research/STATUS.md');s=p.read_text();s=s.replace('Research is paused at completed auction/flow benchmark 16 for the user-requested consolidation. Context and Location evaluations remain unfinished.','Deliverable1 measurement, statistics and timing work is active under the latest user continuation. The source performance repair36 is accepted; current family results and active runs are recorded in the authoritative planning state. Context and Location evaluations remain unfinished.');p.write_text(s)
print(json.dumps({'updated_at':now,'active_registered':research,'oi_attempts':d['options_oi_budget']['attempts_used'],'auction_attempts':d['auction_budget']['attempts_used']}))
