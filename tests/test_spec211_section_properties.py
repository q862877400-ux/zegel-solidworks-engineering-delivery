"""★ 规格 211 · B1-1「截面属性」的契约与负例（★ 不连真机，★ 假件判据）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_mass_property.py` 的 `section_properties` / `section_area_crosscheck`
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B1-1**。★ 真机三条事实（见该模块 docstring）：
#   ★ ① 入口是**当属性取**（`type` 是 `tuple`、`callable` 假、**求值即得结果**）·
#   ★ ② 它吃**当前选择集** · ★ ③ 它**有清空并重写选择集的副作用** ✓
# 判据:   ★★ **契约**：`status=0`+`area` 能读出来；★ 工程图必须**先拒**（同质量属性那条教训）✓
#   ★★ **负例（两条，都是"必然失败"）**：
#     · **工程图**（`GetType()=3`）⇒ 必须 `ok=False` 且**不抛**（★ 与 `mass_property_object` 同判据）✓
#     · **Entry 不存在**（假 `Extension` 没有该成员）⇒ 必须 `ok=False` + 有空 `error` ✓
#   ★★ 并**钉住副作用声明**：★ `SECTION_SIDE_EFFECT` 必须存在且非空
#     —— ★ 因为按**规格 210** 的效应声明体系，★ 这条决定了它**不许被标 `read_only`** ✓
# 官方依据: `C:\swapi\types\IModelDocExtension\GetSectionProperties2.md`（24 元 + status 取值）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_mass_property as MP                                  # noqa: E402


class _Ext:
    """★ 假 `Extension`：★ 把 `GetSectionProperties2` 放成**属性**（★ 真机就是这一形态）✓"""

    def __init__(self, result=None):
        if result is not None:
            self.GetSectionProperties2 = result


class _Model:
    def __init__(self, doc_type=1, ext=None):
        self._t = doc_type
        self.Extension = ext

    def GetType(self):
        return self._t


def _vals(status=0.0, area=400.0, **kw):
    """★ 造一个**官方 24 元**形态的返回（★ 下标按 `SECTION_INDEX`）✓"""
    v = [None] * 24
    v[MP.SECTION_INDEX["status"]] = status
    v[MP.SECTION_INDEX["area"]] = area
    v[MP.SECTION_INDEX["centroid_x"]] = kw.get("cx", 10.0)
    v[MP.SECTION_INDEX["centroid_y"]] = kw.get("cy", 10.0)
    v[MP.SECTION_INDEX["centroid_z"]] = kw.get("cz", 0.0)
    return tuple(v)


def test_section_index_and_status_are_documented():
    """★ 契约：★ 官方下标与 status 取值**都要在代码里**（★ 不许散落在调用方）✓"""
    assert MP.SECTION_INDEX["status"] == 0 and MP.SECTION_INDEX["area"] == 1
    assert MP.SECTION_STATUS[0] == "success"
    assert MP.SECTION_STATUS[2] == "selected faces are not in the same or parallel planes"
    assert MP.SECTION_STATUS[3] == "unable to compute section properties"


def test_side_effect_is_declared():
    """★★ **副作用必须被声明** —— ★ 按**规格 210**，★ 这条决定它**不许被标 `read_only`** ✓"""
    assert MP.SECTION_SIDE_EFFECT == "clears_and_rewrites_selection"
    assert MP.SECTION_UNIT_CAVEAT.strip(), "★ 单位未确证的限度必须写出来（铁律 5）"


def test_reads_status_area_and_centroid_from_the_property_form():
    out = MP.section_properties(_Model(ext=_Ext(_vals(area=400.0))))
    assert out["ok"] is True and out["status"] == 0.0
    assert out["status_text"] == "success"
    assert out["area"] == 400.0 and out["centroid"] == [10.0, 10.0, 0.0]
    assert out["units_verified"] is False, "★ 单位未确证时不许说已验证"
    assert "property" in out["entry_used"]


def test_nonzero_status_is_not_ok():
    """★ **负例（官方必然失败那条）**：`status=1`（invalid input）⇒ ★ **不许算 ok** ✓
    ★ 官方依据：`Sections` 里的对象**已在选择集里**时，status **必然 = 1** ✓"""
    out = MP.section_properties(_Model(ext=_Ext(_vals(status=1.0, area=None))))
    assert out["ok"] is False and out["status_text"] == "invalid input"


def test_drawing_is_refused_before_touching_com():
    """★★ **负例**：★ 工程图（`GetType()=3`）⇒ ★ **必须 `ok=False` 且不抛** ✓
    ★（★ 与 `mass_property_object` 吃过的那个亏同判据 —— ★ 先判类型）✓"""
    out = MP.section_properties(_Model(doc_type=3, ext=_Ext(_vals())))
    assert out["ok"] is False and out["error"], out
    assert "工程图" in out["error"] or "Drawing" in out["error"]


def test_missing_entry_yields_ok_false_with_a_reason():
    """★ **负例**：★ 假 `Extension` **没有**该成员 ⇒ ★ `ok=False` + 有原因的 `error` ✓"""
    out = MP.section_properties(_Model(ext=_Ext(None)))
    assert out["ok"] is False and out["error"], out
