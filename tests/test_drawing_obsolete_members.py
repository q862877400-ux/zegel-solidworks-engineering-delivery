"""★ 测工程图模块里**不再先调废弃成员**（★ `JUDGE-C_D_E` 🔴 #8 · DW2-2 / DW2-7 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\ISFSymbol\` ·
#         `C:\swapi\types\IDisplayDimension\` · `C:\swapi\types\IAnnotation\`）
# 文件:   `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#8**（★ `C-dw-2 DW2-2 / DW2-7`）逐字：
#   · ★ **DW2-7**：「★ 读表面粗糙度符号**先调**官方标 **Obsolete** 的 `GetSymbolType`」· 判定「**不成立**」✓
#     ★★ 官方逐字：★ `ISFSymbol/GetSymbolType.md` ⇒「**Obsolete. Superseded by
#       `ISFSymbol::GetSymbol`**」· ★ 而后继 `GetSymbol.md` 的 Returns 是
#       「Type of symbol as defined in **`swSFSymType_e`**」⇒ **同一语义** ✓
#   · ★★ **DW2-2**：「★ 尺寸文字格式的**兜底**读法用了官方标 Obsolete 的成员」· 判定「不成立」✓
#     ★★ 而这里**顺序是对的**（★ 先现行、★ 废弃只当兜底）⇒ **处置 = 标注而非删** ✓
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
SRC = REPO / "subskills" / "solidworks-engineering-drawing" / "scripts" / "drawing_workflow.py"


def _code_only() -> str:
    """★★ 剥注释与 docstring（★ 事实 513 · 本会话第 11 次 —— 修正说明里逐字引了旧代码）。"""
    text = SRC.read_text(encoding="utf-8", errors="replace")
    try:
        toks = [t for t in tokenize.generate_tokens(io.StringIO(text).readline)
                if t.type != tokenize.COMMENT]
        s = tokenize.untokenize(toks)
    except Exception:                                                     # noqa: BLE001
        s = text
    try:
        tree = ast.parse(s)
        for n in ast.walk(tree):
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                b = getattr(n, "body", None) or []
                if b and isinstance(b[0], ast.Expr) and isinstance(
                        getattr(b[0], "value", None), ast.Constant) and isinstance(
                        b[0].value.value, str):
                    b[0].value.value = ""
        s = ast.unparse(tree)
    except Exception:                                                     # noqa: BLE001
        pass
    return s


def test_official_pages_confirm_the_obsolete_marks() -> None:
    """★★★ **前提断言**：★ 官方两页**确实**标了废弃（★ 判据的锚点）✓"""
    f1 = Path(r"C:\swapi\types\ISFSymbol\GetSymbolType.md")
    f2 = Path(r"C:\swapi\types\ISFSymbol\GetSymbol.md")
    f3 = Path(r"C:\swapi\types\IDisplayDimension\GetTextFormat.md")
    if not (f1.is_file() and f2.is_file() and f3.is_file()):
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    assert "Obsolete" in f1.read_text(encoding="utf-8", errors="replace")
    assert "Obsolete" not in f2.read_text(encoding="utf-8", errors="replace"), (
        "★ `GetSymbol` 也被标废弃了 ⇒ 判据要重看")
    assert "Obsolete" in f3.read_text(encoding="utf-8", errors="replace")


def test_get_symboltype_is_gone_from_code() -> None:
    """★★★ 核心断言（★ DW2-7）：★ **代码里**不许再调 `"GetSymbolType"`（★ 它是废弃成员）✓"""
    code = _code_only()
    assert "GetSymbolType" not in code, (
        "★ 还在调废弃的 `GetSymbolType` ⇒ 现行入口是 `GetSymbol`")
    assert '"GetSymbol"' in code or "'GetSymbol'" in code, "★ 连现行入口也没了"


def test_text_format_fallback_is_annotated() -> None:
    """★★★ 核心断言（★ DW2-2）：★ 那处**兜底**必须**标注**它走的是废弃成员 ✓

    ★★ 判据：★ `format_source` **不是**裸的 `"IDisplayDimension.GetTextFormat()"` ——
      ★ 而要**带上「官方标 Obsolete」的字样** ✓
    """
    src = SRC.read_text(encoding="utf-8", errors="replace")
    assert 'format_source = "IDisplayDimension.GetTextFormat()"' not in src, (
        "★ 那处兜底还是裸的名字 ⇒ 后人看不出它是废弃入口")
    assert "官方标 Obsolete" in src, "★ 没标注"


def test_negative_case_current_entry_still_first() -> None:
    """★★ **负例 · 顺序**：★ **现行入口必须仍然在前** —— ★ 不许把废弃的提到前面 ✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    i_cur = src.find('_safe_member(annotation, "GetTextFormat", 0)')
    i_old = src.find('_safe_member(display_dimension, "GetTextFormat")')
    assert i_cur != -1 and i_old != -1, "★ 两处读法之一丢了"
    assert i_cur < i_old, "★ 废弃那条跑到现行前面了 ⇒ 顺序反了"
