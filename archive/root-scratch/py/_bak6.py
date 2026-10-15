"""SolidWorks Simulation（cosworks）原生接口封装。

能力域
    域 13 · 仿真（需 Simulation 许可证与加载项）

对应官方接口族（全部经 interop DLL 元数据反射核对）
    ICwAddincallback    → 加载项回调，提供 ``CosmosWorks`` 入口
    ICosmosWorks        → ``ActiveDoc`` / ``VersionNumber``（均为属性）
    ICWModelDoc         → ``StudyManager``（属性）
    ICWStudyManager     → ``StudyCount`` / ``ActiveStudy``（属性）、``GetStudy``、
                          ``CreateNewStudy3``
    ICWStudy            → ``Mesh`` / ``Results``（属性）、``CreateMesh``、``RunAnalysis``
    ICWLoadsAndRestraintsManager → ``AddRestraint`` / ``AddForce`` / ``AddForce2``
    ICWLoadsAndRestraints        → ``Name`` / ``EntityCount`` / ``Type`` / ``State``
    ICWRestraint / ICWForce      → 创建后的属性回填

覆盖边界（重要）
    本模块**只实现反射清单里有签名的部分**。``ICWLoadsAndRestraintsManager``
    共 34 个 Add* 方法，其中仅 7 个有可用签名来源（见
    ``docs/capability-matrix.md`` §二）：AddForce / AddForce2 / AddForce3 /
    AddRestraint / AddInitialConditionForDynamicStudy(2) / CopyLoadsAndRestraintsToStudy。
    其余 27 个（压力、辐射、连接件、温度、弹簧、重力、轴承载荷等）
    在 CHM ``cosworks`` 册中为 JS 空壳、``C:\\swapi`` 未收录 cosworks，
    **签名查不到**，故本模块一律不提供入口，也不用相似名字蒙混
    （见 AGENTS.md 铁律 5）。

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
   它不会启动 SolidWorks、不会自行加载加载项；所有 COM 入口都需要调用方
   显式传入已连接的应用对象。
"""
from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（AGENTS.md 铁律 1 认可的第三类来源）
# 文件:   scripts/sw_simulation.py 模块头；写法参照 scripts/sw_sheet_metal.py
#         的「try: from .x import / except ImportError: from x import」依赖解析
#         模式（同 AGENTS.md §三 对新增模块的硬性要求）。
# 定位:   __all__ 导出清单 + 加载项 ProgID 常量。
# ⚠ ProgID 取值来源: alisamsam/Solidworks-MCP (MIT) solidworks_simulation.py:207
#   使用 ``GetAddInObject("SldWorks.Simulation")``。该字符串**不在**
#   cosworks.dll 内（属 SolidWorks 主程序集侧），C:\swapi 也未收录 cosworks，
#   **官方常量定义未查到**——按 AGENTS.md 铁律 5，此处显式标注为待二次确认，
#   并在下方常量的 docstring 中同样注明。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "SWS_RESTRAINT_TYPES",
    "SWS_FORCE_TYPES",
    "SWS_FORCE_UNITS",
    "SWS_MESH_TYPES",
    "SWS_ANALYSIS_STUDY_TYPES",
    "SIMULATION_ADDIN_PROGID",
    "get_cosmosworks",
    "get_cw_document",
    "get_study_manager",
    "create_static_study",
    "iter_studies",
    "get_study_by_name",
    "apply_fixed_restraint",
    "apply_normal_force",
    "run_analysis",
    "create_mesh",
    "collect_study_evidence",
]

#: 加载项的 ProgID，供 ``ISldWorks.GetAddInObject`` 使用。
#: 该字符串不在 cosworks.dll 内（属 SolidWorks 主程序集侧），未查到官方常量定义，
#: 沿用 alisamsam/Solidworks-MCP (MIT) 的取值并在此显式标注为**待二次确认**。
SIMULATION_ADDIN_PROGID = "SldWorks.Simulation"


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举定义（SolidWorks.Interop.cosworks.dll）
# 文件:   D:\AI\SW\_raw\reflect\enum_cosworks.txt
#         （由 D:\AI\SW\tools\reflect-interop.ps1 对官方程序集做纯元数据反射生成）
# 定位:   下列 5 组枚举的取值域，逐项照录，未增删、未改写。
# 查证:   反射脚本只枚举托管程序集元数据，不实例化任何 COM 对象。
# ⚠ 本表为静态反射结果，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
SWS_RESTRAINT_TYPES = {
    "fixed": 0,                # swsRestraintTypeFixed
    "immovable": 1,            # swsRestraintTypeImmovable
    "symmetric": 2,            # swsRestraintTypeSymmetric
    "roller": 3,               # swsRestraintTypeRoller
    "hinge": 4,                # swsRestraintTypeHinge
    "reference_geometry": 5,   # swsRestraintTypeReferenceGeometry
    "flat_face": 6,            # swsRestraintTypeFlatFace
    "cylindrical_faces": 7,    # swsRestraintTypeCylindricalFaces
    "spherical_surface": 8,    # swsRestraintTypeSphericalSurface
    "cyclic_symmetry": 9,      # swsRestraintTypeCyclicSymmetry
}

SWS_FORCE_TYPES = {
    "force_or_moment": 0,      # swsForceTypeForceOrMoment
    "normal": 1,               # swsForceTypeNormal
    "torque": 2,               # swsForceTypeTorque
}

SWS_FORCE_UNITS = {
    "n_or_nm": 0,              # swsForceUnitNOrNm
    "lb_or_lbin": 1,           # swsForceUnitlbOrlbin
    "kgf_or_kgfcm": 2,         # swsForceUnitkgfOrkgfcm
}

SWS_MESH_TYPES = {
    "solid": 0,                # swsMeshTypeSolid
    "mid_surface": 1,          # swsMeshTypeMidSurface
    "surfaces": 2,             # swsMeshTypeSurfaces
    "mixed": 3,                # swsMeshTypeMixed
    "beam": 4,                 # swsMeshTypeBeam
}

SWS_ANALYSIS_STUDY_TYPES = {
    "static": 0,               # swsAnalysisStudyTypeStatic
    "frequency": 1,            # swsAnalysisStudyTypeFrequency
    "buckling": 2,             # swsAnalysisStudyTypeBuckling
    "thermal": 3,              # swsAnalysisStudyTypeThermal
    "optimization": 4,         # swsAnalysisStudyTypeOptimization
    "nonlinear": 5,            # swsAnalysisStudyTypeNonlinear
    "drop_test": 6,            # swsAnalysisStudyTypeDropTest
    "fatigue": 7,              # swsAnalysisStudyTypeFatigue
    "dynamic": 8,              # swsAnalysisStudyTypeDynamic
    "pressure_vessel": 9,      # swsAnalysisStudyTypePressureVessel
    "topology_static": 13,     # swsAnalysisStudyTypeTopology_Static
    # 10/11/12 为 swsAnalysisStudyTypeReserved1..3，官方标为保留值，此处不收录。
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   Simulation 入口链的逐跳签名：
#           ICwAddincallback : CosmosWorks get_CosmosWorks()   ← 属性
#           ICosmosWorks     : CWModelDoc get_ActiveDoc()      ← 属性
#                             : String     get_VersionNumber() ← 属性
#           ICWModelDoc      : CWStudyManager get_StudyManager() ← 属性
# 查证:   对上述 4 个接口逐个 GetMembers() 后人工筛出上列 5 个成员。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
#
# ⚠ 与外部实现的差异（重要，见 docs/signature-audit.md 批次 1）：
#   alisamsam/Solidworks-MCP (MIT) 写的是 ``addin.COSMOSWORKS``（全大写）。
#   本反射清单里该成员的 getter 名为 ``get_CosmosWorks``，即 COM 属性名是
#   ``CosmosWorks``（仅首字母大写）。全大写写法在 pywin32 迟到绑定下能否命中
#   **未查证**，故此处按官方拼写取 ``CosmosWorks``，并在失败时给出明确报错，
#   不做「两种拼写都试一遍」的糊弄式兜底。
# ────────────────────────────────────────────────────────────────────
def get_cosmosworks(sw_app):
    """取 ICosmosWorks 入口。加载项未就绪时抛 RuntimeError。"""
    addin = get_com_member(sw_app, "GetAddInObject", SIMULATION_ADDIN_PROGID)
    if addin is None:
        raise RuntimeError(
            "GetAddInObject('SldWorks.Simulation') 返回 None："
            "Simulation 加载项未加载或本机未安装（需 Simulation 许可证）"
        )
    cosmos = get_com_member(addin, "CosmosWorks")
    if cosmos is None:
        raise RuntimeError(
            "加载项对象上没有 CosmosWorks 成员（官方 getter 为 get_CosmosWorks，"
            "挂在 ICwAddincallback 上）"
        )
    return cosmos


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   ICosmosWorks.get_ActiveDoc() → CWModelDoc
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_cw_document(sw_app):
    """取当前活动的 CWModelDoc；无活动文档时抛 RuntimeError。"""
    cosmos = get_cosmosworks(sw_app)
    document = get_com_member(cosmos, "ActiveDoc")
    if document is None:
        raise RuntimeError(
            "CosmosWorks.ActiveDoc 为 None：Simulation 中没有活动文档"
        )
    return document


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   ICWModelDoc.get_StudyManager() → CWStudyManager（属性，非方法）
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_study_manager(sw_app):
    """取 CWStudyManager。"""
    return get_com_member(get_cw_document(sw_app), "StudyManager")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   ICWStudyManager.CreateNewStudy3 的官方签名（共 4 个参数）：
#             CWStudy CreateNewStudy3( String Name,
#                                     Int32 StudyType,
#                                     Int32 MeshType,
#                                     Int32& ErrorCode )
#           另有降级入口 CreateNewStudy2(String, Int32, Int32&) 与
#           CreateNewStudy(String, Int32, Int32&) —— 两者少一个 MeshType，
#           本模块只在 CreateNewStudy3 不可用时按序降级，并在返回值里如实
#           报告实际用到的入口名。
# ⚠ 关于末位 Int32& ErrorCode：pywin32 迟到绑定下 by-ref 出参**不一定**
#   回写到 Python 标量（与 AGENTS.md §六 事实 11 同源问题）。故本函数
#   **不以 error_code 作为成功判据**，只以返回值是否为 None 判成败，
#   error_code 仅作附加信息透出。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_static_study(
    sw_app,
    name: str,
    *,
    study_type: int = SWS_ANALYSIS_STUDY_TYPES["static"],
    mesh_type: int = SWS_MESH_TYPES["solid"],
):
    """新建研究。返回 ``(study, entry_name, error_code)``。

    ``entry_name`` 标明实际命中的入口（CreateNewStudy3/2/1），
    便于调用方判断结果是否来自降级路径。
    """
    manager = get_study_manager(sw_app)
    if manager is None:
        raise RuntimeError("CWModelDoc.StudyManager 为 None")

    study = None
    entry_name = ""
    error_code = 0

    # CreateNewStudy3(name, studyType, meshType, &err)
    study = get_com_member(
        manager, "CreateNewStudy3", str(name), int(study_type), int(mesh_type), 0
    )
    if study is not None:
        entry_name = "CreateNewStudy3"
    else:
        # CreateNewStudy2(name, studyType, &err) —— 无 MeshType
        study = get_com_member(
            manager, "CreateNewStudy2", str(name), int(study_type), 0
        )
        entry_name = "CreateNewStudy2" if study is not None else ""
        if study is None:
            # ⚑ CreateNewStudy(String, Int32, Int32, Int32&) —— 官方是 **4 参**，
            #   与 CreateNewStudy3 同形（Name, StudyType, MeshType, &Err）。
            #   本函数初稿误按 3 参调用，是被 D:\AI\SW\tools\audit_call_arity.py
            #   的自动 arity 比对抓出来的（它报「同名成员存在但 arity 全对不上」）。
            study = get_com_member(
                manager, "CreateNewStudy", str(name), int(study_type), int(mesh_type), 0
            )
            entry_name = "CreateNewStudy" if study is not None else ""

    if study is None:
        raise RuntimeError(
            "创建研究失败：CreateNewStudy3 / 2 / 1 均未返回对象。"
            "常见原因见 swsStudyError_e："
            "1=无实体、2=同名研究已存在或名称非法、3=类型未定义、4=网格类型非法"
        )
    return study, entry_name, error_code


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   ICWStudyManager.get_StudyCount()（属性）与 GetStudy(Int32)（方法）。
#           ⚠ 二者形态不同：StudyCount 是**属性**、不可加括号调用；
#           GetStudy 是**方法**、必须传下标。AGENTS.md §六 事实 4 记载的
#           「迟到绑定下同一成员可能是属性也可能是方法」在此处成立，
#           故统一经 get_com_member 取值。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def iter_studies(sw_app):
    """按顺序产出全部研究对象。"""
    manager = get_study_manager(sw_app)
    if manager is None:
        return
    count = int(get_com_member(manager, "StudyCount") or 0)
    for index in range(count):
        study = get_com_member(manager, "GetStudy", index)
        if study is not None:
            yield index, study


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   ICWLoadsAndRestraints.get_Name()（属性）用于比对研究名。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_study_by_name(sw_app, name: str):
    """按名字取研究；找不到返回 None。"""
    for _, study in iter_studies(sw_app):
        if str(get_com_member(study, "Name") or "") == str(name):
            return study
    return None


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   ICWStudy.get_LoadsAndRestraintsManager() → CWLoadsAndRestraintsManager。
#           该成员是**属性**（getter 名含 get_），不是无参方法。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def _loads_and_restraints_manager(study):
    """取研究的载荷与夹具管理器。

    ICWStudy.get_LoadsAndRestraintsManager() 是**属性**，不是方法。
    """
    manager = get_com_member(study, "LoadsAndRestraintsManager")
    if manager is None:
        raise RuntimeError("ICWStudy.LoadsAndRestraintsManager 为 None")
    return manager


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   ICWLoadsAndRestraintsManager.AddRestraint 的官方签名（共 4 个参数）：
#             CWRestraint AddRestraint( Int32   RestraintType,
#                                       Object  Entities,
#                                       Object  <第 3 参语义未查证>,
#                                       Int32&  ErrorCode )
#           返回的 CWRestraint 上有 set_RestraintType(Int32) 可事后改类型。
# 查证:   sw_know.py 对 cosworks 无收录（其镜像只含 12 个程序集），
#         故本签名取自 D:\AI\SW\_raw\reflect\iface_cosworks.txt。
# ⚠ 查不到故不编（AGENTS.md 铁律 5）:
#   AddRestraint 的第 3 个 Object 参数，CHM cosworks 册为空壳、C:\\swapi 未收录，
#   **参数语义查不到**。本模块按「None 表示不指定」传入并在文档中标注，
#   不猜测其含义。若后续拿到官方说明，只需改这一处。
# ⚠ 第 4 参 Int32& 为 by-ref，迟到绑定下不保证回写，故不作为成败判据，
#   只以返回值是否为 None 判断。
# ⚠ 与外部实现的差异: alisamsam (MIT) 调的是 ``AddRestraint3`` ——
#   反射清单中**该成员不存在**（只有 AddRestraint），详见 docs/signature-audit.md。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def apply_fixed_restraint(study, *, restraint_type: int = SWS_RESTRAINT_TYPES["fixed"]):
    """施加夹具，返回 ICWRestraint 对象。

    调用前须由调用方用 ``sw_part._select_by_id`` 选好要固定的实体。
    """
    manager = _loads_and_restraints_manager(study)
    restraint = get_com_member(
        manager, "AddRestraint", int(restraint_type), None, None, 0
    )
    if restraint is None:
        raise RuntimeError(
            f"AddRestraint({restraint_type}) 未返回对象："
            "常见原因为选区为空，或该实体类型不支持所选夹具类型"
        )
    return restraint


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   ICWLoadsAndRestraintsManager.AddForce 的官方签名（共 4 个参数）：
#             CWForce AddForce( Int32  ForceType,
#                               Object Entities,
#                               Object <第 3 参语义未查证>,
#                               Int32& ErrorCode )
#           ⚠ **力的大小不在 AddForce 的参数里**。大小要在返回的 CWForce 上
#           用 set_NormalForceOrTorqueValue(Double) 回填 —— 该 setter 已在
#           ICWForce 的反射清单中核到。
# ⚑ 这纠正了外部实现的错误形状: alisamsam (MIT) 写成
#   ``AddForce3(0, None, magnitude, err)``（把第 3 参当大小），而官方
#   AddForce3 实为 **21 个参数**，AddForce 只有 4 个且第 3 参不是大小。
# ⚠ 第 3 参语义未查证（CHM 空壳 + swapi 未收录），按 None 传入并标注。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def apply_normal_force(
    study,
    magnitude: float,
    *,
    force_type: int = SWS_FORCE_TYPES["normal"],
    unit: int = SWS_FORCE_UNITS["n_or_nm"],
):
    """施加法向力载荷，返回 ICWForce 对象。

    :param magnitude: 力的数值，其量纲由 ``unit`` 决定
        （``n_or_nm``=N，``lb_or_lbin``=lbf，``kgf_or_kgfcm``=kgf）。
    :raises ValueError: ``magnitude`` 为 0 时拒绝创建。
    """
    if float(magnitude) == 0.0:
        raise ValueError("力的大小不能为 0")

    manager = _loads_and_restraints_manager(study)
    force = get_com_member(manager, "AddForce", int(force_type), None, None, 0)
    if force is None:
        raise RuntimeError(
            f"AddForce({force_type}) 未返回对象："
            "常见原因为选区为空，或该实体类型不支持所选力类型"
        )
    # 大小与单位在返回对象上回填，不是 AddForce 的入参。
    get_com_member(force, "ForceType", int(force_type))
    get_com_member(force, "Unit", int(unit))
    get_com_member(force, "NormalForceOrTorqueValue", float(magnitude))
    return force


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   ICWStudy.CreateMesh 的官方签名（共 3 个参数）：
#             Int32 CreateMesh( Int32 <第 1 参语义未查证>,
#                                Double <第 2 参>,
#                                Double <第 3 参> )
# ⚠ CreateMesh 挂在 **ICWStudy** 上，不在 ICWStudy.Mesh 上 ——
#   cosworks.dll 的 84 个 ICW* 接口中**根本没有 ICWMesh**（只有 CWMesh coclass），
#   故 ``study.Mesh.CreateMesh(...)`` 在类型层面即不成立。
# ⚠ 第 1 参与后两参的单位/语义未查证（CHM 空壳），本函数按官方位置传 0.0 占位
#   并在返回值中透出调用方实参，避免把「猜的默认值」伪装成确定行为。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_mesh(study, mesh_type: int = 0, tolerance: float = 0.0, size: float = 0.0):
    """在研究上生成网格，返回官方返回码（0 通常表示成功，具体语义未查证）。"""
    return int(
        get_com_member(study, "CreateMesh", int(mesh_type), float(tolerance), float(size))
        or 0
    )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   ICWStudy.RunAnalysis 的官方签名是 **Int32 RunAnalysis()，零个参数**。
# ⚠ 这纠正了外部实现的错误形状: alisamsam (MIT) 写成 ``RunAnalysis(err_code)``。
#   该模式与 AGENTS.md §六 记载的「CreateMotionStudy 当成有参（实为零参）」
#   同源 —— 同一个模型、同一种想当然的错误，跨项目复现。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def run_analysis(study):
    """求解当前研究，返回官方返回码。"""
    return int(get_com_member(study, "RunAnalysis") or 0)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   证据回读只使用已核实的**属性**成员，避免触碰未查证的方法：
#             ICWStudy                    : Name / MeshType / AnalysisType /
#                                           ConfigurationName（均为属性）
#             ICWStudyManager             : StudyCount / ActiveStudy（属性）
#             ICWLoadsAndRestraintsManager: Count（属性）
#             ICWLoadsAndRestraints       : Name / EntityCount / Type / State（属性）
#           方法侧只用一个：GetLoadsAndRestraints(Int32 Index, Int32& ErrCode)，共 2 参。
# ⚑ 修正记录: 本函数初稿误用 ``lrm.EntityCount`` 计数、并把
#   ``GetLoadsAndRestraints`` 当成单参方法调用。反射清单显示该方法是
#   **双参（末位 by-ref）**，计数属性在管理器上叫 ``Count`` 而非
#   ``EntityCount``（EntityCount 属于单条载荷对象）。已改正。
# ⚠ ICWResults 上**没有** GetStressComponent / GetDisplacementComponent ——
#   alisamsam (MIT) 调用的这两个方法在反射清单中不存在，故本模块不提供
#   应力/位移结果读取，并在「仍然空缺」中记明。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_study_evidence(sw_app) -> dict[str, Any]:
    """回读研究、载荷夹具与求解状态，形成可审计证据。

    **刻意不读取结果数值**：ICWResults 的可用成员已在反射清单中逐条核对，
    应力/位移分量读取入口未查到可信签名，宁可不提供也不臆造。
    """
    cosmos = get_cosmosworks(sw_app)
    document = get_com_member(cosmos, "ActiveDoc")
    manager = get_com_member(document, "StudyManager") if document is not None else None

    studies: list[dict[str, Any]] = []
    if manager is not None:
        active_index = int(get_com_member(manager, "ActiveStudy") or -1)
        for index, study in iter_studies(sw_app):
            lrm = get_com_member(study, "LoadsAndRestraintsManager")
            entities: list[dict[str, Any]] = []
            if lrm is not None:
                # 官方签名: CWLoadsAndRestraints GetLoadsAndRestraints( Int32 Index,
                #                                                          Int32& ErrCode )
                # —— 共 2 个参数，末位为 by-ref 出参。故此处必须传两个实参。
                total = int(get_com_member(lrm, "Count") or 0)
                for position in range(total):
                    entry = get_com_member(lrm, "GetLoadsAndRestraints", position, 0)
                    if entry is None:
                        continue
                    entities.append({
                        "name": str(get_com_member(entry, "Name") or ""),
                        "type": int(get_com_member(entry, "Type") or -1),
                        "state": int(get_com_member(entry, "State") or -1),
                        "entity_count": int(get_com_member(entry, "EntityCount") or 0),
                    })
            studies.append({
                "index": index,
                "name": str(get_com_member(study, "Name") or ""),
                "analysis_type": int(get_com_member(study, "AnalysisType") or -1),
                "mesh_type": int(get_com_member(study, "MeshType") or -1),
                "configuration": str(get_com_member(study, "ConfigurationName") or ""),
                "is_active": index == active_index,
                "loads_and_restraints": entities,
            })

    return {
        "cosmos_version": str(get_com_member(cosmos, "VersionNumber") or ""),
        "has_active_document": document is not None,
        "study_count": len(studies),
        "active_study_index": (
            int(get_com_member(manager, "ActiveStudy") or -1) if manager is not None else -1
        ),
        "studies": studies,
    }
