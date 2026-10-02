"""钉住 `sw_export.export_to_pdf` 的两处**已修**缺陷（不连 SolidWorks）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_sw_export_pdf_contract.py
# 定位:   2026-10-01（轮 158）真机查出这个**此前从未能运行过**的函数有**两处**缺陷：
#           ① 第一行 `model.GetSldWorksObject()` —— **两套官方源都查不到该成员**
#              （铁律 5：名字缺席 = 官方 API 里没有它）⇒ 零件/工程图**都**抛
#              `AttributeError: <unknown>.GetSldWorksObject`；
#           ② `SaveAs(output_path, …)` 收 `Path` ⇒ `TypeError: must be real number, not WindowsPath`。
#         ⇒ 本文件把这两处**钉死**，不许回退。
# 官方依据: `ISldWorks.GetExportFileData`（`C:\\swapi\\types\\ISldWorks\\GetExportFileData.md`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT))


def _src() -> str:
    return (REPO_ROOT / "scripts" / "sw_export.py").read_text(encoding="utf-8")


def _fn_src() -> str:
    src = _src()
    i = src.index("def export_to_pdf(")
    j = src.find("\ndef ", i + 1)
    return src[i:j if j > 0 else len(src)]


def test_the_nonexistent_member_is_gone():
    """@brief ★★★ `GetSldWorksObject` 不许再出现在**代码**里 —— 官方没有这个成员（铁律 5）。

    ⚠ 判据必须只看**代码**：docstring 里**要**写明它（那是这次缺陷的记录）。
    ⚠⚠ 第一版判据搜的是整个函数源码 ⇒ 把 docstring 里那句说明也算了进来 ⇒
    **假阳性**。⇒ 改成用 `ast` 遍历**属性访问**，只认真正的代码。
    """
    import ast as _ast
    src = _src()
    tree = _ast.parse(src)
    hits = []
    for node in _ast.walk(tree):
        if isinstance(node, _ast.FunctionDef) and node.name == "export_to_pdf":
            for sub in _ast.walk(node):
                if isinstance(sub, _ast.Attribute) and sub.attr == "GetSldWorksObject":
                    hits.append(getattr(sub, "lineno", "?"))
    assert not hits, (
        "`export_to_pdf` 的**代码**里又出现了 `GetSldWorksObject`（第 %s 行）—— "
        "**两套官方源都查不到该成员**（铁律 5），它会让整个函数抛 AttributeError"
        % (hits,))


def test_saveas_path_is_stringified():
    """@brief ★★ 传给 `SaveAs` 的路径必须是 **`str`**（`Path` 会抛 `TypeError`）。"""
    body = _fn_src()
    m = re.search(r"\.SaveAs\(([^,]+),", body)
    assert m, "找不到 SaveAs 调用"
    assert m.group(1).strip().startswith("str("), (
        "`SaveAs` 的路径参数没有 `str(...)` 包起来 —— "
        "`Path` 会抛 `TypeError: must be real number, not WindowsPath`")


def test_sw_is_an_optional_keyword():
    """@brief ★ 调用方可以传 `sw`（项目链里有）；不传也能用（向后兼容）。"""
    import sw_export
    sig = inspect.signature(sw_export.export_to_pdf)
    assert "sw" in sig.parameters, "应当有可选入参 `sw`"
    p = sig.parameters["sw"]
    assert p.kind is inspect.Parameter.KEYWORD_ONLY, "`sw` 应当是仅关键字参数"
    assert p.default is None, "`sw` 的缺省应当是 None"


def test_docstring_records_the_two_defects():
    """@brief ★★ docstring 要写明这两处缺陷与「此前从未能运行过」。"""
    body = _fn_src()
    assert "轮 158" in body, "要标注实测轮次"
    assert "GetSldWorksObject" in body, "要写明第一处"
    assert "从未能运行过" in body, "要写明它此前**从未能运行过**"
