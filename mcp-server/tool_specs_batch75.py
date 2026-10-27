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
        module=_EXPOSE,
        function="create_projected_view",
        inject="drawing_model",
        params=[
            Param(
                "part_path",
                str,
                description="Full path of an already saved model file ending in .sldprt or .sldasm.",
            ),
            Param(
                "view_name",
                str,
                description=(
                    "View orientation such as *Front, *Top or *Isometric; English names are resolved to the local names"
                    ". Defaults to *Front."
                ),
            ),
            Param("x_mm", float, description="X of the view centre in millimetres. Defaults to 140."),
            Param("y_mm", float, description="Y of the view centre in millimetres. Defaults to 120."),
            Param(
                "scale",
                float,
                description="View scale written as 1/scale, where 0 leaves the sheet default. Defaults to 0.",
            ),
        ],
        evidence=(
            "★ **投影/模型视图**：`CreateDrawViewFromModelView3`（经 `add_view`）。★★ **真机证据**：本工具**经工具层**"
            "实测返回真实视图对象（`CDispatch`）、★ 且**正是靠本地化名回退**建成（`*Front` 失败 → `*前视` 成功；known-f"
            "acts 494）。⚠ **另一条与本工具无关的**（★ 2026-10-04 接手轮更正）：`create_standard_views_with_projection`"
            "（三视图布局那条路）此前在本机返回 `blocked / DRAWING_PROJECTION_API_UNAVAILABLE`，而**真因不是「本机 COM "
            "代理没有那个成员」**—— 是**成员名拼错**：代码写 `CreateFirstAngleViews2`，官方真名 **`Create1stAngleViews2"
            "`**（`1st` 非 `First`）⇒ ★ 已在 `drawing_workflow.py` 修正。该限制**未**挂成工具。"
        ),
        doc=(
            "Insert a projected or model view of a saved part into the active drawing. It writes a view and does not sa"
            "ve the document; the model must already be saved with a path ending in .sldprt or .sldasm, and English vie"
            "w names such as *Front are resolved to this machine's localized name."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_create_section_view",
        title="Drawing Section View",
        module=_EXPOSE,
        function="create_section_view",
        inject="drawing_model",
        params=[
            Param("x_mm", float, description="X where the section view is placed, in millimetres."),
            Param("y_mm", float, description="Y where the section view is placed, in millimetres."),
        ],
        evidence=(
            "★ **剖面视图**：`CreateSectionViewAt5`。★★ **前置（官方 Remarks 逐字）：调用前必须先选好剖面线** ⇒ 本工具*"
            "*不代选**，先回读选区计数并在返回值里给 `preconditions_held`。⚠ 真机该格**前置未成立**（选区为空）⇒ ★ **不"
            "能**据此判「剖面视图不成」（事实 496）。"
        ),
        doc=(
            "Insert a section view at the given position on the active drawing. It writes a view and does not save the "
            "document; a section line must already be selected because this tool selects nothing, and it reports precon"
            "ditions_held so an empty selection is not read as a failure of the call."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_create_detail_view",
        title="Drawing Detail View",
        module=_EXPOSE,
        function="create_detail_view",
        inject="drawing_model",
        params=[
            Param("x_mm", float, description="X where the detail view is placed, in millimetres."),
            Param("y_mm", float, description="Y where the detail view is placed, in millimetres."),
            Param(
                "scale",
                float,
                description="Numerator of the detail view scale with the denominator fixed at 1, so 2.0 means 2:1.",
            ),
            Param("label", str, description="Label text for the detail view; empty uses the SolidWorks default."),
            Param(
                "shape_intensity",
                int,
                description="Sawtooth outline intensity from 1 (strongest) to 5 (weakest).",
            ),
        ],
        evidence=(
            "★ **局部视图**：`CreateDetailViewAt4`（官方 **12 参**）。★ 真机证据：视图数 **1→2**、返回非 None（证据 JSO"
            "N 的 V3 格）。★ 前置：图上要有**局部圆（草图圆）**（官方例子的调用序：`ActivateView` → `CreateCircle` → 才"
            "调）。"
        ),
        doc=(
            "Insert a detail view at the given position on the active drawing. It writes a view and does not save the d"
            "ocument; the drawing needs a detail circle, a sketch circle, in the source view first, and scale is the nu"
            "merator with the denominator fixed at 1."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_set_sheet_format",
        title="Drawing Sheet Format / Template",
        module=_EXPOSE,
        function="set_sheet_format",
        inject="drawing_model",
        params=[
            Param("format_path", str, description="Path of the sheet format file ending in .slddrt."),
        ],
        evidence=(
            "★ **图纸格式/模板**：**`ISheet.SetTemplateName(String NameIn)`**（官方 **`void`、未废弃**）。★★ **为什么不"
            "是 `SetupSheet6`**（★ 本 doc 原先写的是它，2026-10-03 更正）：`ISheet.SetTemplateName` 才是**换图框**的成"
            "员；`SetupSheet6` 是用来**新建/重置图纸**的（17 参）—— ★ 两者不是一件事。★★★ **而真机踩过一个坑**：能力层"
            "原先是 `sheet = GetCurrentSheet(); sheet.SetTemplateName(p)`（**直接属性访问**）⇒ 经工具层报 **`com_error:"
            " 找不到成员`**；★ 定点诊断（`output/_diag_sheetfmt.json`）证明**同一个成员、同一个对象**用 `get_com_member"
            "` 就成功（返回 `None` = `void` 成功）⇒ ★ 是**通道**问题、不是名字问题（known-facts 499）。★ 官方 Remarks "
            "逐字：调完要 `ForceRebuild3` 才刷新第一角/第三角投影（★ 现已在能力层里补上）。★ 判据：`SetTemplateName` 回"
            " `None` **且** `GetTemplateName` 回读等于新路径。"
        ),
        doc=(
            "Set the sheet format, that is the drawing frame, of the active drawing from a format file. It writes the n"
            "ew format and does not save the document; it rebuilds afterwards so the first-angle or third-angle project"
            "ion refreshes, and success is the read-back path matching the requested one."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_add_note",
        title="Drawing Note / Annotation",
        module=_EXPOSE,
        function="add_drawing_note",
        inject="drawing_model",
        params=[
            Param("x_mm", float, description="X where the note is placed, in millimetres."),
            Param("y_mm", float, description="Y where the note is placed, in millimetres."),
            Param(
                "text",
                str,
                description="Note text; symbols must be written in the <*library-symbol*> form.",
            ),
        ],
        evidence=(
            "★ **注释/文字**：`InsertNote`。★ 真机证据：两格（选中 / 不选）都返回非 None，判据是注解读数增量（证据 JSON"
            " 的 A4 格）。★ 官方 Remarks 逐字：**引线附着点来自调用前做的选择**；**没有选中时**无引线、自由放置、在原点"
            "。"
        ),
        doc=(
            "Insert a text note at the given position on the active drawing. It writes a note and does not save the doc"
            "ument; the leader attachment point comes from whatever is selected before the call, and with nothing selec"
            "ted the note is free-standing at the origin."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_create_hole_table",
        title="Drawing Hole Table",
        module=_EXPOSE,
        function="create_hole_table",
        inject="drawing_model",
        params=[
            Param(
                "view_name",
                str,
                description="Name of the drawing view that carries the hole table.",
            ),
            Param(
                "x_mm",
                float,
                description=(
                    "X where the table is placed, in millimetres; the API takes metres, so it is converted here."
                ),
            ),
            Param("y_mm", float, description="Y where the table is placed, in millimetres."),
            Param(
                "anchor_type",
                int,
                description="Anchor type, one of the swBOMConfigurationAnchorType_e values.",
            ),
            Param("start_value", str, description="First item number in the table, for example A."),
            Param(
                "template",
                str,
                description=(
                    "Hole table template file ending in .sldholtbt, found under the language folder of the install dire"
                    "ctory."
                ),
            ),
            Param("tag_order", int, description="Tag order value; the official example uses 1."),
            Param("tag_type", int, description="Tag type value; the official example uses 1."),
        ],
        evidence=(
            "★ **孔表**：**`IView.InsertHoleTable3`（9 参、未废弃）**。★★ **本工具改过实现**（2026-10-03 真机 e2e 实测"
            "的教训）：原先把 `InsertTableAnnotation` 当孔表入口 —— ★ 而官方签名逐字是 `InsertTableAnnotation(X, Y, Anc"
            "horType, Rows, Columns)`，**它没有任何参数说\"这是孔表\"** ⇒ ★ **它建的是通用表，建不出孔表**（e2e 实测："
            "注解数 72→72）。★★★ **前置（官方 Remarks 的 mark 表，逐字）**：基准原点**顶点 mark 1** · 孔**边与面 mark 2"
            "** · X 向参考 mark 4 · Y 向参考 mark 8 ⇒ ★ 本工具**不代选**，先回读选区里 mark 1/2 各几个，`preconditions_"
            "held` 如实给出（★ 前置不成立时**不能**判「孔表不成」）。★ 真机证据：`output/drawing-batch-evidence.json` "
            "的 A6 格（`GetTableAnnotationCount` 增量、前置成立）。"
        ),
        doc=(
            "Insert a hole table on a drawing view. It writes a table and does not save the document; the base-origin v"
            "ertex must be selected with mark 1 and the hole edges or faces with mark 2 first, because this tool select"
            "s nothing, and it reports preconditions_held."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_create_revision_table",
        title="Drawing Revision Table",
        module=_EXPOSE,
        function="create_revision_table",
        inject="drawing_model",
        params=[
            Param("x_mm", float, description="X where the table is placed, in millimetres."),
            Param("y_mm", float, description="Y where the table is placed, in millimetres."),
            Param(
                "anchor_type",
                int,
                description="Anchor type, one of the swBOMConfigurationAnchorType_e values.",
            ),
            Param(
                "template",
                str,
                description=(
                    "Revision table template path ending in .sldrevtbt; the template and the table must be the same typ"
                    "e."
                ),
            ),
            Param("shape", int, description="Table shape value."),
            Param(
                "auto_update_zoom_cells",
                bool,
                description="Whether to update the zoom cells automatically.",
            ),
        ],
        evidence=(
            "★ **修订表**：**`ISheet.InsertRevisionTable2`（7 参、未废弃）**。★★ 同孔表：`InsertTableAnnotation` **建不"
            "出修订表**（它没有\"表类型\"参数）⇒ 走**真入口**。★★ 官方 Returns 逐字：**已有修订表时回 `null`** ⇒ ★ **第"
            "二次调用「回 null」是契约、不是失败**（★ 返回值里有 `raw_is_none` 供按契约解释）。★ 真机证据：`output/draw"
            "ing-batch-evidence.json` 的 A7 格（两格都返回非 None）。 ★ 别名: pdm, pdm_operations, revision, vault"
        ),
        doc=(
            "Insert a revision table on the active drawing sheet. It writes a table and does not save the document; the"
            " template and the table must be the same type, and a null return means a revision table already exists, wh"
            "ich is the documented result rather than a failure."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_insert_center_marks",
        title="Drawing Center Marks (auto, per view)",
        module=_EXPOSE,
        function="insert_center_marks",
        inject="drawing_model",
        params=[
            Param(
                "requirements",
                list,
                description="List of views or centre-mark requirements, passed unchanged to the capability layer.",
            ),
        ],
        evidence=(
            "★ **中心符号线**（批量）：`AutoInsertCenterMarks2`。⚠⚠ **真机阴性已知**：单点入口 `InsertCenterMark3` 两格"
            "都**不成**，且其中**一格前置是成立的**（证据 JSON 的 A8 格）⇒ ★ 本工具走的是**批量**那条路，★ **尚未单独真"
            "机验证** ⇒ ★ 如实标注，**不许**当成「已验证」。"
        ),
        doc=(
            "Insert centre marks on drawing views through the batch entry point. It writes marks and does not save the "
            "document, it passes the requirements list straight to the capability layer, and this batch path has not ye"
            "t been verified on its own on this machine."
        ),
    ),
]

#: ★ 注册器按 `SPECS_*` 找本批（`register_capabilities.BATCH_MODULES` 里也要加一行）。
SPECS_BATCH75 = _BATCH75
