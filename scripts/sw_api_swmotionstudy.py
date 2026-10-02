r"""SolidWorks swmotionstudy 官方接口全量索引。

能力域
    SolidWorks Motion —— 机构运动仿真（**需独立许可**）

本模块是什么
------------
**官方 API 的完整抄录** —— 11 个接口族、**81 个成员**，
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
    D:\AI\SW\_raw\reflect\iface_swmotionstudy.txt
      对 **SolidWorks.Interop.swmotionstudy.dll** 的纯元数据反射（AGENTS.md §四.1③）。
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
# 仓库:   官方 interop 程序集的纯元数据反射（SolidWorks.Interop.swmotionstudy.dll）
# 文件:   D:\AI\SW\_raw\reflect\iface_swmotionstudy.txt
# 定位:   11 个接口族的**全量**能力登记表 {族: {能力名: 实参个数}}。
# ⚑ 逐条机械生成，**不手抄、不折叠、不合并重载**。
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = ["ASSEMBLY", "FAMILIES", "ARITY", "PROPERTIES", "call_index"]

ASSEMBLY = 'swmotionstudy'

FAMILIES: tuple[str, ...] = (    'DMotionStudyEvents',
    'DMotionStudyEvents_Event',
    'IAVIParameter',
    'ICosmosMotionStudyProperties',
    'ICosmosMotionStudyResults',
    'IMotionPlotFeatureOutput',
    'IMotionStudy',
    'IMotionStudyManager',
    'IMotionStudyProperties',
    'IMotionStudyResults',
    'IPhysicalSimulationMotionStudyProperties',
)

#: 全量能力登记表 {族: {能力名: 实参个数}}（排除 by-ref 出参）
ARITY: dict[str, dict[str, int]] = {
    'DMotionStudyEvents': {
        'ForceOutputTimeStepChangeNotify': 6,
        'ForceTimeStepChangeNotify': 2,
        'MotorOutputTimeStepChangeNotify': 6,
        'MotorTimeStepChangeNotify': 2,
        'OutputTimeStepChangeNotify': 1,
        'PartCollideNotify': 7,
        'SpecialMotionEventNotify': 2,
        'StartCalculateNotify': 1,
        'StopCalculateNotify': 1,
    },
    'DMotionStudyEvents_Event': {
        'add_ForceOutputTimeStepChangeNotify': 1,
        'add_ForceTimeStepChangeNotify': 1,
        'add_MotorOutputTimeStepChangeNotify': 1,
        'add_MotorTimeStepChangeNotify': 1,
        'add_OutputTimeStepChangeNotify': 1,
        'add_PartCollideNotify': 1,
        'add_SpecialMotionEventNotify': 1,
        'add_StartCalculateNotify': 1,
        'add_StopCalculateNotify': 1,
        'remove_ForceOutputTimeStepChangeNotify': 1,
        'remove_ForceTimeStepChangeNotify': 1,
        'remove_MotorOutputTimeStepChangeNotify': 1,
        'remove_MotorTimeStepChangeNotify': 1,
        'remove_OutputTimeStepChangeNotify': 1,
        'remove_PartCollideNotify': 1,
        'remove_SpecialMotionEventNotify': 1,
        'remove_StartCalculateNotify': 1,
        'remove_StopCalculateNotify': 1,
    },
    'IAVIParameter': {
    },
    'ICosmosMotionStudyProperties': {
    },
    'ICosmosMotionStudyResults': {
        'CreatePlotFeatureData': 0,
        'CreatePlotXAxisFeatureData': 0,
        'CreatePlotYAxisFeatureData': 0,
        'ExportCSVFile': 2,
        'GetPlotCount': 0,
        'GetPlotFeatures': 0,
        'GetValues': 3,
        'InsertPlotFeature': 3,
    },
    'IMotionPlotFeatureOutput': {
        'GetXAxis': 0,
        'GetYAxis': 1,
    },
    'IMotionStudy': {
        'Activate': 0,
        'AddCosmosWorksPlot': 5,
        'Calculate': 0,
        'CreateByCollapse': 3,
        'CreateByExplode': 3,
        'CreateByRotateModel': 6,
        'CreateDefinition': 1,
        'CreateFeature': 1,
        'Duplicate': 0,
        'GetDuration': 0,
        'GetFireOutputTimeStepEvents': 0,
        'GetMotionFeatures': 0,
        'GetMotionFeaturesCount': 0,
        'GetNumOfExternalForces': 0,
        'GetNumOfExternalMotors': 0,
        'GetProperties': 1,
        'GetResults': 1,
        'GetSupportedStudyTypes': 0,
        'GetTime': 0,
        'Play': 0,
        'PlayFromStart': 0,
        'SaveToAVI': 2,
        'SetDuration': 1,
        'SetFireOutputTimeStepEvents': 1,
        'SetTime': 1,
        'Stop': 0,
    },
    'IMotionStudyManager': {
        'ActivateMotionStudy': 1,
        'CreateAVIParameter': 0,
        'CreateMotionStudy': 0,
        'DeleteMotionStudy': 1,
        'GetMotionStudy': 1,
        'GetMotionStudyCount': 0,
        'GetMotionStudyNames': 0,
    },
    'IMotionStudyProperties': {
        'GetFrameRate': 0,
        'SetFrameRate': 1,
    },
    'IMotionStudyResults': {
        'GetAngularAcceleration': 2,
        'GetAngularVelocity': 2,
        'GetCMPosition': 2,
        'GetEulerAngles': 2,
        'GetForceFromMate': 2,
        'GetLinearAcceleration': 2,
        'GetLinearVelocity': 2,
        'GetTorqueFromMate': 2,
        'IsOutOfDate': 0,
    },
    'IPhysicalSimulationMotionStudyProperties': {
    },
}

#: 属性名（反射里是 get_/set_，**不是方法**；这里只留去掉前缀的名字）
PROPERTIES: dict[str, tuple[str, ...]] = {
    'DMotionStudyEvents': (
    ),
    'DMotionStudyEvents_Event': (
    ),
    'IAVIParameter': (
        'AspectRatio',
        'AspectRatio',
        'BlurLength',
        'BlurLength',
        'BlurOffset',
        'BlurOffset',
        'EndTime',
        'EndTime',
        'FramePerSecond',
        'FramePerSecond',
        'ImageSize',
        'ImageSize',
        'MotionBlur',
        'MotionBlur',
        'OutputType',
        'OutputType',
        'PreserveRatio',
        'PreserveRatio',
        'RendererType',
        'RendererType',
        'SaveEntireAnimation',
        'SaveEntireAnimation',
        'ScreenHeight',
        'ScreenHeight',
        'ScreenRatio',
        'ScreenRatio',
        'ScreenWidth',
        'ScreenWidth',
        'StartTime',
        'StartTime',
    ),
    'ICosmosMotionStudyProperties': (
        'AnimateDuringSimulation',
        'AnimateDuringSimulation',
        'ContactResolution3D',
        'ContactResolution3D',
        'DeleteRedundantConstraints',
        'DeleteRedundantConstraints',
        'ErrorTolerance',
        'ErrorTolerance',
        'IntegratorAdaptivity',
        'IntegratorAdaptivity',
        'IntegratorType',
        'IntegratorType',
        'JacobianEval',
        'JacobianEval',
        'MakeAllMatesFlexible',
        'MakeAllMatesFlexible',
        'MaxIterations',
        'MaxIterations',
        'MaxStepSize',
        'MaxStepSize',
        'MinStepSize',
        'MinStepSize',
        'UsePreciseContact',
        'UsePreciseContact',
        'WireFrameGraphics',
        'WireFrameGraphics',
    ),
    'ICosmosMotionStudyResults': (
    ),
    'IMotionPlotFeatureOutput': (
    ),
    'IMotionStudy': (
        'IsActive',
        'IsPlaying',
        'Name',
        'Name',
        'PlayMode',
        'PlayMode',
        'StudyType',
        'StudyType',
    ),
    'IMotionStudyManager': (
    ),
    'IMotionStudyProperties': (
    ),
    'IMotionStudyResults': (
    ),
    'IPhysicalSimulationMotionStudyProperties': (
        'GeometricAccuracy',
        'GeometricAccuracy',
        'MateAccuracy',
        'MateAccuracy',
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
def call_index(obj, family: str, member: str, *args):
    """按登记表校核实参个数，通过后调用该族的成员。

    :raises KeyError: 族名或成员名不在登记表里（**不静默忽略**）
    :raises ValueError: 实参个数对不上（在**发起调用之前**就报）
    """
    sub = ARITY.get(family)
    if sub is None:
        raise KeyError(
            f"本清单没有这个族: {family}（swmotionstudy 共 {len(ARITY)} 族）。"
            f"⚠ 别的程序集请用对应的 call_index。")
    expected = sub.get(member)
    if expected is None:
        raise KeyError(
            f"{family} 上没有名为 {member} 的能力（该族登记 {len(sub)} 项）。"
            f"⚠ 若它是属性或 COM 内部分发口，请用对应封装。")
    if expected != len(args):
        raise ValueError(
            f"{family}.{member} 官方签名是 {expected} 个实参"
            f"（不含末位 by-ref 出参），本次调用给了 {len(args)} 个")
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

