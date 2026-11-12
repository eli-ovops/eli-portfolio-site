from pathlib import Path
import shutil,os,json,hashlib,tarfile
base=Path('/srv/eli-sites/portfolio');old=base/'releases/20261008-085549-polish';new=base/'releases'/'20261008-090042-records-motion'
assert (base/'public').resolve()==old
package=Path('/root/20261008-090042-records-motion.tar');assert hashlib.sha256(package.read_bytes()).hexdigest()=='d0e5faefa53a3a3753de6314688a559ca974943c014041a2615723d255bcae40'
assert not new.exists()
with tarfile.open(package) as t:
 members=t.getmembers();assert {m.name for m in members}=={'app.js','motion.js'}
 assert all(m.isfile() and not m.pax_headers for m in members)
 shutil.copytree(old,new)
 for m in members:(new/m.name).write_bytes(t.extractfile(m).read())
for p in new.rglob('*.html'):
 text=p.read_text().replace('app.js"','app.js?v=20261008-motion"').replace('motion.js"','motion.js?v=20261008-motion"');p.write_text(text)
h=json.loads((new/'health.json').read_text());h['release']='20261008-090042-records-motion';(new/'health.json').write_text(json.dumps(h,indent=2))
assert (base/'public').resolve()==old
pending=base/('public-next-'+'20261008-090042-records-motion');os.symlink(str(new),pending);os.replace(pending,base/'public')
receipt={'release':'20261008-090042-records-motion','previous':str(old),'package_sha256':'d0e5faefa53a3a3753de6314688a559ca974943c014041a2615723d255bcae40','target':str(new),'rollback':'restore previous public symlink'}
(base/('deployment-'+'20261008-090042-records-motion'+'.json')).write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
