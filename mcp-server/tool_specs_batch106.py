"""★ 批次 106：规格 217 · B5 收尾 —— 特征阵列读数 + 配合参考 + 装配特征树遍历（3 个纯读）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `specs/217-expose-orphans/plan.md` 的 **B5（收尾）**
# 定位:   ★ 把「已实现但没暴露」的**最后 3 个纯暴露**函数补成工具；判据见 spec.md §四。
# 官方依据: ★ 逐个函数的官方依据在它们各自的 `scripts/` 源码块里（本仓铁律 1）——
#          本文件只做声明式包装 ⇒ 详见：
#            · `scripts/sw_part.py` 的来源块（linear_pattern_report）
#            · `scripts/sw_curve_and_split.py` 的来源块（insert_mate_reference）
#            · `scripts/sw_assembly.py` 的来源块（iter_feature_tree）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **3 个工具** ⇒ 工具数 469 → **472**
# ★★★ 等级如实：★ 本条**只增加暴露面**，★ **不动台账任何 `level`** ✓
#   （★ 挂柜台定则：暴露成功 / 可运行 / 返回语义已验证是**三件事**）✓
# ★★ **开工前的预选族预检已做**（★ 规格 217 第 7 轮定的闸）：
#   ★ 三个函数体**都无选区信号**（★ `linear_pattern_report` · `insert_mate_reference` ·
# ★ `iter_feature_tree` 各自查过：无 `GetSelectedObjectCount2`/`preconditions_held`/「先
# 选中」）✓
#   ⇒ ★ **可作纯暴露** ✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

SPECS_BATCH106 = [
    ToolSpec(
        name="solidworks_linear_pattern_report",
        title="Read Linear Pattern Feature",
        module="sw_part",
        function="linear_pattern_report",
        inject="model",
        params=[
            Param(
                "feature_name",
                str,
                description="★ 被阵列的特征名（★ 名字不是坐标 ⇒ 规则 3 合规）。",
            ),
            Param(
                "spacing_mm",
                float,
                description="★ 实例间距（**毫米**，★ 本仓单位口径见事实 2）。",
            ),
            Param("count", int, description="★ 实例总数（★ 含源特征）。"),
        ],
        doc="★ **读线性阵列特征的参数**（★ 读侧）✓"
        "★★ 与既有两个阵列工具的区别（★ 逐字比对过）："
        "★ `solidworks_sketch_linear_pattern` 是**草图**里的线性阵列（**动作**）；"
        "★ `solidworks_circular_pattern` 是**圆周**阵列（**动作**）；"
        "★ 本工具是**特征**级线性阵列的**读数** ⇒ ★ **建 / 读、线性 / 圆周，三者都不同** ✓"
        "★ 判据：★ 回的是**逐项参数读数**（★ 读不到就如实报，不假装有值）✓",
    ),
    ToolSpec(
        name="solidworks_insert_mate_reference",
        title="Insert Mate Reference",
        module="sw_curve_and_split",
        function="insert_mate_reference",
        inject="model",
        params=[
            Param(
                "name",
                str,
                description="★ 配合参考的名字（★ 名字不是坐标 ⇒ 规则 3 合规）。",
            ),
        ],
        doc="★ **插入配合参考**（★ 动作）。"
        "★★ 与既有配合工具的区别：★ `solidworks_assembly_add_*_mate` 那族是"
        "**在装配体里加配合**；★ 本工具是在**零件**上**定义配合参考**（★ 为后续装配做准备）"
        "⇒ ★ **作用对象不同**，不是重复 ✓"
        "★ 判据：★ **回读**（★ 本仓事实 8：布尔返回值不可信）—— ★ 用特征树/配合参考的读侧工具复核。",
    ),
    ToolSpec(
        name="solidworks_assembly_iter_feature_tree",
        title="Iterate Assembly Feature Tree",
        module="sw_assembly",
        function="iter_feature_tree",
        inject="model",
        read_only=True,
        params=[],
        doc="★ **遍历装配体的特征树**（★ 读侧）：★ 回一份**逐节点**的清单 ✓"
        "★★ 与既有 `solidworks_assembly_list_components` 的区别：★ 那个只列**组件**；"
        "★ 这个遍历**整棵树**（★ 组件 + 特征 + 配合都在其中）⇒ ★ **范围更宽** ✓"
        "★ 判据：★ 回的是 JSON 化清单（★ 读不到就如实报，不假装有内容）✓",
    ),
]
