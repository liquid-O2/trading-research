"""Public documentation capture for research review; no account/API-key calls."""
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor
import re,json,hashlib,datetime
out=Path('/workspace/planning/trading-model/review/external/skylit');out.mkdir(parents=True,exist_ok=True)
def get(url):
 req=Request(url,headers={'User-Agent':'Mozilla/5.0 (research documentation review)'})
 with urlopen(req,timeout=25) as r:return r.status,r.read(),r.headers.get('Content-Type','')
status,raw,ct=get('https://docs.skylit.ai/llms.txt');(out/'llms.txt').write_bytes(raw)
urls=re.findall(r'\]\((https://docs\.skylit\.ai/[^)]+\.md)\)',raw.decode())
# Capture entire public indexed documentation so linked relevant pages are preserved;
# reading/visual accounting is tracked separately and never inferred from download.
def capture(u):
 path=urlsplit(u).path.lstrip('/');p=out/path;p.parent.mkdir(parents=True,exist_ok=True)
 try:
  status,raw,ct=get(u);p.write_bytes(raw)
  return {'url':u.removesuffix('.md'),'fetch_url':u,'path':str(p),'status':status,'content_type':ct,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'lines':len(raw.decode(errors='replace').splitlines()),'text_reviewed':[],'visual_reviewed':[]}
 except Exception as e:return {'url':u,'error':str(e),'text_reviewed':[]}
with ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(capture,urls))
res={'visited_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pages':rows};(out/'inventory.json').write_text(json.dumps(res,indent=2));print('Captured',len(rows),'pages;',sum('error'in r for r in rows),'errors;',sum(r.get('bytes',0) for r in rows),'bytes')
for i,r in enumerate(rows,1):print(f"SKY{i:03d}",r['url'],r.get('lines'),r.get('error',''))
