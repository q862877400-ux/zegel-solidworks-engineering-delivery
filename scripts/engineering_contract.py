"""★ EC01 工程设计契约与对象模型 —— **单一权威**的 `EngineeringContract` 与配套对象。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC01**（★ T01–T08 逐字）
#         `specs/303-ec01-engineering-contract/spec.md`（★ 15 FR · 8 V）
#         `specs/302-ec00-trustworthy-tool-base/contracts/quantity.md`（★ **复用**的 Quantity）
#         `subskills/solidworks-vibecad/schemas/design_plan.schema.json`（★ 旧计划 · 10 字段）
# 定位:   ★ **EC01** 的**唯一权威**实现。★★★ 依据计划 §5 EC01 逐字：「★ 增加单一权威 E
#           ngineeringContract 定义」
#         ★★ **铁律 1（只做缝合）**：★ `Quantity` **复用 EC00 的定义**（★ 不另建一套量纲）；
#         ★ 只在「design_plan 装不下」时才新增概念（★ 工况/义务/批准/四类信息）。
# 官方依据: 不适用（本仓的工程契约模型 —— ★ 不调 SolidWorks API）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件（★ **纯离线** —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "InformationClass", "ContractState", "Resolution", "Rejection",
    "Quantity", "NormalizedQuantity", "Datum", "LoadCase", "MaterialRef",
    "ProcessIntent", "ParameterDomain", "VerificationObligation",
    "Assumption", "ApprovalRef", "EngineeringContract",
    "normalize_quantity", "REJECTION_CODES", "adapt_design_plan",
    "LEGACY_FIELDS", "LEGACY_ALWAYS_MISSING",
]


# ══════════════════════════════════════════════════════════════════════
# 一、★★ 四类信息（★ EC01-T01 · FR-001）
# ══════════════════════════════════════════════════════════════════════

class InformationClass:
    """★ 四类信息（★ 计划 §5 EC01-T01 逐字：「划分已知、假设、待确认、必需缺失四类信息」）。"""

    KNOWN = "known"                              #: ★ 已知（★ 用户给了）
    ASSUMED = "assumed"                          #: ★ 假设（★ 我们保守填了 —— ★ **必须给依据**）
    NEEDS_CONFIRMATION = "needs_confirmation"    #: ★ 待确认（★ 问了才知道）
    REQUIRED_MISSING = "required_missing"        #: ★★ **必需缺失** ⇒ ★ **阻断**

    ALL = (KNOWN, ASSUMED, NEEDS_CONFIRMATION, REQUIRED_MISSING)
    #: ★★ **阻断类**（★ 非空 ⇒ 不得冻结、不得进 COM）
    BLOCKING = (REQUIRED_MISSING,)


class ContractState:
    """★ 契约状态机（★ 计划 §5 EC01-T04 逐字：`draft→needs_clarification→frozen→superseded`）。"""

    DRAFT = "draft"
    NEEDS_CLARIFICATION = "needs_clarification"
    FROZEN = "frozen"
    SUPERSEDED = "superseded"

    #: ★★ **允许的迁移**（★ 封闭表 —— ★ 别的迁移一律拒绝）
    TRANSITIONS = {
        DRAFT: (NEEDS_CLARIFICATION, FROZEN),
        NEEDS_CLARIFICATION: (DRAFT, FROZEN),
        FROZEN: (SUPERSEDED,),
        SUPERSEDED: (),                          #: ★ 终态
    }
    #: ★★ **只有这个状态能进 COM**（★ FR-004）
    COM_ELIGIBLE = (FROZEN,)


class Resolution:
    """★ 引用解析结果（★ **复用 EC00 的封闭词表** —— ★ `specs/302-*/data-model.md` §4.2）。"""

    RESOLVED_UNIQUE = "resolved_unique"
    NOT_FOUND = "not_found"
    AMBIGUOUS = "ambiguous"
    WRONG_CONTEXT = "wrong_context"
    UNSUPPORTED = "unsupported"

    #: ★ 只有这个允许进入修改
    ALLOWED = (RESOLVED_UNIQUE,)


#: ★★ 拒绝码（★ **封闭词表** —— ★ 与 EC00 的 `contracts/quantity.md` §二 **同一套**）
REJECTION_CODES = (
    "reject-kind-mismatch",        #: ★ 量纲不符
    "reject-nonfinite",            #: ★ NaN / ±无穷
    "reject-out-of-domain",        #: ★ 域外
    "reject-unknown-unit",         #: ★ 未知单位
    "reject-double-conversion",    #: ★ 重复换算
)


class Rejection(Exception):
    """★ 拒绝（★ 带**封闭词表**的码 —— ★ 与 EC00 同族）。"""

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in REJECTION_CODES, "★ 非法拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


# ══════════════════════════════════════════════════════════════════════
# 二、★★ Quantity（★ **复用 EC00** —— ★ 不另建一套量纲 · FR-002）
# ══════════════════════════════════════════════════════════════════════

#: ★★ 规范单位（★ 与 EC00 `contracts/quantity.md` §2.3 **同一张表**）
CANONICAL_UNIT = {
    "length": "m",
    "angle": "rad",
    "force": "N",
    "stress": "Pa",
    "speed": "rad/s",
    "mass": "kg",
    "temperature": "K",
}

#: ★★ 公开单位 → 规范单位的**换算因子**（★ 只对**可乘**单位 —— ★ 温度是偏置，单列）
UNIT_SCALE = {
    ("length", "mm"): 1.0 / 1000.0,
    ("length", "m"): 1.0,
    ("angle", "deg"): math.pi / 180.0,
    ("angle", "rad"): 1.0,
    ("force", "N"): 1.0,
    ("force", "kN"): 1000.0,
    ("mass", "kg"): 1.0,
    ("mass", "g"): 1.0 / 1000.0,
}

#: ★★ **偏置单位**（★ 官方/工程惯例：★ 温度**不能**用乘法 —— ★ 承 EC00 `contracts/quanti
#: ty.md` §2.3）
OFFSET_UNITS = {
    ("temperature", "degC"): ("K", 273.15),      #: ★ value + 273.15
}


@dataclass(frozen=True)
class Quantity:
    """★ 用户提交的原始量值（★ **复用 EC00 的字段语义**）。"""

    value: float
    unit: str
    quantity_kind: str
    source: str = "supplied"          #: ★ `supplied` / `legacy_contract_default`


@dataclass(frozen=True)
class NormalizedQuantity:
    """★ 规范化结果（★ **独立结构** ⇒ ★ 防重复换算 —— ★ 承 EC00）。"""

    value: float
    canonical_unit: str
    original: Quantity
    rule_version: str = "ec01-v1"


def normalize_quantity(q: Quantity, *, already_normalized: bool = False) -> NormalizedQuantity:
    """★ 规范化（★ 唯一入口 —— ★ 只做**一次**换算）。

    ★★★ 拒绝条件（★ 与 EC00 `contracts/quantity.md` §二 **同一套码**）：
      · `reject-kind-mismatch` —— ★ 量纲与单位不匹配（★ 如长度字段收 `deg`）
      · `reject-nonfinite` —— ★ NaN / ±无穷
      · `reject-unknown-unit` —— ★ 未知单位
      · `reject-double-conversion` —— ★ `NormalizedQuantity` **再次**进入
    """
    if already_normalized:
        raise Rejection("reject-double-conversion",
                        "★ 规范化结果**不能**再次作为原始 Quantity 转换")
    if not isinstance(q.value, (int, float)) or not math.isfinite(q.value):
        raise Rejection("reject-nonfinite", "★ 值不是有限数：%r" % (q.value,))
    kind, unit = q.quantity_kind, q.unit
    #: ★★ 偏置单位（★ 温度）单列 —— ★ **不混用乘法**
    if (kind, unit) in OFFSET_UNITS:
        canon, offset = OFFSET_UNITS[(kind, unit)]
        return NormalizedQuantity(float(q.value) + offset, canon, q)
    key = (kind, unit)
    if key not in UNIT_SCALE:
        #: ★★ 区分「量纲不对」与「单位不认识」—— ★ 两个**不同**的码
        #:   ★★★ **2026-10-10 订正**：★ 第一版判反了 —— ★ 它查「该量纲有没有别的单位」
        #:     ⇒ ★ `("length","deg")` 落进「量纲有单位 ⇒ 单位不认识」✗
        #: ★★ **正解**：★ 查 **`unit` 是否属于**别的**量纲** —— ★ 是 ⇒ `reject-kind-mism
        #: atch`；
        #:     ★ 谁都不属于 ⇒ `reject-unknown-unit` ✓
        known_kinds_of_this_unit = {k for (k, u) in UNIT_SCALE if u == unit}
        known_kinds_of_this_unit |= {k for (k, u) in OFFSET_UNITS if u == unit}
        if known_kinds_of_this_unit and kind not in known_kinds_of_this_unit:
            raise Rejection("reject-kind-mismatch",
                            "★ 量纲 %r 与单位 %r 不匹配（★ 该单位属于 %r）"
                            % (kind, unit, sorted(known_kinds_of_this_unit)))
        raise Rejection("reject-unknown-unit", "★ 量纲 %s 不认识单位 %r" % (kind, unit))
    scale = UNIT_SCALE[key]
    return NormalizedQuantity(float(q.value) * scale, CANONICAL_UNIT[kind], q)


# ══════════════════════════════════════════════════════════════════════
# 三、★★ 其余工程对象（★ FR-002）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Datum:
    """★ 工程基准。

    ★★★ **关键（★ 计划 §5 EC01 验收逐字）**：「★ **工程基准不能简单等同任一 CAD 基准面**」
      ⇒ ★ 工程基准**引用**CAD 平面（★ 可以换），★ 而**工程语义**（★ 如「装配结合面」）
        ★★ **不随 CAD 平面改名而变**。
    """

    name: str
    semantic_role: str                                   #: ★ 工程语义（★ 「装配结合面」等）
    cad_plane_hint: str | None = None                    #: ★ **提示**，★ 不是身份
    #: ★★ 依据（★ 计划 §5 EC01 逐字）：「工程基准不能简单等同任一 CAD 基准面」
    NOT_MERELY_A_CAD_PLANE = True

    def identity(self) -> str:
        """★ 身份 = **语义角色**（★ **不含** CAD 平面名 —— ★ 那会随 UI 语言变）。"""
        return "datum:%s" % self.semantic_role


@dataclass
class LoadCase:
    """★ 工况（★ **缺它不能给强度结论** —— ★ 承计划 §5 EC05-T01）。"""

    name: str
    kind: str                        #: ★ 如 `static` / `fatigue` / `impact` / `thermal`
    magnitude: NormalizedQuantity | None = None
    #: ★★ **缺失时的处置**（★ FR-003 逐字：「安全等级/工况缺失不能默认「普通」」）
    is_missing: bool = False

    def blocks(self) -> bool:
        """★★ **缺失 ⇒ 阻断**（★ 不默认「普通」）。"""
        return bool(self.is_missing) or self.magnitude is None


@dataclass
class MaterialRef:
    """★ 材料引用（★ **带版本** —— ★ FR-006）。"""

    name: str
    standard: str = ""
    version: str = ""                #: ★★ 材料标准会换版 ⇒ ★ 必须记版本
    properties: dict = field(default_factory=dict)


@dataclass
class ProcessIntent:
    """★ 工艺意图（★ 如 `machined` / `sheet_metal` / `welded` / `3d_printed`）。"""

    kind: str
    notes: str = ""


@dataclass
class ParameterDomain:
    """★ 参数域（★ **逐字段** —— ★ 不搞全局域）。"""

    name: str
    low: float
    high: float
    unit: str = ""
    #: ★★ **是否允许负值由字段语义决定**（★ 承 EC00 `plan.md` §6.1 逐字）
    allow_negative: bool = True

    def contains(self, value: float) -> bool:
        if not math.isfinite(value):
            return False
        if value < 0 and not self.allow_negative:
            return False
        return self.low <= value <= self.high


@dataclass
class VerificationObligation:
    """★ 验证义务（★ **Agent 不能删掉硬义务** —— ★ 承 EC00 `data-model.md` §三）。"""

    id: str
    description: str
    mandatory: bool = True
    evidence_kind: str = ""          #: ★ 如 `readback` / `calc` / `test`


@dataclass
class Assumption:
    """★ 假设（★ **必须给依据** —— ★ S1-3）。"""

    field_name: str
    value: Any
    basis: str                       #: ★★ 依据（★ 不能「我觉得」）
    conservative: bool = True        #: ★ 可保守假设 / 禁止假设（★ EC01-T07）

    def is_acceptable(self) -> bool:
        """★★ **只有可保守假设项 + 有依据**才可接受。"""
        return bool(self.conservative) and bool(self.basis.strip())


@dataclass
class ApprovalRef:
    """★ 批准引用（★ **绑定内容哈希** ⇒ ★ 内容变了就失效 —— ★ FR-004）。"""

    approver: str
    content_hash: str
    note: str = ""


# ══════════════════════════════════════════════════════════════════════
# 四、★★★ EngineeringContract（★ **单一权威**）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class EngineeringContract:
    """★★★ **EC01 的单一权威工程契约**（★ 计划 §5 EC01 逐字要求）。

    ★★ 与 EC00 的分工：★ EC00 管「工具执行可信」；★★★ **本类管「工程语义正确」**。
    """

    contract_id: str
    intent: str                                     #: ★ 工程意图（★ 一句话）
    state: str = ContractState.DRAFT
    #: ★★ 四类信息（★ 逐字段）
    information: dict = field(default_factory=dict)  #: field -> InformationClass
    #: ★ 工程对象
    datums: list = field(default_factory=list)
    load_cases: list = field(default_factory=list)
    material: MaterialRef | None = None
    process: ProcessIntent | None = None
    parameter_domains: dict = field(default_factory=dict)
    obligations: list = field(default_factory=list)
    assumptions: list = field(default_factory=list)
    approvals: list = field(default_factory=list)
    #: ★ 澄清问题（★ **最小集** —— ★ FR-007）
    clarifications: list = field(default_factory=list)
    #: ★ 安全等级（★ **缺省不是「普通」** —— ★ FR-003）
    safety_level: str | None = None
    #: ★ 冻结时算的**内容哈希**
    content_hash: str = ""

    # ── 四类信息 ────────────────────────────────────────────────────
    def classify(self, field_name: str, cls: str) -> None:
        assert cls in InformationClass.ALL, "★ 非法信息类：%r" % cls
        self.information[field_name] = cls

    def blocking_fields(self) -> list[str]:
        """★★ **必需缺失**的字段（★ 非空 ⇒ ★ 不得冻结、不得进 COM）。"""
        return sorted(f for f, c in self.information.items()
                      if c in InformationClass.BLOCKING)

    # ── 内容哈希 ────────────────────────────────────────────────────
    def compute_hash(self) -> str:
        """★ 内容哈希（★ **不含** `state`/`approvals`/`content_hash` 自身 —— ★ 否则自指）。

        ★★ 依据（★ FR-004）：★ 「新版本不能借用旧批准」⇒ ★ 批准绑的是**内容**哈希。
        """
        payload = {
            "contract_id": self.contract_id,
            "intent": self.intent,
            "information": dict(sorted(self.information.items())),
            "datums": [d.identity() if hasattr(d, "identity") else str(d) for d in self.datums],
            "load_cases": [
                {"name": lc.name, "kind": lc.kind, "is_missing": lc.is_missing,
                 "value": (lc.magnitude.value if lc.magnitude else None),
                 "unit": (lc.magnitude.canonical_unit if lc.magnitude else None)}
                for lc in self.load_cases],
            "material": ({"name": self.material.name, "version": self.material.version}
                         if self.material else None),
            "process": (self.process.kind if self.process else None),
            "parameter_domains": {
                k: [v.low, v.high, v.unit, v.allow_negative]
                for k, v in sorted(self.parameter_domains.items())},
            "obligations": [o.id for o in self.obligations],
            "assumptions": [
                {"field": a.field_name, "value": str(a.value), "basis": a.basis,
                 "conservative": a.conservative} for a in self.assumptions],
            "safety_level": self.safety_level,
        }
        blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
        return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()

    # ── 状态机 ──────────────────────────────────────────────────────
    def may_transition_to(self, target: str) -> bool:
        return target in ContractState.TRANSITIONS.get(self.state, ())

    def transition(self, target: str) -> None:
        """★ 状态迁移（★ **非法迁移一律拒绝**）。"""
        if not self.may_transition_to(target):
            raise ValueError("★ 非法状态迁移：%s → %s（★ 允许：%r）"
                             % (self.state, target, ContractState.TRANSITIONS.get(self.state, ())))
        self.state = target

    def freeze(self) -> str:
        """★★★ **冻结**（★ 唯一产生内容哈希的地方 —— ★ 且**有阻断就不许冻**）。"""
        blocking = self.blocking_fields()
        if blocking:
            raise ValueError("★★ 有**必需缺失**字段 ⇒ 不得冻结：%r" % blocking)
        #: ★★ 安全等级缺失 ⇒ ★ **不得默认「普通」**（★ FR-003 逐字）
        if self.safety_level is None:
            raise ValueError("★★ `safety_level` 缺失 ⇒ ★ 不得默认「普通」（★ FR-003）")
        #: ★★ 不可接受的假设 ⇒ 拒绝
        bad = [a.field_name for a in self.assumptions if not a.is_acceptable()]
        if bad:
            raise ValueError("★★ 有不可接受的假设（★ 需「可保守」+「有依据」）：%r" % bad)
        self.state = ContractState.FROZEN
        self.content_hash = self.compute_hash()
        return self.content_hash

    # ── 批准 ────────────────────────────────────────────────────────
    def add_approval(self, approver: str, note: str = "") -> ApprovalRef:
        """★ 批准（★ **绑定当前内容哈希** —— ★ 内容变了就失效）。"""
        if self.state != ContractState.FROZEN:
            raise ValueError("★★ 只有 `frozen` 才能批准（★ 当前 %s）" % self.state)
        ref = ApprovalRef(approver=approver, content_hash=self.content_hash, note=note)
        self.approvals.append(ref)
        return ref

    def approval_is_valid(self, ref: ApprovalRef) -> bool:
        """★★★ **旧批准不能用于新内容**（★ FR-004 · ★ V4 的核心）。"""
        return (ref.content_hash == self.content_hash
                and self.content_hash != ""
                and self.state == ContractState.FROZEN)

    def supersede(self) -> None:
        """★ 取代（★ **旧批准随之失效** —— ★ 因为哈希会变）。"""
        self.transition(ContractState.SUPERSEDED)

    # ── 进 COM 的门 ─────────────────────────────────────────────────
    def com_eligible(self) -> bool:
        """★★★ **只有 `frozen` 才能进 COM**（★ 且内容哈希非空）。"""
        return self.state in ContractState.COM_ELIGIBLE and bool(self.content_hash)


# ══════════════════════════════════════════════════════════════════════
# 五、★★★★ 旧 `design_plan` → 新契约适配（★ EC01-T05 · FR-005）
# ══════════════════════════════════════════════════════════════════════

#: ★★ 旧 `design_plan.schema.json` 的**10 个字段**（★ 逐字，★ 不凭记忆）
LEGACY_FIELDS = ("plan_version", "source_brief", "part_family", "parameters",
                 "features", "operation_sequence", "assumptions", "risk_register",
                 "review_plan", "solidworks_mapping")

#: ★★★ **旧计划装不下、必须标 `required_missing` 的字段**（★ 不编默认值）
#:   ★★ 依据（★ 计划 §5 EC01-T05 逐字）：「★ **旧信息不足保留 `unknown`**」
LEGACY_ALWAYS_MISSING = ("material", "load_case", "safety_level", "process", "datums")


def adapt_design_plan(legacy: dict, *, contract_id: str = "") -> EngineeringContract:
    """★★★ **旧 `design_plan` → 新 `EngineeringContract`** 的适配器（★ EC01-T05）。

    ★★★ **两条硬规则**：
      1. ★★ **旧信息不足 ⇒ 保留 `unknown`** —— ★ **绝不编默认值**
         （★ 尤其 ★ **`safety_level` 不得默认「普通」** —— ★ FR-003 逐字）；
      2. ★★ **不改旧公开契约**（★ 承 `DSH_DECISIONS.md` **D-001**）—— ★ 本函数**只读** `legacy`，
         ★ **不写回**、★ **不要求旧计划加字段**。

    ★ **旧计划里能用的**（★ 10 字段里真的有内容的）：
      · `source_brief` → ★ `intent`
      · `part_family`  → ★ `process` 的**提示**（★ 不是结论）
      · `assumptions`  → ★ `Assumption`（★ **必须补依据**，★ 否则不可接受）
      · `parameters`   → ★ 标 `needs_confirmation`（★ **旧计划没有单位** ⇒ ★ **不造域**）
    """
    if not isinstance(legacy, dict):
        raise TypeError("★ `legacy` 必须是 dict（★ 旧 design_plan 的解析结果）")
    missing_required = [f for f in ("plan_version", "source_brief", "part_family")
                        if f not in legacy]
    if missing_required:
        raise ValueError("★★ 不是合法的旧 design_plan（★ 缺 %r）" % missing_required)

    c = EngineeringContract(
        contract_id=contract_id or ("LEGACY-%s" % legacy.get("plan_version", "?")),
        #: ★★ `intent` 是**必填** ⇒ ★ 先给旧计划里的 `source_brief`（★ 可能是空串）
        intent=str(legacy.get("source_brief") or ""))
    c.intent = str(legacy.get("source_brief") or "")
    c.classify("intent",
               InformationClass.KNOWN if c.intent else InformationClass.REQUIRED_MISSING)
    c.classify("part_family", InformationClass.KNOWN)
    #: ★★ `part_family` 只是**工艺提示**（★ 不据此定工艺结论）
    if legacy.get("part_family"):
        c.process = ProcessIntent(kind=str(legacy["part_family"]),
                                  notes="★ 来自旧计划（仅提示）")
    #: ★ `assumptions` → ★ `Assumption`（★ **旧计划没给依据 ⇒ 依据留空** ⇒ 不可接受）
    for a in (legacy.get("assumptions") or []):
        c.assumptions.append(Assumption(
            field_name="legacy_assumption", value=str(a), basis="", conservative=True))
        c.classify("legacy_assumption", InformationClass.NEEDS_CONFIRMATION)
    #: ★★ `parameters` ⇒ ★ 标待确认（★ 旧计划**没有单位** ⇒ ★ **不造域**）
    if legacy.get("parameters"):
        c.classify("parameters", InformationClass.NEEDS_CONFIRMATION)
    #: ★★★ **旧计划装不下的** ⇒ ★ **一律 `required_missing`**（★ **不编默认值**）
    for field_name in LEGACY_ALWAYS_MISSING:
        c.classify(field_name, InformationClass.REQUIRED_MISSING)
    #: ★★ **`safety_level` 保持 `None`** —— ★ **绝不默认「普通」**（★ FR-003 逐字）
    assert c.safety_level is None, "★ 适配器不得默认安全等级"
    return c
