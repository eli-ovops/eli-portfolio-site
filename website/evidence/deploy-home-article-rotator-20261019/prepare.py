from pathlib import Path
import json, hashlib, re, sys, tarfile, gzip, io, shutil

r = Path(__file__).resolve().parents[2]
e = Path(__file__).resolve().parent
b = json.loads((e / 'preflight.json').read_text())
d = r / 'dist'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
verification = json.loads((r / 'verification-files/manifest.json').read_text())['public_root_files']
new_assets = ['assets/article-rotator.css', 'assets/article-rotator.js']
# The build directory can contain historical preview assets. Publish the known
# live file set plus the two reviewed new files, never that directory wholesale.
inputs = {}
for name in sorted(set(b['files']) | set(new_assets)):
    source = r / 'verification-files' / name if name in verification else d / name
    assert source.is_file() and not source.is_symlink(), name
    inputs[name] = source
files = {name: sha(source) for name, source in inputs.items()}
assert all(files[name] == digest for name, digest in verification.items())
unchanged = [name for name in b['files'] if not name.endswith('.html') and name != 'asset-manifest.json']
assert all(files[name] == b['files'][name] for name in unchanged)
sys.path.insert(0, str(r / 'scripts'))
from page_updates import fingerprint
before = json.loads((r / 'evidence/home-article-rotator-20261019/before-html-fingerprints.json').read_text())
changed = [name for name in before if before[name] != fingerprint((d / name).read_text())]
assert set(changed) == {'index.html', 'en/index.html'}
revision = re.search(r'name="portfolio-revision" content="([^"]+)', (d / 'index.html').read_text())[1]
assert revision == 'db2a07f4b91429cb3f5c'
release = '20261019-home-article-rotator-db2a07f4'
package = e / (release + '.tar.gz')
assert not package.exists()
with package.open('xb') as raw:
    with gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode='w', format=tarfile.USTAR_FORMAT) as archive:
            for name, source in inputs.items():
                assert not any(part.startswith('.') or part == '..' for part in Path(name).parts)
                content = source.read_bytes()
                info = tarfile.TarInfo(name)
                info.size = len(content)
                info.mode = 0o644
                info.mtime = info.uid = info.gid = 0
                info.uname = info.gname = ''
                archive.addfile(info, io.BytesIO(content))
with tarfile.open(package) as archive:
    members = archive.getmembers()
    assert len(members) == len(files) and all(m.isreg() and not m.pax_headers for m in members)
    assert all(hashlib.sha256(archive.extractfile(m).read()).hexdigest() == files[m.name] for m in members)
checks = ['index.html', 'en/index.html'] + new_assets + [
    'assets/depth-gallery.js', 'assets/stacked-gallery.css', 'assets/home-ambient.js',
    'assets/home-ambient.css', 'assets/articles.css', 'assets/page-version.js',
    'about.html', 'en/about.html', 'sitemap.xml', 'robots.txt', 'llms.txt']
slugs = ['inventory-reconciliation', 'enterprise-knowledge-base', 'ai-inventory-exceptions',
         'ai-knowledge-base-start', 'owner-ai-first-step', 'what-is-agent', 'first-ai-task', 'what-is-skill']
checks += [prefix + 'articles/' + slug + '.html' for prefix in ['', 'en/'] for slug in slugs]
checks += ['cases/p10.html', 'en/cases/p36.html'] + list(verification)
plan = dict(release=release, revision=revision, previous=b['previous'],
            target='/srv/eli-sites/portfolio/domain-releases/' + release,
            package=str(package), package_sha256=sha(package), files=files,
            public_checks=checks, changed_assets=['asset-manifest.json'],
            publication_authorized=True,
            scope='Bilingual homepage upward article carousel only; preserve layout and other motion; no search submissions',
            semantic_html_changed=changed, new_assets=new_assets,
            archive_bytes=package.stat().st_size)
(e / 'plan.json').write_text(json.dumps(plan, indent=2))
shutil.copy2(r / 'evidence/deploy-article-service-links-20261019/deploy.py', e / 'deploy.py')
print(json.dumps({key: plan[key] for key in ['revision', 'release', 'semantic_html_changed', 'archive_bytes', 'package_sha256']}))
print('Verified files', len(files), 'public checks', len(checks), 'unchanged public assets', len(unchanged))
