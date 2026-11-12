from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit,unquote
import tarfile,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OLD=ROOT/'evidence/deploy-seo-geo-20261012/portfolio-20261012-143006-seo-geo.tar.gz'
assert hashlib.sha256(OLD.read_bytes()).hexdigest()=='46239f282c235d9bc994d4946af21a9bab0905add9aea7f5853314229eaa094f'
with tarfile.open(OLD) as archive:
 old={m.name:archive.extractfile(m).read() for m in archive.getmembers() if m.isreg()}
allowed=set(old)|{'assets/page-version.js'}
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  parsed=urlsplit(self.path);relative=unquote(parsed.path).lstrip('/') or 'index.html'
  if relative not in allowed or any(part.startswith('.') or part=='..' for part in Path(relative).parts):self.send_error(404);return
  phase=(HERE/'fixture-phase.txt').read_text().strip()
  data=old[relative] if phase=='old' else (ROOT/'dist'/relative).read_bytes()
  mime={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'application/javascript','.json':'application/json','.png':'image/png','.webp':'image/webp','.svg':'image/svg+xml','.ttf':'font/ttf'}.get(Path(relative).suffix,'application/octet-stream')
  self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)))
  self.send_header('Cache-Control','public, max-age=3600');self.send_header('X-Robots-Tag','noindex, nofollow');self.end_headers();self.wfile.write(data)
 def log_message(self,*args):pass
print('Controlled warm-cache fixture on http://127.0.0.1:4179; actual accepted old/current portfolio output only',flush=True)
ThreadingHTTPServer(('127.0.0.1',4179),Handler).serve_forever()
