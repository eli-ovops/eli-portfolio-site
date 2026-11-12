from pathlib import Path
import hashlib, json, tarfile, io
from datetime import datetime, timezone

r = Path(__file__).resolve().parents[2]
e = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
baseline = json.loads((r/'evidence/deploy-industry-expansion-20261020/deployed-manifest.json').read_text())
verify = json.loads((r/'verification-files/manifest.json').read_text())['public_root_files']
paths = {rel: (r/'verification-files'/rel if rel in verify else r/'dist'/rel) for rel in baseline}
files = {rel: sha(p) for rel,p in paths.items()}
assert all(files[p] == h for p,h in verify.items()) and len(verify) == 6
scope = json.loads((r/'evidence/stable-urls-case-services-local-20261021/scope-checks.json').read_text())
assert scope['status'] == 'PASS'
assert scope['revision'] in (r/'dist/index.html').read_text()
assets = [p for p,h in files.items() if not p.endswith('.html') and h != baseline[p]]
assert set(assets) == {'assets/page-version.js', 'sitemap.xml'}, assets
for rel in scope['visual_motion_files_byte_unchanged']:
    # The local preview also holds inactive experiments, absent from production.
    if rel in baseline:
        assert files[rel] == baseline[rel], rel
release = '20261021-stable-urls-'+scope['revision'][:8]
package = e/(release+'.tar.gz')
assert not package.exists()
with tarfile.open(package, 'w:gz', format=tarfile.USTAR_FORMAT) as t:
    for rel,p in paths.items():
        assert p.is_file() and not p.is_symlink()
        assert not any(x.startswith('.') or x == '..' for x in Path(rel).parts)
        data=p.read_bytes(); info=tarfile.TarInfo(rel)
        info.size=len(data); info.mode=0o644; info.mtime=0
        t.addfile(info,io.BytesIO(data))
with tarfile.open(package) as t:
    assert len(t.getmembers()) == len(files)
    assert all(m.isreg() and not m.pax_headers and
               hashlib.sha256(t.extractfile(m).read()).hexdigest() == files[m.name]
               for m in t.getmembers())
plan = dict(publication_authorized=True, authorization_reference='authorization.json',
    release=release, revision=scope['revision'],
    previous_expected='/srv/eli-sites/portfolio/domain-releases/20261020-industry-expansion-4bc544a5',
    target='/srv/eli-sites/portfolio/domain-releases/'+release, package=str(package),
    package_sha256=sha(package), files=files, changed_assets=assets,
    scope='Stable page URLs and six bilingual case-to-service links; visuals/motion unchanged',
    verification_files_preserved=list(verify),
    live_preflight_status='BLOCKED_SSH_AUTHENTICATION; no upload or switch performed')
(e/'plan.json').write_text(json.dumps(plan,indent=2))
receipt = dict(checked_at=datetime.now(timezone.utc).isoformat(),
    status='BLOCKED_SSH_AUTHENTICATION', candidate_revision=scope['revision'],
    package_ready=True, package_sha256=plan['package_sha256'], public_files=len(files),
    changed_non_html_files=assets, production_uploads=0, production_switches=0,
    search_submissions=0, security_changes=0, ssh_attempts=1,
    error='Permission denied (publickey,password)',
    cause='UNKNOWN; guide records authorized key expiry 20261020235959, now passed; not verified on server')
(e/'receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt,indent=2))
