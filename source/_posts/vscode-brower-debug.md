---
title: 史诗级更新，VSCODE 可无缝调试浏览器了！
tags: [工具, VSCODE]
categories:
  - [工具, VSCODE]
date: 2021-07-28
---

2021-07-16 微软发布了一篇博客专门介绍了这个功能，VSCODE 牛逼！

在此之前，你想要在 vscode 内调试 chrome 或者 edge 需要借助于 Chrome Debugger 或者 the Microsoft Edge Debugger extension 这两款 vscode 扩展。

并且更重要的是，其仅能提供最基本的控制台功能，其他的诸如 network，element 是无法查看的，我们仍然需要到浏览器中查看。

<!-- more -->

## 这是个什么功能

更新之后，我们可以直接在 vscode 中 `open link` in chrome or edge，并且**直接在 vscode 内完成诸如查看 element，network 等几乎所有的常见调试需要用到的功能**。

效果截图：

![](https://tva1.sinaimg.cn/large/008i3skNly1gsvftr837qj30sg0cejsu.jpg)
（edge devtools）

![](https://tva1.sinaimg.cn/large/008i3skNly1gsvfupkll2j30sg07omxi.jpg)
（debug console）

## 如何使用

使用方式非常简单，大家只需要在前端项目中按 F5 触发调试并进行简单的配置即可。这里给大家贴一份 lauch.json 配置，有了它就可以直接开启调试浏览器了。

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "pwa-msedge",
      "request": "launch",
      "name": "Launch Microsoft Edge and open the Edge DevTools",
      "url": "http://localhost:8080",
      "webRoot": "${workspaceFolder}"
    }
  ]
}
```

> 大家需要根据自己的情况修改 url 和 webRoot 等参数。

## 原理

原理其实和 chrome debugger 扩展原理类似。也是基于 Chrome 的 devtool 协议，建立 **websocket 链接。通过发送格式化的 json 数据进行交互**，这样 vscode 就可以动态拿到运行时的一些信息。比如浏览器网络线程发送的请求以及 DOM 节点信息。

你可以通过 **chrome devtool protocol** 拿到很多信息，比如上面提到的 network 请求。

由于是 websocket 建立的双向链接，因此在 VSCODE 中改变 dom 等触发浏览器的修改也变得容易。我们只需要在 VSCODE（websocket client） 中操作后通过 websocket 发送一条 JSON 数据到浏览器（websocket server）即可。浏览器会根据收到的 JSON 数据进行一些操作，从效果上来看**和用户直接在手动在浏览器中操作并无二致。**

值得注意的，chrome devtool protocol 的客户端有很多，不仅仅是 NodeJS 客户端，Python，Java，PHP 等各种客户端一应俱全。

## 更多

- [Easier browser debugging with Developer Tools integration in Visual Studio Code](https://blogs.windows.com/msedgedev/2021/07/16/easier-debugging-developer-tools-in-visual-studio-code/)
- [vscode-js-debug](https://github.com/microsoft/vscode-js-debug#readme)
- [chrome devtools-protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Microsoft Edge (Chromium) DevTools Protocol overview](https://docs.microsoft.com/en-us/microsoft-edge/devtools-protocol-chromium/)
