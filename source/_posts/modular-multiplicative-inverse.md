---
title: 全网最易懂的“乘法逆元”
date: 2024-03-03
tags: [乘法逆元, 算法, 模运算]
categories:
  - [算法]
---

## 全等号

≡ 是数学中的“全等号”（congruence symbol），在数论和模运算中有着特殊的含义。它表示两个数在某个模数下的“相等性”，具体来说：

如果 \(a \equiv b \pmod{m}\)，意思是 \(a\) 和 \(b\) 在模 \(m\) 下全等，也就是说，\(a - b\) 能被 \(m\) 整除，或者换句话说，\(a\) 和 \(b\) 除以 \(m\) 后的余数相同。

### 示例
- \(15 \equiv 1 \pmod{7}\)，因为 \(15 - 1 = 14\)，而 \(14\) 是 \(7\) 的倍数（\(14 \div 7 = 2\)，余数为 \(0\)）。
- \(10 \equiv 3 \pmod{7}\)，因为 \(10 - 3 = 7\)，也是 \(7\) 的倍数。

### 与普通等号 (=) 的区别
- \(=\) 表示严格相等，例如 \(5 = 5\)。
- \(≡\) 是模意义下的相等，允许两数在模 \(m\) 下“等价”，即使数值不同。例如 \(15 \neq 1\)，但 \(15 \equiv 1 \pmod{7}\)。

## 乘法逆元的概念

乘法逆元是数论中的核心概念，广泛应用于线性同余方程、组合数计算等场景。定义为：对于整数 \(a\) 和模数 \(m\)，若存在 \(b\) 满足 \(a \cdot b \equiv 1 \pmod{m}\)，则 \(b\) 是 \(a\) 在模 \(m\) 下的乘法逆元，记作 \(b = a^{-1} \pmod{m}\)。前提是 \(a\) 和 \(m\) 互质（\(\gcd(a, m) = 1\)）。

比如 \(a \cdot b \equiv 1 \pmod{m}\) 表示 \(a\) 和 \(b\) 的乘积除以 \(m\) 后余数为 \(1\)，这正是乘法逆元的定义基础。

接下来我们通过一个例子来理解乘法逆元的概念。

### 示例

假设我们要计算 \(\frac{1}{3} \pmod{7}\)。在普通算术中（不考虑 mod），这很简单：\(1 \div 3 = \frac{1}{3}\)。但在模运算中，除法不再直接适用，我们需要找到一种方法让这个分数在模 \(7\) 下有意义。

令 x = \(\frac{1}{3} \pmod{7}\)，那么我们的目标就是求出 x。将等式两边同时乘以 3 得到 \(3 \cdot x \) = 1 mod 7

我们可以逐个尝试 x：

- 如果 \(x = 1\)，则 \(3 \cdot 1 = 3 \equiv 3 \pmod{7}\)，不对。
- 如果 \(x = 2\)，则 \(3 \cdot 2 = 6 \equiv 6 \pmod{7}\)，不对。
- 如果 \(x = 3\)，则 \(3 \cdot 5 = 9 \equiv 2 \pmod{7}\)，不对。
- 如果 \(x = 4\)，则 \(3 \cdot 4 = 12 \equiv 5 \pmod{7}\)，不对。
- 如果 \(x = 5\)，则 \(3 \cdot 5 = 9 \equiv 1 \pmod{7}\)，对了！

所以：

1. \(\frac{1}{3} \pmod{7}\) 就是找 3 mod 7 的乘法逆元。
2. \(x = 5\) 就是我们要找的 3 mod 7 的乘法逆元。

## 普通解法及其问题

最直观的方法是**枚举**：从 \(0\) 到 \(m-1\) 逐一测试每个数 \(x\)，看是否满足 \(a \cdot x \equiv 1 \pmod{m}\)。对于上面的例子，\(m = 7\) 还算小，枚举几步就找到了。但如果 \(m = 10^9 + 7\)（常见的大质数模），枚举 \(10^9\) 个数显然不现实，时间复杂度高达 \(O(m)\)，效率极低。

**问题**：
1. **效率低下**：当模数很大时，枚举不可行。
2. **无规律性**：无法快速判断逆元是否存在或直接计算。

这时候，我们需要更高效的方案。

## 高效算法

枚举太慢，下面介绍两种高效方法。

实际上上面的问题等价于：**找到 \(b\)，使得 \(a \cdot b - k \cdot m = 1\)（\(k\) 为整数）。** 

### 方法一：扩展欧几里得算法

扩展欧几里得算法（Extended Euclidean algorithm，EEA）是一种求解两个数的最大公约数和最小公倍数的算法。它是基于辗转相除法（欧几里得算法）的，但它可以同时求解两个数的乘法逆元。

**代码示例**：

- **C++**：
```cpp
long long exgcd(long long a, long long b, long long &x, long long &y) {
    if (b == 0) { x = 1; y = 0; return a; }
    long long d = exgcd(b, a % b, x, y);
    long long t = x; x = y; y = t - (a / b) * y;
    return d;
}

long long mod_inverse(long long a, long long m) {
    long long x, y;
    long long g = exgcd(a, m, x, y);
    if (g != 1) return -1;
    return (x % m + m) % m;
}
```

- **Python 3**：
```python
def exgcd(a, b):
    if b == 0: return a, 1, 0
    d, x, y = exgcd(b, a % b)
    return d, y, x - (a // b) * y

def mod_inverse(a, m):
    g, x, _ = exgcd(a, m)
    if g != 1: return -1
    return (x % m + m) % m
```

- **Java**：
```java
class Pair { long x, y; Pair(long x, long y) { this.x = x; this.y = y; } }
class Main {
    static long exgcd(long a, long b, Pair p) {
        if (b == 0) { p.x = 1; p.y = 0; return a; }
        long d = exgcd(b, a % b, p);
        long t = p.x; p.x = p.y; p.y = t - (a / b) * p.y;
        return d;
    }
    static long modInverse(long a, long m) {
        Pair p = new Pair(0, 0);
        long g = exgcd(a, m, p);
        if (g != 1) return -1;
        return (p.x % m + m) % m;
    }
}
```

- **JavaScript**：
```javascript
function exgcd(a, b) {
    if (b === 0n) return [a, 1n, 0n];
    let [d, x, y] = exgcd(b, a % b);
    return [d, y, x - (a / b) * y];
}

function modInverse(a, m) {
    let [g, x] = exgcd(BigInt(a), BigInt(m));
    if (g !== 1n) return -1n;
    return (x % m + m) % m;
}
```

- **Go**：
```go
func exgcd(a, b int64) (int64, int64, int64) {
    if b == 0 { return a, 1, 0 }
    d, x, y := exgcd(b, a%b)
    return d, y, x - (a/b)*y
}

func modInverse(a, m int64) int64 {
    g, x, _ := exgcd(a, m)
    if g != 1 { return -1 }
    return (x%m + m) % m
}
```

**建议视觉内容**：
- **动画**：展示扩展欧几里得的递归过程，例如 \(7\) 和 \(3\) 的计算，逐步分解并回代，突出 \(x = 5\) 的得出过程。

### 方法二：费马小定理

若 \(m\) 是质数且 \(a\) 不被 \(m\) 整除，则 \(a^{m-1} \equiv 1 \pmod{m}\)，故 \(a^{m-2} \equiv a^{-1} \pmod{m}\)。用快速幂计算，时间复杂度 \(O(\log m)\)。

**代码示例**：

- **C++**：
```cpp
long long quick_pow(long long a, long long b, long long m) {
    long long res = 1; a %= m;
    while (b) {
        if (b & 1) res = res * a % m;
        a = a * a % m; b >>= 1;
    }
    return res;
}

long long mod_inverse(long long a, long long m) {
    return quick_pow(a, m - 2, m);
}
```

- **Python 3**：
```python
def quick_pow(a, b, m):
    res = 1; a %= m
    while b:
        if b & 1: res = res * a % m
        a = a * a % m; b >>= 1
    return res

def mod_inverse(a, m):
    return quick_pow(a, m - 2, m)
```

- **Java**：
```java
class Main {
    static long quickPow(long a, long b, long m) {
        long res = 1; a %= m;
        while (b > 0) {
            if ((b & 1) == 1) res = res * a % m;
            a = a * a % m; b >>= 1;
        }
        return res;
    }
    static long modInverse(long a, long m) {
        return quickPow(a, m - 2, m);
    }
}
```

- **JavaScript**：
```javascript
function quickPow(a, b, m) {
    let res = 1n; a = BigInt(a) % BigInt(m);
    while (b > 0n) {
        if (b & 1n) res = res * a % m;
        a = a * a % m; b >>= 1n;
    }
    return res;
}

function modInverse(a, m) {
    return quickPow(a, BigInt(m) - 2n, BigInt(m));
}
```

- **Go**：
```go
func quickPow(a, b, m int64) int64 {
    res := int64(1); a %= m
    for b > 0 {
        if b&1 == 1 { res = res * a % m }
        a = a * a % m; b >>= 1
    }
    return res
}

func modInverse(a, m int64) int64 {
    return quickPow(a, m-2, m)
}
```


## 总结

回到开头的思考：模运算中的除法怎么办？乘法逆元通过 \(b \cdot a^{-1} \pmod{m}\) 完美替代；它的高效求解（扩展欧几里得或费马小定理）解决了枚举的低效问题；若 \(a\) 和 \(m\) 不互质，逆元不存在，需检查条件。这把“秘密武器”让数论计算更优雅，希望你也能掌握它的魅力！


