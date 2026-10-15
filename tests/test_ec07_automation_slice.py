"""★ EC07 判据 —— MotionIR / AutomationIR / SafetyFunctionIR / 状态可达性 / 故障矩阵 / 选型。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/automation.py`（★ EC07 的实现）
#         `specs/309-ec07-automation-slice/spec.md`
# 定位:   ★ EC07 的判据（★ 逐字承计划 §5 EC07 的「验收」）。
# 官方依据: 不适用（本仓的自动化设计层）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰 COM · ★ **不下发 PLC**）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest

from engineering import automation as A


def _motion(**kw) -> A.MotionIR:
    base = dict(stroke_m=0.300, cycle_time_s=1.2, payload_kg=5.0,
                moving_mass_kg=2.0, efficiency=0.85, braking="★ 电磁失电制动",
                thermal_limit_c=60.0)
    base.update(kw)
    return A.MotionIR(**base)


def _safe(**kw) -> A.SafetyFunctionIR:
    base = dict(safety_level=A.SafetyLevel.ASSESSED,
                assessment_method="★ ISO 13849-1 PLd 评估（★ 方法已具名）",
                accountable_person="★ 安全负责人 A")
    base.update(kw)
    s = A.SafetyFunctionIR(**base)
    return s


# ══════════════════════════════════════════════════════════════════════
# V1 · MotionIR 的六项
# ══════════════════════════════════════════════════════════════════════

def test_v1_motion_ir_requires_all_fields():
    """★★★ V1：★ **MotionIR 缺项 ⇒ 不完整**（★ 逐字承 EC07-T02 的六项）。

    ★★ 判据：★ 缺项 ⇒ **不得据此选型**（★ 不是「用默认值凑」）。
    """
    assert _motion().is_complete()["ok"] is True
    for miss in ({"stroke_m": 0.0}, {"cycle_time_s": 0.0},
                 {"efficiency": 0.0}, {"braking": ""}):
        out = _motion(**miss).is_complete()
        assert out["ok"] is False, "★★ 缺 %r 却判完整" % miss
        assert out["missing"], "★ 没说是缺哪项"


def test_v1_peak_and_rms_force_are_computed():
    """★★★ V1：★ **峰值/均方根负荷**必须算（★ 逐字承 EC07-T02）。"""
    m = _motion()
    assert m.peak_force() > 0, "★ 峰值力没算"
    assert m.rms_force() < m.peak_force(), "★ RMS 应**小于**峰值"
    #: ★★ 独立核算（★ 手写 —— ★ 不共享实现）
    v = 0.300 / (1.2 * 0.5)
    a = 4.0 * v / 1.2
    f = 7.0 * a
    assert abs(m.peak_velocity() - v) < 1e-12, "★ 峰值速度不符"
    assert abs(m.peak_force() - f) < 1e-9, "★ 峰值力不符"
    assert abs(m.rms_force() - f / math.sqrt(3.0)) < 1e-9, "★ RMS 不符"


def test_v1_peak_power_uses_efficiency():
    """★★ V1：★ **峰值功率含效率**（★ `P = F v / η`）。"""
    m = _motion()
    expected = m.peak_force() * m.peak_velocity() / 0.85
    assert abs(m.peak_power() - expected) < 1e-9, "★ 功率没算效率"


# ══════════════════════════════════════════════════════════════════════
# V2 · AutomationIR 的来源与版本
# ══════════════════════════════════════════════════════════════════════

def test_v2_sensors_require_source_and_version():
    """★★★★ V2：★ **接口型号数据须有来源和版本**（★ 逐字承 EC07-T03）。

    ★★ 判据：★ 缺 `source` 或 `version` ⇒ **不算合格**（★ 且**点名**哪个传感器）。
    """
    good = A.AutomationIR(sensors=[
        {"name": "S1", "type": "接近开关", "source": "★ 厂商 A 样本", "version": "2024-03"},
    ])
    assert good.sensors_have_sources()["ok"] is True
    #: ★★ 缺 version ⇒ 不合格
    bad = A.AutomationIR(sensors=[
        {"name": "S1", "type": "接近开关", "source": "★ 厂商 A 样本"},
    ])
    out = bad.sensors_have_sources()
    assert out["ok"] is False, "★★ 缺 version 却判合格"
    assert out["bad"][0]["missing"] == ["version"]
    #: ★★ 空表 ⇒ 不合格
    assert A.AutomationIR().sensors_have_sources()["ok"] is False


def test_v2_interlocks_are_queryable_by_kind():
    """★★ V2：★ 互锁**按种类可查**（★ 那是「安全与普通分开」的基础）。"""
    ir = A.AutomationIR(interlocks=[
        {"kind": A.InterlockKind.NORMAL, "expr": "★ 夹紧到位才允许移动"},
        {"kind": A.InterlockKind.SAFETY, "expr": "★ 开门即停"},
    ])
    assert len(ir.interlock_by_kind(A.InterlockKind.NORMAL)) == 1
    assert len(ir.interlock_by_kind(A.InterlockKind.SAFETY)) == 1


# ══════════════════════════════════════════════════════════════════════
# V3 · 安全功能不能被普通互锁替代（★ 验收核心）
# ══════════════════════════════════════════════════════════════════════

def test_v3_unknown_safety_level_cannot_be_replaced_by_normal_interlocks():
    """★★★★★ V3：★ **安全功能 `unknown` 不能被普通互锁测试替代**（★ 逐字承验收）。

    ★★★ **判据**：★ 即使**普通互锁全通过**，★ 只要安全等级是 `UNKNOWN`
      ⇒ ★ 结论**仍是 `unknown`** ✓
    """
    s = A.SafetyFunctionIR()          #: ★ 默认 `safety_level = UNKNOWN`
    out = s.verdict(normal_interlocks=[{"ok": True}, {"ok": True}, {"ok": True}])
    assert out["verdict"] == "unknown", (
        "★★★ 普通互锁全通过就把安全功能判成 %r ⇒ ★ 那正是验收禁止的「替代」"
        % out["verdict"])
    assert out["releasing"] is False
    assert out["substituted"] is False, "★★ 它**没有被替代**（★ 如实标）"
    assert out["normal_interlocks_passed"] is True, (
        "★ 应如实记「普通互锁确实通过了」—— ★ 但**结论仍是 unknown**")


def test_v3_safety_level_requires_method_and_accountability():
    """★★★★ V3：★ **安全等级需要适用方法与审核责任**（★ 逐字承 EC07-T04）。"""
    #: ★ 只有等级、没方法/责任人 ⇒ 仍不算确定
    s = A.SafetyFunctionIR(safety_level=A.SafetyLevel.ASSESSED)
    out = s.level_is_established()
    assert out["ok"] is False, "★★ 只有等级却没方法/责任人 ⇒ 不算确定"
    assert set(out["missing"]) == {"assessment_method", "accountable_person"}
    #: ★ 补齐 ⇒ 算确定
    s.assessment_method = "★ ISO 13849-1"
    s.accountable_person = "★ 安全负责人 A"
    assert s.level_is_established()["ok"] is True


def test_v3_unverified_safety_function_blocks():
    """★★★ V3：★ **安全功能未验证 ⇒ `unknown`**（★ 等级已定也不行）。"""
    s = _safe()
    s.add_safety_function("急停", implements="★ 断动力", verified=False)
    out = s.verdict()
    assert out["verdict"] == "unknown", "★★ 未验证的安全功能被判通过"
    assert out["unverified_functions"] == ["急停"]


def test_v3_fully_verified_passes_with_the_mark():
    """★★★★ V3：★ **等级已定 + 全验证 ⇒ `pass`，★ 且**必须带标记****。

    ★★ 依据（★ 验收逐字）：★「★ 设计产物**标清「未经实机调试/安全确认」**」。
    """
    s = _safe()
    s.add_safety_function("急停", implements="★ 断动力", verified=True)
    out = s.verdict()
    assert out["verdict"] == "pass", "★ 该通过却判 %r" % out["verdict"]
    assert out["mark"] == A.UNVERIFIED_ON_REAL_MACHINE, (
        "★★★ 通过了却**没带「未经实机调试」标记** ⇒ ★ 违反验收")


def test_v3_safety_functions_are_tagged_as_safety_not_normal():
    """★★★ V3：★ 安全功能**必须被标成 `safety_function`**（★ 不是普通互锁）。"""
    s = _safe()
    s.add_safety_function("开门停", implements="★ 门开即断", verified=True)
    assert s.functions[0]["kind"] == A.InterlockKind.SAFETY, (
        "★★ 安全功能被标成了普通互锁 ⇒ ★ 两类会混")
    assert s.functions[0]["kind"] != A.InterlockKind.NORMAL


# ══════════════════════════════════════════════════════════════════════
# V4 · 状态可达性与正常循环
# ══════════════════════════════════════════════════════════════════════

def _sm() -> A.StateMachine:
    """★ 一个**直线搬运单元**的状态机（★ 首域 —— ★ 计划 §5 EC07）。"""
    return A.StateMachine(
        initial="idle",
        transitions={
            "idle": {"start": "homing"},
            "homing": {"home_ok": "ready"},
            "ready": {"clamp": "clamped"},
            "clamped": {"move": "moving"},
            "moving": {"in_position": "unclamping"},
            "unclamping": {"done": "idle"},
            "faulted": {"reset": "idle"},
            "estop": {"reset": "idle"},
        })


def test_v4_normal_cycle_is_repeatable():
    """★★★★ V4：★ **一个正常循环可重复验证**（★ 逐字承验收）。"""
    sm = _sm()
    events = ["start", "home_ok", "clamp", "move", "in_position", "done"]
    a = sm.run_cycle(events)
    b = sm.run_cycle(events)
    assert a["ok"] is True, "★ 正常循环跑不通：%r" % a
    assert a["trace"] == b["trace"], "★★ 同一个事件序两次跑出不同轨迹 ⇒ 不可重复"
    assert a["final"] == "idle", "★ 循环该回到 idle：%r" % a["final"]


def test_v4_missing_transition_is_reported():
    """★★ V4：★ **缺迁移 ⇒ 报出来**（★ 不静默停）。"""
    sm = _sm()
    out = sm.run_cycle(["start", "bogus_event"])
    assert out["ok"] is False, "★★ 非法事件却没报"
    assert out["event"] == "bogus_event"
    assert "没有对事件" in out["reason"]


def test_v4_unreachable_states_are_detected():
    """★★★★ V4：★ **不可达状态必须检出**（★ 逐字承 EC07-T05：★「★ **有限状态可达性测试**」）。"""
    sm = A.StateMachine(initial="a",
                        transitions={"a": {"go": "b"}, "b": {"back": "a"},
                                     "orphan": {"x": "a"}})
    assert "orphan" in sm.unreachable(), (
        "★★ 定义里写了但走不到的状态**没检出**")
    assert "a" in sm.reachable() and "b" in sm.reachable()


def test_v4_dead_ends_are_detected_but_safe_terminals_are_ok():
    """★★ V4：★ **死端**要检出（★ 但 `estop`/`faulted` **是安全终态** ⇒ 不算死端）。"""
    sm = A.StateMachine(initial="a",
                        transitions={"a": {"go": "stuck"}, "stuck": {},
                                     "estop": {}, "faulted": {}})
    assert "stuck" in sm.dead_ends(), "★★ 死端没检出"
    assert "estop" not in sm.dead_ends(), "★★ `estop` 被当成死端 ⇒ ★ 误报"
    assert "faulted" not in sm.dead_ends(), "★★ `faulted` 被当成死端"


# ══════════════════════════════════════════════════════════════════════
# V5 · 具名故障矩阵
# ══════════════════════════════════════════════════════════════════════

def test_v5_all_seven_fault_kinds_are_required():
    """★★★★ V5：★ **七类故障都要具名**（★ 逐字承 EC07-T05）。

    ★★ 七类：★ 极限/原点/夹紧/开门/**失电/失气/传感器冲突**。
    """
    fm = A.FaultMatrix()
    for k in A.FaultMatrix.DEFAULT_KINDS:
        fm.add(k, expected="★ 期望：断动力并停在安全位", implemented=True)
    out = fm.is_named_and_complete()
    assert out["ok"] is True, "★ 七类齐却判不完整：%r" % out
    assert out["count"] == 7


def test_v5_missing_fault_kind_is_reported():
    """★★★ V5：★ **缺一类 ⇒ 报出来**（★ 且**点名**缺哪类）。"""
    fm = A.FaultMatrix()
    for k in A.FaultMatrix.DEFAULT_KINDS[:-1]:      #: ★ 少最后一类
        fm.add(k, expected="★ 期望反应", implemented=True)
    out = fm.is_named_and_complete()
    assert out["ok"] is False
    assert out["missing_kinds"] == [A.FaultKind.SENSOR_CONFLICT], (
        "★ 没点名缺哪类：%r" % out["missing_kinds"])


def test_v5_fault_row_without_expected_is_rejected():
    """★★★ V5：★ **没写期望反应 ⇒ 不算具名**（★ 那是「有个名字」不是「具名」）。"""
    fm = A.FaultMatrix()
    with pytest.raises(ValueError):
        fm.add(A.FaultKind.LIMIT, expected="   ", implemented=True)


def test_v5_unimplemented_faults_are_reported_not_hidden():
    """★★★★ V5：★ **未实现的故障必须如实报**（★ 不假装做了）。"""
    fm = A.FaultMatrix()
    for k in A.FaultMatrix.DEFAULT_KINDS:
        fm.add(k, expected="★ 期望反应",
               implemented=(k != A.FaultKind.AIR_LOSS))
    out = fm.is_named_and_complete()
    assert out["ok"] is True, "★ 齐了就该 ok（★ 未实现不影响「具名完整」）"
    assert out["unimplemented"] == [A.FaultKind.AIR_LOSS], (
        "★★ 未实现的故障没如实报 ⇒ ★ 会被当成做了")


# ══════════════════════════════════════════════════════════════════════
# V6 · 选型
# ══════════════════════════════════════════════════════════════════════

def test_v6_selection_picks_the_largest_margin():
    """★★★ V6：★ **选余量最大的**（★ 且**带依据**）。"""
    m = _motion()
    cands = [{"kind": "motor", "model": "M1", "rated_force_n": m.peak_force() * 1.5},
             {"kind": "motor", "model": "M2", "rated_force_n": m.peak_force() * 3.0},
             {"kind": "motor", "model": "M3", "rated_force_n": m.peak_force() * 2.0}]
    out = A.select_drive(m, candidates=cands)
    assert out.model == "M2", "★ 没选余量最大的：%r" % out.model
    assert out.basis, "★ 选型没有依据"
    assert out.mark == A.UNVERIFIED_ON_REAL_MACHINE, "★★ 选型缺标记"


def test_v6_incomplete_motion_blocks_selection():
    """★★★★ V6：★ **MotionIR 不完整 ⇒ 不选型**（★ 不硬算）。"""
    out = A.select_drive(_motion(stroke_m=0.0),
                         candidates=[{"kind": "motor", "model": "M1",
                                      "rated_force_n": 1000.0}])
    assert out.kind == "" and out.model == "", "★★ 不完整却选了型"
    assert "不完整" in out.basis


def test_v6_no_candidate_means_no_selection():
    """★★ V6：★ **没候选 ⇒ 不选**（★ 不编一个）。"""
    out = A.select_drive(_motion(), candidates=[])
    assert out.model == ""
    assert "没有可用候选" in out.basis


def test_v6_margin_must_be_enough():
    """★★ V6：★ **余量不够 ⇒ 不接受**（★ `min_margin` 默认 1.2）。"""
    tight = A.SelectionResult(kind="motor", model="M", margin=1.05,
                              basis="★ 依据")
    assert tight.is_acceptable()["ok"] is False, "★★ 余量 1.05 < 1.2 却接受"
    ok = A.SelectionResult(kind="motor", model="M", margin=1.8, basis="★ 依据")
    assert ok.is_acceptable()["ok"] is True


# ══════════════════════════════════════════════════════════════════════
# V7 · 纯离线 + 不下发 PLC
# ══════════════════════════════════════════════════════════════════════

def test_v7_module_is_offline():
    """★★★ V7：★ **自动化层不 import COM**（★ 首域是**只设计不驱动**）。"""
    assert A.assert_no_com_imports()["ok"] is True


def test_v7_no_plc_output_in_the_module():
    """★★★★ V7：★ **不直接下发 PLC 控制**（★ 逐字承总计划 §3.2）。

    ★★ 判据：★ 模块里**不许**出现 PLC/实机驱动相关的**导入或调用**。
    """
    src = (ROOT / "scripts" / "engineering" / "automation.py").read_text(
        encoding="utf-8", errors="replace")
    for banned in ("import snap7", "import pycomm3", "modbus", "OPCUA", "opcua"):
        assert banned not in src, (
            "★★★ 自动化层出现了实机驱动 `%s` ⇒ ★ 违反「不直接驱动实机」" % banned)


def test_v7_design_mark_is_mandatory():
    """★★★★ V7：★ **「未经实机调试/安全确认」标记是强制的**（★ 逐字承验收）。"""
    assert "未经实机调试" in A.UNVERIFIED_ON_REAL_MACHINE
    assert "不得据此驱动实机" in A.UNVERIFIED_ON_REAL_MACHINE, (
        "★★ 标记里没写「不得据此驱动实机」⇒ ★ 不够明确")
    #: ★★ 选型结果**默认**带它
    assert A.SelectionResult().mark == A.UNVERIFIED_ON_REAL_MACHINE
