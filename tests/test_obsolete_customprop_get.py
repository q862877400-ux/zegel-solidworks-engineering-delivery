"""★ 测 `sw_custom_property` 用**现行的 `Get6` + `VT_BYREF` 包法**（★ 阶段 2 · T1 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\ICustomPropertyManager\`）
# 文件:   `scripts/sw_custom_property.py` · `scripts/sw_document_data.py`（★ 现成的范例）
# 定位:   ★ 阶段 2 · T1 的逐条流程第一条：★ **先查官方签名与 Remarks** ✓
#   ★★ **官方实测（★ 我逐个读了整族）**：★ `Get` / `Get2` / `Get3` / `Get4` / `Get5` **全标 `Obsolete`** ·
#     ★★ **只有 `Get6` 未标**（★ `int Get6(string FieldName, bool UseCached, out string ValOut,
#       out string ResolvedValOut, out bool WasResolved, out bool IsLinked)`）✓
#   ★★★ **而本模块原来那段"不能用 `Get2+`"的结论要**更正一半****：
#     ★ **仍成立**：★ **不包 `VARIANT(VT_BYREF | …)` 的出参确实报 `类型不匹配`** ✓
#     ★★ **被推翻**：★ **`Get2+` 不是"不通"** —— ★ 包对了就能用 ✓
#     ★★★ **反例就在同一个仓**：★ `sw_document_data.read_custom_property` 用 `VT_BYREF` 包四个出参、
#       调 `Get6` ⇒ ★★ **而它**工作**（★ 轮 78 真机验过）** ✓
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
SRC = REPO / "scripts" / "sw_custom_property.py"
PEER = REPO / "scripts" / "sw_document_data.py"
OFF = Path(r"C:\swapi\types\ICustomPropertyManager")


def _code_only(path: Path) -> str:
    """★ 剥注释与 docstring（★ 事实 513）。"""
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
                        getattr(b[0].value, "value", None), ast.Constant) and isinstance(
                        b[0].value.value, str):
                    b[0] = ast.Pass()
        s = ast.unparse(tree)
    except Exception:                                                     # noqa: BLE001
        pass
    return s


def test_official_family_status() -> None:
    """★★★ **前提断言**：★ 官方整族里**只有 `Get6` 未废弃**（★ 判据的锚点）✓"""
    if not OFF.is_dir():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    for n in ("Get", "Get2", "Get3", "Get4", "Get5"):
        f = OFF / (n + ".md")
        if f.is_file():
            assert "Obsolete" in f.read_text(encoding="utf-8", errors="replace"), \
                "★ `%s` 竟然不废弃了 ⇒ 判据要重看" % n
    g6 = OFF / "Get6.md"
    if g6.is_file():
        assert "Obsolete" not in g6.read_text(encoding="utf-8", errors="replace"), \
            "★ `Get6` 也被标废弃了 ⇒ 判据要重看"


def test_no_obsolete_get_in_code() -> None:
    """★★★ 核心断言：★ 代码里**不许**再调废弃的 `"Get"` ✓"""
    code = _code_only(SRC)
    assert '"Get"' not in code and "'Get'" not in code, "★ 还在调废弃的 `Get`"


def test_uses_get6_with_byref_variants() -> None:
    """★★★ 核心断言：★ 必须用 `Get6` **且出参用 `VT_BYREF` 包** ✓

    ★★ 为什么必须两件一起：★ **不包 `VT_BYREF` 就报 `类型不匹配`** ⇒
      ★★★ **"换成 `Get6`"与"包对出参"是**一件事的两半**** ✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    assert "Get6" in t, "★ 没用现行的 `Get6`"
    assert "VT_BYREF" in t, "★ 没包 `VT_BYREF` ⇒ 会报「类型不匹配」"
    assert "VARIANT" in t, "★ 没造 VARIANT"


def test_negative_case_the_peer_is_the_reference() -> None:
    """★★ **负例 · 同仓一致性**：★ 同仓那条**也用 `Get6` + `VT_BYREF`** ⇒ ★ 两条要一致 ✓"""
    code = _code_only(PEER)
    assert "Get6" in code, "★ 同仓那条范例变了 ⇒ 判据要重看"
    assert "VT_BYREF" in code, "★ 同仓那条范例没有 `VT_BYREF`"
