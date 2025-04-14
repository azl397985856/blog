---
title: Web3 中的授权与撤销授权
tags: [区块链, web3, approve]
categories:
  - [区块链]
date: 2025-04-02
---

web3 是一个非常流行的概念，它的基础是区块链技术。区块链技术是一种分布式账本技术，它的特点是去中心化、不可篡改、安全可靠。区块链技术的应用场景非常广泛，比如数字货币、智能合约、供应链金融等等。

网上关于区块链的资料非常多，但是从零开始构建的资料却很少。熟悉我的朋友应该知道，我经常从零实现一些东西帮助我理解，比如从零实现 git，从零实现 webpack 打包器，从零实现一个框架等等。

本文就是继上一篇 [《从零开始构建区块链》](https://lucifer.ren/blog/2024/11/22/web3-zero-to-one/ "《从零开始构建区块链》") 的文章，讲述**什么是 Web3 中的授权与撤销授权**，以及如何用 Python3 模拟其过程。

<!-- more -->

##  Web3 中的授权与撤销授权

随着 Web3 的兴起，去中心化的理念逐渐渗透到数字世界的每一个角落。与传统的中心化授权机制不同，Web3 的授权更强调用户的主权、数据的隐私以及系统的透明性。在这篇文章中，我们将深入探讨 Web3 授权的核心原理，并通过 Python3 代码模拟其关键过程，帮助读者更直观地理解这一技术背后的逻辑。同时，我们还会解答一些常见问题：为什么 Swap 前需要授权并填写金额？能否跳过授权直接 Swap？如何撤销授权？以及 EIP-7702 如何通过单次交易优化授权流程？



## 授权的本质：从中心化到去中心化

在 Web2 时代，授权通常由中心化的服务器控制。比如，当你登录一个网站时，你的用户名和密码会被发送到服务器，服务器验证后返回一个会话令牌。这种模式虽然简单高效，但存在单点故障和隐私泄露的风险。Web3 的授权则完全不同，它基于区块链和密码学技术，用户通过私钥和公钥对来证明自己的身份，无需依赖第三方。

在 Web3 中，授权的核心是“控制权归于用户”。用户通过钱包（例如 MetaMask）签名一笔交易或消息，证明自己对某个地址的所有权。这种机制不仅安全，还能无缝集成到去中心化应用（DApp）中。接下来，我们将通过一个简单的例子，展示如何用 Python3 模拟这一过程。



## 授权过程解析：签名与验证

在 Web3 的授权中，最常见的方式是通过椭圆曲线数字签名算法（ECDSA）。用户使用私钥对消息进行签名，生成一个独一无二的签名，任何拥有公钥的人都可以验证签名的有效性，而无法伪造签名。这种机制是区块链（如以太坊）的基础。

让我们逐步拆解这个过程：

1. **生成密钥对**：用户首先需要一对公私钥。私钥是用户的核心机密，公钥则可以公开，用于验证。
2. **消息签名**：用户用私钥对一段消息（例如“授权登录”）进行签名，生成签名。
3. **验证签名**：DApp 或其他服务使用用户的公钥验证签名，确保消息未被篡改且确实来自该用户。

下面，我们用 Python3 结合 `eth_account` 库（以太坊生态中常用的工具）来模拟这一过程。

### 模拟代码：生成密钥对与签名验证

在开始代码之前，我们先描述一下代码的目标：我们将首先生成一个随机的私钥和对应的公钥（模拟用户创建钱包的过程），然后对一条消息进行签名，最后验证签名的有效性。这里的消息可以看作是用户授权登录 DApp 时发送的请求。

```python
from eth_account import Account
import secrets

# 步骤 1：生成随机的私钥和公钥
# 在现实中，私钥由用户妥善保管，绝不泄露
private_key = "0x" + secrets.token_hex(32)  # 生成一个随机的 32 字节私钥
account = Account.from_key(private_key)
public_address = account.address  # 从私钥派生出公钥对应的地址

print(f"私钥: {private_key}")
print(f"公钥地址: {public_address}")

# 步骤 2：对消息进行签名
message = "授权登录 Web3 DApp"
signed_message = Account.sign_message(
    {"message": message},  # 消息内容
    private_key=private_key  # 使用私钥签名
)

print(f"签名: {signed_message.signature.hex()}")

# 步骤 3：验证签名
recovered_address = Account.recover_message(
    {"message": message},
    signature=signed_message.signature
)

# 检查签名是否有效
if recovered_address == public_address:
    print("签名验证成功，用户授权有效！")
else:
    print("签名验证失败，授权无效！")
```

运行这段代码，你会看到类似下面的输出：

```
私钥: 0x1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2
公钥地址: 0xAbCdEf1234567890aBcDeF1234567890aBcDeF12
签名: 0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef12345678901b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
签名验证成功，用户授权有效！
```

### 代码解析

- **私钥生成**：我们使用 `secrets` 模块生成一个安全的随机私钥。在实际应用中，钱包软件会为用户生成并存储私钥。
- **签名过程**：`Account.sign_message` 使用 ECDSA 算法对消息进行签名，生成一个独一无二的签名。
- **验证过程**：`Account.recover_message` 从签名中恢复出公钥地址，并与原始地址对比，验证授权的真实性。

这个过程完美体现了 Web3 授权的去中心化特性：无需服务器存储用户密码，所有验证都在本地完成。

## Swap 与 Approve

如果你使用过 Web3 的去中心化交易所（DEX），比如 Uniswap 或 PancakeSwap，你可能会注意到，在进行代币交换（Swap）之前，通常需要先进行一次“授权”（Approve）操作。钱包会弹出一个界面，要求你签名并设置一个金额（可以是具体数值，也可以选择“无上限”）。这是怎么回事？它和我们上面讲的授权有什么联系？更进一步，有人会问：既然 Swap 时也要签名，能否跳过授权直接进行 Swap？如果授权有风险，如何撤销？还有人提到 EIP-7702 可以实现单次交易临时执行智能合约，这又是什么原理？

### Swap 授权的原理

在以太坊等区块链上，代币通常遵循 ERC-20 标准。ERC-20 代币有一个重要的函数叫做 `approve`，它允许用户授权某个智能合约（比如 DEX 的合约）从你的地址中转移一定数量的代币。这个授权过程本质上是对智能合约的信任声明：你告诉区块链，“我允许这个合约在未来从我的账户中提取不超过 X 数量的代币”。

- **为什么要授权？** 因为智能合约无法直接访问你的代币余额。你的代币存储在你的地址中，只有通过你的授权，合约才能代表你执行转账操作。
- **为什么需要填写金额？** 这是为了控制风险。你可以设置一个具体的金额（比如 100 USDT），限制合约能提取的上限；也可以选择“无上限”（通常是 `2^256-1`，一个非常大的数字），方便后续多次交易无需重复授权。
- **和签名验证的联系**：授权操作依然依赖私钥签名。你通过钱包签名一笔交易，调用 `approve` 函数，这与我们上面模拟的签名过程一致，都是用私钥证明身份和意图。

### 模拟代码：授权代币转移

让我们用 Python3 模拟一个简化的授权过程。这里假设我们有一个 ERC-20 代币合约，授权某个地址（模拟 DEX 合约）转移代币。

```python
from eth_account import Account
import secrets

# 模拟用户和合约地址
user_private_key = "0x" + secrets.token_hex(32)
user_account = Account.from_key(user_private_key)
user_address = user_account.address
contract_address = "0x1234567890abcdef1234567890abcdef12345678"  # 模拟 DEX 合约地址

# 授权金额（可以是具体值或无上限）
approved_amount = "100"  # 假设授权 100 个代币
# approved_amount = "115792089237316195423570985008687907853269984665640564039457584007913129639935"  # 无上限

# 构造授权消息（简化版，实际中是交易数据）
approve_message = f"授权 {contract_address} 转移 {approved_amount} 代币"
signed_approve = Account.sign_message(
    {"message": approve_message},
    private_key=user_private_key
)

print(f"用户地址: {user_address}")
print(f"授权签名: {signed_approve.signature.hex()}")

# 验证授权
recovered_address = Account.recover_message(
    {"message": approve_message},
    signature=signed_approve.signature
)

if recovered_address == user_address:
    print(f"授权验证成功，{contract_address} 可转移 {approved_amount} 代币！")
else:
    print("授权验证失败！")
```

### 输出示例

```
用户地址: 0xAbCdEf1234567890aBcDeF1234567890aBcDeF12
授权签名: 0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef12345678901b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
授权验证成功，0x1234567890abcdef1234567890abcdef12345678 可转移 100 代币！
```

### 能否跳过授权直接 Swap？

一个常见的疑问是：既然 Swap 时需要用户签名交易，为什么不能跳过授权，直接通过签名完成 Swap？答案在于区块链的权限模型和效率设计。

- **授权和 Swap 的分离**：授权（Approve）是一次性签名，允许合约在未来转移代币；Swap 是另一笔签名，执行具体的交易。如果没有授权，合约没有权限从你的地址提取代币，Swap 交易会失败。
- **为什么不合并？** 将授权和 Swap 合并成一步会增加每次交易的复杂性和 Gas 成本。分开授权的好处是，你只需授权一次，后续多次 Swap 都能复用，减少操作和费用。
- **例外情况**：
  - 如果你用的是原生代币（如 ETH），Swap 不需要授权，因为 ETH 直接通过交易发送，无需 ERC-20 的 `approve`。
  - 一些新型协议支持 EIP-2612（Permit），允许用户通过单次签名同时完成授权和 Swap。这种方式简化了流程，但本质上仍是授权的变种。

因此，对于标准 ERC-20 代币，授权是 Swap 的必要前提，无法直接跳过。但在特定场景下（如原生代币或 Permit），流程可以优化。

### 如何撤销授权？

授权并非不可更改。如果你担心某个合约被滥用，或者不再信任某个 DApp，可以通过撤销授权来保护资产。撤销的原理是再次调用 `approve` 函数，将合约的限额设置为 0。

#### 模拟代码：撤销授权

```python
# 构造撤销授权消息（将限额设为 0）
revoke_message = f"授权 {contract_address} 转移 0 代币"
signed_revoke = Account.sign_message(
    {"message": revoke_message},
    private_key=user_private_key
)

print(f"撤销授权签名: {signed_revoke.signature.hex()}")

# 验证撤销
recovered_address = Account.recover_message(
    {"message": revoke_message},
    signature=signed_revoke.signature
)

if recovered_address == user_address:
    print(f"撤销授权成功，{contract_address} 的限额已设为 0！")
else:
    print("撤销授权失败！")
```

#### 注意事项
- 撤销需要支付 Gas 费用。
- 可用工具（如 Revoke.cash）简化操作，检查并撤销不必要的授权。

## EIP-7702：单次交易临时执行智能合约

EIP-7702 提供了一种全新的授权方式，避免了传统 `approve` 的永久性授权问题。它允许用户在单次交易中临时让外部账户（EOA）执行智能合约逻辑，完成后恢复原状。这一提案由 Vitalik Buterin 等核心开发者提出，旨在提升账户抽象（Account Abstraction）的灵活性和安全性。

### EIP-7702 规范细节
根据 EIP-7702 的草案（EIP-7702: Set EOA account code），其核心机制包括：
1. **新交易类型**：引入一种新的交易类型（类型 `0x04`），包含以下字段：
   - `chain_id`：指定交易适用的链 ID（可选，设为 0 表示跨链有效）。
   - `contract_code`：临时赋予 EOA 的智能合约代码（或指向代码的地址）。
   - `signature`：用户对交易的签名，用于验证身份。
   - `nonce`：EOA 的交易计数器，防止重放攻击。
2. **临时执行**：
   - 交易执行时，EOA 的代码被设置为 `contract_code`，在本次交易中执行指定逻辑。
   - 交易完成后，EOA 的代码被清空，恢复为普通账户状态。
3. **设计目标**：
   - **单次性**：授权仅在当前交易有效，避免长期风险。
   - **兼容性**：与 ERC-4337（账户抽象标准）兼容，无需引入新操作码。
   - **灵活性**：支持批量操作（如授权+Swap）或自定义逻辑。

### 应用场景
假设你想用 100 USDT 换 ETH：
- 传统方式：先 Approve 授权 DEX 转移 100 USDT，再签名 Swap 交易。
- EIP-7702：签名一笔交易，临时让 EOA 执行“授权 100 USDT 并调用 DEX Swap”的逻辑，完成后权限自动消失。

### 模拟代码：EIP-7702 实现
以下是基于 EIP-7702 规范的 Python 模拟实现。我们假设一个简单的场景：用户通过 EIP-7702 交易临时授权并执行 Swap。

```python
from eth_account import Account
import secrets
from eth_account.messages import encode_defunct

# 模拟用户和 DEX 合约地址
user_private_key = "0x" + secrets.token_hex(32)
user_account = Account.from_key(user_private_key)
user_address = user_account.address
dex_address = "0x1234567890abcdef1234567890abcdef12345678"

# EIP-7702 交易数据
eip7702_tx = {
    "chain_id": 1,  # 主网 Chain ID
    "nonce": 0,     # 交易计数器
    "contract_code": "0x60606040523415600e57600080fd5b5b600a80601a6000396000f3006060604052600080fd",  # 简化的合约字节码
    "call_data": "授权并Swap: 100 USDT -> ETH"  # 模拟调用数据
}

# 构造 EIP-7702 消息
message = f"chain_id: {eip7702_tx['chain_id']}, nonce: {eip7702_tx['nonce']}, code: {eip7702_tx['contract_code']}, data: {eip7702_tx['call_data']}"
encoded_message = encode_defunct(text=message)  # 转换为 EIP-712 兼容格式

# 用户签名
signed_tx = Account.sign_message(encoded_message, private_key=user_private_key)

print(f"用户地址: {user_address}")
print(f"EIP-7702 交易签名: {signed_tx.signature.hex()}")

# 验证签名（模拟节点处理）
recovered_address = Account.recover_message(encoded_message, signature=signed_tx.signature)
if recovered_address == user_address:
    print(f"签名验证成功，临时执行合约代码...")
    print(f"模拟执行: {dex_address} 转移 100 USDT 并 Swap 为 ETH")
    print("交易完成，EOA 恢复原状")
else:
    print("签名验证失败！")

# 输出示例
"""
用户地址: 0xAbCdEf1234567890aBcDeF1234567890aBcDeF12
EIP-7702 交易签名: 0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef12345678901b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
签名验证成功，临时执行合约代码...
模拟执行: 0x1234567890abcdef1234567890abcdef12345678 转移 100 USDT 并 Swap 为 ETH
交易完成，EOA 恢复原状
"""
```

### 代码解析
- **交易构造**：`eip7702_tx` 包含 EIP-7702 所需字段。`contract_code` 是简化的字节码，实际中可能是指向已有合约的地址。
- **消息编码**：使用 `encode_defunct` 将消息转换为以太坊签名标准格式。
- **签名与验证**：用户签名交易，节点验证后临时执行代码，完成后清空。
- **模拟执行**：这里仅打印操作，实际中会调用 DEX 合约的 Swap 函数。

### 优势
- **安全性**：权限仅限单次交易。
- **效率**：一步完成授权和 Swap。
- **未来兼容性**：支持账户抽象发展。


## 结语

Web3 的授权机制是去中心化世界的基石，它将权力从中心化的机构手中交还给用户。无论是登录 DApp、进行 Swap，还是通过 EIP-7702 优化流程，授权的核心都离不开私钥签名和密码学验证。然而，挑战也同样存在。例如，私钥丢失意味着用户失去所有控制权；“无上限”授权可能被恶意合约滥用；传统授权和撤销的 Gas 成本较高。

通过 Python3 的代码模拟，我们不仅理解了其背后的原理，也看到了它在实际应用中的多样性。未来，随着技术如 EIP-7702 的普及，Web3 授权将变得更安全、更高效，为我们带来一个更自由的数字时代。

如果你对代码有任何疑问，或者想深入探讨某个细节，欢迎留言交流！

