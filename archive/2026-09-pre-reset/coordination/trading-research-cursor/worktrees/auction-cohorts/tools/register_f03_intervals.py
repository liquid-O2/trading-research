"""Retain completed source inspection and freeze the bounded F03 batch."""

from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from trading_research.operations.artifacts import code_snapshot, file_digest
from trading_research.operations.trials import TrialRegistry

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT.parent / 'planning/trading-model'


def main():
    registry = TrialRegistry(ROOT / 'evidence/trials')
    original = json.loads(Path('/tmp/f03-original-reading.json').read_text())
    supplemental = json.loads(Path('/tmp/f03-supplemental-reading.json').read_text())
    pages = json.loads(Path('/tmp/f03-original-pages/manifest.json').read_text())
    routes = {v['id']: v for v in json.loads((PLAN / 'review/source_design_routing.json').read_text())}
    by_path = {}
    for row in original['sources'] + supplemental['sources']:
        entry = by_path.setdefault(row['path'], {'sha256': row['sha256'], 'lines': set(), 'clauses': set()})
        assert entry['sha256'] == row['sha256']
        entry['lines'].update(row['lines'])
        entry['clauses'].update(row.get('clauses', []))
    osf = next(k for k in by_path if k.endswith('Open Source Fractal - Customized.txt'))
    by_path[osf]['lines'].update(range(386, 452))
    source_records = []
    for path, row in by_path.items():
        raw = Path(path).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row['sha256']
        lines = raw.decode('utf-8-sig').splitlines()
        excerpt = [{'line': n, 'text': lines[n - 1]} for n in sorted(row['lines'])]
        ref = registry.artifacts.put_json({'original_path': path, 'original_sha256': row['sha256'], 'lines': excerpt}, kind='static_original_source_excerpt')
        source_records.append({'path': path, 'sha256': row['sha256'], 'lines_read': sorted(row['lines']),
                               'source_ids': sorted(row['clauses']), 'excerpt': asdict(ref), 'executed': False})
    pdf_records = []
    checked = set()
    for row in pages['pages']:
        if row['original_path'] not in checked:
            assert file_digest(Path(row['original_path'])) == row['original_sha256']
            checked.add(row['original_path'])
        raw_text = Path(row['text_path']).read_bytes()
        assert hashlib.sha256(raw_text).hexdigest() == row['text_sha256']
        text_ref = registry.artifacts.put_bytes(raw_text, kind='original_pdf_page_text')
        pixels_ref = registry.artifacts.put_bytes(Path(row['image_path']).read_bytes(), kind='inspected_original_pdf_page')
        pdf_records.append({k: row[k] for k in ('prefix', 'original_path', 'original_sha256', 'page')} |
                           {'text': asdict(text_ref), 'render': asdict(pixels_ref), 'text_read': True, 'visually_inspected': True})
    inventory = json.loads((PLAN / 'review/source_inventory.json').read_text())
    conversation = next(v for v in inventory if v['finding_ids'].startswith('CEX-01'))
    image = next(v for v in inventory if v['finding_ids'].startswith('IMG-01'))
    for row in (conversation, image):
        assert file_digest(Path(row['path'])) == row['sha256']
    lines = Path(conversation['path']).read_text().splitlines()
    cex = registry.artifacts.put_json({'original_sha256': conversation['sha256'], 'lines': [
        {'line': n, 'text': lines[n - 1]} for n in range(1155, 1200)]}, kind='original_conversation_excerpt')
    img = registry.artifacts.put_bytes(Path(image['path']).read_bytes(), kind='inspected_original_reference_image')
    # Each group retains distinct literal variants; this is not a claim that
    # one generic assertion reproduces every source indicator.
    groups = [
        ('F03-01', 'Immutable typed calendar facts and known-time revisions', 'CEX-26'),
        ('F03-02', 'NY wall versus fixed offsets and explicit DST folds', 'JSS-04 JTR-03 MAV-11 PIN018-02 PIN021-02 PIN025-01'),
        ('F03-03', 'Declared Sunday/overnight trading date; complete midnight interval', 'JSS-04 OSF-01 PIN001-01 PIN032-02 PIN066-03 PIN078-01'),
        ('F03-04', 'Named half-open intersections retain overlap and inactive gaps', 'PIN075-01 PIN057-01 PIN083-01'),
        ('F03-05', 'Weekly/monthly actual date union retains holidays and half-days', 'CEX-26 VW10-05 PIN045-05 PIN066-03 PIN077-02 PIN078-01'),
        ('F03-06', 'Earliest venue/firm/platform boundary minus explicit margin', 'CEX-26 JXA-21'),
        ('F03-07', 'Independent timer, no market tick, stable reset owner', 'JSS-04 PIN007-05 PIN012-04 PIN013-03 PIN024-02 PIN040-02 PIN068-03 PIN081-04'),
        ('F03-08', 'Restart before and after atomic internal state commit', 'PIN061-01 PIN066-03 PIN068-03 PIN070-01 PIN077-02'),
        ('F03-09', 'Future boundary revision supersedes unfired timer', 'CEX-26'),
        ('F03-10', 'Past revision reconciles at known cut; never repeats a committed reset', 'CEX-26 PIN068-03'),
        ('F03-11', 'Missing opening/closing print does not move a clock or supply a price', 'PIN012-02 PIN025-01 PIN040-02 PIN074-02 PIN076-02 PIN081-04'),
        ('F03-12', '09:00 versus 09:30 and completed 5-minute opening range', 'JTR-03 JXA-05 TP3-01 PIN003-01 PIN057-01 PIN059-01 PIN083-01'),
        ('F03-13', 'Literal exchange clocks remain separate from NY-labelled clocks', 'PIN006-01 PIN013-03 PIN015-01 PIN015-02 PIN016-04 PIN024-02 PIN028-01 PIN043-01 PIN046-01 PIN047-01 PIN064-01 PIN071-05'),
        ('F03-14', 'Distinct Asia 18/19/20 starts, London and NY formations', 'PIN039-01 PIN041-01 PIN041-02 PIN049-01 PIN061-01 PIN064-01 PIN080-01 PIN082-01'),
        ('F03-15', 'Three-hour 14–17 block and actual elapsed time, not bar counts', 'PIN001-01 PIN002-02 PIN032-02 PIN040-02 PIN054-01 PIN055-02 PIN081-04'),
        ('F03-16', 'Separate formation, confirmation, publication and reset', 'AM1-04 MAT-07 PIN003-01 PIN014-02 PIN041-03 PIN047-02 PIN059-01 PIN065-01 PIN068-01 PIN068-02 PIN070-01'),
        ('F03-17', 'Irregular DTT windows and inner minute markers; missing import stays open', 'PIN012-02 PIN012-03 PIN012-04'),
        ('F03-18', 'Seven magic-hour one-hour formations with three-hour analysis', 'PIN081-01 PIN081-04'),
        ('F03-19', 'Price-triggered anchor and bar-index expiry need price/bar dependencies', 'VW10-05 PIN051-02 PIN069-01'),
        ('F03-20', 'Display clocks and filenames are not historical availability', 'IMG-01 TBR-07 OBT-03 OSF-01 PIN007-05 PIN021-02 PIN076-02'),
        ('F03-21', 'No direction, global session ban or private formula inferred from narrative', 'JTR-09 JXA-05 JXA-21 JFN-04 JFN-10 AM1-04 MAT-07 TBR-07 OBT-03'),
        ('F03-22', 'Source UI examples and alternative clock choices remain explicit', 'JSS-02 JSS-04 MAV-11 PIN055-02 PIN057-01 PIN065-01 PIN069-01 PIN074-02 PIN076-02 PIN083-01'),
        ('F03-23', 'Literal versus compiled queries on frozen clocks and endpoints', 'JTR-03 TP3-01 PIN001-01 PIN054-01 PIN075-01 PIN081-01'),
        ('F03-24', 'No empirical statistics or all-consumer admission from synthetic clock parity', 'PIN039-01 PIN041-01 PIN041-02 PIN043-01 PIN046-01 PIN047-02 PIN054-01 PIN080-01 PIN082-01 PIN082-03'),
    ]
    mapped = {s for _, _, ids in groups for s in ids.split()}
    assert set(original['source_ids']) == mapped
    cases = [{'id': key, 'expected': description, 'source_ids': ids.split(), 'whole_case_verified': False,
              'batch_scope': 'reference infrastructure only; source-specific indicator replay remains separate'}
             for key, description, ids in groups]
    findings = [{**routes[key], 'batch_cases': [c['id'] for c in cases if key in c['source_ids']],
                 'original_assigned_passages_reviewed': True, 'full_indicator_implementation_claimed': False}
                for key in original['source_ids']]
    report = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'scope': 'F03/F03.SESSION_CASES opening source/case review',
              'source_findings': findings, 'cases': cases, 'static_original_sources': source_records,
              'pdf_pages': pdf_records, 'renderer': pages['renderer'],
              'conversation': {'path': conversation['path'], 'sha256': conversation['sha256'], 'lines_read': [1155, 1199], 'excerpt': asdict(cex)},
              'image': {'path': image['path'], 'sha256': image['sha256'], 'visually_inspected': True, 'artifact': asdict(img)},
              'source_code_executed': False, 'market_tape_reads': 0, 'economic_runs': 0,
              'whole_definition_or_phase_closure': False,
              'unresolved': ['Utilities/10 and SetSessionTimes imported implementation absent.',
                             'Actual historical venue/firm/platform cutoffs require dated admission.',
                             'Private range formulas and London formation start are not reconstructed.',
                             'All source indicator variants, fair-cost comparisons and C/L/R/P P5 integration remain open.',
                             'Cash calendar context and supplied continuous NQ series do not certify the complete E0 parent universe.']}
    review = registry.artifacts.put_json(report, kind='original_source_case_review')
    (ROOT / 'reports/f03-source-cases.json').write_text(json.dumps({'artifact': asdict(review), **report}, indent=2) + '\n')
    prose = '''# F03 source clocks and reference cases

The assigned original passages were reviewed before this batch: 74 finding
rows, 47 static source files, 41 original PDF pages with both text and visual
inspection, the original multi-panel image, and conversation lines 1155–1199.
Exact source hashes, inspected line/page sets, retained excerpts/renders and
every source-specific finding/fixture are in `reports/f03-source-cases.json`.
No Pine source was executed. Narrative examples and embedded percentage tables
are source claims, not observed predictive performance.

The graph preserves clock alternatives rather than selecting them from results.
New York wall time differs from fixed EST/GMT offsets; exchange-time `time()`
calls do not become NY because a label says so. Sunday belongs to its declared
trading date. The OSF twelve-hour addition is a display day-label adjustment,
not a trading-date rule. Weekly/monthly membership uses supplied dated sessions.
The 14–17 final '4H' block lasts three hours. All twelve irregular time-based
windows retain their gaps. Asia 18/19/20 starts and NY 08/09/09:30 starts remain
separately named choices. The 23-hour magic formation ends at 00 and its analysis
ends at 03, not 04; the source countdown is one hour late.

No print means a missing price observation, not a moved boundary. Completed
H/L/C cannot be published at formation start. A display toggle, `timenow`,
array position, shifted UTC date or elapsed bar count cannot establish a reset.
Midnight double resets and transition-driven commits require one stable owner.
The generic timer journal commits internal state only; order-side uncertainty
and complete reactor/consumer integration remain separate work.

JFN is assistant synthesis. Its global session bans, IB dismissal and private
range formulas are not adopted. JTR's failed 09:40–50 turn is not a fixed
directional clock rule. London formation start remains unresolved. PDF/image
screen clocks and filenames are not observed exchange or strategy receipts.
The supplied cash calendar remains cash context; official futures and account
cutoffs require their own dated sources. Source imports and indicator statistics
are not supplied by this reference implementation.

All cases below are preregistered expectations; none closes the whole source
case or unit. Named test evidence will be attached after the single batch review
and consolidated repair pass.

| Case | Expected behavior | Assigned clauses |
|---|---|---|
'''
    prose += ''.join(f"| {c['id']} | {c['expected']} | {', '.join(c['source_ids'])} |\n" for c in cases)
    (ROOT / 'validation/F03_SOURCE_CASES.md').write_text(prose)
    protocol = registry.artifacts.put_bytes((ROOT / 'validation/F03_INTERVAL_PROTOCOL.md').read_bytes(), kind='engineering_protocol')
    golden = registry.artifacts.put_bytes((ROOT / 'tests/golden/f03-intervals.json').read_bytes(), kind='independent_golden_reference')
    baseline = code_snapshot(ROOT, registry.artifacts)
    registration = {'protocol': asdict(protocol), 'golden': asdict(golden), 'source_cases': asdict(review),
                    'baseline': asdict(baseline), 'maximum_cpu_per_attempt': 180, 'hard_cpu_seconds': 190,
                    'address_space_bytes': 4 * 1024 ** 3, 'wall_seconds': 240,
                    'market_tape_reads': 0, 'model_fits': 0, 'economic_runs': 0}
    registry.register_family('F03-interval-timer-reference-v1', scope_ids=('F03', 'F03.SESSION_CASES', 'B00.1'),
                             protocol=registration, max_attempts=3, cpu_budget_seconds=600)
    (ROOT / 'reports/f03-interval-registration.json').write_text(json.dumps(registration, indent=2) + '\n')
    print(json.dumps({'registration': registration, 'assigned_findings': len(findings), 'static_files': len(source_records),
                      'pdf_pages': len(pdf_records), 'cases': len(cases)}, indent=2))


if __name__ == '__main__':
    main()
