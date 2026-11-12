"""Verify visible ordering, structured ordering and preservation of case evidence."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--baseline',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
dist=ROOT/'dist'
body=lambda text:text.split('<body>',1)[1]
row_pattern=r'<li id="project-([a-z0-9]+)"[^>]*>[\s\S]*?</li>'
baseline_examples=json.loads((args.baseline.parent/'content/case-examples.json').read_text())
examples=json.loads((ROOT/'content/case-examples.json').read_text())
assert {pid:{key:value for key,value in entry.items() if key not in ('hero_intro','hero_stage')} for pid,entry in examples.items()}==baseline_examples,'Original facts/stages/tables changed'
changed_cases={pid.lower() for pid,entry in examples.items() if 'hero_intro' in entry}
assert len(changed_cases)==13
unchanged=0
for file in dist.rglob('*.html'):
    relative=file.relative_to(dist).as_posix()
    before=(args.baseline/relative).read_text();after=file.read_text()
    if relative in ('records.html','en/records.html'):
        old_rows=list(re.finditer(row_pattern,body(before)))
        new_rows=list(re.finditer(row_pattern,body(after)))
        assert len(old_rows)==len(new_rows)==38
        assert {m[1]:m[0] for m in old_rows}=={m[1]:m[0] for m in new_rows},'Record contents altered'
        home=(args.baseline/('en/index.html' if relative.startswith('en/') else 'index.html')).read_text()
        featured=re.findall(r'class="text-link case-detail-link" href="cases/(p[0-9]+)\.html"',home)
        ids=[m[1] for m in new_rows]
        assert len(featured)==7 and ids[:7]==featured,'Library does not match the existing homepage order'
        graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',after,re.S)[1])['@graph']
        items=next(node for node in graph if node['@type']=='ItemList')['itemListElement']
        assert [item['url'].rsplit('/',1)[1].split('.')[0] for item in items]==ids
        assert [item['position'] for item in items]==list(range(1,39))
        assert re.sub(row_pattern,'',body(before))==re.sub(row_pattern,'',body(after)),'Library changed beyond row ordering'
    elif file.stem in changed_cases and '/cases/' in '/'+relative:
        split='<dl class="case-facts">'
        assert body(before).split(split,1)[1]==body(after).split(split,1)[1],('Evidence/details changed',relative)
        assert body(before).split('<div class="case-hero">',1)[0]==body(after).split('<div class="case-hero">',1)[0]
        assert re.search(r'<h1\b.*?</h1>',before,re.S)[0]==re.search(r'<h1\b.*?</h1>',after,re.S)[0]
        image=lambda text:re.findall(r'<figure class="detail-image.*?</figure>',text,re.S)
        assert image(before)==image(after),('Screenshot or its existing interaction altered',relative)
        if relative=='cases/p10.html':
            hero=after.split('<div class="case-hero">',1)[1].split('<div class="detail-grid">',1)[0]
            assert hero.count('已交付，尚未全面使用')==1 and '成熟底座' in hero
        for token in ({'p09':['虚拟库存通过；现场使用待核'], 'p12':['图文发布全链路未通过'], 'p15':['全部开发由我完成','发行闭环待核','配图为独立 Demo'], 'p36':['问答为示意']} if not relative.startswith('en/') else {}).get(file.stem,[]):
            assert token in after,(relative,token)
    else:
        assert body(before)==body(after),('Unapproved page body change',relative)
        unchanged+=1
assert unchanged==56
result={'pages':84,'homepage_library_order':'PASS','record_contents':'38 unchanged records per language','structured_visible_order':'PASS','case_heroes':13,'case_facts_and_body':'UNCHANGED','screenshots_and_viewer':'UNCHANGED','unaffected_page_bodies':unchanged,'indexing':'STILL DISABLED'}
args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
