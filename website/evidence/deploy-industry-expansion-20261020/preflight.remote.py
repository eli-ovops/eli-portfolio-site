from pathlib import Path
import hashlib,json,shutil,subprocess
root=Path('/srv/eli-sites/portfolio'); current=root/'domain-current'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
actual={p.relative_to(current).as_posix():sha(p) for p in current.rglob('*') if p.is_file()}
assert not any(p.is_symlink() for p in current.rglob('*'))
configs={p:sha(Path(p)) for p in ['/etc/nginx/sites-available/portfolio-domain-pending','/etc/nginx/sites-available/erp-trial']}
print(json.dumps({'previous':str(current.resolve()),'files':actual,'configs':configs,'ip_public':str((root/'public').resolve()),'hostname':subprocess.check_output(['hostname'],text=True).strip(),'services':{s:subprocess.check_output(['systemctl','is-active',s],text=True).strip() for s in ['nginx','erp-trial','mysql','redis-server']},'free_bytes':shutil.disk_usage(root).free}))
