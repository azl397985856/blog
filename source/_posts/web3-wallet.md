---
title: Web3 的入口 - 区块链钱包
tags: [区块链, web3, 钱包]
categories:
  - [区块链]
date: 2025-02-16
---

web3 是一个非常流行的概念，它的基础是区块链技术。区块链技术是一种分布式账本技术，它的特点是去中心化、不可篡改、安全可靠。区块链技术的应用场景非常广泛，比如数字货币、智能合约、供应链金融等等。

网上关于区块链的资料非常多，但是从零开始构建的资料却很少。熟悉我的朋友应该知道，我经常从零实现一些东西帮助我理解，比如从零实现 git，从零实现 webpack 打包器，从零实现一个框架等等。

本文就是继上一篇 [《从零开始构建区块链》](https://lucifer.ren/blog/2024/11/22/web3-zero-to-one/ "《从零开始构建区块链》") 的文章，讲述区块链钱包是什么，有什么作用，以及其实现原理，希望能帮助你快速入门区块链技术。

<!-- more -->

## 前言

由于本文不是科普文章，而是直接带你实现，从而加深理解，因此建议你对区块链技术有一定的了解。如果你对区块链技术还不了解，可以先看一些区块链的基础知识，比如区块链的概念、区块链的特点、区块链的应用等等。比如 [learn_blockchain](https://github.com/chaseSpace/learn_blockchain "learn_blockchain") 就是一个还不错的入门资料集合页。

本文使用 Python 语言来实现区块链，Python 是一种非常流行的编程语言，它的语法简单，非常适合初学者。如果你对 Python 不熟悉也没关系，相信我他真的很容易懂。如果你实在不懂，也可以让 chatgpt 给你解释甚至直接翻译为其他语言。

## 学习建议

为了方便大家直接运行，我提供了相对完整的代码示例。强烈大家边看看在本地跟着一起写，一起运行查看效果，只有动手才可能真正理解其核心。并且尽可能地根据我的思路和代码默写，而不是抄写一遍。

## 什么是区块链钱包

本文的实现代码比较简单，但是涉及到区块链的一些基础知识，比如签名、公钥、私钥等等，需要有一定的理解。如果有不懂的地方，可以参考我的上篇文章《从零开始构建区块链》。

上一篇文章介绍了区块链的基本概念，以及如何构建一个简单的区块链。那么作为普通用户，如何与区块链进行交互呢？比如买币，质押等等。

答案是：通常是通过区块链钱包。钱包是一个概念，我们接触的是具体的钱包表现形式。钱包的表现形式可以是一个硬件设备，里面保存着你的私钥，也可以是一个浏览器扩展插件，也可以是一个 APP 等等。

如果说区块链是公司，那么区块链上发行的数字货币就是公司的股票。普通用户不会去开公司，更多的则是买卖股票。买卖股票首先要做的就是开户。而在区块链中，开户就是创建一个钱包地址。 开户我们需要身份认证，然后设置密码。而在区块链中，我们需要生成秘钥。

当开好户后，我们就得到了一个**地址**。我们既可以将地址给别人，让别人给我们转账。也可以将你的地址作为 sender 发起一笔交易。

## 地址拥有权 - 真实世界与区块链的映射

上一节我们提到了如果你想发起一笔交易，我们需要构造一个包括若干字段信息的交易数据（比如 sender、receiver、amount 等等），然后把它发送到区块链网络中，等待被打包进区块。 而发起一笔交易，需要确保**你对该地址的拥有权**，不然就乱套了，谁都可以任意发起交易，就没有意义了。

那么我们如何证明自己对某个地址的拥有权呢？答案是：签名。

签名是一种加密技术，它可以让你证明你拥有某个公钥对应的私钥。也就是说**真实世界中的个人是通过私钥映射到区块链世界的，你掌握了某个私钥，就拥有了某个地址及其对应的资产。** 任何人只要拥有了私钥，它就拥有了私钥对应的资产，因此保护好你的私钥显得尤为重要。

在区块链中，我们需要用私钥对交易数据进行签名，然后把签名和交易数据一起发送到区块链网络中。而验证签名的过程，则是由接收方用公钥进行验证。这在上一节的 Transaction 类的 is_valid 方法中有体现。

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

对于上述代码有疑问的可以看下我的上篇文章《从零开始构建区块链》。

因此对于普通用户来说，我们要做的就是保存私钥，即上述代码中的 private_key。有了 private_key， 我们就可以证明对某个地址的拥有权，进而就可以以该地址作为 sender 发起一笔交易，或者进行一项智能合约操作等等。

## 私钥与助记词

私钥是一串数据，这串数据可以转为字符串来进行保存。私钥是非常重要的，它可以让你拥有对该地址的完全控制权。但是私钥不容易记忆，所以我们通常会用助记词来保存私钥。助记词是一串单词组成的短语，它可以帮助我们记忆私钥。

助记词和私钥是可以通过一定的算法推导的。不同的规范有不同的算法。比如 BIP39 规范，它使用了单词表来生成助记词。 BIP39 规范是固定几个（通常是 12、18 或 24 个单词）单词的助记词。注意自己随便输入 12 个单词是不可行的，因为这些单词是需要特定的结构的（最后一个单词包含一个校验和）。

比如这个助记词就是我根据 BIP 39 规范生成的： `machine future include capable mouse soap blouse fiction cube clip exist series`。其对应的根私钥是 `L4UqB9ABBnvcLQu6WfDk3C9gvpNf98kPw32rp4RQE2YCyj7dzEwA`

我们知道一条链上会发行多种代币。并且目前也有非常多流行的链，这样的话我们的地址就可能有很多。我们知道一个私钥对应一个公钥，一个公钥可以生成一个地址。但是现在我们有很多地址需要管理，如何做呢？

一种方式是：通过地址派生的方式来管理我们的代币。我们只保存主私钥，然后根据一定的派生路径生成不同的地址。这样给定一个主私钥就可以生成很多的子私钥，也就有了很多地址。比如对于 HD 钱包，就可以通过不同的派生路径来生成不同的私钥，将这些子私钥分给不同代币，我们只需要记住一个助记词，而不必记住所有的子私钥。

EVM 链上有很多 token，比如 Base, BNB chain, Polygon 等等。这些 token 都有自己的私钥，而这些私钥都可以通过同一个助记词通过一定的规则来生成。如下图：

![](https://p.ipic.vip/q9nfhj.png)

大家可以使用这个[bip39 网站](https://bip39.best/ "bip39 网站")来基于 BIP39 规范生成助记词或私钥进行相互转化。

本质上，助记词充当您所有私钥的主密钥，种子助记词可以控制许多个账户，而每个私钥只能控制一个账户。作为普通用户，保存好助记词就好了。

## Dapp

我们保存好了助记词，准备开始与区块链进行交互了。

作为普通用户，不可能直接编写运行代码来交互。虽然你可以这么做，但是更普遍的做法是使用 Dapp 或者 Web3 App 来与区块链进行交互。

Dapp 就是一个运行在浏览器中的应用，它可以帮助你与区块链进行交互。与传统的 web2 网站最大的不同是：

1. 它不需要注册登录。因为传统 web2 的用户信息是存到各个公司的后台数据库中，彼此不互通。因此你在网站 A 注册了，网站 B 就无法使用你的账户。你不得不在每个网站注册一个账号。而区块链的数据是公开的，任何人都可以访问。Dapp 可以直接从区块链中读取数据，而不需要每个网站注册一次，用户只需要“登录”即可
2. 用户的“交易，资产”等数据也是存在区块链中的。Dapp 可以直接读取区块链数据，这样多个 Dapp 的数据就可以互通（假设不同 Dapp 使用的是同一条链）

一个简单的 Dapp 的代码，帮助大家理解 Dapp 是如何与区块链交互的。复杂的 Dapp 可能需要编写很多代码，但是基本的原理是一样的。

这里我们使用 web3.js 来实现一个简单的 Dapp。

```html
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DApp Transfer Example</title>
    <script src="https://cdn.jsdelivr.net/npm/web3@1.5.2/dist/web3.min.js"></script>
</head>
<body>
    <h1>发起转账交易</h1>
    <label for="toAddress">接收地址:</label>
    <input type="text" id="toAddress" placeholder="请输入接收地址">
    <br/>
    <label for="amount">转账金额 (以太):</label>
    <input type="number" id="amount" step="any" placeholder="请输入转账金额">
    <br/>
    <button onclick="transfer()">发起转账</button>
    <script>
        let web3;

        // 检查窗口中是否已经注入了web3
        if (window.ethereum) {
            web3 = new Web3(window.ethereum);
            try {
                // 请求用户授权
                window.ethereum.enable();
            } catch (error) {
                console.error("用户拒绝了授权");
            }
        } else if (window.web3) {
            // 老版 MetaMask 在这里注入 web3
            web3 = new Web3(window.web3.currentProvider);
        } else {
            // 用户没有安装 MetaMask
            console.error("请安装 MetaMask 插件");
        }

        async function transfer() {
            const toAddress = document.getElementById('toAddress').value;
            const amount = document.getElementById('amount').value;
            const weiAmount = web3.utils.toWei(amount, 'ether');

            if (!toAddress || !amount || weiAmount <= 0) {
                alert("请输入有效的接收地址和转账金额");
                return;
            }

            const accounts = await web3.eth.getAccounts();
            const sender = accounts[0];

            if (!sender) {
                alert("请确保你已经登录并授权 MetaMask");
                return;
            }

            const transaction = {
                from: sender,
                to: toAddress,
                value: weiAmount,
            };

            try {
                const receipt = await web3.eth.sendTransaction(transaction);
                console.log("转账成功", receipt);
                alert("转账成功");
            } catch (error) {
                console.error("转账失败", error);
                alert("转账失败，请检查你的输入或账户余额");
            }
        }
    </script>
</body>
</html>

```

实现效果如下图：

![](https://p.ipic.vip/7yk3zg.png)

这段代码首先检查用户是否安装了 MetaMask 或其他支持以太坊的浏览器扩展。如果已安装并授权，它将获取用户的账户信息。当用户点击“发起转账”按钮时，代码会调用 transfer 函数，获取用户输入的接收地址和转账金额，然后发送以太坊转账交易。转账金额从以太转换为 wei，因为以太坊的最小单位是 wei。

请注意，这只是一个简单的示例，实际应用中需要处理更多的错误情况和安全问题。确保在生产环境中使用最新的安全实践和库版本。

## 钱包的核心

### 秘钥保存

上面提到用户只需要“登录”即可。这个登录在 web3 叫**Connect Wallet（连接钱包）**。

最简单的，用户点击 Dapp 上的“连接钱包”按钮，然后出来一个输入框让用户输入助记词，Dapp 拿到助记词推出地址，然后就可以展示给用户地址，然后拿地址去区块链中拿交易，资产等数据展现给用户就好了。

这么做的最大问题就是安全性。用户的助记词直接泄漏给了 Dapp，如果这个 Dapp 就是不法分子呢？如果这个 Dapp 被黑客攻击呢？

这个时候钱包就起到作用了，钱包最重要的事情之一就是**安全保存用户的私钥，不让黑客攻击，也不要泄漏给第三方（比如 Dapp）**。

这个实现其实不难。比如 Dapp 需要用户的地址，钱包就暴露一个 `get_address()` 方法 让 dapp 获取。钱包接受到请求后，就用助记词生成私钥，推导出地址，然后返回给 Dapp。Dapp 再拿到地址去区块链中拿交易，资产等数据展现给用户就好了。

再比如 Dapp 需要签署一个交易以转账，钱包暴露一个 `sign_transaction(sender, receiver, amount)` 方法让 dapp 调用。钱包接受到请求后，就用私钥对交易数据进行签名，然后返回给 Dapp。Dapp 再把签名和交易数据一起发送到区块链网络中。

代码：

```py
class Wallet:
    def __init__(self, private_key=None):
        self.private_key = private_key

    def get_address(self):
        if not self.private_key:
            raise Exception('No private key')
            sk = SigningKey.from_string(bytes.fromhex(self.private_key), curve=SECP256k1)
        return sk.verifying_key.to_string().hex()


    def sign_transaction(self, sender, receiver, amount):
        if not self.private_key:
            raise Exception('No private key')
        sk = SigningKey.from_string(bytes.fromhex(self.private_key), curve=SECP256k1)
        transaction = {
           'sender': sender,
           'receiver': receiver,
            'amount': amount
        }
        message = str(transaction).encode('utf-8')
        signature = sk.sign(message).hex()
        return signature
# 1. 钱包测初始化
wallet = Wallet(private_key='your private key')

# 2. Dapp 调用 get_address 方法获取地址
address = wallet.get_address()
print(address)
# 3. Dapp 调用 sign_transaction 方法签名交易
signature = wallet.sign_transaction('sender', 'receiver', 100)
print(signature)
```

> 这里简单起见，将 dapp 环境和钱包核心环境放到一起了，正常不会这样，这里只是方便理解。

这样 Dapp 就接触不到私钥了，就不存在因为 Dapp 被黑客攻击而泄漏私钥的风险。只要钱包开发商是安全的，用户的私钥就不会泄漏给第三方。这样就将**风险从无限多个 dapp 缩小到一个钱包。**

### 多链支持

目前区块链可远远不止比特币，以太坊这么简单。现在的链有很多，热门的有 solana，move 系，ton 系等等。这些热门的内部实现和外部接口都不太一样。

举个例子，EVM 中获取用户地址的方法可能是 `window.ethereum.request({ method: 'eth_requestAccounts'})`，而 solana 中可能是 `window.solana.connect()`。这些 API 不一样，互相无法兼容。这些就需要钱包就实现支持，否则用户就无法使用你的钱包与某条链进行交互。

> 不兼容的可远远不止 api，其交互逻辑，内部算法很可能都不同。不过由于这并不是本文重点，因此我就不展开了。

比如我现在要支持 solana，对于钱包来说，代码可能是这样的：

```py
class SolanaWallet:
    def __init__(self, private_key=None):
        self.private_key = private_key
    def get_address(self):
        if not self.private_key:
            raise Exception('No private key')
            sk = SigningKey.from_string(bytes.fromhex(self.private_key), curve=SECP256k1)
            return sk.verifying_key.to_string().hex()
    def sign_transaction(self, sender, receiver, amount):
        if not self.private_key:
            raise Exception('No private key')
        sk = SigningKey.from_string(bytes.fromhex(self.private_key), curve=SECP256k1)
        transaction = {
           'sender': sender,
        transaction = {
           'sender': sender,
           'receiver': receiver,
            'amount': amount
        }
        message = str(transaction).encode('utf-8')
        signature = sk.sign(message).hex()
        return signature

class Wallet:
    def __init__(self, private_key=None):
        self.private_key = private_key
        self.wallets = {
            'BTC': BitcoinWallet(private_key),
            'ETH': EthereumWallet(private_key),
            'SOL': SolanaWallet(private_key)
        }
    def get_address(self, chain):
        if not self.private_key:
            raise Exception('No private key')
            return self.wallets[chain].get_address()
    def sign_transaction(self, chain, sender, receiver, amount):
        if not self.private_key:
            raise Exception('No private key')
        return self.wallets[chain].sign_transaction(sender, receiver, amount)
1. 钱包测初始化
wallet = Wallet(private_key='your private key')
```

在这种情况下，JS 测只需要简单转化一下即可。

```js
window.solana = {
  connect: () => {
    // 2. Dapp 调用 get_address 方法获取地址
    address = wallet.get_address("SOL"); // 这里 wallet 可以通过 rpc 调用到 python 端的 wallet
    print(address);
  },
  signTransaction: (sender, receiver, amount) => {
    // 3. Dapp 调用 sign_transaction 方法签名交易
    signature = wallet.sign_transaction("SOL", "sender", "receiver", 100);
    print(signature);
  },
};

window.ethereum = {
  // ...
};
```

值得一提的是不同的链签名数据组装很可能是不同的。比如某条链要求前几个字节存 sender，某条链要求前几个字节存 receiver，某条链要求前几个字节存 amount 等等。因此需要钱包根据链的不同，来组装不同的签名数据。另外签名的算法不同链也不一样，比如某条链要求用 ed25519 签名，某条链要求用 secp256k1 签名等等。这些都需要钱包开发者根据链的不同，来定制化接入。

关于钱包开发的细节我还没有讲，如果大家感兴趣，可以留言。如果留言人数多，我会写一篇专门介绍钱包开发的文章（私钥保存与多链支持）。

## 扩展

本文只讲了相对简单的助记词钱包。实际上，还有一种更为先进的叫做 MPC 钱包，即 multi-party computation 钱包。MPC 钱包可以让多个用户一起参与签名，从而提高安全性。MPC 钱包的实现原理是基于多方计算，比如多方一起计算出签名，然后再把结果聚合起来。你的钱包会被分为三个分片，只有拥有两个及以上的分片签名的结果才算有效。一般来说，一个分片保存在用户本质，另外一个保存在托管的钱包 App，第三个上传到云端，比如 iCloud。这样一来，即使你的助记词泄漏给了黑客，也无法通过你的签名来控制资产。如果大家对这部分感兴趣，可以给我留言，如果留言人数多，我会写一篇专门介绍 MPC 钱包的文章。

## 总结

本文介绍了区块链钱包的概念，以及如何实现一个简单的助记词钱包。

区块链钱包的核心两个作用是：

1. 帮助用户保存私钥，并通过私钥签名交易。通过钱包，用户可以与区块链进行交互，比如发起交易、查看交易记录、进行智能合约操作等等。

2. 而区块链的链有很多，因此支持多条链的钱包就显得尤为重要。

另外我们也知道了 Dapp 其实就是运行在浏览器中的应用，它可以帮助用户与区块链进行交互。Dapp 不需要注册，只需要登录（链接我们的钱包）就好了。同时我给大家展示了一个极其简单的 Dapp 例子，帮助大家理解 Dapp 是如何与区块链交互的。麻雀虽小，五脏俱全。大家可以通过这个例子，了解 Dapp 是如何与区块链交互的，以及如何实现一个简单的 Dapp。

最后，感谢大家的阅读，希望本文对大家有所帮助。
