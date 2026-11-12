"""SEO metadata and launch-ready sitemap for the existing static portfolio."""
import html
import ipaddress
import json
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
from project_order import prioritize_projects


def load_config(root):
    config = json.loads((root / 'content/seo.json').read_text())
    if 'articles' not in config:
        config['articles'] = json.loads((root / 'content/articles.json').read_text())
    if 'en' not in config['articles']:
        config['articles']['en'] = json.loads((root / 'content/articles-en.json').read_text())['articles']
    from tutorials import load_tutorials
    lessons_zh, lessons_en = load_tutorials(root)
    config['articles']['articles'].extend(lessons_zh)
    config['articles']['en'].extend(lessons_en)
    original, translated = config['articles']['articles'], config['articles']['en']
    if [a['slug'] for a in original] != [a['slug'] for a in translated]:
        raise ValueError('Article translations must cover every Chinese article')
    for zh, en in zip(original, translated):
        if ([s['id'] for s in zh['sections']] != [s['id'] for s in en['sections']]
                or zh['projects'] != en['projects'] or zh['service'] != en['service']):
            raise ValueError('Article translations must preserve sections, cases and service')
    parsed = urlparse(config['base_url'])
    if (parsed.scheme not in ('https', 'http') or not parsed.hostname
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or not config['base_url'].endswith('/') or '..' in parsed.path.split('/')):
        raise ValueError('Invalid SEO base_url')
    if not isinstance(config.get('indexing_enabled'), bool):
        raise ValueError('Explicit SEO indexing_enabled boolean required')
    if config['indexing_enabled']:
        try:
            ipaddress.ip_address(parsed.hostname)
            literal_ip = True
        except ValueError:
            literal_ip = False
        # Project launch safeguard: do not accidentally index the preview/IP release.
        if parsed.scheme != 'https' or literal_ip or parsed.hostname == 'localhost' or '.' not in parsed.hostname:
            raise ValueError('Indexing requires the verified HTTPS domain; preview/IP URLs must stay disabled')
    return config


def page_url(config, page_path, lang='zh-CN'):
    prefix = 'en/' if lang == 'en' else ''
    path = '' if page_path == 'index.html' else page_path
    return config['base_url'] + prefix + path


def alternates(config, page_path):
    return {lang: page_url(config, page_path, lang) for lang in ('zh-CN', 'en')}


def metadata(config, profile, projects, page_path, lang, socials=()):
    english = lang == 'en'
    missing = page_path == '404.html'
    service_page = next((s for s in config.get('service_pages', [])
                         if page_path == 'services/' + s['slug'] + '.html'), None)
    page_type = 'WebPage'
    writing_page = page_path == 'articles.html' or page_path.startswith('articles/')
    article = next((item for item in config['articles']['en' if english else 'articles']
                    if page_path == 'articles/' + item['slug'] + '.html'), None)
    if page_path.startswith('cases/'):
        project = projects[page_path.rsplit('/', 1)[1].split('.')[0].upper()]
        name = project.get('publicTitle') or project['name']
        title = name + (' | Eli Case Study' if english else '案例 - Eli')
        title = config.get('case_titles', {}).get(project['id'], {}).get(lang, title)
        description = project['displaySummary']
        if project['id'] == 'P36' and any(section['id'] == 'qa' for section in project['publicStory']):
            description += (' Answers are AI-written illustrations, not real support records.' if english
                            else ' 问答为 AI 拟写示意，非真实客服记录。')
    elif service_page:
        text = service_page[lang]
        title, description = text['title'], text['description']
    elif writing_page:
        title = article['title'] + ' - Eli' if article else ('AI beginner tutorials, agents and office tasks | Eli' if english else 'AI 入门教程｜Agent、办公实操与老板用 AI - Eli')
        description = article['summary'] if article else ('100 bilingual beginner lessons on AI, language models, agents, skills, GitHub and office tasks, plus project-based practical notes.' if english else '100 篇中英双语 AI 基础教程，涵盖大模型、Agent、Skills、GitHub、WorkBuddy、办公实操与老板用 AI，并保留真实项目实践文章。')
        page_type = 'Article' if article else 'CollectionPage'
    elif missing:
        title = 'Page not found | Eli' if english else '页面未找到｜Eli'
        description = 'This page could not be found. Explore Eli’s projects from the homepage.' if english else '当前页面未找到，请从首页浏览 Eli 的项目与联系信息。'
    else:
        key = {'index.html': 'home', 'about.html': 'about', 'records.html': 'records'}[page_path]
        text = config[key][lang]
        title, description = text['title'], text['description']
        page_type = {'home': 'WebPage', 'about': 'AboutPage', 'records': 'CollectionPage'}[key]
    canonical = page_url(config, page_path, lang)
    robots = 'index,follow' if config['indexing_enabled'] and not missing else 'noindex,nofollow'
    if writing_page and config['articles']['publication_status'] != 'published':
        robots = 'noindex,nofollow'
    esc = lambda text: html.escape(text, quote=True)
    head = ''
    head += '<meta name="author" content="' + esc(profile['displayName']) + '">\n'
    head += '<meta http-equiv="content-language" content="' + lang + '">\n'
    if not missing:
        head += '<link rel="canonical" href="' + esc(canonical) + '">\n'
        pair = alternates(config, page_path)
        for code, url in (dict(pair, **{'x-default': pair['zh-CN']}) if pair else {}).items():
            head += '<link rel="alternate" hreflang="' + code + '" href="' + esc(url) + '">\n'
        for key, value in {'og:type': 'website', 'og:title': title, 'og:description': description,
                           'og:url': canonical, 'og:site_name': 'Eli',
                           'og:locale': 'en_US' if english else 'zh_CN',
                           'og:locale:alternate': 'zh_CN' if english else 'en_US'}.items():
            head += '<meta property="' + key + '" content="' + esc(value) + '">\n'
        head += '<meta name="twitter:card" content="summary">\n'
        head += '<meta name="twitter:title" content="' + esc(title) + '">\n'
        head += '<meta name="twitter:description" content="' + esc(description) + '">\n'
        # Share the same image visitors see; never expose a raw anonymized-client asset.
        if page_path.startswith('cases/') and project.get('image'):
            image = project.get('publicImage') or ('assets/' + project['image'].lower() + '.' + project.get('imageFormat', 'webp'))
            if project.get('anonymized') and not project.get('publicImage'):
                raise ValueError('Anonymized case requires a public share image')
            image_url = config['base_url'] + image
            image_alt = project.get('publicImageAlt') or project.get('imageAlt') or name
            for key, value in {'og:image': image_url, 'og:image:alt': image_alt}.items():
                head += '<meta property="' + key + '" content="' + esc(value) + '">\n'
            head += '<meta name="twitter:image" content="' + esc(image_url) + '">\n'
            head += '<meta name="twitter:image:alt" content="' + esc(image_alt) + '">\n'
        person_id, website_id = config['base_url'] + '#eli', config['base_url'] + '#website'
        # Describe the author of this portfolio, never a sole creator of every client system.
        person = {'@type': 'Person', '@id': person_id, 'name': profile['displayName'],
                  'url': page_url(config, 'about.html', lang),
                  'description': profile['intro'], 'jobTitle': profile['role']}
        same_as = list(dict.fromkeys(s['url'] for s in socials))
        if same_as:
            for url in same_as:
                parsed = urlparse(url)
                if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
                    raise ValueError('Invalid existing social profile URL')
            person['sameAs'] = same_as
        if profile.get('email'):
            person['email'] = profile['email']
        graph = [person, {'@type': 'WebSite', '@id': website_id, 'name': 'Eli',
                          'url': config['base_url'], 'inLanguage': ['zh-CN', 'en'],
                          'publisher': {'@id': person_id}}]
        page = {'@type': page_type, '@id': canonical + '#page', 'url': canonical,
                  'name': title, 'description': description, 'inLanguage': lang,
                  'isPartOf': {'@id': website_id}, 'author': {'@id': person_id}}
        if article:
            page.update({'headline': article['title'], 'dateCreated': article['date'],
                         'mainEntityOfPage': canonical})
        if service_page:
            text = service_page[lang]
            identity = canonical + '#service'
            graph.append({'@type': 'Service', '@id': identity, 'name': text['heading'],
                          'description': text['intro'], 'url': canonical,
                          'provider': {'@id': person_id}})
            faq_id = canonical + '#questions'
            graph.append({'@type': 'FAQPage', '@id': faq_id, 'url': faq_id,
                          'inLanguage': lang, 'isPartOf': {'@id': page['@id']},
                          'mainEntity': [
                              {'@type': 'Question', 'name': q,
                               'acceptedAnswer': {'@type': 'Answer', 'text': a}}
                              for q, a in text['faqs']]})
            page['mainEntity'] = {'@id': identity}
            page['hasPart'] = {'@id': faq_id}
        if page_path == 'index.html':
            consultation_id = canonical + '#consultation'
            graph.append({'@type': 'Service', '@id': consultation_id,
                          'name': config['consultation'][lang]['name'],
                          'description': config['consultation'][lang]['description'],
                          'url': page_url(config, 'about.html', lang) + '#contact',
                          'provider': {'@id': person_id}})
            services = []
            for item in config['services']:
                identity = canonical + '#service-' + item['id']
                text = item[lang]
                graph.append({'@type': 'Service', '@id': identity,
                              'name': text['name'], 'serviceType': text['serviceType'],
                              'description': text['description'], 'url': canonical + '#needs',
                              'provider': {'@id': person_id}})
                services.append({'@id': identity})
            page['about'] = [{'@id': consultation_id}] + services
        if page_path == 'about.html':
            page['mainEntity'] = {'@id': person_id}
            faq_id = canonical + '#questions'
            graph.append({'@type': 'FAQPage', '@id': faq_id, 'url': faq_id,
                          'inLanguage': lang, 'isPartOf': {'@id': page['@id']},
                          'mainEntity': [
                              {'@type': 'Question', 'name': item[lang]['question'],
                               'acceptedAnswer': {'@type': 'Answer',
                                                  'text': item[lang]['lead'] + ' ' + item[lang]['answer']}}
                              for item in config['questions']]})
            page['hasPart'] = {'@id': faq_id}
        elif page_path == 'records.html':
            list_id = canonical + '#projects'
            items = [{'@type': 'ListItem', 'position': i,
                      'name': p.get('publicTitle') or p['name'],
                      'url': page_url(config, 'cases/' + p['id'].lower() + '.html', lang)}
                     for i, p in enumerate(prioritize_projects(list(projects.values())), 1)]
            graph.append({'@type': 'ItemList', '@id': list_id, 'numberOfItems': len(items),
                          'itemListElement': items})
            page['mainEntity'] = {'@id': list_id}
        elif page_path.startswith('cases/'):
            breadcrumb_id = canonical + '#breadcrumb'
            graph.append({'@type': 'BreadcrumbList', '@id': breadcrumb_id, 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Projects' if english else '项目库',
                 'item': page_url(config, 'records.html', lang)},
                {'@type': 'ListItem', 'position': 2, 'name': name, 'item': canonical}]})
            page['breadcrumb'] = {'@id': breadcrumb_id}
            page['about'] = {'@type': 'Thing', 'name': name}
        graph.append(page)
        structured = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False)
        # Keep JSON valid and prevent user-controlled strings from closing the script element.
        structured = structured.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        head += '<script type="application/ld+json">' + structured + '</script>'
    return {'title': title, 'description': description, 'robots': robots, 'head': head}


def sitemap(config, paths):
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', ns)
    root = ET.Element('{' + ns + '}urlset')
    # Hreflang is already maintained in HTML. No redundant second implementation needed.
    for path in sorted(paths):
        if path.endswith('404.html'):
            continue
        relative = path[3:] if path.startswith('en/') else path
        if (config['articles']['publication_status'] != 'published'
                and (relative == 'articles.html' or relative.startswith('articles/'))):
            continue
        lang = 'en' if path.startswith('en/') else 'zh-CN'
        relative = path[3:] if lang == 'en' else path
        item = ET.SubElement(root, '{' + ns + '}url')
        ET.SubElement(item, '{' + ns + '}loc').text = page_url(config, relative, lang)
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def ai_context(config):
    """Optional context export from the same visible copy; no private evidence."""
    lines = ['# Eli', '']
    for lang in ('zh-CN', 'en'):
        lines += ['## ' + config['home'][lang]['title'], config['home'][lang]['description'],
                  '', '[' + ('联系与合作' if lang == 'zh-CN' else 'Contact and cooperation')
                  + '](' + page_url(config, 'about.html', lang) + '#contact)', '']
        for service in config['services']:
            text = service[lang]
            lines += ['### ' + text['name'], text['description']]
            lines += ['[' + label + '](' + page_url(config, 'cases/' + pid.lower() + '.html', lang) + ')'
                      for pid, label in zip(service['projects'], text['links'])]
            lines.append('')
        for item in config['questions']:
            text = item[lang]
            lines += ['### ' + text['question'], text['lead'], text['answer'], '']
        for item in config.get('service_pages', []):
            text = item[lang]
            lines += ['### ' + text['heading'], text['intro'],
                      '[' + text['heading'] + ']('
                      + page_url(config, 'services/' + item['slug'] + '.html', lang) + ')', '']
    return '\n'.join(lines)


def write_discovery(root, target, config, output):
    candidate = root / 'evidence/seo-foundation/sitemap-candidate.xml'
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_bytes(sitemap(config, output))
    context_candidate = candidate.with_name('llms-candidate.txt')
    context_candidate.write_text(ai_context(config))
    if config['indexing_enabled']:
        (target / 'sitemap.xml').write_bytes(candidate.read_bytes())
        (target / 'llms.txt').write_text(context_candidate.read_text())
        robots = 'User-agent: *\nAllow: /\nSitemap: ' + config['base_url'] + 'sitemap.xml\n'
    else:
        # Await domain/HTTPS/filing readiness. Do not advertise noindex pages in a live sitemap.
        robots = 'User-agent: *\nDisallow: /\n'
        if (target / 'llms.txt').exists():
            raise ValueError('Existing public AI context while indexing disabled; review required')
        if (target / 'sitemap.xml').exists():
            raise ValueError('Existing live sitemap while indexing disabled; review required')
    (target / 'robots.txt').write_text(robots)
