"""Read-only current checks of public reference URLs."""
import json,re,hashlib,urllib.request,concurrent.futures
from pathlib import Path
from html.parser import HTMLParser
root=Path(__file__).resolve().parents[2]
sources=json.loads((root/'content/tutorials/sources.json').read_text())
class Text(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.parts=[]
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip:self.parts.append(d)
def read(entry):
 key,s=entry
 try:
  request=urllib.request.Request(s['url'],headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(request,timeout=20) as r:
   body=r.read(2000000).decode('utf-8','replace');text=Text();text.feed(body)
   plain=' '.join(text.parts);title=re.search(r'<title[^>]*>(.*?)</title>',body,re.I|re.S)
   record=dict(key=key,status=r.status,url=r.url,title=title[1].strip() if title else '',body_sha256=hashlib.sha256(body.encode()).hexdigest(),text_length=len(plain))
   # Save focused official body for editorial review, not screenshots or private data.
   if key in ('wb-first-task','wb-skills','mcp','skills-spec','search'):
    (root/'evidence/tutorials-redteam-20261017'/('source-'+key+'.txt')).write_text(plain)
   return record
 except Exception as e:return dict(key=key,url=s['url'],error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(read,sources.items()))
(root/'evidence/tutorials-redteam-20261017/source-current-checks.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'total':len(results),'http200':sum(r.get('status')==200 for r in results),'failures':[r for r in results if 'error' in r]},ensure_ascii=False,indent=2))
