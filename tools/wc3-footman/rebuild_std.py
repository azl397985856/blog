# -*- coding: utf-8 -*-
"""Shell-free standard rebuild of FF 5.5.3W-based maps.

Background (2026-10-25): the original FF 5.5.3W is VxOP-shell protected with
nonstandard object tables (extra trailing int per mod in w3u/w3a). Every repack
keeping the shell crashed on ALL clients (netbar direct, KK). This script emits
a plain vanilla map instead: standard MPQ (MPQWriter), object tables re-encoded
WITHOUT the trailing ints, shell assets materialized under their referenced
paths, plus a war3map.imp manifest.

Usage: python3 rebuild_std.py            # builds v0.0s and v0.6s
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import w3obj
import build as ffbuild
from mpq import MPQWriter

SRC = os.path.join(HERE, "base", "Footmen_Frenzy_v5.5.3W.w3x")
EX = os.path.join(HERE, "base", "ff553_extract")
EXTRA = os.path.join(HERE, "base", "ff553_extra")
DIST = os.path.join(HERE, "dist")

STANDARD_FILES = [
    "war3map.w3i", "war3map.w3e", "war3map.doo", "war3map.wts", "war3map.shd",
    "war3mapMap.blp", "war3mapMisc.txt", "war3mapSkin.txt",
    "war3map.w3t", "war3map.w3h", "war3map.w3q",
]


def rd(name):
    return open(os.path.join(EX, name), "rb").read()


def std_obj(ff_bytes, use_optional_ints):
    """FF-variant object table bytes -> standard-format bytes (no trailing int)."""
    f = w3obj.ObjFile.parse(ff_bytes, use_optional_ints=use_optional_ints)
    return f.encode(with_end=False)


def walk_std(data, name, optional):
    """Strict walk under the STANDARD model; returns (ok, detail)."""
    p = 4
    try:
        for ti in range(2):
            count = struct.unpack_from("<I", data, p)[0]
            p += 4
            for _ in range(count):
                nmod = struct.unpack_from("<I", data, p + 8)[0]
                p += 12
                for _ in range(nmod):
                    vtype = struct.unpack_from("<I", data, p + 4)[0]
                    p += 8
                    if vtype not in (0, 1, 2, 3):
                        return False, f"bad type {vtype} @ {p-4}"
                    if optional:
                        p += 8
                    if vtype == 3:
                        e = data.find(b"\x00", p)
                        if e < 0:
                            return False, f"unterminated string @ {p}"
                        p = e + 1
                    else:
                        p += 4
                # standard model: no trailing int
        if p != len(data):
            return False, f"EOF mismatch: walked {p}, file {len(data)}"
        return True, "OK"
    except (struct.error, IndexError) as exc:
        return False, f"exception @ {p}: {exc}"


def build_imp(custom_names):
    out = struct.pack("<II", 1, len(custom_names))
    for n in custom_names:
        out += b"\x0d" + n.encode("ascii") + b"\x00"
    return out


def build_std(profile, out_name):
    w = MPQWriter(block_size=4096)

    w.add("war3map.w3u", std_obj(ffbuild.make_w3u(profile), False))
    w.add("war3map.w3a", std_obj(ffbuild.make_w3a(profile), True))
    if profile.get("fx") or profile.get("ai"):
        w.add("Scripts\\war3map.j", ffbuild.make_j(profile))
    else:
        w.add("Scripts\\war3map.j", rd("war3map.j"))
    w.add("war3map.wts", ffbuild.make_wts())
    for f in STANDARD_FILES:
        if f in ("war3map.wts",):
            continue
        w.add(f, rd(f))
    # 最小合法 war3mapUnits.doo（底图无此文件，全图单位由脚本创建；给个空表防解析异常）
    w.add("war3mapUnits.doo", struct.pack("<III", 5, 11, 0))
    # 壳资产落位
    w.add("war3mapPath.map", open(os.path.join(EXTRA, "blk06.bin"), "rb").read())
    custom = ["war3mapImported\\hk_pool.tga", "war3mapImported\\hk_test.tga",
              "war3mapImported\\hk_model1.mdl", "war3mapImported\\hk_model2.mdl",
              "war3mapImported\\hk_model3.mdl", "war3mapImported\\hk_model4.mdl",
              "UI\\Minimap\\MinimapIconCreepLoc2.blp"]
    w.add("war3mapImported\\hk_pool.tga", open(os.path.join(EXTRA, "blk27.bin"), "rb").read())
    w.add("war3mapImported\\hk_test.tga", open(os.path.join(EXTRA, "blk22.bin"), "rb").read())
    for i, blk in enumerate(["blk17", "blk18", "blk21", "blk28"], 1):
        w.add(f"war3mapImported\\hk_model{i}.mdl",
              open(os.path.join(EXTRA, f"{blk}.bin"), "rb").read())
    w.add("UI\\Minimap\\MinimapIconCreepLoc2.blp", open(os.path.join(EXTRA, "blk16.bin"), "rb").read())
    for blk in ["blk19", "blk20", "blk24", "blk25", "blk26"]:
        n = f"war3mapImported\\{blk}.tga"
        w.add(n, open(os.path.join(EXTRA, f"{blk}.bin"), "rb").read())
        custom.append(n)
    w.add("war3map.imp", build_imp(custom))

    blob = w.build()
    hm3w = open(SRC, "rb").read()[:512]
    out = os.path.join(DIST, out_name)
    open(out, "wb").write(hm3w + blob)

    # 自校验：标准模型严格走查 + 文件清点
    mpq = __import__("mpq").MPQReader(open(out, "rb").read(), base=512)
    ok_u, d_u = walk_std(mpq.read("war3map.w3u"), "w3u", False)
    ok_a, d_a = walk_std(mpq.read("war3map.w3a"), "w3a", True)
    print(f"built {out}: {len(hm3w)+len(blob)} B | w3u std-walk {ok_u} {d_u} | w3a std-walk {ok_a} {d_a}")
    assert ok_u and ok_a


if __name__ == "__main__":
    targets = sys.argv[1:] or ["v0.0s", "v0.6s"]
    prof = {"v0.0s": dict(renames=False, skills=False),
            "v0.6s": dict(icons=True, tints=True, fx=True, ai=True)}
    for t in targets:
        build_std(prof[t], f"FF_4Brothers_{t}.w3x")
