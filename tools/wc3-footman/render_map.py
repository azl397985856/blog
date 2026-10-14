# -*- coding: utf-8 -*-
"""把 FF 地图渲染成预览大图: 地形 (w3e) + 关键点位标记 (来自 Scripts\war3map.j 区域)。

用法: python3 render_map.py [输入目录] [输出png]
  默认读 base/ff553_extract/, 输出 base/preview_map_full.png
"""
import os
import re
import struct
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

# 65x65 cells, cell = [height:i16][water:i16][tex&flags:1][detail:1][cliff:1]
GRID = 65
CELL_BYTES = 7
HEADER = 85
BASE_HEIGHT = 0x2000

# 'Y' 自定义图块集 (10 个): 按渲染效果调色
PALETTE = {
    0: (124, 96, 62),    # Yrdt 土
    1: (86, 122, 58),    # Ydtr 草
    2: (64, 102, 48),    # Yblm 深草/大理石
    3: (128, 128, 132),  # Yltb 亮石
    4: (108, 108, 112),  # Ysqd 方石
    5: (96, 122, 60),    # Yrtl
    6: (74, 112, 52),    # Ygsb
    7: (88, 124, 58),    # Yhdg
    8: (116, 116, 120),  # Ywmb
    9: (140, 138, 134),  # Ksat 沥青
}
VOID = (24, 24, 26)


def load_font(size):
    for p in ("/System/Library/Fonts/PingFang.ttc",
              "/System/Library/Fonts/STHeiti Medium.ttc",
              "/System/Library/Fonts/Hiragino Sans GB.ttc"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def terrain(EXTRACT):
    data = open(os.path.join(EXTRACT, "war3map.w3e"), "rb").read()
    img = Image.new("RGB", (GRID, GRID))
    px = img.load()
    hmin, hmax = 32767, -32768
    for i in range(GRID * GRID):
        h = struct.unpack_from("<h", data, HEADER + i * CELL_BYTES)[0]
        hmin, hmax = min(hmin, h), max(hmax, h)
    for i in range(GRID * GRID):
        off = HEADER + i * CELL_BYTES
        h = struct.unpack_from("<h", data, off)[0]
        texb = data[off + 4]
        tex, boundary = texb & 0x7F, bool(texb & 0x80)
        c = VOID if boundary else PALETTE.get(tex, (200, 60, 200))
        shade = 0.82 + 0.36 * (h - hmin) / max(1, hmax - hmin)
        x, y = i % GRID, i // GRID
        px[x, y] = tuple(min(255, int(v * shade)) for v in c)
    return img


def rects(EXTRACT):
    j = open(os.path.join(EXTRACT, "Scripts_war3map.j" if os.path.exists(
        os.path.join(EXTRACT, "Scripts_war3map.j")) else "war3map.j"), "rb").read().decode("gbk", "replace")
    out = {}
    for m in re.finditer(r"set gg_rct_(\w+)=Rect\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)", j):
        out[m.group(1)] = tuple(float(x) for x in m.groups()[1:])
    return out


def to_cell(wx, wy):
    # 世界坐标 [-4096, 4096) -> cell
    return int((wx + 4096) // 128), int((wy + 4096) // 128)


def render(out_path, EXTRACT=None):
    EXTRACT = EXTRACT or os.path.join(HERE, "base", "ff553_extract")
    S = 10  # 放大倍数
    M = 46  # 边距
    terr = terrain(EXTRACT)
    W = GRID * S + M * 2
    H = GRID * S + M * 2 + 56
    img = Image.new("RGB", (W, H), (16, 16, 18))
    img.paste(terr.resize((GRID * S, GRID * S), Image.NEAREST), (M, M))
    dr = ImageDraw.Draw(img)
    f_title = load_font(30)
    f_mark = load_font(17)
    f_legend = load_font(17)
    dr.text((M, 10), "四兄弟 Footmen Frenzy 纪念版  v0.2 地图预览", font=f_title, fill=(240, 220, 160))

    rc = rects(EXTRACT)

    def dot(name, color, label=None, dy=0):
        l, b, r, t = rc[name]
        cx, cy = to_cell((l + r) / 2, (b + t) / 2)
        x, y = M + cx * S + S // 2, M + cy * S + S // 2
        dr.ellipse([x - 7, y - 7, x + 7, y + 7], outline=color, width=3)
        if label:
            dr.text((x + 9, y - 8 + dy), label, font=f_mark, fill=color)

    for k in range(1, 7):
        dot("TAVERN%d" % k, (255, 210, 80), "酒" if k == 1 else None)
    dot("MAP_CENTER", (255, 140, 60), "中心商店")
    # 四角基地 (T1..T4_COMPLETE 区域中心)
    corners = [("T1_COMPLETE", (90, 160, 255), "基地1"), ("T2_COMPLETE", (240, 90, 200), "基地2"),
               ("T3_COMPLETE", (120, 220, 120), "基地3"), ("T4_COMPLETE", (230, 90, 90), "基地4")]
    for name, color, label in corners:
        if name in rc:
            dot(name, color, label)

    lg = "● 黄圈=英雄酒馆×6   ● 橙圈=中心商店   ● 彩圈=四角基地   深色=禁区   中间 X 型=出兵路线"
    dr.text((M, H - 40), lg, font=f_legend, fill=(190, 190, 190))
    img.save(out_path)
    print("saved", out_path)


if __name__ == "__main__":
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "base", "preview_map_full.png")
    render(out, sys.argv[1] if len(sys.argv) > 1 else None)
