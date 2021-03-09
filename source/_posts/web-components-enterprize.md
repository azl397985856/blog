---
title: 使用web-component搭建企业级组件库
tags: [前端, 组件化, web-component]
categories:
  - [前端, 组件化]
  - [前端, web-component]
date: 2020-02-22
---

前端目前比较主流的框架有 react，vuejs，angular 等。 我们通常去搭建组件库的时候都是基于某一种框架去搭建，比如 ant-design 是基于 react 搭建的 UI 组件库，而 elementUI 则是基于 vuejs 搭建的组件库。

虽然目前社区有相关工具，提供框架之间的转化服务，比如讲 vuejs 组件转化为 react 组件。但是毕竟是不同的框架，有不同的标准。因此框架 api 发生变动，那么你就需要重写转化逻辑，显然是不灵活的，因此我们暂不讨论这种情况。作为公司而言，就需要为不同的框架写不同的组件库，尽管逻辑都是一样的。

另外如果框架升级，比如从 1.x 升级到 2.x，那么对应组件库就需要升级，如果公司的组件库有很多（vuejs，react，angular 等），那么这种升级的概率就会更大。

<!-- more -->

## 什么是 web-component？

那么有没有更好的方案，一次编写，到处使用呢？

答案就是借助 web component。

Web Components 是一系列加入`w3c`的 HTML 和 DOM 的特性，使得开发者可以创建可复用的组件。

由于 web components 是由 w3c 组织去推动的，因此它很有可能在不久的将来成为浏览器的一个标配。

Web Components 主要由以下四个部分组成：

- Custom Elements – 定义新 html 元素的 api
- Shadow DOM – Encapsulated DOM and styling, with composition
- HTML Imports – Declarative methods of importing HTML documents into other documents
- HTML Templates – The `<template>` element, which allows documents to contain inert chunks of DOM

## web-component 有什么优点

使用 web components 搭建组件库能够带来什么好处呢？
前面说了，web components 是 w3c 推动的一系列的规范，它是一个标准。

如果我们使用 web components 的 api 开发一个组件，这个组件是脱离框架存在的，也就是说
你可以在任何框架中使用它，当然也可以直接在原生 js 中使用。

我们无须为不同的框架编写不同的组件库。

使用 web components 编写的组件库的基本使用方法大概是这样的：

```js
  <script src="/build/duiba.js"></script>

  <!-- 运营位组件 -->
  <operation-list></operation-list>

```

毫不夸张地说， `web components` 就是未来。

但是 web components 的 api 还是相对复杂的，因此用原生的 api 开发 web components 还是
相对比较复杂的，就好像你直接用原生 canvas api 去开发游戏一样。

下面我们介绍下用于简化 web components 开发的库。

## polymer

polymer 是我接触的第一个 web componment 开发库，那已经是很多年前的往事了。

> Build modern apps using web components

更多介绍[polymer](https://github.com/Polymer/polymer)

## stencil

stencil 是在 polymer 之后出现的一个库。
第一次接触时在 Polymer Summit 2017 的分享上，这里贴下地址[Using Web Components in Ionic - Polymer Summit 2017](https://youtu.be/UfD-k7aHkQE)。

> Stencil is a tool developers use to create Web Components with some powerful features baked in, but it gets out of the way at runtime.

那么 powerful features 具体指的是什么？

```
Virtual DOM
Async rendering (inspired by React Fiber)
Reactive data-binding
TypeScript
JSX
```

它也是一个用于生成 web compoennt 的 tool。 不同的是她提供了更多的特性(Reactive data-binding,TypeScript,JSX, virtual dom)以及更强的性能(virtual dom, Async rendering).

细心的人可能已经发现了，我将 Virtual DOM 既归为特性，又归为性能，没错！ Virtual DOM 提供了一种到真实 dom 的映射，使得开发者不必关心真实 dom，从这个层面讲它是特性。

从虚拟 dom 之间的 diff，并将 diff info patch 到 real dom（调和）的过程来看，它是性能。

用 stencil 开发 web components 体验大概是这样的：

```js
import { Component, Prop, State } from "@stencil/core";

@Component({
  tag: "my-component",
  styleUrl: "my-component.scss",
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

这是我基于[stenciljs](https://github.com/ionic-team/stencil) + [storybook](https://github.com/storybooks/storybook)写的一个小例子。大家可以 clone，并运行查看效果。

[duiba-components](https://github.com/azl397985856/duiba-components)

通过这样搭建的企业级组件库，就可以轻松地为不同业务线提供基础组件库，而不必担心使用者（各个业务方）的技术栈。

将来业务方的框架升级（比如 vue1 升级到 vue2），我们的组件库照样可以使用。

可以想象，如果 es 标准发展地够好，web components 等规范也足够普及，无框架时代将会到来。

> 无框架，不代表不使用库。

只需要借助工具库就可以开发足够通用的组件，也不需要 babel 这样的转换器，更不需要各种 polyfill。
那么开发者大概会非常幸福吧，可惜这样的日子不可能存在，但是离这个目标足够近也是极好的。
