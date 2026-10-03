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


def dissolve_assembly(doc) -> int:
    """解散子装配。

    ⚠ 官方是 ``DissolveSubAssembly()``，**没有** ``DissolveAll``。
    """
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
