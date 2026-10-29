# -*- coding: utf-8 -*-
r"""Transplant the four brothers' memorial skills (AZ01-AZ04) into F45_BROTHERS.w3x
via in-place MPQ block surgery.

F4.5's object system is full-replacement SLK/TXT at standard game paths:
  blk036 = Units\AbilityData.slk      — numeric rows (87 cols, Y=2..943)
  blk071 = ability text INI           — 942 [A*]/[S*] sections, UTF-8 CRLF
  blk142 = Units\UnitAbilities.slk    — heroAbilList per hero
  blk178 = war3map.j                  — YDWE script; gets the BFX cast-line trigger

Skill design (from build.py SKILLS, adapted to FF 6-level idiom):
  AZ01 审判      = code AHtb (storm bolt)   6lv skip3 req1  → H005 方超（法官）
  AZ02 离家出走  = code AOwk (wind walk)    6lv skip3 req1  → H00A 路志远（土木）
  AZ03 我要回家了 = code AHmt (mass teleport) 3lv skip5 req6  → H009 路鹏飞（画家）
  AZ04 重启      = code AHre (resurrect)    1lv req6        → O003 路志鹏（程序员）
Base rows are copied verbatim (numeric behaviour = the base skill, same as the
v0.6s binary approach that had zero numeric mods); AZ04's resurrect base is
absent from the map's table, so its row is minimal and relies on engine class
defaults (same as A011/A011-style minimal rows that ship in the map).

Output: F45_BROTHERS_SKILL.w3x next to the source file, HM3W renamed to
"FF4B SKILLS F45" (ASCII, same byte length as "FF F4.5 CHINESE").
"""
import os
import re
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from f45surgery import F45Map, BASE, verify_pair

SRC = os.path.expanduser("~/wc3-test/fixpack/F45_BROTHERS.w3x")
DST = os.path.expanduser("~/wc3-test/fixpack/F45_BROTHERS_SKILL.w3x")

# blk182 = the REAL war3map.j the game reads (hash slot locale0/platform0).
# blk178 (platform 0xFF00) is a stale shadow block the game ignores — the
# 2026-10-29 dialog rename went there and was a no-op. Storm-encrypted:
# sector table key K, sector spans (mask byte included) encrypted with K+1+s.
STORM_KEY = 0x5486BEAF
REAL_J_BLOCK = 182

DIALOG_RENAMES = [
    ('DialogAddButtonBJ(udg_ChooseHero,"皇帝")', 'DialogAddButtonBJ(udg_ChooseHero,"方超（法官）")'),
    ('DialogAddButtonBJ(udg_ChooseHero,"狙击手")', 'DialogAddButtonBJ(udg_ChooseHero,"路志鹏（程序员）")'),
    ('DialogAddButtonBJ(udg_ChooseHero,"魔法师")', 'DialogAddButtonBJ(udg_ChooseHero,"路鹏飞（画家）")'),
    ('DialogAddButtonBJ(udg_ChooseHero,"恶魔猎手")', 'DialogAddButtonBJ(udg_ChooseHero,"路志远（土木工程师）")'),
]

# blk182's slot is exactly full; these file-DEFINED identifiers (globals and
# script-local functions, never natives/BJ wrappers) are renamed to short
# forms to fund the BFX trigger injection. Textual \b replace-all is safe:
# the script has zero dynamic ExecuteFunc, and string literals referencing
# function names are renamed together with the definitions.
BASE_RENAMES = [
    ("YDWETriggerRegisterEnterRectSimpleNull", "yd_trerm"),
    ("YDWEGetUnitsInRangeOfLocMatchingNull", "yd_gurml"),
    ("YDWEGetUnitsOfPlayerMatchingNull", "yd_guopm"),
    ("YDWEBase___AbilityCastingOverEventNumber", "yd_abcev"),
    ("udg_suijingyingxiongX", "udg_sjyX"),
    ("udg_fengbaojianglindanwei", "udg_fbjldw"),
    ("udg_mubiaodanwei", "udg_mbdw"),
    ("udg_chufadanwei", "udg_cfdw"),
]

EXTRA_RENAMES = [  # applied in order until the compressed blob fits the slot
    ("YDWEBase___yd_PlayerColor", "yd_pcol"),
    ("udg_shifangdian", "udg_sfd"),
    ("udg_bikaqiumubiao", "udg_bkmb"),
    ("YDWETimerSystem___TaskListNext", "yd_tsnx"),
    ("YDWETimerDestroyEffect", "yd_tdes"),
    ("udg_bikaqiuweizhi", "udg_bkwz"),
    ("YDWEPolledWaitNull", "yd_pwait"),
    ("udg_jianrenfengbao", "udg_jrfb"),
    ("udg_mubiaodian", "udg_mbd"),
    ("udg_jiuguan", "udg_jg1"),
    ("YDWERPGGetKey", "yd_rgk"),
    ("udg_shijian", "udg_sj12"),
]

IDENTIFIER_RENAMES = BASE_RENAMES
HERO_APPEND = {
    "H005": ("AHhb,AHds,A04Y,A0FL,A011", "AZ01"),
    "H00A": ("AHtc,AHtb,A00D,AHav,A01C", "AZ02"),
    "H009": ("AHfs,AHbn,AHpx,A0EL,A014", "AZ03"),
    "O003": ("AOwk,A01N,A00G,AOmi,AOww", "AZ04"),
}

BTN = {
    "AZ01": "ReplaceableTextures\\CommandButtons\\BTNStaffOfPurification.blp",
    "AZ02": "ReplaceableTextures\\CommandButtons\\BTNGhostMage.blp",
    "AZ03": "ReplaceableTextures\\CommandButtons\\BTNScroll.blp",
    "AZ04": "ReplaceableTextures\\CommandButtons\\BTNPowerGenerator.blp",
}


def section(id_, fields):
    body = "\r\n".join("%s=%s" % (k, v) for k, v in fields)
    return "[%s]\r\n%s\r\n" % (id_, body)


def lvtip(name, hk, n):
    return ",".join("%s(|cffffcc00%s|r) - [|cffffcc00等级 %d|r]" % (name, hk, i) for i in range(1, n + 1))


def build_text_sections():
    """blk071 sections mirroring the file's own field style (sorted fields,
    Tip/Ubertip comma-per-level, Research* for the learn button). Text is kept
    compact — blk071's slot has only ~100 compressed bytes of slack."""
    secs = []
    secs.append(section("AZ01", [
        ("Art", BTN["AZ01"]),
        ("Buttonpos", "4,2"),
        ("Hotkey", "F"),
        ("Name", "审判"),
        ("ResearchArt", BTN["AZ01"]),
        ("Researchbuttonpos", "4,2"),
        ("Researchhotkey", "F"),
        ("Researchtip", "学习审判(|cffffcc00F|r) - [|cffffcc00等级 %d|r]"),
        ("Researchubertip", "法槌落下，公正判决。掷出法槌伤害并眩晕目标敌人。"),
        ("Tip", lvtip("审判", "F", 6)),
        ("Ubertip", ",".join(
            "造成%d点伤害，眩晕%d秒。" % (dmg, st)
            for dmg, st in [(200, 2), (400, 3), (600, 4), (800, 5), (800, 5), (800, 5)])),
    ]))
    secs.append(section("AZ02", [
        ("Art", BTN["AZ02"]),
        ("Buttonpos", "4,2"),
        ("Hotkey", "G"),
        ("Name", "离家出走"),
        ("ResearchArt", BTN["AZ02"]),
        ("Researchbuttonpos", "4,2"),
        ("Researchhotkey", "G"),
        ("Researchtip", "学习离家出走(|cffffcc00G|r) - [|cffffcc00等级 %d|r]"),
        ("Researchubertip", "这个家呆不下去了！隐身并加速，破隐一击附带额外伤害。"),
        ("Tip", lvtip("离家出走", "G", 6)),
        ("Ubertip", ",".join(
            "隐身并加速，持续%d秒。破隐一击造成%d点额外伤害。"
            % (dur, dmg) for dur, dmg in [(20, 200), (40, 400), (60, 600), (60, 800), (60, 800), (60, 800)])),
    ]))
    secs.append(section("AZ03", [
        ("Art", BTN["AZ03"]),
        ("Buttonpos", "4,2"),
        ("Hotkey", "T"),
        ("Name", "我要回家了"),
        ("ResearchArt", BTN["AZ03"]),
        ("Researchbuttonpos", "4,2"),
        ("Researchhotkey", "T"),
        ("Researchtip", "学习我要回家了(|cffffcc00T|r) - [|cffffcc00等级 %d|r]"),
        ("Researchubertip", "阳阳在家等我呢！传送自己与周围友军。"),
        ("Tip", lvtip("我要回家了", "T", 3)),
        ("Ubertip", ",".join(["阳阳在家等我！传送自己与周围友军到目标友方单位处。"] * 3)),
    ]))
    secs.append(section("AZ04", [
        ("Art", BTN["AZ04"]),
        ("Buttonpos", "4,2"),
        ("Hotkey", "V"),
        ("Name", "重启"),
        ("ResearchArt", BTN["AZ04"]),
        ("Researchbuttonpos", "4,2"),
        ("Researchhotkey", "V"),
        ("Researchtip", "学习重启(|cffffcc00V|r)"),
        ("Researchubertip", "重启一下就好了。复活周围阵亡的友军。—— 路志鹏"),
        ("Tip", "重启(|cffffcc00V|r)"),
        ("Ubertip", "重启一下就好了。复活周围阵亡的友军。—— 路志鹏"),
    ]))
    return "\r\n".join(secs)


BFX_JASS = """function BFX_Cond takes nothing returns boolean
    local integer id = GetSpellAbilityId()
    return id == 'AZ01' or id == 'AZ02' or id == 'AZ03' or id == 'AZ04'
endfunction

function BFX_Act takes nothing returns nothing
    local integer id = GetSpellAbilityId()
    local unit u = GetTriggerUnit()
    local texttag tt = CreateTextTag()
    local string msg = ""
    local string fx = ""
    if id == 'AZ01' then
        set msg = "|cffffcc00本案宣判：有罪！|r"
        set fx = "Abilities\\\\Spells\\\\Human\\\\ThunderClap\\\\ThunderClapCaster.mdl"
    elseif id == 'AZ02' then
        set msg = "|cff88ff88这个家呆不下去了！|r"
    elseif id == 'AZ03' then
        set msg = "|cff88ccff我要回家了，阳阳在家等我呢！|r"
    elseif id == 'AZ04' then
        set msg = "|cff9cb4ff重启一下就好了。|r"
        set fx = "Abilities\\\\Spells\\\\Human\\\\Resurrect\\\\ResurrectCaster.mdl"
    endif
    call SetTextTagText(tt, msg, 0.030)
    call SetTextTagPosUnit(tt, u, 80.0)
    call SetTextTagColor(tt, 255, 230, 140, 255)
    call SetTextTagVelocity(tt, 0.0, 0.035)
    call SetTextTagFadepoint(tt, 2.4)
    call SetTextTagLifespan(tt, 3.2)
    call SetTextTagPermanent(tt, false)
    if fx != "" then
        call AddSpecialEffectTarget(fx, u, "origin")
    endif
    set u = null
endfunction

function InitBrothersFX takes nothing returns nothing
    local trigger t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddCondition(t, Condition(function BFX_Cond))
    call TriggerAddAction(t, function BFX_Act)
endfunction

"""


def patch_ability_data(text):
    """Append AZ01-04 rows: verbatim copy of the base rows' C-lines with the
    alias cell rewritten; AZ04 gets a minimal row. Updates the B;..Y header."""
    rows = {}
    for mm in re.finditer(r'C;X1;Y(\d+);K"([A-Za-z0-9]+)"', text):
        rows.setdefault(mm.group(2), int(mm.group(1)))
    last_y = max(rows.values())
    assert last_y == 943, last_y

    def row_segment(alias):
        y = rows[alias]
        # find the segment [first line of Y..first line of next Y)
        bounds = sorted(y2 for y2 in rows.values() if y2 > y)
        y_end = bounds[0] if bounds else None
        start = text.index('C;X1;Y%d;' % y)
        end = text.index('C;X1;Y%d;' % y_end) if y_end else len(text)
        return text[start:end]

    def renumber(seg, new_y, new_alias):
        seg = re.sub(r'C;X1;Y\d+;', 'C;X1;Y%d;' % new_y, seg, count=1)
        seg = re.sub(r'C;X1;Y%d;K"[A-Za-z0-9]+"' % new_y,
                     'C;X1;Y%d;K"%s"' % (new_y, new_alias), seg, count=1)
        return seg

    out = text
    plan = [("AHtb", "AZ01"), ("AOwk", "AZ02"), ("AHmt", "AZ03")]
    new_y = last_y + 1
    for base, az in plan:
        seg = row_segment(base)
        out += renumber(seg, new_y, az)
        new_y += 1
    # AZ04 minimal resurrect row (engine class defaults, like A011's style)
    out += ('C;X1;Y%d;K"AZ04"\r\nC;X2;K"AHre"\r\nC;X15;K1\r\nC;X72;K1\r\n'
            'C;X75;K6\r\n' % new_y)
    out = out.replace("B;X87;Y%d;D0" % last_y, "B;X87;Y%d;D0" % (last_y + 4))
    return out


def patch_hero_abilities(text):
    for hero, (old, az) in HERO_APPEND.items():
        needle = 'K"%s"' % old
        assert text.count(needle) == 1, (hero, text.count(needle))
        text = text.replace(needle, 'K"%s,%s"' % (old, az))
    return text


def patch_script_real(raw):
    """Inject BFX + dialog renames into the REAL war3map.j (blk182).
    Layout: UTF-8 JASS body + a GBK comment tail (//55YOU injector banners)."""
    cut = raw.rfind(b"endfunction\r\n")
    assert cut > 0
    cut += len("endfunction\r\n")
    body, tail = raw[:cut], raw[cut:]
    j = body.decode("utf-8")

    for old, new in DIALOG_RENAMES:
        assert j.count(old) == 1, (old, j.count(old))
        j = j.replace(old, new)

    for old, new in IDENTIFIER_RENAMES:
        assert not re.search(r'\b%s\b' % re.escape(new), j), "new name collides: " + new
        assert re.search(r'\b%s\b' % re.escape(old), j), "old name absent: " + old
        j = re.sub(r'\b%s\b' % re.escape(old), new, j)

    assert "BFX_Cond" not in j and "InitBrothersFX" not in j
    main_head = "function main takes nothing returns nothing"
    assert j.count(main_head) == 1
    j = j.replace(main_head, BFX_JASS + main_head, 1)
    anchor = "call InitCustomTriggers()\r\ncall RunInitializationTriggers()"
    assert j.count(anchor) == 1, "InitBrothersFX anchor missing"
    j = j.replace(
        anchor, "call InitCustomTriggers()\r\ncall InitBrothersFX()\r\ncall RunInitializationTriggers()")

    # U+FEFF BOMs sit mid-file on some function lines (YDWE assembly artifact,
    # tolerated by the game) — strip them before counting
    nf = sum(1 for l in j.splitlines() if l.lstrip("﻿").strip().startswith("function "))
    ne = sum(1 for l in j.splitlines() if l.strip() == "endfunction")
    assert nf == ne, "JASS unbalanced: %d vs %d" % (nf, ne)
    return j.encode("utf-8") + tail  # native CRLF kept verbatim


def patch_hm3w(data, new_name):
    """Same-length ASCII rename, tail after NUL preserved."""
    assert len(new_name.encode("ascii")) == 15
    out = bytearray(data)
    old = bytes(out[8:out.index(b"\0", 8)])
    assert len(old) == len(new_name), (old, new_name)
    out[8:8 + len(new_name)] = new_name.encode("ascii")
    return bytes(out)


def main():
    m = F45Map.open(SRC)
    expected = {}

    ini = m.read_block(71)
    assert ini.endswith(b"\r\n") and b"[AZ01]" not in ini
    expected[71] = ini + build_text_sections().encode("utf-8")

    ad = m.read_block(36).decode("utf-8")
    assert not re.search(r'AZ0\d', ad)
    expected[36] = patch_ability_data(ad).encode("utf-8")

    ua = m.read_block(142).decode("utf-8")
    expected[142] = patch_hero_abilities(ua).encode("utf-8")

    # Tail budget for the grown real-script block: archive tail minus the tiny
    # sibling block (blk183, cipher snapshot needed — the grown blob overwrites
    # it), the hash table, and the block table (all 184 entries — the zero-size
    # entries are real empty-file overrides, not free slots).
    used = [i for i in range(m.block_n) if m.block(i)[1] or m.block(i)[2]]
    assert REAL_J_BLOCK in used and used[-1] == 183
    sib_raw = {183: bytes(m.data[BASE + m.block(183)[0]:BASE + m.block(183)[0] + m.block(183)[1]])}
    archive_size = struct.unpack_from("<I", m.data, BASE + 8)[0]
    budget = archive_size - m.block(REAL_J_BLOCK)[0] - len(sib_raw[183]) - 4096 - 184 * 16

    real_j = m.read_block_storm(REAL_J_BLOCK, STORM_KEY)
    # Self-adaptive slot fit: rename file-defined identifiers (highest
    # byte-yield first, short target names) until the recompressed blob fits.
    self_mod = sys.modules[__name__]
    cand_pool = []
    seen = {o for o, _ in BASE_RENAMES}
    defined = set(re.findall(r'^function\s+([A-Za-z_][A-Za-z0-9_]*)', real_j.decode("utf-8", "replace"), re.M))
    gb = real_j.decode("utf-8", "replace")
    gb = gb[:gb.find("\nfunction")]
    for line in gb.splitlines():
        s = line.strip()
        mm = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s+(\w+)$', s)
        if mm: defined.add(mm.group(1))
        mm = re.match(r'^(\w+)\s+array\s+([A-Za-z_][A-Za-z0-9_]*)$', s)
        if mm: defined.add(mm.group(2))
    body_txt = real_j.decode("utf-8", "replace")
    used_short = {n for _, n in BASE_RENAMES}
    short_letters = "abcdefghijklmnopqrstuvwxyz"
    short_names = (["yd_" + a for a in short_letters] +
                   ["udg_" + a for a in short_letters] +
                   ["yd_" + a + b for a in short_letters for b in short_letters])
    si = 0
    for k in sorted(defined, key=lambda x: -len(re.findall(r'\b%s\b' % re.escape(x), body_txt)) * (len(x) - 6)):
        if k in seen or len(k) <= 10 or k.startswith("yd_"):
            continue
        n = len(re.findall(r'\b%s\b' % re.escape(k), body_txt))
        if n < 5:
            break
        while si < len(short_names) and (short_names[si] in used_short or re.search(r"\b%s\b" % short_names[si], body_txt)):
            si += 1
        if si >= len(short_names):
            break
        cand_pool.append((k, short_names[si]))
        used_short.add(short_names[si])
        seen.add(k)
        si += 1

    def _best_sec(sec):
        best = None
        for st in (zlib.Z_DEFAULT_STRATEGY, zlib.Z_FILTERED, zlib.Z_RLE):
            for ml in (8, 9):
                c = zlib.compressobj(9, zlib.DEFLATED, 15, ml, st)
                b = c.compress(sec) + c.flush()
                if best is None or len(b) < len(best):
                    best = b
        return best

    self_mod.IDENTIFIER_RENAMES = list(BASE_RENAMES)
    n_extra = 0
    while True:
        expected[REAL_J_BLOCK] = patch_script_real(real_j)
        n_sec = max(1, -(-len(expected[REAL_J_BLOCK]) // m.sector_size))
        approx = 4 * (n_sec + 1) + sum(1 + len(_best_sec(expected[REAL_J_BLOCK][s*m.sector_size:(s+1)*m.sector_size])) for s in range(n_sec))
        if approx <= budget:
            break
        if n_extra >= len(cand_pool):
            raise SystemExit("cannot fit blk182 even with all candidate renames")
        self_mod.IDENTIFIER_RENAMES = list(BASE_RENAMES) + cand_pool[:n_extra + 1]
        n_extra += 1
    # rebuild the rename pairs actually used (old, new)
    self_mod.IDENTIFIER_RENAMES = (list(BASE_RENAMES) + cand_pool[:n_extra])
    print("identifier renames: %d base + %d extra" % (len(BASE_RENAMES), n_extra))
    # (expected[REAL_J_BLOCK] already holds the final patched content)


    for idx, content in expected.items():
        if idx == REAL_J_BLOCK:
            csize = m.write_block_storm(idx, content, STORM_KEY, limit=budget)
        else:
            csize = m.write_block(idx, content)  # raises if a slot runs out
        print("blk%03d: rsize %d -> %d, csize %d (budget %d)" % (
            idx, m.block(idx)[2], len(content), csize, budget if idx == REAL_J_BLOCK else m.block(idx)[1]))

    data = patch_hm3w(bytes(m.data), "FF4B SKILLS F45")
    m.data = bytearray(data)
    info = m.save_relocated_tail(DST)
    print("saved", DST, info)

    # ---- verification ----
    dst = F45Map.open(DST)
    for idx, content in expected.items():
        if idx == REAL_J_BLOCK:
            got = dst.read_block_storm(idx, STORM_KEY)
        else:
            got = dst.read_block(idx)
        assert got == content, "blk%d roundtrip mismatch" % idx
    # every untouched block must survive relocation byte-identically
    for i in used:
        if i in expected:
            continue
        if m.block(i)[2] and m.block(i)[3] & 0x030000:
            ra = bytes(m.data[BASE + m.block(i)[0]:BASE + m.block(i)[0] + m.block(i)[1]])
            rb = bytes(dst.data[BASE + dst.block(i)[0]:BASE + dst.block(i)[0] + dst.block(i)[1]])
            assert ra == rb, "blk%d cipher bytes changed" % i
            continue
        assert m.read_block(i) == dst.read_block(i), "blk%d changed" % i
    # hash table must be fully identical (no remap)
    assert m.hash_table == dst.hash_table, "hash table changed!"

    # semantics spot checks
    ad2 = dst.read_block(36).decode("utf-8")
    for az in ("AZ01", "AZ02", "AZ03", "AZ04"):
        assert re.search(r'K"%s"' % az, ad2)
    j2 = dst.read_block_storm(REAL_J_BLOCK, STORM_KEY)
    body = j2.decode("utf-8", "replace")  # whole file; GBK tail has none of these markers
    assert body.count("InitBrothersFX") == 2, body.count("InitBrothersFX")  # definition + call in main
    assert "call InitBrothersFX()" in body.split("function main")[-1]
    for old, new in DIALOG_RENAMES:
        assert body.count(new) == 1, new

    try:
        import io
        from mpyq import MPQArchive
        with open(DST, "rb") as f:
            arch = MPQArchive(io.BytesIO(f.read()[512:]), listfile=False)  # strip HM3W
        for name in ("Units\\AbilityData.slk", "Units\\UnitAbilities.slk"):
            blob = arch.read_file(name, force_decompress=True)
            assert blob, name
        print("mpyq referee: hash probe + SLK blocks readable OK")
    except Exception as e:
        print("mpyq check FAILED: %s" % e)
        raise

    print("\n=== final hero skill lists ===")
    ua2 = dst.read_block(142).decode("utf-8")
    for hero, (old, az) in HERO_APPEND.items():
        assert 'K"%s,%s"' % (old, az) in ua2, hero
        print("%s: %s,%s" % (hero, old, az))
    print("OK ->", DST)


if __name__ == "__main__":
    main()
