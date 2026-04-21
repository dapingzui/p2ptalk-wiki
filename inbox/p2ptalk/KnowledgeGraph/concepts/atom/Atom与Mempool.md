---
type: concept
subject: Atom与Mempool
category: atom
tags: [atom, p2ptalk, mempool, 争议]
related:
  - [[atom/Atom是什么]]
  - [[consensus/hashcash与POW]]
created: 2026-04-20
---

# Atom与Mempool

## Woo 的立场：Atom 不应进入 Mempool

> "ATOM 跟比特币有本质上的区别。atom本身不存在业务需求，所以atom本身不应该进入mempool。"
> — **Woo**

理由：
- Atom 不是业务载体
- Atom 不需要交易排序
- Atom 的存在目的是共识，不是价值转移

## 矢孤的探索：Atom 如何进入 Mempool？

> "Atom 是否可以进入 Mempool？"

矢孤的思路：
1. 是否可以将 atom 的传播转化为比特币脚本？
2. 从而加入到比特币内存池中，继而参与到共识中去？

## initsysctrl 的反思

> "雷雷这个回答很棒，尤其是'信用评分是否需要附带算力证明才能进入 memepool'？给我提供了思路——我特么为什么需要有内存池？"

最直接的原因是：如果进入共识的数据不仅需要满足语法、语义上的正确，还可能需要其他条件。

## Atom 在 Mempool 中是什么形式？

沄涣的分析：

> "atom在memepool中呈现的不是utxo的交易类型，因为atom的数据状态，更像是一种'信号'，一种'声明'……atom像是一种特殊的、非金融信息、用来传递信号的数据结构。"

Atom 在 Mempool 中：
- 不是 UTXO 类型
- 是信号/声明
- 独立于 UTXO 模型

## 两条路线

| 路线 | 方案 | 状态 |
|---|---|---|
| A | Atom 加入 Mempool，参与共识 | 讨论中 |
| B | 完全抛弃 Mempool，直接参与共识 | 讨论中 |

---

## 相关概念

- [[atom/Atom是什么]]
