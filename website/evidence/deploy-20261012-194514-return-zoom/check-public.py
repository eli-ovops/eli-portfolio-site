from pathlib import Path
import json,hashlib,urllib.request,urllib.error,concurrent.futures
here=Path(__file__).resolve().parent
manifest=json.loads((here/'package-manifest.json').read_text())
base='http://[REDACTED_HOST]/sites/portfolio/'
expected={p:digest for p,digest in manifest['file_hashes'].items() if Path(p).suffix in ['.html','.css','.js','.json','.txt']}
def verify(item):
    path,digest=item
    with urllib.request.urlopen(base+path,timeout=20) as response:
        data=response.read();assert response.status==200
        assert hashlib.sha256(data).hexdigest()==digest,('Public hash mismatch',path)
        if path.endswith('.html'):assert b'<meta name="robots" content="noindex,nofollow">' in data,path
        if path=='robots.txt':assert data==b'User-agent: *\nDisallow: /\n'
        return {'path':path,'status':200,'sha256_matches':True,'robots_header':response.headers.get('X-Robots-Tag')}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:checks=list(pool.map(verify,expected.items()))
private={}
for path in ['sitemap.xml','content/seo.json','scripts/seo.py','evidence/seo-geo-20261012/receipt.json','.git/config','assets/img01.webp','cases/']:
    try:
        with urllib.request.urlopen(base+path,timeout=15) as response:raise AssertionError(('Unexpected public path',path,response.status))
    except urllib.error.HTTPError as error:
        assert error.code in ([403,404] if path=='cases/' else [404]),(path,error.code)
        private[path]=error.code
erp={}
for path in ['login','mobile/']:
    with urllib.request.urlopen('http://[REDACTED_HOST]/'+path,timeout=15) as response:
        assert response.status==200;erp[path]=response.status
result={'date':'2026-10-12','status':'PUBLIC_CHECKS_PASS','release':manifest['release'],'text_files_verified':len(checks),'html_pages_noindex':sum(p.endswith('.html') for p in expected),'robots':'Disallow: / at portfolio path','sitemap_public':False,'private_paths':private,'erp_entry_pages':erp,'checks':checks}
(here/'public-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False))
