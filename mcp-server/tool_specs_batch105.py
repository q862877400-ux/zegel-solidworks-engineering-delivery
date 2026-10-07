"""★ 批次 105：规格 217 · B5/B6 —— 钣金特征遍历 + topology 约束读侧（2 个纯读）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `specs/217-expose-orphans/plan.md` 的 **B5 + B6**
# 定位:   ★ 把「已实现但没暴露」的 **2 个纯读**函数补成工具；判据见 spec.md §四。
# 官方依据: ★ 逐个函数的官方依据在它们各自的 `scripts/` 源码块里（本仓铁律 1）——
#          本文件只做声明式包装 ⇒ 详见：
#            · `scripts/sw_sheet_metal.py` 的来源块（iter_features）
#            · `scripts/sw_topology.py` 的来源块（topology_constraints_report）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **2 个工具** ⇒ 工具数 467 → **469**
# ★★★ 等级如实：★ 本条**只增加暴露面**，★ **不动台账任何 `level`** ✓
#   （★ 挂柜台定则：暴露成功 / 可运行 / 返回语义已验证是**三件事**）✓
# ★★ **开工前的预选族预检已做**（★ 规格 217 第 7 轮定的闸）：★ 两个都**无选区信号**
#   （★ `iter_features` 无 · `topology_constraints_report` 见其函数体）⇒ ★ **可作纯暴露** ✓
# ★ 本批**留下的三个**（★ 下一轮）：`linear_pattern_report` · `insert_mate_reference` ·
#   `iter_feature_tree` —— ★ 它们**没有条目认领**（★ 需先找到合适的归属条目）⇒ ★ 不硬塞 ✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

SPECS_BATCH105 = [
    ToolSpec(
        name="solidworks_sheet_metal_iter_features",
        title="Iterate Sheet-metal Features",
        module="sw_sheet_metal", function="iter_features",
        inject="model",
        read_only=True,
        params=[],
        doc="★ **遍历钣金特征**（★ 读侧）：★ 回一份**逐特征**的清单 ✓"
            "★★ 与既有 `solidworks_weldment_iter_features` 的区别：★ 那个遍历**焊件**特征；"
            "★ 这个遍历**钣金**特征 —— ★ **不是同一族**（★ 已逐字比对过）✓"
            "★ 判据：★ 回的是一份 JSON 化清单（★ 读不到就如实报，★ 不假装有内容）。",
    ),
    ToolSpec(
        name="solidworks_topology_constraints_report",
        title="Read Topology Constraints and Controls",
        module="sw_topology", function="topology_constraints_report",
        inject="study",
        read_only=True,
        params=[],
        doc="★ **读拓扑研究里的约束与控制**（★ 读侧）✓"
            "★ 与既有 `solidworks_topology_list_constraints` 的区别：★ 那个回**布尔清单**"
            "（哪几类**有/没有**）；★ 这个回**逐条的读数**（★ 哪些约束、什么参数）⇒ ★ 更细 ✓"
            "★★ 本仓在规格 216 已定性：★ **建侧**那一族（对称/脱模/质量约束）在本机**整体回 `None`**"
            "（★ 族级边界）⇒ ★ 本工具是**读侧**，★ 用来**观察**那种边界（★ 不是绕过它）✓"
            "⚠ 需要**拓扑研究对象**（★ 注入器给 `study`；★ 没有研究时应报错）。",
    ),
]
