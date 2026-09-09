"""Registered Jumbo Context phase orchestration and readable decisions."""
from dataclasses import asdict
import gc
import json
from pathlib import Path
import time

from trading_research.errors import DependencyUnavailable, IntegrityError
from trading_research.operations.artifacts import artifact_ref, canonical_json, digest, publish_new
from trading_research.research.jumbo_fitting import (fit_domain, confirm_domain, common_targets,
                                                   put_json_compressed, read_json_compressed)
from trading_research.research.jumbo_matrix import prepare_paths
from trading_research.research.jumbo_targets import target_catalog


VERSION='jumbo-independent-research-pipeline-v1'


def _validate_extraction(value):
    if (value.get('success') is not True or value.get('mode')!='develop'
        or value.get('phase')!='extract' or len(value.get('shards',()))!=10
        or {(s['root'],s['year']) for s in value['shards']}!={(r,y) for r in ('NQ','ES') for y in range(2020,2025)}):
        raise IntegrityError('the complete intended development extraction is required')
    if any('anchor_supplement' not in s for s in value['shards']):
        raise IntegrityError('every immutable source shard needs its exact anchor supplement')


def _matrix(store, shards, plan, phase):
    supplements={(s['root'],s['year']):s['anchor_supplement'] for s in shards}
    return prepare_paths(store,shards,plan=plan,phase=phase,anchor_supplements=supplements)


def _domains(matrix, store, shards, analysis_plan, model_plan, *, measurement_sink=None):
    """Yield real source targets with independent feature and target cuts."""
    yield 'range_paths',matrix,target_catalog(matrix)
    from trading_research.research.jumbo_clock_comparison import prepare_common_clock_comparison
    common=prepare_common_clock_comparison(matrix,plan=analysis_plan)
    yield 'matched_clocks',common,common_targets(common)
    del common
    gc.collect()
    from trading_research.research.jumbo_special_models import prepare_special_model_views
    from trading_research.research.jumbo_special_targets import SPECIAL_CLOCK_IDS, prepare_special_targets
    special_plan={**analysis_plan, **model_plan,
                  'expected_special_clock_ids': analysis_plan.get('expected_special_clock_ids', SPECIAL_CLOCK_IDS)}
    compact=prepare_special_targets(store, shards, plan=special_plan, path_matrix=matrix)
    views=prepare_special_model_views(matrix,compact,plan=special_plan)
    if measurement_sink is not None:
        measurement_sink({'source_manifest':compact.manifest,
                          'dispositions':views.measurement_dispositions,
                          'statistics_evidence':[{'root':s['root'],'year':s['year'],'statistics':s['statistics']} for s in shards],
                          'scope':'Deterministic or already known quantities remain measurements and causal features; they are not presented as future forecast improvements'})
    for name,(view,targets) in sorted(views.items()):
        # Formation/open measurements remain in the view manifest for audit,
        # but only declared future heads enter fitting.  A measurement-only
        # domain is still yielded so its source-year disposition is retained.
        model_targets = {target_name: target for target_name, target in targets.items()
                         if target.metadata.get('model_head', True)}
        view.manifest['model_target_ids'] = sorted(model_targets)
        view.manifest['measurement_dispositions'] = views.measurement_dispositions.get(name, {})
        if not model_targets and not view.manifest['measurement_dispositions']:
            raise IntegrityError('a declared source mechanism cannot disappear from independent target evaluation')
        yield 'source_specials/'+name,view,model_targets
    del views,compact
    gc.collect()


def _summary_table(domains, *, phase, minimum_gain):
    def number(value):
        return 'unavailable' if value is None else f'{value:.5f}'
    lines=[f'# Jumbo independent Context results: {phase}','',
      'Each target below has its own prediction cut, eligible/missing population, grouped comparator, fixed capacity comparisons, calibration and proper-score result. '
      'Fits use2020–2022, fixed-variant model selection uses2023, calibration uses2024H1 and the independent development assessment uses2024H2. '
      'The2025-onward confirmation restores the same records. Every stored prediction population is selected before future-label eligibility; scored rows are flagged separately.', '',
      'The empirical source/horizon comparator shrinks using independent date mass. Controls, own geometry, explicit multiple-range relationships and a fixed nonlinear basis '
      'separate information from capacity; the declared boosted challenger receives the same available information. '
      'Numerical failures emit the common comparator with an explicit failed status and cannot establish that a learner was successfully tested.', '',
      '| Domain / target | Variant | Intended / scored rows | Independent dates | Proper loss | Paired gain [95% interval] | Evidence decision |',
      '|---|---|---:|---:|---:|---|---|']
    summaries=[]
    for domain in domains:
        for result in domain['targets']:
            summary=result.get('summary')
            if summary is None:
                lines.append(f"| {domain['domain']} / {result['target']} | unavailable | unavailable | unavailable | unavailable | unavailable | {result['status']} |")
                continue
            summaries.append(summary)
            for name,value in summary['comparisons'].items():
                point=value.get('primary_loss') or {}
                gain=value.get('paired') or {}
                support=gain.get('support') or {}
                status=value['status']
                if status!='fitted':
                    decision='numerical fallback; no successful capacity claim'
                elif (gain.get('estimate') is not None and gain.get('lower') is not None
                      and gain['estimate']>=minimum_gain and gain['lower']>0 and not support.get('sparse',True)):
                    decision='paired score support; calibration and subgroup limits remain separate'
                else:
                    decision='inconclusive or below declared useful-effect threshold'
                interval=f"{number(gain.get('estimate'))} [{number(gain.get('lower'))}, {number(gain.get('upper'))}]"
                lines.append(f"| {domain['domain']} / {result['target']} | {name} | {summary['intended_rows']} / {summary['eligible_rows']} | {point.get('valid_dates','unavailable')} | {number(point.get('estimate'))} | {interval} | {decision} |")
    lines += ['',f'The prespecified useful score gain is {minimum_gain:g} in the declared target score units, with a positive95%paired date-block lower bound and sufficient support. '
      'This is a research support rule, not a profitability threshold. Quantile scores assess the final emitted monotone quantiles; coverage bounds retain atoms and ties. '
      'Compatible-event likelihoods retain observation ambiguity and the stated coarsening assumptions. No-event and unavailable cases are never interchangeable.', '',
      'The compressed complete evaluations contain the individual root/clock/horizon results, failure and intended-date denominators, uncertainty and calibration. '
      'Prediction artifacts retain exact source row positions, cuts, known-at labels, fitted/calibrated identity and original units. '
      'The common-clock target keeps one receiver cut/end/reference across all declared clocks; its comparisons, rather than different-duration breach frequencies, assess timing information.', '',
      'Full candidate-generator, scorer, contextual and lifecycle Location quality remains separately assessed. A target distribution is not an ordered-path forecast or a reversal-node guarantee. '
      'Original proprietary formulas, unresolved source clocks and exact trade-order requirements remain explicitly outside the corresponding observed-OHLC claims.']
    return '\n'.join(lines)+'\n'


def run_fit(packet, protocol, root, store):
    from trading_research.research.jumbo_study import _predecessor
    source=_predecessor(packet,root,store)
    _validate_extraction(source)
    selected_shards=source.get('model_shards',source['shards'])
    _validate_extraction({**source,'shards':selected_shards})
    analysis=store.read_json(artifact_ref(packet['analysis_plan']))
    model_plan=store.read_json(artifact_ref(packet['model_plan']))
    maximum=packet['limits']['maximum_output_bytes']
    output_bytes=0
    destination=Path(packet['worker_report']).parent
    start=time.process_time()
    matrix=_matrix(store,selected_shards,analysis,'development')
    domains=[]
    measurements=[]
    for name,view,targets in _domains(matrix,store,selected_shards,analysis,model_plan,measurement_sink=measurements.append):
        def checkpoint(value):
            # This retains useful target evidence if a later bounded consumer
            # fails; it does not convert a partial run into phase completion.
            payload=canonical_json(value)
            if len(payload)>maximum-output_bytes:
                raise DependencyUnavailable('independent target checkpoint exceeds output allowance')
            path=destination/('target-'+digest({'domain':name,'target':value['target']})+'.json')
            publish_new(path,payload)
            return len(payload)
        if targets:
            fitted=fit_domain(view,targets,store,domain=name,plan=model_plan,maximum_output_bytes=maximum-output_bytes,checkpoint=checkpoint)
        else:
            # A formation-measurement domain has no future model head.  Keep
            # its complete disposition in the frozen domain manifest so the
            # source population remains reviewable and confirmation can
            # restore the empty fit contract exactly.
            fitted={'version': 'jumbo-independent-fits-v1', 'domain': name,
                    'matrix_manifest': view.manifest, 'targets': [],
                    'model_plan': model_plan, 'derived_output_bytes': 0,
                    'cpu_seconds': 0.0, 'heldout_rows_used': 0,
                    'measurement_only': True}
        output_bytes+=fitted['derived_output_bytes']
        ref=put_json_compressed(store,fitted,kind='jumbo_frozen_context_domain_gzip_v1',remaining_bytes=maximum-output_bytes)
        output_bytes+=ref['size_bytes']
        domains.append({'domain':name,'frozen_domain':ref,'targets':fitted['targets']})
        del fitted
        gc.collect()
    del matrix
    gc.collect()
    narrative_text=_summary_table(domains,phase='independent development assessment',minimum_gain=model_plan['minimum_practical_score_gain'])
    source_resolution=source.get('source_supersession_summary') or {}
    narrative_text+='\nSource population: '+('Verified source-corrected NQ2024; original cohort and complete correction sensitivity are retained in the extraction report. '
                    if source_resolution.get('actual_accepted') else 'Original admitted population, including explicitly retained source-definition exclusions. ')
    narrative_text+='Known quantities are retained in the measurement dispositions and source statistics; they are not scored as future forecast heads.\n'
    narrative=narrative_text.encode()
    if 2*len(narrative)>maximum-output_bytes:
        raise DependencyUnavailable('Context report exceeds aggregate output allowance')
    narrative_ref=store.put_bytes(narrative,kind='jumbo_independent_context_report_markdown_v1')
    publish_new(destination/'context-report.md',narrative)
    output_bytes+=2*len(narrative)
    frozen={'version':VERSION,'source_extraction':packet['predecessor'],'admission_predecessor':source['admission_predecessor'],
            'admission_manifest':source.get('admission_manifest'),'analysis_plan':packet['analysis_plan'],'model_plan':packet['model_plan'],
            'domains':domains,'shards':selected_shards,'selected_without_heldout':True,
            'measurement_dispositions':measurements,
            'source_supersession':source.get('source_supersession'),
            'source_population_rule':'Use an actually verified source correction for NQ2024; retain original population report; same corrected causal warmup in heldout',
            'actual_model_artifact_created_at_ns':time.time_ns(),
            'historical_training_calibration_closure_ns':1719792000000000000,
            'retrospective_reconstruction':True}
    frozen_ref=put_json_compressed(store,frozen,kind='jumbo_frozen_confirmation_inputs_gzip_v1',remaining_bytes=maximum-output_bytes)
    output_bytes+=frozen_ref['size_bytes']
    return {'success':True,'scope':'Independent target-specific development fitting, calibration and assessment; exact confirmation inputs frozen',
            'version':VERSION,'frozen_confirmation_inputs':frozen_ref,'domains':domains,'narrative':asdict(narrative_ref),
            'measurement_dispositions':measurements,
            'derived_output_bytes':output_bytes,'cpu_seconds_internal':time.process_time()-start,
            'heldout_target_rows_used':0,'context_quality_rule':'Every target retains successful/failed/inconclusive status; phase completion is not universal predictive acceptance',
            'family_statistics_complete':False,'context_models_complete':False,'location_quality_complete':False,
            'remaining':['heldout confirmation','source/measurement dependencies','full Location candidate/scorer/generator/lifecycle quality']}


def run_confirmation(packet, protocol, root, store):
    from trading_research.research.jumbo_study import _predecessor, _run_extraction
    fitted=_predecessor(packet,root,store)
    if fitted.get('mode')!='develop' or fitted.get('phase')!='fit' or fitted.get('success') is not True:
        raise IntegrityError('confirmation requires the exact successful independent fit predecessor')
    frozen=read_json_compressed(store,fitted['frozen_confirmation_inputs'])
    if frozen['version']!=VERSION or frozen['analysis_plan']!=packet['analysis_plan'] or frozen['model_plan']!=packet['model_plan']:
        raise IntegrityError('frozen confirmation definitions changed')
    identity=frozen['admission_predecessor']
    raw=(root/identity['path']).read_bytes()
    import hashlib
    if hashlib.sha256(raw).hexdigest()!=identity['sha256']:
        raise IntegrityError('original successful admission identity changed')
    admission_execution=json.loads(raw)
    admission=store.read_json(artifact_ref(admission_execution['worker_report']))
    extracted=_run_extraction(packet,protocol,root,store,admitted=admission,heldout=True,
                             frozen_source_supplement=frozen.get('source_supersession'))
    maximum=packet['limits']['maximum_output_bytes']
    output_bytes=extracted['derived_output_bytes']
    analysis=store.read_json(artifact_ref(packet['analysis_plan']))
    model_plan=store.read_json(artifact_ref(packet['model_plan']))
    matrix=_matrix(store,extracted['shards'],analysis,'heldout')
    by_name={r['domain']:r for r in frozen['domains']}
    domains=[]
    measurements=[]
    for name,view,targets in _domains(matrix,store,extracted['shards'],analysis,model_plan,measurement_sink=measurements.append):
        if name not in by_name:
            raise IntegrityError('an independent confirmation domain lacks frozen model records')
        original=read_json_compressed(store,by_name[name]['frozen_domain'])
        result=confirm_domain(view,targets,original,store,plan=model_plan,maximum_output_bytes=maximum-output_bytes)
        output_bytes+=result['derived_output_bytes']
        ref=put_json_compressed(store,result,kind='jumbo_independent_heldout_context_domain_gzip_v1',remaining_bytes=maximum-output_bytes)
        output_bytes+=ref['size_bytes']
        domains.append({'domain':name,'heldout_domain':ref,'targets':result['targets']})
        del result,original
        gc.collect()
    if set(by_name)!={r['domain'] for r in domains}:
        raise IntegrityError('frozen independent target domains lost in confirmation')
    del matrix
    gc.collect()
    narrative=_summary_table(domains,phase='heldout confirmation',minimum_gain=model_plan['minimum_practical_score_gain']).encode()
    if 2*len(narrative)>maximum-output_bytes:
        raise DependencyUnavailable('heldout Context narrative exceeds aggregate output allowance')
    ref=store.put_bytes(narrative,kind='jumbo_heldout_context_report_markdown_v1')
    publish_new(Path(packet['worker_report']).parent/'context-report.md',narrative)
    output_bytes+=2*len(narrative)
    return {'success':True,'version':VERSION,'scope':'Frozen heldout range/path/source-mechanism Context assessment on actual admitted2025onward observations',
            'extraction':extracted,'domains':domains,'narrative':asdict(ref),'frozen_confirmation_inputs':fitted['frozen_confirmation_inputs'],
            'measurement_dispositions':measurements,
            'derived_output_bytes':output_bytes,'new_model_fits':0,'new_calibrations':0,'heldout_guided_selections':0,
            'family_statistics_complete':False,'context_models_complete':False,'location_quality_complete':False,
            'completion_scope':'Declared targets and cohorts evaluated; source dependencies and full Location questions retain their individual dispositions'}
