"""Focused regression checks for bilingual metadata and indexing safeguards."""
import json
from pathlib import Path
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
from urllib.parse import urlparse, unquote
from seo import load_config, page_url, metadata, sitemap, write_discovery
from content import load_content
from localization import english_content
ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/'dist'
class Head(HTMLParser):
    def __init__(self):
        super().__init__();self.meta={};self.links=[];self.title='';self.structured=[];self.in_title=False;self.in_json=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta':self.meta[a.get('name') or a.get('property')]=a.get('content')
        if tag=='link':self.links.append(a)
        if tag=='title':self.in_title=True
        if tag=='script' and a.get('type')=='application/ld+json':self.in_json=True
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
        if tag=='script':self.in_json=False
    def handle_data(self,text):
        if self.in_title:self.title+=text
        if self.in_json:self.structured.append(text)
config=load_config(ROOT);assert config['indexing_enabled'] is False, 'This task only prepares SEO; indexing must remain disabled'
titles=set();descriptions=set();pages={}
for f in DIST.rglob('*.html'):
    page=f.relative_to(DIST).as_posix();head=Head();head.feed(f.read_text());pages[page]=head
    assert head.title and head.title not in titles,('Duplicate title',page);titles.add(head.title)
    assert head.meta.get('description') and head.meta['description'] not in descriptions,('Duplicate description',page);descriptions.add(head.meta['description'])
    assert head.meta['robots']=='noindex,nofollow',page
    if page.endswith('404.html'):
        assert not head.structured and not any(l.get('rel')=='canonical' for l in head.links),page
        continue
    english=page.startswith('en/');relative=page[3:] if english else page;lang='en' if english else 'zh-CN'
    canonical=[l['href'] for l in head.links if l.get('rel')=='canonical'];assert canonical==[page_url(config,relative,lang)],page
    pair={l['hreflang']:l['href'] for l in head.links if l.get('rel')=='alternate'}
    assert pair=={'zh-CN':page_url(config,relative),'en':page_url(config,relative,'en'),'x-default':page_url(config,relative)},page
    assert head.meta['og:url']==canonical[0] and head.meta['og:title']==head.title
    assert head.meta['og:description']==head.meta['description']
    structured=json.loads(''.join(head.structured));assert structured['@context']=='https://schema.org'
    nodes=structured['@graph'];assert {n['@type'] for n in nodes} >= {'Person','WebSite'}
    assert nodes[0]['name']=='Eli' and nodes[-1]['url']==canonical[0] and nodes[-1]['inLanguage']==lang
    assert not any(k in n for n in nodes for k in ['aggregateRating','review','award','worksFor']),page
    # No visible redesign: compare the body to the last saved full public build.
    prior=(ROOT/'evidence/english-version/release/public'/page).read_text()
    assert prior.split('<body>',1)[1]==f.read_text().split('<body>',1)[1],('Body changed',page)
assert len(pages)==84
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls=[x.text for x in ET.parse(ROOT/'evidence/seo-foundation/sitemap-candidate.xml').findall('.//s:loc',ns)]
assert len(urls)==82 and len(set(urls))==82
assert not any('404.html' in url or '?' in url for url in urls)
assert not (DIST/'sitemap.xml').exists(),'No live sitemap while index disabled'
assert (DIST/'robots.txt').read_text()=='User-agent: *\nDisallow: /\n'
# Domain-switch dry run: exercise metadata/sitemap functions without modifying config or enabling the site.
future=dict(config,base_url='https://www.eliai.cn/',indexing_enabled=True)
profile,projects,images=load_content(ROOT);en_profile,en_projects=english_content(ROOT,profile,projects)
for lang,pro,items in [('zh-CN',profile,projects),('en',en_profile,en_projects)]:
    mapping={p['id']:p for p in items}
    for path in ['index.html','about.html','records.html','cases/p36.html']:
        data=metadata(future,pro,mapping,path,lang)
        assert 'http://[REDACTED_HOST]' not in data['head'] and data['robots']=='index,follow'
    assert metadata(future,pro,mapping,'404.html',lang)['robots']=='noindex,nofollow'
assert b'https://www.eliai.cn/' in sitemap(future,pages)
result={'html_pages':84,'unique_titles':len(titles),'unique_descriptions':len(descriptions),'paired_hreflang':'PASS','self_canonical':'PASS','structured_data':'82 valid JSON graphs','candidate_sitemap_urls':82,'indexing':'DISABLED','body_unchanged':'PASS','future_domain_dry_run':'PASS'}
(ROOT/'evidence/seo-foundation/checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
