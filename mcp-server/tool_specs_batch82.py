"""★ 批次 82：由 Bunny 扇出产出、**经门禁**（`tools/check_bunny_toolspec_rows.py`）过滤后的 ToolSpec 声明。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   sw_assembly · sw_assembly_doc · sw_export · sw_render_material · sw_simulation
# 定位:   ★ 规格 `specs/204-tool-ramp/spec.md` 的批 82；
#         ★★ **本文件由 `tools/build_toolspec_batch_from_rows.py` 生成** ——
#         行来自 Bunny 子代理（**只读官方源与仓库**），而**判据、门禁、真机、提交归主线** ✓
# 官方依据: 逐行的 `official_file` / `official_signature` 见下表（★ 每条都是官方页的逐字
#           签名）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **19 个工具**
# ⚠ 生成器**只收 `exposable=True` 且门禁 0 问题的行**（★ 被门禁挡下的 47 行见 `output/`
# ）
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH82"]

SPECS_BATCH82 = [
    ToolSpec(
        name="solidworks_assembly_add_mate_checked",
        title="Add a Mate (IAssemblyDoc::AddMate5) With Error-Code Check",
        module="sw_assembly",
        function="add_mate5_checked",
        inject="asm_model",
        #: ★★★ 2026-10-07（规格 212 · C-3）：★ **改掉两个"说假话"的后缀** ——
        #: ★ 实录：`lock_rotation_deg` 实为 **bool**、`width_mate_option_mm` 实为 **int
        #: 枚举**
        #:   ⇒ ★★ **`_deg` / `_mm` 在说假话** ✗ —— ★ 而**读代码的人与 AI 都会信它** ✓
        #:   ★★ 这是**规则 2 的盲区**：★ 门禁只查「名字含长度词却无 `_mm`」（**单向** ✗）⇒
        #:     ★ 反过来那种（★ **不含长度词、却带了 `_mm`/`_deg`**）门禁抓不到 ✗
        #: ★ 新判据补上了这个方向（★ `tools/check_unit_suffix_consistency.py` 的第 ③ 档
        #: ）✓
        #: ★ 改法：★ **改成能力层已有的正确名**（`sw_assembly.add_mate5_checked` 的形参
        #: 就是
        #: `lock_rotation` / `width_mate_option`）⇒ ★★ **于是别名条目成了自映射、一并删
        #: 掉** ✓
        #: ⚠★ **兼容性**：★ 这两个名字**原先就带错后缀** ⇒ ★ 改后**旧的传参名不再被接受*
        #: * ✓
        #:     ★ 这是**有意为之** —— ★★ 留着假后缀比破坏一次兼容更糟（★ 它会持续骗人）✓
        #: ★★ 第 60 轮：实现层形参加了单位后缀（`distance` → `distance_m`，见事实 570），
        #:   所以别名目标名跟着改。★ 对外仍叫 `*_mm`（用户看毫米），
        #:   换算在工具层做**一次**（规则 2），到实现层就是米 ⇒ 后缀 `_m`。
        #: ⚠ `angle_deg` → `angle` **没动**：角度这一类本轮**没有**迁移，
        #:   它仍在棘轮基线里（234 处之一）。一次只迁一类，不混。
        param_alias={
            "distance_mm": "distance_m",
            "distance_upper_mm": "distance_upper_m",
            "distance_lower_mm": "distance_lower_m",
            "angle_deg": "angle",
            "angle_upper_deg": "angle_upper",
            "angle_lower_deg": "angle_lower",
        },
        params=[
            Param(
                "mate_type",
                int,
                default=0,
                description=(
                    "Mate type as an official swMateType_e enum value, for example the parallel or distance type. Defau"
                    "lts to 0."
                ),
            ),
            Param(
                "align",
                int,
                default=0,
                description="Alignment as an official swMateAlign_e enum value. Defaults to 0.",
            ),
            Param(
                "flip",
                bool,
                default=False,
                description=(
                    "Whether to flip the mated entities; the value only takes effect for a distance mate. Defaults to f"
                    "alse."
                ),
            ),
            Param(
                "distance_mm",
                str,
                default="0.0",
                description=(
                    "Distance of a distance mate in millimetres; converted to metres once at this boundary. Defaults to"
                    " 0.0."
                ),
            ),
            Param(
                "distance_upper_mm",
                str,
                default="",
                description=(
                    "Absolute upper distance limit in millimetres; empty falls back to distance_mm, which means no limi"
                    "t. Defaults to empty."
                ),
            ),
            Param(
                "distance_lower_mm",
                str,
                default="",
                description=(
                    "Absolute lower distance limit in millimetres; empty falls back to distance_mm, which means no limi"
                    "t. Defaults to empty."
                ),
            ),
            Param(
                "gear_num",
                str,
                default="0.0",
                description="Numerator of the gear ratio for a gear mate, a dimensionless ratio. Defaults to 0.0.",
            ),
            Param(
                "gear_den",
                str,
                default="0.0",
                description="Denominator of the gear ratio for a gear mate, a dimensionless ratio. Defaults to 0.0.",
            ),
            Param(
                "angle_deg",
                str,
                default="0.0",
                description=(
                    "Angle of an angle mate in degrees; converted to radians once at this boundary. Defaults to 0.0."
                ),
            ),
            Param(
                "angle_upper_deg",
                str,
                default="",
                description="Absolute upper angle limit in degrees; empty falls back to angle_deg. Defaults to empty.",
            ),
            Param(
                "angle_lower_deg",
                str,
                default="",
                description="Absolute lower angle limit in degrees; empty falls back to angle_deg. Defaults to empty.",
            ),
            Param(
                "for_positioning_only",
                bool,
                default=False,
                description=(
                    "Whether to place the entities by the mate relationship without returning a mate object. Defaults t"
                    "o false."
                ),
            ),
            #: ★★ 原为 `lock_rotation_deg` —— ★ **`_deg` 是假话**（它类型是 `bool`、描述
            #: 自称"无量纲布尔"）✗
            #:   ⇒ ★ 2026-10-07（规格 212）改成能力层的真名 `lock_rotation` ✓
            Param(
                "lock_rotation",
                bool,
                default=False,
                description=(
                    "Whether to lock the component rotation; keep it false for concentric mates that feed a motion stud"
                    "y. Defaults to false."
                ),
            ),
            #: ★★ 原为 `width_mate_option_mm` —— ★ **`_mm` 是假话**（它是 `int`、官方 `s
            #: wMateWidthOptions_e` **枚举值**）✗
            #:   ⇒ ★ 2026-10-07（规格 212）改成能力层的真名 `width_mate_option` ✓
            Param(
                "width_mate_option",
                int,
                default=0,
                description=(
                    "Width mate option as an official swMateWidthOptions_e enum value; this is the one argument AddMate"
                    "5 adds over AddMate4. Defaults to 0."
                ),
            ),
            Param(
                "name",
                str,
                default="",
                description=(
                    "Optional mate name written onto the created mate; the write is best effort. Defaults to empty."
                ),
            ),
            Param(
                "clear_selection",
                bool,
                default=True,
                description=(
                    "Whether to clear the selection with ClearSelection2 once the mate is created. Defaults to true."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 AddMate5.md）：`**Signature**: `Mate2 AddMate5( System.int MateTypeFromEnum, System"
            ".int AlignFromEnum, System.bool Flip, System.double Distance, System.double DistanceAbsUpperLimit, System."
            "double DistanceAbsLowerLimi`。官方页第 12 行逐字：『Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]'"
            "'⇒ ★ **已废弃但当前仍可调**（废弃 ≠ 不可达）。Remarks 逐字给了三条分流：『Standard, advanced, and mechanic"
            "al mates, use [[IAssemblyDoc::CreateMate]]. / Misaligned concentric mates, use [[IAssemblyDoc::AddConcentr"
            "icMateWithTolerance]]. / Cylindrical distance ma"
        ),
        doc=(
            "Add a mate between two preselected entities with the 15-parameter AddMate5 call. Obsolete in the official "
            "API, where standard, advanced and mechanical mates should use CreateMate instead; both entities must alrea"
            "dy be selected with their marks, otherwise the call returns Nothing with an IncorrectSelections error. Cre"
            "ates the mate in the active assembly and clears the selection afterwards by default."
        ),
    ),
    ToolSpec(
        name="solidworks_assembly_suppress_component",
        title="压缩（隐藏）一个装配组件：先按名字选中该 COMPONENT，再调 IModelDoc2.EditSuppress2",
        module="sw_assembly",
        function="suppress_component",
        inject="asm_model",
        params=[
            Param(
                "component_name",
                str,
                default="",
                description=(
                    "Component name as it appears in the feature tree, including the instance suffix, passed straight t"
                    "o the name-based selection. Defaults to empty, which selects nothing, so always pass a real name."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 EditSuppress2.md）：``System.bool EditSuppress2()``。本函数的动作本体就是官方成员 I"
            "ModelDoc2.EditSuppress2（零参、回 System.bool），源码 scripts\\sw_assembly.py:755 只有一句 `asm_model.Edit"
            "Suppress2()`，前面那步选组件是本仓补的前置、不属于该成员。官方页 C:\\swapi\\types\\IModelDoc2\\EditSuppres"
            "s2.md 首句逐字「Suppresses the selected feature, the selected component, or the owning feature of the sele"
            "cted face.」⇒ ★ "
        ),
        doc=(
            "Suppress one component of the active assembly by its feature-tree name. Modifies the component state of th"
            "at assembly; pass the instance name shown in the tree, for example Part1-1, and not the part file name."
        ),
    ),
    ToolSpec(
        name="solidworks_assembly_unsuppress_component",
        title="Unsuppress an Assembly Component",
        module="sw_assembly",
        function="unsuppress_component",
        inject="asm_model",
        params=[
            Param(
                "component_name",
                str,
                default="...",
                description=(
                    "Component name as it appears in the feature tree, including the instance suffix such as <1>, passe"
                    "d straight to the name-based selection. Defaults to a literal placeholder string, so always pass a"
                    " real name."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 EditUnsuppress2.md）：`System.bool EditUnsuppress2()`。官方页 IModelDoc2/EditUnsupp"
            "ress2.md 的 ## Remarks 逐字：「This routine is identical to the obsoleted IModelDoc2::EditUnsuppress. The "
            "version number was incremented to allow VB applications to take advantage of information not available in "
            "the obsoleted IPartDoc::EditUnsuppress.」⇒ 零参、作用在**当前选择**上、只是纯改名（调用序："
        ),
        doc=(
            "Unsuppress one component of the active assembly by its feature-tree name. Modifies the component state of "
            "that assembly; pass the instance name shown in the tree, for example Part1-1, and not the part file name."
        ),
    ),
    ToolSpec(
        name="solidworks_assembly_replace_component",
        title="Replace an Assembly Component",
        module="sw_assembly",
        function="replace_component",
        inject="asm_model",
        params=[
            Param(
                "old_component_name",
                str,
                default="...",
                description=(
                    "Component name of the instance to replace, including the instance suffix, selected by name before "
                    "the call. Defaults to a literal placeholder string, so always pass a real name."
                ),
            ),
            Param(
                "new_part_path",
                str,
                default="...",
                description=(
                    "Absolute path of the replacement part file passed as the official file-name argument. Defaults to "
                    "a literal placeholder string, so always pass a real path."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 ReplaceComponents2.md）：`System.bool ReplaceComponents2( System.string FileName, S"
            "ystem.string ConfigName, System.bool ReplaceAllInstance, System.int UseConfigChoice, System.bool ReAttachM"
            "ates )`。★ 成员归属：官方页在 **IAssemblyDoc**（不是 IModelDoc2）—— C:\\swapi\\types\\IAssemblyDoc\\Replac"
            "eComponents2.md；旧一代 IAssemblyDoc::ReplaceComponents 官方页逐字标「Obsolete. Superseded by [[IAssemblyD"
            "oc::ReplaceComponents2]].」。## Returns：「True if the selected components are replaced, false if not」。#"
            "# Remarks 逐字三条硬约束：(1)「You"
        ),
        doc=(
            "Replace one selected assembly component with another part file and reattach its mates. Modifies the compon"
            "ent list of the active assembly; only the selected instance is replaced, the default configuration choice "
            "is used, and mates are reattached."
        ),
    ),
    ToolSpec(
        name="solidworks_assembly_dissolve",
        title="Dissolve Subassembly",
        module="sw_assembly_doc",
        function="dissolve_assembly",
        inject="doc",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 DissolveSubAssembly.md）：`**Signature**: `System.bool DissolveSubAssembly()``。官"
            "方 Remarks 逐字：「You must preselect the subassembly to dissolve when you run this method.」⇒ ★ 硬前置："
            "调用前必须已选中要解散的子装配。同页另两句：解散会自动删除因此需要删除的特征、不向用户询问；在装配中调用会"
            "关闭组件文件，组件若已修改**不会自动保存**，须在关闭前自行保存。★ 本函数（scripts/sw_assembly_doc.py:370-3"
            "75）不接收任何选择参数、不代做选择 ⇒ 暴露为工具时必须由调用方先用声明式选择器族选中（solidworks_select_by_"
            "selector / so"
        ),
        doc=(
            "Delete the selected subassembly by dissolving it. You must preselect the subassembly before the call; diss"
            "olving deletes the features it needs without asking, and it closes the component files without saving them"
            ", so save any modified component first."
        ),
    ),
    ToolSpec(
        name="solidworks_assembly_exit_edit_part_in_context",
        title="退出「在上下文编辑」态、回到装配文档编辑（IAssemblyDoc.EditAssembly）",
        module="sw_assembly_doc",
        function="exit_edit_part_in_context",
        inject="asm_model",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 EditAssembly.md）：``void EditAssembly()``。官方该页没有 Parameters / Returns 段（"
            "零参、回 void），## Remarks 逐字只有一句：「This method is used with [[IAssemblyDoc::EditPart2]], which al"
            "lows you to edit a part within the context of an assembly.」——★ 即官方把它定位成 EditPart2 的**配对回退**"
            "（正是上一行那一对）。调用序：docs\\recon\\member-to-example-index.md 第 427 行把 EditAssembly 归到 Create"
            "_Pl"
        ),
        doc=(
            "Leave the in-context part editing state and return to the assembly. Modifies only the editing state of the"
            " active document; it is the counterpart of the call that starts editing a part inside an assembly."
        ),
    ),
    ToolSpec(
        name="solidworks_appearance_delete_render_material",
        title="按外观 ID 删除外观定义（IModelDocExtension.DeleteRenderMaterial —— 官方 2011 起标「不支持」，"
               "仓库刻意保留这个真机可调的入口）",
        module="sw_render_material",
        function="delete_render_material",
        inject="model",
        params=[
            Param(
                "index",
                str,
                default="",
                description=(
                    "Appearance ID of the definition to delete, an identifier rather than a list position. Defaults to "
                    "empty, so pass the ID read from the appearance listing."
                ),
            ),
            Param(
                "cascade",
                str,
                default="False",
                description=(
                    "Whether to reassign and invalidate the remaining appearance IDs after the delete. Defaults to Fals"
                    "e."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 DeleteRenderMaterial.md）：``System.bool DeleteRenderMaterial( System.int PwMateria"
            "lId, System.bool BReassignIdsAndInvalidate )``。★ 首段（成员摘要，**不是** Remarks 段）逐字：「Not support"
            "ed in SOLIDWORKS 2011 and later. Superseded by [[IModelDocExtension::DeleteDisplayStateSpecificRenderMater"
            "ial]] and [[IModelDocExtension::IDeleteDisplayStateSpecificRenderMaterial]]。」⇒ 官方自 **2011 起不支持**"
            "本成员（比 Obsolete 更强的一类措辞）。## Returns 逐字「True if the appear"
        ),
        doc=(
            "Delete one appearance definition from the active document by its appearance ID. The official member is doc"
            "umented as not supported since SolidWorks 2011 and its named successor cannot be called through this machi"
            "ne's binding, so this older entry point is kept; it modifies document appearances and returns the flag the"
            " call produced."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_ensure_addin",
        title="取 Simulation 加载项对象（ISldWorks.GetAddInObject；取不到先用 LoadAddIn 装 cosworks.dll 再取）",
        module="sw_simulation",
        function="ensure_simulation_addin",
        inject="sw_app",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_simulation.py）：`查不到（repo_original —— ensure_simulation_addin 本身**不是** "
            "SolidWorks API 成员；它是编排两个官方成员的包装）。它逐字调用的两个官方成员签名如下）: `System.object GetA"
            "ddInObject( System.string Clsid )` | `System.int LoadAddIn( System.string F`。★ 真源是本仓两段：① 源码 scr"
            "ipts\\sw_simulation.py:225-265（:248 `GetAddInObject(sw_app, SIMULATION_ADDIN_PROGID)` → 非 None 就直接返"
            "回；为 None 则 :253 先确认 SIMULATION_ADDIN_DLL 存在、:257 `LoadAddIn(str(dll))`、:259 再 `GetAddInObject`"
            "；第二次仍 None 就抛 RuntimeError 并把返回码按 swLoadAddinError_e 译成 0=成功·2=已加载·3=文件没找到·4=被禁"
            "用·7=许可错）；② "
        ),
        doc=(
            "Load the SolidWorks Simulation add-in and return its add-in object. Loading modifies the current session o"
            "nly and does not change the registry or the startup list, so a later session loads it again; it raises a R"
            "untimeError carrying the LoadAddIn return code when the add-in still cannot be obtained."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_get_study_manager",
        title="Get the Simulation CWStudyManager",
        module="sw_simulation",
        function="get_study_manager",
        inject="sw_app",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_simulation.py）：`ICWModelDoc.get_StudyManager() → CWStudyManager（属性，非方法"
            "）`。★ source_kind=repo_original：本函数是本仓自研的**编排层**，不是 SolidWorks API 成员（成员真名是 ICWMo"
            "delDoc.StudyManager）。真源 = D:\\AI\\SW\\scripts\\sw_simulation.py 第 297-305 行的来源块 + 函数体：先 get"
            "_cw_document(sw_app) 拿 ICWModelDoc，再 get_com_member(doc, 'StudyManager')。--- (1) 官方页：q1=false。C:"
            "\\swapi\\types 下**不存在** ICWModelDoc / ICWS"
        ),
        doc=(
            "Get the Simulation study manager of the active document as a COM object. Read-only: it only fetches the ma"
            "nager and changes nothing, and the result is a COM object rather than JSON, so use the study listing tools"
            " when you need names you can read."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_create_study_by_type",
        title="Create a Simulation Study by Type and Mesh Type",
        module="sw_simulation",
        function="create_static_study",
        inject="sw_app",
        params=[
            Param(
                "name",
                str,
                default="",
                description=(
                    "Study name handed to the official create call; the source treats it as required, so always pass a "
                    "real name. Defaults to empty."
                ),
            ),
            Param(
                "study_type",
                int,
                default=0,
                description=(
                    "Analysis study type: 0=static, 1=frequency, 2=buckling, 3=thermal, 4=optimization, 5=nonlinear, 6="
                    "drop test, 7=fatigue, 8=dynamic, 9=pressure vessel. Defaults to 0, the only type verified on this "
                    "machine."
                ),
            ),
            Param(
                "mesh_type",
                int,
                default=0,
                description="Mesh type: 0=solid, 1=midsurface, 2=surfaces, 3=mixed, 4=beam. Defaults to 0.",
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_simulation.py）：`CWStudy CreateNewStudy3( String Name,`。★ source_kind=repo_ori"
            "ginal：本函数是本仓自研的**编排层**（CreateNewStudy3 → CreateNewStudy2 → CreateNewStudy 三级降级 + swsStud"
            "yError_e 报错 + 不拿 error_code 当成功判据），不是 SolidWorks API 成员。真源 = D:\\AI\\SW\\scripts\\sw_sim"
            "ulation.py 第 308-374 行的来源块 + 函数体（该来源块把官方 4 参签名整段抄进了文件，见下）。--- (1) 官方页："
            "q1=false。C:\\swapi\\types 下**不存在 ICWSt"
        ),
        doc=(
            "Create a simulation study of the given analysis type and mesh type and report which entry point ran. Creat"
            "es the study in the active document and falls back from CreateNewStudy3 to the older entry points; an empt"
            "y entry_name means no study was created, and only the static type is verified on this machine."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_default_solve_memory_budget_gb",
        title="Read the Default Solve Memory Budget (GB)",
        module="sw_simulation",
        function="default_solve_memory_budget_gb",
        inject="",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_simulation.py）：`查不到 —— 它不是 SolidWorks API 成员（源码 sw_simulation.py:12"
            "64，纯 Python/ctypes）`。★ 真源是**本仓** `scripts/sw_simulation.py` 的 `default_solve_memory_budget_gb`（"
            "★ 它不是 SolidWorks API 成员，故无官方页）—— source_kind=repo_original。真源有三处、都不是 SolidWorks API"
            "：① Windows kernel32 GlobalMemoryStatusEx（ctypes.Structure _MemStatus，读 ullTotalPhys，源码 1272-1287）"
            "；② 模块常量 DOF_PER_GB = 2_000_000（源码 1248），逐字来自本机"
        ),
        doc=(
            "Get the default solve memory budget in gigabytes used by the pre-solve gate. Read-only and pure arithmetic"
            " with no SolidWorks call; the value is half the physical memory capped at 16 GB, and it falls back to a fi"
            "xed constant when the physical memory cannot be read."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_mesh_settings_report",
        title="Read the ICWMesh Settings That Decide Mesh Size",
        module="sw_simulation",
        function="mesh_settings_report",
        inject="study",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_simulation.py）：`查不到 —— C:\\swapi\\types\\ 下**没有 ICWMesh\\ 目录**（Test-P"
            "ath 返回 False）；对整个 C:\\swapi grep 'ICWMesh|MinElementSize|MesherType|AutomaticLooping' **0 命中**；t"
            "ypes 下仅有 IMeshBody（另一个族）。CW 系接口属另一程序集 SolidWorks.Interop`。★ 真源是**本仓** `scripts/sw"
            "_simulation.py` 的 `mesh_settings_report`（★ 它不是 SolidWorks API 成员，故无官方页）—— source_kind=repo_o"
            "riginal —— 本函数**不是单个 API 成员**，而是 scripts/sw_simulation.py:1292 的只读报告：① get_com_member(st"
            "udy, 'Mesh') 取 ICWMesh，取不到就回 {ok: False, reason: 'study 上取不到 Mesh 对象'}（1307-1309）；② 逐个读"
            " Quality /"
        ),
        doc=(
            "Read the mesh settings that decide the size of a study's mesh. Read-only; it reports quality, mesher type,"
            " element size limits, looping options and the current element and node counts, and returns ok false with a"
            " reason when the study has no mesh object to read."
        ),
    ),
    ToolSpec(
        name="solidworks_assembly_add_parallel_mate",
        title="Add a Parallel Mate Between Two Named Faces",
        module="sw_assembly",
        function="add_mate_parallel",
        inject="asm_model",
        params=[
            Param(
                "face1_name",
                str,
                default="",
                description=(
                    "Name of the first face to mate, selected by name before the second one. Defaults to empty, which s"
                    "elects nothing, so always pass a real face name."
                ),
            ),
            Param(
                "face2_name",
                str,
                default="",
                description=(
                    "Name of the second face, appended to the same selection with mark 1 after the first one. Defaults "
                    "to empty, so always pass a real face name."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_assembly.py）：`def add_mate_parallel(asm_model, face1_name, face2_name):`。查不"
            "到同名官方成员（source_kind=repo_original）—— 本函数不是 SolidWorks API 成员。★ 真源 = D:\\AI\\SW\\scripts"
            "\\sw_assembly.py:688-693（本仓自研编排函数；文件级来源块在同文件第 7 行写明『仓库: 本项目自身』，**本函数"
            "上方没有逐函数来源块** —— 该文件只有 3 处 `# ── 来源 ──`：行 7 / 842 / 872）。★ 它编排三个官方成员，逐字签"
            "名如下（三个官方页均已确认存在，各页第 14 行的 `**Signature**:` 行）：① `IModelDoc2.ClearSelection2`"
        ),
        doc=(
            "Add a parallel mate between two named faces of the active assembly. It clears the selection, selects both "
            "faces by name with mark 1 and then creates the mate, so each name must be one the name-based selection acc"
            "epts, for example Boss-Extrude1@Part1-1."
        ),
    ),
]
