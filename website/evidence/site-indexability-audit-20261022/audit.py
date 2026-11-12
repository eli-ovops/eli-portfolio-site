import urllib.request,urllib.error,urllib.parse,urllib.robotparser,hashlib,json,re,time,collections,concurrent.futures
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
D=Path(__file__).resolve().parent
urls=json.loads((D/'sitemap-urls.json').read_text()); base='https://www.eliai.cn/'
class Parser(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.canonical=[];self.hreflang=[];self.meta={};self.title=[];self.h1=[];self.links=[];self.ids=[];self.resources=[];self.maintext=[];self.paragraphs=[];self.jsonld=[];self.stack=[];self.script_data=[];self.in_ld=False;self.lang=''
 def handle_starttag(self,t,attrs):
  a=dict(attrs);self.stack.append(t) if t not in ['meta','link','img','input','br','hr','source','wbr','area','base','embed','param','track','col'] else None
  if t=='html': self.lang=a.get('lang','')
  if a.get('id'):self.ids.append(a['id'])
  if t=='link':
   if 'canonical' in a.get('rel','').split():self.canonical.append(a.get('href'))
   if a.get('hreflang'):self.hreflang.append([a['hreflang'],a.get('href')])
   if a.get('rel')=='stylesheet':self.resources.append(a.get('href'))
  if t=='script':
   if a.get('src'):self.resources.append(a['src'])
   self.in_ld=a.get('type')=='application/ld+json';self.script_data=[]
  if t=='meta':self.meta.setdefault(a.get('name',a.get('property','')).lower(),[]).append(a.get('content',''))
  if t=='a' and a.get('href'):self.links.append(a['href'])
  if t=='img' and a.get('src'):self.resources.append(a['src'])
 def handle_endtag(self,t):
  if t=='script' and self.in_ld:
   try:self.jsonld.append(json.loads(''.join(self.script_data)))
   except Exception as e:self.jsonld.append({'PARSE_ERROR':str(e)})
   self.in_ld=False
  if t in self.stack:self.stack=self.stack[:len(self.stack)-1-self.stack[::-1].index(t)]
 def handle_data(self,s):
  if self.in_ld:self.script_data.append(s)
  if 'script' in self.stack or 'style' in self.stack:return
  if 'title' in self.stack:self.title.append(s)
  if 'h1' in self.stack:self.h1.append(s)
  if 'main' in self.stack and not any(t in self.stack for t in ['nav','aside','footer']):
   self.maintext.append(s)
   if 'p' in self.stack:self.paragraphs.append(s)
 def export(self):
  d={k:getattr(self,k) for k in ['canonical','hreflang','meta','links','ids','resources','jsonld','lang']};d.update(title=''.join(self.title),h1=' '.join(self.h1),maintext=' '.join(self.maintext),paragraphs=self.paragraphs);return d

def fetch(url):
 start=time.monotonic();path=urllib.parse.urlparse(url).path.lstrip('/');path=path+'index-root.html' if not path or path.endswith('/') else path;dest=D/'raw'/path;dest.parent.mkdir(parents=True,exist_ok=True)
 try:
  with urllib.request.urlopen(url,timeout=25) as r:
   b=r.read();dest.write_bytes(b);p=Parser();p.feed(b.decode('utf-8'))
   return dict(url=url,status=r.status,final_url=r.url,elapsed=round(time.monotonic()-start,3),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),headers={k:v for k,v in r.headers.items() if k.lower() in ['content-type','x-robots-tag','link','location','last-modified','etag']},**p.export())
 except Exception as e:
  return dict(url=url,status=getattr(e,'code',None),error=str(e),elapsed=round(time.monotonic()-start,3))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 results=list(pool.map(fetch,urls))
(D/'pages.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
lookup={x['url']:x for x in results};rp=urllib.robotparser.RobotFileParser();rp.parse((D/'raw/robots.txt').read_text().splitlines())
issues=[];broken_links=[];anchor_issues=[];parameter_links=[]
def norm(u):
 p=urllib.parse.urlparse(u);return urllib.parse.urlunparse(p._replace(query='',fragment=''))
for x in results:
 u=x['url']
 if x['status']!=200:issues.append({'issue':'HTTP_NOT_200','url':u,'status':x['status']});continue
 if x['final_url']!=u:issues.append({'issue':'CANONICAL_URL_REDIRECT','url':u,'final_url':x['final_url']})
 if x['canonical']!=[u]:issues.append({'issue':'CANONICAL_MISMATCH','url':u,'value':x['canonical']})
 directives=' '.join(x['meta'].get('robots',[])+x['meta'].get('googlebot',[])+[x['headers'].get('X-Robots-Tag','')])
 if re.search(r'\b(noindex|none)\b',directives,re.I):issues.append({'issue':'NOINDEX','url':u,'value':directives})
 if not rp.can_fetch('Googlebot',u):issues.append({'issue':'ROBOTS_BLOCK','url':u})
 if not x['title'] or not x['h1']:issues.append({'issue':'MISSING_TITLE_OR_H1','url':u})
 if not x['meta'].get('description',[''])[0]:issues.append({'issue':'MISSING_DESCRIPTION','url':u})
 for lang,target in x['hreflang']:
  if target not in lookup:issues.append({'issue':'HREFLANG_NOT_IN_SITEMAP','url':u,'target':target})
  elif target!=u and lang!='x-default' and not any(t==u for l,t in lookup[target].get('hreflang',[])):issues.append({'issue':'HREFLANG_RETURN_MISSING','url':u,'target':target})
 if not any(t==u for l,t in x['hreflang'] if l!='x-default'):issues.append({'issue':'HREFLANG_SELF_MISSING','url':u})
 for j in x['jsonld']:
  if 'PARSE_ERROR' in j:issues.append({'issue':'JSONLD_INVALID','url':u})
 for href in x['links']:
  absu=urllib.parse.urljoin(u,href);parts=urllib.parse.urlparse(absu)
  if parts.netloc!='www.eliai.cn' or parts.scheme!='https':continue
  canonical=norm(absu)
  if parts.query:parameter_links.append({'from':u,'to':absu})
  if canonical in lookup:
   if parts.fragment and urllib.parse.unquote(parts.fragment) not in lookup[canonical].get('ids',[]):anchor_issues.append({'from':u,'to':absu})
  elif not parts.path.startswith('/assets/'):broken_links.append({'from':u,'to':absu})
# Link graph uses raw HTML links only; root and /index.html are equivalent for discovery.
adj={u:set() for u in lookup}
for x in results:
 for h in x.get('links',[]):
  target=norm(urllib.parse.urljoin(x['url'],h))
  if target in lookup:adj[x['url']].add(target)
dist={base:0,base+'index.html':0};q=collections.deque(dist)
while q:
 u=q.popleft()
 for v in adj.get(u,set()):
  if v not in dist:dist[v]=dist[u]+1;q.append(v)
inbound=collections.Counter(v for a in adj.values() for v in a)
article=[x for x in results if '/articles/' in x['url']];services=[x for x in results if '/services/' in x['url']]
summary={'checked_at':datetime.now(timezone.utc).isoformat(),'count':len(results),'articles':len(article),'services':len(services),'statuses':dict(collections.Counter(str(x['status']) for x in results)),'issues':issues,'links_not_in_sitemap':broken_links,'missing_fragment_targets':anchor_issues,'parameter_links':parameter_links,'raw_html_unreachable_articles':[x['url'] for x in article if x['url'] not in dist],'article_depths':dict(collections.Counter(dist.get(x['url'],'unreachable') for x in article)),'zero_inbound_articles':[x['url'] for x in article if not inbound[x['url']]],'focus_html_sizes':{'min':min(x['bytes'] for x in article+services if 'bytes'in x),'max':max(x['bytes'] for x in article+services if 'bytes'in x)}}
(D/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k not in ['parameter_links','links_not_in_sitemap','missing_fragment_targets','raw_html_unreachable_articles','zero_inbound_articles']},ensure_ascii=False,indent=2))
print('OUTSIDE_MAP',len(broken_links),'ANCHOR_ISSUES',len(anchor_issues),'PARAM_LINKS',len(parameter_links),'UNREACHABLE',len(summary['raw_html_unreachable_articles']))
