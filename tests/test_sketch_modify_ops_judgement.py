"""★ 测 `sw_sketch_modify_ops.py` 的 5 个函数是否兑现了 **doc 承诺的几何判据**（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/test_sketch_modify_ops_judgement.py
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#1 · E5-1** 逐字：「★ 仓内 doc：`★ 判据 =
#   ModelToSketchTransform.ArrayData 的平移分量变化` ／ 改几何的 ⇒ `判据 = 草图线段端点的
#   bbox 变没变` ★ 而目标：`return {"ok": True, … "verified_by": "no_exception", …}` ／
#   ★★ **`ModelToSketchTransform` 与 `ArrayData` 在该文件各 0 次**」· 判定「**确认**」✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import inspect
import re
import sys
import tokenize
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import sw_sketch_modify_ops as M                                          # noqa: E402

SRC_FILE = REPO / "scripts" / "sw_sketch_modify_ops.py"
FNS = ["sketch_move", "sketch_rotate", "sketch_scale", "sketch_stretch", "sketch_flip"]


def _code_only(text: str) -> str:
    """★★ **剥掉注释与 docstring** 再查 —— ★ 因为**来源块里逐字引了旧代码**（★ 见事实 513）。

    ★★ 本会话**两次**踩到这个：★ 不剥注释的检查会在自己的记录里"找到"旧代码 ⇒ 假阳性 ✓
    """
    import io
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


def test_no_hardcoded_ok_true_in_code() -> None:
    """★★★ 核心断言：★ **代码里**（★ 剥掉注释与 docstring 后）5 个函数**一个都不许**写死 `ok: True`。"""
    code = _code_only(SRC_FILE.read_text(encoding="utf-8", errors="replace"))
    assert not re.search(r'"ok"\s*:\s*True', code), (
        "★ 代码里仍有写死的 ok:True ⇒ 「没抛异常」又当成「做成了」")


def test_all_five_use_geom_evidence() -> None:
    """★ 5 个函数**必须**都走 `_geom_evidence`（★ doc 承诺的两个判据的实现）✓"""
    miss = [fn for fn in FNS if "_geom_evidence" not in inspect.getsource(getattr(M, fn))]
    assert not miss, "★ 这些函数没兑现 doc 承诺的判据：%s" % miss


def test_promised_names_now_appear() -> None:
    """★ 裁判说那两个名字「各 0 次」⇒ ★ **现在必须出现**（★ 那是修复的直接证据）✓"""
    code = SRC_FILE.read_text(encoding="utf-8", errors="replace")
    assert "ModelToSketchTransform" in code, "★ doc 承诺的 `ModelToSketchTransform` 还是没出现"
    assert "ArrayData" in code, "★ doc 承诺的 `ArrayData` 还是没出现"


def test_moved_is_three_state() -> None:
    """★★★ `_moved` 必须是**三态**：★ 变了 `True` · ★ 没变 `False` · ★★ **取不到 `None`** ✓

    ★★ 为什么关键：★ 若把"取不到"当成"变了"，★ 那就**又回到了「无条件 True」**那个病灶 ✓
    """
    assert M._moved(None, [1.0]) is None, "★ 取不到时 `_moved` 必须回 None（不许当成变了）"
    assert M._moved([1.0], None) is None
    assert M._moved([1.0], [1.0]) is False
    assert M._moved([1.0], [1.0, 2.0]) is True


def test_geom_evidence_reports_none_when_unmeasurable() -> None:
    """★★ **负例**：★ 两个量**都取不到** ⇒ `ok` **必须** `None`（★ **不许报 True**）✓"""
    class _NoModel:
        pass

    out = M._geom_evidence(_NoModel(), None, None)
    assert out["ok"] is None, "★★ 量不到却报了成功 ⇒ 静默成功（违反规则 6）：%r" % out
    assert "verified_by" in out and "不报成功" in out["verified_by"]
