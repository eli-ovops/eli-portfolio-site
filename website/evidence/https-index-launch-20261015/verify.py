from pathlib import Path
import json,subprocess,ssl,urllib.request,urllib.error,hashlib,concurrent.futures
from ops import E,R,HEADER,run
M=json.loads((E/'manifest.json').read_text());B=json.loads((E/'bootstrap.json').read_text());L=json.loads((E/'launch.json').read_text())
script=HEADER+f'M={M!r}\nB={B!r}\nL={L!r}\n'+r'''
import urllib.error,xml.etree.ElementTree as ET
assert sha(conf.read_bytes())==L['config_sha'] and sha(erp.read_bytes())==B['erp_sha']
assert str((root/'domain-current').resolve())==M['target'] and str((root/'public').resolve())==B['public']
assert all(sha((Path(M['target'])/n).read_bytes())==h for n,h in M['file_hashes'].items())
checks=[];indexed=0;notfound=0
for n,h in M['file_hashes'].items():
 if n.endswith('.html') or n in ['robots.txt','sitemap.xml','llms.txt','assets/social-footer.css','app.js','assets/editorial.js']:
  with urllib.request.urlopen('https://www.eliai.cn/'+n,timeout=10) as v:
   data=v.read();assert sha(data)==h,n;assert 'noindex' not in (v.headers.get('X-Robots-Tag') or '').lower(),n
   if n.endswith('.html'):
    assert (b'noindex,nofollow' if n.endswith('404.html') else b'index,follow') in data
    if n.endswith('404.html'):notfound+=1
    else:indexed+=1
   checks.append({'path':n,'status':v.status,'sha256':h})
robots=(Path(M['target'])/'robots.txt').read_text();assert robots=='User-agent: *\nAllow: /\nSitemap: https://www.eliai.cn/sitemap.xml\n'
urls=[x.text for x in ET.parse(Path(M['target'])/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')];assert len(urls)==82 and len(set(urls))==82 and all(x.startswith('https://www.eliai.cn/') for x in urls)
for n in ['not-a-page','content/profile.json','scripts/build.py','.git/config','assets/img17.jpg']:
 try:urllib.request.urlopen('https://www.eliai.cn/'+n,timeout=10);raise AssertionError(n+' exposed')
 except urllib.error.HTTPError as ex:assert ex.code in (403,404),(n,ex.code)
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
redirects=[];opener=urllib.request.build_opener(NoRedirect)
for u in ['http://eliai.cn/','http://www.eliai.cn/','https://eliai.cn/']:
 try:opener.open(u,timeout=10);raise AssertionError('No redirect '+u)
 except urllib.error.HTTPError as ex:
  assert ex.code==301 and ex.headers['Location']=='https://www.eliai.cn/',(u,ex.code,dict(ex.headers));redirects.append({'url':u,'status':ex.code,'location':ex.headers['Location']})
with urllib.request.urlopen('http://[REDACTED_HOST]/sites/portfolio/',timeout=10) as v:assert b'noindex,nofollow' in v.read()
with urllib.request.urlopen('http://[REDACTED_HOST]/sites/portfolio/robots.txt',timeout=10) as v:assert v.read()==b'User-agent: *\nDisallow: /\n'
hook=Path('/etc/letsencrypt/renewal-hooks/deploy/eli-portfolio-reload');env=dict(os.environ,RENEWED_LINEAGE='/etc/letsencrypt/live/www.eliai.cn');p=subprocess.run([str(hook)],env=env,capture_output=True,text=True);assert p.returncode==0,p.stderr
states={s:cmd(['systemctl','is-active',s]) for s in ['nginx','erp-trial','mysql','redis-server','certbot.timer']};assert all(v=='active' for v in states.values())
old=json.loads((root/'backups/https-index-20261015/before.json').read_text());assert old['erp_sha']==sha(erp.read_bytes())
print(json.dumps({'status':'PASS','remote_files':len(M['file_hashes']),'https_http_checks':checks,'indexable_pages':indexed,'noindex_404':notfound,'redirects':redirects,'sitemap_urls':len(urls),'IP_noindex':True,'private_paths':'403/404','ERP_config_unchanged':True,'renew_hook':'PASS','timer_enabled':cmd(['systemctl','is-enabled','certbot.timer']),'timer_next':cmd(['systemctl','show','certbot.timer','-p','NextElapseUSecRealtime','--value']),'services':states}))
'''
x=run('verify-remote',script,180);print(json.dumps({k:v for k,v in x.items() if k!='https_http_checks'}))
# Independent HTTPS requests from the operator's machine, normal DNS/TLS verification.
urls=['https://www.eliai.cn/','https://www.eliai.cn/robots.txt','https://www.eliai.cn/sitemap.xml','https://www.eliai.cn/en/index.html','https://eliai.cn/']
def get(u):
 try:
  with urllib.request.urlopen(u,timeout=15) as v:
   b=v.read();return {'url':u,'status':v.status,'final_url':v.url,'sha256':hashlib.sha256(b).hexdigest(),'noindex_header':v.headers.get('X-Robots-Tag'),'meta_index':b'name="robots" content="index,follow"' in b}
 except Exception as ex:return {'url':u,'error':str(ex)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:checks=list(pool.map(get,urls))
(E/'verify-external.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print(json.dumps(checks,ensure_ascii=False))
