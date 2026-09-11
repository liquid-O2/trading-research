"""Read-only source preparation for the Phase 1 chart audit.

Source PDFs and Pine are immutable. Text and visual inspection copies go to /tmp;
only the source manifest goes beside the delivered chart audit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

import fitz

ROOT = Path(__file__).resolve().parents[2]
CACHE = Path('/tmp/phase1-chart-audit')
OUT = ROOT / 'implementation/reports/phase1-live/chart-audit'


def prepare() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for src in sorted((ROOT / 'sources/documents').rglob('*.pdf')):
        key = src.stem
        dest = CACHE / 'sources' / key
        dest.mkdir(parents=True, exist_ok=True)
        doc = fitz.open(src)
        pages = []
        for i, page in enumerate(doc, 1):
            (dest / f'p{i:03}.txt').write_text(
                f'{src.relative_to(ROOT)} | PDF page {i}/{len(doc)}\n'
                + page.get_text(sort=True))
            pages.append({'page': i, 'embedded_images': len(page.get_images()),
                          'vector_paths': len(page.get_drawings()),
                          'size': [page.rect.width, page.rect.height]})
        manifest.append({'source': str(src.relative_to(ROOT)), 'sha256': hashlib.sha256(src.read_bytes()).hexdigest(),
                         'pages': pages, 'cache': str(dest)})
    pine = CACHE / 'pine'
    pine.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ROOT / 'sources/documents/indicators/Pinescript-indicators--main.zip') as z:
        for item in z.infolist():
            if item.is_dir():
                continue
            target = pine / Path(item.filename).name
            target.write_bytes(z.read(item))
    rules = (ROOT / 'planning/phase-1-live/RULES.md').read_text()
    section = rules.split('## B. Sourced recipes', 1)[1].split('## C. Swaps', 1)[0]
    ids = re.findall(r'^\*\*(R-[A-Z]\d\d)\b', section, re.M)
    assert len(ids) == 105 and len(set(ids)) == 105
    (OUT / 'source_manifest.json').write_text(json.dumps({'recipe_ids': ids, 'pdfs': manifest}, indent=2))
    print(json.dumps({'ids': len(ids), 'pdfs': len(manifest), 'pages': sum(len(p['pages']) for p in manifest),
                      'pine_files': len(list(pine.iterdir())), 'manifest': str(OUT/'source_manifest.json')}))


def render(name: str, dpi: int) -> None:
    data = json.loads((OUT/'source_manifest.json').read_text())
    for src in data['pdfs']:
        if name != 'all' and name != Path(src['source']).stem:
            continue
        doc = fitz.open(ROOT/src['source'])
        dest = Path(src['cache'])
        for i, page in enumerate(doc, 1):
            target = dest/f'p{i:03}.png'
            if not target.exists():
                page.get_pixmap(dpi=dpi).save(target)
        print(f"Rendered {src['source']}: {len(doc)} pages", flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--render')
    parser.add_argument('--dpi', type=int, default=150)
    args = parser.parse_args()
    if args.render:
        render(args.render, args.dpi)
    else:
        prepare()
