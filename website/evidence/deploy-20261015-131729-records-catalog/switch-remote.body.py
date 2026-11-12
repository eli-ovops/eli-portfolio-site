assert public.is_symlink() and str(public.resolve())==manifest['previous'],'Current release changed; no switch'
assert hashlib.sha256(config.read_bytes()).hexdigest()==manifest['nginx_sha256'],'Config changed; no switch'
assert hashes(target)==expected,'Prepared release differs; no switch'
assert hashes(Path(manifest['previous']))==manifest['previous_files'],'Previous release changed'
assert (backup/'previous-release.json').is_file()
for service in ['nginx','erp-trial','mysql','redis-server']:
 assert subprocess.run(['systemctl','is-active','--quiet',service]).returncode==0,service
for name in expected:
 if name.endswith('.html'):assert b'<meta name="robots" content="noindex,nofollow">' in (target/name).read_bytes()
link=root/('public.next.'+release);assert not link.exists() and not link.is_symlink()
os.symlink(str(target),link);os.replace(link,public)
assert public.resolve()==target
print(json.dumps({'status':'SWITCHED','release':release,'previous':manifest['previous'],'target':str(target),'files_verified':len(expected),'indexing':'DISABLED','switched_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
