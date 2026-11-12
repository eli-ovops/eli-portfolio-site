"""Read-only origin inspection. No raw visitor IPs, queries, or referers emitted."""
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit
import datetime
import hashlib
import json
import re

START = datetime.datetime(2026, 10, 19, 5, 30, tzinfo=datetime.timezone.utc)
END = datetime.datetime(2026, 10, 19, 5, 45, tzinfo=datetime.timezone.utc)
TARGET = '/services/fde-consulting.html'
RX = re.compile(r'^(\S+) \S+ \S+ \[([^\]]+)\] "([A-Z]+) ([^ ]+) [^" ]+" (\d+) (\S+) "[^"]*" "([^"]*)"')
groups = {}
events = []
today = Counter()
files = []
ua_claims = Counter()
for p in [Path('/var/log/nginx/access.log'), Path('/var/log/nginx/access.log.1')]:
    if not p.exists():
        continue
    files.append({'name': p.name, 'bytes': p.stat().st_size})
    for line in p.open(errors='replace'):
        m = RX.match(line)
        if not m:
            continue
        ip, when, method, url, status, size, ua = m.groups()
        if not when.startswith('19/Oct/2026:'):
            continue
        path = urlsplit(url).path
        tm = datetime.datetime.strptime(when, '%d/%b/%Y:%H:%M:%S %z').astimezone(datetime.timezone.utc)
        if re.search(r'360|qihoo|qihu|nami|namiso', ua, re.I):
            ua_claims[(path, status)] += 1
        if path != TARGET:
            continue
        today[status] += 1
        if START <= tm <= END:
            if ip not in groups:
                groups[ip] = len(groups) + 1
            ua = re.sub(r'[\w.+-]+@[\w.-]+', '[email redacted]', ua)
            events.append({'utc': tm.isoformat(), 'method': method, 'status': status,
                           'bytes': size, 'user_agent': ua[:500], 'source_group': groups[ip]})
errors = Counter()
ep = Path('/var/log/nginx/error.log')
if ep.exists():
    for line in ep.open(errors='replace'):
        m = re.match(r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})', line)
        if not m:
            continue
        tm = datetime.datetime.strptime(m[1], '%Y/%m/%d %H:%M:%S').astimezone(datetime.timezone.utc)
        if not START <= tm <= END:
            continue
        if TARGET in line:
            errors['target_path_mentioned'] += 1
        if 'eliai.cn' in line:
            errors['host_mentioned'] += 1
        if 'SSL' in line or 'handshake' in line:
            errors['global_tls_errors_unattributed'] += 1
cp = Path('/etc/nginx/sites-available/portfolio-domain-pending')
cfg = cp.read_text()
global_configs = []
for p in [Path('/etc/nginx/nginx.conf'), *Path('/etc/nginx/conf.d').glob('*.conf')]:
    txt = p.read_text(errors='replace')
    global_configs.append({'file': str(p), 'restriction_directives': sorted(set(re.findall(
        r'^\s*(deny|auth_basic|limit_req|limit_conn|geo|map)\s', txt, re.M))),
        'log_format_contains_host': bool(re.search(r'log_format[^;]*\$host', txt, re.S))})
print(json.dumps({'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'read_only': True, 'window_utc': [START.isoformat(), END.isoformat()],
    'logs': files, 'target': TARGET, 'today_target_status_counts': dict(today),
    'window_target_requests': events, 'source_group_note': 'Ephemeral equality groups only; not identities',
    'claimed_nami_or_360_ua_today': [{'path': k[0], 'status': k[1], 'count': v} for k, v in ua_claims.items()],
    'bot_identity_verified': False, 'error_log_window_counts': dict(errors),
    'error_time_interpretation': 'Server local timezone converted to UTC',
    'site_directives_present': {k: bool(re.search(r'^\s*' + re.escape(k) + r'\s', cfg, re.M))
        for k in ['deny', 'allow', 'auth_basic', 'limit_req', 'limit_conn', 'if', 'proxy_pass', 'access_log', 'error_log']},
    'site_config_sha256': hashlib.sha256(cfg.encode()).hexdigest(),
    'global_configs': global_configs,
    'current_release': str(Path('/srv/eli-sites/portfolio/domain-current').resolve()),
    'limitations': 'Combined access logs omit host and Range; no official Nami IP/UA verification found.'
}, ensure_ascii=False, indent=2))
