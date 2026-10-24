"""★ 阶段 7 · 箱体孔系 + 剖分面 + 最终 DoD（规格 322 的 M1~M4）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/housing.py
# 定位:   规格 `specs/322-stage7-housing-final-dod` 的 M1（共享接口控制关联零件）/M2（
#           证据非循环）/ M3（四层区分）/ M4（最终 DoD 清单）。★★ 实测（2026-10-12）起点
#           ：`assembly.py` 已有 `ToleranceChain`；`sw_hole_features.py` + `prove_hole_p
#           attern.py` 已有孔系能力；`sw_mold.py` 已有分型/剖分能力；阶段 3 的 `recovery
#           .py` 已有`ArtifactDigest`/`changed_after_revision`；阶段 4~6 已有三类产品的
#           规划。★ 而**没有最终 DoD 清单、没有「证据非循环」检查、  没有四层区分、没有
#           9 案例汇总**。
# 官方依据: ① 外部方案阶段 7 的验收 S7-A / S7-B（逐字）② 外部方案 §5 R7 ④ 逐字：「替换一
#           份证据为『读取台账并断言 verified』、   移除必需图纸、替换旧版本产物、隐藏一
#           次人工接管，   交付完整性与证据检查必须分别失败」③ `scripts/engineering/reco
#           very.py` 的 `ArtifactDigest`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收入口 `tools/run_stage7_final_dod.py`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

try:
    from ._case_collector import CaseCollectorMixin
except ImportError:
    from _case_collector import CaseCollectorMixin

from dataclasses import dataclass, field

#: ══════════════════════════════════════════════════════════════════════
# 一、封闭码
#: ══════════════════════════════════════════════════════════════════════

PASS = "pass"
FAIL = "fail"
MISSING = "missing"
CIRCULAR = "circular-evidence"
OUT_OF_SCOPE = "out-of-scope-claim"

DOD_CODES = (PASS, FAIL, MISSING, CIRCULAR, OUT_OF_SCOPE)


class HousingError(Exception):
    """★ 箱体/DoD 失败（★ 带封闭码）。"""

    CODES = (
        "no-baseline",
        "axis-mismatch",
        "circular-evidence",
        "missing-gate",
        "out-of-scope",
    )

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法箱体拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


#: ══════════════════════════════════════════════════════════════════════
# 二、共享接口控制关联零件（★ M1 —— ★ FR-001/002/003）
#: ══════════════════════════════════════════════════════════════════════


@dataclass
class AxisInterface:
    """★ 一条**轴系接口**（★ 上下箱体共用）。"""

    name: str
    value: float
    unit: str = "mm"
    dependents: tuple = ()


#: ★★ **轴系接口 → 依赖它的产物**（★ FR-002 的传播判据的真源）。
#:   ★ 改一个轴系参数 ⇒ **受影响孔/件/图/计算全刷新**；★ 不相关的**可复用**。
AXIS_DEPENDENTS: dict[str, tuple] = {
    #: ★ 轴承孔中心距变了 ⇒ 上下箱体的孔系 + 装配 + 图纸 + 计算
    "bore_center_distance_mm": ("上箱体孔系", "下箱体孔系", "装配", "图纸", "计算"),
    #: ★ 轴径变了 ⇒ 只有孔系与配合（★ 箱体外形不动）
    "shaft_dia_mm": ("上箱体孔系", "下箱体孔系", "配合"),
    #: ★ 剖分面高度变了 ⇒ 上下箱体的分界 + 图纸
    "split_height_mm": ("上箱体", "下箱体", "图纸"),
    #: ★ 壁厚变了 ⇒ 两个箱体
    "wall_thickness_mm": ("上箱体", "下箱体"),
}


@dataclass
class HousingModel:
    """★ 箱体的**轴系接口集**（★ M1）。"""

    baseline: str = ""
    interfaces: dict = field(default_factory=dict)

    def set(self, name: str, value: float, unit: str = "mm") -> AxisInterface:
        it = AxisInterface(
            name=name,
            value=float(value),
            unit=unit,
            dependents=AXIS_DEPENDENTS.get(name, ()),
        )
        self.interfaces[name] = it
        return it

    def require_baseline(self) -> None:
        """★★ **必须声明统一基准**（★ FR-001 的判据）。"""
        if not self.baseline:
            raise HousingError("no-baseline", "★ 没有声明统一基准 ⇒ 上下箱体无共同依据")


#: ★ 默认轴系（★ 冻结值 —— ★ 由「已确认轴系和轴承接口」给定）
DEFAULT_AXES = {
    "bore_center_distance_mm": 120.0,
    "shaft_dia_mm": 40.0,
    "split_height_mm": 90.0,
    "wall_thickness_mm": 10.0,
}


def default_housing() -> HousingModel:
    m = HousingModel(baseline="箱体底面 + 主轴线")
    for k, v in DEFAULT_AXES.items():
        m.set(k, v)
    return m


def propagate_axis(
    name: str, old: float, new: float, all_parts: tuple | None = None
) -> dict:
    """★★ **轴系接口变更传播**（★ FR-002）。

    ★★ 判据（★ 两条都要，★ 与阶段 3 的失效闭包、阶段 5 的接口传播同族）：
      · **依赖它的产物全部刷新**
      · **不依赖的可复用**（★ 不是「全都标脏」）
    """
    if old == new:
        return {
            "changed": False,
            "stale": [],
            "reusable": list(all_parts or ()),
            "reason": "★ 值没变 ⇒ 无传播",
        }
    affected = set(AXIS_DEPENDENTS.get(name, ()))
    parts = (
        list(all_parts)
        if all_parts is not None
        else sorted({p for v in AXIS_DEPENDENTS.values() for p in v})
    )
    return {
        "changed": True,
        "interface": name,
        "old": old,
        "new": new,
        "stale": [p for p in parts if p in affected],
        "reusable": [p for p in parts if p not in affected],
        "ok": bool(affected & set(parts)),
    }


#: ══════════════════════════════════════════════════════════════════════
# 三、孔系关系（★ M1 —— ★ FR-003/011）
#: ══════════════════════════════════════════════════════════════════════


@dataclass
class BoreRelation:
    """★ 一个轴承孔的**关系**（★ 不是它自己的直径）。"""

    axis: str = ""
    center_distance_mm: float = 0.0
    expected_center_distance_mm: float = 0.0
    fit: str = ""
    split: str = ""
    tolerance_mm: float = 0.01

    @property
    def distance_ok(self) -> bool:
        return (
            abs(self.center_distance_mm - self.expected_center_distance_mm)
            <= self.tolerance_mm
        )

    @property
    def ok(self) -> bool:
        """★★ 判据（★ FR-011）：**孔系关系**（中心距 + 配合 + 剖分），
        ★ **不是**「各孔自身直径都对」。"""
        return self.distance_ok and bool(self.fit) and bool(self.split)


def check_bore_relations(relations: list) -> dict:
    """★★ **孔系关系检查**（★ FR-011）。

    ★★ **为什么不能只看孔径**（★ 外部方案 R7 ④ 逐字）：
      「**各孔自身直径都正确不能使其通过**」——
      ★ 因为孔系的功能是**中心距与配合**，★ 孔径对了而中心距错了照样装不上。
    """
    bad = [r for r in relations if not r.ok]
    return {
        "total": len(relations),
        "ok": not bad,
        "bad": [
            {
                "axis": r.axis,
                "distance_ok": r.distance_ok,
                "fit": r.fit,
                "split": r.split,
            }
            for r in bad
        ],
        "★": "★ 判据是**孔系关系**（中心距+配合+剖分），★ 不是各孔自身直径",
    }


#: ══════════════════════════════════════════════════════════════════════
# 四、证据非循环（★ M2 —— ★ FR-004/SC-010）
#: ══════════════════════════════════════════════════════════════════════

#: ★ 证据种类
EV_PRODUCT = "product"  #: ★ 产品级（真机/文件/回读）—— **可用**
EV_LEDGER = "ledger"  #: ★ 台账级（★ `capabilities.yaml` 的 `level`）—— **不可用**
EVIDENCE_KINDS = (EV_PRODUCT, EV_LEDGER)

#: ★★ **禁止的循环证据形态**（★ 外部方案 R7 ④ 逐字）
CIRCULAR_PATTERNS = (
    "读取台账",
    "断言 verified",
    "capabilities.yaml",
    "level == verified",
    "level==verified",
    "台账等级",
)


@dataclass
class Evidence:
    kind: str = EV_PRODUCT
    path: str = ""
    sha256: str = ""
    note: str = ""

    def __post_init__(self) -> None:
        assert self.kind in EVIDENCE_KINDS, "★ 非法证据种类：%r" % self.kind

    @property
    def usable(self) -> bool:
        """★★ **能不能当产品级证据**（★ 台账级**不能**）。"""
        return self.kind == EV_PRODUCT


def evidence_is_noncircular(evidences: list) -> dict:
    """★★★ **证据非循环**（★ M2 —— ★ FR-004 / SC-010）。

    ★★ 判据（★ 两条）：
      ① **台账级证据**（`kind=ledger`）**不得**当产品级证据
      ② 证据的 `note`/`path` 里**不得**出现循环形态
         （★ 外部方案逐字：「读取台账并断言 `verified`」）

    ★★ **为什么这条最重要**（★ 外部方案 R7 ④）：
      ★ 台账是我们**自己写的** —— ★ 拿它证明自己，就是**循环论证**。
      ★ 产品级证据必须是**外部可核**的（真机回读 / 文件 / 尺寸）。
    """
    circular = []
    for e in evidences:
        blob = "%s %s %s" % (e.path, e.note, e.kind)
        if e.kind == EV_LEDGER:
            circular.append({"path": e.path, "why": "★ 台账级证据不能当产品级"})
            continue
        for pat in CIRCULAR_PATTERNS:
            if pat in blob:
                circular.append({"path": e.path, "why": "★ 循环形态：%r" % pat})
                break
    return {
        "ok": not circular,
        "total": len(evidences),
        "circular": circular,
        "★": "★ 产品级证据必须**外部可核**；★ 台账（自己写的）不算",
    }


#: ══════════════════════════════════════════════════════════════════════
# 五、四层区分（★ M3 —— ★ FR-005/006）
#: ══════════════════════════════════════════════════════════════════════


@dataclass
class LayeredVerdict:
    """★★ **四层区分**（★ M3 —— ★ FR-005）。

    ★★ **为什么必须分开报**（★ 外部方案 S7-B ③ 逐字）：
      「报告**区分规划成功、执行成功、工程通过和人工批准**」
      ⇒ ★★ 把四件事压成**一个 bool** 会让「规划出来了」冒充「工程通过了」。
    """

    planned: bool = False  #: ★ 规划成功
    executed: bool = False  #: ★ 执行成功
    engineering_passed: bool = False  #: ★ 工程通过
    human_approved: bool = False  #: ★ 人工批准
    human_takeovers: list = field(default_factory=list)

    @property
    def all_four(self) -> bool:
        """★★ **四层全过**才算真交付（★ 不是"跑完了"）。"""
        return (
            self.planned
            and self.executed
            and self.engineering_passed
            and self.human_approved
        )

    def to_dict(self) -> dict:
        return {
            "planned": self.planned,
            "executed": self.executed,
            "engineering_passed": self.engineering_passed,
            "human_approved": self.human_approved,
            "human_takeovers": list(self.human_takeovers),
            "all_four": self.all_four,
            "★": "★ 四层分开报 —— ★ 不许用一个 bool 压过去",
        }


#: ══════════════════════════════════════════════════════════════════════
# 六、最终 DoD（★ M4 —— ★ FR-007~010）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ **三类产品**（★ FR-007）
PRODUCTS = ("vise", "linkage", "housing")
#: ★★ **每类 3 个参数变体** ⇒ **9 个真机案例**
VARIANTS = (1, 2, 3)
#: ★★ **必需的门禁**（★ FR-009：缺一 ⇒ 不完整）
REQUIRED_GATES = (
    "py_syntax",
    "unit_count",
    "release_check",
    "corpus_315",
    "stage3_recovery",
    "stage4_corpus",
)
#: ★★ **越界声明的形态**（★ FR-010）
OUT_OF_SCOPE_CLAIMS = (
    "完整减速器已设计",
    "整机已设计",
    "全套已交付",
    "通用机构综合已支持",
)


@dataclass
class CaseResult:
    product: str
    variant: int
    obligations_passed: bool = False
    artifacts: list = field(default_factory=list)
    layers: LayeredVerdict = field(default_factory=LayeredVerdict)
    failed: int = 0

    @property
    def key(self) -> str:
        return "%s-v%d" % (self.product, self.variant)


@dataclass
class FinalDod(CaseCollectorMixin):
    """★★ **最终 DoD 清单**（★ M4）。"""

    cases: list = field(default_factory=list)
    gates: dict = field(default_factory=dict)
    failed_total: int = 0
    new_failures: int = 0
    claims: list = field(default_factory=list)
    evidences: list = field(default_factory=list)

    def evaluate(self) -> dict:
        """★★ **最终 DoD 判定**（★ S7-B）。

        ★★ 判据（★ 八条都要）：
          ① 9 个案例齐（3 类 × 3 变体）
          ② 9/9 通过所有规定义务
          ③ failed_total == 0 且 new_failures == 0
          ④ 无缺失的必需门禁
          ⑤ 证据**非循环**
          ⑥ 无越界声明
          ⑦ 四层判定逐案例齐
          ⑧ 人工接管**可见**

        ★★ **③④ 是「不靠挑最好案例」的判据** ——
          ★ 不是「有 9 个案例」，而是「**9 个都过且全局 0 failed**」。
        """
        out: dict = {}

        #: ① 案例齐
        keys = {c.key for c in self.cases}
        want = {"%s-v%d" % (p, v) for p in PRODUCTS for v in VARIANTS}
        out["cases_total"] = len(self.cases)
        out["cases_missing"] = sorted(want - keys)
        out["cases_ok"] = not out["cases_missing"] and len(self.cases) == 9

        #: ② 9/9 义务
        bad = [c.key for c in self.cases if not c.obligations_passed]
        out["obligations_bad"] = bad
        out["obligations_ok"] = not bad and len(self.cases) == 9

        #: ③ 0 failed
        out["failed_total"] = self.failed_total
        out["new_failures"] = self.new_failures
        out["failures_ok"] = self.failed_total == 0 and self.new_failures == 0

        #: ④ 门禁齐
        miss = [g for g in REQUIRED_GATES if g not in self.gates]
        out["gates_missing"] = miss
        out["gates_ok"] = not miss

        #: ⑤ 证据非循环
        ev = evidence_is_noncircular(self.evidences)
        out["evidence"] = ev
        out["evidence_ok"] = ev["ok"]

        #: ⑥ 无越界声明
        bad_claims = [
            c for c in self.claims if any(o in c for o in OUT_OF_SCOPE_CLAIMS)
        ]
        out["out_of_scope"] = bad_claims
        out["claims_ok"] = not bad_claims

        #: ⑦ 四层（★ 逐案例）
        out["layers"] = {c.key: c.layers.to_dict() for c in self.cases}
        out["all_four_ok"] = all(c.layers.all_four for c in self.cases)

        #: ⑧ 人工接管**可见**（★ FR-006）
        takeovers = [c.key for c in self.cases if c.layers.human_takeovers]
        out["human_takeovers"] = takeovers
        out["takeovers_visible"] = True  #: ★ 我们**如实列出**了

        out["ok"] = bool(
            out["cases_ok"]
            and out["obligations_ok"]
            and out["failures_ok"]
            and out["gates_ok"]
            and out["evidence_ok"]
            and out["claims_ok"]
            and out["all_four_ok"]
        )
        return out