from pathlib import Path
import hashlib,json,tarfile,shutil,os,subprocess,datetime,urllib.request
release='20261012-182317-reading-social'
expected_package='bd83bf65718cdcac3a69fb3af23437eca6675cb80b46b8481e6ca3a6d13f8cb8'
previous='/srv/eli-sites/portfolio/releases/20261012-143006-seo-geo'
config_hash='f8feed3d72ef606d90674a633f73a9449a31a874197e823130ed9b3b9d213445'
root=Path('/srv/eli-sites/portfolio');public=root/'public';target=root/'releases'/release;backup=root/'backups'/release
config=Path('/etc/nginx/sites-available/erp-trial')
manifest=Path('/root/portfolio-'+release+'.sha256')
expected={}
for line in manifest.read_text().splitlines():
 digest,name=line.split('  ',1);assert len(digest)==64 and name not in expected;expected[name]=digest
assert len(expected)==143 and 'index.html' in expected and 'sitemap.xml' not in expected

assert public.is_symlink() and str(public.resolve())==previous,'Current release changed'
assert hashlib.sha256(config.read_bytes()).hexdigest()==config_hash,'Config changed'
package=Path('/root/portfolio-'+release+'.tar.gz')
assert hashlib.sha256(package.read_bytes()).hexdigest()==expected_package,'Upload hash mismatch'
allowed={'.html','.css','.js','.json','.txt','.svg','.png','.jpg','.jpeg','.webp','.woff2','.ttf','.ico','.gif'}
with tarfile.open(package) as archive:
 members=archive.getmembers();seen=set()
 for member in members:
  path=Path(member.name)
  assert member.isreg() and not member.pax_headers and not path.is_absolute()
  assert all(not part.startswith('.') and part!='..' for part in path.parts)
  assert member.name in expected and member.name not in seen
  assert path.suffix in allowed or member.name=='assets/social-icons/LICENSE.md'
  data=archive.extractfile(member).read()
  assert hashlib.sha256(data).hexdigest()==expected[member.name]
  if path.suffix=='.html':assert b'<meta name="robots" content="noindex,nofollow">' in data
  if member.name=='robots.txt':assert data==b'User-agent: *\nDisallow: /\n'
  seen.add(member.name)
 assert seen==set(expected) and not target.exists()
 backup.mkdir(mode=0o700,parents=True,exist_ok=False)
 shutil.copyfile(config,backup/'nginx-erp-trial.conf');os.chmod(backup/'nginx-erp-trial.conf',0o600)
 old=public.resolve();old_hashes={}
 for f in sorted(old.rglob('*')):
  assert not f.is_symlink()
  if f.is_file():old_hashes[f.relative_to(old).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
 (backup/'previous-release.json').write_text(json.dumps({'previous':str(old),'files':old_hashes},indent=2))
 target.mkdir(mode=0o755)
 for member in members:
  destination=target/member.name;destination.parent.mkdir(mode=0o755,parents=True,exist_ok=True)
  with archive.extractfile(member) as source,destination.open('xb') as output:shutil.copyfileobj(source,output)
  os.chmod(destination,0o644)
actual={f.relative_to(target).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in target.rglob('*') if f.is_file()}
assert actual==expected and str(public.resolve())==previous
print(json.dumps({'status':'PREPARED_NOT_SWITCHED','release':release,'previous':previous,'target':str(target),'backup':str(backup),'files_verified':len(actual),'package_sha256':expected_package,'indexing':'DISABLED'}))
