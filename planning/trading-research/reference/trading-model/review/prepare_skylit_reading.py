from pathlib import Path
from urllib.parse import urlsplit
import re,json
root=Path('/workspace/planning/trading-model/review/external/skylit');x=json.load(open(root/'inventory.json'));images=[]
for idx,r in enumerate(x['pages'],1):
 r['id']=f'SKY{idx:03d}';s=Path(r['path']).read_text()
 def img(m):
  raw=m.group(0);src=re.search(r'src="([^"]+)"',raw)
  if not src:return raw
  u=src.group(1);iid=f"IMG{len(images)+1:03d}";images.append({'id':iid,'page_id':r['id'],'url':u,'source_page':r['url'],'viewed':False});return f'[{iid}: image {u.split("/")[-1].split("?")[0]}]'
 s=re.sub(r'<img\b[^>]+>',img,s)
 def mdimg(m):
  iid=f"IMG{len(images)+1:03d}";images.append({'id':iid,'page_id':r['id'],'url':m.group(2),'source_page':r['url'],'viewed':False});return f'[{iid}: image {m.group(1)}]'
 s=re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',mdimg,s)
 q=root/'readable'/f"{r['id']}.md";q.parent.mkdir(exist_ok=True);q.write_text(s);r['readable_path']=str(q);r['readable_lines']=len(s.splitlines())
(root/'inventory.json').write_text(json.dumps(x,indent=2));(root/'images.json').write_text(json.dumps(images,indent=2));print(len(images),'image references')
