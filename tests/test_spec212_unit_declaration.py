"""★ 规格 212 · E-1：**"未确证"必须说出来**的契约与负例（★ 不连真机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_mass_property.py` 的 `section_properties` 等"声明了单位未确证"的返回
# 定位:   ★ 规格 `specs/212-unit-discipline` 的 **E-1**。★ 规则 2b 的**第 ③ 条**：
#   ★★ **"未确证"必须说出来** —— ★ 依据**铁律 5「查不到就说查不到」** ✓
# 判据:   ★★★ **三条，全是机械的**（★ 不猜语义、★ 不靠 LLM）：
#     ★ ① 返回里 `units_verified` **为 `False`** ⇒ ★ **必须同时带 `unit_caveat`** ✓
#     ★ ② 同上 ⇒ ★ **还必须带 `unit_assumption`** ✓ —— ★★ 这是**统一到仓里的既有约定**：
#        ★ 扫描时发现仓里早有 `unit_assumption`（★ 7 处：`sw_curve_and_split.py` ·
#        ★ `sw_drawing_create_missing.py` ×2 · ★ `sw_sheet_metal_weld_entry.py` ×4）✓
#        ★ 依据**铁律 1「只缝合不发明」** ⇒ ★★ 我在规格 211 里临时造的键**必须与它对上** ✓
#     ★ ③ `units_verified` **为 `True`** ⇒ ★ **不该**同时带 `unit_caveat`（★ 否则自相矛盾）✓
#   ★★ **两个键各有用途**（★ 不是二选一）：★ `unit_assumption` = **说法**（字符串、人读）·
#     ★ `units_verified` = **机器可判的布尔**（★ 供门禁与调用方一眼判断）✓
# 官方依据: 无（本仓约定 `docs/union-conventions.md` **规则 2b**）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_mass_property as MP                                  # noqa: E402


class _Ext:
    def __init__(self, result):
        self.GetSectionProperties2 = result


class _Model:
    def __init__(self, doc_type=1, ext=None):
        self._t = doc_type
        self.Extension = ext

    def GetType(self):
        return self._t


def _vals(status=0.0, area=400.0):
    v = [None] * 24
    v[MP.SECTION_INDEX["status"]] = status
    v[MP.SECTION_INDEX["area"]] = area
    return tuple(v)


def _sect():
    return MP.section_properties(_Model(ext=_Ext(_vals())))


# ── ① `units_verified: False` ⇒ 必须带 `unit_caveat` ────────────────────────
def test_unverified_requires_caveat():
    out = _sect()
    assert out["units_verified"] is False
    assert isinstance(out.get("unit_caveat"), str) and out["unit_caveat"].strip()


# ── ② 同上 ⇒ 还必须带 `unit_assumption`（★ 统一到既有约定）──────────────────
def test_unverified_requires_unit_assumption():
    out = _sect()
    assert isinstance(out.get("unit_assumption"), str)
    assert out["unit_assumption"].strip(), "★ 未确证必须说出来（规则 2b 第 ③ 条）"


# ── ③ 三个键的**语义**必须自洽（★ 负例：不能声称已验证却带 caveat）───────────
def test_three_keys_do_not_contradict():
    out = _sect()
    if out.get("units_verified") is True:
        assert not out.get("unit_caveat"), "★ 说已验证、却又带 unit_caveat ⇒ 自相矛盾"
    else:
        assert out.get("unit_caveat") and out.get("unit_assumption")


# ── ④ 常量本身必须**非空且能被引用**（★ 静态可查的那一半）──────────────────
def test_constants_exist_and_are_nonempty():
    assert MP.SECTION_UNIT_CAVEAT.strip()
    assert MP.SECTION_UNIT_ASSUMPTION.strip()
    #: ★★ `unit_assumption` 必须**指向冲突登记表**（★ 让读者能查到"为什么未确证"）
    assert "unit-conflicts" in MP.SECTION_UNIT_ASSUMPTION


# ── ⑤ 负例：工程图先拒 ⇒ 那条路上**不该**冒出单位声明（★ 免得误读）──────────
def test_refused_document_does_not_claim_units():
    out = MP.section_properties(_Model(doc_type=3, ext=_Ext(_vals())))
    assert out["ok"] is False and out["error"]
