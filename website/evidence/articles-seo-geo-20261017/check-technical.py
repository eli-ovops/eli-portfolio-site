from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree as ET
import json,urllib.request,concurrent.futures,collections,datetime,hashlib,re
R=Path(__file__).resolve().parents[2];E=Path(__file__).resolve().parent;base='https://www.eliai.cn/'
class Page(HTMLParser):
 def __init__(self,s):
  super().__init__();self.meta={};self.links=[];self.h1=0;self.title='';self.intitle=False;self.jsonblocks=[];self.injson=False;self.jsontext='';self.feed(s)
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='meta':self.meta[a.get('name','')]=a.get('content','')
  if t=='link' or t=='a':self.links.append((t,a))
  if t=='h1':self.h1+=1
  if t=='title':self.intitle=True
  if t=='script' and a.get('type')=='application/ld+json':self.injson=True;self.jsontext=''
 def handle_endtag(self,t):
  if t=='title':self.intitle=False
  if t=='script' and self.injson:
   self.jsonblocks.append(json.loads(self.jsontext));self.injson=False
 def handle_data(self,d):
  if self.intitle:self.title+=d
  if self.injson:self.jsontext+=d
robots=urllib.request.urlopen(base+'robots.txt',timeout=20).read().decode();robot=RobotFileParser();robot.parse(robots.splitlines());sm=urllib.request.urlopen(base+'sitemap.xml',timeout=20).read();allurls=[u.find('{*}loc').text for u in ET.fromstring(sm).findall('{*}url')];urls=[u for u in allurls if '/articles/' in u or u.endswith('articles.html')];assert len(urls)==206
agents=['Googlebot','bingbot','Baiduspider','OAI-SearchBot','ChatGPT-User','PerplexityBot','Perplexity-User']
def check(url):
 with urllib.request.urlopen(url,timeout=20) as response:
  raw=response.read();s=raw.decode();p=Page(s);headers=dict(response.headers)
  canonical=[a['href'] for t,a in p.links if t=='link' and a.get('rel')=='canonical'];langs={a.get('hreflang'):a['href'] for t,a in p.links if t=='link' and a.get('rel')=='alternate' and a.get('hreflang')};detail='/articles/' in url;graphs=[x for b in p.jsonblocks for x in b.get('@graph',[b])];article=next((x for x in graphs if x.get('@type')=='Article'),None);refs=[a['href'] for t,a in p.links if t=='a' and a.get('href','').startswith('https://') and 'eliai.cn' not in urlsplit(a['href']).netloc];errors=[]
  if response.status!=200 or len(canonical)!=1 or canonical[0]!=url:errors.append('HTTP/canonical')
  if p.meta.get('robots')!='index,follow' or 'noindex' in headers.get('X-Robots-Tag','').lower():errors.append('indexability')
  if p.h1!=1 or not p.title or not p.meta.get('description'):errors.append('H1/title/description')
  if not all(k in langs for k in ['zh-CN','en','x-default']):errors.append('hreflang')
  if any(not robot.can_fetch(a,url) for a in agents):errors.append('crawler_robots')
  if detail and (not article or not article.get('datePublished') or not article.get('author')):errors.append('Article schema')
  staticlinks=[urljoin(url,a['href']).split('?')[0].split('#')[0] for t,a in p.links if t=='a' and 'href' in a]
  return dict(url=url,status=response.status,bytes=len(raw),title=p.title,description=p.meta.get('description'),canonical=canonical,alternates=langs,robots=p.meta.get('robots'),article_schema=bool(article),source_links=len(set(refs)),static_article_links=len({v for v in staticlinks if '/articles/' in v}),errors=errors,revision=p.meta.get('portfolio-revision'),sha256=hashlib.sha256(raw).hexdigest())
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,urls))
titles=collections.Counter(x['title'] for x in results);descriptions=collections.Counter(x['description'] for x in results);assert not any(x['errors'] for x in results)
llms=urllib.request.urlopen(base+'llms.txt',timeout=20).read().decode()
output=dict(status='PASS',timestamp=datetime.datetime.now().astimezone().isoformat(),public_sitemap_urls=len(allurls),article_detail_pages=204,article_lists=2,pages_checked=len(results),revision=set(x['revision'] for x in results).pop(),crawler_access={a:robot.can_fetch(a,base+'articles/what-is-ai.html') for a in agents},duplicate_titles=[k for k,v in titles.items() if v>1],duplicate_descriptions=[k for k,v in descriptions.items() if v>1],static_list_link_counts=[x['static_article_links'] for x in results if x['url'].endswith('articles.html')],llms_has_article_entry='articles.html' in llms,robots=robots,errors=[],pages=results)
(E/'technical-checks.json').write_text(json.dumps(output,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in output.items() if k not in ['pages','robots']},ensure_ascii=False))
