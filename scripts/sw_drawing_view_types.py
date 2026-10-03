"""★ 工程图视图类型：官方枚举 `swDrawingViewTypes_e` 的**单一真源**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（常量单一真源）。★ 2026-10-03（接手轮）为**消除重复**而建。
# 文件:   scripts/sw_drawing_view_types.py
# 定位:   ★★ **为什么要这个文件**（业主当场指出的重复）：
#   本仓原先把「视图类型 ∈ {2, 3}」这个知识**用魔数写在两个地方**：
#     · `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py:1798`
#         `"note_kind": "view_label" if owner_view_type in {2, 3} and not note_text else "note"`
#     · `scripts/sw_review.py:174`
#         `if item.get("type") in {2, 3} and same_sheet(note, item) ...`
#   ⇒ ★ 同一份知识两个家 + **魔数**（2/3 是什么？没人能一眼看出来，改也没人敢改）⚠
#   ★★ 而那个 subskill **本来就 import 顶层 `scripts/`**（`from scripts.sw_review import …`）
#     ⇒ ★ **可以共享一个家**，故把真源放这里、两处都改成引用。
#
#   官方依据（★ 铁律 4：枚举值不许猜，逐字核官方页）：
#     `C:\swapi\enums\swDrawingViewTypes_e.md`（`kind: enum`，`enum_member_count: 10`）
#     ```text
#     | swDrawingAlternatePositionView | 10 = Alternate position view |
#     | swDrawingAuxiliaryView         |  5 = Auxiliary view           |
#     | swDrawingDetachedView          |  9 = Detached view            |
#     | swDrawingDetailView            |  3 = Detail view              |
#     | swDrawingNamedView             |  7 = Named view               |
#     | swDrawingProjectedView         |  4 = Projected (unfolded) view|
#     | swDrawingRelativeView          |  8 = Relative view to the model|
#     | swDrawingSectionView           |  2 = Section view             |
#     | swDrawingSheet                 |  1 = Drawing sheet            |
#     | swDrawingStandardView          |  6 = Standard view            |
#     ```
#
#   ★ `LABELLED_VIEW_TYPES` 的**语义依据**：剖面视图与局部视图**自带标签文字**
#     （`A` / `A-A` 这种）—— 故「视图上那段没有文字的 note 其实是它的标签」只对这两型成立。
#     ⚠ **如实标注限度**：★ 该语义是**从两处既有实现的用法反推**的（它们都把这两型当"带标签"用），
#       ★ **官方枚举页只给数值、不给这个语义** ⇒ ★ 不写成"官方规定"，写成**本仓的定义**。
# 许可:   本仓库 MIT。★ **无第三方代码引入**（枚举值取自官方 API 文档，只作数值依据）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

#: ★ 官方 `swDrawingViewTypes_e` 的**逐字数值**（`C:\swapi\enums\swDrawingViewTypes_e.md`）
SW_DRAWING_SHEET = 1                       # swDrawingSheet                 = 1  Drawing sheet
SW_DRAWING_SECTION_VIEW = 2                # swDrawingSectionView           = 2  Section view
SW_DRAWING_DETAIL_VIEW = 3                 # swDrawingDetailView            = 3  Detail view
SW_DRAWING_PROJECTED_VIEW = 4              # swDrawingProjectedView         = 4  Projected (unfolded) view
SW_DRAWING_AUXILIARY_VIEW = 5              # swDrawingAuxiliaryView         = 5  Auxiliary view
SW_DRAWING_STANDARD_VIEW = 6               # swDrawingStandardView          = 6  Standard view
SW_DRAWING_NAMED_VIEW = 7                  # swDrawingNamedView             = 7  Named view
SW_DRAWING_RELATIVE_VIEW = 8               # swDrawingRelativeView          = 8  Relative view to the model
SW_DRAWING_DETACHED_VIEW = 9               # swDrawingDetachedView          = 9  Detached view
SW_DRAWING_ALTERNATE_POSITION_VIEW = 10    # swDrawingAlternatePositionView = 10 Alternate position view

#: ★ **本仓定义**（★ 不是官方规定，语义见文件头"限度"段）：
#:   **自带标签文字**的视图类型 = **剖面视图** + **局部视图**。
#:   ⇒ ★ 判据「视图上那段**没有文字**的 note 是它的标签」**只对这两型成立**。
LABELLED_VIEW_TYPES = frozenset({SW_DRAWING_SECTION_VIEW, SW_DRAWING_DETAIL_VIEW})

__all__ = [
    "SW_DRAWING_SHEET", "SW_DRAWING_SECTION_VIEW", "SW_DRAWING_DETAIL_VIEW",
    "SW_DRAWING_PROJECTED_VIEW", "SW_DRAWING_AUXILIARY_VIEW", "SW_DRAWING_STANDARD_VIEW",
    "SW_DRAWING_NAMED_VIEW", "SW_DRAWING_RELATIVE_VIEW", "SW_DRAWING_DETACHED_VIEW",
    "SW_DRAWING_ALTERNATE_POSITION_VIEW", "LABELLED_VIEW_TYPES",
]
