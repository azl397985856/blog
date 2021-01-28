---
title: 力扣刷题插件
tags: [LeetCode, 插件, 刷题]
categories:
  - [LeetCode]
  - [插件]
---

之前我做了一个视频， 介绍我的刷题浏览器扩展插件，视频地址：https://www.bilibili.com/video/BV1UK4y1x7zj/。 今天我在上次的基础上增加了部分公司的显示以及优化了若干体验功能。

<!-- more -->

## 这个刷题插件能做什么？

### 题解模板（新功能）

为了方便大家写出格式良好的题解，插件现在内置题解模板功能，目前模板只有一套，这套模板是**我经常使用的题解模板**。

安装好我们的插件(版本需要 v0.8.0 及以上)后，打开力扣中文版，会发现如下的按钮。

![](https://tva1.sinaimg.cn/large/008eGmZEly1gn3bp2ag3kj312b0u0gys.jpg)

点击之后会自动引导你到一个新的页面，

![](https://tva1.sinaimg.cn/large/008eGmZEly1gn3bvpadsbj31g70u0k38.jpg)

该页面的**题解语言**，**题目地址**和**题目名称**信息会自动填充。

你可以快速完成时间复杂度，空间复杂度的插入，复杂度已经按照性能好坏的顺序给大家排好了，点击即可插入。

此外我们提供了若干常用的公式供你快速复制使用。除了公式，其他内容都可以在右侧的预览区域查看。

写完只会可以点击复制，将其复制到其他地方以便持久化存储。由于我们没有做持久化存储，因此**页面刷新内容就会消失哦**。

最后祝大家写出漂亮的题解！

### 数据结构可视化

你可以使用 canvas 自由绘制各种数据结构，不管是写题解还是帮助理解题目都很有用。

我们提供了很多内置的模板供你快速上手。

![](https://tva1.sinaimg.cn/large/008eGmZEly1gms0ni6r2pj317c0cw75j.jpg)

如果你对内置的模板不满意，也可以将自己的模板保存以便下次使用。

![](https://tva1.sinaimg.cn/large/008eGmZEly1gmrz98cxflj31bp0u07k9.jpg)

### 学习路线

算法怎么学？推荐按专题来。具体到某一个专题怎么学？这里提供了一个学习路线帮助你。本功能旨在将一个专题中的题目进行分类。专题本质就是对题目的一种划分，学习路线基于专题又进行了一次划分。

![](https://tva1.sinaimg.cn/large/0081Kckwly1glpqbuba55j30w00u0tgr.jpg)

### 复杂度分析

你的代码能会超时么？复杂度分析帮助你。

![](https://tva1.sinaimg.cn/large/0081Kckwly1gm6xl5uih3j30o50nl0u9.jpg)

### 一键复制所有内置测试用例

省去了一个个手动复制的过程，效率翻倍！

![](https://tva1.sinaimg.cn/large/0081Kckwly1glmfz7knmtj32060f0mye.jpg)

### 模板

提供了大量的经过反复验证的模板。模板的作用是在你理解了问题的基础上，快速书写，并减少出错概率，即使出错，也容易 debug。

### 禅定模式

![](https://tva1.sinaimg.cn/large/0081Kckwly1glmg5pa61gj31jk0u0qgg.jpg)

点击之后会变成这样：

![](https://tva1.sinaimg.cn/large/0081Kckwly1glmg6srs4kj31h50u0dml.jpg)

底部控制台会消失，当你鼠标重新移过来或者退出禅定模式就出现了。

### 查看题解

当你在任意非题目详情页或者我还没有收录的题目详情页的时候， 我都会列出当前我总结的所有题解。

![](https://tva1.sinaimg.cn/large/007S8ZIlly1ghsse7cw2oj313s0u0tbz.jpg)

> 其实我给比较经典的题目做了题解，因此这个题目数目不是很多，目前是 173 道题。另外有时候我直接写了专题，没有单独给每道题写题解，因此数量上要比 173 多很多。

当你进到一个我写了题解的题目详情页的时候， 你就可以正式使用我的插件了。 它可以：

- 给出这道题目的前置知识。换句话说就是**我需要先掌握什么才能做出这道题**。
- 这个题目的关键点。
- 哪些公司出了这道题。
- 我实在不会了，给我看看题解吧。好，满足你。
- 题解我就不看了，直接 show me code 吧。好，满足你。
- 根据公司，查找题目。面试突击必备

![](https://tva1.sinaimg.cn/large/007S8ZIlly1ghssdtat3zj31290u0dii.jpg)

## 我怎么才能获取呢？

公众号《力扣加加》后台回复刷题插件即可。

## 如何离线安装

- 将下载的压缩包解压
- 在 Chrome 浏览器的地址栏输入 chrome://extensions/
- 点击 load uppack

> 不知道中文是什么名字，反正就是上面三个按钮最左边的。

- 选择你解压之后的文件夹

![](https://tva1.sinaimg.cn/large/007S8ZIlly1ghsscnetjej30os0cw75e.jpg)

- 出现下面这个就说明你安装成功了，点一下试试吧。

![](https://tva1.sinaimg.cn/large/007S8ZIlly1ghss5p4j9oj30l802g0t3.jpg)

## 后期的规划是怎么样的？

> 后期的功能计划先对 91 活动的用户开发。关于 91 活动，大家可以关注我的公众号《力扣加加》了解详情。

- 更多公司信息。 持续完善题目的公司信息，这个过程需要大家的帮助，大家可以把自己面试遇到的问题发给我（附带公司和岗位信息），我可以免费提供咨询服务。

- 岗位信息。

![](https://tva1.sinaimg.cn/large/007S8ZIlly1ghss7raskrj31c00u046y.jpg)

这个过程同样需要大家的帮助，大家可以把自己面试遇到的问题发给我（附带公司和岗位信息），我可以免费提供咨询服务。

- 可视化调试。 可视化展示你的代码允许情况。

![](https://tva1.sinaimg.cn/large/007S8ZIlly1ghssbhbbnvg30dc02w3z4.gif)

（一个双指针题目的可视化调试过程）

- 自动制定复习计划。
- AI 智能提示。即新的提示也可以根据题目信息推测可能的解法。
- 等等

## 关注更新

大家可以关注我的公众号， 如果插件有更新，会第一时间在公众号同步的哦~

想看题解可以访问我的 LeetCode 题解仓库：https://github.com/azl397985856/leetcode 。 目前已经 35K star 啦。

关注公众号力扣加加，努力用清晰直白的语言还原解题思路，并且有大量图解，手把手教你识别套路，高效刷题。

![](https://tva1.sinaimg.cn/large/007S8ZIlly1gfcuzagjalj30p00dwabs.jpg)
