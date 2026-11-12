# -*- coding: utf-8 -*-
"""Shared HTML components. Content is escaped here; templates accept rendered HTML."""
import html
import json
import posixpath
from localization import translate_ui
from seo import load_config, metadata
from string import Template


def escape(value):
    return html.escape(str(value or ''), quote=True)


class Renderer:
    def __init__(self, root, profile, projects, images, lang="zh-CN"):
        self.lang = lang
        self.seo = load_config(root)
        self.templates = root / 'templates'
        self.profile = profile
        self.projects = {p['id']: p for p in projects}
        self.images = images
        previews = root / "content/image-previews.json"
        self.previews = json.loads(previews.read_text()) if previews.is_file() else {}

    def template(self, template_name, **values):
        source = (self.templates / (template_name + '.html')).read_text(encoding='utf-8')
        return Template(source).substitute(values)

    def image_path(self, project, base=''):
        if project.get('publicImage'):
            return base + project['publicImage']
        return base + 'assets/' + project['image'].lower() + '.' + project.get('imageFormat', 'webp')

    def image(self, project, base='', preview=False):
        image = project.get('image')
        if not image:
            return ''
        width, height = project.get('publicImageDimensions') or self.images[image.lower()]
        alt = project.get('publicImageAlt') or project.get('imageAlt') or (self.title(project) + '界面展示')
        path = self.image_path(project, base)
        responsive = ''
        if preview and project['id'] in self.previews:
            sources = self.previews[project['id']]['sources']
            path = base + sources[-1]['path']
            srcset = ', '.join(base + item['path'] + ' ' + str(item['width']) + 'w' for item in sources)
            responsive = f' srcset="{escape(srcset)}" sizes="(max-width: 650px) calc(100vw - 64px), (max-width: 1440px) 45vw, 600px"'
        return (f'<img src="{escape(path)}"{responsive} alt="{escape(alt)}" '
                f'loading="lazy" decoding="async" width="{width}" height="{height}">')

    @staticmethod
    def title(project):
        return project.get('publicTitle') or project['name']

    def link(self, project, text='查看案例'):
        return (f'<a class="text-link" href="cases/{project["id"].lower()}.html">'
                f'{escape(text)} <span aria-hidden="true">↗</span></a>')

    def card(self, project_id):
        p = self.projects[project_id]
        return self.template('project-card', id=p['id'].lower(), name=escape(self.title(p)),
                             image=self.image(p), summary=escape(p['displaySummary']))

    def selected_card(self, project_id):
        p = self.projects[project_id]
        return self.template('selected-project', id=p['id'].lower(), image=self.image(p),
                             title=escape(self.title(p)), summary=escape(p['displaySummary']))

    def client_story(self, project_id):
        p = self.projects[project_id]
        return self.template('client-story', id=p['id'].lower(),
                             title=escape(self.title(p)), summary=escape(p['displaySummary']))

    def gallery_card(self, project_id):
        p = self.projects[project_id]
        covers = {
            'P02': ('charity', 'websites', '公益网站', '公益机构\n展示官网'),
            'P03': ('legal', 'websites', '律所网站', '专业服务\n展示官网'),
            'P10': ('inventory', 'systems', '库存管理', '库存管理\n业务系统'),
            'P04': ('office', 'systems', '办公协同', '内部办公\n协同系统'),
            'P05': ('water', 'brand-ai', '品牌营销', '品牌出海\n全域营销'),
            'P36': ('support', 'brand-ai', 'AI 客服', '知识检索\n智能客服'),
            'P07': ('furniture', 'websites', '品牌网站', '品牌展示\n产品官网'),
            'P09': ('scan', 'systems', '扫码库存', '扫码出入库\n库存追踪'),
            'P12': ('weave', 'brand-ai', '小红书营销', '自动做图\n自动上传'),
            'P13': ('rove', 'apps', '每日任务应用', '每日任务\n微冒险应用')
        }
        skin, group, label, word = covers[project_id]
        picture = self.image(p, preview=True)
        if picture:
            visual = '<div class="poster-preview">' + picture + '</div>'
        else:
            visual = ('<svg class="office-art" viewBox="0 0 400 230" aria-hidden="true">'
                      '<path d="M32 176H120V70H280V176H368" fill="none" stroke="currentColor" stroke-width="2"/>'
                      '<circle cx="32" cy="176" r="13" fill="currentColor"/>'
                      '<circle cx="200" cy="70" r="13" fill="currentColor"/>'
                      '<circle cx="368" cy="176" r="13" fill="currentColor"/></svg>')
        anchor = {'P02': 'websites', 'P10': 'systems', 'P05': 'brand-ai'}.get(project_id)
        anchor_attr = f' id="{anchor}"' if anchor else ''
        related = self.inline_case('P08', '产品目录') if project_id == 'P07' else ''
        paragraphs = [p['processSummary']] if p.get('processSummary') else [text for entry in p['publicStory'] for text in entry['paragraphs']]
        process = (f'<details class="project-process" id="process-{p["id"].lower()}"><summary>查看项目过程 ＋</summary>'
                   + ''.join(f'<p>{escape(text)}</p>' for text in paragraphs) + '</details>')
        if picture:
            media = (f'<a class="project-image" data-reveal="image" data-image-view href="{escape(self.image_path(p))}" '
                     f'data-image-title="{escape(self.title(p))}" aria-haspopup="dialog" aria-label="查看 {escape(self.title(p))} 截图">'
                     + visual + '</a>')
            image_link = ''
        else:
            media = (f'<button type="button" class="project-image" data-reveal="image" data-case-toggle '
                     f'aria-controls="process-{p["id"].lower()}" aria-expanded="false" aria-label="展开 {escape(self.title(p))} 案例">'
                     + visual + '</button>')
            image_link = '<p class="case-evidence-note">流程示意 · 非客户系统截图</p>'
        return self.template('gallery-project', id=p['id'].lower(), anchor=anchor_attr,
                             skin=skin, group=group, label=escape(label),
                             word=escape(word).replace('\n', '<br>'), visual=visual, media=media,
                             title=escape(self.title(p)), summary=escape(p['displaySummary']), related=related, process=process, image_link=image_link)

    def inline_case(self, project_id, label):
        p = self.projects[project_id]
        paragraphs = [p['processSummary']] if p.get('processSummary') else [text for entry in p['publicStory'] for text in entry['paragraphs']]
        return ('<details class="project-process supplemental-project"><summary>' + escape(label) + '</summary>'
                + ''.join(f'<p>{escape(text)}</p>' for text in paragraphs) + '</details>')

    def personal_project(self, project_id):
        p = self.projects[project_id]
        related = (self.link(self.projects['P08'], '产品目录') if project_id == 'P07' else '')
        return self.template('personal-project', id=p['id'].lower(), related_link=related,
                             title=escape(self.title(p)), summary=escape(p['displaySummary']))

    def archive_row(self, p, filterable=True):
        attributes = ''
        if filterable:
            search = ' '.join([self.title(p), p['category'], p['displaySummary']])
            attributes = f'data-category="{escape(p["category"])}" data-search="{escape(search)}"'
        return self.template('archive-row', attributes=attributes, id=p['id'].lower(),
                             code=escape(p['id']), category=escape(p['category']),
                             name=escape(p.get('publicTitle') or p['name']), summary=escape(p['displaySummary']))

    def shell(self, title, body, base='', current='', page_path=None):
        name = self.profile.get('displayName') or '实践档案'
        routes = [('home', '首页', 'index.html'), ('work', '项目库', 'records.html'),
                  ('about', '关于', 'about.html')]
        nav = ''
        for key, label, path in routes:
            active = ' aria-current="page"' if key == current else ''
            nav += f'<a data-nav="{key}" href="{base}{path}"{active}>{label}</a>'
        email = self.profile.get('email')
        phone = self.profile.get('phone')
        qr = self.profile.get('wechatQr')
        methods = []
        if email:
            methods.append(f'<div class="footer-contact-method"><p>邮箱</p><a href="mailto:{escape(email)}">{escape(email)} ↗</a></div>')
        if phone:
            methods.append(f'<div class="footer-contact-method"><p>电话</p><a href="tel:{escape(phone)}">{escape(phone)} ↗</a></div>')
        if qr:
            methods.append(f'<div class="footer-contact-method footer-wechat"><p>微信</p><a href="{base}{escape(qr)}"><img src="{base}{escape(qr)}" width="144" height="144" loading="lazy" alt="Eli 的微信二维码"></a></div>')
        contact = '<div class="footer-contacts" aria-label="联系方式">' + ''.join(methods) + '</div>'

        page_path = page_path or {'home': 'index.html', 'work': 'records.html', 'about': 'about.html'}.get(current, '404.html')
        location = ('en/' if self.lang == 'en' else '') + page_path
        other = ('' if self.lang == 'en' else 'en/') + page_path
        language_href = posixpath.relpath(other, posixpath.dirname(location) or '.')
        language = ('<a class="language-switch" href="' + escape(language_href)
                    + '" lang="' + ('zh-CN' if self.lang == 'en' else 'en')
                    + '" hreflang="' + ('zh-CN' if self.lang == 'en' else 'en')
                    + '" aria-label="' + ('Switch to Chinese' if self.lang == 'en' else '切换到英文版')
                    + '">' + ('中文' if self.lang == 'en' else 'EN') + '</a>')
        seo = metadata(self.seo, self.profile, self.projects, page_path, self.lang)
        rendered = self.template('layout', title=escape(seo['title']), description=escape(seo['description']),
                                 robots=seo['robots'], seo_head=seo['head'], name=escape(name), base=base,
                                 nav=nav, body=body, contact=contact, lang=self.lang, language_switch=language)
        if current in ('work', 'about'):
            rendered = rendered.replace('</head>', f'<link rel="stylesheet" href="{base}assets/editorial.css?v=local-20261008">\n<script src="{base}assets/editorial.js?v=local-20261008" defer></script>\n</head>')
        return translate_ui(rendered) if self.lang == 'en' else rendered
