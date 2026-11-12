from pathlib import Path
import hashlib,json,subprocess,urllib.request
root=Path('/srv/eli-sites/portfolio');release='20261014-124659-customer-paths';target=root/'releases'/release
assert (root/'public').resolve()==target
backup=root/'backups'/release
old=json.loads((backup/'previous-release.json').read_text());previous=Path(old['previous'])
assert {p.relative_to(previous).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in previous.rglob('*') if p.is_file()}==old['files'],'Previous version changed'
config_hash=hashlib.sha256(Path('/etc/nginx/sites-available/erp-trial').read_bytes()).hexdigest()
assert config_hash=='f8feed3d72ef606d90674a633f73a9449a31a874197e823130ed9b3b9d213445'
services={s:subprocess.run(['systemctl','is-active','--quiet',s]).returncode==0 for s in ['nginx','erp-trial','mysql','redis-server']}
assert all(services.values())
http={}
for path in ['/login','/mobile/']:
    with urllib.request.urlopen('http://127.0.0.1'+path,timeout=15) as response:http[path]=response.status
print(json.dumps({'status':'REMOTE_POSTCHECK_PASS','target':str(target),'previous':str(previous),'previous_files_preserved':len(old['files']),'nginx_sha256':config_hash,'services':services,'erp_http':http,'scope':'ERP entry-page availability only; no login or business operations'}))
