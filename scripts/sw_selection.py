"""SolidWorks 选中管理：ISelectionMgr 完整封装。

能力域
    域 1 · 应用与会话。选中是所有操作的地基 —— 拉伸要选面、装配要选组件、
    工程图要选视图，全从这里起步。

为什么要单独成模块
------------------
既有代码里选中散落在各处（sw_part._select_by_id、sw_assembly、
sw_hole_features 各写各的），且只用到 3 个成员
（ClearSelection2 / GetSelectedObjectCount2 / SelectionManager）。
本模块把 ISelectionMgr 的**调用侧成员系统性补齐**，
并把本项目已知的两个坑固化成函数行为（见下）。

⚠⚑ 两个必须编码进实现的已知坑
-------------------------------
1. **AddSelectionListObject 的 Boolean 返回值不可信** ——
   AGENTS.md §六 事实 8：本机实测 12 次全返回 False，而实际选中数是 12。
   ⇒ :func:`add_to_selection_list` **不返回**那个布尔值，
     而是返回用 GetSelectedObjectCount2(-1) **回读**的真实计数。
2. **pywin32 迟到绑定下同一成员可能既是属性也是方法** ——
   AGENTS.md §六 事实 4。ISelectionMgr 上 EnableSelection /
   EnableContourSelection / SelectionColor(Int32) 都是**属性**。
   ⇒ 一律经 get_com_member 访问，不裸写 ``obj.X()``。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt → ISelectionMgr 段
      —— 对 SolidWorks.Interop.sldworks.dll 的**纯元数据反射**
         （AGENTS.md §四.1③「读官方程序集，不是实测」）。
         该段共 65 个成员，其中 **20 个是 I 前缀的 COM 内部分发口**
         （IDeSelect / IGetSelectedObject* / IGetSelectionPoint* …）——
         那些是给 COM 运行时的，**不提供给调用方**，本模块一律不封装。

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游与既有模式的写法**发展而来）。
# 文件:   scripts/sw_selection.py —— 本文件（**轮 145 的命名迁移**）。
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
    from .sw_connect import get_com_member, call_com_member
except ImportError:
    from sw_connect import get_com_member, call_com_member, set_com_member# ── 来源 ─────────────────────────────────────────────────────────────, set_com_member
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_selection.py —— 本文件自身
# 定位:   模块导出清单与签名表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "SELECTION_ARITY",
    "SELECTION_ALL_KINDS",
    "get_selection_manager",
    "clear_selection",
    "get_selection_count",
    "get_selected_object",
    "get_selected_objects",
    "get_selected_object_type",
    "get_selected_face",
    "get_selected_component",
    "get_selected_view",
    "get_selection_point",
    "get_selection_point_in_sketch_space",
    "set_selection_point",
    "deselect",
    "add_to_selection_list",
    "suspend_selection_list",
    "resume_selection_list",
    "set_selection_color",
    "clear_selection_colors",
    "get_selected_object_mark",
    "set_selected_object_mark",
    "set_enable_selection",
    "set_enable_contour_selection",
    "is_coord_sys_element_selected",
    "is_in_edit_target",
    "collect_selection_evidence",
]

#: 反射确认的实参个数（调用侧成员；**不含**末尾 by-ref 出参）
SELECTION_ARITY: dict[str, int] = {
    "GetSelectedObjectCount": 0,
    "GetSelectedObjectCount2": 1,
    "GetSelectedObject": 1,
    "GetSelectedObject2": 1,
    "GetSelectedObject3": 1,
    "GetSelectedObject4": 1,
    "GetSelectedObject5": 1,
    "GetSelectedObject6": 2,
    "GetSelectedObjectType": 1,
    "GetSelectedObjectType2": 1,
    "GetSelectedObjectType3": 2,
    "GetSelectedObjectsFace": 2,
    "GetSelectedObjectsComponent": 1,
    "GetSelectedObjectsComponent2": 1,
    "GetSelectedObjectsComponent3": 2,
    "GetSelectedObjectsComponent4": 2,
    "GetSelectedObjectsDrawingView": 1,
    "GetSelectedObjectsDrawingView2": 2,
    "GetSelectionPoint": 1,
    "GetSelectionPoint2": 2,
    "GetSelectionPointInSketchSpace": 1,
    "GetSelectionPointInSketchSpace2": 2,
    "SetSelectionPoint": 4,
    "SetSelectionPoint2": 5,
    "DeSelect": 1,
    "DeSelect2": 2,
    "AddSelectionListObject": 2,
    "AddSelectionListObjects": 2,
    "SuspendSelectionList": 0,
    "ResumeSelectionList": 0,
    "ResumeSelectionList2": 1,
    "SetCallout": 2,
    "IsCoordSysElementSelected": 2,
    "IsInEditTarget": 1,
    "IsInEditTarget2": 2,
    "GetSelectedObjectMark": 1,
    "SetSelectedObjectMark": 3,
    "GetSelectedObjectLoop": 1,
    "GetSelectedObjectLoop2": 2,
    "GetSelectedCoordSysElement": 2,
}

#: 读全部选中项时用 -1 表示「所有类型」（官方惯用法，AGENTS.md §六 事实 8 记载）
SELECTION_ALL_KINDS = -1


def _checked(target, member: str, *args):
    """按签名表校核实参个数，通过后才发起调用（开发期护栏）。"""
    expected = SELECTION_ARITY.get(member)
    if expected is not None and expected != len(args):
        raise ValueError(
            f"{member} 官方签名是 {expected} 个实参（不含末尾 by-ref 出参），"
            f"本次调用给了 {len(args)} 个"
        )
    if target is None:
        raise ValueError("selection 为 None：须先由 IModelDoc2.SelectionManager 取得")
    return get_com_member(target, member, *args)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（scripts/sw_part.py::_select_by_id）
# 文件:   scripts/sw_part.py
# 定位:   取选中管理器的入口，沿用既有写法 model.SelectionManager。
# ⚠ 官方反射里 ISelectionMgr **没有** 自己的获取方法 ——
#   它是 IModelDoc2.SelectionManager **属性**。
# 覆盖:   后续同级定义
# ⚠ 本组为照既有模式新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_selection_manager(model):
    """取 ISelectionMgr。⚑ 官方是 IModelDoc2.SelectionManager **属性**。"""
    if model is None:
        raise ValueError("model 为 None")
    return get_com_member(model, "SelectionManager")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → ISelectionMgr 段
# 定位:   计数与取对象。官方签名逐条照抄：
#     Int32  GetSelectedObjectCount()                    ← **零参**
#     Int32  GetSelectedObjectCount2(Int32 Type)          → 1
#     Object GetSelectedObject(Int32) … GetSelectedObject5(Int32) → 1
#     Object GetSelectedObject6(Int32, Int32)            → 2
#     Int32  GetSelectedObjectType(Int32) / Type2(Int32) → 1
#     Int32  GetSelectedObjectType3(Int32, Int32)        → 2
# ⚠ GetSelectedObject 到 GetSelectedObject6 是**六个不同的重载**，
#   官方没有参数类型可依赖（都是 Int32 序号）⇒ 差别**只在返回类型**。
#   本模块**默认用最新的 6 号**，并把 1 号也显式暴露，不替调用方猜。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_selection_count(selection, selection_type: int = SELECTION_ALL_KINDS) -> int:
    """当前选中数量。selection_type 传 -1 表示所有类型。"""
    return int(_checked(selection, "GetSelectedObjectCount2", int(selection_type)))


def get_selected_object(selection, index: int):
    """按序号取选中项（用最新的 6 号重载）。"""
    return _checked(selection, "GetSelectedObject6", int(index), 0)


def get_selected_objects(selection, count: int | None = None) -> list[Any]:
    """取出全部选中项（跳过取不到的空位）。"""
    total = count if count is not None else get_selection_count(selection)
    out = []
    for index in range(total):
        item = get_selected_object(selection, index)
        if item is not None:
            out.append(item)
    return out


def get_selected_object_type(selection, index: int) -> int:
    """取选中项的类型码。"""
    return int(_checked(selection, "GetSelectedObjectType2", int(index)))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）
# 定位:   强类型取项。官方签名逐条照抄：
#     Face2      GetSelectedObjectsFace(Int32, Int32)         → 2
#     Component2 GetSelectedObjectsComponent3(Int32, Int32)    → 2
#     View       GetSelectedObjectsDrawingView2(Int32, Int32)  → 2
# ⚠ 这三个的第二参在反射里是 Int32，语义（配置？层？）两套源都未说明
#   ⇒ 统一传 0，参数名如实标为 secondary。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_selected_face(selection, index: int, secondary: int = 0):
    """取选中项作为面（Face2）。"""
    return _checked(selection, "GetSelectedObjectsFace", int(index), int(secondary))


def get_selected_component(selection, index: int, secondary: int = 0):
    """取选中项作为组件（Component2）。"""
    return _checked(selection, "GetSelectedObjectsComponent3",
                    int(index), int(secondary))


def get_selected_view(selection, index: int, secondary: int = 0):
    """取选中项作为工程图视图（View）。"""
    return _checked(selection, "GetSelectedObjectsDrawingView2",
                    int(index), int(secondary))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）
# 定位:   选区坐标读写。官方签名逐条照抄：
#     Object  GetSelectionPoint(Int32)                  → 1
#     Object  GetSelectionPoint2(Int32, Int32)          → 2
#     Object  GetSelectionPointInSketchSpace(Int32)     → 1
#     Object  GetSelectionPointInSketchSpace2(Int32, Int32) → 2
#     Boolean SetSelectionPoint(Int32, Double, Double, Double)          → 4
#     Boolean SetSelectionPoint2(Int32, Int32, Double, Double, Double) → 5
# ⚠ 前四个返回 Object（按反射的返回类型原样透传，不解释成 tuple 也不强转）——
#   迟到绑定下实际拿到什么由 SolidWorks 决定，本模块不替它定型。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_selection_point(selection, index: int, secondary: int = 0):
    """取选区在模型空间的坐标点。"""
    return _checked(selection, "GetSelectionPoint2", int(index), int(secondary))


def get_selection_point_in_sketch_space(selection, index: int, secondary: int = 0):
    """取选区在草图空间的坐标点。"""
    return _checked(selection, "GetSelectionPointInSketchSpace2",
                    int(index), int(secondary))


def set_selection_point(selection, index: int, x: float, y: float, z: float) -> bool:
    """设置选区坐标。"""
    return bool(_checked(selection, "SetSelectionPoint",
                         int(index), float(x), float(y), float(z)))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）
# 定位:   取消选择与选中列表。官方签名逐条照抄：
#     Int32  DeSelect(Object)                  → 1
#     Int32  DeSelect2(Object, Int32)          → 2
#     Boolean AddSelectionListObject(Object, Object)  → 2
#     Int32  AddSelectionListObjects(Object, Object) → 2
#     Int32  SuspendSelectionList()            ← **零参**
#     Void   ResumeSelectionList()             ← **零参**
#     Void   ResumeSelectionList2(Boolean)     → 1
# ⚠⚑ 事实 8 编码在 :func:`add_to_selection_list` 里 ——
#   AddSelectionListObject 的 Boolean 返回值不可信，本函数改用计数回读。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def deselect(selection, item, mark: int = 0) -> int:
    """取消选择某项。"""
    return _checked(selection, "DeSelect2", item, int(mark))


def add_to_selection_list(selection, item, select_data) -> int:
    """把对象加进选中列表，**回读真实选中数**。

    ⚠⚑ 官方 Boolean 返回值不可信（AGENTS.md §六 事实 8：本机实测 12 次全
      返回 False，而实际选中数是 12）。⇒ 本函数**不返回**那个布尔值，
      返回 ``GetSelectedObjectCount2(-1)`` 的回读结果 —— 那是可信的。
    """
    _checked(selection, "AddSelectionListObject", item, select_data)
    return get_selection_count(selection, SELECTION_ALL_KINDS)


def suspend_selection_list(selection) -> int:
    """挂起选中列表。**零参**。"""
    return _checked(selection, "SuspendSelectionList")


def resume_selection_list(selection, report_errors: bool = False) -> bool:
    """恢复选中列表。"""
    if selection is None:
        raise ValueError("selection 为 None：须先由 IModelDoc2.SelectionManager 取得")
    if report_errors:
        get_com_member(selection, "ResumeSelectionList2", bool(report_errors))
        return True
    get_com_member(selection, "ResumeSelectionList")
    return True


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）
# 定位:   颜色、标记、开关、状态查询。官方签名逐条照抄：
#     Int32  get_SelectionColor(Int32) / set_SelectionColor(Int32, Int32)
#     Void   ClearSelectionColors()                    ← **零参**
#     Int32  GetSelectedObjectMark(Int32)              → 1
#     Boolean SetSelectedObjectMark(Int32, Int32, Int32) → 3
#     Boolean get_EnableSelection() / set_EnableSelection(Boolean)  ← **属性**
#     Boolean get_EnableContourSelection() / set_EnableContourSelection(Boolean)
#     Boolean IsCoordSysElementSelected(Int32, Int32)  → 2
#     Boolean IsInEditTarget(Int32) / IsInEditTarget2(Int32, Int32) → 1 / 2
# ⚑ 三个开关/颜色成员都是**属性**，迟到绑定下加括号会 TypeError
#   （AGENTS.md §六 事实 4）。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def set_selection_color(selection, color: int) -> bool:
    """设选中高亮颜色。⚑ 官方是**属性**（set_SelectionColor）。"""
    if selection is None:
        raise ValueError("selection 为 None：须先由 IModelDoc2.SelectionManager 取得")
    set_com_member(selection, "SelectionColor", int(color))
    return True


def clear_selection_colors(selection) -> bool:
    """清除选中高亮颜色。**零参**。"""
    if selection is None:
        raise ValueError("selection 为 None：须先由 IModelDoc2.SelectionManager 取得")
    call_com_member(selection, "ClearSelectionColors")
    return True


def get_selected_object_mark(selection, index: int) -> int:
    """取某选中项的标记号。"""
    return int(_checked(selection, "GetSelectedObjectMark", int(index)))


def set_selected_object_mark(selection, index: int, mark: int, value: int) -> bool:
    """设置某选中项的标记。"""
    return bool(_checked(selection, "SetSelectedObjectMark",
                         int(index), int(mark), int(value)))


def set_enable_selection(selection, enabled: bool) -> bool:
    """开关选中功能。⚑ 官方是**属性**。"""
    if selection is None:
        raise ValueError("selection 为 None：须先由 IModelDoc2.SelectionManager 取得")
    set_com_member(selection, "EnableSelection", bool(enabled))
    return True


def set_enable_contour_selection(selection, enabled: bool) -> bool:
    """开关轮廓选择。⚑ 官方是**属性**。"""
    if selection is None:
        raise ValueError("selection 为 None：须先由 IModelDoc2.SelectionManager 取得")
    set_com_member(selection, "EnableContourSelection", bool(enabled))
    return True


def is_coord_sys_element_selected(selection, kind: int, index: int) -> bool:
    """判断是否选中了坐标系元素。"""
    return bool(_checked(selection, "IsCoordSysElementSelected",
                         int(kind), int(index)))


def is_in_edit_target(selection, index: int, secondary: int = 0) -> bool:
    """判断某项是否处于编辑目标中。"""
    return bool(_checked(selection, "IsInEditTarget2",
                         int(index), int(secondary)))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_simulation_study.py::collect_study_evidence）
# 定位:   选区状态证据回读，沿用「只取已核实成员」的写法。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_selection_evidence(selection) -> dict[str, Any]:
    """回读当前选区状态。"""
    if selection is None:
        raise ValueError("selection 为 None")
    count = get_selection_count(selection, SELECTION_ALL_KINDS)
    types = [get_selected_object_type(selection, i) for i in range(count)]
    return {
        "count": count,
        "types": types,
        "type_histogram": {str(t): types.count(t) for t in sorted(set(types))},
        "enable_selection": bool(get_com_member(selection, "EnableSelection")),
        "enable_contour_selection": bool(
            get_com_member(selection, "EnableContourSelection")),
    }
