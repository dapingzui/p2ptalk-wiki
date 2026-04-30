---
subject: （补充资料）Re: 领取计算任务
thread_size: 1
first_date: 2025-12-26 02:28
last_date: 2025-12-26 02:28
participants: ["shijingyao123 <shijingyao123@gmail.com>"]
source: Google Groups p2ptalk
tags:
  - p2ptalk
  - thread
---

# （补充资料）Re: 领取计算任务

**1 条消息** · 2025-12-26 02:28 → 2025-12-26 02:28

## 参与者
- shijingyao123 <shijingyao123@gmail.com>

---

## 消息列表

### [1] shijingyao123 <shijingyao123@gmail.com>
> 2025-12-26 02:28 · 回复 #<CABkMa_N0JrdV-N=ktmjJZPPXC24d

一 hashcash是一种特定格式的文本字符串：这个意思是说，你得先有一个特定格式的文本字符串，再进行哈希计算。
我认为这里我们需要知道这个特定格式的字符串怎么来的，因为过去大家的重点在doublehash上。

引用：https://www.btcstudy.org/2021/10/26/bitcoin-is-an-idea-by-Gigi/#Hashcash-Adam-Back-1997 
Hashcash部分，第二段。

二 然后，我们再来看看hashcash怎么得到这个特定格式字符串的。

引用1：http://www.hashcash.org/docs/hashcash.1   hashcash的代码

引用2：http://www.hashcash.org/faq/   hashcash的FAQ 第三部分

三 回到比特币的论文引用5  《secure names for 
bit-strings》，这里我一直有meme，因为没人告诉我中本聪为什么要引用这篇，但我觉得这个字符串的命名跟比特币的字符串转换有关系。

四 到比特币的代码中，我们可以去查看那个 tostrings的函数，来看看比特币的字符串是怎么转换的。


在2025年12月26日星期五 UTC+8 15:57:38<xuyapeng110> 写道：

> 1.哈希计算的真实性是什么，为什么矿工经过哈希计算能够达成最长链，为什么正确的哈希出来的时候，大家是可以第一时间就能验证通过的。
> 2.难度调整是怎么保证比特币的哈希计算或者比特币的走向是一个正确的方向。
>
> 3. 基准测试在整个比特币的向前发展中发挥的作用是什么？
>
>
>
> jiyeyulie4b310 <jiyeyul...@gmail.com> 于 2025年12月26日周五 15:03写道：
>
>> 1.激励的那一刻发生的是 矿工虽然有算力投入但是在nounce被计算出来那一刻 矿工是不清楚的
>> 2.难度是怎么影响计算成本的
>> 3.难度调整和哈希计算的过程是怎么样的
>>
>> On Friday, December 26, 2025 at 3:00:19 PM UTC+8 chenmoonmo wrote:
>>
>>> 1. 哈希算法的原像计算及其谜题友好性来源（最好是数学保证）
>>> 2. 比特币难度调整算法对此的应用
>>> 3. 比特币挖矿过程中这种验证和计算 nonce 的关系
>>>
>>> 在2025年12月26日星期五 UTC+8 13:31:25<initsysctrl> 写道：
>>>
>>>> 1、需要对你的meme进行拆分，拆分成具体的几个子问题。
>>>> 2、需要对上述子问题结合源代码进行分析
>>>> 3、对所有子问题的解决方式进行抽象，并结合现实进行理解和拓展
>>>> 会议邀请
>>>>
>>>>
>>>> ---- 回复的原邮件 ---- 
>>>> 发件人 矢孤<shijin...@gmail.com> 
>>>> 发送日期 2025年12月26日 13:17 
>>>> 收件人 p2ptalk<p2p...@googlegroups.com> 
>>>> 主题 请求计算 
>>>>
>>>> 挖矿的感觉是什么，是你手里有一个验证的标准，但是，你没有算出来之前，你就是验证不成功，这里甚至都没有系统，在你没有算出来之前没有任何人知道答案是什么，但是三个人都觉得自己算出来了，且验证都通过，可是答案并不一样。系统会选择第一个广播到大多数节点并且被确认的那个来进行激励。所以这里我就很好奇，这个难度调整算法到底是怎么具体运行的，和哈希计算的关系是什么（meme一下，这个跟我现实中遇到问题解决问题的感觉是一样的，我想要解决这个问题，我也大概有预期解决了之后是什么感觉，但是没有解决之前我就是没有解决）
>>>>
>>>> -- 
>>>> You received this message because you are subscribed to the Google 
>>>> Groups "p2ptalk" group.
>>>> To unsubscribe from this group and stop receiving emails from it, send 
>>>> an email to p2ptalk+u...@googlegroups.com.
>>>> To view this discussion visit 
>>>> https://groups.google.com/d/msgid/p2ptalk/CADc1sGYAeautrsB43b7YmbYV_%2B%3Do7WZ%2BD7BmdFdKOoAcN2_dAQ%40mail.gmail.com 
>>>> <https://groups.google.com/d/msgid/p2ptalk/CADc1sGYAeautrsB43b7YmbYV_%2B%3Do7WZ%2BD7BmdFdKOoAcN2_dAQ%40mail.gmail.com?utm_medium=email&utm_source=footer>
>>>> .
>>>> For more options, visit https://groups.google.com/d/optout.
>>>>
>>> -- 
>> You received this message because you are subscribed to the Google Groups 
>> "p2ptalk" group.
>> To unsubscribe from this group and stop receiving emails from it, send an 
>> email to p2ptalk+u...@googlegroups.com.
>>
> To view this discussion visit 
>> https://groups.google.com/d/msgid/p2ptalk/5c8abfe5-9b0c-414c-9c16-3f7735de1dcfn%40googlegroups.com 
>> <https://groups.google.com/d/msgid/p2ptalk/5c8abfe5-9b0c-414c-9c16-3f7735de1dcfn%40googlegroups.com?utm_medium=email&utm_source=footer>
>> .
>
>
>> For more options, visit https://groups.google.com/d/optout.
>>

---
