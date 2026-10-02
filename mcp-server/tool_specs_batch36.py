"""第三十六批 MCP 工具声明：**读数与纯数据 11 个**（24h 段 4/5 续 / Spec Kit `153`）。

## ★★★ 选法（★ 让**规则**决定范围；★ 事实 191 的"逐条判"）
```
★ 先在**薄模块**里列"有公开函数、但没工具"的 ⇒ ★ 逐个判**入参能不能表达**：
   ① ★ **规则 3**：★ 全部**无裸坐标** ✓
   ② ★★ **入参能不能表达**（★ 真筛子）：
      · ✅ `custom_property_count(model, config_name='')` / `custom_property_names(model, config_name='')`
      · ✅ `resolve_direction(selector)`（★ **无 COM**，纯查表）· `resolve_point(model, selector, *, body_index=0)`
      · ✅ `sheet_count(model)` / `sheet_names(model)` / `current_sheet_name(model)`
      · ✅ `build_bom_traceability(bom_rows, *, model_path='', drawing_path='', review_path='')`（★ 纯数据）
      · ✅ `build_pack_and_go_audit_matrix(source_path, dependencies, component_records, …)`（★ 纯数据）
      · ✅ `export_assembly_bom_csv(model, output_path, *, include_excluded=False, overwrite=False)`
      · ✅ `list_setter_summary()`（★ **零参**）
      · ⚠ `configure_static_solver(options, …)` 族 5 个 ⇒ ★ 要一个 `options` **宿主对象**
        ⇒ ★★ **需新注入键** ⇒ **本批不挂**（★ 不顺手加键 —— 加了要同步 `RESOLVERS`）
      · ⚠ `custom_property_manager(model, …)` / `require_drawing(model)` ⇒ ★ **取宿主/守卫**，非工具候选
⇒ ★ **本批 11 个** ⇒ `all_specs()` **128 → 139**。
```

## 判据
```
★ 读数为主：★ 判"回 dict / list / int 且不抛"；★ `export_assembly_bom_csv` 判**文件存在且非空**
  （★ 同导出族的判据）；★ `list_setter_summary()` 零参 ⇒ 判"回 dict 非空"。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch36.py
# 定位:   24h 计划 段 4/5 续（Spec Kit `153`）—— 读数与纯数据 11 个。
# 官方依据: `ICustomPropertyManager` / `IDrawingDoc` / `IFeatureManager` 族
#          （★ 见各 `scripts/sw_*.py` 的来源块）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批**不保存文档**（红线）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH36"]

_CFG = "Configuration name; empty = the active configuration."


SPECS_BATCH36 = [
    #: ── 自定义属性（★ 读数）──────────────────────────────────────────────
    ToolSpec(
        name="solidworks_custom_property_count",
        title="Count the Custom Properties",
        module="sw_custom_property", function="custom_property_count",
        inject="model",
        params=[Param("config_name", str, default="", description=_CFG)],
        doc="Return how many custom properties the document (or one configuration) has. "
            "★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_custom_property_names",
        title="List the Custom Property Names",
        module="sw_custom_property", function="custom_property_names",
        inject="model",
        params=[Param("config_name", str, default="", description=_CFG)],
        doc="Return the custom property names as a list. ★ Read-only.",
    ),
    #: ── 几何选择器（★ resolve）──────────────────────────────────────────
    ToolSpec(
        name="solidworks_selector_resolve_direction",
        title="Resolve a Direction Selector to a Vector",
        module="sw_geometry_selectors", function="resolve_direction",
        inject=None,
        params=[Param("selector", str,
                      description="A direction selector name (★ see "
                                  "solidworks_available_direction_selectors).")],
        doc="Resolve a named direction selector to its (x, y, z) vector. "
            "★ Pure lookup — no SolidWorks call.",
    ),
    ToolSpec(
        name="solidworks_selector_resolve_point",
        title="Resolve a Point Selector to Coordinates",
        module="sw_geometry_selectors", function="resolve_point",
        inject="model",
        params=[
            Param("selector", str,
                  description="A point selector name (★ see "
                              "solidworks_available_point_selectors), or \"__current_selection__\"."),
            Param("body_index", int, default=0,
                  description="Zero-based solid-body index. ⚠ Not a persistent reference."),
        ],
        doc="Resolve a named point selector to its (x, y, z) coordinates in MILLIMETRES. "
            "★ No coordinates are passed in (rule 3).",
    ),
    #: ── 工程图读数（★ 轻量）──────────────────────────────────────────────
    ToolSpec(
        name="solidworks_drawing_sheet_count",
        title="Count the Drawing Sheets",
        module="sw_drawing_query", function="sheet_count",
        inject="model",
        params=[],
        doc="Return the number of sheets in the active drawing. ★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_drawing_sheet_names",
        title="List the Drawing Sheet Names",
        module="sw_drawing_query", function="sheet_names",
        inject="model",
        params=[],
        doc="Return the drawing's sheet names as a list. ★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_drawing_current_sheet_name",
        title="Get the Current Drawing Sheet Name",
        module="sw_drawing_query", function="current_sheet_name",
        inject="model",
        params=[],
        doc="Return the name of the sheet currently being edited. ★ Read-only.",
    ),
    #: ── 交付（★ 纯数据 + 一个导出）──────────────────────────────────────
    ToolSpec(
        name="solidworks_delivery_bom_traceability",
        title="Build a BOM Traceability Record",
        module="sw_delivery", function="build_bom_traceability",
        inject=None,
        params=[
            Param("bom_rows", list, description="The BOM rows (★ as returned by a BOM tool)."),
            Param("model_path", str, default="", description="Optional model path to record."),
            Param("drawing_path", str, default="", description="Optional drawing path to record."),
            Param("review_path", str, default="", description="Optional review report path."),
        ],
        doc="Build a traceability record from BOM rows. ★ Pure data — no SolidWorks call.",
    ),
    ToolSpec(
        name="solidworks_delivery_pack_and_go_audit_matrix",
        title="Build a Pack-and-Go Audit Matrix",
        module="sw_delivery", function="build_pack_and_go_audit_matrix",
        inject=None,
        params=[
            Param("source_path", str, description="The source document path."),
            Param("dependencies", list, description="The dependency paths found."),
            Param("component_records", list, description="Per-component records."),
        ],
        doc="Build the audit matrix that a Pack-and-Go hand-off is reviewed against. "
            "★ Pure data — no SolidWorks call.",
    ),
    ToolSpec(
        name="solidworks_delivery_export_bom_csv",
        title="Export an Assembly BOM to CSV (read-back verified)",
        module="sw_delivery", function="export_assembly_bom_csv",
        inject="model",
        params=[
            Param("output_path", str, description="Absolute CSV output path."),
            Param("include_excluded", bool, default=False,
                  description="Include components excluded from the BOM."),
            Param("overwrite", bool, default=False, description="Allow replacing an existing file."),
        ],
        doc="Export the assembly BOM to CSV. ★ The criterion is the FILE (exists and non-empty). "
            "⚠ Does NOT save the document.",
    ),
    #: ── 仿真选项（★ 零参那个）──────────────────────────────────────────
    ToolSpec(
        name="solidworks_simulation_list_setter_summary",
        title="List Every Simulation Study-Option Setter",
        module="sw_simulation_study_options", function="list_setter_summary",
        inject=None,
        params=[],
        doc="Return the catalogue of simulation study-option setters (family / name / type) as a "
            "dict. ★ Zero-argument, no SolidWorks call — use it to discover valid "
            "family/name pairs before calling set_option.",
    ),
]
