"""★ 批次 86：由 Bunny 扇出产出、**经门禁**（`tools/check_bunny_toolspec_rows.py`）过滤后的 ToolSpec 声明。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   sw_simulation_results · sw_simulation_study_options · sw_view
# 定位:   ★ 规格 `specs/204-tool-ramp/spec.md` 的批 86；
#         ★★ **本文件由 `tools/build_toolspec_batch_from_rows.py` 生成** ——
#         行来自 Bunny 子代理（**只读官方源与仓库**），而**判据、门禁、真机、提交归主线** ✓
# 官方依据: 逐行的 `official_file` / `official_signature` 见下表（★ 每条都是官方页的逐字
#           签名）
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
        module="sw_simulation_results",
        function="collect_mesh_evidence",
        inject="mesh",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_simulation_results.py）：`查不到 —— 本函数不是 SolidWorks API 成员（官方 API 参"
            "考里没有 collect_mesh_evidence 这个成员），且 `C:\\swapi\\types\\ICWMesh\\` 目录本身就不存在（Test-Path=Fa"
            "lse），故连可逐字抄的 `**Signature**:` 行都没有。`。★★ source_kind=repo_original：**真源是本仓** `scripts/"
            "sw_simulation_results.py` —— 函数体 :268-291，加它上方 :259-267 的来源块（逐字「仓库: 本项目自身既有模式（"
            "scripts/sw_simulation_study.py::collect_study_evidence）」，定位逐字「网格状态证据回读，沿用『只取已核实成"
            "员』的写法」）。★ 为什么官方 API 页查不到（本机三处都查过）：① `C:\\swapi\\types\\` 下 **566 个目录里 0 个"
            " `ICW*`**（`Get-ChildItem"
        ),
        doc=(
            "Read mesh quality readings from the mesh object of a simulation study. Read-only; it returns element and n"
            "ode counts, mesh and mesher types, quality, mesh state, the mesh-failed flag, element sizes, growth and as"
            "pect ratios, jacobian points, mesh control and loop counts, the failed component count and the worst jacob"
            "ian ratio, and it raises when no mesh object is available."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_set_registered_study_option",
        title="Set One Registered Study Option On The Injected Options Object",
        module="sw_simulation_study_options",
        function="set_option",
        inject="options",
        params=[
            Param(
                "family",
                str,
                default="",
                description=(
                    "Option family name, one of the nine registered families such as 'ICWStaticStudyOptions' or 'ICWFre"
                    "quencyStudyOptions'; an unregistered name raises. Defaults to empty."
                ),
            ),
            Param(
                "name",
                str,
                default="",
                description=(
                    "Setter name that exists in that family's registry entry, for example 'ComputeFreeBodyForce2'; a mi"
                    "sspelling raises and lists the entries that family does register. Defaults to empty."
                ),
            ),
            Param(
                "value",
                str,
                default="",
                description=(
                    "The value as text, converted to the registered type (int, bool, float or string) before it is set."
                    " Defaults to empty."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_simulation_study_options.py）：`查不到 —— 本函数不是 SolidWorks API 成员（官方 A"
            "PI 里没有 set_option 这个成员）。★ 且它的成员名是**变量** `name`，签名按项才定：值域由本仓登记表 `STUDY_OP"
            "TION_SETTERS`（:99-360）给出，每个项都是反射里的 `set_XXX(...)` **属性**（不是方法），而 `C:\\swapi\\types"
            "\\` 下**没有 ICWS`。★★ source_kind=repo_original：**真源是本仓** `scripts/sw_simulation_study_options.py` "
            "—— 函数体 :602-654，加它上方 :578-586 的来源块（逐字「仓库: 本项目自身（本任务新增的能力层）… 定位: 通用 s"
            "etter 的取值校验与调用」）。★ 官方 API 页查不到（本机三处都查过）：① `C:\\swapi\\types\\` 下 566 个目录里 "
            "0 个 `ICW*`；② 对整个 `C:\\swapi` grep `ICWStaticStudyOptions|ICWFrequencyStudyOptions|"
        ),
        doc=(
            "Set one registered solver option on a simulation study by family and option name. Writes the option throug"
            "h the study options object; an unknown family or option name raises an error that lists the valid entries,"
            " so list the registered setters first."
        ),
    ),
    ToolSpec(
        name="solidworks_view_activate",
        title="Activate Model View",
        module="sw_view",
        function="activate_view",
        inject="view",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 Activate.md）：`void Activate()`。查不到 —— 该官方页**没有 `## Remarks` 段**（全文"
            "只有正文一句 'Activates the model view.' + `**Signature**: void Activate()` + `## See Also` 的两个链接 `IM"
            "odelView Interface` / `IModelView Members`）⇒ 官方**未给任何前置条件或语义细节**。"
        ),
        doc=(
            "Activate the active model view of the open document. It takes no arguments, returns nothing, modifies only"
            " which view is active, and the reference documents no preconditions or other semantics for it."
        ),
    ),
    ToolSpec(
        name="solidworks_view_redraw",
        title="Redraw Graphics Window",
        module="sw_view",
        function="redraw_view",
        inject="view",
        params=[
            Param("scope_or_none", str, default="", description=(
                                                        "Region to redraw as the four integers giving its boundary; the"
                                                        " reference does not document the object form, and an empty val"
                                                        "ue redraws the entire graphics window. Defaults to empty."
                                                    )),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 GraphicsRedraw.md）：`void GraphicsRedraw( System.object Rect )`。`## Parameters` "
            "逐字：「**Rect**: Array of four integers or longs indicating the boundary of the region in the SOLIDWORKS "
            "graphics window to redraw; **if the array is empty, then the entire graphics window is redrawn**」。`## Re"
            "marks` 逐字：「This method forces the specified region or the entire SOLIDWORKS gr"
        ),
        doc=(
            "Refresh the graphics window or one rectangular region of it. It modifies no model geometry and only forces"
            " a repaint; pass a region to redraw that part, leave it empty to redraw the whole window, and it reports s"
            "uccess after the call."
        ),
    ),
    ToolSpec(
        name="solidworks_view_initialize_shading",
        title="初始化三维视图的 OpenGL 着色",
        module="sw_view",
        function="initialize_shading",
        inject="view",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 InitializeShading.md）：`void InitializeShading()`。官方页存在且有完整 `## Remarks`"
            "（C:\\swapi\\types\\IModelView\\InitializeShading.md:16-39），逐字要点：① 「Third-party developers should "
            "call this method if they are going to use OpenGL shading and are unsure whether shading has already been u"
            "sed for the current window. **This method needs to be called for any window dra"
        ),
        doc=(
            "Start shading for the current window before using OpenGL shading. It modifies the window shading state onl"
            "y, takes no arguments and returns nothing; call it when you use OpenGL shading and are unsure whether shad"
            "ing has already been used for that window."
        ),
    ),
    ToolSpec(
        name="solidworks_view_get_frame",
        title="读三维视图所在文档窗口的几何（left/top/width/height/state）",
        module="sw_view",
        function="get_view_frame",
        inject="view",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 FrameLeft.md）：`System.int FrameLeft {get; set;}`。★ 五个官方页全部存在（逐字路径 "
            "`C:\\swapi\\types\\IModelView\\FrameLeft.md` / `FrameTop.md` / `FrameWidth.md` / `FrameHeight.md` / `Frame"
            "State.md`），逐字 Signature 如下：`System.int FrameLeft {get; set;}`、`System.int FrameTop {get; set;}`、`"
            "System.int FrameWidth {get; set;}`、`System.int FrameHeight {get; set;}`、`System.int "
        ),
        doc=(
            "Read the document window frame: left, top, width and height. Read-only; it also returns the window state, "
            "the reference gives no unit for these readings, and it documents no preconditions for reading them."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_activate_plot",
        title="Activate Result Plot",
        module="sw_simulation_results",
        function="activate_plot",
        inject="results",
        params=[
            Param("plot_name", str, default="", description=(
                                                    "Name of the result plot to activate, as the results object names i"
                                                    "t. Defaults to empty."
                                                )),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 CosmosWorksLib~CWResults~ActivatePlot.html）：`Public Function ActivatePlot(`。★★ *"
            "*官方页存在，但在第三套官方源里**：`C:\\swapi\\types\\` 的 566 个接口目录里**没有** `ICWResults`、也没有 `"
            "D:\\AI\\SW\\AI Solidworks\\官方文档\\SWhelp\\cosworks\\` 里那 47 个文件（全属 `ICWLoadsAndRestraintsManage"
            "r`）⇒ **这两处查不到**；本页在**第三套官方源 `C:\\cworks_vb6\\`**（页头逐字 `SOLIDWORKS Simulation Type Li"
            "brary`，Innovasys Document! X 生成，★ 本仓 `mcp-server/tool"
        ),
        doc=(
            "Activate one result plot of a solved simulation study. It modifies which plot is active in the results obj"
            "ect and needs a study that has already produced results."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_delete_plot",
        title="Delete Result Plot",
        module="sw_simulation_results",
        function="delete_plot",
        inject="results",
        params=[
            Param("plot_name", str, default="", description=(
                                                    "Name of the result plot to delete, as the results object names it."
                                                    " Defaults to empty."
                                                )),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 CosmosWorksLib~CWResults~DeletePlot.html）：`Public Function DeletePlot(`。★★ **官"
            "方页存在，但在第三套官方源里**：`C:\\swapi\\types\\` 与 `D:\\AI\\SW\\AI Solidworks\\官方文档\\SWhelp\\cosw"
            "orks\\` 两处**查不到** `ICWResults`/`DeletePlot`；本页在 `C:\\cworks_vb6\\`（页头逐字 `SOLIDWORKS Simulati"
            "on Type Library`，★ 本仓已把该目录当官方页引用，见 `mcp-server/tool_specs_batch83.py`），文件名用**共类名 "
            "`CWResults`** ⇒ ⚠ 按 `ICWResults` 找会扑空（该目录下 `ICW"
        ),
        doc=(
            "Delete one result plot from the results of a solved simulation study. It deletes the named plot from the r"
            "esults object and needs a study that has already produced results."
        ),
    ),
    ToolSpec(
        name="solidworks_view_set_frame",
        title="View Set Frame",
        module="sw_view",
        function="set_view_frame",
        inject="view",
        param_alias={
            "left_px": "left",
            "top_px": "top",
            "width_px": "width",
            "height_px": "height",
        },
        params=[
            Param(
                "left_px",
                int,
                default=0,
                description="Left position of the document window in the client area, in pixels. Defaults to 0.",
            ),
            Param(
                "top_px",
                int,
                default=0,
                description="Top position of the document window in the client area, in pixels. Defaults to 0.",
            ),
            Param(
                "width_px",
                int,
                default=0,
                description="Width of the document window in the client area, in pixels. Defaults to 0.",
            ),
            Param(
                "height_px",
                int,
                default=0,
                description="Height of the document window in the client area, in pixels. Defaults to 0.",
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 FrameLeft.md）：`System.int FrameLeft {get; set;}`。★ **五个相关官方页全部没有 `## "
            "Remarks` 段**（`FrameLeft.md` / `FrameTop.md` / `FrameWidth.md` / `FrameHeight.md` / `FrameState.md` 的结"
            "构都是 front matter + 正文一句 + `**Signature**` + `## Returns` + `## Examples` + `## See Also`）⇒ **前置"
            "条件查不到**（铁律 5）。本函数写四个属性，各自的 `**Signature**:` 逐字为：`System.int FrameLeft {get; set;"
            "}`、`"
        ),
        doc=(
            "Set the document window frame: left, top, width and height. It modifies the window layout only and does no"
            "t set the window state; the reference documents no value ranges, no DPI handling and no precondition for i"
            "t."
        ),
    ),
    ToolSpec(
        name="solidworks_view_get_display_mode",
        title="View Get Display Mode",
        module="sw_view",
        function="get_display_mode",
        inject="view",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 DisplayMode.md）：`System.int DisplayMode {get; set;}`。★ **该页没有 `## Remarks` "
            "段**（front matter + 正文一句 + `**Signature**` + `## Returns` + `## Examples` + `## See Also`）⇒ **前置条"
            "件查不到**（铁律 5）。正文逐字：`Gets or sets the display mode for this model view.`；`## Returns` 逐字 `D"
            "isplay mode as defined by [[swViewDisplayMode_e]]` ⇒ ★★ **返回值是枚举码，不是数值、不是长度/角度**（故规"
            "则 2 对本行不适用"
        ),
        doc=(
            "Read the display mode of the model view as an swViewDisplayMode code. Read-only; the value is an enum code"
            " and not a length or an angle, and the reference documents no preconditions for reading it."
        ),
    ),
    ToolSpec(
        name="solidworks_view_set_display_mode",
        title="设三维视图的显示模式（线框/着色/隐藏线等）",
        module="sw_view",
        function="set_display_mode",
        inject="view",
        params=[
            Param(
                "mode",
                int,
                default=0,
                description=(
                    "Display mode code from swViewDisplayMode, whose 13 members run from 1 to 13, for example 5 for sha"
                    "ded with edges. Defaults to 0."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 DisplayMode.md）：`**Signature**: `System.int DisplayMode {get; set;}``。kind=prope"
            "rty，**无 `## Remarks` 段**（★ 铁律 5：查不到就写查不到，不替官方补）。`## Returns` 逐字「Display mode as "
            "defined by [[swViewDisplayMode_e]]」⇒ 值域是 swViewDisplayMode_e（官方枚举页 C:\\swapi\\enums\\swViewDispl"
            "ayMode_e.md，13 个成员，值 1..13）。`## Examples` 只列一份：Set_Model_Display_Mode_Example_VB。`## See Als"
            "o` 点名 IModelView::StartDy"
        ),
        doc=(
            "Set the display mode of the model view from an swViewDisplayMode code. It modifies how the model is drawn "
            "rather than the model itself; the enum has 13 members running from 1 to 13."
        ),
    ),
    ToolSpec(
        name="solidworks_view_get_scale",
        title="取三维视图的缩放比（IModelView.Scale）",
        module="sw_view",
        function="get_view_scale",
        inject="view",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 Scale.md）：`**Signature**: `System.double Scale {get; set;}``。kind=property。★ **"
            "该官方页第一句就是废弃声明**，逐字：「Obsolete. Superseded by [[IModelView::Scale2]]。」——**无 `## Returns"
            "`、无 `## Remarks`、无 `## Examples`**（★ 查不到就写查不到，不替官方补）。⇒ ★ 本仓 `get_view_scale` 用的正"
            "是这个**已废弃**成员，官方指定的继任者是 `Scale2`（C:\\swapi\\types\\IModelView\\Scale2.md，其 `## Returns"
            "` 逐字「Scale factor」，`## Remarks` 给出用法"
        ),
        doc=(
            "Read the scale factor of the model view. Read-only; it reads the scale member that the reference marks as "
            "superseded by Scale2, and it documents no preconditions for reading it."
        ),
    ),
    ToolSpec(
        name="solidworks_view_set_scale",
        title="View Set Scale",
        module="sw_view",
        function="set_view_scale",
        inject="view",
        params=[
            Param(
                "scale",
                float,
                default=0.0,
                description="New absolute scale factor of the view, a plain ratio with no unit. Defaults to 0.0.",
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 Scale.md）：`System.double Scale {get; set;}`。★ 该页**没有 `## Remarks` 段**（全文"
            "只有 front matter + 正文一句 + See Also）⇒ 前置查不到。正文逐字：`Obsolete. Superseded by [[IModelView::Sc"
            "ale2]].` ⇒ ★★ 本仓 `set_view_scale` 写的是**官方已废弃的 `Scale`**。后继页 `C:\\swapi\\types\\IModelView\\"
            "Scale2.md` 的 `**Signature**:` 逐字是 `System.double Scale2 {get; set;}`，其 `## Returns` 是 `Scale fact"
        ),
        doc=(
            "Set the scale factor of the model view as an absolute ratio, not a multiplier. It modifies the view only, "
            "so to zoom by a factor read the current scale first, multiply it yourself and write the result back; the z"
            "oom-by-factor tool already does that multiplication."
        ),
    ),
    ToolSpec(
        name="solidworks_view_zoom_by_factor",
        title="View Zoom By Factor",
        module="sw_view",
        function="zoom_view",
        inject="view",
        params=[
            Param(
                "factor",
                float,
                default=0.0,
                description=(
                    "Zoom multiplier, strictly between 0 and 2: above 1 zooms in and below 1 zooms out. Defaults to 0.0"
                    "."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 ZoomByFactor.md）：`void ZoomByFactor( System.double Factor )`。摘要逐字：`Modifies"
            " the zoom factor for the model view.`；`## Parameters` 只有一条 `- **Factor**: Zoom factor`（**官方没写单"
            "位**）。★ `## Remarks` 逐字：`The zoom factor should be in the range 0.0 < factor < 2.0. For factor greate"
            "r than 1, the model view is zoomed in, for factor less than 1 the model view is zoomed out.`"
        ),
        doc=(
            "Zoom the model view in or out by a multiplier. It modifies the view only; the factor must lie strictly bet"
            "ween 0 and 2, values above 1 zoom in and values below 1 zoom out, and the reference defines no behaviour o"
            "utside that range."
        ),
    ),
    ToolSpec(
        name="solidworks_view_translate_view",
        title="Translate Model View",
        module="sw_view",
        function="translate_view",
        inject="view",
        param_alias={"dx_mm": "dx", "dy_mm": "dy"},
        params=[
            Param(
                "dx_mm",
                float,
                default=0.0,
                description="Pan offset along the graphics-area X axis, in millimetres. Defaults to 0.0.",
            ),
            Param(
                "dy_mm",
                float,
                default=0.0,
                description=(
                    "Pan offset along the graphics-area Y axis, in millimetres; the reference words this axis different"
                    "ly from the X axis. Defaults to 0.0."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 TranslateBy.md）：`**Signature**: `void TranslateBy( System.double X, System.double"
            " Y )``。官方页有 `## Remarks`（逐字要点）：指定一个向量来平移当前 SOLIDWORKS **图形区**；该向量**单位是米*"
            "*、相对图形区的 X,Y 轴；★ 「This vector has **no relation to the SOLIDWORKS triad axis** that is displayed"
            " in the graphics area」（与模型三轴无关）；本方法等价于用户界面上对图形区的 **panning**（平移）。★ 调用序"
            "证据（`docs/recon/member-to-example-index.md:3303` 登记 2 个例子 → `Set_Viewp"
        ),
        doc=(
            "Move the graphics area by a pan vector relative to the graphics-area axes rather than the model triad. It "
            "modifies the view only; both offsets are millimetres here and are converted once to the metres the referen"
            "ce expects."
        ),
    ),
    ToolSpec(
        name="solidworks_view_rotate_about_center",
        title="Rotate Model View About Center",
        module="sw_view",
        function="rotate_about_center",
        inject="view",
        param_alias={"x_angle_deg": "angle_x", "y_angle_deg": "angle_y"},
        params=[
            Param(
                "x_angle_deg",
                float,
                default=0.0,
                description=(
                    "Rotation about the screen X axis, treated as degrees; the reference states no unit. Defaults to 0."
                    "0."
                ),
            ),
            Param(
                "y_angle_deg",
                float,
                default=0.0,
                description=(
                    "Rotation about the screen Y axis, treated as degrees; the reference states no unit. Defaults to 0."
                    "0."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 RotateAboutCenter.md）：`**Signature**: `void RotateAboutCenter( System.double XAng"
            "le, System.double YAngle )``。★ **该官方页没有 `## Remarks` 段** —— 逐段核过：只有 front-matter（type/memb"
            "er/kind/assembly/namespace/category）、标题「Rotates the model view about the screen X and Y axes.」、`## "
            "Parameters`、`## Examples`、`## See Also` ⇒ 前置条件与语义**官方无文档**，故本行不编前置（铁律 5）。★ Para"
            "meters 逐字只有两条且**均未标单位**：「**XAngle**: Rotation about the X axi"
        ),
        doc=(
            "Rotate the model view about the screen X and Y axes. It modifies the view only; the reference documents no"
            " preconditions and states no unit for either angle, and this tool passes both through as degrees."
        ),
    ),
    ToolSpec(
        name="solidworks_view_roll_view",
        title="Roll the Model View About the Line of Sight (IModelView.RollBy)",
        module="sw_view",
        function="roll_view",
        inject="view",
        param_alias={"angle_deg": "angle"},
        params=[
            Param(
                "angle_deg",
                float,
                default=0.0,
                description=(
                    "Roll angle about the line of sight, treated as degrees; the reference states no unit and no range."
                    " Defaults to 0.0."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 RollBy.md）：`void RollBy( System.double Angle )`。★ 官方页**没有 `## Remarks` 段**"
            "（逐行读过，25 行只有 front-matter + 一句标题 + Signature + Parameters + Examples + See Also）⇒ 语义只能取"
            "标题句与参数表：① 标题逐字「Rolls the model view about the line of sight by the specified angle.」② 参数逐"
            "字「**Angle**: Angle by which to roll the model view about the line of sight」⇒ **未写单位、未写取值范围、"
            "未写是否立即生"
        ),
        doc=(
            "Rotate the model view about the line of sight, that is roll it, by an angle. It modifies the view only; th"
            "e reference states no unit and no range, and this tool treats the angle as degrees, matching the reference"
            " example that passes 90."
        ),
    ),
    ToolSpec(
        name="solidworks_view_get_camera",
        title="Get the Camera of the Model View (IModelView.Camera property)",
        module="sw_view",
        function="get_view_camera",
        inject="view",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 Camera.md）：`Camera Camera {get; set;}`。★ 官方页逐字要点：① 标题句「Gets or sets "
            "the camera.」② `## Returns` = `[[Camera]]`（⇒ 返回 COM 对象 `ICamera`，**不是**标量）；③ `## Remarks` **唯"
            "一一段**逐字：「If the return value is Nothing or NULL, then the camera view for this model is turned off."
            "」⇒ ★★ **判空是官方写明的语义**，也是本函数唯一可靠的回读判据（`collect_view_evidence` 里 `has_camera = ge"
            "t_"
        ),
        doc=(
            "Read the camera of the model view. Read-only; it returns the camera object, and a null result means the ca"
            "mera view for this model is turned off."
        ),
    ),
    ToolSpec(
        name="solidworks_view_set_camera_by_name",
        title="按相机特征名切换三维模型视图 · IModelView.SetCameraByName",
        module="sw_view",
        function="set_view_camera_by_name",
        inject="view",
        params=[
            Param(
                "name",
                str,
                default="",
                description=(
                    "Feature name of the camera that should set the view; cameras are features, so their names come fro"
                    "m the document's camera list. Defaults to empty."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 SetCameraByName.md）：`System.bool SetCameraByName( System.string Name )`。官方页 `"
            "IModelView.SetCameraByName`（kind: method，category: User-interface Interfaces）：摘要逐字 'Sets the model"
            " view to that of the specified camera, if in camera view mode.'；Returns 逐字 'True if the camera is set, "
            "false if not'。`## Remarks` 是一张两行表，逐字：「A nonexistent camera when another camera view is active "
        ),
        doc=(
            "Set the model view to a named camera while the model is in camera view mode. It modifies the view only; th"
            "e name is a camera feature name, and the call reports false when that camera does not exist."
        ),
    ),
    ToolSpec(
        name="solidworks_view_has_perspective",
        title="View Has Perspective (IModelView.HasPerspective)",
        module="sw_view",
        function="has_perspective",
        inject="view",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 HasPerspective.md）：``System.bool HasPerspective()``。★ 官方页**没有 `## Remarks` "
            "段** ⇒ 不编（铁律 5）。页内逐字可摘的只有两处：摘要「Determines if the model view currently has perspectiv"
            "e.」与 `## Returns`「True if the view currently has perspective viewing turned on, false otherwise」⇒ **零"
            "参**、返回布尔。`kind: method` / `category: User-interface Interfaces`（front-matter 逐字）。"
        ),
        doc=(
            "Report whether the model view currently has perspective turned on. Read-only, takes no arguments, and retu"
            "rns true only while perspective viewing is enabled."
        ),
    ),
    ToolSpec(
        name="solidworks_view_add_perspective",
        title="View Add Perspective (IModelView.AddPerspective)",
        module="sw_view",
        function="add_perspective",
        inject="view",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 AddPerspective.md）：``void AddPerspective()``。★ 官方页**没有 `## Remarks` 段、也"
            "没有 `## Returns` 段** ⇒ 不编（铁律 5）。页内逐字可摘的只有摘要「Adds perspective to the model view.」⇒ **"
            "零参、无返回值（void）**。`kind: method` / `category: User-interface Interfaces`（front-matter 逐字）。★ "
            "同族的 `RemovePerspective.md` 也在同目录存在（反向操作），本批未取。"
        ),
        doc=(
            "Add perspective to the model view. It modifies the view only; it takes no arguments, returns nothing, and "
            "the reference documents no precondition for turning perspective on."
        ),
    ),
    ToolSpec(
        name="solidworks_view_remove_perspective",
        title="View Remove Perspective",
        module="sw_view",
        function="remove_perspective",
        inject="view",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 RemovePerspective.md）：`void RemovePerspective()`。★ 该页**没有 `## Remarks` 段**"
            "、也没有 `## Parameters` / `## Returns` 段（全文 = front matter + 标题 + 正文一句 + `## See Also`）⇒ **前"
            "置查不到**（铁律 5，不编）。正文逐字一句：`Removes perspective from the model view.`（**动词 Remove，无返"
            "回值语义**）。`## See Also` 列 `IModelView::AddPerspective Method` / `HasPerspective Method` / `GetEyePoin"
            "t` / `S"
        ),
        doc=(
            "Remove perspective from the model view. It modifies the view only; it takes no arguments, returns nothing,"
            " and the reference documents no precondition for turning perspective off."
        ),
    ),
    ToolSpec(
        name="solidworks_view_start_dynamics",
        title="View Start Dynamics",
        module="sw_view",
        function="start_dynamics",
        inject="view",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 StartDynamics.md）：`void StartDynamics()`。摘要逐字：`Provides faster rotation of "
            "model views.`；签名 `void StartDynamics()`（**零参、无返回值语义**）。`## Remarks` 三条，逐字要点：① 「Aft"
            "er setting swUserPreferenceIntegerValue_e.swLevelOfDetail high enough, this method can be used at the begi"
            "nning of dynamic model view changes to: change HLR or HLV mode to wireframe mo"
        ),
        doc=(
            "Start fast dynamic view changes so that following rotations redraw faster. It modifies how the view redraw"
            "s only; use it at the beginning of dynamic view changes and pair it with the stop-dynamics call, which res"
            "tores the previous display mode."
        ),
    ),
    ToolSpec(
        name="solidworks_view_stop_dynamics",
        title="View Stop Dynamics (IModelView.StopDynamics)",
        module="sw_view",
        function="stop_dynamics",
        inject="view",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 StopDynamics.md）：``void StopDynamics()``。★ 官方页**有 `## Remarks` 段**，逐字："
            "「Use this method with [[IModelView::StartDynamics]] at the end of dynamic view motion. This method return"
            "s the view to its previous HLR, HLV, or shaded mode and recalculates the display.」「After calling this me"
            "thod, you must call [[IModelDoc2::GraphicsRedraw2]] or [[IMod"
        ),
        doc=(
            "Stop dynamic view changes and restore the previous display mode. It modifies the view only; call it at the"
            " end of dynamic motion to return to the earlier display mode, then redraw the graphics area so the display"
            " is recalculated."
        ),
    ),
    ToolSpec(
        name="solidworks_view_get_next",
        title="View Get Next Model View (IModelView.GetNext)",
        module="sw_view",
        function="get_next_view",
        inject="view",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 GetNext.md）：``System.object GetNext()``。★ 官方页**有 `## Returns` 与 `## Remarks"
            "` 两段**，逐字：`## Returns`「Next [[model view]] or Nothing or null if no more model views exist」；`## R"
            "emarks`「You can traverse through the model views in a document by using this method. When this method ret"
            "urns Nothing or null, you have reached the end of the list.」「Se"
        ),
        doc=(
            "Get the next model view in the document, or nothing when the list of views ends. Read-only; walk the views"
            " by calling it repeatedly, and a null result means you have reached the end of the list."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_get_buckling_load_factors",
        title="Get Buckling Load Factors",
        module="sw_simulation_results",
        function="get_buckling_load_factors",
        inject="results",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_simulation_results.py）：`查不到（官方页不存在 —— `C:\\swapi\\types\\` 无 `ICWRe"
            "sults` 目录；CHM 的 `SWhelp\\cosworks\\` 只覆盖 `ICWLoadsAndRestraintsManager` 一族，没有 `ICWResults~GetB"
            "ucklingLoadFactors`）。`。查不到 —— 没有官方页可摘 Remarks。`docs\\recon\\member-inventory.md:696` 对该成"
            "员三列均记「查不到（该源无此字段）」。本仓来源块（sw_simulation_results.py:194-207）逐字记载的反射签名是 `"
            "Object GetBucklingLoadFactors(Int32&)`（**零**实参 + 1 by-ref）。"
        ),
        doc=(
            "Get the buckling load factors of a solved buckling study. Read-only; it passes through what the results ob"
            "ject returns, no reference page documents the exact result form, and the factor count comes back through a"
            "n output argument rather than the return value."
        ),
    ),
    ToolSpec(
        name="solidworks_get_view_model_doc",
        title="Get the Document That Owns a 3D Model View",
        module="sw_view",
        function="get_view_model_doc",
        inject="view",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_view.py）：`查不到 —— C:\\swapi\\types\\IModelView\\GetModelDoc.md 不存在（IMode"
            "lView 目录下 79 个成员文件里没有 GetModelDoc.md；全 swapi 里带 GetModelDoc 的 .md 只有 IComponent2 / IDeri"
            "vedPartFeatureData / IMirrorPartFeatureData 三个**别的接口**）`。★ 真源是**本仓** `scripts/sw_view.py` 的 "
            "`get_view_model_doc`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到（无官方 .md 页 ⇒ 无 ## Remarks "
            "可摘；反射只给签名与返回类型，���给语义）"
        ),
        doc=(
            "Get the document that owns the model view. Read-only; it takes no arguments and returns the document objec"
            "t behind the view rather than a name or a path."
        ),
    ),
    ToolSpec(
        name="solidworks_collect_view_evidence",
        title="Read Back the 3D Model View State",
        module="sw_view",
        function="collect_view_evidence",
        inject="view",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_view.py）：`查不到 —— 「collect_view_evidence」本身**不是官方成员**（官方 IModel"
            "View 没有同名成员，IModelView 目录 79 个 .md 里也没有）⇒ 本仓自研的**聚合回读**，无单一官方签名可抄。它内"
            "部只读 14 个官方成员，逐字签名见 evidence.constituent_signatures。`。★ 真源是**本仓** `scripts/sw_view.py`"
            " 的 `collect_view_evidence`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到（无单一官方成员可摘 Remar"
            "ks）；来源块 scripts/sw_view.py:458-462 逐字：「沿用『只取已核实成员』的写法」+「⚠ 本组为照官方签名新写，"
            "未在本机实测（见 AGENTS.md 铁律 2）」"
        ),
        doc=(
            "Read the state of the model view as one evidence record. Read-only; the record holds the window frame, dis"
            "play mode, HLR quality, scale, perspective flag, graphics-update and zebra-stripe flags, xor highlight, an"
            "d whether a camera and an orientation are present."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_get_worst_jacobian_ratio",
        title="Read the Worst Jacobian Ratio of the Study Mesh",
        module="sw_simulation_results",
        function="get_worst_jacobian_ratio",
        inject="mesh",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_simulation_results.py）：`查不到（官方页不存在）—— ★ `C:\\swapi\\types\\` 下**没"
            "有 `ICWMesh\\` 目录**；对整个 `C:\\swapi` 递归 grep `ICWMesh|GetWorstJacobianRatio|IsComponentFailed` **0 "
            "命中**；`C:\\swapi\\types\\` 里唯一的 Mesh 族是 `IMeshBody`（**另一个族**，见 `Get_Mes`。★ **没有 `## Rema"
            "rks`** —— 因为根本没有官方页可抄（该模块 docstring 逐字：「⚠ **这两个接口族官方 CHM 没有文档页**（cosworks"
            " 册只覆盖 `ICWLoadsAndRestraintsManager` 一个族），因此**没有参数语义说明**」）。⇒ 前置、单位、取值区间**"
            "一律查不到**，本工具**不编**（铁律 5）。可用的事实只有反射签名本身：`Double` 返回 ⇒ 无量纲比值（雅可比畸变"
            "指标），**零参** ⇒ 不需要任何输入。本仓包装 `scripts/sw_simulation_results.py:249` 逐字 `return "
        ),
        doc=(
            "Get the worst jacobian ratio of the mesh as a mesh-distortion reading. Read-only; it takes no arguments an"
            "d returns a plain ratio, and no reference page documents a valid range for it."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_is_component_failed",
        title="Check Whether a Simulation Component Failed Meshing",
        module="sw_simulation_results",
        function="is_component_failed",
        inject="mesh",
        params=[
            Param(
                "component_name",
                str,
                default="",
                description=(
                    "Name of the component to check; the reference documents this parameter only as a string, with no f"
                    "ormat. Defaults to empty."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_simulation_results.py）：`查不到（官方页不存在）—— ★ `C:\\swapi\\types\\` 下**没"
            "有 `ICWMesh\\` 目录**；对整个 `C:\\swapi` 递归 grep `ICWMesh|GetWorstJacobianRatio|IsComponentFailed` **0 "
            "命中**（`types\\` 里唯一的 Mesh 族是 `IMeshBody`，另一个族）。⇒ 签名只能取自本仓反射转储 `_raw\\r`。★ **没"
            "有 `## Remarks`** —— 因为根本没有官方页可抄（同模块 docstring 逐字：ICWResults / ICWMesh 两族「官方 CHM 没"
            "有文档页」）。⇒ 前置、单位、字符串的取值格式**一律查不到**，本工具**不编**（铁律 5）。可用事实只有反射签名"
            "本身：`Boolean` 返回 ⇒ 判据是布尔；**1 个 `String` 入参**，无 by-ref 出参。本仓包装 `scripts/sw_simulation"
            "_results.py:254` 逐字 `return bool(_checked(MESH_ARITY, mesh, 'IsComponent"
        ),
        doc=(
            "Report whether one component of the mesh failed meshing. Read-only; it passes the component name to the bo"
            "olean member and returns that verdict, and no reference page documents what form the name must take."
        ),
    ),
]
