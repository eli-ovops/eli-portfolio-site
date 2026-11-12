from pathlib import Path
from datetime import datetime,timezone
import urllib.request,urllib.error,hashlib,json,concurrent.futures,re
D=Path(__file__).resolve().parent;P=json.loads((D/'plan.json').read_text());base='https://www.eliai.cn'
paths=['/','/en/','/index.html','/en/index.html','/records.html','/en/records.html','/about.html','/en/about.html','/articles.html','/en/articles.html','/assets/page-version.js','/sitemap.xml','/robots.txt','/llms.txt']
paths += ['/'+prefix+'cases/'+p+'.html' for prefix in ['','en/'] for p in ['p09','p10','p36']]
paths += ['/'+prefix+'services/'+p+'.html' for prefix in ['','en/'] for p in ['ai-agent','workflow-automation','fde-consulting']]
paths += ['/'+prefix+'articles/'+p+'.html' for prefix in ['','en/'] for p in ['inventory-reconciliation','enterprise-knowledge-base']]
paths += ['/'+p for p in P['verification_files']]
def check(path):
 key=path.lstrip('/');key+='index.html' if path.endswith('/') else ''
 with urllib.request.urlopen(base+path,timeout=20) as r:
  b=r.read();h=hashlib.sha256(b).hexdigest();assert r.status==200 and h==P['files'][key],path
  if key.endswith('.html') and key not in P['verification_files']:
   assert P['revision'].encode() in b,path
   assert not re.search(rb'<a\b[^>]*\bhref="[^"#?]*index\.html(?:[?#][^"]*)?"',b),path
  return {'url':base+path,'status':r.status,'sha256':h,'matches_candidate':True}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:checks=list(pool.map(check,paths))
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
routes={'/cases/':'/records.html','/articles/':'/articles.html','/en/cases/':'/en/records.html','/en/articles/':'/en/articles.html','/services/':'/index.html#needs','/en/services/':'/en/index.html#needs'}
redirects=[]
for src,dst in routes.items():
 try:r=urllib.request.build_opener(NoRedirect).open(base+src,timeout=20)
 except urllib.error.HTTPError as e:r=e
 assert r.code==301 and r.headers.get('Location')==base+dst,(src,r.code,r.headers.get('Location'))
 redirects.append({'url':base+src,'status':r.code,'location':r.headers.get('Location')});r.close()
result={'checked_at':datetime.now(timezone.utc).isoformat(),'revision':P['revision'],'public_file_checks':checks,'count':len(checks),'redirects_unchanged':redirects,'status':'PASS','traffic':'OWN_QA_NOT_ORGANIC'}
(D/'public-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({'status':'PASS','independent_https_file_checks':len(checks),'existing_directory_redirect_checks':len(redirects)}))
