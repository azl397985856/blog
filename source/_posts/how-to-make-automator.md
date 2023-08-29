---
title: 如何自己实现一个自动化框架？
tags: [前端，自动化，automator, chrome]
date: 2023-08-27
categories:
  - [前端]
  - [自动化]
  - [devtool]
---

大家眼里的自动化框架一般都和测试进行绑定，这也可以理解， 毕竟自动化的目的就在于模拟用户行为，确认是否正常工作，代替传统的手工测试。

但实际上自动化和测试是两个问题，我们完全可以单独实现。

比如我可以将自动化框架 A 和 测试框架 B 结合起来使用。也可以将自动化框架 A 和 测试框架 C 一起使用。二者本应该是独立的。

因此本文将只聚焦自动化部分。如果需要扩展自动化测试功能，那么只需要集成一个测试框架进行简单接入就好了，不算复杂。

<!-- more -->

## 什么是自动化框架？

1. 用户角度

从用户角度上讲，自动化框架是一个能够自动操作软件的框架，其提供了一套用于编脚本的语言，用户使用这套语言就可以模拟各种各样使用软件的行为。

2. 输入输出角度

从输入输出的角度上讲，自动化框架就是给定一段测试脚本，能够根据其脚本内容执行对应行为的系统。也就是说，输入是一段脚本，输出可能 IO 操作，返回一段特定的文本等等。

## 自动化框架需要支持什么功能？

从前面的解释很容易看出，自动化框架核心就是模拟用户行为。靠什么模拟？靠脚本代码。

### 模拟用户操作

比如我们想模拟用户打开浏览器，在地址栏输入 https://lucifer.ren/blog

我们可以将上面的步骤具体定义为几步：

1. 打开浏览器
2. 输入 https://lucifer.ren/blog

这就是一个用户操作序列。

如果我们想要实现自动化框架，如果支持类似这样的用户操作序列？

主流的做法是面向对象编程， 先抽象几个类。比如 Browser, Page, Element 等等，然后给每个类定义细粒度的 API。通过 API 的组合完成上面的功能。

比如的自动化框架名字叫 my-automator，我们就可以实现如下几个 API。

一段示意测试脚本，这里我们的脚本采用 JS 语言编写（下同，不再赘述）。

```js
const automator = require("my-automator");

const browser = automator.launch(options);
browser.open({
  url: "https://lucifer.ren/blog",
});
```

browser 就是 Browser 类的一个实例，我们定义了一个 open 方法。

类似的，如果我们模拟这样的一个操作序列。

1. 打开浏览器
2. 输入 https://lucifer.ren/blog
3. 找到第一篇文章
4. 点击阅读全文
5. 找到页面下方的留言框
6. 输入留言内容：赞！

这里有一些前置知识。 这些知识需要自动化框架的使用者知晓，而自动化框架的开发者无需知晓。

这里的页面有多篇文章，每一篇文章都有一个阅读全文按钮，按钮用一个 div 实现，div 上有一个名为 readmore 的 class，其下有一个 a 标签，点击 a 标签会跳到对应文章。

文章详情页面的评论框是一个 textarea，有一个名为 gt-header-textarea 的 class。

我们可以这样设计我们的 API。

```js
const automator = require("my-automator");

const browser = automator.launch(options);
const page = browser.open({
  url: "https://lucifer.ren/blog",
});
const element = page.select(".readmore a"); // 类似于 document.querySelector 功能
element.click();
await browser.waitForNavigation(); // 等待页面跳转完成
const textarea = browser.currentPage.select(".gt-header-textarea");
textarea.input("赞");
```

也就是说，如果我们实现了这几个 API，就可以自动化测试上面的这一套用户操作序列了。

那么理论上我们只需要不断完成 API，就可以造一个完整的自动化框架了。文章后面会讲如果实现这些 API 的整体思路。

当然如何设计 API 不是本文重点， 大家完全可以采用自己认可的方式进行。大家只需要理解，我们是按照这种面向对象的方式，根据常见的用户操作进行细粒度拆分 API 即可。

### 返回特定的信息

除了模拟用户操作，我们还需要能够返回特定的信息。

比如当前页面是否在 loading， 当前 button 上显示的文字是什么。

这个有两个用途：

1. 方便根据不同情况写代码。还是以前面的跳转到最新文章下留言为例，我想看下当前第一篇文章是人为置顶的文章，还是按照时间排它是最新的。（假设我们会给置顶文章加一个特殊 class），那么就需要有一个获取元素 class 的 API。
2. 方便集成测试框架。还是以前面的跳转到最新文章下留言为例，我想知道这个过程有没有成功。那么可以根据 selectAll 方法找到所有留言，然后根据留言内容判断是否刚才成功留言了。那么就需要获取元素内容。这也是一种信息。

有了这两个功能，大部分常用的自动化框架的内容都可以实现。

## 如果实现一个自动化框架

首先不管是 web 的自动化， 还是小程序的自动化，甚至是手机的自动化，我们都需要明确一点。那就是：不管是 web 应用也好，小程序应用也好，手机应用也好。他们都是通过某种语言编写的，并且这些语言都可以满足我们前面提到的第二条”返回特定的信息“。

但是它不是根据自动化脚本自动执行，而是需要用户驱动。

不过这个很好办。我们只需设计一个通信机制。

1. 测试脚本通过这套通信机制通知应用需要执行何种操作。
2. 然后应用根据脚本发送的信息，执行操作，然后返回结果信息。

也就是说我们需要：

- 设计一套测试脚本和应用的通信手段。
- 实现一套应用代码，这段代码监听发送的消息，并将消息转化为页面的操作，然后返回结果信息。

对于第一个问题为了足够通用，通信我们选择 websocket，主流自动化框架都支持，尤其是 web 自动化框架。第二个问题就更简单了，只要你掌握应用编写的技巧，那么这套植入到应用中的代码并不难写。

### 整体架构

![](https://p.ipic.vip/jndga4.png)

如图，测试脚本通过 websocket 消息和应用通信，应用收到消息做对应动作，然后返回对应信息给测试脚本。

其中 handle 是对结果进行处理。 比如把不支持序列化的属性去掉或者转化为可序列化的结构。

### 功能实现

消息的结果，我们可以参考 [CDP](https://chromedevtools.github.io/devtools-protocol/)。CDP 使用 method 来标识不同类型的参数。其中 method 的命名采用固定格式：

```
[domain_name].[method_name]
```

比如你想调用 document.querySelector，就可以发送一个 websocket 消息给 chrome，其中 method 字段固定为 "DOM.querySelector"，参数为 nodeId 和 selector，返回值是选中结果 DOM 的 nodeId。

> 基于 CDP，你可以自己定制一个远程 devtool 工具，而不必使用 chrome 内置的 devtool。其实 chrome 内置的 devtool 也是基于 CDP 做的。

我们也可以采用这种格式来实现，下面代码是以 web 自动化框架为例，其他框架同理。

#### 测试脚本端

我们需要分别实现 Browser，Page 和 Element 类。

测试脚本端主要就是发送消息， 然后等待应用端返回对应的结果消息，最后回传给用户即可。

Browser:

```js
class Browser {
  constructor() {}
  open({ url }) {
    // open page in browser
  }
}
```

Page：

```js
class Page {
    constructor() {}
    select({ selector }) {
        return new Promise((resolve, reject) => {
            const id = uuid()
            ws.send({
                id
                method: 'PAGE.select', // PAGE 是 domain， select 是 method
                query: {
                    selector
                }
            })
            // 等待应用端消息
            ws.addEventListener("message", (event) => {
                const data = event.data
                if (data.id === id) {
                    resolve(data.result)
                    // 这里其实可以移除监听了
                }
            // ...
            });
        })
    }
    selectAll({ selector }) {
        // ...
    }
    // ...
}
```

Element

```js
class Element {
    constructor(id) {
        this.id = id
    }
    click() {
        return new Promise((resolve, reject) => {
            const id = uuid()
            ws.send({
                id
                method: 'ELEMENT.click', // ELEMENT 是 domain, click 是 method
                query: {
                    id: this.id
                }
            })
            // 等待应用端消息
            ws.addEventListener("message", (event) => {
                const data = event.data
                if (data.id === id) {
                    resolve(data.result)
                    // 这里其实可以移除监听了
                }
            // ...
            });
        })
    }
    attribute(name) {
        // ...
    }
}
```

可以看出测试脚本端代码都是类似的。

#### 应用端

我们需要植入一段代码到应用端。这套代码如果你了解应用代码如何编写， 也不会难。

总之，应用端就是监听消息，做动作，然后通过 websocket 将结果回传即可。

```js
const domMap = new Map();
function getElementById(id) {
  return domMap.get(id);
}
function setElementById(id, ele) {
  return domMap.set(id, ele);
}
ws.addEventListener("message", (event) => {
  const data = event.data;
  if (data.method === "select") {
    const ele = document.querySelector(data.query.selector);
    const id = uuid();
    setElementById(id, ele);
    ws.send({
      id: data.id,
      result: {
        id,
        ...handle(ele),
      },
    });
  }
  if (data.method === "click") {
    const element = getElementById(data.query.id);
    ws.send({
      id: data.id,
      result: handle(element.click()),
    });
  }
  // ...
});
```

## 总结

不管是 web 端自动化框架，还是小程序端自动化框架，甚至是手机端，电脑端自动化框架，我们都可以使用这个思路来完成。

即：

1. 注入一段代码到应用端。
2. 定义一套脚本语言，脚本发送消息到应用端。
3. 应用响应消息后做动作，最后返回结果信息给脚本端。

使用面向对象编程方法，结合 CDP 的定义格式可以帮助我们写出更清晰易懂的代码。

同时我们的自动化框架也可以轻松集成任意的测试框架，实现自动化测试的目的。
