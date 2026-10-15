"""★ EC07 T06 判据 —— **交叉检查**（★ 机械侧与控制侧**都要有交代**）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/automation.py`（★ `CrossCheckKind` · `CrossCheck`）
#         `specs/309-ec07-automation-slice/spec.md`（★ EC07-T06）
# 定位:   ★ EC07 **T06**（★ 逐字：★「★ 机械**行程止挡**、**制动/保持**、**能量释放**、
#         ★ **维护模式**与控制需求**交叉检查**」）。
# 官方依据: 不适用（本仓的自动化设计层）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰 COM · ★ **不下发 PLC**）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from engineering import automation as A


def test_t06_four_cross_check_kinds_exist():
    """★★★ T06：★ **四类必须齐**（★ 逐字承 EC07-T06）。"""
    assert set(A.CrossCheckKind.ALL) == {
        "stroke_stop", "brake_hold", "energy_release", "maintenance_mode"}, (
        "★ 四类不齐：%r" % (A.CrossCheckKind.ALL,))


def test_t06_all_four_sides_satisfied_passes():
    """★★ T06：★ **四类两侧都有 ⇒ 通过**。"""
    c = A.CrossCheck()
    for k in A.CrossCheckKind.ALL:
        c.add(k, mechanical="★ 机械侧有交代", control="★ 控制侧有交代")
    out = c.verdict()
    assert out["ok"] is True, "★ 四类齐且两侧都有却判失败：%r" % out
    assert out["checked"] == 4


def test_t06_missing_kind_is_reported():
    """★★★ T06：★ **缺一类 ⇒ 报出来**（★ 且**点名**）。"""
    c = A.CrossCheck()
    for k in A.CrossCheckKind.ALL[:-1]:
        c.add(k, mechanical="★ 机械", control="★ 控制")
    out = c.verdict()
    assert out["ok"] is False
    assert out["missing_kinds"] == [A.CrossCheckKind.MAINTENANCE_MODE], (
        "★ 没点名缺哪类：%r" % out["missing_kinds"])


def test_t06_one_sided_is_not_a_cross_check():
    """★★★★★ T06：★ **只写了一侧 ⇒ 不算交叉检查**（★ 那是「交叉」二字的**全部意义**）。

    ★★ 判据：★ 机械侧写了、★ 控制侧**空** ⇒ ★ **不通过**（★ 且点名）。
    """
    c = A.CrossCheck()
    for k in A.CrossCheckKind.ALL:
        c.add(k, mechanical="★ 机械侧写了", control="★ 控制侧写了")
    #: ★★ **把「能量释放」的控制侧抹掉**（★ 只写了机械侧）
    c.items[A.CrossCheckKind.ENERGY_RELEASE]["control"] = ""
    out = c.verdict()
    assert out["ok"] is False, (
        "★★★ 只写了机械侧却判通过 ⇒ ★ 那不是「交叉检查」")
    assert out["one_sided"] == [A.CrossCheckKind.ENERGY_RELEASE], (
        "★ 没点名哪一项只写了一侧：%r" % out["one_sided"])
    assert "只写了一侧" in out["reason"]


def test_t06_whitespace_only_side_is_treated_as_empty():
    """★★ T06：★ **只有空白 ⇒ 算空**（★ 不能靠空格蒙混）。"""
    c = A.CrossCheck()
    for k in A.CrossCheckKind.ALL:
        c.add(k, mechanical="★ 机械", control="★ 控制")
    c.items[A.CrossCheckKind.STROKE_STOP]["mechanical"] = "   "
    assert c.verdict()["ok"] is False, "★★ 空白被当成了有内容"
