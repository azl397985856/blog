# -*- coding: utf-8 -*-
"""四兄弟 Footmen Frenzy 构建器 — 基于 FF 5.5.3W 原档做手术式重打包。

原则：
  - 未知名字的原始数据块（模型/贴图导入）按字节原样保留，哈希表项不动
  - 要改的标准文件用我们的修改版替换：改写其哈希槽指向新数据块
  - 新数据块追加在原数据区之后，块表在原 31 项后追加

版本 profile（累积式）：
  v0.3  图标: 四个回忆技能配主题图标（路径全部来自本图内已验证资源）
  v0.4  + 职业色调 tint（uclr/uclg/uclb，安全）
  v0.4m + 实验性模型替换（umdl 换原版英雄模型；绿方块风险隔离在此版）
  v0.5  + 脚本特效层（施法台词浮字 + 特效，动 Scripts\war3map.j）
"""
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mpq import (_decrypt_block, _encrypt_block, _mpq_hash, CRYPT_TABLE,
                 MPQ_HASH_FILE_KEY, MPQ_HASH_NAME_A, MPQ_HASH_NAME_B)
import w3obj

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "base", "Footmen_Frenzy_v5.5.3W.w3x")
EXTRACT = os.path.join(HERE, "base", "ff553_extract")
DIST = os.path.join(HERE, "dist")
SECTOR = 512 << 10  # VxOP 图的扇区指数是 0x0a

STANDARD_NAMES = [
    "war3map.w3i", "war3map.w3e", "war3map.doo", "war3mapUnits.doo", "war3map.wts",
    "Scripts\\war3map.j", "war3map.shd", "war3mapMap.blp", "war3mapPath.map",
    "war3map.imp", "war3map.w3c", "war3map.w3s", "war3map.w3u", "war3map.w3t",
    "war3map.w3a", "war3map.w3h", "war3map.w3b", "war3map.w3q", "war3map.w3r",
    "war3mapMisc.txt", "war3mapSkin.txt", "war3mapExtra.txt",
]

def gbk(s):
    return s.encode("gbk")

# 英雄定义: rawcode -> (名字, 职业称号, 技能表, 色调, 缩放, [v0.4m 模型路径])
# v0.6 重分配: 法官=圣骑士(圣光审判) / 画家=血法师(烈焰作画) / 程序员=剑圣 / 土木=山丘
BROTHERS = {
    b"H005": dict(name="方超", title="法官", uhab="AHhl,AZ01,AHad,AHre",
                  tint=(255, 240, 200), scale=1.06,
                  model=None),
    b"H00A": dict(name="路志远", title="土木工程师", uhab="AHtc,AHtb,AZ02,AHav",
                  tint=(255, 205, 130), scale=1.02,
                  model=None),
    b"O003": dict(name="路志鹏", title="程序员", uhab="AOwk,AZ04,A041,AOww",
                  tint=(150, 180, 255), scale=1.0,
                  model=None),
    b"H009": dict(name="路鹏飞", title="画家", uhab="AHbz,AZ03,AHdr,AHpx",
                  tint=(170, 255, 170), scale=1.0,
                  model=None),
}
# v0.4m 实验模型: 程序员 -> 地精工程师(机器人形态)
BROTHERS[b"O003"]["model_v04m"] = "Units\\Orcs\\HeroTinker\\HeroTinker.mdl"

# 回忆技能: rawcode -> (基础, 名称, 短说明, 长说明, 等级数, 图标, 台词, 施法特效[可为空])
SKILLS = [
    (b"AZ01", b"AHtb", "审判", "|cff99ccff审判|r - 公平正义",
     "法槌落下，公正判决。对目标敌人造成伤害并眩晕。", 3,
     "ReplaceableTextures\\CommandButtons\\BTNStaffOfPurification.blp",
     "本案宣判：有罪！", "Abilities\\Spells\\Human\\ThunderClap\\ThunderClapCaster.mdl"),
    (b"AZ02", b"AOwk", "离家出走", "|cff99ccff离家出走|r",
     "这个家呆不下去了！进入隐身并提升移动速度，下一击附带额外伤害。", 3,
     "ReplaceableTextures\\CommandButtons\\BTNGhostMage.blp",
     "这个家呆不下去了！", ""),
    (b"AZ03", b"AHmt", "我要回家了", "|cff99ccff我要回家了|r - 阳阳在家等我",
     "我要回家了，阳阳在家等我呢！吟唱后传送自己与周围友军到目标友方单位处。", 1,
     "ReplaceableTextures\\CommandButtons\\BTNScroll.blp",
     "我要回家了，阳阳在家等我呢！", ""),
    (b"AZ04", b"AHre", "重启", "|cff99ccff重启|r - 程序员的终极手段",
     "重启一下就好了。复活周围阵亡的友军，让他们重新上线。—— 路志鹏", 1,
     "ReplaceableTextures\\CommandButtons\\BTNPowerGenerator.blp",
     "重启一下就好了。", "Abilities\\Spells\\Human\\Resurrect\\ResurrectCaster.mdl"),
]


# ---------------- 数据改造 ----------------

def make_w3u(profile):
    f = w3obj.ObjFile.parse(open(os.path.join(EXTRACT, "war3map.w3u"), "rb").read())

    def set_int(obj, mod_id, val):
        m = obj.get(mod_id)
        if m is None:
            m = w3obj.Mod()
            m.mod_id = mod_id
            m.value_type = 0
            m.end = b"\x00\x00\x00\x00"
            obj.mods.append(m)
        m.value = val

    for rc, spec in BROTHERS.items():
        obj = f.find(rc)
        assert obj, rc
        full = "%s·%s" % (spec["title"], spec["name"])
        obj.set_str(b"unam", gbk(spec["name"]))
        obj.set_str(b"upro", gbk(full))
        obj.set_str(b"utip", gbk("召唤 |cffffcc00%s|r" % full))
        obj.set_str(b"uhab", spec["uhab"].encode("ascii"))
        if profile.get("tints"):
            r, g, b = spec["tint"]
            set_int(obj, b"uclr", r)
            set_int(obj, b"uclg", g)
            set_int(obj, b"uclb", b)
            set_int(obj, b"ussc", int(100 * spec.get("scale", 1.0)))
        if profile.get("models"):
            model = spec.get("model_v04m") or spec.get("model")
            if model:
                obj.set_str(b"umdl", gbk(model))
    return f.encode()


def make_w3a(profile):
    f = w3obj.ObjFile.parse(open(os.path.join(EXTRACT, "war3map.w3a"), "rb").read(),
                            use_optional_ints=True)

    for (new, orig, name, tip, ext, levels, icon, _quote, _fx) in SKILLS:
        obj = w3obj.Obj(orig, new)
        mods = [(b"anam", 0, name)]
        if profile.get("icons"):
            mods.append((b"aart", 0, icon))
            mods.append((b"arar", 0, icon))
        for lv in range(1, levels + 1):
            mods.append((b"atp%d" % lv, lv, tip))
            mods.append((b"aub%d" % lv, lv, ext))
        for mid, lv, val in mods:
            m = w3obj.Mod()
            m.mod_id = mid
            m.value_type = 3
            m.level = lv
            m.pointer = 0
            m.value = gbk(val)
            m.end = b"\x00\x00\x00\x00"
            obj.mods.append(m)
        f.tables[1].append(obj)
    return f.encode()


def make_wts():
    t = open(os.path.join(EXTRACT, "war3map.wts"), "rb").read().decode("utf-8-sig")
    t = t.replace("Footmen Frenzy 5.5.3 |cffff0000W|r",
                  "四兄弟 Footmen Frenzy |cffffcc00纪念版|r", 1)
    out = []
    for ch in t:
        try:
            ch.encode("gbk")
            out.append(ch)
        except UnicodeEncodeError:
            out.append("-")
    return "".join(out).encode("gbk")


# ---------------- v0.5 脚本特效层 ----------------

FX_JASS = r"""
//============================================================================
// 四兄弟回忆技能 · 施法台词层 (build.py 生成)
//============================================================================
function BFX_Cond takes nothing returns boolean
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
        set fx = "Abilities\\Spells\\Human\\ThunderClap\\ThunderClapCaster.mdl"
    elseif id == 'AZ02' then
        set msg = "|cff88ff88这个家呆不下去了！|r"
    elseif id == 'AZ03' then
        set msg = "|cff88ccff我要回家了，阳阳在家等我呢！|r"
    elseif id == 'AZ04' then
        set msg = "|cff9cb4ff重启一下就好了。|r"
        set fx = "Abilities\\Spells\\Human\\Resurrect\\ResurrectCaster.mdl"
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


# ---------------- v0.6 AI 层 ----------------
# AI 原理: FF 的英雄池和酒馆都是中立被动的, AI 用 IssueNeutralImmediateOrderById
# 走正规购买路径 -> 地图自身的 SELL 记账 / autorevive / 收入系统全部自然生效。
# AI 层只补三件事: 买英雄(轮换池重试) / 自动加点(生成自 w3u 技能表) / 推线与残血回撤。

def ai_pool():
    """(pool_codes, kit表) — 从 w3u 收割 AI 可用英雄及其技能表, 排除四兄弟."""
    f = w3obj.ObjFile.parse(open(os.path.join(EXTRACT, "war3map.w3u"), "rb").read())
    ours = set(BROTHERS)
    standard = {
        b'Hamg': ['AHwe', 'AHbr', 'AHab', 'AHmt'],
        b'Hmkg': ['AHtb', 'AHtc', 'AHbh', 'AHav'],
        b'Hpal': ['AHhl', 'AHzb', 'AHad', 'AHre'],
        b'Hblm': ['AHbz', 'AHbn', 'AHdr', 'AHpx'],
        b'Obla': ['AOwk', 'AOcr', 'AOmi', 'AObl'],
        b'Udea': ['AUcs', 'AUsl', 'AUav', 'AUin'],
    }
    pool = []  # (rawcode_bytes, [skill_bytes...])
    for obj in f.iter_objs():
        rc = obj.new if obj.new != b"\x00\x00\x00\x00" else None
        if not rc or rc in ours or rc[0:1] not in b"OHUE":
            continue
        hab = obj.get(b"uhab")
        base = obj.orig
        kit = None
        if hab and hab.value_type == 3 and hab.value:
            kit = [s.encode("ascii") for s in hab.value.decode().split(",")]
        elif base in standard:
            kit = [s.encode("ascii") for s in standard[base]]
        if kit and len(kit) >= 3:
            pool.append((rc, kit))
    return pool


AI_JASS = r"""function BFX_AI_IsTavern takes nothing returns boolean
    return GetUnitTypeId(GetFilterUnit()) == 'nhef'
endfunction

function BFX_AI_Tavern takes nothing returns unit
    local group g = CreateGroup()
    local unit u = null
    call GroupEnumUnitsOfPlayer(g, Player(15), Condition(function BFX_AI_IsTavern))
    set u = FirstOfGroup(g)
    call DestroyGroup(g)
    return u
endfunction

function BFX_AI_MyHero takes player p returns unit
    local group g = CreateGroup()
    local unit u = null
    local unit hero = null
    call GroupEnumUnitsOfPlayer(g, p, null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        if IsUnitType(u, UNIT_TYPE_HERO) then
            set hero = u
        endif
        call GroupRemoveUnit(g, u)
    endloop
    call DestroyGroup(g)
    return hero
endfunction

function BFX_AI_Kit takes integer h, integer s returns integer
%%KIT%%
    return 0
endfunction

function BFX_AI_Learn takes unit hero, integer h returns nothing
    local integer s = 1
    loop
        exitwhen s > 4
        if GetHeroSkillPoints(hero) > 0 and GetUnitAbilityLevel(hero, BFX_AI_Kit(h, s)) < 1 then
            call SelectHeroSkill(hero, BFX_AI_Kit(h, s))
        endif
        set s = s + 1
    endloop
endfunction

function BFX_AI_Target takes player p returns location
    local integer i = 0
    local integer sl
    loop
        exitwhen i > 11
        if IsPlayerEnemy(p, Player(i)) then
            set sl = GetPlayerStartLocation(Player(i))
            if sl >= 0 then
                return Location(GetStartLocationX(sl), GetStartLocationY(sl))
            endif
        endif
        set i = i + 1
    endloop
    return Location(0.0, -256.0)
endfunction

function BFX_AI_UnitAct takes nothing returns nothing
    local unit u = GetEnumUnit()
    local real hp = GetUnitState(u, UNIT_STATE_LIFE) / GetUnitState(u, UNIT_STATE_MAX_LIFE)
    if hp < 0.30 then
        call IssuePointOrderLocBJ(u, "move", BAI_home)
    elseif DistanceBetweenPoints(u, BAI_home) < 1000.0 then
        call IssuePointOrderLocBJ(u, "attack", BAI_tgt)
    endif
endfunction

function BFX_AI_Pushable takes nothing returns boolean
    local unit u = GetFilterUnit()
    return GetUnitState(u, UNIT_STATE_LIFE) > 0.0 and not IsUnitType(u, UNIT_TYPE_HERO) and not IsUnitType(u, UNIT_TYPE_STRUCTURE)
endfunction

function BFX_AI_HeroAct takes player p, unit hero returns nothing
    local real hp = GetUnitState(hero, UNIT_STATE_LIFE) / GetUnitState(hero, UNIT_STATE_MAX_LIFE)
    if hp < 0.35 then
        call IssuePointOrderLocBJ(hero, "move", BAI_home)
    elseif ModuloInteger(BAI_tick, 3) == 0 then
        call IssuePointOrderLocBJ(hero, "attack", BAI_tgt)
    endif
endfunction

function BFX_AI_Tick takes nothing returns nothing
    local integer i = 0
    local player p
    local unit hero
    local unit tav
    local integer sl
    local group g
    set BAI_tick = BAI_tick + 1
    loop
        exitwhen i >= 12
        set p = Player(i)
        if GetPlayerController(p) == MAP_CONTROL_COMPUTER and GetPlayerSlotState(p) == PLAYER_SLOT_STATE_PLAYING then
            set sl = GetPlayerStartLocation(p)
            if sl >= 0 then
                set BAI_home = Location(GetStartLocationX(sl), GetStartLocationY(sl))
            else
                set BAI_home = Location(0.0, -256.0)
            endif
            set BAI_tgt = BFX_AI_Target(p)
            if BAI_state[i] == 0 then
                set tav = BFX_AI_Tavern()
                if tav != null then
                    call IssueNeutralImmediateOrderById(p, tav, BAI_pool[ModuloInteger(BAI_try[i], BAI_pooln)])
                    set BAI_try[i] = BAI_try[i] + 1
                    set BAI_state[i] = 1
                endif
            elseif BAI_state[i] == 1 then
                set hero = BFX_AI_MyHero(p)
                if hero != null then
                    set BAI_hero[i] = hero
                    set BAI_state[i] = 2
                elseif BAI_try[i] >= BAI_pooln then
                    set BAI_state[i] = 0
                endif
            else
                set hero = BFX_AI_MyHero(p)
                if hero != null then
                    set BAI_hero[i] = hero
                    call BFX_AI_Learn(hero, GetUnitTypeId(hero))
                    call BFX_AI_HeroAct(p, hero)
                    set g = GetUnitsOfPlayerMatching(p, Condition(function BFX_AI_Pushable))
                    call ForGroup(g, function BFX_AI_UnitAct)
                    call DestroyGroup(g)
                endif
            endif
            call RemoveLocation(BAI_home)
            call RemoveLocation(BAI_tgt)
        endif
        set i = i + 1
    endloop
endfunction

function InitBrothersAI takes nothing returns nothing
    local trigger t = CreateTrigger()
%%POOL%%
    set BAI_pooln = %%POOLN%%
    call TriggerRegisterTimerEvent(t, 2.5, true)
    call TriggerAddAction(t, function BFX_AI_Tick)
endfunction
"""


def gen_ai_jass():
    pool = ai_pool()
    kit_lines = []
    for rc, kit in pool:
        kit_lines.append("    if h == '%s' then" % rc.decode())
        for slot, sk in enumerate(kit[:4], 1):
            kit_lines.append("        if s == %d then" % slot)
            kit_lines.append("            return '%s'" % sk.decode())
            kit_lines.append("        endif")
        kit_lines.append("    endif")
    pool_init = []
    for i, (rc, _kit) in enumerate(pool):
        pool_init.append("    set BAI_pool[%d] = '%s'" % (i, rc.decode()))
    ai = AI_JASS.replace("%%KIT%%", "\n".join(kit_lines))
    ai = ai.replace("%%POOL%%", "\n".join(pool_init))
    ai = ai.replace("%%POOLN%%", str(len(pool)))
    return ai


AI_GLOBALS = (b"unit array BAI_hero\rlocation BAI_home\rlocation BAI_tgt\r"
              b"integer array BAI_state\rinteger array BAI_try\rinteger array BAI_pool\r"
              b"integer BAI_pooln\rinteger BAI_tick\r")


def make_j(profile):
    if not profile.get("fx"):
        return open(os.path.join(EXTRACT, "war3map.j"), "rb").read()
    j = open(os.path.join(EXTRACT, "war3map.j"), "rb").read()
    blocks = b""
    calls = b""
    if profile.get("fx"):
        blocks += FX_JASS.encode("gbk").strip(b"\r\n") + b"\r"
        calls += b"    call InitBrothersFX()\r"
    if profile.get("ai"):
        blocks += gen_ai_jass().encode("gbk").strip(b"\r\n") + b"\r"
        calls += b"    call InitBrothersAI()\r"
    # JASS 单遍编译: 函数块插在 main 之前, 调用注入在 main 内部
    i = j.find(b"function main")
    assert i >= 0, "main not found"
    j = j[:i] + blocks + j[i:]
    end = j.find(b"endfunction", j.find(b"function main"))
    assert end >= 0
    j = j[:end] + calls + j[end:]
    if profile.get("ai"):
        g = j.find(b"endglobals")
        assert g >= 0, "globals block not found"
        j = j[:g] + AI_GLOBALS + j[g:]
    return j


# ---------------- 手术式重打包 ----------------

def recover_keys(out0, plain0):
    ks = plain0 ^ out0
    cands = []
    for l in range(256):
        k = (ks - 0xEEEEEEEE - CRYPT_TABLE[0x400 + l]) & 0xFFFFFFFF
        if k & 0xFF == l:
            cands.append(k)
    return cands


def file_blob(data):
    n = max(1, -(-len(data) // SECTOR)) if data else 0
    if not data:
        return b"", 0, 0
    tlen = 4 * (n + 1)
    offs = [tlen] + [tlen + min(i * SECTOR, len(data)) for i in range(1, n + 1)]
    return struct.pack("<%dI" % len(offs), *offs) + data, len(data), len(data) + tlen


def build(replacements, out_path):
    raw = open(SRC, "rb").read()
    base = raw.find(b"MPQ\x1a")
    hash_off, block_off, hash_size, block_cnt = struct.unpack_from("<4I", raw, base + 16)
    ht = struct.unpack("<%dI" % (hash_size * 4),
                       _decrypt_block(raw[base + hash_off:base + hash_off + hash_size * 16],
                                      _mpq_hash("(hash table)", MPQ_HASH_FILE_KEY)))
    bt = struct.unpack("<%dI" % (block_cnt * 4),
                       _decrypt_block(raw[base + block_off:base + block_off + block_cnt * 16],
                                      _mpq_hash("(block table)", MPQ_HASH_FILE_KEY)))
    blocks = [bt[i * 4:(i + 1) * 4] for i in range(block_cnt)]
    data_end = base + hash_off

    slot_of_name = {}
    for name in STANDARD_NAMES:
        na, nb = _mpq_hash(name, MPQ_HASH_NAME_A), _mpq_hash(name, MPQ_HASH_NAME_B)
        for si in range(hash_size):
            if ht[si * 4] == na and ht[si * 4 + 1] == nb:
                slot_of_name[name] = si
                break

    new_entries = []
    blobs = []
    pos = data_end
    new_block_index = {}
    for name, content in replacements.items():
        blob, real, arch = file_blob(content)
        new_block_index[name] = block_cnt + len(new_entries)
        new_entries.append((pos - base, arch, real, 0x80000000))
        blobs.append(blob)
        pos += len(blob)

    new_hash = list(ht)
    for name in replacements:
        si = slot_of_name.get(name)
        if si is None:
            raise SystemExit("no hash slot for %s" % name)
        new_hash[si * 4 + 3] = new_block_index[name]

    new_block_words = list(bt)
    for off, arch, real, flags in new_entries:
        new_block_words += [off, arch, real, flags]
    new_block_cnt = block_cnt + len(new_entries)

    hash_offset = pos - base
    block_offset = hash_offset + hash_size * 16
    archive_size = block_offset + new_block_cnt * 16

    header = struct.pack("<4s2I2H4I", b"MPQ\x1a", 32, archive_size, 0, 10,
                         hash_offset, block_offset, hash_size, new_block_cnt)
    hash_enc = _encrypt_block(struct.pack("<%dI" % len(new_hash), *new_hash),
                              _mpq_hash("(hash table)", MPQ_HASH_FILE_KEY))
    block_enc = _encrypt_block(struct.pack("<%dI" % len(new_block_words), *new_block_words),
                               _mpq_hash("(block table)", MPQ_HASH_FILE_KEY))

    end = raw.index(b"\x00", 8)
    flags, editor = struct.unpack_from("<II", raw, end + 1)
    head = b"HM3W" + struct.pack("<I", 0) + b"FourBrothers FootmenFrenzy 5.5.3W" + b"\x00" + \
        struct.pack("<II", flags, editor)
    hm3w = head + b"\x00" * (base - len(head))

    out = bytearray(hm3w)
    out += header
    out += raw[base + 32:data_end]
    for blob in blobs:
        out += blob
    assert len(out) == base + hash_offset
    out += hash_enc
    out += block_enc

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, "wb").write(bytes(out))
    print("built %s: %d bytes, replaced [%s]" %
          (out_path, len(out), ", ".join(replacements)))


PROFILES = {
    "v0.3": dict(icons=True),
    "v0.4": dict(icons=True, tints=True),
    "v0.4m": dict(icons=True, tints=True, models=True),
    "v0.5": dict(icons=True, tints=True, fx=True),
    "v0.6": dict(icons=True, tints=True, fx=True, ai=True),
    "v0.6m": dict(icons=True, tints=True, fx=True, ai=True, models=True),
}


def build_version(ver):
    profile = PROFILES[ver]
    replacements = {
        "war3map.w3u": make_w3u(profile),
        "war3map.w3a": make_w3a(profile),
        "war3map.wts": make_wts(),
    }
    if profile.get("fx") or profile.get("ai"):
        replacements["Scripts\\war3map.j"] = make_j(profile)
    build(replacements, os.path.join(DIST, "FF_4Brothers_%s.w3x" % ver))


if __name__ == "__main__":
    targets = sys.argv[1:] or ["v0.6", "v0.6m"]
    for ver in targets:
        build_version(ver)
