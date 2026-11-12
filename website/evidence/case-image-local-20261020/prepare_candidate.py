"""Prepare a reproducible LOCAL package; never upload, connect or deploy."""
from pathlib import Path
import json,hashlib,re,tarfile,gzip,io
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
previous=json.loads((ROOT/'evidence/deploy-home-industries-20261020/plan.json').read_text())
verification=json.loads((ROOT/'verification-files/manifest.json').read_text())['public_root_files']
revision=re.search(r'portfolio-revision" content="([^"]+)',(ROOT/'dist/index.html').read_text())[1]
assert revision=='87919417171750dd1242'
inputs={name:(ROOT/'verification-files'/name if name in verification else ROOT/'dist'/name)
        for name in sorted(previous['files'])}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,source in inputs.items():
    assert source.is_file() and not source.is_symlink()
    assert not Path(name).is_absolute() and not any(x.startswith('.') or x=='..' for x in Path(name).parts)
files={name:sha(source) for name,source in inputs.items()}
assert all(files[name]==digest for name,digest in verification.items())
changed=[name for name in files if files[name]!=previous['files'][name]]
assert all(name.endswith('.html') or name=='sitemap.xml' for name in changed),changed
package=OUT/('20261020-seo-geo-'+revision[:8]+'.tar.gz')
assert not package.exists()
with package.open('xb') as raw:
    with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0) as gz:
        with tarfile.open(fileobj=gz,mode='w',format=tarfile.USTAR_FORMAT) as archive:
            for name,source in inputs.items():
                data=source.read_bytes();info=tarfile.TarInfo(name);info.size=len(data)
                info.mode=0o644;info.mtime=info.uid=info.gid=0;info.uname=info.gname=''
                archive.addfile(info,io.BytesIO(data))
with tarfile.open(package) as archive:
    members=archive.getmembers()
    assert len(members)==len(files) and {m.name for m in members}==set(files)
    assert all(m.isreg() and not m.pax_headers for m in members)
    assert all(hashlib.sha256(archive.extractfile(m).read()).hexdigest()==files[m.name] for m in members)
plan={'status':'LOCAL_PACKAGE_ONLY_PENDING_PUBLICATION_APPROVAL','revision':revision,
      'baseline_last_confirmed_revision':previous['revision'],
      'baseline_source':'Prior successful release manifest, not a new server preflight',
      'publication_authorized':False,'live_preflight_required_before_upload':True,
      'package':str(package),'package_sha256':sha(package),'archive_bytes':package.stat().st_size,
      'public_file_count':len(files),'files':files,'changed_files_vs_prior_manifest':changed,
      'verification_files_preserved':list(verification),'new_assets':[],
      'excluded_stale_dist_files':sorted(str(p.relative_to(ROOT/'dist')) for p in (ROOT/'dist').rglob('*')
                                        if p.is_file() and str(p.relative_to(ROOT/'dist')) not in files),
      'scope':'294 approved author descriptions, 6 article link corrections and 4 case responsive img references; no CSS/JS/media edits',
      'server_operations':0,'search_submissions':0}
(OUT/'candidate-package.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:plan[k] for k in ['status','revision','public_file_count','archive_bytes','package_sha256']},ensure_ascii=False))
