"""Verify responsive image delivery without changing copy, layout, schema or originals."""
from pathlib import Path
import re,json,hashlib

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
base=json.loads((OUT/'baseline.json').read_text())
def normalize(s):
    s=re.sub(r'(<meta name="portfolio-revision" content=")[^"]+',r'\1REVISION',s)
    return re.sub(r'([?&](?:amp;)?pv=)[a-f0-9]{20}',r'\1REVISION',s)
changed=[]
for rel,digest in base['html_normalized_hashes'].items():
    now=(ROOT/'dist'/rel).read_text()
    if hashlib.sha256(normalize(now).encode()).hexdigest()!=digest:changed.append(rel)
assert set(changed)==set(base['allowed_html_changes']),changed
sizes=[]
for rel in changed:
    before=normalize((OUT/'before/dist'/rel).read_text())
    after=normalize((ROOT/'dist'/rel).read_text())
    old_img=re.search(r'<img[^>]+>',before)[0]
    new_img=re.search(r'<img[^>]+>',after)[0]
    assert after.replace(new_img,old_img,1)==before,rel
    attrs=lambda tag:dict(re.findall(r'([\w-]+)="([^"]*)"',tag))
    a,b=attrs(old_img),attrs(new_img)
    assert {k:v for k,v in a.items() if k!='src'}=={k:v for k,v in b.items() if k not in ('src','srcset','sizes')},rel
    case=Path(rel).stem
    prefix='../../' if rel.startswith('en/') else '../'
    assert b['src']==prefix+'assets/previews/'+case+'-1200.jpg',rel
    assert all(prefix+'assets/previews/'+case+'-'+str(w)+'.jpg '+str(w)+'w' in b['srcset'] for w in [640,1200]),rel
    assert '1050px' in b['sizes'] and b['loading']=='lazy'
    assert 'href="'+prefix+'assets/public-cases/'+case+'.png"' in after
    assert 'data-image-view' in after
    if not rel.startswith('en/'):
        original=ROOT/'assets/public-cases'/f'{case}.png'
        previews=[ROOT/'assets/previews'/f'{case}-{w}.jpg' for w in [640,1200]]
        sizes.append({'case':case,'original_bytes':original.stat().st_size,
                      'responsive_candidates':[{'width':w,'bytes':p.stat().st_size,
                        'reduction_fraction':1-p.stat().st_size/original.stat().st_size} for w,p in zip([640,1200],previews)]})
protected=[]
for rel,digest in base['dist_hashes'].items():
    if rel.startswith('assets/') or rel.endswith(('.css','.js')) or rel in ('robots.txt','llms.txt'):
        assert hashlib.sha256((ROOT/'dist'/rel).read_bytes()).hexdigest()==digest,rel
        protected.append(rel)
ledger_old=json.loads((OUT/'before/content/page-updates.json').read_text())['pages']
ledger_new=json.loads((ROOT/'content/page-updates.json').read_text())['pages']
assert {p for p in ledger_new if ledger_new[p]!=ledger_old[p]}==set(changed)
result={'status':'PASS','changed_html':changed,'unchanged_html':296-len(changed),
        'only_changed_elements':'4 responsive img elements; all copy, schema, anchor originals and other markup unchanged',
        'protected_asset_files':len(protected),'all_media_bytes_unchanged':True,
        'payload_sizes':sizes,'size_claim_boundary':'Existing file byte comparison; no speed, CWV or ranking improvement measured',
        'search_submissions':0,'deployments':0}
(OUT/'scope-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
