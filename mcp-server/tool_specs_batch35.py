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

_PICK = ("Declarative selection, e.g. \"index:0\" or \"__current_selection__\" — "
         "★ rule 3: no coordinates are passed.")


SPECS_BATCH35 = [
    ToolSpec(
        name="solidworks_weldment_create_cut_list",
        title="Create the Cut List (and read it back)",
        module="sw_weldment", function="create_cut_list",
        inject="model",
        params=[
            Param("sort_options", int, default=None,
                  description="swCutListSortOptions_e value; omit for the document default."),
            Param("collect_identical_bodies", bool, default=False,
                  description="Collect identical bodies into one cut-list item."),
        ],
        doc="Create the weldment cut list and return the cut-list folders as evidence.",
    ),
    ToolSpec(
        name="solidworks_weldment_set_cut_list_properties",
        title="Set Cut-List Properties (and read them back)",
        module="sw_weldment", function="set_cut_list_properties",
        inject="model",
        params=[
            Param("properties", dict,
                  description="Mapping of property name to value (e.g. {\"Description\": \"tube\"})."),
        ],
        doc=("Set cut-list properties and return the read-back list. ⚠ Does NOT save the document. "
             "★★ **属性名用中文（本地化）名**：`说明` / `材料`，★ **不是** `Description` / `Material`"
             "（真机：后者报「切割清单属性回读失败」，而前者写入并回读得到）。"),
    ),
    ToolSpec(
        name="solidworks_weldment_export_cut_list_csv",
        title="Export a Cut List to CSV (read-back verified)",
        module="sw_weldment", function="export_cut_list_csv",
        inject=None,
        params=[
            Param("evidence", dict,
                  description="The cut-list evidence dict (★ as returned by "
                              "solidworks_weldment_evidence / create_cut_list)."),
            Param("output_path", str, description="Absolute CSV output path."),
        ],
        doc="Write a cut-list evidence dict to CSV and return the path. "
            "★ The criterion is the FILE (exists and non-empty), not the return value.",
    ),
    ToolSpec(
        name="solidworks_weldment_read_property_manager",
        title="Read a Property Manager as a Dict",
        module="sw_weldment", function="read_property_manager",
        inject="manager",
        params=[
            Param("core_only", bool, default=True,
                  description="Only the core properties (★ False reads everything)."),
        ],
        doc="Read the active PropertyManager page's controls as a JSON-able dict. ★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_weldment_create_profile_center_mate",
        title="Create a Profile-Center Mate (declarative selection)",
        module="sw_weldment", function="create_profile_center_mate",
        inject="model",
        params=[
            Param("entities", str, default="__current_selection__", description=_PICK),
            Param("mate_alignment", int, default=0, description="Mate alignment enum value."),
            Param("offset_distance_mm", float, default=0.0,
                  description="Offset distance in MILLIMETRES (★ rule 2)."),
            Param("flip_dimension", bool, default=False, description="Flip the mate dimensions."),
        ],
        #: ★★ 能力层的形参是 `offset_distance`（**不带** `_mm`）⇒ 用 `param_alias` 把
        #:   工具层的 `offset_distance_mm` 映过去 —— ★ 那正是本项目的统一形态
        #:   （★ 工具层带 `_mm`、能力层不带；★ 由 `check_param_binding.py` 盯着）。
        param_alias={"offset_distance_mm": "offset_distance"},
        doc="Create a profile-center mate between declaratively selected structural members. "
            "★ Uses the official entry IAssemblyDoc::CreateMateData(swMatePROFILECENTER=24) + "
            "IAssemblyDoc::CreateMate (spec 240); the deprecated AddMate* family is NOT used.",
    ),
    ToolSpec(
        name="solidworks_weldment_create_weldment_profile",
        title="Create a Weldment Profile from a Sketch (declarative selection)",
        module="sw_weldment", function="create_weldment_profile",
        inject="model",
        params=[
            Param("sketch_ref", str, default="__current_selection__", description=_PICK),
            Param("output_path", str, description="Absolute path for the saved .sldlfp profile."),
            Param("properties", dict, default=None,
                  description="Optional profile properties (★ omit for none)."),
        ],
        doc="Create a weldment profile from a declaratively selected sketch and write it to "
            "output_path. ★ The criterion is the FILE.",
    ),
]
