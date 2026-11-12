from pathlib import Path
import json,subprocess,hashlib,urllib.request
from datetime import datetime,timezone
E=Path(__file__).resolve().parent;P=json.loads((E/'plan.json').read_text());B=json.loads((E/'preflight.json').read_text())
old=(E.parent/'deploy-seo-geo-20261020/postflight.remote.py').read_text();body=old[old.index('from pathlib import Path\nimport json,hashlib,subprocess,shutil'):];code='P='+repr(P)+'\nB='+repr(B)+'\n'+body;(E/'postflight.remote.py').write_text(code)
SSH=['ssh','-F','/dev/null','-i','/Users/USER/.ssh/erp-jdcloud-trial-20261005','-o','IdentityAgent=none','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/Volumes/EXTERNAL/ERP试跑-20261005/known_hosts','-o','ForwardAgent=no','-o','ConnectTimeout=10','root@[REDACTED_HOST]','python3 -']
x=subprocess.run(SSH,input=code,text=True,capture_output=True,timeout=40);(E/'postflight.stderr.txt').write_text(x.stderr);assert x.returncode==0,x.stderr[-1200:];d=json.loads(x.stdout);(E/'postflight.json').write_text(json.dumps(d,indent=2)+'\n')
checks=[]
for name in ['index.html','en/index.html','about.html','en/about.html','assets/industry-scenarios.css','assets/industry-scenarios.js','motion.js','assets/depth-gallery.js','sitemap.xml','robots.txt','llms.txt']:
 with urllib.request.urlopen('https://www.eliai.cn/'+name,timeout=15) as response:
  content=response.read();h=hashlib.sha256(content).hexdigest();assert response.status==200 and h==P['files'][name],name;checks.append({'path':name,'status':response.status,'sha256':h})
(E/'public-http-checks.json').write_text(json.dumps({'checked_at':datetime.now(timezone.utc).isoformat(),'checks':checks},indent=2)+'\n');(E/'deployed-manifest.json').write_text(json.dumps(P['files'],indent=2)+'\n');print(json.dumps({'postflight':d,'independent_public_checks':len(checks)},indent=2))
