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
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游与既有模式的写法**发展而来）。
# 文件:   scripts/sw_simulation.py —— 本文件（**轮 145 的命名迁移**）。
# 定位:   2026-10-01（轮 145）**只做了一件事**：把那些「**故意要调**」的零参调用
#         从 `get_com_member(...)` 改成 **`call_com_member(...)`**。
#         ★★ 起因：审计（`tools/audit_get_com_member_semantics.py`）发现
#         `get_com_member` 的语义是「**取或调**」—— **对 COM 成员，「取」可能等于「调」**；
#         而 471 个无实参调用点里有 193 处的成员在反射里**有零参重载**（会真的执行）。
#         ★ 逐条读过之后确认：**作者大多是故意的**（拿返回值当成败 / 要的就是那个动作），
#         但**代码里读不出来** ⇒ 本轮用 `call_com_member` **让名字表态**。
# 官方签名依据: 本次迁移**不改任何 COM 调用**（只是换个名字），
#         各调用的官方依据在原函数的来源块里。
# 许可:   本仓库 MIT（上游部分见 `THIRD-PARTY-NOTICES.md`）。无第三方代码引入。
# 覆盖:   全文件 —— ⚠ 本块是**轮 145 迁移这件事**的说明，
#         它**不替代**本文件里原有的、更精确的逐函数来源块。
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from pathlib import Path
from typing import Any

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（AGENTS.md 铁律 1 认可的第三类来源）
# 文件:   scripts/sw_simulation.py 的依赖导入块；写法参照 scripts/sw_sheet_metal.py
#         的「try: from .x import / except ImportError: from x import」双路解析模式。
# 定位:   导入的五个 helper 各有出处：`get_com_member` 见 AGENTS.md §六 已知事实 4
#         （迟到绑定下属性/方法二象性）；`create_empty_dispatch_variant` 见已知事实 12；
#         `out_i4` 与 `set_com_member` 是 2026-10-01 真机实测新增
#         （`D:\AI\SW\probe_outparam_convention.py` / `probe_setter_forms.py`）；
#         `safe_get_com_member` 是 `get_com_member` 的宽容别名，供逐下标探测选区用。
# 官方签名依据: ICWLoadsAndRestraintsManager 的 AddRestraint / AddForce 一族的
#         参数类型（String / Int32 / Variant / Object / Int32&）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本导入块整体（自本行至 except 分支结束）
# ─────────────────────────────────────────────────────────────────────────
try:
    from .sw_connect import (
        call_com_member,
        create_empty_dispatch_variant,
        get_com_member,
        out_i4,
        safe_get_com_member,
        set_com_member,
    )
except ImportError:
    from sw_connect import (
        call_com_member,
        create_empty_dispatch_variant,
        get_com_member,
        out_i4,
        safe_get_com_member,
        set_com_member,

    )

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
    "create_study_report",
    "list_studies",
    "find_study",
    "mesh_size_report",
    "create_mesh_report",
    "run_analysis_report",
    "apply_fixed_restraint",
    "apply_normal_force",
    "run_analysis",
    "create_mesh",
    "collect_study_evidence",
]

#: 加载项的 ProgID，供 ``ISldWorks.GetAddInObject`` 使用。
#: 该字符串不在 cosworks.dll 内（属 SolidWorks 主程序集侧），未查到官方常量定义，
#: 沿用 alisamsam/Solidworks-MCP (MIT) 的取值并在此显式标注为**待二次确认**。
#: ⚑ **2026-10-01（轮 202）二次确认完成**：本机只读注册表实测
#: `HKLM\SOFTWARE\Classes\SldWorks.Simulation` **存在**，且它指向 CLSID
#: `{C8F79410-CD71-4061-A2E4-B6BF17CCB27F}` ⇒ `InprocServer32` = 下面的 `SIMULATION_ADDIN_DLL`。
#: ⇒ ★ **这个 ProgID 是对的**（旧代码取不到它，不是 ProgID 的问题，是**加载项没启用**）。
SIMULATION_ADDIN_PROGID = "SldWorks.Simulation"

#: Simulation 加载项 DLL 的**完整路径** —— `LoadAddIn` 要的是这个（官方文档：
#: "Fully qualified file name of the add-in"）。路径来自只读注册表的 `InprocServer32`。
SIMULATION_ADDIN_DLL = Path(
    r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\Simulation\cosworks.dll")

#: 官方 `swLoadAddinError_e`（读 `C:\swapi\enums\swLoadAddinError_e.md`）——
#: ★ 有它才能**把"许可错"和"文件没找到"分开**（7 vs 3）。
#: ⚠ 旧代码把 `LoadAddIn` 的 `3` 读成了"可能是许可问题"，**那是错的**。
LOAD_ADDIN_CODES = {
    0: "swSuccess", 1: "swAddinNotLoaded", 2: "swAddinAlreadyLoaded", 3: "swFileNotFound",
    4: "swAddinsDisabled", 5: "swLoadConflict", 6: "swRegistrationError",
    7: "swLicenseError", -1: "swUnknownError",
}


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
def ensure_simulation_addin(sw_app):
    """取 Simulation **加载项对象**（`ISldWorks.GetAddInObject`），取不到就**先用 `LoadAddIn` 装上**。

    :param sw_app: `ISldWorks`。
    :returns: 加载项对象（COM）。**取不到时抛 `RuntimeError`**，错误信息里带 `LoadAddIn` 的返回码。

    ⚠⚠⚠ **2026-10-01（轮 202）—— 此前那句「（需 Simulation 许可证）」是**错归因****：
    ```
    实测（本机 SW 2026 SP4.1）：
      ① 旧写法 `LoadAddIn("SldWorks.Simulation")` ⇒ 返回 **3 = swFileNotFound**
         ★ 官方文档（C:\\swapi\\types\\ISldWorks\\LoadAddIn.md）写明参数是
           "**Fully qualified file name of the add-in**" ⇒ **要完整路径**，传名字当然"找不到"
         ★ 而**许可错是 7 = swLicenseError** ⇒ 返回 3 **根本不是**许可问题
      ② 用注册表里读到的真路径（只读、不改）
         `LoadAddIn("…\\SOLIDWORKS\\Simulation\\cosworks.dll")` ⇒ **0 = swSuccess**
      ③ 加载后 `GetAddInObject("SldWorks.Simulation")` ⇒ **非 None**（CDispatch）
    ⇒ ★★ 真因是「**加载项没启用**」（`SOLIDWORKS\\Addins` 下没注册它、SW 启动时没加载），
      **不是许可**。⇒ 本函数把 LoadAddIn 这一步**做进正常路径**，于是"仿真验收是红的"不再复现。
    ```
    ⚠ **`LoadAddIn` 的影响范围**：只影响**当前会话**（不改注册表、不改启动项）——
      即"这次跑得通，下次启动仍要再装一次"；★ 若要让 SW 每次自动加载，
      那要在 Tools > Add-Ins 里勾（**本函数不动那里**）。
    """
    addin = get_com_member(sw_app, "GetAddInObject", SIMULATION_ADDIN_PROGID)
    if addin is not None:
        return addin
    #: ① 取不到 ⇒ 用**完整路径**装一次（路径来自只读注册表实测；也可由调用方覆盖）
    dll = SIMULATION_ADDIN_DLL
    if not dll.is_file():
        raise RuntimeError(
            "Simulation 加载项取不到，且找不到它的 DLL（%s）⇒ "
            "**路径不对**，不是许可问题（许可错会是 7）" % dll)
    rc = get_com_member(sw_app, "LoadAddIn", str(dll))
    #: ② 装完再取
    addin = get_com_member(sw_app, "GetAddInObject", SIMULATION_ADDIN_PROGID)
    if addin is None:
        raise RuntimeError(
            "LoadAddIn(%s) ⇒ %s（%s），之后 GetAddInObject 仍为 None ⇒ "
            "见 swLoadAddinError_e：0=成功·2=已加载·3=文件没找到·4=被禁用·7=**许可错**"
            % (dll, rc, LOAD_ADDIN_CODES.get(rc, "不在枚举里")))
    return addin


def get_cosmosworks(sw_app):
    """取 ICosmosWorks 入口。加载项未就绪时**先装**（见 `ensure_simulation_addin`）再抛。"""
    addin = ensure_simulation_addin(sw_app)
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
        manager, "CreateNewStudy3", str(name), int(study_type), int(mesh_type), out_i4()
    )
    if study is not None:
        entry_name = "CreateNewStudy3"
    else:
        # CreateNewStudy2(name, studyType, &err) —— 无 MeshType
        study = get_com_member(
            manager, "CreateNewStudy2", str(name), int(study_type), out_i4()
        )
        entry_name = "CreateNewStudy2" if study is not None else ""
        if study is None:
            # ⚑ CreateNewStudy(String, Int32, Int32, Int32&) —— 官方是 **4 参**，
            #   与 CreateNewStudy3 同形（Name, StudyType, MeshType, &Err）。
            #   本函数初稿误按 3 参调用，是被 D:\AI\SW\tools\audit_call_arity.py
            #   的自动 arity 比对抓出来的（它报「同名成员存在但 arity 全对不上」）。
            study = get_com_member(
                manager, "CreateNewStudy", str(name), int(study_type), int(mesh_type), out_i4()
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
# 仓库:   本项目自身（本机实测结论的固化）
# 文件:   scripts/sw_simulation.py 的 _selected_dispatch_array
# 定位:   AGENTS.md 铁律 4「三源互证」的产物：官方 VB 示例（CHM `cworksapi`
#         的 Create_Topology_Study_Example_VBA）+ 官方参数名表（工作区
#         `solidpilot-salvage/官方文档/Simulation载荷夹具API签名全表.md`）
#         + 本机实测（`D:\AI\SW\probe_disparray_forms.py` 六种形态逐一试）。
# 官方签名依据: ICWLoadsAndRestraintsManager.AddRestraint(Int32 NRestraintType,
#         Variant DispArray, Object RefGeom, Int32& ErrorCode)
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ─────────────────────────────────────────────────────────────────────────
def _selected_dispatch_array(model, expected: int | None = None):
    """把**当前选区**里的实体装成官方要求的 ``DispArray``。

    官方示例（工作区 `_raw/cworksapi/Create_Topology_Study_Example_VBA.txt`）：
    ```vb
    Set DispatchObj1 = Part.SelectionManager.GetSelectedObject6(1, -1)
    DispArray = Array(DispatchObj1, DispatchObj2)
    Set CWRestraintObj = LoadsAndRestraintsManagerObj.AddRestraint(0, (DispArray), Nothing, ErrorCodeObj)
    ```
    ⇒ ``DispArray`` 是 ``GetSelectedObject6(i, -1)`` 取出的对象**数组**，不是 ``Nothing``。

    ⚑ 真机结论（2026-10-01，SW 2026 SP4.1）：第 2 参传 ``None`` ⇒ ``AddRestraint``
      返回 None（无实体，夹具建不出来，且**不抛异常**）；传对象列表 ⇒ 返回对象且
      ``LoadsAndRestraintsManager.Count == 1``。

    :param expected: 期望实体数；给定时不足则抛 ``RuntimeError``（早失败优于静默）
    """
    mgr = get_com_member(model, "SelectionManager")
    objs: list[Any] = []
    index = 1
    while index <= 512:  # 防御：选区异常大时停下，不无限循环
        obj = safe_get_com_member(mgr, "GetSelectedObject6", index, -1)
        if obj is None:
            break
        objs.append(obj)
        index += 1
    if expected is not None and len(objs) < expected:
        raise RuntimeError("选区里只有 %d 个实体，至少要 %d 个" % (len(objs), expected))
    return objs


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
# ⚑ 2026-10-01 真机补齐（`D:\AI\SW\probe_disparray_forms.py`，六种形态）：
#   第 2 参（`DispArray`，官方示例里是 `Array(GetSelectedObject6(1,-1), …)`）
#   **必须是选中对象的列表**；传 `None` 不抛异常但**返回 None**（没有实体）。
#   第 3 参（`RefGeom`）**必须**是空 Dispatch —— 裸 `None` 一律抛 `类型不匹配 (arg 3)`，
#   与第 2 参无关（官方 VB 写 `Nothing`，那 ≡ pywin32 的 `VARIANT(VT_DISPATCH, None)`）。
#   传对之后 `LoadsAndRestraintsManager.Count == 1`，夹具确实建成。
# ────────────────────────────────────────────────────────────────────
def _require_nonempty_selection(model, *, what: str) -> int:
    """★★★ **前置判据：选区不能为空**（★ 2026-10-04 —— 这条的缺失正是那条弹窗的根因）。

    ★★★★ 为什么必须有它（★ 真根因，就在本文件的注释里、**写了好几年而没人执行**）：
      · 本文件 `select_face_at` 的 docstring 逐字写着：
        「计数为 ``0`` 就说明没选中，**此时不要继续施夹/加载**（会得到空的 ``DispArray``）」✓
      · ★★ 而**没有任何调用方执行它** ⇒ 于是当坐标不在面上时（真机实测：
        `SelectByID2("", "FACE", 0, 0, 0, …)` 回计数 **0**，因为**原点在实体内部**），
        `AddForce` 拿到**空 DispArray** ⇒ ★★ **载荷建成但无效** ⇒ Simulation 弹
        「**未定义载荷或规定的位移** … 固定-刚性零件上的载荷将不处于活动状态」⇒
        ★ `RunAnalysis` 返回 0、`Results` 为空 ⇒ **整条链白跑**（★ 2026-10-01/02 与今天
        三次撞的都是它，而那句注释每次都在旁边）✓
    ⇒ ★ 所以把它**变成会拒绝的代码**（★ 事实 40：判据要能被机器守住，否则等于没有）✓

    :raises ValueError: 选区计数为 0（★ 带**怎么改**的提示）。
    """
    try:
        from .sw_selection_spec import get_selection_count
    except ImportError:
        from sw_selection_spec import get_selection_count

    n = int(get_selection_count(model) or 0)
    if n <= 0:
        raise ValueError(
            "%s 之前**选区是空的**（回读计数 0）⇒ 拒绝继续 —— ★ 那会得到空的 DispArray，"
            "载荷/夹具**建成也无效**，求解时会弹「未定义载荷或规定的位移」并失败。"
            "★ 改法：用 `face_selector`（如 `-z` / `+z` / `+x` …）或先确认那个坐标点"
            "**落在面上**（真机实测：`(0,0,0)` 在实体内部 ⇒ 计数 0；`(0,0,-0.02)` 在面上 ⇒ 计数 1）"
            % what)
    return n


def apply_fixed_restraint(study, *, model=None, face_selector: str | None = None,
                          restraint_type: int = SWS_RESTRAINT_TYPES["fixed"]):
    """施加夹具，返回 ICWRestraint 对象。

    ★ 实体选择有**三条**合法的路（★ 推荐第 1 条 —— 它**不带坐标**）：
      ① ``face_selector="-z"`` 之类**声明式**选择器（本函数内部解析成面上的点并回读计数）；
      ② 调用方**先选好**（此时本函数只回读计数）；
      ③ ``sw_part._select_by_id`` 一类的旧路（★ 不推荐）。
    ★★ **三条路都要求选区计数 ≥ 1** —— ★ 空选区会被**拒绝**（见 `_require_nonempty_selection`）✓
    ``model`` 是活动文档 —— **给了它才会把选区实体装成官方要求的 ``DispArray``**；
    不给则退回旧行为（传 ``None``），此时**必然建不出来**，只为兼容既有调用方。
    """
    if face_selector is not None:
        if model is None:
            raise ValueError("给了 `face_selector` 就必须同时给 `model`（要用来解析面上的点）")
        _n = select_face_by_selector(model, str(face_selector))
    if model is not None:
        _require_nonempty_selection(model, what="AddRestraint")
    manager = _loads_and_restraints_manager(study)
    entities = _selected_dispatch_array(model) if model is not None else None
    restraint = get_com_member(
        manager, "AddRestraint", int(restraint_type), entities,
        create_empty_dispatch_variant(), out_i4(),
    )
    if restraint is None:
        raise RuntimeError(
            f"AddRestraint({restraint_type}) 未返回对象："
            + ("未传 model ⇒ 无法把选区实体装成 DispArray" if model is None
               else f"选区里只有 {len(entities or [])} 个实体；"
                    "常见原因为选区为空，或该实体类型不支持所选夹具类型")
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
# ⚑ 2026-10-01 真机补齐：与 `apply_fixed_restraint` 同一族 ——
#   第 2 参（`DispArray`）**必须是选中对象的列表**（传 None 会返回 None 而不抛异常），
#   第 3 参（`RefGeom`）**必须**是空 Dispatch。详见 `_selected_dispatch_array` 的注释。
# ────────────────────────────────────────────────────────────────────
def apply_normal_force(
    study,
    magnitude: float,
    *,
    model=None,
    face_selector: str | None = None,
    force_type: int = SWS_FORCE_TYPES["normal"],
    unit: int = SWS_FORCE_UNITS["n_or_nm"],
):
    """施加法向力载荷，返回 ICWForce 对象。

    ★ 与 `apply_fixed_restraint` 同契约：★ `face_selector="-z"/"+z"` 之类**声明式**选择器
      （★ **推荐**）· 或调用方**先选好** —— ★★ **两者都要求选区计数 ≥ 1**，
      ★ 空选区会被**拒绝**（★ 那正是「未定义载荷或规定的位移」那条弹窗的根因，
      见 `_require_nonempty_selection`）✓
    ``model`` 是活动文档 —— **给了它才会把选区实体装成官方要求的 ``DispArray``**。

    :param magnitude: 力的数值，其量纲由 ``unit`` 决定
        （``n_or_nm``=N，``lb_or_lbin``=lbf，``kgf_or_kgfcm``=kgf）。
    :raises ValueError: ``magnitude`` 为 0 时拒绝创建；★ 或**选区为空**时拒绝。
    """
    if float(magnitude) == 0.0:
        raise ValueError("力的大小不能为 0")
    if face_selector is not None:
        if model is None:
            raise ValueError("给了 `face_selector` 就必须同时给 `model`（要用来解析面上的点）")
        _n = select_face_by_selector(model, str(face_selector))
    if model is not None:
        _require_nonempty_selection(model, what="AddForce")

    manager = _loads_and_restraints_manager(study)
    entities = _selected_dispatch_array(model) if model is not None else None
    force = get_com_member(
        manager, "AddForce", int(force_type), entities,
        create_empty_dispatch_variant(), out_i4(),
    )
    if force is None:
        raise RuntimeError(
            f"AddForce({force_type}) 未返回对象："
            "常见原因为选区为空，或该实体类型不支持所选力类型"
        )
    # 大小与单位在返回对象上回填，不是 AddForce 的入参。
    # ⚑ 补正（反射 ICWForce 段才发现）：官方提供
    #   ForceBeginEdit() / ForceEndEdit() 一对**编辑事务**入口。
    #   本函数初稿直接设属性、**没有开事务**。
    #   ICWContactSet 也有同形的 ContactSetBeginEdit / ContactSetEndEdit，
    #   说明这是载荷/接触对象的**通用约定**，不是 ICWForce 独有。
    #   按反射签名，两方法都是**零参**。
    get_com_member(force, "ForceBeginEdit")
    try:
        # ⚑ 2026-10-01 真机（`probe_setter_forms.py`）：这些属性**只能用赋值写**。
        #   反射里叫 `set_ForceType` / `set_Unit` / `set_NormalForceOrTorqueValue`，
        #   但 pywin32 迟到绑定下那三个名字**取不到**（`set_` / `put_` 都失败），
        #   唯一可行的是 `f.ForceType = …` ⇒ 用 `set_com_member`。
        set_com_member(force, "ForceType", int(force_type))
        set_com_member(force, "Unit", int(unit))
        set_com_member(force, "NormalForceOrTorqueValue", float(magnitude))
    finally:
        # 无论设成功与否都收尾，避免编辑事务悬着
        get_com_member(force, "ForceEndEdit")
    return force


#: ``swsUnit_e`` —— 与 VB6 CHM 的 `CosmosWorksLib~swsUnit_e` 页逐条一致。
#  ⚠ 这三行常量有意放在**来源块之前**：`check_provenance` 的 `_extend_to_code`
#  把来源块之后的**第一个代码单元**当作被说明对象；常量若夹在块与 `def` 之间，
#  延伸会止于常量，`def` 反而落空。
SWSU_SI = 0
SWSU_ENGLISH = 1
SWSU_METRIC = 2


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 Simulation **VB6 类型库 CHM**（唯一给出参数名的源）
# 文件:   `lang\english\api\cworksapivb6.chm` 的
#         `CosmosWorksLib~CWStudy~CreateMesh.html`（解包到 `C:\cworks_vb6`）
# 定位:   ``ICWStudy.CreateMesh`` 的**官方参数名与顺序**：
#             Public Function CreateMesh( _
#                 ByVal NUnits As Long, _          ' ← 第 1 参 = 单位（swsUnit_e）
#                 ByVal DElementSize As Double, _  ' ← 第 2 参 = 单元尺寸
#                 ByVal DTolerance As Double _     ' ← 第 3 参 = 容差
#             ) As Long
# 枚举:   ``swsUnit_e`` = SI 0 / English 1 / Metric 2
#         （同源页 `CosmosWorksLib~swsUnit_e.html`）
# ⚠⚠ **本函数此前把第 2、3 参写反了**（旧签名 `create_mesh(study, mesh_type, tolerance, size)`
#   把 tolerance 传在第 2 位、size 第 3 位）。2026-10-01 真机实测（SW 2026 SP4.1）：
#         CreateMesh(0, 4.9339, 0.2467)   → 返回 0，**7,219 个单元**（100×60×20 mm 板，✓ 正常）
#         CreateMesh(0, 0.2467, 4.9339)   → 返回 0，**19,509,593 个单元**（✗ 爆），耗时 233 秒
#   反推：单元体积 = 1.2e5 mm³ ÷ 1.95e7 = 0.00614 mm³ ⇒ 边长 0.183 mm，
#   与「ElementSize 被当成 0.2467」同量级 ⇒ **吻合**。
#   ⇒ 单位是**毫米**（与文档单位制一致），不是米：
#     同一次实测里 `GetDefaultElementSizeAndTolerance(-1,·)` 返回 4.9339/0.2467，
#     对 100 mm 的板正是「约 5% 板长」的合理建议值；而传 `(2, ·)` 时它返回米级 0.0049339。
# ⚠ 另注：`CreateMesh` 挂在 **ICWStudy** 上；`ICWMesh`（coclass `CWMesh`）持有
#   `ElementSize` / `Tolerance` / `Unit` / `ElementCount` / `NodeCount` 等**设置与回读**成员，
#   但**不持有** `CreateMesh`。设置用 `study.Mesh`，执行用 `study.CreateMesh(...)`。
# ⚠ 本函数为照官方签名新写：**调用形状已真机实测**（见上），
#   但**整链（建网格→求解→出结果）未在本机实测**（求解仍卡在材料赋值）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ────────────────────────────────────────────────────────────────────
def create_mesh(study, *, units: int = SWSU_SI, element_size: float = 0.0,
                tolerance: float = 0.0):
    """在研究上生成网格，返回官方返回码（0 = ``swsStudyMeshSucceeded``）。

    ⚠ **参数单位是「毫米」**（与文档长度单位一致），且**顺序是**
    ``(NUnits, DElementSize, DTolerance)`` —— 见上方来源块的真机证据。

    ⚠ **两者都必须是正数**：传 0 会得到返回码 **5**（``SpecifyPositiveValue``）。
    不知道给什么值时，用 ``default_element_size_and_tolerance(study, units)``
    取官方建议值（对本机 100×60×20 mm 的板是 4.9339 / 0.2467）。

    :param units: ``swsUnit_e``（``SWSU_SI`` / ``SWSU_ENGLISH`` / ``SWSU_METRIC``）。
    :param element_size: 全局单元尺寸（毫米）。
    :param tolerance: 网格容差（毫米）；官方默认是单元尺寸的 5%。
    :returns: 官方返回码。0 = 成功；5 = 尺寸/容差非正。
    """
    return int(
        get_com_member(study, "CreateMesh", int(units),
                       float(element_size), float(tolerance))
        or 0
    )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 Simulation VB6 类型库 CHM（同 `create_mesh` 的来源块）
# 文件:   `CosmosWorksLib~CWMesh~GetDefaultElementSizeAndTolerance.html`
# 定位:   ``Public Sub GetDefaultElementSizeAndTolerance( _
#             ByVal NUnits As Long, _      ' 与 CreateMesh 的第 1 参同义
#             ByRef DElementSize As Double, _
#             ByRef DTolerance As Double _ )``
# ⚠ 真机实测（2026-10-01）：传 ``NUnits=-1`` 返回**毫米级**（4.9339 / 0.2467）；
#   传 ``NUnits=2``（Metric）返回**米级**（0.0049339 / 0.0002467）—— 同一个建议值两种量纲。
#   **⇒ 用哪个 unit 取，就用哪个 unit 传给 `create_mesh` 的位置参数会错**；
#   本库固定用**毫米**（`SWSU_SI` 另见 `create_mesh` 的来源块实测），故这里默认 `-1`
#   以拿到毫米级数值。**⚠ 这一条「-1 给毫米」的规律是实测归纳，未在官方文档中找到说明。**
# ⚠ 本函数返回路径的异常分支**未在本机实测**（见 AGENTS.md 铁律 2）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ────────────────────────────────────────────────────────────────────
def default_element_size_and_tolerance(study, units: int = -1) -> tuple[float, float]:
    """取官方的**建议**单元尺寸与容差。

    ★★★ **`units` 的量纲：两次真机实测**差 1000 倍**（2026-10-01）—— 见下方来源块**
        · 当时的实测：`NUnits=-1` ⇒ **4.9339 / 0.2467**（毫米）·  `NUnits=2` ⇒ **0.0049339**（米）
        · 本次的实测：`units=-1`  ⇒ **4930.50 / 246.53**       ·  `units=2`  ⇒ **4.9305 / 0.2465**
        ★ 同一个 `units` 值两次差**恰好 1000 倍** ⇒ ★★ **说明返回值按「文档当前单位」解释**
          （★ 而两次的**文档单位不同** —— ★ **具体原因未查清**，不编解释）。
        ⚠ **父进程与子进程回的值完全一致**（本次实测）⇒ 与"在哪个进程调"无关。
    ★★ **用法上的硬约束**：★ **「取」与「用」必须口径一致** ——
        取到什么值就**原样**传给 `create_mesh` 的 `element_size` / `tolerance`，
        ★ **不要自己换算**（★ 既有证据脚本 `tools/capture_simulation_evidence.py` 就是这么用的，
        它多次真机跑通：网格 7,310 单元 · 4 张图）。

        :returns: ``(element_size, tolerance)``；调用失败时返回 ``(0.0, 0.0)``。
    """
    import pythoncom
    from win32com.client import VARIANT

    mesh = get_com_member(study, "Mesh")          # ← 设置成员在 ICWMesh 上
    v_size = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.0)
    v_tol = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.0)
    try:
        get_com_member(mesh, "GetDefaultElementSizeAndTolerance",
                       int(units), v_size, v_tol)
    except Exception:
        return 0.0, 0.0
    return float(v_size.value), float(v_tol.value)


#: 官方材料库的**显示名** —— 与 ``.sldmat`` 文件名不同，务必照此拼写
#  ⚠ 常量有意放在**来源块之前**：`check_provenance` 的 `_extend_to_code`
#  把来源块之后的**第一个代码单元**当作被说明对象；常量若夹在块与 `def` 之间，
#  延伸会止于常量，`def` 反而落空。
SWS_MATERIAL_DATABASE = "SOLIDWORKS Materials"


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks 反射）+ **VB6 类型库 CHM**（补参数名）
#         + 两家 MIT/Apache 项目的现成用法（交叉印证）
# 文件:   - `C:\swapi_vb6\SldWorks~PartDoc~SetMaterialPropertyName2.html`：
#             ``Public Sub SetMaterialPropertyName2( _
#                 ByVal ConfigName As String, ByVal Database As String, ByVal Name As String)``
#         - `C:\swprojects\Eduardof0nt\sw_client.py`（MIT，`set_material`）：
#             ``doc.SetMaterialPropertyName2("", database_name, material_name)``，
#             其默认 ``database_name = "SOLIDWORKS Materials"``
#         - `C:\swprojects\Slacker-LLC\sw_file.py`（Apache-2.0）：同一形状
# 定位:   零件级材料赋值。**两个坑都踩过，2026-10-01 真机定案**：
#  ⚠⚠ 坑 1 —— **库名必须是大写的 ``"SOLIDWORKS Materials"``**（带空格），
#     不是 ``.sldmat`` 的**文件名** ``"solidworks materials"``。真机证据：
#         库名 "SOLIDWORKS Materials" + 材料 "Plain Carbon Steel" → 回读 ``MaterialIdName = ''``
#         库名 "SOLIDWORKS Materials" + 材料 "AISI 1020"          → 回读
#             ``'solidworks materials|AISI 1020|2'``  ✓
#     ⇒ **``"Plain Carbon Steel"`` 不在该库里**；库里是 ``"AISI 1020"`` 这类名。
#  ⚠⚠ 坑 2 —— **判据必须是回读 ``MaterialIdName``，不是返回值**。
#     ``SetMaterialPropertyName2`` 返回 ``Void``；而在研究上调用
#     ``SetFavLibraryMaterialToSelectedEntities`` / ``SetFavLibraryMaterialToAllBodiesByCompName``
#     会返回 0/1 却**都无效果**（第四个「静默成功」）。
#  ⚠ 直接写 ``set_MaterialIdName`` 只赋**标签**、不加载材料属性数据 ⇒
#     `RunAnalysis` 仍报 19（MaterialNotDefined）。**不要走那条路。**
# 许可:   本仓库 MIT；引用的两家用法仅作交叉印证，无代码移植。
# 覆盖:   本函数整体（自本行至函数结束）
# ⚠ 本函数的成功路径**已在本机实测**（见 `docs/A9-solve-attempts.md` §二之三），
#   但**失败分支**（库名/材料名拼错）未逐一实测。
# ────────────────────────────────────────────────────────────────────
def set_material(model, material_name: str,
                 database: str = SWS_MATERIAL_DATABASE) -> str:
    """给零件赋材料，**返回回读到的材料名**（空串 = 没赋上）。

    ★★★ **spec 261 换路由后的语义变化（★ 真机实测）**：本函数原先回读**废弃的** ``MaterialIdName``，
      ★ 它给的是**复合串** ``库名|材料名|编号``（★ 真机实测：``'solidworks materials|AISI 1020|2'``）；
      ★ 换到官方后继 ``IPartDoc::GetMaterialPropertyName2`` 后，回的是**纯材料名**（★ 实测：``'AISI 1020'``）。
      ⇒ ★★ **两代不等价**（★ 语义不同，不是同值）—— ★ 换路由**改善了**语义（现在可直接与 ``material_name`` 比）。
      ★★ **已核调用方（★ 这是关键）**：全仓有 **16 处**调用（★ 都在 `tools/` 的证据采集脚本里），\n        ★ 逐个核过 —— ★ 它们只用 ``bool(返回值)`` 与**直接存值**，★ **没有一处**做字符串切分/比较\n        ⇒ ★ **不依赖** ``库名|材料名|编号`` 那个格式 ⇒ ★ **语义变化是安全的**。\n      ★★ **定则：行为变化的**安全性**取决于「调用方怎么用它」，不是「有没有人用」**。

    ⚠ 库名用 ``SWS_MATERIAL_DATABASE``（``"SOLIDWORKS Materials"``），
    材料名用库里的名（如 ``"AISI 1020"``、``"Alloy Steel"``）。
    **``"Plain Carbon Steel"`` 不在该库里，用了会静默失败。**

    ⚠ ``SetMaterialPropertyName2`` 返回 ``Void`` ⇒ **判据只能是回读**，
    故本函数返回回读值而不是返回码（与 AGENTS.md 已知事实 8 同一条纪律）。

    :returns: 回读到的 ``MaterialIdName``；``''`` 表示**没赋上**（库名或材料名不对）。
    """
    get_com_member(model, "SetMaterialPropertyName2", "", database, material_name)
    return _read_material_id_name(model)


def _read_material_id_name(model) -> str:
    """读材料名（★ spec 261 换路由：官方后继 `IPartDoc::GetMaterialPropertyName2`）。

    ★★ **为什么换**：`IModelDoc2::MaterialIdName` 官方标
      「Obsolete. Superseded by [[IPartDoc::GetMaterialPropertyName2]] and
       [[IPartDoc::SetMaterialPropertyName2]]」。
    ★★★ **两处不是 drop-in**：① **接口换了**（`IModelDoc2` ⇒ **`IPartDoc`**，★ 零件文档上两者是同一 COM 对象）；
      ② **签名换了**（原是无参**属性**；后继是 `(ConfigName, out Database)` ⇒ ★ 要传配置名 + 一个 **by-ref 出参**）。
    ★ `ConfigName` 传 `""`（★ 官方 Remarks：只有默认配置时用 `""`）。
    ★ 取不到就回 `""`（★ 与旧写法同语义）。
    """
    try:
        import pythoncom
        from win32com.client import VARIANT
        db = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")
        return str(get_com_member(model, "GetMaterialPropertyName2", "", db) or "")
    except Exception:                                              # noqa: BLE001
        return ""


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks 反射）+ 本项目既有模式
# 文件:   `IModelDocExtension.SelectByID2(String Name, String Type, Double X, Double Y,
#             Double Z, Boolean Append, Int32 Mark, Callout Callout, Int32 SelectOption)`
# 定位:   按**面上的坐标**选面。**2026-10-01 真机定案的坑**：
#  ⚠⚠ 既有代码 ``sw_part._select_by_id(ext, "", "FACE", …)`` 走的是
#     ``SelectByID2("", "FACE", 0, 0, 0, …)`` —— **空名 + 硬编码原点**。
#     原点在实体**内部、不在任何面上** ⇒ **一个面都没选中** ⇒ ``DispArray`` 为空
#     ⇒ Simulation 弹「**未定义载荷或规定的位移**」（用户截图确认），求解失败。
#     真机对比（同一个 100×60×20 mm 的板）：
#         SelectByID2("", "FACE", 0, 0, 0, …)      → 选区计数 **0**
#         SelectByID2("", "FACE", 0, 0, -0.02, …)  → 选区计数 **1**  ✓
#     （``SelectByID2`` 对 FACEE 用「面**上的一个点**」定位，不是包围盒中心。）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ⚠ 已在本机实测（上面两组计数即证据）；但**只测了平面**，
#   曲面/圆柱面用点定位的行为未实测。
# ────────────────────────────────────────────────────────────────────
def select_face_at(model, x: float, y: float, z: float, *, mark: int = 0,
                   append: bool = False) -> int:
    """按**面上的一个点**（米）选面，返回**回读到的选区计数**。

    ⚠ ``SelectByID2`` 的返回值不可信（AGENTS.md 已知事实 8）⇒ 本函数返回计数。
    计数为 ``0`` 就说明没选中，**此时不要继续施夹/加载**（会得到空的 ``DispArray``）。

    :param x, y, z: 面上的一点（**米**；SolidWorks API 的长度单位）。
    :returns: ``ISelectionManager.GetSelectedObjectCount2(-1)`` 的回读值。
    """
    from .sw_part import _empty_callout
    ext = get_com_member(model, "Extension")
    get_com_member(ext, "SelectByID2", "", "FACE", float(x), float(y), float(z),
                   bool(append), int(mark), _empty_callout(), 0)
    sm = get_com_member(model, "SelectionManager")
    return int(get_com_member(sm, "GetSelectedObjectCount2", -1) or 0)


#: 声明式面选择器的合法键（**外法向**命名，不是「上/下」这类视角相关词）
#  ⚠ 常量有意放在**来源块之前**：`check_provenance` 的 `_extend_to_code`
#  把来源块之后的**第一个代码单元**当作被说明对象；常量若夹在块与 `def` 之间，
#  延伸会止于常量，`def` 反而落空。**本会话第三次踩 —— 见下方门禁改进。**
FACE_SELECTORS = ("+x", "-x", "+y", "-y", "+z", "-z")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks 反射）+ 本项目既有模式
# 文件:   `IBody2.GetBodyBox()` → `Object`（6 个 Double：xmin ymin zmin xmax ymax zmax）
#         `IModelDocExtension.SelectByID2(String, String, Double, Double, Double, …)`
# 定位:   **声明式面选择** —— 把「哪个面」解析成 ``select_face_at`` 要的**面上一点**。
#  ⚠⚠ **为什么需要这一层**（T-011 暴露的真实冲突）：
#     ``select_face_at(model, x, y, z, …)`` 的入参是**裸坐标**，
#     **违反「并入六条规则」的规则 3**（「选择用声明式 ``selection``，不写裸坐标」）
#     ⇒ 直接暴露成 MCP 工具会被本项目自己的门禁拒掉。
#     **但这不是 bug**：官方 ``SelectByID2`` 对 ``FACE`` **必须**给面上一点
#     （见 ``select_face_at`` 的来源块：给原点选不中任何面）。
#     ⇒ 正确做法是**加一层显式解析**：对外收「哪个面」，内部算成坐标。
#  ⚠ **解析规则必须显式**（不能藏在默认值里）：本函数用**轴对齐包围盒**的六个面，
#     以 **+X/-X/+Y/-Y/+Z/-Z 的向外法向**命名，取该面的**中心点**。
#     对**非轴对齐**或**曲面**零件，中心点可能不在面上 ⇒ 返回 `None` 让调用方处理。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ⚠ **未在本机实测**（2026-10-01 写就；`select_face_at` 本身已实测，但本解析层没跑过）
#   ⇒ 按铁律 2 标注；MCP 声明里不得把它写成「已验证」。
# ────────────────────────────────────────────────────────────────────
def resolve_face_selector(model, selector: str):
    """把声明式面选择器解析成 ``(x, y, z)``（**面上一点**，米）；解析不了返回 ``None``。

    :param selector: ``"+x"`` / ``"-x"`` / ``"+y"`` / ``"-y"`` / ``"+z"`` / ``"-z"``
        —— 取包围盒上**该外法向那一面的中心点**。大小写不敏感。
    :returns: ``(x, y, z)`` 三点元组，或 ``None``（选择器非法 / 取不到包围盒）。

    ⚠ **只对轴对齐的实体可靠**。曲面/斜面零件上，「包围盒那一面的中心」未必落在零件表面上
    ⇒ 此时 ``select_face_at`` 会返回选区计数 0，调用方**必须**检查计数。
    """
    key = str(selector).strip().lower()
    if key not in FACE_SELECTORS:
        return None
    bodies = get_com_member(model, "GetBodies2", 0, True)   # 0 = swSolidBody
    if not bodies:
        return None
    try:
        box = get_com_member(bodies[0], "GetBodyBox")
    except Exception:
        return None
    if not box or len(box) < 6:
        return None
    xmin, ymin, zmin, xmax, ymax, zmax = (float(box[i]) for i in range(6))
    mid = {
        "+x": (xmax, (ymin + ymax) / 2.0, (zmin + zmax) / 2.0),
        "-x": (xmin, (ymin + ymax) / 2.0, (zmin + zmax) / 2.0),
        "+y": ((xmin + xmax) / 2.0, ymax, (zmin + zmax) / 2.0),
        "-y": ((xmin + xmax) / 2.0, ymin, (zmin + zmax) / 2.0),
        "+z": ((xmin + xmax) / 2.0, (ymin + ymax) / 2.0, zmax),
        "-z": ((xmin + xmax) / 2.0, (ymin + ymax) / 2.0, zmin),
    }
    return mid[key]


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把上面两个函数组合成一个**声明式**入口）
# 文件:   scripts/sw_simulation.py 的 select_face_by_selector ——
#         组合 `resolve_face_selector`（声明式 → 坐标）与 `select_face_at`（坐标 → 选中）
# 定位:   T-011 的「声明式选择」对外形状：**收选择器，不收坐标**。
#         `ToolSpec` 里对应的参数名就叫 `selection`（规则 3 的词）。
# 官方签名依据: 复用上面两个函数已核过的官方签名，本函数**不引入新的 COM 成员**
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ⚠ **未在本机实测**（组合层没跑过；两个被组合的函数各自已实测）—— 铁律 2
# ────────────────────────────────────────────────────────────────────
def select_face_by_selector_report(model, selection: str, *, mark: int = 0,
                                   append: bool = False) -> dict:
    """★ 按**声明式选择器**选一个面，回**可 JSON 化**的报告。

    ★★ 为什么它**能**当工具而旁边两条不能（**规则 3** 的判断）：
      ★ `select_object(model, obj)`          ⇒ 吃 **COM 对象** ⇒ **没法入参数表达**
      ★ `resolve_face_selector(model, sel)`  ⇒ 回 **`(x, y, z)` 米** ⇒ **暴露它就是暴露裸坐标**
      ★★ 而本函数：**对外的参数是选择器**，坐标**只在内部用** ✓

    :param selection: 见 :data:`FACE_SELECTORS`（`+x` / `-x` / `+y` / `-y` / `+z` / `-z`）。
    :param mark: 选择标记（默认 0）。
    :param append: 传给底层的 `Append`。
        ⚠★ **真机（轮 452）**：`append=False` 时**它并没清掉上一次的选区**
        （★ 回读从 1 变成 **2**）⇒ ★★ **调用方要自己先 `ClearSelection2`**。
    :returns: `{ok, selection, count, ...}`，判据是**回读计数**（★ 不是返回值）。
    """
    try:
        n = int(select_face_by_selector(model, str(selection), mark=int(mark), append=bool(append)))
    except ValueError as exc:
        return {"ok": False, "selection": str(selection), "stage": "resolve",
                "error": str(exc)[:200], "legal": list(FACE_SELECTORS)}
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "selection": str(selection), "stage": "select",
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:160])}
    return {"ok": n == 1, "selection": str(selection), "count": n,
            "mark": int(mark), "append": bool(append),
            "★": "★ 判据是**回读计数 == 1**（★ 而不是返回值）；"
                 "★★ 而 `append=False` **不会清掉上一次** ⇒ 需要时自己先 `ClearSelection2`。"}


def select_face_by_selector(model, selection: str, *, mark: int = 0,
                            append: bool = False) -> int:
    """按**声明式选择器**选面，返回**回读到的选区计数**（0 = 没选中）。

    :param selection: 见 :data:`FACE_SELECTORS`。
    :returns: 选区计数。**调用方必须检查它** —— ``SelectByID2`` 的返回值不可信。
    :raises ValueError: 选择器非法（而不是静默不选）。
    """
    point = resolve_face_selector(model, selection)
    if point is None:
        raise ValueError(
            "非法或无法解析的面选择器 %r；合法值：%r" % (selection, list(FACE_SELECTORS))
        )
    return select_face_at(model, point[0], point[1], point[2], mark=mark, append=append)



# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   ICWStudy.RunAnalysis 的官方签名是 **Int32 RunAnalysis()，零个参数**。
# ⚠ 这纠正了外部实现的错误形状: alisamsam (MIT) 写成 ``RunAnalysis(err_code)``。
#   该模式与 AGENTS.md §六 记载的「CreateMotionStudy 当成有参（实为零参）」
#   同源 —— 同一个模型、同一种想当然的错误，跨项目复现。
# ⚠⚠ **返回码 0 不等于求解成功**（2026-10-01 真机）：夹具/载荷未定义时，
#   Simulation 弹「未定义载荷或规定的位移」且研究显示「失败」，
#   而 `RunAnalysis` **仍返回 0**。⇒ **判据必须是 `study.Results` 非空 + 图数**
#   （实测成功时 `GetPlotCount = 4`、`GetPlotNames = ('品质1','应力1','位移1','应变1')`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ⚠ 成功路径已在本机实测；失败路径未逐一实测。
# ────────────────────────────────────────────────────────────────────
def run_analysis(study):
    """求解当前研究，返回官方返回码。

    ⚠ **返回 0 不代表成功** —— 必须再用 ``study.Results`` 判定（见上方来源块）。
    """
    return int(call_com_member(study, "RunAnalysis") or 0)


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
                    entry = get_com_member(lrm, "GetLoadsAndRestraints", position, out_i4())
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

# ── Spec Kit `141`（24h 计划 段 1.1）：仿真研究族的**可 JSON 化**包装 ──────────────
# ★ 为什么要有这三个薄函数（而不是直接挂既有四个）：
#   ① `create_static_study` 回**三元组** `(study, entry_name, error_code)` —— 而 `study` 是
#      **COM 对象** ⇒ MCP **回不了对象**；★ 而 `entry_name` 是「**是否走了降级入口**」的
#      **唯一证据**（其 docstring 明写）⇒ ★ 必须把它翻出来。
#   ② `iter_studies` yield 的是 **`(index, study)` 元组** ⇒ 同样含对象 ⇒ 不可直接回。
#   ③ `get_study_by_name` 回**对象或 None** ⇒ 已实测「找不到**返回 None**，不抛错」
#      ⇒ ★ 对外要把它变成**显式的 `found` 字段**（不静默）。
# ★ 三个的返回**形状一致**（都是只含 str/int/bool 的字典）⇒ 调用方好处理。
# ★ 既有四个函数**一行未改**（本特性只**加**这三个薄函数）。


def create_study_report(sw_app, name: str) -> dict[str, Any]:
    """**新建静力学研究**并回**可 JSON 化**的报告。

    :returns: `{ok, requested_name, study_name, entry_name, error_code}`
        ★ `entry_name` 标明实际命中的入口（`CreateNewStudy3` / `2` / `1`）——
        它是「**是否走了降级路径**」的唯一证据（★ 空字符串表示**三个入口都没命中**）。
        ⚠ **只支持静力学研究**（`study_type = static`）—— 其它类型**未真机验证**。
    """
    study, entry_name, error_code = create_static_study(sw_app, name)
    actual = ""
    if study is not None:
        try:
            actual = str(get_com_member(study, "Name") or "")
        except Exception:                                      # noqa: BLE001
            actual = ""
    return {
        "ok": study is not None,
        "requested_name": str(name),
        "study_name": actual,
        "entry_name": str(entry_name or ""),
        "error_code": int(error_code or 0),
        "★": "entry_name 是「是否走了降级入口」的证据；空 ⇒ 没建成",
    }


def list_studies(sw_app) -> list[dict[str, Any]]:
    """**列出全部研究**（只回名字与序号，**不回 COM 对象**）。

    ★ `iter_studies` yield 的是 `(index, study)` 元组（含对象）⇒ 本函数把它翻成
      `[{"index": int, "name": str}, …]`。★ 取不到名字的研究**也列出来**（名字为空串），
      ★ **不跳过** —— 跳过会让调用方以为"没有这个研究"。
    """
    out: list[dict[str, Any]] = []
    for index, study in iter_studies(sw_app):
        name = ""
        try:
            name = str(get_com_member(study, "Name") or "")
        except Exception:                                      # noqa: BLE001
            name = ""
        out.append({"index": int(index), "name": name})
    return out


def find_study(sw_app, name: str) -> dict[str, Any]:
    """**按名字取研究**，回 `{found, requested_name, study_name}`。

    ★ 已实测：`get_study_by_name` 在**找不到时返回 `None`**（**不抛错**）
      ⇒ 本函数把它变成**显式的 `found` 字段**，避免调用方把"没有"当成"有"。
    """
    study = get_study_by_name(sw_app, name)
    actual = ""
    if study is not None:
        try:
            actual = str(get_com_member(study, "Name") or "")
        except Exception:                                      # noqa: BLE001
            actual = ""
    return {"found": study is not None, "requested_name": str(name), "study_name": actual}

# ── 24h 计划 段 1.2（Spec Kit `142`）：网格 / 求解的**回读优先**报告 ─────────────
# ★★★ 为什么这三个也要包（本项目的**铁律**，写在 `tools/capture_simulation_evidence.py` 里）：
#   「**COM 返回值凡不能自证，一律以回读为判据**（本项目已累计四处「返回码撒谎」）」
#   · `create_mesh` / `run_analysis` **都只回一个 int 返回码** ⇒ ★ **不能自证**
#   ⇒ 所以本函数**一律回读**，并且**显式声明返回码不可信**
#     （`return_is_trustworthy: False` —— ★ 照抄既有证据脚本的表达，让调用方**无法**误用）。
#   · `default_element_size_and_tolerance` 回 `(float, float)` ⇒ ★ 单位由 `units` 决定
#     （既有事实：`units=-1` 回**毫米级**值）。


def mesh_size_report(study, units: int = -1) -> dict[str, Any]:
    """回**建议的网格尺寸与公差**（只回数，无 COM 对象）。

    ★ `units = -1`（默认）回**毫米级**的值 —— 这是既有事实（官方 `swsUnit_e` 的语义在
      本项目里已被实测过；本函数**不做换算**，照实透传并把 `units` 一并回给调用方）。
    """
    size, tol = default_element_size_and_tolerance(study, units)
    return {"element_size": float(size), "tolerance": float(tol), "units": int(units)}


def create_mesh_report(study, units: int = 0, element_size: float = 0.0,
                       tolerance: float = 0.0) -> dict[str, Any]:
    """**建网格**并回**回读报告**。

    :returns: `{ok, return_code, return_is_trustworthy, element_count}`
        ★★ **`ok` 判的是 `element_count > 0`**，**不是**返回码 ——
        判据抄自 `tools/capture_simulation_evidence.py`：「`CreateMesh` 返回 0 **且**
        `ElementCount` 为一个（小的）正整数」。
        ★ `return_is_trustworthy` **恒为 False**：本项目的铁律是**回读优先**。
    """
    return_code = create_mesh(study, units=units, element_size=element_size, tolerance=tolerance)
    element_count = 0
    try:
        mesh = get_com_member(study, "Mesh")
        element_count = int(get_com_member(mesh, "ElementCount") or 0)
    except Exception:                                          # noqa: BLE001
        element_count = 0
    return {
        "ok": element_count > 0,
        "return_code": int(return_code or 0),
        "return_is_trustworthy": False,
        "element_count": element_count,
        "★": "ok 由 element_count 决定，**不看返回码**（本项目铁律：回读优先）",
    }


def run_analysis_report(study) -> dict[str, Any]:
    """**跑求解**并回**回读报告**。

    :returns: `{ok, return_code, return_is_trustworthy, results_present, plot_count, plot_names}`
        ★★ **`ok` 判的是 `results 非空` 且 `plot_count > 0`**，**不是**返回码 ——
        判据抄自 `tools/capture_simulation_evidence.py`：「**不是** `RunAnalysis` 的返回码，
        而是 `study.Results` 非空 + `GetPlotCount > 0`」。
    """
    return_code = run_analysis(study)
    results = None
    try:
        results = get_com_member(study, "Results")
    except Exception:                                          # noqa: BLE001
        results = None
    plot_count = None
    plot_names = None
    if results is not None:
        try:
            plot_count = int(get_com_member(results, "GetPlotCount") or 0)
        except Exception:                                      # noqa: BLE001
            plot_count = None
        try:
            plot_names = [str(x) for x in (get_com_member(results, "GetPlotNames") or ())]
        except Exception:                                      # noqa: BLE001
            plot_names = None
    return {
        "ok": results is not None and bool(plot_count),
        "return_code": int(return_code or 0),
        "return_is_trustworthy": False,
        "results_present": results is not None,
        "plot_count": plot_count,
        "plot_names": plot_names,
        "★": "ok 由 results_present + plot_count 决定，**不看返回码**",
    }

# ── 24h 计划 段 5「修地基」（Spec Kit `145`）：**网格参数生效判据** ─────────────────
# ★★★★★ 为什么加它（2026-10-01 轮 248，把"跑求解必挂"的链条**掐断在网格这一步**）：
#
#   | 方式 | 报出的 element_size | CreateMesh 后的单元数 | RunAnalysis |
#   | 既有 `tools/capture_simulation_evidence.py`（**跑通**）| **4.933908705960544** | **7310** | **1 秒 · 4 张图** |
#   | 本项目其它链                                          | **4930.501659457233** | **7250** | ★ **300 秒超时 / 无结果** |
#
#   ⇒ ★★ **两次读同一条 `default_element_size_and_tolerance(study, -1)` 却差**恰好 1000 倍**
#     （★ 原因**未查清**：`probe_document_units` 里"文档单位"那一处读不到，报 `非选择性的参数`／`-1`）。
#   ⇒ ★★★ **而 4930.5 是**不合理的**：那比零件（100 mm）大 49 倍** ——
#     单元比零件还大 ⇒ ★ **网格退化** ⇒ `CreateMesh` **静默退回默认值**（7250 ≈ 默认的 7310）
#     ⇒ ★★★★ **求解因此无解 / 卡住** ⇒ **而弹框与挂起就发生在那一步**。
#   ⇒ ★★★★★ **所以：只要在**建网格之前**判出"这个 element_size 不合理"，就**不必跑求解** ⇒
#     **挂起从源头被掐断**（★ 这与 `sw_isolate` 的进程隔离**互补**：一个防外溢，一个防发生）。
#
# ★★ 判据怎么选（★ 不发明）：★ **拿 `element_size` 与**零件自身尺寸**比** ——
#   官方建议值必然是零件尺度的一个**小分数**（本机实测：100 mm 的板 ⇒ 4.93 mm，约 **1/20**）。
#   ⇒ 取一个**宽到不可能误伤**的门槛：**单元尺寸不得大于零件的最大边**。
#     ★ 这个门槛**永远不该被合法的网格参数触到**（单元等于零件最大边 ⇒ 网格只有 1 个单元）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_simulation.py —— 本段
# 定位:   建网格前的**参数合理性判据**（24h 段 5「修地基」）。
# 官方依据: `ICWMesh.GetDefaultElementSizeAndTolerance`（本模块已记：两次实测差 1000 倍）；
#          零件尺寸取 `IBody2.GetBodyBox`（本模块/`sw_part` 已有）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面这个 `check_mesh_size_sane`
# ─────────────────────────────────────────────────────────────────────────────


# ★★★★★ 2026-10-04（接手轮）**判据②的两个系数与内存预算** —— ★ 依据逐条写在下面：
#
# 【一】官方内存规则（★ 逐字取自本机解包的 Simulation 手册）
#   文件: C:\cworks_manual\c_Analysis_Solvers.htm · C:\cworks_manual\IDC_HELP_PRESTATIC_OPTIONS.htm
#   逐字: 「FFEPlus (iterative) … For every 2,000,000 degrees of freedom, you need 1GB of RAM.」
#   ⇒ ★ 故 DOF_PER_GB = 2_000_000（★ 这是**官方给的那条换算**，不是我们拍的）✓
#
# 【二】每单元的自由度系数（★ 实测标定，不是猜）
#   依据: 本仓事实 293 的**求解进度窗**逐字 —— 「自由度: **30,456** · 节数: 11,301 ·
#         单元数: **7,250**」⇒ 30_456 / 7_250 = **4.20** ✓
#   ⚠ 这个系数**粗糙**（随单元类型 / 网格质量变），★ 故它只用来拒绝**离谱的量级**
#     （★ 实测那个事故差 ~9 个数量级 ⇒ 系数再差 2 倍也照样拦得住）✓
DOF_PER_GB = 2_000_000
DOF_PER_ELEMENT = 4.2
#: ★★ 每个节点的自由度数 = **3**（★ 三个平动）—— ★ 这是**第一性原理**，不是标定值。
#:   ★ 而在本机的实测里它是**上界**：事实 293 的「30,456 自由度 / 11,301 节点」= **2.69**
#:   （★ 因为约束把部分自由度消掉了）⇒ ★ 用 3 是**保守**（偏大）⇒ 对"内存上限"这种判据是**安全侧** ✓
DOF_PER_NODE = 3

# 【三】默认内存预算
#   ★ 为什么要有它：★ 2026-10-04 真机事故里，求解进程实际吃到 **38.5 GB / 整机 63.8 GB**
#     ⇒ 整机只剩 5.7 GB ⇒ **卡死**。★ 故默认取「物理内存的一半，且不超过 16 GB」——
#     ★ 一半：给系统与 SolidWorks 自己留余量；★ 16 GB 上限：再大的单次求解**本来就该换做法**
#     （★ 官方：模型超出物理内存时用 **Large Problem Direct Sparse**，
#      或改用对称 / 2D 简化 / 梁壳理想化 —— 见 `c_Analysis_Solvers.htm`）✓
DEFAULT_MEMORY_BUDGET_GB = 16.0


def default_solve_memory_budget_gb() -> float:
    """★ 默认的**单次求解内存预算**（GB）= min(物理内存的一半, 16)。

    ⚠ **读不到物理内存时回 `DEFAULT_MEMORY_BUDGET_GB`**（★ 不因为读不到就误拒）✓
    """
    try:
        import ctypes

        class _MemStatus(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

        st = _MemStatus()
        st.dwLength = ctypes.sizeof(_MemStatus)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
            return DEFAULT_MEMORY_BUDGET_GB
        total_gb = float(st.ullTotalPhys) / (1024.0 ** 3)
        return max(1.0, min(total_gb / 2.0, DEFAULT_MEMORY_BUDGET_GB))
    except Exception:                                          # noqa: BLE001
        return DEFAULT_MEMORY_BUDGET_GB


def mesh_settings_report(study) -> dict[str, Any]:
    """★ 读 `ICWMesh` 上**决定网格规模**的那一组设置（★ 只读，用来"改动前后"对照）。

    ★ 成因（★ 官方手册给了机制，★ 这正是"同一单元尺寸两条链差别巨大"的解释）：
      · `C:\\cworks_manual\\c_meshing_options.htm` 逐字：
        「**Curvature-based mesher** — Creates **more elements in higher-curvature areas
         automatically**, without the need for mesh control」；
      · `c_Element_Size_in_Curvature_Based_Mesher.htm` 逐字：
        「For a **curvature based** mesh, the element size is determined mathematically by the
         **minimum number of elements that fit in a hypothetical circle**」·「For this option to
         have effect, **h_min < h < h_max** where h_min and h_max are sizes from
         **Minimum element size** and **Maximum element size**」
      ⇒ ★★ **即：曲率自适应网格器会在高曲率处自动加密，而加密下界由 `MinElementSize` 定、
        **不由全局 `element_size` 定** ⇒ 只给 `element_size` 是**管不住**网格规模的** ✓
    """
    mesh = get_com_member(study, "Mesh")
    if mesh is None:
        return {"ok": False, "reason": "study 上取不到 Mesh 对象"}
    out: dict[str, Any] = {"ok": True}
    for name in ("Quality", "MesherType", "ElementSize", "MinElementSize", "MaxElementSize",
                 "ElementSizeFactorForEachLoop", "MinElementsInCircle", "NumberOfLoops",
                 "AutomaticLooping2", "ElementCount", "NodeCount"):
        try:
            out[name] = get_com_member(mesh, name)
        except Exception as exc:                               # noqa: BLE001
            out[name] = "err: %s" % (str(exc)[:60],)
    return out


def configure_mesh_settings(study, *, quality: int | None = None,
                            mesher_type: int | None = None,
                            min_element_size: float | None = None,
                            max_element_size: float | None = None,
                            element_size_factor_for_each_loop: float | None = None,
                            min_elements_in_circle: int | None = None,
                            number_of_loops: int | None = None,
                            automatic_looping: bool | None = None) -> dict[str, Any]:
    """★ **建网格之前**设那一组"决定规模"的网格设置 —— ★ 每一项都**回读核对**。

    ★★★ 为什么要有它（★ 2026-10-04 · 官方给的两条机制）：
      · ★ 缺内存时，**先降网格规模**比"换机器"便宜得多；而**降规模的旋钮是这几个**，不是
        `element_size` 一个（★ 曲率自适应会绕过它，见 `mesh_settings_report` 的引用）✓
      · ★ 取值逐字来自本机官方枚举：
        `swsMeshQuality_e` ⇒ **`Draft=0` / `High=1`**（★ 官方手册：draft「**does not have
        midside nodes**」⇒ 线性四面体 ⇒ 节点数与 DOF 都大降）；
        `swsMesherType_e` ⇒ **`Standard=0` / `Alternate=1` / `AlternateCB=2`** ✓
      ⚠ ★ **本函数不预设默认值**：★ 只设调用方**显式给的**项 ——
        ★ 免得"顺手把用户的网格偏好改成 draft"而没人知道（★ 与事实 525 的纪律同源）✓
      ⚠ ★ **代价要说清**：官方手册逐字「Use a **draft quality mesh for a quick evaluation** and
        in solid models where **bending effects are small**. Use a **high-quality mesh in most
        cases**」⇒ ★★ **draft 是"快评"用，不是通用推荐** ——
        ★ 所以本函数把它做成**显式选择**、并在返回值里带 `★_代价` ✓

    :returns: ``{ok, changed, readback, failed, ★_代价}`` —— ★ `changed` 只记**真的变了**的项，
        ★ 每项都带**回读值**（★ 不把"set 没报错"当成"设上了" —— 规则 6）。
    """
    mesh = get_com_member(study, "Mesh")
    if mesh is None:
        return {"ok": False, "reason": "study 上取不到 Mesh 对象", "changed": [], "readback": {}}
    wanted = {
        "Quality": quality, "MesherType": mesher_type,
        "MinElementSize": min_element_size, "MaxElementSize": max_element_size,
        "ElementSizeFactorForEachLoop": element_size_factor_for_each_loop,
        "MinElementsInCircle": min_elements_in_circle, "NumberOfLoops": number_of_loops,
        "AutomaticLooping2": automatic_looping,
    }
    changed, readback, failed, before = [], {}, [], {}
    for name, value in wanted.items():
        if value is None:
            continue
        try:
            before[name] = get_com_member(mesh, name)
        except Exception:                                      # noqa: BLE001
            before[name] = None
        try:
            set_com_member(mesh, name, value)
        except Exception as exc:                               # noqa: BLE001
            failed.append({"name": name, "value": value,
                           "error": "%s: %s" % (type(exc).__name__, str(exc)[:100])})
            continue
        try:
            readback[name] = get_com_member(mesh, name)
        except Exception as exc:                               # noqa: BLE001
            readback[name] = "err: %s" % (str(exc)[:60],)
        if readback.get(name) != before.get(name):
            changed.append({"name": name, "before": before.get(name), "after": readback.get(name)})
    return {
        "ok": not failed,
        "changed": changed, "readback": readback, "failed": failed, "before": before,
        "★_代价": ("★ `Quality=Draft(0)` ⇒ 线性单元（无中间节点）：★ 官方逐字"
                   "「for a quick evaluation … where bending effects are small」"
                   "⇒ **弯曲为主的问题别用 draft**；★ 换机器或换求解器更合适 ✓"),
        "★_依据": "官方 `c_meshing_options.htm` · `c_Element_Size_in_Curvature_Based_Mesher.htm` · "
                  "枚举 `swsMeshQuality_e` / `swsMesherType_e`（本机官方类型库）",
    }


#: ★★★ **网格安全档**（★ 事实 526：这是"爆内存"的**根因处置**）——
#:   ★ 官方逐字给的机制：★ 曲率自适应网格器「Creates **more elements in higher-curvature areas
#:     automatically**」，而加密下界「**Minimum element size**」**出厂是 `0.0`**（=没有下界）
#:     ⇒ ★★ **全局 `element_size` 管不住网格规模** ⇒ 圆角/边就能触发无界细化 ✓
#:   ⇒ ★ 故安全档 = **两个 `Int32` 枚举**（★ 无单位风险，★ 见 `configure_mesh_settings` 的注）：
#:     · `Quality = 0`（`swsMeshQualityDraft`）—— ★ 线性单元（无中间节点）⇒ 节点/DOF 大幅下降；
#:     · `MesherType = 0`（`swsMesherTypeStandard`）—— ★ **关掉曲率自适应**（这条才是治本的那条）✓
#:   ⚠ ★ **代价要一起给出去**（官方逐字：draft 是给「a **quick evaluation** … where **bending
#:     effects are small**」用的）⇒ ★ 弯曲为主的问题**不该**靠它蒙 ✓
MESH_SAFETY_QUALITY_DRAFT = 0
MESH_SAFETY_MESHER_STANDARD = 0
#: ★ 安全档会动的**全部**成员（★ 用来算"要不要还原" —— ★ 只碰这几个，别的一个不碰）
MESH_SAFETY_KNOBS = ("Quality", "MesherType")


def mesh_safety_apply(study, *, quality: int = MESH_SAFETY_QUALITY_DRAFT,
                      mesher_type: int = MESH_SAFETY_MESHER_STANDARD) -> dict[str, Any]:
    """★★ **建网格之前**把网格设置降到"安全档"，并回一个**可还原的凭据**。

    ★★★ 为什么（★ 事实 526 · 官方给的两条机制）：★ 出厂默认是**曲率自适应 + 加密下界 0**
      ⇒ ★ **网格规模不受全局 `element_size` 约束** ⇒ 实测见过"同一个 `element_size`，
      一条链 7250 单元/1.4 s、另一条烧到 **38.5 GB**" ✓
    ★★ 本函数与 `configure_mesh_settings` 的分工：★ 那个是**通用旋钮**（谁都能用）；
      本函数是**安全档 + 还原凭据**（★ 给"我要跑一次别爆就行"的人）✓
    ★ 判据：★ `before` 逐项记原值 ⇒ ★ 交给 `mesh_safety_restore` 就能**一字不差地还回去**
      （★ 与事实 525 的偏好守卫**同一套纪律**：★ **改动可见 + 可还原**）✓

    :returns: ``{ok, before, applied, changed, readback, failed, token, ★_代价}``
        ★ `token` **必须**原样交给 `mesh_safety_restore`（★ 里面是改动前的原值）。
    """
    before = mesh_settings_report(study)
    if not before.get("ok"):
        return {"ok": False, "reason": before.get("reason") or "读不到 Mesh 对象",
                "before": before, "applied": None, "changed": []}
    knobs: dict[str, Any] = {}
    if quality is not None:
        knobs["quality"] = int(quality)
    if mesher_type is not None:
        knobs["mesher_type"] = int(mesher_type)
    applied = configure_mesh_settings(study, **knobs)
    token = {k: before.get(k) for k in MESH_SAFETY_KNOBS}
    return {
        "ok": bool(applied.get("ok")),
        "before": {k: before.get(k) for k in MESH_SAFETY_KNOBS},
        "applied": knobs,
        "changed": applied.get("changed") or [],
        "readback": applied.get("readback") or {},
        "failed": applied.get("failed") or [],
        "token": token,
        "★_代价": applied.get("★_代价"),
        "★_依据": applied.get("★_依据"),
    }


def mesh_safety_restore(study, token: dict[str, Any] | None) -> dict[str, Any]:
    """★ 把 `mesh_safety_apply` 改过的网格设置**还回去**（★ 事实 526/525 的同一套纪律）。

    ★ 判据：★ **原值是 `None`/读不到的项不写回**（★ 免得把"读不到"变成"写了个错的旧值"）；
      ★ 写回后**逐项读回校验**并给 `match` ⇒ ★ 不把"设了"当成"还原了" ✓
    """
    if not token:
        return {"ok": False, "reason": "没有 token ⇒ 不猜该还原成什么（★ 不写）", "restored": []}
    knobs: dict[str, Any] = {}
    mapping = {"Quality": "quality", "MesherType": "mesher_type"}
    skipped: list[dict[str, Any]] = []
    for name, arg in mapping.items():
        old = token.get(name)
        if old is None:
            skipped.append({"name": name, "why": "★ 原值读不到 ⇒ 不写回（免得写错）"})
            continue
        knobs[arg] = int(old)
    if not knobs:
        return {"ok": False, "reason": "token 里所有原值都读不到 ⇒ 一个字都不写",
                "restored": [], "skipped": skipped}
    back = configure_mesh_settings(study, **knobs)
    return {"ok": bool(back.get("ok")), "restored": back.get("changed") or [],
            "readback": back.get("readback") or {}, "failed": back.get("failed") or [],
            "skipped": skipped}


def create_mesh_safely(study, *, model=None, units: int = 0, element_size: float = 0.0,
                       tolerance: float = 0.0, memory_budget_gb: float | None = None,
                       quality: int = MESH_SAFETY_QUALITY_DRAFT,
                       mesher_type: int = MESH_SAFETY_MESHER_STANDARD,
                       keep_profile: bool = False) -> dict[str, Any]:
    """★★★★★ **建网格的唯一推荐入口** —— 一次调用把"别把机器算爆 / 别把会话卡死"整套做完。

    ★★★ 它按顺序做**七件事**（★ 每一步都留读数，★ 任一步不成立就**停下并如实说为什么**）：
      ① ★ **量预算前置闸**：`check_mesh_size_sane`（★ 单元尺寸 > 零件最大边 ⇒ 直接拒）；
      ② ★ **网格安全档**：`mesh_safety_apply`（★ 关掉**曲率自适应** + 转 **Draft** ——
         ★★ 这是"爆内存"的**根因处置**，事实 526：★ 曲率自适应会在高曲率处**无界加密**，
         而加密下界出厂是 `0`）✓
      ③ 建网格（`create_mesh_report`）；
      ④ ★ **读真实读数**：`ElementCount` / **`NodeCount`**（★ 后者才是 DOF 的第一性来源）；
      ⑤ ★ **求解前内存闸**：`solve_memory_preflight`（★ 优先用节点数 ⇒ `DOF≈3×节点`）——
         ★ 它不过就**不进求解**（★ 官方：内存不够会走 out-of-core、极慢）；
      ⑥ ★ **还原网格设置**（★ 除非 `keep_profile=True`）—— ★ 与事实 525 的偏好守卫**同一套纪律**：
         ★ **改动可见 + 用完还回去** ✓
      ⑦ 回一份**可入证据**的报告（★ 含每一项的读数与拒因）。

    :param model: ★★★ **零件文档**（可选，但**强烈建议给**）—— ★ 量预算前置闸要用它读包围盒。
        ⚠★ **第一版在这里犯过一个真错**（2026-10-04 真机跑出来的）：★ 我把 **`study`** 传给了
        `check_mesh_size_sane(model, …)` ⇒ ★ 那道闸在**错误的对象**上取包围盒 ⇒
        ★★ **它静默失效**（内部 `except` 把 `AttributeError` 收成"判据自身出错、不因此阻断"）
        ⇒ ★ 于是"量预算前置闸"**看起来在跑、实际没判**（★ 事实 40 的老毛病：**存在但没生效的守卫**）✓
        ⇒ ★ 现在：★ 给了 `model` 才判；★ **没给就把"跳过"如实记进 `size_gate`**（★ 不假装判过）✓
    :param keep_profile: ★ `True` ⇒ **保留**安全档（★ 调用方明确要"以后都这样"时才用）。
    :returns: ``{ok, blocked?, size_gate, safety, mesh, node_count, preflight, restored, ★_结论}``
    """
    out: dict[str, Any] = {"ok": False, "units": int(units), "element_size": float(element_size),
                           "tolerance": float(tolerance),
                           "★": "建网格的唯一推荐入口（①量闸 ②安全档 ③建网格 ④真读数 ⑤内存闸 ⑥还原）"}
    #: ① 量预算前置闸（★ **必须用零件文档** —— ★ 传 study 会让它静默失效，见 docstring）
    if model is None:
        size_gate: dict[str, Any] = {"ok": None, "skipped": True,
                                     "reason": "★ 调用方没给 `model` ⇒ **这一闸跳过**"
                                               "（★ 如实记，不假装判过；★ 后面的求解前内存闸仍在）"}
    else:
        size_gate = check_mesh_size_sane(model, float(element_size),
                                        memory_budget_gb=memory_budget_gb)
    out["size_gate"] = size_gate
    if size_gate.get("ok") is False:
        out["blocked"] = "MESH_SIZE_UNSANE"
        out["reason"] = "量预算前置闸不放行 ⇒ **不建网格**：%s" % size_gate.get("reason")
        return out
    #: ② 安全档（★ 记原值，供 ⑥ 还原）
    safety = mesh_safety_apply(study, quality=quality, mesher_type=mesher_type)
    out["safety"] = safety
    if not safety.get("ok"):
        out["blocked"] = "MESH_SAFETY_APPLY_FAILED"
        out["reason"] = "网格安全档没设上 ⇒ **不建网格**（★ 不拿无界加密去赌）：%r" % (safety.get("failed"),)
        return out
    try:
        #: ③ 建网格
        try:
            mesh = create_mesh_report(study, units=int(units), element_size=float(element_size),
                                      tolerance=float(tolerance))
        except Exception as exc:                               # noqa: BLE001
            #: ★ 能力层抛错 ⇒ **如实记**（★ 不吞、也不让"还原"被跳过 —— 见 finally）
            mesh = {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:200]),
                    "★": "★ 建网格那一步抛了异常（★ 如实记，★ 不吞）"}
            out["mesh_exception"] = mesh["error"]
        out["mesh"] = mesh
        #: ④ 真实读数（★ `NodeCount` 是 DOF 的第一性来源）
        settings = mesh_settings_report(study)
        out["after_settings"] = settings
        node_count = int(settings.get("NodeCount") or 0) or None
        out["node_count"] = node_count
        out["element_count"] = int(mesh.get("element_count") or 0)
        #: ⑤ 求解前内存闸
        pre = solve_memory_preflight(out["element_count"], node_count=node_count,
                                     memory_budget_gb=memory_budget_gb)
        out["preflight"] = pre
        out["ok"] = bool(mesh.get("ok")) and bool(pre.get("ok"))
        if not pre.get("ok"):
            out["blocked"] = "SOLVE_MEMORY_BUDGET"
            out["reason"] = ("网格建成了，但**求解前内存闸不放行** ⇒ 别跑求解：%s"
                             % pre.get("reason"))
        elif not mesh.get("ok"):
            out["blocked"] = "MESH_FAILED"
            out["reason"] = "网格没建成：%r" % (mesh.get("error") or mesh.get("return_code"),)
        out["★_结论"] = ("★ 网格读数：单元 %s · 节点 %s ⇒ 估求解内存 %.4g GB（预算 %.1f GB）"
                         % (out["element_count"], node_count,
                            pre.get("est_ram_gb") or 0.0, pre.get("memory_budget_gb") or 0.0))
    finally:
        #: ⑥ 还原（★ `finally` ⇒ **连建网格抛异常也还** —— ★ 与事实 525 同纪律）
        if not keep_profile:
            out["restored"] = mesh_safety_restore(study, safety.get("token"))
        else:
            out["restored"] = {"ok": True, "★": "keep_profile=True ⇒ 按调用方要求**保留**安全档"}
    return out


#: ★★ `swsSolverType_e` —— ★ 出处：本仓 `_raw` 的 cosworks 枚举页 + `STUDY_OPTION_SETTERS`
#:   （★ 逐条核过：Automatic=0 · DirectSparse=1 · **FFEPlus=2** · CASI=5 · Abaqus=6 ·
#:    INTEL=7 · INTELCluster=8）✓
#: enum-gate: enum swsSolverType_e
SWS_SOLVER_TYPES = {
    "automatic": 0, "direct_sparse": 1, "ffeplus": 2, "casi": 5,
    "abaqus": 6, "intel": 7, "intel_cluster": 8,
}
_SOLVER_NAME_BY_VALUE = {v: k for k, v in SWS_SOLVER_TYPES.items()}


def static_solver_type_report(study) -> dict[str, Any]:
    """★ 读**本研究当前用的求解器**（`ICWStaticStudyOptions.SolverType`）—— ★ 只读。

    ★★★ 为什么要它（★ 2026-10-04 · 我自己刚留下的一个正确性漏洞）：
      · ★ `solve_memory_preflight` 用的那条换算「**每 2,000,000 自由度 1 GB RAM**」
        **逐字出自 FFEPlus 那一页**（`c_Analysis_Solvers.htm`）✓
      · ★★ 而真机那次成功的求解，进度窗上写的是 **`类型: Intel Direct Sparse`** ⇒
        ★ **不是 FFEPlus** ⇒ ★★ **那条换算对直接法不能当同一把尺子** ✓
      ⇒ ★ 所以要把"本研究用的是哪个求解器"**读出来并如实带进估计结果**，
        ★ 而不是让调用方以为那条规则普适 ✓
    ⚠ ★ `SolverType` 在 `STUDY_OPTION_SETTERS` 里是 **setter** ⇒ ★ **它能不能读**未在本仓验证 ⇒
      ★ 读不到就回 `{"ok": False, "reason": ...}`（★ **不猜、也不默认成 FFEPlus**）✓
    """
    out: dict[str, Any] = {"ok": False, "value": None, "name": None, "reason": ""}
    try:
        from .sw_simulation_study_options import study_options_of
    except ImportError:
        from sw_simulation_study_options import study_options_of

    try:
        options = study_options_of(study, "ICWStaticStudyOptions")
    except Exception as exc:                                   # noqa: BLE001
        out["reason"] = "取不到 ICWStaticStudyOptions：%s: %s" % (type(exc).__name__, str(exc)[:120])
        return out
    if options is None:
        out["reason"] = "ICWStaticStudyOptions 为 None（该研究可能不是静力族）"
        return out
    try:
        value = get_com_member(options, "SolverType")
    except Exception as exc:                                   # noqa: BLE001
        out["reason"] = ("读 SolverType 失败（★ 它在本仓只以 **setter** 记过、getter 未验证）："
                         "%s: %s" % (type(exc).__name__, str(exc)[:100]))
        return out
    out.update({"ok": True, "value": value,
                "name": _SOLVER_NAME_BY_VALUE.get(value, "unknown(%r)" % (value,))})
    return out


def solve_memory_preflight(element_count: int, *, node_count: int | None = None,
                           memory_budget_gb: float | None = None,
                           solver_name: str | None = None) -> dict[str, Any]:
    """★ **建完网格、跑求解之前**再判一次 —— ★★ 有 `NodeCount` 时用**真节点数**算，最准。

    ★★★ 为什么要有**第二道**（第一道是 `check_mesh_size_sane`）：
      · 第一道只能按**包围盒体积 ÷ 单元尺寸³** 估单元数 ⇒ ★ 对**非长方体**会高估、
        对**曲率自适应加密**会**严重低估** ⇒ ★ 它够用来拒"离谱"，**不够用来决定"跑不跑"**；
      · ★★ 而建完网格后 `ICWMesh.ElementCount` / `ICWMesh.NodeCount` 都是**真实读数** ✓
    ★★★ **自由度怎么算**（★ 两档，★ 优先用节点数 —— ★ 那是**第一性原理**）：
      · 有 `node_count` ⇒ **DOF ≈ 3 × 节点数**（★ 每个节点 3 个平动自由度）；
      · 否则回落到 **DOF ≈ 4.2 × 单元数**（★ 本仓实测标定：事实 293 的 30,456 / 7,250 = 4.20）。
      ★ 两者在**同一台真机**上互相印证：30,456 自由度 / 11,301 节点 = **2.69** ⇒ ★ 3× 是它的上界 ✓
    内存换算仍是官方那条：**每 2,000,000 自由度 1 GB RAM**（见 `DOF_PER_GB` 上方注释）。

    :param element_count: `ICWMesh.ElementCount` 的回读值。
    :param node_count: `ICWMesh.NodeCount` 的回读值（★ 给了就用它算，更准）。
    :param memory_budget_gb: 内存上限（GB）；★ `None` ⇒ `default_solve_memory_budget_gb()`。
    :returns: ``{ok, element_count, node_count, est_dof, est_ram_gb, memory_budget_gb, reason}``
        ★ **`ok=False` ⇒ 不要跑求解**（★ 官方：内存不够会走 out-of-core，**极慢**）。
    """
    n = int(element_count or 0)
    nodes = int(node_count) if node_count else 0
    out: dict[str, Any] = {"element_count": n, "node_count": nodes or None, "ok": True,
                           "reason": "",
                           "★": "跑求解前的第二道闸（★ 优先用**真节点数**；★ DOF≈3×节点数）"}
    if nodes > 0:
        est_dof = nodes * DOF_PER_NODE
        basis = "3 × 节点数（★ 第一性原理：每节点 3 个平动自由度）"
    elif n > 0:
        est_dof = n * DOF_PER_ELEMENT
        basis = "4.2 × 单元数（★ 事实 293 实测标定）"
    else:
        out.update({"ok": False,
                    "reason": "element_count 与 node_count 都不是正整数（%r / %r）⇒ 网格没建成"
                              % (element_count, node_count)})
        return out
    est_ram_gb = est_dof / DOF_PER_GB
    budget = (float(memory_budget_gb) if memory_budget_gb is not None
              else default_solve_memory_budget_gb())
    out.update({"est_dof": est_dof, "est_ram_gb": est_ram_gb, "memory_budget_gb": budget,
                "★_算式": basis + " · RAM ≈ DOF / 2,000,000 GB（★ 官方 FFEPlus 规则）"})
    #: ★★★★ 2026-10-04 **把那条换算是"哪把尺子"说清楚**（★ 我自己刚留下的漏洞）：
    #:   · ★ 它**逐字出自 FFEPlus 那一页**（`c_Analysis_Solvers.htm`）✓
    #:   · ★★ 而真机那次**成功**的求解，求解器写的是 **`Intel Direct Sparse`** ⇒
    #:     ★ **不是 FFEPlus** ⇒ ★★ 直接法的内存在本仓**没有官方规则**（★ 铁律 5：查不到就说查不到）✓
    #:   ⇒ ★ 于是结果里**必须**带一句"这条换算对谁成立"，★ 免得后人当通用尺子用 ✓
    #: ⚠ ★ **不要写 `solver_name or ""`** —— ★ `SolverType = 0`（`automatic`）是**合法值**，
    #:   而 `0 or ""` ⇒ `""` ⇒ 被判成"未告知"（★ 由我自己的负例当场抓出）✓
    _s = ("" if solver_name is None else str(solver_name)).strip().lower()
    #: ⚠ ★ 按**子串**匹配，不按精确名 —— ★ 真机上那个名字是 **`Intel Direct Sparse`**（★ 带空格的组合名），
    #:   而第一版按精确等值比 ⇒ ★ **它落进了 else 分支**（★ 由我自己当场发现的）✓
    _is_direct = any(tok in _s for tok in ("direct", "intel", "sparse"))
    _is_ffe = ("ffe" in _s) or ("plus" in _s)
    if not _s:
        out["★_适用性"] = ("⚠ ★ 求解器**未告知** ⇒ 这条换算的适用性未定（★ 它出自 **FFEPlus** 官方页；"
                           "★ 直接法如 `Intel Direct Sparse` 的内存在本仓**无官方规则**）")
    elif "automatic" in _s or _s == "0":
        #: ★★ 真机实测（2026-10-04）：`SolverType = 0 (automatic)` **而求解器自己**选的是
        #:   `Intel Direct Sparse`（进度窗逐字）⇒ ★ 对 `automatic` 这条 FFEPlus 尺子**更不适用** ✓
        out["★_适用性"] = ("⚠⚠ 求解器 = `Automatic` ⇒ ★ **由 SolidWorks 自选** —— ★ 真机实测它选的是 "
                           "**`Intel Direct Sparse`**（★ 直接法）⇒ ★ **别用 FFEPlus 的换算**"
                           "（★ 想确定用哪个，就在进度窗上看 `类型:` 那一行）✓")
    elif _is_ffe:
        out["★_适用性"] = "★ 求解器 = `%s` ⇒ **这条换算正适用**（★ 它就是 FFEPlus 的规则）✓" % (solver_name,)
    elif _is_direct:
        out["★_适用性"] = ("⚠⚠ 求解器 = `%s`（**直接法**）⇒ ★ **别拿 FFEPlus 的换算当同一把尺子** —— "
                           "★ 直接法的内存随**带宽/填充**走、与自由度**不成那条比例**，"
                           "而本仓**没有**直接法的官方换算（★ 铁律 5）⇒ ★ 本条只能当**下界参考** ✓"
                           % (solver_name,))
    else:
        out["★_适用性"] = ("⚠ 求解器 = `%s` ⇒ ★ 该换算出自 **FFEPlus**、对本求解器**适用性未查证** ✓"
                           % (solver_name,))
    if est_ram_gb > budget:
        out.update({
            "ok": False,
            "reason": ("%s ⇒ 估 %.3g 自由度 ⇒ 预估求解内存 **%.2f GB** > 预算 %.1f GB"
                       "（★ 官方规则：每 2,000,000 自由度需 1 GB RAM）"
                       " ⇒ **别跑** —— 官方向导：内存不够会走 out-of-core、"
                       "「the solution progress can be extremely slow」"
                       % (basis, est_dof, est_ram_gb, budget)),
        })
    return out


def check_mesh_size_sane(model, element_size: float, *,
                         memory_budget_gb: float | None = None) -> dict[str, Any]:
    """★ **建网格之前**判一次：给定的单元尺寸对**这个零件**是否合理 —— ★★ **两侧都判**。

    ★★★ 这是把"跑求解必挂 / 把机器打爆"**掐断在源头**的那道闸。

    **判据 ①（原有 · 太大方向）**：`element_size` 若**大于零件的最大边**，网格必然退化、
    `CreateMesh` 会**静默退回默认值**，而随后的 `RunAnalysis` **无解 ⇒ 弹模态框 ⇒ 挂住会话**。

    **判据 ②（★ 2026-10-04 新加 · 太小方向）**：`element_size` 若**小得离谱**，
    网格单元数会爆炸 ⇒ **求解器把内存吃光**。★ 真机事故（本轮实录）：
    一个 100×60×20 mm 的板被喂进 **0.0049（把"米"当"毫米"）** ⇒ 单元数按包围盒估 ≈ 1e12
    ⇒ 求解进程 `cwbcbfmesh.exe` 实际吃到 **38.5 GB 工作集 / 52.6 GB 提交**
    （整机 63.8 GB，剩余 5.7 GB）⇒ **整机卡死、程序无响应**。

    ★★★★ **判据②的公式不是发明的，两个系数各有官方/实测出处**：
      · **每 2,000,000 自由度 1 GB RAM** —— ★ 官方逐字（FFEPlus 求解器）：
        `C:\\cworks_manual\\c_Analysis_Solvers.htm` 与 `IDC_HELP_PRESTATIC_OPTIONS.htm`
        「For every 2,000,000 degrees of freedom, you need 1GB of RAM.」✓
      · **每单元 4.2 个自由度** —— ★ 本仓实测（事实 293 的求解进度窗逐字）：
        「自由度: **30,456** · 单元数: **7,250**」⇒ 30456 / 7250 = **4.20** ✓
      · 单元数按 **包围盒体积 / element_size³** 估（★ 粗糙，但**只用于拒绝"离谱"的量级**）✓

    :param model: 活动文档（用来量零件包围盒）。
    :param element_size: 打算传给 ``CreateMesh`` 的单元尺寸（★ 单位口径见 `create_mesh` 的 docstring）。
    :param memory_budget_gb: ★ 允许这次求解用掉的内存上限（GB）；★ `None` ⇒ 用默认
        （见 `default_solve_memory_budget_gb`：**物理内存的一半，且不超过 16 GB**）。
    :returns: ``{ok, element_size, max_dim, volume_mm3, est_elements, est_dof, est_ram_gb,
        memory_budget_gb, reason}`` —— ★ **`ok=False` 时调用方应当停下**
        （不要建网格、更不要跑求解）。
    """
    out: dict[str, Any] = {"element_size": float(element_size), "max_dim": None,
                           "ok": True, "reason": "",
                           "★": "建网格前的**双侧**合理性判据（★ 太大=网格退化；★ 太小=内存打爆）"}
    if not (float(element_size) > 0.0):
        out.update({"ok": False, "reason": "element_size 不是正数（%r）" % element_size})
        return out
    try:
        size = None
        try:
            import sw_part

            bb = sw_part.get_bounding_box(model)
            size = (bb or {}).get("size")
        except Exception:                                      # noqa: BLE001
            size = None
        if not size:
            out.update({"reason": "量不到零件包围盒 ⇒ **只记不判**（★ 不因为没有参照就误报）"})
            return out
        max_dim = max(float(x) for x in size)
        out["max_dim"] = max_dim
        #: ★ 判据 ①（原有）：太大 ⇒ 网格退化
        if float(element_size) > max_dim:
            out.update({
                "ok": False,
                "reason": ("单元尺寸 %.4f 大于零件最大边 %.4f ⇒ **网格必然退化**"
                           "（CreateMesh 会静默退回默认值，随后 RunAnalysis 无解 ⇒ 弹模态框 ⇒ 挂住会话）"
                           % (float(element_size), max_dim)),
            })
            return out
        #: ★ 判据 ②（★ 新）：太小 ⇒ 单元数爆炸 ⇒ 求解吃光内存
        volume = 1.0
        for x in size:
            volume *= max(float(x), 0.0)
        if volume <= 0.0:
            out.update({"reason": "包围盒体积算不出（%r）⇒ **只记不判**" % (size,)})
            return out
        est_elements = volume / (float(element_size) ** 3)
        est_dof = est_elements * DOF_PER_ELEMENT
        est_ram_gb = est_dof / DOF_PER_GB
        budget = (float(memory_budget_gb) if memory_budget_gb is not None
                  else default_solve_memory_budget_gb())
        out.update({"volume_mm3": round(volume, 4),
                    "est_elements": est_elements, "est_dof": est_dof,
                    "est_ram_gb": est_ram_gb, "memory_budget_gb": budget,
                    "★_公式": "单元数≈包围盒体积/单元尺寸³ · DOF≈4.2×单元数（事实 293 实测）· "
                              "RAM≈DOF/2,000,000 GB（官方 FFEPlus 规则）"})
        if est_ram_gb > budget:
            out.update({
                "ok": False,
                "reason": ("单元尺寸 %.6f 太小 ⇒ 按包围盒估 **%.3g 个单元 / %.3g 自由度**"
                           " ⇒ 预估求解内存 **%.1f GB** > 预算 %.1f GB"
                           "（★ 官方规则：每 2,000,000 自由度需 1 GB RAM）"
                           " ⇒ **会把内存吃光 / 走 out-of-core 而极慢**"
                           % (float(element_size), est_elements, est_dof, est_ram_gb, budget)),
            })
        return out
    except Exception as exc:                                   # noqa: BLE001
        out.update({"reason": "判据自身出错（★ 不因此阻断）：%s: %s"
                              % (type(exc).__name__, str(exc)[:120])})
        return out
