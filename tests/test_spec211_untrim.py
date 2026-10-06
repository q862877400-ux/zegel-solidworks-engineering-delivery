"""★ 规格 211 · B2-1「取消剪裁」的契约与负例（★ 不连真机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`scripts/sw_surface_features.py` 的 `untrim_surface_report`）
# 文件:   tests/test_spec211_untrim.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B2-1**。★ 官方页三样已读
#   （★ `C:\swapi\types\IFeatureManager\InsertUntrimSurface2.md`）✓
#   ★★ **先说边界**：★ **"剪裁曲面"本身仓里已有**（`trim_surface_report` + `cut_surface_report`）⇒
#     ★ **本批补的是"取消剪裁"** ✓；★★ **正例（曲面零件上真的取消）本轮未做** ✗ ——
#     它需要「先建出被剪裁的曲面」那一条链，★ 不在本批范围 ✓
# 判据:   ★★ **三条负例**（★ 都"必然失败"，★ 且都不需要复杂前置 ✓）：
#     ★ ① `face_untrim_type` 越界 ⇒ ★ 不在官方 `swFaceUntrimType_e` ⇒ **必然非法** ✓
#     ★ ② `edge_untrim_type` 越界 ⇒ ★ 同上 ✓
#     ★ ③ ★★★ **真机实证**（★ 证据 `output/spec211-b2-untrim.json`）：★ 在**普通零件**上、
#       ★ **能选到面**、★ 调用**没抛**、★★ **特征树 7→7、新增 `[]`** ✓
#       ⇒ ★ 这是官方那句「**is valid only for surface parts**」的**实证** ✓
#   ★ 另两条契约：
#     ★ ④ **官方两条前置必须写进返回值**（`documented_preconditions`）⇒ ★ 让调用方查得到 ✓
#     ★ ⑤ **`unit_assumption` 必须非空**（★ 官方对 `Distance` **没给单位** ✓，★ 缝合既有约定 ✓）
# 官方依据: 见上
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

import sw_surface_features as SF                               # noqa: E402


class _Model:
    """★ 假件：★ 只够走到"枚举越界"那一判（★ 更后面的路要 COM ⇒ 不在本测试里）✓"""

    def GetType(self):
        return 1


# ── 契约：两个枚举与官方 `sw*UntrimType_e` 一致 ────────────────────────────
def test_untrim_enums_match_official():
    assert SF.UNT_FACE_UNTYPES == {0: "swFaceUntrimTypeAutomatic", 1: "swFaceUntrimTypeManual"}
    assert SF.UNT_EDGE_UNTYPES == {0: "swEdgeUntrimTypeAutomatic", 1: "swEdgeUntrimTypeManual"}


# ── 负例 ① / ②：枚举越界 ⇒ 必然非法 ────────────────────────────────────────
@pytest.mark.parametrize("bad", [2, 9, -1])
def test_face_untrim_type_out_of_range(bad):
    r = SF.untrim_surface_report(_Model(), face_untrim_type=bad)
    assert r["ok"] is False and "swFaceUntrimType_e" in str(r["error"])


@pytest.mark.parametrize("bad", [2, 9, -1])
def test_edge_untrim_type_out_of_range(bad):
    r = SF.untrim_surface_report(_Model(), edge_untrim_type=bad)
    assert r["ok"] is False and "swEdgeUntrimType_e" in str(r["error"])


# ── 契约 ④：官方两条前置必须写进返回值（★ 让调用方查得到）──────────────────
def test_documented_preconditions_are_returned():
    r = SF.untrim_surface_report(_Model(), face_untrim_type=9)
    pre = r.get("documented_preconditions")
    assert isinstance(pre, list) and len(pre) == 2, "★ 官方两条前置都要在"
    txt = " ".join(pre)
    assert "only for surface parts" in txt, "★ 官方逐字要留住"
    assert "preselection" in txt, "★ 官方逐字要留住"


# ── 契约 ⑤：`unit_assumption` 非空（★ 官方对 `Distance` 没给单位）────────────
def test_unit_assumption_is_present_and_nonempty():
    r = SF.untrim_surface_report(_Model())
    assert isinstance(r.get("unit_assumption"), str) and r["unit_assumption"].strip(), (
        "★ 官方 `Distance` 未给单位 ⇒ 必须写明单位假设（缝合既有约定 `unit_assumption`）")
    assert "毫米" in r["unit_assumption"] or "mm" in r["unit_assumption"]


# ── 契约：非只读（★ 会改面体）⇒ 必须显式声明副作用 ─────────────────────────
def test_side_effects_declared():
    r = SF.untrim_surface_report(_Model())
    assert r.get("side_effects"), "★ 会改面体的能力必须声明副作用（★ 不许被当只读）"
