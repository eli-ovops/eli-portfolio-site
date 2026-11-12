from pathlib import Path
import json, hashlib, datetime
HERE=Path(__file__).resolve().parent
SITE=HERE.parents[1]
load=lambda name:json.loads((HERE/name).read_text())
package=load('package-manifest.json');switch=load('switch-receipt.json');post=load('postcheck-receipt.json');public=load('public-checks.json');browser=load('browser-checks.json')
assert switch['status']=='SWITCHED' and post['status']=='REMOTE_POSTCHECK_PASS' and public['status']=='PUBLIC_CHECKS_PASS'
assert switch['release']==package['release']==browser['release']=='20261012-212302-first-pointer'
assert package['content_revision']==browser['revision']=='374bf42e288f80f56bf7'
assert public['html_pages_noindex']==84 and public['text_files_verified']==102
assert post['previous_files_preserved']==144 and all(post['services'].values())
assert browser['media_restored'] and browser['viewport_restored']
c={check['test']:check for check in browser['checks']}
assert c['online-fast-first-filter']['count']=='9 \u9879\u8bb0\u5f55'
assert c['online-search-filter']['projects']==['project-p10','project-p09']
assert c['online-fast-image-entry']['open'] and c['online-fast-image-entry']['naturalWidth']==2558
assert c['online-escape-focus']['focus']=='detail-image-trigger' and not c['online-escape-focus']['open']
assert c['online-caption-image']['open'] and c['online-caption-image']['width']==2558
assert c['online-native-back']['projects']==['project-p10','project-p09']
assert c['online-fast-explicit-back']['focus']=='project-p09' and c['online-fast-explicit-back']['query']=='\u5e93\u5b58'
assert c['online-reset']['query']=='' and c['online-reset']['count']=='38 \u9879\u8bb0\u5f55'
assert c['online-empty']['count']=='0 \u9879\u8bb0\u5f55'
m=c['online-english-mobile-reduce-keyboard'];assert m['open'] and m['width']==390 and m['height']==844 and m['overflow']<=0 and m['imageTransform']=='none'
assert 'demo profiles, not real community users' in m['note']
actual={p.relative_to(SITE/'dist').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (SITE/'dist').rglob('*') if p.is_file()}
assert actual==package['file_hashes']
assert hashlib.sha256((HERE/('portfolio-'+package['release']+'.tar.gz')).read_bytes()).hexdigest()==package['archive_sha256']
receipt={'status':'PUBLISHED_ACCEPTED_INDEXING_DISABLED','release':package['release'],'content_revision':package['content_revision'],'published_at':switch['switched_at'],'accepted_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owner':'01a123a8-16ae-76f0-85c9-8e017dd95758','url':'http://[REDACTED_HOST]/sites/portfolio/','current_version_url':'http://[REDACTED_HOST]/sites/portfolio/?pv='+package['content_revision'],'previous':post['previous'],'previous_files_preserved':144,'archive_sha256':package['archive_sha256'],'remote_files_verified':144,'public_text_files_verified':102,'html_pages_noindex':84,'indexing':'DISABLED','nginx_config':'UNCHANGED_NO_RELOAD','nginx_sha256':post['nginx_sha256'],'erp_services':post['services'],'erp_boundary':'Entry-page availability only; no login/business/DB operation','local_output_matches_package':True,'browser':str(len(c))+' focused actual checks; native/shared-title path, fast first filter, inventory search, two screenshot entries/Escape, native/fast explicit back, empty/reset and English390px keyboard/reduce mode','mobile_screenshot_note':'Initial screenshot captured an unsettled paint and is retained as online-mobile-keyboard.jpg; actual loaded modal rechecked and stable full-context proof saved in online-mobile-keyboard-stable.jpg','limits':['IAB desktop and simulated mobile; no all-browser/real-touch/FPS claim','Old already-open HTML needs an initial refresh or current-version entry'],'protected':['Nginx','ERP','database','DNS','HTTPS','ICP automation','indexing disabled'],'artifacts_retained':sorted(p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file())}
(HERE/'receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({k:v for k,v in receipt.items() if k!='artifacts_retained'},indent=2))
