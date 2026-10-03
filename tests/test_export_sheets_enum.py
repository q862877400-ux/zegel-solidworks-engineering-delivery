"""★ 测 `sw_export.export_to_pdf` 的 `SetSheets` 第一实参是**合法枚举**（★ `JUDGE-C_D_E` 🔴 #6 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方枚举（本机 `C:\swapi\enums\swExportDataSheetsToExport_e.md`）
# 文件:   `scripts/sw_export.py::export_to_pdf` ·
#         `scripts/sw_com_traps.py`（★ `SaveAs4` 那句的接口限定）
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#6**（★ `C-dw-3 #20 / #22`）逐字：
#   · #20 ★ 「`SetSheets(0, …)` … ★ en 的成员表**只有 1/2/3（无 0）**」✓
#   · #22 ★ 「**仓内两处矛盾**」：★ `sw_com_traps.py` 说「SaveAs4 不存在」·
#     ★★ 而同一仓 `sw_api_sldworks.py` 的 `ARITY` 里 `IModelDoc2` 段有 `'SaveAs4': 3` ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

OFFICIAL_ENUM = Path(r"C:\swapi\enums\swExportDataSheetsToExport_e.md")


def _seg(path: Path, fn: str) -> str:
    src = path.read_text(encoding="utf-8", errors="replace")
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and n.name == fn:
            return ast.get_source_segment(src, n) or ""
    return ""


def test_official_enum_has_no_zero() -> None:
    """★★★ **前提断言**：★ 官方枚举里**确实没有 0**（★ 判据的锚点）✓"""
    if not OFFICIAL_ENUM.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    text = OFFICIAL_ENUM.read_text(encoding="utf-8", errors="replace")
    vals = re.findall(r"\|\s*swExportData\w+\s*\|\s*(\d+)\s*\|", text)
    assert "0" not in vals, "★ 官方枚举有 0 了 ⇒ 本条判据要重看：%r" % vals
    assert sorted(vals) == ["1", "2", "3"], "★ 官方成员变了：%r" % vals


def _code_only(path: Path) -> str:
    """★★ 剥注释与 docstring（★ 事实 513 · 本会话第 9 次 —— 修正说明里逐字引了旧代码）。"""
    import io
    import tokenize
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


def test_set_sheets_never_passes_zero() -> None:
    """★★★ 核心断言：★ `SetSheets` 的第一实参**不许是 0**（★ 那不是合法成员）✓"""
    seg = _seg(REPO / "scripts" / "sw_export.py", "export_to_pdf")
    assert seg, "★ 找不到 export_to_pdf"
    #: ★ 只看**代码**（★ 注释里引了旧写法）
    code = _code_only(REPO / "scripts" / "sw_export.py")
    assert "SetSheets(0," not in code, "★ 还在传 0 ⇒ 不存在的枚举值"
    m = re.search(r"SetSheets\((\w+),", code)
    assert m, "★ 解析不出 SetSheets 的第一实参"
    assert m.group(1) == "which", "★ 第一实参应为一个变量 `which`：%r" % m.group(1)
    assert re.search(r"which\s*=\s*3\s+if\s+sheet_names\s+else\s+1", code), (
        "★ `which` 没按官方语义二选一（★ 给了名 ⇒ 3 · ★ 没给 ⇒ 1）")


def test_negative_case_no_other_zero_setsheets() -> None:
    """★★ **负例 · 全仓**：★ 别的文件里也不许有 `SetSheets(0,`（★ 只看代码）✓"""
    hits = []
    for f in sorted((REPO / "scripts").rglob("*.py")):
        if "SetSheets(0," in _code_only(f):
            hits.append(f.name)
    assert not hits, "★ 还有文件在传 0：%r" % hits


def test_saveas4_statement_has_interface_qualifier() -> None:
    """★★★ 核心断言：★ 「`SaveAs4` 不存在」那句**必须**带**接口限定**（★ 否则与 `ARITY` 矛盾）✓"""
    src = (REPO / "scripts" / "sw_com_traps.py").read_text(encoding="utf-8", errors="replace")
    assert "IModelDocExtension" in src and "SaveAs4" in src, "★ 没写接口限定"
    assert "IModelDoc2` 下**有** `SaveAs4" in src or "IModelDoc2` 下有 `SaveAs4" in src, (
        "★ 没写明 `IModelDoc2` 下有 `SaveAs4`（★ 那正是矛盾的另一半）")
