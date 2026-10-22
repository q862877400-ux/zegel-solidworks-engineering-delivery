"""★ EC07 机械与自动化纵切片 —— MotionIR / AutomationIR / SafetyFunctionIR / 状态可达性。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC07**（★ T01–T08 逐字）
#         `specs/309-ec07-automation-slice/spec.md`
#         `scripts/engineering/rules.py`（★ EC02 的 `power_efficiency_margin` —— ★ **复用**）
#         `scripts/engineering/jobs.py`（★ EC04 的 `VersionBinding` —— ★ **复用**）
# 定位:   ★ **EC07** 的实现。★★★ 计划 §5 EC07 验收逐字：「★ 至少**一个正常循环**和**具
#           名故障矩阵**可重复验证； ★ **安全功能 `unknown` 不能被普通互锁测试替代**； ★
#            设计产物**标清「未经实机调试/安全确认」**」
#         ★★★ **首域**（★ 逐字）：「★ 限定行程/载荷/节拍的**直线搬运单元**；
#           ★ **只设计和验证，不直接驱动实机**」
# 官方依据: 不适用（本仓的自动化设计层 —— ★ **不调 SolidWorks API** · ★ **不下发 PLC**）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件（★ **纯离线** —— ★ 见 `assert_no_com_imports`）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import math
from dataclasses import dataclass, field

__all__ = [
    "InterlockKind",
    "SafetyLevel",
    "FaultKind",
    "MotionIR",
    "AutomationIR",
    "SafetyFunctionIR",
    "StateMachine",
    "FaultMatrix",
    "SelectionResult",
    "UNVERIFIED_ON_REAL_MACHINE",
    "select_drive",
    "check_reachability",
    "assert_no_com_imports",
    "CrossCheckKind",
    "CrossCheck",
]


#: ★★★ **强制标记**（★ 逐字承验收：★「★ 设计产物**标清「未经实机调试/安全确认」**」）
#:   ★★ 每个交付物**必须带**它 —— ★ 不是可选字段
UNVERIFIED_ON_REAL_MACHINE = (
    "★ 未经实机调试 / 安全确认（★ 仅设计材料，★ 不得据此驱动实机）"
)


class SafetyLevel:
    """★ 安全等级（★ EC07-T04 逐字：★「★ **风险/安全等级的确定需要适用方法与审核责任**」）。"""

    NONE = "none"  #: ★ 没做安全评估
    ASSESSED = "assessed"  #: ★ 已评估（★ 有方法与责任人）
    UNKNOWN = "unknown"  #: ★★ **未确定** ⇒ ★ **不放行**（★ 验收核心）

    ALL = (NONE, ASSESSED, UNKNOWN)
    #: ★★★ **只有已评估才放行**
    RELEASING = (ASSESSED,)


class InterlockKind:
    """★★ **互锁种类**（★ EC07-T04 逐字：★「★ **分开普通互锁和安全功能**」）。"""

    NORMAL = "normal_interlock"  #: ★ 普通互锁（★ 工艺/防错）
    SAFETY = "safety_function"  #: ★★ **安全功能**（★ 失电/失气/急停/人员接近）

    ALL = (NORMAL, SAFETY)


class FaultKind:
    """★★ **故障种类**（★ EC07-T05 逐字点名的七类 —— ★ 见 `FaultMatrix.DEFAULT_KINDS`）。"""

    LIMIT = "limit"  #: ★ 极限位
    HOME = "home"  #: ★ 原点
    CLAMP = "clamp"  #: ★ 夹紧
    DOOR = "door"  #: ★ 开门
    POWER_LOSS = "power_loss"  #: ★ 失电
    AIR_LOSS = "air_loss"  #: ★ 失气
    SENSOR_CONFLICT = "sensor_conflict"  #: ★ 传感器冲突

    ALL = (LIMIT, HOME, CLAMP, DOOR, POWER_LOSS, AIR_LOSS, SENSOR_CONFLICT)


# ══════════════════════════════════════════════════════════════════════
# 一、★★★★★ MotionIR（★ EC07-T02）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class MotionIR:
    """★★★ **MotionIR**（★ 逐字承 EC07-T02）：

    「★ MotionIR 包含**运动曲线、峰值/均方根负荷、惯量、效率、制动、热边界**；
    ★ 选择**电机/减速/丝杠或气动**方案」。
    """

    stroke_m: float = 0.0  #: ★ 行程
    cycle_time_s: float = 0.0  #: ★ 节拍
    payload_kg: float = 0.0  #: ★ 负载
    moving_mass_kg: float = 0.0  #: ★ 运动质量
    efficiency: float = 1.0  #: ★ 效率（★ 传动链）
    #: ★★ **制动**（★ 有/无 + 方式）
    braking: str = ""
    #: ★ 热边界（★ 允许温升）
    thermal_limit_c: float = 0.0
    #: ★★ **运动曲线**（★ 如 `trapezoid` / `scurve`）
    profile: str = "trapezoid"

    def peak_velocity(self) -> float:
        """★ **峰值速度**（★ 梯形曲线粗算：★ 行程 / (节拍 × 0.5)）。

        ★★ 假设：★ 加速 + 匀速 + 减速各占 1/4、1/2、1/4（★ **梯形**）⇒ ★ `v_peak = s / (t/2)`。
        """
        if self.cycle_time_s <= 0:
            return 0.0
        return self.stroke_m / (self.cycle_time_s * 0.5)

    def peak_acceleration(self) -> float:
        """★ **峰值加速度**（★ 梯形：★ `a = 4 v / t`）。"""
        if self.cycle_time_s <= 0:
            return 0.0
        return 4.0 * self.peak_velocity() / self.cycle_time_s

    def peak_force(self) -> float:
        """★★ **峰值力**（★ `F = m a` —— ★ 含负载与运动质量）。"""
        m = self.payload_kg + self.moving_mass_kg
        return m * self.peak_acceleration()

    def rms_force(self) -> float:
        """★★ **均方根力**（★ 逐字承 EC07-T02：★「★ **峰值/均方根负荷**」）。

        ★★ 梯形曲线的 RMS 系数 ≈ `1/√3`（★ 近似 —— ★ 如实标注是近似）。
        """
        return self.peak_force() / math.sqrt(3.0)

    def peak_power(self) -> float:
        """★ **峰值功率**（★ `P = F v / η`）。"""
        if self.efficiency <= 0:
            return float("inf")
        return self.peak_force() * self.peak_velocity() / self.efficiency

    def is_complete(self) -> dict:
        """★★★ **完整性**（★ 缺项 ⇒ `unknown` —— ★ 不硬算）。

        ★★ 依据（★ EC07-T01 逐字）：★ 要冻结「节拍、负载、行程、精度、环境、人员接近、失电/失气工况」。
        """
        missing = []
        if self.stroke_m <= 0:
            missing.append("stroke_m")
        if self.cycle_time_s <= 0:
            missing.append("cycle_time_s")
        if self.payload_kg <= 0 and self.moving_mass_kg <= 0:
            missing.append("mass")
        if self.efficiency <= 0 or self.efficiency > 1:
            missing.append("efficiency")
        if not self.braking:
            missing.append("braking")
        return {
            "ok": not missing,
            "missing": missing,
            "reason": (
                "★ MotionIR 完整"
                if not missing
                else "★★ 缺 %r ⇒ 不得据此选型" % missing
            ),
        }


# ══════════════════════════════════════════════════════════════════════
# 二、★★★★★ AutomationIR（★ EC07-T03）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class AutomationIR:
    """★★★ **AutomationIR**（★ 逐字承 EC07-T03）：

    「★ AutomationIR 定义 **IO、传感器、状态机、互锁、超时和故障恢复**；
    ★ **接口型号数据须有可用来源和版本**」。
    """

    io_points: list = field(default_factory=list)  #: ★ `[{"name","kind"}]`
    sensors: list = field(
        default_factory=list
    )  #: ★ `[{"name","type","source","version"}]`
    interlocks: list = field(default_factory=list)  #: ★ `[{"kind","expr"}]`
    timeouts: dict = field(default_factory=dict)  #: ★ `{name: seconds}`
    recovery: dict = field(default_factory=dict)  #: ★ `{fault: action}`

    def sensors_have_sources(self) -> dict:
        """★★★★ **接口型号数据须有来源与版本**（★ 逐字承 EC07-T03）。

        ★★ 判据：★ 每个传感器**必须**有 `source` 与 `version` —— ★ 缺一个 ⇒ **不算合格**。
        """
        bad = []
        for s in self.sensors:
            miss = [k for k in ("name", "type", "source", "version") if not s.get(k)]
            if miss:
                bad.append({"sensor": s.get("name", "?"), "missing": miss})
        if not self.sensors:
            return {"ok": False, "reason": "★★ 一个传感器都没有 ⇒ 不算合格", "bad": []}
        return {
            "ok": not bad,
            "bad": bad,
            "reason": (
                "★ %d 个传感器都有来源与版本" % len(self.sensors)
                if not bad
                else "★★ %d 个传感器缺来源/版本" % len(bad)
            ),
        }

    def interlock_by_kind(self, kind: str) -> list:
        """★ 按种类取互锁（★ 用于**安全与普通分开** —— ★ EC07-T04）。"""
        return [i for i in self.interlocks if i.get("kind") == kind]


# ══════════════════════════════════════════════════════════════════════
# 三、★★★★★ SafetyFunctionIR（★ EC07-T04 —— ★ **安全与普通分开**）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class SafetyFunctionIR:
    """★★★★★ **SafetyFunctionIR**（★ 逐字承 EC07-T04）：

    「★ 分开**普通互锁**和**安全功能**；★ **风险/安全等级的确定需要适用方法与审核责任**」。

    ★★★ **验收（★ 逐字）**：★「★ **安全功能 `unknown` 不能被普通互锁测试替代**」。

    ★★★ **本类的意义**：★ 它**物理上**把两类分开 ⇒
      ★★ 「用普通互锁的通过去顶替安全功能的未知」**做不到**（★ 因为它们**不在同一个清单里**）✓
    """

    functions: list = field(default_factory=list)
    #: ★★★ **安全等级**（★ `NONE`/`ASSESSED`/`UNKNOWN`）
    safety_level: str = SafetyLevel.UNKNOWN
    #: ★★ **评估方法**（★ 逐字要求：「★ 需要**适用方法**」）
    assessment_method: str = ""
    #: ★★ **审核责任**（★ 逐字要求：「★ 和**审核责任**」）
    accountable_person: str = ""

    def add_safety_function(
        self, name: str, *, implements: str, verified: bool = False, note: str = ""
    ) -> None:
        """★ 加一个**安全功能**（★ **不是**普通互锁 —— ★ 两类不混）。"""
        self.functions.append(
            {
                "kind": InterlockKind.SAFETY,
                "name": name,
                "implements": implements,
                "verified": bool(verified),
                "note": note,
            }
        )

    def level_is_established(self) -> dict:
        """★★★★ **安全等级是否已确定**（★ 逐字：★「★ 需要**适用方法与审核责任**」）。

        ★★ 判据：★ ① 等级**不是** `UNKNOWN`；★ ② 有**评估方法**；★ ③ 有**审核责任人**。
        """
        missing = []
        if self.safety_level == SafetyLevel.UNKNOWN:
            missing.append("safety_level")
        if not str(self.assessment_method).strip():
            missing.append("assessment_method")
        if not str(self.accountable_person).strip():
            missing.append("accountable_person")
        return {
            "ok": not missing,
            "missing": missing,
            "reason": (
                "★ 安全等级已确定（★ 方法：%s · ★ 责任人：%s）"
                % (self.assessment_method, self.accountable_person)
                if not missing
                else "★★ 安全等级**未确定** ⇒ 缺 %r ⇒ **不放行**" % missing
            ),
        }

    def verdict(self, normal_interlocks: list | None = None) -> dict:
        """★★★★★ **判定**（★ 逐字承验收）。

        ★★★ **关键**：★ 即使**普通互锁全通过**，★ 只要安全等级是 `UNKNOWN`
          ⇒ ★ **结论仍是 `unknown`**（★ **不能被替代**）✗
        """
        lvl = self.level_is_established()
        if not lvl["ok"]:
            return {
                "verdict": "unknown",
                "releasing": False,
                "normal_interlocks_passed": self._normal_all_ok(normal_interlocks),
                "reason": (
                    "★★★ 安全功能**未确定**（%s）⇒ ★ 结论 `unknown`；"
                    "★★ **普通互锁的通过不能替代它**" % lvl["missing"]
                ),
                "substituted": False,
            }
        unverified = [f for f in self.functions if not f["verified"]]
        if unverified:
            return {
                "verdict": "unknown",
                "releasing": False,
                "unverified_functions": [f["name"] for f in unverified],
                "reason": "★★ 有安全功能**未验证**：%r ⇒ `unknown`"
                % [f["name"] for f in unverified],
            }
        return {
            "verdict": "pass",
            "releasing": True,
            "safety_level": self.safety_level,
            "reason": "★ 安全等级已确定 + 全部安全功能已验证",
            "mark": UNVERIFIED_ON_REAL_MACHINE,
        }

    @staticmethod
    def _normal_all_ok(normal_interlocks: list | None) -> bool:
        items = normal_interlocks or []
        return bool(items) and all(i.get("ok") for i in items)


# ══════════════════════════════════════════════════════════════════════
# 四、★★★★★ 状态机与可达性（★ EC07-T05）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class StateMachine:
    """★★★★ **有限状态机**（★ 逐字承 EC07-T05）：

    「★ 极限/原点/夹紧/开门/失电/失气/**传感器冲突**形成**有限状态可达性测试**」。
    """

    initial: str = "idle"
    transitions: dict = field(default_factory=dict)  #: `{state: {event: next}}`
    states: tuple = ()

    def all_states(self) -> set:
        s = {self.initial}
        for a, evs in self.transitions.items():
            s.add(a)
            s.update(evs.values())
        return s

    def reachable(self) -> set:
        """★★ **可达状态集**（★ BFS —— ★ **可重复**）。"""
        seen, stack = {self.initial}, [self.initial]
        while stack:
            cur = stack.pop()
            for nxt in (self.transitions.get(cur) or {}).values():
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return seen

    def unreachable(self) -> list:
        """★★★ **不可达状态**（★ 定义里写了但走不到 ⇒ ★ 那是**死代码或设计缺陷**）。"""
        return sorted(self.all_states() - self.reachable())

    def dead_ends(self) -> list:
        """★★ **死端**（★ 没有出边的状态 —— ★ 除了明确的安全终态）。"""
        safe_terminals = {"estop", "faulted"}
        return sorted(
            s
            for s in self.reachable()
            if not (self.transitions.get(s) or {}) and s not in safe_terminals
        )

    def run_cycle(self, events: list) -> dict:
        """★★★★ **跑一个正常循环**（★ 逐字承验收：★「★ 至少**一个正常循环**……可重复验证」）。

        ★★ 判据：★ 每个事件都**有对应迁移**；★ 缺迁移 ⇒ **报出来**（★ 不静默停）。
        """
        cur = self.initial
        trace = [cur]
        for e in events:
            nxt = (self.transitions.get(cur) or {}).get(e)
            if nxt is None:
                return {
                    "ok": False,
                    "at": cur,
                    "event": e,
                    "trace": trace,
                    "reason": "★★ 状态 %r 没有对事件 %r 的迁移" % (cur, e),
                }
            cur = nxt
            trace.append(cur)
        return {
            "ok": True,
            "final": cur,
            "trace": trace,
            "repeatable": True,
            "reason": "★ 正常循环跑通（★ 事件序固定 ⇒ **可重复**）",
        }


def check_reachability(sm: StateMachine) -> dict:
    """★ 对外入口（★ 与 `StateMachine` 的几个方法**合起来** —— ★ 便于判据调用）。"""
    return {
        "reachable": sorted(sm.reachable()),
        "unreachable": sm.unreachable(),
        "dead_ends": sm.dead_ends(),
    }


# ══════════════════════════════════════════════════════════════════════
# 五、★★★★★ 具名故障矩阵（★ EC07-T05/T07）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class FaultMatrix:
    """★★★★ **故障矩阵**（★ 逐字承验收：★「★ 至少一个正常循环和**具名故障矩阵**可重复验证」）。

    ★★ **具名** = ★ 每一类故障**都有名字**、★ 都有**期望反应**、★ 都**可重复**。
    """

    rows: list = field(default_factory=list)

    #: ★★ **默认七类**（★ 逐字承 EC07-T05）
    DEFAULT_KINDS = FaultKind.ALL

    def add(
        self, kind: str, expected: str, *, implemented: bool, note: str = ""
    ) -> None:
        """★ 加一行（★ **必须给期望反应** —— ★ 空的不算具名）。"""
        if not str(expected).strip():
            raise ValueError("★★ 故障行**必须给期望反应**（★ 否则不是具名）")
        self.rows.append(
            {
                "kind": kind,
                "expected": expected,
                "implemented": bool(implemented),
                "note": note,
            }
        )

    def is_named_and_complete(self) -> dict:
        """★★★★ **具名且完整**（★ 七类都要有）。

        ★★ 判据：★ ① 七类**都有**；★ ② 每类都有**期望反应**；★ ③ **如实标**哪些没实现。
        """
        have = {r["kind"] for r in self.rows}
        missing = [k for k in self.DEFAULT_KINDS if k not in have]
        no_expected = [r["kind"] for r in self.rows if not r.get("expected")]
        unimplemented = [r["kind"] for r in self.rows if not r.get("implemented")]
        return {
            "ok": not missing and not no_expected,
            "missing_kinds": missing,
            "rows_without_expected": no_expected,
            "unimplemented": unimplemented,  #: ★★ **如实报**（★ 不假装做了）
            "count": len(self.rows),
            "reason": (
                "★ 七类齐且都有期望反应"
                if not missing and not no_expected
                else "★★ 缺 %r / 无期望反应的 %r" % (missing, no_expected)
            ),
        }


# ══════════════════════════════════════════════════════════════════════
# 六、★★★★ 选型（★ EC07-T02/T07）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class SelectionResult:
    """★ 选型结果（★ **带依据** —— ★ 不是「就它了」）。"""

    kind: str = ""  #: ★ `motor` / `pneumatic`
    model: str = ""
    margin: float = 0.0  #: ★ 余量（★ 越大越保守）
    basis: str = ""
    #: ★★★ **强制标记**（★ 逐字承验收）
    mark: str = UNVERIFIED_ON_REAL_MACHINE

    def is_acceptable(self, *, min_margin: float = 1.2) -> dict:
        """★★ **可接受？**（★ 余量必须够 —— ★ 且**必须带标记**）。"""
        if self.margin < min_margin:
            return {
                "ok": False,
                "reason": "★★ 余量 %.2f < %.2f ⇒ 不够保守" % (self.margin, min_margin),
            }
        if not self.basis:
            return {"ok": False, "reason": "★★ 没有依据 ⇒ 不是选型"}
        if self.mark != UNVERIFIED_ON_REAL_MACHINE:
            return {"ok": False, "reason": "★★ 缺「未经实机调试」标记"}
        return {"ok": True, "reason": "★ 余量够 + 有依据 + 有标记"}


def select_drive(motion: MotionIR, *, candidates: list) -> SelectionResult:
    """★★★ **选型**（★ EC07-T02 逐字：★「★ 选择**电机/减速/丝杠或气动**方案」）。

    ★★ 判据：★ 峰值力**必须**小于候选的额定力 × 余量；★ 选**余量最大**的那个。
    ★★★ **缺项 ⇒ 不选**（★ `MotionIR.is_complete()` 不过 ⇒ 报 `unknown`）。
    """
    comp = motion.is_complete()
    if not comp["ok"]:
        return SelectionResult(
            kind="",
            model="",
            margin=0.0,
            basis="★★ MotionIR 不完整（%s）⇒ **不选型**" % comp["missing"],
        )
    need = motion.peak_force()
    best: SelectionResult | None = None
    for c in candidates or []:
        rated = float(c.get("rated_force_n") or 0)
        if rated <= 0:
            continue
        margin = rated / need if need > 0 else float("inf")
        if best is None or margin > best.margin:
            best = SelectionResult(
                kind=c.get("kind", ""),
                model=c.get("model", ""),
                margin=margin,
                basis=(
                    "★ 峰值力 %.1f N ≤ 额定 %.1f N（★ 余量 %.2f）—— ★ 取余量最大者"
                    % (need, rated, margin)
                ),
            )
    if best is None:
        return SelectionResult(
            kind="", model="", margin=0.0, basis="★★ 没有可用候选 ⇒ 不选"
        )
    return best


# ══════════════════════════════════════════════════════════════════════
# 七、★★★★ 纯离线自证
# ══════════════════════════════════════════════════════════════════════

COM_MODULE_MARKERS = (
    "win32com",
    "comtypes",
    "pythoncom",
    "pywintypes",
    "SldWorks",
    "sw_connect",
    "sw_part",
    "sw_session",
)


def assert_no_com_imports() -> dict:
    """★★★ **纯离线自证**（★ 本模块不 import COM —— ★ 与 EC03/EC04 同族）。"""
    import pathlib

    src = pathlib.Path(__file__).read_text(encoding="utf-8", errors="replace")
    hits = []
    for ln in src.splitlines():
        s = ln.strip()
        if not (s.startswith("import ") or s.startswith("from ")):
            continue
        for marker in COM_MODULE_MARKERS:
            if marker in s:
                hits.append(s)
    return {"ok": not hits, "offending_imports": hits}


# ══════════════════════════════════════════════════════════════════════
# 八、★★★★★ 交叉检查（★ EC07-T06）
# ══════════════════════════════════════════════════════════════════════


class CrossCheckKind:
    """★★ **交叉检查的项**（★ 逐字承 EC07-T06）：★「★ 机械**行程止挡**、**制动/保持**、
    ★ **能量释放**、**维护模式**与控制需求**交叉检查**」。
    """

    STROKE_STOP = "stroke_stop"  #: ★ 行程止挡
    BRAKE_HOLD = "brake_hold"  #: ★ 制动/保持
    ENERGY_RELEASE = "energy_release"  #: ★ 能量释放
    MAINTENANCE_MODE = "maintenance_mode"  #: ★ 维护模式

    ALL = (STROKE_STOP, BRAKE_HOLD, ENERGY_RELEASE, MAINTENANCE_MODE)


@dataclass
class CrossCheck:
    """★★★★ **交叉检查**（★ EC07-T06 逐字）。

    ★★★ **「交叉」的意思**：★ 每一项**同时**要在**机械侧**与**控制侧**都有交代 ——
      ★★ 只在一边写了 ⇒ ★ **不算交叉检查通过** ✗
    """

    items: dict = field(
        default_factory=dict
    )  #: `{kind: {"mechanical": str, "control": str}}`

    def add(self, kind: str, *, mechanical: str, control: str) -> None:
        self.items[kind] = {"mechanical": mechanical, "control": control}

    def verdict(self) -> dict:
        """★★★ **判定**（★ 四类齐 + ★ **每类两侧都有**）。"""
        missing = [k for k in CrossCheckKind.ALL if k not in self.items]
        one_sided = [
            k
            for k, v in self.items.items()
            if not str(v.get("mechanical") or "").strip()
            or not str(v.get("control") or "").strip()
        ]
        ok = not missing and not one_sided
        return {
            "ok": ok,
            "missing_kinds": missing,
            "one_sided": one_sided,
            "checked": len(self.items),
            "reason": (
                "★ 四类都在**机械侧与控制侧**有交代"
                if ok
                else "★★ 缺 %r / 只写了一侧 %r" % (missing, one_sided)
            ),
        }
