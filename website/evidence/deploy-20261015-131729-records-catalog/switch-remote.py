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
assert public.is_symlink() and str(public.resolve())==manifest['previous'],'Current release changed; no switch'
assert hashlib.sha256(config.read_bytes()).hexdigest()==manifest['nginx_sha256'],'Config changed; no switch'
assert hashes(target)==expected,'Prepared release differs; no switch'
assert hashes(Path(manifest['previous']))==manifest['previous_files'],'Previous release changed'
assert (backup/'previous-release.json').is_file()
for service in ['nginx','erp-trial','mysql','redis-server']:
 assert subprocess.run(['systemctl','is-active','--quiet',service]).returncode==0,service
for name in expected:
 if name.endswith('.html'):assert b'<meta name="robots" content="noindex,nofollow">' in (target/name).read_bytes()
link=root/('public.next.'+release);assert not link.exists() and not link.is_symlink()
os.symlink(str(target),link);os.replace(link,public)
assert public.resolve()==target
print(json.dumps({'status':'SWITCHED','release':release,'previous':manifest['previous'],'target':str(target),'files_verified':len(expected),'indexing':'DISABLED','switched_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
