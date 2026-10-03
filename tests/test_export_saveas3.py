"""★ 测 `sw_export.py` 的保存入口都是**现行的 `SaveAs3`**（★ `JUDGE-C_D_E` 🔴 #6 · #21 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IModelDocExtension\`）
# 文件:   `scripts/sw_export.py::export_to_pdf` / `_export_generic` / `export_to_image`
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#6**（★ `C-dw-3 #21`）逐字：「★ PDF 走**已标废弃**的
#   `IModelDocExtension.SaveAs`（★ 而**同仓自己写着**「一律用 `SaveAs3`」）」✓
#   ★★ **官方逐字**（★ 我读了三个 md）：
#     · `IModelDocExtension/SaveAs.md` ⇒ 「**Obsolete. Superseded by `SaveAs2`**」✓
#     · `IModelDocExtension/SaveAs2.md` ⇒ 「**Obsolete. Superseded by `SaveAs3`**」✓
#     · `IModelDocExtension/SaveAs3.md` ⇒ **无 Obsolete 标记** ⇒ **现行入口** ✓
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
SRC = REPO / "scripts" / "sw_export.py"
OFFICIAL_DIR = Path(r"C:\swapi\types\IModelDocExtension")


def _code_only(path: Path) -> str:
    """★★ 剥注释与 docstring（★ 事实 513 · 本会话第 10 次 —— 修正说明里逐字引了旧代码）。"""
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


def test_official_chain_is_three_levels() -> None:
    """★★★ **前提断言**：★ 官方确实有**三级废弃链**（★ 判据的锚点）✓"""
    if not OFFICIAL_DIR.is_dir():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    assert "Obsolete" in (OFFICIAL_DIR / "SaveAs.md").read_text(encoding="utf-8", errors="replace")
    assert "Obsolete" in (OFFICIAL_DIR / "SaveAs2.md").read_text(encoding="utf-8", errors="replace")
    assert "Obsolete" not in (OFFICIAL_DIR / "SaveAs3.md").read_text(
        encoding="utf-8", errors="replace"), "★ `SaveAs3` 也被标废弃了 ⇒ 判据要重看"


def test_no_obsolete_saveas_in_code() -> None:
    """★★★ 核心断言：★ **代码里**不许再有 `Extension.SaveAs(` / `SaveAs2(` ✓"""
    code = _code_only(SRC)
    assert ".SaveAs(" not in code, "★ 还有废弃的 `Extension.SaveAs(`"
    assert ".SaveAs2(" not in code, "★ 还有废弃的 `Extension.SaveAs2(`"


def test_all_save_routes_use_saveas3() -> None:
    """★★★ 核心断言：★ **三处**保存路由都走 `"SaveAs3"`（★ 同一个文件里不许两种做法）✓"""
    code = _code_only(SRC)
    n = code.count("SaveAs3")
    #: ★ 断言**至少 3 次**（★ `export_to_pdf` · `_export_generic` · `export_to_image`）✓
    assert n >= 3, "★ `SaveAs3` 只出现 %d 次 ⇒ 还有路由没换" % n


def test_negative_case_pdf_keeps_its_export_data() -> None:
    """★★★ **负例 · 语义**：★ PDF 那条**第 4 参必须是 `pdf_data`** —— ★ 不许被换成空 Dispatch ✓

    ★★ 为什么重要：★ `SetSheets` 的效果**就挂在 `pdf_data` 上** ⇒
      ★ 换入口时若把第 4 参写成空 Dispatch，★ **图纸选择会静默失效**（★ 而导出仍然成功）✓
    """
    code = _code_only(SRC)
    #: ★ 抓 `export_to_pdf` 里的那次 `SaveAs3`
    seg = None
    src = SRC.read_text(encoding="utf-8", errors="replace")
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and n.name == "export_to_pdf":
            seg = ast.get_source_segment(src, n)
            break
    assert seg and "SaveAs3" in seg, "★ export_to_pdf 没走 SaveAs3"
    #: ★ 取 `"SaveAs3"` 之后的**那一段**（★ 到 `_print_result` 之前）⇒ 里面必须出现 `pdf_data`
    tail = seg.split('"SaveAs3"', 1)[1].split("_print_result", 1)[0]
    assert "pdf_data" in tail, (
        "★ PDF 那条第 4 参不是 `pdf_data` ⇒ `SetSheets` 的效果会静默失效")
