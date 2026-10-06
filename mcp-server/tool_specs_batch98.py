"""★ 批次 98：规格 209 · B2-3 —— 工程图视图里的中心线（`IDrawingDoc::InsertCenterLine2`）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `scripts/sw_drawing_create_missing.py::insert_center_lines`（本轮新增）
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B2-3** · 外部项目 idx **52 `centerline`**。
#   ★★ 裁决书要求「**须真机定案**」（两家外部项目结论互相矛盾）⇒ ★ **已定案，见下** ✓
#   ★★★ **裁决书建议"与 idx 30 `auto_center_marks` 合并成一条工具两种模式"——我没照做**，
#     理由可核：两条入口的**入参形状不同** —— 本条形参可全做成标量，而 `auto_center_marks`
#     收的是**结构化 requirements 列表** ⇒ `Param` 表达不了 ⇒ ★ 硬合并会造出
#     「一半参数对一半模式无意义」的工具 ⇒ ★ **不合并**（★ 偏离已记进 tasks.md）✓
# 官方依据: `C:\\swapi\\types\\IDrawingDoc\\InsertCenterLine2.md`（零参；摘要逐字
#   「on the **selected entities**」；★ **无 Remarks 也无 Parameters**）·
#   ★★ `examples\\Get_Centerlines_in_Drawing_Example_VB.md`（**调用序**：先选 **COMPONENT**、
#   再按**点**选 **FACE**）· `IView\\GetVisibleEntities2.md` · `IView\\GetCenterLineCount.md` ·
#   `enums\\swViewEntityType_e.md`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **1 个工具** ⇒ 工具数 446 → **447**
# ★★ **诚实边界**：本条真机**只走到"选中成功但产出 0"**，而且**官方前置只复现了一半**
#   （★ 官方是先选 **COMPONENT** 再选面，且它的视图来自**装配**）⇒ 能力标 **`stitched`** ✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH98"]

SPECS_BATCH98 = [
    ToolSpec(
        name="solidworks_drawing_insert_center_lines",
        title="Insert a Centerline in a Drawing View (InsertCenterLine2)",
        module="sw_drawing_create_missing", function="insert_center_lines",
        inject="model",
        params=[
            Param("view_name", str, default="",
                  description="视图名（★ 留空 = 当前图纸**第一个**视图）。"),
            Param("entity_type", str, default="edge",
                  description="`edge`(1) / `vertex`(2) / `face`(3) / `silhouette_edge`(4)"
                              "（官方 `swViewEntityType_e`）—— ★ 取的是**视图里可见的**实体"
                              "（`IView::GetVisibleEntities2`）✓"),
            Param("entity_index", int, default=0,
                  description="选第几个（0 基）—— ★ **声明式**（规则 3：本工具**不收坐标**）。"
                              "★ 官方示例走的是「按点选面」（要猜坐标）⇒ 本工具改走**按对象选**"
                              "（事实 32：`IEntity::Select4`）✓"),
        ],
        doc="★ **在工程图视图里插中心线**（官方 `IDrawingDoc::InsertCenterLine2`，**零参**）—— "
            "★★ **状态：`stitched`**（真机**没建出来**，且★ **官方前置只复现了一半**）—— "
            "★★ **真机读数（2026-10-06 · SW 2026 SP4.1 · 圆柱零件的工程图视图）**："
            "视图里可见实体 **edge=1 · face=1**；`Select4` 按对象选上后 **选区回读 = 1**；"
            "而 `InsertCenterLine2` **回 `None`**、`IView::GetCenterLineCount()` **0 → 0（Δ=0）** ⇒ "
            "★ **「选中了也没产出」** ✓ "
            "★★ **两家外部项目各对一半（定案）**：★ 说「**静默无效**」的那家**不准确** —— "
            "它**并不静默**（返回值就是 `None`）；★ 而说 `bool(result)` 的那家**恰好对**"
            "（`bool(None)` 为假）—— ★★ **但那条判据不能通用**（另有「回非 None 而几何没变」的情形，"
            "★ 只有**回读**才抓得住）✓ "
            "★★ **判据（规则 6）**：① **选区计数**（事实 8：不许信 `Select4` 的返回值）"
            "② ★ **`IView::GetCenterLineCount()` 的前后回读** —— ★ 它回的 `ICenterLine` **不当判据** ✓ "
            "★★ **把两种失败分开记**：**选不上**（选区 0 ⇒ 本工具**在调它之前就报错**，"
            "★ 那不算能力的证据）与 **选了也没用**（Δ=0）✓ "
            "⚠ **前置只复现一半**：官方示例是**先选 `COMPONENT`、再按点选 `FACE`**，"
            "且它的视图来自**装配** ⇒ ★ 本工具那条「先选组件」没走 ⇒ **下一步**见 limitations ✓",
    ),
]
