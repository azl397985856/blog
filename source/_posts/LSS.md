---
title: 一文看懂《最大子序列和问题》
tags: [LeetCode, 数据结构, 算法, 数组]
date: 2020-06-20
categories:
  - [算法, 子序列]
  - [数据结构, 数组]
  - [LeetCode]
---

最大子序列和是一道经典的算法题， leetcode 也有原题《53.maximum-sum-subarray》，今天我们就来彻底攻克它。

<!-- more -->

## 题目描述

求取数组中最大连续子序列和，例如给定数组为 A = [1， 3， -2， 4， -5]， 则最大连续子序列和为 6，即 1 + 3 +（-2）+ 4 = 6。

首先我们来明确一下题意。

- 题目说的子数组是连续的
- 题目只需要求和，不需要返回子数组的具体位置。
- 数组中的元素是整数，可能是正数，负数和 0。
- 子序列的最小长度为 1，不能为空。（这点很讨厌，不过题目就是这样~）

比如：

- 对于数组 [1, -2, 3, 5, -3, 2], 应该返回 3 + 5 = 8
- 对于数组 [0, -2, 3, 5, -1, 2], 应该返回 3 + 5 + -1 + 2 = 9
- 对于数组 [-9, -2, -3, -5, -3], 应该返回 -2（不能返回 0，即什么都不选）

## 解法一 - 暴力法（超时法）

一般情况下，先从暴力解分析，然后再进行一步步的优化。

### 思路

我们来试下最直接的方法，就是计算所有的子序列的和，然后取出最大值。
记 Sum[i,....,j]为数组 A 中第 i 个元素到第 j 个元素的和，其中 0 <= i <= j < n，遍历所有可能的 Sum[i,....,j] 即可。

枚举以 0,1,2...n-1 开头的所有子序列，对于每一个以其开头的子序列，都去枚举从当前开始到索引 n-1 的情况。

这种做法的时间复杂度为 O(N^2), 空间复杂度为 O(1)。

### 代码

JavaScript:

```js
function LSS(list) {
  const len = list.length;
  let max = -Number.MAX_VALUE;
  let sum = 0;
  for (let i = 0; i < len; i++) {
    sum = 0;
    for (let j = i; j < len; j++) {
      sum += list[j];
      if (sum > max) {
        max = sum;
      }
    }
  }

  return max;
}
```

Java：

```java
class MaximumSubarrayPrefixSum {
  public int maxSubArray(int[] nums) {
      int len = nums.length;
      int maxSum = Integer.MIN_VALUE;
      int sum = 0;
      for (int i = 0; i < len; i++) {
        sum = 0;
        for (int j = i; j < len; j++) {
          sum += nums[j];
          maxSum = Math.max(maxSum, sum);
        }
      }
      return maxSum;
  }
}
```

Python 3:

```python
import sys
class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        n = len(nums)
        maxSum = -sys.maxsize
        sum = 0
        for i in range(n):
            sum = 0
            for j in range(i, n):
                sum += nums[j]
                maxSum = max(maxSum, sum)

        return maxSum

```

空间复杂度非常理想，但是时间复杂度有点高。怎么优化呢？我们来看下下一个解法。

## 解法二 - 分治法

### 思路

先把数组平均分成左右两部分。

此时有三种情况：

- 最大子序列全部在数组左部分
- 最大子序列全部在数组右部分
- 最大子序列横跨左右数组

对于前两种情况，我们相当于将原问题转化为了规模更小的同样问题。

对于第三种情况，由于已知循环的一个端点（即中点），我们只需要进行一次循环，分别找出
左边和右边的端点即可。

因此我们可以每次都将数组分成左右两部分，然后分别计算上面三种情况的最大子序列和，取出最大的即可。

举例说明，如下图：

![](https://p.ipic.vip/zxttfx.jpg)
(by [snowan](https://github.com/snowan))

这种做法的时间复杂度为 O(N\*logN), 空间复杂度为 O(1)。

### 代码

JavaScript:

```js
function helper(list, m, n) {
  if (m === n) return list[m];
  let sum = 0;
  let lmax = -Number.MAX_VALUE;
  let rmax = -Number.MAX_VALUE;
  const mid = ((n - m) >> 1) + m;
  const l = helper(list, m, mid);
  const r = helper(list, mid + 1, n);
  for (let i = mid; i >= m; i--) {
    sum += list[i];
    if (sum > lmax) lmax = sum;
  }

  sum = 0;

  for (let i = mid + 1; i <= n; i++) {
    sum += list[i];
    if (sum > rmax) rmax = sum;
  }

  return Math.max(l, r, lmax + rmax);
}

function LSS(list) {
  return helper(list, 0, list.length - 1);
}
```

Java:

```java
class MaximumSubarrayDivideConquer {
  public int maxSubArrayDividConquer(int[] nums) {
      if (nums == null || nums.length == 0) return 0;
      return helper(nums, 0, nums.length - 1);
    }
    private int helper(int[] nums, int l, int r) {
      if (l > r) return Integer.MIN_VALUE;
      int mid = (l + r) >>> 1;
      int left = helper(nums, l, mid - 1);
      int right = helper(nums, mid + 1, r);
      int leftMaxSum = 0;
      int sum = 0;
      // left surfix maxSum start from index mid - 1 to l
      for (int i = mid - 1; i >= l; i--) {
        sum += nums[i];
        leftMaxSum = Math.max(leftMaxSum, sum);
      }
      int rightMaxSum = 0;
      sum = 0;
      // right prefix maxSum start from index mid + 1 to r
      for (int i = mid + 1; i <= r; i++) {
        sum += nums[i];
        rightMaxSum = Math.max(sum, rightMaxSum);
      }
      // max(left, right, crossSum)
      return Math.max(leftMaxSum + rightMaxSum + nums[mid], Math.max(left, right));
    }
}

```

Python 3 :

```python
import sys
class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        return self.helper(nums, 0, len(nums) - 1)
    def helper(self, nums, l, r):
        if l > r:
            return -sys.maxsize
        mid = (l + r) // 2
        left = self.helper(nums, l, mid - 1)
        right = self.helper(nums, mid + 1, r)
        left_suffix_max_sum = right_prefix_max_sum = 0
        sum = 0
        for i in reversed(range(l, mid)):
            sum += nums[i]
            left_suffix_max_sum = max(left_suffix_max_sum, sum)
        sum = 0
        for i in range(mid + 1, r + 1):
            sum += nums[i]
            right_prefix_max_sum = max(right_prefix_max_sum, sum)
        cross_max_sum = left_suffix_max_sum + right_prefix_max_sum + nums[mid]
        return max(cross_max_sum, left, right)

```

## 解法三 - 动态规划

### 思路

上面的分治虽然将问题规模缩小了，但是分解的三个子问题有两个是规模变小的**同样问题**，而有一个不是。 那能不能将其**全部**拆解为**规模更小的同样问题**，并且能找出
递推关系呢? 如果可以，那么我们就可以使用记忆化递归或者动态规划来解决了。

不妨假设问题 Q(list, i) 表示 list 中以索引 i 结尾的情况下最大子序列和，那么原问题就转化为 max(Q(list, i)), 其中 i = 0,1,2...n-1 。

明确了状态， 继续来看下递归关系，这里是 Q(list, i)和 Q(list, i - 1)的关系，即如何根据 Q(list, i - 1) 推导出 Q(list, i)。

如果已知 Q(list, i - 1)， 我们可以将问题分为两种情况，即以索引为 i 的元素终止，或者只有一个索引为 i 的元素。

- 如果以索引为 i 的元素终止， 那么就是 Q(list, i - 1) + list[i]
- 如果只有一个索引为 i 的元素，那么就是 list[i]

分析到这里，递推关系就很明朗了，即`Q(list, i) = Math.max(0, Q(list, i - 1)) + list[i]`

举例说明，如下图：

![53.maximum-sum-subarray-dp.png](https://p.ipic.vip/w8yxqs.jpg)
(by [snowan](https://github.com/snowan))

这种算法的时间复杂度 O(N), 空间复杂度为 O(1)

### 代码

JavaScript:

```js
function LSS(list) {
  const len = list.length;
  let max = list[0];
  for (let i = 1; i < len; i++) {
    list[i] = Math.max(0, list[i - 1]) + list[i];
    if (list[i] > max) max = list[i];
  }

  return max;
}
```

Java:

```java
class MaximumSubarrayDP {
  public int maxSubArray(int[] nums) {
     int currMaxSum = nums[0];
     int maxSum = nums[0];
     for (int i = 1; i < nums.length; i++) {
       currMaxSum = Math.max(currMaxSum + nums[i], nums[i]);
       maxSum = Math.max(maxSum, currMaxSum);
     }
     return maxSum;
  }
}

```

Python 3:

```python
class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        dp = [0] * len(nums)
        ans = dp[0] = nums[0]
        for i in range(1, len(nums)):
            dp[i] = max(nums[i], dp[i - 1] + nums[i])
            ans = max(ans, dp[i])
        return ans

```

## 解法四 - 数学分析（前缀和）

### 思路

最后通过数学分析来看一下这个题目。

定义函数 S(i) ，它的功能是计算以 0（包括 0）开始加到 i（包括 i）的值。那么 S(j) - S(i - 1) 就等于 从 i 开始（包括 i）加到 j（包括 j）的值。

我们进一步分析，实际上我们只需要遍历一次计算出所有的 S(i), 其中 i 等于 0,1,2....,n-1。然后我们再减去之前的 S(k),其中 k 等于 0，1，i - 1，中的最小值即可。 因此我们需要
用一个变量来维护这个最小值，还需要一个变量维护最大值。

这种算法的时间复杂度 O(N), 空间复杂度为 O(1)。

其实很多题目，都有这样的思想， 比如之前的《每日一题 - 电梯问题》。

### 代码

JavaScript:

```js
function LSS(list) {
  const len = list.length;
  let max = list[0];
  let min = 0;
  let sum = 0;
  for (let i = 0; i < len; i++) {
    sum += list[i];
    if (sum - min > max) max = sum - min;
    if (sum < min) {
      min = sum;
    }
  }

  return max;
}
```

Java:

```java
class MaxSumSubarray {
  public int maxSubArray3(int[] nums) {
      int maxSum = nums[0];
      int sum = 0;
      int minSum = 0;
      for (int num : nums) {
        // prefix Sum
        sum += num;
        // update maxSum
        maxSum = Math.max(maxSum, sum - minSum);
        // update minSum
        minSum = Math.min(minSum, sum);
      }
      return maxSum;
  }
}

```

Python 3:

```python
class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        n = len(nums)
        maxSum = nums[0]
        minSum = sum = 0
        for i in range(n):
            sum += nums[i]
            maxSum = max(maxSum, sum - minSum)
            minSum = min(minSum, sum)

        return maxSum

```

## 扩展

如果题目变化为如下，问题该怎么解决呢？

```
求取数组拼接 k 次的最大连续子序列和，例如给定数组为 A = [1， 3， 4， -5] ，k = 2， 拼接会的数组为 [1， 3， 4， -5, 1， 3， 4， -5]，那么最大连续子序列和为 11，即子数组 [1, 3, 4, -5, 1, 3, 4] 的和。
```

直接将 A 拼接 k 次后转化为上面的问题的话空间会超出限制,空间复杂度为 $O(n * k)$。代码：

```py
class Solution:
    def solve(self, A, k):
        A = A * k
        dp = [0] * len(A)
        for i in range(len(A)):
            dp[i] = max(A[i], dp[i - 1] + A[i])
        return max(dp)
```

然而实际上，我们可以仅拼接两次，因为当拼接次数大于 2，那么之后只是无限循环罢了。这种算法空间复杂度可以降低到 $O(n)$。

经过这样的处理，问题转化为求： A 拼接 min(2, k) 次后的最大子序和 + max(0, k-2) 次 A 的和（如果 A 的和小于 0，则不必加）。

代码：

```py
class Solution:
    def solve(self, nums, k):
        if not nums or not k:
            return 0
        A = nums * min(2, k)
        dp = [0] * (len(A) + 1)
        for i in range(len(A)):
            dp[i] = max(A[i], dp[i - 1] + A[i])
        return max(dp) + max(0, sum(nums)) * max(0, (k - 2))
```

## 总结

我们使用四种方法解决了`《最大子序列和问题》`,并详细分析了各个解法的思路以及复杂度，相信下次你碰到相同或者类似的问题的时候也能够发散思维，做到`一题多解，多题一解`。

实际上，我们只是求出了最大的和，如果题目进一步要求出最大子序列和的子序列呢？如果要题目允许不连续呢？ 我们又该如何思考和变通？如何将数组改成二维，求解最大矩阵和怎么计算？
这些问题留给读者自己来思考。
