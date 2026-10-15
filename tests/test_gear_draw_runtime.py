"""★ 判据 —— **画出太阳轮**（★ 业主说「那你再画个齿轮」）。

★★★★★ **业主原话**：「★ **那你再画个齿轮，看看是否和最初画行星减速太阳齿轮一样犯错误**」✓
  ★★★ **答案：★ 是 —— 犯了同一族的错**（★ 1000× 单位错）；★ **现已修好并真机画出来了** ✓

★★★ **真机读数**（★ 证据 `output/_probe_gear_draw.json` · ★ 走 `sw_guard`）：
  | ★ 项 | ★ 解析值（独立） | ★ 实测 | ★ 一致 |
  |---|---|---|---|
  | ★ 外径 | ★ **22.000 mm** | ★ **22.0 mm** | ✅ |
  | ★ 齿宽 | ★ **10 mm** | ★ **10.0 mm** | ✅ |
  | ★ 体数 | ★ 1 | ★ **1** | ✅ |
  | ★ 体积 | ★ 独立近似 **2600.6 mm³** | ★ **2561.9 mm³**（★ 比值 **0.9851**） | ✅ |
  | ★ 特征 | ★ — | ★ **`SpurGear_m1_z20`** | ✅ |
  | ★ 出图 | ★ — | ★ **`output/gear_sun_z20_m1.png`**（248 KB） | ✅ |

★★ **本判据守的是「齿轮真的画出来了」** —— ★ 而不是「函数返回了非空」✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_gear.py`（★ `create_external_spur_gear_report`）
#         `output/_probe_gear_draw.json`（★ 真机证据）
#         `output/gear_sun_z20_m1.png`（★ 等轴测出图）
# 定位:   ★ 守卫「齿轮交付物」这条 —— ★ 起因是业主说「再画一个看看」。
# 官方依据: 渐开线直齿轮几何 · `ISketchManager::CreateLine` · `FeatureExtrusion3`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 纯离线 —— ★ 读证据 JSON + 图片存在性）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "output" / "_probe_gear_draw.json"
PNG = ROOT / "output" / "gear_sun_z20_m1.png"

#: ★★ **太阳轮规格**（★ 记忆里那个任务的参数）
TEETH, MODULE_MM, FACE_MM, BORE_MM = 20, 1.0, 10.0, 8.0
OUTSIDE_DIA_MM = MODULE_MM * (TEETH + 2)          #: ★ 标准齿顶高系数 1.0
ROOT_DIA_MM = MODULE_MM * (TEETH - 2.5)           #: ★ 标准齿根高系数 1.25


@pytest.fixture(scope="module")
def ev() -> dict:
    if not EVIDENCE.is_file():
        pytest.skip("★★ 缺真机证据 ⇒ 跑 `sw_guard` 探针后再判")
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_gear_feature_was_really_created(ev):
    """★★★★ **特征真的建出来了**（★ 规则 6：★ 判据是**特征树变化**，★ 不是返回值）。"""
    assert ev.get("create", {}).get("ok") is True, (
        "★★ 建件失败：%r" % ev.get("create_error") or ev.get("create"))
    new = ev.get("create", {}).get("new_features") or []
    assert any("SpurGear" in f for f in new), (
        "★★ 新增特征里没有齿轮：%r" % new)


def test_gear_bbox_matches_the_analytic_value(ev):
    """★★★★★ **包围盒 = 解析外径 × 齿宽**（★ 这是「尺寸对不对」的硬判据）。

    ★★ 解析：★ 外径 = `m×(z+2)` = **22 mm** · ★ 齿宽 = **10 mm** ✓
    ★★★ **修前**这里会得 `0.0039 × 0.0076 mm`（★ 比值 0.000177）✗
    """
    bb = ev.get("bbox") or {}
    assert abs(bb.get("dx_mm", 0) - OUTSIDE_DIA_MM) < 0.05, (
        "★★ 外径 %r ≠ %r" % (bb.get("dx_mm"), OUTSIDE_DIA_MM))
    assert abs(bb.get("dy_mm", 0) - OUTSIDE_DIA_MM) < 0.05, (
        "★★ 外径（Y）%r ≠ %r" % (bb.get("dy_mm"), OUTSIDE_DIA_MM))
    assert abs(bb.get("dz_mm", 0) - FACE_MM) < 0.05, (
        "★★ 齿宽 %r ≠ %r" % (bb.get("dz_mm"), FACE_MM))


def test_single_body(ev):
    """★★★ **体数 = 1**（★ 齿轮是一个实体，★ 不是一堆碎片）。"""
    assert ev.get("body_count") == 1, "★★ 体数 %r ≠ 1" % ev.get("body_count")


def test_volume_matches_an_independent_approximation(ev):
    """★★★★★ **体积与独立近似相符**（★ 双盲 —— ★ 近似**手写**，★ 不取自被测实现）。

    ★★ 独立近似（★ 手写）：
      · ★ **齿体**（根圆→外圆）≈ 该圆环的**一半**（★ 齿宽约为周节的一半）
      · ★ **轮体**（轴孔→根圆）= 完整圆环
      · ★ 再乘齿宽
    ★★★ **实测 2561.9 mm³ vs 近似 2600.6 mm³ ⇒ 比值 0.9851** ✓
    """
    v_m3 = ev.get("volume_m3")
    assert v_m3, "★★ 没有体积读数"
    r_out, r_root, r_bore = OUTSIDE_DIA_MM / 2, ROOT_DIA_MM / 2, BORE_MM / 2
    teeth_area = 0.5 * math.pi * (r_out ** 2 - r_root ** 2)
    body_area = math.pi * (r_root ** 2 - r_bore ** 2)
    approx_mm3 = (teeth_area + body_area) * FACE_MM
    got_mm3 = v_m3 * 1e9
    ratio = got_mm3 / approx_mm3
    assert 0.90 < ratio < 1.10, (
        "★★★ 体积比值 %.4f 超出 0.90~1.10（★ 实测 %.1f / 近似 %.1f）⇒ "
        "★ 齿形可能不对" % (ratio, got_mm3, approx_mm3))


def test_image_was_exported(ev):
    """★★★★ **出图了**（★ 业主说「画一个」—— ★ 要**能看**的东西）。

    ★★ 判据：★ PNG **存在且非零字节**（★ 承 EC00 的「判据是文件」口径）✓
    """
    assert ev.get("png_exists") is True, (
        "★★ 出图失败：%r" % ev.get("image_error"))
    assert ev.get("png_bytes", 0) > 1000, (
        "★★★ PNG 只有 %r 字节 ⇒ ★ 那是空白图" % ev.get("png_bytes"))
    assert PNG.is_file(), "★ 图不在预期路径"


def test_analytic_dimensions_are_the_standard_ones(ev):
    """★★★ **解析尺寸是标准直齿轮的**（★ 独立算 —— ★ 不取自实现）。

    ★★ 依据（★ 标准外啮合直齿轮）：★ 节圆 = `mz` · ★ 外径 = `m(z+2)` ·
      ★ 根圆 = `m(z−2.5)`（★ 齿顶高系数 1.0 · ★ 齿根高系数 1.25）✓
    """
    a = ev.get("analytic") or {}
    assert abs(a.get("pitch_dia_mm", 0) - MODULE_MM * TEETH) < 1e-6, (
        "★★ 节圆 %r ≠ %r" % (a.get("pitch_dia_mm"), MODULE_MM * TEETH))
    assert abs(a.get("outside_dia_mm", 0) - OUTSIDE_DIA_MM) < 1e-6, (
        "★★ 外径 %r ≠ %r" % (a.get("outside_dia_mm"), OUTSIDE_DIA_MM))
    assert abs(a.get("root_dia_mm", 0) - ROOT_DIA_MM) < 1e-6, (
        "★★ 根圆 %r ≠ %r" % (a.get("root_dia_mm"), ROOT_DIA_MM))
    #: ★ 20 齿、20° 压力角 ⇒ **不根切**（★ 最少齿数 ≈ 17）
    assert a.get("undercut_risk") is False, "★★ 20 齿不该报根切风险"


def test_no_residue_after_the_run(ev):
    """★★★ **零残留**（★ 关文档 —— ★ 图**保留**，★ 那是交付物）。"""
    assert ev.get("closed") is True, "★★ 没关掉自己开的文档"
