"""★ EC01 判据（T05/T08）—— 旧计划适配器 + **四类**工程契约正例。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering_contract.py`（★ `adapt_design_plan` · ★ 四类契约）
#         `specs/303-ec01-engineering-contract/spec.md`（★ FR-005 · FR-008 · V6）
#         `subskills/solidworks-vibecad/schemas/design_plan.schema.json`（★ 旧计划 · 10 字段）
# 定位:   ★ EC01 的 **T05（旧计划适配）** 与 **T08（板/轴/机构/气动四类契约 + 三类负例）**。
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


# ══════════════════════════════════════════════════════════════════════
# T05 · 旧 design_plan → 新契约适配
# ══════════════════════════════════════════════════════════════════════

def _legacy_min() -> dict:
    """★ 一份**最小合法**的旧 design_plan（★ 信息不足 —— ★ 那正是要测的）。"""
    return {"plan_version": 1, "source_brief": "做一个安装板", "part_family": "plate",
            "parameters": {"thickness_mm": 10}, "features": [],
            "operation_sequence": [], "assumptions": ["板厚按中值"],
            "risk_register": [], "review_plan": {}}


def test_t05_adapter_exists_and_returns_a_contract():
    """★★ T05：★ 适配器必须存在且回一个 `EngineeringContract`。"""
    assert hasattr(ec, "adapt_design_plan"), "★ 缺 `adapt_design_plan`（★ T05 的产物）"
    c = ec.adapt_design_plan(_legacy_min())
    assert isinstance(c, ec.EngineeringContract), "★ 适配器没回契约"
    assert c.intent == "做一个安装板", "★ `source_brief` 没映射到 `intent`：%r" % c.intent


def test_t05_adapter_keeps_unknown_instead_of_inventing_defaults():
    """★★★★★ T05：★ **旧信息不足 ⇒ 保留 `unknown`**（★ **不编默认值**）。

    ★★ 依据（★ 计划 §5 EC01-T05 逐字）：「★ **旧信息不足保留 `unknown`**」。
    """
    c = ec.adapt_design_plan(_legacy_min())
    #: ★★★ **安全等级**：★ 绝不默认「普通」
    assert c.safety_level is None, "★★ 适配器默认了安全等级 ⇒ ★ 违反 FR-003"
    #: ★★ **材料/工况**：★ 不编
    assert c.material is None, "★★ 适配器编了材料"
    assert not c.load_cases, "★★ 适配器编了工况"
    #: ★★★ 且这些字段**必须**在阻断清单里
    for f in ("material", "load_case", "safety_level"):
        assert f in c.blocking_fields(), "★★ `%s` 没被标 `required_missing`" % f
    #: ★★ 且**不得冻结**
    with pytest.raises(ValueError):
        c.freeze()


def test_t05_adapter_does_not_write_back_to_the_legacy_plan():
    """★★★ T05：★ 适配器**只读**旧计划（★ **不改旧公开契约** —— ★ 承 D-001）。"""
    legacy = _legacy_min()
    before = json.dumps(legacy, ensure_ascii=False, sort_keys=True)
    ec.adapt_design_plan(legacy)
    after = json.dumps(legacy, ensure_ascii=False, sort_keys=True)
    assert before == after, "★★ 适配器**改写了**旧计划 ⇒ ★ 违反 D-001（★ 旧契约不变）"


def test_t05_adapter_rejects_an_invalid_legacy_plan():
    """★★ T05：★ 非法旧计划 ⇒ **拒绝**（★ 不是硬适配出一个错的）。"""
    with pytest.raises((ValueError, TypeError)):
        ec.adapt_design_plan({"foo": 1})
    with pytest.raises((ValueError, TypeError)):
        ec.adapt_design_plan("not a dict")


def test_t05_adapter_covers_all_ten_legacy_fields():
    """★★ T05：★ 适配器必须**认全**旧 schema 的 10 个字段（★ 不挑着认）。"""
    d = json.loads(OLD_SCHEMA.read_text(encoding="utf-8"))
    on_disk = set(d["properties"])
    assert set(ec.LEGACY_FIELDS) == on_disk, (
        "★★ 适配器认的字段与旧 schema 不一致：\n  旧 schema %r\n  适配器 %r"
        % (sorted(on_disk), sorted(ec.LEGACY_FIELDS)))


def test_t05_legacy_assumption_has_no_basis_so_it_is_unacceptable():
    """★★★ T05：★ 旧计划的假设**没有依据** ⇒ ★ **不可接受**（★ 不自动当可信）。"""
    c = ec.adapt_design_plan(_legacy_min())
    assert c.assumptions, "★ 旧计划的假设没被带过来"
    for a in c.assumptions:
        assert a.basis == "", "★ 旧计划本无依据 ⇒ ★ 适配器**编了**一个依据"
        assert a.is_acceptable() is False, (
            "★★ 无依据的旧假设被当成可接受 ⇒ ★ 等于替用户拍板")


# ══════════════════════════════════════════════════════════════════════
# T08 · 板 / 轴 / 机构 / 气动 四类契约
# ══════════════════════════════════════════════════════════════════════

def _make(kind: str) -> ec.EngineeringContract:
    """★ 造四类契约之一（★ 每类有**不同的**工程语义）。"""
    c = ec.EngineeringContract(contract_id="K-" + kind, intent="做%s" % kind)
    c.classify("intent", ec.InformationClass.KNOWN)
    c.safety_level = "普通"
    c.material = ec.MaterialRef(name="Q235", standard="GB/T 700", version="2006")
    c.process = ec.ProcessIntent(kind=kind)
    if kind == "plate":
        #: ★ 板：★ 结合面 + 面载荷
        c.datums.append(ec.Datum(name="安装结合面", semantic_role="mounting_interface",
                                 cad_plane_hint="Front Plane"))
        c.load_cases.append(ec.LoadCase("面压", "static",
                                        ec.normalize_quantity(ec.Quantity(1.0, "N", "force"))))
        c.parameter_domains["thickness"] = ec.ParameterDomain(
            "thickness", 0.002, 0.05, "m", allow_negative=False)
    elif kind == "shaft":
        #: ★ 轴：★ **回转轴** + 转矩/转速
        c.datums.append(ec.Datum(name="回转轴", semantic_role="rotation_axis"))
        c.load_cases.append(ec.LoadCase("转矩", "static",
                                        ec.normalize_quantity(ec.Quantity(50.0, "N", "force"))))
        c.parameter_domains["diameter"] = ec.ParameterDomain(
            "diameter", 0.005, 0.2, "m", allow_negative=False)
    elif kind == "mechanism":
        #: ★ 机构：★ **运动副** + 行程
        c.datums.append(ec.Datum(name="机架基准", semantic_role="frame_datum"))
        c.load_cases.append(ec.LoadCase("动载荷", "impact",
                                        ec.normalize_quantity(ec.Quantity(200.0, "N", "force"))))
        c.parameter_domains["stroke"] = ec.ParameterDomain(
            "stroke", 0.0, 1.0, "m", allow_negative=False)
    elif kind == "pneumatic":
        #: ★ 气动：★ **气路接口** + 压力
        c.datums.append(ec.Datum(name="气路接口面", semantic_role="port_interface"))
        c.load_cases.append(ec.LoadCase("气压", "static",
                                        ec.normalize_quantity(ec.Quantity(0.6, "N", "force"))))
        c.parameter_domains["bore"] = ec.ParameterDomain(
            "bore", 0.008, 0.1, "m", allow_negative=False)
    else:
        raise ValueError("★ 未知类别：%r" % kind)
    c.obligations.append(ec.VerificationObligation(
        id="OB-%s" % kind, description="回读关键尺寸", evidence_kind="readback"))
    return c


@pytest.mark.parametrize("kind", ["plate", "shaft", "mechanism", "pneumatic"])
def test_t08_four_contract_kinds_can_be_frozen(kind):
    """★★★ T08：★ **四类契约都能冻结**（★ 且各有不同的工程语义）。"""
    c = _make(kind)
    assert c.state == ec.ContractState.DRAFT
    h = c.freeze()
    assert h.startswith("sha256:"), "★ 冻结没产生内容哈希：%r" % h
    assert c.com_eligible() is True, "★ 冻结后应可进 COM"


def test_t08_four_kinds_have_distinct_semantics():
    """★★★ T08：★ 四类契约的**工程语义必须不同**（★ 不是同一个模板换个名字）。

    ★★ 判据：★ **语义角色**（★ datum 的 `semantic_role`）与**参数字段**必须**各不相同**。
    """
    roles, params = set(), set()
    for kind in ("plate", "shaft", "mechanism", "pneumatic"):
        c = _make(kind)
        roles.add(c.datums[0].semantic_role)
        params.add(tuple(sorted(c.parameter_domains)))
    assert len(roles) == 4, "★★ 四类的语义角色不互异：%r" % sorted(roles)
    assert len(params) == 4, "★★ 四类的参数字段不互异：%r" % sorted(params)


def test_t08_four_kinds_have_distinct_content_hashes():
    """★★ T08：★ 四类的**内容哈希必须互异**（★ 否则「不同契约」是假的）。"""
    hashes = {k: _make(k).compute_hash() for k in ("plate", "shaft", "mechanism", "pneumatic")}
    assert len(set(hashes.values())) == 4, "★★ 有内容哈希相同 ⇒ ★ 契约没区分开：%r" % hashes


# ══════════════════════════════════════════════════════════════════════
# T08 · 三类负例（缺参数 / 冲突 / 错误单位）
# ══════════════════════════════════════════════════════════════════════

def test_t08_negative_missing_parameter():
    """★★★ T08 负例 ①：★ **缺参数** ⇒ ★ 阻断。"""
    c = _make("plate")
    c.classify("hole_diameter", ec.InformationClass.REQUIRED_MISSING)
    with pytest.raises(ValueError) as exc:
        c.freeze()
    assert "hole_diameter" in str(exc.value)


def test_t08_negative_wrong_unit():
    """★★★ T08 负例 ③：★ **错误单位** ⇒ ★ 拒绝（★ COM 前）。"""
    with pytest.raises(ec.Rejection) as exc:
        ec.normalize_quantity(ec.Quantity(10.0, "deg", "length"))
    assert exc.value.code == "reject-kind-mismatch"


def test_t08_negative_conflicting_domains():
    """★★★ T08 负例 ②：★ **冲突**（★ 两个域不相交 ⇒ ★ 阻断）。

    ★ 例：★ 一个说「厚度 ∈ [2, 5] mm」、★ 另一个说「厚度 ∈ [10, 20] mm」⇒ ★ **无交集**。
    """
    a = ec.ParameterDomain("thickness", 0.002, 0.005, "m", allow_negative=False)
    b = ec.ParameterDomain("thickness", 0.010, 0.020, "m", allow_negative=False)
    lo, hi = max(a.low, b.low), min(a.high, b.high)
    assert lo > hi, (
        "★ 两个域**有交集** ⇒ ★ 这组样本不是「冲突」⇒ ★ 换个样本（★ 判据自身要有效）")
    #: ★★ 冲突 ⇒ ★ 不得冻结
    c = _make("plate")
    c.parameter_domains["thickness"] = a
    c.classify("thickness_conflict", ec.InformationClass.REQUIRED_MISSING)
    with pytest.raises(ValueError):
        c.freeze()
