from pathlib import Path
import json,subprocess,hashlib,ast,sys
R=Path(__file__).resolve().parents[2];E=Path(__file__).resolve().parent;P=json.loads((E/'plan.json').read_text());BASE=json.loads(Path(P['previous_manifest']).read_text());OLD=R/'evidence/deploy-20261015-200719-center-about';B=json.loads((OLD/'preflight.json').read_text());SSH=json.loads((OLD/'ssh-options.json').read_text())
def remote(name,body):
 code='P='+repr(P)+'\nBASE='+repr(BASE)+'\nB='+repr(B)+'\n'+body;ast.parse(code);(E/(name+'.remote.py')).write_text(code)
 x=subprocess.run(SSH+['python3 -'],input=code,text=True,capture_output=True,timeout=60);(E/(name+'.stderr.txt')).write_text(x.stderr)
 if x.returncode:print(x.stderr[-1600:]);print(x.stdout[-500:]);raise SystemExit(x.returncode)
 d=json.loads(x.stdout);(E/(name+'.json')).write_text(json.dumps(d,indent=2));print(json.dumps(d));return d
HEADER='''from pathlib import Path
import os,json,hashlib,shutil,subprocess,tarfile,urllib.request
root=Path('/srv/eli-sites/portfolio');current=root/'domain-current'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guard():
 assert {p:sha(Path(p)) for p in B['configs']}==B['configs']
 assert str((root/'public').resolve())==B['public']
'''
mode=sys.argv[1]
if mode=='preflight':
 remote(mode,HEADER+'''
guard();assert str(current.resolve())==P['previous']
assert all(sha(current/n)==h for n,h in BASE['file_hashes'].items())
assert all(not (current/n).exists() for n in P['files'])
print(json.dumps({'status':'PREFLIGHT_PASS','previous':str(current.resolve()),'files_verified':len(BASE['file_hashes']),'configs_unchanged':True,'free_bytes':shutil.disk_usage(root).free}))
''')
elif mode=='upload':
 assert (E/'preflight.json').exists()
 x=subprocess.run(['scp']+SSH[1:-1]+[P['package'],'root@[REDACTED_HOST]:/root/portfolio-'+P['release']+'.tar.gz'],capture_output=True,text=True,timeout=45);assert x.returncode==0,x.stderr[-1000:];print('UPLOAD_PASS')
elif mode=='publish':
 remote(mode,HEADER+'''
guard();assert str(current.resolve())==P['previous'];prior=Path(P['previous']);target=Path(P['target']);assert not target.exists()
assert all(sha(prior/n)==h for n,h in BASE['file_hashes'].items())
package=Path('/root/portfolio-'+P['release']+'.tar.gz');assert sha(package)==P['package_sha256']
with tarfile.open(package) as t:
 assert set(m.name for m in t.getmembers())==set(P['files'])
 assert all(m.isreg() and not m.pax_headers and len(Path(m.name).parts)==1 for m in t.getmembers())
 assert all(hashlib.sha256(t.extractfile(m).read()).hexdigest()==P['files'][m.name] for m in t.getmembers())
 shutil.copytree(prior,target,symlinks=False)
 for m in t.getmembers():
  q=target/m.name
  with q.open('xb') as f:f.write(t.extractfile(m).read())
  os.chmod(q,0o644)
assert all(sha(target/n)==h for n,h in BASE['file_hashes'].items())
assert all(sha(target/n)==h for n,h in P['files'].items())
backup=root/'backups'/P['release'];backup.mkdir(mode=0o700);(backup/'before.json').write_text(json.dumps({'previous':P['previous'],'files':BASE['file_hashes'],'configs':B['configs']},indent=2))
tmp=root/('domain-current.next.'+P['release']);assert not tmp.exists() and not tmp.is_symlink();os.symlink(str(target),tmp);os.replace(tmp,current)
try:
 guard()
 for n,h in P['files'].items():
  with urllib.request.urlopen('https://www.eliai.cn/'+n,timeout=15) as v:assert v.status==200 and hashlib.sha256(v.read()).hexdigest()==h
except Exception:
 q=root/('domain-current.rollback.'+P['release']);os.symlink(P['previous'],q);os.replace(q,current);raise
print(json.dumps({'status':'VERIFICATION_FILES_PUBLISHED','release':P['release'],'previous_retained':P['previous'],'ui_files_unchanged':len(BASE['file_hashes']),'new_verification_files':len(P['files']),'no_config_or_service_change':True,'ui_revision':P['ui_revision']}))
''')
else:raise SystemExit('bad mode')
