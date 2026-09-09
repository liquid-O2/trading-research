"""Render the authored per-component refinement; this runs no trading tests."""
from pathlib import Path
from collections import Counter
import csv
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
rows = list(csv.DictReader((HERE/'component_refinements.psv').open(), delimiter='|'))
registry = json.loads((ROOT/'review/component_registry.json').read_text())
assert len(rows)==153 and {r['id'] for r in rows}==set(registry)
assert all(set(r)=={'id','focus','definition','comparison','fixtures'} and all(r.values()) for r in rows)
byid = {r['id']:r for r in rows}
names = {'F':'Foundations','M':'Measurements','C':'Context','O':'Options','X':'Cross-market information',
         'L':'Locations','G':'Mixtures and selection','P':'Policy, execution and risk','R':'Later Response',
         'V':'Research and operations'}
doc = ['# Full-system contract refinement','',
       'This binding review refines every one of the **153 parent contracts**. It preserves the existing 191 named refinements, original source routes and P0–P7 experiment program. Each row below adds a concrete definition/interaction clarification, comparison and local failure case. These are authored implementation requirements; their proposed trading-system tests have not been run.', '',
       'The [complete handoff](IMPLEMENTATION_HANDOFF.md) and [scope index](IMPLEMENTATION_SCOPE.md) carry the entire B00–B10 program in one continuing implementation workflow. The original IV/VIX question illustrated desired feature/model depth across the system; it did not replace the other families. This contract pass makes the definitions and comparisons precise. The companion [153 substantive upgrade paths and 191 specific child bindings](UPGRADE_PATHS.md) preserve original idea → prior conversation improvement → further construction, with [shared implementation constructions](UPGRADE_CONSTRUCTIONS.md). They can improve deterministic measurements without adding a model.', '',
       '## Corrections that apply across the graph','',
       '| Issue | Binding resolution and future verification |','|---|---|',
       '| Computation latency counted twice | CC-01 uses actual completion and required input/confirmation availability; modeled duration is applied once only when completion is unobserved. The 10:00:00 input / 10:00:02 finish example must remain available at 10:00:02. |',
       '| Normalization and quality dependencies look recursive | F06.RAW prechecks precede F05 normalization; F06.SEMANTIC and F07 operation eligibility follow it. The port compiler must reject an actual cycle. |',
       '| Unchanged prices confused with missing observations | Distinguish source events, last value change, receipt, standing-state validity, liveness and scheduled publication cadence. Healthy unchanged quotes may be valid; repeated copies do not certify an outage. |',
       '| Incompatible prediction targets | Integrated/realized variation, terminal-return variance, extrema, first passage and executable policy value carry different capabilities, units and horizons. Terminal variance needs covariance terms unless the model justifies their absence. |',
       '| Conflicting probabilities across heads | Enforce only the declared coherence relations: fixed-object cumulative incidence by nested horizon, noncrossing quantiles, explicit outcome partitions and realizable joint paths. Overlapping roles/bands are not exclusive categories. Gap crossings break naive nested-band reach assumptions. |',
       '| Calibration broken by later changes | Coherence projection, calibration, gating and selection have a declared order; the final emitted chain is evaluated. Every fitted transform belongs to the chronological training closure. |',
       '| Moving definitions create apparent new market events | Freeze episode/label geometry and record revisions separately: developing value areas, profile bins, swing thresholds, mapped nodes and dynamic targets. Price motion, boundary motion and representation change have distinct provenance. |',
       '| Gamma sensitivity treated as exact finite hedging | Local Greeks, full nonlinear scenario repricing, assumed holdings and actual observed flow remain separate. Near-expiry delta saturation is a required finite-move case. No dealer ownership is inferred from aggregate OI. |',
       '| Uncertainty collapses from duplicated observations | Preserve common quote/sign/surface/holdings errors and evidence-assimilation lineage. Missing tape is different from observed unknown-side volume; endpoint OI supervision does not identify the intraday path. |',
       '| Future evaluation extended until favorable | Choose a fixed endpoint before collecting evidence, or specify a valid sequential-inference protocol with its process assumptions. An ordinary interval cannot be extended until it passes. |',
       '| An early benchmark becomes the end of scope | B00–B10 remains one program. Engineering state, evaluation state and selected/rejected/inconclusive/blocked disposition are separate and evidence-backed. Every source clause, unit, dataset and task remains visible. |','',
       'The [common contracts](components/COMMON_CONTRACTS.md), [computation schedule](components/COMPUTATION_SCHEDULE.md) and [runtime scheduler](components/RUNTIME_SCHEDULER.md) contain the corrected graph-wide rules. Parent-local details below also bind named children when their inputs/outputs are affected; do not force an unrelated child to repeat a shared arithmetic test, but record the applicable parent evidence and integration check.', '',
       '## Local refinements','']
for family, name in names.items():
    subset = sorted((r for r in rows if r['id'].startswith(family)), key=lambda r:r['id'])
    doc += [f'### {name}: {len(subset)} contracts','']
    for r in subset:
        cid=r['id'];path=Path(registry[cid]['path']).relative_to(ROOT)
        anchor='sr-'+cid.lower()
        doc += [f'<a id="{anchor}"></a>',f'#### SR-{cid} — {r["focus"]}','',
                f'Parent: [{cid} — {registry[cid]["title"]}]({path}); [individual phases](experiments/{family}.md#{cid.lower()}).', '',
                '**Definition and interaction.** '+r['definition'],'',
                '**Comparison.** '+r['comparison'],'',
                '**Local cases to implement.** '+r['fixtures'],'']
doc += ['## Evidence and acceptance','',
        'The source file [component_refinements.psv](review/system-refinement/component_refinements.psv) contains 153 individually authored records and is checked against exact parent IDs. The preserved baseline is in [baseline.zip](review/system-refinement/baseline.zip), with [baseline.json](review/system-refinement/baseline.json). Coverage/link/hash checks establish document consistency only; they do not certify the semantics of an implementation or market performance.', '',
        'At implementation expand each case into named expected assertions under the parent/local phase and relevant source clause. Apply zero-unexplained-failure rules for deterministic semantics, correct inference for forecasts, and full constrained economic evaluation for actionable changes. Preserve rejected and inconclusive results. The full-system pass is not a claim that no further improvement is possible.', '']
(ROOT/'SYSTEM_REFINEMENT.md').write_text('\n'.join(doc))

# Bind the authored detail into the original card instead of leaving it in an
# optional review appendix. Keep the original ten-field structure and wording.
for p in (ROOT/'components').glob('*.md'):
    text=p.read_text()
    def bind(m):
        cid=m[1];body=m[0]
        marker=f'[SR-{cid}](../SYSTEM_REFINEMENT.md#sr-{cid.lower()})'
        if marker not in body:
            body=re.sub(r'^(3\. \*\*[^*]+\*\*[^\n]*)',lambda n:n[0]+' Binding local refinement: '+marker+'.',body,count=1,flags=re.M)
        return body
    text=re.sub(r'^## ([FMCOLXGPRV]\d{2}) — [^\n]+\n.*?(?=^## |\Z)',bind,text,flags=re.M|re.S)
    p.write_text(text)
print(json.dumps({'status':'rendered planned refinements','parents':len(rows),
                  'families':dict(Counter(r['id'][0] for r in rows))},indent=2))
