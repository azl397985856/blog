---
title: 更加安全的区块链钱包：MPC 钱包
tags: [区块链, web3, 钱包, MPC 钱包, Web3 钱包, 数字钱包, 多签钱包, 冷钱包]
categories:
  - [区块链]
date: 2025-03-05
---

web3 是一个非常流行的概念，它的基础是区块链技术。区块链技术是一种分布式账本技术，它的特点是去中心化、不可篡改、安全可靠。区块链技术的应用场景非常广泛，比如数字货币、智能合约、供应链金融等等。

网上关于区块链的资料非常多，但是从零开始构建的资料却很少。熟悉我的朋友应该知道，我经常从零实现一些东西帮助我理解，比如从零实现 git，从零实现 webpack 打包器，从零实现一个框架等等。

本文就是继上一篇 [《Web3 的入口 - 区块链钱包》](https://lucifer.ren/blog/2025/02/16/web3-wallet/ "《Web3 的入口 - 区块链钱包》") 的文章，讲述 MPC 钱包是什么，原理是什么，以及多签钱包是什么，它们都是如何增强区块链钱包的安全性的。

<!-- more -->

## 前言

由于本文不是科普文章，而是直接带你实现，从而加深理解，因此建议你对区块链技术有一定的了解。如果你对区块链技术还不了解，可以先看一些区块链的基础知识，比如区块链的概念、区块链的特点、区块链的应用等等。比如 [learn_blockchain](https://github.com/chaseSpace/learn_blockchain "learn_blockchain") 就是一个还不错的入门资料集合页。

本文使用 Python 语言来实现区块链，Python 是一种非常流行的编程语言，它的语法简单，非常适合初学者。如果你对 Python 不熟悉也没关系，相信我他真的很容易懂。如果你实在不懂，也可以让 chatgpt 给你解释甚至直接翻译为其他语言。

## 学习建议

为了方便大家直接运行，我提供了相对完整的代码示例。强烈大家边看看在本地跟着一起写，一起运行查看效果，只有动手才可能真正理解其核心。并且尽可能地根据我的思路和代码默写，而不是抄写一遍。

Web3 的世界里，钱包不仅是资产的容器，更是安全与隐私的守护者。在区块链的去中心化浪潮中，多签（Multisig）和多方安全计算（MPC，Multi-Party Computation）作为两种核心技术，频频被提及。前者是区块链原生支持的经典方案，后者则是密码学领域的新星。今天，我们将从零开始，带你走进 MPC 的实现逻辑，剖析多签的原理，用 Python 代码为你解锁它们的奥秘，同时对比两者的优劣，最后聊聊业内优秀钱包供应商的支持情况，以及普通人如何上手使用。

---

上一篇我们提到了 MPC 钱包。我是这么说的：


> 有一种先进的钱包叫做 MPC 钱包，即 multi-party computation 钱包。MPC 钱包可以让多个分片一起参与签名，从而提高安全性。MPC 钱包的实现原理是基于多方计算，比如多方一起计算出签名，然后再把结果聚合起来。你的钱包会被分为三个分片，只有拥有两个及以上的分片签名的结果才算有效。一般来说，一个分片保存在用户本地，另外一个保存在托管的钱包 App，第三个上传到云端，比如 iCloud。这样一来，即使你的私钥泄漏给了黑客，由于黑客只有一片私钥，也无法通过你的签名来控制资产。

这一节我们继续详细讲述一下 MPC 钱包是什么，以及它是如何增强区块链钱包的安全性的。对于普通人又该如何使用呢？

在讲述 MPC 之前，我们先来看看和 MPC 很像的，被很多人误以为就是 MPC 的**多签（Multi-Signature）**。这对我们理解 MPC 很有帮助。

## 多签

### 什么是多签

多签，顾名思义，就是多重签名（Multi-Signature）。它是一种基于区块链智能合约的机制，要求一笔交易必须获得多个私钥的签名才能执行。想象一个保险箱，需要三把钥匙中的两把才能打开——这就是多签的直观比喻。

在比特币、以太坊等区块链中，多签通常以 `M-of-N` 的形式实现：
- **N**：总共有 N 个参与方的私钥。
- **M**：需要其中 M 个签名（M ≤ N）才能完成交易。

以比特币为例，多签地址由多个公钥生成，交易脚本会嵌入一个条件：只有当提供 M 个有效签名时，资金才能被转移。这种机制的核心是**分散风险**——单个私钥丢失或泄露不会导致资产全损。

对于以太坊来说，**多签就是一个智能合约**，它要求一笔交易必须获得多个私钥的签名才能执行。智能合约的执行需要消耗一定成本（gas），因此多签的使用场景也受到限制。想象下你每次 approve 都需要花费 gas，多难受？因此普通人其实不怎么需要多签，更多的是企业。比如前段时间的 Bybit的多签冷钱包被黑，损失约14.6亿美元，那就是一种多签钱包。

智能合约就是一段代码，每个合约都有一个地址，这个地址就可以发给别人，让别人给你转钱，也可以作为 sender 来执行一笔交易。这个合约里面的逻辑就是**转发请求到之前配置好的多个账号，让它们签名，然后判断签名是否正确并且否有足够的签名**，如果全部满足则**自动执行**转账操作。

一句话来总结以太坊的多签机制：


> 多签本质是智能合约，即一段代码，代码的逻辑是：转发签名请求到 N 个参与方，收到至少 M 个合法签名后，才自动执行真正的签名动作。

### 代码实现

我们可以用 Python 的 `ecdsa` 库来模拟一个简单的多签签名过程。以下是一个简化版的多签实现：

```python
# 1. 第一步：生成 N个密钥对
import ecdsa
import hashlib

# 生成多个私钥和公钥对
def generate_keypair():
    private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    public_key = private_key.get_verifying_key()
    return private_key, public_key

# 模拟交易数据
message = "Send 1 BTC to Alice".encode()
message_hash = hashlib.sha256(message).digest()

# 创建 3 个密钥对 (3-of-3 示例)
keys = [generate_keypair() for _ in range(3)]
private_keys = [k[0] for k in keys]
public_keys = [k[1] for k in keys]

# 2. 第二步：收到签名请求，转发给 N 个参与方

# 签名
signatures = []
for priv_key in private_keys:
    signature = priv_key.sign(message_hash)
    signatures.append(signature)

# 3. 第三步：验证签名 (需要至少 M 个签名通过)
def verify_multisig(pub_keys, signatures, message_hash, m):
    valid_count = 0
    for pub_key, sig in zip(pub_keys, signatures):
        try:
            if pub_key.verify(sig, message_hash):
                valid_count += 1
        except:
            continue
    return valid_count >= m

# 4. 第四步：检查是否满足 2-of-3 条件
result = verify_multisig(public_keys, signatures[:2], message_hash, 2)
print("2-of-3 多签验证结果:", result)
```

这段代码展示了如何生成密钥对、签名交易并验证多签条件。虽然现实中的多签依赖区块链脚本（如 Bitcoin 的 `OP_CHECKMULTISIG`），但这个例子足以说明其核心逻辑：分散控制权，依赖多方协作。

## MPC

在介绍 MPC 之前，我们先了解一下无私钥。

### 无私钥

相比于上一篇文章反复强调的**用户必要保管好自己的私钥**，实际上还有一种无私钥方案。用户无需保持私钥或助记词，甚至在丢失本地私钥分片的情况下还可以通过**恢复**的方式来找回钱包。这在传统的钱包中是不可能的。这其实给了**去中心化钱包了一点中心化的味道**。

MPC 就是实现“无私钥体验”的一种技术手段。在某些语境下，人们将基于 MPC 的钱包称为“无私钥钱包”（Keyless Wallet），主要是因为用户在使用过程中无需直接管理完整的私钥，而是通过分布式计算间接控制资产。这种称呼更多是**营销或用户体验层面的简化**，而非技术上的精确描述。并且这里的无私钥也并非没有私钥，而是**没有完整私钥，仅有私钥的碎片**。

传统热钱包或冷钱包如果私钥丢失且无备份，资产 100% 无法找回。MPC 的优势在于分布式特性，只要部分碎片或参与方可用，就能挽救局面。当然如果用户丢失所有碎片（如所有绑定设备损坏，且无备份），资产将无法恢复。这与传统钱包丢失种子短语的结果一致。但优秀 MPC 钱包会通过设计（如分布式备份）尽量避免这种情况。


### 什么是 MPC

相比多签的区块链原生特性，MPC（多方安全计算）更像是一个密码学领域的“黑魔法”。它允许多个参与方在不泄露各自输入的情况下，共同计算一个结果。MPC 的核心思想是**秘密共享**（Secret Sharing），通过将私钥拆分成多个碎片（Shares），分散存储和计算。

关于秘密共享，大家可以参考维基百科的[秘密共享](https://zh.wikipedia.org/wiki/%E7%A7%98%E5%AF%86%E5%88%86%E4%BA%AB "秘密共享")词条。

MPC 的典型实现基于 Shamir 秘密共享方案：
1. **私钥拆分**：一个私钥被拆成 N 个碎片，任何 M 个碎片可以重构完整私钥（M ≤ N）。
2. **分布式计算**：每个参与方持有自己的碎片，通过数学协议（如加法、乘法同态）计算部分签名。
3. **签名合成**：将部分签名合并为一个完整签名，无需在任何节点上重构完整私钥。

与多签不同，MPC 不依赖区块链的原生支持，而是通过链下计算实现类似的多方验证效果。这意味着它更灵活，但也更复杂。**也就是说多签依赖于具体的链上协议，比如在比特币链上的多签就和以太坊上的多签不一样。但是对于 MPC 来说，是链无感的，也就是说不管是比特币还是以太坊，MPC 都可以用，并且使用起来没有任何差别**。

MPC 会先在内存中生成一个临时的私钥，这个私钥仅在生成的时候在内存中出现，不会持久化。比如我们创建三个分片，要求两片就可以恢复完整私钥。那么三片交给三个人来保管，需要签名就通过三个中的两个来完成。

一句话来总结 MPC 的原理：


> MPC 依赖秘密共享，通过数学协议计算部分签名，然后合并签名来完成交易。普通用户保存一份私钥，平台和云保存部分私钥。避免了“单点问题”，即用户私钥被泄露后财产损失，极大地提高了安全性。

### 代码实现

我们可以用 `secretsharing` 库模拟一个基于 Shamir 秘密共享的 MPC 签名过程：

```python
from secretsharing import SecretSharer
import ecdsa
import hashlib

# 第一步： 生成一个私钥
private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
private_key_hex = private_key.to_string().hex()

# 第二步：将私钥拆分为 3 个碎片，2 个即可恢复 (2-of-3)
shares = SecretSharer.split_secret(private_key_hex, 2, 3)

# 模拟交易
message = "Send 1 ETH to Bob".encode()
message_hash = hashlib.sha256(message).digest()

# 第三步：用 2 个碎片恢复私钥
recovered_key_hex = SecretSharer.recover_secret(shares[:2])
recovered_key = ecdsa.SigningKey.from_string(bytes.fromhex(recovered_key_hex), curve=ecdsa.SECP256k1)

# 第四步：生成签名
signature = recovered_key.sign(message_hash)
print("MPC 恢复签名:", signature.hex())

# 第五步：验证签名
public_key = recovered_key.get_verifying_key()
print("签名验证结果:", public_key.verify(signature, message_hash))
```

这里我们用 Shamir 方案拆分私钥并恢复签名。但真实的 MPC 更复杂，会涉及分布式签名协议（如 GG18 或 CGGMP），避免任何一方直接拿到完整私钥。


## 如何创建和使用多签与 MPC？

### 创建和使用多签
1. **创建多签地址**：
   - 使用钱包软件（如 Gnosis Safe 或 MetaMask + 多签插件）。
   - 设置 M 和 N（如 2-of-3），输入参与方的公钥。（一般会有 UI 界面，让你输入 M 和 N，然后直接 create 地址。）
   - 部署到区块链（如以太坊上创建一个多签合约）。
2. **使用多签**：
   - 发起交易时，收集 M 个签名。
   - 提交到区块链验证并执行。

### 创建和使用 MPC
1. **创建 MPC 钱包**：
   - 选择支持 MPC 的钱包（比如某安钱包或者某易钱包）。
   - 进入后选择创建 MPC 钱包，系统会自动生成私钥并拆分碎片，分发给参与方或设备。钱包 APP 自动保存一份，你自己保存两个。一般要求你一个保存到本地，另一个上传到云端。
2. **使用 MPC**：
   - 发起交易时，各方通过协议计算部分签名。
   - 合并签名后提交到链上，无需手动管理私钥。

目前，MPC 钱包在个人更受欢迎，因其安全性和跨链能力；多签则在机构市场中占据主流。


## 多签 vs MPC

最后来一个简单的对比。

| **维度**         | **多签（Multisig）**                     | **MPC**                              |
|-------------------|-----------------------------------------|-------------------------------------|
| **实现位置**     | 链上（依赖区块链协议）                  | 链下（密码学协议）                  |
| **私钥管理**     | 多个独立私钥                           | 单私钥拆分碎片                     |
| **灵活性**       | 受限于区块链支持                       | 可跨链、跨场景                     |
| **透明性**       | 签名可追踪（可问责）                   | 签名匿名（无个体追溯性）           |
| **使用成本**     | 高（需要支付合约交互的 gas 费用）                     | 低（无需额外支付 gas 费用）           |
| **计算成本**     | 低（链上验证简单）                     | 高（需要多方通信和计算）           |
| **单点风险**     | 无（分散私钥）                         | 低（无需重组私钥）                 |

- **多签的优势**：简单直接，链上原生支持，适合需要透明性和可问责性的场景（如公司资金管理）。
- **MPC 的优势**：隐私性更强，灵活性更高，适合跨链或复杂隐私需求的场景（如机构间的联合计算）。

Vitalik Buterin 曾提到，MPC 的一个潜在风险是“碎片永久性”——如果过去的持有者串通，可能威胁资产安全。而多签则因链上记录清晰，避免了这一问题。


## 聊聊最近的黑客事件

### 前置知识

最近，一家名为 Bybit 的交易平台被黑客攻击，损失了约 14.6 亿美元。这家交易平台的多签钱包被黑客攻击，导致用户资产损失。而 Bybit 使用的就是多签冷钱包。

多签钱包我们已经知道了，就是需要多个私钥签名才能执行交易的钱包。那什么是冷钱包呢？

冷钱包（Cold Wallet）是一种存储加密货币私钥的方式，其核心特点是将私钥与互联网完全隔离，以最大程度地提高安全性。简单来说，冷钱包就像一个“离线保险箱”，专门用来存放你的数字资产密钥，避免因网络攻击、恶意软件或设备被黑而导致资产丢失。冷钱包通过物理隔离，确保私钥不会暴露在联网环境中。常见的实现方式包括：

- 硬件钱包：如 Ledger、Trezor，使用专用设备存储私钥。
- 纸钱包：将私钥和公钥打印在纸上，纯物理存储。
- 离线设备：如一台永不联网的电脑或 U 盘。

与冷钱包相对的是热钱包（Hot Wallet），后者始终联网（如手机钱包或交易所账户），方便交易但安全性较低。大多数个人使用的都是热钱包。

冷钱包会在离线环境中生成私钥和对应的公钥地址。接下来将加密货币转入冷钱包的公钥地址。需要使用资产时，在离线设备上签名交易（生成一串签名数据），然后通过其他联网设备广播到区块链。

### 攻击过程

1. 黑客通过社会工程学搞定了一个关键人物的私钥。
2. 黑客修改了前端页面，伪造了一个看起来正常的交易请求，并将其发送给用户。但实际上这个请求会将钱包的钱全部转到多个钱包地址。
3. 黑客通过第一步获取的私钥，对交易请求进行签名，并等待其他人签名。由于前端页面已经被黑客修改了，因此骗过了其他人。

可以看出尽管有多签的冷钱包，但由于交易请求的前端页面被黑客修改，导致用户误操作，导致资产损失。

### 如何防范

使用多签提高安全性还不够，我们也要小心前端页面被修改，导致你认为的操作和实际操作不一致。那普通人怎么能做到呢？除非你是程序员，否则很难。但是还是有办法可以提高安全性。

这里给大家两条建议：

**1. 使用硬件钱包**：

其实硬件钱包会有一个小小的屏幕，你可以直接通过这个屏幕来查看交易，而不是通过前端页面。相比修改 web 页面，硬件上的代码被黑客修改的概率要低得多。

因此一个有用的建议就是，不要依赖于前端页面，而是使用硬件钱包来签名交易。但这不管是使用成本还是持有成本都比较高，因此建议用户做好资产隔离，对于重要的资金，不常使用的地方使用硬件冷钱包。其他地方还是使用 MPC 钱包。

**2. 找靠谱的钱包供应商**：

另外一点需要注意的是，我们的热钱包安全问题其实都依赖于我们使用的钱包供应商。因此随便找一家不靠谱的钱包供应商，就算它们使用的是 MPC 钱包，也会有极大的安全风险。因此使用一个靠谱的安全供应商来存储私钥是非常重要的。

至于具体的钱包供应商我就不说具体的名字了，否则有打广告嫌疑。

## 总结

本文介绍了 MPC 钱包的原理、实现原理，以及如何创建和使用。MPC 钱包和多签钱包都可以增强区块链钱包的安全性，但 MPC 钱包更加复杂，需要更高的计算能力和通信能力。

一句话来总结以太坊的多签机制：


> 多签本质是智能合约，即一段代码，代码的逻辑是：转发签名请求到 N 个参与方，收到至少 M 个合法签名后，才自动执行真正的签名动作。

一句话来总结 MPC 的原理：

> MPC 依赖秘密共享，通过数学协议计算部分签名，然后合并签名来完成交易。普通用户保存一份私钥，平台和云保存部分私钥。避免了“单点问题”，即用户私钥被泄露后财产损失，极大地提高了安全性。

最后，希望大家能从本文中学到更多有关区块链技术的知识，并在实际应用中运用到自己的钱包。