---
title: 从零开始构建区块链
tags: [区块链, web3]
categories:
  - [区块链]
date: 2024-11-22
---

web3 是一个非常流行的概念，它的基础是区块链技术。区块链技术是一种分布式账本技术，它的特点是去中心化、不可篡改、安全可靠。区块链技术的应用场景非常广泛，比如数字货币、智能合约、供应链金融等等。

网上关于区块链的资料非常多，但是从零开始构建的资料却很少。熟悉我的朋友应该知道，我经常从零实现一些东西帮助我理解，比如从零实现 git，从零实现 webpack 打包器，从零实现一个框架等等。

本文就是一篇从零开始构建区块链的文章，希望能帮助你快速入门区块链技术。

<!-- more -->

## 前言

由于本文不是科普文章，而是直接带你实现，从而加深理解，因此建议你对区块链技术有一定的了解。如果你对区块链技术还不了解，可以先看一些区块链的基础知识，比如区块链的概念、区块链的特点、区块链的应用等等。比如 [learn_blockchain](https://github.com/chaseSpace/learn_blockchain "learn_blockchain") 就是一个还不错的入门资料集合页。

本文使用 Python 语言来实现区块链，Python 是一种非常流行的编程语言，它的语法简单，非常适合初学者。如果你对 Python 不熟悉也没关系，相信我他真的很容易懂。如果你实在不懂，也可以让 chatgpt 给你解释甚至直接翻译为其他语言。

## 学习建议

为了方便大家直接运行，我提供了相对完整的代码示例。强烈大家边看看在本地跟着一起写，一起运行查看效果，只有动手才可能真正理解其核心。并且尽可能地根据我的思路和代码默写，而不是抄写一遍。

## 基础

我们可以实现一个简单的区块链类来模拟区块链的基本功能。

从数据结构上来说，区块链本质上是一个链表结构，每个区块包含一个索引、时间戳、数据、前一个区块的哈希值和当前区块的哈希值。区块链中的第一个区块叫做创世区块，它的前一个区块的哈希值是 0。

首先我们先定义几个类，分别是 `Block` 类和 `Blockchain` 类。其中 `Block` 类表示区块，`Blockchain` 类表示区块链。 `Blockchain` 会引用 `Block` 类。

- Block 类：包含索引、时间戳、数据、前一个区块的哈希值和当前区块的哈希值。

- Blockchain 类： 包含一个区块链列表，初始化时创建创世区块，支持新块的方法。

关于哈希计算，可以使用 SHA-256 算法，算法细节不是本文的重点，你可以直接使用 Python 的 hashlib 库来计算。

```py
import hashlib
import time

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        sha.update(f"{self.index}{self.timestamp}{self.data}{self.previous_hash}".encode('utf-8'))
        return sha.hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, time.time(), "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

# 使用示例
blockchain = Blockchain()
blockchain.add_block(Block(1, time.time(), "Block 1 Data", blockchain.get_latest_block().hash))
blockchain.add_block(Block(2, time.time(), "Block 2 Data", blockchain.get_latest_block().hash))

# 打印区块链
for block in blockchain.chain:
    print(f"Index: {block.index}")
    print(f"Timestamp: {block.timestamp}")
    print(f"Data: {block.data}")
    print(f"Previous Hash: {block.previous_hash}")
```

## 交易与挖矿

另一个重要的基础概念就是交易（Transaction）。交易本质上是一种数据结构，包含发送者、接收者和金额等用来描述交易的信息即可。交易是区块链中的基本单位，区块链中的每个区块都包含一系列交易。

区块链中的挖矿是另外一个非常重要的概念，挖矿的过程是通过计算一个符合条件的哈希值来创建新的区块。挖矿的过程是一个计算密集型的过程，需要大量的计算资源。

为什么把两个放在一起？ 因为我觉得可以将**挖矿看作是一种特殊的交易**，这种交易是没有发送者的，只有接收者，接收者就是矿工，矿工通过挖矿来获得奖励。

为了在区块链中添加挖矿和转账功能，我们需要进行以下步骤：

1. 定义交易类：包含发送者、接收者和金额。

定义 Transaction 类：包含发送者、接收者和金额。

```py
class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
```

2. 修改区块类：包含交易列表和挖矿奖励。

修改 Block 类：计算哈希值时包含交易信息（前面计算哈希的时候没有对交易信息进行哈希，因此前面还没有交易信息）。

```py
class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.transactions = transactions
        # ...

    def calculate_hash(self):
        sha = hashlib.sha256()
        transactions_str = "".join([f"{tx.sender}{tx.receiver}{tx.amount}" for tx in self.transactions])
        sha.update(f"{self.index}{self.timestamp}{transactions_str}{self.previous_hash}".encode('utf-8'))
        return sha.hexdigest()
```

3. 修改区块链类：添加挖矿和创建交易的方法。

由于挖矿就是没有发送者的交易，因此创建一个没有 sender 的交易，并将其加入到区块的交易列表中即可。

简单起见，我们一个区块只包含一个交易。因此我们在挖矿后，直接创建一个新的区块，并将交易添加到区块中。

```py
def mine_pending_transactions(self, mining_reward_address):
    # 可以看到 sender 是 None，receiver 是矿工地址，amount 是挖矿奖励
    reward_tx = Transaction(None, mining_reward_address, self.mining_reward) # 创建一个没有 sender 的交易
    self.pending_transactions.append(reward_tx) # 将其加入到区块的交易列表中
    new_block = Block(len(self.chain), time.time(), self.pending_transactions, self.get_latest_block().hash)
    new_block.hash = new_block.calculate_hash()
    self.chain.append(new_block)
    self.pending_transactions = []
```

以下为完整代码：

```py
import hashlib
import time

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        transactions_str = "".join([f"{tx.sender}{tx.receiver}{tx.amount}" for tx in self.transactions])
        sha.update(f"{self.index}{self.timestamp}{transactions_str}{self.previous_hash}".encode('utf-8'))
        return sha.hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.mining_reward = 100

    def create_genesis_block(self):
        return Block(0, time.time(), [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def mine_pending_transactions(self, mining_reward_address):
        reward_tx = Transaction(None, mining_reward_address, self.mining_reward)
        self.pending_transactions.append(reward_tx)
        new_block = Block(len(self.chain), time.time(), self.pending_transactions, self.get_latest_block().hash)
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)
        self.pending_transactions = []

    def create_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.receiver == address:
                    balance += tx.amount
        return balance

# 使用示例
blockchain = Blockchain()

# 创建一些交易
blockchain.create_transaction(Transaction("Alice", "Bob", 50))
blockchain.create_transaction(Transaction("Bob", "Alice", 30))

# 挖矿
blockchain.mine_pending_transactions("Miner1")

# 打印区块链
for block in blockchain.chain:
    print(f"Index: {block.index}")
    print(f"Timestamp: {block.timestamp}")
    print(f"Transactions: {[{'sender': tx.sender, 'receiver': tx.receiver, 'amount': tx.amount} for tx in block.transactions]}")
    print(f"Previous Hash: {block.previous_hash}")
    print(f"Hash: {block.hash}")
    print()

# 打印余额
print(f"Balance of Miner1: {blockchain.get_balance('Miner1')}")
print(f"Balance of Alice: {blockchain.get_balance('Alice')}")
print(f"Balance of Bob: {blockchain.get_balance('Bob')}")
```

## 谁能挖矿成功？

在区块链中，挖矿是一个竞争的过程，只有第一个找到符合条件的哈希值的矿工才能获得奖励。这个过程是一个随机的过程，因此只能通过不断尝试来找到符合条件的哈希值。

决定谁可以挖矿成功的算法有很多种，比如工作量证明（Proof of Work）、权益证明（Proof of Stake）等等。其中工作量证明是最常见的一种算法，比特币就是使用工作量证明算法来决定谁可以挖矿成功。

这里我们实现一下工作量证明算法（POW）。工作量证明算法的核心思想是找到一个符合条件的哈希值，这个哈希值的前几位是 0。这个条件是可以调整的，比如前两位是 0，前三位是 0 等等。位数越多，实现起来越困难。我们可以将这个位数称为难度（Difficulty）。如果被哈希的字符串是固定的，那么哈希值一定也是固定的，因此被哈希的字符串不能是固定的（否则可能无法找到符合条件的哈希值），通常的做法是包含一个随机数 nonce，这个随机数就是我们需要不断尝试的值。

也就是说没有这个约束，我们很快就能计算出哈希，这个哈希有可能也不满足 difficult 条件，但是有了这个约束，我们就需要不断尝试，直到找到符合条件的哈希值。

为了实现这个目的，我们需要：

- 修改 Block 类：添加 nonce 属性和 proof_of_work 方法。

```py
def proof_of_work(self, difficulty):
    self.nonce = 0
    computed_hash = self.calculate_hash()
    while not computed_hash.startswith('0' * difficulty):
        self.nonce += 1
        computed_hash = self.calculate_hash()
    return computed_hash
```

- 修改 Blockchain 类：在挖矿时调用 proof_of_work 方法。

```py
import hashlib
import time

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        transactions_str = "".join([f"{tx.sender}{tx.receiver}{tx.amount}" for tx in self.transactions])
        sha.update(f"{self.index}{self.timestamp}{transactions_str}{self.previous_hash}{self.nonce}".encode('utf-8'))
        return sha.hexdigest()

    def proof_of_work(self, difficulty):
        self.nonce = 0
        computed_hash = self.calculate_hash()
        while not computed_hash.startswith('0' * difficulty):
            self.nonce += 1
            computed_hash = self.calculate_hash()
        return computed_hash

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.mining_reward = 100
        self.difficulty = 4

    def create_genesis_block(self):
        return Block(0, time.time(), [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def mine_pending_transactions(self, mining_reward_address):
        reward_tx = Transaction(None, mining_reward_address, self.mining_reward)
        self.pending_transactions.append(reward_tx)
        new_block = Block(len(self.chain), time.time(), self.pending_transactions, self.get_latest_block().hash)
        # 注意这里调用的是 proof_of_work 方法
        new_block.hash = new_block.proof_of_work(self.difficulty)
        self.chain.append(new_block)
        self.pending_transactions = []

    def create_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.receiver == address:
                    balance += tx.amount
        return balance

# 使用示例
blockchain = Blockchain()

# 创建一些交易
blockchain.create_transaction(Transaction("Alice", "Bob", 50))
blockchain.create_transaction(Transaction("Bob", "Alice", 30))

# 挖矿
blockchain.mine_pending_transactions("Miner1")

# 打印区块链
for block in blockchain.chain:
    print(f"Index: {block.index}")
    print(f"Timestamp: {block.timestamp}")
    print(f"Transactions: {[{'sender': tx.sender, 'receiver': tx.receiver, 'amount': tx.amount} for tx in block.transactions]}")
    print(f"Previous Hash: {block.previous_hash}")
    print(f"Hash: {block.hash}")
    print(f"Nonce: {block.nonce}")
    print()

# 打印余额
print(f"Balance of Miner1: {blockchain.get_balance('Miner1')}")
print(f"Balance of Alice: {blockchain.get_balance('Alice')}")
print(f"Balance of Bob: {blockchain.get_balance('Bob')}")
```

## 智能合约

智能合约是区块链中的另一个重要概念，它是一种自动执行的合约，不需要中间人，不需要信任。智能合约是区块链中的一种应用，它可以实现一些自动化的业务逻辑，比如数字货币、供应链金融等等。

本质上，智能合约是一段代码，这段代码会被部署到区块链上，然后通过交易来调用这段代码。智能合约的代码是不可篡改的，一旦部署到区块链上，就无法修改。

智能合约的本体就是代码，本质类似于状态机。

智能合约还有一个很重要的概念是 ABI。ABI（Application Binary Interface，应用二进制接口）是智能合约与外部应用程序之间的接口定义。它描述了智能合约的函数和事件，使得外部应用程序可以与智能合约进行交互。


智能合约代码是用 Solidity 等编程语言编写的，定义了合约的逻辑和功能。合约代码通常需要编译，在编译后会生成字节码（bytecode），部署到区块链上。

ABI 是合约编译后生成的 JSON 文件，描述了合约的接口。它不包含合约的逻辑实现，只包含函数和事件的定义。外部应用程序使用 ABI 来与部署在区块链上的合约进行交互。

也就是说 ABI 决定了如何调用合约，而合约代码决定了合约的逻辑。

为了在区块链中添加智能合约功能，我们需要进行以下步骤：

1. 定义智能合约类：创建一个 SmartContract 类，用于定义智能合约的基本结构和功能。

```py
class SmartContract:
    def __init__(self, code):
        self.code = code
        self.state = {}

    def execute(self, sender, receiver, amount):
        exec(self.code, {'sender': sender, 'receiver': receiver, 'amount': amount, 'state': self.state})
```

2. 修改 Blockchain 类：添加处理智能合约的功能。

```py
def deploy_contract(self, contract_code):
    contract = SmartContract(contract_code)
    contract_address = hashlib.sha256(contract_code.encode('utf-8')).hexdigest()
    self.contracts[contract_address] = contract
    return contract_address

def call_contract(self, contract_address, sender, receiver, amount):
    contract = self.contracts.get(contract_address)
    if contract:
        contract.execute(sender, receiver, amount)
        tx = Transaction(sender, receiver, amount, contract_address)
        self.create_transaction(tx)
```

合约有地址属性，合约的地址是合约代码的哈希值，这也说明了合约的本体就是代码本身。通常要调用合约就是指定合约地址，然后调用合约的方法，外加一些参数。本质上和调用函数是一样的。

完整代码：

```py
import hashlib
import time

class Transaction:
    def __init__(self, sender, receiver, amount, contract=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.contract = contract

class SmartContract:
    def __init__(self, code):
        self.code = code
        self.state = {}

    def execute(self, sender, receiver, amount):
        exec(self.code, {'sender': sender, 'receiver': receiver, 'amount': amount, 'state': self.state})

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        transactions_str = "".join([f"{tx.sender}{tx.receiver}{tx.amount}{tx.contract}" for tx in self.transactions])
        sha.update(f"{self.index}{self.timestamp}{transactions_str}{self.previous_hash}{self.nonce}".encode('utf-8'))
        return sha.hexdigest()

    def proof_of_work(self, difficulty):
        self.nonce = 0
        computed_hash = self.calculate_hash()
        while not computed_hash.startswith('0' * difficulty):
            self.nonce += 1
            computed_hash = self.calculate_hash()
        return computed_hash

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.mining_reward = 100
        self.difficulty = 4
        self.contracts = {}

    def create_genesis_block(self):
        return Block(0, time.time(), [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def mine_pending_transactions(self, mining_reward_address):
        reward_tx = Transaction(None, mining_reward_address, self.mining_reward)
        self.pending_transactions.append(reward_tx)
        new_block = Block(len(self.chain), time.time(), self.pending_transactions, self.get_latest_block().hash)
        new_block.hash = new_block.proof_of_work(self.difficulty)
        self.chain.append(new_block)
        self.pending_transactions = []

    def create_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def deploy_contract(self, contract_code):
        contract = SmartContract(contract_code)
        contract_address = hashlib.sha256(contract_code.encode('utf-8')).hexdigest()
        self.contracts[contract_address] = contract
        return contract_address

    def call_contract(self, contract_address, sender, receiver, amount):
        contract = self.contracts.get(contract_address)
        if contract:
            contract.execute(sender, receiver, amount)
            tx = Transaction(sender, receiver, amount, contract_address)
            self.create_transaction(tx)

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.receiver == address:
                    balance += tx.amount
        return balance

# 使用示例
blockchain = Blockchain()

# 部署智能合约
contract_code = """
if amount > 10:
    state['status'] = 'High value transaction'
else:
    state['status'] = 'Low value transaction'
"""
contract_address = blockchain.deploy_contract(contract_code)

# 调用智能合约
blockchain.call_contract(contract_address, "Alice", "Bob", 50)

# 挖矿
blockchain.mine_pending_transactions("Miner1")

# 打印区块链
for block in blockchain.chain:
    print(f"Index: {block.index}")
    print(f"Timestamp: {block.timestamp}")
    print(f"Transactions: {[{'sender': tx.sender, 'receiver': tx.receiver, 'amount': tx.amount, 'contract': tx.contract} for tx in block.transactions]}")
    print(f"Previous Hash: {block.previous_hash}")
    print(f"Hash: {block.hash}")
    print(f"Nonce: {block.nonce}")
    print()

# 打印智能合约状态
print(f"Contract State: {blockchain.contracts[contract_address].state}")

# 打印余额
print(f"Balance of Miner1: {blockchain.get_balance('Miner1')}")
print(f"Balance of Alice: {blockchain.get_balance('Alice')}")
print(f"Balance of Bob: {blockchain.get_balance('Bob')}")
```



## 验证交易

交易不全是有效的，我们需要验证交易的有效性。比如余额不足、交易重复，签名等等。


为了实现验证交易的功能，我们需要以下步骤：

1. 定义交易验证规则：确保交易的发送者有足够的余额，交易的格式正确等。

```py
def validate_transaction(self, transaction):
    if transaction.sender is None:  # Mining reward transaction
        return True
    sender_balance = self.get_balance(transaction.sender)
    if sender_balance >= transaction.amount:
        return True
    return False
```

交易上也改下，校验签名等信息：

```py
class Transaction:
    def __init__(self, sender, receiver, amount, signature=None, contract=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = signature
        self.contract = contract

    def to_dict(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'contract': self.contract
        }

    def sign_transaction(self, private_key):
        sk = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        message = str(self.to_dict()).encode('utf-8')
        self.signature = sk.sign(message).hex()

    def is_valid(self):
        if self.sender is None:  # Mining reward transaction
            return True
        if not self.signature:
            return False
        vk = VerifyingKey.from_string(bytes.fromhex(self.sender), curve=SECP256k1)
        message = str(self.to_dict()).encode('utf-8')
        try:
            return vk.verify(bytes.fromhex(self.signature), message)
        except:
            return False
```
2. 实现交易验证方法：在区块链类中添加一个方法来验证交易。
3. 在添加交易时进行验证：在创建交易时调用验证方法。

```py
import hashlib
import time
import requests
from flask import Flask, jsonify, request
from ecdsa import SigningKey, VerifyingKey, SECP256k1

class Transaction:
    def __init__(self, sender, receiver, amount, signature=None, contract=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = signature
        self.contract = contract

    def to_dict(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'contract': self.contract
        }

    def sign_transaction(self, private_key):
        sk = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        message = str(self.to_dict()).encode('utf-8')
        self.signature = sk.sign(message).hex()

    def is_valid(self):
        if self.sender is None:  # Mining reward transaction
            return True
        if not self.signature:
            return False
        vk = VerifyingKey.from_string(bytes.fromhex(self.sender), curve=SECP256k1)
        message = str(self.to_dict()).encode('utf-8')
        try:
            return vk.verify(bytes.fromhex(self.signature), message)
        except:
            return False

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        transactions_str = "".join([f"{tx.sender}{tx.receiver}{tx.amount}{tx.contract}" for tx in self.transactions])
        sha.update(f"{self.index}{self.timestamp}{transactions_str}{self.previous_hash}{self.nonce}".encode('utf-8'))
        return sha.hexdigest()

    def proof_of_work(self, difficulty):
        self.nonce = 0
        computed_hash = self.calculate_hash()
        while not computed_hash.startswith('0' * difficulty):
            self.nonce += 1
            computed_hash = self.calculate_hash()
        return computed_hash

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.mining_reward = 100
        self.difficulty = 4
        self.contracts = {}
        self.nodes = set()

    def create_genesis_block(self):
        return Block(0, time.time(), [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def mine_pending_transactions(self, mining_reward_address):
        reward_tx = Transaction(None, mining_reward_address, self.mining_reward)
        self.pending_transactions.append(reward_tx)
        new_block = Block(len(self.chain), time.time(), self.pending_transactions, self.get_latest_block().hash)
        new_block.hash = new_block.proof_of_work(self.difficulty)
        self.chain.append(new_block)
        self.pending_transactions = []
        self.broadcast_block(new_block)

    def create_transaction(self, transaction):
        if self.validate_transaction(transaction):
            self.pending_transactions.append(transaction)
            self.broadcast_transaction(transaction)
        else:
            raise ValueError("Invalid transaction")

    def validate_transaction(self, transaction):
        if transaction.sender is None:  # Mining reward transaction
            return True
        sender_balance = self.get_balance(transaction.sender)
        if sender_balance >= transaction.amount and transaction.is_valid():
            return True
        return False

    def deploy_contract(self, contract_code):
        contract = SmartContract(contract_code)
        contract_address = hashlib.sha256(contract_code.encode('utf-8')).hexdigest()
        self.contracts[contract_address] = contract
        return contract_address

    def call_contract(self, contract_address, sender, receiver, amount):
        contract = self.contracts.get(contract_address)
        if contract:
            contract.execute(sender, receiver, amount)
            tx = Transaction(sender, receiver, amount, contract_address)
            self.create_transaction(tx)

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.receiver == address:
                    balance += tx.amount
        return balance


class Node:
    def __init__(self, address):
        self.address = address
        self.blockchain = Blockchain()

```

## 如果两个矿工同时挖到了区块怎么办？

这涉及到一个共识算法，比如比特币使用的共识算法是最长链原则。

在区块链中，如果两个矿工同时挖到了区块，那么就会出现分叉的情况。这个时候需要选择一个分支作为主链，另一个分支作为孤块。选择主链的原则是选择最长的链作为主链。

至今我们的区块链都是单节点的，接下来我们要实现多节点的区块链来解决这个问题。

首先我们需要实现多节点、节点广播和节点同步的功能。为此我需要：

1. 定义节点类：创建一个 Node 类，用于表示区块链网络中的节点。

```py
class Node:
    def __init__(self, address):
        self.address = address
        self.blockchain = Blockchain()

    def connect_to_node(self, node_address):
        self.blockchain.add_node(node_address)

    def broadcast_transaction(self, transaction):
        for node in self.blockchain.nodes:
            requests.post(f"{node}/add_transaction", json=transaction.__dict__)
```

2. 修改 Blockchain 类：添加处理节点和广播的功能。

```py
    def add_node(self, address):
        self.nodes.add(address)

    def broadcast_block(self, block):
        for node in self.nodes:
            requests.post(f"{node}/add_block", json=block.__dict__)

    def sync_chain(self):
        longest_chain = None
        max_length = len(self.chain)
        for node in self.nodes:
            response = requests.get(f"{node}/chain")
            length = response.json()['length']
            chain = response.json()['chain']
            if length > max_length:
                max_length = length
                longest_chain = chain
        if longest_chain:
            self.chain = [Block(**block) for block in longest_chain]
```

3. 实现节点之间的通信：使用 HTTP 或 WebSocket 实现节点之间的通信。

```py
app = Flask(__name__)
node = Node("http://localhost:5000")

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [block.__dict__ for block in node.blockchain.chain]
    return jsonify(length=len(chain_data), chain=chain_data)

@app.route('/add_block', methods=['POST'])
def add_block():
    block_data = request.get_json()
    block = Block(**block_data)
    node.blockchain.chain.append(block)
    return "Block added", 201

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    tx_data = request.get_json()
    transaction = Transaction(**tx_data)
    node.blockchain.create_transaction(transaction)
    return "Transaction added", 201

@app.route('/mine', methods=['GET'])
def mine():
    node.blockchain.mine_pending_transactions(node.address)
    return "Mining complete", 200

if __name__ == '__main__':
    app.run(port=5000)
```

接下来，我们实现最长链原则，当两个矿工同时挖到了区块时，我们选择最长的链作为主链。

为了实现这个功能，我们先介绍下分叉如何实现。

1. 创建一个新的链：从当前链的某个区块开始创建一个新的链。
2. 添加新的区块到分叉链：在新的链上添加新的区块。
3. 切换到分叉链：在需要的时候切换到分叉链。

整个过程类似于我们 git 上切换分支。

fork_chain 方法：从当前链的某个区块开始创建一个新的链，并将其添加到 forks 列表中。

switch_to_fork 方法：切换到指定的分叉链。

Flask 路由：

- /fork 路由用于创建分叉链。
- /switch_fork 路由用于切换到指定的分叉链。

最后我们来加入最长链原则。

为了在区块链中实现最长链原则，我们需要在同步链时选择最长的链作为当前链。以下是详细步骤和代码实现：

详细步骤

1. 同步链：从所有节点获取链数据。找到最长的链。如果最长的链比当前链长，则替换当前链。
2. 广播新块：当有新块时，广播给所有节点。
3. 验证链：验证链的有效性。


- sync_chain 方法：从所有节点获取链数据，找到最长的链并替换当前链。

- is_valid_chain 方法：验证链的有效性，确保链中的每个块都有效。

Flask 路由：

- /chain 路由用于获取当前链数据。

```py
import hashlib
import time
import requests
from flask import Flask, jsonify, request
from ecdsa import SigningKey, VerifyingKey, SECP256k1

class Transaction:
    def __init__(self, sender, receiver, amount, signature=None, contract=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = signature
        self.contract = contract

    def to_dict(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'contract': self.contract
        }

    def sign_transaction(self, private_key):
        sk = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        message = str(self.to_dict()).encode('utf-8')
        self.signature = sk.sign(message).hex()

    def is_valid(self):
        if self.sender is None:  # Mining reward transaction
            return True
        if not self.signature:
            return False
        vk = VerifyingKey.from_string(bytes.fromhex(self.sender), curve=SECP256k1)
        message = str(self.to_dict()).encode('utf-8')
        try:
            return vk.verify(bytes.fromhex(self.signature), message)
        except:
            return False

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        transactions_str = "".join([f"{tx.sender}{tx.receiver}{tx.amount}{tx.contract}" for tx in self.transactions])
        sha.update(f"{self.index}{self.timestamp}{transactions_str}{self.previous_hash}{self.nonce}".encode('utf-8'))
        return sha.hexdigest()

    def proof_of_work(self, difficulty):
        self.nonce = 0
        computed_hash = self.calculate_hash()
        while not computed_hash.startswith('0' * difficulty):
            self.nonce += 1
            computed_hash = self.calculate_hash()
        return computed_hash

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.mining_reward = 100
        self.difficulty = 4
        self.contracts = {}
        self.nodes = set()
        self.forks = []

    def create_genesis_block(self):
        return Block(0, time.time(), [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def mine_pending_transactions(self, mining_reward_address):
        reward_tx = Transaction(None, mining_reward_address, self.mining_reward)
        self.pending_transactions.append(reward_tx)
        new_block = Block(len(self.chain), time.time(), self.pending_transactions, self.get_latest_block().hash)
        new_block.hash = new_block.proof_of_work(self.difficulty)
        self.chain.append(new_block)
        self.pending_transactions = []
        self.broadcast_block(new_block)

    def create_transaction(self, transaction):
        if self.validate_transaction(transaction):
            self.pending_transactions.append(transaction)
            self.broadcast_transaction(transaction)
        else:
            raise ValueError("Invalid transaction")

    def validate_transaction(self, transaction):
        if transaction.sender is None:  # Mining reward transaction
            return True
        sender_balance = self.get_balance(transaction.sender)
        if sender_balance >= transaction.amount and transaction.is_valid():
            return True
        return False

    def deploy_contract(self, contract_code):
        contract = SmartContract(contract_code)
        contract_address = hashlib.sha256(contract_code.encode('utf-8')).hexdigest()
        self.contracts[contract_address] = contract
        return contract_address

    def call_contract(self, contract_address, sender, receiver, amount):
        contract = self.contracts.get(contract_address)
        if contract:
            contract.execute(sender, receiver, amount)
            tx = Transaction(sender, receiver, amount, contract_address)
            self.create_transaction(tx)

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.receiver == address:
                    balance += tx.amount
        return balance

    def add_node(self, address):
        self.nodes.add(address)

    def broadcast_block(self, block):
        for node in self.nodes:
            requests.post(f"{node}/add_block", json=block.__dict__)

    def broadcast_transaction(self, transaction):
        for node in self.nodes:
            requests.post(f"{node}/add_transaction", json=transaction.__dict__)

    def sync_chain(self):
        longest_chain = None
        max_length = len(self.chain)
        for node in self.nodes:
            response = requests.get(f"{node}/chain")
            length = response.json()['length']
            chain = response.json()['chain']
            if length > max_length and self.is_valid_chain(chain):
                max_length = length
                longest_chain = chain
        if longest_chain:
            self.chain = [Block(**block) for block in longest_chain]

    def is_valid_chain(self, chain):
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i - 1]
            if current_block['previous_hash'] != previous_block['hash']:
                return False
            block = Block(**current_block)
            if block.hash != block.calculate_hash():
                return False
        return True

    def fork_chain(self, fork_point):
        if fork_point < 0 or fork_point >= len(self.chain):
            raise ValueError("Invalid fork point")
        forked_chain = self.chain[:fork_point + 1]
        self.forks.append(forked_chain)
        return forked_chain

    def switch_to_fork(self, fork_index):
        if fork_index < 0 or fork_index >= len(self.forks):
            raise ValueError("Invalid fork index")
        self.chain = self.forks[fork_index]

class Node:
    def __init__(self, address):
        self.address = address
        self.blockchain = Blockchain()

    def connect_to_node(self, node_address):
        self.blockchain.add_node(node_address)

    def broadcast_transaction(self, transaction):
        for node in self.blockchain.nodes:
            requests.post(f"{node}/add_transaction", json=transaction.__dict__)

app = Flask(__name__)
node = Node("http://localhost:5000")

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [block.__dict__ for block in node.blockchain.chain]
    return jsonify(length=len(chain_data), chain=chain_data)

@app.route('/add_block', methods=['POST'])
def add_block():
    block_data = request.get_json()
    block = Block(**block_data)
    node.blockchain.chain.append(block)
    return "Block added", 201

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    tx_data = request.get_json()
    transaction = Transaction(**tx_data)
    try:
        node.blockchain.create_transaction(transaction)
        return "Transaction added", 201
    except ValueError as e:
        return str(e), 400

@app.route('/mine', methods=['GET'])
def mine():
    node.blockchain.mine_pending_transactions(node.address)
    return "Mining complete", 200

@app.route('/fork', methods=['POST'])
def fork():
    fork_point = request.json.get('fork_point')
    try:
        forked_chain = node.blockchain.fork_chain(fork_point)
        return jsonify([block.__dict__ for block in forked_chain]), 201
    except ValueError as e:
        return str(e), 400

@app.route('/switch_fork', methods=['POST'])
def switch_fork():
    fork_index = request.json.get('fork_index')
    try:
        node.blockchain.switch_to_fork(fork_index)
        return "Switched to fork", 200
    except ValueError as e:
        return str(e), 400

if __name__ == '__main__':
    app.run(port=5000)
```


## 总结

在本文中，我们学习了如何使用 Python 实现一个简单的区块链。我们实现了区块链、区块、交易、智能合约、节点等核心概念。我们还实现了挖矿、交易验证、节点同步等功能。最后，我们介绍了如何使用 Flask 实现一个简单的区块链网络。

后面我们可以继续完善区块链，比如实现更复杂的智能合约、共识算法、隐私保护等功能。希望这篇文章对你有所帮助，欢迎留言讨论。