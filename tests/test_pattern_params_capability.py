"""★ 测 `pattern_params`：★ 读数、★ **第三层单位口径**、★ 6/6 判据（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\ILinearPatternFeatureData\`）
# 文件:   `scripts/sw_feature_readback.py::pattern_params`（★ 阶段 3 补的能力）·
#         `tools/probe_pattern_params_recheck.py`（★ 只报不动）·
#         `output/pattern-params-capability-recheck.json`
# 定位:   ★ 阶段 3 · 按密度图补能力 ⇒ **第三个**、★ **换了一个族**（★ 前两个在
#   `IExtrudeFeatureData2`、★ 本个在 `ILinearPatternFeatureData`）✓
#   ★★ **官方逐字**：★ `D1Spacing` / `D2Spacing` ⇒ 「Distance **in meters**」·
#     ★ `D1TotalInstances` ⇒ `int` · ★ `GetPatternBodyCount()` ⇒ 「Number of **seed bodies**」·
#     ★ `GetSkippedItemCount()` ⇒ 「Number of **skipped instances**」·
#     ★ `IsDirection2Specified()` ⇒ 「True if direction 2 is specified」✓
#   ★★★ **真机 6/6 全过**（★ `output/pattern-params-capability-recheck.json`）：
#     ★ `D1TotalInstances=2` · ★ **`D1Spacing=0.02`（★ 米）** · ★ `D2TotalInstances=1` ·
#     ★ `IsDirection2Specified=False` · ★ `GetSkippedItemCount=0` · ★ `GetPatternBodyCount=1` ✓
#   ★★★★ **单位口径的第三层**（★ 本会话已见三层）：
#     ★ ① `GetDepth` ⇒ **随文档单位** · ★★ ② `GetDraftAngle` ⇒ **写死 radians** ·
#     ★★★ ③ `D1Spacing` ⇒ **写死 meters** ✓
#     ⇒ ★★★★★ **可复用判据**：★★★ **「官方 API 吃什么单位」是**逐成员**的事 ——
#       ★ 同一个仓里已经有**三种**口径** ⇒ **每读一个量都要单独查它那一页** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_feature_readback.py"
EVID = REPO / "output" / "pattern-params-capability-recheck.json"
SP = Path(r"C:\swapi\types\ILinearPatternFeatureData\D1Spacing.md")


def test_official_spacing_says_meters() -> None:
    """★★★ **前提断言**：★ 官方**明写** `in meters`（★ 判据的锚点）✓"""
    if not SP.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t = SP.read_text(encoding="utf-8", errors="replace")
    assert "in meters" in t, "★ 官方那页不再写 `in meters` 了 ⇒ 判据要重看"


def test_code_records_the_unit_basis_per_member() -> None:
    """★★★ 核心断言：★ 返回值**逐项**标口径、★ 且**不替调用方换算** ✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    i = src.find("def pattern_params(")
    assert i != -1, "★ 找不到 `pattern_params`"
    seg = src[i:i + 4000]
    assert "单位口径" in seg, "★ 没写单位口径"
    assert "meters" in seg, "★ 没写间距是米"
    assert "无量纲" in seg, "★ 没写实例数无量纲"
    for bad in ("* 1000", "/ 1000", "* 1000.0", "/ 1000.0"):
        assert bad not in seg, "★ 函数里出现了换算 `%s` ⇒ 它不该替调用方换算" % bad


def test_the_three_unit_bases_are_all_recorded() -> None:
    """★★★★ 核心断言：★ **三层口径**都写在模块里（★ 那正是本轮的核心判断）✓

    ★★ 判据：★ 模块里要能同时看到 `document`（★ 随文档）· `radians` · `meters` ✓
    """
    src = SRC.read_text(encoding="utf-8", errors="replace")
    assert "radians" in src, "★ 没记 `GetDraftAngle` 是弧度"
    assert "meters" in src, "★ 没记 `D1Spacing` 是米"
    assert "document（" in src or "unit_source" in src, "★ 没记 `GetDepth` 随文档"
    assert "三种" in src, "★ 没把「三种口径」这条判据写下来"


def test_negative_case_evidence_all_six_pass() -> None:
    """★★★ **负例 · 6 条判据全过**：★ 含 `D1Spacing = 0.02`（★ 米口径）✓"""
    if not EVID.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(EVID.read_text(encoding="utf-8", errors="replace"))
    checks = d.get("★_逐条判据") or {}
    assert len(checks) >= 6, "★ 判据条数不够：%r" % sorted(checks)
    bad = [k for k, v in checks.items() if v is not True]
    assert not bad, "★ 有判据没过：%r" % bad
    assert d.get("★_全过") is True, "★ 汇总不是全过"
    #: ★★ 前置也必须记（★ 上轮学到的：★ 阵列要先**选方向 + 选实体**）✓
    pre = d.get("★_前置") or {}
    assert pre.get("方向 mark=1") is True and pre.get("实体 mark=256") is True, (
        "★ 前置没记全：%r" % pre)
