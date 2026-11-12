from pathlib import Path
import shutil,os,json,tarfile,hashlib,re
base=Path('/srv/eli-sites/portfolio');old=Path('/srv/eli-sites/portfolio/releases/20261008-195210-douyin-link');release='20261008-200047-technical-content';hashes={'about.html': 'e3e0eff94263d8573c432a50ee4c7d5d226d5d51c4a8dc052c841a16b25b4bc8', 'en/about.html': 'f7b7fcb16c4fc22e82316669b1dcffd649ce3d746d6a8ba39412b0ded3c4da09', 'assets/editorial.css': '1a17079dfba0d3ed2e5714fecf8ebcd4ce3393df3eacc3d90d6ed88a7d40e9fb', 'cases/p06.html': '5dbc3ac577366849586ed573c2fe76b1410d13709808f059e79ce4ad559e6ecc', 'cases/p09.html': '655ca9174643f40c53440cb18cd8299a0a9dcdb07d6013104e12876a9d9ec5b8', 'cases/p10.html': 'edbae9da43c31fba37f3405af736b96ff4fc63e72bdf63ed1798ad08f19db885', 'cases/p12.html': '062415e4348279903eb7e673b0688ec4933ac8c61efeaeaba7c7f9eebc0744f3', 'cases/p13.html': 'dd6104024b7f4f12f6ca0c56eb81d8ed439c6f8aac4e1d90cbffcad58a3f493b', 'en/cases/p06.html': 'be1d70347909f2e935db393f4bd797b9bc1c2bb48dbc8a26f57a596a71d8ec57', 'en/cases/p09.html': '858568b4ae1b6014e39ce7044e78e4c79d3b5f4769aa1eef652a61a1aea792ba', 'en/cases/p10.html': '4b2bedbb6749aedd4eeaba1706924d39e9ad30a267cc0369c2f6f508e8f7d53d', 'en/cases/p12.html': '0c3eebc1cd8e440373c7f1493ebee60dfc6a7f5b5cd2072bf54a17c588e0c489', 'en/cases/p13.html': '769a749c3387e895856ed68699fca065db1cd2351ab2a6c7bb25139a885df493'}
assert (base/'public').resolve()==old
package=Path('/root/'+release+'.tar');assert hashlib.sha256(package.read_bytes()).hexdigest()=='43f7487da4a6a4b935b2f8c34126a3ebbbf4d653021908efa955421658235561'
new=base/'releases'/release;assert not new.exists()
with tarfile.open(package) as t:
 members=t.getmembers();assert set(m.name for m in members)==set(hashes)
 assert all(m.isfile() and not m.pax_headers and not m.name.startswith('/') and '..' not in Path(m.name).parts for m in members)
 assert all(hashlib.sha256(t.extractfile(m).read()).hexdigest()==hashes[m.name] for m in members)
 shutil.copytree(old,new)
 for m in members:(new/m.name).write_bytes(t.extractfile(m).read())
for p in new.rglob('*.html'):
 s=p.read_text();s=re.sub(r'(assets/editorial\.css)(?:\?[^"\s]*)?"',lambda m:m[1]+'?v='+release+'"',s);p.write_text(s)
assert '技术与实践' in (new/'about.html').read_text()
assert 'Tools in practice' in (new/'en/about.html').read_text()
assert all('https://www.douyin.com/user/MS4wLjABAAAA5LVKqAWfTG40DI3xWmdYCgegjxnDqqocrZlcGqFDldzRQLOWg4S65imwRNIA_ycH' in p.read_text() for p in new.rglob('*.html'))
h=json.loads((new/'health.json').read_text());h['release']=release;(new/'health.json').write_text(json.dumps(h,indent=2))
assert (base/'public').resolve()==old
pending=base/('public-next-'+release);os.symlink(str(new),pending);os.replace(pending,base/'public')
receipt={'release':release,'previous':str(old),'target':str(new),'package_sha256':'43f7487da4a6a4b935b2f8c34126a3ebbbf4d653021908efa955421658235561','updated_files':len(hashes)}
(base/('deployment-'+release+'.json')).write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
