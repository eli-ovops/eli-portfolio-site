from pathlib import Path
import re,sys,json,hashlib,subprocess
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'scripts'))
from page_versions import canonical_home_links

def scrub(s):
 s=re.sub(r'(<meta name="portfolio-revision" content=")[^"]*(")',r'\1REV\2',s)
 return re.sub(r'(src="[^"]*assets/page-version\.js)\?v=[a-f0-9]{12}',r'\1?v=ASSET',s)
count=0
for p in (D/'before/dist').rglob('*.html'):
 path=p.relative_to(D/'before/dist');old=p.read_text();new=(R/'dist'/path).read_text()
 assert scrub(canonical_home_links(old,path.as_posix()))==scrub(new),path
 assert not re.search(r'<a\b[^>]*\bhref="[^"#?]*index\.html(?:[?#][^"]*)?"',new),path
 count+=1
cases=[('cases/p10.html','../index.html?project=p10&amp;return=p09#work','/?project=p10&amp;return=p09#work'),('en/articles/what-is-agent.html','../index.html#needs','/en/#needs'),('index.html','#work','#work'),('en/index.html','#main','#main'),('index.html','https://other.test/index.html?project=p10#work','https://other.test/index.html?project=p10#work')]
for page,href,expected in cases:
 assert canonical_home_links('<a href="'+href+'">same text</a>',page)=='<a href="'+expected+'">same text</a>'
baseline=json.loads((D/'baseline-dist-hashes.json').read_text());changes=[p for p,h in baseline.items() if p.endswith(('.css','.js','.woff2','.png','.jpg','.svg','.webp')) and (R/'dist'/p).is_file() and hashlib.sha256((R/'dist'/p).read_bytes()).hexdigest()!=h]
assert changes==['assets/page-version.js'],changes
logs=[]
for script in ['check_navigation_version.cjs','check_home_case_return.cjs','check_return_owner.cjs','check_service_return.cjs','check_home_entry.cjs']:
 r=subprocess.run(['node',str(R/'scripts'/script)],text=True,capture_output=True);logs.append({'script':script,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0,(script,r.stderr)
revision=re.search('name="portfolio-revision" content="([a-f0-9]+)"',(R/'dist/index.html').read_text())[1]
result={'html_pages':count,'body_text_and_other_markup_unchanged':True,'home_alias_hrefs_remaining':0,'static_url_semantic_cases':len(cases),'changed_media_css_js':changes,'presentation_css_motion_media_unchanged':True,'revision':revision,'navigation_tests':logs,'publication':False,'search_submissions':0}
(D/'diff-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
