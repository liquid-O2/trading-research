from pathlib import Path
import json,re,yaml
from PIL import Image,ImageDraw
p=Path('/workspace/planning/trading-model/review/external/skylit'); a=json.loads((p/'inventory.json').read_text()); seen={}; out=[]
for d in a['pages']:
 t=Path(d['readable_path']).read_text()
 if '## OpenAPI' not in t: continue
 s=t.split('````yaml ',1)[1].split('\n',1)[1].split('````',1)[0]; z=yaml.safe_load(s)
 row=[f"## {d['id']} {d['url']}"]
 for k,v in z.items():
  if k=='components':
   for c,items in v.items():
    for name,value in items.items():
     sig=json.dumps(value,sort_keys=True)
     if sig in seen: row.append(f'component {c}/{name}: same as {seen[sig]}')
     else: seen[sig]=f"{d['id']} {c}/{name}";row.append(f'component {c}/{name}: '+json.dumps(value,ensure_ascii=False,separators=(',',':')))
  else:
   sig=json.dumps(v,sort_keys=True)
   if sig in seen: row.append(f'{k}: same as {seen[sig]}')
   else: seen[sig]=f"{d['id']} {k}";row.append(k+': '+json.dumps(v,ensure_ascii=False,separators=(',',':')))
 out.append('\n'.join(row))
(p/'openapi-unique-review.md').write_text('\n\n'.join(out))
ims=json.loads((p/'images.json').read_text()); dest=p/'sheets';dest.mkdir(exist_ok=True)
for b in range(0,len(ims),3):
 items=ims[b:b+3];imgs=[]
 for d in items:
  im=Image.open(d['path']).convert('RGB');im.thumbnail((1700,1000));imgs.append((d,im))
 canvas=Image.new('RGB',(max(im.width for _,im in imgs),sum(im.height+36 for _,im in imgs)),(235,235,235));draw=ImageDraw.Draw(canvas);y=0
 for d,im in imgs:
  draw.text((10,y+6),d['id']+' / '+d['page_id'],fill='black');canvas.paste(im,(0,y+36));y+=im.height+36
 canvas.save(dest/f"sheet-{b//3+1:02}.jpg",quality=92)
print('OpenAPI review chars',sum(map(len,out)),'pages',len(out),'sheets',len(list(dest.glob('*.jpg'))))
