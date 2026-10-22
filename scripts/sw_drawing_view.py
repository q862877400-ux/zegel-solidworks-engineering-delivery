"""SolidWorks 工程图视图：IView 成员登记表 + 通用访问器。

能力域
    域 9 · 工程图

⚠⚑ 本模块为什么是「登记表」而不是 207 个手写函数
-----------------------------------------------
``IView`` 是全库**最大的单个接口族**。对 ``iface_sldworks.txt`` 逐行解析
（不用正则切段 —— 前瞻会提前截断）的实测构成：

    原始成员                  496
    ├ I 前缀内部分发口        134   （27%，COM 运行时用，不给调用方）
    ├ 属性（get_/set_）         61
    └ 方法签名                301
        └ 编号历史变体         94   （X2 / X3 形态）
    ── 归约到基础名后 = **207 个不同能力**

207 个手写函数代码量大、单位信息量低；而且其中大量是
``GetXxxCount`` / ``GetXxx`` 的固定配对（前 40 个能力里占了 20 个）。

⇒ 与 ``sw_simulation_study_options.py`` 同一套做法：
  1. **登记表** ``VIEW_MEMBER_ARITY``：207 个能力名 → 实参个数。
     机械生成（``tools/gen_iview_registry.py``），
     **不手抄**，可被测试逐条对回反射清单。
  2. **受登记表约束的通用访问器** :func:`call_view` —— 传成员名，
     先查表校核实参个数，通过才发起调用。
  3. 少量高频能力做显式包装（:func:`get_view_name` / :func:`set_view_scale` 等）。

⚠ **登记表只说「这个名字存在、参数个数对得上」，不解释它干什么。**
  官方 CHM 对 IView 的语义说明是按「方法页」分散的，
  逐条抄进注释不现实也不可靠 ⇒ 需要语义请查官方 API 文档对应方法页。

⚠ **编号变体的取舍**：官方 ``GetFirstView`` / ``GetFirstView2`` /
  ``GetFirstView3`` 这类变体，官方未说明差别。本模块的登记表把它们
  **折叠到基础名**并保留**实参最多的那一条** ⇒ 调用时传基础名。
  这是一��**明确声明的取舍**，不是「它们等价」。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt → IView 段
      —— 对 SolidWorks.Interop.sldworks.dll 的纯元数据反射
         （AGENTS.md §四.1③）。
    登记表数据：``D:\\AI\\SW\\_raw\\iview_members.json``（由上述脚本生成）。

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游与既有模式的写法**发展而来）。
# 文件:   scripts/sw_drawing_view.py —— 本文件（**轮 145 的命名迁移**）。
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

from typing import Any

try:
    from .sw_connect import get_com_member, call_com_member, set_com_member
except ImportError:
    #: ★★★ 2026-10-03（轮 470）**这一支原先缺 `set_com_member`** ——
    #:   ★ 它那一行是 `from sw_connect import get_com_member, call_com_member`，
    #:     **紧接着**就是 `# ── 来源 ──` 那条注释 ⇒ ★★ 我最初批量补名字时把它**追加到了注释之后**
    #:     （`…call_com_member# ── 来源 ──, set_com_member`）⇒ **名字掉进注释里、从未生效** ⚠
    #:   ★★ 而那意味着：★ 本模块被**顶层载入**时（脚本 / 探针 / pytest 的 prepend 模式），
    #:     `set_view_scale_verified` 里那几处写会 `NameError` —— ★ **只在包内口径下才正常**。
    #:   ★ 实测（轮 470）：16 个用 `set_com_member` 的模块里，**只有这一个**在顶层口径下取不到它。
    #:   ★ 修法：把它**插在注释之前**（★ 与另外 15 个一致）✓
    from sw_connect import get_com_member, call_com_member, set_com_member
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_drawing_view.py —— 本文件自身
# 定位:   模块导出清单与成员登记表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方函数另附更精确的来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "VIEW_MEMBER_ARITY",
    "VIEW_PROPERTY_NAMES",
    "call_view",
    "call_view_no_args",
    "get_view_scale",
    "set_view_scale",
    "get_view_name",
    "get_first_view",
    "get_next_view",
    "get_annotation_count",
    "get_annotations",
    "get_visible_component_count",
    "get_scale_decimal",
    "collect_view_evidence",
]
#: IView 能力登记表：{能力名: 实参个数}。机械生成，不手抄。
# ⚠ 编号变体已折叠到基础名（保留实参最多的那一条）。
#: arity-reflect: byref=excluded
VIEW_MEMBER_ARITY: dict[str, int] = {
    'AlignDrawingView': 1,
    'AlignHorizontalTo': 1,
    'AlignVerticalTo': 1,
    'AlignWithView': 2,
    'AutoInsertCenterMarks2': 10,
    'CreateViewArrow': 2,
    'Crop2': 3,
    'EnumHiddenComponents': 0,
    'EnumSectionLines2': 1,
    'GetAlignment': 0,
    'GetAnnotationCount': 0,
    'GetAnnotations': 0,
    'GetAnnotationsByType': 1,
    'GetArcCount': 0,
    'GetArcs': 0,
    'GetBaseView': 0,
    'GetBendLineCount': 0,
    'GetBendLines': 0,
    'GetBendNoteAttributeString': 1,
    'GetBendNoteTextFormat': 0,
    'GetBodiesCount': 0,
    'GetBomTable': 0,
    'GetBreakLineCount': 0,
    'GetBreakLineInfo': 0,
    'GetBreakLines': 0,
    'GetBreakOutSectionCount': 0,
    'GetBreakOutSections': 0,
    'GetCThreadCount': 0,
    'GetCThreadQuality': 0,
    'GetCThreads': 0,
    'GetCenterLineCount': 0,
    'GetCenterLineSketch': 0,
    'GetCenterLines': 0,
    'GetCenterMarkCount2': 0,
    'GetCenterMarkInfo': 0,
    'GetCenterMarks': 0,
    'GetCorresponding': 1,
    'GetCorrespondingEntity': 1,
    'GetDatumOriginCount': 0,
    'GetDatumOrigins': 0,
    'GetDatumPoints': 0,
    'GetDatumPointsCount': 0,
    'GetDatumTagCount': 0,
    'GetDatumTags': 0,
    'GetDatumTargetSymCount': 0,
    'GetDatumTargetSyms': 0,
    'GetDependentViewCount': 2,
    'GetDependentViews': 2,
    'GetDesignTableExtent': 0,
    'GetDetail': 0,
    'GetDetailCircleCount2': 0,
    'GetDetailCircleInfo': 0,
    'GetDetailCircleStrings': 0,
    'GetDetailCircles': 0,
    'GetDimensionCount': 0,
    'GetDimensionDisplayInfo': 0,
    'GetDimensionDisplayInfoSize': 0,
    'GetDimensionDisplayString5': 0,
    'GetDimensionIds': 0,
    'GetDimensionInfo': 0,
    'GetDimensionString': 0,
    'GetDisplayData': 0,
    'GetDisplayDimensionCount': 0,
    'GetDisplayDimensions': 0,
    'GetDisplayEdgesInShadedMode': 0,
    'GetDisplayMode': 0,
    'GetDisplayTangentEdges': 0,
    'GetDowelSymbolCount': 0,
    'GetDowelSymbols': 0,
    'GetEllipseCount': 0,
    'GetEllipses': 0,
    'GetFaceHatchCount': 0,
    'GetFaceHatches': 0,
    'GetFacettedHlrDisplay': 0,
    'GetFirstAnnotation': 0,
    'GetFirstBlockInstance': 0,
    'GetFirstCThread': 0,
    'GetFirstCenterLine': 0,
    'GetFirstCenterMark': 0,
    'GetFirstCenterOfMass': 0,
    'GetFirstCustomSymbol': 0,
    'GetFirstDatumOrigin': 0,
    'GetFirstDatumTag': 0,
    'GetFirstDatumTargetSym': 0,
    'GetFirstDisplayDimension': 0,
    'GetFirstDowelSymbol': 0,
    'GetFirstGTOL': 0,
    'GetFirstMultiJogLeader': 0,
    'GetFirstNote': 0,
    'GetFirstRevisionCloud': 0,
    'GetFirstSFSymbol': 0,
    'GetFirstTableAnnotation': 0,
    'GetFirstWeldBead': 0,
    'GetFirstWeldSymbol': 0,
    'GetGTolCount': 0,
    'GetGTols': 0,
    'GetHiddenComponents': 0,
    'GetHiddenEdgeCount': 0,
    'GetKeepLinkedToBOM': 0,
    'GetKeepLinkedToBOMName': 0,
    'GetLineCount2': 1,
    'GetLines4': 1,
    'GetMirrorViewOrientation': 0,
    'GetMultiJogLeaderCount': 0,
    'GetMultiJogLeaders': 0,
    'GetName2': 0,
    'GetNextView': 0,
    'GetNoteCount': 0,
    'GetNotes': 0,
    'GetOrientationName': 0,
    'GetOutline': 0,
    'GetParabolaCount': 0,
    'GetParabolas': 0,
    'GetPolyLineCount5': 1,
    'GetPolyLinesAndCurves': 1,
    'GetPolyLinesAndCurvesCount': 1,
    'GetPolylines6': 1,
    'GetProjectionArrow': 0,
    'GetProjectionLineCount': 0,
    'GetProjectionLines': 0,
    'GetReferencedModelName': 0,
    'GetRelatedTangentEdgeCount': 1,
    'GetRelatedTangentEdges': 1,
    'GetRevisionCloudCount': 0,
    'GetRevisionClouds': 0,
    'GetSFSymbolCount': 0,
    'GetSFSymbols': 0,
    'GetSMBoundaryBoxDisplayData': 0,
    'GetSection': 0,
    'GetSectionLineCount': 0,
    'GetSectionLineInfo': 0,
    'GetSectionLineStrings': 0,
    'GetSectionLines': 0,
    'GetSketch': 0,
    'GetSketchPictureCount': 0,
    'GetSketchPictures': 0,
    'GetSolidHatchCount': 0,
    'GetSolidHatchInfo': 0,
    'GetSplineCount': 0,
    'GetSplines': 0,
    'GetTableAnnotationCount': 0,
    'GetTableAnnotations': 0,
    'GetTemporaryAxes': 0,
    'GetTemporaryAxesCount': 0,
    'GetUniqueName': 0,
    'GetUseParentDisplayMode': 0,
    'GetUserPoints': 0,
    'GetUserPointsCount': 0,
    'GetViewXform': 0,
    'GetVisible': 0,
    'GetVisibleComponentCount': 0,
    'GetVisibleComponents': 0,
    'GetVisibleDrawingComponents': 0,
    'GetVisibleEntities': 2,
    'GetVisibleEntityCount': 2,
    'GetWeldBeadCount': 0,
    'GetWeldBeads': 0,
    'GetWeldSymbolCount': 0,
    'GetWeldSymbols': 0,
    'GetWitnessEntitiesCount': 0,
    'GetWitnessGeomInfo': 0,
    'GetXform': 0,
    'HasDesignTable': 0,
    'ImportAnnotations': 5,
    'InsertAlternateView': 1,
    'InsertBendTable': 6,
    'InsertBomTable6': 12,
    'InsertBreak3': 6,
    'InsertCutListPropertyNote': 3,
    'InsertHoleTable3': 9,
    'InsertPunchTable': 6,
    'InsertViewAsBlock': 2,
    'InsertWeldTable': 8,
    'InsertWeldmentTable': 6,
    'IsBroken': 0,
    'IsCropped': 0,
    'IsExploded': 0,
    'IsFlatPatternView': 0,
    'IsLightweight': 0,
    'IsModelBreakState': 0,
    'IsModelLoaded': 0,
    'IsModelOutOfDate': 0,
    'IsPerspectiveView': 0,
    'LoadModel': 0,
    'MergeBendTags': 2,
    'ModifyViewArrow': 2,
    'MoveViewArrow': 4,
    'RemoveAlignment': 0,
    'ReplaceViewWithBlock': 1,
    'ReplaceViewWithSketch': 0,
    'ResetSketchVisibility': 0,
    'SelectEntity': 2,
    'SetBendNoteTextFormat': 1,
    'SetDisplayMode4': 5,
    'SetDisplayTangentEdges': 1,
    'SetKeepLinkedToBOM': 2,
    'SetLightweightToResolved': 0,
    'SetMirrorViewOrientation': 2,
    'SetName2': 1,
    'SetResolvedToLightweight': 0,
    'SetViewPosition': 2,
    'SetVisible': 2,
    'SetXform': 1,
    'ShowExploded': 1,
    'ShowModelBreakState': 2,
    'UpdateViewDisplayGeometry': 0,
    'UseDefaultAlignment': 0,
}

#: IView 上的属性名（反射里是 get_/set_，**不是方法**）。
# ⚑ 它们的实参个数不在上面那张表里 —— 赋值是单参数、读取是零参。
VIEW_PROPERTY_NAMES: tuple[str, ...] = (
    'Angle',
    'Bodies',
    'BreakLineGap',
    'CropViewJaggedOutline',
    'CropViewJaggedShapeIntensity',
    'CropViewNoOutline',
    'DisableAutoUpdate',
    'DisplayState',
    'EmphasizeOutline',
    'FlipView',
    'FocusLocked',
    'HiddenEdges',
    'IPosition',
    'IScaleRatio',
    'LinkParentConfiguration',
    'ModelToViewTransform',
    'Name',
    'Position',
    'PositionLocked',
    'ProjectedDimensions',
    'ReferencedConfiguration',
    'ReferencedConfigurationID',
    'ReferencedDocument',
    'RootDrawingComponent',
    'RootDrawingComponent2',
    'ScaleDecimal',
    'ScaleHatchPattern',
    'ScaleRatio',
    'Sheet',
    'ShowSheetMetalBendNotes',
    'SuppressState',
    'Type',
    'UseParentScale',
    'UseSheetScale',
)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（发布门禁同款护栏）
# 文件:   scripts/sw_drawing_view.py —— 本文件自身
# 定位:   通用访问器 :func:`call_view` 的 arity 校核与调用。
# ⚠ 成员名与取值都由调用方给 ⇒ 静态 arity 审计**归因不到**（成员名是变量）。
#   对账靠 tests/test_sw_drawing_view_contract.py：把登记表逐条对回反射清单。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
#: dispatch-guard: exempt module-local
def call_view(view, member: str, *args):
    """按登记表校核实参个数，通过后调用该成员。

    :param member: VIEW_MEMBER_ARITY 里的能力名
    :raises KeyError: 名字不在登记表里（**不静默忽略**）
    :raises ValueError: 实参个数与登记表对不上（在**发起调用之前**就报）
    """
    if view is None:
        raise ValueError("view 为 None：须先由 IDrawingDoc/Sheet 取得 IView")
    expected = VIEW_MEMBER_ARITY.get(member)
    if expected is None:
        raise KeyError(
            f"IView 上没有名为 {member} 的能力（登记表共 "
            f"{len(VIEW_MEMBER_ARITY)} 项）。若它是属性或 I 前缀内部分发口，"
            f"请用对应的专用封装。"
        )
    if expected != len(args):
        raise ValueError(
            f"{member} 官方签名是 {expected} 个实参，本次调用给了 {len(args)} 个"
        )
    return get_com_member(view, member, *args)


def call_view_no_args(view, member: str):
    """调用零参成员（表格里绝大多数是这种）。"""
    #: dispatch-fwd: upstream call_view_no_args orphan 二级转发：本函数**全仓零引用**（真 orphan，见 output/orphan-capabilities.json）
    return call_view(view, member)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IView 段
# 定位:   下面几个是工程出图里最高频的视图操作。**全部逐条照抄反射签名**：
#     Double get_Scale() / set_Scale(Double)          ← **属性**
#     String get_Name()                               ← **属性**
#     View   GetFirstView()                           ← **零参**
#     View   GetNextView()                            ← **零参**
#     Int32  GetAnnotationCount()                     ← **零参**
#     Object GetAnnotations()                         ← **零参**
#     Int32  GetVisibleComponentCount()               ← **零参**
#     Int32  GetScaleDecimal()                        ← **零参**
#     Boolean OrientToward(View, Double, Double)      → 2
# ⚑ 前七项里除 `GetFirstView` / `GetNextView` 外都是**属性或零参**，
#   迟到绑定下加括号会 TypeError（AGENTS.md §六 事实 4）。
# ⚠ `OrientToward` 的后两个 Double 单位官方未说明 ⇒ 原样透传。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_view_name(view) -> str:
    """取视图名（★ **只用现行的 `GetName2`**；★ 取不到就报空串）。

    ★★★★ 2026-10-04（轮 110）**换到现行成员** —— 处置阶段 2 · T1 ✓
      ★ **官方逐字**（★ `C:\\swapi\\types\\IView\\Name.md`）：
        > ★ 「Obsolete. **Superseded by `IView::GetName2` and `IView::SetName2`**」✓
    ★★★★★ **2026-10-10（spec 256）订正：兜底已删。**
      ★ 本函数原先写「**先试 `GetName2`、再兜底废弃的 `Name`**」，并在 docstring 里断言
        「**兜底不能删**：老成员可能仍可调、两代都试最稳」——
      ★★ **那句已被推翻**：★ **真机**（SW **34.4.1**）在 **5 个视图**（★ 254 的 1 个伪视图 +
        255 造的 4 个视图，其中 **3 个真实模型视图**）上测得 `Name` == `GetName2` **全部相同**
        ⇒ ★ **两代不等价的风险已排除** ⇒ ★ **不再调用废弃成员**。
      ★★★ **行为变化（★ 如实记）**：★ 若 `GetName2` 抛异常 ⇒ ★ 现在报 **空串**（★ 原先会回落取 `Name`）。
        ★ 这是**有意的**：★ 失败就是**取不到名字**，★ **不换一个废弃成员再试**。
      ★★ **依据落点**：`specs/254-iview-name-routing/` · `specs/255-multi-view-drawing-evidence/` ·
        `specs/256-iview-name-routing-done/`（★ 判据 `tests/test_iview_name_routing_done.py`）。
    """
    if view is None:
        raise ValueError("view 为 None")
    try:
        got = get_com_member(view, "GetName2")
        if got:
            return str(got)
    except Exception:                                          # noqa: BLE001
        pass
    #: ★★★ spec 256：**不再回落调废弃的 `IView::Name`**（★ 同上，真机已证 `GetName2` 等价）。
    return ""


def get_first_view(drawing):
    """取图纸第一张视图。**零参**。"""
    if drawing is None:
        raise ValueError("drawing 为 None：须先取得 IDrawingDoc")
    return get_com_member(drawing, "GetFirstView")


def get_next_view(view):
    """取下一张视图。**零参**。"""
    if view is None:
        raise ValueError("view 为 None")
    return get_com_member(view, "GetNextView")


def get_annotation_count(view) -> int:
    """视图里的注释数。**零参**。"""
    if view is None:
        raise ValueError("view 为 None")
    return int(get_com_member(view, "GetAnnotationCount") or 0)


def get_annotations(view) -> list[Any]:
    """视图里的注释列表。**零参**，返回 SAFEARRAY。"""
    if view is None:
        raise ValueError("view 为 None")
    value = get_com_member(view, "GetAnnotations")
    if value is None:
        return []
    try:
        return list(value)
    except TypeError:
        return [value]


def get_visible_component_count(view) -> int:
    """视图里可见的零件数。**零参**。"""
    if view is None:
        raise ValueError("view 为 None")
    return int(get_com_member(view, "GetVisibleComponentCount") or 0)


def get_scale_decimal(view) -> int:
    """比例的小数位设置。⚑ 官方是**零参属性** ``ScaleDecimal``。

    ⚑⚑ **更正**：初稿调的是 ``GetScaleDecimal``，该成员在 ``IView`` 上**不存在** ——
    反射实测的真实成员是 ``ScaleDecimal``（零参属性），
    与同族的 ``ScaleRatio`` / ``UseSheetScale`` / ``UseParentScale`` 同形。
    由 scripts/audit_call_arity.py 全仓扫描的「查不到」一栏抓出。
    ⚠ 语义（位数？标志位？）官方未说明。
    """
    if view is None:
        raise ValueError("view 为 None")
    return int(call_com_member(view, "ScaleDecimal") or 0)


# ⚑⚑ **删掉了一个查不到的成员**：`get_orient_toward` 初稿调 ``IView.OrientToward(Object, Double, Double)``。
#   铁律 4 要求**两套官方源都查**：
#     ① 对 sldworks.dll 的纯元数据反射 —— **全程序集无此成员名**
#     ② CHM 全文检索 ``OrientToward`` —— **无结果**
#   ⇒ 按铁律 5「查不到就写查不到并停」，**删除该封装**，不拿相似名字蒙混。
#   IView 上真实的定向相关成员是（全部零参）：
#     ScaleDecimal / ScaleRatio / UseSheetScale / UseParentScale
#     GetOrientationName / GetMirrorViewOrientation
#     SetMirrorViewOrientation(Double, Double) → 2
#   ⚠ 要「转向另一个视图」，本机两套官方源都**查不到**对应成员名 ——
#     该能力**本轮标为查不到**，不编。


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_simulation_study.py::collect_study_evidence）
# 定位:   视图状态证据回读，沿用「只取已核实成员」的写法。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_view_evidence(view) -> dict[str, Any]:
    """回读工程图视图状态。"""
    if view is None:
        raise ValueError("view 为 None")
    return {
        "name": get_view_name(view),
        "scale": get_view_scale(view),
        "annotation_count": get_annotation_count(view),
        "visible_component_count": get_visible_component_count(view),
        "scale_decimal": get_scale_decimal(view),
        "rotation": float(get_com_member(view, "Rotation") or 0.0),
        "xform": get_com_member(view, "Xform") is not None,
    }


# ── 24h 计划 段 6 续（Spec Kit `160`）：**工程图视图读数的包装** ─────────────────────
# ★★★★ 为什么包一层（★ 第四次同法）：`sw_drawing_view` 的 12 个函数**全部吃一个 `view` 对象**
#   ⇒ ★★ 而工具层的入参只能是 `model`（★ 文档）⇒ ★ **所以要注入 `model` + 内部往下取 view**。
#   ★ 入口链：`model` → `get_first_view(drawing)` → `get_next_view(view)` → 逐个读。
#
# ★ 判据：★ ① **取视图链成功**（★ 一个视图都没有 ⇒ 如实报"这不是工程图 / 图里没视图"）；
#   ② ★ 每个视图的读数**如实回传**；③ ★ **按视图名查找失败时报出**已有的名字（★ 会列合法值）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_drawing_view.py —— 本段
# 定位:   段 6 续：让"工程图视图"从工具层可表达（★ 此前 12 个函数一个工具都没挂）。
# 官方依据: `IView` 族（★ Name / ScaleDecimal / GetAnnotationCount / GetVisibleComponent
#           Count /
#          SetScale）—— ★ 见 `scripts/sw_drawing_view.py` 的既有来源块
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面 4 个包装
# ─────────────────────────────────────────────────────────────────────────────


def _iter_views(model):
    """★ 遍历图纸上的视图（★ 取不到就回 `([], 原因)`）。"""
    try:
        require = getattr(__import__("scripts.sw_drawing_query", fromlist=["x"]), "require_drawing")
        require(model)                                          #: ★ 非工程图 ⇒ 它自己会抛（★ 不静默）
    except Exception as exc:                                   # noqa: BLE001
        return [], "不是工程图文档：%s" % str(exc)[:160]
    #: ★★★ 2026-10-01（轮 291）：**先向 `sw_drawing_query.list_views` 取名单** ——
    #:   它的 docstring 记着一条**真机实测的陷阱**：空图纸上 `GetFirstView()` 回的是**图纸本身**
    #:   （`Type == 1`、名字等于图纸名）⇒ 不排除就会列出**假视图**。
    #:   ★★ 所以本处不自己判陷阱，而是**先取已验证的名单**，再按名对上 view 对象。
    #: ★★ 2026-10-03（轮 470）：**统一导入口径**（★ 同 `sw_sketch.py` 那一处）——
    #:   本行原写 `from scripts.sw_drawing_query import …`（包内用绝对包路径）
    #:   ⇒ 与本模块别处的相对口径混用 ⇒ 可能出现同一模块两份实例。
    #:   ★ 改为相对优先、绝对回退。
    try:
        from .sw_drawing_query import list_views as _list_views
    except ImportError:                                        # 顶层载入（脚本 / 探针）
        from scripts.sw_drawing_query import list_views as _list_views
    try:
        _names = [str((_r or {}).get("name") or "") for _r in (_list_views(model) or [])]
    except Exception as exc:                                   # noqa: BLE001
        return [], "取视图清单失败：%s: %s" % (type(exc).__name__, str(exc)[:160])
    if not _names:
        return [], "图里没有视图（★ 图纸可能是空的）"
    try:
        v = get_first_view(model)
    except Exception as exc:                                   # noqa: BLE001
        return [], "取第一个视图失败：%s: %s" % (type(exc).__name__, str(exc)[:160])
    out, seen = [], 0
    while v is not None and seen < 200:                        #: ★ 上限防死循环
        out.append(v); seen += 1
        try:
            v = get_next_view(v)
        except Exception:                                      # noqa: BLE001
            break
    _picked = []
    for _o in out:
        try:
            if str(get_view_name(_o)) in _names: _picked.append(_o)
        except Exception:                                      # noqa: BLE001
            continue
    if not _picked:
        return [], "按名字没对上任何视图（★ 清单里有 %d 个）" % len(_names)
    return _picked, None


def list_drawing_views_report(model) -> dict:
    """★ **列出工程图的所有视图**（★ 名字 / 比例 / 注释数 / 可见件数）。"""
    views, err = _iter_views(model)
    if err:
        return {"ok": False, "error": err}
    rows = []
    for v in views:
        row = {}
        for key, fn in (("name", get_view_name), ("scale", get_view_scale),
                        ("scale_decimal", get_scale_decimal),
                        ("annotation_count", get_annotation_count),
                        ("visible_component_count", get_visible_component_count)):
            try:
                row[key] = fn(v)
            except Exception:                                  # noqa: BLE001
                row[key] = None
        rows.append(row)
    return {"ok": True, "count": len(rows), "views": rows}


def _find_view(model, view_name: str):
    views, err = _iter_views(model)
    if err:
        return None, err
    for v in views:
        try:
            if str(get_view_name(v)) == str(view_name):
                return v, None
        except Exception:                                      # noqa: BLE001
            continue
    names = []
    for v in views:
        try: names.append(str(get_view_name(v)))
        except Exception: names.append("?")
    return None, "没有名为 %r 的视图。★ 合法值：%s" % (view_name, names[:20])


def get_view_scale_report(model, view_name: str) -> dict:
    """★ **按视图名取比例**（★ 找不到就**列出合法值**）。"""
    v, err = _find_view(model, view_name)
    if err:
        return {"ok": False, "error": err}
    try:
        return {"ok": True, "view_name": str(view_name), "scale": get_view_scale(v),
                "scale_decimal": get_scale_decimal(v)}
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "view_name": str(view_name),
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:180])}


def set_view_scale_report(model, view_name: str, scale: float) -> dict:
    """★ **按视图名设比例并回读**（★ 改走真机验证过的赋值形态，见 `set_view_scale_verified`）。"""
    _v, _err = _find_view(model, view_name)
    if _err:
        return {"ok": False, "error": _err}
    _r = set_view_scale_verified(_v, float(scale))
    _r["view_name"] = str(view_name)
    return _r


def collect_view_evidence_report(model) -> dict:
    """★ **每个视图的完整证据**（★ 走 `collect_view_evidence`）。"""
    views, err = _iter_views(model)
    if err:
        return {"ok": False, "error": err}
    out = []
    for v in views:
        try:
            out.append(collect_view_evidence(v))
        except Exception as exc:                               # noqa: BLE001
            out.append({"error": "%s: %s" % (type(exc).__name__, str(exc)[:140])})
    return {"ok": True, "count": len(out), "evidence": out}


# ── 24h 计划 段 6 续（Spec Kit `161`）：**比例成员名的更正（`Scale` → `ScaleRatio`）** ────
# ★★★★★ 2026-10-01（轮 293）**真机抓到三处同类错**（而这是**三源互证**该抓的那种）：
#   · `get_view_scale` / `set_view_scale` 都调 **`Scale`** —— ★ **而 `IView` 上**没有那个成员****
#     （★ 真机表现：`AttributeError: <unknown>.Scale` ⇒ ★ **那是事实 36 的形态**）。
#   · ★★ 而**同文件的 `get_scale_decimal` 的 docstring 早就写着**：
#       「⚑⚑ **更正**：初稿调的是 `GetScaleDecimal`，该成员在 `IView` 上**不存在** ——
#        反射实测的真实成员是 `ScaleDecimal`（零参属性），★ **与同族的 `ScaleRatio` / `UseSheetScale` /
#        `UseParentScale` 同形**」⇒ ★★★ **即：真名 `ScaleRatio` 早就被记下，只是那两个函数没跟着改**。
#   · ★★★ **官方（`C:\swapi\types\IView\ScaleRatio.md`）**：
#       「Gets or sets the scale of the drawing view, **returning the results in ratio format (n:n)**」
#       · **Returns: Array of 2 doubles** · ★「This property and `IView::ScaleDecimal` contain
#       **the same information**, but use the value in a different way」
#     ⇒ ★★ **所以**：① 真名是 **`ScaleRatio`**；② 它回**两个 double**（★ 不是单个 float）。
#
# ★ 判据：★ **`ScaleRatio` 回 2 个数 ⇒ 比例 = 第 1 个 / 第 2 个**；★ 取不到就**如实抛**（★ 原样）。
# ★ ⚠ 本段**只更正成员名与取值形态**，★ **不改行为语义**（★ 不给默认值兜底）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_drawing_view.py —— 本段
# 定位:   段 6 续：把"视图比例"的成员名从**臆造的 `Scale`** 更正为官方真名 `ScaleRatio
#           `。
# 官方依据: `C:\swapi\types\IView\ScaleRatio.md`（★ 真名 + "Array of 2 doubles" + ratio 
#           语义）·
#          ★ 与 `ScaleDecimal` 同族（★ 本文件 docstring 里的那条已存在的更正经）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面 3 个函数
# ─────────────────────────────────────────────────────────────────────────────


def get_view_scale_ratio(view):
    """★ **取视图比例（官方形态：两个数）** —— `IView.ScaleRatio` ⇒ `Array of 2 doubles`。

    ★ 回 `(numerator, denominator)`；★ **取不到就抛**（★ 不兜底 —— 兜底会把"成员名错"盖成"比例是 0"）。
    """
    if view is None:
        raise ValueError("view 为 None")
    raw = call_com_member(view, "ScaleRatio")
    if raw is None:
        raise RuntimeError("IView.ScaleRatio 回 None（★ 本机取不到 ⇒ 别用 0 兜底）")
    try:
        vals = [float(x) for x in raw]
    except TypeError:
        vals = [float(raw)]
    if len(vals) >= 2 and vals[1]:
        return vals[0], vals[1]
    return (vals[0] if vals else None), None


def get_view_scale(view) -> float:
    """★ **取视图比例（便利形态：一个 float）** = `ScaleRatio` 的第 1 个 / 第 2 个。

    ⚑⚑ **2026-10-01 更正**：本函数原调 `Scale` —— ★ **那是臆造的成员名**（`IView` 上没有；
    ★ 真机报 `<unknown>.Scale`）。★ 官方真名是 **`ScaleRatio`**（★ 回两个 double）。
    """
    n, d = get_view_scale_ratio(view)
    if n is None:
        raise RuntimeError("ScaleRatio 不可用 ⇒ 比例取不到")
    return float(n) / float(d) if d else float(n)


def set_view_scale(view, scale: float) -> bool:
    """★ **设视图比例** —— 走官方真名 `IView.ScaleRatio`（★ 按 `n:1` 形态写两个数）。

    ⚑⚑ **2026-10-01 更正**：本函数原调 `Scale`（★ 同样是不存在的成员名）。
    ★★★★★ **2026-10-03（轮 467）修一条会说谎的路径** —— 起因是用户问
      「你的 B5 探针那种问题在我们项目里**有别的类似的存在吗**」。用
      `tools/scan_blind_criteria.py` 扫出来的答案：**有，就是本函数**。

    ★★★ **本函数原来的两处毛病（★ 都在同一行里）**：
      ```
      ① ★ 它走 `get_com_member(view, "ScaleRatio", (s, 1.0))` ——
         ★★ 而 `get_com_member(obj, name, *args)` 的语义是「取或调」：**有实参就一定调用**
         ⇒ ★ 它在一个 **tuple** 上"调用" ⇒ **必然 `TypeError: 'tuple' object is not callable`**。
         ⚑ ★ 而**项目早在轮 294 就查清了这件事**（见下方那段注释），
           ★★ 只是**没回来改这个函数** ⇒ ★ 于是它一直**必然失败**。
      ② ★★★ **而它 `return True`** —— 无条件说成功 ⇒
         ★ **任何调用方都会以为"设好了"**，★ 而视图比例**根本没变**。
      ```
    ★ 真机硬证据：`output/scale-ratio-probe.json`（`set_try.ok=false` + 那句 TypeError）·
      `output/set-view-scale-probe.json`（`before == after` 而 `ok=false`）✓

    ★★ **现在的行为**：走 `set_com_member`（属性赋值 —— 本仓真机验证过的唯一可行形态），
      然后**回读**，★ 只有**两个数真的变了**才回 `True`（★ 规则 6：不静默成功）。

    :raises RuntimeError: 写了但**回读没变** ⇒ ★ **明确失败**，不再假装成功。
    """
    if view is None:
        raise ValueError("view 为 None")
    #: ★ 直接走**同文件后面**那个带回读的实现（★ Python 运行时解析名字 ⇒ 前后顺序无妨）
    return bool(set_view_scale_verified(view, scale)["ok"])


# ── 24h 计划 段 6 续（Spec Kit `162`）：**设视图比例的正确形态** ──────────────────────
# ★★★★★ 2026-10-01（轮 294）真机把三件事一次查清：
#   ① ★ **`ScaleRatio` 回的是**比例的两个数**** —— 真机 `(1.0, 500.0)`（★ 即 **1:500**）·
#      而 `ScaleDecimal` 回 **`0.002`**（★ = 1/500）⇒ ★★ **官方那句** "contain the same information,
#      but use the value in a different way" **正是此意**（★ 一个给"两个数"、一个给"小数"）。
#   ② ★★★ **"写"失败的原因**：`get_com_member(v, "ScaleRatio", (2.0, 1.0))` 报
#      `TypeError: 'tuple' object is not callable` —— ★★ **因为 `get_com_member(obj, name, *args)`
#      的语义是「取或调」：有实参就**一定调用****（★ 于是它在"调用"一个 tuple）。
#      ⇒ ★★★ **正解是 `set_com_member(obj, name, value)`** —— 它的 docstring 写着
#        「设置 COM 成员的**唯一被真机验证通过的形态**：**属性赋值**」。
#   ③ ★ **`UseSheetScale` 真机回 `True`** ⇒ ★★ **该视图**跟随图纸比例**** ——
#      ⇒ ★ **所以"设视图比例"之前要先把"跟随图纸"关掉**（★ 否则设了也可能被图纸覆盖）。
#
# ★ 判据：★ **设完**必须回读**，★ 并判"两个数真的变了"**（★ 规则 6 的精神 —— 不静默成功）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_drawing_view.py —— 本段
# 定位:   段 6 续：把"设视图比例"从**取值 helper** 改到**赋值 helper**，并处理 `UseShe
#           etScale` 前置。
# 官方依据: `C:\swapi\types\IView\ScaleRatio.md`（★ ratio 形态 / Array of 2 doubles）·
#          `UseSheetScale.md`（★ 布尔：视图是否跟随图纸比例）·
#          ★ 本项目 `sw_connect.set_com_member` 的真机结论（"唯一被验证通过的形态：属性赋值"）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面 2 个函数
# ─────────────────────────────────────────────────────────────────────────────


def set_view_scale_verified(view, scale: float) -> dict:
    """★ **设视图比例（走真机验证过的赋值形态）+ 回读核对**。

    ★ 步骤：① **先把 `UseSheetScale` 关掉**（★ 否则视图跟随图纸，设了也可能无效）；
      ② ★ 用 `set_com_member(view, "ScaleRatio", (scale, 1.0))`（★ **不是** `get_com_member` 带参）；
      ③ ★ **回读**并判"两个数真的变了"。
    ★ 回 `{"ok", "before", "after", "asked", "use_sheet_scale_before"}`；★ **任一步失败都如实写 stage**。
    """
    #: ★★★ 2026-10-03（轮 470）**删掉这一行"函数内 import"** ——
    #:   它写的是 `from sw_connect import set_com_member as _set`，★ 那会**直接绑到真模块**，
    #:   ⇒ ★★ **契约测试对 `模块.set_com_member` 的猴补丁就补不到它**（★ 于是测试记录不到那次写，
    #:      断言 `seen == [("ScaleRatio", ((2.0, 1.0),))]` 失败）。
    #:   ★ 而**模块顶部早就 import 了 `set_com_member`**（★ 就是那对 try/except）⇒
    #:     ★ 直接用**模块级名字**即可 —— ★ 这样猴补丁可补、测试可记录 ✓
    #:   ⚠ 与本仓 `sw_simulation_study_options.py` L631 记的教训**同源**（★ 那里逐字写着
    #:     "`set_com_member` **必须在模块顶部 import** —— 我第一版写在函数体内 ⇒ 测试当场失败"）。
    #:   ★ 故下面把 `set_com_member(` 全部改成模块级的 `set_com_member(`。
    if view is None:
        return {"ok": False, "stage": "view", "error": "view 为 None"}
    #: ★ ① 读前置
    try:
        uss = get_com_member(view, "UseSheetScale")
    except Exception as exc:                                   # noqa: BLE001
        uss = None
        _uss_err = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    else:
        _uss_err = None
    #: ★ ② 关掉"跟随图纸"
    uss_cleared = None
    if uss:
        try:
            set_com_member(view, "UseSheetScale", False)
            uss_cleared = True
        except Exception as exc:                               # noqa: BLE001
            uss_cleared = False
            _uss_set_err = "%s: %s" % (type(exc).__name__, str(exc)[:140])
        else:
            _uss_set_err = None
    #: ★ ③ 读 before
    before = None
    try:
        before = get_com_view_scale_ratio_raw(view)
    except Exception:                                          # noqa: BLE001
        before = None
    #: ★ ④ 赋值（★ 真机验证过的形态）
    try:
        set_com_member(view, "ScaleRatio", (float(scale), 1.0))
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "set", "asked": float(scale),
                "before": before, "use_sheet_scale_before": uss,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    #: ★ ⑤ 回读
    try:
        after = get_com_view_scale_ratio_raw(view)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "readback", "asked": float(scale),
                "before": before, "use_sheet_scale_before": uss,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    changed = (before is not None and after is not None and tuple(before) != tuple(after))
    return {"ok": bool(changed), "asked": float(scale), "before": before, "after": after,
            "use_sheet_scale_before": uss, "use_sheet_scale_cleared": uss_cleared,
            "use_sheet_scale_read_error": _uss_err, "use_sheet_scale_set_error": _uss_set_err}


def get_com_view_scale_ratio_raw(view):
    """★ **取 `ScaleRatio` 的原始两个数**（★ 真机 `(1.0, 500.0)` 即 **1:500**）。"""
    if view is None:
        raise ValueError("view 为 None")
    raw = get_com_member(view, "ScaleRatio")
    if raw is None:
        raise RuntimeError("IView.ScaleRatio 回 None")
    try:
        return tuple(float(x) for x in raw)
    except TypeError:
        return (float(raw),)
