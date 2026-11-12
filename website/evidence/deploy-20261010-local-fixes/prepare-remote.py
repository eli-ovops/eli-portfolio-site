from pathlib import Path
import hashlib,json,tarfile,shutil,os,subprocess
release='20261010-223517-portfolio-local-fixes'
expected_package='7e129d4d1ba3af4e6e07473c2fe6bcbef31b6138cd791ece75bf52476cfa30ca'
expected_previous='/srv/eli-sites/portfolio/releases/20261008-200047-technical-content'
root=Path('/srv/eli-sites/portfolio');public=root/'public'
assert public.is_symlink() and str(public.resolve())==expected_previous,'Current release changed'
config=Path('/etc/nginx/sites-available/erp-trial')
assert hashlib.sha256(config.read_bytes()).hexdigest()=='f8feed3d72ef606d90674a633f73a9449a31a874197e823130ed9b3b9d213445','Nginx config changed'
package=Path('/root/portfolio-'+release+'.tar.gz');manifest=Path('/root/portfolio-'+release+'.sha256')
assert hashlib.sha256(package.read_bytes()).hexdigest()==expected_package,'Upload hash mismatch'
expected={}
for line in manifest.read_text().splitlines():
 digest,name=line.split('  ',1);assert len(digest)==64 and name not in expected;expected[name]=digest
assert len(expected)==143 and 'index.html' in expected
allowed={'.html','.css','.js','.json','.txt','.svg','.png','.jpg','.jpeg','.webp','.woff2','.ttf','.ico','.gif'}
with tarfile.open(package) as archive:
 members=archive.getmembers();seen=set()
 for member in members:
  path=Path(member.name)
  assert member.isreg() and not member.pax_headers and not path.is_absolute()
  assert all(not part.startswith('.') and part!='..' for part in path.parts)
  assert member.name in expected and member.name not in seen
  assert path.suffix in allowed or member.name=='assets/social-icons/LICENSE.md'
  assert hashlib.sha256(archive.extractfile(member).read()).hexdigest()==expected[member.name]
  seen.add(member.name)
 assert seen==set(expected)
 target=root/'releases'/release;assert not target.exists()
 backup=root/'backups'/release;backup.mkdir(mode=0o700,parents=True,exist_ok=False)
 shutil.copyfile(config,backup/'nginx-erp-trial.conf');os.chmod(backup/'nginx-erp-trial.conf',0o600)
 old=public.resolve();old_hashes={}
 for f in sorted(old.rglob('*')):
  assert not f.is_symlink()
  if f.is_file():old_hashes[f.relative_to(old).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
 (backup/'previous-release.json').write_text(json.dumps({'previous':str(old),'files':old_hashes},indent=2))
 target.mkdir(mode=0o755)
 for member in members:
  destination=target/member.name;destination.parent.mkdir(mode=0o755,parents=True,exist_ok=True)
  with archive.extractfile(member) as source,destination.open('xb') as out:shutil.copyfileobj(source,out)
  os.chmod(destination,0o644)
actual={f.relative_to(target).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in target.rglob('*') if f.is_file()}
assert actual==expected,'Extracted file set/hash mismatch'
assert str(public.resolve())==expected_previous,'Concurrent deploy detected'
print(json.dumps({'status':'PREPARED_NOT_SWITCHED','release':release,'previous':expected_previous,'target':str(target),'backup':str(backup),'package_sha256':expected_package,'files_verified':len(actual)}))
