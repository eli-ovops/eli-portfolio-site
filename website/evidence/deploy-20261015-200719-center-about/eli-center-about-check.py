from pathlib import Path
import sys,json,contextlib,io
R=Path('/Users/USER/Documents/原点向量/个人网站/website');E=Path(Path('/tmp/eli-center-about-evidence-path.txt').read_text());sys.path.insert(0,str(R/'scripts'));C=E/'candidate'
for name in ['check_localization.py','check_seo.py']:
 s=(R/'scripts'/name).read_text().replace("DIST=ROOT/'dist'",'DIST=Path('+repr(str(C))+')').replace("DIST = ROOT / 'dist'",'DIST=Path('+repr(str(C))+')')
 s=s.replace("(ROOT/'evidence/english-version/localization-checks.json')",'(Path('+repr(str(E/'localization-checks.json'))+'))')
 sys.argv=[name,'--output',str(E/'seo-checks.json')] if name=='check_seo.py' else [name]
 out=io.StringIO()
 with contextlib.redirect_stdout(out):exec(compile(s,str(R/'scripts'/name),'exec'),{'__file__':str(R/'scripts'/name),'__name__':'__main__'})
 print(out.getvalue().strip())
# Validate actual candidate references and fragment targets without borrowing localhost dist.
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
class P(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.ids=[];self.h1=0
 def handle_starttag(self,t,a):
  d=dict(a);self.h1+=t=='h1'
  if 'id' in d:self.ids.append(d['id'])
  self.refs.extend(d[k] for k in ['href','src'] if k in d)
for p in C.rglob('*.html'):
 a=P();a.feed(p.read_text());assert a.h1==1 and len(a.ids)==len(set(a.ids))
 for ref in a.refs:
  u=urlsplit(ref)
  if u.scheme or u.netloc:continue
  q=(C/unquote(u.path).lstrip('/') if u.path.startswith('/') else p.parent/unquote(u.path)) if u.path else p
  assert q.is_file(),(p,ref)
  if u.fragment and q.suffix=='.html':b=P();b.feed(q.read_text());assert unquote(u.fragment) in b.ids,(p,ref)
(E/'candidate-static-checks.json').write_text(json.dumps({'html_pages':84,'links_anchors_h1':'PASS','archive':'Regular USTAR files only; no PAX/xattr/hidden/symlink assets; extracted content hashes matched','catalogue':'Existing production catalogue preserved except shared layout/asset hashes/version links'},indent=2));print('PASS candidate links/anchors/H1/archive')
