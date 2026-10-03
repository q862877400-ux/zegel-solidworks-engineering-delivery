# ── 24h 计划 · 阶段 3 · 段 5：**把回读能力挂出去**（轮 95–102 补的 6 个）──────────────
# ★★★★★★ 2026-10-04（轮 103）**本文件补的是一个我自己造成的缺口**：
#   ★ 任务书阶段 5 逐字：「每格：查官方签名 → 建能力 → **挂 ToolSpec** → 真机验证 → 提交」⇒
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
]
