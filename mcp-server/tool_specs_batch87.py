"""★ 批次 87：由 Bunny 扇出产出、**经门禁**（`tools/check_bunny_toolspec_rows.py`）过滤后的 ToolSpec 声明。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   sw_costing · sw_selection
# 定位:   ★ 规格 `specs/204-tool-ramp/spec.md` 的批 87；
#         ★★ **本文件由 `tools/build_toolspec_batch_from_rows.py` 生成** ——
#         行来自 Bunny 子代理（**只读官方源与仓库**），而**判据、门禁、真机、提交归主线** ✓
# 官方依据: 逐行的 `official_file` / `official_signature` 见下表（★ 每条都是官方页的逐字
#           签名）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **2 个工具**
# ⚠ 生成器**只收 `exposable=True` 且门禁 0 问题的行**（★ 被门禁挡下的 0 行见 `output/`）
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH87"]

SPECS_BATCH87 = [
    ToolSpec(
        name="solidworks_selection_clear_colors",
        title="Clear All Selection Colors (ISelectionMgr.ClearSelectionColors)",
        module="sw_selection",
        function="clear_selection_colors",
        inject="selection",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 ClearSelectionColors.md）：`void ClearSelectionColors()`。官方页正文只有一句描述逐"
            "字「Cleans all of selection color settings.」；★ 该页**没有 `## Remarks` 段**（`## See Also` 里逐字两条：`"
            "[[ISelectionMgr Interface]]` · `[[ISelectionMgr Members]]` · `[[ISelectionMgr::SelectionColor Property]]` "
            "⇒ ★ 官方自己把它和 `SelectionColor` 属性配成一对）。★ CHM VB6 页 `SldWorks~SelectionMgr~ClearSelectionColo"
            "rs"
        ),
        doc="★ 官方签名（逐字，来自 ClearSelectionColors.md）：`void ClearSelectionColors()`。"
             "官方页正文只有一句描述逐字「Cleans all of selection color settings.」；★ 该页**没有 `## Remarks` "
             "段**（`## See Also` 里逐字两条：`[[ISelectionMgr Interface]]` · `[[ISelectionMgr Members]]` · "
             "`[[ISelectionMgr::SelectionColor Property]]` ⇒ ★ 官方自己把它和 `SelectionColor` 属性配成一对）。★ CHM "
             "VB6 页 `SldWorks~SelectionMgr~ClearSelectionColors",
    ),
    ToolSpec(
        name="solidworks_costing_set_default_template",
        title="Set the Default Costing Template of a Category",
        module="sw_costing",
        function="set_default_template",
        inject="defaults",
        params=[
            Param("category", int, default=0, description=""),
            Param("template_name", str, default="", description=""),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_costing.py）：`查不到（C:\\swapi\\types\\ICostingDefaults\\SetTemplateName.md 不"
            "存在 ⇒ 无 **Signature**: 行可抄）。★ 第三源（出厂程序集纯元数据反射）逐字：`Void SetTemplateName(Int32, St"
            "ring)` —— D:\\AI\\SW\\_raw\\reflect\\iface_sldcostingapi.txt:288（位于 `#`。★ 真源是**本仓** `scripts/sw_c"
            "osting.py` 的 `set_default_template`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到官方 ## Remarks（"
            "四册 CHM 无 costing 册 + C:\\swapi 无该接口页）。★ 出厂反射只给签名、**没有参数语义**。⚠ 首参 Int32 的语义"
            "（「页签序号」还是「模板类别」？）两套官方源都查不到 ⇒ 本工具原样透传、**不解释**（铁律 5）。⚠ 返回类型是 "
            "Void ⇒ 源码 `set_default_template` 用 `_checked(...)` 的**异常*"
        ),
        doc="★ 官方签名（逐字，来自 sw_costing.py）：`查不到（C:\\swapi\\types\\ICostingDefaults\\SetTemplateName.md "
             "不存在 ⇒ 无 **Signature**: 行可抄）。★ 第三源（出厂程序集纯元数据反射）逐字：`Void SetTemplateName(Int32, "
             "String)` —— D:\\AI\\SW\\_raw\\reflect\\iface_sldcostingapi.txt:288（位于 `#`。★ 真源是**本仓** "
             "`scripts/sw_costing.py` 的 `set_default_template`（★ 它不是 SolidWorks API 成员，故无官方页）—— "
             "查不到官方 ## Remarks（四册 CHM 无 costing 册 + C:\\swapi 无该接口页）。★ 出厂反射只给签名、"
             "**没有参数语义**。⚠ 首参 Int32 的语义（「页签序号」还是「模板类别」？）两套官方源都查不到 ⇒ "
             "本工具原样透传、**不解释**（铁律 5）。⚠ 返回类型是 Void ⇒ 源码 `set_default_template` 用 `_checked(...)` "
             "的**异常*",
    ),
]
