from pathlib import Path
import hashlib,json,subprocess,socket,urllib.request
r=Path('/srv/eli-sites/portfolio')
def hashes(p):return {str(x.relative_to(p)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(p.rglob('*')) if x.is_file()}
c=['/etc/nginx/sites-available/erp-trial','/etc/nginx/sites-available/portfolio-domain-pending']
out={'links':{s:{'target':str((r/s).resolve()),'files':hashes(r/s)} for s in ['public','domain-current']},'configs':{s:hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in c},'dns':{h:socket.gethostbyname_ex(h) for h in ['eliai.cn','www.eliai.cn']},'services':{s:subprocess.run(['systemctl','is-active',s],capture_output=True,text=True).stdout.strip() for s in ['nginx','erp-trial','mysql','redis-server']},'domain_http':[],'https_listener':False}
for port in [443]:
 s=socket.socket();s.settimeout(3);out['https_listener']=s.connect_ex(('127.0.0.1',port))==0;s.close()
for u in ['http://www.eliai.cn/','http://eliai.cn/','http://[REDACTED_HOST]/login','http://[REDACTED_HOST]/mobile/']:
 try:
  with urllib.request.urlopen(u,timeout=8) as v:
   b=v.read();out['domain_http'].append({'url':u,'status':v.status,'final_url':v.url,'bytes':len(b),'headers':dict(v.headers),'sha256':hashlib.sha256(b).hexdigest()})
 except Exception as ex:out['domain_http'].append({'url':u,'error':str(ex)})
print(json.dumps(out))
