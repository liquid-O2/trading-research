"""Build numbered contact sheets; this does not assert visual review passed."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw

p=argparse.ArgumentParser();p.add_argument('--run-root',required=True)
root=Path(p.parse_args().run_root).resolve()
manifest=json.loads((root/'charts/manifest.json').read_text())
out=root/'charts/qa';out.mkdir(exist_ok=True)
pages=[]
for begin in range(0,len(manifest['charts']),4):
    sheet=Image.new('RGB',(2400,1800),'#d9dde2');draw=ImageDraw.Draw(sheet)
    members=[]
    for k,item in enumerate(manifest['charts'][begin:begin+4]):
        im=Image.open(item['path']).convert('RGB');im.thumbnail((1190,850))
        x=(k%2)*1200;y=(k//2)*900
        draw.text((x+8,y+8),f"{begin+k+1}: {Path(item['path']).name}",fill='black')
        sheet.paste(im,(x+(1200-im.width)//2,y+38))
        members.append({'number':begin+k+1,'path':item['path'],'sha256':item['sha256']})
    path=out/f'contact-{begin//4+1:03}.png';sheet.save(path)
    pages.append({'sheet':str(path),'charts':members})
(out/'CONTACT_INDEX.json').write_text(json.dumps({'status':'prepared_for_manual_review','pages':pages},indent=2)+'\n')
print(len(manifest['charts']),'charts;',len(pages),'contact sheets')
