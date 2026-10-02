"""@brief 契约测试：`scripts/sw_chamfer_geometry.py` 的两个解析公式与那条"三件一起"的判据。

★ **不连 COM**（★ 纯几何 + 判据逻辑）。
★★ 判据的**期望值**不是我们量的，而是**解析公式**给的 —— ★ 本测试用**独立算出的数**去校它
   （★ 不重复调用被测函数来"自证"）。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_sw_chamfer_geometry.py
# 定位:   24h 计划 段 5「修地基 **D4**」的验收：★ 解析公式正确 + 判据有判别力。
# 官方依据: 不适用（几何推导；公式来源见 `scripts/sw_chamfer_geometry.py` 的来源块，MIT）。
# 许可:   本仓库 MIT。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from sw_chamfer_geometry import (                                    # noqa: E402
    chamfer_volume_report,
    circular_rim_chamfer_volume_mm3,
    straight_chamfer_volume_mm3,
)


def test_straight_chamfer_volume_matches_hand_computed_value():
    """★ 直边：`0.5·w²·L` —— 用**手算数**校（不信被测函数自己）。"""
    #: 手算：w=1、L=10 ⇒ 0.5·1·1·10 = 5.0
    assert straight_chamfer_volume_mm3(10.0, 1.0) == 5.0
    #: 手算：w=2、L=30 ⇒ 0.5·4·30 = 60.0
    assert straight_chamfer_volume_mm3(30.0, 2.0) == 60.0


def test_circular_rim_matches_the_upstream_reference_number():
    """★★ 圆孔缘：★ 四家判据里写着「~**2.29 mm³**」（工件 Ø5.5 ⇒ r=2.75 · w=0.5）。

    ⇒ ★ 本测试**独立复算**这个数（★ 圆台 − 圆柱，不用被测函数的表达式）。
    """
    r, w = 2.75, 0.5
    #: 独立复算：圆台 π/3·h·(R²+Rr+r²) − 圆柱 π·r²·w
    frustum = math.pi / 3.0 * w * ((r + w) ** 2 + (r + w) * r + r * r)
    cylinder = math.pi * r * r * w
    independent = frustum - cylinder
    got = circular_rim_chamfer_volume_mm3(r, w)
    assert abs(got - independent) < 1e-9, (got, independent)
    #: ★ 与那份判据写的 ~2.29 对上（两位小数）
    assert round(got, 2) == 2.29, got


def test_circular_rim_is_positive_and_monotonic_in_width():
    """★ 边界：w>0 ⇒ 体积为正；且 w 越大切得越多（★ 单调）。"""
    assert circular_rim_chamfer_volume_mm3(2.75, 0.1) > 0
    a = circular_rim_chamfer_volume_mm3(2.75, 0.5)
    b = circular_rim_chamfer_volume_mm3(2.75, 1.0)
    assert b > a > 0


def test_report_rejects_a_silent_no_op():
    """★★ 负例①：★ **零体积变化** ⇒ `ok=False`（★ 那是"静默空操作"）。"""
    r = chamfer_volume_report("straight", 1000.0, 1000.0, expected_removed_mm3=60.0)
    assert r["decreased"] is False and r["ok"] is False


def test_report_rejects_the_wrong_geometry_with_a_nonzero_delta():
    """★★★ 负例②（★ 那份判据点名的**更糟**那种）：★ **体积变了，但不是该变的量** ⇒ `ok=False`。

    ★ 那份判据的原文警告：★ **非零体积差比零体积更糟** —— 因为它**看起来对了**。
    """
    #: 期望切 60（直边 w=2、L=30），而实测只切了 2.29（★ 那是做在圆孔缘上的量）
    r = chamfer_volume_report("straight", 1000.0, 997.71, expected_removed_mm3=60.0)
    assert r["decreased"] is True, "体积确实降了"
    assert r["matches_formula"] is False, "但降的量不是该降的"
    assert r["ok"] is False, "★ 非零差 + 错几何 ⇒ 必须判失败"


def test_report_accepts_the_correct_case():
    """★ 正例：★ 降了且量对得上 ⇒ `ok=True`。"""
    r = chamfer_volume_report("straight", 1000.0, 940.0, expected_removed_mm3=60.0)
    assert r["ok"] is True and r["rel_error"] == 0.0
