# -*- coding: utf-8 -*-
"""Extractor for OP-protected Footmen Frenzy maps (VxOP header watermark).

The OP shell is standard MPQ with three twists, all reversible:
  1. garbled header_size field ("VxOP") — ignored by the game
  2. hash-table entries under standard names point to EMPTY decoy blocks;
     real blocks are identified by decrypting their sector-offset table with
     (hash(name, FILE_KEY) - 1) and checking it starts with [table_size, arch]
  3. files carry ENCRYPTED|COMPRESS: sectors decrypt with
     hash(name, FILE_KEY) + sector_index, then type-byte + zlib
"""
import struct
import sys
import zlib

from mpq import _decrypt_block, _mpq_hash, MPQ_HASH_FILE_KEY

SECTOR = 512 << 10  # VxOP maps use 512KB sectors (header exponent 0x0a)

CANDIDATE_NAMES = [
    "war3map.w3i", "war3map.w3e", "war3map.doo", "war3mapUnits.doo", "war3map.wts",
    "war3map.j", "war3map.shd", "war3mapMap.blp", "war3mapPath.map", "war3map.imp",
    "war3map.w3c", "war3map.w3s", "war3map.w3u", "war3map.w3t", "war3map.w3a",
    "war3map.w3h", "war3map.w3b", "war3map.w3q", "war3map.w3r", "war3mapMisc.txt",
    "war3mapSkin.txt", "war3mapExtra.txt", "(listfile)", "(attributes)",
]


def extract(map_path, out_dir):
    import os
    raw = open(map_path, "rb").read()
    base = raw.find(b"MPQ\x1a")
    assert base > 0
    hash_off, block_off, hash_size, block_cnt = struct.unpack_from("<4I", raw, base + 16)
    bt = struct.unpack("<%dI" % (block_cnt * 4),
                       _decrypt_block(raw[base + block_off:base + block_off + block_cnt * 16],
                                      _mpq_hash("(block table)", MPQ_HASH_FILE_KEY)))
    blocks = [bt[i * 4:(i + 1) * 4] for i in range(block_cnt)]

    os.makedirs(out_dir, exist_ok=True)
    used = set()
    results = {}
    for name in CANDIDATE_NAMES:
        key = _mpq_hash(name, MPQ_HASH_FILE_KEY)
        for bi, (off, arch, real, flags) in enumerate(blocks):
            if bi in used or real == 0 or arch <= 8:
                continue
            t = _decrypt_block(raw[base + off:base + off + 8], (key - 1) & 0xFFFFFFFF)
            p0, p1 = struct.unpack_from("<II", t)
            if p0 != 8 or p1 != arch:
                continue
            n = max(1, -(-real // SECTOR))
            offs = struct.unpack("<%dI" % (n + 1),
                                 _decrypt_block(raw[base + off:base + off + (n + 1) * 4],
                                                (key - 1) & 0xFFFFFFFF))
            out = b""
            for i in range(n):
                chunk = raw[base + off + offs[i]:base + off + offs[i + 1]]
                dec = _decrypt_block(chunk, (key + i) & 0xFFFFFFFF)
                if flags & 0x00000200 and dec:
                    t = dec[0]
                    if t == 2:
                        # tail < 4 bytes of the sector stays outside the block
                        # cipher (adler32 region) — stream-decompress without it
                        d = zlib.decompressobj()
                        dec = d.decompress(dec[1:]) + d.flush()
                    elif t == 0:
                        dec = dec[1:]
                    elif t == 0x10:
                        import bz2
                        dec = bz2.decompress(dec[1:])
                out += dec
            assert len(out) == real, "%s: %d != %d" % (name, len(out), real)
            used.add(bi)
            safe = name.replace("\\", "_")
            open(os.path.join(out_dir, safe), "wb").write(out)
            results[name] = len(out)
            break
    return results


if __name__ == "__main__":
    res = extract(sys.argv[1], sys.argv[2])
    for name, size in sorted(res.items()):
        print("%-20s %8d" % (name, size))
    print("extracted %d files" % len(res))
