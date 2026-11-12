from pathlib import Path
import zipfile,hashlib,json,os,subprocess
base=Path('/srv/eli-sites/portfolio')
archive=Path('/root/eliai-domain-ready.zip')
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='3b61c52e8ba65556581de2ebfb0daa3ab75ec6f0a9baccc5805c822d2db6e72f'
release='domain-prepared-20261007'
target=base/'domain-releases'/release
assert not target.exists(), 'Do not overwrite existing prepared domain release'
assert not (base/'domain-current').exists(), 'Domain target already exists; review required'
with zipfile.ZipFile(archive) as z:
 items=z.infolist()
 for item in items:
  assert not item.is_dir() and not item.filename.startswith('/') and '..' not in Path(item.filename).parts
  assert not any(x.startswith('.') or x=='__MACOSX' for x in Path(item.filename).parts)
  assert (item.external_attr>>16)&0o170000==0o100000
 assert len(items)==120 and 'index.html' in z.namelist() and 'en/index.html' in z.namelist()
 target.mkdir(parents=True,exist_ok=False)
 hashes={}
 for item in items:
  data=z.read(item.filename)
  if item.filename.endswith('.html'):
   assert b'content="noindex,nofollow"' in data
   assert b'http://[REDACTED_HOST]/sites/portfolio/' not in data
  p=target/item.filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);p.chmod(0o644)
  hashes[item.filename]=hashlib.sha256(data).hexdigest()
for directory in [target,*[p for p in target.rglob('*') if p.is_dir()]]:directory.chmod(0o755)
os.symlink(str(target),str(base/'domain-current'))
conf=Path('/etc/nginx/sites-available/portfolio-domain-pending')
assert not conf.exists()
conf.write_text('server {\n    listen 80;\n    server_name eliai.cn www.eliai.cn;\n    root /srv/eli-sites/portfolio/domain-current;\n    index index.html;\n    autoindex off;\n    add_header X-Content-Type-Options nosniff always;\n    add_header X-Robots-Tag "noindex, nofollow" always;\n    location / { try_files $uri $uri/ =404; }\n    location ~ /\\. { deny all; }\n    error_page 404 /404.html;\n}\n');conf.chmod(0o644)
# This file stays outside sites-enabled. Syntax check the candidate in isolation without starting it.
test_config=base/'domain-config-test.conf'
assert not test_config.exists()
test_config.write_text('events {}\nhttp { include /etc/nginx/mime.types; include '+str(conf)+'; }\n')
result=subprocess.run(['nginx','-t','-c',str(test_config)],capture_output=True,text=True)
print(result.stderr);assert result.returncode==0
assert not Path('/etc/nginx/sites-enabled/portfolio-domain-pending').exists()
assert (base/'public').resolve()==base/'releases/20261007-144516'
receipt={'domain':'eliai.cn','domain_root':str(target),'nginx_candidate':str(conf),'enabled':False,'DNS_modified':False,'public_release':'20261007-144516','files':hashes,'reason':'ICP filing not completed, confirmed by user'}
(base/'domain-prepared-20261007.json').write_text(json.dumps(receipt,indent=2));print(json.dumps({k:v for k,v in receipt.items() if k!='files'},indent=2))
