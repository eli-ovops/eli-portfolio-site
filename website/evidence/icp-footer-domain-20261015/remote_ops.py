import importlib.util,json,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('release_tools',E/'release.py');mod=importlib.util.module_from_spec(spec)
# release.py dispatch is guarded by its mode argument; importing for helpers uses this inert mode.
mode=sys.argv[1];sys.argv=['release.py','helpers'];spec.loader.exec_module(mod);sys.argv=['remote_ops.py',mode]
m=json.loads((E/'manifest.json').read_text());p=json.loads((E/'preflight.json').read_text())
header='''from pathlib import Path,PurePosixPath
import json,hashlib,tarfile,shutil,os,subprocess,datetime,urllib.request
'''+f'M={m!r}\nP={p!r}\n'+'''
root=Path('/srv/eli-sites/portfolio');release=M['release'];backup=root/'backups'/release
links={'ip':'public','domain':'domain-current'}
def sha(b):return hashlib.sha256(b).hexdigest()
def hashes(p):return {str(x.relative_to(p)):sha(x.read_bytes()) for x in sorted(p.rglob('*')) if x.is_file()}
def unchanged():
 for key,link in links.items():
  assert str((root/link).resolve())==P['links'][link]['target'],('Changed current',link)
  assert hashes(root/link)==P['links'][link]['files'],('Changed previous files',link)
 for file,digest in P['configs'].items():assert sha(Path(file).read_bytes())==digest,('Config changed',file)
'''
if mode=='upload':
 for variant,v in m['variants'].items():
  remote='/root/portfolio-'+m['release']+'-'+variant+'.tar.gz'
  args=['scp']+mod.SSH[1:-1]+[v['package'],'root@[REDACTED_HOST]:'+remote]
  x=subprocess.run(args,capture_output=True,text=True,timeout=90)
  assert x.returncode==0,x.stderr
 (E/'upload.json').write_text(json.dumps({'status':'UPLOADED_NOT_DEPLOYED','release':m['release']}));print('Uploaded two static packages; not deployed')
elif mode=='prepare':
 body='''unchanged()
assert not backup.exists();assert all(not Path(v['target']).exists() for v in M['variants'].values())
for key,v in M['variants'].items():
 package=Path('/root/portfolio-'+release+'-'+key+'.tar.gz');assert sha(package.read_bytes())==v['sha256']
 with tarfile.open(package) as t:
  seen=set()
  for ti in t.getmembers():
   p=PurePosixPath(ti.name);assert ti.isreg() and not ti.pax_headers and not p.is_absolute()
   assert not any(s.startswith('.') or s=='..' for s in p.parts)
   assert ti.name in v['file_hashes'] and ti.name not in seen;seen.add(ti.name)
   b=t.extractfile(ti).read();assert sha(b)==v['file_hashes'][ti.name]
   if ti.name.endswith('.html'):assert b'noindex,nofollow' in b and '浙ICP备2026044062号-2'.encode() in b
   if ti.name=='robots.txt':assert b==b'User-agent: *\\nDisallow: /\\n'
  assert seen==set(v['file_hashes']) and 'sitemap.xml' not in seen
backup.mkdir(mode=0o700)
(backup/'previous.json').write_text(json.dumps(P,indent=2))
for i,(file,digest) in enumerate(P['configs'].items()):
 shutil.copyfile(file,backup/('nginx-'+str(i)+'.conf'));os.chmod(backup/('nginx-'+str(i)+'.conf'),0o600)
for key,v in M['variants'].items():
 target=Path(v['target']);target.mkdir(mode=0o755)
 with tarfile.open('/root/portfolio-'+release+'-'+key+'.tar.gz') as t:
  for ti in t.getmembers():
   dst=target/ti.name;dst.parent.mkdir(parents=True,exist_ok=True)
   with dst.open('xb') as f:f.write(t.extractfile(ti).read())
   os.chmod(dst,0o644)
 assert hashes(target)==v['file_hashes']
unchanged()
print(json.dumps({'status':'PREPARED_NOT_SWITCHED','release':release,'files':{k:len(v['file_hashes']) for k,v in M['variants'].items()},'backup':str(backup)}))
'''
 print(json.dumps(mod.remote('prepare',header+body)))
elif mode=='switch':
 body='''unchanged()
assert backup.is_dir()
for s in ['nginx','erp-trial','mysql','redis-server']:assert subprocess.run(['systemctl','is-active','--quiet',s]).returncode==0,s
for key,v in M['variants'].items():assert hashes(Path(v['target']))==v['file_hashes']
for key,v in M['variants'].items():
 nextlink=root/(links[key]+'.next.'+release);assert not nextlink.exists() and not nextlink.is_symlink()
 os.symlink(v['target'],nextlink);os.replace(nextlink,root/links[key])
print(json.dumps({'status':'SWITCHED','release':release,'links':{k:str((root/link).resolve()) for k,link in links.items()},'time':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
'''
 print(json.dumps(mod.remote('switch',header+body)))
elif mode=='postcheck':
 body='''out={'files':{},'requests':[],'services':{}}
for key,v in M['variants'].items():
 assert str((root/links[key]).resolve())==v['target'];assert hashes(root/links[key])==v['file_hashes'];out['files'][key]=len(v['file_hashes'])
 assert hashes(Path(P['links'][links[key]]['target']))==P['links'][links[key]]['files']
 for file,digest in P['configs'].items():assert sha(Path(file).read_bytes())==digest
 base='http://[REDACTED_HOST]/sites/portfolio/' if key=='ip' else 'http://www.eliai.cn/'
 for n in ['index.html','about.html','records.html','en/index.html','en/records.html','cases/p10.html','assets/social-footer.css','robots.txt']:
  with urllib.request.urlopen(base+n,timeout=10) as resp:
   b=resp.read();assert sha(b)==v['file_hashes'][n],n
   out['requests'].append({'url':base+n,'status':resp.status,'sha256':sha(b),'noindex_header':resp.headers.get('X-Robots-Tag')})
 for n in ['sitemap.xml','content/profile.json','scripts/build.py','.git/config','assets/img17.jpg']:
  try:urllib.request.urlopen(base+n,timeout=10);raise AssertionError(n+' exposed')
  except urllib.error.HTTPError as error:assert error.code in (403,404),(n,error.code)
for s in ['nginx','erp-trial','mysql','redis-server']:
 out['services'][s]=subprocess.run(['systemctl','is-active',s],capture_output=True,text=True).stdout.strip();assert out['services'][s]=='active'
for u in ['http://[REDACTED_HOST]/login','http://[REDACTED_HOST]/mobile/']:
 with urllib.request.urlopen(u,timeout=10) as x:
  h=sha(x.read());before=next(y for y in P['domain_http'] if y['url']==u);assert h==before['sha256'];out['requests'].append({'url':u,'status':x.status,'unchanged':True})
print(json.dumps(out))
'''
 print(json.dumps(mod.remote('postcheck',header+body)))
