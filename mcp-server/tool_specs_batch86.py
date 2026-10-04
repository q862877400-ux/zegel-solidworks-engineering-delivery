"""★ 批次 86：由 Bunny 扇出产出、**经门禁**（`tools/check_bunny_toolspec_rows.py`）过滤后的 ToolSpec 声明。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   sw_simulation_results · sw_simulation_study_options · sw_view
# 定位:   ★ 规格 `specs/204-tool-ramp/spec.md` 的批 86；
#         ★★ **本文件由 `tools/build_toolspec_batch_from_rows.py` 生成** ——
#         行来自 Bunny 子代理（**只读官方源与仓库**），而**判据、门禁、真机、提交归主线** ✓
# 官方依据: 逐行的 `official_file` / `official_signature` 见下表（★ 每条都是官方页的逐字签名）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **30 个工具**
# ⚠ 生成器**只收 `exposable=True` 且门禁 0 问题的行**（★ 被门禁挡下的 0 行见 `output/`）
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH86"]

SPECS_BATCH86 = [
    ToolSpec(
        name="solidworks_simulation_collect_mesh_evidence",
        title="Collect the Mesh Quality Evidence Of The Injected Mesh",
        module="sw_simulation_results", function="collect_mesh_evidence",
        inject="mesh",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 sw_simulation_results.py）：`查不到 —— 本函数不是 SolidWorks API 成员（官方 API 参考里没有 collect_mesh_evidence 这个成员），且 `C:\\swapi\\types\\ICWMesh\\` 目录本身就不存在（Test-Path=False），故连可逐字抄的 `**Signature**:` 行都没有。`。★★ source_kind=repo_original：**真源是本仓** `scripts/sw_simulation_results.py` —— 函数体 :268-291，加它上方 :259-267 的来源块（逐字「仓库: 本项目自身既有模式（scripts/sw_simulation_study.py::collect_study_evidence）」，定位逐字「网格状态证据回读，沿用『只取已核实成员』的写法」）。★ 为什么官方 API 页查不到（本机三处都查过）：① `C:\\swapi\\types\\` 下 **566 个目录里 0 个 `ICW*`**（`Get-ChildItem",
    ),
    ToolSpec(
        name="solidworks_simulation_set_registered_study_option",
        title="Set One Registered Study Option On The Injected Options Object",
        module="sw_simulation_study_options", function="set_option",
        inject="options",
        params=[
            Param("family", str, default="", description="研究设置族名，取自 STUDY_OPTION_FAMILIES / STUDY_OPTION_SETTERS 的九个族之一（如 'ICWStaticStudyOptions' / 'ICWFrequencyStudyOptions' / 'ICWBucklingStudyOptions'）。★ **字符串名、不是坐标**（规则 3 不适用）。★ 无默认：不在登记表里时 `set_option` 抛 `KeyError` 并逐字报「未知的研究设置族: …」（scripts/sw_simulation_study_options.py:611-612），**不静默忽略**。⚠ 该参数**被用两次*"),
            Param("name", str, default="", description="该族登记表中确实存在的 setter 名（如 'ComputeFreeBodyForce2' / 'ContactPenaltyStiffnessScaleFactor' / 'DefinedReferencePressure'）。★ 拼错时抛 `KeyError` 并逐字列出「该族登记的 N 项」与布尔型推荐清单（scripts/sw_simulation_study_options.py:613-619）⇒ 错误信息自带合法值。★ 建议先调 solidworks_simulation_list_setter_summary 列全量再设。"),
            Param("value", str, default="", description="取值，**按 TEXT 传** —— 与既有 solidworks_simulation_set_study_option 同口径：模块内 `_coerce`（scripts/sw_simulation_study_options.py:588-599）按登记表登记的反射类型把文本转成 int / bool / float / str 再下发（`_TYPE_ALIASES` 逐条对应 'Int32'/'System.Int32'→int、'Boolean'/'System.Boolean'→bool、'Double'/'System.Double'→float、'String'/'System"),
        ],
        doc="★ 官方签名（逐字，来自 sw_simulation_study_options.py）：`查不到 —— 本函数不是 SolidWorks API 成员（官方 API 里没有 set_option 这个成员）。★ 且它的成员名是**变量** `name`，签名按项才定：值域由本仓登记表 `STUDY_OPTION_SETTERS`（:99-360）给出，每个项都是反射里的 `set_XXX(...)` **属性**（不是方法），而 `C:\\swapi\\types\\` 下**没有 ICWS`。★★ source_kind=repo_original：**真源是本仓** `scripts/sw_simulation_study_options.py` —— 函数体 :602-654，加它上方 :578-586 的来源块（逐字「仓库: 本项目自身（本任务新增的能力层）… 定位: 通用 setter 的取值校验与调用」）。★ 官方 API 页查不到（本机三处都查过）：① `C:\\swapi\\types\\` 下 566 个目录里 0 个 `ICW*`；② 对整个 `C:\\swapi` grep `ICWStaticStudyOptions|ICWFrequencyStudyOptions|",
    ),
    ToolSpec(
        name="solidworks_view_activate",
        title="Activate Model View",
        module="sw_view", function="activate_view",
        inject="view",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 Activate.md）：`void Activate()`。查不到 —— 该官方页**没有 `## Remarks` 段**（全文只有正文一句 'Activates the model view.' + `**Signature**: void Activate()` + `## See Also` 的两个链接 `IModelView Interface` / `IModelView Members`）⇒ 官方**未给任何前置条件或语义细节**。",
    ),
    ToolSpec(
        name="solidworks_view_redraw",
        title="Redraw Graphics Window",
        module="sw_view", function="redraw_view",
        inject="view",
        params=[
            Param("scope_or_none", str, default="", description=""),
        ],
        doc="★ 官方签名（逐字，来自 GraphicsRedraw.md）：`void GraphicsRedraw( System.object Rect )`。`## Parameters` 逐字：「**Rect**: Array of four integers or longs indicating the boundary of the region in the SOLIDWORKS graphics window to redraw; **if the array is empty, then the entire graphics window is redrawn**」。`## Remarks` 逐字：「This method forces the specified region or the entire SOLIDWORKS gr",
    ),
    ToolSpec(
        name="solidworks_view_initialize_shading",
        title="初始化三维视图的 OpenGL 着色",
        module="sw_view", function="initialize_shading",
        inject="view",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 InitializeShading.md）：`void InitializeShading()`。官方页存在且有完整 `## Remarks`（C:\\swapi\\types\\IModelView\\InitializeShading.md:16-39），逐字要点：① 「Third-party developers should call this method if they are going to use OpenGL shading and are unsure whether shading has already been used for the current window. **This method needs to be called for any window dra",
    ),
    ToolSpec(
        name="solidworks_view_get_frame",
        title="读三维视图所在文档窗口的几何（left/top/width/height/state）",
        module="sw_view", function="get_view_frame",
        inject="view",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 FrameLeft.md）：`System.int FrameLeft {get; set;}`。★ 五个官方页全部存在（逐字路径 `C:\\swapi\\types\\IModelView\\FrameLeft.md` / `FrameTop.md` / `FrameWidth.md` / `FrameHeight.md` / `FrameState.md`），逐字 Signature 如下：`System.int FrameLeft {get; set;}`、`System.int FrameTop {get; set;}`、`System.int FrameWidth {get; set;}`、`System.int FrameHeight {get; set;}`、`System.int ",
    ),
    ToolSpec(
        name="solidworks_simulation_activate_plot",
        title="Activate Result Plot",
        module="sw_simulation_results", function="activate_plot",
        inject="results",
        params=[
            Param("plot_name", str, default="", description=""),
        ],
        doc="★ 官方签名（逐字，来自 CosmosWorksLib~CWResults~ActivatePlot.html）：`Public Function ActivatePlot(`。★★ **官方页存在，但在第三套官方源里**：`C:\\swapi\\types\\` 的 566 个接口目录里**没有** `ICWResults`、也没有 `D:\\AI\\SW\\AI Solidworks\\官方文档\\SWhelp\\cosworks\\` 里那 47 个文件（全属 `ICWLoadsAndRestraintsManager`）⇒ **这两处查不到**；本页在**第三套官方源 `C:\\cworks_vb6\\`**（页头逐字 `SOLIDWORKS Simulation Type Library`，Innovasys Document! X 生成，★ 本仓 `mcp-server/tool",
    ),
    ToolSpec(
        name="solidworks_simulation_delete_plot",
        title="Delete Result Plot",
        module="sw_simulation_results", function="delete_plot",
        inject="results",
        params=[
            Param("plot_name", str, default="", description=""),
        ],
        doc="★ 官方签名（逐字，来自 CosmosWorksLib~CWResults~DeletePlot.html）：`Public Function DeletePlot(`。★★ **官方页存在，但在第三套官方源里**：`C:\\swapi\\types\\` 与 `D:\\AI\\SW\\AI Solidworks\\官方文档\\SWhelp\\cosworks\\` 两处**查不到** `ICWResults`/`DeletePlot`；本页在 `C:\\cworks_vb6\\`（页头逐字 `SOLIDWORKS Simulation Type Library`，★ 本仓已把该目录当官方页引用，见 `mcp-server/tool_specs_batch83.py`），文件名用**共类名 `CWResults`** ⇒ ⚠ 按 `ICWResults` 找会扑空（该目录下 `ICW",
    ),
    ToolSpec(
        name="solidworks_view_set_frame",
        title="View Set Frame",
        module="sw_view", function="set_view_frame",
        inject="view",
        param_alias={"left_px": "left", "top_px": "top", "width_px": "width", "height_px": "height"},
        params=[
            Param("left_px", int, default=0, description="文档窗口在 SOLIDWORKS 客户区内的左边距（像素）。★ 官方 `## Returns` 逐字 `Left position of document window in client area in pixels` ⇒ **单位是像素、不是长度**（故按规则 2 用 `_px` 而不是 `_mm`，与既有 `solidworks_export_bmp` 的 `pixel_width`/`pixel_height` 同一手法）。⚠ 官方页**没有 `## Remarks` 段** ⇒ 取值范围、是否受 DPI 缩放影响、是否要求文档已可见，**全部查不到**（铁律 5，不编）。"),
            Param("top_px", int, default=0, description="文档窗口在 SOLIDWORKS 客户区内的上边距（像素）。★ 官方 `## Returns` 逐字 `Top position of document window in client area in pixels` ⇒ 单位是像素、不是长度。⚠ 同样**没有 `## Remarks` 段** ⇒ 前置与取值范围查不到。"),
            Param("width_px", int, default=0, description="文档窗口在客户区内的宽度（像素）。★ 官方 `## Returns` 逐字 `Width of document window in client area in pixels` ⇒ **不是长度**（像素），故按规则 2 不加 `_mm`，改用 `_px` + `param_alias` 指回真形参 `width`。⚠ 无 `## Remarks` ⇒ 最小宽度限制查不到。"),
            Param("height_px", int, default=0, description="文档窗口在客户区内的高度（像素）。★ 官方 `## Returns` 逐字 `Height of document window in client area in pixels` ⇒ **不是长度**（像素），故用 `_px` + `param_alias` 指回真形参 `height`。⚠ 无 `## Remarks` ⇒ 最小高度限制查不到。⚠★ 官方示例还多设了一个 `ModelView.FrameState = swWindowNormal`，**本函数不设 FrameState**（能力层 `scripts/sw_view.py:265-272` 只写四个属性）⇒ 最小化窗口时调用"),
        ],
        doc="★ 官方签名（逐字，来自 FrameLeft.md）：`System.int FrameLeft {get; set;}`。★ **五个相关官方页全部没有 `## Remarks` 段**（`FrameLeft.md` / `FrameTop.md` / `FrameWidth.md` / `FrameHeight.md` / `FrameState.md` 的结构都是 front matter + 正文一句 + `**Signature**` + `## Returns` + `## Examples` + `## See Also`）⇒ **前置条件查不到**（铁律 5）。本函数写四个属性，各自的 `**Signature**:` 逐字为：`System.int FrameLeft {get; set;}`、`",
    ),
    ToolSpec(
        name="solidworks_view_get_display_mode",
        title="View Get Display Mode",
        module="sw_view", function="get_display_mode",
        inject="view",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 DisplayMode.md）：`System.int DisplayMode {get; set;}`。★ **该页没有 `## Remarks` 段**（front matter + 正文一句 + `**Signature**` + `## Returns` + `## Examples` + `## See Also`）⇒ **前置条件查不到**（铁律 5）。正文逐字：`Gets or sets the display mode for this model view.`；`## Returns` 逐字 `Display mode as defined by [[swViewDisplayMode_e]]` ⇒ ★★ **返回值是枚举码，不是数值、不是长度/角度**（故规则 2 对本行不适用",
    ),
    ToolSpec(
        name="solidworks_view_set_display_mode",
        title="设三维视图的显示模式（线框/着色/隐藏线等）",
        module="sw_view", function="set_display_mode",
        inject="view",
        params=[
            Param("mode", int, default=0, description="显示模式码（官方 DisplayMode，取值域 swViewDisplayMode_e；如 swViewDisplayMode_ShadedWithEdges=5、swViewDisplayMode_IntegratedPreview=13，取值页 C:\\swapi\\enums\\swViewDisplayMode_e.md 共 13 个成员）。★ 无量纲（是枚举码不是长度）故不加后缀。★ 本仓刻意**不内嵌副本**（来源块 scripts/sw_view.py:248-249 逐字：『枚举值官方在 C:\\swapi 的 swconst 册里可查，本模块**不内嵌副本**（会随版本漂移"),
        ],
        doc="★ 官方签名（逐字，来自 DisplayMode.md）：`**Signature**: `System.int DisplayMode {get; set;}``。kind=property，**无 `## Remarks` 段**（★ 铁律 5：查不到就写查不到，不替官方补）。`## Returns` 逐字「Display mode as defined by [[swViewDisplayMode_e]]」⇒ 值域是 swViewDisplayMode_e（官方枚举页 C:\\swapi\\enums\\swViewDisplayMode_e.md，13 个成员，值 1..13）。`## Examples` 只列一份：Set_Model_Display_Mode_Example_VB。`## See Also` 点名 IModelView::StartDy",
    ),
    ToolSpec(
        name="solidworks_view_get_scale",
        title="取三维视图的缩放比（IModelView.Scale）",
        module="sw_view", function="get_view_scale",
        inject="view",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 Scale.md）：`**Signature**: `System.double Scale {get; set;}``。kind=property。★ **该官方页第一句就是废弃声明**，逐字：「Obsolete. Superseded by [[IModelView::Scale2]]。」——**无 `## Returns`、无 `## Remarks`、无 `## Examples`**（★ 查不到就写查不到，不替官方补）。⇒ ★ 本仓 `get_view_scale` 用的正是这个**已废弃**成员，官方指定的继任者是 `Scale2`（C:\\swapi\\types\\IModelView\\Scale2.md，其 `## Returns` 逐字「Scale factor」，`## Remarks` 给出用法",
    ),
    ToolSpec(
        name="solidworks_view_set_scale",
        title="View Set Scale",
        module="sw_view", function="set_view_scale",
        inject="view",
        params=[
            Param("scale", float, default=0.0, description="视图缩放比（新的 Scale2 值）。★ **无量纲**（不是长度、不是角度 ⇒ 按规则 2 不加 `_mm`/`_deg`；与既有 solidworks_drawing_view_set_scale 的 `scale` 同一口径）。⚠ 官方给的是**绝对比例**而非倍数：要放大 2 倍应先读当前比例再乘 2 后写回（本仓另有 zoom_view 走倍数那条路）。⚠ 官方成员 IModelView.Scale 已标 Obsolete（后继 Scale2），而本函数写的是基础版 ⇒ 挂出时应在 doc 里带上这条。"),
        ],
        doc="★ 官方签名（逐字，来自 Scale.md）：`System.double Scale {get; set;}`。★ 该页**没有 `## Remarks` 段**（全文只有 front matter + 正文一句 + See Also）⇒ 前置查不到。正文逐字：`Obsolete. Superseded by [[IModelView::Scale2]].` ⇒ ★★ 本仓 `set_view_scale` 写的是**官方已废弃的 `Scale`**。后继页 `C:\\swapi\\types\\IModelView\\Scale2.md` 的 `**Signature**:` 逐字是 `System.double Scale2 {get; set;}`，其 `## Returns` 是 `Scale fact",
    ),
    ToolSpec(
        name="solidworks_view_zoom_by_factor",
        title="View Zoom By Factor",
        module="sw_view", function="zoom_view",
        inject="view",
        params=[
            Param("factor", float, default=0.0, description="缩放**倍数**。★ **无量纲**（不是长度、不是角度 ⇒ 按规则 2 不加 `_mm`/`_deg`）。★ 官方逐字给的区间是 `0.0 < factor < 2.0`：>1 放大、<1 缩小（**两端都是开区间，0 与 2 不含**）⇒ 传 0 / ≥2 官方未定义行为，本工具不编语义、只在 desc 里如实写明。"),
        ],
        doc="★ 官方签名（逐字，来自 ZoomByFactor.md）：`void ZoomByFactor( System.double Factor )`。摘要逐字：`Modifies the zoom factor for the model view.`；`## Parameters` 只有一条 `- **Factor**: Zoom factor`（**官方没写单位**）。★ `## Remarks` 逐字：`The zoom factor should be in the range 0.0 < factor < 2.0. For factor greater than 1, the model view is zoomed in, for factor less than 1 the model view is zoomed out.`",
    ),
    ToolSpec(
        name="solidworks_view_translate_view",
        title="Translate Model View",
        module="sw_view", function="translate_view",
        inject="view",
        param_alias={"dx_mm": "dx", "dy_mm": "dy"},
        params=[
            Param("dx_mm", float, default=0.0, description="★ 规则 2 改名：仓库形参 `dx` → `dx_mm`（长度带 `_mm`）。官方 `IModelView.TranslateBy` 的第一个参数。★ 官方 Parameters 逐字：「**X**: Translation in X direction, **in meters** and relative to X,Y axes of the graphics area」⇒ ★ 官方单位是**米**，且相对**图形区**的 X/Y 轴。★ 边界换算：本工具对外收**毫米**、在边界只换算一次成米（`sw_connect.mm()` 同一手法，参见 `solidworks_add_dim"),
            Param("dy_mm", float, default=0.0, description="★ 规则 2 改名：仓库形参 `dy` → `dy_mm`（长度带 `_mm`）。官方 `IModelView.TranslateBy` 的第二个参数。★ 官方 Parameters 逐字：「**Y**: Translation in Y direction, **in meters** and relative to **Windows** X,Y axes of the graphics area」⇒ ★ 注意官方对 Y 特意写的是 **Windows 的 X,Y 轴**（X 用的是「X,Y axes of the graphics area」）⇒ 两个轴的基准措辞在官方页里**不一致**"),
        ],
        doc="★ 官方签名（逐字，来自 TranslateBy.md）：`**Signature**: `void TranslateBy( System.double X, System.double Y )``。官方页有 `## Remarks`（逐字要点）：指定一个向量来平移当前 SOLIDWORKS **图形区**；该向量**单位是米**、相对图形区的 X,Y 轴；★ 「This vector has **no relation to the SOLIDWORKS triad axis** that is displayed in the graphics area」（与模型三轴无关）；本方法等价于用户界面上对图形区的 **panning**（平移）。★ 调用序证据（`docs/recon/member-to-example-index.md:3303` 登记 2 个例子 → `Set_Viewp",
    ),
    ToolSpec(
        name="solidworks_view_rotate_about_center",
        title="Rotate Model View About Center",
        module="sw_view", function="rotate_about_center",
        inject="view",
        param_alias={"x_angle_deg": "angle_x", "y_angle_deg": "angle_y"},
        params=[
            Param("x_angle_deg", float, default=0.0, description="★ 规则 2 改名：仓库形参 `angle_x` → `x_angle_deg`（角度带 `_deg`；★ 由于官方形参名是 `XAngle`，`_deg` 后缀不能直接挂在 `angle_x` 后面凑成自动别名，故同时给 `param_alias`）。官方 `IModelView.RotateAboutCenter` 的第一个参数。★★ **单位官方未标注（铁律 5：查不到就说查不到）** —— 官方页 Parameters 逐字只有「**XAngle**: Rotation about the X axis」，**没有单位**；该页**整页没有 `## Remarks` 段**。★ 因此本"),
            Param("y_angle_deg", float, default=0.0, description="★ 规则 2 改名：仓库形参 `angle_y` → `y_angle_deg`（理由同上，同时配 `param_alias`）。官方 `IModelView.RotateAboutCenter` 的第二个参数。★★ **单位官方未标注** —— Parameters 逐字只有「**YAngle**: Rotation about the Y axis」，无单位、无 Remarks ⇒ **原样透传不换算**，理由与 `x_angle_deg` 完全相同（同一条官方页、同一处缺口，不重复编造依据）。★ `scripts/sw_view.py:311-313` 的来源块也逐字记着同一件事：「⚠ "),
        ],
        doc="★ 官方签名（逐字，来自 RotateAboutCenter.md）：`**Signature**: `void RotateAboutCenter( System.double XAngle, System.double YAngle )``。★ **该官方页没有 `## Remarks` 段** —— 逐段核过：只有 front-matter（type/member/kind/assembly/namespace/category）、标题「Rotates the model view about the screen X and Y axes.」、`## Parameters`、`## Examples`、`## See Also` ⇒ 前置条件与语义**官方无文档**，故本行不编前置（铁律 5）。★ Parameters 逐字只有两条且**均未标单位**：「**XAngle**: Rotation about the X axi",
    ),
    ToolSpec(
        name="solidworks_view_roll_view",
        title="Roll the Model View About the Line of Sight (IModelView.RollBy)",
        module="sw_view", function="roll_view",
        inject="view",
        param_alias={"angle_deg": "angle"},
        params=[
            Param("angle_deg", float, default=0.0, description="绕视线轴（line of sight）滚转的角度。★ **规则 2 改名** `angle` → `angle_deg`（见 param_alias；形参名含 `angle` ⇒ 角度类必须带 `_deg`）。⚠ **单位官方页没写**：`RollBy.md` 的参数表逐字只有「Angle by which to roll the model view about the line of sight」，度/弧度都没标；★ 盘上唯一的单位线索是官方 VBA 示例 `swModelView.RollBy (90#)` 且其 Postconditions 逐字「Rolls the model vie"),
        ],
        doc="★ 官方签名（逐字，来自 RollBy.md）：`void RollBy( System.double Angle )`。★ 官方页**没有 `## Remarks` 段**（逐行读过，25 行只有 front-matter + 一句标题 + Signature + Parameters + Examples + See Also）⇒ 语义只能取标题句与参数表：① 标题逐字「Rolls the model view about the line of sight by the specified angle.」② 参数逐字「**Angle**: Angle by which to roll the model view about the line of sight」⇒ **未写单位、未写取值范围、未写是否立即生",
    ),
    ToolSpec(
        name="solidworks_view_get_camera",
        title="Get the Camera of the Model View (IModelView.Camera property)",
        module="sw_view", function="get_view_camera",
        inject="view",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 Camera.md）：`Camera Camera {get; set;}`。★ 官方页逐字要点：① 标题句「Gets or sets the camera.」② `## Returns` = `[[Camera]]`（⇒ 返回 COM 对象 `ICamera`，**不是**标量）；③ `## Remarks` **唯一一段**逐字：「If the return value is Nothing or NULL, then the camera view for this model is turned off.」⇒ ★★ **判空是官方写明的语义**，也是本函数唯一可靠的回读判据（`collect_view_evidence` 里 `has_camera = get_",
    ),
    ToolSpec(
        name="solidworks_view_set_camera_by_name",
        title="按相机特征名切换三维模型视图 · IModelView.SetCameraByName",
        module="sw_view", function="set_view_camera_by_name",
        inject="view",
        params=[
            Param("name", str, default="", description="相机（camera）的**特征名**。官方页 Parameters 逐字：'Feature name of the camera to use to set the model view, if in camera view mode'。★ 合法取值**不是**预置清单：官方示例的取法是 `IModelDocExtension.GetCameraCount` → `GetCameraById(i)` → 得到的 `ICamera`（官方示例注释逐字 'A camera is a feature'）→ `.Name`（C:\\swapi\\examples\\Turn_Cameras_On_an"),
        ],
        doc="★ 官方签名（逐字，来自 SetCameraByName.md）：`System.bool SetCameraByName( System.string Name )`。官方页 `IModelView.SetCameraByName`（kind: method，category: User-interface Interfaces）：摘要逐字 'Sets the model view to that of the specified camera, if in camera view mode.'；Returns 逐字 'True if the camera is set, false if not'。`## Remarks` 是一张两行表，逐字：「A nonexistent camera when another camera view is active ",
    ),
    ToolSpec(
        name="solidworks_view_has_perspective",
        title="View Has Perspective (IModelView.HasPerspective)",
        module="sw_view", function="has_perspective",
        inject="view",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 HasPerspective.md）：``System.bool HasPerspective()``。★ 官方页**没有 `## Remarks` 段** ⇒ 不编（铁律 5）。页内逐字可摘的只有两处：摘要「Determines if the model view currently has perspective.」与 `## Returns`「True if the view currently has perspective viewing turned on, false otherwise」⇒ **零参**、返回布尔。`kind: method` / `category: User-interface Interfaces`（front-matter 逐字）。",
    ),
    ToolSpec(
        name="solidworks_view_add_perspective",
        title="View Add Perspective (IModelView.AddPerspective)",
        module="sw_view", function="add_perspective",
        inject="view",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 AddPerspective.md）：``void AddPerspective()``。★ 官方页**没有 `## Remarks` 段、也没有 `## Returns` 段** ⇒ 不编（铁律 5）。页内逐字可摘的只有摘要「Adds perspective to the model view.」⇒ **零参、无返回值（void）**。`kind: method` / `category: User-interface Interfaces`（front-matter 逐字）。★ 同族的 `RemovePerspective.md` 也在同目录存在（反向操作），本批未取。",
    ),
    ToolSpec(
        name="solidworks_view_remove_perspective",
        title="View Remove Perspective",
        module="sw_view", function="remove_perspective",
        inject="view",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 RemovePerspective.md）：`void RemovePerspective()`。★ 该页**没有 `## Remarks` 段**、也没有 `## Parameters` / `## Returns` 段（全文 = front matter + 标题 + 正文一句 + `## See Also`）⇒ **前置查不到**（铁律 5，不编）。正文逐字一句：`Removes perspective from the model view.`（**动词 Remove，无返回值语义**）。`## See Also` 列 `IModelView::AddPerspective Method` / `HasPerspective Method` / `GetEyePoint` / `S",
    ),
    ToolSpec(
        name="solidworks_view_start_dynamics",
        title="View Start Dynamics",
        module="sw_view", function="start_dynamics",
        inject="view",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 StartDynamics.md）：`void StartDynamics()`。摘要逐字：`Provides faster rotation of model views.`；签名 `void StartDynamics()`（**零参、无返回值语义**）。`## Remarks` 三条，逐字要点：① 「After setting swUserPreferenceIntegerValue_e.swLevelOfDetail high enough, this method can be used at the beginning of dynamic model view changes to: change HLR or HLV mode to wireframe mo",
    ),
    ToolSpec(
        name="solidworks_view_stop_dynamics",
        title="View Stop Dynamics (IModelView.StopDynamics)",
        module="sw_view", function="stop_dynamics",
        inject="view",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 StopDynamics.md）：``void StopDynamics()``。★ 官方页**有 `## Remarks` 段**，逐字：「Use this method with [[IModelView::StartDynamics]] at the end of dynamic view motion. This method returns the view to its previous HLR, HLV, or shaded mode and recalculates the display.」「After calling this method, you must call [[IModelDoc2::GraphicsRedraw2]] or [[IMod",
    ),
    ToolSpec(
        name="solidworks_view_get_next",
        title="View Get Next Model View (IModelView.GetNext)",
        module="sw_view", function="get_next_view",
        inject="view",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 GetNext.md）：``System.object GetNext()``。★ 官方页**有 `## Returns` 与 `## Remarks` 两段**，逐字：`## Returns`「Next [[model view]] or Nothing or null if no more model views exist」；`## Remarks`「You can traverse through the model views in a document by using this method. When this method returns Nothing or null, you have reached the end of the list.」「Se",
    ),
    ToolSpec(
        name="solidworks_simulation_get_buckling_load_factors",
        title="Get Buckling Load Factors",
        module="sw_simulation_results", function="get_buckling_load_factors",
        inject="results",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 sw_simulation_results.py）：`查不到（官方页不存在 —— `C:\\swapi\\types\\` 无 `ICWResults` 目录；CHM 的 `SWhelp\\cosworks\\` 只覆盖 `ICWLoadsAndRestraintsManager` 一族，没有 `ICWResults~GetBucklingLoadFactors`）。`。查不到 —— 没有官方页可摘 Remarks。`docs\\recon\\member-inventory.md:696` 对该成员三列均记「查不到（该源无此字段）」。本仓来源块（sw_simulation_results.py:194-207）逐字记载的反射签名是 `Object GetBucklingLoadFactors(Int32&)`（**零**实参 + 1 by-ref）。",
    ),
    ToolSpec(
        name="solidworks_get_view_model_doc",
        title="Get the Document That Owns a 3D Model View",
        module="sw_view", function="get_view_model_doc",
        inject="view",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 sw_view.py）：`查不到 —— C:\\swapi\\types\\IModelView\\GetModelDoc.md 不存在（IModelView 目录下 79 个成员文件里没有 GetModelDoc.md；全 swapi 里带 GetModelDoc 的 .md 只有 IComponent2 / IDerivedPartFeatureData / IMirrorPartFeatureData 三个**别的接口**）`。★ 真源是**本仓** `scripts/sw_view.py` 的 `get_view_model_doc`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到（无官方 .md 页 ⇒ 无 ## Remarks 可摘；反射只给签名与返回类型，���给语义）",
    ),
    ToolSpec(
        name="solidworks_collect_view_evidence",
        title="Read Back the 3D Model View State",
        module="sw_view", function="collect_view_evidence",
        inject="view",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 sw_view.py）：`查不到 —— 「collect_view_evidence」本身**不是官方成员**（官方 IModelView 没有同名成员，IModelView 目录 79 个 .md 里也没有）⇒ 本仓自研的**聚合回读**，无单一官方签名可抄。它内部只读 14 个官方成员，逐字签名见 evidence.constituent_signatures。`。★ 真源是**本仓** `scripts/sw_view.py` 的 `collect_view_evidence`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到（无单一官方成员可摘 Remarks）；来源块 scripts/sw_view.py:458-462 逐字：「沿用『只取已核实成员』的写法」+「⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）」",
    ),
    ToolSpec(
        name="solidworks_simulation_get_worst_jacobian_ratio",
        title="Read the Worst Jacobian Ratio of the Study Mesh",
        module="sw_simulation_results", function="get_worst_jacobian_ratio",
        inject="mesh",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 sw_simulation_results.py）：`查不到（官方页不存在）—— ★ `C:\\swapi\\types\\` 下**没有 `ICWMesh\\` 目录**；对整个 `C:\\swapi` 递归 grep `ICWMesh|GetWorstJacobianRatio|IsComponentFailed` **0 命中**；`C:\\swapi\\types\\` 里唯一的 Mesh 族是 `IMeshBody`（**另一个族**，见 `Get_Mes`。★ **没有 `## Remarks`** —— 因为根本没有官方页可抄（该模块 docstring 逐字：「⚠ **这两个接口族官方 CHM 没有文档页**（cosworks 册只覆盖 `ICWLoadsAndRestraintsManager` 一个族），因此**没有参数语义说明**」）。⇒ 前置、单位、取值区间**一律查不到**，本工具**不编**（铁律 5）。可用的事实只有反射签名本身：`Double` 返回 ⇒ 无量纲比值（雅可比畸变指标），**零参** ⇒ 不需要任何输入。本仓包装 `scripts/sw_simulation_results.py:249` 逐字 `return ",
    ),
    ToolSpec(
        name="solidworks_simulation_is_component_failed",
        title="Check Whether a Simulation Component Failed Meshing",
        module="sw_simulation_results", function="is_component_failed",
        inject="mesh",
        params=[
            Param("component_name", str, default="", description="组件名（**字符串名，不是坐标**）—— ★ **无量纲**（不是长度、不是角度 ⇒ 按规则 2 不加 `_mm`/`_deg`）。★ 反射签名逐字是 `Boolean IsComponentFailed2(String)`：**入参类型只写 `String`，官方没写它是组件名 / 文件名 / 路径**，两套官方源也查不到语义 ⇒ 本仓源码逐字按名直译成 `component_name` 并在注释里标明「语义官方无文档」，**不编**取值格式。⚠ `scripts/sw_simulation_results.py:254` 的签名**没有默认值**（`def is_component_fai"),
        ],
        doc="★ 官方签名（逐字，来自 sw_simulation_results.py）：`查不到（官方页不存在）—— ★ `C:\\swapi\\types\\` 下**没有 `ICWMesh\\` 目录**；对整个 `C:\\swapi` 递归 grep `ICWMesh|GetWorstJacobianRatio|IsComponentFailed` **0 命中**（`types\\` 里唯一的 Mesh 族是 `IMeshBody`，另一个族）。⇒ 签名只能取自本仓反射转储 `_raw\\r`。★ **没有 `## Remarks`** —— 因为根本没有官方页可抄（同模块 docstring 逐字：ICWResults / ICWMesh 两族「官方 CHM 没有文档页」）。⇒ 前置、单位、字符串的取值格式**一律查不到**，本工具**不编**（铁律 5）。可用事实只有反射签名本身：`Boolean` 返回 ⇒ 判据是布尔；**1 个 `String` 入参**，无 by-ref 出参。本仓包装 `scripts/sw_simulation_results.py:254` 逐字 `return bool(_checked(MESH_ARITY, mesh, 'IsComponent",
    ),
]
