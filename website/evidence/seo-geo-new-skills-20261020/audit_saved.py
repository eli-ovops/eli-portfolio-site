"""Read-only analysis of the exact published static artifacts; no fetch or edits."""
from pathlib import Path
from collections import Counter, defaultdict, deque
from urllib.parse import urlsplit, urljoin, unquote
import json, hashlib, sys, re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
UPSTREAM = Path('/Users/USER/.codex/skills/seo-toolkit/reference/upstream/scripts')
sys.path.insert(0, str(UPSTREAM))
from parse_html import parse_html

plan = json.loads((ROOT / 'evidence/deploy-home-industries-20261020/plan.json').read_text())
base = 'https://www.eliai.cn/'
snapshots = OUT / 'snapshots'
snapshots.mkdir(exist_ok=True)
core = ['index.html', 'about.html', 'services/ai-agent.html',
        'services/workflow-automation.html', 'services/fde-consulting.html',
        'articles/enterprise-knowledge-base.html', 'articles/inventory-reconciliation.html',
        'cases/p09.html', 'cases/p10.html', 'cases/p36.html']
core += ['en/' + p for p in core[:7]]
parsed, main_data, graph = {}, {}, {}
errors, image_flags, text_blocks = [], [], defaultdict(list)
inbound = defaultdict(set)

def local_path(url):
    u = urlsplit(url)
    if u.netloc and u.netloc != 'www.eliai.cn':
        return None
    path = unquote(u.path).lstrip('/')
    if not path or path.endswith('/'):
        path += 'index.html'
    return path

def canonical_url(path):
    return base + ({'index.html':'', 'en/index.html':'en/'}.get(path, path))

for file in sorted((ROOT / 'dist').rglob('*.html')):
    rel = file.relative_to(ROOT / 'dist').as_posix()
    if rel.endswith('404.html'):
        continue
    raw = file.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == plan['files'][rel], rel
    source = raw.decode('utf-8')
    data = parse_html(source, base + rel)
    soup = BeautifulSoup(source, 'lxml')
    main = soup.find('main') or soup.body
    if len(data['h1']) != 1:
        errors.append([rel, 'H1 count', len(data['h1'])])
    expected = canonical_url(rel)
    if data['canonical'] != expected:
        errors.append([rel, 'canonical', data['canonical'], expected])
    if 'noindex' in (data['meta_robots'] or '').lower():
        errors.append([rel, 'noindex'])
    alternate = {x['lang']:x['href'] for x in data['hreflang']}
    pair = rel[3:] if rel.startswith('en/') else 'en/' + rel
    lang = 'en' if rel.startswith('en/') else 'zh-CN'
    pair_lang = 'zh-CN' if lang == 'en' else 'en'
    expected_pair = canonical_url(pair)
    if alternate.get(pair_lang) != expected_pair:
        errors.append([rel, 'paired hreflang', alternate])
    if alternate.get(lang) != expected:
        errors.append([rel, 'self hreflang', alternate])
    links = []
    for a in main.find_all('a', href=True):
        href = urljoin(base + rel, a['href'])
        dest = local_path(href)
        if dest and dest.endswith('.html'):
            links.append({'path':dest,'text':a.get_text(' ',strip=True),'raw_href':a['href']})
            inbound[dest].add(rel)
    graph[rel] = sorted({dest for a in soup.find_all('a',href=True)
                         for dest in [local_path(urljoin(base + rel,a['href']))]
                         if dest and dest.endswith('.html')})
    for p in main.find_all('p'):
        text = re.sub(r'\s+',' ',p.get_text(' ',strip=True))
        if len(text) >= 55:
            text_blocks[text].append(rel)
    for image in data['images']:
        path = local_path(image['src'])
        asset = ROOT / 'dist' / (path or '')
        size = asset.stat().st_size if asset.is_file() else None
        if size and (size > 200_000 or not image['width'] or not image['height']):
            image_flags.append({'page':rel,**image,'bytes':size})
    parsed[rel] = data
    main_data[rel] = {'title':data['title'],'main_chars':len(main.get_text(' ',strip=True)),
                     'headings':[h.get_text(' ',strip=True) for h in main.find_all(['h1','h2','h3'])],
                     'main_links':links,'paragraphs':[p.get_text(' ',strip=True) for p in main.find_all('p')]}
    if rel in core:
        (snapshots / rel.replace('/','__')).write_bytes(raw)

depth = {'index.html':0}
todo = deque(['index.html'])
while todo:
    src = todo.popleft()
    for dest in graph.get(src,[]):
        if dest in graph and dest not in depth:
            depth[dest] = depth[src] + 1
            todo.append(dest)
service_paths = ['services/ai-agent.html','services/workflow-automation.html','services/fde-consulting.html']
services = {}
for prefix in ['', 'en/']:
    for slug in service_paths:
        path = prefix + slug
        sources = sorted(inbound[path])
        services[path] = {'click_depth_from_zh_home':depth.get(path),
                          'main_content_inbound_pages':len(sources),
                          'article_inbound_pages':[p for p in sources if '/articles/' in '/'+p],
                          'sources':sources}
repeats = [{'text':text,'pages':sorted(set(pages)),'count':len(set(pages))}
           for text,pages in text_blocks.items() if len(set(pages)) >= 4]
repeats.sort(key=lambda x:x['count'],reverse=True)
summary = {'published_revision':plan['revision'],'read_only':True,'parsed_indexable_html':len(parsed),
           'core_snapshots':len(core),'errors':errors,
           'unique_titles':len(set(x['title'] for x in parsed.values())),
           'unique_descriptions':len(set(x['meta_description'] for x in parsed.values())),
           'unreachable_in_crawl_graph':[p for p in graph if p not in depth],
           'max_crawl_graph_depth':max(depth.values()),'services':services,
           'article_details':sum('/articles/' in '/'+p for p in parsed),
           'image_flag_count':len(image_flags),'shared_paragraph_groups':len(repeats),
           'word_count_warning':'Upstream English/regex count is not a Chinese depth threshold or ranking score',
           'crawler_warning':'No network helper called, no bot spoofing, actual platform access/citations not established by robots or HTML.'}
for name,value in [('summary.json',summary),('core-parsed.json',{p:parsed[p] for p in core}),
                   ('core-reading.json',{p:main_data[p] for p in core}),
                   ('all-main-links.json',{p:x['main_links'] for p,x in main_data.items()}),
                   ('image-flags.json',image_flags),('repeated-paragraphs.json',repeats)]:
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pages':len(parsed),'snapshots':len(core),'errors':errors,'max_main_depth':max(depth.values()),
                  'service_main_inbound':{p:v['main_content_inbound_pages'] for p,v in services.items()},
                  'service_article_inbound':{p:len(v['article_inbound_pages']) for p,v in services.items()},
                  'image_flags':len(image_flags),'shared_paragraph_groups':len(repeats)},ensure_ascii=False))
