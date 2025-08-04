---
title: Web3 科学家之如何查看鲸鱼挂单数据
tags: [区块链, web3, dex]
categories:
  - [区块链]
date: 2025-08-04
---

在 Web3 的去中心化金融（DeFi）世界中，“鲸鱼”（即大庄家）凭借巨额资金的交易行为，常常能掀起市场波澜。他们的挂单——无论是已成交的订单还是尚未执行的限价订单——都可能隐藏着市场意图的线索。得益于区块链的透明性，我们可以通过链上数据和专业工具，窥探这些鲸鱼的动向。本文将以循序渐进的方式，带你从零开始探索如何在 Web3 环境中查看鲸鱼的挂单数据，重点使用 Python3 代码展示实现原理，并结合以太坊和 Solana 生态的实际案例，力求清晰、实用。

<!-- more -->

## 已成交订单与未成交挂单

在 Web3 中，挂单分为两类：**已成交的订单**和**未成交的挂单**。已成交的订单记录在区块链上，可通过区块链浏览器直接查询；未成交的挂单则可能存储在去中心化交易所（DEX）的订单簿中（如 dYdX、Serum）或以太坊的内存池（Mempool）中，等待确认。鲸鱼的挂单通常表现为大额资金的买卖订单或流动性操作，可能影响价格走势或市场深度。

## 为什么需要查看鲸鱼挂单？
鲸鱼的挂单数据能揭示他们的交易策略，例如：
- **价格支撑或压制**：大额买单/卖单可能形成“支撑墙”或“阻力墙”。
- **市场操纵**：通过虚假挂单（如“假墙”）吸引散户或诱导价格波动。
- **流动性操作**：在 AMM（如 Uniswap V3）中添加/移除大额流动性，影响交易滑点。

通过链上分析工具和代码，我们可以追踪这些行为，提前捕捉市场信号。

---

## 从区块链浏览器入手，查看已成交挂单

### 原理与过程
区块链的透明性让已成交的订单无处遁形。鲸鱼的交易记录存储在区块链上，无论是转账、代币交换（swap），还是向 DEX 流动性池添加资金，都可以通过区块链浏览器查询。我们以以太坊为例，使用 Etherscan 的 API 和 Python3，提取某个地址的交易历史，筛选出大额订单，推测鲸鱼的挂单行为。

**步骤**：
1. 获取鲸鱼钱包地址（可通过 X 平台或 Nansen 等工具发现）。
2. 使用 Etherscan API 查询该地址的交易记录。
3. 筛选金额超过一定阈值的交易（如 10 ETH 或等值代币）。
4. 分析交易类型（转账、swap、流动性操作）。

### Python 实现
以下代码展示如何通过 Etherscan API 获取某个地址的交易记录，并筛选大额交易：

```python
import requests
import time

# 配置 Etherscan API 密钥和目标地址
API_KEY = "YOUR_ETHERSCAN_API_KEY"  # 替换为你的 Etherscan API 密钥
WALLET_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"  # 示例鲸鱼地址
ETHERSCAN_API = "https://api.etherscan.io/api"

def get_transactions(address, api_key, min_value_eth=10):
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": api_key
    }
    response = requests.get(ETHERSCAN_API, params=params)
    data = response.json()
    
    if data["status"] != "1":
        print(f"API Error: {data['message']}")
        return []
    
    # 筛选大额交易（以 ETH 计）
    large_txs = []
    for tx in data["result"]:
        value_eth = int(tx["value"]) / 10**18  # 转换为 ETH
        if value_eth >= min_value_eth:
            large_txs.append({
                "hash": tx["hash"],
                "value_eth": value_eth,
                "to": tx["to"],
                "timestamp": time.ctime(int(tx["timeStamp"]))
            })
    return large_txs

# 执行查询
transactions = get_transactions(WALLET_ADDRESS, API_KEY)
for tx in transactions:
    print(f"Tx Hash: {tx['hash']}, Value: {tx['value_eth']} ETH, To: {tx['to']}, Time: {tx['timestamp']}")
```

**代码说明**：
- 使用 `requests` 库调用 Etherscan API，查询目标地址的交易历史。
- 筛选金额大于 10 ETH 的交易（可调整阈值）。
- 输出交易哈希、金额、目标地址和时间戳，方便进一步分析。

**注意**：
- 你需要注册 Etherscan 并获取免费 API 密钥。
- 对于代币交易，可修改代码查询 `tokentx` 接口（需调整 `action` 参数）。
- 鲸鱼地址可通过社区（如 X 上的 @Whale_Alert）或 Nansen 获得。

---

## 深入 Mempool，捕捉未成交挂单

### 原理与过程
未成交的挂单可能以待处理交易的形式出现在区块链的内存池（Mempool）中。以太坊的 Mempool 包含尚未确认的交易，可能包括鲸鱼提交的限价订单或大额转账。通过实时监控 Mempool，我们可以捕捉这些未成交的挂单，推测鲸鱼的意图。

**步骤**：
1. 连接以太坊 WebSocket 节点（如 Infura、Alchemy）。
2. 使用 `ethers.py` 监听 Mempool 中的待处理交易。
3. 筛选大额交易（例如价值超过 10 ETH）。
4. 分析交易的目标合约（如 Uniswap 路由器），判断是否为挂单。

### Python 实现
以下代码展示如何使用 `web3.py` 监控以太坊 Mempool 中的大额待处理交易：

```python
from web3 import Web3
import asyncio
import time

# 配置 Web3 提供者
WEB3_WS_URL = "wss://mainnet.infura.io/ws/v3/YOUR_INFURA_PROJECT_ID"  # 替换为你的 Infura WebSocket URL
w3 = Web3(Web3.WebsocketProvider(WEB3_WS_URL))

async def monitor_mempool(min_value_eth=10):
    print("Starting Mempool monitor...")
    while True:
        try:
            # 获取待处理交易
            pending_block = w3.eth.get_block('pending', full_transactions=True)
            for tx in pending_block["transactions"]:
                value_eth = w3.from_wei(tx["value"], "ether")
                if value_eth >= min_value_eth:
                    print(f"Large Pending Tx: Hash={tx['hash'].hex()}, Value={value_eth} ETH, To={tx['to']}")
        except Exception as e:
            print(f"Error: {e}")
        await asyncio.sleep(1)  # 每秒检查一次

# 运行异步监控
if __name__ == "__main__":
    asyncio.run(monitor_mempool())
```

**代码说明**：
- 使用 `web3.py` 连接 Infura 的 WebSocket 节点，实时获取待处理区块的交易。
- 筛选价值大于 10 ETH 的交易，输出交易哈希、金额和目标地址。
- 可扩展代码，分析 `to` 地址是否为 DEX 合约（如 Uniswap 的 Router）。
- 需要 Infura 或 Alchemy 的 WebSocket URL（免费或付费订阅）。

**注意**：
- Mempool 数据变化快，需高性能节点支持。
- 鲸鱼可能使用高 Gas 费用优先确认交易，需关注 Gas Price。

---

## 探索订单簿型 DEX 的未成交挂单

### 原理与过程
在订单簿型 DEX（如 Solana 上的 Serum），未成交的限价订单直接存储在链上或链下订单簿中，公开可查。鲸鱼的挂单可能表现为集中在某一价格区间的大额买单或卖单。我们以 Serum 为例，使用 Python 和 `@solana/web3.py` 查询订单簿，提取大额挂单。

**步骤**：
1. 获取 Serum 市场的地址（通过 Serum 文档或 Solscan）。
2. 使用 `@solana/web3.py` 和 `@project-serum/serum` 库加载市场数据。
3. 查询买单（Bids）和卖单（Asks），筛选大额订单。
4. 分析订单的账户地址，判断是否为鲸鱼。

### Python 实现
以下代码展示如何查询 Serum 市场的订单簿：

```python
from solana.rpc.async_api import AsyncClient
from serum.market import Market
import asyncio

# 配置 Solana 节点和 Serum 市场地址
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
MARKET_ADDRESS = "9wFFyRfZB1P2V3Ab8DwNwg3Vv9NmnfK1h3ScAqaMpfg"  # 示例 Serum 市场地址
PROGRAM_ID = "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin"  # Serum 程序 ID

async def get_orderbook():
    async with AsyncClient(SOLANA_RPC) as client:
        market = await Market.load(client, MARKET_ADDRESS, PROGRAM_ID)
        bids = await market.load_bids(client)
        asks = await market.load_asks(client)
        
        print("Large Buy Orders (Bids):")
        for order in bids:
            if order.size > 1000:  # 筛选大额订单（例如 >1000 单位）
                print(f"Price: {order.price}, Size: {order.size}, Owner: {order.owner}")
        
        print("\nLarge Sell Orders (Asks):")
        for order in asks:
            if order.size > 1000:
                print(f"Price: {order.price}, Size: {order.size}, Owner: {order.owner}")

# 运行查询
if __name__ == "__main__":
    asyncio.run(get_orderbook())
```

**代码说明**：
- 使用 `@solana/web3.py` 和 `@project-serum/serum` 加载 Serum 市场数据。
- 查询买单和卖单，筛选数量大于 1000 的订单（可调整阈值）。
- 输出订单价格、数量和持有者地址，供进一步分析。
- 需要安装 `solana-py` 和 `py-serum` 库（`pip install solana py-serum`）。

**注意**：
- Serum 市场地址需通过 Solscan 或 Serum 文档获取。
- 鲸鱼可能使用多个账户分散挂单，需结合 Nansen 等工具分析。

---

## 分析 AMM 型 DEX 的限价挂单

### 原理与过程
在 AMM 型 DEX（如 Uniswap V3），未成交挂单以限价订单（Range Orders）的形式存在，表现为用户在特定价格区间提供的流动性。鲸鱼可能在关键价格点设置大额流动性，影响市场。我们使用 The Graph 的 Subgraph API 查询 Uniswap V3 池子的流动性数据，筛选大额挂单。

**步骤**：
1. 获取 Uniswap V3 池子地址（通过 Etherscan 或 Uniswap 界面）。
2. 使用 The Graph 的 Subgraph 查询池子的活跃头寸（Positions）。
3. 筛选流动性大于某个阈值的头寸，推测鲸鱼挂单。
4. 分析头寸的价格区间（tickLower 和 tickUpper）。

### Python 实现
以下代码展示如何查询 Uniswap V3 池子的流动性头寸：

```python
import requests

# 配置 Uniswap V3 Subgraph URL 和池子地址
SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
POOL_ADDRESS = "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"  # 示例池子地址（USDC/ETH）

def query_positions(pool_address, min_liquidity=10**18):
    query = """
    {
      positions(where: {pool: "%s", liquidity_gt: %d}) {
        id
        owner
        tickLower
        tickUpper
        liquidity
      }
    }
    """ % (pool_address.lower(), min_liquidity)
    
    response = requests.post(SUBGRAPH_URL, json={"query": query})
    data = response.json()
    
    if "errors" in data:
        print(f"GraphQL Error: {data['errors']}")
        return []
    
    positions = data["data"]["positions"]
    for pos in positions:
        print(f"Position ID: {pos['id']}, Owner: {pos['owner']}, "
              f"Tick Range: {pos['tickLower']} - {pos['tickUpper']}, Liquidity: {pos['liquidity']}")
    return positions

# 执行查询
positions = query_positions(POOL_ADDRESS)
```

**代码说明**：
- 使用 `requests` 向 Uniswap V3 Subgraph 发送 GraphQL 查询。
- 筛选流动性大于 10^18 的头寸（可调整阈值）。
- 输出头寸的 ID、持有者地址、价格区间（tick）和流动性。
- 池子地址可通过 Uniswap 界面或 Etherscan 获取。

**注意**：
- 需要熟悉 Uniswap V3 的 tick 机制，将 tick 转换为价格（可参考 Uniswap 文档）。
- 鲸鱼可能在多个池子分散流动性，需监控多个交易对。

---

## 总结

通过区块链浏览器、Mempool 监控、订单簿查询和 AMM 流动性分析，我们可以全面追踪 Web3 中鲸鱼的挂单数据。Python 代码让这些过程变得可编程、可定制，适合不同层次的用户。无论是初学者的 Etherscan 查询，还是开发者的 Serum 订单簿分析，都能让你更接近 Web3 的“科学家”角色。未来，随着 Web3 生态的演进，更多工具和协议将进一步简化鲸鱼数据的追踪，保持学习，紧跟趋势！

我们最后来总结一下。

### 综合工具推荐
- **基础用户**：Etherscan + DexTools（查看已成交订单和简单订单簿）。
- **进阶用户**：Dune Analytics + Nansen（分析链上数据和鲸鱼行为）。
- **开发者**：Web3.py + Solana-py + The Graph（深度定制分析）。

### 注意事项
- **数据实时性**：Mempool 和订单簿数据变化快，需使用 WebSocket 或高频轮询。
- **隐私与分散**：鲸鱼可能使用多地址或混淆工具（如 Tornado Cash），需结合社区线索（如 X 上的 @Whale_Alert）验证。
- **风险规避**：警惕“貔貅盘”或假挂单陷阱，检查合约代码（通过 Etherscan）确保安全。
- **成本考量**：高级工具（如 Nansen、Blocknative）需付费，评估需求后再订阅。

### 进阶建议
- 结合 **Flashbots** 分析 MEV 交易，捕捉鲸鱼的复杂挂单策略。
- 使用 **0x API** 查询链下订单簿，获取更多 DEX 的未成交挂单。
- 关注 X 平台和 Telegram 群组（如 @NewsCoinSpace），获取鲸鱼地址和市场动态。

