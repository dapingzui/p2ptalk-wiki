# P2PTalk Wiki — index

> 基于真实讨论提炼的概念知识图谱。每个概念页含：核心引述 + 讨论要点 + 相关链接。

---

## Concepts（50 pages）

### atom（16）
- [[atom/Atom是什么]] — atom ≠ 业务载体，atom ≠ mempool
- [[atom/Atom的信号属性]] — 信号/声明，不是交易
- [[atom/Atom数据结构]] — atoms_in/out、links_out、total_atoms
- [[atom/Atom流转机制]] — throughRate + 随机选择问题
- [[atom/可组合与可复制]] — 与 Bitcoin 的核心区别
- [[atom/Atom与Mempool]] — 两条路线：进 vs 不进
- [[atom/Atom与Bitcoin关系]] — Bitcoin 是外部输入
- [[atom/创世Atom与nonce]] — Genesis Atom 与 nonce 广播
- [[atom/观测值与节点行为]] — atom 数量作为观测值
- [[atom/Atom的独立性]] — Atom 系统的自主性
- [[atom/脚本是谓词]] — Bitcoin 脚本 = 布尔值函数
- [[atom/CUser与CReview数据结构]] — market.h 中的数据结构，与 Bitcoin 独立
- [[atom/Mempool不是唯一业务来源]] — mempool 不是唯一的业务通道
- [[atom/比特币块出块时间作为atom]] — 出块时间 = Bitcoin 的 atom
- [[atom/挖矿必然有Mempool]] — 有挖矿就有 mempool 的推测
- [[atom/IP与品牌]] — 迪士尼IP类比：可复制 ≈ Atom，稀缺性控制
- [[atom/双花问题]] — 防双花需求与 Atom 可复制属性的天然冲突

### atom/谓词（1）
- [[atom/谓词]] — 谓词 = 条件返回 TRUE/FALSE 的函数

### consensus（10）
- [[consensus/hashcash与POW]] — hashcash 格式，nonce 的存在性
- [[consensus/难度调整]] — DAA
- [[consensus/不可逆性与激励]] — 难度归零 = 激励的实现
- [[consensus/Bitcoin难度调整三问]] — 无上帝视角的正确答案判定
- [[consensus/传播算法与生产关系]] — 传播算法决定生产关系
- [[consensus/竞争与押注]] — 押注社会结构改变
- [[consensus/中本聪共识原理]] — Bitcoin 的参照
- [[consensus/BitDNS与P2P市场]] — 中本聪2010年愿景
- [[consensus/研究推动与洞察迭代]] — 三次推动研究的计算
- [[consensus/元胞自动机]] — 传播=计算，局部规则涌现全局声誉

### broadcast（6）
- [[broadcast/中间会面机制]] — 订阅行为、桥梁节点、轻节点类比
- [[broadcast/泛洪与5跳]] — 5跳覆盖全网
- [[broadcast/节点与SPV轻节点]] — 全节点 vs 轻节点
- [[broadcast/发布订阅机制]] — 发布订阅与匹配
- [[broadcast/网络拓扑与衰减因子]] — 衰减因子、局部 vs 全域共识
- [[broadcast/洪泛atom的激励问题]] — 洪泛 atom 的动机问题

### meeting（2）
- [[meeting/会议共识]] — 社交共识层
- [[meeting/会议规则与激励闭环]] — 完成任务才能发起会议

### market（4）
- [[market/声誉与市场]] — 声誉需要使用才有价值
- [[market/匹配系统]] — 意图广播、节点发现
- [[market/算力市场]] — 计算任务发布与承接
- [[market/商品与声誉]] — 商品 offerbook vs 声誉系统

### ai（4）
- [[ai/AI与生产关系]] — AI agent + 闪电贷
- [[ai/AI与女巫攻击]] — AI agent 的女巫问题
- [[ai/闪电贷模式]] — 原子性交易的四个步骤
- [[ai/自驱系统]] — AI 时代的自驱激励

### security（3）
- [[security/女巫攻击防护]] — POW / 质押两条路线
- [[security/时间锁与多签机制]] — Bitcoin 闪电网络三大机制
- [[security/预信任节点]] — Pre-trusted Peers，PageRank，分布式信任

### math（2）
- [[math/向量空间模型]] — atom 作为向量
- [[math/图论与集聚性]] — 网络拓扑与集聚系数

---

## 核心引述

> "ATOM 跟比特币有本质上的区别。atom本身不存在业务需求，所以atom本身不应该进入mempool。"
> — **Woo**

> "atom在memepool中呈现的不是utxo的交易类型，因为atom的数据状态，更像是一种'信号'，一种'声明'。"
> — **沄涣**

> "比特币系统里，传播算法决定生产关系。"
> — **Woo**

> "P2P markets can be built on top. The nodes would just need to remember the feedback scores."
> — **中本聪（2010）**
>
> "在市场里面，IP就是成交的最后一环，当一个商品在市场占有一定份额，而且这个份额跟对手趋于平衡的时候，那个贴有米奇老鼠的商品会卖的更好。"
> — **Woo**
>
> "这个米奇老鼠是可以复制的，可以双花的。就像Atom一样。"
> — **Woo**
>
> "pub/sub之前只有推消息的模式，后面引入了中间件，才有了频道和拉取的模式。中间件是pub/sub消息模型的一个很大的创新，直接让pub/sub从可用到好用。"
> — **沄涣（引 Satoshi 研究）**

> "挖矿的感觉是什么，是你手里有一个验证的标准，但是你没有算出来之前，你就是验证不成功。一旦这个nonce被找到，就成真的了。"
> — **shijingyao123**

> "只要系统存在挖矿机制，那么就必然存在内存池。"
> — **initsysctrl**

---

## Metadata

| | |
|---|---|
| messages | 333 |
| threads | 74 |
| concept pages | 50 |
| date range | 2025-11 ~ 2026-04 |
