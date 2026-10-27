"""第十批 MCP 工具声明 —— **把 127 轮攒下来的可用入口接出去**。

## 本批为什么存在
`042`~`046`（轮 123~127）查证并接出了一批**可用的高层入口**，但它们**只活在 `scripts/` 里**：
```
sw_part.get_bounding_box                      （轮 127，真机 8/8，偏差 0.00e+00）
sw_hole_features.list_hole_standards          （轮 124，真机 6/6，15 条真实标准）
sw_hole_features.list_fastener_types          （轮 125，真机 11/11，14 条）
sw_hole_features.list_fastener_table_types    （轮 125，真机 11/11）
```
★ 与 `014`/`015` 的「孤立函数从没跑过」相对：这几个**跑过了**，
但**还没接出去** —— 不接出去，**外部使用者拿不到**。

## ⚑ 一个需要说清的点：这三个要的是 **`ISldWorks`**（不是活动文档）
`list_*` 三个要的是 **`ISldWorks`** —— 而 `tool_registry` 的**注入键字面上等于 `inject` 的值**
（`register()` **不传 `inject_as`**）⇒ ★★ **`inject` 必须等于目标函数的首参名**。
★ 本文件这三条的 `inject` 原先是 **"sw_app"**，而函数首参叫 **`sw`** ⇒ ★ **真机报
`TypeError: … unexpected keyword argument 'sw_app'`**（2026-10-03 接手轮实测）。
⇒ ★ 已改为 **`inject="sw"`**，并在 `register_capabilities.RESOLVERS` 里加了 **`"sw"`** 一行
（复用同一个 `resolve_sw_app`）——★ **加一行正是那张表的设计用途**。
★ 修后真机复验：返回真实的孔标准表（`ANSI Inch` / `ANSI Metric` / `BSI` / `DIN` …）✓

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   mcp-server/tool_specs_batch10.py
# 定位:   把轮 123~127 查证并接出的 4 个高层入口声明为 MCP 工具。
#         每条声明的 `module`/`function` 指向 `scripts/` 里**已存在且真机跑过**的函数；
#         参数**逐条照真实签名抄**（守卫测试用 `inspect.signature` 核）。
# 官方签名依据: 不适用（本文件只做参数搬运，不做 COM 调用；
#         被搬运的函数各自的官方依据在其源码的来源块里）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH10"]


SPECS_BATCH10 = [
    ToolSpec(
        name="solidworks_part_bounding_box",
        title="Get Part Bounding Box",
        module="sw_part",
        function="get_bounding_box",
        read_only=True,  # ⚑ 本批 4 条**都是查询**（不改几何、不改文档）
        inject="model",
        evidence=(
            "Get the bounding box of the first solid body. ⚠⚠ SOLIDWORKS documents the returned values as APPROXIMATE a"
            "nd says they 'should not be used for comparison or calculation purposes'; the box may also vary after a re"
            "build. Use this for a rough overview only. ⚠ Units are MILLIMETRES (measured on SW 2026 SP4.1: an 80x60x50"
            " mm box returns 80/60/50, not 0.08/0.06/0.05)."
        ),
        doc=(
            "Get the bounding box of one solid body in millimetres. Read-only; the values are approximate and SolidWork"
            "s states they must not be used for comparison or calculation, and the box can change after a rebuild, so t"
            "reat it as a rough overview only."
        ),
        param_alias={},
        params=[
            Param(
                "body_index", int, default=0, description="Zero-based index of the solid body; defaults to 0."
            ),
            Param(
                "include_hidden",
                bool,
                default=False,
                description="Whether hidden bodies are included; defaults to false.",
            ),
        ],
    ),
    ToolSpec(
        name="solidworks_hole_standards",
        title="List Hole Wizard Standards",
        module="sw_hole_features",
        function="list_hole_standards",
        read_only=True,  # ⚑ 本批 4 条**都是查询**（不改几何、不改文档）
        inject="sw",
        evidence=(
            "List the Hole Wizard standards available for a hole type (official ISldWorks.GetHoleStandardsData + IHoleS"
            "tandardsData.GetHoleStandards). Returns [{id, name}, ...]; the two out parameters are paired positionally."
            " ⚠ Officially returns null when hole_type_id is 5 (swWzdLegacy)."
        ),
        doc=(
            "List the Hole Wizard standards available for one hole type, as id and name pairs. Read-only; the two outpu"
            "t lists are paired by position, and hole type 5, the legacy type, officially returns nothing."
        ),
        param_alias={},
        params=[
            Param(
                "hole_type_id",
                int,
                default=0,
                description=(
                    "Hole type from the general hole type enum; 5 is the legacy type and yields no data. Defaults to 0."
                ),
            ),
        ],
    ),
    ToolSpec(
        name="solidworks_fastener_types",
        title="List Hole Wizard Fastener Types",
        module="sw_hole_features",
        function="list_fastener_types",
        read_only=True,  # ⚑ 本批 4 条**都是查询**（不改几何、不改文档）
        inject="sw",
        evidence=(
            "List the fastener types under a Hole Wizard standard. Returns [{id, name}, ...]. ⚠ The names follow the SO"
            "LIDWORKS UI language (a Chinese UI returns Chinese names); do not assume English. Use an id from this list"
            " as fastener_id elsewhere. ⚠ Internally the IHoleStandardsData object must be primed with GetHoleStandards"
            " first, otherwise SOLIDWORKS returns False (measured); this function does that."
        ),
        doc=(
            "List the fastener types available under one Hole Wizard standard, as id and name pairs. Read-only; the nam"
            "es follow the SolidWorks interface language, so a Chinese interface returns Chinese names, and an id from "
            "this list is the fastener id the table-type tool expects."
        ),
        param_alias={},
        params=[
            Param(
                "standard_name",
                str,
                default="",
                description=(
                    "Standard name taken from solidworks_hole_standards, for example ANSI Inch. Defaults to empty."
                ),
            ),
            Param(
                "hole_type_id",
                int,
                default=0,
                description=(
                    "Hole type from the general hole type enum; 5 is the legacy type and yields no data. Defaults to 0."
                ),
            ),
        ],
    ),
    ToolSpec(
        name="solidworks_fastener_table_types",
        title="List Hole Wizard Fastener Table Types",
        module="sw_hole_features",
        function="list_fastener_table_types",
        read_only=True,  # ⚑ 本批 4 条**都是查询**（不改几何、不改文档）
        inject="sw",
        evidence=(
            "List the fastener table type ids for one fastener (official IHoleStandardsData.GetFastenerTableTypes). ⚠ T"
            "he official second parameter is an Int32 FASTENER ID (from solidworks_fastener_types), not a size name - p"
            "assing a size name raises a type-mismatch error. Returns a list of ints."
        ),
        doc=(
            "List the fastener table type ids for one fastener under a Hole Wizard standard. Read-only; the second argu"
            "ment must be a fastener id from solidworks_fastener_types and not a size name, because a size name raises "
            "a type-mismatch error."
        ),
        param_alias={},
        params=[
            Param(
                "standard_name",
                str,
                default="",
                description="Standard name taken from solidworks_hole_standards. Defaults to empty.",
            ),
            Param(
                "fastener_id",
                int,
                default=0,
                description=(
                    "Fastener id from solidworks_fastener_types, as a number and not a size name; defaults to 0."
                ),
            ),
            Param(
                "hole_type_id", int, default=0, description="Hole type from the general hole type enum. Defaults to 0."
            ),
        ],
    ),
]
