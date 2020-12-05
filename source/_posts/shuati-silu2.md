---
title: 来和大家聊聊我是如何刷题的（第二弹）
tags: [LeetCode, 刷题方法]
categories: [刷题方法]
date: 2020-12-04
---

上一篇的地址在这里，没有看过的同学建议先看第一篇 [来和大家聊聊我是如何刷题的（第一弹）](https://lucifer.ren/blog/2020/11/29/shuati-silu/)。

今天给大家聊聊怎么刷题， 预计分几篇文章来写，今天是第二篇。

话不多说，直接上干货。

<!-- more -->

## 代码书写技巧

### 改参数

一个简单但是有用的技巧是力扣的参数是可以改名字的。

![](https://tva1.sinaimg.cn/large/0081Kckwly1glawz82w0fj310l0a4wgd.jpg)

你可以将名字改成一个短的或者你熟悉的。比如上面这道题，我写的时候就可以：

```py
class Solution:
    def findMedianSortedArrays(self, A: List[int], B: List[int]) -> float:
        # can use A and B now
```

这可以使得代码看起来**简洁**且具有**一致性**。

经常看我题解的小伙伴应该注意到我的代码比较简洁。一方面是因为我经常用 Python，另一方面就是因为这个技巧。

这里我顺便吐槽一下力扣。力扣的形参命名相当不规范。比如二维数组有时候是 mat，有时候是 nums，有时候是 matrix，有时候又是 grid 。。。 真心不舒服，不过有了这个技巧，大家就不要依赖官方了，自己统一一下就好。

就拿我来说，二维数组我就用 mat 或者 matrix，一维数组用 nums 或者 A 或者 A 和 B（两个一维数组的情况）。比如：

```py
# A 和  B 是两个一维的数组
def test(A, B):
    for a in A:
        # do something
    for b in B:
        # do something else
```

不仅仅是形参的命名要统一，我们的代码也是一样的。对于我来说：

- 堆我习惯叫 h
- 图我习惯叫 graph
- 队列我习惯叫 q
- 。。。

大家没有必要和我一样，但是一定要保持一致性，这样可以显著增加代码可读性，可读性高了，调试工作也会变得轻松。

### zip

力扣有一些题目会给你两个或者三个一维数组，这两个一维数组的是有关联的。

比如给你两个一维数组 A 和 B，其中 A[i] 表示第 i 个人的体重，B[i] 表示第 i 个人的身高。也就是说都是表示第 i 个人，但是表示的东西不一样。

其实就相当于结构体，力扣给你一个数组，其中数组每一项都是结构体是我们日常开发常用的格式。

```ts
interface Person {
  weight: number;
  height: number;
}
```

但是力扣以两个数组的形式给你了，其实这样不难啊，不就是用一个索引记录么？

```java
for(int i= 0;i<A.length;i++) {
    int weight = A[i]
    int height = B[i]
}
```

但是如果，我需要对重量排序呢？如果你仅仅对 A 排序了，B 也需要进行排序，这个时候就不方便了。

这里介绍一个我经常使用的技巧 **zip**。

![](https://tva1.sinaimg.cn/large/0081Kckwly1glaxhfvp7fj311o0e3got.jpg)

代码：

```py
    zipped = zip(A, B)
    # 下面我对其进行排序也不会改变相对顺序
    zipped.sort()
```

另外 zip 还有一些其他用处。比如我想要获取当前数组位置的前一项。

不用 zip 可以这么做：

```py
for i in range(1, len(A)):
    pre = A[i - 1]
    cur = A[i]
```

如果使用 zip 可以这样：

```py
for pre, cur in zip(A, A[1:]):
    # do something
```

> 这个技巧用处不大，可以不必掌握，大家知道有这么回事就行

有的人可能想问，我的语言没有 zip 怎么办？ 我的答案是自行实现 zip。 比如 JavaScript 可以这样实现 zip：

```js
const zip = (rows) => rows[0].map((_, c) => rows.map((row) => row[c]));
```

你把它改造成自己的语言版本即可。

## 调试技巧

### 批量测试

力扣的测试用例其实是可以一次写多个的。

![](https://tva1.sinaimg.cn/large/0081Kckwly1glaxys6s2gj30pi0letcl.jpg)

如上图，该题目有两个参数。那两行其实就是**一个完整用例**。 我这里输入了六行，也就是三个用例。这个时候点击执行，就可以一次执行三个用例。

> 妈妈再也不用担心我提交太频繁啦~

执行成功后，我们可以一次查看所有的差异。

![](https://tva1.sinaimg.cn/large/0081Kckwly1glay1130cnj313j084q3r.jpg)

### 树的可视化

力扣支持大家对树进行可视化，只要点击这个**树结构可视化按钮**即可

![](https://tva1.sinaimg.cn/large/0081Kckwly1glay3e4j34j31450lq0uz.jpg)

如果你写了多个数组，也并不会生成多个树，貌似是以最后一次输入为准。

力扣暂时没有提供其他数据结构的可视化，比如数组，链表等。这可能对大部分人来说没什么，但是对于我这样经常写题解，画图的人就不一样了。如果可以快速画图，那么对我效率肯定有大幅度的提升。

> lucifer 建议大家也养成写题解的好习惯。

因此我打算在我的刷题插件里面加其他数据结构的可视化功能， 已经在规划啦~ 现在草稿了一些东西。

比如这样的树：

![](https://tva1.sinaimg.cn/large/0081Kckwly1glay88vsibj30yq0o9mz5.jpg)

和这样的树：

![](https://tva1.sinaimg.cn/large/0081Kckwly1glayb242idj30n509fmy9.jpg)

现在其实还有些问题，而且我想多加几种数据结构方便写题解，所以就之后再说好了。

## 絮叨

上次给大家说了要总结和记忆模板。还说了给我的插件加一个模板功能， 我果然很可靠！

自古深情留不住，唯有套路得人心。 我的刷题插件给大家准备了几种常见的模板帮你快速高效解题。 比如下面这个 hard 题目， 就是一个 BFS 模板 + 状态压缩模板，类似的题目数不胜数，基本都是套个模板改几个地方就过了。

再比如，下面这个 1439 hard 题， 不就一个二分模板（最左满足条件） + 二维网格 DFS 么？

![](https://tva1.sinaimg.cn/large/0081Kckwly1glawnsz0n9j306o06lgmx.jpg)

给大家提供多种刷题模板，可以直接复制使用。 各个模板都有都有的题目，大家可以直达题目进行”默写“。

![](https://tva1.sinaimg.cn/large/0081Kckwly1glawoq00uwj30pb09ogmo.jpg)

![](https://tva1.sinaimg.cn/large/0081Kckwly1glawp0t0vlj30mm0h2ta4.jpg)

插件地址：https://chrome.google.com/webstore/detail/leetcode-cheatsheet/fniccleejlofifaakbgppmbbcdfjonle?hl=en-US。

另外我的插件后续计划增加更多功能以及上架商店，有消息我会通过公众号和大家同步。

## 预告

下期给大家讲更加干货的技巧。

- 一看就会，一写就废， 如何克服？
- **如何锁定使用哪种算法**。比如我看到了这道题，我怎么知道该用什么解法呢？二分？动态规划？
