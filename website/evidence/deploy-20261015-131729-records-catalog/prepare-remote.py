from pathlib import Path
import hashlib,json,tarfile,shutil,os,subprocess,datetime,socket
assert socket.gethostname()=='lavm-zm3gcu3m6m'
release='20261015-131729-records-catalog'
manifest_file=Path('/root/portfolio-'+release+'.json')
assert hashlib.sha256(manifest_file.read_bytes()).hexdigest()=='ae5f8488cfac0b93b3c7f565616785992b75b76e63e9e97043f1afd034490143'
manifest=json.loads(manifest_file.read_text());expected=manifest['file_hashes']
root=Path('/srv/eli-sites/portfolio');public=root/'public';target=root/'releases'/release;backup=root/'backups'/release
config=Path('/etc/nginx/sites-available/erp-trial')
def hashes(directory):
 result={}
 for f in directory.rglob('*'):
  assert not f.is_symlink()
  if f.is_file():result[f.relative_to(directory).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
 return result
assert public.is_symlink() and str(public.resolve())==manifest['previous'],'Current release changed'
assert hashlib.sha256(config.read_bytes()).hexdigest()==manifest['nginx_sha256'],'Config changed'
assert not target.exists() and not backup.exists(),'Release already exists; inspect rather than retry'
package=Path('/root/portfolio-'+release+'.tar.gz')
assert hashlib.sha256(package.read_bytes()).hexdigest()==manifest['archive_sha256'],'Package hash mismatch'
assert hashes(Path(manifest['previous']))==manifest['previous_files'],'Previous release changed'
with tarfile.open(package) as archive:
 members=archive.getmembers();seen=set()
 for member in members:
  path=Path(member.name)
  assert member.isreg() and not member.pax_headers and not path.is_absolute()
  assert all(not part.startswith('.') and part!='..' for part in path.parts)
  assert member.name in expected and member.name not in seen
  data=archive.extractfile(member).read()
  assert hashlib.sha256(data).hexdigest()==expected[member.name]
  if member.name.endswith('.html'):assert b'<meta name="robots" content="noindex,nofollow">' in data
  if member.name=='robots.txt':assert data==b'User-agent: *\nDisallow: /\n'
  seen.add(member.name)
 assert seen==set(expected) and 'sitemap.xml' not in seen
 backup.mkdir(mode=0o700,parents=True)
 shutil.copyfile(config,backup/'nginx-erp-trial.conf');os.chmod(backup/'nginx-erp-trial.conf',0o600)
 (backup/'previous-release.json').write_text(json.dumps({'previous':manifest['previous'],'files':manifest['previous_files']},indent=2))
 target.mkdir(mode=0o755)
 for member in members:
  destination=target/member.name;destination.parent.mkdir(mode=0o755,parents=True,exist_ok=True)
  with archive.extractfile(member) as source,destination.open('xb') as output:shutil.copyfileobj(source,output)
  os.chmod(destination,0o644)
assert hashes(target)==expected and str(public.resolve())==manifest['previous']
print(json.dumps({'status':'PREPARED_NOT_SWITCHED','release':release,'target':str(target),'previous':manifest['previous'],'files_verified':len(expected),'package_sha256':manifest['archive_sha256']}))
