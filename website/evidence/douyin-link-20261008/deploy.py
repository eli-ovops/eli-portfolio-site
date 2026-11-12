from pathlib import Path
import shutil,os,json,hashlib
base=Path('/srv/eli-sites/portfolio');old=Path('/srv/eli-sites/portfolio/releases/20261008-184740-footer-no-qr');release='20261008-195210-douyin-link';before='https://www.douyin.com/user/MS4wLjABAAAA7VB6KYGM4HZmt1g86KBowpFHFJNgJmRtoGYrA5WylDi1m6KJgSaNJ-YGBJeGudoG';after='https://www.douyin.com/user/MS4wLjABAAAA5LVKqAWfTG40DI3xWmdYCgegjxnDqqocrZlcGqFDldzRQLOWg4S65imwRNIA_ycH'
assert (base/'public').resolve()==old
pages=list(old.rglob('*.html'));assert len(pages)==84
assert all(p.read_text().count(before)==1 for p in pages)
new=base/'releases'/release;assert not new.exists();shutil.copytree(old,new)
for p in new.rglob('*.html'):
 s=p.read_text();p.write_text(s.replace(before,after));assert p.read_text().count(after)==1 and before not in p.read_text()
h=json.loads((new/'health.json').read_text());h['release']=release;(new/'health.json').write_text(json.dumps(h,indent=2))
assert (base/'public').resolve()==old
pending=base/('public-next-'+release);os.symlink(str(new),pending);os.replace(pending,base/'public')
receipt={'release':release,'previous':str(old),'html_pages':len(pages),'change':'Douyin URL only; pending technical content excluded'}
(base/('deployment-'+release+'.json')).write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
