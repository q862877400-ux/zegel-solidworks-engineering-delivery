"""★ 工程图「已有实现」的对外包装：收**毫米**、只在边界换算，并把**前置回读**带回来。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 的边界换算层）。规格 `specs/202-user-coverage-gaps` 的 **R1**。
# 文件:   scripts/sw_drawing_expose.py
# 定位:   ★★ **为什么要有这一层**（三件事，缺一层都不成）：
#   ① ★ **不重写实现**：真正的实现早已在 `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`，
#      经 `scripts/sw_drawing.py`（`spec_from_file_location` 按路径加载 + `globals()` 再导出）可达。
#      ★ 依据：`specs/202-user-coverage-gaps/recon/drawing-existing-coverage.md` ——
#      **工程图 13 项里本仓已实现 8 项、却只挂出了 4 项**（且全靠同一个 `solidworks_drawing` 工具）。
#      ⇒ ★ 本层只做**转接**，★ 一行实现逻辑都不重写（"缝合优先不发明"）。
#   ② ★ **单位边界**（规则 2）：既有实现的 `x`/`y` 是**米**，而对外一律收**毫米**
#      ⇒ ★ **换算只在本文件发生一次**（`_mm()`），★ 上层与实现层都不做第二遍。
#   ③ ★ **前置必须回读**：`add_section_view` 的官方 Remarks 逐字要求"**先选剖面线**"
#      ⇒ ★ 本层先回读**选区计数**再调用，并在返回值里如实给出 `preconditions_held`
#      （★ 依据：事实 496 —— 一个前置失败会**拖垮整批**，所以前置必须与能力分开记）。
#   官方依据（★ 逐页读过；契约抄本见 `recon/api/`）:
#     · `IDrawingDoc.CreateDrawViewFromModelView3`（投影视图）· `IDrawingDoc.CreateSectionViewAt5`（剖面）
#     · `IDrawingDoc.CreateDetailViewAt4`（局部，**12 参**）· `IDrawingDoc.SetupSheet6`（图纸格式）
#     · `IModelDoc2.InsertNote`（注释）· `IView.InsertHoleTable3` / `ISheet.InsertRevisionTable2`（表）
#     · `IDrawingDoc.InsertCenterMark3` / `IView.AutoInsertCenterMarks2`（中心符号线）
#   许可:   本仓库 MIT。★ 无第三方代码引入（实现来自本仓 subskill）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
for _p in (str(_REPO), str(_REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C                                    # noqa: E402
from scripts import sw_drawing as D                                    # noqa: E402


def _mm(value) -> float:
    """★ 毫米 → 米（**整个仓库里这一处**负责工程图坐标的换算）。"""
    return float(value) / 1000.0


def _selection_count(model) -> int:
    """★ 回读当前选区计数（★ 判"前置成不成立"要用它；事实 32/496）。"""
    try:
        return int(C.get_com_member(C.get_com_member(model, "SelectionManager"),
                                    "GetSelectedObjectCount2", -1) or 0)
    except Exception:                                                   # noqa: BLE001
        return 0


def _result(op: str, payload: dict, verified_by: str, *, pre_ok=None) -> dict:
    """★ 统一的返回形状（★ 判据要**可回读**，且**前置与能力分开记**）。"""
    out = {"ok": bool(payload.get("ok", payload.get("view") is not None)) if isinstance(payload, dict)
          else payload is not None,
          "op": op, "verified_by": verified_by, "raw": payload}
    if pre_ok is not None:
        out["preconditions_held"] = bool(pre_ok)
        out["ok"] = bool(out["ok"] and pre_ok)
    return out


def create_projected_view(drawing_model, part_path: str, *, projection: str = "first_angle") -> dict:
    """★ 投影视图（`CreateDrawViewFromModelView3`，含第一角/第三角投影布局）。

    ★ 前置：`part_path` 必须是**已存盘的模型完整路径且含 `.sldprt`/`.sldasm`**（官方 Remarks 逐字）。
    ★★ 视图名由底层**自己解析本地化名**（`_create_model_view`，事实 494）—— 调用方**不必**知道中文界面叫什么。
    """
    res = D.create_standard_views_with_projection(drawing_model, part_path, projection=projection)
    return _result("create_projected_view", res if isinstance(res, dict) else {"value": res},
                   "视图数增量 + 返回非 None（★ 底层为 CreateDrawViewFromModelView3）",
                   pre_ok=bool(part_path and str(part_path).lower().endswith((".sldprt", ".sldasm"))))


def create_section_view(drawing_model, *, x_mm: float, y_mm: float) -> dict:
    """★ 剖面视图（`CreateSectionViewAt5`）—— ★ **调用前必须先选好剖面线**（官方 Remarks 逐字）。

    ★ 本函数**不代选**：先回读选区计数并在返回值里给出 `preconditions_held`。
    """
    pre = _selection_count(drawing_model)
    res = D.add_section_view(drawing_model, _mm(x_mm), _mm(y_mm))
    return _result("create_section_view", {"ok": res is not None, "view": res},
                   "视图数增量（★ 前置成立才算）", pre_ok=pre > 0)


def create_detail_view(drawing_model, *, x_mm: float, y_mm: float, scale: float = 2.0,
                       style: int = 0, label: str = "", show_type: int = 0,
                       full_outline: bool = False, jagged_outline: bool = False,
                       no_outline: bool = False, shape_intensity: int = 0) -> dict:
    """★ 局部视图（`CreateDetailViewAt4`，12 参）—— ★ 前置是"图上有局部圆（草图圆）"。

    ★ `scale` 是比例分子（分母固定 1.0）⇒ `scale=2` 表示 **2:1**。
    """
    res = D.add_detail_view(drawing_model, _mm(x_mm), _mm(y_mm), scale, style=style, label=label,
                            show_type=show_type, full_outline=full_outline,
                            jagged_outline=jagged_outline, no_outline=no_outline,
                            shape_intensity=shape_intensity)
    return _result("create_detail_view", {"ok": res is not None, "view": res},
                   "视图数增量 + 返回非 None")


def set_sheet_format(drawing_model, format_path: str) -> dict:
    """★ 图纸格式/模板（`SetupSheet6`）—— 换图纸格式。

    ★ 官方 Remarks 逐字：调完要 `ForceRebuild3` 才刷新第一角/第三角投影；★ 底层已处理。
    """
    res = D.set_sheet_format(drawing_model, format_path)
    return _result("set_sheet_format", {"ok": res is not None, "value": res},
                   "返回非 None + 图纸信息回读变化")


def add_drawing_note(drawing_model, *, x_mm: float, y_mm: float, text: str) -> dict:
    """★ 注释/文字（`InsertNote`）—— ★ 引线附着点来自**调用前**的选择（官方 Remarks 逐字）。"""
    res = D.add_note(drawing_model, _mm(x_mm), _mm(y_mm), text)
    return _result("add_note", {"ok": res is not None, "note": res}, "注解计数增量")


def create_hole_table(drawing_model, *, x_mm: float, y_mm: float, table_type: int,
                      row: int = 0, column: int = 0, template: str = "",
                      use_anchor_point: bool = False) -> dict:
    """★ 孔表（`InsertHoleTable3` / 通用表注解）。

    ⚠ **`table_type` 的取值表官方两源都查不到**（★ 铁律 5）⇒ ★ 本函数**原样透传**、
    ★ **不写死**、也**不猜**；选值由调用方按官方枚举给。
    """
    res = D.insert_table_annotation(drawing_model, _mm(x_mm), _mm(y_mm), int(table_type),
                                    row, column, template=template,
                                    use_anchor_point=use_anchor_point)
    return _result("create_hole_table", {"ok": res is not None, "table": res}, "表注解计数增量")


def create_revision_table(drawing_model, *, x_mm: float, y_mm: float, table_type: int,
                          row: int = 0, column: int = 0, template: str = "",
                          use_anchor_point: bool = False) -> dict:
    """★ 修订表（`InsertRevisionTable2`）。

    ★ 官方 Returns 逐字：**已有修订表时回 `null`** ⇒ ★ 第二次调用"回 null"是**契约**、不是失败
    （★ 本函数把它报成 `ok=False` 但**不判为出错**，由调用方按契约解释）。
    ⚠ `table_type` 同孔表：取值表查不到 ⇒ **原样透传**。
    """
    res = D.insert_table_annotation(drawing_model, _mm(x_mm), _mm(y_mm), int(table_type),
                                    row, column, template=template,
                                    use_anchor_point=use_anchor_point)
    return _result("create_revision_table", {"ok": res is not None, "table": res},
                   "返回非 None + ISheet.RevisionTable 回读")


def insert_center_marks(drawing_model, requirements) -> dict:
    """★ 中心符号线（`AutoInsertCenterMarks2`，批量按视图插）。

    ⚠ **真机阴性（已知）**：`InsertCenterMark3` 两格都不成、其中一格**前置是成立的**
    ⇒ ★ 本函数走的是**批量**那条路（`AutoInsertCenterMarks2`），★ **尚未单独真机验证** ⇒ 如实标注。
    """
    res = D.auto_insert_center_marks(drawing_model, requirements)
    return _result("insert_center_marks", res if isinstance(res, dict) else {"value": res},
                   "★ 待真机验证（`GetCenterMarkCount2` 增量）—— ⚠ 单点 `InsertCenterMark3` 已实测为阴性")


__all__ = [
    "create_projected_view", "create_section_view", "create_detail_view", "set_sheet_format",
    "add_drawing_note", "create_hole_table", "create_revision_table", "insert_center_marks",
]
