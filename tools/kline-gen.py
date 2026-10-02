#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成《蜡烛图技术分析》(japan-k-line.md) 全部 40 张形态示意图。

风格约定：
- 红色 = 阳线（收 > 开），绿色 = 阴线（收 < 开）
- 灰色蜡烛 = 形态出现前的趋势背景
- 暖色高亮带 = 形态本体所在区域
- 虚线箭头 = 形态之后的预期方向
运行：python3 gen.py   （依赖 matplotlib，输出到本目录 *.png）
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
import os

plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "source", "images", "kline")

UP_FACE, UP_EDGE = "#e8554e", "#c13a34"
DN_FACE, DN_EDGE = "#1fa06b", "#157a52"
CTX_FACE, CTX_EDGE = "#dadee6", "#a9b2bd"
INK, SUB, GUIDE = "#2e3a46", "#7b8794", "#8a93a0"
HIGHLIGHT = "#fdf3d8"
BULL, BEAR = "#c13a34", "#157a52"

TAG_STYLE = {
    "bull": ("#fdeceb", "#e8554e", "#b2322c"),
    "bear": ("#e5f5ee", "#1fa06b", "#116b48"),
    "neutral": ("#eef1f5", "#8a93a0", "#5a6572"),
}


def mirror(seq):
    """上下镜像一组蜡烛（用于顶部形态 <-> 底部形态），阳线变阴线。"""
    out = []
    for o, h, l, c in seq:
        out.append((108 - c, 108 - l, 108 - h, 108 - o))
    return out


def ctx_down(n, start, end, seed=7):
    """n 根下跌趋势的灰色背景蜡烛，最后一根收盘恰为 end。"""
    import random
    rnd = random.Random(seed)
    out, prev = [], start
    step = (start - end) / n
    for i in range(n):
        close = end if i == n - 1 else start - step * (i + 1) + rnd.uniform(-1.2, 1.2)
        o = prev + rnd.uniform(-0.6, 2.2)
        h = max(o, close) + rnd.uniform(0.3, 1.5)
        l = min(o, close) - rnd.uniform(0.3, 1.5)
        out.append((round(o, 1), round(h, 1), round(l, 1), round(close, 1)))
        prev = close
    return out


def ctx_up(n, start, end, seed=7):
    return mirror(ctx_down(n, 108 - start, 108 - end, seed))


# ---------------------------------------------------------------- 图形定义
# 蜡烛格式: (open, high, low, close)
# notes 类型:
#   ("p", x, y, 文字, dx, dy)            指针标注
#   ("h", y, x0, x1, 文字)               水平参考线
#   ("w", x0, x1, y0, y1, 文字)          跳空窗口
#   ("t", (x1,y1), (x2,y2), 文字)        趋势线（支撑/压力）
F = []  # (文件名, 主标题, 副标题, [panel, ...])

# ============ 1. 单一 K 线 ============
F.append(("1-1-umbrella.png", "伞形线：锤子线 / 上吊线", "实体较短、下影线较长，出现的位置决定多空含义", [
    dict(name="锤子线（下跌趋势中）", tag=("看涨反转", "bull"),
         ctx=ctx_down(4, 66, 46), pat=[(45.5, 48.8, 31, 48)],
         post="up", post_label="看涨",
         notes=[("p", 4, 32, "长下影线", -1.2, -2), ("p", 4, 47.6, "小实体", 1.0, 3.5)]),
    dict(name="上吊线（上涨趋势中）", tag=("看跌反转", "bear"),
         ctx=ctx_up(4, 36, 58), pat=[(59.5, 60.5, 45, 57)],
         post="down", post_label="看跌",
         notes=[("p", 4, 46, "长下影线", -1.2, -2), ("p", 4, 60.2, "小实体", 1.0, 3.5)]),
]))

F.append(("1-2-shooting-star.png", "流星线 / 倒锤子线", "实体较短、上影线较长，出现的位置决定多空含义", [
    dict(name="倒锤子线（下跌趋势中）", tag=("看涨反转", "bull"),
         ctx=ctx_down(4, 66, 46), pat=[(45.5, 61, 44.6, 48)],
         post="up", post_label="看涨",
         notes=[("p", 4, 59.5, "长上影线", 1.0, 3), ("p", 4, 46.8, "小实体", -1.4, -3.5)]),
    dict(name="流星线（上涨趋势中）", tag=("看跌反转", "bear"),
         ctx=ctx_up(4, 36, 58), pat=[(59.5, 75, 56.4, 57)],
         post="down", post_label="看跌",
         notes=[("p", 4, 73.5, "长上影线", 1.0, 3), ("p", 4, 58.3, "小实体", -1.4, -3.5)]),
]))

F.append(("1-3-belt-hold.png", "捉腰带线", "实体较长、影线极短，开盘价即当段极值", [
    dict(name="看涨捉腰带线（阳线）", tag=("看涨反转", "bull"),
         ctx=ctx_down(4, 66, 46), pat=[(46, 60.5, 45.6, 59)],
         post="up", post_label="看涨",
         notes=[("p", 4, 45.9, "开盘≈最低价", 1.0, -4)]),
    dict(name="看跌捉腰带线（阴线）", tag=("看跌反转", "bear"),
         ctx=ctx_up(4, 36, 58), pat=[(59.8, 60, 45.5, 46.5)],
         post="down", post_label="看跌",
         notes=[("p", 4, 60, "开盘≈最高价", 1.0, 4)]),
]))

F.append(("1-4-northern-doji.png", "北方十字线", "上涨趋势中出现的十字线（开盘价≈收盘价）", [
    dict(name=None, tag=("看跌意味", "bear"),
         ctx=ctx_up(5, 34, 56), pat=[(56.2, 61, 52, 56.6)],
         post="down", post_label="警惕见顶",
         notes=[("p", 4, 52.5, "开≈收", 1.0, -3)]),
]))

F.append(("1-5-southern-doji.png", "南方十字线", "下跌趋势中出现的十字线（开盘价≈收盘价）", [
    dict(name=None, tag=("看涨意味", "bull"),
         ctx=ctx_down(5, 68, 46), pat=[(45.8, 50, 41, 45.4)],
         post="up", post_label="警惕见底",
         notes=[("p", 4, 41.5, "开≈收", 1.0, -3)]),
]))

F.append(("1-6-long-legged-doji.png", "长腿十字线", "开盘价≈收盘价，上下影线均较长，多空胶着", [
    dict(name=None, tag=("变盘信号", "neutral"),
         ctx=ctx_down(4, 62, 50), pat=[(50.2, 63, 37, 49.8)],
         post="both",
         notes=[("p", 4, 61.5, "长上影线", 1.0, 3), ("p", 4, 38.5, "长下影线", 1.0, -3)]),
]))

F.append(("1-7-gravestone-doji.png", "墓碑十字线", "开盘≈收盘≈最低价，上影线较长", [
    dict(name=None, tag=("看跌反转", "bear"),
         ctx=ctx_up(4, 38, 54), pat=[(53.8, 70, 53.2, 53.8)],
         post="down", post_label="看跌",
         notes=[("p", 4, 68, "长上影线", 1.0, 3), ("p", 4, 53.4, "实体≈最低", -1.8, -3.5)]),
]))

F.append(("1-8-dragonfly-doji.png", "蜻蜓十字线", "开盘≈收盘≈最高价，下影线较长", [
    dict(name=None, tag=("看涨反转", "bull"),
         ctx=ctx_down(4, 66, 48), pat=[(48.2, 48.8, 32, 48.2)],
         post="up", post_label="看涨",
         notes=[("p", 4, 33.5, "长下影线", 1.0, -3), ("p", 4, 48.6, "实体≈最高", 1.2, 3)]),
]))

# ============ 2. 两根 K 线 ============
F.append(("2-1-engulfing.png", "吞没形态", "后一根实体完全包裹前一根实体，且二者颜色相反", [
    dict(name="看涨吞没（下跌趋势中）", tag=("看涨反转", "bull"),
         ctx=ctx_down(3, 60, 46),
         pat=[(46.5, 47.3, 43.9, 44), (42.8, 53, 42.2, 52.3)],
         post="up", post_label="看涨",
         notes=[("p", 4, 47.1, "小阴线", -1.3, 3.5), ("p", 5, 52.6, "实体吞没", 1.0, 3.5)]),
    dict(name="看跌吞没（上涨趋势中）", tag=("看跌反转", "bear"),
         ctx=ctx_up(3, 40, 56),
         pat=[(54.5, 57.6, 54, 57), (58.8, 59.4, 49, 49.8)],
         post="down", post_label="看跌",
         notes=[("p", 4, 57.8, "小阳线", -1.3, 3.5), ("p", 5, 49.3, "实体吞没", 1.0, -3.5)]),
]))

F.append(("2-2-dark-cloud-cover.png", "乌云盖顶", "上涨趋势中：阳线之后，阴线高开且收盘深入阳线实体中点之下", [
    dict(name=None, tag=("看跌反转", "bear"),
         ctx=ctx_up(4, 38, 54),
         pat=[(53.5, 59.8, 52.9, 59), (62.5, 63.2, 53.8, 54.6)],
         post="down", post_label="看跌",
         notes=[("h", 56.25, 3.6, 6.4, "阳线实体中点"),
                ("p", 5, 54.6, "收盘破中点", 1.1, -4)]),
]))

F.append(("2-3-piercing-line.png", "刺透形态", "下跌趋势中：阴线之后，阳线低开且收盘上穿阴线实体中点", [
    dict(name=None, tag=("看涨反转", "bull"),
         ctx=ctx_down(4, 62, 46),
         pat=[(46.5, 47.2, 41, 41.8), (38.5, 45.6, 37.9, 44.9)],
         post="up", post_label="看涨",
         notes=[("h", 44.15, 3.6, 6.4, "阴线实体中点"),
                ("p", 5, 45, "收盘穿中点", 1.1, 4)]),
]))

F.append(("2-4-harami.png", "孕线", "后一根 K 线的实体完全包裹前一根 K 线的实体，且二者颜色相反", [
    dict(name="看涨孕线（下跌趋势中）", tag=("看涨反转", "bull"),
         ctx=ctx_down(3, 60, 46),
         pat=[(47, 47.7, 38.5, 39.2), (41.5, 44, 40.7, 43.3)],
         post="up", post_label="看涨",
         notes=[("p", 4, 38.8, "大阴线", -1.2, -3.5), ("p", 5, 44.2, "实体被包含", 1.0, 3.5)]),
    dict(name="看跌孕线（上涨趋势中）", tag=("看跌反转", "bear"),
         ctx=ctx_up(3, 40, 56),
         pat=[(54, 61.5, 53.4, 60.8), (58.5, 59.2, 55.6, 56.3)],
         post="down", post_label="看跌",
         notes=[("p", 4, 61.7, "大阳线", -1.2, 3.5), ("p", 5, 55.4, "实体被包含", 1.0, -3.5)]),
]))

F.append(("2-5-cross-harami.png", "十字孕线", "被包裹的是一个十字线，多空转折意味更强", [
    dict(name="看涨十字孕线（下跌趋势中）", tag=("看涨反转·更强", "bull"),
         ctx=ctx_down(3, 60, 46),
         pat=[(47, 47.7, 38.5, 39.2), (42.5, 43.8, 41.2, 42.5)],
         post="up", post_label="看涨",
         notes=[("p", 5, 44, "十字被包含", 1.0, 3.5)]),
    dict(name="看跌十字孕线（上涨趋势中）", tag=("看跌反转·更强", "bear"),
         ctx=ctx_up(3, 40, 56),
         pat=[(54, 61.5, 53.4, 60.8), (58, 59.3, 56.7, 58)],
         post="down", post_label="看跌",
         notes=[("p", 5, 59.5, "十字被包含", 1.0, 3.5)]),
]))

F.append(("2-6-flat-top.png", "平头顶部形态", "两根 K 线最高点相同，前阳后阴", [
    dict(name=None, tag=("看跌反转", "bear"),
         ctx=ctx_up(4, 40, 55),
         pat=[(54.5, 62.4, 54, 61.6), (61.2, 62.4, 57, 57.8)],
         post="down", post_label="看跌",
         notes=[("h", 62.4, 3.7, 6.5, "相同高点")]),
]))

F.append(("2-7-flat-bottom.png", "平头底部形态", "两根 K 线最低点相同，前阴后阳", [
    dict(name=None, tag=("看涨反转", "bull"),
         ctx=ctx_down(4, 60, 45),
         pat=[(45.5, 46.2, 37.6, 38.4), (38.2, 46, 37.6, 45.3)],
         post="up", post_label="看涨",
         notes=[("h", 37.6, 3.7, 6.5, "相同低点")]),
]))

F.append(("2-8-upside-gap-two-crows.png", "向上跳空两只乌鸦", "上涨趋势中：阳线之后出现两根跳空高开的阴线", [
    dict(name=None, tag=("看跌反转", "bear"),
         ctx=ctx_up(4, 36, 50),
         pat=[(49.5, 55.9, 49, 55), (60.4, 60.9, 58.5, 59.1), (61.6, 62.2, 58.6, 58.7)],
         post="down", post_label="看跌",
         notes=[("w", 4, 6, 55.9, 58.5, "跳空窗口")]),
]))

F.append(("2-9-meeting-lines.png", "约会线形态", "前后两根颜色相反，且具有相同的收盘价", [
    dict(name="看跌约会线（前阳后阴）", tag=("看跌反转", "bear"),
         ctx=ctx_up(3, 40, 55),
         pat=[(54.5, 61, 54, 60.3), (63.5, 64, 59.5, 60.3)],
         post="down", post_label="看跌",
         notes=[("h", 60.3, 3.7, 6.2, "相同收盘价")]),
    dict(name="看涨约会线（前阴后阳）", tag=("看涨反转", "bull"),
         ctx=ctx_down(3, 60, 45),
         pat=[(45.5, 46, 39.5, 40), (37, 40.8, 36.4, 40)],
         post="up", post_label="看涨",
         notes=[("h", 40, 3.7, 6.2, "相同收盘价")]),
]))

F.append(("2-10-separating-lines.png", "分手线形态", "前后两根颜色相反，且具有相同的开盘价", [
    dict(name="看跌分手线（前阳后阴）", tag=("看跌持续", "bear"),
         ctx=ctx_down(3, 58, 47),
         pat=[(46.5, 53.5, 46, 52.8), (46.5, 47, 38, 38.8)],
         post="down", post_label="持续看跌",
         notes=[("h", 46.5, 3.7, 6.2, "相同开盘价")]),
    dict(name="看涨分手线（前阴后阳）", tag=("看涨持续", "bull"),
         ctx=ctx_up(3, 42, 53),
         pat=[(53.5, 54, 46.5, 47.2), (53.5, 61.5, 53, 60.8)],
         post="up", post_label="持续看涨",
         notes=[("h", 53.5, 3.7, 6.2, "相同开盘价")]),
]))

F.append(("2-11-upside-gap-side-by-side.png", "向上跳空并列阴阳线", "向上跳空的阳线之后跟随阴线，且窗口未被回补", [
    dict(name=None, tag=("看涨持续", "bull"),
         ctx=[(48, 49.2, 46.8, 47.4), (44, 46.5, 43.5, 46), (40, 42.5, 39.6, 42)],
         pat=[(50.8, 57.2, 50.4, 56.6), (56, 56.5, 50.9, 51.4)],
         post="up", post_label="持续看涨",
         notes=[("w", 2, 5, 49.2, 50.4, "窗口未回补")]),
]))

F.append(("2-12-downside-gap-side-by-side.png", "向下跳空并列阴阳线", "向下跳空的阴线之后跟随阳线，且窗口未被回补", [
    dict(name=None, tag=("看跌持续", "bear"),
         ctx=[(52, 53, 49, 50), (50.5, 51.4, 48.6, 49), (49.3, 50, 47.5, 48)],
         pat=[(46.2, 46.6, 39.8, 40.5), (40.8, 45.9, 40.2, 45.3)],
         post="down", post_label="持续看跌",
         notes=[("w", 2, 5, 46.6, 47.5, "窗口未回补")]),
]))

# ============ 3. 三根 K 线 ============
F.append(("3-1-morning-star.png", "启明星形态", "阴线 → 向下跳空的小实体星线 → 阳线收复失地", [
    dict(name=None, tag=("看涨反转", "bull"),
         ctx=ctx_down(3, 60, 50),
         pat=[(50.5, 51.2, 39.5, 41.3), (37.8, 39, 36.4, 37), (39, 48.5, 38.2, 47.8)],
         post="up", post_label="看涨",
         notes=[("t", (3, 39.5), (5, 38.2), "支撑线"),
                ("p", 4, 36.8, "星线", -1.1, -3.5)]),
]))

F.append(("3-2-morning-doji-star.png", "十字启明星形态", "中间的星线是十字线，看涨信号更强", [
    dict(name=None, tag=("看涨反转·更强", "bull"),
         ctx=ctx_down(3, 60, 50),
         pat=[(50.5, 51.2, 39.5, 41.3), (37, 38.4, 35.8, 37), (39, 48.5, 38.2, 47.8)],
         post="up", post_label="看涨",
         notes=[("t", (3, 39.5), (5, 38.2), "支撑线"),
                ("p", 4, 36.2, "十字星线", -1.3, -3.5)]),
]))

F.append(("3-3-abandoned-baby-bottom.png", "弃婴底部形态", "十字启明星中，中间的十字线两侧均跳空，十分罕见", [
    dict(name=None, tag=("看涨反转·罕见", "bull"),
         ctx=ctx_down(3, 62, 52),
         pat=[(52.5, 53.2, 41.5, 42.3), (36.8, 37.6, 36, 36.8), (40.5, 48.6, 40.2, 47.9)],
         post="up", post_label="看涨",
         notes=[("w", 3, 4, 37.6, 41.5, "跳空"),
                ("w", 4, 5, 37.6, 40.2, "跳空"),
                ("p", 4, 35.7, "十字线", -1.2, -3.5)]),
]))

F.append(("3-4-evening-star.png", "黄昏星形态", "阳线 → 向上跳空的小实体星线 → 阴线收回失地", [
    dict(name=None, tag=("看跌反转", "bear"),
         ctx=ctx_up(3, 40, 50),
         pat=[(49.5, 58.8, 49, 58), (61.5, 62.6, 60.3, 62.2), (60.5, 61, 50.8, 51.6)],
         post="down", post_label="看跌",
         notes=[("t", (3, 58.8), (5, 61), "压力线"),
                ("p", 4, 62.5, "星线", 1.0, 3.5)]),
]))

F.append(("3-5-evening-doji-star.png", "十字黄昏星形态", "中间的星线是十字线，看跌信号更强", [
    dict(name=None, tag=("看跌反转·更强", "bear"),
         ctx=ctx_up(3, 40, 50),
         pat=[(49.5, 58.8, 49, 58), (61.8, 62.8, 60.8, 61.8), (60.5, 61, 50.8, 51.6)],
         post="down", post_label="看跌",
         notes=[("t", (3, 58.8), (5, 61), "压力线"),
                ("p", 4, 62.7, "十字星线", 1.0, 3.5)]),
]))

F.append(("3-6-abandoned-baby-top.png", "弃婴顶部形态", "十字黄昏星中，中间的十字线两侧均跳空，十分罕见", [
    dict(name=None, tag=("看跌反转·罕见", "bear"),
         ctx=ctx_up(3, 40, 50),
         pat=[(49.5, 59.5, 49, 58.6), (63.8, 64.9, 63.0, 63.8), (60.5, 61.0, 50.7, 51.5)],
         post="down", post_label="看跌",
         notes=[("w", 3, 4, 59.5, 63.0, "跳空"),
                ("w", 4, 5, 61.0, 63.0, "跳空"),
                ("p", 4, 64.7, "十字线", 1.0, 3.5)]),
]))

F.append(("3-7-three-crows.png", "三只乌鸦", "上涨顶部接连出现三根依次走低的阴线", [
    dict(name=None, tag=("看跌反转", "bear"),
         ctx=ctx_up(4, 38, 56),
         pat=[(57, 57.7, 50.4, 51.2), (55.5, 56, 48.5, 49.3), (53.8, 54.3, 46.6, 47.4)],
         post="down", post_label="看跌",
         notes=[("t", (4, 57.7), (6, 54.3), "高点降低")]),
]))

F.append(("3-8-three-white-soldiers.png", "白三兵", "下跌底部接连出现三根依次走高的阳线", [
    dict(name=None, tag=("看涨反转", "bull"),
         ctx=ctx_down(4, 62, 44),
         pat=[(43.5, 50.2, 43, 49.4), (48.6, 55.3, 48.1, 54.5), (53.8, 60.5, 53.3, 59.7)],
         post="up", post_label="看涨",
         notes=[("t", (4, 43), (6, 53.3), "低点抬高")]),
]))

F.append(("3-9-rising-three-methods.png", "上升三法", "大阳线 + 三根回落的小阴线 + 收盘创新高的阳线", [
    dict(name=None, tag=("看涨持续", "bull"),
         ctx=ctx_up(2, 40, 46),
         pat=[(45.5, 57, 45, 56.2), (54, 54.5, 51.6, 52.2), (53, 53.4, 50.8, 51.4),
              (51.8, 52.3, 49.8, 50.4), (51, 59.5, 50.6, 58.8)],
         post="up", post_label="持续看涨",
         notes=[("p", 4, 56.4, "大阳线", -1.3, 3.5), ("p", 5, 50, "不破大阳线开盘", 0.6, -4)]),
]))

F.append(("3-10-falling-three-methods.png", "下降三法", "大阴线 + 三根反弹的小阳线 + 收盘创新低的阴线", [
    dict(name=None, tag=("看跌持续", "bear"),
         ctx=ctx_down(2, 60, 54),
         pat=[(54.5, 54.9, 43, 43.8), (46, 48.4, 45.6, 47.8), (47.5, 49.3, 46.2, 48.6),
              (48.9, 50.6, 47.8, 50), (49.5, 50, 40.5, 41.3)],
         post="down", post_label="持续看跌",
         notes=[("p", 4, 43.6, "大阴线", -1.3, -3.5), ("p", 5, 50.8, "不破大阴线开盘", 0.6, 4)]),
]))

F.append(("3-11-tri-star-top.png", "三星顶部形态", "三个十字线，中间的最高，构成顶部结构", [
    dict(name=None, tag=("看跌反转", "bear"),
         ctx=ctx_up(3, 40, 50),
         pat=[(51.5, 52.6, 50.4, 51.5), (56, 57.2, 54.8, 56), (50.5, 51.6, 49.4, 50.5)],
         post="down", post_label="看跌",
         notes=[("p", 5, 57, "中间最高", 1.0, 3.5)]),
]))

F.append(("3-12-tri-star-bottom.png", "三星底部形态", "三个十字线，中间的最低，构成底部结构", [
    dict(name=None, tag=("看涨反转", "bull"),
         ctx=ctx_down(3, 60, 50),
         pat=[(48.5, 49.6, 47.4, 48.5), (44, 45.1, 42.9, 44), (48, 49.1, 47, 48)],
         post="up", post_label="看涨",
         notes=[("p", 5, 42.8, "中间最低", 1.0, -3.5)]),
]))

# ============ 4. 一大堆 K 线 ============
m1 = [(46, 48.6, 45.4, 48), (48.5, 52, 48, 51.5), (51.8, 56.5, 51.3, 56)]
three_mountains = [
    (55.8, 62, 55.3, 61.5), (62.5, 68.2, 61, 63), (63.5, 64.2, 58.6, 59.2),
    (59, 61.5, 58.5, 61), (60.8, 66, 60.3, 65.5), (65.8, 68.6, 64, 64.8),
    (65.2, 66, 60.5, 61), (60.8, 63.5, 60.3, 63), (62.8, 67, 62.3, 66.5),
    (66.8, 68.3, 64.4, 65), (64.8, 65.5, 59.5, 60), (60.2, 60.8, 54, 54.7),
]
three_buddha = [
    (55.8, 62, 55.3, 61.5), (62.5, 66, 61, 63), (63.5, 64.2, 58.6, 59.2),
    (59, 64.8, 58.5, 64.3), (64.6, 72.5, 63.5, 64.8), (65.2, 66, 59.8, 60.4),
    (60.2, 64.5, 59.7, 64), (63.8, 66.2, 62, 62.6), (63, 63.8, 57.5, 58),
    (58.2, 59, 52.5, 53.2),
]
rounding_top = [
    (46.3, 50.5, 46, 50), (50.2, 53.8, 49.8, 53.4), (53.6, 56.8, 53.2, 56.2),
    (56.4, 59.2, 56, 58.6), (58.8, 61.4, 58.4, 60.6), (60.8, 62.6, 60, 61),
    (61.2, 61.8, 58.8, 59.2), (59.6, 60.2, 56.4, 57), (57.4, 58, 53.6, 54.2),
    (54.6, 55.2, 50.8, 51.4), (48.5, 49.4, 42.5, 43.3),
]
tower_top = [
    (52.3, 64.5, 52, 64), (63.8, 64.6, 56.5, 57.2), (57.6, 58.4, 49, 49.8),
    (50.2, 51, 44, 44.8),
]

F.append(("4-1-three-mountains.png", "三山形态", "K 线构成三座高度相近的山峰，三次冲击同一水平受阻", [
    dict(name=None, tag=("看跌反转", "bear"),
         ctx=m1, pat=three_mountains,
         post="down", post_label="看跌",
         notes=[("h", 68.35, 3, 12.6, "三次受阻")]),
]))
F.append(("4-2-three-buddha-top.png", "三尊顶部形态", "中间的山峰比两边高（头肩顶），看跌信号更强烈", [
    dict(name=None, tag=("看跌反转·更强", "bear"),
         ctx=m1, pat=three_buddha,
         post="down", post_label="看跌",
         notes=[("h", 66.1, 3, 10.6, "两肩高点"), ("h", 58.6, 3, 10.6, "颈线")]),
]))
F.append(("4-3-three-river-bottom.png", "三川底部形态", "K 线构成三座深度相近的山谷，三次探底获得支撑", [
    dict(name=None, tag=("看涨反转", "bull"),
         ctx=mirror(m1), pat=mirror(three_mountains),
         post="up", post_label="看涨",
         notes=[("h", 39.65, 3, 12.6, "三次获支撑")]),
]))
F.append(("4-4-inverted-three-buddha.png", "倒三尊底部形态", "中间的山谷比两边深（头肩底），看涨信号更强烈", [
    dict(name=None, tag=("看涨反转·更强", "bull"),
         ctx=mirror(m1), pat=mirror(three_buddha),
         post="up", post_label="看涨",
         notes=[("h", 41.9, 3, 10.6, "两肩低点"), ("h", 49.4, 3, 10.6, "颈线")]),
]))
F.append(("4-5-rounding-top.png", "圆形顶部形态", "K 线缓缓爬升后弯头向下，最后出现向下跳空的阴线", [
    dict(name=None, tag=("看跌反转", "bear"),
         ctx=[(40, 43.5, 39.5, 43), (42.8, 47, 42.3, 46.5)], pat=rounding_top,
         post="down", post_label="看跌",
         notes=[("w", 10, 11, 49.4, 50.8, "向下跳空")]),
]))
F.append(("4-6-fry-pan-bottom.png", "平底锅底部形态", "K 线缓缓下滑后弯头向上，最后出现向上跳空的阳线", [
    dict(name=None, tag=("看涨反转", "bull"),
         ctx=mirror([(40, 43.5, 39.5, 43), (42.8, 47, 42.3, 46.5)]), pat=mirror(rounding_top),
         post="up", post_label="看涨",
         notes=[("w", 10, 11, 57.2, 58.6, "向上跳空")]),
]))
F.append(("4-7-tower-top.png", "塔形顶部形态", "高位先是耸立的大阳线（塔尖），随后出现大阴线倾泻而下", [
    dict(name=None, tag=("看跌反转", "bear"),
         ctx=[(40, 44, 39.5, 43.5), (43.8, 48, 43.3, 47.5), (48.2, 52.5, 47.8, 52)],
         pat=tower_top,
         post="down", post_label="看跌",
         notes=[("p", 3, 64.3, "大阳线", -1.4, 3), ("p", 4, 56.3, "大阴线", 1.0, 3)]),
]))
F.append(("4-8-tower-bottom.png", "塔形底部形态", "低位先是耸立的大阴线（塔尖），随后出现大阳线拔地而起", [
    dict(name=None, tag=("看涨反转", "bull"),
         ctx=mirror([(40, 44, 39.5, 43.5), (43.8, 48, 43.3, 47.5), (48.2, 52.5, 47.8, 52)]),
         pat=mirror(tower_top),
         post="up", post_label="看涨",
         notes=[("p", 3, 43.7, "大阴线", -1.4, -3), ("p", 4, 51.7, "大阳线", 1.0, -3)]),
]))


# ---------------------------------------------------------------- 渲染引擎
def check(candles):
    for o, h, l, c in candles:
        assert h >= max(o, c) - 1e-6 and l <= min(o, c) + 1e-6 and h >= l, f"非法蜡烛 {o, h, l, c}"


def draw_panel(ax, p):
    ctx, pat = p["ctx"], p["pat"]
    check(ctx); check(pat)
    candles = ctx + pat
    n = len(candles)
    allv = [v for o, h, l, c in candles for v in (o, h, l, c)]
    ymin, ymax = min(allv), max(allv)
    rng = ymax - ymin
    minbody = rng * 0.006
    ax.set_xlim(-0.9, n - 1 + 2.5)
    ax.set_ylim(ymin - rng * 0.07, ymax + rng * 0.10)

    x0p = len(ctx)
    if 0 < len(pat) <= 6:  # 形态高亮带
        ax.axvspan(x0p - 0.45, n - 1 + 0.45, color=HIGHLIGHT, alpha=0.75, zorder=0.5)

    for i, (o, h, l, c) in enumerate(candles):
        isc = i < x0p
        face = CTX_FACE if isc else (UP_FACE if c >= o else DN_FACE)
        edge = CTX_EDGE if isc else (UP_EDGE if c >= o else DN_EDGE)
        ax.plot([i, i], [l, h], color=edge, lw=1.5, zorder=3, solid_capstyle="round")
        top, bot = max(o, c), min(o, c)
        hgt = max(top - bot, minbody)
        ax.add_patch(Rectangle((i - 0.31, bot), 0.62, hgt, facecolor=face,
                               edgecolor=edge, lw=1.2, zorder=3.1))

    # 前期趋势箭头
    if ctx:
        falling = ctx[-1][3] < ctx[0][0]
        ax.annotate("", xy=(x0p - 0.8, ctx[-1][3]), xytext=(0.2, ctx[0][1]),
                    arrowprops=dict(arrowstyle="-|>", color="#9aa4af", lw=1.8,
                                    connectionstyle=f"arc3,rad={0.22 if falling else -0.22}"),
                    zorder=2)
        mx, my = (0.2 + x0p - 0.8) / 2, (ctx[0][1] + ctx[-1][3]) / 2
        ax.text(mx - 0.1, my + (2.6 if falling else -3.4),
                "下跌趋势" if falling else "上涨趋势", fontsize=9, color=GUIDE, ha="center")

    # 后续预期箭头
    post = p.get("post")
    lc = pat[-1][3]
    if post in ("up", "down", "both"):
        col = BULL if post == "up" else BEAR
        if post == "both":
            for d, cc, lb in ((1, BULL, "看涨"), (-1, BEAR, "看跌")):
                ax.annotate("", xy=(n - 1 + 1.45, lc + d * rng * 0.16),
                            xytext=(n - 1 + 0.4, lc),
                            arrowprops=dict(arrowstyle="-|>", color=cc, lw=1.9,
                                            linestyle=(0, (5, 3))), zorder=4)
                ax.text(n - 1 + 1.55, lc + d * rng * 0.16, lb, fontsize=10,
                        color=cc, fontweight="bold", ha="left", va="center")
        else:
            d = 1 if post == "up" else -1
            ax.annotate("", xy=(n - 1 + 1.7, lc + d * rng * 0.20),
                        xytext=(n - 1 + 0.45, lc),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=2,
                                        linestyle=(0, (5, 3))), zorder=4)
            ax.text(n - 1 + 1.8, lc + d * rng * 0.20, p.get("post_label", "看涨" if post == "up" else "看跌"),
                    fontsize=10.5, color=col, fontweight="bold", ha="left", va="center")

    # 标注
    for note in p.get("notes", []):
        kind = note[0]
        if kind == "p":
            _, x, y, txt, dx, dy = note
            ax.annotate(txt, xy=(x, y), xytext=(x + dx, y + dy),
                        fontsize=9, color="#4a5560",
                        ha="left" if dx > 0 else "right",
                        va="center",
                        arrowprops=dict(arrowstyle="->", color=GUIDE, lw=1.1), zorder=5)
        elif kind == "h":
            _, y, a, b, txt = note
            ax.hlines(y, a, b, color=GUIDE, linestyles=(0, (5, 4)), lw=1.2, zorder=2.5)
            ax.text(b + 0.08, y, txt, fontsize=8.8, color="#4a5560", ha="left", va="center")
        elif kind == "w":
            _, a, b, y0, y1, txt = note
            ax.add_patch(Rectangle((a + 0.34, y0), b - a - 0.34, y1 - y0,
                                   facecolor="#d8e9fb", alpha=0.65, edgecolor="#7fa8d9",
                                   linewidth=1, linestyle=(0, (4, 3)), zorder=1.6))
            ax.text((a + b) / 2, (y0 + y1) / 2, txt, fontsize=8.2, color="#3d6a99",
                    ha="center", va="center", zorder=5)
        elif kind == "t":
            _, p1, p2, txt = note
            ax.plot([p1[0] - 0.5, p2[0] + 0.9], [p1[1], p2[1]], color=GUIDE,
                    linestyle=(0, (5, 4)), lw=1.3, zorder=2.5)
            ax.text(p2[0] + 1.0, p2[1], txt, fontsize=8.8, color="#4a5560",
                    ha="left", va="center")

    # 面板小标题 + 信号标签
    if p.get("name"):
        ax.set_title(p["name"], loc="left", fontsize=12, fontweight="bold",
                     color=INK, pad=30)
    tag = p.get("tag")
    if tag:
        fc, ec, tc = TAG_STYLE[tag[1]]
        ax.text(0.995, 1.045 if p.get("name") else 1.03, tag[0],
                transform=ax.transAxes, ha="right", va="bottom", fontsize=9.5,
                color=tc, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.35", fc=fc, ec=ec, lw=1.1))

    ax.grid(axis="y", color="#eef1f5", lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


LEGEND = [Patch(fc=UP_FACE, ec=UP_EDGE, label="阳线（收＞开）"),
          Patch(fc=DN_FACE, ec=DN_EDGE, label="阴线（收＜开）"),
          Patch(fc=CTX_FACE, ec=CTX_EDGE, label="前期走势")]


def render(fname, title, sub, panels):
    two = len(panels) == 2
    fig, axes = plt.subplots(1, 2 if two else 1, figsize=(11 if two else 9, 4.8))
    fig.suptitle(title, x=0.012, y=0.985, ha="left", fontsize=15.5,
                 fontweight="bold", color=INK)
    fig.text(0.014, 0.912, sub, fontsize=10, color=SUB)
    fig.subplots_adjust(top=0.76, bottom=0.105, left=0.02, right=0.985, wspace=0.10)
    for ax, p in zip(np_axes(axes), panels):
        draw_panel(ax, p)
    fig.legend(handles=LEGEND, loc="lower center", ncol=3, frameon=False,
               fontsize=8.8, handlelength=1.2, columnspacing=1.6)
    fig.savefig(os.path.join(OUT, fname), dpi=150, facecolor="white")
    plt.close(fig)
    print("saved", fname)


def np_axes(axes):
    return axes if hasattr(axes, "__iter__") else [axes]


if __name__ == "__main__":
    for fname, title, sub, panels in F:
        render(fname, title, sub, panels)
    print(f"\n共生成 {len(F)} 张图")
