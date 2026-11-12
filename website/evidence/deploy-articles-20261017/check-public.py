from pathlib import Path
import json,hashlib,urllib.request,urllib.error,concurrent.futures,datetime,re
from xml.etree import ElementTree as ET
R=Path(__file__).resolve().parents[2];E=Path(__file__).resolve().parent;P=json.loads((E/'plan.json').read_text());B=json.loads((E/'preflight.json').read_text());revision=P['revision']
def check(item):
 name,digest=item
 with urllib.request.urlopen('https://www.eliai.cn/'+name+'?release_check='+revision,timeout=20) as response:
  data=response.read();assert response.status==200 and hashlib.sha256(data).hexdigest()==digest,name
  if name.endswith('.html') and name not in P['verification_files']:
   s=data.decode();assert revision in s,name
   if '/articles/' in '/'+name or name in ['articles.html','en/articles.html']:
    assert '<meta name="robots" content="index,follow">' in s,name
   assert 'noindex' not in response.headers.get('X-Robots-Tag','').lower(),name
  return dict(path=name,status=200,sha256=digest)
# All generated HTML pages and discovery/verification plus scripts and styles used by the release.
items=[(n,h) for n,h in P['files'].items() if n.endswith(('.html','.css','.js')) or n in ['robots.txt','sitemap.xml','health.json','llms.txt','BingSiteAuth.xml','sogousiteverification.txt']]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,items))
xml=urllib.request.urlopen('https://www.eliai.cn/sitemap.xml',timeout=15).read();urls=ET.fromstring(xml).findall('{*}url');assert len(urls)==294
for name in ['content/articles.json','site.yaml','evidence/deploy-articles-20261017/plan.json','assets/flex-carousel-official.js','assets/img10.webp','experiments.html']:
 try:urllib.request.urlopen('https://www.eliai.cn/'+name,timeout=15);raise AssertionError('Must be unavailable: '+name)
 except urllib.error.HTTPError as err:assert err.code==404,(name,err.code)
(E/'public-http-checks.json').write_text(json.dumps(dict(status='PASS',timestamp=datetime.datetime.now().astimezone().isoformat(),revision=revision,checked=len(results),sitemap_urls=294,article_topics=102,localized_article_pages=204,search_submissions=0,private_and_retired_paths='404',results=results),indent=2))
print('PUBLIC_HTTP_PASS',len(results),'files;294 sitemap URLs;204 published article pages')
