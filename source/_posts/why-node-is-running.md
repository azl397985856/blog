---
title: 为什么我的 node 进程一直在运行？
tags: [前端, node]
categories: [前端]
date: 2024-08-10
---

有时候我们打开进程管理器，发现 node 进程一直在运行，但是我们并不知道它在做什么。

如果通过不停打日志的方式来找出原因，会非常耗时，而且不一定能找到问题所在。因为一个异步操作可能是由于另外一个异步操作触发的，这样就会导致我们很难找到根本原因，或者说定位过程会非常艰难。 ` 那么有没有一种更有效率的方法可以帮助我们找出为什么 node 进程一直在运行呢？

<!-- more -->

## 什么是 async_hooks

要回答这个问题，首先我们需要了解 Node.js 的  `async_hooks`  内置模块。这个模块提供了一组 API，可以用来跟踪异步操作。

例如，我们可以使用  `async_hooks`  来跟踪异步操作的创建和销毁，以及它们之间的关系。这样，我们就可以知道哪些异步操作还在运行，哪些已经结束了。

代码示例：

```js
const async_hooks = require("async_hooks");

const hook = async_hooks.createHook({
  /**
   * 当一个异步操作被创建时，会调用这个方法。
   * @param {number} asyncId 异步操作的唯一标识符。
   * @param {string} type 异步操作的类型。枚举值有：'PROMISE'、'TIMER'、'IMMEDIATE'、'MICROTASK'、'ASYNC_RESOURCE'。
   * @param {number} triggerAsyncId 触发这个异步操作的异步操作的唯一标识符。
   * @param {Object} resource 异步操作的资源对象。比如，如果是一个 Promise，这个对象就是 Promise 对象本身。
   */
  init(asyncId, type, triggerAsyncId, resource) {},
  /**
   * 当一个异步操作被销毁时，会调用这个方法。
   * @param {number} asyncId 异步操作的唯一标识符。
   */
  destroy(asyncId) {},
});

hook.enable(); // 启用钩子。可以在之后调用 hook.disable() 来禁用钩子。
```

如上代码，创建异步操作的时候会调用  `init`  方法，销毁异步操作的时候会调用  `destroy`  方法。

## 实现原理

有了前面的铺垫，我们就可以来解决这个问题了。

以下是一个简化的示例，展示了如何使用  `async_hooks`  来跟踪异步操作：

```js
const async_hooks = require("async_hooks");
const stackTraces = new Map();
const hook = async_hooks.createHook({
  init(asyncId, type, triggerAsyncId, resource) {
    // 在新的异步操作被创建时，记录堆栈跟踪
    stackTraces.set(asyncId, new Error().stack);
  },
  destroy(asyncId) {
    // 在异步操作被关闭时，删除记录
    stackTraces.delete(asyncId);
  },
});
hook.enable();
// 一段时间后...
setTimeout(() => {
  // 打印所有仍然活跃的异步操作的堆栈跟踪
  for (const stackTrace of stackTraces.values()) {
    console.log(stackTrace);
  }
}, 1000);
```

这个一段时间可以变为手动控制，比如等我们发送一个用户信号 `SIGUSR1` 的时候，我们就可以打印出所有的异步操作的堆栈跟踪。

## 思考

社区中已经有一些现成的实现了，比如  [why-is-node-running](https://github.com/mafintosh/why-is-node-running)。它的实现和我们上面的一样， 很简单就可以实现这样的功能。之所以能够做到这一点，是因为 Node.js 提供了  `async_hooks`  这个内置模块。也就是说我们只要站到巨人的肩膀上，就可以很容易地实现这样的功能。这提示我们对框架和库提供的底层基本原理有一定的了解，这样我们就可以更好地利用它们，提高我们的工作效率。很多复杂的库都是基于简单的原理实现的，只要我们掌握了这些原理，就可以很容易地理解它们的工作原理，从而更好地使用它们。只不过由于越来越流行，而不得不增加了很多的功能，修复了很多 bug，这样就会导致我们很难理解它们的工作原理，这就需要我们花费更多的时间去学习它们。

留给大家一个思考题。如果不使用 node 内置的  `async_hooks`  模块，我们还可以通过什么方式来实现这样的功能呢？这种方法和  `async_hooks`  相比，有什么优缺点呢？欢迎大家留言讨论。

## 总结

通过这篇文章，我们了解了 Node.js 的  `async_hooks`  内置模块，以及如何使用它来跟踪异步操作。我们还展示了如何使用  `async_hooks`  来找出为什么 Node.js 进程一直在运行。最后，我们讨论了如何站在巨人的肩膀上，更好地利用框架和库提供的底层基本原理，从而提高我们的工作效率。


