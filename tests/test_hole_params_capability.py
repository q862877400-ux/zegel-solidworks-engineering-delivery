"""★ 测 `hole_params`：★ **官方没写单位**、★ 而**实测**出**接口内部就分裂**（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IWizardHoleFeatureData2\`）
# 文件:   `scripts/sw_feature_readback.py::hole_params`（★ 阶段 3 补的能力 · 第四个）·
#         `tools/probe_hole_params_recheck.py`（★ 只报不动）·
#         `output/hole-params-capability-recheck.json`
# 定位:   ★ 阶段 3 · 按密度图补能力 ⇒ **第四个**、★ **第三个族** ✓
#   ★★ **这一族的特点：★ 官方 `## Returns` **没写单位****（★ 逐个读都是「Hole diameter」这种光名字）⇒
#     ★★★ **铁律 5**：★ 查不到就写「查不到」、★ **不许按族推断** ✓
#   ★★★ **而真机测出来了**（★ `M8` 通孔 · ★ 板厚 20mm）：
#     ★ `ThruHoleDiameter = **0.008**` ⇒ **米** · ★ `ThruHoleDepth = **20.0**` ⇒ **毫米** ⇒
#     ★★★★ **⇒ **同一个接口里两个量的口径不同**** ✓
#   ★★★★ **单位口径的第五层**（★ 本会话已见五层）：
#     ★ ① `GetDepth` ⇒ 随文档 · ★② `GetDraftAngle` ⇒ radians · ★③ `D1Spacing` ⇒ meters ·
#     ★④ 本族 ⇒ 官方没写 · ★⑤ **本族内部**就分裂 ✓
#     ⇒ ★★★★★ **可复用判据**：★★★ **「同一个接口」也**不**保证同一口径** ——
#       ★ **每读一个量都要单独真机验** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_feature_readback.py"
EVID = REPO / "output" / "hole-params-capability-recheck.json"
THRU_D = Path(r"C:\swapi\types\IWizardHoleFeatureData2\ThruHoleDiameter.md")
THRU_DEPTH = Path(r"C:\swapi\types\IWizardHoleFeatureData2\ThruHoleDepth.md")


def test_official_pages_give_no_unit() -> None:
    """★★★ **前提断言**：★ 官方那两页**都没写单位**（★ 判据的锚点）✓"""
    for p in (THRU_D, THRU_DEPTH):
        if not p.is_file():
            continue                                                      # ★ 官方源不在本机 ⇒ 跳过
        t = p.read_text(encoding="utf-8", errors="replace")
        low = t.lower()
        for w in ("meters", "meter", "millimeters", "millimeter", "inches"):
            assert not __import__("re").search(r"\b%s\b" % w, low), (
                "★ 官方页 `%s` 现在写了单位 `%s` ⇒ 判据要重看" % (p.name, w))


def test_evidence_shows_the_split_within_one_interface() -> None:
    """★★★★ 核心断言：★ 证据里**同一接口的两个量口径不同** ✓

    ★★ 判据逐字：★ `ThruHoleDiameter` 判成**米**、★ 而 `ThruHoleDepth` 判成**毫米** ✓
    """
    if not EVID.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(EVID.read_text(encoding="utf-8", errors="replace"))
    per = d.get("★_逐量判定") or {}
    assert per, "★ 没记逐量判定：%r" % sorted(d)
    assert "米" in str(per.get("ThruHoleDiameter")), "★ 直径那条口径变了：%r" % per
    assert "毫米" in str(per.get("ThruHoleDepth")), "★ 深度那条口径变了：%r" % per


def test_code_records_both_the_official_silence_and_the_measured_values() -> None:
    """★★★ 核心断言：★ 返回值**保留「官方未写」**、★ docstring **记实测口径** ✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    i = src.find("def hole_params(")
    assert i != -1, "★ 找不到 `hole_params`"
    seg = src[i:i + 5200]
    assert "官方 ## Returns 未写" in seg, "★ 没保留「官方未写」这个事实"
    assert "0.008" in seg and "20.0" in seg, "★ 没写实测读数"
    assert "米" in seg and "毫米" in seg, "★ 没写两个量的口径"
    for bad in ("* 1000", "/ 1000", "* 1000.0", "/ 1000.0"):
        assert bad not in seg, "★ 函数里出现了换算 `%s` ⇒ 它不该替调用方换算" % bad


def test_negative_case_the_five_layers_are_recorded() -> None:
    """★★★★ **负例 · 五层口径要记全**：★ 模块里要能看到**五层**那条判据 ✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    assert "第五层" in src, "★ 没记「第五层」"
    assert "同一个接口" in src, "★ 没写「同一个接口也不保证同一口径」"
