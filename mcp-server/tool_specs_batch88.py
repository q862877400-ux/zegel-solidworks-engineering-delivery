"""★ 批次 88：由 Bunny 扇出产出、**经门禁**（`tools/check_bunny_toolspec_rows.py`）过滤后的 ToolSpec 声明。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   sw_assembly · sw_assembly_doc · sw_costing · sw_selection · sw_sketch
# 定位:   ★ 规格 `specs/204-tool-ramp/spec.md` 的批 88；
#         ★★ **本文件由 `tools/build_toolspec_batch_from_rows.py` 生成** ——
#         行来自 Bunny 子代理（**只读官方源与仓库**），而**判据、门禁、真机、提交归主线** ✓
# 官方依据: 逐行的 `official_file` / `official_signature` 见下表（★ 每条都是官方页的逐字
#           签名）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **17 个工具**
# ⚠ 生成器**只收 `exposable=True` 且门禁 0 问题的行**（★ 被门禁挡下的 0 行见 `output/`）
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH88"]

SPECS_BATCH88 = [
    ToolSpec(
        name="solidworks_selection_suspend_list",
        title="Selection: Suspend Selection List",
        module="sw_selection",
        function="suspend_selection_list",
        inject="selection",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 SuspendSelectionList.md）：`System.int SuspendSelectionList()`。官方摘要逐字『Suspe"
            "nds the current selection list.』。## Returns 逐字『0 if the suspended list is empty, 1 if not』⇒ ★ 返回值"
            "是**被挂起列表是否非空**（不是错误码、不是新列表的计数）。## Remarks 给了官方四步调用序：① SuspendSelectio"
            "nList（保留原列表内容并**另起**一个新列表）→ ② AddSelectionListObject / AddSelectionListObjects 填新列表（"
            "要加 selection set 里的对象则调 [[ISelectionSe"
        ),
        doc="★ 官方签名（逐字，来自 SuspendSelectionList.md）：`System.int SuspendSelectionList()`。"
             "官方摘要逐字『Suspends the current selection list.』。## Returns 逐字『0 if the suspended list is empty, "
             "1 if not』⇒ ★ 返回值是**被挂起列表是否非空**（不是错误码、不是新列表的计数）。## Remarks "
             "给了官方四步调用序：① SuspendSelectionList（保留原列表内容并**另起**一个新列表）→ ② "
             "AddSelectionListObject / AddSelectionListObjects 填新列表（要加 selection set 里的对象则调 [[ISelectionSe",
    ),
    ToolSpec(
        name="solidworks_selection_set_object_mark",
        title="Set Selection Object Mark (ISelectionMgr.SetSelectedObjectMark)",
        module="sw_selection",
        function="set_selected_object_mark",
        inject="selection",
        param_alias={"action": "value"},
        params=[
            Param("index", int, default=0, description=""),
            Param("mark", int, default=0, description=""),
            Param("action", int, default=0, description=""),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 SetSelectedObjectMark.md）：`System.bool SetSelectedObjectMark( System.int AtIndex,"
            " System.int Mark, System.int Action )`。★ **该官方页同样没有 `## Remarks` 段**（逐段核过：YAML 头 → 标题 →"
            " 一句描述「Sets the mark value for the specified selection.」→ `**Signature**:` → `## Parameters` → `## Re"
            "turns` → `## Examples` → `## See Also`）⇒ 铁律 5，不编 Remarks。能逐字引的官方正文：① Parameters 三条逐字"
            "「**AtIndex**: 1 <= Index position within the current list of selecte"
        ),
        doc="★ 官方签名（逐字，来自 SetSelectedObjectMark.md）：`System.bool SetSelectedObjectMark( System.int AtIndex,"
             " System.int Mark, System.int Action )`。★ **该官方页同样没有 `## Remarks` 段**（逐段核过：YAML 头 → 标题 "
             "→ 一句描述「Sets the mark value for the specified selection.」→ `**Signature**:` → `## Parameters` → `## "
             "Returns` → `## Examples` → `## See Also`）⇒ 铁律 5，不编 Remarks。能逐字引的官方正文：① Parameters "
             "三条逐字「**AtIndex**: 1 <= Index position within the current list of selecte",
    ),
    ToolSpec(
        name="solidworks_selection_enable",
        title="Enable/Disable Selection (ISelectionMgr.EnableSelection)",
        module="sw_selection",
        function="set_enable_selection",
        inject="selection",
        params=[
            Param(
                "enabled",
                bool,
                default=False,
                description="True = 允许选择（官方 Returns 逐字「True if selection is enabled」）；False = 禁用选择。★ "
                             "无量纲布尔开关（不是长度/角度，规则 2 不适用）★ ⚠ 这是**文档级会话开关**：置 False 之后，"
                             "本会话里所有依赖选择的工具（`solidworks_select_entity_by_index` / "
                             "`solidworks_select_by_selector` / 孔族 / 配合族…）都会失效 ⇒ 调用方须自行负责改回 True",
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 EnableSelection.md）：`System.bool EnableSelection {get; set;}`。官方页正文只有一句"
            "逐字「Enables or disables selection.」；`## Returns` 逐字「True if selection is enabled, false if disabled"
            "」；★ 该页**没有 `## Remarks` 段、也没有 `## Examples` 段**（只有 `## See Also` 三条：`[[ISelectionMgr Int"
            "erface]]` · `[[ISelectionMgr Members]]` · `[[ISelectionMgr::EnableContourSelection Property]]` ⇒ 官方自己"
            "把它与 "
        ),
        doc="★ 官方签名（逐字，来自 EnableSelection.md）：`System.bool EnableSelection {get; set;}`。"
             "官方页正文只有一句逐字「Enables or disables selection.」；`## Returns` 逐字「True if selection is enabled,"
             " false if disabled」；★ 该页**没有 `## Remarks` 段、也没有 `## Examples` 段**（只有 `## See Also` 三条："
             "`[[ISelectionMgr Interface]]` · `[[ISelectionMgr Members]]` · `[[ISelectionMgr::EnableContourSelection "
             "Property]]` ⇒ 官方自己把它与 ",
    ),
    ToolSpec(
        name="solidworks_selection_enable_contour",
        title="Enable/Disable Contour Selection (ISelectionMgr.EnableContourSelection)",
        module="sw_selection",
        function="set_enable_contour_selection",
        inject="selection",
        params=[
            Param(
                "enabled",
                bool,
                default=False,
                description="True = 允许按草图轮廓框选区域（官方 Returns 逐字「True to enable contour selection, false "
                             "to disable it」）；False = 禁用。★ 无量纲布尔开关（不是长度/角度，规则 2 不适用）★ "
                             "官方示例的用法是**成对开关**：用完立刻置 False，避免影响后续选择",
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 EnableContourSelection.md）：`System.bool EnableContourSelection {get; set;}`。官方"
            "页正文逐字「Enables and disables contour selection.」；`## Returns` 逐字「True to enable contour selection"
            ", false to disable it」；★★ `## Remarks` 逐字「This property enables you to select regions that are define"
            "d by single, multiple, open, or closed sketch boundaries. See the SOLIDWORKS Help for more information"
        ),
        doc="★ 官方签名（逐字，来自 EnableContourSelection.md）：`System.bool EnableContourSelection {get; set;}`。"
             "官方页正文逐字「Enables and disables contour selection.」；`## Returns` 逐字「True to enable contour "
             "selection, false to disable it」；★★ `## Remarks` 逐字「This property enables you to select regions that "
             "are defined by single, multiple, open, or closed sketch boundaries. See the SOLIDWORKS Help for more "
             "information",
    ),
    ToolSpec(
        name="solidworks_selection_is_coord_sys_element_selected",
        title="Is a Coordinate System Element Selected (ISelectionMgr)",
        module="sw_selection",
        function="is_coord_sys_element_selected",
        inject="selection",
        param_alias={"index": "kind", "mark": "index"},
        params=[
            Param(
                "index",
                int,
                default=0,
                description="★ RENAMED at the tool surface: the source spells this parameter `kind` (`def "
                             "is_coord_sys_element_selected(selection, kind: int, index: int)` , scripts/sw_selection."
                             "py:382), but the OFFICIAL first parameter is `Index` — see official_file signature "
                             "`IsCoordSysElementSelected(System.int Index, System.",
            ),
            Param(
                "mark",
                int,
                default=0,
                description="★ RENAMED at the tool surface: the source spells this parameter `index` "
                             "(scripts/sw_selection.py:382, passed second at :385), but the OFFICIAL second parameter "
                             "is `Mark`. Official semantics (verbatim values): -1 = all selections regardless of marks "
                             "· 0 = only the selections without marks · any other",
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 IsCoordSysElementSelected.md）：`System.bool IsCoordSysElementSelected( System.int "
            "Index, System.int Mark )`。Member summary (verbatim): 'Gets whether the selection is a coordinate system e"
            "lement.' Parameters (verbatim): 'Index: Index position within the current list of selected items, where In"
            "dex ranges from 1 to [[ISelectionMgr::GetSelectedObjectCount2]] (see Remarks)'; 'Mark: -1 = All selections"
            " regardle"
        ),
        doc="★ 官方签名（逐字，来自 IsCoordSysElementSelected.md）：`System.bool IsCoordSysElementSelected( System.int "
             "Index, System.int Mark )`。Member summary (verbatim): 'Gets whether the selection is a coordinate system "
             "element.' Parameters (verbatim): 'Index: Index position within the current list of selected items, where "
             "Index ranges from 1 to [[ISelectionMgr::GetSelectedObjectCount2]] (see Remarks)'; 'Mark: -1 = All "
             "selections regardle",
    ),
    ToolSpec(
        name="solidworks_selection_is_in_edit_target",
        title="Is a Selected Item In the Edit Target (ISelectionMgr)",
        module="sw_selection",
        function="is_in_edit_target",
        inject="selection",
        param_alias={"mark": "secondary"},
        params=[
            Param(
                "index",
                int,
                default=0,
                description="Source spelling is `index` and it is also the official first parameter name, so **no "
                             "rename**. Official semantics (verbatim): 'Index position with in the current list of "
                             "selected items, where AtIndex ranges from 1 to [[ISelectionMgr::GetSelectedObjectCount2]] "
                             "(see Remarks)' — note the official text ",
            ),
            Param(
                "mark",
                int,
                default=0,
                description="★ RENAMED: the source spells this parameter `secondary` (`def is_in_edit_target(selection,"
                             " index: int, secondary: int = 0)`, scripts/sw_selection.py:388, passed second at :390), "
                             "but the OFFICIAL second parameter is `Mark`. Official values (verbatim): -1 = all "
                             "selections regardless of marks · 0 = onl",
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 IsInEditTarget2.md）：`System.bool IsInEditTarget2( System.int Index, System.int Ma"
            "rk )`。Member summary (verbatim): 'Gets whether the selected object is in the edit target.' Returns (verba"
            "tim): 'True if the selected item specified by AtIndex belongs to a model that is the current edit target, "
            "false if not'. ★★ Remarks (verbatim, three sentences, all load-bearing): (1) 'Calling this meth"
        ),
        doc="★ 官方签名（逐字，来自 IsInEditTarget2.md）：`System.bool IsInEditTarget2( System.int Index, System.int "
             "Mark )`。Member summary (verbatim): 'Gets whether the selected object is in the edit target.' Returns "
             "(verbatim): 'True if the selected item specified by AtIndex belongs to a model that is the current edit "
             "target, false if not'. ★★ Remarks (verbatim, three sentences, all load-bearing): (1) 'Calling this meth",
    ),
    ToolSpec(
        name="solidworks_selection_collect_evidence",
        title="Selection: Collect Selection Evidence",
        module="sw_selection",
        function="collect_selection_evidence",
        inject="selection",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_selection.py）：`查不到（本函数不是 SolidWorks API 成员，无签名可抄）。★ 它编排"
            "的**四个**底层成员，官方 `**Signature**:` 逐字抄如下：① `System.int GetSelectedObjectCount2( System.int Ma"
            "rk )`（C:\\swapi\\types\\ISelectionMgr\\GetSelectedObjectCount2.md:14）② `Sy`。★ 真源是**本仓** `scripts/s"
            "w_selection.py` 的 `collect_selection_evidence`（★ 它不是 SolidWorks API 成员，故无官方页）—— ★ 本函数**自"
            "身**无官方页（不是 API 成员）。底层四个成员的官方原文要点： ① `GetSelectedObjectCount2` —— 摘要逐字『Gets "
            "the number of selected objects.』；Parameters 的 Mark 三档逐字『-1 = All selections regardless of marks / "
            "0 = only the sele"
        ),
        doc="★ 官方签名（逐字，来自 sw_selection.py）：`查不到（本函数不是 SolidWorks API 成员，无签名可抄）。★ "
             "它编排的**四个**底层成员，官方 `**Signature**:` 逐字抄如下：① `System.int GetSelectedObjectCount2( System."
             "int Mark )`（C:\\swapi\\types\\ISelectionMgr\\GetSelectedObjectCount2.md:14）② `Sy`。★ 真源是**本仓** "
             "`scripts/sw_selection.py` 的 `collect_selection_evidence`（★ 它不是 SolidWorks API 成员，故无官方页）—— ★ "
             "本函数**自身**无官方页（不是 API 成员）。底层四个成员的官方原文要点： ① `GetSelectedObjectCount2` —— "
             "摘要逐字『Gets the number of selected objects.』；Parameters 的 Mark 三档逐字『-1 = All selections "
             "regardless of marks / 0 = only the sele",
    ),
    ToolSpec(
        name="solidworks_assembly_apply_component_transform_x",
        title="按绕局部 X 轴旋转 + XYZ 平移修改选中组件的位姿并触发装配求解",
        module="sw_assembly",
        function="apply_component_transform_x",
        inject="component",
        param_alias={
            "tx_mm": "tx",
            "ty_mm": "ty",
            "tz_mm": "tz",
            "angle_deg": "angle_rad",
        },
        params=[
            Param(
                "tx_mm",
                str,
                default="",
                description="X 平移量，单位【毫米】（源码 `tx` 按【米】收，边界换算一次；官方逐字『The transform "
                             "specified must be in relation to the **root component**』）",
            ),
            Param(
                "ty_mm",
                str,
                default="",
                description="Y 平移量，单位【毫米】（源码 `ty`）",
            ),
            Param(
                "tz_mm",
                str,
                default="",
                description="Z 平移量，单位【毫米】（源码 `tz`）",
            ),
            Param(
                "angle_deg",
                str,
                default="0.0",
                description="绕**局部 X 轴**的旋转角，单位【度】（源码形参名是 `angle_rad`、按【弧度】收 ⇒ "
                             "边界换算一次；0 = 纯平移）",
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_assembly.py）：`查不到 —— 本函数**不是 SolidWorks API 成员**（它没有同名官方页，"
            "故无签名可抄）。它编排的官方成员逐字签名如下： ① C:\\swapi\\types\\IComponent2\\SetTransformAndSolve3.md:1"
            "4 —— `System.bool SetTransformAndSolve3( MathTransform XformIn, System.bool T`。★ 真源是**本仓** `scripts/"
            "sw_assembly.py` 的 `apply_component_transform_x`（★ 它不是 SolidWorks API 成员，故无官方页）—— ① SetTransf"
            "ormAndSolve3 官方 Returns 逐字『True if the transform was set and solved, false if not』+ Parameters 逐字"
            "『**ThisConfiguration**: True to transform **this configuration**, false to transform **all"
        ),
        doc="★ 官方签名（逐字，来自 sw_assembly.py）：`查不到 —— 本函数**不是 SolidWorks API 成员**（它没有同名官方页，"
             "故无签名可抄）。它编排的官方成员逐字签名如下： ① C:\\swapi\\types\\IComponent2\\SetTransformAndSolve3.md:"
             "14 —— `System.bool SetTransformAndSolve3( MathTransform XformIn, System.bool T`。★ 真源是**本仓** "
             "`scripts/sw_assembly.py` 的 `apply_component_transform_x`（★ 它不是 SolidWorks API 成员，故无官方页）—— ① "
             "SetTransformAndSolve3 官方 Returns 逐字『True if the transform was set and solved, false if not』+ "
             "Parameters 逐字『**ThisConfiguration**: True to transform **this configuration**, false to transform **all",
    ),
    ToolSpec(
        name="solidworks_assembly_external_reference_count",
        title="Count a Component's External File References (IComponent2.ListExternalFileReferencesCount)",
        module="sw_assembly_doc",
        function="list_external_file_references_count",
        inject="component",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 ListExternalFileReferencesCount.md）：``System.int ListExternalFileReferencesCount("
            ")``。官方页逐字：「Gets the number of external references on the component.」+ `## Returns` 逐字「Number o"
            "f external references」+ `## Remarks` 逐字「Call this method before calling [[IComponent2::IListExternalFi"
            "leReferences2]] to get the number of external references of the component.」★ 调用序摘一句（`docs/recon/me"
            "mber-to-ex"
        ),
        doc="★ 官方签名（逐字，来自 ListExternalFileReferencesCount.md）：``System.int "
             "ListExternalFileReferencesCount()``。官方页逐字：「Gets the number of external references on the "
             "component.」+ `## Returns` 逐字「Number of external references」+ `## Remarks` 逐字「Call this method "
             "before calling [[IComponent2::IListExternalFileReferences2]] to get the number of external references of "
             "the component.」★ 调用序摘一句（`docs/recon/member-to-ex",
    ),
    ToolSpec(
        name="solidworks_costing_set_default_lot_size",
        title="Set the Default Costing Lot Size (Single Body / Multibody)",
        module="sw_costing",
        function="set_default_lot_size",
        inject="defaults",
        params=[
            Param(
                "single_body",
                int,
                default=0,
                description="单实体算例的默认批量（Int32，**无量纲件数**，官方未给语义）",
            ),
            Param(
                "multibody",
                int,
                default=0,
                description="多实体算例的默认批量（Int32，**无量纲件数**，官方未给语义）",
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_costing.py）：`查不到（`C:\\swapi\\types\\` 下**没有** ICostingDefaults 目录 —— "
            "该树零个 Costing 接口目录；在 `C:\\swapi\\types\\*\\*.md` 全量检索 `LotSizeForSingleBody` = **0 命中** ⇒ "
            "无 `**Signature**:` 行可抄）。第三源（出厂程序集纯元数据反射）逐字：`D:\\AI\\SW\\_raw\\refl`。★ 查不到官方"
            " `## Remarks`（四册 CHM 无 costing 册 + `C:\\swapi` 无该接口页 —— 模块 docstring `sw_costing.py:30-31` 逐"
            "字记载这一点）⇒ 只有签名、没有参数语义。★ **真源是本仓** `scripts/sw_costing.py:386-393` 的 `set_default_l"
            "ot_size`（★ 它不是 SolidWorks API 成员，故无官方页），其 `# ── 来源 ──` 块在同文件 `:367-385`，逐字抄了上"
            "列签名并标「照官方签名新写、未在本机实测（AGENTS.md 铁律 2）」。⚠ 首参 `"
        ),
        doc="★ 官方签名（逐字，来自 sw_costing.py）：`查不到（`C:\\swapi\\types\\` 下**没有** ICostingDefaults 目录 —— "
             "该树零个 Costing 接口目录；在 `C:\\swapi\\types\\*\\*.md` 全量检索 `LotSizeForSingleBody` = **0 命中** ⇒ "
             "无 `**Signature**:` 行可抄）。第三源（出厂程序集纯元数据反射）逐字：`D:\\AI\\SW\\_raw\\refl`。★ "
             "查不到官方 `## Remarks`（四册 CHM 无 costing 册 + `C:\\swapi` 无该接口页 —— 模块 docstring `sw_costing.py:"
             "30-31` 逐字记载这一点）⇒ 只有签名、没有参数语义。★ **真源是本仓** `scripts/sw_costing.py:386-393` 的 "
             "`set_default_lot_size`（★ 它不是 SolidWorks API 成员，故无官方页），其 `# ── 来源 ──` 块在同文件 `:"
             "367-385`，逐字抄了上列签名并标「照官方签名新写、未在本机实测（AGENTS.md 铁律 2）」。⚠ 首参 `",
    ),
    ToolSpec(
        name="solidworks_costing_set_default_material",
        title="设某类别的默认材料（ICostingDefaults.SetMaterialName）",
        module="sw_costing",
        function="set_default_material",
        inject="defaults",
        params=[
            Param(
                "category",
                str,
                default="",
                description="类别整型枚举值。★ 官方未给语义（见 official_remarks_gist）⇒ 原样透传、不解释、不换算；"
                             "无量纲枚举，按规则 2 不加 _mm。",
            ),
            Param(
                "material_name",
                str,
                default="",
                description="材料库里的材料名字符串。字符串、无量纲；按规则 2 不加任何单位后缀。",
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_costing.py）：`查不到 —— C:\\swapi\\types\\ICostingDefaults\\ 目录不存在（该目录"
            "下按 'ost' 过滤零命中；C:\\swapi\\types 共 566 个接口目录里没有任何 costing 接口），且四册官方 CHM 里没有 "
            "costing 册（sw_costing.py 模块 docstring L30-31 逐字记载）⇒ 无官方 .md 页可抄 `**Signature**:`。★ 真源是**"
            "本仓** `scripts/sw_costing.py` 的 `set_default_material`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查"
            "不到官方 Remarks（C:\\swapi 无该页 + CHM 无 costing 册）⇒ 按铁律 5 不编参数语义。★ 已知的三条边界：① 首参 "
            "Int32 的语义（是「页签序号」还是「模板类别」？）官方未注明 —— sw_costing.py:380-381 逐字写「这些 `Set*` 首"
            "参的 Int32 语义……未注明」，模块 docstring 逐字写「整型取值的含义两套源都查不到 ⇒ 一律原样透出"
        ),
        doc="★ 官方签名（逐字，来自 sw_costing.py）：`查不到 —— C:\\swapi\\types\\ICostingDefaults\\ "
             "目录不存在（该目录下按 'ost' 过滤零命中；C:\\swapi\\types 共 566 个接口目录里没有任何 costing 接口），"
             "且四册官方 CHM 里没有 costing 册（sw_costing.py 模块 docstring L30-31 逐字记载）⇒ 无官方 .md 页可抄 "
             "`**Signature**:`。★ 真源是**本仓** `scripts/sw_costing.py` 的 `set_default_material`（★ 它不是 SolidWorks "
             "API 成员，故无官方页）—— 查不到官方 Remarks（C:\\swapi 无该页 + CHM 无 costing 册）⇒ 按铁律 5 "
             "不编参数语义。★ 已知的三条边界：① 首参 Int32 的语义（是「页签序号」还是「模板类别」？）官方未注明 —— "
             "sw_costing.py:380-381 逐字写「这些 `Set*` 首参的 Int32 语义……未注明」，模块 docstring "
             "逐字写「整型取值的含义两套源都查不到 ⇒ 一律原样透出",
    ),
    ToolSpec(
        name="solidworks_costing_set_default_manufacturing_method",
        title="设某类别的默认制造方法（ICostingDefaults.SetManufacturingMethod）",
        module="sw_costing",
        function="set_default_manufacturing_method",
        inject="defaults",
        params=[
            Param(
                "category",
                str,
                default="",
                description="类别整型枚举值。★ 官方未给语义（见 official_remarks_gist）⇒ 原样透传、不解释、不换算；"
                             "无量纲枚举，按规则 2 不加 _mm。",
            ),
            Param(
                "method",
                str,
                default="",
                description="制造方法整型枚举值。★ 取值表两套源都查不到（sw_costing.py 模块 docstring 逐字："
                             "「CostingType / MarkUpType / BodyStatus / LengthUnit 等整型取值的含义两套源都查不到 ⇒ "
                             "一律原样透出，不解释、不换算」）⇒ 原样透传；无量纲枚举，按规则 2 不加 _mm。",
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_costing.py）：`查不到 —— C:\\swapi\\types\\ICostingDefaults\\ 目录不存在（该目录"
            "下按 'ost' 过滤零命中），且四册官方 CHM 里没有 costing 册（sw_costing.py 模块 docstring L30-31 逐字记载）⇒"
            " 无官方 .md 页可抄 `**Signature**:`。★ 出厂程序集反射逐字（D:\\AI\\SW\\_raw\\reflect\\iface_s`。★ 真源是**"
            "本仓** `scripts/sw_costing.py` 的 `set_default_manufacturing_method`（★ 它不是 SolidWorks API 成员，故无官"
            "方页）—— 查不到官方 Remarks（C:\\swapi 无该页 + CHM 无 costing 册）⇒ 按铁律 5 不编参数语义。★ 已知的三条边"
            "界：① 两个 Int32 的语义（首参是「页签序号」还是「模板类别」？次参是哪套制造方法枚举？）官方未注明 —— sw_co"
            "sting.py:380 逐字写「这些 `Set*` 首参的 Int32 语义（是「页签序号」还是「模板类别」？）未注明」；② "
        ),
        doc="★ 官方签名（逐字，来自 sw_costing.py）：`查不到 —— C:\\swapi\\types\\ICostingDefaults\\ "
             "目录不存在（该目录下按 'ost' 过滤零命中），且四册官方 CHM 里没有 costing 册（sw_costing.py 模块 docstring "
             "L30-31 逐字记载）⇒ 无官方 .md 页可抄 `**Signature**:`。★ 出厂程序集反射逐字（D:"
             "\\AI\\SW\\_raw\\reflect\\iface_s`。★ 真源是**本仓** `scripts/sw_costing.py` 的 "
             "`set_default_manufacturing_method`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到官方 Remarks（C:"
             "\\swapi 无该页 + CHM 无 costing 册）⇒ 按铁律 5 不编参数语义。★ 已知的三条边界：① 两个 Int32 "
             "的语义（首参是「页签序号」还是「模板类别」？次参是哪套制造方法枚举？）官方未注明 —— sw_costing.py:380 "
             "逐字写「这些 `Set*` 首参的 Int32 语义（是「页签序号」还是「模板类别」？）未注明」；② ",
    ),
    ToolSpec(
        name="solidworks_selection_deselect",
        title="Deselect Item (mark-aware, official DeSelect2)",
        module="sw_selection",
        function="deselect",
        inject="selection",
        params=[
            Param("item", int, default=0, description=""),
            Param("mark", int, default=0, description=""),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 DeSelect2.md）：`System.int DeSelect2( System.object AtIndex, System.int Mark )`。D"
            "eselects the specified entity. Returns 逐字「1 if the specified entity is deselected, 0 if not」。Paramete"
            "rs 两条：AtIndex = 当前选中项列表里的位置，范围 **1 到 GetSelectedObjectCount2**；Mark = -1 全部 / 0 只有"
            "无标记 / 其它=当初打标记用的值。Remarks 逐字两条：① 「If running SOLIDWORKS x64, then you must declare AtI"
            "ndex as a **Long** in VBA」；② 「"
        ),
        doc="★ 官方签名（逐字，来自 DeSelect2.md）：`System.int DeSelect2( System.object AtIndex, System.int Mark )`。"
             "Deselects the specified entity. Returns 逐字「1 if the specified entity is deselected, 0 if not」。"
             "Parameters 两条：AtIndex = 当前选中项列表里的位置，范围 **1 到 GetSelectedObjectCount2**；Mark = -1 全部 "
             "/ 0 只有无标记 / 其它=当初打标记用的值。Remarks 逐字两条：① 「If running SOLIDWORKS x64, then you must "
             "declare AtIndex as a **Long** in VBA」；② 「",
    ),
]
