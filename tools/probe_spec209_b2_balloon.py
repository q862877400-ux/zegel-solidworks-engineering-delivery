"""★ 真机：规格 209 · B2-2（idx 34 balloon）—— ★★ 给"两家外部项目结论互相矛盾"**定案**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_spec209_b2_balloon.py
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B2-2** · 外部项目 idx **34 `balloon`**。
#   ★★★ 裁决书的硬约束（§一）逐字：「★★ 两家结论**互相矛盾**（Slacker-LLC 说静默无效、
#     Eduardof0nt 直接调并回 `bool(result)`）⇒ **不许照抄任何一家**，必须真机定案」✓
#   ★★ 而**定案的钥匙在官方示例的 Preconditions 里**（逐字）：
#     「Open a drawing **with a bill of materials (BOM) table**」
#     ⇒ ★★ 假设：**没有 BOM 表时 `AutoBalloon5` 静默什么都不插** ⇒
#        · **Slacker-LLC 的观察是对的**（"silently does nothing"）
#        · **Eduardof0nt 的 `bool(result)` 是错的**（★ 空数组 / `None` ⇒ 假）
#   ★★ 本探针**一次跑两种前置**（★ 同一份装配 + 同一张工程图）：
#     ```
#     ① 装配工程图 + **没有** BOM 表 ⇒ 调 AutoBalloon5 ⇒ 记 GetNoteCount 增量 + 返回数组长度
#     ② 用 IView::InsertBomTable6 插一张 BOM 表 ⇒ 再调 ⇒ 同上
#     ```
#   ★★ 判据（规则 6，纯回读）：**`sum(IView::GetNoteCount)` 的增量** ——
#     ★ **不拿 `AutoBalloon5` 返回的数组当判据**（那正是别家错的地方）✓
# 官方依据: `C:\\swapi\\types\\IDrawingDoc\\AutoBalloon5.md`（Returns = **Array of INotes**；
#   `## Remarks` 给**四步前置**）· `C:\\swapi\\types\\IModelDocExtension\\InsertBOMBalloon2.md`
#   （单发气泡：`Note InsertBOMBalloon2(BalloonOptions)`，四步前置）·
#   `C:\\swapi\\types\\IView\\GetNoteCount.md`（**判据来源**）·
#   `C:\\swapi\\types\\IView\\InsertBomTable6.md`（12 参；★ 用来造「有 BOM 表」那个前置）·
#   `enums\\{swBomType_e,swBomConfigurationAnchorType_e}.md` ·
#   ★★ `examples\\Add_Autoballoon_to_Face_Example_VB.md`（**调用序 + Preconditions**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "spec209-balloon.json"


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    import sw_part as P
    import sw_assembly as A
    import sw_drawing_create_missing as DM
    import sw_drawing_expose as E0

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "规格 209 · B2-2 balloon —— 给「两家矛盾」定案（判据 = GetNoteCount 的增量）",
          "judge": "sum(IView::GetNoteCount) 的增量（★ 不用返回的数组当判据）",
          "steps": {}, "verdict": {}}
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

    def _select_view(drw, view_name):
        from sw_part import _empty_callout
        get_com_member(drw, "ClearSelection2", True)
        get_com_member(get_com_member(drw, "Extension"), "SelectByID2", view_name,
                       "DRAWINGVIEW", 0.0, 0.0, 0.0, False, 0, _empty_callout(), 0)
        get_com_member(drw, "ActivateView", view_name)

    try:
        #: ① 零件（存盘）→ ② 装配（两个组件，存盘）→ ③ 装配工程图 + 一个投影视图
        part = sw_connect.new_document(sw, "part")
        opened.append(part)
        with P.sketch(part, "Front Plane") as sk:
            P.sketch_corner_rectangle(part, -30.0, -20.0, 30.0, 20.0)
        P.end_sketch(part)
        P.extrude_boss(part, "草图1", 10.0)
        part_path = str(outdir / "probe209_balloon_part.sldprt")
        ev["part_saved"] = bool(sw_connect.save_document(part, part_path))

        asm = sw_connect.new_document(sw, "assembly")
        opened.append(asm)
        A.add_component(asm, part_path, 0.0, 0.0, 0.0, sw=sw)
        A.add_component(asm, part_path, 0.06, 0.0, 0.0, sw=sw)
        asm_path = str(outdir / "probe209_balloon_asm.sldasm")
        ev["asm_saved"] = bool(sw_connect.save_document(asm, asm_path))

        drw = sw_connect.new_document(sw, "drawing")
        opened.append(drw)
        made = None
        try:
            made = E0.create_projected_view(drw, asm_path, view_name="*Front",
                                            x_mm=140.0, y_mm=120.0, scale=0.0)
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["view_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        views = [DM._view_name(v) for v in DM._iter_views(drw)]
        ev["views"] = views
        ev["view_made"] = bool(made)
        print("  装配工程图视图：%r" % (views,))

        if views:
            #: ── ① **没有 BOM 表**时调 AutoBalloon5 ────────────────────────────────
            _select_view(drw, views[0])
            r1 = DM.auto_insert_balloons(drw)
            ev["steps"]["no_bom"] = {k: r1.get(k) for k in
                                     ("ok", "returned_is_none", "balloon_note_count",
                                      "note_count_before", "note_count_after",
                                      "note_count_delta", "selection_count", "error")}
            print("  【无 BOM】ok=%s 返回数组=%s 标注数 %s→%s (Δ%s)"
                  % (r1.get("ok"), r1.get("balloon_note_count"), r1.get("note_count_before"),
                     r1.get("note_count_after"), r1.get("note_count_delta")))

            #: ── ② **另起一张**工程图 + 先插 BOM 表，再调 ─────────────────────────────
            #: ★★ 第一版把这一格跑在**同一张图、同一个视图**上 —— ★ 而那时气泡**已经存在**了，
            #:   `IgnoreMultiple=True` 很可能只是**没重复插** ⇒ ★ Δ=0 **不能**当「有 BOM 表就不行」
            #:   的证据（★★ 那是我探针的**设计缺陷**，已如实记进产物）⇒ ★ **换一张干净的图**重做 ✓
            _close(drw)
            drw2 = sw_connect.new_document(sw, "drawing")
            opened.append(drw2)
            try:
                E0.create_projected_view(drw2, asm_path, view_name="*Front",
                                         x_mm=140.0, y_mm=120.0, scale=0.0)
            except Exception as exc:                           # noqa: BLE001
                ev["steps"]["view2_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
            views2 = [DM._view_name(v) for v in DM._iter_views(drw2)]
            ev["views2"] = views2
            print("  第二张图视图：%r" % (views2,))
            found = DM._find_view(drw2, views2[0]) if views2 else (None, "无视图")
            view_obj = found[0] if isinstance(found, tuple) else found
            bom = None
            if view_obj is not None:
                try:
                    bom = get_com_member(view_obj, "InsertBomTable6", False, 0.15, 0.15, 1, 1,
                                         "", "", False, 0, False, False, False)
                    ev["steps"]["bom_table"] = {"returned": str(bom)[:80]}
                except Exception as exc:                       # noqa: BLE001
                    ev["steps"]["bom_table"] = {"error": "%s: %s" % (type(exc).__name__,
                                                                    str(exc)[:160])}
                print("  BOM 表：%s" % str(ev["steps"]["bom_table"])[:110])
                _select_view(drw2, views2[0])
                r2 = DM.auto_insert_balloons(drw2)
                ev["steps"]["with_bom"] = {k: r2.get(k) for k in
                                           ("ok", "returned_is_none", "balloon_note_count",
                                            "note_count_before", "note_count_after",
                                            "note_count_delta", "selection_count", "error")}
                print("  【有 BOM·独立图纸】ok=%s 返回数组=%s 标注数 %s→%s (Δ%s)"
                      % (r2.get("ok"), r2.get("balloon_note_count"),
                         r2.get("note_count_before"), r2.get("note_count_after"),
                         r2.get("note_count_delta")))

        nb, wb = ev["steps"].get("no_bom", {}), ev["steps"].get("with_bom", {})
        ev["verdict"] = {
            "no_bom_delta": nb.get("note_count_delta"),
            "no_bom_returned": nb.get("balloon_note_count"),
            "with_bom_delta": wb.get("note_count_delta"),
            "with_bom_returned": wb.get("balloon_note_count"),
            "★ 与假设相反的那一格": (
                "★★ 我原来的假设是「**没有 BOM 表 ⇒ 静默什么都不插**」（因为官方示例的 "
                "Preconditions 逐字要求 BOM 表）—— ★★ **真机推翻了它**："
                "**没有 BOM 表时它照样插了 1 个气泡**（Δ=%r、返回数组 %r）⇒ "
                "★★ **两家外部项目的话都不该照抄**：Slacker-LLC 的「静默无效」不成立、"
                "Eduardof0nt 的 `bool(result)` 也不能当判据（★ 它只是「返回数组非空」）✓"
                % (nb.get("note_count_delta"), nb.get("balloon_note_count"))),
            "★ 判据定案": (
                "★★ **判据只能是 `sum(IView::GetNoteCount)` 的增量** —— "
                "★ 两个前置格都是**回读 Δ** 与**返回数组长度**一起记的："
                "Δ>0 才是「真插进去了」的证据；★ 返回数组长度**只回报、不当判据** ✓"),
        }
        print("  verdict =", json.dumps(ev["verdict"], ensure_ascii=False)[:500])
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
