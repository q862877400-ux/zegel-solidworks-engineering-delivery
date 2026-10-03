"""SolidWorks 阵列特征：线性阵列 / 沿曲线阵列 的 FeatureData 装配。

能力域
    域 3 · 零件特征（阵列是最高频的零件特征之一）

补齐的接口族
------------
    ILinearPatternFeatureData      60 成员（3% → 本模块覆盖主要 setter）
    ICurveDrivenPatternFeatureData 44 成员（5% → 本模块覆盖主要 setter）

与既有代码的关系
----------------
上游 ``scripts/sw_part.py`` 用的是 ``IFeatureManager.FeaturePattern2`` 这类
**旧式方法入口**。本模块走的是**现代 FeatureData 路径**：
``IFeatureManager.CreateDefinition(swFmLinearPattern / swFmCurveDrivenPattern)``
→ 设属性 → ``CreateFeature``。两条路径官方并存，本模块补的是后者。

⚠ 两个 FeatureData 的形状**不一样**，本模块刻意分开封装、不合并：
  · ``ILinearPatternFeatureData`` 用 **D1*/D2* 前缀**（轴、间距、总数、
    端条件、端参考、种子参考）
  · ``ICurveDrivenPatternFeatureData`` 用 **D1Direction / D1Spacing /
    D1IsEqualSpaced / D1ReverseDirection** 这一套，没有「总数」概念
  ⇒ 把它们硬塞进一个「通用 setter」只会掩盖差异。

⚑ 两个族共有的「选区事务」
----------------------------
两者的 ``AccessSelections(Object, Object)`` 都是 **2 参**，
且都有配套的 ``ReleaseSelectionAccess()``（**零参**）。
⇒ 本模块所有装配函数一律 ``Access → 设 → finally Release``。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt
      → ILinearPatternFeatureData 段 + ICurveDrivenPatternFeatureData 段
      —— 对 SolidWorks.Interop.sldworks.dll 的**纯元数据反射**
         （AGENTS.md §四.1③）。
    枚举取自 ``C:\\swapi\\enums\\swPatternEndCondition_e.md``。

⚠ **不提供** ``I*`` 前缀的成员（IAccessSelections / ISetPatternFaceArray /
  IGetSkippedItemArray …）—— 那些是 COM 内部分发口，不该给调用方。
⚠ 端条件枚举官方只有 2 项（见 SWS_PATTERN_END_CONDITIONS）；
  「总数 / 间距」是两套互斥的终态条件，本模块**只透传官方枚举**，
  不替 SolidWorks 决定两者的一致性。

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
# 文件:   scripts/sw_pattern.py —— 本文件自身
# 定位:   模块导出清单与枚举表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "SWS_PATTERN_END_CONDITIONS",
    "SWS_PATTERN_ELEMENT_SELECTION",
    "SWS_FEATURES_TO_PATTERN",
    "PATTERN_MEMBER_ARITY",
    "edit_selection",
    "configure_linear_pattern",
    "configure_curve_driven_pattern",
    "read_pattern_element",
    "collect_pattern_evidence",
]

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举（C:\swapi 收录的 swconst）
# 文件:   C:\swapi\enums\swPatternEndCondition_e.md
#         C:\swapi\enums\swPatternElementSelection_e.md
#         C:\swapi\enums\swFeaturesToPatternType_e.md
# 定位:   阵列的端条件 / 阵列元素 / 可阵列特征类型。
# 取值:   swPatternEndCondition_e **全量照录**（官方只有 2 项）。
# ⚑ 查证过程: 我先按印象写 `swPatternObjectType_e` / `swPatternDirection_e`，
#   sw_know 两者都报无 ⇒ 真实名字是 swPatternElementSelection_e /
#   swFeaturesToPatternType_e。**方向**方向的枚举名本机查不到
#   （`sw_know find PatternDirection` 只返回 IFillPatternFeatureData 的两个成员，
#    不是枚举）⇒ 方向参数一律 int 透传，不臆造枚举名。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
SWS_PATTERN_END_CONDITIONS = {
    "spacing_and_instances": 0,   # swPatternEndCondition_SpacingAndInstances
    "up_to_reference": 1,         # swPatternEndCondition_UpToReference
}

SWS_PATTERN_ELEMENT_SELECTION = {
    "point": 0,
    "edge": 1,
    "face": 2,
    "feature": 3,
    "body": 4,
    "sketch": 5,
    "curve": 6,
}

SWS_FEATURES_TO_PATTERN = {
    "solid": 1,
    "surface": 2,
    "sketch": 3,
    "curve": 4,
    "trim": 5,
    "dressup": 6,
    "apex": 7,
    "refpoint": 8,
}

#: 两个 FeatureData 共有的「方法型」成员的实参个数
#: （属性型成员不进这张表 —— 它们由下面的显式 setter 负责）
PATTERN_MEMBER_ARITY: dict[str, int] = {
    "AccessSelections": 2,
    "ReleaseSelectionAccess": 0,
    "GetD1AxisType": 0,
    "GetD2AxisType": 0,
    "GetTransform": 1,
    "GetPatternBodyCount": 0,
    "GetPatternFaceCount": 0,
    "GetPatternFeatureCount": 0,
    "GetSkippedItemCount": 0,
    "SetFeatureScope": 3,
    "SetInstanceToVaryOptions": 1,
    "GetInstanceToVaryOptions": 0,
    "IsDirection2Specified": 0,
}


def _checked(target, member: str, *args):
    """按签名表校核实参个数，通过后才发起调用（开发期护栏）。"""
    expected = PATTERN_MEMBER_ARITY.get(member)
    if expected is not None and expected != len(args):
        raise ValueError(
            f"{member} 官方签名是 {expected} 个实参（不含末尾 by-ref 出参），"
            f"本次调用给了 {len(args)} 个"
        )
    if target is None:
        raise ValueError("data 为 None：须先由 IFeatureManager.CreateDefinition 取得")
    return get_com_member(target, member, *args)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
#           → ILinearPatternFeatureData 段 + ICurveDrivenPatternFeatureData 段
# 定位:   两个族的**选区事务**。官方签名逐条照抄（**完全同形**）：
#     Boolean AccessSelections(Object Model, Object SelectionData)  ← **2 参**
#     Void    ReleaseSelectionAccess()                              ← **零参**
# ⚠ 与本项目其它 FeatureData 一致：AccessSelections 是 **2 参**，
#   第 2 参（SelectionData）语义未查到 → 传 None 并在此标注。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
class _SelectionAccess:
    """``Access → 设 → finally Release`` 的上下文管理器。

    异常路径也释放选区接管，避免事务悬着 —— 与 sw_simulation_loadprops
    的 ``edit_transaction`` 同一形状。
    """

    def __init__(self, data, model, what: str):
        self._data = data
        self._model = model
        self._what = what
        self._opened = False

    def __enter__(self):
        if self._data is None:
            raise ValueError(f"{self._what} 为 None")
        if self._model is None:
            raise ValueError("model 为 None：AccessSelections 的第 1 参需要它")
        _checked(self._data, "AccessSelections", self._model, None)
        self._opened = True
        return self._data

    def __exit__(self, exc_type, exc, tb):
        if self._opened:
            _checked(self._data, "ReleaseSelectionAccess")
        return False


def edit_selection(data, model, what: str = "FeatureData") -> _SelectionAccess:
    """取得选区事务上下文管理器。"""
    return _SelectionAccess(data, model, what)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）→ ILinearPatternFeatureData 段
# 定位:   线性阵列的属性装配。官方 setter 逐条照抄（**全部是属性**）：
#     set_D1Axis(Object) / set_D2Axis(Object)              ← 方向对象
#     set_D1Spacing(Double) / set_D2Spacing(Double)        ← 间距
#     set_D1TotalInstances(Int32) / set_D2TotalInstances(Int32)
#     set_D1EndCondition(Int32) / set_D2EndCondition(Int32)  ← swPatternEndCondition_e
#     set_D1EndUseSpacing(Boolean) / set_D2EndUseSpacing(Boolean)
#     set_D1EndUseSeedReference(Boolean) / set_D2EndUseSeedReference(Boolean)
#     set_D1EndSeedReference(Object) / set_D2EndSeedReference(Object)
#     set_D1EndRefOffset(Double) / set_D2EndRefOffset(Double)
#     set_D1EndRefReverseOffset(Boolean) / set_D2EndRefReverseOffset(Boolean)
#     set_D1ReverseDirection(Boolean) / set_D2ReverseDirection(Boolean)
#     set_D2PatternSeedOnly(Boolean)
#     set_GeometryPattern(Boolean) / set_BodyPattern(Boolean)
#     set_InstancesToVary(Boolean) / set_VarySketch(Boolean)
#     set_PropagateVisualProperty(Boolean)
#     set_PatternFaceArray(Object) / set_PatternFeatureArray(Object) /
#          set_PatternBodyArray(Object) / set_SkippedItemArray(Object)
#     set_StructureSystemToPatternArray(Object)
# ⚠ 「方向」的**枚举类型**本机查不到（D1Axis/D2Axis 的对象类型是
#   swPatternObjectType_e 之类，但该枚举名查不到）⇒ 只透传对象，不解释。
# ⚠ 端条件与总数/间距**互斥性**由 SolidWorks 判定，本模块只透传，
#   不在前端做一致性校验（官方没给规则，不臆造）。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def configure_linear_pattern(
    data,
    model,
    *,
    d1_axis=None,
    d1_spacing: float | None = None,
    d1_total_instances: int | None = None,
    d1_end_condition: int | None = None,
    d1_reverse: bool | None = None,
    d1_end_use_spacing: bool | None = None,
    d1_end_seed_reference=None,
    d1_end_use_seed_reference: bool | None = None,
    d1_end_ref_offset: float | None = None,
    d1_end_ref_reverse_offset: bool | None = None,
    d2_axis=None,
    d2_spacing: float | None = None,
    d2_total_instances: int | None = None,
    d2_end_condition: int | None = None,
    d2_reverse: bool | None = None,
    d2_pattern_seed_only: bool | None = None,
    geometry_pattern: bool | None = None,
    body_pattern: bool | None = None,
    instances_to_vary: bool | None = None,
    vary_sketch: bool | None = None,
) -> dict[str, Any]:
    """装配线性阵列（自动包在选区事务里）。返回实际设置了的项。"""
    applied: dict[str, Any] = {}
    with edit_selection(data, model, "ILinearPatternFeatureData"):
        if d1_axis is not None:
            set_com_member(data, "D1Axis", d1_axis)
            applied["D1Axis"] = d1_axis
        if d1_spacing is not None:
            set_com_member(data, "D1Spacing", float(d1_spacing))
            applied["D1Spacing"] = float(d1_spacing)
        if d1_total_instances is not None:
            set_com_member(data, "D1TotalInstances", int(d1_total_instances))
            applied["D1TotalInstances"] = int(d1_total_instances)
        if d1_end_condition is not None:
            set_com_member(data, "D1EndCondition", int(d1_end_condition))
            applied["D1EndCondition"] = int(d1_end_condition)
        if d1_reverse is not None:
            set_com_member(data, "D1ReverseDirection", bool(d1_reverse))
            applied["D1ReverseDirection"] = bool(d1_reverse)
        if d1_end_use_spacing is not None:
            set_com_member(data, "D1EndUseSpacing", bool(d1_end_use_spacing))
            applied["D1EndUseSpacing"] = bool(d1_end_use_spacing)
        if d1_end_seed_reference is not None:
            set_com_member(data, "D1EndSeedReference", d1_end_seed_reference)
            applied["D1EndSeedReference"] = d1_end_seed_reference
        if d1_end_use_seed_reference is not None:
            set_com_member(data, "D1EndUseSeedReference",
                           bool(d1_end_use_seed_reference))
            applied["D1EndUseSeedReference"] = bool(d1_end_use_seed_reference)
        if d1_end_ref_offset is not None:
            set_com_member(data, "D1EndRefOffset", float(d1_end_ref_offset))
            applied["D1EndRefOffset"] = float(d1_end_ref_offset)
        if d1_end_ref_reverse_offset is not None:
            set_com_member(data, "D1EndRefReverseOffset",
                           bool(d1_end_ref_reverse_offset))
            applied["D1EndRefReverseOffset"] = bool(d1_end_ref_reverse_offset)
        if d2_axis is not None:
            set_com_member(data, "D2Axis", d2_axis)
            applied["D2Axis"] = d2_axis
        if d2_spacing is not None:
            set_com_member(data, "D2Spacing", float(d2_spacing))
            applied["D2Spacing"] = float(d2_spacing)
        if d2_total_instances is not None:
            set_com_member(data, "D2TotalInstances", int(d2_total_instances))
            applied["D2TotalInstances"] = int(d2_total_instances)
        if d2_end_condition is not None:
            set_com_member(data, "D2EndCondition", int(d2_end_condition))
            applied["D2EndCondition"] = int(d2_end_condition)
        if d2_reverse is not None:
            set_com_member(data, "D2ReverseDirection", bool(d2_reverse))
            applied["D2ReverseDirection"] = bool(d2_reverse)
        if d2_pattern_seed_only is not None:
            set_com_member(data, "D2PatternSeedOnly", bool(d2_pattern_seed_only))
            applied["D2PatternSeedOnly"] = bool(d2_pattern_seed_only)
        if geometry_pattern is not None:
            set_com_member(data, "GeometryPattern", bool(geometry_pattern))
            applied["GeometryPattern"] = bool(geometry_pattern)
        if body_pattern is not None:
            set_com_member(data, "BodyPattern", bool(body_pattern))
            applied["BodyPattern"] = bool(body_pattern)
        if instances_to_vary is not None:
            set_com_member(data, "InstancesToVary", bool(instances_to_vary))
            applied["InstancesToVary"] = bool(instances_to_vary)
        if vary_sketch is not None:
            set_com_member(data, "VarySketch", bool(vary_sketch))
            applied["VarySketch"] = bool(vary_sketch)
    return applied


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）→ ICurveDrivenPatternFeatureData 段
# 定位:   沿曲线阵列的属性装配。官方 setter 逐条照抄（**全部是属性**）：
#     set_D1Direction(Object) / set_D1FaceNormal(Object)
#     set_D1Spacing(Double) / set_D2Spacing(Double)
#     set_D1IsEqualSpaced(Boolean) / set_D2IsEqualSpaced(Boolean)
#     set_D1ReverseDirection(Boolean) / set_D2ReverseDirection(Boolean)
#     set_D2Direction(Object) / set_Dir2Specified(Boolean)
#     set_D2PatternSeedOnly(Boolean)
#     set_GeometryPattern(Boolean) / set_BodyPattern(Boolean)
#     set_VarySketch(Boolean) / set_PropagateVisualProperty(Boolean)
#     set_PatternFaceArray / PatternFeatureArray / PatternBodyArray /
#          SkippedItemArray (Object)
# ⚑ 与线性阵列的**形状差异**（本模块刻意不合并两族）：
#   沿曲线阵列**没有**「总数」「端条件」「种子参考」这一套，
#   取而代之的是「等间距 IsEqualSpaced」。
# ⚠ `Dir2Specified` 的名字与 `IsDirection2Specified()` 方法**同义**，
#   反射里两者都在（一个是属性、一个是方法）⇒ 本模块**只封属性**，
#   方法留在 PATTERN_MEMBER_ARITY 里不重复封装。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def configure_curve_driven_pattern(
    data,
    model,
    *,
    d1_direction=None,
    d1_face_normal=None,
    d1_spacing: float | None = None,
    d1_is_equal_spaced: bool | None = None,
    d1_reverse: bool | None = None,
    d2_direction=None,
    d2_spacing: float | None = None,
    d2_is_equal_spaced: bool | None = None,
    d2_reverse: bool | None = None,
    d2_pattern_seed_only: bool | None = None,
    geometry_pattern: bool | None = None,
    body_pattern: bool | None = None,
    vary_sketch: bool | None = None,
) -> dict[str, Any]:
    """装配沿曲线阵列（自动包在选区事务里）。返回实际设置了的项。"""
    applied: dict[str, Any] = {}
    with edit_selection(data, model, "ICurveDrivenPatternFeatureData"):
        if d1_direction is not None:
            set_com_member(data, "D1Direction", d1_direction)
            applied["D1Direction"] = d1_direction
        if d1_face_normal is not None:
            set_com_member(data, "D1FaceNormal", d1_face_normal)
            applied["D1FaceNormal"] = d1_face_normal
        if d1_spacing is not None:
            set_com_member(data, "D1Spacing", float(d1_spacing))
            applied["D1Spacing"] = float(d1_spacing)
        if d1_is_equal_spaced is not None:
            set_com_member(data, "D1IsEqualSpaced", bool(d1_is_equal_spaced))
            applied["D1IsEqualSpaced"] = bool(d1_is_equal_spaced)
        if d1_reverse is not None:
            set_com_member(data, "D1ReverseDirection", bool(d1_reverse))
            applied["D1ReverseDirection"] = bool(d1_reverse)
        if d2_direction is not None:
            set_com_member(data, "D2Direction", d2_direction)
            applied["D2Direction"] = d2_direction
        if d2_spacing is not None:
            set_com_member(data, "D2Spacing", float(d2_spacing))
            applied["D2Spacing"] = float(d2_spacing)
        if d2_is_equal_spaced is not None:
            set_com_member(data, "D2IsEqualSpaced", bool(d2_is_equal_spaced))
            applied["D2IsEqualSpaced"] = bool(d2_is_equal_spaced)
        if d2_reverse is not None:
            set_com_member(data, "D2ReverseDirection", bool(d2_reverse))
            applied["D2ReverseDirection"] = bool(d2_reverse)
        if d2_pattern_seed_only is not None:
            set_com_member(data, "D2PatternSeedOnly", bool(d2_pattern_seed_only))
            applied["D2PatternSeedOnly"] = bool(d2_pattern_seed_only)
        if geometry_pattern is not None:
            set_com_member(data, "GeometryPattern", bool(geometry_pattern))
            applied["GeometryPattern"] = bool(geometry_pattern)
        if body_pattern is not None:
            set_com_member(data, "BodyPattern", bool(body_pattern))
            applied["BodyPattern"] = bool(body_pattern)
        if vary_sketch is not None:
            set_com_member(data, "VarySketch", bool(vary_sketch))
            applied["VarySketch"] = bool(vary_sketch)
    return applied


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_simulation_study.py::collect_study_evidence）
# 定位:   阵列状态证据回读，沿用「只取已核实成员」的写法。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def read_pattern_element(data) -> dict[str, Any]:
    """回读阵列当前的元素设置。"""
    if data is None:
        raise ValueError("data 为 None")
    return {
        "pattern_element": int(get_com_member(data, "PatternElement") or -1),
        "geometry_pattern": bool(get_com_member(data, "GeometryPattern")),
        "body_pattern": bool(get_com_member(data, "BodyPattern")),
        "vary_sketch": bool(get_com_member(data, "VarySketch")),
        "propagate_visual_property": bool(
            get_com_member(data, "PropagateVisualProperty")),
        "feature_scope": bool(get_com_member(data, "FeatureScope")),
    }


def collect_pattern_evidence(data) -> dict[str, Any]:
    """回读阵列的计数类信息（两族共有）。"""
    if data is None:
        raise ValueError("data 为 None")
    return {
        "pattern_body_count": int(_checked(data, "GetPatternBodyCount") or 0),
        "pattern_face_count": int(_checked(data, "GetPatternFaceCount") or 0),
        "pattern_feature_count": int(_checked(data, "GetPatternFeatureCount") or 0),
        "skipped_item_count": int(_checked(data, "GetSkippedItemCount") or 0),
    }
