"""★ `tools/compare_geometry.py` 的**绝对 mm 判据**的契约测试（objective④ 的收尾）。

## 一、为什么要有它（★ 与相对判据的分工）
```
★ `compare_geometry(a, b, rel_tol)` 是**相对**判据（拓扑全等 + |ΔV|/|ΔA| ≤ 1%）——
   ★★ **它对"位置错了"完全瞎**：★ 整体平移时**所有相对量都不变**。
★ 而同一文件里还有三个**绝对 mm** 判据（`check_axis_alignment` / `check_radii` / `check_same_level`）
   ⇒ ★★ **它们才判"位置/尺寸对不对"**（★ 逐轴、逐值、逐端点，单位 mm）✓
⇒ ★ 两条**互补**：★ 定位用绝对、等价用相对（★ 只留一条会各瞎一半）—— ★ 本文件验**绝对**那一条。
```

## 二、★★★ 本文件的判据哲学（★ 与 `compare_geometry` 自己一致）
```
★★ **"读不到" ≠ "验过了"** —— ★ 三个判据对**空输入**一律回 `ok=False`
   （`check_radii` 的原话：「★ 读不到就不算验过」）⇒ ★ 本测试**专门有一条**验它。
★★ **每条判据都要有负例**（★ 事实 62：一个门禁"写了"不等于"有效"，负例是唯一的证明）⇒
   ★ 本文件对**每条判据**都有「超容差必被报出」的用例，★ **而且验 `reasons` 非空**（★ 不只验 `ok=False`）。
★★ **边界值**：★ 三个函数用的都是 `<=` ⇒ ★ **恰好等于容差应判通过**（★ 那是易错处，★ 单列一条）。
★ **`axial` 的第三个条件是 `|dz| > tol`（"大于"）** —— ★ 一个**横躺的边**必须被判"不是轴"，
   ★★ 那是最容易漏的一条（★ 单列一条）。
```

"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_compare_geometry_absolute.py
# 定位:   objective④：给**绝对 mm 判据**补契约测试（相对判据已真机 PASS，绝对的那条此前无测试）。
# 官方依据: 不适用（★ 被测对象是本地工具；其判据来源在 `tools/compare_geometry.py` 的来源块里）。
# 许可:   本仓库 MIT。被测判据的来源 `native_features.py` 标注为 MIT（见该文件内注）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "tools"))

import compare_geometry as CG  # noqa: E402


# ── ① 默认容差：题述的 0.05 / 0.1 mm ─────────────────────────────────
def test_default_tolerances_are_the_documented_millimetre_values():
    """★ 默认容差要是**绝对 mm**（定位 0.05 / 半径 0.1）—— ★ 那是 objective④ 的题述值。"""
    assert CG.ABS_TOL_MM == pytest.approx(0.05), CG.ABS_TOL_MM
    assert CG.RADIUS_TOL_MM == pytest.approx(0.1), CG.RADIUS_TOL_MM
    #: ★ 用默认值调一次，确认默认真的传下去了
    assert CG.check_axis_alignment((0.0, 0.0, 50.0))["tol_mm"] == pytest.approx(CG.ABS_TOL_MM)
    assert CG.check_radii([5.0], 5.0)["tol_mm"] == pytest.approx(CG.RADIUS_TOL_MM)


# ── ② check_axis_alignment ───────────────────────────────────────────
def test_axis_alignment_axial_accepts_a_true_axis():
    """★ `axial`：横向两轴在容差内 **且** 轴向长出一截 ⇒ 通过。"""
    r = CG.check_axis_alignment((0.01, -0.02, 50.0), "axial")
    assert r["ok"] is True, r
    assert r["reasons"] == [], r


def test_axis_alignment_axial_rejects_a_lying_edge():
    """★★★ **`axial` 的第三条件是 `|dz| > tol`（"大于"）** —— 一个**横躺的边**必须被判"不是轴"。

    ★ 这条最容易漏：★ 只判"横向两轴在容差内"会把**任何横躺的边**都当成轴对齐。
    """
    r = CG.check_axis_alignment((0.0, 0.0, 0.01), "axial")     #: ★ dz 很小 ⇒ 它不是轴
    assert r["ok"] is False, r
    assert r["reasons"], "★ 必须给理由（不能只回 ok=False）"


def test_axis_alignment_axial_rejects_lateral_drift():
    """★ 横向超容差 ⇒ 必须报出。"""
    r = CG.check_axis_alignment((0.5, 0.0, 50.0), "axial")
    assert r["ok"] is False and r["reasons"], r


def test_axis_alignment_planar_only_cares_about_dz():
    """★ `planar`：只看 `|dz| ≤ tol`（★ 横向多少都不管 —— ★ 一个平的面可以在任意位置）。"""
    assert CG.check_axis_alignment((999.0, -999.0, 0.01), "planar")["ok"] is True
    assert CG.check_axis_alignment((0.0, 0.0, 0.2), "planar")["ok"] is False


def test_axis_alignment_boundary_is_inclusive():
    """★ 边界：**恰好等于**容差 ⇒ 通过（★ 三个函数用的都是 `<=`）。"""
    assert CG.check_axis_alignment((CG.ABS_TOL_MM, CG.ABS_TOL_MM, 50.0), "axial")["ok"] is True


def test_axis_alignment_rejects_bad_input_without_raising():
    """★ 类型/长度错 ⇒ `ok=False` + 理由，★ **不抛**（★ 判据不能把调用方炸掉）。"""
    r = CG.check_axis_alignment("not-three-numbers")           # type: ignore[arg-type]
    assert r["ok"] is False and r["reasons"], r


# ── ③ check_radii ────────────────────────────────────────────────────
def test_radii_accepts_all_within_tolerance():
    assert CG.check_radii([5.0, 5.05, 4.95], 5.0)["ok"] is True


def test_radii_rejects_one_bad_value_and_says_how_many():
    """★ 逐值：★ **一个不等就不过** —— ★ 且理由里要写**几个超了**。"""
    r = CG.check_radii([5.0, 5.0, 9.0], 5.0)
    assert r["ok"] is False, r
    assert r["reasons"] and "1/3" in r["reasons"][0], r
    assert r["max_dev"] == pytest.approx(4.0, abs=1e-9), r


def test_radii_empty_is_a_failure_not_a_pass():
    """★★★ **"读不到就不算验过"** —— 空输入必须 `ok=False`（★ 那是本判据的哲学）。"""
    r = CG.check_radii([], 5.0)
    assert r["ok"] is False, r
    assert r["reasons"], r


# ── ④ check_same_level ───────────────────────────────────────────────
def test_same_level_accepts_both_endpoints_on_the_level():
    assert CG.check_same_level([(0.0, 0.0), (0.02, -0.03)], 0.0)["ok"] is True


def test_same_level_rejects_when_either_endpoint_drifts():
    """★ **每对的两个端点都要落在 level 上** —— ★ 只查第一个端点就会漏。"""
    r = CG.check_same_level([(0.0, 0.0), (0.0, 1.5)], 0.0)
    assert r["ok"] is False and r["reasons"], r
    #: ★ 反向：只有**第一个**端点偏 ⇒ 同样要报（★ 证明它两个端点都查）
    r2 = CG.check_same_level([(1.5, 0.0)], 0.0)
    assert r2["ok"] is False and r2["reasons"], r2


def test_same_level_empty_is_a_failure():
    assert CG.check_same_level([], 0.0)["ok"] is False


# ── ⑤ 与**相对**判据的分工（★ 用一条真实会瞎的场景说明）───────────────
def test_relative_criteria_are_blind_to_translation_but_absolute_is_not():
    """★★ **本文件存在的理由**：★ 整体平移时**零件内部的相对量全不变** ⇒
    ★ 相对判据对"位置错了"完全瞎；★ 而绝对判据**抓得到**。

    ★ 构造（★ 第一版我写错了 ⇒ 这里记下正确形态）：
      · **相对量** = ★ **同一个零件内部**的量（★ 这里用「各点到首点的间距」当代表；
        ★ 真实里就是体积 / 面积 / 拓扑全等）—— ★ **平移前后完全一样**；
      · **绝对量** = ★ 它与**某个基准 level** 的关系 —— ★ **平移后就变了**。
    ⚠ 我第一版拿「零件 A 与零件 B 的逐点差」当"相对量" ⇒ ★ **那当然会变**（★ 那是绝对关系）。
      ⇒ ★ **定则：说"相对判据瞎"时，要拿**零件自己内部**的量举例，★ 不能拿两件之间的关系当"相对量"。**
    """
    #: ★ 同一个零件（一串 z），原样 与 整体抬高 5 mm
    part_z = [0.0, 0.0, 0.0]          #: ★ **都在 z=0** —— 这才是"同层"（★ 上面那版我拿了 0 和 20，那本就不同层）
    shifted_z = [z + 5.0 for z in part_z]

    #: ① **相对量**：★ 零件**内部**各点到首点的间距 —— ★ 平移前后必须完全一样
    def internal_gaps(zs):
        return [round(z - zs[0], 9) for z in zs]

    assert internal_gaps(part_z) == internal_gaps(shifted_z), \
        "★ 零件内部的相对量在平移下不该变（★ 相对判据看不见平移 ⇒ 它对位置错完全瞎）"
    assert internal_gaps(part_z) == [0.0, 0.0, 0.0], internal_gaps(part_z)

    #: ② **绝对量**：★ 端点与 level=0 的关系 —— ★ 平移后必须被抓到
    pairs = [(z, z) for z in part_z]
    assert CG.check_same_level(pairs, 0.0)["ok"] is True, "★ 原位都落在 level=0 上"
    shifted_pairs = [(z, z) for z in shifted_z]
    assert CG.check_same_level(shifted_pairs, 0.0)["ok"] is False, \
        "★ 整体抬高 5 mm 必须被绝对判据抓到（★ 而上面 ① 证明了相对量对此无感）"
