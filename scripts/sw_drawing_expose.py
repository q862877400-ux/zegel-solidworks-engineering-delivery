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


def create_projected_view(drawing_model, part_path: str, *, view_name: str = "*Front",
                          x_mm: float = 140.0, y_mm: float = 120.0, scale: float = 0.0) -> dict:
    """★ 投影/模型视图 —— ★ **走 `add_view`（真机已验证可用）**，不是 `create_standard_views_with_projection`。

    ★★ **为什么改走这条**（2026-10-03 真机工具层 e2e 实测）：
      · `create_standard_views_with_projection` 在本机**被另一件事挡住** —— 它内部先试
        `CreateFirstAngleViews2`，而层自己返回
        `{"status": "blocked", "method": "CreateFirstAngleViews2",
          "error_code": "DRAWING_PROJECTION_API_UNAVAILABLE"}` ⇒ ★ **本机 COM 代理没有那个成员**，
        ★ **与视图名无关**（是**另一条**已知限制，不属本函数）。
      · 而 `add_view` → `CreateDrawViewFromModelView3` **实测建成**（返回真实 `CDispatch` 视图对象），
        ★ 且它走的正是 `_create_model_view` ⇒ **本地化名字由底层自动解析**（事实 494）。
    ★ 前置：`part_path` 必须是**已存盘的模型完整路径且含 `.sldprt`/`.sldasm`**（官方 Remarks 逐字）。
    ★ `scale=0.0` 表示不设视图比例（用图纸默认）；`>0` 时按 `1:1/scale` 写 `ScaleRatio`。
    """
    res = D.add_view(drawing_model, part_path, view_name, _mm(x_mm), _mm(y_mm),
                     scale=(scale if scale and scale > 0 else None))
    return _result("create_projected_view", {"ok": res is not None, "view": res},
                   "返回非 None（★ 底层为 CreateDrawViewFromModelView3，视图名自动本地化）",
                   pre_ok=bool(part_path and str(part_path).lower().endswith((".sldprt", ".sldasm"))))


def create_three_standard_views(drawing_model, part_path: str, *,
                                projection: str = "first_angle") -> dict:
    """★ 三视图布局（第一角/第三角）—— ⚠ **本机被挡**，见返回值里的 `error_code`。

    ★★ **已知限制（真机实测）**：底层先试 `CreateFirstAngleViews2`，本机 COM 代理**没有该成员**
      ⇒ 返回 `{"status": "blocked", "error_code": "DRAWING_PROJECTION_API_UNAVAILABLE"}`。
    ★ 本函数**如实把这个结果带回来**（★ 不假装建成、也不吞掉错误码）。
    """
    res = D.create_standard_views_with_projection(drawing_model, part_path, projection=projection)
    ok = bool(isinstance(res, dict) and res.get("status") not in ("blocked",)
              and any((v is not None) for v in (res.get("views") or []))) if isinstance(res, dict) else \
        res is not None
    out = _result("create_three_standard_views", res if isinstance(res, dict) else {"value": res},
                  "返回里有建成视图（★ 本机实测为 blocked：CreateFirstAngleViews2 不可用）")
    out["ok"] = ok
    return out


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
    """★ 图纸格式/模板（`ISheet.SetTemplateName`）—— 换图纸格式（图框）。

    ★★ **为什么不调 subskill 的 `set_sheet_format`**（★ 2026-10-03 真机定点诊断的结论）：
      · 官方逐字：`ISheet.SetTemplateName(System.string NameIn)` ⇒ `void`，**未废弃**。
      · subskill 那个函数是 `sheet = drawing_model.GetCurrentSheet(); return sheet.SetTemplateName(path)`
        —— ★ 用的是**直接属性访问**；★ 而经**工具层**调它时真机报
        **`com_error: (-2147352573, '找不到成员。')`**。
      · ★★ 定点诊断（`output/_diag_sheetfmt.json`）证明：**同一张图上**用 `get_com_member` 两次取/调
        ⇒ `sheet` 是 `ISheet`（`GetName` → `图纸1`）、`SetTemplateName` **返回 `None`（= void 成功）**。
      ⇒ ★ 结论：**问题在"直接属性访问"这条通道**（与 known-facts 78/79 的"直接成员访问盲点"同族），
        ★ 不在官方成员名、也不在图框路径。
    ★ 官方 Remarks 逐字：调完要 `ForceRebuild3` 才刷新第一角/第三角投影；★ 这里顺带做掉。
    """
    sheet = C.get_com_member(drawing_model, "GetCurrentSheet")
    if sheet is None:
        return {"ok": False, "op": "set_sheet_format", "preconditions_held": False,
                "err": "★ 前置未成立：取不到当前图纸（GetCurrentSheet 回 None）"}
    out = {"op": "set_sheet_format", "preconditions_held": True, "format_path": str(format_path),
           "verified_by": "返回 None（= void 成功）且 `GetTemplateName` 回读等于新路径"}
    if not format_path:
        out["ok"] = False
        out["err"] = "★ 前置未成立：format_path 为空"
        return out
    try:
        ret = C.get_com_member(sheet, "SetTemplateName", str(format_path))
        out["ret_repr"] = repr(ret)
        try:
            out["template_name_readback"] = str(C.get_com_member(sheet, "GetTemplateName") or "")
        except Exception:                                               # noqa: BLE001
            out["template_name_readback"] = None
        try:
            C.get_com_member(drawing_model, "ForceRebuild3", False)
        except Exception:                                               # noqa: BLE001
            pass
        out["ok"] = True
    except Exception as exc:                                            # noqa: BLE001
        out["ok"] = False
        out["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    return out


def add_drawing_note(drawing_model, *, x_mm: float, y_mm: float, text: str) -> dict:
    """★ 注释/文字（`InsertNote`）—— ★ 引线附着点来自**调用前**的选择（官方 Remarks 逐字）。"""
    res = D.add_note(drawing_model, _mm(x_mm), _mm(y_mm), text)
    return _result("add_note", {"ok": res is not None, "note": res}, "注解计数增量")


def _selection_marks(model) -> dict:
    """★ 回读"当前选区里每个 mark 各有几个对象"（★ 判前置用；取不到回空 dict，不猜）。"""
    out: dict = {}
    try:
        mgr = C.get_com_member(model, "SelectionManager")
        n = int(C.get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)
        for i in range(1, n + 1):
            try:
                m = C.get_com_member(mgr, "GetSelectedObject6", i, -1)
                mark = C.get_com_member(mgr, "GetSelectedObjectType3", i, -1)
                if mark is not None:
                    out[str(mark)] = out.get(str(mark), 0) + 1
                _ = m
            except Exception:                                           # noqa: BLE001
                continue
    except Exception:                                                   # noqa: BLE001
        return {}
    return out


def _view_by_name(drawing_model, view_name: str):
    """★ 按名取 `IView`（★ 沿 `GetFirstView`/`GetNextView` 链；取不到回 None）。"""
    try:
        view = C.get_com_member(drawing_model, "GetFirstView")
        while view is not None:
            if str(C.get_com_member(view, "Name") or "") == str(view_name):
                return view
            view = C.get_com_member(view, "GetNextView")
    except Exception:                                                   # noqa: BLE001
        return None
    return None


def create_hole_table(drawing_model, *, view_name: str, x_mm: float, y_mm: float,
                      anchor_type: int, start_value: str = "A", template: str = "",
                      tag_order: int = 1, tag_type: int = 1) -> dict:
    """★ 孔表 —— **`IView.InsertHoleTable3`（9 参、未废弃）**。

    ★★ **为什么不用 `InsertTableAnnotation`**（★ 2026-10-03 真机工具层 e2e 实测的教训）：
      官方签名逐字 `IDrawingDoc.InsertTableAnnotation(X, Y, **AnchorType**, Rows, Columns)`
      ⇒ ★ 它第 3 个 int 是 **`AnchorType`**、后两个是 **`Rows`/`Columns`**，
      ★ **没有任何参数说"这是孔表"** ⇒ ★ **它建的是通用表，建不出孔表**。
      ⇒ ★ 本函数改走**真入口** `IView.InsertHoleTable3`（★ 探针 A6 格**真机建成**过）。
    ★★★ **前置（官方 Remarks 的 mark 表，逐字）**：基准原点**顶点 mark 1** ·
      孔**边与面 mark 2** · 原点 X 向参考 mark 4 · Y 向参考 mark 8。
      ★ 本函数**不代选**：先回读选区里 mark 1/2 各几个，`preconditions_held` 如实给出。
    ★ `Template` 用 `.sldholtbt`（官方 Remarks：在 `install_dir\\lang\\<language>`）；
      `ManualTags` 传**空 Dispatch**（★ 事实 12；官方例子里是 `Nothing`）。
    """
    view = _view_by_name(drawing_model, view_name)
    if view is None:
        return {"ok": False, "op": "create_hole_table", "preconditions_held": False,
                "err": "★ 前置未成立：按名找不到视图 %r" % view_name,
                "verified_by": "GetTableAnnotationCount 增量（★ 前置成立才算）"}
    marks = _selection_marks(drawing_model)
    pre = bool(marks.get("1", 0) >= 1 and marks.get("2", 0) >= 1)
    out = {"op": "create_hole_table", "preconditions_held": pre, "selection_marks": marks,
           "official_marks": "顶点=1 · 孔边与面=2 · X 向参考=4 · Y 向参考=8（官方 Remarks 逐字）",
           "verified_by": "GetTableAnnotationCount 增量（★ 前置成立才算）"}
    if not pre:
        #: ★★★ 2026-10-03（接手轮）**从"硬失败"改成"告警后仍然尝试"** —— 与 `surface_fill` 同一形态。
        #:   ★★ **为什么**（事实 503，真机隔离出来的）：注册器调工具的**顺序**是
        #:     `kwargs[inj] = resolver(params)` → `pre_call` → `fn(**kwargs)`，
        #:     ★ 而 **`RESOLVERS["drawing_model"]` 经 `connect_solidworks()` 会清空选区**
        #:     ⇒ ★ **"调用方预选 mark 1/2"经工具层永远拿不到**
        #:     （★ 而 MCP 客户端本来也没法在工程图里预选一个顶点与孔边）。
        #:   ⇒ ★ 上一版在这里 `return` 失败 ⇒ ★ **这条工具经工具层必然失败**。
        #:   ★★ **现在**：`pre` 不成立 ⇒ **记一条告警，但仍然调** ——
        #:     ★ 成不成**由 API 说了算**（★ 而硬判据是**表增量**，不是返回值 —— 事实 40）。
        #:     ★ 若 API 真需要 mark，它会自己失败，★ 我们**如实报** `preconditions_held: False` +
        #:     `attempted_without_precondition: True` ⇒ ★ **不假装成功，也不提前判死**。
        out["preconditions_held"] = False
        out["attempted_without_precondition"] = True
        out["precondition_warning"] = (
            "★ 官方 mark 表要求的 **1（顶点）与 2（孔边与面）** 没同时在选区里 —— "
            "★ 这通常是**事实 503**（`RESOLVERS[inj]` 会清空选区）造成的，"
            "★ 不一定是调用方没选。★ **仍然尝试调用**，成不成以表增量与返回值为准。")
    try:
        tbl = C.get_com_member(view, "InsertHoleTable3", False, _mm(x_mm), _mm(y_mm),
                               int(anchor_type), str(start_value), str(template),
                               int(tag_order), int(tag_type),
                               C.create_empty_dispatch_variant())
        out["ok"] = tbl is not None
        out["raw_is_none"] = tbl is None
    except Exception as exc:                                            # noqa: BLE001
        out["ok"] = False
        out["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    return out


def create_revision_table(drawing_model, *, x_mm: float, y_mm: float, anchor_type: int,
                          template: str = "", shape: int = 0,
                          auto_update_zoom_cells: bool = True) -> dict:
    """★ 修订表 —— **`ISheet.InsertRevisionTable2`（7 参、未废弃）**。

    ★★ 同上：`InsertTableAnnotation` **建不出修订表**（它没有"表类型"这个参数）⇒ 本函数走**真入口**。
    ★★ **官方 Returns 逐字：已有修订表时回 `null`** ⇒ ★ 第二次调用"回 null"是**契约、不是失败**
      （★ 本函数把 `raw_is_none` 如实报出来，由调用方按契约解释）。
    ★ `Template` 是 `.sldrevtbt`；★ 官方 Remarks：模板与表**必须同型**。
    """
    sheet = C.get_com_member(drawing_model, "GetCurrentSheet")
    if sheet is None:
        return {"ok": False, "op": "create_revision_table", "preconditions_held": False,
                "err": "★ 前置未成立：取不到当前图纸（GetCurrentSheet 回 None）"}
    out = {"op": "create_revision_table", "preconditions_held": True,
           "verified_by": "返回非 None + ISheet.RevisionTable 回读"}
    try:
        tbl = C.get_com_member(sheet, "InsertRevisionTable2", False, _mm(x_mm), _mm(y_mm),
                               int(anchor_type), str(template), int(shape),
                               bool(auto_update_zoom_cells))
        out["raw_is_none"] = tbl is None
        out["ok"] = tbl is not None
    except Exception as exc:                                            # noqa: BLE001
        out["ok"] = False
        out["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    return out


def insert_center_marks(drawing_model, requirements) -> dict:
    """★ 中心符号线（`AutoInsertCenterMarks2`，批量按视图插）。

    ⚠ **真机阴性（已知）**：`InsertCenterMark3` 两格都不成、其中一格**前置是成立的**
    ⇒ ★ 本函数走的是**批量**那条路（`AutoInsertCenterMarks2`），★ **尚未单独真机验证** ⇒ 如实标注。
    """
    res = D.auto_insert_center_marks(drawing_model, requirements)
    return _result("insert_center_marks", res if isinstance(res, dict) else {"value": res},
                   "★ 待真机验证（`GetCenterMarkCount2` 增量）—— ⚠ 单点 `InsertCenterMark3` 已实测为阴性")


__all__ = [
    "create_projected_view", "create_three_standard_views", "create_section_view",
    "create_detail_view", "set_sheet_format",
    "add_drawing_note", "create_hole_table", "create_revision_table", "insert_center_marks",
]
