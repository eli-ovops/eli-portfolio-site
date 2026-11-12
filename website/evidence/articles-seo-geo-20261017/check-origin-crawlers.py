from pathlib import Path
import json,subprocess,datetime
R=Path(__file__).resolve().parents[2];E=Path(__file__).resolve().parent
ssh=json.loads((R/'evidence/deploy-20261015-200719-center-about/ssh-options.json').read_text())
assert Path('/Volumes/EXTERNAL/ERP试跑-20261005/known_hosts').is_file()
# Read only the configured current log. Emit aggregate path/status/time by claimed crawler,
# never raw lines, visitor IPs, referrers, query strings or contact data.
code=r'''from pathlib import Path
import re,json,collections,datetime
from urllib.parse import urlsplit
p=Path('/var/log/nginx/access.log'); pattern=re.compile(r'^(\S+) \S+ \S+ \[([^\]]+)\] "([A-Z]+) ([^ ]+) [^" ]+" (\d+) \S+ "[^"]*" "([^"]*)"')
tokens=['Googlebot','bingbot','Baiduspider','OAI-SearchBot','ChatGPT-User','PerplexityBot','Perplexity-User','Bytespider','YisouSpider','Sogou']
bots={t:dict(total=0,articles=0,sitemap=0,article_paths={},article_statuses={},first_article=None,last_article=None) for t in tokens};read=0;parsed=0
for line in p.open(errors='replace'):
 read+=1;m=pattern.match(line)
 if not m:continue
 ip,when,method,url,status,ua=m.groups()
 if not when.startswith('17/Oct/2026:'):continue
 parsed+=1;path=urlsplit(url).path
 for t,b in bots.items():
  if t.lower() not in ua.lower():continue
  b['total']+=1
  if path=='/sitemap.xml':b['sitemap']+=1
  if path.startswith(('/articles/','/en/articles/')) or path in ['/articles.html','/en/articles.html']:
   b['articles']+=1;b['article_paths'][path]=b['article_paths'].get(path,0)+1;b['article_statuses'][status]=b['article_statuses'].get(status,0)+1;b['first_article']=b['first_article'] or when;b['last_article']=when
print(json.dumps({'scope':'Current access.log only;2026-10-17;shared log host attribution unknown;UA claims only, not verified bot identity','lines_scanned':read,'today_parsed':parsed,'generated_at':datetime.datetime.now().astimezone().isoformat(),'bots':bots}))
'''
(E/'origin-crawler-aggregation.remote.py').write_text(code)
x=subprocess.run(ssh+['python3 -'],input=code,text=True,capture_output=True,timeout=25);assert x.returncode==0,x.stderr
result=json.loads(x.stdout);(E/'origin-crawler-observations.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
