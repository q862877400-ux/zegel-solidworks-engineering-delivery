"""第五批 MCP 工具声明：**孤立能力**里签名可直接暴露的 5 个。

## 为什么是这 5 个（2026-10-01 轮 90，Spec Kit `012`）
`tools/probe_unexposed_functions.py` 量出：`scripts/` 有 779 个公开函数，
被工具引用的只有 **72**（下界），其中 **308 个「孤立能力」**（既没暴露、也没人调用）。
本批从「**签名兼容现有注入**」的那 22 个里，挑 5 个**最实用且只读**的：

| 函数 | 模块 | 为什么值得暴露 |
|---|---|---|
| `current_selection` | `sw_selection_spec` | 查当前选区（**AI 最需要**：知道用户/上一步选了什么）|
| `clear_selection` | `sw_selection_spec` | 清选区（每次操作的收尾动作）|
| `set_standard_view` | `sw_review` | 切标准视图（出图/复核前的准备）|
| `list_render_materials` | `sw_render_material` | 列外观材质（复核外观用）|
| `collect_appearance_evidence` | `sw_render_material` | 外观证据（与「证据驱动」一贯做法一致）|

⚠ **只挑只读或缺省安全的**：`current_selection` / `list_render_materials` /
`collect_appearance_evidence` 是**纯读**（`read_only=True`）；
`clear_selection` 与 `set_standard_view` 改的是**视图/选择状态**，不碰几何。

## 与既有批次的关系
形式与 `tool_specs_batch1..4` 完全一致，由 `register_capabilities.py` 的
`BATCH_MODULES` 统一注册（**不新增注册路径**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch5.py
# 定位:   「孤立能力暴露」的第一步 —— 只做**签名可直接暴露**的那批。
# 官方签名依据: 不适用（只做参数搬运；被搬运函数的依据在其源码来源块里）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH5"]


SPECS_BATCH5 = [
    ToolSpec(
        name="solidworks_current_selection",
        title="Current Selection",
        module="sw_selection_spec",
        function="current_selection",
        inject="model",
        read_only=True,
        evidence=(
            "Read the current selection set (optionally filtered to one selection mark)."
        ),
        doc=(
            "Read the current selection set as a list of objects. Read-only; an empty selection returns an empty list, "
            "and mark restricts which selection marks are returned."
        ),
        param_alias={},
        params=[
            Param(
                "mark",
                int,
                default=-1,
                description="Selection mark to read; -1 means all marks. Defaults to -1.",
            ),
        ],
    ),
    ToolSpec(
        name="solidworks_clear_selection",
        title="Clear Selection",
        module="sw_selection_spec",
        function="clear_selection",
        inject="model",
        evidence=(
            "Clear the current selection set."
        ),
        doc=(
            "Clear the current selection set of the active document. Clears every selected entity, changes no geometry,"
            " and does not save the document."
        ),
        param_alias={},
        params=[],
    ),
    ToolSpec(
        name="solidworks_set_standard_view",
        title="Set Standard View",
        module="sw_review",
        function="set_standard_view",
        inject="model",
        evidence=(
            "Switch the model to a named standard view (e.g. isometric, front, top)."
        ),
        doc=(
            "Switch the model to a named standard view such as isometric, front or top. It changes the display orientat"
            "ion and zooms to fit; a name it does not recognize is passed to SolidWorks as a view name. It changes no g"
            "eometry and does not save the document."
        ),
        param_alias={},
        params=[
            Param(
                "view_name",
                str,
                default="isometric",
                description=(
                    "Standard view name such as isometric, front or top; an unrecognized name is passed to SolidWorks a"
                    "s a view name. Defaults to 'isometric'."
                ),
            ),
        ],
    ),
    ToolSpec(
        name="solidworks_list_render_materials",
        title="List Render Materials",
        module="sw_render_material",
        function="list_render_materials",
        inject="model",
        read_only=True,
        evidence=(
            "List the render materials available in the active document."
        ),
        doc=(
            "List the render-material appearance objects defined in the active document. Read-only; an empty document r"
            "eturns an empty list, and the count is read separately to trim the returned array."
        ),
        param_alias={},
        params=[],
    ),
    ToolSpec(
        name="solidworks_collect_appearance_evidence",
        title="Collect Appearance Evidence",
        module="sw_render_material",
        function="collect_appearance_evidence",
        inject="model",
        read_only=True,
        evidence=(
            "Collect appearance evidence for the active document (read-only, for verification). ★ 别名: appearance, bac"
            "kground, scene"
        ),
        doc=(
            "Collect appearance evidence for the active document as one row per appearance. Each row carries ambient, d"
            "iffuse, specular, roughness, transparency and emission. Read-only; use it to verify that an appearance cha"
            "nge actually landed."
        ),
        param_alias={},
        params=[],
    ),
]
