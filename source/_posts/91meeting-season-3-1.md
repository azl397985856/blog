---
title: 91 天学算法第三期视频会议总结
tags: [数据结构, 算法, 算法提高班, 91天学算法, 力扣加加]
date: 2021-03-01
categories:
  - [力扣加加]
  - [91天学算法]
---

这是 91 天学算法第三期视频会议的一个文字版总结。想要参加第三期的小伙伴可在公众号后台回复 91 查看参与方式。

大家好，我是 lucifer。前几天给 91 的学员开了一场视频会议，关于目前学习的情况，西法给大家的学习建议以及下期的规划做了简单的讨论。

​<!-- more -->

## 时间

- 2021-02-28 10:00

## 参与人员

- 91 第三期的部分学员

## 在线观看

- https://www.bilibili.com/video/BV1qK4y1J7DD/

## 会议主题

### 基础篇回顾

基础篇内容如下：

- 【91 算法-基础篇】01.数组，栈，队列
- 【91 算法-基础篇】02.链表
- 【91 算法-基础篇】03.树
- 【91 算法-基础篇】04.哈希表
- 【91 算法-基础篇】05.双指针
- 【91 算法-基础篇】06.图（加餐）
- 【待定】模拟和枚举（加餐）

除了加餐，其他都会给大家每日一题的练习时间。对于加餐来说，目前还没有完结，等到完结之后会第一时间在群里通知。

对于基础篇的内容需要大家重点掌握的是**队列和栈**。理由如下：

- 数组没啥好讲的，大家用的太多了，唯一需要注意的是各种操作的复杂度。
- 链表和树我写的两篇专题已经非常清楚了，几乎涉及了所有考点。大家如果对这两部分内容没信息，建议看看我公众号的[几乎刷完了系列](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzI4MzUxNjI3OA==&action=getalbum&album_id=1702469751517528072#wechat_redirect "几乎刷完了系列")。
- 哈希表从战略上考察点基本就是**空间换时间**，战术上就是统计频率，计算最近或者最远，分桶等几个操作而已，具体可看讲义。
- 双指针我们会在专题篇分两个小专题讲解，分别是 **二分法** 和 **滑动窗口**，因此基础篇没太搞懂也不要紧。

### 通过几个题目，讲解更有如何有效率的解题

以下是视频中提到的题目，每个题目都有一定代表性。

1. https://binarysearch.com/problems/Split-List-to-Minimize-Largest-Sum

第一题主要告诉大家做题的时候一定要**结合讲义**，我们出的题通常都是和讲义中的一个或者多个知识点有关。出题的目的就是强化理解讲义中的内容。因此如果看完题目，你完全不知道讲义中有挂内容，很有可能是你自己对讲义的理解不到位。这个时候需要再次阅读讲义或者求助群友和群主。否则你的进步会很慢，这也是**一些同学向我反馈跟了很久却没有效果的最主要原因**。

2. https://binarysearch.com/problems/Kth-Largest-Pair-Product/editorials/3567227

这道题其实是想告诉大家：

2.1. 如果一道题没思路。可以通过最最暴力的解法入手，然后找算法瓶颈，根据瓶颈使用适当的数据结构和算法进行优化
2.2. 讲义中提到的点，一定要牢记。比如我们讲义中提到了**固定小顶堆求第 k 大的数**，这道题就是求第 k 大的数，你就应该想到。作为新手我对你们的期望是要想到，不管最终能不能用，想到是必须的。

3. https://leetcode-cn.com/problems/widest-vertical-area-between-two-points-containing-no-points/

这道题主要告诉大家**题目如果看不懂， 那练习再多都没用**，建议大家通过几个文字很多的题目或者带图的题目练练手，提供阅读理解能力。

### 算法面试题（非编程题）epoll

![](https://p.ipic.vip/b8at1z.jpg)

以一个具体的例子： 《epoll 是如何优化我们的程序的？》 为例，讲解算法面试中**问答题**。如果你不想八股文式面试， 那么就需要大家对基本的数据结构与算法有很深的理解。而这恰好是基础篇的内容。

### 下期（专题篇）预告

专题篇目录:

- 二分专题
- 滑动窗口专题
- 位运算专题
- 搜索（BFS、DFS、回溯）专题
- 背包
- 动态规划
- 分治
- 贪心

这部分的重点是：**搜索** 和 **动态规划（含背包）**。为什么这两个重要？

- 搜索篇重要的原因是其范围太广了，涉及到的知识很多。
- 动态规划不仅容易考，而且大家普遍认为比较难。（我承认它要比搜索篇难）

而：

- 二分法，滑动窗口相信你看了我的讲义，不会有太大问题。
- 位运算则考察频率不那么高，大家可以将优先级适当放低。
- 分治和贪心算法下限很低，基本看了我的讲义跟着做做题入门是可以的。但是要想精通可是相当难的，但是如果你掌握了搜索篇以及动态规划，那么对你掌握这两个专题会有极大的帮助，这也是为啥我特别强调要掌握**搜索篇**和**动态规划**的原因。

### 插件有什么用？

- 插件源码：https://github.com/leetcode-pp/leetcode-cheat
- 插件功能介绍: https://lucifer.ren/blog/2020/08/16/leetcode-cheat/
- 插件获取方式：公众号《力扣加加》回复插件。

很多人不会用我的插件功能，尤其是复制测试用例。他们好奇为啥官方有了运行内置用例功能，我还弄个复制所有测试用例的功能。这是因为官方的是**运行内置用例**，并不会自动复制到自定义用例的输入框中。

这有什么问题呢？比如我执行了内置的用例报错了，报错的用例是 [1,2,3,4]，而这个用例不在内置用例中。我肯定要调整代码，调整完毕后继续运行。而我这个时候期望的是**运行所有的测试用例** 和 **[1,2,3,4]**这个上次出错的用例。因为我可能为了改这个而导致其他本来可以过的用例现在过不了。

如果这个时候又挂在 [3,2,1] 这个用例。我肯定希望运行所有内置的用例和 [1,2,3,4] 以及 [3,2,1]。而这是官方的功能不具备的。如果想实现这个效果，你需要先点击**执行内置用例**，再点击执行自定义用例。而我的**复制所有内置用例**可以很好的解决这个问题。

### 答疑

回答了几个比较具有代表性的问题。有一个问题是：我想往 java 后端发展，求推荐学习路线。

答：关于 java，其实我并不权威，尽管我是 java 入行，但毕竟几年不碰了。但是任何计算机相关岗位的学习我都建议先学基础，比如网络，算法。然后学操作系统和汇编（操作系统和汇编用到了大量数据结构与算法）。接下来可以学习编程语言的语法，语法熟悉就是语言内置的库，然后是三方库，然后是运行时，比如 java 就是 jvm。最后从大的方向将知识串起来。比如你可以从一个经典的问题**浏览器输入 url 发生了什么**入手来验证自己知识的掌握程度。

其他问题可看视频。

以上就是本文的全部内容了， 大家对此有何看法，欢迎给我留言，我有时间都会一一查看回答。我是 lucifer，维护西湖区最好的算法题解，Github 超 40K star 。大家也可以关注我的公众号《力扣加加》带你啃下算法这块硬骨头。

![力扣加加公众号二维码](https://p.ipic.vip/06i8hz.jpg)
