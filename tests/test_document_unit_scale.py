"""★ 测 `_document_length_unit_scale`：★ 倍数必须**按文档单位**推、★ 不硬编码 1000（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方枚举（`swLengthUnit_e`）
# 文件:   `scripts/sw_document_data.py::_document_length_unit_scale`
# 定位:   ★★★★ 2026-10-04（接手轮）**真机定案的一个真 bug** ——
#   · ★ 上一轮真机跑 A4 证据时**顺带量到**：★ `before_mm.current = **20000.0**`，
#     而那个尺寸的本意是 **20 mm** ✓
#   · ★★ **定案（两个独立证据交叉）**：★ ① `GetUnits() = [**0**, …]` ⇒ `swLengthUnit_e = 0 = swMM`；
#     ★ `GetSystemValue3` 原始回 `(20.0,)`。★ ② `extrude_boss(model,"Sketch1",20.0)` 建出的实体
#     `size = [100, 60, **20**]` ⇒ **真的是 20 mm** ✓
#   · ★★★ **⇒ `Get/SetSystemValue3` 吃的就是**文档单位**，★ 而旧代码硬编码 `×/÷ 1000`（★ 假定是米）** ✓
#   · ★★★★ **真机修后**：★ `before_mm.current` **20000.0 → 20.0** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import sw_document_data as D                                              # noqa: E402


class _FakeModel:
    """★ 假的文档：★ 只实现 `GetUnits()`（★ 那正是换算要读的东西）✓"""

    def __init__(self, units) -> None:
        self._units = units

    def GetUnits(self):                                                   # noqa: N802
        return self._units


def test_mm_document_scale_is_one() -> None:
    """★★★ 核心断言：★ `swLengthUnit_e = 0`（`swMM`）⇒ 倍数 **1.0**（★ 不是 1000）✓

    ★★ **这一条就是那个真 bug 的判据**：★ 旧代码在毫米文档上回 1000.0 ⇒
      ★ 一个 20 mm 的尺寸被读成 **20000** ✓
    """
    assert D._document_length_unit_scale(_FakeModel([0, 1, 8, 2, 0])) == 1.0


def test_meter_document_scale_is_1000() -> None:
    """★ `swLengthUnit_e = 2`（`swM`）⇒ 倍数 **1000.0**（★ 旧行为对**米**文档是对的）✓"""
    assert D._document_length_unit_scale(_FakeModel([2, 1, 8, 2, 0])) == 1000.0


def test_inch_document_scale_is_25_4() -> None:
    """★ `swLengthUnit_e = 3`（`swINCHES`）⇒ 倍数 **25.4** ✓"""
    assert D._document_length_unit_scale(_FakeModel([3, 1, 8, 2, 0])) == 25.4


def test_negative_case_falls_back_to_1000() -> None:
    """★★ **负例**：★ 读不到单位（★ `GetUnits` 抛 / 回 `None`）⇒ **回退旧行为 1000.0** ✓

    ★ 而这**不是静默成功** —— ★ 它是**明确的向下兼容**；★ 调用方要更准的口径就得给 `model` ✓
    """

    class _NoUnits:
        def GetUnits(self):                                               # noqa: N802
            raise AttributeError("假文档没有 GetUnits")

    assert D._document_length_unit_scale(_NoUnits()) == 1000.0
    assert D._document_length_unit_scale(_FakeModel(None)) == 1000.0


def test_no_hardcoded_thousand_in_module() -> None:
    """★★★ 核心断言：★ 模块里**不再有**硬编码的 `/ 1000.0` 或 `* 1000.0`（★ 那正是病灶）✓"""
    src = (REPO / "scripts" / "sw_document_data.py").read_text(encoding="utf-8", errors="replace")
    assert "/ 1000.0" not in src, "★ 还有硬编码的 `/ 1000.0` ⇒ 米制假设又回来了"
    assert "* 1000.0" not in src, "★ 还有硬编码的 `* 1000.0` ⇒ 米制假设又回来了"
