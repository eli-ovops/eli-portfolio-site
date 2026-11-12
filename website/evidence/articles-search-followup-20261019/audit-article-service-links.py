"""Read-only content-to-service link audit; writes only its evidence receipt."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
from urllib.request import urlopen, Request
from datetime import datetime, timezone, timedelta
from collections import Counter
import xml.etree.ElementTree as ET
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.links = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            classes = set(' '.join(x[1] for x in self.stack).split())
            self.current = dict(href=attrs.get('href', ''), label='',
                                inside_main=any(x[0] == 'main' for x in self.stack),
                                inside_service_slot='article-service' in classes,
                                inside_contact='case-contact' in classes,
                                inside_case_evidence='article-case-links' in classes)
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                       'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append((tag, attrs.get('class', '')))

    def handle_endtag(self, tag):
        if tag == 'a' and self.current is not None:
            self.current['label'] = ' '.join(self.current['label'].split())
            self.links.append(self.current)
            self.current = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, text):
        if self.current is not None:
            self.current['label'] += text


def inspect(raw, url):
    parser = Links()
    parser.feed(raw.decode('utf-8'))
    rows = []
    for a in parser.links:
        target = urlsplit(urljoin(url, a['href']))
        if target.hostname != 'www.eliai.cn':
            continue
        a = dict(a, path=target.path, fragment=target.fragment)
        if a['inside_main'] and (a['inside_service_slot'] or a['inside_contact'] or a['inside_case_evidence']):
            a['target_exists_in_local_output'] = (ROOT / 'dist' / target.path.lstrip('/')).is_file()
            rows.append(a)
    return rows


def main():
    urls = [x.text for x in ET.parse(ROOT / 'dist/sitemap.xml').getroot().findall('{*}url/{*}loc')]
    urls = [u for u in urls if '/articles/' in u and u.endswith('.html')]
    assert len(urls) == 204
    local = []
    for url in urls:
        p = ROOT / 'dist' / urlsplit(url).path.lstrip('/')
        raw = p.read_bytes()
        links = inspect(raw, url)
        service = [a for a in links if a['inside_service_slot']]
        contact = [a for a in links if a['inside_contact']]
        assert len(service) == 1 and len(contact) == 1, url
        assert all(a['target_exists_in_local_output'] for a in links), url
        lang = 'en' if '/en/' in url else 'zh-CN'
        assert service[0]['path'].startswith('/en/services/' if lang == 'en' else '/services/')
        assert contact[0]['path'] == ('/en/about.html' if lang == 'en' else '/about.html')
        assert contact[0]['fragment'] == 'contact'
        local.append(dict(url=url, language=lang, sha256=hashlib.sha256(raw).hexdigest(), links=links))
    counts = {}
    for lang in ['zh-CN', 'en']:
        counts[lang] = dict(Counter(a['path'] for row in local if row['language'] == lang
                                   for a in row['links'] if a['inside_service_slot']))
    public = []
    for slug in ['ai-inventory-exceptions', 'ai-knowledge-base-start', 'rag-explained']:
        for prefix in ['', 'en/']:
            url = 'https://www.eliai.cn/' + prefix + 'articles/' + slug + '.html'
            try:
                with urlopen(Request(url, headers={'User-Agent': 'Eli-read-only-link-audit/1.0'}), timeout=20) as response:
                    raw = response.read()
                    status = response.status
                    final_url = response.url
                path = OUT / ('article-service-live-' + ('en-' if prefix else 'zh-') + slug + '.html')
                path.write_bytes(raw)
                expected = next(x for x in local if x['url'] == url)
                public.append(dict(url=url, status=status, final_url=final_url,
                                   sha256=hashlib.sha256(raw).hexdigest(),
                                   matches_local_hash=hashlib.sha256(raw).hexdigest() == expected['sha256'],
                                   links=inspect(raw, final_url), evidence=path.name))
            except Exception as exc:
                public.append(dict(url=url, status='UNKNOWN', error=type(exc).__name__ + ': ' + str(exc)))
                # Do not retry a failed public read or infer the whole site is down.
    result = dict(checked_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
                  local_article_details=204, bilingual_topics=102,
                  analysis_scope='Main content service slot, contact section and case evidence links; excludes global header/footer.',
                  destination_counts_by_language=counts, rows=local, public_samples=public,
                  source_evidence=['scripts/tutorials.py: service hardcoded to fde-consulting for 100 tutorials',
                                   'templates/article.html: article-service slot', 'content/articles.json', 'content/articles-en.json'],
                  limits=['Full 204-page graph is from current local output, not 204 new online fetches.',
                          'Public sample agreement does not independently verify every unsampled online page.',
                          'A generic service link is a relevance opportunity, not a broken link or proven ranking/conversion failure.',
                          'Does not test visual/mobile behavior or measure visitor traffic.'],
                  website_changes=0, builds=0, deployments=0, search_submissions=0, active_model_queries=0)
    out = OUT / 'article-service-link-audit.json'
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(receipt=str(out), local_article_details=204, destinations=counts,
                          public_samples=[{k:r[k] for k in ['url','status','matches_local_hash'] if k in r} for r in public]), ensure_ascii=False))


if __name__ == '__main__':
    main()
