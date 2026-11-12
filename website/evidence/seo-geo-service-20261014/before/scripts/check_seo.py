"""Focused regression checks for bilingual metadata and indexing safeguards."""
import argparse
import json
import re
from tempfile import TemporaryDirectory
from pathlib import Path
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
from urllib.parse import urlparse, unquote
from seo import load_config, page_url, metadata, sitemap, write_discovery
from content import load_content
from localization import english_content
ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/'dist'
arguments=argparse.ArgumentParser(description=__doc__)
arguments.add_argument('--baseline', type=Path, help='HTML snapshot for this specific batch; never compare against an old release')
arguments.add_argument('--allow-about-body-change', action='store_true', help='Approved About-only layout revision; other page bodies must stay identical')
arguments.add_argument('--output', type=Path, default=ROOT/'evidence/seo-foundation/checks.json')
args=arguments.parse_args()
class Head(HTMLParser):
    def __init__(self):
        super().__init__();self.meta={};self.links=[];self.title='';self.structured=[];self.in_title=False;self.in_json=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta':self.meta[a.get('name') or a.get('property') or a.get('http-equiv')]=a.get('content')
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
with TemporaryDirectory(prefix='portfolio-seo-check-') as temporary:
    fixture=Path(temporary);(fixture/'content').mkdir()
    for base in [config['base_url'],'http://www.eliai.cn/','https://127.0.0.1/','https://localhost/']:
        (fixture/'content/seo.json').write_text(json.dumps(dict(config,base_url=base,indexing_enabled=True)))
        try:
            load_config(fixture)
        except ValueError:
            pass
        else:
            raise AssertionError('Unsafe indexing config accepted: '+base)
    (fixture/'content/seo.json').write_text(json.dumps(dict(config,base_url='https://www.eliai.cn/',indexing_enabled=True)))
    assert load_config(fixture)['indexing_enabled'] is True
titles=set();descriptions=set();pages={}
for f in DIST.rglob('*.html'):
    page=f.relative_to(DIST).as_posix();head=Head();head.feed(f.read_text());pages[page]=head
    assert head.title and head.title not in titles,('Duplicate title',page);titles.add(head.title)
    assert head.meta.get('description') and head.meta['description'] not in descriptions,('Duplicate description',page);descriptions.add(head.meta['description'])
    assert head.meta['robots']=='noindex,nofollow',page
    assert head.meta['content-language']==('en' if page.startswith('en/') else 'zh-CN'),page
    assert head.meta['author']=='Eli',page
    if args.baseline:
        prior=(args.baseline/page).read_text().split('<body>',1)[1]
        current=f.read_text().split('<body>',1)[1]
        is_about=page in ('about.html','en/about.html')
        if not (is_about and args.allow_about_body_change):
            if is_about:
                current=re.sub(r'  <section class="technology-section" id="questions".*?</section>\n','',current,flags=re.S)
            assert prior==current,('Unexpected body change outside approved About scope',page)
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
    socials=json.loads((ROOT/'content/social-links.json').read_text())
    assert nodes[0]['sameAs']==[s['url'] for s in socials],page
    assert all(url in f.read_text().split('<body>',1)[1] for url in nodes[0]['sameAs']),page
    if relative=='records.html':
        collection=next(n for n in nodes if n['@type']=='ItemList')
        assert collection['numberOfItems']==38 and len(collection['itemListElement'])==38
        for item in collection['itemListElement']:
            assert item['name'] in f.read_text() and 'cases/' + item['url'].rsplit('/',1)[1] in f.read_text(),page
    if relative.startswith('cases/'):
        breadcrumb=next(n for n in nodes if n['@type']=='BreadcrumbList')
        assert breadcrumb['itemListElement'][0]['item']==page_url(config,'records.html',lang)
        assert breadcrumb['itemListElement'][-1]['item']==canonical[0]
        if relative=='cases/p36.html' and 'id="qa"' in f.read_text():
            assert ('not real support records' if english else '非真实客服记录') in head.meta['description']
    if 'og:image' in head.meta:
        image=head.meta['og:image'].removeprefix(config['base_url'])
        assert (DIST/image).is_file() and ('../' + image) in f.read_text(),page
        assert head.meta['twitter:image']==head.meta['og:image'] and head.meta['og:image:alt'],page
    assert not any(k in n for n in nodes for k in ['aggregateRating','review','award','worksFor']),page
    if relative=='about.html':
        for item in config['questions']:
            assert item[lang]['question'] in f.read_text() and item[lang]['answer'] in f.read_text(),page
        if args.allow_about_body_change:
            assert f.read_text().count('<details class="about-question"')==len(config['questions'])
            assert f.read_text().count('<h4>')==6,'The six-step workflow must remain'
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
body_scope=('PASS: About-only revision; other 82 bodies identical' if args.allow_about_body_change else 'PASS: only About questions added') if args.baseline else 'Not compared; no batch baseline supplied'
result={'html_pages':84,'unique_titles':len(titles),'unique_descriptions':len(descriptions),'paired_hreflang':'PASS','self_canonical':'PASS','structured_data':'82 valid JSON graphs','same_as_existing_profiles':'PASS','project_lists':'2 x 38','case_breadcrumbs':76,'visible_bilingual_questions':'PASS','share_images':'Existing visitor images only','candidate_sitemap_urls':82,'indexing':'DISABLED','body_scope':body_scope,'future_domain_dry_run':'PASS'}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
