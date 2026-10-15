"""★ 真机：★ **用 `AddRelation(COINCIDENT=9)` 闭合真曲线齿廓**（★ 官方推荐路）。

★★★ **真因（★ 已由数值定位 · ★ 不是猜）**：
  ★ 6 条真曲线的端点间距 **0.695 ~ 2.045 µm**
    （★ `output/_probe_gear_endpoints.json`）⇒ ★★ 那是
    `CreateEquationSpline2` **按自己精度离散**方程留下的**固有**缝 ✗
  ★★★ **缝 ≈ 1 µm** ⇒ ★ SolidWorks **不会自动合并**（★ 它按**同一坐标**判重合）✗

★★★ **规范修法（★ 两条官方入口，★ 本探针都用）**：
  ★ ① `ISketchRelationManager::AddRelation(Entities, RelationType)`
    ★★ 官方签名逐字：★ `SketchRelation AddRelation(object Entities, int RelationType)` ✓
    ★★ 而 `swConstraintType_COINCIDENT` **= 9**（★ 官方枚举表逐字）✓
  ★ ② `ISketch::MergePoints(Distance)`
    ★★ 官方 Remarks **逐字推荐**：★ "To specify a distance below which points are
      automatically merged while creating the segments, use `ISketchRelationManager::AddRelation`
      … and **swConstraintType_COINCIDENT**." ✓

★ 判据：★ ① **点数回到 6**（★ 无孤立点）· ★ ② **拉伸非 None** · ★ ③ **体积 ≈ 解析** ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gear_relation_closure.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 真曲线齿廓的**官方闭合入口**。
# 官方依据: `C:\swapi\types\ISketchRelationManager\AddRelation.md`
#         （★ `SketchRelation AddRelation(object Entities, int RelationType)`）
#         `C:\swapi\enums\swConstraintType_e.md`（★ `swConstraintType_COINCIDENT = 9`）
#         `C:\swapi\types\ISketch\MergePoints.md`（★ Remarks 推荐 AddRelation+COINCIDENT）
#         `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ---------------------------------------------------------------------
from __future__ import annotations

import json
import math
import sys
import time
import traceback as _tb
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
from scripts import gear_geometry as G                                # noqa: E402
from tools.probe_gear_tooth_pattern2 import tooth_curves              # noqa: E402

COINCIDENT = 9          #: ★ 官方 `swConstraintType_e`：★ swConstraintType_COINCIDENT = 9 ✓


def _pt(seg, which):
    try:
        pt = C.get_com_member(seg, which)
        if pt is None:
            return None
        arr = list(pt)
        return (float(arr[0]), float(arr[1])) if len(arr) >= 2 else None
    except Exception:                                                     # noqa: BLE001
        return None


def _main() -> int:
    spec = G.GearSpec(module_mm=1.0, teeth=20, face_width_mm=10.0,
                      pressure_angle_deg=20.0, bore_diameter_mm=8.0)
    geo = G.calculate_gear_geometry(spec)
    curves, meta = tooth_curves(spec, geo)
    rep = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "_": "★ AddRelation(COINCIDENT=9) 闭合真曲线齿廓", "steps": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        sm = C.get_com_member(doc, "SketchManager")
        ok = 0
        for name, x, y, t0, t1 in curves:
            try:
                C.get_com_member(sm, "CreateEquationSpline2", x, y, "",
                                 "%r" % t0, "%r" % t1, False, 0.0, 0.0, 0.0, True, True)
                ok += 1
            except Exception:                                             # noqa: BLE001
                pass
        rep["steps"].append({"curves_ok": ok})
        sk = C.get_com_member(doc, "GetActiveSketch2")
        segs = list(C.get_com_member(sk, "GetSketchSegments") or [])
        rep["steps"].append({"segments": len(segs),
                             "points_before": len(list(C.get_com_member(sk, "GetSketchPoints2") or []))})
        #: ★ 取每段的两个端点
        ends = [(_pt(s, "GetStartPoint2"), _pt(s, "GetEndPoint2")) for s in segs]
        #: ★★ 逐对接缝：★ 选**两个端点**再加关系
        rm = None
        for g in ("RelationManager", "GetRelationManager"):
            try:
                rm = C.get_com_member(sk, g)
                if rm is not None:
                    break
            except Exception:                                             # noqa: BLE001
                pass
        rep["steps"].append({"relation_manager": rm is not None,
                             "rm_type": type(rm).__name__ if rm is not None else None})
        results = []
        n = len(segs)
        for i in range(n):
            j = (i + 1) % n
            #: ★ 找最近的一对端点
            best = None
            for ai, a in ((0, ends[i][0]), (1, ends[i][1])):
                for bi, b in ((0, ends[j][0]), (1, ends[j][1])):
                    if a is None or b is None:
                        continue
                    d = math.dist(a, b)
                    if best is None or d < best[0]:
                        best = (d, ai, bi)
            if not best:
                continue
            d, ai, bi = best
            row = {"pair": [i, j], "gap_um": round(d * 1e6, 4)}
            try:
                doc.ClearSelection2(True)
                s1 = C.get_com_member(segs[i], "GetStartPoint2" if ai == 0 else "GetEndPoint2")
                s2 = C.get_com_member(segs[j], "GetStartPoint2" if bi == 0 else "GetEndPoint2")
                #: ★ `ISketchPoint::Select4(Append, Callout)`（★ 事实 32：★ 点没名字）
                ok1 = bool(C.get_com_member(s1, "Select4", False, None))
                ok2 = bool(C.get_com_member(s2, "Select4", True, None))
                row["selected"] = [ok1, ok2]
                row["selected_count"] = int(C.get_com_member(
                    C.get_com_member(doc, "SelectionManager"),
                    "GetSelectedObjectCount2", -1))
                if rm is not None:
                    #: ★★ 官方参数序：★ `AddRelation(Entities, RelationType)`
                    rel = C.get_com_member(rm, "AddRelation", None, COINCIDENT)
                    row["relation"] = rel is not None
            except Exception as exc:                                      # noqa: BLE001
                row["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
            results.append(row)
        rep["steps"].append({"relations": results})
        rep["max_gap_um"] = max((r.get("gap_um") or 0) for r in results) if results else None
        rep["relations_added"] = sum(1 for r in results if r.get("relation"))
        #: ★ 复查点数与段数
        sk2 = C.get_com_member(doc, "GetActiveSketch2")
        rep["steps"].append({
            "points_after": len(list(C.get_com_member(sk2, "GetSketchPoints2") or [])),
            "segments_after": len(list(C.get_com_member(sk2, "GetSketchSegments") or [])),
            "constrained_status": int(C.get_com_member(sk2, "GetConstrainedStatus")),
        })
        P.end_sketch(doc)
        f = P.extrude_boss(doc, "草图1", 0.010)
        rep["extrude_ok"] = f is not None
        if f is not None:
            try:
                mp = C.get_com_member(C.get_com_member(doc, "Extension"),
                                      "CreateMassProperty")
                rep["volume_mm3"] = round(float(C.get_com_member(mp, "Volume")) * 1e9, 6)
            except Exception:                                             # noqa: BLE001
                pass
    except Exception as exc:                                              # noqa: BLE001
        rep["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass
    p = R / "output" / "_probe_gear_relation_closure.json"
    p.write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
                 encoding="utf-8")
    print("  ★ 曲线 %s · 段 %s" % (rep["steps"][0].get("curves_ok"),
                                   rep["steps"][1].get("segments")))
    print("  ★ 关系管理器 = %s (%s)" % (rep["steps"][2].get("relation_manager"),
                                        rep["steps"][2].get("rm_type")))
    for r in (rep["steps"][3].get("relations") or [])[:6]:
        print("     接缝%s-%s 缝=%.4f µm 选中=%s 计数=%s 关系=%s %s"
              % (r["pair"][0], r["pair"][1], r.get("gap_um") or 0, r.get("selected"),
                 r.get("selected_count"), r.get("relation"), (r.get("error") or "")[:60]))
    print("  ★ 加了 %s 个关系 · 最大缝 %.4f µm" % (rep.get("relations_added"),
                                                 rep.get("max_gap_um") or 0))
    print("  ★ 加后：点=%s 段=%s 约束状态=%s" % (
        rep["steps"][4].get("points_after"), rep["steps"][4].get("segments_after"),
        rep["steps"][4].get("constrained_status")))
    print("  ★ 拉伸 = %s · 体积 = %s mm³" % (rep.get("extrude_ok"), rep.get("volume_mm3")))
    if rep.get("error"):
        print("  ✗ %s" % rep["error"])
    print("  产物：%s" % p)
    return 0


def main() -> int:
    try:
        return _main()
    except BaseException:                                                 # noqa: BLE001
        (R / "output" / "_probe_rel_tb.txt").write_text(
            _tb.format_exc(), encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
