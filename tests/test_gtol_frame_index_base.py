"""★ 测 GTol 帧的读法是**1 基 + 现行入口**（★ `JUDGE-C_D_E` 🔴 #8 · DW2-5 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IGtol\`）
# 文件:   `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#8**（★ `C-dw-2 DW2-5`）逐字：「★ 工程图上读 GTol 帧用
#   **0 基索引 + 2022 之前的读法**」· 判定「**不成立**」✓
#   ★★ **官方逐字（★ 我读了四个 md）** —— ★ **三重错**：
#     · ★ **0 基**：★ `IGtol/GetFrameSymbols3.md` 的 `## Parameters` ⇒
#       「**FrameNumber**: Frame number to examine (**1 or 2**)」✓
#     · ★★ **代次**：★ 同一页 Remarks ⇒「valid only if this Gtol was created in
#       **a version of SOLIDWORKS earlier than 2022**」· ★★ 而 `IGtol/GetFrame.md` ⇒
#       「valid only if … **2022 or later**」· ★ `FrameIndex` ⇒「**One-based**」✓
#     · ★★★ **帧号不连续**：★ `IGtol/GetFrameCount.md` 的 Remarks ⇒
#       「…displayed with **three** frames … those are frames **1, 2, and 5**. Frames 3 and 4 are **empty**.」✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import io
import sys
import tokenize
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "subskills" / "solidworks-engineering-drawing" / "scripts" / "drawing_workflow.py"
OFF = Path(r"C:\swapi\types\IGtol")


def _code_only() -> str:
    """★ 剥注释与 docstring（★ 事实 513 · 本会话第 12 次）。

    ⚠★ **注意**：★ `ast.unparse` **会把字符串引号统一成单引号**（`"` → `'`）⇒
      ★ 本模块的匹配串**一律用小写单引号形态**（★ 那是"元编程的产物"，★ 值记）✓
    """
    import ast
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


def test_official_pages_confirm_one_based_and_generation() -> None:
    """★★★ **前提断言**：★ 官方三页**确实**这么写（★ 判据的锚点）✓"""
    if not OFF.is_dir():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t1 = (OFF / "GetFrameSymbols3.md").read_text(encoding="utf-8", errors="replace")
    assert "1 or 2" in t1, "★ 官方没写 `1 or 2` 了 ⇒ 判据要重看"
    assert "earlier than 2022" in t1, "★ 官方没写代次限制"
    t2 = (OFF / "GetFrame.md").read_text(encoding="utf-8", errors="replace")
    assert "One-based" in t2 and "2022 or later" in t2, "★ `GetFrame` 的官方口径变了"
    t3 = (OFF / "GetFrameCount.md").read_text(encoding="utf-8", errors="replace")
    assert "1, 2, and 5" in t3, "★ 官方没写「帧号可以不连续」了"


def test_range_is_one_based() -> None:
    """★★★ 核心断言：★ **代码里**不许再有 `range(frame_count)` 当帧号（★ 那是 0 基）✓"""
    code = _code_only()
    assert "range(frame_count)" not in code, (
        "★ 还在 `range(frame_count)` ⇒ 0 基帧号（★ 官方是 `1 or 2`）")


def test_prefers_current_entry_igtol_getframe() -> None:
    """★★★ 核心断言：★ 必须**优先**走 2022+ 的现行入口 `GetFrame` ✓

    ⚠ 匹配串用**单引号**（★ `ast.unparse` 的规范化形态）✓
    """
    code = _code_only()
    assert "'GetFrame'" in code, "★ 没用现行入口 `IGtol.GetFrame`"
    i_new = code.find("'GetFrame'")
    i_old = code.find("'GetFrameSymbols3'")
    assert i_new != -1 and i_old != -1, "★ 两个入口之一丢了"
    assert i_new < i_old, "★ 旧读法跑到现行前面了 ⇒ 代次又反了"


def test_negative_case_empty_frames_are_recorded_not_faked() -> None:
    """★★ **负例**：★ **空帧必须如实记账**（★ 官方：帧可能是空的）—— ★ 不许假造内容 ✓"""
    code = _code_only()
    assert "'empty'" in code, "★ 没记 `empty` ⇒ 空帧与「有内容但读不到」分不开"
