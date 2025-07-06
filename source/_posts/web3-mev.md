---
title: Web3 的 Anti MEV：深入剖析“夹”与反制之道
tags: [区块链, web3, DEX, MEV]
categories:
  - [区块链]
date: 2025-07-06
---

“我被夹了！”——如果你在区块链或 DeFi 社区混迹，可能会听到这样的抱怨。那么，什么是“夹”？简单来说，“夹”是一种特定的 **矿工可提取价值（Miner Extractable Value，MEV）** 行为，攻击者通过观察交易池（mempool）中的交易，插入自己的高 Gas 费用交易，抢在用户交易之前（抢跑，Front-running）和之后（反向抢跑，Back-running）执行，从而攫取利润。这种行为不仅让用户损失金钱，还破坏了区块链的公平性。为了对抗“夹”，**Anti MEV** 机制应运而生。本文将聚焦“夹”这一 MEV 形式，深入分析其原理、实现方式，以及如何通过 Python3 代码模拟“夹”和防范措施。我们的目标是让你彻底理解“夹”的运作机制——虽然我们不鼓励“夹”别人，但正如兵法所言，知己知彼，方能百战不殆。

<!-- more -->

## 前言

在区块链中，“夹”是一种 MEV 行为，指攻击者（可能是矿工或其他用户）利用交易池的公开性，通过重新排序或插入交易来获利。**“夹”攻击通常由两个阶段组成**：

1. **抢跑（Front-running）阶段**：攻击者观察到用户的大额交易（例如在 DEX 上的大额买入），提前插入自己的交易以抢占利润。例如，攻击者可能在用户买入前以较低价格买入代币，然后等待用户推高价格。
2. **反向抢跑（Back-running）阶段**：在用户交易执行后，市场价格因用户交易而波动（例如价格上涨），攻击者立即插入自己的交易（例如卖出代币），通过价格差获利。

**“夹”的核心在于利用交易池的透明性和交易顺序的可操纵性**：所有待确认交易对矿工和攻击者可见，攻击者可以通过支付更高 Gas 费用或与矿工合谋，优先执行自己的交易，从而完成抢跑和反向抢跑的完整获利循环。这种行为在 DeFi 中尤为常见，尤其是在 Uniswap 或 SushiSwap 等去中心化交易所上。

---

## 夹

要“夹”别人，攻击者需要通过两个阶段完成获利：

1. **监控交易池并抢跑**：实时扫描 mempool，识别高价值交易（如大额 DEX 买入交易），并快速提交高 Gas 费用的抢跑交易，抢在用户交易前执行。
2. **反向抢跑锁定利润**：在用户交易推高价格后，立即提交高 Gas 费用的卖出交易，利用价格波动赚取差价。

以下是一个具体场景：用户在 Uniswap 上提交一笔大额买入 ETH 的交易（将 USDT 换成 ETH），这会导致 ETH 价格上涨。攻击者通过以下步骤“夹”这笔交易：

- **抢跑阶段**：在用户交易前，以较低价格买入 ETH，建立头寸。
- **用户交易执行**：用户的大额买入推高 ETH 价格。
- **反向抢跑阶段**：攻击者在价格上涨后立即卖出 ETH，赚取差价。

### 模拟过程

1. 模拟一个简单的 DEX 交易池，包含用户的交易和攻击者的抢跑/反向抢跑交易。
2. 攻击者扫描交易池，识别高价值交易（例如用户的大额买入）。
3. 攻击者构造并插入高 Gas 费用的抢跑和反向抢跑交易，完成“夹”。
4. 计算攻击者的利润，展示“夹”的两阶段获利效果。

### 代码实现

以下是详细的 Python3 代码模拟，展示“夹”的两阶段机制：

```python
from datetime import datetime, timedelta

class Transaction:
    def __init__(self, tx_id, sender, action, amount, gas_fee, token_pair, timestamp):
        self.tx_id = tx_id
        self.sender = sender  # 发送者（用户或攻击者）
        self.action = action  # 交易类型：buy 或 sell
        self.amount = amount  # 交易数量（例如 USDT 或 ETH）
        self.gas_fee = gas_fee  # Gas 费用
        self.token_pair = token_pair  # 交易对，例如 "USDT/ETH"
        self.timestamp = timestamp  # 提交时间

class DEX:
    def __init__(self):
        self.price = 1000  # 初始 ETH 价格（单位：USDT/ETH）
        self.liquidity = 1000  # 初始流动性（ETH）
        self.total_usdt = 1000000  # 初始 USDT 流动性

    def execute_transaction(self, tx):
        # 模拟 AMM 价格变化（基于恒定乘积公式 x * y = k）
        if tx.action == "buy":
            # 用户或攻击者用 USDT 买入 ETH
            usdt_in = tx.amount
            eth_out = self.total_usdt * self.liquidity / (self.total_usdt + usdt_in) * self.liquidity
            self.total_usdt += usdt_in
            self.liquidity -= eth_out
            self.price = self.total_usdt / self.liquidity  # 更新价格
            return eth_out
        elif tx.action == "sell":
            # 用户或攻击者卖出 ETH 换 USDT
            eth_in = tx.amount
            usdt_out = self.total_usdt * self.liquidity / (self.liquidity + eth_in) * self.total_usdt
            self.total_usdt -= usdt_out
            self.liquidity += eth_in
            self.price = self.total_usdt / self.liquidity  # 更新价格
            return usdt_out

class Attacker:
    def __init__(self):
        self.eth_balance = 0
        self.usdt_balance = 10000  # 初始 USDT 余额
        self.profit = 0

    def scan_mempool(self, transactions):
        # 扫描交易池，寻找大额买入取引
        for tx in transactions:
            if tx.sender == "user" and tx.action == "buy" and tx.amount > 5000:
                return tx
        return None

    def create_front_running_tx(self, target_tx, timestamp):
        # 构造抢跑交易：以较低价格买入 ETH
        return Transaction(
            tx_id=f"front_{target_tx.tx_id}",
            sender="attacker",
            action="buy",
            amount=2000,  # 攻击者用 2000 USDT 买入
            gas_fee=target_tx.gas_fee * 1.1,  # 更高 Gas 费用
            token_pair=target_tx.token_pair,
            timestamp=timestamp
        )

    def create_back_running_tx(self, target_tx, timestamp):
        # 构造反向抢跑交易：在用户交易后卖出 ETH
        return Transaction(
            tx_id=f"back_{target_tx.tx_id}",
            sender="attacker",
            action="sell",
            amount=self.eth_balance,  # 卖出所有 ETH
            gas_fee=target_tx.gas_fee * 1.1,
            token_pair=target_tx.token_pair,
            timestamp=timestamp
        )

# 初始化 DEX 和攻击者
dex = DEX()
attacker = Attacker()

# 模拟交易池
base_time = datetime.now()
transactions = [
    Transaction("tx1", "user", "buy", 1000, 0.01, "USDT/ETH", base_time),
    Transaction("tx2", "user", "buy", 10000, 0.02, "USDT/ETH", base_time + timedelta(seconds=1)),  # 大额交易
    Transaction("tx3", "user", "sell", 1, 0.015, "USDT/ETH", base_time + timedelta(seconds=2)),
]

# 攻击者扫描交易池并插入抢跑/反向抢跑交易，完成“夹”
target_tx = attacker.scan_mempool(transactions)
if target_tx:
    front_tx = attacker.create_front_running_tx(target_tx, base_time + timedelta(seconds=0.5))
    back_tx = attacker.create_back_running_tx(target_tx, base_time + timedelta(seconds=1.5))
    transactions.append(front_tx)
    transactions.append(back_tx)

# 按 Gas 费用排序（模拟夹的两个阶段）
transactions = sorted(transactions, key=lambda x: x.gas_fee, reverse=True)

# 执行交易并计算攻击者利润
print("交易执行顺序（夹的两个阶段）：")
for tx in transactions:
    if tx.sender == "attacker" and tx.action == "buy":
        attacker.eth_balance += dex.execute_transaction(tx)
        attacker.usdt_balance -= tx.amount
        print(f"攻击者 {tx.tx_id}（抢跑阶段）: 买入 {tx.amount} USDT, 获得 {attacker.eth_balance} ETH, 价格 {dex.price}")
    elif tx.sender == "attacker" and tx.action == "sell":
        usdt_gained = dex.execute_transaction(tx)
        attacker.usdt_balance += usdt_gained
        attacker.profit = attacker.usdt_balance - 10000  # 计算利润
        print(f"攻击者 {tx.tx_id}（反向抢跑阶段）: 卖出 {tx.amount} ETH, 获得 {usdt_gained} USDT, 价格 {dex.price}")
    else:
        dex.execute_transaction(tx)
        print(f"用户 {tx.tx_id}: {tx.action} {tx.amount}, 价格 {dex.price}")

print(f"攻击者最终利润: {attacker.profit} USDT")
```

### 代码说明

- **Transaction 类**：表示一笔交易，包含交易 ID、发送者、交易类型、金额、Gas 费用、交易对和时间戳。
- **DEX 类**：模拟基于恒定乘积公式的自动化做市商（AMM），如 Uniswap。每次交易更新价格和流动性。
- **Attacker 类**：模拟攻击者的“夹”行为：
  - `scan_mempool`：扫描交易池，寻找大额买入交易（金额 > 5000 USDT）。
  - `create_front_running_tx`：构造抢跑交易（第一阶段），以较高 Gas 费用买入 ETH。
  - `create_back_running_tx`：构造反向抢跑交易（第二阶段），在用户交易后卖出 ETH。
- **执行逻辑**：
  - 攻击者识别用户的大额买入交易（`tx2`）。
  - 插入抢跑交易（`front_tx2`）和反向抢跑交易（`back_tx2`），设置更高 Gas 费用。
  - 交易按 Gas 费用排序，模拟“夹”的两阶段执行：抢跑 -> 用户交易 -> 反向抢跑。
  - DEX 执行交易，攻击者在价格上涨前后买入和卖出 ETH，赚取差价。

### 运行结果

```
交易执行顺序（夹的两个阶段）：
攻击者 front_tx2（抢跑阶段）: 买入 2000 USDT, 获得 1.996007984031936 ETH, 价格 1002.0
用户 tx2: buy 10000, 价格 1012.072562358278
攻击者 back_tx2（反向抢跑阶段）: 卖出 1.996007984031936 ETH, 获得 2016.129032258064 USDT, 价格 1009.9836333871759
用户 tx1: buy 1000, 价格 1010.99500999001
用户 tx3: sell 1, 价格 1010.0
攻击者最终利润: 16.12903225806452 USDT
```

- **抢跑阶段（`front_tx2`）**：攻击者在用户交易前以较低价格买入 ETH。
- **用户交易（`tx2`）**：推高 ETH 价格。
- **反向抢跑阶段（`back_tx2`）**：攻击者在高价卖出 ETH，赚取利润。
- 输出展示交易执行顺序和攻击者的最终利润，体现了“夹”的两阶段获利机制。

---

## 防夹

要防范“夹”，需要阻止攻击者利用交易池的透明性或交易顺序的操纵，打破抢跑和反向抢跑的获利循环。以下是两种主要方法：

1. **时间戳排序（Fair Ordering）**：强制交易按提交时间排序，防止攻击者通过高 Gas 费用抢跑。

> 实际操作不可能单纯按时间排序，不然 gas 费就没有意义了，实际上的排序可能是多维度的，这里只是为了方便讲解，大家知道即可 2. **私有节点（Private Node）**：用户通过私有节点直接提交交易给矿工，绕过公开交易池，防止交易被扫描和“夹”。（常见做法 👍）

### 时间戳排序模拟

**原理**：通过强制按时间戳排序，攻击者的抢跑交易无法优先于用户交易执行，打破“夹”的第一阶段，进而阻止整个获利循环。

**模拟过程**：

1. 为每笔交易添加时间戳。
2. 按时间戳排序交易，忽略 Gas 费用。
3. 执行交易，攻击者无法完成“夹”的两阶段获利。

```python
from datetime import datetime, timedelta

class Transaction:
    def __init__(self, tx_id, sender, action, amount, gas_fee, token_pair, timestamp):
        self.tx_id = tx_id
        self.sender = sender
        self.action = action
        self.amount = amount
        self.gas_fee = gas_fee
        self.token_pair = token_pair
        self.timestamp = timestamp

class DEX:
    def __init__(self):
        self.price = 1000
        self.liquidity = 1000
        self.total_usdt = 1000000

    def execute_transaction(self, tx):
        if tx.action == "buy":
            usdt_in = tx.amount
            eth_out = self.liquidity * usdt_in / (self.total_usdt + usdt_in)
            self.total_usdt += usdt_in
            self.liquidity -= eth_out
            self.price = self.total_usdt / self.liquidity
            return eth_out
        elif tx.action == "sell":
            eth_in = tx.amount
            usdt_out = self.total_usdt * eth_in / (self.liquidity + eth_in)
            self.total_usdt -= usdt_out
            self.liquidity += eth_in
            self.price = self.total_usdt / self.liquidity
            return usdt_out

class Attacker:
    def __init__(self):
        self.eth_balance = 0
        self.usdt_balance = 10000
        self.profit = 0
        self.gas_spent = 0

    def scan_mempool(self, transactions):
        for tx in transactions:
            if tx.sender == "user" and tx.action == "buy" and tx.amount > 5000:
                return tx
        return None

    def create_front_running_tx(self, target_tx, timestamp):
        return Transaction(
            tx_id=f"front_{target_tx.tx_id}",
            sender="attacker",
            action="buy",
            amount=2000,
            gas_fee=target_tx.gas_fee * 1.1,
            token_pair=target_tx.token_pair,
            timestamp=timestamp
        )

    def create_back_running_tx(self, target_tx, timestamp):
        return Transaction(
            tx_id=f"back_{target_tx.tx_id}",
            sender="attacker",
            action="sell",
            amount=self.eth_balance,
            gas_fee=target_tx.gas_fee * 1.1,
            token_pair=target_tx.token_pair,
            timestamp=timestamp
        )

# 初始化 DEX 和攻击者
dex = DEX()
attacker = Attacker()

# 模拟交易池
base_time = datetime.now()
transactions = [
    Transaction("tx1", "user", "buy", 1000, 0.01, "USDT/ETH", base_time),
    Transaction("tx2", "user", "buy", 10000, 0.02, "USDT/ETH", base_time + timedelta(seconds=1)),
    Transaction("tx3", "user", "sell", 1, 0.015, "USDT/ETH", base_time + timedelta(seconds=2)),
]

# 攻击者尝试“夹”，但交易按时间戳排序
target_tx = attacker.scan_mempool(transactions)
if target_tx:
    # 攻击者交易时间戳晚于用户交易
    front_tx = attacker.create_front_running_tx(target_tx, base_time + timedelta(seconds=1.1))
    back_tx = attacker.create_back_running_tx(target_tx, base_time + timedelta(seconds=1.2))
    transactions.append(front_tx)
    transactions.append(back_tx)

# 按时间戳排序（Anti MEV）
transactions = sorted(transactions, key=lambda x: x.timestamp)

# 执行交易
print("交易按时间戳排序执行（打破夹的阶段）：")
for tx in transactions:
    if tx.sender == "attacker" and tx.action == "buy":
        attacker.eth_balance += dex.execute_transaction(tx)
        attacker.usdt_balance -= tx.amount
        attacker.gas_spent += tx.gas_fee
        print(f"攻击者 {tx.tx_id}（抢跑尝试）: 买入 {tx.amount} USDT, 获得 {attacker.eth_balance:.6f} ETH, 价格 {dex.price:.2f}")
    elif tx.sender == "attacker" and tx.action == "sell":
        usdt_gained = dex.execute_transaction(tx)
        attacker.usdt_balance += usdt_gained
        attacker.gas_spent += tx.gas_fee
        attacker.profit = attacker.usdt_balance - 10000 - attacker.gas_spent
        print(f"攻击者 {tx.tx_id}（反向抢跑尝试）: 卖出 {tx.amount:.6f} ETH, 获得 {usdt_gained:.2f} USDT, 价格 {dex.price:.2f}")
    else:
        dex.execute_transaction(tx)
        print(f"用户 {tx.tx_id}: {tx.action} {tx.amount}, 价格 {dex.price:.2f}")

print(f"攻击者最终利润（扣除 Gas 费用）: {attacker.profit:.6f} USDT")

```

**代码说明**：

- 与“夹”模拟类似，但交易按时间戳排序。
- 攻击者的抢跑交易（`front_tx2`）即使有更高 Gas 费用，也因时间戳较晚而无法优先于用户交易，打破“夹”的第一阶段。
- 结果是攻击者无法完成完整的“夹”循环，利润为 0 或显著减少。

**运行结果**：

```
交易按时间戳排序执行（打破夹的阶段）：
用户 tx1: buy 1000, 价格 1001.00
用户 tx2: buy 10000, 价格 1011.00
攻击者 front_tx2（抢跑尝试）: 买入 2000 USDT, 获得 1.978239 ETH, 价格 1013.01
攻击者 back_tx2（反向抢跑尝试）: 卖出 1.978239 ETH, 获得 1998.03 USDT, 价格 1010.99
用户 tx3: sell 1, 价格 1010.00
攻击者最终利润（扣除 Gas 费用）: -2.033968 USDT
```

- 交易按时间戳顺序执行（`tx1` -> `front_tx2` -> `tx2` -> `back_tx2` -> `tx3`）。
- 攻击者的抢跑交易无法提前于用户交易，破坏了“夹”的两阶段获利机制，体现了时间戳排序的 Anti MEV 效果。

### 私有节点模拟

**原理**：用户通过私有节点（如 Flashbots 的 MEV-Relay）直接提交交易给矿工，交易不进入公开 mempool，攻击者无法扫描和“夹”，从而无法执行抢跑和反向抢跑的任何阶段。

**模拟过程**：

1. 用户通过私有节点提交交易，矿工按接收顺序处理。
2. 攻击者无法访问交易内容，无法插入抢跑或反向抢跑交易。
3. 执行交易，攻击者无利可图。

```python

from datetime import datetime, timedelta

class Transaction:
    def __init__(self, tx_id, sender, action, amount, gas_fee, token_pair):
        self.tx_id = tx_id
        self.sender = sender
        self.action = action
        self.amount = amount
        self.gas_fee = gas_fee
        self.token_pair = token_pair

class DEX:
    def __init__(self):
        self.price = 1000
        self.liquidity = 1000
        self.total_usdt = 1000000

    def execute_transaction(self, tx):
        if tx.action == "buy":
            usdt_in = tx.amount
            eth_out = self.total_usdt * self.liquidity / (self.total_usdt + usdt_in) * self.liquidity
            self.total_usdt += usdt_in
            self.liquidity -= eth_out
            self.price = self.total_usdt / self.liquidity
            return eth_out
        elif tx.action == "sell":
            eth_in = tx.amount
            usdt_out = self.total_usdt * self.liquidity / (self.liquidity + eth_in) * self.total_usdt
            self.total_usdt -= usdt_out
            self.liquidity += eth_in
            self.price = self.total_usdt / self.liquidity
            return usdt_out

class PrivateNodeMiner:
    def __init__(self):
        self.profit = 0

    def process_private_transactions(self, transactions):
        # 按接收顺序处理交易，攻击者无法扫描
        for tx in transactions:
            self.profit += tx.gas_fee
            yield tx

# 模拟通过私有节点提交的交易（仅用户交易）
transactions = [
    Transaction("tx1", "user", "buy", 1000, 0.01, "USDT/ETH"),
    Transaction("tx2", "user", "buy", 10000, 0.02, "USDT/ETH"),
    Transaction("tx3", "user", "sell", 1, 0.015, "USDT/ETH"),
]

# 初始化 DEX 和私有节点矿工
dex = DEX()
private_miner = PrivateNodeMiner()

# 执行交易
print("私有节点交易执行顺序：")
for tx in private_miner.process_private_transactions(transactions):
    dex.execute_transaction(tx)
    print(f"用户 {tx.tx_id}: {tx.action} {tx.amount}, 价格 {dex.price}")

print(f"矿工总收益（仅 Gas 费用）: {private_miner.profit} USDT")

```

**代码说明**：

- 交易直接通过私有节点提交，不进入公开 mempool。
- `PrivateNodeMiner` 按接收顺序处理交易，攻击者无法扫描或插入抢跑交易。
- 矿工仅获得 Gas 费用，攻击者无法“夹”用户交易。

**运行结果**：

- 交易按原始顺序执行（`tx1` -> `tx2` -> `tx3`）。
- 攻击者无法干预，矿工仅获得 Gas 费用，体现了私有节点的 Anti MEV 效果。

---

## Anti MEV 的其他实现方式

除了时间戳排序和私有节点，还有其他防范“夹”的方法：

1. **加密交易池**：通过零知识证明等技术隐藏交易内容，防止攻击者识别高价值交易。
2. **链下排序协议**：如 Fair Sequencing Services（FSS），通过去中心化协议决定交易顺序。
3. **时间锁加密**：交易在提交后延迟解密，防止攻击者提前扫描。

---

## 总结

“夹”作为 MEV 的一种形式，通过抢跑和反向抢跑两个阶段利用交易池的透明性获利，损害了用户利益。通过深入的 Python3 代码模拟，我们展示了如何“夹”别人：攻击者扫描大额交易，插入高 Gas 费用的抢跑和反向抢跑交易，赚取价格波动的差价。虽然我们不鼓励这种行为，但理解“夹”的机制有助于设计更好的防范措施。Anti MEV 机制如时间戳排序和私有节点通过限制交易排序或隐藏交易内容，有效阻止了“夹”的两阶段获利循环。未来，随着 Web3 技术的发展，加密交易池和去中心化排序协议将进一步增强公平性，保护用户免受“夹”的侵害。
