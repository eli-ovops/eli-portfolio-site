from pathlib import Path
import os,subprocess,json,hashlib,urllib.request,socket,ssl,datetime,shutil
root=Path('/srv/eli-sites/portfolio');conf=Path('/etc/nginx/sites-available/portfolio-domain-pending');erp=Path('/etc/nginx/sites-available/erp-trial')
def sha(b):return hashlib.sha256(b).hexdigest()
def cmd(args):
 p=subprocess.run(args,capture_output=True,text=True);assert p.returncode==0,(args,p.stderr[-1000:]);return p.stdout.strip()
expected='63e0b3c4d3853108cac6d9396d158ced9c3704fdd932af3069501ca17cfd6398'

assert sha(conf.read_bytes())==expected,'Concurrent config change'
backup=root/'backups'/'https-index-20261015';assert not backup.exists();backup.mkdir(mode=0o700)
shutil.copyfile(conf,backup/'domain-before.conf');os.chmod(backup/'domain-before.conf',0o600)
info={'config_before_sha':sha(conf.read_bytes()),'erp_sha':sha(erp.read_bytes()),'public':str((root/'public').resolve()),'domain':str((root/'domain-current').resolve()),'certbot':cmd(['certbot','--version']),'backup':str(backup)}
(backup/'before.json').write_text(json.dumps(info,indent=2))
acme=root/'acme';token=acme/'.well-known/acme-challenge/eli-https-preflight-20261015';token.parent.mkdir(parents=True,exist_ok=True);token.write_text('eli-https-preflight-20261015')
challenge='    location ^~ /.well-known/acme-challenge/ { root /srv/eli-sites/portfolio/acme; default_type text/plain; try_files $uri =404; }\n'
s=conf.read_text();s=s.replace('    return 301 http://www.eliai.cn$request_uri;',challenge+'    location / { return 301 http://www.eliai.cn$request_uri; }')
s=s.replace('    server_name www.eliai.cn;','    server_name www.eliai.cn;\n'+challenge)
conf.write_text(s)
p=subprocess.run(['nginx','-t'],capture_output=True,text=True)
if p.returncode:
 shutil.copyfile(backup/'domain-before.conf',conf);raise RuntimeError(p.stderr)
cmd(['systemctl','reload','nginx'])
info['bootstrap_sha']=sha(conf.read_bytes());info['challenge_checks']=[]
for h in ['eliai.cn','www.eliai.cn']:
 with urllib.request.urlopen('http://'+h+'/.well-known/acme-challenge/'+token.name,timeout=10) as v:
  assert v.read().decode()==token.read_text();info['challenge_checks'].append({'host':h,'status':v.status})
assert sha(erp.read_bytes())==info['erp_sha'];info['nginx_test']=p.stderr.strip();print(json.dumps(info))
