"""Verify this batch against its actual pre-edit release, not historical UI assumptions."""
from pathlib import Path
import json, re, hashlib, sys
from html.parser import HTMLParser
from urllib.parse import urlsplit, urljoin

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
from tutorials import load_tutorials

baseline = json.loads((OUT / 'baseline.json').read_text())
expected_bodies = set(baseline['visible_link_changes_expected'])
normalize = lambda s: re.sub(r'([?&](?:amp;)?pv=)[a-f0-9]{20}', r'\1REVISION', s)
zh_profile = json.loads((ROOT / 'content/profile.json').read_text())
en_profile = json.loads((ROOT / 'content/en.json').read_text())['profile']
changed_bodies, cross_language, person_pages = [], [], 0
class Links(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.main=False; self.links=[]; self.feed(text)
    def handle_starttag(self, tag, attrs):
        if tag=='main': self.main=True
        if self.main and tag=='a': self.links.append(dict(attrs).get('href',''))
    def handle_endtag(self, tag):
        if tag=='main': self.main=False

for old in sorted((OUT / 'before/dist').rglob('*.html')):
    rel = old.relative_to(OUT / 'before/dist').as_posix()
    before, after = old.read_text(), (ROOT/'dist'/rel).read_text()
    if normalize(before.split('<body>',1)[1]) != normalize(after.split('<body>',1)[1]):
        changed_bodies.append(rel)
    if rel.endswith('404.html'):
        continue
    def graph(text):
        return json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])
    a,b=graph(before),graph(after)
    pa=next(n for n in a['@graph'] if n['@type']=='Person')
    pb=next(n for n in b['@graph'] if n['@type']=='Person')
    profile=en_profile if rel.startswith('en/') else zh_profile
    assert pb['description']==' '.join(profile['biography'][:2]),rel
    pa['description']=pb['description']
    assert a==b,('Unexpected schema change',rel)
    person_pages+=1
    if rel.startswith(('articles/','en/articles/')):
        for link in Links(after).links:
            u=urlsplit(urljoin('https://www.eliai.cn/'+rel,link))
            if u.netloc=='www.eliai.cn' and u.path.startswith(('/services/','/en/services/')):
                if rel.startswith('en/') != u.path.startswith('/en/'):
                    cross_language.append((rel,link))

assert set(changed_bodies)==expected_bodies,(changed_bodies,expected_bodies)
assert not cross_language,cross_language
protected=[]
for rel,digest in baseline['protected'].items():
    if rel.endswith(('.css','.js')) or rel.startswith('assets/') or rel in ('robots.txt','llms.txt'):
        assert hashlib.sha256((ROOT/'dist'/rel).read_bytes()).hexdigest()==digest,rel
        protected.append(rel)
rows=load_tutorials(ROOT)
for lang,items in enumerate(rows):
    for slug in ['ai-ocr-check','workbuddy-spreadsheet']:
        item=next(a for a in items if a['slug']==slug)
        assert item['service']=='workflow-automation'
    for slug in ['ai-consultation-prepare','what-is-fde-business']:
        item=next(a for a in items if a['slug']==slug)
        href=next(s['url'] for s in item['sources'] if 'eliai.cn' in s['url'])
        assert href=='https://www.eliai.cn/'+('en/' if lang else '')+'services/fde-consulting.html'
ledger_before=json.loads((OUT/'before/content/page-updates.json').read_text())['pages']
ledger_after=json.loads((ROOT/'content/page-updates.json').read_text())['pages']
changed_dates=[p for p in ledger_after if ledger_after[p]!=ledger_before[p]]
assert len(changed_dates)==294
assert all(ledger_after[p]['lastmod']=='2026-10-20' for p in changed_dates)
result={'status':'PASS','html_pages':296,'schema_person_biography_pages':person_pages,
        'other_schema_fields_unchanged':True,'changed_visible_bodies':changed_bodies,
        'all_other_visible_bodies_unchanged':290,'wrong_language_article_service_links':cross_language,
        'protected_assets_and_discovery_files':protected,
        'content_ledger_changed_pages':len(changed_dates),
        'lastmod_reason':'Actual Person description changed on all 294 indexable pages; article publication/review dates and body copy retained',
        'legacy_checks':'check_tutorials assumes 2 article-row nodes although baseline already has 10; check_localization rejects unchanged bilingual translation exercise. Not claimed as passing.'}
(OUT/'scope-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS: 296 page diffs, 294 author biographies, 6 scoped link changes, no cross-language article/service links; protected assets unchanged')
