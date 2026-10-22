"""★ 真机：规格 209 · B4-5（idx 205 model_annotations）—— 判据 = 视图标注数的前后回读。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_spec209_b4_model_annotations.py
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B4-5** · 外部项目 idx **205 `model_a
#           nnotations`**。
#   ★★ 判据（规则 6，全回读）：
#     ```
# ① 视图标注数        ★ IView::GetAnnotationCount() 的**前后读数**（本模块既有 _sum_over
# _views）
# ② 官方调用序        ★ 先选中视图（DRAWINGVIEW）→ **ActivateView** → ClearSelection2 →
# 调它
# ③ 负例              ★ 空图纸（一个视图都没有）⇒ **必须如实报**（官方语义是「当前选中的
# 视图」）
# ④ Types 语义        ★ 两个 insert_all_* 都为 False 且 types 空 ⇒ **官方说 Types 只在那
# 时有效**
#                         ⇒ 本函数**拒绝**（★ 不猜）
#     ```
# 官方依据: `C:\\swapi\\types\\IDrawingDoc\\InsertModelAnnotations4.md`（8 参 + Paramete
#           rs + Returns）·
#   `C:\\swapi\\enums\\{swImportModelItemsSource_e,swInsertAnnotation_e}.md` ·
#   `C:\\swapi\\types\\IView\\GetAnnotationCount.md` ·
#   ★★ `C:\\swapi\\examples\\Insert_Model_Annotations_Example_VB.md`（**调用序**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "spec209-model-annotations.json"


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    import sw_part as P
    import sw_drawing_create_missing as DM
    import sw_drawing_expose as E0

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "规格 209 · B4-5 model_annotations（判据 = 视图标注数前后回读）",
        "judge": "IView::GetAnnotationCount 前后读数 + 官方调用序",
        "steps": {},
        "negative": {},
    }
    opened = []
    outdir = R / "output" / "probe209"
    outdir.mkdir(parents=True, exist_ok=True)

    def _close(doc):
        try:
            t = str(safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass

    try:
        #: ① 造零件并**存盘**（★ 工程图投影要有路径 —— 既有探针的教训）
        #:   ★★ **而且要带尺寸** —— 第一版用"纯坐标画出来的草图"（**一个尺寸都没有**）⇒
        #: `InsertModelAnnotations4` **回的数组长度 0**（★ 那不是"调用失败"，是**没东西
        #: 可插**）✓
        part = sw_connect.new_document(sw, "part")
        opened.append(part)
        import sw_sketch_dimensions as SD

        with P.sketch(part, "Front Plane") as sk:
            P.sketch_corner_rectangle(part, -30.0, -20.0, 30.0, 20.0)
            ev["dimension_added"] = []
            for fn, args in (
                ("add_horizontal_dimension", (0.0, 15.0)),
                ("add_vertical_dimension", (35.0, 0.0)),
            ):
                try:
                    ev["dimension_added"].append(
                        {"fn": fn, "ret": str(getattr(SD, fn)(part, *args))[:60]}
                    )
                except Exception as exc:  # noqa: BLE001
                    ev["dimension_added"].append(
                        {
                            "fn": fn,
                            "error": "%s: %s" % (type(exc).__name__, str(exc)[:90]),
                        }
                    )
        P.end_sketch(part)
        P.extrude_boss(part, "草图1", 20.0)
        print(
            "  尺寸：%s" % json.dumps(ev["dimension_added"], ensure_ascii=False)[:200]
        )
        part_path = str(outdir / "probe209_annot_part.sldprt")
        ev["part_saved"] = bool(sw_connect.save_document(part, part_path))
        ev["part_path"] = part_path

        #: ② 造工程图 + 一个投影视图（★ 走已知能通的那条：create_projected_view）
        drw = sw_connect.new_document(sw, "drawing")
        opened.append(drw)
        made = None
        try:
            made = E0.create_projected_view(
                drw, part_path, view_name="*Front", x_mm=140.0, y_mm=120.0, scale=0.0
            )
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["view_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
        ev["steps"]["view_made"] = str(made)[:120]
        views = [DM._view_name(v) for v in DM._iter_views(drw)]
        ev["views"] = views
        ev["steps"]["view_count"] = len(views)
        print("  视图：%r" % (views,))

        if views:
            #: ③A 官方示例那一路：**AllViews=True** + 全插
            r = DM.insert_model_annotations(
                drw,
                views[0],
                all_views=True,
                insert_all_annotations=True,
                insert_all_reference_geometry=True,
            )
            ev["steps"]["all_views_true"] = {
                k: r.get(k)
                for k in (
                    "ok",
                    "view",
                    "annotation_count_before",
                    "annotation_count_after",
                    "annotation_delta",
                    "returned_count",
                    "selected_count",
                    "mask",
                    "error",
                )
            }
            print(
                "  all_views=True  ok=%s 标注 %s→%s 返回 %s"
                % (
                    r.get("ok"),
                    r.get("annotation_count_before"),
                    r.get("annotation_count_after"),
                    r.get("returned_count"),
                )
            )
            #: ③B **AllViews=False** ⇒ ★ 视图**必须留在选区里**（官方摘要的 "currently s
            #: elected"）
            r1b = DM.insert_model_annotations(
                drw,
                views[0],
                insert_all_annotations=True,
                insert_all_reference_geometry=True,
            )
            ev["steps"]["all_views_false"] = {
                k: r1b.get(k)
                for k in (
                    "ok",
                    "annotation_count_before",
                    "annotation_count_after",
                    "annotation_delta",
                    "returned_count",
                    "selected_count",
                    "error",
                )
            }
            print(
                "  all_views=False ok=%s 标注 %s→%s 返回 %s"
                % (
                    r1b.get("ok"),
                    r1b.get("annotation_count_before"),
                    r1b.get("annotation_count_after"),
                    r1b.get("returned_count"),
                )
            )
            #: ④ 只插"标记给工程图的尺寸"（★ 官方示例的那一组参数，但 AllViews=False）
            r2 = DM.insert_model_annotations(
                drw, views[0], types="swInsertDimensionsMarkedForDrawing"
            )
            ev["steps"]["marked_dims"] = {
                k: r2.get(k)
                for k in (
                    "ok",
                    "mask",
                    "types_used",
                    "annotation_delta",
                    "returned_count",
                    "error",
                )
            }
            print(
                "  marked_dims ok=%s mask=%s Δ=%s"
                % (r2.get("ok"), r2.get("mask"), r2.get("annotation_delta"))
            )
        _close(drw)

        #: ⑤ 负例：空图纸（无视图）
        empty = sw_connect.new_document(sw, "drawing")
        opened.append(empty)
        r3 = DM.insert_model_annotations(empty, insert_all_annotations=True)
        ev["negative"]["no_view"] = {"ok": r3.get("ok"), "error": r3.get("error")}
        print("  负例 no_view ok=%s err=%s" % (r3.get("ok"), str(r3.get("error"))[:70]))
        #: ⑥ 负例：两个 insert_all 都 False 且 types 空
        r4 = DM.insert_model_annotations(empty)
        ev["negative"]["nothing_selected"] = {
            "ok": r4.get("ok"),
            "error": r4.get("error"),
        }
        print("  负例 nothing ok=%s err=%s" % (r4.get("ok"), str(r4.get("error"))[:70]))
        _close(empty)

        ev["verdict"] = {
            "insert_all_built": bool(ev["steps"].get("insert_all", {}).get("ok")),
            "marked_dims_mask_ok": ev["steps"].get("marked_dims", {}).get("mask")
            == 32768,
            "negative_no_view_loud": (
                ev["negative"]["no_view"].get("ok") is False
                and bool(ev["negative"]["no_view"].get("error"))
            ),
            "negative_nothing_loud": (
                ev["negative"]["nothing_selected"].get("ok") is False
                and bool(ev["negative"]["nothing_selected"].get("error"))
            ),
        }
        print("  verdict =", json.dumps(ev["verdict"], ensure_ascii=False))
    except Exception as exc:  # noqa: BLE001
        ev["fatal"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        print("  FATAL %s" % str(exc)[:140])

    for d in opened:
        _close(d)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  产物：%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:  # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
