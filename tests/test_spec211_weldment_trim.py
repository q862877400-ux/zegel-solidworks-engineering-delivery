"""★ 规格 211 · B3-1「裁剪/延伸焊件」的契约与负例（★ 不连真机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`scripts/sw_weldment.py` 的 `insert_weldment_trim_report`）
# 文件:   tests/test_spec211_weldment_trim.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B3-1**。★ 官方页三样已读
#   （★ `C:\swapi\types\IFeatureManager\InsertWeldmentTrimFeature2.md`）✓
#   ★★ 本条的定性（★ 与"扫描曲面"那条路**同型**，★ 照它走 ✓）：
#     ★ **只到"第一步：查行为"** —— ★ 真机读数：★ **两种数组形参形态都调通**（不抛 ✓），
#     ★★ **而特征树都没变** ✗ ⇒ ★ **因为前置没上**（★ 官方 `## Remarks` 明写 mark 1/2 都要选 ✓）
#     ⇒ ★★ **还不到"试死"** —— ★ 定则：「**读到静默/没建**」≠「**判定试死**」✓
#     ★（★ 那条定则是"扫描曲面"那轮定下的，★ 当时若写成"试死"，★ 后来"建成"的发现就会被挡住 ✓）
# 判据:   ★★ **四条契约**（★ 全部确定性、★ 不猜语义 ✓）：
#     ★ ① `WELDMENT_TRIM_MARKS` 必须与官方 `## Remarks` 的 mark 表**逐字一致**（1 / 2）✓
#     ★ ② **官方 mark 表与选择契约必须写进返回值**（供调用方照做 ✓）
#     ★ ③ **`unit_assumption` 非空** —— ★ 官方 `GapValue` 只写 "Length to trim"、**没给单位** ✓
#     ★ ④ **`side_effects` 非空**（★ 会改/建焊件体、★ 非只读 ✓）
#   ★ 另一条：★ `options_note` 要留住官方那句 **Logical sum**（★ 选项是**按位或**叠的 ✓）
# 官方依据: 见上
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_weldment as W                                        # noqa: E402


def test_weldment_trim_marks_match_official_remarks():
    """★ 官方 `## Remarks` 逐字：1 = Body or bodies to trim · 2 = Trimming boundaries ✓"""
    assert W.WELDMENT_TRIM_MARKS == {"body_to_trim": 1, "trim_boundary": 2}


def test_selection_contract_is_returned():
    r = W.insert_weldment_trim_report(None)
    sc = str(r.get("selection_contract", ""))
    assert "SelectByID2" in sc and "Body" in sc and "boundaries" in sc, sc[:160]
    assert r.get("official_marks") == {"body_to_trim": 1, "trim_boundary": 2}


def test_unit_assumption_is_present_and_nonempty():
    """★ 官方 `GapValue` 只写 Length to trim、**没给单位** ⇒ 必须写明单位假设 ✓"""
    r = W.insert_weldment_trim_report(None)
    ua = str(r.get("unit_assumption", ""))
    assert ua.strip(), "★ 官方未给单位 ⇒ 必须声明（缝合既有约定 unit_assumption）"
    assert "毫米" in ua or "mm" in ua


def test_options_note_keeps_official_logical_sum_wording():
    """★ 官方逐字：`Options` 是 `swWeldmentTrimExtendOptionType_e` 的 **Logical sum** ✓"""
    r = W.insert_weldment_trim_report(None)
    assert "Logical sum" in str(r.get("options_note", ""))


def test_side_effects_declared():
    r = W.insert_weldment_trim_report(None)
    assert r.get("side_effects"), "★ 会改/建焊件体的能力必须声明副作用（★ 不许被当只读）"


def test_none_model_is_refused_without_raising():
    """★ **负例**：`model=None` ⇒ ★ `ok=False` + 有原因（★ 不抛 ✓）"""
    r = W.insert_weldment_trim_report(None)
    assert r["ok"] is False and r["error"]


def test_module_imports_the_new_dependencies():
    """★★ **回归钉**（★ 本批真栽过两次）：★ `mm` 与 `feature_names` 必须**在模块里可用** ✓

    ★ 实录：★ 我第一版块里用了 `mm` 和 `feature_names`，★ 而 `sw_weldment.py` **都没导入** ✗ ⇒
      ★ **运行时 `NameError`** ⇒ ★★ 这个测试**把那个坑钉死** ✓
    """
    assert callable(W.mm), "★ `mm` 必须在（规则 2：换算只在边界做一次）"
    #: ★★ 2026-10-07（B8 收口）：★ **不再断言 `feature_names`** ——
    #:   ★ 因为那会新增一个**独立的 `from .X import` 行**，★ 而
    #:     `scripts/check_relative_imports.py` 的判据是「**前一行为 `try:`**」⇒
    #:     ★★ **每个文件只有第一行合格** ✗ ⇒ 新增独立行会让棘轮计数 +1（35 → 36）✗
    #:   ⇒ ★ 改用**本文件已有**的 `iter_features_recursive`（★ 只缝合不发明 ✓）
    assert callable(W.iter_features_recursive), "★ `iter_features_recursive` 必须在（回读特征树用）"
    assert callable(W.create_empty_dispatch_variant), (
        "★ 空 VARIANT 必须在 —— ★ 实测：两个 object 数组形参**传 None 调不通**、"
        "★ 传 `VARIANT(VT_DISPATCH, None)` ⇒ 调用完成 ✓（事实 12/33）")
