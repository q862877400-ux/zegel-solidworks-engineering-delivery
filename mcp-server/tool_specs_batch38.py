"""第三十八批 MCP 工具声明：**Costing 读数 8 个**（24h 段 4 续 / Spec Kit `155`）。

## ★★★★ 为什么这一片有真价值（★ 而它同时把 `all_specs()` 推过 145）
```
★ **Costing 是 AGENTS.md §〇 点名的三个「真正全网空白域」之一**
  （拓扑优化 · 动画导出 AVI · **Costing**）⇒ ★ 挂它不是凑数。
★ `sw_costing` 有 **25 个公开函数**，★ 而**只挂了 1 个**（`get_costing_manager`）。
⇒ ★★ 其余 24 个的入参都是**宿主对象**（`cost_manager` / `cost_part` / `cost_analysis` /
  `cost_body` / `defaults`）⇒ ★ **要点是"怎么拿到它们"**。
⇒ ★★★ **正解与轮 272 完全同一手法**：★ **注入 `manager`（已有 resolver）+ 包装内部取下游**
  （`CostingModel` / `CostingDefaults` / `GetCostAnalysis()` / `GetBodies()`）—— ★ **不动 RESOLVERS**。
```

## ★ 参数命名（规则 2 / 3）
```
★ 本批**没有长度参数**、★ **没有裸坐标** ✓
★ `category` / `method_name` / `body_name` 都是**登记表/实体名**（★ 不是长度、不是角度）⇒ 不带后缀。
★ ⚠ `body_name` 的合法值由 `solidworks_costing_list_bodies` 给出；`method_name` 由
  `solidworks_costing_read_analysis` 给出（★ **即"会列合法值"的入口**）。
```

## 判据
```
★ 三层（★ 与 `configure_*_solver_report` 一致）：① **取下游对象成功**（★ 失败则写明**卡在哪一环**）；
② **底层返回值如实回传**；③ 把**读了什么**记在返回里。
★ `read_cost_body_report` 对**找不到的实体名**报错时**列出合法值**（★ 事实 204 的形态）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch38.py
# 定位:   24h 计划 段 4 续（Spec Kit `155`）—— Costing 读数 8 个（★ 护城河域）。
# 官方依据: `IModelDocExtension.GetCostingManager` · `ICostManager` / `ICostPart` /
#          `ICostAnalysis` / `ICostingDefaults`（★ 见 `scripts/sw_costing.py` 的来源块）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批**只读、不保存文档**（红线）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH38"]

_CATM = ("Costing category enum value (★ the templates list is the way to discover what exists "
         "for a category).")


SPECS_BATCH38 = [
    ToolSpec(
        name="solidworks_costing_evidence",
        title="Collect the Costing Overview",
        module="sw_costing", function="collect_costing_evidence_report",
        inject="cost_manager",
        params=[],
        doc="Return the Costing overview (body count + whether a cost analysis exists). "
            "★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_costing_read_analysis",
        title="Read the Whole Cost Analysis",
        module="sw_costing", function="read_cost_analysis_report",
        inject="cost_manager",
        params=[],
        doc="Read every readable field of the part's cost analysis as a dict. "
            "★ Use it to discover the valid cost-method names. ★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_costing_body_count",
        title="Count the Costing Bodies",
        module="sw_costing", function="get_body_count_report",
        inject="cost_manager",
        params=[],
        doc="Return how many bodies Costing sees (★ cost is computed per body). ★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_costing_list_bodies",
        title="List the Costing Body Names",
        module="sw_costing", function="list_cost_bodies_report",
        inject="cost_manager",
        params=[],
        doc="Return the Costing body names (★ feed one to solidworks_costing_read_body). "
            "★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_costing_read_body",
        title="Read One Body's Cost Data",
        module="sw_costing", function="read_cost_body_report",
        inject="cost_manager",
        params=[
            Param("body_name", str,
                  description="A body name from solidworks_costing_list_bodies."),
        ],
        doc="Read one body's cost data. ★ An unknown body name fails with the list of valid "
            "names. ★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_costing_list_templates",
        title="List the Costing Templates for a Category",
        module="sw_costing", function="list_costing_templates_report",
        inject="cost_manager",
        params=[Param("category", int, default=0, description=_CATM)],
        doc="Return the Costing template names available for a category. ★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_costing_default_template",
        title="Get the Default Costing Template of a Category",
        module="sw_costing", function="get_default_template_report",
        inject="cost_manager",
        params=[Param("category", int, description=_CATM)],
        doc="Return the default Costing template name for a category. ★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_costing_method_value",
        title="Get the Value of One Costing Method",
        module="sw_costing", function="get_costing_method_report",
        inject="cost_manager",
        params=[
            Param("method_name", str,
                  description="A cost-method name (★ see solidworks_costing_read_analysis)."),
        ],
        doc="Return the current value of one cost method. ★ Read-only.",
    ),
]
