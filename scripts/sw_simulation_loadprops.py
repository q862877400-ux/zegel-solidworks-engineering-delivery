"""SolidWorks Simulation 载荷对象属性：ICWForce / ICWPressure / ICWHeatFlux /
ICWContactSet / ICWMaterial 的装配封装。

能力域
    域 13 · 仿真（需许可证）

模块分工（Simulation 域共五件套）
--------------------------------
    sw_simulation.py          addin 入口 + 端到端骨架
    sw_simulation_loads.py    载荷夹具 24 个 Add* 方法（创建）
    sw_simulation_study.py    研究管理与求解
    sw_simulation_results.py  结果云图与网格质量
    sw_simulation_loadprops.py（本文件）**创建之后**的属性装配

为什么单独成文件
----------------
24 个 ``Add*`` 只负责「造出对象」，**数值、单位、方向、摩擦这些真正的工程参数
是在返回对象上设属性**的。本模块封装的就是这一层 —— 工程师实际要填的那些值。
这层不做，「能创建载荷」就只是句空话。

⚑ 本模块的核心发现：编辑事务
----------------------------
反射 `ICWForce` 段首两个成员是 ``ForceBeginEdit()`` / ``ForceEndEdit()``（均零参），
`ICWContactSet` 段首两个是 ``ContactSetBeginEdit()`` / ``ContactSetEndEdit()``
（同样零参）。**同形的一对** ⇒ 这是载荷/接触对象的**通用约定**，
不是某个接口的特例。

⇒ **设属性必须在 Begin/End 之间**。本模块所有装配函数一律
  ``begin → 设 → finally end``，异常路径也收尾，不让编辑事务悬着。
⇒ 据此**回头改了 scripts/sw_simulation.py::apply_normal_force** ——
   它初稿直接设属性、没开事务。已在该处标注补正原因。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt   （对 interop 纯元数据反射）
    D:\\AI\\SW\\_raw\\reflect\\enum_cosworks.txt     （枚举取值）

⚠ 这五个族**官方 CHM 都没有文档页**（cosworks 册只覆盖
  ICWLoadsAndRestraintsManager 一族），故**只有签名、没有参数语义**。
  各函数处逐条标注这一点；不给未查证的参数编「合理解释」。

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
# 文件:   scripts/sw_simulation_loadprops.py —— 本文件自身
# 定位:   模块导出清单与枚举表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "FORCE_BEGIN_EDIT",
    "CONTACT_SET_BEGIN_EDIT",
    "edit_transaction",
    "configure_force",
    "configure_pressure",
    "configure_heat_flux",
    "configure_contact_set",
    "read_material_card",
    "collect_load_property_evidence",
]

#: 各对象的编辑事务入口（反射确认均零参）
FORCE_BEGIN_EDIT = ("ForceBeginEdit", "ForceEndEdit")
CONTACT_SET_BEGIN_EDIT = ("ContactSetBeginEdit", "ContactSetEndEdit")


def _require(target, what: str):
    if target is None:
        raise ValueError(f"{what} 为 None")
    return target


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
#           → ICWForce 段首两个成员 + ICWContactSet 段首两个成员
# 定位:   编辑事务。官方签名逐条照抄：
#     ICWForce       : Void  ForceBeginEdit()          ← **零参**
#                       Int32  ForceEndEdit()           ← **零参**，返回 Int32
#     ICWContactSet  : Void  ContactSetBeginEdit()     ← **零参**
#                       Int32  ContactSetEndEdit()      ← **零参**，返回 Int32
# ⚠ EndEdit 返回 Int32，**语义未注明**（可能是错误码）。本函数**透传返回值**，
#   不据此判成败 —— 官方没说它是什么。
# ⚠ Begin 的返回是 Void，若它抛异常，finally 里的 End 也会在事务未开的情况下被调；
#   本实现只在 begin 成功后才进入 try。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def edit_transaction(target, begin_end: tuple[str, str], what: str):
    """返回一个上下文管理器，在其中安全地修改载荷/接触对象属性。

    用法::

        with edit_transaction(force, FORCE_BEGIN_EDIT, "ICWForce"):
            get_com_member(force, "NormalForceOrTorqueValue", 100.0)

    异常路径也会调用 EndEdit，不让编辑事务悬着。
    """
    begin, end = begin_end

    class _Tx:
        def __enter__(self_inner):
            _require(target, what)
            #: dispatch-arg: dynamic `begin` 由 `begin_end` 形参解包而来（BeginEdit 成员名由调用方给）
            get_com_member(target, begin)
            return target

        def __exit__(self_inner, exc_type, exc, tb):
            #: dispatch-arg: dynamic `end` 由 `begin_end` 形参解包而来（EndEdit 成员名由调用方给）
            get_com_member(target, end)
            return False   # 不吞异常

    return _Tx()


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt → ICWForce 段的 set_ 成员
# 定位:   力的属性装配。官方 setter 逐条照抄（**全部是属性**，不是方法）：
#     set_ForceType(Int32) / set_Unit(Int32) / set_NormalForceOrTorqueValue(Double)
#     set_PhaseAngle(Double) / set_PhaseAngleUnit(Int32)
#     set_Equation(String) / set_EquationLinearUnit(Int32) /
#     set_EquationAngularUnit(Int32) / set_EquationCoordinateSystemType(Int32)
#     set_IncludeNonUniformDistribution(Int32) / set_IncludeNonUniformDistribution2(Boolean)
# ⚑ 名称歧义提示: IncludeNonUniformDistribution 有 **Int32 与 Boolean 两个版本**
#   （Reflection 确认 `get_IncludeNonUniformDistribution` 返回 Int32、
#   `get_IncludeNonUniformDistribution2` 返回 Boolean）—— **不是新旧版替代**，
#   是两个不同签名的成员。本模块**只碰 Boolean 版**，不混用。
# ⚠ 本族**无官方文档页** ⇒ Unit / PhaseAngleUnit 等枚举名查不到，
#   只做 int 透传，不设默认值。ForceType 的枚举见 sw_simulation_loads.py。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def configure_force(
    force,
    *,
    magnitude: float | None = None,
    force_type: int | None = None,
    unit: int | None = None,
    phase_angle: float | None = None,
    phase_angle_unit: int | None = None,
    equation: str | None = None,
    equation_linear_unit: int | None = None,
    equation_angular_unit: int | None = None,
    equation_coordinate_system: int | None = None,
    include_non_uniform: bool | None = None,
) -> dict[str, Any]:
    """装配 ICWForce（自动包在编辑事务里）。返回实际设置了的项。"""
    _require(force, "force")
    applied: dict[str, Any] = {}
    with edit_transaction(force, FORCE_BEGIN_EDIT, "ICWForce"):
        if force_type is not None:
            set_com_member(force, "ForceType", int(force_type))
            applied["ForceType"] = int(force_type)
        if unit is not None:
            set_com_member(force, "Unit", int(unit))
            applied["Unit"] = int(unit)
        if magnitude is not None:
            #: ★★★★★ 2026-10-10 **修一处真 bug（★ 本仓自己的纪律被违反）**：
            #: ★ 原来这里写的是 `get_com_member(force, "NormalForceOrTorqueValue", 值)` 
            #: ✗
            #: ★★ 而 `get_com_member` 的语义是「**取或调**」（★ 有实参 ⇒ **一定调用**）—
            #: —
            #:     `NormalForceOrTorqueValue` 是**可写属性**（★ 不是方法）⇒
            #:     ★★ 它**不是「找不到成员」**，而是**取回来是个 `float`、不可调用** ⇒
            #:     ★ 于是 `get_com_member` **抛 `TypeError`** ⇒ ★ **力的大小从来没设上** ✗
            #:   ★★★ **后果（★ 真机实测）**：★ 求解弹窗报「★ **未定义载荷或规定的位移**」
            #:     +「固定-刚性零件上的载荷将不处于活动状态」⇒ ★ **求解被前置检查拦住** ✓
            #: ★★ **正解在本仓早已写明** —— `sw_connect.set_com_member` 的 docstring 逐
            #: 字：
            #: 「★★ 与已知事实 4（读用 `get_com_member`）成对：★ **读走 `get_com_member`
            #: ，
            #:       ★ 写走本函数**」✓
            #:   ★ 故此处改用 `set_com_member`（★ 下面 `PhaseAngle` 等三处同病同修）。
            set_com_member(force, "NormalForceOrTorqueValue", float(magnitude))
            applied["NormalForceOrTorqueValue"] = float(magnitude)
        if phase_angle is not None:
            set_com_member(force, "PhaseAngle", float(phase_angle))
            applied["PhaseAngle"] = float(phase_angle)
        if phase_angle_unit is not None:
            set_com_member(force, "PhaseAngleUnit", int(phase_angle_unit))
            applied["PhaseAngleUnit"] = int(phase_angle_unit)
        if equation is not None:
            set_com_member(force, "Equation", str(equation))
            applied["Equation"] = str(equation)
        if equation_linear_unit is not None:
            set_com_member(force, "EquationLinearUnit", int(equation_linear_unit))
            applied["EquationLinearUnit"] = int(equation_linear_unit)
        if equation_angular_unit is not None:
            set_com_member(force, "EquationAngularUnit", int(equation_angular_unit))
            applied["EquationAngularUnit"] = int(equation_angular_unit)
        if equation_coordinate_system is not None:
            set_com_member(force, "EquationCoordinateSystemType",
                           int(equation_coordinate_system))
            applied["EquationCoordinateSystemType"] = int(equation_coordinate_system)
        if include_non_uniform is not None:
            set_com_member(force, "IncludeNonUniformDistribution2",
                           bool(include_non_uniform))
            applied["IncludeNonUniformDistribution2"] = bool(include_non_uniform)
    return applied


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt → ICWPressure 段
# 定位:   压力属性。**ICWPressure 段里只有 get_，本模块不设任何属性** ——
#   反射未列出任何 set_，故「压力值」要么在 AddPressure 的入参里、
#   要在别处。**不臆造 setter**。
#   仅提供只读回读：
#     get_PressureType() / get_CoordSystemType() / get_DirectionType()
#     get_PhaseAngle() / get_PhaseAngleUnit() / get_ReverseDirection2()
# ⚑ ReverseDirection 与 ReverseDirection2 并存（Int32 / Boolean 各一），
#   回读取 Boolean 版 2。
# ⚠ 本族**无官方文档页** ⇒ 各枚举名查不到，只透传。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def configure_pressure(pressure, *, reverse_direction: bool | None = None
                       ) -> dict[str, Any]:
    """回读（并按反射可写时设置）压力属性。

    ⚠ 反射的 ICWPressure 段**没有任何 set_**，故本函数当前**只读不写**；
       保留 ``reverse_direction`` 参数是为将来官方补上 setter 时可直接启用，
       现阶段传了也**不会生效**（不会静默假装成功 —— 见下方 raise）。
    """
    _require(pressure, "pressure")
    if reverse_direction is not None:
        raise ValueError(
            "ICWPressure 的反射清单里没有任何 setter，"
            "压力方向当前不可通过脚本设置；该参数被显式拒绝而不是静默忽略"
        )
    return {
        "pressure_type": int(get_com_member(pressure, "PressureType") or -1),
        "coord_system_type": int(get_com_member(pressure, "CoordSystemType") or -1),
        "direction_type": int(get_com_member(pressure, "DirectionType") or -1),
        "phase_angle": float(get_com_member(pressure, "PhaseAngle") or 0.0),
        "reverse_direction": bool(
            get_com_member(pressure, "ReverseDirection2")),
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt → ICWHeatFlux 段
# 定位:   热流属性。同 ICWPressure：反射只列出 get_，**无 setter**。
#   可读：get_HFValue() / get_Unit() / get_PerUnitLength2() /
#         get_ReverseDirection2() / get_UseTimeCurve2() / get_UseTemperatureCurve2()
# ⚠ 热流**值**由 AddHeatFlux 返回的对象携带，但反射未见 setter
#   ⇒ 疑似只能在 GUI 改，或走本模块未覆盖的其它族。
#   **不编一个「应该能设」的封装**，只如实回读并说明。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def configure_heat_flux(heat_flux) -> dict[str, Any]:
    """回读热流属性。⚠ 反射无 setter，故**只读不写**。"""
    _require(heat_flux, "heat_flux")
    return {
        "value": float(get_com_member(heat_flux, "HFValue") or 0.0),
        "unit": int(get_com_member(heat_flux, "Unit") or -1),
        "per_unit_length": bool(get_com_member(heat_flux, "PerUnitLength2")),
        "reverse_direction": bool(get_com_member(heat_flux, "ReverseDirection2")),
        "use_time_curve": bool(get_com_member(heat_flux, "UseTimeCurve2")),
        "use_temperature_curve": bool(
            get_com_member(heat_flux, "UseTemperatureCurve2")),
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt → ICWContactSet 段
# 定位:   接触对设置。官方签名逐条照抄：
#     Void  ContactSetBeginEdit()      ← **零参**，与 ForceBeginEdit 同形
#     Int32 ContactSetEndEdit()        ← **零参**
#     Double get_FrictionValue() / get_ClearanceValue() / get_AxialStiffnessValue()
#     Int32  get_ClearanceUnit() / get_ResistanceUnit() / get_ContactSetType()
#     Int32  get_GapType() / get_ResistanceType() / get_Options()
#     String get_ContactName()
#     Int32  get_IncludeFriction() / get_IncludeFriction2()
# ⚠ 反射的 ICWContactSet 段**同样没有 set_**（只有 Begin/End 两个方法 +
#   一堆 get_ 属性）⇒ 本函数**只读不写**，与压力/热流一致。
#   有趣的是：它有编辑事务入口却没有 setter。
#   可能是 setter 定义在别的接口上，或本版本未导出。
#   **两种可能都没排除，故不下「不可写」的结论**，只如实说「本族反射未见 setter」。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def configure_contact_set(contact_set) -> dict[str, Any]:
    """回读接触对设置。⚠ 反射未见 setter，故**只读不写**。"""
    _require(contact_set, "contact_set")
    return {
        "name": str(get_com_member(contact_set, "ContactName") or ""),
        "set_type": int(get_com_member(contact_set, "ContactSetType") or -1),
        "include_friction": bool(get_com_member(contact_set, "IncludeFriction2")),
        "friction_value": float(get_com_member(contact_set, "FrictionValue") or 0.0),
        "clearance_value": float(get_com_member(contact_set, "ClearanceValue") or 0.0),
        "clearance_unit": int(get_com_member(contact_set, "ClearanceUnit") or -1),
        "axial_stiffness": float(
            get_com_member(contact_set, "AxialStiffnessValue") or 0.0),
        "gap_type": int(get_com_member(contact_set, "GapType") or -1),
        "resistance_type": int(get_com_member(contact_set, "ResistanceType") or -1),
        "resistance_unit": int(get_com_member(contact_set, "ResistanceUnit") or -1),
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt → ICWMaterial 段
# 定位:   材料卡回读。反射列出的全是 **get_ 属性**（无 setter、无方法），
#   包含可辨识性字段（MaterialName / Category / Description / Count /
#   ModelType / MaterialUnits）与疲劳/超弹性相关字段
#   （SNCurve* / MooneyRivlinConstants / OgdenConstants / NoOfBulkModuli 等）。
# ⚠ **如何「取得」ICWMaterial 对象本身，反射里查不到入口** ——
#   ICWStudy 上没有 GetMaterial（已逐条核过 ICWStudy 63 个成员），
#   整个 cosworks 程序集里也**没有** GetMaterial 成员
#   （本地 vespo92/SolidworksMCP-TS 调用的 swStudy.GetMaterial 是不存在的成员）。
#   ⇒ 本函数**只接受已取到的对象**，不代为取材料。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def read_material_card(material) -> dict[str, Any]:
    """回读材料卡的可辨识字段。"""
    _require(material, "material")
    return {
        "name": str(get_com_member(material, "MaterialName") or ""),
        "category": str(get_com_member(material, "Category") or ""),
        "description": str(get_com_member(material, "Description") or ""),
        "count": int(get_com_member(material, "Count") or 0),
        "model_type": int(get_com_member(material, "ModelType") or -1),
        "material_units": int(get_com_member(material, "MaterialUnits") or -1),
        "include_creep": bool(get_com_member(material, "IncludeCreep2")),
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_simulation_study.py::collect_study_evidence）
# 定位:   载荷对象属性证据回读，沿用「只取已核实成员」的写法。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_load_property_evidence(force) -> dict[str, Any]:
    """回读 ICWForce 当前设置。读取的属性均为反射确认的 get_ 成员。"""
    _require(force, "force")
    return {
        "force_type": int(get_com_member(force, "ForceType") or -1),
        "unit": int(get_com_member(force, "Unit") or -1),
        "value": float(get_com_member(force, "NormalForceOrTorqueValue") or 0.0),
        "phase_angle": float(get_com_member(force, "PhaseAngle") or 0.0),
        "phase_angle_unit": int(get_com_member(force, "PhaseAngleUnit") or -1),
        "equation": str(get_com_member(force, "Equation") or ""),
        "has_coordinate_system": get_com_member(force, "GetCoordinateSystem") is not None,
        "has_time_curve": get_com_member(force, "GetTimeCurve") is not None,
    }
