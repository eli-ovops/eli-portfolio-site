set -eu
python3 - <<'REMOTE'
from pathlib import Path
import tarfile,hashlib,json,os,subprocess
release='20261007-132028'
package=Path('/root/portfolio-'+release+'.tar.gz')
assert hashlib.sha256(package.read_bytes()).hexdigest()=='8217e20da86164f5748faf72b42786c787c518eb5f039f9ed4713194d29961a5'
base=Path('/srv/eli-sites/portfolio');target=base/'releases'/release
assert not target.exists()
conf=Path('/etc/nginx/sites-available/erp-trial'); original=conf.read_bytes()
assert b'/sites/portfolio' not in original
assert not (base/'public').exists()
backup=Path('/srv/eli-sites/backups')/release;backup.mkdir(parents=True,exist_ok=False)
(backup/'erp-trial.conf').write_bytes(original)
with tarfile.open(package) as t:
 members=t.getmembers()
 for m in members:
  assert m.isfile() and not m.pax_headers and not m.name.startswith('/') and '..' not in Path(m.name).parts
  assert not any(x.startswith('.') or x=='__MACOSX' for x in Path(m.name).parts)
 assert 'index.html' in [m.name for m in members]
 target.mkdir(parents=True,exist_ok=False)
 for m in members:
  p=target/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read());p.chmod(0o644)
for p in [base,target,*[p for p in target.rglob('*') if p.is_dir()]]:p.chmod(0o755)
os.symlink(str(target),str(base/'public-next'));os.replace(base/'public-next',base/'public')
route=' location = /sites/portfolio { return 302 /sites/portfolio/; }\n location ^~ /sites/portfolio/ {\n  alias /srv/eli-sites/portfolio/public/;\n  index index.html;\n  autoindex off;\n  add_header X-Content-Type-Options nosniff always;\n  add_header Referrer-Policy strict-origin-when-cross-origin always;\n  error_page 404 /sites/portfolio/404.html;\n }\n'
text=original.decode();assert text.rstrip().endswith('}')
updated=text[:text.rfind('}')]+route+'}\n'
assert conf.read_bytes()==original
conf.write_text(updated)
result=subprocess.run(['nginx','-t'],capture_output=True,text=True)
print(result.stdout,result.stderr)
if result.returncode:
 conf.write_bytes(original)
 raise RuntimeError('nginx validation failed; original config restored; no reload')
subprocess.run(['systemctl','reload','nginx'],check=True)
receipt={'release':release,'root':str(target),'previous_public':None,'backup':str(backup/'erp-trial.conf'),'package_sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'nginx':'test passed; reloaded','files':len(members)}
(base/'deployment-'+release+'.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
REMOTE
