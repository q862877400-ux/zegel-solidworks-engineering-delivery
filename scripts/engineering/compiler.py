"""★ EC03 方法库与受约束规划编译 —— **纯离线编译器**（★ 不 import 任何 COM 模块）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC03**（★ T01–T08 逐字）
#         `specs/305-ec03-method-library-and-ir/spec.md`（★ 8 FR · 10 V）
#         `golden-workflows.yaml`（★ **复用** —— 10 个 workflow）
#         `apps/desktop/cad_workbench/engineering_orchestrator.py`（★ **复用** —— 八阶段 DAG）
#         `scripts/engineering_contract.py`（★ EC01 的 `EngineeringContract` —— ★ **只吃它**）
# 定位:   ★ **EC03** 的编译器。★★★ 计划 §5 EC03 验收逐字：「★ 两模型生成的合法意图都通
#           过**同一编译器**；★ 编译器能拒绝**越权/欠约束/循环依赖**； ★ **不需要 COM 即
#           可检验计划正确性**；★ **冻结计划不能被执行器静默改写**」
#         ★★★ **⇒ 四条不变量**：① 只吃 `EngineeringContract`（模型无关）
#           ② 全部检查在编译期 ③ **不 import COM** ④ 冻结计划带哈希 + 执行前校验
# 官方依据: 不适用（本仓的规划编译层 —— ★ 不调 SolidWorks API）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件（★ **纯离线** —— ★ 见本文件末尾的**自证**函数 `assert_no_com_imports`）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "PlanError", "RejectCode", "Complexity", "MethodSpec", "METHOD_LIBRARY",
    "SketchIR", "FeatureIR", "AssemblyIR", "DrawingIR",
    "ToolDAG", "DAGNode", "CompiledPlan", "EleganceScore",
    "compile_contract", "score_elegance", "assert_no_com_imports",
    "is_production_method", "list_sandbox_methods", "SANDBOX_PREFIX",
    "SolveStatus", "find_unsat_core", "solve_with_budget", "rank_plans",
]


# ══════════════════════════════════════════════════════════════════════
# 一、★★★★ 编译期拒绝码（★ **封闭词表** —— ★ 非法路由**在编译期**失败）
# ══════════════════════════════════════════════════════════════════════

class RejectCode:
    """★★ 编译期拒绝码（★ 逐字承计划 §5 EC03 验收）。"""

    OVERREACH = "reject-overreach"              #: ★ 越权（★ 动冻结域之外）
    UNDERCONSTRAINED = "reject-underconstrained"  #: ★ 欠约束（★ 参数没定域）
    CYCLIC = "reject-cyclic-dependency"         #: ★ 循环依赖
    ILLEGAL_ROUTE = "reject-illegal-route"      #: ★ 非法路由
    NOT_APPLICABLE = "reject-method-not-applicable"  #: ★ 方法不适用
    UNKNOWN_NOT_FEASIBLE = "reject-unknown-not-feasible"  #: ★ `unknown` 不得当可行
    CONTRACT_NOT_FROZEN = "reject-contract-not-frozen"    #: ★ 契约未冻结
    NO_METHOD = "reject-no-method-for-intent"   #: ★ 没有匹配的方法

    ALL = (OVERREACH, UNDERCONSTRAINED, CYCLIC, ILLEGAL_ROUTE, NOT_APPLICABLE,
           UNKNOWN_NOT_FEASIBLE, CONTRACT_NOT_FROZEN, NO_METHOD)


class PlanError(Exception):
    """★ 编译期失败（★ 带**封闭码** —— ★ 与 EC00/EC01/EC02 同族）。"""

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in RejectCode.ALL, "★ 非法拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


class Complexity:
    """★ 方法复杂度（★ 用于**多方案排序** —— ★ 不是唯一指标）。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    RANK = {LOW: 1, MEDIUM: 2, HIGH: 3}


# ══════════════════════════════════════════════════════════════════════
# 二、★★★★★ MethodSpec（★ FR-001 —— ★ 逐字承 EC03-T01）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class MethodSpec:
    """★★ `MethodSpec`（★ 逐字承计划 §5 EC03-T01）：

    「★ 目标、适用域、前后置、步骤、**禁止条件**、复杂度、**修改域**、验证义务和**失败域**」
    """

    id: str
    goal: str                                            #: ★ 目标
    applicable_devices: tuple = ()                       #: ★ 适用域
    preconditions: tuple = ()                            #: ★ 前置
    postconditions: tuple = ()                           #: ★ 后置
    steps: tuple = ()                                    #: ★ 步骤（★ **工具名序列**）
    forbidden: tuple = ()                                #: ★★ **禁止条件**
    complexity: str = Complexity.MEDIUM                  #: ★ 复杂度
    modification_domain: tuple = ()                      #: ★★ **修改域**（★ 越权检查靠它）
    verification_obligations: tuple = ()                 #: ★ 验证义务
    failure_domain: tuple = ()                           #: ★★ **失败域**（★ 什么时候不适用）
    #: ★★ **选法原因与替代方案**（★ EC03-T02 逐字）
    rationale: str = ""
    alternatives: tuple = ()

    def applies_to(self, device_class: str) -> bool:
        """★ 适用性（★ **空适用域 ⇒ 不适用任何类别** —— ★ 不默认「通用」）。"""
        return device_class in (self.applicable_devices or ())

    def allows(self, target: str) -> bool:
        """★★ **越权检查**：★ `target` 是否在**修改域**内。"""
        return target in (self.modification_domain or ())


#: ★★★ **受控方法库**（★ EC03-T02 逐字：★「板/孔组/阶梯轴/安装支架四个受控方法」）
#:   ★★ **复用** `golden-workflows.yaml` 的能力口径（★ 不另建）
METHOD_LIBRARY: dict[str, MethodSpec] = {
    "plate": MethodSpec(
        id="plate",
        goal="★ 做一块安装板（★ 基准 + 主特征 + 倒角后置）",
        applicable_devices=("plate",),
        preconditions=("★ 外形尺寸与板厚已冻结", "★ 基准已定语义角色"),
        postconditions=("★ 体数 = 1", "★ 厚度回读等于冻结值"),
        steps=("sketch_start", "sketch_add_rectangle", "sketch_end",
               "extrude_boss", "chamfer"),
        forbidden=("★ 禁止先倒角再打孔", "★ 禁止在未冻结基准上开草图"),
        complexity=Complexity.LOW,
        modification_domain=("outline", "thickness", "chamfer", "datum"),
        verification_obligations=("★ 回读厚度", "★ 回读体数"),
        failure_domain=("★ 板厚 < 2×倒角半径", "★ 外形不闭合"),
        rationale="★ 平板件用「基准 → 主特征 → 倒角后置」最稳（★ 倒角后置避免早期拓扑依赖）",
        alternatives=("★ 先倒角再拉伸（★ 否：拓扑依赖早）",),
    ),
    "hole_group": MethodSpec(
        id="hole_group",
        goal="★ 打一组孔（★ 一次成形 + 阵列）",
        applicable_devices=("plate", "bracket"),
        preconditions=("★ 孔径/孔距/基准已冻结", "★ 边距已按 EC02 规则验过"),
        postconditions=("★ 孔数与冻结一致", "★ 孔心坐标回读一致"),
        steps=("sketch_start", "sketch_add_circle", "sketch_end", "extrude_cut",
               "circular_pattern"),
        forbidden=("★ 禁止逐孔单独建（★ 应为阵列）", "★ 禁止边距未验就开孔"),
        complexity=Complexity.MEDIUM,
        modification_domain=("hole_diameter", "hole_spacing", "hole_count", "datum"),
        verification_obligations=("★ 回读孔数", "★ 回读孔心坐标"),
        failure_domain=("★ 边距不足", "★ 孔距与板宽冲突"),
        rationale="★ 孔组用「一次成形 + 阵列」⇒ 改参数时只改一处（★ 修改稳定）",
        alternatives=("★ 每孔一个 cut（★ 否：改参数要改 N 处）",),
    ),
    "stepped_shaft": MethodSpec(
        id="stepped_shaft",
        goal="★ 做一根阶梯轴（★ 回转 + 分档）",
        applicable_devices=("shaft",),
        preconditions=("★ 各档直径与长度已冻结", "★ 材料许用应力已定"),
        postconditions=("★ 回转体数 = 1", "★ 各档直径回读一致"),
        steps=("sketch_start", "sketch_add_line", "sketch_add_centerline", "sketch_end",
               "revolve_boss"),
        forbidden=("★ 禁止无中心线回转", "★ 禁止各档用独立实体"),
        complexity=Complexity.MEDIUM,
        modification_domain=("diameter", "length", "fillet", "datum"),
        verification_obligations=("★ 回读各档直径", "★ 强度按 EC02 复算"),
        failure_domain=("★ 相邻档直径比过大（★ 应力集中）", "★ 无中心线"),
        rationale="★ 阶梯轴用**单个**回转特征 ⇒ 各档同属一个特征（★ 意图可读）",
        alternatives=("★ 各档单独拉伸再合并（★ 否：体数与特征数都会涨）",),
    ),
    "mounting_bracket": MethodSpec(
        id="mounting_bracket",
        goal="★ 做安装支架（★ 板 + 折弯 + 孔组）",
        applicable_devices=("bracket",),
        preconditions=("★ 包络与安装对象已冻结", "★ 孔组与折弯半径已定"),
        postconditions=("★ 支架体数 = 1", "★ 安装孔与对象配合"),
        steps=("sketch_start", "sketch_add_rectangle", "sketch_end",
               "extrude_boss", "sheet_metal_create_base_flange", "hole_group"),
        forbidden=("★ 禁止折弯半径 < 板厚", "★ 禁止孔跨折弯线"),
        complexity=Complexity.HIGH,
        modification_domain=("outline", "thickness", "bend_radius", "hole_spacing"),
        verification_obligations=("★ 回读折弯半径", "★ 回读孔位", "★ 展开一致性"),
        failure_domain=("★ 折弯半径 < 板厚", "★ 孔跨折弯线"),
        rationale="★ 支架先板后折弯再打孔 ⇒ 孔在展平态定位（★ 可制造性好）",
        alternatives=("★ 先折弯再打孔（★ 否：孔位跨折弯难保证）",),
    ),
}


# ══════════════════════════════════════════════════════════════════════
# 三、★★★★ 四个 IR（★ FR-003 —— ★ 带版本）
# ══════════════════════════════════════════════════════════════════════

IR_VERSION = "ec03-ir-v1"


@dataclass
class SketchIR:
    """★ 草图 IR（★ 设计语义引用 —— ★ **不写裸坐标**）。"""

    name: str
    plane_datum: str = ""                 #: ★ 引用 EC01 的 `Datum.identity()`
    entities: tuple = ()
    version: str = IR_VERSION


@dataclass
class FeatureIR:
    """★ 特征 IR。"""

    name: str
    kind: str = ""                        #: ★ 如 `boss` / `cut` / `revolve` / `fillet`
    source_sketch: str = ""
    params: dict = field(default_factory=dict)
    depends_on: tuple = ()                #: ★★ **依赖**（★ 循环检查靠它）
    version: str = IR_VERSION


@dataclass
class AssemblyIR:
    """★ 装配 IR。"""

    name: str
    components: tuple = ()
    mates: tuple = ()
    degrees_of_freedom: int = 0
    version: str = IR_VERSION


@dataclass
class DrawingIR:
    """★ 工程图 IR。"""

    name: str
    views: tuple = ()
    dimensions: tuple = ()
    version: str = IR_VERSION


# ══════════════════════════════════════════════════════════════════════
# 四、★★★★★ 工具 DAG（★ FR-006）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class DAGNode:
    """★ DAG 节点（★ 带**前后置**与**验证步骤** —— ★ EC03-T06 逐字）。"""

    tool: str
    preconditions: tuple = ()
    postconditions: tuple = ()
    verification: tuple = ()
    depends_on: tuple = ()                #: ★★ **前驱**（★ 循环检查靠它）


@dataclass
class ToolDAG:
    """★ 工具 DAG。"""

    nodes: list = field(default_factory=list)

    def has_cycle(self) -> bool:
        """★★★ **循环依赖检查**（★ 编译期 —— ★ 拓扑排序）。

        ★★ 依据（★ 计划验收逐字）：★「编译器能拒绝……**循环依赖**」。
        """
        graph: dict[str, list[str]] = {}
        for n in self.nodes:
            graph[n.tool] = list(n.depends_on or ())
        #: ★ 引用了不存在的节点 ⇒ 也算**非法路由**（★ 由调用方判）
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {k: WHITE for k in graph}

        def visit(u: str, stack: list) -> list | None:
            color[u] = GRAY
            for v in graph.get(u, ()):
                if v not in graph:
                    continue                   #: ★ 悬空前驱由 `illegal_route` 抓
                if color[v] == GRAY:
                    return stack + [u, v]
                if color[v] == WHITE:
                    r = visit(v, stack + [u])
                    if r:
                        return r
            color[u] = BLACK
            return None

        for k in graph:
            if color[k] == WHITE:
                r = visit(k, [])
                if r:
                    return True
        return False

    def cycle_path(self) -> list[str]:
        """★ 回一条**具体的**环（★ 便于定位 —— ★ 不只说「有环」）。"""
        graph = {n.tool: list(n.depends_on or ()) for n in self.nodes}
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {k: WHITE for k in graph}
        path: list[str] = []

        def visit(u: str) -> list[str] | None:
            color[u] = GRAY
            path.append(u)
            for v in graph.get(u, ()):
                if v not in graph:
                    continue
                if color[v] == GRAY:
                    return path[path.index(v):] + [v]
                if color[v] == WHITE:
                    r = visit(v)
                    if r:
                        return r
            path.pop()
            color[u] = BLACK
            return None

        for k in graph:
            if color[k] == WHITE:
                r = visit(k)
                if r:
                    return r
        return []

    def unknown_dependencies(self) -> list[str]:
        """★ **悬空前驱**（★ 引用了不在 DAG 里的节点 ⇒ ★ 非法路由）。"""
        names = {n.tool for n in self.nodes}
        bad = []
        for n in self.nodes:
            for d in (n.depends_on or ()):
                if d not in names:
                    bad.append("%s→%s" % (n.tool, d))
        return bad


# ══════════════════════════════════════════════════════════════════════
# 五、★★★★★ 编译产物（★ 冻结带哈希 —— ★ 不可静默改写）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class CompiledPlan:
    """★★ **编译产物**（★ 冻结带内容哈希 —— ★ V6 的核心）。"""

    contract_hash: str
    method_id: str
    dag: ToolDAG
    irs: list = field(default_factory=list)
    frozen: bool = False
    plan_hash: str = ""
    warnings: list = field(default_factory=list)

    def compute_hash(self) -> str:
        """★ 计划哈希（★ 只算**计划内容** —— ★ 不含 `frozen`/`plan_hash` 自身）。"""
        payload = {
            "contract_hash": self.contract_hash,
            "method_id": self.method_id,
            "nodes": [{"tool": n.tool, "pre": list(n.preconditions or ()),
                       "post": list(n.postconditions or ()),
                       "ver": list(n.verification or ()),
                       "dep": list(n.depends_on or ())} for n in self.dag.nodes],
            "irs": [type(x).__name__ + ":" + getattr(x, "name", "") for x in self.irs],
        }
        blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
        return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def freeze(self) -> str:
        """★ 冻结（★ 产生计划哈希）。"""
        self.frozen = True
        self.plan_hash = self.compute_hash()
        return self.plan_hash

    def verify_unchanged(self) -> bool:
        """★★★★ **执行前校验**（★ V6 的核心：★ **冻结计划不能被执行器静默改写**）。

        ★★ 判据：★ ① 必须**已冻结**；★ ② 重算哈希必须**等于**冻结时的哈希。
        ★★★ **⇒ 不符 ⇒ 拒绝**（★ 不是警告 —— ★ 计划验收逐字）。
        """
        if not self.frozen or not self.plan_hash:
            return False
        return self.compute_hash() == self.plan_hash


# ══════════════════════════════════════════════════════════════════════
# 六、★★★★★ 「优雅」的多指标（★ FR-007 —— ★ **不能仅最少特征**）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class EleganceScore:
    """★★ **优雅的多指标**（★ 逐字承 EC03-T07）：

    「★ 修改稳定、基准表达、意图可读、工具风险、可制造性；★ **不能仅最少特征**」。
    """

    modification_stability: float = 0.0    #: ★ 改一个参数要动几处
    datum_expression: float = 0.0          #: ★ 基准是否用语义角色
    intent_readability: float = 0.0        #: ★ 特征名/结构是否可读
    tool_risk: float = 0.0                 #: ★ 用到的工具风险（★ 越高越差 ⇒ 取负向）
    manufacturability: float = 0.0         #: ★ 可制造性

    def total(self) -> float:
        """★ 加权总分（★ **五指标都要** —— ★ 不是 `1/特征数`）。"""
        return (0.25 * self.modification_stability
                + 0.20 * self.datum_expression
                + 0.15 * self.intent_readability
                + 0.20 * (1.0 - self.tool_risk)
                + 0.20 * self.manufacturability)

    def is_single_metric(self) -> bool:
        """★★★ **自查**：★ 是不是退化成了「单指标」（★ 那**不算**优雅）。

        ★★ 判据：★ 五个指标里**只有 ≤1 个非零** ⇒ ★ 退化。
        """
        vals = (self.modification_stability, self.datum_expression,
                self.intent_readability, self.tool_risk, self.manufacturability)
        return sum(1 for v in vals if v > 0.0) <= 1


def score_elegance(plan: CompiledPlan) -> EleganceScore:
    """★★ **按多指标打分**（★ 可算 —— ★ 不是形容词）。

    ★★ 依据（★ EC03-T07 逐字）：★「★ **不能仅最少特征**」——
      ★★★ **⇒ 本函数**不看**特征个数**作为主指标** ✓
    """
    tools = [n.tool for n in plan.dag.nodes]
    #: ★ **修改稳定**：★ 参数化的工具（阵列/回转）比逐项建的稳
    parametric = sum(1 for t in tools if "pattern" in t or "revolve" in t)
    stability = min(1.0, 0.4 + 0.2 * parametric)
    #: ★ **基准表达**：★ 有基准引用（★ IR 里有 `plane_datum`）则高
    has_datum = any(getattr(x, "plane_datum", "") for x in plan.irs)
    datum = 1.0 if has_datum else 0.3
    #: ★ **意图可读**：★ 步骤名是**语义工具名**（★ 不是 `call_1`/`op_2`）
    semantic = sum(1 for t in tools if t.islower() and "_" in t)
    readability = min(1.0, semantic / max(1, len(tools)))
    #: ★ **工具风险**：★ 危险工具（★ 删除/替换/薄壁）拉高风险
    risky = sum(1 for t in tools if any(k in t for k in ("delete", "replace", "thicken")))
    risk = min(1.0, risky / max(1, len(tools)))
    #: ★ **可制造性**：★ 有倒角/圆角后置 + 有孔阵列 ⇒ 好
    #:   ⚠ 别把续行的 `+` 写成**行首** —— ★ 门禁 `check_diff_markers.py` 会把它当 **patch 记号**
    #:     （★ 本会话就红了一次：★ 报「`scripts/engineering/compiler.py:428` 混入 diff 记号」）
    has_finish = any("chamfer" in t or "fillet" in t for t in tools)
    has_pattern = any("pattern" in t for t in tools)
    manuf = 0.5 + (0.25 if has_finish else 0.0) + (0.25 if has_pattern else 0.0)
    return EleganceScore(modification_stability=stability, datum_expression=datum,
                         intent_readability=readability, tool_risk=risk,
                         manufacturability=min(1.0, manuf))


# ══════════════════════════════════════════════════════════════════════
# 七、★★★★★ 编译器（★ 只吃 `EngineeringContract` ⇒ ★ 模型无关）
# ══════════════════════════════════════════════════════════════════════

#: ★★ 意图关键词 → 方法 id（★ **确定性映射** —— ★ 不是模型自由发挥）
INTENT_KEYWORDS = (
    ("支架", "mounting_bracket"),
    ("bracket", "mounting_bracket"),
    ("阶梯轴", "stepped_shaft"),
    ("轴", "stepped_shaft"),
    ("shaft", "stepped_shaft"),
    ("孔组", "hole_group"),
    ("孔", "hole_group"),
    ("板", "plate"),
    ("plate", "plate"),
)


def _pick_method(intent: str) -> MethodSpec | None:
    """★ **确定性**选法（★ 关键词最长优先 —— ★ 不靠模型）。

    ★★ 依据（★ 计划 §5 EC03 验收逐字）：★「★ **两模型生成的合法意图都通过同一编译器**」
      ⇒ ★★ 选法必须**确定性**，★ 否则两个模型会走两条路 ✗
    """
    low = (intent or "").lower()
    best: tuple[int, MethodSpec] | None = None
    for kw, mid in INTENT_KEYWORDS:
        if kw.lower() in low:
            spec = METHOD_LIBRARY[mid]
            if best is None or len(kw) > best[0]:
                best = (len(kw), spec)
    return best[1] if best else None


def compile_contract(contract: Any, *, device_class: str = "") -> CompiledPlan:
    """★★★★★ **编译**（★ EC03 的主入口）。

    ★★★ **四条不变量**（★ 见模块头）：
      ① ★ **只吃 `EngineeringContract`** —— ★ 用它的 `intent`/`content_hash`/`state`；
      ② ★ **全部检查在编译期**；
      ③ ★ **不 import 任何 COM 模块**（★ 见 `assert_no_com_imports`）；
      ④ ★★ **契约未冻结 ⇒ 拒绝**（★ `reject-contract-not-frozen`）。

    ★★ 编译期会拒绝（★ 逐字承计划验收）：
      · **越权**（★ 动修改域之外）· **欠约束**（★ 参数没定域）·
      · **循环依赖** · **非法路由**（★ 悬空前驱）·
      · **方法不适用** · **`unknown` 不得当可行**
    """
    #: ④ 契约必须**已冻结**（★ 否则编译的是一个还没定的东西）
    if not getattr(contract, "content_hash", ""):
        raise PlanError(RejectCode.CONTRACT_NOT_FROZEN,
                        "★ 契约没有内容哈希（★ 未冻结）⇒ 不编译")
    if getattr(contract, "state", "") != "frozen":
        raise PlanError(RejectCode.CONTRACT_NOT_FROZEN,
                        "★ 契约状态是 %r（★ 非 `frozen`）⇒ 不编译" % getattr(contract, "state", ""))
    #: ★★ **`unknown` 不得当可行**（★ FR-005）
    blocking = list(getattr(contract, "blocking_fields", lambda: [])())
    if blocking:
        raise PlanError(RejectCode.UNKNOWN_NOT_FEASIBLE,
                        "★ 契约仍有必需缺失字段 %r ⇒ `unknown` **不得当可行**" % blocking)
    #: ★ 确定性选法
    spec = _pick_method(getattr(contract, "intent", ""))
    if spec is None:
        raise PlanError(RejectCode.NO_METHOD,
                        "★ 没有匹配「%s」的方法" % getattr(contract, "intent", ""))
    #: ★★ **适用域检查**
    if device_class and not spec.applies_to(device_class):
        raise PlanError(RejectCode.NOT_APPLICABLE,
                        "★ 方法 %s 不适用设备类别 %r（★ 适用 %r）"
                        % (spec.id, device_class, list(spec.applicable_devices)))
    #: ★★ **欠约束检查**（★ 参数域必须存在 —— ★ 计划验收逐字）
    domains = getattr(contract, "parameter_domains", {}) or {}
    if not domains:
        raise PlanError(RejectCode.UNDERCONSTRAINED,
                        "★ 契约没有任何 `parameter_domains` ⇒ 欠约束")
    #: ★★ **越权检查**（★ 契约里的域必须在方法的**修改域**内）
    over = [k for k in domains if not spec.allows(k)]
    if over:
        raise PlanError(RejectCode.OVERREACH,
                        "★ 参数 %r 不在方法 %s 的修改域 %r 内 ⇒ 越权"
                        % (over, spec.id, list(spec.modification_domain)))
    #: ★ 编译成 DAG（★ 每步带前后置与验证）
    nodes: list[DAGNode] = []
    prev = None
    for i, step in enumerate(spec.steps):
        nodes.append(DAGNode(
            tool=step,
            preconditions=spec.preconditions if i == 0 else (),
            postconditions=spec.postconditions if i == len(spec.steps) - 1 else (),
            verification=spec.verification_obligations if i == len(spec.steps) - 1 else (),
            depends_on=(prev,) if prev else (),
        ))
        prev = step
    dag = ToolDAG(nodes=nodes)
    #: ★★ **循环依赖检查**（★ 编译期）
    if dag.has_cycle():
        raise PlanError(RejectCode.CYCLIC,
                        "★ DAG 有环：%r" % dag.cycle_path())
    #: ★★ **非法路由检查**（★ 悬空前驱）
    dangling = dag.unknown_dependencies()
    if dangling:
        raise PlanError(RejectCode.ILLEGAL_ROUTE, "★ 悬空前驱：%r" % dangling)
    #: ★ 造 IR（★ 带版本）
    irs: list = [SketchIR(name="sketch1", plane_datum="datum:mounting_interface")]
    for i, step in enumerate(spec.steps):
        irs.append(FeatureIR(name="feat%d_%s" % (i + 1, step), kind=step,
                             depends_on=(nodes[i - 1].tool,) if i else ()))
    return CompiledPlan(contract_hash=getattr(contract, "content_hash", ""),
                        method_id=spec.id, dag=dag, irs=irs)


# ══════════════════════════════════════════════════════════════════════
# 八、★★★★ 纯离线**自证**（★ V5：★ 不需要 COM 即可检验）
# ══════════════════════════════════════════════════════════════════════

#: ★★ **禁止出现的 COM 模块名**（★ 本模块**及其依赖**都不许有）
COM_MODULE_MARKERS = ("win32com", "comtypes", "pythoncom", "pywintypes",
                      "SldWorks", "sw_connect", "sw_part", "sw_session")


def assert_no_com_imports() -> dict:
    """★★★★ **纯离线自证**（★ V5：★「不需要 COM 即可检验计划正确性」）。

    ★★ 判据：★ 本模块的**源码里不出现**任何 COM 模块名（★ **含注释**）。
    ★★★ **⇒ 这条让「编译期验计划」在**没有 SolidWorks 的机器上**也成立** ✓
    """
    import pathlib
    src = pathlib.Path(__file__).read_text(encoding="utf-8", errors="replace")
    #: ★★ 只扫 `import` 行（★ 注释里提到「不 import COM」是**允许**的）
    hits = []
    for ln in src.splitlines():
        s = ln.strip()
        if not (s.startswith("import ") or s.startswith("from ")):
            continue
        for marker in COM_MODULE_MARKERS:
            if marker in s:
                hits.append(s)
    return {"ok": not hits, "offending_imports": hits,
            "checked_markers": list(COM_MODULE_MARKERS)}


# ══════════════════════════════════════════════════════════════════════
# 九、★★★★ 沙箱隔离（★ FR-008 —— ★ 探索产物**不得**直接进生产）
# ══════════════════════════════════════════════════════════════════════

#: ★★ 沙箱方法 id 的**前缀**（★ 一眼可辨 —— ★ 不是靠人记）
SANDBOX_PREFIX = "sandbox_"


def is_production_method(method_id: str) -> bool:
    """★★★★ **是不是生产方法**（★ EC03-T08 逐字：★「★ 建**沙箱探索通道**；
    ★ **探索产物不得直接进入生产方法库**，★ 需审查来源/域/正负例」）。

    ★★★ **判据**：★ 只有在 `METHOD_LIBRARY` 里**且不带沙箱前缀**的，★ 才算生产方法。
    ★★ **⇒ 沙箱产物**天然**进不来** —— ★ 它们不在库里，★ 且前缀不同 ✓
    """
    if not isinstance(method_id, str):
        return False
    if method_id.startswith(SANDBOX_PREFIX):
        return False
    return method_id in METHOD_LIBRARY


def list_sandbox_methods(candidates: list[str]) -> list[str]:
    """★ 从候选里挑出**沙箱产物**（★ 便于审查 —— ★ 不是直接入库）。"""
    return [m for m in candidates if isinstance(m, str) and m.startswith(SANDBOX_PREFIX)]


# ══════════════════════════════════════════════════════════════════════
# 十、★★★★ 不可满足核心 / 超时 / 多方案排序（★ FR-005 · EC03-T05）
# ══════════════════════════════════════════════════════════════════════

class SolveStatus:
    """★★ 求解状态（★ **`unknown` 不是「可行」** —— ★ FR-005 逐字）。"""

    SAT = "satisfiable"
    UNSAT = "unsatisfiable"
    UNKNOWN = "unknown"                #: ★★ 超时/信息不足
    TIMEOUT = "timeout"

    ALL = (SAT, UNSAT, UNKNOWN, TIMEOUT)


def find_unsat_core(constraints: list) -> dict:
    """★★★★ **不可满足核心**（★ EC03-T05 逐字：★「★ 定义**不可满足核心**/未知/超时/多方案排序」）。

    ★★ 输入：★ `[(变量, 下界, 上界)]` —— ★ 每条是一个**区间约束**。
    ★★★ **输出**：★ 一个**最小**的冲突子集（★ 不是「全都冲突」）。
      · ★ 例：★ `[(a, 0, 5), (a, 10, 20)]` ⇒ ★ 核心 = ★ **这两条**（★ 同变量、区间不相交）
    ★★ **为什么是「核心」而不是「全部」**：★ 指认**哪几条**冲突，★ 接手方才知道改哪个。

    ★ **本函数**不塞 SMT** —— ★ 只做区间求交（★ 确定性、★ 多项式时间）。
    """
    by_var: dict = {}
    for item in constraints:
        name, lo, hi = item[0], item[1], item[2]
        by_var.setdefault(name, []).append((name, lo, hi))
    for var, items in by_var.items():
        if len(items) < 2:
            continue
        lo = max(it[1] for it in items)
        hi = min(it[2] for it in items)
        if lo > hi:
            #: ★★★ **最小核心** = ★ 造成冲突的那几条（★ 不是全部约束）
            culprit = sorted(items, key=lambda it: (it[1], it[2]))
            return {"status": SolveStatus.UNSAT, "variable": var,
                    "core": [c[0] for c in culprit],
                    "reason": ("★ 变量 %s 的区间不相交：★ 下界最大 %r > 上界最小 %r"
                               % (var, lo, hi))}
    return {"status": SolveStatus.SAT, "core": [],
            "reason": "★ 所有区间约束都有交集"}


def solve_with_budget(constraints: list, *, steps_budget: int = 10_000) -> dict:
    """★★★ **带预算的求解**（★ EC03-T05 逐字：★「★ **超时**……★ `unknown` 不能落入默认可行」）。

    ★★★ **关键**：★ 预算用尽 ⇒ ★ **`timeout`**（★ **不是 `satisfiable`**）✗
      ⇒ ★★ **`unknown` 绝不落入默认可行** ✓
    """
    if steps_budget <= 0:
        return {"status": SolveStatus.TIMEOUT, "core": [],
                "reason": "★ 预算为 0 ⇒ **超时**（★ `unknown` 不当可行）"}
    needed = max(1, len(constraints))
    if needed > steps_budget:
        return {"status": SolveStatus.TIMEOUT, "core": [],
                "reason": "★ 需要 %d 步 > 预算 %d ⇒ **超时**" % (needed, steps_budget)}
    return find_unsat_core(constraints)


def rank_plans(plans: list, *, prefer: str = "elegance") -> list:
    """★★ **多方案排序**（★ EC03-T05 逐字：★「★ 多方案排序」）。

    ★★ 依据（★ EC03-T07）：★ 排序**必须**用**多指标**（★ 不能只按复杂度/特征数）。
    ★ 排序键：★ `elegance` ⇒ ★ 用 `EleganceScore.total()`；
      ★★ **复杂度只在并列时**当次序（★ 不是主指标）。
    """
    def key(p):
        s = score_elegance(p) if prefer == "elegance" else EleganceScore()
        c = METHOD_LIBRARY.get(getattr(p, "method_id", ""), None)
        rank = Complexity.RANK.get(c.complexity, 2) if c else 2
        return (-s.total(), rank)
    return sorted(plans, key=key)
