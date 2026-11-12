from pathlib import Path
import ast,json,subprocess,sys
R=Path(__file__).resolve().parents[2];E=Path(__file__).resolve().parent;P=json.loads((E/'plan.json').read_text());B=json.loads((E/'preflight.json').read_text());SSH=json.loads((R/'evidence/deploy-20261015-200719-center-about/ssh-options.json').read_text());mode=sys.argv[1]
HEADER='''from pathlib import Path
import os,json,hashlib,tarfile,urllib.request,subprocess
root=Path('/srv/eli-sites/portfolio'); current=root/'domain-current';target=Path(P['target'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def guard():
 assert str(current.resolve())==P['previous']
 assert str((root/'public').resolve())==B['ip_public']
 assert all(sha(Path(p))==h for p,h in B['configs'].items())
 assert all(sha(Path(P['previous'])/p)==h for p,h in B['files'].items())
'''
if mode=='upload':
 x=subprocess.run(['scp']+SSH[1:-1]+[P['package'],'root@[REDACTED_HOST]:/root/portfolio-'+P['release']+'.tar.gz'],capture_output=True,text=True,timeout=60);assert x.returncode==0,x.stderr;print('UPLOAD_PASS');raise SystemExit
if mode=='validate':
 body='''guard();assert not target.exists()
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
assert all(sha(target/p)==h for p,h in B['files'].items() if not p.endswith('.html') and p not in P['changed_assets'])
backup=root/'backups'/P['release'];backup.mkdir(mode=0o700)
(backup/'before.json').write_text(json.dumps(B,indent=2));(backup/'validation.json').write_text(json.dumps({'status':'VALIDATED','revision':P['revision'],'files':P['files']},indent=2))
print(json.dumps({'status':'VALIDATED','target':str(target),'files':len(P['files']),'unrelated_assets_unchanged':True,'previous_retained':P['previous'],'no_switch_yet':True}))
'''
elif mode=='publish':
 body='''guard()
v=json.loads((root/'backups'/P['release']/'validation.json').read_text());assert v['status']=='VALIDATED' and v['files']==P['files']
assert all(sha(target/p)==h for p,h in P['files'].items())
temp=root/('domain-current.next.'+P['release']);assert not temp.exists() and not temp.is_symlink();os.symlink(str(target),temp);os.replace(temp,current)
try:
 for name in ['index.html','services/fde-consulting.html','services/ai-agent.html','services/workflow-automation.html','en/services/fde-consulting.html','en/services/ai-agent.html','en/services/workflow-automation.html','sitemap.xml','robots.txt','google0fc37373bc2d604d.html','BingSiteAuth.xml','yandex_56b4e9c66008d8fa.html','baidu_verify_codeva-UabAhVS0s3.html','sogousiteverification.txt','about.html','en/index.html','assets/depth-gallery.js','assets/stacked-gallery.css','assets/office-workflow.svg','ByteDanceVerify.html','articles.html','en/articles.html','articles/inventory-reconciliation.html','en/articles/inventory-reconciliation.html','articles/enterprise-knowledge-base.html','en/articles/enterprise-knowledge-base.html','assets/article-library.js','assets/articles.css','llms.txt']:
  with urllib.request.urlopen('https://www.eliai.cn/'+name,timeout=15) as response:
   assert response.status==200 and hashlib.sha256(response.read()).hexdigest()==P['files'][name],name
 assert all(sha(Path(p))==h for p,h in B['configs'].items())
 assert str((root/'public').resolve())==B['ip_public']
 services={s:subprocess.check_output(['systemctl','is-active',s],text=True).strip() for s in B['services']}
 assert services==B['services']
except Exception:
 rollback=root/('domain-current.rollback.'+P['release']);os.symlink(P['previous'],rollback);os.replace(rollback,current);raise
print(json.dumps({'status':'PUBLISHED','revision':P['revision'],'current':str(current.resolve()),'previous_retained':P['previous'],'public_hashes_checked':29,'services':services,'configs_and_ip_preview':'UNCHANGED'}))
'''
else:raise SystemExit('Unknown mode')
code='P='+repr(P)+'\nB='+repr(B)+'\n'+HEADER+body;ast.parse(code);(E/(mode+'.remote.py')).write_text(code)
x=subprocess.run(SSH+['python3 -'],input=code,text=True,capture_output=True,timeout=90);(E/(mode+'.stderr.txt')).write_text(x.stderr)
if x.returncode:print(x.stderr[-1600:]);print(x.stdout[-800:]);raise SystemExit(x.returncode)
data=json.loads(x.stdout);(E/(mode+'.json')).write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))
