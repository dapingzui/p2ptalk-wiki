---
type: concept
subject: hashcash与POW
category: consensus
tags: [atom, p2ptalk, hashcash, POW, nonce, 工作量证明]
related:
  - [[consensus/难度调整]]
  - [[atom/Atom是什么]]
  - [[security/女巫攻击防护]]
created: 2026-04-20
---

# hashcash与POW

## hashcash 格式

```
hashcash:1:2026-04-20:random_data:::
```

原理：
1. 给定一个字符串
2. 寻找 nonce 使 SHA256(字符串+nonce) 前 N 位为 0
3. N 越大，难度越高

## shijingyao123 的关键分析

> "hashcash是一种特定格式的文本字符串：这个意思是说，你得先有一个特定格式的文本字符串，再进行哈希计算。过去大家的重点在 doublehash 上。"

重点：hashcash 的价值不在于哈希计算本身，而在于**特定格式字符串的设计**。

## nonce 的存在性问题

Woo 提出的深层问题：

> "计算出来的 nonce 在计算出来之前是不存在的，为什么计算出来就是真实存在？"

这涉及到：
- nonce 作为"发现"而非"发明"
- 计算完成 = 状态从不存在变为存在
- 不可逆性

## Atom 中 nonce 的作用

initsysctrl 的实例：

> "我的谓词是同步了历史的停机内容，还有更新雷雷的难度，**nonce符合范围**。"

nonce 在 Atom 中用于：
- 难度验证
- 同步历史
- 状态确认

---

## 相关概念

- [[consensus/难度调整]]
- [[security/女巫攻击防护]]
