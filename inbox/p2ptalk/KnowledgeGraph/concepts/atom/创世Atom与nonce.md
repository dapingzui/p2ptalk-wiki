---
type: concept
subject: 创世Atom与nonce
category: atom
tags: [atom, p2ptalk, 创世, Genesis, nonce]
related:
  - [[consensus/hashcash与POW]]
  - [[atom/Atom数据结构]]
created: 2026-04-20
---

# 创世Atom与nonce

## 创世 Atom

创世 Atom = Atom 系统的起点，类似 Bitcoin 的 Genesis Block。

## nonce 在 Atom 中的角色

nonce 在 Atom 系统中的作用：
1. **标识符**：作为 atom 的唯一标识
2. **难度证明**：满足 hashcash 格式的要求
3. **同步媒介**：通过 nonce 广播建立会议连贯性

## 上下两个 nonce 的衔接

叶鹏提出：

> "广播-会议中上下两个 nounce 的衔接问题与解决方案"

nonce 的衔接问题：
- 上一个会议结束时的 nonce
- 下一个会议开始时的 nonce
- 如何保证连续性？

## 预 nonce

预 nonce = 预先计算的 nonce，用于：
- 提前建立连接
- 减少实时计算成本
- 确保会议连贯性

## nonce 广播的作用

1. 同步网络难度
2. 建立会议之间的连贯性
3. 作为 atom 的标识符

---

## 相关概念

- [[consensus/hashcash与POW]]
- [[atom/Atom数据结构]]
