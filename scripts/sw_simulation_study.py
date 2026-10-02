"""SolidWorks Simulation 研究管理与求解：ICWStudyManager / ICWStudy 封装。

能力域
    域 13 · 仿真（需许可证）

本模块与既有模块的分工
----------------------
``scripts/sw_simulation.py``      addin 入口 + 研究创建 + 夹具/力 + 网格 + 求解的**骨架**
``scripts/sw_simulation_loads.py`` 载荷夹具的 24 个 Add* 方法（本模块的兄弟）
``scripts/sw_simulation_study.py``（本文件）**研究管理器的全量方法** +
                                研究对象的网格/求解/导出/结果入口

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt
      —— 对 SolidWorks.Interop.cosworks.dll 的**纯元数据反射**，
         属 AGENTS.md §四.1③「读官方程序集，不是实测」。
    D:\\AI\\SW\\_raw\\reflect\\enum_cosworks.txt
      —— 枚举取值（363 个枚举全量反射所得）。

⚠ 官方 CHM 的 cosworks 册**没有** ICWStudyManager / ICWStudy 的接口页
  （该册只覆盖 ICWLoadsAndRestraintsManager 一个族），所以本模块的签名
  **只能**来自反射。这一点必须写明，否则下游会误以为同样有语义文档可查。

⚑ 本模块是对三个 MIT 项目的**交叉核对结果**，不照抄它们
--------------------------------------------------------------------
本地 3 个 MIT 项目里 `vespo92/SolidworksMCP-TS`（src/tools/vba-advanced.ts）
有一份 Simulation 的 VBA 生成器。逐条核对反射签名后，**它有 6 处与官方不符**，
故本模块**不移植其代码**，只把它当作「独立第三方实现存在」的佐证：

| 它的写法 | 官方反射/枚举 | 判定 |
|---|---|---|
| `swStudy.AddRestraint(type, SelectionManager)` | 该成员**不在 ICWStudy 上**；`AddRestraint` 只在 `ICWLoadsAndRestraintsManager`，**4 参** | ❌ 成员不存在 |
| `swStudy.AddLoad(type, selMgr)` | `AddLoad` 在**整个 cosworks 程序集里都不存在** | ❌ 成员不存在 |
| `swStudy.GetMaterial(name)` | 同上，不存在 | ❌ 成员不存在 |
| `swStudy.ApplyMaterial(mat)` | 同上，不存在 | ❌ 成员不存在 |
| 夹具 `roller = 1` | `swsRestraintTypeRoller = 3`（1 是 Immovable） | ❌ 枚举错 |
| 研究类型 `nonlinear = 4` | `swsAnalysisStudyTypeNonlinear = 5`（4 是 Optimization） | ❌ 枚举错 |

⇒ **直接照抄 MIT 项目会把这些错误带进来**。本模块一律用反射值。
   （该项目的 `CreateNewStudy3(name, type, 0, errCode)` 四参形态是对的，已采用。）

⚠ `RunAnalysis()` / `MeshAndRun()` / `UpdateAllComponents()` /
  `ActivateConfiguration()` 官方反射确认是**零参**方法 —— 加括号传参会 TypeError。
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
# 文件:   scripts/sw_simulation_study.py —— 本文件自身
# 定位:   模块导出清单、枚举表与签名表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的
#         来源块（逐接口的反射签名）。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "SWS_ANALYSIS_STUDY_TYPES",
    "SWS_MESH_TYPES",
    "SWS_RUN_ANALYSIS_ERRORS",
    "STUDY_MANAGER_ARITY",
    "STUDY_ARITY",
    "create_study",
    "create_study_v2",
    "create_study_v3",
    "get_study",
    "delete_study",
    "duplicate_study",
    "rename_study",
    "convert_study",
    "set_active_study",
    "run_analysis",
    "mesh_and_run",
    "create_mesh",
    "create_mesh_for_control",
    "get_study_manager_of",
    "get_loads_manager_of",
    "get_results_of",
    "export_study",
    "generate_report",
    "collect_study_evidence",
]


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举（对 interop 程序集纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\enum_cosworks.txt
# 定位:   研究类型 / 网格类型 / 求解错误码。取值逐个反射核出。
# ⚑ 与 MIT 项目的差异已写进模块头：本地 vespo92/SolidworksMCP-TS 把
#   nonlinear 映射成 4、roller 映射成 1，两者都与反射值不符。
# 取值:   下面两张表**全量照录**官方反射所得（未收录的项不臆造）。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
SWS_ANALYSIS_STUDY_TYPES = {
    "static": 0,            # swsAnalysisStudyTypeStatic
    "frequency": 1,         # swsAnalysisStudyTypeFrequency
    "buckling": 2,          # swsAnalysisStudyTypeBuckling
    "thermal": 3,           # swsAnalysisStudyTypeThermal
    "optimization": 4,      # swsAnalysisStudyTypeOptimization
    "nonlinear": 5,         # swsAnalysisStudyTypeNonlinear
    "drop_test": 6,         # swsAnalysisStudyTypeDropTest
    "fatigue": 7,           # swsAnalysisStudyTypeFatigue
    "dynamic": 8,           # swsAnalysisStudyTypeDynamic
    "pressure_vessel": 9,   # swsAnalysisStudyTypePressureVessel
    "topology_static": 13,  # swsAnalysisStudyTypeTopology_Static
    # 10 / 11 / 12 在官方枚举里是 Reserved1~3，刻意不收录
}

SWS_MESH_TYPES = {
    "solid": 0,             # swsMeshTypeSolid
    "mid_surface": 1,       # swsMeshTypeMidSurface
    "surfaces": 2,          # swsMeshTypeSurfaces
    "mixed": 3,             # swsMeshTypeMixed
    "beam": 4,              # swsMeshTypeBeam
}

SWS_RUN_ANALYSIS_ERRORS = {
    "successful": 0,            # swsRunAnalysisErrorSuccessful
    "use_high_quality_mesh": 1, # swsRunAnalysisErrorUseHighQualityMesh
    "define_rigid_virtual_wall_contact": 2,
    "define_initial_temperature": 3,
    "multiple_loads_use_same_time_curve": 4,
    "set_up_drop_test_study": 5,
    "need_one_or_more_static_studies": 6,
    "no_fatigue_event": 7,
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（对 interop 程序集纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
#           → ICWStudyManager 段 + ICWStudy 段
# 定位:   本模块全部封装的**官方实参个数**，逐条照抄反射清单。
#         表里**不含**末位 ByRef Int32 的 ErrorCode
#         （pywin32 迟到绑定传 0 占位，见模块头）。
# ⚠ 这张表就是 A3（签名比对）的可执行依据：
#   tests/test_sw_simulation_study_contract.py 会拿它与源码里的调用点逐项对账。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
STUDY_MANAGER_ARITY: dict[str, int] = {
    "CreateNewStudy": 3,
    "CreateNewStudy2": 2,
    "CreateNewStudy3": 3,
    "GetStudy": 1,
    "DeleteStudy": 1,
    "DuplicateStudy": 4,
    "DuplicateStudy2": 6,
    "ConvertStudy": 6,
    "ConvertStudy2": 8,
    "RenameStudyFromID": 2,
    "RenameStudyFromName": 2,
    "RunAllStudies": 0,
    "RunSpecifiedStudyByName": 0,
    "SetDistributedSimulation": 1,
    "ManageDistributedSimulation": 2,
}

STUDY_ARITY: dict[str, int] = {
    "RunAnalysis": 0,
    "MeshAndRun": 0,
    "CreateMesh": 3,
    "CreateMeshForMeshControl": 1,
    "UpdateAllComponents": 0,
    "ActivateConfiguration": 0,
    "CopyMeshFromStudy": 1,
    "CreateAnalysisDatabase": 1,
    "ConnectAnalysisDatabase": 1,
    "ExportSimulationStudy": 7,
    "GenerateReport": 3,
    "GetMassPropertiesManager": 0,
    "SetNonLinearStudyOptions": 1,
    "SetFatigueResultOptions": 2,
    "SetResultCombinationSetup": 4,
    "SetClusterComputers": 1,
}


def _checked(table: dict[str, int], target, member: str, *args):
    """按签名表校核实参个数，通过后才发起调用（开发期护栏）。"""
    expected = table.get(member)
    if expected is not None and expected != len(args):
        raise ValueError(
            f"{member} 官方签名是 {expected} 个实参（不含末尾 by-ref ErrorCode），"
            f"本次调用给了 {len(args)} 个"
        )
    if target is None:
        raise ValueError("目标对象为 None")
    return get_com_member(target, member, *args)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks/cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt → ICWStudyManager 段
# 定位:   研究创建/取用/改名/转换。官方签名逐条照抄：
#     CWStudy CreateNewStudy (String Name, Int32 Type, Int32 ConfigOpt,
#                            Int32& ErrorCode)                            → 3 + err
#     CWStudy CreateNewStudy2(String Name, Int32 Type, Int32& ErrorCode)   → 2 + err
#     CWStudy CreateNewStudy3(String Name, Int32 Type, Int32 ConfigOpt,
#                            Int32& ErrorCode)                            → 3 + err
#     CWStudy GetStudy(Int32 Id)                                            → 1
#     Void   DeleteStudy(String Name)                                       → 1
#     CWStudy DuplicateStudy(String, String, String, Int32, Int32&)         → 4 + err
#     CWStudy DuplicateStudy2(String,String,String,Int32,Boolean,Boolean,
#                             Int32&)                                      → 6 + err
#     CWStudy ConvertStudy(String, Int32, String, Int32, String, Int32,
#                          Int32&)                                         → 6 + err
#     Int32   RenameStudyFromID(Int32 Id, String NewName)                   → 2
#     Int32   RenameStudyFromName(String Old, String New)                   → 2
#     Void    set_ActiveStudy(Int32)                                        ← **属性**
# ⚑ CreateNewStudy3 的 4 参形态与本地 vespo92/SolidworksMCP-TS 的
#   `CreateNewStudy3(name, type, 0, errCode)` 一致 —— 该项目此处是对的，已采用。
# ⚠ 本接口无官方文档页，语义只能靠反射 + 参数名（见上）。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_study(manager, name: str, study_type: int, config_option: int = 0):
    """建研究。``study_type`` 见 SWS_ANALYSIS_STUDY_TYPES。"""
    return _checked(STUDY_MANAGER_ARITY, manager, "CreateNewStudy",
                    str(name), int(study_type), int(config_option))


def create_study_v2(manager, name: str, study_type: int):
    """建研究（2 参版，不带 ConfigOpt）。"""
    return _checked(STUDY_MANAGER_ARITY, manager, "CreateNewStudy2",
                    str(name), int(study_type))


def create_study_v3(manager, name: str, study_type: int, config_option: int = 0):
    """建研究（3 参版，与 CreateNewStudy 同形）。"""
    return _checked(STUDY_MANAGER_ARITY, manager, "CreateNewStudy3",
                    str(name), int(study_type), int(config_option))


def get_study(manager, study_id: int):
    """按序号取研究。"""
    return _checked(STUDY_MANAGER_ARITY, manager, "GetStudy", int(study_id))


def delete_study(manager, name: str) -> bool:
    """按名删除研究。"""
    _checked(STUDY_MANAGER_ARITY, manager, "DeleteStudy", str(name))
    return True


def duplicate_study(manager, source: str, target: str, config_name: str,
                    options: int):
    """复制研究。"""
    return _checked(STUDY_MANAGER_ARITY, manager, "DuplicateStudy",
                    str(source), str(target), str(config_name), int(options))


def rename_study(manager, old_name: str, new_name: str) -> int:
    """按名改研究名。"""
    return _checked(STUDY_MANAGER_ARITY, manager, "RenameStudyFromName",
                    str(old_name), str(new_name))


def convert_study(manager, source: str, target_type: int, target_name: str,
                  options: int, config_name: str, extra: int):
    """转换研究类型。"""
    return _checked(STUDY_MANAGER_ARITY, manager, "ConvertStudy",
                    str(source), int(target_type), str(target_name),
                    int(options), str(config_name), int(extra))


def set_active_study(manager, study_id: int) -> bool:
    """设当前激活研究。

    ⚑ 官方反射是 ``set_ActiveStudy(Int32)`` —— **属性**，不是方法。
      迟到绑定下 ``manager.ActiveStudy(id)`` 会 TypeError。
    """
    if manager is None:
        raise ValueError("manager 为 None")
    get_com_member(manager, "ActiveStudy", int(study_id))
    return True


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
#         + SolidWorks Simulation **VB6 类型库 CHM**（补参数名，见下）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt → ICWStudy 段
#         C:\cworks_vb6\CosmosWorksLib~CWStudy~CreateMesh.html
# 定位:   求解与网格。官方签名逐条照抄：
#     Int32 RunAnalysis()                      ← **零参**（AGENTS.md §六 已记前科）
#     Void  MeshAndRun()                       ← **零参**
#     Int32 CreateMesh(ByVal NUnits As Long, ByVal DElementSize As Double,
#                      ByVal DTolerance As Double)
#     Int32 CreateMeshForMeshControl(String MeshControlName)
#     Void  UpdateAllComponents()              ← 零参
#     Void  ActivateConfiguration()            ← 零参
#     Int32 CopyMeshFromStudy(String StudyName)
# ⚠⚠ **本组此前把 `CreateMesh` 的第 1 参写成 `MeshType` —— 是错的**（2026-10-01 更正）。
#   反射只给类型 `(Int32, Double, Double)`，参数名要靠 VB6 CHM 的签名页；
#   真名是 **`NUnits`**（`swsUnit_e`：SI 0 / English 1 / Metric 2），
#   后两参是 `DElementSize` / `DTolerance`（**毫米**）。
#   真机证据：`CreateMesh(0, 4.9339, 0.2467)` → 0 且 **7,219 个单元**（正常）；
#   `CreateMesh(0, 0.2467, 4.9339)` → 0 且 **19,509,593 个单元**（爆）⇒ 后两参顺序不能反。
#   详见 `scripts/sw_simulation.py::create_mesh` 的来源块。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def run_analysis(study) -> int:
    """运行求解。**零参**。返回官方错误码，见 SWS_RUN_ANALYSIS_ERRORS。"""
    return _checked(STUDY_ARITY, study, "RunAnalysis")


def mesh_and_run(study) -> bool:
    """划网格并求解。**零参**。"""
    _checked(STUDY_ARITY, study, "MeshAndRun")
    return True


def create_mesh(study, units: int, element_size: float, tolerance: float) -> int:
    """划网格。

    ⚠ 第 1 参是**单位**（``swsUnit_e``：0=SI、1=English、2=Metric），**不是网格类型**。
    后两参单位是**毫米**且须为正（传 0 得返回码 5 = ``SpecifyPositiveValue``）。
    """
    return _checked(STUDY_ARITY, study, "CreateMesh",
                    int(units), float(element_size), float(tolerance))


def create_mesh_for_control(study, control_name: str) -> int:
    """按网格控制项划网格。"""
    return _checked(STUDY_ARITY, study, "CreateMeshForMeshControl", str(control_name))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt → ICWStudy 段
# 定位:   载荷管理器 / 结果 / 网格对象的取用路径。官方反射确认这些是
#         **属性**（get_Xxx）：
#             CWLoadsAndRestraintsManager get_LoadsAndRestraintsManager()
#             CWResults                 get_Results()
#             CWMesh                    get_Mesh()
#             CWBeamManager             get_BeamManager()
#             CWContactManager          get_ContactManager()
#             CWLoadCaseManager         get_LoadCaseManager()
# ⚠ 这些属性在**有求解结果后**才有意义；未求解时取 Results 可能为 None。
#   本模块**不代为判断**是否已求解，只透传。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_study_manager_of(study):
    """取该研究的载荷夹具管理器（载荷模块的入口）。"""
    if study is None:
        raise ValueError("study 为 None")
    return get_com_member(study, "LoadsAndRestraintsManager")


def get_loads_manager_of(study):
    """同 :func:`get_study_manager_of`，语义更明确的名。"""
    return get_study_manager_of(study)


def get_results_of(study):
    """取结果对象 ICWResults（需已求解）。"""
    if study is None:
        raise ValueError("study 为 None")
    return get_com_member(study, "Results")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt → ICWStudy 段
# 定位:   研究导出与报告。官方签名逐条照抄：
#     Int32 ExportSimulationStudy(String, String, Int32, Int32, Int32,
#                                 Int32, Int32)                    → 7
#     Int32 GenerateReport(String, String, Boolean)                → 3
#     Int32 CreateAnalysisDatabase(String, String&)                 → 1 + out
#     Int32 ConnectAnalysisDatabase(String)                        → 1
#     Int32 CopyMeshFromStudy(String)                              → 1
# ⚠ ExportSimulationStudy 的 7 个参数**官方无文档页**，参数名与顺序只能靠
#   反射的声明顺序，语义未知 —— 本模块只按位置透传，不解释、不设默认值。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def export_study(study, *args):
    """导出研究（官方 7 参，参数语义无文档，按位置透传）。"""
    if len(args) != 7:
        raise ValueError(f"ExportSimulationStudy 官方签名是 7 个实参，给了 {len(args)} 个")
    return _checked(STUDY_ARITY, study, "ExportSimulationStudy", *args)


def generate_report(study, template: str, path: str, append: bool = False) -> int:
    """生成研究报告。"""
    return _checked(STUDY_ARITY, study, "GenerateReport",
                    str(template), str(path), bool(append))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（scripts/sw_simulation.py::collect_study_evidence）
# 定位:   研究状态证据回读，沿用「只取已核实成员」的写法。读取的属性全部是
#         ICWStudy 上反射确认为 Int32 / String / Boolean 的那些。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_study_evidence(study) -> dict[str, Any]:
    """回读研究对象的关键属性。"""
    if study is None:
        raise ValueError("study 为 None")
    return {
        "name": str(get_com_member(study, "Name") or ""),
        "configuration": str(get_com_member(study, "ConfigurationName") or ""),
        "analysis_type": int(get_com_member(study, "AnalysisType") or -1),
        "mesh_type": int(get_com_member(study, "MeshType") or -1),
        "dynamic_subtype": int(get_com_member(study, "DynamicAnalysisSubType") or -1),
        "nonlinear_subtype": int(get_com_member(study, "NonlinearAnalysisSubType") or -1),
        "off_load": bool(get_com_member(study, "OffLoad")),
        "has_results": get_com_member(study, "Results") is not None,
        "has_mesh": get_com_member(study, "Mesh") is not None,
    }
