"""★ EC00 残留 ① 判据 —— 拉伸必须**先选中草图**（★ 官方 Example 的调用序）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `C:\swapi\examples\Insert_Feature_Extrusion_Example_VB.md`（★ **官方 Example 逐字**）
#         `C:\swapi\types\IFeatureManager\FeatureExtrusion3.md`（★ `D1` = **meters**）
#         `scripts/sw_part.py`（★ `extrude_boss` · `_ensure_sketch_selected`）
#         `output/_probe_ec00_extrude_official.json`（★ 真机两臂对照）
# 定位:   ★ 清 **EC00 残留 ①**（★ 拉伸建不出来）。★★★ **真因（★ 真机两臂实测）**：
#         ★ **拉伸前必须选中草图** —— ★ 官方 Example 逐字那行：
#         `boolstatus = Part.Extension.SelectByID2("Sketch1", "SKETCH", 0, 0, 0, False, 0, Nothing, 0)`
#         ★★ 臂 A（选中）⇒ **建成**、★ 臂 B（不选）⇒ **返回 None**。
# 官方依据: 见上（★ Example 给的是**调用序** —— ★ 铁律 §十四）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM · ★ 用**静态核 + 真机读数**）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs" / "302-ec00-trustworthy-tool-base"
PROBE = ROOT / "output" / "_probe_ec00_extrude_official.json"
PART = ROOT / "scripts" / "sw_part.py"


def _fn_body(src: str, name: str) -> str:
    """★ 取函数体（★ **AST** —— ★ 不用 `find("\\ndef ")`）。

    ⚠ 第一版用 `src.find("\\ndef ", i+1)` 切 —— ★★ 而订正后的 docstring 里**含 `def `**
      ⇒ ★ 切**早了** ⇒ ★ 判据**假红**（★ 说「找不到 `_ensure_sketch_selected`」，★ 其实在）。
      ★★ **⇒ 取函数体要用 AST**（★ 与 `test_ec00_unit_boundary_negative.py` 同一手法）。
    """
    import ast
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(src, node) or ""
    return ""


def _strip_docstring(fn_src: str) -> str:
    """★ 剥掉函数体里的**文档串**（★ 只留**代码**）。

    ★★ 为什么需要：★ 判「A 在 B 之前」时，★ 若 A/B 的名字**也出现在注释/docstring 里**
      ⇒ ★ `find` 会命中**注释**的位置 ⇒ ★ 判据**假红**（★ 本判据第二版就这么红了一次）。
    """
    import ast
    try:
        node = ast.parse(fn_src).body[0]
    except SyntaxError:
        return fn_src
    if node.body and isinstance(node.body[0], ast.Expr) and isinstance(
            getattr(node.body[0], "value", None), ast.Constant) and isinstance(
            node.body[0].value.value, str):
        node.body = node.body[1:]          #: ★ 砍掉第一个 Expr（★ 那是 docstring）
    return ast.unparse(node)


def test_extrude_requires_a_selected_sketch_in_source():
    """★★★ 残留 ①：★ `extrude_boss` **必须先选中草图**（★ 官方 Example 的调用序）。

    ★★ 依据（★ 官方 Example 逐字）：★ 拉伸前那行 `SelectByID2("Sketch1", "SKETCH", …, False, 0, …)`。
    ★ 判据：★ `extrude_boss` 的函数体里**必须**先调 `_ensure_sketch_selected`。
    """
    body = _fn_body(PART.read_text(encoding="utf-8", errors="replace"), "extrude_boss")
    assert body, "★ 取不到 `extrude_boss` 的函数体"
    #: ⚠ 第二版直接对**整个函数体** `find` ⇒ ★★ 而订正后的 **docstring 里同时提到**
    #:   `_ensure_sketch_selected` 与 `FeatureExtrusion3` ⇒ ★ 比到的是**注释里的位置** ✗
    #:   （★ 报 `assert 1070 < 236`）⇒ ★★ **必须先剥掉 docstring**。
    code = _strip_docstring(body)
    assert "_ensure_sketch_selected" in code, (
        "★★ `extrude_boss` 的**代码**里没有 `_ensure_sketch_selected`"
        " ⇒ ★ 可能不选草图就拉伸（★ 会回 None）")
    #: ★★ 且必须在 `FeatureExtrusion3` **之前**
    assert code.find("_ensure_sketch_selected") < code.find("FeatureExtrusion3"), (
        "★★ 选草图在 `FeatureExtrusion3` **之后** ⇒ ★ 顺序错")


def test_extrude_machine_evidence_two_arms():
    """★★★ 残留 ①：★ 真机两臂对照必须**落盘**（★ 选中 ⇒ 建成；★ 不选 ⇒ `None`）。

    ★★ 这是**判据的核心**：★ 不是「看起来对」，★ 而是**两臂差异**证明前置。
    """
    assert PROBE.is_file(), "★ 缺真机两臂对照证据 `output/_probe_ec00_extrude_official.json`"
    d = json.loads(PROBE.read_text(encoding="utf-8"))
    a, b = d.get("arm_a", {}), d.get("arm_b", {})
    #: ★★★ 臂 A：★ 选中 ⇒ **建成**
    assert a.get("selected_by_name") is True, "★ 臂 A 没选中草图"
    assert a.get("returned_is_none") is False, "★ 臂 A 的返回是 None ⇒ 没建成"
    assert a.get("has_extrude") is True, "★★ 臂 A 特征树里没有拉伸特征"
    assert a.get("body_count") == 1, "★★ 臂 A 体数不是 1（实得 %r）" % a.get("body_count")
    #: ★★★ 臂 B：★ 不选 ⇒ **失败**
    assert b.get("returned_is_none") is True, (
        "★★ 臂 B（不选草图）居然建成了 ⇒ ★ 「必须先选中」这个结论**不成立**")
    assert b.get("has_extrude") is False, "★★ 臂 B 不该建成"


def test_extrude_depth_unit_is_meters_per_official():
    """★★★ 残留 ②：★ `extrude_boss` 的 `depth` 单位 —— ★ 官方说 **meters**。

    ★★ 依据（★ `C:\\swapi` 逐字）：★ `D1`: **「Depth of extrusion for first end in meters」**。
    ★ 判据：★ 本仓真机脚本用 `mm(...)` 传参（★ 即**先转米**）⇒ ★ **那证明收的是米**。
    """
    reg = ROOT / "tests" / "solidworks_configuration_family_regression.py"
    assert reg.is_file(), "★ 找不到真机回归脚本"
    body = reg.read_text(encoding="utf-8", errors="replace")
    #: ★★★ 本仓真机脚本的写法：`extrude_boss(model, sketch_name, mm(...))`
    assert "extrude_boss(model, sketch_name, mm(" in body, (
        "★★ 真机脚本没有用 `mm(...)` 包 `extrude_boss` 的深度 ⇒ ★ 单位口径不明")


def test_extrude_docstring_is_corrected_to_meters():
    """★★★ 残留 ②：★ `extrude_boss` 的 docstring **必须**写对单位（★ 官方说米）。

    ★★ 依据：★ 它原写「depth: 拉伸深度（**毫米**）」★ 而**没有**乘 `_MM_TO_M`
      ⇒ ★★ **文档与实现不一致**（★ 同模块的 `sketch_line` **乘了**）。
    """
    src = PART.read_text(encoding="utf-8", errors="replace")
    body = _fn_body(src, "extrude_boss")
    assert body, "★ 取不到 `extrude_boss` 的函数体"
    doc_end = body.find('"""', body.find('"""') + 3)
    doc = body[:doc_end + 3]
    #: ⚠ 第三版直接禁 `"拉伸深度（**毫米**）" not in doc` ⇒ ★★ **假红** ——
    #:   因为**订正记录本身就引用了那句错的原文**（★ 那是**证据**、★ 该留）。
    #: ★★ 真判据：★ **参数行**（★ 以 `depth:` 开头的**声明行**）必须写「米」。
    depth_lines = [ln.strip() for ln in doc.splitlines() if ln.strip().startswith("depth:")]
    assert depth_lines, "★ docstring 里找不到 `depth:` 参数行"
    #: ★★ 参数行必须**先**声明「米」（★ 那是**该函数的单位**）
    assert any("米" in ln for ln in depth_lines), (
        "★★ `depth:` 参数行没写明单位是「米」：%r" % depth_lines)
    #: ⚠ 第四版禁「毫米」出现在该行 ⇒ ★★ **又假红** —— ★ 因为**正确的写法**是
    #:   「★ **米** —— ★ 毫米请用 `mm(x)` 转换」⇒ ★ 那句「毫米」是**给调用者的指引**，★ 该留。
    #: ★★ 真判据：★ **第一个**出现的单位词必须是「米」（★ 不能以「毫米」起头）。
    for ln in depth_lines:
        i_m = ln.find("米")
        i_mm = ln.find("毫米")
        assert i_m >= 0, "★ 参数行没写「米」：%r" % ln
        if i_mm >= 0:
            assert i_m < i_mm, (
                "★★ 参数行**先**说「毫米」⇒ ★ 会误导调用者（★ 残留 ②）：%r" % ln)
