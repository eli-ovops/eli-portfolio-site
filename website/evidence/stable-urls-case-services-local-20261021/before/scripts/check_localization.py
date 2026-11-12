"""Regression checks for full English copy, shared assets and paired language routes."""
import json
import re
import argparse
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote, parse_qs
from seo import load_config
ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
arguments=argparse.ArgumentParser(description=__doc__)
arguments.add_argument('--output', type=Path, default=ROOT/'evidence/english-version/localization-checks.json')
args=arguments.parse_args()
practice=json.loads((ROOT/'content/tutorial-practice.json').read_text())
config=load_config(ROOT)
class Page(HTMLParser):
    def __init__(self, allowed_practice_input=None):
        super().__init__(); self.hits=[]; self.refs=[]; self.switch=None; self.lang=None; self.revision=None; self.in_filing=False
        self.allowed_practice_input=allowed_practice_input; self.in_practice=False; self.allowed_practice_blocks=0
    def handle_data(self, data):
        if self.in_filing and data.strip() == '浙ICP备2026044062号-2': return
        # Only exact labelled translation/token examples may contain Chinese terms.
        # Chinese elsewhere, or altered exercise material, must still be flagged.
        if self.in_practice and self.allowed_practice_input is not None and data==self.allowed_practice_input:
            self.allowed_practice_blocks+=1
            return
        if re.search(r'[\u4e00-\u9fff]',data) and data.strip() != '中文': self.hits.append(data)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='a': self.in_filing=a.get('href')=='https://beian.miit.gov.cn/'
        if tag=='pre': self.in_practice='data-practice-input' in a
        if tag=='html': self.lang=a.get('lang')
        if tag=='meta' and a.get('name')=='portfolio-revision': self.revision=a.get('content')
        if 'language-switch' in a.get('class',''): self.switch=a.get('href')
        for k,v in attrs:
            if k in ('alt','aria-label','placeholder','content','title') and v and re.search(r'[\u4e00-\u9fff]',v): self.hits.append(v)
            if k in ('href','src') and v: self.refs.append(v)
            if k=='srcset' and v: self.refs.extend(part.strip().split()[0] for part in v.split(','))
    def handle_endtag(self, tag):
        if tag=='a': self.in_filing=False
        if tag=='pre': self.in_practice=False
checked=[]
for path in sorted((DIST/'en').rglob('*.html')):
    teaching_example=path.relative_to(DIST).as_posix() in {
        'en/articles/ai-translation-review.html','en/articles/what-is-token.html'}
    allowed=practice[path.stem]['input'][1] if teaching_example else None
    en=Page(allowed);en.feed(path.read_text());assert en.lang=='en';assert not en.hits,(path,en.hits)
    if teaching_example: assert en.allowed_practice_blocks==1
    counterpart=DIST/path.relative_to(DIST/'en')
    zh=Page();zh.feed(counterpart.read_text());assert zh.lang=='zh-CN'
    assert (path.parent/unquote(urlparse(en.switch).path)).resolve()==counterpart.resolve(),path
    assert (counterpart.parent/unquote(urlparse(zh.switch).path)).resolve()==path.resolve(),counterpart
    assert re.fullmatch(r'[a-f0-9]{20}', en.revision or '') and en.revision==zh.revision,path
    assert parse_qs(urlparse(en.switch).query).get('pv')==[en.revision],path
    assert parse_qs(urlparse(zh.switch).query).get('pv')==[zh.revision],counterpart
    for ref in en.refs:
        u=urlparse(ref)
        if u.scheme or u.netloc or not u.path:continue
        assert (path.parent/unquote(u.path)).is_file(),(path,ref)
    checked.append(path.relative_to(DIST).as_posix())
project_records=json.loads((ROOT/'content/projects.json').read_text())
routes={'index.html','about.html','records.html','404.html','articles.html'}
routes.update('cases/'+p['id'].lower()+'.html' for p in project_records)
routes.update('services/'+s['slug']+'.html' for s in config.get('service_pages',[]))
routes.update('articles/'+a['slug']+'.html' for a in config['articles']['en'])
assert set(checked)=={'en/'+p for p in routes}
result={'english_pages':len(checked),'chinese_pages':len(routes),'visitor_copy':'English; Chinese only in language switch, verified official ICP number and exact labelled translation/token examples','same_page_switches':'PASS','asset_and_srcset_paths':'PASS','project_translations':len(project_records),'article_translations':len(config['articles']['en']),'allowed_teaching_examples':2}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
