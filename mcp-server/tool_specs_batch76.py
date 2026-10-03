"""★ 覆盖面缺口批（第四批）：把**已真机证明、却只在探针里**的直入法挂成工具（本批：装饰螺纹线）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层）· 规格 `specs/202-user-coverage-gaps` 的 **R6+**。
# 文件:   mcp-server/tool_specs_batch76.py
# 定位:   ★★ **本批与前几批都不同的一种形态**（★ 值得单独记）：
#   · batch72：接的是「AST 量出**已有实现**」的；
#   · batch73：接的是「**本仓一个都没有**」的（先写了能力层）；
#   · batch75：接的是「**早实现了、只是没挂**」的（转接既有 subskill）；
#   · ★ **本批**：接的是「**已经真机建成过、代码却只留在 `tools/prove_*.py` 探针里**」的。
#     ★ 判据逐字来自 `specs/202-user-coverage-gaps/recon/scan-S2b-ledger-vs-tools.md` 的 **A 表**
#       （台账有、`mcp_tools` 无挂 —— 41 条），★ 而它的 `limitations` 里**自己写着**
#       「⚠ **本包装未接进 MCP 工具层**」⇒ ★ 挂出来就是**台账写明的下一步**。
#   ★★ **不发明**：能力层的调用序**照抄那次建成的真机探针**（`tools/prove_cosmetic_thread.py`）。
#
#   ==========================  ==========================================  ==================
#   覆盖率项                     工具名                                       计数关键词（逐字）
#   ==========================  ==========================================  ==================
#   特征/螺纹                    solidworks_feature_cosmetic_thread            thread
#   ==========================  ==========================================  ==================
#   ★ 关键词逐字取自 `D:\SW-coverage-tool\gen_user_feature_coverage.py`。
#
#   官方依据: `C:\swapi\types\IFeatureManager\InsertCosmeticThread3.md`（**7 参**、未废弃）·
#     `ISurface.IsCylinder()`（★ 官方判形方法）
#   许可:   本仓库 MIT。★ **无第三方代码引入**。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from tool_registry import Param, ToolSpec

_MODULE = "sw_feature_entry_ops"

_BATCH76: list[ToolSpec] = [
    ToolSpec(
        name="solidworks_feature_cosmetic_thread",
        title="Cosmetic Thread (insert by cylindrical edge)",
        module=_MODULE, function="insert_cosmetic_thread",
        inject="model",
        params=[
            Param("standard", int, description="螺纹标准：**1 = ANSI Metric**（官方 `Standard`，逐字）。"),
            Param("standard_type", str, description="标准细分（官方 `StandardType`；例子传空串）。"),
            Param("size", str, description="规格串（官方 `Size`；例子传空串）。"),
            Param("diameter_mm", float, description="公称直径（**毫米**）—— ★ 官方 `Diameter` 是 "
                                                    "`System.double` 且**未写单位** ⇒ ★ 本工具收毫米、"
                                                    "**只在边界换算一次**（真机那次传 `0.008` = 8 mm，口径一致）。"),
            Param("end_type", int, description="末端条件（官方 `EndType`）：**0 = Blind**（此时 `depth_mm` 有效）"
                                               "· **2 = Through**。"),
            Param("depth_mm", float, description="深度（**毫米**）—— ★ **仅 Blind 类有效**（官方逐字）。"),
            Param("note", str, description="注释文字（官方 `Note`；例子传空串）。"),
        ],
        doc="★ **装饰螺纹线**：`IFeatureManager.InsertCosmeticThread3`（**7 参** · 官方 md **未标 Obsolete**）。"
            "★★ **官方前置（台账逐字）：选圆柱面的**一条边**（★ 不是那个面）** ⇒ ★ 本工具**自己找**："
            "先用官方 `ISurface.IsCylinder()` 定位圆柱面、取它的第一条边并按 `mark=0` 选中 "
            "⇒ ★ 调用方**不必**先选；★ 找不到圆柱面时**如实报** `preconditions_held=False` + 原因。"
            "★ **判据**：特征树**新增** + 返回对象 `GetTypeName2`（★ 真机建成时是 **`CosmeticThread`**、"
            "名 `装饰螺纹线1`）。"
            "★★ **真机证据**（已建成过，★ 但那是在**探针**里的读数）："
            "`output/cosmetic-thread-evidence.json`（2026-10-03 轮 568，走 `sw_guard`、零弹窗）。"
            "⚠ 经**本工具**的端到端读数**尚未跑** ⇒ ★ 在那之前**不许**把它写成「经工具层已验证」。",
    ),
]

#: ★★ **第 2 条：样条曲线** —— ★ 这一条修掉了**一个从没被发现的真 bug**（见 ToolSpec 的 doc）
_BATCH76.append(
    ToolSpec(
        name="solidworks_sketch_spline",
        title="Sketch Spline (CreateSpline2, VARIANT array)",
        module="sw_part", function="sketch_spline",
        inject="model",
        params=[
            Param("points", list, description="控制点列表 `[[x, y], …]`（**毫米**，★ 至少 2 组 —— "
                                              "官方 Remarks 要求至少两组 X,Y,Z）⇒ ★ 换算只在能力层边界做一次。"),
        ],
        doc="★ **草图样条曲线**：`ISketchManager.CreateSpline2(data, False)`。"
            "★★★ **本条修掉了一个真 bug（★ 且是一处「被误记成架构限制」的假阴性）**："
            "能力层 `scripts/sw_part.sketch_spline` **此前每次都抛**，其 docstring 断言"
            "「**本机实测建不出来**」并把原因归给 **事实 47/68 的 pywin32 架构限制**。"
            "★ 而真因是 **数组的包装形态**：✗ `array.array('d')` ⇒ **静默回 `None`**；"
            "✓ **`VARIANT(VT_ARRAY|VT_R8, 扁平 list)`** ⇒ **建成**（草图段数 0→1）。"
            "★ 证据：`output/spline-with-variant-evidence.json`（四格对照，`form=spline2` ⇒ `ok=true`）。"
            "★★ 而**正解早在本仓**：`scripts/sketch_relations.create_spline:272-273` 逐字写着"
            "「★★★ 必须包 `VARIANT(VT_ARRAY|VT_R8)` —— 裸 list/tuple 会**静默返回 None**（轮 183 实测）」"
            "⇒ ★ **同一个仓里两条路，一条修了、另一条从没跟上**。"
            "★ 前置（**官方 `## Remarks` 逐字**）："
            "「This method creates a spline in the active 2D sketch. "
            "★★ If a sketch is not active, then a new sketch is created.」"
            "⇒ ★★★ **即：★ 没有活动草图时它**会新建一个**、★ 不会失败** ✓"
            "⚠⚠ **2026-10-04（接手轮）更正 —— 这里原来写的是**假引用****"
            "（★ 处置 `JUDGE-C_D_E.md` 🔴 **#5** · `E-6 #1`）："
            "★ 原句逐字「★ 前置（官方 Remarks）：**必须先有活动草图**」· "
            "★★ 而**官方 `CreateSpline2` 写的是**反面**** —— ★ 那一句其实是 "
            "**`ISketchManager.CreateLine` 的 Remarks**，逐字「If a sketch is not active, then the line "
            "is **not created and NULL is returned**.」（★ 我读了两个 md 逐字比对；"
            "★ 另注：`CreateLine2` **不存在**，★ 只有 `CreateLine`）⇒ "
            "★★★ **把 `CreateLine` 的前置搬到 `CreateSpline2` 上、还冠以「官方 Remarks」，"
            "是一处**假引用** —— ★ 它比「没写依据」更坏：★ 后人照它排查会**停在死路上** ✓"
            "⚠ 经**本工具**的端到端读数**尚未跑** ⇒ ★ 在那之前不许写成「经工具层已验证」。",
    )
)

#: ★★ **第 3 条：曲面展平** —— ★ 同形态（真机已建成过、代码只在探针里）
_BATCH76.append(
    ToolSpec(
        name="solidworks_flatten_surface",
        title="Flatten Surface (face mark=1 + anchor mark=16)",
        module=_MODULE, function="create_flatten_surface",
        inject="model",
        params=[
            Param("accuracy_factor", int, description="精度因子（官方第 1 参）：**10 ≥ 精度 ≥ 1**（1 = 最高）；"
                                                      "★ 真机用 **4** 成（台账逐字）。"),
            Param("should_use_tears", bool, description="是否使用撕裂（官方第 2 参）—— ★ 台账标注**未查**，"
                                                        "★ 本工具原样透传。"),
            Param("body_type", str, description="`surface`（默认，取 `GetBodies2(1, …)` 曲面体）"
                                                "或 `solid`（取 `GetBodies2(0, …)`）。"),
        ],
        doc="★ **曲面展平**：`IFeatureManager.InsertFlattenSurface2(AccuracyFactor, ShouldUseTears)`（**2 参**）。"
            "★★★ **官方前置（台账逐字）**：必须选中 **面（mark = 1）** 与 **锚点（mark = 16）**；"
            "★ 另可选 2 = 引导边 · 4 = 映射边 · 8 = 撕裂边。"
            "★★ 台账还逐字记着那组**四格对照**的结论：「**面-only（mark=1）不够**」"
            "⇒ ★ 本工具**自己两个都选**（面按 1、该体第一条边的一个顶点按 16）；"
            "★ 锚点没选上时**如实报** `preconditions_held=False` 并**指明**那正是失败原因。"
            "★ **判据**：特征树**新增** + 返回对象 `GetTypeName2`（★ 真机建成时是 **`FlattenSurface`**、"
            "名 `曲面-展平1`）。"
            "★★ **真机证据（探针级）**：`output/flatten-with-anchor-evidence.json`"
            "（2026-10-03 轮 556，走 `sw_guard`、零弹窗）。"
            "⚠ 经**本工具**的端到端读数**尚未跑** ⇒ ★ 在那之前不许写成「经工具层已验证」。",
    )
)

#: ★★ **第 4 条：加厚 / 加厚切除** —— ★★★ **本条的成员名与前置来自 R4「E 类换名重查」的产出**
#:   （`recon/r4-e-class-rename-lookup.md`）⇒ ★ 两个都**未废弃**、官方 Remarks 给了明确前置。
_BATCH76.append(
    ToolSpec(
        name="solidworks_thicken", 
        title="Thicken / Thicken Cut (FeatureBossThicken | FeatureCutThicken)",
        module=_MODULE, function="thicken_surface",
        inject="model",
        params=[
            Param("thickness_mm", float, description="厚度（**毫米**）—— ★ 官方 `Thickness` 是 `System.double`，"
                                                     "★ 本工具收毫米、**只在边界换算一次**（COM 吃米）。"),
            Param("cut", bool, description="True = **加厚切除**（`FeatureCutThicken`）；"
                                           "False = **加厚凸台**（`FeatureBossThicken`）。"),
            Param("direction", int, description="方向（官方 `Direction`）。"),
            Param("fill_volume", bool, description="★ 官方逐字：「If FillVolume is true, **other arguments are "
                                                   "ignored**. A **closed surface is required** when FillVolume is true.」"),
            Param("merge", bool, description="★ **仅加厚凸台**有此参（官方 `Merge`）。"),
            Param("use_feat_scope", bool, description="官方 `UseFeatScope`。"),
            Param("use_auto_select", bool, description="★ 官方（切减）逐字：「When `UseAutoSelect` is **false**, "
                                                       "the user must **select the bodies** that the feature will affect.」"),
        ],
        doc="★ **加厚 / 加厚切除**：**`IFeatureManager.FeatureBossThicken`（7 参）** / "
            "**`IFeatureManager.FeatureCutThicken`（6 参）** —— ★★ **两个都未废弃**。"
            "★★★ **为什么是这两个成员**（★ 本条的来历）：`IModelDoc2` 那份**同名**成员已废弃"
            "（`FeatureBossThicken2` 头顶逐字：`Superseded by [[IFeatureManager::FeatureBossThicken]].`），"
            "★ 而另一族 `IModeler.ThickenSheet` 造的是**片体、不是特征** ⇒ ★ 入口只有这两个。"
            "★★ **官方前置（Remarks 逐字）**：参考面**必须按 `mark=1` 选中**；"
            "`FillVolume=true` 时**其余参数被忽略**、且**必须闭合曲面**；切减时 `UseAutoSelect=false` "
            "要**先选实体** ⇒ ★ 本工具**自己把第一张面按 `mark=1` 选上**，选不上就**如实报前置**。"
            "★ **判据**：特征树**新增** + 返回对象 `GetTypeName2`（★ 两条都报）。"
            "⚠ **尚未真机验证**（★ 由 `tools/probe_thicken_tool.py` 单独验）⇒ "
            "★ 在那之前不许把它写成 `verified`。",
    )
)

#: ★ 注册器按 `SPECS_*` 找
SPECS_BATCH76 = _BATCH76
