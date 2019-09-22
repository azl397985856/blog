# 一文搞懂《链表翻转》


## 分组翻转

[25. K 个一组翻转链表](https://leetcode-cn.com/problems/reverse-nodes-in-k-group/)

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

### 代码
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
var reverseKGroup = function(head, k) {
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
