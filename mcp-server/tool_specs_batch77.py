# ── 24h 计划 · 阶段 3 · 段 5：**把回读能力挂出去**（轮 95–102 补的 6 个）──────────────
# ★★★★★★ 2026-10-04（轮 103）**本文件补的是一个我自己造成的缺口**：
# ★ 任务书阶段 5 逐字：「每格：查官方签名 → 建能力 → **挂 ToolSpec** → 真机验证 → 提交」
# ⇒
#   ★★ 我在轮 95–102 补了 **6 个回读能力**、★ 做了「建能力」与「真机验证」、
#     ★★★ **却没做「挂 ToolSpec」** ⇒ 真机查（★ `output/_check_readback_toolspecs.py`）：
#       ★ `ToolSpec 总数 280` · ★★ **我补的 6 个全部「没有」** ·
#       ★★★ **与 `feature_readback` 相关的 ToolSpec：一个都没有** ✓
#   ★★★★ **⇒ 那 6 个能力**只在 Python 层可用、★ MCP 层调不到**** ✓
#   ★★★★★ **可复用判据**：★★★ **"建成了能力"与"能力能被调"是两件事** ——
#     ★ 前者看**函数存在 + 真机读数**、★ 后者看**ToolSpec 清单里有没有它** ✓
#     （★ 与「**一个存在但没人用的守卫与没有守卫等价**」（事实 40）**同族**）✓
#
# ★ 本批 6 条**全部只读**（★ `inject="model"` · ★ 无写操作）⇒ ★ 风险低 ✓
# ★★ 而每一条的**单位口径**都写进 doc（★ 那是本会话最贵的一批读数）✓
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层：`scripts/sw_feature_readback.py`）
# 文件:   mcp-server/tool_specs_batch77.py —— 本文件（新）
# 定位:   阶段 3 · 把轮 95–102 的 6 个**回读能力**挂成 MCP 工具。
# 官方签名依据: `C:\swapi\types\{IExtrudeFeatureData2,ILinearPatternFeatureData,
#   IWizardHoleFeatureData2,IFeature,ISimpleFilletFeatureData2}\*.md`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

_FEAT_NAME = Param("feature_name", str, default="",
                   description="特征名（★ 留空 = 按类型找第一个/最后一个；"
                               "★ 而留空时**要看清兜底找的是哪一类** —— "
                               "★ 见各工具 doc 里那条「三次判据修正」的记录）")

SPECS_BATCH77 = [
    ToolSpec(
        name="solidworks_extrude_depth",
        title="Read Extrude Feature Depth",
        module="sw_feature_readback", inject="model", function="extrude_depth",
        params=[_FEAT_NAME,
                Param("forward", bool, default=True,
                      description="True = 正向 / False = 反向（★ 官方 `GetDepth` 的入参）")],
        doc="★ **读拉伸特征的深度**（★ 官方 `IExtrudeFeatureData2::GetDepth(bool Forward)`）。"
            "★★★ **单位口径**：★ 真机两轮实测（★ 建 `depth=20` ⇒ 回 **`20.0`**、建 `5` ⇒ `5.0`）⇒"
            "★ **它随**文档单位****（★ 不是米）—— ★ 而官方 `## Returns` **没写单位**。"
            "★ 返回值带 `unit_source` ⇒ ★ **调用方不用猜**。"
            "★ ⚠ **本工具不替调用方换算**（★ 要毫米自己按 `GetUnits()` 判）。",
    ),
    ToolSpec(
        name="solidworks_extrude_params",
        title="Read Extrude Feature Parameters",
        module="sw_feature_readback", inject="model", function="extrude_params",
        params=[_FEAT_NAME],
        doc="★ **读拉伸特征的一组参数**（★ 端条件 / 拔模角 / 轮廓数 / 两向开关）。"
            "★★★ **单位口径**：★ `GetDepth` **随文档单位**、"
            "★ 而 `GetDraftAngle` ★ **官方逐字 `in radians`** ⇒ ★ **两者口径不同**。"
            "★ 返回值**逐项**标口径。"
            "★★ ⚠ **`GetFace` 已废弃** ⇒ 本工具不调它；★ `GetDirectionReference` 带 out ⇒ 也不碰。",
    ),
    ToolSpec(
        name="solidworks_pattern_params",
        title="Read Linear Pattern Parameters",
        module="sw_feature_readback", inject="model", function="pattern_params",
        params=[_FEAT_NAME],
        doc="★ **读线性阵列特征的一组参数**（★ 两向实例数/间距 + 若干开关 + 计数）。"
            "★★★ **单位口径**：★ `D1Spacing` / `D2Spacing` ★ **官方逐字 `in meters`** ⇒ "
            "★ **写死米**（★ 与 `GetDepth` 的「随文档」**不同**）。"
            "★ 而 `D1TotalInstances` 是**实例数**（★ 无量纲）。",
    ),
    ToolSpec(
        name="solidworks_hole_params",
        title="Read Hole Wizard Feature Parameters",
        module="sw_feature_readback", inject="model", function="hole_params",
        params=[_FEAT_NAME],
        doc="★ **读异型孔向导特征的一组参数**（★ 尺寸 / 标准 / 类型 / 端条件）。"
            "★★★★★ **单位口径的那一族最特别**：★ 官方 `## Returns` ★ **没写单位** ⇒"
            "★ 而真机实测出 ★★ **同一个接口里两个量的口径**不同**** ——"
            "★ `ThruHoleDiameter` = **米**（★ `M8` ⇒ `0.008`）、"
            "★ `ThruHoleDepth` = **毫米**（★ 板厚 `20` ⇒ `20.0`）。"
            "★ 返回值**保留「官方未写」这个事实** + ★ 逐项标口径。"
            "★★ ⚠ `FastenerType` **已废弃** ⇒ 不读。",
    ),
    ToolSpec(
        name="solidworks_feature_info",
        title="Read Feature Metadata",
        module="sw_feature_readback", inject="model", function="feature_info",
        params=[_FEAT_NAME],
        doc="★ **读一个特征的一组通用属性**（★ 元数据 / 面数 / 可见性 / 子父特征）。"
            "★★★★ **⚠ 本工具**不读 `GetBox`**** —— ★ 官方 `## Remarks` 逐字："
            "「The values returned are **approximate** and **should not be used for "
            "comparison or calculation purposes**」⇒ ★ **要包围盒用 `part_bounding_box`**。"
            "★★★ **⚠ 留空 `feature_name` 时取的「第一个真特征」要看清是哪一类** ——"
            "★ 它是**按名字 + 类型名两层过滤**后的第一个（★ 中文 UI 下通常是 `前视基准面`）⇒"
            "★ 而**基准面没有面**（`GetFaceCount = 0` 是应然的）⇒ "
            "★ **要对拉伸下判据就显式传特征名**。",
    ),
    ToolSpec(
        name="solidworks_fillet_params",
        title="Read Fillet Feature Parameters",
        module="sw_feature_readback", inject="model", function="fillet_params",
        params=[_FEAT_NAME],
        doc="★ **读简单圆角特征的一组参数**（★ 默认半径 / 类型 / 边数 / 若干开关）。"
            "★★★ **单位口径**：★ `DefaultRadius` 官方 **没写单位** ⇒ ★ 真机实测 **随文档单位**"
            "（★ 建 `R5` ⇒ 回 `5.0`）。"
            "★★ ⚠ **本工具不碰那三个「要 item 对象」的成员**"
            "（★ `GetRadius` / `GetDistance` / `GetConicRhoOrRadius`）——"
            "★ 它们要先 `IGetFilletEdgeAtIndex` ⇒ ★ **硬写会得到一个每次都不一样的结果**。",
    ),
    ToolSpec(
        name="solidworks_csys_params",
        title="Read Coordinate System Feature Parameters",
        module="sw_feature_readback", inject="model", function="csys_params",
        params=[_FEAT_NAME],
        doc="★ **读坐标系特征的一组参数**（★ 原点实体类型 / 三轴实体数 / 变换对象）。"
            "★★★ **读数自洽**：★ 建**默认三轴**的坐标系 ⇒ ★ `GetOriginEntityType = -1` ·"
            "★ 三轴实体数 `0/0/0` · ★ `Transform.ArrayData` **16 个数 = 单位阵** ✓"
            "★★★★ **⚠ 本族的官方页**只有四个****（★ `output/_read_csys_members.py`）⇒"
            "★ `Flipped` / ★ `Reverse*Direction` / ★ `Get*AxisEntities` 等 **11 个「页不在」** ⇒"
            "★★ **按铁律 5：★ 本工具**不调**它们、★ 也不猜**（★ 返回值里列了那份清单）✓"
            "★★★ **⚠ 本族**没有长度量****（★ 三是计数、★ 一是枚举、★ 一是变换对象）⇒"
            "**不涉及单位口径** —— ★ 那是本会话**唯一**一个这样的一族 ✓",
    ),
    ToolSpec(
        name="solidworks_base_flange_params",
        title="Read Sheet Metal Base Flange Parameters",
        module="sw_feature_readback", inject="model", function="base_flange_params",
        params=[_FEAT_NAME],
        doc="★ **读钣金基体法兰特征的一组参数**（★ 厚度 / 折弯半径 / K 因子 / 释放槽 / 若干开关）。"
            "★★★ **单位口径（★ 第七族）**：★ 官方 `## Returns` **七个长度量全没写单位** ⇒"
            "★ 而**本仓 `BaseFlangeSpec` 的 docstring 逐字写着「全部长度单位为米」** ⇒"
            "★★ **实机一致性**：★ 传 `thickness=0.002` ⇒ ★ `Thickness` 回 **`0.002`** ✓"
            "★★ **另外三个表值**（★ `TableKFactor` / `TableRadius` / `TableThickness`）"
            "在不用 gauge table 时**必然是 `0.0`** ⇒ **与 `UseGaugeTable` 互相印证** ✓"
            "★★★★ **⚠ 本工具**不读 `D1OffsetDistance`****（★ 官方标**真废弃**）✓",
    ),
    #: ★★★★★★ 2026-10-04（轮 122）**第 9 条** —— ★ 阶段 5「按缺口密度补能力」的第一格 ✓
    #:   ★ **本批补的是一个**零覆盖的格****：★ 密度图（`output/density-gap-map.json`）里
    #:     ★★ **`查 × 特征` = 官方 451 成员、★ 我们 8** ⇒ **那是最大的一格** ✓
    #:   ★★★ **而挑它的理由**：★ 本仓有 **6 个"能写"的特征工具**
    #:     （★ `revolve_boss` / ★ `shell_report` / ★ `rib_report` / ★ `insert_dome_report` /
    #:      ★ `create_loft_report` / ★ `create_sweep_report`）、★ **却一个读都没有** ⇒
    #:     ★★★★ **⇒ 那正是本仓最典型的**「能写不能读」**** ✓
    #: ★★★★★ **⚠ 而 `IRevolveFeatureData` **查不到****（★ `C:\swapi\types\` 下没有那个目
    #: 录）⇒
    #:     按**铁律 5**：★ **停下、★ 不用相似名字蒙混** ⇒ **改做 `shell`**（★ 16 个成员里
    #:     5 个可读、★ 比 `sweep` 的 54 小）✓
    ToolSpec(
        name="solidworks_shell_params",
        title="Read Shell Feature Parameters",
        module="sw_feature_readback", inject="model", function="shell_params",
        params=[_FEAT_NAME],
        doc="★ **读抽壳特征的一组参数**（★ 厚度 / 方向 / 移除面数 / 多厚度面数与逐面厚度）。"
            "★★★★★ **单位口径（★ 第八族）**：★ 官方 `IShellFeatureData::Thickness` 的"
            "`## Returns` **只写 `Shell thickness`、★ 没写单位** ⇒"
            "★★ **而真机量了**（★ `tools/probe_shell_params_recheck.py`）："
            "★ **板 60×40×10（毫米）⇒ 抽壳 `2 mm` ⇒ 读回 `Thickness = 2.0`** ⇒"
            "★★★ **口径 = **随文档单位**** ✓"
            "★★★★ **⚠ 而这是**量**出来的** —— ★ 写侧 `shell_report` 也有同口径的记录、"
            "★ **但不能把写侧口径套到读侧**（★ 本会话见过**同一接口内部就分裂**的先例："
            "`IWizardHoleFeatureData2` 直径是**米**、深度是**毫米**）✓"
            "★★★★ **⚠ 本工具**不碰**指针接口**：★ `IGetFacesRemoved` / `IGetMultipleThicknessFaces`"
            "的官方 `## Returns` 逐字写「**in-process, unmanaged C++: Pointer to an array** of …」⇒"
            "★ 那正是**事实 47 那一族**（★ pywin32 到达不了）✓"
            "★★★ **也不碰**要「Accessing Selections」前置的那几个"
            "（★ `AccessSelections` / ★ `ReleaseSelectionAccess` / ★ `FacesRemoved` /"
            "★ `MultipleThicknessFaces`）—— ★ 那是**前置**、★ 不是「读参数」 ✓",
    ),
    #: ★★★★★★ 2026-10-04（轮 123）**第 10 条** —— ★ 同族继续 ✓
    #:   ★ **真机量到了**（★ `output/rib-dome-params-capability-recheck.json`）：
    #:     ★ 管 40×40×10（毫米）⇒ 圆顶 **5 mm** ⇒ 读回 **`Height = 5.0`** ⇒
    #:     ★★ **⇒ 单位口径 = **随文档单位**（★ 第十族）** ✓
    #: ★★★ **⚠ 而那次成功靠的是**三步选面序****（★ 先 `mark=0` ⇒ ★ `ClearSelection2(True
    #: )`
    #:     ⇒ ★★ **再按 `mark=1` 选**）—— ★ 那序**只在** `tools/verify_dome_smoke.py` 里、
    #:     ★ **签名与 Remarks 的散文都给不出** ⇒
    #:     ★★★★ **⇒ 又一次验证**「官方示例给的是**调用序**」那条纪律** ✓
    ToolSpec(
        name="solidworks_dome_params",
        title="Read Dome Feature Parameters",
        module="sw_feature_readback", inject="model", function="dome_params",
        params=[_FEAT_NAME],
        doc="★ **读圆顶特征的一组参数**（★ 高度 / 是否椭圆 / 方向 / 面数）。"
            "★★★★★ **单位口径（★ 第十族）**：★ 官方 `IDomeFeatureData2::Height` 的"
            "`## Returns` **只写 `Height of the dome`、★ 没写单位** ⇒"
            "★★ **而真机量了**：★ 管 40×40×10（毫米）⇒ 圆顶 `5 mm` ⇒"
            "**读回 `Height = 5.0`** ⇒ ★★★ **口径 = **随文档单位**** ✓"
            "★★★★ **⚠ `ReverseDir` 的官方语义逐字**：★「**True for concave domes,"
            "false for convex domes**」⇒ ★★ **那是**语义**、★ 不是「反向开关」那种字面意思** ⇒"
            "★★★ **本工具把语义一并带回来**（★ 免得下一个人按名字猜）✓"
            "★★★★ **⚠ 不碰**：★ `Face`/`IFace`（★ 官方标**真废弃**）·"
            "★ `IGetFaces`（★ 官方逐字「**in-process, unmanaged C++: Pointer to an array**」⇒"
            "**事实 47 那一族**）· ★ `ISetFaces`（★ 含 `ref Face2`）·"
            "★ `Faces`/`Direction`/`ConstraintPointOrSketch`（★ 要「Accessing Selections」）·"
            "★ `AccessSelections`/`IAccessSelections`/`ReleaseSelectionAccess`（★ 前置）✓",
    ),
    ToolSpec(
        name="solidworks_sweep_params",
        title="Read Sweep Feature Parameters",
        module="sw_feature_readback", inject="model", function="sweep_params",
        params=[_FEAT_NAME],
        doc="★ **读扫描特征的一组参数**（★ 类型 / 薄壁 / 圆轮廓直径 / 壁厚 / 扭转角 / 引导线数）。"
            "★★★★★ **单位口径 —— ★ 本族把两种量分开**：★ 官方对 `GetTwistAngle()` 与"
            "`GetD2TwistAngle()` **逐字写了 radians**（★ 本会话**第二族**官方明说单位的）⇒"
            "★ **那两条不用量**；★ 而 `CircularProfileDiameter` 与 `GetWallThickness` 的"
            "`## Returns` **没写单位** ⇒ ★ **要真机量** ✓"
            "★★★★ **⚠ 而本轮真机跑过、★ 那两个量仍未定案** —— 读数都是 `0.0`、"
            "★ **而那是应然的**（★ 本探针用**草图轮廓** ⇒ `CircularProfile=false` ⇒ 直径本就该 0；"
            "★ 官方说 `GetWallThickness` **valid only if `IsThinFeature` is true**）⇒"
            "★★ **如实留作待办、★ 不谎称量到了** ✓"
            "★★★★ **而其余读数全部自洽**（★ 建成了 `type_name=Sweep` · 树 9→10）："
            "★ `SweepType=17`（`swFmSweep`）· ★ `IsBossFeature=true` · ★ `IsThinFeature=false` ·"
            "★ `CircularProfile=false` · ★ `GetTwistAngle=0.0` · ★ `GetPathType=9` ·"
            "★ `GetProfileType=9` · ★ `GetGuideCurvesCount=0` ✓"
            "★★★★ **⚠ 不碰**：★ **真废弃 6 个**（`EndDirectionVector` · `IAccessSelections` ·"
            "`IGetFeatureScopeBodies` · `IGetGuideCurves` · `IGetGuideCurvesType` ·"
            "`ISetFeatureScopeBodies`）· ★ `GetPathAlignmentDirectionVector(out int)`（★ 有 `out`）·"
            "★ `Path`/`Profile`/`GuideCurves`/`FeatureScopeBodies`（★ 对象数组 + 要前置）·"
            "★ `Set*` 那一族（★ 那是写）· ★ `AccessSelections`/`ReleaseSelectionAccess`（★ 前置）✓",
    ),
    ToolSpec(
        name="solidworks_revolve_params",
        title="Read Revolve Feature Parameters",
        module="sw_feature_readback", inject="model", function="revolve_params",
        params=[_FEAT_NAME],
        doc="★ **读旋转特征的一组参数**（★ 角度 / 轴类型 / 方向 / 薄壁 / 轮廓数）。"
            "★★★★★ **单位口径（★ 第十三族）**：★ 官方 `ISweepFeatureData` 那一族没写单位 ——"
            "★ 而本族的 `GetRevolutionAngle` 官方也**没写** ⇒ ★★ **真机量出来了：★ **radians**** ✓"
            "★★ **三条独立证据**：★ ① 传 `math.radians(30)` ⇒ 读回 `0.5235987755982988`"
            "（★ **正是 π/6 的精确值**；★ 若回度该是 `30.0`）⇒ 距离 `0.000000` · 次近 `29.476`；"
            "★ ② **几何**：体积 `785.398` = 「30° 扇形环」的解析值 `785.398`；"
            "★ ③ **反面对照**：误传**度**时读回 `4.867259 rad = 278.8734°`、"
            "而 `30 rad mod 360°` 也正是 `278.8734°`（★ 差 `0.000000°`）✓"
            "★★★★ **⚠ 其余真机读数**：★ `GetAxisType=10` · ★ `IsBossFeature=true` ·"
            "★ `IsThinFeature=false` · ★ `GetContoursCount=0` · ★ `ReverseDirection=false` ✓"
            "★★★ **⚠ `GetWallThickness` 仍 `unknown`** —— 官方 `## Remarks` 说它"
            "「**only affects thin features**」⇒ ★ 本探针建的是**非薄壁** ⇒ ★ **如实标、★ 不谎称** ✓"
            "★★★★ **⚠ 不碰**：★ `Axis`/`Contours`/`FeatureScopeBodies`（★ 对象数组 + 要前置）·"
            "★ `ISetContours`/`ISetFeatureScopeBodies`（★ `ref`）· ★ `Set*`（★ 写）·"
            "★ `AccessSelections`/`IAccessSelections`/`ReleaseSelectionAccess`（★ 前置）✓"
            "★★★★★ **⚠ 而两个带参量**（`GetRevolutionAngle` / `GetWallThickness`）**单独带参调** ——"
            "★ 因为 `get_com_member` 对「必须带实参」的成员会**静默回 bound method** ✓",
    ),
    ToolSpec(
        name="solidworks_loft_params",
        title="Read Loft Feature Parameters",
        module="sw_feature_readback", inject="model", function="loft_params",
        params=[_FEAT_NAME],
        doc="★ **读放样特征的一组参数**（★ 轮廓数 / 引导线 / 起止相切 / 拔模角 / 薄壁 / 闭合）。"
            "★★★★★ **真机读数（★ 建成了 ⇒ 读回来了）**：★ 建放样（★ 两个草图、按 mark=1 选）⇒"
            "★ `ok=True · feature_name=**放样1** · **type_name='Blend'** · tree 7→8` ⇒"
            "★★ 读回：★ `GetProfileCount=**2**`（★ 两个轮廓 ⇒ 对）· ★ `GetGuideCurvesCount=0` ·"
            "★ `IsBossFeature=true` · ★ `IsThinFeature=false` · ★ `Close=false` ·"
            "★ `StartTangencyType=0` · ★ `EndTangencyType=0` ·"
            "★ `StartConstraintDraftAngle=0.0` · ★ `StartTangentLength=**0.1**` ✓"
            "★★★★ **⚠ `NumberOfSections=**1.0**` 与 `GetProfileCount=**2**` 不一致** ——"
            "★ 那**不是矛盾**：★ 官方那两个名字逐字是「Number of **sections**」与"
            "「Number of **profiles**」⇒ ★ 是两个不同的量 ✓"
            "★★★★ **⚠ 那几个量的口径仍 `unknown`**（★ 拔模角 / 相切长度 / 壁厚）——"
            "★ 它们**都带前置**（★ 拔模角要开起/止约束）⇒ ★ **本探针的几何没打开它们** ⇒"
            "★ **不谎称量到了** ✓"
            "★★★★★ **⚠ 类型名走 `FEATURE_TYPE_NAMES` 表**（★ 每个名字都有**证据引用**）——"
            "★ 本会话**连续两轮**在「猜类型名」上栽了（★ `Revolve` vs `Revolution` · ★ `Loft` vs `Blend`）⇒"
            "★ **⇒ 不再凭记忆写** ✓"
            "★★★★ **⚠ 不碰**：★ `Profiles`/`GuideCurves`/`Centerline`/`PickPoints`/"
            "`FeatureScopeBodies`/`StartDirectionVector`/`EndDirectionVector`（★ 对象或数组）·"
            "★ `ISet*`（★ `ref`）· ★ `Set*`（★ 写）· ★ `AccessSelections`（★ 前置）✓",
    ),
    ToolSpec(
        name="solidworks_drawing_view_annotations",
        title="Read Drawing View Annotations",
        module="sw_drawing_query", inject="model", function="view_annotations_report",
        params=[],
        doc="★ **读当前图纸**每个视图上的注释 / 显示尺寸 / 弧数****（★ **工程图读侧第一批**）✓"
            "★★★★★★ **为什么做它**：★ 本仓有 `add_note`（**能写注释**）★ 而**读不回来** ⇒"
            "★★ **⇒ 又是「能写不能读」**（★ 本会话**第 6 次同型**：`shell`/`dome`/`sweep`/"
            "`revolve`/`loft` 之后）✓"
            "★★★★★ **官方例子的**调用序**（★ 签名与 `## Remarks` 都给不了）** ——"
            "逐字来自 `Get_Names_of_Annotations_Example_VB.md`：`GetFirstView` ⇒"
            "★ **`' First drawing view is the sheet, so get first drawing view`** ⇒ `GetNextView` ⇒"
            "`GetName2` ⇒ **`annArray = swDrView.GetAnnotations`** ⇒ `If Not IsEmpty(annArray)` ⇒"
            "`For Each obj In annArray` ⇒ `currAnn.GetName` ⇒ `GetNextView` ✓"
            "★★ **⇒ 那印证了本模块 `list_views` 早就写下的那条**：★ **第一个视图是**图纸本身**（sheet）** ⇒"
            "★ **必须跳过它**（★ 否则会列出一个假视图）✓"
            "★★★★★★ **✅ 真机读数（★ 建视图 → 写注释 → 读回）**：★ 零件**先存盘** ⇒"
            "`create_projected_view` ⇒ ★ **`ok: True`** ⇒ `add_drawing_note(x_mm=50, y_mm=50)` ⇒"
            "★ **`ok: True`** ⇒ ★★ **读回 `view_count = 1`**："
            "`{name: 工程图视图1, type: 7, annotation_count_by_api: 1, annotations: [细节项目254], "
            "annotation_len: 1, display_dimension_count: 0, arc_count: 0}` ⇒"
            "★★★ **两条独立读数一致**（`1` 与 `1`）⇒ `mismatches = 0` ⇒ **判据成立** ✓"
            "而 `细节项目254` **正是我写进去的那条注释**（★ SolidWorks 自动编号）⇒"
            "★★★★ **⇒ 「能写」与「能读」在真机上**对上了**** ✓"
            "★★★★★ **⚠ 两条边界（★ 都实测过）**："
            "★ **① 零件必须先存盘** —— 不存盘则 `GetPathName()` 是**空串** ⇒ 视图插不上 ⇒"
            "`view_count = 0`（★ **那是应然的、★ 不是读侧坏了**）·"
            "★★ **② 本机 `create_three_standard_views` 当时是 `blocked`**"
            "（★ 逐字：★「本机实测为 blocked：`CreateFirstAngleViews2` 不可用」）"
            "—— ★★ **2026-10-04（接手轮）更正：那句「不可用」是假阴性** ——"
            "真因是**成员名拼错**（`CreateFirstAngleViews2` 官方**不存在**；真名 **`Create1stAngleViews2`**，"
            "`1st` 非 `First`）⇒ 已在 `drawing_workflow.py` 修正、**待真机复验** ⇒"
            "★ **要插视图仍建议走 `create_projected_view`**（★ 它已真机建成）✓"
            "★★★★ **⚠ 不读**：★ `GetLineCount()` ⇒ ★ **官方标 `Obsolete`** ⇒ **本模块不碰** ✓",
    ),
]
