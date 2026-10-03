"""★ 测 `batch58` 的**文件头与注册表一致**（★ `JUDGE-C_D_E` 🔴 #16 · E-4 #3 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 出厂类型库反射 dump（`_raw/**/iface_cosworks.txt`）
# 文件:   `mcp-server/tool_specs_batch58.py`
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#16**（★ `E-4 #3`）逐字：「★ 文件头写「`temperature`
#   仍不注册」、同文件却**已注册**且 arity 仍停在被怀疑过时的 CHM 声明上」✓
#   ★★ **而实测复核（★ 我读了反射 dump）**：
#     · ★ `_raw/**/iface_cosworks.txt:1533-1534` 逐字
#       `CWTemperature AddTemperature(Object, Int32&)` ⇒ ★ **2 参数、与 CHM 一致** ✓
#     · ★★ 而**本仓生成的 `ARITY` 表**（`scripts/sw_api_sldworks.py`）里**没有**它 ⇒
#       ★★★ **那是那张表的**覆盖缺口**、★ 不是「该成员不存在」** ✓
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
SPEC = REPO / "mcp-server" / "tool_specs_batch58.py"
ARITY_SRC = REPO / "scripts" / "sw_api_sldworks.py"
COSWORKS = REPO / "_raw"


def _comments_only(path: Path) -> str:
    """★★ **只取注释**（★ 与"只取 docstring"相反的取法）—— ★ 本条要判的正是**文件头注释** ✓"""
    out = []
    src = path.read_text(encoding="utf-8", errors="replace")
    try:
        for t in tokenize.generate_tokens(io.StringIO(src).readline):
            if t.type == tokenize.COMMENT:
                out.append(t.string)
    except Exception:                                                     # noqa: BLE001
        pass
    return "\n".join(out)


def test_reflection_dump_has_addtemperature_with_arity_two() -> None:
    """★★★ **前提断言**：★ 反射 dump **确实**有它、★ 且是 2 参数（★ 判据的锚点）✓"""
    if not COSWORKS.is_dir():
        return                                                            # ★ 反射 dump 不在本机 ⇒ 跳过
    hits = []
    for f in COSWORKS.rglob("iface_cosworks.txt"):
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            if "AddTemperature" in line:
                hits.append(line.strip())
    assert hits, "★ 反射 dump 里没有 `AddTemperature` 了 ⇒ 判据要重看"
    assert any("Object" in h and "Int32" in h for h in hits), (
        "★ 反射里的参数表变了：%r" % hits[:3])


def test_header_does_not_say_unregistered() -> None:
    """★★★ 核心断言：★ 文件头**不许**再说「仍不注册」（★ 同文件已注册）✓"""
    comments = _comments_only(SPEC)
    #: ★ 允许**引述**旧句（★ 更正块里要引），★ 但**不许**把它当现状陈述
    if "仍不注册" in comments:
        assert "更正" in comments or "已注册" in comments, (
            "★ 文件头还有「仍不注册」、★ 却没写明那是**旧说法** ⇒ 自相矛盾")
    assert "已注册" in comments, "★ 没写明该条**已注册**"
    assert "AddTemperature(Object, Int32&)" in comments, "★ 没给反射逐字（★ 那是新依据）"


def test_negative_case_registry_and_header_agree() -> None:
    """★★ **负例 · 一致性**：★ 文件头说的与**注册表实际**必须一致 ✓

    ★★ 判据：★ **spec 列表里确有 `solidworks_simulation_apply_temperature`** ——
      ★ 所以"不注册"这个陈述**在任何情况下都不该出现为现状** ✓
    """
    src = SPEC.read_text(encoding="utf-8", errors="replace")
    assert '"solidworks_simulation_apply_temperature"' in src, (
        "★ 该工具**确实**已注册 ⇒ 文件头说「不注册」必是过时的")
    assert "apply_temperature_report" in src, "★ 函数名也没了"


def test_negative_case_arity_table_gap_is_recorded() -> None:
    """★★ **负例 · 记账**：★ 那条「本仓 ARITY 表**没收录**它」必须写明（★ 否则又被当成"不存在"）✓"""
    comments = _comments_only(SPEC)
    assert "ARITY" in comments, "★ 没写明那是**本仓 ARITY 表**的覆盖缺口"
