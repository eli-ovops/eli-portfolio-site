from pathlib import Path,PurePosixPath
import subprocess,json,hashlib,tarfile,io,re,sys,datetime
ROOT=Path(__file__).resolve().parents[2]; E=Path(__file__).resolve().parent
SSH=['ssh','-F','/dev/null','-i','/Users/USER/.ssh/erp-jdcloud-trial-20261005','-o','IdentityAgent=none','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/Volumes/EXTERNAL/ERP试跑-20261005/known_hosts','-o','ForwardAgent=no','-o','ConnectTimeout=10','root@[REDACTED_HOST]']
def sha(b):return hashlib.sha256(b).hexdigest()
def remote(name,script):
 (E/(name+'.remote.py')).write_text(script)
 p=subprocess.run(SSH+['python3 -'],input=script,text=True,capture_output=True,timeout=90)
 if p.returncode: print(p.stderr[-3000:]);raise SystemExit(p.returncode)
 x=json.loads(p.stdout);(E/(name+'.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2));return x
if sys.argv[1]=='preflight':
 x=remote('preflight','''from pathlib import Path
import hashlib,json,subprocess,socket,urllib.request
r=Path('/srv/eli-sites/portfolio')
def hashes(p):return {str(x.relative_to(p)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(p.rglob('*')) if x.is_file()}
c=['/etc/nginx/sites-available/erp-trial','/etc/nginx/sites-available/portfolio-domain-pending']
out={'links':{s:{'target':str((r/s).resolve()),'files':hashes(r/s)} for s in ['public','domain-current']},'configs':{s:hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in c},'dns':{h:socket.gethostbyname_ex(h) for h in ['eliai.cn','www.eliai.cn']},'services':{s:subprocess.run(['systemctl','is-active',s],capture_output=True,text=True).stdout.strip() for s in ['nginx','erp-trial','mysql','redis-server']},'domain_http':[],'https_listener':False}
for port in [443]:
 s=socket.socket();s.settimeout(3);out['https_listener']=s.connect_ex(('127.0.0.1',port))==0;s.close()
for u in ['http://www.eliai.cn/','http://eliai.cn/','http://[REDACTED_HOST]/login','http://[REDACTED_HOST]/mobile/']:
 try:
  with urllib.request.urlopen(u,timeout=8) as v:
   b=v.read();out['domain_http'].append({'url':u,'status':v.status,'final_url':v.url,'bytes':len(b),'headers':dict(v.headers),'sha256':hashlib.sha256(b).hexdigest()})
 except Exception as ex:out['domain_http'].append({'url':u,'error':str(ex)})
print(json.dumps(out))
''')
 baseline=json.loads((ROOT/'evidence/deploy-20261015-131729-records-catalog/package-manifest.json').read_text())
 assert x['links']['public']['files']==baseline['file_hashes'],'Production no longer matches known accepted archive'
 assert all(v=='active' for v in x['services'].values())
 print(json.dumps({'public':x['links']['public']['target'],'domain':x['links']['domain-current']['target'],'files':len(baseline['file_hashes']),'dns':x['dns'],'HTTPS_listener':x['https_listener'],'HTTP':x['domain_http']},ensure_ascii=False))
elif sys.argv[1]=='package':
 old=ROOT/'evidence/deploy-20261015-131729-records-catalog'
 m=json.loads((old/'package-manifest.json').read_text());archive=old/'portfolio-20261015-131729-records-catalog.tar.gz'
 assert sha(archive.read_bytes())==m['archive_sha256']
 with tarfile.open(archive) as t:
  source={}
  for f in t.getmembers():
   p=PurePosixPath(f.name);assert f.isreg() and not p.is_absolute() and '..' not in p.parts and not f.pax_headers
   b=t.extractfile(f).read();assert sha(b)==m['file_hashes'][f.name];source[f.name]=b
 assert set(source)==set(m['file_hashes'])
 assert source['assets/social-footer.css']==(E/'before/assets/social-footer.css').read_bytes()
 release=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')+'-icp-footer'
 plan={'release':release,'variants':{}}
 for variant in ['ip','domain']:
  target=E/(variant+'-candidate');assert not target.exists();target.mkdir()
  files=dict(source);files['assets/social-footer.css']+=(E/'footer-styles.css').read_bytes()
  cssver=sha(files['assets/social-footer.css'])[:12]
  for name,b in list(files.items()):
   if not name.endswith('.html'):continue
   s=b.decode();assert s.count('</footer>')==1 and 'footer-filing' not in s
   s=s.replace('  </footer>',(E/'footer-markup.txt').read_text()+'  </footer>')
   s=re.sub(r'(assets/social-footer\.css\?v=)[a-f0-9]+',lambda x:x[1]+cssver,s)
   s=s.replace(m['revision'],'__PORTFOLIO_REVISION__')
   if variant=='domain':s=s.replace('http://[REDACTED_HOST]/sites/portfolio/','http://www.eliai.cn/')
   assert 'noindex,nofollow' in s and s.count('浙ICP备2026044062号-2')==1
   files[name]=s.encode()
  digest=hashlib.sha256()
  for name,b in sorted(files.items()):digest.update(name.encode()+b'\0'+b+b'\0')
  revision=digest.hexdigest()[:20]
  files={n:b.replace(b'__PORTFOLIO_REVISION__',revision.encode()) if n.endswith('.html') else b for n,b in files.items()}
  for n,b in files.items():
   p=target/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  out=E/(variant+'.tar.gz')
  with tarfile.open(out,'w:gz',format=tarfile.USTAR_FORMAT) as t:
   for n,b in sorted(files.items()):
    ti=tarfile.TarInfo(n);ti.size=len(b);ti.mode=0o644;ti.uid=ti.gid=0;ti.mtime=0;t.addfile(ti,io.BytesIO(b))
  with tarfile.open(out) as t:
   for ti in t.getmembers():assert ti.isreg() and not ti.pax_headers and not any(p.startswith('.') or p=='..' for p in PurePosixPath(ti.name).parts)
  # All original payload outside footer/style and release marker must remain exact.
  for n,b in files.items():
   if n.endswith('.html'):
    s=b.decode().replace(revision,m['revision']).replace((E/'footer-markup.txt').read_text(),'')
    s=re.sub(r'(assets/social-footer\.css\?v=)[a-f0-9]+',lambda x:x[1]+sha(source['assets/social-footer.css'])[:12],s)
    if variant=='domain':s=s.replace('http://www.eliai.cn/','http://[REDACTED_HOST]/sites/portfolio/')
    assert s==source[n].decode(),n
   elif n!='assets/social-footer.css':assert b==source[n],n
  plan['variants'][variant]={'revision':revision,'sha256':sha(out.read_bytes()),'file_hashes':{n:sha(b) for n,b in files.items()},'target':('/srv/eli-sites/portfolio/releases/' if variant=='ip' else '/srv/eli-sites/portfolio/domain-releases/')+release,'package':str(out)}
 (E/'manifest.json').write_text(json.dumps(plan,indent=2));print(json.dumps({'release':release,'variants':{k:{'revision':v['revision'],'files':len(v['file_hashes']),'sha256':v['sha256']} for k,v in plan['variants'].items()}}))
