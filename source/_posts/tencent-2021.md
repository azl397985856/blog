---
title: 腾讯校招还考抛物线？
tags: [校招]
date: 2021-12-13
categories:
  - [校招]
---

昨天翻了一下牛客网的腾讯 2021 校园招聘技术类**编程题汇总**，一共有五道题目。难度大不大？我们来看下！

具体代码我就不贴了，大家如果看了我的思路还是写不出来可以来我的校招群来问，大家可以在公众号后台回复校招进群。

题目地址：https://www.nowcoder.com/test/30545524/summary

<!-- more -->

## 第一题

### 题目描述

现在有 $10^5$ 个用户，编号为 1-$10^5$，现在已知有 m 对关系，每一对关系给你两个数 x 和 y ，代表编号为 x 的用户和编号为 y 的用户是在一个圈子中，例如： A 和 B 在一个圈子中， B 和 C 在一个圈子中，那么 A , B , C 就在一个圈子中。现在想知道最多的一个圈子内有多少个用户。

![](https://p.ipic.vip/1k6kyp.jpg)

### 思路

我们可以将用户抽象为点，用户的关系抽象为边。那么问题转化为最大联通子图。我们可以使用并查集来解决，直接套用下我的并查集模板即可解决。模板可以在我的刷题插件中找到，插件说明：https://github.com/azl397985856/leetcode-cheat

## 第二题

### 题目描述

输入一个字符串 s，s 由小写英文字母组成，保证 s 长度小于等于 5000 并且大于等于 1。在 s 的所有不同的子串中，输出字典序第 k 小的字符串。
字符串中任意个连续的字符组成的子序列称为该字符串的子串。
字母序表示英文单词在字典中的先后顺序，即先比较第一个字母，若第一个字母相同，则比较第二个字母的字典序，依次类推，则可比较出该字符串的字典序大小。

![](https://p.ipic.vip/qdpoxm.jpg)

### 思路

我们可以枚举所有的子串，这需要 $n^2$的时间复杂度。 接下来，我们排序取 第 k 个，或者使用堆来取第 k 个都是可以的。

有一点需要注意： 由于子串可能重复，因此我们需要去重。以题目中的 aabb 来说， a 这个子串其实有两个，但是算答案的时候仅仅算一个。

## 第三题

### 题目描述

![](https://p.ipic.vip/mg8q7x.jpg)

### 思路

。。。 非常郁闷。为什么会考这种题？

这道题可以用微积分的知识来解。具体来说，我们可以根据 A，B，C 的值求出交点（两个交点），然后对 y 做积分，求出定积分的值即为所求的面积。

91 天学算法群里的数学大佬 @空识 给了一个计算方法，大家可以参考一下。

![](https://p.ipic.vip/7ykfng.jpg)

## 第四题

### 题目描述

数据结构基础之一——队列
队列有五种基本操作，插入队尾、取出队首、删除队首、队列大小、清空队列。

现在让你模拟一个队列的操作，具体格式参考输入。

注意本题有多组输入。

![](https://p.ipic.vip/7cpdwa.jpg)

### 思路

由于时间复杂度需要 $O(1)$，因此无法使用数组来模拟，我们需要使用链表来模拟。代码可以参考一下双端队列的源码。

如果大家实现有困难，可以先尝试使用数组来模拟，然后改为链表。由于链表和数组其实都是线性数据结构，只是具体 api 不一样，因此改起来只要掌握方法很容易。

## 第五题

### 题目描述

界面中存在 id=jsContainer 的节点 A，系统会随机生成 id 为 jsLayout 的 m 行 x n 列 表格(m >= 3, n >= 3)，并随机选中一个 td 节点，请按照如下需求实现 bind 函数
1、bind 函数为每个 td 节点绑定 click 事件，当某个 td 节点被点击时 class 变为 current，同时以该 td 为中心的同一行和同一列 td 节点 class 变为 wrap，具体效果参考以下图片
2、每次 click 后，请清空所有不需要变动的 td 节点的 class
3、请不要手动调用 bind 函数
4、当前界面为系统生成 $9 * 9$ 表格，执行 bind 函数，并点击其中 td 后的效果
5、请不要手动修改 html 和 css
6、不要使用第三方插件

![](https://p.ipic.vip/vxsjsa.jpg)

题目预设代码：

```html
<div id="jsContainer">
  <table class="game">
    <tbody>
      <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td class="wrap"></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td class="wrap"></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td class="wrap"></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td class="wrap"></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td class="wrap"></td>
        <td class="wrap"></td>
        <td class="wrap"></td>
        <td class="wrap"></td>
        <td class="current"></td>
        <td class="wrap"></td>
        <td class="wrap"></td>
        <td class="wrap"></td>
        <td class="wrap"></td>
      </tr>
      <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td class="wrap"></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td class="wrap"></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td class="wrap"></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td class="wrap"></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
      </tr>
    </tbody>
  </table>
</div>
```

```css
table.game {
  font-size: 14px;
  border-collapse: collapse;
  width: 100%;
  table-layout: fixed;
}
table.game td {
  border: 1px solid #e1e1e1;
  padding: 0;
  height: 30px;
  text-align: center;
}
table.game td.current {
  background: #1890ff;
}
table.game td.wrap {
  background: #f5f5f5;
}
```

```js
function bind() {}
```

### 思路

这是一个前端题目。

由于只可以修改 js，因此我们可以：

1. 使用事件代理在最外层绑定 click 事件

2. click 处理函数判断 event target 是第几行，第几列，从而给格子添加不同 class。比如 event target 是第 x 行，第 y 列，那么只需要给 x 行 y 列设置 current，给 x 行 **其他** 以及 y 列 **其他** 设置 wrap，最后清空**其他**单元格 class 即可。

## 总结

五道题难度除了积分求面试这道题有点不太常规之外，其他都是很常见的题目，难度也不大。

- 第一题是常规的并查集的题目，基本属于最简单的并查集了。
- 第二题纯暴力其实也可以解决。
- 第三题，emmmm
- 第四题，实现一个队列。很常规的一个题目了，唯一需要注意的是使用链表来模拟。
- 第五题，是一个前端题目。考察事件代理，以及基本的 dom 操作。
