---
type: concept
subject: Mempool不是唯一业务来源
category: atom
tags: [atom, p2ptalk, mempool, 业务来源, Bitcoin]
related:
  - [[atom/Atom与Mempool]]
  - [[atom/CUser与CReview数据结构]]
created: 2026-04-20
---

# Mempool不是唯一业务来源

## 核心洞察

> "mempool 并不是比特币系统中唯一的业务来源。"
> — **沄涣**

## Bitcoin 的两种业务通道

| 通道 | 说明 |
|---|---|
| mempool | 交易中继，通过交易进入共识 |
| 其他通道 | 不经过 mempool 的业务 |

## Atom 的业务逻辑

> "atom 则围绕 CUser / CReview 等非交易对象，实现链下的业务与声誉逻辑。"

Atom 的业务：
- 不需要经过 mempool
- 围绕用户和评论对象
- 实现链下业务

## 对 Atom 设计的意义

如果 mempool 不是唯一的业务来源，那么：
- Atom 可以独立于 Bitcoin 的 mempool 运行
- Atom 可以有自己的业务逻辑
- Atom 不需要"进入" Bitcoin 的共识机制

## 问题

- Atom 的业务通过什么通道？
- Atom 如何保证业务的一致性？
- Atom 的"业务"和"共识"是什么关系？

---

## 相关概念

- [[atom/Atom与Mempool]]
- [[atom/CUser与CReview数据结构]]
