# HEARTBEAT.md

## Cron Health Check

Check the following cron tasks are running. If any missed their schedule by >2x the interval, report to ice:

| Task | Schedule | Log File |
|------|----------|----------|
| token-sync | hourly | ~/.openclaw/logs/token-sync.log |
| research-director | every 4h | ~/.openclaw/logs/research-director.log |
| lcm-to-qmd-sync | hourly | ~/.openclaw/logs/lcm-sync.log (actual name: lcm-sync.log) |
| soul-guardian | every 30min | ~/.openclaw/logs/soul-guardian.log |

Check method: read last line of each log for timestamp. If stale (>2x interval), report to ice.

## Agent Health Check

### main agent
- Session state: check `~/.openclaw/agents/main/sessions/` for recent activity
- `main` field only describes session activity: `ok` / `idle` / `issue`
- Do not stuff provider/model timeout details into the `main` field

### quantaalpha agent
- Session state: check `~/.openclaw/agents/quantaalpha/sessions/` for recent activity
- Data freshness: latest A股数据更新 log in `~/.openclaw/logs/`
- `quantaalpha` field only describes agent state: `ok` / `stale` / `issue`
- A single embedded timeout or one failed run is not enough to say “needs restart”
- Only say restart is needed if the agent is confirmed stuck or its required data path is not recovering

### daemon
Note: mine_daemon is currently dead (OOM since Apr 3). User has been notified and requested no auto-restart.
- `daemon` in heartbeat output refers ONLY to `mine_daemon`
- Never use proxy / Clash / mihomo / watchdog / random python processes as evidence that `daemon` is alive
- Unless you directly verify a real `mine_daemon` process, report `daemon: dead`

### provider / model health
- Provider/model degradation is a separate note, not part of `main` or `quantaalpha`
- Good note: `provider: minimax timeout spikes observed`
- Bad note: `main: active (LLM timeouts)`

## 自愈检查

读取近期日志，发现问题尝试修复：
- `tail -50 ~/.openclaw/logs/*.log | grep -i "error\|fail"`
- 发现工具失败、API 超时等问题时：诊断根因，能修则修，修完记录，不能修则报告 ice
- 不要把不同数据源混成一句“全挂”。至少分开判断：EIA、interconnection 主队列、interconnection `/data-center`、proxy 本身。
- 如果某一块已修复或直连可用，就不要继续沿用旧告警文案。

## 主动惊喜

问自己：**"现在能做什么让 ice 说'我没要求但很有用'？"**
- 不允许回答"没想到"
- 参考方向：时效性机会、消除瓶颈、他提过一次的事、可以自动化的重复操作
- 默认优先做**小而真的有用**的事，而不是发更多状态汇报
- 有好主意则执行或记录到 `~/.openclaw/workspace/memory/proactive-ideas.md`

### heartbeat 优先级顺序
1. 先做底线巡检（cron / session / proxy /数据源）
2. 发现问题先区分是**旧告警、误报、还是当前真实故障**
3. 能修直接修，修完再决定是否要打扰 ice
4. 如果没有真实故障，默认推进 1 个小优化，例如：
   - 给旧脚本加 freshness guard
   - 修复误报模板
   - 补充 wiki / memory / 文档索引
   - 定位最 stale 的数据链路并修掉
5. 如果没有实质进展，就安静返回 `HEARTBEAT_OK`

## 系统清理

- 检查桌面是否有堆积的截图/临时文件，移到废纸篓
- 不主动关闭 app（避免误操作），只记录异常进程

## Memory Maintenance

1. If today's memory file `memory/YYYY-MM-DD.md` does not exist, create it
2. Append important decisions and experiences from this session
3. Periodically consolidate key learnings into MEMORY.md

## Quick Report

After checks, reply with one line:
`HEARTBEAT_OK | cron: N/N ok | main: ok | quantaalpha: ok/stale/issue | daemon: dead | memory: synced`

If there is a real issue worth surfacing, be specific.
- Bad: `EIA/interconnection all fail`
- Good: `proxy down, but EIA direct fetch OK; interconnection /data-center failing`
- Bad: `main: active (LLM timeouts + context overflow)`
- Good: `main: ok` plus note `provider: timeout spikes observed`
