from pathlib import Path
import shutil,os,json,hashlib
base=Path('/srv/eli-sites/portfolio');old=base/'releases/20261007-183736-filters-v2';new=base/'releases'/'20261007-184306-inline-search'
assert (base/'public').resolve()==old
assert hashlib.sha256((old/'styles.css').read_bytes()).hexdigest()=='6dd02ef8851028b95c74ffb603146fa15ceb31d4ace5a3f01473058997d63974'
css=Path('/root/portfolio-20261007-184306-inline-search.css').read_bytes();assert hashlib.sha256(css).hexdigest()=='b537dfbcf074913b86430e28cc655c1d5cf7cae27d776e3ff97cbb2a2755e811'
assert not new.exists();shutil.copytree(old,new);(new/'styles.css').write_bytes(css)
count=0
for p in new.rglob('*.html'):
 text=p.read_text();updated=text.replace('styles.css?v=20261007-nowrap','styles.css?v=20261007-inline-search')
 if text!=updated:p.write_text(updated);count+=1
assert count==84
h=json.loads((new/'health.json').read_text());h['release']='20261007-184306-inline-search';(new/'health.json').write_text(json.dumps(h,indent=2))
assert (base/'public').resolve()==old
pending=base/('public-next-'+'20261007-184306-inline-search');os.symlink(str(new),pending);os.replace(pending,base/'public')
receipt={'release':'20261007-184306-inline-search','previous':str(old),'css_sha256':'b537dfbcf074913b86430e28cc655c1d5cf7cae27d776e3ff97cbb2a2755e811','html_cache_links':count,'rollback':'restore previous public symlink'}
(base/('deployment-'+'20261007-184306-inline-search'+'.json')).write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
