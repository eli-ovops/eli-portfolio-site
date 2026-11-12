from pathlib import Path
import hashlib,json,urllib.request
base=Path('/srv/eli-sites/portfolio');root=base/'domain-current'
hashes={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
actual=hashlib.sha256('\n'.join(k+':'+v for k,v in sorted(hashes.items())).encode()).hexdigest()
assert actual=='0cfe3b3f21c4625d0654e777c0fa5711a41cc5341f07defd7f5255e09f2e8d2a'
for path in ['/','/en/','/cases/p36.html','/en/cases/p36.html']:
 with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1'+path,headers={'Host':'www.eliai.cn'})) as res:
  body=res.read().decode();assert res.status==200 and 'content="noindex,nofollow"' in body and 'http://www.eliai.cn/' in body
for path in ['/login','/mobile/','/sites/portfolio/']:
 with urllib.request.urlopen('http://127.0.0.1'+path) as res:assert res.status==200
receipt={'domain':'www.eliai.cn','directory':str(root.resolve()),'files_verified':len(hashes),'aggregate_sha256':actual,'HTTP_vhost':'verified','HTTPS':'not configured','DNS':'pending user SMS verification','filing':'not completed','indexing':'noindex retained','old_IP_release':'20261007-144516','ERP':'read-only entry checks passed; config untouched'}
(base/'domain-http-20261007.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
