# GPUs, TPUs & AI 经济学 — Gavin Baker 访谈编译

> **来源**: [YouTube: GPUs, TPUs, & The Economics of AI Explained | Gavin Baker Interview](https://youtu.be/cmUo4841KQw)  
> **主持人**: Patrick O'Shaughnessy (Invest Like the Best)  
> **访谈日期**: 2025年（原文发布时间约2025年底）  
> **编译时间**: 2026-04-25  
> **总时长**: 88分钟  
> **关键词**: Scaling Laws, NVIDIA, Google TPU, Blackwell, Reasoning, ASIC, AI ROI, 太空数据中心, SaaS代理

---

## 一、概述

Gavin Baker 是 Atreides Management 的管理合伙人，一位专注于科技投资的深度价值投资者。这期播客是他与 Patrick O'Shaughnessy 的系列对话之一，覆盖了2025年 AI 基础设施格局的最前沿——从芯片战争、scaling laws 的当前状态，到四大前沿实验室的竞争态势，以及 AI 应用层的经济模型变革。

**核心论点**: AI 进入了一个由三种 scaling laws（预训练 + 后训练 RLVR + test-time compute）同时驱动的时代，Blackwell 的延迟曾靠 reasoning 桥接，但 Blackwell 模型的发布将深刻改变 Google TPU 与 NVIDIA GPU 的竞争格局，并触发 AI 经济学的全局重算。

---

## 二、信息处理方法论

Gavin 分享了他如何追踪 AI 领域的快速变化：

- **亲自使用最高级模型**: 坚持付费使用 Gemini Ultra / Super Grok 等 $200/月 级模型，而不是基于免费版得出结论。免费版≈10岁儿童，付费版≈35岁成人。大量投资人基于免费版下结论是重大错误。
- **X（Twitter）是 AI 主战场**: OpenAI 很大程度上"活在 X 的 vibe 上"。核心研究人员在 X 上公开辩论（如 PyTorch vs Jax）。地球上真正理解前沿 AI 的人约500-1000人，必须紧密跟进他们。
- **Andrew Karpathy 的内容是必读**: 每篇要读三遍。
- **四大前沿实验室**: OpenAI、Gemini（Google）、Anthropic、XAI。任何来自这些实验室的人上播客都值得听。
- **用 AI 追踪 AI**: 播客听完后用 AI 讨论感兴趣的部分，降低摩擦成本。

---

## 三、Scaling Laws 现状

### 3.1 预训练 Scaling Laws

**核心事实**: Gemini 3 确认了预训练 scaling laws 仍然有效。这是一个经验观察而不是物理定律——人类精确测量它但尚未理解其底层机制（Gavin 类比古埃及人精确测量太阳运动但不懂轨道力学）。

关键时间线：
- XAI 实现了 20 万块 Hoppers 的 coherent 集群后，受限于芯片代际，无法获得更大规模的 coherent 集群
- 因此按预训练 scaling laws，**2024-2025 年本应无 AI 进步**
- Blackwell 延迟使这个"空窗期"从理论上延伸到 18 个月

### 3.2 Reasoning 挽救了 AI 进步

**如果不出现 reasoning，从2024年中到Gemini 3发布将没有任何AI进展。** 这对市场的影响不可想象。

2024年10月之后的所有进展都基于两种新的 scaling laws：

1. **后训练 Scaling Law (RLVR)**: 基于 verified rewards 的强化学习。Karpathy 名言：软件中"只要你能指定，就能自动化"；AI 中"只要你能验证，就能自动化"。这个区分至关重要。
2. **Test-Time Compute Scaling Law**: 推理时让模型思考更久。

ARC AGI 评分从 0→8%（四年）到 8→95%（三个月），就是 reasoning 的威力。

三种 scaling laws 是**乘数关系**——更好的基础模型 × reasoning = 指数级进步。

---

## 四、芯片战争：NVIDIA vs Google TPU

### 4.1 Blackwell 的艰难诞生

Blackwell 是科技史上最复杂的产品转型：

| 维度 | Hopper | Blackwell |
|------|--------|-----------|
| 散热 | 风冷 | 液冷 |
| 机架重量 | ~1000磅 | ~3000磅 |
| 功耗 | ~30kW (30个美国家庭) | ~130kW (130个美国家庭) |

**机架级转型的类比**：换一台新 iPhone = 要换全屋插座到220V + 装Tesla Powerwall + 发电机 + 太阳能板 + 全屋加湿系统 + 加固地板。

多个 Blackwell SKU 被取消，产量爬坡极其缓慢，大规模部署仅在过去3-4个月才开始。

### 4.2 TPU 的短期优势

在 Blackwell 难产的18个月里，Google 的 TPU V6（2024）→ TPU V7（2025）稳步迭代。
Gavin 的类比：Hopper = WWII 王牌战机 P-51 Mustang；Blackwell = F-35 隐形战机。但 Hopper→Blackwell 之间，Google 的 TPU 已经进化到了 F-4 Phantom 水平。

Google 在此期间成为**最低成本的 token 生产者**，这是 Gavin 职业生涯中第一次"低成本生产者"在科技领域如此重要（Apple 不是靠低价手机成为万亿公司的）。

Google 的战略：**吸走 AI 生态系统的经济氧气**——以低成本优势使竞争对手难以融资，最终取得主导份额。

### 4.3 Blackwell 的逆转

**关键预测**: 第一个 Blackwell 训练的模型将来自 XAI（约2026年初）。原因：
- Jensen 公开表示"没有人比 Elon 建数据中心更快"
- XAI 为 NVIDIA 承担了工作台角色——最快部署大规模 coherent 集群，帮助 NVIDIA 找出 bug

即使拿到了 Blackwell，也需要 6-9 个月才能达到 Hopper 的性能水平（软件优化、工程经验积累）。Hopper 当年超越 Ampere 也是这个节奏。

**GB300 的战略意义**: 与 GB200 的机架完全兼容（drop-in compatible），无需改造数据中心——意味着所有 GB200 数据中心可以直接插 GB300。这是大规模快速部署的关键。

### 4.4 Google TPU 的结构性困境

Gavin 对 Google TPU 的长期前景提出了尖锐质疑：

**Broadcom 的中间利润问题**:
- 芯片设计分前端（架构）和后端（实现+代工管理）
- Google 做 TPU 前端，Broadcom 做后端并管理台积电
- Broadcom 的半导体部门毛利率 **50-55%**
- 2027年 TPU 支出估算约 $300亿 → Google 支付 Broadcom ~$150亿
- 整个 Broadcom 半导体部门的 OPEX 仅 ~$50亿
- **经济理性**: Google 可以挖走 Broadcom 整个半导体团队、双倍薪资、再多赚 $50亿
- **导火索**: Google 引入 MediaTek（台湾 ASIC 公司，毛利率更低）作为第二个供应商，这是对 Broadcom 的第一枪

**保守设计决策**: Gavin 认为 Google 在 TPU 设计上偏保守，部分原因是与 Broadcom 的双轨供货结构导致的摩擦力。

**GPU 加速 vs ASIC**: AMD Lisa Su 和 Jensen 对"客户自己做 ASIC"的回应是：**我们每年一代 GPU，你跟不上**。而且 ASIC 用户会迅速发现：
- 只做了加速器芯片，那 NIC 怎么办？CPU 怎么办？scale-up switch？scale-out protocol？光模块？软件栈？
- 至少三代才能做出好芯片（TPU V1 很弱，TPU V3/V4 才勉强有竞争力）
- Gavin 认为最终只有 Trainium（Amazon）和 TPU 会存活，且两者最终都会运行在客户自有的工具链上

---

## 五、四大前沿实验室格局

### 5.1 Reasoning 改变了游戏规则

**2023-2024 年 Eric Vichria 的观察**（Gavin 引用）：
- 基础模型是"历史上增值最快的资产"
- Gavin 修正版：**没有独特数据和互联网级分发渠道的**基础模型才是增值最快的

Reasoning 从根本上改变了这个逻辑：

**数据飞轮重新启动**:
- 传统互联网公司飞轮：好产品→用户→数据→更好产品（Netflix/Amazon/Meta/Google 的护城河）
- 预训练时代：模型发布后就是它了，RLHF 反馈很难闭环
- Reasoning 时代：用户反馈 → verifiable reward → 模型改进。飞轮开始重新转动。

### 5.2 各家点评

**Meta**: Mark Zuckerberg 2025年1月预测 Meta 将拥有"最好、最强性能的 AI"。Gavin 的结论："他错得不能再错了"。Meta 在 AI 上投入巨资但失败了（Jan LeCun 离职、十亿美金挖研究员），说明这件事**真的很难做**。

**Microsoft**: 收购 Inflection AI，公开宣称内部模型将快速进步。没有发生。

**Amazon**: 收购 Adept AI，Nova 模型排不进前 20。

**XAI**: 第一个 Blackwell 模型，第一个大规模推理部署。OpenRouter 上 token 处理量已领先（1.35万亿 vs Google 8000亿 vs Anthropic 7000亿）。Elon 的 Tesla/SpaceX/XAI 正在融合——XAI = Optimus 的智能模块 + 太空数据中心 + 内置客户群。

**OpenAI**: 核心问题是**高成本的 token 生产者**。支付的 compute margin 和运营效率问题导致 $1.4万亿 的 Stargate 承诺。Code Red 状态正是这些结构性压力的体现。

**Anthropic**: 运营最谨慎——烧钱速度远低于 OpenAI，增速更快。与 Google/Amazon 合作使用 TPU 和 Trainium，受益于同 Google 一样的低成本优势。近期签署 $50亿 NVIDIA 订单——Dario 理解 Blackwell/Rubin 相对 TPU 的优势，NVIDIA 因此从有 XAI 和 OpenAI 两个"拳手"变成三个。

### 5.3 中国因素

DeepSeek V3.2 技术论文坦言：**与美国前沿实验室的差距在于算力不足**——这是政治上正确但仍有风险的说法。

中国限制 Blackwell 进口可能是一个战略错误。Blackwell 模型上线后将大幅扩大中美 AI 差距。预计中国在 2026 年底左右会意识到问题，届时 DARPA/DoD 正在推进稀土替代方案。地缘政治上，Blackwell 给了美国很大的筹码。

---

## 六、AI 的 ROI 问题

### 6.1 经验事实：ROI 已为正

Gavin 强调：AI 的 ROI 在经验上、事实上、无可争议地已经为正。

方法很简单：
- 最大的 GPU 支出来自上市公司
- 这些公司报告**经过审计的季度财报**
- 计算 ROIC，大额 GPU 支出后的 ROIC 高于支出前

来源：
- OPEX 节省（部分 ROI）
- 推荐系统从 CPU 迁移到 GPU 带来的效率提升（主要驱动力）
- 所有大型互联网公司的收入增长已加速

### 6.2 Blackwell ROI 空窗担忧

Gavin 曾担心 Blackwell 大规模部署后的 ROI 空窗：
- Blackwell 用于训练（无直接 ROI）→ 通过推理产生 ROI
- 可能存在 3 个季度的 ROCE 空窗，CapEx 极高而 ROI 尚未体现
- Meta 已经出现 ROIC 下降的季度（未能产出前沿模型）

**缓解信号**: 2025年第三季度是第一个 Fortune 500 非科技公司给出具体 AI 量化效益的季度。
- **C.H. Robinson**（全球最大货运代理公司）：AI 报价从 15-45 分钟/60%回复率 → 秒级/100%回复率。股价涨 20%。

### 6.3 未来 ROI 的三个阶段

Gavin 认为 AI 需要完成价值传递的三步：
1. **更智能 → 更有用**（短期）
2. **更有用 → 科学突破**（中期）
3. **科学突破 → 全新产业**（长期）

**有用性的核心**: 一致性和可靠性。关键在于：
- 长上下文窗口（记住所有 Slack/Outlook/公司手册）
- 持续执行长时间任务（从预订餐厅 → 预订整个家庭旅行）
- 销售和客户支持（AI 最擅长说服）

---

## 七、边缘 AI 是最大的熊市案例

Gavin 认为除了 scaling laws 本身衰退外，**edge AI 是最大、最可怕的熊市逻辑**。

三年后，一台更大更厚的手机上，搭载足够的 DRAM 和电池，可以运行精简版的 Gemini 5 或 Grok 4（30-60 tokens/秒，115 IQ 水平），**免费**。这正是 Apple 的策略——成为 AI 的分发者，隐私安全，设备侧运行。

如果 30-60 t/s、115 IQ 的水平"足够好"，则云端"God models"的需求逻辑将被颠覆。

---

## 八、SaaS 公司的致命错误

这是 Gavin 最强烈的观点之一。

**历史类比**: 传统零售商对电商的判断——"亚马逊在亏损，电商低毛利，我们不投"——最终导致全行业覆灭。

**SaaS 的自我欺骗**: 死守 70-90% 的毛利率，拒绝接受 AI 的 40% 毛利率。

AI 的本质是**每次使用都要重新计算**（与传统软件"一次编写、无限分发"完全相反）。好的 AI 公司毛利率在 40% 左右，但因为人类员工极少，现金流产生速度反而更快。

**Gavin 的方案**: SaaS 公司应该：
1. 公开拆分 AI 收入和 AI 毛利率
2. 短期内将毛利率降至接近零，用现金牛业务补贴
3. 用数据优势碾压纯 AI 创业公司

"这是生死存亡的决策。**除了微软，所有人都在失败**。"

核心平台公司的方案：CRM → 销售 Agent；ServiceNow → 服务 Agent。如果不这样做，别人的 Agent 会接入你的系统抽走数据，**你最终会被关掉**。

> "他们的平台在燃烧，旁边就有一个漂亮的平台可以跳过去，扑灭火，现在你有两个平台了。"

---

## 九、电力和算力供给

### 9.1 电力约束

电力是推高 GPU 定价权的天然约束：
- 如果电力的瓶颈，每瓦特能产出的 token 数 = 收入倍数
- 顶级产品不在乎价格，3-5x 的 token/瓦特就是 3-5x 的 revenue
- 美国核电建设太慢（NEPA法规、一只蚂蚁都可能让核电站停工多年）
- **天然气 + 太阳能**是现实解决方案
- 已观察到供给侧响应：Caterpillar 计划未来几年将产能提升75%

### 9.2 台积电的保守

台积电因恐惧产能过剩而放缓扩张——他们曾在与 Sam Altman 会面后"嘲笑他是播客小哥，根本不知道自己在说什么"。这种谨慎可能成为供给的天然调节器（与电力一样）。

### 9.3 DRAM 周期风险

如果出现自 90 年代以来第一个真正的 DRAM 周期——价格不是涨百分之几十，而是涨**数倍**——将成为 AI 基础设施的重大瓶颈。

---

## 十、太空数据中心

**Gavin 认为未来 3-4 年最重要的非芯片突破**。

**第一性原理分析**:

| 维度 | 地面数据中心 | 太空数据中心 |
|------|-------------|-------------|
| 能源 | 需要电网+电池+备用发电机 | 24小时太阳直射，能量强度+30%，总辐照量6倍，无需电池 |
| 散热 | 复杂 HVAC/CDU/液冷系统（占机架大部分重量） | 暗面辐射器，接近绝对零度，**免费** |
| 互联 | 光纤（激光通过玻璃纤维） | 真空中激光直连，更快 |
| 延迟 | 手机→基站→光纤→metro router→数据中心→回传 | 卫星与手机直连（Starlink Direct to Cell 已验证） |

"第一性原理上，太空数据中心的每个维度都优于地面数据中心。"

**关键制约**: 发射成本。只有 Starship 能经济地实现。SpaceX/Tesla/XAI 正在融合——XAI=智能模块，Optimus=执行体，SpaceX=太空算力。这将为 XAI 带来战略优势。

**时间线**: 太空数据中心成为主力部署约需 5-6 年。届时如果台积电同时扩张产能，可能导致快速产能过剩。

---

## 十一、半导体创业复兴

NVIDIA 的市值飙升单枪匹马点燃了半导体VC。与历史上不同的是，现在的新创公司创始人平均 50 岁——是已经在行业巨头工作了 20 年的资深架构师。

**系统级需求**: 一个 Blackwell 机架有数千个组件，NVIDIA 只做其中 2-300 个。所有其他组件厂商（收发器、线缆、背板、激光器）也必须每年加速。这种生态系统的竞争压力是推动年更节奏的关键。没有哪一家公司能独自完成这件事。

---

## 十二、核聚变、量子与泡沫

Gavin 观察到当前市场存在**滚动泡沫**：

- 2020: EV 创业公司泡沫（非 Tesla 的 EV 公司跌了 99%）
- 2021: Meme stocks
- 现在: **核聚变/SMR 和量子计算**泡沫

**问题不是这些技术不伟大，而是公开市场没有好的表达方式**：
- 核聚变/SMR：公开市场标的都不是真正领先者
- 量子计算的真正领先者是 Google、IBM、Honeywell（不是上市的量子概念股）

"Quantum supremacy"被广泛误解——它不是量子在所有领域超越经典计算，而是量子能做经典计算做不了的计算。

---

## 十三、"Whatever AI needs, it gets"

一个有趣的观察：过去两年，每当 AI 遇到瓶颈，社会会自发加速解决问题。
- 电力瓶颈 → 美国核能舆论 180 度反转
- 芯片瓶颈 → 太空数据中心概念迅速崛起
- Rubin 相对 Blackwell 将是"极其顺畅的过渡"
- AMD MI450 加入竞争

Gavin 提到 Kevin Kelly 的《What Technology Wants》——技术作为一个整体（technium）会推动人类为其成长提供所需的一切。

---

## 十四、Gavin 的个人投资哲学

### 14.1 投资生涯起源

Gavin 大学专业是英语和历史，原计划做滑雪流浪者 + 河流向导 + 野生动物摄影师 + 写小说。父母唯一的要求是："去做一次专业实习"。

唯一能拿到的实习：DLJ（Donaldson, Lufkin & Jenrette）私人财富管理部门。工作是：每次出研报，查阅哪些客户持有该股票，邮寄给他们。然后他开始读研报——"这是我见过最有趣的东西"。

**他理解的投资本质**：**技巧和运气并存的游戏**，类似于扑克。技术在于：
- 拥有最彻底的历史知识
- 与对当下事件最准确的理解相交
- 对"接下来会发生什么"形成差异化的判断
- 在股票市场这个"赌马系统"中找出被错误定价的标的

**三天内做了什么**：
- 买 Peter Lynch 的书，两天看完
- 读关于 Warren Buffett 的书
- 读《Market Wizards》
- 读巴菲特致股东的信——再读一遍
- 自学会计
- 回学校后从英语/历史双专业改为历史/经济学

### 14.2 关键方法论

- **ROIC (Return on Invested Capital)** 和 **Incremental ROIC** 是最重要的指标之一
- 投资 = **寻找隐藏的真相**。找到别人还没看到的真相，是对冲基金产生 alpha 的方式
- **历史 + 当下事件 = 对未来的差异性判断**

### 14.3 给年轻人的建议

- "我一辈子没擅长过任何事"——运动最后被选、滑雪不好、乒乓球输给所有朋友、无法战胜公园里的棋手
- 投资是唯一让他觉得有竞争力的领域
- **好奇心驱动的学习**: 从历史→对当下事件的兴趣→对投资的热情，是一条自然路径

---

## 十五、关键预测总结

| 预测 | 时间线 |
|------|--------|
| 第一个 Blackwell 训练模型（XAI） | 2026年初 |
| 中国企业意识到失去 Blackwell 是战略错误 | 2026年底 |
| 太空数据中心成为主力部署 | 约2030-2031 |
| SaaS 公司大规模 AI agent 化 | 2026-2027 |
| Edge AI 开始威胁云端推理需求 | 约3年后 |

---

## 延伸阅读与参考资料

- **Patrick O'Shaughnessy**: Invest Like the Best 播客
- **Kevin Kelly**: *What Technology Wants* — 讨论技术作为有自主生命力的整体（technium）
- **Andrew Karpathy**: AI 研究博客与论文
- **Eric Vichria**: 关于 foundation models 是"最快增值资产"的观察
- **ARC AGI 评分**: 从 0→8%（四年）到 8→95%（三个月）的 reasoning 突破
- **OpenRouter**: 各模型 API token 使用量统计（反映相对市场地位）

---

*本编译基于 88 分钟播客转录，内容已按主题重组，保留核心论点和关键数据，去除口语化冗余。*
