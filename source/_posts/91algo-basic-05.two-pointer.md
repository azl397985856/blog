---
title: 【91算法-基础篇】05.双指针
tags: [数据结构, 算法, 算法提高班, 91天学算法, 力扣加加]
categories:
  - [力扣加加]
  - [91天学算法]
---

力扣加加，一个努力做西湖区最好的算法题解的团队。就在今天它给大家带来了《91 天学算法》，帮助大家摆脱困境，征服算法。`前天想加入却没能加入的小伙伴可以进来啦，直接扫描文末二维码即可。`

<img src="https://tva1.sinaimg.cn/large/007S8ZIlly1gf2atkdikgj30u70u0tct.jpg" width="50%">

​<!-- more -->

## 什么是双指针

顾名思议，双指针就是**两个指针**，但是不同于 C，C++中的指针， 其是一种**算法思想**。

如果说，我们迭代一个数组，并输出数组每一项，我们需要一个指针来记录当前遍历的项，这个过程我们叫单指针（index）的话。

![](https://tva1.sinaimg.cn/large/007S8ZIlly1gf5w79tciyj30aa0hl77b.jpg)

（图 1）

那么双指针实际上就是有两个这样的指针，最为经典的就是二分法中的左右双指针啦。

![](https://tva1.sinaimg.cn/large/007S8ZIlly1gf5yfe9da7j307504ut8r.jpg)

（图 2）

我们发现双指针是一个很宽泛的概念，就好像数组，链表一样，其类型会有很多很多， 比如二分法经常用到`左右端点双指针`。滑动窗口会用到`快慢指针和固定间距指针`。 因此双指针其实是一种综合性很强的类型，类似于数组，栈等。。 但是我们这里所讲述的双指针，往往指的是某几种类型的双指针，而不是“只要有两个指针就是双指针了”。

那么究竟我们算法中提到的双指针指的是什么呢？我们一起来看下算法中双指针的常见题型吧。

## 常见题型有哪些？

这里我将其分为三种类类型，分别是：

1. 快慢指针（两个指针步长不同）
2. 左右端点指针（两个指针分别指向头尾，并往中间移动，步长不确定）
3. 固定间距指针（两个指针间距相同，步长相同）

不管是哪一种双指针，只考虑双指针部分的话 ，由于最多还是会遍历整个数组一次，因此时间复杂度取决于步长，如果步长是 1，2 这种常数的话，那么时间复杂度就是 O(N)，如果步长是和数据规模有关（比如二分法），其时间复杂度就是 O(logN)。并且由于不管规模多大，我们都只需要最多两个指针，因此空间复杂度是 O(1)。下面我们就来看看双指针的常见套路有哪些。

## 常见套路

1. 快慢指针

   1.1. 判断链表是否有环

   - [find-the-duplicate-number](https://leetcode-cn.com/problems/find-the-duplicate-number/)

   - [【每日一题】- 2020-01-14 - 142. 环形链表 II · Issue #274 · azl397985856/leetcode](https://github.com/azl397985856/leetcode/issues/274)

     1.2 读写指针。典型的是`删除重复元素`

   - [remove-duplicates-from-sorted-list](https://leetcode-cn.com/problems/remove-duplicates-from-sorted-list/)

2. 左右端点指针

   2.1. 二分查找。

   2.2. 暴力枚举中“从大到小枚举”（剪枝）[find-the-longest-substring-containing-vowels-in-even](https://leetcode-cn.com/problems/find-the-longest-substring-containing-vowels-in-even-counts/solution/qian-zhui-he-zhuang-tai-ya-suo-pythonjava-by-fe-lu/)

   2.3 有序数组。区别于上面的二分查找，这种算法指针移动是连续的，而不是跳跃性的，典型的是 LeetCode 的`两数和`，以及`N数和`系列问题。

3. 固定间距指针

   3.1 一次遍历（One Pass）求链表的中点

   3.2 一次遍历（One Pass）求链表的倒数第 k 个元素

   3.3. 固定窗口大小的滑动窗口

## 模板(伪代码)

1. 快慢指针

```jsx
l = 0
r = 0
while 没有遍历完
  if 一定条件
    l += 1
  r += 1
return 合适的值
```

2. 左右端点指针

```jsx
l = 0
r = n - 1
while l < r
  if 找到了
    return 找到的值
  if 一定条件1
    l += 1
  else if  一定条件2
    r -= 1
return 没找到

```

3. 固定间距指针

```jsx
l = 0
r = k
while 没有遍历完
  自定义逻辑
  l += 1
  r += 1
return 合适的值
```

## 题目推荐

### 左右端点指针

- Pair with Target Sum (easy)
- Remove Duplicates (easy)
- Squaring a Sorted Array (easy)
- Triplet Sum to Zero (medium)
- Triplet Sum Close to Target (medium)
- Triplets with Smaller Sum (medium)
- Subarrays with Product Less than a Target (medium)
- Dutch National Flag Problem (medium)
  > 下面是二分类型
- Order-agnostic Binary Search (easy)
- Ceiling of a Number (medium)
- Next Letter (medium)
- Number Range (medium)
- Search in a Sorted Infinite Array (medium)
- Minimum Difference Element (medium)
- Bitonic Array Maximum (easy)

### 快慢指针

- LinkedList Cycle (easy)
- Start of LinkedList Cycle (medium)
- Happy Number (medium)
- Middle of the LinkedList (easy)

### 固定间距指针

- Maximum Number of Vowels in a Substring of Given Length（medium）
  > 固定窗口大小的滑动窗口见专题篇的滑动窗口专题（暂未发布）
