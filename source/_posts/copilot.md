---
title: 写注释就能自动出代码？copilot 尝鲜
tags: [AI, VSCODE]
date: 2021-10-05
categories:
  - [工具, VSCODE]
---

copilot 是一个基于 AI 的编程辅助工具。目前已经集成在了 vscode 中，后续可能集成到更多平台和工具，目前还是测试阶段。官网地址：https://copilot.github.com/

<!-- more -->

## 支持所有语言

copilot 是利用网络中现有的公开数据，尤其是开源在 Github 上的代码， 然后基于机器学习算法训练出来的。因此 copilot 理论上支持所有编程语言。

目前我测试了 JS 和 Python，效果都还蛮不错的。官方提供了 ts，go，py 和 rb 语言的示例。

## 注释即代码

你可以通过编写注释然后一路根据 copilot 的提示编写出完整的程序。

比如我想根据 Github 用户名获取用户信息。我只需要写下这样一行注释。以 JS 为例：

```js
// 根据 Github 用户名获取用户信息
```

copilot 是如何一步步引导你完成完整功能的呢？我们来看下。

第一步：

![](https://tva1.sinaimg.cn/large/008i3skNly1guzsi9e2oxj60oe04wwej02.jpg)

注意：注释下面的代码颜色是浅色的，是 copilot 提示出来的。下同，不再解释。

按下 tab 键就会浅色的代码就会被填充，并提示接下来的代码。

第二步：

![](https://tva1.sinaimg.cn/large/008i3skNly1guzsj49jjaj60ym0bqwfg02.jpg)

再次按下 tab 键，整体的代码就生成了。

![](https://tva1.sinaimg.cn/large/008i3skNly1guzsjfft9ij60y20bwjsy02.jpg)

类似的例子还有很多，等待大家来探索。

## 代码补全

IDE 的一个很重要的功能就是代码补全。 copilot 增强了 IDE 的补全功能。

copilot 可以根据你的代码仓库以及世界上公开的代码仓库提示你可能的输入，从而减少你敲击键盘的次数，在更短的时间写出更多的代码，获取更多的摸鱼时间。

举个例子，仍然以 JS 为例。我想发送一个 fetch 请求。

```js

fetch('https://www.leetcode-solution.cn', {
```

它就提示我：

![](https://tva1.sinaimg.cn/large/008i3skNly1guzsnk6vygj60r804kaaa02.jpg)

接下来按照它的提示，只按 tab 不写代码的情况就可以写出如下代码。

```js
fetch("https://leetcode-solution.cn", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    question_id: "1",
    lang: "javascript",
    code: "console.log(1)",
  }),
}).then((res) => {
  console.log(res);
});
```

对我的仓库功能来说， 上面代码有一小部分是有问题的。 不过我只需要稍微改改就行了。效率提升还是不错的。

## 如何使用？

在 vscode 插件市场搜索 `github copilot`，点击 install，然后按照提示安装即可。

安装好了就可以体验了！ 写写注释？敲敲代码？按按 tab？代码 duang 的一下就生成了。

## 总结

copilot 是一个类似 tabnine 的 ai 编程辅助工具，目前以 vscode 插件的形式提供免费服务，目前是测试阶段，还没有最终发行。它有自动提示，根据注释写代码等诸多激动人心的功能。

更多功能以及最新动态请访问官方网站：https://copilot.github.com/
