from pathlib import Path
import tarfile,hashlib,json,os,urllib.request
release='20261007-142029'
base=Path('/srv/eli-sites/portfolio');previous=Path('/srv/eli-sites/portfolio/releases/20261007-134331')
assert (base/'public').resolve()==previous, 'Active version changed; do not overwrite'
package=Path('/root/portfolio-'+release+'.tar.gz')
assert hashlib.sha256(package.read_bytes()).hexdigest()=='5d4be3845f0f493085f8cb09731d6267900c88b5002ea193c7d889381eb3d92c'
target=base/'releases'/release
assert not target.exists()
with tarfile.open(package) as t:
 members=t.getmembers()
 for m in members:
  assert m.isfile() and not m.pax_headers and not m.name.startswith('/') and '..' not in Path(m.name).parts
  assert not any(x.startswith('.') or x=='__MACOSX' for x in Path(m.name).parts)
 assert {'index.html','en/index.html'} <= {m.name for m in members}
 target.mkdir(parents=True,exist_ok=False)
 for m in members:
  p=target/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read());p.chmod(0o644)
for p in [target,*[p for p in target.rglob('*') if p.is_dir()]]:p.chmod(0o755)
assert (base/'public').resolve()==previous
os.symlink(str(target),str(base/'public-next'));os.replace(base/'public-next',base/'public')
with urllib.request.urlopen('http://127.0.0.1/sites/portfolio/health.json') as response:
 assert json.load(response)['release']==release
receipt={'release':release,'previous':str(previous),'directory':str(target),'files':len(members),'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'mechanism':'atomic static symlink; no Nginx changes or service restart'}
(base/('deployment-'+release+'.json')).write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
