import urllib.request,urllib.error,json,hashlib,re,concurrent.futures
from pathlib import Path
from datetime import datetime,timezone
D=Path(__file__).resolve().parent
before=json.loads((D/'preflight.json').read_text())
base='https://www.eliai.cn'
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl): return None
routes={'/articles/':'/articles.html','/en/articles/':'/en/articles.html','/en/cases/':'/en/records.html','/services/':'/index.html#needs','/en/services/':'/en/index.html#needs','/cases/':'/records.html'}
def route(item):
    src,target=item
    try:
        response=urllib.request.build_opener(NoRedirect).open(base+src,timeout=20)
    except urllib.error.HTTPError as e: response=e
    status=response.code; loc=response.headers.get('Location');response.close()
    assert status==301 and loc==base+target,(src,status,loc)
    with urllib.request.urlopen(base+src,timeout=20) as r:
        body=r.read().decode(); final=r.url
        assert r.status==200
        if '#needs' in target: assert 'id="needs"' in body and final==base+target
        return {'source':base+src,'status':status,'location':loc,'follow_status':r.status,'final_url':final}
paths=['index.html','en/index.html','records.html','en/records.html','articles.html','en/articles.html']
for lang in ['','en/']:
    paths += [lang+'cases/'+p+'.html' for p in ['p09','p10','p36']]
    paths += [lang+'services/'+p+'.html' for p in ['ai-agent','workflow-automation','fde-consulting']]
    paths += [lang+'articles/'+p+'.html' for p in ['inventory-reconciliation','enterprise-knowledge-base']]
def page(path):
    with urllib.request.urlopen(base+'/'+path,timeout=20) as r:
        data=r.read();h=hashlib.sha256(data).hexdigest()
        assert r.status==200 and h==before['hashes'][path],path
        return {'path':path,'status':r.status,'sha256':h,'unchanged':True,'title':re.search(r'<title>(.*?)</title>',data.decode(),re.S).group(1)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    red=list(pool.map(route,routes.items())); pages=list(pool.map(page,paths))
result={'checked_at':datetime.now(timezone.utc).isoformat(),'redirects':red,'unchanged_pages':pages,'page_count':len(pages),'all_passed':True,'traffic_classification':'OWN_QA_NOT_NATURAL_SEARCH'}
(D/'public-postflight.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'redirects':red,'unchanged_pages':len(pages),'all_passed':True},ensure_ascii=False,indent=2))
