"""★ 测新能力 `extrude_depth`：★ 判据、单位口径、以及**不替调用方换算**（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IExtrudeFeatureData2\`）
# 文件:   `scripts/sw_feature_readback.py::extrude_depth`（★ 阶段 3 补的能力）·
#         `tools/probe_extrudefeaturedata_getdepth.py` · `tools/probe_extrude_depth_recheck.py`（★ 只报不动）·
#         `output/extrudefeaturedata-getdepth-evidence.json` · `output/extrude-depth-capability-recheck.json`
# 定位:   ★ 阶段 3（T2 缺口地图）⇒ 密度图算出 **查 × 特征 = 官方 451 · 我们 0** ⇒
#   ★★ 而那一格实际有 **1008 个成员 / 174 个族**（★ 现算）⇒ 本能力是**第一个** ✓
#   ★★★ **官方逐字**：★ `System.double GetDepth( System.bool Forward )` ·
#     ★ `## Returns` = 「Depth of the extrusion」· ★★ **⚠ 官方**没写单位**** ✓
#   ★★★★ **真机读数**（★ 两次、★ 不同深度）：★ 20mm ⇒ **20.0** · ★ 5mm ⇒ **5.0** ⇒
#     ★ **它随**文档单位**（★ `GetUnits() = [0, …]` ⇒ `LengthUnit = 0` = 毫米）** ✓
#   ★★★★★ **而"找独立锚点"那一步失败得有价值**：★ 我本想用 `IBody2::GetBodyBox` 锚定 ⇒
#     ★★ **而它自己**混口径**** —— 实测 `[-0.05, -0.03, -20.0, 0.05, 0.03, 0.0]`：
#     ★ X 是 ±0.05（**米**）· ★ Z 是 -20.0…0.0（**毫米**）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_feature_readback.py"
E1 = REPO / "output" / "extrudefeaturedata-getdepth-evidence.json"
E2 = REPO / "output" / "extrude-depth-capability-recheck.json"
OFF = Path(r"C:\swapi\types\IExtrudeFeatureData2\GetDepth.md")


def test_official_page_gives_no_unit() -> None:
    """★★★ **前提断言**：★ 官方那页**确实没写单位**（★ 判据的锚点）✓"""
    if not OFF.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t = OFF.read_text(encoding="utf-8", errors="replace")
    assert "GetDepth" in t and "Depth of the extrusion" in t, "★ 官方页变了"
    #: ★★★★ **判据要精确**（★ 我第一版写 `"meter" in t.lower()`）⇒ ★★ **红了** ——
    #:   真因：★ **`## Parameters` 这个词**含 `meter`**** ✓
    #:   ⇒ ★ 所以要用**整词**匹配（★ 与**事实 51**同族：★ 判据要贴合被判的对象）✓
    low = t.lower()
    for word in ("meters", "meter", "millimeters", "millimeter"):
        assert not re.search(r"\b%s\b" % word, low), (
            "★ 官方页现在写了单位 `%s` ⇒ 判据要重看（★ 那就该照它写）" % word)


def test_capability_records_the_document_unit_basis() -> None:
    """★★★ 核心断言：★ 返回值必须带 `unit_source`、★ 且**不替调用方换算** ✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    fn = None
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == "extrude_depth":
            fn = n
    assert fn is not None, "★ 找不到 `extrude_depth`"
    code = ast.unparse(fn)
    assert "unit_source" in code, "★ 没带 `unit_source` ⇒ 调用方要猜单位"
    #: ★★ **判据：★ 不许做 1000 倍换算**（★ 那会把"随文档单位"变成"永远米"）✓
    for bad in ("/ 1000.0", "* 1000.0", "/ 1000", "* 1000"):
        assert bad not in code, "★ 函数里出现了换算 `%s` ⇒ 它不该替调用方换算" % bad


def test_evidence_shows_two_depths_read_back_same_basis() -> None:
    """★★★ 核心断言：★ 证据里**两个不同深度**读数与所建**同口径** ✓"""
    if not E2.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(E2.read_text(encoding="utf-8", errors="replace"))
    rows = d.get("rows") or []
    assert len(rows) >= 2, "★ 复查证据少于两次：%r" % rows
    for r in rows:
        asked = float(r["asked_depth_mm"])
        got = r["readback"].get("depth")
        assert got is not None, "★ 没读到 depth：%r" % r
        assert abs(float(got) - asked) < 1e-9, (
            "★ 建 %s ⇒ 读回 %s ⇒ 口径不一致" % (asked, got))
        assert r.get("GetUnits") and r["GetUnits"][0] == 0, (
            "★ 文档单位不是毫米了（%r）⇒ 判据要重看" % r.get("GetUnits"))


def test_negative_case_the_mixed_unit_anchor_is_recorded() -> None:
    """★★★★ **负例 · 锚点自己混口径**：★ 必须把 `GetBodyBox` 那条记下来 ✓

    ★★ **为什么**：★★★ **"找一个独立的量来锚定单位"这条判据，
      要先证明**那个量自己是干净的**** ——
      ★ 否则**你会拿一个混口径的东西去校准另一个** ✓
      ★ 与**事实 40**同族：★ **一个读数如果看起来像正常值，比没有读数更糟** ✓
    """
    blob = E1.read_text(encoding="utf-8", errors="replace") if E1.is_file() else ""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    hay = blob + src
    assert "GetBodyBox" in hay, "★ 没记 `GetBodyBox` 那次尝试"
    assert "混口径" in hay or "混了两套" in hay, "★ 没写明它**自己**混口径"
