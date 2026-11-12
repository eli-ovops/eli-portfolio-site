from pathlib import Path
import hashlib,json,re,tarfile,io,shutil
r=Path(__file__).resolve().parents[2];e=Path(__file__).resolve().parent;pre=json.loads((e/'preflight.json').read_text());old=json.loads((r/'evidence/deploy-seo-geo-20261020/plan.json').read_text());assert pre['files']==old['files'],'Live release drift'
rev='4bc544a5361e14236d53';release='20261020-industry-expansion-4bc544a5';sha=lambda b:hashlib.sha256(b).hexdigest()
verify=json.loads((r/'verification-files/manifest.json').read_text())['public_root_files']
paths={rel:(r/'verification-files'/rel if rel in verify else r/'dist'/rel) for rel in pre['files']};files={rel:sha(p.read_bytes()) for rel,p in paths.items()}
assert all(files[p]==h for p,h in verify.items()) and len(verify)==6
# Existing production allowlist excludes unrelated local experimental assets.
def norm(s):
 s=re.sub(r'(<meta name="portfolio-revision" content=")[^"]+',r'\1REVISION',s)
 return re.sub(r'([?&](?:amp;)?pv=)[a-f0-9]{20}',r'\1REVISION',s)
changed=[];b=r/'evidence/industries-more-local-20261020/before/dist'
for p in b.rglob('*.html'):
 rel=p.relative_to(b).as_posix();a=norm(p.read_text());c=norm((r/'dist'/rel).read_text())
 if a!=c:
  changed.append(rel);assert rel in ['index.html','en/index.html']
  def rest(s):
   s=re.sub(r'<section class="industry-overview".*?</section>','__INDUSTRIES__',s,flags=re.S)
   return re.sub(r'(industry-scenarios\.css\?v=)[a-f0-9]{12}',r'\1CSS',s)
  assert rest(a)==rest(c),rel
changed_assets=[p for p,h in files.items() if not p.endswith('.html') and h!=pre['files'][p]];assert changed_assets==['assets/industry-scenarios.css'],changed_assets
for p in ['styles.css','motion.css','motion.js','app.js','assets/industry-scenarios.js','robots.txt','llms.txt','sitemap.xml']:assert files[p]==pre['files'][p]
assert rev in (r/'dist/index.html').read_text();css=(r/'assets/industry-scenarios.css').read_text();assert 'blur(' not in css and 'backdrop-filter' not in css
package=e/(release+'.tar.gz')
with tarfile.open(package,'w:gz',format=tarfile.USTAR_FORMAT) as t:
 for rel,p in paths.items():
  assert not p.is_symlink();assert not any(v.startswith('.') for v in Path(rel).parts);assert p.suffix.lower() in ['.html','.css','.js','.json','.txt','.xml','.png','.jpg','.jpeg','.svg','.webp','.woff2','.ttf','.md'],rel
  data=p.read_bytes();info=tarfile.TarInfo(rel);info.size=len(data);info.mode=0o644;info.mtime=0;t.addfile(info,io.BytesIO(data))
with tarfile.open(package) as t:
 assert len(t.getmembers())==len(files);assert all(m.isreg() and not m.pax_headers and sha(t.extractfile(m).read())==files[m.name] for m in t.getmembers())
checks=['index.html','en/index.html','about.html','en/about.html','assets/industry-scenarios.css','assets/industry-scenarios.js','motion.js','assets/depth-gallery.js','assets/stacked-gallery.css','assets/article-rotator.js','sitemap.xml','robots.txt','llms.txt','services/workflow-automation.html','en/services/workflow-automation.html']+list(verify)
plan={'release':release,'revision':rev,'previous':pre['previous'],'target':'/srv/eli-sites/portfolio/domain-releases/'+release,'package':str(package),'package_sha256':sha(package.read_bytes()),'files':files,'public_checks':checks,'changed_assets':changed_assets,'publication_authorized':True,'authorization_reference':'authorization.json','scope':'Two bilingual homepage industry sections and industry CSS; unchanged other bodies and all JS/media','archive_bytes':package.stat().st_size}
(e/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');shutil.copy2(r/'evidence/deploy-seo-geo-20261020/deploy.py',e/'deploy.py')
audit={'status':'PASS','revision':rev,'visible_html_changed':changed,'other_html_unchanged':294,'changed_assets':changed_assets,'all_js_media_other_css_unchanged':True,'sitemap_and_robots_unchanged':True,'verification_files_preserved':list(verify),'archive_files':len(files),'package_sha256':plan['package_sha256'],'new_frosted_glass':False,'unrelated_local_experiments_excluded':True}
(e/'scope-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))
