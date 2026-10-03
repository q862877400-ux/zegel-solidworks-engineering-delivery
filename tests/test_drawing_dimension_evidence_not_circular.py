"""★ 测 `drawing_dimension_insertion` 的 evidence **不许只挂一个"循环自证"**（★ `JUDGE-A_B` 🔴 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `capabilities.yaml`（`drawing_dimension_insertion.evidence`）·
#         `tests/test_cad_reliability.py`（★ 那个"循环自证"文件）
# 定位:   ★ `JUDGE-A_B.md` 的 🔴 **A-drawing 一** 逐字：「★ `drawing_dimension_insertion` 的
#   evidence 唯一相关行是 `assert index[...]["level"] == "verified"` —— ★ **循环自证**，
#   ★ 测试文件**自己写「未在本机实测」**」✓
#   ★★ **实测复核**：★ `tests/test_cad_reliability.py` 逐字 L8「⚠ **未在本机实测 SolidWorks**」·
#     L53 `assert index["drawing_dimension_insertion"]["level"] == "verified"` ✓
#   ★★★ **本条的判据（★ 与 A4 同源）**：★★★ **一条 evidence 若只是"断言自己的 level"，
#     那不是运行证据** —— ★ 因为**它假定自己是对的** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _ev() -> list[str]:
    d = json.loads((REPO / "capabilities.yaml").read_text(encoding="utf-8"))
    c = [x for x in d["capabilities"] if x.get("id") == "drawing_dimension_insertion"][0]
    return [str(x) for x in (c.get("evidence") or [])]


def test_the_circular_file_really_says_untested() -> None:
    """★★★ **前提断言**：★ 那个测试文件**确实**自陈「未在本机实测」（★ 判据的锚点）✓"""
    p = REPO / "tests" / "test_cad_reliability.py"
    assert p.is_file(), "★ 那个测试文件不在"
    t = p.read_text(encoding="utf-8", errors="replace")
    assert "未在本机实测" in t, "★ 它不再自陈「未实测」了 ⇒ 判据要重看"


def test_evidence_marks_the_circular_one_as_not_runtime() -> None:
    """★★★ 核心断言：★ 必须**显式标注**那条不是运行证据 ✓"""
    blob = " ".join(_ev())
    assert "不是运行证据" in blob, "★ 没标注那条是「循环自证」"
    assert "循环自证" in blob, "★ 没写明它是循环自证"


def test_negative_case_does_not_say_already_run() -> None:
    """★★★ **负例 · 用词**：★ 既然没跑过，★ **不许**留下「已跑过」那种措辞（★ 除非在否定句里）✓"""
    blob = " ".join(_ev())
    if "已跑过" in blob:
        assert "不许" in blob or "不是" in blob, (
            "★ 有「已跑过」字样、★ 却没在否定它 ⇒ 会被读成「跑过了」")


def test_negative_case_names_what_is_missing() -> None:
    """★★ **负例 · 待补**：★ 必须写明**缺什么**（★ 否则后人不知道该怎么补）✓"""
    blob = " ".join(_ev())
    assert "真机" in blob, "★ 没写明要补真机证据"
    assert "A4" in blob, "★ 没指向验收标准 A4（★ verified 要有自己的运行证据）"
