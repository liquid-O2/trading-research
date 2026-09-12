#!/usr/bin/env python3
"""Record the parent's source/chart comparison and immutable evidence links.

The observations below are the manual source review. File hashes and native
arithmetic are refreshed mechanically; they do not perform image interpretation
or turn an illustration into a discovered historical candidate.
"""
from __future__ import annotations

import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path

from trading_research.research.method_pack.source_config import load_catalog

ROOT=Path(__file__).resolve().parents[2]
VALIDATION=ROOT/'implementation/validation/phase1-completion'
OUT=ROOT/'implementation/reports/phase1-live/methods/reconstructions/v2'

# Read with the original pages and current images. The short-side orderblock
# is an implementation mirror: both source pages show the long example.
REVIEWS={
 'JJ-range-control-2026-02-24':('native_control_verified','JJ-range-control-2026-02-24.png',
   'The 06:00–09:00 ET native range, its own width, quadrants and both projection branches reconcile. This dated control is not an observed author trade.'),
 'JJ-profiles-2026-06-12':('structure_preserved_settings_unknown','JJ-profiles-2026-06-12.png',
   'The original shows separate profile panels. Five distinct native prior-RTH, prior-ETH, overnight, developing-RTH and selected-range windows are plotted; unreadable author windows and VA expansion cannot be matched. The 40% control setting is attributed to Sires, not recovered for Jumbo.'),
 'JJ-orderblock-long':('source_sequence_retained','source-images/TBR-27-page.png',
   'TBR pages 27–28 show the long three-minute example. Complete-candle pattern tests preserve the swept low, full second-candle zone and later confirmation; the exact dated native execution is unavailable.'),
 'JJ-orderblock-short-mirror':('synthetic_mirror_only','source-images/TBR-27-page.png',
   'The short branch is tested with three identified mirrored candles. Neither cited page is a short observed source trade, so this record remains a synthetic fixture.'),
 'GB-FAIL-2025-11-20':('sequence_correction_preserved','GB-FAIL-2025-11-20.png',
   'The MNQ two-minute display shows 25301.75 and entry at the later high sweep, before MSS/FVG annotations. The NQ 10:38–10:40 comparison and its close remain measurements, excluded from source sweep/fill/confirmation bindings. No NQ fill or return is inferred.'),
 'GB-VWAP-2026-02-24':('frozen_comparison_reproduced','GB-VWAP-2026-02-24.png',
   'The opening reversal, later pullback and continuation are retained. The single previous-18:00/HLC3 comparison reproduces the prior curve; source reset, price basis and unreadable timeframe remain unverified. No new parameter grid was searched.'),
 'GB-SCALP-bearish':('source_description_retained','source-images/GB-40-page.png',
   'The September 2 publication reports bearish bias, short scalps and 20–30 points with no size increase. Publication time is not entry time; quantity, fills, timeframe and a general entry/exit algorithm are absent. The source profit statement is not a reconstructed return.'),
 'GB-SCALP-bullish':('source_description_retained','source-images/GB-40-page.png',
   'The September 10 publication describes longs with NYAM direction, discount pullbacks and smaller size. This is the separate bullish discretionary loop. No numerical size, dated fill or automatic trigger is invented from that description.'),
 'SIRES-overnight-profile':('source_window_bound_native_control','native-SIRES-overnight-2026-06-12.png',
   'The source specifies previous 18:00–09:30 ET. O073 uses the same actual O011 window and an immutable native overnight profile, retaining an older POC identity. June 12 is a declared control date; the source illustration is undated. LVN selection and VA expansion remain unknown.'),
 'SIRES-same-candle-POC':('schematic_and_native_control_separated','source-images/FP9-5-page.png',
   'FP9 page 5 is a same-candle POC schematic, not a dated native fill. Three dated native controls preserve distinct developing and close snapshots, full footprint rows and known/unknown delta. Their POC change is not claimed as the author’s observed flip.'),
 'STOP-confirmed':('source_stages_retained','source-images/STOP-11-page.png',
   'The displayed example is ES/EPZ25 on one-minute candles. The separate NQ 40-range setting is not transferred here. Defense, replenishment, exhaustion and liftoff remain separate; exact dated executions and native passive-order evidence are absent.'),
 'STOP-early':('early_attempt_retained','source-images/STOP-13-page.png',
   'The deliberate early attempt remains a separate case with its declared small-risk interpretation. It does not receive the later complete-confirmation branch result or an invented fill.'),
 'SIRES-losses-2026-07-23':('losses_and_source_conflict_retained','SIRES-losses-2026-07-23.png',
   'The nine visible outcomes are loss, loss, win, loss, win, win, loss, loss, win. The caption about the first four conflicts with the positive third plotted attempt and is retained as a conflict. Native one-minute NQU6 context is not an alignment of undocumented source fill clocks.'),
 'SAINT-break-retest':('source_route_retained','source-images/TRAP-7-page.png',
   'The Saint continuation/trapped-buyer route keeps the marked balance, prior distinct failures, break and defended same-boundary retest. Exact date/timeframe and complete native flow observations are unavailable; no Sires confirmation is substituted.'),
 'SAINT-failed-auction':('source_route_retained','source-images/AMTL-10-page.png',
   'Page 10 is explanatory source text; pages 8–9 support the failed-auction schematic. It is not labeled a dated embedded chart. Exploration, failure, original-balance return/reacceptance and local control are tested as a distinct Saint route.'),
 'MEMBER-resistance':('independent_reasons_retained','source-images/K10-7-page.png',
   'The right execution display is ES two-minute; the left context is NQ five-minute. The marked prior reaction and independent minor HVN remain two identified reasons, rather than two labels on one price. Exact native date and source fill are absent.'),
 'MEMBER-return':('source_return_plan_retained','source-images/K10-8-page.png',
   'The planned return to structure, fresh absorption/hold and adverse-side stop stay scoped to this long-return case. Missing source clocks or prior-defense records are not copied from the resistance case.'),
 'KEANI-open-above':('schematic_sequence_retained','source-images/AVG-22-page.png',
   'Page 22 is a schematic. Prior value, completed opening A, developing value before the break, buy imbalance and defended retest remain distinct dated dependencies in the implementation. No source date, fill or author VA engine is invented.'),
 'REFILL-selected-order':('selected_order_record_retained','source-images/REF-7-page.png',
   'Source zone/threshold, causal prior-touch memory, selected order, cancellation, fills and costs remain separate records. Queue position and missing native order history remain unavailable. No return path or optimization was manufactured.'),
 'JETBUNDLE-state-process':('process_observation_retained','source-images/MATH-3-page.png',
   'The five-state process is kept as participation/response/state evidence. Actual adjacent state records and known conditioning are required for O166; supplied transition counts alone remain arithmetic, not evidence of a transition or a trained classifier.'),
 'STOIC-process':('research_process_retained','source-images/DATA-3-page.png',
   'Frozen process, uniform journal, all outcome categories, original-R provenance and causal review remain research/process observations. Missing private records and deferred macro collection do not become an entry strategy.'),
 'STOIC-risk':('risk_illustration_retained','source-images/DATA-7-page.png',
   'The fixed-baseline risk ladder remains conditional on a distinct prior closed sample and matched supplied validation. The source illustration is not an actual validated portfolio or evidence of profitability.'),
}


def file_ref(path):
    path=Path(path)
    if not path.is_file():raise FileNotFoundError(path)
    return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def frozen_vwap_comparison():
    original=OUT.parent/'vwap-source-points.csv';native=OUT/'GB-VWAP-2026-02-24.json'
    curve={row['as_of']:Decimal(row['vwap']) for row in json.loads(native.read_text())['curve']}
    rows=[]
    for source in csv.DictReader(original.open()):
        current=curve[int(source['known_at_ns'])];previous=Decimal(source['reconstructed_hlc3']);sample=Decimal(source['source_price'])
        rows.append(dict(bar_open_et=source['bar_open_et'],known_at=int(source['known_at_ns']),
            source_digitized_price=str(sample),frozen_previous_value=str(previous),native_value=str(current),
            error_points=str(current-sample),change_from_previous=str(current-previous)))
    errors=[Decimal(row['error_points']) for row in rows]
    doc=dict(schema='phase1-frozen-vwap-source-comparison-v2',source_points=file_ref(original),native_curve=file_ref(native),
        point_count=len(rows),mean_absolute_error_points=str(sum(map(abs,errors))/len(errors)),
        maximum_absolute_error_points=str(max(map(abs,errors))),
        maximum_change_from_previous=str(max(abs(Decimal(row['change_from_previous'])) for row in rows)),
        settings=dict(bars_minutes=1,basis='HLC3',reset='previous 18:00 ET',variant='comparison'),
        observations=rows,new_parameter_search=False,author_settings_verified=False,
        limitation='The retained points were digitized from pixels. Residuals describe this frozen comparison only; they neither identify the author engine nor estimate performance.')
    path=OUT/'GB-VWAP-frozen-comparison.json';path.write_text(json.dumps(doc,indent=2)+'\n')
    return doc


def main():
    catalog=load_catalog(verify_sources=True)
    assert {c['case_id'] for c in catalog['cases']}==set(REVIEWS)
    rows=[]
    for case in catalog['cases']:
        cid=case['case_id'];agreement,chart,review=REVIEWS[cid]
        entry=dict(case_id=cid,method_id=case['method_id'],evidence_mode=case['evidence_mode'],
            historical_candidate=False,source_case=case,
            visual_review=dict(status='reviewed',reviewer='parent',chart=file_ref(OUT/chart),
                observations=review,layout='Labels, date/window distinctions, legends and captions inspected; original source interpretation retained separately.'),
            source_ambiguity=dict(status='retained',missing_fields=case['missing_fields']),
            source_case_agreement=dict(status=agreement,notes=review,faithful_disagreements=None),
            historical_discovery=dict(status='unavailable',n=None,reason='Retrospective source illustration/control, not a contemporaneously selected historical cohort.'),
            software_completeness=dict(status='see_final_acceptance',evidence_path=str(VALIDATION/'obligation-matrix.json')))
        path=VALIDATION/'source-cases'/(cid+'.result.json')
        if path.exists():
            measured=json.loads(path.read_text());r=measured['measurement_result']
            entry['assembled_measurement']=dict(evidence=file_ref(path),verdict=r['verdict'],software_complete=r['software_complete'],
                native_object_count=len(measured['resolved_objects']),missing_operands=measured['assembly_holes'],
                detected_causal_violations=r['detected_causal_violations'],rejected_proxy_attempts=r['rejected_proxy_attempts'])
            entry['data_coverage']=dict(status='per_native_window',windows=[dict(dataset_id=w.get('dataset_id'),
                start_ns=w.get('start_ns'),end_ns=w.get('end_ns'),coverage_ok=w.get('coverage_ok'),
                missing_intervals=w.get('missing_intervals'),mismatch_count=len(w.get('mismatches',[]))) for w in measured['native_window_audits']])
        elif (OUT/(cid+'.json')).exists():
            measurement=json.loads((OUT/(cid+'.json')).read_text());entry['native_measurement']=file_ref(OUT/(cid+'.json'))
            entry['data_coverage']=dict(status='per_native_window',coverage_ok=measurement.get('native',{}).get('coverage_ok'),
                profile_coverage=[dict(profile_id=p['profile_id'],coverage_ok=p['coverage_ok'],payload=p['payload']) for p in measurement.get('profiles',[])])
        else:
            entry['data_coverage']=dict(status='source_record_only',reason='No exact dated native source execution can be identified from this source record.')
        if cid in {'SIRES-overnight-profile','SIRES-same-candle-POC'}:
            entry['additional_native_controls']=[file_ref(VALIDATION/('native-geometry.json' if cid=='SIRES-overnight-profile' else 'native-flow.json'))]
        rows.append(entry)
    vwap=frozen_vwap_comparison()
    charts=[file_ref(p) for p in sorted(OUT.glob('*.png'))]
    doc=dict(schema='phase1-source-case-review-v2',review_date='2026-09-12',case_count=len(rows),
        source_catalog=file_ref(ROOT/'implementation/src/trading_research/research/method_pack/source_cases_v2.json'),
        cases=rows,charts=charts,frozen_vwap_comparison=file_ref(OUT/'GB-VWAP-frozen-comparison.json'),
        separation=['software_completeness','source_ambiguity','data_coverage','source_case_agreement','historical_discovery'],
        stage8_research='deferred: macro collection, parameters, timeframes, price bases, new classifiers and Phase 2 performance')
    (VALIDATION/'source-case-review.json').write_text(json.dumps(doc,indent=2)+'\n')
    lines=['# Phase 1 source-case and chart verification','',
      f'The repaired code has been compared with {len(rows)} retained source cases and explicit native controls across all 12 methods. No figure is used as an unbiased historical performance sample. Exact source dates, fills and undisclosed settings stay unknown where the source does not establish them.','',
      '| Case | Verification | Reviewed image |','| --- | --- | --- |']
    for row in rows:
        image_path=Path(row['visual_review']['chart']['path']).relative_to(OUT)
        lines.append(f'| {row["case_id"]} | {row["visual_review"]["observations"]} | [Image](reconstructions/v2/{image_path}) |')
    lines+=['','The frozen Green Bird VWAP comparison was recalculated at all 13 retained digitized points. Its largest change from the earlier numerical curve is '+vwap['maximum_change_from_previous']+' points; mean absolute pixel-reference error is '+str(round(Decimal(vwap['mean_absolute_error_points']),4))+' points. This reproduces the comparison without identifying the source settings.','',
      'The five dated profile snapshots and the disjoint composite retain full native rows and unknown-side volume. Independent minute checks preserve four profile-window coverage uncertainties; the selected 06:00–09:00 control reconciles. [Clock and coverage evidence](../../../validation/phase1-completion/native-clock-coverage.json) records the retained timestamps and unresolved cross-source bucket differences.','',
      'The native flow controls retain full footprints and same-candle snapshots; the TPO control retains all 390 underlying minute bars across 13 periods. [Machine-readable review](../../../validation/phase1-completion/source-case-review.json) contains source facts/inferences, missing records, native-control results and SHA-256 links.','',
      'Software acceptance and acquired-scope method reports are reported separately in [COMPLETION_REPORT.md](COMPLETION_REPORT.md). Stage 8 remains deferred.','']
    (OUT.parents[1]/'CHART_VERIFICATION.md').write_text('\n'.join(lines))
    print(json.dumps(dict(case_count=len(rows),chart_count=len(charts),path=str(VALIDATION/'source-case-review.json'))))


if __name__=='__main__':main()
