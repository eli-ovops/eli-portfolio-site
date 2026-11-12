from pathlib import Path
import json,urllib.request,urllib.parse,urllib.robotparser,hashlib,collections,concurrent.futures,re,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent
source=(D/'audit.py').read_text();namespace={"__file__":str(D/"audit.py")};exec(source[:source.index('with concurrent.futures.ThreadPoolExecutor')],namespace)
with urllib.request.urlopen('https://www.eliai.cn/en/',timeout=20) as r:
 b=r.read();(D/'raw/en/index-root.html').write_bytes(b);p=namespace['Parser']();p.feed(b.decode())
 x=dict(url='https://www.eliai.cn/en/',status=r.status,final_url=r.url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),headers={k:v for k,v in r.headers.items() if k.lower() in ['content-type','x-robots-tag','link','last-modified','etag']},**p.export())
results=json.loads((D/'pages.json').read_text());results=[x if a['url']==x['url'] else a for a in results];(D/'pages.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
ns={'results':results,'D':D,'base':'https://www.eliai.cn/','urllib':__import__('urllib'),'collections':collections,'re':re,'json':json,'datetime':__import__('datetime').datetime,'timezone':__import__('datetime').timezone}
exec(source[source.index('lookup={'):],ns)
focus=[x for x in results if '/articles/' in x['url'] or '/services/' in x['url']]
resources=sorted(set(urllib.parse.urljoin(x['url'],h) for x in focus for h in x['resources'] if urllib.parse.urlparse(urllib.parse.urljoin(x['url'],h)).netloc=='www.eliai.cn'))
def fetchres(u):
 with urllib.request.urlopen(u,timeout=20) as r:
  b=r.read();return {'url':u,'status':r.status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: resource_results=list(pool.map(fetchres,resources))
(D/'resources.json').write_text(json.dumps(resource_results,indent=2))
groups={}
for key in ['title','description','maintext']:
 g=collections.defaultdict(list)
 for x in focus:
  value=x.get('meta',{}).get('description',[''])[0] if key=='description' else x[key]
  g[value].append(x['url'])
 groups[key]=[v for v in g.values() if len(v)>1]
parents={urllib.parse.urlparse(x['url']).path:x for x in results}
root=E.fromstring((D/'raw/sitemap.xml').read_bytes());s={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
lastmods=collections.Counter(n.find('s:lastmod',s).text for n in root.findall('s:url',s));print('LASTMODS',dict(lastmods));print('DUPLICATES',groups,'RESOURCES',len(resources))
inbounds=[]
for x in focus:
 if '/services/' in x['url'] and '/en/' not in x['url']:
  ins=[z['url'] for z in results if any(urllib.parse.urljoin(z['url'],h)==x['url'] for h in z.get('links',[]))]
  inbounds.append({'service':x['url'],'inbound_page_count':len(ins),'article_inbound':sum('/articles/' in u for u in ins)})
print('SERVICE_INBOUNDS',inbounds)
(D/'supplement.json').write_text(json.dumps({'exact_duplicate_focus_groups':groups,'focus_page_count':len(focus),'focus_resource_count':len(resources),'sitemap_lastmod_counts':dict(lastmods),'services_inbound':inbounds,'raw_article_links_zh':len(set(urllib.parse.urljoin('https://www.eliai.cn/articles.html',h) for h in parents['/articles.html']['links'] if '/articles/' in urllib.parse.urljoin('https://www.eliai.cn/articles.html',h))),'raw_article_links_en':len(set(urllib.parse.urljoin('https://www.eliai.cn/en/articles.html',h) for h in parents['/en/articles.html']['links'] if '/articles/' in urllib.parse.urljoin('https://www.eliai.cn/en/articles.html',h)))},ensure_ascii=False,indent=2))
