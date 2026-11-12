"""Explicit, content-based sitemap dates; ordinary builds never touch the ledger."""
import hashlib
import html
import json
import re
from datetime import date
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def fingerprint(source):
    # A cache revision is not a content update. Keep every other byte, including
    # descriptions, article text, navigation links and structured data.
    source = re.sub(r'(<meta name="portfolio-revision" content=")[^"]*(")',
                    r'\1__CONTENT_REVISION__\2', source)

    # This shared navigation controller's cache hash is not page content either.
    source = re.sub(r'(src="[^"?]*assets/page-version\.js)\?v=[a-f0-9]{12}(")',
                    r'\1?v=__ASSET_REVISION__\2', source)

    def clean_link(match):
        url = urlsplit(html.unescape(match[2]))
        if url.scheme or url.netloc or not url.path.endswith('.html'):
            return match[0]
        query = [(k, v) for k, v in parse_qsl(url.query, keep_blank_values=True) if k != 'pv']
        value = urlunsplit(('', '', url.path, urlencode(query), url.fragment))
        return match[1] + html.escape(value, quote=True) + match[3]

    source = re.sub(r'(<a\b[^>]*\bhref=")([^"]*)(")', clean_link, source)
    return hashlib.sha256(source.encode('utf-8')).hexdigest()


def prepare_updates(root, output, record_date=None):
    ledger_path = root / 'content/page-updates.json'
    ledger = json.loads(ledger_path.read_text())
    rows = ledger['pages']
    if record_date is not None:
        date.fromisoformat(record_date)
    changed = []
    # Exclude 404s just as the sitemap does. Validate all rows before writing.
    proposed = {}
    for path, source in sorted(output.items()):
        if path.endswith('404.html'):
            continue
        previous = rows.get(path, {})
        digest = fingerprint(source)
        if previous.get('content_sha256') == digest:
            date.fromisoformat(previous['lastmod'])
            proposed[path] = previous
            continue
        if record_date is None:
            changed.append(path)
            continue
        if previous.get('lastmod', '') > record_date:
            raise ValueError('Cannot backdate a changed page: ' + path)
        proposed[path] = {'lastmod': record_date, 'content_sha256': digest}
        changed.append(path)
    if changed and record_date is None:
        raise ValueError('Content dates need review for %d pages. After reviewing changes, '
                         'build with --record-lastmod YYYY-MM-DD. First page: %s'
                         % (len(changed), changed[0]))
    # Retain historical rows for removed pages; only emitted routes enter the sitemap.
    if changed:
        rows.update(proposed)
        ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n')
    return proposed
