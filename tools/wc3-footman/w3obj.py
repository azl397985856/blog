# -*- coding: utf-8 -*-
"""Parse/serialize WC3 object-modification tables (w3u/w3t/w3q/w3a/w3h/w3b).

Format (verified against FF 5.5.3W data + invoker-bot/war3map parser):
  header: int version
  then TWO tables (original objects, then custom objects):
    int count
    per object: char origID[4], char newID[4], int modCount
      per modification: char modID[4], int valueType,
        value: 0=int32, 1=float32, 2=float32(unreal), 3=C-string (null-terminated)
        int end  (junk value in FF maps — the game ignores it; preserved verbatim)

For w3a (abilities), modifications additionally carry level/variation and
dataPointer ints between type and value (useOptionalInts=True).
"""
import struct


class Mod:
    __slots__ = ("mod_id", "value_type", "value", "end", "level", "pointer", "raw_extra")

    def __init__(self):
        self.mod_id = b""
        self.value_type = 0
        self.value = None      # int / float / str (str keeps raw bytes minus null)
        self.end = b""         # preserved 4 bytes
        self.level = None      # w3a only
        self.pointer = None    # w3a only

    def encode(self):
        out = self.mod_id + struct.pack("<I", self.value_type)
        if self.level is not None:
            out += struct.pack("<I", self.level) + struct.pack("<I", self.pointer)
        if self.value_type == 3:
            out += self.value + b"\x00"
        elif self.value_type == 1 or self.value_type == 2:
            out += struct.pack("<f", self.value)
        else:
            out += struct.pack("<i", self.value)
        return out + self.end


class Obj:
    __slots__ = ("orig", "new", "mods")

    def __init__(self, orig, new):
        self.orig = orig
        self.new = new
        self.mods = []

    def get(self, mod_id):
        for m in self.mods:
            if m.mod_id == mod_id:
                return m
        return None

    def set_str(self, mod_id, text, create_type=3):
        m = self.get(mod_id)
        if m is None:
            m = Mod()
            m.mod_id = mod_id
            m.value_type = create_type
            m.end = b"\x00\x00\x00\x00"
            self.mods.append(m)
        m.value = text if isinstance(text, bytes) else text.encode("gbk")

    def encode(self):
        out = self.orig + self.new + struct.pack("<I", len(self.mods))
        for m in self.mods:
            out += m.encode()
        return out


class ObjFile:
    def __init__(self, use_optional_ints=False):
        self.version = 2
        self.tables = [[], []]  # (original, custom)
        self.use_optional_ints = use_optional_ints

    @classmethod
    def parse(cls, data, use_optional_ints=False):
        f = cls(use_optional_ints)
        f.version = struct.unpack_from("<I", data, 0)[0]
        p = 4
        for ti in range(2):
            count = struct.unpack_from("<I", data, p)[0]
            p += 4
            objs = []
            for _ in range(count):
                orig = data[p:p + 4]
                new = data[p + 4:p + 8]
                nmod = struct.unpack_from("<I", data, p + 8)[0]
                p += 12
                obj = Obj(orig, new)
                for _ in range(nmod):
                    m = Mod()
                    m.mod_id = data[p:p + 4]
                    m.value_type = struct.unpack_from("<I", data, p + 4)[0]
                    p += 8
                    if use_optional_ints:
                        m.level = struct.unpack_from("<I", data, p)[0]
                        m.pointer = struct.unpack_from("<I", data, p + 4)[0]
                        p += 8
                    if m.value_type == 3:
                        e = data.index(b"\x00", p)
                        m.value = data[p:e]
                        p = e + 1
                    elif m.value_type in (1, 2):
                        m.value = struct.unpack_from("<f", data, p)[0]
                        p += 4
                    else:
                        m.value = struct.unpack_from("<i", data, p)[0]
                        p += 4
                    m.end = data[p:p + 4]
                    p += 4
                    obj.mods.append(m)
                objs.append(obj)
            f.tables[ti] = objs
        return f

    def encode(self):
        out = struct.pack("<I", self.version)
        for objs in self.tables:
            out += struct.pack("<I", len(objs))
            for obj in objs:
                out += obj.encode()
        return out

    def iter_objs(self):
        for tbl in self.tables:
            yield from tbl

    def find(self, rawcode):
        for obj in self.iter_objs():
            if obj.new == rawcode or (obj.new == b"\x00\x00\x00\x00" and obj.orig == rawcode):
                return obj
        return None
