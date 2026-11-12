"""Evidence-bounded local reading pages, using the existing site shell."""
from components import escape


def cards(items, base='', heading=3, lang='zh-CN'):
    if heading not in (2, 3):
        raise ValueError('Article row heading must be H2 or H3')
    read = 'Read' if lang == 'en' else '阅读'
    return '<div class="article-list">' + ''.join(
        f'<article class="article-row"><div class="article-row-meta"><span>{escape(item["category"])}</span>'
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
            + cards(items, lang=lang) + '</section>')


def localized_items(r):
    return r.seo['articles']['en' if r.lang == 'en' else 'articles']


def listing(r):
    english = r.lang == 'en'
    eyebrow = 'Tools, workflows and small-scale implementation' if english else '工具、流程与小范围实施'
    heading = 'Practical notes' if english else '实践文章'
    intro = ('Lessons from project work: where to start, how to run a small trial and how to judge whether it helps.'
             if english else '结合实际项目，聊聊重复工作从哪里改、怎么试，以及怎样判断有没有帮助。')
    body = ('<main id="main" class="detail-main articles-main"><div class="detail-header">'
            f'<p class="meta">{eyebrow}</p><h1 data-motion-title>{heading}</h1>'
            f'<p class="detail-intro">{intro}</p>'
            '</div>' + cards(localized_items(r), heading=2, lang=r.lang) + '</main>')
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
    other = [a for a in localized_items(r) if a['slug'] != item['slug']]
    body = r.template('article', title=escape(item['title']), category=escape(item['category']),
                      date=escape(item['date']), reading=escape(item['reading']), intro=escape(item['intro']),
                      takeaway=escape(item['takeaway']), section_index=index, sections=contents,
                      service=item['service'], service_label=escape(item['service_label']),
                      related=cards(other, '../', lang=r.lang),
                      back_label='← Back to articles' if english else '← 返回实践文章',
                      written_label='Written on' if english else '写于',
                      index_label='On this page' if english else '文章目录',
                      contact_heading='Start with one task' if english else '先聊一项具体工作',
                      contact_copy=('Describe the current process and its slowest step. The initial conversation is free.'
                                    if english else '说说现在怎么做、哪一步最费时间。初次沟通免费。'),
                      consult_label='Let’s talk' if english else '免费聊聊',
                      next_label='Keep reading' if english else '继续阅读')
    return r.shell(item['title'], body, '../', 'articles', 'articles/' + item['slug'] + '.html')
