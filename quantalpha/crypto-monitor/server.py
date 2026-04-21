#!/usr/bin/env python3
import json
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path('/Users/ice/.openclaw/workspace')
APP_DIR = ROOT / 'quantalpha' / 'crypto-monitor'
STATE_DIR = ROOT / 'state' / 'coinglass-monitor'
SCRIPT = ROOT / 'scripts' / 'coinglass_state_monitor.py'

MIME = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.md': 'text/plain; charset=utf-8',
}

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, content_type='text/plain; charset=utf-8'):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/' or path == '/index.html':
            data = (APP_DIR / 'index.html').read_bytes()
            return self._send(200, data, MIME['.html'])
        if path == '/styles.css':
            data = (APP_DIR / 'styles.css').read_bytes()
            return self._send(200, data, MIME['.css'])
        if path == '/app.js':
            data = (APP_DIR / 'app.js').read_bytes()
            return self._send(200, data, MIME['.js'])
        if path == '/api/snapshot':
            data = (STATE_DIR / 'snapshot.json').read_bytes()
            return self._send(200, data, MIME['.json'])
        if path == '/api/report':
            data = (STATE_DIR / 'report.md').read_bytes()
            return self._send(200, data, MIME['.md'])
        return self._send(404, b'Not found')

    def do_POST(self):
        path = urlparse(self.path).path
        if path == '/api/refresh':
            proc = subprocess.run(['python3', str(SCRIPT)], cwd=str(ROOT), capture_output=True)
            if proc.returncode != 0:
                return self._send(500, proc.stderr or b'refresh failed')
            return self._send(200, b'{"ok":true}', MIME['.json'])
        return self._send(404, b'Not found')

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8765), Handler)
    print('listening on http://0.0.0.0:8765')
    print('open from LAN via http://<your-mac-lan-ip>:8765')
    server.serve_forever()
