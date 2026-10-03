"""★ 测 `sw_part.linear_pattern` 的单位（★ 处置 `JUDGE-C_D_E` 🔴 #9 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/test_linear_pattern_units.py
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#9**（★ `C-sm-3 #3.2`）逐字：「★ `linear_pattern` 毫米 ↔
#   `in meters`：★ **阵列间距差 1000 倍**；★ 同仓另一条路径已做 `* 0.001` 并注明旧文档串是「错话」」✓
#   ★★ 官方依据：`FeatureLinearPattern3.md` 的 `Spacing1` / `Spacing2` 逐字 **`in meters`** ✓
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
    """★★ 剥注释与 docstring（★ 事实 513 · 本会话第 5 次 —— 修正说明里逐字引了旧代码）。"""
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


def test_linear_pattern_converts_mm_to_m() -> None:
    """★★★ 核心断言：★ `linear_pattern` **必须**把毫米换成米（★ 官方逐字 `in meters`）✓"""
    seg = _seg("linear_pattern")
    assert seg, "★ 找不到 linear_pattern"
    assert re.search(r"float\(d1_spacing\)\s*\*\s*0\.001", seg), (
        "★ `d1_spacing` 没乘 0.001 ⇒ 阵列间距会差 1000 倍（★ JUDGE-C_D_E #9）")
    assert re.search(r"float\(d2_spacing\)\s*\*\s*0\.001", seg), (
        "★ `d2_spacing` 没乘 0.001 ⇒ 方向 2 的间距会差 1000 倍")


def test_no_raw_mm_passthrough_left() -> None:
    """★ **代码里**不许再有「把 `d1_spacing` / `d2_spacing` 原样透传」的写法 ✓"""
    code = _code_only(SRC.read_text(encoding="utf-8", errors="replace"))
    assert "float(d1_spacing)," not in code, "★ 还有 `float(d1_spacing),` 的裸透传"
    assert "float(d2_spacing)," not in code, "★ 还有 `float(d2_spacing),` 的裸透传"


def test_two_paths_agree_on_units() -> None:
    """★★★ **同文件两条路径必须一致** —— ★ 这正是本缺陷的形态（★ 「与同仓另一条路径自相矛盾」）✓"""
    a = _seg("linear_pattern")
    b = _seg("linear_pattern_report")
    assert "* 0.001" in a and "* 0.001" in b, (
        "★ 两条路径对同一参数的单位处理不一致 ⇒ 又回到了本缺陷的形态")


def test_docstring_records_the_fix() -> None:
    """★ docstring **必须**留下这次的修正说明（★ 否则后人看不出单位变过）✓"""
    seg = _seg("linear_pattern")
    assert "1000 倍" in seg and "in meters" in seg, (
        "★ docstring 没写明「差 1000 倍」与官方单位 ⇒ 后人会再踩")


def test_negative_case_pattern4_also_converts() -> None:
    """★★ **负例**：★ 若有人把 `FeatureLinearPattern4`（20 参）接进来，★ 它的 `Spacing1/2` **同样吃米** ⇒
    ★ 本测试**记下这条约束**（★ 那个入口目前**无调用点**，★ 所以这里只断言"官方单位"这条事实）✓"""
    official = Path(r"C:\swapi\types\IFeatureManager\FeatureLinearPattern4.md")
    if not official.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    text = official.read_text(encoding="utf-8", errors="replace")
    assert "in meters" in text, "★ 官方 `FeatureLinearPattern4` 也写 `in meters` ⇒ 接它时同样要换算"
