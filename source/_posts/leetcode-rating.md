---
title: 一款显示题目对应周赛难度分的浏览器插件| TamperMonkey | Chrome | FireFox
tags: [刷题技巧, 工具, LeetCode]
date: 2023-01-19
categories:
  - [LeetCode]
  - [刷题技巧]
---

## leetcode rating website

经常有同学反映力扣难度设置的不合理。 比如：“为什么我觉得这个中等题目比某个困难还要难啊？”。

这其实很正常，尤其是在力扣上。因此我也不建议大家完全按照难度去刷题， 而是结合通过率等其他指标去刷。

而今天介绍的这个网站能够将力扣中的题目通过各个维度算出一个**更接近题目实际难度的隐藏分**。这个分数和你的竞赛分数是一致的。大家可以根据你的竞赛分去刷题。

比如你的竞赛分是 1800， 那么你就可以直接搜索 1800 - 1900 的题目进行练习，效率高很多。

![](https://tva1.sinaimg.cn/large/008vxvgGly1h8ni9nscv4j32bq0u0dkr.jpg)

网站地址：https://zerotrac.github.io/leetcode_problem_rating/#/

## leetcode rating extension

有一位朋友基于上面网站作为数据源自己写了一个扩展，直接在力扣官网里显示对应题目分数（如果有分数的话）。

这是一款显示题目对应周赛难度分的浏览器插件| TamperMonkey | Chrome | FireFox

![](https://p.ipic.vip/8wqbhj.jpg)

它是基于油猴的脚本， 大家需要先安装油猴扩展， 然后通过油猴去启动即可。

使用效果：

![](https://p.ipic.vip/plii96.jpg)

![](https://p.ipic.vip/p4hyjb.jpg)

仓库地址：https://github.com/zhang-wangz/LeetCodeRating

## 总结

如果你需要根据第几场周赛或者分数进行筛选，建议你直接使用网站即可。如果你平时都是在力扣刷题，比如每天做一下力扣的每日一题活动， 那么建议你安装浏览器扩展。另外扩展目前在不断完善中，后续可能增加更多功能，大家有可以去仓库提 issue 或者 pr。
