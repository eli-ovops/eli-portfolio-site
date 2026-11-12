"""Loopback-only diagnostic copy of the accepted public build; no source edits."""
from pathlib import Path
import shutil
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
ROOT = Path(__file__).resolve().parent
SITE = ROOT.parents[1]
FIXTURE = ROOT / 'fixture'
PROBE = '''<script>
window.__pointerProbe=[];
for (const kind of ['pointerdown','pointerup','click','DOMContentLoaded','pageshow']) {
 addEventListener(kind,event=>{
  const target=event.target;
  const selected=document.querySelector('.filters button[aria-pressed="true"]');
  window.__pointerProbe.push({kind,t:performance.now(),target:target?.closest?.('button,a')?.outerHTML.slice(0,300)||target?.nodeName,selected:selected?.textContent,ready:document.readyState,x:event.clientX,y:event.clientY});
 },true);
}
</script>'''
if not FIXTURE.exists():
 shutil.copytree(SITE / 'dist', FIXTURE)
 for page in FIXTURE.rglob('*.html'):
  page.write_text(page.read_text().replace('<head>', '<head>'+PROBE, 1))
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(FIXTURE),**kwargs)
 def end_headers(self):
  self.send_header('Cache-Control','no-store')
  self.send_header('X-Robots-Tag','noindex, nofollow')
  super().end_headers()
print('Pointer diagnostic on http://127.0.0.1:4179; isolated public copy',flush=True)
ThreadingHTTPServer(('127.0.0.1',4179),Handler).serve_forever()
