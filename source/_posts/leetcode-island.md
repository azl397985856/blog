---
title: 【LeetCode日记】 1162. 地图分析
tags: [数据结构, 算法, LeetCode日记]
date: 2020-06-13
categories:
  - [数据结构, hashtable]
  - [算法, BFS]
---

LeetCode 上有很多小岛题，虽然官方没有这个标签， 但是在我这里都差不多。不管是思路还是套路都比较类似，大家可以结合起来练习。

- [200.number-of-islands](https://github.com/azl397985856/leetcode/blob/master/problems/200.number-of-islands.md)
- [695.max-area-of-island](https://leetcode-cn.com/problems/max-area-of-island/solution/695-dao-yu-de-zui-da-mian-ji-dfspython3-by-fe-luci/)

​<!-- more -->

原题地址：https://leetcode-cn.com/problems/as-far-from-land-as-possible/

## 思路

这里我们继续使用上面两道题的套路，即不用 visited，而是原地修改。由于这道题求解的是最远的距离，而距离我们可以使用 BFS 来做。算法：

- 对于每一个海洋，我们都向四周扩展，寻找最近的陆地，每次扩展 steps 加 1。
- 如果找到了陆地，我们返回 steps。
- 我们的目标就是所有 steps 中的最大值。

实际上面算法有很多重复计算，如图中间绿色的区域，向外扩展的时候，如果其周边四个海洋的距离已经计算出来了，那么没必要扩展到陆地。实际上只需要扩展到周边的四个海洋格子就好了，其距离陆地的最近距离就是 1 + 周边四个格子中到达陆地的最小距离。

![](https://p.ipic.vip/tod9l3.jpg)

我们考虑优化。

- 将所有陆地加入队列，而不是海洋。
- 陆地不断扩展到海洋，每扩展一次就 steps 加 1，直到无法扩展位置。
- 最终返回 steps 即可。

图解：

![](https://p.ipic.vip/e2psd1.jpg)

## 代码

```python
class Solution:
    def maxDistance(self, grid: List[List[int]]) -> int:
        n = len(grid)
        steps = -1
        queue = [(i, j) for i in range(n) for j in range(n) if grid[i][j] == 1]
        if len(queue) == 0 or len(queue) == n ** 2: return steps
        while len(queue) > 0:
            for _ in range(len(queue)):
                x, y = queue.pop(0)
                for xi, yj in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
                    if xi >= 0 and xi < n and yj >= 0 and yj < n and grid[xi][yj] == 0:
                        queue.append((xi, yj))
                        grid[xi][yj] = -1
            steps += 1

        return steps
```

> 由于没有 early return，steps 其实会多算一次。 我们可以返回值减去 1，也可以 steps 初始化为-1。这里我选择是 steps 初始化为-1

**_复杂度分析_**

- 时间复杂度：$O(N ^ 2)$
- 空间复杂度：$O(N ^ 2)$

## 优化

由于数组删除第一个元素（上面代码的 queue.pop(0)）是$O(N)$的时间复杂度，我们可以使用 deque 优化，代码如下：

```python
   def maxDistance(self, grid: List[List[int]]) -> int:
        from collections import deque
        N = len(grid)
        steps = -1
        q = deque([(i, j) for i in range(N) for j in range(N) if grid[i][j] == 1])
        if len(q) == 0 or len(q) == N ** 2:
            return steps
        move = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        while len(q) > 0:
            for _ in range(len(q)):
                x, y = q.popleft()
                for dx, dy in move:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < N and 0 <= ny < N and grid[nx][ny] == 0:
                        q.append((nx, ny))
                        grid[nx][ny] = -1
            steps += 1

        return steps
```

更多题解可以访问我的 LeetCode 题解仓库：https://github.com/azl397985856/leetcode 。 目前已经接近 30K star 啦。

大家也可以关注我的公众号《脑洞前端》获取更多更新鲜的 LeetCode 题解

![](https://p.ipic.vip/kqnvg9.jpg)
