"""Bilingual, hand-authored beginner lessons. No runtime content generation."""
import json
import re
import math
from pathlib import Path

CATEGORIES = [
 ('basics','AI 入门','AI basics'),('models','大模型原理','How models work'),
 ('prompting','提问方法','Better prompts'),('agents','Agent 入门','Agent basics'),
 ('skills','Skills 与 MCP','Skills and MCP'),('harness','Harness 与 AI 编程','Harnesses and AI coding'),
 ('github','GitHub 入门','GitHub basics'),('workbuddy','WorkBuddy 办公','WorkBuddy at work'),
 ('office','办公实操','Office tasks'),('business','老板用 AI','AI for business owners')]

def load_tutorials(root):
    source = json.loads((root/'content/tutorials/sources.json').read_text())
    practice = json.loads((root/'content/tutorial-practice.json').read_text())
    result = [[],[]]
    for category,zh_name,en_name in CATEGORIES:
        rows = json.loads((root/('content/tutorials/'+category+'.json')).read_text())
        if len(rows)!=10: raise ValueError(category+': expected 10 complete lessons')
        for i,row in enumerate(rows):
            required=('slug','title','answer','steps','exercise','problem','check','source')
            if any(k not in row for k in required): raise ValueError('Incomplete lesson')
            if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',row['slug']): raise ValueError('Invalid lesson slug')
            if len(row['steps'])!=3: raise ValueError('Three specific steps required')
            for lang in range(2):
                trial = practice[row['slug']]
                if any(len(trial[k]) != 2 or not all(trial[k]) for k in ('setup','input','expected')):
                    raise ValueError('Complete bilingual practice required: ' + row['slug'])
                values = [row[k][lang] for k in ('title','answer','exercise','problem','check')]
                if any(not isinstance(v,str) or not v.strip() for v in values): raise ValueError('Missing translation')
                def section(sid,title,paragraphs,**extra): return dict(id=sid,title=title,paragraphs=paragraphs,**extra)
                labels = (['先弄明白','分三步试一试','可以这样问','遇到问题怎么办','怎么判断学会了'],
                          ['The short answer','Try it in three steps','A practice prompt','If it goes wrong','Check your result'])[lang]
                steps=[p[lang] for p in row['steps']]
                separator = '。' if lang == 0 else '. '
                parts = row['answer'][lang].split(separator, 1)
                intro = parts[0] + ('。' if lang == 0 else '.')
                remainder = parts[1] if len(parts) > 1 else row['answer'][lang]
                sections=[section('understand',labels[0],[remainder]),
                          section('try',labels[1],[],bullets=steps),
                          section('example',labels[2],[],prompt=row['exercise'][lang],
                                  practice={k:trial[k][lang] for k in ('setup','input','expected')}),
                          section('troubleshoot',labels[3],[row['problem'][lang]]),
                          section('check',labels[4],[row['check'][lang]])]
                body_text = ' '.join([row[k][lang] for k in ('answer','exercise','problem','check')]
                                     + steps + [trial[k][lang] for k in ('setup','input','expected')])
                units = len(re.findall(r'[\u4e00-\u9fff]',body_text)) if lang == 0 else len(re.findall(r"\b[\w'-]+\b",body_text))
                minutes = max(1, math.ceil(units / (300 if lang == 0 else 180)))
                result[lang].append(dict(slug=row['slug'],title=row['title'][lang],category=(zh_name,en_name)[lang],category_id=category,
                    lesson=i+1,summary=(row['summary'][lang] if row.get('summary') else row['answer'][lang].split('。' if lang==0 else '. ')[0]+('。' if lang==0 else '.')),
                    date='2026-10-17',reading=(f'约 {minutes} 分钟阅读', f'{minutes} min read')[lang],intro=intro,
                    takeaway='',
                    service='fde-consulting',service_label=('需要帮助？了解小范围实施服务','Need help? See small-scale implementation services')[lang],projects=[],
                    sections=sections,sources=[dict(title=source[k]['title'][lang],url=source[k]['url']) for k in row['source']],
                    search_text=' '.join(row['title'] + row['answer'] + row['exercise'] + row['problem'] + [v for step in row['steps'] for v in step] + trial['input'] + [zh_name,en_name]),
                    reviewed='2026-10-17',related=row.get('related',[])))
    if len({a['slug'] for a in result[0]})!=100: raise ValueError('Expected 100 unique tutorials')
    return result
