#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复 F45_BROTHERS_SKILL.w3x blk182 的行尾: BFX 注入段 42 行是 LF-only,
1.27 地图脚本惯例全文 CRLF(原版逐行 CRLF)。字节级归一后重写槽位+尾部重定位,
全套 roundtrip/邻块/hash 表验证照 f45_skills.py。"""
import os
import re
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from f45surgery import F45Map, BASE, verify_pair

STORM_KEY = 0x5486BEAF
REAL_J_BLOCK = 182

SRC = os.path.expanduser("~/wc3-test/fixpack/F45_BROTHERS_SKILL.w3x")
DST = os.path.expanduser("~/wc3-test/fixpack/F45_BROTHERS_SKILL.w3x")  # 原地语义: 先写 tmp 再替换


def norm_crlf(b):
    # 幂等: 先全部归一为 LF, 再统一 CRLF
    return b.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")


def main():
    tmp = SRC + ".fix"
    m = F45Map(open(SRC, "rb").read())
    raw = m.read_block_storm(REAL_J_BLOCK, STORM_KEY)
    fixed = norm_crlf(raw)
    n_lf = raw.count(b"\n") - raw.count(b"\r\n")
    print("blk182: %d bytes, LF-only lines before: %d -> after: %d (+%d bytes)"
          % (len(raw), n_lf, fixed.count(b"\n") - fixed.count(b"\r\n"), len(fixed) - len(raw)))
    assert fixed != raw and b"\r\n" in fixed
    # 断言只有行尾变化 (去掉 \r 后逐字节一致)
    assert fixed.replace(b"\r\n", b"\n") == raw.replace(b"\r\n", b"\n"), "content changed!"

    # 尾部预算 (同 f45_skills): archive 尾 - blk183 快照 - hash 表 - block 表 - 4K 余量
    used = [i for i in range(m.block_n) if m.block(i)[1] or m.block(i)[2]]
    assert used[-1] == 183
    sib_raw = {183: bytes(m.data[BASE + m.block(183)[0]:BASE + m.block(183)[0] + m.block(183)[1]])}
    archive_size = struct.unpack_from("<I", m.data, BASE + 8)[0]
    budget = archive_size - m.block(REAL_J_BLOCK)[0] - len(sib_raw[183]) - 4096 - 184 * 16

    # 幂等压缩自检: 新内容按槽位重压后必须能放下
    n_sec = max(1, -(-len(fixed) // m.sector_size))
    approx = 4 * (n_sec + 1) + sum(
        1 + len(zlib.compress(fixed[s * m.sector_size:(s + 1) * m.sector_size], 9))
        for s in range(n_sec))
    assert approx <= budget, "budget %d < approx %d" % (budget, approx)

    csize = m.write_block_storm(REAL_J_BLOCK, fixed, STORM_KEY, limit=budget)
    print("rewrote blk182: csize %d (budget %d)" % (csize, budget))
    info = m.save_relocated_tail(tmp, sib_raw=sib_raw)
    print("saved", tmp, info)

    # ---- 验证 ----
    dst = F45Map.open(tmp)
    got = dst.read_block_storm(REAL_J_BLOCK, STORM_KEY)
    assert got == fixed, "blk182 roundtrip mismatch"
    assert got.count(b"\n") - got.count(b"\r\n") == 0, "LF-only lines remain!"
    # 邻块与全部未动块逐字节一致
    for i in used:
        if i == REAL_J_BLOCK:
            continue
        ra = bytes(m.data[BASE + m.block(i)[0]:BASE + m.block(i)[0] + m.block(i)[1]])
        rb = bytes(dst.data[BASE + dst.block(i)[0]:BASE + dst.block(i)[0] + dst.block(i)[1]])
        assert ra == rb, "blk%d cipher bytes changed" % i
    assert m.hash_table == dst.hash_table, "hash table changed!"
    # 语义抽查: BFX 触发器与对话框改名仍在
    body = got.decode("utf-8", "replace")
    assert body.count("InitBrothersFX") == 2
    assert "call InitBrothersFX()" in body.split("function main")[-1]
    assert 'DialogAddButtonBJ(udg_ChooseHero,"方超（法官）")' in body
    print("all checks passed")

    os.replace(tmp, DST)
    print("replaced", DST)


if __name__ == "__main__":
    main()
