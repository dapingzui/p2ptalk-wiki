---
type: concept
subject: Atom数据结构
category: atom
tags: [atom, p2ptalk, 数据结构, atoms_in, atoms_out]
related:
  - [[atom/Atom流转机制]]
  - [[atom/Atom是什么]]
  - [[meeting/会前同步]]
created: 2026-04-20
---

# Atom数据结构

## 每个节点维护的状态

```python
node_state = {
    atoms_in:    Number,   # 收到的 atom 总数（流入）
    atoms_out:   Number,   # 发出的 atom 总数（流出）
    links_out:   Number,   # 向外的链接数
    total_atoms: Number,   # 净余额 = atoms_in - atoms_out
}
```

## 会前同步中的实际数据

```
hzw:
  atoms_in: 8
  atoms_out: 5
  links_out: 1
  total_atoms: 9

ls:
  atoms_in: 14
  atoms_out: 8
  links_out: 4
  total_atoms: 15
```

## atomNew、atomsIn、atomsOut 的流转

沄涣提出：

> "atom的 new、in、out 对应 memepool 中的交易过程，最终通过 atom 的流转跟流向，会产生关系图谱。"

- **atomNew**：新产生的 atom，尚未决定流转方向
- **atomsIn**：收到的 atom 累积
- **atomsOut**：发出的 atom 累积

流转：
```
A 评论 B → A 的 atomNew 转移给 B
B 评论 C → B 的 atomsOut 复制给 C
```

## 关系图谱

> "atom的流转跟流向会产生关系图谱，最终是为了确立谁的关系权重。"
> — **沄涣**

---

## 相关概念

- [[atom/Atom流转机制]]
- [[meeting/会前同步]]
