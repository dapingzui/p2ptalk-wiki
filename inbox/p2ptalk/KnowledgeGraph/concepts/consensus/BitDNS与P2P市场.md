---
type: concept
subject: BitDNS与P2P市场
category: consensus
tags: [atom, p2ptalk, BitDNS, P2P市场, 中本聪, 反馈分数]
related:
  - [[consensus/传播算法与生产关系]]
  - [[market/声誉与市场]]
created: 2026-04-20
---

# BitDNS与P2P市场

## 中本聪的原话

2010年 Bitcointalk 论坛：

> "P2P markets can be built on top. The nodes would just need to remember the feedback scores."
> "P2P 市场可以建立在上层……节点只需要记住评分反馈即可。"

来源：https://bitcointalk.org/index.php?topic=195.msg1611#msg1611

## 中本聪的愿景

中本聪早在 2010 年就设想了：
1. Bitcoin 作为底层
2. P2P 市场建立在上面
3. 节点自己记住反馈分数（声誉）

## BitDNS 的含义

BitDNS = Bitcoin + DNS
- 在 Bitcoin 基础上建立 DNS 类似系统
- 节点自己维护声誉评分
- 无需中心化权威

## 这条路线的重要性

> "这个里面就在聊交易类型和脚本了，这就是我完整找到的路线。"

Atom 系统继承的路线：
- Bitcoin 底层（POW、时间戳）
- P2P 市场（声誉、反馈）
- 节点自主维护（去中心化）

补一条边界提醒：这里讨论“上层能搭什么”时，不要把外部辅助能力误算成 Bitcoin Script 的原生能力。关于 Script 作为谓词系统、以及“阿克曼函数 / 图灵完备 / 外部展开”的边界，见 [[atom/Script表达能力边界]]。

---

## 相关概念

- [[consensus/传播算法与生产关系]]
- [[market/声誉与市场]]
