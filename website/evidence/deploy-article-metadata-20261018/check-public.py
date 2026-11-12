from pathlib import Path
import sys,json,hashlib,urllib.request,concurrent.futures,datetime,collections
from xml.etree import ElementTree as ET
R=Path(__file__).resolve().parents[2]; E=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'scripts'))
from check_article_metadata import Head
P=json.loads((E/'plan.json').read_text()); base='https://www.eliai.cn/'
def check(n):
    with urllib.request.urlopen(base+n,timeout=25) as response:
        b=response.read(); headers=dict(response.headers);status=response.status
    assert status==200 and hashlib.sha256(b).hexdigest()==P['files'][n],n
    assert 'noindex' not in headers.get('X-Robots-Tag','').lower(),n
    return n,b,headers
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    all_results=list(pool.map(check,P['files']))
results={n:b for n,b,h in all_results}
descriptions=json.loads((R/'content/article-search-descriptions.json').read_text())
# The approved descriptions and head validation are also checked in the local regression.
assert len([n for n in results if n.startswith(('articles/','en/articles/')) and n.endswith('.html')])==204
pairs=[]
for n,b in results.items():
    if not n.startswith(('articles/','en/articles/')) or not n.endswith('.html'): continue
    h=Head(b.decode());desc=h.meta['description']
    assert h.meta['og:description']==h.meta['twitter:description']==desc
    article=[x for block in h.json_data for x in block.get('@graph',[]) if x.get('@type')=='Article'][0]
    assert article['description']==desc
    alternates={x['hreflang']:x['href'] for x in h.links if x.get('rel')=='alternate' and x.get('hreflang')}
    assert 'zh-CN' in alternates and 'en' in alternates
    for lang,url in alternates.items():
        assert url.startswith(base) and url[len(base):] in results,(n,lang,url)
    pairs.append({'path':n,'description':desc,'alternates':alternates})
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls=ET.fromstring(results['sitemap.xml']).findall('s:url',ns)
ledger=json.loads((R/'content/page-updates.json').read_text())['pages'];dates=[]
for u in urls:
    loc=u.find('s:loc',ns).text;date=u.find('s:lastmod',ns).text
    path=loc[len(base):] or 'index.html'
    if path=='en/':path='en/index.html'
    assert path in results and date==ledger[path]['lastmod'],(path,date)
    dates.append(date)
assert len(urls)==294 and collections.Counter(dates)=={'2026-10-17':180,'2026-10-18':114}
receipt=dict(status='PUBLIC_HTTP_PASS',checked_at=datetime.datetime.now().astimezone().isoformat(),revision=P['revision'],public_file_hashes_checked=len(results),article_metadata_checked=len(pairs),bilingual_alternate_links='PASS_ALL_204',sitemap_urls=294,lastmod_distribution=dict(collections.Counter(dates)),unexpected_noindex_headers=0,search_submissions=0,descriptions=pairs)
(E/'public-http-checks.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in receipt.items() if k!='descriptions'},indent=2))
