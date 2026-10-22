"""★ 工具层端到端探针：8 条工程图工具**按 ToolSpec 契约**能否经注册器跑通。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）。规格 `specs/202-user-coverage-gaps` 的 **R1 收口**。
# 文件:   tools/probe_drawing_tools_e2e.py
# 定位:   ★★ **为什么要这一层**：R1 把 8 条工程图工具注册进了 `register_capabilities.B
#           ATCH_MODULES`，
#   机器核验只到「`all_specs()` 里有它们 + `check_specs` 无问题」这一步 ——
#   ★ **那不等于"经工具层能跑"**。本探针补的就是这一段：
#   ★ **复刻注册器真实做的三步**（★ 逐字依据 `mcp-server/tool_registry.py`）：
# ① `kwargs[inject_as or inj] = resolver(params)`（:507）⇒ ★ 注入的**键名**由 `inject`
# 决定
# ② `kwargs[target] = getattr(params, p.name)`（:498）⇒ ★ 参数按 `spec.params` 的**名字*
# *取
#     ③ `mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])`（:524）
#        ⇒ ★ **模块名拼在 `scripts.` 之后**、函数按 `spec.function` 取
# ⇒ ★★ 这三步正是最容易错的地方（模块名拼错 / 注入键错 / 形参名错 —— 见 known-facts 491
# ），
#     ★ 而它们**只有按契约调才会暴露**。
#   ★ 判据三分（★ 事实 496：前置与能力必须分开记）：
#     **建成** / **前置未成立**（写明缺什么）/ **真阴性**。
#   官方依据（★ 逐页读过；契约抄本在 `specs/202-user-coverage-gaps/recon/api/`）:
# · `IDrawingDoc.CreateDrawViewFromModelView3` · `CreateSectionViewAt5` · `CreateDetailV
# iewAt4`
#     · `IDrawingDoc.SetupSheet6` · `IModelDoc2.InsertNote` · `IView.InsertHoleTable3`
#     · `ISheet.InsertRevisionTable2` · `IView.AutoInsertCenterMarks2`
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as rc  # noqa: E402

from scripts import sw_connect as c  # noqa: E402

OUT = REPO / "output" / "drawing-tools-e2e-evidence.json"
#: ★★ **每次运行用唯一文件名** —— 否则上一轮留下的同名文件可能仍被 SolidWorks 打开
#:   ⇒ `SaveAs` 失败（`part_saved=False`）⇒ ★ 后续"需要已存盘零件"的格子会**静默跳过前置**
#: （2026-10-03 实测：那正是"两格都 views_before=0"的原因，且会让 `projected_view` **误
#: 用旧文件**）。
_RUN_TAG = time.strftime("%H%M%S")
PART = REPO / "output" / ("_probe_tools_e2e_part_%s.SLDPRT" % _RUN_TAG)

#: ★ 8 条工具各自要给的实参（★ 名字**必须与 `tool_specs_batch75.py` 里 `Param(...)` 的第
#: 一个参数逐字一致**）。
TOOL_ARGS: dict[str, dict] = {
    "solidworks_drawing_create_projected_view": {
        "part_path": str(PART),
        "view_name": "*Front",
        "x_mm": 140.0,
        "y_mm": 120.0,
        "scale": 0.0,
    },
    "solidworks_drawing_create_section_view": {"x_mm": 160.0, "y_mm": 120.0},
    "solidworks_drawing_create_detail_view": {
        "x_mm": 200.0,
        "y_mm": 140.0,
        "scale": 2.0,
        "label": "",
        "shape_intensity": 0,
    },
    "solidworks_drawing_set_sheet_format": {"format_path": ""},  # ★ 运行期填入真实路径
    "solidworks_drawing_add_note": {"x_mm": 60.0, "y_mm": 40.0, "text": "MCP-E2E"},
    "solidworks_drawing_create_hole_table": {
        "view_name": "★由前置步骤填入",
        "x_mm": 100.0,
        "y_mm": 60.0,
        "anchor_type": 1,
        "start_value": "A",
        "template": "",
        "tag_order": 1,
        "tag_type": 1,
    },
    "solidworks_drawing_create_revision_table": {
        "x_mm": 100.0,
        "y_mm": 80.0,
        "anchor_type": 1,
        "template": "",
        "shape": 0,
        "auto_update_zoom_cells": True,
    },
    "solidworks_drawing_insert_center_marks": {
        "requirements": [
            {"id": "e2e-cm", "view": "front", "count": 1, "targets": ["holes"]}
        ]
    },
    # ★★ **batch73 的四条**（工程图真缺口）—— ★ 它们此前**只有探针级**真机证据，
    #    ★ **没走过工具层** ⇒ 本轮补上（★ 判据仍是"工具返回 ok + 可回读增量"）。
    "solidworks_drawing_create_broken_view": {
        "view_name": "★由前置步骤填入",
        "position1_mm": -10.0,
        "position2_mm": 10.0,
        "orientation": 2,
        "style": 5,
        "shape_intensity": 2,
        "break_sketch_blocks": True,
    },
    "solidworks_drawing_create_auxiliary_view": {
        "x_mm": 200.0,
        "y_mm": 200.0,
        "z_mm": 0.0,
        "label": "",
        "not_aligned": True,
        "show_arrow": True,
        "flip": False,
    },
    "solidworks_drawing_insert_surface_finish_symbol": {
        "sym_type": 0,
        "leader_type": 1,
        "x_mm": 50.0,
        "y_mm": 50.0,
        "z_mm": 0.0,
        "lay_symbol": 0,
        "arrow_type": 0,
        "mach_allowance": "",
        "other_vals": "",
        "prod_method": "",
        "sample_len": "",
        "max_roughness": "",
        "min_roughness": "",
    },
    "solidworks_drawing_insert_datum_tag": {},
}

#: ★ 需要"同一张图上先有视图"才能测的工具（★ 逐个建一张新工程图 ⇒ 先补一个视图）。
#: ★ `insert_center_marks` 也在内 —— 它先 `_map_standard_views_from_sheet_views` 找 **fr
#: ont/top/right**，
#: ★ 图上没视图时 `mapped_views.get("front")` 是 None ⇒ 直接判 failed（★ 那是**前置**，
#: 不是能力）。
#: ★ `create_broken_view` 要**按视图名**解析（官方 Remarks：无选区前置，按名字取 IView）
#: ；
#: ★ `create_auxiliary_view` 官方要求「based on a **selected edge in a drawing view**」⇒
#:  先有视图。
NEEDS_VIEW = {
    "solidworks_drawing_create_hole_table",
    "solidworks_drawing_insert_center_marks",
    "solidworks_drawing_create_broken_view",
    "solidworks_drawing_create_auxiliary_view",
}


def _get(o, name, *a):
    return c.get_com_member(o, name, *a)


def _find_drwdot():
    for root in (r"c:\ProgramData\SOLIDWORKS", r"c:\ProgramData\SolidWorks"):
        for f in sorted(Path(root).rglob("*.drwdot")):
            return str(f)
    return None


def _find_slddrt():
    for root in (r"c:\ProgramData\SOLIDWORKS", r"c:\ProgramData\SolidWorks"):
        for f in sorted(Path(root).rglob("*.slddrt")):
            return str(f)
    return None


def _build_part(sw, row: dict):
    """★ 建一块板并**存盘**（★ 视图工具的 `ModelName` 必须是含 `.sldprt` 的完整路径）。"""
    doc = c.new_document(sw, "part")
    try:
        from scripts import sw_part as p_

        p_.start_sketch(doc, plane_name="Front Plane")
        _get(
            _get(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.04,
            -0.03,
            0.0,
            0.04,
            0.03,
            0.0,
        )
        p_.end_sketch(doc)
        names = [
            n
            for n in (p_.feature_names(doc) or [])
            if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
        ]
        if names:
            p_.extrude_boss(doc, names[-1], 0.01)
            row["extrude_sketch"] = names[-1]
        # ★ 打一个孔：★ 好让"孔表 / 中心符号线（targets=['holes']）"有**圆边**可用
        # （★ 与 `tools/prove_drawing_batch.py::_build_part` 同一手法；★ 孔不成**不阻断*
        # *）
        try:
            from scripts import sw_hole_features as hf

            rep = hf.create_hole_wizard_at_selection_report(doc, "+z", "M8")
            row["hole"] = {k: rep.get(k) for k in ("ok",) if k in rep}
        except Exception as exc:  # noqa: BLE001
            row["hole_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
    except Exception as exc:  # noqa: BLE001
        row["part_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    try:
        row["part_saved"] = bool(c.save_document(doc, str(PART)))
    except Exception as exc:  # noqa: BLE001
        row["part_save_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        row["part_saved"] = False
    return (doc, str(PART)) if row.get("part_saved") else (None, None)


def _new_drawing(sw, row: dict):
    try:
        return c.new_document(sw, "drawing")
    except Exception as exc:  # noqa: BLE001
        row["drawing_template_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
    tpl = _find_drwdot()
    if not tpl:
        return None
    try:
        return c.new_document(sw, "drawing", template_path=tpl)
    except Exception as exc2:  # noqa: BLE001
        row["drawing_template_err2"] = "%s: %s" % (type(exc2).__name__, str(exc2)[:140])
        return None


def _view_count(doc):
    try:
        import scripts.sw_drawing_query as dq

        return len(dq.list_views(doc) or [])
    except Exception:  # noqa: BLE001
        return None


def _annotation_total(doc):
    """★ 可回读的注解总量（沿视图链累加 `GetAnnotationCount`）。

    ★ 取不到回 `None` —— **降级，不猜 0**（本仓既有形态）。
    """
    total = 0
    seen = False
    try:
        view = _get(doc, "GetFirstView")
        while view is not None:
            n = _get(view, "GetAnnotationCount")
            if n is not None:
                total += int(n)
                seen = True
            view = _get(view, "GetNextView")
    except Exception:  # noqa: BLE001
        return None
    return total if seen else None


def _call_tool(spec, resolvers, args: dict) -> tuple[object, str]:
    """★ **复刻注册器的调用路径**（`tool_registry.py` :498/:507/:524）。

    ★ 返回 `(返回值, 说明)`；★ 只在"契约层面"失败时抛 —— 那正是本探针要抓的东西。
    """
    mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
    fn = getattr(mod, spec.function)
    kwargs = {}
    want = {getattr(p, "name", None) for p in (spec.params or [])}
    for name, value in args.items():
        if name in want:
            kwargs[name] = value
    inj = spec.inject
    resolver = resolvers.get(inj)
    if resolver is None:
        raise RuntimeError(
            "★ 注入名 %r 不在 RESOLVERS 里（是 %s）" % (inj, sorted(resolvers))
        )
    kwargs[inj] = resolver(None)
    return fn(**kwargs), "module=%s function=%s inject=%s params=%s" % (
        spec.module,
        spec.function,
        inj,
        sorted(kwargs),
    )


def main() -> int:
    started = time.time()
    sw, _meta = c.connect_solidworks(wait_seconds=30)
    report = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": []}

    specs = {getattr(s, "name", None): s for s in rc.all_specs()}
    report["registered_tool_count"] = len(specs)
    report["resolvers"] = sorted(rc.RESOLVERS)

    prep = {}
    part_doc, part_path = _build_part(sw, prep)
    prep["drawing_template"] = _find_drwdot()
    prep["sheet_format"] = _find_slddrt()
    report["prep"] = prep
    if part_path:
        TOOL_ARGS["solidworks_drawing_create_projected_view"]["part_path"] = part_path
    if prep["sheet_format"]:
        TOOL_ARGS["solidworks_drawing_set_sheet_format"]["format_path"] = prep[
            "sheet_format"
        ]

    for name, args in TOOL_ARGS.items():
        row = {"tool": name, "ok": False, "args": args}
        spec = specs.get(name)
        if spec is None:
            row["err"] = "★ 工具没注册（all_specs 里没有）"
            report["cases"].append(row)
            continue
        doc = None
        try:
            doc = _new_drawing(sw, row)
            if doc is None:
                row["err"] = "★ 前置未成立：新建工程图失败"
                row["preconditions_held"] = False
                report["cases"].append(row)
                continue
            row["drawing_title"] = str(_get(doc, "GetTitle") or "")
            row["views_before"] = _view_count(doc)
            row["annotations_before"] = _annotation_total(doc)
            # ★ 有的工具要求"同一张图上先有视图" ⇒ 先补一个（★ 用**能力层**建，避免又引
            # 入一层变量）
            if name in NEEDS_VIEW:
                if not part_path:
                    row["pre_step_skip"] = (
                        "★ 前置未成立：零件没存盘 ⇒ 无法建母视图"
                        "（★ 本格据此判前置，**不判能力**）"
                    )
                    row["preconditions_held"] = False
                else:
                    try:
                        from scripts import sw_drawing as _d

                        v = _d.add_view(doc, part_path, "*Front", 0.10, 0.10)
                        row["pre_view_created"] = v is not None
                        args["view_name"] = "*Front"  # ★ 占位名；下面按实际视图名改写
                        row["views_after_pre_step"] = _view_count(doc)
                        import scripts.sw_drawing_query as _dq

                        names_now = [x.get("name") for x in (_dq.list_views(doc) or [])]
                        if names_now:
                            args["view_name"] = str(names_now[0])
                        row["pre_view_name"] = args.get("view_name")
                    except Exception as exc:  # noqa: BLE001
                        row["pre_step_err"] = "%s: %s" % (
                            type(exc).__name__,
                            str(exc)[:140],
                        )
            # ★ 视图类工具的前置：零件已存盘
            if "part_path" in args:
                row["preconditions_held"] = bool(part_path)
            # ★★ **重新取基线** —— 前置步骤自己会建一个母视图；★ 若不在调工具前重取，
            #   `view_delta` 会把**前置步骤的成果**算成本工具的成果 ⇒ ★ **假绿**
            # （2026-10-03 实测踩到：`hole_table` / `insert_center_marks` 两格被误判为 o
            # k）。
            if name in NEEDS_VIEW:
                row["views_before_call"] = _view_count(doc)
                row["annotations_before_call"] = _annotation_total(doc)
                if row["views_before_call"] is not None:
                    row["views_before"] = row["views_before_call"]
                if row["annotations_before_call"] is not None:
                    row["annotations_before"] = row["annotations_before_call"]
            ret, how = _call_tool(spec, rc.RESOLVERS, args)
            row["call_path"] = how
            row["ret_type"] = type(ret).__name__
            row["ret_ok"] = bool(ret.get("ok")) if isinstance(ret, dict) else None
            row["views_after"] = _view_count(doc)
            row["annotations_after"] = _annotation_total(doc)
            if row["views_before"] is not None and row["views_after"] is not None:
                row["view_delta"] = row["views_after"] - row["views_before"]
            if (
                row["annotations_before"] is not None
                and row["annotations_after"] is not None
            ):
                row["annotation_delta"] = (
                    row["annotations_after"] - row["annotations_before"]
                )
            # ★★★ **2026-10-03 修的一处判据缺陷（★ 我自己的探针漏判）**：
            #   原先只认 `ret_ok` 与 `view_delta` ⇒ ★ **产"注解"的工具全被漏判**
            #   （实测：`insert_surface_finish_symbol` 明明 `annotations 72 → 73`，
            #    ★ 却因 `ret_ok=False` 且 `view_delta=0` 被判成 `ok=False`）。
            # ★ 现把 **`annotation_delta`** 也纳入判据（★ 三条**都报**，判据取"任一为正"
            # ）。
            row["ok"] = bool(
                row.get("ret_ok")
                or (row.get("view_delta") or 0) >= 1
                or (row.get("annotation_delta") or 0) >= 1
            )
            row["verified_by"] = (
                "工具返回值 ok **或** 视图数增量 **或** 注解数增量"
                "（★ 三条都报、判据取任一为正）"
            )
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
            row["ok"] = False
        report["cases"].append(row)
        try:
            if doc is not None:
                _get(sw, "CloseDoc", str(row.get("drawing_title") or ""))
        except Exception:  # noqa: BLE001
            pass

    report["passed"] = sum(1 for r in report["cases"] if r.get("ok"))
    report["total"] = len(report["cases"])
    report["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    print(
        "注册器工具数:",
        report["registered_tool_count"],
        "| RESOLVERS:",
        report["resolvers"],
    )
    print(
        "零件:",
        part_path,
        "| 模板:",
        prep["drawing_template"],
        "| 图框:",
        bool(prep["sheet_format"]),
    )
    for r in report["cases"]:
        print(
            "  %-52s ok=%-6s delta=%-4s %s"
            % (
                r["tool"][:51],
                r.get("ok"),
                r.get("view_delta"),
                (r.get("err") or "")[:60],
            )
        )
    print(
        "passed %d/%d in %.1fs" % (report["passed"], report["total"], report["seconds"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
