"""Retain the completed original-source pass and preregister the F04 batch."""
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from trading_research.operations.artifacts import code_snapshot, file_digest
from trading_research.operations.trials import TrialRegistry

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT.parent/'planning/trading-model'
GROUPS=[
 ('F04-01','Availability joins: future OI, revised CPI, stale and conflicting observations','CEX-24 PIN066-02'),
 ('F04-02','Derived completion, confirmation and modeled duration are charged once','DTM-A01 OSF-02 OSF-03 PIN081-03'),
 ('F04-03','Pivot origin differs from right-bar confirmation and actionable availability','OSF-02 OSF-03 PIN009-02 PIN032-01 PIN071-06'),
 ('F04-04','Availability merge has insertion-order and prefix invariance','INV-01 INV-02 INV-03 INV-04 INV-05 INV-06 INV-07 INV-08 INV-09 INV-10 CEX-24'),
 ('F04-05','Independent equal-time streams retain ambiguity and within-source order','PIN027-02 PIN048-01 PIN073-02 PIN081-03'),
 ('F04-06','Domain watermarks isolate optional feed stalls and asynchronous chains','CEX-24 INV-01 INV-07 PIN066-02'),
 ('F04-07','Durable spill, repeatable peek, ack and restart preserve exact envelope identity','INV-01 INV-02 INV-03 INV-04 INV-05 INV-06 INV-07 INV-08 INV-09 INV-10'),
 ('F04-08','Record/byte/tie bounds fail closed with retained backpressure evidence','INV-12 DTM-A01'),
 ('F04-09','Changed OI fields invalidate exposure without recomputing trade CVD','PIN066-02 CEX-24 DTM-A01'),
 ('F04-10','Unchanged numeric value with new source lineage still invalidates forecast','PIN071-02 PIN064-02 PIN045-03'),
 ('F04-11','Missing required input blocks only consumers; optional absence is explicit','CEX-24 INV-01 INV-07'),
 ('F04-12','Registered FIFO, deadline and cost-aware optional ordering retain choices','DTM-A01 CEX-04 CRL-17'),
 ('F04-13','Past measured runtime costs, prefix-safe estimates and percentile telemetry','INV-12 DTM-A01'),
 ('F04-14','Queued/slow/late forecasts preserve original cut and endpoint','DTM-A01 CEX-04 PIN081-03'),
 ('F04-15','Duplicate dispatch, terminal publication and coalescing preserve identity','DTM-A01 CRL-17'),
 ('F04-16','Raw market, timer, account and order integrity remain unconditional','DTM-A01 CRL-17 PIN066-03 PIN077-02'),
 ('F04-17','Current HTF final H/L/C is unavailable at start; offset prior values differ','PIN012-02 PIN014-02 PIN019-02 PIN021-01 PIN022-01 PIN022-03 PIN023-01 PIN023-02 PIN035-01 PIN037-01 PIN047-01 PIN058-01 PIN059-01 PIN068-02 PIN071-01 PIN071-02 PIN071-03'),
 ('F04-18','Display toggles, drawn origins and screen timestamps cannot select observations','IMG-01 DEN-04 ALM-06 TBR-07 PIN023-02 PIN064-02 PIN071-02'),
 ('F04-19','Daily OI changes are delayed reports, not observed intraday traded volume','PIN066-02 CEX-24'),
 ('F04-20','Completed ranges, minute aggregates and anchors have separate formation/freeze cuts','VW10-05 OFM-01 PIN027-02 PIN040-02 PIN043-01 PIN045-03 PIN048-01 PIN056-01 PIN059-01 PIN066-03 PIN073-02 PIN077-02 PIN080-01'),
 ('F04-21','Inventory/screenshot/provider clocks do not certify live strategy receipts','IMG-01 INV-11 INV-12 VX4-07 DEN-04 ALM-06 OFM-01 TBR-07 CEX-24'),
 ('F04-22','Cadence is a candidate; retain every matured label and rejected/untraded opportunity','DTM-A01 CEX-04 CRL-17'),
 ('F04-23','Full versus incremental output parity is separate from empirical/economic admission','DTM-A01 CEX-24 PIN045-03 PIN047-01 PIN080-01')]

def main():
 registry=TrialRegistry(ROOT/'evidence/trials'); store=registry.artifacts
 original=json.loads(Path('/tmp/f04-original-reading.json').read_text())
 routes={r['id']:r for r in json.loads((PLAN/'review/source_design_routing.json').read_text())}
 inventory=json.loads((PLAN/'review/source_inventory.json').read_text())
 prior=json.loads((ROOT/'reports/f03-source-cases.json').read_text())
 sources=[]
 for row in original['sources']:
  raw=Path(row['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256']
  numbers=set(row['lines'])
  if 'PIN019-02' in row['clauses']:numbers.update(range(55,86))
  if 'PIN037-01' in row['clauses']:numbers.update(range(1,26))
  lines=raw.decode('utf-8-sig').splitlines()
  excerpt=store.put_json({'original_path':row['path'],'original_sha256':row['sha256'],
    'lines':[{'line':n,'text':lines[n-1]} for n in sorted(numbers)]},kind='static_original_source_excerpt')
  sources.append({'path':row['path'],'sha256':row['sha256'],'lines_read':sorted(numbers),'source_ids':row['clauses'],
   'excerpt':asdict(excerpt),'reused_lines':row['previously_inspected_lines'],'prior_review':original['prior_review'],
   'read':True,'source_code_executed':False})
 pages=[]
 page_manifest=json.loads(Path('/tmp/f04-original-pages/manifest.json').read_text())
 for row in page_manifest['pages']:
  assert file_digest(Path(row['original_path']))==row['original_sha256']
  assert file_digest(Path(row['text_path']))==row['text_sha256']
  pages.append({k:row[k] for k in ('prefix','original_path','original_sha256','page')}|
   {'text':asdict(store.put_bytes(Path(row['text_path']).read_bytes(),kind='original_pdf_page_text')),
    'render':asdict(store.put_bytes(Path(row['image_path']).read_bytes(),kind='inspected_original_pdf_page')),
    'text_read':True,'visually_inspected':True})
 reused_pages=[r for r in prior['pdf_pages'] if (r['prefix']=='VW10' and r['page']==7) or r['prefix']=='TBR']
 for row in reused_pages:assert file_digest(Path(row['original_path']))==row['original_sha256']
 text_sources=[]
 for name,ranges in [('conversations/Develop Trading Model.md',[(35,89),(315,381)]),
  ('conversations/conversation_export (1).md',[(66,110),(1023,1087),(1201,1245),(1281,1296)]),
  ('conversations/conversation_raw_log.md',[(749,783)])]:
  row=next(r for r in inventory if r['relative_path']==name);assert file_digest(Path(row['path']))==row['sha256']
  lines=Path(row['path']).read_text().splitlines()
  excerpt=store.put_json({'original_path':row['path'],'original_sha256':row['sha256'],
   'lines':[{'line':n,'text':lines[n-1]} for a,b in ranges for n in range(a,b+1)]},kind='original_conversation_excerpt')
  text_sources.append({'path':row['path'],'sha256':row['sha256'],'ranges':ranges,'excerpt':asdict(excerpt),'read':True})
 f01=json.loads((ROOT/'reports/f01-source-case-review.json').read_text())
 reused_inventory=[]
 for row in inventory:
  if row['relative_path'].startswith('inventory/'):
   assert file_digest(Path(row['path']))==row['sha256']
   reused_inventory.append({'path':row['path'],'sha256':row['sha256'],'prior_review':f01['review'],
    'read_extent':f01['read_extent'],'admission':'inventory metadata only; unequal field/cohort evidence; missing hardware transcript unresolved'})
 assert file_digest(Path(prior['image']['path']))==prior['image']['sha256']
 cases=[{'id':id,'expected':expected,'source_ids':ids.split(),'whole_case_verified':False} for id,expected,ids in GROUPS]
 assert set(original['source_ids'])=={s for c in cases for s in c['source_ids']}
 findings=[routes[id]|{'cases':[c['id'] for c in cases if id in c['source_ids']],
  'assigned_original_passages_reviewed':True,'full_indicator_implementation_claimed':False} for id in original['source_ids']]
 corrections=[
  'DTM cadence values are proposed comparisons, not mandatory live frequencies. CEX vendor one-for-one equivalence and claimed pulls remain unaudited.',
  'CRL selective updates only on traded/gate-positive examples and forced daily gate zeroing are rejected; retain all matured labels and continuity.',
  'Unshifted final HTF H/L/C under lookahead_on is unavailable at interval start; prior [1] completed values have a different causal release contract.',
  'PIN037 offset default 1 means expression offset-1=0 (current HTF); default lookahead_off still has historical/live confirmation differences.',
  'PIN019 getFVGData includes unoffset current close/high/low at L81-85; cannot publish completed gap before confirmation.',
  'PIN022 manual HTF/auto current timeframe mismatch is not inherited; compute and publication clocks must identify the actual source series.',
  'PIN027 IB close is assigned from first outside-session bar; preserve literal parity separately from last inside close. Same-minute high-first ties are ambiguous.',
  'PIN032 pivot draws at offset origin but becomes confirmed after right bars; FindT price equality is a visual placement, not receipt evidence.',
  'PIN048 lower-timeframe arrays only contain confirmed observed prefixes; a parent-bar array is not available at its bar open, and simultaneous extremes remain ambiguous.',
  'PIN045 volatility multiplier is frozen per anchor from what was available; close-to-close standard deviation differs from source RMS estimator and embedded performance is unverified.',
  'PIN071 _ischange compares OHLC value, omitting equal-valued new bars/lineage. Exact bar identity must drive admission; visual deletes do not delete historical state.',
  'PIN066 daily OI delta is neither signed trade volume nor an intraday holdings observation; receipt/report publication controls its use.',
  'Final body/wick classification in OFM becomes available at bar close. Aggressive liquidity can include marketable limits; the cited bubble thresholds are source candidates.',
  'ALM p11 right edge recovers the weekly balance; do not describe it as a current confirmed lower hold. Narrative claims and screenshots provide no complete event tape.',
  'Provider receipt, local wall display, filename and inventory metadata do not establish actual strategy receipt latency or economic observations.'
 ]
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'scope':'F04 and F04.SCHEDULER opening source cases',
  'source_findings':findings,'cases':cases,'static_original_sources':sources,'pdf_pages':pages,'reused_pdf_pages':reused_pages,
  'reused_pdf_review':prior['artifact'],'renderer':page_manifest['renderer'],'conversation_sources':text_sources,
  'reused_inventory_sources':reused_inventory,'reused_image':prior['image'],'source_corrections':corrections,
  'source_code_executed':False,'whole_definition_or_phase_closure':False,'market_tape_reads':0,'economic_runs':0,
  'unresolved':['Actual strategy receipts and broad field/cohort semantics remain unadmitted.',
    'Imported/private source formulas and source-specific indicator replays remain separate.',
    'All-consumer reference/scheduler decision and E0-E5 economic consequences remain open.',
    'INV-12 historical hardware commands/results are absent; current measured runtime will be separate.']}
 ref=store.put_json(report,kind='original_source_case_review')
 (ROOT/'reports/f04-source-cases.json').write_text(json.dumps({'artifact':asdict(ref),**report},indent=2)+'\n')
 prose='# F04 availability and scheduler source cases\n\nAll 58 assigned/lineage findings have original-passage coverage. The retained report records 28 static source files, six newly inspected original PDF pages, six reused PDF pages, three original conversation excerpts, unchanged inventory evidence and the original image. No Pine source was executed. Cases are expectations, not whole-source or whole-phase completion.\n\n'
 prose+='\n'.join(corrections)+'\n\n| Case | Expected behavior | Source clauses |\n|---|---|---|\n'
 prose+=''.join(f"| {c['id']} | {c['expected']} | {', '.join(c['source_ids'])} |\n" for c in cases)
 (ROOT/'validation/F04_SOURCE_CASES.md').write_text(prose)
 protocol=store.put_bytes((ROOT/'validation/F04_REPLAY_PROTOCOL.md').read_bytes(),kind='engineering_protocol')
 golden=store.put_bytes((ROOT/'tests/golden/f04-replay.json').read_bytes(),kind='independent_golden_reference')
 registration={'protocol':asdict(protocol),'golden':asdict(golden),'source_cases':asdict(ref),'baseline':asdict(code_snapshot(ROOT,store)),
  'maximum_cpu_per_attempt':180,'hard_cpu_seconds':190,'address_space_bytes':4*1024**3,'wall_seconds':240,
  'market_tape_reads':0,'model_fits':0,'economic_runs':0}
 registry.register_family('F04-availability-scheduler-reference-v1',scope_ids=('F04','F04.SCHEDULER','B00.1'),
  protocol=registration,max_attempts=3,cpu_budget_seconds=600)
 (ROOT/'reports/f04-replay-registration.json').write_text(json.dumps(registration,indent=2)+'\n')
 print(json.dumps({'registration':registration,'source_findings':len(findings),'static_sources':len(sources),
  'pdf_pages':len(pages),'reused_pdf_pages':len(reused_pages),'cases':len(cases)},indent=2))

if __name__=='__main__':main()
