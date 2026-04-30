# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Default save paths for data types
- Anything environment-specific

## 🌐 Inkwell

- API key env: `~/.openclaw/workspace/.env.inkwell`
- Python client: `~/.openclaw/workspace/scripts/inkwell_fetch.py`
- Shell wrapper: `~/.openclaw/workspace/scripts/inkwell.sh`
- Daily helper: `~/.openclaw/workspace/scripts/inkwell_daily.sh`
- 用法示例：
  - `source ~/.openclaw/workspace/.env.inkwell && python3 ~/.openclaw/workspace/scripts/inkwell_fetch.py home`
  - `~/.openclaw/workspace/scripts/inkwell.sh articles --search "AI infra" --limit 5`
  - `~/.openclaw/workspace/scripts/inkwell.sh bookmark-add ARTICLE_ID --note "why saved"`

## 📎 文档发送规则

**当 ice 说：**“文档发我” / “发我文件” / “直接发 md”

**默认动作：**
1. 优先发送 **真正的附件文件**，不要把正文直接贴到聊天里
2. 如果原文件不在 message 工具允许目录下，先复制到 `~/.openclaw/workspace/outbox/`
3. 再用 `message` 发送该附件
4. 除非 ice 明确要求贴正文，否则不要发长文本内容流

**outbox 目录：** `~/.openclaw/workspace/outbox/`

**转录文件规则：**
- 所有转录产物（`.md` / `.txt`）完成后，同步复制一份到 `~/.openclaw/workspace/outbox/`
- 对于分段转录，优先额外产出一个 `*_full.md` 合并版，发送时默认优先发合并版

## 📥 微信文章保存路径

**判断逻辑**：URL 包含 `mp.weixin.qq.com` 或 `weixin.qq.com/s/`

**默认保存目录**: `~/Document/QuantaAlpha/data/wechat_articles/`

抓取微信文章后，保存到该目录，文件名格式：`作者_文章标题_日期.md`

## 🎙️ 播客转录规则

**适用平台**：小宇宙 FM（xiaoyuzhoufm.com）

**处理流程**：
1. 用 browser 打开播客页面，执行 `evaluate` JS 获取 `document.querySelector('audio').src`
2. 下载音频到 `~/Document/QuantaAlpha/data/podcasts/`
3. 调本地服务 `bash scripts/podcast-transcriber.sh`（使用 mlx Qwen3-ASR 模型）
4. 转录结果保存到 `~/Document/QuantaAlpha/data/podcasts/transcripts/`
5. 后台运行，不阻塞主 session；完成后发 Telegram

**判断逻辑**：URL 包含 `xiaoyuzhoufm.com/episode/`

**依赖**：
- whisper 需 venv：`~/.venv-whisper`
- 模型：`base`（中文识别效果好的最小模型）
- 音频格式：m4a 下载后直接可用

## 📚 API Docs — chub

**Context Hub CLI** — 获取最新 LLM 优化的第三方 API 文档，避免幻觉。

```bash
chub search "openai"              # 搜索可用文档
chub get openai/chat --lang py    # 获取 Python 文档
chub get anthropic/claude-api --lang js  # 获取 JS 文档
chub annotate stripe/api "webhook 需要 raw body" # 保存发现的坑
```

**规则：写调用外部 API/SDK 的代码之前，先 `chub search` 确认有没有文档，有就 `chub get` 取来读。**

可用文档：`chub search`（无参数列出所有 20 条）

---

## 📈 Market Data - Alpha Vantage

**重要：使用MCP访问，不要直接调用API**

- **MCP服务器**: alpha-vantage-mcp
- **优势**: 无限流、更快速、更稳定
- **获取方式**: 通过MCP tools直接访问
- **注意**: ❌ 不要用requests直接调用Alpha Vantage API

---

## 🌐 复杂网站抓取策略

**遇到 SPA / 政府网站 / session 依赖页面时：**

❌ 不要：headless Playwright + 逆向 API + 猜参数
✅ 直接：让真实浏览器去操作

### 方法优先级
1. **Brave DevTools 抓包** — 打开网页，F12 → Network，手动操作一次，复制 request 参数
2. **Playwright 连接已运行浏览器** — `--remote-debugging-port=9222` 启动后连进去
3. **通过主框架导航** — SPA 子页面要先加载主入口（如 index.do），再用框架函数跳转，不能直接加载子页面 URL
4. **curl/Python 直调** — 只在接口简单且无 session 依赖时用

### 经验教训（韩国 tradedata.go.kr）
- `openETS0100019Q.do` 是 iframe 片段，没有 `<head>`，直接加载缺 jQuery
- 主入口 `index.do` → `ets_f_prccMenuLoad()` → 子页面才是正确流程
- RuntimeException 根因：tradeKind 为空（radioTypePc 没在 DOM 里）
- 教训：先用浏览器手动操作抓包，3分钟搞定；别硬啃 JS 源码

## 🔍 Web Search

**⚠️ 默认搜索：本地 SearXNG（优先于 web_search 工具）**

**SearXNG** - 本地开源搜索引擎，**始终优先使用**
- 地址: `http://127.0.0.1:8888`
- 健康检查: `curl -fsS 'http://127.0.0.1:8888/search?q=test&format=json' | head`
- 使用: `curl -s "http://127.0.0.1:8888/search?q=查询内容&format=json"`
- **规则: 搜索时先用本地 SearXNG，不要先用 web_search（Brave API 未配置）**
- 支持 JSON 输出，结果包含 title/url/content 字段
- 可配合 web_fetch 或 curl 抓取具体页面内容
- 当前实现: 本机 LaunchAgent `com.user.searxng-local`，不再依赖 Colima/SSH tunnel

## 🚀 OpenClaw 项目配置

### Workspace 结构
- 主目录: `~/.openclaw/workspace`
- 配置: `openclaw.json`（在 ~/.openclaw）
- Agent 配置: `~/.openclaw/agents/main/`
- 日志: `~/.openclaw/logs/gateway.log`

### 关键命令
```bash
# 检查配置
jq . ~/.openclaw/openclaw.json

# 验证配置有效性
openclaw doctor --fix

# 查看网关日志
tail -f ~/.openclaw/logs/gateway.log

# 强制重启网关
pkill -9 -f "openclaw.*gateway"
```

### 常见问题排查
- 配置无效 → `openclaw doctor --fix`
- Telegram 无法连接 → 检查 `channels.telegram` 配置
- Agent 无响应 → 查看 `gateway.log`，检查模型是否在线

### 默认配置
- **默认模型**: `zai/glm-5`（GLM-5）
- **本地模型**: 通过 OMLX（localhost:8000）
- **Telegram 账号**: `default`（已配置）
- **Discord**: 已启用

---

## 🇺🇸 EIA API (美国能源信息署)

- **API Key:** `qWxyqSk18H4GliGcZQ00NqMUXdUo4AYpYETsDrdn`
- **Base URL:** `https://api.eia.gov/v2/`
- **用途:** 美国电网需求、天然气价格、ERCOT燃料结构、核电停机、德州分区/分行业用电
- **数据目录:** `~/Document/QuantaAlpha/data/grid_demand/`
- **抓取脚本:** `~/Document/QuantaAlpha/scripts/grid_demand_fetch.py`（6个数据源）
- **注意:** 不要再问 ice 要这个 key

---

## 🇯🇵 e-stat API (日本政府统计)

- **AppId:** `530f76dab1e568789262cc0a69ab208a0a79cf6f`
- **Base URL:** `https://api.e-stat.go.jp/rest/3.0/app/json/`
- **用途:** 日本海关贸易统计（statsCode: 00350300），9位HS码月度数据
- **注意:** 不要再问 ice 要这个 key

---

## 📋 信息查询策略

**所有研究/分析任务默认遵循 `SOURCE_POLICY.md`**
- 来源分级：一级（学术/权威媒体）> 二级（专业文章）> 禁止（社交媒体/Wiki/博客）
- 强制交叉验证：每个结论至少 2 个独立来源
- 时效性：时间相关数据必须三路径验证
- 黑名单严格执行：社交媒体、Wiki、未经同行评审的材料一律排除

---

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.



## 🎙️ 播客转录排队规则

**同时只能跑一个转录任务。**

当有多个待处理时：
1. 先记录所有任务
2. 串行执行（一个完成再下一个）
3. 防止并发压垮 MLX 模型或被系统 SIGKILL

**判断逻辑**：URL 包含 `xiaoyuzhoufm.com/episode/` 或 `youtube.com/watch` 或 `youtu.be/`

**已有任务列表（需完成）：**
1. 小宇宙134 - 谢晨「数据的综述」(3段转录中)
2. YouTube - Why Scientists Can't Rebuild a Polaroid Camera (2段转录中)
