from pathlib import Path
import os,subprocess,json,hashlib,urllib.request,socket,ssl,datetime,shutil
root=Path('/srv/eli-sites/portfolio');conf=Path('/etc/nginx/sites-available/portfolio-domain-pending');erp=Path('/etc/nginx/sites-available/erp-trial')
def sha(b):return hashlib.sha256(b).hexdigest()
def cmd(args):
 p=subprocess.run(args,capture_output=True,text=True);assert p.returncode==0,(args,p.stderr[-1000:]);return p.stdout.strip()
B={'config_before_sha': '63e0b3c4d3853108cac6d9396d158ced9c3704fdd932af3069501ca17cfd6398', 'erp_sha': 'f8feed3d72ef606d90674a633f73a9449a31a874197e823130ed9b3b9d213445', 'public': '/srv/eli-sites/portfolio/releases/20261015-165606-icp-footer', 'domain': '/srv/eli-sites/portfolio/domain-releases/20261015-165606-icp-footer', 'certbot': 'certbot 1.21.0', 'backup': '/srv/eli-sites/portfolio/backups/https-index-20261015', 'bootstrap_sha': 'affbceef3878890496055913f2a825635b0785c0c73cce97a15da8f5137a8a7b', 'challenge_checks': [{'host': 'eliai.cn', 'status': 200}, {'host': 'www.eliai.cn', 'status': 200}], 'nginx_test': 'nginx: the configuration file /etc/nginx/nginx.conf syntax is ok\nnginx: configuration file /etc/nginx/nginx.conf test is successful'}
CONFIG='# Prepared only; not installed. Certificate must exist and be verified first.\nserver {\n    listen 80;\n    server_name eliai.cn www.eliai.cn;\n    location ^~ /.well-known/acme-challenge/ {\n        root /srv/eli-sites/portfolio/acme;\n        default_type text/plain;\n        try_files $uri =404;\n    }\n    location / { return 301 https://www.eliai.cn$request_uri; }\n}\nserver {\n    listen 443 ssl;\n    server_name eliai.cn;\n    ssl_certificate /etc/letsencrypt/live/www.eliai.cn/fullchain.pem;\n    ssl_certificate_key /etc/letsencrypt/live/www.eliai.cn/privkey.pem;\n    ssl_protocols TLSv1.2 TLSv1.3;\n    return 301 https://www.eliai.cn$request_uri;\n}\nserver {\n    listen 443 ssl;\n    server_name www.eliai.cn;\n    ssl_certificate /etc/letsencrypt/live/www.eliai.cn/fullchain.pem;\n    ssl_certificate_key /etc/letsencrypt/live/www.eliai.cn/privkey.pem;\n    ssl_protocols TLSv1.2 TLSv1.3;\n    root /srv/eli-sites/portfolio/domain-current;\n    index index.html;\n    autoindex off;\n    add_header X-Content-Type-Options nosniff always;\n    add_header X-Robots-Tag "noindex, nofollow" always;\n    location / { try_files $uri $uri/ =404; }\n    location ~ /\\. { deny all; }\n    error_page 404 /404.html;\n}\n'
HOOK='#!/bin/sh\nset -eu\n[ "${RENEWED_LINEAGE:-}" = /etc/letsencrypt/live/www.eliai.cn ] || exit 0\n/usr/sbin/nginx -t\n/bin/systemctl reload nginx\n'

assert sha(conf.read_bytes()) in [B['bootstrap_sha'],sha(CONFIG.encode())] and sha(erp.read_bytes())==B['erp_sha']
assert str((root/'domain-current').resolve())==B['domain']
cert=Path('/etc/letsencrypt/live/www.eliai.cn/fullchain.pem');assert cert.is_file()
assert subprocess.run(['openssl','x509','-checkend','86400','-noout','-in',str(cert)],capture_output=True).returncode==0
before=conf.read_bytes();conf.write_text(CONFIG)
p=subprocess.run(['nginx','-t'],capture_output=True,text=True)
if p.returncode:conf.write_bytes(before);raise RuntimeError(p.stderr)
cmd(['systemctl','reload','nginx'])
ctx=ssl.create_default_context();result=[]
for host in ['eliai.cn','www.eliai.cn']:
 with socket.create_connection(('127.0.0.1',443),timeout=8) as sock:
  with ctx.wrap_socket(sock,server_hostname=host) as conn:
   result.append({'host':host,'TLS':conn.version(),'expires':conn.getpeercert()['notAfter']})
renew=Path('/etc/letsencrypt/renewal-hooks/deploy/eli-portfolio-reload');assert not renew.exists() or renew.read_text()==HOOK;renew.write_text(HOOK);os.chmod(renew,0o700)
cmd(['systemctl','enable','--now','certbot.timer'])
assert sha(erp.read_bytes())==B['erp_sha']
print(json.dumps({'status':'HTTPS_ENABLED_NOINDEX_PENDING_VERIFICATION','config_sha':sha(conf.read_bytes()),'certificate_validation':result,'renew_hook':str(renew),'timer':cmd(['systemctl','is-active','certbot.timer']),'nginx_test':p.stderr.strip()}))
