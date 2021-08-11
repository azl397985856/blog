---
title: 你不知道的 LeetCode 技巧（第一篇）
tags: [LeetCode, 刷题技巧]
date: 2021-08-06
categories:
  - [LeetCode, 刷题技巧]
---

今天来给使用 **JS 刷题**的朋友分享**三个** LeetCode 上你或许不知道的刷题技巧。

<!-- more -->

## tip1 - ES6+

首先穿插一个小知识：`我们提交的 JS 是如何被 LeetCode 执行的？`

我们在力扣提交的代码是放到力扣后台运行的， 而 JS 代码在力扣后台是在 node 中以 --harmony 方式运行的。

大概是这样：

```js
node --harmony  index.js
```

其中 index.js 就是你提交的代码。

比如：

```js
// 前面 LeetCode 会添加一些代码
function sum(a, b) {
  // you code
}

// 这里是 LeetCode 的测试用例
expect(sum(1, 2)).toBe(3);
expect(sum(1, 8)).toBe(9); // 如果测试用例不通过，则直接抛出错误给前端
```

因此 ES6 特性是完全支持的，大家可以放心使用。

比如我们可以使用 ES6 的解构语法完成数组两个值的交换。

```js
[a, b] = [b, a];
```

如下就是使用了 ES6 的数组解构语法，更多 ES6+ 请参考相关文档。

## tip2 - lodash

在 LeetCode 中 [lodash](https://lodash.com/ "lodash") 默认可直接通过 `_` 访问。

这是因为 LeetCode 直接将 lodash require 进来了。类似：

```js
const _ = require("lodash");

// 前面 LeetCode 会添加一些代码
function sum(a, b) {
  // you code
  // 你的代码可以通过 _ 访问到 lodash 的所有功能。
}

// 这里是 LeetCode 的测试用例
expect(sum(1, 2)).toBe(3);
expect(sum(1, 8)).toBe(9); // 如果测试用例不通过，则直接抛出错误给前端
```

lodash 有很多有用的功能可直接使用。西法建议你**如果让你手写你能够写出，那么就可以放心的使用 lodash 提供的功能**。

比如数组拍平：

```js
_.flatten([1, [2, [3, [4]], 5]]);
// => [1, 2, [3, [4]], 5]
```

再比如深拷贝：

```js
var objects = [{ a: 1 }, { b: 2 }];

var deep = _.cloneDeep(objects);
console.log(deep[0] === objects[0]);
// => false
```

更多 API 可参考官方文档。

## tip3 - queue & priority-queue

为了弥补 JS 内置数据结构的缺失。除了 JS 内置数据结构之外，LeetCode 平台还对 JS 提供了两种额外的数据结构，它们分别是:

- queue
- priority-queue

这两个数据结构都使用的是第三方 `datastructures-js` 实现的版本，代码我看过了，还是很容易看懂的。

### queue

LeetCode 提供了 JS 对队列的支持。

```js
// empty queue
const queue = new Queue();

// from an array
const queue = new Queue([1, 2, 3]);
```

其中 queue 的实现也是使用数组模拟。不过不是直接使用 shift 来删除头部元素，因为直接使用 shift 删除最坏情况时间复杂度是 $O(n)$。这里它使用了一种标记技巧，即每次删除头部元素并不是真的移除，而是标记其已经被移除。

这种做法时间复杂度可以降低到 $O(1)$。只不过如果不停入队和出队，空间复杂度会很高，因为会保留所有的已经出队的元素。因此它会在每次出队超过一半的时候执行一次**缩容**（类似于数组扩容）。这样时间复杂度会增大到 $O(logn)$，但是空间会省。

详细用法可以参考：https://github.com/datastructures-js/queue

另外西法我自己实现了一套 queue，我是使用链表实现的，理论上**复杂度更好**，插入和删除时间复杂度都是 O(1)，也不会有空间的浪费，核心代码就**20 行**。但实际使用的话性能不一定谁好，为什么呢，大家可以思考一下？

- [西法自己实现的 deque](https://github.com/azl397985856/js-algorithm-light/blob/master/deque.js "西法自己实现的 deque")

### priority-queue

除了普通队列，LeetCode 还提供了一种特殊的队列 - 优先队列。

```js
// empty queue with default priority the element value itself.
const numbersQueue = new MinPriorityQueue();

// empty queue, will provide priority in .enqueue
const patientsQueue = new MinPriorityQueue();

// empty queue with priority returned from a prop of the queued object
const biddersQueue = new MaxPriorityQueue({ priority: (bid) => bid.value });
```

priority-queue 的 api 则可以参考 https://github.com/datastructures-js/priority-queue

同样，西法也实现了堆，大家可以参考一下。

- [西法自己实现的 heap](https://github.com/azl397985856/js-algorithm-light/blob/master/heap.js "西法自己实现的 heap")

值得一提的是，西法还实现了一些堆的高级功能，详情参考 [indexed_priority_queue](https://github.com/azl397985856/js-algorithm-light/blob/master/indexed_priority_queue.js "西法自己实现的 indexed_priority_queue")

## 总结

LeetCode 对 JS 的支持主要有：

- ES6+ 语法的支持
- 内置 lodash 库，可直接通过 `_` 来使用其上的功能函数。
- 内置数据结构支持队列和优先队列。

文中提到的我自己实现的数据结构代码来自 js-algorithm-light，它是轻量级的 JavaScript 数据结构与算法库。为了让使用 JS 刷题的朋友学习和使用一些常用的数据结构，我开辟了这个仓库，暂定的目标是对标 Python 所有的内置数据结构和算法。

贴一下西法已经实现的数据结构。

![](https://tva1.sinaimg.cn/large/008i3skNly1gt69et5delj31560lw40v.jpg)

求个一键三连支持一下，点赞多的话西法立马就安排下一篇。下一次给大家分享几个 **你不知道的 LeetCode 通用小技巧**。
