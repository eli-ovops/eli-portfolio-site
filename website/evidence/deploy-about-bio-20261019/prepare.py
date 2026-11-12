from pathlib import Path
import sys,json,hashlib,re,tarfile,io,gzip,datetime,xml.etree.ElementTree as ET,difflib,html
R=Path(__file__).resolve().parents[2];E=Path(__file__).resolve().parent;D=R/'dist'
sys.path.insert(0,str(R/'scripts'))
from page_updates import fingerprint
sha=lambda b:hashlib.sha256(b).hexdigest()
B=json.loads((E/'preflight.json').read_text())
old=json.loads((R/'evidence/deploy-article-metadata-20261018/plan.json').read_text())
assert B['previous']==old['target'] and B['files']==old['files']
with tarfile.open(old['package']) as t:
    before={m.name:t.extractfile(m).read() for m in t.getmembers()}
assert {n:sha(b) for n,b in before.items()}==B['files']
verification=json.loads((R/'verification-files/manifest.json').read_text())['public_root_files']
blobs={}
for n in sorted(B['files']):
    p=R/'verification-files'/n if n in verification else D/n
    assert p.is_file() and not p.is_symlink(),n
    blobs[n]=p.read_bytes()
    if n in verification:assert sha(blobs[n])==verification[n]==B['files'][n]
html_changes=[]
for n,b in blobs.items():
    if not n.endswith('.html') or n in verification:continue
    if fingerprint(before[n].decode())!=fingerprint(b.decode()):html_changes.append(n)
assert sorted(html_changes)==['about.html','en/about.html'],html_changes
changed_non_html=[n for n in blobs if not n.endswith('.html') and sha(blobs[n])!=B['files'][n]]
assert sorted(changed_non_html)==['llms.txt','sitemap.xml'],changed_non_html
old_phrase='Agree tool subscriptions, development, training and maintenance separately.'
new_phrase="We'll agree separately on the scope and fees for tool subscriptions, development, training and maintenance."
assert before['llms.txt'].decode().replace(old_phrase,new_phrase)==blobs['llms.txt'].decode()
def dates(data):
    ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    return {u.find('s:loc',ns).text:u.find('s:lastmod',ns).text for u in ET.fromstring(data).findall('s:url',ns)}
a,b=dates(before['sitemap.xml']),dates(blobs['sitemap.xml'])
assert a.keys()==b.keys() and len(b)==294
changed_dates=[u for u in b if a[u]!=b[u]]
assert sorted(changed_dates)==['https://www.eliai.cn/about.html','https://www.eliai.cn/en/about.html']
assert all(b[u]=='2026-10-19' for u in changed_dates)
assert '你好，我是 Eli，一名来自中国的独立开发者。' in blobs['about.html'].decode()
assert "Hi, I'm Eli, an independent developer from China." in html.unescape(blobs['en/about.html'].decode())
for n in html_changes:
    text=blobs[n].decode();assert text.index('class="about-consult')<text.index('class="about-bio')
revision=re.search(r'portfolio-revision" content="([^"]+)',blobs['about.html'].decode()).group(1)
assert revision=='0e8f1d0f8a593578ab3e'
for n in html_changes:
    (E/(n.replace('/','-')+'.diff')).write_text(''.join(difflib.unified_diff(before[n].decode().splitlines(True),blobs[n].decode().splitlines(True),fromfile='previous/'+n,tofile='candidate/'+n)))
release='20261019-about-bio-'+revision[:8];package=E/(release+'.tar.gz')
assert not package.exists()
with package.open('wb') as f:
    with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0) as gz:
        with tarfile.open(fileobj=gz,mode='w',format=tarfile.USTAR_FORMAT) as t:
            for n,data in sorted(blobs.items()):
                info=tarfile.TarInfo(n);info.size=len(data);info.mode=0o644;info.mtime=0;info.uid=info.gid=0
                t.addfile(info,io.BytesIO(data))
with tarfile.open(package) as t:
    members=t.getmembers();assert len(members)==len(blobs)
    assert all(m.isreg() and not m.pax_headers and not m.name.startswith('/') and all(not p.startswith('.') for p in Path(m.name).parts) and sha(t.extractfile(m).read())==sha(blobs[m.name]) for m in members)
P=dict(release=release,revision=revision,previous=B['previous'],target='/srv/eli-sites/portfolio/domain-releases/'+release,package=str(package),package_sha256=sha(package.read_bytes()),files={n:sha(data) for n,data in blobs.items()},changed_assets=changed_non_html,created_at=datetime.datetime.now().astimezone().isoformat(),authorized_scope='User2026-10-19: publish approved bilingual About biography and three reviewed fixes; preserve visuals/motion; no search submissions',verification_files=verification)
(E/'plan.json').write_text(json.dumps(P,indent=2)+'\n')
checks=dict(status='PASS',revision=revision,public_files=len(blobs),html_pages=296,semantic_html_changes=html_changes,unchanged_html_except_cache_revision=294,changed_non_html=changed_non_html,changed_sitemap_dates=changed_dates,sitemap_urls=294,verification_files_preserved=len(verification),all_visual_motion_assets_unchanged=True,package_bytes=package.stat().st_size,package_sha256=P['package_sha256'])
(E/'package-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
(E/'artifacts.md').write_text('This directory contains the reviewed deployment scripts, exact public-only archive, preflight, validation, publication and postflight receipts, public hashes and browser QA. All are retained for release audit and rollback; no source, secret or private evidence is in the public package.\n')
print(json.dumps(checks,indent=2))
