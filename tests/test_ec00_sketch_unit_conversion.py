"""★ 判据 —— `sw_part` 的 10 个草图图元**都必须把毫米换算成米**（★ 1000× bug 的守卫）。

★★★ **为什么要有它**（★ 2026-10-10 真机裁决）：
  ★ `scripts/sw_part.py` 的 `sketch_*` **对外收毫米**，而 **COM 侧单位是米**（★ 事实 2）。
  ★★ 2026-10-08 的「根因修复」只给 **5 个**函数加了 `_MM_TO_M`，★ **另外 4 个漏了** ⇒
    ★ `sketch_polygon` / `sketch_slot` / `sketch_ellipse` / `sketch_centerline`
      **把毫米原样送进 COM** ⇒ **1000×** ✓
  ★ 真机读数（★ 证据 `output/_probe_unit_verdict.json`）：
    · 修前：★ `polygon(radius=25)` ⇒ 跨度 **50000 mm** ✗ · ★ `centerline(0,0→25,25)` ⇒ **25000 mm** ✗
    · 修后：★ 两者分别 **50 mm** ✓ / **25 mm** ✓（★ 与「有换算」那组**同口径**）
  ★★★ **⇒ 本判据是**结构性的****：★ 只要哪个 `sketch_*` 少了一次换算，它就红 ✓
    （★ 比「记住要换算」强 —— ★ 与**事实 62**「门禁写了 ≠ 有效」同族）
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_part.py`（★ 10 个 `sketch_*` 助手）
#         `docs/known-facts.md` 事实 2（COM 侧单位是米）· 事实 73（★ **已过时** —— 见下）
#         `output/_probe_unit_verdict.json`（★ 真机裁决读数）
# 定位:   ★ 守卫「草图图元单位换算」这一族 bug；★ 起因是 2026-10-08 修复**漏了 4 个函数**。
# 官方依据: `C:\\swapi\\types\\ISketchManager\\Create*.md`（★ 坐标单位 = **meters**）
#         `IModelDoc2::GetPartBox`（★ 回**米** —— 探针就是靠它量的）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 用 AST 静态核，★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SW_PART = ROOT / "scripts" / "sw_part.py"

#: ★★ **收长度坐标的草图图元**（★ 都必须换算）
LENGTH_SKETCH_FNS = (
    "sketch_line", "sketch_rectangle", "sketch_corner_rectangle", "sketch_circle",
    "sketch_arc", "sketch_polygon", "sketch_slot", "sketch_spline",
    "sketch_ellipse", "sketch_centerline",
)


def _body_source(src: str, tree: ast.Module, name: str) -> str:
    """★ 取某函数的**函数体**源码（★ 跳过 docstring —— ★ 否则注释里提一句就假绿）。"""
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)):
                body = body[1:]
            return "\n".join((ast.get_source_segment(src, s) or "") for s in body)
    raise AssertionError("★ 找不到函数 %r" % name)


def test_all_ten_length_sketch_fns_convert_mm_to_m():
    """★★★★★ **10 个草图图元全部换算**（★ 缺一个 ⇒ 那个就是 1000× bug）。

    ★★ 判据：★ 函数体里必须出现 `_MM_TO_M` 或 `/1000.0`。
    ★★★ **红基线已验**：★ 去掉 `sketch_polygon` 的换算 ⇒ 本判据**立刻红** ✓
    """
    src = SW_PART.read_text(encoding="utf-8")
    tree = ast.parse(src)
    missing = []
    for fn in LENGTH_SKETCH_FNS:
        body = _body_source(src, tree, fn)
        if ("_MM_TO_M" not in body) and ("1000.0" not in body):
            missing.append(fn)
    assert not missing, (
        "★★★ 这些草图图元**没把毫米换算成米** ⇒ 会得 **1000×**：%r\n"
        "    ★ 依据：★ COM 侧单位是米（事实 2）；★ 同族函数用 `_MM_TO_M` ✓" % missing)


def test_the_four_previously_broken_fns_are_named_explicitly():
    """★★★★ **点名守那 4 个曾经漏掉的**（★ 它们就是本判据的起因）。

    ★★ 依据（★ 2026-10-10 真机裁决）：★ `sketch_polygon` / `sketch_slot` /
      ★ `sketch_ellipse` / `sketch_centerline` —— ★ **修前**实测得 50000/25000/50000 mm ✗
    """
    src = SW_PART.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for fn in ("sketch_polygon", "sketch_slot", "sketch_ellipse", "sketch_centerline"):
        body = _body_source(src, tree, fn)
        assert "_MM_TO_M" in body, (
            "★★★ `%s` 又漏了换算 ⇒ 那个 1000× bug 复发了" % fn)


def test_spline_converts_via_its_own_division():
    """★★ `sketch_spline` 走的是**逐点 `/1000.0`**（★ 与 `_MM_TO_M` 等价）。

    ★★ 如实说明：★ 它**不是**用 `_MM_TO_M`（★ 因为它是**扁平数组**构造），
      ★ 所以判据要认**两种形态** —— ★ 否则会误报 ✓
    """
    src = SW_PART.read_text(encoding="utf-8")
    tree = ast.parse(src)
    body = _body_source(src, tree, "sketch_spline")
    assert "1000.0" in body, "★ `sketch_spline` 的逐点换算不见了"


def test_module_declares_the_unit_contract():
    """★★ 模块里必须**写明单位契约**（★ 对外毫米 · ★ COM 米）。

    ★★ 依据（★ 事实 73 的教训）：★ 「docstring 里的单位声明**不会被任何门禁检查**」
      ⇒ ★ 至少要有**一处**明文说明，★ 供接手方对照 ✓
    """
    src = SW_PART.read_text(encoding="utf-8")
    assert "_MM_TO_M = 1.0 / 1000.0" in src, "★ 换算常量不见了"
    #: ★★ **换算块附近必须说明**「对外毫米、COM 米」
    #:   ⚠ 第一版只搜前 12000 字符 ⇒ ★ 那段在 L556 之后、**超出窗口** ⇒ 假红（★ 判据自己的错）
    idx = src.find("_MM_TO_M = 1.0 / 1000.0")
    assert idx > 0, "★ 找不到换算常量那行"
    window = src[max(0, idx - 3000): idx + 500]
    assert ("COM 侧单位是米" in window) or ("COM 吃米" in window), (
        "★★ 换算常量附近没写明「COM 侧单位是米」⇒ 接手方会再判错一次（★ 事实 73 的坑）")
