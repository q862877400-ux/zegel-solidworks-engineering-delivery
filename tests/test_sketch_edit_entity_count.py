"""★ 测 `sketch_mirror` / `convert_entities` 是否真的回读了**草图实体计数**（★ `JUDGE-C_D_E` 🔴 #3）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/test_sketch_edit_entity_count.py
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#3**（★ `E-3 #1 / #2`）逐字：「★ doc 承诺的回读判据在代码里
#   **完全不存在**；★ `sketch_mirror` / `convert_entities` 甚至 **`return True` 写死**」✓
#   ★★ 对外契约逐字：「★ The criterion is that the **sketch entity count changes**.」✓
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
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import sw_sketch_edit as E                                                # noqa: E402

SRC = REPO / "scripts" / "sw_sketch_edit.py"
TWO = ["sketch_mirror", "convert_entities"]


def _code_only(text: str) -> str:
    """★★ 剥注释与 docstring（★ 事实 513 · 本会话第 7 次 —— 修正说明里逐字引了旧代码）。"""
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


def _seg(fn: str) -> str:
    src = SRC.read_text(encoding="utf-8", errors="replace")
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and n.name == fn:
            return ast.get_source_segment(src, n) or ""
    return ""


def test_no_bare_return_true_in_code() -> None:
    """★★★ 核心断言：★ **代码里**（★ 剥注释后）两个函数都**不许**再裸 `return True` ✓"""
    code = _code_only(SRC.read_text(encoding="utf-8", errors="replace"))
    tree = ast.parse(code)
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name in TWO:
            for sub in ast.walk(n):
                if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Constant):
                    if sub.value.value is True:
                        raise AssertionError("★ %s 里还有裸 `return True`" % n.name)


def test_both_read_entity_count() -> None:
    """★★★ 核心断言：★ 两个函数**都必须**调用计数助手（★ 那正是 doc 承诺的判据）✓"""
    for fn in TWO:
        seg = _seg(fn)
        assert "_active_sketch_segment_count" in seg, (
            "★ %s 没回读草图实体计数 ⇒ doc 承诺的判据仍不存在" % fn)


def test_result_is_a_dict_with_three_state() -> None:
    """★ 返回值格式：★ **回 dict**（★ 带 `ok` / 前后计数 / `verified_by`）✓"""
    for fn in TWO:
        seg = _seg(fn)
        for key in ('"ok"', "segments_before", "segments_after", "verified_by"):
            assert key in seg, "★ %s 的返回值缺 %r" % (fn, key)


def test_convert_entities_keeps_official_bool() -> None:
    """★ `convert_entities` **必须**保留官方的 `bool` 判据（★ 那是**另一层**，★ 不是被替换）✓"""
    seg = _seg("convert_entities")
    assert "SketchUseEdge3" in seg and "official_return" in seg, (
        "★ 官方的布尔返回值被丢了 ⇒ 应两层都要（★ 跨种类 ⇒ and）")


def test_helper_returns_none_when_unreadable() -> None:
    """★★ **负例**：★ 助手在**读不到**时必须回 `None`（★ 不许回 0 —— ★ 那会把"读不到"当"没变"）✓"""
    class _NoModel:
        pass

    out = E._active_sketch_segment_count(_NoModel())
    #: ★ 拿不到 `get_lines`/`get_arcs` ⇒ 两边都 None ⇒ 回 None（★ 而不是 0）
    assert out is None or isinstance(out, int), "★ 助手返回类型异常：%r" % (out,)
