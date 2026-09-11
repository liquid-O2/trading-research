"""Extract and tile original PDF figures for manual vision inspection.

This only creates inspection copies. It never modifies an input PDF. Crops
overlap so labels and candles at a crop boundary remain visible in another crop.
No inference or automated visual verdict is made here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
CACHE = Path('/tmp/phase1-chart-audit/visuals')
OUT = ROOT / 'implementation/reports/phase1-live/chart-audit'


def prepare() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    figures: dict[str, dict] = {}
    for src in sorted((ROOT / 'sources/documents').rglob('*.pdf')):
        doc = pymupdf.open(src)
        for pno, page in enumerate(doc, 1):
            for ino, item in enumerate(page.get_images(full=True), 1):
                data = doc.extract_image(item[0])
                w, h = data['width'], data['height']
                # Repeating Ethos logo and decorative cover/background only.
                if (w, h) in {(438, 489), (1588, 2246), (900, 1900)}:
                    continue
                if w < 120 or h < 60:
                    continue
                sha = hashlib.sha256(data['image']).hexdigest()
                ref = {'source': str(src.relative_to(ROOT)), 'page': pno,
                       'image': ino, 'width': w, 'height': h}
                if sha in figures:
                    figures[sha]['occurrences'].append(ref)
                    continue
                key = f'{src.stem}-p{pno:03}-i{ino}'
                folder = CACHE / key
                folder.mkdir(exist_ok=True)
                original = folder / ('original.' + data['ext'])
                original.write_bytes(data['image'])
                im = Image.open(original).convert('RGB')
                boxes = {
                    'upper-left': (0, 0, int(w*.58), int(h*.58)),
                    'upper-right': (int(w*.42), 0, w, int(h*.58)),
                    'lower-left': (0, int(h*.42), int(w*.58), h),
                    'lower-right': (int(w*.42), int(h*.42), w, h),
                }
                crops = []
                for label, box in boxes.items():
                    f = folder / (label + '.png')
                    im.crop(box).save(f)
                    crops.append({'region': label, 'bounds_px': box, 'file': str(f)})
                figures[sha] = {'key': key, 'sha256': sha, 'original': str(original),
                                'occurrences': [ref], 'crops': crops,
                                'reviewed': False}
    (OUT / 'figure_crop_manifest.json').write_text(json.dumps(list(figures.values()), indent=2))
    print(json.dumps({'unique_figures': len(figures),
                      'occurrences': sum(len(f['occurrences']) for f in figures.values()),
                      'overlapping_crops': len(figures)*4}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.parse_args()
    prepare()
