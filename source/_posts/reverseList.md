---
title: 一文搞懂《链表反转》
tags: [字节跳动, 链表, 数据结构, 算法, LeetCode]
date: 2020-01-20
categories:
  - [算法, 链表反转]
  - [数据结构, 链表]
  - [LeetCode]
author:
  name: snowan
  avatar: https://avatars1.githubusercontent.com/u/6018815?s=40&v=4
  url: https://github.com/snowan
---

翻转链表一直都是热门题目，笔者就在某大型互联网公司的面试题中碰到过这种题目，这种题目很常常见，相对应的变形和扩展也很多，今天我们就来攻克它吧。

<!-- more -->

## 反转链表

反转链表是这个系列中最简单的了，没有别的要求，就是将一个链表从头到尾进行反转，最后返回反转后的链表即可。

我们来看一个 LeetCode 题目, [206. 反转链表](https://leetcode-cn.com/problems/reverse-linked-list/), 官方难度为 Easy。

### 题目描述

```
反转一个单链表。

示例:

输入: 1->2->3->4->5->NULL
输出: 5->4->3->2->1->NULL
进阶:
你可以迭代或递归地反转链表。你能否用两种方法解决这道题？
```

### 思路

链表的翻转过程，初始化一个为 null 的 previous node（prev），然后遍历链表的同时，当前 node （curr）的下一个（next）指向前一个 node（prev）， 在改变当前 node 的指向之前，用一个临时变量记录当前 node 的下一个 node（curr.next). 即

```java
ListNode temp = curr.next;
curr.next = prev;
prev = curr;
curr = temp;
```

举例如图：翻转整个链表 1->2->3->4->null -> 4->3->2->1->null

![](https://p.ipic.vip/d3iwgw.jpg)

### 代码

我们直接来看下代码：

```js
/**
 * Definition for singly-linked list.
 * function ListNode(val) {
 *     this.val = val;
 *     this.next = null;
 * }
 */
/**
 * @param {ListNode} head
 * @return {ListNode}
 */
function reverseList(head) {
  if (!head || !head.next) return head;

  let cur = head;
  let pre = null;
  while (cur) {
    const next = cur.next;
    cur.next = pre;
    pre = cur;
    cur = next;
  }

  return pre;
}
```

这里不再赘述，如果不理解，想看更多更详细内容，请参考我的[LeetCode 题解 - 206.reverse-linked-list](https://github.com/azl397985856/leetcode/blob/master/problems/206.reverse-linked-list.md)

## 分组反转

这个题目和上面的有点类似，只不过我们并不是从头到尾反转，而是每 k 个为一组进行反转。LeetCode 同样有原题[25. K 个一组翻转链表](https://leetcode-cn.com/problems/reverse-nodes-in-k-group/)官方难度为 Hard。

### 题目描述

```
给你一个链表，每 k 个节点一组进行翻转，请你返回翻转后的链表。

k 是一个正整数，它的值小于或等于链表的长度。

如果节点总数不是 k 的整数倍，那么请将最后剩余的节点保持原有顺序。

示例 :

给定这个链表：1->2->3->4->5

当 k = 2 时，应当返回: 2->1->4->3->5

当 k = 3 时，应当返回: 3->2->1->4->5

说明 :

你的算法只能使用常数的额外空间。
你不能只是单纯的改变节点内部的值，而是需要实际的进行节点交换。

```

### 思路

我们的思路还是一样的，我们把每 k 位的位置当成是尾节点即可。 我们的任务就是每次反转头尾之间的所有节点，
然后将链表重新拼起来即可。 我们先来写一下`反转头尾之间的所有节点`这个方法。

```js
// 翻转head到tail之间的部分，不包括head和tail
// 返回原链表的第一个元素，也就是翻转后的最后一个元素
function reverseList(head, tail) {
  if (head === null || head.next === null) return head;
  let cur = head.next;
  first = cur;
  let pre = head; // 这里就是翻转不包括head的原因，否则就是head.pre了（当然我们没有pre指针）
  // 这里就是翻转不包括tail的原因，否则就是tail.next了。
  while (cur !== tail) {
    const next = cur.next;
    cur.next = pre;
    pre = cur;
    cur = next;
  }
  // 拼接
  head.next = pre;
  first.next = cur;

  return first;
}
```

这里的反转不包括 head 和 tail，并不是我一开始的思路，但是在慢慢想的过程，发现这样写代码会更优雅。

上面的代码如果是 head 是我们的头节点，tail 是 null，那么就等效于上面的那道题。也就是说我们的这个 k 分组是上面题目的一般形式，当 k 为链表长度的时候，就会变成上面那道题了。

还有一点不同的是，我们每次反转之后都要对链表进行拼接，这是上面那个反转所没有的，这里要注意一下。

```js
head.next = pre;
first.next = cur;
```

这里是对每一组（`k个nodes`）进行翻转，

1. 先分组，用一个`count`变量记录当前节点的个数

2. 用一个`start` 变量记录当前分组的起始节点位置的前一个节点

3. 用一个`end`变量记录要翻转的最后一个节点位置

4. 翻转一组（`k个nodes`）即`(start, end) - start and end exclusively`。

5. 翻转后，`start`指向翻转后链表, 区间`（start，end）`中的最后一个节点, 返回`start` 节点。

6. 如果不需要翻转，`end` 就往后移动一个（`end=end.next`)，每一次移动，都要`count+1`.

如图所示 步骤 4 和 5： 翻转区间链表区间`（start， end）`

![reverse linked list range in (start, end)](https://p.ipic.vip/1entxw.jpg)

举例如图，`head=[1,2,3,4,5,6,7,8], k = 3`

![reverse k nodes in linked list](https://p.ipic.vip/gbfnkm.jpg)

> **NOTE**: 一般情况下对链表的操作，都有可能会引入一个新的`dummy node`，因为`head`有可能会改变。这里`head 从1->3`,
> `dummy (List(0))`保持不变。

这种做法的时间复杂度为 O(n)，空间复杂度为 O(1)。

### 代码

Java 代码：

```java
class ReverseKGroupsLinkedList {
  public ListNode reverseKGroup(ListNode head, int k) {
      if (head == null || k == 1) {
        return head;
      }
      ListNode dummy = new ListNode(0);
      dummy.next = head;

      ListNode start = dummy;
      ListNode end = head;
      int count = 0;
      while (end != null) {
        count++;
        // group
        if (count % k == 0) {
          // reverse linked list (start, end]
          start = reverse(start, end.next);
          end = start.next;
        } else {
          end = end.next;
        }
      }
      return dummy.next;
    }

    /**
     * reverse linked list from range (start, end), return last node.
     * for example:
     * 0->1->2->3->4->5->6->7->8
     * |           |
     * start       end
     *
     * After call start = reverse(start, end)
     *
     * 0->3->2->1->4->5->6->7->8
     *          |  |
     *       start end
     *       first
     *
     */
    private ListNode reverse(ListNode start, ListNode end) {
      ListNode curr = start.next;
      ListNode prev = start;
      ListNode first = curr;
      while (curr != end){
        ListNode temp = curr.next;
        curr.next = prev;
        prev = curr;
        curr = temp;
      }
      start.next = prev;
      first.next = curr;
      return first;
    }
}
```

Python3 代码：

```Python
class Solution:
    def reverseKGroup(self, head: ListNode, k: int) -> ListNode:
        if head is None or k < 2:
            return head
        dummy = ListNode(0)
        dummy.next = head
        start = dummy
        end = head
        count = 0
        while end:
            count += 1
            if count % k == 0:
                start = self.reverse(start, end.next)
                end = start.next
            else:
                end = end.next
        return dummy.next

    def reverse(self, start, end):
        prev, curr = start, start.next
        first = curr
        while curr != end:
            temp = curr.next
            curr.next = prev
            prev = curr
            curr = temp
        start.next = prev
        first.next = curr
        return first

```

JavaScript 代码：

```js
/**
 * Definition for singly-linked list.
 * function ListNode(val) {
 *     this.val = val;
 *     this.next = null;
 * }
 */

// 翻转head到tail之间的部分，不包括head和tail
// 返回原链表的第一个元素，也就是翻转后的最后一个元素
function reverseList(head, tail) {
  if (head === null || head.next === null) return head;
  let cur = head.next;
  first = cur;
  let pre = head; // 这里就是翻转不包括head的原因
  while (cur !== tail) {
    // 这里就是翻转不包括tail的原因
    const next = cur.next;
    cur.next = pre;
    pre = cur;
    cur = next;
  }
  // 拼接
  head.next = pre;
  first.next = cur;

  return first;
}
/**
 * @param {ListNode} head
 * @param {number} k
 * @return {ListNode}
 */
var reverseKGroup = function (head, k) {
  if (head === null || k === 1) {
    return head;
  }

  let cnt = 0;
  const dummy = {
    next: head,
  };
  let start = dummy;
  let end = head;

  while (end !== null) {
    cnt++;
    if (cnt % k !== 0) {
      end = end.next;
    } else {
      start = reverseList(start, end.next);
      end = start.next;
    }
  }

  return dummy.next;
};
```

这里不再赘述，如果不理解，想看更多更详细内容，请参考我的[LeetCode 题解 - 25.reverse-nodes-in-k-groups-cn](https://github.com/azl397985856/leetcode/blob/master/problems/25.reverse-nodes-in-k-groups-cn.md)

## 分组反转 - 增强版

这道题目来自字节跳动面试题。

### 题目描述

要求从后往前以 k 个为一组进行翻转。

例子，1->2->3->4->5->6->7->8, k = 3,

从后往前以 k=3 为一组，

6->7->8 为一组翻转为 8->7->6，
3->4->5 为一组翻转为 5->4->3.
1->2 只有 2 个 nodes 少于 k=3 个，不翻转。
最后返回： 1->2->5->4->3->8->7->6

### 思路

这里的思路跟从前往后以`k`个为一组进行翻转类似，可以进行预处理：

1. 翻转链表

2. 对翻转后的链表进行从前往后以 k 为一组翻转。

3. 翻转步骤 2 中得到的链表。

例子：`1->2->3->4->5->6->7->8, k = 3`

1. 翻转链表得到：`8->7->6->5->4->3->2->1`

2. 以 k 为一组翻转： `6->7->8->3->4->5->2->1`

3. 翻转步骤#2 链表： `1->2->5->4->3->8->7->6`

## 类似题目

- [Swap Nodes in Pairs](https://leetcode.com/problems/swap-nodes-in-pairs/)
