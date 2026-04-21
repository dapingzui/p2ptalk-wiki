---
type: concept
subject: Atom流转机制
category: atom
tags: [atom, p2ptalk, 流转, throughRate, 随机选择]
related:
  - [[atom/Atom数据结构]]
  - [[broadcast/中间会面机制]]
  - [[consensus/难度调整]]
created: 2026-04-20
---

# Atom流转机制

## throughRate（流转阈值）

当 atomNew 数量超过 throughRate 时，超出部分转移到 atomsOut。

这是系统的流控机制，防止 atom 过度集中。

## 随机选择问题（核心未解）

> "当 B 再次评论时，将其 atomOut 复制给 C，那么在 C 的视角里，看到的 atomOut 可能和 B 不一致。"

问题：
- 不同节点的随机函数不同
- 可能选择**不同的 atom** 加入 atomsOut
- 导致跨节点状态不一致

## 可能的解决方向

1. **确定性随机**：使用共同种子（区块哈希）
2. **广播确认**：选择结果广播确认
3. **选举机制**：类似 PoS 的验证人选择

## 流转与关系权重

> "atom的流转跟流向会产生关系图谱，最终是为了确立谁的关系权重。"
> — **沄涣**

atom 的流转不是简单的转移，而是**关系权重的确认过程**。

---

## 相关概念

- [[atom/Atom数据结构]]
- [[broadcast/中间会面机制]]
