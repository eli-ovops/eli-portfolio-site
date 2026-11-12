from pathlib import Path
import urllib.request,json,re,hashlib,subprocess,datetime,concurrent.futures
from urllib.robotparser import RobotFileParser
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent.parent
HOST='https://www.eliai.cn'
paths=['/articles/inventory-reconciliation.html','/articles/enterprise-knowledge-base.html','/articles/what-is-agent.html','/robots.txt','/llms.txt']
def fetch(path):
    start=datetime.datetime.now().astimezone().isoformat()
    with urllib.request.urlopen(HOST+path,timeout=30) as r:
        b=r.read();s=b.decode('utf-8-sig');h=dict(r.headers)
        return {'path':path,'at':start,'status':r.status,'final_url':r.url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'content_type':r.headers.get('Content-Type'),'x_robots_tag':r.headers.get('X-Robots-Tag'),'title':re.findall(r'<title>(.*?)</title>',s,re.S),'canonical':re.findall(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"',s),'robots':re.findall(r'<meta[^>]*name="robots"[^>]*content="([^"]+)"',s),'body_text_chars':len(re.sub('<[^>]+>','',s)),'text':s if path in ['/robots.txt','/llms.txt'] else None}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as e:
    checks=list(e.map(fetch,paths))
(BASE/'public-pages.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
robot=RobotFileParser();robot.parse(next(x['text'] for x in checks if x['path']=='/robots.txt').splitlines())
print(json.dumps({'http':[{k:v for k,v in x.items() if k!='text'} for x in checks],'allowed':{bot:{p:robot.can_fetch(bot,HOST+p) for p in paths[:3]} for bot in ['PerplexityBot','Perplexity-User']}},ensure_ascii=False))
ranges={}
for bot,name in [('PerplexityBot','perplexitybot'),('Perplexity-User','perplexity-user')]:
    with urllib.request.urlopen('https://www.perplexity.com/'+name+'.json',timeout=30) as r:d=json.load(r)
    (BASE/(name+'.json')).write_text(json.dumps(d,indent=2))
    ranges[bot]=[v for p in d['prefixes'] for k,v in p.items() if k in ('ipv4Prefix','ipv6Prefix')]
remote='RANGES='+repr(ranges)+'''\nfrom pathlib import Path
import json,re,ipaddress,datetime,hashlib
from urllib.parse import urlsplit,parse_qs
nets={k:[ipaddress.ip_network(n) for n in v] for k,v in RANGES.items()}
result={k:{'verified_article_requests':0,'unverified_article_requests':0,'verified_all_paths':{},'last_events':[]} for k in nets}
rx=re.compile(r'^(\\S+) \\S+ \\S+ \\[([^\\]]+)\\] "([A-Z]+) ([^ ]+) [^" ]+" (\\d+) \\S+ "[^"]*" "([^"]*)"')
marker_hits=[]
for line in Path('/var/log/nginx/access.log').open(errors='replace'):
 m=rx.match(line)
 if not m:continue
 ip,when,method,url,status,ua=m.groups();u=urlsplit(url);path=u.path
 if not when.startswith('17/Oct/2026:'):continue
 if parse_qs(u.query).get('diag')==['perplexity-article-20261017-1820']:
  marker_hits.append({'time':when,'path':path,'status':status,'ua_claim':'Perplexity-User' if 'Perplexity-User' in ua else 'PerplexityBot' if 'PerplexityBot' in ua else 'other','official_ip':any(ipaddress.ip_address(ip) in n for ns in nets.values() for n in ns)})
 for bot in nets:
  if bot not in ua:continue
  b=result[bot];verified=any(ipaddress.ip_address(ip) in n for n in nets[bot]);article=path.startswith(('/articles/','/en/articles/'))
  if article:b['verified_article_requests' if verified else 'unverified_article_requests']+=1
  if verified:
   b['verified_all_paths'][path]=b['verified_all_paths'].get(path,0)+1
   b['last_events'].append({'time':when,'path':path,'status':status})
for b in result.values():b['last_events']=b['last_events'][-20:]
config=Path('/etc/nginx/sites-available/portfolio-domain-pending').read_bytes()
print(json.dumps({'timestamp':datetime.datetime.now().astimezone().isoformat(),'scope':'current access.log; 2026-10-17; official IP plus UA; no raw visitor IPs stored; global log lacks hostname','bots':result,'marker_hits':marker_hits,'config_sha256':hashlib.sha256(config).hexdigest(),'current_release':str(Path('/srv/eli-sites/portfolio/domain-current').resolve())}))
'''
(BASE/'origin-check.remote.py').write_text(remote)
ssh=json.loads((ROOT/'evidence/deploy-20261015-200719-center-about/ssh-options.json').read_text())
p=subprocess.run(ssh+['python3 -'],input=remote,text=True,capture_output=True,timeout=45,check=True)
snapshot=json.loads(p.stdout)
(BASE/'origin-before.json').write_text(json.dumps(snapshot,indent=2))
print(json.dumps(snapshot))
