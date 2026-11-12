from pathlib import Path
import hashlib,json,tarfile,shutil,os,subprocess,datetime,urllib.request
release='20261014-124659-customer-paths'
expected_package='237f8ffdb6b486410efb42155e27e9373cd705d72f297867831de891694a4673'
previous='/srv/eli-sites/portfolio/releases/20261014-110604-return-origin'
config_hash='f8feed3d72ef606d90674a633f73a9449a31a874197e823130ed9b3b9d213445'
root=Path('/srv/eli-sites/portfolio');public=root/'public';target=root/'releases'/release;backup=root/'backups'/release
config=Path('/etc/nginx/sites-available/erp-trial')
manifest=Path('/root/portfolio-'+release+'.sha256')
expected={}
for line in manifest.read_text().splitlines():
 digest,name=line.split('  ',1);assert len(digest)==64 and name not in expected;expected[name]=digest
assert len(expected)==144 and 'index.html' in expected and 'sitemap.xml' not in expected

assert public.is_symlink() and str(public.resolve())==previous,'Current changed; no switch'
assert hashlib.sha256(config.read_bytes()).hexdigest()==config_hash,'Config changed; no switch'
actual={f.relative_to(target).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in target.rglob('*') if f.is_file()}
assert actual==expected,'Prepared files changed; no switch'
assert (backup/'previous-release.json').is_file() and (backup/'nginx-erp-trial.conf').is_file()
for service in ['nginx','erp-trial','mysql','redis-server']:assert subprocess.run(['systemctl','is-active','--quiet',service]).returncode==0,service
for f in target.rglob('*.html'):assert '<meta name="robots" content="noindex,nofollow">' in f.read_text(),str(f)
link=root/('public.next.'+release);assert not link.exists() and not link.is_symlink()
os.symlink(str(target),link);os.replace(link,public)
assert public.resolve()==target
print(json.dumps({'status':'SWITCHED','release':release,'previous':previous,'target':str(public.resolve()),'switched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'nginx_sha256':config_hash,'nginx_config':'UNCHANGED','services':'UNCHANGED_ACTIVE','files_verified':len(actual),'indexing':'DISABLED'}))
