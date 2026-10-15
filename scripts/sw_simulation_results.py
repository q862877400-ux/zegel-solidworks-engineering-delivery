"""SolidWorks Simulation 结果读取与网格检查：ICWResults / ICWMesh 封装。

能力域
    域 13 · 仿真（需许可证）

模块分工（三件套，本仓库 Simulation 域）
--------------------------------------
    sw_simulation.py         addin 入口 + 端到端骨架
    sw_simulation_loads.py   载荷夹具 24 个 Add* 方法
    sw_simulation_study.py   研究管理与求解（ICWStudyManager / ICWStudy）
    sw_simulation_results.py（本文件）**结果读取 / 云图绘图 / 网格质量**

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt   （对 interop 纯元数据反射）
    D:\\AI\\SW\\_raw\\reflect\\enum_cosworks.txt     （枚举取值）

⚠ **这两个接口族官方 CHM 没有文档页**（cosworks 册只覆盖
  ICWLoadsAndRestraintsManager 一个族），因此**没有参数语义说明**，
  只能按反射的声明顺序透传。已在各函数处逐条标注这一点。
  与 sw_simulation_study.py 同属「有签名、无语义」的一类。

⚑ 只做「读取」，不做「改结果」
--------------------------------
ICWResults 的绘图方法绝大多数以 by-ref 结束（``Int32&`` / ``Object&``），
迟到绑定下**不保证回写**。本模块因此：
  · 一律透传返回值，**不据其判成败**
  · 对需要 by-ref 出参的方法（如 GetDisplacementAtPoints），**不提供封装** ——
    输出缓冲的分配规则两套源都查不到，不臆造。

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_simulation_results.py —— 本文件自身
# 定位:   模块导出清单与枚举表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的
#         来源块（逐成员的反射签名）。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "SWS_NODAL_STRESS_COMPONENTS",
    "SWS_MESH_QUALITY",
    "SWS_MESHER_TYPES",
    "RESULTS_ARITY",
    "MESH_ARITY",
    "create_plot",
    "create_deformed_body",
    "activate_plot",
    "delete_plot",
    "get_displacement_at_points",
    "get_buckling_load_factors",
    "get_mesh_quality_report",
    "get_mesh_node_location",
    "get_mesh_element_location",
    "get_worst_jacobian_ratio",
    "is_component_failed",
    "collect_mesh_evidence",
]


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举（对 interop 程序集纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\enum_cosworks.txt
#         → swsStaticResultNodalStressComponentTypes_e / swsMeshQuality_e /
#           swsMesherType_e 段
# 定位:   结果分量、网格质量档位、网格器类型。取值逐个反射核出。
# ⚠ **位移分量 / 绘图类型的枚举名在反射 dump 里查不到**
#   （`swsStaticResultNodalDisplacementComponentTypes_e` 与
#    `swsResultPlotType_e` 均无该名）⇒ 本模块不臆造它们的名字，
#   相关参数一律 int 透传。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
#: enum-gate: enum swsStaticResultNodalStressComponentTypes_e
SWS_NODAL_STRESS_COMPONENTS = {
    "sx": 0, "sy": 1, "sz": 2,        # swsStaticNodalStress_SX / SY / SZ
    "txy": 3, "txz": 4, "tyz": 5,     # swsStaticNodalStress_TXY / TXZ / TYZ
    "p1": 6, "p2": 7, "p3": 8,        # swsStaticNodalStress_P1 / P2 / P3
}

SWS_MESH_QUALITY = {
    "draft": 0,     # swsMeshQualityDraft
    "high": 1,      # swsMeshQualityHigh
}

SWS_MESHER_TYPES = {
    "standard": 0,        # swsMesherTypeStandard
    "alternate": 1,       # swsMesherTypeAlternate
    "alternate_cb": 2,    # swsMesherTypeAlternateCB
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
#           → ICWResults 段 + ICWMesh 段
# 定位:   本模块全部封装的**官方实参个数**，逐条照抄反射清单。
#         **不含**末位 by-ref 出参（迟到绑定传 0/None 占位，见模块头）。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
#: enum-gate: not-enum arity
#: arity-reflect: byref=excluded
RESULTS_ARITY: dict[str, int] = {
    "CreatePlot": 4,
    "CreateDeformedBody": 2,
    "CreateDeformedBody2": 5,
    "ActivatePlot": 1,
    "DeletePlot": 1,
    "GetDisplacementAtPoints": 5,
    "GetBucklingLoadFactors": 0,
    "CreateStressHotSpotPlot": 2,
    "AddIsoClippingToPlot": 5,
}

#: arity-reflect: byref=excluded
MESH_ARITY: dict[str, int] = {
    "GetNodeLocation": 1,
    "GetElementLocation": 1,
    "GetWorstJacobianRatio": 0,
    "IsComponentFailed": 1,
    "IsComponentFailed2": 1,
    "GetNoOfFailedComponents": 0,
    "GetMeshControlAt": 1,
    "DeleteMeshControl": 1,
    "GetDefaultElementSizeAndTolerance": 1,
    "GetDefaultMaxAndMinElementSize": 1,
}


#: dispatch-guard: exempt internal-helper
def _checked(table: dict[str, int], target, member: str, *args):
    """按签名表校核实参个数，通过后才发起调用（开发期护栏）。"""
    expected = table.get(member)
    if expected is not None and expected != len(args):
        raise ValueError(
            f"{member} 官方签名是 {expected} 个实参（不含末尾 by-ref 出参），"
            f"本次调用给了 {len(args)} 个"
        )
    if target is None:
        raise ValueError("目标对象为 None")
    return get_com_member(target, member, *args)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt → ICWResults 段
# 定位:   云图与变形体。官方签名逐条照抄：
#     CWPlot CreatePlot(Int32 PlotType, Int32 Component, Int32 Step,
#                       Boolean ShowDeformation, Int32& ErrorCode)   → 4 + err
#     Void   CreateDeformedBody(Int32, String, Int32&)                → 2 + err
#     Int32  CreateDeformedBody2(Int32, Int32, Int32, String, String) → 5
#     Boolean ActivatePlot(String PlotName)                            → 1
#     Boolean DeletePlot(String PlotName)                              → 1
#     CWPlot CreateStressHotSpotPlot(Boolean, Boolean, Int32&)        → 2 + err
#     Int32  AddIsoClippingToPlot(String, Int32, Object, Boolean, Boolean) → 5
# ⚠ **本族无官方文档页**，上述参数的语义一律未注明 ——
#   尤其 CreatePlot 的 (PlotType, Component, Step) 三项分别指什么，
#   两套源都查不到。本模块**只按位置透传、参数名照抄反射的声明顺序**，
#   注释里不给它们编「合理解释」。
# ⚠ PlotType 的枚举名 `swsResultPlotType_e` 在反射 dump 里**不存在**，
#   故该参数只做 int 透传。应力分量用 SWS_NODAL_STRESS_COMPONENTS（有据）。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_plot(results, plot_type: int, component: int, step: int = 0,
                show_deformation: bool = False):
    """创建云图。⚠ 三个 Int32 参数的语义官方无文档，按位置透传。"""
    return _checked(RESULTS_ARITY, results, "CreatePlot",
                    int(plot_type), int(component), int(step), bool(show_deformation))


def create_deformed_body(results, plot_type: int, name: str = ""):
    """生成变形体。"""
    return _checked(RESULTS_ARITY, results, "CreateDeformedBody",
                    int(plot_type), str(name))


def activate_plot(results, plot_name: str) -> bool:
    """激活某张云图。"""
    return bool(_checked(RESULTS_ARITY, results, "ActivatePlot", str(plot_name)))


def delete_plot(results, plot_name: str) -> bool:
    """删除某张云图。"""
    return bool(_checked(RESULTS_ARITY, results, "DeletePlot", str(plot_name)))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt → ICWResults 段
# 定位:   结果数值读取。官方签名逐条照抄：
#     Object GetDisplacementAtPoints(Int32, Int32, Object, Object, Int32,
#                                    Int32& ErrorCode)                 → 5 + err
#     Object GetBucklingLoadFactors(Int32&)                            → 0 + err
# ⚠ GetDisplacementAtPoints 的前 4 参（两个 Int32 + 两个 Object）语义未注明。
#   典型用法是「(分量类型, 步, 点数组, 输出数组, 步号&, 错误码&)」，
#   但**官方文档没这么写**，故本模块不把该用法写进注释冒充官方说明，
#   只在参数名上如实反映反射的声明顺序。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_displacement_at_points(results, component: int, step: int,
                               points, out_values=None):
    """按点集取位移。⚠ 参数语义官方无文档，按位置透传。"""
    return _checked(RESULTS_ARITY, results, "GetDisplacementAtPoints",
                    int(component), int(step), points, out_values, 0)


def get_buckling_load_factors(results):
    """取屈曲载荷因子。"""
    return _checked(RESULTS_ARITY, results, "GetBucklingLoadFactors")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt → ICWMesh 段
# 定位:   网格质量诊断。官方签名逐条照抄：
#     Void  GetNodeLocation(Int32 NodeNo, Double& X, Double& Y, Double& Z) → 1
#     Void  GetElementLocation(Int32 ElemNo, Double& X, Double& Y, Double& Z) → 1
#     Double GetWorstJacobianRatio()                                   → **零参**
#     Int32  IsComponentFailed(String)                                 → 1
#     Boolean IsComponentFailed2(String)                               → 1
#     Int32  GetNoOfFailedComponents()                                 → 零参
# ⚠ GetNodeLocation / GetElementLocation 的后 3 参是 **by-ref 出参**，
#   迟到绑定下**不保证回写** ⇒ 本模块只透传返回值（返回 None），
#   **不提供坐标解析封装** —— by-ref VARIANT 的分配规则两套源都查不到。
#   这两个方法列在 MESH_ARITY 里是为了保留签名事实，不是为了取到坐标。
# ⚠ IsComponentFailed 返回 Int32 而 IsComponentFailed2 返回 Boolean ——
#   官方就是两个不同返回类型的方法，**不要当成新旧版互相替代**。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_mesh_node_location(mesh, node_number: int):
    """取节点坐标。⚠ 官方是 by-ref 出参，本封装**取不到坐标**，只透传。"""
    return _checked(MESH_ARITY, mesh, "GetNodeLocation", int(node_number))


def get_mesh_element_location(mesh, element_number: int):
    """取单元坐标。⚠ 同上，by-ref 出参取不到。"""
    return _checked(MESH_ARITY, mesh, "GetElementLocation", int(element_number))


def get_worst_jacobian_ratio(mesh) -> float:
    """取最差雅可比比（网格畸变指标）。**零参**。"""
    return float(_checked(MESH_ARITY, mesh, "GetWorstJacobianRatio") or 0.0)


def is_component_failed(mesh, component_name: str) -> bool:
    """判断组件是否网格失败。用 2 号（返回 Boolean）。"""
    return bool(_checked(MESH_ARITY, mesh, "IsComponentFailed2", str(component_name)))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（scripts/sw_simulation_study.py::collect_study_evidence）
# 定位:   网格状态证据回读，沿用「只取已核实成员」的写法。读取的全部是
#         ICWMesh 上反射确认为 Int32 / Double / Boolean 的属性。
# ⚑ 注意其中几个成员是**成对的**：get_X 与 get_X2（Int32 / Boolean 两种返回）。
#   本模块只取 Int32 版本（反射里更基础的那个），不混用。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_mesh_evidence(mesh) -> dict[str, Any]:
    """回读网格的整体质量指标。"""
    if mesh is None:
        raise ValueError("mesh 为 None")
    return {
        "element_count": int(get_com_member(mesh, "ElementCount") or 0),
        "node_count": int(get_com_member(mesh, "NodeCount") or 0),
        "mesh_type": int(get_com_member(mesh, "MeshType") or -1),
        "mesher_type": int(get_com_member(mesh, "MesherType") or -1),
        "quality": int(get_com_member(mesh, "Quality") or -1),
        "mesh_state": int(get_com_member(mesh, "MeshState") or -1),
        "is_mesh_failed": int(get_com_member(mesh, "IsMeshFailed") or 0) != 0,
        "element_size": float(get_com_member(mesh, "ElementSize") or 0.0),
        "min_element_size": float(get_com_member(mesh, "MinElementSize") or 0.0),
        "max_element_size": float(get_com_member(mesh, "MaxElementSize") or 0.0),
        "growth_ratio": float(get_com_member(mesh, "GrowthRatio") or 0.0),
        "max_aspect_ratio": float(get_com_member(mesh, "MaxAspectRatio") or 0.0),
        "jacobian_points": int(get_com_member(mesh, "JacobianPoints") or 0),
        "mesh_control_count": int(get_com_member(mesh, "MeshControlCount") or 0),
        "number_of_loops": int(get_com_member(mesh, "NumberOfLoops") or 0),
        "failed_component_count": int(
            get_com_member(mesh, "GetNoOfFailedComponents") or 0),
        "worst_jacobian_ratio": get_worst_jacobian_ratio(mesh),
    }
