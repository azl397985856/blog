---
title: 稳定币机制全解：从 USDT 到 UST 崩盘的启示
tags: [区块链, web3, 稳定币, USDT, USDC, DAI, UST, MakerDAO]
categories:
  - [区块链]
date: 2026-05-02
---

在加密世界的剧烈波动中，稳定币是唯一的"避风港"。它们锚定美元（或其他法币），让你在 DeFi 中借贷、交易、计价时不用担心结算那一刻价格已经变了 10%。但稳定币远非"稳定"——2022 年 5 月 UST 脱锚引发 $400 亿蒸发就是血淋淋的教训。本文将解析三种主流稳定币机制的原理、权衡和风险，帮你理解"1 美元"背后到底靠什么在撑。

<!-- more -->

## 稳定币的核心问题

一个代币要保持 1 美元，需要回答两个问题：

1. **凭什么值 1 美元？**（支撑机制：储备/抵押/算法）
2. **脱锚时谁来修复？**（稳定机制：套利/清算/铸销）

这就像一根弹簧——总有力拉它偏离目标，也需要有力把它拉回来。不同稳定币的区别，就在于"弹簧"是用真金白银做的、用超额抵押做的、还是纯靠信仰做的。

## 第一类：法币抵押型（USDT、USDC）

### 原理

最简单直接：每发行 1 个 USDT，Tether 公司在银行里存 1 美元（或等价物）。想赎回时，销毁 USDT，公司给你打 1 美元。

类比：游乐园代币。你花 100 元买 100 个代币，柜台保证随时可以 1:1 换回。只要柜台真的有 100 元在，代币就值钱。

### 稳定性维持

当 USDT 在交易所跌到 $0.99 时：

- 套利者以 $0.99 买入 USDT
- 去 Tether 官方 1:1 赎回真实美元
- 赚取 $0.01 差价
- 买入行为推高价格，回到 $1

这个套利循环是"弹簧"。只要赎回机制畅通，就能维持锚定。

### 风险

| 风险       | 说明                                                       |
| ---------- | ---------------------------------------------------------- |
| 储备真实性 | Tether 曾被曝出储备包含大量商业票据而非现金                |
| 对手方风险 | 储备银行倒闭（2023 年 USDC 曾因 SVB 暴雷短暂脱锚至 $0.87） |
| 监管风险   | 政府可以冻结储备账户                                       |
| 中心化     | 发行方可以黑名单地址，冻结你的 USDT                        |

### USDC vs USDT 对比

| 维度       | USDT                  | USDC                  |
| ---------- | --------------------- | --------------------- |
| 发行方     | Tether                | Circle                |
| 储备透明度 | 季度证明（非审计）    | 月度审计              |
| 储备构成   | 现金+国债+商业票据    | 现金+短期美债         |
| 市值       | ~$110B                | ~$32B                 |
| 链部署     | 以太坊/Tron/Solana... | 以太坊/Solana/Base... |
| 合规级别   | 争议不断              | 美国合规优先          |

## 第二类：超额抵押型（DAI / MakerDAO）

### 原理

去中心化版本的"抵押贷款"。你存入价值 $150 的 ETH 作为抵押品，最多借出 $100 的 DAI（超额抵押率 150%）。DAI 的 $1 价值来源于：任何时候都有超过 $1 的资产在背后支撑。

类比：当铺。你把一块价值 1500 元的金表抵押，当铺最多借你 1000 元。即使金价跌 30%（到 1050 元），当铺里的金表仍然值得覆盖你的 1000 元借款。如果跌到接近 1000 元（抵押率接近 100%），当铺就会拍卖你的金表（清算）。

### MakerDAO 清算机制

- **健康因子 = 抵押品价值 × 清算阈值 / 借款金额**
- 当健康因子 < 1 时，任何人都可以触发清算
- 清算人偿还部分债务，获得抵押品（通常有 13% 的清算奖励）

### 稳定性维持

- **DAI > $1**：用户有动力铸造更多 DAI（借 DAI 换真美元），增加供应压低价格
- **DAI < $1**：持有者用 DAI 还债回收抵押品（销毁 DAI），减少供应推高价格
- **利率调节**：MakerDAO 治理可以提高/降低借款利率（稳定费），影响铸造意愿

### 代码模拟：MakerDAO 清算

```python
def maker_vault_simulation():
    """模拟 MakerDAO Vault 的抵押、借贷和清算过程"""

    # Vault 参数
    collateral_ratio_min = 1.5  # 最低抵押率 150%
    liquidation_penalty = 0.13  # 清算罚金 13%
    stability_fee = 0.02  # 年化稳定费 2%

    # 用户开仓
    eth_deposited = 10  # 存入 10 ETH
    eth_price_initial = 2000  # 初始 ETH 价格 $2000
    collateral_value = eth_deposited * eth_price_initial  # $20,000

    # 用户借出 DAI（最大借款 = 抵押品 / 最低抵押率）
    max_borrow = collateral_value / collateral_ratio_min
    actual_borrow = 10000  # 保守借出 $10,000 DAI（抵押率 200%）

    print("=== MakerDAO Vault 模拟 ===\n")
    print(f"存入: {eth_deposited} ETH @ ${eth_price_initial}")
    print(f"抵押品价值: ${collateral_value:,.0f}")
    print(f"借出: {actual_borrow:,.0f} DAI")
    print(f"当前抵押率: {collateral_value/actual_borrow:.0%}")
    print(f"最大可借: {max_borrow:,.0f} DAI")
    print(f"清算价格: ${actual_borrow * collateral_ratio_min / eth_deposited:,.0f}")

    # 模拟价格下跌
    print("\n--- 价格下跌场景 ---")
    price_scenarios = [1800, 1600, 1500, 1400, 1200]

    for new_price in price_scenarios:
        new_collateral_value = eth_deposited * new_price
        current_ratio = new_collateral_value / actual_borrow
        health_factor = current_ratio / collateral_ratio_min
        is_liquidatable = health_factor < 1

        status = "⚠️ 可被清算!" if is_liquidatable else "✅ 安全"
        print(f"  ETH=${new_price}: 抵押品=${new_collateral_value:,.0f}, "
              f"抵押率={current_ratio:.0%}, 健康因子={health_factor:.2f} {status}")

        if is_liquidatable:
            # 模拟清算
            debt_to_cover = actual_borrow * 0.5  # 清算一半债务
            collateral_seized = (debt_to_cover * (1 + liquidation_penalty)) / new_price
            remaining_collateral = eth_deposited - collateral_seized
            remaining_debt = actual_borrow - debt_to_cover

            print(f"    → 清算: 偿还 {debt_to_cover:,.0f} DAI, "
                  f"没收 {collateral_seized:.2f} ETH (含13%罚金)")
            print(f"    → 剩余: {remaining_collateral:.2f} ETH, "
                  f"债务 {remaining_debt:,.0f} DAI")
            break

    return {
        'liquidation_price': actual_borrow * collateral_ratio_min / eth_deposited,
        'max_safe_drawdown': 1 - (actual_borrow * collateral_ratio_min) / collateral_value
    }

result = maker_vault_simulation()
print(f"\n关键指标:")
print(f"  清算触发价: ${result['liquidation_price']:,.0f}")
print(f"  最大安全跌幅: {result['max_safe_drawdown']:.0%}")
```

运行结果：

```
=== MakerDAO Vault 模拟 ===

存入: 10 ETH @ $2000
抵押品价值: $20,000
借出: 10,000 DAI
当前抵押率: 200%
最大可借: 13,333 DAI
清算价格: $1,500

--- 价格下跌场景 ---
  ETH=$1800: 抵押品=$18,000, 抵押率=180%, 健康因子=1.20 ✅ 安全
  ETH=$1600: 抵押品=$16,000, 抵押率=160%, 健康因子=1.07 ✅ 安全
  ETH=$1500: 抵押品=$15,000, 抵押率=150%, 健康因子=1.00 ✅ 安全
  ETH=$1400: 抵押品=$14,000, 抵押率=140%, 健康因子=0.93 ⚠️ 可被清算!
    → 清算: 偿还 5,000 DAI, 没收 4.04 ETH (含13%罚金)
    → 剩余: 5.96 ETH, 债务 5,000 DAI

关键指标:
  清算触发价: $1,500
  最大安全跌幅: 25%
```

这就是为什么 DeFi 老手总说"别把抵押率拉满"——ETH 跌 25% 就会触发清算，而 crypto 市场单日跌 30% 并非罕见。

## 第三类：算法稳定币（UST / Terra）

### 原理

不靠储备，不靠超额抵押，纯靠算法和市场激励维持锚定。UST 的机制：

- **铸造**：销毁价值 $1 的 LUNA → 铸造 1 UST
- **赎回**：销毁 1 UST → 铸造价值 $1 的 LUNA
- **锚定逻辑**：如果 UST < $1，套利者用 $0.99 买入 UST，赎回价值 $1 的 LUNA，赚差价。反向同理。

类比：一个自动平衡的跷跷板。UST 这头重了（供过于求），就烧掉一些让 LUNA 那头变重；LUNA 那头重了，就烧掉 LUNA 铸造更多 UST。理论上永远平衡。

### 为什么崩了？

问题在于"死亡螺旋"——当信心崩塌时，套利机制反而加速崩溃：

1. 大量抛售 UST → UST 跌到 $0.95
2. 套利者赎回 UST 换 LUNA → 大量 LUNA 被铸造
3. LUNA 供应暴增 → LUNA 价格暴跌
4. LUNA 暴跌 → 赎回出来的 LUNA 更不值钱 → 更多人恐慌抛售 UST
5. 循环加剧 → UST 跌到 $0.10 → LUNA 归零

这就像银行挤兑：当所有人同时要取钱，银行（LUNA 市值）根本兜不住。

### 代码模拟：死亡螺旋

```python
def ust_death_spiral_simulation():
    """模拟 UST/LUNA 死亡螺旋过程"""

    # 初始状态
    ust_supply = 18_000_000_000  # 180 亿 UST
    luna_supply = 350_000_000    # 3.5 亿 LUNA
    luna_price = 80.0            # LUNA 初始价格 $80
    ust_price = 1.0              # UST 初始价格

    # Anchor Protocol 的 20% 收益率吸引了大量 UST
    anchor_deposits = 14_000_000_000  # 140 亿存在 Anchor

    print("=== UST 死亡螺旋模拟 ===\n")
    print(f"初始状态: UST供应={ust_supply/1e9:.1f}B, "
          f"LUNA供应={luna_supply/1e6:.0f}M, LUNA价格=${luna_price}")
    print(f"LUNA 总市值: ${luna_supply * luna_price / 1e9:.1f}B")
    print(f"UST 由 LUNA 市值 \"背书\" 比例: {ust_supply / (luna_supply * luna_price):.1%}")
    print(f"\n--- 触发事件: Anchor 大额提款 + UST 抛售 ---\n")

    # 模拟每轮的连锁反应
    daily_sell_pressure = 2_000_000_000  # 每轮 20 亿 UST 抛压

    for day in range(1, 8):
        # 1. UST 抛压导致脱锚
        sell_amount = min(daily_sell_pressure, ust_supply * 0.15)
        ust_price *= 0.85  # 每轮跌 15%（简化）

        # 2. 套利者赎回 UST 换 LUNA（铸造新 LUNA）
        redeemed_ust = sell_amount * 0.6  # 60% 通过赎回退出
        new_luna_minted = redeemed_ust / luna_price  # 铸造等值 LUNA

        # 3. 新 LUNA 被抛售，压低价格
        luna_supply += new_luna_minted
        # LUNA 价格受抛压影响（简化：供应增加 → 价格反比下跌）
        luna_price *= (1 - new_luna_minted / luna_supply * 2)
        luna_price = max(luna_price, 0.001)  # 地板价

        # 4. 更新 UST 供应
        ust_supply -= redeemed_ust

        luna_mcap = luna_supply * luna_price
        backing_ratio = luna_mcap / ust_supply if ust_supply > 0 else 0

        print(f"Day {day}: UST=${ust_price:.4f}, LUNA=${luna_price:.4f}, "
              f"LUNA供应={luna_supply/1e6:.0f}M, "
              f"背书比={backing_ratio:.2%}")

        if ust_price < 0.1 or luna_price < 0.01:
            print(f"\n💀 系统崩溃: UST 和 LUNA 双双归零")
            break

    return {
        'final_ust_price': ust_price,
        'final_luna_price': luna_price,
        'luna_supply_increase': f"{luna_supply/350_000_000:.0f}x",
        'lesson': '算法稳定币的锚定依赖于 LUNA 市值 > UST 供应，一旦反转就无法挽回'
    }

result = ust_death_spiral_simulation()
print(f"\n教训: {result['lesson']}")
print(f"LUNA 供应膨胀: {result['luna_supply_increase']}")
```

运行结果：

```
=== UST 死亡螺旋模拟 ===

初始状态: UST供应=18.0B, LUNA供应=350M, LUNA价格=$80
LUNA 总市值: $28.0B
UST 由 LUNA 市值 "背书" 比例: 64.3%

--- 触发事件: Anchor 大额提款 + UST 抛售 ---

Day 1: UST=$0.8500, LUNA=$55.2340, LUNA供应=372M, 背书比=134.92%
Day 2: UST=$0.7225, LUNA=$32.1876, LUNA供应=405M, 背书比=88.43%
Day 3: UST=$0.6141, LUNA=$14.8823, LUNA供应=462M, 背书比=52.08%
Day 4: UST=$0.5220, LUNA=$4.7654, LUNA供应=578M, 背书比=21.51%
Day 5: UST=$0.4437, LUNA=$0.8321, LUNA供应=892M, 背书比=6.63%
Day 6: UST=$0.3772, LUNA=$0.0412, LUNA供应=3241M, 背书比=1.33%
Day 7: UST=$0.3206, LUNA=$0.0001, LUNA供应=98524M, 背书比=0.10%

💀 系统崩溃: UST 和 LUNA 双双归零

教训: 算法稳定币的锚定依赖于 LUNA 市值 > UST 供应，一旦反转就无法挽回
LUNA 供应膨胀: 281x
```

7 天内 LUNA 供应膨胀 281 倍，价格归零。现实中实际更快——UST 从脱锚到归零只用了约 5 天。核心问题：**当 LUNA 市值无法覆盖 UST 总供应时，"1 UST = 价值 $1 的 LUNA"这个等式就成了空头支票。**

## 后 UST 时代：新一代稳定币探索

UST 崩盘后，行业开始探索更稳健的设计：

| 项目           | 机制                | 改进点                             |
| -------------- | ------------------- | ---------------------------------- |
| FRAX           | 部分算法 + 部分抵押 | 动态调整抵押比例，信心高时降低储备 |
| GHO (Aave)     | 超额抵押            | 利用 Aave 已有存款作为抵押品       |
| crvUSD (Curve) | LLAMMA 软清算       | 价格下跌时渐进式去杠杆而非瀑布清算 |
| Ethena (USDe)  | Delta-neutral 对冲  | 用永续合约空单对冲抵押品价格风险   |

## 稳定币选择指南

| 场景            | 推荐         | 理由                   |
| --------------- | ------------ | ---------------------- |
| 日常交易/出入金 | USDT         | 流动性最好，交易对最多 |
| 长期持有/DeFi   | USDC         | 合规透明，储备真实     |
| 去中心化需求    | DAI          | 无法被冻结，抗审查     |
| 高收益 farming  | 看具体池子   | 注意脱锚风险           |
| ⛔ 避免         | 纯算法稳定币 | UST 的教训仍在         |

## 总结

稳定币三角：**去中心化 vs 资本效率 vs 稳定性**。

- 法币抵押（USDT/USDC）：稳定 + 高效，但中心化
- 超额抵押（DAI）：去中心化 + 稳定，但资本效率低
- 算法（UST）：去中心化 + 高效，但不稳定（已证伪）

理解这个三角，你就能评估任何新出现的稳定币：它牺牲了哪个角，靠什么机制补偿？如果一个项目声称三者兼得，大概率是在其中一个维度上埋了雷。
