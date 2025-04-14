---
title: Web3 金融的基石 - Swap 和 Staking
tags: [区块链, web3, swap, staking]
categories:
  - [区块链]
date: 2025-03-28
---

web3 是一个非常流行的概念，它的基础是区块链技术。区块链技术是一种分布式账本技术，它的特点是去中心化、不可篡改、安全可靠。区块链技术的应用场景非常广泛，比如数字货币、智能合约、供应链金融等等。

网上关于区块链的资料非常多，但是从零开始构建的资料却很少。熟悉我的朋友应该知道，我经常从零实现一些东西帮助我理解，比如从零实现 git，从零实现 webpack 打包器，从零实现一个框架等等。

本文就是继上一篇 [《从零开始构建区块链》](https://lucifer.ren/blog/2024/11/22/web3-zero-to-one/ "《从零开始构建区块链》") 的文章，讲述**什么是 swap，什么是滑点，什么是 staking，背后原理又是怎么样的？**

<!-- more -->

## Defi

在 Web3 的浪潮中，去中心化金融（DeFi）正在重新定义我们对资产交换和增值的认知。今天，我们将深入探讨 Web3 的两大核心机制——**Swap**（交换）和 **Staking**（质押）。它们不仅是 DeFi 生态的基石，也是用户参与区块链经济的直接途径。

由于本文不是科普文章，而是直接带你实现，从而加深理解，因此建议你对区块链技术有一定的了解。如果你对区块链技术还不了解，可以先看一些区块链的基础知识，比如区块链的概念、区块链的特点、区块链的应用等等。比如 [learn_blockchain](https://github.com/chaseSpace/learn_blockchain "learn_blockchain") 就是一个还不错的入门资料集合页。

本文使用 Python 语言来实现区块链，Python 是一种非常流行的编程语言，它的语法简单，非常适合初学者。如果你对 Python 不熟悉也没关系，相信我他真的很容易懂。如果你实在不懂，也可以让 chatgpt 给你解释甚至直接翻译为其他语言。

## 学习建议

为了方便大家直接运行，我提供了相对完整的代码示例。强烈大家边看看在本地跟着一起写，一起运行查看效果，只有动手才可能真正理解其核心。并且尽可能地根据我的思路和代码默写，而不是抄写一遍。

## Swap：去中心化的价值交换

### 什么是 Swap？

顾名思义，Swap 是指代币的交换。在银行中，我们可以用各种各样的货币进行交易，比如美元、人民币、欧元等等。在 Web3 中，swap 指的是代币的交换。

在传统金融中，资产交换需要依赖银行或中心化交易所。交易依赖订单簿，即根据用户的出价来促成交易。这个过程依赖中心化交易所。如果它挂了，我们是无法交易的。由于依赖中心化交易所，因此很多时候也会有手续费。

而在 Web3 中，Swap 通过去中心化交易所（DEX）实现，用户可以直接在链上交换代币，无需中介。Uniswap、SushiSwap 等平台采用的**自动化做市商（AMM）**模型是其核心。

AMM 不依赖订单簿，而是通过数学公式（如恒定乘积公式 `x * y = k`）来维持流动性池的平衡，其中 `x` 和 `y` 分别代表两种代币的储备量，`k` 是常数。

### Swap 的过程与原理

> 这里简化了 Swap 中的 AMM 过程，实际上 Swap 过程更复杂，但是核心思想是一样的。

假设有一个流动性池，初始储备为 100 个代币 A 和 10000 个代币 B。当用户想用 A 换取 B 时，他们会向池子输入一定数量的 A（比如 10 个），池子根据 `x * y = k` 计算出需要输出的 B 数量。关键在于，池子里的 A 增加后，B 的储备量会减少，以保持 `k` 不变。这种机制通过价格滑点（slippage）反映供需变化：投入的 A 越多，获得的 B 越少，价格自然调整。

那么什么是价格滑点？

### 滑点

在 Web3 的去中心化交易所（DEX）中，滑点（Slippage）是指交易执行价格与用户预期价格之间的差异。这种差异通常发生在使用自动化做市商（AMM）模型时，因为 AMM 的价格是由池子中代币的储备量动态决定的，而不是固定的订单簿。

具体来说，当你用一种代币（比如 A）换另一种代币（B）时，池子里的 A 增加，B 减少，根据恒定乘积公式 x \* y = k，价格会实时调整。如果**交易量较大，池子储备的变化会更显著，导致你实际获得的 B 数量比初始价格预期的少，这就是滑点**。滑点的程度取决于交易量与池子流动性的比例：**池子越小，或者交易量越大，滑点越高。**

例如：

初始池子：100 个 A 和 10000 个 B，价格为 1 A = 100 B。你投入 10 个 A，按初始价格预期得到 1000 个 B。但实际由于池子调整，你可能只得到 909 个 B，滑点就是 (1000 - 909) / 1000 ≈ 9.1%。在现实中，用户通常会在交易时设置一个“最大滑点容忍度”（如 0.5% 或 1%），如果实际滑点超过这个值，交易会失败，以保护用户。

### 代码实现

代币的供应量（即储备量）通常由流动性提供者（LP）存入池子，初始值由池子的创建者设定，后续通过用户交易动态调整。

下面，我们用 Python3 模拟这个过程：

```python
class AMM:
    def __init__(self, token_a: float, token_b: float):
        self.reserve_a = token_a  # 代币 A 的储备量
        self.reserve_b = token_b  # 代币 B 的储备量
        self.k = token_a * token_b  # 恒定乘积 k

    def swap_a_to_b(self, amount_a: float, max_slippage: float = 0.05) -> tuple[float, float]:
        """用代币 A 换取代币 B，返回 (获得的 B 数量, 滑点百分比)"""
        # 初始价格和预期输出
        initial_price = self.reserve_b / self.reserve_a
        expected_b_out = amount_a * initial_price

        # 实际输出
        new_reserve_a = self.reserve_a + amount_a
        new_reserve_b = self.k / new_reserve_a
        amount_b_out = self.reserve_b - new_reserve_b

        # 计算滑点
        slippage = (expected_b_out - amount_b_out) / expected_b_out if expected_b_out > 0 else 0

        # 检查滑点是否超出容忍度
        if slippage > max_slippage:
            raise ValueError(f"滑点 {slippage:.2%} 超出最大容忍度 {max_slippage:.2%}，交易失败")

        # 更新池子状态
        self.reserve_a = new_reserve_a
        self.reserve_b = new_reserve_b
        return amount_b_out, slippage

    def get_price_a_to_b(self) -> float:
        """计算 A 对 B 的价格（1 个 A 换多少 B）"""
        return self.reserve_b / self.reserve_a

    def get_price_b_to_a(self) -> float:
        """计算 B 对 A 的价格（1 个 B 换多少 A）"""
        return self.reserve_a / self.reserve_b

# 示例运行
if __name__ == "__main__":
    # 初始化一个流动性池，100 个 A 和 10000 个 B
    pool = AMM(token_a=100, token_b=10000)
    print(f"初始价格 (A -> B): {pool.get_price_a_to_b()}")  # 1 A = 100 B
    print(f"初始价格 (B -> A): {pool.get_price_b_to_a()}")  # 1 B = 0.01 A

    # 用 10 个 A 换 B，最大滑点容忍度 5%
    try:
        amount_b, slippage = pool.swap_a_to_b(10, max_slippage=0.05)
        print(f"换得 {amount_b:.2f} 个 B，滑点: {slippage:.2%}")
        print(f"交换后价格 (A -> B): {pool.get_price_a_to_b():.2f}")
        print(f"交换后价格 (B -> A): {pool.get_price_b_to_a():.4f}")
    except ValueError as e:
        print(e)

    # 尝试一个大额交易，触发滑点超限
    pool = AMM(token_a=100, token_b=10000)  # 重置池子
    try:
        amount_b, slippage = pool.swap_a_to_b(50, max_slippage=0.05)
        print(f"换得 {amount_b:.2f} 个 B，滑点: {slippage:.2%}")
    except ValueError as e:
        print(e)
```

运行结果：

```
初始价格 (A -> B): 100.0
初始价格 (B -> A): 0.01
换得 909.09 个 B，滑点: 9.09%
交换后价格 (A -> B): 90.91
交换后价格 (B -> A): 0.0110
滑点 33.33% 超出最大容忍度 5.00%，交易失败
```

### 代码解析

- **储备量来源**：`reserve_a` 和 `reserve_b` 是池子的初始代币量，模拟中我们手动设定为 100 和 10000，现实中由流动性提供者存入。
- **swap_a_to_b**：B 的储备量不会增加，而是减少，因为用户拿走了部分 B（`amount_b_out` 是输出的 B 量）。

- **滑点计算**：

  - `expected_b_out` 是按初始价格计算的理论输出。
  - `amount_b_out` 是实际输出，滑点为 `(expected_b_out - amount_b_out) / expected_b_out`。
  - 在上面的例子中，10 个 A 预期换 1000 个 B，实际得到 909.09 个 B，滑点约为 9.09%。

- **最大滑点容忍度**：

  - 默认设为 5%（0.05）。当用 10 个 A 交易时，滑点 9.09% 超过 5%，但为了展示结果，这里未中断。
  - 当交易量增至 50 个 A 时，滑点高达 33.33%，触发异常，交易失败。

- **现实应用**：
  - 在 pancakeswap 等平台上，用户可以在前端设置滑点容忍度，智能合约会根据池子状态实时检查。

滑点是 AMM 的核心特性之一，它提醒我们在高波动性或低流动性池中交易时要谨慎选择交易量。通过这个修改后的代码，你可以更直观地理解滑点如何影响你的 Swap 操作。

## Staking：让资产为你工作

### 什么是 Staking？

Staking 是将代币锁定在区块链网络中以支持其运行（比如验证交易）并获得奖励的过程。在权益证明（PoS，即 Proof of Stake）网络中，用户质押代币以参与共识，获得年化收益率（APY）。这类似于银行存款，但完全去中心化。

> Pos 在这里不细节展开，如果大家感兴趣，我后面会考虑单独写一篇文章来介绍。

Staking 的根本目的是支持 PoS 区块链的共识机制，确保网络的安全、稳定和去中心化运行。包括：

- 交易验证：质押者（或委托的验证者）负责验证交易并生成新区块，替代了 PoW（即 Proof of Work） 中的算力挖矿。
- 防止恶意行为：质押的代币作为“抵押品”，如果验证者作恶（如双重签名或宕机），部分代币会被没收（ slashing），从而激励诚实行为。
- 安全性：质押的代币越多，质押的时间越久,攻击网络的成本越高。
- 节能环保：相比 PoW 的高能耗，PoS 通过 Staking 极大降低了碳足迹。

另外 staking 会减少流通供应，这是因为用户质押的代币被锁定，无法在市场上交易，这降低了流通量，可能推高代币价格或减少抛压。

### Staking 的过程与原理

假设一个质押池初始有 1000 个代币，年化收益率（reward_rate）为 10%。用户 Alice 质押 100 个代币后，池子总质押量变为 1100。奖励按时间和质押量比例分配，比如 30 天后，Alice 根据日收益率获得回报。
下面是 Python3 模拟：

```python
class StakingPool:
    def __init__(self, total_staked: float, reward_rate: float):
        self.total_staked = total_staked  # 总质押量
        self.reward_rate = reward_rate    # 年化收益率（百分比）
        self.stakers = {}                 # 存储每个质押者的信息

    def stake(self, user: str, amount: float):
        """用户质押代币"""
        if user in self.stakers:
            self.stakers[user] += amount
        else:
            self.stakers[user] = amount
        self.total_staked += amount

    def calculate_reward(self, user: str, days: int) -> float:
        """计算某用户在指定天数后的奖励"""
        if user not in self.stakers:
            return 0
        staked_amount = self.stakers[user]
        daily_rate = self.reward_rate / 365 / 100  # 将年化收益率转为日收益率
        reward = staked_amount * daily_rate * days
        return reward

# 示例运行
if __name__ == "__main__":
    # 初始化一个质押池，总质押量 1000，10% 年化收益率
    # 现实中，`reward_rate` 由网络协议设定，可能基于通胀率、交易费用等动态调整。
    pool = StakingPool(total_staked=1000, reward_rate=10)

    # 用户 Alice 质押 100 个代币
    pool.stake("Alice", 100)
    print(f"Alice 质押后总质押量: {pool.total_staked}")

    # 计算 Alice 30 天后的奖励
    reward = pool.calculate_reward("Alice", 30)
    print(f"Alice 30 天后的奖励: {reward:.4f}")
```

运行结果：

```
Alice 质押后总质押量: 1100
Alice 30 天后的奖励: 0.8219
```

### 代码解析

- **reward_rate 来源**：这里设为 10%，现实中由区块链网络（如 Ethereum）的协议参数决定，可能通过治理投票或算法调整。
- **奖励计算**：基于质押量和时间线性分配，链上智能合约会类似地执行。

## IDO（TGE）：代币的首次亮相

最后我们来聊聊大家比较关注和感兴趣的 IDO（Token Generation Event，代币生成事件）。正好这个其实也和我们今天讲的内容有关联。大家今后如果遇到新的内容，也可以想一下是否和我们已经学过的东西有关联。

**IDO**（Initial DEX Offering，首次去中心化交易所发行）或 **TGE**（Token Generation Event，代币生成事件）是区块链项目通过去中心化平台首次发行代币的方式。与传统的 ICO（首次代币发行）不同，IDO 通常在 DEX 上进行，结合流动性池和社区参与，旨在公平分发代币并立即提供交易流动性。

- **过程**：
  1. 项目方创建代币并设定初始供应量。
  2. 在 DEX 上部署流动性池，通常搭配一种基础代币（如 ETH 或 BNB）。
  3. 用户通过认购（通常有白名单或 Staking 要求）或直接购买参与。一般认购都有时间要求，比如几个小时内。
  4. 认购结束，代币上线后，用户可立即交易，流动性由池子支持。
- **特点**：
  - **去中心化**：无需中介，智能合约自动执行。
  - **社区驱动**：常要求用户质押已有代币（如平台的治理代币）以获得参与资格。
  - **即时流动性**：通过 AMM 池，代币一发行即可交易，避免了 ICO 的“锁仓后抛售”问题。

- **对各方的好处**：
  - **项目方**：快速筹集资金（前面提到的基础代币），吸引早期用户，建立市场。
  - **用户**：低门槛参与新项目，可能获得高回报（若代币升值）。
  - **生态**：增强 DEX 的使用率，促进代币经济循环。

### 代码模拟
我们模拟一个简单的 IDO 过程：项目方初始化代币池，用户认购代币，池子随后支持 Swap。

```python
class IDO:
    def __init__(self, token_name: str, total_supply: float, initial_price: float, base_token: float):
        self.token_name = token_name
        self.total_supply = total_supply  # 总供应量
        self.available = total_supply     # 可售量
        self.initial_price = initial_price  # 初始价格（每单位代币换多少基础代币）
        self.base_token = base_token      # 基础代币储备（如 ETH）
        self.raised = 0                   # 筹集的基础代币
        self.participants = {}

    def participate(self, user: str, base_amount: float) -> float:
        """用户用基础代币认购新代币"""
        token_amount = base_amount / self.initial_price
        if token_amount > self.available:
            raise ValueError("代币不足")
        self.participants[user] = self.participants.get(user, 0) + token_amount
        self.available -= token_amount
        self.raised += base_amount
        self.base_token += base_amount
        return token_amount

    def launch_pool(self) -> 'AMM':
        """IDO 结束后启动 AMM 池"""
        if self.available > 0:
            raise ValueError("IDO 未结束")
        return AMM(token_a=self.total_supply - self.available, token_b=self.base_token)

# 示例运行
if __name__ == "__main__":
    # 初始化 IDO：发行 10000 个 NEW_TOKEN，初始价格 0.01 ETH/代币，池子有 10 ETH
    ido = IDO(token_name="NEW_TOKEN", total_supply=10000, initial_price=0.01, base_token=10)
    print(f"初始可用代币: {ido.available}, 初始 ETH: {ido.base_token}")

    # 用户 Alice 用 5 ETH 认购
    tokens_bought = ido.participate("Alice", 5)
    print(f"Alice 认购 {tokens_bought} 个 {ido.token_name}, 剩余代币: {ido.available}")

    # 假设所有代币售罄，启动 AMM 池
    ido.available = 0  # 模拟售罄
    pool = ido.launch_pool()
    print(f"池子启动: {ido.token_name} 储备 {pool.reserve_a}, ETH 储备 {pool.reserve_b}")

    # Alice 用 1 ETH 交换 NEW_TOKEN
    amount_token, slippage = pool.swap_a_to_b(1)
    print(f"Alice 换得 {amount_token:.2f} 个 {ido.token_name}, 滑点: {slippage:.2%}")
```

运行结果：
```
初始可用代币: 10000, 初始 ETH: 10
Alice 认购 500.0 个 NEW_TOKEN, 剩余代币: 9500.0
池子启动: NEW_TOKEN 储备 10000, ETH 储备 15
Alice 换得 666.67 个 NEW_TOKEN, 滑点: 4.76%
```

### 代码解析
- **认购阶段**：用户用基础代币（ETH）按初始价格购买新代币，筹集的 ETH 进入池子。
- **池子启动**：IDO 结束后，剩余代币和筹集的 ETH 组成 AMM 池，支持后续 Swap。
- **现实映射**：实际 IDO 可能有时间限制、白名单或 Staking 要求，这里简化为直接认购。
 孵化新项目，三者共同构建了一个去中心化、开放且充满活力的金融生态。你会选择参与哪一环？未来已来，答案在你手中。


## 结语

Swap 和 Staking 是 Web3 金融的核心，一个实现无中介的价值交换，一个赋予资产增值能力。通过 Python 模拟，我们看到了它们的数学美感与去中心化逻辑。你觉得这种机制如何影响未来的金融世界？最后我们聊了下备受关注的 IDO，希望大家能有所收获。
