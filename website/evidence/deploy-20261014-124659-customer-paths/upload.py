from pathlib import Path
import json, subprocess, hashlib
HERE=Path(__file__).resolve().parent
release='20261014-124659-customer-paths'
assert json.loads((HERE/'preflight-receipt.json').read_text())['status']=='PREFLIGHT_PASS'
manifest=json.loads((HERE/'package-manifest.json').read_text())
package=HERE/('portfolio-'+release+'.tar.gz')
assert hashlib.sha256(package.read_bytes()).hexdigest()==manifest['archive_sha256']
review={'status':'REVIEWED_READY_FOR_ISOLATED_PREPARE','authorization':'Current user specific portfolio sync','archive_members':144,'public_output_equals_accepted_local':True,'previous_target':'20261014-110604-return-origin','unchanged_nginx':'f8feed3d72ef606d90674a633f73a9449a31a874197e823130ed9b3b9d213445','retained_scope':'Portfolio public symlink and private release/backup only; no services/data/DNS/indexing writes','scripts':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ['preflight-remote.py','prepare-remote.py','switch-remote.py','postcheck-remote.py']}}
(HERE/'review.json').write_text(json.dumps(review,indent=2))
options=['-F','/dev/null','-i','/Users/USER/.ssh/erp-jdcloud-trial-20261005','-o','IdentityAgent=none','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/Volumes/EXTERNAL/ERP\u8bd5\u8dd1-20261005/known_hosts','-o','ForwardAgent=no','-o','ConnectTimeout=10']
for local,remote in [(package,'/root/portfolio-'+release+'.tar.gz'),(HERE/'manifest.sha256','/root/portfolio-'+release+'.sha256')]:
 run=subprocess.run(['scp',*options,str(local),'root@[REDACTED_HOST]:'+remote],capture_output=True,text=True,timeout=180)
 assert run.returncode==0,run.stderr[-1500:]
(HERE/'upload-receipt.json').write_text(json.dumps({'status':'UPLOADED_NOT_SWITCHED','release':release,'archive_sha256':manifest['archive_sha256'],'remote_package':'/root/portfolio-'+release+'.tar.gz'},indent=2))
print('UPLOADED_NOT_SWITCHED; strict pinned identity; package + manifest')
