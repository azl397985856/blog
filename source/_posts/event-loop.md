---
title: 《一文看懂浏览器事件循环》
tags: [前端, 浏览器, 事件循环]
date: 2019-12-11
categories:
  - [前端, 浏览器]
---

实际上浏览器的事件循环标准是由 HTML 标准规定的，具体来说就是由 whatwg 规定的，具体内容可以参考[event-loops in browser](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops)。而 NodeJS 中事件循环其实也略有不同，具体可以参考[event-loops in nodejs](https://nodejs.org/en/docs/guides/event-loop-timers-and-nexttick/#what-is-the-event-loop)

我们在讲解`事件模型`的时候，多次提到了事件循环。 `事件`指的是其所处理的对象就是事件本身，每一个浏览器都至少有一个事件循环，一个事件循环至少有一个任务队列。`循环`指的是其永远处于一个“无限循环”中。不断将注册的回调函数推入到执行栈。

那么事件循环究竟是用来做什么的？浏览器的事件循环和 NodeJS 的事件循环有什么不同？让我们从零开始，一步一步探究背后的原因。

<!-- more -->

## 为什么要有事件循环

### JS 引擎

要回答这个问题，我们先来看一个简单的例子：

```js
function c() {}
function b() {
  c();
}
function a() {
  b();
}
a();
```

以上一段简单的 JS 代码，究竟是怎么被浏览器执行的？

首先，浏览器想要执行 JS 脚本，需要一个“东西”，将 JS 脚本（本质上是一个纯文本），变成一段机器可以理解并执行的计算机指令。这个“东西”就是 JS 引擎，它实际上会将 JS 脚本进行编译和执行，整个过程非常复杂，这里不再过多介绍，感兴趣可以期待下我的 V8 章节，如无特殊说明，以下都拿 V8 来举例子。

有两个非常核心的构成，`执行栈`和`堆`。执行栈中存放正在执行的代码，堆中存放变量的值，通常是不规则的。

当 V8 执行到`a()`这一行代码的时候，a 会被压入栈顶。

![](https://p.ipic.vip/820jqx.jpg)

在 a 的内部，我们碰到了`b()`，这个时候 b 被压入栈顶。

![](https://p.ipic.vip/22i029.jpg)

在 b 的内部，我们又碰到了`c()`，这个时候 c 被压入栈顶。

![](https://p.ipic.vip/ers145.jpg)

c 执行完毕之后，会从栈顶移除。

![](https://p.ipic.vip/22i029.jpg)

函数返回到 b，b 也执行完了，b 也从栈顶移除。

![](https://p.ipic.vip/820jqx.jpg)

同样 a 也会被移除。

![](https://p.ipic.vip/0hk2wd.jpg)

整个过程用动画来表示就是这样的：

![](https://p.ipic.vip/romqox.gif)
([在线观看](http://latentflip.com/loupe/?code=ZnVuY3Rpb24gYygpIHt9CmZ1bmN0aW9uIGIoKSB7CgljKCk7Cn0KZnVuY3Rpb24gYSgpIHsKCWIoKTsKfQphKCk7!!!))

这个时候我们还没有涉及到`堆内存`和`执行上下文栈`，一切还比较简单，这些内容我们放到后面来讲。

### DOM 和 WEB API

现在我们有了可以执行 JS 的引擎，但是我们的目标是`构建用户界面`，而传统的前端用户界面是基于 DOM 构建的，因此我们需要引入 DOM。DOM 是`文档对象模型`，其提供了一系列 JS 可以直接调用的接口，理论上其可以提供其他语言的接口，而不仅仅是 JS。 而且除了 DOM 接口可以给 JS 调用，浏览器还提供了一些 WEB API。 DOM 也好，WEB API 也好，本质上和 JS 没有什么关系，完全不一回事。JS 对应的 ECMA 规范，V8 用来实现 ECMA 规范，其他的它不管。 这也是 JS 引擎和 JS 执行环境的区别，V8 是 JS 引擎，用来执行 JS 代码，浏览器和 Node 是 JS 执行环境，其提供一些 JS 可以调用的 API 即`JS bindings`。

由于浏览器的存在，现在 JS 可以操作 DOM 和 WEB API 了，看起来是可以构建用户界面啦。 有一点需要提前讲清楚，V8 只有栈和堆，其他诸如事件循环，DOM，WEB API 它一概不知。原因前面其实已经讲过了，因为 V8 只负责 JS 代码的编译执行，你给 V8 一段 JS 代码，它就从头到尾一口气执行下去，中间不会停止。

另外这里我还要继续提一下，JS 执行栈和渲染线程是相互阻塞的。为什么呢？ 本质上因为 JS 太灵活了，它可以去获取 DOM 中的诸如坐标等信息。 如果两者同时执行，就有可能发生冲突，比如我先获取了某一个 DOM 节点的 x 坐标，下一时刻坐标变了。 JS 又用这个“旧的”坐标进行计算然后赋值给 DOM，冲突便发生了。 解决冲突的方式有两种：

1. 限制 JS 的能力，你只能在某些时候使用某些 API。 这种做法极其复杂，还会带来很多使用不便。
2. JS 和渲染线程不同时执行就好了，一种方法就是现在广泛采用的`相互阻塞`。 实际上这也是目前浏览器广泛采用的方式。

### 单线程 or 多线程 or 异步

前面提到了`你给V8一段JS代码，它就从头到尾一口气执行下去，中间不会停止`。 为什么不停止，可以设计成可停止么，就好像 C 语言一样？

假设我们需要获取用户信息，获取用户的文章，获取用的朋友。

#### 单线程无异步

由于是单线程无异步，因此我们三个接口需要采用同步方式。

```js
fetchUserInfoSync().then(doSomethingA); // 1s
fetchMyArcticlesSync().then(doSomethingB); // 3s
fetchMyFriendsSync().then(doSomethingC); // 2s
```

由于上面三个请求都是同步执行的，因此上面的代码会先执行`fetchUserInfoSync`，一秒之后执行`fetchMyArcticlesSync`，再过三秒执行`fetchMyFriendsSync`。 最可怕的是我们刚才说了`JS执行栈和渲染线程是相互阻塞的`。 因此用户就在这期间根本无法操作，界面无法响应，这显然是无法接受的。

#### 多线程无异步

由于是多线程无异步，虽然我们三个接口仍然需要采用同步方式，但是我们可以将代码分别在多个线程执行，比如我们将这段代码放在三个线程中执行。

线程一：

```js
fetchUserInfoSync().then(doSomethingA); // 1s
```

线程二：

```js
fetchMyArcticlesSync().then(doSomethingB); // 3s
```

线程三：

```js
fetchMyFriendsSync().then(doSomethingC); // 2s
```

![1575538849801.jpg](https://p.ipic.vip/ujasyp.jpg)

由于三块代码同时执行，因此总的时间最理想的情况下取决与最慢的时间，也就是 3s，这一点和使用异步的方式是一样的（当然前提是请求之间无依赖）。为什么要说最理想呢？由于三个线程都可以对 DOM 和堆内存进行访问，因此很有可能会冲突，冲突的原因和我上面提到的 JS 线程和渲染线程的冲突的原因没有什么本质不同。因此最理想情况没有任何冲突的话是 3s，但是如果有冲突，我们就需要借助于诸如`锁`来解决，这样时间就有可能高于 3s 了。 相应地编程模型也会更复杂，处理过锁的程序员应该会感同身受。

#### 单线程 + 异步

如果还是使用单线程，改成异步是不是会好点？问题的是关键是如何实现异步呢？这就是我们要讲的主题 - `事件循环`。

## 事件循环究竟是怎么实现异步的？

我们知道浏览器中 JS 线程只有一个，如果没有事件循环，就会造成一个问题。 即如果 JS 发起了一个异步 IO 请求，在等待结果返回的这个时间段，后面的代码都会被阻塞。 我们知道 JS 主线程和渲染进程是相互阻塞的，因此这就会造成浏览器假死。 如何解决这个问题？ 一个有效的办法就是我们这节要讲的`事件循环`。

其实`事件循环就是用来做调度的，浏览器和NodeJS中的事件循坏就好像操作系统的调度器一样。`操作系统的调度器决定何时将什么资源分配给谁。对于有线程模型的计算机，那么操作系统执行代码的最小单位就是线程，资源分配的最小单位就是进程，代码执行的过程由操作系统进行调度，整个调度过程非常复杂。 我们知道现在很多电脑都是多核的，为了让多个 core 同时发挥作用，即没有一个 core 是特别闲置的，也没有一个 core 是特别累的。操作系统的调度器会进行某一种神秘算法，从而保证每一个 core 都可以分配到任务。 这也就是我们使用 NodeJS 做集群的时候，Worker 节点数量通常设置为 core 的数量的原因，调度器会尽量将每一个 Worker 平均分配到每一个 core，当然这个过程并不是确定的，即不一定调度器是这么分配的，但是很多时候都会这样。

了解了操作系统调度器的原理，我们不妨继续回头看一下事件循环。 事件循环本质上也是做调度的，只不过调度的对象变成了 JS 的执行。事件循环决定了 V8 什么时候执行什么代码。`V8只是负责JS代码的解析和执行，其他它一概不知。`浏览器或者 NodeJS 中触发事件之后，到事件的监听函数被 V8 执行这个时间段的所有工作都是事件循环在起作用。

我们来小结一下：

1. 对于 V8 来说，它有：

- 调用栈（call stack）
  > 这里的单线程指的是只有一个 call stack。只有一个 call stack 意味着同一时间只能执行一段代码。
- 堆（heap）

2. 对于浏览器运行环境来说：

- WEB API
- DOM API
- 任务队列

> 事件来触发事件循环进行流动

以如下代码为例：

```js
function c() {}
function b() {
  c();
}
function a() {
  setTimeout(b, 2000);
}
a();
```

执行过程是这样的：

![](https://p.ipic.vip/p5lxfj.gif)
([在线观看](http://latentflip.com/loupe/?code=ZnVuY3Rpb24gYygpIHt9CmZ1bmN0aW9uIGIoKSB7CgljKCk7Cn0KZnVuY3Rpb24gYSgpIHsKCXNldFRpbWVvdXQoYiwgMjAwMCkKfQphKCk7!!!))

因此事件循环之所以可以实现异步，是因为碰到异步执行的代码“比如 fetch，setTimeout”，浏览器会将用户注册的回调函数存起来，然后继续执行后面的代码。等到未来某一个时刻，“异步任务”完成了，会触发一个事件，浏览器会将“任务的详细信息”作为参数传递给之前用户绑定的回调函数。具体来说，就是将用户绑定的回调函数推入浏览器的执行栈。

但并不是说随便推入的，只有浏览器将当然要执行的 JS 脚本“一口气”执行完，要”换气“的时候才会去检查有没有要被处理的“消息”。
如果于则将对应消息绑定的回调函数推入栈。当然如果没有绑定事件，这个事件消息实际上会被丢弃，不被处理。比如用户触发了一个 click 事件，但是用户没有绑定 click 事件的监听函数，那么实际上这个事件会被丢弃掉。

我们来看一下加入用户交互之后是什么样的，拿点击事件来说：

```js
$.on("button", "click", function onClick() {
  setTimeout(function timer() {
    console.log("You clicked the button!");
  }, 2000);
});

console.log("Hi!");

setTimeout(function timeout() {
  console.log("Click the button!");
}, 5000);

console.log("Welcome to loupe.");
```

上述代码每次点击按钮，都会发送一个事件，由于我们绑定了一个监听函数。因此每次点击，都会有一个点击事件的消息产生，浏览器会在“空闲的时候”对应将用户绑定的事件处理函数推入栈中执行。

伪代码:

```js
while (true) {
  if (queue.length > 0) {
    queue.processNextMessage();
  }
}
```

动画演示：

![](https://p.ipic.vip/fy5ifj.gif)
([在线观看](http://latentflip.com/loupe/?code=JC5vbignYnV0dG9uJywgJ2NsaWNrJywgZnVuY3Rpb24gb25DbGljaygpIHsKICAgIHNldFRpbWVvdXQoZnVuY3Rpb24gdGltZXIoKSB7CiAgICAgICAgY29uc29sZS5sb2coJ1lvdSBjbGlja2VkIHRoZSBidXR0b24hJyk7ICAgIAogICAgfSwgMjAwMCk7Cn0pOwoKY29uc29sZS5sb2coIkhpISIpOwoKc2V0VGltZW91dChmdW5jdGlvbiB0aW1lb3V0KCkgewogICAgY29uc29sZS5sb2coIkNsaWNrIHRoZSBidXR0b24hIik7Cn0sIDUwMDApOwoKY29uc29sZS5sb2coIldlbGNvbWUgdG8gbG91cGUuIik7!!!PGJ1dHRvbj5DbGljayBtZSE8L2J1dHRvbj4%3D))

### 加入宏任务&微任务

我们来看一个更复制的例子感受一下。

```js
console.log(1);

setTimeout(() => {
  console.log(2);
}, 0);

Promise.resolve()
  .then(() => {
    return console.log(3);
  })
  .then(() => {
    console.log(4);
  });

console.log(5);
```

上面的代码会输出：1、5、3、4、2。 如果你想要非常严谨的解释可以参考 whatwg 对其进行的描述 -[event-loop-processing-model](https://html.spec.whatwg.org/multipage/webappapis.html#event-loop-processing-model)。

下面我会对其进行一个简单的解释。

- 浏览器首先执行宏任务，也就是我们 script（仅仅执行一次）
- 完成之后检查是否存在微任务，然后不停执行，直到清空队列
- 执行宏任务

其中：

宏任务主要包含：setTimeout、setInterval、setImmediate、I/O、UI 交互事件

微任务主要包含：Promise、process.nextTick、MutaionObserver 等

![](https://p.ipic.vip/vupgds.jpg)

有了这个知识，我们不难得出上面代码的输出结果。

由此我们可以看出，`宏任务&微任务`只是实现异步过程中，我们对于信号的处理顺序不同而已。如果我们不加区分，全部放到一个队列，就不会有`宏任务&微任务`。这种人为划分优先级的过程，在某些时候非常有用。

### 加入执行上下文栈

说到执行上下文，就不得不提到`浏览器执行JS函数其实是分两个过程的`。一个是创建阶段`Creation Phase`,一个是执行阶段`Execution Phase`。

同执行栈一样，浏览器每遇到一个函数，也会将当前函数的执行上下文栈推入栈顶。

举个例子：

```js
function a(num) {
  function b(num) {
    function c(num) {
      const n = 3;
      console.log(num + n);
    }
    c(num);
  }
  b(num);
}
a(1);
```

遇到上面的代码。 首先会将 a 的压入执行栈，我们开始进行创建阶段`Creation Phase`， 将 a 的执行上下文压入栈。然后初始化 a 的执行上下文，分别是 VO，ScopeChain（VO chain）和 This。 从这里我们也可以看出，this 其实是动态决定的。VO 指的是`variables, functions 和 arguments`。 并且执行上下文栈也会同步随着执行栈的销毁而销毁。

伪代码表示：

```js
const EC = {
  scopeChain: {},
  variableObject: {},
  this: {},
};
```

![](https://p.ipic.vip/d6z9cb.jpg)

我们来重点看一下 ScopeChain(VO chain)。如上图的执行上下文大概长这个样子，伪代码：

```js

global.VO = {
    a: pointer to a(),
    scopeChain: [global.VO]
}

a.VO = {
    b: pointer to b(),
    arguments: {
		0: 1
	},
    scopeChain: [a.VO, global.VO]
}

b.VO = {
	c: pointer to c(),
	arguments: {
		0: 1
	},
	scopeChain: [b.VO, a.VO, global.VO]
}
c.VO = {
	arguments: {
		0: 1
	},
	n: 3
	scopeChain: [c.VO, b.VO, a.VO, global.VO]
}
```

引擎查找变量的时候，会先从 VOC 开始找，找不到会继续去 VOB...，直到 GlobalVO，如果 GlobalVO 也找不到会返回`Referrence Error`，整个过程类似原型链的查找。

值得一提的是，JS 是词法作用域，也就是静态作用域。换句话说就是作用域取决于代码定义的位置，而不是执行的位置，`这也就是闭包产生的本质原因`。 如果上面的代码改造成下面的：

```js
function c() {}
function b() {}
function a() {}
a();
b();
c();
```

或者这种：

```js
function c() {}
function b() {
  c();
}
function a() {
  b();
}
a();
```

其执行上下文栈虽然都是一样的，但是其对应的 scopeChain 则完全不同，因为函数定义的位置发生了变化。拿上面的代码片段来说,c.VO 会变成这样：

```js
c.VO = {
  scopeChain: [c.VO, global.VO],
};
```

也就是说其再也无法获取到 a 和 b 中的 VO 了。

## 总结

通过这篇文章，希望你对单线程，多线程，异步，事件循环，事件驱动等知识点有了更深的理解和感悟。除了这些大的层面，我们还从执行栈，执行上下文栈角度讲解了我们代码是如何被浏览器运行的，我们顺便还解释了作用域和闭包产生的本质原因。

最后我总结了一个浏览器运行代码的整体原理图，希望对你有帮助：

![](https://p.ipic.vip/gepbz4.jpg)

下一节`浏览器的事件循环和NodeJS的事件循环有什么不同`, 敬请期待～

## 参考

- [Node.js event loop - logrocket](https://blog.logrocket.com/a-complete-guide-to-the-node-js-event-loop/)
- [event-loop - nodejs.org](https://nodejs.org/de/docs/guides/event-loop-timers-and-nexttick/)
- [what-is-the-execution-context-in-javascript](http://davidshariff.com/blog/what-is-the-execution-context-in-javascript/)
- [Event Loop in JS - youtube ](https://www.youtube.com/watch?v=8aGhZQkoFbQ)
