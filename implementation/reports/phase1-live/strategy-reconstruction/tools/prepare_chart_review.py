from pathlib import Path
from PIL import Image,ImageDraw
import json,math,argparse
p=argparse.ArgumentParser();p.add_argument('--run-root',required=True);root=Path(p.parse_args().run_root)
m=json.loads((root/'charts/manifest.json').read_text());out=root/'charts/qa';out.mkdir(exist_ok=True)
lines=['# Diagnostic charts — strategy reconstruction','',m['selection']+'.','']
for n,e in enumerate(m['examples'],1):lines.append(f"{n}. [{e['coverage_id']} — {e['verdict']}, {e['date']}]({e['path']}) · [native job]({e['job']['path']})")
(root/'charts/README.md').write_text('\n'.join(lines)+'\n')
for begin in range(0,len(m['examples']),4):
 sheet=Image.new('RGB',(2000,1450),'#d9dde2');draw=ImageDraw.Draw(sheet)
 for k,e in enumerate(m['examples'][begin:begin+4]):
  im=Image.open(e['path']).convert('RGB');im.thumbnail((990,681))
  x=(k%2)*1000;y=(k//2)*725
  draw.text((x+6,y+5),f"{begin+k+1}: {e['coverage_id']} | {e['verdict']}",fill='black')
  sheet.paste(im,(x+(1000-im.width)//2,y+30))
 sheet.save(out/f'contact-{begin//4+1:02}.jpg',quality=95)
print(len(m['examples']),'charts;',math.ceil(len(m['examples'])/4),'contact sheets')
