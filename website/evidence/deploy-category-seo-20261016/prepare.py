from pathlib import Path
import ast,hashlib,html,io,json,re,shutil,subprocess,tarfile
R=Path(__file__).resolve().parents[2]; E=Path(__file__).resolve().parent
SSH=json.loads((R/'evidence/deploy-20261015-200719-center-about/ssh-options.json').read_text())
BASE=json.loads((R/'evidence/search-platform-360-sogou-20261016/deployed-manifest.json').read_text())
SOURCE=json.loads((R/'evidence/category-seo-20261016/receipt.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(R/p)==h for p,h in SOURCE['changed_sources'].items()), 'Source changed since validated build'
code='''from pathlib import Path
import hashlib,json,shutil,subprocess
root=Path('/srv/eli-sites/portfolio'); current=root/'domain-current'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
actual={p.relative_to(current).as_posix():sha(p) for p in current.rglob('*') if p.is_file()}
assert not any(p.is_symlink() for p in current.rglob('*'))
configs={p:sha(Path(p)) for p in ['/etc/nginx/sites-available/portfolio-domain-pending','/etc/nginx/sites-available/erp-trial']}
print(json.dumps({'previous':str(current.resolve()),'files':actual,'configs':configs,'ip_public':str((root/'public').resolve()),'hostname':subprocess.check_output(['hostname'],text=True).strip(),'services':{s:subprocess.check_output(['systemctl','is-active',s],text=True).strip() for s in ['nginx','erp-trial','mysql','redis-server']},'free_bytes':shutil.disk_usage(root).free}))
'''
(E/'preflight.remote.py').write_text(code)
x=subprocess.run(SSH+['python3 -'],input=code,text=True,capture_output=True,timeout=45);assert x.returncode==0,x.stderr
before=json.loads(x.stdout); assert before['previous']==BASE['target'];assert before['files']==BASE['file_hashes'];assert before['hostname']=='lavm-zm3gcu3m6m';assert before['free_bytes']>1_000_000_000
(E/'preflight.json').write_text(json.dumps(before,indent=2))
# Download only the hash-verified public release as a read-only recovery snapshot.
download='''from pathlib import Path
import io,sys,tarfile
root=Path('''+repr(before['previous'])+''')
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz',format=tarfile.USTAR_FORMAT) as t:
 for p in sorted(root.rglob('*')):
  if p.is_file():
   assert not p.is_symlink()
   data=p.read_bytes(); info=tarfile.TarInfo(p.relative_to(root).as_posix());info.size=len(data);info.mode=0o644;info.mtime=0;t.addfile(info,io.BytesIO(data))
'''
x=subprocess.run(SSH+['python3 -'],input=download.encode(),capture_output=True,timeout=45);assert x.returncode==0,x.stderr.decode()
(E/'before-public.tar.gz').write_bytes(x.stdout)
prior=E/'before-public';assert not prior.exists();prior.mkdir()
with tarfile.open(fileobj=io.BytesIO(x.stdout)) as t:
 assert {m.name for m in t.getmembers()}==set(before['files'])
 for m in t.getmembers():
  assert m.isreg() and not m.pax_headers and '..' not in Path(m.name).parts and not m.name.startswith('/')
  data=t.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==before['files'][m.name]
  f=prior/m.name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
candidate=E/'public';assert not candidate.exists();shutil.copytree(prior,candidate)
# Precisely patch home SEO + the existing needs section; retain the production shell and scripts.
for path in ['index.html','en/index.html']:
 live=(prior/path).read_text();local=(R/'dist'/path).read_text()
 for pattern in [r'<title>.*?</title>',r'<meta name="description"[^>]*>',r'<meta (?:property|name)="(?:og:title|og:description|twitter:title|twitter:description)"[^>]*>',r'<script type="application/ld\+json">.*?</script>']:
  old=list(re.finditer(pattern,live,re.S));new=list(re.finditer(pattern,local,re.S));assert len(old)==len(new) and old
  for a,b in zip(old,new):live=live.replace(a[0],b[0],1)
 pattern=r'<section class="customer-topics".*?</section>'
 a=re.search(pattern,live,re.S);b=re.search(pattern,local,re.S);assert a and b
 live=live[:a.start()]+b[0]+live[a.end():]
 (candidate/path).write_text(live)
for path in SOURCE['new_service_urls_pending_release_and_submission']:
 relative=path.removeprefix('https://www.eliai.cn/');f=candidate/relative;assert not f.exists();f.parent.mkdir(parents=True,exist_ok=True)
 text=(R/'dist'/relative).read_text()
 # New pages consume the accepted production CSS/JS bytes, never unapproved local asset revisions.
 def asset_version(m):
  name=m[2].removeprefix('../');assert name in before['files'],name
  return m[1]+m[2]+'?v='+before['files'][name][:12]+m[3]
 text=re.sub(r'((?:href|src)=")((?:\.\./)?(?:assets/[^"?]+|styles\.css|motion\.css|app\.js|motion\.js))\?v=[^"<]+(")',asset_version,text)
 f.write_text(text)
for name in ['sitemap.xml','llms.txt']:(candidate/name).write_bytes((R/'dist'/name).read_bytes())
# A single consistent new revision across existing and new HTML, while preserving old bodies.
normalize=lambda s:re.sub(r'[a-f0-9]{20}', '__REVISION__',s)
digest=hashlib.sha256()
for p in sorted(candidate.rglob('*')):
 if p.is_file():
  rel=p.relative_to(candidate).as_posix();data=normalize(p.read_text()).encode() if p.suffix=='.html' else p.read_bytes();digest.update(rel.encode()+b'\0'+data+b'\0')
revision=digest.hexdigest()[:20]
for f in candidate.rglob('*.html'):
 s=f.read_text();s=re.sub(r'(name="portfolio-revision" content=")[a-f0-9]{20}',lambda m:m[1]+revision,s)
 s=re.sub(r'([?&](?:amp;)?pv=)[a-f0-9]{20}',lambda m:m[1]+revision,s);f.write_text(s)
for p,h in before['files'].items():
 if not p.endswith('.html') and p not in ['sitemap.xml','llms.txt']:assert sha(candidate/p)==h, p
 elif p.endswith('.html') and p not in ['index.html','en/index.html']:
  assert normalize((candidate/p).read_text())==normalize((prior/p).read_text()),p
verification=json.loads((R/'verification-files/manifest.json').read_text())['public_root_files'];assert all(sha(candidate/p)==h for p,h in verification.items())
files={p.relative_to(candidate).as_posix():sha(p) for p in candidate.rglob('*') if p.is_file()}
release='20261016-service-keywords-'+revision[:8]
plan={'release':release,'revision':revision,'previous':before['previous'],'target':'/srv/eli-sites/portfolio/domain-releases/'+release,'files':files,'source_local_revision':SOURCE['revision'],'new_pages':6,'preserved_assets':True,'authorization':'User 2026-10-16 explicitly requests service-keyword SEO publication, mobile/case return/contact verification and Bing submission; Baidu only as review/quota permit','package':str(E/'release.tar.gz')}
with tarfile.open(E/'release.tar.gz','w:gz',format=tarfile.USTAR_FORMAT) as t:
 for name in sorted(files):
  data=(candidate/name).read_bytes();info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;info.mtime=0;t.addfile(info,io.BytesIO(data))
plan['package_sha256']=sha(E/'release.tar.gz');(E/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
(E/'artifacts.md').write_text('All files in this directory are task-created retained deployment, recovery or acceptance evidence. before-public is the original public release; public is the scoped candidate. No source/private data or disposable files are in the release. preview.py is the local candidate preview runner. No cleanup authorized for recovery artifacts.\n')
print(json.dumps({k:v for k,v in plan.items() if k!='files'},ensure_ascii=False,indent=2))
