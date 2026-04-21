---
type: concept
subject: AI与女巫攻击
category: ai
tags: [atom, p2ptalk, AI, agent, 女巫, Sybil]
related:
  - [[ai/AI与生产关系]]
  - [[security/女巫攻击防护]]
  - [[consensus/hashcash与POW]]
created: 2026-04-20
---

# AI与女巫攻击

## AI Agent 的女巫问题

> "首要问题类似女巫攻击，我怎么知道某个 agent 是可信靠谱的？"

AI agent 的特殊性：
- 可以快速复制
- 能力难以验证
- 恶意 agent 可以伪装成多个可信 agent

## leilei 的三个问题

> "1. 信用评分是否需要附带算力证明才能进入 memepool？（类似 memepool 的 1 sat 每字节定价来防止女巫）
> 2. 当来自同一个节点的两个相反的信用评分进入 memepool，选择哪个？（如何应对双花？）
> 3. memepool 因为有……"

## Bitcoin 的解法

> "比特币的共识是在解决女巫问题后出现的。"
> — **leilei**

POW：创建节点需要真实算力，51% 攻击成本巨大。

## AI Agent 的解法

1. **BTC 质押**：作恶需要锁定 BTC 作保证金
2. **谓词验证**：通过谓词验证 agent 能力真实性

---

## 相关概念

- [[ai/AI与生产关系]]
- [[security/女巫攻击防护]]
