---
title: 听说逆向思维能够降低时间复杂度？
tags: [数据结构, 算法, 逆向思维]
date: 2022-01-27
---

以终为始在日常生活中指的是**先确定目标，再做好计划**。之前读管理学的书的时候，学到了这个概念。

而在算法中，以终为始指的是**从结果反向推，直到问题的初始状态**。

那么什么时候适合反向思考呢？简单的原则就是：

1. 正向思考的情况比较多
2. 代码比较难写或者算法复杂度过高

这个时候我们可以考虑反向操作。

我的习惯是如果直接求解很难，我会优先考虑使用能力检测二分，如果不行我则会考虑反向思考。

> 关于能力检测二分，可以在我的公众号中找到，大家可以在《力扣加加》回复二分获取。

今天西法通过三道题来给大家聊聊到底怎么在写算法题的时候运用**以终为始**思想。

<!-- more -->

## 机器人跳跃问题

这道题来自于牛客网。地址：nowcoder.com/question/next?pid=16516564&qid=362295&tid=36905981

### 题目描述

```
时间限制：C/C++ 1秒，其他语言2秒

空间限制：C/C++ 32M，其他语言64M

机器人正在玩一个古老的基于DOS的游戏。游戏中有N+1座建筑——从0到N编号，从左到右排列。编号为0的建筑高度为0个单位，编号为i的建筑的高度为H(i)个单位。

起初， 机器人在编号为0的建筑处。每一步，它跳到下一个（右边）建筑。假设机器人在第k个建筑，且它现在的能量值是E, 下一步它将跳到第个k+1建筑。它将会得到或者失去正比于与H(k+1)与E之差的能量。如果 H(k+1) > E 那么机器人就失去 H(k+1) - E 的能量值，否则它将得到 E - H(k+1) 的能量值。

游戏目标是到达第个N建筑，在这个过程中，能量值不能为负数个单位。现在的问题是机器人以多少能量值开始游戏，才可以保证成功完成游戏？

输入描述:
第一行输入，表示一共有 N 组数据.

第二个是 N 个空格分隔的整数，H1, H2, H3, ..., Hn 代表建筑物的高度

输出描述:
输出一个单独的数表示完成游戏所需的最少单位的初始能量

输入例子1:
5
3 4 3 2 4

输出例子1:
4

输入例子2:
3
4 4 4

输出例子2:
4

输入例子3:
3
1 6 4

输出例子3:
3
```

### 思路

题目要求初始情况下至少需要多少能量。正向求解会比较困难，因此我的想法是：

1. 能力检测二分。比如能量 x 是否可以，如果 x 可以，那么大于 x 的能量都可以。依此我们不难写出代码。
2. 反向思考。 虽然我们不知道最开始的能量是多少，但是我们知道最后的能量是 0 才最优，基于此我们也可以写出代码。

这里我们使用第二种方法。

具体来说：我们从后往前思考。到达最后一级的能量最少是 0 。而由于:

```py
next = pre + (pre - H[i])
```

因此：

```py
pre = (next + H[i]) / 2
```

由于除以 2 可能会出现小数的情况，因此需要 ceil。

你可以：

```py
pre = math.ceil((next + H[i]) / 2)
```

也可以：

```py
pre = (next + H[i] + 1) // 2
```

> // 是地板除，即向下取整

### 代码（Python）

```py
n = input()
H = input().split(" ")
ans = 0
for i in range(len(H) - 1, -1, -1):
    ans = (ans + int(H[i]) + 1) // 2
print(ans)
```

**复杂度分析**

- 时间复杂度：$O(n)$
- 空间复杂度：$O(1)$

这个题目的关键一句话总结就是：我们需要确定最少需要多少初始能量，因此我们是不确定最初的能量的，我们可以确定的是达到最后一个建筑能量是 0 才最优。

## 2139. 得到目标值的最少行动次数

第二道题是 2022.01 月份的一场周赛的第二题，题目还是比较新的。

### 题目地址

https://leetcode-cn.com/problems/minimum-moves-to-reach-target-score/

### 题目描述

```
你正在玩一个整数游戏。从整数 1 开始，期望得到整数 target 。

在一次行动中，你可以做下述两种操作之一：

递增，将当前整数的值加 1（即， x = x + 1）。
加倍，使当前整数的值翻倍（即，x = 2 * x）。

在整个游戏过程中，你可以使用 递增 操作 任意 次数。但是只能使用 加倍 操作 至多 maxDoubles 次。

给你两个整数 target 和 maxDoubles ，返回从 1 开始得到 target 需要的最少行动次数。

 

示例 1：

输入：target = 5, maxDoubles = 0
输出：4
解释：一直递增 1 直到得到 target 。


示例 2：

输入：target = 19, maxDoubles = 2
输出：7
解释：最初，x = 1 。
递增 3 次，x = 4 。
加倍 1 次，x = 8 。
递增 1 次，x = 9 。
加倍 1 次，x = 18 。
递增 1 次，x = 19 。


示例 3：

输入：target = 10, maxDoubles = 4
输出：4
解释：
最初，x = 1 。
递增 1 次，x = 2 。
加倍 1 次，x = 4 。
递增 1 次，x = 5 。
加倍 1 次，x = 10 。


 

提示：

1 <= target <= 109
0 <= maxDoubles <= 100
```

### 思路

由于刚开始数字为 1，最终状态为 target。因此正向思考和反向思考都是 ok 的。

而如果正向模拟的话，虽然很容易实现，但是时间复杂度太高。

这是因为从 1 开始我们有两个选择（如果仍然可以加倍），接下来仍然有两个选择（如果仍然可以加倍）。。。

因此时间复杂度大致为 $O(target * maxDoubles)$。代入题目给的数据范围显然是无法通过的。

而正向思考比较困难，我们不妨从反向进行思考。

从 target 开始，如果 target 是奇数，显然我们只能通过 + 1 而来，即使我们仍然可以加倍。这样时间复杂度就降低了。不过这还不够，进而我们发现如果 target 为偶数我们应该选择加倍到 target（如果仍然可以加倍），而不是 + 1 到 target。这是因为

1. 我们是反向思考的，如果你现在不选择加倍而是后面再选择加倍那么加倍带来的收益会更低
2. 加倍的收益一定大于 + 1，换句话说加倍可以更快达到 target。

基于此，不难写出如下代码。

### 代码

- 语言支持：Python3

Python3 Code:

```python

class Solution:
    def minMoves(self, target: int, maxDoubles: int) -> int:
        ans = 0
        while maxDoubles and target != 1:
            ans += 1
            if target % 2 == 1:
                target -= 1
            else:
                maxDoubles -= 1
                target //= 2
        ans += (target - 1)
        return ans

```

**复杂度分析**

如果 maxDoubles 无限大，那么时间大概是 $log target$。而如果 target 无限大，那么时间大概是 maxDoubles。因此时间复杂度为 $O(min(maxDouble, log target))$

- 时间复杂度：$O(min(maxDouble, log target))$
- 空间复杂度：$O(1)$

## LCP 20. 快速公交

最后一道题是力扣杯的一道题，难度为 hard，我们来看下。

## 题目地址(20. 快速公交)

https://leetcode-cn.com/problems/meChtZ/

### 题目描述

```
小扣打算去秋日市集，由于游客较多，小扣的移动速度受到了人流影响：

小扣从 x 号站点移动至 x + 1 号站点需要花费的时间为 inc；
小扣从 x 号站点移动至 x - 1 号站点需要花费的时间为 dec。

现有 m 辆公交车，编号为 0 到 m-1。小扣也可以通过搭乘编号为 i 的公交车，从 x 号站点移动至 jump[i]*x 号站点，耗时仅为 cost[i]。小扣可以搭乘任意编号的公交车且搭乘公交次数不限。

假定小扣起始站点记作 0，秋日市集站点记作 target，请返回小扣抵达秋日市集最少需要花费多少时间。由于数字较大，最终答案需要对 1000000007 (1e9 + 7) 取模。

注意：小扣可在移动过程中到达编号大于 target 的站点。

示例 1：

输入：target = 31, inc = 5, dec = 3, jump = [6], cost = [10]

输出：33

解释：
小扣步行至 1 号站点，花费时间为 5；
小扣从 1 号站台搭乘 0 号公交至 6 * 1 = 6 站台，花费时间为 10；
小扣从 6 号站台步行至 5 号站台，花费时间为 3；
小扣从 5 号站台搭乘 0 号公交至 6 * 5 = 30 站台，花费时间为 10；
小扣从 30 号站台步行至 31 号站台，花费时间为 5；
最终小扣花费总时间为 33。

示例 2：

输入：target = 612, inc = 4, dec = 5, jump = [3,6,8,11,5,10,4], cost = [4,7,6,3,7,6,4]

输出：26

解释：
小扣步行至 1 号站点，花费时间为 4；
小扣从 1 号站台搭乘 0 号公交至 3 * 1 = 3 站台，花费时间为 4；
小扣从 3 号站台搭乘 3 号公交至 11 * 3 = 33 站台，花费时间为 3；
小扣从 33 号站台步行至 34 站台，花费时间为 4；
小扣从 34 号站台搭乘 0 号公交至 3 * 34 = 102 站台，花费时间为 4；
小扣从 102 号站台搭乘 1 号公交至 6 * 102 = 612 站台，花费时间为 7；
最终小扣花费总时间为 26。

提示：

1 <= target <= 10^9
1 <= jump.length, cost.length <= 10
2 <= jump[i] <= 10^6
1 <= inc, dec, cost[i] <= 10^6
```

### 思路

由于起点是 0，终点是 target。和上面一样，正向思考和反向思考难度差不多。

那么我们可以正向思考么? 和上面一样正向思考情况太多，复杂度过高。

那么如何反向思考呢？反向思考如何优化复杂度的呢？

由于题目可以在移动过程中到达编号大于 target 的站点，因此正向思考过程中坐标大于 target 的很多点我们都需要考虑。

而如果反向思考，我们是**不能在移动过程中到达编号大于 0 的站点的**，因此情况就大大减少了。而达编号大于 target 的站点只需要思考**向右移动后再乘坐公交返回 target 的情况即可（也就是说我们是做了公交然后往回走的情况）**

对于每一个位置 pos，我们都思考：

1. 全部走路
2. 直接乘公交
3. 走几步再乘公交

在这三种情况取最小值即可。

问题的关键是情况 3，我们如何计算是走几步再乘公交呢？如果反向思考，我们可以很简单地通过 pos % jump[i] 算出来，而开始乘公交的点则是 pos // jump。

### 代码

- 语言支持：Python3

Python3 Code:

```python

class Solution:
    def busRapidTransit(self, target: int, inc: int, dec: int, jumps: List[int], cost: List[int]) -> int:
        @lru_cache(None)
        def dfs(pos):
            if pos == 0: return 0
            if pos == 1: return inc
            # 最坏的情况是全部走路，不乘公交，这种情况时间为 pos * inc
            ans = pos * inc
            for i, jump in enumerate(jumps):
                pre_pos, left = pos // jump, pos % jump
                if left == 0: ans = min(ans, cost[i] + dfs(pre_pos))
                else: ans = min(ans, cost[i] + dfs(pre_pos) + inc * left, cost[i] + dfs(pre_pos + 1) + dec * (jump - left))
            return ans
        return dfs(target) % 1000000007


```

**复杂度分析**

令 T 为 jump 数组的长度。

- 时间复杂度：$O(target * T)$
- 空间复杂度：$O(target)$

## 总结

反向思考往往可以达到降维打击的效果。有时候可以使得求解思路更简单，代码更好写。有时候可以使得情况更少，复杂度降低。

回顾一下什么时候使用反向思考呢？一个很简单的原则就是：

1. 正向思考的情况比较多
2. 代码比较难写或者算法复杂度过高

我给大家举了三个例子来说明如何运用反向思考技巧。其中

- 第一题正向思考只能使用逐一枚举的方式，当然我们可以使用二分降低复杂度，但是复杂度仍然不及反向思考。
- 第二题反向思考情况大大减少，复杂度指数级降低，真的是降维打击了。
- 第三题利用无法超过 0 的位置这点，反向思考降低复杂度。

这些题还是冰山一角，实际做题过程中你会发现**反向思考很常见，只是主流的算法划分没有对应的专题罢了** 。我甚至还有想法将其加入**91 天学算法中**，就像后期加**枚举章节一样**，我认为反向思考也是一个基础的算法思考，请诸君务必掌握！
