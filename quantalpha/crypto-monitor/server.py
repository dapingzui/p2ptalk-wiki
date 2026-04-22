#!/usr/bin/env python3
import json
import subprocess
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

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
INTERVAL_MAP = {'1m': '1m', '5m': '5m', '15m': '15m', '1h': '1h'}


def http_json(url: str):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode('utf-8'))


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, content_type='text/plain; charset=utf-8'):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self._send(code, data, MIME['.json'])

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == '/' or path == '/index.html':
            return self._send(200, (APP_DIR / 'index.html').read_bytes(), MIME['.html'])
        if path == '/styles.css':
            return self._send(200, (APP_DIR / 'styles.css').read_bytes(), MIME['.css'])
        if path == '/app.js':
            return self._send(200, (APP_DIR / 'app.js').read_bytes(), MIME['.js'])
        if path == '/api/snapshot':
            return self._send(200, (STATE_DIR / 'snapshot.json').read_bytes(), MIME['.json'])
        if path == '/api/report':
            return self._send(200, (STATE_DIR / 'report.md').read_bytes(), MIME['.md'])
        if path == '/api/candles':
            qs = parse_qs(parsed.query)
            interval = INTERVAL_MAP.get(qs.get('interval', ['5m'])[0], '5m')
            symbol = (qs.get('symbol', ['BTCUSDT'])[0]).upper()
            try:
                url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=300'
                raw = http_json(url)
                candles = [
                    {
                        'time': int(x[0] / 1000),
                        'open': float(x[1]),
                        'high': float(x[2]),
                        'low': float(x[3]),
                        'close': float(x[4]),
                        'volume': float(x[5]),
                    }
                    for x in raw
                ]
                return self._json({'candles': candles, 'interval': interval, 'symbol': symbol})
            except Exception as e:
                return self._json({'candles': [], 'interval': interval, 'symbol': symbol, 'error': str(e)}, 500)
        if path == '/api/depth':
            qs = parse_qs(parsed.query)
            symbol = (qs.get('symbol', ['BTCUSDT'])[0]).upper()
            try:
                data = http_json(f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit=20')
                bids = [{'price': float(p), 'qty': float(q)} for p, q in data.get('bids', [])]
                asks = [{'price': float(p), 'qty': float(q)} for p, q in data.get('asks', [])]
                bid_sum = sum(x['qty'] for x in bids)
                ask_sum = sum(x['qty'] for x in asks)
                return self._json({'symbol': symbol, 'bids': bids, 'asks': asks, 'bid_sum': bid_sum, 'ask_sum': ask_sum, 'imbalance': bid_sum - ask_sum})
            except Exception as e:
                return self._json({'symbol': symbol, 'bids': [], 'asks': [], 'error': str(e)}, 500)
        if path == '/api/market':
            qs = parse_qs(parsed.query)
            symbol = (qs.get('symbol', ['bitcoin'])[0]).lower()
            try:
                data = http_json(f'https://api.coingecko.com/api/v3/coins/{urllib.parse.quote(symbol)}')
                md = data.get('market_data', {})
                out = {
                    'symbol': symbol,
                    'market_cap': md.get('market_cap', {}).get('usd'),
                    'volume_24h': md.get('total_volume', {}).get('usd'),
                    'high_24h': md.get('high_24h', {}).get('usd'),
                    'low_24h': md.get('low_24h', {}).get('usd'),
                    'price_change_24h': md.get('price_change_percentage_24h'),
                    'ath_change_pct': md.get('ath_change_percentage', {}).get('usd') if isinstance(md.get('ath_change_percentage'), dict) else None,
                }
                return self._json(out)
            except Exception as e:
                return self._json({'symbol': symbol, 'error': str(e)}, 500)
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
