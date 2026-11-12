# -*- coding: utf-8 -*-
from pathlib import Path
import json
root=Path(__file__).resolve().parent.parent
p=root/'content/profile.json'
d=json.loads(p.read_text())
d.update({'headline':'理解问题。\n推进实践。','intro':'我关注真实业务中的问题，借助 AI 协作推进网站、业务工具与工作流程。这里介绍我的参与经历、做事方式和可核对的实践。','about':'2026 年 5 月至 8 月，我在原点向量参与技术支持相关工作，涉及网站前后端、运营维护和测试。此后持续探索 AI 协作、企业业务工具与交付方法。'})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
p=root/'scripts/build.py';s=p.read_text()
s=s.replace('网站、业务工具与 App 的参与经历和实践记录。内部预览版。','个人介绍、网站、业务工具与 AI 协作的参与经历和实践记录。内部预览版。')
s=s.replace('<nav aria-label="主导航"><a href="{base}index.html#work">作品</a><a href="{base}index.html#about">关于</a><a href="{base}index.html#archive">全部记录 <span aria-hidden="true">↗</span></a></nav>','<nav aria-label="主导航"><a href="{base}index.html#work">作品</a><a href="{base}index.html#about">关于</a><a href="{base}experiments.html">实验</a><a href="{base}index.html#archive">记录</a></nav>')
start=s.index("hero=f'''");end=s.index("\nclients=",start)
s=s[:start]+'''hero=f\'''<section class="hero editorial-hero"><p class="hero-kicker">技术支持 / AI 协作</p><h1>{e(profile['headline']).replace(chr(10),'<br>')}</h1><div class="hero-bottom"><div class="hero-statement"><p class="hero-intro">{e(profile['intro'])}</p><a class="primary" href="#work">浏览作品 <span aria-hidden="true">↗</span></a></div><div class="hero-focus"><p>从业务需求出发，<br>把想法拆成可以验证的步骤。</p><span>网站与界面 · 业务工具 · 交付实践</span></div></div></section>\'''\n''' +s[end:]
s=s.replace('网站 / 业务工具 / iOS / AI 工作流','业务理解 / 网站与工具 / AI 协作')
s=s.replace('<div class="app-projects">{project_card(\'P13\')}{project_card(\'P14\')}{project_card(\'P15\')}</div>','')
s=s.replace('<h2>选一些做过的事，<br><span>认真说清楚。</span></h2>','<h2>先理解业务，<br><span>再推进实现。</span></h2>')
s=s.replace('</article></div></section><section class="clients','</article></div><div class="experiment-entry"><div><h3>探索，另留一个空间。</h3><p>产品原型、App 实践与研究，收在实验栏目。</p></div><a class="text-link" href="experiments.html">查看产品实验 <span aria-hidden="true">↗</span></a></div></section><section class="clients')
s=s.replace("(out/'index.html').write_text(shell('网站与产品实践',body))","(out/'index.html').write_text(shell('个人介绍与业务实践',body))")
point=s.index('\nfor p in projects:\n image=')
extra='''\nexperiment_items=[p for p in projects if p['category'] in ['App 实践','内容与研究']]\nexperiment_list=''.join(f'<li><a href="cases/{p["id"].lower()}.html"><span class="archive-name">{e(p["name"])}</span><span class="archive-category">{e(p["category"])}</span><span class="archive-status">{e(p["label"])}</span><span aria-hidden="true">↗</span></a></li>' for p in experiment_items)\nexperiment_body=f\'''<main id="main" class="experiments-main"><section class="experiments-heading"><a class="back" href="index.html#work">← 返回业务实践</a><h1>保留好奇，<br>继续探索。</h1><p>这里收集产品原型、App 实践与研究。<br>阶段各不相同，已有验证与待完成部分分开说明。</p></section><div class="app-projects">{project_card('P13')}{project_card('P14')}{project_card('P15')}</div><section class="experiment-archive"><h2>实验与研究记录</h2><ul class="archive-list">{experiment_list}</ul></section></main>\'''\n(out/'experiments.html').write_text(shell('产品实验与研究',experiment_body))\n'''
s=s[:point]+extra+s[point:]
s=s.replace('网站首版 v0.1','本地预览 v0.2').replace("'version':'0.1.0'","'version':'0.2.0'")
p.write_text(s)
p=root/'package.json';d=json.loads(p.read_text());d['version']='0.2.0';p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
print('Direction revised: four business cases on homepage; apps on experiments page.')
