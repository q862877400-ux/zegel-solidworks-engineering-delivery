"""★ 契约测试：选型计算（★ 齿轮 / 轴承寿命 / 弹簧 / V 带）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_selection_calc.py
# 定位:   规格 `specs/336-selection-calc` 的契约测试。
#           ★★ 触发它的是 2026-10-14 全自动挖掘的**收口盘点**：
#             `tools/closure_inventory.py` 判「24 个 .ps1 校核脚本」是唯一
#             还剩的**值得做**项。
# 官方依据: `mech-design/知识库/70-标准件与选型计算/校核脚本/*.ps1`
#           （★ 自述来源 EngineersEdge ANSI B6.1 / ISO 281 等公开标准）
# 许可:   本仓库 MIT。★ 公式是公开标准公式 ⇒ ★ 自建实现，未抄第三方代码。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import math
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import selection_calc as S                    # noqa: E402


#: ══ ★★ 齿轮（★ 逐条对 ANSI B6.1 公式）═══════════════════════════════

def test_gear_geometry_matches_formulas() -> None:
    """★★ **逐条对公式**（★ `m=3 · z=20`）。

    ★★ 判据（★ 逐字承该脚本）：
      `d=m·z` · `da=m(z+2)` · `df=m(z-2.5)` · `h=2.25m` · `db=d·cosα`
    """
    g = S.spur_gear(module_mm=3, z1=20)
    assert g["d1_mm"] == 60.0
    assert g["da1_mm"] == 66.0            #: ★ 3×(20+2)
    assert g["df1_mm"] == 52.5            #: ★ 3×(20-2.5)
    assert g["h_mm"] == 6.75              #: ★ 2.25×3
    assert abs(g["db1_mm"] - 60.0 * math.cos(math.radians(20))) < 1e-9


def test_gear_pitch_is_pi_m() -> None:
    """★ 齿距 `p = πm`（★ `m=3` ⇒ `3π ≈ 9.4248`）。"""
    g = S.spur_gear(module_mm=3, z1=20)
    assert abs(g["p_mm"] - math.pi * 3) < 1e-9


def test_gear_center_distance_crosscheck() -> None:
    """★★★ **交叉验算**（★ 该脚本的核心手法）：
    `a = m(z1+z2)/2` **应等于** `(d1+d2)/2`。

    ★★ 判据：★ **两个独立公式给同一个数** ⇒ ★ 才叫验过。
    """
    g = S.spur_gear(module_mm=3, z1=20, z2=40)
    assert g["center_distance_mm"] == 90.0
    assert g["center_crosscheck_mm"] == 90.0
    assert g["center_crosscheck_ok"] is True


def test_gear_ratio() -> None:
    """★ 传动比 `i = z2/z1`（★ 40/20 = 2）。"""
    assert S.spur_gear(module_mm=3, z1=20, z2=40)["ratio"] == 2.0


def test_gear_rejects_bad_input() -> None:
    """★ 模数 ≤ 0 或齿数 < 1 ⇒ 报错（★ 不静默算）。"""
    with pytest.raises(S.CalcError):
        S.spur_gear(module_mm=0, z1=20)
    with pytest.raises(S.CalcError):
        S.spur_gear(module_mm=3, z1=0)


#: ══ ★★ 轴承寿命（★ ISO 281）══════════════════════════════════════════

def test_bearing_life_formula() -> None:
    """★★ **`L10 = (C/P)^ε × 10⁶ 转`**（★ `ε=3` 球 · `10/3` 滚子）。

    ★★ 判据（★ 逐字承 `design_rules.yaml`）。
    """
    b = S.bearing_life(c_kn=10, p_kn=5, rpm=1000, kind="ball")
    assert b["l10_mrev"] == 8.0            #: ★ (10/5)^3 = 8
    assert b["epsilon"] == 3.0


def test_bearing_life_roller_exponent() -> None:
    """★ **滚子用 `ε=10/3`**（★ 不是 3）—— ★ 与球不同。"""
    b = S.bearing_life(c_kn=10, p_kn=5, rpm=1000, kind="roller")
    assert abs(b["epsilon"] - 10 / 3) < 1e-9
    assert abs(b["l10_mrev"] - 2 ** (10 / 3)) < 1e-9


def test_bearing_life_hours() -> None:
    """★ 小时数 `L10h = 10⁶ × L10 / (60 × n)`。"""
    b = S.bearing_life(c_kn=10, p_kn=5, rpm=1000)
    assert abs(b["l10h"] - 8.0 * 1e6 / (60 * 1000)) < 1e-6


def test_bearing_required_c_roundtrip() -> None:
    """★★★ **反解与正算闭环**：由寿命反解的 C ⇒ 正算应回同一个寿命。

    ★★ 判据（★ 逐字承 `design_rules.yaml` 的 `selection_steps`）：
      「**由寿命要求反算所需基本额定动载荷 C**」。
    """
    target = 20000.0
    r = S.required_c(p_kn=5.0, target_hours=target, rpm=1500)
    back = S.bearing_life(c_kn=r["required_c_kn"], p_kn=5.0, rpm=1500)
    assert abs(back["l10h"] - target) < 1e-6, "★★ 反解不闭环"


def test_bearing_rejects_bad_input() -> None:
    """★ C/P/n ≤ 0 ⇒ 报错。"""
    with pytest.raises(S.CalcError):
        S.bearing_life(c_kn=0, p_kn=5, rpm=1000)
    with pytest.raises(S.CalcError):
        S.bearing_life(c_kn=10, p_kn=5, rpm=0)


def test_bearing_unknown_kind_raises() -> None:
    """★ `kind` 只有 `ball` / `roller`。"""
    with pytest.raises(S.CalcError):
        S.bearing_life(c_kn=10, p_kn=5, rpm=1000, kind="nope")


#: ══ ★★ 弹簧（★ Wahl 修正）═══════════════════════════════════════════

def test_spring_index_and_wahl() -> None:
    """★★ `C=D/d` · `Kw=(4C-1)/(4C-4)+0.615/C`（★ 该脚本自述
    「**Wahl 系数已与原表逐点核对**」）。
    """
    s = S.spring(wire_d_mm=2, mean_d_mm=20, active_coils=8)
    assert s["spring_index_c"] == 10.0
    expect = (4 * 10 - 1) / (4 * 10 - 4) + 0.615 / 10
    assert abs(s["wahl_kw"] - expect) < 1e-9


def test_spring_rate_formula() -> None:
    """★ 刚度 `k = G·d⁴/(8·D³·n)`。"""
    s = S.spring(wire_d_mm=2, mean_d_mm=20, active_coils=8)
    expect = 79000 * 2 ** 4 / (8 * 20 ** 3 * 8)
    assert abs(s["rate_n_per_mm"] - expect) < 1e-9


def test_spring_rejects_small_index() -> None:
    """★★ **旋绕比 C < 3 ⇒ 制造困难**（★ 报 `out-of-range`，★ 不是静默算）。

    ★ 判据：★ 常用旋绕比 4~16；★ `C<3` 时**弹簧卷不出来**。
    """
    with pytest.raises(S.CalcError) as ei:
        S.spring(wire_d_mm=10, mean_d_mm=20, active_coils=8)
    assert ei.value.code == "out-of-range"
    assert "制造困难" in ei.value.detail


def test_spring_stiffer_with_fewer_coils() -> None:
    """★ **圈数越少越硬**（★ `k ∝ 1/n`）—— ★ 物理上必须如此。"""
    a = S.spring(wire_d_mm=2, mean_d_mm=20, active_coils=4)
    b = S.spring(wire_d_mm=2, mean_d_mm=20, active_coils=8)
    assert a["rate_n_per_mm"] > b["rate_n_per_mm"]


#: ══ ★★ V 带 ═════════════════════════════════════════════════════════

def test_belt_speed_formula() -> None:
    """★ `v = π·d1·n / 60000`（★ m/s）。"""
    v = S.v_belt(d1_mm=100, d2_mm=200, rpm=1450, center_mm=400)
    assert abs(v["belt_speed_m_s"] - math.pi * 100 * 1450 / 60000) < 1e-9


def test_belt_length_two_algorithms_agree() -> None:
    """★★★ **带长双算法交叉验算**（★ 该脚本自述的手法）。

    ★★ 判据：★ **两个独立算法给的带长应几乎相同**（★ 差 < 1mm）。
    """
    v = S.v_belt(d1_mm=100, d2_mm=200, rpm=1450, center_mm=400)
    assert v["length_crosscheck_delta_mm"] < 1.0, (
        "★★ 两算法差 %.3f mm ⇒ 至少一个算错了" % v["length_crosscheck_delta_mm"])


def test_belt_ratio() -> None:
    """★ 传动比 `i = d2/d1`。"""
    assert S.v_belt(d1_mm=100, d2_mm=200, rpm=1450,
                    center_mm=400)["ratio"] == 2.0


def test_belt_rejects_bad_input() -> None:
    """★ 直径/转速/中心距 ≤ 0 ⇒ 报错。"""
    with pytest.raises(S.CalcError):
        S.v_belt(d1_mm=0, d2_mm=200, rpm=1450, center_mm=400)


#: ══ 元信息 ═══════════════════════════════════════════════════════════

def test_report_lists_five_calcs() -> None:
    """★ 五类计算都可查。"""
    r = S.report()
    for k in ("spur_gear", "bearing_life", "required_c", "spring", "v_belt"):
        assert k in r


def test_closure_inventory_exists() -> None:
    """★ 收口盘点文档在（★ 记录「还剩什么」）。"""
    p = (ROOT / "specs" / "332-known-facts-triage"
         / "closure-inventory.md")
    assert p.is_file()
    t = p.read_text(encoding="utf-8")
    for k in ("已扫完的", "还剩什么", "24 个 .ps1"):
        assert k in t, "★ 盘点文档缺 `%s`" % k
