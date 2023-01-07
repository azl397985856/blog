---
title: 为什么eslint没有 no-magic-string？
tags: [前端, eslint]
date: 2020-05-05
categories:
  - [前端, eslint]
---

最近参加了几次公司组内的 Code Review， 发现了一些问题。其中一些问题可以通过工具（比如 eslint）解决。 我们就想着通过工具自动化的方式进行解决。 而这些工具中有一些是现成的，比如 魔法数。 大家对魔法数的看法也是莫衷一是。本文通过`讲解什么是魔法数，eslint 是怎么检查魔法数的，以及思考为什么eslint 偏爱数字，而不是偏爱字符串来` 来深入剖析一下魔法数。

<!-- more -->

## 计算机科学中的魔法数

什么是魔法数？ 这里我摘取了维基百科的解释：

> 程序设计中所谓的魔术数字（magic number）可能有以下含意：

    •	缺乏解释或命名的独特数值
    •	用于识别一个文件格式或协议的一段常量或字符串，例如UNIX的特征签名
    •	防止误作他用的一段数值，例如UUID

实际上魔法数真的是一个很古老的话题了。从我刚从业开始，就不停听到这样的词语。大家都对此深恶痛绝，不想看到别人的魔法数，但是时不时自己也会写一些魔法数。 如果你经常做算法题，肯定对此深有感受。 很多人（或许包括我自己）喜欢通过魔法数来炫技。当然我的心理倒不仅仅是炫技这么简单，也掺杂了诸如“这个很显然易见”，“这个我也不知道怎么起名字”的想法。

## eslint 中的魔法数

eslint 有一个 rule 是 no-magic-number. 为什么没有类似的比如 no-magic-string?

我们首先来看下什么是”no-magic-number”。 根据 eslint 官方描述来看，其是通过确保数字被显式赋予一个常量，从而增加代码可读性和可维护性。

如下代码被认为是不好的：

```js
/*eslint no-magic-numbers: “error”*/
var dutyFreePrice = 100,
  finalPrice = dutyFreePrice + dutyFreePrice * 0.25;
```

而这段代码被认为是好的：

```js
/*eslint no-magic-numbers: “error”*/
var TAX = 0.25;

var dutyFreePrice = 100,
  finalPrice = dutyFreePrice + dutyFreePrice * TAX;
```

这两段代码有什么不同？为什么下面的代码被认为是好的？

## 一窥 eslint 源码

通过阅读源码，我发现代码有这样一句：

```js
// utils/ast-utils.js
function isNumericLiteral(node) {
  return (
    node.type === "Literal" &&
    (typeof node.value === "number" || Boolean(node.bigint))
  );
}
// no-magic-numbers.js
if (!isNumericLiteral(node)) {
  return;
}
```

也就是说如果字面量不是数字会被忽略。这和我们的想法`这条规则只会检查魔法数字，而不会检查诸如魔法字符串等`。

让我们时光倒流，将代码回退到 eslint 官方首次关于”no-magic-rule”的[提交](https://github.com/eslint/eslint/blob/510013c27eb917cd4c7268d5deb6301243b182cf/lib/rules/no-magic-number.js)。

![](https://p.ipic.vip/n6pgqi.jpg)

代码大概意思是：

1. 如果是变量声明语句，就去检查是否强制使用 const。 如果是则观察语句是否为 const 声明。
2. 对于其他情况，直接检查父节点的类型。
   2.1. 如果检查对象内部的魔法数字，则直接报错。
   2.2. 如果不需要检查对象类型，则进行规则过滤，即如果是`[“ObjectExpression”,“Property”,“AssignmentExpression”]` 中的一种的话也是没问题的。其他情况报错。

那么上面的三种类型是什么呢？

从名字不难发现，其中 AssignmentExpression 和 ObjectExpression 属于表达式。 而 Property 则是对象属性。

ObjectExpression 的例子：

```
a = {}
```

> 思考题：为什么 ObjectExpression 也是不被允许的？
> AssignmentExpression 的例子：

```js
a = b = 2;
```

Property 的例子：

```
a = { number: 1 }
```

也就是说，如果设置了`检查对象`，那么上面三种情况都会报错。否则不进行报错处理。

## AST-Explorer

大家使用[AST explorer](https://astexplorer.net/#/gist/a595f16646dbbb4184afc3880b87aa2c/276fd81226015b7782056947b70c4b9e047113c9) 来可视化 AST。

![](https://p.ipic.vip/srxts2.jpg)

由于 eslint 使用的 ast 转化工具是 espree， 推荐大家使用 espree。 如果大家写 babel 插件的话，相应的引擎最好修改一下。

值得注意的是，上面我们用的 parent 是不会在 ast-explorer 进行显示的。原因在于其不是 ast 结构的一部分，而如果要做到，也非常容易。 前提是你懂得递归，尤其是树的递归。 如果你还不太懂树的递归， 可以关注我的 B 站[LeetCode 加加的个人空间 - 哔哩哔哩 ( ゜- ゜)つロ 乾杯~ Bilibili](https://space.bilibili.com/519510412)

通过观察 eslint/espree 的源码也可以发现，其过程是多么的自然和简单。

![](https://p.ipic.vip/6d5sdv.jpg)

## Magic String

实际上一个第三方的 tslint 仓库的一个[issue](https://github.com/palantir/tslint/issues/2928) 明确指出了想要增加”no
-magic-string” 的想法，只不过被仓库成员给否掉了，原因是其不够通用，除非能证明大家都需要这样一个规则。

那么问题是“为什么 no-magic-string 没有 no-magic-number 通用呢”？[【每日一题】- 2020-05-05 - no-magic-string · Issue #122 · azl397985856/fe-interview · GitHub](https://github.com/azl397985856/fe-interview/issues/122#issuecomment-623997774) 有一个回答，小漾给出了很好的回答。但是还没有解决疑问“为什么没有 no-magic-string”这样的规则呢？

我的观点是`魔法字符串也是不好的，只不过没有不好的那么明显`。

我们来看个例子：

```js
name = "lucifer";
a = "hello, " + name;
if (type === "add") {
} else if (type == "edit") {
}
```

如上代码，就可以被认定为 `magic string`。但是其在现实代码中是非常普遍的，并且不对我们造成很大的困扰。如果对其改写会是这样的：

```js
name = "lucifer";
const PRFIX = "hello, ";
const TYPE_ADD = "add";
const TYPE_EDIT = "edit";
a = prefix + name;
if (type === TYPE_ADD) {
} else if (type == TYPE_EDIT) {
}
```

再来看看数字：

```js
if (type === 1) {
  //
}

if (total > 5) {
  //
}
```

如上是我实际工作中见到过的例子，还算有代表性。 上面的代码，如果不通读代码或者事先有一些背景知识，我们根本无从知晓代码的准确含义。

还有一个地方，是数字不同于字符串的。 那就是数字可能是一个无限小数。计算机无法精确表示。 那么程序就不得不进行合理近似，而如果同一个程序不同地方采用的近似手段不同，那么就会有问题。而不使用魔法数就可以就可以避免这个问题。 举个例子：

我们需要计算一个圆的面积，可能会这样做：

```
area = 3.1415 * R ** 2
```

```
area = 3.141516 * R ** 2
```

这样就会有问题了。 而如果我们将 PI 的值抽离到一个变量去维护，任何代码都取这个变量的值就不会有问题。那么有人可能有这样的疑问`字符串如果拼写错了，是不是也是一样的么？`

比如：

```
// a.js
if (type == 'add') {...}
// b.js
if (type == 'addd') {...}
```

事实上，这样的事情很有可能发生。 只不过这种问题相比于数字来说更容易被发现而已。

这么看来魔法数字确实给大家带来了很大的困扰，那么我们是否应该全面杜绝魔法数呢？

## 取舍之间

真的魔法数字(字符串吧)就是不好的么？其实也不见得。

下面再来看一个我实际工作中碰到的例子：

```js
MS = 0;
if (type === "day") {
  MS = 24 * 60 * 60 * 1000;
}
if (type === "week") {
  MS = 7 * 24 * 60 * 60 * 1000;
}
```

这种代码我不知道看了多少遍了。 或许这在大家眼中已然成为了一种共识，那么这种所谓的魔法数字代码的不可读问题就不存在了。 我们仍可以轻易知道代码的含义。

如果将其进行改造：

```js
MS = 0;
const HOURS_PER_DAY = 24;
const MINUTES_PER_HOUR = 60;
const SECONDs_PER_MINUTE = 60;
const MS_PER_SECOND = 1000;
const DAYS_PER_WEEK = 7;
if (type === "day") {
  MS = HOURS_PER_DAY * MINUTES_PER_HOUR * SECONDs_PER_MINUTE * MS_PER_SECOND;
}
if (type === "week") {
  MS =
    DAYS_PER_WEEK *
    HOURS_PER_DAY *
    MINUTES_PER_HOUR *
    SECONDs_PER_MINUTE *
    MS_PER_SECOND;
}
```

上面的代码不见的要比上面的好到哪里。 `《程序设计实践》`提到了一点“变量命令不是越长越好，越具体越好，而是根据具体的限定范围”。 比如你在 queue 的 class 中定义的 size 字段可以直接叫 size ，而不是 queue_size。

那么一些社会或者编码常识何尝不是一种限定呢？ 如果是的话， 我们是否可以不用特殊限定，而回归到“魔法数”呢？
