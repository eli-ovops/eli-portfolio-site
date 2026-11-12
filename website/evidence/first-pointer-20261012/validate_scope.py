"""Compare the final public build to the last accepted release, without extraction."""
from pathlib import Path
from html.parser import HTMLParser
import tarfile, json, hashlib, re, difflib
ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[1]
class Body(HTMLParser):
 def __init__(self):
  super().__init__(); self.inside=False; self.text=[]; self.images=[]
 def handle_starttag(self,tag,attrs):
  if tag=='body': self.inside=True
  if self.inside and tag=='img': self.images.append(dict(attrs))
 def handle_endtag(self,tag):
  if tag=='body': self.inside=False
 def handle_data(self,data):
  if self.inside: self.text.append(data)
 def content(self): return re.sub(r'\s+', ' ', ''.join(self.text)).strip()
archive=SITE/'evidence/deploy-20261012-194514-return-zoom/portfolio-20261012-194514-return-zoom.tar.gz'
checked=[]
with tarfile.open(archive) as bundle:
 for member in bundle.getmembers():
  if not member.name.endswith('.html'): continue
  relative=member.name.removeprefix('./')
  old=Body(); new=Body()
  old.feed(bundle.extractfile(member).read().decode())
  new.feed((SITE/'dist'/relative).read_text())
  assert old.content()==new.content(), relative+' body text changed'
  assert old.images==new.images, relative+' image attributes changed'
  checked.append(relative)
assert len(checked)==84
before=json.loads((ROOT/'before-hashes.json').read_text())
changes={p:hashlib.sha256((SITE/p).read_bytes()).hexdigest()!=digest for p,digest in before.items()}
assert {p for p,changed in changes.items() if changed}=={'motion.js','assets/editorial.js','assets/editorial.css'}
wrappers=sum(p.read_text().count('class="detail-image-visual"') for p in (SITE/'dist').rglob('*.html'))
assert wrappers==22
diff=''
for saved,current in [('before-motion.js','motion.js'),('before-editorial.js','assets/editorial.js'),('before-editorial.css','assets/editorial.css'),('before-pages.py','scripts/pages.py')]:
 diff+=''.join(difflib.unified_diff((ROOT/saved).read_text().splitlines(True),(SITE/current).read_text().splitlines(True),fromfile=saved,tofile=current))
(ROOT/'source.diff').write_text(diff)
result={'status':'PASS','html_body_text_unchanged':len(checked),'image_attributes_unchanged':len(checked),'bilingual_stable_image_hit_areas':wrappers,'protected_hash_changes':changes,'new_regression':'scripts/check_first_pointer.cjs','indexing':'DISABLED','publication':'NOT_PERFORMED'}
(ROOT/'scope-checks.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
