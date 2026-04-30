---
subject: "Google group 和 比特币的 P2P 都来自 Usenet"
category: 其他话题
thread_size: 2
first_date: 2025-11-18 00:06
last_date: 2025-11-19 15:43
participants: ["chenmoonmo", "icekernel"]
source: Google Groups p2ptalk
created: "2026-04-20"
tags:
  - p2ptalk
  - 其他话题
---

# Google group 和 比特币的 P2P 都来自 Usenet

**2 条消息** · 2025-11-18 → 2025-11-19
**分类：** 其他话题

## 参与者
chenmoonmo | icekernel

---

## 消息时间线

### 1. chenmoonmo <chenmoonmo@gmail.com>  ·  2025-11-18 00:06

首先 Google group 是来自于谷歌收购的 Deja News，它是 Deja 的 Usenet 存档。而 Google group 
的服务是一个通过电子邮件进行主题讨论的讨论组（discussion groups），电子邮件只是其实现方式，其还是脱胎于 Usnet。
另外在比特币白皮书、邮件列表、中本聪私人邮件和讨论组中都多次提到 Usenet 和其标准 NNTP。
- 首先在白皮书中提到：“A timestamp server works by taking a hash of a block of items 
to be timestamped and widely publishing the hash, such as in a newspaper or 
*Usenet* post [2-5]. ”，这里只是因为 timestamp server 在当时依赖于 Usenet 
的分布式见证，而比特币则取代了这种模式。
- 在和亚当贝克的私人邮件中，中本聪也提到：“The main thing my system adds is to also use 
proof-of-work to support a distributed timestamp server.While users are 
generating proof-of-work to make new coins for themselves, the same 
proof-of-work isalso supporting the network timestamping. This is instead 
of Usenet.”
- 还可见于 https://en.bitcoin.it/wiki/Source:Trammell/Nakamoto_emails
- 而在比特币早期，服务器和客户端还没有明显分化，虽然中本聪在论文中写到了 SPV，但他还没有实现它，而在关于 EOS 
创始人质疑比特币的带宽和存储成本将导致系统无法处理微支付时，中本聪则说“The current system where every user is 
a network node is not the intended configuration for large scale.  That 
would be like every Usenet user runs their own NNTP server.  The design 
supports letting users just be users.  The more burden it is to run a node, 
the fewer nodes there will be.  Those few nodes will be big server farms. 
 The rest will be client nodes that only do transactions and don't 
generate.”，而这正好在解释 NNTP 协议 
https://datatracker.ietf.org/doc/html/rfc3977#section-5 中关于 NNTP 
的两种使用模式，“NNTP is traditionally used in two different ways. The first use is 
"reading", where the client fetches articles from a large store maintained 
by the server for immediate or later presentation to a user and sends 
articles created by that user back to the server (an action called 
"posting") to be stored and distributed to other stores and users. The 
second use is for the bulk transfer of articles from one store to another. 
Since the hosts making this transfer tend to be peers in a network that 
transmit articles among one another, and not end-user systems, this process 
is called "peering" or "transit". (Even so, one host is still the client 
and the other is the server). NNTP 
传统上有两种不同的用途。第一种用途是“读取”，即客户端从服务器维护的大型存储库中获取文章，以便立即或稍后呈现给用户，并将用户创建的文章发送回服务器（此操作称为“发布”），以便服务器存储并分发给其他存储库和用户。第二种用途是将文章从一个存储库批量传输到另一个存储库。由于执行此传输的主机通常是网络中相互传输文章的对等节点，而不是终端用户系统，因此此过程称为“对等连接”或“传输”。（即便如此，其中一台主机仍然是客户端，另一台主机仍然是服务器。）”，再此基础上深入研究，会发现比特币的泛洪传播机制也和 
NNTP 类似，和我们之前认为的比特币直接传播新接收到的交易和区块给邻近节点不同，当比特币节点收到新交易或区块时，它向邻居发送 inv 
消息，包含数据项的哈希值列表。邻居节点对比本地内存池（Mempool）或区块链，若发现缺失，则回复 getdata 消息。原始节点发送 tx 或 
block 消息。
而NNTP的协议则是服务器 A 向服务器 B 发送 IHAVE <message-id> 命令，列出自己拥有的一批新文章的 ID，服务器 B 
检查本地数据库，回复 SENDME <message-id>，仅请求自己缺失的文章。 服务器 A 仅发送被请求的文章内容。

剩余部分我还在研究，但是这里确实有很多有意思的点，所以发出来讨论...

---

### 2. icekernel <icekernel@gmail.com>  ·  2025-11-19 15:43
> ↩ 回复: `<f1e6aa9c-28f9-40b7-99ba-b131ac82d340n@googlegroups.com>`

>
> https://medium.com/coinmonks/craig-wright-the-wei-dai-lies-d03ad9c32a87

Satoshi Nakamoto replied to Dr Back on 21 August 2008 as follows:

“*Thanks, I wasn’t aware of the b-money page, but my ideas start from
exactly that point. I’ll e-mail him to confirm the year of publication so I
can credit him. The main thing my system adds is to also use proof-of-work
to support a distributed timestamp server. While users are generating
proof-of-work to make new coins for themselves, the same proof-of-work is
also supporting the network timestamping. This is instead of Usenet.*”


在这里讨论 中本聪一开始说的是要替代usenet的时间戳功能
因为之前usenet被密码学当作存在性证明。所以看起来时间戳的需求一直存在，并且在被使用中本聪找了一个更好的办法来解决了这个问题，因为解决双花问题需要时间戳


usenet 时间戳具体用法

90年代末，为了对抗由于出口管制带来的审查，密码朋克们非常依赖匿名网络。
 为了证明某个匿名声明（比如漏洞披露或政治宣言）是在特定时间发出的，而不暴露身份，发帖者会：
-

   1.

   对消息签名并哈希。
   2.

   通过 Mixmaster（混淆网络）发送到 alt.anonymous.messages。
   3.

   Usenet 的服务器会自动打上 Date 头信息。
   4.

   这个 Date 加上全网可见的哈希，就构成了*匿名但可验证的时间证明  *

---
