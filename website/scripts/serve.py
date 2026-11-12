from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parent.parent/'dist'
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
 def list_directory(self,path): self.send_error(404);return None
 def do_GET(self):
  if any(part.startswith('.') for part in self.path.split('/')): self.send_error(404);return
  return super().do_GET()
 def send_error(self,code,message=None,explain=None):
  if code==404:
   data=(ROOT/'404.html').read_bytes(); self.send_response(404);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  else: super().send_error(code,message,explain)
 def end_headers(self):
  self.send_header('Cache-Control','no-store');self.send_header('X-Robots-Tag','noindex, nofollow');self.send_header('X-Content-Type-Options','nosniff');super().end_headers()
parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=4178);args=parser.parse_args()
print(f'Internal preview: http://127.0.0.1:{args.port} (dist only)',flush=True)
ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
