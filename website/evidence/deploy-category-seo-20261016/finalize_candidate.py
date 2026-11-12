from pathlib import Path
from urllib.parse import urlparse,parse_qsl,urlencode,urlunparse
import hashlib,html,io,json,re,tarfile
E=Path(__file__).resolve().parent;D=E/'public';P=json.loads((E/'plan.json').read_text());B=json.loads((E/'preflight.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p in D.rglob('services/*.html'):
 def change(m):
  u=urlparse(html.unescape(m[2]));f=(p.parent/u.path).resolve()
  if u.scheme or u.netloc or f.suffix not in ('.css','.js'):return m[0]
  name=f.relative_to(D.resolve()).as_posix();assert name in B['files']
  q=dict(parse_qsl(u.query));q['v']=B['files'][name][:12]
  return m[1]+html.escape(urlunparse(u._replace(query=urlencode(q))),quote=True)+m[3]
 p.write_text(re.sub(r'((?:href|src)=")([^"]+)(")',change,p.read_text()))
normalize=lambda s:re.sub(r'[a-f0-9]{20}', '__REVISION__',s)
h=hashlib.sha256()
for p in sorted(D.rglob('*')):
 if p.is_file():h.update(p.relative_to(D).as_posix().encode()+b'\0'+(normalize(p.read_text()).encode() if p.suffix=='.html' else p.read_bytes())+b'\0')
rev=h.hexdigest()[:20]
for p in D.rglob('*.html'):
 s=p.read_text();s=re.sub(r'(name="portfolio-revision" content=")[a-f0-9]{20}',lambda m:m[1]+rev,s);s=re.sub(r'([?&](?:amp;)?pv=)[a-f0-9]{20}',lambda m:m[1]+rev,s);p.write_text(s)
P.update(revision=rev,release='20261016-service-keywords-'+rev[:8]);P['target']='/srv/eli-sites/portfolio/domain-releases/'+P['release'];P['files']={p.relative_to(D).as_posix():sha(p) for p in D.rglob('*') if p.is_file()}
with tarfile.open(E/'release.tar.gz','w:gz',format=tarfile.USTAR_FORMAT) as t:
 for name in sorted(P['files']):
  data=(D/name).read_bytes();i=tarfile.TarInfo(name);i.size=len(data);i.mode=0o644;i.mtime=0;t.addfile(i,io.BytesIO(data))
P['package_sha256']=sha(E/'release.tar.gz');(E/'plan.json').write_text(json.dumps(P,ensure_ascii=False,indent=2));print('Final scoped revision:',rev)
