"""SEO metadata and launch-ready sitemap for the existing static portfolio."""
import html
import json
from urllib.parse import urlparse
from xml.etree import ElementTree as ET


def load_config(root):
    config = json.loads((root / 'content/seo.json').read_text())
    parsed = urlparse(config['base_url'])
    if (parsed.scheme not in ('https', 'http') or not parsed.hostname
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or not config['base_url'].endswith('/') or '..' in parsed.path.split('/')):
        raise ValueError('Invalid SEO base_url')
    if not isinstance(config.get('indexing_enabled'), bool):
        raise ValueError('Explicit SEO indexing_enabled boolean required')
    return config


def page_url(config, page_path, lang='zh-CN'):
    prefix = 'en/' if lang == 'en' else ''
    path = '' if page_path == 'index.html' else page_path
    return config['base_url'] + prefix + path


def alternates(config, page_path):
    return {lang: page_url(config, page_path, lang) for lang in ('zh-CN', 'en')}


def metadata(config, profile, projects, page_path, lang):
    english = lang == 'en'
    missing = page_path == '404.html'
    page_type = 'WebPage'
    if page_path.startswith('cases/'):
        project = projects[page_path.rsplit('/', 1)[1].split('.')[0].upper()]
        name = project.get('publicTitle') or project['name']
        title = name + (' | Eli' if english else '｜Eli 项目案例')
        description = project['displaySummary']
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
    esc = lambda text: html.escape(text, quote=True)
    head = ''
    if not missing:
        head = '<link rel="canonical" href="' + esc(canonical) + '">\n'
        pair = alternates(config, page_path)
        for code, url in dict(pair, **{'x-default': pair['zh-CN']}).items():
            head += '<link rel="alternate" hreflang="' + code + '" href="' + esc(url) + '">\n'
        for key, value in {'og:type': 'website', 'og:title': title, 'og:description': description,
                           'og:url': canonical, 'og:site_name': 'Eli',
                           'og:locale': 'en_US' if english else 'zh_CN',
                           'og:locale:alternate': 'zh_CN' if english else 'en_US'}.items():
            head += '<meta property="' + key + '" content="' + esc(value) + '">\n'
        head += '<meta name="twitter:card" content="summary">\n'
        head += '<meta name="twitter:title" content="' + esc(title) + '">\n'
        head += '<meta name="twitter:description" content="' + esc(description) + '">\n'
        person_id, website_id = config['base_url'] + '#eli', config['base_url'] + '#website'
        # Describe the author of this portfolio, never a sole creator of every client system.
        person = {'@type': 'Person', '@id': person_id, 'name': profile['displayName'],
                  'url': page_url(config, 'about.html', lang),
                  'jobTitle': 'Forward Deployed Engineer' if english else '前沿部署工程师',
                  'description': profile['about']}
        if profile.get('email'):
            person['email'] = profile['email']
        graph = [person, {'@type': 'WebSite', '@id': website_id, 'name': 'Eli',
                          'url': config['base_url'], 'publisher': {'@id': person_id}},
                 {'@type': page_type, '@id': canonical + '#page', 'url': canonical,
                  'name': title, 'description': description, 'inLanguage': lang,
                  'isPartOf': {'@id': website_id}, 'author': {'@id': person_id}}]
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
        lang = 'en' if path.startswith('en/') else 'zh-CN'
        relative = path[3:] if lang == 'en' else path
        item = ET.SubElement(root, '{' + ns + '}url')
        ET.SubElement(item, '{' + ns + '}loc').text = page_url(config, relative, lang)
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def write_discovery(root, target, config, output):
    candidate = root / 'evidence/seo-foundation/sitemap-candidate.xml'
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_bytes(sitemap(config, output))
    if config['indexing_enabled']:
        (target / 'sitemap.xml').write_bytes(candidate.read_bytes())
        robots = 'User-agent: *\nAllow: /\nSitemap: ' + config['base_url'] + 'sitemap.xml\n'
    else:
        # Await domain/HTTPS/filing readiness. Do not advertise noindex pages in a live sitemap.
        robots = 'User-agent: *\nDisallow: /\n'
        if (target / 'sitemap.xml').exists():
            raise ValueError('Existing live sitemap while indexing disabled; review required')
    (target / 'robots.txt').write_text(robots)
