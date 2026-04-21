---
type: concept
subject: CUser与CReview数据结构
category: atom
tags: [atom, p2ptalk, CUser, CReview, market.h, 数据结构]
related:
  - [[atom/Atom数据结构]]
  - [[broadcast/网络拓扑与衰减因子]]
created: 2026-04-20
---

# CUser与CReview数据结构

## market.h 中的设计

胥亚朋描述：

> "根据 market.h 中对 CUser 的设计，里面的 vector<uint256> vLinksOut 结构可以构成 1 个完整的网络拓扑。"

## CUser 结构

```cpp
class CUser {
    vector<uint256> vLinksOut;  // 向外连接的链接
    // ...
}
```

vLinksOut = 该用户向外连接的其他用户地址列表

## CReview 结构

CReview = 评论对象

> "atom 则围绕 CUser / CReview 等非交易对象，实现链下的业务与声誉逻辑。"

## 关键洞察：与 Bitcoin 的独立性

> "二者在对象类型、状态空间以及调用路径上彼此独立，不存在直接依赖或调用关系。"

| | Bitcoin | Atom |
|---|---|---|
| 核心对象 | CTransaction | CUser / CReview |
| 存储 | Mempool | 链下业务 |
| 关系 | UTXO | vLinksOut 网络 |

## mempool 不是唯一的业务来源

> "进一步看，mempool 并不是比特币系统中唯一的业务来源。"

这说明：
- 除了 mempool，还有其他业务通道
- Atom 可以有自己的业务逻辑，不需要经过 mempool

---

## 相关概念

- [[atom/Atom数据结构]]
- [[broadcast/网络拓扑与衰减因子]]
