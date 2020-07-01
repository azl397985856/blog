## 本质

```py

queue = [0]
visited = set()
steps = 0

while queue:
    for _ in range(len(queue)):
        cur = queue.pop(0)
        if cur in visited: continue
        visited.add(cur)
        if nums[cur] === target: return (cur, steps)
        queue.append(cur - 1)
        queue.append(cur + 1)
    steps += 1
return (-1, steps)

```

## 题目

- https://leetcode-cn.com/problems/binary-tree-level-order-traversal-ii/
- https://leetcode-cn.com/problems/find-largest-value-in-each-tree-row/
- https://leetcode-cn.com/problems/shortest-path-visiting-all-nodes/
