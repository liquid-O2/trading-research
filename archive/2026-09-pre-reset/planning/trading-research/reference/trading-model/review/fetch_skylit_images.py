from pathlib import Path
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
import json,hashlib
root=Path('/workspace/planning/trading-model/review/external/skylit');rows=json.load(open(root/'images.json'));out=root/'images';out.mkdir(exist_ok=True)
def fetch(r):
 try:
  req=Request(r['url'],headers={'User-Agent':'Mozilla/5.0'})
  with urlopen(req,timeout=25) as f:b=f.read();r['status']=f.status
  p=out/(r['id']+'.png');p.write_bytes(b);r.update(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:r['error']=str(e)
 return r
with ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(fetch,rows))
(root/'images.json').write_text(json.dumps(rows,indent=2));print('Images',len(rows),'errors',sum('error'in r for r in rows),'bytes',sum(r.get('bytes',0)for r in rows))
