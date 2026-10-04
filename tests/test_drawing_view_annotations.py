"""★ 测「工程图读侧第一批」+ 那两条边界（★ 含负例 · 轮 136）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `IView\GetAnnotations.md` / `GetAnnotationCount.md` / `GetArcCount.md` /
#         `GetDisplayDimensions.md` + 官方示例 `Get_Names_of_Annotations_Example_VB.md` +
#         真机证据 `output/drawing-annotations-capability-recheck.json`
# 文件:   tests/test_drawing_view_annotations.py（★ 新）
# 定位:   ★★★★★★★ 2026-10-04（轮 136）**工程图读侧第一批真机验证通过**：
#     ★ 建视图 → 写注释 → 读回 ⇒ ★★ **`view_count = 1`** ·
#       `{name: 工程图视图1, type: 7, annotation_count_by_api: **1**,
#         annotations: [**细节项目254**], annotation_len: **1**, arc_count: 0}` ✓
#     ★★★ **两条独立读数一致**（`1` 与 `1`）⇒ `mismatches = 0` ⇒ **判据成立** ✓
#   ★★★★ **两条边界（★ 都实测过、★ 必须写清）**：
#     ★ **① 零件必须先存盘** —— 不存盘则 `GetPathName()` 是空串 ⇒ 视图插不上 ⇒
#       `view_count = 0`（★ **那是应然的、★ 不是读侧坏了**）✓
#     ★★ **② 本机 `create_three_standard_views` 是 blocked**
#       （★ 逐字：本机实测为 blocked：`CreateFirstAngleViews2` 不可用）⇒
#       ★ **⇒ 要插视图走 `create_projected_view`** ✓
#   ★★★★★ **官方例子的调用序**（★ 签名给不了）：★ `GetFirstView` ⇒ ★ **第一个是图纸本身（sheet）** ⇒
#     `GetNextView` ⇒ **`GetAnnotations`** ⇒ `For Each` ⇒ `GetName` ✓
#   ★★★★★★ **⚠ 写本文件时我踩了一个坑（★ 值记）**：★ 我用一个**正则**把中文串里的 ASCII 引号
#     批量换成 `「」` ⇒ ★★ **而它**误伤了 docstring 的定界符** ⇒ `SyntaxError` ✗ ⇒
#     ★★★ **⇒ 处置：★ 重写文件**（★ **别用正则去改引号** —— ★ 它分不清「定界符」与「内容」）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
sys.path.insert(0, str(TESTS))
from _funcbody import func_source  # noqa: E402

SRC = REPO / "scripts" / "sw_drawing_query.py"
OUT = REPO / "output" / "drawing-annotations-capability-recheck.json"
PROBE = REPO / "tools" / "probe_drawing_annotations_recheck.py"


def test_the_real_readings_are_recorded() -> None:
    """★★★ 核心断言：★ 真机那几个读数在能力里（★ 那是「怎么知道的」）✓"""
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"),
                       "view_annotations_report")
    assert "工程图视图1" in body, "★ 真机那个视图名没记下"
    assert "细节项目254" in body, "★ 那条注释名没记下"
    assert "mismatches = 0" in body or "两条独立读数一致" in body, "★ 判据那句没记下"


def test_the_two_independent_readings_are_both_read() -> None:
    """★★★★ 核心断言：★ 代码里**两个独立读数都读了**（★ count 与数组长度）✓

    ★★ **为什么**：★ 官方 `GetAnnotationCount` 的 `## Remarks` 逐字说它
      「determine the size of the array for that method」⇒ ★★★ **⇒ 两个数**应当一致** ⇒
      ★ **不一致就说明有东西没读到** ⇒ **⇒ 那是一对判据、★ 不能只读一个** ✓
    """
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"),
                       "view_annotations_report")
    assert "GetAnnotationCount" in body, "★ 没读 `GetAnnotationCount`"
    assert "GetAnnotations" in body, "★ 没读 `GetAnnotations`"
    assert "annotation_count_by_api" in body and "annotation_len" in body, (
        "★ 两个读数要分别记名 ⇒ 才能对账")


def test_the_sheet_pseudo_view_is_skipped() -> None:
    """★★★★ 核心断言：★ **跳过「图纸本身」**（★ 官方例子逐字说了这件事）✓

    ★★ **为什么**：★ 官方例子注释逐字 `' First drawing view is the sheet` ⇒
      ★★★ **⇒ 不跳就会列出一个假视图**（★ 而本模块 `list_views` 早就这么做了）✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    body = func_source(t, "view_annotations_report")
    assert "SHEET_PSEUDO_VIEW_TYPE" in body, "★ 没跳过「图纸本身」"
    assert "First drawing view is the sheet" in t, "★ 官方那句依据没留下"


def test_the_obsolete_member_is_not_read() -> None:
    """★★★★ 核心断言：★ **废弃成员不读**（★ `GetLineCount` 官方标 `Obsolete`）✓

    ★★ **为什么**：★ 本会话做过 6 次同型的读侧 ⇒ ★ **每次都逐条查官方页的废弃位** ⇒
      ★★★ **⇒ `GetLineCount()` 的那一页有 `Obsolete`** ⇒ **不读** ✓

    ★★★★★★ **⚠ 而这条判据我**改了三版才对****（★ 值记 —— ★ 三版都是**同一个病**）：
      ★ **第 1 版**：★ 用「剥掉 `#` 开头的行」当"代码" ⇒ ★★ **docstring 的行不以 `#` 开头** ⇒
        docstring 里那句「不读 `GetLineCount`」被当成**代码命中** ⇒ **假阳性** ✗
      ★★ **第 2 版**：★ 改用 `ast` 按 `end_lineno` 剪掉 docstring ⇒ ★★ **又红** ——
        ★ **真因**：★ **`GetLineCount` 出现在**返回值**里**
        （★ `"★_不读": ["GetLineCount（★ 官方标 Obsolete）"]`）⇒ **那是**记录"为什么不读"**** ✗
      ★★★ **第 3 版（正确）**：★ 查**调用形态** —— ★ 即
        `get_com_member(…, "GetLineCount")` 这种**当成员名用**的形态** ⇒
        ★ **★ 而"记录它不读"是**合法**的、★ 不该被判成违规** ✓
      ★★★★ **⇒ 按**事实 53**：★ 同一处判据改到第 3 版就该**换判据**、★ 不是继续调** ✓
      ★★★★★ **可复用判据**：★★★ **「有没有用它」要查**调用形态**、
        ★ 不要查名字出现** —— ★ **而这条本会话**早就有过**（★ 我却还是先踩了名子匹配）✓
        ★★ 同族：★ **"剥注释"式的判据**默认会**漏掉 docstring**（★ 本仓 `_codescan.code_only`
          就是为此而写）✓
    """
    import re as _re
    src = SRC.read_text(encoding="utf-8", errors="replace")
    #: ★★★ **按调用形态判**：★ 有没有把 `GetLineCount` 当**成员名**用 ✓
    calls = _re.findall(r'get_com_member\([^)]*"GetLineCount"', src)
    assert not calls, "★ 代码里按调用形态读了 `GetLineCount`（★ 官方标废弃）：%r" % calls
    #: ★★ 而 docstring 里**要**有它（★ 那是"为什么不读"的记录）✓
    assert "GetLineCount" in src, "★ 但要把「为什么不读它」记下来"


def test_the_two_boundaries_are_recorded_and_evidenced() -> None:
    """★★★★ 核心断言：★ 两条边界都写进能力 + ★ 证据里**两条路都试过** ✓"""
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"),
                       "view_annotations_report")
    assert "存盘" in body and "GetPathName" in body, "★ 「零件要先存盘」那条没记"
    assert "Create1stAngleViews2" in body or "blocked" in body, (
        "★ 「本机三视图 blocked」那条没记")
    t = PROBE.read_text(encoding="utf-8", errors="replace")
    assert "create_projected_view" in t and "create_three_standard_views" in t, (
        "★ 探针只试了一条路 ⇒ blocked 那件事就没有证据")
    #: ★★★ 2026-10-04（接手轮）**给真机产物加一道可解释的闸** —— ★ 处置**事实 57 的同族**：
    #:   `output/` 在 `.gitignore:120` 里 ⇒ ★ **那份证据是"本机产物"、不是入库件** ⇒
    #:   ★★ **干净检出上它必然不在** ⇒ 原来的 `json.loads(OUT.read_text(...))` 会抛
    #:   `FileNotFoundError`（★ 而后人只会看到一条红，看不出"这是环境依赖"）。
    #:   ⇒ ★ 判据：**前置（那份证据在不在）**与**结论（两条路都进了证据）**分开 ——
    #:     ★ 不在 ⇒ `skip` 并**写明缺的是哪一份、由哪个探针产**（★ 契约违约**可见**）。
    if not OUT.is_file():
        import pytest

        pytest.skip("★ 前置未成立：本机产物 `output/%s` 不在（`.gitignore:120` 排除 `output/`）"
                    "⇒ 重跑 `python tools/sw_guard.py --timeout 900 -- python %s` 再验"
                    % (OUT.name, PROBE.name))
    d = json.loads(OUT.read_text(encoding="utf-8"))
    step = next((s for s in d["steps"] if s["name"] == "insert_views"), None)
    assert step and "projected" in step and "three_std" in step, "★ 两条路的返回没进证据"
