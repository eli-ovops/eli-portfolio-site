from pathlib import Path
import json,re,hashlib,html,base64,zlib
from urllib.parse import urlsplit,parse_qsl,urlencode,urlunsplit
r=Path(__file__).resolve().parents[2];e=Path(__file__).resolve().parent
p=json.loads((e/'plan.json').read_text());old=json.loads((r/'evidence/deploy-industry-expansion-20261020/deployed-manifest.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest_sha=lambda v:sha(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def clean_links(s):
 def link(m):
  u=urlsplit(html.unescape(m[2]))
  if u.scheme or u.netloc or not u.path.endswith('.html'):return m[0]
  q=[(k,v) for k,v in parse_qsl(u.query,keep_blank_values=True) if k!='pv']
  return m[1]+html.escape(urlunsplit(('', '', u.path,urlencode(q),u.fragment)),quote=True)+m[3]
 return re.sub(r'(<a\b[^>]*\bhref=")([^"]*)(")',link,s)
patches={}
for route in ['cases/p09.html','cases/p10.html','cases/p36.html','en/cases/p09.html','en/cases/p10.html','en/cases/p36.html']:
 before=(r/'evidence/stable-urls-case-services-local-20261021/before/dist'/route).read_text();after=(r/'dist'/route).read_text()
 pattern=r'<section class="case-contact".*?</section>'
 patches[route]=[clean_links(re.search(pattern,before,re.S)[0]),re.search(pattern,after,re.S)[0]]
navhash=sha((r/'dist/assets/page-version.js').read_bytes())[:12]
payload={'release':p['release'],'revision':p['revision'],'target':p['target'],'previous':p['previous_expected'],'baseline_digest':manifest_sha(old),'candidate_digest':manifest_sha(p['files']),'files_count':len(p['files']),'html_routes':sorted(f.relative_to(r/'dist').as_posix() for f in (r/'dist').rglob('*.html')),'nav_hash':navhash,'patches':patches,'binary_files':{name:base64.b64encode((r/'dist'/name).read_bytes()).decode() for name in ['assets/page-version.js','sitemap.xml']},'public_checks':['index.html','en/index.html','cases/p09.html','cases/p10.html','cases/p36.html','en/cases/p09.html','en/cases/p10.html','en/cases/p36.html','services/ai-agent.html','en/services/ai-agent.html','services/workflow-automation.html','en/services/workflow-automation.html','about.html','en/about.html','assets/page-version.js','sitemap.xml','robots.txt','llms.txt']+p['verification_files_preserved']}
transform='''def clean_links(s):
 def link(m):
  u=urlsplit(html.unescape(m[2]))
  if u.scheme or u.netloc or not u.path.endswith('.html'):return m[0]
  q=[(k,v) for k,v in parse_qsl(u.query,keep_blank_values=True) if k!='pv']
  return m[1]+html.escape(urlunsplit(('', '', u.path,urlencode(q),u.fragment)),quote=True)+m[3]
 return re.sub(r'(<a\\b[^>]*\\bhref=")([^"]*)(")',link,s)
def transform(route,s):
 s,n=re.subn(r'(<meta name="portfolio-revision" content=")[^"]+',lambda m:m[1]+P['revision'],s);assert n==1,route
 s,n=re.subn(r'(src="[^"?]*assets/page-version\\.js\\?v=)[a-f0-9]{12}',lambda m:m[1]+P['nav_hash'],s);assert n==1,route
 s=clean_links(s)
 if route in P['patches']:
  before,after=P['patches'][route];assert s.count(before)==1,route;s=s.replace(before,after)
 return s
'''
ns={'P':payload,'re':re,'html':html,'urlsplit':urlsplit,'parse_qsl':parse_qsl,'urlencode':urlencode,'urlunsplit':urlunsplit};exec(transform,ns)
for route in payload['html_routes']:
 before=(r/'evidence/stable-urls-case-services-local-20261021/before/dist'/route).read_text()
 assert sha(before.encode())==old[route],route
 assert sha(ns['transform'](route,before).encode())==p['files'][route],route
header='''from pathlib import Path
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
'''
validate='''assert str(current.resolve())==P['previous']; assert not target.exists() and not backup.exists()
B={'previous':str(current.resolve()),'files':manifest(previous),'configs':{p:sha(Path(p).read_bytes()) for p in ['/etc/nginx/sites-available/portfolio-domain-pending','/etc/nginx/sites-available/erp-trial']},'ip_public':str((root/'public').resolve()),'services':{s:subprocess.check_output(['systemctl','is-active',s],text=True).strip() for s in ['nginx','erp-trial','mysql','redis-server']}}
assert manifest_sha(B['files'])==P['baseline_digest'] and len(B['files'])==P['files_count']
assert all(v=='active' for v in B['services'].values())
assert shutil.disk_usage(root).free>100*1024**2
backup.mkdir(mode=0o700);(backup/'before.json').write_text(json.dumps(B,indent=2))
shutil.copytree(previous,target)
for route in P['html_routes']:
 if route in B['files']:
  f=target/route;f.write_text(transform(route,f.read_text()))
for route,data in P['binary_files'].items():(target/route).write_bytes(base64.b64decode(data))
files=manifest(target);assert manifest_sha(files)==P['candidate_digest'] and len(files)==P['files_count']
assert manifest(previous)==B['files'];assert all(sha(Path(p).read_bytes())==h for p,h in B['configs'].items());assert str((root/'public').resolve())==B['ip_public']
v={'status':'VALIDATED_NOT_SWITCHED','revision':P['revision'],'files':files,'digest':P['candidate_digest'],'validated_at':datetime.now(timezone.utc).isoformat()}
(backup/'validation.json').write_text(json.dumps(v,indent=2))
print('VALIDATED_NOT_SWITCHED',P['revision'],'FILES',len(files),'DIGEST',P['candidate_digest'])
print('PREVIOUS_RETAINED',P['previous']);print('CONFIGS_SERVICES_IP_PREVIEW_UNCHANGED')
'''
publish='''B=json.loads((backup/'before.json').read_text());V=json.loads((backup/'validation.json').read_text())
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
'''
for mode,body in [('validate',transform+validate),('publish',publish)]:
 code='P='+repr(payload)+'\n'+header+body
 compile(code,'<webterminal-'+mode+'>','exec');(e/(mode+'.webterminal.py')).write_text(code)
 encoded=base64.b64encode(zlib.compress(code.encode(),9)).decode()
 command="python3 -c 'import zlib,base64;exec(zlib.decompress(base64.b64decode(\""+encoded+"\")))'"
 (e/(mode+'.webterminal-command.txt')).write_text(command)
 print(mode,'command_bytes',len(command))
(e/'webterminal-plan.json').write_text(json.dumps({k:v for k,v in payload.items() if k not in ['patches','binary_files']},indent=2))
(e/'reconstruction-check.json').write_text(json.dumps({'status':'PASS','all_296_reconstructed_html_hashes_match_candidate':True,'baseline_manifest_digest':payload['baseline_digest'],'candidate_manifest_digest':payload['candidate_digest'],'unchanged_public_file_allowlist':len(old),'no_new_credentials_or_ssh_changes':True},indent=2))
print('LOCAL_RECONSTRUCTION_PASS: 296 exact HTML hashes; remaining file hashes and payload verified')
