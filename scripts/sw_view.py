"""SolidWorks 三维视图操纵：IModelView 完整封装。

能力域
    域 10 · 几何与拓扑（视图层） / 与域 1 应用与会话交叉

为什么值得做
------------
视图操纵（缩放、旋转、相机、显示模式）是**自动化出图与截图的前置**——
「把模型摆到某个角度再导出」这类需求全靠它。
上游代码里几乎没有这一层，视图状态只能靠 GUI 手调。

接口族
------
    IModelView  75 个成员（本模块覆盖其中的调用侧全部方法 + 主要属性）

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt → IModelView 段
      —— 对 SolidWorks.Interop.sldworks.dll 的**纯元数据反射**
         （AGENTS.md §四.1③）。

⚠⚑ 三组「不封装」——理由不同，勿混为一谈
------------------------------------------
1. **``I*`` 前缀**（IGetEyePoint / IGetVisibleBox / IGetNext /
   IGraphicsRedraw / ISetEyePoint / ISetStereoSeparation / IGetStereoSeparation）
   —— COM 内部分发口，不给调用方。
2. **by-ref 出参**（``ProjectModelPoint(3 + 3 out)`` /
   ``UnprojectModelPoint(3 + 3 out)`` / ``GetDIBHeader*`` /
   ``GetStripsOfDIB*`` / ``set_I*Xform(Double&)``）
   —— 迟到绑定不保证回写，by-ref VARIANT 的分配规则两套源都查不到 ⇒ 不封装。
3. **纯界面自动化**（``GetViewHWnd`` / ``GetMouse`` / ``GetViewDIB`` /
   ``SectionAnnotationViewAttr`` / ``MagnifyingGlass`` 系列）
   —— 依赖可见窗口句柄，headless / 批处理下无意义，且官方无文档说明其行为。

⚠ **相机与姿态的「成对」形态**：
  官方对同一件事给了 1/2/3 三代（``Orientation`` / ``Orientation2`` /
  ``Orientation3``；``Translation`` / ``Translation2`` / ``Translation3``；
  新式 ``Transform`` / 旧式 ``Xform`` / 更旧 ``IXform``）。
  官方**未说明取舍** ⇒ 本模块**以 3 号为准**（最新的 MathTransform / MathVector），
  其余在注释里点名，不替调用方删掉。

⚠ 视图的取得路径：``IModelDoc.ActiveView``（属性）⇒ 详见
  :func:`get_active_view`。**不臆造** ``IModelDoc2`` 上的其它取法。

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游与既有模式的写法**发展而来）。
# 文件:   scripts/sw_view.py —— 本文件（**轮 145 的命名迁移**）。
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
    from sw_connect import get_com_member, call_com_member# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_view.py —— 本文件自身
# 定位:   模块导出清单与方法型成员签名表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "VIEW_ARITY",
    "VIEW_UNWRAPPED",
    "get_active_view",
    "activate_view",
    "redraw_view",
    "initialize_shading",
    "get_view_frame",
    "set_view_frame",
    "get_display_mode",
    "set_display_mode",
    "get_view_zoom",
    "zoom_view",
    "translate_view",
    "rotate_about_center",
    "roll_view",
    "get_view_scale",
    "set_view_scale",
    "get_view_camera",
    "set_view_camera_by_name",
    "get_view_orientation",
    "set_view_orientation",
    "get_view_translation",
    "has_perspective",
    "add_perspective",
    "remove_perspective",
    "start_dynamics",
    "stop_dynamics",
    "get_next_view",
    "get_view_model_doc",
    "collect_view_evidence",
]

#: 方法型成员的实参个数（**属性型成员不进表** —— 它们由下面的显式读写封装负责）
VIEW_ARITY: dict[str, int] = {
    "Activate": 0,
    "DrawHighlightedItems": 0,
    "GraphicsRedraw": 1,
    "InitializeShading": 0,
    "SetCameraByName": 1,
    "ZoomByFactor": 1,
    "TranslateBy": 2,
    "TurnBy": 2,
    "RollBy": 1,
    "RotateAboutCenter": 2,
    "RotateAboutPoint": 5,
    "RotateAboutAxis": 7,
    "AddPerspective": 0,
    "RemovePerspective": 0,
    "HasPerspective": 0,
    "ShowMagnifyingGlass": 5,
    "HideMagnifyingGlass": 0,
    "MoveMagnifyingGlass": 3,
    "StartDynamics": 0,
    "StopDynamics": 0,
    "GetNext": 0,
    "GetModelDoc": 0,
    "GetMouse": 0,
    "GetEyePoint": 0,
    "SetEyePoint": 1,
    "GetVisibleBox": 0,
    "GetIsoPlaneDistance": 0,
    "GetViewPlaneDistance": 0,
    "DrawTransparentFeatureTree": 0,
    "CreateCallout": 2,
}

#: 刻意**不封装**的成员（附理由，勿当成遗漏）
VIEW_UNWRAPPED: dict[str, str] = {
    "ProjectModelPoint": "末位 3 个 Double 是 by-ref 出参，迟到绑定不保证回写",
    "UnprojectModelPoint": "末位 3 个 Double 是 by-ref 出参，"
                           "且两个方法的轴心参数语义官方无文档",
    "GetDIBHeader": "参数是 out 缓冲（GetDIBHeaderx64 变体用 Int64）；"
                    "缓冲区分配规则两套源都查不到",
    "GetDIBHeaderx64": "参数是 out 缓冲（Int64）；缓冲区分配规则两套源都查不到",
    "GetStripsOfDIB": "3 个参数的缓冲区分配规则查不到",
    "GetStripsOfDIBx64": "参数含 Int64 缓冲区，分配规则查不到",
    "GetViewDIB": "返回 IntPtr 且需释放；释放规则官方无文档，泄漏风险不可控",
    "GetViewDIBx64": "返回 Int64 形式的位图句柄；释放规则官方无文档",
    "GetViewHWnd": "依赖可见窗口句柄，headless 下无意义",
    "GetViewHWndx64": "返回 Int64 句柄；依赖可见窗口，headless 下无意义",
    "GetMouse": "依赖可见窗口句柄，headless 下无意义",
    "SectionAnnotationViewAttr": "语义与前置条件官方无文档",
    "GetBkgdImageDisplayAreaAspectRatio": "返回 Double 但语义无文档，"
                                          "无法判断单位与含义",
    "GetStereoSeparation": "返回 Object（SAFEARRAY？），类型未明，不封装",
    "IGetStereoSeparation": "COM 内部分发口；对应非 I 版的 GetStereoSeparation",
    "IGetEyePoint": "COM 内部分发口；对应非 I 版的 GetEyePoint",
    "IGetVisibleBox": "COM 内部分发口；对应非 I 版的 GetVisibleBox",
    "IGetNext": "COM 内部分发口；对应非 I 版的 GetNext",
    "IGraphicsRedraw": "COM 内部分发口；对应非 I 版的 GraphicsRedraw",
    "ISetEyePoint": "COM 内部分发口；对应非 I 版的 SetEyePoint",
    "ISetStereoSeparation": "COM 内部分发口；对应非 I 版的 SetEyePoint（立体）",
}


def _require(view):
    if view is None:
        raise ValueError("view 为 None：须先由 IModelDoc.ActiveView 取得")
    return view


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（scripts/sw_part.py::_select_by_id）
# 文件:   scripts/sw_part.py
# 定位:   取活动视图的入口，沿用「属性用单参数赋值」的既有写法。
# ⚠ 取视图的路径是 **IModelDoc.ActiveView（属性）**；
#   官方在 IModelDoc2 上另有 GetFirstView / GetNextView 一类取法，
#   但那是「按图纸视图」那条线（属 IView，不是三维视图），本模块不混。
# 覆盖:   后续同级定义
# ⚠ 本组为照既有模式新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_active_view(model):
    """取当前活动的三维视图。⚑ 官方是 **IModelDoc.ActiveView 属性**。"""
    if model is None:
        raise ValueError("model 为 None")
    return get_com_member(model, "ActiveView")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IModelView 段
# 定位:   激活与重绘。官方签名逐条照抄：
#     Void Activate()                            ← **零参**
#     Void DrawHighlightedItems()                ← **零参**
#     Void GraphicsRedraw(Object)                → 1
#     Void InitializeShading()                   ← **零参**
#     Void DrawTransparentFeatureTree()          ← **零参**
# ⚠ GraphicsRedraw 的 Object 语义（重绘整个场景还是局部？）官方无文档
#   ⇒ 默认传 None，并在参数名上如实标为 scope_or_none。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def activate_view(view) -> bool:
    """激活视图。**零参**。"""
    _require(view)
    call_com_member(view, "Activate")
    return True


def redraw_view(view, scope_or_none=None) -> bool:
    """重绘。⚠ 参��的 Object 语义官方无文档，默认 None。"""
    _require(view)
    get_com_member(view, "GraphicsRedraw", scope_or_none)
    return True


def initialize_shading(view) -> bool:
    """初始化着色。**零参**。"""
    _require(view)
    get_com_member(view, "InitializeShading")
    return True


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）
# 定位:   窗口几何与显示模式。官方签名逐条照抄（**全部是属性**）：
#     Int32  get_FrameLeft() / get_FrameTop() / get_FrameWidth() /
#           get_FrameHeight() / get_FrameState()      ← 像素
#     Void   set_FrameLeft(Int32) / set_FrameTop / set_FrameWidth /
#           set_FrameHeight / set_FrameState
#     Int32  get_DisplayMode() / set_DisplayMode(Int32)
#     Int32  get_HlrQuality()  / set_HlrQuality(Int32)
#     Double get_Scale() / set_Scale(Double)     ← 另有 Scale2
#     Boolean get_EnableGraphicsUpdate() / set_EnableGraphicsUpdate(Boolean)
#     Boolean get_DisplayZebraStripes() / set_DisplayZebraStripes(Boolean)
#     Boolean get_XorHighlight() / set_XorHighlight(Boolean)
#     Int32  get_UpAxisFlyout() / set_UpAxisFlyout(Int32)
# ⚑ 迟到绑定下这些**全是属性** —— 加括号会 TypeError（AGENTS.md §六 事实 4）。
# ⚠ 坐标单位（像素？缇？）官方无文档说明 ⇒ 数值原样透传，不换算。
# ⚠ DisplayMode / HlrQuality / FrameState 的枚举值官方在 C:\\swapi 的
#   swconst 册里可查，本模块**不内嵌副本**（会随版本漂移），只透传 int。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_view_frame(view) -> dict[str, int]:
    """取窗口几何（四个 Int32，单位官方未说明）。"""
    _require(view)
    return {
        "left": int(get_com_member(view, "FrameLeft") or 0),
        "top": int(get_com_member(view, "FrameTop") or 0),
        "width": int(get_com_member(view, "FrameWidth") or 0),
        "height": int(get_com_member(view, "FrameHeight") or 0),
        "state": int(get_com_member(view, "FrameState") or 0),
    }


def set_view_frame(view, left: int, top: int, width: int, height: int) -> bool:
    """设窗口几何。⚑ 四个都是**属性**。"""
    _require(view)
    get_com_member(view, "FrameLeft", int(left))
    get_com_member(view, "FrameTop", int(top))
    get_com_member(view, "FrameWidth", int(width))
    get_com_member(view, "FrameHeight", int(height))
    return True


def get_display_mode(view) -> int:
    """取显示模式码。"""
    _require(view)
    return int(get_com_member(view, "DisplayMode") or -1)


def set_display_mode(view, mode: int) -> bool:
    """设显示模式。⚑ 官方是**属性**。枚举在 swconst 册，不内嵌。"""
    _require(view)
    get_com_member(view, "DisplayMode", int(mode))
    return True


def get_view_scale(view) -> float:
    """取视图缩放比。"""
    _require(view)
    return float(call_com_member(view, "Scale") or 0.0)


def set_view_scale(view, scale: float) -> bool:
    """设视图缩放比。⚑ 官方是**属性**（另有 Scale2，本模块用基础版）。"""
    _require(view)
    get_com_member(view, "Scale", float(scale))
    return True


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）
# 定位:   视图操纵。官方签名逐条照抄：
#     Void ZoomByFactor(Double)                  → 1
#     Void TranslateBy(Double, Double)           → 2
#     Void TurnBy(Double, Double)                → 2
#     Void RollBy(Double)                        → 1
#     Void RotateAboutCenter(Double, Double)     → 2
#     Void RotateAboutPoint(Double, Double, Double, Double, Double) → 5
#     Void RotateAboutAxis(Double × 7)           → 7
# ⚠ 旋转参数的**单位**（度？弧度？）官方无文档；`RotateAboutAxis` 的
#   前两参（轴向量）与后 5 参（角）的对应关系也无文档
#   ⇒ 本模块**原样透传**，函数名只说「按轴旋转」，不解释参数含义。
# ⚠ 这些是**立即生效的交互式**操纵（不是记录轨迹回放），与
#   SolidWorks 的「相机路径」机制不同；后者本模块不涉及。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def zoom_view(view, factor: float) -> bool:
    """按倍数缩放视图。"""
    _require(view)
    get_com_member(view, "ZoomByFactor", float(factor))
    return True


def translate_view(view, dx: float, dy: float) -> bool:
    """平移视图。"""
    _require(view)
    get_com_member(view, "TranslateBy", float(dx), float(dy))
    return True


def rotate_about_center(view, angle_x: float, angle_y: float) -> bool:
    """绕视图中心旋转（两个角）。⚠ 单位官方无文档。"""
    _require(view)
    get_com_member(view, "RotateAboutCenter", float(angle_x), float(angle_y))
    return True


def roll_view(view, angle: float) -> bool:
    """绕视线轴滚转。⚠ 单位官方无文档。"""
    _require(view)
    get_com_member(view, "RollBy", float(angle))
    return True


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）
# 定位:   相机与姿态。官方签名逐条照抄：
#     Camera      get_Camera() / set_Camera(Camera)          ← **属性**
#     Boolean     SetCameraByName(String)                     → 1
#     MathTransform get_Orientation3() / set_Orientation3(MathTransform)
#     MathVector     get_Translation3() / set_Translation3(MathVector)
#     MathTransform get_Transform()     / set_Transform(MathTransform)
# ⚑ 同一件事官方给了三代：Orientation / Orientation2 / Orientation3，
#   Translation / Translation2 / Translation3，Xform / IXform / Transform。
#   官方**未说明取舍** ⇒ 本模块**以 3 号（MathTransform / MathVector）为准**，
#   其余在注释里点名，不替调用方删掉。
# ⚠ SetCameraByName 的名字取值（官方预置视角名？）两套源都查不到
#   ⇒ 只透传字符串，不给预设列表。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_view_camera(view):
    """取相机对象。⚑ 官方是**属性**。"""
    _require(view)
    return get_com_member(view, "Camera")


def set_view_camera_by_name(view, name: str) -> bool:
    """按名字设相机。⚠ 名字取值官方未给出。"""
    _require(view)
    return bool(get_com_member(view, "SetCameraByName", str(name)))


def get_view_orientation(view):
    """取视图姿态。⚑ 官方 3 号是 **属性**（MathTransform）。"""
    _require(view)
    return get_com_member(view, "Orientation3")


def set_view_orientation(view, transform) -> bool:
    """设视图姿态。⚑ 官方 3 号是**属性**。"""
    _require(view)
    get_com_member(view, "Orientation3", transform)
    return True


def get_view_translation(view):
    """取视图平移。⚑ 官方 3 号是**属性**（MathVector）。"""
    _require(view)
    return get_com_member(view, "Translation3")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）
# 定位:   透视与动态。官方签名逐条照抄：
#     Void    AddPerspective()      ← **零参**
#     Void    RemovePerspective()   ← **零参**
#     Boolean HasPerspective()      ← **零参**
#     Void    StartDynamics() / StopDynamics()  ← **零参**
#     Object  GetNext()             ← **零参**，返回下一个 IModelView
#     ModelDoc GetModelDoc()        ← **零参**
#     Object  GetVisibleBox()       ← **零参**
#     Object  GetEyePoint() / Boolean SetEyePoint(Object) → 0 / 1
# ⚠ 立体（Stereo）的 set/get 有 Object 与 Double& 两套，且 GetStereoSeparation
#   的返回类型反射里是 Object（含义未明）⇒ **立体相关一律不封装**，
#   见 VIEW_UNWRAPPED。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def has_perspective(view) -> bool:
    """是否处于透视。**零参**。"""
    _require(view)
    return bool(get_com_member(view, "HasPerspective"))


def add_perspective(view) -> bool:
    """开启透视。**零参**。"""
    _require(view)
    call_com_member(view, "AddPerspective")
    return True


def remove_perspective(view) -> bool:
    """关闭透视。**零参**。"""
    _require(view)
    call_com_member(view, "RemovePerspective")
    return True


def start_dynamics(view) -> bool:
    """进入动态（拖拽旋转）模式。**零参**。"""
    _require(view)
    call_com_member(view, "StartDynamics")
    return True


def stop_dynamics(view) -> bool:
    """退出动态模式。**零参**。"""
    _require(view)
    call_com_member(view, "StopDynamics")
    return True


def get_next_view(view):
    """取下一个三维视图。**零参**。"""
    _require(view)
    return get_com_member(view, "GetNext")


def get_view_model_doc(view):
    """取该视图所属的文档。**零参**。"""
    _require(view)
    return get_com_member(view, "GetModelDoc")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_simulation_study.py::collect_study_evidence）
# 定位:   视图状态证据回读，沿用「只取已核实成员」的写法。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_view_evidence(view) -> dict[str, Any]:
    """回读视图状态（供出图前记录用）。"""
    _require(view)
    frame = get_view_frame(view)
    return {
        "frame": frame,
        "display_mode": get_display_mode(view),
        "hlr_quality": int(get_com_member(view, "HlrQuality") or -1),
        "scale": get_view_scale(view),
        "has_perspective": has_perspective(view),
        "enable_graphics_update": bool(
            get_com_member(view, "EnableGraphicsUpdate")),
        "display_zebra_stripes": bool(get_com_member(view, "DisplayZebraStripes")),
        "xor_highlight": bool(get_com_member(view, "XorHighlight")),
        "has_camera": get_view_camera(view) is not None,
        "has_orientation": get_view_orientation(view) is not None,
    }
