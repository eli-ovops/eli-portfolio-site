from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
D=Path(__file__).resolve().parent/'public'
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(D),**kwargs)
 def list_directory(self,path):self.send_error(404)
 def end_headers(self):self.send_header('X-Robots-Tag','noindex, nofollow');self.send_header('Cache-Control','no-store');super().end_headers()
ThreadingHTTPServer(('127.0.0.1',4186),Handler).serve_forever()
