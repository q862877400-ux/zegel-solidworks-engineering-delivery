"""★ 测 `sketch_spline` 的 doc **不许假引用官方 Remarks**（★ `JUDGE-C_D_E` 🔴 #5 · E-6 #1 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\ISketchManager\`）
# 文件:   `mcp-server/tool_specs_batch76.py`（`solidworks_sketch_spline` 的 doc）
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#5**（★ `E-6 #1`）逐字：「★ 把 `CreateLine2` 的前置
#   （「无活动草图就不建、回 NULL」）**搬到 `CreateSpline2` 上**并冠以「官方 Remarks」——
#   ★ 官方逐字写的是**反面**（没有草图会**新建**）」✓
#   ★★ **官方两页逐字（★ 我读了两个 md 比对）**：
#     · `ISketchManager/CreateSpline2.md` ⇒「If a sketch is not active, then **a new sketch is
#       created**.」✓
#     · `ISketchManager/CreateLine.md` ⇒「If a sketch is not active, then the line is
#       **not created and NULL is returned**.」✓
#     · ★ 而 `CreateLine2.md` **不存在**（★ 只有 `CreateLine`）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import io
import sys
import tokenize
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SPEC = REPO / "mcp-server" / "tool_specs_batch76.py"
OFF = Path(r"C:\swapi\types\ISketchManager")


def _doc_strings_only(path: Path) -> str:
    """★★ 只留**字符串字面量**（★ 那才是 doc 正文）—— ★ 注释本来就不在 AST 里 ✓

    ★★★ **为什么必须这样**：★ 本条的修正说明里**逐字引了旧句**
      （★ 事实 513 的形态）⇒ ★★ 若直接对**文件全文**做 `in` 判「旧句还在不在」，
      会**假阳性**（★ 我这次就踩了一次）✓
    ★ 而 `ast` 的 `Constant` 只覆盖**字符串字面量** ⇒ ★ **注释天然不在里面** ✓
    """
    src = path.read_text(encoding="utf-8", errors="replace")
    out = []
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
    return "\n".join(out)


def test_official_two_pages_are_opposite() -> None:
    """★★★ **前提断言**：★ 官方两页**确实**相反（★ 判据的锚点）✓"""
    f1 = OFF / "CreateSpline2.md"
    f2 = OFF / "CreateLine.md"
    if not (f1.is_file() and f2.is_file()):
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t1 = f1.read_text(encoding="utf-8", errors="replace")
    t2 = f2.read_text(encoding="utf-8", errors="replace")
    assert "a new sketch is created" in t1, "★ `CreateSpline2` 的官方口径变了"
    assert "not created and NULL is returned" in t2, "★ `CreateLine` 的官方口径变了"
    assert not (OFF / "CreateLine2.md").is_file(), "★ `CreateLine2` 竟然存在了 ⇒ 判据要重看"


def test_spline_doc_does_not_claim_the_line_precondition() -> None:
    """★★★ 核心断言：★ 旧句**要么不在**、★ **要么与「假引用」标注**同框**（★ 两者必居其一）✓

    ★★★★ **为什么不是"旧句必须消失"** —— ★ 本仓库的纪律是
      **「自我否定必须补正而不是删除」**：★ 旧句是历史证据。
      ⇒ ★★ 所以判据是**二选一**：
        · ★ **旧句不在** ⇒ 那也行（★ 干净）；
        · ★★ **旧句在** ⇒ ★ **必须同时写明它是「假引用」**（★ 否则后人会照它排查）✓
    ★ 而「同框」的粒度取**同一批 doc 字符串**（★ 那是文件的 doc 正文）✓
    """
    docs = _doc_strings_only(SPEC)
    if "必须先有活动草图" in docs:
        assert "假引用" in docs, (
            "★ doc 里有那句「必须先有活动草图」、★ 却**没标注它是假引用** ⇒ 后人会照它排查")
        assert "CreateLine" in docs, "★ 没点明那句的真出处"


def test_spline_doc_quotes_the_real_remarks() -> None:
    """★★★ 核心断言：★ 必须引**真**的官方 Remarks（★ 「a new sketch is created」）✓"""
    docs = _doc_strings_only(SPEC)
    assert "a new sketch is created" in docs, "★ 没引官方原话"
    assert "假引用" in docs, "★ 没写明那处是假引用（★ 后人会再犯）"


def test_negative_case_marks_where_the_wrong_sentence_came_from() -> None:
    """★★ **负例**：★ 更正里**必须点明那句的真出处**（★ `CreateLine`）——
    ★ 否则后人只知道「错了」、★ 不知道**错在哪** ✓
    """
    docs = _doc_strings_only(SPEC)
    assert "CreateLine" in docs, "★ 没点明那句真出处是 `CreateLine`"
