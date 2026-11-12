from pathlib import Path
import os,subprocess,json,hashlib,urllib.request,socket,ssl,datetime,shutil
root=Path('/srv/eli-sites/portfolio');conf=Path('/etc/nginx/sites-available/portfolio-domain-pending');erp=Path('/etc/nginx/sites-available/erp-trial')
def sha(b):return hashlib.sha256(b).hexdigest()
def cmd(args):
 p=subprocess.run(args,capture_output=True,text=True);assert p.returncode==0,(args,p.stderr[-1000:]);return p.stdout.strip()
B={'config_before_sha': '63e0b3c4d3853108cac6d9396d158ced9c3704fdd932af3069501ca17cfd6398', 'erp_sha': 'f8feed3d72ef606d90674a633f73a9449a31a874197e823130ed9b3b9d213445', 'public': '/srv/eli-sites/portfolio/releases/20261015-165606-icp-footer', 'domain': '/srv/eli-sites/portfolio/domain-releases/20261015-165606-icp-footer', 'certbot': 'certbot 1.21.0', 'backup': '/srv/eli-sites/portfolio/backups/https-index-20261015', 'bootstrap_sha': 'affbceef3878890496055913f2a825635b0785c0c73cce97a15da8f5137a8a7b', 'challenge_checks': [{'host': 'eliai.cn', 'status': 200}, {'host': 'www.eliai.cn', 'status': 200}], 'nginx_test': 'nginx: the configuration file /etc/nginx/nginx.conf syntax is ok\nnginx: configuration file /etc/nginx/nginx.conf test is successful'}

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
