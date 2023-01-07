---
title: 为了提高 Github 的阅读体验，我做了一个 Github 阅读器
tags: [Github]
date: 2021-05-16
categories:
  - [Github]
---

## 这是个什么东西？

虽然自从 Github 嫁给微软之后，做了很多的工作。不管是功能上，还是视觉 UI 上。因此在 Github 上看文档也比以前舒服多了。

![](https://p.ipic.vip/grpncc.jpg)

可我仍然不是很喜欢这样的界面，我想让界面更加好看一点。

于是我就做了这么一个工具。

**只需要输入 Github 地址，点击阅读就 OK 了**。是不是很简单？

<!-- more -->

上面的 mardown 页面转换后的效果：

![](https://p.ipic.vip/d7pqhx.jpg)

## 如何体验？

体验地址：https://leetcode-solution.cn/github

界面非常简单。简单来说就是：输入一个 github 的 md 地址，点击阅读就行了。

![网页截图](https://p.ipic.vip/szd932.jpg)

另外你如果有一个 md 源码，想在线转化也是可以的。比如我用 md 写了下面一段话：

````
## 思路

这个是我的思路。

上一个图片吧。

![蓝色表示叶子节点](https://p.ipic.vip/z0syhs.jpg)

## 代码

```py
def f():
  pass
```

**复杂度分析**

令 N 为数组长度。

- 时间复杂度：$O(N+max(0, K-N)^2)$
- 空间复杂度：$O(max(1, K - N))$

````

你可以将其复制粘贴到我这里的多行文本框，点击前往阅读即可。

![效果图1](https://p.ipic.vip/w6wmpu.jpg)
![效果图2](https://p.ipic.vip/2c6b0l.jpg)

如果你愿意的话，也可以将渲染结果复制粘贴到其他地方，比如一些云笔记平台。

值得注意的是，现在只支持 markdown，如果你输入的地址不是 markdown 是不可以的哦。

之后计划支持更多网站，不仅仅是 Github。

现在很多人都把周刊或者一些面试资料以 markdown 的形式放到 github 上， 如果你也经常看在 Github 上看 markdown 不妨尝试一下吧~

## 推荐几个资源

最后推荐几个 Github 上的阅读资源给大家：

- https://github.com/ruanyf/weekly

![](https://p.ipic.vip/fe5or6.jpg)

- https://github.com/sorrycc/weekly

![](https://p.ipic.vip/fj8uhp.jpg)

- https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/get-started/ch1.md

![](https://p.ipic.vip/curpyx.jpg)

- https://github.com/azl397985856/fe-interview/blob/master/docs/topics/network/tcp.md

![](https://p.ipic.vip/2we2u9.jpg)

> 有没有一个很突兀？
