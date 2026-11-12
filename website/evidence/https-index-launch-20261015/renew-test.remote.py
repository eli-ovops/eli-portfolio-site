from pathlib import Path
import os,subprocess,json,hashlib,urllib.request,socket,ssl,datetime,shutil
root=Path('/srv/eli-sites/portfolio');conf=Path('/etc/nginx/sites-available/portfolio-domain-pending');erp=Path('/etc/nginx/sites-available/erp-trial')
def sha(b):return hashlib.sha256(b).hexdigest()
def cmd(args):
 p=subprocess.run(args,capture_output=True,text=True);assert p.returncode==0,(args,p.stderr[-1000:]);return p.stdout.strip()

p=subprocess.run(['certbot','renew','--cert-name','www.eliai.cn','--dry-run','--no-random-sleep-on-renew'],capture_output=True,text=True,timeout=180)
log=root/'backups/https-index-20261015/renewal-dry-run.log';log.write_text(p.stdout+'\n'+p.stderr);os.chmod(log,0o600)
print(json.dumps({'status':'PASS' if p.returncode==0 else 'FAILED','returncode':p.returncode,'output':p.stdout[-1800:],'error':p.stderr[-1200:]}))
