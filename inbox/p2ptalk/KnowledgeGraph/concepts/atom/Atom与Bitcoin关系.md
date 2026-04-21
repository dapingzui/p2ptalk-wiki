---
type: concept
subject: Atom与Bitcoin关系
category: atom
tags: [atom, p2ptalk, Bitcoin, 外部输入]
related:
  - [[atom/Atom是什么]]
  - [[consensus/hashcash与POW]]
created: 2026-04-20
---

# Atom与Bitcoin关系

## 待确认的观点

> "比特币只是atom的外部输入，输出却跟比特币没啥关系。"
> — **会议讨论（待确认）**

## Atom 从 Bitcoin 获取什么？

可能的输入：
- **时间戳**：Bitcoin 区块哈希提供不可篡改的时间证明
- **随机数**：区块哈希作为随机源
- **Sybil 抵抗**：POW 的计算成本防止女巫攻击
- **激励**：通过 BTC 支付结算

## Atom 输出什么？

当前理解：Atom 的输出与 Bitcoin 无关。

Atom 是独立的共识层，不依赖 Bitcoin 的业务逻辑。

## 两条路线

| | 路线A | 路线B |
|---|---|---|
| Atom 与 Bitcoin | 深度绑定 | 独立运行 |
| Atom 进 Mempool | ✅ 作为信号 | ❌ 不进入 |
| 共识保障 | Bitcoin 底层保障 | Atom 自己保证 |
| 状态 | 待确认 | 待确认 |

## 未解答问题

- Atom 如何从 Bitcoin 获取外部输入？
- Atom 是否需要自己的代币激励？
- Atom 是否可以反哺 Bitcoin 网络？

---

## 相关概念

- [[atom/Atom是什么]]
- [[consensus/hashcash与POW]]
