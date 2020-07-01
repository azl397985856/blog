# Loading 最佳实践

loading 相信大家都遇到过这样的需求。然而 loading 的交互形式有很多，技术实现上也各种各样。网上看到的资料也是各种各样的，很少有系统性的学习资料。因此我打算自己写一篇。

这篇文章回答几个问题：

- 什么时候应该使用 loading
- 怎么使用 loading
- 不同的框架不同终端的交互和实现形式有什么不同？本文带你走进这些问题。

## 什么时候应该用 loading

简单来说， 一切需要用户等待的地方都可能需要 loading。

上面这句话有两个核心点：

### 需要用户等待

代码运行都是需要时间的，即使只有一行代码，也是需要时间来执行的。实际上需要用户等待这句话更准确地说应该是用户可感知的等待。如果用户只需要等待几 ms，实际上是无感知的。具体多少 ms 用户可以感知到， 这个是有专门的研究数据的，大家可以网上搜索一下。

另外需要说明的是，不同的应用对“可感知时间”是不同的。比如一个即时战略游戏和一个查询成绩的网站来说“可感知时间”就不等的。因此“用户可感知时间”并不是一个静态的参考值，而是随着具体的情景变化的变量。

但是并不是说一个长时的任务一定就需要 loading，比如接下来要讲的同步任务。

### 可能需要（可能不需要）

上面说了，**时间长到可感知就可能需要 loading 来给予用户一种反馈了**。但是也有例外的情况：

1. 同步任务不需要 loading

由于浏览器执行 JS 代码的线程和绘制的线程会相互阻塞。因此理论上同步的长时间执行的代码不需要 loading。

> 当然我们应该尽量避免这种情况。 比如转移到 webworker，或者使用诸如 requestIdleCallback 等浏览器 API

如下代码，会让浏览器卡死，如果这个时候增加 loading ，是不会有可感知效果的。

```js
import React, { useState } from "react";

function waitSync(seconds: number) {
  const start = new Date().getTime();

  while (new Date().getTime() - start < seconds * 1000) {}
}

function App() {
  const [isloading, setLoading] = useState(false);
  return (
    <div className="App">
      <div>{isloading ? "loading" : "lucifer"}</div>
      <button
        onClick={() => {
          setLoading(true);
          waitSync(5);
          setLoading(false);
        }}
      >
        点我让你卡死三秒
      </button>
    </div>
  );
}

export default App;
```

2. 不重要内容不需要 loading

比如一个文章详情页面，其中文章内容是主要内容，可以增加 loading。但是文章导航这种不需要第一时间加载出来的东西，但是却是在首屏出现的，我们也可以不增加 loading 或者延迟增加 loading，比如 5 s 还没返回再增加 loading。

如果页面上 loading 太多，可能给用户一种慢的感觉。因此要**只在必要的时候增加 loading**。

3. 重要内容但是存在存在重叠关系的， 被覆盖的部分可以不 loading。

### 一个容器

我在[你不知道的 TypeScript 泛型（万字长文，建议收藏）](https://lucifer.ren/blog/2020/06/16/ts-generics/) 提到了 “我们平时开发都是对值进行编程”。

而实际上我们需要用户等待的情况根本原因是“值还没有准备好，并且需要一定的时间来完成”。值可能在未来的某一个时刻到达，在这个时刻到达之前这个动作无法进行下去， 用户就需要等待。

```js
// 1. initial state, so we have to wait
const data = {};
// 2. later, data comes
data = {
  name: "lucfer",
  age: 17,
};
// 3. now we can go on
```

如果上面的步骤 1 很慢，你可能需要增加 loading 来抚慰用户“在取数据了，马上好”。

比如我们要发送一个 HTTP 请求获取数据：

```js
data = await fetch("http://www.lucifer.ren/about");

data.isloading; // ?
!data; // ?
```

data 指的是未来 HTTP 会返回的数据。我们是否可以在上面挂在 loading 属性来表示当前请求正在进行呢？我们是否可以判断 data 是否存在来表示当前请求正在进行呢？

这是不行的。因为增加 loading 会破坏 data 的数据结构，更严重的是可能会键冲突。 判断 data 是否为空也是行不通的，因为这个依赖一个前提“真正值返回之前，data 是 Falsy 的”。也就是说 data 的初始值不能是 {}, [] 等 truthy。

在很久之前，Promise 尚未普及，jQuery 1.5.0 版本开始引入的一个新功能----deferred 对象， 主要是为了解决 jQuery 的回调函数使用不便的问题。但是本文要讲的并不是 jq 的 defered，而是我自己发明的一个数据结构，只是名字恰好一样。

```js
defered = defer(fetch("https://api.github.com/users/azl397985856"));
defered.isloading;
defered.then(console.log);
defered.catch(console.error);
```

如上， defer 接受一个 Promise，返回一个形如：

```js
{
  isloading: true,
  data: {},
  error: null
}

```

的对象。

这样我们可以从 data 中获取数据， 从 isloading 中获取是否正在 loading，从 error 获取是否失败已经失败的原因。

我们现在就来实现一下这个神秘的 defer 方法。

```js
const defer = (p) => {
  p.isloading = true;
  return p
    .then((data) => ({ isloading: false, data, error: null }))
    .catch((error) => ({
      isloading: false,
      data: null,
      error,
    }));
};
```

## 怎么使用 loading

## 各种各样的 loading

## 全自动 loading

## 小提示

短暂间隔的连续 loadng 可以考虑合并
