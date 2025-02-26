---
title: 从零实现区块链 - 侧链与L2
tags: [区块链, web3, 侧链, L2]
categories:
  - [区块链]
date: 2025-02-29
---


web3 是一个非常流行的概念，它的基础是区块链技术。区块链技术是一种分布式账本技术，它的特点是去中心化、不可篡改、安全可靠。区块链技术的应用场景非常广泛，比如数字货币、智能合约、供应链金融等等。

网上关于区块链的资料非常多，但是从零开始构建的资料却很少。熟悉我的朋友应该知道，我经常从零实现一些东西帮助我理解，比如从零实现 git，从零实现 webpack 打包器，从零实现一个框架等等。

本文就是继上一篇 [《Web3 的入口 - 区块链钱包》](https://lucifer.ren/blog/2025/02/16/web3-wallet/ "《从零开始构建区块链》") 的文章，讲述侧链与 L2 的设计理念、技术原理和实现细节。

<!-- more -->

## 前言

由于本文不是科普文章，而是直接带你实现，从而加深理解，因此建议你对区块链技术有一定的了解。如果你对区块链技术还不了解，可以先看一些区块链的基础知识，比如区块链的概念、区块链的特点、区块链的应用等等。比如 [learn_blockchain](https://github.com/chaseSpace/learn_blockchain "learn_blockchain") 就是一个还不错的入门资料集合页。

本文使用 Python 语言来实现区块链，Python 是一种非常流行的编程语言，它的语法简单，非常适合初学者。如果你对 Python 不熟悉也没关系，相信我他真的很容易懂。如果你实在不懂，也可以让 chatgpt 给你解释甚至直接翻译为其他语言。

## 学习建议

为了方便大家直接运行，我提供了相对完整的代码示例。强烈大家边看看在本地跟着一起写，一起运行查看效果，只有动手才可能真正理解其核心。并且尽可能地根据我的思路和代码默写，而不是抄写一遍。


## 区块链的瓶颈与解法

区块链技术自比特币诞生以来，已经从一个神秘的密码学实验演变为去中心化世界的基石。然而，随着应用的扩展，尤其是以太坊上智能合约的流行，区块链的性能瓶颈逐渐暴露：交易吞吐量低、Gas 费用高、确认时间长。这些问题让“区块链要改变世界”听起来像是个遥远的梦。

为了解决这些问题，社区提出了多种扩展方案，其中侧链（Sidechain）和 Layer 2（L2）成为了最受关注的两种技术路径。它们就像高速公路旁的辅路和立交桥，虽然实现方式不同，但目标一致：让区块链更快、更便宜，同时保留去中心化的核心价值。

本文将带你从零开始，探索侧链与 L2 的设计理念、技术原理和实现细节。如果你是个开发者，或者只是对区块链技术好奇，这篇文章会让你对它们的运作有个清晰的认知。


## 侧链：平行世界的分担者

### 1. 什么是侧链？

侧链，顾名思义，是“挂靠”在主链（比如比特币或以太坊）旁边的一条独立区块链。它通过某种机制（通常是双向锚定，Two-way Peg）与主链连接，允许资产在主链与侧链之间安全转移。侧链有自己的共识机制、规则和特性，可以根据需求定制，比如更高的吞吐量或更低的延迟。

想象一下，主链是一座繁忙的大都市，侧链则是旁边的卫星城。卫星城有自己的交通规则，但通过桥梁与主城连接，居民（资产）可以自由来往。

### 2. 侧链的核心技术

- **双向锚定（Two-way Peg）**  
  这是侧链的灵魂。简单来说，就是把主链上的资产“锁定”，然后在侧链上“生成”对应的等值资产；反过来，侧链资产销毁后，主链上的资产解锁。最经典的实现是基于智能合约或多签机制。比如，比特币的侧链 Liquid Network 用多方签名来保证资产转移的安全性。

- **独立共识**  
  侧链可以选择跟主链完全不同的共识算法。主链用 PoW（工作量证明）？侧链可以用 PoS（权益证明）或者 DPoS，甚至是中心化的数据库规则。这种灵活性让侧链能适配不同的场景，比如游戏、支付或企业应用。

- **跨链通信**  
  侧链需要定期与主链同步状态，通常通过提交“检查点”或“默克尔根”来证明自己的合法性。这有点像卫星城定期向主城汇报人口和物资流动。

### 3. 侧链的优劣

**优点：**
- 高度灵活，可以根据需求调整性能和规则。
- 与主链相对独立，风险隔离——侧链崩了，主链不受影响。

**缺点：**
- 去中心化程度可能低于主链，尤其是依赖中心化机制的侧链。
- 跨链桥的安全性是个大问题，黑客最爱盯着这个“桥梁”下手。


### 4. 动手实现一个简单侧链

假设我们要为以太坊写一个玩具侧链，实现 ETH 在主链和侧链之间的转移。下面是实现步骤和伪代码：

1. **主链锁仓合约**  
   用户将 ETH 存入主链合约锁定，并触发事件通知侧链。
```solidity
   contract MainChainLock {
       mapping(address => uint) public lockedBalances;
       event Locked(address user, uint amount);

       // 用户锁仓 ETH
       function lock() external payable {
           lockedBalances[msg.sender] += msg.value;
           emit Locked(msg.sender, msg.value);
       }

       // 解锁 ETH（由侧链触发）
       function unlock(address user, uint amount) external {
           require(lockedBalances[user] >= amount, "Insufficient balance");
           lockedBalances[user] -= amount;
           payable(user).transfer(amount);
       }
   }
```

2. **侧链代币合约**  
   侧链监听主链事件，铸造等值的代币给用户；销毁代币时通知主链解锁。
   
```solidity
   contract SideChainToken {
       mapping(address => uint) public balances;
       event Minted(address user, uint amount);
       event Burned(address user, uint amount);

       // 中继器调用，铸造代币
       function mint(address user, uint amount) external {
           balances[user] += amount;
           emit Minted(user, amount);
       }

       // 用户销毁代币，准备回主链
       function burn(uint amount) external {
           require(balances[msg.sender] >= amount, "Insufficient balance");
           balances[msg.sender] -= amount;
           emit Burned(msg.sender, amount);
       }
   }
```

3. **中继器逻辑（链下）**  
   一个简单的中继器，监听主链和侧链的事件，完成资产转移。
```python
   class Relayer:
       def __init__(self, mainchain, sidechain):
           self.mainchain = mainchain  # 主链合约实例
           self.sidechain = sidechain  # 侧链合约实例

       # 监听主链锁仓事件，触发侧链铸造
       def on_mainchain_locked(self, user, amount):
           self.sidechain.mint(user, amount)
           print(f"Minted {amount} tokens to {user} on sidechain")

       # 监听侧链销毁事件，触发主链解锁
       def on_sidechain_burned(self, user, amount):
           self.mainchain.unlock(user, amount)
           print(f"Unlocked {amount} ETH for {user} on mainchain")
```

4. **运行流程**  
   - 用户调用 `MainChainLock.lock()`，锁定 1 ETH，主链发出 `Locked` 事件。
   - 中继器监听到事件，调用 `SideChainToken.mint()`，用户在侧链获得 1 个代币。
   - 用户在侧链用完代币后调用 `burn(1)`，销毁代币，发出 `Burned` 事件。
   - 中继器监听到事件，调用 `MainChainLock.unlock()`，用户拿回 1 ETH。

这只是个简化版实现，忽略了安全性（比如防止重放攻击）和同步延迟问题。真实的侧链需要更复杂的验证机制，比如默克尔证明或多签确认。


### 说明
- **代码完整性**：补充了主链、侧链和中继器的伪代码，形成了完整的资产转移闭环。
- **简化原则**：保持伪代码风格，避免过多实现细节（如错误处理或事件监听的具体实现），符合原文“玩具级别”的教学定位。
- **改进空间**：如果需要更真实的实现，可以加入时间锁、挑战期或签名验证，但这超出了当前简易目标。


## Layer 2：主链的加速器

### 1. 什么是 L2？

Layer 2 是构建在主链（Layer 1）之上的扩展方案，它不改变主链本身的规则，而是把大量计算和存储卸载到“第二层”，然后定期把结果“打包”回主链。以太坊的 L2 方案尤为活跃，比如 Rollup、状态通道和 Plasma。

如果说侧链是平行宇宙，那 L2 更像是主链的“外包团队”，干活快、成本低，但最终得向主链汇报。

### 2. L2 的主流方案

- **状态通道（State Channels）**  
  两个人下棋，不用每次移动都记录到区块链上，只在游戏开始和结束时上链，中间过程在链下完成。适合高频交互，比如微支付或游戏。

- **Plasma**  
  通过“子链”处理交易，定期把根状态提交到主链。Plasma 像个树状结构，但退出机制复杂，数据可用性问题也让它逐渐被 Rollup 取代。

- **Rollup**  
  当前 L2 的王者，分两种：
  - **Optimistic Rollup**：假设交易有效，出问题再回滚（乐观主义）。
  - **ZK-Rollup**：用零知识证明（ZKP）确保交易正确性（严谨派）。
  Rollup 把数百上千笔交易压缩成一个“批次”，极大降低 Gas 成本。

### 3. Rollup 的技术细节

以 ZK-Rollup 为例：
- **链下计算**：交易在 L2 执行，生成一个状态更新。
- **零知识证明**：用 ZK-SNARK 或 ZK-STARK 证明这些交易有效。
- **上链提交**：把证明和压缩数据提交到主链，主链验证后更新状态。

优点是安全性高（继承主链），缺点是零知识证明的生成成本较高。


### 4. 动手实现一个迷你 Rollup

我们将实现一个简化的 Optimistic Rollup，假设是以太坊为主链。目标是收集链下交易，提交状态根到主链，并提供一个挑战期来验证。以下是步骤和伪代码：

1. **主链 Rollup 合约**  
   负责接收状态根并处理挑战。
   ```solidity
   contract RollupMainChain {
       bytes32 public currentStateRoot;  // 当前状态根
       uint public challengePeriod = 7 days;  // 挑战期
       uint public lastUpdate;  // 上次提交时间
       mapping(bytes32 => bool) public fraudProofs;  // 欺诈证明记录

       event StateUpdated(bytes32 newStateRoot);

       // 提交新的状态根
       function submitState(bytes32 newStateRoot) external {
           currentStateRoot = newStateRoot;
           lastUpdate = block.timestamp;
           emit StateUpdated(newStateRoot);
       }

       // 提交欺诈证明，挑战状态
       function challenge(bytes32 wrongStateRoot) external {
           require(block.timestamp < lastUpdate + challengePeriod, "Challenge period ended");
           fraudProofs[wrongStateRoot] = true;  // 标记为欺诈状态
           // 这里简化，假设回滚到上一个状态
           currentStateRoot = 0x0;  // 假设回滚
       }
   }
   ```

2. **链下 Rollup 处理器**  
   收集交易，计算新状态，并提交到主链。
   ```python
   class RollupProcessor:
       def __init__(self):
           self.state = {}  # 链下状态，比如用户余额
           self.pending_txs = []  # 未处理的交易

       # 添加交易
       def add_tx(self, tx):
           self.pending_txs.append(tx)

       # 处理交易并计算新状态根
       def process_txs(self):
           new_state = self.state.copy()
           for tx in self.pending_txs:
               new_state[tx["from"]] -= tx["amount"]
               new_state[tx["to"]] += tx["amount"]
           self.state = new_state
           self.pending_txs = []
           return self.compute_state_root()

       # 模拟计算状态根（如 Merkle Root）
       def compute_state_root(self):
           return hash(str(self.state))  # 简化版状态根
   ```

3. **中继器逻辑（链下）**  
   将链下计算结果提交到主链。
   ```python
   class RollupRelayer:
       def __init__(self, rollup_contract):
           self.contract = rollup_contract  # 主链合约实例
           self.processor = RollupProcessor()

       # 监听并提交状态
       def submit_state(self):
           new_state_root = self.processor.process_txs()
           self.contract.submitState(new_state_root)
           print(f"Submitted state root: {new_state_root}")

       # 模拟挑战者，检查欺诈
       def challenge_if_invalid(self, expected_state_root):
           if self.contract.currentStateRoot != expected_state_root:
               self.contract.challenge(self.contract.currentStateRoot)
               print("Fraud detected, challenged!")
   ```

4. **运行流程**  
   - 用户在链下发送交易（如 `{"from": "Alice", "to": "Bob", "amount": 10}`），`RollupProcessor` 收集并更新状态。
   - `RollupRelayer` 调用 `process_txs()` 计算新状态根，并通过 `submitState()` 提交到主链。
   - 主链记录状态根，进入 7 天挑战期。
   - 如果有人发现状态错误（如 Alice 余额不足），调用 `challenge()` 提交欺诈证明，回滚状态。

这只是个迷你版 Optimistic Rollup，忽略了 Merkle Tree、数据可用性和完整欺诈证明的细节。真实实现需要更多验证逻辑和数据压缩。


### 说明
- **代码完整性**：补充了主链合约、链下处理器和中继器的伪代码，形成了一个完整的 Optimistic Rollup 工作流。
- **简化设计**：聚焦核心逻辑（状态提交和挑战），省略复杂细节（如 Merkle 证明或 Gas 优化），符合“迷你”目标。
- **一致性**：与侧链部分的风格保持一致，使用 Solidity 和 Python 伪代码，便于理解。


## 侧链 vs L2：谁更胜一筹？

| 特性         | 侧链             | L2             |
|--------------|------------------|----------------|
| 独立性       | 高，自成体系     | 低，依赖主链   |
| 安全性       | 取决于侧链设计   | 继承主链       |
| 开发难度     | 中等             | 较高           |
| 使用场景     | 定制化需求       | 高频低成本交易 |

简单来说：
- 需要完全独立的规则和生态？选侧链。
- 想继承主链的安全性，同时提升性能？选 L2。

## 总结

侧链和 L2 并不是终点，而是区块链扩展性探索中的重要一步。随着技术的进步，我们可能会看到更多融合方案，比如 L2 与侧链结合，或者跨链协议的进一步成熟。作为开发者，理解这些技术的底层逻辑，能让你在 Web3 的浪潮中找到自己的位置。

从零开始实现区块链并不容易，但每一步尝试都在为这个去中心化的未来添砖加瓦。你准备好动手了吗？