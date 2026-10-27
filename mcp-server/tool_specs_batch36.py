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
        module="sw_custom_property",
        function="custom_property_count",
        inject="model",
        params=[Param("config_name", str, default="", description=(
                                                          "Configuration name to count in; empty reads the active confi"
                                                          "guration. Defaults to empty."
                                                      ))],
        evidence=(
            "Return how many custom properties the document (or one configuration) has. ★ Read-only."
        ),
        doc=(
            "Return how many custom properties the document or one configuration has. Read-only; pass an empty configur"
            "ation name to count the active configuration."
        ),
    ),
    ToolSpec(
        name="solidworks_custom_property_names",
        title="List the Custom Property Names",
        module="sw_custom_property",
        function="custom_property_names",
        inject="model",
        params=[Param("config_name", str, default="", description=(
                                                          "Configuration name to read from; empty reads the active conf"
                                                          "iguration. Defaults to empty."
                                                      ))],
        evidence=(
            "Return the custom property names as a list. ★ Read-only."
        ),
        doc=(
            "Return the custom property names of the document or one configuration as a list. Read-only; pass an empty "
            "configuration name to read the active configuration."
        ),
    ),
    #: ── 几何选择器（★ resolve）──────────────────────────────────────────
    ToolSpec(
        name="solidworks_selector_resolve_direction",
        title="Resolve a Direction Selector to a Vector",
        module="sw_geometry_selectors",
        function="resolve_direction",
        inject=None,
        params=[
            Param(
                "selector",
                str,
                description=(
                    "Direction selector name, using the same outward-normal naming as the face selectors; see solidwork"
                    "s_available_direction_selectors for the accepted values."
                ),
            )
        ],
        evidence=(
            "Resolve a named direction selector to its (x, y, z) vector. ★ Pure lookup — no SolidWorks call."
        ),
        doc=(
            "Resolve a named direction selector to its x, y and z unit vector. Read-only and needs no SolidWorks call a"
            "nd no open document; take the accepted names from solidworks_available_direction_selectors, and it raises "
            "a selector error on an unknown name."
        ),
    ),
    ToolSpec(
        name="solidworks_selector_resolve_point",
        title="Resolve a Point Selector to Coordinates",
        module="sw_geometry_selectors",
        function="resolve_point",
        inject="model",
        params=[
            Param(
                "selector",
                str,
                description=(
                    "Point selector name, or __current_selection__ to use whatever is already selected; see solidworks_"
                    "available_point_selectors for the accepted values."
                ),
            ),
            Param(
                "body_index",
                int,
                default=0,
                description=(
                    "Zero-based index of the solid body the selector is resolved on; the index is not a persistent refe"
                    "rence across rebuilds. Defaults to 0."
                ),
            ),
        ],
        evidence=(
            "Resolve a named point selector to its (x, y, z) coordinates in MILLIMETRES. ★ No coordinates are passed in"
            " (rule 3)."
        ),
        doc=(
            "Resolve a named point selector to its x, y and z coordinates in millimetres. Read-only and needs no SolidW"
            "orks call, and it takes no coordinates because the selector itself names the point; take the accepted name"
            "s from solidworks_available_point_selectors."
        ),
    ),
    #: ── 工程图读数（★ 轻量）──────────────────────────────────────────────
    ToolSpec(
        name="solidworks_drawing_sheet_count",
        title="Count the Drawing Sheets",
        module="sw_drawing_query",
        function="sheet_count",
        inject="model",
        params=[],
        evidence=(
            "Return the number of sheets in the active drawing. ★ Read-only."
        ),
        doc=(
            "Return the number of sheets in the active drawing. Read-only; the count comes straight from the drawing do"
            "cument, so call it while the drawing is the active document."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_sheet_names",
        title="List the Drawing Sheet Names",
        module="sw_drawing_query",
        function="sheet_names",
        inject="model",
        params=[],
        evidence=(
            "Return the drawing's sheet names as a list. ★ Read-only."
        ),
        doc=(
            "Return the names of every sheet in the active drawing. Read-only; call it while the drawing is the active "
            "document, and use solidworks_drawing_current_sheet_name when you only need the sheet being edited."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_current_sheet_name",
        title="Get the Current Drawing Sheet Name",
        module="sw_drawing_query",
        function="current_sheet_name",
        inject="model",
        params=[],
        evidence=(
            "Return the name of the sheet currently being edited. ★ Read-only."
        ),
        doc=(
            "Return the name of the sheet currently being edited. Read-only, and it reads the current sheet object of t"
            "he active drawing; pass the returned name to any tool that takes a sheet name."
        ),
    ),
    #: ── 交付（★ 纯数据 + 一个导出）──────────────────────────────────────
    ToolSpec(
        name="solidworks_delivery_bom_traceability",
        title="Build a BOM Traceability Record",
        module="sw_delivery",
        function="build_bom_traceability",
        inject=None,
        params=[
            Param(
                "bom_rows",
                list,
                description="Bill-of-materials rows, in the form a bill-of-materials tool returns them.",
            ),
            Param(
                "model_path",
                str,
                default="",
                description="Model path to record in the traceability entry. Defaults to empty.",
            ),
            Param(
                "drawing_path",
                str,
                default="",
                description="Drawing path to record in the traceability entry. Defaults to empty.",
            ),
            Param(
                "review_path",
                str,
                default="",
                description="Review report path to record in the traceability entry. Defaults to empty.",
            ),
        ],
        evidence=(
            "Build a traceability record from BOM rows. ★ Pure data — no SolidWorks call."
        ),
        doc=(
            "Build a traceability record linking bill-of-materials rows to the model, drawing and review paths. Read-on"
            "ly and pure data with no SolidWorks call, so it needs no open document; an empty path is simply left out o"
            "f the record."
        ),
    ),
    ToolSpec(
        name="solidworks_delivery_pack_and_go_audit_matrix",
        title="Build a Pack-and-Go Audit Matrix",
        module="sw_delivery",
        function="build_pack_and_go_audit_matrix",
        inject=None,
        params=[
            Param("source_path", str, description="Path of the source document the hand-off starts from."),
            Param("dependencies", list, description="Dependency paths that were found for that source document."),
            Param("component_records", list, description="Per-component records to audit."),
            #: ★★★ 2026-10-03（接手轮）**补上 5 个必填形参** —— ★ 原先一个都没声明 ⇒
            #:   ★ 经工具层必 `TypeError`：真机实测
            #: `build_pack_and_go_audit_matrix() missing 2 required positional arguments
            #: :
            #:    'associated_drawings' and 'outputs'`
            #:   （★ 另外 3 个是 `KEYWORD_ONLY`，Python 会在补上位置参数之后**再报**）。
            #:   ★ 检测它的判据是 `tools/check_tool_param_binding.py` 的**判据 ⑤**
            #: （「目标函数的必填形参，spec 必须声明」）—— ★ ①②④ 问的都是"声明了的名字有
            #: 没有去处"，
            #:   ★ 只有 ⑤ 反过来问「**函数要的东西，spec 给没给**」。
            Param("associated_drawings", list, description="Associated drawing paths."),
            Param("outputs", list, description="Output artifact paths to audit."),
            Param(
                "include_drawings",
                bool,
                description="Whether drawings are covered by the matrix.",
            ),
            Param(
                "include_toolbox_components",
                bool,
                description="Whether Toolbox components are covered by the matrix.",
            ),
            Param(
                "include_suppressed", bool, description="Whether suppressed components are covered by the matrix."
            ),
        ],
        evidence=(
            "Build the audit matrix that a Pack-and-Go hand-off is reviewed against. ★ Pure data — no SolidWorks call."
        ),
        doc=(
            "Build the audit matrix that a Pack and Go hand-off is reviewed against. Read-only and pure data with no So"
            "lidWorks call; each include flag decides which dependency kind the matrix covers."
        ),
    ),
    ToolSpec(
        name="solidworks_delivery_export_bom_csv",
        title="Export an Assembly BOM to CSV (read-back verified)",
        module="sw_delivery",
        function="export_assembly_bom_csv",
        inject="model",
        params=[
            Param("output_path", str, description="Absolute path of the CSV file to write."),
            Param(
                "include_excluded",
                bool,
                default=False,
                description="Whether to include components excluded from the bill of materials. Defaults to false.",
            ),
            Param(
                "overwrite",
                bool,
                default=False,
                description="Whether to replace a file that already exists at that path. Defaults to false.",
            ),
        ],
        evidence=(
            "Export the assembly BOM to CSV. ★ The criterion is the FILE (exists and non-empty). ⚠ Does NOT save the do"
            "cument."
        ),
        doc=(
            "Export the assembly bill of materials to a UTF-8 CSV file. Writes the file and returns its size and SHA-25"
            "6, and does not save the document; the file is the criterion, so check that it exists and is non-empty."
        ),
    ),
    #: ── 仿真选项（★ 零参那个）──────────────────────────────────────────
    ToolSpec(
        name="solidworks_simulation_list_setter_summary",
        title="List Every Simulation Study-Option Setter",
        module="sw_simulation_study_options",
        function="list_setter_summary",
        inject=None,
        params=[],
        evidence=(
            "Return the catalogue of simulation study-option setters (family / name / type) as a dict. ★ Zero-argument,"
            " no SolidWorks call — use it to discover valid family/name pairs before calling set_option."
        ),
        doc=(
            "Return the catalogue of simulation study-option setters per family with their names and counts. Read-only "
            "and needs no SolidWorks call, and it takes no arguments; read it before setting a study option so that the"
            " family and name you pass are registered ones."
        ),
    ),
]
