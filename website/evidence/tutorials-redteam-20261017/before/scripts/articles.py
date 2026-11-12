"""Evidence-bounded local reading pages, using the existing site shell."""
from components import escape
from tutorials import CATEGORIES


def cards(items, base='', heading=3, lang='zh-CN'):
    if heading not in (2, 3):
        raise ValueError('Article row heading must be H2 or H3')
    read = 'Read' if lang == 'en' else '阅读'
    return '<div class="article-list">' + ''.join(
        f'<article class="article-row" data-category="{escape(item.get("category_id", "cases"))}" data-search="{escape(item.get("search_text", item["title"] + " " + item["summary"]))}"><div class="article-row-meta"><span>{escape(item["category"])}</span>'
        f'<span>{escape(item["reading"])}</span></div><div class="article-row-copy">'
        f'<h{heading}><a href="{base}articles/{item["slug"]}.html">{escape(item["title"])}</a></h{heading}>'
        f'<p>{escape(item["summary"])}</p></div><a class="article-row-link text-link" '
        f'href="{base}articles/{item["slug"]}.html" aria-label="{read}: {escape(item["title"])}">{read} <span aria-hidden="true">↗</span></a></article>'
        for item in items) + '</div>'


def preview(items, lang='zh-CN'):
    eyebrow, title, all_label = (('From real project work', 'Practical notes', 'All articles')
                                if lang == 'en' else ('从实际工作出发', '实践文章', '全部文章'))
    return ('<section class="practice-articles" id="articles" aria-labelledby="articles-title">'
            f'<div class="work-heading"><div><p class="meta">{eyebrow}</p>'
            f'<h2 id="articles-title">{title}</h2></div><a class="text-link" href="articles.html">{all_label} ↗</a></div>'
            + cards(items[:2], lang=lang) + '</section>')


def localized_items(r):
    return r.seo['articles']['en' if r.lang == 'en' else 'articles']


def listing(r):
    english = r.lang == 'en'
    items = localized_items(r)
    heading = 'AI tutorials and practical notes' if english else 'AI 入门教程与实践文章'
    intro = ('100 short lessons for beginners, from the first question to agents and office tasks. Each includes steps, a practice prompt and troubleshooting. Two project-based articles are also included.' if english else '100 篇基础教程，从第一次提问到 Agent 和日常办公。每篇都有步骤、练习和排错办法，也保留两篇结合实际项目的文章。')
    categories = [('all', '全部', 'All'), ('cases', '案例实践', 'Case notes')] + CATEGORIES
    options = ''.join(f'<option value="{key}">{escape(en if english else zh)}</option>' for key,zh,en in categories)
    recommended = ['what-is-ai','first-ai-task','prompt-basics','what-is-agent','owner-ai-first-step']
    start = ''.join(f'<a href="articles/{slug}.html">{escape(next(a["title"] for a in items if a["slug"] == slug))} <span aria-hidden="true">↗</span></a>' for slug in recommended)
    controls = ('<form class="article-controls" data-library-controls hidden role="search">'
        f'<label>{"Search articles" if english else "搜索文章"}<input name="q" type="search" placeholder="{"Try Agent, GitHub or notes" if english else "试试 Agent、GitHub、会议纪要"}" autocomplete="off"></label>'
        f'<label>{"Category" if english else "分类"}<select name="category">{options}</select></label>'
        f'<button type="reset">{"Clear" if english else "清除"}</button></form>'
        '<div class="article-results" data-library-status role="status" aria-live="polite"></div>')
    body = ('<main id="main" class="detail-main articles-main" data-article-library><div class="detail-header">'
        f'<p class="meta">{"Learn one task at a time" if english else "一次弄懂一个问题"}</p><h1 data-motion-title>{heading}</h1><p class="detail-intro">{intro}</p></div>'
        f'<details class="article-start"><summary>{"New here? Start with these five lessons" if english else "不知道从哪看？先读这五篇"}</summary><nav aria-label="{"Suggested starting points" if english else "入门阅读顺序"}">{start}</nav></details>'
        + controls + cards(items, heading=2, lang=r.lang)
        + f'<p data-library-empty hidden>{"No articles match. Try fewer words or clear the filters." if english else "没有匹配的文章，试试更短的词，或清除筛选。"}</p>'
        + '<nav class="article-pagination" data-library-pages hidden aria-label="'+('Article pages' if english else '文章分页')+'">'
        + f'<button type="button" data-library-prev>{"Previous" if english else "上一页"}</button><span data-library-page></span><button type="button" data-library-next>{"Next" if english else "下一页"}</button></nav>'
        + '<script defer src="assets/article-library.js"></script></main>')
    return r.shell(heading, body, current='articles', page_path='articles.html')


def detail(r, item):
    english = r.lang == 'en'
    related_label = 'Related cases' if english else '相关案例'
    contents, index = '', ''
    for section in item['sections']:
        sid = escape(section['id'])
        index += f'<a href="#{sid}">{escape(section["title"])}</a>'
        kind = section.get('kind', '')
        contents += f'<section id="{sid}" class="article-section {escape(kind)}"><h2>{escape(section["title"])}</h2>'
        if section.get('label'):
            contents += '<p class="calculation-label">' + escape(section['label']) + '</p>'
        contents += ''.join('<p>' + escape(p) + '</p>' for p in section['paragraphs'])
        if section.get('prompt'):
            contents += '<pre class="article-prompt"><code>' + escape(section['prompt']) + '</code></pre>'
        if section.get('bullets'):
            contents += '<ul class="article-points">' + ''.join('<li>' + escape(p) + '</li>' for p in section['bullets']) + '</ul>'
        if section.get('rows'):
            contents += '<dl class="article-calculation">' + ''.join(
                '<div><dt>' + escape(label) + '</dt><dd>' + escape(value) + '</dd></div>'
                for label, value in section['rows']) + '</dl>'
        contents += ''.join('<p>' + escape(p) + '</p>' for p in section.get('paragraphs_after', []))
        if section.get('projects'):
            contents += f'<nav class="article-case-links" aria-label="{related_label}">' + ''.join(
                f'<a class="text-link" data-article-case href="../cases/{pid.lower()}.html">'
                f'{escape(r.title(r.projects[pid]))} ↗</a>' for pid in section['projects']) + '</nav>'
        contents += '</section>'
    if item.get('sources'):
        label = 'References and scope' if english else '参考资料与适用范围'
        index += f'<a href="#sources">{label}</a>'
        note = ('Concepts and product guidance checked against official documentation on 2026-10-17. The exercises are original teaching examples, not hands-on test receipts or customer results. Interfaces and availability may change.' if english else '概念及产品说明按 2026-10-17 官方资料核对。练习为原创教学示例，不代表实际操作回执或客户效果；界面与功能可用性以当前产品为准。')
        contents += f'<section id="sources" class="article-section"><h2>{label}</h2><p>{note}</p><ul class="article-points">' + ''.join(f'<li><a href="{escape(source["url"])}" rel="noopener">{escape(source["title"])}</a></li>' for source in item['sources']) + '</ul></section>'
    all_other = [a for a in localized_items(r) if a['slug'] != item['slug']]
    same = [a for a in all_other if a.get('category_id', 'cases') == item.get('category_id', 'cases')]
    if item.get('lesson'):
        same.sort(key=lambda a: (a.get('lesson',0) <= item['lesson'], abs(a.get('lesson',0)-item['lesson'])))
    other = (same + [a for a in all_other if a not in same])[:3]
    body = r.template('article', title=escape(item['title']), category=escape(item['category']),
                      date=escape(item['date']), reading=escape(item['reading']), intro=escape(item['intro']),
                      takeaway=escape(item['takeaway']), section_index=index, sections=contents,
                      service=item['service'], service_label=escape(item['service_label']),
                      related=cards(other, '../', lang=r.lang),
                      back_label='← Back to articles' if english else '← 返回文章',
                      written_label='Written on' if english else '写于',
                      index_label='On this page' if english else '文章目录',
                      contact_heading='Start with one task' if english else '先聊一项具体工作',
                      contact_copy=('Describe the current process and its slowest step. The initial conversation is free.'
                                    if english else '说说现在怎么做、哪一步最费时间。初次沟通免费。'),
                      consult_label='Let’s talk' if english else '免费聊聊',
                      next_label='Keep reading' if english else '继续阅读')
    return r.shell(item['title'], body, '../', 'articles', 'articles/' + item['slug'] + '.html')
