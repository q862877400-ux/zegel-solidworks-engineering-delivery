"""★ spec 252：`HEM_POSITIONS` 的**真机类型库**复核（把「反射转储」升级为「本机实读」）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/sw_sheet_metal.py（`HEM_POSITIONS` = 0/1，取自**离线反射转储**）
#         tests/test_pattern_enum_alignment.py（`OFFICIAL_HEM_POSITIONS` = 0/1；md 侧 = 1/2）
# 定位:   两源冲突（官方 md 1/2 vs 出厂反射 0/1），铁律 4 取反射；
#         ★★ 但**反射是离线转储，从未在真机上核过** —— 本文件把它补上：
#         ★ 直读**本机装好的** `swconst.tlb`（与离线转储**不同的获取路径**）。
# 官方依据: D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\swconst.tlb（本机 v34.0 常量库）
#           · C:/swapi/enums/swHemPositionTypes_e.md（md 侧，★ 实测**错**）
# 许可:   本仓自产（无外部来源）
# 覆盖:   ★ **只读**：只加载类型库、读常量；★ 不改任何文档、不调用任何建模 API
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import glob
import os
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sw_sheet_metal import HEM_POSITIONS  # noqa: E402

#: ★ 本机实测安装根（★ 枚举在 `swconst.tlb`；接口在 `sldworks.tlb`）。
ROOTS = (r"D:\Program Files\SOLIDWORKS Corp", r"C:\Program Files\SOLIDWORKS Corp",
         r"C:\Program Files (x86)\SOLIDWORKS Corp")

#: ★★ 代码表里的值 → 官方成员名（★ 逐字，用于去类型库里查）。
MEMBERS = {
    "swHemPositionTypeInside": 0,
    "swHemPositionTypeOutside": 1,
}

#: ★★ 官方 **md** 侧的值（★ 实测**错** —— 留作永久负例）。
MD_WRONG = {
    "swHemPositionTypeInside": 1,
    "swHemPositionTypeOutside": 2,
}

#: ★ 下界（★ 只允许增不允许减）。
BASELINE_MEMBERS = 2


def _tlb_enum() -> dict[str, int]:
    """★ 直读本机 SolidWorks 类型库里的 `swHemPosition*` 常量（★ **只读**）。

    ★ 没有类型库 / 没有 comtypes ⇒ 返回 `{}`（★ 调用方 `skip`：缺数据源 ≠ 检查失败）。
    """
    tlbs: list[str] = []
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        tlbs += glob.glob(os.path.join(root, "**", "swconst.tlb"), recursive=True)
    if not tlbs:
        return {}
    try:
        import comtypes.client
        import comtypes.gen as g
        import pkgutil
    except ImportError:                                                # pragma: no cover
        return {}
    for t in sorted(set(tlbs)):
        try:
            comtypes.client.GetModule(t)
        except Exception:                                              # noqa: BLE001
            continue
    out: dict[str, int] = {}
    for m in pkgutil.iter_modules(g.__path__):
        try:
            mod = __import__("comtypes.gen." + m.name, fromlist=["*"])
        except Exception:                                              # noqa: BLE001
            continue
        for attr in dir(mod):
            #: ★★ **必须只收「整数常量」** —— ★ `swHemPositionTypes_e`（枚举**类型本身**）也匹配前缀，
            #:   它是 `ctypes.c_long` 类、**不是值** ⇒ ★ 收进来会让「读数」虚高且不可序列化。
            val = getattr(mod, attr)
            if re.match(r"^swHemPositionType", attr) and isinstance(val, int):
                out[attr] = val
    return out


def _failures(table: dict[str, int], tlb: dict[str, int]) -> list[str]:
    """★ 纯函数：返回问题清单（★ 空 = 通过）。"""
    out: list[str] = []
    if len(tlb) < BASELINE_MEMBERS:
        out.append("类型库里只读到 %d 个 `swHemPositionType*` ⇒ 读取器太窄" % len(tlb))
    for member, want in MEMBERS.items():
        got = tlb.get(member)
        if got is None:
            out.append("类型库里没有 %s" % member)
            continue
        code = table.get(_key_of(member))
        if code is None:
            out.append("代码表 `HEM_POSITIONS` 里没有 %s 对应的键" % member)
            continue
        if code != got:
            out.append("★ %s：代码 %d · 真机类型库 %d ⇒ 不一致" % (member, code, got))
    return out


def _key_of(member: str) -> str:
    """`swHemPositionTypeInside` → `inside`（★ 代码表的键是短名）。"""
    return member.replace("swHemPositionType", "").lower()


# ── ① ★★ 真机类型库必须与代码表一致 ──────────────────────────────────
def test_hem_positions_match_machine_type_library():
    """★★★ 本文件的核心：**本机 `swconst.tlb` 的值必须等于 `HEM_POSITIONS` 的值**。

    ★ 能红的判据：把 `HEM_POSITIONS` 的 `inside` 改成 `1`（= md 的值）⇒ 当场红。
    """
    tlb = _tlb_enum()
    if not tlb:
        pytest.skip("本机没有 SolidWorks 类型库（`swconst.tlb`）⇒ 无数据源（★ 缺数据源 ≠ 检查失败）")
    bad = _failures(HEM_POSITIONS, tlb)
    assert not bad, "真机类型库复核不合格：\n" + "\n".join("  " + b for b in bad)


# ── ② ★ 永久负例：官方 **md** 的值必须**不通过** ──────────────────────
def test_official_md_values_are_rejected_by_machine_type_library():
    """★ 两源冲突的另一侧：官方 md 写 1/2 ⇒ ★ **真机类型库证明它错**（★ 铁律 4 的实证）。"""
    tlb = _tlb_enum()
    if not tlb:
        pytest.skip("本机没有 SolidWorks 类型库 ⇒ 无数据源")
    for member, mdval in MD_WRONG.items():
        got = tlb.get(member)
        assert got is not None, "类型库里没有 %s" % member
        assert mdval != got, (
            "负例失效：%s 的 md 值 %d 竟等于真机类型库值 ⇒ 本负例无意义" % (member, mdval))


# ── ③ 下界 + 读取器自证 ───────────────────────────────────────────────
def test_type_library_reader_is_not_too_narrow():
    """★ 读取器必须真读到 ≥2 个成员（★ 否则「读不到」与「全通过」同形）。"""
    tlb = _tlb_enum()
    if not tlb:
        pytest.skip("本机没有 SolidWorks 类型库 ⇒ 无数据源")
    assert len(tlb) >= BASELINE_MEMBERS, \
        "只读到 %d 个 `swHemPositionType*` ⇒ 读取器太窄：%s" % (len(tlb), sorted(tlb))
    assert set(MEMBERS) <= set(tlb), \
        "本文件要核的成员没被读到：%s" % sorted(set(MEMBERS) - set(tlb))


# ── ④ ★★ 纯函数**能红**（合成负例）──────────────────────────────────
def test_pure_function_is_red_able():
    """★ 合成负例：把代码表改成 md 的值 ⇒ 纯函数必须报出 2 条不一致。"""
    tlb = {"swHemPositionTypeInside": 0, "swHemPositionTypeOutside": 1}
    good = {"inside": 0, "outside": 1}
    badt = {"inside": 1, "outside": 2}
    assert not _failures(good, tlb), "正常表被判红 ⇒ 判据过严"
    assert len(_failures(badt, tlb)) == 2, "改成 md 值却未被判出 ⇒ **空判据**"
    assert len(_failures(good, {})) >= 1, "类型库为空时未被判出 ⇒ 读取器下界失效"
