"""★ 覆盖面缺口批（第三批）：钣金斜接法兰 / 闭合角 · 焊件顶端盖 / 角撑板。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层）· 规格 `specs/202-user-coverage-gaps`
# 文件:   mcp-server/tool_specs_batch74.py
# 定位:   ★ 2026-10-03（接手轮）★ 规格 `202-user-coverage-gaps` 的 **T-C2**：钣金/焊件
#            5 项
# **「直入法」**（★ 即"直接调一个方法把特征建出来"，★ 不是 `CreateDefinition`+`CreateFea
# ture`）。
# ★★ 承 `tool_specs_batch72.py`（第一批：接已有实现）与 `batch73.py`（第二批：工程图五项
# 缺口）。
#
# ==============================  ============================================  ========
# ==========
#   缺口项                          工具名                                        官方入口
# ==============================  ============================================  ========
# ==========
# 钣金/斜接法兰                  solidworks_sheet_metal_insert_miter_flange   IFeatureMa
# nager.
#                                                                    InsertSheetMetalMiterFlange
# 钣金/闭合角转折褶边            solidworks_sheet_metal_insert_closed_corner  IModelDoc2
# .
#                                                                    InsertSheetMetalClosedCorner
# 焊件/顶端盖                    solidworks_weldment_insert_end_cap          IFeatureMan
# ager.
#                                                                    InsertEndCapFeature3
# 焊件/角撑板                    solidworks_weldment_insert_gusset           IFeatureMan
# ager.
#                                                                    InsertGussetFeature3
# 曲面/中面                      ★★ **不建 ToolSpec**（理由见文件尾）★★        IFeatureM
# anager.
#                                                                    InsertMidSurface
# ==============================  ============================================  ========
# ==========
#
#   ★★ **本批最核心的产出不是代码，是「废弃链」本身**（★ 铁律 4）—— ★ 逐条查证如下：
#     · `IModelDoc2.InsertSheetMetalMiterFlange`（11 参 · 回 void）**Obsolete**
#       → `IFeatureManager.InsertSheetMetalMiterFlange`（**14 参 · 回 Feature**）
#       ★★ 两份**同名页**、★ **参数个数不同** ⇒ ★ 用错不只是"没反应"，★ 是**个数对不上**。
# · `IFeatureManager.InsertEndCapFeature`（6 参）**Obsolete** → `InsertEndCapFeature3`（
# 10 参）。
#       ⚠ ★★ `InsertEndCapFeature2`（7 参 · 末位 `System.object Faces`）**不在链上** ——
#         官方页**无** Obsolete 句，★ 且 Remarks 明写它是「用 Faces 数组」的**并列**入口
#         ⇒ ★ **不是** `1 → 2 → 3` 线性继承（★ 想当然就会写错入口）。
# · `IFeatureManager.InsertGussetFeature`（15 参）**Obsolete** → **`InsertGussetFeature3
# `**（20 参）。
#       ⚠ ★★ **官方在此断链**：`InsertGussetFeature2` 的页**没有** Obsolete 句
#         ⇒ ★ 第 1 代**直接**指向第 3 代，★ 中间那代的废弃状态**官方没写**。
#     · `IModelDoc2.InsertMidSurfaceExt` / `IInsertMidSurfaceExt` **都 Obsolete**；
#       ★★ 后者点名的后继 **`IFeatureManager::IInsertMidSurface` 官方没写**
# （`C:\swapi\types\` 全库只有 3 个 `*MidSurface*` 页）⇒ ★ **查不到** ⇒ ★ 不顶替（铁律 5
# ）。
#
#   ★★★ **接口别认错**（★ 已知事实 36 的原型，★ 本批的焊件角撑板尤其容易认错）：
#     `IGussetFeatureData`（官方 category = `Feature Interfaces/**Weldments**`，描述逐字
#     "Allows access to a **weldment** gusset feature."，14 属性 / 4 方法）
#     vs `ISMGussetFeatureData`（category = `Feature Interfaces/**Sheet Metal**`，描述逐字
#     "Allows access to a **sheet metal** gusset feature."，28 属性 / 2 方法）
#     ★ ★ 两者共有成员**只有 3 个** ⇒ ★ 用错时**连读都读不到**。
#     ★ 本批的角撑板是**焊件**那个 ⇒ ★ 钣金那个由本仓 `sw_sheet_metal.create_gusset`
#       走 `swFmSMGusset` 那条（★ **另一条路**，★ 不算本项的实现）。
#
#   ★★ **官方前置（逐字来源）—— 已写进各工具 doc 与能力层返回值**：
#     · 斜接法兰 / 闭合角：**官方页无 `## Remarks` 段 ⇒ 前置查不到** ⇒ ★ **不编前置**
#       （铁律 5），★ 能力层如实报 `preconditions_held: None`（★ **不是** `False`）。
# · 顶端盖：「**select one or more end faces** of a structural member in the graphics ar
# ea」
#       ⇒ ★ 官方**没给 mark**，★ 官方例子用的是 mark=**0**。
#     · 角撑板：「**two faces** that are the supporting legs … **with a Mark of 1**」
# ⇒ ★★ **mark=1**，★ 且官方例子两次都 **Append=True** ⇒ ★ 与顶端盖**不一样**，★ 不能套用
# 。
#
# ★★ **单位**（规则 2）：距离官方吃**米**（官方例子 0.005 / 0.025 / 0.0125 ⇒ 5 / 25 / 12
# .5 mm）⇒
#     本工具**对外收 `_mm`**；★ 角度官方吃**弧度**（例子 `0.78539816339745 = π/4 = 45°`）⇒
#     **对外收 `_deg`**；★ 换算**各只在边界做一次**（能力层 `sw_connect.mm` / `deg`）。
#     ⚠ `WallThicknessRatio`（0.6）**是比例量、不换算** ⇒ 见下面那条 `param_alias`。
#
#   官方依据（三源 · 铁律 4）:
#     · `C:\swapi\types\IFeatureManager\InsertSheetMetalMiterFlange.md`（14 参）
#       / `C:\swapi\types\IModelDoc2\InsertSheetMetalMiterFlange.md`（11 参 · **Obsolete**）
# + `C:\swapi\enums\swSheetMetalReliefTypes_e.md` + `C:\swapi\enums\swFlangePositionType
# s_e.md`
#     · `C:\swapi\types\IModelDoc2\InsertSheetMetalClosedCorner.md`（**零参 · 回 void**）
#     · `C:\swapi\types\IFeatureManager\InsertEndCapFeature3.md`（10 参 · **有 Remarks**）
# + `C:\swapi\enums\swEndCapThicknessDirection_e.md`（Outward=0 / Inward=1 / **Inset=2**
# ）
# + `C:\swapi\examples\Insert_Weldment_End_Cap_Example_VB.md`（米制 + mark=0 + `GetDefin
# ition` 读回）
#     · `C:\swapi\types\IFeatureManager\InsertGussetFeature3.md`（20 参 · **mark=1 逐字**）
# + `C:\swapi\enums\swGussetThicknessType_e.md` + `C:\swapi\enums\swGussetProfileLocatio
# nType_e.md`
# + `C:\swapi\examples\Insert_Gusset_Feature_Example_VB.md`（Append=True + mark=1 + 弧度
# /米制佐证）
#     · `C:\swapi\types\IFeatureManager\InsertMidSurface.md`（4 参 · 前两位是**对象形参**）
#     · ★ arity 与官方签名**逐条互证**（反射 dump `scripts/sw_api_sldworks.py`，第三源）：
#       `14 / 0 / 10 / 20 / 4` ✓✓✓✓✓
#   许可:   本仓库 MIT。★ **无第三方代码引入**。
#   覆盖:   全文件
# ⚠ 本批为**静态签名比对后新写**，**未在本机实测**（铁律 2：真机由 Lead 独家执行）。
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from tool_registry import Param, ToolSpec

#: ★★ 本批 5 项里**只有 4 项**在这里声明（第 5 项「曲面/中面」的**前两个形参是对象** ⇒ `
#: Param` 表达不了
#: ★ ⇒ 见文件尾那段理由）；★ 模块名在这里**只出现一次**，★ 便于 grep 核对。
_MODULE = "sw_sheet_metal_weld_entry"


#: ★★★ 2026-10-03（接手轮）**`pre_call` 选面 —— 本批两条焊件工具的前置必须这样做**。
#:   ★★ **为什么不能用"调用方预先选择"**（★ 单变量真机隔离出来的，证据
#:     `output/selection-lifetime-evidence.json`）：
#:     注册器的顺序是 `kwargs[inj] = resolver(params)` → `pre_call(params)` → `fn(**kwargs)`
#:     （`tool_registry.py:507/510/525`），★ 而 **`RESOLVERS["model"]` 会经
#:     `connect_solidworks()` 清空选区** —— 实测：选完 2 个面 `mark1=2`，
#:     ★ **调过 `RESOLVERS['model']` 之后变成 `mark1=0`**。
#:     ⇒ ★★ 于是"指望调用方预选"的工具**经工具层永远拿不到选区**
#:       （★ 而 MCP 客户端本来也没法预选）。
#:   ★ **正确形态照本仓既有先例**：`solidworks_fillet` / `solidworks_chamfer` 用的是
#: `pre_call=_select_edge` —— ★ 在 `pre_call`（= 注入**之后**）解析成真实选区 ⇒ **能存活
#: **。
#: ★ 官方 mark（逐字）：顶端盖「select one or more **end faces**」**没给 mark**（官方例
#: 子用 **0**）；
#:     角撑板「**two faces** … with a **Mark of 1**」。
def _select_faces_for(mark: int, count: int):
    """★ 造一个 `pre_call`：调目标函数前按官方 mark 选 `count` 个面。

    ★ 判据用**回读计数**（★ 事实 8：`Select4` 的 bool 返回值不可信）——
      ★ 没选够就**抛**（★ 不静默地把前置未成立当成能力不成）。
    """

    def _pick(params):  # noqa: ANN001, ARG001
        import register_capabilities as _rc

        from scripts.sw_connect import get_com_member
        from scripts.sw_part import _select_com_object

        model = _rc.RESOLVERS["model"](None)  #: ★ 与注册器取同一个对象
        try:
            get_com_member(model, "ClearSelection2", True)
        except Exception:  # noqa: BLE001
            pass
        sm = get_com_member(model, "SelectionManager")
        picked = 0
        for body in list(get_com_member(model, "GetBodies2", 0, True) or []):
            for face in list(get_com_member(body, "GetFaces") or []):
                if picked >= count:
                    break
                try:
                    _select_com_object(face, append=(picked > 0), mark=mark)
                    got = int(get_com_member(sm, "GetSelectedObjectCount2", mark) or 0)
                    if got > picked:
                        picked = got
                except Exception:  # noqa: BLE001
                    continue
            if picked >= count:
                break
        if picked < count:
            raise RuntimeError(
                "★ 前置未成立：按 mark=%d 只选上 %d/%d 个面（官方要求的面没备齐）"
                % (mark, picked, count)
            )
        return picked

    return _pick


_BATCH74: list[ToolSpec] = [
    ToolSpec(
        name="solidworks_sheet_metal_insert_miter_flange",
        title="Sheet Metal Miter Flange",
        module=_MODULE,
        function="insert_sheet_metal_miter_flange",
        inject="model",
        param_alias={
            "use_default_radius": "use_default_radius",
            "global_radius_mm": "global_radius_mm",
            "rip_gap_mm": "rip_gap_mm",
            "use_default_relief": "use_default_relief",
            "use_relief_ratio": "use_relief_ratio",
            "relief_ratio": "relief_ratio",
            "relief_width_mm": "relief_width_mm",
            "relief_depth_mm": "relief_depth_mm",
            "relief_type": "relief_type",
            "trim_side_bends": "trim_side_bends",
            "flange_pos": "flange_pos",
            "offset_dist1_mm": "offset_dist1_mm",
            "offset_dist2_mm": "offset_dist2_mm",
        },
        params=[
            Param(
                "use_default_radius",
                bool,
                default=True,
                description="官方逐字「True to use **default bend radius**, false to use GlobalRadius」。",
            ),
            Param(
                "global_radius_mm",
                float,
                default=0.0,
                description="全局折弯半径（**毫米**）—— ★ 仅 `use_default_radius=False` 时有意义。"
                "★ 官方**没给单位**；本工具按 SolidWorks 惯例当**米**、边界换算一次。",
            ),
            Param(
                "rip_gap_mm",
                float,
                default=0.0,
                description="切口间隙（**毫米**；★ 单位约定同 `global_radius_mm`）。",
            ),
            Param(
                "use_default_relief",
                bool,
                default=True,
                description="官方逐字「True to use **parent bend's ratio**」。",
            ),
            Param(
                "use_relief_ratio",
                bool,
                default=False,
                description="True 用**自定义让位比**、False 不用（官方 `UseReliefRatio`）。",
            ),
            Param(
                "relief_ratio",
                float,
                default=0.0,
                description="让位比 —— ★ **比例量、不换算**（官方逐字「If useReliefRatio is True, "
                "then specify relief ratio」⇒ 官方例子是 `0.6` 那类无量纲值）。",
            ),
            Param(
                "relief_width_mm",
                float,
                default=0.0,
                description="★ 官方对 `ReliefWidth` 与 `ReliefDepth` **写的是同一句**"
                "「…specify relief **depth**」⇒ ★ **官方这两句自相矛盾** ⇒ 本工具"
                "**原样透传、不替官方调和**（铁律 5）。★ 仅当 `use_relief_ratio=True` "
                "且 `relief_type` ∈ {Rectangular, Obround} 时有意义。",
            ),
            Param(
                "relief_depth_mm",
                float,
                default=0.0,
                description="让位深度（**毫米**）—— ★ 与 `relief_width_mm` 同一条官方矛盾。",
            ),
            Param(
                "relief_type",
                int,
                default=1,
                description="官方 `swSheetMetalReliefTypes_e`（逐字核官方枚举页）："
                "**1=Rectangular · 2=Tear · 3=Obround · 4=None · 5=TearBend**。",
            ),
            Param(
                "trim_side_bends",
                bool,
                default=False,
                description="官方 `TrimSideBends` —— True 裁剪侧折弯。",
            ),
            Param(
                "flange_pos",
                int,
                default=1,
                description="官方 `swFlangePositionTypes_e`：**1=MaterialInside · 2=MaterialOutside · "
                '3=BendOutside · 4=BendCenterLine · 5=BendSharp（"Bend from virtual sharp"）'
                ' · 6=BendTangent**。⚠ 官方注明 **BendTangent** 对 "Up To Edge And Merge" '
                "长度终止条件**无效**。",
            ),
            Param(
                "offset_dist1_mm",
                float,
                default=0.0,
                description="部分法兰的**起始**偏移距离（**毫米**）。",
            ),
            Param(
                "offset_dist2_mm",
                float,
                default=0.0,
                description="部分法兰的**结束**偏移距离（**毫米**）。",
            ),
        ],
        evidence=(
            "★ **钣金斜接法兰**：`IFeatureManager.InsertSheetMetalMiterFlange(14 参)` → `Feature`。★★★ **同名两份页、★ "
            "参数个数不同**：★ `IModelDoc2` 那份（11 参 · 回 void）官方逐字标 `Obsolete. Superseded by [[IFeatureManage"
            "r::InsertSheetMetalMiterFlange]].` ⇒ ★ **本工具走 IFeatureManager 那份**，★ 而用错的后果是**参数个数对不上"
            "**、★ 不只是「没反应」。⚠ 末位 `PCBA` 是**对象形参**：★ 官方把它写成二选一 —— **non-NULL** ⇒ \"Pointer to "
            "`ICustomBendAllowance` object **for which required values have been set**\"；**NULL** ⇒ \"Parent bend's be"
            "nd allowance is used\" ⇒ ★ 本工具传**空 Dispatch**（＝ NULL 语义）★★ **不伪造一个没设过必需值的 PCBA**，★ "
            "因此**不接受自定义 PCBA**。★★ **前置查不到**：★ 该官方页**无 `## Remarks` 段**（逐字段核过）⇒ ★ 本工具**不"
            "编前置**（铁律 5），★ 只回读选区计数、★ `preconditions_held` 如实报 **None**（★ 不是 False）。★ 判据 = **"
            "特征树增量** + 返回对象非 None + **实体面数增量**（三个都要）。"
        ),
        doc="★ **钣金斜接法兰**：`IFeatureManager.InsertSheetMetalMiterFlange(14 参)` → `Feature`。"
        "★★★ **同名两份页、★ 参数个数不同**：★ `IModelDoc2` 那份（11 参 · 回 void）官方逐字标 "
        "`Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalMiterFlange]].` ⇒ ★ **本工具走 "
        "IFeatureManager 那份**，★ 而用错的后果是**参数个数对不上**、★ 不只是「没反应」。"
        '⚠ 末位 `PCBA` 是**对象形参**：★ 官方把它写成二选一 —— **non-NULL** ⇒ "Pointer to '
        '`ICustomBendAllowance` object **for which required values have been set**"；'
        '**NULL** ⇒ "Parent bend\'s bend allowance is used" ⇒ ★ 本工具传**空 Dispatch**'
        "（＝ NULL 语义）★★ **不伪造一个没设过必需值的 PCBA**，★ 因此**不接受自定义 PCBA**。"
        "★★ **前置查不到**：★ 该官方页**无 `## Remarks` 段**（逐字段核过）⇒ ★ 本工具**不编前置**"
        "（铁律 5），★ 只回读选区计数、★ `preconditions_held` 如实报 **None**（★ 不是 False）。"
        "★ 判据 = **特征树增量** + 返回对象非 None + **实体面数增量**（三个都要）。",
    ),
    ToolSpec(
        name="solidworks_sheet_metal_insert_closed_corner",
        title="Sheet Metal Closed Corner",
        module=_MODULE,
        function="insert_sheet_metal_closed_corner",
        inject="model",
        params=[],
        evidence=(
            "★ **钣金闭合角**：`IModelDoc2.InsertSheetMetalClosedCorner()` → **`void`**（★ **零参**）。⚠⚠★ **这是本批判"
            "据最紧的一条**，★ 因为官方**同时**给了「零参数」与「回 `void`」：⇒ ★ **没有返回对象可读** ⇒ ★「返回非 None"
            "」这条判据在本工具上**根本不存在** ⇒ ★ 判据**只能**是 **特征树增量** + **实体面数增量** + **体积增量**（★ "
            "后两个互相独立、缺一不可）。★★ **前置查不到**：★ 官方页**无 `## Remarks` 段** ⇒ ★ 本工具**不编前置**（铁律"
            " 5），★ 只回读选区计数、★ `preconditions_held` 如实报 **None**。⚠ 该族另有 `IClosedCornerFeatureData` 指针"
            "路：★ 其 `IAccessSelections` 官方已标 `Obsolete` → 后继 `IAccessSelections2`；★ ★ 而该族是**进程内指针接口"
            "**，★ 本仓 pywin32 后端到不了（已知事实 47）⇒ ★ 本工具**只走直入法**、★ 不碰指针族。"
        ),
        doc="★ **钣金闭合角**：`IModelDoc2.InsertSheetMetalClosedCorner()` → **`void`**（★ **零参**）。"
        "⚠⚠★ **这是本批判据最紧的一条**，★ 因为官方**同时**给了「零参数」与「回 `void`」："
        "⇒ ★ **没有返回对象可读** ⇒ ★「返回非 None」这条判据在本工具上**根本不存在** ⇒ ★ 判据**只能**是 "
        "**特征树增量** + **实体面数增量** + **体积增量**（★ 后两个互相独立、缺一不可）。"
        "★★ **前置查不到**：★ 官方页**无 `## Remarks` 段** ⇒ ★ 本工具**不编前置**（铁律 5），"
        "★ 只回读选区计数、★ `preconditions_held` 如实报 **None**。"
        "⚠ 该族另有 `IClosedCornerFeatureData` 指针路：★ 其 `IAccessSelections` 官方已标 "
        "`Obsolete` → 后继 `IAccessSelections2`；★ ★ 而该族是**进程内指针接口**，"
        "★ 本仓 pywin32 后端到不了（已知事实 47）⇒ ★ 本工具**只走直入法**、★ 不碰指针族。",
    ),
    ToolSpec(
        name="solidworks_weldment_insert_end_cap",
        title="Weldment End Cap",
        module=_MODULE,
        function="insert_weldment_end_cap",
        #: ★ 官方「select one or more end faces」· 没给 mark（例子用 0）
        pre_call=_select_faces_for(0, 1),
        inject="model",
        param_alias={
            "depth_mm": "depth_mm",
            "is_given_offset": "is_given_offset",
            "is_chamfer": "is_chamfer",
            "offset_value_mm": "offset_value_mm",
            # ★★ 官方形参名是 `WallThicknessRatio`，★ 但它是**比例量（0.6）不是
            # 长度** ——
            # ★ 而 `tool_registry` 规则 2 按子串扫 `thickness` 会要求 `_mm` 后
            # 缀 ⇒
            # ★ 加 `_mm` 就是**说错话**（门禁自己的注记原话）。⇒ ★ 对外用 `wall
            # _ratio`，
            # ★ ★ 用 `param_alias` 显式指回真形参 `wall_thickness_ratio`
            # ★ （`ToolSpec.param_alias` 的用途逐字就是「MCP 表面…比…合规（规则
            #  2），
            # ★ 而实现里的名字不该为了对外好看去改」）。
            "wall_ratio": "wall_thickness_ratio",
            "chamfer_value_mm": "chamfer_value_mm",
            "is_corner_treatment": "is_corner_treatment",
            "depth_offset_mm": "depth_offset_mm",
            "is_reverse": "is_reverse",
            "is_end_cap_inward": "is_end_cap_inward",
        },
        params=[
            Param(
                "depth_mm",
                float,
                description="顶端盖厚度（**毫米**；★ 官方未给单位，按米收、边界换算一次）。",
            ),
            Param(
                "is_given_offset",
                bool,
                default=False,
                description="官方逐字「True to provide an **offset value**, false to provide a "
                "**thickness ratio**」⇒ ★ 它决定下面两个形参**哪一个有效**。",
            ),
            Param(
                "is_chamfer",
                bool,
                default=False,
                description="官方逐字「True if end cap feature is **chamfered**, false if "
                "**filleted**」⇒ ★ 决定 `chamfer_value_mm` 的含义。",
            ),
            Param(
                "offset_value_mm",
                float,
                default=0.0,
                description="边偏移值（**毫米**；★ 官方逐字「valid **only if** `BIsGivenOffset` "
                "is true」）。",
            ),
            Param(
                "wall_ratio",
                float,
                default=0.0,
                description="壁厚比 —— ★ 对应官方形参 **`WallThicknessRatio`**，★ 是**比例量**"
                "（官方例子 `0.6`）⇒ **不换算**。⚠ ★ 官方形参名含 `Thickness`，"
                "★ 而本工具**故意不叫** `wall_thickness_*`：★ 规则 2 的长度词表里有 "
                "`thickness`、★ 会要求 `_mm` 后缀，★ 而给一个**比例量**加 `_mm` 是"
                "**说错话** ⇒ ★ 故对外叫 `wall_ratio`、★ 由 `param_alias` 指回真形参。",
            ),
            Param(
                "chamfer_value_mm",
                float,
                default=0.0,
                description="倒角距离（`is_chamfer=True`）/ 圆角半径（`False`）（**毫米**）。",
            ),
            Param(
                "is_corner_treatment",
                bool,
                default=False,
                description="官方逐字「…chamfer or fillet the end cap corners … valid **only if** "
                "`BIsGivenOffset` is false」。",
            ),
            Param(
                "depth_offset_mm",
                float,
                default=0.0,
                description="内插距离（**毫米**）—— ★ 官方逐字「valid **only if** `BIsEndCapInward` "
                "**= 2**」⇒ ★ 与枚举 `swSpecifyInset = 2` **对得上**"
                "（★ 官方例子也确实传 `2`）✓。",
            ),
            Param(
                "is_reverse",
                bool,
                default=False,
                description="官方 `BIsReverse` —— 反转偏移或厚度比。",
            ),
            Param(
                "is_end_cap_inward",
                int,
                default=0,
                description="官方 `swEndCapThicknessDirection_e`：**0=swExtendOutward · "
                "1=swExtendInward · 2=swSpecifyInset**（★ 逐字核官方枚举页）。",
            ),
        ],
        evidence=(
            "★ **焊件顶端盖**：`IFeatureManager.InsertEndCapFeature3(10 参)` → `IFeature`。★★★ **官方前置（Remarks 逐字"
            "）**：\"Before calling this method, **select one or more end faces** of a structural member in the graphic"
            "s area.\" ⇒ ★ 调用前必须在图形区选中端面；★ 本工具**不代选**（★ 面没有可用名字 —— 已知事实 32；★ 且规则 3 "
            "禁裸坐标），★ 只**回读选区计数**写进 `preconditions_held`。★ ★ 官方**这一句没给 mark**，★ 官方例子用的是 m"
            "ark=**0** ⇒ ★ **与角撑板的 mark=1 不一样**，★ 两个入口的 mark 不能互相套用。⚠ ★★ `InsertEndCapFeature2`（7"
            " 参 · 末位 `System.object Faces`）**不是**废弃成员 —— ★ 官方页无 Obsolete 句、★ 且 Remarks 明写它是「用 Fa"
            "ces 数组」的**并列**入口 ⇒ ★★ **不是** `1 → 2 → 3` 的线性继承；★ 而它末位是**数组形参** ⇒ `Param` 表达不了"
            " ⇒ 本工具不做。★ 判据 = **特征树增量** + 返回对象非 None + **`GetDefinition()` 属性回读**（官方例子读法）"
            "。"
        ),
        doc="★ **焊件顶端盖**：`IFeatureManager.InsertEndCapFeature3(10 参)` → `IFeature`。"
        '★★★ **官方前置（Remarks 逐字）**："Before calling this method, **select one or more end '
        'faces** of a structural member in the graphics area." ⇒ ★ 调用前必须在图形区选中端面；'
        "★ 本工具**不代选**（★ 面没有可用名字 —— 已知事实 32；★ 且规则 3 禁裸坐标），"
        "★ 只**回读选区计数**写进 `preconditions_held`。"
        "★ ★ 官方**这一句没给 mark**，★ 官方例子用的是 mark=**0** ⇒ ★ **与角撑板的 mark=1 不一样**，"
        "★ 两个入口的 mark 不能互相套用。"
        "⚠ ★★ `InsertEndCapFeature2`（7 参 · 末位 `System.object Faces`）**不是**废弃成员 —— "
        "★ 官方页无 Obsolete 句、★ 且 Remarks 明写它是「用 Faces 数组」的**并列**入口 ⇒ ★★ "
        "**不是** `1 → 2 → 3` 的线性继承；★ 而它末位是**数组形参** ⇒ `Param` 表达不了 ⇒ 本工具不做。"
        "★ 判据 = **特征树增量** + 返回对象非 None + **`GetDefinition()` 属性回读**（官方例子读法）。",
    ),
    ToolSpec(
        name="solidworks_weldment_gusset_create",
        title="Weldment Gusset (Corner Gusset)",
        module=_MODULE,
        function="insert_weldment_gusset",
        #: ★ 官方「two faces … with a Mark of 1」
        pre_call=_select_faces_for(1, 2),
        inject="model",
        param_alias={
            "depth_mm": "depth_mm",
            "dir_type": "dir_type",
            "loc_type": "loc_type",
            "is_profile": "is_profile",
            "profile_d1_mm": "profile_d1_mm",
            "profile_d2_mm": "profile_d2_mm",
            "profile_d3_mm": "profile_d3_mm",
            "profile_angle_deg": "profile_angle_deg",
            "profile_d4_mm": "profile_d4_mm",
            "offset_reference_plane": "offset_reference_plane",
            "d_profile_offset_mm": "d_profile_offset_mm",
            "crv_index": "crv_index",
            "reverse_dir": "reverse_dir",
            "reverse_face": "reverse_face",
            "use_len_dim": "use_len_dim",
            "profile_d5_mm": "profile_d5_mm",
            "profile_d6_mm": "profile_d6_mm",
            "profile_chamfer_angle_deg": "profile_chamfer_angle_deg",
            "use_len_dim_for_chamfer": "use_len_dim_for_chamfer",
            "need_chamfer_in_gusset": "need_chamfer_in_gusset",
        },
        params=[
            Param("depth_mm", float, description="角撑板厚度（**毫米**）。"),
            Param(
                "dir_type",
                int,
                default=1,
                description="官方 `DirType`（**`System.short`**）—— `swGussetThicknessType_e`："
                "**0=Inner · 1=BothSides · 2=Outer**（★ 官方例子用 1）。",
            ),
            Param(
                "loc_type",
                int,
                default=1,
                description="官方 `LocType`（**`System.short`**）—— `swGussetProfileLocationType_e`："
                "**0=Start · 1=Center · 2=End**（★ 官方例子用 1）。"
                '★ 官方逐字："Location of the reference plane for the **sketch** of the gusset"。',
            ),
            Param(
                "is_profile",
                bool,
                default=False,
                description="官方逐字「True to use a **polygon** profile, false to use a "
                "**triangle** profile」。",
            ),
            Param(
                "profile_d1_mm",
                float,
                default=0.0,
                description="轮廓距离 1（**毫米**）。",
            ),
            Param(
                "profile_d2_mm",
                float,
                default=0.0,
                description="轮廓距离 2（**毫米**）。",
            ),
            Param(
                "profile_d3_mm",
                float,
                default=0.0,
                description="轮廓距离 3（**毫米**）。",
            ),
            Param(
                "profile_angle_deg",
                float,
                default=45.0,
                description="轮廓角（**度**）—— ★ 官方吃**弧度**（★ 例子 `0.78539816339745` = π/4 = 45°），"
                "★ 本工具**边界换算一次**。★ 官方逐字：valid **only if** `BUseLenDim` is "
                "**false**。★ 官方把 `ProfileD1..D4` 的精确语义指向 SOLIDWORKS Help"
                "（「See the SOLIDWORKS Help for more information about profile and chamfer "
                "distances and angles」）⇒ ★ 本工具**不代官方释义**。",
            ),
            Param(
                "profile_d4_mm",
                float,
                default=0.0,
                description="轮廓距离 4（**毫米**）—— ★ 官方逐字：valid **only if** `BUseLenDim` is **true**。",
            ),
            Param(
                "offset_reference_plane",
                bool,
                default=False,
                description="官方 `BOffset` —— 偏置角撑板草图的参考平面。",
            ),
            Param(
                "d_profile_offset_mm",
                float,
                default=0.0,
                description="参考平面的偏置值（**毫米**；官方 `DProfileOffset`）。",
            ),
            Param(
                "crv_index",
                int,
                default=0,
                description="官方 `CrvIndex` —— 「Index of the edge to use if **multiple intersecting "
                "edges** exist」。",
            ),
            Param(
                "reverse_dir",
                bool,
                default=False,
                description='官方 `BReverseDir` —— ★ 官方逐字："**If `BOffset` set to true**, then true '
                'to reverse direction"。',
            ),
            Param(
                "reverse_face",
                bool,
                default=False,
                description="官方 `BReverseFace` —— 三角形轮廓时反转 d1/d2；多边形轮廓时还反转 d3/d4。",
            ),
            Param(
                "use_len_dim",
                bool,
                default=False,
                description="官方 `BUseLenDim` —— True 用 `profile_d4_mm`、False 用 `profile_angle_deg`。",
            ),
            Param(
                "profile_d5_mm",
                float,
                default=0.0,
                description="倒角距离 5（**毫米**）—— ★ 官方逐字：valid **only if** "
                "`BNeedChamferInGusset` is **true**。",
            ),
            Param(
                "profile_d6_mm",
                float,
                default=0.0,
                description="倒角距离 6（**毫米**）—— ★ 官方逐字：valid **only if** "
                "`BNeedChamferInGusset` **and** `BUseLenDimForChamfer` are **both** true。",
            ),
            Param(
                "profile_chamfer_angle_deg",
                float,
                default=45.0,
                description="倒角角（**度**；★ 官方吃**弧度**，★ 边界换算一次）。★ 官方逐字：valid "
                "only if `BUseLenDimForChamfer` is **false** **and** "
                "`BNeedChamferInGusset` is **true**。",
            ),
            Param(
                "use_len_dim_for_chamfer",
                bool,
                default=False,
                description="官方 `BUseLenDimForChamfer` —— True 用 `profile_d6_mm`、"
                "False 用 `profile_chamfer_angle_deg`。",
            ),
            Param(
                "need_chamfer_in_gusset",
                bool,
                default=False,
                description="官方 `BNeedChamferInGusset` —— 逐字「…to allow room for a **weld bead** "
                "under the gusset」。",
            ),
        ],
        evidence=(
            "★ **焊件角撑板**：`IFeatureManager.InsertGussetFeature3(20 参)` → `IFeature`。★★★ **官方前置（Remarks 逐字"
            "，本批最硬的一条）**：\"Before calling this method, you must call `SelectByID2` to select **two faces** th"
            "at are the supporting legs of this gusset **with a Mark of 1**.\" ⇒ ★★ 必须选**两个面**、★ **mark = 1**（★"
            " **不是 0**）；★ ★ 官方例子两次都 **Append=True 且 mark=1** ⇒ ★ 本工具照抄这个组合、★ `preconditions_held`"
            " 判的是「**mark 1 上 ≥ 2 个**」⇒ ★ 调用者能一眼看见「mark 1 上只有 1 个面」这种失败。⚠★ **接口别认错**：★ "
            "这是**焊件**角撑板（`IGussetFeatureData`，官方描述 \"Allows access to a **weldment** gusset feature.\"，14"
            " 属性 / 4 方法）⇒ ★ **不是**钣金那个 `ISMGussetFeatureData`（\"Allows access to a **sheet metal** gusset f"
            "eature.\"，28 属性 / 2 方法）⇒ ★★ 两者共有成员**只有 3 个**、★ 用错时**连读都读不到**（已知事实 36）。⚠ ★★"
            " **官方在废弃链上断了一节**：`InsertGussetFeature`（15 参）**Obsolete** → 直接指向 `InsertGussetFeature3`"
            "；★ 而中间的 `InsertGussetFeature2` 的页**没有** Obsolete 句 ⇒ ★★ **别写「Gusset 三代线性链」** —— ★ 官方*"
            "*没写**中间那代的废弃状态。★ 判据 = **特征树增量** + 返回对象非 None + **实体面数增量** + **mark-1 选区计"
            "数**。"
        ),
        doc="★ **焊件角撑板**：`IFeatureManager.InsertGussetFeature3(20 参)` → `IFeature`。"
        '★★★ **官方前置（Remarks 逐字，本批最硬的一条）**："Before calling this method, you must '
        "call `SelectByID2` to select **two faces** that are the supporting legs of this gusset "
        '**with a Mark of 1**." ⇒ ★★ 必须选**两个面**、★ **mark = 1**（★ **不是 0**）；'
        "★ ★ 官方例子两次都 **Append=True 且 mark=1** ⇒ ★ 本工具照抄这个组合、★ `preconditions_held` "
        "判的是「**mark 1 上 ≥ 2 个**」⇒ ★ 调用者能一眼看见「mark 1 上只有 1 个面」这种失败。"
        '⚠★ **接口别认错**：★ 这是**焊件**角撑板（`IGussetFeatureData`，官方描述 "Allows access to a '
        '**weldment** gusset feature."，14 属性 / 4 方法）⇒ ★ **不是**钣金那个 '
        '`ISMGussetFeatureData`（"Allows access to a **sheet metal** gusset feature."，'
        "28 属性 / 2 方法）⇒ ★★ 两者共有成员**只有 3 个**、★ 用错时**连读都读不到**（已知事实 36）。"
        "⚠ ★★ **官方在废弃链上断了一节**：`InsertGussetFeature`（15 参）**Obsolete** → 直接指向 "
        "`InsertGussetFeature3`；★ 而中间的 `InsertGussetFeature2` 的页**没有** Obsolete 句 ⇒ "
        "★★ **别写「Gusset 三代线性链」** —— ★ 官方**没写**中间那代的废弃状态。"
        "★ 判据 = **特征树增量** + 返回对象非 None + **实体面数增量** + **mark-1 选区计数**。",
    ),
]

#: ★★ **本批**刻意**不给「曲面/中面」建 ToolSpec** —— ★ 不是遗漏，是**形参形态表达不了**
#: ：
#: `IFeatureManager.InsertMidSurface( Body2 PBodyIn, ModelDoc2 PPartDocIn, double Placem
#: ent,
#:   bool KnitFlag )` —— ★ **前两个形参是 COM 对象**，★ 而 `tool_registry.Param` 只能表达
#:   **str / float / int / bool** ⇒ ★ **表达不了**。
#:   ★ 那两个对象也**不该被换成标量**：★ 官方 `## Remarks` 逐字要求它们是
#:   「the **component's model document**」与「the **body of that component**」
#: ⇒ ★ 它们是**身份**，★ 不是可以拿 id / 名字顶替的量（★ 铁律 5：不许用相近的东西代替）
#: 。
#:   ⇒ ★ **能力层已实现**：`scripts/sw_sheet_metal_weld_entry.py::insert_mid_surface`
#: —— ★ 内部照官方 4 参原序传对象，★ 并回读**曲面体数增量**（★ 官方逐字「Each reference
#: surface
#:     is considered a **sheet body**」⇒ ★ 它产出曲面体、★ 实体面数对它没有意义）。
#: ⇒ ★ 将来要暴露它，**正确形态是带 `extra_op` 的 ToolSpec**（`extra_op` 自己解析对象）
#: ，
#:     ★ 而**不是**把对象硬塞进 `Param`（★ 那会把它说成一个它不是的东西）。
#:
#: ★★ 顺带登记**一条本批查到的「查不到」**（铁律 5）：★ `IModelDoc2.IInsertMidSurfaceExt
#: ` 官方逐字标
#: `Obsolete. Superseded by [[IFeatureManager::IInsertMidSurface]].`，★ 而 **`IFeatureMa
#: nager::
#: IInsertMidSurface` 那一页官方没写**（`C:\swapi\types\` 全库只有 3 个 `*MidSurface*`
#: 页）
#: ⇒ ★ **那条链断在这里、无后继签名可抄** ⇒ ★ **不拿**非 `I` 前缀的 `InsertMidSurface`
#: 顶替它。

#: ★ ★★ **第 5 条：中面**（★ 原先因两个对象形参挂不上，本轮补了**按体号解析**的转接层）
#:   据 `recon/scan-S2b-ledger-vs-tools.md` 的 A 表：`surface_midsurface` 这类是
#:   **`level: verified` 却没暴露成工具**的条目 ⇒ ★ 转接层 = `create_midsurface`（同模块，
#:   ★ **不重写实现**，它转调既有 `insert_mid_surface`）。
#: ★ 做法：`body_index` 指体号 ⇒ `IPartDoc.GetBodies2(0, False)` 取体表；`part_doc` 用同
#: 一个 `model`。
#: ⚠⚠ **未真机验证**（★ 与同批其余条目同一纪律）⇒ ★ **在工具层 e2e 给出读数之前不许写 `v
#: erified`**。
_BATCH74.append(
    ToolSpec(
        name="solidworks_surface_midsurface_create",
        title="Surface Mid-Surface (by body index)",
        module=_MODULE,
        function="create_midsurface",
        inject="model",
        params=[
            Param(
                "body_index",
                int,
                description="★ **实体体号**（0 基）—— 由 "
                "`IPartDoc.GetBodies2(0, False)` 取体表后按序号取（★ 参数里**不收对象**）。",
            ),
            Param(
                "placement",
                float,
                description="参考面位置（★ 官方**既没给单位也没给量纲** ⇒ "
                "★ 原样透传、不换算，铁律 5）。",
            ),
            Param(
                "knit",
                bool,
                description="True = 所有参考面**缝合成一张**（官方逐字 `sewn`）。",
            ),
        ],
        evidence=(
            "★ **曲面中面**：`IFeatureManager.InsertMidSurface(4 参)` → `System.object`。★★ **官方前置（Remarks 逐字）*"
            "*：`pPartDocIn` 是**该组件的模型文档**、`pBody` 是**该组件的体** ⇒ ★ 本工具**要求活动文档是零件**；★ 取不"
            "到体时**如实报** `preconditions_held=False` 并写明原因，★ **不猜**。判据 = **曲面体数增量**（官方逐字：每"
            "张参考面都算一个 **`sheet body`**）+ 返回对象非 None + 树增量（★ 后者单独**不足以**当判据）。⚠ 本工具**尚"
            "未真机验证**；★ 同批其余 4 条同样只是**已注册**，不是**已验证**。"
        ),
        doc="★ **曲面中面**：`IFeatureManager.InsertMidSurface(4 参)` → `System.object`。"
        "★★ **官方前置（Remarks 逐字）**：`pPartDocIn` 是**该组件的模型文档**、`pBody` 是**该组件的体** "
        "⇒ ★ 本工具**要求活动文档是零件**；★ 取不到体时**如实报** `preconditions_held=False` 并写明原因，"
        "★ **不猜**。判据 = **曲面体数增量**（官方逐字：每张参考面都算一个 **`sheet body`**）+ "
        "返回对象非 None + 树增量（★ 后者单独**不足以**当判据）。"
        "⚠ 本工具**尚未真机验证**；★ 同批其余 4 条同样只是**已注册**，不是**已验证**。",
    )
)

#: ★ 注册器按 `SPECS_*` 找
SPECS_BATCH74 = _BATCH74
