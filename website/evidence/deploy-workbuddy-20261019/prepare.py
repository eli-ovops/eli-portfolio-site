"""Prepare the approved static release; this script never connects or publishes."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json, sys, hashlib, re, tarfile, gzip, io
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
from page_updates import fingerprint

sha = lambda data: hashlib.sha256(data).hexdigest()
prior = json.loads((ROOT / 'evidence/deploy-about-bio-20261019/plan.json').read_text())
scope = json.loads((ROOT / 'evidence/workbuddy-local-20261019/scope-check.json').read_text())
verification = json.loads((ROOT / 'verification-files/manifest.json').read_text())['public_root_files']
with tarfile.open(prior['package']) as archive:
    before = {m.name: archive.extractfile(m).read() for m in archive.getmembers()}
assert {name: sha(data) for name, data in before.items()} == prior['files']
blobs = {}
for name in sorted(prior['files']):
    path = ROOT / ('verification-files' if name in verification else 'dist') / name
    assert path.is_file() and not path.is_symlink(), name
    blobs[name] = path.read_bytes()
    if name in verification:
        assert sha(blobs[name]) == verification[name] == prior['files'][name]

changed_html = [name for name, data in blobs.items()
                if name.endswith('.html') and name not in verification
                and fingerprint(data.decode()) != fingerprint(before[name].decode())]
assert sorted(changed_html) == scope['normalized_changed_html']
assert sorted(changed_html) == ['articles.html', 'articles/what-is-workbuddy.html',
                               'en/articles.html', 'en/articles/what-is-workbuddy.html']
changed_non_html = [name for name, data in blobs.items()
                    if not name.endswith('.html') and sha(data) != prior['files'][name]]
assert changed_non_html == ['sitemap.xml'], changed_non_html
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
def dates(raw):
    return {u.find('s:loc', ns).text: u.find('s:lastmod', ns).text
            for u in ET.fromstring(raw).findall('s:url', ns)}
old_dates, new_dates = dates(before['sitemap.xml']), dates(blobs['sitemap.xml'])
assert old_dates.keys() == new_dates.keys() and len(new_dates) == 294
date_changes = [u for u in new_dates if old_dates[u] != new_dates[u]]
assert set(date_changes) == {'https://www.eliai.cn/' + name for name in changed_html}
assert all(new_dates[u] == '2026-10-19' for u in date_changes)
revision = re.search(r'portfolio-revision" content="([^"]+)',
                     blobs['articles/what-is-workbuddy.html'].decode()).group(1)
assert revision == scope['revision'] == 'e2be96987b2798068e82'
release = '20261019-workbuddy-' + revision[:8]
package = OUT / (release + '.tar.gz')
assert not package.exists(), 'Do not overwrite a prepared release'
with package.open('xb') as stream:
    with gzip.GzipFile(filename='', fileobj=stream, mode='wb', mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode='w', format=tarfile.USTAR_FORMAT) as archive:
            for name, data in sorted(blobs.items()):
                entry = tarfile.TarInfo(name)
                entry.size = len(data)
                entry.mode = 0o644
                entry.mtime = entry.uid = entry.gid = 0
                archive.addfile(entry, io.BytesIO(data))
with tarfile.open(package) as archive:
    entries = archive.getmembers()
    assert len(entries) == len(blobs) and len({m.name for m in entries}) == len(entries)
    for entry in entries:
        assert entry.isreg() and not entry.pax_headers and not entry.name.startswith('/')
        assert all(not p.startswith('.') and p != '..' for p in Path(entry.name).parts)
        assert sha(archive.extractfile(entry).read()) == sha(blobs[entry.name])
plan = dict(release=release, revision=revision, previous=prior['target'],
            target='/srv/eli-sites/portfolio/domain-releases/' + release,
            package=str(package), package_sha256=sha(package.read_bytes()),
            files={name: sha(data) for name, data in blobs.items()},
            changed_assets=changed_non_html, verification_files=verification,
            created_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
            authorized_scope='User2026-10-19: publish approved bilingual WorkBuddy introduction, title and search description; preserve visuals/motion; verify mobile, language switch and consultation; no search submissions',
            production_preflight_required=True)
(OUT / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
checks = dict(status='PREPARED_NOT_PUBLISHED', revision=revision, public_files=len(blobs),
              html_pages=296, semantic_html_changes=changed_html,
              other_page_content_unchanged=292, changed_non_html=changed_non_html,
              sitemap_urls=294, verification_files_preserved=len(verification),
              visual_motion_assets_unchanged=True, package_bytes=package.stat().st_size,
              package_sha256=plan['package_sha256'],
              production_current_state='UNKNOWN: strict SSH preflight connection closed',
              deployments=0, uploads=0, search_submissions=0)
(OUT / 'package-checks.json').write_text(json.dumps(checks, indent=2) + '\n')
print(json.dumps(checks, indent=2))
