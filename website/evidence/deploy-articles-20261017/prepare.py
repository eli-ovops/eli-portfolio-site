from pathlib import Path
import json,hashlib,re,tarfile,io,gzip,datetime
R=Path(__file__).resolve().parents[2]; E=Path(__file__).resolve().parent;D=R/'dist';B=json.loads((E/'preflight.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
verification=json.loads((R/'verification-files/manifest.json').read_text())['public_root_files']
paths={p.relative_to(D).as_posix() for p in D.rglob('*.html') if 'assets' not in p.relative_to(D).parts}
assert len(paths)==296
paths |= set(json.loads((D/'asset-manifest.json').read_text()))|set(B['files'])|{'styles.css','motion.css','app.js','motion.js','robots.txt','sitemap.xml','llms.txt','asset-manifest.json','health.json'}
blobs={}
for name in sorted(paths):
 p=R/'verification-files'/name if name in verification else D/name
 assert p.is_file() and not p.is_symlink(),name
 blobs[name]=p.read_bytes()
 if name in verification:assert sha(blobs[name])==verification[name]==B['files'][name]
assert not any('flex-carousel' in n or 'portrait-editorial' in n or 'atmosphere-editorial' in n for n in blobs)
protected=json.loads((E/'source-before.json').read_text())['protected']
for n,h in protected.items():assert sha(blobs[n])==h==B['files'][n],n
allowed={'sitemap.xml','asset-manifest.json','assets/page-version.js'}
changed=[n for n,h in B['files'].items() if sha(blobs[n])!=h]
assert all(n.endswith('.html') or n in allowed for n in changed)
assert set(blobs)-set(B['files'])=={p for p in blobs if p.startswith(('articles/','en/articles/')) or p in ['articles.html','en/articles.html','assets/articles.css','assets/article-library.js']}
before=json.loads((E/'before/content/articles.json').read_text());after=json.loads((R/'content/articles.json').read_text());assert before['articles']==after['articles']
source=json.loads((E/'source-before.json').read_text())['hashes'];content_unchanged=[n for n in source if n.startswith('content/') and n not in ['content/articles.json','content/tutorials/README.md']];assert all(sha((R/n).read_bytes())==source[n] for n in content_unchanged)
revision=re.search(r'<meta name="portfolio-revision" content="([^"]+)"',blobs['index.html'].decode()).group(1)
release='20261017-articles-'+revision[:8];package=E/(release+'.tar.gz')
with package.open('wb') as f:
 with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0) as gz:
  with tarfile.open(fileobj=gz,mode='w',format=tarfile.USTAR_FORMAT) as t:
   for n,b in sorted(blobs.items()):
    info=tarfile.TarInfo(n);info.size=len(b);info.mode=0o644;info.mtime=0;info.uid=info.gid=0;t.addfile(info,io.BytesIO(b))
with tarfile.open(package) as t:
 assert len(t.getmembers())==len(blobs)
 for m in t.getmembers():
  assert m.isreg() and not m.pax_headers and not m.name.startswith('/') and all(not p.startswith('.') and p!='__MACOSX' for p in Path(m.name).parts)
  assert sha(t.extractfile(m).read())==sha(blobs[m.name])
P=dict(release=release,revision=revision,previous=B['previous'],target='/srv/eli-sites/portfolio/domain-releases/'+release,package=str(package),package_sha256=sha(package.read_bytes()),files={n:sha(b) for n,b in blobs.items()},changed_assets=sorted(allowed),created_at=datetime.datetime.now().astimezone().isoformat(),authorized_scope='102 reviewed bilingual topics, navigation and article return; existing visual/motion unchanged; no search submissions',git_commit=None,git_reason='Static source directory has no Git repository',verification_files=verification,protected=protected,content_sources_unchanged=content_unchanged)
(E/'plan.json').write_text(json.dumps(P,indent=2,ensure_ascii=False));(E/'package-checks.json').write_text(json.dumps(dict(status='PASS',files=len(blobs),bytes=package.stat().st_size,added=len(set(blobs)-set(B['files'])),changed_non_html=[n for n in changed if not n.endswith('.html')],verification_files_preserved=6,protected_visual_files=len(protected),stale_experiments_excluded=True),indent=2))
print((E/'package-checks.json').read_text());print('REVISION',revision)
