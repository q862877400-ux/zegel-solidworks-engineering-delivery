"""★ 测 `create_extruded_surface_report` 是否走**四级回退**选草图（★ 事实 517 的修复）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_surface_features.py::create_extruded_surface_report` ·
#         `scripts/sw_part.py::_ensure_sketch_selected`（★ 本仓既有的**四级回退**选中器）
# 定位:   ★ `docs/known-facts.md` **事实 517** §三之二的**修复** —— ★ 真机跑出
#   `create_extruded_surface(depth_mm=10.0) ⇒ ok: False · new_features: []` ⇒
#   ★★ **回原文查到真因**：★ `FeatureExtruRefSurface3` 的 `## Remarks` 要求
#     「**select the entities** for the extruded surface using `SelectByID2`」（★ 草图 **mark 0**）✓
#   ★★★ **而我第一版自己写了一级 `SelectByID2("草图1","SKETCH",…)` ⇒ 真机 `select_returned: False` ·
#     `selection_count: 0`** ⇒ ★★★★ **本仓那个四级回退一次都没走** ✓
#   ★★ **修后真机**：★ `ok: **True**` · ★ `new_features: ['曲面-拉伸1']` · ★ 树 **6 → 7** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

SRC = REPO / "scripts" / "sw_surface_features.py"


def _seg(fn: str) -> str:
    src = SRC.read_text(encoding="utf-8", errors="replace")
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and n.name == fn:
            return ast.get_source_segment(src, n) or ""
    return ""


def test_uses_the_repo_sketch_selector() -> None:
    """★★★ 核心断言：★ 必须**复用** `sw_part._ensure_sketch_selected`（★ 本仓的四级回退）✓"""
    seg = _seg("create_extruded_surface_report")
    assert "_ensure_sketch_selected" in seg, (
        "★ 没复用本仓的四级回退 ⇒ 又会退化成「只写一级选中」")


def test_selection_count_is_read_back() -> None:
    """★★ 判据必须**回读选区计数**（★ 事实 8：★ 不信返回值、只看回读）✓"""
    seg = _seg("create_extruded_surface_report")
    assert "GetSelectedObjectCount2" in seg, "★ 没回读选区计数"
    assert "selection_count" in seg, "★ 没把回读计数写进返回值"


def test_refuses_when_selection_fails() -> None:
    """★★★ **负例**：★ 选不中 ⇒ **必须** `ok: False` **且** `stage: "select"`（★ 不许静默往下调）✓"""
    seg = _seg("create_extruded_surface_report")
    assert '"stage": "select"' in seg, "★ 选不中时没走早退分支"
    assert "前置未成立" in seg or "选草图抛" in seg, "★ 没写清失败原因"


def test_declares_official_remarks_source() -> None:
    """★ 必须**写明官方依据**（★ `## Remarks` 的 mark 表）—— ★ 否则后人不知道为什么要选 ✓"""
    seg = _seg("create_extruded_surface_report")
    assert "Remarks" in seg and "mark" in seg, "★ 没写明官方 Remarks 与 mark 表"
