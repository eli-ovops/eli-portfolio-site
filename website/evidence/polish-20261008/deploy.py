from pathlib import Path
import shutil,os,json,hashlib,tarfile
base=Path('/srv/eli-sites/portfolio');old=base/'releases/20261007-184306-inline-search';new=base/'releases'/'20261008-085549-polish'
assert (base/'public').resolve()==old
assert hashlib.sha256((old/'styles.css').read_bytes()).hexdigest()=='b537dfbcf074913b86430e28cc655c1d5cf7cae27d776e3ff97cbb2a2755e811'
package=Path('/root/20261008-085549-polish.tar');assert hashlib.sha256(package.read_bytes()).hexdigest()=='e592731cccbb8592b67b00e5236d64207aa86742f487719f3932f7a54af45401'
assert not new.exists()
with tarfile.open(package) as t:
 members=t.getmembers();assert {m.name for m in members}=={'styles.css','assets/depth-gallery.js','records.html','en/records.html'}
 assert all(m.isfile() and not m.pax_headers for m in members)
 shutil.copytree(old,new)
 for m in members:(new/m.name).write_bytes(t.extractfile(m).read())
for p in new.rglob('*.html'):
 text=p.read_text().replace('styles.css?v=20261007-inline-search','styles.css?v=20261008-polish').replace('assets/depth-gallery.js"','assets/depth-gallery.js?v=20261008-continuous"');p.write_text(text)
h=json.loads((new/'health.json').read_text());h['release']='20261008-085549-polish';(new/'health.json').write_text(json.dumps(h,indent=2))
assert (base/'public').resolve()==old
pending=base/('public-next-'+'20261008-085549-polish');os.symlink(str(new),pending);os.replace(pending,base/'public')
receipt={'release':'20261008-085549-polish','previous':str(old),'package_sha256':'e592731cccbb8592b67b00e5236d64207aa86742f487719f3932f7a54af45401','target':str(new),'changed':['styles.css','assets/depth-gallery.js','records.html','en/records.html','HTML cache links','health.json'],'rollback':'restore previous public symlink'}
(base/('deployment-'+'20261008-085549-polish'+'.json')).write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
