from pathlib import Path
import os,json,shutil,hashlib,subprocess,urllib.request
base=Path('/srv/eli-sites/portfolio'); prepared=base/'domain-releases/domain-prepared-20261007'; live=base/'domain-releases/domain-http-20261007'
assert (base/'domain-current').resolve()==prepared and not live.exists()
assert (base/'public').resolve()==base/'releases/20261007-144516'
erp=Path('/etc/nginx/sites-available/erp-trial');erp_hash=hashlib.sha256(erp.read_bytes()).hexdigest()
for p in prepared.rglob('*'):assert not p.is_symlink()
shutil.copytree(prepared,live)
for p in live.rglob('*.html'):
 text=p.read_text();body=text.split('<body>',1)[1]
 text=text.replace('https://www.eliai.cn/','http://www.eliai.cn/')
 assert text.split('<body>',1)[1]==body and 'content="noindex,nofollow"' in text
 p.write_text(text)
conf=Path('/etc/nginx/sites-available/portfolio-domain-pending');original=conf.read_bytes();backup=base/'domain-http-config-before.conf';assert not backup.exists();backup.write_bytes(original)
link=Path('/etc/nginx/sites-enabled/portfolio-domain-pending');assert not link.exists()
text='''server {
    listen 80;
    server_name eliai.cn;
    return 301 http://www.eliai.cn$request_uri;
}
server {
    listen 80;
    server_name www.eliai.cn;
    root /srv/eli-sites/portfolio/domain-current;
    index index.html;
    autoindex off;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Robots-Tag "noindex, nofollow" always;
    location = /index.html { return 301 /$is_args$args; }
    location = /en/index.html { return 301 /en/$is_args$args; }
    location / { try_files $uri $uri/ =404; }
    location ~ /\\. { deny all; }
    error_page 404 /404.html;
}
'''
conf.write_text(text);os.symlink(str(conf),str(link))
result=subprocess.run(['nginx','-t'],capture_output=True,text=True);print(result.stderr)
if result.returncode:
 conf.write_bytes(original);link.unlink();raise RuntimeError('Validation failed; own config restored; no reload')
os.symlink(str(live),str(base/'domain-next'));os.replace(base/'domain-next',base/'domain-current')
subprocess.run(['systemctl','reload','nginx'],check=True)
for path in ['/','/en/','/cases/p36.html','/en/cases/p36.html']:
 request=urllib.request.Request('http://127.0.0.1'+path,headers={'Host':'www.eliai.cn'})
 with urllib.request.urlopen(request) as response:
  data=response.read().decode();assert response.status==200 and 'content="noindex,nofollow"' in data
  assert 'http://www.eliai.cn/' in data
assert hashlib.sha256(erp.read_bytes()).hexdigest()==erp_hash
receipt={'domain':'www.eliai.cn','domain_root':str(live),'HTTP_vhost':'enabled and server-internal pages verified','HTTPS':'not configured','filing':'not completed; user requests deployment before filing','ERP_config':'unchanged','old_IP_release':'20261007-144516','prior_domain_root':str(prepared),'backup':str(backup)}
(base/'domain-http-20261007.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
