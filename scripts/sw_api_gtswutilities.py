r"""SolidWorks gtswutilities 官方接口全量索引。

能力域
    几何分析 / 壁厚分析 / 图档比较 等独立工具

本模块是什么
------------
**官方 API 的完整抄录** —— 11 个接口族、**120 个成员**，
逐个照抄自对官方 interop 程序集的**纯元数据反射**。

怎么用
------
    call_index(对象, "族名", "成员名", *参数)

例：
    call_index(特征管理器, "IFeatureManager", "FeatureCut4", x1, ..., x27)

⚑ 口径（与本仓库所有模块统一）
--------------------------------
  · **成员名用 COM 名** —— 反射清单里属性形态写作 ``get_Xxx``（.NET interop 约定），
    但 COM 里实际叫 ``Xxx``。⚠ 传 ``GetXxx``（大写 G）**谁都不认**。
  · **arity = 调用方要传的实参**，**排除 by-ref 出参**（``Xxx&``）。
    ⚠ 反射里 ``Void GetErrorMessages(Object&, Object&, Object&)`` 是 **0 参**
    —— 三个全是 [out]，调用方一个都不传。
  · 编号成员**未折叠** —— SolidWorks 的编号不是重载，是不同版本的不同操作
    （``FeatureExtrusion`` / ``2`` / ``3`` 三个都存在且都是不同成员）。
  · COM 内部分发口（名字形如 ``IGetXxx``）**不登记** —— 它们是同一能力的
    内部变体，不是独立能力。

⚠ 本模块**只登记名字与参数个数，不解释语义**。
  语义请查官方文档（`C:\swapi` 与本机 CHM 册）。

签名来源
--------
    D:\AI\SW\_raw\reflect\iface_gtswutilities.txt
      对 **SolidWorks.Interop.gtswutilities.dll** 的纯元数据反射（AGENTS.md §四.1③）。
    ⚠ 属「读官方程序集」，**不是实测**（铁律 2）。

⚠ 本模块为机械抄录，未在本机实测（见 AGENTS.md 铁律 2）。
"""

from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   官方 interop 程序集的纯元数据反射（SolidWorks.Interop.gtswutilities.dll）
# 文件:   D:\AI\SW\_raw\reflect\iface_gtswutilities.txt
# 定位:   11 个接口族的**全量**能力登记表 {族: {能力名: 实参个数}}。
# ⚑ 逐条机械生成，**不手抄、不折叠、不合并重载**。
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = ["ASSEMBLY", "FAMILIES", "ARITY", "PROPERTIES", "call_index"]

ASSEMBLY = "gtswutilities"

FAMILIES: tuple[str, ...] = (
    "IBendSequenceDrawing",
    "ICompareDocument",
    "ICompareFeature",
    "ICompareGeometry",
    "IFeaturePaint",
    "IFindReplaceAnnotations",
    "IGeometryAnalysis",
    "IPowerSelect",
    "IThicknessAnalysis",
    "IUtilOptions",
    "IUtilities",
)

#: 全量能力登记表 {族: {能力名: 实参个数}}（排除 by-ref 出参）
ARITY: dict[str, dict[str, int]] = {
    "IBendSequenceDrawing": {
        "GenerateDrawing": 5,
        "GetBendListForBody": 1,
        "Init": 0,
        "SetDrawingFileNameForBody": 2,
        "SetResequencedBendListForBody": 1,
    },
    "ICompareDocument": {
        "Close": 0,
        "CompareDocument": 5,
        "CompareDocument2": 9,
        "SaveCompareVolumeResults": 1,
    },
    "ICompareFeature": {
        "Close": 0,
        "CompareFeatures": 4,
        "CompareFeatures2": 8,
    },
    "ICompareGeometry": {
        "Close": 0,
        "CompareGeometry": 5,
        "CompareGeometry2": 9,
        "CompareGeometry3": 9,
        "SaveCompareVolumeResults": 1,
    },
    "IFeaturePaint": {
        "FeaturePaint": 2,
        "FeaturePaint2": 3,
    },
    "IFindReplaceAnnotations": {
        "Close": 0,
        "FindNext": 0,
        "FindPrevious": 0,
        "InitPMPage": 0,
        "Replace": 0,
        "ReplaceAll": 0,
    },
    "IGeometryAnalysis": {
        "Close": 0,
        "GetDiscontinuousEdgesCount": 0,
        "GetDiscontinuousFacesCount": 0,
        "GetKnifeEdgesCount": 1,
        "GetKnifeVerticesCount": 1,
        "GetShortEdgesCount": 1,
        "GetSliverFacesCount": 1,
        "GetSmallFacesCount": 1,
        "Init": 0,
        "SaveReport": 1,
        "SaveReport2": 3,
        "ShowResultsDialog": 0,
    },
    "IPowerSelect": {
        "Close": 0,
        "GetAppliedFilters": 0,
        "GetAppliedFiltersCount": 0,
        "GetEdgeAngleFilter": 0,
        "GetEdgeConvexityFilter": 0,
        "GetFaceColorFilter": 0,
        "GetFeatureColorFilter": 0,
        "GetFeatureNameFilter": 0,
        "GetFeatureTypeFilter": 0,
        "GetFeatureTypeFilterCount": 0,
        "GetSelectEntitiesTypes": 0,
        "GetShowHiddenEntities": 0,
        "GetSurfaceTypeCount": 0,
        "GetSurfaceTypeFilter": 0,
        "Init": 0,
        "RemoveFilters": 1,
        "RunPowerSelect": 1,
        "SelectResults": 0,
        "SetEdgeAngleFilter": 2,
        "SetEdgeConvexityFilter": 3,
        "SetFaceColorFilter": 3,
        "SetFeatureColorFilter": 3,
        "SetFeatureNameFilter": 1,
        "SetFeatureTypeFilter": 1,
        "SetSelectEntitiesTypes": 1,
        "SetShowHiddenEntities": 1,
        "SetSurfaceTypeFilter": 1,
    },
    "IThicknessAnalysis": {
        "Close": 0,
        "GetAnalysisDetails": 1,
        "GetAvgWeightedTckOnAnalArea": 0,
        "GetAvgWeightedTckOnCritArea": 0,
        "GetCriticalFeatureNames": 0,
        "GetCriticalSurfaceArea": 0,
        "GetIntervalCount": 0,
        "GetMaxDeviationfromTargetThickness": 0,
        "GetMaxTckOnAnalArea": 0,
        "GetMinTckOnAnalArea": 0,
        "GetNumCriticalFaces": 0,
        "GetNumCriticalFeatures": 0,
        "GetThicknessAnalysisBody": 0,
        "GetTotalSurfaceAreaAnalyzed": 0,
        "Init": 0,
        "RunThickAnalysis": 8,
        "RunThickAnalysis2": 9,
        "RunThinAnalysis": 6,
        "RunThinAnalysis2": 7,
        "SetThicknessAnalysisBody": 1,
    },
    "IUtilOptions": {
        "GetAngularTolerance": 0,
        "GetPositionTolerance": 0,
        "SetAngularTolerance": 1,
        "SetPositionTolerance": 1,
    },
    "IUtilities": {
        "appCallbackFunction": 3,
        "GetAutoPartSimplification": 0,
        "GetOptions": 0,
        "GetToolInterface": 1,
        "HelpErrCallback": 4,
        "OnBendSequence": 0,
        "OnCompareDocuments": 0,
        "OnCompareFeatures": 0,
        "OnCompareGeometry": 0,
        "OnFeaturePaint": 0,
        "OnFindFeatures": 0,
        "OnFindReplaceAnnotation": 0,
        "OnGeometryAnalysis": 0,
        "OnPowSelect": 0,
        "OnReplaceFeatures": 0,
        "OnReportMgr": 0,
        "OnSimplify": 0,
        "OnSuppressFeatures": 0,
        "OnThicknessAnalysis": 0,
        "OnUpdateBendSequence": 0,
        "OnUpdateCompareDocuments": 0,
        "OnUpdateCompareFeatures": 0,
        "OnUpdateCompareGeometry": 0,
        "OnUpdateFeaturePaint": 0,
        "OnUpdateFindFeatures": 0,
        "OnUpdateFindReplaceAnnotation": 0,
        "OnUpdateGeometryAnalysis": 0,
        "OnUpdatePowerSelect": 0,
        "OnUpdateReplaceFeatures": 0,
        "OnUpdateSimplify": 0,
        "OnUpdateSuppressFeatures": 0,
        "OnUpdateThicknessAnalysis": 0,
    },
}

#: 属性名（反射里是 get_/set_，**不是方法**；这里只留去掉前缀的名字）
PROPERTIES: dict[str, tuple[str, ...]] = {
    "IBendSequenceDrawing": (),
    "ICompareDocument": (),
    "ICompareFeature": (),
    "ICompareGeometry": (),
    "IFeaturePaint": (),
    "IFindReplaceAnnotations": (
        "AnnotationFilter",
        "AnnotationFilter",
        "FindText",
        "FindText",
        "ReplaceText",
        "ReplaceText",
        "options",
        "options",
    ),
    "IGeometryAnalysis": (),
    "IPowerSelect": (),
    "IThicknessAnalysis": (),
    "IUtilOptions": (),
    "IUtilities": (
        "BendSequenceDrawing",
        "CompareDocument",
        "CompareFeature",
        "CompareGeometry",
        "FeaturePaint",
        "FindReplaceAnnotations",
        "GeometryAnalysis",
        "PowerSelect",
        "ThicknessAnalysis",
        "options",
    ),
}


def _require(obj, what: str = "对象"):
    if obj is None:
        raise ValueError(f"{what} 为 None")
    return obj


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（与 sw_hubs.py / sw_sldworks_app.py 同款护栏）
# 文件:   {mod} —— 本文件自身
# 定位:   通用访问器 :func:`call_index` 的 arity 校核与调用。
# ⚑ **族名与成员名都由调用方给** ⇒ 静态 arity 审计归因不到，
#   对账靠 scripts/check_member_names.py（全仓成员名门禁）。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
#: dispatch-guard: exempt generated-api
def call_index(obj, family: str, member: str, *args):
    """按登记表校核实参个数，通过后调用该族的成员。

    :raises KeyError: 族名或成员名不在登记表里（**不静默忽略**）
    :raises ValueError: 实参个数对不上（在**发起调用之前**就报）
    """
    sub = ARITY.get(family)
    if sub is None:
        raise KeyError(
            f"本清单没有这个族: {family}（gtswutilities 共 {len(ARITY)} 族）。"
            f"⚠ 别的程序集请用对应的 call_index。"
        )
    expected = sub.get(member)
    if expected is None:
        raise KeyError(
            f"{family} 上没有名为 {member} 的能力（该族登记 {len(sub)} 项）。"
            f"⚠ 若它是属性或 COM 内部分发口，请用对应封装。"
        )
    if expected != len(args):
        raise ValueError(
            f"{family}.{member} 官方签名是 {expected} 个实参"
            f"（不含末位 by-ref 出参），本次调用给了 {len(args)} 个"
        )
    _require(obj, f"{family} 对象")
    return get_com_member(obj, member, *args)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 interop 程序集**自身的元数据**
# 文件:   D:\AI\SW\interop-dimension-census.json（40,921 行全量普查）
# 定位:   每个成员的**调用属性**维度 —— 属性方向 / 是否内部使用 / DISPID。
# ⚑ 这三个维度**不是本项目推断的**，官方程序集里本来就有：
#     · CanRead / CanWrite   ← System.Reflection.PropertyInfo
#     · FHidden              ← SolidWorks 标「内部使用」的属性
#                              （⚠ 全 assembly 命中 0 次 [Obsolete]
#                                —— 记 obsolete 这一栏永远是空的）
#     · DispIdAttribute      ← makepy 生成物的主键，可精确 join
# ⚑ 已用三个独立源交叉验证（typelib / interop DLL / makepy），
#   只写属性 10 个三源一致、数量对账吻合。
# ⚠ 读取方式是**纯元数据**（读程序集 / typelib），
#   **未启动 SolidWorks 进程、未做任何 COM 实例化调用**。
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测 SolidWorks 行为（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
