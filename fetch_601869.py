import urllib.request, json
url = 'https://query1.finance.yahoo.com/v8/finance/chart/601869.SS?interval=5m&range=1d'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as r:
    d = json.loads(r.read())
result = d['chart']['result'][0]
quotes = result['indicators']['quote'][0]
timestamps = result['timestamp']
opens = quotes['open']; closes = quotes['close']; vols = quotes['volume']
highs = quotes['high']; lows = quotes['low']

high = max([h for h in highs if h is not None])
low = min([l for l in lows if l is not None and l > 0])
close = closes[-1]
open_ = opens[0]
vol = sum([v for v in vols if v is not None])
price_chg = (close - open_) / open_ * 100

import datetime
ts = timestamps[-1]
dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone(datetime.timedelta(hours=8)))
print(f'长飞光纤 601869.SS')
print(f'时间: {dt.strftime("%H:%M")}')
print(f'开盘: {open_:.2f}')
print(f'最高: {high:.2f}')
print(f'最低: {low:.2f}')
print(f'收盘: {close:.2f}')
print(f'涨跌: {price_chg:+.2f}%')
print(f'成交量: {vol:,.0f}')
print(f'持仓成本: 277.00')
print(f'盈亏: {(close-277)/277*100:+.1f}%')
