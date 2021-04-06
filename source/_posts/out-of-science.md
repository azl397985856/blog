---
title: 为何我刷了很多，遇到新的题还是唯唯诺诺，无法重拳出击？
tags: [走出科学]
categories: [走出科学]
date: 2021-04-06
---

为何我刷了很多题，遇到新的题还是唯唯诺诺，无法重拳出击？为何一看就会一些就废？这其中又隐藏着怎样的秘密？究竟是道德的沦丧还是人性的扭曲？欢迎收看本期的 **走出科学** 特别栏目。

今天给大家带来了**三位重量级选手**，一位体重 98 公斤，一位体重 100 公斤，还有一位体重 98 斤，今天 lucifer 就带大家用同样的招式 KO 他们三位。

<!-- more -->

# 第一位选手 - 84. 柱状图中最大的矩形

## 题目地址

https://leetcode-cn.com/problems/largest-rectangle-in-histogram/

## 题目描述

给定 n 个非负整数，用来表示柱状图中各个柱子的高度。每个柱子彼此相邻，且宽度为 1 。

求在该柱状图中，能够勾勒出来的矩形的最大面积。

![](https://tva1.sinaimg.cn/large/007S8ZIlly1ghltx8sr4uj305805odfn.jpg)

以上是柱状图的示例，其中每个柱子的宽度为 1，给定的高度为  [2,1,5,6,2,3]。

![](https://tva1.sinaimg.cn/large/007S8ZIlly1ghltx9kgd2j305805oa9z.jpg)

图中阴影部分为所能勾勒出的最大矩形面积，其面积为  10  个单位。

```
示例：

输入：[2,1,5,6,2,3]
输出：10

```

## 公司

- 阿里
- 腾讯
- 百度
- 字节

## 前置知识

- 单调栈

## 暴力枚举 - 左右端点法（TLE）

### 思路

我们暴力尝试`所有可能的矩形`。由于矩阵是二维图形， 我我们可以使用`左右两个端点来唯一确认一个矩阵`。因此我们使用双层循环枚举所有的可能性即可。 而矩形的面积等于`（右端点坐标 - 左端点坐标 + 1) * 最小的高度`，最小的高度我们可以在遍历的时候顺便求出。

### 代码

```python
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        n, ans = len(heights), 0
        if n != 0:
            ans = heights[0]
        for i in range(n):
            height = heights[i]
            for j in range(i, n):
                height = min(height, heights[j])
                ans = max(ans, (j - i + 1) * height)
        return ans
```

**复杂度分析**

- 时间复杂度：$O(N^2)$
- 空间复杂度：$O(1)$

## 暴力枚举 - 中心扩展法（TLE）

### 思路

我们仍然暴力尝试`所有可能的矩形`。只不过我们这一次从中心向两边进行扩展。对于每一个 i，我们计算出其左边第一个高度小于它的索引 p，同样地，计算出右边第一个高度小于它的索引 q。那么以 i 为最低点能够构成的面积就是`(q - p - 1) * heights[i]`。 这种算法毫无疑问也是正确的。 我们证明一下，假设 f(i) 表示求以 i 为最低点的情况下，所能形成的最大矩阵面积。那么原问题转化为`max(f(0), f(1), f(2), ..., f(n - 1))`。

具体算法如下：

- 我们使用 l 和 r 数组。l[i] 表示 左边第一个高度小于它的索引，r[i] 表示 右边第一个高度小于它的索引。
- 我们从前往后求出 l，再从后往前计算出 r。
- 再次遍历求出所有的可能面积，并取出最大的。

### 代码

```python
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        n = len(heights)
        l, r, ans = [-1] * n, [n] * n, 0
        for i in range(1, n):
            j = i - 1
            while j >= 0 and heights[j] >= heights[i]:
                j -= 1
            l[i] = j
        for i in range(n - 2, -1, -1):
            j = i + 1
            while j < n and heights[j] >= heights[i]:
                j += 1
            r[i] = j
        for i in range(n):
            ans = max(ans, heights[i] * (r[i] - l[i] - 1))
        return ans

```

**复杂度分析**

- 时间复杂度：$O(N^2)$
- 空间复杂度：$O(N)$

## 优化中心扩展法（Accepted）

### 思路

实际上我们内层循环没必要一步一步移动，我们可以直接将`j -= 1` 改成 `j = l[j]`, `j += 1` 改成 `j = r[j]`。

### 代码

```python
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        n = len(heights)
        l, r, ans = [-1] * n, [n] * n, 0

        for i in range(1, n):
            j = i - 1
            while j >= 0 and heights[j] >= heights[i]:
                j = l[j]
            l[i] = j
        for i in range(n - 2, -1, -1):
            j = i + 1
            while j < n and heights[j] >= heights[i]:
                j = r[j]
            r[i] = j
        for i in range(n):
            ans = max(ans, heights[i] * (r[i] - l[i] - 1))
        return ans

```

**复杂度分析**

- 时间复杂度：$O(N)$
- 空间复杂度：$O(N)$

## 单调栈（Accepted）

### 思路

实际上，读完第二种方法的时候，你应该注意到了。我们的核心是求左边第一个比 i 小的和右边第一个比 i 小的。 如果你熟悉单调栈的话，那么应该会想到这是非常适合使用单调栈来处理的场景。

从左到右遍历柱子，对于每一个柱子，我们想找到第一个高度小于它的柱子，那么我们就可以使用一个单调递增栈来实现。 如果柱子大于栈顶的柱子，那么说明不是我们要找的柱子，我们把它塞进去继续遍历，如果比栈顶小，那么我们就找到了第一个小于的柱子。 **对于栈顶元素，其右边第一个小于它的就是当前遍历到的柱子，左边第一个小于它的就是栈中下一个要被弹出的元素**，因此以当前栈顶为最小柱子的面积为**当前栈顶的柱子高度 \* (当前遍历到的柱子索引 - 1 - (栈中下一个要被弹出的元素索引 + 1) + 1)**，化简一下就是 **当前栈顶的柱子高度 \* (当前遍历到的柱子索引 - 栈中下一个要被弹出的元素索引 - 1)**。

这种方法只需要遍历一次，并用一个栈。由于每一个元素最多进栈出栈一次，因此时间和空间复杂度都是$O(N)$。

为了统一算法逻辑，减少边界处理，我在 heights 首尾添加了两个哨兵元素，**这样我们可以保证所有的柱子都会出栈**。

### 代码

代码支持： Python,CPP

Python Code:

```python
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        n, heights, st, ans = len(heights), [0] + heights + [0], [], 0
        for i in range(n + 2):
            while st and heights[st[-1]] > heights[i]:
                ans = max(ans, heights[st.pop(-1)] * (i - st[-1] - 1))
            st.append(i)
        return ans
```

CPP Code:

```cpp
class Solution {
public:
    int largestRectangleArea(vector<int>& A) {
        A.push_back(0);
        int N = A.size(), ans = 0;
        stack<int> s;
        for (int i = 0; i < N; ++i) {
            while (s.size() && A[s.top()] >= A[i]) {
                int h = A[s.top()];
                s.pop();
                int j = s.size() ? s.top() : -1;
                ans = max(ans, h * (i - j - 1));
            }
            s.push(i);
        }
        return ans;
    }
};
```

**复杂度分析**

- 时间复杂度：$O(N)$
- 空间复杂度：$O(N)$

2020-05-30 更新：

有的观众反应看不懂为啥需要两个哨兵。 其实末尾的哨兵就是为了将栈清空，防止遍历完成栈中还有没参与运算的数据。

而前面的哨兵有什么用呢？ 我这里把上面代码进行了拆解：

```py
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        n, heights, st, ans = len(heights),[0] + heights + [0], [], 0
        for i in range(n + 2):
            while st and heights[st[-1]] > heights[i]:
                a = heights[st[-1]]
                st.pop()
                # 如果没有前面的哨兵，这里的 st[-1] 可能会越界。
                ans = max(ans, a * (i - 1 - st[-1]))
            st.append(i)
        return ans
```

## 相关题目

- [42.trapping-rain-water](https://github.com/azl397985856/leetcode/blob/master/problems/42.trapping-rain-water.md)

# 第二位选手 - 85. 最大矩形

## 题目地址

https://leetcode-cn.com/problems/maximal-rectangle/

## 题目描述

给定一个仅包含  0 和 1 的二维二进制矩阵，找出只包含 1 的最大矩形，并返回其面积。

示例：

输入：

```
[
  ["1","0","1","0","0"],
  ["1","0","1","1","1"],
  ["1","1","1","1","1"],
  ["1","0","0","1","0"]
]
```

输出：6

## 前置知识

- 单调栈

## 公司

- 阿里
- 腾讯
- 百度
- 字节

## 思路

我在 [【84. 柱状图中最大的矩形】多种方法（Python3）](https://leetcode-cn.com/problems/largest-rectangle-in-histogram/solution/84-zhu-zhuang-tu-zhong-zui-da-de-ju-xing-duo-chong/) 使用了多种方法来解决。 然而在这道题，我们仍然可以使用完全一样的思路去完成。本题解是基于那道题的题解来进行的。

拿题目给的例子来说：

```
[
  ["1","0","1","0","0"],
  ["1","0","1","1","1"],
  ["1","1","1","1","1"],
  ["1","0","0","1","0"]
]
```

我们逐行扫描得到 `84. 柱状图中最大的矩形` 中的 heights 数组：

![](https://tva1.sinaimg.cn/large/007S8ZIlly1ghlu7999xyj30t21cgtcn.jpg)

这样我们就可以使用`84. 柱状图中最大的矩形` 中的解法来进行了，这里我们使用单调栈来解。

下面的代码直接将 84 题的代码封装成 API 调用了。

## 代码

代码支持：Python

Python Code:

```python
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        n, heights, st, ans = len(heights), [0] + heights + [0], [], 0
        for i in range(n + 2):
            while st and heights[st[-1]] > heights[i]:
                ans = max(ans, heights[st.pop(-1)] * (i - st[-1] - 1))
            st.append(i)

        return ans
    def maximalRectangle(self, matrix: List[List[str]]) -> int:
        m = len(matrix)
        if m == 0: return 0
        n = len(matrix[0])
        heights = [0] * n
        ans = 0
        for i in range(m):
            for j in range(n):
                if matrix[i][j] == "0":
                    heights[j] = 0
                else:
                    heights[j] += 1
            ans = max(ans, self.largestRectangleArea(heights))
        return ans

```

**复杂度分析**

- 时间复杂度：$O(M * N)$
- 空间复杂度：$O(N)$

# 第三位选手 - 221. 最大正方形

## 题目地址

https://leetcode-cn.com/problems/maximal-square/

## 题目描述

```
在一个由 0 和 1 组成的二维矩阵内，找到只包含 1 的最大正方形，并返回其面积。

示例:

输入:

1 0 1 0 0
1 0 1 1 1
1 1 1 1 1
1 0 0 1 0

输出: 4

```

## 前置知识

- 动态规划
- 递归

## 公司

- 阿里
- 腾讯
- 百度
- 字节

## 思路

看到题看起来和上面的题目类似，只不过把长方形限定为了正方形嘛。

![221.maximal-square](https://tva1.sinaimg.cn/large/007S8ZIlly1ghludl52xfj30bo09vmxo.jpg)

符合直觉的做法是暴力求解处所有的正方形，逐一计算面积，然后记录最大的。这种时间复杂度很高。

我们考虑使用动态规划，我们使用 dp[i][j]表示以 matrix[i][j]为右下角的顶点的可以组成的最大正方形的边长。
那么我们只需要计算所有的 i，j 组合，然后求出最大值即可。

我们来看下 dp[i][j] 怎么推导。 首先我们要看 matrix[i][j], 如果 matrix[i][j]等于 0，那么就不用看了，直接等于 0。
如果 matrix[i][j]等于 1，那么我们将 matrix[[i][j]分别往上和往左进行延伸，直到碰到一个 0 为止。

如图 dp[3][3] 的计算。 matrix[3][3]等于 1，我们分别往上和往左进行延伸，直到碰到一个 0 为止，上面长度为 1，左边为 3。
dp[2][2]等于 1（之前已经计算好了），那么其实这里的瓶颈在于三者的最小值, 即`Min(1, 1, 3)`, 也就是`1`。 那么 dp[3][3] 就等于
`Min(1, 1, 3) + 1`。

![221.maximal-square](https://tva1.sinaimg.cn/large/007S8ZIlly1ghludlnra9j30an08xt96.jpg)

dp[i - 1][j - 1]我们直接拿到，关键是`往上和往左进行延伸`, 最直观的做法是我们内层加一个循环去做就好了。
但是我们仔细观察一下，其实我们根本不需要这样算。 我们可以直接用 dp[i - 1][j]和 dp[i][j -1]。
具体就是`Min(dp[i - 1][j - 1], dp[i][j - 1], dp[i - 1][j]) + 1`。

![221.maximal-square](https://tva1.sinaimg.cn/large/007S8ZIlly1ghludm7ilmj30a507sglz.jpg)

事实上，这道题还有空间复杂度 O(N)的解法，其中 N 指的是列数。
大家可以去这个[leetcode 讨论](https://leetcode.com/problems/maximal-square/discuss/61803/C%2B%2B-space-optimized-DP)看一下。

## 关键点解析

- DP
- 递归公式可以利用 dp[i - 1][j]和 dp[i][j -1]的计算结果，而不用重新计算
- 空间复杂度可以降低到 O(n), n 为列数

## 代码

代码支持：Python，JavaScript：

Python Code：

```python
class Solution:
    def maximalSquare(self, matrix: List[List[str]]) -> int:
        res = 0
        m = len(matrix)
        if m == 0:
            return 0
        n = len(matrix[0])
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1 if matrix[i - 1][j - 1] == "1" else 0
                res = max(res, dp[i][j])
        return res ** 2
```

JavaScript Code：

```js
/*
 * @lc app=leetcode id=221 lang=javascript
 *
 * [221] Maximal Square
 */
/**
 * @param {character[][]} matrix
 * @return {number}
 */
var maximalSquare = function (matrix) {
  if (matrix.length === 0) return 0;
  const dp = [];
  const rows = matrix.length;
  const cols = matrix[0].length;
  let max = Number.MIN_VALUE;

  for (let i = 0; i < rows + 1; i++) {
    if (i === 0) {
      dp[i] = Array(cols + 1).fill(0);
    } else {
      dp[i] = [0];
    }
  }

  for (let i = 1; i < rows + 1; i++) {
    for (let j = 1; j < cols + 1; j++) {
      if (matrix[i - 1][j - 1] === "1") {
        dp[i][j] = Math.min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1]) + 1;
        max = Math.max(max, dp[i][j]);
      } else {
        dp[i][j] = 0;
      }
    }
  }

  return max * max;
};
```

**复杂度分析**

- 时间复杂度：$O(M * N)$，其中 M 为行数，N 为列数。
- 空间复杂度：$O(M * N)$，其中 M 为行数，N 为列数。

## 如果我还想用上面的方法可以么？

当然可以！ lucifer 我就专门给大家改写了一下，直接将上面的代码复制过来，改了一行就 AC 了。

```py
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        n, heights, st, ans = len(heights), [0] + heights + [0], [], 0
        for i in range(n + 2):
            while st and heights[st[-1]] > heights[i]:
                # 就只改了下面这一行
                ans = max(ans, min(heights[st.pop()], (i - st[-1] - 1)) ** 2)
            st.append(i)

        return ans

    def maximalSquare(self, matrix: List[List[str]]) -> int:
        m = len(matrix)
        if m == 0:
            return 0
        n = len(matrix[0])
        heights = [0] * n
        ans = 0
        for i in range(m):
            for j in range(n):
                if matrix[i][j] == "0":
                    heights[j] = 0
                else:
                    heights[j] += 1
            ans = max(ans, self.largestRectangleArea(heights))
        return ans
```

## 总结

上面三道题我都用的是 **largestRectangleArea** 的核心逻辑，基本上调用下稍微改改就完事了。对于 **largestRectangleArea** 的解法最明显的莫过于平方级别的暴力，可如果你仔细分析就发现我们可以通过**指针不回溯**达到降低复杂度的效果。而这里的指针不回溯可以是单调栈，也可以是我给的双指针数组方法。不管用的哪种，区别的只是战术，战略思想是一样的。大家做题的时候也要注重战略，训练战术。

你说这招是不是很好使？学习算法不可贪多，不然嚼不烂。当你细细咀嚼后会发现，其实算法的思想和套路还真不多，至少应付大部分的面试和 OJ 题目不成问题。
