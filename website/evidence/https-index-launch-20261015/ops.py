from pathlib import Path
import subprocess,json,sys,hashlib
E=Path(__file__).resolve().parent;R=E.parents[1]
SSH=['ssh','-F','/dev/null','-i','/Users/USER/.ssh/erp-jdcloud-trial-20261005','-o','IdentityAgent=none','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/Volumes/EXTERNAL/ERP试跑-20261005/known_hosts','-o','ForwardAgent=no','-o','ConnectTimeout=10','root@[REDACTED_HOST]']
def run(name,script,timeout=180):
 import ast;ast.parse(script)
 (E/(name+'.remote.py')).write_text(script)
 x=subprocess.run(SSH+['python3 -'],input=script,text=True,capture_output=True,timeout=timeout)
 (E/(name+'.stderr.txt')).write_text(x.stderr)
 if x.returncode:print(x.stderr[-2500:]);print(x.stdout[-2500:]);raise SystemExit(x.returncode)
 data=json.loads(x.stdout);(E/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2));return data
HEADER="""from pathlib import Path
import os,subprocess,json,hashlib,urllib.request,socket,ssl,datetime,shutil
root=Path('/srv/eli-sites/portfolio');conf=Path('/etc/nginx/sites-available/portfolio-domain-pending');erp=Path('/etc/nginx/sites-available/erp-trial')
def sha(b):return hashlib.sha256(b).hexdigest()
def cmd(args):
 p=subprocess.run(args,capture_output=True,text=True);assert p.returncode==0,(args,p.stderr[-1000:]);return p.stdout.strip()
"""
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='bootstrap':
  previous=json.loads((R/'evidence/icp-footer-domain-20261015/preflight.json').read_text())
  expected=previous['configs']['/etc/nginx/sites-available/portfolio-domain-pending']
  data=run(mode,HEADER+f'expected={expected!r}\n'+r'''
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
''')
  print(json.dumps(data,ensure_ascii=False))
 elif mode=='issue':
  b=json.loads((E/'bootstrap.json').read_text())
  data=run(mode,HEADER+f'B={b!r}\n'+r'''
assert sha(conf.read_bytes())==B['bootstrap_sha'] and sha(erp.read_bytes())==B['erp_sha']
assert not Path('/etc/letsencrypt/live/www.eliai.cn/fullchain.pem').exists(),'Existing certificate; inspect before issuing'
args=['certbot','certonly','--non-interactive','--agree-tos','--register-unsafely-without-email','--webroot','-w','/srv/eli-sites/portfolio/acme','--cert-name','www.eliai.cn','-d','eliai.cn','-d','www.eliai.cn','--key-type','ecdsa']
p=subprocess.run(args,capture_output=True,text=True,timeout=120)
private_log=root/'backups/https-index-20261015/certbot-issuance.log';private_log.write_text(p.stdout+'\n'+p.stderr);os.chmod(private_log,0o600)
if p.returncode:
 print(json.dumps({'status':'ISSUANCE_FAILED','returncode':p.returncode,'output':p.stdout[-1800:],'error':p.stderr[-2500:]}))
else:
 cert=Path('/etc/letsencrypt/live/www.eliai.cn/fullchain.pem');key=Path('/etc/letsencrypt/live/www.eliai.cn/privkey.pem');assert cert.is_file() and key.is_file()
 print(json.dumps({'status':'CERTIFICATE_ISSUED','certificate':str(cert),'details':cmd(['openssl','x509','-in',str(cert),'-noout','-subject','-issuer','-dates','-ext','subjectAltName']),'key_mode':oct(key.stat().st_mode & 0o777)}))
''',180)
  print(json.dumps(data,ensure_ascii=False))
