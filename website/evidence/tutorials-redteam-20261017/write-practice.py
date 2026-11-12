"""Task-owned authoring helper; bilingual practice data, not model-generated results."""
import json,sys,pathlib
p=pathlib.Path('content/tutorial-practice.json')
items=json.loads(p.read_text()) if p.exists() else {}
for line in sys.stdin.read().strip().splitlines():
 cells=line.strip().split('|')
 if len(cells)!=4:raise ValueError(line[:80])
 slug,*fields=cells
 pairs=[x.split('~') for x in fields]
 assert all(len(x)==2 for x in pairs),slug
 items[slug]=dict(zip(['setup','input','expected'],pairs))
p.write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n')
