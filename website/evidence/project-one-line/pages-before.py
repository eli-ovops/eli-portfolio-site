# -*- coding: utf-8 -*-
"""Page composition; no file writes, network requests or global content state."""
from components import escape


def shared_content(r, profile, projects):
    client_ids = ('P05', 'P02', 'P03', 'P10', 'P36', 'P09', 'P04', 'P07', 'P08')
    def project_entry(p):
        paragraphs = [p['processSummary']] if p.get('processSummary') else [text for entry in p['publicStory'] for text in entry['paragraphs']]
        return ('<li><h4>' + escape(r.title(p)) + '</h4>'
                + ''.join('<p>' + escape(text) + '</p>' for text in paragraphs) + '</li>')
    remaining = [p for p in projects if p['id'] not in client_ids + ('P01', 'P06', 'P13')]
    groups = [('客户项目', [r.projects[pid] for pid in client_ids]),
              ('产品与工具实践', [p for p in remaining if p['category'] in ('网站与工具', 'App 实践')]),
              ('研究与工作方法', [p for p in remaining if p['category'] not in ('网站与工具', 'App 实践')])]
    clients = ''.join('<section class="project-experience-group"><h3>' + escape(label)
                      + '</h3><ul class="project-experience-grid">' + ''.join(project_entry(p) for p in items)
                      + '</ul></section>' for label, items in groups)
    filters = ''
    categories = [('全部', '全部'), ('客户参与', '客户项目'), ('网站与工具', '网站与工具'),
                  ('App 实践', '移动应用'), ('内容与研究', '内容与研究'), ('方法与支持', '方法与工具')]
    for category, label in categories:
        pressed = str(category == '全部').lower()
        filters += (f'<button type="button" data-filter="{escape(category)}" '
                    f'aria-pressed="{pressed}">{escape(label)}</button>')
    fields = {key: escape(profile[key]) for key in ('intro', 'personality', 'about', 'background')}
    fields['headline'] = escape(profile['headline']).replace('\n', '<br>')
    return dict(fields, clients=clients, filters=filters,
                archive=''.join(r.archive_row(p) for p in projects))


def home(r, profile, projects):
    shared = shared_content(r, profile, projects)
    shared['public_name'] = escape(profile.get('displayName') or '作者')
    shared['featured_gallery'] = ''.join(r.gallery_card(pid) for pid in ('P05', 'P02', 'P10', 'P36', 'P09', 'P12', 'P04'))
    body = r.template('home', **shared)
    return r.shell('Eli · FDE 与项目经历', body, current='home')


def about(r, profile, projects):
    shared = shared_content(r, profile, projects)
    email = profile.get('email')
    methods = ''
    if email:
        methods += (f'<div class="contact-method"><p>邮箱</p>'
                    f'<a class="text-link" href="mailto:{escape(email)}">{escape(email)} ↗</a></div>')
    phone = profile.get('phone')
    if phone:
        methods += (f'<div class="contact-method"><p>电话</p>'
                    f'<a class="text-link" href="tel:{escape(phone)}">{escape(phone)} ↗</a></div>')
    shared['contact_content'] = '<div class="contact-methods">' + methods + '</div>'
    qr = profile.get('wechatQr')
    shared['wechat_qr'] = (
        '<figure class="wechat-contact"><h3>微信</h3>'
        f'<a href="{escape(qr)}" target="_blank" rel="noopener noreferrer" aria-label="放大微信二维码">'
        f'<img src="{escape(qr)}" width="728" height="728" loading="lazy" decoding="async" alt="Eli 的微信二维码">'
        '</a></figure>' if qr else '')
    body = r.template('about', **shared)
    return r.shell('关于我', body, current='about')


def records(r, profile, projects):
    body = r.template('records', **shared_content(r, profile, projects))
    return r.shell('项目索引', body)


def case(r, p):
    image = ''
    if p.get('image'):
        image = (f'<figure class="detail-image {p["id"].lower()}">{r.image(p, "../")}'
                 '<figcaption>'
                 f'<a class="text-link" href="{escape(r.image_path(p, "../"))}" target="_blank" rel="noopener noreferrer">查看大图 ↗</a>'
                 '</figcaption></figure>')
    fields = {k: escape(v) for k, v in p.items() if isinstance(v, str)}
    fields['image'] = image
    fields['project_summary'] = escape(p.get('processSummary') or p['displaySummary'])
    study = p.get('caseStudy', {})
    fields['case_title'] = escape(p.get('publicTitle') or p.get('homePreview', {}).get('title') or p['name'])
    sections, index = '', ''
    for entry in p['publicStory']:
        key, title = entry['id'], entry['title']
        section = (f'<section id="{key}"><h2>{escape(title)}</h2>'
                   + ''.join(f'<p>{escape(text)}</p>' for text in entry['paragraphs']))
        sections += section + '</section>'
        index += f'<a href="#{key}">{escape(title)}</a>'
    if p.get('publicUrl') and not p.get('anonymized'):
        sections += (f'<section id="evidence"><h2>项目链接</h2><p><a class="text-link" href="{escape(p["publicUrl"])}" '
                     'target="_blank" rel="noopener noreferrer">打开项目网站 ↗</a></p></section>')
        index += '<a href="#evidence">项目链接</a>'
    fields.update(case_sections=sections, case_index=index)
    fields['related'] = ''.join(
        f'<p class="case-related"><a class="text-link" href="{pid.lower()}.html">'
        f'{escape(r.projects[pid].get("publicTitle") or r.projects[pid]["name"])} ↗</a></p>' for pid in study.get('related', []))
    body = r.template('case', **fields)
    return r.shell(r.title(p), body, '../', 'work')


def not_found(r):
    body = ('<main id="main" class="not-found"><p class="meta">404</p>'
            '<h1>页面未找到</h1><p>请返回首页浏览项目。</p>'
            '<a class="primary" href="/index.html">返回首页 ↗</a></main>')
    return r.shell('未找到页面', body, '/')
