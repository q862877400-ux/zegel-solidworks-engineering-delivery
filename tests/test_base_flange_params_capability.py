"""★ 测 `base_flange_params`：★ 判据、★ **第七族单位口径**、★ 不读已废弃成员（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IBaseFlangeFeatureData\`）
# 文件:   `scripts/sw_feature_readback.py::base_flange_params`（★ 阶段 3 补的能力 · 第八个）·
#         `tools/probe_base_flange_params_recheck.py`（★ 只报不动）·
#         `output/base-flange-params-capability-recheck.json`
# 定位:   ★ 阶段 3 · 按密度图补能力 ⇒ **第八个**、★ **第七个族**、★ **钣金域** ✓
#   ★★ **官方逐字**：★ `Thickness` ⇒ 「Value for thickness」· ★ `BendRadius` ⇒
#     「Value of the bend radius」· ★ `TableRadius` ⇒ 「Bend radius」· ★ `TableThickness` ⇒
#     「Thickness」· ★ `ReliefWidth` / ★ `ReliefDepth` ⇒ 光名字 ⇒
#     ★★★ **七个长度量**都没写单位**** ✓
#     ★ `KFactor` / ★ `TableKFactor` / ★ `ReliefRatio` ⇒ **无量纲比例** ·
#     ★ `ReliefType` ⇒ `swSheetMetalReliefTypes_e` · ★ `D1EndConditionType` ⇒ `swFlangeOffsetTypes_e` ✓
#     ★★★★ **`D1OffsetDistance` ⇒ **真废弃****（★ 新判据也认）⇒ **不读** ✓
#   ★★★ **真机 8/8 全过**（★ `output/base-flange-params-capability-recheck.json`）：
#     ★ 特征 **`基体-法兰1`** · ★ `Thickness = **0.002**` · ★ `BendRadius = **0.001**` ·
#     ★ `KFactor = **0.42**` · ★ `ReliefType = 1` · ★ `ReliefRatio = **0.5**` ·
#     ★ `ReliefWidth = **0.001**` ✓
#   ★★★★ **单位口径的第七族**：★ 官方 `## Returns` **没写单位**、★ 而**本仓的
#     `BaseFlangeSpec` docstring 逐字写着「全部长度单位为米」** ⇒
#     ★★ **实测一致**（★ 传 `0.002` ⇒ 回 `0.002`）⇒ ★★★ **⇒ 本族的**实测口径 = 米**** ✓
#     ★★★★ **⇒ 而那条判据的来源很干净**：★ **我从仓里读出了 spec 的 docstring**、
#       ★ 而**不是猜** ⇒ ★ **"判据现成"是搜出来的** ✓
#   ★★★★★ **⚠ 而三个表值 `TableKFactor`/`TableRadius`/`TableThickness` 都是 `0.0`** ⇒
#     ★ **应然的**（★ 没用 gauge table）⇒ ★★ **它们与 `UseGaugeTable` **互相印证**** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _funcbody import func_source  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_feature_readback.py"
SPEC = REPO / "scripts" / "sw_sheet_metal.py"
EVID = REPO / "output" / "base-flange-params-capability-recheck.json"


def test_spec_docstring_still_says_meters() -> None:
    """★★★ **前提断言**：★ `BaseFlangeSpec` 的 docstring **仍写「全部长度单位为米」** ✓

    ★★ **为什么**：★ 本轮的单位判定**就是靠这句**（★ 传 `0.002` ⇒ 回 `0.002`）⇒
      ★★★ **若哪天 spec 改成毫米，本测试会红** ⇒ **那时该重测** ✓
    """
    t = SPEC.read_text(encoding="utf-8", errors="replace")
    i = t.find("class BaseFlangeSpec")
    assert i != -1, "★ 找不到 `BaseFlangeSpec`"
    seg = t[i:i + 400]
    assert "米" in seg, "★ spec 的 docstring 不再写「米」了：%r" % seg[:200]


def test_code_does_not_read_the_obsolete_member() -> None:
    """★★★ 核心断言：★ 函数体里**不读 `D1OffsetDistance`**（★ 官方标真废弃）✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    i = src.find("def base_flange_params(")
    assert i != -1, "★ 找不到 `base_flange_params`"
    #: ★★★★ 2026-10-04（轮 113）**改用 `ast` 取那一个函数**（★ 事实 51）——
    #:   ★ **真因**：★ `src[i:].split('"""')[-1]` **看着像"函数体"**、
    #:     ★★ **而它实际是"从那个 `def` 到**文件末尾**"** ⇒
    #:     ★★★ **文件末尾后来多了一个函数 ⇒ 范围**悄悄变宽**、判据**误报**** ✓
    #:   ★★★★ **⇒ 用 `tests/_funcbody.py::func_source`**（★ 按 `ast` 的 `end_lineno`）✓
    body = func_source(src, "base_flange_params")
    assert 'get_com_member(fd, "D1OffsetDistance"' not in body, (
        "★ 函数体里读了 `D1OffsetDistance`（★ 官方标真废弃）")
    #: ★★ 而那份"不读"的清单**必须在**（★ 那是记录）✓
    assert "不读" in body, "★ 那份「不读」清单不见了"


def test_code_uses_the_two_layer_filter() -> None:
    """★★★ 核心断言：★ 兜底过**两层**（★ 名字 + ★ `BaseFlange` 类型名）✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    i = src.find("def base_flange_params(")
    seg = src[i:i + 4600]
    assert "_CONTAINER_NODES" in seg, "★ 兜底没过名字那一层"
    assert "BaseFlange" in seg, "★ 兜底没过类型名那一层"


def test_negative_case_the_unit_basis_and_self_consistent_tables() -> None:
    """★★★★ **负例 · 口径 + 自洽都要记**：★ `0.002 ⇒ 0.002` + ★ 三个表值 `0.0` ✓

    ★★ **判据逐字**：★ 传 `BaseFlangeSpec(thickness=0.002)` ⇒
      ★ `Thickness = 0.002`（★ **同口径 ⇒ 米**）·
      ★★ **而 `TableKFactor` / `TableRadius` / `TableThickness` 全是 `0.0`** ⇒
        ★★★ **应然的**（★ 没用 gauge table）⇒ **与 `UseGaugeTable` 互相印证** ✓
    """
    if not EVID.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(EVID.read_text(encoding="utf-8", errors="replace"))
    checks = d.get("★_逐条判据") or {}
    assert len(checks) >= 8, "★ 判据条数不够：%r" % sorted(checks)
    bad = [k for k, v in checks.items() if v is not True]
    assert not bad, "★ 有判据没过：%r" % bad
    r = d.get("读取") or {}
    assert str(r.get("Thickness")) == "0.002", "★ 厚度不是 0.002 ⇒ 口径变了：%r" % r.get("Thickness")
    assert str(r.get("BendRadius")) == "0.001", "★ 折弯半径不是 0.001：%r" % r.get("BendRadius")
    for k in ("TableKFactor", "TableRadius", "TableThickness"):
        assert str(r.get(k)) == "0.0", "★ `%s` 不是 0.0 ⇒ 是不是用了 gauge table？%r" % (k, r.get(k))
    assert "米" in str(d.get("★_单位判定")), "★ 单位判定没写「米」：%r" % d.get("★_单位判定")
