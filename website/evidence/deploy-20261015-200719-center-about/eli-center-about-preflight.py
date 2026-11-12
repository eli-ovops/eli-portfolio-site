from pathlib import Path
import subprocess,json,hashlib,ast
R=Path('/Users/USER/Documents/原点向量/个人网站/website'); E=Path('/tmp/eli-center-about-evidence-path.txt').read_text(); E=Path(E)
SSH=['ssh','-F','/dev/null','-i','/Users/USER/.ssh/erp-jdcloud-trial-20261005','-o','IdentityAgent=none','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/Volumes/EXTERNAL/ERP试跑-20261005/known_hosts','-o','ForwardAgent=no','-o','ForwardX11=no','-o','ClearAllForwardings=yes','-o','ConnectTimeout=10','root@[REDACTED_HOST]']
base=json.loads((R/'evidence/https-index-launch-20261015/manifest.json').read_text())
script='expected='+repr(base['file_hashes'])+'\n'+r'''
from pathlib import Path
import hashlib,subprocess,json,shutil,os
root=Path('/srv/eli-sites/portfolio');current=(root/'domain-current').resolve();assert str(current)=='/srv/eli-sites/portfolio/domain-releases/20261015-183949-https-index'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(current/n)==h for n,h in expected.items()),'Live release drift'
conf=Path('/etc/nginx/sites-available/portfolio-domain-pending');erp=Path('/etc/nginx/sites-available/erp-trial');assert '/srv/eli-sites/portfolio/domain-current' in conf.read_text()
ps=subprocess.run(['ps','-eo','args'],capture_output=True,text=True).stdout
concurrent=[x for x in ps.splitlines() if '/srv/eli-sites/portfolio' in x and any(k in x for k in ['tar -','mv -T','rsync ','npm run build'])]
assert not concurrent,'Concurrent release process'
ng=subprocess.run(['nginx','-t'],capture_output=True,text=True);assert ng.returncode==0
states={s:subprocess.run(['systemctl','is-active',s],capture_output=True,text=True).stdout.strip() for s in ['nginx','erp-trial','mysql','redis-server']};assert all(v=='active' for v in states.values())
print(json.dumps({'hostname':subprocess.run(['hostname'],capture_output=True,text=True).stdout.strip(),'previous':str(current),'public':str((root/'public').resolve()),'configs':{str(p):sha(p) for p in [conf,erp]},'previous_files_verified':len(expected),'free_bytes':shutil.disk_usage(root).free,'services':states,'concurrent_release':False,'nginx_test':ng.stderr.strip()}))
'''
ast.parse(script);(E/'preflight.remote.py').write_text(script)
x=subprocess.run(SSH+['python3 -'],input=script,capture_output=True,text=True,timeout=45);(E/'preflight.stderr.txt').write_text(x.stderr)
if x.returncode:print(x.stderr[-1500:]);print(x.stdout[-1000:]);raise SystemExit(x.returncode)
data=json.loads(x.stdout);(E/'preflight.json').write_text(json.dumps(data,indent=2));print(json.dumps(data))
(E/'ssh-options.json').write_text(json.dumps(SSH))
