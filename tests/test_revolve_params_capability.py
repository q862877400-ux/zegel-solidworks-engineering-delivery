"""★ 测「第十三族的口径」+「三层单位契约」+「按 ToolSpec 契约调」（★ 含负例 · 轮 130）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `C:\\swapi\\types\\IRevolveFeatureData2\\*.md` +
#         真机证据 `output/revolve-params-capability-recheck.json`
# 文件:   tests/test_revolve_params_capability.py（★ 新）
# 定位:   ★★★★★★★ 2026-10-04（轮 130）**量出第十三族**：
#     ★ `ISweepFeatureData`… 不 —— ★ **`IRevolveFeatureData2::GetRevolutionAngle` 的口径 = radians** ✓
#     **三条独立证据**：★ ① 读回 `0.5235987755982988`（★ **π/6 的精确值**）·
#       ★★ ② **几何**：★ 体积 `785.398` = 「30° 扇形环」解析值 `785.398` ·
#       ★★★ ③ **反面对照**：★ 误传度时读回 `4.867259 rad = 278.8734°`、★ 而
#         `30 rad mod 360° = 278.8734°`（★ 差 0.000000°）✓
#   ★★★★ **⚠ 而本轮我先栽了一次**（★ 价值最高的一条）：
#     ★ 我**绕过 ToolSpec 直调能力层**、★ 却按 **ToolSpec 的名字**（`angle_deg`）传了**度** ⇒
#     ★★ **而能力层的契约是**弧度****（★ 形参名就叫 `angle_rad`）⇒
#     ★★★ **⇒ **三层都对、★ 只有我错了**** ⇒ ★ **正是 AGENTS.md 明写的**
#       「跑探针验能力时：★ **按 `ToolSpec` 的契约调，别手调内部实现**」✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
sys.path.insert(0, str(TESTS))
from _funcbody import func_source  # noqa: E402

SRC = REPO / "scripts" / "sw_feature_readback.py"
PART = REPO / "scripts" / "sw_part.py"
PROBE = REPO / "tools" / "probe_revolve_params_recheck.py"


def test_the_thirteenth_family_is_recorded_as_a_conclusion() -> None:
    """★★★ 核心断言：★ 第十三族那条**结论**（radians）在能力里 ✓"""
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "revolve_params")
    assert "第十三族" in body, "★ 没记下族号"
    assert "radians" in body, "★ 口径的结论没写"
    #: ★★ 三条证据都要在（★ 那是"怎么知道的"）✓
    assert "0.5235987755982988" in body, "★ 精确读数没记下"
    assert "785.398" in body, "★ 几何那条没记下"
    assert "278.8734" in body, "★ 反面对照没记下"


def test_the_three_layers_have_three_different_contracts() -> None:
    """★★★★ 核心断言：★ **三层各写一种**、★ 而**每层都对** ✓

    ★★ **为什么这条值钱**：★ 本轮我判"是 bug"、★ 结果**不是** ——
      ★★★ **⇒ 三层的契约本来就不一样**（★ 而**每层内部自洽**）✓
    """
    #: ★ ① 能力层：★ 形参名是 `angle_rad` ✓
    p = PART.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(p)
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "revolve_boss")
    assert [a.arg for a in fn.args.args][2] == "angle_rad", (
        "★ 能力层的形参名应是 `angle_rad` ⇒ 它的契约是**弧度**")
    doc = ast.get_docstring(fn) or ""
    assert "弧度" in doc, "★ 能力层的 docstring 要写明是弧度"
    #: ★★ ② ToolSpec 层：★ 对外 `angle_deg` **且要有换算** ✓
    spec = (REPO / "mcp-server" / "tool_specs_batch17.py").read_text(encoding="utf-8",
                                                                    errors="replace")
    i = spec.find("solidworks_revolve_boss")
    assert i != -1
    seg = spec[max(0, i - 1200):i + 900]
    assert '"angle_deg"' in seg or "'angle_deg'" in seg, "★ ToolSpec 的对外名应是 `angle_deg`"
    assert "_radians_of_deg" in seg, "★ ToolSpec 要在**边界**把度换成弧度"


def test_negative_case_the_probe_passes_radians_to_the_capability_layer() -> None:
    """★★★★ 核心断言：★ 探针按**能力层的契约**传**弧度**（★ 不是 `angle_deg` 那个名字）✓

    ★★ **为什么**：★ 我第一版传了 `ANGLE_DEG`（= `30.0`）⇒
      ★★★ **⇒ 实际转出 278.87°**（★ 因为 30 rad mod 360°）⇒
      ★★ **⇒ 那**不是能力坏了、★ 是我调错了**** ✓
    """
    t = PROBE.read_text(encoding="utf-8", errors="replace")
    code = "\n".join(l for l in t.splitlines() if not l.strip().startswith("#"))
    assert "math.radians(ANGLE_DEG)" in code, (
        "★ 探针没把度换成弧度 ⇒ 会再次「调错」")
    assert "revolve_boss(model, str(sk), ANGLE_DEG)" not in code, (
        "★ 又把**度**直接传给能力层了")


def test_negative_case_the_type_substring_is_the_real_name() -> None:
    """★★★★ **负例 · 类型名子串要是**真机打出来的那个**** ✓

    ★★ **为什么**：★ `Revolution` 里**没有** `Revolve`（★ `Revol`+`ution` vs `Revol`+`ve`）⇒
      ★★★ **⇒ 我先前"以为"它在里面** ⇒ **⇒ 而那**不是 bug、是我看错了**** ✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    assert '"Revolution"' in t, "★ 兜底的类型名子串应是真机打出来的 `Revolution`"
    assert '"Revolve",' not in t, "★ 又用回了 `Revolve`（★ 它不在 `Revolution` 里）"
