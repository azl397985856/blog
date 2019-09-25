---
title: 使用web-component搭建企业级组件库
tags: [前端, 组件化, web-component]
categories: 
  - [前端, 组件化]
  - [前端, web-component]
---
前端目前比较主流的框架有react，vuejs，angular等。 我们通常去搭建组件库的时候都是基于某一种框架去搭建，比如ant-design是基于react搭建的UI组件库，而elementUI则是基于vuejs搭建的组件库。

虽然目前社区有相关工具，提供框架之间的转化服务，比如讲vuejs组件转化为react组件。但是毕竟是不同的框架，有不同的标准。因此框架api发生变动，那么你就需要重写转化逻辑，显然是不灵活的，因此我们暂不讨论这种情况。作为公司而言，就需要为不同的框架写不同的组件库，尽管逻辑都是一样的。

另外如果框架升级，比如从1.x升级到2.x，那么对应组件库就需要升级，如果公司的组件库有很多（vuejs，react，angular等），那么这种升级的概率就会更大。
<!-- more -->
## 什么是web-component？
那么有没有更好的方案，一次编写，到处使用呢？

答案就是借助web component。

Web Components 是一系列加入`w3c`的HTML和DOM的特性，使得开发者可以创建可复用的组件。

由于web components是由w3c组织去推动的，因此它很有可能在不久的将来成为浏览器的一个标配。

Web Components 主要由以下四个部分组成：

- Custom Elements – 定义新html元素的api
- Shadow DOM – Encapsulated DOM and styling, with composition
- HTML Imports – Declarative methods of importing HTML documents into other documents
- HTML Templates – The `<template>` element, which allows documents to contain inert chunks of DOM

## web-component有什么优点

使用web components搭建组件库能够带来什么好处呢？
前面说了，web components 是w3c推动的一系列的规范，它是一个标准。

如果我们使用web components的api 开发一个组件，这个组件是脱离框架存在的，也就是说
你可以在任何框架中使用它，当然也可以直接在原生js中使用。

我们无须为不同的框架编写不同的组件库。

使用web components编写的组件库的基本使用方法大概是这样的：

```js
  <script src="/build/duiba.js"></script>

  <!-- 运营位组件 -->
  <operation-list></operation-list>

```

毫不夸张地说， `web components` 就是未来。


但是web components的api还是相对复杂的，因此用原生的api开发web components还是
相对比较复杂的，就好像你直接用原生canvas api去开发游戏一样。

下面我们介绍下用于简化web components开发的库。
## polymer
polymer是我接触的第一个web componment开发库，那已经是很多年前的往事了。
> Build modern apps using web components

更多介绍[polymer](https://github.com/Polymer/polymer)

## stencil
stencil是在polymer之后出现的一个库。
第一次接触时在Polymer Summit 2017的分享上，这里贴下地址[Using Web Components in Ionic - Polymer Summit 2017](https://youtu.be/UfD-k7aHkQE)。

> Stencil is a tool developers use to create Web Components with some powerful features baked in, but it gets out of the way at runtime.

那么powerful features具体指的是什么？

```
Virtual DOM
Async rendering (inspired by React Fiber)
Reactive data-binding
TypeScript
JSX
```

它也是一个用于生成web compoennt的tool。 不同的是她提供了更多的特性(Reactive data-binding,TypeScript,JSX, virtual dom)以及更强的性能(virtual dom, Async rendering).

细心的人可能已经发现了，我将Virtual DOM既归为特性，又归为性能，没错！ Virtual DOM提供了一种到真实dom的映射，使得开发者不必关心真实dom，从这个层面讲它是特性。 

从虚拟dom之间的diff，并将diff info patch到real dom（调和）的过程来看，它是性能。

用stencil开发web components体验大概是这样的：

```js
import { Component, Prop, State } from '@stencil/core';

@Component({
  tag: 'my-component',
  styleUrl: 'my-component.scss'
})
export class MyComponent {
  // Indicate that name should be a property on our new component
  @Prop() first: string;

  @Prop() last: string;

  @State() isVisible: boolean = true;

  render() {
    return (
      <p>
        Hello, my name is {this.first} {this.last}
      </p>
    );
  }
}

```

## Demo

这是我基于[stenciljs](https://github.com/ionic-team/stencil) + [storybook](https://github.com/storybooks/storybook)写的一个小例子。大家可以clone，并运行查看效果。

[duiba-components](https://github.com/azl397985856/duiba-components)

通过这样搭建的企业级组件库，就可以轻松地为不同业务线提供基础组件库，而不必担心使用者（各个业务方）的技术栈。

将来业务方的框架升级（比如vue1升级到vue2），我们的组件库照样可以使用。

可以想象，如果es标准发展地够好，web components 等规范也足够普及，无框架时代将会到来。

> 无框架，不代表不使用库。

只需要借助工具库就可以开发足够通用的组件，也不需要babel这样的转换器，更不需要各种polyfill。
那么开发者大概会非常幸福吧，可惜这样的日子不可能存在，但是离这个目标足够近也是极好的。