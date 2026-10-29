# -*- coding: utf-8 -*-
"""In-place MPQ block surgery for the WE-built F4.5-family maps.

F4.5 (新Footman Frenzy F4.5正式版) quirks, all verified 2026-10-29:
  - .w3x layout: HM3W header @0, MPQ @512
  - MPQ header BlockSize field = 7 → sector = 512 << 7 = 65536 bytes
  - no (listfile); files are addressed by hash only → surgery is block-index based
  - per-sector compression mask byte: 0x02 zlib, 0x08 PKWARE, 0x10 bzip2, 0 stored
  - hash/block tables use the standard "(hash table)"/"(block table)" cipher keys

Surgery model: read block → mutate content → recompress sector-wise (zlib-9,
mask 0x02) → splice back into the SAME slot (must fit old csize, tail zero
padded) → update the block table entry → re-encrypt the block table in place.
The game resolves files by name hash; keeping offsets and tables intact makes
the rewrite invisible to it. All 183 untouched blocks stay byte-identical.
"""
import bz2
import os
import struct
import sys
import zlib

import blast  # PKWARE explode, local module
from mpq import (_decrypt_block, _encrypt_block, _mpq_hash,
                 MPQ_HASH_FILE_KEY, MPQ_HASH_NAME_A, MPQ_HASH_NAME_B)

BASE = 512  # MPQ starts after the HM3W header


class F45Map:
    def __init__(self, data):
        self.data = bytearray(data)
        (magic, header_size, archive_size, fmt, shift,
         hash_off, block_off, hash_n, block_n) = struct.unpack_from("<4s2I2H4I", self.data, BASE)
        assert magic == b"MPQ\x1a", magic
        self.shift = shift
        self.sector_size = 512 << shift
        self.hash_off, self.block_off = BASE + hash_off, BASE + block_off
        self.hash_n, self.block_n = hash_n, block_n
        self.hash_table = list(struct.unpack(
            "<%dI" % (hash_n * 4),
            _decrypt_block(bytes(self.data[self.hash_off:self.hash_off + hash_n * 16]),
                           _mpq_hash("(hash table)", MPQ_HASH_FILE_KEY))))
        self.block_table = list(struct.unpack(
            "<%dI" % (block_n * 4),
            _decrypt_block(bytes(self.data[self.block_off:self.block_off + block_n * 16]),
                           _mpq_hash("(block table)", MPQ_HASH_FILE_KEY))))

    @classmethod
    def open(cls, path):
        with open(path, "rb") as f:
            return cls(f.read())

    def block(self, i):
        """(offset, csize, rsize, flags) of block i."""
        return self.block_table[i * 4:i * 4 + 4]

    def find_by_name(self, name):
        """Block index for name via the hash table, or None."""
        a = _mpq_hash(name, MPQ_HASH_NAME_A)
        b = _mpq_hash(name, MPQ_HASH_NAME_B)
        for slot in range(self.hash_n):
            na, nb, _lp, idx = self.hash_table[slot * 4:slot * 4 + 4]
            if (na, nb) == (a, b) and idx < 0xFFFFFFFE:
                return idx
        return None

    def read_block(self, i):
        off, csize, rsize, flags = self.block(i)
        assert flags & 0x80000000, "block %d not present" % i
        assert not flags & 0x030000, "encrypted sector table unsupported (blk%d)" % i
        if rsize == 0:
            return b""
        n_sectors = max(1, -(-rsize // self.sector_size))
        spans = struct.unpack_from("<%dI" % (n_sectors + 1), self.data, BASE + off)
        out = []
        for s in range(n_sectors):
            span = bytes(self.data[BASE + off + spans[s]:BASE + off + spans[s + 1]])
            want = min(self.sector_size, rsize - s * self.sector_size)
            if len(span) == want:  # stored, no mask byte
                out.append(span)
                continue
            mask, body = span[0], span[1:]
            if mask & 0x10:
                body = bz2.decompress(body)
            if mask & 0x02:
                body = zlib.decompress(body, 15)
            if mask & 0x08:
                body = blast.blast(body)
            assert not mask & 0xE1, "unsupported mask %#x (blk%d sec%d)" % (mask, i, s)
            # Legacy patched blocks (blk168/j, 2026-10-29 name surgery) may hold
            # a few bytes more than rsize says; the game reads rsize total.
            assert len(body) >= want, "blk%d sec%d: %d < %d" % (i, s, len(body), want)
            out.append(body[:want])
        return b"".join(out)

    # ---- Storm-encrypted blocks (e.g. the REAL war3map.j of F4.5, blk182):
    # sector table encrypted with the file key; each sector span INCLUDING its
    # mask byte encrypted with filekey+1+sector_index. F4.5's own packer even
    # truncates some zlib terminators — the game stops at the wanted byte
    # count, so tolerate eof=False when output length is met. ----

    def read_block_storm(self, i, key):
        off, csize, rsize, flags = self.block(i)
        assert flags & 0x030000, "blk%d not storm-encrypted" % i
        n_sectors = max(1, -(-rsize // self.sector_size))
        tlen = 4 * (n_sectors + 1)
        spans = struct.unpack("<%dI" % (n_sectors + 1),
                              _decrypt_block(bytes(self.data[BASE + off:BASE + off + tlen]), key))
        assert spans[0] == tlen and spans[-1] == csize, "bad storm sector table (blk%d)" % i
        out = []
        for s in range(n_sectors):
            span = bytes(self.data[BASE + off + spans[s]:BASE + off + spans[s + 1]])
            want = min(self.sector_size, rsize - s * self.sector_size)
            whole = _decrypt_block(span, (key + 1 + s) & 0xFFFFFFFF)
            mask = whole[0]
            if mask == 0x00:
                body = whole[1:]
            elif mask == 0x02:
                d = zlib.decompressobj(15)
                body = d.decompress(whole[1:])
                assert len(body) >= want and (d.eof or len(body) == want), \
                    "blk%d sec%d: stream %dB want %d eof=%s" % (i, s, len(body), want, d.eof)
            else:
                raise ValueError("blk%d sec%d mask %#x" % (i, s, mask))
            out.append(body[:want])
        return b"".join(out)

    def write_block_storm(self, i, content, key, limit=None):
        """Re-encrypt content into storm-encrypted block i. Returns new csize.
        `limit` overrides the slot size when the caller has budgeted a larger
        tail (save_compact relocates the tables afterwards)."""
        assert isinstance(content, bytes)
        off, csize, rsize, flags = self.block(i)
        if limit is not None:
            csize = limit
        n_sectors = max(1, -(-len(content) // self.sector_size))
        tlen = 4 * (n_sectors + 1)
        spans = [tlen]
        body = bytearray()
        for s in range(n_sectors):
            sector = content[s * self.sector_size:(s + 1) * self.sector_size]
            best = None
            for strategy in (zlib.Z_DEFAULT_STRATEGY, zlib.Z_FILTERED, zlib.Z_RLE):
                for ml in (8, 9):
                    c = zlib.compressobj(9, zlib.DEFLATED, 15, ml, strategy)
                    comp = c.compress(sector) + c.flush()
                    if best is None or len(comp) < len(best):
                        best = comp
            blob = (b"\x02" + best) if len(best) + 1 < len(sector) else (b"\x00" + sector)
            body += _encrypt_block(blob, (key + 1 + s) & 0xFFFFFFFF)
            spans.append(tlen + len(body))
        enc = _encrypt_block(struct.pack("<%dI" % len(spans), *spans), key)
        blob = enc + bytes(body)
        assert len(blob) <= csize, "blk%d: %d > slot %d" % (i, len(blob), csize)
        self.data[BASE + off:BASE + off + csize] = blob + b"\x00" * (csize - len(blob))
        self.block_table[i * 4 + 1] = len(blob)
        self.block_table[i * 4 + 2] = len(content)
        return len(blob)

    def write_block(self, i, content):
        """Recompress content into block i's slot (best zlib settings per
        sector). Returns new csize. Raises if it does not fit (slot sizes are
        fixed in place)."""
        assert isinstance(content, bytes)
        off, csize, rsize, flags = self.block(i)
        n_sectors = max(1, -(-len(content) // self.sector_size))
        table_len = 4 * (n_sectors + 1)
        spans = [table_len]
        body = bytearray()
        for s in range(n_sectors):
            sector = content[s * self.sector_size:(s + 1) * self.sector_size]
            best = None
            for strategy in (zlib.Z_DEFAULT_STRATEGY, zlib.Z_FILTERED, zlib.Z_RLE):
                for ml in (8, 9):
                    c = zlib.compressobj(9, zlib.DEFLATED, 15, ml, strategy)
                    comp = c.compress(sector) + c.flush()
                    if best is None or len(comp) < len(best):
                        best = comp
            if len(best) + 1 < len(sector):
                body += b"\x02" + best
            else:
                body += b"\x00" + sector
            spans.append(table_len + len(body))
        blob = struct.pack("<%dI" % len(spans), *spans) + bytes(body)
        assert len(blob) <= csize, "blk%d: %d > slot %d (need new-block technique)" % (i, len(blob), csize)
        self.data[BASE + off:BASE + off + csize] = blob + b"\x00" * (csize - len(blob))
        self.block_table[i * 4 + 1] = len(blob)
        self.block_table[i * 4 + 2] = len(content)
        return len(blob)

    def save(self, path):
        out = bytearray(self.data)
        enc = _encrypt_block(struct.pack("<%dI" % len(self.block_table), *self.block_table),
                             _mpq_hash("(block table)", MPQ_HASH_FILE_KEY))
        out[self.block_off:self.block_off + len(enc)] = enc
        with open(path, "wb") as f:
            f.write(out)

    def save_relocated_tail(self, path, sib_raw=None):
        """Rebuild the file tail after the last data block changed size: pack
        any data blocks living past the blob's new end (raw cipher copies —
        fix-key crypto is position independent), then the unchanged hash and
        block tables, and update header offsets/archive_size. Block indices
        and hash slots are left completely untouched."""
        used = [i for i in range(self.block_n) if self.block(i)[1] or self.block(i)[2]]
        blob_end = max(self.block(i)[0] + self.block(i)[1] for i in used)
        movers = sorted((i for i in used if self.block(i)[0] >= blob_end),
                        key=lambda x: self.block(x)[0])
        pos = blob_end
        for i in movers:
            raw = bytes(self.data[BASE + self.block(i)[0]:BASE + self.block(i)[0] + self.block(i)[1]])
            self.data[BASE + pos:BASE + pos + len(raw)] = raw
            self.block_table[i * 4 + 0] = pos
            pos += len(raw)

        hash_enc = _encrypt_block(struct.pack("<%dI" % len(self.hash_table), *self.hash_table),
                                  _mpq_hash("(hash table)", MPQ_HASH_FILE_KEY))
        block_enc = _encrypt_block(struct.pack("<%dI" % len(self.block_table), *self.block_table),
                                   _mpq_hash("(block table)", MPQ_HASH_FILE_KEY))
        out = bytearray(self.data[:BASE + pos])
        out += hash_enc + block_enc
        hash_rel, block_rel = pos, pos + len(hash_enc)
        struct.pack_into("<4s2I2H4I", out, BASE, b"MPQ\x1a", 32, len(out) - BASE, 0,
                         self.shift, hash_rel, block_rel, self.hash_n, self.block_n)
        with open(path, "wb") as f:
            f.write(out)
        return {"moved": movers, "file": len(out)}


def verify_pair(src_path, dst_path, patched_blocks, storm_blocks=frozenset(), verbose=True):
    """Every block outside patched/storm blocks must be byte-identical after
    surgery. Storm-encrypted blocks are skipped here (caller verifies them by
    read_block_storm round-trip); their block-table entries are checked."""
    src, dst = F45Map.open(src_path), F45Map.open(dst_path)
    assert len(src.data) == len(dst.data), "file size changed!"
    changed = []
    for i in range(src.block_n):
        so, sc, sr, sf = src.block(i)
        do, dc, dr, df = dst.block(i)
        if sc == 0 and sr == 0:  # free slot
            continue
        if i in storm_blocks:
            continue  # table entry intentionally changed; verified by caller
        if sf & 0x030000:  # encrypted sector table: unreadable, assert untouched
            assert (so, sc, sr, sf) == (do, dc, dr, df), "blk%d table entry changed" % i
            continue
        a, b = src.read_block(i), dst.read_block(i)
        if i in patched_blocks:
            assert a != b or patched_blocks[i] == a, "blk%d not updated" % i
            assert b == patched_blocks[i], "blk%d content mismatch" % i
            changed.append(i)
        else:
            assert a == b, "blk%d changed unexpectedly!" % i
    if verbose:
        print("verify OK: %d blocks intact, %d patched %s" % (src.block_n, len(changed), changed))
    return changed
