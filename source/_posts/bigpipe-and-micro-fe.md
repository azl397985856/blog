---
title: BigPipe和微前端
tags: [BigPipe, 微前端]
date: 2020-02-02
---

你可能听说过 BigPipe，这是一个十多年前的技术，而 BigPipe 通常都会跟“性能优化”同时被提起。微前端也是一个很早被提出的技术，但是最近几年才开始比较流行。而目前微前端能够解决的最大的问题恐怕就是遗留系统改造。我们可以将新技术构造的系统和旧技术构造的系统完美融合到一起，彼此构建，发布，运行等不受干扰。 那么 BigPipe 究竟和微前端有什么关系呢，我为什么要把这两个放到一起来看？

<!-- more -->

回答这个问题之前，我们先来看下什么是 BigPipe，以及什么是微前端。

## BigPipe

BigPipe 最早上 FaceBook 用来提升自家网站性能的一个秘密武器。其核心思想在于将页面分成若干小的构件，我们称之为 pagelet。每一个构件之间并行执行。

那么 BigPipe 做了什么？和传统方式有什么不同呢？我们知道浏览器处理我们的 HTML 文档以及其中包含的 CSS，JS 等资源的时候是从上到下串行执行的。如果我们把浏览器处理的过程划分为若干阶段（stage），那么这些阶段之间有着明显的时间先后关系。那么我们能不能将其并行化，从而减少时间呢？这就是 BigPipe 的基本思想。

话不多说，我们通过一段代码来帮助大家理解,比如你的项目首页是 home.html，大概这样子：

```html
<!DOCTYPE html>
<html>
  <head>
    <script>
      window.BigPipe = {
        render(selector, content) {
          document.querySelector(selector).innerHTML = content;
        }
      };
    </script>
  </head>
  <body>
    <div id="pagelet1"></div>
    <div id="pagelet2"></div>
    <div id="pagelet3"></div>
  </body>
</html>
```

浏览器首先加载过来就是一个占位元素，这部分没有 JS 和 CSS，只有 HTML 部分，因此会很快。

之后我们慢慢填充`pagelet1`,`pagelet2`, `pagelet3`,在用户看来，就是一种“渐进式渲染”的效果。

服务端代码大概是：

```js
const app = require('express')();
const fs = require('fs');

// 模拟真实场景
function wirteChunk(content, delay, res) {
    return new Promise(r => {
        setTimeout(function() {
            res.write(content);
        delay);
    })
}

app.get('/', function (req, res) {
  // 为了简化代码，直接同步读。 强烈不建议生产环境这么做！
  res.write(fs.readFileSync(__dirname + "/home.html").toString());

  const p1 = wirteChunk('<script>BigPipe.render("#pagelet1","hello");</script>', 1000)
  const p2 = wirteChunk('<script>BigPipe.render("#pagelet2","word");</script>', 2000)
  const p3 = wirteChunk('<script>BigPipe.render("#pagelet3","!");</script>', 3000)

  Promise.all([p1, p2, p3]).then(res.end)

});

app.listen(3000);
```

从这里我们可以看出，BigPipe 不是框架，不是新技术。我们只需要按照这样做就行了。 这对于页面可以细分为多个块，块之间关联不大的场景非常有用。如果还是不太明白，可以看下这篇文章 -[bigpipe-pipelining-web-pages-for-high-performance](https://www.facebook.com/notes/facebook-engineering/bigpipe-pipelining-web-pages-for-high-performance/389414033919/)

说完了 BigPipe，我们再来看一下微前端。

## 微前端

和后端微服务类似，“微前端是一种架构风格，其中众多独立交付的前端应用组合成一个大型整体。”

如果你想做微前端，一定要能够回答出这 10 个问题。

1. 微应用的注册、异步加载和生命周期管理；
2. 微应用之间、主从之间的消息机制；
3. 微应用之间的安全隔离措施；
4. 微应用的框架无关、版本无关；
5. 微应用之间、主从之间的公共依赖的库、业务逻辑(utils)以及版本怎么管理；
6. 微应用独立调试、和主应用联调的方式，快速定位报错（发射问题）；
7. 微应用的发布流程；
8. 微应用打包优化问题；
9. 微应用专有云场景的出包方案；
10. 渐进式升级：用微应用方案平滑重构老项目。

这里有一篇文档，区别与别的微前端文章的点在于其更加靠近规范层面，而不是结合自己的业务场景做的探索。这篇文章来自于阿里团队。

![](https://tva1.sinaimg.cn/large/006tNbRwgy1g9kuat53elj30u00lgdhe.jpg)

文章地址： https://mp.weixin.qq.com/s/rYNsKPhw2zR84-4K62gliw

还有一篇文章也不错，一并推荐给大家 - [大前端时代下的微前端架构：实现增量升级、代码解耦、独立部署](https://mp.weixin.qq.com/s/DVkrV_KKE9KaGSeUSenc6w)

微前端中有一个重要的需要解决的问题是子系统之间的路由。而我们的 BigPipe 如果被当作一个个子应用的，那不就是微前端中的一个点么？BigPipe 也好，微前端也好，都是一种概念，一种指导思想。微前端是不限于技术栈的， 你可以使用传统的 ssr，也可以使用 csr，也可以使用现代 csr + ssr 等，框架也可以五花八门。 如何将这些系统组合起来，并且能够有条不紊地进行合作完成一个完整的应用？这是微前端所研究和要解决的问题。

对于微前端，我们隔离各个应用的方式有几种：

1. iframe
2. 类似 bigpipe 这种客户端异步加载技术
3. web-components

不管采用哪种方式，我们的大体逻辑都是：

- 先加载主框架
- 异步加载各个子应用

只不过加载子应用，我们可以通过 iframe 去加载，也可以使用 web-component 去加载，也可以使用类似 bigpipe 的方式分段并行加载。我们甚至可以将这几者进行结合使用。而 iframe 和 web-compoents 顺带解决了诸如 js 和 css 等隔离的作用，而 bigPipe 只是对资源加载的一个有效控制，其本身并没有什么特殊含义，更不要说诸如 js 和 css 等隔离作用了。

## 事物关联

当前端有了 Nodejs 之后，我们发现可以做的事情变多了，除了 BigPipe，我们又去做 ssr，又要做 graphql，还要做微前端，海报服务，AI 等等。当你从大的视角看的时候，会发现这些技术或多或少都有交集，比如我刚才提到的 ssr。 我们知道 ssr 中有一点就是我们先返回给用户一个有内容的 html，这个 html 在服务端生成，由于在服务端生成，因此只有样式，没有绑定事件，所以后续我们需要在客户端合成事件。 如果将上面 BigPipe 的代码拿过来看的话，会发现我们的 html markup 可以看作服务端渲染内容（可以是直接写死的，也可以是服务端动态生成的）。之后我们输出后续 pagelet 的 JS 代码到前端，前端继续去执行。基于 BigPipe 我们甚至可以控制页面优先级显示。我们再继续去看的话， BFF 常见的一个功能“合并请求”在这里扮演了什么样的角色？大家可以自己想一下。当你不断从不同角度思考问题，会发现很多东西都有关联。每一个技术背后往往都会落到几个基本的原理上。了解技术初始产生背后解决的问题对于掌握一个技术来说非常重要。
