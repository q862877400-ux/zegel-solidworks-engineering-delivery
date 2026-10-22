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
# ⚠ 生成器**只收 `exposable=True` 且门禁 0 问题的行**（★ 被门禁挡下的 47 行见 `output/`）
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH82"]

SPECS_BATCH82 = [
    ToolSpec(
        name="solidworks_assembly_add_mate_checked",
        title="Add a Mate (IAssemblyDoc::AddMate5) With Error-Code Check",
        module="sw_assembly", function="add_mate5_checked",
        inject="asm_model",
        #: ★★★ 2026-10-07（规格 212 · C-3）：★ **改掉两个"说假话"的后缀** ——
        #:   ★ 实录：`lock_rotation_deg` 实为 **bool**、`width_mate_option_mm` 实为 **int 枚举**
        #:   ⇒ ★★ **`_deg` / `_mm` 在说假话** ✗ —— ★ 而**读代码的人与 AI 都会信它** ✓
        #:   ★★ 这是**规则 2 的盲区**：★ 门禁只查「名字含长度词却无 `_mm`」（**单向** ✗）⇒
        #:     ★ 反过来那种（★ **不含长度词、却带了 `_mm`/`_deg`**）门禁抓不到 ✗
        #:   ★ 新判据补上了这个方向（★ `tools/check_unit_suffix_consistency.py` 的第 ③ 档）✓
        #:   ★ 改法：★ **改成能力层已有的正确名**（`sw_assembly.add_mate5_checked` 的形参就是
        #:     `lock_rotation` / `width_mate_option`）⇒ ★★ **于是别名条目成了自映射、一并删掉** ✓
        #:   ⚠★ **兼容性**：★ 这两个名字**原先就带错后缀** ⇒ ★ 改后**旧的传参名不再被接受** ✓
        #:     ★ 这是**有意为之** —— ★★ 留着假后缀比破坏一次兼容更糟（★ 它会持续骗人）✓
        param_alias={"distance_mm": "distance", "distance_upper_mm": "distance_upper", "distance_lower_mm": "distance_lower", "angle_deg": "angle", "angle_upper_deg": "angle_upper", "angle_lower_deg": "angle_lower"},
        params=[
            Param("mate_type", int, default=0, description="配合类型，官方 swMateType_e 枚举值（无量纲）。★ 调用前必须先按 mark 选好两个实体，否则官方写明返回 Nothing、ErrorStatus=swAddMateError_IncorrectSelections。"),
            Param("align", int, default=0, description="对齐方式，官方 swMateAlign_e 枚举值（无量纲）。源码默认 0。"),
            Param("flip", bool, default=False, description="是否翻转配合实体（无量纲布尔）。官方逐字：valid only if MateTypeFromEnum is swMateDISTANCE；距离/角度配合落在另一个可能位置时置 true。"),
            Param("distance_mm", str, default="0.0", description="距离配合的距离值（**毫米**；本仓一律收毫米，在工具层边界换算成官方 COM 吃的米）。官方逐字：valid only if MateTypeFromEnum is swMateDISTANCE。"),
            Param("distance_upper_mm", str, default="", description="距离绝对上限（**毫米**）。★ 源码把 None 回落到 distance（sw_assembly.py:410）—— 与官方逐字一致：『To specify a distance mate without limits, set the DistanceAbsUpperLimit and DistanceAbsLowerLimit parameters equal to the Distance parameter.』"),
            Param("distance_lower_mm", str, default="", description="距离绝对下限（**毫米**）。★ None 时回落到 distance_mm，同上一条官方口径。"),
            Param("gear_num", str, default="0.0", description="齿轮配合的齿轮比**分子**（无量纲比值，不加 _mm）。官方逐字：valid only if MateTypeFromEnum is swMateGEAR。"),
            Param("gear_den", str, default="0.0", description="齿轮配合的齿轮比**分母**（无量纲比值，不加 _mm）。官方逐字：valid only if MateTypeFromEnum is swMateGEAR。"),
            Param("angle_deg", str, default="0.0", description="角度配合的角度值（**度**；工具层收度、边界换算成弧度——★ 注意官方 AddMate5 的 Angle 形参类型是 System.double 且官方页未写单位，本仓按度收并在边界换算，与 D:\\AI\\SW\\scripts\\sw_assembly.py:383 docstring『15 参数 AddMate5』及本仓角度一律 `_deg` 的规则一致）。官方逐字：valid only if MateTypeFromEnum is swMateANGLE。"),
            Param("angle_upper_deg", str, default="", description="角度绝对上限（**度**）。★ 源码把 None 回落到 angle（sw_assembly.py:412）。"),
            Param("angle_lower_deg", str, default="", description="角度绝对下限（**度**）。★ 源码把 None 回落到 angle（sw_assembly.py:413）。"),
            Param("for_positioning_only", bool, default=False, description="True = 只按配合关系摆位、不返回 Mate（无量纲布尔）。"),
            #: ★★ 原为 `lock_rotation_deg` —— ★ **`_deg` 是假话**（它类型是 `bool`、描述自称"无量纲布尔"）✗
            #:   ⇒ ★ 2026-10-07（规格 212）改成能力层的真名 `lock_rotation` ✓
            Param("lock_rotation", bool, default=False, description="True = 锁定组件旋转（无量纲布尔）。★ 同心配合在运动模型里应保持 False。"),
            #: ★★ 原为 `width_mate_option_mm` —— ★ **`_mm` 是假话**（它是 `int`、官方 `swMateWidthOptions_e` **枚举值**）✗
            #:   ⇒ ★ 2026-10-07（规格 212）改成能力层的真名 `width_mate_option` ✓
            Param("width_mate_option", int, default=0, description="宽度配合选项，官方 swMateWidthOptions_e 枚举值（无量纲）。官方逐字：valid only if MateTypeFromEnum is swMateWIDTH。★ 这正是 AddMate4→AddMate5 的唯一差别。"),
            Param("name", str, default="", description="可选的 Mate 名称；给定时写入 mate.Name（源码对写入失败是吞掉的 best-effort，sw_assembly.py:440-444）。"),
            Param("clear_selection", bool, default=True, description="建完配合后是否调 ClearSelection2 清选区（无量纲布尔）。★ 官方调用序第 4 步。"),
        ],
        doc="★ 官方签名（逐字，来自 AddMate5.md）：`**Signature**: `Mate2 AddMate5( System.int MateTypeFromEnum, System.int AlignFromEnum, System.bool Flip, System.double Distance, System.double DistanceAbsUpperLimit, System.double DistanceAbsLowerLimi`。官方页第 12 行逐字：『Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]''⇒ ★ **已废弃但当前仍可调**（废弃 ≠ 不可达）。Remarks 逐字给了三条分流：『Standard, advanced, and mechanical mates, use [[IAssemblyDoc::CreateMate]]. / Misaligned concentric mates, use [[IAssemblyDoc::AddConcentricMateWithTolerance]]. / Cylindrical distance ma",
    ),
    ToolSpec(
        name="solidworks_assembly_suppress_component",
        title="压缩（隐藏）一个装配组件：先按名字选中该 COMPONENT，再调 IModelDoc2.EditSuppress2",
        module="sw_assembly", function="suppress_component",
        inject="asm_model",
        params=[
            Param("component_name", str, default="", description="要压缩的组件名，直接喂 `SelectByID2(component_name, 'COMPONENT', 0,0,0, append=False, mark=0)`（源码 scripts\\sw_assembly.py:754 经 _select_by_id，:64–80）。★ 无默认值 ⇒ 必填。字符串，无单位。★ 与规则 3 相容：这是**按名字选具名实体**，不是裸坐标；官方组件名带实例号（见 IComponent2.Name2 官方 Remarks 的 Part1-1 / subAssem1-2/Part1-1），调用方须填 SelectByID2 能认的那个名字，不是零件文件名。"),
        ],
        doc="★ 官方签名（逐字，来自 EditSuppress2.md）：``System.bool EditSuppress2()``。本函数的动作本体就是官方成员 IModelDoc2.EditSuppress2（零参、回 System.bool），源码 scripts\\sw_assembly.py:755 只有一句 `asm_model.EditSuppress2()`，前面那步选组件是本仓补的前置、不属于该成员。官方页 C:\\swapi\\types\\IModelDoc2\\EditSuppress2.md 首句逐字「Suppresses the selected feature, the selected component, or the owning feature of the selected face.」⇒ ★ ",
    ),
    ToolSpec(
        name="solidworks_assembly_unsuppress_component",
        title="Unsuppress an Assembly Component",
        module="sw_assembly", function="unsuppress_component",
        inject="asm_model",
        params=[
            Param("component_name", str, default="...", description="要解压缩的组件名（FeatureManager 树里的组件名，含 <1> 这类实例后缀）。★ 内部先 SelectByID2(component_name, 'COMPONENT', 0,0,0, …) 选中、再调零参成员（scripts/sw_assembly.py:767-768，辅助 _select_by_id 在 sw_assembly.py:64-80；坐标 0,0,0 是辅助函数内部固定的，不出现在工具签名里）。"),
        ],
        doc="★ 官方签名（逐字，来自 EditUnsuppress2.md）：`System.bool EditUnsuppress2()`。官方页 IModelDoc2/EditUnsuppress2.md 的 ## Remarks 逐字：「This routine is identical to the obsoleted IModelDoc2::EditUnsuppress. The version number was incremented to allow VB applications to take advantage of information not available in the obsoleted IPartDoc::EditUnsuppress.」⇒ 零参、作用在**当前选择**上、只是纯改名（调用序：",
    ),
    ToolSpec(
        name="solidworks_assembly_replace_component",
        title="Replace an Assembly Component",
        module="sw_assembly", function="replace_component",
        inject="asm_model",
        params=[
            Param("old_component_name", str, default="...", description="要被替换的旧组件名（FeatureManager 树里的组件名，含 <1> 这类实例后缀）。★ 内部先 SelectByID2(old_component_name, 'COMPONENT', 0,0,0, …) 选中（scripts/sw_assembly.py:779，辅助 _select_by_id 在 sw_assembly.py:64-80；坐标 0,0,0 是辅助函数内部固定的，不出现在工具签名里）。"),
            Param("new_part_path", str, default="...", description="替换件的新零件文件绝对路径（官方形参 FileName：Path and file name of the replacement component）。★ 不是坐标、无量纲，不带 _mm 后缀。"),
        ],
        doc="★ 官方签名（逐字，来自 ReplaceComponents2.md）：`System.bool ReplaceComponents2( System.string FileName, System.string ConfigName, System.bool ReplaceAllInstance, System.int UseConfigChoice, System.bool ReAttachMates )`。★ 成员归属：官方页在 **IAssemblyDoc**（不是 IModelDoc2）—— C:\\swapi\\types\\IAssemblyDoc\\ReplaceComponents2.md；旧一代 IAssemblyDoc::ReplaceComponents 官方页逐字标「Obsolete. Superseded by [[IAssemblyDoc::ReplaceComponents2]].」。## Returns：「True if the selected components are replaced, false if not」。## Remarks 逐字三条硬约束：(1)「You",
    ),
    ToolSpec(
        name="solidworks_assembly_dissolve",
        title="Dissolve Subassembly",
        module="sw_assembly_doc", function="dissolve_assembly",
        inject="doc",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 DissolveSubAssembly.md）：`**Signature**: `System.bool DissolveSubAssembly()``。官方 Remarks 逐字：「You must preselect the subassembly to dissolve when you run this method.」⇒ ★ 硬前置：调用前必须已选中要解散的子装配。同页另两句：解散会自动删除因此需要删除的特征、不向用户询问；在装配中调用会关闭组件文件，组件若已修改**不会自动保存**，须在关闭前自行保存。★ 本函数（scripts/sw_assembly_doc.py:370-375）不接收任何选择参数、不代做选择 ⇒ 暴露为工具时必须由调用方先用声明式选择器族选中（solidworks_select_by_selector / so",
    ),
    ToolSpec(
        name="solidworks_assembly_exit_edit_part_in_context",
        title="退出「在上下文编辑」态、回到装配文档编辑（IAssemblyDoc.EditAssembly）",
        module="sw_assembly_doc", function="exit_edit_part_in_context",
        inject="asm_model",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 EditAssembly.md）：``void EditAssembly()``。官方该页没有 Parameters / Returns 段（零参、回 void），## Remarks 逐字只有一句：「This method is used with [[IAssemblyDoc::EditPart2]], which allows you to edit a part within the context of an assembly.」——★ 即官方把它定位成 EditPart2 的**配对回退**（正是上一行那一对）。调用序：docs\\recon\\member-to-example-index.md 第 427 行把 EditAssembly 归到 Create_Pl",
    ),
    ToolSpec(
        name="solidworks_appearance_delete_render_material",
        title="按外观 ID 删除外观定义（IModelDocExtension.DeleteRenderMaterial —— 官方 2011 起标「不支持」，仓库刻意保留这个真机可调的入口）",
        module="sw_render_material", function="delete_render_material",
        inject="model",
        params=[
            Param("index", str, default="", description="对应官方 **PwMaterialId** —— ★ 它是**外观 ID（Appearance ID）**，不是列表下标（源码沿用 `index` 这个名字，但语义是 ID）；**无量纲**，故按规则 2 不加 `_mm` 后缀。源码 scripts\\sw_render_material.py:342-343 逐字 `get_com_member(extension, 'DeleteRenderMaterial', int(index), bool(cascade))`。★ 取 ID 的入口：官方 DeleteRenderMaterial.md ## Remarks 逐字点名 [[IMode"),
            Param("cascade", str, default="False", description="对应官方 **BReassignIdsAndInvalidate** —— True 则重排并作废外观 ID（**布尔量、无单位**）。源码签名 scripts\\sw_render_material.py:308 `cascade: bool = False`，:343 传 `bool(cascade)`。官方 ## Remarks 逐字给了语义：「By default, appearance IDs are persistent… However, if you set BReassignIdsAndInvalidate to true, then appearance ID 2 is i"),
        ],
        doc="★ 官方签名（逐字，来自 DeleteRenderMaterial.md）：``System.bool DeleteRenderMaterial( System.int PwMaterialId, System.bool BReassignIdsAndInvalidate )``。★ 首段（成员摘要，**不是** Remarks 段）逐字：「Not supported in SOLIDWORKS 2011 and later. Superseded by [[IModelDocExtension::DeleteDisplayStateSpecificRenderMaterial]] and [[IModelDocExtension::IDeleteDisplayStateSpecificRenderMaterial]]。」⇒ 官方自 **2011 起不支持**本成员（比 Obsolete 更强的一类措辞）。## Returns 逐字「True if the appear",
    ),
    ToolSpec(
        name="solidworks_simulation_ensure_addin",
        title="取 Simulation 加载项对象（ISldWorks.GetAddInObject；取不到先用 LoadAddIn 装 cosworks.dll 再取）",
        module="sw_simulation", function="ensure_simulation_addin",
        inject="sw_app",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 sw_simulation.py）：`查不到（repo_original —— ensure_simulation_addin 本身**不是** SolidWorks API 成员；它是编排两个官方成员的包装）。它逐字调用的两个官方成员签名如下）: `System.object GetAddInObject( System.string Clsid )` | `System.int LoadAddIn( System.string F`。★ 真源是本仓两段：① 源码 scripts\\sw_simulation.py:225-265（:248 `GetAddInObject(sw_app, SIMULATION_ADDIN_PROGID)` → 非 None 就直接返回；为 None 则 :253 先确认 SIMULATION_ADDIN_DLL 存在、:257 `LoadAddIn(str(dll))`、:259 再 `GetAddInObject`；第二次仍 None 就抛 RuntimeError 并把返回码按 swLoadAddinError_e 译成 0=成功·2=已加载·3=文件没找到·4=被禁用·7=许可错）；② ",
    ),
    ToolSpec(
        name="solidworks_simulation_get_study_manager",
        title="Get the Simulation CWStudyManager",
        module="sw_simulation", function="get_study_manager",
        inject="sw_app",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 sw_simulation.py）：`ICWModelDoc.get_StudyManager() → CWStudyManager（属性，非方法）`。★ source_kind=repo_original：本函数是本仓自研的**编排层**，不是 SolidWorks API 成员（成员真名是 ICWModelDoc.StudyManager）。真源 = D:\\AI\\SW\\scripts\\sw_simulation.py 第 297-305 行的来源块 + 函数体：先 get_cw_document(sw_app) 拿 ICWModelDoc，再 get_com_member(doc, 'StudyManager')。--- (1) 官方页：q1=false。C:\\swapi\\types 下**不存在** ICWModelDoc / ICWS",
    ),
    ToolSpec(
        name="solidworks_simulation_create_study_by_type",
        title="Create a Simulation Study by Type and Mesh Type",
        module="sw_simulation", function="create_static_study",
        inject="sw_app",
        params=[
            Param("name", str, default="", description="研究名称（对应官方 ICWStudyManager.CreateNewStudy3 的 String Name）。★ 源码里是**必填**位置参数，故 default 为空串；无单位。"),
            Param("study_type", int, default=0, description="swsAnalysisStudyType_e 枚举（**无量纲枚举值，不是长度也不是角度**，按规则 2 不加任何后缀）。0=Static 1=Frequency 2=Buckling 3=Thermal 4=Optimization 5=Nonlinear 6=DropTest 7=Fatigue 8=Dynamic 9=PressureVessel（源码 scripts/sw_simulation.py:191-200 的 SWS_ANALYSIS_STUDY_TYPES）。★ 源码默认 SWS_ANALYSIS_STUDY_TYPES['static'] 即 0；★ 除 0 之外**未真"),
            Param("mesh_type", int, default=0, description="swsMeshType_e 枚举（**无量纲枚举值**，按规则 2 不加后缀）。0=Solid 1=MidSurface 2=Surfaces 3=Mixed 4=Beam（源码 scripts/sw_simulation.py:183-189 的 SWS_MESH_TYPES）。★ 源码默认 SWS_MESH_TYPES['solid'] 即 0。"),
        ],
        doc="★ 官方签名（逐字，来自 sw_simulation.py）：`CWStudy CreateNewStudy3( String Name,`。★ source_kind=repo_original：本函数是本仓自研的**编排层**（CreateNewStudy3 → CreateNewStudy2 → CreateNewStudy 三级降级 + swsStudyError_e 报错 + 不拿 error_code 当成功判据），不是 SolidWorks API 成员。真源 = D:\\AI\\SW\\scripts\\sw_simulation.py 第 308-374 行的来源块 + 函数体（该来源块把官方 4 参签名整段抄进了文件，见下）。--- (1) 官方页：q1=false。C:\\swapi\\types 下**不存在 ICWSt",
    ),
    ToolSpec(
        name="solidworks_simulation_default_solve_memory_budget_gb",
        title="Read the Default Solve Memory Budget (GB)",
        module="sw_simulation", function="default_solve_memory_budget_gb",
        inject="",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 sw_simulation.py）：`查不到 —— 它不是 SolidWorks API 成员（源码 sw_simulation.py:1264，纯 Python/ctypes）`。★ 真源是**本仓** `scripts/sw_simulation.py` 的 `default_solve_memory_budget_gb`（★ 它不是 SolidWorks API 成员，故无官方页）—— source_kind=repo_original。真源有三处、都不是 SolidWorks API：① Windows kernel32 GlobalMemoryStatusEx（ctypes.Structure _MemStatus，读 ullTotalPhys，源码 1272-1287）；② 模块常量 DOF_PER_GB = 2_000_000（源码 1248），逐字来自本机",
    ),
    ToolSpec(
        name="solidworks_simulation_mesh_settings_report",
        title="Read the ICWMesh Settings That Decide Mesh Size",
        module="sw_simulation", function="mesh_settings_report",
        inject="study",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 sw_simulation.py）：`查不到 —— C:\\swapi\\types\\ 下**没有 ICWMesh\\ 目录**（Test-Path 返回 False）；对整个 C:\\swapi grep 'ICWMesh|MinElementSize|MesherType|AutomaticLooping' **0 命中**；types 下仅有 IMeshBody（另一个族）。CW 系接口属另一程序集 SolidWorks.Interop`。★ 真源是**本仓** `scripts/sw_simulation.py` 的 `mesh_settings_report`（★ 它不是 SolidWorks API 成员，故无官方页）—— source_kind=repo_original —— 本函数**不是单个 API 成员**，而是 scripts/sw_simulation.py:1292 的只读报告：① get_com_member(study, 'Mesh') 取 ICWMesh，取不到就回 {ok: False, reason: 'study 上取不到 Mesh 对象'}（1307-1309）；② 逐个读 Quality /",
    ),
    ToolSpec(
        name="solidworks_assembly_add_parallel_mate",
        title="Add a Parallel Mate Between Two Named Faces",
        module="sw_assembly", function="add_mate_parallel",
        inject="asm_model",
        params=[
            Param("face1_name", str, default="", description="第一个要配合的**面**名（字符串，**不是坐标**）。★ 源码 sw_assembly.py:691 把实体类型**写死**为 'FACE'（与 add_mate_distance 不同，后者把 type 提成参数）⇒ 本工具名里的 'face' 与实际行为一致，但**不能**拿它配平面/边。★ 已知事实 32：裸的 'Face1' 在真机上 SelectByID2 计数为 0；可靠的是组件上下文的特征名（'Boss-Extrude1@Part1-1' 之类）或按面上点的 SelectByID2('','FACE',x,y,z,...) —— 后者是裸坐标路径，规则 3 禁止作为工具参数。"),
            Param("face2_name", str, default="", description="第二个要配合的**面**名，append=True、mark=1 选中（源码 sw_assembly.py:692）。要求同 face1_name。"),
        ],
        doc="★ 官方签名（逐字，来自 sw_assembly.py）：`def add_mate_parallel(asm_model, face1_name, face2_name):`。查不到同名官方成员（source_kind=repo_original）—— 本函数不是 SolidWorks API 成员。★ 真源 = D:\\AI\\SW\\scripts\\sw_assembly.py:688-693（本仓自研编排函数；文件级来源块在同文件第 7 行写明『仓库: 本项目自身』，**本函数上方没有逐函数来源块** —— 该文件只有 3 处 `# ── 来源 ──`：行 7 / 842 / 872）。★ 它编排三个官方成员，逐字签名如下（三个官方页均已确认存在，各页第 14 行的 `**Signature**:` 行）：① `IModelDoc2.ClearSelection2`",
    ),
]
