"""★ 测 `sw_curve_and_split.py` 的判据（★ E5-6 + 顺带发现的两处**跨种类 `or`**）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/test_curve_and_split_judgement.py
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#1 · E5-6** 逐字：「★ 仓内 doc：`★ 判据 = Point/End 的
#   返回值 **且** 特征树增量。` ★ 而目标：`point_rets.append(bool(get_com_member(model,
#   "InsertCurveFilePoint", …)))` ／ `return {"ok": end_ret and bool(added), …}`」· 判定「**确认**」✓
#   ★★ 而本轮扫描**顺带发现**：同文件两处 `"ok": bool(added) **or** (face_delta or 0) > 0`
#     ⇒ ★★★ **跨种类用 `or`**（★ 与 E5-3 / E5-4 同一个错）✓
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

import sw_curve_and_split as C                                            # noqa: E402

SRC = REPO / "scripts" / "sw_curve_and_split.py"


def _code_only(text: str) -> str:
    """★★ 剥注释与 docstring（★ 事实 513 · 本会话第 4 次 —— 来源块里逐字引了旧代码）。"""
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


def test_no_cross_kind_or_in_code() -> None:
    """★★★ 核心断言：★ **代码里**不许有「树增量 **or** 面数增量」这种**跨种类 `or`** ✓"""
    code = _code_only(SRC.read_text(encoding="utf-8", errors="replace"))
    assert "or (face_delta" not in code, (
        "★ 跨种类用了 `or` ⇒ 把「缺一不可」写成了「有一个就行」（★ E5-3/E5-4 同一个错）")


def test_curve_uses_all_point_returns() -> None:
    """★ `insert_curve_through_points` **必须**把每个 `InsertCurveFilePoint` 的返回值都用上 ✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    seg = None
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and n.name == "insert_curve_through_points":
            seg = ast.get_source_segment(src, n)
            break
    assert seg, "★ 找不到 insert_curve_through_points"
    assert "all_points_ok" in seg, "★ `point_rets` 算了却没进 ok（doc 承诺的 `Point` 返回值）"
    assert re.search(r'"ok":\s*bool\(all_points_ok', seg), (
        "★ `ok` 那一行没用上 `all_points_ok`")


def test_mate_reference_uses_and() -> None:
    """★ `insert_mate_reference` 的判据是「回对象非 None **+** 树增量」= **跨种类 ⇒ `and`** ✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    seg = None
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and n.name == "insert_mate_reference":
            seg = ast.get_source_segment(src, n)
            break
    assert seg and "feat is not None and bool(added)" in seg, (
        "★ insert_mate_reference 的判据不是『对象 and 树增量』⇒ 与文件头 L57 的承诺不符")


def test_ok_note_explains_void_entries() -> None:
    """★ 两条 `split_line_*` 回 `void` ⇒ **必须**在返回值里说明"为什么只剩一个判据" ✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    assert src.count("ok_note") >= 2, "★ 两条 void 入口缺 `ok_note` ⇒ 后人看不出判据为什么只剩一个"


def test_negative_case_refuses_none_model() -> None:
    """★★ **负例**：★ `model=None` ⇒ **必须**明确失败 ✓"""
    cases = [
        ("insert_split_line_project", None),
        ("insert_split_line_silhouette", None),
        ("insert_curve_through_points", [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]),
    ]
    for fn, arg in cases:
        f = getattr(C, fn, None)
        assert f is not None, "★ 找不到 %s" % fn
        out = f(None, arg) if arg is not None else f(None)
        assert out["ok"] is False and "error" in out, "★ %s 对 None 没明确失败" % fn
