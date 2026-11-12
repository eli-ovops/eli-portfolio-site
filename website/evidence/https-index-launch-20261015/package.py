from pathlib import Path
import sys,json,hashlib,tarfile,io,re,datetime
from html.parser import HTMLParser
from urllib.parse import urlsplit
R=Path(__file__).resolve().parents[2];E=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'scripts'))
from seo import load_config,write_discovery
config=load_config(R);assert config['base_url']=='https://www.eliai.cn/' and config['indexing_enabled']
prior=R/'evidence/icp-footer-domain-20261015';m=json.loads((prior/'manifest.json').read_text())['variants']['domain'];source=prior/'domain-candidate'
files={n:(source/n).read_bytes() for n in m['file_hashes']};assert all(hashlib.sha256(b).hexdigest()==m['file_hashes'][n] for n,b in files.items())
for n,b in list(files.items()):
 if n.endswith('.html'):
  s=b.decode().replace('http://www.eliai.cn/','https://www.eliai.cn/').replace(m['revision'],'__PORTFOLIO_REVISION__')
  if not n.endswith('404.html'):s=s.replace('name="robots" content="noindex,nofollow"','name="robots" content="index,follow"')
  files[n]=s.encode()
h=hashlib.sha256()
for n,b in sorted(files.items()):h.update(n.encode()+b'\0'+b+b'\0')
revision=h.hexdigest()[:20];target=E/'domain-candidate';assert not target.exists();target.mkdir()
for n,b in list(files.items()):
 if n.endswith('.html'):
  b=b.replace(b'__PORTFOLIO_REVISION__',revision.encode());files[n]=b
  # Launch cannot silently publish the local-only catalogue or change any body copy/animation.
  assert b.decode().split('<body>',1)[1].replace(revision,m['revision'])==(source/n).read_text().split('<body>',1)[1],n
 p=target/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
output={n:b.decode() for n,b in files.items() if n.endswith('.html')};write_discovery(R,target,config,output)
class Head(HTMLParser):
 def __init__(self):super().__init__();self.meta={};self.links=[];self.refs=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='meta':self.meta[a.get('name') or a.get('property')]=a.get('content')
  if tag=='link':self.links.append(a)
  if tag in ['script','img','source','video'] and a.get('src'):self.refs.append(a['src'])
  if tag=='link' and a.get('rel')=='stylesheet':self.refs.append(a.get('href',''))
for n,s in output.items():
 p=Head();p.feed(s)
 assert p.meta['robots']==('noindex,nofollow' if n.endswith('404.html') else 'index,follow'),n
 assert p.meta['portfolio-revision']==revision
 assert not any(x.startswith('http:') for x in p.refs),(n,p.refs)
 assert 'http://www.eliai.cn/' not in s and 'http://[REDACTED_HOST]/sites/portfolio/' not in s
 if not n.endswith('404.html'):assert next(x['href'] for x in p.links if x.get('rel')=='canonical').startswith(config['base_url'])
files={p.relative_to(target).as_posix():p.read_bytes() for p in target.rglob('*') if p.is_file()};assert len(files)==140
release=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')+'-https-index'
archive=E/'domain.tar.gz'
with tarfile.open(archive,'w:gz',format=tarfile.USTAR_FORMAT) as t:
 for n,b in sorted(files.items()):
  assert not any(x.startswith('.') or x=='..' for x in Path(n).parts)
  ti=tarfile.TarInfo(n);ti.size=len(b);ti.uid=ti.gid=0;ti.mode=0o644;ti.mtime=0;t.addfile(ti,io.BytesIO(b))
with tarfile.open(archive) as t:
 assert all(x.isreg() and not x.pax_headers and not Path(x.name).is_absolute() for x in t.getmembers())
m={'release':release,'revision':revision,'previous':json.loads((E/'bootstrap.json').read_text())['domain'],'target':'/srv/eli-sites/portfolio/domain-releases/'+release,'file_hashes':{n:hashlib.sha256(b).hexdigest() for n,b in files.items()},'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'package':str(archive),'body_integrity':'84 unchanged except revision links','indexable_pages':82,'not_found_noindex_pages':2}
(E/'manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps({k:v for k,v in m.items() if k not in ['file_hashes','package']}))
