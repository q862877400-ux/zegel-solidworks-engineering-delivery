"""★ 真机：**倒角到底建成没有** —— ★ 三条判据并列，不拿「树没涨」定性（事实 104 的教训）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_chamfer_geometry.py
# 定位:   ★ 2026-10-03（轮 462）★ 承**事实 104**：「**「看到异常就定性」是误判之源** ——
#   `CreateChamfer` 判成「架构性限制」，其实**倒角已经建成**了」。
#   ★★ 而我这一轮用「**特征树增量**」判 `sw_part.chamfer` ⇒ 报 ✗ ——
#     ★ **而事实 104 说这一类判法会误判** ⇒ ★ 故本轮**换判据**：核**几何** ✓
#   ★★★ 三条并列（★ 不预设哪条对）：
#     ```
#     ① ★ 特征树增量（★ 我上一条用的，★ 保留作对照）
#     ② ★★ **几何**：★ 面数 / 边数 / 体积（★ 倒角**必须**改变它们）
#     ③ ★ 原始返回值（★ None / Feature —— ★ 最直接的一条线索）
#     ```
#   ⚠ **前置**：★ 先建一个**有实体**的零件（★ 拉伸一个方块）⇒ 再选一条边 ⇒ 再倒角 ✓
# 官方依据: `IFeatureManager.InsertFeatureChamfer`（★ 8 参）· 本仓 `scripts/sw_part.py` 的 `chamfer`
#   （★ 实参 `4, 1, distance, angle_rad, 0, 0, 0, 0`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上（三条并列）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "chamfer-geometry-evidence.json"


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    from sw_part import (chamfer, current_sketch_name, end_sketch, extrude_boss,
                         feature_names, sketch_corner_rectangle, start_sketch)
    from sw_selection_spec import get_selection_count, resolve_selection

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")

        def geom():
            out = {}
            try:
                bs = list(get_com_member(doc, "GetBodies2", -1, True) or [])
                out["bodies"] = len(bs)
                if bs:
                    b = bs[0]
                    out["faces"] = len(list(get_com_member(b, "GetFaces") or []))
                    out["edges"] = len(list(get_com_member(b, "GetEdges") or []))
            except Exception as e:
                out["err"] = str(e)[:70]
            try:
                ext = get_com_member(doc, "Extension")
                vals = get_com_member(ext, "GetMassProperties", 1)
                out["volume"] = round(float(vals[3]), 12) if vals else None
            except Exception as e:
                out["vol_err"] = str(e)[:60]
            return out

        names = {}
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -20.0, -15.0, 20.0, 15.0)
        names["sk"] = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, names["sk"], 10.0)
        ev["tree_after_boss"] = len(list(feature_names(doc)))
        ev["geom_before"] = geom()
        ev["sel"] = int(resolve_selection(doc, "index:0", "EDGE"))
        ev["sel_count"] = int(get_selection_count(doc))

        rec = {}
        rec["tree_before"] = len(list(feature_names(doc)))
        try:
            r = chamfer(doc, 2.0)
            rec["raw_is_none"] = r is None
            rec["raw_type"] = type(r).__name__
        except Exception as e:
            rec["err"] = "%s: %s" % (type(e).__name__, str(e)[:140])
        rec["tree_after"] = len(list(feature_names(doc)))
        rec["tree_grew"] = rec["tree_after"] > rec["tree_before"]
        ev["geom_after"] = geom()
        gb, ga = ev["geom_before"], ev["geom_after"]
        rec["geom_changed"] = {k: [gb.get(k), ga.get(k)]
                               for k in ("faces", "edges", "volume") if gb.get(k) != ga.get(k)}
        rec["geom_grew"] = bool(rec["geom_changed"])
        ev["chamfer"] = rec
        ev["verdict"] = "pass" if (rec.get("geom_grew") or rec.get("tree_grew")) else "fail"
        ev["note"] = ("★ 三条判据并列：① 特征树增量（★ 上一条用过的）· ② **几何**（面/边/体积）· "
                      "③ 原始返回值。★ 承事实 104：「看到异常就定性」是误判之源 ⇒ "
                      "**不拿「树没涨」当「没建成」**。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:1100])
        print("  产物：%s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:
            pass
        if doc is not None:
            try:
                t = str(safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
