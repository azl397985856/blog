---
title: 看懂 Web3 的 K 线
tags: [区块链, web3, k 线]
categories:
  - [区块链]
date: 2025-06-10
---

web3 是一个非常流行的概念，它的基础是区块链技术。区块链技术是一种分布式账本技术，它的特点是去中心化、不可篡改、安全可靠。区块链技术的应用场景非常广泛，比如数字货币、智能合约、供应链金融等等。

网上关于区块链的资料非常多，但是从零开始构建的资料却很少。熟悉我的朋友应该知道，我经常从零实现一些东西帮助我理解，比如从零实现 git，从零实现 webpack 打包器，从零实现一个框架等等。

本文就是继上一篇 [《Web3 的入口 - 区块链钱包》](https://lucifer.ren/blog/2025/02/16/web3-wallet/ "《Web3 的入口 - 区块链钱包》") 的文章，讲述 K 线图（也称蜡烛图）是什么。并以给定的价格序列 `[1, 10, 20, 8, 3, 2]` 为例，详细讲解 K 线的构成、自定义绘制方法，以及技术指标（移动平均线、布林带、MACD、RSI）的计算与应用，结合背驰分析、趋势判断和支撑/阻力位识别，带你全面理解如何在 Web3 市场中“看懂 K 线”。

<!-- more -->

## 什么是 K 线？

K 线是一种通过柱状图展示价格变动的可视化工具，起源于日本米市交易。每根 K 线代表某段时间内的价格波动，包含四个关键数据点：**开盘价（Open）、收盘价（Close）、最高价（High）、最低价（Low）**。在 Web3 的加密货币市场中，K 线用于分析代币价格在不同时间周期（如 1 分钟、1 小时、1 天等）的表现。

- **K 线的构成**：
  - **实体**：由开盘价和收盘价构成，反映价格的实际变化。收盘价高于开盘价为阳线（通常绿色或白色），反之为阴线（通常红色或黑色）。
  - **影线**：上下两条细线，表示最高价和最低价，反映价格波动范围。
  - **粗细（实体宽度）**：K 线的粗细通常由时间周期决定，固定为图表中每个时间单位的宽度，与价格或成交量无关。但在某些可视化中，可通过自定义设置使实体宽度反映成交量（成交量越大，实体越宽）。
  - **时间周期**：K 线可按分钟、小时、天等周期绘制，周期越短，短期波动越详细；周期越长，越能体现长期趋势。

K 线通过直观形式展现价格动态，帮助投资者判断市场情绪和趋势。

---

## 如何使用代码来画 K 线？

我们将使用 Python 的 `matplotlib` 库自定义绘制 K 线图，基于给定的价格序列 `[1, 10, 20, 8, 3, 2]`，展示从数据处理到绘图的过程。

### 绘制 K 线的原理和过程
1. **数据准备**：K 线需要 OHLC 数据。给定价格序列作为收盘价，模拟开盘价、最高价、最低价和成交量。
2. **数据处理**：将数据整理为 Pandas DataFrame，包含时间戳和 OHLC 列。
3. **自定义绘制**：
   - **实体**：用矩形表示开盘价和收盘价之间的区域，阳线填充绿色，阴线填充红色。
   - **影线**：用线段表示最高价和最低价，连接实体上下两端。
   - **成交量**：在图表下方绘制柱状图，表示交易量。
4. **优化展示**：调整坐标轴、添加网格和标签，确保图表清晰。

以下是自定义绘制 K 线图的代码：

```py
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

# 使用示例价格数据
prices = [1, 10, 20, 8, 3, 2]
dates = [datetime(2025, 6, 1) + timedelta(days=i) for i in range(6)]
data = {
    'Date': dates,
    'Open': [p + np.random.uniform(-1, 1) for p in prices],
    'High': [p + np.random.uniform(1, 3) for p in prices],
    'Low': [p - np.random.uniform(1, 3) for p in prices],
    'Close': prices,
    'Volume': np.random.randint(1000, 5000, 6)
}
df = pd.DataFrame(data)
df.set_index('Date', inplace=True)

# 自定义绘制 K 线图
fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, figsize=(8, 6))
for i, (date, row) in enumerate(df.iterrows()):
    # 绘制影线
    ax1.plot([i, i], [row['Low'], row['High']], color='black', linewidth=1)
    # 绘制实体
    color = 'green' if row['Close'] >= row['Open'] else 'red'
    ax1.bar(i, abs(row['Close'] - row['Open']), bottom=min(row['Open'], row['Close']), color=color, width=0.4)
    # 绘制成交量
    ax2.bar(i, row['Volume'], color='blue', width=0.4)

# 设置图表属性
ax1.set_title('K-Line for Prices [1, 10, 20, 8, 3, 2]')
ax1.set_xticks(range(len(df)))
ax1.set_xticklabels(df.index, rotation=45)
ax1.set_ylabel('Price')
ax2.set_ylabel('Volume')
ax2.set_xticks(range(len(df)))
ax2.set_xticklabels(df.index, rotation=45)
plt.tight_layout()
plt.show()
```

![](https://p.ipic.vip/py5129.png)

### 代码说明
- **数据生成**：以 `[1, 10, 20, 8, 3, 2]` 作为收盘价，随机生成开盘价（±1）、最高价（+1到+3）、最低价（-1到-3）和成交量。
- **自定义绘制**：
  - **影线**：使用 `plot` 绘制最高价到最低价的线。
  - **实体**：使用 `bar` 绘制开盘价到收盘价的矩形，阳线绿色，阴线红色。
  - **成交量**：在下方子图绘制柱状图。
- **美化**：设置时间轴标签、标题和网格，调整子图比例。

运行代码，你将看到一个 K 线图，反映价格从 1 涨到 20 后跌至 2 的波动。

---

## 常见的 K 线技术指标有哪些？

技术指标通过数学计算提炼价格信号，以下是四种常用指标，我们将详细讲解并基于价格序列 `[1, 10, 20, 8, 3, 2]` 进行计算和展示：

1. **移动平均线（MA）**
2. **布林带（Bollinger Bands）**
3. **MACD（移动平均线收敛-发散）**
4. **相对强弱指数（RSI）**

### 移动平均线（MA）的原理和过程

**原理**：移动平均线平滑价格波动，揭示趋势方向。常见类型：
- **简单移动平均线（SMA）**：固定窗口内价格的算术平均值。
- **指数移动平均线（EMA）**：近期价格权重更高，反应更灵敏。

**计算公式**：
- SMA: \(\text{SMA}_n = \frac{\text{Price}_1 + \text{Price}_2 + \dots + \text{Price}_n}{n}\)
- EMA: \(\text{EMA}_t = \text{Price}_t \times k + \text{EMA}_{t-1} \times (1 - k)\)，其中 \(k = \frac{2}{n+1}\)，\(n\) 为周期。

**过程**：
1. 选择周期（如 3 日 SMA 或 EMA，适应短数据）。
2. 对收盘价计算滑动平均（SMA）或加权平均（EMA）。
3. 绘制 MA 线，观察趋势或交叉信号。

**使用场景**
- 短期趋势判断：SMA 适合于短期趋势判断，如 3 日、5 日、10 日均线。
- 长期趋势判断：EMA 适合于长期趋势判断，如 12 月、24 月、36 月均线。

**代码实现**：计算 3 日 SMA 和 EMA，并绘制。

```python
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

# 使用示例价格数据
prices = [1, 10, 20, 8, 3, 2]
dates = [datetime(2025, 6, 1) + timedelta(days=i) for i in range(6)]
data = {
    'Date': dates,
    'Open': [p + np.random.uniform(-1, 1) for p in prices],
    'High': [p + np.random.uniform(1, 3) for p in prices],
    'Low': [p - np.random.uniform(1, 3) for p in prices],
    'Close': prices
}
df = pd.DataFrame(data)
df.set_index('Date', inplace=True)

# 计算 MA
df['SMA3'] = df['Close'].rolling(window=3).mean()
df['EMA3'] = df['Close'].ewm(span=3, adjust=False).mean()

# 绘制 K 线图并添加 MA
fig, ax = plt.subplots(figsize=(8, 6))
for i, (date, row) in enumerate(df.iterrows()):
    ax.plot([i, i], [row['Low'], row['High']], color='black', linewidth=1)
    color = 'green' if row['Close'] >= row['Open'] else 'red'
    ax.bar(i, abs(row['Close'] - row['Open']), bottom=min(row['Open'], row['Close']), color=color, width=0.4)
ax.plot(range(len(df)), df['SMA3'], label='SMA3', color='blue')
ax.plot(range(len(df)), df['EMA3'], label='EMA3', color='orange')

# 设置图表属性
ax.set_title('K-Line with MA for Prices [1, 10, 20, 8, 3, 2]')
ax.set_xticks(range(len(df)))
ax.set_xticklabels(df.index, rotation=45)
ax.set_ylabel('Price')
ax.legend()
plt.tight_layout()
plt.show()
```

![](https://p.ipic.vip/j6y4t2.png)

**代码说明**：
- **SMA3**：使用 `rolling(window=3).mean()` 计算 3 日 SMA。
- **EMA3**：使用 `ewm(span=3, adjust=False).mean()` 计算 3 日 EMA。
- **可视化**：在 K 线图上绘制 SMA 和 EMA，观察趋势。
- **示例结果**：对于 `[1, 10, 20, 8, 3, 2]`，SMA3 和 EMA3 在价格上涨（1→20）时上升，在下跌（20→2）时下降，EMA3 因权重更高，贴近价格变化更紧密，可能更早提示趋势反转（如 20→8）。

---

### 布林带（Bollinger Bands）的原理和过程

**原理**：布林带由中轨（SMA）、上轨（SMA + k×标准差）、下轨（SMA - k×标准差）组成，衡量价格波动范围和超买/超卖区域。
- **中轨**：通常为 SMA，反映趋势。
- **上轨/下轨**：基于标准差，反映波动边界，通常 \(k=2\)。
- **应用**：价格触及上轨可能超买，触及下轨可能超卖；布林带收窄预示低波动，扩张预示高波动。

**计算公式**：
- 中轨: \(\text{SMA}_n = \frac{\text{Price}_1 + \text{Price}_2 + \dots + \text{Price}_n}{n}\)
- 标准差: \(\sigma = \sqrt{\frac{\sum (\text{Price}_i - \text{SMA})^2}{n}}\)
- 上轨: \(\text{SMA} + k \cdot \sigma\)
- 下轨: \(\text{SMA} - k \cdot \sigma\)

**过程**：
1. 计算 3 日 SMA（适应短数据）作为中轨。
2. 计算 3 日标准差。
3. 计算上轨和下轨（\(k=2\)）。
4. 绘制三条线，观察价格与上下轨的关系。

**使用场景**
- 交易策略：布林带上轨和下轨作为买入/卖出信号。
- 分析：判断价格是否超出布林带，判断价格是否在上/下轨附近波动。

**代码实现**：计算 3 日布林带并绘制。

```python
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

# 使用示例价格数据
prices = [1, 10, 20, 8, 3, 2]
dates = [datetime(2025, 6, 1) + timedelta(days=i) for i in range(6)]
data = {
    'Date': dates,
    'Open': [p + np.random.uniform(-1, 1) for p in prices],
    'High': [p + np.random.uniform(1, 3) for p in prices],
    'Low': [p - np.random.uniform(1, 3) for p in prices],
    'Close': prices
}
df = pd.DataFrame(data)
df.set_index('Date', inplace=True)

# 计算布林带
def calculate_bollinger_bands(data, window=3, k=2):
    sma = data['Close'].rolling(window=window).mean()
    std = data['Close'].rolling(window=window).std()
    upper_band = sma + k * std
    lower_band = sma - k * std
    return sma, upper_band, lower_band

df['SMA3'], df['Upper'], df['Lower'] = calculate_bollinger_bands(df)

# 绘制 K 线图并添加布林带
fig, ax = plt.subplots(figsize=(8, 6))
for i, (date, row) in enumerate(df.iterrows()):
    ax.plot([i, i], [row['Low'], row['High']], color='black', linewidth=1)
    color = 'green' if row['Close'] >= row['Open'] else 'red'
    ax.bar(i, abs(row['Close'] - row['Open']), bottom=min(row['Open'], row['Close']), color=color, width=0.4)
ax.plot(range(len(df)), df['SMA3'], label='SMA3', color='blue')
ax.plot(range(len(df)), df['Upper'], label='Upper Band', color='red')
ax.plot(range(len(df)), df['Lower'], label='Lower Band', color='green')

# 设置图表属性
ax.set_title('K-Line with Bollinger Bands for Prices [1, 10, 20, 8, 3, 2]')
ax.set_xticks(range(len(df)))
ax.set_xticklabels(df.index, rotation=45)
ax.set_ylabel('Price')
ax.legend()
plt.tight_layout()
plt.show()
```

![](https://p.ipic.vip/xxk8he.png)

**代码说明**：
- **布林带计算**：使用 3 日 SMA 和标准差，计算上轨和下轨（\(k=2\)）。
- **可视化**：绘制中轨、上轨、下轨，观察价格波动。
- **示例结果**：对于 `[1, 10, 20, 8, 3, 2]`，布林带在价格剧烈波动（10→20→8）时扩张，价格接近上轨（如 20）提示超买，接近下轨（如 2）提示超卖。

---

### MACD（移动平均线收敛-发散）的原理和过程

**原理**：MACD 通过比较短期和长期 EMA 的差值，衡量价格动能和趋势变化，包含：
- **双线**：快线 DIF 和慢线 DEA，反映价格趋势。
- **能量柱**：n * (快线 DIF - 快线 DEA)，反映价格动能。
- **默认值**：(12, 26, 9) 表示快线由 12日 EMA减去 26日 EMA，慢线是快线的 9日移动平均线。

快线大于慢线，能量柱在 0 以上，差值越大，能量柱越大。反之，快线小于慢线，能量柱在 0 以下，差值越小，能量柱越小。

**计算公式**：

> 这里为了方便演示，不是使用默认参数 (12, 26, 9)，而是使用 (3, 6, 2)

- 快线: \(\text{MACD} = \text{EMA}_{3} - \text{EMA}_{6}\)
- 慢线: \(\text{Signal} = \text{EMA}_{2}(\text{MACD})\)
- 柱状图: \(\text{Histogram} = \text{MACD} - \text{Signal}\)

**过程**：
1. 计算 3 日和 6 日 EMA，得到快线。
2. 对 MACD 线取 2 日 EMA，得到慢线。
3. 计算柱状图，绘制快线、慢线和能量柱。


**使用场景**
- 快线在慢线上方表示近期上涨趋势，快线在慢线下方表示近期下跌趋势。
- 快线与慢线金叉（上穿）提示买入，死叉（下穿）提示卖出。


**代码实现**：计算 MACD 并绘制。

```python
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

# 使用示例价格数据
prices = [1, 10, 20, 8, 3, 2]
dates = [datetime(2025, 6, 1) + timedelta(days=i) for i in range(6)]
data = {
    'Date': dates,
    'Open': [p + np.random.uniform(-1, 1) for p in prices],
    'High': [p + np.random.uniform(1, 3) for p in prices],
    'Low': [p - np.random.uniform(1, 3) for p in prices],
    'Close': prices
}
df = pd.DataFrame(data)
df.set_index('Date', inplace=True)

# 计算 MACD
def calculate_macd(data, fast=3, slow=6, signal=2):
    ema_fast = data['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = data['Close'].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

df['MACD'], df['Signal'], df['Histogram'] = calculate_macd(df)

# 绘制 K 线图并添加 MACD
fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, figsize=(8, 6))
for i, (date, row) in enumerate(df.iterrows()):
    ax1.plot([i, i], [row['Low'], row['High']], color='black', linewidth=1)
    color = 'green' if row['Close'] >= row['Open'] else 'red'
    ax1.bar(i, abs(row['Close'] - row['Open']), bottom=min(row['Open'], row['Close']), color=color, width=0.4)
ax2.plot(range(len(df)), df['MACD'], label='MACD', color='blue')
ax2.plot(range(len(df)), df['Signal'], label='Signal', color='red')
ax2.bar(range(len(df)), df['Histogram'], color='gray', alpha=0.5)

# 设置图表属性
ax1.set_title('K-Line with MACD for Prices [1, 10, 20, 8, 3, 2]')
ax1.set_xticks(range(len(df)))
ax1.set_xticklabels(df.index, rotation=45)
ax1.set_ylabel('Price')
ax2.set_ylabel('MACD')
ax2.set_xticks(range(len(df)))
ax2.set_xticklabels(df.index, rotation=45)
ax2.legend()
plt.tight_layout()
plt.show()
```

![](https://p.ipic.vip/uxhipc.png)

**代码说明**：
- **MACD 计算**：使用 3 日和 6 日 EMA 计算 MACD 线，2 日 EMA 计算信号线，差值生成柱状图。
- **可视化**：绘制 MACD 线、信号线和柱状图，观察交叉信号。
- **示例结果**：对于 `[1, 10, 20, 8, 3, 2]`，MACD 线在价格上涨（1→20）时上升，下跌（20→2）时下降，可能在 20→8 时出现死叉，提示卖出。

---

### 相对强弱指数（RSI）的原理和过程

**原理**：RSI 衡量价格涨跌的相对强度，判断超买（>70）或超卖（<30）状态。
- **应用**：超买提示下跌风险，超卖提示上涨机会，结合 K 线形态确认信号。

**计算公式**：
\[ RSI = 100 - \frac{100}{1 + \frac{\text{平均上涨幅度}}{\text{平均下跌幅度}}} \]

**过程**：
1. 计算每日价格变化（`diff`）。
2. 分离上涨和下跌幅度，计算 3 日平均值（适应短数据）。
3. 套用 RSI 公式，绘制 RSI 曲线。

**使用场景**
- RSI 超过 70 时，提示超买，RSI 低于 30 时，提示超卖。
- RSI 高于 70 时，价格可能反转，RSI 低于 30 时，价格可能反转。

**代码实现**：计算 3 日 RSI 并绘制。

```python
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

# 使用示例价格数据
prices = [1, 10, 20, 8, 3, 2]
dates = [datetime(2025, 6, 1) + timedelta(days=i) for i in range(6)]
data = {
    'Date': dates,
    'Open': [p + np.random.uniform(-1, 1) for p in prices],
    'High': [p + np.random.uniform(1, 3) for p in prices],
    'Low': [p - np.random.uniform(1, 3) for p in prices],
    'Close': prices
}
df = pd.DataFrame(data)
df.set_index('Date', inplace=True)

# 计算 RSI
def calculate_rsi(data, periods=3):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['RSI'] = calculate_rsi(df)

# 绘制 K 线图并添加 RSI
fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, figsize=(8, 6))
for i, (date, row) in enumerate(df.iterrows()):
    ax1.plot([i, i], [row['Low'], row['High']], color='black', linewidth=1)
    color = 'green' if row['Close'] >= row['Open'] else 'red'
    ax1.bar(i, abs(row['Close'] - row['Open']), bottom=min(row['Open'], row['Close']), color=color, width=0.4)
ax2.plot(range(len(df)), df['RSI'], color='purple', label='RSI')
ax2.axhline(70, color='red', linestyle='--', alpha=0.5)
ax2.axhline(30, color='green', linestyle='--', alpha=0.5)

# 设置图表属性
ax1.set_title('K-Line with RSI for Prices [1, 10, 20, 8, 3, 2]')
ax1.set_xticks(range(len(df)))
ax1.set_xticklabels(df.index, rotation=45)
ax1.set_ylabel('Price')
ax2.set_ylabel('RSI')
ax2.set_xticks(range(len(df)))
ax2.set_xticklabels(df.index, rotation=45)
ax2.legend()
plt.tight_layout()
plt.show()
```

![](https://p.ipic.vip/wf2dfw.png)

**代码说明**：
- **RSI 计算**：使用 3 日平均值计算 RSI，适应短数据。
- **可视化**：绘制 RSI 曲线，标注超买（70）和超卖（30）线。
- **示例结果**：对于 `[1, 10, 20, 8, 3, 2]`，RSI 在上涨（1→20）时可能接近 70，提示超买；在下跌（8→2）时接近 30，提示超卖。

---


## K 的实际应用

这里以 **支撑位和阻力位**为例，介绍 K 线的实际应用。

### 支撑位和阻力位的定义
- **支撑位**：价格下跌时难以跌破的水平，通常为历史低点或密集交易区。
- **阻力位**：价格上涨时难以突破的水平，通常为历史高点或密集交易区。

### 支撑位和阻力位的识别
- **历史价格**：多次触及但未跌破的低点（支撑）或未突破的高点（阻力）。
- **成交量**：高成交量强化支撑/阻力位的有效性。
- **技术指标**：布林带下轨可作为动态支撑，上轨可作为动态阻力。

**代码实现**：检测支撑位。

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 使用示例价格数据
prices = [1, 10, 20, 8, 3, 2]
dates = [datetime(2025, 6, 1) + timedelta(days=i) for i in range(6)]
data = {
    'Date': dates,
    'Close': prices,
    'Volume': np.random.randint(1000, 5000, 6)
}
df = pd.DataFrame(data)
df.set_index('Date', inplace=True)

# 检测支撑位
def detect_support_levels(df, window=2):
    supports = []
    for i in range(window, len(df) - window):
        if (df['Close'].iloc[i] < df['Close'].iloc[i-window:i].min() and
            df['Close'].iloc[i] < df['Close'].iloc[i+1:i+window+1].min() and
            df['Volume'].iloc[i] > df['Volume'].mean()):
            supports.append((df.index[i], df['Close'].iloc[i]))
    return supports

supports = detect_support_levels(df)
for date, price in supports:
    print(f"Support level detected at {date}: Price={price:.2f}")
```

![](https://p.ipic.vip/4jpcyb.png)

**代码说明**：
- **支撑位检测**：使用 2 日窗口（适应短数据），寻找价格低点且成交量高于平均值。
- **示例结果**：对于 `[1, 10, 20, 8, 3, 2]`，价格 2（6/6）可能被识别为支撑位，因其为最低点且成交量可能较高。

## 总结

K 线是 Web3 市场分析的核心工具，通过 OHLC 数据展示价格波动，其粗细通常由时间周期决定，可自定义反映成交量。以价格序列 `[1, 10, 20, 8, 3, 2]` 为例，我们使用 Python 的 `matplotlib` 自定义绘制了 K 线图，并详细讲解了 MA、布林带、MACD 和 RSI 的计算与应用，展示了趋势（如 1→20 上涨，20→2 下跌）、买卖信号（如 RSI 接近 30 时买入）和支撑位（如价格 2）。支撑/阻力位识别增强了交易决策。这些工具和方法帮助投资者在 Web3 市场捕捉机会，愿本文助你在加密世界中“看懂 K 线”！