"""Rendered names agree with controls; client work remains a cross-type facet."""
from pathlib import Path
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parent.parent
class Catalog(HTMLParser):
    def __init__(self):
        super().__init__();self.rows=[];self.buttons={};self.button=None;self.meta=0;self.label=False;self.row=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='li' and 'data-category' in a:
            self.row=dict(a,label='');self.rows.append(self.row)
        if tag=='button' and 'data-filter' in a:
            self.button=a['data-filter'];self.buttons[self.button]=''
        if tag=='span':
            if 'archive-meta' in a.get('class','').split():self.meta=1
            elif self.meta:self.meta+=1;self.label=True
    def handle_endtag(self,tag):
        if tag=='button':self.button=None
        if tag=='li':self.row=None
        if tag=='span' and self.meta:self.meta-=1;self.label=False
    def handle_data(self,data):
        if self.button is not None:self.buttons[self.button]+=data
        if self.label and self.row is not None:self.row['label']+=data

for prefix,expected,client,website in [
    ('',{'客户参与':'客户项目','网站与工具':'网站与工具','App 实践':'移动应用','内容与研究':'内容与研究','方法与支持':'方法与工具'},'客户参与','网站与工具'),
    ('en/',{'Client work':'Client work','Websites & tools':'Websites & tools','Mobile apps':'Mobile apps','Content & research':'Content & research','Methods & tools':'Methods & tools'},'Client work','Websites & tools')]:
    page=Catalog();page.feed((ROOT/'dist'/prefix/'records.html').read_text())
    assert len(page.rows)==38 and len({r['id'] for r in page.rows})==38
    for row in page.rows:
        key=row['data-category']
        assert page.buttons[key]==row['label']==expected[key],(prefix,key,row['label'],page.buttons[key])
    clients={r['id'] for r in page.rows if r['data-category']==client or r['data-client']=='true'}
    websites={r['id'] for r in page.rows if r['data-category']==website}
    assert len(clients)==9 and len(websites)==8
    assert clients & websites=={'project-p07','project-p08','project-p09','project-p10'}
print('PASS: bilingual visible labels; original filter keys; 38 unique rows; 9 clients with 4 cross-type matches')
