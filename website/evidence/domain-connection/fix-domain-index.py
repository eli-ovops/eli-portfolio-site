from pathlib import Path
import subprocess,urllib.request,json,hashlib
base=Path('/srv/eli-sites/portfolio');conf=Path('/etc/nginx/sites-available/portfolio-domain-pending');s=conf.read_text()
for line in ['    location = /index.html { return 301 /$is_args$args; }\n','    location = /en/index.html { return 301 /en/$is_args$args; }\n']:
 assert line in s;s=s.replace(line,'')
(base/'domain-index-redirect-before.conf').write_text(conf.read_text());conf.write_text(s)
subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
print('Index aliases now served normally; canonical still uses directory URL')
