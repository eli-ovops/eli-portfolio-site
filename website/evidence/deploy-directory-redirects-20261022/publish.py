"""Apply the approved five exact Nginx routes with drift checks and backup."""
import base64
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
before = json.loads((HERE / 'preflight.json').read_text())
candidate = (HERE / 'nginx-candidate.conf').read_bytes()
remote_input = {
    'expected': before['config_sha256'],
    'release': before['release'],
    'hashes': before['hashes'],
    'enabled_config_hashes': before['enabled_config_hashes'],
    'services': before['services'],
    'addition': '    location = /articles/ { return 301 /articles.html; }\n    location = /en/articles/ { return 301 /en/articles.html; }\n    location = /en/cases/ { return 301 /en/records.html; }\n    location = /services/ { return 301 "/index.html#needs"; }\n    location = /en/services/ { return 301 "/en/index.html#needs"; }\n',
    'candidate': base64.b64encode(candidate).decode(),
}
remote = r'''
import base64, hashlib, json, os, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path
x = json.loads(INPUT)
conf = Path('/etc/nginx/sites-available/portfolio-domain-pending')
root = Path('/srv/eli-sites/portfolio/domain-current')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
public_hashes = lambda: {str(p.relative_to(root)): sha(p) for p in root.rglob('*') if p.is_file()}
assert sha(conf) == x['expected'], 'Configuration changed since preflight; stop'
assert str(root.resolve()) == x['release'], 'Release changed since preflight; stop'
assert public_hashes() == x['hashes'], 'Public files changed since preflight; stop'
for u, expected_state in x['services'].items():
    assert subprocess.check_output(['systemctl', 'show', u, '--property=ActiveState,MainPID'], text=True).strip() == expected_state, 'Service state drift; stop'
for p, h in x['enabled_config_hashes'].items():
    assert sha(Path(p)) == h, 'Enabled configuration drift; stop'
old = conf.read_bytes()
new = base64.b64decode(x['candidate'])
needle = b'    location / { try_files $uri $uri/ =404; }'
addition = x['addition'].encode()
assert old.count(needle) == 1 and new == old.replace(needle, addition + needle)
assert b'autoindex off;' in new and new.count(b'location = /cases/') == 1
backup = Path('/srv/eli-sites/portfolio/backups/20261022-directory-redirects')
backup.mkdir(mode=0o700, exist_ok=False)
backup_conf = backup / 'portfolio-domain-pending.before.conf'
shutil.copy2(conf, backup_conf)
assert sha(backup_conf) == x['expected']
result = {'started_at': datetime.now(timezone.utc).isoformat(), 'backup': str(backup_conf),
          'old_sha256': x['expected'], 'new_sha256': hashlib.sha256(new).hexdigest(),
          'public_files_count': len(x['hashes']), 'nginx_reload_count': 0, 'rollback': False}
temp = conf.with_name(conf.name + '.directory-redirects-20261022.tmp')
assert not temp.exists(), 'Unexpected staging file; stop'
try:
    with temp.open('xb') as f:
        f.write(new)
        f.flush()
        os.fsync(f.fileno())
    shutil.copystat(conf, temp)
    os.replace(temp, conf)
    test = subprocess.run(['nginx', '-t'], text=True, capture_output=True)
    result['nginx_test'] = {'returncode': test.returncode, 'stderr': test.stderr}
    if test.returncode:
        raise RuntimeError('Nginx syntax validation failed')
    reload = subprocess.run(['systemctl', 'reload', 'nginx'], text=True, capture_output=True)
    result['reload'] = {'returncode': reload.returncode, 'stderr': reload.stderr}
    result['nginx_reload_count'] = 1
    if reload.returncode:
        raise RuntimeError('Nginx reload failed')
    result['services'] = {u: subprocess.check_output(
        ['systemctl', 'show', u, '--property=ActiveState,MainPID'], text=True).strip()
        for u in ['nginx', 'erp-trial', 'mysql', 'redis-server']}
    assert result['services'] == x['services'], 'Service state or PID changed'
    result['service_states_unchanged'] = True
    assert public_hashes() == x['hashes'], 'Public file hashes differ'
    assert str(root.resolve()) == x['release']
    assert sha(conf) == result['new_sha256']
    result['other_configs_unchanged'] = all(
        sha(Path(p)) == h for p, h in x['enabled_config_hashes'].items()
        if Path(p).resolve() != conf)
    assert result['other_configs_unchanged']
    result['public_files_unchanged'] = True
    result['status'] = 'APPLIED_AND_NGINX_RELOADED'
except Exception as exc:
    result['error'] = str(exc)
    if sha(conf) == hashlib.sha256(new).hexdigest():
        restore = conf.with_name(conf.name + '.directory-restore-20261022.tmp')
        assert not restore.exists()
        shutil.copy2(backup_conf, restore)
        os.replace(restore, conf)
        check = subprocess.run(['nginx', '-t'], text=True, capture_output=True)
        if check.returncode == 0 and result['nginx_reload_count']:
            subprocess.run(['systemctl', 'reload', 'nginx'], check=True)
        result['rollback'] = True
        result['status'] = 'FAILED_CONFIG_RESTORED'
    else:
        result['status'] = 'FAILED_EXTERNAL_CONFIG_DRIFT_REQUIRES_REVIEW'
finally:
    result['finished_at'] = datetime.now(timezone.utc).isoformat()
    (backup / 'publish-result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
'''.replace('INPUT', repr(json.dumps(remote_input)))

args = ['ssh', '-F', '/dev/null', '-i', '/Users/USER/.ssh/erp-jdcloud-trial-20261005',
        '-o', 'IdentityAgent=none', '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes',
        '-o', 'StrictHostKeyChecking=yes', '-o',
        'UserKnownHostsFile=/Users/USER/.codex/servers/jdcloud-[REDACTED_HOST]/known_hosts',
        '-o', 'ForwardAgent=no', '-o', 'ConnectTimeout=10', '-o', 'ServerAliveInterval=15',
        '-o', 'ServerAliveCountMax=2', '-o',
        'ProxyCommand=python3 /Users/USER/.codex/servers/jdcloud-[REDACTED_HOST]/tcp-transport.py',
        'root@[REDACTED_HOST]', 'python3 -']
(HERE / 'remote-apply-reviewed.py').write_text(remote)
r = subprocess.run(args, input=remote, text=True, capture_output=True, timeout=60)
(HERE / 'publish-transport.json').write_text(json.dumps({
    'checked_at': datetime.now(timezone.utc).isoformat(), 'returncode': r.returncode,
    'stderr': r.stderr}, indent=2) + '\n')
if r.stdout:
    (HERE / 'publish-result.json').write_text(r.stdout)
print(r.stdout or r.stderr)
raise SystemExit(r.returncode)
