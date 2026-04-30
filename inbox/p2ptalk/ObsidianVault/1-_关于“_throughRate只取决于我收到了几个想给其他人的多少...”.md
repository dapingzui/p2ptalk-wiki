---
subject: 关于“ throughRate只取决于我收到了几个想给其他人的多少...”
thread_size: 1
first_date: 2026-04-16 07:09
last_date: 2026-04-16 07:09
participants: ["文博 <chenmoonmo@gmail.com>"]
source: Google Groups p2ptalk
tags:
  - p2ptalk
  - thread
---

# 关于“ throughRate只取决于我收到了几个想给其他人的多少...”

**1 条消息** · 2026-04-16 07:09 → 2026-04-16 07:09

## 参与者
- 文博 <chenmoonmo@gmail.com>

---

## 消息列表

### [1] 文博 <chenmoonmo@gmail.com>
> 2026-04-16 07:09

周一老史提到一个对于 atom 系统的思考，即如何理解 throughRate 这个值，他说“*throughRate 控制从 atomNew 到 
atomOut 
的速率，和对外传播的关系不大，只取决于我收到了几个想给其他人的多少，进而他认为既然这里是‘我决定给别人多少’那么是不是可以交给用户自己定义*”。

我当时在回答这个问题的时候并没有回答前面的问题，而是从后面的推广入手，说明这样会造成挖出 atom 的人本身能带来的权重不如将 throughRate 
设定得更低的人，因为一旦有人将这个值设得低，那么他就会成为系统的突破口，可以通过这个点进行刷量。

但是回到前面的问题，关于 throughRate 
这个值的理解，也存在一点问题，即他并不是“我”收到多少个想给别人多少，也不是和对外传播的关系不大，甚至说从代码中他就是和对外传播强关联的。

//// instead of zero atom, should change to free atom that propagates, //// 
limited to lower than a certain value like 5 so conflicts quickly // The 
zero atom never propagates, // new atoms always propagate through the user 
that created them if (nAtom == 0 || fOrigin) { vector<unsigned short> 
vTmp(1, nAtom); Union(vAtomsIn, vTmp); if (fOrigin) 
vAtomsOut.push_back(nAtom); return; } vAtomsNew.push_back(nAtom); if 
(vAtomsNew.size() >= nFlowthroughRate || vAtomsOut.empty()) { // Select 
atom to flow through to vAtomsOut 
vAtomsOut.push_back(vAtomsNew[GetRand(vAtomsNew.size())]); // Merge 
vAtomsNew into vAtomsIn sort(vAtomsNew.begin(), vAtomsNew.end()); 
Union(vAtomsIn, vAtomsNew); vAtomsNew.clear(); } 

在代码中，如果我们需要走到 nFlowthroughRate 相关逻辑需要先判断是否为 fOrigin，而如果是则直接 atom 加到 AtomIn 
和 AtomOut 中，而不会继续执行后面的行为。那么这里后面这部分代码的含义就是“我收到的非 origin atom，有多少能进入到 
atomOut”，并且中本聪在代码注释中也说new atoms always propagate through the user that 
created them，那么可以看出这个值不限制传播的起点，而只在传播的过程中起作用，那么他的实际作用就是在影响对外传播。

这个值是影响用户在这个传播算法中接收到几个 
atom后继续传播几个这个说法没问题，但是在表述中，将协议规定的“一个节点可以传播多少”的表述修改成了“我收到了几个想给其他人的多少”，这样将固定的传播过程变成了用户的主观意愿，进而才讨论那这个值是不是可以由用户设置，这里出现了循环论证。

而我理解中，中本聪这里的设计类似于统计和分析的过程，节点通过统计用户的 review 
行为和挖矿行为，进而将这个数据转变为将挖矿（维护网络的行为）视为一种权重并使其基于review 建立的关系传递，从而使用这个值来对评论进行排序。

而“我收到了几个想给其他人的多少”是站在被统计者的角度去看这个系统，反而因为这个统计过程掌握在使用数据的人手上，被统计者只能通过 review 
刷边或努力出块这两个途径来影响结果，才让系统的可攻击面变少。

---
