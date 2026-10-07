"""★ 测 `sw_part.sketch_slot` 的参数位置与系数（★ 处置 `JUDGE-C_D_E` 🔴 #4 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方签名 / 枚举 / 示例（三处都读）
# 文件:   tests/test_sketch_slot_params.py
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#4**（★ `E-4 #1`）逐字：「★ 长度被塞进官方枚举位、
#   第 3 位才是 `Width` ⇒ ★ **槽口尺寸差一个系数 2**，且 Param 描述「半径＝宽度一半」
#   与实传的**整宽**相反」✓
#   ★★ 官方 `CreateSketchSlot(int SlotCreationType, int SlotLengthType, double Width, …)`；
#     ★ 官方示例第 2 参传枚举成员、第 3 参传 `0.05`（= Width）✓
#   ★★★ 修完必须用负例证明它真能拦（★ 事实 62）✓
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
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

SRC = REPO / "scripts" / "sw_part.py"


def _code_only(text: str) -> str:
    """★★ 剥注释与 docstring（★ 事实 513 · 本会话第 6 次 —— 修正说明里逐字引了旧代码）。"""
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
    src = SRC.read_text(encoding="utf-8", errors="replace")
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and n.name == fn:
            return ast.get_source_segment(src, n) or ""
    return ""


def test_width_is_two_times_radius() -> None:
    """★★★ 核心断言：★ 官方 `Width` **必须**拿到 `2 * radius`（★ 本函数语义是半径）✓"""
    seg = _seg("sketch_slot")
    assert seg, "★ 找不到 sketch_slot"
    assert re.search(r"2\.0\s*\*\s*float\(radius\)", seg), (
        "★ `Width` 没乘 2 ⇒ 槽口尺寸差一个系数 2（★ JUDGE-C_D_E #4）")


def test_slot_length_type_is_a_valid_enum_member() -> None:
    """★★★ 核心断言：★ 第 2 参（`SlotLengthType`）**必须**是合法枚举值 —— ★ 官方只有 `0` / `1` ✓

    ★★ 实现方式：★ 把调用**剥注释后**再看，★ 并**按逗号切实参**（★ 行内注释会干扰正则）✓
    """
    code = _code_only(SRC.read_text(encoding="utf-8", errors="replace"))
    #: ★★ 2026-10-07（接手轮 · 规格 214 T-214-04）**只改正则，不动任何断言** ——
    #:   ★ 起因：本条断言从某轮起一直红，而**实现是对的**（`scripts/sw_part.py` 的 `sketch_slot`
    #:   实参逐字就是 `0, 0, 2.0 * float(radius), …`）✓
    #:   ★★ 真因是**调用形态变了**：`sketch_slot` 不再直呼方法，而是走
    #:     `get_com_member(<SketchManager>, "CreateSketchSlot", <实参…>)`
    #:     ⇒ ★ 旧正则 `CreateSketchSlot\(`（要求名字后紧跟 `(`）**永远匹配不上** ✗
    #:   ⚠ 这类"**契约测试要跟着实现形态一起改**"在本仓有先例（`tests/test_sw_selection_contract.py`
    #:     轮 470 逐字写过同一句话）⇒ ★★ **断言（第 1/2/3 参各是什么）一个字不改**，
    #:     ★ 只把"从哪里开始抓实参"跟着实现挪一格 ✓
    #: ★ `[^)]*` 会被 `float(radius)` 的内层 `)` 截断 ⇒ 保持原做法：**宽松匹配到 `float(radius)` 之后**
    m = re.search(r"""CreateSketchSlot['"]\s*,\s*([^)]*float\(radius\)[^)]*)""", code, re.S)
    assert m, "★ 剥注释后仍解析不出 CreateSketchSlot 的实参"
    args = [a.strip() for a in m.group(1).split(",")]
    assert len(args) >= 3, "★ 实参不足 3 个：%r" % args
    assert args[0] == "0", "★ 第 1 参（SlotCreationType）应为 0（line）：%r" % args[0]
    assert args[2].startswith("2.0 * float(radius)"), (
        "★ 第 3 参（Width）应为 `2 * radius`：%r" % args[2])
    assert args[1] == "0", (
        "★ 第 2 参（SlotLengthType）应为合法枚举 0（CenterCenter），★ 实为 %r" % args[1])


def test_no_radius_in_enum_slot_in_code() -> None:
    """★ **代码里**（★ 剥注释后）不许再把 `radius` 塞进那个枚举位 ✓"""
    code = _code_only(SRC.read_text(encoding="utf-8", errors="replace"))
    assert "radius, radius" not in code, "★ 还有 `radius, radius` 的错位写法"


def test_docstring_records_the_fix() -> None:
    """★ docstring **必须**留下这次的修正说明（★ 含官方签名与示例）✓"""
    seg = _seg("sketch_slot")
    assert "SlotLengthType" in seg and "Width" in seg, "★ docstring 没写明官方签名"
    assert "系数 2" in seg or "2 * radius" in seg.replace(" ", ""), "★ 没写明系数 2 这件事"


def test_negative_case_enum_page_has_only_two_members() -> None:
    """★★ **负例 · 记档**：★ 官方 `swSketchSlotLengthType_e` **只有 2 个成员** ⇒
    ★ 任何 >1 的值都是越界（★ 那正是病灶形态）✓"""
    official = Path(r"C:\swapi\enums\swSketchSlotLengthType_e.md")
    if not official.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    text = official.read_text(encoding="utf-8", errors="replace")
    vals = re.findall(r"\|\s*swSketchSlotLengthType_\w+\s*\|\s*(\d+)\s*\|", text)
    assert sorted(vals) == ["0", "1"], (
        "★ 官方枚举成员变了（★ 现为 %r）⇒ 传 `radius` 更是越界" % vals)
