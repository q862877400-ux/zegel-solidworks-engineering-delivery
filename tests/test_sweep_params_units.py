"""★ 测「`sweep_params` 的两条口径记录」+ 「空 Dispatch 那条判据」（★ 含负例 · 轮 127）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `C:\\swapi\\types\\ISweepFeatureData\\*.md` +
#         真机证据 `output/sweep-units-capability-recheck.json`
# 文件:   tests/test_sweep_params_units.py（★ 新）
# 定位:   ★★★★★★ 2026-10-04（轮 127）**量出了第十一族**：
#     ★ `CircularProfileDiameter` 的口径 = **随文档单位（毫米）** ✓
#     **怎么量的**（★ 关键是**判据独立**）：
#       ★ 设 `CircularProfile=True` + `CircularProfileDiameter=12.0` ⇒ `ModifyDefinition` ⇒
#       ★★ **量**包围盒**（★ 几何 ≠ 那个属性）**：★ `bbox_before=[6,6,40]` ⇒ `after=[**12,12**,40]` ✓
#     ★★ **⚠ 而那次成功卡在**第 3 参**上**：★ 传 `None` ⇒
#       `com_error(-2147352571, '**类型不匹配。**', None, **3**)` ⇒
#       ★★★ **正解**：★ 传 `create_empty_dispatch_variant()`（★ **事实 12/33**）✓
#   ★★★ **⚠ 而 `GetWallThickness` **仍未定案****（★ 官方：valid only if `IsThinFeature`)⇒
#     ★ **如实标**、★ **不谎称** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# -----------------------------------------------------------------────────────────

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
sys.path.insert(0, str(TESTS))
from _funcbody import func_source  # noqa: E402

SRC = REPO / "scripts" / "sw_feature_readback.py"
PROBE = REPO / "tools" / "probe_sweep_units_recheck.py"


def test_the_measured_unit_is_recorded_as_a_conclusion() -> None:
    """★★★ 核心断言：★ 那条**已量出**的口径写成了**结论**（★ 不是"待办"）✓"""
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "sweep_params")
    assert "第十一族" in body, "★ 没记下那是第几族"
    assert "随文档单位" in body, "★ 口径的**结论**没写"
    #: ★★ 而**几何判据**那两步也要在（★ 那是"怎么量的"）✓
    assert "bbox_before" in body or "6.0, 6.0" in body, "★ 没记下**几何**那一步"
    assert "12000" in body, "★ 没记下**对照组**（★ 若口径是米会是 12000）"


def test_the_still_unmeasured_one_is_marked_as_open() -> None:
    """★★★★ 核心断言：★ **没量到的那个**仍标"未定案"（★ 不谎称）✓

    ★★ **为什么**：★ `GetWallThickness` 官方说 **valid only if `IsThinFeature` is true** ⇒
      ★★★ **本会话没建过薄壁扫描** ⇒ ★ **如实留作待办** ✓
    """
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "sweep_params")
    assert "GetWallThickness" in body and "仍未定案" in body, (
        "★ `GetWallThickness` 要如实标「仍未定案」")


def test_negative_case_the_probe_uses_the_empty_dispatch_variant() -> None:
    """★★★★ 核心断言：★ 探针那第 3 参用的是 **`create_empty_dispatch_variant()`** ✓

    ★★ **为什么**：★ 传裸 `None` ⇒
      `com_error(-2147352571, '**类型不匹配。**', None, **3**)` ⇒
      ★★★ **而那个错误**看不出是哪个参数****（★ **事实 12/33**）⇒
      ★ **所以要用本仓那个帮手、★ 并把这条判据钉住** ✓
    """
    t = PROBE.read_text(encoding="utf-8", errors="replace")
    assert "create_empty_dispatch_variant()" in t, "★ 没走那条正解"
    #: ★★ 而**裸 `None`** 那个形态**不许**再出现在 `ModifyDefinition` 那一句里 ✓
    code = "\n".join(l for l in t.splitlines() if not l.strip().startswith("#"))
    assert 'ModifyDefinition", data, model,\n' in code or \
        'ModifyDefinition", data, model, ' in code, "★ 调用形态变了"
    assert '"ModifyDefinition", data, model, None' not in code, (
        "★ 第 3 参又传裸 `None` 了 ⇒ 会报「类型不匹配」（★ 看不出是哪个参数）")


def test_negative_case_the_independent_criterion_is_recorded() -> None:
    """★★★★ **负例 · 判据**独立**这件事要写明**（★ 那是本轮最值钱的一条）✓

    ★★ **为什么**：★ "写 `12.0` 再读回 `12.0`" 是**循环自证** ⇒
      ★★★ **⇒ 必须用**几何**（★ 包围盒）⇒ ★ **那条理由要留在代码里** ✓
    """
    t = PROBE.read_text(encoding="utf-8", errors="replace")
    assert "循环自证" in t or "独立" in t, "★ 没写明「为什么用几何」"
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "sweep_params")
    assert "独立" in body, "★ `sweep_params` 的 docstring 里没写明判据要独立"
