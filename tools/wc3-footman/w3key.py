# -*- coding: utf-8 -*-
"""WC3 26-char CD-key -> registry 16-byte value ("War3 CD"/"War3X CD").

Faithful Python port of bncsutil's CDKeyDecoder::processWarCraft3Key
(BNETDocs/bncsutil, LGPL) — the same transform the official installer
applies when writing the key into the registry.

Usage: python3 w3key.py <26-char-key>
"""
import re
import struct
import sys

_src = open(__file__.replace('w3key.py', 'keytables.h')).read()


def _parse_array(name):
    m = re.search(name + r'\[\] = \{(.*?)\};', _src, re.S)
    return [int(v, 16) for v in re.findall(r'0x[0-9A-Fa-f]{1,2}', m.group(1))]


W3_KEY_MAP = _parse_array('w3KeyMap')
W3_TRANSLATE = _parse_array('w3TranslateMap')
W3_BUFLEN = 52
M32 = 0xFFFFFFFF


def decode_values(key):
    """26-char key -> (values[4], product). Port of processWarCraft3Key."""
    cdkey = key.upper().replace('-', '')
    assert len(cdkey) == 26, len(cdkey)
    table = [0] * W3_BUFLEN
    a, b = 0, 0x21
    for ch in cdkey:
        a = (b + 0x07B5) % W3_BUFLEN
        b = (a + 0x07B5) % W3_BUFLEN
        decode = W3_KEY_MAP[ord(ch)]
        assert decode != 0xFF, f'bad char {ch!r}'
        table[a] = decode // 5
        table[b] = decode % 5

    # mult(4, 5, values+3, table[i-1]) for i = 52..1  (bigint: values = values*5 + digit)
    values = [0, 0, 0, 0]
    for i in range(W3_BUFLEN, 0, -1):
        digit = table[i - 1]
        carry = digit
        for k in range(3, -1, -1):  # a-- : values[3] -> values[0]
            prod = values[k] * 5 + carry
            values[k] = prod & M32
            carry = prod >> 32
        # carry beyond limb0 dropped (C code discards it)

    decode_key_table(values)

    product = _swap32((values[0] & M32) >> 0x0A)
    return values, product


def decode_key_table(keyTable):
    # ---- pass 1 (nibble walking through w3TranslateMap) ----
    var8 = 29
    i = 464
    while True:
        esi = (var8 & 7) << 2
        var4 = var8 >> 3
        varC = (keyTable[3 - var4] >> esi) & 0xF
        if i < 464:
            j = 29
            while j > var8:
                ecx = (j & 7) << 2
                ebp = (keyTable[3 - (j >> 3)] >> ecx) & 0xF
                varC = W3_TRANSLATE[ebp ^ (W3_TRANSLATE[varC + i] + i)]
                j -= 1
        var8 -= 1
        j = var8
        while j >= 0:
            ecx = (j & 7) << 2
            ebp = (keyTable[3 - (j >> 3)] >> ecx) & 0xF
            varC = W3_TRANSLATE[ebp ^ (W3_TRANSLATE[varC + i] + i)]
            j -= 1
        # write-back uses OLD var8's esi/var4 (computed before decrement)
        j_idx = 3 - var4
        ebx = (W3_TRANSLATE[varC + i] & 0xF) << esi
        keyTable[j_idx] = (ebx | (~((0xF << esi) & M32) & keyTable[j_idx])) & M32
        i -= 16
        if i < 0:
            break

    # ---- pass 2 (bit permutation, esi += 11 mod 120; 源位来自循环前快照 copy[]) ----
    snapshot = keyTable[:]  # C: copy[i] = LSB4(keyTable[i])，本机构建下 LSB4 为恒等
    esi = 0
    for edi in range(120):
        eax = edi & 0x1F
        ecx = esi & 0x1F
        edx = 3 - (edi >> 5)
        # 源位: keyTable[3 - (esi >> 5)] bit (esi & 31)，读自快照
        ebp = (snapshot[3 - (esi >> 5)] >> ecx) & 1
        keyTable[edx] = ((ebp << eax) | (~((1 << eax)) & keyTable[edx])) & M32
        esi += 0xB
        if esi >= 120:
            esi -= 120


def _swap32(v):
    return ((v >> 24) & 0xFF) | ((v >> 8) & 0xFF00) | ((v << 8) & 0xFF0000) | ((v << 24) & 0xFF000000)


def key_to_registry(key):
    values, product = decode_values(key)
    return struct.pack('>4I', *[v & M32 for v in values]), product


if __name__ == '__main__':
    key = sys.argv[1] if len(sys.argv) > 1 else 'H8DNBV-NW7Y-NXFZVE-FNDY-H6HXNE'
    reg, product = key_to_registry(key)
    print('key     :', key)
    print('registry(BE):', reg.hex().upper())
    print('product :', hex(product), '(swap4 of values[0]>>10)')
