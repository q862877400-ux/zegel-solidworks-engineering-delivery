"""★ 批次 97：规格 209 · B2-2 —— BOM 气泡（`IDrawingDoc::AutoBalloon5`，给「两家矛盾」定案）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `scripts/sw_drawing_create_missing.py::auto_insert_balloons`（★ 能力层**早已实现**，
#         本批做两件事：★ **把判据收紧成纯回读** + ★ **把它挂成工具**）✓
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B2-2** · 外部项目 idx **34 `balloon`**。
#   ★★★ 裁决书硬约束（§一）逐字：「★★ 两家结论**互相矛盾**（Slacker-LLC 说静默无效、
#     Eduardof0nt 直接调并回 `bool(result)`）⇒ **不许照抄任何一家**，必须真机定案」✓
#   ★★ 而**原函数自述「不建 ToolSpec」的理由是过期的**：它写「`AutoBalloon5` 的形参是
#     `AutoBalloonOptions` **COM 对象** ⇒ `Param` 表达不了」—— ★★ 那句说的是**底层成员**，
#     ★ 而**包装函数的形参全是标量**（`layout`/`style`/`size`/…）⇒ ★ **它能挂** ✓
#     （★ 这也是裁决书 §九 的原话：「建议挂在 `auto_insert_balloons` 之上」）
# 官方依据: `C:\\swapi\\types\\IDrawingDoc\\AutoBalloon5.md`（Returns = **Array of INotes**；
#   `## Remarks` 给**四步前置**）· `C:\\swapi\\types\\IView\\GetNoteCount.md`（**判据来源**）·
#   `C:\\swapi\\types\\IModelDocExtension\\InsertBOMBalloon2.md`（单发气泡，四步前置）·
#   ★★ `examples\\Add_Autoballoon_to_Face_Example_VB.md`（**调用序**）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **1 个工具** ⇒ 工具数 445 → **446**
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH97"]

SPECS_BATCH97 = [
    ToolSpec(
        name="solidworks_drawing_insert_balloons",
        title="Insert BOM Balloons into the Selected Drawing View(s) (AutoBalloon5)",
        module="sw_drawing_create_missing", function="auto_insert_balloons",
        inject="model",
        params=[
            Param("layout", int, default=1,
                  description="`swBalloonLayoutType_e`（默认 `swDetailingBalloonLayout_Square = 1`）。"),
            Param("style", int, default=1,
                  description="`swBalloonStyle_e`（默认 `swBS_Circular = 1`）。"),
            Param("size", int, default=5,
                  description="`swBalloonFit_e`（默认 `swBF_5Chars = 5`）。"),
            Param("upper_text_content", int, default=1,
                  description="`swBalloonTextContent_e`（默认 `swBalloonTextItemNumber = 1`"
                              " ⇒ 气泡里显示**件号**）。"),
            Param("upper_text", str, default="", description="气泡上方的自定义文字（默认空）。"),
            Param("layername", str, default="-None-",
                  description="图层名（★ 默认值逐条照**官方示例**，★ 不声称是出厂默认）。"),
            Param("item_number_start", int, default=1, description="件号起始值。"),
            Param("item_number_increment", int, default=1, description="件号增量。"),
            Param("item_order", int, default=1, description="`swBalloonItemNumbersOrder_e`"
                                                            "（默认 `DoNotChangeItemNumbers = 1`）。"),
            Param("edit_balloons", bool, default=True, description="官方 `EditBalloons`。"),
            Param("edit_balloon_option", int, default=1,
                  description="`swEditBalloonOption_e`（默认 `Resequence = 1`）。"),
            Param("reverse_direction", bool, default=False, description="官方 `ReverseDirection`。"),
            Param("ignore_multiple", bool, default=True, description="官方 `IgnoreMultiple`。"),
            Param("insert_magnetic_line", bool, default=True, description="官方 `InsertMagneticLine`。"),
            Param("leader_attachment_to_faces", bool, default=True,
                  description="官方 `LeaderAttachmentToFaces`。"),
        ],
        doc="★ **往选中的视图/图纸里插 BOM 气泡**（官方 `IDrawingDoc::AutoBalloon5`）—— "
            "★★ **本条是裁决书点名要「真机定案」的那一件**（两家外部项目结论互相矛盾）⇒ "
            "★★ **定案（2026-10-06 真机，两格独立对照）**：装配工程图上 "
            "**有没有 BOM 表都插得进去**（各 **Δ=1**、返回数组长度 1）⇒ "
            "★ **Slacker-LLC 的「静默无效」不成立**；★ **Eduardof0nt 的 `bool(result)` 也不能当判据**"
            "（它只是「返回数组非空」）✓ "
            "★★ **判据（规则 6）**：**`sum(IView::GetNoteCount)` 的增量 > 0** —— "
            "★ 返回的数组长度**只回报、不当判据** ✓（★ 本批就为此**收紧了原函数的 `ok`**："
            "它原先依赖返回数组、且 `delta >= 0` 太松）✓ "
            "★★ **前置照官方四步**：① **先选中一个或多个视图 / 图纸** "
            "（★ 官方 Remarks 逐字；★ 若选的是**图纸**，它会插到该图纸的**所有**视图上）"
            "② `CreateAutoBalloonOptions()` ③ 设属性 ④ 调它 —— ★ ②③ **由本工具内部完成** ✓ "
            "⚠ 官方示例的 Preconditions 写着「a drawing **with a BOM table**」—— ★★ **而真机实测"
            "没有 BOM 表照样能插** ⇒ ★ 那句是**例子的环境**、**不是方法的硬前置** ✓",
    ),
]
