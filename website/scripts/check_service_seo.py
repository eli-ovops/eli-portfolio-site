"""Check service intent, crawl paths, honest schema and unchanged presentation assets."""
import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
EVIDENCE = ROOT / 'evidence/category-seo-20261016'
config = json.loads((ROOT / 'content/seo.json').read_text())
items = config['service_pages']
assert {s['slug'] for s in items} == {'fde-consulting', 'ai-agent', 'workflow-automation'}

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.h1=0; self.text=[]; self.json=[]; self.in_json=False
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='a': self.links.append(a.get('href',''))
        if tag=='h1': self.h1+=1
        if tag=='script' and a.get('type')=='application/ld+json': self.in_json=True
    def handle_endtag(self, tag):
        if tag=='script': self.in_json=False
    def handle_data(self, data):
        (self.json if self.in_json else self.text).append(data)

routes=[]
for lang in ('zh-CN','en'):
    prefix='en/' if lang=='en' else ''
    home=Page(); home.feed((DIST/prefix/'index.html').read_text())
    # All three topics have real, crawlable HTML links, not click-only controls.
    assert {urlparse(u).path for u in home.links} >= {'services/'+s['slug']+'.html' for s in items}
    for item in items:
        path=prefix+'services/'+item['slug']+'.html'; f=DIST/path
        source=f.read_text(); page=Page(); page.feed(source)
        assert not re.search(r'<a data-nav="[^"]+"[^>]*aria-current="page"',source)
        text=item[lang]; visible=' '.join(page.text)
        assert page.h1==1 and text['heading'] in visible
        graph=json.loads(''.join(page.json))['@graph']
        service=next(n for n in graph if n['@type']=='Service')
        assert service['name'] in visible and service['description'] in visible
        assert service['url']==config['base_url']+path
        faq=next(n for n in graph if n['@type']=='FAQPage')
        assert len(faq['mainEntity'])==len(text['faqs'])
        for node,(question,answer) in zip(faq['mainEntity'],text['faqs']):
            assert node['name']==question and node['acceptedAnswer']['text']==answer
            assert question in visible and answer in visible
        assert not any(key in node for node in graph for key in ('aggregateRating','offers','award','review'))
        links={urlparse(u).path for u in page.links}
        assert '../about.html' in links
        assert {'../cases/'+pid.lower()+'.html' for pid in item['projects']} <= links
        assert {s['slug']+'.html' for s in items if s!=item} <= links
        # Core text, case evidence and consultation are available without JavaScript.
        for section in text['sections']:
            assert section['title'] in visible
            assert all(p in visible for p in section['paragraphs'])
        routes.append(path)

before=json.loads((EVIDENCE/'before-hashes.json').read_text())
preserved=[p for p in before if p.endswith(('.css','.js'))]
for p in preserved:
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==before[p],('Presentation changed',p)

# Only release query parameters may differ on these existing page bodies.
for old in (EVIDENCE/'before/dist').rglob('*.html'):
    relative=old.relative_to(EVIDENCE/'before/dist')
    if relative.as_posix() in ('index.html','en/index.html'): continue
    normalize=lambda s: re.sub(r'([?&](?:amp;)?pv=)[a-f0-9]{20}',r'\1REVISION',s.split('<body>',1)[1])
    assert normalize(old.read_text())==normalize((DIST/relative).read_text()),('Existing body changed',relative)

result={'service_pages':routes,'schema_matches_visible_copy':'PASS','crawlable_internal_links':'PASS',
        'existing_case_and_about_bodies':'PASS for scoped snapshots; release query normalized',
        'presentation_assets_unchanged':preserved,'indexing_enabled':config['indexing_enabled'],
        'deployment':'NOT DEPLOYED','keyword_rankings':'NOT CLAIMED'}
(EVIDENCE/'service-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
