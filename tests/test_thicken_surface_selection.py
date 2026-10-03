"""★ 测 `thicken_surface_report` 是否按官方 Remarks 做了 `mark 1` 选曲面（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_surface_features.py::thicken_surface_report` ·
#         `scripts/sw_surface_features.py::_select_all_surface_faces`（★ 本仓既有）
# 定位:   ★ 官方 `IFeatureManager.FeatureBossThicken` 的 `## Remarks` 逐字：
#   > ★ 「This method generates a boss feature by thickening a **selected reference surface**.
#   >   ★★ **The surface must be selected with a mark of 1.**」✓
#   ★★ 而该函数旧 docstring 写的前置是「★ **文件里要有曲面体**（★ 而 `use_auto_select=True`
#     时官方会"自动选所有体"）」⇒ ★★★ **那是把「体在不在」当成了「选没选中」** ✓
#   ★★★ **本轮真机**：★ 补上 `mark 1` 后 **选中数 = 4**、★ 而 `FeatureBossThicken`
#     **仍回 `None`** ⇒ ★★★★ **那是一条更强的否定结果：★ 把「前置没做」排除了** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────

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


def test_thicken_selects_with_mark_1() -> None:
    """★★★ 核心断言：★ 必须按官方 Remarks **用 `mark=1` 选中曲面** ✓"""
    seg = _seg("thicken_surface_report")
    assert "_select_all_surface_faces(model, mark=1)" in seg, (
        "★ 没按 `mark 1` 选中曲面 ⇒ 又回到「把『体在不在』当成『选没选中』」")


def test_thicken_refuses_when_selection_empty() -> None:
    """★★★ **负例**：★ 选不中 ⇒ **必须** `ok: False` + `stage: "select"`（★ 不许静默往下调）✓"""
    seg = _seg("thicken_surface_report")
    assert '"stage": "select"' in seg, "★ 选不中时没走早退分支"
    assert "前置未成立" in seg, "★ 没写清失败原因"


def test_thicken_declares_official_remarks() -> None:
    """★ 必须**写明官方 `## Remarks` 原文**（★ 否则后人不知道 `mark 1` 是哪来的）✓"""
    seg = _seg("thicken_surface_report")
    assert "must be selected with a mark of 1" in seg, "★ 没引官方原话"


def test_thicken_ledger_counts_the_new_group() -> None:
    """★★ 总账**必须**记上本轮那一组（★ 而那才是"写明依据"）✓

    ★★ 判据：★ **12 组** · ★ 且表格里**有「按官方 Remarks 做了」那一行** ✓
    """
    seg = _seg("thicken_surface_report")
    assert "共 12 组" in seg, "★ 总账没更新（★ 旧值是 11 组）"
    assert "不是**「前置没做」" in seg or "不是「前置没做」" in seg, (
        "★ 没写明本轮排除的那个可能性（★ 那正是本组实验的价值）")
