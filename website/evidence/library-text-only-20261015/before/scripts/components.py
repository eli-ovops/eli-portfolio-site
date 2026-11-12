# -*- coding: utf-8 -*-
"""Shared HTML components. Content is escaped here; templates accept rendered HTML."""
import html
import hashlib
import json
import posixpath
import re
import xml.etree.ElementTree as ET
from localization import translate_ui
from seo import load_config, metadata
from string import Template

# The same client-project set already used by the About page. Client context
# is independent of the record's artifact type and does not imply acceptance.
CLIENT_PROJECT_IDS = ('P05', 'P02', 'P03', 'P10', 'P36', 'P09', 'P04', 'P07', 'P08')

# Local, inert brand artwork only: gradients are fragment references, never URLs.
SOCIAL_SVG_ATTRIBUTES = {
    'svg': {'viewBox', 'fill'},
    'path': {'d', 'fill', 'transform'},
    'rect': {'x', 'y', 'width', 'height', 'rx', 'fill'},
    'circle': {'cx', 'cy', 'r', 'fill'},
    'defs': set(),
    'linearGradient': {'id', 'x1', 'x2', 'y1', 'y2'},
    'stop': {'offset', 'stop-color'},
}


def escape(value):
    return html.escape(str(value or ''), quote=True)


def international_phone(phone):
    """Format the owner's existing Chinese mobile number; leave unknown formats alone."""
    if re.fullmatch(r'1[3-9][0-9]{9}', phone or ''):
        return '+86' + phone
    return phone


class Renderer:
    def __init__(self, root, profile, projects, images, lang="zh-CN"):
        self.root = root
        self.lang = lang
        self.seo = load_config(root)
        self.templates = root / 'templates'
        self.profile = profile
        self.projects = {p['id']: p for p in projects}
        self.images = images
        self.technical = json.loads((root / 'content/technical-details.json').read_text())
        self.case_examples = json.loads((root / 'content/case-examples.json').read_text())
        socials = root / 'content/social-links.json'
        self.socials = json.loads(socials.read_text()) if socials.is_file() else []
        previews = root / "content/image-previews.json"
        self.previews = json.loads(previews.read_text()) if previews.is_file() else {}
        # These small, local brand paths render with HTML instead of lazy image requests.
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        self.social_icons = {}
        for social in self.socials:
            key = social['icon']
            if not re.fullmatch(r'[a-z]+', key):
                raise ValueError('Invalid social icon name')
            icon = ET.fromstring((root / 'assets/social-icons' / (key + '.svg')).read_text())
            if icon.tag != '{http://www.w3.org/2000/svg}svg':
                raise ValueError('Invalid social SVG root: ' + key)
            gradients = set()
            for node in icon.iter():
                tag = node.tag.removeprefix('{http://www.w3.org/2000/svg}')
                if node.tag != '{http://www.w3.org/2000/svg}' + tag or tag not in SOCIAL_SVG_ATTRIBUTES or any(
                    attr not in SOCIAL_SVG_ATTRIBUTES[tag] for attr in node.attrib
                ):
                    raise ValueError('Unexpected social icon content: ' + key)
                if 'id' in node.attrib:
                    identifier = node.attrib['id']
                    if not re.fullmatch('social-' + key + r'-[a-z]+', identifier) or identifier in gradients:
                        raise ValueError('Invalid social gradient ID: ' + key)
                    gradients.add(identifier)
                if 'transform' in node.attrib and not re.fullmatch(
                    r'(?:\s*(?:translate|scale)\([\d\s.,+\-e]+\))+\s*', node.attrib['transform']
                ):
                    raise ValueError('Invalid social transform: ' + key)
            for node in icon.iter():
                for attr in ('fill', 'stop-color'):
                    value = node.get(attr)
                    gradient_fill = attr == 'fill' and value in {
                        'url(#' + identifier + ')' for identifier in gradients
                    }
                    if value is not None and not re.fullmatch(r'#[0-9a-fA-F]{6}', value) and not gradient_fill:
                        raise ValueError('Invalid social color reference: ' + key)
            icon.attrib.update({'class': 'social-icon', 'aria-hidden': 'true', 'focusable': 'false', 'width': '24', 'height': '24'})
            self.social_icons[key] = ET.tostring(icon, encoding='unicode')

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
            'P12': ('weave', 'brand-ai', '内容工作台', '内容编辑\n人工确认'),
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
                     + visual + '<span class="image-view-hint" aria-hidden="true">'
                     + ('Enlarge screenshot' if self.lang == 'en' else '放大截图') + ' ↗</span></a>')
            image_link = ''
        else:
            media = (f'<button type="button" class="project-image" data-reveal="image" data-case-toggle '
                     f'aria-controls="process-{p["id"].lower()}" aria-expanded="false" aria-label="展开 {escape(self.title(p))} 案例">'
                     + visual + '</button>')
            image_link = '<p class="case-evidence-note">流程示意 · 非客户系统截图</p>'
        case_link = (f'<a class="text-link case-detail-link" href="cases/{p["id"].lower()}.html" '
                     f'aria-label="{escape(("Full case study: " if self.lang == "en" else "完整案例：") + self.title(p))}">'
                     + ('Full case study ↗' if self.lang == 'en' else '完整案例 ↗') + '</a>')
        delivery_note = ('<p class="case-stage">' + ('Delivered' if self.lang == 'en' else '已交付') + '</p>'
                         if project_id in ('P09', 'P10') else '')
        return self.template('gallery-project', id=p['id'].lower(), anchor=anchor_attr,
                             skin=skin, group=group, label=escape(label),
                             word=escape(word).replace('\n', '<br>'), visual=visual, media=media,
                             title=escape(self.title(p)), summary=escape(p['displaySummary']), related=related, process=process, image_link=image_link, case_link=case_link, delivery_note=delivery_note)

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
            # Search describes the work; the artifact category belongs to filters.
            # An inventory app must not match "website" only because it is a tool.
            aliases = {
                'P09': ('库存 扫码 条码 出入库 进销存', 'inventory barcode stock management'),
                'P10': ('库存 盘点 采购 进销存', 'inventory stocktake stock management'),
                'P02': ('网站 官网 公益官网', 'website nonprofit website'),
                'P03': ('网站 官网 律所官网', 'website law firm website'),
                'P07': ('网站 官网 企业官网 品牌官网', 'website company website brand website'),
                'P11': ('网站 官网 网站改版', 'website website redesign'),
            }
            alias = aliases.get(p['id'], ('', ''))[self.lang == 'en']
            search = ' '.join([self.title(p), p['displaySummary'], alias])
            client = p['id'] in CLIENT_PROJECT_IDS
            attributes = (f'data-category="{escape(p["category"])}" data-client="{str(client).lower()}" '
                          f'data-search="{escape(search)}"')
        preview = self.image(p, preview=True)
        if preview:
            preview = re.sub(r' sizes="[^"]+"', ' sizes="96px"', preview)
        else:
            preview = '<span>' + escape(p['id']) + '</span>'
        preview = '<span class="archive-preview" aria-hidden="true">' + preview + '</span>'
        return self.template('archive-row', attributes=attributes, id=p['id'].lower(), preview=preview,
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
        methods = []
        if email:
            methods.append(f'<div class="footer-contact-method"><p>邮箱</p><a href="mailto:{escape(email)}">{escape(email)} ↗</a></div>')
        if phone:
            phone_label = 'Phone' if self.lang == 'en' else '电话'
            number = international_phone(phone)
            methods.append(f'<div class="footer-contact-method"><p>{phone_label}</p><a href="tel:{escape(number)}">{escape(number)} ↗</a></div>')
        contact = '<div class="footer-contacts" aria-label="联系方式">' + ''.join(methods) + '</div>'

        social_label = 'Social profiles' if self.lang == 'en' else '社交主页'
        social_links = ''
        for social in self.socials:
            label = social['en'] if self.lang == 'en' else social['zh']
            social_links += (f'<a href="{escape(social["url"])}" target="_blank" rel="noopener noreferrer" '
                             f'aria-label="{escape(label)}" title="{escape(label)}">'
                             f'{self.social_icons[social["icon"]]}'
                             f'<span aria-hidden="true">{escape(label)}</span></a>')
        social_nav = f'<nav class="footer-socials" aria-label="{social_label}">{social_links}</nav>'

        page_path = page_path or {'home': 'index.html', 'work': 'records.html', 'about': 'about.html'}.get(current, '404.html')
        location = ('en/' if self.lang == 'en' else '') + page_path
        other = ('' if self.lang == 'en' else 'en/') + page_path
        language_href = posixpath.relpath(other, posixpath.dirname(location) or '.')
        language = ('<a class="language-switch" href="' + escape(language_href)
                    + '" lang="' + ('zh-CN' if self.lang == 'en' else 'en')
                    + '" hreflang="' + ('zh-CN' if self.lang == 'en' else 'en')
                    + '" aria-label="' + ('Switch to Chinese' if self.lang == 'en' else '切换到英文版')
                    + '">' + ('中文' if self.lang == 'en' else 'EN') + '</a>')
        seo = metadata(self.seo, self.profile, self.projects, page_path, self.lang, self.socials)
        rendered = self.template('layout', title=escape(seo['title']), description=escape(seo['description']),
                                 robots=seo['robots'], seo_head=seo['head'], name=escape(name), base=base,
                                 nav=nav, body=body, contact=contact, social_nav=social_nav, lang=self.lang, language_switch=language)
        rendered = rendered.replace('</head>', f'<link rel="stylesheet" href="{base}assets/bits-ui.css">\n'
                                    f'<script src="{base}assets/bits-ui.js" defer></script>\n</head>')
        if current == 'home' and page_path == 'index.html':
            rendered = rendered.replace('</head>', f'<link rel="stylesheet" href="{base}assets/home-ambient.css">\n'
                                        f'<script src="{base}assets/home-ambient.js" defer></script>\n</head>')
        if current == 'about':
            rendered = rendered.replace('</head>', f'<link rel="stylesheet" href="{base}assets/dither-veil.css">\n'
                                        f'<script src="{base}assets/dither-veil.js" defer></script>\n</head>')
        if current in ('work', 'about'):
            # The homepage retains its existing controller. Other pages have one
            # motion owner, instead of nested observers animating the same scene.
            rendered = rendered.replace(f'<script src="{base}motion.js?v=20261008-motion" defer></script>', '')
            plugins = ''
            if page_path == 'records.html':
                plugins = f'<script src="{base}assets/vendor/gsap-3.15.0/Flip.min.js" defer></script>\n'
            elif current == 'about':
                plugins = f'<script src="{base}assets/vendor/gsap-3.15.0/ScrollTrigger.min.js" defer></script>\n'
            arrival = ('<script>addEventListener("pagereveal",function(e){if(!e.viewTransition)return;'
                       'var p=location.pathname,r=document.referrer,back=new URLSearchParams(location.search).has("return");'
                       'var shared=(p.indexOf("/cases/")>=0&&r.indexOf(location.origin)===0&&new URL(r).pathname.endsWith("/records.html"))||(p.endsWith("/records.html")&&back);'
                       'if(shared)document.documentElement.dataset.routeMotion="native-title";'
                       'else{e.viewTransition.skipTransition();document.documentElement.dataset.routeMotion="local";}});</script>')
            rendered = rendered.replace('</head>', f'<link rel="stylesheet" href="{base}assets/editorial.css?v=case-flow-20261009">\n{plugins}{arrival}\n<script src="{base}assets/editorial.js?v=case-flow-20261009" defer></script>\n</head>')
        # Content hashes make changed local scripts/styles fresh for returning visitors.
        for asset in ('styles.css', 'motion.css', 'app.js', 'motion.js',
                      'assets/depth-gallery.js', 'assets/editorial.js', 'assets/editorial.css',
                      'assets/screenshot-viewer.js', 'assets/social-footer.css', 'assets/page-version.js',
                      'assets/home-ambient.css', 'assets/home-ambient.js',
                      'assets/bits-ui.css', 'assets/bits-ui.js',
                      'assets/dither-veil.css', 'assets/dither-veil.js'):
            revision = hashlib.sha256((self.root / asset).read_bytes()).hexdigest()[:12]
            pattern = r'((?:href|src)="' + re.escape(base + asset) + r')(?:\?[^"\s]*)?"'
            rendered = re.sub(pattern, lambda match: match[1] + '?v=' + revision + '"', rendered)
        return translate_ui(rendered) if self.lang == 'en' else rendered
