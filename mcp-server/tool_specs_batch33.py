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

_PATH = (
    "Absolute output path for the exported file (e.g. D:\\\\AI\\\\SW\\\\output\\\\part.step). "
    "★ The result is judged by READ-BACK: the file must exist and be non-empty."
)
_CFG = (
    'Configuration name (e.g. "默认" / "Default"). ⚠ Leave empty for operations that '
    "default to the active configuration."
)

SPECS_BATCH33 = [
    #: ── 配置族（★ 直挂：能力层回的就是 dict）──────────────────────────────
    ToolSpec(
        name="solidworks_config_inspect",
        title="Inspect the Document's Configurations",
        module="sw_document_data",
        function="inspect_configurations",
        inject="model",
        params=[],
        evidence=(
            "List the document's configurations and the active one as a JSON-able dict. ★ Read-only."
        ),
        doc=(
            "List the document's configurations and the active one as a JSON-able dict. Read-only: it reports what exis"
            "ts and changes nothing, so call it before creating, activating or updating a configuration."
        ),
    ),
    ToolSpec(
        name="solidworks_config_create",
        title="Create (and optionally activate) a Configuration",
        module="sw_document_data",
        function="create_configuration",
        inject="model",
        params=[
            Param(
                "configuration_name",
                str,
                description="Name of the configuration to create.",
            ),
            Param("comment", str, default="", description=(
                                                  "Optional comment stored with the configuration; defaults to an empty"
                                                  " string."
                                              )),
            Param(
                "alternate_name",
                str,
                default="",
                description="Optional alternate name for the configuration; defaults to an empty string.",
            ),
            Param(
                "activate",
                bool,
                default=True,
                description="Whether to activate the new configuration after creating it; defaults to true.",
            ),
            Param("rebuild", bool, default=True, description=(
                                                     "Whether to rebuild the model after creating it; defaults to true."
                                                 )),
        ],
        evidence=(
            "Create a configuration, optionally activate and rebuild, then read the result back. ⚠ Does NOT save the do"
            "cument."
        ),
        doc=(
            "Create a configuration and read the configuration list back. It writes the new configuration into the open"
            " document and does not save it, so the configuration exists only in that document until you save."
        ),
    ),
    ToolSpec(
        name="solidworks_config_activate",
        title="Activate a Configuration (read-back verified)",
        module="sw_document_data",
        function="activate_configuration",
        inject="model",
        params=[
            Param("configuration_name", str, description="Name of an existing configuration to activate."),
            Param(
                "rebuild", bool, default=True, description="Whether to rebuild after activating; defaults to true."
            ),
        ],
        evidence=(
            "Activate a configuration and verify it by read-back. ⚠ Does NOT save the document."
        ),
        doc=(
            "Activate an existing configuration and verify the switch by reading the active configuration back. It chan"
            "ges the active configuration and does not save the document, so the switch reaches disk only when you save"
            "."
        ),
    ),
    ToolSpec(
        name="solidworks_config_read_custom_property",
        title="Read a Custom Property (file-level or per-configuration)",
        module="sw_document_data",
        function="read_custom_property",
        inject="model",
        params=[
            Param("name", str, description=(
                                   "Exact custom property name as stored; property names follow the UI language and are"
                                   " case sensitive."
                               )),
            Param("configuration_name", str, default="", description=(
                                                             "Configuration to read from; empty reads the default confi"
                                                             "guration. Defaults to empty."
                                                         )),
        ],
        evidence=(
            "Read one custom property as a JSON-able dict. ★ Read-only."
        ),
        doc=(
            "Read one custom property value together with its type and whether it is editable. Read-only: writing is so"
            "lidworks_config_set_custom_properties, and an empty configuration name reads the default configuration."
        ),
    ),
    ToolSpec(
        name="solidworks_config_set_custom_properties",
        title="Set Custom Properties (and read them back)",
        module="sw_document_data",
        function="set_custom_properties",
        inject="model",
        params=[
            Param(
                "properties",
                dict,
                description="Mapping of property name to value; every value must be a string.",
            ),
            Param("configuration_name", str, default="", description=(
                                                             "Configuration to write to; empty writes the default confi"
                                                             "guration. Defaults to empty."
                                                         )),
        ],
        evidence=(
            "Set several custom properties and return the read-back list. ⚠ Does NOT save the document."
        ),
        doc=(
            "Set several custom properties and return the read-back list. It writes the values into the open document a"
            "nd does not save it, so call the save tool afterwards when the values must persist."
        ),
    ),
    ToolSpec(
        name="solidworks_config_update_dimension",
        title="Update a Named Dimension in mm (read-back verified)",
        module="sw_document_data",
        function="update_dimension_mm",
        inject="model",
        params=[
            Param(
                "dimension_name",
                str,
                description="Exact dimension name as it appears in the tree, for example D1@Sketch1.",
            ),
            Param("value_mm", float, description="New dimension value in millimetres."),
            #: ★ 能力层的形参是 **`configuration_mode`**（+ `configuration_names`），**
            #: 不是**
            #: `configuration_name` —— ★ 初版写错，被 `scripts/check_param_binding.py`
            #: 当场抓到
            #:   （「既不在形参表里、也没在 param_alias 里 ⇒ 调用时会 TypeError」）。
            Param(
                "configuration_mode",
                str,
                default="current",
                description=(
                    "Which configurations to change: 'current' for the active configuration, 'all' for every configurat"
                    "ion, or 'specific' for the names in configuration_names. Defaults to 'current'."
                ),
            ),
            Param(
                "configuration_names",
                list,
                default=None,
                description=(
                    "Configuration names to change when configuration_mode is 'specific'; defaults to null, which names"
                    " no configuration."
                ),
            ),
            Param(
                "rebuild", bool, default=True, description="Whether to rebuild after the change; defaults to true."
            ),
        ],
        evidence=(
            "Update an exact named dimension and return a read-back report (before/after). ⚠ Does NOT save the document"
            "."
        ),
        doc=(
            "Update one exact named dimension to a new millimetre value and report before and after. It writes the valu"
            "e and rebuilds by default while leaving the document unsaved, so an unwanted change can still be dropped b"
            "y not saving."
        ),
    ),
    #: ── 导出族（★ 能力层已包成"回读报告"：判据 = 文件存在且非空）────────
    ToolSpec(
        name="solidworks_export_step",
        title="Export the Active Part to STEP (read-back verified)",
        module="sw_export",
        function="export_step_report",
        inject="model",
        params=[Param("output_path", str, description=(
                                              "Absolute path of the STEP file to write, for example D:/work/part.step."
                                          ))],
        evidence=(
            "Export the active document to STEP and return a READ-BACK report: the file must exist and be non-empty. ★ "
            "Rule: the criterion is the FILE, not the return value."
        ),
        doc=(
            "Export the active document to a STEP file at output_path and confirm the file exists and is not empty. It "
            "writes the file, and the file itself is the criterion of success rather than the return value."
        ),
    ),
    ToolSpec(
        name="solidworks_export_stl",
        title="Export the Active Part to STL (read-back verified)",
        module="sw_export",
        function="export_stl_report",
        inject="model",
        params=[
            Param("output_path", str, description=(
                                          "Absolute path of the STL file to write, for example D:/work/part.stl."
                                      )),
            Param(
                "quality",
                str,
                default="fine",
                description="Mesh quality: 'coarse' or 'fine'. Defaults to 'fine'.",
            ),
        ],
        evidence=(
            "Export to STL and return a READ-BACK report (file exists and is non-empty). ★ The criterion is the FILE."
        ),
        doc=(
            "Export the active document to an STL mesh at output_path and confirm the file exists and is not empty. It "
            "writes the file; quality chooses the tessellation, and the file itself is the criterion of success."
        ),
    ),
    ToolSpec(
        name="solidworks_export_iges",
        title="Export the Active Part to IGES (read-back verified)",
        module="sw_export",
        function="export_iges_report",
        inject="model",
        params=[Param("output_path", str, description=(
                                              "Absolute path of the IGES file to write, for example D:/work/part.igs."
                                          ))],
        evidence=(
            "Export to IGES and return a READ-BACK report (file exists and is non-empty)."
        ),
        doc=(
            "Export the active document to an IGES file at output_path and confirm the file exists and is not empty. It"
            " writes the file, and the file itself is the criterion of success rather than the return value."
        ),
    ),
    ToolSpec(
        name="solidworks_export_parasolid",
        title="Export the Active Part to Parasolid (read-back verified)",
        module="sw_export",
        function="export_parasolid_report",
        inject="model",
        params=[Param("output_path", str, description=(
                                              "Absolute path of the Parasolid file to write, for example D:/work/part.x"
                                              "_t."
                                          ))],
        evidence=(
            "Export to Parasolid and return a READ-BACK report (file exists and is non-empty)."
        ),
        doc=(
            "Export the active document to a Parasolid file at output_path and confirm the file exists and is not empty"
            ". It writes the file, and the file itself is the criterion of success rather than the return value."
        ),
    ),
    ToolSpec(
        name="solidworks_export_dxf",
        title="Export a SHEET-METAL Flat Pattern to DXF (read-back verified)",
        module="sw_export",
        function="export_dxf_report",
        inject="model",
        params=[Param("output_path", str, description=(
                                              "Absolute path of the DXF file to write, for example D:/work/flat.dxf."
                                          ))],
        evidence=(
            "Export to DXF and return a READ-BACK report (file exists and is non-empty). ⚠⚠ THIS IS A SHEET-METAL FLAT-"
            "PATTERN EXPORT, not a general DXF export: on a non-sheet-metal part the capability layer refuses with 「导"
            "出展开 DXF 前必须先保存钣金零件」. ★ That refusal is deliberate — it is a readable, actionable failure rat"
            "her than a silent one."
        ),
        doc=(
            "Export the active document to a DXF file at output_path and confirm the file exists and is not empty. It w"
            "rites the file; a drawing goes out as a drawing DXF, while a part takes the sheet-metal flat-pattern path "
            "and is refused unless it is a saved sheet-metal part."
        ),
    ),
    ToolSpec(
        name="solidworks_export_bmp",
        title="Export a BMP Snapshot of the Active Part (read-back verified)",
        module="sw_export",
        function="export_bmp_report",
        inject="model",
        params=[
            Param("output_path", str, description=(
                                          "Absolute path of the BMP file to write, for example D:/work/view.bmp."
                                      )),
            Param(
                "pixel_width",
                int,
                default=0,
                description="Image width in pixels; 0 uses the document default. Defaults to 0.",
            ),
            Param(
                "pixel_height",
                int,
                default=0,
                description="Image height in pixels; 0 uses the document default. Defaults to 0.",
            ),
        ],
        evidence=(
            "Export a BMP image of the active document and return a READ-BACK report (file exists and is non-empty). ★ "
            "Covered by the existing smoke tools/verify_bmp_smoke.py."
        ),
        doc=(
            "Export a BMP image of the active document to output_path and confirm the file exists and is not empty. It "
            "writes the image from the current view; the pixel sizes are counts rather than lengths, and zero means the"
            " document default."
        ),
    ),
]
