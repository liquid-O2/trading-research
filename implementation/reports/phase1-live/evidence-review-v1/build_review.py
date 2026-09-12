"""Rebuild evidence-review artifacts from the accepted run; never run a replay.

Manual chart observations live in review_notes.json. This script checks their
coverage and provenance; it does not perform or certify visual inspection.
"""
from collections import Counter, defaultdict
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
EMP = OUT.parent / 'empirical'
SOURCE_COMMIT = '43beed9a0146d5a99a90d56945e61e4d799e17ab'
identities = {}


def read(path):
    raw = path.read_bytes()
    identities[str(path.relative_to(ROOT))] = sha256(raw).hexdigest()
    return json.loads(raw)


def content_hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def clock(value):
    return datetime.fromtimestamp(value / 1e9, ZoneInfo('America/New_York')).isoformat() if value is not None else None


def markdown(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


results = read(EMP / 'RESULTS.json')
manifest = read(EMP / 'RUN_MANIFEST.json')
registry = read(EMP / 'registry/CANDIDATE_REGISTRY.json')
charts = read(EMP / 'charts/INDEX.json')['charts']
inventory = read(EMP / 'coverage/native-inventory-all.json')
notes = json.loads((OUT / 'review_notes.json').read_text())
for split in manifest['splits'].values():
    path = Path(split['path'])
    read(path)
    assert identities[str(path.relative_to(ROOT))] == split['sha256']
assert manifest['manifest_sha256'] == 'd80935d548abe3cafcd695ec842dc69b1d3391646c2da8fe0db9e935a6c37247'

jobs_by_rule = defaultdict(list)
artifacts = {}
records = {}
rule_records = defaultdict(list)
unknowns = []
checkpoint_count = 0
for path in sorted((EMP / 'checkpoints').glob('*.json')):
    checkpoint = read(path)
    checkpoint_count += 1
    assert checkpoint['run_manifest_sha256'] == manifest['manifest_sha256']
    assert checkpoint['registry_sha256'] == registry['registry_sha256']
    assert checkpoint['search_completed']
    artifact_path = Path(checkpoint['artifact_path'])
    artifact = read(artifact_path)
    assert identities[str(artifact_path.relative_to(ROOT))] == checkpoint['artifact_sha256']
    artifacts[str(artifact_path)] = artifact
    for rule in checkpoint['rules']:
        jobs_by_rule[rule['rule_id']].append({
            'date': checkpoint['session_date'], 'job_id': checkpoint['job_id'],
            'instrument_id': checkpoint['instrument_id'], 'cohort': checkpoint['cohort'],
            'checkpoint': str(path.relative_to(ROOT)), 'status': rule['status'],
            'observed_counts': {k: rule['summary'][k] for k in ('p', 'f', 'u', 'n', 'N')},
            'population_holes': rule['population_holes'],
            'incomplete_references': [r for r in rule['references'] if not r.get('complete')],
        })
    for record in artifact['records']:
        opportunity, replay = record['opportunity'], record['replay']
        oid = opportunity['opportunity_id']
        assert oid not in records
        records[oid] = record
        rule_records[opportunity['rule_id']].append(record)
        assert replay['source_method_verdict'] == 'unknown'
        assert replay['proxy_as_faithful'] == 0 and replay['timing_violations'] == 0
        if replay['verdict'] == 'unknown':
            unknowns.append({'opportunity_id': oid, 'rule_id': opportunity['rule_id'],
                             'date': opportunity['session_date'], 'side': opportunity['side'],
                             'trigger_bar_id': opportunity['trigger']['bar_id'],
                             'reason': replay['reason'], 'censored': replay['censored'],
                             'ambiguous': replay['ambiguous']})

registry_rules = {r['rule_id']: r for r in registry['rules']}
assert len(results['rule_reports']) == len(registry_rules) == 50
assert len(results['extra_observation_units']) == 8
assert {r['rule_id'] for r in results['rule_reports']} == set(registry_rules)
assert set(notes['branch_notes']) == {r['rule_id'] for r in registry['rules'] if r['supported']}

branch_rows = []
for report in results['rule_reports']:
    rid = report['rule_id']
    jobs = jobs_by_rule[rid]
    population = Counter(r['status'] for r in jobs)
    observed = report['observed_counts']
    if report['supported']:
        assert len(jobs) == report['scope']['scanned'] == report['scope']['eligible']
        assert population['missing_data'] == report['scope']['missing']
        assert {k: sum(j['observed_counts'][k] for j in jobs) for k in observed} == observed
        assert observed['N'] == len(rule_records[rid]) == observed['p'] + observed['f'] + observed['u']
        assert observed['n'] == observed['p'] + observed['f']
        assert Counter(r['replay']['verdict'] for r in rule_records[rid]) == Counter({k: v for k, v in [('pass', observed['p']), ('fail', observed['f']), ('unknown', observed['u'])] if v})
    else:
        assert not jobs and all(v is None for v in observed.values())
    groups = [g for g in results['groups'] if g['rule_id'] == rid]
    branch_rows.append({
        'rule_id': rid, 'method_id': report['method_id'], 'branch': report['branch'],
        'disposition': report['disposition'], 'status': report['status'],
        'supported': report['supported'], 'observation_unit': report['observation_unit'],
        'declared_search': report['scope'], 'job_status_counts': dict(population),
        'completed_zero_opportunity_jobs': sum(j['status'] == 'completed' and j['observed_counts']['N'] == 0 for j in jobs),
        'observed_counts': observed, 'published_counts': {k: report[k] for k in ('p', 'f', 'u', 'n', 'N')},
        'population_complete': report['population_complete'],
        'group_count': len(groups), 'complete_group_count': sum(g['population_complete'] for g in groups),
        'groups_with_identified_rate': sum(g['rate'] is not None for g in groups),
        'observed_by_year': {year: {k: sum(j['observed_counts'][k] for j in jobs if j['date'].startswith(year)) for k in ('p', 'f', 'u', 'n', 'N')} for year in sorted({j['date'][:4] for j in jobs})},
        'unknown_reasons': dict(Counter(r['replay']['reason'] for r in rule_records[rid] if r['replay']['verdict'] == 'unknown')),
        'source_method_verdict': report['source_method_verdict'],
        'definition_or_disposition': registry_rules[rid]['readable_rule'],
        'review': notes['branch_notes'].get(rid, registry_rules[rid]['readable_rule']),
        'source_refs': registry_rules[rid]['source_refs'], 'jobs': jobs,
    })

parents = {r['opportunity']['opportunity_id']: r for r in records.values()
           if r['opportunity']['branch'] == 'nyam_box' and r['replay']['verdict'] == 'pass'}
children = [r for r in records.values() if r['opportunity']['branch'] == 'mss_fvg_refinement']
parent_ids = [r['opportunity']['reference']['parent_opportunity_id'] for r in children]
assert len(children) == len(set(parent_ids)) == len(parents) == 99
assert set(parent_ids) == set(parents)
assert all(r['opportunity']['available_at'] == parents[r['opportunity']['reference']['parent_opportunity_id']]['replay']['completed_at'] for r in children)
dual_band = [r for r in unknowns if r['reason'] == 'both_deviation_bands_in_trigger_bar']
assert len(dual_band) == 10 and len({r['trigger_bar_id'] for r in dual_band}) == 6

seen = set()
chart_rows = []
for index, chart in enumerate(charts):
    path = Path(chart['chart_path'])
    identities[str(path.relative_to(ROOT))] = sha256(path.read_bytes()).hexdigest()
    assert identities[str(path.relative_to(ROOT))] == chart['chart_sha256']
    assert identities[str(Path(chart['source_artifact']).relative_to(ROOT))] == chart['source_sha256']
    record = records[chart['opportunity_id']]
    assert content_hash(record) == chart['record_sha256']
    assert record['opportunity']['rule_id'] == chart['rule_id']
    assert record['replay']['verdict'] == chart['verdict']
    key = chart['rule_id'], chart['verdict']
    if key in seen:
        continue
    seen.add(key)
    opportunity, replay = record['opportunity'], record['replay']
    chart_rows.append({**chart, 'index': index, 'analyst_observation': notes['chart_notes'][str(index)],
                       'side': opportunity['side'], 'available_et': clock(opportunity['available_at']),
                       'endpoint_et': clock(replay['completed_at']), 'expiry_et': clock(opportunity['expiry_at']),
                       'reference': opportunity['reference'], 'trigger': opportunity['trigger'],
                       'endpoint': replay['endpoint'], 'endpoint_reason': replay['reason'],
                       'review_scope': 'PNG overview plus linked record; no author-method or trade validation'})
assert {int(i) for i in notes['chart_notes']} == {r['index'] for r in chart_rows}
assert len(chart_rows) == 36 and len({r['rule_id'] for r in chart_rows}) == 15

job_status = Counter(j['status'] for rows in jobs_by_rule.values() for j in rows)
assert job_status == {'missing_data': 733, 'completed': 1535, 'completed_with_population_holes': 6}
totals = {k: sum(r['observed_counts'][k] or 0 for r in branch_rows) for k in ('p', 'f', 'u', 'n', 'N')}
assert totals == {'p': 1000, 'f': 1412, 'u': 40, 'n': 2412, 'N': 2452}
assert len(results['groups']) == 790
for group in results['groups']:
    if not group['population_complete']:
        assert group['rate'] is None and group['interval'] is None
        if group['observed_counts']['N'] == 0:
            assert all(group[k] is None for k in ('p', 'f', 'u', 'n', 'N'))
        else:
            assert {k: group[k] for k in ('p', 'f', 'u', 'n', 'N')} == group['observed_counts']
    if group['observed_counts']['N'] == 0:
        assert group['rate'] is None and group['interval'] is None

summary = {
    'schema': 'phase1-follow-on-evidence-review-v1', 'review_date_utc': '2026-09-12',
    'phase1_status': 'complete; this is a separate follow-on review',
    'source_commit': SOURCE_COMMIT, 'run_version': manifest['run_version'],
    'run_manifest_sha256': manifest['manifest_sha256'], 'registry_sha256': registry['registry_sha256'],
    'scope': results['scope'], 'checkpoint_count': checkpoint_count,
    'rule_count': 50, 'supported_comparison_count': 19, 'source_disposition_count': 31,
    'extra_observation_unit_count': 8, 'observed_record_counts_additive_only': totals,
    'job_status_counts': dict(job_status), 'group_count': 790,
    'complete_groups': sum(g['population_complete'] for g in results['groups']),
    'incomplete_groups': sum(not g['population_complete'] for g in results['groups']),
    'incomplete_groups_with_unavailable_counts': sum(not g['population_complete'] and g['observed_counts']['N'] == 0 for g in results['groups']),
    'incomplete_groups_with_observed_counts': sum(not g['population_complete'] and g['observed_counts']['N'] > 0 for g in results['groups']),
    'groups_with_identified_rate': sum(g['rate'] is not None for g in results['groups']),
    'complete_zero_groups': sum(g['population_complete'] and g['observed_counts']['N'] == 0 for g in results['groups']),
    'all_unknown_complete_groups': sum(g['population_complete'] and g['observed_counts']['N'] > 0 and g['observed_counts']['n'] == 0 for g in results['groups']),
    'unknown_reason_counts': dict(Counter(r['reason'] for r in unknowns)),
    'mss_parent_lineage': {'children': 99, 'unique_passing_nyam_parents': 99, 'one_to_one': True, 'child_availability_equals_parent_completion': True},
    'sires_dual_band_ambiguity': {'observations': 10, 'unique_trigger_bars': 6},
    'charts_hash_verified': len(charts), 'charts_visually_reviewed': len(chart_rows),
    'rules_with_chart_review': len({r['rule_id'] for r in chart_rows}),
    'replay_expanded': False, 'parameters_changed': False,
}
write_json('REVIEW_SUMMARY.json', summary)
write_json('DENOMINATOR_AUDIT.json', {'schema': 'phase1-branch-denominator-review-v1',
                                    'branches': branch_rows, 'unknown_observations': unknowns,
                                    'extra_observation_units': results['extra_observation_units']})
write_json('CHART_REVIEW.json', {'scope': notes['scope'], 'charts': chart_rows})

lines = ['# Branch evidence matrix', '',
         'All 50 registered branches are listed below. `null` means unavailable. Observed N counts initial records; n=p+f and N=p+f+u. These additive counts do not authorize pooled branch/family rates.', '',
         'Complete/partial/missing are **rule/date search jobs**, not opportunity counts. A complete search may contain unknown outcomes. Zero means a complete search found no initial opportunity. Group columns use the frozen rule/cohort/year/instrument/evidence-mode/observation-unit strata.', '',
         '## Supported comparisons', '',
         '| Branch | Observed p / f / u | Observed n / N | Complete / partial / missing jobs | Complete zero jobs | Complete / all groups | Frozen status |',
         '| --- | ---: | ---: | ---: | ---: | ---: | --- |']
for row in branch_rows:
    if not row['supported']:
        continue
    c, j = row['observed_counts'], row['job_status_counts']
    lines.append(f"| {row['method_id']} / {row['branch']} | {c['p']} / {c['f']} / {c['u']} | {c['n']} / {c['N']} | {j.get('completed',0)} / {j.get('completed_with_population_holes',0)} / {j.get('missing_data',0)} | {row['completed_zero_opportunity_jobs']} | {row['complete_group_count']} / {row['group_count']} | {row['status']} |")
lines += ['', '## Branch conclusions', '', '| Branch | Definition and evidence implication |', '| --- | --- |']
for row in branch_rows:
    if row['supported']:
        lines.append(f"| {row['method_id']} / {row['branch']} | {markdown(row['review'])} |")
lines += ['', '## Source dispositions', '',
          'Each of these 31 branches has unavailable p/f/u/n/N, no declared empirical search, and source-method verdict unknown. More historical price data alone does not supply the missing definition, selection, process or state record.', '',
          '| Branch | Disposition | Required evidence or limitation |', '| --- | --- | --- |']
for row in branch_rows:
    if not row['supported']:
        lines.append(f"| {row['method_id']} / {row['branch']} | {row['disposition']} | {markdown(row['review'])} |")
lines += ['', '## Separate observation units', '',
          'All eight remain supplied-only with unavailable denominators. They are not added to initial market opportunities.', '',
          '| Unit ID | Observation unit | Status | Required evidence |', '| --- | --- | --- | --- |']
for row in results['extra_observation_units']:
    lines.append(f"| {row['unit_id']} | {row['observation_unit']} | {row['status']} | {markdown(row['reason'])} |")
lines += ['', 'The exact definitions, counts by year, population holes, missing reference objects and per-date checkpoint links are in [DENOMINATOR_AUDIT.json](DENOMINATOR_AUDIT.json). Source definitions remain in the [frozen registry](../empirical/registry/CANDIDATE_REGISTRY.json).', '']
(OUT / 'BRANCH_MATRIX.md').write_text('\n'.join(lines))

lines = ['# Chart evidence review', '', notes['scope'], '',
         'All 50 existing chart files and their scored-record/source-artifact hashes were verified. This follow-on visual sample is 36 charts covering 15 branches; four supported branches have no observed opportunities and therefore no charts. Original chart selection is chronological and stratified, not a random performance sample.', '',
         'The blue line marks availability; purple marks endpoint or expiry. Minute OHLC bars are plotted at their interval starts, so the bar drawn at an endpoint timestamp belongs to the next interval. Numerical predicates use the linked record. Source-method verdict remains unknown throughout.', '',
         '| Index and chart | Branch / verdict | Visual observation and limitation |', '| --- | --- | --- |']
for row in chart_rows:
    relative_chart = '../empirical/charts/' + Path(row['chart_path']).name
    lines.append(f"| [{row['index']}]({relative_chart}) | {row['rule_id']} / {row['verdict']} | {markdown(row['analyst_observation'])} |")
lines += ['', '## Diagnostic improvements for later work', '',
          'Add the TDO line for Asia cases, a labeled pre-bar VWAP at the touch (and its time series) for GB-VWAP, and the 2-minute candle grid/gap for MSS/FVG. A local-price inset would improve prior-month/week examples whose distant opposite boundary compresses the bars. These are presentation limitations of the existing overviews; the exact predicate evidence is retained in the records.', '',
          'No existing chart, record or verdict was rewritten. [CHART_REVIEW.json](CHART_REVIEW.json) binds each note to its chart, source artifact, scored-record SHA256, clocks, reference, trigger and endpoint.', '']
(OUT / 'CHART_REVIEW.md').write_text('\n'.join(lines))

tables = (EMP / 'PHASE_AND_AUDIT_TABLES.md').read_text().replace('](RESULTS.md)', '](../empirical/RESULTS.md)')
(OUT / 'PHASE_AND_AUDIT_TABLES.md').write_text(tables.replace('# PHASE and audit tables', '# PHASE and audit tables\n\nAccepted Phase 1 tables reproduced for this follow-on review. No new replay or test-suite run is represented here.', 1))
identities[str((EMP / 'PHASE_AND_AUDIT_TABLES.md').relative_to(ROOT))] = sha256((EMP / 'PHASE_AND_AUDIT_TABLES.md').read_bytes()).hexdigest()
implementation_files = manifest['implementation']['files']
for rel, expected in implementation_files.items():
    assert sha256((ROOT / rel).read_bytes()).hexdigest() == expected, rel
write_json('SOURCE_IDENTITIES.json', {'source_commit': SOURCE_COMMIT,
                                     'run_manifest_sha256': manifest['manifest_sha256'],
                                     'source_files_sha256': identities,
                                     'accepted_implementation_files_verified': len(implementation_files),
                                     'validation': 'counts, nulls, group suppression, 165 checkpoint/artifact pairs, 50 chart/record identities, 99 parent-child links and manual-note selection agree'})
local_links = []
for path in sorted(OUT.glob('*.md')):
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if '://' in target or target.startswith('#'):
            continue
        linked = (path.parent / target.split('#')[0]).resolve()
        if linked != OUT / 'VERIFICATION.json':
            assert linked.exists(), (path.name, target)
        local_links.append({'document': path.name, 'target': target})
probe = json.loads((OUT / 'RECOVERY_PROBES.json').read_text())
assert probe['source_inventory']['sha256'] == identities[str((EMP / 'coverage/native-inventory-all.json').relative_to(ROOT))]
assert probe['probe_script_sha256'] == sha256((OUT / 'probe_recovery.py').read_bytes()).hexdigest()
output_hashes = {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'VERIFICATION.json'}
write_json('VERIFICATION.json', {
    'schema': 'phase1-evidence-review-verification-v1', 'status': 'pass',
    'source_commit': SOURCE_COMMIT, 'run_manifest_sha256': manifest['manifest_sha256'],
    'checks': {'branch_count': 50, 'extra_units': 8, 'checkpoint_artifact_pairs': checkpoint_count,
               'observed_counts_reconciled': totals, 'group_suppression': True,
               'chart_file_and_scored_record_hashes': len(charts),
               'manual_notes_match_declared_chart_sample': len(chart_rows),
               'mss_parent_child_links': len(children),
               'accepted_implementation_file_hashes': len(implementation_files),
               'recovery_probe_inventory_and_script_identity': True,
               'local_markdown_links_resolve': len(local_links)},
    'scope': 'Derived report verification and bounded presence probes; no new test-suite run, replay, input admission or certified data repair.',
    'visual_inspection': notes['scope'], 'report_files_sha256': output_hashes,
})
print(json.dumps(summary, indent=2, sort_keys=True))
