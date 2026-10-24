"""★ 批次 103：规格 217 · B1（前半）—— 草图读数/关系/按名取草图/相交曲线共 5 项。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `specs/217-expose-orphans/plan.md` 的 **B1**（★ 前半）
# 定位:   ★ 把「已实现但没暴露」的 5 个公开函数补成工具；判据见 spec.md §四。
# 官方依据: ★ **逐个函数的官方依据在它们各自的 `scripts/` 源码块里**（本仓铁律 1）——
#          本文件**不重复抄**签名，只做声明式包装 ⇒ 详见：
#            · `scripts/sw_sketch_dimensions.py` 的来源块（接口/成员逐条）
#            · `scripts/sw_sketch.py` / `scripts/sw_sketch_edit_ops.py` 的来源块
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **5 个工具** ⇒ 工具数 459 → **464**
# ★★★ 等级如实：★ 本条**只增加暴露面**，★ **不动台账任何 `level`**
#   （★ 挂柜台定则：暴露成功 / 可运行 / 返回语义已验证是**三件事**；
#    ★★ 规格 204 的 P4–P6 曾把 339 暴露面缺口误当真实能力缺口而整阶段作废）✓
# ★★ 本批**排除/挪后**（理由留档，防后人重判）：
#   · `add_horizontal_dimension` / `add_vertical_dimension` / `add_path_length_dimension`
#     ⇒ ★ 坐标是**标注放置位置**（规则 3 的书面例外），★ 但**要求先选中实体** ⇒
#       ★ 必须配声明式选择 + 紧邻调用 ⇒ ★ **另立 T-217-01b** ✓
#   · `fully_define_sketch` ⇒ ★ 8 个枚举参数须逐个查官方源（铁律 4）⇒ **另立 T-217-01c** ✓
# · `sw_selection_spec.entity_geometry` ⇒ ★ 其归属条目 `selection_helpers` 的 `mcp_tools
# `
#     尾部**本轮未读到准确原文** ⇒ ★ **不猜**（事实 61 定则②）⇒ **挪到下一批** ✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

SPECS_BATCH103 = [
    ToolSpec(
        name="solidworks_count_sketch_relations",
        title="Count Sketch Relations",
        module="sw_sketch_dimensions",
        function="count_sketch_relations",
        inject="model",
        read_only=True,
        params=[
            Param(
                "filter",
                int,
                default=0,
                description="Relations to count: 0 = all (swAll), 1 = dangling, "
                "2 = over-defining, 3 = external, 4 = defined-in-context, "
                "5 = locked, 6 = broken, 7 = selected entities. "
                "NOTE: -1 is NOT a valid value and silently returns 0.",
            ),
        ],
        doc="★ 数当前草图里的**几何关系**（★ 读侧，回一个整数）。"
        "★★ `filter` 按关系类型筛，**0 = 全数（`swAll`）**；★ 取值表以 "
        "`scripts/sw_sketch_dimensions.py` 里的官方枚举为准。"
        "⚠ **不要传 -1** —— 它不在枚举里，会静默回 0（2026-10-25 修）。"
        "★ 与既有 `solidworks_sketch_fully_defined_status` 的区别：那个读**完全定义状态码**，"
        "★ 这个读**关系条数** —— 两个是不同读数，不是重复工具。"
        "⚠ 需要**活动草图**（没有则报错，不静默回 0）。",
    ),
    ToolSpec(
        name="solidworks_delete_all_sketch_relations",
        title="Delete All Sketch Relations",
        module="sw_sketch_dimensions",
        function="delete_all_sketch_relations",
        inject="model",
        params=[],
        doc="★ **删掉当前草图里的全部几何关系**（★ 动作，回 `bool`）。"
        "★★ **判据请回读**：★ 先 `solidworks_count_sketch_relations` 记数、删后再数一次 "
        "（★ 本仓事实 8：布尔返回值不可信，判据只有回读）。"
        "⚠ 破坏性动作：★ 会**清掉草图的几何关系**（尺寸不受影响，但草图的约束没了）。",
    ),
    ToolSpec(
        name="solidworks_delete_sketch_relation",
        title="Delete One Sketch Relation",
        module="sw_sketch_dimensions",
        function="delete_sketch_relation",
        inject="model",
        params=[
            Param(
                "index",
                int,
                description="★ 关系序号（★ 口径以源码块/官方 `GetSketchRelations` 为准）。",
            ),
            Param(
                "filter",
                int,
                default=-1,
                description="★ 关系类型过滤（-1 = 不过滤）。",
                required=False,
            ),
        ],
        doc="★ **按序号删掉一条几何关系**（★ 动作，回 `bool`）。"
        "★★ 判据同 `delete_all`：**回读计数**（★ 事实 8）。"
        "★ 声明式：★ 参数是**序号**，不是坐标（规则 3）✓。"
        "⚠ 序号越界应报错，不静默。",
    ),
    ToolSpec(
        name="solidworks_sketch_by_name",
        title="Get Sketch by Name",
        module="sw_sketch",
        function="sketch_by_name",
        inject="model",
        read_only=True,
        params=[
            Param(
                "name",
                str,
                description="★ 草图特征名（★ 名字不是坐标 ⇒ 规则 3 合规）。",
            ),
        ],
        doc="★ **按名字取一张草图**（★ 读侧）。"
        "★ 用法：★ 先拿到草图特征名（如 `草图1` / `Sketch1`，★ **随 UI 语言变**，见已知事实 9）⇒ "
        "★ 再喂给需要草图的动作。"
        "⚠ 名字不存在时应报错（★ 不返回空对象让人误以为成功）。",
    ),
]
# ★★ 2026-10-07（规格 217 · T-217-01 第 3 轮）：**`sketch_intersect_curves` 撤出本批** —
# —
# ★ 本仓**预选族门禁**（`scripts/check_preselect_family.py`，已接进 `release_check`）实
# 测判它：
#     「★ 要求先选中相交的两条曲线，★ 而**没有任何选法**」⇒ ★★ **门禁是对的** ✓
#   ★ 它与 `add_*_dimension` 三条**同类**（都要先选中实体）⇒ ★ 一并挪到 **T-217-01b**
#     （★ 那一批统一配**声明式选择 + 紧邻调用**）✓
#   ★★ 记一笔：**这是本规格第一次"门禁在尽职地拦下我自己新加的工具"** —— ★ 判据有效 ✓
