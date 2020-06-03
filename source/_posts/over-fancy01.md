---
title: 【异议！】第一期 《这个🦅题的复杂度怎么分析？》
date: 2020-06-03
tags: [异议！]
categories:
  - [异议！]
---

力扣加加，努力做西湖区最好的算法题解。

<!-- more -->

## 事情的起源

昨天有人在我的力扣题解下留言，说我的时间复杂度解释有问题。思考再三，决定将这个问题抛出来大家一起讨论一下，我会在明天的公众号给大家公布参考答案。对于回答正确且点赞数最高的，我会送出 **8.88** 的现金红包，参与方式以及要求在文末。

其实这是一道前几天的力扣官方每日一题，我们先来看一下题目描述：

给定 n 个非负整数，用来表示柱状图中各个柱子的高度。每个柱子彼此相邻，且宽度为 1 。

求在该柱状图中，能够勾勒出来的矩形的最大面积。

![](https://tva1.sinaimg.cn/large/007S8ZIlly1gfewdafiexj305805odft.jpg)

以上是柱状图的示例，其中每个柱子的宽度为 1，给定的高度为  [2,1,5,6,2,3]。

![](https://tva1.sinaimg.cn/large/007S8ZIlly1gfewdi9rmlj305805o0sv.jpg)

图中阴影部分为所能勾勒出的最大矩形面积，其面积为  10  个单位。

示例:

输入: [2,1,5,6,2,3]

输出: 10

## 那么问题来了

这个题目我给出了四个解法，其中前两个是超时的，后两个是可以 AC 的。

而后两个可以 AC 的有一个是单调栈的解法，这个单调栈的解法有两个精妙的地方。第一是哨兵元素的选取，第二是是用了一个栈而不是两个。

另外一个可以 AC 的解法，也就是今天我们要讨论的解法，这个解法使用了两个数组，相对于单调栈的复杂度，其常系数更大，但是其思路同样巧妙。

为了大家更好的理解这个解法，我这里贴一下它的未被优化版本。思路为：

暴力尝试`所有可能的矩形`。从中心向两边进行扩展。对于每一个 i，我们计算出其左边第一个高度小于它的索引 p，同样地，计算出右边第一个高度小于它的索引 q。那么以 i 为最低点能够构成的面积就是`(q - p - 1) * heights[i]`。 这种算法毫无疑问也是正确的。 假设 f(i) 表示求以 i 为最低点的情况下，所能形成的最大矩阵面积。那么原问题转化为`max(f(0), f(1), f(2), ..., f(n - 1))`。

具体算法如下：

- 我们使用 l 和 r 数组。l[i] 表示 左边第一个高度小于它的索引，r[i] 表示 右边第一个高度小于它的索引。
- 我们从前往后求出 l，再从后往前计算出 r。
- 再次遍历求出所有的可能面积，并取出最大的。

代码：

```python
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        n = len(heights)
        l, r, ans = [-1] * n, [n] * n, 0
        for i in range(1, n):
            j = i - 1
            while j >= 0 and heights[j] >= heights[i]:
                j -= 1
            l[i] = j
        for i in range(n - 2, -1, -1):
            j = i + 1
            while j < n and heights[j] >= heights[i]:
                j += 1
            r[i] = j
        for i in range(n):
            ans = max(ans, heights[i] * (r[i] - l[i] - 1))
        return ans
```

其实 while 循环内部是没有必要一格一格移动的。 举例来说，对于数组[1,2,3,4,5]，我们要建立 r 数组。我们从 4 开始，4 的右侧第一个小于它索引的是 n（表示不存在）。同样 3 的右侧第一个小于它索引的也是 n（表示不存在），以此类推。如果用上面的解法的话，我们每次都需要从当前位置遍历到尾部，时间复杂度为$O(N^2)$。

实际上，比如遍历到 2 的时候，我们拿 2 和前面的 3 比较，发现 3 比 2 大，并且我们之前计算出了比 3 大的右侧第一个小于它索引的是 n，也就是说我们可以直接移动到 n 继续搜索，因为**这中间的都比 3 大，自然比 2 大了，没有比较的意义**。 这样看来时间复杂度就被优化到了$O(N)$。

代码：

```python
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        n = len(heights)
        l, r, ans = [-1] * n, [n] * n, 0

        for i in range(1, n):
            j = i - 1
            while j >= 0 and heights[j] >= heights[i]:
                j = l[j]
            l[i] = j
        for i in range(n - 2, -1, -1):
            j = i + 1
            while j < n and heights[j] >= heights[i]:
                j = r[j]
            r[i] = j
        for i in range(n):
            ans = max(ans, heights[i] * (r[i] - l[i] - 1))
        return ans

```

这位读者看到这里产生了一个疑问，这个疑问就是我开篇所讲的。我们来看下他是怎么说的。

![](https://tva1.sinaimg.cn/large/007S8ZIlly1gfexzj6zm3j31ae0b8q4w.jpg)

这位读者提到**交替的这种情况时间复杂度会退化到$O(N^2)$**，那么实际情况真的是这样么？

## 悬赏

大家对上面的优化后的算法复杂度是怎么看的？请留言告诉我！ 需要注意的是：

1. 我们所说的复杂度是渐进复杂度，也就是说是忽略常数项的。而这里我要求你**带上常系数**。
2. 这里要求计算的是**整个完整算法**的复杂度。
3. 请分别说出该算法在`最差情况`，`最好情况`下的复杂度。

参与方式：`复制链接，并在浏览器打开，然后在里面评论即可`。链接地址：https://leetcode-cn.com/problems/largest-rectangle-in-histogram/solution/84-zhu-zhuang-tu-zhong-zui-da-de-ju-xing-duo-chong/

大家也可以关注我的公众号《力扣加加》获取更多更新鲜的 LeetCode 题解。

![](https://tva1.sinaimg.cn/large/007S8ZIlly1gfcuzagjalj30p00dwabs.jpg)
