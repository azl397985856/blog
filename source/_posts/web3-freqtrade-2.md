---
title: Freqtrade 进阶：把多个弱信号拧成一根绳——多信号评分策略实战
tags: [区块链, web3, 量化交易]
categories:
  - [区块链]
date: 2026-07-20
---
大家好，我是 Lucifer，又来聊聊 Web3 的那些有趣事儿了。今天咱们来聊聊 Freqtrade。

上一篇我们从零搭好了 Freqtrade，写了个最简单的 SMA 交叉策略。很多人跑完回测后跟我说：“这策略也太简单了，实盘根本扛不住。”

说得对。那篇是入门用的“Hello World”。真正能活下来的策略，从来不是依赖某一个“神级指标”，而是把一堆看起来不怎么样的弱信号，用正确的方式组合起来。

今天这篇是正式续篇。我们会把「组合弱信号」这个核心思想，落地成一个能直接在 Freqtrade 里跑的策略。


<!-- more -->


### 先补一点前置知识

在写策略之前，先把两个最基础的概念说清楚。

**1. 什么是信号？**

信号不是“我觉得这个币要涨”这种模糊感觉，而是一个可量化、有方向、可重复的数据点。比如：

- RSI 从 30 以下回升
- 快线上穿慢线
- 成交量放大到均线的 1.3 倍

这些都是信号。单个信号通常很弱，准确率往往只有 50% 多一点点。

**2. dataframe.loc 是干什么的？**

Freqtrade 策略的核心是一张表格（DataFrame），每一行是一根 K 线，每一列是价格或指标。

`dataframe.loc[条件, 列名] = 值` 的意思是：  
**找到符合条件的那些 K 线，给它们打上标记。**

比如：

```python
dataframe.loc[
    (dataframe['rsi'] < 30) & (dataframe['volume'] > 0),
    'enter_long'
] = 1
```

这句话的意思就是：“凡是 RSI 低于 30 且有成交量的 K 线，都标记为可以买入。”

后面所有买卖逻辑，本质上都是在用 `.loc` 给不同的行打分或打标记。

### 为什么要组合多个弱信号？

单一信号最大的问题是：**它大部分时候都是错的**。

量化里把单个信号的准确度叫 IC（Information Coefficient）。机构级信号的 IC 通常只有 0.05～0.15，意思是它跟市场真实走势的相关性非常弱。

但主动管理基本定律告诉我们：

**IR = IC × √N**

系统整体表现 = 单个信号准确度 × 独立信号数量的平方根。

所以，与其苦苦寻找一个“永远正确”的神级信号，不如收集几十个“稍微有点准”的弱信号，然后把它们正确地组合起来。噪音会互相抵消，优势会叠加。

这就是今天策略的核心思路。

### 策略思路

我们不追求某一个指标特别准，而是让多个弱信号一起“投票”。

具体做法：

1. 选取 6 个相关性较低的常见信号（动量、均值回归、成交量、趋势强度等）。
2. 每个信号根据自己的条件给当前 K 线打分（有的 +1，有的 +2）。
3. 把所有分数加总，得到一个综合置信度分数。
4. 只有当综合分数达到设定阈值时，才允许开仓。
5. 出场逻辑反过来，用反向信号打分，达到阈值就平仓。

这样做的好处是：

- 不再要求所有条件同时成立（那会让信号极少）。
- 不同信号可以有不同权重（比如 RSI 回升给 2 分，普通交叉只给 1 分）。
- 噪音被分散，真正有优势的时刻更容易被识别出来。

这已经是文章里“组合引擎”思想的简化落地版。真正的机构还会做去均值、正交化、残差加权等更复杂的步骤，但对我们现阶段来说，评分投票已经足够体现核心逻辑。

### 完整策略代码（辅助参考）

把下面代码保存为 `user_data/strategies/MultiSignalScore.py` 即可：

```python
from freqtrade.strategy import IStrategy, IntParameter
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class MultiSignalScore(IStrategy):
    """
    多弱信号评分策略
    核心思想：用多个低 IC 信号投票，提升整体系统表现
    """

    INTERFACE_VERSION = 3
    timeframe = '15m'
    can_short = False

    minimal_roi = {
        "0": 0.035,
        "40": 0.02,
        "90": 0.01
    }
    stoploss = -0.055
    trailing_stop = True
    trailing_stop_positive = 0.012
    trailing_stop_positive_offset = 0.022
    trailing_only_offset_is_reached = True

    startup_candle_count = 50

    # 可优化参数
    buy_score_threshold = IntParameter(4, 8, default=5, space='buy')
    sell_score_threshold = IntParameter(3, 6, default=4, space='sell')

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 动量
        dataframe['sma_fast'] = ta.SMA(dataframe, timeperiod=10)
        dataframe['sma_slow'] = ta.SMA(dataframe, timeperiod=30)
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # 均值回归
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lower'] = bollinger['lower']
        dataframe['bb_middle'] = bollinger['mid']
        dataframe['bb_upper'] = bollinger['upper']

        # 趋势强度 + 成交量
        dataframe['adx'] = ta.ADX(dataframe)
        dataframe['volume_sma'] = ta.SMA(dataframe, timeperiod=20, price='volume')

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['buy_score'] = 0

        # 1. SMA 金叉
        dataframe.loc[
            (dataframe['sma_fast'] > dataframe['sma_slow']) &
            (dataframe['sma_fast'].shift(1) <= dataframe['sma_slow'].shift(1)),
            'buy_score'] += 1

        # 2. MACD 柱由负转正
        dataframe.loc[
            (dataframe['macdhist'] > 0) &
            (dataframe['macdhist'].shift(1) <= 0),
            'buy_score'] += 1

        # 3. RSI 从超卖区回升（权重更高）
        dataframe.loc[
            (dataframe['rsi'] > 30) &
            (dataframe['rsi'].shift(1) <= 30),
            'buy_score'] += 2

        # 4. 价格接近布林下轨
        dataframe.loc[
            (dataframe['close'] < dataframe['bb_lower'] * 1.01),
            'buy_score'] += 1

        # 5. 成交量放大
        dataframe.loc[
            (dataframe['volume'] > dataframe['volume_sma'] * 1.3),
            'buy_score'] += 1

        # 6. ADX 有趋势且上升
        dataframe.loc[
            (dataframe['adx'] > 20) &
            (dataframe['adx'] > dataframe['adx'].shift(1)),
            'buy_score'] += 1

        # 分数达标才入场
        dataframe.loc[
            (dataframe['buy_score'] >= self.buy_score_threshold.value) &
            (dataframe['volume'] > 0),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['sell_score'] = 0

        dataframe.loc[
            (dataframe['sma_fast'] < dataframe['sma_slow']) &
            (dataframe['sma_fast'].shift(1) >= dataframe['sma_slow'].shift(1)),
            'sell_score'] += 1

        dataframe.loc[
            (dataframe['macdhist'] < 0) &
            (dataframe['macdhist'].shift(1) >= 0),
            'sell_score'] += 1

        dataframe.loc[
            (dataframe['rsi'] > 70),
            'sell_score'] += 2

        dataframe.loc[
            (dataframe['close'] > dataframe['bb_upper'] * 0.99),
            'sell_score'] += 1

        dataframe.loc[
            (dataframe['sell_score'] >= self.sell_score_threshold.value) &
            (dataframe['volume'] > 0),
            'exit_long'] = 1

        return dataframe
```

### 怎么跑起来

下载数据后执行回测：

```bash
freqtrade backtesting --strategy MultiSignalScore --timerange 20240701-20250701 --export trades
```

想优化阈值参数，可以用：

```bash
freqtrade hyperopt --strategy MultiSignalScore --hyperopt-loss SharpeHyperOptLoss --spaces buy sell --epochs 100
```

### 总结

一个现实中真正可用的策略基本就是按照这个方式去叠加信号， 给不同信号分配不同的权重等等。

量化最反直觉的一点是：你越执着于寻找“永远正确”的信号，你就越容易亏钱。真正能持续活下来的人，都在默默收集那些“稍微有点准”的弱信号，然后用数学把它们拧成一股绳。