from pathlib import Path
import hashlib,json,subprocess,urllib.request,shutil,socket
root=Path('/srv/eli-sites/portfolio');public=root/'public'
previous='/srv/eli-sites/portfolio/releases/20261014-124659-customer-paths'
assert socket.gethostname()=='lavm-zm3gcu3m6m','Unexpected host'
assert public.is_symlink() and str(public.resolve())==previous,'Current release changed; stop'
config=Path('/etc/nginx/sites-available/erp-trial')
assert 'alias /srv/eli-sites/portfolio/public/;' in config.read_text(),'Unexpected portfolio route'
services={s:subprocess.run(['systemctl','is-active','--quiet',s]).returncode==0 for s in ['nginx','erp-trial','mysql','redis-server']}
assert all(services.values()),'Service baseline is not healthy'
http={}
for path in ['/login','/mobile/','/sites/portfolio/','/sites/portfolio/about.html']:
    with urllib.request.urlopen('http://127.0.0.1'+path,timeout=15) as response:
        http[path]=response.status
        if path.startswith('/sites/portfolio/'):
            assert b'<meta name="robots" content="noindex,nofollow">' in response.read(),'Old site unexpectedly indexable'
usage=shutil.disk_usage(root)
assert usage.free>200*1024*1024,'Insufficient release space'
print(json.dumps({'status':'PREFLIGHT_PASS','hostname':socket.gethostname(),'previous':previous,'nginx_sha256':hashlib.sha256(config.read_bytes()).hexdigest(),'services':services,'http':http,'free_bytes':usage.free,'previous_files':len([p for p in public.resolve().rglob('*') if p.is_file()])}))
