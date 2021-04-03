---
title: lucifer 的面试之路
tags: [前端, 面经, 校招, 虾皮]
date: 2021-04-03
categories:
  - [前端]
  - [面经]
  - [校招]
  - [虾皮]
---

<!-- more -->

## 为什么有这个栏目？

关注 lucifer 的同学可能知道，我之前在组织模拟面试。这个活动是我作为面试官虐别人的。很多胖友想看我是如何面试被虐的。可是我想我也没被面试虐过啊（逃~），就算被虐过你们也看不到，所以我也不会承认的。

所以我就打算开这个系列，从网上找一些靠谱的面经。把我自己当成面试者去回答面经的问题，让大家看看我是如何被虐的。

为了更好的节目效果（不会承认是自己懒），我就不提前准备了，直接拿起来面经就开始干了，这样大家的参考价值更高。

## 本期猎物

- 虾皮

## 题目

面经来源：https://www.1point3acres.com/bbs/forum.php?mod=viewthread&tid=723973&extra=page%3D1%26filter%3Dsortid%26sortid%3D327%26sortid%3D327

### 一面

1. JS 给一个 array ["1", "2", "3"]转化为 string "1, 2, 3"，["1", "2", ["1", "2"], "3"] 转化为 string "1,2,1,2,3"，
   follow up: 输入的 array 可能有哪些异常情况，该如何处理

> 其实就是考察 flatten。我的大前端面试宝典收录了这个题。大前端面试宝典地址在文末。

2. 经典问题实现函数柯里化 curry(add())，背了无数遍的实现，秒了

> 我的大前端面试宝典收录了这个题。大前端面试宝典地址在文末。

基础知识问答：

1. html 渲染流程，follow up: defer 和 async 标签的区别

> defer 和 async 都不会组织后面文档的渲染和执行。区别是文档中的 defer 标签会按照在文档中的声明顺序执行，async 则不会。

2. https 和 http, follow up: 什么是中间人攻击，数字签名证书，RSA 加密过程

3. JavaScript 有几种数据类型

4. JavaScript 代码的执行顺序（宏任务，微任务经典背诵）

5. 什么是闭包

> 一定先搞明白作用域，然后提到词法作用域才是闭包产生的原因。最后讲下闭包的原理和应用。

### 二面

一些 BQ，问的 LZ 有点懵

基础知识问答：

1. React 大致介绍一下
2. React 的 virtual dom, follow up: 渲染中 reflow 和 repaint 的区别
3. React 的 render return 的是什么

4. React native 用过吗（答：没有，但我会用 Java 写 Android）follow up: Recycler View 介绍一下（说好的前端呢）
5. 跑偏了，Java 的垃圾处理（LZ 从 JVM 的内存结构开始讲起，什么新生代老年代元空间，什么标记清除法）
6. 一个像素占用内存大小，答：不知道。follow up：猜一下，LZ 猜测 RGB 三个通道 0-255，256 是 2 的 8 次方，所以一个通道 1byte，三个加上 3 byte。面试官表示还有个透明通道，加上一共 4byte

1 周以后 HR 通知过了

## 视频解析

## 参考

- [大前端面试宝典](https://lucifer.ren/fe-interview/#/ "大前端面试宝典")
- [不要再问我头像如何变灰了，试试这几种滤镜吧！](https://lucifer.ren/blog/2020/04/12/canvas-filter/ "不要再问我头像如何变灰了，试试这几种滤镜吧！")
