---
title: Chrome 新功能 - 录制小视频
tags: [Chrome]
date: 2021-11-10
categories:
  - [工具, Chrome]
---


Chrome 97 推出了一个预览功能 - Recorder。它允许你录制 Web 页面的操作并支持**回放，编辑，测量性能** 等诸多功能。

<!-- more -->


## 它长什么样

你可以直接在 chrome devtool 中看到一个 Recorder 面板，点击它就可以体验。

> 如果没有找到，可以尝试 cmd + shift + p 调出命令面板搜索 Recorder。当然如果该功能未发布是搜不到的

![](https://tva1.sinaimg.cn/large/008i3skNly1gwacz4fu4rj318g0r0dj6.jpg)

## 它有什么用？

通过它，你可以实现一些有趣的功能。

比如：

- 测试同学录制一段“视频”， 然后发送给开发，开发根据这段视频定位问题。
- 测试某一个业务流程在各种不同的网络和硬件环境下的表现，甚至你可以看其在不同平台的表现（比如 PC，手机，平板等）。

![](https://tva1.sinaimg.cn/large/008i3skNly1gwad3bf8vkj318g0tcadz.jpg)

- 自动化测试。你可以录制一段视频，然后通过修改其中部分参数的形式来自动化生成很多测试用例。

![](https://tva1.sinaimg.cn/large/008i3skNly1gwad32b9a1j31080u0mzw.jpg)

- 。。。

由于是预览版，因此最终是什么样可能还不确定。

## 大招

对于我来说，我想要到一个比较有意思的功能。

我们知道 Chrome 的 devtool frontend（就是你看到的开发者工具） 是开源的，代码托管在 Github：https://github.com/ChromeDevTools/devtools-frontend

因此你可以直接集成它到你的项目中。比如你可以开发一个调试工具，这个工具 fork 一下 devtool frontend，然后修改 Recoreder 部分的源码，使得用户可以手动上报自己的录像，然后你将用户的录像数据，网络数据等其他数据发送到你的后端进行分析。

> Recorder 的源码到时候应该在这个文件夹下 https://github.com/ChromeDevTools/devtools-frontend/tree/main/front_end/panels

这个功能我在之前的公司做过，不过做的并不好。而如果依托于 Chrome 团队，那些棘手的问题都不需要你解决了，比如性能问题就很棘手。

如果你的公司有做用户错误上报或者信息收集的需求，不妨考虑一下是否可以为你所用。

更多介绍：https://developer.chrome.com/docs/devtools/recorder/

