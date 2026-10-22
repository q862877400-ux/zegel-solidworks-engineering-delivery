"""★ EC06 装配与机构 —— 约束图 / 干涉扫描 / 公差链映射（★ 离线部分）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC06**（★ T01–T08 逐字）
#         `specs/308-ec06-assembly-and-mechanism/spec.md`
#         `scripts/engineering/rules.py`（★ EC02 的尺寸链 —— ★ **复用**）
#         `scripts/engineering/jobs.py`（★ EC04 的 `VersionBinding` —— ★ **复用**）
# 定位:   ★ **EC06** 的离线部分。★★★ 计划 §5 EC06 验收逐字：「★ 目标自由度与**实际一致
#           **；★ 边界位姿**无未解释干涉**； ★ **错误配合/错轴向位置必被检测**；★ **无法
#           证明全域的部分以 `coverage`/`unknown` 记录**」
# 官方依据: 不适用（本仓的装配分析层 —— ★ **不调 SolidWorks API**）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件（★ **纯离线** —— ★ 真机部分在 `output/` 的探针里）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "DofVerdict",
    "MateKind",
    "Component",
    "Mate",
    "ConstraintGraph",
    "InterferenceScan",
    "ToleranceChain",
    "MaintenanceCheck",
    "CASE_LIBRARY",
    "build_case",
    "ASSEMBLY_TOOLS",
    "bom_traceability",
    "replacement_stability",
]


# ══════════════════════════════════════════════════════════════════════
# 一、★★★★★ 自由度判定（★ EC06-T02 —— ★ 四类**分开**）
# ══════════════════════════════════════════════════════════════════════


class DofVerdict:
    """★★ 约束状态（★ 逐字承 EC06-T02：★「★ 区分**欠约束、冗余、过约束和预期运动自由度**」）。

    ★★★ **四类必须分开** —— ★ 把它们混成「约束不够/太多」就丢了诊断力 ✗
    """

    UNDER_CONSTRAINED = "under_constrained"  #: ★ 欠约束（★ 还能动，★ 但**没预期**）
    REDUNDANT = "redundant"  #: ★ 冗余（★ 重复约束，★ **不冲突**）
    OVER_CONSTRAINED = "over_constrained"  #: ★ 过约束（★ 冲突）
    EXPECTED_MOTION = "expected_motion"  #: ★ ★★ **预期运动**（★ **有意保留**的自由度）
    FULLY_CONSTRAINED = "fully_constrained"  #: ★ 完全约束

    ALL = (
        UNDER_CONSTRAINED,
        REDUNDANT,
        OVER_CONSTRAINED,
        EXPECTED_MOTION,
        FULLY_CONSTRAINED,
    )
    #: ★★ **可放行的**（★ 完全约束 或 有意保留的运动）
    RELEASING = (FULLY_CONSTRAINED, EXPECTED_MOTION)


class MateKind:
    """★ 配合种类（★ 与工具面对齐 —— ★ 铁律 1：★ 不另建一套）。"""

    COINCIDENT = "coincident"
    CONCENTRIC = "concentric"
    DISTANCE = "distance"
    PARALLEL = "parallel"
    PERPENDICULAR = "perpendicular"

    ALL = (COINCIDENT, CONCENTRIC, DISTANCE, PARALLEL, PERPENDICULAR)
    #: ★★ **每个配合消去的自由度数**（★ 平面/回转的常见口径）
    REMOVES = {
        COINCIDENT: 3,  #: ★ 面贴合：★ 1 平动 + 2 转动
        CONCENTRIC: 4,  #: ★ 同轴：★ 2 平动 + 2 转动
        DISTANCE: 1,  #: ★ 距离：★ 1 平动
        PARALLEL: 2,  #: ★ 平行：★ 2 转动
        PERPENDICULAR: 2,  #: ★ 垂直：★ 2 转动
    }


@dataclass
class Component:
    """★ 组件（★ 带**是否地件** —— ★ EC06-T01 逐字）。"""

    name: str
    is_ground: bool = False  #: ★★ **地件**（★ 固定不动）
    #: ★★ **组件自己的自由度**（★ 一个自由刚体在 3D 是 6）
    dof: int = 6


@dataclass
class Mate:
    """★ 配合（★ 带**轴向**信息 —— ★ 「错轴向位置必被检测」靠它）。"""

    kind: str
    a: str
    b: str
    axis: str = ""  #: ★ 轴向（★ 如 `"X"` / `"Y"` / `"Z"`）
    value: float | None = None  #: ★ 距离类配合的数值
    #: ★★ **是不是冗余的**（★ 由调用方判 —— ★ 或由本模块的图检查判）
    redundant: bool = False
    conflicts_with: tuple = ()


@dataclass
class ConstraintGraph:
    """★★★★ **约束图**（★ EC06-T02 的核心）。

    ★★★ **判据（★ 逐字承验收）**：★「★ 目标自由度与**实际一致**；★ **错误配合/错轴向位置必被检测**」。
    """

    components: list = field(default_factory=list)
    mates: list = field(default_factory=list)
    #: ★★★ **目标自由度**（★ 由调用方声明 —— ★ **不是算出来再倒推**）
    target_dof: int | None = None
    #: ★★ **预期运动**（★ 逐条：★ 哪个组件、沿什么动、★ **为什么是有意的**）
    expected_motions: list = field(default_factory=list)

    def total_dof(self) -> int:
        """★ 自由度 = ★ Σ(组件自由度) − Σ(配合消去的)（★ 地件算 0）。"""
        base = sum(c.dof for c in self.components if not c.is_ground)
        removed = 0
        for m in self.mates:
            if m.redundant:
                continue  #: ★★ **冗余的不重复消**（★ 那是「冗余」的定义）
            removed += MateKind.REMOVES.get(m.kind, 0)
        return max(0, base - removed)

    def verdict(self) -> dict:
        """★★★★★ **四类判定**（★ 逐字承 EC06-T02）。

        ★★ 顺序（★ 保守优先）：
          ① ★ **过约束**（★ 有冲突）⇒ `over_constrained`
          ② ★ **冗余**（★ 有冗余但无冲突）⇒ `redundant`
          ③ ★ **预期运动**（★ 自由度 > 0 且**逐条标注了**）⇒ `expected_motion`
          ④ ★ **欠约束**（★ 自由度 > 0 但**没标注**）⇒ `under_constrained`
          ⑤ ★ 自由度 0 ⇒ `fully_constrained`
        """
        conflicts = [m for m in self.mates if m.conflicts_with]
        if conflicts:
            return {
                "verdict": DofVerdict.OVER_CONSTRAINED,
                "dof": self.total_dof(),
                "conflicts": [
                    {"kind": m.kind, "a": m.a, "b": m.b, "with": list(m.conflicts_with)}
                    for m in conflicts
                ],
                "releasing": False,
                "reason": "★★ 有**冲突**的配合 ⇒ 过约束",
            }
        redundants = [m for m in self.mates if m.redundant]
        if redundants:
            return {
                "verdict": DofVerdict.REDUNDANT,
                "dof": self.total_dof(),
                "redundant": [{"kind": m.kind, "a": m.a, "b": m.b} for m in redundants],
                "releasing": False,
                "reason": "★ 有**冗余**配合（★ 不冲突但重复）⇒ 应去掉多余的那条",
            }
        dof = self.total_dof()
        if dof > 0:
            if len(self.expected_motions) >= dof:
                return {
                    "verdict": DofVerdict.EXPECTED_MOTION,
                    "dof": dof,
                    "expected": list(self.expected_motions),
                    "releasing": True,
                    "reason": "★ 自由度 %d 个，★ **已逐条标注为有意保留**" % dof,
                }
            return {
                "verdict": DofVerdict.UNDER_CONSTRAINED,
                "dof": dof,
                "expected_count": len(self.expected_motions),
                "releasing": False,
                "reason": (
                    "★★ 还有 %d 个自由度**没标注** ⇒ 那是「没锁住」不是「有意保留」"
                    % (dof - len(self.expected_motions))
                ),
            }
        return {
            "verdict": DofVerdict.FULLY_CONSTRAINED,
            "dof": 0,
            "releasing": True,
            "reason": "★ 完全约束",
        }

    def target_matches_actual(self) -> dict:
        """★★★★ **目标自由度与实际一致？**（★ 逐字承验收）。

        ★★ 判据：★ `target_dof` **必须**等于算出来的自由度。
        """
        actual = self.total_dof()
        if self.target_dof is None:
            return {
                "ok": False,
                "reason": "★★ **没声明目标自由度** ⇒ 无法判「一致」",
                "actual": actual,
                "target": None,
            }
        return {
            "ok": self.target_dof == actual,
            "actual": actual,
            "target": self.target_dof,
            "reason": (
                "★ 目标 %d = 实际 %d ✓" % (self.target_dof, actual)
                if self.target_dof == actual
                else "★★ 目标 %d ≠ 实际 %d ⇒ 不一致" % (self.target_dof, actual)
            ),
        }

    def axis_errors(self) -> list:
        """★★★★★ **错轴向位置检测**（★ 逐字承验收：★「★ **错误配合/错轴向位置必被检测**」）。

        ★★ 判据：★ 同一个组件对之间若有**多条**配合，★ 它们的**轴向必须一致**
          （★ 除非是 `PARALLEL`/`PERPENDICULAR` 那类**本身表达轴关系**的）。
        """
        by_pair: dict = {}
        for m in self.mates:
            if m.kind in (MateKind.PARALLEL, MateKind.PERPENDICULAR):
                continue  #: ★ 那两类**本身**就是轴关系
            key = tuple(sorted((m.a, m.b)))
            by_pair.setdefault(key, []).append(m)
        bad = []
        for key, items in by_pair.items():
            axes = {m.axis for m in items if m.axis}
            if len(axes) > 1:
                bad.append(
                    {
                        "pair": list(key),
                        "axes": sorted(axes),
                        "reason": "★★ 同一对组件上有多条**轴向不一致**的配合",
                    }
                )
        return bad


# ══════════════════════════════════════════════════════════════════════
# 二、★★★★★ 干涉扫描（★ EC06-T04 —— ★ **有限采样不冒充全域**）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class InterferenceScan:
    """★★★★ **位置扫描 + 自适应局部加密**（★ EC06-T04 逐字）。

    ★★★ **验收（★ 逐字）**：★「★ 边界位姿**无未解释干涉**」+ ★
      「★★★ **无法证明全域的部分以 `coverage`/`unknown` 记录**」。

    ★★★ **本类最要紧的一条**：★ **有限采样 ≠ 连续全域证明** ——
      ★★ 所以必须记 `coverage`，★ **且不许把 `unknown` 说成「无干涉」** ✗
    """

    positions_scanned: int = 0
    interferences: list = field(default_factory=list)
    #: ★★★ **已加密的区间**（★ 自适应局部加密的记录）
    refined_intervals: list = field(default_factory=list)
    #: ★★ **是否做到了全域证明**（★ **几乎永远是 False** —— ★ 除非解析可证）
    is_full_domain_proof: bool = False
    #: ★★ **未覆盖的区间**（★ 如实记 —— ★ 不假装覆盖了）
    uncovered: list = field(default_factory=list)

    def coverage(self) -> float:
        """★★ **覆盖率**（★ 已扫描 / (已扫描 + 未覆盖)）。

        ★★ 分母为 0 ⇒ ★ 返回 **0.0**（★ 不是 1.0 —— ★ **没扫就没有覆盖**）。
        """
        total = self.positions_scanned + len(self.uncovered)
        if total <= 0:
            return 0.0
        return self.positions_scanned / total

    def verdict(self) -> dict:
        """★★★★★ **干涉扫描判定**（★ 逐字承验收）。

        ★★ 三种结论：
          · ★ **有干涉** ⇒ `interference`（★ 且必须**解释**或记 `unknown`）
          · ★★ **无干涉但覆盖率 < 1** ⇒ `unknown`（★ **不许说「无干涉」**）
          · ★ 无干涉 + 全域证明 ⇒ `pass`
        """
        if self.interferences:
            return {
                "verdict": "interference",
                "count": len(self.interferences),
                "interferences": list(self.interferences),
                "coverage": self.coverage(),
                "releasing": False,
                "reason": "★★ 检出干涉 ⇒ 必须**解释**或记 `unknown`（★ 不能当无干涉）",
            }
        cov = self.coverage()
        if not self.is_full_domain_proof:
            return {
                "verdict": "unknown",
                "coverage": cov,
                "releasing": False,
                "reason": (
                    "★★★ 无检出干涉，★ 但**没有全域证明**（★ 覆盖率 %.2f）"
                    "⇒ ★ **有限采样不能冒充连续全域** ⇒ 记 `unknown`" % cov
                ),
                "uncovered": list(self.uncovered),
            }
        return {
            "verdict": "pass",
            "coverage": 1.0,
            "releasing": True,
            "reason": "★ 无干涉 **且** 有全域证明",
        }

    def refine(self, interval: str, why: str) -> None:
        """★★ **自适应局部加密**（★ EC06-T04 逐字：★「★ 位置扫描 + **自适应局部加密**」）。"""
        self.refined_intervals.append({"interval": interval, "why": why})


# ══════════════════════════════════════════════════════════════════════
# 三、★★★★ 公差链映射（★ EC06-T03）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class ToleranceChain:
    """★★★ **基准与配合链 → 公差链**（★ EC06-T03 逐字：★「★ 基准与配合链映射到公差链；
    ★ **极限法与统计法各自声明假设**」）。

    ★★★ **复用 EC02**（★ 铁律 1）—— ★ **不另写一套尺寸链算法** ✓
    """

    name: str
    links: list = field(default_factory=list)  #: ★ `[(名义值, 公差)]`
    method: str = "worst_case"  #: ★ `worst_case` / `rss`
    #: ★★ **统计假设**（★ 用 RSS 时**必须**声明 —— ★ 承 EC02 的 V5）
    statistical_basis: str = ""

    def compute(self) -> dict:
        """★★★ **算公差链**（★ 转给 EC02 的两个算法 —— ★ **不重复实现**）。"""
        from . import rules as R

        if self.method == "rss":
            return R.tolerance_stack_rss(
                self.links, distribution=self.statistical_basis
            )
        return R.tolerance_stack_worst_case(self.links)


# ══════════════════════════════════════════════════════════════════════
# 四、★★★★ 维护与装拆（★ EC06-T05）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class MaintenanceCheck:
    """★★ **维护可达性**（★ EC06-T05 逐字：★「★ 验证**紧固件可达、装拆次序、轴承安装、润滑、
    传感器调整和维护空间**」）。"""

    items: list = field(default_factory=list)

    def add(self, kind: str, ok: bool, note: str = "") -> None:
        """★ 登记一项（★ 逐项**可判** —— ★ 不是「都行」）。"""
        self.items.append({"kind": kind, "ok": bool(ok), "note": note})

    def verdict(self) -> dict:
        """★★ **判定**（★ 有任一不满足 ⇒ 不通过 —— ★ 且**逐条具名**）。"""
        bad = [i for i in self.items if not i["ok"]]
        if not self.items:
            return {"ok": False, "reason": "★★ 一项都没检查 ⇒ 不算通过", "items": []}
        return {
            "ok": not bad,
            "failed": bad,
            "items": list(self.items),
            "reason": (
                "★ 全部 %d 项满足" % len(self.items)
                if not bad
                else "★★ %d 项不满足：%s" % (len(bad), [i["kind"] for i in bad])
            ),
        }


# ══════════════════════════════════════════════════════════════════════
# 五、★★★★ 两个受控案例（★ EC06-T06 —— ★ 双导杆滑台 / 轴承支撑轴系）
# ══════════════════════════════════════════════════════════════════════

#: ★★★ **两个受控案例的冻结参数**（★ EC06-T06 逐字：★「★ 建立简单**双导杆滑台/轴承支撑轴
#: 系**
#:   两类案例；★ **齿轮列为附加挑战**」）
CASE_LIBRARY: dict = {
    "double_rod_slide": {
        "name": "★ 双导杆滑台",
        #: ★★ **自由度算法**（★ 本模块口径）：★ `6 − CONCENTRIC(4) − DISTANCE(1) = 1` ✓
        #:   ★★★ **如实说明**：★ 这是**简化口径**（★ 常见平面/回转算法）—— ★ 它**不区分**
        #:     「留的是平动还是转动」⇒ ★ 两个案例的**自由度都是 1**，★ 而语义不同 ✓
        "components": (("base", True), ("slider", False)),
        "mates": (
            ("concentric", "base", "slider", "X"),
            ("distance", "base", "slider", "X"),
        ),
        #: ★★ **目标自由度 = 1**（★ 滑台只能沿 X 移）—— ★ 那是**功能要求**
        "target_dof": 1,
        "expected_motions": ("★ 沿 X 滑移（★ 行程由 EC07 冻结节拍决定）",),
        "why": (
            "★ 双导杆**抗扭转**（★ 单导杆会转）⇒ 只保留 1 个自由度；"
            "★ 简化口径：★ 同轴消 4 + 轴向定位消 1 = 5 ⇒ 留 1"
        ),
    },
    "bearing_supported_shaft": {
        "name": "★ 轴承支撑轴系",
        "components": (("base", True), ("shaft", False)),
        "mates": (
            ("concentric", "base", "shaft", "X"),
            ("distance", "base", "shaft", "X"),
        ),
        #: ★★ **目标自由度 = 1**（★ 轴只能绕 X 转）
        "target_dof": 1,
        "expected_motions": ("★ 绕 X 转动（★ 那是**传动要求**）",),
        "why": (
            "★ 轴承支撑 ⇒ 保留 1 个转动自由度；"
            "★ 简化口径：★ 同轴消 4 + 轴向定位消 1 = 5 ⇒ 留 1"
        ),
    },
}


def build_case(case_id: str) -> ConstraintGraph:
    """★★★ **从冻结参数建一个受控案例**（★ EC06-T06）。

    ★★ 依据（★ EC06-T06 逐字）：★「★ 建立简单**双导杆滑台/轴承支撑轴系**两类案例」。
    """
    c = CASE_LIBRARY.get(case_id)
    if c is None:
        raise KeyError("★ 未知案例 %r（★ 有 %r）" % (case_id, sorted(CASE_LIBRARY)))
    comps = [Component(name=n, is_ground=g) for n, g in c["components"]]
    mates = [Mate(kind=k, a=a, b=b, axis=ax) for k, a, b, ax in c["mates"]]
    return ConstraintGraph(
        components=comps,
        mates=mates,
        target_dof=c["target_dof"],
        expected_motions=list(c["expected_motions"]),
    )


# ══════════════════════════════════════════════════════════════════════
# 六、★★★★ BOM 与替换件（★ EC06-T07 —— ★ **复用工具面**，★ 不另建）
# ══════════════════════════════════════════════════════════════════════

#: ★★ **工具面已有的装配相关工具**（★ EC06-T07 逐字点名的：★「★ 组件配置、**BOM**、
#:   持久引用、**替换件**和参数修改后的配合稳定性」）
ASSEMBLY_TOOLS = {
    "bom_read": "solidworks_collect_assembly_bom",  #: ★ 读 BOM
    "bom_export": "solidworks_export_assembly_bom",  #: ★ 导出 BOM
    "component_list": "solidworks_assembly_list_components",  #: ★ 组件清单
    "replace_component": "solidworks_assembly_replace_component",  #: ★ **替换件**
    "config_inspect": "solidworks_config_inspect",  #: ★ 组件配置
    "interference": "solidworks_assembly_check_interference",  #: ★ 干涉
}


def bom_traceability(rows: list) -> dict:
    """★★★ **BOM 可追溯性**（★ EC06-T07 逐字：★「★ 检查组件配置、**BOM**、持久引用、
    **替换件**和参数修改后的**配合稳定性**」）。

    ★★ 判据：★ 每一行必须带**可指认的字段**（★ 否则 BOM 是一张纸）。
    """
    REQUIRED = ("name", "quantity", "file_path")
    bad = []
    for i, r in enumerate(rows or []):
        miss = [k for k in REQUIRED if k not in r]
        if miss:
            bad.append({"index": i, "missing": miss})
    return {
        "ok": bool(rows) and not bad,
        "rows": len(rows or []),
        "bad_rows": bad,
        "required_fields": list(REQUIRED),
        "reason": (
            "★ %d 行全部可追溯" % len(rows)
            if rows and not bad
            else ("★★ 空 BOM ⇒ 不算通过" if not rows else "★★ %d 行缺字段" % len(bad))
        ),
    }


def replacement_stability(before: dict, after: dict, *, keys: tuple = ()) -> dict:
    """★★★★ **替换件后的配合稳定性**（★ EC06-T07 逐字）。

    ★★ 判据：★ 替换后**配合数**与**自由度**都**不能变**（★ 变了就是「换件换坏了」）。
    """
    fields = keys or ("mate_count", "total_dof", "verdict")
    diffs = {}
    for k in fields:
        if before.get(k) != after.get(k):
            diffs[k] = {"before": before.get(k), "after": after.get(k)}
    return {
        "ok": not diffs,
        "diffs": diffs,
        "reason": (
            "★ 替换后 %r 全未变 ⇒ 配合稳定" % list(fields)
            if not diffs
            else "★★ 替换后这些变了：%r" % sorted(diffs)
        ),
    }
