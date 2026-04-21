# CLAUDE.md — P2PTalk Wiki

> Schema for maintaining the P2PTalk wiki.
> Based on Karpathy LLM Wiki pattern.

## Wiki Structure

```
KnowledgeGraph/
├── index.md          ← 入口+目录
├── CLAUDE.md        ← THIS FILE
├── log.md           ← 演进历史
│
├── atom/           ← 5 pages: 核心问题+数据结构+流转+可组合+谓词
├── consensus/      ← 2 pages: hashcash/POW + 难度调整
├── broadcast/      ← 2 pages: 中间会面 + 泛洪5跳
├── meeting/        ← 1 page: 会议共识
├── market/         ← 2 pages: 声誉与市场 + 匹配系统
├── ai/             ← 2 pages: AI与生产关系 + AI与女巫攻击
├── security/       ← 1 page: 女巫攻击防护
└── math/           ← 1 page: 向量空间模型
```

## 内容原则

每个概念页必须包含：
1. **核心引述** — 摘录参与者的原话，用引号标注
2. **讨论要点** — 从讨论中提炼的关键洞察
3. **相关概念链接** — 用 `[[wiki链接]]` 标注

每个概念页回答的核心问题：
- 这个概念是什么？（定义）
- 参与者对这个概念有什么争论？（讨论）
- 这个概念和其他概念有什么关系？（链接）

## 三个操作

### INGEST
新内容 → 提炼到对应概念页 → 更新 log

### QUERY
读 index → 找相关概念 → 综合答案 → 引用 `[[页面]]`

### LINT
检查矛盾、过时、孤立页面

## 状态标签
- 🔴 未解答 — 核心问题
- 🟡 待确认 — 进行中
- 🟢 已确立 — 稳定理解
