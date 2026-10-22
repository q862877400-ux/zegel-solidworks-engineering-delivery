"""第三十三批 MCP 工具声明：**配置族 6 + 导出族 6** 共 12 个（24h 段 4 / Spec Kit `147`）。

## ★★★ 为什么选这两族（★ 让**规则**决定范围，不是我挑数量）
```
★ 段 4 的候选按"能不能挂"分三类（2026-10-01 轮 254 清点）：
    · `sw_hole_features` 未挂 **13** ⇒ ⚠ 建孔那几个吃 `center`（**裸坐标**）⇒ **规则 3 红线** ⇒ 要声明式包装
    · `sw_weldment` 未挂 **10**       ⇒ ⚠ 混了 `profile_path` / `segment_groups` 这类复杂入参
    · `sw_document_data` 未挂 **6**   ⇒ ★★ **全部无裸坐标** ✓
    · `sw_export` 未挂 **13**         ⇒ ★★ **全部无裸坐标** ✓
  ⇒ ★ **本批取后两族里最常用的 12 个** —— ★ **不为了凑数量挂违反规则 3 的工具**。
```

## ★★ §5.0：证据脚本**先找了**（★ 轮 252 学到的：判据 / 证据脚本 / 批量入口三样都要找）
```
· 配置族 ⇒ ★ **有现成的**：`tools/capture_custom_property_evidence.py` + `tools/probe_custom_property_reads.py`
· 导出族 ⇒ ★ **有现成的**：`tools/verify_bmp_smoke.py` + `tools/verify_png_smoke.py`
⇒ ★★ 本批**复用它们**（★ 而不再新写 —— ★ 那正是轮 252 的教训）。
```

## ★★ 两族的挂法不同（★ 由**返回形状**决定）
```
★ **配置族 6 个全部回 `dict`**（★ 可 JSON 化）⇒ ★ **直挂**（`inject="model"`，无需包装）。
★ **导出族回 bool / 路径** ⇒ ★★ 按本项目铁律「**COM 返回值凡不能自证，一律以回读为判据**」
  ⇒ ★★★ **判据 = 那个文件真的存在、且大小 > 0**（★ **不是**"函数说成功了"）。
    ★ 能力层已加 6 个 `export_*_report` 包装（`scripts/sw_export.py`）。
```

## ★ 参数命名（规则 2 / 规则 3）
```
★ `output_path` —— ★ 绝对路径（导出的落点）；★ **不写裸坐标**（本批没有坐标参数）✓
★ `quality` / `width` / `height` —— ★ `width`/`height` 是**像素**（不是长度）⇒ 不带 `_mm`（★ 与规则 2 一致：
  规则 2 管的是**长度**与**角度**）。
★ `value_mm` / `configuration_name` / `properties` —— ★ 长度参数带 `_mm`（规则 2）✓
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch33.py
# 定位:   24h 计划 段 4（Spec Kit `147`）—— 配置族 6 + 导出族 6。
# 官方依据: `IConfigurationManager` / `ICustomPropertyManager` / `IModelDoc2.SaveAs3` 等
#          （见 `scripts/sw_document_data.py` 与 `scripts/sw_export.py` 的来源块）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批**不保存文档**（只改配置/属性与导出文件）—— ★ 红线：不碰高风险写操作。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH33"]

_PATH = ("Absolute output path for the exported file (e.g. D:\\\\AI\\\\SW\\\\output\\\\part.step). "
         "★ The result is judged by READ-BACK: the file must exist and be non-empty.")
_CFG = ("Configuration name (e.g. \"默认\" / \"Default\"). ⚠ Leave empty for operations that "
        "default to the active configuration.")

SPECS_BATCH33 = [
    #: ── 配置族（★ 直挂：能力层回的就是 dict）──────────────────────────────
    ToolSpec(
        name="solidworks_config_inspect",
        title="Inspect the Document's Configurations",
        module="sw_document_data", function="inspect_configurations",
        inject="model",
        params=[],
        doc="List the document's configurations and the active one as a JSON-able dict. "
            "★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_config_create",
        title="Create (and optionally activate) a Configuration",
        module="sw_document_data", function="create_configuration",
        inject="model",
        params=[
            Param("configuration_name", str, description="Name of the configuration to create."),
            Param("comment", str, default="", description="Optional comment."),
            Param("alternate_name", str, default="", description="Optional alternate name."),
            Param("activate", bool, default=True, description="Activate it after creating."),
            Param("rebuild", bool, default=True, description="Rebuild after creating."),
        ],
        doc="Create a configuration, optionally activate and rebuild, then read the result "
            "back. ⚠ Does NOT save the document.",
    ),
    ToolSpec(
        name="solidworks_config_activate",
        title="Activate a Configuration (read-back verified)",
        module="sw_document_data", function="activate_configuration",
        inject="model",
        params=[
            Param("configuration_name", str, description="Configuration to activate."),
            Param("rebuild", bool, default=True, description="Rebuild after activating."),
        ],
        doc="Activate a configuration and verify it by read-back. ⚠ Does NOT save the document.",
    ),
    ToolSpec(
        name="solidworks_config_read_custom_property",
        title="Read a Custom Property (file-level or per-configuration)",
        module="sw_document_data", function="read_custom_property",
        inject="model",
        params=[
            Param("name", str, description="Custom property name."),
            Param("configuration_name", str, default="", description=_CFG),
        ],
        doc="Read one custom property as a JSON-able dict. ★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_config_set_custom_properties",
        title="Set Custom Properties (and read them back)",
        module="sw_document_data", function="set_custom_properties",
        inject="model",
        params=[
            Param("properties", dict,
                  description="Mapping of property name to value. ★ Values are strings."),
            Param("configuration_name", str, default="", description=_CFG),
        ],
        doc="Set several custom properties and return the read-back list. "
            "⚠ Does NOT save the document.",
    ),
    ToolSpec(
        name="solidworks_config_update_dimension",
        title="Update a Named Dimension in mm (read-back verified)",
        module="sw_document_data", function="update_dimension_mm",
        inject="model",
        params=[
            Param("dimension_name", str,
                  description="Exact dimension name, e.g. D1@草图1 or D1@凸台-拉伸1."),
            Param("value_mm", float, description="New value in MILLIMETRES."),
            #: ★ 能力层的形参是 **`configuration_mode`**（+ `configuration_names`），**
            #: 不是**
            #: `configuration_name` —— ★ 初版写错，被 `scripts/check_param_binding.py` 
            #: 当场抓到
            #:   （「既不在形参表里、也没在 param_alias 里 ⇒ 调用时会 TypeError」）。
            Param("configuration_mode", str, default="current",
                  description="'current' (active configuration only) / 'all' / 'specific'."),
            Param("configuration_names", list, default=None,
                  description="Only for configuration_mode='specific': the configuration names."),
            Param("rebuild", bool, default=True, description="Rebuild after the change."),
        ],
        doc="Update an exact named dimension and return a read-back report (before/after). "
            "⚠ Does NOT save the document.",
    ),
    #: ── 导出族（★ 能力层已包成"回读报告"：判据 = 文件存在且非空）────────
    ToolSpec(
        name="solidworks_export_step",
        title="Export the Active Part to STEP (read-back verified)",
        module="sw_export", function="export_step_report",
        inject="model",
        params=[Param("output_path", str, description=_PATH)],
        doc="Export the active document to STEP and return a READ-BACK report: the file must "
            "exist and be non-empty. ★ Rule: the criterion is the FILE, not the return value.",
    ),
    ToolSpec(
        name="solidworks_export_stl",
        title="Export the Active Part to STL (read-back verified)",
        module="sw_export", function="export_stl_report",
        inject="model",
        params=[
            Param("output_path", str, description=_PATH),
            Param("quality", str, default="fine",
                  description="STL quality: 'coarse' or 'fine'."),
        ],
        doc="Export to STL and return a READ-BACK report (file exists and is non-empty). "
            "★ The criterion is the FILE.",
    ),
    ToolSpec(
        name="solidworks_export_iges",
        title="Export the Active Part to IGES (read-back verified)",
        module="sw_export", function="export_iges_report",
        inject="model",
        params=[Param("output_path", str, description=_PATH)],
        doc="Export to IGES and return a READ-BACK report (file exists and is non-empty).",
    ),
    ToolSpec(
        name="solidworks_export_parasolid",
        title="Export the Active Part to Parasolid (read-back verified)",
        module="sw_export", function="export_parasolid_report",
        inject="model",
        params=[Param("output_path", str, description=_PATH)],
        doc="Export to Parasolid and return a READ-BACK report (file exists and is non-empty).",
    ),
    ToolSpec(
        name="solidworks_export_dxf",
        title="Export a SHEET-METAL Flat Pattern to DXF (read-back verified)",
        module="sw_export", function="export_dxf_report",
        inject="model",
        params=[Param("output_path", str, description=_PATH)],
        doc="Export to DXF and return a READ-BACK report (file exists and is non-empty). "
            "⚠⚠ THIS IS A SHEET-METAL FLAT-PATTERN EXPORT, not a general DXF export: on a "
            "non-sheet-metal part the capability layer refuses with "
            "「导出展开 DXF 前必须先保存钣金零件」. ★ That refusal is deliberate — it is a "
            "readable, actionable failure rather than a silent one.",
    ),
    ToolSpec(
        name="solidworks_export_bmp",
        title="Export a BMP Snapshot of the Active Part (read-back verified)",
        module="sw_export", function="export_bmp_report",
        inject="model",
        params=[
            Param("output_path", str, description=_PATH),
            Param("pixel_width", int, default=0,
                  description="Image width in PIXELS (★ PIXELS, not a length ⇒ named pixel_width (rule 2: no _mm for a non-length)). "
                              "⚠ 0 = use the document default."),
            Param("pixel_height", int, default=0,
                  description="Image height in PIXELS. ★ Named pixel_height because it is NOT a length (rule 2). ⚠ 0 = use the document default."),
        ],
        doc="Export a BMP image of the active document and return a READ-BACK report "
            "(file exists and is non-empty). ★ Covered by the existing smoke "
            "tools/verify_bmp_smoke.py.",
    ),
]
