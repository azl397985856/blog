---
title: 刷题插件可以隐藏测试用例啦
tags: [LeetCode, 插件, 刷题]
date: 2021-12-22
categories:
  - [LeetCode]
  - [插件]
---

## 一切都来源于一个 issue

今日有粉丝提意想增加隐藏测试用例的功能。issue 地址：https://github.com/azl397985856/blog/issues/91

![](https://files.mdnice.com/user/2016/d673b560-4865-40f7-8ff8-c803807502cb.png)

当天我就完成了这个功能的开发，并上架商店进行审核了。

![](https://files.mdnice.com/user/2016/8b683fe7-12c9-4986-8db9-d94ea8b508ee.png)

<!-- more -->

## 功能介绍

简单介绍一个这个功能，有需要的同学可以更新一下最新的版本。

当我们提交力扣代码，并且无法通过时，力扣会直接显示出错误的测试用例以及期望的输出。

有些时候，我们不想立马看到错误的具体细节，而只想知道有错误就够了。这样可以起到很好的练习作用。试想你正在参加面试，面试官告诉你代码有问题，而不告诉你具体哪个 case 有问题，这是很正常的吧？因此锻炼自己的这种自己分析问题的能力也很有必要。

比如题目直接显示错误的用例输入是空字符，那你直接就知道自己忘记处理边界了。但是如果这个空字符串是自己想出来的，那么效果肯定比力扣告诉你要好。

于是我开发了这个提交错误后默认隐藏出错细节的功能。

![](https://files.mdnice.com/user/2016/1d424bb3-2607-4905-8540-8bc634f2263c.png)

只有你点击显示的时候才可以看到详细信息。避免你自己不想看，却被弹到脸上的尴尬。

![](https://files.mdnice.com/user/2016/ed1da6c6-5c67-41ce-8bfc-3439269e3eee.png)

> 值得注意的是这个功能目前默认开启，无法关闭。

## 如何使用

大家首先要更新到 v0.10.0 及以上版本。其次找到力扣中的任意一道题，点击提交即可。如果提交出错即可看到西法给你的贴心提示啦！

> 插件的安装和使用方法请到我的公众号力扣加加回复插件获取

## 后话

为了测试这个功能，我可以故意做错了很多题，满屏的红色好扎心。

![](https://tva1.sinaimg.cn/large/008i3skNly1gxmjb5dyymj30qo12o78p.jpg)