#!/usr/bin/env python3
import json
import math
import os
import statistics
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path('/Users/ice/.openclaw/workspace')
STATE_DIR = ROOT / 'state' / 'coinglass-monitor'
STATE_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = ROOT / 'state' / 'coinglass-monitor' / 'config.json'
SNAPSHOT_PATH = ROOT / 'state' / 'coinglass-monitor' / 'snapshot.json'
REPORT_PATH = ROOT / 'state' / 'coinglass-monitor' / 'report.md'

DEFAULT_CONFIG = {
    'symbol': 'BTC',
    'price_symbol': 'bitcoin',
    'lookbacks': {'fast': 12, 'medium': 48, 'slow': 168},
    'thresholds': {
        'funding_hot': 0.03,
        'funding_cold': -0.01,
        'oi_1h_strong': 1.5,
        'oi_4h_strong': 4.0,
        'price_1h_strong': 1.2,
        'price_4h_strong': 3.0,
        'liquidation_cluster_near_pct': 1.5,
        'squeeze_bias_ratio': 1.35
    }
}

@dataclass
class MarketSnapshot:
    ts: int
    price: float
    oi: float
    funding: float
    long_liq_24h: float
    short_liq_24h: float
    history_price: List[float]
    history_oi: List[float]
    history_funding: List[float]


def ensure_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2))
        return DEFAULT_CONFIG
    return json.loads(CONFIG_PATH.read_text())


def http_json(url: str, headers: Optional[Dict[str, str]] = None) -> Any:
    req = urllib.request.Request(url, headers=headers or {'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode('utf-8'))


def fetch_price(symbol: str) -> Dict[str, Any]:
    data = http_json(f'https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=usd&days=7&interval=hourly')
    prices = [float(x[1]) for x in data.get('prices', [])]
    return {'current': prices[-1], 'history': prices}


def fetch_binance_oi(symbol: str) -> Dict[str, Any]:
    pair = f'{symbol.upper()}USDT'
    try:
        hist = http_json(f'https://fapi.binance.com/futures/data/openInterestHist?symbol={pair}&period=1h&limit=200')
        vals = [float(x['sumOpenInterestValue']) for x in hist if 'sumOpenInterestValue' in x]
        if vals:
            return {'current': vals[-1], 'history': vals, 'source': 'binance'}
    except Exception:
        pass
    fallback = [1000000000.0 + i * 1000000.0 for i in range(200)]
    return {'current': fallback[-1], 'history': fallback, 'source': 'fallback'}


def fetch_binance_funding(symbol: str) -> Dict[str, Any]:
    pair = f'{symbol.upper()}USDT'
    try:
        hist = http_json(f'https://fapi.binance.com/fapi/v1/fundingRate?symbol={pair}&limit=200')
        vals = [float(x['fundingRate']) * 100 for x in hist if 'fundingRate' in x]
        if vals:
            return {'current': vals[-1], 'history': vals, 'source': 'binance'}
    except Exception:
        pass
    fallback = [0.01 for _ in range(200)]
    return {'current': fallback[-1], 'history': fallback, 'source': 'fallback'}


def fetch_coinglass_liq(symbol: str) -> Dict[str, Any]:
    key = os.environ.get('COINGLASS_API_KEY')
    if not key:
        return {'long': 0.0, 'short': 0.0, 'source': 'missing_api_key'}
    headers = {'CG-API-KEY': key, 'accept': 'application/json'}
    try:
        data = http_json(f'https://open-api-v4.coinglass.com/api/futures/liquidation-chart?symbol={symbol.upper()}', headers=headers)
        body = data.get('data') or {}
        long_v = float(body.get('longVolUsd', 0) or 0)
        short_v = float(body.get('shortVolUsd', 0) or 0)
        return {'long': long_v, 'short': short_v, 'source': 'coinglass'}
    except Exception as e:
        return {'long': 0.0, 'short': 0.0, 'source': f'error:{e.__class__.__name__}'}


def pct_change(series: List[float], n: int) -> float:
    if len(series) <= n:
        return 0.0
    old = series[-1 - n]
    if old == 0:
        return 0.0
    return (series[-1] / old - 1.0) * 100


def zscore(series: List[float], window: int = 50) -> float:
    if len(series) < max(5, window // 2):
        return 0.0
    sample = series[-window:] if len(series) >= window else series
    if len(sample) < 2:
        return 0.0
    mean = statistics.mean(sample)
    stdev = statistics.pstdev(sample)
    if stdev == 0:
        return 0.0
    return (sample[-1] - mean) / stdev


def classify(snapshot: MarketSnapshot, cfg: Dict[str, Any]) -> Dict[str, Any]:
    lb = cfg['lookbacks']
    th = cfg['thresholds']
    p1h = pct_change(snapshot.history_price, lb['fast'])
    p4h = pct_change(snapshot.history_price, lb['medium'])
    oi1h = pct_change(snapshot.history_oi, lb['fast'])
    oi4h = pct_change(snapshot.history_oi, lb['medium'])
    funding = snapshot.funding
    funding_z = zscore(snapshot.history_funding)
    oi_z = zscore(snapshot.history_oi)
    liq_ratio = (snapshot.short_liq_24h + 1.0) / (snapshot.long_liq_24h + 1.0)

    tags = []
    score = {'trend_continuation': 0, 'short_squeeze_risk': 0, 'long_liquidation_risk': 0, 'overheated': 0, 'chop_no_trade': 0}

    if p1h > 0 and oi1h > 0.5:
        score['trend_continuation'] += 2
        tags.append('price_up_oi_up')
    if p4h > th['price_4h_strong'] and oi4h > th['oi_4h_strong']:
        score['trend_continuation'] += 2
        tags.append('strong_4h_expansion')
    if p1h > 0.8 and liq_ratio > th['squeeze_bias_ratio']:
        score['short_squeeze_risk'] += 2
        tags.append('shorts_under_pressure')
    if p1h < -0.8 and liq_ratio < (1 / th['squeeze_bias_ratio']):
        score['long_liquidation_risk'] += 2
        tags.append('longs_under_pressure')
    if funding > th['funding_hot'] and oi_z > 1.0 and abs(p1h) < 0.8:
        score['overheated'] += 3
        tags.append('crowded_long')
    if abs(p1h) < 0.6 and abs(oi1h) < 0.8 and abs(funding_z) < 0.7:
        score['chop_no_trade'] += 2
        tags.append('low_signal')
    if funding < th['funding_cold'] and p1h < 0 and oi1h > 0:
        score['long_liquidation_risk'] += 1
        tags.append('panic_short_term')

    if max(score.values()) <= 0:
        score['chop_no_trade'] = 1
    state = max(score, key=score.get)
    confidence = score[state]
    risk = 'LOW'
    if state in ('short_squeeze_risk', 'long_liquidation_risk', 'overheated') and confidence >= 2:
        risk = 'HIGH'
    elif confidence >= 2:
        risk = 'MEDIUM'

    return {
        'state': state,
        'confidence': confidence,
        'risk': risk,
        'tags': tags,
        'metrics': {
            'price_1h_pct': round(p1h, 2),
            'price_4h_pct': round(p4h, 2),
            'oi_1h_pct': round(oi1h, 2),
            'oi_4h_pct': round(oi4h, 2),
            'funding_pct': round(funding, 4),
            'funding_z': round(funding_z, 2),
            'oi_z': round(oi_z, 2),
            'liq_short_long_ratio': round(liq_ratio, 2),
        }
    }


def build_report(snapshot: MarketSnapshot, verdict: Dict[str, Any]) -> str:
    m = verdict['metrics']
    human_state = {
        'trend_continuation': '趋势延续',
        'short_squeeze_risk': '逼空风险',
        'long_liquidation_risk': '多头清算风险',
        'overheated': '过热拥挤',
        'chop_no_trade': '震荡/不交易'
    }[verdict['state']]
    lines = [
        f'# Crypto Structure Monitor',
        '',
        f'- 时间戳: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(snapshot.ts))}',
        f'- 当前状态: **{human_state}**',
        f'- 风险等级: **{verdict["risk"]}**',
        f'- 置信度: **{verdict["confidence"]}**',
        '',
        '## Snapshot',
        f'- Price: {snapshot.price:,.2f}',
        f'- Open Interest: {snapshot.oi:,.2f}',
        f'- Funding: {snapshot.funding:.4f}%',
        f'- 24h Long Liquidation: {snapshot.long_liq_24h:,.0f} USD',
        f'- 24h Short Liquidation: {snapshot.short_liq_24h:,.0f} USD',
        '',
        '## Structure Metrics',
        f'- Price 1h: {m["price_1h_pct"]}%',
        f'- Price 4h: {m["price_4h_pct"]}%',
        f'- OI 1h: {m["oi_1h_pct"]}%',
        f'- OI 4h: {m["oi_4h_pct"]}%',
        f'- Funding z-score: {m["funding_z"]}',
        f'- OI z-score: {m["oi_z"]}',
        f'- Short/Long liq ratio: {m["liq_short_long_ratio"]}',
        '',
        '## Interpretation',
        f'- Tags: {", ".join(verdict["tags"]) if verdict["tags"] else "none"}',
    ]

    action = {
        'trend_continuation': '顺势看，优先等回踩确认，不追极端拉升。',
        'short_squeeze_risk': '警惕向上加速，别逆势空，等待挤空后再看衰竭。',
        'long_liquidation_risk': '警惕下破触发连锁清算，别急着抄底。',
        'overheated': '拥挤度偏高，减仓/不追高优先。',
        'chop_no_trade': '没有明显 edge，少动或者不交易。'
    }[verdict['state']]
    lines += ['', '## Action Bias', f'- {action}', '']
    return '\n'.join(lines)


def main():
    cfg = ensure_config()
    price = fetch_price(cfg['price_symbol'])
    oi = fetch_binance_oi(cfg['symbol'])
    funding = fetch_binance_funding(cfg['symbol'])
    liq = fetch_coinglass_liq(cfg['symbol'])

    snapshot = MarketSnapshot(
        ts=int(time.time()),
        price=price['current'],
        oi=oi['current'],
        funding=funding['current'],
        long_liq_24h=float(liq['long']),
        short_liq_24h=float(liq['short']),
        history_price=price['history'],
        history_oi=oi['history'],
        history_funding=funding['history'],
    )
    verdict = classify(snapshot, cfg)
    payload = {
        'snapshot': snapshot.__dict__,
        'verdict': verdict,
        'liquidation_source': liq.get('source'),
        'oi_source': oi.get('source'),
        'funding_source': funding.get('source')
    }
    SNAPSHOT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    REPORT_PATH.write_text(build_report(snapshot, verdict), encoding='utf-8')
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
