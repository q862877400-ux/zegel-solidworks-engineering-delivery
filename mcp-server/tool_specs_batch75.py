"""★ 覆盖面缺口批（第三批）：把工程图**已实现却没挂**的 8 项接成工具（不重写实现）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层）· 规格 `specs/202-user-coverage-gaps` 的 **R1**。
# 文件:   mcp-server/tool_specs_batch75.py
# 定位:   ★★ **本批与 batch72/73 的性质都不同**（★ 三批要分清）：
# · batch72：接的是「AST 量出**已有实现**」的几条（`tools/audit_gap_implementations.py`
# ）；
#     · batch73：接的是「**本仓一个都没有**」的工程图真缺口（先写了能力层）；
#     · ★ **本批**：接的是「**早就实现了、却只挂出了 4 项**」的 8 项
#       —— ★ 依据 `specs/202-user-coverage-gaps/recon/drawing-existing-coverage.md`：
# **工程图 13 项里本仓已实现 8 项、而挂成工具的只有 4 项（且全靠同一个 `solidworks_drawi
# ng`）**。
#       ⇒ ★★ **本批一行实现逻辑都不新写**（"缝合优先不发明"）⇒ 只做**转接 + 单位边界**。
#   ★ 转接层 = `scripts/sw_drawing_expose.py`（★ 与 `scripts/sw_drawing.py` 的差别：
#     后者是"按路径加载 subskill 再导出"的**兼容桥**，前者是**对外包装**：
#     收**毫米**、只在边界换算一次、并把**前置回读**带回来）。
#
# ==================================  =================================  ===============
# ==========
# 缺口项                              工具名                              覆盖率的计数关
# 键词（逐字）
# ==================================  =================================  ===============
# ==========
# 投影视图                            solidworks_drawing_create_projected_view       pro
# jected_view
# 剖面视图                            solidworks_drawing_create_section_view         sec
# tion_view
# 局部视图                            solidworks_drawing_create_detail_view          det
# ail_view
# 图纸格式/模板                       solidworks_drawing_set_sheet_format            she
# et_format
# 注释/文字                           solidworks_drawing_add_note                    add
# _note
# 孔表                                solidworks_drawing_create_hole_table           hol
# e_table
# 修订表                              solidworks_drawing_create_revision_table       rev
# ision_table
# 中心符号线                          solidworks_drawing_insert_center_marks         cen
# ter_mark
# ==================================  =================================  ===============
# ==========
#   ★ 那些关键词逐字取自 `D:\SW-coverage-tool\gen_user_feature_coverage.py:130-148`
#     ⇒ ★ **工具名必须含它们才会计数**（★ 而名字本身也要**准确** —— 计划里写明：
#        **不许**把"改个名字让计数涨上去"当成"能力补上了"）。
#
#   ★★ 注入名：这 8 个包装函数的**首参都是 `drawing_model`** ⇒ `inject="drawing_model"`
#     （★ 该键已在 `register_capabilities.RESOLVERS` 里 —— 见 known-facts 491）。
# ★★ 单位：对外收**毫米**（`x_mm`/`y_mm`），★ **换算只发生在 `scripts/sw_drawing_expose.
# py` 一处**。
#
#   官方依据（★ 逐页读过；契约抄本在 `specs/202-user-coverage-gaps/recon/api/`）:
# · `IDrawingDoc.CreateDrawViewFromModelView3`（投影）· `IDrawingDoc.CreateSectionViewAt
# 5`（剖面）
# · `IDrawingDoc.CreateDetailViewAt4`（局部，**12 参**）· `IDrawingDoc.SetupSheet6`（图
# 纸格式）
# · `IModelDoc2.InsertNote`（注释）· `IView.InsertHoleTable3` / `ISheet.InsertRevisionTa
# ble2`（表）
#     · `IDrawingDoc.InsertCenterMark3` / `IView.AutoInsertCenterMarks2`（中心符号线）
#   许可:   本仓库 MIT。★ **无第三方代码引入**。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from tool_registry import Param, ToolSpec

_EXPOSE = "sw_drawing_expose"

_BATCH75: list[ToolSpec] = [
    ToolSpec(
        name="solidworks_drawing_create_projected_view",
        title="Drawing Projected / Model View",
        module=_EXPOSE, function="create_projected_view",
        inject="drawing_model",
        params=[
            Param("part_path", str, description="★ **已存盘模型**的完整路径，且**含 `.sldprt`/`.sldasm`**"
                                                "（官方 Remarks 逐字要求）。"),
            Param("view_name", str, description="视图方向名，★ **传英文名即可**（如 `*Front`/`*Top`/`*Isometric`）"
                                                "—— ★ 底层会**自动改用本机本地化名**（`*前视` 等，事实 494）。"),
            Param("x_mm", float, description="视图中心 X（**毫米**，默认 140）。"),
            Param("y_mm", float, description="视图中心 Y（**毫米**，默认 120）。"),
            Param("scale", float, description="视图比例（`1/scale`）；★ `0` = 不设、用图纸默认。"),
        ],
        doc="★ **投影/模型视图**：`CreateDrawViewFromModelView3`（经 `add_view`）。"
            "★★ **真机证据**：本工具**经工具层**实测返回真实视图对象（`CDispatch`）、"
            "★ 且**正是靠本地化名回退**建成（`*Front` 失败 → `*前视` 成功；known-facts 494）。"
            "⚠ **另一条与本工具无关的**（★ 2026-10-04 接手轮更正）："
            "`create_standard_views_with_projection`（三视图布局那条路）此前在本机返回 "
            "`blocked / DRAWING_PROJECTION_API_UNAVAILABLE`，而**真因不是「本机 COM 代理没有那个成员」**"
            "—— 是**成员名拼错**：代码写 `CreateFirstAngleViews2`，官方真名 **`Create1stAngleViews2`**"
            "（`1st` 非 `First`）⇒ ★ 已在 `drawing_workflow.py` 修正。该限制**未**挂成工具。",
    ),
    ToolSpec(
        name="solidworks_drawing_create_section_view",
        title="Drawing Section View",
        module=_EXPOSE, function="create_section_view",
        inject="drawing_model",
        params=[
            Param("x_mm", float, description="剖视图放置位置 X（**毫米**）。"),
            Param("y_mm", float, description="剖视图放置位置 Y（**毫米**）。"),
        ],
        doc="★ **剖面视图**：`CreateSectionViewAt5`。"
            "★★ **前置（官方 Remarks 逐字）：调用前必须先选好剖面线** ⇒ 本工具**不代选**，"
            "先回读选区计数并在返回值里给 `preconditions_held`。"
            "⚠ 真机该格**前置未成立**（选区为空）⇒ ★ **不能**据此判「剖面视图不成」（事实 496）。",
    ),
    ToolSpec(
        name="solidworks_drawing_create_detail_view",
        title="Drawing Detail View",
        module=_EXPOSE, function="create_detail_view",
        inject="drawing_model",
        params=[
            Param("x_mm", float, description="局部视图放置位置 X（**毫米**）。"),
            Param("y_mm", float, description="局部视图放置位置 Y（**毫米**）。"),
            Param("scale", float, description="比例**分子**（分母固定 1.0）⇒ `2.0` 表示 **2:1**。"),
            Param("label", str, description="标签文字（留空用 SolidWorks 默认）。"),
            Param("shape_intensity", int, description="锯齿轮廓强度 1(最强)–5(最弱)；"
                                                      "★ 仅当 `jagged_outline=True` 且 `no_outline=False` 时有效。"),
        ],
        doc="★ **局部视图**：`CreateDetailViewAt4`（官方 **12 参**）。"
            "★ 真机证据：视图数 **1→2**、返回非 None（证据 JSON 的 V3 格）。"
            "★ 前置：图上要有**局部圆（草图圆）**（官方例子的调用序：`ActivateView` → `CreateCircle` → 才调）。",
    ),
    ToolSpec(
        name="solidworks_drawing_set_sheet_format",
        title="Drawing Sheet Format / Template",
        module=_EXPOSE, function="set_sheet_format",
        inject="drawing_model",
        params=[
            Param("format_path", str, description="图纸格式文件路径（`.slddrt`）。"),
        ],
        doc="★ **图纸格式/模板**：**`ISheet.SetTemplateName(String NameIn)`**（官方 **`void`、未废弃**）。"
            "★★ **为什么不是 `SetupSheet6`**（★ 本 doc 原先写的是它，2026-10-03 更正）："
            "`ISheet.SetTemplateName` 才是**换图框**的成员；`SetupSheet6` 是用来**新建/重置图纸**的"
            "（17 参）—— ★ 两者不是一件事。"
            "★★★ **而真机踩过一个坑**：能力层原先是 `sheet = GetCurrentSheet(); sheet.SetTemplateName(p)`"
            "（**直接属性访问**）⇒ 经工具层报 **`com_error: 找不到成员`**；"
            "★ 定点诊断（`output/_diag_sheetfmt.json`）证明**同一个成员、同一个对象**用 `get_com_member` "
            "就成功（返回 `None` = `void` 成功）⇒ ★ 是**通道**问题、不是名字问题（known-facts 499）。"
            "★ 官方 Remarks 逐字：调完要 `ForceRebuild3` 才刷新第一角/第三角投影（★ 现已在能力层里补上）。"
            "★ 判据：`SetTemplateName` 回 `None` **且** `GetTemplateName` 回读等于新路径。",
    ),
    ToolSpec(
        name="solidworks_drawing_add_note",
        title="Drawing Note / Annotation",
        module=_EXPOSE, function="add_drawing_note",
        inject="drawing_model",
        params=[
            Param("x_mm", float, description="注释位置 X（**毫米**）。"),
            Param("y_mm", float, description="注释位置 Y（**毫米**）。"),
            Param("text", str, description="注释文字。★ 用符号时要写成 `<*库名-符号名*>`（官方 Remarks 逐字）。"),
        ],
        doc="★ **注释/文字**：`InsertNote`。"
            "★ 真机证据：两格（选中 / 不选）都返回非 None，判据是注解读数增量（证据 JSON 的 A4 格）。"
            "★ 官方 Remarks 逐字：**引线附着点来自调用前做的选择**；**没有选中时**无引线、自由放置、在原点。",
    ),
    ToolSpec(
        name="solidworks_drawing_create_hole_table",
        title="Drawing Hole Table",
        module=_EXPOSE, function="create_hole_table",
        inject="drawing_model",
        params=[
            Param("view_name", str, description="承载孔表的视图名（★ 孔表挂在 **`IView`** 上）。"),
            Param("x_mm", float, description="表放置位置 X（**毫米**；官方该参数单位是**米**，边界换算一次）。"),
            Param("y_mm", float, description="表放置位置 Y（**毫米**）。"),
            Param("anchor_type", int, description="★ 锚点类型，取值见 **`swBOMConfigurationAnchorType_e`**"
                                                 "（官方 Parameters 逐字）。"),
            Param("start_value", str, description="起始编号（官方例子用 `A`）。"),
            Param("template", str, description="孔表模板（`.sldholtbt`；官方 Remarks：在 `install_dir\\lang\\<language>`）。"),
            Param("tag_order", int, description="标签顺序（官方 8 参，例子用 1）。"),
            Param("tag_type", int, description="标签类型（官方 9 参，例子用 1）。"),
        ],
        doc="★ **孔表**：**`IView.InsertHoleTable3`（9 参、未废弃）**。"
            "★★ **本工具改过实现**（2026-10-03 真机 e2e 实测的教训）：原先把 `InsertTableAnnotation` 当孔表入口 —— "
            "★ 而官方签名逐字是 `InsertTableAnnotation(X, Y, AnchorType, Rows, Columns)`，"
            "**它没有任何参数说\"这是孔表\"** ⇒ ★ **它建的是通用表，建不出孔表**（e2e 实测：注解数 72→72）。"
            "★★★ **前置（官方 Remarks 的 mark 表，逐字）**：基准原点**顶点 mark 1** · 孔**边与面 mark 2** · "
            "X 向参考 mark 4 · Y 向参考 mark 8 ⇒ ★ 本工具**不代选**，先回读选区里 mark 1/2 各几个，"
            "`preconditions_held` 如实给出（★ 前置不成立时**不能**判「孔表不成」）。"
            "★ 真机证据：`output/drawing-batch-evidence.json` 的 A6 格（`GetTableAnnotationCount` 增量、前置成立）。",
    ),
    ToolSpec(
        name="solidworks_drawing_create_revision_table",
        title="Drawing Revision Table",
        module=_EXPOSE, function="create_revision_table",
        inject="drawing_model",
        params=[
            Param("x_mm", float, description="表放置位置 X（**毫米**）。"),
            Param("y_mm", float, description="表放置位置 Y（**毫米**）。"),
            Param("anchor_type", int, description="★ 锚点类型，取值见 **`swBOMConfigurationAnchorType_e`**。"),
            Param("template", str, description="模板路径（`.sldrevtbt`）；★ 官方 Remarks：模板与表**必须同型**。"),
            Param("shape", int, description="表形状（官方 6 参）。"),
            Param("auto_update_zoom_cells", bool, description="是否自动更新缩放单元格（官方 7 参）。"),
        ],
        doc="★ **修订表**：**`ISheet.InsertRevisionTable2`（7 参、未废弃）**。"
            "★★ 同孔表：`InsertTableAnnotation` **建不出修订表**（它没有\"表类型\"参数）⇒ 走**真入口**。"
            "★★ 官方 Returns 逐字：**已有修订表时回 `null`** ⇒ ★ **第二次调用「回 null」是契约、不是失败**"
            "（★ 返回值里有 `raw_is_none` 供按契约解释）。"
            "★ 真机证据：`output/drawing-batch-evidence.json` 的 A7 格（两格都返回非 None）。 ★ 别名: pdm, pdm_operations, revision, vault",
    ),
    ToolSpec(
        name="solidworks_drawing_insert_center_marks",
        title="Drawing Center Marks (auto, per view)",
        module=_EXPOSE, function="insert_center_marks",
        inject="drawing_model",
        params=[
            Param("requirements", list, description="要插中心标记的视图/要求列表（**原样透传**给能力层）。"),
        ],
        doc="★ **中心符号线**（批量）：`AutoInsertCenterMarks2`。"
            "⚠⚠ **真机阴性已知**：单点入口 `InsertCenterMark3` 两格都**不成**，"
            "且其中**一格前置是成立的**（证据 JSON 的 A8 格）⇒ ★ 本工具走的是**批量**那条路，"
            "★ **尚未单独真机验证** ⇒ ★ 如实标注，**不许**当成「已验证」。",
    ),
]

#: ★ 注册器按 `SPECS_*` 找本批（`register_capabilities.BATCH_MODULES` 里也要加一行）。
SPECS_BATCH75 = _BATCH75
