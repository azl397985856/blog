---
title: 一个简单的 web3 应用
tags: [区块链, web3, approve]
categories:
  - [区块链]
date: 2025-05-11
---

在传统的 Web2 开发中，开发者通常会选择 MySQL、MongoDB 或 Firebase 这样的数据库来存储用户数据。而随着区块链技术和 Web3 的兴起，我们可以直接将区块链作为数据库来使用，省去中心化服务器的麻烦，同时赋予用户数据主权。这篇文章将带你探索如何用 Web3 实现一个去中心化的数据存储方案，并通过 Python3 代码模拟关键流程。

<!-- more -->

区块链本质上是一个分布式账本，数据以不可篡改的方式存储在链上，且通过智能合约可以实现灵活的数据操作。相比传统数据库，Web3 数据库的优势包括：

- **去中心化**：没有单点故障，数据由网络节点共同维护。
- **数据透明性**：链上数据公开可查，适合需要高信任的场景。
- **用户控制**：通过加密签名，用户可以完全掌控自己的数据。
- **无需后端**：智能合约替代了传统后端逻辑，简化开发流程。

当然，Web3 数据库也有局限性，比如存储成本较高（链上 Gas 费用）、查询效率较低等。但对于某些场景，比如用户身份管理、资产记录或去中心化社交，这些劣势可以被其独特优势抵消。

接下来，我们将通过一个简单的例子，展示如何用 Python 和 Web3 技术将区块链（以太坊为例）作为数据库，存储和查询用户数据。

## 准备工作：搭建 Web3 环境

要将区块链作为数据库，我们需要以下工具：

1. **以太坊节点**：可以通过 Infura 或 Alchemy 提供的 RPC 节点访问以太坊网络。
2. **智能合约**：编写一个简单的 Solidity 合约，用于存储和查询数据。
3. **Web3.py**：Python 的 Web3 库，用于与区块链交互。
4. **MetaMask 或私钥**：用于签名交易。

我们假设你已经安装了 Python3 和 `web3.py`（可以通过 `pip install web3` 安装）。下面，我们将逐步实现一个用户数据存储的案例。

## 步骤 1：编写智能合约

首先，我们需要一个智能合约来定义数据存储的逻辑。以下是一个简单的 Solidity 合约，允许用户存储和查询自己的数据（比如用户名和个人简介）。

### 合约逻辑说明

合约的核心功能包括：
- 每个用户（以以太坊地址标识）可以存储一组数据（用户名和简介）。
- 用户可以通过地址查询自己的数据。
- 数据存储在链上，公开可查。

以下是 Solidity 合约代码：

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UserDatabase {
    struct User {
        string username;
        string bio;
    }

    mapping(address => User) public users;

    function setUser(string memory _username, string memory _bio) public {
        users[msg.sender] = User(_username, _bio);
    }

    function getUser(address _userAddress) public view returns (string memory, string memory) {
        User memory user = users[_userAddress];
        return (user.username, user.bio);
    }
}
```

我们将这个合约部署到以太坊测试网（比如 Sepolia）上，并获取合约地址和 ABI（Application Binary Interface）。这些信息将用于 Python 代码与合约交互。

## 步骤 2：用 Python 连接区块链

在 Python 中，我们使用 `web3.py` 库来与以太坊网络交互。以下是连接区块链并调用智能合约的流程：

### 连接流程说明

1. **初始化 Web3 实例**：通过 Infura 或 Alchemy 的 RPC URL 连接到以太坊节点。
2. **加载合约**：使用合约地址和 ABI 初始化合约实例。
3. **准备账户**：通过私钥加载用户账户，用于签名交易。
4. **调用合约方法**：通过 `web3.py` 调用 `setUser` 和 `getUser` 方法。

以下是实现代码：

```python
from web3 import Web3
import json

# 连接到以太坊测试网（Sepolia）
rpc_url = "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"
w3 = Web3(Web3.HTTPProvider(rpc_url))

# 确认连接
if not w3.is_connected():
    raise Exception("Failed to connect to Ethereum node")

# 合约地址和 ABI（从部署后的合约获取）
contract_address = "0xYOUR_CONTRACT_ADDRESS"
with open("UserDatabase.json") as f:
    contract_abi = json.load(f)

# 初始化合约
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# 用户账户和私钥
user_address = "0xYOUR_USER_ADDRESS"
private_key = "YOUR_PRIVATE_KEY"

# 设置用户数据
def set_user_data(username, bio):
    nonce = w3.eth.get_transaction_count(user_address)
    txn = contract.functions.setUser(username, bio).build_transaction({
        "from": user_address,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("50", "gwei")
    })
    
    signed_txn = w3.eth.account.sign_transaction(txn, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    return receipt

# 查询用户数据
def get_user_data(user_address):
    username, bio = contract.functions.getUser(user_address).call()
    return {"username": username, "bio": bio}

# 示例：存储和查询数据
if __name__ == "__main__":
    # 存储数据
    receipt = set_user_data("Lucifer", "Web3 enthusiast")
    print(f"Transaction receipt: {receipt.transactionHash.hex()}")

    # 查询数据
    data = get_user_data(user_address)
    print(f"User data: {data}")
```

### 代码解析

- **连接节点**：通过 `Web3.HTTPProvider` 连接到 Sepolia 测试网的 Infura 节点。
- **合约交互**：通过 `contract.functions` 调用 `setUser`（需要签名交易）和 `getUser`（只读调用）。
- **交易签名**：使用用户私钥签名交易，并通过 `send_raw_transaction` 发送到网络。
- **Gas 参数**：手动设置 `gas` 和 `gasPrice` 以确保交易成功。

运行这段代码后，你可以将数据存储到链上，并通过用户地址查询数据。链上的数据是公开的，任何人都可以通过合约的 `getUser` 方法查看。

## 步骤 3：优化和扩展

上述例子是一个最简化的实现，实际应用中可以做以下优化：

- **数据加密**：如果数据需要隐私保护，可以在客户端加密后再上链，链上只存储加密后的密文。
- **事件日志**：在合约中添加事件（`event`），记录每次数据更新的日志，便于前端监听。
- **批量操作**：支持批量存储或查询，减少 Gas 消耗。
- **IPFS 集成**：将大块数据存储到 IPFS，链上只存储哈希，降低成本。

以下是一个简单的加密存储示例：

### 加密存储说明

我们使用 Python 的 `cryptography` 库对数据进行加密，然后将密文存储到链上。查询时，使用相同的密钥解密。

```python
from cryptography.fernet import Fernet

# 生成加密密钥
key = Fernet.generate_key()
cipher = Fernet(key)

# 加密数据
def encrypt_data(data):
    return cipher.encrypt(data.encode()).decode()

# 解密数据
def decrypt_data(encrypted_data):
    return cipher.decrypt(encrypted_data.encode()).decode()

# 示例：加密存储
username = encrypt_data("Lucifer")
bio = encrypt_data("Web3 enthusiast")
receipt = set_user_data(username, bio)
print(f"Encrypted data stored: {receipt.transactionHash.hex()}")

# 示例：查询并解密
data = get_user_data(user_address)
decrypted_username = decrypt_data(data["username"])
decrypted_bio = decrypt_data(data["bio"])
print(f"Decrypted data: {decrypted_username}, {decrypted_bio}")
```

### 代码解析

- **加密**：使用 `Fernet`（对称加密）对数据加密，生成密文。
- **存储**：将密文存储到链上，确保链上数据不可读。
- **解密**：客户端使用相同的密钥解密，恢复原始数据。

这种方式适合需要隐私保护的场景，比如存储用户敏感信息。

## 注意事项

1. **Gas 费用**：链上存储需要支付 Gas，建议优化数据结构，减少上链操作。
2. **查询效率**：链上查询速度较慢，适合低频操作。如果需要高频查询，可以结合 The Graph 等索引协议。
3. **安全性**：私钥必须妥善保存，避免泄露。智能合约需经过审计，避免漏洞。
4. **测试网优先**：开发时使用 Sepolia 或 Goerli 测试网，避免主网的高成本。

## 总结

通过将 Web3 作为数据库，我们可以构建完全去中心化的应用，赋予用户对数据的控制权，同时省去传统后端服务器的维护成本。本文通过一个简单的用户数据存储案例，展示了如何用 Python 和 Web3.py 与以太坊交互，并介绍了加密存储的优化方案。

Web3 的潜力远不止于此。你可以将区块链与 IPFS、The Graph 或 Layer2 方案结合，构建更高效、低成本的去中心化应用。赶快动手试试，把 Web3 当成你的数据库，开启去中心化开发的旅程吧！


