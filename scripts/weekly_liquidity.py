#!/usr/bin/env python3
import json, re, sys, urllib.request
from datetime import datetime

UA={"User-Agent":"Mozilla/5.0"}

def get_json(url, timeout=12):
    req=urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8','replace'))

def get_text(url, timeout=12):
    req=urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8','replace')

def yf_change(sym):
    url=f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=7d&interval=1d"
    d=get_json(url)
    r=d['chart']['result'][0]
    closes=[x for x in r['indicators']['quote'][0]['close'] if x is not None]
    if len(closes)<2: return None
    return (closes[-1]/closes[0]-1)*100

def light(v, good=None, red=None):
    if red and red(v): return '🔴'
    if good and good(v): return '🟢'
    return '🟡'

lines=[]
red=False
try:
    rr=get_json('https://markets.newyorkfed.org/api/rp/reverserepo/propositions/search.json')
    rows=rr.get('repo',{}).get('operations',[]) or rr.get('operations',[]) or rr.get('data',[])
    vals=[]
    for row in rows:
        val=row.get('totalAmtAccepted') or row.get('amt') or row.get('total_amount_accepted')
        date=row.get('operationDate') or row.get('date')
        if val is None: continue
        vals.append((date,float(str(val).replace(',',''))))
    vals=vals[-5:]
    latest=vals[-1][1] if vals else None
    delta=latest-vals[0][1] if len(vals)>1 else 0
    # NY Fed unit usually millions USD
    latest_b=latest/1e9 if latest else latest
    delta_b=delta/1e9
    rr_red=latest_b is not None and latest_b>=50
    red |= rr_red
    lines.append(f"RRP: {latest_b:.1f}B ({delta_b:+.1f}B/w) {'🔴' if rr_red else '🟢' if latest_b<5 else '🟡'}")
except Exception as e:
    lines.append(f"RRP: 数据暂缺 🟡")

try:
    h=get_text('https://www.federalreserve.gov/releases/h41/current/')
    # H.4.1 is HTML-heavy. Parse the row window after the first "Total assets" label.
    idx=h.lower().find('total assets')
    win=h[idx:idx+3500] if idx >= 0 else h
    clean=re.sub(r'<[^>]+>', ' ', win)
    clean=clean.replace('&#xa0;', ' ').replace('&nbsp;', ' ')
    nums=[int(x.replace(',','')) for x in re.findall(r'(?<![\d,])\d{1,3}(?:,\d{3}){2,}(?![\d,])', clean)]
    # First large number after Total assets is current total assets, in millions USD.
    total=next((n for n in nums if n > 1_000_000), None)
    # The following signed figures are weekly and yearly changes, also in millions USD.
    changes=[]
    for sign, num in re.findall(r'([+-])\s*(\d{1,3}(?:,\d{3})*)', clean):
        v=int(num.replace(',','')) * (1 if sign == '+' else -1)
        if abs(v) >= 100:
            changes.append(v)
    weekly=changes[0] if changes else None
    fed_red=weekly is not None and weekly < -30000
    red |= fed_red
    if total:
        suffix=f" ({weekly/1000:+.1f}B/w)" if weekly is not None else ""
        lines.append(f"Fed资产负债表: {total/1e6:.2f}T{suffix} {'🔴' if fed_red else '🟡'}")
    else:
        lines.append("Fed资产负债表: 数据暂缺 🟡")
except Exception:
    lines.append("Fed资产负债表: 数据暂缺 🟡")

try:
    cs={s:yf_change(s) for s in ['LQD','HYG','JNK']}
    credit_red=all(v is not None and v<-1 for v in cs.values())
    red |= credit_red
    lines.append('信用ETF: ' + ', '.join(f"{k} {v:+.1f}%" if v is not None else f"{k} NA" for k,v in cs.items()) + (' 🔴' if credit_red else '🟡'))
except Exception:
    lines.append("信用ETF: 数据暂缺 🟡")

try:
    uup=yf_change('UUP'); shy=yf_change('SHY'); tlt=yf_change('TLT')
    uup_red=uup is not None and uup>1.5
    red |= uup_red
    lines.append(f"美元/久期: UUP {uup:+.1f}%, SHY {shy:+.1f}%, TLT {tlt:+.1f}% {'🔴' if uup_red else '🟡'}")
except Exception:
    lines.append("美元/久期: 数据暂缺 🟡")

summary='流动性环境：恶化' if red else '流动性环境：持平/温和'
print(('⚠️ ' if red else '') + '周度流动性监控')
print('\n'.join(lines[:4]))
print(summary)
