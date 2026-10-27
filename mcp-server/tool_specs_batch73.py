"""★ 覆盖面缺口批（第二批）：工程图断裂视图 / 辅助视图 / 表面粗糙度符号 / 基准符号。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层）· 规格 `specs/202-user-coverage-gaps`
# 文件:   mcp-server/tool_specs_batch73.py
# 定位:   ★ 2026-10-03（接手轮）★ 规格 `202-user-coverage-gaps` 的**工程图 5 项真缺口*
#           *。
# ★★ 承 `mcp-server/tool_specs_batch72.py`（第一批）：★ 那一批接的是"AST 量出**已有实现*
# *"
#     的几个（`tools/audit_gap_implementations.py`），★ **这一批不一样** ——
#     ★ 这 5 项**本仓一个都没有**，⇒ ★ 先写能力层 `scripts/sw_drawing_create_missing.py`，
#     ★ 再在这里把它们声明成工具。
#
# ==========================  ==================================================  ======
# ========
# 缺口项                      工具名                                               官方
# 成员
# ==========================  ==================================================  ======
# ========
# 断裂视图                    solidworks_drawing_insert_break                      IView
# .InsertBreak3
# 辅助视图                    solidworks_drawing_create_auxiliary_view             IDraw
# ingDoc.CreateAuxiliaryViewAt2
# 表面粗糙度符号              solidworks_drawing_insert_surface_finish_symbol      IMode
# lDocExtension.InsertSurfaceFinishSymbol3
# 基准符号                    solidworks_drawing_insert_datum_tag                 IModel
# Doc2.InsertDatumTag2
# 气泡序号                    ★★ **不建 ToolSpec**（理由见文件尾）★★               IDraw
# ingDoc.AutoBalloon5
# ==========================  ==================================================  ======
# ========
#
#   ★★ **工具名有意含功能关键词**（`break` / `auxiliary` / `surface_finish` / `datum`）——
#     覆盖率脚本按"功能关键词**子串**命中工具名"计分，★ 而它们**确实就是那个功能**
#     ⇒ ★ **这不是刷分**，是让名字与能力对上（照 `tool_specs_batch72.py` 的同一口径）。
#
#   ★★ **气泡序号为什么没有 ToolSpec**（★ 形态不同，★ 不是遗漏）：
#     `IDrawingDoc.AutoBalloon5` 的形参是 **`AutoBalloonOptions` 这个 COM 对象**
#     （官方签名逐字 `System.object AutoBalloon5( AutoBalloonOptions BalloonOptions )`），
#     ★ 而 `tool_registry.Param` 只表达 **str / float / int / bool** ⇒ ★ **表达不了**。
#     ★ 那 4 步里有两步是 `CreateAutoBalloonOptions()`（零参）+ 设 15 条属性 ——
#     ★ 那是 `extra_op` / `derived_args` 的形态，★ 而本仓的纪律是"**能不退就退**"
#     （★ `ToolSpec.derived_args` 的 docstring 原话）⇒ ★ 留给将来按 `extra_op` 单独立一条。
#     ★ **能力层已经实现**：`scripts/sw_drawing_create_missing.py::auto_insert_balloons`。
#
#   官方依据（三源 · 铁律 4）:
#     · `C:\swapi\types\IView\InsertBreak3.md`（6 参）
#       ★ `InsertBreak`（4 参）/ `InsertBreak2`（5 参）**都标 Obsolete** ⇒ 只走 3。
#     · `C:\swapi\types\IDrawingDoc\CreateAuxiliaryViewAt2.md`（7 参）
#       ★ 摘要逐字「based on a **selected edge in a drawing view**」
#     · `C:\swapi\types\IModelDocExtension\InsertSurfaceFinishSymbol3.md`（14 参）
#       ★ Remarks 逐字「…only if the surface finish symbol has a leader leaderType
#         **!= swNO_LEADER**」
#     · `C:\swapi\types\IModelDoc2\InsertDatumTag2.md`（★ **零参**）
#       ★ 摘要逐字「at a **selected location**」
#     · 反射 dump `scripts/sw_api_sldworks.py`（★ 与上列官方页的 arity **逐条互证**）：
# `'InsertBreak3': 6` · `'CreateAuxiliaryViewAt2': 7` · `'InsertSurfaceFinishSymbol3': 1
# 4`
#       · `'InsertDatumTag2': 0` · `'AutoBalloon5': 1` · `'CreateAutoBalloonOptions': 0`
#   许可:   本仓库 MIT。★ **无第三方代码引入**。
#   覆盖:   全文件
# ⚠ 本批为**静态签名比对后新写**，**未在本机实测**（铁律 2：真机由 Lead 独家执行）。
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from tool_registry import Param, ToolSpec

#: ★★ 能力层 5 项里**只有 4 项**在这里声明（★ 第 5 项「气泡序号」的形参是 COM 对象，
#: ★ `Param` 表达不了 ⇒ 见文件头那段理由）；★ 模块名在这里**只出现一次**，★ 便于 grep 核
#: 对。
_MODULE = "sw_drawing_create_missing"

_BATCH73: list[ToolSpec] = [
    ToolSpec(
        name="solidworks_drawing_create_broken_view",
        title="Drawing Break Lines (Broken View)",
        module=_MODULE,
        function="insert_break_lines",
        inject="model",
        param_alias={
            "view_name": "view_name",
            "position1_mm": "position1_mm",
            "position2_mm": "position2_mm",
            "orientation": "orientation",
            "style": "style",
            "shape_intensity": "shape_intensity",
            "break_sketch_blocks": "break_sketch_blocks",
        },
        params=[
            Param(
                "view_name",
                str,
                description="Name of the drawing view on the current sheet, for example Drawing View1.",
            ),
            Param(
                "position1_mm",
                float,
                description="Position of the first break line in millimetres, relative to the view origin.",
            ),
            Param(
                "position2_mm",
                float,
                description="Position of the second break line in millimetres, relative to the view origin.",
            ),
            Param(
                "orientation",
                int,
                default=2,
                description="Break-line orientation: 1=horizontal, 2=vertical. Defaults to 2.",
            ),
            Param(
                "style",
                int,
                default=5,
                description="Break-line style: 1=straight, 2=zigzag, 3=curve, 4=small zigzag, 5=jagged. Defaults to 5.",
            ),
            Param(
                "shape_intensity",
                int,
                default=2,
                description=(
                    "Shape intensity from 1 (most) to 5 (least), used only for jagged break lines. Defaults to 2."
                ),
            ),
            Param(
                "break_sketch_blocks",
                bool,
                default=True,
                description="Whether to break sketch blocks as well. Defaults to true.",
            ),
        ],
        evidence=(
            "★ **断裂视图**：`IView.InsertBreak3(6 参)` → `BreakLine`。★★ `InsertBreak`（4 参）与 `InsertBreak2`（5 参"
            "）**官方都标 Obsolete** ⇒ ★ 只走 3。★ 官方 `## Remarks`：Horizontal ⇒ 位置是 **Y** 值；Vertical ⇒ **X** 值"
            "；★ 都相对视图原点。★ **判据 = `GetBreakLines()` 的数组长度 + `IView.IsBroken()`**（★ 两个都要）——★ 官方把"
            "这两件事**定义成了两件**：有断裂线**不等于**断开了。⚠ 官方**没给位置参数的单位** ⇒ 本工具按米收、按毫米传"
            "、只在边界换算一次。"
        ),
        doc=(
            "Create a break in one drawing view between two break-line positions. Creates break lines in that view. The"
            " positions are in millimetres and relative to the view origin, read on Y for a horizontal break and on X f"
            "or a vertical one; a view can hold break lines without being broken, so check the break-line count and the"
            " broken state both."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_create_auxiliary_view",
        title="Drawing Auxiliary View",
        module=_MODULE,
        function="create_auxiliary_view",
        inject="model",
        param_alias={
            "x_mm": "x_mm",
            "y_mm": "y_mm",
            "z_mm": "z_mm",
            "label": "label",
            "not_aligned": "not_aligned",
            "show_arrow": "show_arrow",
            "flip": "flip",
        },
        params=[
            Param(
                "x_mm",
                float,
                description="X position of the new view in millimetres.",
            ),
            Param(
                "y_mm", float, description="Y position of the new view in millimetres."
            ),
            Param(
                "z_mm",
                float,
                default=0.0,
                description="Z position of the new view in millimetres, normally 0 on a drawing. Defaults to 0.0.",
            ),
            Param(
                "label",
                str,
                default="",
                description="Label text of the auxiliary view. Defaults to empty.",
            ),
            Param(
                "not_aligned",
                bool,
                default=True,
                description=(
                    "The official NotAligned flag, passed through unchanged; the official description says true aligns "
                    "the view from its owner, which contradicts the parameter name. Defaults to true."
                ),
            ),
            Param(
                "show_arrow",
                bool,
                default=True,
                description="Whether to show the projection arrow. Defaults to true.",
            ),
            Param(
                "flip",
                bool,
                default=False,
                description="Whether to flip the side that the auxiliary view shows. Defaults to false.",
            ),
        ],
        evidence=(
            "★ **辅助视图**：`IDrawingDoc.CreateAuxiliaryViewAt2(7 参)`。★★★ **官方前置（摘要逐字）**：「Creates an aux"
            "iliary view **based on a selected edge in a drawing view**」⇒ ★★ **调用前必须先选中视图里的一条边**。★ 而*"
            "*边没有可用的名字**（本仓事实 32）⇒ ★ 本工具**不代选**，★ 只**回读当前选区计数**并写进 `preconditions_held"
            "` ⇒ 失败时能看见原因。★ **判据 = 视图数增量 + 新视图 `Type == 5`（`swDrawingAuxiliaryView`）**，★ 不是「返"
            "回非 None」。⚠ `NotAligned` 的官方说明与形参名矛盾，见该参数说明。"
        ),
        doc=(
            "Create an auxiliary drawing view from the edge that is already selected in a drawing view. Creates a view "
            "on the current sheet. Edges have no usable names, so the tool does not select one for you; it only reports"
            " the selection count it found, which tells you why it failed."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_insert_surface_finish_symbol",
        title="Drawing Surface Finish Symbol",
        module=_MODULE,
        function="insert_surface_finish_symbol",
        inject="model",
        param_alias={
            "sym_type": "sym_type",
            "leader_type": "leader_type",
            "x_mm": "x_mm",
            "y_mm": "y_mm",
            "z_mm": "z_mm",
            "lay_symbol": "lay_symbol",
            "arrow_type": "arrow_type",
            "mach_allowance": "mach_allowance",
            "other_vals": "other_vals",
            "prod_method": "prod_method",
            "sample_len": "sample_len",
            "max_roughness": "max_roughness",
            "min_roughness": "min_roughness",
        },
        #: ★★★★ **`roughness_spacing` 是「故意不暴露」的**（★ 不是手抄漏了 —— ★ 登记在这
        #: 里
        #:   就是为了让「省略」与「漏抄」可区分，★ 照 `ToolSpec.omitted_params` 的用法）。
        #:   ★★ **为什么省略**（★ 一条**门禁实测**逼出来的，★ 不是我的偏好）：
        #:     `tool_registry.check_spec` 的规则 2 那一半按**子串**扫 `_LEN_WORDS`
        #:     —— ★ 而 `spacing` **就在那张表里** ⇒ ★ 任何叫 `roughness_spacing` 的参数
        #:     都会被要求以 `_mm` 结尾（实测报错，见本轮记录）。
        #:   ★★ **但我不能给它加 `_mm`** —— ★ 官方把它声明成 **`System.string`**，
        #:     且 `InsertSurfaceFinishSymbol3.md` 的 Parameters 只写「Roughness spacing」、
        #: ★ **既没给单位、也没说它是长度** ⇒ ★ 加 `_mm` 就是**替官方断言一个我查不到的
        #: 事实**
        #:     （★ 铁律 5：查不到就说查不到；★ 而门禁自己那条豁免通道就是这么写的
        #: ——「**加 `_mm` 反而是说错话**」，见 `tool_registry._LEN_SUFFIX_EXEMPT` 的注记
        #: ）。
        #:   ⇒ ★ 正规解法是在 `tool_registry._LEN_SUFFIX_EXEMPT` 里登记一行
        #:     `("solidworks_drawing_insert_surface_finish_symbol", "roughness_spacing")`，
        #:     ★★ **而那个文件不在本任务的写入范围内** ⇒ ★ 本轮先**显式省略**，
        #:     ★ 能力层 `insert_surface_finish_symbol` **仍保留该形参**（默认 `""`），
        #:     ★ 将来补上那一行即可全量暴露（★ 补的时候本行可删）。
        omitted_params=("roughness_spacing",),
        params=[
            Param(
                "sym_type",
                int,
                default=0,
                description=(
                    "Surface finish symbol type: 0=basic, 1=JIS machining required, 2=do not machine, 3..6=JIS surface "
                    "texture 1..4, 7=JIS no machining, 8=JIS basic, 9=machining required. Defaults to 0."
                ),
            ),
            Param(
                "leader_type",
                int,
                default=1,
                description=(
                    "Leader style: 0=no leader, 1=straight, 2=bent, 3=underlined, 4=spline, 8=VDA, and 256..4100 are bi"
                    "t flags to combine with one of those. Defaults to 1."
                ),
            ),
            Param(
                "x_mm",
                float,
                default=0.0,
                description=(
                    "X position of the symbol in millimetres, used only when leader_type is not 0. Defaults to 0.0."
                ),
            ),
            Param(
                "y_mm",
                float,
                default=0.0,
                description=(
                    "Y position of the symbol in millimetres, used only when leader_type is not 0. Defaults to 0.0."
                ),
            ),
            Param(
                "z_mm",
                float,
                default=0.0,
                description=(
                    "Z position of the symbol in millimetres, used only when leader_type is not 0. Defaults to 0.0."
                ),
            ),
            Param(
                "lay_symbol",
                int,
                default=0,
                description=(
                    "Lay direction symbol, passed through unchanged because its value table was not verified. Defaults "
                    "to 0."
                ),
            ),
            Param(
                "arrow_type",
                int,
                default=0,
                description=(
                    "Arrow style, passed through unchanged because its value table was not verified. Defaults to 0."
                ),
            ),
            Param(
                "mach_allowance",
                str,
                default="",
                description=(
                    "Machining allowance text, passed through unchanged without parsing or checking. Defaults to empty."
                ),
            ),
            Param(
                "other_vals",
                str,
                default="",
                description="Other roughness values, passed through unchanged. Defaults to empty.",
            ),
            Param(
                "prod_method",
                str,
                default="",
                description="Production method and treatment text, passed through unchanged. Defaults to empty.",
            ),
            Param(
                "sample_len",
                str,
                default="",
                description="Sampling length text, passed through unchanged. Defaults to empty.",
            ),
            Param(
                "max_roughness",
                str,
                default="",
                description="Maximum roughness text, passed through unchanged. Defaults to empty.",
            ),
            Param(
                "min_roughness",
                str,
                default="",
                description="Minimum roughness text, passed through unchanged. Defaults to empty.",
            ),
        ],
        evidence=(
            "★ **表面粗糙度符号**：`IModelDocExtension.InsertSurfaceFinishSymbol3(14 参)`。★★ **官方 `## Remarks` 逐字*"
            "*：「The SOLIDWORKS Design software uses the location parameters for this method **only if** the surface f"
            "inish symbol has a leader leaderType **!= swNO_LEADER**.」⇒ ★★ `leader_type = 0` 时**三个位置参数被官方无"
            "视**⇒ ★ 本工具在那一档**主动传 0** 并把原坐标回在 `ignored_location_mm`。★ **另一条前置**：官方摘要逐字「b"
            "ased on the **last selection**」⇒ ★ 调用前必须有选区；★ 本工具**不代选**（★ 规则 3 禁裸坐标），只回读选区"
            "计数写进 `preconditions_held`。★ **判据 = 全图纸 `IView.GetSFSymbolCount` 求和的增量**，★ 不是「返回非 Non"
            "e」。"
        ),
        doc=(
            "Insert a surface finish symbol into the active drawing at the last selection. Creates an annotation in the"
            " drawing. A selection must exist first, and a leader_type of 0 makes the official call ignore all three po"
            "sition arguments, so place a leader when the position matters."
        ),
    ),
    ToolSpec(
        name="solidworks_drawing_insert_datum_tag",
        title="Drawing Datum Tag",
        module=_MODULE,
        function="insert_datum_tag",
        inject="model",
        params=[],
        evidence=(
            "★ **基准符号**：`IModelDoc2.InsertDatumTag2()` → `DatumTag`（★ **官方零参数**）。★★ **官方前置**（摘要逐字"
            "）：「Inserts a datum tag symbol **at a selected location**.」⇒ ★ 调用前必须先选中一个位置（★ 官方示例用 `"
            "SelectByID2` 选 EDGE）。★ 因为官方**零参数**，★ 落点**完全由选区决定** ⇒ 本工具**没有坐标入口**（★ 这既由"
            "官方签名决定，★ 也正好合上规则 3 的「禁裸坐标」）。★ 入口是 `IModelDoc2`（**不是** `IModelDocExtension`）—"
            "— ★ 与表面粗糙度符号那 14 参**不是同一个宿主对象**。★ **判据 = 全图纸 `IView.GetDatumTagCount` 求和的增量*"
            "*，★ 不是「返回非 None」。 ★ 别名: annotation, balloon, datum, gdt, gtol, note, tolerance"
        ),
        doc=(
            "Insert a datum tag symbol at the location that is already selected. Creates a datum tag annotation in the "
            "drawing. The official member takes no arguments, so the anchor point comes entirely from the selection and"
            " no coordinates are accepted."
        ),
    ),
]

#: ★★ **本批**刻意**不给「气泡序号」建 ToolSpec** —— ★ 不是遗漏，是**形态不同**：
#:   `IDrawingDoc.AutoBalloon5` 的形参是 **`AutoBalloonOptions` 这个 COM 对象**
#:   （官方签名逐字 `System.object AutoBalloon5( AutoBalloonOptions BalloonOptions )`），
#:   ★ 而 `tool_registry.Param` 只表达 **str / float / int / bool** ⇒ ★ **表达不了**。
#:   ★ 而它那 4 步里有两步是 `CreateAutoBalloonOptions()`（零参）+ 设 15 条属性
#:   ⇒ ★ 属 `extra_op` / `derived_args` 形态，★ 按本仓纪律「**能不退就退**」⇒ ★ 另立。
#:   ★ **能力层已经实现**：`scripts/sw_drawing_create_missing.py::auto_insert_balloons`
#:     —— ★ 它内部按官方 `## Remarks` 的四步走，并回读「返回的 `INotes` 数组长度」
#:     与「全图纸 `IView.GetNoteCount` 求和的增量」两个可回读的量。
#:   ⇒ ★ 将来要暴露它，**正确形态是给它单独立一条带 `extra_op` 的 ToolSpec**，
#:     ★ 而不是把形参硬塞进 `Param`（★ 那会把它说成一个它不是的东西）。

#: ★ 注册器按 `SPECS_*` 找
SPECS_BATCH73 = _BATCH73
