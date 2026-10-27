# ── 24h 计划 段 6 续（Spec Kit `166` 的批次声明）：**曲面特征（第一条）** ─────────────
# ─
# ★★★★★ 2026-10-01（轮 308）真机（`output/surface-feature-evidence.json`）：
# · ★★ **通过**：`create_extruded_surface_report(doc, 10.0)` ⇒ **`曲面-拉伸1`** · 特征树
#  `6 → 7` · 22 参
#   · ★ **负例通过**：`depth_mm=-5.0` ⇒ **显式拒绝**
#   · ⚠ **未通过**：`through_all=True` ⇒ 特征树 `7 → 7`（★ **没建成**）——
# ★ **如实标"未通过"**，★ 且**不猜参数**（★ `swEndConditions_e` 的取值要查了再改，铁律 4
# ）。
# ★★ **本批为什么重要**：★ 它把「**不做曲面族**」那条结论拆成两半 ——
#   ★ `IModeler.Create*Surface`（造**曲面体**）**仍然不做**（事实 40 成立）；
#   ★★ `IFeatureManager.FeatureExtruRefSurface3`（建**曲面特征**）**做了，且真机通过**。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch45.py —— 本文件
# 定位:   段 6 续：把 `sw_surface_features` 的「曲面-拉伸」包装挂成 MCP 工具。
# 官方签名依据: `C:\swapi\types\IFeatureManager\FeatureExtruRefSurface3.md`（22 参 · 回
# void）·
#   `scripts/sw_api_sldworks.py:4300`（反射 arity 22）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

SPECS_BATCH45 = [
    ToolSpec(
        name="solidworks_surface_create_extruded",
        title="Create Extruded Surface Feature",
        module="sw_surface_features",
        function="create_extruded_surface_report",
        inject="model",
        params=[
            Param(
                "depth_mm",
                float,
                description="Extrude depth in millimetres; the conversion to metres happens once at this boundary.",
            ),
            Param(
                "sketch_name",
                str,
                default="",
                description="Name of the sketch to extrude; empty uses the current sketch. Defaults to empty.",
            ),
            Param(
                "through_all",
                bool,
                default=False,
                description=(
                    "Whether to extrude through all geometry instead of the given depth; this mode is not verified and "
                    "the feature tree did not change on a real machine. Defaults to false."
                ),
            ),
        ],
        evidence=(
            "★ **用已有草图建「曲面-拉伸」特征** —— 走 `IFeatureManager.FeatureExtruRefSurface3`（官方 **22 个参数** · "
            "★★ **返回 `void`**）。★★ 判据**不是返回值**，而是「**特征树真的多了**」（规则 6：不静默成功）。★ 真机证据"
            "：10 mm 深度 ⇒ 建成 `曲面-拉伸1`（树 6→7）· 负例 `-5.0` ⇒ 显式拒绝。⚠ 与 `sw_surface.py` 的「`IModeler.Cre"
            "ate*Surface` 造曲面**体**」是**两条不同的路** ——后者在本机返回值跨次都变（事实 40），本条**不走那条**。"
        ),
        doc=(
            "Create a surface extrude feature from an existing sketch of the active part. Writes a surface feature and "
            "does not save; success is judged by the feature tree growing, because the call returns nothing."
        ),
    ),
]

# ── 24h 计划 段 6 续（Spec Kit `166` 续的批次声明）：**缝合曲面** ─────────────────────
# ─
# ★★★★★ 2026-10-01（轮 309）真机（`output/surface-knit-evidence.json`）**PASS 2/2**：
#   · ★★ `knit_surfaces_report(doc, 0.0001)` ⇒ **新特征 `曲面-缝合1`** · 选中 **8** 张面 ·
#     **body `2 → 1`** ✓（★ 判据两条都要 —— 规则 6）
#   · ★ 负例：容差 `5.0` ⇒ **显式拒绝**，★ 并**列出官方上下限**（0.0001 ～ 0.1 mm）
# ★★ **对应四家缺口名 `knit_surfaces`**。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch45.py —— 追加本声明
# 定位:   段 6 续：把 `sw_surface_features.knit_surfaces_report` 挂成 MCP 工具。
# 官方签名依据: `C:\swapi\types\IFeatureManager\InsertSewRefSurface.md`
#   （5 参 · Remarks：mark = 1 · 容差 0.0001–0.1 mm）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────

_SPEC_KNIT = ToolSpec(
    name="solidworks_surface_knit",
    title="Knit Selected Surfaces",
    module="sw_surface_features",
    function="knit_surfaces_report",
    inject="model",
    params=[
        Param(
            "knit_tolerance_mm",
            float,
            default=0.0001,
            description="Knit tolerance in millimetres; the valid range is 0.0001 to 0.1. Defaults to 0.0001.",
        ),
        Param(
            "try_to_form_solid",
            bool,
            default=False,
            description="Whether to turn the knitted surface into a solid when possible. Defaults to false.",
        ),
    ],
    evidence=(
        "★ **把曲面缝成一张** —— 走 `IFeatureManager.InsertSewRefSurface`（官方 **5 参**）。★ 官方 Remarks：选中项要 **"
        "selection mark = 1**，而**缝合容差的有效范围是 0.0001 ～ 0.1 mm**。★★ 判据（规则 6）：**特征树多出新特征** **"
        "且** **body 数变少**（真机：`曲面-缝合1` · 2→1）。★ 它按**对象**选面（实体没有名字 —— 事实 32），★ 选中数**回"
        "读** `GetSelectedObjectCount2(-1)`（★ 不信返回值 —— 事实 8）。"
    ),
    doc=(
        "Join the selected surfaces of the active part into one surface body. Writes a knit feature and does not save; "
        "the selected faces need selection mark 1, and success means the feature tree grew and the body count dropped."
    ),
)

SPECS_BATCH45 = SPECS_BATCH45 + [_SPEC_KNIT]

# ── 24h 计划 段 6 续（objective② 的真缺之一）：**延伸曲面** ───────────────────────────
# ─
# ★★★★ 2026-10-02（轮 386）真机（`output/extend-surface-evidence.json`）**PASS**：
#   · ★ 前置 `曲面-拉伸1`（树 6→7）；★ 负例 `distance_mm = 0` ⇒ **显式拒绝**
# · ★★ `insert_extend_surface_report(doc, 10.0)` ⇒ **新特征 `曲面-延伸1`** · 选 4 张面 ·
#  树 **7→8** ✓
# ★★ **对应四家缺口名 `extend_surface`**（★ objective② 重核后确认的真缺 —— 事实 302/303
# ）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch45.py —— 追加本声明
# 定位:   把 `sw_surface_features.insert_extend_surface_report` 挂成 MCP 工具。
# 官方签名依据: `C:\swapi\types\IModelDoc2\InsertExtendSurface.md`
# （3 参：`bool ExtendLinear` / `int EndCondition`（0=按距离 · 1=到选定点）/ `double Dis
# tance`；
#    ★ 回 `void` ⇒ 判据只能是特征树）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────

_SPEC_EXTEND = ToolSpec(
    name="solidworks_surface_extend",
    title="Extend Surface Feature",
    module="sw_surface_features",
    function="insert_extend_surface_report",
    inject="model",
    params=[
        Param(
            "distance_mm",
            float,
            description="Extension distance in millimetres; zero is rejected.",
        ),
        Param(
            "extend_linear",
            bool,
            default=True,
            description="Whether to extend linearly instead of following the same curved surface. Defaults to true.",
        ),
        Param(
            "end_condition",
            int,
            default=0,
            description=(
                "Extension end condition, where 0 uses the given distance and 1 extends to a selected point, which is n"
                "ot verified. Defaults to 0."
            ),
        ),
    ],
    evidence=(
        "★ **延伸曲面** —— 走 `IModelDoc2.InsertExtendSurface`（官方 **3 参** · ★★ **返回 `void`**）。★★ 判据**不是返回"
        "值**，而是「**特征树真的多了**」（规则 6）。★ 真机证据：10 mm ⇒ 建成 `曲面-延伸1`（树 7→8）· 负例 `distance_mm"
        " = 0` ⇒ 显式拒绝。⚠ **不选面它也能成**（它自己会找面）—— 真机实测，★ 故 `faces_selected = 0` 不构成失败。⚠ `en"
        "d_condition = 1`（延伸到选定点）**未真机验证**。⚠ 与 `sw_surface.py` 的 `create_revolution_surface` 那族**不是"
        "一回事** ——那族是 `IModeler.Create*Surface`（造曲面**体**，事实 40 返回值不可靠），本条造的是**曲面特征**。"
    ),
    doc=(
        "Extend a surface of the active part by a distance along or beyond its own shape. Writes an extend feature and "
        "does not save; success is judged by the feature tree growing, because the call returns nothing."
    ),
)

SPECS_BATCH45 = SPECS_BATCH45 + [_SPEC_EXTEND]

# ── 24h 计划 段 6 续（objective② 的第二个真缺）：**填充曲面** ─────────────────────────
# ─
# ★★★★★ 2026-10-02（轮 388）真机（`output/fill-surface-evidence.json`）**PASS**：
#   · ★ 前置 `曲面-拉伸1`（树 6→7）；★ 负例 `resolutions = 9` ⇒ **显式拒绝**
# · ★★ `insert_fill_surface_report(doc, 2)` ⇒ **新特征 `曲面填充1`** · 选 4 条边 · 树 **
# 7→8** ✓
# ★★ **两个关键细节**（★ 真机撞出来的）：★ 边界边必须用 `SelectByID2` 带 **mark = 1**
# （★ `Select4` **没有 mark 参数** —— 事实 32；★ 传 mark = 4 会**静默失败**：回 true 而
# 计数 0 —— 事实 8）·
#   ★ `Options = 1`（`swOptimizeSurface`，★ 与官方示例一致）。
# ★★ **对应四家缺口名 `filled_surface`**（★ objective② 重核后确认的真缺 —— 事实 302/304
# ）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch45.py —— 追加本声明
# 定位:   把 `sw_surface_features.insert_fill_surface_report` 挂成 MCP 工具。
# 官方签名依据: `C:\swapi\types\IFeatureManager\InsertFillSurface2.md`（**6 参** · mark
# 表 ·
# `Resolutions` = 1/2/3）· `C:\swapi\enums\swFeatureFillSurfaceOptions_e.md`（★ Bitmask
# ，
#   `swOptimizeSurface = 1`，★ md 表与反射两源一致）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────

_SPEC_FILL = ToolSpec(
    name="solidworks_surface_fill",
    title="Fill Surface Feature",
    module="sw_surface_features",
    function="insert_fill_surface_report",
    inject="model",
    params=[
        Param(
            "resolutions",
            int,
            default=2,
            description=(
                "Surface resolution, one of 1, 2 or 3, where a higher value gives a better quality patch. Defaults to 2"
                "."
            ),
        ),
        Param(
            "options",
            int,
            default=1,
            description=(
                "Bitmask of swFeatureFillSurfaceOptions_e flags. Defaults to 1, which is the optimize-surface flag."
            ),
        ),
        Param(
            "selection",
            str,
            default="",
            description=(
                "Declarative selection of the boundary edge loop to fill; leaving it empty picks the highest loop autom"
                "atically. Defaults to empty."
            ),
        ),
    ],
    evidence=(
        "★ **填充曲面** —— 走 `IFeatureManager.InsertFillSurface2`（官方 **6 参**）。★★ 判据（规则 6）：**回 `Feature` "
        "非 None** **且** **特征树增量非空**。★ 真机证据：建 `曲面填充1`（树 7→8）· 负例 `resolutions = 9` ⇒ 显式拒绝。"
        "★★ **边界边按中点 + `mark = 1` 选**（★ 官方 Remarks；`Select4` 没有 mark 参数 —— 事实 32；传 mark = 4 会静默失"
        "败：回 true 而计数 0 —— 事实 8）。★★ 2026-10-03（轮 435）**两条路都已真机 PASS**：★ 各建成 `曲面填充1`（树 [7,"
        "8]）。★ 而**选边时请用 `mark = 1`**（官方 Remarks：边界边用 mark 1）。★ 留空 `selection` 时**自动取最高那一圈*"
        "*（★ 保留原行为）。"
    ),
    doc=(
        "Create a surface patch over a closed boundary of the active part. Writes a fill surface feature and does not s"
        "ave; boundary edges must be selected with mark 1, and success needs both a returned feature and a bigger featu"
        "re tree."
    ),
)

SPECS_BATCH45 = SPECS_BATCH45 + [_SPEC_FILL]
