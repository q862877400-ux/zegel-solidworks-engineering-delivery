"""★ 阶段 5 契约测试：平口钳（规格 320 的 H1~H4）。

★★ 含**反向验证**（★ 规格 §5 的 R1~R5）：
   R1 固定活动钳口 / R2 删去导向关系 / R3 导程误绑 / R4 删螺纹定义 / R5 仅体积通过
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_stage5_vise.py
# 定位:   规格 `specs/320-stage5-bench-vise` 的 H1~H4 契约测试
# 官方依据: ① 外部方案阶段 5 的验收 S5（逐字）
#           ② `scripts/engineering/assembly.py` 的 `DofVerdict.RELEASING`
#              —— ★★ 「预期运动」是允许的（★ 那正是活动钳口需要的）
#           ③ 本仓**事实 51**（判据要贴合组织单元）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import vise as V                                # noqa: E402
from scripts.engineering.assembly import DofVerdict                      # noqa: E402


def _model() -> V.ViseModel:
    return V.default_model()


def _good() -> dict:
    return V.evaluate_vise(_model(), turns=5.0, readback_mm=20.0, jaw_dof=1,
                           jaw_motions=["沿导向移动"])


#: ══ H1 共享接口 ══════════════════════════════════════════════════════

def test_interface_kinds_closed_set() -> None:
    """★ 接口种类就是四种（导向/螺杆/螺母/钳口）。"""
    assert len(V.INTERFACE_KINDS) == 4
    with pytest.raises(AssertionError):
        V.SharedInterface(name="x", kind="乱写的", value=1.0)


def test_default_model_has_all_interfaces() -> None:
    """★ 默认模型**接口齐**（★ 缺了 `require` 会抛）。"""
    m = _model()
    m.require(*V.DEFAULT_INTERFACES)
    assert len(m.interfaces) == len(V.DEFAULT_INTERFACES)


def test_missing_interface_raises() -> None:
    """★ 缺接口 ⇒ **抛**（★ 不静默）。"""
    m = V.ViseModel()
    with pytest.raises(V.ViseError) as ei:
        m.require("guide_width_mm")
    assert ei.value.code == "missing-interface"


def test_propagate_marks_dependents_only() -> None:
    """★★ FR-002：**依赖它的零件失效 · 不依赖的可复用**。"""
    r = V.propagate("screw_lead_mm", 4.0, 6.0)
    assert r["changed"] is True
    assert r["stale"] == ["螺母"], r
    #: ★ 「活动钳口」不依赖导程 ⇒ **可复用**
    assert "活动钳口" in r["reusable"], r


def test_propagate_no_change_is_noop() -> None:
    """★ 值没变 ⇒ **无传播**（★ 不是「全都标脏」）。"""
    r = V.propagate("screw_lead_mm", 4.0, 4.0)
    assert r["changed"] is False and r["stale"] == []


def test_propagate_guide_affects_jaw_and_base() -> None:
    """★ 导向间距变 ⇒ 活动钳口 + 底座都失效。"""
    r = V.propagate("guide_width_mm", 120.0, 140.0)
    assert set(r["stale"]) == {"活动钳口", "底座", "导轨"}


#: ══ H2 传动计算 ═════════════════════════════════════════════════════

def test_travel_is_independent_arithmetic() -> None:
    """★★ FR-003：位移 = **导程 × 圈数**（★ 纯算术，不碰 CAD）。"""
    tc = V.lead_to_travel(4.0, 5.0, readback_mm=20.0)
    assert tc.computed == 20.0
    assert tc.consistent is True


def test_travel_detects_mismatch() -> None:
    """★ 独立算与回读不一致 ⇒ `consistent=False`。"""
    tc = V.lead_to_travel(4.0, 5.0, readback_mm=100.0)
    assert tc.consistent is False
    assert tc.delta == 80.0


def test_travel_without_readback_is_inconsistent() -> None:
    """★ 没给回读 ⇒ `readback=0` ⇒ **必然不一致**（★ 如实报，不假装通过）。"""
    tc = V.lead_to_travel(4.0, 5.0)
    assert tc.consistent is False


def test_travel_tolerance_is_respected() -> None:
    """★ 容差内的差 ⇒ 算一致。"""
    tc = V.lead_to_travel(4.0, 5.0, readback_mm=20.005, tolerance_mm=0.01)
    assert tc.consistent is True
    tc2 = V.lead_to_travel(4.0, 5.0, readback_mm=20.5, tolerance_mm=0.01)
    assert tc2.consistent is False


#: ══ H3 活动钳口自由度 ═══════════════════════════════════════════════

def test_jaw_fixed_fails() -> None:
    """★★ FR-004 / R1：**被固定 ⇒ 失败**（★ 功能没了）。"""
    jf = V.check_jaw_free(dof=1, motions=["移动"], is_fixed=True)
    v = jf.verdict()
    assert v["verdict"] == "jaw-fixed" and v["releasing"] is False


def test_jaw_zero_dof_fails() -> None:
    """★ 自由度为 0 ⇒ 同「被固定」（★ 功能没了）。"""
    v = V.check_jaw_free(dof=0, motions=["移动"]).verdict()
    assert v["verdict"] == "jaw-fixed" and v["releasing"] is False


def test_jaw_without_annotation_is_under_constrained() -> None:
    """★ FR-005：有自由度但**没标注** ⇒ `under_constrained`。"""
    v = V.check_jaw_free(dof=1, motions=[]).verdict()
    assert v["verdict"] == "under_constrained" and v["releasing"] is False


def test_jaw_with_annotation_is_expected_motion() -> None:
    """★★ 正例：有自由度且已标注 ⇒ `expected_motion`（★ **允许**）。"""
    v = V.check_jaw_free(dof=1, motions=["沿导向移动"]).verdict()
    assert v["verdict"] == "expected_motion" and v["releasing"] is True
    #: ★ 与既有 `DofVerdict.RELEASING` 一致
    assert DofVerdict.EXPECTED_MOTION in DofVerdict.RELEASING


#: ══ H4 螺纹工程定义 ═════════════════════════════════════════════════

def test_default_thread_is_complete() -> None:
    """★ 默认螺纹定义**完整** ⇒ `PASS`。"""
    v = V.default_thread().verdict()
    assert v["verdict"] == "PASS" and v["releasing"] is True
    assert "Tr20" in v["spec"]


def test_incomplete_thread_is_indeterminate() -> None:
    """★★ FR-007：螺纹定义缺项 ⇒ **`INDETERMINATE`**（★ 缺依据不得算通过）。"""
    v = V.ThreadSpec().verdict()
    assert v["verdict"] == "INDETERMINATE" and v["releasing"] is False
    assert set(v["missing"]) == {"standard", "designation", "pitch_mm",
                                 "tolerance_class", "material"}


def test_partial_thread_lists_exact_missing() -> None:
    """★ 缺哪几项要**具名**（★ 便于定位）。"""
    th = V.ThreadSpec(standard="GB/T 5796", designation="Tr20", pitch_mm=4.0)
    v = th.verdict()
    assert v["verdict"] == "INDETERMINATE"
    assert set(v["missing"]) == {"tolerance_class", "material"}


#: ══ S5 整体 ═════════════════════════════════════════════════════════

def test_evaluate_vise_good() -> None:
    """★ 正例：五项都过。"""
    r = _good()
    assert r["ok"] is True, r
    assert r["interfaces_ok"] is True
    assert r["thread"]["releasing"] is True
    assert r["travel"]["consistent"] is True
    assert r["jaw"]["releasing"] is True
    assert r["indeterminate"] == []


def test_geometry_pass_is_not_function_pass() -> None:
    """★★ FR-009：**几何通过 ≠ 功能通过**。

    ★ 判据：把钳口固定（几何照样"成功"）⇒ `ok` **必须为 False**。
    """
    r = V.evaluate_vise(_model(), turns=5.0, readback_mm=20.0,
                        jaw_dof=1, jaw_motions=["移动"], jaw_fixed=True)
    assert r["ok"] is False
    assert r["jaw"]["verdict"] == "jaw-fixed"


#: ══ ★★ 反向验证 R1~R5 ═══════════════════════════════════════════════

def test_r1_fixing_the_jaw_must_fail() -> None:
    """★★ **R1**：**固定活动钳口** ⇒ 相关功能检查必须**失败**。"""
    good = _good()
    bad = V.evaluate_vise(_model(), turns=5.0, readback_mm=20.0,
                          jaw_dof=1, jaw_motions=["移动"], jaw_fixed=True)
    assert good["ok"] is True and bad["ok"] is False
    assert bad["jaw"]["verdict"] == "jaw-fixed"


def test_r2_removing_guide_relation_must_fail() -> None:
    """★★ **R2**：**删去导向关系** ⇒ 接口检查必须**失败**。

    ★ 判据：导向接口缺失 ⇒ `require` 抛 ⇒ `interfaces_ok=False`。
    """
    m = _model()
    del m.interfaces["guide_width_mm"]
    r = V.evaluate_vise(m, turns=5.0, readback_mm=20.0, jaw_dof=1,
                        jaw_motions=["移动"])
    assert r["interfaces_ok"] is False
    assert r["ok"] is False


def test_r3_misbinding_the_lead_must_fail() -> None:
    """★★ **R3**：把「**导程**」误绑成**另一字段** ⇒ 传动检查必须**失败**。

    ★ 做法：把 `screw_lead_mm` 的值换成 `screw_dia_mm`（20）而回读还是 20
      ⇒ 独立算 20×5=100 vs 回读 20 ⇒ **不一致** ⇒ 检出。
    """
    tc = V.lead_to_travel(20.0, 5.0, readback_mm=20.0)   #: ★ 误绑成直径
    assert tc.consistent is False, "★★ 导程误绑没被发现！"
    assert tc.computed == 100.0


def test_r4_deleting_thread_definition_must_fail() -> None:
    """★★ **R4**：**删除螺纹工程定义** ⇒ 图纸/规则检查必须**失败**。"""
    r = V.evaluate_vise(_model(), turns=5.0, readback_mm=20.0, jaw_dof=1,
                        jaw_motions=["移动"], thread=V.ThreadSpec())
    assert r["thread"]["verdict"] == "INDETERMINATE"
    assert r["indeterminate"] == ["thread"]
    assert r["ok"] is False


def test_r5_volume_alone_cannot_make_it_pass() -> None:
    """★★ **R5**：**仅体积通过不能使其恢复为成功**。

    ★ 判据：`evaluate_vise` **没有**「体积」这个输入 ——
      ★ 即**不可能**用体积把一个失败的功能检查「盖过去」。
      ★ 这是**结构性**保证（★ 不是靠判据写对）。
    """
    import inspect
    sig = inspect.signature(V.evaluate_vise)
    assert "volume" not in sig.parameters, \
        "★★ `evaluate_vise` 收了 volume ⇒ 体积可能盖过功能检查"
    #: ★ 且四项功能判据都在返回体里**逐项**可见（★ 不是一个大 bool）
    r = _good()
    for k in ("interfaces_ok", "thread", "travel", "jaw"):
        assert k in r, "★ 缺功能判据 %s ⇒ 无法逐项核" % k
