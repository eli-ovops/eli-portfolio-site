from pathlib import Path
import shutil,hashlib,json,os
base=Path('/srv/eli-sites/portfolio')
previous=base/'releases/20261007-144516'
assert (base/'public').resolve()==previous
assert hashlib.sha256((previous/'styles.css').read_bytes()).hexdigest()=='f97801b5bc05af313c3b554e181375aa537d2d88404750eedb2ed7f072d849ab'
css=Path('/root/portfolio-20261007-183736-filters.css').read_bytes()
assert hashlib.sha256(css).hexdigest()=='6dd02ef8851028b95c74ffb603146fa15ceb31d4ace5a3f01473058997d63974'
target=base/'releases'/'20261007-183736-filters'
assert not target.exists()
shutil.copytree(previous,target)
(target/'styles.css').write_bytes(css)
health=json.loads((target/'health.json').read_text());health['release']='20261007-183736-filters'
(target/'health.json').write_text(json.dumps(health,indent=2))
assert (base/'public').resolve()==previous
pending=base/('public-next-'+'20261007-183736-filters')
os.symlink(str(target),pending);os.replace(pending,base/'public')
receipt={'release':'20261007-183736-filters','previous':str(previous),'target':str(target),'css_sha256':'6dd02ef8851028b95c74ffb603146fa15ceb31d4ace5a3f01473058997d63974','changed':['styles.css','health.json'],'rollback':'atomic public symlink to previous'}
(base/('deployment-'+'20261007-183736-filters'+'.json')).write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
