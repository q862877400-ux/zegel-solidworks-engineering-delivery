r"""SolidWorks swpublished 官方接口全量索引。

能力域
    加载项开发框架（属性管理页回调、消息栏）

本模块是什么
------------
**官方 API 的完整抄录** —— 31 个接口族、**354 个成员**，
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
    D:\AI\SW\_raw\reflect\iface_swpublished.txt
      对 **SolidWorks.Interop.swpublished.dll** 的纯元数据反射（AGENTS.md §四.1③）。
    ⚠ 属「读官方程序集」，**不是实测**（铁律 2）。

⚠ 本模块为机械抄录，未在本机实测（见 AGENTS.md 铁律 2）。
"""

from __future__ import annotations


try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   官方 interop 程序集的纯元数据反射（SolidWorks.Interop.swpublished.dll）
# 文件:   D:\AI\SW\_raw\reflect\iface_swpublished.txt
# 定位:   31 个接口族的**全量**能力登记表 {族: {能力名: 实参个数}}。
# ⚑ 逐条机械生成，**不手抄、不折叠、不合并重载**。
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = ["ASSEMBLY", "FAMILIES", "ARITY", "PROPERTIES", "call_index"]

ASSEMBLY = "swpublished"

FAMILIES: tuple[str, ...] = (
    "IMessageBarHandler",
    "IPropertyManagerPage2Handler",
    "IPropertyManagerPage2Handler2",
    "IPropertyManagerPage2Handler3",
    "IPropertyManagerPage2Handler4",
    "IPropertyManagerPage2Handler5",
    "IPropertyManagerPage2Handler6",
    "IPropertyManagerPage2Handler7",
    "IPropertyManagerPage2Handler8",
    "IPropertyManagerPage2Handler9",
    "IPropertyManagerPageHandler",
    "IPropertyManagerPageHandler2",
    "IPtnrPMPageHandler",
    "IPtnrPMPageHandler2",
    "IPtnrPMPageHandler3",
    "ISwAddin",
    "ISwAddinAdvancedOptionBroker",
    "ISwAddinBroker",
    "ISwAddinLicenseManager",
    "ISwCalloutHandler",
    "ISwColorContour",
    "ISwColorContour1",
    "ISwComFeature",
    "ISwManipulatorHandler",
    "ISwManipulatorHandler2",
    "ISwPEManager",
    "ISwPointInferenceBroker",
    "ISwQuickTip",
    "ISwUndoAPIHandler",
    "ITaskpaneViewHandler",
    "IUserNotificationHandler",
)

#: 全量能力登记表 {族: {能力名: 实参个数}}（排除 by-ref 出参）
ARITY: dict[str, dict[str, int]] = {
    "IMessageBarHandler": {
        "OnUserClose": 0,
        "OnUserResponseA": 1,
        "OnUserResponseB": 1,
    },
    "IPropertyManagerPage2Handler": {
        "AfterClose": 0,
        "OnButtonPress": 1,
        "OnCheckboxCheck": 2,
        "OnClose": 1,
        "OnComboboxSelectionChanged": 2,
        "OnGroupCheck": 2,
        "OnGroupExpand": 2,
        "OnHelp": 0,
        "OnListboxSelectionChanged": 2,
        "OnNumberboxChanged": 2,
        "OnOptionCheck": 1,
        "OnSelectionboxFocusChanged": 1,
        "OnSelectionboxListChanged": 2,
        "OnTextboxChanged": 2,
    },
    "IPropertyManagerPage2Handler2": {
        "AfterClose": 0,
        "OnActiveXControlCreated": 2,
        "OnButtonPress": 1,
        "OnCheckboxCheck": 2,
        "OnClose": 1,
        "OnComboboxEditChanged": 2,
        "OnComboboxSelectionChanged": 2,
        "OnGroupCheck": 2,
        "OnGroupExpand": 2,
        "OnHelp": 0,
        "OnListboxSelectionChanged": 2,
        "OnNextPage": 0,
        "OnNumberboxChanged": 2,
        "OnOptionCheck": 1,
        "OnPreviousPage": 0,
        "OnSelectionboxCalloutCreated": 1,
        "OnSelectionboxCalloutDestroyed": 1,
        "OnSelectionboxFocusChanged": 1,
        "OnSelectionboxListChanged": 2,
        "OnTextboxChanged": 2,
    },
    "IPropertyManagerPage2Handler3": {
        "AfterClose": 0,
        "OnActiveXControlCreated": 2,
        "OnButtonPress": 1,
        "OnCheckboxCheck": 2,
        "OnClose": 1,
        "OnComboboxEditChanged": 2,
        "OnComboboxSelectionChanged": 2,
        "OnGroupCheck": 2,
        "OnGroupExpand": 2,
        "OnHelp": 0,
        "OnListboxSelectionChanged": 2,
        "OnNextPage": 0,
        "OnNumberboxChanged": 2,
        "OnOptionCheck": 1,
        "OnPreview": 0,
        "OnPreviousPage": 0,
        "OnSelectionboxCalloutCreated": 1,
        "OnSelectionboxCalloutDestroyed": 1,
        "OnSelectionboxFocusChanged": 1,
        "OnSelectionboxListChanged": 2,
        "OnSliderPositionChanged": 2,
        "OnSubmitSelection": 3,
        "OnTabClicked": 1,
        "OnTextboxChanged": 2,
        "OnWhatsNew": 0,
    },
    "IPropertyManagerPage2Handler4": {
        "AfterClose": 0,
        "OnActiveXControlCreated": 2,
        "OnButtonPress": 1,
        "OnCheckboxCheck": 2,
        "OnClose": 1,
        "OnComboboxEditChanged": 2,
        "OnComboboxSelectionChanged": 2,
        "OnGroupCheck": 2,
        "OnGroupExpand": 2,
        "OnHelp": 0,
        "OnKeystroke": 4,
        "OnListboxSelectionChanged": 2,
        "OnNextPage": 0,
        "OnNumberboxChanged": 2,
        "OnOptionCheck": 1,
        "OnPopupMenuItem": 1,
        "OnPopupMenuItemUpdate": 1,
        "OnPreview": 0,
        "OnPreviousPage": 0,
        "OnSelectionboxCalloutCreated": 1,
        "OnSelectionboxCalloutDestroyed": 1,
        "OnSelectionboxFocusChanged": 1,
        "OnSelectionboxListChanged": 2,
        "OnSliderPositionChanged": 2,
        "OnSliderTrackingCompleted": 2,
        "OnSubmitSelection": 3,
        "OnTabClicked": 1,
        "OnTextboxChanged": 2,
        "OnUndo": 0,
        "OnWhatsNew": 0,
    },
    "IPropertyManagerPage2Handler5": {
        "AfterActivation": 0,
        "AfterClose": 0,
        "OnActiveXControlCreated": 2,
        "OnButtonPress": 1,
        "OnCheckboxCheck": 2,
        "OnClose": 1,
        "OnComboboxEditChanged": 2,
        "OnComboboxSelectionChanged": 2,
        "OnGroupCheck": 2,
        "OnGroupExpand": 2,
        "OnHelp": 0,
        "OnKeystroke": 4,
        "OnListboxSelectionChanged": 2,
        "OnNextPage": 0,
        "OnNumberboxChanged": 2,
        "OnOptionCheck": 1,
        "OnPopupMenuItem": 1,
        "OnPopupMenuItemUpdate": 1,
        "OnPreview": 0,
        "OnPreviousPage": 0,
        "OnSelectionboxCalloutCreated": 1,
        "OnSelectionboxCalloutDestroyed": 1,
        "OnSelectionboxFocusChanged": 1,
        "OnSelectionboxListChanged": 2,
        "OnSliderPositionChanged": 2,
        "OnSliderTrackingCompleted": 2,
        "OnSubmitSelection": 3,
        "OnTabClicked": 1,
        "OnTextboxChanged": 2,
        "OnUndo": 0,
        "OnWhatsNew": 0,
    },
    "IPropertyManagerPage2Handler6": {
        "AfterActivation": 0,
        "AfterClose": 0,
        "OnActiveXControlCreated": 2,
        "OnButtonPress": 1,
        "OnCheckboxCheck": 2,
        "OnClose": 1,
        "OnComboboxEditChanged": 2,
        "OnComboboxSelectionChanged": 2,
        "OnGroupCheck": 2,
        "OnGroupExpand": 2,
        "OnHelp": 0,
        "OnKeystroke": 4,
        "OnListboxSelectionChanged": 2,
        "OnNextPage": 0,
        "OnNumberboxChanged": 2,
        "OnOptionCheck": 1,
        "OnPopupMenuItem": 1,
        "OnPopupMenuItemUpdate": 1,
        "OnPreview": 0,
        "OnPreviousPage": 0,
        "OnRedo": 0,
        "OnSelectionboxCalloutCreated": 1,
        "OnSelectionboxCalloutDestroyed": 1,
        "OnSelectionboxFocusChanged": 1,
        "OnSelectionboxListChanged": 2,
        "OnSliderPositionChanged": 2,
        "OnSliderTrackingCompleted": 2,
        "OnSubmitSelection": 3,
        "OnTabClicked": 1,
        "OnTextboxChanged": 2,
        "OnUndo": 0,
        "OnWhatsNew": 0,
    },
    "IPropertyManagerPage2Handler7": {
        "AfterActivation": 0,
        "AfterClose": 0,
        "OnActiveXControlCreated": 2,
        "OnButtonPress": 1,
        "OnCheckboxCheck": 2,
        "OnClose": 1,
        "OnComboboxEditChanged": 2,
        "OnComboboxSelectionChanged": 2,
        "OnGainedFocus": 1,
        "OnGroupCheck": 2,
        "OnGroupExpand": 2,
        "OnHelp": 0,
        "OnKeystroke": 4,
        "OnListboxSelectionChanged": 2,
        "OnLostFocus": 1,
        "OnNextPage": 0,
        "OnNumberboxChanged": 2,
        "OnOptionCheck": 1,
        "OnPopupMenuItem": 1,
        "OnPopupMenuItemUpdate": 1,
        "OnPreview": 0,
        "OnPreviousPage": 0,
        "OnRedo": 0,
        "OnSelectionboxCalloutCreated": 1,
        "OnSelectionboxCalloutDestroyed": 1,
        "OnSelectionboxFocusChanged": 1,
        "OnSelectionboxListChanged": 2,
        "OnSliderPositionChanged": 2,
        "OnSliderTrackingCompleted": 2,
        "OnSubmitSelection": 3,
        "OnTabClicked": 1,
        "OnTextboxChanged": 2,
        "OnUndo": 0,
        "OnWhatsNew": 0,
    },
    "IPropertyManagerPage2Handler8": {
        "AfterActivation": 0,
        "AfterClose": 0,
        "OnActiveXControlCreated": 2,
        "OnButtonPress": 1,
        "OnCheckboxCheck": 2,
        "OnClose": 1,
        "OnComboboxEditChanged": 2,
        "OnComboboxSelectionChanged": 2,
        "OnGainedFocus": 1,
        "OnGroupCheck": 2,
        "OnGroupExpand": 2,
        "OnHelp": 0,
        "OnKeystroke": 4,
        "OnListboxRMBUp": 3,
        "OnListboxSelectionChanged": 2,
        "OnLostFocus": 1,
        "OnNextPage": 0,
        "OnNumberboxChanged": 2,
        "OnOptionCheck": 1,
        "OnPopupMenuItem": 1,
        "OnPopupMenuItemUpdate": 1,
        "OnPreview": 0,
        "OnPreviousPage": 0,
        "OnRedo": 0,
        "OnSelectionboxCalloutCreated": 1,
        "OnSelectionboxCalloutDestroyed": 1,
        "OnSelectionboxFocusChanged": 1,
        "OnSelectionboxListChanged": 2,
        "OnSliderPositionChanged": 2,
        "OnSliderTrackingCompleted": 2,
        "OnSubmitSelection": 3,
        "OnTabClicked": 1,
        "OnTextboxChanged": 2,
        "OnUndo": 0,
        "OnWhatsNew": 0,
        "OnWindowFromHandleControlCreated": 2,
    },
    "IPropertyManagerPage2Handler9": {
        "AfterActivation": 0,
        "AfterClose": 0,
        "OnActiveXControlCreated": 2,
        "OnButtonPress": 1,
        "OnCheckboxCheck": 2,
        "OnClose": 1,
        "OnComboboxEditChanged": 2,
        "OnComboboxSelectionChanged": 2,
        "OnGainedFocus": 1,
        "OnGroupCheck": 2,
        "OnGroupExpand": 2,
        "OnHelp": 0,
        "OnKeystroke": 4,
        "OnListboxRMBUp": 3,
        "OnListboxSelectionChanged": 2,
        "OnLostFocus": 1,
        "OnNextPage": 0,
        "OnNumberboxChanged": 2,
        "OnNumberBoxTrackingCompleted": 2,
        "OnOptionCheck": 1,
        "OnPopupMenuItem": 1,
        "OnPopupMenuItemUpdate": 1,
        "OnPreview": 0,
        "OnPreviousPage": 0,
        "OnRedo": 0,
        "OnSelectionboxCalloutCreated": 1,
        "OnSelectionboxCalloutDestroyed": 1,
        "OnSelectionboxFocusChanged": 1,
        "OnSelectionboxListChanged": 2,
        "OnSliderPositionChanged": 2,
        "OnSliderTrackingCompleted": 2,
        "OnSubmitSelection": 3,
        "OnTabClicked": 1,
        "OnTextboxChanged": 2,
        "OnUndo": 0,
        "OnWhatsNew": 0,
        "OnWindowFromHandleControlCreated": 2,
    },
    "IPropertyManagerPageHandler": {
        "DoDataExchange": 1,
        "OnCancel": 0,
        "OnOK": 0,
    },
    "IPropertyManagerPageHandler2": {
        "DoDataExchange": 1,
        "OnCancel": 0,
        "OnHelp": 0,
        "OnOK": 0,
    },
    "IPtnrPMPageHandler": {
        "DoDataExchange": 1,
        "getBackPageIndex": 0,
        "getNextPageIndex": 0,
        "OnCancel": 0,
        "OnHelp": 0,
        "OnInitDialog": 0,
        "OnOK": 0,
        "OnUndo": 0,
        "PreDestroyNotify": 1,
    },
    "IPtnrPMPageHandler2": {
        "DoDataExchange": 1,
        "getBackPageIndex": 0,
        "getNextPageIndex": 0,
        "OnCancel": 0,
        "OnHelp": 0,
        "OnInitDialog": 0,
        "OnOK": 0,
        "OnPreview": 0,
        "OnUndo": 0,
        "PreDestroyNotify": 1,
    },
    "IPtnrPMPageHandler3": {
        "DoDataExchangex64": 1,
        "getBackPageIndex": 0,
        "getNextPageIndex": 0,
        "OnCancel": 0,
        "OnHelp": 0,
        "OnInitDialog": 0,
        "OnOK": 0,
        "OnPreview": 0,
        "OnUndo": 0,
        "PreDestroyNotify": 1,
    },
    "ISwAddin": {
        "ConnectToSW": 2,
        "DisconnectFromSW": 0,
    },
    "ISwAddinAdvancedOptionBroker": {
        "GetMessageIDs": 0,
        "SetMessageIDs": 1,
    },
    "ISwAddinBroker": {
        "GetInferencePoints": 5,
        "GetSelectedObjectsBBox": 2,
    },
    "ISwAddinLicenseManager": {
        "AcquireLicense": 0,
        "IsHoldingLicense": 0,
        "ReleaseLicense": 0,
    },
    "ISwCalloutHandler": {
        "OnStringValueChanged": 3,
    },
    "ISwColorContour": {
        "Color": 1,
        "DisplayString": 1,
        "NeedsUpdate": 0,
        "Value": 1,
    },
    "ISwColorContour1": {
        "Color": 1,
        "DisplayString": 1,
        "NeedsUpdate": 0,
        "Value": 7,
    },
    "ISwComFeature": {
        "Edit": 3,
        "Regenerate": 3,
        "Security": 3,
    },
    "ISwManipulatorHandler": {
        "OnDelete": 1,
        "OnDirectionFlipped": 1,
        "OnDoubleValueChanged": 2,
        "OnEndDrag": 1,
        "OnEndNoDrag": 2,
        "OnHandleRmbSelected": 2,
        "OnHandleSelected": 2,
        "OnItemSetFocus": 2,
        "OnLmbSelected": 1,
        "OnStringValueChanged": 2,
        "OnUpdateDrag": 3,
    },
    "ISwManipulatorHandler2": {
        "OnDelete": 1,
        "OnDirectionFlipped": 1,
        "OnDoubleValueChanged": 2,
        "OnEndDrag": 2,
        "OnEndNoDrag": 2,
        "OnHandleLmbSelected": 1,
        "OnHandleRmbSelected": 2,
        "OnHandleSelected": 2,
        "OnItemSetFocus": 2,
        "OnStringValueChanged": 2,
        "OnUpdateDrag": 3,
    },
    "ISwPEManager": {
        "IdentifyToSW": 1,
    },
    "ISwPointInferenceBroker": {
        "GetInferencePoints": 5,
    },
    "ISwQuickTip": {
        "AppState": 1,
        "SwState": 1,
    },
    "ISwUndoAPIHandler": {
        "DoUndo": 0,
        "UndoReSet": 0,
    },
    "ITaskpaneViewHandler": {
        "OnActivate": 0,
        "OnDeactivate": 0,
        "OnDestroy": 0,
    },
    "IUserNotificationHandler": {
        "OnTimeout": 0,
        "OnUserClose": 0,
        "OnUserResponseA": 1,
        "OnUserResponseB": 1,
    },
}

#: 属性名（反射里是 get_/set_，**不是方法**；这里只留去掉前缀的名字）
PROPERTIES: dict[str, tuple[str, ...]] = {
    "IMessageBarHandler": (),
    "IPropertyManagerPage2Handler": (),
    "IPropertyManagerPage2Handler2": (),
    "IPropertyManagerPage2Handler3": (),
    "IPropertyManagerPage2Handler4": (),
    "IPropertyManagerPage2Handler5": (),
    "IPropertyManagerPage2Handler6": (),
    "IPropertyManagerPage2Handler7": (),
    "IPropertyManagerPage2Handler8": (),
    "IPropertyManagerPage2Handler9": (),
    "IPropertyManagerPageHandler": (),
    "IPropertyManagerPageHandler2": (),
    "IPtnrPMPageHandler": (),
    "IPtnrPMPageHandler2": (),
    "IPtnrPMPageHandler3": (),
    "ISwAddin": (),
    "ISwAddinAdvancedOptionBroker": (),
    "ISwAddinBroker": (),
    "ISwAddinLicenseManager": (),
    "ISwCalloutHandler": (),
    "ISwColorContour": (),
    "ISwColorContour1": (),
    "ISwComFeature": (),
    "ISwManipulatorHandler": (),
    "ISwManipulatorHandler2": (),
    "ISwPEManager": (),
    "ISwPointInferenceBroker": (),
    "ISwQuickTip": (
        "ApplicationName",
        "HideGuide",
        "MenuName",
        "ShowInAssemblyDoc",
        "ShowInDrawingDoc",
        "ShowInPartDoc",
        "Url",
    ),
    "ISwUndoAPIHandler": (),
    "ITaskpaneViewHandler": (),
    "IUserNotificationHandler": (),
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
#: dispatch-guard: exempt generated-api
def call_index(obj, family: str, member: str, *args):
    """按登记表校核实参个数，通过后调用该族的成员。

    :raises KeyError: 族名或成员名不在登记表里（**不静默忽略**）
    :raises ValueError: 实参个数对不上（在**发起调用之前**就报）
    """
    sub = ARITY.get(family)
    if sub is None:
        raise KeyError(
            f"本清单没有这个族: {family}（swpublished 共 {len(ARITY)} 族）。"
            f"⚠ 别的程序集请用对应的 call_index。"
        )
    expected = sub.get(member)
    if expected is None:
        raise KeyError(
            f"{family} 上没有名为 {member} 的能力（该族登记 {len(sub)} 项）。"
            f"⚠ 若它是属性或 COM 内部分发口，请用对应封装。"
        )
    if expected != len(args):
        raise ValueError(
            f"{family}.{member} 官方签名是 {expected} 个实参"
            f"（不含末位 by-ref 出参），本次调用给了 {len(args)} 个"
        )
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
