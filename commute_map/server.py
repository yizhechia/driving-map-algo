"""Local demonstration server. No external routing APIs."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
from urllib.parse import urlsplit
from .app import run, export

STATIC = Path(__file__).parent / "static"

class Handler(BaseHTTPRequestHandler):
    def send(self,status,content,kind="application/json; charset=utf-8"):
        raw = content if isinstance(content,bytes) else json.dumps(content,allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type",kind)
        self.send_header("Content-Length",str(len(raw)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Content-Security-Policy","default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlsplit(self.path).path
        paths = {"/":("index.html","text/html; charset=utf-8"),
                 "/app.js":("app.js","text/javascript; charset=utf-8"),
                 "/style.css":("style.css","text/css; charset=utf-8")}
        if path == "/health":
            self.send(200,{"status":"ok","source":"synthetic"})
        elif path in paths:
            name,kind = paths[path]
            self.send(200,(STATIC/name).read_bytes(),kind)
        elif path == "/favicon.ico":
            self.send(200,b"","image/x-icon")
        else:
            self.send(404,{"error":"Not found"})

    def do_POST(self):
        path = urlsplit(self.path).path
        if path not in ("/api/run","/api/export"):
            self.send(404,{"error":"Not found"})
            return
        try:
            size = int(self.headers.get("Content-Length","0"))
            if size < 1 or size > 8192:
                raise ValueError("Request body must be 1–8192 bytes")
            body = json.loads(self.rfile.read(size))
            result = run(body) if path == "/api/run" else export(body)
        except (ValueError,TypeError,UnicodeDecodeError) as error:
            self.send(400,{"error":str(error)})
            return
        self.send(200,result)

    def log_message(self,fmt,*args):
        pass

def make_server(port=8080):
    return ThreadingHTTPServer(("127.0.0.1",port),Handler)

def serve(port=8080):
    with make_server(port) as server:
        print(f"Commute Lab: http://127.0.0.1:{server.server_port}",flush=True)
        print("Synthetic scenario data. Press Ctrl+C to stop.",flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
