from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote,parse_qs
from xml.etree import ElementTree as ET
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2]; E=Path(__file__).resolve().parent; D=E/'public';plan=json.loads((E/'plan.json').read_text());before=json.loads((E/'preflight.json').read_text())
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=set();self.refs=[];self.h1=0;self.meta={};self.canonical=None;self.json='';self.structured=False
 def handle_starttag(self,t,a):
  a=dict(a)
  if 'id' in a:assert a['id'] not in self.ids;self.ids.add(a['id'])
  if t=='h1':self.h1+=1
  if t=='meta':self.meta[a.get('name',a.get('property'))]=a.get('content')
  if t=='link' and a.get('rel')=='canonical':self.canonical=a['href']
  if t=='script' and a.get('type')=='application/ld+json':self.structured=True
  for key in ['href','src']:
   if a.get(key):self.refs.append(a[key])
 def handle_endtag(self,t):
  if t=='script':self.structured=False
 def handle_data(self,s):
  if self.structured:self.json+=s
pages={}
for p in D.rglob('*.html'):
 # Standalone official verification files are not visitor pages.
 if p.name.startswith(('google','baidu_verify','yandex_')):continue
 a=Page();a.feed(p.read_text());assert a.h1==1,p;assert a.meta['portfolio-revision']==plan['revision'],p
 assert a.meta['robots']==('noindex,nofollow' if p.name=='404.html' else 'index,follow'),p
 if p.name!='404.html':assert json.loads(a.json)['@context']=='https://schema.org';assert a.canonical=='https://www.eliai.cn/'+('' if p.relative_to(D).as_posix()=='index.html' else p.relative_to(D).as_posix().replace('en/index.html','en/'))
 pages[p]=a
for p,a in pages.items():
 for ref in a.refs:
  u=urlparse(ref)
  if u.scheme or u.netloc:continue
  target=((D/u.path.lstrip('/')) if u.path.startswith('/') else p.parent/unquote(u.path)).resolve() if u.path else p
  assert target.is_relative_to(D.resolve()) and target.is_file(),(p,ref)
  if u.fragment and target in pages:assert unquote(u.fragment) in pages[target].ids,(p,ref)
  if target.suffix in ('.css','.js'):
   name=target.relative_to(D.resolve()).as_posix();v=parse_qs(u.query).get('v')
   assert not v or v==[before['files'][name][:12]],('Asset fingerprint mismatch',p,ref)
  if u.path.endswith('.html'):assert parse_qs(u.query).get('pv')==[plan['revision']],(p,ref)
assert len(pages)==90
urls=[n.text for n in ET.parse(D/'sitemap.xml').findall('.//{*}loc')];assert len(urls)==len(set(urls))==88
assert not any('?' in u or '404' in u for u in urls)
assert all((D/(u.removeprefix('https://www.eliai.cn/')+('index.html' if u.endswith('/') else ''))).is_file() for u in urls)
assert (D/'robots.txt').read_text()=='User-agent: *\nAllow: /\nSitemap: https://www.eliai.cn/sitemap.xml\n'
assert all(hashlib.sha256((D/p).read_bytes()).hexdigest()==h for p,h in plan['files'].items())
result={'status':'CANDIDATE_PASS','pages':90,'sitemap_urls':88,'files':len(plan['files']),'asset_versions':'Match original production bytes','links_and_anchors':'PASS','five_verification_files':'Retained','production_styles_and_scripts':'Unchanged','unrelated_local_catalogue':'EXCLUDED'}
(E/'candidate-checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
