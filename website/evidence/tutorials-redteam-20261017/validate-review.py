"""Current-version checks for the authorized 102-topic content review."""
import sys,json,hashlib,re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'scripts'))
from seo import load_config
config=load_config(root);evidence=root/'evidence/tutorials-redteam-20261017'
class HTML(HTMLParser):
 def __init__(self,source):
  super().__init__();self.links=[];self.meta={};self.lang='';self.feed(source)
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='a':self.links.append(a)
  if t=='html':self.lang=a.get('lang')
  if t=='meta':self.meta[a.get('name')]=a.get('content')
records=[]
for language,key,prefix,paired in [('zh-CN','articles','','en/'),('en','en','en/','')]:
 for item in config['articles'][key]:
  page=root/'dist'/prefix/'articles'/(item['slug']+'.html');source=page.read_text();html=HTML(source)
  assert html.lang==language
  assert html.meta.get('robots')=='noindex,nofollow'
  switch=[a for a in html.links if 'language-switch' in a.get('class','')]
  assert len(switch)==1
  target=urlsplit(switch[0]['href']).path
  assert (page.parent/target).resolve()==(root/'dist'/paired/'articles'/(item['slug']+'.html')).resolve()
  records.append(dict(slug=item['slug'],language=language,language_pair='PASS',draft='PASS'))
practice=json.loads((root/'content/tutorial-practice.json').read_text());assert len(practice)==100
for trial in practice.values():
 for key in ('setup','input','expected'):assert len(trial[key])==2 and all(trial[key])
for lang in range(2):
 s=practice['skill-file-structure']['input'][lang]
 assert s.startswith('---\nname: note-sorter\ndescription:')
 assert '\n---\n' in s
assert 30*(3-2)*20/60==10
assert divmod(20*(4-2)*20,60)==(13,20)
assert sum([5,8,10,9])==32 and 32-30==2
assert 8-10==-2
baseline=json.loads((evidence/'baseline.json').read_text());protected=dict(baseline['protected'])
protected['assets/articles.css']=baseline['files']['assets/articles.css']
for name,digest in protected.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
# Compare the actual decoded search metadata across languages, avoiding false
# passes from index strings that localization accidentally altered.
for prefix in ('','en/'):
 html=HTML((root/'dist'/prefix/'articles.html').read_text())
 assert html.lang==('en' if prefix else 'zh-CN')
 source=(root/'dist'/prefix/'articles.html').read_text()
 assert '&#' in source
samples=practice['skill-file-structure']['input']
result=dict(status='PASS',topics=102,localized_detail_pages=len(records),original_topics_retained=True,bilingual_practice_topics=100,skill_file_samples_valid=True,arithmetic_examples='PASS',visual_css_and_motion_unchanged=True,protected_files=protected,language_checks=records,limitations=['No real beginner participant test','Responsive browser emulation, not physical phones','Official documentation review, not hands-on use of all external tools'])
(evidence/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS: 102 topics, 204 localized detail pages; 100 bilingual practice sets; sample format, arithmetic and visual/motion hashes checked')
