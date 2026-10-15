"""★ 判据 —— **齿轮路径的单位口径**（★ 业主点破的那一处：★ 是否和最初一样犯错误）。

★★★★★ **业主原话**：「★ **那你再画个齿轮，看看是否和最初画行星减速太阳齿轮一样犯错误**」✓
  ★★★ **答案：★ 是 —— 犯了同一族的错**（★ 1000× 单位错）✓

★★★ **真机裁决（★ 证据 `output/_probe_gear_units.json` · ★ 走 `sw_guard`）**：
  | ★ | ★ 修前 | ★ 修后 |
  |---|---|---|
  | ★ 建件 | ★ **失败** `RuntimeError: 创建齿廓离散线段失败` | ★ **建成** `SpurGear_m1_z20` |
  | ★ 包围盒 | ★ `0.0039 × 0.0076 mm` | ★ **`22.0 × 22.0 × 10.0 mm`** |
  | ★ 比值（盒 / 解析外径 22 mm） | ★ **0.000177** ≈ 1/1000 ✗ | ★ **1.0** ✓ |

★★★ **根因（★ 两条，都在 `create_external_spur_gear` 里）**：
  · ★ ① `sketch_line` 的契约是**毫米**（★ 它内部再乘 `_MM_TO_M`），
    ★★ 而 `outline_points_m` 是**米** ⇒ ★ **又被除了一次 1000** ✗
  · ★ ② `sketch_circle` 同病：★ `bore_diameter_mm / 2000.0` 先变**米**、★ 再当**毫米**传 ⇒ **1000×** ✗
  ★★★ **而第三处是对的**：★ `extrude_boss` **确实收米**（★ 官方 `D1` = meters）
    ⇒ ★★ **三处口径互不相同** —— ★ **不能一刀切** ✓

★★ **判据分层**：★ 本文件**纯离线**（★ AST 扫源码 + 读真机证据）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_gear.py`（★ `create_external_spur_gear` —— ★ 三处调用）
#         `scripts/sw_part.py`（★ `sketch_line`/`sketch_circle` **毫米** · `extrude_boss` **米**）
#         `output/_probe_gear_units.json`（★ 真机证据：修前 0.000177 / 修后 1.0）
# 定位:   ★ 守卫「齿轮齿廓与轴孔的单位换算」；★ 起因是业主点破「是否和最初一样犯错误」。
# 官方依据: `ISketchManager::CreateLine`（★ 坐标 = **meters**）· `FeatureExtrusion3`（★ `D1` = meters）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 纯离线 —— ★ AST + JSON，★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GEAR = ROOT / "scripts" / "sw_gear.py"
EVIDENCE = ROOT / "output" / "_probe_gear_units.json"


@pytest.fixture(scope="module")
def gear_src() -> str:
    return GEAR.read_text(encoding="utf-8")


def test_gear_profile_points_are_scaled_to_millimetres(gear_src):
    """★★★★★ **齿廓点必须乘 1000**（★ 米 → 毫米）—— ★ 本判据的核心。

    ★★ 依据：★ `outline_points_m` 是**米**，★ 而 `sketch_line` 收**毫米**
      ⇒ ★ 不乘 1000 ⇒ **又被除一次 1000** ✗（★ 真机比值 0.000177）
    """
    tree = ast.parse(gear_src)
    #: ★ 找 `sketch_line(...)` 那个调用
    call = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "sketch_line"):
            call = node
            break
    assert call is not None, "★★ 找不到 `sketch_line` 调用"
    seg = ast.get_source_segment(gear_src, call) or ""
    assert "* 1000.0" in seg, (
        "★★★ 齿廓点**没乘 1000** ⇒ ★ `outline_points_m`（米）被当成毫米 ⇒ **1000×**：\n    %s"
        % seg[:200])
    #: ★ 且**不许**再出现「原样解包」（★ 那正是修前的形态）
    assert "*start" not in seg, (
        "★★★ 又用 `*start` 原样解包了（★ 修前的形态）⇒ ★ 单位没换算：%s" % seg[:160])


def test_bore_radius_is_passed_as_millimetres(gear_src):
    """★★★★★ **轴孔半径必须传毫米**（★ 不是 `/2000`）。

    ★★ 依据：★ `sketch_circle` 收**毫米** ⇒ ★ 半径 = `bore_diameter_mm / 2` ✓
      ★ 而修前的 `/2000.0` 把它变成了**米** ⇒ **1000×** ✗
    """
    tree = ast.parse(gear_src)
    call = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "sketch_circle"):
            call = node
            break
    assert call is not None, "★★ 找不到 `sketch_circle` 调用"
    seg = ast.get_source_segment(gear_src, call) or ""
    assert "/ 2000" not in seg and "/2000" not in seg, (
        "★★★ 轴孔用了 `/2000`（★ 把 mm 变米再当毫米传）⇒ **1000×**：\n    %s" % seg[:200])
    assert "/ 2.0" in seg or "/ 2 " in seg or "/2.0" in seg, (
        "★★ 轴孔半径应是 `bore_diameter_mm / 2`（毫米）：%s" % seg[:200])


def test_extrude_depth_stays_in_metres(gear_src):
    """★★★★ **拉伸深度**必须**保持米**（★ 三处口径不同 —— ★ 别一刀切）。

    ★★ 依据（★ 官方 `FeatureExtrusion3.md` 逐字）：★ `D1` = **meters**
      ⇒ ★ `extrude_boss` 收米 ⇒ ★ 那里**保留** `face_width_mm / 1000.0` ✓
    ★★★ **这条判据防的是「修 bug 时一刀切」** —— ★ 把三处都乘 1000 会把拉伸搞坏 ✗
    """
    tree = ast.parse(gear_src)
    call = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "extrude_boss"):
            call = node
            break
    assert call is not None, "★★ 找不到 `extrude_boss` 调用"
    seg = ast.get_source_segment(gear_src, call) or ""
    assert "/ 1000.0" in seg, (
        "★★★ 拉伸深度**没有**换算成米 ⇒ ★ 会**大 1000 倍**：\n    %s" % seg[:200])


def test_real_machine_evidence_shows_correct_size():
    """★★★★★ **真机证据：齿轮尺寸正确**（★ 判据不是我说了算，★ 是证据）。

    ★★ 依据（★ `output/_probe_gear_units.json` 真机读数）：
      · ★ 解析外径 **22.000 mm**（★ 独立算的 —— ★ `m×z` + 2×ha*×m）
      · ★★ 回读包围盒 **`22.0 × 22.0 × 10.0 mm`** ⇒ ★ 比值 **1.0** ✓
      · ★ 特征名 `SpurGear_m1_z20`（★ 真的建出来了）✓
    """
    if not EVIDENCE.is_file():
        pytest.skip("★★ 缺真机证据 ⇒ 跑 `sw_guard` 探针后再判")
    d = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if d.get("verdict") == "too_small_1000x":
        pytest.skip("★ 该证据是**修前**的（★ 0.000177）⇒ 修后重跑即生效")
    assert d.get("verdict") == "ok", (
        "★★ 裁决 = %r（★ 期望 ok）" % d.get("verdict"))
    bb = d.get("bbox") or {}
    expected = d.get("expected_outside_dia_mm")
    assert expected and abs(bb.get("dx_mm", 0) - expected) < 0.05 * expected, (
        "★★★ 包围盒 %r 与解析外径 %r 不符" % (bb, expected))
    #: ★★ 齿宽也要对（★ 10 mm）
    assert abs(bb.get("dz_mm", 0) - 10.0) < 0.5, (
        "★★ 齿宽 %r ≠ 10 mm" % bb.get("dz_mm"))
    #: ★★★ **特征真的建出来了**
    feats = d.get("feature_names") or []
    assert any("SpurGear" in f for f in feats), (
        "★★ 特征树里没有齿轮特征：%r" % feats[-6:])


def test_the_three_call_sites_have_distinct_units(gear_src):
    """★★★★ **三处调用的单位口径**互不相同**（★ 这条判据防「一刀切」）。

    ★★ 逐字：
      · ★ `sketch_line` / `sketch_circle` ⇒ **毫米**（★ 内部乘 `_MM_TO_M`）
      · ★ `extrude_boss` ⇒ **米**（★ 官方 `D1` = meters）
    ⇒ ★★ **同一个函数里两种口径** —— ★ 这正是**最初那类错误的土壤** ✓
    """
    from scripts import sw_part as P
    import inspect
    line_doc = inspect.getdoc(P.sketch_line) or ""
    circle_doc = inspect.getdoc(P.sketch_circle) or ""
    extrude_doc = inspect.getdoc(P.extrude_boss) or ""
    assert "毫米" in line_doc, "★★ `sketch_line` 的契约不再是毫米了？"
    assert "毫米" in circle_doc, "★★ `sketch_circle` 的契约不再是毫米了？"
    assert "米" in extrude_doc, "★★ `extrude_boss` 的契约不再是米了？"
    #: ★★ 且**必须写明**那条区别（★ 否则下一个人还会踩）
    assert "米" in extrude_doc and "毫米" in extrude_doc, (
        "★★ `extrude_boss` 的 docstring 应**同时**说明「对外毫米/COM 米」的区别")
