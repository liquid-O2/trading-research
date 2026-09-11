"""Assemble the manually reviewed Phase 1 audit; never infer audit verdicts."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'implementation/reports/phase1-live/chart-audit'
REFRESH = OUT / 'source-recheck-2026-09-11'
DEST = ROOT / 'planning/phase-1-live/CHART_AUDIT.md'
FAMILIES = {'J':'Jumbo','G':'Greenbird','A':'Auction / VP / TPO','F':'Discretionary order flow',
            'R':'Native options / regime','S':'Sires','P':'Pine'}
ALIASES = {'TBR':'Time-Based ranges Framework (JJumbo)','XF':'xfcmg2','FIND':'jjumbo-findings','SS':'SessionStat+',
           'AMT1':'amt-lesson-1','VP2':'vp-lesson-2','TPO3':'tpo-lesson-3','MAMT':'mastering-amt-vp',
           'MATH':'the-math-behind-auction-market-theory','LIVE':'amt-on-live-markets',
           'RTVP':'reading-the-volume-profile','ABS':'your-mistakes-with-absorption',
           'C3':'code-3-orderflow','WIC':'whos-in-control','TRAP':'trapped-buyers-one-retest',
           'VWAP':'vwap-lesson-10','FP8':'fp-lesson-8','FP9':'fp-lesson-9',
           'DOM5':'dom-lesson-5','DOM6':'dom-lesson-6','DOM7':'dom-lesson-7',
           'STOP':'stop-re-entering','RD':'reading-delta','K18':'18k-payout-session',
           'BIG':'only-trade-big-trades','OFM':'origin-of-the-move','REF':'refill-effect',
           'CONT':'a-clean-continuation-short','GEX':'gex-framework','VIX4':'vix-lesson-4',
           'C1':'code-1-thesis','C2':'code-2-risk','K10':'10k-first-month',
           'NYAM':'ny-am-session','K2345':'2345-funded-session','LOSS':'anatomy-of-a-losing-start',
           'ANAT':'anatomy-of-a-losing-start','AVG':'average-unprofitable-trader'}

def link(label,path):
    p = Path(path)
    if not p.is_absolute():p=ROOT/p
    return f'[{label}](<{p}>)'

def esc(s):return str(s).replace('|','\\|').replace('\n',' ')

@lru_cache(maxsize=None)
def target_link(target):
    filename, _, symbol = target.partition('::')
    if filename.endswith('.md'):
        path = ROOT / 'planning/phase-1-live' / filename
        lines = path.read_text().splitlines()
        if symbol:
            ident = symbol.split()[0]
            candidates = [i for i,s in enumerate(lines,1) if re.search(r'\b'+re.escape(ident)+r'\b',s)]
            if not candidates:raise ValueError('Missing document target '+target)
            # RULES uses bold per-ID entries; prefer the actual recipe over its
            # earlier appearance in a family inventory or cross-reference.
            anchored = [i for i in candidates if re.match(
                r'^(?:#{1,6}\s+|\*\*)'+re.escape(ident)+r'\b', lines[i-1])]
            line = anchored[0] if anchored else next(
                (i for i in candidates if lines[i-1].startswith('#')), candidates[0])
        else:line=1
    else:
        paths = list((ROOT / 'implementation/src').rglob(filename))
        if len(paths)!=1:raise ValueError('Non-unique code target '+target)
        path=paths[0];line=1
        if symbol:
            definitions={}
            def visit(node,prefix=''):
                for child in ast.iter_child_nodes(node):
                    if isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                        name=prefix+child.name;definitions[name]=child.lineno
                        visit(child,name+'.')
                    else:
                        if isinstance(child,(ast.Assign,ast.AnnAssign)):
                            targets=child.targets if isinstance(child,ast.Assign) else [child.target]
                            for item in targets:
                                for binding in ast.walk(item):
                                    if isinstance(binding,ast.Name):definitions[prefix+binding.id]=child.lineno
                        visit(child,prefix)
            visit(ast.parse(path.read_text()))
            if symbol not in definitions:raise ValueError('Missing code symbol '+target)
            line=definitions[symbol]
    return link(target,str(path)+':'+str(line))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--draft',action='store_true');args=ap.parse_args()
    ids=json.loads((OUT/'source_manifest.json').read_text())['recipe_ids']
    records={}
    for p in sorted(OUT.glob('audit_records_*.json')):
        for r in json.loads(p.read_text()):
            if r['id'] in records:raise ValueError('Duplicate audit record '+r['id'])
            records[r['id']]=r
    if not args.draft and set(records)!=set(ids):raise ValueError(f'Missing audit IDs: {set(ids)-set(records)}')
    source_coverage=json.loads((REFRESH/'source_coverage.json').read_text())
    source_digest=source_coverage['source_set_sha256']
    new_figures=json.loads((REFRESH/'new_figure_review.json').read_text())
    detail_path=REFRESH/'raw_detail_pass_2026-09-11.json'
    detail=json.loads(detail_path.read_text())
    detail_digest=hashlib.sha256(detail_path.read_bytes()).hexdigest()
    refreshed=[r for r in records.values() if r.get('source_refresh',{}).get('source_set_sha256')==source_digest
               and r.get('source_refresh',{}).get('close_pass_sha256')==detail_digest
               and r.get('source_refresh',{}).get('rechecked')]
    if not args.draft and len(refreshed)!=105:
        raise ValueError(f'Source-set redo after completed close pass incomplete: {len(refreshed)}/105')
    detail_pages=[p for d in detail['pdfs'] for p in d['pages']]
    detail_done=[p for p in detail_pages if p.get('detail_pass_complete')]
    if not args.draft and len(detail_done)!=len(detail_pages):
        raise ValueError(f'Additional raw-source close inspection incomplete: {len(detail_done)}/{len(detail_pages)} pages')
    oks={'yes','no','blocked','cannot-tell','gap'}
    for r in records.values():
        if set(r['oks'])-oks or len(r['oks'])!=4:raise ValueError(r['id'])
        if not r['fix'] or not r['acceptance']:raise ValueError('Missing repair specification '+r['id'])
    figs=json.loads((OUT/'figure_crop_manifest.json').read_text())
    vectors=json.loads((OUT/'vector_review_manifest.json').read_text())
    scores={r['id']:r for r in json.loads((OUT/'score_snapshot.json').read_text())}
    plots=[]
    for fn in ('plot_results.json','source_date_plot_results.json','extra_plot_results.json','clock_plot_results.json'):
        p=OUT/fn
        if p.exists():plots.extend(json.loads(p.read_text()))
    reviews={(r['id'],r['case'],r['date']):r for r in json.loads((OUT/'chart_review.json').read_text())}
    native=json.loads((OUT/'native_options_review.json').read_text()) if (OUT/'native_options_review.json').exists() else []
    if not args.draft:
        for p in plots:
            q=reviews.get((p['id'],p['case'],p['date']))
            if not q or not q.get('reviewed') or not q.get('source_should_fire') or not q.get('notes'):
                raise ValueError('Missing manual chart review '+str(p))
            if not (OUT/p['plot']).is_file():raise ValueError('Missing chart '+p['plot'])
    def source_links(r):
        result=[]
        for ref in r.get('sources',[]):
            if ':' not in ref:
                result.append(ref);continue
            alias,page=ref.rsplit(':',1)
            if not page.isdigit():result.append(ref);continue
            if alias.startswith('PINE '):
                p=OUT/'source-pine'/alias[5:]
                if not p.exists():raise ValueError('Missing Pine source '+str(p))
                result.append(link(alias+' L'+page,str(p)+':'+page));continue
            if alias=='GB':
                result.append(link('GB pack L'+page, str(ROOT/'planning/phase-1-fable/references/greenbirdtrader-trading-framework.md')+':'+page));continue
            if alias in ('JRAW','GBRAW'):
                stem='JJumboFX_Raw_X_Archive_v2' if alias=='JRAW' else 'greenbirdtrader-complete'
                number=int(page)
                result.append(link(f'{alias} p.{number} posts',REFRESH/'new-source-figures'/stem/f'p{number:03d}.png'))
                for f in new_figures:
                    if Path(f['pdf']).stem==stem and f['page']==number:
                        label=f'{alias} p.{number} fig.{f["image"]}'
                        if f.get('post_id'):label+=' post '+f['post_id']
                        else:label+=' (unmatched cached PDF figure)'
                        result.append(link(label,f['artifact']))
                continue
            if alias=='REFIMG':
                result.append(link('native SPX/SPY/QQQ reference',ROOT/'sources/documents/reference-images/zerano-charts-SPX-2026-08-24T18-51-29-251Z.webp'));continue
            stem=ALIASES.get(alias,alias);page=int(page)
            matched=[f for f in figs if any(Path(o['source']).stem==stem and o['page']==page for o in f['occurrences'])]
            vm=[v for v in vectors if Path(v['source']).stem==stem and v['page']==page]
            if matched or vm:
                result.extend(link(f'{alias} p.{page} fig.{i+1}',f['artifact_original']) for i,f in enumerate(matched))
                result.extend(link(f'{alias} p.{page} vector',OUT/v['artifact_original']) for v in vm)
            else:
                src=next((p['source'] for p in json.loads((OUT/'source_manifest.json').read_text())['pdfs'] if Path(p['source']).stem==stem),None)
                result.append(link(f'{alias} p.{page}',src) if src else ref)
        return '; '.join(result)
    selected=[records[k] for k in ids if k in records]
    text=['# Phase 1 chart audit','',
          (f'**Source-set re-audit in progress: {len(refreshed)}/105 Section B IDs revised.**' if args.draft else '**Audit complete for all 105 Section B IDs.**'),'',
          ('All source rereads and the additional close inspection of both new PDFs are complete. Implementation-chart and per-ID review is now being repeated against the completed close pass. Rows marked pending retain earlier provisional findings. Counts describe retained implementation measurements, not certified faithful results.' if args.draft else 'Every row and repair specification has been reassessed against the expanded source set and completed close pass. Raw posts and matched figures take precedence over archive write-ups. Existing implementation charts were retained where their geometry and input hashes were unchanged, then compared with the refreshed sources.'),'',
          f'Additional source detail pass: {len(detail_done)}/{len(detail_pages)} PDF pages; {sum(p["image_occurrences"] for p in detail_done)}/158 figures inspected in their post context with native pixels and close crops. '+link('page-by-page observations, limits and affected IDs',detail_path)+'.','',
          'This report audits the retained Phase 1 implementation against the supplied sources. It contains no Phase 2 work and makes no production recipe changes. Repair instructions at the bottom are specifications, not implemented fixes. Source conflicts stop faithful certification of the affected ID.','',
          'The four verdicts have different meanings: `source_ok` checks whether FORMULAS describes the source; `code_ok` checks construction and timing; `score_event_ok` checks the event and denominator; `chart_ok` checks the plotted implementation against the source geometry and sequence. `cannot-tell` preserves unpublished or ambiguous source details; `gap` and `blocked` preserve missing inputs. A retained positive is never treated as proof that the source recipe should fire.','',
          (f'Refreshed findings so far: {sum("no" in r["oks"] for r in refreshed)} of {len(refreshed)} reassessed IDs have at least one definite mismatch.' if args.draft else f'Audit outcome: {sum("no" in r["oks"] for r in selected)} IDs have at least one definite mismatch. All-four-yes IDs: {", ".join(r["id"] for r in selected if r["oks"]==["yes"]*4) or "none"}. Blocked and unavailable inputs remain explicit in their individual verdicts.'),'',
          'Implementation plots state their own time basis, normally America/New_York. Source charts have no assumed default timezone: posting timestamps, export timestamps, displayed axes, author session names and exchange clocks are separate evidence. An export stamp alone does not prove the axis timezone. Convert only from a supported source timezone/offset on that session date, account for daylight saving, and retain an unresolved clock mapping when evidence is insufficient. EST is a fixed UTC-5 offset; it is not a year-round synonym for New York time. Bar timestamps in the implementation plots are starts; a one-minute close is known one minute later. Native contracts, cash indices and ETFs retain their own price coordinates.','',
          'User clarification on September 11: Asia, London and other reference highs AND lows remain active only while unvisited. Apply that requirement independently to both sides. A first revisit consumes the reference and ends its active line; a later revisit is not a fresh target or sweep setup. Historical range geometry may remain visible as history, and the event begun on the first visit may still develop a subsequent confirmation, but neither restores an active unvisited reference. Source descriptions and older implementations that reuse visited levels must be identified separately from this requested behavior.','',
          'Source coverage: 41 PDFs / 711 pages reread; 330 original distinct figures and 18 vector pages re-viewed, preserving the earlier crop reviews; 158 figures in the added PDFs; 85 Pine/archive/supplement files (including the one-line README); 13 prose/reference/manifest files; the separate native-product reference image; two videos with review limits recorded. The supplied Pine archive has 83 files including README, not the 84 asserted in the wiki. The supplied hourly_stats_levels and magic_hours files end mid-statement, so their visible logic is not a complete executable source. '+link('source coverage and hashes',REFRESH/'source_coverage.json')+'.','',
          'The added Greenbird raw post figures supply visual evidence previously unavailable from the pack. Cached PDF figures without a matching post retain that limitation. Zip images are used only after a verified match to a PDF post; four unmatched Spain stills remain unused. Video observations preserve their sampling and audio-transcription limits. The archive gap list and older assistant proposals are secondary context, not author formulas. '+link('new figure reviews',REFRESH/'new_figure_review.json')+'; '+link('zip associations',REFRESH/'zip_caption_candidates.json')+'; '+link('video reviews',REFRESH/'video_review.json')+'.','',
          f'Dated evidence: {len(plots)} price/geometry charts plus {len(native)} native-product supplements, each manually inspected. Every ID has at least two dated charts. These distinguish source positives, named-default positives, prerequisite-only cases, negatives and unavailable source events. A further chronological scan of 642 eligible sessions with complete RTH bars found later A07/A08/A09 sequences, an A10 no-through-open positive and true P02/P06/P19 event negatives. It found no J03 positive under the specific existing extended/single-path and 15-minute EQ-hold conditions. Missing author definitions or unbuilt source inputs remain explicit limitations; the audit does not certify their proxy-positive charts. See '+link('additional sequence evidence',OUT/'additional_sequence_candidates.json')+'.','',
          'The source label distinction is material: `pRTHVAH/VAL` is prior RTH value, while `pdVAH/VAL` is prior full ETH value. Current/developing VP, prior price extremes, range EQ, range open and RTH open are separate objects. The dated January 2 Jumbo figure places the purple Range OP at displayed 09:00 near the range finish, distinct from the forming interval’s first print; its absolute axis mapping and later source configurations must be kept explicit. The June 8 shelf rectangle is a manual profile annotation; the 302-lot bubble is a print, and neither alone constitutes a computed absorption signal.','',
          'Evidence inventories: '+ '; '.join(link(n,OUT/f) for n,f in [('audited inputs and hashes','audit_input_manifest.json'),('source figure reviews','figure_crop_manifest.json'),('literal label ledger','source_label_ledger.json'),('Pine review','pine_source_review.json'),('Pine source copies','pine_copy_manifest.json'),('prose review','prose_source_review.json'),('source pages','page_scan_coverage.json'),('vector review','vector_review_manifest.json'),('completion checks','completion_check.json'),('delivery hashes','delivery_manifest.json')])+'.','',
          'Verification: 598 existing fixture checks passed, but several fixtures test helpers that the producer does not call, and at least one forces its pass flag. Strict replay compares the union of stored and fresh keys: 638 recipe rows lack the newer A02/A06/A18 fields, and 658 level rows lack four newer P16 bounds. All 668 failure rows match. Fresh assembly changes A02 on 371 dates, A06 on 311 and A18 on 386, out of all 668 rows (not the eligible-session denominator). Tape replay on 33 selected dates changes OFM on 22 and squeeze on 26, on 27 distinct dates. Missing s04_rev in the direct helper replay is wrapper metadata, not a demonstrated event change. The intentional S08 recipe override is also not a stale-tape disagreement. Chart headers retain the original scorer result; fresh disagreements are identified in the case notes. See '+link('strict replay differences',OUT/'producer_replay_strict_disagreements.json')+', '+link('assembly differences',OUT/'assembly_predicate_disagreements.json')+' and '+link('fixture results',OUT/'fixture_snapshot.json')+'.','',
          'The PHASE table below counts audited IDs, not trading sessions. `faithful_disagreements` counts IDs with a definite `no` in at least one verdict; it is not a recalculated trading-rate difference. The audit table records semantic leakage even when the retained structural leakage flag is zero.','',
          '| family | variant | n | faithful_disagreements | status | report path |',
          '|---|---|---:|---:|---|---|']
    for family,name in FAMILIES.items():
        rs=[r for r in selected if r['id'][2]==family]
        if rs:text.append(f'| {name} | source + chart audit | {len(rs)} | {sum("no" in r["oks"] for r in rs)} | {"fail" if any("no" in r["oks"] for r in rs) else "partial"} | '+link('CHART_AUDIT.md',DEST)+' |')
    text += ['','| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |',
             '|---|---|---|---|---|---|---|']
    for r in selected:
        verdict='fail' if 'no' in r['oks'] else 'blocked' if 'blocked' in r['oks'] else 'gap' if 'gap' in r['oks'] else 'cannot-tell' if 'cannot-tell' in r['oks'] else 'pass'
        if args.draft and r not in refreshed:verdict='pending source-set redo; prior '+verdict
        text.append('| '+' | '.join(map(esc,[FAMILIES[r['id'][2]],r['id'],verdict,r.get('fixture','existing suite passes; semantic coverage insufficient'),r.get('leakage','see specification'),r.get('proxy','yes'),r['finding']]))+' |')
    text += ['','## Required per-ID verdicts','',
             '| id | source_ok | code_ok | score_event_ok | chart_ok | evidence | ask_user |',
             '|---|---|---|---|---|---|---|']
    for r in selected:
        pp=[p for p in plots if p['id']==r['id']]
        cases='; '.join(link(p['date']+' '+p['case'],OUT/p['plot']) for p in pp)
        evidence=cases+'. '+r['finding']+' Source: '+source_links(r)+'. '+r['source']
        if args.draft and r not in refreshed:evidence='SOURCE-SET REDO PENDING. Earlier evidence: '+evidence
        if r['id']=='R-R01':evidence+=' Native-product evidence: '+link('all native plots and reviews',OUT/'native_options_review.json')+'.'
        text.append('| '+' | '.join([r['id'],*r['oks'],esc(evidence),'yes' if r.get('ask_user') else 'no'])+' |')
    text += ['','## Per-ID repair specifications','',
          'Apply these only in a separately authorized implementation task. Do not create a new faithful recipe to repair a source contradiction. Keep author definitions, explicitly named research defaults, unavailable inputs and outcome measurements distinguishable. Every event record must identify its instrument/contract, session scope, source/variant, level bounds, feature cutoff, known_at, touch, confirmation, invalidation and outcome horizon. Unknown or incomplete observations are null with a reason, not false.','',
          'Common implementation requirements: identify the source display timezone, the strategy session timezone and the instrument exchange calendar separately. Use a named IANA zone with date-specific daylight-saving rules where established; a fixed UTC offset is valid only when that is the stated source convention. Preserve both raw display time and converted event time with the evidence for their mapping. If that mapping is unresolved, stop clock-dependent source certification instead of treating the chart as EST or shifting its range to fit. Then resample on the declared session clock; require complete bars; advance close-based known_at to bar completion; use an explicit tick-rounding policy; scan events chronologically; freeze chosen levels at the decision time; never select a level or direction using later extrema. Do not count one extended visit as multiple retests. If a one-minute bar contains both success and invalidation with unknown order, inspect available executions or keep the observation ambiguous. Cache identity must include source/producer version, required schema keys, input hashes, clocks, parameters and eligibility. Validate the schema before reuse; a matching revision number alone is insufficient.','',
          'For profile work, include zero-volume price bins within the price grid, define tie handling, retain aggressor-unknown volume separately and keep fixed prior profiles separate from developing profiles. Quantile/volume baselines used at an event must use only observations available then. Rates require an explicit eligible population, censoring and event unit; conditional empty populations have n=0. A presence/touch statistic must not inherit a confirmation, hold, reversal or target-reaching label.','']
    text += ['Reference-high/low lifecycle required by the user: assign each completed reference a stable ID, side, price, formation interval and known_at. Scan all subsequent available prices from known_at, including overnight trading before a later decision window. For each side store first_revisit_at and stop the active line there. An exact visit consumes freshness independently of any separately named two-tick sweep-depth threshold. Keep missing coverage as freshness unknown; do not infer unvisited from absent bars. Preserve a first-visit sweep/failure episode through its confirmation and outcome, but do not rearm that same reference after price leaves and returns. Only a newly formed reference with its own ID can be fresh again. Keep the opposite high/low independent, and distinguish a historical completed box from its active target lines. Opening-price lines, profile value and other objects need their own sourced lifecycle; do not erase them merely by analogy to a session extreme.','']
    for r in selected:
        s=scores[r['id']];text += [f'### {r["id"]} — {r["title"]}','',r['source'],'',r['finding'],'',
            '**Source references:** '+source_links(r)+'.','',
            '**Code to change:** '+', '.join(target_link(x) for x in r['targets'])+'.','']
        if r in refreshed:
            text+=['**Clock evidence:** '+r['source_refresh']['clock_basis'],'']
            text+=['**Refreshed verdict reasons:**','','| check | verdict | reason |','|---|---|---|']
            for name,check in r['source_refresh']['checks'].items():
                text.append('| '+' | '.join(map(esc,[name,check['verdict'],check['reason']]))+' |')
            text+=['']
        elif args.draft:text+=['**Source-set redo pending:** this specification is retained from the earlier audit.','']
        text+=['**Build steps:**','']
        text += [f'{i}. {v}' for i,v in enumerate(r['fix'],1)]
        text += ['','**Acceptance checks:**','']+[f'- {v}' for v in r['acceptance']]
        if r.get('ask_user'):text += ['','**Chart decision needed:** '+r['question']]
        if r.get('definition_decision'):text += ['','**Unresolved definition:** '+r['definition_decision']]
        text += ['','**Dated chart evidence:**','', '| case / date | retained scorer | source-event assessment | observed chart detail |','|---|---|---|---|']
        for p in [p for p in plots if p['id']==r['id']]:
            q=reviews.get((p['id'],p['case'],p['date']),{})
            score='unscored on this date' if p['code_result'] is None else str(p['code_result']).lower()
            label=link(p['case']+' / '+p['date'],OUT/p['plot'])
            text.append('| '+' | '.join(map(esc,[label,score,q.get('source_should_fire','review pending'),q.get('notes','review pending')]))+' |')
        if r['id']=='R-R01':
            text+=['','**Native-product supplements:**','','| product / date | observed input and chart limitation |','|---|---|']
            for q in native:text.append('| '+link(q['product']+' / '+q['date'],OUT/q['plot'])+' | '+esc(q['notes'])+' |')
        text += ['']
    DEST.write_text('\n'.join(text)+'\n')
    print(f'Wrote {DEST}: {len(selected)} IDs / {sum(len(r["fix"]) for r in selected)} explicit build steps')

if __name__=='__main__':main()
