# -*- coding: utf-8 -*-
"""Minimal MPQ v1 archive reader/writer for WC3 1.27 classic maps.

A .w3x/.w3m map is an MPQ archive. We only need the subset WC3 1.27 reads:
  - MPQ v1 header (format_version=0), 4096-byte sectors
  - files stored uncompressed (no IMPLODE/COMPRESS flags)
  - hash/block tables encrypted with the standard MPQ block cipher
  - no (attributes), no HET/BET, no patches

References: StormLib src/StormLib.h (flag constants, MPQ_FILE_VALID_FLAGS_W3X),
mpyq (crypt table / hash / block-cipher reference implementation).
"""
import struct

SECTOR_SIZE = 4096
FLAG_EXISTS = 0x80000000
FLAG_SINGLE_UNIT = 0x01000000
FLAG_ENCRYPTED = 0x00010000

MPQ_HASH_TABLE_INDEX = 0x000
MPQ_HASH_NAME_A = 0x100
MPQ_HASH_NAME_B = 0x200
MPQ_HASH_FILE_KEY = 0x300


def _prepare_crypt_table():
    seed = 0x00100001
    table = [0] * 0x500
    for i in range(256):
        index = i
        for _ in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            temp1 = (seed & 0xFFFF) << 0x10
            seed = (seed * 125 + 3) % 0x2AAAAB
            temp2 = seed & 0xFFFF
            table[index] = temp1 | temp2
            index += 0x100
    return table


CRYPT_TABLE = _prepare_crypt_table()


def _mpq_hash(name, hash_type):
    """MPQ string hash; names are uppercased ASCII with backslash separators."""
    seed1, seed2 = 0x7FED7FED, 0xEEEEEEEE
    for ch in name.upper().encode("ascii"):
        value = CRYPT_TABLE[hash_type + ch]
        seed1 = (value ^ (seed1 + seed2)) & 0xFFFFFFFF
        seed2 = (ch + seed1 + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
    return seed1


def _encrypt_block(data, key):
    """MPQ block cipher, encrypt direction. StormLib EncryptMpqBlock:
    the key chain evolves over the PLAINTEXT words."""
    seed1, seed2 = key, 0xEEEEEEEE
    out = bytearray()
    for i in range(0, len(data) - len(data) % 4, 4):
        seed2 = (seed2 + CRYPT_TABLE[0x400 + (seed1 & 0xFF)]) & 0xFFFFFFFF
        value = struct.unpack_from("<I", data, i)[0]
        cipher = (value ^ (seed1 + seed2)) & 0xFFFFFFFF
        seed1 = (((~seed1 << 0x15) & 0xFFFFFFFF) + 0x11111111 | (seed1 >> 0x0B)) & 0xFFFFFFFF
        seed2 = (value + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
        out += struct.pack("<I", cipher)
    return bytes(out)


def _decrypt_block(data, key):
    """MPQ block cipher, decrypt direction (mpyq-style): the key chain
    evolves over the recovered plaintext words."""
    seed1, seed2 = key, 0xEEEEEEEE
    out = bytearray()
    for i in range(0, len(data) - len(data) % 4, 4):
        seed2 = (seed2 + CRYPT_TABLE[0x400 + (seed1 & 0xFF)]) & 0xFFFFFFFF
        value = struct.unpack_from("<I", data, i)[0]
        value = (value ^ (seed1 + seed2)) & 0xFFFFFFFF
        seed1 = (((~seed1 << 0x15) & 0xFFFFFFFF) + 0x11111111 | (seed1 >> 0x0B)) & 0xFFFFFFFF
        seed2 = (value + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
        out += struct.pack("<I", value)
    return bytes(out)


def _table_key(name):
    return _mpq_hash(name, MPQ_HASH_FILE_KEY)


class MPQWriter:
    """Builds a fresh MPQ v1 archive from an ordered {name: bytes} mapping."""

    def __init__(self, block_size=SECTOR_SIZE):
        self.block_size = block_size
        self.block_exponent = {512: 0, 1024: 1, 2048: 2, 4096: 3}[block_size]
        self.files = {}

    def add(self, name, data):
        assert isinstance(data, bytes)
        assert name not in self.files, name
        self.files[name] = data

    def build(self):
        names = list(self.files)
        hash_size = 16  # fixed small table: our maps hold < 20 files
        while hash_size < 2 * len(names):
            hash_size *= 2

        # wBlockSize in the header is a power-of-two exponent: sector = 512 << n
        assert self.block_size == 512 << self.block_exponent
        header_size = 32
        # file data first, then hash table, then block table
        file_blobs = []
        blocks = []  # (offset, archived_size, real_size, flags)
        pos = header_size
        for name in names:
            data = self.files[name]
            if data:
                n_sectors = max(1, -(-len(data) // self.block_size))
                # Sector offsets are relative to the file block start (the
                # offset table itself is at its head), so entry 0 = table size.
                # StormLib: RawFilePos = block_offset + SectorOffsets[i].
                table_len = 4 * (n_sectors + 1)
                offsets = [table_len]
                for i in range(1, n_sectors + 1):
                    offsets.append(table_len + min(i * self.block_size, len(data)))
                sector_table = struct.pack("<%dI" % len(offsets), *offsets)
                assert offsets[-1] == len(sector_table) + len(data)
                blob = sector_table + data
                blocks.append((pos, len(blob), len(data),
                               FLAG_EXISTS))
            else:  # zero-length file: no sector table
                blob = b""
                blocks.append((pos, 0, 0, FLAG_EXISTS))
            file_blobs.append(blob)
            pos += len(blob)

        hash_offset, block_offset = pos, pos + hash_size * 16
        archive_size = block_offset + len(names) * 16

        header = struct.pack("<4s2I2H4I", b"MPQ\x1a", header_size, archive_size, 0,
                             self.block_exponent, hash_offset, block_offset,
                             hash_size, len(names))
        assert len(header) == header_size

        hash_table = []
        slots = [None] * hash_size
        for i, name in enumerate(names):
            idx = _mpq_hash(name, MPQ_HASH_TABLE_INDEX) % hash_size
            while slots[idx] is not None:
                idx = (idx + 1) % hash_size
            slots[idx] = (i, name)
        for slot in slots:
            if slot is None:
                hash_table.extend([0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF])
            else:
                i, name = slot
                hash_table.extend([_mpq_hash(name, MPQ_HASH_NAME_A),
                                   _mpq_hash(name, MPQ_HASH_NAME_B),
                                   0, i])  # locale/platform 0, block index

        block_table = []
        for i, name in enumerate(names):
            off, arch, real, flags = blocks[i]
            block_table.extend([off, arch, real, flags])

        hash_enc = _encrypt_block(struct.pack("<%dI" % len(hash_table), *hash_table),
                                _table_key("(hash table)"))
        block_enc = _encrypt_block(struct.pack("<%dI" % len(block_table), *block_table),
                                 _table_key("(block table)"))

        out = bytearray(header)
        for blob in file_blobs:
            out += blob
        assert len(out) == hash_offset
        out += hash_enc
        out += block_enc
        return bytes(out)


class MPQReader:
    """Reads back what we write (self-check); mpyq stays the independent referee.
    WC3 maps carry a 512-byte HM3W header before the MPQ archive."""

    def __init__(self, data, base=0):
        self.data = data
        self.base = base
        (magic, self.header_size, self.archive_size, self.format_version,
         block_exponent, hash_off, block_off, hash_size,
         block_size_entries) = struct.unpack_from("<4s2I2H4I", data, base)
        assert magic == b"MPQ\x1a"
        self.block_size = 512 << block_exponent
        self.hash_table = struct.unpack("<%dI" % (hash_size * 4),
                                        _decrypt_block(data[base + hash_off:base + hash_off + hash_size * 16],
                                                     _table_key("(hash table)")))
        self.block_table = struct.unpack("<%dI" % (block_size_entries * 4),
                                         _decrypt_block(data[base + block_off:base + block_off + block_size_entries * 16],
                                                      _table_key("(block table)")))
        # hash entries are 4 words; slots per 4
        self.slots = {}
        for i in range(hash_size):
            name_a, name_b, _lp, block_idx = self.hash_table[i * 4:i * 4 + 4]
            if block_idx < 0xFFFFFFFE:
                self.slots[(name_a, name_b)] = block_idx

    def read(self, name):
        key = (_mpq_hash(name, MPQ_HASH_NAME_A), _mpq_hash(name, MPQ_HASH_NAME_B))
        idx = self.slots[key]
        off, arch, real, flags = self.block_table[idx * 4:idx * 4 + 4]
        assert flags & FLAG_EXISTS and not flags & (0x00000100 | 0x00000200), "stored only"
        if real == 0:
            return b""
        n_sectors = max(1, -(-real // self.block_size))
        offsets = struct.unpack_from("<%dI" % (n_sectors + 1), self.data, base + off)
        # offsets are relative to the file block start (see MPQWriter.build)
        return self.data[base + off + offsets[0]:base + off + offsets[-1]]


if __name__ == "__main__":
    import os
    import random

    random.seed(20261012)
    payloads = {
        "(listfile)": b"(listfile)\r\nwar3map.wts\r\nwar3map.w3i\r\n",
        "war3map.wts": "等等 = 中文字符串测试\r\n".encode("gbk") + b"tiny\r\n",
        "war3map.w3i": bytes(random.randrange(256) for _ in range(10)),
        "war3map.w3e": bytes(random.randrange(256) for _ in range(SECTOR_SIZE + 5)),
        "war3map.doo": bytes(random.randrange(256) for _ in range(SECTOR_SIZE + 1)),
        "war3map.j": bytes(random.randrange(256) for _ in range(3 * SECTOR_SIZE + 77)),
        "war3mapUnits.doo": bytes(random.randrange(256) for _ in range(SECTOR_SIZE * 2 - 1)),
        "war3map.shd": b"",
    }
    path = os.path.join(os.path.dirname(__file__), "dist")
    os.makedirs(path, exist_ok=True)
    target = os.path.join(path, "_selftest.w3x")

    w = MPQWriter()
    for name, data in payloads.items():
        w.add(name, data)
    blob = w.build()
    with open(target, "wb") as f:
        f.write(blob)

    # 1) our own reader round-trip
    r = MPQReader(blob)
    for name, data in payloads.items():
        got = r.read(name)
        assert got == data, "roundtrip mismatch: %s" % name
    # 2) independent referee: mpyq
    from mpyq import MPQArchive

    archive = MPQArchive(target, listfile=False)
    archive.header
    extracted = archive.read_file("(listfile)")
    assert extracted == payloads["(listfile)"]
    assert archive.read_file("war3map.wts") == payloads["war3map.wts"]
    assert archive.read_file("war3map.j") == payloads["war3map.j"]
    assert archive.read_file("war3mapUnits.doo") == payloads["war3mapUnits.doo"]
    os.remove(target)
    print("MPQ self-test OK: %d files, archive %d bytes, both readers agree"
          % (len(payloads), len(blob)))
