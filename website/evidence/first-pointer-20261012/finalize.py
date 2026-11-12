from pathlib import Path
import json, hashlib, datetime, re, subprocess
ROOT=Path(__file__).resolve().parent
SITE=ROOT.parents[1]
browser=json.loads((ROOT/'browser-final.json').read_text())
checks={check['test']:check for check in browser['checks']}
assert checks['fast-first-filter']['count']=='9 \u9879\u8bb0\u5f55'
assert checks['search-filter']['projects']==['project-p10','project-p09']
assert checks['fast-image-during-title-entry']['dialog'] is True
assert checks['fast-image-during-title-entry']['imageWidth']==2558
assert checks['escape-focus']['dialog'] is False
assert checks['escape-focus']['focus']=='detail-image-trigger'
assert checks['native-back']['projects']==['project-p10','project-p09']
assert checks['fast-explicit-back']['focus']=='project-p09'
assert checks['fast-explicit-back']['query']=='\u5e93\u5b58'
assert checks['empty']['count']=='0 \u9879\u8bb0\u5f55'
assert checks['reset']['count']=='38 \u9879\u8bb0\u5f55'
assert checks['reset']['query']==''
mobile=checks['english-mobile-reduce-keyboard']
assert mobile['width']==390 and mobile['height']==844
assert mobile['overflow']<=0 and mobile['dialog'] is True
assert mobile['imageTransform']=='none'
assert 'demo profiles, not real community users' in mobile['note']
revision=re.search(r'name="portfolio-revision" content="(\w+)"',(SITE/'dist/index.html').read_text()).group(1)
assert revision==browser['revision']==mobile['revision']
for saved,current in [('before-delivery.md',SITE/'docs/\u4ea4\u4ed8\u4e0e\u9a8c\u8bc1.md'),('before-handoff.md',Path('/Users/USER/Documents/eli/PERSONAL_WEBSITE_HANDOFF_2026-10-10.md'))]:
 prior=(ROOT/saved).read_text().split('\n',1)[1]
 assert current.read_text().endswith(prior), saved+' old contents not preserved'
try:
 result=subprocess.check_output(['ps','-p','1095','-o','args='],text=True).strip()
except subprocess.CalledProcessError:
 result=''
assert not result.endswith('first-pointer-20261012/probe.py')
files={str(p.relative_to(SITE/'dist')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (SITE/'dist').rglob('*') if p.is_file()}
assert len(files)==144
scope=json.loads((ROOT/'scope-checks.json').read_text())
assert scope['status']=='PASS'
receipt={'status':'LOCAL_ACCEPTED_NOT_PUBLISHED','checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owner':'01a123a8-16ae-76f0-85c9-8e017dd95758','local_revision':revision,'online_release_unchanged':'20261012-194514-return-zoom','server_actions':False,'indexing':'DISABLED','build_pages':84,'records':38,'validation':['build','static/privacy','localization','SEO/noindex','navigation-version','first-pointer-route-regression','accepted-archive-body-image-comparison','real-browser-focused-flow'],'browser_receipt':'browser-final.json','scope_receipt':'scope-checks.json','new_source_files':['scripts/check_first_pointer.cjs'],'changed_source_files':['motion.js','assets/editorial.js','assets/editorial.css','scripts/pages.py'],'public_files':files,'diagnostic_server_4179_stopped':True,'preview_4178_kept':True,'old_control_docs_preserved':True,'artifacts_retained':sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()),'limits':['IAB desktop and simulated mobile only','No real touch device or all-browser/FPS claim','No server sync this turn']}
(ROOT/'receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({k:v for k,v in receipt.items() if k not in ['public_files','artifacts_retained']},indent=2))
