"""★ 测 `CreateSpline2` 的「记档保留」**有真机证据**（★ 阶段 2 · T1 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\ISketchManager\CreateSpline3.md`）
# 文件:   `scripts/sw_part.py::sketch_spline` · `tools/probe_createspline3.py`（★ 只报不动）·
#         `output/createspline3-probe-evidence.json`
# 定位:   ★ 阶段 2 · T1 的逐条流程第 ② 步：★ **真机验证后继可不可调** ✓
#   ★★ **官方逐字**：★ `CreateSpline3(object PointData, object Surfs, object Direction,
#     bool SimulateNaturalEnds, **out object Status**)` ⇒ **5 参** ·
#     ★★ 而 Remarks 逐字：★ 「To create a **2D spline**… ★ **All other parameters with
#       null or Nothing.**」✓
#   ★★★ **真机结果**（★ 三种出参包装）：
#     · `out_dispatch()` ⇒ **`类型不匹配`（位置 5）**
#     · **空 Dispatch** ⇒ **`类型不匹配`（位置 5）**
#     · `None` ⇒ **`类型不匹配`（位置 5）**
#     · ★★ **基线 `CreateSpline2(data, False)` ⇒ `built=True` · 段数 0→1** ✓
#   ★★★★ **∴ 那条「后继到不了」是**真机否证过的** —— ★ 不是猜的** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_part.py"
EVID = REPO / "output" / "createspline3-probe-evidence.json"
PROBE = REPO / "tools" / "probe_createspline3.py"
OFF = Path(r"C:\swapi\types\ISketchManager\CreateSpline3.md")


def test_official_successor_has_five_params() -> None:
    """★★★ **前提断言**：★ 官方后继**确实是 5 参**（★ 判据的锚点）✓"""
    if not OFF.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t = OFF.read_text(encoding="utf-8", errors="replace")
    assert "out System.object Status" in t, "★ 后继的末参变了 ⇒ 判据要重看"
    assert "null or Nothing" in t, "★ Remarks 里的 2D 调法变了"


def test_probe_evidence_says_all_three_forms_failed() -> None:
    """★★★ 核心断言：★ 证据文件里**三种包装全败、★ 而基线建成** ✓"""
    if not EVID.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(EVID.read_text(encoding="utf-8", errors="replace"))
    rows = {r["form"]: r for r in d["rows"]}
    v3 = [r for k, r in rows.items() if k.startswith("v3_")]
    assert len(v3) == 3, "★ 三种包装的记录不全：%r" % list(rows)
    for r in v3:
        assert r.get("error") and "类型不匹配" in r["error"], (
            "★ `%s` 竟然不报「类型不匹配」了 ⇒ 判据要重看" % r["form"])
        assert "5" in r["error"], "★ 出错位置不是 5 ⇒ 与「末参」的结论不符"
    base = rows.get("v2_baseline") or {}
    assert base.get("built") is True, "★ 基线没建成 ⇒ 证据不可用"


def _seg_code_only(fn: str) -> str:
    """★ 只取**一个函数**的代码（★ 剥掉它自己的 docstring）✓

    ⚠★ **为什么不能取整个模块**：★ 本仓**别的函数**的 docstring 里也在讲 `CreateSpline3`
      （★ 那是"补正而不删除"的产物）⇒ ★★ **取全模块会把说明文字当成代码** ✓
    ⇒ ★★★ **这正是事实 51**：★★★ **分析范围要贴合代码的**组织单元**（★ 所在函数）** ✓
    """
    import ast
    src = SRC.read_text(encoding="utf-8", errors="replace")
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and n.name == fn:
            if n.body and isinstance(n.body[0], ast.Expr) and isinstance(
                    getattr(n.body[0], "value", None), ast.Constant) and isinstance(
                    n.body[0].value.value, str):
                n.body[0] = ast.Pass()
            return ast.unparse(n)
    return ""


def test_code_still_calls_the_working_member() -> None:
    """★★★ 核心断言：★ 记档期间**仍要调 `CreateSpline2`** ✓

    ★★ 判据：★ 而**不许**出现对 `CreateSpline3` 的**调用**（★ 它到不了 ⇒ 用了就会崩）✓
      ★★★ **范围限定在 `sketch_spline` 这一个函数里**（★ 事实 51）✓
    """
    seg = _seg_code_only("sketch_spline")
    assert seg, "★ 找不到 `sketch_spline`"
    assert "CreateSpline2" in seg, "★ 可用的那个没了"
    #: ★ 判据：★ **调用的形态**（★ `"CreateSpline3"` 那个字符串被传进 get_com_member）
    assert "'CreateSpline3'" not in seg and '"CreateSpline3"' not in seg, (
        "★ 竟然调了到不了的后继")


def test_negative_case_reason_cites_machine_evidence() -> None:
    """★★★ **负例 · 理由要有真机证据**：★ 那条记档必须**引证据文件与探针** ✓

    ★★ 为什么：★ 本仓判「不可换」的**门槛**是**真机否证**、★ 不是「看起来复杂」⇒
      ★★★ **所以注释里要能看到**证据文件名 + 探针名**** ✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find("def sketch_spline")
    seg = t[i:i + 5000]
    assert "createspline3-probe-evidence.json" in seg, "★ 没引真机证据文件"
    assert "probe_createspline3.py" in seg, "★ 没引探针名（★ 证据要可复跑）"
    assert "位置 5" in seg or "位置 **5**" in seg, "★ 没写清失败位置（★ 那才对上「末参」）"
