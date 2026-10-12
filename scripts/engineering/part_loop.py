"""★ EC05 首个零件工程闭环 —— 独立参考值 / 冻结扰动集 / 五项回读判定（★ 离线部分）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC05**（★ T01–T08 逐字）
#         `specs/307-ec05-first-part-loop/spec.md`（★ 8 FR · ★ **冻结的扰动集**）
#         `scripts/engineering/rules.py`（★ EC02 的 `hole_edge_margin` —— ★ **复用**）
#         `scripts/engineering/jobs.py`（★ EC04 的 `VersionBinding` —— ★ **复用**）
# 定位:   ★ **EC05** 的**离线部分**（★ 参考值 / 扰动集 / 判定）。
#         ★★★ 计划 §5 EC05 验收逐字：「★ 原尺寸与**至少三组不同类型参数扰动**均有测试；
#           ★ 保存重开和工程图无悬空；★ **所有通过项都绑定同一模型版本**。
#           ★ **具体扰动集合由 spec 冻结，不在验收时删掉失败点**」
# 官方依据: 不适用（本仓的工程闭环层 —— ★ **不调 SolidWorks API**）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件（★ **纯离线** —— ★ 真机部分在 `output/` 的探针里）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "READBACK_ITEMS", "DISTURBANCE_SET", "Disturbance",
    "reference_plate_volume", "reference_hole_positions",
    "readback_verdict", "check_disturbance_coverage",
    "load_case_allows_strength", "PartLoopResult",
    "DofPlan", "check_dof_plan", "config_switch_verdict", "export_compare_verdict",
]


# ══════════════════════════════════════════════════════════════════════
# 一、★★★★★ 五项独立回读（★ FR-005 · EC05-T05）
# ══════════════════════════════════════════════════════════════════════

#: ★★ **必须独立回读的五项**（★ 逐字承 EC05-T05：★「★ 独立回读**孔径/位置/轮廓/体数/材料**」）
READBACK_ITEMS = ("hole_diameter", "hole_position", "outline", "body_count", "material")


def readback_verdict(measured: dict, expected: dict, *,
                     tolerances: dict | None = None) -> dict:
    """★★★★ **五项回读判定**（★ 逐字承 EC05-T05）。

    ★★★ **判据（★ 全回读 —— ★ 不看 API 返回值）**：
      · ★ 五项**都要有**读数；★ 缺一项 ⇒ ★ `unknown`（★ **不放行**）
      · ★ 每项在**容差内** ⇒ `pass`；★ 超出 ⇒ `fail`
    ★★ **依据（★ 承 EC00 的 `contracts/effects.md` §三）**：
      ★「★★ **`readback_ok == False` ⇒ `effect_status` 必须是 `unknown`**，★ **不得 `pass`**」。
    """
    tol = dict(tolerances or {})
    per_item: dict = {}
    for item in READBACK_ITEMS:
        if item not in measured or item not in expected:
            per_item[item] = {"status": "unknown",
                              "reason": "★ 缺读数（★ measured 或 expected 没有它）"}
            continue
        m, e = measured[item], expected[item]
        if isinstance(m, (int, float)) and isinstance(e, (int, float)):
            t = float(tol.get(item, 0.0))
            ok = abs(float(m) - float(e)) <= t
        else:
            ok = (m == e)
        per_item[item] = {"status": "pass" if ok else "fail",
                          "measured": m, "expected": e,
                          "tolerance": tol.get(item)}
    #: ★★ **整体**：★ 有 `unknown` ⇒ 整体 `unknown`；★ 有 `fail` ⇒ 整体 `fail`
    statuses = {v["status"] for v in per_item.values()}
    if "unknown" in statuses:
        overall = "unknown"
    elif "fail" in statuses:
        overall = "fail"
    else:
        overall = "pass"
    return {"overall": overall, "items": per_item,
            "releasing": overall == "pass"}


# ══════════════════════════════════════════════════════════════════════
# 二、★★★★★ 独立参考值（★ FR-002 · EC05-T02 —— ★ 不取自被测实现）
# ══════════════════════════════════════════════════════════════════════

def reference_plate_volume(width_m: float, height_m: float, thickness_m: float) -> float:
    """★★ **独立参考体积**（★ 手写公式 —— ★ **不共享被测实现**）。

    ★★ 依据（★ 承 EC02 的 V6 与 EC00 的双盲纪律）：
      ★「★★ **`tolerance_source` 不得取自被测实现**」。
    """
    return float(width_m) * float(height_m) * float(thickness_m)


def reference_hole_positions(hole_count: int, spacing_m: float, *,
                             start_x: float = 0.0, y: float = 0.0) -> list:
    """★★ **独立参考孔位**（★ 手写 —— ★ 等距排布）。

    ★★ 判据（★ EC05-T02）：★「★ 建立独立参考几何……**孔坐标验收值**」。
    """
    if hole_count <= 0:
        return []
    return [{"x": start_x + i * float(spacing_m), "y": float(y)}
            for i in range(int(hole_count))]


# ══════════════════════════════════════════════════════════════════════
# 三、★★★★★ 冻结的扰动集（★ 逐字承验收：「★ 具体扰动集合由 spec 冻结」）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Disturbance:
    """★ 一组扰动（★ 带**类型** —— ★ 验收要求「**类型不同**」）。"""

    id: str
    kind: str                     #: ★ `dimension` / `position` / `relation`
    description: str
    target: str                   #: ★ 动哪个参数
    value: Any = None
    #: ★★ **为什么选它**（★ 可复核）
    why: str = ""


#: ★★★ **冻结的三组扰动**（★ 逐字承 `spec.md` §四 —— ★ **不许在验收时换掉**）
#:   ★★ 三组**类型互异**：★ `dimension`（尺寸）· `position`（位置）· `relation`（关系）
DISTURBANCE_SET = (
    Disturbance(
        id="P1", kind="dimension",
        description="★ 板厚取**域下限**", target="thickness", value="low",
        why="★ 边界值 —— ★ 最易暴露「差一点就废」（★ 与 P2/P3 类型不同：★ 它动**连续量**）",
    ),
    Disturbance(
        id="P2", kind="position",
        description="★ 孔距取**域上限**", target="hole_spacing", value="high",
        why="★ 与 P1 类型不同 —— ★ 它动的是**布局**不是尺寸（★ 且上限最容易**破边**）",
    ),
    Disturbance(
        id="P3", kind="relation",
        description="★ 关系从 `perpendicular` 换成 `coincident`", target="relation",
        value="coincident",
        why="★ 与 P1/P2 类型不同 —— ★ 它动的是**约束语义**（★ 不是数值）",
    ),
)


def check_disturbance_coverage(disturbances: tuple = DISTURBANCE_SET) -> dict:
    """★★★★ **扰动覆盖检查**（★ 逐字承验收：「★ **至少三组不同类型**参数扰动」）。

    ★★ 两条都要满足：
      · ★ **至少三组**
      · ★★ **类型互异**（★ 「不同类型」是字面要求）
    """
    kinds = [d.kind for d in disturbances]
    unique = sorted(set(kinds))
    return {
        "count": len(disturbances),
        "kinds": kinds,
        "unique_kinds": unique,
        "has_at_least_three": len(disturbances) >= 3,
        "kinds_all_distinct": len(unique) == len(kinds),
        "ok": len(disturbances) >= 3 and len(unique) == len(kinds),
    }


# ══════════════════════════════════════════════════════════════════════
# 四、★★★★★ 缺载荷不给强度结论（★ FR-001 · EC05-T01）
# ══════════════════════════════════════════════════════════════════════

def load_case_allows_strength(load_cases: list) -> dict:
    """★★★★ **缺载荷 ⇒ 不给强度结论**（★ 逐字承 EC05-T01：

    「★ 冻结工况与包络……；★ **缺载荷不能给强度结论**」）。

    ★★★ **本函数只回答「能不能给强度结论」** —— ★ **不给结论本身**
      （★ 那要 EC02 的规则 + ★ 真的载荷）✓
    """
    usable = []
    for lc in (load_cases or []):
        missing = getattr(lc, "is_missing", False)
        mag = getattr(lc, "magnitude", None)
        if not missing and mag is not None:
            usable.append(getattr(lc, "name", "?"))
    if not usable:
        return {"may_give_strength_conclusion": False,
                "reason": "★★ **缺载荷 ⇒ 不给强度结论**（★ EC05-T01 逐字）",
                "usable_load_cases": []}
    return {"may_give_strength_conclusion": True,
            "reason": "★ 有 %d 个可用工况" % len(usable),
            "usable_load_cases": usable}


# ══════════════════════════════════════════════════════════════════════
# 五、★★★★ 闭环结果（★ 绑同一模型版本 —— ★ 逐字承验收）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class PartLoopResult:
    """★★★ **闭环结果**（★ 逐字承验收：★「★ **所有通过项都绑定同一模型版本**」）。"""

    binding: Any = None                  #: ★ EC04 的 `VersionBinding`（★ **三版本**）
    baseline: dict = field(default_factory=dict)
    disturbances: list = field(default_factory=list)
    reopen: dict = field(default_factory=dict)
    failures: list = field(default_factory=list)   #: ★★★ **失败点不许删**

    def all_items_share_one_version(self) -> bool:
        """★★★ **所有通过项绑同一版本**（★ 验收核心）。

        ★★ 判据：★ 每个扰动项与基线项**都记了同一个 binding**。
        """
        if self.binding is None:
            return False
        keys = []
        for item in [self.baseline] + list(self.disturbances):
            b = (item or {}).get("binding")
            if b is None:
                return False
            keys.append((b.contract_hash, b.plan_hash, b.model_revision))
        return len(set(keys)) == 1 and len(keys) >= 1

    def keep_failures(self) -> dict:
        """★★★ **失败点不许删**（★ 逐字承验收：「★ **不在验收时删掉失败点**」）。"""
        return {"failures": list(self.failures), "count": len(self.failures),
                "deleted": False,
                "basis": "★ 验收逐字：「★ **具体扰动集合由 spec 冻结，不在验收时删掉失败点**」"}


# ══════════════════════════════════════════════════════════════════════
# 六、★★★★★ 草图自由度计划（★ FR-003 · EC05-T03）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class DofPlan:
    """★★★★ **自由度/尺寸图**（★ 逐字承 EC05-T03）：

    「★ 草图先设计**自由度/关系/尺寸图**，再执行；★ **有意保留自由度必须标注**，
    ★ **不机械要求全锁死**」。

    ★★★ **本类的意义**：★ 它**逼你先把图画出来**（★ 再执行），
      ★★ 而且**保留的自由度必须写明理由** —— ★ 不是「忘了锁」✗
    """

    entities: int = 0
    #: ★★ 已加的关系（★ 逐条）
    relations: list = field(default_factory=list)
    #: ★★ 已给的尺寸（★ 逐条）
    dimensions: list = field(default_factory=list)
    #: ★★★ **有意保留的自由度**（★ **必须带理由** —— ★ 那是本条的核心）
    intentional_dof: list = field(default_factory=list)

    def total_dof(self) -> int:
        """★ 自由度 = ★ `2 × 实体数 − 关系数 − 尺寸数`（★ 平面草图粗算）。"""
        return max(0, 2 * int(self.entities) - len(self.relations) - len(self.dimensions))

    def add_intentional_dof(self, name: str, why: str) -> None:
        """★★★ **标注一个有意保留的自由度**（★ **理由必填** —— ★ 空理由 ⇒ 拒）。"""
        if not str(why).strip():
            raise ValueError("★★ 有意保留的自由度**必须给理由**（★ EC05-T03 逐字）")
        self.intentional_dof.append({"name": name, "why": why})

    def is_acceptable(self) -> dict:
        """★★★★ **可接受性**（★ 两条：★ ① 自由度要么为 0、★ ② 要么**逐条标注了理由**）。

        ★★★ **逐字承 EC05-T03**：★「★ **有意保留自由度必须标注**，★ **不机械要求全锁死**」
          ⇒ ★★ **不要求自由度必须为 0**（★ 那正是「机械要求全锁死」）✗
        """
        dof = self.total_dof()
        unexplained = dof - len(self.intentional_dof)
        if unexplained > 0:
            return {"ok": False, "total_dof": dof,
                    "explained": len(self.intentional_dof),
                    "unexplained": unexplained,
                    "reason": ("★★ 还有 %d 个自由度**没标注理由** ⇒ 那是「忘了锁」不是「有意保留」"
                               % unexplained)}
        return {"ok": True, "total_dof": dof, "explained": len(self.intentional_dof),
                "unexplained": 0, "reason": "★ 自由度全部有交代（★ 锁死 或 逐条标注理由）"}


def check_dof_plan(plan: DofPlan) -> dict:
    """★ 对外入口（★ 与 `DofPlan.is_acceptable()` 同义 —— ★ 便于判据调用）。"""
    return plan.is_acceptable()


# ══════════════════════════════════════════════════════════════════════
# 七、★★★★ 配置切换与导出的验收口径（★ FR-007 · EC05-T07）
# ══════════════════════════════════════════════════════════════════════

def config_switch_verdict(name_before: str, name_after_create: str,
                          name_after_switch_back: str, target: str) -> dict:
    """★★★ **配置切换判定**（★ 逐字承 EC05-T07：★「★ **保存重开/配置切换/导出比较**」）。

    ★★ 判据（★ 与 EC00 T026 **同一口径**）：★ 名字**真的**变过、★ 且能**切回来**（★ 不串）。
    """
    switched = (name_after_create == target)
    returned = (name_after_switch_back != target)
    return {
        "switched_to_target": switched,
        "switched_back": returned,
        "ok": bool(switched and returned),
        "basis": ("★ 期望：★ %s → %s → 非 %s；★ 实得：★ %s → %s → %s"
                  % (name_before, target, target, name_before, name_after_create,
                     name_after_switch_back)),
    }


def export_compare_verdict(exports: dict) -> dict:
    """★★★ **导出比较**（★ 逐字承 EC05-T07：★「★ ……**导出比较**」）。

    ★★ 判据：★ **每个导出文件必须存在且非零字节**（★ 承 EC00 的「判据是文件」口径）。
    """
    items = {}
    for fmt, info in (exports or {}).items():
        exists = bool(info.get("exists"))
        size = int(info.get("bytes") or 0)
        items[fmt] = {"exists": exists, "bytes": size,
                      "ok": bool(exists and size > 0)}
    ok = bool(items) and all(v["ok"] for v in items.values())
    return {"ok": ok, "items": items,
            "basis": "★ 判据是**文件**（★ 存在且非零字节 —— ★ 承 EC00 的导出口径）"}
