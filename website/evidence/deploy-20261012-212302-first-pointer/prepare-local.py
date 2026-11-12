"""This authorized static release only. Build, match accepted output, reproducible package."""
from pathlib import Path
import json, hashlib, subprocess, shutil, tarfile, io, gzip, stat
HERE=Path(__file__).resolve().parent
SITE=HERE.parents[1]
RELEASE='20261012-212302-first-pointer'
PREVIOUS='20261012-194514-return-zoom'
old=SITE/'evidence'/('deploy-'+PREVIOUS)
accepted=json.loads((SITE/'evidence/first-pointer-20261012/receipt.json').read_text())
assert accepted['status']=='LOCAL_ACCEPTED_NOT_PUBLISHED'
assert accepted['local_revision']=='374bf42e288f80f56bf7'
assert not (SITE/'.git').exists(), 'Git appeared; inspect current state before release'
results={}
for name,command in [('build',['npm','run','build']),('navigation',['node','scripts/check_navigation_version.cjs']),('first-pointer',['node','scripts/check_first_pointer.cjs']),('static',['python3','scripts/check.py']),('localization',['python3','scripts/check_localization.py']),('seo',['python3','scripts/check_seo.py'])]:
 run=subprocess.run(command,cwd=SITE,text=True,capture_output=True)
 results[name]={'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr}
 (HERE/'local-checks.json').write_text(json.dumps(results,indent=2))
 assert run.returncode==0, name
dist=SITE/'dist'
files={p.relative_to(dist).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dist.rglob('*')) if p.is_file()}
assert files==accepted['public_files'] and len(files)==144,'Output differs from accepted local version'
allowed={'.html','.css','.js','.json','.txt','.svg','.png','.jpg','.jpeg','.webp','.woff2','.ttf','.ico','.gif'}
raw=io.BytesIO()
with tarfile.open(fileobj=raw,mode='w',format=tarfile.USTAR_FORMAT) as archive:
 for name,digest in files.items():
  path=dist/name
  assert not path.is_symlink() and all(not part.startswith('.') and part!='..' for part in Path(name).parts)
  assert path.suffix in allowed or name=='assets/social-icons/LICENSE.md'
  data=path.read_bytes()
  if name.endswith('.html'):assert b'<meta name="robots" content="noindex,nofollow">' in data
  if name=='robots.txt':assert data==b'User-agent: *\nDisallow: /\n'
  info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;info.uid=info.gid=0;info.mtime=0
  archive.addfile(info,io.BytesIO(data))
payload=gzip.compress(raw.getvalue(),mtime=0)
package=HERE/('portfolio-'+RELEASE+'.tar.gz')
package.write_bytes(payload)
digest=hashlib.sha256(payload).hexdigest()
with tarfile.open(package) as archive:
 actual={}
 for member in archive.getmembers():
  assert member.isreg() and not member.pax_headers and not Path(member.name).is_absolute()
  actual[member.name]=hashlib.sha256(archive.extractfile(member).read()).hexdigest()
 assert actual==files
(HERE/'manifest.sha256').write_text(''.join(h+'  '+p+'\n' for p,h in files.items()))
(HERE/'package-manifest.json').write_text(json.dumps({'release':RELEASE,'content_revision':accepted['local_revision'],'archive_sha256':digest,'archive_bytes':len(payload),'file_hashes':files,'members':len(files),'format':'USTAR/gzip-mtime0; regular allowlisted files only'},indent=2))
for name in ['run-remote.py','preflight-remote.py','prepare-remote.py','switch-remote.py','postcheck-remote.py','check-public.py']:
 source=(old/name).read_text()
 # Replace the old previous release first, then the batch being superseded.
 source=source.replace('20261012-182317-reading-social',PREVIOUS)
 if name!='preflight-remote.py':
  source=source.replace("release='"+PREVIOUS+"'","release='"+RELEASE+"'")
 source=source.replace('1b6a855902f9ad2a1a5d6260912e8e6a12c1c529d908456ad94874c9d32a61bf',digest)
 (HERE/name).write_text(source)
for source,target in [(SITE/'site.yaml','before-site.yaml'),(SITE/'docs/\u4ea4\u4ed8\u4e0e\u9a8c\u8bc1.md','before-delivery.md'),(Path('/Users/USER/Documents/eli/PERSONAL_WEBSITE_HANDOFF_2026-10-10.md'),'before-handoff.md')]:
 shutil.copy2(source,HERE/target)
plan={'release':RELEASE,'previous':PREVIOUS,'owner':'01a123a8-16ae-76f0-85c9-8e017dd95758','authorization':'Current user: publish first-click, fast-return and image-zoom fixes; preserve visuals/motion; verify search/filter/back online; keep indexing disabled','target':'http://[REDACTED_HOST]/sites/portfolio/','content_revision':accepted['local_revision'],'expected_files':144,'source':'Accepted source/output hashes; non-Git portfolio, no package dependencies','boundary':'Isolated static portfolio release, private backup and atomic public symlink only. No Nginx/ERP/DB/DNS/HTTPS/ICP/automation/indexing change','infrastructure_contract':'Current user JDCloud117.72.148.45 guide and site.yaml take precedence over unrelated175.178.238.90 skill access details','routing':'ROUTING-2026-09-30-v3; no model setting changes; unavailable actual model fields UNKNOWN','rollback_target':'/srv/eli-sites/portfolio/releases/'+PREVIOUS,'abort_before_switch':'Current target, config, services, package/member hashes or noindex fail; preserve evidence, do not switch','checks':['accepted local output','strict SSH/current release','private backup and old hashes','safe archive and isolated extraction','single atomic symlink switch','remote/public hashes and noindex','real-browser fast filter/search/native+explicit back/image dialog']}
(HERE/'plan.json').write_text(json.dumps(plan,indent=2))
print(json.dumps({'status':'LOCAL_PACKAGE_PASS','release':RELEASE,'revision':accepted['local_revision'],'members':len(files),'archive_sha256':digest,'archive_bytes':len(payload),'checks':{k:v['exit_code'] for k,v in results.items()}},indent=2))
