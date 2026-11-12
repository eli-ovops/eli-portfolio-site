"""This batch only: strict SSH to its reviewed script; write returned receipts locally."""
import subprocess,json,sys
from pathlib import Path
here=Path(__file__).resolve().parent
mode=sys.argv[1]
assert mode in ('preflight','prepare','switch','postcheck')
script=here/(mode+'-remote.py')
options=['-F','/dev/null','-i','/Users/USER/.ssh/erp-jdcloud-trial-20261005',
         '-o','IdentityAgent=none','-o','IdentitiesOnly=yes','-o','BatchMode=yes',
         '-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/Volumes/EXTERNAL/ERP试跑-20261005/known_hosts',
         '-o','ForwardAgent=no','-o','ConnectTimeout=10']
result=subprocess.run(['ssh',*options,'root@[REDACTED_HOST]','python3 -'],input=script.read_text(),text=True,capture_output=True,timeout=90)
if result.returncode:
    print(result.stderr[-2000:]);raise SystemExit(result.returncode)
receipt=json.loads(result.stdout)
(here/(mode+'-receipt.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
print(json.dumps(receipt,ensure_ascii=False))
