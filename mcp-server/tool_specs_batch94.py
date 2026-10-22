"""★ 批次 94：规格 209 · B2-4 —— 隐藏/显示**选中的**草图（`BlankSketch` / `UnblankSketch`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `scripts/sw_sketch.py`（本轮追加段）
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B2-4** · 外部项目 idx **175 `hide_al
#           l_sketches`**。
# ★★★ 裁决书的硬约束（§九）逐字：「官方 `BlankSketch` 逐字是「Hides the **selected** ske
# tches」
# ⇒ ★ **官方没有 "all" 这个语义**（是别家自己许的）⇒ 工具名**不许叫 `hide_all_sketches`*
# *」·
#     「★ 别家**零选区 + 返回常量** = **规则 6 的反例**」✓
# ⇒ ★ 本批工具名 = **`solidworks_sketch_set_blanked`**（动词用官方的 Blank、**不承诺 all
# **）；
#     ★★ 收**声明式选择器**（不新开「全隐藏」那条官方没有的路）✓
# 官方依据: `C:\\swapi\\types\\IModelDoc2\\{BlankSketch,UnblankSketch}.md`（都零参回 `vo
#           id`；
#   ★ `BlankSketch` 那页**既无 Returns 也无 Remarks**）·
# ★★ `C:\\swapi\\types\\IFeature\\Visible.md`（`System.int Visible {get;}` → `swVisibili
# tyState_e`）
#   —— ★ **这是「隐藏了没有」的唯一官方回读入口**（官方示例里只有肉眼）·
# `C:\\swapi\\enums\\swVisibilityState_e.md`（Hide=1 · Shown=2 · Unknown=3，**没有 0**）
# ·
# `C:\\swapi\\examples\\Hide_and_Show_Sketches_Example_VB.md`（★ 调用序：**先在树里选中
# 草图**，
#   再 `BlankSketch`；显示同样要先选中）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **1 个工具** ⇒ 工具数 442 → **443**
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH94"]

SPECS_BATCH94 = [
    ToolSpec(
        name="solidworks_sketch_set_blanked",
        title="Hide / Show the SELECTED Sketches (BlankSketch / UnblankSketch)",
        module="sw_sketch",
        function="set_sketch_blanked",
        inject="model",
        params=[
            Param(
                "selection",
                str,
                default="__current_selection__",
                description='**声明式选择器**（★ 规则 3）—— `"__current_selection__"`'
                "（★ 官方示例的前置就是「先在树/图形区里选中要隐藏的草图」）"
                "或**逗号分隔的草图特征名**（★ 事实 32：**特征可以按名字选**，"
                "草图段/实体不行）。",
            ),
            Param(
                "blank",
                bool,
                default=True,
                description="`True` ⇒ `IModelDoc2::BlankSketch()`（隐藏）· "
                "`False` ⇒ `IModelDoc2::UnblankSketch()`（显示）。",
            ),
        ],
        doc="★ **隐藏 / 显示选中的草图**（官方 `IModelDoc2::BlankSketch` / `UnblankSketch`，"
        "★ **两个都零参、都回 `void`**）—— "
        "★★ **官方摘要逐字是「Hides the *selected* sketches」** ⇒ "
        "★ **官方没有「全部」这个语义** ⇒ ★ 本工具**不叫 `hide_all_sketches`、也不实现它** ✓ "
        "★★ **判据（规则 6）**：★ 它回 `void` ⇒ 只能回读 ⇒ ① **选区计数**（事实 8：不许信返回值）"
        "② ★★ **`IFeature::Visible` 的前后读数**（`swVisibilityState_e`：Hide=1 · Shown=2 · Unknown=3）"
        "—— ★ 要求**真的变了**才判 `ok`；★ **读不到 ≠ 没变**（两者在返回值里分开）✓ "
        "⚠ 官方示例的判据只有肉眼（「Examine the graphics area」）⇒ ★ 本条的价值就是**把那个"
        "回读入口定出来**（★ 这正是裁决书点名的真风险）✓",
    ),
]
