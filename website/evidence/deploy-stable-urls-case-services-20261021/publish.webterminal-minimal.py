P={'release': '20261021-stable-urls-cc132dc0', 'revision': 'cc132dc0e7da5cecf41d', 'target': '/srv/eli-sites/portfolio/domain-releases/20261021-stable-urls-cc132dc0', 'previous': '/srv/eli-sites/portfolio/domain-releases/20261020-industry-expansion-4bc544a5', 'candidate_digest': 'b826b5f70249c14d429dfe848d75523c8cb50f187f0b49bd24d01b616c220525', 'public_checks': ['index.html', 'en/index.html', 'cases/p09.html', 'cases/p10.html', 'cases/p36.html', 'en/cases/p09.html', 'en/cases/p10.html', 'en/cases/p36.html', 'services/ai-agent.html', 'en/services/ai-agent.html', 'services/workflow-automation.html', 'en/services/workflow-automation.html', 'about.html', 'en/about.html', 'assets/page-version.js', 'sitemap.xml', 'robots.txt', 'llms.txt', 'google0fc37373bc2d604d.html', 'BingSiteAuth.xml', 'yandex_56b4e9c66008d8fa.html', 'baidu_verify_codeva-UabAhVS0s3.html', 'sogousiteverification.txt', 'ByteDanceVerify.html']}
from pathlib import Path
import os,json,hashlib,shutil,base64,re,html,subprocess,urllib.request
from urllib.parse import urlsplit,parse_qsl,urlencode,urlunsplit
from datetime import datetime,timezone
root=Path('/srv/eli-sites/portfolio'); current=root/'domain-current'; previous=Path(P['previous']); target=Path(P['target']); backup=root/'backups'/P['release']
sha=lambda b:hashlib.sha256(b).hexdigest()
def manifest(folder):
 assert not any(p.is_symlink() for p in folder.rglob('*'))
 return {p.relative_to(folder).as_posix():sha(p.read_bytes()) for p in folder.rglob('*') if p.is_file()}
manifest_sha=lambda v:sha(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
assert subprocess.check_output(['hostname'],text=True).strip()=='lavm-zm3gcu3m6m'
B=json.loads((backup/'before.json').read_text());V=json.loads((backup/'validation.json').read_text())
assert V['status']=='VALIDATED_NOT_SWITCHED' and V['digest']==P['candidate_digest']
assert str(current.resolve())==P['previous'] and manifest(previous)==B['files']
assert manifest(target)==V['files'];assert all(sha(Path(p).read_bytes())==h for p,h in B['configs'].items())
assert str((root/'public').resolve())==B['ip_public']
assert not (backup/'publish.json').exists()
temp=root/('domain-current.next.'+P['release']);assert not temp.exists() and not temp.is_symlink()
os.symlink(str(target),temp);os.replace(temp,current)
try:
 for route in P['public_checks']:
  with urllib.request.urlopen('https://www.eliai.cn/'+route,timeout=15) as response:assert response.status==200 and sha(response.read())==V['files'][route],route
 assert all(sha(Path(p).read_bytes())==h for p,h in B['configs'].items())
 assert str((root/'public').resolve())==B['ip_public']
 services={s:subprocess.check_output(['systemctl','is-active',s],text=True).strip() for s in B['services']};assert services==B['services']
except Exception:
 rollback=root/('domain-current.rollback.'+P['release']);assert not rollback.exists() and not rollback.is_symlink();os.symlink(P['previous'],rollback);os.replace(rollback,current);raise
receipt={'status':'PUBLISHED','revision':P['revision'],'current':str(current.resolve()),'previous_retained':P['previous'],'files_verified':len(V['files']),'manifest_digest':P['candidate_digest'],'public_checks':len(P['public_checks']),'services':services,'configs_and_ip_preview':'UNCHANGED','published_at':datetime.now(timezone.utc).isoformat(),'carrier':'owner-authenticated JDCloud WebTerminal SSH session; no authentication/security changes'}
(backup/'publish.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt,sort_keys=True))
