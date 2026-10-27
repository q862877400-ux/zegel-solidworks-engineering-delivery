"""★ 批次 92：规格 209 · B1 批 —— 重建 / 构造几何 / 显示状态 / 引用文档（5 个工具）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `scripts/sw_session.py`（重建）· `scripts/sw_sketch_edit_ops.py`（构造几何）·
#         `scripts/sw_render_material.py`（显示状态）· `scripts/sw_document_data.py`（引用文档）
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B1 批** —— 来源是规格 207 逐条核实后
#         **采纳的 18 条候选**（`docs/recon-207/adjudication.md`），本批取其中最干净的 4 件活：
#         ```
#         idx 235 + 236  rebuild          ★ 裁决书强制「**合并成一条**（三档 mode），不建两条」
#         idx  79        construction_geometry  ★ 复用 sw_sketch_edit_ops 已有的声明式选段包装
#         idx  97        display_states   ★ 读侧落 sw_render_material（事实 286 已真机 PASS）
#         idx 244        referenced_documents  ★ 补 pack_and_go 一直枚举却不暴露的**读侧**
#         ```
# 官方依据: ★★ **逐页读过**（`C:\swapi` 的 md + 出厂类型库反射 arity）—— 逐条见各函数来
#           源块：
# `IModelDoc2\{EditRebuild3,ForceRebuild3}.md` · `IModelDocExtension\{ForceRebuildAll,Ne
# edsRebuild2}.md` ·
#   `enums\swModelRebuildStatus_e.md` · `ISketchManager\CreateConstructionGeometry.md` ·
# `ISketchSegment\ConstructionGeometry.md` · `IConfiguration\{GetDisplayStates,ApplyDisp
# layState,
#   GetDisplayStatesCount}.md` · `IConfigurationManager\ActiveConfiguration.md` ·
#   `enums\swDocumentTypes_e.md` · `ISldWorks\GetDocumentDependencies2.md`
#   ★★ 其中三条**官方逐字**被当成硬约束写进了实现（见下），**不是我们自己定的口径**：
#     ① `EditRebuild3` 是**方法**（三家外部项目当属性读 ⇒ 拿到 bound method ⇒ 判据恒真）；
# ② `GetDisplayStates` 的 Remarks「first name = active」**只在没有多个显示状态同时活动时
# **成立
#        ⇒ 装配里必须给 `ambiguous`；
#     ③ `GetDocumentDependencies2` 「**Library features 不会返回**」⇒ 盲区要随返回值带出去。
# 许可:   本仓库 MIT。★ 无第三方代码引入（全部按官方签名自建）。
# 规模:   **6 个工具** ⇒ 工具数 433 → **439**
# ★★ 本批**不做**的（★ 裁决书已裁掉，**别顺手补**）：
# · idx 273 `setup_template_positions` —— **缓办**（域未分类 + 要用 `ISheet::SetProperti
# es2`
#       的写入通道，且那些属性名/数值约定**两套官方源都查不到**）✓
# · idx 115/145 `edges`/`faces` —— ★ **独立风险**（"读属性读不到"）⇒ 裁决书要求**先小验
# 证**，
#       故不在本批（★ 它要**扩**已有 `solidworks_entities_on_body`，**不许开平行工具**）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH92"]


SPECS_BATCH92 = [
    # ── ① 重建（1）—— ★★ 裁决书强制「235+236 合并成一条」，**不建两条** ───────────────
    # ──────
    ToolSpec(
        name="solidworks_session_rebuild",
        title="Rebuild the Model (three modes: edit / force / all)",
        module="sw_session",
        function="rebuild_report",
        inject="model",
        params=[
            Param(
                "mode",
                str,
                default="edit",
                description=(
                    "Rebuild mode: 'edit' rebuilds only the features that need it, 'force' rebuilds every feature of th"
                    "e active configuration, and 'all' rebuilds every configuration without switching. Defaults to 'edi"
                    "t'."
                ),
            ),
            Param(
                "top_only",
                bool,
                default=False,
                description=(
                    "Whether a force rebuild covers only the top level and leaves subassemblies alone; the other two mo"
                    "des ignore it. Defaults to false."
                ),
            ),
        ],
        evidence=(
            "★ **重建模型** —— 三档 `mode` 一条工具（★ 官方三个入口：`EditRebuild3` / `ForceRebuild3` / `ForceRebuildAl"
            "l`；★ **不建三条**，因为它们是同一件事的三档，合并才不会在能力清单里留下同进同退的条目）✓ ★★ **判据是回读"
            "，不是返回值**：① 回读 `IModelDocExtension::NeedsRebuild2` 须为 `fully_rebuilt`；② 特征树计数**不变**（重"
            "建改的是状态、不是树的形状）；③ 包围盒**不变**（同参数下重建不该改几何）。★★ 为什么返回值不能当判据：★ `Ed"
            "itRebuild3` 是**方法**、不是属性 —— 三家外部项目都把它当属性读（`_get(doc, 'EditRebuild3')`），★ 那样拿到"
            "的是 **bound method**，**恒为真**。⚠ **边界（官方 Remarks 逐字）**：`EditRebuild3` 「only works **in-conte"
            "xt of the active document**」⇒ 对未激活的文档调用没有意义（本工具不替调用方激活文档）。"
        ),
        doc=(
            "Refresh the active document by rebuilding it in one of three modes and report the read-back state. Modifie"
            "s the document state, leaves the feature tree and geometry alone, and only works on the active document; j"
            "udge the result by the read-back, not by the return value."
        ),
    ),
    # ── ② 构造几何（1）—— ★ 复用该文件已有的声明式选段包装（裁决书指定）───────────────
    # ─────
    ToolSpec(
        name="solidworks_sketch_set_construction_geometry",
        title="Set / Unset Selected Sketch Segments as Construction Geometry",
        module="sw_sketch_edit_ops",
        function="sketch_set_construction_geometry",
        inject="model",
        params=[
            Param(
                "selection",
                str,
                description=(
                    "Declarative segment selection: __current_selection__ for the existing selection, or index:0 and in"
                    "dex:0,index:1 for zero-based segment positions."
                ),
            ),
            Param(
                "construction",
                bool,
                default=True,
                description=(
                    "Whether to make the segments construction geometry; false turns them back into normal sketch geome"
                    "try. Defaults to true."
                ),
            ),
        ],
        evidence=(
            "★ **把选中的草图段置为 / 复位为构造几何**（合并工具：方向由 `construction` 定，★ 不建两条）✓ ★ 官方两个入"
            "口分工**已在注释里定死**：置位走零参 `ISketchManager::CreateConstructionGeometry()`（官方摘要逐字「**Sets*"
            "* … **instead of**」，★ 是**置位**不是 toggle）；复位走 `ISketchSegment::ConstructionGeometry` 属性 setter"
            "（★ 官方唯一的回程）✓ ★★ **判据 = 回读属性**：调用后逐段读 `ConstructionGeometry`，要求**目标段读数 == 请"
            "求值**；读回不等于请求 ⇒ `ok=False` 并**如实报哪几段没对上**（★ 不静默 —— 这正是「再调一次是切换还是置位」"
            "那件事会暴露的地方）✓"
        ),
        doc=(
            "Set or clear construction geometry on the selected sketch segments. Modifies the active sketch: the segmen"
            "t property is read back afterwards and a mismatch is reported, because the set call assigns the state inst"
            "ead of toggling it."
        ),
    ),
    # ── ③ 显示状态（2）—— ★★ `ambiguous` 是裁决书点名的硬约束 ─────────────────────────
    # ────
    ToolSpec(
        name="solidworks_config_list_display_states",
        title="List the Display States of the Active Configuration",
        module="sw_render_material",
        function="list_display_states",
        inject="model",
        read_only=True,
        params=[],
        evidence=(
            "★ **列出当前配置的显示状态**（官方 `IConfiguration::GetDisplayStates()`）✓ ★★ **结果里必须看 `ambiguous`**"
            "：官方 Remarks 逐字「The **first name in the list is the active display state**. **If more than one displa"
            "y state is active** in the current model, call `IComponent2::ReferencedDisplayState` …」⇒ ★ **装配**里「第"
            "一个即活动」**不保证成立** ⇒ ★ 本工具在装配里给 `ambiguous=True` 并写明理由，**不替调用方猜**（裁决书硬约"
            "束）✓ ★ 判据 = `GetDisplayStates()` 与 `GetDisplayStatesCount()` **两个官方入口**读数一致（规则 6：不用被"
            "调成员自己的返回值当判据）。"
        ),
        doc=(
            "List the display states of the current configuration. Read-only; the first name is the active state only w"
            "hen the model is a part, so the returned ambiguous flag marks the assemblies where that rule does not hold"
            "."
        ),
    ),
    ToolSpec(
        name="solidworks_config_apply_display_state",
        title="Activate a Display State of the Active Configuration",
        module="sw_render_material",
        function="apply_display_state",
        inject="model",
        params=[
            Param(
                "display_state_name",
                str,
                description=(
                    "Display state name to activate; take it from solidworks_config_list_display_states, since a name t"
                    "hat is not listed is rejected instead of created."
                ),
            ),
        ],
        evidence=(
            "★ **激活指定显示状态**（官方 `IConfiguration::ApplyDisplayState(Name)`，回 `bool`）✓ ★★ **判据（规则 6）**"
            "：① 返回 `True`（官方 Returns 逐字）；② **回读** `GetDisplayStates()` —— 第一个名字变成请求的那个。★ 而 `a"
            "mbiguous=True`（装配）时**只认①**、不做②（★ 官方那句在装配里不成立）—— 返回值里会写明「②不可用」✓ ⚠ 本工具"
            "**不做**「新建显示状态」—— 那是 `IConfiguration::CreateDisplayState` 的事，不属于本规格的候选。"
        ),
        doc=(
            "Activate one display state by name in the current configuration. Modifies the active display state; the na"
            "me must already exist because this tool never creates one, and the first-name read-back is skipped for ass"
            "emblies, where the returned ambiguous flag says so."
        ),
    ),
    # ── ④ 引用文档（1）—— ★ 补 pack_and_go 的读侧 ─────────────────────────────────────
    # ───
    ToolSpec(
        name="solidworks_document_dependencies",
        title="List a Document's Referenced Documents (dependencies)",
        module="sw_document_data",
        function="document_dependencies",
        inject="sw_app",
        read_only=True,
        params=[
            Param(
                "document",
                str,
                description=(
                    "Document name or full path, passed through to the official call unchanged; the official examples u"
                    "se a full path."
                ),
            ),
            Param(
                "traverse",
                bool,
                default=True,
                description=(
                    "Whether to recurse into every depended-on file; false reports only the top level. Defaults to true"
                    "."
                ),
            ),
            Param(
                "search",
                bool,
                default=False,
                description=(
                    "Whether to find dependencies with the search rules, which also changes the current directory after"
                    "wards. Defaults to false."
                ),
            ),
            Param(
                "add_read_only_info",
                bool,
                default=False,
                description=(
                    "Whether to add a read-only information string after each document, where an empty string means the"
                    " file is not read-only. Defaults to false."
                ),
            ),
        ],
        evidence=(
            "★ **列出一个文档的引用（依赖）清单**（官方 `ISldWorks::GetDocumentDependencies2`）—— ★ 补上 `solidworks_pa"
            "ck_and_go` **一直枚举却不暴露的读侧** ✓ ★ 返回值按官方 `## Returns` 的**步长**还原成记录（每个文档 2 个串"
            "：名字 + 全路径；开了 `add_read_only_info` 再加 1 个），★ **数组长度除不尽就报错**、不硬凑 ✓ ★★ **已知盲区"
            "（官方 Remarks 逐字）**：**库特征（Library features）不会返回** —— 「Library features are completely unass"
            "ociated … Therefore, this method would not return Library features.」⇒ ★ 该盲区**随返回值一起**回给调用方"
            "，★ **把这份清单当「完整依赖」是错的** ✓ ⚠ 另两条官方逐字已写进返回值：★ **被压缩的组件也会出现**（别把「"
            "出现了」当「生效了」）· ★ `search=True` 会**改当前目录**。"
        ),
        doc=(
            "List the external references of a document as name and path records. Read-only; library features are never"
            " returned and suppressed components do appear, so do not read this list as the complete dependency set."
        ),
    ),
    # ── ⑤ 移动/复制实体（1）—— ★ 裁决书 §九 称它是「本批最干净的一条」─────────────────
    # ───
    ToolSpec(
        name="solidworks_part_move_copy_body",
        title="Move or Copy Solid Bodies (InsertMoveCopyBody2)",
        module="sw_body_ops",
        function="move_copy_body",
        inject="model",
        params=[
            Param(
                "selection",
                str,
                default="all",
                description=(
                    "Which bodies to move or copy: 'all' for every body in the part, or 'index:<n>' for the n-th body. "
                    "Defaults to 'all'."
                ),
            ),
            Param(
                "translate_x_mm", float, default=0.0, description=(
                                                          "Translation increment along X in millimetres, taken as docum"
                                                          "ent units and not converted. Defaults to 0.0."
                                                      )
            ),
            Param(
                "translate_y_mm", float, default=0.0, description=(
                                                          "Translation increment along Y in millimetres, taken as docum"
                                                          "ent units and not converted. Defaults to 0.0."
                                                      )
            ),
            Param(
                "translate_z_mm", float, default=0.0, description=(
                                                          "Translation increment along Z in millimetres, taken as docum"
                                                          "ent units and not converted. Defaults to 0.0."
                                                      )
            ),
            Param(
                "translate_dist_mm",
                float,
                default=0.0,
                description=(
                    "Translation distance in millimetres, taken as document units and not converted. Defaults to 0.0."
                ),
            ),
            Param(
                "rotate_point_x_mm",
                float,
                default=0.0,
                description="X of the rotation origin in millimetres, taken as document units. Defaults to 0.0.",
            ),
            Param(
                "rotate_point_y_mm",
                float,
                default=0.0,
                description="Y of the rotation origin in millimetres, taken as document units. Defaults to 0.0.",
            ),
            Param(
                "rotate_point_z_mm",
                float,
                default=0.0,
                description="Z of the rotation origin in millimetres, taken as document units. Defaults to 0.0.",
            ),
            Param(
                "rotate_angle_x_deg",
                float,
                default=0.0,
                description=(
                    "Rotation angle about X in degrees, converted to radians once at this boundary; the axis mapping is"
                    " compensated, so this value really turns about X. Defaults to 0.0."
                ),
            ),
            Param(
                "rotate_angle_y_deg",
                float,
                default=0.0,
                description=(
                    "Rotation angle about Y in degrees, converted to radians once at this boundary. Defaults to 0.0."
                ),
            ),
            Param(
                "rotate_angle_z_deg",
                float,
                default=0.0,
                description=(
                    "Rotation angle about Z in degrees, converted to radians once at this boundary; the axis mapping is"
                    " compensated, so this value really turns about Z. Defaults to 0.0."
                ),
            ),
            Param(
                "copy",
                bool,
                default=False,
                description=(
                    "Whether to copy the bodies instead of moving them, which adds bodies rather than displacing them. "
                    "Defaults to false."
                ),
            ),
            Param(
                "num_copies",
                int,
                default=1,
                description="How many copies to create, at least 1. Defaults to 1.",
            ),
        ],
        evidence=(
            "★ **移动或复制实体**（官方 `IFeatureManager::InsertMoveCopyBody2`，**12 参**）—— ★ 官方页 **signature + 逐"
            "字 mark 表（1/2/4/8）+ 官方示例调用序**全齐 ✓ ★★ **判据（规则 6）**：① **移动** ⇒ **包围盒必须变**；② **复"
            "制** ⇒ **实体个数必须增** —— 两者都用 `IBody2.GetBodyBox` / `GetBodies2` **回读**，★ **不用**它回的 `IFeat"
            "ure` 指针 ✓ ★★ **官方 Remarks 的坑已编码**：**平移与旋转不能同时生效**，**同时给则只应用旋转** ⇒ 本工具检"
            "测到两者都给时**置 `both_given=True` 并写明**（★ 不静默）✓ ★ **mark 不在 `Select2` 的形参里** —— 它设在 `I"
            "SelectData` 对象上 （官方示例调用序：`CreateSelectData` → `Mark = 1` → `body.Select2(True, data)`）✓ ★★ **"
            "单位是个坑，且本工具已按实测定死**：官方页**没写**这几个长度参数的单位，真机实测**按文档长度单位（本机 mm"
            "）解释、不是米** —— 传 25 就挪 25 mm；★ 因此本工具**原样收毫米、不做换算**（⚠ 与本仓绝大多数 COM 几何接口*"
            "*相反**）✓ ★ 角度则收**度**、在边界换算成**弧度**（真机实测 COM 侧是弧度）—— ★ 也就是说**同一个调用里长度"
            "是 mm、角度是 rad** ✓ ★★ **还有一件官方没写的事**：**参数名与实际作用轴不一致（`RotAngleX` 实际绕 Z、`RotA"
            "ngleZ` 实际绕 X，`Y` 是对的）** —— 真机由「只给一个角、看哪一轴跨度不变」的三格互证定出 ⇒ ★ 本工具**已按单"
            "源常量 `ROTATION_AXIS_MAP` 补偿**，对外的 `rotate_angle_x/y/z_deg` **含义就是「绕该轴转」** ✓ ⚠ **已知限制"
            "**：★ 只验了**单实体 / 全部实体**两种选择器；★ 旋转只验了「**只给一个轴、30°、RotPoint=(0,0,0)**」（★ **三"
            "轴同时给的合成顺序未验**）；★ 非原点旋转与「绕选定参考实体」（mark 2/4/8）**未验**。"
        ),
        doc=(
            "Move or copy solid bodies by translation and rotation about a point, for all bodies or one body index. Mod"
            "ifies the body set: a translate displaces the body, a copy adds bodies, and translation and rotation do no"
            "t both take effect, with rotation winning when both are given."
        ),
    ),
]
