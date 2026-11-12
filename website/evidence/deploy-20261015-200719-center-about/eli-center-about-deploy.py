from pathlib import Path
import subprocess,json,sys,ast
R=Path('/Users/USER/Documents/原点向量/个人网站/website');E=Path(Path('/tmp/eli-center-about-evidence-path.txt').read_text());M=json.loads((E/'manifest.json').read_text());B=json.loads((E/'preflight.json').read_text());SSH=json.loads((E/'ssh-options.json').read_text());mode=sys.argv[1]
remote_package='/root/portfolio-'+M['release']+'.tar.gz'
if mode=='upload':
 args=['scp']+SSH[1:-1]+[M['package'],'root@[REDACTED_HOST]:'+remote_package]
 x=subprocess.run(args,capture_output=True,text=True,timeout=100);(E/'upload.stderr.txt').write_text(x.stderr);assert x.returncode==0,x.stderr[-1000:];print('UPLOADED '+str(M['bytes'])+' bytes');raise SystemExit()
H='M='+repr(M)+'\nB='+repr(B)+'\npackage_path='+repr(remote_package)+'\n'+r'''
from pathlib import Path
import json,hashlib,os,subprocess,tarfile,urllib.request,urllib.error,shutil
root=Path('/srv/eli-sites/portfolio');target=Path(M['target']);current=root/'domain-current'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guarded():
 assert {p:sha(Path(p)) for p in B['configs']}==B['configs'],'Concurrent config edit'
 assert str((root/'public').resolve())==B['public'],'IP preview target drift'
'''
if mode=='prepare':
 script=H+r'''
guarded();assert str(current.resolve())==M['previous'];assert not target.exists()
p=Path(package_path);assert sha(p)==M['sha256']
with tarfile.open(p) as t:
 seen=set()
 for m in t.getmembers():
  n=Path(m.name);assert m.isreg() and not m.pax_headers and not n.is_absolute() and all(not x.startswith('.') and x!='..' for x in n.parts)
  assert m.name in M['file_hashes'] and m.name not in seen;seen.add(m.name)
  assert hashlib.sha256(t.extractfile(m).read()).hexdigest()==M['file_hashes'][m.name]
 assert seen==set(M['file_hashes'])
 target.mkdir(mode=0o755)
 for m in t.getmembers():
  p=target/m.name;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as f:f.write(t.extractfile(m).read())
  os.chmod(p,0o644)
assert all(sha(target/n)==h for n,h in M['file_hashes'].items())
backup=root/'backups'/M['release'];backup.mkdir(mode=0o700)
(backup/'before.json').write_text(json.dumps(B,indent=2));(backup/'manifest.json').write_text(json.dumps(M,indent=2))
assert Path(M['previous']).is_dir()
print(json.dumps({'status':'PREPARED_NOT_SWITCHED','target':str(target),'files':len(M['file_hashes']),'package_sha256':sha(Path(package_path)),'previous_retained':M['previous'],'backup_record':str(backup),'free_bytes':shutil.disk_usage(root).free}))
'''
elif mode=='switch':
 script=H+r'''
guarded();assert str(current.resolve())==M['previous'] and current.is_symlink()
assert all(sha(target/n)==h for n,h in M['file_hashes'].items())
tmp=root/('domain-current.next.'+M['release']);assert not tmp.exists() and not tmp.is_symlink()
os.symlink(str(target),tmp);os.replace(tmp,current)
guarded();assert str(current.resolve())==M['target']
try:
 with urllib.request.urlopen('https://www.eliai.cn/index.html?deploy='+M['revision'],timeout=15) as v:
  assert v.status==200 and hashlib.sha256(v.read()).hexdigest()==M['file_hashes']['index.html']
except Exception:
 rollback=root/('domain-current.rollback.'+M['release']);os.symlink(M['previous'],rollback);os.replace(rollback,current);raise
print(json.dumps({'status':'SWITCHED_HEALTH_OK','target':str(current.resolve()),'previous_retained':M['previous'],'revision':M['revision'],'configs_unchanged':True,'nginx_reload':False}))
'''
elif mode=='verify':
 script=H+r'''
guarded();assert str(current.resolve())==M['target'];assert all(sha(target/n)==h for n,h in M['file_hashes'].items())
paths=['index.html','about.html','en/about.html','records.html','en/index.html','cases/p10.html','assets/content-layout.css','assets/depth-gallery.js','assets/screenshot-viewer.js','assets/office-workflow.svg','robots.txt','sitemap.xml','llms.txt']
checks=[]
for n in paths:
 with urllib.request.urlopen('https://www.eliai.cn/'+n+'?verify='+M['revision'],timeout=15) as v:
  assert hashlib.sha256(v.read()).hexdigest()==M['file_hashes'][n],n
  checks.append({'path':n,'status':v.status,'x_robots_tag':v.headers.get('X-Robots-Tag')})
assert (target/'robots.txt').read_text()=='User-agent: *\nAllow: /\nSitemap: https://www.eliai.cn/sitemap.xml\n'
for n in ['missing-test-page','content/profile.json','scripts/build.py','.git/config','assets/img17.jpg']:
 try:urllib.request.urlopen('https://www.eliai.cn/'+n,timeout=10);raise AssertionError('Unexpected exposed '+n)
 except urllib.error.HTTPError as ex:assert ex.code in [403,404],(n,ex.code)
services={s:subprocess.run(['systemctl','is-active',s],capture_output=True,text=True).stdout.strip() for s in B['services']};assert all(v=='active' for v in services.values())
for n in ['/login','/mobile/']:
 with urllib.request.urlopen('http://127.0.0.1'+n,timeout=10) as v:assert v.status==200
print(json.dumps({'status':'PASS','files_verified':len(M['file_hashes']),'https_paths':checks,'configs_unchanged':True,'IP_target_unchanged':True,'services':services,'ERP_static_login_paths':'200','no_service_restart':True,'previous_retained':M['previous']}))
'''
else:raise SystemExit('Invalid mode')
ast.parse(script);(E/(mode+'.remote.py')).write_text(script)
x=subprocess.run(SSH+['python3 -'],input=script,capture_output=True,text=True,timeout=75);(E/(mode+'.stderr.txt')).write_text(x.stderr)
if x.returncode:print(x.stderr[-1800:]);print(x.stdout[-1000:]);raise SystemExit(x.returncode)
d=json.loads(x.stdout);(E/(mode+'.json')).write_text(json.dumps(d,indent=2));print(json.dumps(d))
