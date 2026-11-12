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
assert public.resolve()==target and hashes(target)==expected
assert hashes(Path(manifest['previous']))==manifest['previous_files'],'Previous release changed'
assert hashlib.sha256(config.read_bytes()).hexdigest()==manifest['nginx_sha256']
services={s:subprocess.run(['systemctl','is-active','--quiet',s]).returncode==0 for s in ['nginx','erp-trial','mysql','redis-server']}
assert all(services.values())
print(json.dumps({'status':'REMOTE_POSTCHECK_PASS','release':release,'files_verified':len(expected),'previous_files_preserved':len(manifest['previous_files']),'nginx_config':'UNCHANGED','services':services,'indexing':'DISABLED'}))
