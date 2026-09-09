from pathlib import Path
import pymupdf
root=Path('/workspace/sources/documents/discretionary');out=Path('/workspace/planning/trading-model/review/pdf-render/discretionary')
order=['amt-lesson-1','vp-lesson-2','tpo-lesson-3','vix-lesson-4','dom-lesson-5','dom-lesson-6','dom-lesson-7','fp-lesson-8','fp-lesson-9','vwap-lesson-10']
files=sorted(root.glob('*.pdf'),key=lambda p:order.index(p.stem) if p.stem in order else 100)
for p in files:
 d=pymupdf.open(p);dest=out/p.stem;dest.mkdir(parents=True,exist_ok=True)
 for i,page in enumerate(d,1):
  target=dest/f'p{i:03d}.png'
  if not target.exists():page.get_pixmap(matrix=pymupdf.Matrix(1600/page.rect.width,1600/page.rect.width),alpha=False).save(target)
 print(p.name,len(d),flush=True)
