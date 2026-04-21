# Crypto Structure Monitor Web

## 启动
```bash
python3 quantalpha/crypto-monitor/server.py
```

打开：
- http://127.0.0.1:8765

## 功能
- 网页展示当前结构状态
- 一键刷新数据
- 读取 `state/coinglass-monitor` 的 snapshot/report
- 调用 `scripts/coinglass_state_monitor.py` 重新计算

## 说明
- 当前是最小可用网页产品
- 后续可以继续接 CoinGlass key、多币种、图表、登录、Telegram 推送
