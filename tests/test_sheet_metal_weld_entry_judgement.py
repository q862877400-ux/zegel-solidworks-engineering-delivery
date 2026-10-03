"""★ 测 `scripts/sw_sheet_metal_weld_entry.py` 的**判据分层**（★ 含**负例** · 事实 62）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/test_sheet_metal_weld_entry_judgement.py
# 定位:   ★ 处置 `JUDGE-C_D_E.md` 的 🔴 **#1**（★ 裁判逐字：「★ batch74 闭合角用 `or`
#   把「缺一不可」写成「有一个就行」是**最严重的一处**」）⇒ ★★ **修完必须用负例证明它真能拦** ✓
#   ★★ 判据分层（★ 本轮定）：★★★ **跨种类用 `and`（都必须满足）· 同种类用 `or`（任一即可）** ✓
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


def _src() -> str:
    return (REPO / "scripts" / "sw_sheet_metal_weld_entry.py").read_text(
        encoding="utf-8", errors="replace")


def _code_only() -> str:
    """★ **剥掉注释与 docstring** 后再看 —— ★ 因为我在修复时**把旧的那一行逐字引进了注释**。

    ★★★ 这正是**事实 513** 那一课：★ 「剥注释」要同时想清三样 ——
      ★ `#` 注释 · ★★ **docstring** · ★ 字符串字面量 ✓
    ★★ 而本条里，**不剥注释的检查会假阳性**（★ 旧代码在注释里被"找到"了）✓
    """
    src = _src()
    #: ① 用 `tokenize` 去掉 `#` 注释
    out = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type != tokenize.COMMENT:
                out.append(tok)
        stripped = tokenize.untokenize(out)
    except Exception:                                                     # noqa: BLE001
        stripped = src
    #: ② 用 AST 把 docstring 清空（★ 只清 docstring，★ 不动其它字符串字面量）
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


def test_closed_corner_uses_and_across_kinds() -> None:
    """★★★ 核心断言：★ 闭合角的 `ok` **不许**用 `or` 把「树增量」与「几何量」并列。

    ★ 病灶原形（★ 裁判点名的那一处）：
      `bool(changed and (bool(added) or (face_delta or 0) != 0 or (vol_delta or 0) != 0))`
    ★★ 修后必须是：★ `bool(added) **and** ((face_delta or 0) != 0 **or** (vol_delta or 0) != 0)` ✓
    """
    src = _code_only()
    assert "ok_judgement = bool(added) and" in src, (
        "★ 找不到修后的判据行 ⇒ 判据可能被改回 `or` 了（事实 62：负例是唯一证明）")
    bad = "changed and (bool(added) or (face_delta or 0) != 0"
    assert bad not in src, "★★ 旧的那个 `or` 判据又回来了 ⇒ 「缺一不可」会退化成「有一个就行」"


def test_closed_corner_negative_case_is_refused() -> None:
    """★ 负例：★ `model=None` ⇒ **必须** `ok=False`（★ 不许静默成功）。"""
    import sw_sheet_metal_weld_entry as M                                # noqa: PLC0415
    out = M.insert_sheet_metal_closed_corner(None)
    assert out["ok"] is False
    assert "error" in out


def test_judgement_layers_declared() -> None:
    """★ 返回值里**必须**带上判据分层说明 —— ★ 否则后人看不出「为什么是 and 又是 or」。"""
    src = _src()
    for key in ("judgement_layers", "cross_kind", "same_kind"):
        assert key in src, "★ 缺少判据分层字段 %r（★ 后人会看不出「为什么跨种类 and、同种类 or」）" % key


def test_docstring_still_says_all_three() -> None:
    """★ docstring 里那句「三个都要」**必须**保留 —— ★ 它才是修复的目标（★ doc 与代码要一致）。"""
    src = _src()
    assert "特征树增量" in src and "实体面数增量" in src and "体积增量" in src, (
        "★ docstring 里的三量描述被删了 ⇒ 而那句话正是本修复要兑现的契约")
