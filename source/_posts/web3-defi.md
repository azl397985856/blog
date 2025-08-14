---
title: 探索 DeFi 借贷与收益率交易的无限潜力
tags: [区块链, web3, defi, borrow, lending, aave, pendle]
categories:
  - [区块链]
date: 2025-08-14
---

在 Web3 的世界里，DeFi（去中心化金融）协议正如雨后春笋般涌现，其中 AAVE/pendle 作为借贷领域的佼佼者，帮助无数用户实现了资产的增值和流动性管理。想象一下，你手里的 ETH 或 USDC 不再只是躺在钱包里睡觉，而是能通过 AAVE/pendle 赚取稳定的利息，甚至通过杠杆放大收益。本文将带你深入了解 defi protocol 的核心机制，我们是如何赚钱的以及具体实操。

这篇文章的灵感来源于我对 DeFi 协议的探索，这次我们转向实际赚钱工具。学习建议：先理解基本概念，然后通过代码模拟过程，加深印象。

AAVE 的官网是 [https://app.aave.com/](https://app.aave.com/)，pendle 的官网是 [https://www.pendle.finance/](https://www.pendle.finance/)， 建议你打开它跟随操作。

<!-- more -->

## AAVE

AAVE 是一个开源的去中心化借贷协议，运行在 Ethereum 和其他链上（如 Polygon、Avalanche）。它的核心是让用户像银行一样存钱借钱，但没有中心化中介，一切通过智能合约自动化执行。

- **存款（Supply）**：用户可以将加密资产存入 AAVE 的流动性池中，成为流动性提供者（Liquidity Provider）。这些资产会被借给其他人使用，你则赚取利息。
- **借款（Borrow）**：用户可以借出资产，但需要提供超额抵押品（Collateral）。借款有固定利率和可变利率两种模式。
- **闪贷（Flash Loans）**：这是 AAVE 的创新功能，允许用户在同一笔交易中借出巨额资金、使用后再归还，无需抵押。适合套利或清算操作。
- **其他功能**：如 Staking AAVE 代币赚取奖励、治理投票等。

这些功能让 AAVE 成为 DeFi 的“瑞士军刀”，用户可以根据市场情况灵活配置资产。

### 赚钱原理

AAVE 的赚钱逻辑本质上是借贷市场的供需平衡：存款用户提供资金，借款用户支付利息，平台从中抽取少量费用。存款的年化收益率（APY）取决于资产的利用率——借款需求越高，利息越高。

简单来说，我们赚钱的原理有两种：

1. **被动赚钱**：存款资产，赚取存款利息。AAVE 使用复合利息模型，利息会自动复投。
2. **主动赚钱**：通过借款杠杆放大收益。比如，存入 ETH 作为抵押，借出 USDC，然后用 USDC 投资其他高收益机会。但这需要监控健康因子（Health Factor），避免清算。

为了让你更好地理解复合利息的原理，我们先来描述过程：假设你存入 1000 USDC，年化利率 5%。每天利息会根据当前余额计算并累加，形成复利效应。AAVE 的利率是动态的，受市场影响，但核心是时间价值和供需。

现在，我们用 Python 代码模拟一个简化版的复合利息计算过程。这里不涉及真实链上数据，只是为了展示原理：我们定义初始本金、年利率、时间周期，然后循环计算每天的利息累加。

```python
# 模拟 AAVE 存款的复合利息计算
# 假设年化利率 APY = 5%，每天复利（简化，实际 AAVE 是连续复利）

initial_deposit = 1000.0  # 初始存款 USDC
annual_rate = 0.05  # 年化利率 5%
days = 365  # 一年天数

daily_rate = annual_rate / 365  # 每日利率
balance = initial_deposit

for day in range(1, days + 1):
    interest = balance * daily_rate  # 当日利息
    balance += interest  # 复投

print(f"初始存款: {initial_deposit} USDC")
print(f"一年后余额: {balance:.2f} USDC")
print(f"总收益: {balance - initial_deposit:.2f} USDC")
```

这个代码运行后，你会看到一年后余额约为 1051.27 USDC，收益 51.27 USDC。这就是复利的魔力，在 AAVE 中，你的 aToken（存款凭证）会自动增长，代表累积利息。

另一个赚钱原理是杠杆借款：存入价值 1000 USD 的 ETH，健康因子允许你借出 800 USD 的 USDC，然后用 USDC 再存入赚取更多利息，形成循环。但杠杆会放大风险，我们稍后讨论。

让我们用代码模拟杠杆过程的简化版：假设抵押率 80%，你存入 ETH，借出 USDC，再用 USDC 存入，形成两次杠杆。原理是计算可借额度 = 抵押价值 \* LTV（Loan-to-Value 比率）。

```python
# 模拟 AAVE 杠杆借款过程
# 假设 ETH 价格 $2000，LTV 80%（可借抵押价值的80%）

eth_price = 2000.0  # ETH 价格 USD
initial_eth = 1.0  # 存入 1 ETH
ltv = 0.80  # 贷款价值比

# 第一步：存入 ETH，计算初始可借额度
collateral_value = initial_eth * eth_price
borrowable = collateral_value * ltv

# 假设借出 USDC 并再存入作为额外抵押（简化循环一次）
additional_collateral = borrowable  # 用借出的 USDC 存入
total_collateral = collateral_value + additional_collateral
final_borrowable = total_collateral * ltv

print(f"初始抵押价值: {collateral_value} USD")
print(f"初始可借: {borrowable} USD")
print(f"杠杆后总抵押: {total_collateral} USD")
print(f"杠杆后可借: {final_borrowable} USD")
```

运行后，初始可借 1600 USD，杠杆后总可借 2880 USD。这展示了如何通过循环借款放大暴露，但实际操作需注意利率和市场波动。

### 风险点

AAVE 虽强大，但 DeFi 世界充满不确定性。核心风险包括：

- **清算风险**：如果抵押品价值下跌（如 ETH 价格跌），健康因子低于 1，你的部分抵押品会被清算拍卖。清算罚金通常 5-10%。
- **智能合约风险**：尽管 AAVE 经过审计，但代码漏洞可能导致资金损失。历史上 DeFi 协议有过黑客事件。
- **市场风险**：利率波动、流动性不足可能导致借款成本上升或无法及时提取资金。
- ** oracle 风险**：AAVE 依赖 Chainlink 等预言机提供价格，如果预言机出错，会影响清算。

一句话总结：高收益伴随高风险，建议从小额开始，监控健康因子 > 1.5。

为了量化清算风险，我们描述原理：健康因子 = (抵押价值 \* 清算阈值) / 借款总额。如果 ETH 跌 20%，健康因子可能降至危险区。

用 Python 模拟清算阈值检查：

```python
# 模拟 AAVE 清算风险
# 假设清算阈值 80%，初始健康因子计算

collateral_value = 2000.0  # 初始抵押 USD
borrow_amount = 1000.0  # 借款 USD
liquidation_threshold = 0.80  # 清算阈值

health_factor = (collateral_value * liquidation_threshold) / borrow_amount

# 模拟价格下跌 20%
new_collateral_value = collateral_value * 0.80
new_health_factor = (new_collateral_value * liquidation_threshold) / borrow_amount

print(f"初始健康因子: {health_factor:.2f}")
print(f"价格跌20%后健康因子: {new_health_factor:.2f}")
if new_health_factor < 1:
    print("警告：将被清算！")
```

初始健康因子 1.60，跌后 1.28，仍安全；但如果跌更多，就触发清算。这帮助你理解为什么需要缓冲。

### 操作流程

使用 AAVE 很简单，但需有以太坊钱包如 MetaMask。步骤如下：

1. **连接钱包**：访问 [https://app.aave.com/](https://app.aave.com/)，点击“Connect Wallet”，选择你的钱包并授权。
2. **选择市场**：AAVE 支持多链，选择 Ethereum 主网或侧链。
3. **存款资产**：在 Dashboard 选资产（如 USDC），输入金额，确认交易。收到 aUSDC 代币代表你的存款。
4. **借款**：启用抵押，选借款资产，输入金额，确保健康因子 >1，确认。
5. **提取或还款**：随时提取存款或还款借款，支付 gas 费。

整个过程链上透明，建议用小额测试。高级用户可探索闪贷，但需写智能合约。

## Pendle

在 DeFi 生态中，Pendle Finance 是另一个备受关注的协议，专注于收益率的 tokenization 和交易。它构建在像 AAVE 这样的基础借贷协议之上，允许用户更精细地管理未来收益。Pendle 的官网是 [https://app.pendle.finance/trade/markets](https://app.pendle.finance/trade/markets)，它提供了一个收益率市场，让你买卖未来的利息。接下来，我们对比一下 Pendle 和 AAVE，帮助你选择合适的工具。

Pendle 是一个收益率 tokenization 协议，主要运行在 Ethereum 和 Arbitrum 等链上。它将 yield-bearing assets（如 AAVE 的 aTokens 或 stETH）分离成两个部分：Principal Token (PT) 和 Yield Token (YT)。

- **收益率分离（Tokenization）**：用户可以将 yield-bearing 资产分成 PT（本金部分，到期可赎回全额底层资产）和 YT（收益率部分，持有可赚取所有未来收益）。
- **收益率交易（Yield Trading）**：在市场上买卖 PT 和 YT，允许锁定固定收益率或投机高收益。
- **流动性提供**：用户可以为 PT/YT 池提供流动性，赚取交易费用和 PENDLE 奖励。
- **其他功能**：如 Zap-in（一键分离资产）、固定收益率锁定，以及与 AAVE 等协议的集成。

相比 AAVE 的借贷焦点，Pendle 更像是一个“收益率衍生品市场”，它利用 AAVE 等产生的收益进行二次创新。

### 赚钱原理

Pendle 的赚钱逻辑基于收益率的分离和市场交易：PT 通常以折扣价交易，代表固定收益率；YT 则像杠杆工具，放大收益率但也放大风险。供需决定价格——如果市场看好未来收益率，YT 价格上涨。

赚钱方式主要有三种：

1. **固定收益**：买入折扣 PT，持有到期赎回全额，赚取隐含收益率。
2. **杠杆收益**：买入 YT，赚取底层资产的所有收益率，但无需持有全额本金。
3. **流动性挖矿**：提供 PT/YT 流动性，赚取费用。

例如，你可以将 1 stETH 分离成 PT-stETH 和 YT-stETH。PT 以 0.95 ETH 价格出售，持有到期得 1 ETH；YT 则赚取所有 stETH 收益。

为了理解收益率分离的原理，我们先描述过程：假设一个 yield-bearing 资产价值 1 ETH，预期年收益率 5%，到期日 1 年。分离后，PT 的价值是本金折扣（基于市场利率），YT 的价值是预期收益的现值。市场交易会调整这些价值。

现在，用 Python 代码模拟一个简化版的收益率 tokenization 过程：定义底层资产、预期收益率、时间到到期，然后计算 PT 和 YT 的理论价值（使用简单折现模型）。

```python
# 模拟 Pendle 收益率 tokenization
# 假设底层资产 1 ETH，预期年收益率 5%，到期 1 年，市场无风险利率 2% 用于折现

underlying_value = 1.0  # 底层资产价值 ETH
expected_annual_yield = 0.05  # 预期年收益率
years_to_maturity = 1.0  # 到期年数
risk_free_rate = 0.02  # 市场无风险利率（用于 YT 折现）

# 计算预期总收益
total_yield = underlying_value * expected_annual_yield * years_to_maturity

# PT 价值：本金折现（简化假设 PT = 底层 / (1 + yield)，但实际市场决定）
pt_value = underlying_value / (1 + expected_annual_yield)

# YT 价值：收益折现
yt_value = total_yield / (1 + risk_free_rate) ** years_to_maturity

print(f"底层资产价值: {underlying_value} ETH")
print(f"PT 价值 (折扣本金): {pt_value:.4f} ETH")
print(f"YT 价值 (预期收益现值): {yt_value:.4f} ETH")
print(f"总和 (PT + YT): {pt_value + yt_value:.4f} ETH")
```

运行后，PT 约为 0.9524 ETH，YT 约为 0.0490 ETH，总和接近 1 ETH。这展示了分离如何创建可交易的部分，在 Pendle 中，你可以买入低价 PT 锁定收益，或买入 YT 杠杆放大。

相比 AAVE 的直接利息赚钱，Pendle 允许你“卖掉”未来收益换取即时流动性，或投机收益率波动，提供更灵活的策略。但它依赖底层协议如 AAVE 的稳定收益率。

### 风险点

Pendle 的风险与 AAVE 类似，但更侧重衍生品层面：

- **市场波动风险**：PT 和 YT 价格受市场情绪影响，如果收益率不如预期，YT 可能贬值到零。
- **到期风险**：持有 YT 到期前卖出可能亏损；PT 如果市场利率涨，价格跌。
- **智能合约和集成风险**：依赖 AAVE 等底层，任何漏洞或 oracle 问题会放大影响。
- **流动性风险**：小众市场可能导致滑点或无法及时交易。

总体上，Pendle 的风险高于 AAVE，因为它是二级衍生品——AAVE 是基础借贷，Pendle 是其上的杠杆工具。建议监控 implied APY（隐含收益率）。

用代码模拟 YT 风险：假设实际收益率低于预期，计算 YT 持有者的损失。

```python
# 模拟 Pendle YT 风险
# 假设买入 YT 价格基于 5% 预期，但实际只有 3%

yt_purchase_price = 0.0490  # 买入 YT 价格 ETH
expected_yield = 0.05  # 预期
actual_yield = 0.03  # 实际
years_to_maturity = 1.0

# 实际收益
actual_return = actual_yield * years_to_maturity  # 简化，无复利

profit_loss = actual_return - yt_purchase_price

print(f"YT 买入价格: {yt_purchase_price:.4f} ETH")
print(f"实际收益: {actual_return:.4f} ETH")
print(f"盈亏: {profit_loss:.4f} ETH")
if profit_loss < 0:
    print("警告：亏损！")
```

如果实际 3%，盈亏 -0.0190 ETH，展示投机风险。AAVE 的风险更偏向清算，而 Pendle 更偏向预测错误。

### 操作流程

Pendle 操作类似于 AAVE，但焦点在收益率市场：

1. **连接钱包**：访问 [https://app.pendle.finance/trade/markets](https://app.pendle.finance/trade/markets)，连接 MetaMask 等。
2. **选择市场**：浏览可用资产（如 stETH），查看到期日和 APY。
3. **分离资产**：用 Zap-in 功能输入资产，一键分离成 PT 和 YT，或直接买卖。
4. **交易或持有**：买入/卖出 PT/YT，提供流动性，或持有到期赎回。
5. **提取**：到期赎回 PT 为底层资产，YT 收益自动流转。

流程更注重交易视图，gas 费类似。初学者从小额 YT 测试。

## 对比总结

AAVE 和 Pendle 互补：AAVE 提供基础借贷和流动性，适合被动存款或杠杆；Pendle 则在 AAVE 等基础上添加收益率衍生，适合主动交易者和对冲者。AAVE 更稳定（TVL 更高），Pendle 更创新但波动大。如果你想简单赚息，用 AAVE；想玩收益率期货，用 Pendle。两者结合（如在 AAVE 存款后用 Pendle tokenization）能解锁更多策略。

通过 AAVE，我们可以解锁加密资产的更多潜力：从简单存款赚息，到杠杆放大收益。添加 Pendle 的对比，让你看到 DeFi 的层级生态。但记住，原理虽简单，风险不可忽视。用上面的代码模拟，你能更好地把握机制。希望这篇文章让你对 DeFi 有新认识，实际操作时多监控市场，并在评论区分享你的经验。保持安全，享受 Web3 的乐趣！
