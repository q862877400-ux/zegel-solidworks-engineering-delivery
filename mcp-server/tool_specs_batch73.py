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
                description="★ **当前图纸上**的视图名（如 `Drawing View1` / `视图1`）。"
                "★ 官方示例要先选中视图、★ 那只是为了**拿到 IView 对象** ⇒ "
                "★ 本工具改成**按名字解析**，★ **不要求调用者先备选区**。",
            ),
            Param(
                "position1_mm",
                float,
                description="★ 第一条断裂线的位置（**毫米**）。⚠ **官方没给单位**，"
                "★ 本工具按 SolidWorks API 惯例当**米**、只在边界换算一次 —— "
                "★ 官方示例 `InsertBreak3(2, -2.91950859897372E-02, …)` = "
                "-29.195 mm，**佐证了米制**。★ 落在哪根轴上由 `orientation` 决定。",
            ),
            Param(
                "position2_mm",
                float,
                description="★ 第二条断裂线的位置（**毫米**；★ 同 `position1_mm` 的单位约定）"
                "—— ★ 官方逐字：一次断裂**由一对线**组成。",
            ),
            Param(
                "orientation",
                int,
                default=2,
                description="官方 `swBreakLineOrientation_e`：**1=Horizontal · 2=Vertical**。"
                "★★ 官方 `## Remarks` 逐字：Horizontal 时 Position1/2 是**Y** 值、"
                "Vertical 时是**X** 值，★ **两者都相对视图原点**。",
            ),
            Param(
                "style",
                int,
                default=5,
                description="官方 `swBreakLineStyle_e`：**1=Straight · 2=ZigZag · 3=Curve · "
                "4=SmallZigZag · 5=Jagged**（★ 逐字核 `swBreakLineStyle_e.md`）。",
            ),
            Param(
                "shape_intensity",
                int,
                default=2,
                description="★ 官方逐字「valid range is **1 (most) through 5 (least)**」；"
                "★ **只对锯齿（jagged）断裂线生效**。",
            ),
            Param(
                "break_sketch_blocks",
                bool,
                default=True,
                description="官方 `BreakSketchBlocks` —— True 连草图块一起断开。",
            ),
        ],
        evidence=(
            "★ **断裂视图**：`IView.InsertBreak3(6 参)` → `BreakLine`。★★ `InsertBreak`（4 参）与 `InsertBreak2`（5 参"
            "）**官方都标 Obsolete** ⇒ ★ 只走 3。★ 官方 `## Remarks`：Horizontal ⇒ 位置是 **Y** 值；Vertical ⇒ **X** 值"
            "；★ 都相对视图原点。★ **判据 = `GetBreakLines()` 的数组长度 + `IView.IsBroken()`**（★ 两个都要）——★ 官方把"
            "这两件事**定义成了两件**：有断裂线**不等于**断开了。⚠ 官方**没给位置参数的单位** ⇒ 本工具按米收、按毫米传"
            "、只在边界换算一次。"
        ),
        doc="★ **断裂视图**：`IView.InsertBreak3(6 参)` → `BreakLine`。"
        "★★ `InsertBreak`（4 参）与 `InsertBreak2`（5 参）**官方都标 Obsolete** ⇒ ★ 只走 3。"
        "★ 官方 `## Remarks`：Horizontal ⇒ 位置是 **Y** 值；Vertical ⇒ **X** 值；★ 都相对视图原点。"
        "★ **判据 = `GetBreakLines()` 的数组长度 + `IView.IsBroken()`**（★ 两个都要）——"
        "★ 官方把这两件事**定义成了两件**：有断裂线**不等于**断开了。"
        "⚠ 官方**没给位置参数的单位** ⇒ 本工具按米收、按毫米传、只在边界换算一次。",
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
                description="★ 辅助视图落位 X（**毫米**）。⚠ **官方没给单位** ⇒ 按米收、"
                "边界换算一次；★ ⚠ **该假设未由官方示例佐证**，须真机复核。",
            ),
            Param(
                "y_mm", float, description="★ 落位 Y（**毫米**；★ 单位约定同 `x_mm`）。"
            ),
            Param(
                "z_mm",
                float,
                default=0.0,
                description="★ 落位 Z（**毫米**；★ 工程图上通常留 0）。",
            ),
            Param(
                "label",
                str,
                default="",
                description="官方 `Label` —— 辅助视图的标签文字。",
            ),
            Param(
                "not_aligned",
                bool,
                default=True,
                description="官方形参 `NotAligned`。⚠★ **官方说明与形参名自相矛盾**："
                "官方 Parameters 逐字写「True **aligns** the view from its owner」——"
                "★ 名字说「不对齐」、说明说「对齐」⇒ ★ **原样透传、不替官方解释**，"
                "★ 默认取形参名的读法（True）。",
            ),
            Param(
                "show_arrow",
                bool,
                default=True,
                description="官方 `Showarrow` —— True 显示投影箭头。",
            ),
            Param(
                "flip",
                bool,
                default=False,
                description="官方 `Flip` —— True 翻转辅助视图所显示的那一侧。",
            ),
        ],
        evidence=(
            "★ **辅助视图**：`IDrawingDoc.CreateAuxiliaryViewAt2(7 参)`。★★★ **官方前置（摘要逐字）**：「Creates an aux"
            "iliary view **based on a selected edge in a drawing view**」⇒ ★★ **调用前必须先选中视图里的一条边**。★ 而*"
            "*边没有可用的名字**（本仓事实 32）⇒ ★ 本工具**不代选**，★ 只**回读当前选区计数**并写进 `preconditions_held"
            "` ⇒ 失败时能看见原因。★ **判据 = 视图数增量 + 新视图 `Type == 5`（`swDrawingAuxiliaryView`）**，★ 不是「返"
            "回非 None」。⚠ `NotAligned` 的官方说明与形参名矛盾，见该参数说明。"
        ),
        doc="★ **辅助视图**：`IDrawingDoc.CreateAuxiliaryViewAt2(7 参)`。"
        "★★★ **官方前置（摘要逐字）**："
        "「Creates an auxiliary view **based on a selected edge in a drawing view**」"
        "⇒ ★★ **调用前必须先选中视图里的一条边**。"
        "★ 而**边没有可用的名字**（本仓事实 32）⇒ ★ 本工具**不代选**，"
        "★ 只**回读当前选区计数**并写进 `preconditions_held` ⇒ 失败时能看见原因。"
        "★ **判据 = 视图数增量 + 新视图 `Type == 5`（`swDrawingAuxiliaryView`）**，"
        "★ 不是「返回非 None」。⚠ `NotAligned` 的官方说明与形参名矛盾，见该参数说明。",
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
                description="官方 `swSFSymType_e`（★ 10 个成员）："
                "**0=Basic · 1=JIS_Machining_Req · 2=Dont_Machine · "
                "3..6=JIS_Surface_Texture_1..4 · 7=JIS_No_Machining · "
                "8=JIS_Basic · 9=Machining_Req**（★ 逐字核 `swSFSymType_e.md`）。",
            ),
            Param(
                "leader_type",
                int,
                default=1,
                description="★ 官方 `swLeaderStyle_e`：**0=NO_LEADER · 1=STRAIGHT · 2=BENT · "
                "3=UNDERLINED · 4=SPLINE · 8=VDA**；★ 256..4100 那几个是"
                "**位掩码**、要**与** 1/2/3/4/8 之一**合用**。"
                "★★ **它决定那三个位置参数用不用**（见工具说明的官方 Remarks 逐字）。",
            ),
            Param(
                "x_mm",
                float,
                default=0.0,
                description="★ 符号位置 X（**毫米**）—— ★★ **仅当 `leader_type != 0` 时被官方使用**；"
                "★ 取 0（`swNO_LEADER`）时本工具**主动传 0** 并把原值回在 "
                "`ignored_location_mm` 里。",
            ),
            Param(
                "y_mm",
                float,
                default=0.0,
                description="★ 符号位置 Y（**毫米**；★ 条件同 `x_mm`）。",
            ),
            Param(
                "z_mm",
                float,
                default=0.0,
                description="★ 符号位置 Z（**毫米**；★ 条件同 `x_mm`）。",
            ),
            Param(
                "lay_symbol",
                int,
                default=0,
                description="官方 `swSFLaySym_e`（纹理方向）。★ ★ **本轮没查 `0` 是什么** ⇒ "
                "本工具**原样透传、不作断言**（★ 铁律 5：查不到就说查不到）。",
            ),
            Param(
                "arrow_type",
                int,
                default=0,
                description="官方 `swArrowStyle_e`（箭头样式）。★ 同 `lay_symbol`："
                "**默认值 0 的语义未查**，原样透传。",
            ),
            Param(
                "mach_allowance",
                str,
                default="",
                description="官方 `MachAllowance`（材料去除余量）。★ 官方类型是 `System.string` "
                "**且没给格式** ⇒ 本工具**原样透传、不解析、不校验**。",
            ),
            Param(
                "other_vals",
                str,
                default="",
                description="官方 `OtherVals`（其它粗糙度值）。★ 同上：字符串、原样透传。",
            ),
            Param(
                "prod_method",
                str,
                default="",
                description="官方 `ProdMethod`（生产方法与处理）。★ 同上。",
            ),
            Param(
                "sample_len",
                str,
                default="",
                description="官方 `SampleLen`（取样长度）。★ 同上。",
            ),
            Param(
                "max_roughness",
                str,
                default="",
                description="官方 `MaxRoughness`（最大粗糙度）。★ 同上。",
            ),
            Param(
                "min_roughness",
                str,
                default="",
                description="官方 `MinRoughness`（最小粗糙度）。★ 同上。",
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
        doc="★ **表面粗糙度符号**：`IModelDocExtension.InsertSurfaceFinishSymbol3(14 参)`。"
        "★★ **官方 `## Remarks` 逐字**：「The SOLIDWORKS Design software uses the location "
        "parameters for this method **only if** the surface finish symbol has a leader "
        "leaderType **!= swNO_LEADER**.」⇒ ★★ `leader_type = 0` 时**三个位置参数被官方无视**"
        "⇒ ★ 本工具在那一档**主动传 0** 并把原坐标回在 `ignored_location_mm`。"
        "★ **另一条前置**：官方摘要逐字「based on the **last selection**」⇒ ★ 调用前必须有选区；"
        "★ 本工具**不代选**（★ 规则 3 禁裸坐标），只回读选区计数写进 `preconditions_held`。"
        "★ **判据 = 全图纸 `IView.GetSFSymbolCount` 求和的增量**，★ 不是「返回非 None」。",
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
        doc="★ **基准符号**：`IModelDoc2.InsertDatumTag2()` → `DatumTag`（★ **官方零参数**）。"
        "★★ **官方前置**（摘要逐字）：「Inserts a datum tag symbol **at a selected "
        "location**.」⇒ ★ 调用前必须先选中一个位置（★ 官方示例用 `SelectByID2` 选 EDGE）。"
        "★ 因为官方**零参数**，★ 落点**完全由选区决定** ⇒ 本工具**没有坐标入口**"
        "（★ 这既由官方签名决定，★ 也正好合上规则 3 的「禁裸坐标」）。"
        "★ 入口是 `IModelDoc2`（**不是** `IModelDocExtension`）—— ★ 与表面粗糙度符号那 14 参"
        "**不是同一个宿主对象**。"
        "★ **判据 = 全图纸 `IView.GetDatumTagCount` 求和的增量**，★ 不是「返回非 None」。 ★ 别名: annotation, balloon, datum, gdt, gtol, note, tolerance",
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
