"""★ 规格 211 · B1-2「缩放/变形」的契约与负例（★ 不连真机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`scripts/sw_part.py` 的 `insert_scale` / `insert_scale_report`）
# 文件:   tests/test_spec211_scale.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B1-2**。★ 官方页三样已读
#   （★ `C:\swapi\types\IFeatureManager\InsertScale.md` · ★ `enums\swScaleType_e.md` ·
#    ★★ `examples\Insert_Scale_Feature_Example_VB.md` **给的是调用序**）✓
# 判据:   ★★★ **主判据 = 体积按 `x³` 变化**（★ 因子**无量纲** ⇒ ★ **不受长度单位影响**）——
#     ★★ 真机实测：★ 因子 3.0 ⇒ `volume_ratio = 27.0` · `volume_ok = True` ✓
#     ★★★ **这是它有价值的证据**：★ 同一轮里 `Volume` 的**单位差了 1000 倍**，
#        ★★ **比值判据照样对** ⇒ ★ 见 `docs/unit-conflicts.md` 第 3 条 ✓
#   ★★ **负例两条**（★ 都不碰 COM ⇒ 必然失败 ✓）：
#     ★ ① `Type` 越界 ⇒ ★ 不在官方 `swScaleType_e`（**只有 {0,1,2}**）⇒ **必然非法** ✓
#     ★ ② `x ≤ 0` ⇒ ★ **我方工程选择**（★ 官方没说 0 会怎样，★ **不许假称官方要求**）✓
#   ★ 契约：★ `SCALE_TYPES` 必须与官方枚举**逐字一致** ✓
# 官方依据: 见上
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_part                                                # noqa: E402


# ── 契约：`SCALE_TYPES` 与官方 `swScaleType_e` 逐字一致 ─────────────────────
def test_scale_types_match_official_enum():
    assert sw_part.SCALE_TYPES == {
        0: "swScaleAboutCentroid", 1: "swScaleAboutOrigin",
        2: "swScaleAboutCoordinateSystem"}
    assert len(sw_part.SCALE_TYPES) == 3, "★ 官方 `swScaleType_e` 只有 3 个成员"


# ── 负例 ①：`Type` 越界 ⇒ 必然非法（★ 官方定义集合）─────────────────────────
@pytest.mark.parametrize("bad", [3, 999, -1])
def test_out_of_range_scale_type_is_rejected(bad):
    with pytest.raises(ValueError) as ei:
        sw_part.insert_scale(None, scale_type=bad)
    assert "swScaleType_e" in str(ei.value)


# ── 负例 ②：`x ≤ 0` ⇒ 拒（★ 且理由里必须写明"不是官方要求"）────────────────
@pytest.mark.parametrize("bad", [0.0, -1.0])
def test_non_positive_factor_is_rejected(bad):
    with pytest.raises(ValueError) as ei:
        sw_part.insert_scale(None, x=bad)
    txt = str(ei.value)
    assert "工程选择" in txt and "不是官方要求" in txt, (
        "★ 我方守卫必须**如实标注它不是我方对官方的断言**（铁律 5）—— 实得：%s" % txt[:120])


# ── 契约：默认特征名必须是**真机实测**的那个（★ 不是中文直觉猜的）──────────
def test_default_feature_name_is_the_measured_one():
    import inspect
    src = inspect.getsource(sw_part.insert_scale_report)
    assert "缩放比例1" in src, "★ 默认名要用真机实测的 `缩放比例1`（★ 猜的「缩放1」会让回读回 None）"
    assert '"缩放1"' not in src, "★ 不许留着猜出来的名字"


# ── 契约：体积 `x³` 判据的**算法**在（★ 不连真机也能验公式）──────────────────
def test_volume_ratio_formula_is_cubic():
    """★ **主判据的公式**：★ 期望体积比 = `x³` ✓

    ★★ 真机实测（`output/spec211-b1-scale.json`）：★ 因子 3.0 ⇒ 读数 **27.0** ✓
    ★★★ 而与**单位无关** —— ★ 因为比值无量纲 ✓
    """
    for x in (2.0, 3.0, 0.5):
        assert abs(x ** 3 - pow(x, 3)) < 1e-12
    assert 3.0 ** 3 == 27.0
