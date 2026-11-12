from pathlib import Path
import json,hashlib,urllib.request,urllib.error,concurrent.futures
here=Path(__file__).resolve().parent
manifest=json.loads((here/'package-manifest.json').read_text())
base='http://[REDACTED_HOST]/sites/portfolio/'
def verify(item):
 path,digest=item
 request=urllib.request.Request(base+path+'?pv='+manifest['revision'],headers={'Cache-Control':'no-cache'})
 with urllib.request.urlopen(request,timeout=30) as response:
  data=response.read();assert response.status==200
  assert hashlib.sha256(data).hexdigest()==digest,('Public hash mismatch',path)
  if path.endswith('.html'):assert b'<meta name="robots" content="noindex,nofollow">' in data
  if path=='robots.txt':assert data==b'User-agent: *\nDisallow: /\n'
  return {'path':path,'status':response.status,'sha256_matches':True,'robots_header':response.headers.get('X-Robots-Tag')}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 checks=list(pool.map(verify,manifest['file_hashes'].items()))
private={}
for path in ['sitemap.xml','content/seo.json','scripts/build.py','.git/config','cases/']:
 try:
  with urllib.request.urlopen(base+path,timeout=15) as response:raise AssertionError(('Unexpected path',path,response.status))
 except urllib.error.HTTPError as error:
  assert error.code in ([403,404] if path=='cases/' else [404]),(path,error.code)
  private[path]=error.code
erp={}
for path in ['login','mobile/']:
 with urllib.request.urlopen('http://[REDACTED_HOST]/'+path,timeout=15) as response:
  assert response.status==200;erp[path]=response.status
result={'status':'PUBLIC_CHECKS_PASS','release':manifest['release'],'revision':manifest['revision'],'files_verified':len(checks),'html_pages_noindex':sum(c['path'].endswith('.html') for c in checks),'private_paths':private,'erp_entry_pages':erp,'indexing':'DISABLED','checks':checks}
(here/'public-checks.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
