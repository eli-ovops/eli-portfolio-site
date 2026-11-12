RANGES={'PerplexityBot': ['[REDACTED_HOST]/32', '[REDACTED_HOST]/32', '[REDACTED_HOST]/32', '[REDACTED_HOST]/32', '[REDACTED_HOST]/32', '[REDACTED_HOST]/32', '[REDACTED_HOST]/30', '[REDACTED_HOST]/29'], 'Perplexity-User': ['[REDACTED_HOST]/32', '[REDACTED_HOST]/32', '[REDACTED_HOST]/30', '[REDACTED_HOST]/29']}
from pathlib import Path
import json,re,ipaddress,datetime,hashlib
from urllib.parse import urlsplit,parse_qs
nets={k:[ipaddress.ip_network(n) for n in v] for k,v in RANGES.items()}
result={k:{'verified_article_requests':0,'unverified_article_requests':0,'verified_all_paths':{},'last_events':[]} for k in nets}
rx=re.compile(r'^(\S+) \S+ \S+ \[([^\]]+)\] "([A-Z]+) ([^ ]+) [^" ]+" (\d+) \S+ "[^"]*" "([^"]*)"')
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
