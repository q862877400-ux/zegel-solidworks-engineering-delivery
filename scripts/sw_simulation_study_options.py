"""SolidWorks Simulation 求解器设置：各 *StudyOptions 族的 setter 登记表。

能力域
    域 13 · 仿真（需许可证）

本模块解决什么问题
------------------
cosworks 的求解器设置分散在 9 个 ``*StudyOptions`` 族里，**合计 242 个 setter**
（静态研究 55、非线性 40、动态 34、频率 31、屈曲 24、热 22、疲劳 14、
  复合材料壳 12、跌落 10）。逐个包一层 Python 函数，代码量大、单位信息量低。

但「**这个求解器到底能配什么**」本身是权威信息 —— 它决定了下游能做到哪一步。
所以本模块做两件事：
  1. **登记表**（``STUDY_OPTION_SETTERS``）：把反射确认的 242 个可设项
     落成**字符串字面量**，可 grep、可被测试逐条核对。
     刻意**不做运行时反射** —— 那会随 SolidWorks 版本漂移。
  2. **受登记表约束的通用 setter** ``set_option()`` + 少量高频项显式包装。

⚠ 登记表是「名字 + 参数类型」，**不含语义**。这些族官方 CHM 没有文档页，
  参数的工程含义查不到 ⇒ 本模块**不解释任何一项是干什么的**，
  只保证「这个名字确实存在于官方 API，且参数个数对得上」。

⚑ X / X2 成对规律
------------------
多数布尔开关都有**两个** setter：``X(Int32)`` 与 ``X2(Boolean)``
（如 ``CheckFlowPressure`` / ``CheckFlowPressure2``）。
反射确认这是**两个不同签名的成员，不是新旧版替代**。
本模块**只推荐 X2（Boolean）**那一个，并在登记表里把 X2 单列出来 ——
理由：Int32 那个的取值语义（0/1/-1？枚举？）查不到，Boolean 版没有这个歧义。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt   （对 interop 纯元数据反射）
登记表由 D:\\AI\\SW\\tools\\gen_study_options_registry.py 机械生成，
不手抄；生成物 D:\\AI\\SW\\_raw\\study_options_setters.json。

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member, set_com_member
except ImportError:
    #: ★★ 2026-10-01（轮 344）：**两条分支的名字集合必须一致** ——
    #:   ★ 本仓库已踩过一次（`sw_render_material.py` 的 `except` 分支少了 `set_com_member`
    #:   ⇒ 而本机走的**就是**那条 ⇒ `NameError`）⇒ ★ 这里两条都带上。
    from sw_connect import get_com_member, set_com_member

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_simulation_study_options.py —— 本文件自身
# 定位:   模块导出清单、族名常量与类型归一表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方函数另附来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "STUDY_OPTION_FAMILIES",
    "STUDY_OPTION_SETTERS",
    "BOOLEAN_SETTERS",
    "ARITY_TABLE",
    "study_options_of",
    "set_option",
    "set_options",
    "configure_static_solver",
    "configure_frequency_solver",
    "configure_buckling_solver",
    "list_setter_summary",
]

#: 九个可设项的研究设置族（反射确认有 setter 的）
STUDY_OPTION_FAMILIES = (
    "ICWStaticStudyOptions",
    "ICWFrequencyStudyOptions",
    "ICWBucklingStudyOptions",
    "ICWNonLinearStudyOptions",
    "ICWThermalStudyOptions",
    "ICWDynamicStudyOptions",
    "ICWFatigueStudyOptions",
    "ICWDropTestStudyOptions",
    "ICWCompositeShellOptions",
)

#: 反射里的参数类型名 → Python 侧期望的归一类型
_TYPE_ALIASES = {
    "Int32": "int",
    "System.Int32": "int",
    "Boolean": "bool",
    "System.Boolean": "bool",
    "Double": "float",
    "System.Double": "float",
    "String": "str",
    "System.String": "str",
}

#: 反射确认的 setter 登记表：{族: {setter名: 参数类型}}
# ⚠ 机械生成（D:\AI\SW\tools\gen_study_options_registry.py），不手抄。
STUDY_OPTION_SETTERS: dict[str, dict[str, str]] = {
    'ICWStaticStudyOptions': {
        'AdaptiveMethodType': 'Int32',
        'CheckFlowPressure': 'Int32',
        'CheckFlowPressure2': 'Boolean',
        'CheckRunAsLegacy': 'Int32',
        'CheckRunAsLegacy2': 'Boolean',
        'ComputeFreeBodyForce': 'Int32',
        'ComputeFreeBodyForce2': 'Boolean',
        'ContactPenaltyStiffnessScaleFactor': 'Double',
        'ContactPenaltyStiffnessScaleFactorGlobalDefault': 'Double',
        'DefinedReferencePressure': 'Double',
        'EMail': 'Int32',
        'EMail2': 'Boolean',
        'EMailInterval': 'Int32',
        'EMailIntervalUnit': 'Int32',
        'EMailTimebased': 'Int32',
        'EMailTimebased2': 'Boolean',
        'EMailTo': 'String',
        'FlowPressureFile': 'String',
        'FlowTemperatureFile': 'String',
        'FrictionCoefficient': 'Double',
        'HAdaptiveAccuracyBias': 'Double',
        'HAdaptiveMaxNoIterations': 'Int32',
        'HAdaptiveMeshCoarsening': 'Int32',
        'HAdaptiveMeshCoarsening2': 'Boolean',
        'HAdaptiveTargetAccuracy': 'Double',
        'IgnoreClearanceForSurfaceContact': 'Int32',
        'IgnoreClearanceForSurfaceContact2': 'Boolean',
        'IncludeGlobalFriction': 'Int32',
        'IncludeGlobalFriction2': 'Boolean',
        'IncludeRemarkInReport': 'Int32',
        'IncludeRemarkInReport2': 'Boolean',
        'IncompatibleBondingOption': 'Int32',
        'LargeDisplacement': 'Int32',
        'LargeDisplacement2': 'Boolean',
        'NoPenetration': 'Int32',
        'NoPenetration2': 'Boolean',
        'PAdaptiveConvergenceCriteria': 'Int32',
        'PAdaptiveErrorLimit': 'Double',
        'PAdaptiveMaxIterations': 'Int32',
        'PAdaptiveMaxPOrder': 'Int32',
        'PAdaptiveStartingPOrder': 'Int32',
        'PAdaptiveStrainEnergyErrorLimit': 'Double',
        'ReferencePressureOption': 'Int32',
        'RemarkComment': 'String',
        'ResultFolder': 'String',
        'SolverType': 'Int32',
        'ThermalResults': 'Int32',
        'ThermalStudyName': 'String',
        'TimeStep': 'Int32',
        'UseInertialRelief': 'Int32',
        'UseInertialRelief2': 'Boolean',
        'UseInPlaneEffect': 'Int32',
        'UseInPlaneEffect2': 'Boolean',
        'UseSoftSpring': 'Int32',
        'UseSoftSpring2': 'Boolean',
    },
    'ICWFrequencyStudyOptions': {
        'CheckDecouple': 'Boolean',
        'CheckFlowPressure': 'Int32',
        'CheckFlowPressure2': 'Boolean',
        'CheckRunAsLegacy': 'Int32',
        'CheckRunAsLegacy2': 'Boolean',
        'DefinedReferencePressure': 'Double',
        'EMail': 'Int32',
        'EMail2': 'Boolean',
        'EMailInterval': 'Int32',
        'EMailIntervalUnit': 'Int32',
        'EMailTimebased': 'Int32',
        'EMailTimebased2': 'Boolean',
        'EMailTo': 'String',
        'FlowPressureFile': 'String',
        'FlowTemperatureFile': 'String',
        'FrequencyCapOption': 'Int32',
        'FrequencyCapValue': 'Int32',
        'LowerBoundFrequency': 'Int32',
        'NoOfFrequencies': 'Int32',
        'Options': 'Int32',
        'ReferencePressureOption': 'Int32',
        'ResultFolder': 'String',
        'SolverType': 'Int32',
        'ThermalResults': 'Int32',
        'ThermalStudyName': 'String',
        'TimeStep': 'Int32',
        'UpperBoundFrequency': 'Int32',
        'UseLowerBoundFrequency': 'Int32',
        'UseLowerBoundFrequency2': 'Boolean',
        'UseSoftSpring': 'Int32',
        'UseSoftSpring2': 'Boolean',
    },
    'ICWBucklingStudyOptions': {
        'BucklingModes': 'Int32',
        'CheckFlowPressure': 'Int32',
        'CheckFlowPressure2': 'Boolean',
        'CheckRunAsLegacy': 'Int32',
        'CheckRunAsLegacy2': 'Boolean',
        'DefinedReferencePressure': 'Double',
        'EMail': 'Int32',
        'EMail2': 'Boolean',
        'EMailInterval': 'Int32',
        'EMailIntervalUnit': 'Int32',
        'EMailTimebased': 'Int32',
        'EMailTimebased2': 'Boolean',
        'EMailTo': 'String',
        'ExtractPositiveBucklingFactorsOnly': 'Boolean',
        'FlowPressureFile': 'String',
        'FlowTemperatureFile': 'String',
        'ReferencePressureOption': 'Int32',
        'ResultFolder': 'String',
        'SolverType': 'Int32',
        'ThermalResults': 'Int32',
        'ThermalStudyName': 'String',
        'TimeStep': 'Int32',
        'UseSoftSpring': 'Int32',
        'UseSoftSpring2': 'Boolean',
    },
    'ICWNonLinearStudyOptions': {
        'CheckFlowPressure': 'Int32',
        'CheckFlowPressure2': 'Boolean',
        'CheckRunAsLegacy': 'Int32',
        'CheckRunAsLegacy2': 'Boolean',
        'CheckUseTempFromThermalStudy': 'Int32',
        'CheckUseTempFromThermalStudy2': 'Boolean',
        'ContactPenaltyStiffnessScaleFactor': 'Double',
        'ContactPenaltyStiffnessScaleFactorGlobalDefault': 'Double',
        'ControlMethodType': 'Int32',
        'DefinedReferencePressure': 'Double',
        'EMail': 'Int32',
        'EMail2': 'Boolean',
        'EMailInterval': 'Int32',
        'EMailIntervalUnit': 'Int32',
        'EMailTimebased': 'Int32',
        'EMailTimebased2': 'Boolean',
        'EMailTo': 'String',
        'EndTime': 'Double',
        'FixedTimeIncrement': 'Double',
        'FlowPressureFile': 'String',
        'FlowTemperatureFile': 'String',
        'IntegrationMethodType': 'Int32',
        'IterativeMethodType': 'Int32',
        'KeepBoltPreStress': 'Int32',
        'KeepBoltPreStress2': 'Boolean',
        'ReferencePressureOption': 'Int32',
        'ResultFolderPath': 'String',
        'SaveDataForRestartingAnalysis': 'Int32',
        'SaveDataForRestartingAnalysis2': 'Boolean',
        'SolverType': 'Int32',
        'ThermalResults': 'Int32',
        'ThermalStudyName': 'String',
        'TimeIncrement': 'Int32',
        'TimeStep': 'Int32',
        'UseLargeDisplacement': 'Int32',
        'UseLargeDisplacement2': 'Boolean',
        'UseLargeStrain': 'Int32',
        'UseLargeStrain2': 'Boolean',
        'UseUpdateLoadDirection': 'Int32',
        'UseUpdateLoadDirection2': 'Boolean',
    },
    'ICWThermalStudyOptions': {
        'CheckFlowConvectionCoef': 'Int32',
        'CheckFlowConvectionCoef2': 'Boolean',
        'ConvergenceTolerance': 'Double',
        'EMail': 'Int32',
        'EMail2': 'Boolean',
        'EMailInterval': 'Int32',
        'EMailIntervalUnit': 'Int32',
        'EMailTimebased': 'Int32',
        'EMailTimebased2': 'Boolean',
        'EMailTo': 'String',
        'FixedValue': 'Double',
        'FlowConvectionCoefFile': 'String',
        'RelaxationFactor': 'Int32',
        'ResultFolder': 'String',
        'SolutionType': 'Int32',
        'SolverType': 'Int32',
        'ThermalStudyNameUsedForInitialTemperature': 'String',
        'TimeIncrement': 'Double',
        'TimeSteps': 'Int32',
        'TotalTime': 'Double',
        'UseTemperatureFromThermalStudy': 'Int32',
        'UseTemperatureFromThermalStudy2': 'Boolean',
    },
    'ICWDynamicStudyOptions': {
        'EMail': 'Int32',
        'EMail2': 'Boolean',
        'EMailInterval': 'Int32',
        'EMailIntervalUnit': 'Int32',
        'EMailTimebased': 'Int32',
        'EMailTimebased2': 'Boolean',
        'EMailTo': 'String',
        'HarmonicBandwidth': 'Double',
        'HarmonicFrequencyLowerLimit': 'Double',
        'HarmonicFrequencyUnits': 'Int32',
        'HarmonicFrequencyUpperLimit': 'Double',
        'HarmonicInterpolation': 'Int32',
        'HarmonicNoOfPoints': 'Int32',
        'IncompatibleBondingOption': 'Int32',
        'RandomVibrationAnalysisMethod': 'Int32',
        'RandomVibrationBiasingParameter': 'Double',
        'RandomVibrationCorrelationOption': 'Int32',
        'RandomVibrationCrossModeCutOffRatio': 'Double',
        'RandomVibrationFrequencyLowerLimit': 'Double',
        'RandomVibrationFrequencyUnits': 'Int32',
        'RandomVibrationFrequencyUpperLimit': 'Double',
        'RandomVibrationGaussIntegrationOrder': 'Int32',
        'RandomVibrationNoOfFrequencyPoints': 'Int32',
        'ResponseSpectrumClusterFactor': 'Double',
        'ResponseSpectrumCurveInterpolation': 'Int32',
        'ResponseSpectrumModeCombinationMethod': 'Int32',
        'ResponseSpectrumUseMaterialDamping': 'Int32',
        'ResultFolderPath': 'String',
        'SolverType': 'Int32',
        'TimeHistoryFirstIntegrationParameter': 'Double',
        'TimeHistoryIntegrationMethod': 'Int32',
        'TimeHistorySecondIntegrationParameter': 'Double',
        'TimeHistoryWilsonTheta': 'Double',
        'UseSoftSpring': 'Int32',
    },
    'ICWFatigueStudyOptions': {
        'ComputingAlternatingStressOption': 'Int32',
        'ConstantAmplitudeEventInteractionOption': 'Int32',
        'EMail': 'Int32',
        'EMail2': 'Boolean',
        'EMailInterval': 'Int32',
        'EMailIntervalUnit': 'Int32',
        'EMailTimebased': 'Int32',
        'EMailTimebased2': 'Boolean',
        'EMailTo': 'String',
        'FatigueStrengthReductionFactor': 'Double',
        'MeanStressCorrectionOption': 'Int32',
        'RandomVibrationComputationalMethod': 'Int32',
        'ResultFolder': 'String',
        'ShellFace': 'Int32',
    },
    'ICWDropTestStudyOptions': {
        'EMail': 'Int32',
        'EMail2': 'Boolean',
        'EMailInterval': 'Int32',
        'EMailIntervalUnit': 'Int32',
        'EMailTimebased': 'Int32',
        'EMailTimebased2': 'Boolean',
        'EMailTo': 'String',
        'LargeDisplacement': 'Int32',
        'LargeDisplacement2': 'Boolean',
        'ResultFolder': 'String',
    },
    'ICWCompositeShellOptions': {
        'AllPliesSameMaterial': 'Int32',
        'AllPliesSameMaterial2': 'Boolean',
        'LengthUnit': 'Int32',
        'MappingType': 'Int32',
        'PlyRelativeAngle': 'Int32',
        'PlyRelativeAngle2': 'Boolean',
        'RotateZeroDegreeReference': 'Int32',
        'RotateZeroDegreeReference2': 'Boolean',
        'Sandwich': 'Int32',
        'Sandwich2': 'Boolean',
        'Symmetric': 'Int32',
        'Symmetric2': 'Boolean',
    },
}

#: 只列 **X2（Boolean）** 形 —— 避开 Int32 版的取值语义歧义
BOOLEAN_SETTERS: dict[str, tuple[str, ...]] = {
    'ICWStaticStudyOptions': (
        'CheckFlowPressure2',
        'CheckRunAsLegacy2',
        'ComputeFreeBodyForce2',
        'EMail2',
        'EMailTimebased2',
        'HAdaptiveMeshCoarsening2',
        'IgnoreClearanceForSurfaceContact2',
        'IncludeGlobalFriction2',
        'IncludeRemarkInReport2',
        'LargeDisplacement2',
        'NoPenetration2',
        'UseInPlaneEffect2',
        'UseInertialRelief2',
        'UseSoftSpring2',
    ),
    'ICWFrequencyStudyOptions': (
        'CheckFlowPressure2',
        'CheckRunAsLegacy2',
        'EMail2',
        'EMailTimebased2',
        'UseLowerBoundFrequency2',
        'UseSoftSpring2',
    ),
    'ICWBucklingStudyOptions': (
        'CheckFlowPressure2',
        'CheckRunAsLegacy2',
        'EMail2',
        'EMailTimebased2',
        'UseSoftSpring2',
    ),
    'ICWNonLinearStudyOptions': (
        'CheckFlowPressure2',
        'CheckRunAsLegacy2',
        'CheckUseTempFromThermalStudy2',
        'EMail2',
        'EMailTimebased2',
        'KeepBoltPreStress2',
        'SaveDataForRestartingAnalysis2',
        'UseLargeDisplacement2',
        'UseLargeStrain2',
        'UseUpdateLoadDirection2',
    ),
    'ICWThermalStudyOptions': (
        'CheckFlowConvectionCoef2',
        'EMail2',
        'EMailTimebased2',
        'UseTemperatureFromThermalStudy2',
    ),
    'ICWDynamicStudyOptions': (
        'EMail2',
        'EMailTimebased2',
    ),
    'ICWFatigueStudyOptions': (
        'EMail2',
        'EMailTimebased2',
    ),
    'ICWDropTestStudyOptions': (
        'EMail2',
        'EMailTimebased2',
        'LargeDisplacement2',
    ),
    'ICWCompositeShellOptions': (
        'AllPliesSameMaterial2',
        'PlyRelativeAngle2',
        'RotateZeroDegreeReference2',
        'Sandwich2',
        'Symmetric2',
    ),
}

#: 登记表里每个 setter 的**实参个数**（全部是 1，登记以备审计）
ARITY_TABLE: dict[str, int] = {
    'AdaptiveMethodType': 1,
    'AllPliesSameMaterial': 1,
    'AllPliesSameMaterial2': 1,
    'BucklingModes': 1,
    'CheckDecouple': 1,
    'CheckFlowConvectionCoef': 1,
    'CheckFlowConvectionCoef2': 1,
    'CheckFlowPressure': 1,
    'CheckFlowPressure2': 1,
    'CheckRunAsLegacy': 1,
    'CheckRunAsLegacy2': 1,
    'CheckUseTempFromThermalStudy': 1,
    'CheckUseTempFromThermalStudy2': 1,
    'ComputeFreeBodyForce': 1,
    'ComputeFreeBodyForce2': 1,
    'ComputingAlternatingStressOption': 1,
    'ConstantAmplitudeEventInteractionOption': 1,
    'ContactPenaltyStiffnessScaleFactor': 1,
    'ContactPenaltyStiffnessScaleFactorGlobalDefault': 1,
    'ControlMethodType': 1,
    'ConvergenceTolerance': 1,
    'DefinedReferencePressure': 1,
    'EMail': 1,
    'EMail2': 1,
    'EMailInterval': 1,
    'EMailIntervalUnit': 1,
    'EMailTimebased': 1,
    'EMailTimebased2': 1,
    'EMailTo': 1,
    'EndTime': 1,
    'ExtractPositiveBucklingFactorsOnly': 1,
    'FatigueStrengthReductionFactor': 1,
    'FixedTimeIncrement': 1,
    'FixedValue': 1,
    'FlowConvectionCoefFile': 1,
    'FlowPressureFile': 1,
    'FlowTemperatureFile': 1,
    'FrequencyCapOption': 1,
    'FrequencyCapValue': 1,
    'FrictionCoefficient': 1,
    'HAdaptiveAccuracyBias': 1,
    'HAdaptiveMaxNoIterations': 1,
    'HAdaptiveMeshCoarsening': 1,
    'HAdaptiveMeshCoarsening2': 1,
    'HAdaptiveTargetAccuracy': 1,
    'HarmonicBandwidth': 1,
    'HarmonicFrequencyLowerLimit': 1,
    'HarmonicFrequencyUnits': 1,
    'HarmonicFrequencyUpperLimit': 1,
    'HarmonicInterpolation': 1,
    'HarmonicNoOfPoints': 1,
    'IgnoreClearanceForSurfaceContact': 1,
    'IgnoreClearanceForSurfaceContact2': 1,
    'IncludeGlobalFriction': 1,
    'IncludeGlobalFriction2': 1,
    'IncludeRemarkInReport': 1,
    'IncludeRemarkInReport2': 1,
    'IncompatibleBondingOption': 1,
    'IntegrationMethodType': 1,
    'IterativeMethodType': 1,
    'KeepBoltPreStress': 1,
    'KeepBoltPreStress2': 1,
    'LargeDisplacement': 1,
    'LargeDisplacement2': 1,
    'LengthUnit': 1,
    'LowerBoundFrequency': 1,
    'MappingType': 1,
    'MeanStressCorrectionOption': 1,
    'NoOfFrequencies': 1,
    'NoPenetration': 1,
    'NoPenetration2': 1,
    'Options': 1,
    'PAdaptiveConvergenceCriteria': 1,
    'PAdaptiveErrorLimit': 1,
    'PAdaptiveMaxIterations': 1,
    'PAdaptiveMaxPOrder': 1,
    'PAdaptiveStartingPOrder': 1,
    'PAdaptiveStrainEnergyErrorLimit': 1,
    'PlyRelativeAngle': 1,
    'PlyRelativeAngle2': 1,
    'RandomVibrationAnalysisMethod': 1,
    'RandomVibrationBiasingParameter': 1,
    'RandomVibrationComputationalMethod': 1,
    'RandomVibrationCorrelationOption': 1,
    'RandomVibrationCrossModeCutOffRatio': 1,
    'RandomVibrationFrequencyLowerLimit': 1,
    'RandomVibrationFrequencyUnits': 1,
    'RandomVibrationFrequencyUpperLimit': 1,
    'RandomVibrationGaussIntegrationOrder': 1,
    'RandomVibrationNoOfFrequencyPoints': 1,
    'ReferencePressureOption': 1,
    'RelaxationFactor': 1,
    'RemarkComment': 1,
    'ResponseSpectrumClusterFactor': 1,
    'ResponseSpectrumCurveInterpolation': 1,
    'ResponseSpectrumModeCombinationMethod': 1,
    'ResponseSpectrumUseMaterialDamping': 1,
    'ResultFolder': 1,
    'ResultFolderPath': 1,
    'RotateZeroDegreeReference': 1,
    'RotateZeroDegreeReference2': 1,
    'Sandwich': 1,
    'Sandwich2': 1,
    'SaveDataForRestartingAnalysis': 1,
    'SaveDataForRestartingAnalysis2': 1,
    'ShellFace': 1,
    'SolutionType': 1,
    'SolverType': 1,
    'Symmetric': 1,
    'Symmetric2': 1,
    'ThermalResults': 1,
    'ThermalStudyName': 1,
    'ThermalStudyNameUsedForInitialTemperature': 1,
    'TimeHistoryFirstIntegrationParameter': 1,
    'TimeHistoryIntegrationMethod': 1,
    'TimeHistorySecondIntegrationParameter': 1,
    'TimeHistoryWilsonTheta': 1,
    'TimeIncrement': 1,
    'TimeStep': 1,
    'TimeSteps': 1,
    'TotalTime': 1,
    'UpperBoundFrequency': 1,
    'UseInPlaneEffect': 1,
    'UseInPlaneEffect2': 1,
    'UseInertialRelief': 1,
    'UseInertialRelief2': 1,
    'UseLargeDisplacement': 1,
    'UseLargeDisplacement2': 1,
    'UseLargeStrain': 1,
    'UseLargeStrain2': 1,
    'UseLowerBoundFrequency': 1,
    'UseLowerBoundFrequency2': 1,
    'UseSoftSpring': 1,
    'UseSoftSpring2': 1,
    'UseTemperatureFromThermalStudy': 1,
    'UseTemperatureFromThermalStudy2': 1,
    'UseUpdateLoadDirection': 1,
    'UseUpdateLoadDirection2': 1,
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_simulation_study_options.py —— 本文件自身
# 定位:   通用 setter 的取值校验与调用。
# ⚠ 名字与值都由调用方给 ⇒ 静态 arity 审计归因不到（成员名是变量）。
#   对账靠 tests/test_sw_simulation_study_options_contract.py：
#   逐条核对「登记表 ⊆ 反射清单」。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def _coerce(raw_type: str, value):
    """按反射登记的参数类型转换取值；类型对不上直接报错。"""
    want = _TYPE_ALIASES.get(raw_type, raw_type)
    if want == "int":
        return int(value)
    if want == "bool":
        return bool(value)
    if want == "float":
        return float(value)
    if want == "str":
        return str(value)
    return value


#: dispatch-guard: exempt module-local
def set_option(options, family: str, name: str, value) -> bool:
    """按登记表设一个求解器选项。

    :param family: STUDY_OPTION_FAMILIES 里的族名
    :param name: 该族登记表中确实存在的 setter 名
    :raises KeyError: 族名或选项名不在登记表里（**不静默忽略**）
    """
    if options is None:
        raise ValueError("options 为 None")
    if family not in STUDY_OPTION_SETTERS:
        raise KeyError(f"未知的研究设置族: {family}")
    entry = STUDY_OPTION_SETTERS[family].get(name)
    if entry is None:
        raise KeyError(
            f"{family} 没有名为 {name} 的 setter。\n"
            f"该族登记的 {len(STUDY_OPTION_SETTERS[family])} 项，"
            f"其中布尔型（推荐用）: {sorted(BOOLEAN_SETTERS.get(family, ()))[:8]} …"
        )
    #: ★★★★★ 2026-10-01（轮 344）**设属性必须用 `set_com_member`，不能用 `get_com_member(…, value)`** ——
    #:   真因（挖 `simulation_solver_options` 这条 `stitched` 时发现，★ 而它的 `limitations` 里
    #:   **早就写着**「① `TypeError: 'bool' object is not callable` ⇒ 真机上该成员**已是 bool 值**」）：
    #:   ★ `get_com_member(obj, "X", value)` 的语义是**「取或调」** —— ★ **传了实参**时它
    #:   **先无参调一次**拿到返回值、★ **再拿那个返回值去"调用"**（★ 事实 227）。
    #:   ⇒ ★ 对**属性**（值已是 `bool`）就会 `TypeError: 'bool' object is not callable`；
    #:   ⇒ ★★ **而★对方法**才是对的 —— ★ 所以两种语义**必须分开用**：
    #:     · **属性** ⇒ `set_com_member`（★ 直接设）
    #:     · **方法** ⇒ `get_com_member(obj, name, *args)`（★ 调用）
    #:   ⚠ 本处 `name` 来自 `STUDY_OPTION_SETTERS` 登记表，★ 表里**既有属性也有方法** ⇒
    #:     ★ 按"能不能设"分流：★ 先试 `set_com_member`，★ 失败再退回调用式（★ 两条路都记进返回值）。
    #:   ⚠⚠ 而 `set_com_member` **必须在模块顶部 import**（★ 与 `get_com_member` 并列）——
    #:     ★ 我第一版把 `from sw_connect import set_com_member` **写在函数体内**，
    #:     ★★ 而测试里 `sw_connect` 是 **mock**（★ 只提供 `get_com_member`）⇒
    #:     `ImportError: cannot import name 'set_com_member' from 'sw_connect' (unknown location)`
    #:     ⇒ **2 个契约测试当场失败**（★ 那就是"聚焦测试"抓到的）。
    coerced = _coerce(entry, value)
    try:
        set_com_member(options, name, coerced)
        return True
    #: ★★★★ 2026-10-01（轮 344）**收窄 except —— 不许吞自己的编码错**：
    #:   ★ 第一版写的是 `except Exception`，★ 而我把 `_set_com_member` 那行 import 删掉后
    #:   **名字没跟着改** ⇒ ★ `NameError` **被这个宽 except 吞掉** ⇒ **静默退回调用式** ⇒
    #:   ★★ **我的修复根本没生效，而函数看起来"正常"**（★ 是本文件那个新加的测试抓到的）。
    #:   ⇒ ★ 只捕获**"设不进去"那两种**：★ `AttributeError`（不是可设属性）· `TypeError`（不是可调方法）；
    #:     ★ **其余的异常照旧抛出**（★ `NameError` / `KeyboardInterrupt` 之类**必须可见**）。
    except (AttributeError, TypeError) as exc:
        #: ★ 退回"当方法调"（★ 登记表里确实是方法的那些走这里）
        r = get_com_member(options, name, coerced)
        if r is None:
            raise RuntimeError(
                "%s.%s 既不是可设属性、也不是可调方法：%s: %s"
                % (family, name, type(exc).__name__, str(exc)[:120])
            ) from exc
        return bool(r)


def set_options(options, family: str, values: dict[str, Any]) -> dict[str, Any]:
    """批量设；只设你给了的键。返回实际设置成功的键值。"""
    applied: dict[str, Any] = {}
    for name, value in values.items():
        if value is None:
            continue
        #: dispatch-fwd: dynamic `values` 是调用方给的 dict ⇒ 键（成员名）在静态范围外
        set_option(options, family, name, value)
        applied[name] = value
    return applied


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt
#           → ICWStudy.get_StaticStudyOptions / get_FrequencyStudyOptions /
#             get_BucklingStudyOptions 等属性
# 定位:   从研究对象取各设置族。官方反射里这些是**属性**（get_ 形式）。
# ⚠ 取用路径的正确拼写（反射里的属性名）：
#     ICWStudy 上有 get_StaticStudyOptions / get_FrequencyStudyOptions /
#     get_BucklingStudyOptions / get_NonLinearStudyOptions /
#     get_DynamicStudyOptions / get_FatigueStudyOptions /
#     get_DropTestStudyOptions（上面几行 ICWStudy 段的清单里可见部分），
#     **热与复合材料壳的取值名未在已见清单中确认** ⇒ 不臆造，
#     用下面的显式取用器只暴露反射确认过的那些。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
#: study 对象上的设置族属性名（反射逐个确认的）
STUDY_OPTIONS_ACCESSORS = {
    "ICWStaticStudyOptions": "StaticStudyOptions",
    "ICWFrequencyStudyOptions": "FrequencyStudyOptions",
    "ICWBucklingStudyOptions": "BucklingStudyOptions",
    "ICWNonLinearStudyOptions": "NonLinearStudyOptions",
    "ICWDynamicStudyOptions": "DynamicStudyOptions",
    "ICWFatigueStudyOptions": "FatigueStudyOptions",
    "ICWDropTestStudyOptions": "DropTestStudyOptions",
}


def study_options_of(study, family: str):
    """从 ICWStudy 取某个设置族对象。族名须在 STUDY_OPTIONS_ACCESSORS 里。"""
    if study is None:
        raise ValueError("study 为 None")
    accessor = STUDY_OPTIONS_ACCESSORS.get(family)
    if accessor is None:
        raise KeyError(
            f"{family} 的 study 取用属性名未在反射清单里确认，"
            f"不臆造。已确认: {', '.join(sorted(STUDY_OPTIONS_ACCESSORS))}"
        )
    return get_com_member(study, accessor)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt → 三个族的 set_ 段
# 定位:   三组高频求解器设置的显式包装。**只挑反射清单里能确认存在的项**，
#         且只用 **X2（Boolean）** 形（避开 Int32 版的取值语义歧义）。
#   ICWStaticStudyOptions    : set_CheckFlowPressure2(Boolean)
#                              set_ComputeFreeBodyForce2(Boolean)
#                              set_ContactPenaltyStiffnessScaleFactor(Double)
#                              set_DefinedReferencePressure(Double)
#   ICWFrequencyStudyOptions : set_CheckDecouple(Boolean)
#                              set_DefinedReferencePressure(Double)
#   ICWBucklingStudyOptions  : set_BucklingModes(Int32)
#                              set_ExtractPositiveBucklingFactorsOnly(Boolean)
#                              set_DefinedReferencePressure(Double)
# ⚠ 这些项的**工程含义**官方无文档，本模块只保证「签名对得上、值类型对得上」，
#   不解释「什么时候该打开」。需要语义请查 SolidWorks Simulation 用户文档。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def configure_static_solver(options, *, free_body_force: bool | None = None,
                            contact_penalty: float | None = None,
                            reference_pressure: float | None = None
                            ) -> dict[str, Any]:
    """静态研究求解器设置。"""
    return set_options(options, "ICWStaticStudyOptions", {
        "ComputeFreeBodyForce2": free_body_force,
        "ContactPenaltyStiffnessScaleFactor": contact_penalty,
        "DefinedReferencePressure": reference_pressure,
    })


def configure_frequency_solver(options, *, decouple: bool | None = None,
                              reference_pressure: float | None = None
                              ) -> dict[str, Any]:
    """频率研究求解器设置。"""
    return set_options(options, "ICWFrequencyStudyOptions", {
        "CheckDecouple": decouple,
        "DefinedReferencePressure": reference_pressure,
    })


def configure_buckling_solver(options, *, modes: int | None = None,
                              positive_only: bool | None = None,
                              reference_pressure: float | None = None
                              ) -> dict[str, Any]:
    """屈曲研究求解器设置。"""
    return set_options(options, "ICWBucklingStudyOptions", {
        "BucklingModes": modes,
        "ExtractPositiveBucklingFactorsOnly": positive_only,
        "DefinedReferencePressure": reference_pressure,
    })


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_simulation_study_options.py —— 本文件自身
# 定位:   登记表自省，帮助下游看清「这一族能配什么」。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def list_setter_summary() -> dict[str, Any]:
    """返回各族 setter 数量与布尔型清单（供文档生成 / 自检使用）。"""
    return {
        family: {
            "total": len(items),
            "boolean": len(BOOLEAN_SETTERS.get(family, ())),
            "names": sorted(items),
        }
        for family, items in STUDY_OPTION_SETTERS.items()
    }


# ── 24h 计划 段 1 续（Spec Kit `154`）：**从 study 取 options 的求解器设置包装** ──────────
# ★★★★ 为什么包一层（★ 而不是加新的注入键）：
#   · 底层 `configure_static_solver(options, …)` / `set_option(options, family, name, value)` 等
#     **要一个 `options` 宿主对象**；★ 而那个对象**从 study 取**：
#       `study_options_of(study, family)` → `get_com_member(study, accessor)`
#   · ★★ 而 **`inject="study"` 早就存在**（`resolve_study`）⇒ ★★★ **所以包一层就够了**：
#       工具层**注入 `study`** ⇒ 包装内部**先取 options** ⇒ 再调底层
#     ⇒ ★★★★ **不需要新增 `RESOLVERS` 键**（★ 加了要同步解析器，★ 而这里没必要）。
#   ★ 与孔族（`*_at_selection`）**同一手法**：★ **用已有的 resolver + 包装**表达新工具。
#
# ★ 判据（★ 三层）：
#   ① ★ 取 options **成功**（★ 取不到就如实报 —— `study_options_of` 对**未确认的族名**会抛
#      `KeyError` 并**列出已确认的那些** ⇒ ★ 那正是"会列合法值的好报错"，见事实 204）；
#   ② ★ 底层返回的 **`bool` / dict 如实回传**；
#   ③ ★ 把**用了哪个族**与**改了什么**记在返回里（★ 便于下一步回读核对）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_simulation_study_options.py —— 本段
# 定位:   段 1 续：让"求解器设置"能被工具层表达（★ 不要注入键）。
# 官方依据: `ICWStaticStudyOptions` / `ICWFrequencyStudyOptions` / `ICWBucklingStudyOpti
#           ons`
#          （★ 见 `STUDY_OPTIONS_ACCESSORS` 的反射清单）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖: 后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def _options_from_study(study, family: str):
    """★ 从 study 取某个设置族对象；★ 取不到就**如实报**（★ 不静默）。"""
    if study is None:
        return None, "study 为 None（★ 需要先建/找到研究）"
    try:
        opts = study_options_of(study, family)
    except Exception as exc:                                   # noqa: BLE001
        return None, "取 options 失败（family=%s）：%s" % (family, str(exc)[:200])
    if opts is None:
        return None, ("study 上取不到 family=%s 的设置对象 ⇒ "
                      "★ 该研究类型可能不是这一族（★ 见 list_setter_summary 的族清单）" % family)
    return opts, None


def configure_static_solver_report(study, family: str = "ICWStaticStudyOptions",
                                   free_body_force=None, contact_penalty=None,
                                   reference_pressure=None) -> dict:
    """★ **静力求解器设置**：★ 从 `study` 取 options ⇒ 调 `configure_static_solver`。

    ★ kwargs 里**只传非 None 的**（★ 底层用 `None` 表示"不改"，★ 所以过滤掉 None 是**保持语义**）。
    """
    opts, err = _options_from_study(study, family)
    if err:
        return {"ok": False, "family": family, "error": err}
    #: ★ 显式列出（★ 与底层形参一致 ⇒ `check_param_binding.py` 可验 + **形参即文档**）
    kw = {k: v for k, v in (("free_body_force", free_body_force),
                            ("contact_penalty", contact_penalty),
                            ("reference_pressure", reference_pressure)) if v is not None}
    try:
        r = configure_static_solver(opts, **kw)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "family": family, "changed": sorted(kw),
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    #: ★★ 2026-10-01（轮 347）**"nothing to change" 不是失败** ——
    #:   ★ `set_options` 在 `kw` 为空时回 `{}`，而 `bool({})` 是 `False` ⇒
    #:   ★★ 旧写法把「你没给参数」报成 `ok=False`，**让调用方以为能力坏了**（★ 我第一遍就这么误判）。
    #:   ⚠ **本行必须在 `except` 块之外**（★ 我第一次按**行号**批量插入，把它插进了 `except` 里面 ⇒
    #:     正常路径落空、函数回 `None`）—— ★ 与事实 61 同型：**按行插入会挤坏控制流**。
    if not kw:
        return {"ok": True, "family": family, "changed": [], "returned": r,
                "note": "没有要改的项（★ 未传任何参数并非失败）"}
    return {"ok": bool(r), "family": family, "changed": sorted(kw), "returned": r}


def configure_frequency_solver_report(study, family: str = "ICWFrequencyStudyOptions",
                                      decouple=None, reference_pressure=None) -> dict:
    """★ **频率求解器设置**（★ 同族手法）。"""
    opts, err = _options_from_study(study, family)
    if err:
        return {"ok": False, "family": family, "error": err}
    kw = {k: v for k, v in (("decouple", decouple),
                            ("reference_pressure", reference_pressure)) if v is not None}
    try:
        r = configure_frequency_solver(opts, **kw)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "family": family, "changed": sorted(kw),
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    #: ★★ 同 `configure_static_solver_report`（轮 347）：★ **空 `kw` ⇒ 不是失败**（★ 在 `except` 之外）。
    if not kw:
        return {"ok": True, "family": family, "changed": [], "returned": r,
                "note": "没有要改的项（★ 未传任何参数并非失败）"}
    return {"ok": bool(r), "family": family, "changed": sorted(kw), "returned": r}


def configure_buckling_solver_report(study, family: str = "ICWBucklingStudyOptions",
                                     modes=None, positive_only=None, reference_pressure=None) -> dict:
    """★ **屈曲求解器设置**（★ 同族手法）。"""
    opts, err = _options_from_study(study, family)
    if err:
        return {"ok": False, "family": family, "error": err}
    kw = {k: v for k, v in (("modes", modes),
                            ("positive_only", positive_only),
                            ("reference_pressure", reference_pressure)) if v is not None}
    try:
        r = configure_buckling_solver(opts, **kw)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "family": family, "changed": sorted(kw),
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    #: ★★ 同 `configure_static_solver_report`（轮 347）：★ **空 `kw` ⇒ 不是失败**（★ 在 `except` 之外）。
    if not kw:
        return {"ok": True, "family": family, "changed": [], "returned": r,
                "note": "没有要改的项（★ 未传任何参数并非失败）"}
    return {"ok": bool(r), "family": family, "changed": sorted(kw), "returned": r}


def set_study_option_report(study, family: str, name: str, value) -> dict:
    """★ **按登记表设一个求解器选项**（★ 从 `study` 取 options）。

    ⚠ `set_option` 对**未登记的族名/选项名**抛 `KeyError`（★ **不静默忽略**）——
      ★ 包装里如实回传（★ 于是调用方能看出"名字写错了"而不是"设了但没生效"）。
    """
    opts, err = _options_from_study(study, family)
    if err:
        return {"ok": False, "family": family, "name": name, "error": err}
    try:
        #: dispatch-fwd: upstream set_study_option_report tool-only 二级转发：**仅由工具层按名注册**（tool_specs_batch37.py 的 function=），name 来自工具实参
        r = set_option(opts, family, name, value)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "family": family, "name": name,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    return {"ok": bool(r), "family": family, "name": name, "value": value, "returned": r}


def set_study_options_report(study, family: str, values: dict) -> dict:
    """★ **一次设一组求解器选项**（★ 从 `study` 取 options）。"""
    opts, err = _options_from_study(study, family)
    if err:
        return {"ok": False, "family": family, "error": err}
    try:
        r = set_options(opts, family, values)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "family": family,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    return {"ok": bool(r) if isinstance(r, bool) else True, "family": family,
            "asked": sorted(values), "readback": r}
