"""Reproducible document/coverage/preservation checks; no strategy execution.

Run with a Python environment containing PyMuPDF. Source review extents are
checked as recorded declarations, not independently inferred from rendered files.
This audit cannot prove semantic completeness, human viewing, or trading edge.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
import sys
import zipfile
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'review/document_qa.json'
errors = []
counts = Counter()
checks = []


def require(ok, kind, detail):
    counts['assertions'] += 1
    if not ok:
        errors.append({'kind': kind, 'detail': str(detail)})


def read_json(path):
    return json.loads(path.read_text())


def file_lines(path):
    key = str(path.resolve())
    if key not in line_cache:
        line_cache[key] = path.read_text().splitlines()
    return line_cache[key]


line_cache = {}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def extent(ranges, n):
    covered = set()
    for a, b in ranges:
        if a > b or a < 1 or b > n:
            return False
        covered.update(range(a, b + 1))
    return covered == set(range(1, n + 1))


required = '''README.md SOURCE_REVIEW_LEDGER.md SOURCE_FINDINGS_AND_CONFLICTS.md
REQUIREMENTS_TRACEABILITY.md DATA_CAPABILITY_AUDIT.md IMPLEMENTATION_PLAN.md
VALIDATION_PLAN.md IMPLEMENTATION_BACKLOG.md OPEN_QUESTIONS_AND_RISKS.md
SECOND_DESIGN_REVIEW.md ACCOUNT_CONSTRAINTS.md EXTERNAL_RESEARCH.md
components/COMMON_CONTRACTS.md components/COMPUTATION_SCHEDULE.md
traceability/SOURCE_TO_DESIGN.md traceability/EXTERNAL_TO_DESIGN.md
THIRD_DESIGN_REVIEW.md SPECIALIST_EXPERIMENT_PROGRAM.md MODEL_QUALITY_AND_STOPPING_RULES.md
VOLATILITY_RESEARCH_SPEC.md E0_REFERENCE_EXPERIMENT.md CONVERSATION_RECHECK.md
THIRD_REVIEW_RESEARCH.md components/RUNTIME_SCHEDULER.md experiments/README.md
MARKET_DATA_SOURCE_CONTRACT.md IMPLEMENTATION_HANDOFF.md IMPLEMENTATION_SCOPE.md
SYSTEM_REFINEMENT.md UPGRADE_PATHS.md UPGRADE_CONSTRUCTIONS.md'''.split()
for rel in required:
    p = ROOT / rel
    require(p.is_file() and p.stat().st_size > 0, 'required_file', rel)
counts['required_documents'] = len(required)
checks.append('Required planning documents exist and are nonempty.')

expected = {'F': 12, 'M': 13, 'C': 24, 'O': 23, 'X': 10,
            'L': 19, 'G': 10, 'P': 12, 'R': 22, 'V': 8}
cards = {}
for p in sorted((ROOT / 'components').glob('*.md')):
    text = p.read_text()
    matches = list(re.finditer(r'^## ([FCMOLXGPRV]\d{2}) — (.+)$', text, re.M))
    for i, m in enumerate(matches):
        cid = m[1]
        require(cid not in cards, 'duplicate_component', cid)
        body = text[m.end():matches[i + 1].start() if i + 1 < len(matches) else len(text)]
        fields = list(re.finditer(r'^(\d+)\. \*\*(.+?)\*\*\s*(.*)', body, re.M))
        require([int(f[1]) for f in fields] == list(range(1, 11)), 'ten_fields', cid)
        for j, f in enumerate(fields):
            field_text = body[f.end():fields[j + 1].start() if j + 1 < len(fields) else len(body)]
            require(bool((f[3] + field_text).strip()), 'empty_field', f'{cid}/{f[1]}')
        cards[cid] = {'path': str(p), 'line': text[:m.start()].count('\n') + 1, 'title': m[2]}
require(Counter(x[0] for x in cards) == Counter(expected), 'component_counts', dict(Counter(x[0] for x in cards)))
for family, n in expected.items():
    require({c for c in cards if c.startswith(family)} == {f'{family}{i:02}' for i in range(1, n + 1)}, 'component_sequence', family)
require(read_json(ROOT / 'review/component_registry.json') == cards, 'registry_staleness', 'component_registry.json')
counts['component_cards'] = len(cards)
counts['component_numbered_fields'] = len(cards) * 10
checks.append('All 153 component IDs, family sequences, ten nonempty numbered fields and registry locations reconcile.')

src_text = (ROOT / 'SOURCE_FINDINGS_AND_CONFLICTS.md').read_text()
source_ids = re.findall(r'^\| ([A-Z][A-Z0-9]*(?:-[A-Z]*\d+)+)', src_text, re.M)
routes = read_json(ROOT / 'review/source_design_routing.json')
require(len(source_ids) == len(set(source_ids)) == len(routes) == 712, 'source_count', [len(source_ids), len(routes)])
require(set(source_ids) == {r['id'] for r in routes}, 'source_route_coverage', '712 exact IDs')
source_lines = src_text.splitlines()
matrix = (ROOT / 'traceability/SOURCE_TO_DESIGN.md').read_text()
matrix_ids = re.findall(r'^\| \[([^\]]+)\]', matrix, re.M)
require(Counter(matrix_ids) == Counter(source_ids), 'source_matrix_coverage', 'No missing or duplicate rows')
used = set()
for r in routes:
    n = r['source_line']
    require(0 < n <= len(source_lines) and re.match(r'^\| ' + re.escape(r['id']) + r'(?:\s|\|)', source_lines[n-1]) is not None,
            'source_line_target', r['id'])
    require(bool(r['components']) and all(c in cards for c in r['components']), 'source_component', r['id'])
    require(bool(r['rationale'].strip()) and r['fixture'] == 'T-SRC-' + r['id'], 'source_disposition_case', r['id'])
    used.update(r['components'])
counts['source_findings'] = len(routes)
conversation_prefixes = ('DTM-', 'JCV-', 'CEX-', 'CRL-', 'DRF-')
counts['conversation_table_findings'] = sum(s.startswith(conversation_prefixes) for s in source_ids)
require(counts['conversation_table_findings'] == 122, 'conversation_findings', counts['conversation_table_findings'])

ext_text = (ROOT / 'EXTERNAL_RESEARCH.md').read_text()
ext_ids = re.findall(r'^### (EXT-\d+) —', ext_text, re.M) + re.findall(r'^\| ((?:EXT|TECH)-\d+) \|', ext_text, re.M)
ext_routes = read_json(ROOT / 'review/external_design_routing.json')
require(len(ext_ids) == len(set(ext_ids)) == len(ext_routes) == 114, 'external_count', len(ext_ids))
require(set(ext_ids) == {r['id'] for r in ext_routes}, 'external_route_coverage', '114 exact IDs')
ext_matrix = (ROOT / 'traceability/EXTERNAL_TO_DESIGN.md').read_text()
require(Counter(re.findall(r'^\| \[([^\]]+)\]', ext_matrix, re.M)) == Counter(ext_ids), 'external_matrix_coverage', '114 rows')
ext_lines = ext_text.splitlines()
for r in ext_routes:
    n = r['line']
    require(0 < n <= len(ext_lines) and r['id'] in ext_lines[n-1], 'external_line_target', r['id'])
    require(bool(r['components']) and all(c in cards for c in r['components']), 'external_component', r['id'])
    used.update(r['components'])
counts['external_findings'] = len(ext_routes)
requirements = (ROOT / 'REQUIREMENTS_TRACEABILITY.md').read_text()
for prefix, n, pattern in [('U', 46, r'^\| (U\d{2})\b'), ('DTM-U', 5, r'^\| (DTM-U\d+)\b'), ('USR-', 17, r'^\| (USR-\d+-\d+)\b')]:
    found = re.findall(pattern, requirements, re.M)
    require(len(found) == len(set(found)) == n, 'requirement_count', [prefix, len(found), found])
    counts[{'U': 'prompt_requirements', 'DTM-U': 'dtm_user_requirements', 'USR-': 'active_clarifications'}[prefix]] = len(found)
require(set(cards) <= used, 'orphan_components', sorted(set(cards) - used))
checks.append('All source, external, conversation and user-requirement IDs have distinct matrix rows; component destinations and source line targets exist; no orphan cards.')

# Parse balanced Markdown link destinations, including spaces, parentheses and
# angle-bracket wrapped paths. Do not interpret code examples as real links.
def markdown_links(text):
    text = re.sub(r'^(```|~~~).*?^\1\s*$', '', text, flags=re.M | re.S)
    pattern = re.compile(r'\[([^\]\n]+)\]\(')
    for m in pattern.finditer(text):
        pos = m.end()
        depth = 1
        angle = False
        escaped = False
        j = pos
        while j < len(text):
            ch = text[j]
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '<':
                angle = True
            elif ch == '>':
                angle = False
            elif not angle and ch == '(':
                depth += 1
            elif not angle and ch == ')':
                depth -= 1
                if depth == 0:
                    yield m[1], text[pos:j].strip(), text[:m.start()].count('\n') + 1
                    break
            j += 1


docs = sorted(ROOT.glob('*.md')) + sorted((ROOT/'components').glob('*.md')) + sorted((ROOT/'traceability').glob('*.md')) + sorted((ROOT/'experiments').glob('*.md')) + sorted((ROOT/'review/third-review').glob('*.md'))
for p in docs:
    text = p.read_text()
    for label, target, n in markdown_links(text):
        if target.startswith(('http:', 'https:', 'mailto:', '#', 'app:')):
            counts['external_or_anchor_links'] += 1
            continue
        target = target.removeprefix('<').removesuffix('>')
        target = unquote(target.split('#', 1)[0])
        line_match = re.search(r':(\d+)$', target)
        line_no = int(line_match[1]) if line_match else None
        if line_match:
            target = target[:line_match.start()]
        q = Path(target)
        q = q if q.is_absolute() else p.parent/q
        counts['local_links'] += 1
        exists = q.is_file() or q.is_dir() or q.resolve() == REPORT
        require(exists, 'broken_local_link', f'{p.relative_to(ROOT)}:{n} -> {target}')
        if line_no is not None and q.is_file():
            lines = file_lines(q)
            require(1 <= line_no <= len(lines), 'invalid_line_number', f'{target}:{line_no}')
            if label in cards:
                require(str(q.resolve()) == cards[label]['path'] and line_no == cards[label]['line'], 'component_link_target', f'{label} -> {target}:{line_no}')
    # Every delivered Markdown table must have a consistent unescaped-pipe
    # column count. Literal pipes inside code cells also need GFM escaping.
    current_cols = None
    fenced = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith(('```', '~~~')):
            fenced = not fenced
        if fenced or not line.startswith('|'):
            current_cols = None
            continue
        cols = len(re.split(r'(?<!\\)\|', line)) - 2
        if current_cols is None:
            current_cols = cols
        require(cols == current_cols, 'table_columns', f'{p.relative_to(ROOT)}:{n}: expected {current_cols}, got {cols}')
        counts['markdown_table_rows'] += 1
counts['checked_markdown_documents'] = len(docs)
checks.append('All delivered Markdown local links, explicit line references, component links and table column counts checked. Remote URLs are not refetched by this audit.')

inventory = read_json(ROOT/'review/source_inventory.json')
source_root = Path('/workspace/sources/documents')
actual_paths = {str(p) for p in source_root.rglob('*') if p.is_file()}
require(actual_paths == {r['path'] for r in inventory}, 'source_inventory_paths', sorted(actual_paths ^ {r['path'] for r in inventory}))
require(len(inventory) == 52, 'source_file_count', len(inventory))
manifest = read_json(source_root/'SOURCE_MANIFEST.json')
inv_by_rel = {r['relative_path']: r for r in inventory}
require(len(manifest) == 50 and {r['path'] for r in manifest} == set(inv_by_rel) - {'README.md', 'SOURCE_MANIFEST.json'}, 'current_manifest_paths', len(manifest))
for entry in manifest:
    r = inv_by_rel[entry['path']]
    require(entry['bytes'] == r['bytes'] and entry['sha256'] == r['sha256'], 'current_manifest_entry', entry['path'])
counts['current_manifest_entries'] = len(manifest)
control = inv_by_rel['SOURCE_MANIFEST.json']
for version in control.get('previous_versions', []):
    p = Path(version['path'])
    require(p.is_file() and p.stat().st_size == version['bytes'] and sha(p) == version['sha256'], 'previous_manifest_hash', p)
    previous = read_json(p)
    require(manifest[:len(previous)] == previous and len(manifest) - len(previous) == 1 and manifest[-1]['path'] == 'conversations/Design robust feature levels.md', 'manifest_single_addition', p)
    counts['previous_manifest_versions_verified'] += 1
import pymupdf
for r in inventory:
    p = Path(r['path'])
    if not p.is_file():
        continue
    require(p.stat().st_size == r['bytes'] and sha(p) == r['sha256'], 'source_preservation', p)
    counts['source_hashes_verified'] += 1
    if 'pages' in r:
        with pymupdf.open(p) as pdf:
            n = len(pdf)
        require(n == r['pages'], 'pdf_page_count', p)
        require(extent(r['text_reviewed'], n) and extent(r['visual_reviewed'], n), 'pdf_declared_review_extents', p)
        counts['pdf_files'] += 1
        counts['pdf_pages_text_and_visual_declared'] += n
    elif r.get('lines') is not None:
        n = len(p.read_text().splitlines())
        require(n == r['lines'] and extent(r['text_reviewed'], n), 'text_declared_review_extents', p)
        if p.parent.name == 'conversations' or p.name == 'JJumbo_Conversation_Export.md':
            counts['conversations'] += 1
            counts['conversation_lines'] += n
        if p.parent.name == 'indicators':
            counts['standalone_indicator_files'] += 1
            counts['standalone_indicator_lines'] += n
    elif p.suffix.lower() == '.webp':
        require(extent(r['visual_reviewed'], 1), 'standalone_image_declared_review', p)
        counts['standalone_images'] += 1
require(counts['pdf_files'] == 39 and counts['pdf_pages_text_and_visual_declared'] == 580, 'pdf_totals', dict(counts))
require(counts['conversations'] == 5 and counts['conversation_lines'] == 6256, 'conversation_totals', [counts['conversations'], counts['conversation_lines']])
require(counts['standalone_indicator_files'] == 2 and counts['standalone_indicator_lines'] == 2009, 'indicator_totals', counts['standalone_indicator_lines'])
zi = read_json(ROOT/'review/zip_inventory.json')
zpath = source_root/'indicators/Pinescript-indicators--main.zip'
with zipfile.ZipFile(zpath) as z:
    actual_members = {i.filename for i in z.infolist() if not i.is_dir()}
    require(actual_members == {r['member'] for r in zi} and len(zi) == 83, 'zip_members', len(zi))
    for r in zi:
        p = Path(r['path'])
        data = z.read(r['member'])
        require(len(data) == r['bytes'] and hashlib.sha256(data).hexdigest() == r['sha256'], 'zip_archive_hash', r['member'])
        require(p.is_file() and p.stat().st_size == r['bytes'] and sha(p) == r['sha256'], 'zip_extraction_hash', r['member'])
        n = len(data.decode('utf-8-sig').splitlines())
        require(n == r['lines'] and extent(r['text_reviewed'], n), 'zip_declared_review_extents', r['member'])
        counts['zip_text_source_members'] += 1
        counts['zip_source_lines'] += n
require(counts['zip_source_lines'] == 51659, 'zip_lines_total', counts['zip_source_lines'])
checks.append('Supplied file paths, sizes and SHA-256 hashes, PDF page counts, text line totals, ZIP/archive/extraction hashes and all recorded review extents reconcile. Extent declarations do not independently prove viewing.')

pages = read_json(ROOT/'review/external/skylit/inventory.json')['pages']
images = read_json(ROOT/'review/external/skylit/images.json')
for r in pages:
    p = Path(r['path'])
    require(p.is_file() and p.stat().st_size == r['bytes'] and sha(p) == r['sha256'], 'external_capture_hash', r['id'])
    require(r['status'] == 200, 'external_capture_status', r['id'])
    if r['text_reviewed']:
        require(extent(r['text_reviewed'], r['readable_lines']), 'external_full_read_extent', r['id'])
        counts['external_full_text_pages'] += 1
    else:
        require(r.get('semantic_reviewed') is True and 'Focused' in r.get('review_method', ''), 'external_semantic_scope', r['id'])
        counts['external_focused_api_pages'] += 1
for r in images:
    p = Path(r['path'])
    require(p.is_file() and p.stat().st_size == r['bytes'] and sha(p) == r['sha256'], 'external_image_hash', r['id'])
    require(r.get('viewed') is True and bool(r.get('visual_review')), 'external_image_declared_review', r['id'])
counts['external_images_declared_viewed'] = len(images)
require(len(pages) == 96 and counts['external_full_text_pages'] == 41 and counts['external_focused_api_pages'] == 55 and len(images) == 87,
        'external_review_totals', [len(pages), counts['external_full_text_pages'], counts['external_focused_api_pages'], len(images)])
checks.append('All 96 cached documentation pages and 87 images retain capture hashes; full-text versus focused API review scope is kept distinct.')

recon = read_json(ROOT/'review/data-audit/reconciliation.json')
require(recon['inventoried_files'] == recon['actual_dataset_files'] == 80198 and recon['expected_bytes'] == recon['actual_bytes'] == 322136177617,
        'prior_data_reconciliation_totals', recon['actual_dataset_files'])
require(not recon['missing'] and not recon['extra'] and not recon['size_mismatch'], 'prior_data_reconciliation_diffs', 'previous bounded audit artifact')
counts['previously_reconciled_market_files'] = recon['actual_dataset_files']
counts['previously_reconciled_market_bytes'] = recon['actual_bytes']
checks.append('Previously completed market path/size reconciliation artifact totals checked; this document audit does not rescan market rows or certify their quality.')

report = {
    'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    'status': 'PASS' if not errors else 'FAIL',
    'scope': 'Document structure, coverage, captured review declarations and source preservation only; no trading-system tests executed.',
    'counts': dict(counts),
    'component_family_counts': dict(Counter(x[0] for x in cards)),
    'checks': checks,
    'errors': errors,
    'limitations': [
        'Structural completeness cannot prove every semantic clause is correctly specified; SECOND_DESIGN_REVIEW records the separate substantive review.',
        'Recorded textual/visual review extents are checked for coverage, not inferred as human viewing from file existence.',
        'Remote URLs are not revalidated by this local audit; their capture dates and availability are in the research registers.',
        'Future T-* fixtures, model fitting, market backtests, account simulations and profitability have not been executed by this audit.'
    ],
}
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'status': report['status'], 'counts': dict(counts), 'errors': errors}, indent=2, ensure_ascii=False))
sys.exit(bool(errors))
