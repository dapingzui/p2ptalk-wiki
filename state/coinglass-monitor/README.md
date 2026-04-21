# CoinGlass / Crypto Structure Monitor

这是一个可直接跑的最小可用系统，不需要你先确认。

## 目标
- 自动抓取 BTC 价格、Binance OI、Binance funding
- 如果配置了 `COINGLASS_API_KEY`，额外抓取清算数据
- 输出结构状态：
  - trend_continuation
  - short_squeeze_risk
  - long_liquidation_risk
  - overheated
  - chop_no_trade
- 生成两份文件：
  - `snapshot.json`
  - `report.md`

## 文件
- 脚本: `scripts/coinglass_state_monitor.py`
- 配置: `state/coinglass-monitor/config.json`
- 输出: `state/coinglass-monitor/report.md`

## 运行
```bash
python3 scripts/coinglass_state_monitor.py
```

## 如果你有 CoinGlass API key
```bash
export COINGLASS_API_KEY=你的key
python3 scripts/coinglass_state_monitor.py
```

## 当前版本设计原则
- 先做 state engine，不做自动下单
- 先保证早上起床能看到结构结论
- 能在没有 CoinGlass key 的情况下退化运行

## 下一步可以加的东西
- Telegram 定时推送
- 多币种轮询（ETH/SOL/BTC）
- 清算热力图距离计算
- orderbook L2
- dashboard
