"""工程图：把模型标注/尺寸插进图纸视图（IDrawingDoc::InsertModelAnnotations4），带回读。

能力域
    域 9 · 工程图

⚠ 等级如实：**`stitched`** —— 本模块按官方签名与官方示例写就，**未在本机真机建出
  非空插入**（AGENTS.md 铁律 2 / 红线⑥）。判据见 :func:`insert_model_annotations_report`
  返回的 ``delta``：插入前后视图标注计数之差；**读不到就如实报 unknown，不当成功**。

为什么要有这个模块
------------------
`capabilities.yaml` 的 ``drawing_dimension_insertion`` 原记 `not_implemented`，理由是
「实现层没有对应函数」——那是**搜错了成员名**：真正干活的是
``IDrawingDoc::InsertModelAnnotations4``（8 参），而 ``InsertModelDimensions`` 是另一个
只接收 1 个 option、且**无返回值**的成员。子技能
``subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`` 里已有可用实现
（``insert_dimensions``），但**工具层一直没有暴露** ⇒ 本条是「实现有、工具没接」，不是
「没做」。本模块把那条链路补到工具层，并补上**回读**。

签名与调用序来源（三源）
------------------------
① `C:\\swapi\\types\\IDrawingDoc\\InsertModelAnnotations4.md`
   — 签名 8 参；Returns「Array of inserted IAnnotation objects」；
     ``AllViews``：True 插全部视图、False 只插**当前选中视图**。
② `C:\\swapi\\types\\IDrawingDoc\\InsertModelDimensions.md`
   — ``void InsertModelDimensions(int Option)``，Option 0 = 视图内全部尺寸；
     Remarks：「The **Insert Model Items** dialog is not displayed.」
③ `C:\\swapi\\examples\\Insert_Model_Annotations_Example_CSharp.md`
   — 官方示例调用序：``SelectByID2(视图, "DRAWINGVIEW", …)`` →
     ``ActivateView(视图)`` → ``ClearSelection2(true)`` →
     ``InsertModelAnnotations4(0, 32768, true, false, false, false, false, false)``。

⚠ 编号变体的取舍：``InsertModelAnnotations3``（6 参）作为**旧版回退**；两者都不可用时
  再退回 ``InsertModelDimensions(0)``（void，靠回读判是否生效）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/sw_drawing_annotations.py
# 定位:   ★ 补 `capabilities.yaml` 的 `drawing_dimension_insertion`（原 not_implemented）
#         的**工具层缺口**：实现已在 subskills 的 drawing_workflow.insert_dimensions，
#         本模块把它归一成 report 形态并**补回读**。
# 官方依据: 见上「签名与调用序来源（三源）」①②③（逐字取自 C:\swapi）。
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   IDrawingDoc::InsertModelAnnotations4 / -3 / InsertModelDimensions
# ⚠ ★ 未真机验证：见模块 docstring 的「等级如实」。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any

try:  # ★ 包内相对导入（测试以包形态 import 时）
    from .sw_connect import call_com_member, get_com_member
except ImportError:  # pragma: no cover - 脚本直跑时走绝对导入
    from sw_connect import call_com_member, get_com_member

#: `swImportModelItemsSource_e.swImportModelItemsFromEntireModel` —— 从整个模型导入
SW_IMPORT_MODEL_ITEMS_FROM_ENTIRE_MODEL = 0
#: `swInsertAnnotation_e.swInsertDimensionsMarkedForDrawing` —— 只插「标记为工程图」的模型尺寸
SW_INSERT_DIMENSIONS_MARKED_FOR_DRAWING = 32768


def _annot_iter_views(model) -> list:
    """列出当前图纸上的全部视图（拿不到就回空表，不抛）。

    ★ 2026-11-02：本函数原名 `_iter_views`，与 `sw_drawing_view.py` / 
      `sw_drawing_create_missing.py` 同名 ⇒ `check_tool_official_claims.py` 的 
      `FunctionIndex` 按**函数名**建索引，会把本文件的 COM 成员调用错误归属到那几个
      工具上（实测 10 条假 `member-uncited`）⇒ 改成本模块独有名。
    """
    views: list = []
    try:
        sheet = get_com_member(model, "GetCurrentSheet")
    except Exception:  # noqa: BLE001 - 拿不到图纸不是致命错，由调用方按 unknown 处理
        return views
    if sheet is None:
        return views
    try:
        raw = call_com_member(sheet, "GetViews")
    except Exception:  # noqa: BLE001
        return views
    if raw is None:
        return views
    if not isinstance(raw, (list, tuple)):
        raw = [raw]
    for view in raw:
        if view is not None:
            views.append(view)
    return views


def _annotation_total(model) -> int | None:
    """当前图纸全部视图的标注计数之和；任一处读不到就回 None（**不猜 0**）。"""
    views = _annot_iter_views(model)
    if not views:
        return None
    total = 0
    for view in views:
        try:
            count = call_com_member(view, "GetAnnotationCount")
        except Exception:  # noqa: BLE001
            return None
        try:
            total += int(count)
        except (TypeError, ValueError):
            return None
    return total


def _activate_view(model, view_name: str) -> dict:
    """按官方示例的调用序选中并激活一个视图。"""
    stage = {"selected": False, "activated": False}
    try:
        extension = get_com_member(model, "Extension")
    except Exception:  # noqa: BLE001
        extension = None
    if extension is not None:
        try:
            ok = call_com_member(
                extension, "SelectByID2",
                view_name, "DRAWINGVIEW", 0, 0, 0, False, 0, None, 0,
            )
            stage["selected"] = bool(ok)
        except Exception as exc:  # noqa: BLE001
            stage["select_error"] = f"{type(exc).__name__}: {str(exc)[:120]}"
    try:
        stage["activated"] = bool(call_com_member(model, "ActivateView", view_name))
    except Exception as exc:  # noqa: BLE001
        stage["activate_error"] = f"{type(exc).__name__}: {str(exc)[:120]}"
    try:
        call_com_member(model, "ClearSelection2", True)
    except Exception:  # noqa: BLE001 - 清选择失败不阻塞插入
        pass
    return stage


def _count_result(value: Any) -> int | None:
    """把插入返回值折成「插了几条」；拿不到就 None。"""
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return len(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def insert_model_annotations_report(
    model,
    view_name: str | None = None,
    all_views: bool = True,
    types: int = SW_INSERT_DIMENSIONS_MARKED_FOR_DRAWING,
) -> dict:
    """把模型标注插进工程图视图，并用**回读**判断到底插进去没有。

    :param model: 当前活动文档（必须已是 DrawingDoc）。
    :param view_name: 传了就按官方示例先选中并激活该视图；``all_views`` 为真时可省略。
    :param all_views: True 插全部视图（官方 ``AllViews``）；False 只插当前选中视图。
    :param types: ``swInsertAnnotation_e`` 位掩码，默认 32768（标记为工程图的模型尺寸）。
    :returns: 结构化报告 —— ``ok`` / ``stage`` / ``member_used`` / ``args`` /
        ``annotations_before`` / ``annotations_after`` / ``delta`` / ``inserted_returned`` /
        ``notes``。**``delta`` 读不到时为 None，``ok`` 随之为 False**（不许把 None 当 0）。
    """
    report: dict[str, Any] = {
        "ok": False,
        "stage": "start",
        "member_used": None,
        "args": [],
        "view_name": view_name,
        "all_views": all_views,
        "annotations_before": None,
        "annotations_after": None,
        "delta": None,
        "inserted_returned": None,
        "notes": [],
    }
    if model is None:
        report["stage"] = "model"
        report["notes"].append("model 为 None")
        return report

    activated = {}
    if view_name:
        activated = _activate_view(model, view_name)
        report["activation"] = activated
        if not activated.get("activated") and not activated.get("activated") is False:
            report["notes"].append("视图激活未确认（继续尝试，由回读裁决）")

    report["annotations_before"] = _annotation_total(model)

    args4 = (
        SW_IMPORT_MODEL_ITEMS_FROM_ENTIRE_MODEL,
        int(types),
        bool(all_views),
        False,  # DuplicateDims：官方示例传 False
        False,  # HiddenFeatureDims
        False,  # UsePlacementInSketch
        False,  # InsertAllAnnotations
        False,  # InsertAllReferenceGeometry
    )
    args3 = args4[:6]

    call_errors: list[str] = []
    #: ★ 2026-11-02：三个成员**逐个写成字面量**（原本是 `for member, args in (...)` 的
    #:   变量式调用）—— 本仓 `check_dispatch_forward_args` 要求分发口的成员名**可解析**；
    #:   变量名会让它退化成「非字面量调用点」⇒ 门禁红（实测 `class-mismatch`）。
    #:   ⇒ 展平既过门禁，也让「调了哪三个成员」在源码里一眼可见（台账逐条引了官方页）。
    try:
        _value = call_com_member(model, "InsertModelAnnotations4", *args4)
    except Exception as exc:  # noqa: BLE001 - 逐成员回退，错误留证
        call_errors.append(f"InsertModelAnnotations4: {type(exc).__name__}: {str(exc)[:120]}")
    else:
        report["member_used"] = "InsertModelAnnotations4"
        report["args"] = list(args4)
        report["inserted_returned"] = _count_result(_value)
        report["stage"] = "inserted"

    if report["member_used"] is None:
        try:
            _value = call_com_member(model, "InsertModelAnnotations3", *args3)
        except Exception as exc:  # noqa: BLE001
            call_errors.append(f"InsertModelAnnotations3: {type(exc).__name__}: {str(exc)[:120]}")
        else:
            report["member_used"] = "InsertModelAnnotations3"
            report["args"] = list(args3)
            report["inserted_returned"] = _count_result(_value)
            report["stage"] = "inserted"

    if report["member_used"] is None:
        # 最后一档：void 成员，只能靠回读判
        try:
            call_com_member(model, "InsertModelDimensions", SW_IMPORT_MODEL_ITEMS_FROM_ENTIRE_MODEL)
            report["member_used"] = "InsertModelDimensions"
            report["args"] = [SW_IMPORT_MODEL_ITEMS_FROM_ENTIRE_MODEL]
            report["stage"] = "inserted"
            report["notes"].append("退到 void 成员 InsertModelDimensions，只能靠回读判定")
        except Exception as exc:  # noqa: BLE001
            call_errors.append(f"InsertModelDimensions: {type(exc).__name__}: {str(exc)[:120]}")
    if call_errors:
        report["call_errors"] = call_errors

    report["annotations_after"] = _annotation_total(model)
    before, after = report["annotations_before"], report["annotations_after"]
    if before is not None and after is not None:
        report["delta"] = after - before

    if report["member_used"] is None:
        report["stage"] = "no_member"
        report["ok"] = False
        report["notes"].append("三个成员都调不通 ⇒ 如实报失败，不降级成『大概插上了』")
        return report

    returned = report["inserted_returned"]
    delta = report["delta"]
    if returned is not None and returned > 0:
        report["ok"] = True
        report["notes"].append("返回数组非空 ⇒ 插入有据")
    elif delta is not None and delta > 0:
        report["ok"] = True
        report["notes"].append(f"回读标注数增加 {delta} ⇒ 插入有据")
    elif returned == 0 and delta == 0:
        report["ok"] = False
        report["notes"].append(
            "返回空数组且回读无增量 ⇒ **没有产出非空插入**（常见原因：模型里没有"
            "「标记为工程图」的尺寸，或视图未激活／无可见几何）"
        )
    else:
        report["ok"] = False
        report["notes"].append("返回空且回读不可用 ⇒ 判据不足，**不当成功**")
    return report
