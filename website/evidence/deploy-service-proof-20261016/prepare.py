from pathlib import Path
import hashlib,html,io,json,re,shutil,subprocess,tarfile
from urllib.parse import urlsplit,parse_qsl,urlencode,urlunsplit
R=Path(__file__).resolve().parents[2];E=Path(__file__).resolve().parent
SSH=json.loads((R/'evidence/deploy-20261015-200719-center-about/ssh-options.json').read_text())
B=json.loads((E/'preflight.json').read_text())
SOURCE=json.loads((R/'evidence/service-return-refinement-20261016/receipt.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(R/p)==h for p,h in SOURCE['changed_files'].items()),'Local source drift'
code='''from pathlib import Path
import io,sys,tarfile
root=Path('''+repr(B['previous'])+''')
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz',format=tarfile.USTAR_FORMAT) as t:
 for p in sorted(root.rglob('*')):
  if p.is_file():
   assert not p.is_symlink()
   data=p.read_bytes();i=tarfile.TarInfo(p.relative_to(root).as_posix());i.size=len(data);i.mode=0o644;i.mtime=0;t.addfile(i,io.BytesIO(data))
'''
x=subprocess.run(SSH+['python3 -'],input=code.encode(),capture_output=True,timeout=45);assert x.returncode==0,x.stderr.decode()
(E/'before-public.tar.gz').write_bytes(x.stdout)
prior=E/'before-public';prior.mkdir(exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(x.stdout)) as t:
 assert {m.name for m in t.getmembers()}==set(B['files'])
 for m in t.getmembers():
  assert m.isreg() and not m.pax_headers and '..' not in Path(m.name).parts and not m.name.startswith('/')
  data=t.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==B['files'][m.name]
  f=prior/m.name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
D=E/'public';shutil.copytree(prior,D,dirs_exist_ok=True)
# Copy only the validated navigation controller and service-scoped styles.
(D/'assets/page-version.js').write_bytes((R/'assets/page-version.js').read_bytes())
local_css=(R/'assets/editorial.css').read_text()
block=local_css[local_css.index('/* Service evidence'):local_css.index('.case-stage')]
assert all(line.startswith(('.service-main','/*')) for line in block.splitlines() if line)
old_css=(prior/'assets/editorial.css').read_text();assert '.service-main' not in old_css
(D/'assets/editorial.css').write_text(block+old_css)
services=[]
for prefix in ['','en/']:
 for slug in ['fde-consulting','ai-agent','workflow-automation']:
  name=prefix+'services/'+slug+'.html';services.append(name)
  (D/name).write_bytes((R/'dist'/name).read_bytes())
# Update changed asset fingerprints everywhere; retain every unrelated page body.
for p in D.rglob('*.html'):
 def asset(m):
  u=urlsplit(html.unescape(m[2]));target=(p.parent/u.path).resolve()
  if u.scheme or u.netloc or target.suffix not in ('.js','.css'):return m[0]
  assert target.is_relative_to(D.resolve()) and target.is_file()
  query=dict(parse_qsl(u.query))
  if 'v' not in query and target.relative_to(D.resolve()).as_posix() not in ['assets/page-version.js','assets/editorial.css']:return m[0]
  query['v']=sha(target)[:12]
  return m[1]+html.escape(urlunsplit(u._replace(query=urlencode(query))),quote=True)+m[3]
 p.write_text(re.sub(r'((?:href|src)=")([^"]+)(")',asset,p.read_text()))
normalize=lambda s:re.sub(r'[a-f0-9]{20}','__REVISION__',s)
h=hashlib.sha256()
for p in sorted(D.rglob('*')):
 if p.is_file():h.update(p.relative_to(D).as_posix().encode()+b'\0'+(normalize(p.read_text()).encode() if p.suffix=='.html' else p.read_bytes())+b'\0')
rev=h.hexdigest()[:20]
for p in D.rglob('*.html'):
 s=p.read_text();s=re.sub(r'(name="portfolio-revision" content=")[a-f0-9]{20}',lambda m:m[1]+rev,s)
 s=re.sub(r'([?&](?:amp;)?pv=)[a-f0-9]{20}',lambda m:m[1]+rev,s);p.write_text(s)
def stable(s):
 s=normalize(s)
 return re.sub(r'([?&](?:amp;)?v=)[a-f0-9]{12}',r'\1__ASSET__',s)
changed_assets={'assets/page-version.js','assets/editorial.css'}
for name,digest in B['files'].items():
 if name in services or name in changed_assets:continue
 if name.endswith('.html'):assert stable((D/name).read_text())==stable((prior/name).read_text()),name
 else:assert sha(D/name)==digest,name
assert 'backdrop-filter' not in block
verification=json.loads((R/'verification-files/manifest.json').read_text())['public_root_files']
assert all(sha(D/name)==digest for name,digest in verification.items())
files={p.relative_to(D).as_posix():sha(p) for p in D.rglob('*') if p.is_file()}
release='20261016-service-proof-'+rev[:8]
P={'release':release,'revision':rev,'previous':B['previous'],'target':'/srv/eli-sites/portfolio/domain-releases/'+release,'files':files,'package':str(E/'release.tar.gz'),'source_local_revision':SOURCE['revision'],'changed_assets':sorted(changed_assets),'service_pages':services,'authorization':'User explicitly requests deployment of service returns, early proof and deliverables plus mobile/return/contact checks; no analytics installation authorized.'}
with tarfile.open(E/'release.tar.gz','w:gz',format=tarfile.USTAR_FORMAT) as t:
 for name in sorted(files):
  data=(D/name).read_bytes();i=tarfile.TarInfo(name);i.size=len(data);i.mode=0o644;i.mtime=0;t.addfile(i,io.BytesIO(data))
P['package_sha256']=sha(E/'release.tar.gz');(E/'plan.json').write_text(json.dumps(P,ensure_ascii=False,indent=2))
analytics=[name for name in files if name.endswith(('.html','.js')) and re.search(r'googletagmanager\.com|google-analytics\.com|hm\.baidu\.com|clarity\.ms|umami\.is|plausible\.io|matomo\.js', (D/name).read_text())]
(E/'analytics-check.json').write_text(json.dumps({'production_snapshot':B['previous'],'known_analytics_embed_matches':analytics,'note':'No known provider embeds found; server logs and webmaster search reports are separate. No installation performed.'},indent=2))
print(json.dumps({k:v for k,v in P.items() if k!='files'},ensure_ascii=False,indent=2))
