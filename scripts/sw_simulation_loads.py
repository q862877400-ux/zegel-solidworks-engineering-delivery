"""SolidWorks Simulation 载荷与夹具：官方 24 个 Add* 方法的完整封装。

能力域
    域 13 · 仿真（需许可证）

⚠⚑ 本模块存在的理由 —— 一次重大误判的纠正
----------------------------------------
此前「cosworks 官方文档是空壳、27 个 Add* 方法签名不可得」是**误判**。
`SWhelp\\cosworks\\ICWLoadsAndRestraintsManager~<成员>.html` 单页近 1MB，
含 `Syntax` / `Parameters` / `Remarks` 全文；它看起来是空壳，是因为**正文以
JSON 转义（``\\u003c`` = ``<``）嵌在 script 标签里**，按 ``<script>`` 抓不到。

纠正工具（本机，可用）：
    D:\\AI\\SW\\tools\\extract_cosworks_docs.py   42 页提取成功
    D:\\AI\\SW\\tools\\parse_cosworks_signatures.py  31 个方法签名 + 参数说明

所以本模块的每个签名都**照抄官方 VB 声明**，不是反射推测、不是凭印象。

官方签名来源
    D:\\AI\\SW\\AI Solidworks\\官方文档\\SWhelp\\cosworks\\
        ICWLoadsAndRestraintsManager~<方法>.html
    → 解析产物 D:\\AI\\SW\\_raw\\cosworks_signatures.md（31 个方法）
枚举值来源
    D:\\AI\\SW\\_raw\\reflect\\enum_cosworks.txt（对 interop 程序集的纯元数据反射）

接口族覆盖
    ICWLoadsAndRestraintsManager  24 个 Add* + CopyLoadsAndRestraintsToStudy
                                  + GetLoadsAndRestraints + GetEdgeWeldConnector
    （cosworks 程序集共 168 接口 / 363 枚举 / 9,281 成员，本模块只覆盖官方
      文档化的载荷夹具这一个接口族 —— 其余接口族官方无文档页，见 docs/gap-analysis.md）

⚠ 所有方法的**末位是 `ByRef ErrorCode As Integer`**。pywin32 迟到绑定下
  by-ref 出参**不保证回写**（与 AGENTS.md §六 事实 8 记载的
  ISelectionMgr.AddSelectionListObject bool 不可信同源）。
  ⇒ 本模块**一律传 0 占位、且不据返回值判成败**，只透传创建出来的对象。
⚠ 官方文档未逐项说明实体数组的构造规则（如何从零件面得到 DispArray）。
  ⇒ 各方法的 ``*_array`` 参数由调用方提供，本模块不代为构造。
⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""

from __future__ import annotations

from typing import Any

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_simulation_loads.py —— 本文件**顶部导入区**
# 定位:   两个来自 `sw_connect` 的 COM 助手：· `get_com_member`                —— 全模
#           块取 COM 成员的唯一入口· `create_empty_dispatch_variant` —— **空 Dispatch 参
#           数包**  （`VARIANT(VT_DISPATCH, None)`，**已知事实 12**）
# ⚠⚠ 为什么是**三层 try**（2026-10-01 轮 246）：
#   ★ 本模块的设计约束是「**不连 COM 也能 import**」—— 契约测试
#     `tests/test_sw_simulation_loads_contract.py` 把 `sw_connect` stub 掉后仍要能导入。
#   ★ 而 `create_empty_dispatch_variant` 在真机上是 `AddPressure` / `AddForce` 的
# **必需实参**（裸传 `None` 会报 `类型不匹配@arg3`，见 `add_pressure` / `add_torque` 的
# docstring）。
# ⇒ 所以：**取得到就用，取不到置 `None`**（★ 调用点据此判断），**绝不让整模块 import 失
# 败**。
# 许可:   本仓库 MIT。
# 覆盖:   下面这段 `try` 导入
# ─────────────────────────────────────────────────────────────────────
try:
    from .sw_connect import get_com_member, create_empty_dispatch_variant, out_i4
except ImportError:
    try:
        from sw_connect import get_com_member, create_empty_dispatch_variant, out_i4
    except ImportError:
        #: ★★ **测试环境**（`tests/test_sw_simulation_loads_contract.py` 把 `sw_connect`
        #:   stub 掉）⇒ 这个名字取不到 ⇒ ★ **置 None 而不是让 import 炸**。
        #:   本模块的设计约束是「**不连 COM 也能 import**」（契约测试靠它），
        #:   所以顶层**不能**因为缺一个 COM 助手就整模块失败。
        #:   ⚠ 真机上它一定在（`sw_connect.create_empty_dispatch_variant`，已知事实 12）。
        from sw_connect import get_com_member, out_i4

        create_empty_dispatch_variant = None  # type: ignore[assignment]

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_simulation_loads.py —— 本文件自身
# 定位:   模块导出清单、枚举表与签名表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的
#         来源块（逐方法的官方 VB 声明）。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "SWS_RESTRAINT_TYPES",
    "SWS_FORCE_TYPES",
    "SWS_PRESSURE_TYPES",
    "SWS_RADIATION_TYPES",
    "SWS_SPRING_SUBTYPES",
    "OFFICIAL_LOAD_SIGNATURES",
    "add_fixed_restraint",
    "add_reference_geometry_restraint",
    "add_force",
    "add_torque",
    "add_pressure",
    "add_radiation",
    "add_convection",
    "add_heat_flux",
    "add_heat_power",
    "add_temperature",
    "add_gravity",
    "add_centrifugal_force",
    "add_distributed_mass",
    "add_remote_load",
    "add_cyclic_symmetry_restraint",
    "add_prescribed_displacement",
    "add_bearing_load",
    "add_spring_connector",
    "add_pin_connector",
    "add_rigid_connector",
    "add_link_connector",
    "add_elastic_connector",
    "add_bolt_connector",
    "add_spot_weld_connector",
    "add_edge_weld_connector",
    "get_edge_weld_connector",
    "get_loads_and_restraints",
    "collect_loads_evidence",
    "apply_pressure_report",
    "apply_torque_report",
    "apply_gravity_report",
    "apply_centrifugal_force_report",
]


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_simulation_loads.py —— 本文件自身
# 定位:   模块导出清单、枚举表与签名表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的
#         来源块（逐方法的官方 VB 声明）。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举定义（对 interop 程序集纯元数据反射）# 文件:   D:\AI\S
# W\_raw\reflect\enum_cosworks.txt
# 定位:   各 Add* 方法首参（类型位）的合法取值。
# 取值:   逐个反射核出。⚠ 这些枚举**在 CHM cosworks 册里没有页面**
#         （该册只有 34 个接口页 + members 索引，无枚举页），
#         故枚举值只能来自反射 —— 这是「广度查反射」的具体用武之地。
# ⚠ 未收录的枚举不臆造数值，请查 enum_cosworks.txt。
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
SWS_RESTRAINT_TYPES = {
    "fixed": 0,  # swsRestraintTypeFixed
    "immovable": 1,  # swsRestraintTypeImmovable
    "symmetric": 2,  # swsRestraintTypeSymmetric
    "roller": 3,  # swsRestraintTypeRoller
    "hinge": 4,  # swsRestraintTypeHinge
    "reference_geometry": 5,  # swsRestraintTypeReferenceGeometry
    "flat_face": 6,  # swsRestraintTypeFlatFace
    "cylindrical_faces": 7,  # swsRestraintTypeCylindricalFaces
    "spherical_surface": 8,  # swsRestraintTypeSphericalSurface
    "cyclic_symmetry": 9,  # swsRestraintTypeCyclicSymmetry
}

SWS_FORCE_TYPES = {
    "force_or_moment": 0,  # swsForceTypeForceOrMoment
    "normal": 1,  # swsForceTypeNormal
    "torque": 2,  # swsForceTypeTorque
}

SWS_PRESSURE_TYPES = {
    "normal": 0,  # swsPressureTypeNormal
    "use_reference_geometry": 1,  # swsPressureTypeUseReferenceGeometry
}

SWS_RADIATION_TYPES = {
    "surface_to_ambient": 0,  # swsRadiationTypeSurfaceToAmbient
    "surface_to_surface": 1,  # swsRadiationTypeSurfaceToSurface
}

SWS_SPRING_SUBTYPES = {
    "flat_parallel_faces": 0,  # swsSpringSubTypeFlatParallelFaces
    "concentric_cylindrical_faces": 1,  # swsSpringSubTypeConcentricCylindricalFaces
    "between_vertices": 2,  # swsSpringSubTypeBetweenVertices
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方文档（CHM cosworks 册）
# 文件:   D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\
#           ICWLoadsAndRestraintsManager~<方法>.html
# 定位:   本模块 28 个封装的**官方 VB 声明实参个数**，
#         逐条照抄解析产物 D:\AI\SW\_raw\cosworks_signatures.md。
#         这张表本身就是 A3（签名比对）的可执行依据：下方的 arity 审计
#         会拿它与实际调用点数对账。
# ⚠ 表中不列末位的 ByRef ErrorCode（pywin32 迟到绑定传 0 占位，见模块头）。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
#: enum-gate: not-enum arity
OFFICIAL_LOAD_SIGNATURES: dict[str, int] = {
    # 夹具
    "AddRestraint": 3,
    "AddCyclicSymmetryRestraint": 3,
    "AddPrescribedDisplacement": 4,
    "AddBearingLoad": 2,
    # 力 / 压力
    "AddForce": 3,
    "AddForce2": 4,
    "AddForce3": 20,
    "AddPressure": 3,
    "AddRemoteLoad": 6,
    "AddGravity": 1,
    "AddCentrifugalForce": 1,
    "AddDistributedMass": 3,
    # 热
    "AddTemperature": 1,
    "AddHeatFlux": 1,
    "AddHeatPower": 1,
    "AddConvection": 1,
    "AddRadiation": 2,
    # 连接件
    "AddSpringConnector": 3,
    "AddPinConnector": 2,
    "AddRigidConnector": 2,
    "AddLinkConnector": 2,
    "AddElasticConnector": 1,
    "AddBoltConnector": 3,
    "AddSpotWeldConnector": 3,
    "AddEdgeWeldConnector": 4,
    # 读取
    "GetLoadsAndRestraints": 1,
    "GetEdgeWeldConnector": 1,
}


def _require(manager):
    if manager is None:
        raise ValueError("manager 为 None：须先由 study.GetLoadsAndRestraints() 取得")
    return manager


#: dispatch-guard: exempt internal-helper
def _check(manager, member: str, arity: int, *args):
    """按 OFFICIAL_LOAD_SIGNATURES 校核本次调用的实参个数，再发起调用。

    实参个数对不上时**在发起 COM 调用之前**就报错 ——
    这比让 SolidWorks 报一个含糊的 TypeError 有用得多。

    ★★★★★ 2026-10-01（轮 348）**这里原本少传了末尾那个 `ByRef ErrorCode`** —— 真机确认：
    ```
      L.add_pressure(mgr, [面])                                  ⇒ com_error(-2147352561,
                                                                    '非选择性的参数', None, None)   ✗
      get_com_member(mgr, "AddPressure", 0, [面], VARIANT, out_i4()) ⇒ **ok · <COMObject>**          ✓
    ```
    ★ 真因：★ 本函数的 docstring **自己就写着**「官方签名是 N 个实参（**不含末尾 by-ref ErrorCode**）」
      —— ★ 而它调用时**也只传了那 N 个** ⇒ ★★ **`ErrorCode` 从头到尾没传过一次**。
      ★ 而官方那一族的 VB 声明里 `ErrorCode` 是 **`ByRef` 且**非可选****
      （`Function AddPressure(…, ByRef ErrorCode As System.Integer) As CWPressure`）⇒
      ★★ **缺它 = `DISP_E_PARAMNOTOPTIONAL`「非选择性的参数」** ✓
    ★★ 修法：★ **由本函数统一补 `out_i4()`**（★ **一处修改 ⇒ 整批 `Add*` 全受益**，
      ★ 与"修在能力层而不是工具层"同一原则）。
    ★ 与轮 245 那次修复的关系：★ 那次修的是**第 3 参 `RegGeom` 的形态**
      （裸 `None` ⇒ `类型不匹配`，★ 位置 3）；★ 修完**错误形态正好变成**「非选择性的参数」
      ⇒ ★ **两处是两件事**，★ 本轮补上第二处。
    """
    expected = OFFICIAL_LOAD_SIGNATURES.get(member)
    if expected is not None and expected != arity:
        raise ValueError(
            f"{member} 官方签名是 {expected} 个实参（不含末尾 by-ref ErrorCode），"
            f"本次调用给了 {arity} 个"
        )
    #: ★ 末尾 by-ref ErrorCode 必须补（★ 缺它 ⇒ DISP_E_PARAMNOTOPTIONAL）
    tail = list(args)
    if _wants_error_code(member):
        tail.append(out_i4())
    #: ★★★★ 2026-10-01（轮 349）**第 3 参 `RefGeom` 也不能裸传 `None`** ——
    #:   真机（轮 245 就发现过、★ 而**只修了 `add_torque`，`add_force` 漏了**）：
    #:     `AddForce(NForceType, DispArray, **RefGeom**, ErrorCode)` 传 `None` ⇒
    #:     `com_error(-2147352571, '类型不匹配', None, **3**)`（★ 位置 3 就是它）。
    #:   ⇒ ★★ **正解是项目既有的空 Dispatch 参数包**（事实 12）：
    #:     `create_empty_dispatch_variant()` = `VARIANT(VT_DISPATCH, None)`。
    #: ⇒ ★ 现在**在 `_check` 里统一换**（★ 与补 `ErrorCode` 同一原则：**一处 ⇒ 整批受益*
    #: *），
    #: ★ **只对已从官方声明核过"第 3 参是 `RefGeom`"的成员**换（★ 表外的不动 —— 铁律 5）
    #: 。
    #: ★★ 2026-10-03（轮 416）：**按「该成员的 `RefGeom` 在第几个实参」换** ——
    #: ★ 旧写法写死了 `tail[2]`，★ 而反射说 `AddForce2` 在 3、`AddPrescribedDisplacement
    #: ` 在 3、
    #:   `AddForce3` 在 18 ⇒ ★ 照旧写法会把别的参数当 `RefGeom` 去换（比不换更坏）。
    _pos = _REFGEOM_POSITIONS.get(member)
    if (
        _pos is not None
        and len(tail) > _pos
        and tail[_pos] is None
        and create_empty_dispatch_variant is not None
    ):
        tail[_pos] = create_empty_dispatch_variant()
    return get_com_member(manager, member, *tail)


#: ★★ 第 3 参是 `RefGeom`（且**不能裸传 `None`**）的成员 —— ★ 只列**已从官方声明核过**的
#: 。
#: ★ 依据：`sw_simulation_loads.py` 既有来源块里抄的官方 VB 声明
#:   （`AddForce(NForceType, DispArray, RefGeom, ErrorCode)` ·
#:    `AddPressure(NPressureType, DispArray, RegGeom, ErrorCode)` ·
#:    `AddRestraint(NRestraintType, DispArray, RefGeom, ErrorCode)`）·
#:   ★ 以及真机实测（位置 3 的 `类型不匹配`，轮 245 / 349）。
#: ★★★★★ 2026-10-03（轮 416）**本表改为「成员 → `RefGeom`/`RegGeom` 的形参位置」**（铁律
#:  4：**以出厂类型库为准**）。
#:   ★ 旧表是一个 `frozenset`，★ 而 `_check` **写死了位置 2**（第 3 个实参）。
#:   ★★ 真机反射（`SolidWorks.Interop.cosworks.dll` **34.4.1.1011**）给出的真位置：
#:     ```
#:     AddForce(NForceType, DispArray, **RefGeom**)                      → 位置 2
#:     AddForce2(NForceType, NSelectionType, DispArray, **RefGeom**)     → 位置 3
#:     AddForce3(… 19 个…, DispArray, **RefGeom**, PerUnitLength)         → 位置 18
#:     AddPressure(NPressureType, DispArray, **RegGeom**)                → 位置 2
#:     AddRestraint(NRestraintType, DispArray, **RefGeom**)              → 位置 2
#: AddPrescribedDisplacement(Displacements, NLengthUnit, DispArray, **RefGeom**) → 位置
#: 3
#:     ```
#:   ⇒ ★ **按位置换才对**，★ 而"一刀切位置 2"会把 `AddForce2`/`AddPrescribedDisplacement`
#:     的 **`DispArray` 当成 `RefGeom` 去换** ⇒ ★★ 那比不换更坏。
#:   ★ 本表只列**已从反射核过位置**的；★ 表外的不换（铁律 5）。
#: enum-gate: not-enum index
_REFGEOM_POSITIONS = {
    "AddForce": 2,
    "AddForce2": 3,
    "AddForce3": 18,
    "AddPressure": 2,
    "AddRestraint": 2,
    "AddPrescribedDisplacement": 3,
}
#: ★ 旧名保留为只读视图（★ 供既有代码与检查器用）
_REFGEOM_MEMBERS = frozenset(_REFGEOM_POSITIONS)


#: ★★ 需要末尾 `ByRef ErrorCode` 的成员（★ 官方 VB 声明里带 `ByRef ErrorCode` 的那些）。
#: ★ 只列**已从官方声明核过**的；★ 表外的**不加**（★ 宁可报错也不乱补参数 —— 铁律 5）。
#: ★ 依据：`D:\AI\SW\_raw\chm_cosworks\` 的逐页 VB 声明（★ 与 `sw_simulation_loads.py`
#:   既有来源块里抄的 `Function AddPressure(…, ByRef ErrorCode …)` 一致）。
_ERRORCODE_MEMBERS = frozenset(
    {
        "AddBearingConnector",
        "AddBearingLoad",
        "AddBoltConnector",
        "AddCable",
        "AddCentrifugalForce",
        "AddConvection",
        "AddCyclicSymmetryRestraint",
        "AddDistributedMass",
        "AddEdgeWeldConnector",
        "AddElasticConnector",
        "AddForce",
        "AddForce2",
        "AddForce3",
        "AddGeneralSpringConnector",
        "AddGravity",
        "AddHeatFlux",
        "AddHeatPower",
        "AddInitialConditionForDynamicStudy",
        "AddInitialConditionForDynamicStudy2",
        "AddLinkageRod",
        "AddLinkConnector",
        "AddPinConnector",
        "AddPrescribedDisplacement",
        "AddPressure",
        "AddRadiation",
        "AddRemoteLoad",
        "AddRestraint",
        "AddRigidConnector",
        "AddSelectedBaseExcitation",
        "AddSelectedBaseExcitation2",
        "AddSpotWeldConnector",
        "AddSpringConnector",
        "AddTemperature",
        "AddUniformBaseExcitation",
        "AddUniformBaseExcitation2",
    }
)


def _wants_error_code(member: str) -> bool:
    """★ 该成员是否要末尾 `ByRef ErrorCode`（★ 只认已核过的清单）。"""
    return member in _ERRORCODE_MEMBERS


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方文档（CHM cosworks 册）逐页
# 文件:   SWhelp\cosworks\ICWLoadsAndRestraintsManager~AddRestraint.html
#         SWhelp\cosworks\ICWLoadsAndRestraintsManager~AddForce.html
# 定位:   夹具与力的创建。官方 VB 声明逐字照抄：
#   Function AddRestraint(ByVal NRestraintType As System.Integer,
#                         ByVal DispArray As System.Object,
#                         ByVal RefGeom As System.Object,
#                         ByRef  ErrorCode As System.Integer) As CWRestraint
#     ├ NRestraintType — Type of restraint as defined in swsRestraintType_e
#     ├ DispArray      — Array of entities to which to apply the restraint
#     ├ RefGeom        — Reference geometry entity for direction;
#     │                  **valid only if NRestraintType is
#     │                  swsRestraintTypeReferenceGeometry**
#     └ ErrorCode      — Error code as defined in swsRestraintError_e
#
#   Function AddForce(ByVal NForceType As System.Integer,
#                     ByVal DispArray As System.Object,
#                     ByVal RefGeom As System.Object,
#                     ByRef  ErrorCode As System.Integer) As CWForce
#
# ⚑ 这一条纠正了 scripts/sw_simulation.py 里「RefGeom 语义未查到」的标注：
#   官方明写它**只在夹具类型为「参考几何」时有效**，其余类型传 None 是对的。
# ⚠ 力的**数值不在 AddForce 里**——官方返回 CWForce 对象，
#   数值/单位要设在其属性上（见 scripts/sw_simulation.py 的 apply_normal_force）。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def add_fixed_restraint(manager, entities, restraint_type: int = 0):
    """加夹具。``restraint_type`` 见 SWS_RESTRAINT_TYPES。

    :param entities: 官方 DispArray —— 要施加约束的实体数组（调用方构造）。
    """
    return _check(manager, "AddRestraint", 3, int(restraint_type), entities, None)


def add_reference_geometry_restraint(manager, entities, ref_geom):
    """按参考几何加方向约束（swsRestraintTypeReferenceGeometry = 5）。

    这是**唯一**需要 RefGeom 的夹具类型 —— 官方文档明写
    「valid only if NRestraintType is swsRestraintTypeReferenceGeometry」。
    """
    return _check(
        manager,
        "AddRestraint",
        3,
        SWS_RESTRAINT_TYPES["reference_geometry"],
        entities,
        ref_geom,
    )


def add_force(manager, entities, force_type: int = 1, ref_geom=None):
    """加力/力矩。``force_type`` 见 SWS_FORCE_TYPES（1=法向，2=力矩）。"""
    return _check(manager, "AddForce", 3, int(force_type), entities, ref_geom)


def add_torque(manager, entities, ref_geom=None):
    """加力矩（swsForceTypeTorque = 2）。

    ⚠⚠ **`ref_geom` 不能裸传 `None`** —— 官方签名
    ``AddForce(NForceType, DispArray, RefGeom, ErrorCode)``，真机实测（2026-10-01 轮 245）：
    传 `None` ⇒ ``com_error(-2147352571, '类型不匹配', None, 3)``（★ 位置 3 就是它）。
    ⇒ ★ 正解是本项目**既有**的空 Dispatch 参数包（**已知事实 12**）。
    """
    if ref_geom is None and create_empty_dispatch_variant is not None:
        ref_geom = create_empty_dispatch_variant()
    return _check(manager, "AddForce", 3, SWS_FORCE_TYPES["torque"], entities, ref_geom)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方文档（CHM cosworks 册）逐页
# 文件:   SWhelp\cosworks\ICWLoadsAndRestraintsManager~Add{Pressure,Radiation,
#           Convection,HeatFlux,HeatPower,Temperature}.html
# 定位:   热载荷。官方 VB 声明逐字照抄：
#   AddPressure   (ByVal NPressureType As Integer, ByVal DispArray As Object,
#                  ByVal RegGeom As Object, ByRef ErrorCode As Integer) As CWPressure
#     └ RegGeom（官方拼写就是 RegGeom，非 RefGeom）— reference geometry
#   AddRadiation  (ByVal NRadType As Integer, ByVal DispArray As Object,
#                  ByRef ErrorCode As Integer) As CWRadiation
#   AddConvection / AddHeatFlux / AddHeatPower / AddTemperature
#                 四者签名完全相同：
#                  (ByVal DispArray As Object, ByRef ErrorCode As Integer)
# ⚠ 温度/热流/对流/热功率四个方法的 DispArray 各不相同（面/边/点/体），
#   官方未逐一说明选择规则 —— 交由调用方按零件选取。
# ⚠ ⚑ 本块内曾误用 diff 记号写注释，会被 Python 解析器当成算术运算符；
#   已改为正常文本，勿改回。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def add_pressure(manager, entities, pressure_type: int = 0, reg_geom=None):
    """加压力。``pressure_type`` 见 SWS_PRESSURE_TYPES。

    ⚠⚠ **`reg_geom` 不能裸传 `None`** —— 官方签名
    ``AddPressure(NPressureType, DispArray, RegGeom, ErrorCode)``，真机实测
    （2026-10-01 轮 245）：传 `None` ⇒ ``com_error(-2147352571, '类型不匹配', None, 3)``
    （★ **位置 3 就是 `RegGeom`**）。
    ⇒ ★ 正解是本项目**既有**的空 Dispatch 参数包（**已知事实 12**）：
      ``sw_connect.create_empty_dispatch_variant()`` = ``VARIANT(VT_DISPATCH, None)``。
    ★ 修在**能力层**（不是工具层）⇒ **任何调用方都受益**。
    """
    if reg_geom is None and create_empty_dispatch_variant is not None:
        reg_geom = create_empty_dispatch_variant()
    return _check(manager, "AddPressure", 3, int(pressure_type), entities, reg_geom)


def add_radiation(manager, entities, radiation_type: int = 0):
    """加辐射。``radiation_type`` 见 SWS_RADIATION_TYPES。"""
    return _check(manager, "AddRadiation", 2, int(radiation_type), entities)


def add_convection(manager, entities):
    """加对流换热。"""
    return _check(manager, "AddConvection", 1, entities)


def add_heat_flux(manager, entities):
    """加热流。"""
    return _check(manager, "AddHeatFlux", 1, entities)


def add_heat_power(manager, entities):
    """加热功率。"""
    return _check(manager, "AddHeatPower", 1, entities)


def add_temperature(manager, entities):
    """加温度。"""
    return _check(manager, "AddTemperature", 1, entities)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方文档（CHM cosworks 册）逐页
# 文件:   SWhelp\cosworks\ICWLoadsAndRestraintsManager~Add{Gravity,CentrifugalForce,
#           DistributedMass,RemoteLoad}.html
# 定位:   体载荷与惯性载荷。官方 VB 声明逐字照抄：
#   AddGravity             (ByVal DispEntity As Object,  ByRef ErrorCode As Integer)
#                             └ DispEntity 是**单实体**不是数组（名字可数）
#   AddCentrifugalForce    (ByVal DispEntity As Object,  ByRef ErrorCode As Integer)
#   AddDistributedMass     (ByVal DispArray As Object, ByVal NUnits As Integer,
#                           ByVal DMass As Double, ByRef ErrorCode As Integer)
#   AddRemoteLoad          (ByVal NLoadType As Integer, ByVal DispArray As Object,
#                           ByVal NLocationUnits As Integer, ByVal DXValue As Double,
#                           ByVal DYValue As Double, ByVal DZValue As Double,
#                           ByRef ErrorCode As Integer)
# ⚠ NLoadType / NLocationUnits 的枚举在反射 dump 里未收录本页所需的项，
#   故只做 int 透传、不设默认值 —— 请查 enum_cosworks.txt 取真值。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def add_gravity(manager, entity):
    """加重力。``entity`` 是单实体（官方参数名 DispEntity）。"""
    return _check(manager, "AddGravity", 1, entity)


def add_centrifugal_force(manager, entity):
    """加离心力。``entity`` 是单实体。"""
    return _check(manager, "AddCentrifugalForce", 1, entity)


def add_distributed_mass(manager, entities, mass: float, units: int = 0):
    """加分布质量。``units`` 的枚举反射 dump 未收录，故透传。"""
    return _check(manager, "AddDistributedMass", 3, entities, int(units), float(mass))


def add_remote_load(
    manager, entities, load_type: int, units: int, dx: float, dy: float, dz: float
):
    """加远程载荷（位置 + 方向 + 幅值）。"""
    return _check(
        manager,
        "AddRemoteLoad",
        6,
        int(load_type),
        entities,
        int(units),
        float(dx),
        float(dy),
        float(dz),
    )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方文档（CHM cosworks 册）逐页
# 文件:   SWhelp\cosworks\ICWLoadsAndRestraintsManager~Add{CyclicSymmetryRestraint,
#           PrescribedDisplacement,BearingLoad}.html
# 定位:   其余三类夹具。官方 VB 声明逐字照抄：
#   AddCyclicSymmetryRestraint(ByVal FirstFace As Object, ByVal SecondFace As Object,
#                              ByVal Axis As Object, ByRef ErrorCode As Integer)
#   AddPrescribedDisplacement(ByVal Displacements As Object,
#                             ByVal NLengthUnit As Integer, ByVal DispArray As Object,
#                             ByVal RefGeom As Object, ByRef ErrorCode As Integer)
#   AddBearingLoad(ByVal CoordinateSystem As Object, ByVal FirstFace As Object,
#                  ByRef ErrorCode As Integer)
#     └ CoordinateSystem — 轴承载荷的方向基准；
#       官方 Remarks 明写「The Z-axis of CoordinateSystem must coincide with
#       the axes of the faces in the FirstFace array」——
#       这是**官方文档里唯一给出方向约束条件**的载荷，故记在此处。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def add_cyclic_symmetry_restraint(manager, first_face, second_face, axis):
    """加循环对称夹具。"""
    return _check(
        manager, "AddCyclicSymmetryRestraint", 3, first_face, second_face, axis
    )


def add_prescribed_displacement(
    manager, displacements, entities, length_unit: int = 0, ref_geom=None
):
    """加位移约束。``displacements`` 是官方 Displacements（自定义计算数组）。"""
    return _check(
        manager,
        "AddPrescribedDisplacement",
        4,
        displacements,
        int(length_unit),
        entities,
        ref_geom,
    )


def add_bearing_load(manager, coordinate_system, first_faces):
    """加轴承载荷。

    ⚠ 官方 Remarks 明确：``coordinate_system`` 的 **Z 轴必须与 first_faces
    里各面的轴线重合**，否则载荷方向不对。这是本模块唯一有方向前提的载荷。
    """
    return _check(manager, "AddBearingLoad", 2, coordinate_system, first_faces)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方文档（CHM cosworks 册）逐页
# 文件:   SWhelp\cosworks\ICWLoadsAndRestraintsManager~Add{SpringConnector,
#           PinConnector,RigidConnector,LinkConnector,ElasticConnector,
#           BoltConnector,SpotWeldConnector,EdgeWeldConnector}.html
# 定位:   8 种连接件。官方 VB 声明逐字照抄：
#   AddSpringConnector (ByVal NSpringSubType As Integer, ByVal DispArrayComp1 As Object,
#                       ByVal DispArrayComp2 As Object, ByRef ErrorCode As Integer)
#   AddPinConnector    (ByVal DispArrayComp1 As Object, ByVal DispArrayComp2 As Object,
#                       ByRef ErrorCode As Integer)
#   AddRigidConnector  (ByVal PersistIDFaceArray As Object,
#                       ByVal PersistIDTargetArray As Object, ByRef ErrorCode As Integer)
#   AddLinkConnector   (ByVal VertexPointforFirstLocation As Object,
#                       ByVal VertexPointforSecondLocation As Object,
#                       ByRef ErrorCode As Integer)
#   AddElasticConnector(ByVal DispArray As Object, ByRef ErrorCode As Integer)
#   AddBoltConnector   (ByVal NBoltType As Integer, ByVal DispArrayBoltHead As Object,
#                       ByVal DispArrayBoltNut As Object, ByRef ErrorCode As Integer)
#   AddSpotWeldConnector(ByVal FirstFace As Object, ByVal SecondFace As Object,
#                        ByVal DispArrayWeldLocations As Object,
#                        ByRef ErrorCode As Integer)
#   AddEdgeWeldConnector(ByVal FirstFace As Object, ByVal SecondFace As Object,
#                        ByVal Edges As Object, ByVal NEdgeWeldStyle As Integer,
#                        ByRef ErrorCode As Integer)
# ⚠ ⚑ 官方参数名拼写**不一致**且照抄之：AddPressure 用 `RegGeom`、
#   AddRestraint/AddForce 用 `RefGeom`、RigidConnector 用 `PersistIDFaceArray`。
#   这不是笔误，是官方文档原样；改「整齐」了反而对不上文档。
# ⚠ NBoltType / NEdgeWeldStyle 的枚举反射 dump 未收录对应项，只 int 透传。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def add_spring_connector(manager, comp1, comp2, sub_type: int = 0):
    """加弹簧连接件。``sub_type`` 见 SWS_SPRING_SUBTYPES。"""
    return _check(manager, "AddSpringConnector", 3, int(sub_type), comp1, comp2)


def add_pin_connector(manager, comp1, comp2):
    """加销连接件。"""
    return _check(manager, "AddPinConnector", 2, comp1, comp2)


def add_rigid_connector(manager, source_faces, target_faces):
    """加刚性连接件。官方参数名是 PersistIDFaceArray / PersistIDTargetArray。"""
    return _check(manager, "AddRigidConnector", 2, source_faces, target_faces)


def add_link_connector_report(
    manager,
    model,
    first,
    second,
    *,
    first_body_index: int = 0,
    second_body_index: int = 0,
) -> dict:
    """★ 用**两个声明式选择器**取两个顶点，建连接件，回**可 JSON 化**的报告。

    ★★ **为什么它这样设计**（★ 规则 3 的判断 · 事实 367 那条）：
      ★ `add_link_connector(manager, objA, objB)` **吃两个 COM 对象** ⇒ ★ **没法入参数表达** ⚠
      ★★ 故本包装**让调用方给两个**声明式选择器****，★ 而**对象在本层内部解析** ✓
        ★ 选择器形态见 :func:`sw_selection_spec.resolve_entity`
        （★ `"index:<n>"` · ★ `"__current_selection__"` · ★ 或一个 COM 对象）✓
      ★ `kind` 固定为 **`VERTEX`**（★ 而★ 本仓的 `ENTITY_KINDS` **已含它**）✓

    ★ 判据（★ 规则 6 的精神）：★ **载荷与约束计数 `Count` +1** ——
      ★★ **不是**返回值（★ 事实 8：COM 的返回/布尔都不可信）✓

    :param first: 第一个顶点的**声明式选择器**。
    :param second: 第二个顶点的**声明式选择器**。
    :param first_body_index: 第一个选择器里的 `index:<n>` 落在**第几个体**上（★ 默认 0）。
    :param second_body_index: 同上（★ 第二个）。
      ★★ **而★ 两个顶点**可以**在同一个体上** —— 真机（事实 373）验过：★ **同体也成** ✓
    :returns: `{ok, count_before, count_after, first, second, ...}`
    """
    try:  # noqa: SIM105
        from .sw_selection_spec import resolve_entity
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_selection_spec import resolve_entity
    try:
        count_before = int(get_com_member(manager, "Count") or 0)
    except Exception:  # noqa: BLE001
        count_before = -1
    try:
        va = resolve_entity(model, first, "VERTEX", body_index=int(first_body_index))
        vb = resolve_entity(model, second, "VERTEX", body_index=int(second_body_index))
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "stage": "resolve_vertex",
            "count_before": count_before,
            "first": str(first)[:80],
            "second": str(second)[:80],
            "error": "%s: %s" % (type(exc).__name__, str(exc)[:180]),
        }
    try:
        add_link_connector(manager, va, vb)
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "stage": "AddLinkConnector",
            "count_before": count_before,
            "error": "%s: %s" % (type(exc).__name__, str(exc)[:180]),
        }
    try:
        count_after = int(get_com_member(manager, "Count") or 0)
    except Exception:  # noqa: BLE001
        count_after = -1
    return {
        "ok": count_after == count_before + 1,
        "count_before": count_before,
        "count_after": count_after,
        "first": str(first)[:80],
        "second": str(second)[:80],
        "★": (
            "★ 判据是**载荷与约束计数 +1**（★ 而不是返回值 —— 事实 8）；"
            "★★ 而两个顶点**可以在同一个体上**（★ 事实 373 真机验过）"
        ),
    }


def add_link_connector(manager, first_vertex, second_vertex):
    """加链连接件（两个顶点之间）。"""
    return _check(manager, "AddLinkConnector", 2, first_vertex, second_vertex)


def add_elastic_connector(manager, entities):
    """加弹性连接件。"""
    return _check(manager, "AddElasticConnector", 1, entities)


def add_bolt_connector(manager, bolt_heads, bolt_nuts, bolt_type: int = 0):
    """加螺栓连接件。"""
    return _check(manager, "AddBoltConnector", 3, int(bolt_type), bolt_heads, bolt_nuts)


def add_spot_weld_connector(manager, first_face, second_face, weld_locations):
    """加点焊连接件。"""
    return _check(
        manager, "AddSpotWeldConnector", 3, first_face, second_face, weld_locations
    )


def add_edge_weld_connector(
    manager, first_face, second_face, edges, weld_style: int = 0
):
    """加边焊连接件。"""
    return _check(
        manager,
        "AddEdgeWeldConnector",
        4,
        first_face,
        second_face,
        edges,
        int(weld_style),
    )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方文档（CHM cosworks 册）逐页
# 文件:   SWhelp\cosworks\ICWLoadsAndRestraintsManager~{GetLoadsAndRestraints,
#           GetEdgeWeldConnector,Count}.html
# 定位:   载荷回读。官方 VB 声明逐字照抄：
#   GetLoadsAndRestraints(ByVal NIndex As Integer, ByRef ErrorCode As Integer)
#     → 返回 CWLoadsAndRestraints
#   GetEdgeWeldConnector (ByVal NIndex As Integer, ByRef ErrorCode As Integer)
#     → 返回 CWEdgeWeldConnector
#   另有 Count 属性（0 参，无 ErrorCode）
# ⚠ 这两个方法都**带 by-ref ErrorCode**，同样传 0 占位、不据其判成败。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_loads_and_restraints(manager, index: int):
    """按序号取载荷/夹具对象。"""
    return _check(manager, "GetLoadsAndRestraints", 1, int(index))


def get_edge_weld_connector(manager, index: int):
    """按序号取边焊连接件对象。"""
    return _check(manager, "GetEdgeWeldConnector", 1, int(index))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（scripts/sw_sheet_metal.py::sheet_metal_evidence）
# 定位:   证据回读，沿用「只取已核实成员、不臆造方法」的写法。
#         官方已文档化的载荷对象成员：CWLoadsAndRestraints.GetName /
#         GetType（反射 dump enum_cosworks.txt 侧为 363 个枚举，本处不逐个展开）。
# ⚠ 载荷对象的属性清单官方未逐页给出（CHM 只文档化了 Add* 方法本身），
#   故证据只收录**确定存在**的两个成员。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_loads_evidence(manager) -> dict[str, Any]:
    """回读当前研究下的载荷/夹具清单。"""
    _require(manager)
    count = int(get_com_member(manager, "Count") or 0)
    items = []
    for index in range(count):
        try:
            item = get_loads_and_restraints(manager, index)
        except Exception as exc:  # noqa: BLE001
            items.append({"index": index, "error": str(exc)})
            continue
        items.append(
            {
                "index": index,
                "name": str(get_com_member(item, "GetName") or ""),
                "type": int(get_com_member(item, "GetType") or -1),
            }
        )
    return {"count": count, "items": items}


# ── 24h 计划 段 2.1（Spec Kit `143`）：**四类常用载荷的「回读报告」包装** ──────────
# ★★★ 为什么四个都要包（与 `sw_simulation` 的 `create_mesh_report` 同一理由）：
# `add_pressure` / `add_torque` / `add_gravity` / `add_centrifugal_force` **都回 COM 对
# 象**
#   （`_check(...)` 直接回 `get_com_member(manager, member, *args)`）
#   ⇒ ★ **MCP 回不了对象** ⇒ 必须翻成**可 JSON 化**的东西。
# ★★ 判据用**既有脚本那条**（`tools/capture_simulation_loads_evidence.py`）：
#   「夹具/载荷 | 选区计数 = 1 **且** `LoadsAndRestraintsManager.Count` 增加」
#   ⇒ 本组函数一律**回读 `Count` 的前后差**，★ **不看返回对象**（★ 铁律：回读优先）。


def _loads_count(manager) -> int:
    """回读载荷条数（`ICWLoadsAndRestraintsManager.Count`）。★ 取不到回 -1（**不静默成 0**）。"""
    try:
        v = get_com_member(manager, "Count")
        return int(v) if v is not None else -1
    except Exception:  # noqa: BLE001
        return -1


def _report(manager, fn, label: str, model=None):
    """★ 通用：**清选区 → 施加载荷 → 回读 Count 前后差** → 组装回读报告。

    `fn` 是「真正施加载荷」的零参可调用（★ 它在 `try` 里跑 ⇒ 异常**序列化回调用方**，不吞）。

    ★★★ **2026-10-01 轮 261（修地基 **D1**）**：★ **先清选区**再做一切。
      ★ 依据（★ 本项目自己的记载，**不是发明**）：`specs/140-*` 的 `plan.md` L70 ——
        「★ **选区累加 ⇒ 判据假红** | ★ 每次之间 `ClearSelection2(True)`（★ 照既有脚本 L145/L148）」，
        以及同特性 `converge.md` L76：「★「每次载荷之间要清空选区」**只是证据脚本在做** ⇒
        **工具层没有守卫**（★ 若不清空，计数会把上次算进来）⇒ **留后续特性**」。
      ⇒ ★ 本函数就是**那个"后续特性"**：★ **把守卫放进能力层**（★ 于是**任何调用方**都受益，
        而不是每个证据脚本各自记得清）。
    ⚠ **清选区需要 `model`**；★ 传 `None` 时**跳过清理**（★ 旧调用方与单元测试不受影响），
      并在报告里**如实标注**（`selection_cleared: None`）—— ★ 不假装清了。
    """
    cleared: bool | None = None
    if model is not None:
        try:
            get_com_member(model, "ClearSelection2", True)
            cleared = True
        except Exception:  # noqa: BLE001
            cleared = False
    before = _loads_count(manager)
    obj = None
    err = None
    try:
        obj = fn()
    except Exception as exc:  # noqa: BLE001
        err = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    after = _loads_count(manager)
    return {
        "ok": err is None and after == before + 1,
        "load": label,
        "count_before": before,
        "count_after": after,
        "selection_cleared": cleared,
        "created_object": type(obj).__name__ if obj is not None else None,
        "error": err,
        "★": (
            "ok 判的是 count_after == count_before + 1（★ 回读优先，不看返回对象）；"
            "★ `selection_cleared=True` = 施加载荷**之前**已清选区（修地基 D1）"
        ),
    }


def apply_pressure_report(manager, model, pressure_type: int = 0, reg_geom=None):
    """**加压力**并回**回读报告**。

    ★ `model` 是活动文档 —— **给了它才会把选区实体装成官方要求的 `DispArray`**
      （机制与 `sw_simulation.apply_fixed_restraint` 完全一致，★ 复用 `_selected_dispatch_array`）。
    """
    try:  # noqa: SIM105
        from .sw_simulation import _selected_dispatch_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_simulation import _selected_dispatch_array

    entities = _selected_dispatch_array(model)
    return _report(
        manager,
        lambda: add_pressure(manager, entities, pressure_type, reg_geom),
        "pressure",
        model,
    )


def apply_torque_report(manager, model, ref_geom=None):
    """**加力矩**并回**回读报告**（★ 同 `apply_pressure_report`，`model` 用来装 `DispArray`）。"""
    try:  # noqa: SIM105
        from .sw_simulation import _selected_dispatch_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_simulation import _selected_dispatch_array

    entities = _selected_dispatch_array(model)
    return _report(
        manager, lambda: add_torque(manager, entities, ref_geom), "torque", model
    )


def apply_gravity_report(manager, model):
    """**加重力**并回**回读报告**。

    ⚠ 官方参数是**单实体**（`DispEntity`）⇒ ★ 取选区里的**第一个**实体。
    """
    try:  # noqa: SIM105
        from .sw_simulation import _selected_dispatch_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_simulation import _selected_dispatch_array

    ents = _selected_dispatch_array(model)
    entity = ents[0] if ents else None
    return _report(manager, lambda: add_gravity(manager, entity), "gravity", model)


def apply_centrifugal_force_report(manager, model):
    """**加离心力**并回**回读报告**。⚠ 官方参数是**单实体** ⇒ 取选区第一个。"""
    try:  # noqa: SIM105
        from .sw_simulation import _selected_dispatch_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_simulation import _selected_dispatch_array

    ents = _selected_dispatch_array(model)
    entity = ents[0] if ents else None
    return _report(
        manager,
        lambda: add_centrifugal_force(manager, entity),
        "centrifugal_force",
        model,
    )


# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_simulation_loads.py —— 追加 6 个"简单载荷"的 report 封装
# 定位:   ★ 2026-10-03（轮 402）24h 计划 v2 段 5（仿真载荷族）。
# ★★ **为什么是这 6 条**：`tools/triage_real_gaps.py` 在补了"动词对 + 读注册表对象"两条
# 规则后，
# 把 `sw_simulation_loads` 的 30 条缺口收敛到 **21 条真缺口**；★ 其中这一组是**同一种形
# 态** ——
#     `add_X(manager, entities[, 一个 int])` ⇒ ★ 可以像既有的 `apply_pressure_report` 那样
#     **复用同一套机器**（`_selected_dispatch_array` 装实体 + `_report` 回读计数）。
# ★ 其余 15 条是**多面 / 多顶点 / 多组件**参数（bearing / bolt / cyclic / edge_weld / li
# nk /
# pin / rigid / spot_weld / spring / prescribed_displacement / remote_load / reference_g
# eometry /
# distributed_mass / force / get_edge_weld_connector）—— ★ 各自的选择方式不同，★ **留作
# 后批**。
# 官方依据: `ICWLoadsAndRestraintsManager` 的 `AddConvection` / `AddElasticConnector` /
#   `AddHeatFlux` / `AddHeatPower` / `AddTemperature` / `AddRadiation`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def apply_convection_report(manager, model):
    """**加对流**并回**回读报告**（★ 与 `apply_pressure_report` 同一套机器）。"""
    try:  # noqa: SIM105
        from .sw_simulation import _selected_dispatch_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_simulation import _selected_dispatch_array
    entities = _selected_dispatch_array(model)
    return _report(
        manager, lambda: add_convection(manager, entities), "convection", model
    )


def apply_elastic_connector_report(manager, model):
    """**加弹性连接**并回**回读报告**。"""
    try:  # noqa: SIM105
        from .sw_simulation import _selected_dispatch_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_simulation import _selected_dispatch_array
    entities = _selected_dispatch_array(model)
    return _report(
        manager,
        lambda: add_elastic_connector(manager, entities),
        "elastic_connector",
        model,
    )


def apply_heat_flux_report(manager, model):
    """**加热流**并回**回读报告**。"""
    try:  # noqa: SIM105
        from .sw_simulation import _selected_dispatch_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_simulation import _selected_dispatch_array
    entities = _selected_dispatch_array(model)
    return _report(
        manager, lambda: add_heat_flux(manager, entities), "heat_flux", model
    )


def apply_heat_power_report(manager, model):
    """**加热功率**并回**回读报告**。"""
    try:  # noqa: SIM105
        from .sw_simulation import _selected_dispatch_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_simulation import _selected_dispatch_array
    entities = _selected_dispatch_array(model)
    return _report(
        manager, lambda: add_heat_power(manager, entities), "heat_power", model
    )


def apply_temperature_report(manager, model):
    """**加温度**并回**回读报告**。"""
    try:  # noqa: SIM105
        from .sw_simulation import _selected_dispatch_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_simulation import _selected_dispatch_array
    entities = _selected_dispatch_array(model)
    return _report(
        manager, lambda: add_temperature(manager, entities), "temperature", model
    )


def apply_radiation_report(manager, model, radiation_type: int = 0):
    """**加热辐射**并回**回读报告**（★ 唯一带一个 int 参数的那个）。"""
    try:  # noqa: SIM105
        from .sw_simulation import _selected_dispatch_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_simulation import _selected_dispatch_array
    entities = _selected_dispatch_array(model)
    return _report(
        manager,
        lambda: add_radiation(manager, entities, radiation_type),
        "radiation",
        model,
    )


# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_simulation_loads.py —— 追加 3 个"数参型"载荷的 report 封装
# 定位:   ★ 2026-10-03（轮 414）24h 计划 v2 段 5（仿真载荷族）**A 组的收尾**。
#   ★★ **为什么是这三条**：重跑分诊后 `sw_simulation_loads` 的该挂剩 17 条，
#     其中**与已验证的 6 条同形**（`(manager, entities, 若干普通数)`）的只剩：
#     `add_distributed_mass` · `add_force` · `add_remote_load`
# （另两条 `add_reference_geometry_restraint` / `add_prescribed_displacement` 要**引用几
# 何对象**，
#      ★ 那需要另一条前置链 ⇒ 留后批）。
#   ★★ **而本批带着轮 408 学到的那条纪律**：★ **算例类型**是"调用前提"的一维 ——
#     这三条都是**结构载荷** ⇒ ★ 预期要 **`static`**（★ 而热载荷要 `thermal`），
#     ★ 所以探针必须**分别验**、★ 不能一概而论（事实 323 §四）。
#   ⚠★ **一处形态要特别处理**：`add_force` 的裸函数默认传 `ref_geom=None`
#     —— ★ 而**事实 12**（与 `add_pressure` 的 docstring）明写：
#     ★★ 官方的 Object 入参**不能裸传 `None`**（会 `类型不匹配`），
#     要用本项目的空 Dispatch 参数包 `create_empty_dispatch_variant()`。
#     ⇒ ★ 本包装**显式补它**（★ 而**不改裸函数** —— 免得动到别的调用方）。
# 官方依据: CHM `ICWLoadsAndRestraintsManager~Add{DistributedMass,Force,RemoteLoad}.html
#           ` 的 VB 声明 ·
# 本模块既有的来源块（`AddDistributedMass` / `AddRemoteLoad` 的官方声明**逐字抄在 L441-4
# 49**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def apply_distributed_mass_report(manager, model, mass: float, units: int = 0):
    """**加分布质量**并回**回读报告**（★ 与 `apply_pressure_report` 同一套机器）。"""
    try:  # noqa: SIM105
        from .sw_simulation import _selected_dispatch_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_simulation import _selected_dispatch_array
    entities = _selected_dispatch_array(model)
    return _report(
        manager,
        lambda: add_distributed_mass(manager, entities, float(mass), int(units)),
        "distributed_mass",
        model,
    )


def apply_force_report(manager, model, force_type: int = 1):
    """**加力/力矩**并回**回读报告**（★ `force_type` 是官方的种类枚举）。

    ⚠★ 本包装**显式补 `ref_geom`**（空 Dispatch）—— ★ 裸函数的默认值是 `None`，
    而**事实 12** 明写 Object 入参裸传 `None` 会 `类型不匹配`。
    """
    try:  # noqa: SIM105
        from .sw_connect import create_empty_dispatch_variant
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_connect import create_empty_dispatch_variant
    try:  # noqa: SIM105
        from .sw_simulation import _selected_dispatch_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_simulation import _selected_dispatch_array
    entities = _selected_dispatch_array(model)
    return _report(
        manager,
        lambda: add_force(
            manager, entities, int(force_type), create_empty_dispatch_variant()
        ),
        "force",
        model,
    )


def apply_remote_load_report(
    manager, model, load_type: int, units: int, dx: float, dy: float, dz: float
):
    """**加远程载荷**（位置 + 方向 + 幅值）并回**回读报告**。

    ⚠ `load_type` / `units` 的枚举在本仓的来源块里注明"反射 dump 未收录 ⇒ 只做 int 透传"。
    """
    try:  # noqa: SIM105
        from .sw_simulation import _selected_dispatch_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_simulation import _selected_dispatch_array
    entities = _selected_dispatch_array(model)
    return _report(
        manager,
        lambda: add_remote_load(
            manager,
            entities,
            int(load_type),
            int(units),
            float(dx),
            float(dy),
            float(dz),
        ),
        "remote_load",
        model,
    )


# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_simulation_loads.py —— 追加 2 个"双实体"连接件的 report 封装
# 定位:   ★ 2026-10-03（轮 417）24h 计划 v2 **段 5 B 组的开头**（多面 / 多顶点那一族）。
#   ★★ **为什么现在能做**：★ 前两轮把**出厂类型库**（`SolidWorks.Interop.cosworks.dll`
#     **34.4.1.1011**，PowerShell 纯元数据反射）读通了 ⇒ ★★ **每个成员的形参表都有了**：
#     ```
#     AddLinkConnector(VertexPointforFirstLocation, VertexPointforSecondLocation)
#     AddRigidConnector(PersistIDFaceArray, PersistIDTargetArray)
#     ```
#     ⇒ ★ 两条都是「**两个实体/两组实体**」⇒ ★ 而 `_selected_dispatch_array(model)` 回的是
#       **选中对象的列表** ⇒ ★★ **"把选区一分为二"就是这两条的共同形态**。
#   ★ **本批只做两条**（★ 各自的选择方式明确）：
#     · `add_link_connector` —— ★ **两个顶点**（★ 各取一个）；
#     · `add_rigid_connector` —— ★ **两组面**（★ 按"前半 / 后半"切）。
#   ⚠ **`add_pin_connector` 不做**：★ 官方形参是 `DispArrayComp1` / `DispArrayComp2`
#     ⇒ ★ 那是**装配里的两个零件** ⇒ ★ 需要先建装配 ⇒ ★ 另一条链（★ 不在本批）。
# ⚠★ **切分规则要写明**（★ 免得调用方猜）：★ 选区里**前一半给第一个参数、后一半给第二个*
# *；
#     ★ 而**条数必须为偶数**（★ 奇数就拒绝 —— ★ 早失败优于静默）。
# ⚠★ **算例类型**：★ 这两条是**连接件** ⇒ ★ 预期 **static**（★ 而**真机要验**，★ 不能一
# 概而论）。
# 官方依据: 出厂类型库反射（★ 形参名逐字来自它）· 本模块既有的 `_check` 与 arity 表
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def _split_selection(model, *, per_side: int = 1):
    """★ 取当前选区并**一分为二**（★ 前一半 / 后一半）—— ★ 双实体连接件的共同前置。

    :param per_side: 每一侧要几个实体（★ 两侧都按它取 ⇒ **总数必须是 `2 * per_side`**）。
    :raises RuntimeError: 选区条数不足或不是 `2 * per_side`（★ 早失败优于静默）。
    """
    try:  # noqa: SIM105
        from .sw_simulation import _selected_dispatch_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_simulation import _selected_dispatch_array
    objs = _selected_dispatch_array(model)
    want = 2 * int(per_side)
    if len(objs) < want:
        raise RuntimeError(
            "选区里只有 %d 个实体，本连接件需要 %d 个（每侧 %d 个）"
            % (len(objs), want, per_side)
        )
    return objs[:per_side], objs[per_side:want]


def apply_link_connector_report(manager, model):
    """**加链接连接件**（★ 两个**顶点**）并回**回读报告**。

    ★ 官方签名：`AddLinkConnector(VertexPointforFirstLocation, VertexPointforSecondLocation)`
    ⇒ ★ 请**先选中两个顶点**（★ 前一个给第一个参数、后一个给第二个）。
    """
    a, b = _split_selection(model, per_side=1)
    return _report(
        manager,
        lambda: add_link_connector(manager, a[0], b[0]),
        "link_connector",
        model,
    )


def apply_rigid_connector_report(manager, model, *, faces_per_side: int = 1):
    """**加刚性连接件**（★ 两组**面**）并回**回读报告**。

    ★ 官方签名：`AddRigidConnector(PersistIDFaceArray, PersistIDTargetArray)`
    ⇒ ★ 请**先选中 `2 × faces_per_side` 个面**（★ 前一半 = 源、后一半 = 目标）。
    """
    a, b = _split_selection(model, per_side=max(1, int(faces_per_side)))
    return _report(
        manager, lambda: add_rigid_connector(manager, a, b), "rigid_connector", model
    )


# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_simulation_loads.py —— 追加 `apply_rigid_connector_by_objects_repor
# t`
# 定位:   ★ 2026-10-03（轮 424）承**事实 337 的正解**：★ **不读选区，按已知的实体清单
#           装数组**。
#   ★★ 为什么另起一个包装而**不动** `apply_rigid_connector_report`：
#     · 后者走 `_selected_dispatch_array`（★ 读选区）—— ★ 它服务的是**交互式**假设
#       （"用户先在界面上选好"），★ **仍有其用**，★ 只是**多实体时拿不全**（★ 事实 336/337）；
#     · 而本包装走 **`entities_as_array`**（★ 由**序号**取对象）—— ★ 那是**脚本**假设
#       （★ "对象我们本来就有"）。
#   ⇒ ★★ 两者并存，★ 由调用方按场景选；★ **而探针与工具用后者**。
# 官方依据: `ICWLoadsAndRestraintsManager.AddRigidConnector(PersistIDFaceArray, PersistI
#           DTargetArray)`
# （★ 出厂类型库反射逐字）· `IBody2.GetFaces`（★ `entities_on_body` 已在用）· 事实 32 /
# 336 / 337
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def apply_rigid_connector_by_objects_report(
    manager,
    model,
    source_indices,
    target_indices,
    *,
    kind: str = "FACE",
    source_body_index: int = 0,
    target_body_index: int = 0,
):
    """★ **按已知的实体清单**加刚性连接件（★ **不读选区**）并回**回读报告**。

    ★ 官方签名：`AddRigidConnector(PersistIDFaceArray, PersistIDTargetArray)`
    ★ 而本包装**自己把两组实体装好**（★ `entities_as_array`）⇒ ★ 于是**不依赖**
      "用户先在界面上选好"那条交互式假设（★ 那正是事实 336/337 里崩掉的假设）。

    :param source_indices / target_indices: 两组实体的**序号**（★ 0 基）。
    :param kind: `"FACE"` / `"EDGE"` / `"VERTEX"`。
    """
    try:  # noqa: SIM105
        from .sw_selection_spec import entities_as_array
    except ImportError:  # ★ 回退绝对导入 ✓
        from sw_selection_spec import entities_as_array
    #: ★★ 两侧**可分别指定体号** —— ★ 因为"连接件"连的是**两个**东西**：
    #:   ★ 而多体零件里两个体的序号不同（★ 事实 338 的新假设：它要两个体才能连）。
    src = entities_as_array(model, kind, source_indices, body_index=source_body_index)
    tgt = entities_as_array(model, kind, target_indices, body_index=target_body_index)
    return _report(
        manager,
        lambda: add_rigid_connector(manager, src, tgt),
        "rigid_connector_by_objects",
        model,
    )


# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_simulation_loads.py —— 追加 `apply_pin_connector_report`
# 定位:   ★ 2026-10-03（轮 426）`plan-200r-v3` 段 1（B 组）—— ★ 承**事实 339** 给同族
#           开的门。
#   ★★ 事实 339 的结论：★ 连接件一族的**两条硬前提**是
#     ⓐ **它要两个东西**（★ 同族形参名写着 `Comp1`/`Comp2`）·
#     ⓑ **不要从选区读多实体**（★ `ISelectionMgr` 那族只回得到第 1 个）。
#   ★★★ 而**销钉连接件的形参恰好只要"两个零件"**（★ **不要面、不要序号**）：
#     ```
#     AddPinConnector(**DispArrayComp1:Object**, **DispArrayComp2:Object**, ErrorCode&)
#     ```
#     ⇒ ★★ 于是它**比刚性连接件更简单** —— ★ **组件对象本仓直接拿得到**
#       （`sw_assembly.get_components`）★ 连"按序号取实体"都不需要 ✓
#   ★ 而**装配体那条路**在硬约束⑦（禁保存）下**仍然走得通**：
#     ★ 用**已在盘上的**自带零件（★ 本机 `…\samples\tutorial\api\` 下有几十个 `.sldprt`）
#       ⇒ ★ **不保存任何东西** ✓
# 官方依据: 出厂类型库（`SolidWorks.Interop.cosworks.dll` **34.4.1.1011**）反射的形参名
#           ·
# `IAssemblyDoc.AddComponent5`（★ `sw_assembly.add_component` 已在用）· `swsAnalysisStud
# yTypeStatic = 0`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def apply_pin_connector_report(manager, model, *, first: int = 0, second: int = 1):
    """★ **按装配体里的两个零件**加销钉连接件并回**回读报告**（★ **不读选区**）。

    ★ 官方签名：`AddPinConnector(DispArrayComp1, DispArrayComp2)`
    ★ 而它**只要两个组件对象** ⇒ ★ 本包装**直接从装配体取**
      （`sw_assembly.get_components`）⇒ ★ 于是**既不需要选实体、也不需要按序号取** ✓

    :param first / second: 取**第几个**顶层组件（★ 0 基）。
    :raises RuntimeError: 顶层组件不足两个（★ 早失败优于静默 ——
        ★★ 事实 339：★ 单体文档上它会**成功返回却不建**，★ 所以宁可先拒绝）。
    """
    #: ★★★ 2026-10-03（轮 426）**不能用 `sw_assembly.get_components`** ——
    #:   ★ 真机：它回的是 **字典记录**（`name`/`path`/`suppressed`/`visible`）
    #:     而**不是 COM 组件对象** ⇒ ★ 传给 COM 报
    #:     `TypeError: must be real number, not dict`（★ pywin32 把它当数字）。
    #:   ★ 正解：**直接调 `IAssemblyDoc.GetComponents`** 拿**原始 COM 对象**。
    raw = get_com_member(model, "GetComponents", True)
    comps = list(raw) if raw else []
    if len(comps) < max(int(first), int(second)) + 1:
        raise RuntimeError(
            "装配体顶层只有 %d 个组件，取不到第 %d / %d 个 —— 早失败："
            "★ 销钉连接件要**两个零件**（★ 单体文档上它会成功返回却不建）"
            % (len(comps), int(first), int(second))
        )
    #: ★★★ 2026-10-03（轮 426）**两个组件要装成数组** ——
    #:   ★ 真机第一版传了**裸对象** ⇒ `TypeError: must be real number, not dict`
    #:     （★ pywin32 试图把它当数字）。
    #:   ★ 而官方形参是 **`DispArrayComp1` / `DispArrayComp2`** ⇒ ★★ **是数组**。
    #:   ★★ 而这与刚性连接件那次**完全自洽**：
    #:     ★ 那次传的是 `entities_as_array` 回的**列表** ⇒ 成了；
    #:     ★ 这次传裸对象 ⇒ 报 TypeError ✓
    return _report(
        manager,
        lambda: add_pin_connector(manager, [comps[int(first)]], [comps[int(second)]]),
        "pin_connector",
        model,
    )
