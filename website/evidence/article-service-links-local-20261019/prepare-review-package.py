"""Create a local review archive from the previous approved public file list.

This script has no server connection, publishing or search-submission action.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone, timedelta
import gzip
import hashlib
import io
import json
import tarfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    previous = json.loads((ROOT / 'evidence/deploy-home-metadata-20261019/plan.json').read_text())
    accepted = json.loads((OUT / 'receipt.json').read_text())
    before = json.loads((OUT / 'before-public-hashes.json').read_text())
    assert accepted['status'] == 'LOCAL_QA_PASSED_NOT_PUBLISHED'
    assert accepted['revision'] == '5c2760c23a73225e2ff6'
    assert previous['revision'] == accepted['production_revision_unchanged']
    verification = previous['verification_files']
    registry = json.loads((ROOT / 'verification-files/manifest.json').read_text())['public_root_files']
    assert verification == registry
    # The local preview excludes ownership files. Domain packages add the exact
    # six registered public files from their maintained source directory.
    assert all(before.get(name) == digest for name, digest in previous['files'].items()
               if name not in verification)
    files = {}
    sources = {}
    for name in sorted(previous['files']):
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts
        source = ROOT / ('verification-files' if name in verification else 'dist') / name
        assert source.is_file() and not source.is_symlink()
        sources[name] = source
        files[name] = sha(source.read_bytes())
    assert len(files) == 365
    assert all(files[name] == digest for name, digest in verification.items())
    changed = [name for name in files if files[name] != previous['files'][name]]
    changed_non_html = [name for name in changed if not name.endswith('.html')]
    assert changed_non_html == ['sitemap.xml']
    assert not any(name.endswith(('.css', '.js')) for name in changed)
    archive = OUT / '20261019-article-service-links-5c2760c2.tar.gz'
    assert not archive.exists(), 'Do not overwrite an existing reviewed archive.'
    with archive.open('wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode='w', format=tarfile.USTAR_FORMAT) as tar:
                for name in files:
                    data = sources[name].read_bytes()
                    item = tarfile.TarInfo(name)
                    item.size = len(data)
                    item.mode = 0o644
                    item.uid = item.gid = 0
                    item.uname = item.gname = ''
                    item.mtime = 0
                    tar.addfile(item, io.BytesIO(data))
    with tarfile.open(archive, 'r:gz') as tar:
        members = tar.getmembers()
        assert len(members) == len(files)
        assert set(m.name for m in members) == set(files)
        for member in members:
            assert member.isfile() and not member.issym() and not member.islnk()
            assert sha(tar.extractfile(member).read()) == files[member.name]
    plan = dict(
        created_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        status='LOCAL_REVIEW_PACKAGE_READY_NOT_AUTHORIZED_TO_PUBLISH',
        publication_authorized=False,
        revision=accepted['revision'],
        comparison_baseline=previous['revision'],
        baseline_scope='Last verified public release; no fresh server access in package preparation.',
        archive=str(archive), archive_sha256=sha(archive.read_bytes()), archive_bytes=archive.stat().st_size,
        files=files, verification_files=verification,
        source_note='359 approved preview files plus six exact public ownership files from verification-files/manifest.json; not a blanket archive of dist.',
        package_members=365, semantic_html_changes=10,
        scope='Five bilingual tutorial topics: service anchor destinations and existing labels only. '
              'Ten real content-date ledger rows. CSS/JS, motion, other visible bodies preserved.',
        changed_non_html=changed_non_html,
        acceptance_receipt='receipt.json',
        requires_before_publication=['Explicit user approval of this reviewed scope',
                                     'Read-only current production/version/health preflight',
                                     'Stop on baseline drift or unrelated changes',
                                     'Preserve rollback release and all six verification files',
                                     'Atomic publication and independent public/mobile/navigation checks'],
        forbidden=['No upload, server command, release switch, email or search submission in this script'],
        server_actions=0, deployments=0, search_submissions=0,
        artifact_purpose='Retain archive and manifest for concrete user review and future approved release; no cleanup.')
    (OUT / 'release-review-plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:plan[k] for k in ['status','revision','package_members','semantic_html_changes',
                                        'archive_bytes','archive_sha256','publication_authorized',
                                        'server_actions','search_submissions']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
