"""★ 真机：规格 209 · B2-3（idx 52 centerline）—— ★ 给「静默无效 vs 能用」定案。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_spec209_b2_centerline.py
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B2-3** · 外部项目 idx **52 `centerli
#           ne`**。
#   ★★ 裁决书要求「**须真机定案**」：一家说零件视图上 `InsertCenterLine2` **静默无效**，
#     另一家直接调并回 `bool(result)` ⇒ ★ **不许照抄任何一家** ✓
#   ★★ 判据（规则 6）：
#     ```
#     ① 视图里可见实体数     ★ IView::GetVisibleEntities2（★ 无 out 参，pywin32 可直接用）
#     ② 选区计数             ★ 事实 8：不许信 Select4 的返回值
#     ③ 视图中心线数增量     ★ IView::GetCenterLineCount() 的前后回读（★ 真正的判据）
#     ★★ 并把「**选不上**」（选区 0 ⇒ 提前报错）与「**选了也没用**」（Δ=0）**分开记** ✓
#     ```
# 官方依据: `C:\\swapi\\types\\IDrawingDoc\\InsertCenterLine2.md`（零参；摘要逐字
#   「on the **selected entities**」；★ **无 Remarks 也无 Parameters** ⇒ 只能从示例读）·
#   ★★ `examples\\Get_Centerlines_in_Drawing_Example_VB.md`（**调用序**：先选组件、再按点选面）·
#   `IView\\GetVisibleEntities2.md` · `IView\\GetCenterLineCount.md` ·
#   `enums\\swViewEntityType_e.md`
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
OUT = R / "output" / "spec209-centerline.json"


def main() -> int:
    import sw_connect
    from sw_connect import safe_get_com_member
    import sw_part as P
    import sw_drawing_create_missing as DM
    import sw_drawing_expose as E0

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "规格 209 · B2-3 centerline（★ 定案：静默无效 vs 能用）",
          "judge": "视图可见实体数 + 选区计数 + IView::GetCenterLineCount 的增量",
          "runs": [], "verdict": {}}
    opened = []
    outdir = R / "output" / "probe209"
    outdir.mkdir(parents=True, exist_ok=True)

    def _close(doc):
        try:
            t = str(safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
        except Exception:                                      # noqa: BLE001
            pass

    try:
        #: ★ 造一个**圆柱**（官方示例的靶子就是 `cylinder20-9`）⇒ 视图里有圆弧边/圆柱面
        part = sw_connect.new_document(sw, "part")
        opened.append(part)
        with P.sketch(part, "Front Plane") as sk:
            P.sketch_circle(part, 0.0, 0.0, 20.0)
        P.end_sketch(part)
        P.extrude_boss(part, "草图1", 30.0)
        part_path = str(outdir / "probe209_centerline_part.sldprt")
        ev["part_saved"] = bool(sw_connect.save_document(part, part_path))

        drw = sw_connect.new_document(sw, "drawing")
        opened.append(drw)
        made = None
        try:
            made = E0.create_projected_view(drw, part_path, view_name="*Front",
                                            x_mm=140.0, y_mm=120.0, scale=0.0)
        except Exception as exc:                               # noqa: BLE001
            ev["steps_view_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        views = [DM._view_name(v) for v in DM._iter_views(drw)]
        ev["views"] = views
        ev["view_made"] = bool(made)
        print("  视图：%r" % (views,))

        if views:
            #: 先看**视图里到底有多少可见实体**（★ 这一步本身就能解释「静默无效」）
            for et in ("edge", "face", "silhouette_edge", "vertex"):
                r = DM.insert_center_lines(drw, views[0], entity_type=et, entity_index=0)
                ev["runs"].append({
                    "entity_type": et, "ok": r.get("ok"),
                    "visible_count": r.get("visible_count"),
                    "selection_count": r.get("selection_count"),
                    "centerline_count": [r.get("centerline_count_before"),
                                         r.get("centerline_count_after")],
                    "centerline_delta": r.get("centerline_delta"),
                    "returned_is_none": r.get("returned_is_none"),
                    "error": r.get("error")})
                print("  %-16s ok=%-5s 可见=%-4s 选中=%-3s 中心线 %s→%s (Δ%s)"
                      % (et, r.get("ok"), r.get("visible_count"), r.get("selection_count"),
                         r.get("centerline_count_before"), r.get("centerline_count_after"),
                         r.get("centerline_delta")))

        got = [x for x in ev["runs"] if x.get("ok")]
        selected = [x for x in ev["runs"] if (x.get("selection_count") or 0) > 0]
        ev["verdict"] = {
            "any_entity_visible_in_view": any((x.get("visible_count") or 0) > 0
                                              for x in ev["runs"]),
            "any_selection_succeeded": bool(selected),
            "any_centerline_built": bool(got),
            "★ 定案": ("★ **选中成功且 Δ>0** ⇒ 「静默无效」不成立"
                       if got else
                       ("★ **选中成功但 Δ=0** ⇒ 「**选了也没用**」—— 支持「静默无效」那一家的观察"
                        if selected else
                        "★ **本探针没备成前置**（视图里没有可见实体 / 选不上）"
                        "⇒ ★ **不能**据此判「能力无效」（★ 两者必须分开）")),
        }
        print("  verdict =", json.dumps(ev["verdict"], ensure_ascii=False)[:400])
    except Exception as exc:                                   # noqa: BLE001
        ev["fatal"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        print("  FATAL %s" % str(exc)[:150])

    for d in opened:
        _close(d)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
                   encoding="utf-8")
    print("  产物：%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:                                          # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
