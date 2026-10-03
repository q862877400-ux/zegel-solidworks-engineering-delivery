"""★ 测 `sw_delivery` 不再用废弃的 `SetSaveToName`（★ 阶段 2 · T1 · 含负例 · 含"指纹"那一类）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IPackAndGo\`）
# 文件:   `scripts/sw_delivery.py`
# 定位:   ★ 阶段 2 · T1 的逐条流程第一条：★ **先查官方签名与 Remarks** ✓
#   ★★ **官方逐字**（★ `IPackAndGo/SetSaveToName.md`）：
#     「**Obsolete. Superseded by `IPackAndGo::SetSaveToName2`**.」✓
#     旧签名 `(bool Override, string SaveToName)` ⇒ **2 参** ✓
#   ★★★ **后继逐字**（★ `IPackAndGo/SetSaveToName2.md`）：★ **无 Obsolete** ·
#     ★ 签名**同样 2 参、同名同型** · ★★ 而它的 `## Remarks` 逐字：
#     「The difference … is that this method **supports saving to minimal folders**.」✓
#   ★★★★ **∴ 本处只需换名字**（★ 实参不用动、★ 接口不用换）✓
#   ★★★★★ **而本条还带出**第二类用法**：★ `hasattr(value, "SetSaveToName")` 是拿成员名
#     当**指纹**探测对象 ⇒ ★★ **那**不是调用**、★ "搜调用点"搜不到它** ✓
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
SRC = REPO / "scripts" / "sw_delivery.py"
OFF_OLD = Path(r"C:\swapi\types\IPackAndGo\SetSaveToName.md")
OFF_NEW = Path(r"C:\swapi\types\IPackAndGo\SetSaveToName2.md")


def _code_and_strings() -> tuple[str, list[str]]:
    """★ 剥注释与 docstring ⇒ 回（代码, 字符串常量列表）✓

    ★★ **为什么要把字符串单独拿出来**：★ 本条要**分别**判两件事 ——
      ★ **属性访问**（`.SetSaveToName`）不许有 ★ 而 **字符串指纹**（`"SetSaveToName2"`）**要有** ✓
    """
    src = SRC.read_text(encoding="utf-8", errors="replace")
    toks = [t for t in tokenize.generate_tokens(io.StringIO(src).readline)
            if t.type != tokenize.COMMENT]
    s = tokenize.untokenize(toks)
    tree = ast.parse(s)
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b = getattr(n, "body", None) or []
            if b and isinstance(b[0], ast.Expr) and isinstance(
                    getattr(b[0], "value", None), ast.Constant) and isinstance(
                    b[0].value.value, str):
                b[0] = ast.Pass()
    strings = [n.value for n in ast.walk(tree)
               if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    return ast.unparse(tree), strings


def test_official_chain_is_as_documented() -> None:
    """★★★ **前提断言**：★ 官方那两页**确实**这么写（★ 判据的锚点）✓"""
    if not (OFF_OLD.is_file() and OFF_NEW.is_file()):
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    old = OFF_OLD.read_text(encoding="utf-8", errors="replace")
    new = OFF_NEW.read_text(encoding="utf-8", errors="replace")
    assert "Obsolete" in old and "SetSaveToName2" in old, "★ 旧页口径变了"
    assert "Obsolete" not in new, "★ 后继也被标废弃了 ⇒ 判据要重看"
    assert "minimal folders" in new, "★ 后继的 Remarks 变了"


def test_no_attribute_access_to_the_obsolete_member() -> None:
    """★★★ 核心断言：★ **属性访问**不许再是 `SetSaveToName`（★ 两处都换）✓"""
    code, _ = _code_and_strings()
    assert ".SetSaveToName(" not in code, "★ 还有 `.SetSaveToName(` 调用"
    assert code.count(".SetSaveToName2(") >= 2, (
        "★ 后继调用少于 2 处（★ 原文有两处）")


def test_the_fingerprint_is_also_updated() -> None:
    """★★★ 核心断言：★ **指纹探测**也要换成现行名 ✓

    ★★ 判据：★ 字符串常量里**要有** `SetSaveToName2`（★ `hasattr` 那个指纹）✓
    """
    _code, strings = _code_and_strings()
    assert "SetSaveToName2" in strings, "★ `hasattr` 的指纹还是旧名"
    assert "SetSaveToName" not in strings, (
        "★ 还有裸的旧名当字符串用（★ 那也会随废弃失效）")


def test_negative_case_docstring_may_keep_the_old_name() -> None:
    """★★ **负例 · 补正而不删除**：★ **docstring 里**引旧名是**允许**的 ✓

    ★★ 为什么：★ 本仓纪律是**「自我否定必须补正而不是删除」** ⇒
      ★★★ **旧名留在说明文字里是对的**（★ 它解释了这次改了什么）✓
      ★★ **而本条也顺手记下一个坑**：★★★ **只剥注释、不剥 docstring 的计数会假阳性** ✓
    """
    raw = SRC.read_text(encoding="utf-8", errors="replace")
    assert "SetSaveToName" in raw, (
        "★ 连说明文字里的旧名都没了 ⇒ 看不出这次改了什么")
