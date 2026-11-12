from pathlib import Path
import hashlib,json,subprocess,urllib.request,shutil,socket
root=Path('/srv/eli-sites/portfolio');public=root/'public'
assert socket.gethostname()=='lavm-zm3gcu3m6m','Unexpected host'
assert public.is_symlink(),'Portfolio entry is not the expected symlink'
old=public.resolve();assert old.parent==root/'releases','Unexpected release location'
config=Path('/etc/nginx/sites-available/erp-trial')
assert 'alias /srv/eli-sites/portfolio/public/;' in config.read_text(),'Unexpected portfolio route'
services={s:subprocess.run(['systemctl','is-active','--quiet',s]).returncode==0 for s in ['nginx','erp-trial','mysql','redis-server']}
assert all(services.values()),'Unhealthy baseline'
http={}
for path in ['/login','/mobile/','/sites/portfolio/records.html']:
 with urllib.request.urlopen('http://127.0.0.1'+path,timeout=15) as response:
  http[path]=response.status
  if 'portfolio' in path:assert b'<meta name="robots" content="noindex,nofollow">' in response.read()
old_hashes={}
for f in sorted(old.rglob('*')):
 assert not f.is_symlink(),'Unexpected indirect release file'
 if f.is_file():old_hashes[f.relative_to(old).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
usage=shutil.disk_usage(root);assert usage.free>250*1024*1024,'Insufficient space'
print(json.dumps({'status':'PREFLIGHT_PASS','previous':str(old),'previous_files':old_hashes,'nginx_sha256':hashlib.sha256(config.read_bytes()).hexdigest(),'services':services,'http':http,'free_bytes':usage.free,'hostname':socket.gethostname()}))
