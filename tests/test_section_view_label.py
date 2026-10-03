"""★ 测剖视图**必须设标签**（★ `JUDGE-C_D_E` 🔴 #12 · C-dw-1 #3 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IDrSection\` · `IView\`）
# 文件:   `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::add_section_view` ·
#         `scripts/sw_drawing_expose.py::create_section_view`
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#12**（★ `C-dw-1 #3`）逐字：「剖面视图传空 `SectionLabel`
#   且**从不 `SetLabel2`** ⇒ **建出来的剖视图没有标签字母**」✓
#   ★★ **官方逐字（★ 我读了两个 md）**：
#     · `IDrSection/SetLabel2.md` ⇒ `int SetLabel2(string Label)` ⇒ 回 `swSetSectionLabelStatus_e`：
#       ★ **`< 0` = Failed** · ★ **`= 0` = Succeeded** · ★ **`> 0` = Succeeded（但有情况）** ✓
#     · ★★ `IView/GetSection.md` ⇒ ★ 从视图拿 `IDrSection`（★ 链路 `IView` → `GetSection()` →
#       `IDrSection` → `SetLabel2`）✓
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
WF = REPO / "subskills" / "solidworks-engineering-drawing" / "scripts" / "drawing_workflow.py"
EXPOSE = REPO / "scripts" / "sw_drawing_expose.py"
OFF = Path(r"C:\swapi\types")


def _code_only(path: Path) -> str:
    """★ 剥注释与 docstring（★ 事实 513 · 本会话第 14 次）。"""
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


def test_official_pages_confirm_label_chain() -> None:
    """★★★ **前提断言**：★ 官方两页**确实**给了这条链（★ 判据的锚点）✓"""
    f1 = OFF / "IDrSection" / "SetLabel2.md"
    f2 = OFF / "IView" / "GetSection.md"
    if not (f1.is_file() and f2.is_file()):
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t1 = f1.read_text(encoding="utf-8", errors="replace")
    assert "SetLabel2" in t1 and "swSetSectionLabelStatus_e" in t1, "★ `SetLabel2` 的官方口径变了"
    assert "GetSection" in f2.read_text(encoding="utf-8", errors="replace")


def test_section_view_passes_a_real_label() -> None:
    """★★★ 核心断言：★ `SectionLabel` **不许是空串** ✓"""
    code = _code_only(WF)
    assert 'CreateSectionViewAt5(x, y, 0, \'\', 0, None, 0)' not in code, (
        "★ 还在传空 `SectionLabel` ⇒ 剖视图没有标签字母")
    assert "CreateSectionViewAt5" in code and "str(label)" in code, "★ 没把 label 传进去"


def test_section_view_calls_setlabel2() -> None:
    """★★★ 核心断言：★ 必须走 `IView.GetSection()` → `SetLabel2`（★ 官方链）✓"""
    code = _code_only(WF)
    assert "SetLabel2" in code, "★ 仍然**从不** `SetLabel2`（★ 那正是本条病灶）"
    assert "GetSection" in code, "★ 没按官方链先拿 `IDrSection`"
    #: ★ 顺序：先 GetSection，再 SetLabel2
    assert code.find("GetSection") < code.find("SetLabel2"), "★ 顺序反了"


def test_negative_case_status_is_read_back_and_three_state() -> None:
    """★★ **负例 · 三态**：★ `SetLabel2` 的状态**必须回读**、★ 且**量不到要回 `None`** ✓

    ★★ 官方口径：★ **`< 0` 失败** · ★ **`= 0` 成功** · ★ **`> 0` 成功但有情况** ⇒
      ★★★ 所以判据是 **`>= 0`**，★ 而**取不到返回值时不许报成功** ✓
    """
    code = _code_only(WF)
    assert "label_status" in code and "label_ok" in code, "★ 没回读标签状态"
    assert ">= 0" in code, "★ 判据不对（★ 官方是 `< 0` 失败、`= 0` 成功、`> 0` 成功但有情况）"
    assert "label_ok" in code and "None" in code, "★ 三态里缺 `None`（★ 量不到不许报成功）"


def test_negative_case_caller_did_not_drop_the_label_evidence() -> None:
    """★★ **负例 · 调用方**：★ `sw_drawing_expose` 必须**把标签证据透传上去**（★ 不许丢）✓"""
    code = _code_only(EXPOSE)
    assert "label" in code, "★ 调用方没接 label"
    for k in ("label_status", "label_ok"):
        assert k in code, "★ 调用方把 `%s` 丢了 ⇒ 标签失败会被静默" % k
