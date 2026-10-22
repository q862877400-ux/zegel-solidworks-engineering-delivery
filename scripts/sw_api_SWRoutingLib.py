r"""SolidWorks SWRoutingLib 官方接口全量索引。

能力域
    SolidWorks Routers（**需独立许可**）

本模块是什么
------------
**官方 API 的完整抄录** —— 14 个接口族、**87 个成员**，
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
    D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt
      对 **SolidWorks.Interop.SWRoutingLib.dll** 的纯元数据反射（AGENTS.md §四.1③）。
    ⚠ 属「读官方程序集」，**不是实测**（铁律 2）。

⚠ 本模块为机械抄录，未在本机实测（见 AGENTS.md 铁律 2）。
"""

from __future__ import annotations


try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   官方 interop 程序集的纯元数据反射（SolidWorks.Interop.SWRoutingLib.dll）
# 文件:   D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt
# 定位:   14 个接口族的**全量**能力登记表 {族: {能力名: 实参个数}}。
# ⚑ 逐条机械生成，**不手抄、不折叠、不合并重载**。
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = ["ASSEMBLY", "FAMILIES", "ARITY", "PROPERTIES", "call_index"]

ASSEMBLY = "SWRoutingLib"

FAMILIES: tuple[str, ...] = (
    "IAdvancedRouteSelector",
    "IAutoRoute",
    "ICable",
    "ICableProperty",
    "ICovering",
    "IElectricalFlatRoute",
    "IElectricalRoute",
    "IElectricalRouteProperty",
    "IRibbonCable",
    "IRouteManager",
    "IRouteProperty",
    "IRoutingComponentManager",
    "IWire",
    "IWireProperty",
)

#: 全量能力登记表 {族: {能力名: 实参个数}}（排除 by-ref 出参）
ARITY: dict[str, dict[str, int]] = {
    "IAdvancedRouteSelector": {
        "Find": 4,
        "getAttachedComponentsCount": 1,
        "Select": 4,
        "SetSelectionColor": 2,
    },
    "IAutoRoute": {
        "ConvertGuidelinesToRoute": 0,
        "CreatePointToPointAutoRoute": 1,
        "CreateRouteThroughSketchEntities": 4,
        "DeleteAllGuidelines": 0,
        "MergeGuidelines": 0,
        "SelectGuidelines": 0,
        "ShowGuidelines": 0,
    },
    "ICable": {
        "GetCableProperty": 0,
        "GetCores": 0,
        "GetCoresCount": 0,
        "GetCuttingLength": 0,
    },
    "ICableProperty": {
        "GetCoreProperties": 0,
        "GetCorePropertyCount": 0,
    },
    "ICovering": {},
    "IElectricalFlatRoute": {
        "GetConnectorData": 1,
        "GetElectricalDrawingSettings": 0,
        "GetFittingFilePath": 1,
        "GetSketchSegments": 1,
        "GetSketchSegmentsCount": 1,
    },
    "IElectricalRoute": {
        "GetActiveRouteSketch": 0,
        "GetCables": 0,
        "GetCablesCount": 0,
        "GetRibbonCableDispatch": 0,
        "GetRouteProperty": 1,
        "GetRouteSegmentID": 1,
        "GetSketchSegments": 1,
        "GetSketchSegmentsCount": 1,
        "GetWires": 0,
        "GetWiresCount": 0,
        "RouteWires": 0,
    },
    "IElectricalRouteProperty": {},
    "IRibbonCable": {},
    "IRouteManager": {
        "AddToRoute": 0,
        "ChangeRoutingLibComponentPaths": 2,
        "CreateFlattenRoute": 11,
        "CreatePipeDrawingforPipeRoute": 12,
        "CreateRouteLine": 6,
        "EditRoute": 0,
        "ExitRoute": 0,
        "ExportPipeData": 3,
        "ExportTubeData": 3,
        "GetAdvancedRouteSelector": 0,
        "GetAllRouteSegmentCount": 0,
        "GetAllRouteSegmentIDs": 0,
        "GetAutoRoute": 0,
        "GetElectricalComponentFromSearchpath": 1,
        "GetElectricalFlatRoute": 1,
        "GetElectricalRoute": 0,
        "GetRouteProperty": 0,
        "GetRoutingComponentFromSearchpath": 1,
        "GetRoutingLibComponentReferences": 1,
        "ImportFromToList": 6,
        "StartRoute": 2,
    },
    "IRouteProperty": {
        "AddCovering": 1,
        "CreateCovering": 0,
        "GetCovering": 0,
        "GetFixedLength": 0,
        "RemoveCovering": 0,
        "SetFixedLength": 1,
    },
    "IRoutingComponentManager": {
        "CreateEndConnectorIllustration": 0,
        "GetComponentCrossSectionType": 0,
        "GetComponentRouteType": 0,
        "GetComponentRouteTypeFromCustomProperty": 0,
        "GetComponentType": 0,
        "GetComponentUserDefinedRouteTypeName": 0,
        "GetCPointConfiguration": 0,
        "GetRouteComponentSubType": 0,
        "GetRouteComponentTypeSetThrRLM": 0,
        "GetRoutingComponentDescription": 0,
        "GetRoutingStringValue": 1,
        "SetComponentCrossSectionType": 1,
        "SetComponentRouteTypeToCustomProperty": 1,
        "SetComponentType": 1,
        "SetComponentUserDefinedRouteTypeName": 1,
        "SetCPointConfiguration": 1,
        "SetRouteComponentSubType": 1,
        "SetRouteComponentTypeSetThrRLM": 1,
        "SetRouteTypeAndSubRouteType": 2,
        "SetRoutingComponentDescription": 1,
    },
    "IWire": {
        "GetCuttingLength": 0,
        "GetRouteErrors": 0,
        "GetRouteErrorsCount": 0,
        "GetRouteSegmentIDs": 0,
        "GetRouteSegmentIDsCount": 0,
        "GetWireProperty": 0,
        "SetRoutePathForWire": 1,
    },
    "IWireProperty": {},
}

#: 属性名（反射里是 get_/set_，**不是方法**；这里只留去掉前缀的名字）
PROPERTIES: dict[str, tuple[str, ...]] = {
    "IAdvancedRouteSelector": (),
    "IAutoRoute": (),
    "ICable": (
        "UserName",
        "UserName",
    ),
    "ICableProperty": (
        "Diameter",
        "Name",
    ),
    "ICovering": (
        "Color",
        "Color",
        "Name",
        "Name",
        "OuterDiameter",
        "OuterDiameter",
        "PartNumber",
        "PartNumber",
    ),
    "IElectricalFlatRoute": (),
    "IElectricalRoute": (),
    "IElectricalRouteProperty": (
        "BundleDiameter",
        "BundleDiameter",
        "BundleMinimumBendRadius",
        "IsOuterDiameterFixed",
        "IsOuterDiameterFixed",
        "OuterDiameter",
        "OuterDiameter",
        "SubType",
        "SubType",
    ),
    "IRibbonCable": (
        "GetRibbonCableThickness",
        "GetRibbonCableWidth",
    ),
    "IRouteManager": (),
    "IRouteProperty": (
        "BendRadius",
        "BendRadius",
        "HasCovering",
        "MinimumBendRadius",
        "RouteType",
    ),
    "IRoutingComponentManager": (),
    "IWire": (
        "FromComponentReference",
        "FromComponentReference",
        "FromPinReference",
        "FromPinReference",
        "ToComponentReference",
        "ToComponentReference",
        "ToPinReference",
        "ToPinReference",
        "UserName",
        "UserName",
    ),
    "IWireProperty": (
        "Color",
        "Diameter",
        "Name",
        "PartNumber",
        "Size",
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
            f"本清单没有这个族: {family}（SWRoutingLib 共 {len(ARITY)} 族）。"
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
