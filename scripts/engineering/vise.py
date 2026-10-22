"""★ 阶段 5 · 平口钳：共享接口 + 传动 + 钳口自由 + 螺纹定义（规格 320 的 H1~H4）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/vise.py
# 定位:   规格 `specs/320-stage5-bench-vise` 的 H1（共享接口）/ H2（传动计算）/H3（活
#           动钳口不得被误固定）/ H4（螺纹工程定义）。★★ 实测（2026-10-12）起点：`assemb
#           ly.py` 已有 `DofVerdict`（5 档）/`MateKind`（含 `REMOVES` 表）/ `ConstraintG
#           raph.total_dof()` /`ConstraintGraph.verdict()`（五档保守顺序）/ `Interferenc
#           eScan` /`ToleranceChain`；`part_loop.py` 已有 `DofPlan` / `check_dof_plan`。
#           ★ 而**没有平口钳的共享接口模型、没有导程→位移计算、  没有「无误固定活动钳口
#           」的检查、没有螺纹工程定义**。
# 官方依据: ① 外部方案阶段 5 的验收 S5（逐字）② `scripts/engineering/assembly.py` 的 `Do
#           fVerdict.RELEASING`   —— ★★ **「预期运动」是允许的**（★ 那正是活动钳口需要的
#           ）③ 本仓**事实 2**（入参毫米 · COM 侧米）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收入口 `tools/run_stage5_vise.py --live`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import math
from dataclasses import dataclass, field

#: ══════════════════════════════════════════════════════════════════════
# 一、共享接口（★ H1 —— ★ 导向 / 螺杆 / 螺母 / 钳口）
#: ══════════════════════════════════════════════════════════════════════

GUIDE = "guide"
SCREW = "screw"
NUT = "nut"
JAW = "jaw"
INTERFACE_KINDS = (GUIDE, SCREW, NUT, JAW)

#: ★★ **哪些零件依赖哪些接口**（★ FR-002 的传播判据的真源）。
#:   ★ 改一个接口 ⇒ **依赖它的零件全部失效**；★ 不依赖的**可复用**。
INTERFACE_DEPENDENTS: dict[str, tuple] = {
    #: ★ 导向：导轨间距变了 ⇒ 活动钳口与底座都要改
    "guide_width_mm": ("活动钳口", "底座", "导轨"),
    #: ★ 螺杆：外径变了 ⇒ 螺杆本身 + 螺母（★ 配作）
    "screw_dia_mm": ("螺杆", "螺母"),
    #: ★ 导程：变了 ⇒ 螺母与位移关系（★ 但不影响钳口外形）
    "screw_lead_mm": ("螺母",),
    #: ★ 钳口：开口高度变了 ⇒ 两片钳口
    "jaw_height_mm": ("活动钳口", "固定钳口"),
    #: ★ 行程：变了 ⇒ 螺杆长度与底座
    "travel_mm": ("螺杆", "底座"),
    #: ★ 载荷：变了 ⇒ 只有钳口（★ 强度相关）
    "clamp_force_n": ("活动钳口", "固定钳口"),
}


class ViseError(Exception):
    """★ 平口钳模型失败（★ 带封闭码）。"""

    CODES = ("missing-interface", "bad-thread", "jaw-fixed", "lead-mismatch")

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法平口钳拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


@dataclass
class SharedInterface:
    """★ **一个共享接口**（★ 多零件共用 —— ★ 改一处，依赖它的全变）。"""

    name: str
    kind: str
    value: float
    unit: str = "mm"

    def __post_init__(self) -> None:
        assert self.kind in INTERFACE_KINDS, "★ 非法接口种类：%r" % self.kind


@dataclass
class ViseModel:
    """★ 平口钳的**接口集**（★ H1）。"""

    interfaces: dict = field(default_factory=dict)

    def set(
        self, name: str, kind: str, value: float, unit: str = "mm"
    ) -> SharedInterface:
        it = SharedInterface(name=name, kind=kind, value=float(value), unit=unit)
        self.interfaces[name] = it
        return it

    def get(self, name: str) -> SharedInterface | None:
        return self.interfaces.get(name)

    def require(self, *names: str) -> None:
        """★ 缺接口 ⇒ 抛（★ 不静默）。"""
        miss = [n for n in names if n not in self.interfaces]
        if miss:
            raise ViseError("missing-interface", "★ 缺接口：%s" % miss)


#: ══ 默认的平口钳接口（★ 冻结值 —— ★ 需求给的载荷/行程/材料）
DEFAULT_INTERFACES = {
    "guide_width_mm": (GUIDE, 120.0),
    "screw_dia_mm": (SCREW, 20.0),
    "screw_lead_mm": (SCREW, 4.0),
    "jaw_height_mm": (JAW, 40.0),
    "jaw_width_mm": (JAW, 150.0),
    "travel_mm": (SCREW, 100.0),
    "clamp_force_n": (JAW, 15000.0),
}


def default_model() -> ViseModel:
    m = ViseModel()
    for k, (kind, v) in DEFAULT_INTERFACES.items():
        m.set(k, kind, v)
    return m


#: ══════════════════════════════════════════════════════════════════════
# 二、接口变更传播（★ H1 —— ★ FR-002）
#: ══════════════════════════════════════════════════════════════════════


def propagate(
    interface_name: str, old: float, new: float, all_parts: tuple | None = None
) -> dict:
    """★★ **接口变更传播**（★ FR-002）。

    ★★ 判据（★ 两条都要）：
      · **依赖它的零件全部失效**（★ 从 `INTERFACE_DEPENDENTS` 查）
      · **不依赖它的零件可复用**（★ 不是「全都标脏」—— ★ 与阶段 3 的失效闭包同族）
    """
    if old == new:
        return {
            "changed": False,
            "stale": [],
            "reusable": list(all_parts or ()),
            "reason": "★ 值没变 ⇒ 无传播",
        }
    affected = set(INTERFACE_DEPENDENTS.get(interface_name, ()))
    parts = (
        list(all_parts)
        if all_parts is not None
        else sorted({p for v in INTERFACE_DEPENDENTS.values() for p in v})
    )
    stale = [p for p in parts if p in affected]
    reusable = [p for p in parts if p not in affected]
    return {
        "changed": True,
        "interface": interface_name,
        "old": old,
        "new": new,
        "stale": stale,
        "reusable": reusable,
        "ok": bool(stale),
    }


#: ══════════════════════════════════════════════════════════════════════
# 三、传动计算（★ H2 —— ★ FR-003：独立计算，不靠 CAD）
#: ══════════════════════════════════════════════════════════════════════


@dataclass
class TravelCheck:
    lead_mm: float = 0.0
    turns: float = 0.0
    travel_mm: float = 0.0
    readback_mm: float = 0.0
    tolerance_mm: float = 0.01

    @property
    def computed(self) -> float:
        """★ **独立算**：位移 = 导程 × 圈数。"""
        return self.lead_mm * self.turns

    @property
    def delta(self) -> float:
        return abs(self.computed - self.readback_mm)

    @property
    def consistent(self) -> bool:
        """★ 判据：**独立算的**与**回读的**差在容差内。"""
        return self.delta <= self.tolerance_mm

    def verdict(self) -> dict:
        return {
            "computed_mm": round(self.computed, 6),
            "readback_mm": round(self.readback_mm, 6),
            "delta_mm": round(self.delta, 6),
            "tolerance_mm": self.tolerance_mm,
            "consistent": self.consistent,
            "★": "★ 独立算（导程×圈数）与回读**分别**核对",
        }


def lead_to_travel(
    lead_mm: float,
    turns: float,
    *,
    readback_mm: float | None = None,
    tolerance_mm: float = 0.01,
) -> TravelCheck:
    """★★ **导程 → 位移**（★ H2 —— ★ FR-003）。

    ★★ 判据（★ **两条腿**）：
      · `computed = lead × turns`（★ **纯算术** —— ★ 不碰 CAD）
      · `readback` 由真机给（★ 没给 ⇒ `readback=0` ⇒ **必然不一致** ⇒ 如实报）
    ★★ **为什么必须独立算**：若两者都从同一份 CAD 读，★ 那是**共同错误源**
      （★ 外部方案 §新增风险 4 逐字：「生成器与验证器都用同一份错误参数……
        会一起给出错误的绿灯」）。
    """
    return TravelCheck(
        lead_mm=float(lead_mm),
        turns=float(turns),
        travel_mm=float(lead_mm) * float(turns),
        readback_mm=float(readback_mm or 0.0),
        tolerance_mm=float(tolerance_mm),
    )


#: ══════════════════════════════════════════════════════════════════════
# 四、活动钳口的自由度（★ H3 —— ★ FR-004/005）
#: ══════════════════════════════════════════════════════════════════════


@dataclass
class JawFreedom:
    """★ 活动钳口的自由度检查（★ H3）。"""

    dof: int = 0
    annotated_motions: list = field(default_factory=list)
    is_fixed: bool = False

    def verdict(self) -> dict:
        """★★ **判据**（★ 与 `assembly.DofVerdict` 同族）：

        ★★ 三档：
          ```
          ① 被固定（`is_fixed` 或 `dof == 0`）  ⇒ `jaw-fixed`（★ **失败**）
          ② 有自由度但**没标注**              ⇒ `under_constrained`（★ 失败）
          ③ 有自由度且**逐条标注**            ⇒ `expected_motion`（★ **通过**）
          ```
        ★★ **为什么①最严**：活动钳口**必须能动**（★ 那是它的功能）——
          ★ 被固定 = **功能没了**，★ 而「装配成功」看不出来（★ R1 突变正是这一类）。
        """
        if self.is_fixed or self.dof <= 0:
            return {
                "verdict": "jaw-fixed",
                "dof": self.dof,
                "releasing": False,
                "reason": "★★ 活动钳口**被固定**（或自由度为 0）⇒ "
                "★ 功能没了（★ 而装配成功看不出来）",
            }
        if not self.annotated_motions:
            return {
                "verdict": "under_constrained",
                "dof": self.dof,
                "releasing": False,
                "reason": "★ 有自由度但**没逐条标注** ⇒ 欠约束",
            }
        return {
            "verdict": "expected_motion",
            "dof": self.dof,
            "motions": list(self.annotated_motions),
            "releasing": True,
            "reason": "★ 有自由度且已标注 ⇒ 预期运动（★ 允许）",
        }


def check_jaw_free(
    *, dof: int, motions: list | None = None, is_fixed: bool = False
) -> JawFreedom:
    """★ 建一个活动钳口自由度检查（★ 判据见 `JawFreedom.verdict`）。"""
    return JawFreedom(
        dof=int(dof), annotated_motions=list(motions or ()), is_fixed=bool(is_fixed)
    )


#: ══════════════════════════════════════════════════════════════════════
# 五、螺纹工程定义（★ H4 —— ★ FR-007）
#: ══════════════════════════════════════════════════════════════════════


@dataclass
class ThreadSpec:
    """★ 螺纹的**工程定义**（★ 不是装饰螺纹）。"""

    standard: str = ""
    designation: str = ""
    pitch_mm: float = 0.0
    tolerance_class: str = ""
    material: str = ""

    def missing(self) -> list:
        """★ 缺哪几项（★ FR-007 的判据）。"""
        out = []
        if not self.standard:
            out.append("standard")
        if not self.designation:
            out.append("designation")
        if not self.pitch_mm:
            out.append("pitch_mm")
        if not self.tolerance_class:
            out.append("tolerance_class")
        if not self.material:
            out.append("material")
        return out

    @property
    def complete(self) -> bool:
        return not self.missing()

    def verdict(self) -> dict:
        """★★ 判据（★ FR-007 + SC-005）：

        ★ 缺项 ⇒ **规则判 `INDETERMINATE`**（★ 不是 `PASS`）——
          ★ 与阶段 2 七档同族：**缺依据不得算通过**。
        """
        miss = self.missing()
        if miss:
            return {
                "verdict": "INDETERMINATE",
                "missing": miss,
                "releasing": False,
                "reason": "★ 螺纹工程定义缺 %s ⇒ **缺依据不得算通过**" % miss,
            }
        return {
            "verdict": "PASS",
            "releasing": True,
            "spec": "%s %s × %g（%s，%s）"
            % (
                self.standard,
                self.designation,
                self.pitch_mm,
                self.tolerance_class,
                self.material,
            ),
        }


#: ★ 默认的螺杆螺纹（★ 冻结：Tr20×4，梯形螺纹）
def default_thread() -> ThreadSpec:
    return ThreadSpec(
        standard="GB/T 5796",
        designation="Tr20",
        pitch_mm=4.0,
        tolerance_class="7H/7e",
        material="45钢",
    )


#: ══════════════════════════════════════════════════════════════════════
# 六、整体验收（★ S5）
#: ══════════════════════════════════════════════════════════════════════


def evaluate_vise(
    model: ViseModel,
    *,
    thread: ThreadSpec | None = None,
    turns: float = 5.0,
    readback_mm: float | None = None,
    jaw_dof: int = 1,
    jaw_motions: list | None = None,
    jaw_fixed: bool = False,
) -> dict:
    """★★ **平口钳的整体判定**（★ S5）。

    ★★ 判据（★ 五项都要，★ FR-009：**几何通过 ≠ 功能通过**）：
      ① 共享接口齐
      ② 螺纹工程定义**完整**（★ 缺 ⇒ `INDETERMINATE`）
      ③ 导程→位移**独立核对一致**
      ④ 活动钳口**有自由度且已标注**
      ⑤ 关键规则**无 `INDETERMINATE`**
    """
    out: dict = {}

    #: ① 接口齐
    try:
        model.require(*DEFAULT_INTERFACES)
        out["interfaces_ok"] = True
        out["interfaces"] = {k: v.value for k, v in model.interfaces.items()}
    except ViseError as e:
        out["interfaces_ok"] = False
        out["interfaces_error"] = e.detail

    #: ② 螺纹定义
    th = thread if thread is not None else default_thread()
    out["thread"] = th.verdict()

    #: ③ 传动
    lead = model.get("screw_lead_mm")
    tc = lead_to_travel(lead.value if lead else 0.0, turns, readback_mm=readback_mm)
    out["travel"] = tc.verdict()

    #: ④ 活动钳口
    jf = check_jaw_free(dof=jaw_dof, motions=jaw_motions, is_fixed=jaw_fixed)
    out["jaw"] = jf.verdict()

    #: ⑤ 关键规则（★ 螺纹是唯一的关键规则）
    out["rules"] = {"thread": out["thread"]["verdict"]}
    out["indeterminate"] = [k for k, v in out["rules"].items() if v == "INDETERMINATE"]

    out["ok"] = bool(
        out.get("interfaces_ok")
        and out["thread"]["releasing"]
        and out["travel"]["consistent"]
        and out["jaw"]["releasing"]
        and not out["indeterminate"]
    )
    out["★"] = (
        "★ 五项都要：接口齐 + 螺纹完整 + 传动一致 + 钳口可动 + 无 INDETERMINATE"
        "（★ 几何通过 ≠ 功能通过）"
    )
    return out
