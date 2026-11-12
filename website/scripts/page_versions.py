"""Keep build revisions on assets and diagnostics, never on public page navigation."""
import hashlib
import html
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit, urljoin

PLACEHOLDER = '__PORTFOLIO_REVISION__'


def canonical_home_links(source, page_path):
    """Use the published homepage canonicals without losing query or fragment."""
    origin = 'https://www.eliai.cn'

    def link(match):
        value = html.unescape(match[2])
        original = urlsplit(value)
        # In-page controls must remain fragment-only for existing motion handlers.
        if not original.path:
            return match[0]
        resolved = urlsplit(urljoin(origin + '/' + page_path, value))
        if resolved.scheme != 'https' or resolved.netloc != 'www.eliai.cn':
            return match[0]
        homes = {'/index.html': '/', '/en/index.html': '/en/'}
        if resolved.path not in homes:
            return match[0]
        href = urlunsplit((original.scheme, original.netloc, homes[resolved.path],
                           original.query, original.fragment))
        return match[1] + html.escape(href, quote=True) + match[3]

    return re.sub(r'(<a\b[^>]*\bhref=")([^"]*)(")', link, source)


def version_pages(root, output, assets):
    digest = hashlib.sha256()
    for path, source in sorted(output.items()):
        digest.update(path.encode() + b'\0' + source.encode() + b'\0')
    for path in sorted(set(assets) | {'styles.css', 'motion.css', 'app.js', 'motion.js'}):
        digest.update(path.encode() + b'\0' + (root / path).read_bytes() + b'\0')
    revision = digest.hexdigest()[:20]

    def link(match):
        url = urlsplit(html.unescape(match[2]))
        if url.scheme or url.netloc or not url.path.endswith('.html'):
            return match[0]
        query = [(key, value) for key, value in parse_qsl(url.query, keep_blank_values=True) if key != 'pv']
        href = urlunsplit(('', '', url.path, urlencode(query), url.fragment))
        return match[1] + html.escape(href, quote=True) + match[3]

    for path, source in output.items():
        assert source.count(PLACEHOLDER) == 1, path
        source = source.replace(PLACEHOLDER, revision)
        output[path] = re.sub(r'(<a\b[^>]*\bhref=")([^"]*)(")', link, source)
    return revision
