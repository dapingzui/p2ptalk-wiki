---
type: concept
subject: 挖矿必然有Mempool
category: atom
tags: [atom, p2ptalk, 挖矿, mempool, 算力, 信用评分]
related:
  - [[atom/Atom与Mempool]]
  - [[consensus/hashcash与POW]]
created: 2026-04-20
---

# 挖矿必然有Mempool

## 核心推测

initsysctrl 的推测：

> "只要系统存在挖矿机制，那么就必然存在内存池。如果系统不存在挖矿机制……"

## 推理链

1. **Bitcoin 需要 mempool 的原因**：进入共识的数据需要满足"额外条件"（如工作量证明）
2. **内存池的作用**：作为"中继"，等待验证和打包
3. **类比 Atom**：如果 Atom 需要某种"证明"才能参与共识，那么也需要 mempool

## 信用评分的算力证明

> "信用评分是否需要附带算力证明才能进入 memepool？类似 memepool 的 1 sat 每字节定价来防止女巫。"

信用评分进入共识的方式：
- 方式 A：附带算力证明 → 需要 mempool
- 方式 B：无需算力证明 → 可能不需要 mempool

## 对 Atom 系统的意义

如果 initsysctrl 的推测正确：
- Atom 系统如果存在挖矿机制 → 必然存在 mempool
- Atom 系统如果没有挖矿机制 → 可能不需要 mempool

## 开放问题

- Atom 系统需要挖矿机制吗？
- 如果 Atom 不需要挖矿，是否还需要 mempool？

---

## 相关概念

- [[atom/Atom与Mempool]]
