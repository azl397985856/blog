---
title: 【LeetCode日记】 1162. 地图分析
tags: [数据结构, 算法, LeetCode日记]
categories:
  - [数据结构, hashtable]
  - [算法, BFS]
---

LeetCode上有很多小岛题，虽然官方没有这个标签， 但是在我这里都差不多。不管是思路还是套路都比较类似，大家可以结合起来练习。


- [200.number-of-islands](https://github.com/azl397985856/leetcode/blob/master/problems/200.number-of-islands.md)
- [695.max-area-of-island](https://leetcode-cn.com/problems/max-area-of-island/solution/695-dao-yu-de-zui-da-mian-ji-dfspython3-by-fe-luci/)

​<!-- more -->

原题地址：https://leetcode-cn.com/problems/as-far-from-land-as-possible/

## 思路

这里我们继续使用上面两道题的套路，即不用visited，而是原地修改。由于这道题求解的是最远的距离，而距离我们可以使用BFS来做。算法：

- 对于每一个海洋，我们都向四周扩展，寻找最近的陆地，每次扩展steps加1。
- 如果找到了陆地，我们返回steps。
- 我们的目标就是所有steps中的最大值。

实际上面算法有很多重复计算，如图中间绿色的区域，向外扩展的时候，如果其周边四个海洋的距离已经计算出来了，那么没必要扩展到陆地。实际上只需要扩展到周边的四个海洋格子就好了，其距离陆地的最近距离就是1 + 周边四个格子中到达陆地的最小距离。


![](https://pic.leetcode-cn.com/23e21821e14238829dd7021a620895f40a8e42127cfe372e4791d025bb655afc.jpg)

我们考虑优化。 

- 将所有陆地加入队列，而不是海洋。
- 陆地不断扩展到海洋，每扩展一次就steps加1，直到无法扩展位置。
- 最终返回steps即可。

图解：

![](https://pic.leetcode-cn.com/8001c1390fb0d1a402eea5010594a303651b4a09ac6ddcd12d72b5b8a9d37295.jpg)

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

> 由于没有early return，steps 其实会多算一次。 我们可以返回值减去1，也可以steps初始化为-1。这里我选择是steps初始化为-1

***复杂度分析***
- 时间复杂度：$O(N ^ 2)$
- 空间复杂度：$O(N ^ 2)$

更多题解可以访问我的LeetCode题解仓库：https://github.com/azl397985856/leetcode  。 目前已经接近30K star啦。

大家也可以关注我的公众号《脑洞前端》获取更多更新鲜的LeetCode题解

![](https://pic.leetcode-cn.com/89ef69abbf02a2957838499a96ce3fbb26830aae52e3ab90392e328c2670cddc-file_1581478989502)

