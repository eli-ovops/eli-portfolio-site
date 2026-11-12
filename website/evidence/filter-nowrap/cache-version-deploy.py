from pathlib import Path
import shutil,os,json
base=Path('/srv/eli-sites/portfolio');old=base/'releases/20261007-183736-filters';new=base/'releases/20261007-183736-filters-v2'
assert (base/'public').resolve()==old
assert not new.exists()
shutil.copytree(old,new)
count=0
for p in new.rglob('*.html'):
 text=p.read_text();updated=text.replace('styles.css"','styles.css?v=20261007-nowrap"')
 if text!=updated:p.write_text(updated);count+=1
assert count==84
h=json.loads((new/'health.json').read_text());h['release']=new.name;(new/'health.json').write_text(json.dumps(h,indent=2))
assert (base/'public').resolve()==old
os.symlink(str(new),base/'public-next-filters-v2');os.replace(base/'public-next-filters-v2',base/'public')
print(json.dumps({'release':new.name,'previous':str(old),'html_stylesheet_links_updated':count,'rollback_baseline':'/srv/eli-sites/portfolio/releases/20261007-144516'}))
