# -*- coding: utf-8 -*-
"""Shared HTML components. Content is escaped here; templates accept rendered HTML."""
import html
from string import Template


def escape(value):
    return html.escape(str(value or ''), quote=True)


class Renderer:
    def __init__(self, root, profile, projects, images):
        self.templates = root / 'templates'
        self.profile = profile
        self.projects = {p['id']: p for p in projects}
        self.images = images

    def template(self, template_name, **values):
        source = (self.templates / (template_name + '.html')).read_text(encoding='utf-8')
        return Template(source).substitute(values)

    def image_path(self, project, base=''):
        if project.get('publicImage'):
            return base + project['publicImage']
        return base + 'assets/' + project['image'].lower() + '.' + project.get('imageFormat', 'webp')

    def image(self, project, base=''):
        image = project.get('image')
        if not image:
            return ''
        width, height = project.get('publicImageDimensions') or self.images[image.lower()]
        alt = project.get('publicImageAlt') or project.get('imageAlt') or (self.title(project) + '界面展示')
        return (f'<img src="{escape(self.image_path(project, base))}" '
                f'alt="{escape(alt)}" '
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

    def gallery_card(self, project_id, personal=False):
        p = self.projects[project_id]
        covers = {
            'P02': ('charity', 'websites', '公益网站', 'PUBLIC\nGOOD.'),
            'P03': ('legal', 'websites', '律所网站', 'LEGAL\nMATTERS.'),
            'P10': ('inventory', 'systems', '库存管理', 'IN.\nOUT.'),
            'P04': ('office', 'systems', '办公协同', 'WORK\nFLOW.'),
            'P05': ('water', 'brand-ai', '品牌营销', 'WATER.\nEVERYDAY.'),
            'P36': ('support', 'brand-ai', 'AI 客服', 'ASK.\nAI.'),
            'P07': ('furniture', 'personal', '品牌网站', 'ROOM\nTO LIVE.'),
            'P09': ('scan', 'personal', '扫码库存', 'SCAN.\nKEEP TRACK.'),
            'P12': ('weave', 'personal', 'AI 内容工具', 'WEAVE\nIDEAS.'),
            'P13': ('rove', 'personal', '每日任务应用', 'ONE DAY\nAT A TIME.')
        }
        skin, group, label, word = covers[project_id]
        picture = self.image(p)
        if picture:
            visual = '<div class="poster-preview">' + picture + '</div>'
        else:
            visual = ('<svg class="office-art" viewBox="0 0 400 230" aria-hidden="true">'
                      '<path d="M32 176H120V70H280V176H368" fill="none" stroke="currentColor" stroke-width="2"/>'
                      '<circle cx="32" cy="176" r="13" fill="currentColor"/>'
                      '<circle cx="200" cy="70" r="13" fill="currentColor"/>'
                      '<circle cx="368" cy="176" r="13" fill="currentColor"/></svg>')
        anchor = {'P02': 'websites', 'P10': 'systems', 'P05': 'brand-ai'}.get(project_id)
        anchor_attr = f' id="{anchor}"' if anchor and not personal else ''
        related = self.link(self.projects['P08'], '产品目录') if project_id == 'P07' else ''
        return self.template('gallery-project', id=p['id'].lower(), anchor=anchor_attr,
                             skin=skin, group=group, label=escape(label),
                             word=escape(word).replace('\n', '<br>'), visual=visual,
                             title=escape(self.title(p)), summary=escape(p['displaySummary']), related=related)

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
                             name=escape(p.get('publicTitle') or p['name']), summary=escape(p['displaySummary']))

    def shell(self, title, body, base='', current=''):
        name = self.profile.get('displayName') or '实践档案'
        routes = [('home', '首页', 'index.html'), ('work', '作品', 'index.html#work'),
                  ('about', '关于', 'about.html')]
        nav = ''
        for key, label, path in routes:
            active = ' aria-current="page"' if key == current else ''
            nav += f'<a data-nav="{key}" href="{base}{path}"{active}>{label}</a>'
        email = self.profile.get('email')
        contact = f'<a class="text-link" href="mailto:{escape(email)}">邮件联系 ↗</a>' if email else ''
        return self.template('layout', title=escape(title), name=escape(name), base=base,
                             nav=nav, body=body, contact=contact)
