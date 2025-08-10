---
title: Uniswap V4：更灵活、更高效的去中心化交易所
tags: [区块链, web3, swap, uniswap, v4]
categories:
  - [区块链]
date: 2025-08-10
---

如果你是个 DeFi 爱好者，或者刚入门 Web3，肯定听说过 Uniswap 这个去中心化交易所（DEX）。它从 V1 到 V3 一步步进化，现在 V4 又带来了革命性的变化。简单来说，Uniswap V4 继承了 V3 的集中流动性模型，但引入了 hooks、单例架构等创新，让它变得更 customizable、更 gas 友好。

相信我，它真的很容易懂。我们会先快速回顾 Uniswap V3 的核心概念，让即使不懂 V3 的新人也能快速上手，然后拆解 V4 是什么，和 V3 的区别在哪里。文章会用 Python 代码来模拟原理，但别担心，我不会直接扔代码给你看。先用文字描述过程和原理，再给出代码，让你边看边理解。建议你本地跟着敲代码，实践出真知！如果 Python 不熟，用 ChatGPT 帮你翻译下注释就好。

最后，我们会用一个表格总结 V3 和 V4 的区别。

<!-- more -->

## Uniswap V3 快速入门

如果你是 Uniswap 新手，别慌，我们先花点时间了解 V3，因为 V4 是基于它的升级。Uniswap V3 是 2021 年推出的版本，主要创新是“集中流动性”（concentrated liquidity）。 简单说，在旧版（如 V2）中，流动性提供者（LP）把资金均匀分布在整个价格范围（从 0 到无穷），这导致资本效率低，因为大部分资金闲置在不活跃的价格区。

V3 改变了这个：LP 可以指定一个价格范围，比如 ETH/USDC 池子，你可以只在 1500-2500 USDC/ETH 范围内提供流动性。这就像把你的钱“集中”在你认为价格会波动的区间，提高了资金利用率。 原理上，还是用恒定乘积公式（x \* y = k），但在指定范围内，使用“虚拟储备”（virtual reserves）来模拟更大的流动性池子。具体过程：LP 添加流动性时，计算基于 tick（价格刻度）的虚拟 x 和 y；交换时，如果价格在范围内，就用这些虚拟值计算输出；超出范围，流动性“失效”。

另外，V3 引入了多费用层级（0.05%、0.3%、1%），让不同波动性的资产有合适的手续费。 这让 V3 成为 DeFi 的标杆，但也有痛点：自定义性不足（费用固定），gas 消耗高（每个池子独立合约），扩展难（想加限价单得外部合约）。

懂了 V3，V4 就好懂了——它解决这些痛点。

## Uniswap V4 是什么

Uniswap V4 是 Uniswap 协议的第四个版本，于 2023 年公布，并在 2024-2025 年逐步上线主网。 它是一个自动做市商（AMM），允许用户在以太坊等区块链上无许可地交换代币。核心还是基于恒定乘积公式，但 V4 强调自定义和效率。

一句话总结：Uniswap V4 通过 hooks（钩子）让开发者自定义池子行为，通过单例合约（singleton）减少 gas 消耗，并支持闪电记账（flash accounting）来优化交易流程。 相比前代，它更像一个“乐高积木”，开发者可以随意组装功能，比如动态费用、限价单、甚至内置借贷协议。

为什么这么设计？因为 DeFi 生态越来越复杂，用户需要更多灵活性。V4 不是简单升级，而是让整个协议变成一个可扩展的框架，吸引更多创新。

## 与 V3 的区别

Uniswap V3 引入了集中流动性，让 LP 可以指定价格范围，提高资本效率。 但 V4 在此基础上大改架构。简单比喻：V3 像一辆固定配置的汽车，性能好但没法改装；V4 像一辆模块化的电动车，你可以加插件、换电池，跑得更快更省油。

下面用表格总结主要区别：

| 方面 | Uniswap V3 | Uniswap V4 |
| --- | --- | --- |
| 架构 | 每个池子一个独立合约，工厂模式 | 单例架构，所有池子在一个合约中，减少 gas 99% |
| 自定义性 | 固定费用层级（0.05%、0.3%、1%），无钩子 | 引入 hooks，支持动态费用、限价单等自定义逻辑 |
| Gas 效率 | 每个交换转移资产，gas 较高 | 闪电记账，只转移净余额；支持原生 ETH |
| 池子创建 | 有限费用层级，创建成本高 | 无限自定义池子，无费用限制 |
| 创新潜力 | 依赖外部合约扩展 | Hooks 允许内置创新，如 TWAMM、自定义预言机 |

从表格看，V4 的核心优势是灵活性和效率。V3 已经很强大，但 V4 让它更适合大规模 DeFi 应用。

## V4 的核心特点

现在，我们深入解析 V4 的关键创新（基于 V3 的基础）。我会先用文字描述每个部分的原理和过程，然后给出 Python 代码模拟。代码基于简单模型，不会太复杂，主要用 numpy 和基本数学库。记住，这些是简化版，真实 Uniswap 用 Solidity 实现，但 Python 可以帮我们理解逻辑。

### 1. 集中流动性（继承自 V3）

原理：V3 和 V4 都用集中流动性，让 LP 只在特定价格范围内提供流动性，而不是全范围。这像把资金“集中”在热门价格区，提高效率。 过程：LP 指定 tick（价格刻度），池子用虚拟储备计算交换率。当价格移动，流动性自动调整。在范围内，真实流动性被“虚拟化”为更大的储备（virtual reserves），让交换率更高效；超出范围，就没流动性。

在 V4 中，这部分没变，但 hooks 可以扩展，比如自动复投费用。

我们先模拟一个简单 AMM 池子，展示交换过程。假设两个代币 A 和 B，初始储备 1000 A 和 1000 B（k=1e6）。用户交换 100 A 时，计算输出 B。

过程描述：首先，计算当前价格（price = reserve_B / reserve_A），这是资产比率，表示 1 A 换多少 B。然后检查价格是否在 tick 范围内。如果在，用虚拟 k（virtual_k）模拟交换：virtual_k 是基于范围宽度的简化放大（实际 V3 用 sqrt(price) 数学，但这里简化成 k 乘范围差），代表虚拟恒定乘积，让范围内的流动性“放大”。计算新储备：new_A = old_A + input_A，然后 new_B = virtual_k / new_A。输出 = old_B - new_B。但实际中，虚拟 k 用于调整有效储备。

现在，看代码模拟（已修正解释 virtual_k 和 price 的作用）：

```python
import numpy as np

# 初始化池子：储备 A 和 B，恒定 k
reserve_A = 1000
reserve_B = 1000
k = reserve_A * reserve_B

# 模拟交换：输入 delta_A，输出 delta_B
delta_A = 100  # 用户输入 100 A
new_reserve_A = reserve_A + delta_A
new_reserve_B = k / new_reserve_A
delta_B = reserve_B - new_reserve_B

print(f"输出 B (无集中): {delta_B:.2f}")
# 输出 B: 90.91（忽略费用）

# 加入 tick 模拟（简化版集中流动性）
# 假设价格范围 [0.9, 1.1]，virtual_k 含义：简化虚拟恒定乘积，代表范围内的“放大”流动性
# 用处：让交换只在范围内有效，模拟更大储备，提高效率。实际 V3 用 L^2 等公式，这里简化。
tick_lower = 0.9
tick_upper = 1.1
virtual_k = k * (tick_upper - tick_lower) / 0.2  # 修正简化：除以全范围因子，假设默认范围0.2以匹配初始k

# 当前价格：price = reserve_B / reserve_A，表示1 A换多少B。用于检查是否在范围内。
# 为什么用 old 而非 new：因为这是交换前的检查，交换后价格会变，但先验证当前状态。
price = reserve_B / reserve_A  # 当前价格 1

if tick_lower <= price <= tick_upper:
    # 在范围内，用 virtual_k 交换（简化演示放大效果）
    new_reserve_A_virtual = reserve_A + delta_A
    new_reserve_B_virtual = virtual_k / new_reserve_A_virtual
    delta_B_virtual = reserve_B - new_reserve_B_virtual  # 实际输出调整
    print(f"输出 B (集中流动性): {delta_B_virtual:.2f}")
    print("流动性集中，交换高效")
else:
    print("超出范围，无流动性")
```

这个代码展示了基本交换原理，并解释了 virtual_k（虚拟 k 的含义和用处：放大范围内的流动性，让 LP 资金更高效）和 price（当前价格的定义和作用：检查范围，不用 new 因为是预交换验证）。V4 继承这个，但优化了 gas。

### 2. 单例架构（Singleton）

原理：V3 每个池子是一个合约，创建新池子要部署新合约，gas 贵。V4 把所有池子放一个合约里，用 poolKey（token0, token1, fee, hook 等）标识。 过程：创建池子时，只更新内部映射，不部署新合约。交换时，路由器在单合约内跳转，节省 gas。

好处：池子创建 gas 降 99%，多池路由更快。

模拟过程：想象一个字典存储多个池子。每个池子有独特 key，我们用 Python dict 模拟。

过程描述：先定义 Pool 类，包含储备。然后用 dict 以 (token0, token1, fee) 为 key 存储池子。创建新池子只需添加 dict 条目，不像 V3 “部署”新对象。

现在，看代码：

```python
class Pool:
    def __init__(self, reserve_A, reserve_B):
        self.reserve_A = reserve_A
        self.reserve_B = reserve_B
        self.k = reserve_A * reserve_B

    def swap(self, delta_A):
        new_A = self.reserve_A + delta_A
        new_B = self.k / new_A
        delta_B = self.reserve_B - new_B
        self.reserve_A = new_A
        self.reserve_B = new_B
        return delta_B

# 单例模拟：所有池子在一个 "合约" dict 中
singleton = {}

# 创建池子：用 key 标识
pool_key = ("ETH", "USDC", 0.003)  # token0, token1, fee
singleton[pool_key] = Pool(1000, 1000)

# 交换
output = singleton[pool_key].swap(100)
print(f"Singleton 输出: {output:.2f}")
```

这个模拟了 V4 的单例：添加池子超快，不需新实例开销。

### 3. Hooks（钩子）

原理：Hooks 是外部合约，在池子生命周期关键点执行，比如 beforeSwap、afterAddLiquidity。 过程：池子创建时指定 hook 地址和权限。交换时，核心逻辑前/后调用 hook。比如，动态费用 hook：beforeSwap 检查市场波动，调整 fee。

这是 V4 的杀手锏，让池子像插件系统。V3 没这个，全靠外部。

模拟过程：我们定义一个 Hook 类，包含 before_swap 方法。然后在 Pool 中调用它。

过程描述：先检查 hook 是否存在，如果有，调用 before_swap 调整参数（如 fee）。然后执行核心交换。

现在，看代码（模拟动态费用 hook）：

```python
class DynamicFeeHook:
    def before_swap(self, delta_A):
        # 模拟：如果输入大，费用高
        if delta_A > 50:
            fee = 0.005  # 0.5%
        else:
            fee = 0.001  # 0.1%
        return fee

class PoolWithHook(Pool):
    def __init__(self, reserve_A, reserve_B, hook=None):
        super().__init__(reserve_A, reserve_B)
        self.hook = hook

    def swap(self, delta_A):
        if self.hook:
            fee_rate = self.hook.before_swap(delta_A)
            delta_A *= (1 - fee_rate)  # 扣费
        return super().swap(delta_A)

# 使用
hook = DynamicFeeHook()
pool = PoolWithHook(1000, 1000, hook)
output = pool.swap(100)
print(f"带 Hook 输出: {output:.2f}")
```

这里，hook 调整了输入，模拟动态费。V4 允许更多复杂 hook，如限价单。

### 4. 闪电记账（Flash Accounting）

原理：V3 每个交换都转移资产，gas 耗。V4 用临时存储（EIP-1153）记账，只在批处理末尾转移净额。 过程：多步操作（如多池交换）内部记 delta，最后结算。

模拟：用一个 delta 字典跟踪净变化。

过程描述：初始化 delta_A=0, delta_B=0。每个操作更新 delta，最后“结算”转移。

现在，看代码：

```python
# 闪电记账模拟
deltas = {"A": 0, "B": 0}

# 模拟交换：不立即转移
deltas["A"] += 100  # 输入 A
deltas["B"] -= 90.91  # 输出 B

# 另一操作
deltas["A"] -= 50  # 输出 A
deltas["B"] += 45  # 输入 B

# 结算净额
print(f"净转移 A: {deltas['A']}, B: {deltas['B']}")
```

这展示了 V4 的效率：只转移净值，gas 省。

## 总结

Uniswap V4 是 DeFi 的未来：更自定义、更高效。通过 hooks 和单例，它从工具变成平台。相比 V3，V4 降低了门槛，激发创新。如果你想深入，建议去 Uniswap 官网看白皮书，或者自己 fork v4-periphery 仓库玩玩。

希望这篇文章帮到你！如果喜欢，点个赞分享哦。有什么问题，评论见。
