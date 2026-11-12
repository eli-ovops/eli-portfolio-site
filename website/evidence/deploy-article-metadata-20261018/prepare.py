from pathlib import Path
import sys,json,hashlib,re,tarfile,io,gzip,datetime
from html import escape
R=Path(__file__).resolve().parents[2]; E=Path(__file__).resolve().parent; D=R/'dist'
sys.path.insert(0,str(R/'scripts'))
from page_updates import fingerprint
from check_article_metadata import Head
B=json.loads((E/'preflight.json').read_text()); sha=lambda b:hashlib.sha256(b).hexdigest()
verification=json.loads((R/'verification-files/manifest.json').read_text())['public_root_files']
oldplan=json.loads((R/'evidence/deploy-llms-utf8-20261017/plan.json').read_text())
assert B['previous']==oldplan['target'] and B['files']==oldplan['files']
assert len(B['files'])==365
with tarfile.open(oldplan['package']) as t:
    before={m.name:t.extractfile(m).read() for m in t.getmembers()}
assert {n:sha(b) for n,b in before.items()}==B['files']
blobs={}
for n in sorted(B['files']):
    p=R/'verification-files'/n if n in verification else D/n
    assert p.is_file() and not p.is_symlink(),n
    blobs[n]=p.read_bytes()
    if n in verification: assert sha(blobs[n])==verification[n]==B['files'][n]
assert {p.relative_to(D).as_posix() for p in D.rglob('*.html') if 'assets' not in p.relative_to(D).parts}=={n for n in blobs if n.endswith('.html') and n not in verification}
allowed={'sitemap.xml','asset-manifest.json','assets/page-version.js'}
changed=[n for n in blobs if sha(blobs[n])!=B['files'][n]]
assert all(n.endswith('.html') or n in allowed for n in changed)
description_changes=[]; body_checked=0
for n,b in blobs.items():
    if not n.endswith('.html') or n in verification: continue
    old=before[n].decode(); new=b.decode()
    assert fingerprint(re.search(r'<body\b.*',old,re.S).group())==fingerprint(re.search(r'<body\b.*',new,re.S).group()),n
    body_checked+=1
    a=Head(old).meta.get('description'); z=Head(new).meta.get('description')
    if a!=z:
        assert n.startswith(('articles/','en/articles/')),n
        description_changes.append(n)
        # Only the reviewed description may change, including its HTML/JSON encodings.
        head,rest=old.split('</head>',1)
        head=head.replace('content="'+escape(a,quote=True)+'"','content="'+escape(z,quote=True)+'"')
        head=head.replace('"description": '+json.dumps(a,ensure_ascii=False),'"description": '+json.dumps(z,ensure_ascii=False))
        old=head+'</head>'+rest
    assert fingerprint(old)==fingerprint(new),n
assert len(description_changes)==114 and body_checked==296
assert sha(blobs['llms.txt'])==B['files']['llms.txt']
revision=re.search(r'<meta name="portfolio-revision" content="([^"]+)"',blobs['index.html'].decode()).group(1)
assert revision=='066456f5df9368a90560'
release='20261018-article-metadata-'+revision[:8]; package=E/(release+'.tar.gz')
with package.open('wb') as f:
    with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0) as gz:
        with tarfile.open(fileobj=gz,mode='w',format=tarfile.USTAR_FORMAT) as t:
            for n,b in sorted(blobs.items()):
                info=tarfile.TarInfo(n); info.size=len(b);info.mode=0o644;info.mtime=0;info.uid=info.gid=0
                t.addfile(info,io.BytesIO(b))
with tarfile.open(package) as t:
    assert len(t.getmembers())==len(blobs)
    assert all(m.isreg() and not m.pax_headers and not m.name.startswith('/') and all(not p.startswith('.') for p in Path(m.name).parts) and sha(t.extractfile(m).read())==sha(blobs[m.name]) for m in t.getmembers())
P=dict(release=release,revision=revision,previous=B['previous'],target='/srv/eli-sites/portfolio/domain-releases/'+release,package=str(package),package_sha256=sha(package.read_bytes()),files={n:sha(b) for n,b in blobs.items()},changed_assets=sorted(allowed),created_at=datetime.datetime.now().astimezone().isoformat(),authorized_scope='User 2026-10-18: reviewed sitemap lastmod and bilingual article metadata only; preserve visuals and motion; no search submissions',verification_files=verification)
(E/'plan.json').write_text(json.dumps(P,indent=2))
checks=dict(status='PASS',revision=revision,files=len(blobs),package_bytes=package.stat().st_size,metadata_only_html=body_checked,descriptions_changed=len(description_changes),unchanged_non_version_assets=len([n for n in blobs if not n.endswith('.html') and n not in allowed]),changed_non_html=[n for n in changed if not n.endswith('.html')],verification_files_preserved=6,added_or_removed_public_files=0)
(E/'package-checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
