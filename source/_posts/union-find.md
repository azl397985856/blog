---
title: 【算法提高班】并查集
tags: [LeetCode, 算法系列]
categories:
  - [LeetCode]
---

关于并查集的题目不少，官方给的数据是 30 道（截止 2020-02-20），但是有一些题目虽然官方没有贴`并查集`标签，但是使用并查集来说确非常简单。这类题目如果掌握模板，那么刷这种题会非常快，并且犯错的概率会大大降低，这就是模板的好处。

我这里总结了几道并查集的题目：

- [547.朋友圈](https://leetcode-cn.com/problems/friend-circles/solution/mo-ban-ti-bing-cha-ji-python3-by-fe-lucifer-2/)
- [721. 账户合并](https://leetcode-cn.com/problems/accounts-merge/solution/mo-ban-ti-bing-cha-ji-python3-by-fe-lucifer-3/)
- [990. 等式方程的可满足性](https://leetcode-cn.com/problems/satisfiability-of-equality-equations/solution/mo-ban-ti-bing-cha-ji-python3-by-fe-lucifer/)

## 并查集概述

并查集算法，主要是解决图论中「动态连通性」问题的

Union-Find 算法解决的是图的动态连通性问题，这个算法本身不难，能不能应用出来主要是看你抽象问题的能力，是否能够把原始问题抽象成一个有关图论的问题。

如果你对这个算法不是很明白，推荐看一下这篇文章[Union-Find 算法详解](https://leetcode-cn.com/problems/friend-circles/solution/union-find-suan-fa-xiang-jie-by-labuladong/)，讲的非常详细。

你可以把并查集的元素看成部门的人，几个人可以组成一个部门个数。

并查集核心的三个方法分别是`union`, `find`, `connected`。

- `union`: 将两个人所在的两个部门合并成一个部门（如果两个人是相同部门，实际山不需要合并）

![](https://tva1.sinaimg.cn/large/0082zybply1gc32a7x6y1j30zk0k0dki.jpg)
（图来自 labuladong）

- `find`: 查找某个人的部门 leader
- `connnected`: 判断两个人是否是一个部门的

![](https://tva1.sinaimg.cn/large/0082zybply1gc32atzy3tj30zk0k0tde.jpg)
（图来自 labuladong）

## 模板

这是一个我经常使用的模板，我会根据具体题目做细小的变化，但是大体是不变的。

```python
class UF:
    parent = {}
    cnt = 0
    def __init__(self, M):
        n = len(M)
        for i in range(n):
            self.parent[i] = i
            self.cnt += 1

    def find(self, x):
        while x != self.parent[x]:
            x = self.parent[x]
        return x
    def union(self, p, q):
        if self.connected(p, q): return
        self.parent[self.find(p)] = self.find(q)
        self.cnt -= 1
    def connected(self, p, q):
        return self.find(p) == self.find(q)
```

如果你想要更好的性能，这个模板更适合你，相应地代码稍微有一点复杂。

````python

```python
class UF:
    parent = {}
    size = {}
    cnt = 0
    def __init__(self, M):
        n = len(M)
        for i in range(n):
            self.parent[i] = i
            self.size[i] = 1
            self.cnt += 1

    def find(self, x):
        while x != self.parent[x]:
            x = self.parent[x]
            # 路径压缩
            self.parent[x] = self.parent[self.parent[x]];
        return x
    def union(self, p, q):
        if self.connected(p, q): return
        # 小的树挂到大的树上， 使树尽量平衡
        leader_p = self.find(p)
        leader_q = self.find(q)
        if self.size[leader_p] < self.size[leader_q]:
            self.parent[leader_p] = leader_q
        else:
            self.parent[leader_q] = leader_p
        self.cnt -= 1
    def connected(self, p, q):
        return self.find(p) == self.find(q)
````

大家可以根据情况使用不同的模板。
