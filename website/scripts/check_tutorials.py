"""Check bilingual completeness, draft boundaries and preserved site assets."""
import hashlib
import json
import re
import argparse
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
from collections import Counter
from tutorials import load_tutorials

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path)
args = parser.parse_args()
evidence = root/'evidence/beginner-library-local-20261017'
publication = json.loads((root/'content/articles.json').read_text())['publication_status']
published = publication == 'published'
expected_robots = 'index,follow' if published else 'noindex,nofollow'
zh,en = load_tutorials(root)
class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(); self.links=[]; self.meta={}; self.text=[]; self.h1=0
        self.template_depth=0; self.pool_depth=None; self.pool_templates=0
        self.article_rows=0; self.pool_rows=0; self.pool_links=[]
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='a': self.links.append(a)
        if tag=='meta': self.meta[a.get('name','')]=a.get('content','')
        if tag=='h1': self.h1+=1
        if tag=='template':
            self.template_depth+=1
            if 'data-article-pool' in a:
                self.pool_depth=self.template_depth; self.pool_templates+=1
        if tag=='article' and 'article-row' in a.get('class','').split():
            if self.pool_depth is not None: self.pool_rows+=1
            elif not self.template_depth: self.article_rows+=1
        if tag=='a' and self.pool_depth is not None: self.pool_links.append(a.get('href',''))
    def handle_endtag(self, tag):
        if tag=='template':
            if self.template_depth==self.pool_depth: self.pool_depth=None
            self.template_depth-=1
    def handle_data(self, data):self.text.append(data)
counts=Counter(a['category_id'] for a in zh)
assert len(zh)==len(en)==100 and set(counts.values())=={10}
assert len({a['title'] for a in zh})==100
assert len({a['title'] for a in en})==100
assert len({a['sections'][2]['prompt'] for a in zh})==100
assert len({a['sections'][3]['paragraphs'][0] for a in zh})==100
content_counts=[]
for i,(a,b) in enumerate(zip(zh,en)):
    assert a['slug']==b['slug']
    assert len(a['sections'])==len(b['sections'])==5
    assert len(a['sections'][1]['bullets'])==len(b['sections'][1]['bullets'])==3
    for lang,item in [('zh-CN',a),('en',b)]:
        prefix='en/' if lang=='en' else ''
        other='' if lang=='en' else 'en/'
        path=root/'dist'/prefix/'articles'/(item['slug']+'.html')
        source=path.read_text();page=Page(source)
        assert page.h1==1 and page.meta['robots']==expected_robots,path
        switch=[x for x in page.links if 'language-switch' in x.get('class','')]
        assert len(switch)==1
        target=urlsplit(switch[0]['href']).path
        assert (path.parent/target).resolve()==(root/'dist'/other/'articles'/(item['slug']+'.html')).resolve()
        assert source.count('class="article-prompt"')==2
        assert source.count('data-practice-input')==1
        assert source.count('data-practice-expected')==1
        main=source.split('<main',1)[1].split('</main>',1)[0]
        # Foreign-language examples are intentional inside the labelled practice input.
        ui_main = re.sub(r'<pre[^>]*data-practice-input[^>]*>.*?</pre>', '', main, flags=re.S)
        visible=' '.join(Page(ui_main).text)
        if lang=='en': assert not re.search('[\u4e00-\u9fff]',visible),(item['slug'],'English text contains untranslated Chinese')
        assert len(item['sources'])>=1
        content_counts.append(dict(slug=item['slug'],lang=lang,visible_characters=len(visible)))
for prefix in ['','en/']:
    listing=(root/'dist'/prefix/'articles.html').read_text()
    assert Page(listing).article_rows==102
    assert Page(listing).meta['robots']==expected_robots
    home=(root/'dist'/prefix/'index.html').read_text()
    home_page=Page(home)
    # The live window has two rows; the inert template supplies eight articles.
    assert home_page.article_rows==2 and home_page.pool_rows==8 and home_page.pool_templates==1
    pool_targets={urlsplit(href).path for href in home_page.pool_links}
    assert len(pool_targets)==8
    assert all(path.startswith('articles/') and path.endswith('.html') and
               (root/'dist'/prefix/path).is_file() for path in pool_targets)
    assert 'data-article-pause' in home and 'data-article-next' in home
sitemap=(root/'dist/sitemap.xml').read_text()
expected_urls = 294 if published else 88
assert '<loc>' in sitemap and sitemap.count('<loc>')==expected_urls
if published:
    assert sitemap.count('/articles/')==204
    assert sitemap.count('articles.html')==2
else:
    assert 'articles.html' not in sitemap and '/articles/' not in sitemap
baseline=json.loads((evidence/'baseline.json').read_text())
protected=['styles.css','motion.css','app.js','motion.js','assets/page-version.js','assets/stacked-gallery.css','assets/stacked-gallery.js']
checked={}
for name in protected:
    if name in baseline:
        now=hashlib.sha256((root/name).read_bytes()).hexdigest()
        assert now==baseline[name],name+' changed unexpectedly'
        checked[name]=now
legacy_protected=json.loads((root/'evidence/articles-local-20261017/baseline.json').read_text())['protected']
for name,digest in legacy_protected.items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name+' visual/motion baseline changed'
    checked[name]=digest
result=dict(status='PASS',publication_status=publication,tutorial_topics=100,tutorial_pages=200,retained_case_topics=2,total_articles_per_language=102,categories=dict(counts),static_article_links_per_language=102,homepage_article_previews=2,homepage_rotator_pool=8,sitemap_urls=expected_urls,articles_indexable=published,complete_english_text=True,paired_language_switches=200,unique_practice_prompts=100,protected_hashes=checked,content_lengths=content_counts)
output = args.output or evidence/'content-and-boundary-checks.json'
output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS: 100 topics / 200 translated tutorial pages; 10 categories; 102 articles/language; '+publication+' boundaries and protected hashes intact')
