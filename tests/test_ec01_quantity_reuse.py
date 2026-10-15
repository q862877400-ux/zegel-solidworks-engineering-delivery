"""★ EC01 判据（V1–V3）—— 量纲复用 / 必需缺失阻断 / 意图归一。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering_contract.py`（★ EC01 的单一权威实现）
#         `specs/303-ec01-engineering-contract/spec.md`（★ V1–V8）
#         `specs/302-ec00-trustworthy-tool-base/contracts/quantity.md`（★ **复用**的 Quantity）
# 定位:   ★ EC01 的 **V1（非法量纲阻断）· V2（缺关键工况阻断）· V3（同意图归一）**。
# 官方依据: 不适用（本仓的工程契约模型）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import engineering_contract as ec


# ══════════════════════════════════════════════════════════════════════
# V1 · 非法量纲在 COM 前阻断
# ══════════════════════════════════════════════════════════════════════

def test_v1_kind_mismatch_is_rejected():
    """★★★ V1：★ **长度字段收到角度单位 ⇒ 拒绝**（★ 且码是 `reject-kind-mismatch`）。"""
    q = ec.Quantity(value=90.0, unit="deg", quantity_kind="length")
    with pytest.raises(ec.Rejection) as exc:
        ec.normalize_quantity(q)
    assert exc.value.code == "reject-kind-mismatch", "★ 拒绝码不对：%s" % exc.value.code


def test_v1_nonfinite_is_rejected():
    """★★ V1：★ **NaN / ±无穷 ⇒ 拒绝**（★ 码 `reject-nonfinite`）。"""
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ec.Rejection) as exc:
            ec.normalize_quantity(ec.Quantity(value=bad, unit="mm", quantity_kind="length"))
        assert exc.value.code == "reject-nonfinite", "★ %r 的拒绝码不对" % bad


def test_v1_unknown_unit_is_rejected():
    """★★ V1：★ **未知单位 ⇒ 拒绝**（★ 码 `reject-unknown-unit`）。"""
    with pytest.raises(ec.Rejection) as exc:
        ec.normalize_quantity(ec.Quantity(value=1.0, unit="furlong", quantity_kind="length"))
    assert exc.value.code == "reject-unknown-unit", "★ 拒绝码不对：%s" % exc.value.code


def test_v1_double_conversion_is_rejected():
    """★★★ V1：★ **规范化结果再次规范化 ⇒ 拒绝**（★ 防重复换算 —— ★ 承 EC00 FR-003）。"""
    with pytest.raises(ec.Rejection) as exc:
        ec.normalize_quantity(ec.Quantity(value=1.0, unit="m", quantity_kind="length"),
                              already_normalized=True)
    assert exc.value.code == "reject-double-conversion", "★ 拒绝码不对"


def test_v1_rejection_codes_are_a_closed_vocabulary():
    """★★ V1：★ 拒绝码必须是**封闭词表**（★ 与 EC00 **同一套** —— ★ 不各建一套）。"""
    ec00 = (ROOT / "specs" / "302-ec00-trustworthy-tool-base" / "contracts" / "quantity.md")
    assert ec00.is_file(), "★ 缺 EC00 的 quantity 契约"
    body = ec00.read_text(encoding="utf-8", errors="replace")
    for code in ec.REJECTION_CODES:
        assert code in body, (
            "★★ 拒绝码 `%s` **不在 EC00 的契约里** ⇒ ★ 两处各建了一套（★ 违反铁律 1）" % code)


def test_v1_unit_equivalence_normalizes_to_same_value():
    """★★ V1：★ **10 mm 与 0.01 m 归一到同一值**（★ 与 EC00 同口径）。"""
    a = ec.normalize_quantity(ec.Quantity(10.0, "mm", "length"))
    b = ec.normalize_quantity(ec.Quantity(0.01, "m", "length"))
    assert abs(a.value - b.value) < 1e-12, "★ 归一结果不一致：%r vs %r" % (a.value, b.value)
    assert a.canonical_unit == b.canonical_unit == "m"


def test_v1_temperature_uses_offset_not_multiplication():
    """★★★ V1：★ **温度是偏置单位 ⇒ 用加法不用乘法**（★ 承 EC00 `contracts/quantity.md` §2.3）。

    ★★ 依据（★ EC00 逐字）：★「★ **偏置单位如温度独立定义，不混用乘法**」。
    """
    n = ec.normalize_quantity(ec.Quantity(0.0, "degC", "temperature"))
    assert abs(n.value - 273.15) < 1e-9, (
        "★★ 0 degC 应归一为 273.15 K（★ 实得 %r）⇒ ★ 可能错用了乘法" % n.value)
    assert n.canonical_unit == "K"


# ══════════════════════════════════════════════════════════════════════
# V2 · 缺关键工况在 COM 前阻断
# ══════════════════════════════════════════════════════════════════════

def test_v2_missing_load_case_blocks():
    """★★★ V2：★ **缺工况 ⇒ 阻断**（★ 不默认「普通」）。"""
    lc = ec.LoadCase(name="工况A", kind="static", magnitude=None, is_missing=True)
    assert lc.blocks() is True, "★★ 缺工况却**没有**阻断 ⇒ ★ 会拿默认值算强度"


def test_v2_missing_safety_level_blocks_freeze():
    """★★★ V2/FR-003：★ **安全等级缺失 ⇒ 不得冻结**（★ 不默认「普通」）。

    ★★ 依据（★ 计划 §5 EC01-T03 逐字）：
      「★ 定义 …… `ApprovalRef`；★ **安全等级/工况缺失不能默认「普通」**」。
    """
    c = ec.EngineeringContract(contract_id="C1", intent="做一个支架")
    c.classify("load", ec.InformationClass.KNOWN)
    with pytest.raises(ValueError) as exc:
        c.freeze()
    assert "safety_level" in str(exc.value), (
        "★★ 安全等级缺失却冻成了 ⇒ ★ 违反「不能默认普通」：%s" % exc.value)


def test_v2_required_missing_blocks_freeze():
    """★★★ V2：★ **`required_missing` 非空 ⇒ 不得冻结**。"""
    c = ec.EngineeringContract(contract_id="C2", intent="做一个支架")
    c.classify("material", ec.InformationClass.REQUIRED_MISSING)
    c.safety_level = "普通"
    assert c.blocking_fields() == ["material"], "★ 阻断字段识别不对"
    with pytest.raises(ValueError) as exc:
        c.freeze()
    assert "material" in str(exc.value), "★ 阻断信息不具体：%s" % exc.value


def test_v2_assumption_without_basis_is_rejected():
    """★★ V2：★ **假设没有依据 ⇒ 不可接受**（★ S1-3）。"""
    assert ec.Assumption("x", 1, basis="").is_acceptable() is False, (
        "★★ 没有依据的假设被接受了 ⇒ ★ 等于「我觉得」")
    assert ec.Assumption("x", 1, basis="★ 按 GB/T 标准的下限").is_acceptable() is True


def test_v2_non_conservative_assumption_is_rejected():
    """★★★ V2/EC01-T07：★ **禁止假设项**不得被当成假设（★ 保守与禁止要分开）。"""
    a = ec.Assumption("safety", "普通", basis="猜的", conservative=False)
    assert a.is_acceptable() is False, (
        "★★ **非保守**的假设被接受了 ⇒ ★ 会把「禁止假设」的项蒙混过去")


# ══════════════════════════════════════════════════════════════════════
# V3 · 两个不同表述的同意图归一到同语义
# ══════════════════════════════════════════════════════════════════════

def test_v3_same_intent_different_expressions_normalize_equal():
    """★★★ V3：★ **「80 毫米的板」与「0.08 米的板」归一后同语义**。

    ★★ 依据（★ 计划 §5 EC01 验收逐字）：
      「★ **两个不同表述的同意图归一到同语义**」。
    """
    a = ec.normalize_quantity(ec.Quantity(80.0, "mm", "length"))
    b = ec.normalize_quantity(ec.Quantity(0.08, "m", "length"))
    assert abs(a.value - b.value) < 1e-12
    #: ★★ 且**单位也归一**（★ 否则只是「值相等」不是「同语义」）
    assert a.canonical_unit == b.canonical_unit


def test_v3_normalization_is_explainable():
    """★★ V3：★ 归一必须**可解释**（★ 保留原始值 + 规则版本 —— ★ 不是黑箱）。"""
    q = ec.Quantity(80.0, "mm", "length")
    n = ec.normalize_quantity(q)
    assert n.original is q, "★ 归一结果**没有**保留原始量 ⇒ ★ 不可解释"
    assert n.rule_version, "★ 没有规则版本 ⇒ ★ 不可追溯"


def test_v3_different_intents_are_not_conflated():
    """★★★ V3 **负例**：★ **不同意图不得被归一**（★ 长度 ≠ 角度）。"""
    length = ec.normalize_quantity(ec.Quantity(1.0, "m", "length"))
    angle = ec.normalize_quantity(ec.Quantity(1.0, "rad", "angle"))
    assert length.canonical_unit != angle.canonical_unit, (
        "★★ 长度与角度归一到**同一单位** ⇒ ★ 把不同意图混了")
    #: ★★ 且**量纲本身**必须不同（★ 那是「不同意图」的**身份**）
    assert length.original.quantity_kind != angle.original.quantity_kind, (
        "★★ 两个归一结果的 `quantity_kind` 相同 ⇒ ★ 量纲没区分开")
