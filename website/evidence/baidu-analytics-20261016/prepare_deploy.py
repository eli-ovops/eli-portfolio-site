from pathlib import Path
import hashlib,io,json,re,shutil,subprocess,sys,tarfile
R=Path(__file__).resolve().parents[2];E=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'scripts'))
from analytics import markup
SSH=json.loads((R/'evidence/deploy-20261015-200719-center-about/ssh-options.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
code=(R/'evidence/deploy-category-seo-20261016/preflight.remote.py').read_text()
x=subprocess.run(SSH+['python3 -'],input=code,text=True,capture_output=True,timeout=45);assert x.returncode==0,x.stderr
B=json.loads(x.stdout);prior_manifest=json.loads((R/'evidence/deploy-service-proof-20261016/deployed-manifest.json').read_text())
assert B['previous']==prior_manifest['target'] and B['files']==prior_manifest['file_hashes'],'Production drift'
assert B['hostname']=='lavm-zm3gcu3m6m' and B['free_bytes']>1_000_000_000 and all(v=='active' for v in B['services'].values())
(E/'preflight.json').write_text(json.dumps(B,indent=2))
prior=R/'evidence/deploy-service-proof-20261016/public'
assert {p.relative_to(prior).as_posix():sha(p) for p in prior.rglob('*') if p.is_file()}==B['files']
D=E/'public';shutil.copytree(prior,D)
for name in ['assets/site-analytics.js','assets/site-analytics.css']:(D/name).write_bytes((R/name).read_bytes())
normalize=lambda s:re.sub(r'[a-f0-9]{20}','__REVISION__',s)
for p in D.rglob('*.html'):
 if 'portfolio-revision' not in p.read_text():continue
 name=p.relative_to(D).as_posix();base='../'*name.count('/');lang='en' if name.startswith('en/') else 'zh-CN'
 head,body=markup(R,base,lang);old=p.read_text();s=old.replace('</head>',head+'\n</head>').replace('</footer>',body+'\n</footer>')
 assert s.replace(head+'\n','').replace(body+'\n','')==old
 p.write_text(s)
m=json.loads((D/'asset-manifest.json').read_text());m=sorted(set(m)|{'assets/site-analytics.js','assets/site-analytics.css'});(D/'asset-manifest.json').write_text(json.dumps(m,indent=2))
h=hashlib.sha256()
for p in sorted(D.rglob('*')):
 if p.is_file():h.update(p.relative_to(D).as_posix().encode()+b'\0'+(normalize(p.read_text()).encode() if p.suffix=='.html' else p.read_bytes())+b'\0')
rev=h.hexdigest()[:20]
for p in D.rglob('*.html'):
 s=p.read_text();s=re.sub(r'(name="portfolio-revision" content=")[a-f0-9]{20}',lambda m:m[1]+rev,s);s=re.sub(r'([?&](?:amp;)?pv=)[a-f0-9]{20}',lambda m:m[1]+rev,s);p.write_text(s)
for name,digest in B['files'].items():
 if not name.endswith('.html') and name!='asset-manifest.json':assert sha(D/name)==digest,name
files={p.relative_to(D).as_posix():sha(p) for p in D.rglob('*') if p.is_file()}
release='20261016-baidu-analytics-'+rev[:8]
P={'release':release,'revision':rev,'previous':B['previous'],'target':'/srv/eli-sites/portfolio/domain-releases/'+release,'files':files,'package':str(E/'release.tar.gz'),'changed_assets':['assets/site-analytics.js','assets/site-analytics.css','asset-manifest.json'],'authorization':'User explicitly requests Baidu analytics for views, sources and consultation clicks, preserving visuals/motion; user personally logged in and confirmed site creation.'}
with tarfile.open(E/'release.tar.gz','w:gz',format=tarfile.USTAR_FORMAT) as t:
 for name in sorted(files):
  data=(D/name).read_bytes();i=tarfile.TarInfo(name);i.size=len(data);i.mode=0o644;i.mtime=0;t.addfile(i,io.BytesIO(data))
P['package_sha256']=sha(E/'release.tar.gz');(E/'plan.json').write_text(json.dumps(P,ensure_ascii=False,indent=2))
s=(R/'evidence/deploy-service-proof-20261016/deploy.py').read_text();s=s.replace("'public_hashes_checked':14","'public_hashes_checked':14");(E/'deploy.py').write_text(s)
s=(R/'evidence/deploy-service-proof-20261016/check_candidate.py').read_text();s=s.replace("'production_styles_and_scripts':'Only service-scoped CSS and unified navigation changed'","'production_styles_and_scripts':'Original bytes retained; only analytics added'");(E/'check_candidate.py').write_text(s)
(E/'artifacts.md').write_text('Retained task evidence: public candidate and release archive, plan/preflight/validation/publication receipts, analytics source notes, SDK fetch and browser screenshots/network summaries. Prior release retained remotely and hash-verified prior public snapshot remains in deploy-service-proof-20261016/public. No cleanup or media changes.\n')
print(json.dumps({k:v for k,v in P.items() if k!='files'},ensure_ascii=False,indent=2))
