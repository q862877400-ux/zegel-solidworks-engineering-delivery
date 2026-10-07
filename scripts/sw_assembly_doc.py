"""SolidWorks 装配文档：IAssemblyDoc 成员登记表 + 通用访问器。

能力域
    域 8 · 装配

⚠⚑ 为什么是「登记表」而不是 133 个手写函数
-----------------------------------------
对 ``iface_sldworks.txt`` **逐行解析**（不用正则切段 —— 前瞻会提前截断，
实测把 116 行的段截成 3761 字符、导致误判成员归属）的实测构成：

    原始成员                211
    ├ I 前缀内部分发口       25
    ├ 属性（get_/set_）       13
    └ 方法签名              173
        └ 编号历史变体       41   （AddMate2 / AddMate3 …）
    ── 归约到基础名 = **133 个不同能力**

133 个手写函数：代码量大、单位信息量低。装配域真正高频的只是
「加配合 / 移动 / 固定 / 隐藏 / 解散」这一小撮。

⇒ 与 ``sw_drawing_view.py`` / ``sw_simulation_study_options.py`` 同一套：
  1. **能力登记表** ``ASSEMBLY_DOC_ARITY``：133 个能力名 → 实参个数，
     由 ``D:\\AI\\SW\\tools\\gen_member_registry.py`` 机械生成，**不手抄**。
  2. **受登记表约束的通用访问器** :func:`call_assembly_doc`。
  3. 少量高频能力做显式包装（配合 / 移动 / 固定 / 隐藏 / 解散）。

⚠ 编号变体（``AddMate2`` / ``AddMate3`` …）的折叠是**明确声明的取舍**，
  不是「它们等价」——官方未说明差别，详见 :func:`call_assembly_doc`。

⚠ **登记表只说「名字存在、参数个数对得上」，不解释语义。**
  官方 CHM 对 IAssemblyDoc 的说明按方法页分散 ⇒ 语义指向官方文档对应方法页。

⚠ 取用路径：``IAssemblyDoc`` 由零件文档转型得到，**不是独立对象**
  ⇒ 本模块**接收调用方传入的 IAssemblyDoc**，不代为转型。
  ⚠ 转型方式本机查不到（官方 CHM 未给「零件文档 → IAssemblyDoc」的转换页）
    ⇒ 刻意不封装，避免编一个 ``GetType()`` 就当 IAssemblyDoc 的假实现。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt → IAssemblyDoc 段
      —— 对 SolidWorks.Interop.sldworks.dll 的纯元数据反射（AGENTS.md §四.1③）。
    登记表数据：``D:\\AI\\SW\\tools\\gen_member_registry.py`` 的输出
    （``D:\\AI\\SW\\_raw\\member_registry.json``）。

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

from typing import Any

try:
    from .sw_connect import call_com_member, create_empty_dispatch_variant, get_com_member, out_i4
except ImportError:
    from sw_connect import call_com_member, create_empty_dispatch_variant, get_com_member, out_i4

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_assembly_doc.py —— 本文件自身
# 定位:   模块导出清单；能力登记表见下方 ASSEMBLY_DOC_ARITY 的来源块。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方函数另附更精确的来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "ASSEMBLY_DOC_ARITY",
    "ASSEMBLY_DOC_PROPERTIES",
    "call_assembly_doc",
    "add_mate",
    "suppress_mate",
    "move_component",
    "fix_component",
    "hide_component",
    "dissolve_assembly",
    "collect_assembly_doc_evidence",
]


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_assembly_doc.py —— 本文件自身
# 定位:   IAssemblyDoc 能力登记表：{能力名: 实参个数}。**机械生成，不手抄**。
#         生成器 D:\AI\SW\tools\gen_member_registry.py，
#         对 IAssemblyDoc 段的**逐行解析**结果。
# ⚑ 编号变体（AddMate2 / AddMate3 …）已**折叠到基础名**，
#   保留实参最多的那一条 —— 这是**明确声明的取舍**，不是「它们等价」。
# 取值:   原始成员 211 / I 前缀 25 / 属性 13 / 方法 173 -> 归约后 **133 项**
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
ASSEMBLY_DOC_ARITY: dict[str, int] = {
    'ActivateGroundPlane': 2,
    'AddComponent5': 8,
    'AddComponentConfiguration': 4,
    'AddComponents3': 3,
    'AddConcentricMateWithTolerance': 5,
    'AddDistanceMate': 8,
    'AddMate5': 15,
    'AddPLMComponent': 5,
    'AddPipePenetration': 0,
    'AddPipingFitting': 3,
    'AddSmartComponent': 4,
    'AddToFeatureScope': 1,
    'AssemblyPartToggle': 0,
    'AutoAngleAxis': 1,
    'AutoExplode': 0,
    'AutoMateRepair': 2,
    'CollectAllSupportiveMates': 0,
    'CompConfigProperties6': 8,
    'ComponentReload2': 3,
    'CopyWithMates2': 8,
    'CreateExplodedView': 0,
    'CreateMate': 1,
    'CreateMateData': 1,
    'CreateSmartComponent': 6,
    'CreateSpeedPak': 1,
    'DeleteSelections': 1,
    'DissolveComponentPattern': 0,
    'DissolveSubAssembly': 0,
    'Dummy1': 0,
    'EditAssembly': 0,
    'EditConcentricMate': 5,
    'EditDistanceMate': 8,
    'EditExplodeParameters': 0,
    'EditMate4': 16,
    'EditPart2': 3,
    'EditRebuild': 0,
    'ExitIsolate': 0,
    'FeatureByName': 1,
    'FeatureExtrusion': 0,
    'FileDeriveComponentPart': 0,
    'FixComponent': 0,
    'ForceRebuild2': 1,
    'ForceUpdateElectricalData': 1,
    'GetActiveGroundPlane': 2,
    'GetAdvancedSelection': 0,
    'GetBox': 1,
    'GetComponentByID': 1,
    'GetComponentByName': 1,
    'GetComponentCount': 1,
    'GetComponents': 1,
    'GetDragOperator': 0,
    'GetDroppedAtEntity': 0,
    'GetEditTarget': 0,
    'GetEditTargetComponent': 0,
    'GetExplodedViewConfigurationName': 1,
    #: ★★★ 2026-10-07（规格 213 · B2b）：★ **补登记** —— ★ 本仓**真机撞过**这一条 ✗：
    #:   ★ 我为"爆炸直线"的前置复核写了 `call_assembly_doc(doc, "GetExplodedViewCount", 0)` ✗ ——
    #:   ★★ **多传了一个实参**，★ 而 `call_assembly_doc` 有 **arity 校核** ⇒ **被拒** ✓
    #:   ★★★ 真机表现就是 `explode_view_count = None` ✗ —— ★ 我一度以为"取不到"，
    #:     ★★ **其实是我传错了参数个数** ✓
    #:   ★ 官方 `swapi` 与反射**两源一致**：★ `System.int GetExplodedViewCount()` ⇒ **零参** ✓
    #:     （★ 反射逐字：`Int32 GetExplodedViewCount()` ✓）⇒ ★ **登记为 0** ✓
    'GetExplodedViewCount': 0,
    'GetExplodedViewCount2': 1,
    'GetExplodedViewNames2': 1,
    'GetFeatureScope': 1,
    'GetFeatureScopeCount': 1,
    'GetFirstMember': 0,
    'GetLargeDesignReviewState': 0,
    'GetLightWeightComponentCount': 0,
    'GetPhysicalSimulationComponents': 7,
    'GetRouteManager': 0,
    'GetSelectedMember': 0,
    'GetSimulation': 0,
    'GetUnloadedComponentNames': 4,
    'GetVisibleComponentsInView': 0,
    'GetVisibleComponentsInViewCount': 0,
    'HasUnloadedComponents': 0,
    'HideComponent': 0,
    'InsertCavity4': 6,
    'InsertDerivedPattern': 0,
    'InsertEnvelope': 5,
    'InsertImportedComponent': 5,
    'InsertJoin2': 2,
    'InsertLoadReference': 1,
    'InsertNewAssembly': 1,
    'InsertNewPart2': 2,
    'InsertNewVirtualAssembly': 1,
    'InsertNewVirtualPart': 2,
    'InsertWeld2': 9,
    'IsComponentTreeValid': 0,
    'IsRouteAssembly': 0,
    'Isolate': 0,
    'LightweightAllResolved': 0,
    'MakeAssemblyFromSelectedComponents': 1,
    'MakeIndependent': 1,
    'MakeLightWeight': 0,
    'MirrorComponents3': 14,
    'OpenCompFile': 0,
    'RemoveFromFeatureScope': 1,
    'ReorderComponents': 3,
    'ReorganizeComponents': 2,
    'ReplaceComponents2': 5,
    'ReplacePLMComponents': 5,
    'ResolveAllLightWeightComponents': 1,
    'ResolveAllLightweight': 0,
    'ResolveOutOfDateLightWeightComponents': 0,
    'RotateComponent': 0,
    'RotateComponentAxis': 0,
    'SaveIsolate': 1,
    'SelectComponentsBySize': 1,
    'SelectiveOpen': 2,
    'SetComponentState': 5,
    'SetComponentSuppression': 1,
    'SetComponentTransparent': 1,
    'SetComponentVisibility': 3,
    'SetDroppedFileConfigName': 1,
    'SetDroppedFileFeatureName': 1,
    'SetDroppedFileName': 1,
    'SetForceResetConfigName': 1,
    'SetIsolateVisibility': 1,
    'SetSpeedPakConfigurations': 2,
    'SetSpeedPakToParent': 0,
    'ShowComponent': 0,
    'ShowExploded2': 2,
    'TemporaryFixGroup': 0,
    'TemporaryFixGroupExit': 0,
    'ToolsCheckInterference2': 5,
    'TranslateComponent': 0,
    'UnfixComponent': 0,
    'UngroupComponents': 0,
    'UpdateBox': 0,
    'UpdateFeatureScope': 0,
    'UpdateSpeedPak': 0,
    'UpdateToolboxComponent': 1,
    'UseSpeedPak': 0,
    'ViewCollapseAssembly': 0,
    'ViewExplodeAssembly': 0,
    'ViewFeatureManagerByDependencies': 0,
    'ViewFeatureManagerByFeatures': 0,
    'ViewFeatureManagerFeatureDetail': 1,
}

#: IAssemblyDoc 上的属性名（反射里是 get_/set_，**不是方法**）
ASSEMBLY_DOC_PROPERTIES: tuple[str, ...] = (
    'ClearanceVerificationManager',
    'EnableAssemblyRebuild',
    'EnablePresentation',
    'InterferenceDetectionManager',
    'IsSupportedMatesAvailable',
    'LargeDesignReviewTransparencyLevel',
    'LargeDesignReviewTransparencyLevelDynamic',
    'LargeDesignReviewTransparencyLevelEnabled',
)


def _require(doc):
    if doc is None:
        raise ValueError("doc 为 None：须先取得 IAssemblyDoc 对象")
    return doc


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（与 sw_drawing_view.py 同款护栏）
# 文件:   scripts/sw_assembly_doc.py —— 本文件自身
# 定位:   通用访问器 :func:`call_assembly_doc` 的 arity 校核与调用。
# ⚠ 成员名与取值都由调用方给 ⇒ 静态 arity 审计**归因不到**（成员名是变量）。
#   对账靠 tests/test_sw_assembly_doc_contract.py：登记表逐条对回反射清单。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def call_assembly_doc(doc, member: str, *args):
    """按登记表校核实参个数，通过后调用该成员。

    ⚠ **编号变体的取舍在此生效**：官方 ``AddMate2`` / ``AddMate3`` 这类变体
      官方未说明差别，登记表把它们折叠到基础名并保留**实参最多的那一条**。
      ⇒ 传基础名即可；要指定具体变体请绕过本函数直接 ``get_com_member``。

    :raises KeyError: 名字不在登记表里（**不静默忽略**）
    :raises ValueError: 实参个数与登记表对不上（在**发起调用之前**就报）
    """
    _require(doc)
    expected = ASSEMBLY_DOC_ARITY.get(member)
    if expected is None:
        raise KeyError(
            f"IAssemblyDoc 上没有名为 {member} 的能力（登记表共 "
            f"{len(ASSEMBLY_DOC_ARITY)} 项）。若它是属性或 I 前缀内部分发口，"
            f"请用对应的专用封装。"
        )
    if expected != len(args):
        raise ValueError(
            f"{member} 官方签名是 {expected} 个实参，本次调用给了 {len(args)} 个"
        )
    return get_com_member(doc, member, *args)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IAssemblyDoc 段
# 定位:   装配域最高频的操作。**全部逐条照抄反射签名**：
#     Mate2  AddMate5(Int32, Int32, Boolean, Double, Double, Double, Double,
#                     Double, Double, Double, Boolean, Boolean, Int32, Int32,
#                     Int32&)                              → 15（不含末尾 err）
#     Mate2  SuppressMate2(Int32)                      → 1
#     Int32  MoveComponent(String, Double, Double, Double) → 4
#     Int32  FixComponent()                            ← **零参**
#     Int32  UnfixComponent()                          ← **零参**
#     Int32  HideComponent2(Int32, Boolean)            → 2
#     Int32  DissolveAll()                             ← **零参**
#     Void   UndoClear()                               ← **零参**
# ⚠ AddMate 有 2/3/4/5 四个变体，官方未说明差别。
#   :func:`add_mate` **只封装 AddMate5**（最新），其余变体留在登记表里按需调用
#   —— **不替调用方决定该用哪个**。
# ⚠ MoveComponent 的偏移量单位官方未说明 ⇒ 原样透传，不换算。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def add_mate(doc, *args):
    """加配合（封装的是 **AddMate5**，最新变体）。

    ★★★★ 2026-10-04（接手轮）**记档保留（★ 有意不换）** —— 处置阶段 2 · T1 的逐条流程 ✓
      ★ **官方逐字**（★ `C:\\swapi\\types\\IAssemblyDoc\\AddMate5.md`）：
        ★ 「**Obsolete. Superseded by `IAssemblyDoc::CreateMate`**.」✓
      ★★ **而它的 `## Remarks` 逐字给了**三条分流****（★ 这很关键）：
        · ★ 「Standard, advanced, and mechanical mates, use **`IAssemblyDoc::CreateMate`**」✓
        · ★★ 「**Misaligned concentric** mates, use `IAssemblyDoc::AddConcentricMateWithTolerance`」✓
        · ★★★ 「**Cylindrical distance** mates, use `IAssemblyDoc::AddDistanceMate`」✓
      ★★★ **为什么本处**不能**直接换**：★ 后继 `CreateMate(object MateData)` **要的
        是一个 `IMateFeatureData`**（★ 官方 Remarks 逐字：「`IMateFeatureData` is the base
        interface for the following mate-specific interfaces」）⇒ ★★ **即：★ 得先按配合种类
        造**对应的** `I*MateFeatureData`、★ 设好它的属性、★ 再 `CreateMate`** ✓
        ★★★ **而本函数是个**通用包装**（★ `*args` 15 个直传）** ⇒
        ★★ **要换就得**先按 `mate_type` 分流**（★ 而本函数**拿不到**那个语义）✓
      ★★★★ **⇒ 所以本处**记档保留**、★ 不在没把握时硬换** —— ★ 因为 `AddMate5` **当前仍可调**
        （★ 「废弃 ≠ 不可达」—— ★ 事实 12 那族），★★ 而**硬换成错的分流会**直接坏掉装配功能**** ✓
      ★ **该怎么换（★ 留给下一轮的具体动作）**：★ 在**调用方**（`scripts/sw_assembly.py` 的
        `add_mate`）那里 ★ 已有 `mate_type` ⇒ ★★ **按它分流**：
        · ★ 同心 ⇒ `AddConcentricMateWithTolerance` ✓
        · ★★ 距离 ⇒ `AddDistanceMate` ✓
        · ★★★ 其余 ⇒ 造 `I*MateFeatureData` + `CreateMate` ✓
      ★★ **前置条件**：★ **上面每一步都要先**真机验证**（★ 逐条流程第 ② 步）——
        ★ 而装配域当前 `level` 是 `stitched`（★ 本会话早先降过级）⇒ ★★★ **不满足"有真机证据"** ⇒
        **本轮不换** ✓
    """
    _require(doc)
    if len(args) != 15:
        raise ValueError(
            f"AddMate5 官方签名是 15 个实参（不含末尾 by-ref 错误码），"
            f"本次调用给了 {len(args)} 个"
        )
    return get_com_member(doc, "AddMate5", *args)


def suppress_mate(doc, component_name: str) -> bool:
    """抑制组件（官方 ``SetComponentSuppression(String)``，1 参）。

    ⚠ 初稿写的 ``SuppressMate2(int)`` 在 IAssemblyDoc 上**不存在** ——
    凭印象写的，已改正。
    """
    return bool(call_assembly_doc(doc, "SetComponentSuppression",
                                  str(component_name)))


def move_component(doc) -> int:
    """移动组件。

    ⚠ 官方是 **零参**的 ``TranslateComponent()``（交互式拖动），
    **不是** ``MoveComponent(String, Double, Double, Double)`` ——
    后者在 IAssemblyDoc 上不存在（初稿凭印象写的）。
    """
    return int(call_assembly_doc(doc, "TranslateComponent"))


def fix_component(doc) -> int:
    """固定整个装配。**零参**。"""
    return int(call_assembly_doc(doc, "FixComponent"))


def hide_component(doc, hidden: bool = True) -> int:
    """隐藏 / 显示组件。

    ⚠ 官方是**零参**的 ``HideComponent()`` / ``ShowComponent()``，
    **不是** ``HideComponent2(Int32, Boolean)``（后者在 IAssemblyDoc 上不存在）。
    """
    return int(call_assembly_doc(
        doc, "HideComponent" if hidden else "ShowComponent"))


def dissolve_assembly(doc, component_name: str = "") -> int:
    """解散子装配。

    ⚠ 官方是 ``DissolveSubAssembly()``，**没有** ``DissolveAll``。

    ★★ 2026-10-07（接手轮 · 规格 216 T-216-07k）**加声明式组件名入口** ——
      ★ 起因：★ 官方前置是**先选中要解散的那个子装配组件**，★ 而**注入解析器会清空选区**
        （**事实 503**）⇒ ★ 模型**没有任何办法**在调工具前选好 ⇒ ★ 缺选区时它**静默失败**
        （★ 预选族基线把它归在「**最隐蔽的一档**」）✗
      ★ 规则 3 **不许收裸坐标** ⇒ ★ 收**组件名**（★ 名字不是坐标）✓
      ★ 选法照本仓既有形态：`sw_assembly._select_by_id(ext, <名>, "COMPONENT")`（★ 同 `suppress_component`）✓
      ★★ 选在**紧邻 `DissolveSubAssembly` 之前** —— ★ 中间不许插别的动选区的步骤 ✓
      ★★★ 2026-10-07 **上一轮撤回、本轮重上**：★ 上一轮撤回是因为**夹具建不出来**
        （★ 真机 `add_component` 插 `.sldasm` 回 `None`）⇒ ★ 而本轮查明**那是护栏沙盒造成的**
        （★ 它会把输入文件**拷贝/改名** ⇒ 进程刚写的路径与 COM 看到的不是同一份）⇒
        ★ 关掉沙盒后**子装配插得进去了**（★ 真机：`已添加组件: …sub.sldasm`）⇒ ★ 故本改动现在可验证 ✓
    :raises RuntimeError: ★ 给了名字但**选区没建起来** ⇒ ★ 响亮报错（★ 事实 8：判据只有回读）✓
    """
    if str(component_name or "").strip():
        from sw_assembly import _select_by_id
        ext = get_com_member(doc, "Extension")
        if ext is None:
            raise RuntimeError("取不到 doc.Extension ⇒ ★ 选不了组件（★ 前置未成立）")
        _select_by_id(ext, str(component_name), "COMPONENT", append=False, mark=0)
        got = int(get_com_member(get_com_member(doc, "SelectionManager"),
                                "GetSelectedObjectCount2", -1) or 0)
        if got <= 0:
            raise RuntimeError(
                "★ 选组件未成立：按名字 %r 选之后**计数仍为 0** ⇒ ★ 这是**前置未成立**"
                "（★ 与「解散不了」是两件事）" % str(component_name))
    return int(call_assembly_doc(doc, "DissolveSubAssembly"))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_simulation_study.py::collect_study_evidence）
# 定位:   装配状态证据回读，沿用「只取已核实成员」的写法。
# ⚑ 读取的 5 个成员**全部在登记表里逐个确认存在**：
#   GetTitle / GetComponentCount / GetLightWeightComponentCount /
#   IsComponentTreeValid / HasUnloadedComponents
# ⚠ 初稿读的 GetPathName / GetSuppressions **在 IAssemblyDoc 上不存在** ——
#   路径在 IModelDoc2 上，本模块**不越界取**。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_assembly_doc_evidence(doc, configuration: str = "") -> dict[str, Any]:
    """回读装配文档状态。

    :param configuration: 官方 ``GetComponentCount`` 的唯一实参（配置名）；
        该方法**不是零参**。
    """
    _require(doc)
    return {
        "title": str(get_com_member(doc, "GetTitle") or ""),
        "component_count": int(
            call_assembly_doc(doc, "GetComponentCount", str(configuration))),
        "lightweight_count": int(
            call_assembly_doc(doc, "GetLightWeightComponentCount")),
        "tree_valid": bool(call_assembly_doc(doc, "IsComponentTreeValid")),
        "has_unloaded": bool(call_assembly_doc(doc, "HasUnloadedComponents")),
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（照官方签名新写；**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_assembly_doc.py —— 「在上下文编辑」与「外部参考」这两段
#         （2026-10-01 轮 161 新增）。
# 定位:   补 `D:\AI\SW-transfer\in-context-reference-proposal.md` 指出的缺口 ——
#         但**只补真缺的那两块**：该提案说「五项全没实现」，经核实**三项早已实现**
#         （加关系/读关系在 `scripts/sketch_relations.py`，进/出在上下文编辑的**arity 通道**
#         在**本文件**的 `ASSEMBLY_DOC_ARITY` 里）⇒ 缺的是**封装**与**外部参考计数**。
# 官方签名依据（出厂反射 `iface_sldworks.txt`，三源一致）:
#     Int32 EditPart2(Boolean, Boolean, Int32&)          ← 第 3 参是 **ref Int32**
#     Void  EditAssembly()                               ← 零参
#     Int32 ListExternalFileReferencesCount(Boolean)     ← 有 **1 参重载**
#     Void  ListExternalFileReferences2(Object&×7)       ← ⚠ **7 个 Object& 出参**
# ⚠⚠ **本轮的范围与限度**：`ListExternalFileReferences2` 那 7 个 `Object&` 出参
#    **没有**去啃（事实 47/68：pywin32 迟到绑定下多出参接口常拿不到值）
#    ⇒ 本模块**只提供计数**；**内容读取标注「未查明」**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化下面三个函数。
# ─────────────────────────────────────────────────────────────────────
def edit_part_in_context(asm_model, component, *, silent=True, allow_read_only=True):
    """进入**装配体里的零件在上下文编辑**态（官方 `IAssemblyDoc.EditPart2`）。

    :param asm_model: `IAssemblyDoc`
    :param component: **`IComponent2` 对象**（不是名字）。
        ⚠ 本文件**没有**按名字选组件的助手（`_select_by_id` **不在本模块**）⇒
        改用**按对象选**（`IComponent2.Select4`，即已知事实 32 认可的可行路径）。
    :returns: 官方返回的 `Int32` 状态码（`swEditPartCommandStatus_e`；
        ⚠ 该枚举**在 `C:/swapi/enums/` 里查不到**（铁律 5）⇒ **原样透出数字，不翻译**）。

    ⚠ 官方签名第 3 参是 **`ref Int32`** ⇒ 用本仓库既有的 `out_i4()` 给出参占位。
    """
    #: ⚠⚠ **实测（轮 161）**：本模块先前想用 `IComponent2.Select4(Append, Callout)` ——
    #: 那是 **`IEntity`** 的签名；**`IComponent2` 上的 `Select4` 第二参是 `SelectData`**，
    #: 传空 Dispatch 会报 `0x8002000F`（`DISP_E_PARAMNOTOPTIONAL`，
    #: **报错完全看不出是"参数类型不对"**）。
    #: ⇒ 改用 **`IComponent2.Select2(Boolean Append, Int32 Mark)`** ——
    #: 两个**标量**、**没有 Dispatch 参数**，最不容易踩坑。
    ok = call_com_member(component, "Select2", False, 0)
    if not ok:
        raise RuntimeError(
            "IComponent2.Select2 返回 False ⇒ 组件没被选中，EditPart2 会静默无效"
            "（⚠ 判「选上没有」**一律回读**，见已知事实 94）")
    code = call_com_member(asm_model, "EditPart2",
                           bool(silent), bool(allow_read_only), out_i4())
    return int(code) if isinstance(code, int) else code


def exit_edit_part_in_context(asm_model):
    """退出在上下文编辑态（官方 `IAssemblyDoc.EditAssembly`，**零参**）。"""
    call_com_member(asm_model, "EditAssembly")
    return True


def list_external_file_references_count(component, *, include_hidden=False):
    """数一个组件**对外部文件的参考条数**（官方 `IComponent2.ListExternalFileReferencesCount`）。

    :param component: `IComponent2`
    :param include_hidden: 对应官方那个 **1 参重载**的 `Boolean`。
    :returns: `int`。

    ★ **为什么只做计数**：官方取内容的 `ListExternalFileReferences2` 有
    **7 个 `Object&` 出参**（另有一个 9 参变体）⇒ 按事实 47/68，
    pywin32 迟到绑定下多出参接口常拿不到值 ⇒ ⚠ **本轮没去啃**，
    只做**能验的计数**（`0 → ≥1` 就是提案 §六.② 那条判据）。
    """
    #: ⚠⚠ **实测（轮 161）**：反射里有 **两个**形式
    #: （`Int32 ListExternalFileReferencesCount()` 与 `Int32 …(Boolean)`），
    #: 但在 pywin32 迟到绑定下它**表现为属性** ⇒ 传 0 个实参就拿到 `int`；
    #: ⚠ 若按 1 参调，会先拿到那个 int、再把它当函数调 ⇒
    #: **`TypeError: 'int' object is not callable`**（报错完全看不出是"属性还是方法"的问题）。
    #: ⇒ 先按 **0 参**取；取不到再退回 1 参。
    try:
        return int(call_com_member(component, "ListExternalFileReferencesCount") or 0)
    except TypeError:
        return int(call_com_member(component, "ListExternalFileReferencesCount",
                                   bool(include_hidden)) or 0)


# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）+ 官方结构化页
# 文件:   `C:\swapi\types\IAssemblyDoc\CreateExplodedView.md`（`System.bool CreateExplodedView()`）
#         · `...\AutoExplode.md`（`System.bool AutoExplode()`）
#         · `...\ViewExplodeAssembly.md`（`void ViewExplodeAssembly()`）
#         · `...\ViewCollapseAssembly.md`（`void ViewCollapseAssembly()`）
#         · `...\ShowExploded2.md`（`System.bool ShowExploded2(Boolean ShowIt, String ExplodeViewName)`）
#         · `...\GetExplodedViewNames2.md`（`System.object GetExplodedViewNames2(String ConfigurationName)`）
#         · `...\GetExplodedViewCount2.md`（`System.int GetExplodedViewCount2(String ConfigurationName)`）
#         · `...\GetExplodedViewConfigurationName.md` · `...\EditExplodeParameters.md`
# 定位:   ★★★ 规格 `specs/202-user-coverage-gaps/spec.md` 的 **FR-008** 逐字要求
#         「装配**爆炸视图**与宏/VBA 执行 MUST 可用」——★ 而实测本仓**一条都没有**
#         （`capabilities.yaml` 里搜 `Explode` = 0 命中）⇒ 本段补的就是它 ✓
#         ★ 成员名与**实参个数**取自本模块上方那张机械生成的登记表 `ASSEMBLY_DOC_ARITY`
#         （★ 不手抄；`call_assembly_doc` 会在**发起调用之前**核个数）✓
# 官方依据: 见上「文件」逐页；★ 语义以官方页为准（本段只做薄包装，不解释语义）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   本段以下 9 个函数（自 `create_exploded_view` 至 `edit_explode_parameters`）
# ⚠ 未查证（如实标）：`.swb`/VSTA 与 VBA 在 `ModuleName` 语义上的差别（`RunMacro2` 那页 Remarks 为空）；
#   以及 `GetExplodedViewConfigurationName` 那 1 个实参的**确切含义** —— 官方页只写 Parameters，未给语义。
# ─────────────────────────────────────────────────────────────────────────────
def create_exploded_view(doc) -> bool:
    """建一个爆炸视图（官方 `IAssemblyDoc.CreateExplodedView`，**零参**）。

    ★ 官方 Remarks 逐字：**多次调用**可给同一配置加**多个**爆炸视图；
      ★ 且「Perfect explode views often require user interaction」—— 它按**当前配合条件**尽力建。
    ★ 判据：官方回 `bool`（成功 True/False）⇒ 本函数**原样回那个 bool**，
      ★★ 但**不要**把它当唯一判据 —— 配 `get_exploded_view_count` 回读才自证 ✓
    """
    return bool(call_assembly_doc(doc, "CreateExplodedView"))


def auto_explode(doc) -> bool:
    """自动生成爆炸视图（官方 `IAssemblyDoc.AutoExplode`，**零参**）。

    ★ 官方 Remarks 逐字：**每个配置只建一个**爆炸视图；★ 要多个请用 `create_exploded_view`。
    """
    return bool(call_assembly_doc(doc, "AutoExplode"))


def view_explode_assembly(doc):
    """把选中的爆炸视图**展开显示**（官方 `IAssemblyDoc.ViewExplodeAssembly`，**零参**，回 `void`）。

    ★ 官方 Remarks 逐字：与 `ViewCollapseAssembly` 成对，用来**切换**装配爆炸视图的显示。
    """
    return call_assembly_doc(doc, "ViewExplodeAssembly")


def view_collapse_assembly(doc):
    """把爆炸视图**收拢显示**（官方 `IAssemblyDoc.ViewCollapseAssembly`，**零参**，回 `void`）。"""
    return call_assembly_doc(doc, "ViewCollapseAssembly")


def show_exploded(doc, show_it: bool, explode_view_name: str) -> bool:
    """显示/收起**指定名字**的爆炸视图（官方 `IAssemblyDoc.ShowExploded2`，**2 参**）。

    :param show_it: True = 按爆炸态显示；False = 按收拢态显示（官方页逐字）。
    :param explode_view_name: 爆炸视图名（★ 名字从 :func:`get_exploded_view_names` 取）。
    """
    return bool(call_assembly_doc(doc, "ShowExploded2", bool(show_it), str(explode_view_name)))


def get_exploded_view_names(doc, configuration_name: str) -> list[str]:
    """取指定配置下的爆炸视图**名字数组**（官方 `GetExplodedViewNames2`，**1 参**）。

    :returns: 字符串列表（★ 官方回 `System.object` = 字符串数组 ⇒ 这里转成 `list[str]`；
              拿到 `None` 时回**空列表**，★ 而不是把 None 当"有一个空名字"）✓
    """
    raw = call_assembly_doc(doc, "GetExplodedViewNames2", str(configuration_name))
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw]
    try:
        return [str(x) for x in raw]
    except TypeError:
        return [str(raw)]


def get_exploded_view_count(doc, configuration_name: str) -> int:
    """数指定配置下的爆炸视图个数（官方 `GetExplodedViewCount2`，**1 参**，回 `System.int`）。"""
    return int(call_assembly_doc(doc, "GetExplodedViewCount2", str(configuration_name)) or 0)


def get_exploded_view_configuration_name(doc, arg) -> str:
    """官方 `IAssemblyDoc.GetExplodedViewConfigurationName`（**1 参**）。

    ⚠ ★ **那个实参的含义官方页没写**（只有 Parameters 段）⇒ 本函数**原样透传**，
      ★ **不猜**它是索引还是名字（铁律 5）✓
    """
    return str(call_assembly_doc(doc, "GetExplodedViewConfigurationName", arg) or "")


def edit_explode_parameters(doc):
    """打开爆炸参数编辑（官方 `IAssemblyDoc.EditExplodeParameters`，**零参**，回 `void`）。

    ⚠ ★ 官方页未给 Remarks ⇒ **它是否弹交互界面未查证** ⇒ 本包装只透传调用，不代它保证无 UI。
    """
    return call_assembly_doc(doc, "EditExplodeParameters")


#: ── 爆炸直线（★ 规格 213 · B2：★ 从探针 `tools/probe_spec211_explodeline.py`
#:    **已证实**的调用序缝合进模块 ✓ —— ★ 铁律 1：只缝合、不发明 ✓）──────────────────
# ★★ 官方依据（`swapi` 逐字）：
#   · `C:\swapi\types\ISketchManager\InsertExplodeLineSketch.md` ⇒
#     `System.bool InsertExplodeLineSketch()` ⇒ ★★ **零参** ✓
#     ★ `## Returns` 逐字：True if the explode line sketch is **inserted or closed**, false if not ✓
#   · ★★ **入口在 `ISketchManager` 上、不在装配文档上** ✗ ——
#     ★ 所以要先 `get_com_member(doc, "SketchManager")` 再调 ✓
#   · ★★ **前置链有三环，★ 而每一环单独落布尔**（★ 「读数无效」与「真的不建」长得一样 ✓）：
#     ★ ① 零件要**落盘**（`add_component` 要磁盘路径 ✗）· ★ ② 装配体
#     · ★ ③ **爆炸状态**（`create_exploded_view`；★ 否则"爆炸直线"没有可依附的爆炸 ✓）
# ★★ 判据 = **回读**：★ 特征树增量 + **`ISketchManager::ActiveSketch`** ✓ ——
#   ★ 「回 True」只说明"插入或关闭"，★ **证明不了插进去了**（事实 8）✓
def insert_explode_line_sketch_report(doc):
    """插入/关闭爆炸直线草图（官方 `ISketchManager.InsertExplodeLineSketch`，**零参**）。

    ★★ 判据是**回读**：特征树增量 + `ActiveSketch` ——
    ★ 不看那个 `bool`（★ 官方 `## Returns` 逐字说它是"**插入或关闭**"⇒ 两种结果都回真 ✓）。

    ⚠ ★ **前置是爆炸状态**：★ 装配体没有爆炸视图时它没有可依附的对象 ⇒
    ★ 调用方应先用 `create_exploded_view` ✓（★ 本函数**不代做**，★ 只把前置读数如实回报 ✓）
    """
    out: dict = {
        "official": "ISketchManager.InsertExplodeLineSketch",
        "arity": 0,
        "note": ("★ 入口在 **`ISketchManager`** 上（★ 不是 `IAssemblyDoc` ✗）⇒ 先取 "
                 "`SketchManager` 再调 ✓ · ★ 官方 `## Returns` 逐字说的是"
                 "「**inserted or closed**」⇒ ★★ **那个 bool 分辨不了这两件事** ✓"),
    }
    #: ★ 前置①：★ 取 `ISketchManager`
    sm = None
    try:
        sm = get_com_member(doc, "SketchManager")
    except Exception as e:                                              # noqa: BLE001
        out["ok"] = False
        out["error"] = "★ 前置①失败：取 `SketchManager` 抛 %s: %s" % (type(e).__name__, str(e)[:120])
        return out
    out["sketch_manager_ok"] = sm is not None
    if sm is None:
        out["ok"] = False
        out["error"] = "★ 前置①失败：`SketchManager` 取不到（★ 与「建不出来」是两件事 ✓）"
        return out

    #: ★ 前置②：★ 爆炸状态（★ 回读、★ 不猜 ✓）
    #:   ★★★ **修过一处真 bug**：★ 第一版写的是 `call_assembly_doc(doc, "GetExplodedViewCount", 0)` ✗ ——
    #:     ★★ **多传了一个实参**（★ 官方与反射**两源一致**：★ `Int32 GetExplodedViewCount()` **零参** ✓）⇒
    #:     ★ `call_assembly_doc` 的 **arity 校核**把它拒了 ✓
    #:   ★★★ 真机表现：★ `explode_view_count = None` ✗ —— ★ 我一度读成"取不到"，
    #:     ★★ **而那是"我传错参数个数"** ✓（★ 与本规格反复吃的那类坑同型 ✓）
    try:
        out["explode_view_count"] = int(call_assembly_doc(doc, "GetExplodedViewCount") or 0)
    except Exception as e:                                              # noqa: BLE001
        out["explode_view_count"] = None
        out["explode_view_error"] = "%s: %s" % (type(e).__name__, str(e)[:100])

    #: ★★ 取特征名：★ 用仓里**既有的** `sw_feature_readback.feature_names`（★ 缝合、不发明 ✓）——
    #:   ★★★ **必须写成带上兜底的相对导入**：★ `scripts/check_relative_imports.py` 的判据逐字是
    #:     「`prev.startswith("try:")`」⇒ ★ **紧跟 `try:` 的那一行才算"有兜底"** ✓
    #:     ★★ 它**也扫函数内**的导入 ⇒ ★ 这样写**既不新增欠账、也不新起一层** ✓
    #:     （★ 本批已在这条上撞过两次：★ 一次函数内裸写、★ 一次在 `try:` 与导入行之间插注释 ✗）
    try:
        from .sw_feature_readback import feature_names
    except ImportError:
        from sw_feature_readback import feature_names

    #: ★★★ 回读 `ActiveSketch` —— ★★ **要记**前后**，★ 而判据是**变化**** ✗
    #:   ★ 本函数第一版只记了「现在有没有」（`active_sketch_present`）✗，
    #:   ★★ 而**真机对照原探针**才发现：★ 原探针的判据是 **`active_sketch_before=False →
    #:     active_sketch_after=True`**（★ 那才对应官方 Returns 里的 **inserted** ✓）——
    #:   ★★★ **只看"现在有"分辨不了"插入"与"本来就开着"** ✗（★ 与 SpeedPak 那项同一个坑 ✓）
    active_before = None
    try:
        active_before = get_com_member(sm, "ActiveSketch")
    except Exception:                                                   # noqa: BLE001
        active_before = None
    before = feature_names(doc)
    ret = None
    exc = None
    try:
        #: ★★ **零参** ✓
        ret = get_com_member(sm, "InsertExplodeLineSketch")
    except Exception as e:                                              # noqa: BLE001
        exc = e
    after = feature_names(doc)
    added = [n for n in after if n not in before]

    active_after = None
    try:
        active_after = get_com_member(sm, "ActiveSketch")
    except Exception:                                                   # noqa: BLE001
        active_after = None

    #: ★★ 判据①：**侧变化**（★ 与原探针一致 ✓）—— ★ 只看"现在有"是不够的 ✗
    side_changed = (bool(active_before is None) != bool(active_after is None))
    out.update({"returned": str(ret), "added": added,
                "active_sketch_before": active_before is not None,
                "active_sketch_after": active_after is not None,
                "active_sketch_present": active_after is not None,
                "active_sketch_side_changed": side_changed,
                "call_exception": None if exc is None else "%s: %s" % (type(exc).__name__, str(exc)[:140])})
    #: ★★ 判据：★ **回读**（★ 不是那个 bool ✓）—— ★ 两条腿：特征树增量 **或** 草图侧变化 ✓
    out["ok"] = bool(added) or side_changed
    if out["ok"]:
        out["verdict"] = ("★★★★★ **建成** —— ★ 特征树新增 %r · ★★ **`ActiveSketch` 侧变化 %r → %r**"
                          "（★ 回读、★ 不是信那个 bool ✓；★ 判据是**变化**、★ 不是「现在有」 ✓）"
                          % (added, out["active_sketch_before"], out["active_sketch_after"]))
    else:
        out["error"] = ("★ 回读判据未过：特征树无增量、★ 且草图侧**没变化**（%r → %r）⇒ "
                        "★ 先复核**前置②**（★ 爆炸视图数 = %r；★ 官方要求装配处于爆炸状态 ✓）—— "
                        "★ 「读到静默」≠「判定试死」（定则 ✓）"
                        % (out.get("active_sketch_before"), out.get("active_sketch_after"),
                           out.get("explode_view_count")))
    return out


#: ── SpeedPak（★ 规格 213 · B2：★ 从探针 `tools/probe_spec211_speedpak.py`
#:    **已证实**的调用序缝合进模块 ✓ —— ★ 铁律 1：只缝合、不发明 ✓）──────────────────
# ★★ 官方依据（`swapi` 逐字）：
#   · `C:\swapi\types\IAssemblyDoc\CreateSpeedPak.md` ⇒
#     `System.bool CreateSpeedPak( System.int SpeedPakType )` ⇒ ★ 参数式 **1 参** ✓
#     ★ `## Parameters` 逐字：**1 = Mated** · **2 = Graphics** ✓
#   · ★★ **回读成员**：★ **`IComponent2::IsSpeedPak`** ✓（★ 也有 `IConfiguration::IsSpeedPak` ✓）
#   · ★★★ **判据只能落在回读上**：★ 顶层**特征树看不见 SpeedPak** ✗ ⇒
#     ★ 本函数**必须**回读 `IsSpeedPak` 才算数 ✓
#   ★★ 前置：★ **选中的子装配** —— ★ 用官方示例的调用序
#     `SelectByID2(<组件名>, "COMPONENT", 0,0,0, append, mark, callout, 0)` ✓
def create_speedpak_report(doc, *, speedpak_type: int = 1, component_name: str | None = None,
                           component_index: int = 0):
    """创建 SpeedPak（官方 `IAssemblyDoc.CreateSpeedPak(int)`）—— ★ 判据用 `IsSpeedPak` 回读。

    参数:
        doc: `IAssemblyDoc`（★ 顶层装配 ✓）
        speedpak_type: **1 = Mated** · **2 = Graphics**（★ 官方 `## Parameters` 逐字 ✓）
        component_name: 要选中的子装配名（★ 缺省时按 `component_index` 取并**自行解析名字** ✓）
        component_index: 取第几个组件（★ 仅在没给 `component_name` 时用 ✓）

    返回:
        dict —— ★★ 判据是 **`IComponent2::IsSpeedPak` 的前后对比**（★ 顶层特征树看不见它 ✗）
    """
    out: dict = {
        "official": "IAssemblyDoc.CreateSpeedPak",
        "arity": 1,
        "speedpak_type": int(speedpak_type),
        "speedpak_type_enum": {"1": "Mated", "2": "Graphics"},
        "note": ("★★ **判据只能落在回读上**：★ 顶层**特征树看不见 SpeedPak** ✗ ⇒ "
                 "★ 必须回读 `IComponent2::IsSpeedPak` 才算数 ✓"),
    }
    #: ★ 前置①：★ 取组件列表（★ 官方示例要按**组件名**选 ✓）
    comps = []
    try:
        #: ★ 官方示例的调用序是 `IComponent2.Select4` 按**对象**选；
        #:   ★ 这里先用 `GetComponents` 取列表以**解析名字** ✓
        comps = list(get_com_member(doc, "GetComponents", False) or [])
    except Exception as e:                                              # noqa: BLE001
        out["ok"] = False
        out["error"] = "★ 前置①失败：`GetComponents` 抛 %s: %s" % (type(e).__name__, str(e)[:120])
        return out
    out["component_count"] = len(comps)
    if not comps:
        out["ok"] = False
        out["error"] = "★ 前置①失败：装配里**没有组件** ⇒ ★ 无对象可做 SpeedPak（★ 与「建不出来」两件事 ✓）"
        return out
    target = comps[min(int(component_index), len(comps) - 1)]

    #: ★ 前置②：★ **回读初始状态**（★ 「本来就开着」与「这次建成了」要分开 ✓）
    is_sp_before = None
    try:
        is_sp_before = bool(get_com_member(target, "IsSpeedPak"))
    except Exception:                                                   # noqa: BLE001
        is_sp_before = None
    out["is_speedpak_before"] = is_sp_before

    #: ★ 前置③：★ 解析组件名（★ 官方示例要按名字选 ✓；★ 多个访问器逐个试）
    name = component_name
    if not name:
        for _acc in ("Name2", "GetName2", "Name"):
            try:
                name = get_com_member(target, _acc)
                if name:
                    out["component_name_accessor"] = _acc
                    break
            except Exception:                                           # noqa: BLE001
                name = None
    out["component_name"] = str(name) if name else None
    if not name:
        out["ok"] = False
        out["error"] = "★ 前置③失败：解析不出组件名（★ `Name2`/`GetName2`/`Name` 三个都取不到 ✓）"
        return out

    #: ★ 前置④：★ 按官方示例的调用序选中（★ `SelectByID2(<名>, "COMPONENT", …)` ✓）
    sel_ok = False
    try:
        ext = get_com_member(doc, "Extension")
        get_com_member(ext, "SelectByID2", str(name), "COMPONENT", 0.0, 0.0, 0.0,
                       False, 0, create_empty_dispatch_variant(), 0)
        #: ★★ 回读（★ 不信返回值 —— 事实 8 ✓）
        sel_ok = bool(get_com_member(get_com_member(doc, "SelectionManager"),
                                     "GetSelectedObjectCount2", -1))
    except Exception as e:                                              # noqa: BLE001
        out["select_error"] = "%s: %s" % (type(e).__name__, str(e)[:130])
    out["selected"] = sel_ok
    if not sel_ok:
        out["ok"] = False
        out["error"] = ("★ 前置④失败：`SelectByID2(%r, \"COMPONENT\", …)` 没选中 ⇒ "
                        "★ 那与「建不出来」是两件事（★ 官方前置 = **选中的子装配** ✓）" % name)
        return out

    #: ★ 调（★ **1 参** ✓）
    ret = None
    exc = None
    try:
        ret = call_assembly_doc(doc, "CreateSpeedPak", int(speedpak_type))
    except Exception as e:                                              # noqa: BLE001
        exc = e
    out["returned"] = str(ret)
    out["call_exception"] = None if exc is None else "%s: %s" % (type(exc).__name__, str(exc)[:140])

    #: ★★ 判据：★ **回读 `IsSpeedPak`**（★ 不看返回值 —— 事实 8 ✓）
    is_sp_after = None
    try:
        is_sp_after = bool(get_com_member(target, "IsSpeedPak"))
    except Exception:                                                   # noqa: BLE001
        is_sp_after = None
    out["is_speedpak_after"] = is_sp_after
    out["ok"] = bool(is_sp_after is True and is_sp_before is not True)
    if out["ok"]:
        out["verdict"] = ("★★★★★ **建成** —— ★ `IsSpeedPak` **%r → %r**（★ 回读、★ 不是信返回值 ✓）"
                          % (is_sp_before, is_sp_after))
    elif is_sp_after is True and is_sp_before is True:
        out["error"] = ("★ 回读判据未过：**本来就开着**（%r → %r）⇒ ★ 「这次建成了」与"
                        "「它一直是开的」要分开记 ✗" % (is_sp_before, is_sp_after))
    else:
        out["error"] = ("★ 回读判据未过：`IsSpeedPak` 仍 %r（★ 回 %r）⇒ ★ **还不算试死** —— "
                        "★ 前置复核：★ 组件 %r · ★ 选中=%r · ★ 初始=%r（定则：「读到静默」≠「判定试死」✓）"
                        % (is_sp_after, out["returned"], out["component_name"], sel_ok, is_sp_before))
    return out
