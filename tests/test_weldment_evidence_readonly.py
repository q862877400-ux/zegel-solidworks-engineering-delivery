"""★ 测 `weldment_evidence` 的**纯回读路径不写模型**（★ `JUDGE-C_D_E` 🔴 #13 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IBodyFolder\UpdateCutList.md`）
# 文件:   `scripts/sw_weldment.py::weldment_evidence` · `_read_cut_list_folders` · `update_cut_list`
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#13**（★ `E-1 #7`）逐字：「★ doc 说
#   「`create_missing_cut_list=False` 时**只读**」，★ 目标**无条件**调 `update_cut_list`
#   → ★ 对 CutListFolder 调 `UpdateCutList`（★ **写操作**）⇒ ★ **标注为只读的调用实际会改模型**」✓
#   ★★ **官方逐字**：★ `IBodyFolder/UpdateCutList.md` ⇒
#     · Description ⇒ 「**Updates** an automatically generated cut list.」✓
#     · Returns ⇒ 「True if … **successfully updated**」✓
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
SRC = REPO / "scripts" / "sw_weldment.py"
OFF = Path(r"C:\swapi\types\IBodyFolder\UpdateCutList.md")


def _code_only() -> str:
    """★ 剥注释与 docstring（★ 事实 513 · 本会话第 15 次）。"""
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


def _seg(fn: str) -> str:
    """★ 取一个函数的**代码段**（★ **剥掉它自己的 docstring** —— ★ 事实 513）。

    ⚠★ 本会话第 16 次：★ 我在 `_read_cut_list_folders` 的 docstring 里**逐字引了**
      `UpdateCutList`（★ 为了说明为什么不能用它）⇒ ★★ 于是「只读版里不许有它」的检查
      **假阳性** ✓
    ⇒ ★ **定则**：★ 凡「在源码里找某字符串」的检查，**一律先剥注释与 docstring** ✓
    """
    src = SRC.read_text(encoding="utf-8", errors="replace")
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and n.name == fn:
            #: ★ 若首句是字符串常量 ⇒ 换成 `pass`（★ 保留函数形状、★ 去掉 docstring）✓
            if n.body and isinstance(n.body[0], ast.Expr) and isinstance(
                    getattr(n.body[0], "value", None), ast.Constant) and isinstance(
                    n.body[0].value.value, str):
                n.body[0] = ast.Pass()
            return ast.unparse(n)
    return ""


def test_official_page_says_update_not_read() -> None:
    """★★★ **前提断言**：★ 官方页**确实**写的是「Updates」（★ 判据的锚点）✓"""
    if not OFF.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t = OFF.read_text(encoding="utf-8", errors="replace")
    assert "Updates an automatically generated cut list" in t, "★ 官方口径变了"
    assert "successfully updated" in t, "★ Returns 也变了"


def test_evidence_default_does_not_write() -> None:
    """★★★ 核心断言：★ **默认**（`create_missing_cut_list=False`）**不许**调 `update_cut_list` ✓"""
    seg = _seg("weldment_evidence")
    assert seg, "★ 找不到 `weldment_evidence`"
    #: ★ 那句必须**在分支里**、★ 不许无条件
    assert "if do_update:" in seg, "★ 没把更新放进分支 ⇒ 又是无条件写"
    assert "_read_cut_list_folders" in seg, "★ 纯回读路径没走只读版"


def test_read_only_variant_has_no_updatecutlist() -> None:
    """★★★ 核心断言：★ 只读版里**不许**出现 `UpdateCutList` ✓"""
    seg = _seg("_read_cut_list_folders")
    assert seg, "★ 没有只读版"
    assert "UpdateCutList" not in seg, "★ 只读版里还有写操作"
    #: ★ 而 `update_ok` 必须是 `None`（★ **"没做" ≠ "做了但失败"**）
    #: ⚠★ 匹配串用**单引号** —— ★ `ast.unparse` 会把字符串引号规范化（★ 轮 64 记过同一个坑）✓
    assert "'update_ok': None" in seg, "★ 没把 `update_ok` 如实记成 `None`"
    assert "update_attempted" in seg, "★ 没记「这次有没有尝试写」"


def test_negative_case_write_path_still_exists() -> None:
    """★★ **负例**：★ **写路径必须仍然可用**（★ 不许为了"只读"把功能删了）✓"""
    seg = _seg("weldment_evidence")
    assert "update_cut_list(model)" in seg, "★ 写路径没了 ⇒ 需要更新时没得用"
    #: ★ 而 `update_cut_list` 自己**仍然**要调官方那个写成员
    assert "UpdateCutList" in _seg("update_cut_list"), "★ 写路径没真正更新"
