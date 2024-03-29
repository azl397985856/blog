---
title: Git 中的二分
tags: [算法, 二分]
date: 2022-02-11
---

大家好，我是 lucifer。今天给大家分享 Git 中的算法。

这是本系列的第一篇 - 《Git 中的二分》

<!-- more -->

## 二分代码

当我发现一个难以理解和发现的 bug 的时候，我的**终极办法**就是二分代码。

比如先删去文件 a 的一半代码（大约），然后测试问题是否还在。

- 如果问题不在了，那么我们就找到了出问题的代码。
- 如果问题还在，那么我们继续使用同样的办法，继续删去文件 a 的一半代码（大约），
  然后测试问题是否还在。
- 重复上述步骤，直到找到出问题的代码

这个方法在我一时没有思绪或者帮助别人定位问题的时候非常有用。由于这种做法时间复杂
度大致是 logn，因此只需要短短几次我们就可以大致定位到问题代码。类似地，我们也可
以在多个文件中同时进行二分。

## 二分提交

更多的时候，我们是在两次发布之间发现了一个 bug。而这两个发布之间是有若干 commit
的，并且 commit 还不少（几十个甚至上百个）。

我们也可以使用类似的方法。

- 先切换到两次发布之间的中间提交 x（即使得提交 x 相对于两次发布之间的距离差最小
  ）。

> 实际上这个最小距离差要么是 0， 要么是 1

- 验证问题是否存在。如果不存在，我们不能确定就是这个提交的问题，不妨先标记当前提
  交 c 为 good。如果存在，不妨标记当前提交 c 为 bad。

![](https://p.ipic.vip/29pb0b.jpg)

- 经过上面的标记，我们就可以找到最早呈现 bad 的那次提交，并且最关键的是复杂度为
  logn，其中 n 为我们需要验证的提交的总次数。显然，这个工作量比逐个检查 commit
  要快很多。

> 不理解其中原理？稍后我们会讲。

### Git 中的二分查找

git 的开发者也想到了这一点，因此提供了 bisect 命令来帮助我们做上面这个事情。

使用 bisect 进行问题查找主要依赖于下面的三个命令：

1. git bisect start

启动一个查找，start 后面可以加上 good 和 bad 的提交点：

git bisect start [rev bad] [rev good]

如果不加 good 和 bad 的提交点，那么 git 将会等到我们使用 good 和 bad 命令指定对
应的提交点后开始进行查找

2. git bisect good

用来标记一个提交点是正确的，后面可以加上 rev 来指定某个特定的提交点，如果不加，
则默认标记当前的提交点。

3. git bisect bad

用来标记一个提交点是包含问题的，如果 bad 后可以加上 rev 来指定某个特定的提交点，
如果不加，则默认标记当前的提交点。

## 背后原理

我们来补前面的坑。为什么经过这样的标记，我们就可以找到第一个有问题（标记 bad）的
提交？并且时间复杂度为 $O(logn)$。

正好力扣有一道原理，我们直接用它来讲吧。

### 题目地址(278. 第一个错误的版本)

https://leetcode-cn.com/problems/first-bad-version/

### 题目描述

```
你是产品经理，目前正在带领一个团队开发新的产品。不幸的是，你的产品的最新版本没有通过质量检测。由于每个版本都是基于之前的版本开发的，所以错误的版本之后的所有版本都是错的。

假设你有 n 个版本 [1, 2, ..., n]，你想找出导致之后所有版本出错的第一个错误的版本。

你可以通过调用 bool isBadVersion(version) 接口来判断版本号 version 是否在单元测试中出错。实现一个函数来查找第一个错误的版本。你应该尽量减少对调用 API 的次数。

 

示例 1：

输入：n = 5, bad = 4
输出：4
解释：
调用 isBadVersion(3) -> false
调用 isBadVersion(5) -> true
调用 isBadVersion(4) -> true
所以，4 是第一个错误的版本。


示例 2：

输入：n = 1, bad = 1
输出：1


 

提示：

1 <= bad <= n <= 231 - 1
```

### 思路

可以看出，这个过程和我们上面的描述是一样的。并且我们的目标都是找到第一个出错的提
交。

需要明确的是：

- 如果一个版本 x 是 good 的，那么 [1, x] 之间的所有提交肯定都是 good 的，因此待
  检测版本变为 [x+1,n]
- 如果一个版本 x 是 bad 的，那么 [x, n] 之间所有的提交肯定都是 bad 的。由于我们
  要找到的是第一个有问题的版本，因此待检测版本变为 [1,x-1]

因此无论我们检测的版本是 good 还是 bad，我们都可以将待检测的版本数量变为一半，也
就是说我们可以在 $logn$ 次内找到第一个有问题的版本。

如果你看过我的二分专题，应该知道这就是我总结的**最左二分**。

- [二分专题（上）](https://github.com/azl397985856/leetcode/blob/master/thinkings/binary-search-1.md)
- [二分专题（下）](https://github.com/azl397985856/leetcode/blob/master/thinkings/binary-search-2.md)

### 代码

- 语言支持：Python3

Python3 Code:

```python

class Solution:
    def firstBadVersion(self, n):
        l, r = 1, n
        while l <= r:
            mid = (l + r) // 2
            if isBadVersion(mid):
                # 收缩
                r = mid - 1
            else:
                l = mid + 1
        return l

```

**复杂度分析**

- 时间复杂度：$O(logn)$
- 空间复杂度：$O(1)$

## 总结

二分大法在日常工作中应用还是蛮多的，二分找 bug 是其中一个很实用的技巧。最简单的
二分找 bug 可以通过删除文件内容的方式进行。而如果文件很多，就很不方便了，这个时
候我们可以使用二分提交来完成。

其中的原理其实也很简单，就是一个朴素的最左二分。如果大家对此不熟悉，强烈建议看下
文章中提到的二分专题，两万字总结绝对让你有所收获。
