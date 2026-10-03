"""★ 测 E-3 剩下三条（`gtol_insert` · `create_cut_list` · `set_study_option`）的判据（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/test_e3_remaining_judgements.py
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#3**（★ `E-3 #3 / #4 / #6`）—— ★ 裁判逐字：
#   · #3 `gtol_insert`：「★ doc 承诺『回对象 **且** 特征树变化』两件事，★ 代码只做了前一件」✓
#   · #4 `create_cut_list`：「★ doc 承诺『回切割清单文件夹当证据』，★ 目标函数回的是 COM 特征对象」✓
#   · #6 `set_study_option`：「★ doc 字面承诺『raises』，★ 实际 `except` 把 `KeyError` 捕获并回成 dict」✓
#   ★★ 三条**形态相同**：★ **doc 承诺了 X、★ 代码做的是 Y** ✓
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


def _code_only(path: Path) -> str:
    """★★ 剥注释与 docstring（★ 事实 513 · 本会话第 8 次 —— 修正说明里逐字引了旧代码）。"""
    text = path.read_text(encoding="utf-8", errors="replace")
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


def _seg(path: Path, fn: str) -> str:
    src = path.read_text(encoding="utf-8", errors="replace")
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and n.name == fn:
            return ast.get_source_segment(src, n) or ""
    return ""


def test_gtol_reads_feature_tree() -> None:
    """★★★ #3：★ `insert_gtol` **必须**读特征树（★ doc 承诺的第二个判据）✓"""
    seg = _seg(REPO / "scripts" / "sw_gtol.py", "insert_gtol")
    assert seg, "★ 找不到 insert_gtol"
    assert "_feature_names_snapshot" in seg, "★ 没读特征树 ⇒ 只做了 doc 承诺的一半"
    assert '"ok": bool(added)' in seg, "★ `ok` 没接上特征树增量"


def test_gtol_helper_refuses_zero_for_unreadable() -> None:
    """★★ **负例**：★ 特征树读不到 ⇒ **不算通过**（★ 不许静默成功）✓"""
    seg = _seg(REPO / "scripts" / "sw_gtol.py", "insert_gtol")
    assert "added is not None else False" in seg, (
        "★ 树取不到时没回 False ⇒ 会把「读不到」当成「建成了」")


def test_cut_list_returns_dict_with_folders() -> None:
    """★★★ #4：★ `create_cut_list` **必须**回 dict（★ doc 承诺「回切割清单文件夹当证据」）✓"""
    seg = _seg(REPO / "scripts" / "sw_weldment.py", "create_cut_list")
    assert seg, "★ 找不到 create_cut_list"
    for key in ("feature_name", "cut_list_folders", "verified_by"):
        assert key in seg, "★ 返回值缺 %r" % key
    assert "_cut_list_folders(" in seg, "★ 没真去取文件夹清单"


def test_cut_list_helper_exists() -> None:
    """★ 助手 `_cut_list_folders` **必须**存在，★ 且用既有的 `CutListFolder` 类型名判据 ✓"""
    seg = _seg(REPO / "scripts" / "sw_weldment.py", "_cut_list_folders")
    assert seg and "CutListFolder" in seg, "★ 助手没按类型名筛 ⇒ 会收进非切割清单的特征"


def test_study_option_doc_is_corrected() -> None:
    """★★★ #6：★ 两条工具 doc **必须**已更正（★ 不许再说 "raises" 是**当前**行为）✓"""
    p = REPO / "mcp-server" / "tool_specs_batch37.py"
    text = p.read_text(encoding="utf-8", errors="replace")
    assert text.count("旧描述（已作废）") >= 2, "★ 两条 doc 都要标「旧描述（已作废）」"
    assert text.count("不抛异常") >= 2, "★ 两条都要写明**现在**是「不抛异常、回结构化失败」"
    #: ★★ 而**真相一侧**（包装层）**必须**仍然把 KeyError 吃成 dict（★ 改 doc 不改行为）
    seg = _seg(REPO / "scripts" / "sw_simulation_study_options.py", "set_study_option_report")
    assert "except Exception" in seg and '"ok": False' in seg, (
        "★★ 包装层不该改成抛异常 —— ★ 改的是 doc，不是行为")
