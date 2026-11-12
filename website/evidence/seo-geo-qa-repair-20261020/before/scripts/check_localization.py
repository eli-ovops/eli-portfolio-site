"""Regression checks for full English copy, shared assets and paired language routes."""
import json
import re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote, parse_qs
ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.hits=[]; self.refs=[]; self.switch=None; self.lang=None; self.revision=None; self.in_filing=False
    def handle_data(self, data):
        if self.in_filing and data.strip() == '浙ICP备2026044062号-2': return
        if re.search(r'[\u4e00-\u9fff]',data) and data.strip() != '中文': self.hits.append(data)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='a': self.in_filing=a.get('href')=='https://beian.miit.gov.cn/'
        if tag=='html': self.lang=a.get('lang')
        if tag=='meta' and a.get('name')=='portfolio-revision': self.revision=a.get('content')
        if 'language-switch' in a.get('class',''): self.switch=a.get('href')
        for k,v in attrs:
            if k in ('alt','aria-label','placeholder','content','title') and v and re.search(r'[\u4e00-\u9fff]',v): self.hits.append(v)
            if k in ('href','src') and v: self.refs.append(v)
            if k=='srcset' and v: self.refs.extend(part.strip().split()[0] for part in v.split(','))
    def handle_endtag(self, tag):
        if tag=='a': self.in_filing=False
checked=[]
for path in sorted((DIST/'en').rglob('*.html')):
    en=Page();en.feed(path.read_text());assert en.lang=='en';assert not en.hits,(path,en.hits)
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
config=json.loads((ROOT/'content/seo.json').read_text())
project_records=json.loads((ROOT/'content/projects.json').read_text())
expected=4+len(project_records)+len(config.get('service_pages',[]))
assert len(checked)==expected
result={'english_pages':len(checked),'chinese_pages':expected,'visitor_copy':'English; Chinese only in language switch and verified official ICP number','same_page_switches':'PASS','asset_and_srcset_paths':'PASS','project_translations':len(project_records)}
(ROOT/'evidence/english-version/localization-checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
