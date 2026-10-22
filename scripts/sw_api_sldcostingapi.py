r"""SolidWorks sldcostingapi 官方接口全量索引。

能力域
    SolidWorks Composer / Costing（**需独立许可**）

本模块是什么
------------
**官方 API 的完整抄录** —— 14 个接口族、**81 个成员**，
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
    D:\AI\SW\_raw\reflect\iface_sldcostingapi.txt
      对 **SolidWorks.Interop.sldcostingapi.dll** 的纯元数据反射（AGENTS.md §四.1③）。
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
# 仓库:   官方 interop 程序集的纯元数据反射（SolidWorks.Interop.sldcostingapi.dll）
# 文件:   D:\AI\SW\_raw\reflect\iface_sldcostingapi.txt
# 定位:   14 个接口族的**全量**能力登记表 {族: {能力名: 实参个数}}。
# ⚑ 逐条机械生成，**不手抄、不折叠、不合并重载**。
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = ["ASSEMBLY", "FAMILIES", "ARITY", "PROPERTIES", "call_index"]

ASSEMBLY = "sldcostingapi"

FAMILIES: tuple[str, ...] = (
    "ICostAnalysis",
    "ICostAnalysis3dPrinting",
    "ICostAnalysisCasting",
    "ICostAnalysisMachining",
    "ICostAnalysisPlastic",
    "ICostAnalysisSheetMetal",
    "ICostAnalysisStructural",
    "ICostBlankSize",
    "ICostBody",
    "ICostFeature",
    "ICostManager",
    "ICostPart",
    "ICostingDefaults",
    "ITemplateOverrides",
)

#: 全量能力登记表 {族: {能力名: 实参个数}}（排除 by-ref 出参）
ARITY: dict[str, dict[str, int]] = {
    "ICostAnalysis": {
        "GetFirstCostFeature": 0,
        "GetManufacturingCost": 0,
        "GetMaterialCost": 0,
        "GetSetupCost": 0,
        "GetSpecificAnalysis": 0,
        "GetTotalCostToCharge": 0,
        "GetTotalCostToManufacture": 0,
    },
    "ICostAnalysis3dPrinting": {
        "GetMaterialClasses": 0,
        "GetMaterialClassesCount": 0,
        "GetMaterialCount": 1,
        "GetMaterials": 1,
        "ResetShopRate": 0,
    },
    "ICostAnalysisCasting": {
        "GetMaterialClasses": 0,
        "GetMaterialClassesCount": 0,
        "GetMaterialCount": 1,
        "GetMaterials": 1,
        "ResetShopRate": 0,
    },
    "ICostAnalysisMachining": {
        "GetBlankDimensionCount": 1,
        "GetMarginDimensionCount": 0,
        "GetMaterialClasses": 0,
        "GetMaterialClassesCount": 0,
        "GetMaterialCount": 1,
        "GetMaterials": 1,
        "GetMinimumBlankSize": 0,
        "GetStockTypeCount": 2,
        "GetStockTypes": 2,
        "ResetShopRate": 0,
    },
    "ICostAnalysisPlastic": {
        "GetMaterialClasses": 0,
        "GetMaterialClassesCount": 0,
        "GetMaterialCount": 1,
        "GetMaterials": 1,
        "ResetShopRate": 0,
    },
    "ICostAnalysisSheetMetal": {
        "GetMaterialClasses": 0,
        "GetMaterialClassesCount": 0,
        "GetMaterialCount": 1,
        "GetMaterials": 1,
        "GetModelThickness": 0,
        "GetThicknesses": 2,
        "GetThicknessesCount": 2,
    },
    "ICostAnalysisStructural": {
        "GetMaterialClasses": 0,
        "GetMaterialClassesCount": 0,
        "GetMaterialCount": 1,
        "GetMaterials": 1,
        "ResetShopRate": 0,
        "SetCurrentProfile": 3,
    },
    "ICostBlankSize": {},
    "ICostBody": {
        "AssignCustomCost": 1,
        "CreateCostAnalysis": 1,
        "GetBodyType": 0,
        "GetCostAnalysis": 0,
        "GetName": 0,
        "GetSWBody": 0,
    },
    "ICostFeature": {
        "GetFirstSubFeature": 0,
        "GetNextFeature": 0,
        "GetNextSubFeature": 0,
        "GetType": 0,
        "RemoveOverrideCostTime": 0,
        "SelectFaces": 0,
    },
    "ICostManager": {
        "Close": 0,
        "GetTemplateCount": 1,
        "GetTemplatePathnames": 1,
        "WaitForUIUpdate": 0,
    },
    "ICostPart": {
        "ActivateBody": 1,
        "CreateCostAnalysis": 1,
        "GetBodies": 0,
        "GetBodyCount": 0,
        "GetCostAnalysis": 0,
        "GetCostingMethod": 1,
        "IncludeBody": 2,
        "SetCostingMethod": 2,
        "UpdateCostForAllBodies": 0,
    },
    "ICostingDefaults": {
        "GetManufacturingMethod": 1,
        "GetMaterialClass": 1,
        "GetMaterialName": 1,
        "GetTemplateName": 1,
        "SetManufacturingMethod": 2,
        "SetMaterialClass": 2,
        "SetMaterialName": 2,
        "SetTemplateName": 2,
    },
    "ITemplateOverrides": {
        "ApplyOverrides": 0,
        "ResetAll": 0,
        "SaveCostingOverrideSettings": 0,
    },
}

#: 属性名（反射里是 get_/set_，**不是方法**；这里只留去掉前缀的名字）
PROPERTIES: dict[str, tuple[str, ...]] = {
    "ICostAnalysis": (
        "CostingTemplateName",
        "CostingType",
        "CurrencyCode",
        "CurrencyName",
        "CurrencySeparator",
        "LengthUnit",
        "LotSize",
        "LotSize",
        "MarkUpPercent",
        "MarkUpPercent",
        "MarkUpType",
        "MarkUpType",
        "MassUnit",
        "TotalQuantity",
        "TotalQuantity",
        "UnitSystem",
    ),
    "ICostAnalysis3dPrinting": (
        "CurrentMaterial",
        "CurrentMaterial",
        "CurrentMaterialClass",
        "CurrentMaterialClass",
        "FlipDirection",
        "FlipDirection",
        "OrientationPlane",
        "OrientationPlane",
        "PercentInfill",
        "PercentInfill",
        "ShopRate",
        "ShopRate",
        "ShopRateApplied",
        "ShopRateApplied",
        "StructuralMaterialCost",
        "StructuralMaterialCost",
        "WallThickness",
        "WallThickness",
    ),
    "ICostAnalysisCasting": (
        "CurrentMaterial",
        "CurrentMaterial",
        "CurrentMaterialClass",
        "CurrentMaterialClass",
        "CycleTime",
        "CycleTime",
        "MoldCost",
        "MoldCost",
        "PercentWasteMaterial",
        "PercentWasteMaterial",
        "ShopRate",
        "ShopRate",
        "ShopRateApplied",
        "ShopRateApplied",
    ),
    "ICostAnalysisMachining": (
        "BlankSize",
        "BlankSize",
        "CurrentMaterial",
        "CurrentMaterial",
        "CurrentMaterialClass",
        "CurrentMaterialClass",
        "CurrentPlateThickness",
        "CurrentPlateThickness",
        "CurrentStockType",
        "CurrentStockType",
        "CustomStockBodyName",
        "CustomStockBodyName",
        "CustomStockCostInfoType",
        "CustomStockCostInfoType",
        "CustomStockCustomCost",
        "CustomStockCustomCost",
        "CustomStockImportType",
        "CustomStockImportType",
        "IBlankSize",
        "IBlankSize",
        "IMargins",
        "IMargins",
        "Margins",
        "Margins",
        "PreviewShown",
        "PreviewShown",
        "ShopRate",
        "ShopRate",
        "ShopRateApplied",
        "ShopRateApplied",
        "SpecificSizeEnabled",
        "SpecificSizeEnabled",
    ),
    "ICostAnalysisPlastic": (
        "CalculationMethod",
        "CalculationMethod",
        "CurrentMaterial",
        "CurrentMaterial",
        "CurrentMaterialClass",
        "CurrentMaterialClass",
        "CycleTime",
        "CycleTime",
        "MaxWallThickness",
        "MaxWallThickness",
        "MoldCost",
        "MoldCost",
        "PercentWasteMaterial",
        "PercentWasteMaterial",
        "RunnerSystem",
        "RunnerSystem",
        "ShopRate",
        "ShopRate",
        "ShopRateApplied",
        "ShopRateApplied",
    ),
    "ICostAnalysisSheetMetal": (
        "BlankAreaFromModel",
        "BlankOffset",
        "BlankOffset",
        "BlankSizeType",
        "BlankSizeType",
        "CurrentMaterial",
        "CurrentMaterial",
        "CurrentMaterialClass",
        "CurrentMaterialClass",
        "CurrentThickness",
        "CurrentThickness",
        "CustomBlankArea",
        "CustomBlankArea",
        "CustomBlankSize",
        "CustomBlankSize",
        "FinalAreaFromModel",
        "MaterialCost",
        "MaterialCost",
        "MaterialCostFromTemplate",
        "PreviewShown",
        "PreviewShown",
        "Weight",
    ),
    "ICostAnalysisStructural": (
        "CurrentCostMethodType",
        "CurrentCostMethodType",
        "CurrentMaterial",
        "CurrentMaterial",
        "CurrentMaterialClass",
        "CurrentMaterialClass",
        "CurrentProfileSize",
        "CurrentProfileStandard",
        "CurrentProfileType",
        "CurrentStockUnitLength",
        "CurrentStockUnitLength",
        "ShopRate",
        "ShopRate",
        "ShopRateApplied",
        "ShopRateApplied",
    ),
    "ICostBlankSize": (
        "Length",
        "Length",
        "Width",
        "Width",
    ),
    "ICostBody": ("BodyStatus",),
    "ICostFeature": (
        "CombinedCost",
        "CombinedCost",
        "CombinedTime",
        "CombinedTime",
        "Description",
        "IsOverridden",
        "IsSetup",
        "Name",
        "Name",
    ),
    "ICostManager": (
        "CostingDefaults",
        "CostingModel",
    ),
    "ICostPart": (
        "ActiveBody",
        "TemplateOverrides",
    ),
    "ICostingDefaults": (
        "LotSizeForMultibody",
        "LotSizeForMultibody",
        "LotSizeForSingleBody",
        "LotSizeForSingleBody",
        "MachiningStockBodyType",
        "MachiningStockBodyType",
        "SheetmetalBlankSizeType",
        "SheetmetalBlankSizeType",
        "StructuralMemberStockType",
        "StructuralMemberStockType",
        "TotalNumberOfPartsForMultibody",
        "TotalNumberOfPartsForMultibody",
        "TotalNumberOfPartsForSingleBody",
        "TotalNumberOfPartsForSingleBody",
    ),
    "ITemplateOverrides": (
        "CustomBendCost",
        "CustomBendCost",
        "CustomHemCost",
        "CustomHemCost",
        "CustomLibraryFeatureCost",
        "CustomLibraryFeatureCost",
        "DefaultFinishingOperation",
        "DefaultFinishingOperation",
        "DefaultMachiningOperationTool",
        "DefaultMachiningOperationTool",
        "FinishingCostPerVolume",
        "FinishingCostPerVolume",
        "FinishingOffset",
        "FinishingOffset",
        "RemovedMaterialProcessingType",
        "RemovedMaterialProcessingType",
        "RoughingCostPerVolume",
        "RoughingCostPerVolume",
        "SemiFinishingCostPerVolume",
        "SemiFinishingCostPerVolume",
        "SemiFinishingOffset",
        "SemiFinishingOffset",
        "ShowUndeterminedSlotsInNCAFolder",
        "ShowUndeterminedSlotsInNCAFolder",
        "SlotFeatureRecognitionType",
        "SlotFeatureRecognitionType",
        "UseCustomBendCost",
        "UseCustomBendCost",
        "UseCustomHemCost",
        "UseCustomHemCost",
        "UseCustomLibraryFeatureCost",
        "UseCustomLibraryFeatureCost",
        "UseOffsetBasedFinishing",
        "UseOffsetBasedFinishing",
        "VolumeFeatureCalculationType",
        "VolumeFeatureCalculationType",
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
            f"本清单没有这个族: {family}（sldcostingapi 共 {len(ARITY)} 族）。"
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
