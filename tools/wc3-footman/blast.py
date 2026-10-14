# -*- coding: utf-8 -*-
"""PKWARE Data Compression Library (implode) decompressor — Python port of
Mark Adler's blast.c (zlib contrib), for FF map files compressed with the
0x08 PKWARE method. Input: the DCL stream AFTER the MPQ compression-mask byte.
"""
MAXBITS = 13
MAXWIN = 4096

LITLEN = bytes([
    11, 124, 8, 7, 28, 7, 188, 13, 76, 4, 10, 8, 12, 10, 12, 10, 8, 23, 8,
    9, 7, 6, 7, 8, 7, 6, 55, 8, 23, 24, 12, 11, 7, 9, 11, 12, 6, 7, 22, 5,
    7, 24, 6, 11, 9, 6, 7, 22, 7, 11, 38, 7, 9, 8, 25, 11, 8, 11, 9, 12,
    8, 12, 5, 38, 5, 38, 5, 11, 7, 5, 6, 21, 6, 10, 53, 8, 7, 24, 10, 27,
    44, 253, 253, 253, 252, 252, 252, 13, 12, 45, 12, 45, 12, 61, 12, 45,
    44, 173])
LENLEN = bytes([2, 35, 36, 53, 38, 23])
DISTLEN = bytes([2, 20, 53, 230, 247, 151, 248])
BASE = [3, 2, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 40, 72, 136, 264]
EXTRA = [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8]


def _construct(rep):
    length = []
    for r in rep:
        left = (r >> 4) + 1
        ln = r & 15
        length.extend([ln] * left)
    n = len(length)
    count = [0] * (MAXBITS + 1)
    for ln in length:
        count[ln] += 1
    if count[0] == n:
        return count, []
    left = 1
    for ln in range(1, MAXBITS + 1):
        left = (left << 1) - count[ln]
        if left < 0:
            raise ValueError("over-subscribed huffman code")
    offs = [0] * (MAXBITS + 2)
    for ln in range(1, MAXBITS + 1):
        offs[ln + 1] = offs[ln] + count[ln]
    symbol = [0] * n
    for i, ln in enumerate(length):
        if ln:
            symbol[offs[ln]] = i
            offs[ln] += 1
    return count, symbol


_LITCNT, _LITSYM = _construct(LITLEN)
_LENCNT, _LENSYM = _construct(LENLEN)
_DISTCNT, _DISTSYM = _construct(DISTLEN)


class _InputEnd(Exception):
    pass


class _Blast:
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.bitbuf = 0
        self.bitcnt = 0

    def bits(self, need):
        val = self.bitbuf
        while self.bitcnt < need:
            if self.pos >= len(self.data):
                raise _InputEnd()
            val |= self.data[self.pos] << self.bitcnt
            self.pos += 1
            self.bitcnt += 8
        self.bitbuf = val >> need
        self.bitcnt -= need
        return val & ((1 << need) - 1)

    def decode(self, count, symbol):
        bitbuf, bitcnt = self.bitbuf, self.bitcnt
        code = first = index = 0
        length = 1
        nxt = 1
        while True:
            while bitcnt > 0:
                code |= (bitbuf & 1) ^ 1
                bitbuf >>= 1
                bitcnt -= 1
                cnt = count[nxt] if nxt <= MAXBITS else 0
                nxt += 1
                if code < first + cnt:
                    self.bitbuf = bitbuf
                    self.bitcnt = bitcnt
                    return symbol[index + (code - first)]
                index += cnt
                first = (first + cnt) << 1
                code <<= 1
                length += 1
            left = (MAXBITS + 1) - length
            if left == 0:
                raise ValueError("ran out of codes")
            while bitcnt < min(left, 8):
                if self.pos >= len(self.data):
                    raise _InputEnd()
                bitbuf |= self.data[self.pos] << bitcnt
                self.pos += 1
                bitcnt += 8


def blast(data):
    """Returns the decompressed bytes; raises on malformed input."""
    s = _Blast(data)
    out = bytearray()
    lit = s.bits(8)
    if lit > 1:
        raise ValueError("bad literal flag")
    dict_bits = s.bits(8)
    if dict_bits < 4 or dict_bits > 6:
        raise ValueError("bad dictionary size")
    first = True
    try:
        while True:
            if s.bits(1):
                sym = s.decode(_LENCNT, _LENSYM)
                length = BASE[sym] + s.bits(EXTRA[sym])
                if length == 519:
                    break
                nb = 2 if length == 2 else dict_bits
                dist = (s.decode(_DISTCNT, _DISTSYM) << nb) + s.bits(nb) + 1
                if first and dist > len(out):
                    raise ValueError("distance too far back")
                start = len(out) - dist
                for i in range(length):
                    out.append(out[start + i])
            else:
                out.append(s.decode(_LITCNT, _LITSYM) if lit else s.bits(8))
            if len(out) >= MAXWIN:
                first = False
    except _InputEnd:
        pass
    return bytes(out)
