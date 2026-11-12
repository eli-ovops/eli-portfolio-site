"""Package only the reviewed homepage industry change and known public files."""
from pathlib import Path
import json, hashlib, re, sys, tarfile, gzip, io, shutil

r = Path(__file__).resolve().parents[2]
e = Path(__file__).resolve().parent
b = json.loads((e / 'preflight.json').read_text())
d = r / 'dist'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
review = json.loads((r / 'evidence/home-industries-local-20261020/refinement/receipt.json').read_text())
assert all(sha(r / name) == digest for name, digest in review['changed_files_sha256'].items())
revision = re.search(r'name="portfolio-revision" content="([^"]+)', (d / 'index.html').read_text())[1]
assert revision == review['revision'] == 'fcafe9ca8a0e904465b2'
verification = json.loads((r / 'verification-files/manifest.json').read_text())['public_root_files']
new_assets = ['assets/industry-scenarios.css', 'assets/industry-scenarios.js']
inputs = {}
for name in sorted(set(b['files']) | set(new_assets)):
    source = r / 'verification-files' / name if name in verification else d / name
    assert source.is_file() and not source.is_symlink(), name
    assert not any(part.startswith('.') or part == '..' for part in Path(name).parts)
    inputs[name] = source
files = {name: sha(source) for name, source in inputs.items()}
assert all(files[name] == digest for name, digest in verification.items())
changed_assets = ['asset-manifest.json', 'sitemap.xml']
unchanged = [name for name in b['files'] if not name.endswith('.html') and name not in changed_assets]
assert all(files[name] == b['files'][name] for name in unchanged)

sys.path.insert(0, str(r / 'scripts'))
from page_updates import fingerprint
old_plan = json.loads((r / 'evidence/deploy-home-article-rotator-20261019/plan.json').read_text())
assert old_plan['files'] == b['files'] and old_plan['target'] == b['previous']
assert sha(Path(old_plan['package'])) == old_plan['package_sha256']
changed = []
with tarfile.open(old_plan['package']) as old:
    for name in b['files']:
        if not name.endswith('.html') or name in verification:
            continue
        raw = old.extractfile(name).read()
        assert hashlib.sha256(raw).hexdigest() == b['files'][name]
        if fingerprint(raw.decode('utf-8')) != fingerprint(inputs[name].read_text()):
            changed.append(name)
assert set(changed) == {'index.html', 'en/index.html'}, changed

release = '20261020-home-industries-fcafe9ca'
package = e / (release + '.tar.gz')
assert not package.exists()
with package.open('xb') as raw:
    with gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode='w', format=tarfile.USTAR_FORMAT) as archive:
            for name, source in inputs.items():
                content = source.read_bytes()
                info = tarfile.TarInfo(name)
                info.size = len(content)
                info.mode = 0o644
                info.mtime = info.uid = info.gid = 0
                info.uname = info.gname = ''
                archive.addfile(info, io.BytesIO(content))
with tarfile.open(package) as archive:
    members = archive.getmembers()
    assert {m.name for m in members} == set(files) and len(members) == len(files)
    assert all(m.isreg() and not m.pax_headers for m in members)
    assert all(hashlib.sha256(archive.extractfile(m).read()).hexdigest() == files[m.name] for m in members)
checks = ['index.html', 'en/index.html'] + new_assets + [
    'assets/depth-gallery.js', 'assets/stacked-gallery.css', 'assets/home-ambient.js',
    'assets/home-ambient.css', 'assets/article-rotator.js', 'assets/article-rotator.css',
    'about.html', 'en/about.html', 'sitemap.xml', 'robots.txt', 'llms.txt',
    'cases/p10.html', 'en/cases/p36.html']
checks += [prefix + 'services/' + slug + '.html' for prefix in ['', 'en/']
           for slug in ['fde-consulting', 'workflow-automation', 'ai-agent']]
checks += list(verification)
assert len(checks) == len(set(checks))
plan = dict(release=release, revision=revision, previous=b['previous'],
            target='/srv/eli-sites/portfolio/domain-releases/' + release,
            package=str(package), package_sha256=sha(package), files=files,
            public_checks=checks, changed_assets=changed_assets,
            publication_authorized=True,
            authorization='2026-10-20 user: upload this finalized bilingual homepage industry version to server',
            scope='Eight bilingual homepage industry disclosures and approved final wording only; no search submissions',
            semantic_html_changed=changed, new_assets=new_assets,
            archive_bytes=package.stat().st_size)
(e / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
shutil.copy2(r / 'evidence/deploy-home-article-rotator-20261019/deploy.py', e / 'deploy.py')
print(json.dumps({key: plan[key] for key in ['revision', 'release', 'semantic_html_changed', 'archive_bytes', 'package_sha256']}))
print('Verified files', len(files), 'public checks', len(checks), 'unchanged public assets', len(unchanged))
