"""Check metadata-only changes and the lastmod ledger's failure modes."""
import argparse
import hashlib
import json
import re
import tempfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
from page_updates import fingerprint, prepare_updates
from seo import load_config


class Head(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.meta = {}
        self.links = []
        self.json_data = []
        self.in_json = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta':
            self.meta[a.get('name') or a.get('property')] = a.get('content')
        if tag == 'link':
            self.links.append(a)
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self.in_json = True

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_json = False

    def handle_data(self, data):
        if self.in_json:
            self.json_data.append(json.loads(data))


def ledger_checks():
    with tempfile.TemporaryDirectory(prefix='eli-lastmod-check-') as folder:
        root = Path(folder)
        (root / 'content').mkdir()
        output = {'one.html': '<p>one</p>', 'two.html': '<p>two</p>'}
        rows = {p: {'lastmod': '2026-10-17', 'content_sha256': fingerprint(s)}
                for p, s in output.items()}
        ledger = root / 'content/page-updates.json'
        ledger.write_text(json.dumps({'pages': rows}))
        before = ledger.read_bytes()
        prepare_updates(root, output)
        assert ledger.read_bytes() == before
        prepare_updates(root, output, '2026-10-18')
        assert ledger.read_bytes() == before, 'Explicit date alone must not refresh dates'
        changed = dict(output, **{'one.html': '<p>one updated</p>'})
        try:
            prepare_updates(root, changed)
            raise AssertionError('Unreviewed content change was accepted')
        except ValueError:
            assert ledger.read_bytes() == before
        recorded = prepare_updates(root, changed, '2026-10-18')
        assert recorded['one.html']['lastmod'] == '2026-10-18'
        assert recorded['two.html']['lastmod'] == '2026-10-17'
        for invalid in ('not-a-date', '2026-02-30', '2026-10-16'):
            try:
                prepare_updates(root, output, invalid)
                raise AssertionError('Invalid or regressing date was accepted')
            except ValueError:
                pass
        prepare_updates(root, dict(changed, **{'404.html': '<p>not found</p>'}))
        assert '404.html' not in json.loads(ledger.read_text())['pages']
        template = '<meta name="portfolio-revision" content="{rev}"><a href="x.html?project=p02&amp;pv={rev}#work">case</a>'
        assert fingerprint(template.format(rev='a'*20)) == fingerprint(template.format(rev='b'*20))
        assert fingerprint(template.format(rev='a'*20)) != fingerprint(template.format(rev='a'*20).replace('project=p02', 'project=p03'))
    return 'PASS: rebuild stability, explicit review, one-page updates, invalid/backdated dates, 404 exclusion and preserved navigation state'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    config = load_config(root)
    expected = {}
    for key, prefix in (('articles', ''), ('en', 'en/')):
        for a in config['articles'][key]:
            expected[prefix + 'articles/' + a['slug'] + '.html'] = a['search_description']
    assert len(expected) == 204
    descriptions = []
    body_checks = []
    for old in sorted(args.baseline.rglob('*.html')):
        path = old.relative_to(args.baseline).as_posix()
        previous, current = old.read_text(), (root / 'dist' / path).read_text()
        body = lambda s: re.search(r'<body\b.*</body>', s, re.S).group(0)
        assert fingerprint(body(previous)) == fingerprint(body(current)), path + ': visible HTML changed'
        a, b = Head(previous.split('</head>', 1)[0]), Head(current.split('</head>', 1)[0])
        assert a.links == b.links, path + ': canonical or hreflang changed'
        if path in expected:
            for field in ('description', 'og:description', 'twitter:description'):
                assert b.meta[field] == expected[path], (path, field)
            article = next(v for data in b.json_data for v in data['@graph'] if v.get('@type') == 'Article')
            assert article['description'] == expected[path]
            descriptions.append(expected[path])
            if path.startswith('en/'):
                assert not re.search('[\u4e00-\u9fff]', expected[path]), path
        else:
            assert a.meta.get('description') == b.meta.get('description'), path
        body_checks.append(path)
    assert len(body_checks) == 296
    assert len(descriptions) == len(set(descriptions)) == 204
    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    xml = ET.fromstring((root / 'dist/sitemap.xml').read_bytes())
    dates = {}
    rows = json.loads((root / 'content/page-updates.json').read_text())['pages']
    for node in xml.findall(ns + 'url'):
        url = node.findtext(ns + 'loc')
        path = urlsplit(url).path.lstrip('/')
        if not path or path.endswith('/'):
            path += 'index.html'
        value = node.findtext(ns + 'lastmod')
        assert value == rows[path]['lastmod']
        assert fingerprint((root / 'dist' / path).read_text()) == rows[path]['content_sha256']
        dates[url] = value
    assert len(dates) == 294
    protected = json.loads((args.baseline.parent.parent / 'baseline.json').read_text())['protected']
    for path, digest in protected.items():
        assert hashlib.sha256((root / path).read_bytes()).hexdigest() == digest, path
    result = {'status': 'PASS', 'article_descriptions_checked': len(descriptions),
              'unchanged_visible_bodies': len(body_checks), 'sitemap_urls_with_verified_dates': len(dates),
              'lastmod_distribution': dict(Counter(dates.values())),
              'protected_css_js_sources': len(protected), 'behavior_checks': ledger_checks()}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
