# -*- coding: utf-8 -*-
"""Strict walk + base-diff of object tables inside every dist .w3x.

Usage: python3 validate_obj.py
Walks war3map.w3u/w3a/w3t/w3h/w3q with bounds checks (type in 0/1/2/3,
exact EOF), then byte-diffs each file against base/ff553_extract to find
the first divergence and whether the stream realigns afterwards.
"""
import struct, sys, os, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mpq import MPQReader

OBJ_FILES = ["war3map.w3u", "war3map.w3a", "war3map.w3t", "war3map.w3h", "war3map.w3q"]
W3A = "war3map.w3a"


def asciify(b):
    return "".join(chr(c) if 32 <= c < 127 else f"\\x{c:02x}" for c in b)


def walk(data, name):
    """Strictly walk an object table. Returns (ok, detail, n_objects, n_mods)."""
    p = 0
    n_obj = n_mod = 0
    try:
        if len(data) < 4:
            return False, "file shorter than 4 bytes", 0, 0
        ver = struct.unpack_from("<I", data, 0)[0]
        p = 4
        if ver not in (1, 2, 3, 4):
            return False, f"bad version {ver}", 0, 0
        optional = name == W3A
        for ti in range(2):
            if p + 4 > len(data):
                return False, f"table {ti}: EOF while reading count (p={p})", n_obj, n_mod
            count = struct.unpack_from("<I", data, p)[0]
            p += 4
            if count > 100000:
                return False, f"table {ti}: absurd count {count} at p={p-4}", n_obj, n_mod
            for _ in range(count):
                if p + 12 > len(data):
                    return False, f"table {ti} obj#{n_obj}: EOF in header (p={p})", n_obj, n_mod
                orig, new = data[p:p+4], data[p+4:p+8]
                nmod = struct.unpack_from("<I", data, p+8)[0]
                p += 12
                if nmod > 10000:
                    return False, (f"table {ti} obj {asciify(orig)}/{asciify(new)}: "
                                   f"absurd modCount {nmod} at p={p-4}"), n_obj, n_mod
                for _ in range(nmod):
                    if p + 8 > len(data):
                        return False, (f"table {ti} obj {asciify(orig)}: EOF in mod id "
                                       f"#{n_mod} (p={p})"), n_obj, n_mod
                    mid = data[p:p+4]
                    vtype = struct.unpack_from("<I", data, p+4)[0]
                    p += 8
                    if vtype not in (0, 1, 2, 3):
                        return False, (f"obj {asciify(orig)} mod {asciify(mid)}: "
                                       f"bad type {vtype} at p={p-4}"), n_obj, n_mod
                    if optional:
                        p += 8
                    if vtype == 3:
                        e = data.find(b"\x00", p)
                        if e < 0:
                            return False, (f"obj {asciify(orig)} mod {asciify(mid)}: "
                                           f"unterminated string at p={p}"), n_obj, n_mod
                        p = e + 1
                    else:
                        if p + 4 > len(data):
                            return False, (f"obj {asciify(orig)} mod {asciify(mid)}: "
                                           f"EOF in value (p={p})"), n_obj, n_mod
                        p += 4
                    p += 4  # end
                    n_mod += 1
                n_obj += 1
        if p != len(data):
            return False, f"walk ended at p={p}, file is {len(data)} bytes (leftover {len(data)-p})", n_obj, n_mod
        return True, f"OK ver={ver} objs={n_obj} mods={n_mod}", n_obj, n_mod
    except (struct.error, IndexError) as exc:
        return False, f"exception at p={p}: {exc}", n_obj, n_mod


def byte_diff(a, b):
    """First divergence + longest common suffix between base a and variant b."""
    n = min(len(a), len(b))
    first = next((i for i in range(n) if a[i] != b[i]), None)
    if first is None and len(a) == len(b):
        return None
    suffix = 0
    while suffix < n - (first or 0) and a[len(a)-1-suffix] == b[len(b)-1-suffix]:
        suffix += 1
    return first, suffix


def main():
    base_dir = os.path.join(HERE, "base", "ff553_extract")
    dist = os.path.join(HERE, "dist")
    maps = sorted(f for f in os.listdir(dist) if f.endswith(".w3x"))
    for m in maps:
        path = os.path.join(dist, m)
        raw = open(path, "rb").read()
        try:
            mpq = MPQReader(raw, base=512)
        except Exception as exc:
            print(f"{m}: MPQ open FAILED: {exc}")
            continue
        print(f"== {m} ({len(raw)} B)")
        for name in OBJ_FILES:
            try:
                data = mpq.read(name)
            except (KeyError, AssertionError) as exc:
                print(f"  {name}: SKIP ({exc})")
                continue
            ok, detail, _, _ = walk(data, name)
            print(f"  {name}: {detail}")
            if not ok and os.path.exists(os.path.join(base_dir, name)):
                base = open(os.path.join(base_dir, name), "rb").read()
                d = byte_diff(base, data)
                if d:
                    first, suffix = d
                    ctx = data[first:first+24]
                    print(f"    vs base: first diverge @{first} (base {len(base)} B), "
                          f"common suffix {suffix} B, ctx {asciify(ctx)}")
        # published copy identity
        pub = os.path.join(HERE, "..", "..", "source", "files", m)
        if os.path.exists(pub):
            h1 = hashlib.md5(raw).hexdigest()
            h2 = hashlib.md5(open(pub, "rb").read()).hexdigest()
            if h1 != h2:
                print(f"  !! published source/files copy DIFFERS from dist ({h1} vs {h2})")


if __name__ == "__main__":
    main()
