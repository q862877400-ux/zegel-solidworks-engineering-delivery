"""★ 测 `AdvancedGraphics` 的记档：★ 引官方「**Not superseded**」、★ 且**不假装换过**（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `scripts/sw_render_material.py::apply_visual_properties`（★ 生产）
# 定位:   ★ 阶段 2 · T1 的**最后一条** ✓
#   ★★ **官方逐字**（★ `IMaterialVisualPropertiesData/AdvancedGraphics.md`）：
#     ★ 「**Obsolete. Not superseded.**」✓
#     ★ 签名 ⇒ `System.bool AdvancedGraphics {get; set;}` ⇒ ★ **属性** ✓
#     ★★ `## Returns` 逐字 ⇒ 「True if the part is displayed with **shaded textures**」✓
#     ★★★ `## See Also` 点名了 `IMaterialVisualPropertiesData::RealView Property` ✓
#   ★★★ **∴ 处置 = 记档保留**（★ 官方说"没有替代" ⇒ **没有新的一代可换**）✓
#   ★★★★ **可复用判据**：★★★ **「Not superseded」与「查不到后继」不一样** ——
#     ★ 前者是**官方明确说"没有替代"**（★ **终点**）、
#     ★★ 后者只是**我这次没找到**（★ 要按铁律 5 说清**哪个源**查不到）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_render_material.py"
OFF = Path(r"C:\swapi\types\IMaterialVisualPropertiesData\AdvancedGraphics.md")


def test_official_says_not_superseded() -> None:
    """★★★ **前提断言**：★ 官方**确实**写「Obsolete. Not superseded.」（★ 判据的锚点）✓"""
    if not OFF.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t = OFF.read_text(encoding="utf-8", errors="replace")
    assert "Obsolete" in t, "★ 不再废弃了"
    assert "Not superseded" in t, "★ 「Not superseded」那句变了 ⇒ 判据要重看"
    assert "shaded textures" in t, "★ Returns 的语义变了"


def test_code_still_uses_it_because_there_is_no_successor() -> None:
    """★★★ 核心断言：★ 既然官方说无后继，★ 代码**仍用它**（★ 而**不许**假装换过）✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    assert "advanced_graphics" in src, "★ 参数没了"
    #: ★ 剥注释与 docstring 后：★ 属性**赋值**应还在（★ 那是"仍用它"的判据）
    toks = src
    tree = ast.parse(toks)
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            b = getattr(n, "body", None) or []
            if b and isinstance(b[0], ast.Expr) and isinstance(
                    getattr(b[0].value, "value", None), ast.Constant) and isinstance(
                    b[0].value.value, str):
                b[0] = ast.Pass()
    code = ast.unparse(tree)
    assert "AdvancedGraphics" in code, "★ `AdvancedGraphics` 的赋值不见了 ⇒ 是不是假装换了？"
    #: ★★★ **判据要精确**（★ 事实 51：★ 范围/对象要贴合）——
    #:   ★ `RealView` **本来就在**这个接口上（★ 它是**另一个属性**、★ `See Also` 里也点了）⇒
    #:   ★★ **"代码里有 `RealView`"本身不是问题** ⇒
    #:   ★★★ **要判的是「那个参数被**映射到** `RealView`」**（★ 即把无后继的当成有后继）✓
    assert "advanced_graphics" in code, "★ 参数名不见了"
    for m in re.finditer(r"RealView[^\n]{0,80}", code):
        assert "advanced_graphics" not in m.group(0), (
            "★ 把 `advanced_graphics` 映射到 `RealView` 了 ⇒ **官方没说**它是后继")


def test_negative_case_reason_quotes_the_official_wording() -> None:
    """★★★ **负例 · 依据要逐字**：★ 记档里必须有官方那句 `Not superseded` ✓"""
    t = SRC.read_text(encoding="utf-8", errors="replace")
    assert "Not superseded" in t, "★ 没有引官方那句"
    assert "记档保留" in t, "★ 没写「记档保留」"


def test_negative_case_distinguishes_the_two_kinds_of_no_successor() -> None:
    """★★★★ **负例 · 两种"没后继"要分开**：★ 记档必须写清这条判据 ✓

    ★★ **为什么**：★ 本会话里出现过**两种**"没有后继" ——
      ★ **官方明说**没有替代（★ **本条**）· ★★ **我这次没查到**（★ **事实 518** 那一族）⇒
      ★★★ **混起来会让后人以为"官方什么都说了"** ✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    assert "查不到后继" in t, "★ 没写明「两者不一样」的那一半"
    assert "事实 518" in t, "★ 没指向事实 518（★ 那是对照的那一族）"
