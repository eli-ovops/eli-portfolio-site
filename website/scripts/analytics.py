"""Baidu analytics markup; no credentials, dependencies or changes to motion."""
import hashlib
import html
import json
import re
from urllib.parse import urljoin, urlsplit


def tag_contact_links(source, page_path):
    """Static unique IDs let the free Tongji element-conversion reports work."""
    counts = {}
    current = 'https://www.eliai.cn/' + page_path
    def tag(match):
        anchor = match[0]
        href = re.search(r'\bhref="([^"]+)"', anchor)
        if not href:
            return anchor
        url = urlsplit(urljoin(current, html.unescape(href[1])))
        action = None
        if url.netloc == 'www.eliai.cn' and url.fragment == 'contact' and re.fullmatch(r'/(?:en/)?about\.html', url.path):
            action = 'entry'
        elif url.scheme == 'mailto':
            action = 'email'
        elif url.scheme == 'tel':
            action = 'phone'
        elif url.scheme == 'https' and url.netloc == 'wa.me':
            action = 'whatsapp'
        elif url.netloc == 'www.eliai.cn' and url.path.endswith('/assets/wechat-qr.png'):
            action = 'wechat'
        if not action:
            return anchor
        counts[action] = counts.get(action, 0) + 1
        if re.search(r'\bid="', anchor):
            raise ValueError('Contact ID already exists; preserve and map it explicitly')
        return anchor[:-1] + f' id="eli-consult-{action}-{counts[action]}" data-analytics-action="{action}">'
    return re.sub(r'<a\b[^>]*>', tag, source)


def markup(root, base='', lang='zh-CN'):
    config = json.loads((root / 'content/analytics.json').read_text())
    if not config['enabled']:
        return '', ''
    if not re.fullmatch(r'[a-f0-9]{32}', config['baidu_site_id']):
        raise ValueError('Baidu site signature must come from the official account')
    if config['canonical_origin'] != 'https://www.eliai.cn':
        raise ValueError('Analytics is restricted to the canonical website')
    english = lang == 'en'
    t = {
        'title': 'Cookie 与访问统计', 'allow': '允许', 'decline': '暂不',
        'notice': '允许我们统计访问情况，帮助改善网站体验。',
        'privacy': '统计与隐私', 'details': '查看说明', 'close': '关闭',
        'copy': '经你同意，本网站使用百度统计分析页面访问、来源及咨询入口点击。服务可能使用 Cookie、IP 地址、浏览器和设备信息及访问记录。自定义事件只记录页面路径、入口位置和联系渠道，不上报站内搜索词、表单内容或联系方式内容。',
        'limits': '点击咨询或联系方式不代表已发送消息、已收到询盘或成交。拒绝不会加载百度统计；你可在这里撤回同意，撤回后页面会刷新并停止后续采集。',
        'provider': '百度统计隐私政策', 'withdraw': '关闭访问统计',
    } if not english else {
        'title': 'Cookies & analytics', 'allow': 'Allow analytics', 'decline': 'Not now',
        'notice': 'Allow visit analytics to help improve this website.',
        'privacy': 'Analytics & privacy', 'details': 'Details', 'close': 'Close',
        'copy': 'With your permission, this site uses Baidu Analytics for page visits, referral sources and consultation clicks. It may use cookies, IP addresses, browser/device information and visit records. Custom events include only the page path, link placement and contact channel, without site search terms, form text or contact details.',
        'limits': 'A contact click does not mean a message, enquiry or sale. Declining keeps Baidu Analytics unloaded. You can withdraw here; the page reloads to stop further collection.',
        'provider': 'Baidu Analytics privacy policy', 'withdraw': 'Turn off analytics',
    }
    esc = html.escape
    tags = []
    for asset, tag in [('assets/site-analytics.css', 'link'), ('assets/site-analytics.js', 'script')]:
        digest = hashlib.sha256((root / asset).read_bytes()).hexdigest()[:12]
        url = esc(base + asset + '?v=' + digest, quote=True)
        tags.append(f'<link rel="stylesheet" href="{url}">' if tag == 'link' else
                    f'<script src="{url}" data-baidu-site="{config["baidu_site_id"]}" data-consent-version="{esc(config["consent_version"])}" defer></script>')
    body = f'''<section class="analytics-notice" id="analytics-notice" aria-label="{t['title']}" hidden>
  <div class="analytics-notice-inner">
    <p>{t['notice']} <button type="button" data-analytics-details>{t['details']}</button></p>
    <div class="analytics-notice-actions"><button class="analytics-allow" type="button" data-analytics-choice="allow">{t['allow']}</button><button type="button" data-analytics-choice="deny">{t['decline']}</button></div>
  </div>
</section>
<dialog class="analytics-dialog" id="analytics-dialog" aria-labelledby="analytics-title">
  <h2 id="analytics-title">{t['privacy']}</h2><p>{t['copy']}</p><p>{t['limits']}</p>
  <p><a href="https://tongji.baidu.com/web/help/article?id=330&amp;type=0" target="_blank" rel="noopener noreferrer">{t['provider']} ↗</a></p>
  <div><button type="button" data-analytics-choice="allow">{t['allow']}</button><button type="button" data-analytics-choice="deny">{t['withdraw']}</button><button type="button" data-analytics-close>{t['close']}</button></div>
</dialog>
<button type="button" class="analytics-privacy" data-analytics-details hidden>{t['privacy']}</button>'''
    return '\n'.join(tags), body
