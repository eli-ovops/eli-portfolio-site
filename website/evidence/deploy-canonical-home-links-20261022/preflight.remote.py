
import hashlib,json,socket,subprocess
from pathlib import Path
from datetime import datetime,timezone
root=Path('/srv/eli-sites/portfolio/domain-current')
conf=Path('/etc/nginx/sites-available/portfolio-domain-pending')
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
test=subprocess.run(['nginx','-t'],text=True,capture_output=True)
r={'checked_at':datetime.now(timezone.utc).isoformat(),'host':socket.gethostname(),'config':conf.read_text(),'config_sha256':sha(conf),'release':str(root.resolve()),'hashes':{str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()},'enabled_config_hashes':{str(p):sha(p) for p in Path('/etc/nginx/sites-enabled').iterdir() if p.is_file()},'services':{u:subprocess.check_output(['systemctl','show',u,'--property=ActiveState,MainPID'],text=True).strip() for u in ['nginx','erp-trial','mysql','redis-server']},'nginx_test':{'returncode':test.returncode,'stderr':test.stderr}}
import shutil,re
r['ip_public']=str(Path('/srv/eli-sites/portfolio/public').resolve())
r['free_bytes']=shutil.disk_usage('/srv/eli-sites/portfolio').free
r['revision']=re.search(r'name="portfolio-revision" content="([^"]+)',(root/'index.html').read_text())[1]
print(json.dumps(r,indent=2))
