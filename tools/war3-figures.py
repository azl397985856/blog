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

    neutral = [25, 40, 60, 85, 115, 150, 190, 235, 285, 340]
    player = [round(x * 0.8) for x in neutral]
    w = .38
    ax2.bar([i - w / 2 for i in lv], neutral, width=w, color=ACCENT, label="单位基础经验")
    ax2.bar([i + w / 2 for i in lv], player, width=w, color=GUIDE, label="野怪实得（1级英雄×0.8）")
    ax2.set_ylim(0, 400)
    ax2.set_title("击杀获取经验：基础值 vs 野怪实得", fontsize=11, color=INK)
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
        ("LR", 1.4, 3.9, KEEP, "窄道难TR\n雇兵营肥"),
        ("EI", 1.8, 4.4, KEEP, "节奏快\n骚扰往返短"),
        ("TH", 3.0, 3.9, KEEP, "两绿点到 2 级\n对面分矿难开"),
        ("CH", 3.6, 3.6, KEEP, "双温泉+酒馆\n万金油续航好"),
        ("ST", 3.2, 3.1, KEEP, "中央免费矿\n偷矿攻防主题"),
        ("AM", 4.2, 3.3, KEEP, "雇兵营好练\n分矿无尸体克 UD"),
        ("NI", 4.9, 3.4, KEEP, "经典竞技图\n分矿近+角落矿"),
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


# ---------------------------------------------------------------- 14. 战术机制示意图（2.6/6.2）
def fig_tactics():
    import numpy as np

    # 14a 剑圣破隐卡位（阻止巨魔祭司放心灵火）
    fig, ax = plt.subplots(figsize=(7.4, 5.8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis("off")
    ax.add_patch(plt.Circle((4.0, 4.7), 2.5, fill=False, ls="--", ec=GUIDE, lw=1.2))
    ax.text(4.0, 7.45, "营地仇恨范围", ha="center", fontsize=9, color=SUB)
    ax.scatter([4.0], [5.4], s=430, marker="^", color=WARN, zorder=5)
    ax.text(4.0, 5.95, "巨魔祭司", ha="center", fontsize=10, color=INK, fontweight="bold")
    for mx, my in [(2.9, 4.3), (5.1, 4.5), (3.3, 6.0), (4.9, 6.1)]:
        ax.scatter([mx], [my], s=210, marker="o", color=GUIDE, zorder=3)
    ax.text(2.6, 3.6, "营地其他怪", fontsize=8.5, color=SUB)
    ax.scatter([5.95], [2.95], s=430, marker="s", color=KEEP, zorder=5)
    ax.annotate("", xy=(4.5, 4.85), xytext=(5.72, 3.2),
                arrowprops=dict(arrowstyle="-|>", lw=2.4, color=KEEP))
    ax.text(6.05, 2.5, "剑圣（疾风步中）", fontsize=10, color=KEEP)
    ax.annotate("祭司的 4 点钟方向贴脸，\n用攻击主动破隐（别等隐身自然结束）",
                xy=(4.55, 4.8), xytext=(6.7, 4.9), fontsize=9.5, color=BAN,
                arrowprops=dict(arrowstyle="->", lw=1.2, color=BAN))
    ax.text(5.0, 0.75, "进仇恨圈前全程隐身、且不让其他单位先进圈\n成功后整营不再施放心灵火（CH/LR 商店营实测点位）",
            ha="center", fontsize=8.8, color=SUB, linespacing=1.5)
    ax.set_title("剑圣破隐卡位：阻止巨魔祭司放心灵火", fontsize=12, color=INK)
    save(fig, "bm-innerfire.png")

    # 14b 围杀：移动 M vs 攻击 A
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.9))
    for ax, ok in ((ax1, True), (ax2, False)):
        ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_aspect("equal"); ax.axis("off")
        th = np.linspace(0, 2 * np.pi, 9 if ok else 7)[:-1]
        for a in th:
            x, y = 1.7 * np.cos(a), 1.7 * np.sin(a)
            ax.scatter([x], [y], s=300, color=ACCENT, zorder=4)
            ax.annotate("", xy=(x * .62, y * .62), xytext=(x * .88, y * .88),
                        arrowprops=dict(arrowstyle="-|>", lw=1.3, color=ACCENT))
        ax.scatter([0], [0], s=430, marker="X", color=BAN, zorder=5)
        ax.text(0, -.45, "目标英雄", ha="center", fontsize=9.5, color=BAN)
    ax1.set_title("正确：移动指令 M 收口 ✓（无缺口）", fontsize=11.5, color=KEEP)
    ax2.set_title("错误：攻击指令 A 留缺口 ✗（目标溜走）", fontsize=11.5, color=BAN)
    ax2.annotate("", xy=(2.95, 2.6), xytext=(1.15, .95),
                 arrowprops=dict(arrowstyle="-|>", lw=2.2, color=BAN, ls="--"))
    ax2.text(1.35, 1.7, "从缺口逃出", fontsize=9.5, color=BAN)
    fig.suptitle("围杀用 M 不用 A：攻击指令会让单位互相卡位留出缺口", fontsize=12.5, color=INK)
    fig.tight_layout(rect=[0, 0, 1, .93])
    save(fig, "surround-mva.png")

    # 14c 3 单位扎堆才触发野怪 AOE
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
    for ax in (ax1, ax2):
        ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis("off")
        ax.scatter([5.2], [5.6], s=430, marker="^", color=WARN, zorder=5)
        ax.text(5.2, 6.15, "食人魔王（冲击波）/ 花岗岩傀儡（踩地板）", ha="center", fontsize=9, color=INK)
    for mx, my in [(4.6, 3.4), (5.2, 2.9), (5.8, 3.3), (5.2, 3.9)]:
        ax1.scatter([mx], [my], s=290, color=ACCENT, zorder=4)
    ax1.add_patch(Polygon([(5.2, 5.6), (3.2, 2.2), (7.2, 2.2)], closed=True,
                          fc=BAN, alpha=.22, ec=BAN, lw=1.2))
    ax1.text(5.2, 1.4, "≥3 个单位扎堆 → AOE 命中全部 ✗", ha="center", fontsize=10.5, color=BAN)
    for mx, my in [(2.8, 3.2), (5.2, 2.4), (7.6, 3.2), (4.0, 4.4), (6.4, 4.6)]:
        ax2.scatter([mx], [my], s=290, color=ACCENT, zorder=4)
    ax2.text(5.2, 1.4, "散开：任一波形/圆圈打不满 3 个 → 技能不放 ✓", ha="center", fontsize=10.5, color=KEEP)
    ax2.text(5.2, .55, "（伤害为 0 之外还省掉了减速/眩晕）", ha="center", fontsize=8.8, color=SUB)
    fig.suptitle("野怪 AOE 的触发条件：3 个及以上单位被一次打到", fontsize=12.5, color=INK)
    fig.tight_layout(rect=[0, 0, 1, .92])
    save(fig, "creep-aoe3.png")

    # 14d 卡位（body block）救残血
    fig, ax = plt.subplots(figsize=(9.4, 4.6))
    ax.set_xlim(0, 14); ax.set_ylim(0, 7); ax.axis("off")
    ax.add_patch(FancyBboxPatch((.6, 2.4), 1.8, 1.8, boxstyle="round,pad=0.1",
                                fc="#e8e2d2", ec=SUB, lw=1.2))
    ax.text(1.5, 3.3, "基地", ha="center", fontsize=10, color=INK)
    ax.scatter([6.2], [4.1], s=330, marker="o", facecolors="none", edgecolors=BAN, lw=2, zorder=5)
    ax.text(6.2, 4.75, "残血单位", ha="center", fontsize=9.5, color=BAN)
    ax.annotate("", xy=(2.9, 3.6), xytext=(5.7, 4.05),
                arrowprops=dict(arrowstyle="-|>", lw=2, color=BAN, ls="--"))
    ax.scatter([8.3], [3.0], s=330, color=ACCENT, zorder=5)
    ax.text(8.3, 2.35, "卡位单位（健康）", ha="center", fontsize=9.5, color=ACCENT)
    ax.annotate("", xy=(7.1, 3.35), xytext=(8.0, 3.05),
                arrowprops=dict(arrowstyle="-|>", lw=1.6, color=ACCENT))
    for cx, cy in (11.3, 3.6), (11.9, 2.6):
        ax.scatter([cx], [cy], s=330, marker="s", color=WARN, zorder=5)
    ax.annotate("", xy=(9.1, 3.0), xytext=(10.9, 3.2),
                arrowprops=dict(arrowstyle="-|>", lw=2, color=WARN))
    ax.text(11.6, 4.35, "追兵（更快）", ha="center", fontsize=9.5, color=WARN)
    ax.text(7.3, 6.1, "用身体挡住追兵路线，为残血单位赢回跑回基地的时间",
            ha="center", fontsize=10, color=INK)
    ax.text(7.3, .7, "进攻端同理：卡位减速逃走的英雄/单位，配合围杀（见上图）用",
            ha="center", fontsize=8.8, color=SUB)
    ax.set_title("卡位（Body Block）：一堵换一命", fontsize=12, color=INK)
    save(fig, "body-block.png")


def fig_routes():
    """真实地图标注 v3：底图与全部点位数据来自 Liquipedia Preview（权威）。

    数据文件 tools/war3-preview-data.json 由 Preview wikitext 解析而来：
    建筑(酒馆/商店/市场/实验室/雇兵营)、金矿(含储量)、出生点、野怪营地
    (easy/medium/hard = 绿/黄/红点，含怪物组合与掉落)。实测 XP 以 _XP 覆盖。
    Concealed Hill 无 Preview 数据，单独用检测坐标处理。
    """
    import json
    from matplotlib.lines import Line2D

    TOOLS = os.path.dirname(os.path.abspath(__file__))
    BASE = os.path.join(TOOLS, "war3-base")
    DATA = json.load(open(os.path.join(TOOLS, "war3-preview-data.json")))
    C, B = "#c13a34", "#1f6fb0"
    LVL_COLOR = {"easy": "#1fa06b", "medium": "#e8a13a", "hard": "#e8554e"}
    LVL_NAME = {"easy": "绿", "medium": "黄", "hard": "红"}
    BLD_NAME = {"tavern": "酒馆", "merchant": "地精商店", "marketplace": "市场",
                "laboratory": "地精实验室", "merccamp": "雇佣兵营地",
                "fountainhealth": "医疗泉"}
    BLD_CHAR = {"tavern": "酒", "merchant": "商", "marketplace": "市",
                "laboratory": "实", "merccamp": "雇", "fountainhealth": "泉"}
    ITEM = {"Permanent": "永久", "Charged": "消耗", "Power Up": "升级书"}
    CN = {
        "Ogre Warrior": "食人魔战士", "Ogre Magi": "食人魔法师", "Ogre Mauler": "食人魔碎击者",
        "Forest Troll Trapper": "森林巨魔捕兽者", "Forest Troll Berserker": "森林巨魔狂战士",
        "Forest Troll High Priest": "森林巨魔高级祭司", "Forest Troll Warlord": "森林巨魔督军",
        "Forest Troll Shadow Priest": "森林巨魔暗影祭司", "Forest Troll": "森林巨魔",
        "Gnoll": "豺狼人", "Gnoll Warden": "豺狼人看守", "Gnoll Brute": "豺狼人蛮兵",
        "Gnoll Poacher": "豺狼人偷猎者", "Gnoll Overseer": "豺狼人监工", "Gnoll Assassin": "豺狼人刺客",
        "Murloc Nightcrawler": "鱼人夜行者", "Murloc Huntsman": "鱼人猎手",
        "Murloc Tiderunner": "鱼人潮行者", "Murloc Flesheater": "食人鱼人",
        "Mur'gul Snarecaster": "穆格尔诱捕师", "Mur'gul Tidewarrior": "穆格尔潮汐战士",
        "Mur'gul Blood-Gill": "穆格尔血鳃", "Mur'gul Marauder": "穆格尔掠夺者",
        "Kobold": "狗头人", "Kobold Geomancer": "狗头人地卜师", "Kobold Tunneler": "狗头人掘地者",
        "Kobold Taskmaster": "狗头人监工", "Renegade Wizard": "变节法师", "Rogue": "盗贼",
        "Enforcer": "压迫者", "Brigand": "强盗", "Apprentice Wizard": "学徒法师",
        "Rock Golem": "岩石傀儡", "Mud Golem": "泥浆傀儡", "Granite Golem": "花岗岩傀儡",
        "Sasquatch": "大脚野人", "Mammoth": "猛犸",
        "Tuskarr Trapper": "海象人捕兽者", "Tuskarr Spearman": "海象人枪兵", "Tuskarr Sorcerer": "海象人术士",
        "Furbolg Shaman": "熊怪萨满", "Furbolg Tracker": "熊怪追踪者",
        "Polar Furbolg Tracker": "极地熊怪追踪者", "Giant Polar Bear": "巨型北极熊", "Polar Bear": "北极熊",
        "Timber Wolf": "森林狼", "Frost Wolf": "冰霜狼", "Dire Frost Wolf": "凶猛冰霜狼",
        "Giant Sea Turtle": "巨型海龟", "Gargantuan Sea Turtle": "庞然海龟", "Sea Turtle": "海龟",
        "Hydra Hatchling": "九头蛇幼体", "Sea Giant": "海巨人", "Sea Giant Hunter": "海巨人猎手",
        "Makrura Snapper": "马克拉拉撕裂者", "Makrura Tidecaller": "马克拉拉唤潮者",
        "Reef Elemental": "礁石元素", "Enraged Elemental": "狂暴元素",
        "Skeleton Warrior": "骷髅战士", "Skeleton Archer": "骷髅弓手", "Sludge Flinger": "淤泥喷射者",
        "Skeletal Orc": "骷髅兽人", "Stormreaver Hermit": "风暴掠夺者隐士",
        "Stormreaver Apprentice": "风暴掠夺者学徒", "Red Dragon Whelp": "红龙幼龙",
        "Voidwalker": "虚空行者", "Ice Troll Trapper": "冰巨魔捕兽者", "Ice Troll Priest": "冰巨魔祭司",
        "Ice Troll Berserker": "冰巨魔狂战士", "Ice Troll High Priest": "冰巨魔高级祭司",
        "Ice Troll": "冰巨魔", "Ice Troll Warlord": "冰巨魔督军",
        "Spider Crab Limbripper": "蜘蛛蟹裂肢者", "Red Drake": "红幼龙",
        "Ogre Lord": "食人魔领主",
        "Tuskarr Warrior": "海象人战士", "Polar Furbolg Shaman": "极地熊怪萨满",
        "Magnataur Reaver": "猛犸掠夺者", "Nerubian Webspinner": "蛛网编织者",
        "Overlord Arachnathid": "蛛甲兽统领", "Warrior Arachnathid": "蛛甲兽战士",
        "Barbed Arachnathid (Creep)": "倒钩蛛甲兽", "Crystal Arachnathid": "水晶蛛甲兽",
    }

    def comp_cn(creeps):
        return "+".join(f"{CN.get(c['name'], c['name'])}{'×' + str(c['count']) if c['count'] > 1 else ''}"
                        for c in creeps)

    def drops_cn(creeps):
        parts = [f"{ITEM.get(c['item'], c['item'])}{c['ilvl']}"
                 for c in creeps if c["item"]]
        return "掉落: " + "/".join(parts) if parts else ""

    def near(d, x, y, types="spot", tol=0.06):
        src = d["spots"] if types == "spot" else d["objects"]
        best, bd = None, 1
        for e in src:
            dist = abs(e["x"] - x) + abs(e["y"] - y)
            if dist < bd:
                best, bd = e, dist
        return best if bd <= tol else None

    def draw_data(key, title, my, opp, steps, extras, routes, note,
                  my_lab=("center", "top"), opp_lab=("center", "top"), bld_hide=(),
                  legend_loc="upper left"):
        """steps: [(x,y,序号别名,实测行)]；extras: [(x,y,text,ha,va)]"""
        d = DATA[key]
        img = plt.imread(os.path.join(BASE, f"preview-{key}.jpg"))
        h, w = img.shape[:2]
        fig, ax = plt.subplots(figsize=(7.8, 7.8 * h / w))
        ax.imshow(img)
        ax.set_xlim(0, w); ax.set_ylim(h, 0); ax.axis("off")
        X, Y = lambda fx: fx * w, lambda fy: fy * h
        def lab(xx, yy, s, ha="center", va="top", fs=6.8, c=INK):
            ax.text(xx, yy, s, ha=ha, va=va, fontsize=fs, color=c, zorder=7,
                    linespacing=1.35,
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#c8ccd2",
                              lw=.7, alpha=.6))

        # 单字信号标记：仿游戏小地图 ping，深底金字，一字一义
        def tag(xx, yy, ch_, fs=10.5):
            ax.text(xx, yy, ch_, ha="center", va="center", fontsize=fs, fontweight="bold",
                    color="#ffd23f", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.35", fc="#141414", ec="#e0a92f",
                              lw=1.1, alpha=.82))

        # 金矿 / 中立建筑 / 野怪点 / 出生
        chars_seen = {}
        for o in d["objects"]:
            if o["type"] == "goldmine":
                tag(X(o["x"]), Y(o["y"]), "矿")
                chars_seen["矿"] = "金矿"
            elif o["type"] in BLD_CHAR and (o["x"], o["y"]) not in bld_hide:
                ch_ = BLD_CHAR[o["type"]]
                tag(X(o["x"]), Y(o["y"]), ch_)
                chars_seen[ch_] = BLD_NAME[o["type"]]
        for s in d["spots"]:
            ax.scatter([X(s["x"])], [Y(s["y"])], s=95, color=LVL_COLOR.get(s["level"], "#999"),
                       edgecolor="white", lw=1.1, zorder=4)
        ax.scatter([X(my[0])], [Y(my[1])], s=190, color=B, marker="s", edgecolor="white", lw=1.5, zorder=5)
        mx = 13 if my_lab[0] in ("left", "right") else 0
        myy = 12 if my_lab[1] in ("top", "bottom") else 0
        lab(X(my[0]) + (mx if my_lab[0] == "left" else -mx), Y(my[1]) + (myy if my_lab[1] == "top" else -myy),
            "己方出生", my_lab[0], my_lab[1], 7)
        ax.scatter([X(opp[0])], [Y(opp[1])], s=190, color=C, marker="s", edgecolor="white", lw=1.5, zorder=5)
        ox_ = 13 if opp_lab[0] in ("left", "right") else 0
        oy_ = 12 if opp_lab[1] in ("top", "bottom") else 0
        lab(X(opp[0]) + (ox_ if opp_lab[0] == "left" else -ox_), Y(opp[1]) + (oy_ if opp_lab[1] == "top" else -oy_),
            "对面出生", opp_lab[0], opp_lab[1], 7)

        # 路线箭头 + 带序号的营地标签（组合/掉落/实测自动生成）
        for pts, color, ls, _leg in routes:
            px = [(X(x), Y(y)) for x, y in pts]
            for i in range(len(px) - 1):
                ax.add_patch(FancyArrowPatch(px[i], px[i + 1], arrowstyle="-|>",
                             mutation_scale=17, color=color, lw=2.3, ls=ls, zorder=3,
                             connectionstyle="arc3,rad=0.12", shrinkA=8, shrinkB=8))
        for st in steps:
            x, y, alias, measured = st[:4]
            ha, va = (st[4], st[5]) if len(st) > 5 else ("center", "top")
            s = near(d, x, y)
            if not s:
                continue
            lines = [alias + f"〔{LVL_NAME.get(s['level'], '?')}〕", comp_cn(s["creeps"])]
            dr = drops_cn(s["creeps"])
            if dr:
                lines.append(dr)
            if measured:
                lines.append(measured)
            lab(X(x), Y(y) + (10 if va == "top" else -10), "\n".join(lines), ha, va)
        for x, y, text, ha, va in extras:
            lab(X(x), Y(y), text, ha, va)

        handles = [
            Line2D([], [], color=LVL_COLOR["easy"], marker="o", ls="", markersize=7, label="绿点(easy)"),
            Line2D([], [], color=LVL_COLOR["medium"], marker="o", ls="", markersize=7, label="黄点(medium)"),
            Line2D([], [], color=LVL_COLOR["hard"], marker="o", ls="", markersize=7, label="红点(hard)"),
        ]
        for pts, color, ls, leg in routes:
            handles.append(Line2D([], [], color=color, lw=2.3, ls=ls, label=leg))
        ax.legend(handles=handles, loc=legend_loc, fontsize=6.3, framealpha=.75,
                  facecolor="white", handlelength=1.1, labelspacing=0.25, borderpad=0.5)
        ax.set_title(title, fontsize=12, color=INK, pad=8)
        gloss = "  ".join(f"{k}={v}" for k, v in chars_seen.items())
        note = f"{note}；单字标记: {gloss}"
        ax.text(w / 2, h + 12, note, ha="center", fontsize=7.5, color=SUB)
        save(fig, f"route-{key}.png")

    # ---------------- EI：己方右上，雇佣兵营地在右缘（已实测确认）
    draw_data("ei", "Echo Isles 练级路线（真实地图标注）",
        my=(0.75, 0.05), opp=(0.15, 0.05), opp_lab=("left", "center"),
        steps=[
            (0.84, 0.47, "① 雇佣兵营地(右)", "实测: 练完≈2.3(累计230)"),
            (0.76, 0.66, "② 分矿营", "实测: 练完2.7(累计270)"),
            (0.66, 0.815, "③ 基地下方绿点", "收尾至 3.0(累计300)", "center", "top"),
        ],
        extras=[
            (0.66, 0.03, "门口333〔绿〕可做起手", "center", "bottom"),
            (0.845, 0.795, "分矿 12500", "left", "top"),
            (0.79, 0.095, "主矿 13500", "left", "top"),
        ],
        routes=[
            ([(0.84, 0.47), (0.76, 0.66), (0.68, 0.79)], C, "-", "顺序一: 雇兵营→分矿→绿点"),
            ([(0.76, 0.66), (0.84, 0.47), (0.68, 0.79)], B, "--", "顺序二: 分矿→雇兵营→绿点"),
        ],
        note="建筑与营地数据来自 Liquipedia Preview(全图唯一商店在下中, 市场在上中, 中央酒馆)；实测XP来自路线节点")

    # ---------------- AM：己方左下
    draw_data("am", "Amazonia 练级路线（真实地图标注）",
        my=(0.12, 0.81), opp=(0.78, 0.06),
        steps=[
            (0.84, 0.84, "① 雇佣兵营地·勾电盾", "实测: 练完2.0(累计200)"),
            (0.57, 0.87, "② 分矿营(金20000)", "泥浆傀儡无尸体, 亡灵练级难受", "center", "bottom"),
            (0.41, 0.85, "③ 门口营", "", "right", "top"),
        ],
        extras=[(0.93, 0.615, "硬点: 花岗岩傀儡\n掉永久5级(可插哨守等对面练)", "right", "top")],
        routes=[([(0.84, 0.84), (0.57, 0.92), (0.41, 0.85)], C, "-",
                 "雇兵营(勾电盾)→分矿→门口营")],
        note="分矿 20000 金且难开；勾电盾=让电盾套在怪堆里的单位身上白电一圈")

    # ---------------- TM：己方左上(卡傀儡)，对面右下
    draw_data("tm", "Twisted Meadows 练级路线（真实地图标注）",
        my=(0.26, 0.12), opp=(0.73, 0.80),
        steps=[
            (0.27, 0.34, "① 门口营(豺狼人)", "", "center", "bottom"),
            (0.47, 0.32, "② 雇佣兵营地", "实测(NE): 练完2.0(累计200); 掉落小永久+大消耗", "center", "top"),
            (0.155, 0.075, "③ 傀儡营(守角岛矿)", "兵营+大G卡傀儡抢消耗5级(有失败率)", "left", "center"),
        ],
        extras=[(0.33, 0.15, "主矿 12500", "left", "center"),
                (0.14, 0.335, "分矿 12500", "center", "top")],
        routes=[([(0.27, 0.34), (0.47, 0.32), (0.14, 0.07)], C, "-",
                 "门口→佣兵营→傀儡分矿(卡位)")],
        note="4人图取左上/右下对角；角岛只能空抵；全图 1酒馆+2商店+2雇兵营+4实验室(Preview 数据)")

    # ---------------- AL：己方右上
    draw_data("al", "Autumn Leaves 练级路线（真实地图标注）",
        my=(0.72, 0.10), opp=(0.25, 0.90),
        steps=[
            (0.805, 0.185, "① 门口白狼绿点", ""),
            (0.33, 0.27, "② 商店门口大脚营", "实测(NE): 练完2.0(累计200)"),
            (0.705, 0.435, "③ 家门口分矿(金12000)", ""),
        ],
        extras=[(0.705, 0.465, "分矿 12000", "center", "top"),
                (0.72, 0.10, "主矿 12500", "left", "center")],
        routes=[([(0.805, 0.185), (0.33, 0.27), (0.705, 0.435)], C, "-",
                 "白狼绿点→商店门口营→家门口分矿")],
        note="W3C 数据: 对 NE 明显劣势、对 HUM/UD 略优；两处分矿近中部, 易开但易被干扰")

    # ---------------- ST：己方右下
    draw_data("st", "Springtime 练级路线（真实地图标注）",
        my=(0.92, 0.76), opp=(0.04, 0.19),
        steps=[
            (0.66, 0.77, "① 门口海象人营(猛犸)", "实测(NE): 练完1.7(累计170)"),
            (0.51, 0.89, "② 分矿营(金12500)", "实测(NE): 练完2.4(累计240)"),
        ],
        extras=[(0.53, 0.44, "★中央矿 10000\n无守护, 双方都能偷, 侦查必查", "center", "top")],
        routes=[([(0.66, 0.77), (0.51, 0.89)], C, "-", "海象人→分矿")],
        note="双酒馆/双商店/双实验室/双雇兵营(Preview 数据)；中央矿是全图主题")

    # ---------------- HF：己方左上
    draw_data("hf", "HammerFall 练级路线（真实地图标注）",
        my=(0.10, 0.09), opp=(0.88, 0.99), my_lab=("right", "center"), opp_lab=("left", "center"),
        steps=[
            (0.25, 0.34, "① 门口绿点豺狼人", "实测: 练完1.4(累计140), 留一只不打"),
            (0.35, 0.67, "② 绿点海龟", "实测: 练完2.0(累计200)"),
            (0.12, 0.57, "③ 分矿(金10000)", "实测: 练完2.0(累计200); 营地警戒范围大"),
            (0.67, 0.47, "④ 九头蛇绿点", "实测: 练完2.5(累计250)"),
            (0.33, 0.43, "⑤ 地精实验室前营", "实测: 练完3.1(累计310); 实验室=飞艇补给点"),
        ],
        extras=[],
        routes=[([(0.25, 0.34), (0.35, 0.67), (0.10, 0.60), (0.67, 0.47), (0.33, 0.43)],
                 C, "-", "豺狼→海龟→分矿→九头蛇→实验室")],
        legend_loc="upper right",
        note="小图双自然矿可打三矿；建筑为 2实验室+2商店+酒馆(Preview 数据)")

    # ---------------- TH：己方右下
    draw_data("th", "TideHunter 练级路线（真实地图标注）",
        my=(0.75, 0.89), opp=(0.08, 0.17),
        steps=[
            (0.91, 0.49, "① 门口黄点·潮汐(穆格尔)", ""),
            (0.70, 0.57, "② 绿点海龟", "两绿点组合即到 2 级"),
            (0.78, 0.40, "③ 绿点", ""),
            (0.79, 0.69, "④ 地精实验室前营", "", "center", "top"),
        ],
        extras=[(0.945, 0.472, "分矿 11500", "center", "bottom")],
        routes=[([(0.91, 0.49), (0.70, 0.57), (0.78, 0.40), (0.79, 0.69)], C, "-",
                 "潮汐→绿→绿→实验室")],
        note="分矿偏远且怪警戒+100, 对面开矿慢；建筑: 2实验室+市场+商店+酒馆(Preview 数据)")

    # ---------------- CH：Preview 数据已补抓（2026-10-13），建筑身份权威确认
    draw_data("ch", "Concealed Hill 练级路线（真实地图标注）",
        my=(0.145, 0.887), opp=(0.746, 0.057), my_lab=("right", "top"),
        steps=[
            (0.116, 0.745, "① 门口黄点·食人魔", "实测: 练完1.8(累计180)", "left", "bottom"),
            (0.458, 0.953, "② 绿点海龟", "实测: 练完2.2(累计220)", "center", "bottom"),
            (0.712, 0.909, "③ 分矿营(豺狼守)", "实测: 练完3.0(累计300)", "center", "bottom"),
            (0.906, 0.775, "延伸① 红点旁绿点·狗头人", "实测: 练完2.7(累计270)", "right", "top"),
            (0.574, 0.700, "延伸② 商店门口营", "实测: 练完3.1(累计310)", "center", "top"),
        ],
        extras=[
            (0.205, 0.945, "主矿 12500", "left", "center"),
            (0.425, 0.408, "中央矿 12500\n红点食人魔领主守", "right", "center"),
        ],
        routes=[
            ([(0.116, 0.745), (0.458, 0.953), (0.712, 0.909)], C, "-",
             "主路线 门口→海龟→分矿"),
            ([(0.712, 0.909), (0.906, 0.775), (0.574, 0.700)], B, "--",
             "延伸 分矿→狗头人绿点→商店营"),
        ],
        note="5 矿均 12500；医疗泉由红幼龙红点守(Preview 数据)")

    # ---------------- NI：北方群岛（2026-10-13 补抓，S12 图池此前遗漏；XP=battle.net怪等级+Liquipedia公式计算）
    draw_data("ni", "Northern Isles 练级路线（真实地图标注）",
        my=(0.059, 0.787), opp=(0.866, 0.094), my_lab=("left", "bottom"),
        steps=[
            (0.246, 0.953, "① 门口绿点·食人魔", "基础160→1.6", "left", "bottom"),
            (0.376, 0.705, "② 鱼人绿点", "基础150→2.2", "center", "bottom"),
            (0.492, 0.822, "③ 分矿营", "基础280→2.8 开分矿(10000金)", "left", "bottom"),
        ],
        extras=[
            (0.10, 0.845, "主矿 13500", "center", "top"),
            (0.163, 0.135, "角落矿 9000\n猛犸红点守(掉永久5)\n直取后 3.7", "left", "top"),
        ],
        routes=[([(0.246, 0.953), (0.376, 0.705), (0.492, 0.822)], C, "-",
                 "门口→鱼人→分矿营"),
                ([(0.492, 0.822), (0.274, 0.405)], B, "--",
                 "延伸 分矿→实验室前营(3.5)")],
        note="1酒馆+2实验室+1商店+1市场；主矿13500/分矿10000/角落矿9000(Preview 数据)；等级=推演·计算(1本单英雄口径)")

    # ---------------- LR：Last Refuge（2026-10-14 补录；XP=battle.net怪等级+Liquipedia公式计算）
    draw_data("lr", "Last Refuge 练级路线（真实地图标注）",
        my=(0.048, 0.833), opp=(0.838, 0.062), my_lab=("left", "top"),
        steps=[
            (0.358, 0.941, "① 门口绿点·食人魔", "基础180 → 1.7", "right", "bottom"),
            (0.505, 0.911, "② 雇佣兵营", "基础395 → 2.9 雇兵", "left", "center"),
            (0.466, 0.720, "③ 绿鱼人", "基础165 → 3.2", "left", "bottom"),
        ],
        extras=[
            (0.147, 0.298, "本侧 12500 二矿·红营\n食人魔王守(掉永久5)\n直取后 4.0", "left", "top"),
        ],
        routes=[([(0.358, 0.941), (0.505, 0.911), (0.466, 0.720)], C, "-",
                 "门口→雇兵营→鱼人"),
                ([(0.466, 0.720), (0.325, 0.751)], B, "--",
                 "延伸 实验室营(3.8)")],
        note="1酒馆+2实验室+2商店+2雇兵营；等级=推演·计算(1本单英雄口径)")


if __name__ == "__main__":
    fig_xp()
    fig_map_pool()
    fig_tactics()
    fig_ban_flow()
    fig_pyramid()
    fig_population()
    fig_plan()
    fig_routes()
    print("all done")
