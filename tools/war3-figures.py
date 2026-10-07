#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成《让魔兽再次伟大》(war3-website.md) 的全部配图。

运行：python3 tools/war3-figures.py   （依赖 matplotlib，输出到 source/images/war3/）
文章引用 URL：https://lucifer.ren/blog/images/war3/<文件名>

图片清单：
1. xp-tables.png        经验值三张表可视化（3.1 节）
2. map-pool.png         S12 地图池矩阵：体量 x 对 ORC 友好度（2.2 节）
3. ban-flow.png         ban 图三问决策流程（2.2 节）
4. apm-pyramid.png      操作优先级金字塔（6.2 节）
5. population-50.png    50/64 人口构成对比 + 维护费曲线（8.6 节）
6. plan-90d.png         90 天训练计划甘特图（11.1 节）
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon

plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "source", "images", "war3")
os.makedirs(OUT, exist_ok=True)

INK, SUB, GUIDE = "#2e3a46", "#7b8794", "#8a93a0"
KEEP, BAN, WARN = "#1fa06b", "#e8554e", "#e8a13a"
ACCENT = "#3a6ea5"
PAPER = "#fafbfc"


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("saved", path)


# ---------------------------------------------------------------- 1. 经验值
def fig_xp():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    lv = list(range(1, 11))
    cum = [0, 200, 500, 900, 1400, 2000, 2700, 3500, 4400, 5400]
    ax1.plot(lv, cum, color=ACCENT, lw=2.2, marker="o", ms=5, zorder=3)
    for k, (dx, dy) in ((3, (-4, 12)), (5, (-30, -6)), (6, (-6, 12))):
        ax1.scatter([k], [cum[k - 1]], s=90, color=BAN, zorder=4)
        ax1.annotate(f"{k} 级\n{cum[k-1]} 点", (k, cum[k - 1]),
                     textcoords="offset points", xytext=(dx, dy),
                     ha="right", fontsize=9, color=BAN, zorder=5,
                     bbox=dict(boxstyle="round,pad=0.25", fc="white",
                               ec="none", alpha=.8))
    ax1.set_ylim(0, 5800)
    ax1.set_title("英雄升级所需累计经验（关键等级：3 / 5 / 6）", fontsize=11, color=INK)
    ax1.set_xlabel("英雄等级", color=SUB)
    ax1.set_ylabel("累计经验", color=SUB)
    ax1.set_xticks(lv)
    ax1.grid(axis="y", ls="--", lw=.6, color=GUIDE, alpha=.6)
    for s in ("top", "right"):
        ax1.spines[s].set_visible(False)

    neutral = [20, 30, 40, 60, 80, 120, 160, 240, 320, 400]
    player = [round(x * 1.25) for x in neutral]
    w = .38
    ax2.bar([i - w / 2 for i in lv], neutral, width=w, color=GUIDE, label="中立野怪")
    ax2.bar([i + w / 2 for i in lv], player, width=w, color=ACCENT, label="玩家单位（x1.25）")
    ax2.set_ylim(0, 560)
    ax2.set_title("击杀获取经验：野怪 vs 玩家单位", fontsize=11, color=INK)
    ax2.set_xlabel("单位等级", color=SUB)
    ax2.set_ylabel("单杀经验", color=SUB)
    ax2.set_xticks(lv)
    ax2.legend(frameon=False, fontsize=9)
    ax2.grid(axis="y", ls="--", lw=.6, color=GUIDE, alpha=.6)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)

    fig.tight_layout()
    save(fig, "xp-tables.png")


# ---------------------------------------------------------------- 2. 地图矩阵
def fig_map_pool():
    fig, ax = plt.subplots(figsize=(9, 6))

    # x: 体量（相对值，仅定序）；y: 对 ORC 综合友好度
    maps = [
        # 简称, x, y, 结论, 标注
        ("HF", 1.0, 4.6, KEEP, "84x84 小图\n双分矿可三矿"),
        ("EI", 1.8, 4.4, KEEP, "节奏快\n骚扰往返短"),
        ("TH", 3.0, 3.9, KEEP, "两绿点到 2 级\n对面分矿难开"),
        ("CH", 3.6, 3.6, KEEP, "双温泉+酒馆\n万金油续航好"),
        ("ST", 3.2, 3.1, KEEP, "中央免费矿\n偷矿攻防主题"),
        ("AM", 4.2, 3.3, KEEP, "雇兵营好练\n分矿无尸体克 UD"),
        ("AL", 4.6, 2.2, WARN, "对 NE 明显劣势\n对 HUM/UD 略优"),
        ("TM", 5.6, 1.2, BAN, "大图多矿\n运营族主场"),
    ]
    for name, x, y, c, note in maps:
        ax.scatter([x], [y], s=340, color=c, alpha=.92, zorder=3, edgecolor="white", lw=2)
        ax.text(x, y, name, ha="center", va="center", color="white",
                fontsize=10, fontweight="bold", zorder=4)
        ax.annotate(note, (x, y), textcoords="offset points", xytext=(0, -34),
                    ha="center", fontsize=8, color=SUB)

    ax.axhline(2.45, color=GUIDE, ls="--", lw=1, zorder=1)
    ax.text(6.15, 2.53, "ban 分界（示意）", fontsize=8.5, color=GUIDE, ha="right",
            zorder=5)
    ax.set_xlim(.4, 6.3)
    ax.set_ylim(.4, 5.4)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("地图体量：小 ────────→ 大", color=SUB, fontsize=10)
    ax.set_ylabel("对兽族友好度：低 ────→ 高", color=SUB, fontsize=10)
    ax.set_title("S12 地图池：兽族视角全景（绿=保留  黄=看对位  红=ban）",
                 fontsize=12, color=INK, pad=12)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "map-pool.png")


# ---------------------------------------------------------------- 3. ban 决策流程
def fig_ban_flow():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    def box(x, y, w, h, text, fc, ec, tc=INK, fs=10):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                                    fc=fc, ec=ec, lw=1.4))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, color=tc, linespacing=1.5)

    def arrow(p1, p2, text="", color=SUB):
        ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=14,
                                     color=color, lw=1.4))
        if text:
            mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            ax.text(mx + .12, my, text, fontsize=8.5, color=color)

    box(.2, 5.2, 2.9, 1.1, "问题 1\n放大了最难对位的优势？", "#eef1f5", SUB)
    box(.2, 3.4, 2.9, 1.1, "问题 2\n和兽族内核冲突？\n（大图/易守开矿/拖后期）", "#eef1f5", SUB, fs=9)
    box(.2, 1.6, 2.9, 1.1, "问题 3\n个人 30+ 局胜率最低？", "#eef1f5", SUB)

    box(4.1, 4.6, 2.6, 1.9, "TM\n首选 ban\n大图多矿，运营族主场", "#fdeceb", BAN)
    box(4.1, 2.5, 2.6, 1.5, "AL\n第二 ban（怕 NE 时）\n注意：打 HUM/UD 反而占优", "#fdf3d8", WARN)
    box(4.1, .5, 2.6, 1.3, "HF\n永不 ban\n小图+三矿，拆家主场", "#e5f5ee", KEEP)

    box(7.6, 3.0, 2.2, 2.6, "其余保留\nEI / CH / AM\nST / TH\n练熟即优势", "#f4f7f9", SUB)

    arrow((3.1, 5.75), (4.1, 5.55), "是")
    arrow((1.65, 5.2), (1.65, 4.5))
    arrow((3.1, 3.95), (4.1, 3.35), "是")
    arrow((1.65, 3.4), (1.65, 2.7))
    arrow((3.1, 2.15), (4.1, 1.3), "是")
    arrow((5.4, 4.6), (5.4, 4.0), color=WARN)
    arrow((6.7, 3.25), (7.6, 4.0), "否/已满", color=GUIDE)
    ax.text(5, 6.75, "ban 图三问（按顺序过）", fontsize=12, color=INK, ha="center")
    ax.text(5, .02, "问题 3 的答案需要 30+ 局「图 x 对位」个人数据校准",
            fontsize=8.5, color=GUIDE, ha="center")
    save(fig, "ban-flow.png")


# ---------------------------------------------------------------- 4. 微操金字塔
def fig_pyramid():
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    layers = [
        ("1  英雄保命与关键道具", BAN, .95),
        ("2  点杀与救兵", "#e8854e", .85),
        ("3  关键技能互换（网 / 锤 / 踩地板）", WARN, .75),
        ("4  阵型与拉扯（后排输出 / 前排卡位）", "#9db55c", .65),
        ("5  家里生产不断（兵营 / 人口 / 科技）", "#5aab86", .55),
        ("6  侦察", "#4a9bb0", .45),
    ]
    n = len(layers)
    cx = 5
    for i, (text, color, alpha) in enumerate(layers):
        top_w = 2.6 + i * 1.5
        bot_w = 2.6 + (i + 1) * 1.5
        y0 = n - i - 1
        p = Polygon([(cx - top_w / 2, y0 + .86), (cx + top_w / 2, y0 + .86),
                     (cx + bot_w / 2, y0), (cx - bot_w / 2, y0)],
                    closed=True, fc=color, ec="white", lw=2, alpha=alpha)
        ax.add_patch(p)
        ax.text(cx, y0 + .43, text, ha="center", va="center", fontsize=9.5,
                color="white", fontweight="bold")

    ax.annotate("APM 集中在上两层 = 有效操作", (-1.1, 5.5),
                fontsize=10, color=BAN, ha="left")
    ax.annotate("下两层抽空做", (11.6, 1.2), fontsize=10, color="#5a6572", ha="left")
    ax.annotate("无脑框选点地板 = 无效 APM", (11.6, .6), fontsize=10,
                color=GUIDE, ha="left", style="italic")
    ax.set_xlim(-1.2, 15.8)
    ax.set_ylim(-.3, 5.8)
    ax.axis("off")
    ax.set_title("操作优先级金字塔：每次切屏先问「现在最要命的事是什么」",
                 fontsize=12, color=INK)
    save(fig, "apm-pyramid.png")


# ---------------------------------------------------------------- 5. 人口构成 + 维护费
def fig_population():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6.2),
                                   gridspec_kw={"height_ratios": [2, 1]})

    def bar(ax, y, parts, title):
        left = 0
        for label, val, color in parts:
            ax.barh([y], [val], left=left, color=color, edgecolor="white", lw=1.2)
            if val >= 8:
                ax.text(left + val / 2, y, f"{label}\n{val}", ha="center",
                        va="center", fontsize=8.5, color="white")
            elif val >= 4:
                ax.text(left + val / 2, y, f"{label} {val}", ha="center",
                        va="center", fontsize=7.5, color="white")
            left += val
        ax.text(-1, y, title, ha="right", va="center", fontsize=10, color=INK)

    bar(ax1, 1, [
        ("英雄x2", 10, "#c13a34"), ("狼骑x3", 9, "#3a6ea5"), ("大Gx3", 9, "#7a8a4a"),
        ("白牛x3", 9, "#9a6fb0"), ("苦工", 12, "#8a93a0"),
    ], "己方 ORC\n≈50 总人口")
    bar(ax1, 0, [
        ("英雄x2", 10, "#c13a34"), ("火枪x6", 18, "#3a6ea5"), ("男巫x4", 8, "#4a9bb0"),
        ("女巫x3", 6, "#9a6fb0"), ("步兵x3", 6, "#7a8a4a"), ("农民", 16, "#8a93a0"),
    ], "对面 HUM\n≈64 总人口")

    for x in (50, 80):
        ax1.axvline(x, color=BAN, ls="--", lw=1.2)
        ax1.text(x + .8, 1.62, f"{x}", color=BAN, fontsize=9)
    ax1.text(66, .62, "已进低维护\n（采金 7/10）", fontsize=8.5, color=SUB)
    ax1.set_xlim(0, 84)
    ax1.set_ylim(-.6, 2.1)
    ax1.set_yticks([])
    ax1.set_xticks([])
    for s in ax1.spines.values():
        s.set_visible(False)
    ax1.set_title("一眼估算：把对面部队折成人口，和自己的「标准 50」比大小",
                  fontsize=12, color=INK)
    ax1.text(-1, -.45, "公式：作战人口 = 总人口 - 农民；差 10 以上别硬接正面",
             fontsize=9, color=SUB, ha="right")

    zones = [(0, 50, "无维护 10/10", KEEP), (50, 80, "低维护 7/10", WARN),
             (80, 100, "高维护 4/10", BAN)]
    for x0, x1, label, color in zones:
        ax2.axvspan(x0, x1, color=color, alpha=.14)
        ax2.text((x0 + x1) / 2, 92, label, ha="center", fontsize=9.5, color=color)
    ax2.plot([0, 50, 50.01, 80, 80.01, 100], [100, 100, 70, 70, 40, 40],
             color=ACCENT, lw=2.2)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 118)
    ax2.set_xlabel("总人口", color=SUB)
    ax2.set_ylabel("采金效率 %", color=SUB)
    ax2.set_xticks([0, 50, 80, 100])
    ax2.grid(axis="y", ls="--", lw=.6, color=GUIDE, alpha=.5)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    ax2.set_title("维护费：40 / 80 是两道坎——破人口前先把钱花掉", fontsize=11, color=INK)

    fig.tight_layout()
    save(fig, "population-50.png")


# ---------------------------------------------------------------- 6. 90 天甘特图
def fig_plan():
    fig, ax = plt.subplots(figsize=(10, 4.2))
    phases = [
        ("第 0 周  准备", 0, 1, "#8a93a0", "定主族 / 改键 / 跑图建卡 / 背经验表"),
        ("第 1-4 周  一招鲜", 1, 4, ACCENT, "主线战术练成肌肉记忆，上中上分段"),
        ("第 5-8 周  补短板", 5, 4, WARN, "骚扰 / 侦查 / 应变专项 + 第二套战术"),
        ("第 9-12 周  冲分", 9, 4, KEEP, "胜率 60% 持续上分，只打值得打的局"),
    ]
    for i, (name, start, dur, color, goal) in enumerate(phases):
        y = len(phases) - 1 - i
        ax.barh([y], [dur], left=start, height=.58, color=color, alpha=.9)
        if dur >= 2:
            ax.text(start + .12, y, name, va="center", fontsize=10,
                    color="white", fontweight="bold")
            ax.text(start + dur + .25, y, goal, va="center", fontsize=9, color=SUB)
        else:
            ax.text(start + dur + .25, y, f"{name}：{goal}", va="center",
                    fontsize=9, color=INK)
    ax.set_xlim(0, 17.5)
    ax.set_ylim(-.9, 3.6)
    ax.set_yticks([])
    ax.set_xticks(range(0, 14, 2))
    ax.set_xticklabels([f"第 {w} 周" for w in range(0, 14, 2)], fontsize=9)
    ax.grid(axis="x", ls="--", lw=.6, color=GUIDE, alpha=.5)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_title("90 天训练计划：每周 10-12 小时，达不到就拉长周期、比例不变",
                 fontsize=12, color=INK)
    ax.text(13.1, -.55, "每阶段结束做一次大复盘：输因分类没变化 = 专项没练对",
            fontsize=9, color=SUB, ha="right")
    save(fig, "plan-90d.png")


# ---------------------------------------------------------------- 7. 练级路线示意图
# 说明：坐标为「相对方位示意」，非游戏内精确坐标；营地颜色对应文中 黄点/绿点/红点 记号。
# 如需修正某张图的点位，直接改下面 MAPS 里的 (x, y) 即可，0-10 为画布坐标。
def draw_route_map(key, title, elements, routes, filename, note=""):
    fig, ax = plt.subplots(figsize=(7.2, 6.4))

    ax.add_patch(FancyBboxPatch((.25, .25), 9.5, 9.5, boxstyle="round,pad=0.25",
                                fc="#f0ead9", ec="#d8cfb8", lw=1.5, zorder=0))

    kind_style = {
        "spawn_me": ("#3a6ea5", "s", 340),
        "spawn_op": ("#c13a34", "s", 340),
        "mine": ("#e8c13a", "o", 300),
        "camp_g": ("#1fa06b", "o", 300),
        "camp_y": ("#e8a13a", "o", 300),
        "camp_r": ("#e8554e", "o", 300),
        "shop": ("#4a9bb0", "s", 240),
        "lab": ("#4a9bb0", "s", 240),
        "merc": ("#4a9bb0", "s", 240),
        "tavern": ("#4a9bb0", "s", 240),
        "fountain": ("#2a9d8f", "P", 280),
    }
    legend_used = set()

    # 路线画在点位下层、陆地上层
    for pts, color, ls, _label in routes:
        for i in range(len(pts) - 1):
            ax.add_patch(FancyArrowPatch(pts[i], pts[i + 1],
                                         arrowstyle="-|>", mutation_scale=16,
                                         color=color, lw=2.2, ls=ls, zorder=2,
                                         connectionstyle="arc3,rad=0.12",
                                         shrinkA=10, shrinkB=10))

    for kind, x, y, label in elements:
        color, marker, size = kind_style[kind]
        legend_used.add(kind)
        ax.scatter([x], [y], s=size, color=color, edgecolor="white", lw=1.6,
                   marker=marker, zorder=4)
        inside = (len(label) <= 3 and label.isascii()) or len(label) <= 2
        if kind.startswith("camp") and inside:
            ax.text(x, y, label, ha="center", va="center", fontsize=6.5,
                    color="white", fontweight="bold", zorder=5)
        elif label:
            dy = -0.46 if y > 5 else 0.46
            va = "top" if y > 5 else "bottom"
            ax.text(x, y + dy * 0.55, label, ha="center", va=va, fontsize=7.5,
                    color=INK, zorder=5,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none",
                              alpha=.75))

    # 序号徽章：按路线左右错开，避免共用节点上红蓝徽章重叠
    badge_offs = [(-0.42, 0.12), (0.42, -0.12), (-0.42, -0.12)]
    for ri, (pts, color, ls, _label) in enumerate(routes):
        ox, oy = badge_offs[ri % len(badge_offs)]
        for i, (x, y) in enumerate(pts):
            ax.scatter([x + ox], [y + oy], s=200, color="white",
                       edgecolor=color, lw=1.8, zorder=6)
            ax.text(x + ox, y + oy, str(i + 1), ha="center", va="center",
                    fontsize=8, color=color, fontweight="bold", zorder=7)

    handles = []
    from matplotlib.lines import Line2D
    names = {"spawn_me": "己方出生", "spawn_op": "对面出生", "mine": "金矿",
             "camp_g": "绿点", "camp_y": "黄点", "camp_r": "红点",
             "shop": "商店", "lab": "地精实验室", "merc": "雇佣兵营地",
             "tavern": "酒馆", "fountain": "温泉"}
    order = ["spawn_me", "spawn_op", "mine", "camp_g", "camp_y", "camp_r",
             "shop", "lab", "merc", "tavern", "fountain"]
    for k in order:
        if k in legend_used:
            color, marker, _ = kind_style[k]
            handles.append(Line2D([], [], color=color, marker=marker, ls="",
                                  markersize=8, label=names[k]))
    if len(routes) > 1:
        handles.append(Line2D([], [], color=routes[0][1], lw=2.2,
                              label=routes[0][3]))
        handles.append(Line2D([], [], color=routes[1][1], lw=2.2, ls="--",
                              label=routes[1][3]))
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1.0),
              fontsize=7.5, frameon=False)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#d8cfb8")
    ax.set_title(title, fontsize=11.5, color=INK, pad=10)
    if note:
        ax.text(5, -.35, note, ha="center", fontsize=8, color=SUB)
    save(fig, filename)


def fig_routes():
    """真实地图底图 + 营地标注（组合/累计XP/掉落）+ 序号路线箭头。

    坐标 = Liquipedia 底图像素坐标（512 基准），图上红X/蓝X为对面/己方出生、
    黄圆=金矿、房子=中立建筑（均为底图自带）。营地圆点与文字为标注层：
    XP 口径 = 打完该营地后的累计经验（换算自文内实测等级节点）；
    标 ? 的建筑对应关系与「待补」数据请按实测更新后重跑本脚本。
    """
    from matplotlib.lines import Line2D

    BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "source", "images", "war3", "base")
    C, B = "#c13a34", "#1f6fb0"  # 主路线红 / 备选蓝

    def P(x, y):  # 512 基准坐标缩放
        return (x, y)

    def draw(key, title, labels, camps, routes, note):
        img = plt.imread(os.path.join(BASE, f"{key}.png"))
        h, w = img.shape[:2]
        sx, sy = w / 512.0, h / 512.0
        fig, ax = plt.subplots(figsize=(7.6, 7.6 * h / w))
        ax.imshow(img)
        ax.set_xlim(0, w)
        ax.set_ylim(h, 0)
        ax.axis("off")

        def tx(x, y):  # 512 -> 像素
            return x * sx, y * sy

        # 路线箭头（底图上、标签下）
        for ri, (pts, color, ls, _lab) in enumerate(routes):
            px = [tx(*p) for p in pts]
            for i in range(len(px) - 1):
                ax.add_patch(FancyArrowPatch(px[i], px[i + 1],
                             arrowstyle="-|>", mutation_scale=18,
                             color=color, lw=2.4, ls=ls, zorder=3,
                             connectionstyle="arc3,rad=0.12",
                             shrinkA=9, shrinkB=9))
            offs = [(-16, -18), (16, 18), (-16, 18)]
            ox, oy = offs[ri % len(offs)]
            for i, (x, y) in enumerate(px):
                ax.scatter([x + ox], [y + oy], s=200, color="white",
                           edgecolor=color, lw=1.8, zorder=5)
                ax.text(x + ox, y + oy, str(i + 1), ha="center", va="center",
                        fontsize=8, color=color, fontweight="bold", zorder=6)

        # 野怪营地圆点（推演位置：以底图地形为参照）
        for kind, x, y, _lab in camps:
            color = {"camp_g": "#1fa06b", "camp_y": "#e8a13a",
                     "camp_r": "#e8554e"}[kind]
            cx, cy = tx(x, y)
            ax.scatter([cx], [cy], s=260, color=color, alpha=.9,
                       edgecolor="white", lw=1.6, zorder=4)

        # 文字标注（白底圆角框）
        for x, y, text, ha, va in labels:
            lx, ly = tx(x, y)
            ax.text(lx, ly, text, ha=ha, va=va, fontsize=6.8, color=INK,
                    zorder=7, linespacing=1.35,
                    bbox=dict(boxstyle="round,pad=0.28", fc="white",
                              ec="#c8ccd2", lw=.7, alpha=.92))

        handles = [
            Line2D([], [], color=C, lw=2.4, label=routes[0][3]),
        ]
        if len(routes) > 1:
            handles.append(Line2D([], [], color=B, lw=2.4, ls="--",
                                  label=routes[1][3]))
        for col, name in (("#1fa06b", "绿点野怪"), ("#e8a13a", "黄点野怪"),
                          ("#e8554e", "红点野怪")):
            if any(k == name[0] for k, *_ in [(c[0][0], c) for c in camps
                  if {"绿点野怪": "camp_g", "黄点野怪": "camp_y",
                      "红点野怪": "camp_r"}[name] == c[0]]):
                handles.append(Line2D([], [], color=col, marker="o", ls="",
                                      markersize=8, label=name))
        ax.legend(handles=handles, loc="upper left", fontsize=7.5,
                  framealpha=.9, facecolor="white")

        ax.set_title(title, fontsize=12, color=INK, pad=8)
        ax.text(w / 2, h + 14, note, ha="center", fontsize=7.8, color=SUB)
        save(fig, f"route-{key}.png")

    # ---------------- Echo Isles：出生 左上(对面)/右上(己方)，左右镜像
    draw("ei", "Echo Isles 练级路线（真实地图标注）",
         labels=[
             (447, 188, "雇佣兵营地?\n实测: 练完≈2.3(累计230XP)", "center", "top"),
             (415, 296, "分矿\n累计XP 待补", "center", "top"),
             (352, 100, "门口333 ≈120XP(推)", "center", "top"),
             (330, 148, "基地下方绿点\n收尾至 3.0(累计300)", "center", "top"),
             (250, 186, "中心营地?\n组合/XP 待补", "center", "top"),
             (455, 55, "己方出生", "left", "top"),
             (95, 55, "对面出生", "right", "top"),
         ],
         camps=[
             ("camp_y", 383, 78, ""), ("camp_g", 408, 130, ""),
         ],
         routes=[
             ([(452, 200), (405, 285), (408, 130)], C, "-",
               "顺序一：雇兵营→分矿→绿点"),
             ([(405, 285), (452, 200), (408, 130)], B, "--",
               "顺序二：分矿→雇兵营→绿点"),
         ],
         note="红X/蓝X=对面/己方出生，黄圆=金矿（底图自带）；标?者待核对，掉落待补")

    # ---------------- Concealed Hill：出生 右上(对面)/左下(己方)
    draw("ch", "Concealed Hill 练级路线（真实地图标注）",
         labels=[
             (168, 352, "门口555黄点\n实测: 练完1.8(累计180)", "center", "top"),
             (245, 318, "绿点533海龟\n实测: 练完2.2(累计220)", "center", "top"),
             (296, 452, "分矿\n实测: 练完3.0(累计300)", "center", "top"),
             (262, 252, "红点附近绿点\n实测: 练完2.7(累计270)", "center", "top"),
             (330, 330, "商店\n实测: 练完3.1(累计310)", "center", "top"),
             (272, 300, "中央红点\n可勾到酒馆截杀", "center", "top"),
             (448, 62, "对面出生", "left", "top"),
             (118, 415, "己方出生", "right", "top"),
         ],
         camps=[
             ("camp_y", 205, 358, ""), ("camp_g", 258, 332, ""),
             ("camp_g", 275, 262, ""), ("camp_r", 282, 298, ""),
         ],
         routes=[
             ([(205, 358), (258, 332), (302, 455)], C, "-",
               "主路线：555→533→分矿"),
             ([(275, 262), (338, 322)], B, "--", "延伸：红点附近绿点→商店"),
         ],
         note="双温泉位置底图未标注；酒馆/商店/佣兵营对应关系待核对，掉落待补")

    # ---------------- Amazonia：出生 右上(对面)/左下(己方)
    draw("am", "Amazonia 练级路线（真实地图标注）",
         labels=[
             (100, 100, "雇佣兵营地?\n实测: 练完2.0(累计200)\n掉落: 可勾电盾加速", "center", "top"),
             (80, 390, "分矿(三怪无尸体\n→亡灵练级难受)", "center", "top"),
             (200, 480, "门口营地\nXP 待补", "center", "top"),
             (450, 72, "对面出生", "left", "top"),
             (112, 408, "己方出生", "right", "top"),
         ],
         camps=[
             ("camp_y", 128, 88, ""), ("camp_g", 208, 470, ""),
         ],
         routes=[
             ([(120, 96), (75, 388), (200, 468)], C, "-",
               "佣兵营(勾电盾)→分矿→门口营"),
         ],
         note="勾电盾=让电盾套在怪堆里的单位身上白电一圈；酒馆/商店对应待核对")

    # ---------------- Twisted Meadows：4人图，1v1 常用 左上(己)/右下(对)
    draw("tm", "Twisted Meadows 练级路线（真实地图标注）",
         labels=[
             (152, 92, "己方出生\n可兵营+大G卡傀儡抢宝", "center", "bottom"),
             (392, 396, "对面出生(右下)\n对称组合之一", "center", "top"),
             (232, 148, "雇佣兵营地?\n实测: 练完2.0(累计200)\n掉落: 小永久+大消耗", "center", "top"),
             (70, 66, "分矿·傀儡守\nXP 待补", "center", "top"),
             (250, 380, "中心营地?\nXP 待补", "center", "top"),
         ],
         camps=[
             ("camp_y", 205, 180, ""), ("camp_r", 250, 340, ""),
         ],
         routes=[
             ([(195, 172), (238, 160), (80, 78)], C, "-",
               "门口→佣兵营→傀儡分矿(卡位)"),
         ],
         note="4人图，1v1 多为左上/右下对角；傀儡守矿开矿成本高；卡傀儡有失败率需多练")

    # ---------------- Autumn Leaves：出生 右上(己)/左下(对)
    draw("al", "Autumn Leaves 练级路线（真实地图标注）",
         labels=[
             (400, 105, "门口白狼绿点\nXP 待补", "center", "top"),
             (315, 355, "商店\n实测: 练完2.0(累计200)", "center", "top"),
             (390, 40, "己方出生", "left", "top"),
             (140, 425, "对面出生", "right", "top"),
             (352, 200, "分矿位·易开\nXP 待补", "center", "top"),
         ],
         camps=[
             ("camp_g", 400, 120, ""),
         ],
         routes=[
             ([(398, 118), (338, 348), (370, 48)], C, "-",
               "白狼绿点→商店→家门口分矿"),
         ],
         note="W3C 数据: 对 NE 明显劣势、对 HUM/UD 略优；掉落待补")

    # ---------------- Springtime：出生 左上(对面)/右下(己方)
    draw("st", "Springtime 练级路线（真实地图标注）",
         labels=[
             (370, 290, "门口绿点海象人\n实测: 练完1.7(累计170)", "center", "top"),
             (300, 200, "雇佣兵营地?\n冰巨魔系(牧师无驱散)", "center", "top"),
             (258, 258, "★中央矿(无守护)\n双方都能偷, 侦查必查", "center", "top"),
             (150, 130, "分矿\n实测: 练完2.4(累计240)", "center", "top"),
             (100, 110, "对面出生", "right", "top"),
             (452, 348, "己方出生", "left", "top"),
         ],
         camps=[
             ("camp_g", 382, 302, ""),
         ],
         routes=[
             ([(380, 300), (308, 212), (165, 140)], C, "-",
               "海象人→雇兵营→分矿"),
         ],
         note="中央无守护金矿为全图主题；佣兵营/商店对应待核对，掉落待补")

    # ---------------- HammerFall：出生 左上(对面)/右下(己方)
    draw("hf", "HammerFall 练级路线（真实地图标注）",
         labels=[
             (128, 122, "门口绿点豺狼人\n实测: 练完1.4(累计140)\n留一只小豺狼不打", "center", "top"),
             (95, 185, "绿点海龟\n实测: 练完2.0(累计200)", "center", "top"),
             (62, 262, "分矿·警戒范围大\n实测: 练完2.0(累计200)", "center", "top"),
             (218, 172, "九头蛇绿点\n实测: 练完2.5(累计250)", "center", "top"),
             (272, 140, "地精实验室\n实测: 练完3.1(累计310)\n=飞艇补给点", "center", "top"),
             (270, 430, "三矿位矿点\n双分矿可打三矿", "center", "top"),
             (100, 62, "对面出生", "right", "top"),
             (452, 415, "己方出生", "left", "top"),
         ],
         camps=[
             ("camp_g", 152, 135, ""), ("camp_g", 105, 200, ""),
             ("camp_g", 230, 185, ""),
         ],
         routes=[
             ([(148, 138), (105, 198), (62, 258), (228, 182), (262, 152)],
              C, "-", "豺狼(留一只)→海龟→分矿→九头蛇→实验室"),
         ],
         note="小图可打三矿；地精实验室=飞艇补给点，攻防双方都要抢；掉落待补")

    # ---------------- TideHunter：出生 左上(对面)/右下(己方)
    draw("th", "TideHunter 练级路线（真实地图标注）",
         labels=[
             (140, 165, "门口黄点·潮汐\nBR可造得很近\n累计XP 待补", "center", "top"),
             (95, 230, "绿点\n两绿点组合到2级", "center", "top"),
             (215, 240, "绿点", "center", "top"),
             (55, 345, "分矿·远+警戒+100\n对面开矿慢", "center", "top"),
             (290, 205, "地精实验室?", "center", "top"),
             (250, 268, "地精商人?/酒馆?", "center", "top"),
             (100, 122, "对面出生", "right", "top"),
             (452, 415, "己方出生", "left", "top"),
         ],
         camps=[
             ("camp_y", 162, 178, ""), ("camp_g", 112, 245, ""),
             ("camp_g", 232, 252, ""),
         ],
         routes=[
             ([(160, 180), (112, 243), (232, 252), (288, 218)], C, "-",
               "潮汐→绿→绿(两绿点到2)→实验室"),
         ],
         note="分矿远+怪警戒+100，利于前期压制；掉落待补")


if __name__ == "__main__":
    fig_xp()
    fig_map_pool()
    fig_ban_flow()
    fig_pyramid()
    fig_population()
    fig_plan()
    fig_routes()
    print("all done")
