"""Check customer vocabulary against actual generated search attributes."""
from pathlib import Path
from html.parser import HTMLParser
from components import Renderer
from content import load_content
from localization import english_content
ROOT=Path(__file__).resolve().parent.parent
class Row(HTMLParser):
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'data-search' in attrs:self.search=attrs['data-search'].lower()
profile,projects,images=load_content(ROOT)
for lang in ['zh-CN','en']:
    p,items=(profile,projects) if lang=='zh-CN' else english_content(ROOT,profile,projects)
    renderer=Renderer(ROOT,p,items,images,lang=lang)
    searches={}
    for item in items:
        row=Row();row.feed(renderer.archive_row(item));searches[item['id']]=row.search
    website='网站' if lang=='zh-CN' else 'website'
    inventory='进销存' if lang=='zh-CN' else 'stock management'
    assert all(website not in searches[pid] for pid in ['P09','P10']), 'artifact category must not make inventory look like website work'
    assert all(website in searches[pid] for pid in ['P02','P03','P07','P11']), 'website work must remain findable'
    assert {pid for pid,text in searches.items() if inventory in text}=={'P09','P10'},'business vocabulary must find relevant inventory work'
print('PASS: bilingual business vocabulary, website relevance, inventory aliases')
