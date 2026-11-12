from pathlib import Path
import os
r=Path('/srv/eli-sites/portfolio');current=r/'domain-current'
assert str(current.resolve())=='/srv/eli-sites/portfolio/domain-releases/20261015-200719-center-about'
p=r/'domain-current.rollback.20261015-200719-center-about'
assert not p.exists() and not p.is_symlink()
os.symlink('/srv/eli-sites/portfolio/domain-releases/20261015-183949-https-index',p);os.replace(p,current)
print(current.resolve())
