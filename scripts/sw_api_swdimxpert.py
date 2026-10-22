r"""SolidWorks swdimxpert 官方接口全量索引。

能力域
    DimXpert —— 尺寸标注自动化 / GD&T 公差

本模块是什么
------------
**官方 API 的完整抄录** —— 51 个接口族、**136 个成员**，
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
    D:\AI\SW\_raw\reflect\iface_swdimxpert.txt
      对 **SolidWorks.Interop.swdimxpert.dll** 的纯元数据反射（AGENTS.md §四.1③）。
    ⚠ 属「读官方程序集」，**不是实测**（铁律 2）。

⚠ 本模块为机械抄录，未在本机实测（见 AGENTS.md 铁律 2）。
"""

from __future__ import annotations

try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   官方 interop 程序集的纯元数据反射（SolidWorks.Interop.swdimxpert.dll）
# 文件:   D:\AI\SW\_raw\reflect\iface_swdimxpert.txt
# 定位:   51 个接口族的**全量**能力登记表 {族: {能力名: 实参个数}}。
# ⚑ 逐条机械生成，**不手抄、不折叠、不合并重载**。
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = ["ASSEMBLY", "FAMILIES", "ARITY", "PROPERTIES", "call_index"]

ASSEMBLY = "swdimxpert"

FAMILIES: tuple[str, ...] = (
    "IDimXpertAngleBetweenCircularDimTol",
    "IDimXpertAngleBetweenDimTol",
    "IDimXpertAnnotation",
    "IDimXpertAutoDimSchemeOption",
    "IDimXpertBestfitPlaneFeature",
    "IDimXpertBlockTolerances",
    "IDimXpertChamferDimTol",
    "IDimXpertChamferFeature",
    "IDimXpertCompositeDistanceBetweenDimTol",
    "IDimXpertCompositeLineProfileTolerance",
    "IDimXpertCompositePositionTolerance",
    "IDimXpertCompositeSurfaceProfileTolerance",
    "IDimXpertCompoundClosedSlot3DFeature",
    "IDimXpertCompoundHoleFeature",
    "IDimXpertCompoundNotchFeature",
    "IDimXpertCompoundWidthFeature",
    "IDimXpertConcentricityTolerance",
    "IDimXpertConeFeature",
    "IDimXpertCounterBoreDimTol",
    "IDimXpertCounterSinkAngleDimTol",
    "IDimXpertCounterSinkDiameterDimTol",
    "IDimXpertCylinderFeature",
    "IDimXpertDatum",
    "IDimXpertDepthDimTol",
    "IDimXpertDiameterDimTol",
    "IDimXpertDimensionOption",
    "IDimXpertDimensionTolerance",
    "IDimXpertDistanceBetweenDimTol",
    "IDimXpertExtrudeFeature",
    "IDimXpertFeature",
    "IDimXpertFilletFeature",
    "IDimXpertFlatnessTolerance",
    "IDimXpertGtol",
    "IDimXpertIntersectCircleFeature",
    "IDimXpertIntersectLineFeature",
    "IDimXpertIntersectPlaneFeature",
    "IDimXpertIntersectPointFeature",
    "IDimXpertLineProfileTolerance",
    "IDimXpertOrientationTolerance",
    "IDimXpertPart",
    "IDimXpertPatternFeature",
    "IDimXpertPlaneFeature",
    "IDimXpertPositionTolerance",
    "IDimXpertRadiusDimTol",
    "IDimXpertRefPlaneFeature",
    "IDimXpertSphereFeature",
    "IDimXpertStraightnessTolerance",
    "IDimXpertSurfaceProfileTolerance",
    "IDimXpertSymmetryTolerance",
    "IDimXpertTangencyTolerance",
    "IDimXpertTolerance",
)

#: 全量能力登记表 {族: {能力名: 实参个数}}（排除 by-ref 出参）
ARITY: dict[str, dict[str, int]] = {
    "IDimXpertAngleBetweenCircularDimTol": {
        "GetActPlaneVector": 0,
        "GetNomPlaneVector": 0,
    },
    "IDimXpertAngleBetweenDimTol": {
        "GetDirectionVector": 0,
    },
    "IDimXpertAnnotation": {
        "GetAppliedAnnotationCount": 0,
        "GetAppliedAnnotations": 0,
        "GetDisplayEntity": 0,
        "GetModelFeature": 0,
        "IsFreeState": 0,
        "IsStatistical": 0,
        "IsSuppressed": 0,
        "IsToBeInspected": 0,
    },
    "IDimXpertAutoDimSchemeOption": {},
    "IDimXpertBestfitPlaneFeature": {
        "GetNominalPlane": 0,
        "GetSubFeatureCount": 0,
        "GetSubFeatures": 0,
    },
    "IDimXpertBlockTolerances": {
        "GetISO2768PartType": 0,
        "GetToleranceValues": 0,
    },
    "IDimXpertChamferDimTol": {},
    "IDimXpertChamferFeature": {},
    "IDimXpertCompositeDistanceBetweenDimTol": {
        "GetDirectionVector": 0,
        "GetFeature": 0,
        "GetIntraFeature": 0,
        "GetNominalValueIntraFeature": 0,
        "GetOriginFeature": 0,
        "GetPlusAndMinusToleranceIntraFeature": 0,
        "GetUpperAndLowerLimitIntraFeature": 0,
    },
    "IDimXpertCompositeLineProfileTolerance": {
        "GetPlanarZoneVector": 0,
    },
    "IDimXpertCompositePositionTolerance": {
        "GetMaxTolerance": 0,
        "GetMaxToleranceLowerTier": 0,
        "GetPlanarZoneVector": 0,
        "GetProjectedZone": 0,
    },
    "IDimXpertCompositeSurfaceProfileTolerance": {},
    "IDimXpertCompoundClosedSlot3DFeature": {
        "GetBottomFeature": 0,
        "GetEndFeatures": 0,
        "GetNominalBottomPlane": 0,
        "GetNominalClosedSlot": 0,
        "GetNominalTopPlane": 0,
        "GetPlaneFeatures": 0,
    },
    "IDimXpertCompoundHoleFeature": {
        "GetBottomFeature": 0,
        "GetReferenceFeature": 0,
        "GetSubFeatureCount": 0,
        "GetSubFeatures": 0,
    },
    "IDimXpertCompoundNotchFeature": {
        "GetBottomFeature": 0,
        "GetEndFeature": 0,
        "GetNominalBottomPlane": 0,
        "GetNominalNotch": 0,
        "GetOpenSideReferenceFeature": 0,
        "GetPlaneFeatures": 0,
        "GetTopReferenceFeature": 0,
    },
    "IDimXpertCompoundWidthFeature": {
        "GetNominalCompoundWidth": 0,
        "GetNominalLongitude": 0,
        "GetPlaneFeatures": 0,
    },
    "IDimXpertConcentricityTolerance": {
        "GetMaxTolerance": 0,
    },
    "IDimXpertConeFeature": {
        "GetNominalBottomPlane": 0,
        "GetNominalCone": 0,
        "GetNominalTopPlane": 0,
    },
    "IDimXpertCounterBoreDimTol": {},
    "IDimXpertCounterSinkAngleDimTol": {},
    "IDimXpertCounterSinkDiameterDimTol": {},
    "IDimXpertCylinderFeature": {
        "GetNominalBottomPlane": 0,
        "GetNominalCylinder": 0,
        "GetNominalTopPlane": 0,
        "GetThread": 0,
    },
    "IDimXpertDatum": {},
    "IDimXpertDepthDimTol": {
        "IsThreadDepth": 0,
    },
    "IDimXpertDiameterDimTol": {},
    "IDimXpertDimensionOption": {},
    "IDimXpertDimensionTolerance": {
        "GetNominalValue": 0,
        "GetPlusAndMinusTolerance": 0,
        "GetUpperAndLowerLimit": 0,
    },
    "IDimXpertDistanceBetweenDimTol": {
        "GetDirectionVector": 0,
        "GetFeature": 0,
        "GetOriginFeature": 0,
    },
    "IDimXpertExtrudeFeature": {
        "GetBottomBlends": 0,
        "GetBottomFeature": 0,
        "GetReferenceFeature": 0,
        "GetSubFeatureCount": 0,
        "GetSubFeatures": 0,
        "GetTopBlends": 0,
    },
    "IDimXpertFeature": {
        "GetAppliedAnnotationCount": 0,
        "GetAppliedAnnotations": 0,
        "GetAppliedFeatureCount": 0,
        "GetAppliedFeatures": 0,
        "GetFaceCount": 0,
        "GetFaces": 0,
        "GetModelFeature": 0,
        "IsCombinedAnnotation": 0,
        "IsSuppressed": 0,
        "SetCombineAnnotation": 1,
    },
    "IDimXpertFilletFeature": {},
    "IDimXpertFlatnessTolerance": {
        "GetPerUnitArea": 0,
    },
    "IDimXpertGtol": {},
    "IDimXpertIntersectCircleFeature": {
        "GetIntersectFeature": 0,
        "GetNominalCircle": 0,
        "GetPlaneFeature": 0,
    },
    "IDimXpertIntersectLineFeature": {
        "GetNominalLine": 0,
        "GetPlaneFeatures": 0,
    },
    "IDimXpertIntersectPlaneFeature": {
        "GetFeatures": 0,
        "GetNominalPlane": 0,
    },
    "IDimXpertIntersectPointFeature": {
        "GetFeatures": 0,
        "GetNominalPoint": 0,
        "GetNominalVector": 0,
    },
    "IDimXpertLineProfileTolerance": {
        "GetPlanarZoneVector": 0,
    },
    "IDimXpertOrientationTolerance": {
        "GetMaxTolerance": 0,
        "GetPlanarZoneVector": 0,
        "GetProjectedZone": 0,
        "IsTangentPlane": 0,
    },
    "IDimXpertPart": {
        "AutoDimensionScheme": 1,
        "DeleteAllTolerances": 0,
        "GetAnnotation": 1,
        "GetAnnotationCount": 0,
        "GetAnnotations": 0,
        "GetAutoDimSchemeOption": 0,
        "GetBlockTolerances": 0,
        "GetDimOption": 0,
        "GetFeature": 1,
        "GetFeatureCount": 0,
        "GetFeatures": 0,
        "ImportScheme": 2,
        "InsertAngleDimension": 1,
        "InsertBasicDimension": 1,
        "InsertDatum": 1,
        "InsertGtol": 1,
        "InsertLocationDimension": 1,
        "InsertPattern": 3,
        "InsertSizeDimension": 1,
    },
    "IDimXpertPatternFeature": {
        "GetSubFeatureCount": 0,
        "GetSubFeatures": 0,
    },
    "IDimXpertPlaneFeature": {
        "GetNominalPlane": 0,
    },
    "IDimXpertPositionTolerance": {
        "GetMaxTolerance": 0,
        "GetPlanarZoneVector": 0,
        "GetProjectedZone": 0,
    },
    "IDimXpertRadiusDimTol": {},
    "IDimXpertRefPlaneFeature": {
        "GetNominalPlane": 0,
    },
    "IDimXpertSphereFeature": {
        "GetNominalSphere": 0,
    },
    "IDimXpertStraightnessTolerance": {
        "GetMaxTolerance": 0,
        "GetPerUnitLength": 0,
        "GetPlanarZoneVector": 0,
    },
    "IDimXpertSurfaceProfileTolerance": {},
    "IDimXpertSymmetryTolerance": {
        "GetMaxTolerance": 0,
        "GetZoneDirection": 0,
    },
    "IDimXpertTangencyTolerance": {},
    "IDimXpertTolerance": {
        "GetPrimaryDatumCount": 0,
        "GetPrimaryDatumModifiers": 0,
        "GetPrimaryDatums": 0,
        "GetSecondaryDatumCount": 0,
        "GetSecondaryDatumModifiers": 0,
        "GetSecondaryDatums": 0,
        "GetTertiaryDatumCount": 0,
        "GetTertiaryDatumModifiers": 0,
        "GetTertiaryDatums": 0,
    },
}

#: 属性名（反射里是 get_/set_，**不是方法**；这里只留去掉前缀的名字）
PROPERTIES: dict[str, tuple[str, ...]] = {
    "IDimXpertAngleBetweenCircularDimTol": (
        "CenterFeature",
        "OriginFeature",
        "Supplement",
    ),
    "IDimXpertAngleBetweenDimTol": (
        "OriginFeature",
        "Supplement",
    ),
    "IDimXpertAnnotation": (
        "Feature",
        "Name",
        "Type",
    ),
    "IDimXpertAutoDimSchemeOption": (
        "FeatureFilters",
        "FeatureFilters",
        "PartType",
        "PartType",
        "PatternType",
        "PatternType",
        "PolarPatternHoleCount",
        "PolarPatternHoleCount",
        "ScopeAllFeature",
        "ScopeAllFeature",
        "ToleranceType",
        "ToleranceType",
    ),
    "IDimXpertBestfitPlaneFeature": (),
    "IDimXpertBlockTolerances": ("Type",),
    "IDimXpertChamferDimTol": ("ChamferType",),
    "IDimXpertChamferFeature": (
        "Angle",
        "AngleType",
        "ChamferType",
        "Distance1",
        "Distance2",
    ),
    "IDimXpertCompositeDistanceBetweenDimTol": (
        "BlockToleranceDecimalPlacesIntraFeature",
        "DimensionTypeIntraFeature",
        "LimitsAndFitsCodeIntraFeature",
    ),
    "IDimXpertCompositeLineProfileTolerance": (
        "OuterToleranceValue",
        "OuterToleranceValueLowerTier",
        "PrimaryInLowerTier",
        "SecondaryInLowerTier",
        "TertiaryInLowerTier",
        "ToleranceLowerTier",
    ),
    "IDimXpertCompositePositionTolerance": (
        "Modifier",
        "ModifierLowerTier",
        "PrimaryInLowerTier",
        "SecondaryInLowerTier",
        "TertiaryInLowerTier",
        "ToleranceLowerTier",
        "ZoneType",
    ),
    "IDimXpertCompositeSurfaceProfileTolerance": (
        "OuterToleranceValue",
        "OuterToleranceValueLowerTier",
        "PrimaryInLowerTier",
        "SecondaryInLowerTier",
        "TertiaryInLowerTier",
        "ToleranceLowerTier",
    ),
    "IDimXpertCompoundClosedSlot3DFeature": ("Blind",),
    "IDimXpertCompoundHoleFeature": (
        "Blind",
        "CompoundHoleType",
    ),
    "IDimXpertCompoundNotchFeature": ("Blind",),
    "IDimXpertCompoundWidthFeature": ("Inner",),
    "IDimXpertConcentricityTolerance": ("Modifier",),
    "IDimXpertConeFeature": ("Inner",),
    "IDimXpertCounterBoreDimTol": ("ReferenceFeature",),
    "IDimXpertCounterSinkAngleDimTol": ("ReferenceFeature",),
    "IDimXpertCounterSinkDiameterDimTol": ("ReferenceFeature",),
    "IDimXpertCylinderFeature": ("Inner",),
    "IDimXpertDatum": ("Identifier",),
    "IDimXpertDepthDimTol": ("ReferenceFeature",),
    "IDimXpertDiameterDimTol": (
        "EnvelopeRequirement",
        "IndependencyRequirement",
        "PatternTreatment",
    ),
    "IDimXpertDimensionOption": (
        "DatumLength",
        "DatumLength",
        "DimensionPositionOption",
        "DimensionPositionOption",
        "DimensionPositionOption2",
        "DimensionPositionOption2",
        "FeatureSelectorOptions",
        "FeatureSelectorOptions",
        "TextPosition",
        "TextPosition",
    ),
    "IDimXpertDimensionTolerance": (
        "BlockToleranceDecimalPlaces",
        "DimensionType",
        "LimitsAndFitsCode",
    ),
    "IDimXpertDistanceBetweenDimTol": ("PatternTreatment",),
    "IDimXpertExtrudeFeature": ("Blind",),
    "IDimXpertFeature": (
        "Name",
        "Type",
    ),
    "IDimXpertFilletFeature": (
        "Inner",
        "Radius",
    ),
    "IDimXpertFlatnessTolerance": (),
    "IDimXpertGtol": ("Annotation",),
    "IDimXpertIntersectCircleFeature": (),
    "IDimXpertIntersectLineFeature": (),
    "IDimXpertIntersectPlaneFeature": (),
    "IDimXpertIntersectPointFeature": (),
    "IDimXpertLineProfileTolerance": ("OuterToleranceValue",),
    "IDimXpertOrientationTolerance": (
        "Modifier",
        "ZoneType",
    ),
    "IDimXpertPart": (
        "ShowToleranceStatus",
        "ShowToleranceStatus",
    ),
    "IDimXpertPatternFeature": ("PatternType",),
    "IDimXpertPlaneFeature": (),
    "IDimXpertPositionTolerance": (
        "Modifier",
        "ZoneType",
    ),
    "IDimXpertRadiusDimTol": ("PatternTreatment",),
    "IDimXpertRefPlaneFeature": (),
    "IDimXpertSphereFeature": ("Inner",),
    "IDimXpertStraightnessTolerance": (
        "Modifier",
        "ZoneType",
    ),
    "IDimXpertSurfaceProfileTolerance": ("OuterToleranceValue",),
    "IDimXpertSymmetryTolerance": ("Modifier",),
    "IDimXpertTangencyTolerance": ("OriginFeature",),
    "IDimXpertTolerance": ("Tolerance",),
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
            f"本清单没有这个族: {family}（swdimxpert 共 {len(ARITY)} 族）。"
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
