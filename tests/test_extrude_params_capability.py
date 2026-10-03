"""★ 测 `extrude_params`：★ 逐成员对官方 `## Returns`、★ 且**两条期望值我改对过**（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IExtrudeFeatureData2\`）
# 文件:   `scripts/sw_feature_readback.py::extrude_params`（★ 阶段 3 补的能力）·
#         `tools/probe_extrude_params_recheck.py`（★ 只报不动）·
#         `output/extrude-params-capability-recheck.json`
# 定位:   ★ 阶段 3 · 按密度图补能力（★ `查 × 特征` 那一格）⇒ **第二个** ✓
#   ★★ **官方逐字**（★ `output/_read_extrude_members.py` 的逐条读数）：
#     · `GetEndCondition(bool)` ⇒ 回 **`swEndConditions_e`**（★ 盲拉 = 0）✓
#     · **`GetDraftAngle(bool)`** ⇒ 「Draft angle of the extrusion **in radians**」⇒
#       ★★ **官方**明写弧度**** ⇒ ★ 与 `GetDepth` 的"随文档单位"**相反** ✓
#     · `GetContoursCount()` ⇒ 「Number of **selected** contours」✓
#     · `ReverseDirection` / `BothDirections` ⇒ ★ **属性** ✓
#     · `GetFace` ⇒ **废弃**（★ 不用）· `GetDirectionReference` ⇒ **带 out**（★ 不碰）✓
#   ★★★ **真机 7/7 全过**（★ `output/extrude-params-capability-recheck.json`）：
#     ★ 端条件 0 · ★ 正向深度 20.0 · ★ 反向深度 0.0 · ★ 拔模角 0.0 · ★ 轮廓数 0 ·
#     ★ `ReverseDirection=True` · ★ `BothDirections=False` ✓
#   ★★★★ **⚠ 而其中两条是我**先写错、再改对**的**（★ 值记）：
#     ★ ① 我期望 `GetContoursCount == 1` ⇒ **实测 0** —— 真因：★ **官方说的是
#          "**selected** contours"**、★ 而本仓 `extrude_boss` 用的是**整个草图** ✓
#     ★ ② 我期望 `ReverseDirection == False` ⇒ **实测 True** —— 真因：★ **本仓
#          `extrude_boss(..., direction=True)` 传的正是"反向"** ✓
#     ⇒ ★★★★★ **可复用判据**：★★★ **"读回来的值与期望不符"时，
#       先核**期望值是从哪来的**** —— 我两次都是**凭"默认值"想当然**** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_feature_readback.py"
EVID = REPO / "output" / "extrude-params-capability-recheck.json"
DRAFT = Path(r"C:\swapi\types\IExtrudeFeatureData2\GetDraftAngle.md")
CONTOURS = Path(r"C:\swapi\types\IExtrudeFeatureData2\GetContoursCount.md")


def test_official_draft_angle_is_radians() -> None:
    """★★★ **前提断言**：★ 官方**明写** `in radians`（★ 判据的锚点）✓"""
    if not DRAFT.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t = DRAFT.read_text(encoding="utf-8", errors="replace")
    assert "in radians" in t, "★ 官方那页不再写 `in radians` 了 ⇒ 判据要重看"


def test_official_contours_count_says_selected() -> None:
    """★★★ **前提断言**：★ 官方说的是 **selected** contours（★ 那是我第一条错的根据）✓"""
    if not CONTOURS.is_file():
        return
    t = CONTOURS.read_text(encoding="utf-8", errors="replace")
    assert "selected contours" in t, "★ 官方措辞变了 ⇒ 判据要重看"


def test_code_records_the_per_member_unit_basis() -> None:
    """★★★ 核心断言：★ 返回值必须**逐成员**写口径、★ 而不是一个全局口径 ✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    i = src.find("def extrude_params(")
    assert i != -1, "★ 找不到 `extrude_params`"
    seg = src[i:i + 4000]
    assert "单位口径" in seg, "★ 没写单位口径"
    assert "radians" in seg, "★ 没写 `GetDraftAngle` 是弧度"
    assert "document" in seg, "★ 没写 `GetDepth` 随文档单位"


def test_negative_case_evidence_all_seven_pass() -> None:
    """★★★ **负例 · 判据必须**改对之后**才算过****：★ 证据里 7 条全 `True` ✓

    ★★ 若哪天有人把期望值改回"想当然"的默认值 ⇒ ★ **本测试会红** ✓
    """
    if not EVID.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(EVID.read_text(encoding="utf-8", errors="replace"))
    checks = d.get("★_逐条判据") or {}
    assert len(checks) >= 7, "★ 判据条数不够：%r" % sorted(checks)
    bad = [k for k, v in checks.items() if v is not True]
    assert not bad, "★ 有判据没过：%r" % bad
    assert d.get("★_全过") is True, "★ 汇总不是全过"
