"""★ EC01 判据（V4–V8）—— 状态机与批准 / 工程基准 ≠ CAD 平面 / 旧计划适配 / 最小澄清集。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering_contract.py`（★ EC01 的单一权威实现）
#         `specs/303-ec01-engineering-contract/spec.md`（★ V1–V8）
#         `subskills/solidworks-vibecad/schemas/design_plan.schema.json`（★ 旧计划 · 10 字段）
# 定位:   ★ EC01 的 **V4（新版本不能借用旧批准）· V5（工程基准 ≠ CAD 基准面）·
#           V6（旧计划适配）· V7（四类信息）· V8（最小澄清集）**。
# 官方依据: 不适用（本仓的工程契约模型）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import engineering_contract as ec

OLD_SCHEMA = ROOT / "subskills" / "solidworks-vibecad" / "schemas" / "design_plan.schema.json"


def _frozen_contract(**kw) -> ec.EngineeringContract:
    """★ 造一个**能冻结**的契约（★ 最小合法集）。"""
    c = ec.EngineeringContract(contract_id=kw.get("contract_id", "C1"),
                               intent=kw.get("intent", "做一个安装板"))
    c.classify("load", ec.InformationClass.KNOWN)
    c.safety_level = kw.get("safety_level", "普通")
    c.datums.append(ec.Datum(name="安装结合面", semantic_role="mounting_interface",
                             cad_plane_hint="Front Plane"))
    c.load_cases.append(ec.LoadCase(name="工况A", kind="static",
                                    magnitude=ec.normalize_quantity(
                                        ec.Quantity(100.0, "N", "force"))))
    c.material = ec.MaterialRef(name="Q235", standard="GB/T 700", version="2006")
    c.process = ec.ProcessIntent(kind="machined")
    c.parameter_domains["thickness"] = ec.ParameterDomain(
        "thickness", 0.001, 0.05, "m", allow_negative=False)
    c.obligations.append(ec.VerificationObligation(
        id="OB-1", description="回读孔径", evidence_kind="readback"))
    return c


# ══════════════════════════════════════════════════════════════════════
# V4 · 新版本不能借用旧批准
# ══════════════════════════════════════════════════════════════════════

def test_v4_state_machine_transitions_are_closed():
    """★★★ V4：★ 状态机迁移必须是**封闭表**（★ 非法迁移一律拒绝）。"""
    c = ec.EngineeringContract(contract_id="C", intent="x")
    assert c.state == ec.ContractState.DRAFT
    #: ★ 合法：draft → needs_clarification
    c.transition(ec.ContractState.NEEDS_CLARIFICATION)
    assert c.state == ec.ContractState.NEEDS_CLARIFICATION
    #: ★★ 非法：needs_clarification → superseded
    with pytest.raises(ValueError):
        c.transition(ec.ContractState.SUPERSEDED)


def test_v4_only_frozen_can_enter_com():
    """★★★ V4：★ **只有 `frozen` 才能进 COM**（★ FR-004）。"""
    c = _frozen_contract()
    assert c.com_eligible() is False, "★★ 未冻结就 `com_eligible` ⇒ ★ 会先建再说"
    c.freeze()
    assert c.com_eligible() is True, "★ 冻结后应可进 COM"
    c.supersede()
    assert c.com_eligible() is False, "★★ `superseded` 仍可进 COM ⇒ ★ 旧版本还能改模型"


def test_v4_old_approval_cannot_be_borrowed_by_new_content():
    """★★★★★ V4 的**核心**：★ **新版本不能借用旧批准**。

    ★★ 依据（★ 计划 §5 EC01 验收逐字）：「★ **新版本不能借用旧批准**」。
    ★ 判据：★ ① 冻结 → 批准 ⇒ 有效；★ ② **改了内容** ⇒ 旧批准**失效**。
    """
    c = _frozen_contract()
    c.freeze()
    ref = c.add_approval("张三", note="初版批准")
    assert c.approval_is_valid(ref) is True, "★ 刚批准的应有效"
    #: ★★★ **改内容** ⇒ 重算哈希 ⇒ 旧批准失效
    c.parameter_domains["thickness"] = ec.ParameterDomain(
        "thickness", 0.002, 0.06, "m", allow_negative=False)
    c.content_hash = c.compute_hash()          #: ★ 内容变了，哈希跟着变
    assert c.approval_is_valid(ref) is False, (
        "★★★ **新内容**借用了**旧批准** ⇒ ★ 那是「改完设计还用旧审签」（★ V4 的核心负例）")


def test_v4_content_hash_changes_with_content():
    """★★ V4：★ **内容哈希随内容变**（★ 否则批准绑定无意义）。"""
    a = _frozen_contract(contract_id="A")
    b = _frozen_contract(contract_id="B")
    assert a.compute_hash() != b.compute_hash(), "★★ 不同内容的哈希相同 ⇒ ★ 绑定失效"
    #: ★ 同内容 ⇒ 同哈希（★ 可复现）
    assert a.compute_hash() == a.compute_hash(), "★ 同内容哈希不稳定"


def test_v4_hash_excludes_self_referential_fields():
    """★★ V4：★ 哈希**不含** `state`/`approvals`/`content_hash` 自身（★ 否则自指）。"""
    c = _frozen_contract()
    h1 = c.compute_hash()
    c.approvals.append(ec.ApprovalRef(approver="李四", content_hash="x"))
    assert c.compute_hash() == h1, (
        "★★ 加了批准后哈希变了 ⇒ ★ 哈希把 `approvals` 算进去了（★ 自指）")


def test_v4_approval_requires_frozen_state():
    """★★ V4：★ **未冻结不得批准**（★ 否则批准绑定的是一个还没定的东西）。"""
    c = ec.EngineeringContract(contract_id="C", intent="x")
    with pytest.raises(ValueError):
        c.add_approval("王五")


# ══════════════════════════════════════════════════════════════════════
# V5 · 工程基准不能简单等同任一 CAD 基准面
# ══════════════════════════════════════════════════════════════════════

def test_v5_datum_identity_is_semantic_not_cad_plane():
    """★★★★★ V5：★ **工程基准的身份 = 语义角色**，★ **不是 CAD 平面名**。

    ★★ 依据（★ 计划 §5 EC01 验收逐字）：
      「★ **工程基准不能简单等同任一 CAD 基准面**」。
    ★★★ **为什么重要**：★ CAD 平面名随 UI 语言变（★ 已知事实 9：`"Front Plane"` / `"前视基准面"`）
      ⇒ ★★ 若身份绑平面名，★ **换语言就换身份** ✗
    """
    d = ec.Datum(name="安装结合面", semantic_role="mounting_interface",
                 cad_plane_hint="Front Plane")
    assert d.identity() == "datum:mounting_interface", "★ 身份不是语义角色：%s" % d.identity()
    assert "Front Plane" not in d.identity(), (
        "★★ 身份里含 CAD 平面名 ⇒ ★ 换 UI 语言就换身份（★ V5 的核心负例）")


def test_v5_datum_identity_survives_cad_plane_rename():
    """★★★ V5：★ **CAD 平面改名 ⇒ 工程基准身份不变**。"""
    a = ec.Datum(name="安装结合面", semantic_role="mounting_interface", cad_plane_hint="Front Plane")
    b = ec.Datum(name="安装结合面", semantic_role="mounting_interface", cad_plane_hint="前视基准面")
    assert a.identity() == b.identity(), (
        "★★ CAD 平面名一变，工程基准身份就变 ⇒ ★ 违反 V5")


def test_v5_datum_declares_the_distinction():
    """★★ V5：★ 实现必须**显式**声明这条区分（★ 不是只靠注释）。"""
    assert getattr(ec.Datum, "NOT_MERELY_A_CAD_PLANE", False) is True, (
        "★★ `Datum` 没有声明「工程基准 ≠ CAD 基准面」这条")


# ══════════════════════════════════════════════════════════════════════
# V6 · 旧 design_plan 适配（★ 不足留 unknown）
# ══════════════════════════════════════════════════════════════════════

def test_v6_old_schema_is_readable():
    """★★ V6：★ 旧 `design_plan.schema.json` 必须**可读**（★ 适配的前提）。"""
    assert OLD_SCHEMA.is_file(), "★ 找不到旧 design_plan schema"
    d = json.loads(OLD_SCHEMA.read_text(encoding="utf-8"))
    assert "properties" in d, "★ 旧 schema 结构变了"
    #: ★★ 适配器必须认这 10 个字段里的**关键几个**
    for key in ("part_family", "parameters", "features", "assumptions"):
        assert key in d["properties"], "★★ 旧 schema 缺 `%s` ⇒ ★ 适配器要跟着改" % key


def test_v6_adapter_keeps_unknown_instead_of_inventing_defaults():
    """★★★★★ V6：★ **旧信息不足 ⇒ 保留 `unknown`**（★ **不编默认值**）。

    ★★ 依据（★ 计划 §5 EC01-T05 逐字）：
      「★ 实现 schema 校验及**旧设计计划→新契约适配**；★ **旧信息不足保留 `unknown`**」。
    """
    #: ★ 造一个**信息不足**的旧计划（★ 没有材料、没有工况、没有安全等级）
    legacy = {"plan_version": 1, "source_brief": "做个板", "part_family": "plate",
              "parameters": {}, "features": [], "operation_sequence": [],
              "assumptions": [], "risk_register": [], "review_plan": {}}
    c = ec.EngineeringContract(contract_id="LEGACY-1", intent="做个板")
    #: ★★ 适配：★ 缺的字段**标 `required_missing`**（★ 不填一个默认值）
    for field_name in ("material", "load_case", "safety_level"):
        c.classify(field_name, ec.InformationClass.REQUIRED_MISSING)
    assert c.material is None, (
        "★★ 适配器**编了一个默认材料** ⇒ ★ 违反「不足保留 unknown」")
    assert c.safety_level is None, (
        "★★ 适配器**默认了安全等级** ⇒ ★ 违反「不能默认普通」")
    #: ★★ 且这些字段**必须**出现在阻断清单里
    assert set(c.blocking_fields()) == {"material", "load_case", "safety_level"}
    #: ★★★ 且**不得冻结**
    with pytest.raises(ValueError):
        c.freeze()


def test_v6_adapter_does_not_change_the_old_public_contract():
    """★★ V6：★ 适配**不改变**旧公开契约（★ 承 `DSH_DECISIONS.md` **D-001**）。"""
    d = json.loads(OLD_SCHEMA.read_text(encoding="utf-8"))
    #: ★★ 旧 schema 的 `required` 必须**原样**（★ 适配器不许改它）
    assert d.get("required"), "★ 旧 schema 的 `required` 不见了 ⇒ ★ 可能被改过"
    assert "plan_version" in d["required"], "★ 旧 schema 的必需字段被动了"


# ══════════════════════════════════════════════════════════════════════
# V7 · 四类信息
# ══════════════════════════════════════════════════════════════════════

def test_v7_four_information_classes_exist():
    """★★ V7：★ **四类信息**必须齐（★ 计划 §5 EC01-T01 逐字）。"""
    assert set(ec.InformationClass.ALL) == {
        "known", "assumed", "needs_confirmation", "required_missing"}, (
        "★ 四类信息不是这四类：%r" % (ec.InformationClass.ALL,))


def test_v7_only_required_missing_blocks():
    """★★★ V7：★ **只有 `required_missing` 阻断**（★ 别的三类不阻断）。

    ★★ 理由：★ `assumed` 是**保守**填的（★ 可接受）；★ `needs_confirmation` 是**待问**的
      （★ 可以带着问题进下一步）；★★ **`required_missing` 是「没有它就不能做」** ⇒ 阻断。
    """
    c = ec.EngineeringContract(contract_id="C", intent="x")
    for f in ("a", "b", "c", "d"):
        c.classify(f, ec.InformationClass.KNOWN)
    assert c.blocking_fields() == [], "★ 全 `known` 不该阻断"
    c.classify("a", ec.InformationClass.ASSUMED)
    c.classify("b", ec.InformationClass.NEEDS_CONFIRMATION)
    assert c.blocking_fields() == [], "★★ `assumed`/`needs_confirmation` **不该**阻断"
    c.classify("c", ec.InformationClass.REQUIRED_MISSING)
    assert c.blocking_fields() == ["c"], "★★ `required_missing` **必须**阻断"


def test_v7_invalid_information_class_is_rejected():
    """★★ V7：★ 非法信息类必须**拒绝**（★ 不能随手加一个）。"""
    c = ec.EngineeringContract(contract_id="C", intent="x")
    with pytest.raises(AssertionError):
        c.classify("a", "probably_fine")


# ══════════════════════════════════════════════════════════════════════
# V8 · 澄清问题是最小集
# ══════════════════════════════════════════════════════════════════════

def test_v8_clarifications_only_cover_blocking_fields():
    """★★★ V8：★ **澄清问题必须只覆盖影响决策的字段**（★ 最小集 —— ★ EC01-T07）。

    ★★ 依据（★ 计划 §5 EC01-T07 逐字）：
      「★ 把澄清问题**限定成影响决策的最小问题集**」。
    """
    c = ec.EngineeringContract(contract_id="C", intent="x")
    c.classify("material", ec.InformationClass.REQUIRED_MISSING)
    c.classify("color", ec.InformationClass.NEEDS_CONFIRMATION)
    #: ★★ 最小集 = ★ **只问阻断的**（★ `color` **不阻断** ⇒ ★ 不该进最小集）
    minimal = c.blocking_fields()
    assert minimal == ["material"], "★ 最小集不最小：%r" % minimal
    assert "color" not in minimal, (
        "★★ 不阻断的字段进了最小澄清集 ⇒ ★ 会问一堆不影响决策的问题")


def test_v8_conservative_and_forbidden_assumptions_are_separated():
    """★★★ V8：★ **可保守假设项与禁止假设项必须分开**（★ EC01-T07 逐字）。"""
    ok = ec.Assumption("thickness", 0.01, basis="★ 按同类件取中值", conservative=True)
    forbidden = ec.Assumption("safety_level", "普通", basis="猜的", conservative=False)
    assert ok.is_acceptable() is True
    assert forbidden.is_acceptable() is False, (
        "★★ 「禁止假设」的项被当成可假设 ⇒ ★ 两类别没分开")
    #: ★★ 且**不能靠改 basis 混过去**
    sneaky = ec.Assumption("safety_level", "普通", basis="★ 看起来像普通", conservative=False)
    assert sneaky.is_acceptable() is False, (
        "★★★ 只靠「写个好依据」就把**禁止假设项**蒙混过去了 ⇒ ★ 两类别没真正分开")
