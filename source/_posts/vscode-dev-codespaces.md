---
title: github 又出新功能，布局云端 vscode？
tags: [工具, VSCODE]
categories:
  - [工具, VSCODE]
date: 2021-09-02
---

vscode 和 github 是微软的两大开源产品，二者在业界的影响力都是巨大的。

近日 Github 新出了一个功能，用户可以通过将 url 中的 **.com 替换为 .dev** 来直接打开在线版的 vscode 编辑器。

<!-- more -->

如果大家听过之前出现的一个叫做 github1s 的第三方工具的话，那就很容易理解这个功能。和 github1s 的一样，用户通过修改 url 中的少量字符就可以直接在在线版的 vscode 中打开仓库。

比如 github 地址为：

https://github.com/azl397985856/leetcode

那么你就可以通过访问如下地址直接在云端 ide 打开：

https://github.dev/azl397985856/leetcode

> url 长度还是相同的，甚至还有一点整齐美

还有一种更简单的方法：只要你在任何 GitHub Repo 页面上**按下 .键** 会自动跳转到 github.dev 的网站。

笔者特意对 github1s 和 github.dev 进行了对比，结果如下图：

![](https://p.ipic.vip/uqz7bx.jpg)

可以发现二者不管是 UI 还是功能都是非常类似的。大的不同点就是 github.dev 集成了 codespaces，这也是微软的下一个主战场。不难想象，将来不仅是云端 vscode 还是本地的 vscode 都会向 codespaces 发力。

codespaces 允许你使用云端的资源，而不仅仅是作为一个编辑器，整体感觉类似 gitpod，不过功能会更多。

> gitpod 也是一款非常不错的产品，推荐大家使用

codespace 定位更高端，比如可以像 github actions 那样定制镜像，环境等。GitHub Codespaces 支持 Visual Studio Code 和新式 Web 浏览器。 借助在云端的开发，可无缝切换使用不同的工具，随时随地贡献代码。

想直接体验？戳这里：https://visualstudio.microsoft.com/zh-hans/services/github-codespaces/

如下是 codespaces 的架构图：

![](https://p.ipic.vip/jp7lt6.jpg)

可以看出其主要由两部分组成：一部分是编辑器，另外一部分是云端的虚拟机，而几乎所有的功能都可以在云端完成，比如 AI 提供的自动补全，**根据注释写代码**等功能。更多关于 codespaces 的介绍参考：https://docs.github.com/en/codespaces/overview#joining-the-beta

不过 codespaces 目前还没有大规模推广，期待这 codespaces 可以尽快推广，给广大像我一样的开发者带来便利。
