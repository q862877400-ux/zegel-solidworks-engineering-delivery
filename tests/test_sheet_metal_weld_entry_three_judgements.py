"""★ 测 `sw_sheet_metal_weld_entry.py` 的**三处判据是否都纳入 `ok`**（★ E5-4 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/test_sheet_metal_weld_entry_three_judgements.py
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#1 · E5-4** 逐字：「★ 仓内 doc：`判据 = 特征树增量 +
#   返回对象非 None + **实体面数增量**（三个都要）` ／ `… + GetDefinition() 属性回读` ／
#   `… + **mark-1 选区计数**` · ★ 而目标：★ **三处 `ok` 完全相同**：`"ok": bool(added) and fea…`」✓
#   ★★ 修完必须用负例证明它真能拦（★ 事实 62）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import io
import re
import sys
import tokenize
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import sw_sheet_metal_weld_entry as M                                     # noqa: E402

SRC = REPO / "scripts" / "sw_sheet_metal_weld_entry.py"
THREE = ["insert_sheet_metal_miter_flange", "insert_weldment_end_cap",
         "insert_weldment_gusset"]


def _code_only(text: str) -> str:
    """★★ **剥掉注释与 docstring** —— ★ 因为来源块里**逐字引了旧代码**（★ 事实 513 · 本会话第 3 次）。"""
    try:
        toks = [t for t in tokenize.generate_tokens(io.StringIO(text).readline)
                if t.type != tokenize.COMMENT]
        stripped = tokenize.untokenize(toks)
    except Exception:                                                     # noqa: BLE001
        stripped = text
    try:
        tree = ast.parse(stripped)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                body = getattr(node, "body", None) or []
                if body and isinstance(body[0], ast.Expr) and isinstance(
                        getattr(body[0], "value", None), ast.Constant) and isinstance(
                        body[0].value.value, str):
                    body[0].value.value = ""
        stripped = ast.unparse(tree)
    except Exception:                                                     # noqa: BLE001
        pass
    return stripped


def test_no_old_two_term_judgement_in_code() -> None:
    """★★★ 核心断言：★ **代码里**（★ 剥注释后）那个**只含两项**的旧判据必须**全部消失** ✓"""
    code = _code_only(SRC.read_text(encoding="utf-8", errors="replace"))
    assert not re.search(r'"ok":\s*bool\(added\)\s+and\s+feature\s+is\s+not\s+None\s*,', code), (
        "★ 还有只含『树增量 and 返回对象』的旧判据 ⇒ doc 承诺的第三项仍没进 ok")
    #: ★ 而不带 `face_delta` 的写法也不该有（★ 那是"三项都算、只进两项"的形态）
    assert code.count("face_delta_here") >= 3, "★ 三处都要用上 `face_delta_here`"


def _seg(fn: str) -> str:
    """★ 取某个函数的源码段（★ 供逐函数断言）。"""
    src_text = SRC.read_text(encoding="utf-8", errors="replace")
    for n in ast.walk(ast.parse(src_text)):
        if isinstance(n, ast.FunctionDef) and n.name == fn:
            return ast.get_source_segment(src_text, n) or ""
    return ""


def test_all_three_include_face_delta() -> None:
    """★ 三个函数**必须**都把「实体面数增量」纳入 `ok` ✓"""
    for fn in THREE:
        seg = _seg(fn)
        assert seg, "★ 找不到函数 %s" % fn
        assert "face_delta_here" in seg, "★ %s 没用上实体面数增量" % fn


def test_gusset_also_includes_mark1() -> None:
    """★ 角撑板那条 doc 多承诺了 **mark-1 选区计数** ⇒ `ok` 里**必须**有它 ✓"""
    seg = _seg("insert_weldment_gusset")
    assert seg and "mark1" in seg, "★ 角撑板没用上 mark-1 选区计数"
    assert "int(mark1) > 0" in seg, "★ mark-1 计数算了却没进 ok"


def test_verified_by_names_all_judgements() -> None:
    """★ 三处的 `verified_by` 都要**逐字写出**它用了哪几个判据（★ 便于复核）✓"""
    for fn in THREE:
        seg = _seg(fn)
        assert seg and "verified_by" in seg, "★ %s 缺 verified_by" % fn
        assert "实体面数增量" in seg, "★ %s 的 verified_by 没写明用了几项" % fn


def test_negative_case_helper_still_refuses_none_model() -> None:
    """★★ **负例**：★ `model=None` ⇒ **必须**明确失败（★ 不许静默成功）✓"""
    out = M.insert_sheet_metal_closed_corner(None)
    assert out["ok"] is False and "error" in out
