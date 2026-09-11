"""Validate audit coverage and artifacts without changing any production input."""
from __future__ import annotations

import ast
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

from chart_audit_report import ALIASES, DEST, OUT, REFRESH, ROOT, target_link


def read(name):
    return json.loads((OUT / name).read_text())


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def validate_refresh(check, artifact, records, plots, reviews, native, figures, vectors):
    """Check recorded manual coverage against the exact expanded source bytes."""
    def reread(name):
        path = REFRESH / name
        artifact(path)
        return json.loads(path.read_text())

    coverage = reread('source_coverage.json')
    source_files = coverage['files']
    source_by_path = {x['source']: x for x in source_files}
    check(len(source_files) == len(source_by_path) == 106, 'Expanded source inventory differs')
    source_digest = hashlib.sha256(json.dumps(
        source_files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    check(source_digest == coverage['source_set_sha256'], 'Source-set digest is inconsistent')
    for item in source_files:
        path = ROOT / item['source']
        artifact(path, item['sha256'])
        if path.is_file():
            check(path.stat().st_size == item['bytes'], 'Source size changed: ' + item['source'])

    pdfs = reread('pdf_manifest.json')
    pdf_by_path = {p['source']: p for p in pdfs}
    text_reviews = reread('source_text_reread.json')
    check(len(pdfs) == len(pdf_by_path) == len(text_reviews) == 41, 'Expanded PDF count differs')
    check(sum(len(p['pages']) for p in pdfs) == 711, 'Expanded PDF page count differs')
    check({r['source'] for r in text_reviews} == set(pdf_by_path), 'PDF/text reread sets differ')
    for p in pdfs:
        check([q['page'] for q in p['pages']] == list(range(1, len(p['pages']) + 1)),
              'Expanded PDF page inventory incomplete: ' + p['source'])
        check(p['sha256'] == source_by_path.get(p['source'], {}).get('sha256'),
              'PDF hash differs from source set: ' + p['source'])
    for q in text_reviews:
        p = pdf_by_path.get(q['source'], {})
        check(q.get('all_pages_text_reread') is True and bool(q.get('notes'))
              and q['page_count'] == len(p.get('pages', [])) and q['sha256'] == p.get('sha256'),
              'Incomplete refreshed PDF text review: ' + q['source'])

    pine = reread('pine_reread.json')
    prose = reread('prose_reread.json')
    pine_copies = {q['source']: q['copy'] for q in read('pine_copy_manifest.json')}
    canonical_pine_paths = {pine_copies.get(q['source'], q['source']) for q in pine}
    for name, entries, expected in [('Pine', pine, 85), ('prose', prose, 13)]:
        check(len(entries) == len({q['source'] for q in entries}) == expected,
              'Refreshed ' + name + ' inventory differs')
        for q in entries:
            path = ROOT / (pine_copies.get(q['source'], q['source']) if name == 'Pine' else q['source'])
            artifact(path, q['sha256'])
            check(q.get('reread_complete') is True and bool(q.get('notes')),
                  'Incomplete ' + name + ' reread: ' + q['source'])
            if path.is_file():
                check(len(path.read_text().splitlines()) == q['lines'],
                      'Reread line count differs: ' + q['source'])
    pine_archive = reread('pine_archive_coverage.json')
    check(len(pine_archive) == 83, 'Pine archive member count differs')
    with zipfile.ZipFile(ROOT / 'sources/documents/indicators/Pinescript-indicators--main.zip') as archive:
        members = {i.filename for i in archive.infolist() if not i.is_dir()}
        check(members == {q['member'] for q in pine_archive}, 'Pine archive coverage differs')
        for q in pine_archive:
            sha = hashlib.sha256(archive.read(q['member'])).hexdigest()
            check(q.get('copy_equal') is True and sha == q['sha256'],
                  'Pine archive member changed: ' + q['member'])
            artifact(q['copy'], sha)
    check({q['copy'] for q in pine_archive} <= canonical_pine_paths,
          'A Pine archive member lacks a full reread')

    old_figures = reread('old_figure_reread.json')
    old_by_key = {q['key']: q for q in figures}
    check(len(old_figures) == 330 and {q['key'] for q in old_figures} == set(old_by_key),
          'Original figure reread coverage differs')
    for q in old_figures:
        check(q.get('reviewed') is True and bool(q.get('notes'))
              and q['sha256'] == old_by_key.get(q['key'], {}).get('sha256'),
              'Original figure reread incomplete: ' + q['key'])
        artifact(q['artifact'], q['sha256'])
    old_vectors = reread('old_vector_reread.json')
    vector_keys = {(q['source'], q['page']) for q in vectors}
    check(len(old_vectors) == 18 and {(q['source'], q['page']) for q in old_vectors} == vector_keys,
          'Vector reread coverage differs')
    for q in old_vectors:
        check(q.get('reviewed') is True and bool(q.get('notes')), 'Vector reread incomplete: ' + str(q))

    detail_path = REFRESH / 'raw_detail_pass_2026-09-11.json'
    detail = reread(detail_path.name)
    detail_digest = digest(detail_path)
    new_figures = reread('new_figure_review.json')
    figure_key = lambda q: (q['pdf'], q['page'], q['image'])
    new_by_key = {figure_key(q): q for q in new_figures}
    check(len(new_figures) == len(new_by_key) == 158, 'Expanded figure inventory differs')
    detail_keys = set()
    detail_page_count = 0
    crop_count = 0
    for p in detail['pdfs']:
        page_count = len(pdf_by_path.get(p['pdf'], {}).get('pages', []))
        check(p['page_count'] == page_count and p['sha256'] == source_by_path[p['pdf']]['sha256'],
              'Close-pass PDF identity differs: ' + p['pdf'])
        check([q['page'] for q in p['pages']] == list(range(1, page_count + 1)),
              'Close-pass pages incomplete: ' + p['pdf'])
        for page in p['pages']:
            detail_page_count += 1
            check(page.get('detail_pass_complete') is True and bool(page.get('page_notes')),
                  'Raw close-pass page incomplete: ' + str((p['pdf'], page['page'])))
            artifact(page['render'], page.get('render_sha256'))
            check(page['image_occurrences'] == page['recorded_image_occurrences'] == len(page['figures']),
                  'Close-pass image count differs: ' + str((p['pdf'], page['page'])))
            for q in page['figures']:
                key = (p['pdf'], page['page'], q['image'])
                check(key not in detail_keys, 'Repeated close-pass figure: ' + str(key))
                detail_keys.add(key)
                reviewed = any(q.get(k) for k in ('native_viewed', 'native_full_viewed',
                    'native_whole_viewed', 'native_pixels_inspected_in_crops', 'crops_viewed'))
                limits_recorded = isinstance(q.get('limitations'), list) and (
                    bool(q['limitations']) or not q.get('affected_ids'))
                check(reviewed and bool(q.get('observations')) and limits_recorded,
                      'Incomplete native/detail figure review: ' + str(key))
                check(set(q.get('affected_ids', [])) <= {r['id'] for r in records},
                      'Unknown affected ID: ' + str(key))
                f = new_by_key.get(key, {})
                cp = f.get('close_pass', {})
                check(f.get('reviewed') is True and cp.get('complete') is True
                      and cp.get('observations') == q.get('observations')
                      and cp.get('limitations') == q.get('limitations'),
                      'Close-pass observations not reconciled: ' + str(key))
                if f:
                    artifact(f['artifact'], f['sha256'])
                for crop in q.get('crops_viewed', []):
                    path = REFRESH / 'detail-crops' / Path(p['pdf']).stem / crop
                    artifact(path)
                    crop_count += 1
    check(detail_page_count == 131 and detail_keys == set(new_by_key),
          'Complete raw close-pass inventory differs')

    zip_rows = reread('zip_caption_candidates.json')
    with zipfile.ZipFile(ROOT / 'sources/x-raw-2026-09-11/JJumboFX_media_v2.zip') as archive:
        members = {i.filename for i in archive.infolist() if not i.is_dir()}
        check(len(zip_rows) == 48 and members == {q['zip_member'] for q in zip_rows},
              'Raw media archive inventory differs')
        for q in zip_rows:
            sha = hashlib.sha256(archive.read(q['zip_member'])).hexdigest()
            check(q.get('unpacked_equal') is True and sha == q['sha256'],
                  'Raw media archive member changed: ' + q['zip_member'])
            artifact(q['unpacked_file'], sha)
            for match in q.get('caption_matches', []):
                if match.get('pixel_exact'):
                    f = new_by_key.get(figure_key(match), {})
                    check(q.get('rgb_sha256') == f.get('rgb_sha256') and bool(f.get('post_id')),
                          'Zip image lacks a verified PDF/post match: ' + q['zip_member'])
    zip_images = [q for q in zip_rows if 'caption_matches' in q]
    unmatched = [q['zip_member'] for q in zip_images if not any(
        m.get('pixel_exact') for m in q['caption_matches'])]
    check(len(zip_images) == 45 and len(unmatched) == 4, 'Raw zip image association counts differ')
    videos = reread('video_review.json')
    check(len(videos) == 2, 'Video review inventory differs')
    for q in videos:
        check(q['source'] in source_by_path and bool(q.get('match'))
              and bool(q.get('visual_method')) and bool(q.get('observations'))
              and bool(q.get('audio_review')), 'Incomplete or overclaimed video coverage: ' + q['source'])
    references = reread('reference_image_reread.json')
    check(len(references) == 1, 'Separate reference-image inventory differs')
    for q in references:
        check(q.get('reviewed') is True and bool(q.get('notes')) and len(q.get('crops', [])) == 3,
              'Reference-image review incomplete')
        artifact(q['source'], q['sha256'])
        for crop in q['crops']:
            artifact(crop)

    plot_by_key = {(p['id'], p['case'], p['date']): p for p in plots}
    def current(stamp, name):
        check(stamp.get('source_set_sha256') == source_digest
              and stamp.get('close_pass_sha256') == detail_digest, 'Stale source refresh: ' + name)
    for q in reviews:
        key = (q['id'], q['case'], q['date'])
        stamp = q.get('source_refresh', {})
        current(stamp, str(key))
        if key in plot_by_key:
            sha = digest(OUT / plot_by_key[key]['plot'])
            check(stamp.get('rereviewed_plot_sha256') == q.get('reviewed_plot_sha256') == sha,
                  'Chart refresh hash differs: ' + str(key))
    for q in native:
        stamp = q.get('source_refresh', {})
        current(stamp, q['plot'])
        check(stamp.get('rereviewed_plot_sha256') == q['sha256'],
              'Native product refresh hash differs: ' + q['plot'])
    fields = ['source_ok', 'code_ok', 'score_event_ok', 'chart_ok']
    pdf_by_stem = {Path(p['source']).stem: p for p in pdfs}
    for r in records:
        stamp = r.get('source_refresh', {})
        current(stamp, r['id'])
        check(stamp.get('rechecked') is True and stamp.get('repair_specification_rechecked') is True
              and bool(stamp.get('clock_basis')) and stamp.get('source_refs') == r['sources'],
              'Incomplete row/specification refresh: ' + r['id'])
        checks = stamp.get('checks', {})
        check(list(checks) == fields, 'Missing explicit verdict reasons: ' + r['id'])
        for field, verdict in zip(fields, r['oks']):
            check(checks.get(field, {}).get('verdict') == verdict
                  and bool(checks.get(field, {}).get('reason')), 'Stale verdict reason: ' + r['id'] + ' ' + field)
        rechecked = stamp.get('rechecked_charts', [])
        rechecked_keys = {(r['id'], q['case'], q['date']) for q in rechecked}
        required_keys = {k for k in plot_by_key if k[0] == r['id'] and k[1] in ('A', 'B')}
        check(len(rechecked) >= 2 and required_keys <= rechecked_keys,
              'Two main charts not rechecked after source close pass: ' + r['id'])
        for q in rechecked:
            key = (r['id'], q['case'], q['date'])
            check(plot_by_key.get(key, {}).get('plot') == q['plot'], 'Rechecked chart identity differs: ' + str(key))
            artifact(OUT / q['plot'], q['sha256'])
        for ref in r['sources']:
            alias, _, number = ref.rpartition(':')
            check(number.isdigit(), 'Unresolved source reference: ' + r['id'] + ' ' + ref)
            if not number.isdigit():
                continue
            page = int(number)
            if alias.startswith('PINE '):
                path = OUT / 'source-pine' / alias[5:]
                check(path.is_file() and 1 <= page <= len(path.read_text().splitlines()),
                      'Invalid Pine line reference: ' + ref)
            elif alias == 'GB':
                path = ROOT / 'planning/phase-1-fable/references/greenbirdtrader-trading-framework.md'
                check(1 <= page <= len(path.read_text().splitlines()), 'Invalid GB reference: ' + ref)
            elif alias == 'REFIMG':
                check(page == 1, 'Invalid native image reference: ' + ref)
            else:
                stem = {'JRAW': 'JJumboFX_Raw_X_Archive_v2', 'GBRAW': 'greenbirdtrader-complete'}.get(
                    alias, ALIASES.get(alias, alias))
                check(stem in pdf_by_stem and 1 <= page <= len(pdf_by_stem.get(stem, {}).get('pages', [])),
                      'Invalid PDF source reference: ' + ref)

    protected = reread('protected_inputs.json')
    check(len(protected) == 105, 'Protected-input inventory differs')
    changed = [q['path'] for q in protected if not (ROOT / q['path']).is_file()
               or digest(ROOT / q['path']) != q['sha256']]
    check(not changed, 'Protected inputs changed: ' + str(changed))
    for path in REFRESH.glob('*.json'):
        artifact(path)
    return {
        'source_files': len(source_files), 'source_set_sha256': source_digest,
        'source_PDFs': len(pdfs), 'source_PDF_pages': 711,
        'raw_close_pass_pages': detail_page_count, 'raw_close_pass_figures': len(detail_keys),
        'raw_close_pass_crop_views': crop_count, 'close_pass_sha256': detail_digest,
        'Pine_archive_members': len(pine_archive), 'Pine_and_supplement_rereads': len(pine),
        'prose_rereads': len(prose), 'raw_zip_members': len(zip_rows),
        'unmatched_zip_images_excluded': unmatched, 'video_reviews_with_explicit_limits': len(videos),
        'refreshed_rows': len(records), 'refreshed_dated_charts': len(reviews),
        'refreshed_native_charts': len(native),
        'protected_input_preservation': {'group': 'protected_inputs', 'checked': len(protected), 'changed': changed},
    }


def main():
    errors = []
    delivery = {}

    def check(condition, message):
        if not condition:
            errors.append(message)

    def artifact(path, expected=None):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        if not path.is_file():
            errors.append('Missing artifact: ' + str(path))
            return
        sha = digest(path)
        delivery[str(path.relative_to(ROOT))] = sha
        if expected:
            check(sha == expected, 'Changed artifact: ' + str(path))

    rules = (ROOT / 'planning/phase-1-live/RULES.md').read_text()
    section_b = rules.split('## B. Sourced recipes', 1)[1].split('## C.', 1)[0]
    ids = re.findall(r'^\*\*(R-[JGAFRSP]\d{2})\b', section_b, re.M)
    manifest = read('source_manifest.json')
    check(len(ids) == 105 and ids == manifest['recipe_ids'], 'Section B ID inventory mismatch')
    records = [r for path in sorted(OUT.glob('audit_records_*.json'))
               for r in json.loads(path.read_text())]
    counts = Counter(r['id'] for r in records)
    check(set(counts) == set(ids) and all(n == 1 for n in counts.values()),
          'Missing, extra or repeated audit records')
    oks = {'yes', 'no', 'blocked', 'cannot-tell', 'gap'}
    for r in records:
        check(len(r['oks']) == 4 and set(r['oks']) <= oks, 'Invalid verdicts: ' + r['id'])
        for field in ('title', 'finding', 'source', 'sources', 'targets', 'fix', 'acceptance'):
            check(bool(r.get(field)), 'Missing specification ' + field + ': ' + r['id'])
        check(isinstance(r.get('ask_user'), bool), 'Invalid ask_user: ' + r['id'])
        if r.get('ask_user'):
            check(bool(r.get('question')), 'Missing chart question: ' + r['id'])
        for target in r['targets']:
            try:
                target_link(target)
            except Exception as exc:
                errors.append(f'{r["id"]} target {target}: {exc}')

    text = DEST.read_text()
    check('**Audit complete for all 105 Section B IDs.**' in text, 'Report remains draft')
    table = text.split('## Required per-ID verdicts', 1)[1].split('## Per-ID repair specifications', 1)[0]
    rows = [re.split(r'(?<!\\)\|', s)[1:-1] for s in table.splitlines() if s.startswith('| R-')]
    check([row[0].strip() for row in rows] == ids, 'Required verdict table ID order/coverage mismatch')
    for row in rows:
        check(len(row) == 7, 'Wrong verdict-table column count: ' + str(row[:1]))
        check(all(s.strip() in oks for s in row[1:5]), 'Invalid verdict-table values: ' + str(row[:1]))
        check(row[-1].strip() in ('yes', 'no'), 'Invalid ask_user table value: ' + str(row[:1]))
    specs = re.findall(r'^### (R-[JGAFRSP]\d{2}) —', text, re.M)
    check(specs == ids, 'Per-ID repair specification order/coverage mismatch')
    check('| family | variant | n | faithful_disagreements | status | report path |' in text,
          'PHASE table missing')
    check('| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |' in text,
          'Family audit table missing')
    check('review pending' not in text, 'Unreviewed chart in report')
    check('SOURCE-SET REDO PENDING' not in text and 'Source-set redo pending' not in text,
          'Unfinished source refresh in report')
    check(text.count('**Clock evidence:**') == 105 and text.count('**Refreshed verdict reasons:**') == 105,
          'Per-ID clock evidence or four-check reasons missing')

    link_count = 0
    for match in re.finditer(r'\]\(<([^>]+)>\)|\]\(([^)]+)\)', text):
        target = match.group(1) or match.group(2)
        if target.startswith(('https://', 'http://', '#')):
            continue
        link_count += 1
        plain, colon, number = target.rpartition(':')
        lineno = int(number) if colon and number.isdigit() else None
        path = Path(plain if lineno is not None else target)
        check(path.is_absolute(), 'Nonabsolute file link: ' + target)
        check(path.is_file(), 'Broken file link: ' + target)
        if lineno is not None and path.is_file():
            check(1 <= lineno <= len(path.read_text().splitlines()), 'Invalid linked line: ' + target)

    plots = []
    for filename in ('plot_results.json', 'source_date_plot_results.json',
                     'extra_plot_results.json', 'clock_plot_results.json'):
        if (OUT / filename).exists():
            plots.extend(read(filename))
    reviews = read('chart_review.json')
    by_key = {(r['id'], r['case'], r['date']): r for r in reviews}
    keys = [(p['id'], p['case'], p['date']) for p in plots]
    check(len(keys) == len(set(keys)) == len(by_key) == len(reviews), 'Repeated or unmatched chart reviews')
    check(set(keys) == set(by_key), 'Chart/review inventory differs')
    for ident in ids:
        cases = [p for p in read('plot_results.json') if p['id'] == ident]
        check(len(cases) == 2 and len({p['date'] for p in cases}) == 2,
              'Two distinct main dated charts required: ' + ident)
    for p in plots:
        key = (p['id'], p['case'], p['date'])
        q = by_key.get(key, {})
        check(q.get('reviewed') is True and bool(q.get('source_should_fire')) and bool(q.get('notes')),
              'Incomplete manual chart review: ' + str(key))
        artifact(OUT / p['plot'], q.get('reviewed_plot_sha256'))
        artifact(OUT / p['trace'])
        if (OUT / p['trace']).is_file():
            trace = json.loads((OUT / p['trace']).read_text())
            check(trace['case']['id'] == p['id'] and trace['case']['date'] == p['date'],
                  'Wrong chart trace identity: ' + str(key))
    native = read('native_options_review.json')
    check(len(native) == 16, 'Native product supplements incomplete')
    for q in native:
        check(q.get('reviewed') is True and bool(q.get('notes')), 'Native review missing: ' + q['plot'])
        artifact(OUT / q['plot'], q.get('sha256'))

    figures = read('figure_crop_manifest.json')
    vectors = read('vector_review_manifest.json')
    check(len(figures) == 330, 'Source figure count differs')
    native_only_decorations = []
    def crop_reviewed(figure, entry):
        review = entry['review']
        if isinstance(review, str):
            return 'four' in review.lower() and 'crop' in review.lower()
        if (review.get('all_four_native_crops_reviewed') or review.get('all_four_native_crops_viewed')
                or review.get('crops_reviewed') == 4):
            return True
        if review.get('native_reviewed') and review.get('crops_reviewed') == 0:
            # These two repeated logos contain no market chart or trading level.
            if 'logo' in review.get('notes', '').lower():
                native_only_decorations.append(figure['key'])
                return True
        group = read(entry['review_file'])
        inspection = group.get('inspection', '').lower() if isinstance(group, dict) else ''
        return (review.get('reviewed') is True and 'four' in inspection and 'crop' in inspection
                and figure['key'] in group.get('figures', {}))
    for f in figures:
        check(f.get('reviewed') and bool(f.get('manual_reviews')), 'Source figure unreviewed: ' + f['key'])
        check(all(crop_reviewed(f, m) for m in f['manual_reviews']),
              'Native-crop review incomplete: ' + f['key'])
        artifact(f['artifact_original'], f['sha256'])
    for v in vectors:
        check(v.get('reviewed') and bool(v.get('review_notes')), 'Vector source unreviewed: ' + str(v))
        artifact(OUT / v['artifact_original'], v['sha256'])
    pages = read('page_scan_coverage.json')
    check(len(manifest['pdfs']) == 39, 'PDF source count differs')
    for pdf in manifest['pdfs']:
        source = ROOT / pdf['source']
        artifact(source, pdf['sha256'])
        check(pages.get(source.stem) == [p['page'] for p in pdf['pages']],
              'Page review coverage incomplete: ' + str(source))
    for p in read('pine_copy_manifest.json'):
        artifact(p['copy'], p['sha256'])
    check(len(read('pine_source_review.json')) == 85, 'Pine source review count differs')
    for p in read('prose_source_review.json'):
        check(bool(p.get('notes')), 'Prose source review missing')
        artifact(p['file'], p['sha256'])

    preservation = []
    inputs = read('audit_input_manifest.json')
    for group in ('audited_inputs', 'retained_tables'):
        changed = []
        for item in inputs[group]:
            path = ROOT / item['path']
            if not path.is_file() or digest(path) != item['sha256']:
                changed.append(item['path'])
        preservation.append({'group': group, 'checked': len(inputs[group]), 'changed': changed})
        check(not changed, 'Audited inputs changed: ' + str(changed))
    expanded = validate_refresh(check, artifact, records, plots, reviews, native, figures, vectors)
    preservation.append(expanded['protected_input_preservation'])
    fixture = read('fixture_snapshot.json')
    fixture_count = sum(v['n_cases'] for v in fixture.values())
    check(fixture_count == 598 and all(v['pass'] and v['n_failed'] == 0 for v in fixture.values()),
          'Retained fixture snapshot differs')
    scores = {s['id']: s for s in read('score_snapshot.json')}
    for r in records:
        if scores[r['id']]['impl_fidelity'] in ('gap', 'blocked'):
            check(any(v in ('gap', 'blocked') for v in r['oks']),
                  'Retained input gap lost: ' + r['id'])
    for path in (ROOT / 'implementation/tools').glob('chart_audit_*.py'):
        ast.parse(path.read_text(), filename=str(path))
        artifact(path)
    artifact(DEST)
    for path in OUT.glob('audit_records_*.json'):
        artifact(path)
    for path in OUT.glob('*.json'):
        if path.name not in ('completion_check.json', 'delivery_manifest.json'):
            artifact(path)
    summary = {'passed': not errors, 'errors': errors, 'id_count': len(ids),
               'build_steps': sum(len(r['fix']) for r in records),
               'acceptance_checks': sum(len(r['acceptance']) for r in records),
               'main_charts': len(read('plot_results.json')), 'dated_charts': len(plots),
               'native_supplements': len(native), 'source_figures': len(figures) + expanded['raw_close_pass_figures'],
               'source_vector_pages': len(vectors), 'source_PDF_pages': expanded['source_PDF_pages'],
               'original_source_figures': len(figures), 'original_source_PDF_pages': sum(len(p['pages']) for p in manifest['pdfs']),
               'expanded_source_validation': expanded,
               'decorative_figures_reviewed_native_only': native_only_decorations,
               'checked_local_links': link_count, 'input_preservation': preservation,
               'fixture_checks': fixture_count,
               'all_four_yes': [r['id'] for r in records if r['oks'] == ['yes'] * 4],
               'definite_disagreement_count': sum('no' in r['oks'] for r in records),
               'chart_decision_ids': [r['id'] for r in records if r['ask_user']],
               'delivery_hash_note': 'Delivery snapshot hashes. All dated/native charts match their source-refresh review hashes; expanded sources match the sealed source set and each row matches the completed raw close-pass digest. Hashes prove identity/coverage, not trading validity.'}
    (OUT / 'completion_check.json').write_text(json.dumps(summary, indent=2) + '\n')
    (OUT / 'delivery_manifest.json').write_text(json.dumps(delivery, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
