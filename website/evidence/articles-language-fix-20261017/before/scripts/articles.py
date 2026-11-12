"""Evidence-bounded local reading pages, using the existing site shell."""
from components import escape


def cards(items, base='', heading=3):
    if heading not in (2, 3):
        raise ValueError('Article row heading must be H2 or H3')
    return '<div class="article-list">' + ''.join(
        f'<article class="article-row"><div class="article-row-meta"><span>{escape(item["category"])}</span>'
        f'<span>{escape(item["reading"])}</span></div><div class="article-row-copy">'
        f'<h{heading}><a href="{base}articles/{item["slug"]}.html">{escape(item["title"])}</a></h{heading}>'
        f'<p>{escape(item["summary"])}</p></div><a class="article-row-link text-link" '
        f'href="{base}articles/{item["slug"]}.html" aria-label="阅读：{escape(item["title"])}">阅读 <span aria-hidden="true">↗</span></a></article>'
        for item in items) + '</div>'


def preview(items):
    return ('<section class="practice-articles" id="articles" aria-labelledby="articles-title">'
            '<div class="work-heading"><div><p class="meta">从实际工作出发</p>'
            '<h2 id="articles-title">实践文章</h2></div><a class="text-link" href="articles.html">全部文章 ↗</a></div>'
            + cards(items) + '</section>')


def listing(r):
    body = ('<main id="main" class="detail-main articles-main"><div class="detail-header">'
            '<p class="meta">工具、流程与小范围实施</p><h1 data-motion-title>实践文章</h1>'
            '<p class="detail-intro">结合实际项目，聊聊重复工作从哪里改、怎么试，以及怎样判断有没有帮助。</p>'
            '</div>' + cards(r.seo['articles']['articles'], heading=2) + '</main>')
    return r.shell('实践文章', body, current='articles', page_path='articles.html')


def detail(r, item):
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
            contents += '<nav class="article-case-links" aria-label="相关案例">' + ''.join(
                f'<a class="text-link" data-article-case href="../cases/{pid.lower()}.html">'
                f'{escape(r.title(r.projects[pid]))} ↗</a>' for pid in section['projects']) + '</nav>'
        contents += '</section>'
    other = [a for a in r.seo['articles']['articles'] if a['slug'] != item['slug']]
    body = r.template('article', title=escape(item['title']), category=escape(item['category']),
                      date=escape(item['date']), reading=escape(item['reading']), intro=escape(item['intro']),
                      takeaway=escape(item['takeaway']), section_index=index, sections=contents,
                      service=item['service'], service_label=escape(item['service_label']),
                      related=cards(other, '../'))
    return r.shell(item['title'], body, '../', 'articles', 'articles/' + item['slug'] + '.html')
