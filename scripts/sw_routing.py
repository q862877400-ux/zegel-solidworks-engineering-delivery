"""SolidWorks Routers 线束/管线/导管路由：IRouteManager 与配套接口族封装。

能力域
    域 14 · 路由 / Composer / PDM（需许可证）

⚠⚑ 本模块是域 14 的**第一份真实 API 封装**
-------------------------------------
仓库里既有的 ``scripts/routing_review.py`` 名字里有 routing，但它
**完全不使用 COM API** —— 它只静态检查 ``SWRoutingLib.tlb`` 是否存在、
读注册表看加载项有没有注册。即：域 14 此前**零 API 覆盖**。
本模块是第一次真的把接口族用起来。

⚠⚑ 入口 ProgID **查不到**（AGENTS.md 铁律 5：查不到就说查不到）
------------------------------------------------------------
``IRouteManager`` 的正常取得路径应是
``ISldWorks.GetAddInObject(<ProgID>)``，但 **本机没有注册 Routing 加载项**
（读 ``HKLM:\\SOFTWARE\\SOLIDWORKS\\AddIns`` 下 Description 含 Routing/Route
的条目：0 条）—— SolidWorks Routers 是**独立许可产品**，本机没装。
反射清单里也只有接口与 coclass（RouteManager / Cable / Wire / Covering …），
**没有任何 addin 回调接口**（对比 Simulation 有 ``ICwAddincallback``）。

⇒ 本模块**不硬编 ProgID**、不代为取得 RouteManager，
  全部函数**接收调用方传进来的 ``IRouteManager``**。
  这不是偷懒，是没有依据就不写。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect\\iface_SWRoutingLib.txt
      —— 对 SolidWorks.Interop.SWRoutingLib.dll 的**纯元数据反射**，
         属 AGENTS.md §四.1③「读官方程序集，不是实测」。
         实测规模：**28 接口 / 142 成员**。

接口族覆盖（本模块 8 个 / 全库 28 个）
    IRouteManager(22) · IRoutingComponentManager(20) · IWire(20) ·
    IRouteProperty(11) · ICableProperty(5) · IWireProperty(5) ·
    ICovering(8) · ICable(7)

⚠ **本族官方 CHM 没有文档页**（四册 CHM 里没有 routing 册），
  故**只有签名、没有参数语义**。各函数处逐条标注；不编「合理解释」。

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""

from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member, set_com_member
except ImportError:
    from sw_connect import get_com_member, set_com_member

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_routing.py —— 本文件自身
# 定位:   模块导出清单与签名表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "ROUTING_ARITY",
    "start_route",
    "exit_route",
    "add_to_route",
    "edit_route",
    "create_route_line",
    "create_flatten_route",
    "create_pipe_drawing",
    "export_pipe_data",
    "export_tube_data",
    "get_all_route_segment_count",
    "get_electrical_route",
    "get_auto_route",
    "get_route_property",
    "get_routing_component_manager",
    "apply_covering",
    "set_bend_radius",
    "read_cable_card",
    "read_wire_endpoints",
    "set_wire_route_path",
    "collect_routing_evidence",
]

#: 反射确认的实参个数（**不含** by-ref 出参）
#: enum-gate: not-enum arity
#: arity-reflect: byref=excluded
ROUTING_ARITY: dict[str, int] = {
    # IRouteManager
    "StartRoute": 2,
    "ExitRoute": 0,
    "AddToRoute": 0,
    "EditRoute": 0,
    "CreateRouteLine": 6,
    "CreateFlattenRoute": 11,
    "CreatePipeDrawingforPipeRoute": 12,
    "ExportPipeData": 3,
    "ExportTubeData": 3,
    "GetAllRouteSegmentCount": 0,
    "GetElectricalRoute": 0,
    "GetAutoRoute": 0,
    "GetRouteProperty": 0,
    # IRoutingComponentManager
    "SetRouteTypeAndSubRouteType": 2,
    "SetComponentCrossSectionType": 1,
    "GetComponentRouteType": 0,
    "GetComponentCrossSectionType": 0,
    # IRouteProperty
    "AddCovering": 1,
    "CreateCovering": 0,
    "RemoveCovering": 0,
    "GetCovering": 0,
    "SetFixedLength": 1,
    "GetFixedLength": 0,
    "SetCPointConfiguration": 1,
    # IWire
    "SetRoutePathForWire": 1,
    "GetRouteSegmentIDsCount": 0,
    "GetRouteErrorsCount": 0,
    "GetCuttingLength": 0,
    # ICable / ICableProperty
    "GetCableProperty": 0,
    "GetCoresCount": 0,
    "GetCorePropertyCount": 0,
}


#: dispatch-guard: exempt internal-helper
def _checked(target, member: str, *args):
    """按签名表校核实参个数，通过后才发起调用（开发期护栏）。"""
    expected = ROUTING_ARITY.get(member)
    if expected is not None and expected != len(args):
        raise ValueError(
            f"{member} 官方签名是 {expected} 个实参（不含末尾 by-ref 出参），"
            f"本次调用给了 {len(args)} 个"
        )
    if target is None:
        raise ValueError("目标对象为 None")
    return get_com_member(target, member, *args)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SWRoutingLib interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt → IRouteManager 段
# 定位:   路由的起止与线段创建。官方签名逐条照抄：
#     Boolean StartRoute(String, String)                        → 2
#     Void   ExitRoute()                                        ← **零参**
#     Boolean AddToRoute()                                      ← **零参**
#     Void   EditRoute()                                        ← **零参**
#     Object CreateRouteLine(Double, Double, Double,
#                            Double, Double, Double)            → 6
#     Int32  CreateFlattenRoute(Int32, Int32, Double, Double, Int32, Boolean,
#                               String, String, String, String, Boolean) → 11
#     Void   CreatePipeDrawingforPipeRoute(String, String, Boolean, Boolean,
#                          Boolean, Boolean, Double, Double, String, String,
#                          Boolean, Int32)                       → 12
#     Int32  ExportPipeData(String, Int32, Int32)               → 3
#     Int32  ExportTubeData(String, Int32, Int32)               → 3
#     Int32  GetAllRouteSegmentCount()                          ← 零参
#     ElectricalRoute GetElectricalRoute()                      ← 零参
#     AutoRoute        GetAutoRoute()                           ← 零参
#     RouteProperty    GetRouteProperty()                       ← 零参
# ⚠ **本族无官方文档页**：CreateFlattenRoute 的 11 个参数、特别是两个 Double
#   （按位置在第 3、4 位）与 5 个 String 的含义，两套源都查不到。
#   本模块**只按位置透传**，参数名照抄反射声明顺序，注释里不给它们编解释。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def start_route(route_manager, route_type: str, from_point: str) -> bool:
    """开始一条路由。"""
    return bool(_checked(route_manager, "StartRoute", str(route_type), str(from_point)))


def exit_route(route_manager) -> bool:
    """结束路由。**零参**。"""
    _checked(route_manager, "ExitRoute")
    return True


def add_to_route(route_manager) -> bool:
    """把当前选择加进路由。**零参**。"""
    return bool(_checked(route_manager, "AddToRoute"))


def edit_route(route_manager) -> bool:
    """进入路由编辑态。**零参**。"""
    _checked(route_manager, "EditRoute")
    return True


def create_route_line(route_manager, x1, y1, z1, x2, y2, z2):
    """由两端点创建路由线段。⚠ 6 个 Double 的坐标系含义官方无文档。"""
    return _checked(
        route_manager,
        "CreateRouteLine",
        float(x1),
        float(y1),
        float(z1),
        float(x2),
        float(y2),
        float(z2),
    )


def create_flatten_route(route_manager, *args):
    """创建平面化路由（官方 11 参）。⚠ 参数语义无文档，按位置透传。"""
    if len(args) != 11:
        raise ValueError(
            f"CreateFlattenRoute 官方签名是 11 个实参，给了 {len(args)} 个"
        )
    return _checked(route_manager, "CreateFlattenRoute", *args)


def create_pipe_drawing(route_manager, *args):
    """创建管路图（官方 12 参）。⚠ 参数语义无文档，按位置透传。"""
    if len(args) != 12:
        raise ValueError(
            f"CreatePipeDrawingforPipeRoute 官方签名是 12 个实参，给了 {len(args)} 个"
        )
    return _checked(route_manager, "CreatePipeDrawingforPipeRoute", *args)


def export_pipe_data(route_manager, path: str, a: int, b: int) -> int:
    """导出管路数据。⚠ 两个 Int32 的含义官方无文档。"""
    return _checked(route_manager, "ExportPipeData", str(path), int(a), int(b))


def export_tube_data(route_manager, path: str, a: int, b: int) -> int:
    """导出导管数据。⚠ 同上。"""
    return _checked(route_manager, "ExportTubeData", str(path), int(a), int(b))


def get_all_route_segment_count(route_manager) -> int:
    """全部路由段数量。**零参**。"""
    return int(_checked(route_manager, "GetAllRouteSegmentCount") or 0)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）
# 文件:   D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt → IRouteManager 段
# 定位:   各子系统的取用入口（三个都是**零参方法**，不是属性）。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_electrical_route(route_manager):
    """取电气路由对象。"""
    return _checked(route_manager, "GetElectricalRoute")


def get_auto_route(route_manager):
    """取自动路由对象。"""
    return _checked(route_manager, "GetAutoRoute")


def get_route_property(route_manager):
    """取路由属性对象（IRouteProperty）。"""
    return _checked(route_manager, "GetRouteProperty")


def get_routing_component_manager(route_manager):
    """取路由元件管理器。

    ⚠ `IRouteManager` 反射清单里**没有**取它的成员
       （已逐条核过该段 22 个成员）⇒ 本函数**不做取用**，
       只提供「你手上已有这个对象时」的便捷别名。
       调用方须自行取得。
    """
    raise NotImplementedError(
        "IRouteManager 的反射清单里没有取 RoutingComponentManager 的成员。"
        "本机也没装 SolidWorks Routers（读 AddIns 注册表 0 条记录），"
        "故该取用路径查不到 —— 按铁律 5 不臆造。"
        "若你在装有 Routers 的机器上从别处取得该对象，"
        "可直接用 IRoutingComponentManager 的方法（见下方来源块）。"
    )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）→ IRouteProperty / ICovering 段
# 定位:   护套（Covering）与弯曲半径。官方签名逐条照抄：
#     IRouteProperty : Covering CreateCovering()      ← 零参
#                      Boolean  AddCovering(Covering) ← 1
#                      Void     RemoveCovering()      ← 零参
#                      Covering GetCovering()         ← 零参
#                      Int32    SetFixedLength(Double) ← 1
#                      Double   GetFixedLength()      ← 零参
#                      Void set_BendRadius(Double)    ← 属性
#                      Double get_BendRadius() / get_MinimumBendRadius()
#     ICovering      : Void set_Name(String) / set_PartNumber(String) /
#                              set_OuterDiameter(Double) / set_Color(Int32)
# ⚠ AddCovering 收的是 **coclass**（反射清单里既有接口 `ICovering` 也有
#   coclass `Covering`），调用方需自己构造 —— 本模块不代为 new。
# ⚠ **本族无官方文档页** ⇒ 不解释各参数的工程含义。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_covering(route_property):
    """新建一个护套定义。⚠ 需自行 AddCovering 才生效。"""
    return _checked(route_property, "CreateCovering")


def apply_covering(route_property, covering) -> bool:
    """把护套应用到路由。"""
    return bool(_checked(route_property, "AddCovering", covering))


def remove_covering(route_property) -> bool:
    """移除护套。**零参**。"""
    _checked(route_property, "RemoveCovering")
    return True


def set_bend_radius(route_property, radius: float) -> bool:
    """设弯曲半径。⚑ 官方是**属性**（set_BendRadius），不是方法。"""
    if route_property is None:
        raise ValueError("route_property 为 None")
    set_com_member(route_property, "BendRadius", float(radius))
    return True


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）→ ICable / ICableProperty 段
# 定位:   电缆卡。官方签名逐条照抄：
#     ICable         : String get_UserName() / set_UserName(String)
#                      CableProperty GetCableProperty()  ← 零参方法
#                      Int32    GetCoresCount()         ← 零参
#                      Object   GetCores()
#                      Double   GetCuttingLength()      ← 零参
#     ICableProperty : Double get_Diameter() / String get_Name()
#                      Object GetCoreProperties() / Int32 GetCorePropertyCount()
# ⚠ GetCores / GetCoreProperties 返回 SAFEARRAY，本模块**不代为分配**，
#   只透传。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def read_cable_card(cable) -> dict[str, Any]:
    """回读电缆卡信息。"""
    if cable is None:
        raise ValueError("cable 为 None")
    property_object = _checked(cable, "GetCableProperty")
    return {
        "user_name": str(get_com_member(cable, "UserName") or ""),
        "cores_count": int(get_com_member(cable, "GetCoresCount") or 0),
        "cutting_length": float(get_com_member(cable, "GetCuttingLength") or 0.0),
        "diameter": float(get_com_member(property_object, "Diameter") or 0.0),
        "name": str(get_com_member(property_object, "Name") or ""),
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）→ IWire 段
# 定位:   导线端点与路径。官方签名逐条照抄：
#     IWire : Void set_FromComponentReference(String) /
#                   set_ToComponentReference(String) /
#                   set_FromPinReference(String) / set_ToPinReference(String) /
#                   set_UserName(String)                       ← 全是**属性**
#             Int32   SetRoutePathForWire(Object)             ← 1
#             Int32   GetRouteSegmentIDsCount()               ← 零参
#             Int32   GetRouteErrorsCount()                   ← 零参
#             Double  GetCuttingLength()                      ← 零参
# ⚠ `SetRoutePathForWire(Object)` 的 Object 是路径数组，构造规则官方无说明。
# ⚠ 同形成员 ISetRoutePathForWire(Int32, Int32&) 是 COM 内部分发入口，
#   **不提供给调用方**。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def set_wire_route_path(wire, path) -> int:
    """给导线指定路径。"""
    return _checked(wire, "SetRoutePathForWire", path)


def read_wire_endpoints(wire) -> dict[str, Any]:
    """回读导线两端信息。"""
    if wire is None:
        raise ValueError("wire 为 None")
    return {
        "user_name": str(get_com_member(wire, "UserName") or ""),
        "from_component": str(get_com_member(wire, "FromComponentReference") or ""),
        "to_component": str(get_com_member(wire, "ToComponentReference") or ""),
        "from_pin": str(get_com_member(wire, "FromPinReference") or ""),
        "to_pin": str(get_com_member(wire, "ToPinReference") or ""),
        "segment_count": int(get_com_member(wire, "GetRouteSegmentIDsCount") or 0),
        "error_count": int(get_com_member(wire, "GetRouteErrorsCount") or 0),
        "cutting_length": float(get_com_member(wire, "GetCuttingLength") or 0.0),
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_simulation_study.py::collect_study_evidence）
# 定位:   路由状态证据回读，沿用「只取已核实成员」的写法。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_routing_evidence(route_manager) -> dict[str, Any]:
    """回读路由管理器状态。"""
    if route_manager is None:
        raise ValueError("route_manager 为 None")
    property_object = get_route_property(route_manager)
    return {
        "segment_count": get_all_route_segment_count(route_manager),
        "has_electrical_route": get_electrical_route(route_manager) is not None,
        "has_auto_route": get_auto_route(route_manager) is not None,
        "route_type": int(get_com_member(property_object, "RouteType") or -1),
        "has_covering": bool(get_com_member(property_object, "HasCovering")),
        "bend_radius": float(get_com_member(property_object, "BendRadius") or 0.0),
        "minimum_bend_radius": float(
            get_com_member(property_object, "MinimumBendRadius") or 0.0
        ),
    }
