"""第三十五批 MCP 工具声明：**焊件读数与切割清单 6 个**（24h 段 4 续 / Spec Kit `152`）。

## ★★★ 让**规则**决定范围（★ 与段 4 第一批同一判据）
```
★ `sw_weldment` 未挂 **10** 个 ⇒ ★ 逐个看形参，★ **筛子有两条**：
   ① ★ **规则 3**（无裸坐标）—— ★★ 实测**10 个全过**（★ 初查报的"裸坐标嫌疑"是**假阳性**：
      ★ 我的粗查匹配到了 `Any` / `Path` / `properties` 里的字母 `y`）；
   ② ★★ **入参能不能表达**（★ 这才是真筛子）：
      · ✅ `create_cut_list(model, sort_options=None, *, collect_identical_bodies=False)`
      · ✅ `set_cut_list_properties(model, properties: dict)`
      · ✅ `export_cut_list_csv(evidence: dict, output_path)`
      · ✅ `read_property_manager(manager, *, core_only=True)`（★ 要 `manager` 注入）
      · ✅ `create_profile_center_mate(model, entities, *, mate_alignment=0, offset_distance=0.0, …)`
      · ✅ `create_weldment_profile(model, sketch_ref, output_path, *, properties=None)`
      · ⚠ `configure_member_profile(profile, …)` / `configure_split_member(split, …)`
        ⇒ ★ 要一个**宿主对象**（★ 需新的注入键）⇒ **本批不挂**（★ 不顺手加注入键）
      · ⚠ `create_structural_member(model, profile_path, segment_groups, …)`
        ⇒ ★ `segment_groups` 是**嵌套结构**（★ 表达复杂）⇒ **本批不挂**
      · ⚠ `iter_features_recursive(model)` ⇒ ★ **内部辅助**，不是工具候选（事实 191）
⇒ ★★ **本批挂 6 个** ⇒ `all_specs()` **122 → 128**。
```

## ★ 参数命名（规则 2 / 3）
```
★ 长度参数一律 `_mm`（`offset_distance_mm`）；★ 角度 `_deg`；★ **没有裸坐标** ✓
★ `sort_options` / `mate_alignment` 是**枚举值**（不是长度、不是角度）⇒ 不带后缀。
★ `sketch_ref` / `entities` 是**声明式选择**（`index:N` / `__current_selection__`）。
```

## 判据
```
★ 6 个里 `read_property_manager` 与 `create_cut_list` 是**读数**（★ 判"回 dict / 非空"）；
★ `set_cut_list_properties` 回**回读列表**（★ 它本来就读回来）；★ `export_cut_list_csv` 判**文件存在且非空**
  （★ 同段 4 第一批的导出族）；★ 两个 `create_*` 由 `pre_call` 把选择选好。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch35.py
# 定位:   24h 计划 段 4 续（Spec Kit `152`）—— 焊件读数与切割清单 6 个。
# 官方依据: `IStructureSystemFolder` / `ICutListSortOptions` / `IFeatureManager` 族
#          （★ 见 `scripts/sw_weldment.py` 的来源块）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批**不保存文档**（红线）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH35"]

_PICK = (
    'Declarative selection, e.g. "index:0" or "__current_selection__" — '
    "★ rule 3: no coordinates are passed."
)


SPECS_BATCH35 = [
    ToolSpec(
        name="solidworks_weldment_create_cut_list",
        title="Create the Cut List (and read it back)",
        module="sw_weldment",
        function="create_cut_list",
        inject="model",
        params=[
            Param(
                "sort_options",
                int,
                default=None,
                description=(
                    "swCutListSortOptions_e value; defaults to None, which leaves the document sort default in place."
                ),
            ),
            Param(
                "collect_identical_bodies",
                bool,
                default=False,
                description="Whether to collect identical bodies into one cut-list item. Defaults to false.",
            ),
        ],
        evidence=(
            "Create the weldment cut list and return the cut-list folders as evidence."
        ),
        doc=(
            "Skip this tool, NOT USABLE on this machine: the cut-list insert member resolves to None on this backend. U"
            "nder pywin32 late binding InsertWeldmentCutList2 resolves to None, so the call raises instead of creating "
            "a cut list, and the sort and identical-body options only shape a feature this backend cannot build."
        ),
    ),
    ToolSpec(
        name="solidworks_weldment_set_cut_list_properties",
        title="Set Cut-List Properties (and read them back)",
        module="sw_weldment",
        function="set_cut_list_properties",
        inject="model",
        params=[
            Param(
                "properties",
                dict,
                description="Mapping of property name to value; the names must be the localized ones the UI shows.",
            ),
        ],
        evidence=(
            "Set cut-list properties and return the read-back list. ⚠ Does NOT save the document. ★★ **属性名用中文（本"
            "地化）名**：`说明` / `材料`，★ **不是** `Description` / `Material`（真机：后者报「切割清单属性回读失败」，"
            "而前者写入并回读得到）。"
        ),
        doc=(
            "Set cut-list properties on every cut-list item and return the read-back list. Writes the values into each "
            "item, creates the cut list first when it is missing, and does not save the document; a value that does not"
            " read back raises. Pass the localized property names the UI shows, not the English Description or Material"
            " keys, which fail the read-back."
        ),
    ),
    ToolSpec(
        name="solidworks_weldment_export_cut_list_csv",
        title="Export a Cut List to CSV (read-back verified)",
        module="sw_weldment",
        function="export_cut_list_csv",
        inject=None,
        params=[
            Param(
                "evidence",
                dict,
                description=(
                    "The cut-list evidence dict, as returned by solidworks_weldment_evidence or solidworks_weldment_cre"
                    "ate_cut_list."
                ),
            ),
            Param("output_path", str, description="Absolute CSV output path."),
        ],
        evidence=(
            "Write a cut-list evidence dict to CSV and return the path. ★ The criterion is the FILE (exists and non-emp"
            "ty), not the return value."
        ),
        doc=(
            "Export a cut-list evidence dict to a UTF-8 CSV file and return the path. Writes the file and creates its p"
            "arent directory when missing; the criterion is the file existing and being non-empty, not the return value"
            ". Columns are index, name, body_count and every property name found in the rows."
        ),
    ),
    ToolSpec(
        name="solidworks_weldment_read_property_manager",
        title="Read a Property Manager as a Dict",
        module="sw_weldment",
        function="read_property_manager",
        inject="manager",
        params=[
            Param(
                "core_only",
                bool,
                default=True,
                description=(
                    "Whether to keep only the core cut-list property names and drop template title-block noise; false r"
                    "eads every name. Defaults to true."
                ),
            ),
        ],
        evidence=(
            "Read the active PropertyManager page's controls as a JSON-able dict. ★ Read-only."
        ),
        doc=(
            "Read the manufacturing properties of the active PropertyManager page as a dict. Read-only; by default it k"
            "eeps only the core cut-list property names and drops template title-block noise. Set core_only to false to"
            " read every property name the page exposes."
        ),
    ),
    ToolSpec(
        name="solidworks_weldment_create_profile_center_mate",
        title="Create a Profile-Center Mate (declarative selection)",
        module="sw_weldment",
        function="create_profile_center_mate",
        inject="model",
        params=[
            Param("entities", str, default="__current_selection__", description=(
                                                                        "Declarative selection of the entities to mate,"
                                                                        " for example 'index:0' or '__current_selection"
                                                                        "__'; no coordinates are passed. Defaults to '_"
                                                                        "_current_selection__'."
                                                                    )),
            Param(
                "mate_alignment",
                int,
                default=0,
                description="Mate alignment enum value. Defaults to 0.",
            ),
            Param(
                "offset_distance_mm",
                float,
                default=0.0,
                description="Offset distance in millimetres. Defaults to 0.0.",
            ),
            Param(
                "flip_dimension",
                bool,
                default=False,
                description="Whether to flip the mate dimensions. Defaults to false.",
            ),
        ],
        #: ★★ 能力层的形参是 `offset_distance`（**不带** `_mm`）⇒ 用 `param_alias` 把
        #:   工具层的 `offset_distance_mm` 映过去 —— ★ 那正是本项目的统一形态
        #:   （★ 工具层带 `_mm`、能力层不带；★ 由 `check_param_binding.py` 盯着）。
        param_alias={"offset_distance_mm": "offset_distance"},
        evidence=(
            "Create a profile-center mate between declaratively selected structural members. ★ Uses the official entry "
            "IAssemblyDoc::CreateMateData(swMatePROFILECENTER=24) + IAssemblyDoc::CreateMate (spec 240); the deprecated"
            " AddMate* family is NOT used."
        ),
        doc=(
            "Skip this tool, NOT USABLE on this machine: the mate data is created but the mate call returns None. It ta"
            "kes the entities, alignment, offset and flip settings below, yet CreateMate returns None on this build, so"
            " no mate appears in the assembly; use ordinary mates instead."
        ),
    ),
    ToolSpec(
        name="solidworks_weldment_create_weldment_profile",
        title="Create a Weldment Profile from a Sketch (declarative selection)",
        module="sw_weldment",
        function="create_weldment_profile",
        inject="model",
        params=[
            Param(
                "sketch_ref", str, default="__current_selection__", description=(
                                                                        "Declarative selection of the profile sketch, f"
                                                                        "or example 'index:0' or '__current_selection__"
                                                                        "'; no coordinates are passed. Defaults to '__c"
                                                                        "urrent_selection__'."
                                                                    )
            ),
            Param(
                "output_path",
                str,
                description="Absolute path for the saved .sldlfp profile; the suffix must be .sldlfp.",
            ),
            Param(
                "properties",
                dict,
                default=None,
                description=(
                    "Optional custom properties written before saving. Defaults to None, which writes no properties."
                ),
            ),
        ],
        evidence=(
            "Create a weldment profile from a declaratively selected sketch and write it to output_path. ★ The criterio"
            "n is the FILE."
        ),
        doc=(
            "Create a weldment profile file from a declaratively selected sketch and save it as .sldlfp. Writes the fil"
            "e plus any custom properties you pass, creates the parent directory, and raises when the save fails or the"
            " produced file is empty. The output path must end in .sldlfp."
        ),
    ),
]
