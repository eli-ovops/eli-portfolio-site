from pathlib import Path
import ast,json,subprocess,sys
D=Path(__file__).resolve().parent;P=json.loads((D/'plan.json').read_text());B=json.loads((D/'preflight.json').read_text());SSH=json.loads((D/'ssh-args.json').read_text());mode=sys.argv[1]
assert P['publication_authorized'] is True
if mode=='upload':
 args=['scp']+SSH[1:-2]+[P['package'],'root@[REDACTED_HOST]:/root/portfolio-'+P['release']+'.tar.gz']
 r=subprocess.run(args,text=True,capture_output=True,timeout=100)
 (D/'upload-transport.json').write_text(json.dumps({'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2))
 assert r.returncode==0,r.stderr
 print('UPLOADED_ONCE');raise SystemExit
header=r'''
from pathlib import Path
from datetime import datetime,timezone
import os,json,hashlib,tarfile,urllib.request,subprocess,shutil
root=Path('/srv/eli-sites/portfolio');current=root/'domain-current';target=Path(P['target']);backup=root/'backups'/P['release']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def services():
 return {u:subprocess.check_output(['systemctl','show',u,'--property=ActiveState,MainPID'],text=True).strip() for u in B['services']}
def guard():
 assert current.is_symlink() and str(current.resolve())==P['previous'],'Current release drift'
 assert str((root/'public').resolve())==B['ip_public'],'IP preview drift'
 assert all(sha(Path(p))==h for p,h in B['enabled_config_hashes'].items()),'Configuration drift'
 assert all(sha(current/p)==h for p,h in B['hashes'].items()),'Current content drift'
 assert services()==B['services'],'Service states/PIDs drift'
'''
if mode=='validate':
 body=r'''
guard();assert not target.exists() and not backup.exists()
package=Path('/root/portfolio-'+P['release']+'.tar.gz');assert sha(package)==P['package_sha256']
with tarfile.open(package) as t:
 members=t.getmembers();assert len(members)==len(P['files']) and {m.name for m in members}==set(P['files'])
 assert all(m.isreg() and not m.pax_headers and not m.name.startswith('/') and not any(v.startswith('.') or v=='..' for v in Path(m.name).parts) for m in members)
 assert all(hashlib.sha256(t.extractfile(m).read()).hexdigest()==P['files'][m.name] for m in members)
 target.mkdir(mode=0o755)
 for m in members:
  f=target/m.name;f.parent.mkdir(parents=True,exist_ok=True,mode=0o755)
  with f.open('xb') as out:out.write(t.extractfile(m).read())
  os.chmod(f,0o644)
assert all(sha(target/p)==h for p,h in P['files'].items())
assert all(sha(target/p)==h for p,h in B['hashes'].items() if not p.endswith('.html') and p not in P['changed_non_html'])
backup.mkdir(mode=0o700)
(backup/'before.json').write_text(json.dumps(B,indent=2));shutil.copy2('/etc/nginx/sites-available/portfolio-domain-pending',backup/'portfolio-domain-pending.unchanged.conf')
result={'status':'VALIDATED_NOT_SWITCHED','target':str(target),'files':len(P['files']),'package_sha256':sha(package),'revision':P['revision'],'previous_retained':P['previous'],'configs_and_service_states_unchanged':True,'checked_at':datetime.now(timezone.utc).isoformat()}
(backup/'validation.json').write_text(json.dumps(dict(result,files_manifest=P['files']),indent=2));print(json.dumps(result,indent=2))
'''
elif mode=='publish':
 body=r'''
guard();v=json.loads((backup/'validation.json').read_text());assert v['status']=='VALIDATED_NOT_SWITCHED' and v['files_manifest']==P['files']
assert all(sha(target/p)==h for p,h in P['files'].items())
temp=root/('domain-current.next.'+P['release']);assert not temp.exists() and not temp.is_symlink();os.symlink(str(target),temp);os.replace(temp,current)
result={'revision':P['revision'],'previous_retained':P['previous'],'current':str(current.resolve()),'production_switches':1,'nginx_reload_count':0,'published_at':datetime.now(timezone.utc).isoformat()}
try:
 checks=['index.html','en/index.html','about.html','en/about.html','cases/p36.html','en/cases/p36.html','services/ai-agent.html','services/workflow-automation.html','services/fde-consulting.html','assets/page-version.js','sitemap.xml']
 for name in checks:
  with urllib.request.urlopen('https://www.eliai.cn/'+name,timeout=15) as response:
   assert response.status==200 and hashlib.sha256(response.read()).hexdigest()==P['files'][name],name
 assert all(sha(Path(p))==h for p,h in B['enabled_config_hashes'].items())
 assert str((root/'public').resolve())==B['ip_public']
 assert services()==B['services']
 assert all(sha(current/p)==h for p,h in P['files'].items())
 result.update(status='PUBLISHED_AND_SERVER_VERIFIED',server_public_hash_checks=len(checks),file_hashes_verified=len(P['files']),services_and_pids_unchanged=True,configs_and_ip_preview_unchanged=True)
except Exception as e:
 result.update(status='FAILED',error=str(e))
 if str(current.resolve())==str(target):
  rollback=root/('domain-current.rollback.'+P['release']);assert not rollback.exists() and not rollback.is_symlink();os.symlink(P['previous'],rollback);os.replace(rollback,current);result.update(status='FAILED_ROLLED_BACK',current=str(current.resolve()))
 else:result['status']='FAILED_CURRENT_CHANGED_EXTERNALLY'
(backup/'publish.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
'''
else:raise SystemExit('Unsupported mode')
code='P='+repr(P)+'\nB='+repr(B)+'\n'+header+body;ast.parse(code);(D/(mode+'.remote.py')).write_text(code)
r=subprocess.run(SSH,input=code,text=True,capture_output=True,timeout=90)
(D/(mode+'-transport.json')).write_text(json.dumps({'returncode':r.returncode,'stderr':r.stderr},indent=2))
if r.returncode:print(r.stdout);raise RuntimeError(r.stderr)
x=json.loads(r.stdout);(D/(mode+'.json')).write_text(json.dumps(x,indent=2));print(json.dumps(x,indent=2))
assert x['status']==('VALIDATED_NOT_SWITCHED' if mode=='validate' else 'PUBLISHED_AND_SERVER_VERIFIED')
