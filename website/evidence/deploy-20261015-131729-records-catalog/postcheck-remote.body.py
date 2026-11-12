assert public.resolve()==target and hashes(target)==expected
assert hashes(Path(manifest['previous']))==manifest['previous_files'],'Previous release changed'
assert hashlib.sha256(config.read_bytes()).hexdigest()==manifest['nginx_sha256']
services={s:subprocess.run(['systemctl','is-active','--quiet',s]).returncode==0 for s in ['nginx','erp-trial','mysql','redis-server']}
assert all(services.values())
print(json.dumps({'status':'REMOTE_POSTCHECK_PASS','release':release,'files_verified':len(expected),'previous_files_preserved':len(manifest['previous_files']),'nginx_config':'UNCHANGED','services':services,'indexing':'DISABLED'}))
